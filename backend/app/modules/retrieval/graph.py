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

    def __init__(self):
        self._cache: Dict[tuple, List[Evidence]] = {}
        self._full_kg: Optional[Dict[str, Any]] = None
        self._nodes_by_id: Dict[str, Dict[str, Any]] = {}
        self._edges: List[Dict[str, Any]] = []
        self._init_knowledge_graph()

    def _init_knowledge_graph(self):
        try:
            from app.ai.retrieval.graph import GraphRetriever
            kg = GraphRetriever.get_full_knowledge_graph()
            self._full_kg = kg
            self._nodes_by_id = {n["id"]: n for n in kg.get("nodes", [])}
            self._edges = kg.get("edges", [])
            logger.info("Knowledge Graph initialized with %d nodes and %d edges", len(self._nodes_by_id), len(self._edges))
        except Exception as e:
            logger.warning("Could not load full knowledge graph: %s", e)

    def _extract_graph_entities(self, text: str) -> List[str]:
        """Extracts matched Knowledge Graph node IDs from entity strings or raw query text."""
        lower = text.lower()
        matched_node_ids = set()

        # Botanical Aliases
        if any(w in lower for w in ["ashwagandha", "withania somnifera", "withania", "somnifera"]):
            matched_node_ids.add("BOTANICAL_ASHWAGANDHA")
        if any(w in lower for w in ["haridra", "turmeric", "curcuma longa", "curcuma", "curcumin"]):
            matched_node_ids.add("BOTANICAL_HARIDRA")
        if any(w in lower for w in ["brahmi", "bacopa monnieri", "bacopa", "shankhpushpi"]):
            matched_node_ids.add("BOTANICAL_BRAHMI")
        if any(w in lower for w in ["guduchi", "giloy", "tinospora cordifolia", "tinospora", "amritarishta"]):
            matched_node_ids.add("BOTANICAL_GUDUCHI")
        if any(w in lower for w in ["kutki", "picrorhiza kurroa", "picrorhiza"]):
            matched_node_ids.add("BOTANICAL_KUTKI")

        # Classical Texts
        if "charaka" in lower or "caraka" in lower:
            matched_node_ids.add("TEXT_CHARAKA_SAMHITA")
        if "sushruta" in lower or "susmruta" in lower:
            matched_node_ids.add("TEXT_SUSHRUTA_SAMHITA")
        if "bhaishajya" in lower or "ratnavali" in lower:
            matched_node_ids.add("TEXT_BHAISHAJYA_RATNAVALI")
        if "ashtanga" in lower or "hridaya" in lower or "vagbhata" in lower:
            matched_node_ids.add("TEXT_ASHTANGA_HRIDAYA")

        # Statutory Patent Sections
        if any(w in lower for w in ["3(p)", "3 p", "traditional knowledge bar", "tk bar", "section 3(p)"]):
            matched_node_ids.add("SEC_PA_3P")
        if any(w in lower for w in ["3(e)", "3 e", "mere admixture", "synergy", "synergistic", "section 3(e)"]):
            matched_node_ids.add("SEC_PA_3E")
        if any(w in lower for w in ["10(4)", "origin disclosure", "source of origin", "geographical origin"]):
            matched_node_ids.add("SEC_PA_10_4")
        if any(w in lower for w in ["25(1)(k)", "pre-grant opposition", "form 7a"]):
            matched_node_ids.add("SEC_PA_25_1_K")
            matched_node_ids.add("FORM_PA_7A")
        if any(w in lower for w in ["section 39", "foreign filing license", "form 25"]):
            matched_node_ids.add("SEC_PA_39")
            matched_node_ids.add("FORM_PA_25")
        if any(w in lower for w in ["form 18a", "expedited examination", "fast-track"]):
            matched_node_ids.add("FORM_PA_18A")
        if any(w in lower for w in ["form 27", "working statement"]):
            matched_node_ids.add("FORM_PA_27")
        if "patent" in lower or "patents act" in lower:
            matched_node_ids.add("STATUTE_PATENTS_ACT")

        # Biodiversity / ABS
        if any(w in lower for w in ["bda", "biodiversity", "nba", "section 6", "form iii", "form 3", "abs", "benefit sharing", "sbb"]):
            matched_node_ids.add("STATUTE_BDA_2002")
            matched_node_ids.add("SEC_BDA_6")
            matched_node_ids.add("FORM_NBA_III")

        # Drug Regs / DCA / FSSAI
        if any(w in lower for w in ["rule 158b", "158b", "classical", "proprietary", "asu", "form 25d"]):
            matched_node_ids.add("STATUTE_DCA_1940")
            matched_node_ids.add("RULE_DCA_158B")
        if any(w in lower for w in ["ayurveda aahar", "aahara", "fssai", "dietary supplement"]):
            matched_node_ids.add("REG_FSSAI_AAHARA")

        # International / WIPO GRATK
        if any(w in lower for w in ["wipo", "gratk", "treaty", "international", "export", "foreign patent"]):
            matched_node_ids.add("TREATY_WIPO_GRATK")
            matched_node_ids.add("ART_WIPO_GRATK_3")

        return list(matched_node_ids)

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

        cache_key = tuple(sorted(clean_entities))
        if cache_key in self._cache:
            return self._cache[cache_key][:limit]

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

        # 2. Extract multi-hop entities from full Knowledge Graph
        kg_node_ids = set()
        for ent in entities:
            extracted = self._extract_graph_entities(ent)
            kg_node_ids.update(extracted)

        # Traverse Knowledge Graph edges for matched nodes
        graph_evidence_items: List[Evidence] = []
        seen_edges = set()

        if self._edges and self._nodes_by_id and kg_node_ids:
            for edge in self._edges:
                src_id = edge.get("source")
                tgt_id = edge.get("target")
                rel = edge.get("relation", "CONNECTS_TO")
                edge_key = f"{src_id}->{tgt_id}"

                if (src_id in kg_node_ids or tgt_id in kg_node_ids) and edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    src_node = self._nodes_by_id.get(src_id, {"label": src_id, "badge": "", "description": "", "authority": ""})
                    tgt_node = self._nodes_by_id.get(tgt_id, {"label": tgt_id, "badge": "", "description": "", "authority": ""})

                    # Construct rich Knowledge Graph Evidence
                    verbatim = (
                        f"[Knowledge Graph Statutory Traversal: {rel}]\n"
                        f"• Origin Node: {src_node.get('label')} [{src_node.get('badge', '')}]\n"
                        f"• Traversal Link: --[{rel}]--> {tgt_node.get('label')} [{tgt_node.get('badge', '')}]\n"
                        f"• Statutory Context: {src_node.get('description', '')}\n"
                        f"• Relational Evidence: {edge.get('rationale', '')}\n"
                        f"• Connected Authority: {tgt_node.get('authority', '')} ({tgt_node.get('section_reference', '')})\n"
                        f"• Target Rule: {tgt_node.get('description', '')}"
                    )

                    graph_evidence_items.append(
                        Evidence(
                            evidence_id=f"KG-{len(graph_evidence_items) + 1:03d}",
                            source_id=f"KG_{src_id}_{tgt_id}",
                            source_title=f"Knowledge Graph: {src_node.get('label')} -> {rel} -> {tgt_node.get('label')}",
                            section_number=f"KG: {rel}",
                            verbatim_text=verbatim,
                            authority=f"AyuRaksha Knowledge Graph ({tgt_node.get('authority', 'Statutory Graph')})",
                            authority_level=5,
                            relevance_score=0.96,
                            retrieval_modality=RetrievalModality.GRAPH,
                            official_url=tgt_node.get("official_url"),
                            document_sha256=None
                        )
                    )

        # 3. Fallback to static statutory relations if needed
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

        # Add static relation evidence
        for idx, rel in enumerate(all_relations):
            if len(graph_evidence_items) >= limit:
                break
            graph_evidence_items.append(
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

        final_evidence = graph_evidence_items[:limit]
        self._cache[cache_key] = final_evidence
        return final_evidence
