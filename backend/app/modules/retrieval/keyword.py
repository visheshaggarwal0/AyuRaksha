"""
Independent Keyword Retriever
Implements IKeywordRetriever for sparse lexical search (Postgres full-text tsvector or local BM25).
"""
import re
from typing import List, Optional, Dict, Any
import logging
from app.modules.interfaces import IKeywordRetriever
from app.models.domain import Evidence, RetrievalModality
from app.engines.vector_store import NeonPgVectorStore
from app.corpus.chunker import LegalDocumentChunker

logger = logging.getLogger("AyuRaksha.KeywordRetriever")


class IndependentKeywordRetriever(IKeywordRetriever):
    """Sparse lexical retriever operating independently."""

    def __init__(self, vector_store: Optional[NeonPgVectorStore] = None):
        self.vector_store = vector_store or NeonPgVectorStore()
        self.chunker = LegalDocumentChunker()
        self._cached_chunks: Optional[List[Dict[str, Any]]] = None

    def _get_corpus_chunks(self) -> List[Dict[str, Any]]:
        if self._cached_chunks is None:
            self._cached_chunks = self.chunker.process_all_sources()
        return self._cached_chunks

    async def retrieve_keyword(
        self,
        query: str,
        jurisdiction: str = "IN",
        limit: int = 10,
        domain_filter: Optional[str] = None
    ) -> List[Evidence]:
        # 1. Try Postgres tsvector lexical search
        try:
            results = await self.vector_store.search_lexical(
                query_text=query,
                jurisdiction=jurisdiction,
                limit=limit,
                domain_filter=domain_filter
            )
            if results:
                evidence_list: List[Evidence] = []
                for idx, row in enumerate(results):
                    evidence_list.append(
                        Evidence(
                            evidence_id=f"KEY-{idx + 1:03d}",
                            source_id=row.get("source_id", "UNKNOWN"),
                            source_title=row.get("source_title", "Statutory Source"),
                            section_number=row.get("section_number", ""),
                            verbatim_text=row.get("raw_statute") or row.get("text", ""),
                            authority=row.get("authority"),
                            authority_level=row.get("authority_level", 4),
                            relevance_score=min(1.0, float(row.get("lexical_rank", 0.5))),
                            retrieval_modality=RetrievalModality.KEYWORD,
                            official_url=row.get("official_url"),
                            document_sha256=row.get("content_hash")
                        )
                    )
                return evidence_list
        except Exception as e:
            logger.debug("Postgres tsvector search unavailable (%s); using local lexical matcher.", e)

        # 2. Local fallback lexical matcher
        terms = [term for term in re.findall(r"\w+", query.lower()) if len(term) >= 3]
        if not terms:
            return []

        candidates = []
        for chunk in self._get_corpus_chunks():
            if jurisdiction != "CROSS_BORDER" and chunk.get("jurisdiction") != jurisdiction:
                continue
            if domain_filter and chunk.get("domain") != domain_filter:
                continue

            target = chunk.get("text", "").lower()
            matches = sum(1 for term in terms if term in target)
            if matches > 0:
                score = matches / len(terms)
                candidates.append((score, chunk))

        candidates.sort(key=lambda x: x[0], reverse=True)
        top_matches = candidates[:limit]

        evidence_list = []
        for idx, (score, chunk) in enumerate(top_matches):
            evidence_list.append(
                Evidence(
                    evidence_id=f"KEY-LOC-{idx + 1:03d}",
                    source_id=chunk.get("source_id", "UNKNOWN"),
                    source_title=chunk.get("source_title", "Statutory Source"),
                    section_number=chunk.get("section_number", ""),
                    verbatim_text=chunk.get("raw_statute") or chunk.get("text", ""),
                    authority=chunk.get("authority"),
                    authority_level=chunk.get("authority_level", 4),
                    relevance_score=round(score, 4),
                    retrieval_modality=RetrievalModality.KEYWORD,
                    official_url=chunk.get("source_url"),
                    document_sha256=chunk.get("source_sha256")
                )
            )
        return evidence_list
