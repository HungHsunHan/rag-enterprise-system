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
) -> List[dict]:
    """
    Get paginated feedback list for a company
    Optionally filter by feedback type (POSITIVE/NEGATIVE)
    Include proper multi-tenant filtering
    Returns list of dictionaries with UUID fields converted to strings
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
        
        # Convert to dict with proper string conversion for UUIDs
        result = []
        for feedback in feedback_list:
            result.append({
                'id': str(feedback.id),
                'user_id': str(feedback.user_id) if feedback.user_id else None,
                'question': feedback.question,
                'answer': feedback.answer,
                'feedback': feedback.feedback,
                'created_at': feedback.created_at
            })
        
        logger.info(f"Retrieved {len(result)} feedback records for company {company_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error retrieving feedback list for company {company_id}: {e}")
        return []


def get_feedback_stats(db: Session, company_id: str) -> dict:
    """
    Return statistics like total feedback count, positive count, negative count, positive percentage
    """
    try:
        # Get total count
        total_count = db.query(func.count(FeedbackLog.id)).join(User).filter(
            User.company_id == company_id
        ).scalar() or 0
        
        # Get positive count
        positive_count = db.query(func.count(FeedbackLog.id)).join(User).filter(
            User.company_id == company_id,
            FeedbackLog.feedback == 'POSITIVE'
        ).scalar() or 0
        
        # Get negative count
        negative_count = db.query(func.count(FeedbackLog.id)).join(User).filter(
            User.company_id == company_id,
            FeedbackLog.feedback == 'NEGATIVE'
        ).scalar() or 0
        
        # Calculate positive percentage
        positive_percentage = (positive_count / total_count * 100) if total_count > 0 else 0
        
        stats = {
            'total_count': int(total_count),
            'positive_count': int(positive_count),
            'negative_count': int(negative_count),
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
) -> List[dict]:
    """
    Search feedback by question or answer content
    Returns list of dictionaries with UUID fields converted to strings
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
        
        # Convert to dict with proper string conversion for UUIDs
        result = []
        for feedback in feedback_list:
            result.append({
                'id': str(feedback.id),
                'user_id': str(feedback.user_id) if feedback.user_id else None,
                'question': feedback.question,
                'answer': feedback.answer,
                'feedback': feedback.feedback,
                'created_at': feedback.created_at
            })
        
        logger.info(f"Found {len(result)} feedback records matching '{search_term}' for company {company_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error searching feedback for company {company_id} with term '{search_term}': {e}")
        return []