import logging
import traceback
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, desc
from enum import Enum

from app.db.database import SessionLocal

logger = logging.getLogger(__name__)


class ErrorLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ErrorLogger:
    """
    Centralized error logging and management service
    """
    
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """
        Setup enhanced logging configuration
        """
        # Create custom formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Setup file handler for errors
        file_handler = logging.FileHandler('app_errors.log')
        file_handler.setLevel(logging.ERROR)
        file_handler.setFormatter(formatter)
        
        # Add handler to root logger
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)
    
    def log_error(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        company_id: Optional[str] = None,
        level: ErrorLevel = ErrorLevel.ERROR
    ) -> str:
        """
        Log an error with context information
        """
        error_id = f"error_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        error_data = {
            "error_id": error_id,
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.value,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context or {},
            "user_id": user_id,
            "company_id": company_id
        }
        
        # Log to standard logger
        log_message = f"[{error_id}] {error_data['error_type']}: {error_data['error_message']}"
        if context:
            log_message += f" | Context: {json.dumps(context)}"
        
        if level == ErrorLevel.CRITICAL:
            logger.critical(log_message)
        elif level == ErrorLevel.ERROR:
            logger.error(log_message)
        elif level == ErrorLevel.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Store in database (if possible)
        try:
            self._store_error_in_db(error_data)
        except Exception as db_error:
            logger.critical(f"Failed to store error in database: {db_error}")
        
        return error_id
    
    def _store_error_in_db(self, error_data: Dict[str, Any]):
        """
        Store error information in database
        """
        db = SessionLocal()
        try:
            # Create error_logs table if it doesn't exist
            db.execute(text("""
                CREATE TABLE IF NOT EXISTS error_logs (
                    id SERIAL PRIMARY KEY,
                    error_id VARCHAR(100) UNIQUE NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    level VARCHAR(20) NOT NULL,
                    error_type VARCHAR(255) NOT NULL,
                    error_message TEXT NOT NULL,
                    traceback TEXT,
                    context JSONB,
                    user_id UUID,
                    company_id UUID,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """))
            
            # Insert error log
            db.execute(text("""
                INSERT INTO error_logs 
                (error_id, timestamp, level, error_type, error_message, traceback, context, user_id, company_id)
                VALUES (:error_id, :timestamp, :level, :error_type, :error_message, :traceback, :context, :user_id, :company_id)
            """), {
                'error_id': error_data['error_id'],
                'timestamp': datetime.fromisoformat(error_data['timestamp']),
                'level': error_data['level'],
                'error_type': error_data['error_type'],
                'error_message': error_data['error_message'],
                'traceback': error_data['traceback'],
                'context': json.dumps(error_data['context']),
                'user_id': error_data['user_id'],
                'company_id': error_data['company_id']
            })
            
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to store error in database: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_error_logs(
        self, 
        db: Session,
        company_id: Optional[str] = None,
        level: Optional[ErrorLevel] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve error logs with filtering
        """
        try:
            # Build query with filters
            query_parts = ["SELECT * FROM error_logs WHERE 1=1"]
            params = {}
            
            if company_id:
                query_parts.append("AND company_id = :company_id")
                params['company_id'] = company_id
            
            if level:
                query_parts.append("AND level = :level")
                params['level'] = level.value
            
            if start_date:
                query_parts.append("AND timestamp >= :start_date")
                params['start_date'] = start_date
            
            if end_date:
                query_parts.append("AND timestamp <= :end_date")
                params['end_date'] = end_date
            
            query_parts.append("ORDER BY timestamp DESC")
            query_parts.append("LIMIT :limit OFFSET :offset")
            params['limit'] = limit
            params['offset'] = offset
            
            query = " ".join(query_parts)
            
            result = db.execute(text(query), params)
            
            logs = []
            for row in result:
                log_data = {
                    'id': row.id,
                    'error_id': row.error_id,
                    'timestamp': row.timestamp.isoformat(),
                    'level': row.level,
                    'error_type': row.error_type,
                    'error_message': row.error_message,
                    'traceback': row.traceback,
                    'context': json.loads(row.context) if row.context else {},
                    'user_id': str(row.user_id) if row.user_id else None,
                    'company_id': str(row.company_id) if row.company_id else None,
                    'created_at': row.created_at.isoformat()
                }
                logs.append(log_data)
            
            return logs
            
        except Exception as e:
            logger.error(f"Failed to retrieve error logs: {e}")
            return []
    
    def get_error_statistics(
        self, 
        db: Session,
        company_id: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get error statistics for the specified period
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Build base query
            base_params = {'start_date': start_date}
            company_filter = ""
            if company_id:
                company_filter = "AND company_id = :company_id"
                base_params['company_id'] = company_id
            
            # Total errors
            total_result = db.execute(text(f"""
                SELECT COUNT(*) as count 
                FROM error_logs 
                WHERE timestamp >= :start_date {company_filter}
            """), base_params)
            total_errors = total_result.scalar()
            
            # Errors by level
            level_result = db.execute(text(f"""
                SELECT level, COUNT(*) as count 
                FROM error_logs 
                WHERE timestamp >= :start_date {company_filter}
                GROUP BY level
            """), base_params)
            errors_by_level = {row.level: row.count for row in level_result}
            
            # Errors by type
            type_result = db.execute(text(f"""
                SELECT error_type, COUNT(*) as count 
                FROM error_logs 
                WHERE timestamp >= :start_date {company_filter}
                GROUP BY error_type
                ORDER BY count DESC
                LIMIT 10
            """), base_params)
            errors_by_type = [(row.error_type, row.count) for row in type_result]
            
            # Daily error counts
            daily_result = db.execute(text(f"""
                SELECT DATE(timestamp) as date, COUNT(*) as count
                FROM error_logs 
                WHERE timestamp >= :start_date {company_filter}
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """), base_params)
            daily_errors = [(row.date.isoformat(), row.count) for row in daily_result]
            
            return {
                'period_days': days,
                'company_id': company_id,
                'total_errors': total_errors,
                'errors_by_level': errors_by_level,
                'top_error_types': errors_by_type,
                'daily_error_counts': daily_errors,
                'average_errors_per_day': round(total_errors / days, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get error statistics: {e}")
            return {'error': str(e)}


# Global error logger instance
error_logger = ErrorLogger()


def log_application_error(
    error: Exception,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    company_id: Optional[str] = None,
    level: ErrorLevel = ErrorLevel.ERROR
) -> str:
    """
    Log an application error
    """
    return error_logger.log_error(error, context, user_id, company_id, level)


def get_error_logs(
    db: Session,
    company_id: Optional[str] = None,
    level: Optional[str] = None,
    days: int = 7,
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get error logs with filtering
    """
    error_level = None
    if level:
        try:
            error_level = ErrorLevel(level.upper())
        except ValueError:
            pass
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    return error_logger.get_error_logs(
        db, company_id, error_level, start_date, None, limit, offset
    )


def get_error_statistics(
    db: Session,
    company_id: Optional[str] = None,
    days: int = 7
) -> Dict[str, Any]:
    """
    Get error statistics
    """
    return error_logger.get_error_statistics(db, company_id, days)