from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from app.models.state import StateUpdateRequest
from app.services.session_service import SessionService
from app.services.state_service import StateService
from app.services.validation_service import ValidationService
from app.services.document_service import DocumentService

router = APIRouter(prefix="/api/sessions/{session_id}/state", tags=["state"])


@router.get("", response_model=Dict[str, Any])
async def get_state(session_id: str):
    """Retrieve current structured state for a session"""
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
            detail="Structured state not found for this session."
        )

    return {
        "session_id": session_id,
        "state": state.to_clean_dict(),
        "field_statuses": state.field_statuses,
        "completion_percentage": state.get_completion_percentage(),
        "missing_fields": state.get_missing_fields(),
        "updated_at": state.updated_at.isoformat()
    }


@router.patch("", response_model=Dict[str, Any])
async def update_state(session_id: str, payload: StateUpdateRequest):
    """
    Explicit user state update / correction endpoint (e.g. from Review page or edit modal).
    Validates fields, updates MongoDB, and regenerates the document.
    """
    session = await SessionService.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found."
        )

    # Convert request payload to dict and drop None values
    raw_updates = payload.model_dump(exclude_unset=True)
    if not raw_updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field update must be provided."
        )

    # Validate updates
    cleaned_updates, errors = ValidationService.validate_and_clean_updates(raw_updates)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"errors": errors}
        )

    # Apply updates to database and re-generate document
    updated_state, doc_bundle = await StateService.apply_updates(session_id, cleaned_updates)

    return {
        "status": "ok",
        "message": "Structured state updated successfully.",
        "state": updated_state.to_clean_dict(),
        "field_statuses": updated_state.field_statuses,
        "completion_percentage": updated_state.get_completion_percentage(),
        "document": doc_bundle,
        "updated_at": updated_state.updated_at.isoformat()
    }
