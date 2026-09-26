import pytest
from app.config import settings
from app.services.gemini_service import GeminiService
from app.models.state import StructuredState, FieldStatus
from app.services.validation_service import ValidationService
from app.services.interview_controller import InterviewController


@pytest.fixture
def gemini_service():
    if not settings.GEMINI_API_KEY:
        pytest.skip("GEMINI_API_KEY not configured. Skipping live Gemini API tests.")
    return GeminiService(api_key=settings.GEMINI_API_KEY, model=settings.GEMINI_MODEL)


@pytest.mark.asyncio
async def test_gemini_multi_field_extraction(gemini_service):
    """Section 13: Multi-field extraction in a single turn"""
    state = StructuredState()
    msg = "I'm Aarya Sharma, I live at 123 MG Road in Indore, I don't have children, and my brother Rohit Sharma will be my executor."
    
    result = await gemini_service.extract_information(user_message=msg, current_state=state)
    
    info = result.extracted_information
    assert info.full_name == "Aarya Sharma"
    assert "123 MG Road" in info.home_address and "Indore" in info.home_address
    assert info.has_children is False
    assert info.executor is not None
    assert info.executor.name == "Rohit Sharma"
    assert info.executor.relationship == "brother"

    # Validate updates through ValidationService
    val_updates, statuses, errors, needs_clar, _, _ = ValidationService.process_extraction(
        extraction=result,
        current_state=state,
        last_target_field="full_name"
    )
    assert val_updates["full_name"] == "Aarya Sharma"
    assert val_updates["has_children"] is False
    assert val_updates["executor"]["name"] == "Rohit Sharma"
    assert statuses["full_name"] == FieldStatus.CONFIRMED
    assert statuses["home_address"] == FieldStatus.CONFIRMED
    assert statuses["has_children"] == FieldStatus.CONFIRMED
    assert statuses["children"] == FieldStatus.NOT_APPLICABLE


@pytest.mark.asyncio
async def test_gemini_irrelevant_input_rejection(gemini_service):
    """Section 14 & 20: Irrelevant answers must be marked invalid and rejected"""
    state = StructuredState()
    msg = "My favorite color is blue."
    
    result = await gemini_service.extract_information(
        user_message=msg,
        current_state=state,
        last_question="Do you currently have any children?"
    )
    
    assert result.status == "invalid" or "has_children" in result.invalid_fields or result.clarification_needed
    # Validate that no fields are incorrectly updated
    val_updates, statuses, _, needs_clar, _, _ = ValidationService.process_extraction(
        extraction=result,
        current_state=state,
        last_target_field="has_children"
    )
    assert "has_children" not in val_updates
    assert statuses.get("has_children") != FieldStatus.CONFIRMED


@pytest.mark.asyncio
async def test_gemini_ambiguous_input_detection(gemini_service):
    """Section 15 & 17: Ambiguous answers must be flagged and not converted to True/False"""
    state = StructuredState()
    msg = "Maybe I'll have children in the future."
    
    result = await gemini_service.extract_information(
        user_message=msg,
        current_state=state,
        last_question="Do you currently have any children?"
    )
    
    assert result.status == "ambiguous" or "has_children" in result.ambiguous_fields or result.clarification_needed
    # Validate that has_children is marked AMBIGUOUS or rejected
    val_updates, statuses, _, needs_clar, _, _ = ValidationService.process_extraction(
        extraction=result,
        current_state=state,
        last_target_field="has_children"
    )
    assert "has_children" not in val_updates or statuses.get("has_children") == FieldStatus.AMBIGUOUS


@pytest.mark.asyncio
async def test_gemini_specific_gifts_extraction(gemini_service):
    """Section 37: Structured gifts extraction into item, recipient, relationship"""
    state = StructuredState()
    msg = "I want my watch to go to my brother Rohit and my laptop to my sister Priya."
    
    result = await gemini_service.extract_information(
        user_message=msg,
        current_state=state,
        last_question="Do you have any specific gifts you'd like to leave to particular people?"
    )
    
    gifts = result.extracted_information.specific_gifts
    assert len(gifts) >= 2
    gift_items = [g.item.lower() for g in gifts]
    assert any("watch" in item for item in gift_items)
    assert any("laptop" in item for item in gift_items)


@pytest.mark.asyncio
async def test_gemini_all_in_one_message(gemini_service):
    """Section 50: User answers everything in one message"""
    state = StructuredState()
    msg = (
        "I'm Aarya Sharma, I live at 123 MG Road in Indore, yes my assets worldwide should be covered, "
        "I don't have children, my brother Rohit Sharma is my executor, I want my watch to go to Rohit, "
        "and I want my books donated."
    )
    
    result = await gemini_service.extract_information(user_message=msg, current_state=state)
    val_updates, statuses, _, _, _, _ = ValidationService.process_extraction(
        extraction=result,
        current_state=state,
        last_target_field="full_name"
    )
    
    # Apply updates to test state
    state.full_name = val_updates.get("full_name")
    state.home_address = val_updates.get("home_address")
    state.covers_worldwide_assets = val_updates.get("covers_worldwide_assets")
    state.has_children = val_updates.get("has_children")
    if "children" in val_updates:
        state.children = val_updates["children"]
    if "executor" in val_updates:
        state.executor.name = val_updates["executor"].get("name")
        state.executor.relationship = val_updates["executor"].get("relationship")
    if "specific_gifts" in val_updates:
        state.specific_gifts = val_updates["specific_gifts"]
    if "additional_wishes" in val_updates:
        state.additional_wishes = val_updates["additional_wishes"]
    state.field_statuses.update(statuses)

    # Calculate missing fields
    missing = state.get_missing_fields()
    # The interview should be complete or nearly complete (only missing fields, if any, are queried)
    assert "full_name" not in missing
    assert "home_address" not in missing
    assert "covers_worldwide_assets" not in missing
    assert "has_children" not in missing
    assert "children" not in missing
