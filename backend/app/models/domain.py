"""
AyuRaksha Core Domain Models (SIH 26045)
Strongly typed Pydantic v2 domain schemas defining clean architectural contracts
across all 10 modules: Data, Embeddings, Retrieval, Reranking, Generation,
Citations, Guardrails, Knowledge, Evaluation, and Orchestration.
"""
from __future__ import annotations
from enum import Enum
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Enums
# ============================================================================

class JurisdictionEnum(str, Enum):
    IN = "IN"
    INT = "INT"
    US = "US"
    EU = "EU"
    CROSS_BORDER = "CROSS_BORDER"


class DocumentTypeEnum(str, Enum):
    ACT = "ACT"
    RULE = "RULE"
    REGULATION = "REGULATION"
    TREATY = "TREATY"
    GAZETTE_NOTIFICATION = "GAZETTE_NOTIFICATION"
    TAXONOMY = "TAXONOMY"


class RetrievalModality(str, Enum):
    VECTOR = "VECTOR"
    KEYWORD = "KEYWORD"
    GRAPH = "GRAPH"
    COMPOSITE = "COMPOSITE"


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"


class AbstentionCode(str, Enum):
    INSUFFICIENT_STATUTORY_GROUNDING = "INSUFFICIENT_STATUTORY_GROUNDING"
    BIOPIRACY_CIRCUMVENTION_DETECTED = "BIOPIRACY_CIRCUMVENTION_DETECTED"
    DRUGS_MAGIC_REMEDIES_VIOLATION = "DRUGS_MAGIC_REMEDIES_VIOLATION"
    OUT_OF_REGULATORY_SCOPE = "OUT_OF_REGULATORY_SCOPE"


# ============================================================================
# 1. Statutory & Corpus Hierarchy Models
# ============================================================================

class SourceDocument(BaseModel):
    """Represents an official primary legal source (Act, Rule, Regulation, Treaty)."""
    model_config = ConfigDict(from_attributes=True)

    source_id: str = Field(..., description="Canonical unique identifier, e.g. IND_PATENTS_ACT_1970")
    title: str = Field(..., description="Full official statutory title")
    short_title: str = Field(..., description="Short conversational title")
    authority: str = Field(..., description="Issuing/Enforcing statutory authority")
    jurisdiction: JurisdictionEnum = Field(default=JurisdictionEnum.IN)
    document_type: DocumentTypeEnum = Field(default=DocumentTypeEnum.ACT)
    authority_level: int = Field(default=5, ge=1, le=5, description="Legal hierarchy tier (1-5)")
    official_url: Optional[str] = Field(None, description="Official government gazette or portal URL")
    current_status: str = Field(default="ACTIVE", description="ACTIVE, AMENDED, or REPEALED")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DocumentVersion(BaseModel):
    """Represents a specific gazetted amendment or consolidated version of a source document."""
    model_config = ConfigDict(from_attributes=True)

    version_id: str = Field(..., description="Unique version identifier")
    source_id: str = Field(..., description="Foreign key reference to SourceDocument")
    version_label: str = Field(..., description="Version label, e.g. 2024 Consolidated or G.S.R. 211(E)")
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    content_hash: str = Field(..., description="Cryptographic SHA-256 digest of raw document file")
    storage_uri: Optional[str] = None


class Provision(BaseModel):
    """Atomic statutory section, rule, article, or schedule provision."""
    model_config = ConfigDict(from_attributes=True)

    provision_id: str = Field(..., description="Canonical provision identifier, e.g. PATENTS_ACT_1970_SEC_003_P")
    source_id: str = Field(..., description="Owning source identifier")
    section_number: str = Field(..., description="Section or rule number, e.g. 3(p), Rule 122E, Article 3")
    heading: Optional[str] = Field(None, description="Official section heading")
    text: str = Field(..., description="Verbatim statutory text")
    chapter: Optional[str] = Field(None, description="Chapter or Part descriptor")
    statutory_significance: Optional[str] = Field(None, description="Legal impact summary")
    topics: List[str] = Field(default_factory=list)


