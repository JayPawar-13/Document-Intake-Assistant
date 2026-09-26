import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["ok", "degraded"]
    assert "database" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_session_lifecycle(async_client: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    from app.config import settings
    monkeypatch.setattr(settings, "USE_MOCK_LLM", True)
    # 1. Create Session
    resp = await async_client.post("/api/sessions", json={"title": "Test Intake"})
    assert resp.status_code == 201
    s_data = resp.json()
    session_id = s_data["session_id"]
    assert session_id is not None
    assert "What is your full legal name?" in s_data["initial_message"]
    assert "state" in s_data
    assert "document" in s_data

    # 2. Get Session
    get_resp = await async_client.get(f"/api/sessions/{session_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["session_id"] == session_id

    # 3. Get Messages
    msg_resp = await async_client.get(f"/api/sessions/{session_id}/messages")
    assert msg_resp.status_code == 200
    msgs = msg_resp.json()
    assert len(msgs) == 1
    assert msgs[0]["role"] == "assistant"

    # 4. Send Message: Name
    post_msg = await async_client.post(
        f"/api/sessions/{session_id}/messages",
        json={"message": "My name is Jane Smith."}
    )
    assert post_msg.status_code == 200
    msg_data = post_msg.json()
    assert msg_data["state"]["full_name"] == "Jane Smith"
    assert "address" in msg_data["assistant_message"].lower()

    # 5. Send Message: Address
    addr_msg = await async_client.post(
        f"/api/sessions/{session_id}/messages",
        json={"message": "I live at 21 High Street, London."}
    )
    assert addr_msg.status_code == 200
    assert addr_msg.json()["state"]["home_address"] == "21 High Street, London"

    # 6. Send Message: Worldwide Assets
    ww_msg = await async_client.post(
        f"/api/sessions/{session_id}/messages",
        json={"message": "Yes, my document should cover assets worldwide."}
    )
    assert ww_msg.status_code == 200
    assert ww_msg.json()["state"]["covers_worldwide_assets"] is True

    # 7. Send Message: Children
    child_msg = await async_client.post(
        f"/api/sessions/{session_id}/messages",
        json={"message": "I have two children, Sarah and Michael."}
    )
    assert child_msg.status_code == 200
    assert child_msg.json()["state"]["has_children"] is True
    assert "Sarah" in child_msg.json()["state"]["children"]
    assert "Michael" in child_msg.json()["state"]["children"]

    # 8. Send Message: Executor
    exec_msg = await async_client.post(
        f"/api/sessions/{session_id}/messages",
        json={"message": "My brother James Smith should be my executor."}
    )
    assert exec_msg.status_code == 200
    assert exec_msg.json()["state"]["executor"]["name"] == "James Smith"
    assert exec_msg.json()["state"]["executor"]["relationship"] == "brother"

    # 9. Send Message: Specific Gift
    gift_msg = await async_client.post(
        f"/api/sessions/{session_id}/messages",
        json={"message": "I want my watch to go to Michael."}
    )
    assert gift_msg.status_code == 200
    assert any("watch" in g.lower() and "michael" in g.lower() for g in gift_msg.json()["state"]["specific_gifts"])

    # 10. Send Message: Additional Wishes
    wish_msg = await async_client.post(
        f"/api/sessions/{session_id}/messages",
        json={"message": "I would like my photographs to go to Sarah."}
    )
    assert wish_msg.status_code == 200
    assert "photographs to go to Sarah" in wish_msg.json()["state"]["additional_wishes"]

    # 11. Test State PATCH Update (Explicit correction via UI)
    patch_resp = await async_client.patch(
        f"/api/sessions/{session_id}/state",
        json={"executor": {"name": "Sarah Smith", "relationship": "sister"}}
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["state"]["executor"]["name"] == "Sarah Smith"
    assert patch_resp.json()["state"]["executor"]["relationship"] == "sister"

    # 12. Test Document Retrieval & Regeneration
    doc_resp = await async_client.get(f"/api/sessions/{session_id}/document")
    assert doc_resp.status_code == 200
    assert "Sarah Smith" in doc_resp.json()["document_html"]
    assert "DRAFT — FICTIONAL DOCUMENT" in doc_resp.json()["document_html"]

    regen_resp = await async_client.post(f"/api/sessions/{session_id}/document/regenerate")
    assert regen_resp.status_code == 200
    assert "Sarah Smith" in regen_resp.json()["document_html"]


@pytest.mark.asyncio
async def test_empty_message_400(async_client: AsyncClient):
    resp = await async_client.post("/api/sessions", json={})
    session_id = resp.json()["session_id"]
    bad_msg = await async_client.post(f"/api/sessions/{session_id}/messages", json={"message": "   "})
    assert bad_msg.status_code == 400


@pytest.mark.asyncio
async def test_invalid_session_404(async_client: AsyncClient):
    resp = await async_client.get("/api/sessions/non-existent-9999")
    assert resp.status_code == 404
