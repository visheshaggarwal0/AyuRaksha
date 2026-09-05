import pytest
from app.modules.orchestration import orchestration_module
from app.models.domain import ExecutionMode
from app.agents.orchestrator import AyuRakshaOrchestrator
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_greeting_routing_and_response():
    """Verify that greetings return CONVERSATIONAL_GREETING with 0 citations and 6 category starter chips."""
    for greeting in ["Hy there.", "hi", "Hello", "Namaste!", "What can you do?"]:
        resp = await orchestration_module.process_query(query=greeting, jurisdiction="IN")
        assert resp.execution_mode == ExecutionMode.CONVERSATIONAL_GREETING
        assert resp.intent_type == "GREETING"
        assert len(resp.citations) == 0
        assert resp.confidence.level.value == "HIGH"
        assert not resp.safe_abstention
        assert len(resp.clarification_chips) >= 6
        assert "IP-SAKTI Sahayak" in resp.direct_answer

@pytest.mark.asyncio
async def test_underspecified_formulation_intake():
    """Verify that underspecified formulation questions trigger CLASSIFICATION_INTAKE."""
    queries = [
        "Can I patent my pain oil?",
        "I want to sell an herbal cream",
        "Classify my formulation"
    ]
    for q in queries:
        resp = await orchestration_module.process_query(query=q, jurisdiction="IN")
        assert resp.execution_mode == ExecutionMode.CLASSIFICATION_INTAKE
        assert resp.intent_type == "CLASSIFICATION_INTAKE"
        assert len(resp.citations) == 0
        assert len(resp.clarification_chips) >= 3
        assert "First-Schedule" in resp.direct_answer

def test_api_chat_query_greeting_live():
    """Verify POST /api/v1/chat/query returns structured greeting for 'Hy there.'."""
    payload = {"query": "Hy there.", "jurisdiction": "IN"}
    resp = client.post("/api/v1/chat/query", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["intent_type"] == "GREETING"
    assert data["execution_mode"] == "CONVERSATIONAL_GREETING"
    assert len(data["citations"]) == 0
    assert len(data["clarification_chips"]) >= 6
    assert "IP-SAKTI Sahayak" in data["direct_answer"]
