# AyuRaksha — Backend Schema & Data Model

## 1. Database

Primary database: PostgreSQL.

Vector extension: pgvector.

Graph database: optional Neo4j in V2.

## 2. Users

### `users`

| Column             | Type      | Notes                               |
|--------------------|-----------|-------------------------------------|
| id                 | UUID      | PK                                  |
| email              | VARCHAR   | Unique, nullable for anonymous mode |
| name               | VARCHAR   | Optional                            |
| role               | ENUM      | USER/FACILITATOR/REVIEWER/ADMIN     |
| preferred_language | VARCHAR   | ISO-like code                       |
| created_at         | TIMESTAMP |                                     |
| updated_at         | TIMESTAMP |                                     |
| status             | ENUM      | ACTIVE/SUSPENDED/DELETED            |

## 3. User Preferences

### `user_preferences`

- user_id PK/FK
- theme
- language
- analytics_consent
- conversation_retention
- notification_preferences

## 4. Sessions

### `sessions`

- id UUID PK
- user_id FK
- title
- jurisdiction
- language
- created_at
- updated_at
- archived_at

## 5. Messages

### `messages`

- id UUID PK
- session_id FK
- role
- content
- model
- model_version
- created_at
- safety_status

Do not store sensitive content unnecessarily.

## 6. Sources

### `sources`

- id UUID PK
- title
- authority
- document_type
- jurisdiction
- source_url
- publication_date
- effective_from
- effective_to
- current_status
- content_hash
- retrieved_at
- version_label
- authority_level

## 7. Source Versions

### `source_versions`

- id UUID PK
- source_id FK
- version_label
- effective_from
- effective_to
- content_hash
- storage_uri
- ingestion_run_id
- created_at

This allows historical retrieval.

## 8. Sections

### `source_sections`

- id UUID PK
- source_version_id FK
- parent_section_id FK nullable
- section_number
- heading
- text
- page_start
- page_end

## 9. Chunks

### `document_chunks`

- id UUID PK
- section_id FK
- text
- embedding VECTOR
- token_count
- language
- metadata JSONB
- created_at

Indexes: - vector index; - full-text index; - jurisdiction; - source
authority; - document type.

## 10. Legal Entities

### `legal_entities`

- id UUID PK
- type
- canonical_name
- aliases JSONB
- jurisdiction
- metadata JSONB

Types:

- ACT
- RULE
- REGULATION
- TREATY
- AUTHORITY
- SECTION
- CASE
- PRODUCT_CATEGORY
- IP_RIGHT
- BIOLOGICAL_RESOURCE
- TK_CONCEPT
- COUNTRY

## 11. Entity Relationships

### `entity_relationships`

- id UUID PK
- source_entity_id FK
- relationship_type
- target_entity_id FK
- source_section_id FK nullable
- confidence
- created_at

Examples:

- contains;
- amended_by;
- administered_by;
- applies_to;
- related_to;
- supersedes;
- interpreted_by;
- may_require;
- associated_with.

## 12. Products

### `products`

- id UUID PK
- user_id FK
- name
- description
- intended_use
- target_market
- created_at
- updated_at

Avoid storing exact proprietary formulation details unless necessary.

## 13. Product Facts

### `product_facts`

- id UUID PK
- product_id FK
- fact_type
- value_encrypted
- source
- confidence
- created_at

Sensitive fields should be encrypted.

## 14. Product Classifications

### `product_classifications`

- id UUID PK
- product_id FK
- category
- confidence
- rationale
- status
- engine_version
- created_at

## 15. IP Assessments

### `ip_assessments`

- id UUID PK
- product_id FK
- ip_type
- applicability
- confidence
- rationale
- created_at

## 16. ABS Assessments

### `abs_assessments`

- id UUID PK
- product_id FK nullable
- biological_resource
- origin
- purpose
- commercial_use
- traditional_knowledge
- foreign_involvement
- assessment
- confidence
- engine_version
- created_at

Sensitive provenance data should be protected.

## 17. Assessment Evidence

### `assessment_evidence`

- id UUID PK
- assessment_type
- assessment_id
- source_section_id
- support_score
- created_at

## 18. Export Assessments

### `export_assessments`

- id UUID PK
- product_id FK
- destination_country
- destination_region
- purpose
- result
- confidence
- created_at

## 19. Answers

### `answers`

- id UUID PK
- message_id FK
- jurisdiction
- intent
- confidence
- risk_level
- answer_text
- engine_version
- created_at

## 20. Claims

### `answer_claims`

- id UUID PK
- answer_id FK
- claim_text
- claim_type
- support_status
- support_score
- created_at

## 21. Citations

### `citations`

- id UUID PK
- claim_id FK
- source_section_id FK
- citation_text
- support_score
- authority_level
- created_at

## 22. Feedback

### `feedback`

- id UUID PK
- user_id FK nullable
- answer_id FK
- rating
- category
- comment
- created_at

## 23. Escalation Cases

### `cases`

- id UUID PK
- user_id FK
- title
- status
- priority
- summary
- assigned_to FK nullable
- created_at
- updated_at

### `case_sources`

- case_id FK
- source_id FK

## 24. Audit Logs

### `audit_logs`

- id UUID PK
- actor_id FK nullable
- action
- resource_type
- resource_id
- metadata JSONB
- ip_hash
- created_at

Never log raw sensitive product formulations.

## 25. Ingestion

### `ingestion_runs`

- id UUID PK
- source_id FK
- status
- started_at
- completed_at
- error
- document_hash

## 26. Roles

### USER

Can: - ask questions; - create journeys; - view own cases; - delete own
data.

### FACILITATOR

Can: - view assigned cases; - review evidence; - add notes.

### REVIEWER

Can: - review corpus; - validate source mappings; - review evaluation
cases.

### ADMIN

Can: - manage users; - manage roles; - manage corpus; - inspect system
metrics.

## 27. Security Rules

1.  Users can access only their own sessions/products/cases.
2.  Facilitators access only assigned cases.
3.  Corpus administration requires reviewer/admin role.
4.  Source documents are read-only to normal users.
5.  Audit logs are append-only.
6.  Sensitive product facts are encrypted.
7.  Data deletion must cascade or anonymise according to retention
    policy.
8.  API authorisation must be enforced server-side, never only in the
    client.
9.  Administrative endpoints must require stronger authentication.
10. Uploaded documents must be malware-scanned and content-type
    validated.

## 28. Relationships

``` text
User
 ├── Sessions
 │    └── Messages
 │          └── Answers
 │                └── Claims
 │                      └── Citations
 │                            └── Source Sections
 │
 ├── Products
 │    ├── Product Facts
 │    ├── Classification
 │    ├── IP Assessments
 │    ├── ABS Assessments
 │    └── Export Assessments
 │
 └── Cases
      └── Case Sources

Source
 └── Versions
      └── Sections
           └── Chunks
```
