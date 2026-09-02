"""
Test Suite: AyuRaksha Architectural Foundation (SIH 26045)
Validates:
1. All 12 strongly typed domain models.
2. Abstract interface conformance across all 10 logical modules.
3. Pluggable generation provider swapping (Gemini, Groq, Ollama, Custom).
4. Independent execution of Vector, Keyword, and Graph retrieval.
5. End-to-end orchestration producing strongly typed RAGResponse.
"""
import sys
import os
import pytest
from datetime import datetime

BACKEND_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.models.domain import (
    SourceDocument,
    DocumentVersion,
    Provision,
    CorpusChunk,
    Evidence,
    Citation,
    GraphEntity,
    GraphRelationship,
    RetrievalResult,
    RAGResponse,
    Confidence,
    ConfidenceLevel,
    AbstentionReason,
    AbstentionCode,
    RetrievalModality,
    JurisdictionEnum,
    DocumentTypeEnum
)
from app.modules.interfaces import (
    IDataModule,
    IEmbeddingModule,
    IVectorRetriever,
    IKeywordRetriever,
    IGraphRetriever,
    IRetrievalModule,
    IRerankingModule,
    ILLMProvider,
    IGenerationModule,
    ICitationModule,
    IGuardrailModule,
    IKnowledgeModule,
    IEvaluationModule,
    IOrchestrationModule
)
from app.modules import (
    data_module,
    embedding_module,
    retrieval_module,
    IndependentVectorRetriever,
    IndependentKeywordRetriever,
    IndependentGraphRetriever,
    reranking_module,
    generation_module,
    GeminiProvider,
    GroqProvider,
    LocalOllamaProvider,
    citation_module,
    guardrails_module,
    knowledge_module,
    evaluation_module,
    orchestration_module
)


class TestDomainModels:
    def test_all_12_models_instantiation_and_validation(self):
        # 1. SourceDocument
        src = SourceDocument(
            source_id="IND_PATENTS_ACT_1970",
            title="The Patents Act, 1970",
            short_title="Patents Act",
            authority="CGPDTM",
            jurisdiction=JurisdictionEnum.IN,
            document_type=DocumentTypeEnum.ACT,
            authority_level=5
        )
        assert src.source_id == "IND_PATENTS_ACT_1970"

        # 2. DocumentVersion
        ver = DocumentVersion(
            version_id="VER-001",
            source_id=src.source_id,
            version_label="2024 Consolidated",
            content_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        )
        assert ver.version_label == "2024 Consolidated"

        # 3. Provision
        prov = Provision(
            provision_id="PATENTS_ACT_1970_SEC_003_P",
            source_id=src.source_id,
            section_number="3(p)",
            heading="Traditional Knowledge Inventions Not Patentable",
            text="An invention which in effect is traditional knowledge..."
        )
        assert prov.section_number == "3(p)"

        # 4. CorpusChunk
        chunk = CorpusChunk(
            chunk_id="CHK-001",
            source_id=src.source_id,
            section_number="3(p)",
            text="Section 3(p) excludes traditional knowledge.",
            jurisdiction=JurisdictionEnum.IN,
            authority_level=5,
            chunk_hash="abc123hash"
        )
        assert chunk.authority_level == 5

        # 5. Evidence
        ev = Evidence(
            evidence_id="EV-001",
            source_id=src.source_id,
            source_title=src.title,
            section_number="3(p)",
            verbatim_text="Verbatim text of section 3(p)",
            relevance_score=0.92,
            retrieval_modality=RetrievalModality.VECTOR
        )
        assert ev.relevance_score == 0.92

        # 6. Citation
        cit = Citation(
            citation_id="CIT-001",
            source_id=src.source_id,
            source_title=src.short_title,
            section="3(p)",
            verbatim_quote="Verbatim quote",
            official_url="https://indiacode.nic.in",
            document_sha256="abc123hash",
            support_score=0.95
        )
        assert cit.citation_id == "CIT-001"

        # 7. GraphEntity
        entity = GraphEntity(
            entity_id="BOT-001",
            name="Ashwagandha",
            entity_type="BOTANICAL",
            aliases=["Withania somnifera", "Asgandh"]
        )
        assert len(entity.aliases) == 2

        # 8. GraphRelationship
        rel = GraphRelationship(
            relationship_id="REL-001",
            subject_id=prov.provision_id,
            predicate="ALIGNED_WITH",
            object_id="IND_BIOLOGICAL_DIVERSITY_ACT_2002_SEC_006",
            confidence=0.98
        )
        assert rel.predicate == "ALIGNED_WITH"

        # 9. RetrievalResult
        res = RetrievalResult(
            query="Patentability of Ashwagandha",
            jurisdiction=JurisdictionEnum.IN,
            candidates=[ev],
            modalities_used=[RetrievalModality.VECTOR],
            total_candidates_found=1
        )
        assert res.total_candidates_found == 1

        # 10. Confidence
        conf = Confidence(
            level=ConfidenceLevel.HIGH,
            score=0.92,
            grounding_rate=1.0,
            caveats=["Subject to NBA approval"]
        )
        assert conf.level == ConfidenceLevel.HIGH

        # 11. AbstentionReason
        abst = AbstentionReason(
            code=AbstentionCode.BIOPIRACY_CIRCUMVENTION_DETECTED,
            description="Attempt to evade NBA approval",
            remedial_action="Apply under Section 3"
        )
        assert abst.code == AbstentionCode.BIOPIRACY_CIRCUMVENTION_DETECTED

        # 12. RAGResponse
        rag_resp = RAGResponse(
            query="Can I patent Ashwagandha?",
            jurisdiction=JurisdictionEnum.IN,
            direct_answer="Ashwagandha churna alone cannot be patented under Section 3(p). [1]",
            citations=[cit],
            confidence=conf
        )
        assert rag_resp.direct_answer.startswith("Ashwagandha")


