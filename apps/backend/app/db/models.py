from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, UniqueConstraint, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pgvector.sqlalchemy import Vector
import uuid

Base = declarative_base()


class Company(Base):
    """
    Company model - represents tenants in the multi-tenant system
    """
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    knowledge_documents = relationship("KnowledgeDocument", back_populates="company", cascade="all, delete-orphan")
    document_chunks = relationship("DocumentChunk", back_populates="company", cascade="all, delete-orphan")


class Admin(Base):
    """
    Admin model - system administrators with global access
    """
    __tablename__ = "admins"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class User(Base):
    """
    User model - employees who can ask questions
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(String(100), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Ensure employee_id is unique within each company
    __table_args__ = (UniqueConstraint('company_id', 'employee_id', name='uq_company_employee'),)
    
    # Relationships
    company = relationship("Company", back_populates="users")
    feedback_logs = relationship("FeedbackLog", back_populates="user")


class KnowledgeDocument(Base):
    """
    Knowledge document model - uploaded files that contain company knowledge
    """
    __tablename__ = "knowledge_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_name = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False, default="PROCESSING")  # PROCESSING, COMPLETED, FAILED
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    uploaded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="knowledge_documents")
    document_chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """
    Document chunk model - text segments with their embeddings for RAG
    """
    __tablename__ = "document_chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_documents.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False, default=0)  # Order within document
    embedding = Column(Vector(384), nullable=True)  # 384-dimensional vector for all-MiniLM-L6-v2
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    document = relationship("KnowledgeDocument", back_populates="document_chunks")
    company = relationship("Company", back_populates="document_chunks")


class FeedbackLog(Base):
    """
    Feedback log model - stores user feedback on Q&A pairs
    """
    __tablename__ = "feedback_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # SET NULL on delete
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    feedback = Column(String(20), nullable=False)  # POSITIVE or NEGATIVE
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="feedback_logs")