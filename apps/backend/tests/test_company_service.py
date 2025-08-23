import pytest
from app.services.company_service import create_company, get_companies, delete_company
from app.schemas.company import CompanyCreate
from app.services.user_service import create_user
from app.schemas.user import UserCreate


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


def test_delete_company_success(db_session):
    """
    Test successful company deletion
    """
    company_data = CompanyCreate(name="Test Delete Company")
    company = create_company(db_session, company_data)
    
    # Delete the company
    success = delete_company(db_session, str(company.id))
    assert success is True
    
    # Verify company is deleted
    companies = get_companies(db_session)
    company_ids = [str(c.id) for c in companies]
    assert str(company.id) not in company_ids


def test_delete_company_not_found(db_session):
    """
    Test deleting non-existent company
    """
    # Use a valid UUID format that doesn't exist
    success = delete_company(db_session, "550e8400-e29b-41d4-a716-446655440000")
    assert success is False


def test_delete_company_with_users_fails(db_session):
    """
    Test that deleting company with users raises error
    """
    company_data = CompanyCreate(name="Company with Users")
    company = create_company(db_session, company_data)
    
    # Create a user for this company
    user_data = UserCreate(
        employee_id="EMP001",
        name="Test User",
        company_id=str(company.id)
    )
    create_user(db_session, user_data)
    
    # Try to delete company with users
    with pytest.raises(ValueError, match="Cannot delete company with .* users"):
        delete_company(db_session, str(company.id))