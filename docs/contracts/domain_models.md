# AyuRaksha Domain Model Contracts

This document specifies the 12 strongly typed core domain models that govern data flow across all modules in AyuRaksha.

---

## 1. Statutory & Corpus Hierarchy

### `SourceDocument`
Represents an official primary legal source (Act, Rule, Regulation, Treaty, or Gazette Notification).
- `source_id`: Canonical unique identifier (e.g. `IND_PATENTS_ACT_1970`, `INT_WIPO_GRATK_TREATY_2024`).
- `title`: Full statutory title.
- `short_title`: Concise conversational name.
- `authority`: Enforcing regulatory body (e.g. `Intellectual Property India`, `CDSCO`, `NBA`).
- `jurisdiction`: Regulatory regime (`IN`, `INT`, `US`, `EU`, `CROSS_BORDER`).
- `document_type`: Legal classification (`ACT`, `RULE`, `REGULATION`, `TREATY`, `GAZETTE_NOTIFICATION`).
- `authority_level`: Hierarchy integer 1 to 5 (5 = Primary Act / Treaty, 4 = Rules, 3 = Guidelines / Taxonomy).
- `official_url`: Canonical government source URL.
- `current_status`: Status indicator (`ACTIVE`, `AMENDED`, `REPEALED`).

### `DocumentVersion`
Represents a specific gazetted amendment or consolidation version of a source document.
- `version_id`: Unique version identifier.
- `source_id`: Foreign key reference to `SourceDocument`.
- `version_label`: Version descriptor (e.g. `2024 Consolidated`, `G.S.R. 211(E)`).
- `effective_from`: Date the provision took legal force.
- `effective_to`: Date superseded (optional).
- `content_hash`: Cryptographic SHA-256 digest of the raw document file.
- `storage_uri`: Internal blob or disk storage path.

### `Provision`
Atomic statutory section, rule, article, or clause within a document version.
- `provision_id`: Canonical identifier (e.g. `PATENTS_ACT_1970_SEC_003_P`).
- `source_id`: Owning source identifier.
- `section_number`: Statutory number (e.g. `3(p)`, `Rule 122E`, `Article 3.1`).
- `heading`: Official title of the section.
- `text`: Verbatim authentic statutory text.
- `chapter`: Chapter or Part descriptor.
- `statutory_significance`: High-level legal impact summary.
- `topics`: Normalized thematic tags.

### `CorpusChunk`
Searchable atomic chunk indexed into dense vector and sparse lexical databases.
- `chunk_id`: Unique chunk identifier.
- `source_id`: Owning legal source identifier.
- `section_number`: Associated section or rule number.
- `text`: Clean chunk content.
- `raw_statute`: Exact verbatim statutory excerpt.
- `jurisdiction`: Legal regime.
- `authority_level`: Legal hierarchy weight.
- `chunk_hash`: SHA-256 digest of the chunk text.
- `embedding`: Optional 384-dimensional dense vector.
- `token_count`: Estimated token size.

---

## 2. Retrieval, Evidence & Citation Models

### `Evidence`
Factual statutory excerpt retrieved to support generation and audit.
- `evidence_id`: Unique identifier.
- `source_id`: Reference source.
- `source_title`: Human-readable legal source name.
- `section_number`: Applicable section.
- `verbatim_text`: Exact statutory quote.
- `authority_level`: Source tier (1–5).
- `relevance_score`: Normalized similarity / RRF score (0.0 to 1.0).
- `retrieval_modality`: Origin retrieval engine (`VECTOR`, `KEYWORD`, `GRAPH`, `COMPOSITE`).

### `Citation`
User-facing, verifiable legal citation attached to an answer or claim.
- `citation_id`: Reference token (e.g. `CIT-001`).
- `source_id`: Canonical source identifier.
- `source_title`: Short legal name.
- `section`: Specific statutory section or rule.
- `subsection`: Clause or paragraph if applicable.
- `authority`: Governing agency.
- `authority_level`: Legal weight.
- `verbatim_quote`: Exact unedited statutory excerpt.
- `official_url`: Verified government portal URL.
- `document_sha256`: Cryptographic hash proving document integrity.
- `support_score`: Factual entailment score (0.0 to 1.0).

---

## 3. Knowledge Graph Models

### `GraphEntity`
Domain entity within the Ayurvedic IP and regulatory graph.
- `entity_id`: Canonical entity key.
- `name`: Display name (e.g. `Ashwagandha`, `Withania somnifera`, `Charaka Samhita`).
- `entity_type`: Category (`BOTANICAL`, `CLASSICAL_TEXT`, `FORMULATION`, `STATUTE_SECTION`, `DISEASE_INDICATION`).
- `aliases`: Vernacular and botanical synonyms.
- `metadata`: Key-value domain attributes.

### `GraphRelationship`
Directed semantic edge connecting two graph entities.
- `relationship_id`: Unique relationship ID.
- `subject_id`: Origin entity identifier.
- `predicate`: Relationship type (`GOVERNS`, `AMENDED_BY`, `FOUND_IN`, `CONTRAINDICATED_IN`, `ALIGNED_WITH`).
- `object_id`: Destination entity identifier.
- `statutory_basis`: Legal provision justifying the relationship.
- `confidence`: Confidence score (0.0 to 1.0).

---

## 4. Query, Response & Confidence Models

### `RetrievalResult`
Composite output of the multi-modal retrieval engine.
- `query`: Input search query.
- `jurisdiction`: Target jurisdiction.
- `candidates`: List of retrieved `Evidence` objects.
- `modalities_used`: Active retrieval engines utilized.
- `total_candidates_found`: Pre-reranking candidate count.
- `latency_ms`: Search execution time.

### `Confidence`
Multi-dimensional evaluation of response reliability.
- `level`: Discrete confidence grade (`HIGH`, `MODERATE`, `LOW`).
- `score`: Calibrated numerical score (0.0 to 1.0).
- `grounding_rate`: Percentage of claims supported by citations.
- `caveats`: Specific legal limitations or pending evidentiary requirements.

### `AbstentionReason`
Controlled taxonomy for safe model abstention when statutory criteria are not met.
- `code`: Enumerated cause:
  - `INSUFFICIENT_STATUTORY_GROUNDING`
  - `BIOPIRACY_CIRCUMVENTION_DETECTED`
  - `DRUGS_MAGIC_REMEDIES_VIOLATION`
  - `OUT_OF_REGULATORY_SCOPE`
- `description`: Plain-English explanation.
- `remedial_action`: Suggested corrective action for the applicant.

### `RAGResponse`
The final synthesized, verified regulatory assessment delivered to the user.
- `query`: Original user query.
- `jurisdiction`: Resolved jurisdiction (`IN`, `INT`, `CROSS_BORDER`).
- `detected_intent`: Primary user intent.
- `direct_answer`: Multi-paragraph legal guidance.
- `assessment_table`: Structured tabular statutory matrix.
- `citations`: List of verifiable `Citation` objects.
- `verified_claims`: Sentence-level claim verification records.
- `cross_border_posture`: Isolated domestic vs destination market compliance obligations.
- `next_actions`: Actionable compliance milestones (e.g. Forms, CDSCO dossiers).
- `confidence`: `Confidence` assessment object.
- `safe_abstention`: Boolean indicating whether safety guardrails triggered an abstention.
- `abstention_reason`: Optional `AbstentionReason` if abstained.
- `language`: Output language (`en`, `hi`, `sa`, `ta`).
