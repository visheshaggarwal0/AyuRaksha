"""
AyuRaksha Legal Concepts Module
Provides authoritative concept ontology, semantic concept resolution,
query expansion, and EvidencePack structuring.
"""
from app.modules.concepts.ontology import (
    LegalDomain,
    ConceptDefinition,
    LEGAL_CONCEPTS_TAXONOMY
)
from app.modules.concepts.engine import (
    ResolvedConcept,
    LegalConceptEngine,
    concept_engine
)

__all__ = [
    "LegalDomain",
    "ConceptDefinition",
    "LEGAL_CONCEPTS_TAXONOMY",
    "ResolvedConcept",
    "LegalConceptEngine",
    "concept_engine"
]
