import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

# Local modules
from common.curr_user import get_current_user
from data_models import User
from database import get_chat_db

router = APIRouter()

# =============== Pydantic Models ===============
class ChatResponse(BaseModel):
    chat_id: str
    name: str
    preview: Optional[str] = None
    message_count: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ChatsListResponse(BaseModel):
    chats: List[ChatResponse]

class ChatCreate(BaseModel):
    name: Optional[str] = "New Chat"

class ChatUpdate(BaseModel):
    name: Optional[str] = None


# =============== Chat History Endpoints ===============
@router.get("/chats", response_model=ChatsListResponse)
async def list_chats(
    search_query: Optional[str] = Query(None, description="Optional search query"),
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_chat_db)
):
    """List all chats for a user with optional search filtering."""
    try:
        # Base SQL query for chats - using explicit type casting for UUID
        base_query = """
            SELECT chat_id, name, created_at, updated_at 
            FROM chat.chats 
            WHERE user_id::text = :user_id::text
        """
        
        # Add search condition if query is provided
        if search_query:
            search_query = search_query.strip()
            if search_query:
                search_condition = """
                    AND (
                        name ILIKE :search_pattern
                        OR chat_id IN (
                            SELECT chat_id FROM chat.messages 
                            WHERE content ILIKE :search_pattern
                        )
                    )
                """
                base_query += search_condition
        
        # Add ordering
        base_query += " ORDER BY updated_at DESC"
        
        # Execute the query
        params = {
            "user_id": str(user.id),
            "search_pattern": f"%{search_query}%" if search_query else None
        }
        result = db.execute(text(base_query), params).fetchall()
        
        # Format the results
        chats = []
        for row in result:
            # Get the first user message for preview
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
            
            chats.append(ChatResponse(
                chat_id=row.chat_id,
                name=row.name,
                preview=preview,
                message_count=message_count,
                created_at=row.created_at.isoformat() if row.created_at else None,
                updated_at=row.updated_at.isoformat() if row.updated_at else None
            ))
        
        return ChatsListResponse(chats=chats)
    
    except Exception as e:
        print(f"Error listing chats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list chats: {str(e)}")

@router.post("/create_chat")
async def create_chat(
    chat_create: ChatCreate = None, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_chat_db)
):
    """Create a new chat session."""
    try:
        chat_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        
        name = "New Chat"
        if chat_create and chat_create.name:
            name = chat_create.name
        
        # Insert the new chat - store user_id as string explicitly
        insert_sql = text("""
            INSERT INTO chat.chats (chat_id, user_id, name, created_at, updated_at)
            VALUES (:chat_id, :user_id, :name, :created_at, :updated_at)
        """)
        
        db.execute(
            insert_sql, 
            {
                "chat_id": chat_id,
                "user_id": str(user.id),  # Explicitly convert UUID to string
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

@router.delete("/chats/{chat_id}")
async def delete_chat(
    chat_id: str, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_chat_db)
):
    """Delete a chat session."""
    try:
        # First check if the chat exists and belongs to the user
        # Use explicit type casting for both sides of the comparison
        check_sql = text("""
            SELECT 1 FROM chat.chats 
            WHERE chat_id = :chat_id AND user_id::text = :user_id::text
        """)
        
        chat_exists = db.execute(
            check_sql, 
            {"chat_id": chat_id, "user_id": str(user.id)}
        ).fetchone() is not None
        
        if not chat_exists:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Delete messages first because of foreign key constraints
        delete_messages_sql = text("""
            DELETE FROM chat.messages 
            WHERE chat_id = :chat_id
        """)
        
        db.execute(delete_messages_sql, {"chat_id": chat_id})
        
        # Delete the chat with explicit type casting
        delete_chat_sql = text("""
            DELETE FROM chat.chats 
            WHERE chat_id = :chat_id AND user_id::text = :user_id::text
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
    except HTTPException:
        # Pass through HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        print(f"Error deleting chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete chat: {str(e)}")

@router.put("/chats/{chat_id}")
async def update_chat(
    chat_id: str, 
    chat_update: ChatUpdate, 
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_chat_db)
):
    """Update a chat session."""
    try:
        # Check if chat exists and belongs to the user
        # Use explicit type casting for user_id
        check_sql = text("""
            SELECT 1 FROM chat.chats 
            WHERE chat_id = :chat_id AND user_id::text = :user_id::text
        """)
        
        chat_exists = db.execute(
            check_sql, 
            {"chat_id": chat_id, "user_id": str(user.id)}
        ).fetchone() is not None
        
        if not chat_exists:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Update the chat name if provided
        if chat_update.name is not None:
            update_sql = text("""
                UPDATE chat.chats 
                SET name = :name, updated_at = :updated_at
                WHERE chat_id = :chat_id AND user_id::text = :user_id::text
            """)
            
            db.execute(
                update_sql, 
                {
                    "chat_id": chat_id,
                    "user_id": str(user.id),
                    "name": chat_update.name,
                    "updated_at": datetime.utcnow()
                }
            )
            
            db.commit()
        
        # Get updated chat details
        chat_sql = text("""
            SELECT chat_id, name, updated_at 
            FROM chat.chats 
            WHERE chat_id = :chat_id AND user_id::text = :user_id::text
        """)
        
        chat = db.execute(
            chat_sql, 
            {"chat_id": chat_id, "user_id": str(user.id)}
        ).fetchone()
        
        return {
            "message": "Chat updated successfully",
            "chat": {
                "chat_id": chat.chat_id,
                "name": chat.name,
                "updated_at": chat.updated_at.isoformat() if chat.updated_at else None
            }
        }
    except HTTPException:
        # Pass through HTTP exceptions
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update chat: {str(e)}")