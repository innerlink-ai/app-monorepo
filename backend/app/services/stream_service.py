import os
import re
import uuid
import asyncio
import random
import json
from datetime import datetime
from typing import List, Optional

import httpx
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel # Assuming Message is defined here or imported

# Assuming save_messages_to_db is imported or passed correctly
# from ..routers.chat import save_messages_to_db, Message 
# Placeholder for Message type if not imported globally
class Message(BaseModel):
    content: str
    isUser: bool
    created_at: Optional[datetime] = None

# Change to absolute import
from logger import get_logger

logger = get_logger("stream_service")

# =============== TGI Endpoint Constants ===============
TGI_URL = os.getenv("TGI_URL", "http://localhost:3000")
TGI_TIMEOUT = int(os.getenv("TGI_TIMEOUT", "60"))


# =============== Model Context Constants ===============
# These might be needed for calculations within this service
CONTEXT_LENGTH = int(os.getenv("CONTEXT_LENGTH", "2048"))
MAX_PROMPT_LENGTH_CHARS = int(os.getenv("MAX_PROMPT_LENGTH_CHARS", str(1024 * 3)))

# Define stop sequences specific to TGI/streaming
TGI_STOP_SEQUENCES = ["User:", "<|endoftext|>", "Human:", "User"]
# General Stop sequences might still be needed for cleaning
GENERAL_STOP_SEQUENCES = ["User:", "\nUser:", "<|endoftext|>", "Human:", "\nHuman:", "Assistant:", "\nAssistant:"]

# =============== Helper Functions ===============

def calculate_max_new_tokens(prompt, context_window=CONTEXT_LENGTH, buffer=50):
    """
    Dynamically calculate the maximum number of tokens that can be generated
    based on the input prompt length and model's context window.
    """
    estimated_prompt_tokens = len(prompt) // 4
    max_tokens = context_window - estimated_prompt_tokens - buffer
    return max(10, max_tokens)

def clean_partial_text(text: str) -> str:
    """Remove random excessive spacing in partial chunks."""
    return re.sub(r"\s+", " ", text)

def clean_final_response(text: str) -> str:
    """Remove system prompt, leftover tags, finalize punctuation, etc."""
    if not text:
        return ""

    for prefix in ["AI:", "Assistant:", "AI Assistant:"]:
        if text.lstrip().startswith(prefix):
            text = text.lstrip()[len(prefix):].strip()

    for marker in GENERAL_STOP_SEQUENCES:
        if marker in text:
            text = text.split(marker)[0].strip()

    if "User: " in text and text.count("User: ") > 1:
        text = text.split("User: ")[0].strip()

    text = text.strip()
    if text and text[-1] not in ".!?":
        text += "."
    return text

def make_sse_chunk(text: str, model_name: str = "tgi-model") -> str:
    """
    Return a single chunk in Server-Sent Events format.
    """
    response_chunk = {
        "id": f"chatcmpl-{uuid.uuid4().hex[:10]}",
        "object": "chat.completion.chunk",
        "created": int(datetime.now().timestamp()),
        "choices": [
            {
                "index": 0,
                "delta": {"content": text},
                "finish_reason": None
            }
        ],
        "model": model_name
    }
    return f"data: {json.dumps(response_chunk)}\n\n"

# =============== Streaming Functions ===============

