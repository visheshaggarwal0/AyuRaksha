"""
AyuRaksha Legal Concept Engine
Resolves user inquiries into structured legal concepts, builds concept-expanded
retrieval queries, and organizes evidence into canonical EvidencePacks for UI and synthesis.
"""
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.modules.concepts.ontology import LEGAL_CONCEPTS_TAXONOMY, ConceptDefinition, LegalDomain
from app.models.domain import Evidence, EvidencePack, JurisdictionEnum


class ResolvedConcept(BaseModel):
    concept_id: str
    domain: str
    name: str
    confidence: float
    matched_triggers: List[str]
    statutory_hooks: List[str]
    statutory_provisions: List[str]
    priority: int = 5


class LegalConceptEngine:
    """Semantic legal concept resolver and query expansion engine."""

    def __init__(self, taxonomy: Optional[Dict[str, ConceptDefinition]] = None):
        self.taxonomy = taxonomy or LEGAL_CONCEPTS_TAXONOMY

    def resolve_concepts(self, query: str) -> List[ResolvedConcept]:
        """
        Parses the query and matches against the legal concept taxonomy using
        token and multi-word semantic triggers.
        """
        q_clean = query.lower()
        # Word boundary token set for single-word checks
        tokens = set(re.findall(r"\b\w+\b", q_clean))
        resolved: List[ResolvedConcept] = []

        for cid, concept in self.taxonomy.items():
            matched: List[str] = []
            for trigger in concept.semantic_triggers:
                trig_clean = trigger.lower()
                if " " in trig_clean or "-" in trig_clean:
                    # Multi-word phrase check
                    if trig_clean in q_clean:
                        matched.append(trigger)
                else:
                    # Single word token check
                    if trig_clean in tokens:
                        matched.append(trigger)

            if matched:
                # Confidence scaled by match count and concept priority
                match_weight = min(1.0, 0.5 + (len(matched) * 0.15))
                resolved.append(ResolvedConcept(
                    concept_id=concept.concept_id,
                    domain=concept.domain.value,
                    name=concept.name,
                    confidence=round(match_weight, 2),
                    matched_triggers=matched,
                    statutory_hooks=concept.statutory_hooks,
                    statutory_provisions=concept.statutory_provisions,
                    priority=concept.hierarchy_priority
                ))

        # Sort resolved concepts by priority (descending) then confidence
        resolved.sort(key=lambda c: (c.priority, c.confidence), reverse=True)
        return resolved

    def expand_retrieval_query(self, query: str, concepts: List[ResolvedConcept]) -> str:
        """
        Synthesizes a concept-augmented retrieval query for dense embedding and sparse engines.
        """
        if not concepts:
            return query

        statutory_anchors: List[str] = []
        for c in concepts[:3]:  # Top 3 concepts
            for hook in c.statutory_hooks:
                statutory_anchors.append(hook)

        # Deduplicate while preserving order
        unique_anchors = list(dict.fromkeys(statutory_anchors))
        anchor_string = " ".join(unique_anchors)
        return f"{query} [LEGAL_PROVISIONS: {anchor_string}]".strip()

    def get_concept_statutory_targets(self, concepts: List[ResolvedConcept]) -> List[str]:
        """Returns flattened unique statutory provision targets."""
        targets: List[str] = []
        for c in concepts:
            targets.extend(c.statutory_provisions)
        return list(dict.fromkeys(targets))

    def build_evidence_pack(self, evidence_list: List[Evidence]) -> EvidencePack:
        """
        Categorizes flat evidence into an authoritative structured EvidencePack
        for the Citation Drawer, UI Provenance Modal, and LLM context.
        """
        primary_statutes: List[Evidence] = []
        implementing_rules: List[Evidence] = []
        international_treaties: List[Evidence] = []
        regulatory_guidelines: List[Evidence] = []

        for ev in evidence_list:
            src_upper = (ev.source_title or "").upper() + " " + (ev.source_id or "").upper()
            sec_upper = (ev.section_number or "").upper()

            if any(t in src_upper for t in ["TREATY", "DIRECTIVE", "GRATK", "NAGOYA", "CBD", "WIPO"]):
                international_treaties.append(ev)
            elif any(r in sec_upper or r in src_upper for r in ["RULE", "REGULATION", "SCHEDULE A", "DCR_1945", "FSSAI"]):
                implementing_rules.append(ev)
            elif any(g in src_upper for g in ["GUIDELINE", "STANDARDS", "PHARMACOPOEIA", "FIRST SCHEDULE"]):
                regulatory_guidelines.append(ev)
            else:
                # Default primary Acts (Patents Act, BDA, DCA)
                primary_statutes.append(ev)

        return EvidencePack(
            primary_statutes=primary_statutes,
            implementing_rules=implementing_rules,
            international_treaties=international_treaties,
            regulatory_guidelines=regulatory_guidelines,
            total_count=len(evidence_list)
        )


concept_engine = LegalConceptEngine()
