from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class CompanyBase(BaseModel):
    name: str


class CompanyCreate(CompanyBase):
    pass


class Company(CompanyBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True