async def generate_with_fixed_stream(
    messages: List[Message], 
    user_prompt: str, 
    chat_id: str, 
    db: Session, 
    save_messages_func # Pass the function to save messages
):
    """Stream fixed responses when models aren't suitable."""
    async def event_generator():
        buffer = []
        try:
            logger.debug("Using fixed response generator")
            yield make_sse_chunk("", model_name="fixed-response") # Initial empty chunk
            
            responses = [
                "I understand. Could you tell me more about what you're looking for?",
                "That's an interesting point. Let me help you with that.",
                "I'm here to assist you. What specific information do you need?",
                "Thanks for your message. I'd be happy to help with your request.",
                "I'm processing your request. Is there anything specific you'd like to know?",
                "I appreciate your question. Let me provide you with a helpful response."
            ]
            
            words = user_prompt.lower().split()
            if any(word in ["hello", "hi", "hey"] for word in words):
                response = "Hello! How can I help you today?"
            elif any(word in ["thanks", "thank"] for word in words):
                response = "You're welcome! Is there anything else I can help with?"
            elif "?" in user_prompt:
                response = "That's an interesting question. Let me think about that. While I don't have a complete answer right now, I'd be happy to discuss it further."
            else:
                response = random.choice(responses)
                
            for char in response:
                buffer.append(char)
                yield make_sse_chunk(char, model_name="fixed-response")
                await asyncio.sleep(0.01)
            
            # Final completion marker
            end_chunk_payload = {
                 "id": f"chatcmpl-{uuid.uuid4().hex[:10]}",
                 "object": "chat.completion.chunk",
                 "created": int(datetime.now().timestamp()),
                 "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                 "model": "fixed-response"
            }
            yield f"data: {json.dumps(end_chunk_payload)}\n\n"
            yield "data: [DONE]\n\n"
            
            complete_response = "".join(buffer)
            save_messages_func(db, chat_id, user_prompt, complete_response)
            logger.debug(f"Successfully added fixed response to chat history.")
            
        except Exception as e:
            logger.error(f"Error in fixed response: {str(e)}")
            error_json = json.dumps({"error": f"Fixed response error: {str(e)}"})
            yield f"data: {error_json}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")


