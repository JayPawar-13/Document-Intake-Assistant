import pytest
from app.models.state import StructuredState, Executor
from app.services.mock_llm_service import MockLLMService


@pytest.mark.asyncio
async def test_mock_llm_name_extraction():
    state = StructuredState(session_id="llm-1")
    history = [{"role": "assistant", "content": "What is your full legal name?"}]
    result = await MockLLMService.process_message("My name is Jane Smith.", history, state)

    assert result.updates.get("full_name") == "Jane Smith"
    assert not result.needs_clarification
    assert "address" in result.assistant_message.lower()


@pytest.mark.asyncio
async def test_mock_llm_multi_field_extraction():
    state = StructuredState(session_id="llm-2")
    history = [{"role": "assistant", "content": "Hi! Let's get started."}]
    # Multi-field answer: Name + Executor + Relationship
    msg = "My brother James Smith should be my executor. My name is Jane Smith."
    result = await MockLLMService.process_message(msg, history, state)

    assert result.updates.get("full_name") == "Jane Smith"
    assert result.updates.get("executor", {}).get("name") == "James Smith"
    assert result.updates.get("executor", {}).get("relationship") == "brother"


@pytest.mark.asyncio
async def test_mock_llm_ambiguous_response():
    state = StructuredState(session_id="llm-3")
    history = [{"role": "assistant", "content": "Do you have any children?"}]
    result = await MockLLMService.process_message("I'm not sure.", history, state)

    assert result.needs_clarification is True
    assert "confirm" in result.clarification_question.lower()
    assert len(result.suggested_quick_replies) >= 2


@pytest.mark.asyncio
async def test_mock_llm_correction_response():
    state = StructuredState(
        session_id="llm-4",
        full_name="Jane Smith",
        executor=Executor(name="James Smith", relationship="brother")
    )
    history = [
        {"role": "assistant", "content": "Are there any specific gifts?"}
    ]
    msg = "Actually, Sarah should be my executor instead of James."
    result = await MockLLMService.process_message(msg, history, state)

    assert result.is_correction is True
    assert result.updates.get("executor", {}).get("name") == "Sarah"
