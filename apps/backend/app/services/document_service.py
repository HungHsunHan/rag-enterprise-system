from typing import List, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text, and_, func
import os
import logging
import asyncio
import hashlib
from concurrent.futures import ThreadPoolExecutor

from app.db.models import KnowledgeDocument, DocumentChunk
from app.core.config import settings
from app.services.document_processor import document_processor

logger = logging.getLogger(__name__)

# Thread pool for async processing
executor = ThreadPoolExecutor(max_workers=2)


def calculate_content_hash(content: bytes) -> str:
    """
    Calculate SHA-256 hash of file content
    """
    return hashlib.sha256(content).hexdigest()


def parse_tags(tags_string: Optional[str]) -> List[str]:
    """
    Parse comma-separated tags string into list
    """
    if not tags_string:
        return []
    return [tag.strip() for tag in tags_string.split(',') if tag.strip()]


def format_tags(tags_list: List[str]) -> str:
    """
    Format tags list into comma-separated string
    """
    if not tags_list:
        return ""
    return ", ".join(tags_list)


def get_original_filename(filename: str) -> str:
    """
    Extract original filename without version suffix
    """
    base, ext = os.path.splitext(filename)
    # Remove version suffix if present (e.g., "document_v2.pdf" -> "document.pdf")
    if '_v' in base and base.split('_v')[-1].isdigit():
        base = '_v'.join(base.split('_v')[:-1])
    return base + ext


def find_existing_document_by_name(db: Session, company_id: str, original_name: str) -> Optional[KnowledgeDocument]:
    """
    Find existing document by original name to support versioning
    """
    return db.query(KnowledgeDocument).filter(
        and_(
            KnowledgeDocument.company_id == company_id,
            KnowledgeDocument.original_name == original_name
        )
    ).order_by(KnowledgeDocument.version.desc()).first()


def find_document_by_hash(db: Session, company_id: str, content_hash: str) -> Optional[KnowledgeDocument]:
    """
    Find existing document by content hash to detect duplicates
    """
    return db.query(KnowledgeDocument).filter(
        and_(
            KnowledgeDocument.company_id == company_id,
            KnowledgeDocument.content_hash == content_hash
        )
    ).first()


def get_documents(db: Session, company_id: Optional[str] = None, include_shared: bool = True, skip: int = 0, limit: int = 100) -> List[KnowledgeDocument]:
    """
    Get documents for a company, optionally including shared documents
    """
    query = db.query(KnowledgeDocument)
    
    if company_id:
        if include_shared:
            # Include both company-specific and shared documents
            query = query.filter(
                (KnowledgeDocument.company_id == company_id) |
                (KnowledgeDocument.is_shared == True)
            )
        else:
            # Only company-specific documents
            query = query.filter(KnowledgeDocument.company_id == company_id)
    elif include_shared:
        # Only shared documents
        query = query.filter(KnowledgeDocument.is_shared == True)
    
    return query.order_by(KnowledgeDocument.uploaded_at.desc()).offset(skip).limit(limit).all()


def get_documents_by_company_with_pagination(db: Session, company_id: str, skip: int = 0, limit: int = 100, sort_by_date: bool = True) -> List[KnowledgeDocument]:
    """
    Get documents for a company with pagination and sorting
    """
    query = db.query(KnowledgeDocument).filter(
        (KnowledgeDocument.company_id == company_id) |
        (KnowledgeDocument.is_shared == True)
    )
    
    if sort_by_date:
        query = query.order_by(KnowledgeDocument.uploaded_at.desc())
    else:
        query = query.order_by(KnowledgeDocument.original_name.asc())
    
    return query.offset(skip).limit(limit).all()


def get_shared_documents(db: Session, skip: int = 0, limit: int = 100) -> List[KnowledgeDocument]:
    """
    Get all shared documents
    """
    return db.query(KnowledgeDocument).filter(
        KnowledgeDocument.is_shared == True
    ).order_by(KnowledgeDocument.uploaded_at.desc()).offset(skip).limit(limit).all()


