import logging
import time
import psutil
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from app.db.models import KnowledgeDocument, DocumentChunk, FeedbackLog, User, Company
from app.db.database import get_db

logger = logging.getLogger(__name__)


class SystemMonitor:
    """
    System monitoring and health check service
    """
    
    def __init__(self):
        self.start_time = datetime.utcnow()
    
    async def get_system_health(self, db: Session) -> Dict[str, Any]:
        """
        Comprehensive system health check
        """
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "status": "healthy",
            "components": {}
        }
        
        try:
            # Database health
            health_data["components"]["database"] = await self._check_database_health(db)
            
            # System resources
            health_data["components"]["system"] = self._check_system_resources()
            
            # Application metrics
            health_data["components"]["application"] = await self._check_application_metrics(db)
            
            # Determine overall status
            failed_components = [
                name for name, component in health_data["components"].items() 
                if component.get("status") != "healthy"
            ]
            
            if failed_components:
                health_data["status"] = "degraded" if len(failed_components) == 1 else "unhealthy"
                health_data["failed_components"] = failed_components
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            health_data["status"] = "unhealthy"
            health_data["error"] = str(e)
        
        return health_data
    
    async def _check_database_health(self, db: Session) -> Dict[str, Any]:
        """
        Check database connectivity and basic metrics
        """
        try:
            start_time = time.time()
            
            # Test basic connectivity
            result = db.execute(text("SELECT 1")).scalar()
            if result != 1:
                return {"status": "unhealthy", "error": "Database connectivity test failed"}
            
            # Check vector extension
            vector_result = db.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'vector'")).scalar()
            vector_available = vector_result is not None
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            return {
                "status": "healthy",
                "response_time_ms": round(response_time, 2),
                "vector_extension": vector_available,
                "connection_active": True
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "connection_active": False
            }
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """
        Check system resource usage
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Determine status based on resource usage
            status = "healthy"
            warnings = []
            
            if cpu_percent > 80:
                status = "degraded"
                warnings.append("High CPU usage")
            
            if memory.percent > 85:
                status = "degraded"
                warnings.append("High memory usage")
            
            if disk.percent > 90:
                status = "degraded"
                warnings.append("High disk usage")
            
            return {
                "status": status,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": disk.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def _check_application_metrics(self, db: Session) -> Dict[str, Any]:
        """
        Check application-specific metrics
        """
        try:
            # Count total entities
            company_count = db.query(func.count(Company.id)).scalar()
            user_count = db.query(func.count(User.id)).scalar()
            document_count = db.query(func.count(KnowledgeDocument.id)).scalar()
            chunk_count = db.query(func.count(DocumentChunk.id)).scalar()
            
            # Count processing documents
            processing_docs = db.query(func.count(KnowledgeDocument.id)).filter(
                KnowledgeDocument.status == 'PROCESSING'
            ).scalar()
            
            # Recent activity (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(hours=24)
            recent_uploads = db.query(func.count(KnowledgeDocument.id)).filter(
                KnowledgeDocument.uploaded_at >= yesterday
            ).scalar()
            
            recent_feedback = db.query(func.count(FeedbackLog.id)).filter(
                FeedbackLog.created_at >= yesterday
            ).scalar()
            
            # Determine status
            status = "healthy"
            warnings = []
            
            if processing_docs > 10:
                warnings.append(f"High number of documents still processing: {processing_docs}")
                status = "degraded"
            
            return {
                "status": status,
                "total_companies": company_count,
                "total_users": user_count,
                "total_documents": document_count,
                "total_chunks": chunk_count,
                "processing_documents": processing_docs,
                "recent_uploads_24h": recent_uploads,
                "recent_feedback_24h": recent_feedback,
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"Application metrics check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
    
    async def get_usage_statistics(self, db: Session, company_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed usage statistics
        """
        try:
            # Base query filters
            filters = []
            if company_id:
                filters.append(f"company_id = '{company_id}'")
            
            # Time periods
            now = datetime.utcnow()
            last_24h = now - timedelta(hours=24)
            last_7d = now - timedelta(days=7)
            last_30d = now - timedelta(days=30)
            
            stats = {
                "timestamp": now.isoformat(),
                "company_id": company_id,
                "documents": await self._get_document_stats(db, company_id),
                "usage": await self._get_usage_stats(db, company_id),
                "feedback": await self._get_feedback_stats(db, company_id),
                "performance": await self._get_performance_stats(db, company_id)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Usage statistics failed: {e}")
            return {"error": str(e)}
    
    async def _get_document_stats(self, db: Session, company_id: Optional[str]) -> Dict[str, Any]:
        """Get document-related statistics"""
        query = db.query(KnowledgeDocument)
        if company_id:
            query = query.filter(KnowledgeDocument.company_id == company_id)
        
        total_docs = query.count()
        completed_docs = query.filter(KnowledgeDocument.status == 'COMPLETED').count()
        processing_docs = query.filter(KnowledgeDocument.status == 'PROCESSING').count()
        failed_docs = query.filter(KnowledgeDocument.status == 'FAILED').count()
        
        # Recent uploads
        yesterday = datetime.utcnow() - timedelta(hours=24)
        recent_uploads = query.filter(KnowledgeDocument.uploaded_at >= yesterday).count()
        
        return {
            "total": total_docs,
            "completed": completed_docs,
            "processing": processing_docs,
            "failed": failed_docs,
            "recent_uploads_24h": recent_uploads,
            "success_rate": round((completed_docs / total_docs * 100) if total_docs > 0 else 0, 2)
        }
    
    async def _get_usage_stats(self, db: Session, company_id: Optional[str]) -> Dict[str, Any]:
        """Get usage-related statistics"""
        # This would typically come from access logs or request tracking
        # For now, we'll use feedback as a proxy for usage
        query = db.query(FeedbackLog)
        if company_id:
            query = query.join(User).filter(User.company_id == company_id)
        
        # Time-based queries
        now = datetime.utcnow()
        yesterday = now - timedelta(hours=24)
        last_week = now - timedelta(days=7)
        
        total_queries = query.count()
        queries_24h = query.filter(FeedbackLog.created_at >= yesterday).count()
        queries_7d = query.filter(FeedbackLog.created_at >= last_week).count()
        
        return {
            "total_queries": total_queries,
            "queries_last_24h": queries_24h,
            "queries_last_7d": queries_7d,
            "avg_queries_per_day": round(queries_7d / 7, 2)
        }
    
    async def _get_feedback_stats(self, db: Session, company_id: Optional[str]) -> Dict[str, Any]:
        """Get feedback statistics"""
        query = db.query(FeedbackLog)
        if company_id:
            query = query.join(User).filter(User.company_id == company_id)
        
        total_feedback = query.count()
        positive_feedback = query.filter(FeedbackLog.feedback == 'POSITIVE').count()
        negative_feedback = query.filter(FeedbackLog.feedback == 'NEGATIVE').count()
        
        satisfaction_rate = round((positive_feedback / total_feedback * 100) if total_feedback > 0 else 0, 2)
        
        return {
            "total_feedback": total_feedback,
            "positive_feedback": positive_feedback,
            "negative_feedback": negative_feedback,
            "satisfaction_rate": satisfaction_rate
        }
    
    async def _get_performance_stats(self, db: Session, company_id: Optional[str]) -> Dict[str, Any]:
        """Get performance-related statistics"""
        # Chunk statistics
        chunk_query = db.query(DocumentChunk)
        if company_id:
            chunk_query = chunk_query.filter(DocumentChunk.company_id == company_id)
        
        total_chunks = chunk_query.count()
        chunks_with_embeddings = chunk_query.filter(DocumentChunk.embedding.isnot(None)).count()
        
        embedding_rate = round((chunks_with_embeddings / total_chunks * 100) if total_chunks > 0 else 0, 2)
        
        return {
            "total_chunks": total_chunks,
            "chunks_with_embeddings": chunks_with_embeddings,
            "embedding_completion_rate": embedding_rate
        }


# Global monitor instance
system_monitor = SystemMonitor()


async def get_system_health(db: Session) -> Dict[str, Any]:
    """Get system health status"""
    return await system_monitor.get_system_health(db)


async def get_usage_statistics(db: Session, company_id: Optional[str] = None) -> Dict[str, Any]:
    """Get usage statistics"""
    return await system_monitor.get_usage_statistics(db, company_id)