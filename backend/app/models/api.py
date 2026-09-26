from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class CreateSessionRequest(BaseModel):
    title: Optional[str] = "Personal Wishes Document Intake"


class CreateSessionResponse(BaseModel):
    session_id: str
    status: str
    initial_message: str
    state: Dict[str, Any]
    document: Dict[str, Any]


class SessionResponse(BaseModel):
    session_id: str
    status: str
    title: str
    created_at: str
    updated_at: str
    completion_percentage: int


class SendMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message content")


class SendMessageResponse(BaseModel):
    # Section 52 standard response
    message: str
    structured_state: Dict[str, Any] = Field(default_factory=dict)
    field_status: Dict[str, str] = Field(default_factory=dict)
    next_action: str = "ASK_NEXT_QUESTION"
    next_field: Optional[str] = None
    progress: Dict[str, int] = Field(default_factory=dict)

    # Existing frontend backward-compatible fields
    assistant_message: str
    quick_replies: List[str] = Field(default_factory=list)
    state: Dict[str, Any] = Field(default_factory=dict)
    document: Dict[str, Any] = Field(default_factory=dict)
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    is_correction: bool = False


class DocumentResponse(BaseModel):
    session_id: str
    document_html: str
    document_text: str
    updated_at: str


class HealthResponse(BaseModel):
    status: str
    database: str
    llm_provider: str
    version: str
