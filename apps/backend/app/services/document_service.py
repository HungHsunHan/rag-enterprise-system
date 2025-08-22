from typing import List
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.db.models import KnowledgeDocument, DocumentChunk
from app.core.config import settings
from app.services.document_processor import document_processor

logger = logging.getLogger(__name__)

# Thread pool for async processing
executor = ThreadPoolExecutor(max_workers=2)


def get_documents(db: Session, company_id: str) -> List[KnowledgeDocument]:
    """
    Get all documents for a company
    """
    return db.query(KnowledgeDocument).filter(
        KnowledgeDocument.company_id == company_id
    ).order_by(KnowledgeDocument.uploaded_at.desc()).all()


async def upload_document(db: Session, file: UploadFile, company_id: str) -> KnowledgeDocument:
    """
    Upload and process a document
    """
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail=f"File type {file_ext} not allowed")
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Create document record
    document = KnowledgeDocument(
        file_name=file.filename,
        company_id=company_id,
        status="PROCESSING"
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Process document asynchronously
    asyncio.create_task(process_document_async(str(document.id), file_content, file.filename))
    
    return document


async def process_document_async(document_id: str, file_content: bytes, filename: str):
    """
    Process document asynchronously in background
    """
    from app.db.database import SessionLocal
    
    db = SessionLocal()
    try:
        # Get document
        document = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == document_id
        ).first()
        
        if not document:
            logger.error(f"Document {document_id} not found")
            return
        
        # Extract text from file
        try:
            text = document_processor.extract_text_from_file(file_content, filename)
            logger.info(f"Extracted {len(text)} characters from {filename}")
        except Exception as e:
            logger.error(f"Failed to extract text from {filename}: {e}")
            document.status = "FAILED"
            db.commit()
            return
        
        # Chunk the text
        chunks = document_processor.chunk_text(text)
        if not chunks:
            logger.warning(f"No text chunks extracted from {filename}")
            document.status = "COMPLETED"
            db.commit()
            return
        
        logger.info(f"Created {len(chunks)} chunks from {filename}")
        
        # Create embeddings
        try:
            embeddings = document_processor.create_embeddings(chunks)
        except Exception as e:
            logger.error(f"Failed to create embeddings for {filename}: {e}")
            document.status = "FAILED"
            db.commit()
            return
        
        # Store chunks with embeddings
        try:
            for i, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                chunk = DocumentChunk(
                    document_id=document.id,
                    company_id=document.company_id,
                    chunk_text=chunk_text,
                    chunk_index=i,
                    embedding=embedding.tolist()  # Convert numpy array to list
                )
                db.add(chunk)
            
            document.status = "COMPLETED"
            db.commit()
            logger.info(f"Successfully processed {filename} with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to store chunks for {filename}: {e}")
            document.status = "FAILED"
            db.commit()
            
    except Exception as e:
        logger.error(f"Unexpected error processing {filename}: {e}")
        if document:
            document.status = "FAILED"
            db.commit()
    finally:
        db.close()


def delete_document(db: Session, document_id: str) -> bool:
    """
    Delete a document and all its chunks
    """
    try:
        document = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == document_id
        ).first()
        
        if not document:
            return False
        
        # Delete associated chunks first (explicit delete for cleanup)
        chunks_deleted = db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document_id
        ).delete(synchronize_session=False)
        
        logger.info(f"Deleted {chunks_deleted} chunks for document {document_id}")
        
        # Delete document
        db.delete(document)
        db.commit()
        
        logger.info(f"Successfully deleted document {document_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        db.rollback()
        return False


def get_document_chunks(db: Session, company_id: str, limit: int = 100, offset: int = 0) -> List[DocumentChunk]:
    """
    Get document chunks for a company with pagination
    """
    return db.query(DocumentChunk).filter(
        DocumentChunk.company_id == company_id
    ).offset(offset).limit(limit).all()


def search_similar_chunks(db: Session, query_embedding: List[float], company_id: str, limit: int = 5) -> List[DocumentChunk]:
    """
    Search for similar document chunks using vector similarity
    """
    try:
        # Use raw SQL for vector similarity search
        sql = text("""
            SELECT id, document_id, company_id, chunk_text, chunk_index, created_at,
                   embedding <-> :query_embedding AS distance
            FROM document_chunks 
            WHERE company_id = :company_id
            AND embedding IS NOT NULL
            ORDER BY embedding <-> :query_embedding
            LIMIT :limit
        """)
        
        result = db.execute(sql, {
            'query_embedding': query_embedding,
            'company_id': company_id,
            'limit': limit
        })
        
        chunks = []
        for row in result:
            chunk = DocumentChunk()
            chunk.id = row.id
            chunk.document_id = row.document_id
            chunk.company_id = row.company_id
            chunk.chunk_text = row.chunk_text
            chunk.chunk_index = row.chunk_index
            chunk.created_at = row.created_at
            chunks.append(chunk)
            
        return chunks
        
    except Exception as e:
        logger.error(f"Error searching similar chunks: {e}")
        return []