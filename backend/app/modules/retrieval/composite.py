"""
Composite Multi-Modal Retrieval Module
Implements IRetrievalModule by fusing independent vector, keyword, and graph retrievers with RRF.
"""
import re
import time
import asyncio
from typing import List, Optional, Dict, Any

from app.modules.interfaces import (
    IRetrievalModule,
    IVectorRetriever,
    IKeywordRetriever,
    IGraphRetriever
)
from app.models.domain import Evidence, RetrievalResult, RetrievalModality, JurisdictionEnum
from app.modules.retrieval.vector import IndependentVectorRetriever
from app.modules.retrieval.keyword import IndependentKeywordRetriever
from app.modules.retrieval.graph import IndependentGraphRetriever


class CompositeRetrievalModule(IRetrievalModule):
    """Coordinates independent vector, keyword, and graph retrieval."""

    def __init__(
        self,
        vector_retriever: Optional[IVectorRetriever] = None,
        keyword_retriever: Optional[IKeywordRetriever] = None,
        graph_retriever: Optional[IGraphRetriever] = None
    ):
        self.vector_retriever = vector_retriever or IndependentVectorRetriever()
        self.keyword_retriever = keyword_retriever or IndependentKeywordRetriever()
        self.graph_retriever = graph_retriever or IndependentGraphRetriever()

    async def retrieve(
        self,
        query: str,
        jurisdiction: str = "IN",
        limit: int = 5,
        domain_filter: Optional[str] = None
    ) -> RetrievalResult:
        start_time = time.time()
        modalities: List[RetrievalModality] = []

        # Execute independent retrievals concurrently
        vector_task = self.vector_retriever.retrieve_vector(
            query=query,
            jurisdiction=jurisdiction,
            limit=limit * 2,
            domain_filter=domain_filter
        )
        keyword_task = self.keyword_retriever.retrieve_keyword(
            query=query,
            jurisdiction=jurisdiction,
            limit=limit * 2,
            domain_filter=domain_filter
        )

        vector_results, keyword_results = await asyncio.gather(vector_task, keyword_task)
        if vector_results:
            modalities.append(RetrievalModality.VECTOR)
        if keyword_results:
            modalities.append(RetrievalModality.KEYWORD)

        # Reciprocal Rank Fusion (RRF)
        fused_candidates: Dict[str, Evidence] = {}
        rrf_scores: Dict[str, float] = {}

        for rank_list in [vector_results, keyword_results]:
            for rank, ev in enumerate(rank_list, start=1):
                clean_sec = re.sub(r"\s+", " ", (ev.section_number or "").strip().upper())
                key = f"{(ev.source_id or '').upper()}|{clean_sec}"
                if key not in fused_candidates:
                    fused_candidates[key] = ev
                    rrf_scores[key] = 0.0
                rrf_scores[key] += 1.0 / (60 + rank)

        # Graph expansion on top candidates
        top_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)[:3]
        entities_for_graph = [k.split("|")[1] for k in top_keys if "|" in k and k.split("|")[1]]
        if entities_for_graph:
            graph_results = await self.graph_retriever.retrieve_graph(entities_for_graph, limit=3)
            if graph_results:
                modalities.append(RetrievalModality.GRAPH)
                for ev in graph_results:
                    clean_sec = re.sub(r"\s+", " ", (ev.section_number or "").strip().upper())
                    key = f"{(ev.source_id or '').upper()}|{clean_sec}"
                    if key not in fused_candidates:
                        fused_candidates[key] = ev
                        rrf_scores[key] = 0.0
                    rrf_scores[key] += 0.015  # Graph bonus

        # Sort and assemble final evidence
        sorted_keys = sorted(rrf_scores.keys(), key=lambda k: rrf_scores[k], reverse=True)
        final_candidates: List[Evidence] = []
        for k in sorted_keys[:limit]:
            ev = fused_candidates[k]
            ev.relevance_score = round(min(1.0, rrf_scores[k] * 10), 4)
            final_candidates.append(ev)

        latency = round((time.time() - start_time) * 1000, 2)
        jur_enum = JurisdictionEnum.CROSS_BORDER if jurisdiction == "CROSS_BORDER" else JurisdictionEnum(jurisdiction)

        return RetrievalResult(
            query=query,
            jurisdiction=jur_enum,
            candidates=final_candidates,
            modalities_used=modalities or [RetrievalModality.COMPOSITE],
            total_candidates_found=len(fused_candidates),
            latency_ms=latency
        )


# Default shared instance
retrieval_module = CompositeRetrievalModule()
