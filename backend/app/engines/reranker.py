"""A deterministic, explainable reranker for statutory retrieval results."""

from __future__ import annotations

import re
from typing import Any, Dict, List


class LegalCitationReranker:
    def rerank(self, query: str, candidates: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        query_terms = set(re.findall(r"\b\w{3,}\b", query.lower()))
        requested_sections = set(re.findall(r"\b(?:section|rule|article)\s+([\d\w()\-]+)", query.lower()))
        reranked = []
        for candidate in candidates:
            text_terms = set(re.findall(r"\b\w{3,}\b", candidate.get("text", "").lower()))
            overlap = len(query_terms & text_terms) / max(len(query_terms), 1)
            section = candidate.get("section_number", "").lower()
            section_bonus = 0.25 if any(value in section for value in requested_sections) else 0.0
            authority_bonus = (candidate.get("authority_level", 1) / 5.0) * 0.15
            fused_score = candidate.get("fused_score", candidate.get("support_score", 0.0))
            result = dict(candidate)
            result["support_score"] = round(min(1.0, 0.55 * fused_score + 0.30 * overlap + authority_bonus + section_bonus), 4)
            reranked.append(result)
        reranked.sort(key=lambda item: item["support_score"], reverse=True)
        return reranked[:limit]
