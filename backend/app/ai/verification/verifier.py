import re
from typing import List, Dict, Any

class SentenceClaimVerifier:
    """
    Decomposes synthesized regulatory responses into individual sentence-level claims
    and verifies lexical/entailment support against the specific cited sources.
    """

    LEGAL_STOPWORDS = {
        "shall", "which", "under", "where", "there", "their", "these", "those",
        "section", "rule", "rules", "order", "proviso", "provided", "herein",
        "therein", "thereof", "therewith", "therefrom", "whereas", "hereby",
        "sub-section", "clause", "sub-clause", "act", "acts", "schedule", "first"
    }

    @classmethod
    def verify(cls, answer_text: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not answer_text or not sources:
            return {
                "grounding_rate": 0.0,
                "verified_claims": [],
                "unsupported_claims": [],
                "status": "UNVERIFIED"
            }

        # 1. Decompose into sentences
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", answer_text) if len(s.strip()) > 15]

        verified_claims = []
        unsupported_claims = []

        source_lookup = {idx + 1: src for idx, src in enumerate(sources)}

        for sent in sentences:
            citation_markers = [int(m) for m in re.findall(r"\[(\d+)\]", sent)]
            if not citation_markers:
                continue

            sent_clean = re.sub(r"\[\d+\]", "", sent).strip()
            sent_terms = {
                w for w in re.findall(r"\b[a-zA-Z]{4,}\b", sent_clean.lower())
                if w not in cls.LEGAL_STOPWORDS
            }

            if not sent_terms:
                continue

            max_support = 0.0
            best_source = None

            for marker in citation_markers:
                src = source_lookup.get(marker)
                if not src:
                    continue

                source_text = f"{src.get('source_title', '')} {src.get('heading', '')} {src.get('raw_statute', '')} {src.get('text', '')}".lower()
                matches = sum(1 for term in sent_terms if term in source_text)
                score = matches / len(sent_terms)

                if score > max_support:
                    max_support = score
                    best_source = src

            is_supported = max_support >= 0.25
            claim_record = {
                "claim": sent_clean,
                "cited_markers": citation_markers,
                "support_score": round(max_support, 3),
                "is_grounded": is_supported,
                "supporting_source": best_source.get("source_title") if best_source else None
            }

            if is_supported:
                verified_claims.append(claim_record)
            else:
                unsupported_claims.append(claim_record)

        total_claims = len(verified_claims) + len(unsupported_claims)
        grounding_rate = (len(verified_claims) / total_claims) if total_claims > 0 else 1.0

        return {
            "grounding_rate": round(grounding_rate, 3),
            "verified_claims_count": len(verified_claims),
            "unsupported_claims_count": len(unsupported_claims),
            "verified_claims": verified_claims,
            "unsupported_claims": unsupported_claims,
            "status": "PASS" if grounding_rate >= 0.70 else "FLAGGED"
        }
