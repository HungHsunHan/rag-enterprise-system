from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import verify_token
from app.db.database import get_db
from app.db.models import Admin, User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Verify and decode JWT token
    """
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


def get_current_admin(
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user_token)
) -> Admin:
    """
    Get current admin from token
    """
    if token_data.get("type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    admin = db.query(Admin).filter(Admin.id == token_data["sub"]).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found"
        )
    return admin


def get_current_user(
    db: Session = Depends(get_db),
    token_data: dict = Depends(get_current_user_token)
) -> User:
    """
    Get current user from token
    """
    if token_data.get("type") != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    user = db.query(User).filter(User.id == token_data["sub"]).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user