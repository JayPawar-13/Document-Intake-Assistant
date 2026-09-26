import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.database.mongodb import db_manager
from app.models.state import StructuredState
from app.models.conversation import Message, MessageRole
from app.services.document_service import DocumentService


class SessionService:
    @staticmethod
    async def create_session(title: str = "Personal Wishes Document Intake") -> Dict[str, Any]:
        """Creates a new session, initial state, initial document, and welcome message"""
        session_id = str(uuid.uuid4())[:8]
        now = datetime.utcnow()

        # 1. Create session record
        session_doc = {
            "_id": session_id,
            "session_id": session_id,
            "title": title,
            "status": "active",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        await db_manager.sessions.insert_one(session_doc)

        # 2. Create blank structured state
        state = StructuredState(session_id=session_id)
        state.update_field_statuses()
        state_doc = state.model_dump()
        state_doc["_id"] = session_id
        state_doc["created_at"] = now.isoformat()
        state_doc["updated_at"] = now.isoformat()
        await db_manager.structured_states.insert_one(state_doc)

        # 3. Create initial document
        doc_bundle = DocumentService.generate_document_bundle(state)
        doc_record = {
            "_id": session_id,
            "session_id": session_id,
            "document_html": doc_bundle["document_html"],
            "document_text": doc_bundle["document_text"],
            "created_at": now.isoformat(),
            "updated_at": now.isoformat()
        }
        await db_manager.documents.insert_one(doc_record)

        # 4. Insert initial welcoming assistant message
        welcome_text = "Hi! I'll help you create your Personal Wishes Document. Let's get started. What is your full legal name?"
        welcome_msg = {
            "_id": str(uuid.uuid4()),
            "session_id": session_id,
            "role": MessageRole.ASSISTANT.value,
            "content": welcome_text,
            "quick_replies": [],
            "metadata": {"type": "welcome"},
            "created_at": now.isoformat()
        }
        await db_manager.conversations.insert_one(welcome_msg)

        return {
            "session_id": session_id,
            "status": "active",
            "initial_message": welcome_text,
            "state": state.to_clean_dict(),
            "document": doc_bundle
        }

    @staticmethod
    async def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        session_doc = await db_manager.sessions.find_one({"session_id": session_id})
        return session_doc

    @staticmethod
    async def list_recent_sessions(limit: int = 10) -> List[Dict[str, Any]]:
        cursor = db_manager.sessions.find().sort("updated_at", -1).limit(limit)
        results = []
        async for doc in cursor:
            results.append({
                "session_id": doc["session_id"],
                "title": doc.get("title", "Personal Wishes Document"),
                "status": doc.get("status", "active"),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at")
            })
        return results
