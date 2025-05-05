import os
import re
import uuid
import asyncio
import sys
from datetime import datetime
from typing import List, AsyncGenerator, Union, Optional
import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from huggingface_hub import login
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread
import tempfile
import httpx

# Local modules
from common.curr_user import get_current_user
from data_models import User
from database import get_admin_db
from logger import get_logger
#from utils.file_processor import process_file_content, extract_file_content_for_preview, process_file_context
from utils.file_processing import process_file_context, process_file_content, save_document, get_document, get_chat_documents

from services.stream_service import *
from services.vector_search import *

router = APIRouter()
logger = get_logger("chat")

TGI_HEALTH_ENABLED = os.getenv("TGI_HEALTH_ENABLED", "False").lower() == "true"

# =============== Chat Constants ===============
SYSTEM_PROMPT = "You are an AI assistant. Provide clear, concise answers. If you're unsure, be honest. Keep your responses relevant and helpful."
MAX_HISTORY = 6
CONTEXT_LENGTH = 2048
MAX_PROMPT_LENGTH_CHARS=1024*3
STOP_SEQUENCES = ["User:", "\nUser:", "<|endoftext|>", "Human:", "\nHuman:", "Assistant:", "\nAssistant:"]

# =============== SQLAlchemy Models ===============
Base = declarative_base()

