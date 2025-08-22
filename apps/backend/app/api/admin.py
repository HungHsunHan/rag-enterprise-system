from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.core.deps import get_current_admin
from app.db.database import get_db
from app.db.models import Admin
from app.schemas.company import Company, CompanyCreate
from app.schemas.document import KnowledgeDocument
from app.schemas.chat import FeedbackResponse, FeedbackStats
from app.services.company_service import create_company, get_companies
from app.services.document_service import upload_document, get_documents, delete_document
from app.services.feedback_service import get_feedback_list, get_feedback_stats, search_feedback

router = APIRouter()


@router.get("/companies", response_model=List[Company])
def get_company_list(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get all companies (admin only)
    """
    companies = get_companies(db)
    return companies


@router.post("/companies", response_model=Company)
def create_new_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Create a new company (admin only)
    """
    company = create_company(db, company_data)
    return company


@router.get("/knowledge/documents", response_model=List[KnowledgeDocument])
def get_knowledge_documents(
    company_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get all documents for a specific company
    """
    documents = get_documents(db, company_id)
    return documents


@router.post("/knowledge/documents")
async def upload_knowledge_document(
    company_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Upload a new knowledge document
    """
    result = await upload_document(db, file, company_id)
    return {"message": "Document uploaded successfully", "document_id": result.id}


@router.delete("/knowledge/documents/{document_id}")
def delete_knowledge_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Delete a knowledge document and its embeddings
    """
    success = delete_document(db, document_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    return {"message": "Document deleted successfully"}


@router.get("/feedback", response_model=List[FeedbackResponse])
def get_company_feedback(
    company_id: str,
    feedback_type: str = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get feedback list for a specific company with optional filtering
    """
    feedback_list = get_feedback_list(db, company_id, feedback_type, limit, offset)
    return feedback_list


@router.get("/feedback/stats", response_model=FeedbackStats)
def get_company_feedback_stats(
    company_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get feedback statistics for a specific company
    """
    stats = get_feedback_stats(db, company_id)
    return FeedbackStats(**stats)


@router.get("/feedback/search", response_model=List[FeedbackResponse])
def search_company_feedback(
    company_id: str,
    search_term: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Search feedback by question or answer content
    """
    feedback_list = search_feedback(db, company_id, search_term, limit, offset)
    return feedback_list


@router.get("/knowledge/chunks")
def get_knowledge_chunks(
    company_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get knowledge chunks for a specific company
    """
    from app.services.document_service import get_document_chunks
    
    chunks = get_document_chunks(db, company_id, limit, offset)
    return {
        "chunks": [
            {
                "id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "chunk_text": chunk.chunk_text,
                "chunk_index": chunk.chunk_index,
                "created_at": chunk.created_at.isoformat()
            }
            for chunk in chunks
        ]
    }