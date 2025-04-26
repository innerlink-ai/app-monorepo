from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text
from typing import List, Optional, Dict, Any
import uuid
import json
from datetime import datetime
import redis
import os
from logger import get_logger

# Import existing auth and DB modules
from common.curr_user import get_current_user
from data_models import User
from database import get_collections_db

# Pydantic models
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

# Constants
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
OVERLAP = int(os.getenv('OVERLAP', '128'))

# Redis setup
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL)

# Create router
router = APIRouter(
    prefix="/embeddings",
    tags=["embeddings"]
)

# Get logger for this module
logger = get_logger("embeddings")

# =============== Models ===============
class EmbeddingRequest(BaseModel):
    collection_id: Optional[UUID] = None
    document_ids: List[UUID] = []

class EmbeddingStatusResponse(BaseModel):
    task_id: str
    collection_id: Optional[UUID] = None
    document_ids: List[UUID] = []
    status: str
    progress: float
    document_count: int
    processed_count: int
    
    class Config:
        from_attributes = True

class SearchQuery(BaseModel):
    query: str
    collection_id: Optional[UUID] = None
    limit: int = 10
    filter_metadata: Optional[Dict[str, Any]] = None

class SearchResult(BaseModel):
    document_id: UUID
    document_name: str
    collection_id: UUID
    collection_name: str
    chunk_text: str
    chunk_index: int
    similarity: float
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# =============== Redis Task Queue Functions ===============
def queue_embedding_task(task_id, task_type, collection_id=None, document_ids=None):
    """Add embedding task to Redis queue"""
    logger.info(f"Queueing embedding task: task_id={task_id}, type={task_type}, collection_id={collection_id}, document_ids={document_ids}")
    task_data = {
        "task_id": task_id,
        "task_type": task_type,
        "collection_id": str(collection_id) if collection_id else None,
        "document_ids": [str(doc_id) for doc_id in document_ids] if document_ids else [],
        "created_at": datetime.utcnow().isoformat()
    }
    redis_client.lpush("embedding_tasks", json.dumps(task_data))
    logger.info(f"Successfully queued task {task_id} in Redis")

def update_task_status(task_id, status, progress, document_count, processed_count, collection_id=None, document_ids=None):
    """Update task status in Redis"""
    task_data = {
        "task_id": task_id,
        "status": status,
        "progress": progress,
        "document_count": document_count,
        "processed_count": processed_count,
        "collection_id": str(collection_id) if collection_id else None,
        "document_ids": [str(doc_id) for doc_id in document_ids] if document_ids else [],
        "updated_at": datetime.utcnow().isoformat()
    }
    redis_client.set(f"embedding_task:{task_id}", json.dumps(task_data))
    logger.debug(f"Successfully updated task {task_id} status in Redis")

def get_task_status(task_id):
    """Get task status from Redis"""
    data = redis_client.get(f"embedding_task:{task_id}")
    if not data:
        return None
    return json.loads(data)

