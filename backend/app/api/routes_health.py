from fastapi import APIRouter
from app.database.mongodb import db_manager
from app.config import settings
from app.models.api import HealthResponse

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check():
    """Verify backend status and MongoDB connectivity"""
    db_connected = await db_manager.ping()
    db_status = "connected" if db_connected else "disconnected"
    overall_status = "ok" if db_connected else "degraded"

    return HealthResponse(
        status=overall_status,
        database=db_status,
        llm_provider="mock" if settings.USE_MOCK_LLM else settings.LLM_PROVIDER,
        version=settings.APP_VERSION
    )
