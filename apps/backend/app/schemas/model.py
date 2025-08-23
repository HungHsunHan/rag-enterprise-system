from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class LLMModelBase(BaseModel):
    model_name: str
    display_name: str
    is_active: bool = True
    is_default: bool = False


class LLMModelCreate(LLMModelBase):
    pass


class LLMModel(LLMModelBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class LLMModelUpdate(BaseModel):
    display_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None