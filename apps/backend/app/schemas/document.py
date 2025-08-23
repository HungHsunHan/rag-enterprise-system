from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class KnowledgeDocumentBase(BaseModel):
    file_name: str
    original_name: str
    version: int
    status: str
    file_size: Optional[int] = None
    content_hash: Optional[str] = None
    tags: Optional[str] = None


class KnowledgeDocument(KnowledgeDocumentBase):
    id: UUID
    company_id: UUID
    parent_document_id: Optional[UUID] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class DocumentUploadRequest(BaseModel):
    tags: Optional[str] = None


class DocumentTagsUpdate(BaseModel):
    tags: str


class DocumentVersion(BaseModel):
    id: UUID
    version: int
    file_name: str
    status: str
    uploaded_at: datetime
    file_size: Optional[int] = None
    tags: Optional[str] = None
    
    class Config:
        from_attributes = True