async def upload_document(db: Session, file: UploadFile, company_id: Optional[str], tags: Optional[str] = None, is_shared: bool = False) -> KnowledgeDocument:
    """
    Upload and process a document with versioning and tagging support
    """
    # Validate file type
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail=f"File type {file_ext} not allowed")
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Calculate content hash
    content_hash = calculate_content_hash(file_content)
    
    # Check for exact duplicate
    existing_duplicate = find_document_by_hash(db, company_id, content_hash)
    if existing_duplicate:
        raise HTTPException(
            status_code=400, 
            detail=f"Document with identical content already exists: {existing_duplicate.file_name}"
        )
    
    # Get original filename and check for versioning
    original_name = get_original_filename(file.filename)
    existing_document = find_existing_document_by_name(db, company_id, original_name)
    
    # Determine version and relationships
    version = 1
    parent_document_id = None
    
    if existing_document:
        version = existing_document.version + 1
        parent_document_id = existing_document.parent_document_id or existing_document.id
    
    # Create versioned filename if needed
    versioned_filename = file.filename
    if version > 1:
        base, ext = os.path.splitext(original_name)
        versioned_filename = f"{base}_v{version}{ext}"
    
    # Create document record
    document = KnowledgeDocument(
        file_name=versioned_filename,
        original_name=original_name,
        version=version,
        company_id=company_id,
        parent_document_id=parent_document_id,
        status="PENDING",  # Changed to PENDING - will be PROCESSING after user clicks process
        file_size=len(file_content),
        content_hash=content_hash,
        tags=tags,
        is_shared=is_shared
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    
    logger.info(f"Created document {document.file_name} (version {version}) with hash {content_hash[:8]}")
    
    # Immediately process the document with the real file content
    # This ensures we extract actual text instead of using simulated content
    try:
        # Start background processing with the actual file content
        asyncio.create_task(process_document_async(str(document.id), file_content, file.filename))
        logger.info(f"Started background processing for document {document.id}")
    except Exception as e:
        logger.error(f"Failed to start processing for document {document.id}: {e}")
        # Don't fail the upload if background processing fails to start
    
    return document


def get_document_by_id(db: Session, document_id: str) -> Optional[KnowledgeDocument]:
    """
    Get document by ID
    """
    return db.query(KnowledgeDocument).filter(KnowledgeDocument.id == document_id).first()


async def process_document_chunks(db: Session, document_id: str, chunk_size: int, overlap_length: int) -> dict:
    """
    Process a document with specified chunk parameters
    """
    document = get_document_by_id(db, document_id)
    if not document:
        raise ValueError("Document not found")
    
    if document.status not in ["PENDING", "FAILED"]:
        raise ValueError(f"Document cannot be processed. Current status: {document.status}")
    
    # Update document with processing parameters
    document.chunk_size = chunk_size
    document.overlap_length = overlap_length
    document.status = "PROCESSING"
    db.commit()
    
    # For now, we'll simulate processing since we don't have file storage yet
    # In a real implementation, you'd retrieve the file content from storage
    logger.info(f"Processing document {document_id} with chunk_size={chunk_size}, overlap={overlap_length}")
    
    # Create a background task to process the document
    asyncio.create_task(process_document_with_params(document_id, chunk_size, overlap_length))
    
    return {
        "status": "PROCESSING",
        "chunks_created": 0  # Will be updated when processing completes
    }


async def process_document_with_params(document_id: str, chunk_size: int, overlap_length: int):
    """
    Process document with specified parameters
    """
    from app.db.database import SessionLocal
    
    db = SessionLocal()
    try:
        document = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == document_id
        ).first()
        
        if not document:
            logger.error(f"Document {document_id} not found")
            return
        
        # TEMPORARY FIX: For now, we'll notify that reprocessing isn't supported
        # In a real implementation, you'd retrieve the file content from storage
        try:
            logger.error(f"Manual reprocessing not supported - original file content not stored")
            raise ValueError("Manual reprocessing is not supported in the current implementation. Please re-upload the file.")
            
            # Create chunks based on parameters
            chunks = []
            text_length = len(dummy_text)
            start = 0
            chunk_index = 0
            
            while start < text_length:
                end = min(start + chunk_size, text_length)
                chunk_text = dummy_text[start:end]
                
                if chunk_text.strip():  # Only add non-empty chunks
                    chunk = DocumentChunk(
                        document_id=document.id,
                        company_id=document.company_id,
                        chunk_text=chunk_text,
                        chunk_index=chunk_index,
                        is_shared=document.is_shared
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Move start position considering overlap
                start = max(start + chunk_size - overlap_length, start + 1)
                if start >= text_length:
                    break
            
            # Add chunks to database
            db.add_all(chunks)
            
            # Update document status
            document.status = "COMPLETED"
            db.commit()
            
            logger.info(f"Completed processing document {document_id}, created {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"Failed to process document {document_id}: {e}")
            document.status = "FAILED"
            db.commit()
            
    finally:
        db.close()


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


def delete_documents_bulk(db: Session, document_ids: List[str], company_id: str) -> dict:
    """
    Delete multiple documents and all their chunks
    """
    success_count = 0
    failed_ids = []
    
    try:
        # Verify all documents belong to the company for security
        documents = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.id.in_(document_ids),
            KnowledgeDocument.company_id == company_id
        ).all()
        
        valid_document_ids = [str(doc.id) for doc in documents]
        
        # Delete associated chunks first
        chunks_deleted = db.query(DocumentChunk).filter(
            DocumentChunk.document_id.in_(valid_document_ids)
        ).delete(synchronize_session=False)
        
        logger.info(f"Deleted {chunks_deleted} chunks for bulk document deletion")
        
        # Delete documents
        for document in documents:
            try:
                db.delete(document)
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to delete document {document.id}: {e}")
                failed_ids.append(str(document.id))
        
        db.commit()
        
        # Track invalid document IDs (not found or wrong company)
        invalid_ids = [doc_id for doc_id in document_ids if doc_id not in valid_document_ids]
        failed_ids.extend(invalid_ids)
        
        logger.info(f"Bulk delete completed: {success_count} successful, {len(failed_ids)} failed")
        
        return {
            'success_count': success_count,
            'failed_count': len(failed_ids),
            'failed_ids': failed_ids,
            'chunks_deleted': chunks_deleted
        }
        
    except Exception as e:
        logger.error(f"Failed bulk document deletion: {e}")
        db.rollback()
        return {
            'success_count': 0,
            'failed_count': len(document_ids),
            'failed_ids': document_ids,
            'chunks_deleted': 0
        }


def get_document_versions(db: Session, company_id: str, original_name: str) -> List[KnowledgeDocument]:
    """
    Get all versions of a document by original name
    """
    return db.query(KnowledgeDocument).filter(
        and_(
            KnowledgeDocument.company_id == company_id,
            KnowledgeDocument.original_name == original_name
        )
    ).order_by(KnowledgeDocument.version.desc()).all()


def get_documents_with_tags(db: Session, company_id: str, tags: List[str]) -> List[KnowledgeDocument]:
    """
    Get documents filtered by tags
    """
    if not tags:
        return get_documents(db, company_id)
    
    # Build a query that matches any of the provided tags
    tag_conditions = []
    for tag in tags:
        tag_conditions.append(KnowledgeDocument.tags.contains(tag))
    
    from sqlalchemy import or_
    return db.query(KnowledgeDocument).filter(
        and_(
            KnowledgeDocument.company_id == company_id,
            or_(*tag_conditions) if tag_conditions else True
        )
    ).order_by(KnowledgeDocument.uploaded_at.desc()).all()


def update_document_tags(db: Session, document_id: str, tags: str) -> bool:
    """
    Update tags for a document
    """
    try:
        document = db.query(KnowledgeDocument).filter(
            KnowledgeDocument.id == document_id
        ).first()
        
        if not document:
            return False
        
        document.tags = tags
        db.commit()
        
        logger.info(f"Updated tags for document {document_id}: {tags}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update tags for document {document_id}: {e}")
        db.rollback()
        return False


def get_all_tags(db: Session, company_id: str) -> List[str]:
    """
    Get all unique tags used in company documents
    """
    try:
        documents = db.query(KnowledgeDocument).filter(
            and_(
                KnowledgeDocument.company_id == company_id,
                KnowledgeDocument.tags.isnot(None),
                KnowledgeDocument.tags != ''
            )
        ).all()
        
        all_tags = set()
        for doc in documents:
            if doc.tags:
                tags = parse_tags(doc.tags)
                all_tags.update(tags)
        
        return sorted(list(all_tags))
        
    except Exception as e:
        logger.error(f"Failed to get tags for company {company_id}: {e}")
        return []


def search_similar_chunks(db: Session, query_embedding: List[float], company_id: str, limit: int = 5) -> List[DocumentChunk]:
    """
    Search for similar document chunks using vector similarity
    """
    try:
        # Use raw SQL for vector similarity search
        sql = text("""
            SELECT id, document_id, company_id, chunk_text, chunk_index, created_at,
                   embedding <-> CAST(:query_embedding AS vector) AS distance
            FROM document_chunks 
            WHERE company_id = :company_id
            AND embedding IS NOT NULL
            ORDER BY embedding <-> CAST(:query_embedding AS vector)
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