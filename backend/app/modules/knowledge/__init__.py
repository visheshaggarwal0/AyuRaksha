"""
AyuRaksha Knowledge Module
Implements IKnowledgeModule for botanical taxonomy, First Schedule book catalogs,
and relational statutory knowledge graphs.
"""
from typing import List, Optional
from app.modules.interfaces import IKnowledgeModule
from app.models.domain import GraphEntity, GraphRelationship
from app.corpus.taxonomy import taxonomy_engine
from app.ai.retrieval.graph import GraphRetriever


class ModularKnowledgeEngine(IKnowledgeModule):
    """Knowledge service connecting botanical taxonomy and statutory relations."""

    def lookup_botanical(self, name_or_synonym: str) -> Optional[GraphEntity]:
        bot = taxonomy_engine.resolve_plant(name_or_synonym)
        if not bot:
            return None

        return GraphEntity(
            entity_id=f"BOT-{bot.get('id', '001')}",
            name=bot.get("canonical_name", name_or_synonym),
            entity_type="BOTANICAL",
            aliases=bot.get("vernacular_names", []),
            metadata={
                "scientific_name": bot.get("scientific_name", ""),
                "family": bot.get("family", ""),
                "parts_used": bot.get("parts_used", "")
            }
        )

    def is_classical_formulation(self, formulation_name: str) -> bool:
        # Check against authoritative books or known formulations
        matched_books = taxonomy_engine.search_books(formulation_name)
        return len(matched_books) > 0

    def get_related_provisions(self, section_number: str) -> List[GraphRelationship]:
        sec_clean = section_number.strip().lower()
        relationships = []

        # Map known relations from statutory graph
        if "3(p)" in sec_clean:
            relationships.append(
                GraphRelationship(
                    relationship_id="REL-001",
                    subject_id="IND_PATENTS_ACT_1970_SEC_003_P",
                    predicate="ALIGNED_WITH",
                    object_id="IND_BIOLOGICAL_DIVERSITY_ACT_2002_SEC_006",
                    statutory_basis="Patents Act Section 10(4)(ii)(D) disclosure & BDA Section 6",
                    confidence=1.0
                )
            )
            relationships.append(
                GraphRelationship(
                    relationship_id="REL-002",
                    subject_id="IND_PATENTS_ACT_1970_SEC_003_P",
                    predicate="DISTINGUISHES",
                    object_id="IND_DRUGS_COSMETICS_RULES_1945_RULE_158B",
                    statutory_basis="Rule 158B Proprietary vs Classical ASU",
                    confidence=0.95
                )
            )
        elif "158b" in sec_clean:
            relationships.append(
                GraphRelationship(
                    relationship_id="REL-003",
                    subject_id="IND_DRUGS_COSMETICS_RULES_1945_RULE_158B",
                    predicate="GOVERNED_BY",
                    object_id="IND_DRUGS_COSMETICS_ACT_1940_SEC_003_H",
                    statutory_basis="Chapter IV-A ASU Patent or Proprietary Medicines",
                    confidence=1.0
                )
            )

        return relationships


knowledge_module = ModularKnowledgeEngine()