class CorpusChunk(BaseModel):
    """Atomic searchable chunk indexed into dense vector and sparse lexical databases."""
    model_config = ConfigDict(from_attributes=True)

    chunk_id: str = Field(..., description="Unique chunk identifier")
    source_id: str = Field(..., description="Associated SourceDocument identifier")
    section_number: Optional[str] = Field(None, description="Associated section or rule number")
    text: str = Field(..., description="Searchable textual content")
    raw_statute: Optional[str] = Field(None, description="Verbatim authentic excerpt")
    jurisdiction: JurisdictionEnum = Field(default=JurisdictionEnum.IN)
    authority_level: int = Field(default=4, ge=1, le=5)
    chunk_hash: str = Field(..., description="SHA-256 digest of chunk content")
    token_count: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# 2. Retrieval, Evidence & Citation Models
# ============================================================================

class Evidence(BaseModel):
    """Factual statutory excerpt retrieved by vector, lexical, or graph engines."""
    model_config = ConfigDict(from_attributes=True)

    evidence_id: str = Field(..., description="Unique evidence identifier")
    source_id: str = Field(..., description="Owning legal source ID")
    source_title: str = Field(..., description="Official title of the statute/treaty")
    section_number: str = Field(..., description="Section/Rule number")
    verbatim_text: str = Field(..., description="Exact statutory text")
    authority: Optional[str] = Field(None, description="Issuing authority")
    authority_level: int = Field(default=4, ge=1, le=5)
    jurisdiction: JurisdictionEnum = Field(default=JurisdictionEnum.IN)
    provision: Optional[str] = Field(None, description="Formal provision identifier")
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    retrieval_modality: RetrievalModality = Field(default=RetrievalModality.COMPOSITE)
    official_url: Optional[str] = None
    document_sha256: Optional[str] = None
    verification_status: str = Field(default="VERIFIED", description="VERIFIED, PARTIALLY_SUPPORTED, or UNVERIFIED")


class EvidencePack(BaseModel):
    """Canonical grouped statutory evidence package delivered to UI and generator."""
    model_config = ConfigDict(from_attributes=True)

    primary_statutes: List[Evidence] = Field(default_factory=list, description="Primary Acts (e.g. Patents Act, BDA, DCA)")
    implementing_rules: List[Evidence] = Field(default_factory=list, description="Subordinate Rules and Regulations")
    international_treaties: List[Evidence] = Field(default_factory=list, description="International Treaties and Directives")
    regulatory_guidelines: List[Evidence] = Field(default_factory=list, description="Guidelines, Standards, and FSSAI notifications")
    total_count: int = Field(default=0)


class Citation(BaseModel):
    """User-facing, verifiable legal citation attached to an answer or claim."""
    model_config = ConfigDict(from_attributes=True)

    citation_id: str = Field(..., description="Reference token, e.g. CIT-001")
    source_id: str = Field(..., description="Canonical source ID")
    source_title: str = Field(..., description="Short official name of the statute/treaty")
    section: str = Field(..., description="Statutory section, rule, or article")
    subsection: Optional[str] = Field(None, description="Clause or sub-clause")
    authority: str = Field(default="Statutory Authority")
    authority_level: int = Field(default=5, ge=1, le=5)
    verbatim_quote: str = Field(..., description="Exact unedited statutory excerpt")
    official_url: str = Field(..., description="Verifiable government portal link")
    document_sha256: str = Field(..., description="Cryptographic hash proving document integrity")
    support_score: float = Field(default=1.0, ge=0.0, le=1.0)


# ============================================================================
# 3. Knowledge Graph Models
# ============================================================================

