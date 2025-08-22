from typing import Optional
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.db.models import Admin, User


def authenticate_admin(db: Session, email: str, password: str) -> Optional[Admin]:
    """
    Authenticate admin user
    """
    admin = db.query(Admin).filter(Admin.email == email).first()
    if not admin or not verify_password(password, admin.password_hash):
        return None
    return admin


def authenticate_user(db: Session, employee_id: str) -> Optional[User]:
    """
    Authenticate employee user by employee ID
    """
    user = db.query(User).filter(User.employee_id == employee_id).first()
    return user