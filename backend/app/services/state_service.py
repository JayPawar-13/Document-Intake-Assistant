from datetime import datetime
from typing import Optional, Dict, Any, Tuple
from app.database.mongodb import db_manager
from app.models.state import StructuredState, Executor, FieldStatus, SpecificGift
from app.services.document_service import DocumentService


class StateService:
    @staticmethod
    async def get_state(session_id: str) -> Optional[StructuredState]:
        """Fetch structured state from MongoDB"""
        doc = await db_manager.structured_states.find_one({"session_id": session_id})
        if not doc:
            return None
        
        # Convert dict to StructuredState
        exec_data = doc.get("executor") or {}
        executor = Executor(
            name=exec_data.get("name"),
            relationship=exec_data.get("relationship")
        )

        raw_gifts = doc.get("specific_gifts") or []
        parsed_gifts = []
        for g in raw_gifts:
            if isinstance(g, dict) and "item" in g and "description" in g:
                parsed_gifts.append(SpecificGift(**g))
            else:
                parsed_gifts.append(g)

        raw_statuses = doc.get("field_statuses") or {}
        field_statuses = {}
        for k, v in raw_statuses.items():
            try:
                field_statuses[k] = FieldStatus(v)
            except Exception:
                field_statuses[k] = FieldStatus.UNKNOWN

        state = StructuredState(
            session_id=session_id,
            full_name=doc.get("full_name"),
            home_address=doc.get("home_address"),
            covers_worldwide_assets=doc.get("covers_worldwide_assets"),
            has_children=doc.get("has_children"),
            children=doc.get("children") or [],
            executor=executor,
            specific_gifts=parsed_gifts,
            additional_wishes=doc.get("additional_wishes"),
            field_statuses=field_statuses,
        )
        return state

    @staticmethod
    async def save_state(state: StructuredState) -> None:
        """Persist structured state to MongoDB"""
        state.updated_at = datetime.utcnow()
        state.update_field_statuses()
        data = state.model_dump()
        data["_id"] = state.session_id
        data["updated_at"] = state.updated_at.isoformat()
        if "created_at" in data and isinstance(data["created_at"], datetime):
            data["created_at"] = data["created_at"].isoformat()

        # Serialize specific_gifts cleanly
        if "specific_gifts" in data:
            data["specific_gifts"] = [
                g.model_dump() if isinstance(g, SpecificGift) else g
                for g in state.specific_gifts
            ]

        await db_manager.structured_states.replace_one(
            {"session_id": state.session_id},
            data,
            upsert=True
        )

    @classmethod
    async def apply_updates(
        cls,
        session_id: str,
        validated_updates: Dict[str, Any],
        status_updates: Optional[Dict[str, FieldStatus]] = None
    ) -> Tuple[StructuredState, Dict[str, Any]]:
        """
        Applies validated updates to current state, persists to MongoDB,
        regenerates document, and persists document to MongoDB.
        """
        current_state = await cls.get_state(session_id)
        if not current_state:
            current_state = StructuredState(session_id=session_id)

        # Apply top-level scalar fields
        if "full_name" in validated_updates:
            current_state.full_name = validated_updates["full_name"]
        if "home_address" in validated_updates:
            current_state.home_address = validated_updates["home_address"]
        if "covers_worldwide_assets" in validated_updates:
            current_state.covers_worldwide_assets = validated_updates["covers_worldwide_assets"]
        
        # Family fields
        if "has_children" in validated_updates:
            current_state.has_children = validated_updates["has_children"]
            if current_state.has_children is False:
                current_state.children = []
                current_state.field_statuses["children"] = FieldStatus.NOT_APPLICABLE
        if "children" in validated_updates:
            current_state.children = validated_updates["children"]
            if current_state.children:
                current_state.has_children = True

        # Executor
        if "executor" in validated_updates:
            exec_up = validated_updates["executor"]
            if "name" in exec_up and exec_up["name"] is not None:
                current_state.executor.name = exec_up["name"]
            if "relationship" in exec_up and exec_up["relationship"] is not None:
                current_state.executor.relationship = exec_up["relationship"]

        # Gifts
        if "specific_gifts" in validated_updates:
            current_state.specific_gifts = validated_updates["specific_gifts"]

        # Wishes
        if "additional_wishes" in validated_updates:
            current_state.additional_wishes = validated_updates["additional_wishes"]

        # Apply explicit status updates if supplied
        if status_updates:
            current_state.field_statuses.update(status_updates)

        # Save updated state
        await cls.save_state(current_state)

        # Regenerate document
        doc_bundle = DocumentService.generate_document_bundle(current_state)
        await db_manager.documents.replace_one(
            {"session_id": session_id},
            {
                "_id": session_id,
                "session_id": session_id,
                "document_html": doc_bundle["document_html"],
                "document_text": doc_bundle["document_text"],
                "updated_at": doc_bundle["updated_at"]
            },
            upsert=True
        )

        return current_state, doc_bundle
