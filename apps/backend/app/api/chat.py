from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.chat import QuestionRequest, AnswerResponse, FeedbackRequest
from app.services.rag_service import generate_answer
from app.services.feedback_service import save_feedback

router = APIRouter()


@router.post("/chat", response_model=AnswerResponse)
def ask_question(
    question_data: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a question and get an AI-generated answer
    """
    try:
        answer = generate_answer(
            db, 
            question_data.question, 
            str(current_user.company_id)
        )
        return AnswerResponse(answer=answer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate answer"
        )


@router.post("/chat/feedback")
def submit_feedback(
    feedback_data: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback for a question-answer pair
    """
    save_feedback(
        db,
        str(current_user.id),
        feedback_data.question,
        feedback_data.answer,
        feedback_data.feedback
    )
    return {"message": "Feedback saved successfully"}