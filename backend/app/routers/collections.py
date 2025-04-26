'''
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Query
from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, BigInteger, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from typing import List, Optional
import uuid
import os
from datetime import datetime
import shutil
from pathlib import Path
import json
from logger import get_logger

# Import database connections
from database import get_collections_db, CollectionsBase
from sqlalchemy.orm import relationship, Session
from models.collections import *

# Auth imports
from common.curr_user import get_current_user
from data_models import User

# Schemas
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

# UPLOAD_DIR setup
DATA_DIR = os.getenv('DATA_DIR', ".")
os.makedirs(DATA_DIR, exist_ok=True)

# Get logger for this module
logger = get_logger("collections")

# Create router
router = APIRouter()

# Collection endpoints
@router.post("/collections", response_model=CollectionResponse)
async def create_collection(
    collection: CollectionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_collections_db)
):
    db_collection = Collection(
        **collection.dict(),
        user_id=user.id  # Use the authenticated user's ID
    )
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    
    # Add document count
    setattr(db_collection, 'document_count', 0)
    
    return db_collection

@router.get("/collections", response_model=List[CollectionResponse])
async def get_collections(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_collections_db)
):
    collections = db.query(Collection).filter(Collection.user_id == user.id).all()
    
    # Add document count for each collection
    for collection in collections:
        doc_count = db.query(Document).filter(Document.collection_id == collection.id).count()
        setattr(collection, 'document_count', doc_count)
    
    return collections

@router.get("/collections/{collection_id}", response_model=CollectionResponse)
async def get_collection(
    collection_id: UUID, 
    user: User = Depends(get_current_user),
    db: Session = Depends(get_collections_db)
):
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == user.id  # Ensure the collection belongs to the user
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Add document count
    doc_count = db.query(Document).filter(Document.collection_id == collection.id).count()
    setattr(collection, 'document_count', doc_count)
    
    return collection



# Document endpoints
@router.post("/collections/{collection_id}/documents", response_model=DocumentResponse)
async def upload_document(
    collection_id: UUID,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_collections_db)
):
    # Verify collection exists and belongs to user
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == user.id  # Ensure the collection belongs to the user
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    # Create directory for this collection if it doesn't exist
    collection_dir = os.path.join(DATA_DIR, str(collection_id))
    os.makedirs(collection_dir, exist_ok=True)
    
    # Generate unique filename
    file_id = uuid.uuid4()
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(collection_dir, unique_filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create document record
    document = Document(
        collection_id=collection_id,
        name=file.filename,
        type=file_extension.lstrip('.').lower() or "unknown",
        size=os.path.getsize(file_path),
        file_path=file_path,  # This will now be the container path
        content_type=file.content_type
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document

@router.get("/collections/{collection_id}/documents", response_model=List[DocumentResponse])
async def get_documents(
    collection_id: UUID, 
    user: User = Depends(get_current_user),
    db: Session = Depends(get_collections_db)
):
    # Verify collection exists and belongs to user
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == user.id  # Ensure the collection belongs to the user
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    documents = db.query(Document).filter(Document.collection_id == collection_id).all()
    return documents
'''