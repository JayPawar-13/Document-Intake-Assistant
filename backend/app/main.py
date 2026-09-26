import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database.mongodb import db_manager
from app.api.routes_sessions import router as sessions_router
from app.api.routes_messages import router as messages_router
from app.api.routes_state import router as state_router
from app.api.routes_document import router as document_router
from app.api.routes_health import router as health_router
from app.utils.errors import AppException, app_exception_handler, general_exception_handler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for MongoDB connection"""
    logger.info("Initializing Document Intake Assistant Backend...")
    try:
        await db_manager.connect()
        logger.info("Connected to MongoDB successfully.")
    except Exception as e:
        logger.error(f"Could not connect to MongoDB on startup: {e}")
        logger.warning("Backend started in degraded database mode. Start MongoDB to enable persistence.")
    
    yield

    logger.info("Shutting down Document Intake Assistant Backend...")
    await db_manager.disconnect()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Backend API for Document Intake Assistant — Conversational interview, structured state management, validation, and document generation.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(AppException, app_exception_handler)

# Include API routers
app.include_router(health_router)
app.include_router(sessions_router)
app.include_router(messages_router)
app.include_router(state_router)
app.include_router(document_router)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