async def generate_with_tgi_stream(
    full_prompt: str, 
    messages: List[Message], 
    user_prompt: str, 
    chat_id: str, 
    db: Session,
    save_messages_func # Pass the function to save messages
):
    """Stream responses from the TGI GPU model."""
    logger.info(f"Starting TGI stream generation for chat_id: {chat_id}")
    logger.info(f"Prompt length: {len(full_prompt)} characters")
    logger.debug(f"Prompt content (first 500 chars): {full_prompt[:500]}...")

    # Limit prompt length before sending to TGI
    limited_prompt = full_prompt[:MAX_PROMPT_LENGTH_CHARS]
    if len(full_prompt) > MAX_PROMPT_LENGTH_CHARS:
        logger.warning(f"Prompt truncated from {len(full_prompt)} to {len(limited_prompt)} characters")

    max_new_tokens = calculate_max_new_tokens(limited_prompt, context_window=CONTEXT_LENGTH)

    payload = {
        "inputs": limited_prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": 0.9,
            "top_p": 0.9,
            "stream": True,
            "stop": TGI_STOP_SEQUENCES,
            "do_sample": True
        }
    }
    logger.info(f"Configured TGI with max_new_tokens: {max_new_tokens}")

    async def event_generator():
        buffer = []
        full_text = ""
        try:
            logger.info(f"Making request to TGI service at {TGI_URL}/generate_stream")
            async with httpx.AsyncClient(timeout=180.0) as client:
                async with client.stream(
                    "POST", 
                    f"{TGI_URL}/generate_stream",
                    json=payload,
                    headers={"Accept": "text/event-stream"},
                    timeout=180.0
                ) as response:
                    logger.info(f"TGI response status: {response.status_code}")
                    if response.status_code != 200:
                        error_detail = await response.aread()
                        error_msg = f"Model error: {error_detail.decode('utf-8')}"
                        logger.error(f"TGI response error: {response.status_code}, details: {error_msg}")
                        yield f"data: {json.dumps({'error': error_msg})}\n\n"
                        yield "data: [DONE]\n\n"
                        return
                    
                    logger.info("Processing TGI stream response")
                    token_count = 0
                    response_started = False
                    empty_chunk_count = 0
                    max_empty_chunks = 10
                    
                    async for line in response.aiter_lines():
                        if not line or not line.strip() or not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            logger.info("Received [DONE] marker")
                            break
                        
                        try:
                            if data.startswith('"index"'): data = '{' + data # Fix potential JSON issue
                            if data == "{}" or not data: # Handle empty chunks
                                empty_chunk_count += 1
                                if empty_chunk_count >= max_empty_chunks: break
                                await asyncio.sleep(0.1)
                                continue
                            
                            chunk = json.loads(data)
                            token_text = None
                            if "token" in chunk and "text" in chunk["token"]: token_text = chunk["token"]["text"]
                            elif "generated_text" in chunk: token_text = chunk["generated_text"]
                            elif "text" in chunk: token_text = chunk["text"]
                                
                            if token_text is None: continue
                            token_count += 1
                            if token_text in ["</s>", "<|endoftext|>", "<eos>"]: break # Skip EOS
                            
                            # Handle prefix removal at start
                            current_accumulated = full_text + token_text
                            cleaned_token = token_text
                            if not response_started:
                                for prefix in ["Assistant:", "Me:", "Assistant", "Me"]:
                                    if prefix in current_accumulated[:len(prefix)+5]: # Check beginning
                                       # Remove prefix from token if it overlaps
                                       if token_text.startswith(prefix): 
                                           cleaned_token = token_text[len(prefix):].lstrip()
                                       elif prefix.startswith(token_text): # Token is just part of prefix
                                           cleaned_token = "" 
                                       elif prefix in token_text:
                                            cleaned_token = token_text.split(prefix, 1)[-1].lstrip()

                                if cleaned_token != token_text: logger.info(f"Removed prefix overlap from token")    
                                response_started = True
                            
                            full_text += cleaned_token # Accumulate cleaned text

                            # Check for stop sequences
                            should_stop = False
                            final_token_text = cleaned_token
                            for seq in TGI_STOP_SEQUENCES:
                                if seq in full_text[-len(seq)-5:]: # Check recent text
                                    if seq in cleaned_token:
                                        idx = cleaned_token.find(seq)
                                        final_token_text = cleaned_token[:idx]
                                        should_stop = True
                                        break
                                    # Check if stop sequence spans across chunks
                                    combined_end = full_text[-len(seq)-5:] 
                                    if seq in combined_end and combined_end.endswith(seq):
                                        # How much of the current token is part of the sequence?
                                        overlap = len(cleaned_token) - (len(combined_end) - combined_end.find(seq))
                                        if overlap > 0: 
                                            final_token_text = cleaned_token[:-overlap]
                                        else:
                                            final_token_text = cleaned_token # Sequence was in previous tokens
                                        should_stop = True
                                        break
                            
                            if final_token_text:
                                buffer.append(final_token_text)
                                yield make_sse_chunk(final_token_text, model_name="tgi-model")
                            
                            if should_stop:
                                logger.info("Stop sequence detected, ending generation")
                                break
                                
                        except json.JSONDecodeError as e:
                            logger.warning(f"JSON decode error: {e} on data: {data}")
                            continue
                    
                    logger.info(f"Stream complete. Processed {token_count} tokens.")
                    
                    if token_count == 0 and response.status_code == 200:
                        logger.warning("No tokens received from TGI despite 200 OK, generating fallback.")
                        fallback_text = "I'm sorry, I couldn't generate a proper response. Please try rephrasing."
                        buffer.append(fallback_text)
                        yield make_sse_chunk(fallback_text, model_name="tgi-model")
                        
                    # Final completion marker
                    end_chunk_payload = {
                        "id": f"chatcmpl-{uuid.uuid4().hex[:10]}",
                        "object": "chat.completion.chunk",
                        "created": int(datetime.now().timestamp()),
                        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                        "model": "tgi-model"
                    }
                    yield f"data: {json.dumps(end_chunk_payload)}\n\n"
                    yield "data: [DONE]\n\n"
                    
                    if buffer:
                        complete_response = clean_final_response("".join(buffer))
                        logger.info(f"Final response length: {len(complete_response)}")
                        save_messages_func(db, chat_id, user_prompt, complete_response)
                        logger.info(f"Saved TGI response to chat history")
                    else:
                        logger.error("Generated empty response!")
                        
        except httpx.RequestError as e:
            logger.error(f"Network error connecting to TGI: {str(e)}")
            yield f"data: {json.dumps({'error': f'Network error: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"TGI stream generation error: {str(e)}", exc_info=True)
            yield f"data: {json.dumps({'error': f'TGI generation error: {str(e)}'})}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    ) 