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
from app.services.document_service import (
    upload_document, get_documents, delete_document, delete_documents_bulk,
    get_document_versions, get_documents_with_tags, update_document_tags, get_all_tags
)
from app.services.feedback_service import get_feedback_list, get_feedback_stats, search_feedback
from app.services.monitoring_service import get_system_health, get_usage_statistics
from app.services.error_logging_service import get_error_logs, get_error_statistics
from app.services.test_coverage_service import generate_coverage_report, get_coverage_summary, run_tests_with_coverage

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
    tags: str = "",
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Upload a new knowledge document with optional tags
    """
    result = await upload_document(db, file, company_id, tags if tags.strip() else None)
    return {
        "message": "Document uploaded successfully",
        "document_id": result.id,
        "version": result.version,
        "original_name": result.original_name
    }


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


@router.post("/knowledge/documents/bulk-delete")
def bulk_delete_documents(
    request: dict,  # {"company_id": str, "document_ids": List[str]}
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Delete multiple documents and their embeddings
    """
    company_id = request.get("company_id")
    document_ids = request.get("document_ids", [])
    
    if not company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company ID is required"
        )
    
    if not document_ids or not isinstance(document_ids, list):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document IDs list is required"
        )
    
    if len(document_ids) > 50:  # Safety limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete more than 50 documents at once"
        )
    
    result = delete_documents_bulk(db, document_ids, company_id)
    
    return {
        "message": f"Bulk delete completed: {result['success_count']} successful, {result['failed_count']} failed",
        "details": result
    }


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


@router.get("/knowledge/documents/versions")
def get_document_version_history(
    company_id: str,
    original_name: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get version history for a document by original name
    """
    versions = get_document_versions(db, company_id, original_name)
    return {
        "original_name": original_name,
        "versions": [
            {
                "id": str(version.id),
                "version": version.version,
                "file_name": version.file_name,
                "status": version.status,
                "uploaded_at": version.uploaded_at.isoformat(),
                "file_size": version.file_size,
                "tags": version.tags
            }
            for version in versions
        ]
    }


@router.get("/knowledge/documents/tags")
def get_available_tags(
    company_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get all available tags for a company
    """
    tags = get_all_tags(db, company_id)
    return {"tags": tags}


@router.get("/knowledge/documents/by-tags")
def get_documents_by_tags(
    company_id: str,
    tags: str = "",  # Comma-separated list of tags
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get documents filtered by tags
    """
    from app.services.document_service import parse_tags
    tag_list = parse_tags(tags) if tags else []
    documents = get_documents_with_tags(db, company_id, tag_list)
    return documents


@router.put("/knowledge/documents/{document_id}/tags")
def update_document_tags_endpoint(
    document_id: str,
    request: dict,  # {"tags": "tag1, tag2, tag3"}
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Update tags for a document
    """
    tags = request.get("tags", "")
    success = update_document_tags(db, document_id, tags)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found or update failed"
        )
    
    return {"message": "Document tags updated successfully"}


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


@router.get("/system/health")
async def get_system_health_status(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get comprehensive system health status
    """
    health_status = await get_system_health(db)
    return health_status


@router.get("/system/statistics")
async def get_system_statistics(
    company_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get detailed usage statistics for the system or a specific company
    """
    stats = await get_usage_statistics(db, company_id)
    return stats


@router.get("/system/performance")
async def get_performance_metrics(
    company_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get system performance metrics and indicators
    """
    from app.services.monitoring_service import system_monitor
    
    # Get comprehensive health data which includes performance metrics
    health_data = await system_monitor.get_system_health(db)
    
    # Extract performance-related information
    performance_metrics = {
        "timestamp": health_data["timestamp"],
        "uptime_seconds": health_data["uptime_seconds"],
        "status": health_data["status"],
        "database_performance": {
            "response_time_ms": health_data["components"]["database"].get("response_time_ms"),
            "status": health_data["components"]["database"]["status"]
        },
        "system_resources": health_data["components"]["system"],
        "application_metrics": health_data["components"]["application"]
    }
    
    return performance_metrics


@router.get("/system/errors")
async def get_system_errors(
    company_id: Optional[str] = None,
    level: Optional[str] = None,
    days: int = 7,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get system error logs with filtering options
    """
    logs = get_error_logs(db, company_id, level, days, limit, offset)
    return {
        "error_logs": logs,
        "total_count": len(logs),
        "filters": {
            "company_id": company_id,
            "level": level,
            "days": days,
            "limit": limit,
            "offset": offset
        }
    }


@router.get("/system/errors/statistics")
async def get_error_statistics_endpoint(
    company_id: Optional[str] = None,
    days: int = 7,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get error statistics for the specified period
    """
    stats = get_error_statistics(db, company_id, days)
    return stats


@router.get("/system/test-coverage")
async def get_test_coverage_summary(
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Get current test coverage summary
    """
    summary = get_coverage_summary()
    return summary


@router.post("/system/test-coverage/generate")
async def generate_test_coverage_report(
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Generate a new test coverage report by running tests
    """
    report = generate_coverage_report()
    return report


@router.post("/system/tests/run")
async def run_tests_endpoint(
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Run tests with coverage collection
    """
    results = run_tests_with_coverage()
    return results