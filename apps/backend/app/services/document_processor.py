import os
import logging
from typing import List, Optional, BinaryIO
from pathlib import Path
import tempfile

# Document processing imports
import pypdf
from docx import Document as DocxDocument
from sentence_transformers import SentenceTransformer
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Document processor for extracting text from various file formats
    and creating embeddings for RAG pipeline
    """
    
    def __init__(self):
        self.embedding_model = None
        self._load_embedding_model()
    
    def _load_embedding_model(self):
        """
        Load the sentence transformer model for creating embeddings
        """
        try:
            self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
    
    def extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """
        Extract text from uploaded file based on file extension
        """
        file_extension = Path(filename).suffix.lower()
        
        try:
            if file_extension == '.pdf':
                return self._extract_from_pdf(file_content)
            elif file_extension == '.docx':
                return self._extract_from_docx(file_content)
            elif file_extension == '.txt':
                return self._extract_from_txt(file_content)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
        except Exception as e:
            logger.error(f"Error extracting text from {filename}: {e}")
            raise
    
    def _extract_from_pdf(self, file_content: bytes) -> str:
        """
        Extract text from PDF file
        """
        text = ""
        try:
            # Create a temporary file to work with pypdf
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file.flush()
                
                reader = pypdf.PdfReader(temp_file.name)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise ValueError(f"Failed to process PDF file: {e}")
        
        return text.strip()
    
    def _extract_from_docx(self, file_content: bytes) -> str:
        """
        Extract text from DOCX file
        """
        text = ""
        try:
            # Create a temporary file to work with python-docx
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                temp_file.write(file_content)
                temp_file.flush()
                
                doc = DocxDocument(temp_file.name)
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
        except Exception as e:
            logger.error(f"Error processing DOCX: {e}")
            raise ValueError(f"Failed to process DOCX file: {e}")
        
        return text.strip()
    
    def _extract_from_txt(self, file_content: bytes) -> str:
        """
        Extract text from TXT file
        """
        try:
            # Try UTF-8 first, then fallback to other encodings
            try:
                return file_content.decode('utf-8').strip()
            except UnicodeDecodeError:
                try:
                    return file_content.decode('latin-1').strip()
                except UnicodeDecodeError:
                    return file_content.decode('utf-8', errors='ignore').strip()
        except Exception as e:
            logger.error(f"Error processing TXT: {e}")
            raise ValueError(f"Failed to process TXT file: {e}")
    
    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks for processing
        """
        if not text.strip():
            return []
        
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed chunk size, save current chunk
            if len(current_chunk) + len(paragraph) > settings.CHUNK_SIZE:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        # If we have chunks larger than max size, split them further
        final_chunks = []
        for chunk in chunks:
            if len(chunk) <= settings.CHUNK_SIZE:
                final_chunks.append(chunk)
            else:
                # Split by sentences
                sentences = chunk.split('. ')
                current_subchunk = ""
                
                for sentence in sentences:
                    if len(current_subchunk) + len(sentence) > settings.CHUNK_SIZE:
                        if current_subchunk:
                            final_chunks.append(current_subchunk.strip())
                        current_subchunk = sentence
                    else:
                        if current_subchunk:
                            current_subchunk += ". " + sentence
                        else:
                            current_subchunk = sentence
                
                if current_subchunk:
                    final_chunks.append(current_subchunk.strip())
        
        return [chunk for chunk in final_chunks if chunk.strip()]
    
    def create_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Create embeddings for a list of texts
        """
        if not self.embedding_model:
            raise ValueError("Embedding model not loaded")
        
        if not texts:
            return []
        
        try:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
            return [embedding for embedding in embeddings]
        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            raise ValueError(f"Failed to create embeddings: {e}")
    
    def create_single_embedding(self, text: str) -> np.ndarray:
        """
        Create embedding for a single text
        """
        if not self.embedding_model:
            raise ValueError("Embedding model not loaded")
        
        try:
            embedding = self.embedding_model.encode([text], convert_to_numpy=True)
            return embedding[0]
        except Exception as e:
            logger.error(f"Error creating single embedding: {e}")
            raise ValueError(f"Failed to create embedding: {e}")

# Global instance
document_processor = DocumentProcessor()