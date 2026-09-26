from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from app.services.session_service import SessionService
from app.services.state_service import StateService
from app.models.api import CreateSessionRequest, CreateSessionResponse, SessionResponse

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("", response_model=CreateSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(payload: CreateSessionRequest = CreateSessionRequest()):
    """Create a new document intake session with initial state and welcome message"""
    try:
        session_data = await SessionService.create_session(title=payload.title or "Personal Wishes Document Intake")
        return CreateSessionResponse(
            session_id=session_data["session_id"],
            status=session_data["status"],
            initial_message=session_data["initial_message"],
            state=session_data["state"],
            document=session_data["document"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create intake session: {str(e)}"
        )


@router.get("", response_model=List[Dict[str, Any]])
async def list_sessions():
    """List recent document intake sessions"""
    return await SessionService.list_recent_sessions()


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Retrieve session details by ID"""
    session = await SessionService.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with ID '{session_id}' not found."
        )
    
    state = await StateService.get_state(session_id)
    completion = state.get_completion_percentage() if state else 0

    return SessionResponse(
        session_id=session["session_id"],
        status=session.get("status", "active"),
        title=session.get("title", "Personal Wishes Document"),
        created_at=session.get("created_at", ""),
        updated_at=session.get("updated_at", ""),
        completion_percentage=completion
    )
