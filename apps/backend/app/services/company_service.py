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