# =============== API Endpoints ===============
@router.post("/generate", response_model=EmbeddingStatusResponse)
async def generate_embeddings(
    request: EmbeddingRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_collections_db)
):
    """Generate embeddings for documents or a collection"""
    logger.info(f"Received embedding request: collection_id={request.collection_id}, document_ids={request.document_ids}")
    
    document_ids = []
    collection_id = None
    
    # Validate request
    if not request.document_ids and not request.collection_id:
        logger.error("Neither document_ids nor collection_id provided")
        raise HTTPException(status_code=400, detail="Either document_ids or collection_id must be provided")
    
    # Check document permissions if IDs provided
    if request.document_ids:
        for doc_id in request.document_ids:
            check_sql = sql_text("""
                SELECT d.id 
                FROM collections.documents d
                JOIN collections.collections c ON d.collection_id = c.id
                WHERE d.id = :doc_id AND c.user_id = :user_id
            """)
            
            doc = db.execute(check_sql, {"doc_id": str(doc_id), "user_id": str(user.id)}).fetchone()
            if not doc:
                logger.error(f"Document {doc_id} not found or access denied for user {user.id}")
                raise HTTPException(status_code=404, detail=f"Document {doc_id} not found or access denied")
            
            document_ids.append(doc_id)
    
    # Check collection permissions
    elif request.collection_id:
        collection_id = request.collection_id
        
        check_sql = sql_text("""
            SELECT id 
            FROM collections.collections 
            WHERE id = :collection_id AND user_id = :user_id
        """)
        
        collection = db.execute(check_sql, {"collection_id": str(collection_id), "user_id": str(user.id)}).fetchone()
        if not collection:
            logger.error(f"Collection {collection_id} not found or access denied for user {user.id}")
            raise HTTPException(status_code=404, detail="Collection not found or access denied")
    
    # Create task
    task_id = str(uuid.uuid4())
    logger.info(f"Created task ID: {task_id}")
    
    # Handle document IDs
    if document_ids:
        document_count = len(document_ids)
        logger.info(f"Processing {document_count} documents")
        
        # Initialize task status
        try:
            update_task_status(
                task_id, "queued", 0.0, document_count, 0,
                document_ids=document_ids
            )
            logger.info(f"Updated task status in Redis for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to update task status in Redis: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to initialize task status")
        
        # Queue task in Redis
        try:
            queue_embedding_task(
                task_id, "documents", 
                document_ids=document_ids
            )
            logger.info(f"Successfully queued task {task_id} for documents")
        except Exception as e:
            logger.error(f"Failed to queue task in Redis: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to queue task")
        
        return {
            "task_id": task_id,
            "collection_id": None,
            "document_ids": document_ids,
            "status": "queued", 
            "progress": 0.0,
            "document_count": document_count,
            "processed_count": 0
        }
    
    # Handle collection
    elif collection_id:
        doc_count_sql = sql_text("""
            SELECT COUNT(*) 
            FROM collections.documents 
            WHERE collection_id = :collection_id
        """)
        
        document_count = db.execute(doc_count_sql, {"collection_id": str(collection_id)}).scalar()
        logger.info(f"Processing collection {collection_id} with {document_count} documents")
        
        # Initialize task status
        try:
            update_task_status(
                task_id, "queued", 0.0, document_count, 0,
                collection_id=collection_id
            )
            logger.info(f"Updated task status in Redis for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to update task status in Redis: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to initialize task status")
        
        # Queue task in Redis
        try:
            queue_embedding_task(
                task_id, "collection", 
                collection_id=collection_id
            )
            logger.info(f"Successfully queued task {task_id} for collection")
        except Exception as e:
            logger.error(f"Failed to queue task in Redis: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to queue task")
        
        return {
            "task_id": task_id,
            "collection_id": collection_id,
            "document_ids": [],
            "status": "queued",
            "progress": 0.0,
            "document_count": document_count,
            "processed_count": 0
        }

@router.get("/status/{task_id}", response_model=EmbeddingStatusResponse)
async def get_embedding_status(
    task_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_collections_db)
):
    """Get status of an embedding task"""
    status_data = get_task_status(task_id)
    if not status_data:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # If task has a collection_id, verify ownership
    if status_data.get("collection_id"):
        check_sql = sql_text("""
            SELECT id 
            FROM collections.collections 
            WHERE id = :collection_id AND user_id = :user_id
        """)
        
        collection = db.execute(check_sql, {
            "collection_id": status_data["collection_id"], 
            "user_id": str(user.id)
        }).fetchone()
        
        if not collection:
            raise HTTPException(status_code=403, detail="Not authorized to access this task")
    
    # Convert document_ids back to UUIDs
    document_ids = []
    for doc_id in status_data.get("document_ids", []):
        try:
            document_ids.append(UUID(doc_id))
        except (ValueError, TypeError):
            continue
    
    # Format response
    collection_id = None
    if status_data.get("collection_id"):
        try:
            collection_id = UUID(status_data["collection_id"])
        except (ValueError, TypeError):
            pass
            
    return {
        "task_id": task_id,
        "collection_id": collection_id,
        "document_ids": document_ids,
        "status": status_data.get("status", "unknown"),
        "progress": status_data.get("progress", 0.0),
        "document_count": status_data.get("document_count", 0),
        "processed_count": status_data.get("processed_count", 0)
    }

