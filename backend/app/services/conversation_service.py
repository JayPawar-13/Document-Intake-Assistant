import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.database.mongodb import db_manager
from app.models.conversation import Message, MessageRole


class ConversationService:
    @staticmethod
    async def add_message(
        session_id: str,
        role: MessageRole,
        content: str,
        quick_replies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add and persist a new message in MongoDB"""
        msg_id = str(uuid.uuid4())
        now = datetime.utcnow()
        doc = {
            "_id": msg_id,
            "session_id": session_id,
            "role": role.value if isinstance(role, MessageRole) else role,
            "content": content,
            "quick_replies": quick_replies or [],
            "metadata": metadata or {},
            "created_at": now.isoformat()
        }
        await db_manager.conversations.insert_one(doc)

        # Update session updated_at
        await db_manager.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"updated_at": now.isoformat()}}
        )

        return doc

    @staticmethod
    async def get_messages(session_id: str) -> List[Dict[str, Any]]:
        """Retrieve conversation history for a session sorted chronologically"""
        cursor = db_manager.conversations.find({"session_id": session_id}).sort("created_at", 1)
        messages = []
        async for doc in cursor:
            messages.append({
                "id": str(doc["_id"]),
                "session_id": doc["session_id"],
                "role": doc["role"],
                "content": doc["content"],
                "quick_replies": doc.get("quick_replies", []),
                "metadata": doc.get("metadata", {}),
                "created_at": doc.get("created_at")
            })
        return messages

    @staticmethod
    async def clear_messages(session_id: str) -> None:
        """Clear conversation messages and reset to initial welcome message"""
        await db_manager.conversations.delete_many({"session_id": session_id})
        welcome_text = "Hi! I'll help you create your Personal Wishes Document. Let's get started. What is your full legal name?"
        await ConversationService.add_message(
            session_id=session_id,
            role=MessageRole.ASSISTANT,
            content=welcome_text,
            metadata={"type": "welcome"}
        )
