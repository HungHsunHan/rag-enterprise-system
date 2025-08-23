from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import User, Company
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user
    """
    # Verify company exists
    company = db.query(Company).filter(Company.id == user_data.company_id).first()
    if not company:
        raise ValueError("Company not found")
    
    try:
        db_user = User(
            employee_id=user_data.employee_id,
            name=user_data.name,
            company_id=user_data.company_id
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("Employee ID already exists in this company")


def get_users(db: Session, company_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Get users with optional company filtering
    """
    query = db.query(User)
    if company_id:
        query = query.filter(User.company_id == company_id)
    
    return query.offset(skip).limit(limit).all()


def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
    """
    Get user by ID
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_employee_id(db: Session, employee_id: str, company_id: str) -> Optional[User]:
    """
    Get user by employee ID within a company
    """
    return db.query(User).filter(
        User.employee_id == employee_id,
        User.company_id == company_id
    ).first()


def update_user(db: Session, user_id: str, user_data: UserUpdate) -> Optional[User]:
    """
    Update user information
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None
    
    try:
        for key, value in user_data.dict(exclude_unset=True).items():
            if value is not None:
                setattr(db_user, key, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise ValueError("Employee ID already exists in this company")


def delete_user(db: Session, user_id: str) -> bool:
    """
    Delete user by ID
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


def get_users_by_company(db: Session, company_id: str) -> List[User]:
    """
    Get all users in a specific company
    """
    return db.query(User).filter(User.company_id == company_id).all()