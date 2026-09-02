import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import KnowledgeRelation, Source

logger = logging.getLogger("AyuRaksha.GraphRetriever")

class GraphRetriever:
    """
    Traverses statutory knowledge graph relations (AMENDS, IMPLEMENTS, GOVERNS, REFERENCES).
    Expands direct retrieval candidates with interconnected regulatory provisions.
    """

    # Static authoritative knowledge links for offline resilience
    STATIC_STATUTORY_GRAPH = {
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

    @classmethod
    async def expand_candidates(cls, candidates: List[Dict[str, Any]], max_hops: int = 1) -> List[Dict[str, Any]]:
        """
        Expands top candidate sources with relational links from knowledge_relations.
        """
        expanded = list(candidates)
        seen_keys = {c.get("source_id") for c in candidates}

        for candidate in candidates[:5]:
            src_id = candidate.get("source_id")
            if not src_id:
                continue

            # 1. Check database relations
            db_relations = await cls._fetch_db_relations(src_id)

            # 2. Merge with static statutory graph
            static_relations = cls.STATIC_STATUTORY_GRAPH.get(src_id, [])
            all_relations = db_relations + static_relations

            for rel in all_relations:
                target_src = rel.get("target_source") or rel.get("target_label")
                if target_src and target_src not in seen_keys:
                    seen_keys.add(target_src)
                    # Add synthetic relation node to provide graph context to the LLM
                    expanded.append({
                        "source_id": f"GRAPH_RELATION_{target_src}",
                        "source_title": f"Statutory Relation: {rel.get('relation_type')} -> {target_src}",
                        "section_number": f"Rel: {rel.get('relation_type')}",
                        "heading": f"Statutory Link: {rel.get('target_label')}",
                        "raw_statute": rel.get("evidence", ""),
                        "text": f"[Statutory Relation: {rel.get('relation_type')}]\nSource: {src_id}\nConnected Law: {target_src}\nStatutory Evidence: {rel.get('evidence')}",
                        "authority_level": candidate.get("authority_level", 4) - 1,
                        "support_score": candidate.get("support_score", 0.5) * 0.85,
                        "is_graph_expanded": True,
                        "relation_type": rel.get("relation_type")
                    })

        return expanded

    @staticmethod
    async def _fetch_db_relations(source_code: str) -> List[Dict[str, Any]]:
        relations = []
        try:
            async with AsyncSessionLocal() as session:
                stmt = (
                    select(KnowledgeRelation, Source.source_code)
                    .join(Source, KnowledgeRelation.subject_source_id == Source.id)
                    .where(Source.source_code == source_code)
                )
                res = await session.execute(stmt)
                rows = res.all()
                for kr, sc in rows:
                    relations.append({
                        "relation_type": kr.relation_type,
                        "target_label": kr.target_label,
                        "evidence": kr.evidence or "",
                        "confidence": kr.confidence
                    })
        except Exception as e:
            logger.debug(f"DB knowledge_relations query bypassed: {e}")
        return relations