class ChatModel(Base):
    __tablename__ = "chats"
    __table_args__ = {"schema": "chat"}  # Use the chat schema
    
    chat_id = Column(String(36), primary_key=True)  # UUID as string
    user_id = Column(String(36))  # UUID as string
    name = Column(String, nullable=False, default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MessageModel(Base):
    __tablename__ = "messages"
    __table_args__ = {"schema": "chat"}  # Use the chat schema
    
    message_id = Column(String(36), primary_key=True)  # UUID as string
    chat_id = Column(String(36), ForeignKey("chat.chats.chat_id"))  # UUID as string
    content = Column(Text, nullable=False)
    is_user = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# =============== Authentication ===============

login(token=os.getenv("HF_TOKEN"))

# =============== CPU Model Config ===============
#if torch.cuda.is_available():
    #USE_CPU = False # os.getenv("USE_CPU", "False").lower() in ("true", "yes", "1", "on")  # Accept various true values
#else:
    #USE_CPU=True
USE_CPU=os.getenv("USE_CPU", "False").lower() in ("true", "yes", "1", "on")

# =============== Pydantic Models ===============
class Message(BaseModel):
    content: str
    isUser: bool
    created_at: Optional[datetime] = None

class ChatRequest(BaseModel):
    chat_id: str
    prompt: str
    use_cpu: Optional[bool] = None  # Optional override
    files: Optional[List[dict]] = None
    collection: Optional[dict] = None

class ChatCreate(BaseModel):
    name: Optional[str] = "New Chat"

class ChatUpdate(BaseModel):
    name: Optional[str] = None

# =============== Database Utility Functions ===============
def generate_chat_name(prompt: str, max_length: int = 50) -> str:
    """Generate a chat name from the initial prompt."""
    # Clean and truncate the prompt to create a name
    clean_prompt = re.sub(r'\s+', ' ', prompt.strip())
    if len(clean_prompt) > max_length:
        return clean_prompt[:max_length] + "..."
    return clean_prompt

def get_messages_from_db(db: Session, chat_id: str) -> List[Message]:
    """Retrieve messages for a chat from the database."""
    db_messages = db.query(MessageModel).filter(MessageModel.chat_id == chat_id).order_by(MessageModel.created_at).all()
    
    # Convert to Pydantic models
    messages = []
    for msg in db_messages:
        messages.append(Message(
            content=msg.content,
            isUser=msg.is_user,
            created_at=msg.created_at
        ))
    
    return messages

def save_messages_to_db(db: Session, chat_id: str, user_prompt: str, assistant_response: str):
    """Save user and assistant messages to the database."""
    try:
        # First check if the chat exists, if not create it
        chat_exists_sql = text("SELECT 1 FROM chat.chats WHERE chat_id = :chat_id")
        chat_exists = db.execute(chat_exists_sql, {"chat_id": chat_id}).fetchone() is not None
        
        if not chat_exists:
            logger.debug(f"Chat {chat_id} does not exist, creating...")
            # Try to create the chat
            create_chat_sql = text("""
                INSERT INTO chat.chats (chat_id, user_id, name, created_at, updated_at)
                VALUES (:chat_id, 'system', :name, :created_at, :updated_at)
            """)
            db.execute(
                create_chat_sql, 
                {
                    "chat_id": chat_id,
                    "name": "New Chat",
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
        
        # Generate UUIDs for messages
        user_message_id = str(uuid.uuid4())
        assistant_message_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Save user message using direct SQL
        user_sql = text("""
            INSERT INTO chat.messages (message_id, chat_id, content, is_user, created_at)
            VALUES (:message_id, :chat_id, :content, :is_user, :created_at)
        """)
        
        db.execute(
            user_sql,
            {
                "message_id": user_message_id,
                "chat_id": chat_id,
                "content": user_prompt,
                "is_user": True,
                "created_at": now
            }
        )
        
        # Save assistant message using direct SQL
        assistant_sql = text("""
            INSERT INTO chat.messages (message_id, chat_id, content, is_user, created_at)
            VALUES (:message_id, :chat_id, :content, :is_user, :created_at)
        """)
        
        db.execute(
            assistant_sql,
            {
                "message_id": assistant_message_id,
                "chat_id": chat_id,
                "content": assistant_response,
                "is_user": False,
                "created_at": datetime.utcnow()  # Slightly later timestamp
            }
        )
        
        # Check if this is the first message and update chat name if so
        message_count_sql = text("SELECT COUNT(*) FROM chat.messages WHERE chat_id = :chat_id")
        message_count = db.execute(message_count_sql, {"chat_id": chat_id}).scalar()
        
        if message_count <= 2:  # Just the two messages we added
            chat_name_sql = text("SELECT name FROM chat.chats WHERE chat_id = :chat_id")
            chat_name = db.execute(chat_name_sql, {"chat_id": chat_id}).scalar()
            
            if chat_name == "New Chat":
                # Update chat name based on first message
                new_name = generate_chat_name(user_prompt)
                update_name_sql = text("""
                    UPDATE chat.chats 
                    SET name = :name, updated_at = :updated_at
                    WHERE chat_id = :chat_id
                """)
                
                db.execute(
                    update_name_sql,
                    {
                        "chat_id": chat_id,
                        "name": new_name,
                        "updated_at": datetime.utcnow()
                    }
                )
        else:
            # Just update the updated_at timestamp
            update_time_sql = text("""
                UPDATE chat.chats 
                SET updated_at = :updated_at
                WHERE chat_id = :chat_id
            """)
            
            db.execute(
                update_time_sql,
                {
                    "chat_id": chat_id,
                    "updated_at": datetime.utcnow()
                }
            )
        
        db.commit()
        logger.debug(f"Successfully saved messages to chat history.")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving messages: {str(e)}")
        # Don't raise exception so we don't break the chat flow

def format_chat_history(messages: List[Message]) -> str:
    """Format the last N messages into a conversation prompt."""
    recent_messages = messages[-MAX_HISTORY:]
    lines = []
    
    # Start with an empty line for better separation
    lines.append("")
    
    for msg in recent_messages:
        role = "User" if msg.isUser else "Assistant"
        lines.append(f"{role}: {msg.content.strip()}")
    
    # Ensure we don't end with a newline if the last message was from the assistant
    formatted = "\n".join(lines)
    #if not formatted.endswith("User:"):
        #formatted += "\nAssistant:"
    return formatted

def clean_final_response(text: str) -> str:
    """Remove system prompt, leftover tags, finalize punctuation, etc."""
    if not text:
        return ""

    # Remove common prefixes
    for prefix in ["AI:", "Assistant:", "AI Assistant:"]:
        if text.lstrip().startswith(prefix):
            text = text.lstrip()[len(prefix):].strip()

    # Remove content after user markers
    for marker in STOP_SEQUENCES:
        if marker in text:
            text = text.split(marker)[0].strip()

    # Check for repetitive patterns that might indicate the model is stuck
    if "User: " in text and text.count("User: ") > 1:
        # If multiple "User:" instances, keep only until the first one
        text = text.split("User: ")[0].strip()

    # Final formatting
    text = text.strip()
    # Only add a period if the text doesn't end with punctuation
    if text and text[-1] not in ".!?":
        text += "."
    return text

# =============== Streaming Endpoint ===============
@router.post("/generate_stream")
async def generate_stream(request: ChatRequest, db: Session = Depends(get_admin_db)):
    """
    Stream model responses using the stream service.
    Handles context preparation and calls the appropriate streaming function.
    """
    logger.debug("\n===== GENERATE_STREAM REQUEST DATA =====")
    logger.debug(f"Request chat_id: {request.chat_id}, Prompt: {request.prompt[:50]}...")
    logger.debug(f"Has files: {request.files is not None}, Has collection: {request.collection is not None}")
    if request.collection: logger.debug(f"Collection: {request.collection.get('id', 'N/A')}")
    logger.debug("==========================================\n")
    
    # Verify chat exists (or handle creation implicitly? Check save_messages_to_db)
    # chat = db.query(ChatModel).filter(ChatModel.chat_id == request.chat_id).first()
    # if not chat: ... (save_messages_to_db handles chat creation if needed)
    
    # Get messages from database
    messages = get_messages_from_db(db, request.chat_id)
    
    # Retrieve any documents associated with this chat
    documents_content = ""
    try:
        # Use direct SQL to retrieve document content
        docs_sql = text("""
            SELECT document_id, filename, content 
            FROM chat.documents
            WHERE chat_id = :chat_id
            ORDER BY created_at
        """)
        
        doc_rows = db.execute(docs_sql, {"chat_id": request.chat_id}).fetchall()
        print(doc_rows)
        if doc_rows:
            doc_parts = []
            for doc in doc_rows:
                # Skip empty content
                if not doc.content:
                    continue
                    
                # Format document content with filename
                doc_parts.append(f"--- Start of File: {doc.filename} ---\n{doc.content}\n--- End of File: {doc.filename} ---")
            
            if doc_parts:
                documents_content = "\n\n".join(doc_parts)
                logger.debug(f"Retrieved {len(doc_parts)} documents from database for chat {request.chat_id}")
    except Exception as e:
        logger.error(f"Error retrieving documents for chat {request.chat_id}: {e}", exc_info=True)
        # Continue without documents if there's an error
    
    # --- Start Context Assembly ---
    prompt_parts = []

    # 1. System Prompt
    prompt_parts.append(SYSTEM_PROMPT)
    
    # 2. Add previously saved document content (if any)
    if documents_content:
        prompt_parts.append(f"\n\nPreviously Uploaded Documents:\n{documents_content}")
    
    # 3. Process file context (if provided in the JSON request body)
    file_context_str = ""
    if request.files:
        try:
            # Pass the list of file dictionaries directly from the request body
            # Include the chat_id for document storage and db session
            file_context_str = process_file_context(request.files, chat_id=request.chat_id, db=db)
            if file_context_str:
                logger.debug(f"Adding file context (length: {len(file_context_str)}) to prompt.")
                # Add separator and context
                prompt_parts.append(f"\n\nNewly Attached Files:\n{file_context_str}") 
            else:
                 logger.debug("File processing returned empty context.")
        except Exception as e:
            logger.error(f"Error processing file content from JSON payload: {e}", exc_info=True)
            # Optionally add an error message to the context?
            # prompt_parts.append("\n\n[Error processing attached files]" )
    
    # 4. Chat History
    formatted_history = format_chat_history_for_prompt(messages) # Use renamed function
    if formatted_history:
        prompt_parts.append(f"\n\nChat History:\n{formatted_history}") # Add separator

    # 5. Current User Prompt
    # Add an indicator if files were attached
    if request.files:
        request.prompt = f'{request.prompt}  📁 {len(request.files)} files added'
        #prompt_parts.append(f'\n\nCurrent Prompt:\nUser (with attached files): {request.prompt}') # Indicate files were attached

    prompt_parts.append(f'\n\nCurrent Prompt:\nUser: {request.prompt}') # Regular prompt
    
    # 6. Assistant Trigger
    prompt_parts.append(f'\nAssistant: ')

    # Combine all parts
    prompt_context = "".join(prompt_parts)
    # --- End Context Assembly ---

    logger.debug(f"Final prompt context length: {len(prompt_context)} characters")
    print(f"Final prompt context: {prompt_context}\n\n\n\n\n\n")
    
    # Avoid logging potentially large base64 strings from files
    '''log_preview_limit = 500
    context_preview = prompt_context
    if file_context_str: # If files were processed, be more careful about preview
        preview_parts = []
        preview_parts.append(SYSTEM_PROMPT)
        if documents_content: preview_parts.append(f"\n\nPreviously Uploaded Documents:\n{documents_content}")
        if file_context_str: preview_parts.append(f"\n\nNewly Attached Files:\n{file_context_str}")
        if formatted_history: preview_parts.append(f"\n\nChat History:\n{formatted_history}")
        preview_parts.append(f'\n\nUser: {request.prompt}')
        preview_parts.append(f'\nAssistant: ')
        context_preview = "".join(preview_parts)
        # Limit preview length even more if files are involved
        log_preview_limit = min(log_preview_limit, 200 + len(request.prompt))

    logger.debug(f"Final prompt context (preview): {context_preview[:log_preview_limit]}...")'''

    # Determine if CPU or GPU should be used
    use_cpu_mode = request.use_cpu if request.use_cpu is not None else USE_CPU

    if use_cpu_mode:
        logger.debug("Calling fixed response stream service")
        # Add a small delay to make the loading indicator visible
        await asyncio.sleep(2.5)
        return await generate_with_fixed_stream(
            messages=messages, 
            user_prompt=request.prompt, 
            chat_id=request.chat_id, 
            db=db, 
            save_messages_func=save_messages_to_db # Pass the function
        )
    else:
        # Health check for TGI (moved to stream_service? No, keep here before calling)
        if TGI_HEALTH_ENABLED: # Use constant defined above
             try:
                 async with httpx.AsyncClient(timeout=10.0) as client:
                     health_check = await client.get(f"{TGI_URL}/health", timeout=5.0) # Use constant
                     if health_check.status_code != 200:
                         logger.warning(f"TGI health check failed (Status: {health_check.status_code}). Proceeding anyway.")
             except Exception as e:
                 logger.warning(f"TGI health check failed: {str(e)}. Proceeding anyway.")

        logger.debug("Calling TGI stream service")
        try:
            return await generate_with_tgi_stream(
                full_prompt=prompt_context, 
                messages=messages, 
                user_prompt=request.prompt, 
                chat_id=request.chat_id, 
                db=db,
                save_messages_func=save_messages_to_db # Pass the function
            )
        except Exception as e:
            logger.error(f"Error during TGI stream generation: {str(e)}", exc_info=True)
            # Return an error response through SSE if possible
            async def error_stream(): 
                yield f"data: {json.dumps({'error': f'Stream generation failed: {str(e)}'})}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(error_stream(), media_type="text/event-stream")

# =============== Create / Retrieve Chat Endpoints ===============
@router.post("/create_chat")
def create_chat(chat_create: ChatCreate = None, user: User = Depends(get_current_user), db: Session = Depends(get_admin_db)):
    """Create a new chat session."""
    chat_id = str(uuid.uuid4())
    created_at = datetime.utcnow()
    
    name = "New Chat"
    if chat_create and chat_create.name:
        name = chat_create.name
    
    # Try direct SQL insertion instead of ORM
    try:
        insert_sql = text("""
            INSERT INTO chat.chats (chat_id, user_id, name, created_at, updated_at)
            VALUES (:chat_id, :user_id, :name, :created_at, :updated_at)
        """)
        
        db.execute(
            insert_sql, 
            {
                "chat_id": chat_id,
                "user_id": str(user.id),
                "name": name,
                "created_at": created_at,
                "updated_at": created_at
            }
        )
        db.commit()
        
        return {
            "message": "Chat created successfully",
            "chat_id": chat_id,
            "name": name
        }
    except Exception as e:
        db.rollback()
        print(f"Error creating chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create chat: {str(e)}")

@router.get("/chats/{chat_id}")
def get_chat(chat_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_admin_db)):
    """Retrieve a chat session by ID."""
    try:
        # Use direct SQL to query chat
        chat_sql = text("""
            SELECT chat_id, user_id, name, created_at, updated_at 
            FROM chat.chats 
            WHERE chat_id = :chat_id AND user_id = :user_id
        """)
        
        result = db.execute(chat_sql, {"chat_id": chat_id, "user_id": str(user.id)}).fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Get messages using direct SQL
        messages_sql = text("""
            SELECT message_id, chat_id, content, is_user, created_at
            FROM chat.messages
            WHERE chat_id = :chat_id
            ORDER BY created_at
        """)
        
        message_rows = db.execute(messages_sql, {"chat_id": chat_id}).fetchall()
        
        # Convert to appropriate format
        messages = []
        for row in message_rows:
            messages.append({
                "content": row.content,
                "isUser": row.is_user,
                "created_at": row.created_at.isoformat() if row.created_at else None
            })
        
        return {
            "chat_id": result.chat_id,
            "user_id": result.user_id,
            "name": result.name,
            "created_at": result.created_at.isoformat() if result.created_at else None,
            "updated_at": result.updated_at.isoformat() if result.updated_at else None,
            "messages": messages
        }
    except Exception as e:
        if "Chat not found" in str(e):
            raise
        print(f"Error retrieving chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat: {str(e)}")

@router.put("/chats/{chat_id}")
def update_chat(chat_id: str, chat_update: ChatUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_admin_db)):
    """Update a chat session."""
    try:
        # Check if chat exists and belongs to the user using raw SQL with casting
        check_sql = text("""
            SELECT 1 FROM chat.chats 
            WHERE chat_id = :chat_id AND user_id::text = :user_id
        """)
        
        chat_exists = db.execute(
            check_sql, 
            {"chat_id": chat_id, "user_id": str(user.id)} # Pass user_id as string
        ).fetchone() is not None
        
        if not chat_exists:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Update the chat name if provided using raw SQL with casting
        if chat_update.name is not None:
            update_sql = text("""
                UPDATE chat.chats 
                SET name = :name
                WHERE chat_id = :chat_id AND user_id::text = :user_id
            """)
            
            db.execute(
                update_sql, 
                {
                    "chat_id": chat_id,
                    "user_id": str(user.id), # Pass user_id as string
                    "name": chat_update.name.strip() # Ensure name is stripped
                }
            )
            db.commit()
            
            # Fetch the updated chat details to return
            fetch_sql = text("""
                SELECT chat_id, name, updated_at 
                FROM chat.chats 
                WHERE chat_id = :chat_id AND user_id::text = :user_id
            """)
            updated_chat_data = db.execute(
                fetch_sql,
                {"chat_id": chat_id, "user_id": str(user.id)}
            ).fetchone()

            if not updated_chat_data:
                 # Should not happen if update succeeded, but good to check
                 raise HTTPException(status_code=500, detail="Failed to fetch updated chat details.")

            return {
                "message": "Chat updated successfully",
                "chat": {
                    "chat_id": updated_chat_data.chat_id,
                    "name": updated_chat_data.name,
                    # Safely format datetime
                    #"updated_at": updated_chat_data.updated_at.isoformat() if updated_chat_data.updated_at else None 
                }
            }
        else:
            # If name wasn't provided, just return current details
            fetch_sql = text("""
                SELECT chat_id, name, updated_at 
                FROM chat.chats 
                WHERE chat_id = :chat_id AND user_id::text = :user_id
            """)
            current_chat_data = db.execute(
                fetch_sql,
                {"chat_id": chat_id, "user_id": str(user.id)}
            ).fetchone()
            
            if not current_chat_data:
                 raise HTTPException(status_code=404, detail="Chat not found (unexpected error during fetch).")
                  
            return {
                "message": "No update performed (name not provided)",
                "chat": {
                    "chat_id": current_chat_data.chat_id,
                    "name": current_chat_data.name,
                    #"updated_at": current_chat_data.updated_at.isoformat() if current_chat_data.updated_at else None
                }
            }
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating chat in chat.py: {str(e)}") # Added router info
        # Log the error properly in a real application
        # logger.error(f"Error updating chat {chat_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to update chat: {str(e)}")

@router.get("/chats")
def list_chats(user: User = Depends(get_current_user), db: Session = Depends(get_admin_db)):
    """List all chats for a user."""
    try:
        # Use direct SQL to query chats
        chats_sql = text("""
            SELECT chat_id, name, created_at, updated_at 
            FROM chat.chats 
            WHERE user_id = :user_id
            ORDER BY updated_at DESC
        """)
        
        result = db.execute(chats_sql, {"user_id": str(user.id)}).fetchall()
        
        # Format the results
        chats = []
        for row in result:
            # Get the first message for preview (optional)
            preview_sql = text("""
                SELECT content FROM chat.messages 
                WHERE chat_id = :chat_id AND is_user = true
                ORDER BY created_at ASC
                LIMIT 1
            """)
            preview_result = db.execute(preview_sql, {"chat_id": row.chat_id}).fetchone()
            preview = preview_result.content if preview_result else ""
            
            # Get message count
            count_sql = text("SELECT COUNT(*) FROM chat.messages WHERE chat_id = :chat_id")
            message_count = db.execute(count_sql, {"chat_id": row.chat_id}).scalar()
            
            # Truncate preview if too long
            if len(preview) > 100:
                preview = preview[:97] + "..."
            
            chats.append({
                "chat_id": row.chat_id,
                "name": row.name,
                "preview": preview,
                "message_count": message_count,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None
            })
        
        return {
            "chats": chats
        }
    
    except Exception as e:
        print(f"Error listing chats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list chats: {str(e)}")

@router.delete("/chats/{chat_id}")
def delete_chat(chat_id: str, user: User = Depends(get_current_user), db: Session = Depends(get_admin_db)):
    """Delete a chat session."""
    try:
        # First check if the chat exists and belongs to the user
        check_sql = text("""
            SELECT 1 FROM chat.chats 
            WHERE chat_id = :chat_id AND user_id = :user_id
        """)
        
        chat_exists = db.execute(
            check_sql, 
            {"chat_id": chat_id, "user_id": str(user.id)}
        ).fetchone()
        
        if not chat_exists:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Delete all documents associated with this chat
        delete_docs_sql = text("""
            DELETE FROM chat.documents
            WHERE chat_id = :chat_id
        """)
        db.execute(delete_docs_sql, {"chat_id": chat_id})
        
        # Delete all messages associated with this chat
        delete_messages_sql = text("""
            DELETE FROM chat.messages 
            WHERE chat_id = :chat_id
        """)
        db.execute(delete_messages_sql, {"chat_id": chat_id})
        
        # Delete the chat
        delete_chat_sql = text("""
            DELETE FROM chat.chats 
            WHERE chat_id = :chat_id AND user_id = :user_id
        """)
        db.execute(
            delete_chat_sql, 
            {"chat_id": chat_id, "user_id": str(user.id)}
        )
        
        db.commit()
        
        return {
            "message": "Chat deleted successfully",
            "chat_id": chat_id
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete chat: {str(e)}")

def format_chat_history_for_prompt(messages: List[Message]) -> str:
    """
    Formats the chat history for the model prompt.
    """
    # Limit history
    recent_messages = messages[-MAX_HISTORY:]
    if not recent_messages:
        return "" # Return empty string if no history

    formatted_lines = []
    for msg in recent_messages:
        role = "user" if msg.isUser else "assistant"
        # Ensure content is stripped and handle potential None/empty cases safely
        content = (msg.content or "").strip()
        formatted_lines.append(f"{role.capitalize()}: {content}")
    
    # Convert to a single string format for the model
    history_context = "\n".join(formatted_lines)
    
    logger.debug(f"Formatted chat history prepared (length: {len(history_context)})" )
    return history_context # Return just the formatted history string