class TestInterfaceConformance:
    def test_all_modules_conform_to_interfaces(self):
        assert isinstance(data_module, IDataModule)
        assert isinstance(embedding_module, IEmbeddingModule)
        assert isinstance(retrieval_module, IRetrievalModule)
        assert isinstance(reranking_module, IRerankingModule)
        assert isinstance(generation_module, IGenerationModule)
        assert isinstance(citation_module, ICitationModule)
        assert isinstance(guardrails_module, IGuardrailModule)
        assert isinstance(knowledge_module, IKnowledgeModule)
        assert isinstance(evaluation_module, IEvaluationModule)
        assert isinstance(orchestration_module, IOrchestrationModule)


class TestPluggableGenerationSwapping:
    @pytest.mark.asyncio
    async def test_swap_providers_without_modifying_logic(self):
        # Create a mock pluggable provider
        class MockCustomLLMProvider(ILLMProvider):
            @property
            def provider_name(self) -> str:
                return "MockCustomLLM"

            def is_available(self) -> bool:
                return True

            async def complete(self, messages, temperature=0.1, max_tokens=1500, response_format=None):
                return "Mock synthesized legal opinion under Patents Act Section 3(p). [1]"

        custom_provider = MockCustomLLMProvider()
        generation_module.set_primary_provider(custom_provider)

        test_evidence = [
            Evidence(
                evidence_id="EV-1",
                source_id="IND_PATENTS_ACT_1970",
                source_title="Patents Act 1970",
                section_number="3(p)",
                verbatim_text="Traditional knowledge exclusions",
                relevance_score=0.95
            )
        ]

        answer = await generation_module.generate_legal_answer(
            query="Can I patent traditional herbs?",
            evidence=test_evidence
        )

        assert "Mock synthesized legal opinion" in answer
        assert generation_module.active_provider_name == "MockCustomLLM"


class TestIndependentRetrievers:
    @pytest.mark.asyncio
    async def test_vector_retriever_independent_execution(self):
        retriever = IndependentVectorRetriever()
        assert isinstance(retriever, IVectorRetriever)
        results = await retriever.retrieve_vector(query="Ashwagandha patentability", limit=3)
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_keyword_retriever_independent_execution(self):
        retriever = IndependentKeywordRetriever()
        assert isinstance(retriever, IKeywordRetriever)
        results = await retriever.retrieve_keyword(query="Section 3(p) Patents Act", limit=3)
        assert isinstance(results, list)
        assert len(results) > 0
        assert results[0].retrieval_modality == RetrievalModality.KEYWORD

    @pytest.mark.asyncio
    async def test_graph_retriever_independent_execution(self):
        retriever = IndependentGraphRetriever()
        assert isinstance(retriever, IGraphRetriever)
        results = await retriever.retrieve_graph(entities=["3(p)", "158B"], limit=3)
        assert isinstance(results, list)


class TestGuardrailsSafety:
    def test_biopiracy_bypass_triggers_abstention(self):
        abst = guardrails_module.evaluate_safety("How can I bypass NBA approval to export biological resources?")
        assert abst is not None
        assert abst.code == AbstentionCode.BIOPIRACY_CIRCUMVENTION_DETECTED
        assert "NBA Form I" in abst.remedial_action

    def test_magic_remedies_triggers_abstention(self):
        abst = guardrails_module.evaluate_safety("Can I advertise a 100% guaranteed cure for cancer using Ayurvedic bhasmas?")
        assert abst is not None
        assert abst.code == AbstentionCode.DRUGS_MAGIC_REMEDIES_VIOLATION


class TestEndToEndOrchestration:
    @pytest.mark.asyncio
    async def test_orchestration_returns_strongly_typed_rag_response(self):
        response = await orchestration_module.process_query(
            query="Can I patent Ashwagandha in India?",
            jurisdiction="IN"
        )
        assert isinstance(response, RAGResponse)
        assert response.jurisdiction == JurisdictionEnum.IN
        assert response.direct_answer is not None
        assert response.confidence.score > 0.0
        assert len(response.citations) > 0
        assert response.trace_id.startswith("TRC-")
