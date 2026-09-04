"""
Tests for the 3 Execution Modes in AyuRaksha:
Mode 1: DIRECT_STATUTORY (ultra-fast statutory lookup)
Mode 2: GUIDED_RAG (standard regulatory compliance RAG)
Mode 3: MULTI_HOP_PLANNER (cross-border multi-pillar compliance planner)
"""
import pytest
from app.models.domain import ExecutionMode
from app.modules.orchestration import ModularOrchestrator
from app.agents.orchestrator import AyuRakshaOrchestrator


@pytest.fixture
def orchestrator():
    return AyuRakshaOrchestrator()


@pytest.fixture
def modular_orch():
    return ModularOrchestrator()


class TestExecutionModeRouting:
    """Verifies mode determination logic."""

    def test_direct_statutory_routing(self, modular_orch):
        q1 = "What is Section 3(p)?"
        q2 = "Text of Rule 158B"
        q3 = "Explain Section 2(1)(ja)"
        
        m1 = modular_orch.determine_execution_mode(q1, [], "IN")
        m2 = modular_orch.determine_execution_mode(q2, [], "IN")
        m3 = modular_orch.determine_execution_mode(q3, [], "IN")

        assert m1 == ExecutionMode.DIRECT_STATUTORY
        assert m2 == ExecutionMode.DIRECT_STATUTORY
        assert m3 == ExecutionMode.DIRECT_STATUTORY

    def test_multi_hop_cross_border_routing(self, modular_orch):
        q = "We developed an herbal extract from an Indian tribal region, want to patent it in India and export it to Germany."
        m = modular_orch.determine_execution_mode(q, [], "IN")
        assert m == ExecutionMode.MULTI_HOP_PLANNER

    def test_multi_hop_cross_border_jurisdiction_flag(self, modular_orch):
        q = "How do I file Form I for export?"
        m = modular_orch.determine_execution_mode(q, [], "CROSS_BORDER")
        assert m == ExecutionMode.MULTI_HOP_PLANNER

    def test_guided_rag_default_routing(self, modular_orch):
        q = "Can I patent an Ayurvedic churna combining Ashwagandha and Brahmi?"
        m = modular_orch.determine_execution_mode(q, [], "IN")
        assert m == ExecutionMode.GUIDED_RAG


@pytest.mark.asyncio
class TestExecutionModeExecution:
    """End-to-end execution of all 3 modes."""

    async def test_direct_statutory_fast_execution(self, orchestrator):
        ans = await orchestrator.process_query("What is Section 3(p)?")
        assert ans.execution_mode == ExecutionMode.DIRECT_STATUTORY
        assert "3(p)" in ans.direct_answer.lower() or "traditional knowledge" in ans.direct_answer.lower()
        assert len(ans.citations) >= 1
        assert ans.citations[0].section.lower() == "section 3(p)"

    async def test_multi_hop_planner_execution(self, orchestrator):
        query = "We developed a Withaferin extract from Indian tribal source, want to patent it and export it to Germany."
        ans = await orchestrator.process_query(query)
        assert ans.execution_mode == ExecutionMode.MULTI_HOP_PLANNER
        assert ans.evidence_pack is not None
        assert ans.evidence_pack.get("total_count", 0) > 0
        assert ans.cross_border_posture is not None

    async def test_guided_rag_execution(self, orchestrator):
        query = "Can I patent an Ayurvedic churna combining Ashwagandha and Brahmi?"
        ans = await orchestrator.process_query(query)
        assert ans.execution_mode == ExecutionMode.GUIDED_RAG
        assert len(ans.citations) >= 1
