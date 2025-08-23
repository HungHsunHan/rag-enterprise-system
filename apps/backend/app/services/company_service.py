from typing import List
from sqlalchemy.orm import Session

from app.db.models import Company
from app.schemas.company import CompanyCreate


def get_companies(db: Session) -> List[Company]:
    """
    Get all companies
    """
    return db.query(Company).all()


def create_company(db: Session, company_data: CompanyCreate) -> Company:
    """
    Create a new company
    """
    company = Company(name=company_data.name)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def get_company_by_id(db: Session, company_id: str) -> Company:
    """
    Get company by ID
    """
    return db.query(Company).filter(Company.id == company_id).first()


def delete_company(db: Session, company_id: str) -> bool:
    """
    Delete a company by ID
    Returns True if successful, False if company not found
    """
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return False
    
    # Check if company has users before deleting
    from app.db.models import User
    users_count = db.query(User).filter(User.company_id == company_id).count()
    if users_count > 0:
        raise ValueError(f"Cannot delete company with {users_count} users. Please delete or transfer users first.")
    
    # Check if company has documents before deleting
    from app.db.models import KnowledgeDocument
    documents_count = db.query(KnowledgeDocument).filter(KnowledgeDocument.company_id == company_id).count()
    if documents_count > 0:
        raise ValueError(f"Cannot delete company with {documents_count} documents. Please delete documents first.")
    
    db.delete(company)
    db.commit()
    return True