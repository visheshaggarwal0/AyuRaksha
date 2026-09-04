"""
Independent Keyword Retriever
Implements IKeywordRetriever for sparse lexical search (Postgres full-text tsvector or local BM25).
"""
import asyncio
import re
from typing import List, Optional, Dict, Any, Tuple
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
        evidence_map: Dict[Tuple[str, str], Evidence] = {}

        # 1. Try PostgreSQL full-text search with strict timeout
        try:
            results = await asyncio.wait_for(
                self.vector_store.search_lexical(
                    query_text=query,
                    jurisdiction=jurisdiction,
                    limit=limit,
                    domain_filter=domain_filter
                ),
                timeout=0.60
            )
            if results:
                for idx, row in enumerate(results):
                    key = (row.get("source_id", "UNKNOWN"), row.get("section_number", ""))
                    evidence_map[key] = Evidence(
                        evidence_id=f"KEY-PG-{idx + 1:03d}",
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
        except Exception as e:
            logger.debug("Postgres tsvector search unavailable (%s); using local lexical matcher.", e)

        STOPWORDS = {
            "what", "is", "the", "are", "and", "or", "for", "in", "to", "of", "an", "on", "it", "with",
            "does", "under", "from", "any", "section", "sec", "rule", "rules", "act", "as", "like",
            "when", "can", "without", "by", "that", "this", "be", "do", "we", "our", "all", "so", "if"
        }
        raw_terms = re.findall(r"[0-9a-z]+(?:\([0-9a-z]+\))*", query.lower())
        terms = [term for term in raw_terms if len(term) >= 2 and term not in STOPWORDS]
        sec_matches = re.findall(r"\b[0-9]+[a-z]?\b|\b[0-9]+\([a-z0-9]+\)(?:\([a-z0-9]+\))*\b", query.lower())
        for sm in sec_matches:
            if sm not in terms:
                terms.append(sm)

        if terms:
            candidates = []
            for chunk in self._get_corpus_chunks():
                if jurisdiction != "CROSS_BORDER" and chunk.get("jurisdiction") != jurisdiction:
                    continue
                if domain_filter and chunk.get("domain") != domain_filter:
                    continue

                sec_lower = (chunk.get("section_number") or "").lower()
                head_lower = (chunk.get("heading") or "").lower()
                title_lower = (chunk.get("source_title") or "").lower()
                text_lower = (chunk.get("text") or "").lower()

                sec_tokens = set(re.findall(r"[0-9a-z]+", sec_lower))
                head_tokens = set(re.findall(r"[0-9a-z]+", head_lower))
                title_tokens = set(re.findall(r"[0-9a-z]+", title_lower))
                text_tokens = set(re.findall(r"[0-9a-z]+", text_lower))

                match_score = 0.0
                for term in terms:
                    clean_term = re.sub(r"[^\w]", "", term)
                    clean_sec = re.sub(r"[^\w]", "", sec_lower)
                    if clean_term and clean_term in clean_sec:
                        match_score += 15.0
                    elif term in sec_tokens:
                        match_score += 4.0
                    elif term in head_tokens:
                        match_score += 2.5
                    elif term in title_tokens:
                        match_score += 1.5
                    elif term in text_tokens:
                        match_score += 1.0

                if match_score > 0:
                    candidates.append((match_score, chunk))

            candidates.sort(key=lambda x: x[0], reverse=True)
            for idx, (score, chunk) in enumerate(candidates[:limit * 2]):
                key = (chunk.get("source_id", "UNKNOWN"), chunk.get("section_number", ""))
                if key not in evidence_map:
                    evidence_map[key] = Evidence(
                        evidence_id=f"KEY-LOC-{idx + 1:03d}",
                        source_id=chunk.get("source_id", "UNKNOWN"),
                        source_title=chunk.get("source_title", "Statutory Source"),
                        section_number=chunk.get("section_number", ""),
                        verbatim_text=chunk.get("raw_statute") or chunk.get("text", ""),
                        authority=chunk.get("authority"),
                        authority_level=chunk.get("authority_level", 4),
                        relevance_score=round(min(1.0, score / (len(terms) * 4.0)), 4),
                        retrieval_modality=RetrievalModality.KEYWORD,
                        official_url=chunk.get("source_url"),
                        document_sha256=chunk.get("source_sha256")
                    )

        combined = list(evidence_map.values())
        combined.sort(key=lambda e: e.relevance_score, reverse=True)
        return combined[:limit]
