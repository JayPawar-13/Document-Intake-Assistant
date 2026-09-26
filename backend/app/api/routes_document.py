from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from app.services.session_service import SessionService
from app.services.state_service import StateService
from app.services.document_service import DocumentService
from app.database.mongodb import db_manager

router = APIRouter(prefix="/api/sessions/{session_id}/document", tags=["document"])


@router.get("", response_model=Dict[str, Any])
async def get_document(session_id: str):
    """Retrieve current generated Personal Wishes Document for a session"""
    session = await SessionService.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found."
        )

    doc_record = await db_manager.documents.find_one({"session_id": session_id})
    if not doc_record:
        # Generate on the fly if not cached
        state = await StateService.get_state(session_id)
        if not state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="State not found for document generation."
            )
        bundle = DocumentService.generate_document_bundle(state)
        return {
            "session_id": session_id,
            "document_html": bundle["document_html"],
            "document_text": bundle["document_text"],
            "updated_at": bundle["updated_at"]
        }

    return {
        "session_id": session_id,
        "document_html": doc_record.get("document_html", ""),
        "document_text": doc_record.get("document_text", ""),
        "updated_at": doc_record.get("updated_at", "")
    }


@router.post("/regenerate", response_model=Dict[str, Any])
async def regenerate_document(session_id: str):
    """Force document regeneration using current MongoDB structured state"""
    session = await SessionService.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found."
        )

    state = await StateService.get_state(session_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="State not found for document generation."
        )

    bundle = DocumentService.generate_document_bundle(state)
    await db_manager.documents.replace_one(
        {"session_id": session_id},
        {
            "_id": session_id,
            "session_id": session_id,
            "document_html": bundle["document_html"],
            "document_text": bundle["document_text"],
            "updated_at": bundle["updated_at"]
        },
        upsert=True
    )

    return {
        "status": "ok",
        "message": "Document regenerated successfully.",
        "session_id": session_id,
        "document_html": bundle["document_html"],
        "document_text": bundle["document_text"],
        "updated_at": bundle["updated_at"]
    }
