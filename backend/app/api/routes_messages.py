import logging
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional

from app.models.api import SendMessageRequest, SendMessageResponse
from app.models.conversation import MessageRole
from app.models.gemini import NextAction
from app.models.state import FieldStatus
from app.services.session_service import SessionService
from app.services.conversation_service import ConversationService
from app.services.state_service import StateService
from app.services.validation_service import ValidationService
from app.services.contradiction_service import ContradictionService
from app.services.interview_controller import InterviewController, QUESTION_MAP
from app.services.document_service import DocumentService
from app.services.llm_service import get_llm_service
from app.services.gemini_service import GeminiService
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/sessions/{session_id}/messages", tags=["messages"])


@router.get("", response_model=List[Dict[str, Any]])
async def get_messages(session_id: str):
    """Retrieve full conversation history for a session"""
    session = await SessionService.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found."
        )
    return await ConversationService.get_messages(session_id)


@router.post("", response_model=SendMessageResponse)
async def send_message(session_id: str, payload: SendMessageRequest):
    """
    Main conversational intake endpoint implementing the architecture:
    User Message -> Load Session & State -> Gemini Extractor -> Pydantic Validation ->
    Business Validation -> Contradiction / Ambiguity Check -> MongoDB Update ->
    Interview Controller (Find Next Required Field) -> Natural Language Phrasing -> Frontend
    """
    cleaned_user_text = payload.message.strip()
    if not cleaned_user_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty."
        )

    # 1. Verify session existence and load state
    session = await SessionService.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found."
        )

    history = await ConversationService.get_messages(session_id)
    current_state = await StateService.get_state(session_id)
    if not current_state:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Structured state record is missing for this session."
        )

    # Identify the last assistant message and target field before this turn
    last_assistant_msg = ""
    for m in reversed(history):
        if m.get("role") == "assistant":
            last_assistant_msg = m.get("content", "")
            break

    # Determine current target field based on state before user message
    pre_action, current_target_field, _ = InterviewController.determine_next_action_and_field(current_state)

    logger.info("=== INTAKE TURN START ===")
    logger.info("SESSION ID: %s", session_id)
    logger.info("CURRENT FIELD: %s", current_target_field)
    logger.info("USER MESSAGE: %s", cleaned_user_text)
    logger.info("CURRENT STRUCTURED STATE: %s", current_state.to_clean_dict())

    # 2. Persist user message to conversation history
    await ConversationService.add_message(
        session_id=session_id,
        role=MessageRole.USER,
        content=cleaned_user_text
    )

    # 3. Call Gemini Extractor (or fallback)
    llm = get_llm_service()
    extraction_result = await llm.process_message(
        message=cleaned_user_text,
        conversation_history=history,
        structured_state=current_state,
        last_question=last_assistant_msg
    )
    logger.info("GEMINI EXTRACTION: %s", extraction_result.model_dump())

    # 4. Business Rule Validation
    validated_updates, status_updates, val_errors, needs_clarification, clarification_question, quick_replies = (
        ValidationService.process_extraction(
            extraction=extraction_result,
            current_state=current_state,
            last_target_field=current_target_field
        )
    )
    logger.info("VALIDATION RESULT: updates=%s, errors=%s", validated_updates, val_errors)

    # 5. Contradiction & Ambiguity Check
    has_contradiction, contra_q, contra_replies, approved_updates = (
        ContradictionService.check_for_contradictions(
            current_state=current_state,
            candidate_updates=validated_updates,
            user_message=cleaned_user_text,
            is_gemini_correction=extraction_result.is_explicit_correction
        )
    )

    active_clarification_field = None
    if has_contradiction:
        contra_field = None
        if "has_children" in validated_updates or "children" in validated_updates:
            contra_field = "has_children"
        elif "executor" in validated_updates:
            contra_field = "executor.name"
        elif extraction_result.contradictory_fields:
            contra_field = extraction_result.contradictory_fields[0]
        else:
            contra_field = current_target_field

        logger.info("CONTRADICTION DETECTED on field '%s'", contra_field)
        needs_clarification = True
        clarification_question = contra_q
        quick_replies = contra_replies
        active_clarification_field = contra_field
        if contra_field:
            status_updates[contra_field] = FieldStatus.CONTRADICTORY
        # Apply only non-conflicting updates
        candidate_to_apply = approved_updates
    elif needs_clarification:
        logger.info("AMBIGUITY DETECTED: %s", clarification_question)
        if extraction_result.ambiguous_fields:
            active_clarification_field = extraction_result.ambiguous_fields[0]
        candidate_to_apply = validated_updates
    else:
        candidate_to_apply = validated_updates

    # 6. Apply Valid Updates to MongoDB
    if candidate_to_apply or status_updates:
        current_state, doc_bundle = await StateService.apply_updates(
            session_id=session_id,
            validated_updates=candidate_to_apply,
            status_updates=status_updates
        )
    else:
        doc_bundle = DocumentService.generate_document_bundle(current_state)

    logger.info("UPDATED STATE: %s", current_state.to_clean_dict())

    is_wrong_input = (
        extraction_result.user_intent.value == "irrelevant"
        or extraction_result.status == "invalid"
        or (bool(val_errors) and not candidate_to_apply and not extraction_result.is_explicit_correction)
    )
    if is_wrong_input and current_target_field:
        active_clarification_field = current_target_field

    # 7. Calculate Missing Fields & Determine Next Action
    next_action, next_field, fallback_msg = InterviewController.determine_next_action_and_field(
        state=current_state,
        active_clarification_field=active_clarification_field
    )
    if is_wrong_input:
        next_action = NextAction.ASK_CLARIFICATION
        next_field = current_target_field or next_field

    missing_fields = current_state.get_missing_fields()
    logger.info("MISSING FIELDS: %s", missing_fields)
    logger.info("NEXT ACTION: %s, NEXT FIELD: %s", next_action.value, next_field)

    # 8. Generate Natural Language Phrasing
    final_assistant_message: str = ""
    assistive_guidance = None
    if next_field:
        assistive_guidance = InterviewController.get_assistive_message(next_field)

    if has_contradiction:
        final_assistant_message = contra_q
    elif needs_clarification and clarification_question:
        final_assistant_message = clarification_question
    elif is_wrong_input:
        # Prompt Gemini with assistive guidance to explain what is needed and help user
        if not settings.USE_MOCK_LLM and settings.GEMINI_API_KEY:
            try:
                gemini_inst = GeminiService()
                final_assistant_message = await gemini_inst.generate_friendly_response(
                    next_action=NextAction.ASK_CLARIFICATION,
                    next_field=next_field,
                    fallback_question=fallback_msg,
                    acknowledged_fields={},
                    current_state=current_state,
                    user_message=cleaned_user_text,
                    assistive_guidance=assistive_guidance,
                    is_invalid_input=True
                )
            except Exception as e:
                logger.warning("Error generating assistive clarification from Gemini: %s", e)
                final_assistant_message = assistive_guidance or fallback_msg
        else:
            final_assistant_message = assistive_guidance or fallback_msg
    elif next_action == NextAction.INTERVIEW_COMPLETE:
        final_assistant_message = fallback_msg
    else:
        # Generate friendly response using Gemini (or fallback question map)
        if not settings.USE_MOCK_LLM and settings.GEMINI_API_KEY:
            try:
                gemini_inst = GeminiService()
                final_assistant_message = await gemini_inst.generate_friendly_response(
                    next_action=next_action,
                    next_field=next_field,
                    fallback_question=fallback_msg,
                    acknowledged_fields=candidate_to_apply,
                    current_state=current_state,
                    user_message=cleaned_user_text,
                    assistive_guidance=assistive_guidance,
                    is_invalid_input=False
                )
            except Exception as e:
                logger.warning("Error generating friendly response from Gemini: %s", e)
                final_assistant_message = fallback_msg
        else:
            final_assistant_message = extraction_result.assistant_message or fallback_msg

    # Supply default quick replies for standard fields if not already provided
    if not quick_replies:
        if next_field == "covers_worldwide_assets":
            quick_replies = ["Yes, cover assets worldwide", "No, domestic assets only"]
        elif next_field == "has_children":
            quick_replies = ["No, I do not have children", "Yes, I have children"]
        elif next_field == "specific_gifts":
            quick_replies = ["No specific gifts"]
        elif next_field == "additional_wishes":
            quick_replies = ["No additional wishes"]
        elif next_action == NextAction.INTERVIEW_COMPLETE:
            quick_replies = ["Review My Information", "Preview Document"]

    logger.info("FINAL ASSISTANT MESSAGE: %s", final_assistant_message)
    logger.info("=== INTAKE TURN END ===")

    # 9. Persist Assistant Message to Conversation History
    await ConversationService.add_message(
        session_id=session_id,
        role=MessageRole.ASSISTANT,
        content=final_assistant_message,
        quick_replies=quick_replies,
        metadata={
            "next_action": next_action.value,
            "next_field": next_field,
            "needs_clarification": needs_clarification or has_contradiction,
            "is_correction": extraction_result.is_explicit_correction,
            "applied_updates": list(candidate_to_apply.keys())
        }
    )

    progress = InterviewController.calculate_progress(current_state)

    # 10. Return SendMessageResponse (Section 52 + Backward-compatible fields)
    field_status_dict = {k: v.value if hasattr(v, "value") else str(v) for k, v in current_state.field_statuses.items()}

    return SendMessageResponse(
        # Section 52 schema
        message=final_assistant_message,
        structured_state=current_state.to_clean_dict(),
        field_status=field_status_dict,
        next_action=next_action.value,
        next_field=next_field,
        progress=progress,

        # Backward-compatible fields
        assistant_message=final_assistant_message,
        quick_replies=quick_replies,
        state=current_state.to_clean_dict(),
        document=doc_bundle,
        needs_clarification=needs_clarification or has_contradiction,
        clarification_question=clarification_question if (needs_clarification or has_contradiction) else None,
        is_correction=extraction_result.is_explicit_correction
    )


@router.post("/reset", status_code=status.HTTP_200_OK)
async def reset_conversation(session_id: str):
    """Reset conversation history while preserving session"""
    session = await SessionService.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found."
        )
    await ConversationService.clear_messages(session_id)
    return {"status": "ok", "message": "Conversation history reset."}
