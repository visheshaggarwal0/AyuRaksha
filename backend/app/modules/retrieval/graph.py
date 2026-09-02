"""
Independent Knowledge Graph Retriever
Implements IGraphRetriever for relational multi-hop statutory traversal.
"""
from typing import List, Dict, Any
from app.modules.interfaces import IGraphRetriever
from app.models.domain import Evidence, RetrievalModality
from app.ai.retrieval.graph import GraphRetriever


class IndependentGraphRetriever(IGraphRetriever):
    """Relational statutory graph retriever operating independently."""

    async def retrieve_graph(
        self,
        entities: List[str],
        limit: int = 10
    ) -> List[Evidence]:
        if not entities:
            return []

        # Form mock candidate objects with entity names to drive graph expansion
        initial_candidates = [
            {"source_id": e.upper(), "section_number": e, "text": f"Entity mention {e}"}
            for e in entities
        ]
        expanded = await GraphRetriever.expand_candidates(initial_candidates)

        evidence_list: List[Evidence] = []
        for idx, row in enumerate(expanded[:limit]):
            evidence_list.append(
                Evidence(
                    evidence_id=f"GRP-{idx + 1:03d}",
                    source_id=row.get("source_id", "GRAPH_RELATION"),
                    source_title=row.get("source_title", "Statutory Knowledge Graph"),
                    section_number=row.get("section_number", ""),
                    verbatim_text=row.get("text", ""),
                    authority=row.get("authority", "Statutory Cross-Reference"),
                    authority_level=row.get("authority_level", 4),
                    relevance_score=0.85,
                    retrieval_modality=RetrievalModality.GRAPH,
                    official_url=row.get("official_url"),
                    document_sha256=row.get("content_hash")
                )
            )
        return evidence_list
