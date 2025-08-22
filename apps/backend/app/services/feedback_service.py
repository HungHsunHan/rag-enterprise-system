from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
import logging

from app.db.models import FeedbackLog, User

logger = logging.getLogger(__name__)


def save_feedback(
    db: Session,
    user_id: str,
    question: str,
    answer: str,
    feedback: str
) -> FeedbackLog:
    """
    Save user feedback for a question-answer pair
    """
    feedback_log = FeedbackLog(
        user_id=user_id,
        question=question,
        answer=answer,
        feedback=feedback
    )
    db.add(feedback_log)
    db.commit()
    db.refresh(feedback_log)
    return feedback_log


def get_feedback_list(
    db: Session,
    company_id: str,
    feedback_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> List[FeedbackLog]:
    """
    Get paginated feedback list for a company
    Optionally filter by feedback type (POSITIVE/NEGATIVE)
    Include proper multi-tenant filtering
    """
    try:
        query = db.query(FeedbackLog).join(User).filter(
            User.company_id == company_id
        )
        
        # Filter by feedback type if provided
        if feedback_type:
            query = query.filter(FeedbackLog.feedback == feedback_type)
        
        # Apply pagination and ordering
        feedback_list = query.order_by(
            FeedbackLog.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        logger.info(f"Retrieved {len(feedback_list)} feedback records for company {company_id}")
        return feedback_list
        
    except Exception as e:
        logger.error(f"Error retrieving feedback list for company {company_id}: {e}")
        return []


def get_feedback_stats(db: Session, company_id: str) -> dict:
    """
    Return statistics like total feedback count, positive count, negative count, positive percentage
    """
    try:
        # Get total count and positive count in one query
        stats_query = db.query(
            func.count(FeedbackLog.id).label('total_count'),
            func.sum(
                func.case(
                    (FeedbackLog.feedback == 'POSITIVE', 1),
                    else_=0
                )
            ).label('positive_count')
        ).join(User).filter(
            User.company_id == company_id
        ).first()
        
        total_count = stats_query.total_count or 0
        positive_count = stats_query.positive_count or 0
        negative_count = total_count - positive_count
        
        # Calculate positive percentage
        positive_percentage = (positive_count / total_count * 100) if total_count > 0 else 0
        
        stats = {
            'total_count': total_count,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'positive_percentage': round(positive_percentage, 2)
        }
        
        logger.info(f"Retrieved feedback stats for company {company_id}: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error retrieving feedback stats for company {company_id}: {e}")
        return {
            'total_count': 0,
            'positive_count': 0,
            'negative_count': 0,
            'positive_percentage': 0
        }


def search_feedback(
    db: Session,
    company_id: str,
    search_term: str,
    limit: int = 100,
    offset: int = 0
) -> List[FeedbackLog]:
    """
    Search feedback by question or answer content
    """
    try:
        if not search_term or not search_term.strip():
            logger.warning(f"Empty search term provided for company {company_id}")
            return []
        
        search_pattern = f"%{search_term.strip()}%"
        
        feedback_list = db.query(FeedbackLog).join(User).filter(
            User.company_id == company_id,
            or_(
                FeedbackLog.question.ilike(search_pattern),
                FeedbackLog.answer.ilike(search_pattern)
            )
        ).order_by(
            FeedbackLog.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        logger.info(f"Found {len(feedback_list)} feedback records matching '{search_term}' for company {company_id}")
        return feedback_list
        
    except Exception as e:
        logger.error(f"Error searching feedback for company {company_id} with term '{search_term}': {e}")
        return []