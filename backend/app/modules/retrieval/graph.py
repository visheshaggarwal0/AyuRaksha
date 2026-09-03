"""
Independent Knowledge Graph Retriever
Implements IGraphRetriever for relational multi-hop statutory traversal.
Completely decoupled from legacy app.ai monolith.
"""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from app.modules.interfaces import IGraphRetriever
from app.models.domain import Evidence, RetrievalModality
from app.db.session import AsyncSessionLocal
from app.db.models import KnowledgeRelation, Source

logger = logging.getLogger("AyuRaksha.IndependentGraphRetriever")


class IndependentGraphRetriever(IGraphRetriever):
    """Relational statutory graph retriever operating independently."""

    # Authoritative statutory relations for offline fallback resilience
    STATUTORY_GRAPH: Dict[str, List[Dict[str, Any]]] = {
        "IND_PATENTS_ACT_1970": [
            {
                "relation_type": "REFERENCES",
                "target_source": "TKDL_AYURVEDA_BOOKS",
                "target_label": "First Schedule Classical Books",
                "evidence": "Section 3(p) excludes traditional knowledge documented in classical texts."
            },
            {
                "relation_type": "GOVERNED_BY",
                "target_source": "IND_BIOLOGICAL_DIVERSITY_ACT_2002",
                "target_label": "BDA Section 6 (Form III Patent Mandate)",
                "evidence": "Filing patents on Indian biological resources requires NBA approval under Section 6."
            },
            {
                "relation_type": "AMENDED_BY_RULES",
                "target_source": "IND_PATENTS_AMENDMENT_RULES_2024",
                "target_label": "Patents (Amendment) Rules, 2024",
                "evidence": "Modernizes Form 3 foreign filing reporting and accelerates RFE timeline to 31 months under Rule 24B."
            },
            {
                "relation_type": "ALIGNED_WITH",
                "target_source": "INT_WIPO_GRATK_TREATY_2024",
                "target_label": "WIPO GRATK Treaty (2024)",
                "evidence": "Article 3 internationalizes mandatory disclosure of genetic resources and traditional knowledge in patent filings."
            }
        ],
        "INT_WIPO_GRATK_TREATY_2024": [
            {
                "relation_type": "IMPLEMENTS_PRINCIPLE_OF",
                "target_source": "IND_PATENTS_ACT_1970",
                "target_label": "Patents Act, 1970 (Section 10(4)(ii)(D))",
                "evidence": "Mandates worldwide disclosure of country of origin for biological resources and traditional knowledge."
            },
            {
                "relation_type": "RECOGNIZES_DATABASE",
                "target_source": "TKDL_AYURVEDA_BOOKS",
                "target_label": "Traditional Knowledge Digital Library (TKDL)",
                "evidence": "Article 6 provides formal international legal sanction for TKDL databases in global patent examination."
            }
        ],
        "IND_PATENTS_AMENDMENT_RULES_2024": [
            {
                "relation_type": "AMENDS_PROCEDURE_OF",
                "target_source": "IND_PATENTS_ACT_1970",
                "target_label": "Patents Act, 1970 (Sections 8, 11B, 146)",
                "evidence": "Amends Form 3 (Rule 12), Form 18 RFE to 31 months (Rule 24B), and Form 27 to 3-year cycle (Rule 131)."
            }
        ],
        "IND_BIOLOGICAL_DIVERSITY_ACT_2002": [
            {
                "relation_type": "AMENDED_BY",
                "target_source": "IND_BDA_AMENDMENT_2023",
                "target_label": "Biological Diversity (Amendment) Act, 2023",
                "evidence": "Amended Section 7 exempting registered Ayush practitioners from SBB prior intimation."
            }
        ],
        "IND_DRUGS_COSMETICS_ACT_1940": [
            {
                "relation_type": "IMPLEMENTS",
                "target_source": "IND_DRUGS_COSMETICS_RULES_1945",
                "target_label": "Drugs and Cosmetics Rules, 1945 (Rule 158B)",
                "evidence": "Prescribes licensing, proof of effectiveness, and safety studies for ASU medicines."
            },
            {
                "relation_type": "REFERENCES",
                "target_source": "TKDL_AYURVEDA_BOOKS",
                "target_label": "First Schedule (56 Authoritative Classical Texts)",
                "evidence": "Section 3(a) defines classical ASU drugs as those manufactured strictly according to First Schedule texts."
            }
        ]
    }

    async def retrieve_graph(
        self,
        entities: List[str],
        limit: int = 5
    ) -> List[Evidence]:
        if not entities:
            return []

        clean_entities = [e.strip().upper() for e in entities if e and len(e.strip()) >= 2]
        if not clean_entities:
            return []

        # 1. Query database KnowledgeRelation table if available
        db_relations: List[Dict[str, Any]] = []
        if AsyncSessionLocal:
            try:
                async with AsyncSessionLocal() as session:
                    stmt = (
                        select(KnowledgeRelation, Source.source_code)
                        .join(Source, KnowledgeRelation.subject_source_id == Source.id)
                        .where(Source.source_code.in_(clean_entities))
                    )
                    rows = (await session.execute(stmt)).all()
                    for kr, sc in rows:
                        db_relations.append({
                            "source_id": sc,
                            "relation_type": kr.relation_type,
                            "target_label": kr.target_label,
                            "evidence": kr.evidence or "",
                            "confidence": kr.confidence
                        })
            except Exception as e:
                logger.debug("Database knowledge relations query bypassed: %s", e)

        # 2. Merge with authoritative fallback statutory relations
        all_relations: List[Dict[str, Any]] = list(db_relations)
        seen_targets = {r.get("target_label") for r in db_relations if r.get("target_label")}

        for ent in clean_entities:
            for static_key, static_list in self.STATUTORY_GRAPH.items():
                if ent in static_key or static_key in ent:
                    for s_rel in static_list:
                        tgt = s_rel.get("target_label")
                        if tgt and tgt not in seen_targets:
                            seen_targets.add(tgt)
                            all_relations.append({
                                "source_id": static_key,
                                "relation_type": s_rel.get("relation_type"),
                                "target_label": tgt,
                                "evidence": s_rel.get("evidence", ""),
                                "confidence": 0.95
                            })

        # 3. Format as domain Evidence objects
        evidence_list: List[Evidence] = []
        for idx, rel in enumerate(all_relations[:limit]):
            evidence_list.append(
                Evidence(
                    evidence_id=f"GRP-{idx + 1:03d}",
                    source_id=rel.get("source_id", "GRAPH_RELATION"),
                    source_title=f"Statutory Relation: {rel.get('relation_type')} -> {rel.get('target_label')}",
                    section_number=f"Rel: {rel.get('relation_type')}",
                    verbatim_text=rel.get("evidence", ""),
                    authority="Statutory Cross-Reference",
                    authority_level=4,
                    relevance_score=float(rel.get("confidence", 0.85)),
                    retrieval_modality=RetrievalModality.GRAPH,
                    official_url=None,
                    document_sha256=None
                )
            )

        return evidence_list
