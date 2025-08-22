from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime


class QuestionRequest(BaseModel):
    question: str


class AnswerResponse(BaseModel):
    answer: str


class FeedbackRequest(BaseModel):
    question: str
    answer: str
    feedback: Literal["POSITIVE", "NEGATIVE"]


class FeedbackResponse(BaseModel):
    id: str
    user_id: Optional[str]
    question: str
    answer: str
    feedback: str
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackStats(BaseModel):
    total_count: int
    positive_count: int
    negative_count: int
    positive_percentage: float