import logging
from typing import List, Dict, Any, Optional
from app.engines.vector_store import NeonPgVectorStore, generate_embedding
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
        retrieval_status = {"dense": False, "lexical": False, "fallback": False}

        # 1. Dense Vector Search (pgvector)
        try:
            dense_vector = generate_embedding(dense_query)
            dense_results = await self.vector_store.search(
                query_vector=dense_vector,
                jurisdiction=jurisdiction,
                limit=plan.get("max_candidates", 10),
                domain_filter=domain_filter
            )
            raw_candidates.extend(dense_results)
            retrieval_status["dense"] = True
        except Exception as e:
            logger.warning(f"Vector store search failed: {e}")
            retrieval_status["dense"] = False

        # 2. Sparse Lexical Search (Postgres tsvector)
        try:
            sparse_results = await self.vector_store.search_lexical(
                query_text=reformulated_query,
                jurisdiction=jurisdiction,
                limit=plan.get("max_candidates", 10),
                domain_filter=domain_filter
            )
            raw_candidates.extend(sparse_results)
            retrieval_status["lexical"] = True
        except Exception as e:
            logger.warning(f"Lexical store search failed: {e}")
            retrieval_status["lexical"] = False

        # 3. Local In-Memory Fallback if Postgres returned few results
        if len(raw_candidates) < 3:
            local_results = self._local_search(reformulated_query, jurisdiction, domain_filter)
            raw_candidates.extend(local_results)
            retrieval_status["fallback"] = True
        else:
            retrieval_status["fallback"] = False

        # 4. Deduplicate Candidates by key
        deduped = {}
        for c in raw_candidates:
            key = f"{c.get('source_id')}|{c.get('section_number')}"
            if key not in deduped or c.get("support_score", 0) > deduped[key].get("support_score", 0):
                deduped[key] = c
        candidates = list(deduped.values())

        # Attach retrieval status to first candidate for pipeline access
        if candidates:
            candidates[0]["retrieval_status"] = retrieval_status

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

        if isinstance(domain_filter, str):
            allowed_domains = {domain_filter}
        elif isinstance(domain_filter, (list, tuple, set)):
            allowed_domains = set(domain_filter)
        else:
            allowed_domains = None

        candidates = []
        for chunk in self._get_local_chunks():
            if jurisdiction != "CROSS_BORDER" and chunk.get("jurisdiction") != jurisdiction:
                continue
            if allowed_domains and chunk.get("domain") not in allowed_domains:
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
