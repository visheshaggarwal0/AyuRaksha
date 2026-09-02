import asyncio
import re
from typing import Any, Dict, List, Optional

from app.corpus.chunker import LegalDocumentChunker
from app.engines.reranker import LegalCitationReranker
from app.engines.vector_store import NeonPgVectorStore, generate_deterministic_embedding


class HybridLegalSearchEngine:
    """Fuse PostgreSQL full-text and pgvector retrieval with a safe local fallback."""

    def __init__(self):
        self.chunker = LegalDocumentChunker()
        self._cached_chunks: Optional[List[Dict[str, Any]]] = None
        self.vector_store = NeonPgVectorStore()
        self.reranker = LegalCitationReranker()

    def _get_corpus_chunks(self) -> List[Dict[str, Any]]:
        if self._cached_chunks is None:
            self._cached_chunks = self.chunker.process_all_sources()
        return self._cached_chunks

    @staticmethod
    def _lexical_score(query: str, text: str) -> float:
        terms = [term for term in re.findall(r"\w+", query.lower()) if len(term) >= 3]
        if not terms:
            return 0.0
        target = text.lower()
        matches = sum(1 for term in terms if term in target)
        return matches / len(terms)

    def _local_lexical_search(
        self, query: str, jurisdiction: str, limit: int, domain_filter: Optional[str]
    ) -> List[Dict[str, Any]]:
        candidates = []
        for chunk in self._get_corpus_chunks():
            if jurisdiction != "CROSS_BORDER" and chunk.get("jurisdiction") != jurisdiction:
                continue
            if domain_filter and chunk.get("domain") != domain_filter:
                continue
            score = self._lexical_score(query, chunk.get("text", ""))
            if score <= 0:
                continue
            candidate = dict(chunk)
            candidate["official_url"] = chunk.get("source_url")
            candidate["support_score"] = score
            candidates.append(candidate)
        candidates.sort(key=lambda candidate: candidate["support_score"], reverse=True)
        return candidates[:limit]

    @staticmethod
    def _candidate_key(candidate: Dict[str, Any]) -> str:
        source_id = str(candidate.get("source_id", "")).strip().upper()
        sec_norm = re.sub(r"[^a-z0-9]", "", str(candidate.get("section_number", "")).lower())
        if source_id and sec_norm:
            return f"{source_id}|{sec_norm}"
        return f"{source_id}|{sec_norm}|{candidate.get('text', '')[:80].strip()}"

    def _fuse_rankings(self, rankings: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        merged: Dict[str, Dict[str, Any]] = {}
        for ranking in rankings:
            for rank, candidate in enumerate(ranking, start=1):
                key = self._candidate_key(candidate)
                if key not in merged:
                    merged[key] = {**candidate, "fused_score": 0.0}
                current = merged[key]
                current["fused_score"] += 1.0 / (60 + rank)
                current["authority_level"] = max(
                    current.get("authority_level", 1), candidate.get("authority_level", 1)
                )
                if candidate.get("support_score", 0.0) > current.get("support_score", 0.0):
                    current["support_score"] = candidate["support_score"]
        return list(merged.values())

    async def search(
        self,
        query: str,
        jurisdiction: str = "IN",
        limit: int = 5,
        domain_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query_vector = generate_deterministic_embedding(query)
        vector_results, lexical_results = await asyncio.gather(
            self.vector_store.search(query_vector, jurisdiction, max(limit * 3, 10), domain_filter),
            self.vector_store.search_lexical(query, jurisdiction, max(limit * 3, 10), domain_filter),
        )
        rankings = [ranking for ranking in (vector_results, lexical_results) if ranking]
        if not rankings:
            rankings = [self._local_lexical_search(query, jurisdiction, max(limit * 3, 10), domain_filter)]
        return self.reranker.rerank(query, self._fuse_rankings(rankings), limit=limit)
