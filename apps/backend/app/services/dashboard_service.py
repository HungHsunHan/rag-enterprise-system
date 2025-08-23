from typing import Dict, List, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.db.models import Company, User, KnowledgeDocument, FeedbackLog


def get_dashboard_metrics(db: Session) -> Dict[str, Any]:
    """
    Get dashboard metrics with system overview cards
    """
    # Get total companies count
    total_companies = db.query(Company).count()
    
    # Get shared documents count
    shared_documents_count = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.is_shared == True
    ).count()
    
    # Get all companies first
    companies = db.query(Company).all()
    
    # Get today's date for query filtering
    today = datetime.utcnow().date()
    
    # Prepare data for frontend
    company_metrics = []
    
    for company in companies:
        company_id_str = str(company.id)
        
        # Get user count for this company
        user_count = db.query(User).filter(User.company_id == company.id).count()
        
        # Get document count for this company
        document_count = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.company_id == company.id
        ).count()
        
        # Get today's queries for this company (using feedback logs)
        queries_today = db.query(FeedbackLog).join(User).filter(
            User.company_id == company.id,
            func.date(FeedbackLog.created_at) == today
        ).count()
        
        company_metrics.append({
            "company_id": company_id_str,
            "company_name": company.name,
            "user_count": user_count,
            "document_count": document_count,
            "queries_today": queries_today
        })
    
    return {
        "total_companies": total_companies,
        "shared_documents_count": shared_documents_count,
        "company_metrics": company_metrics,
        "timestamp": datetime.utcnow().isoformat()
    }


def get_system_summary(db: Session) -> Dict[str, int]:
    """
    Get high-level system summary metrics
    """
    total_users = db.query(User).count()
    total_documents = db.query(KnowledgeDocument).count()
    
    # Get today's total queries
    today = datetime.utcnow().date()
    total_queries_today = db.query(FeedbackLog).filter(
        func.date(FeedbackLog.created_at) == today
    ).count()
    
    return {
        "total_users": total_users,
        "total_documents": total_documents,
        "total_queries_today": total_queries_today,
        "total_companies": db.query(Company).count()
    }