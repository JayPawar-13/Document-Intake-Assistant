from app.models.state import StructuredState, Executor
from app.services.contradiction_service import ContradictionService


def test_contradiction_detected_children_conflict():
    state = StructuredState(
        session_id="contra-1",
        has_children=False,
        children=[]
    )
    candidate = {"children": ["Sarah", "Michael"]}
    has_c, q, replies, filtered = ContradictionService.check_for_contradictions(
        current_state=state,
        candidate_updates=candidate,
        user_message="My children Sarah and Michael should be included"
    )

    assert has_c is True
    assert "Earlier you indicated that you do not have children" in q
    assert len(replies) == 2
    assert "children" not in filtered  # Conflicting update filtered out


def test_explicit_correction_bypasses_contradiction():
    state = StructuredState(
        session_id="contra-2",
        executor=Executor(name="James Smith", relationship="brother")
    )
    candidate = {"executor": {"name": "Sarah", "relationship": "sister"}}
    has_c, q, replies, filtered = ContradictionService.check_for_contradictions(
        current_state=state,
        candidate_updates=candidate,
        user_message="Actually, Sarah should be my executor instead of James."
    )

    assert has_c is False
    assert q is None
    assert filtered["executor"]["name"] == "Sarah"
