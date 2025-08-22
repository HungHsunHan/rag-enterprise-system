import pytest
from app.services.company_service import create_company, get_companies
from app.schemas.company import CompanyCreate


def test_create_company(db_session):
    """
    Test company creation
    """
    company_data = CompanyCreate(name="Test Company")
    company = create_company(db_session, company_data)
    
    assert company.name == "Test Company"
    assert company.id is not None
    assert company.created_at is not None


def test_get_companies(db_session):
    """
    Test getting all companies
    """
    # Create test companies
    company1_data = CompanyCreate(name="Company 1")
    company2_data = CompanyCreate(name="Company 2")
    
    create_company(db_session, company1_data)
    create_company(db_session, company2_data)
    
    companies = get_companies(db_session)
    assert len(companies) == 2
    
    company_names = [company.name for company in companies]
    assert "Company 1" in company_names
    assert "Company 2" in company_names