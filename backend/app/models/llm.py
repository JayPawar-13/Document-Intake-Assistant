from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class LLMExtractionResult(BaseModel):
    updates: Dict[str, Any] = Field(default_factory=dict)
    needs_clarification: bool = False
    clarification_question: Optional[str] = None
    suggested_quick_replies: Optional[List[str]] = Field(default_factory=list)
    reason: Optional[str] = None
    is_correction: bool = False
    assistant_message: Optional[str] = None
