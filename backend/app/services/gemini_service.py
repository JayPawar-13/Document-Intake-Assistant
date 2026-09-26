import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from google import genai
from google.genai import types

from app.config import settings
from app.models.gemini import GeminiExtractionResult, ExtractedInformation, NextAction, UserIntent
from app.models.state import StructuredState

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """You are the information extraction component of the Document Intake Assistant.

Your job is to understand the user's latest message and extract every piece of relevant information explicitly provided by the user.

You are NOT responsible for deciding the next interview question.
The backend controls the interview.

RULES:
1. Extract every relevant field mentioned in the user's message.
2. Do not extract only the field related to the previous question.
3. If the user provides multiple pieces of information, extract all of them.
4. Never invent information.
5. Never infer information that is not reasonably stated.
6. Do not convert vague statements into confirmed facts.
7. Detect ambiguity. If the user is unsure, undecided, or says "maybe", "not sure", or "someday", mark the field as ambiguous in ambiguous_fields and set clarification_needed=true.
8. Detect contradictions with the existing structured state. If the user states something directly contradictory to already confirmed state without an explicit correction cue (e.g. was has_children=false, now mentions children), add to contradictory_fields and set clarification_needed=true.
9. Detect explicit corrections. If the user says "actually", "make that", "instead of", "change to", mark is_explicit_correction=true.
10. Preserve the user's actual information accurately (e.g., complete addresses, exact gift descriptions).
11. If the user explicitly says no, represent the appropriate field as false or an empty list where appropriate (e.g., has_children=false, has_no_gifts=true).
12. If the user says they do not know or refuse to answer, do not invent an answer. Mark user_intent="dont_know" or "refusal".
13. If the user gives irrelevant information (e.g. "I like playing cricket" when asked for address), mark status="invalid", add field to invalid_fields, set user_intent="irrelevant", and do NOT assign the value to any field.
14. Return only information supported by the user message.
15. The backend will validate all extracted information.
16. Never decide that the interview is complete.
17. CRITICAL DISTINCTION: SPECIFIC GIFTS vs ADDITIONAL WISHES
    - "specific_gifts": ONLY for specific, individual tangible items or property bequeathed to an explicitly named, individual beneficiary (e.g. "my watch to my brother Rohit", "my laptop to Priya").
    - "additional_wishes": General desires, charitable donations, donating collections or books (e.g. "donate my books to the library", "clothes to charity"), funeral preferences (e.g. "cremation", "scatter ashes"), family photograph preservation, or ANY requests/wishes provided when the user is asked about additional wishes!
    - If the user is currently answering the additional wishes question (or mentions general wishes/donations), extract these into "additional_wishes", NEVER into "specific_gifts".
    - Specific gifts and additional wishes are two strictly separate categories.
"""


class GeminiService:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self._client: Optional[genai.Client] = None

    def get_client(self) -> genai.Client:
        if self._client is None:
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY is not configured.")
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    async def extract_information(
        self,
        user_message: str,
        current_state: StructuredState,
        last_question: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> GeminiExtractionResult:
        """
        Calls Gemini using structured outputs (Pydantic schema) to extract
        information, detect ambiguity, detect contradictions, and classify intent.
        """
        client = self.get_client()

        # Build context payload
        state_context = {
            "current_structured_state": current_state.to_clean_dict(),
            "field_statuses": current_state.field_statuses,
            "last_question_asked": last_question or "None",
            "recent_conversation": [
                {"role": m.get("role"), "content": m.get("content")}
                for m in (conversation_history or [])[-6:]
            ]
        }

        user_prompt = f"""CONTEXT:
{json.dumps(state_context, indent=2)}

LATEST USER MESSAGE TO ANALYZE:
"{user_message}"

Extract all stated information matching the schema according to the system rules."""

        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                def _call_extraction():
                    return client.models.generate_content(
                        model=self.model,
                        contents=user_prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=EXTRACTION_SYSTEM_PROMPT,
                            response_mime_type="application/json",
                            response_schema=GeminiExtractionResult,
                            temperature=0.0,
                        )
                    )

                response = await asyncio.wait_for(asyncio.to_thread(_call_extraction), timeout=10.0)
                result_json = response.text
                logger.info("Gemini Extraction Raw Response: %s", result_json)
                parsed_result = GeminiExtractionResult.model_validate_json(result_json)
                return parsed_result

            except Exception as e:
                err_str = str(e)
                if attempt < max_retries and any(code in err_str for code in ["429", "503", "RESOURCE_EXHAUSTED", "UNAVAILABLE"]):
                    wait_sec = 2 * (attempt + 1)
                    logger.warning("Gemini API rate limit or service unavailable. Retrying in %ds... (attempt %d/%d)", wait_sec, attempt + 1, max_retries)
                    await asyncio.sleep(wait_sec)
                    continue
                logger.error("Error calling Gemini extraction API: %s", str(e))
                raise e

    async def generate_friendly_response(
        self,
        next_action: NextAction,
        next_field: Optional[str],
        fallback_question: str,
        acknowledged_fields: Dict[str, Any],
        current_state: StructuredState,
        user_message: str,
        assistive_guidance: Optional[str] = None,
        is_invalid_input: bool = False
    ) -> str:
        """
        Separated Gemini call to generate a polite, conversational phrasing
        for the backend's deterministic decision.
        If it fails, the fallback_question is safely returned.
        """
        if not self.api_key:
            return fallback_question

        client = self.get_client()

        prompt = f"""You are the friendly AI assistant for Document Intake Assistant.
The backend interview controller has made the following deterministic decision:

Action: {next_action.value}
Target Field: {next_field or "None"}
Standard Question / Message: "{fallback_question}"
User's latest message: "{user_message}"
Newly recorded and confirmed fields from this turn: {json.dumps(acknowledged_fields, default=str)}
Assistive Guidance / What is needed: {assistive_guidance or "None"}
Is Invalid or Irrelevant Input: {is_invalid_input}

YOUR TASK:
Formulate a warm, natural, professional 1-2 sentence response.
- If the user gave an off-topic, invalid, or unclear answer (Is Invalid or Irrelevant Input is True):
  1) Acknowledge what they said kindly without being dismissive or robotic,
  2) Clearly state what specific information is needed for this step,
  3) Help and assist the user by giving clear guidance or an example of how to answer (using the Assistive Guidance provided above).
- If new information was just confirmed (e.g. name or address), acknowledge it briefly and politely, then ask the next required question.
- If clarifying ambiguity, present the clarification clearly and warmly with helpful guidance.
- Keep it concise, helpful, and empathetic. No legal jargon. Do not invent questions beyond the Target Field.

Return ONLY the plain response text with no extra commentary or quotes."""

        try:
            def _call_response():
                return client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=180,
                    )
                )

            response = await asyncio.wait_for(asyncio.to_thread(_call_response), timeout=8.0)
            text = response.text.strip()
            return text if text else fallback_question
        except Exception as e:
            logger.warning("Gemini response phrasing failed, using fallback: %s", str(e))
            return fallback_question
