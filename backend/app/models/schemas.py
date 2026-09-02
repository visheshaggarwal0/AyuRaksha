from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid

class Jurisdiction(str, Enum):
    INDIA = "IN"
    INTERNATIONAL = "INT"
    CROSS_BORDER = "CROSS_BORDER"

class AuthorityLevel(int, Enum):
    STATUTE_TREATY = 5
    NOTIFICATION_ORDER = 4
    OFFICIAL_GUIDELINE = 3
    SECONDARY = 2
    COMMENTARY = 1

class Citation(BaseModel):
    source_id: str = Field(..., description="Unique source code, e.g. IND_PATENTS_ACT_1970")
    source_title: str
    section: str = Field(..., description="e.g. Section 3(p)")
    subsection: Optional[str] = None
    jurisdiction: Jurisdiction = Jurisdiction.INDIA
    official_url: Optional[str] = None
    support_score: float = Field(default=1.0, ge=0.0, le=1.0)
    verbatim_quote: str
    document_sha256: Optional[str] = None

class ClaimVerification(BaseModel):
    claim: str
    is_supported: bool
    confidence_score: float
    supporting_citations: List[Citation] = []

class StructuredAnswer(BaseModel):
    direct_answer: str
    jurisdiction: Jurisdiction
    assessment_table: Dict[str, Any] = {}
    verified_claims: List[ClaimVerification] = []
    citations: List[Citation] = []
    confidence_level: str = "HIGH" # HIGH, MODERATE, LOW
    caveats: List[str] = []
    safe_abstention: bool = False
    abstention_reason: Optional[str] = None
    recommended_next_action: str
    cross_border_posture: Optional[Dict[str, str]] = None
    language: str = "en"

# Product Classification Request & Response
class ProductClassificationRequest(BaseModel):
    name: str = Field(..., description="Name of the formulation or product")
    in_classical_text: bool = Field(..., description="Is the formulation from an authoritative classical Ayurvedic text?")
    is_formulation_modified: bool = Field(..., description="Is the composition or ratio modified?")
    has_novel_excipients: bool = Field(default=False, description="Are novel excipients or extraction techniques used?")
    is_purified_standardized_fraction: bool = Field(default=False, description="Is the formulation a purified and standardized fraction with defined marker compounds (Phytopharmaceutical)?")
    intended_use: str = Field(default="therapeutic", description="therapeutic, supplement, cosmetic, food")
    disease_treatment_claims: bool = Field(default=True, description="Does the product claim to treat/cure/mitigate disease?")
    has_biological_resources: bool = Field(default=True, description="Does it contain plants/animals/microbes sourced from India?")
    target_market: str = Field(default="IN", description="IN, US, EU, UAE")

class ProductClassificationResponse(BaseModel):
    product_name: str
    category: str
    governing_act: str
    patentability: str
    patent_rationale: str
    abs_required: bool
    regulatory_authority: str
    citations: List[Citation] = []
    confidence: float
    next_actions: List[str] = []

# ABS Wizard Request & Response
class ABSAssessmentRequest(BaseModel):
    biological_resource: str = Field(..., description="Botanical/biological resource, e.g. Ashwagandha, Neem")
    origin_country: str = Field(default="India")
    sourced_from_state: Optional[str] = Field(default="Himachal Pradesh")
    is_commercial_utilization: bool = Field(default=True)
    is_traditional_knowledge_associated: bool = Field(default=True)
    is_indian_entity: bool = Field(default=True, description="Is the entity Indian citizen/incorporated in India without foreign equity?")
    is_export_intended: bool = Field(default=False)

class ABSAssessmentResponse(BaseModel):
    resource: str
    trigger_detected: bool
    governing_statute: str
    applicable_authority: str # NBA or SBB
    approval_type: str # Prior Intimation (Sec 7) or Prior Approval (Sec 3)
    risk_level: str  # e.g. HIGH_COMPLIANCE_MANDATE | STANDARD_DOMESTIC_COMPLIANCE
    benefit_sharing_applicable: bool = True
    statutory_citations: List[Citation] = Field(default_factory=list)
    mandatory_next_steps: List[str] = []


# Re-export core domain models for module-wide access
from app.models.domain import (
    SourceDocument,
    DocumentVersion,
    Provision,
    CorpusChunk,
    Evidence,
    GraphEntity,
    GraphRelationship,
    RetrievalResult,
    RAGResponse,
    Confidence,
    ConfidenceLevel,
    AbstentionReason,
    AbstentionCode,
    RetrievalModality,
    JurisdictionEnum,
    DocumentTypeEnum,
)
