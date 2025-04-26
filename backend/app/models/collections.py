from sqlalchemy import Column, String, Integer, Text, Boolean, DateTime, ForeignKey, BigInteger, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from typing import List, Optional
import uuid
import os
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID

# Import database connections
from database import get_collections_db, CollectionsBase
from sqlalchemy.orm import relationship, Session

# Update the Collection model to include encryption flag
class Collection(CollectionsBase):
    __tablename__ = "collections"
    __table_args__ = {"schema": "collections"}
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), nullable=False)
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    description = Column(Text)
    is_encrypted = Column(Boolean, default=True)  # Added encryption flag, default to True
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    documents = relationship("Document", back_populates="collection", cascade="all, delete-orphan")

# Update the Pydantic schemas in the router file

# Add is_encrypted to CollectionBase
class CollectionBase(BaseModel):
    name: str
    type: str
    description: Optional[str] = None
    is_encrypted: bool = True  # Default to True

# Make sure to update the response model too
class CollectionResponse(CollectionBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    document_count: int = 0
    
    class Config:
        orm_mode = True
        from_attributes = True
        

class Document(CollectionsBase):
    __tablename__ = "documents"
    __table_args__ = {"schema": "collections"}
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_id = Column(PG_UUID(as_uuid=True), ForeignKey("collections.collections.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
    size = Column(BigInteger, nullable=False)
    file_path = Column(Text, nullable=False)
    content_type = Column(Text)
    is_encrypted = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(Text)
    
    collection = relationship("Collection", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(CollectionsBase):
    __tablename__ = "document_chunks"
    __table_args__ = {"schema": "collections"}
    
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(PG_UUID(as_uuid=True), ForeignKey("collections.documents.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    # Renamed from 'metadata' to 'chunk_metadata' to avoid conflict
    chunk_metadata = Column(JSONB)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    document = relationship("Document", back_populates="chunks")


class CollectionBase(BaseModel):
    name: str
    type: str
    description: Optional[str] = None

class CollectionCreate(CollectionBase):
    pass

class CollectionResponse(CollectionBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    document_count: int = 0
    
    class Config:
        orm_mode = True
        from_attributes = True

class DocumentBase(BaseModel):
    name: str
    type: str
    size: int
    file_path: str
    content_type: Optional[str] = None
    status: Optional[str] = 'not_processed'  # Can be 'not_processed', 'processing', 'completed', or 'unprocessable'

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: UUID
    collection_id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        from_attributes = True