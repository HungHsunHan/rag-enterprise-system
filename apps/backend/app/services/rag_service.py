from typing import List, Optional
from sqlalchemy.orm import Session
import logging
import httpx

from app.db.models import DocumentChunk
from app.core.config import settings
from app.services.document_processor import document_processor
from app.services.document_service import search_similar_chunks

logger = logging.getLogger(__name__)

class RAGService:
    """
    RAG (Retrieval-Augmented Generation) service for question answering
    """
    
    def __init__(self):
        self.openrouter_base_url = "https://openrouter.ai/api/v1"
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.LLM_MODEL
        self._validate_config()
    
    def _validate_config(self):
        """
        Validate OpenRouter configuration
        """
        if not self.api_key:
            logger.warning("OpenRouter API key not provided, using mock responses")
        else:
            logger.info(f"Initialized OpenRouter client with model: {self.model}")
    
    def generate_answer(self, db: Session, question: str, company_id: str, model_name: Optional[str] = None) -> str:
        """
        Generate answer using RAG pipeline with company-scoped search
        """
        try:
            # Step 1: Convert question to embedding
            query_embedding = self._vectorize_question(question)
            if query_embedding is None:
                return self._fallback_response(question)
            
            # Step 2: Perform company-scoped vector similarity search (includes shared documents)
            relevant_chunks = self._search_company_scoped_chunks(
                db, 
                query_embedding.tolist(), 
                company_id, 
                limit=5
            )
            
            if not relevant_chunks:
                return "I don't have enough information to answer your question. Please make sure relevant documents have been uploaded to the knowledge base."
            
            # Step 3: Construct context from relevant chunks
            context = self._build_context(relevant_chunks)
            
            # Step 4: Generate answer using LLM (use specified model or default)
            actual_model = model_name or self.model
            answer = self._generate_llm_response(question, context, actual_model)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return "I'm sorry, I encountered an error while processing your question. Please try again or contact your HR team for assistance."
    
    def _search_company_scoped_chunks(self, db: Session, query_embedding: List[float], company_id: str, limit: int = 5) -> List[DocumentChunk]:
        """
        Search for relevant chunks scoped to company (including shared documents)
        """
        try:
            # Query chunks that belong to the company OR are shared
            from sqlalchemy import text
            
            # Use raw SQL for vector similarity search with company scoping
            sql = text("""
                SELECT * FROM document_chunks 
                WHERE (company_id = :company_id OR is_shared = true)
                AND embedding IS NOT NULL
                ORDER BY embedding <-> :embedding
                LIMIT :limit
            """)
            
            result = db.execute(sql, {
                'company_id': company_id,
                'embedding': str(query_embedding),
                'limit': limit
            })
            
            chunk_ids = [row[0] for row in result.fetchall()]
            
            if chunk_ids:
                return db.query(DocumentChunk).filter(DocumentChunk.id.in_(chunk_ids)).all()
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error in company-scoped chunk search: {e}")
            # Fallback to simple company filter without vector search
            return db.query(DocumentChunk).filter(
                (DocumentChunk.company_id == company_id) | (DocumentChunk.is_shared == True)
            ).limit(limit).all()
    
    def _vectorize_question(self, question: str) -> Optional[any]:
        """
        Convert question to embedding vector
        """
        try:
            return document_processor.create_single_embedding(question)
        except Exception as e:
            logger.error(f"Failed to vectorize question: {e}")
            return None
    
    def _build_context(self, chunks: List[DocumentChunk]) -> str:
        """
        Build context string from relevant chunks
        """
        context_parts = []
        for i, chunk in enumerate(chunks[:5]):  # Use top 5 chunks
            context_parts.append(f"Context {i+1}:\n{chunk.chunk_text}")
        
        return "\n\n".join(context_parts)
    
    def _generate_llm_response(self, question: str, context: str, model_name: str = None) -> str:
        """
        Generate response using OpenRouter LLM
        """
        if not self.api_key:
            return self._mock_llm_response(question, context)
        
        try:
            # Construct prompt
            prompt = self._build_prompt(question, context)
            
            # Call OpenRouter API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/anthropics/claude-code",  # Optional, for analytics
                "X-Title": "HR Q&A System"  # Optional, for analytics
            }
            
            payload = {
                "model": model_name or self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful HR assistant. Answer questions based on the provided context from company documents. Be professional, accurate, and concise."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.7
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.openrouter_base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return self._mock_llm_response(question, context)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """
        Build prompt for LLM
        """
        return f"""Based on the following company information, please answer the user's question.

Company Information:
{context}

User Question: {question}

Please provide a helpful and accurate answer based on the company information provided. If the information is not sufficient to answer the question completely, please indicate what additional information might be needed and suggest contacting HR for more details."""
    
    def _mock_llm_response(self, question: str, context: str) -> str:
        """
        Generate mock response when LLM is not available
        """
        context_summary = context[:300] + "..." if len(context) > 300 else context
        
        return f"""Based on the available company information, here's what I found relevant to your question about "{question}":

{context_summary}

Please note: This response is generated from your company's knowledge base. For more detailed information or if you need clarification, please contact your HR team directly."""
    
    def _fallback_response(self, question: str) -> str:
        """
        Fallback response when RAG pipeline fails
        """
        return f"""I'm having trouble processing your question about "{question}" right now. This could be due to:

1. The knowledge base is still being updated
2. No relevant documents have been uploaded yet
3. Technical issues with the system

Please try again later or contact your HR team directly for immediate assistance."""

# Global instance
rag_service = RAGService()


def generate_answer(db: Session, question: str, company_id: str) -> str:
    """
    Generate answer using RAG pipeline
    """
    return rag_service.generate_answer(db, question, company_id)