@router.get("/document/{document_id}/status")
async def get_document_embedding_status(
    document_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_collections_db)
):
    """Get embedding status for a document"""
    # Verify document ownership
    check_sql = sql_text("""
        SELECT d.id, d.collection_id, d.status, d.metadata
        FROM collections.documents d
        JOIN collections.collections c ON d.collection_id = c.id
        WHERE d.id = :document_id AND c.user_id = :user_id
    """)
    
    document = db.execute(check_sql, {"document_id": str(document_id), "user_id": str(user.id)}).fetchone()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found or access denied")
    
    # If document is marked as unprocessable, return that status
    if document.status == 'unprocessable':
        return {
            "document_id": document_id,
            "status": "unprocessable",
            "chunks_processed": 0,
            "collection_id": document.collection_id,
            "metadata": None
        }
    
    # Get metadata from document if available
    metadata = document.metadata or {}
    total_chunks = metadata.get('total_chunks', 0) if metadata else 0
    processed_chunks = metadata.get('processed_chunks', 0) if metadata else 0
    
    # Determine status based on chunk count and document status
    status = document.status or 'not_processed'
    
    # If no metadata available, fall back to counting chunks
    if not processed_chunks and status != 'processing':
        chunk_sql = sql_text("""
            SELECT COUNT(*) as chunk_count
            FROM collections.document_chunks
            WHERE document_id = :document_id
        """)
        
        processed_chunks = db.execute(chunk_sql, {"document_id": str(document_id)}).scalar()
        
        if processed_chunks > 0:
            status = 'completed'
    
    return {
        "document_id": document_id,
        "status": status,
        "chunks_processed": processed_chunks,
        "total_chunks": total_chunks,
        "collection_id": document.collection_id,
        "metadata": metadata
    }

@router.get("/collection/{collection_id}/status", response_model=Optional[EmbeddingStatusResponse])
async def get_collection_status(
    collection_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_collections_db)
):
    """Get most recent embedding status for a collection"""
    # Verify collection ownership
    check_sql = sql_text("""
        SELECT id 
        FROM collections.collections 
        WHERE id = :collection_id AND user_id = :user_id
    """)
    
    collection = db.execute(check_sql, {"collection_id": str(collection_id), "user_id": str(user.id)}).fetchone()
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found or access denied")
    
    # Find tasks for this collection from Redis
    tasks = []
    for key in redis_client.scan_iter(f"embedding_task:*"):
        data = redis_client.get(key)
        if data:
            task = json.loads(data)
            if task.get("collection_id") == str(collection_id):
                tasks.append(task)
    
    if not tasks:
        # Count processed documents by checking chunks
        doc_sql = sql_text("""
            SELECT d.id
            FROM collections.documents d
            WHERE d.collection_id = :collection_id
        """)
        
        docs = db.execute(doc_sql, {"collection_id": str(collection_id)}).fetchall()
        document_count = len(docs)
        
        processed_count = 0
        for doc in docs:
            chunk_sql = sql_text("""
                SELECT COUNT(*) 
                FROM collections.document_chunks 
                WHERE document_id = :doc_id
            """)
            
            chunk_count = db.execute(chunk_sql, {"doc_id": str(doc.id)}).scalar()
            if chunk_count > 0:
                processed_count += 1
        
        status = "completed" if processed_count == document_count and document_count > 0 else "not_processed"
        progress = processed_count / document_count if document_count > 0 else 0.0
        
        return {
            "task_id": f"collection-status-{collection_id}",
            "collection_id": collection_id,
            "document_ids": [],
            "status": status,
            "progress": progress,
            "document_count": document_count,
            "processed_count": processed_count
        }
    
    # Sort by updated_at (newest first)
    tasks.sort(key=lambda t: t.get("updated_at", ""), reverse=True)
    latest_task = tasks[0]
    
    # Format response
    document_ids = []
    for doc_id in latest_task.get("document_ids", []):
        try:
            document_ids.append(UUID(doc_id))
        except (ValueError, TypeError):
            continue
    
    return {
        "task_id": latest_task["task_id"],
        "collection_id": collection_id,
        "document_ids": document_ids,
        "status": latest_task.get("status", "unknown"),
        "progress": latest_task.get("progress", 0.0),
        "document_count": latest_task.get("document_count", 0),
        "processed_count": latest_task.get("processed_count", 0)
    }