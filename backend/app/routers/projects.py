from fastapi import APIRouter, Depends, HTTPException, status, Body
from typing import List, Optional
from pydantic import BaseModel, UUID4
from sqlalchemy.orm import Session
from database import get_admin_db
from common.curr_user import get_current_user
from data_models import User
import uuid
from logger import get_logger
from sqlalchemy import text
import base64

# Set up logger
logger = get_logger("projects")

# Create router
router = APIRouter()

# Pydantic models for request/response
class DocumentBase(BaseModel):
    name: str
    content: str
    file_type: Optional[str] = None

class ProjectCreate(BaseModel):
    name: str
    custom_instructions: Optional[str] = None
    documents: Optional[List[DocumentBase]] = []

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    custom_instructions: Optional[str] = None

class ProjectDocument(BaseModel):
    doc_id: UUID4
    name: str
    file_type: Optional[str] = None

class ProjectResponse(BaseModel):
    project_id: UUID4
    name: str
    custom_instructions: Optional[str] = None
    created_at: str
    updated_at: str
    documents: List[ProjectDocument] = []

# Routes for projects
@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_admin_db)
):
    """Create a new project with optional documents"""
    try:
        # Generate a new project ID
        project_id = uuid.uuid4()
        
        # Insert project
        query = text("""
            INSERT INTO admin.projects (project_id, user_id, name, custom_instructions)
            VALUES (:project_id, :user_id, :name, :custom_instructions)
            RETURNING project_id, name, custom_instructions, created_at, updated_at
        """)
        
        result = db.execute(query, {
            "project_id": project_id,
            "user_id": current_user.id,
            "name": project.name,
            "custom_instructions": project.custom_instructions or ""
        })
        project_data = result.fetchone()
        
        # Process documents if any
        document_ids = []
        if project.documents:
            for doc in project.documents:
                doc_id = uuid.uuid4()
                doc_query = text("""
                    INSERT INTO admin.documents (doc_id, project_id, name, content, file_type)
                    VALUES (:doc_id, :project_id, :name, :content, :file_type)
                    RETURNING doc_id, name, file_type
                """)
                
                doc_result = db.execute(doc_query, {
                    "doc_id": doc_id,
                    "project_id": project_id,
                    "name": doc.name,
                    "content": doc.content,
                    "file_type": doc.file_type or "text/plain"
                })
                doc_data = doc_result.fetchone()
                document_ids.append({
                    "doc_id": doc_data.doc_id,
                    "name": doc_data.name,
                    "file_type": doc_data.file_type
                })
        
        db.commit()
        
        # Return project data
        return {
            "project_id": project_data.project_id,
            "name": project_data.name,
            "custom_instructions": project_data.custom_instructions,
            "created_at": project_data.created_at.isoformat(),
            "updated_at": project_data.updated_at.isoformat(),
            "documents": document_ids
        }
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_admin_db)
):
    """Get all projects for the current user"""
    try:
        # Get all projects for the user (basic info only)
        project_query = text("""
            SELECT project_id, name, custom_instructions, created_at, updated_at
            FROM admin.projects
            WHERE user_id = :user_id
            ORDER BY updated_at DESC
        """)
        
        project_results = db.execute(project_query, {"user_id": current_user.id})
        projects_base_data = project_results.fetchall()
        
        response = []
        for project_base in projects_base_data:
            project_id = project_base.project_id
            project_data = {
                "project_id": project_base.project_id,
                "name": project_base.name,
                "custom_instructions": project_base.custom_instructions,
                "created_at": project_base.created_at.isoformat(),
                "updated_at": project_base.updated_at.isoformat(),
                "documents": []
            }

            try:
                # Fetch documents for this project (separate query execution)
                doc_query = text("""
                    SELECT doc_id, name, file_type
                    FROM admin.documents
                    WHERE project_id = :project_id
                """)
                doc_result = db.execute(doc_query, {"project_id": project_id})
                project_data["documents"] = [
                    {"doc_id": doc.doc_id, "name": doc.name, "file_type": doc.file_type}
                    for doc in doc_result.fetchall()
                ]
            except Exception as doc_error:
                # Log error fetching documents for this specific project
                logger.error(f"Error fetching documents for project {project_id}: {doc_error}")
                # Continue with empty documents list

            response.append(project_data)
            
        return response
    
    except Exception as e:
        # This outer exception handles errors during the initial project fetch
        # or potentially other unexpected issues.
        db.rollback() # Rollback if the main query fails
        logger.error(f"Error fetching projects list: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch projects list: {str(e)}"
        )

