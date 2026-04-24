from typing import Optional, List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message")
    session_id: str = Field(..., min_length=1, description="Frontend session id")
    page: Optional[str] = Field(default=None, description="Website page path")
    language_hint: Optional[str] = Field(default=None, description="Optional frontend language hint")


class ChatResponse(BaseModel):
    answer: str
    language: str
    sources_used: bool
    session_id: str
    suggestions: List[str] = []


class FeedbackRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None