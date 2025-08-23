from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class UserBase(BaseModel):
    employee_id: str
    name: str
    company_id: UUID


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    employee_id: Optional[str] = None
    company_id: Optional[UUID] = None