@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_admin_db)
):
    """Get a specific project by ID"""
    try:
        # Check if project exists and belongs to user
        query = text("""
            SELECT project_id, name, custom_instructions, created_at, updated_at 
            FROM admin.projects 
            WHERE project_id = :project_id AND user_id = :user_id
        """)
        
        result = db.execute(query, {
            "project_id": project_id,
            "user_id": current_user.id
        })
        project = result.fetchone()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Get documents
        doc_query = text("""
            SELECT doc_id, name, file_type
            FROM admin.documents
            WHERE project_id = :project_id
        """)
        
        doc_result = db.execute(doc_query, {"project_id": project_id})
        documents = [
            {"doc_id": doc.doc_id, "name": doc.name, "file_type": doc.file_type}
            for doc in doc_result.fetchall()
        ]
        
        return {
            "project_id": project.project_id,
            "name": project.name,
            "custom_instructions": project.custom_instructions,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
            "documents": documents
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch project: {str(e)}"
        )

@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID4,
    project_update: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_admin_db)
):
    """Update a project's name or custom instructions"""
    try:
        # Check if project exists and belongs to user
        check_query = text("""
            SELECT project_id FROM admin.projects 
            WHERE project_id = :project_id AND user_id = :user_id
        """)
        
        check_result = db.execute(check_query, {
            "project_id": project_id,
            "user_id": current_user.id
        })
        
        if not check_result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Prepare update query with only provided fields
        update_fields = []
        params = {"project_id": project_id}
        
        if project_update.name is not None:
            update_fields.append("name = :name")
            params["name"] = project_update.name
            
        if project_update.custom_instructions is not None:
            update_fields.append("custom_instructions = :custom_instructions")
            params["custom_instructions"] = project_update.custom_instructions
        
        if not update_fields:
            # Nothing to update
            return await get_project(project_id, current_user, db)
        
        # Always update the updated_at timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        update_query = text(f"""
            UPDATE admin.projects
            SET {", ".join(update_fields)}
            WHERE project_id = :project_id
        """)
        
        db.execute(update_query, params)
        db.commit()
        
        # Return the updated project
        return await get_project(project_id, current_user, db)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )

@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_admin_db)
):
    """Delete a project and all associated data"""
    try:
        # Check if project exists and belongs to user
        check_query = text("""
            SELECT project_id FROM admin.projects 
            WHERE project_id = :project_id AND user_id = :user_id
        """)
        
        check_result = db.execute(check_query, {
            "project_id": project_id,
            "user_id": current_user.id
        })
        
        if not check_result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Delete project chats
        db.execute(
            text("DELETE FROM admin.project_chats WHERE project_id = :project_id"),
            {"project_id": project_id}
        )
        
        # Delete project documents
        db.execute(
            text("DELETE FROM admin.project_documents WHERE project_id = :project_id"),
            {"project_id": project_id}
        )
        
        # Delete the project itself
        db.execute(
            text("DELETE FROM admin.projects_encrypted WHERE project_id = :project_id"),
            {"project_id": project_id}
        )
        
        db.commit()
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )

@router.post("/projects/{project_id}/documents", response_model=ProjectDocument)
async def add_document(
    project_id: UUID4,
    document: DocumentBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_admin_db)
):
    """Add a document to an existing project"""
    try:
        # Check if project exists and belongs to user
        check_query = text("""
            SELECT project_id FROM admin.projects 
            WHERE project_id = :project_id AND user_id = :user_id
        """)
        
        check_result = db.execute(check_query, {
            "project_id": project_id,
            "user_id": current_user.id
        })
        
        if not check_result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Add document
        doc_id = uuid.uuid4()
        query = text("""
            INSERT INTO admin.documents (doc_id, project_id, name, content, file_type)
            VALUES (:doc_id, :project_id, :name, :content, :file_type)
            RETURNING doc_id, name, file_type
        """)
        
        result = db.execute(query, {
            "doc_id": doc_id,
            "project_id": project_id,
            "name": document.name,
            "content": document.content,
            "file_type": document.file_type or "text/plain"
        })
        
        doc_data = result.fetchone()
        
        # Update project's updated_at timestamp
        db.execute(
            text("UPDATE admin.projects SET updated_at = CURRENT_TIMESTAMP WHERE project_id = :project_id"),
            {"project_id": project_id}
        )
        
        db.commit()
        
        return {
            "doc_id": doc_data.doc_id,
            "name": doc_data.name,
            "file_type": doc_data.file_type
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding document to project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add document: {str(e)}"
        )

@router.delete("/projects/{project_id}/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    project_id: UUID4,
    doc_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_admin_db)
):
    """Delete a document from a project"""
    try:
        # Check if project exists and belongs to user
        check_query = text("""
            SELECT p.project_id 
            FROM admin.projects p
            JOIN admin.documents d ON p.project_id = d.project_id
            WHERE p.project_id = :project_id AND p.user_id = :user_id AND d.doc_id = :doc_id
        """)
        
        check_result = db.execute(check_query, {
            "project_id": project_id,
            "user_id": current_user.id,
            "doc_id": doc_id
        })
        
        if not check_result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or doesn't belong to your project"
            )
        
        # Delete the document
        db.execute(
            text("DELETE FROM admin.project_documents WHERE doc_id = :doc_id"),
            {"doc_id": doc_id}
        )
        
        # Update project's updated_at timestamp
        db.execute(
            text("UPDATE admin.projects SET updated_at = CURRENT_TIMESTAMP WHERE project_id = :project_id"),
            {"project_id": project_id}
        )
        
        db.commit()
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting document {doc_id} from project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete document: {str(e)}"
        )

@router.get("/projects/{project_id}/documents/{doc_id}/content")
async def get_document_content(
    project_id: UUID4,
    doc_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_admin_db)
):
    """Get the content of a specific document"""
    try:
        # Check if document exists and belongs to user's project
        query = text("""
            SELECT d.content
            FROM admin.documents d
            JOIN admin.projects p ON d.project_id = p.project_id
            WHERE d.doc_id = :doc_id AND p.project_id = :project_id AND p.user_id = :user_id
        """)
        
        result = db.execute(query, {
            "doc_id": doc_id,
            "project_id": project_id,
            "user_id": current_user.id
        })
        
        document = result.fetchone()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or access denied"
            )
        
        return {"content": document.content}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching document content for {doc_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch document content: {str(e)}"
        )






# Add to project chats
@router.post("/projects/{project_id}/chats/{chat_id}")
async def link_chat_to_project(
    project_id: UUID4,
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_admin_db)
):
    """Link a chat to a project"""
    try:
        # Check if project exists and belongs to user
        check_query = text("""
            SELECT project_id FROM admin.projects 
            WHERE project_id = :project_id AND user_id = :user_id
        """)
        
        check_result = db.execute(check_query, {
            "project_id": project_id,
            "user_id": current_user.id
        })
        
        if not check_result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Link chat to project
        query = text("""
            INSERT INTO admin.project_chats (project_id, chat_id)
            VALUES (:project_id, :chat_id)
            ON CONFLICT (project_id, chat_id) DO NOTHING
        """)
        
        db.execute(query, {
            "project_id": project_id,
            "chat_id": chat_id
        })
        
        # Update project's updated_at timestamp
        db.execute(
            text("UPDATE admin.projects SET updated_at = CURRENT_TIMESTAMP WHERE project_id = :project_id"),
            {"project_id": project_id}
        )
        
        db.commit()
        
        return {"message": "Chat linked to project successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error linking chat {chat_id} to project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to link chat to project: {str(e)}"
        )
    



@router.get("/projects/{project_id}/chats")
async def get_project_chats(
    project_id: UUID4,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_admin_db)
):
    """Get all chats associated with a project"""
    try:
        # Check if project exists and belongs to user
        check_query = text("""
            SELECT project_id FROM admin.projects 
            WHERE project_id = :project_id AND user_id = :user_id
        """)
        
        check_result = db.execute(check_query, {
            "project_id": project_id,
            "user_id": current_user.id
        })
        
        if not check_result.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Get chats linked to the project
        query = text("""
            SELECT pc.chat_id, c.name, c.created_at, c.updated_at
            FROM admin.project_chats pc
            JOIN chat.chats c ON pc.chat_id = c.chat_id
            WHERE pc.project_id = :project_id
            ORDER BY c.updated_at DESC
        """)
        
        result = db.execute(query, {"project_id": project_id})
        chats = result.fetchall()
        
        # Format response
        chat_list = []
        for chat in chats:
            chat_list.append({
                "id": chat.chat_id,
                "title": chat.name or "Untitled Chat",
                "created_at": chat.created_at.isoformat(),
                "updated_at": chat.updated_at.isoformat()
            })
        
        return chat_list
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error fetching chats for project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch project chats: {str(e)}"
        )