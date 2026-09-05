import pytest
from app.modules.retrieval.composite import CompositeRetrievalModule
from app.models.domain import RetrievalModality

@pytest.mark.asyncio
async def test_knowledge_graph_rag_retrieval_on_botanical_query():
    retriever = CompositeRetrievalModule()
    
    query = "Can I patent an Ayurvedic formulation of Ashwagandha and Guduchi for arthritis?"
    result = await retriever.retrieve(query=query, jurisdiction="IN", limit=10)
    
    assert result is not None
    assert len(result.candidates) > 0
    assert RetrievalModality.GRAPH in result.modalities_used
    
    graph_candidates = [c for c in result.candidates if c.retrieval_modality == RetrievalModality.GRAPH]
    assert len(graph_candidates) > 0
    
    first_graph = graph_candidates[0]
    assert "Knowledge Graph" in first_graph.source_title or "Statutory Relation" in first_graph.source_title
    assert any(term in first_graph.verbatim_text for term in ["Withania", "Ashwagandha", "Charaka", "Patents Act", "Statutory"])

@pytest.mark.asyncio
async def test_knowledge_graph_rag_retrieval_on_bda_query():
    retriever = CompositeRetrievalModule()
    
    query = "What are my ABS obligations under BDA 2023 for sourcing Kutki from Himachal Pradesh?"
    result = await retriever.retrieve(query=query, jurisdiction="IN", limit=10)
    
    assert result is not None
    assert RetrievalModality.GRAPH in result.modalities_used
    graph_candidates = [c for c in result.candidates if c.retrieval_modality == RetrievalModality.GRAPH]
    assert len(graph_candidates) > 0
    assert any("BDA" in c.source_title or "NBA" in c.verbatim_text or "Picrorhiza" in c.verbatim_text or "Knowledge Graph" in c.source_title for c in graph_candidates)
