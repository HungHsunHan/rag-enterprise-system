from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.db.database import get_db
from app.schemas.auth import Token, AdminLogin, UserLogin
from app.services.auth_service import authenticate_admin, authenticate_user

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/admin/login", response_model=Token)
def admin_login(admin_data: AdminLogin, db: Session = Depends(get_db)):
    """
    Admin login endpoint
    """
    admin = authenticate_admin(db, admin_data.email, admin_data.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(admin.id), "type": "admin"}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def user_login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Employee login endpoint
    """
    user = authenticate_user(db, user_data.employee_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid employee ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "company_id": str(user.company_id), "type": "user"}
    )
    return {"access_token": access_token, "token_type": "bearer"}