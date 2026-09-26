import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from app.config import settings
from app.models.gemini import GeminiExtractionResult
from app.models.state import StructuredState
from app.services.gemini_service import GeminiService
from app.services.mock_llm_service import MockLLMService

logger = logging.getLogger(__name__)


class BaseLLMService(ABC):
    @abstractmethod
    async def process_message(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        structured_state: StructuredState
    ) -> GeminiExtractionResult:
        pass


class OpenAIService(BaseLLMService):
    """Legacy/secondary OpenAI service wrapper"""
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model

    async def process_message(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        structured_state: StructuredState
    ) -> GeminiExtractionResult:
        return await MockLLMService.process_message(message, conversation_history, structured_state)


class LLMServiceWrapper(BaseLLMService):
    """
    Unified LLM service layer.
    Routes to official Google GenAI Gemini SDK when configured with GEMINI_API_KEY.
    Falls back gracefully to MockLLMService on error or when in mock mode.
    """

    def __init__(self):
        self._gemini = None

    @property
    def gemini(self) -> Optional[GeminiService]:
        if settings.GEMINI_API_KEY:
            if self._gemini is None:
                self._gemini = GeminiService(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)
            return self._gemini
        return None

    async def process_message(
        self,
        message: str,
        conversation_history: List[Dict[str, Any]],
        structured_state: StructuredState,
        last_question: Optional[str] = None
    ) -> GeminiExtractionResult:
        # Check if real Gemini API should be used
        if not settings.USE_MOCK_LLM and settings.GEMINI_API_KEY and self.gemini:
            try:
                logger.info("Routing extraction to Google Gemini API (model: %s)", settings.GEMINI_MODEL)
                return await self.gemini.extract_information(
                    user_message=message,
                    current_state=structured_state,
                    last_question=last_question,
                    conversation_history=conversation_history
                )
            except Exception as e:
                logger.error("Gemini API call failed (%s). Falling back to MockLLMService.", str(e))
                # Graceful fallback: do not crash conversation
                return await MockLLMService.process_message(
                    message=message,
                    conversation_history=conversation_history,
                    structured_state=structured_state,
                    last_question=last_question
                )
        else:
            return await MockLLMService.process_message(
                message=message,
                conversation_history=conversation_history,
                structured_state=structured_state,
                last_question=last_question
            )


_llm_instance = None


def get_llm_service() -> LLMServiceWrapper:
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMServiceWrapper()
    return _llm_instance
