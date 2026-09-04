"""
Independent Vector Retriever
Implements IVectorRetriever for dense semantic search over pgvector or in-memory vector index.
"""
import asyncio
from typing import List, Optional
import logging
from app.modules.interfaces import IVectorRetriever
from app.models.domain import Evidence, RetrievalModality
from app.modules.embeddings import embedding_module
from app.engines.vector_store import NeonPgVectorStore

logger = logging.getLogger("AyuRaksha.VectorRetriever")


class IndependentVectorRetriever(IVectorRetriever):
    """Dense vector retriever that operates completely independently."""

    def __init__(self, vector_store: Optional[NeonPgVectorStore] = None):
        self.vector_store = vector_store or NeonPgVectorStore()

    async def retrieve_vector(
        self,
        query: str,
        jurisdiction: str = "IN",
        limit: int = 10,
        domain_filter: Optional[str] = None
    ) -> List[Evidence]:
        query_vector = await embedding_module.embed_query(query)
        try:
            results = await asyncio.wait_for(
                self.vector_store.search(
                    query_vector=query_vector,
                    jurisdiction=jurisdiction,
                    limit=limit,
                    domain_filter=domain_filter
                ),
                timeout=0.75
            )
        except (asyncio.TimeoutError, Exception) as e:
            logger.debug("Neon pgvector search skipped or timed out (%s); relying on fused sparse/graph retrieval.", e)
            results = []

        evidence_list: List[Evidence] = []
        for idx, row in enumerate(results):
            evidence_list.append(
                Evidence(
                    evidence_id=f"VEC-{idx + 1:03d}",
                    source_id=row.get("source_id", "UNKNOWN"),
                    source_title=row.get("source_title", "Statutory Source"),
                    section_number=row.get("section_number", ""),
                    verbatim_text=row.get("raw_statute") or row.get("text", ""),
                    authority=row.get("authority"),
                    authority_level=row.get("authority_level", 4),
                    relevance_score=float(row.get("support_score", 0.5)),
                    retrieval_modality=RetrievalModality.VECTOR,
                    official_url=row.get("official_url"),
                    document_sha256=row.get("content_hash")
                )
            )
        return evidence_list