class GraphEntity(BaseModel):
    """Domain entity within the Ayurvedic IP and regulatory graph."""
    model_config = ConfigDict(from_attributes=True)

    entity_id: str = Field(..., description="Canonical entity key")
    name: str = Field(..., description="Entity display name")
    entity_type: str = Field(..., description="BOTANICAL, CLASSICAL_TEXT, STATUTE_SECTION, FORMULATION")
    aliases: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphRelationship(BaseModel):
    """Directed semantic edge connecting two graph entities."""
    model_config = ConfigDict(from_attributes=True)

    relationship_id: str = Field(..., description="Unique edge identifier")
    subject_id: str = Field(..., description="Source entity ID")
    predicate: str = Field(..., description="GOVERNS, AMENDED_BY, FOUND_IN, CONTRAINDICATED_IN, ALIGNED_WITH")
    object_id: str = Field(..., description="Target entity ID")
    statutory_basis: Optional[str] = Field(None, description="Legal provision justifying the relationship")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


# ============================================================================
# 4. Query, Response & Confidence Models
# ============================================================================

class RetrievalResult(BaseModel):
    """Composite output of the multi-modal retrieval engine."""
    model_config = ConfigDict(from_attributes=True)

    query: str = Field(..., description="Input search query")
    jurisdiction: JurisdictionEnum = Field(default=JurisdictionEnum.IN)
    candidates: List[Evidence] = Field(default_factory=list)
    modalities_used: List[RetrievalModality] = Field(default_factory=list)
    total_candidates_found: int = Field(default=0)
    latency_ms: float = Field(default=0.0)


class Confidence(BaseModel):
    """Multi-dimensional evaluation of response reliability."""
    model_config = ConfigDict(from_attributes=True)

    level: ConfidenceLevel = Field(default=ConfidenceLevel.HIGH)
    score: float = Field(default=0.9, ge=0.0, le=1.0)
    grounding_rate: float = Field(default=1.0, ge=0.0, le=1.0)
    caveats: List[str] = Field(default_factory=list)


class AbstentionReason(BaseModel):
    """Controlled taxonomy for safe model abstention when statutory criteria are not met."""
    model_config = ConfigDict(from_attributes=True)

    code: AbstentionCode = Field(...)
    description: str = Field(..., description="Plain-English explanation")
    remedial_action: str = Field(..., description="Suggested corrective action for applicant")


class ClaimVerificationResult(BaseModel):
    """Sentence-level factual verification record."""
    model_config = ConfigDict(from_attributes=True)

    claim: str = Field(..., description="Decomposed sentence claim")
    is_supported: bool = Field(default=True)
    confidence_score: float = Field(default=0.9, ge=0.0, le=1.0)
    supporting_citations: List[Citation] = Field(default_factory=list)


class RAGResponse(BaseModel):
    """Final synthesized, verified regulatory assessment delivered to the user."""
    model_config = ConfigDict(from_attributes=True)

    query: str = Field(..., description="Original user query")
    jurisdiction: JurisdictionEnum = Field(default=JurisdictionEnum.IN)
    detected_intent: str = Field(default="REGULATORY_INQUIRY")
    direct_answer: str = Field(..., description="Multi-paragraph legal guidance with citations")
    assessment_table: Dict[str, Any] = Field(default_factory=dict)
    citations: List[Citation] = Field(default_factory=list)
    verified_claims: List[ClaimVerificationResult] = Field(default_factory=list)
    cross_border_posture: Optional[Dict[str, str]] = None
    next_actions: List[str] = Field(default_factory=list)
    confidence: Confidence = Field(default_factory=Confidence)
    safe_abstention: bool = Field(default=False)
    abstention_reason: Optional[AbstentionReason] = None
    language: str = Field(default="en")
    execution_mode: str = Field(default="GUIDED_RAG", description="DIRECT_STATUTORY, GUIDED_RAG, or MULTI_HOP_PLANNER")
    resolved_concepts: List[str] = Field(default_factory=list, description="Detected legal concept tags")
    evidence_pack: Optional[EvidencePack] = None
    trace_id: Optional[str] = None
    diagnostics: Dict[str, Any] = Field(default_factory=dict, description="Internal retrieval diagnostics")
    latency_breakdown: Dict[str, float] = Field(default_factory=dict, description="Stage latencies in milliseconds")
