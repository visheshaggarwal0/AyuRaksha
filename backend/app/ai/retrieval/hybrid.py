import logging
from typing import List, Dict, Any, Optional
from app.engines.vector_store import NeonPgVectorStore
from app.corpus.chunker import LegalDocumentChunker
from app.ai.retrieval.graph import GraphRetriever
from app.ai.retrieval.reranker import LegalAuthorityReranker

logger = logging.getLogger("AyuRaksha.HybridRetriever")

class HybridRetriever:
    """
    Coordinates Dense Vector Retrieval, Lexical Search, Knowledge Graph Expansion,
    and Legal Authority Reranking.
    """

    def __init__(self):
        self.vector_store = NeonPgVectorStore()
        self.chunker = LegalDocumentChunker()
        self._cached_chunks: Optional[List[Dict[str, Any]]] = None

    def _get_local_chunks(self) -> List[Dict[str, Any]]:
        if self._cached_chunks is None:
            self._cached_chunks = self.chunker.process_all_sources()
        return self._cached_chunks

    async def retrieve(
        self,
        query: str,
        plan: Dict[str, Any],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        jurisdiction = plan.get("jurisdiction", "IN")
        domain_filter = plan.get("domain_filter")
        reformulated_query = plan.get("reformulated_query", query)
        dense_query = plan.get("dense_query", query)

        raw_candidates: List[Dict[str, Any]] = []

        # 1. Dense Vector Search (pgvector)
        try:
            dense_results = await self.vector_store.search(
                query=dense_query,
                jurisdiction=jurisdiction,
                limit=plan.get("max_candidates", 10),
                domain_filter=domain_filter
            )
            raw_candidates.extend(dense_results)
        except Exception as e:
            logger.debug(f"Vector store search bypassed: {e}")

        # 2. Sparse Lexical Search (Postgres tsvector)
        try:
            sparse_results = await self.vector_store.search_lexical(
                query=reformulated_query,
                jurisdiction=jurisdiction,
                limit=plan.get("max_candidates", 10),
                domain_filter=domain_filter
            )
            raw_candidates.extend(sparse_results)
        except Exception as e:
            logger.debug(f"Lexical store search bypassed: {e}")

        # 3. Local In-Memory Fallback if Postgres returned few results
        if len(raw_candidates) < 3:
            local_results = self._local_search(reformulated_query, jurisdiction, domain_filter)
            raw_candidates.extend(local_results)

        # 4. Deduplicate Candidates by key
        deduped = {}
        for c in raw_candidates:
            key = f"{c.get('source_id')}|{c.get('section_number')}"
            if key not in deduped or c.get("support_score", 0) > deduped[key].get("support_score", 0):
                deduped[key] = c
        candidates = list(deduped.values())

        # 5. Knowledge Graph Expansion
        if plan.get("enable_graph_expansion", True):
            try:
                candidates = await GraphRetriever.expand_candidates(candidates)
            except Exception as e:
                logger.debug(f"Graph expansion error: {e}")

        # 6. Legal Authority-Weighted Reranking
        final_candidates = LegalAuthorityReranker.rerank(query, candidates, top_k=top_k)
        return final_candidates

    def _local_search(self, query: str, jurisdiction: str, domain_filter: Optional[str]) -> List[Dict[str, Any]]:
        import re
        terms = [t for t in re.findall(r"\w+", query.lower()) if len(t) >= 3]
        if not terms:
            return []

        candidates = []
        for chunk in self._get_local_chunks():
            if jurisdiction != "CROSS_BORDER" and chunk.get("jurisdiction") != jurisdiction:
                continue
            if domain_filter and chunk.get("domain") != domain_filter:
                continue

            target = chunk.get("text", "").lower()
            matches = sum(1 for t in terms if t in target)
            score = matches / len(terms) if terms else 0.0
            if score > 0:
                c = dict(chunk)
                c["support_score"] = score
                candidates.append(c)

        candidates.sort(key=lambda x: x["support_score"], reverse=True)
        return candidates[:12]
