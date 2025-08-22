from typing import List, Optional
from sqlalchemy.orm import Session
import logging
import openai
from openai import AsyncOpenAI

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
        self.llm_client = None
        self._initialize_llm_client()
    
    def _initialize_llm_client(self):
        """
        Initialize LLM client (OpenAI)
        """
        if settings.OPENAI_API_KEY:
            try:
                self.llm_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("Initialized OpenAI client")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
        else:
            logger.warning("OpenAI API key not provided, using mock responses")
    
    async def generate_answer(self, db: Session, question: str, company_id: str) -> str:
        """
        Generate answer using RAG pipeline
        """
        try:
            # Step 1: Convert question to embedding
            query_embedding = self._vectorize_question(question)
            if query_embedding is None:
                return self._fallback_response(question)
            
            # Step 2: Perform vector similarity search
            relevant_chunks = search_similar_chunks(
                db, 
                query_embedding.tolist(), 
                company_id, 
                limit=5
            )
            
            if not relevant_chunks:
                return "I don't have enough information to answer your question. Please make sure relevant documents have been uploaded to the knowledge base."
            
            # Step 3: Construct context from relevant chunks
            context = self._build_context(relevant_chunks)
            
            # Step 4: Generate answer using LLM
            answer = await self._generate_llm_response(question, context)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return "I'm sorry, I encountered an error while processing your question. Please try again or contact your HR team for assistance."
    
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
    
    async def _generate_llm_response(self, question: str, context: str) -> str:
        """
        Generate response using LLM
        """
        if not self.llm_client:
            return self._mock_llm_response(question, context)
        
        try:
            # Construct prompt
            prompt = self._build_prompt(question, context)
            
            # Call OpenAI API
            response = await self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful HR assistant. Answer questions based on the provided context from company documents. Be professional, accurate, and concise."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"LLM API error: {e}")
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
    Synchronous wrapper for generate_answer (for backward compatibility)
    """
    import asyncio
    return asyncio.run(rag_service.generate_answer(db, question, company_id))


async def generate_answer_async(db: Session, question: str, company_id: str) -> str:
    """
    Asynchronous version of generate_answer
    """
    return await rag_service.generate_answer(db, question, company_id)