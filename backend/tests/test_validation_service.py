from app.services.validation_service import ValidationService


def test_validation_clean_valid_updates():
    raw = {
        "full_name": "  Jane Smith  ",
        "home_address": "21 High Street, London",
        "covers_worldwide_assets": "true",
        "has_children": True,
        "children": ["Sarah", "Michael"],
        "executor": {"name": "James Smith", "relationship": "Brother"},
        "specific_gifts": ["My watch to Michael"],
        "additional_wishes": "Photographs to Sarah"
    }
    cleaned, errors = ValidationService.validate_and_clean_updates(raw)
    assert len(errors) == 0
    assert cleaned["full_name"] == "Jane Smith"
    assert cleaned["covers_worldwide_assets"] is True
    assert cleaned["children"] == ["Sarah", "Michael"]
    assert cleaned["executor"]["relationship"] == "brother"


def test_validation_has_children_false_resets_children():
    raw = {
        "has_children": False,
        "children": ["Ghost Child"]
    }
    cleaned, errors = ValidationService.validate_and_clean_updates(raw)
    assert len(errors) == 0
    assert cleaned["has_children"] is False
    assert cleaned["children"] == []


def test_validation_invalid_data():
    raw = {
        "full_name": "A",  # too short
        "home_address": "X",  # too short
        "covers_worldwide_assets": "invalid_boolean_string"
    }
    cleaned, errors = ValidationService.validate_and_clean_updates(raw)
    assert len(errors) >= 2


def test_validation_gifts_and_wishes_separation():
    from app.models.gemini import GeminiExtractionResult, ExtractedInformation, GiftExtraction
    from app.models.state import StructuredState, SpecificGift
    
    state = StructuredState(
        session_id="sep-1",
        specific_gifts=[SpecificGift(item="watch", recipient_name="Rohit", description="My watch to my brother Rohit.")]
    )
    # Simulate extraction during additional_wishes question where LLM extracted a gift-like structure
    ext = GeminiExtractionResult(
        status="valid",
        extracted_information=ExtractedInformation(
            specific_gifts=[GiftExtraction(item="books", recipient_name="library", description="Donate my books to the local library.")],
            additional_wishes=[]
        )
    )
    val_updates, statuses, errors, _, _, _ = ValidationService.process_extraction(
        extraction=ext,
        current_state=state,
        last_target_field="additional_wishes"
    )
    # Must NOT pollute specific_gifts, must be in additional_wishes
    assert "additional_wishes" in val_updates
    assert "Donate my books" in val_updates["additional_wishes"]
    assert "specific_gifts" not in val_updates


def test_assistive_guidance_message():
    from app.services.interview_controller import InterviewController
    for field in ["full_name", "home_address", "covers_worldwide_assets", "has_children", "specific_gifts", "additional_wishes"]:
        msg = InterviewController.get_assistive_message(field)
        assert len(msg) > 20
        assert "need" in msg.lower() or "please" in msg.lower()
