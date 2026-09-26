from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    id: Optional[str] = None
    session_id: str
    role: MessageRole
    content: str
    quick_replies: Optional[List[str]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "role": self.role.value,
            "content": self.content,
            "quick_replies": self.quick_replies or [],
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class ConversationHistory(BaseModel):
    session_id: str
    messages: List[Message] = Field(default_factory=list)
