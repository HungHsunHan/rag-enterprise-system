from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class KnowledgeDocumentBase(BaseModel):
    file_name: str
    status: str


class KnowledgeDocument(KnowledgeDocumentBase):
    id: UUID
    company_id: UUID
    uploaded_at: datetime
    
    class Config:
        from_attributes = True