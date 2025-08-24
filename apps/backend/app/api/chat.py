from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import json

from app.core.deps import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.schemas.chat import QuestionRequest, AnswerResponse, FeedbackRequest
from app.services.rag_service import generate_answer, generate_answer_stream
from app.services.feedback_service import save_feedback

router = APIRouter()


@router.post("/chat", response_model=AnswerResponse)
def ask_question(
    question_data: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a question and get an AI-generated answer (non-streaming)
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


@router.post("/chat/stream")
async def ask_question_stream(
    question_data: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a question and get a streaming AI-generated answer
    """
    async def stream_response():
        try:
            async for token in generate_answer_stream(
                db, 
                question_data.question, 
                str(current_user.company_id)
            ):
                # Send each token as Server-Sent Events (SSE) format
                yield f"data: {json.dumps({'token': token})}\n\n"
        except Exception as e:
            # Send error message
            error_msg = "Sorry, I encountered an error while processing your question. Please try again or contact your HR team for assistance."
            yield f"data: {json.dumps({'token': error_msg})}\n\n"
        finally:
            # Send end signal
            yield f"data: {json.dumps({'done': True})}\n\n"
    
    return StreamingResponse(
        stream_response(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
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