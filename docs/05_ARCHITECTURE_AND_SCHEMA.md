# AyuRaksha — System Architecture, Database Schema & Decision Records

**Document:** 05_ARCHITECTURE_AND_SCHEMA.md  
**Product:** AyuRaksha (आयुसुरक्षा)  
**Version:** 2.0 (Consolidated)  
**Status:** Canonical Technical Architecture & Data Specification  

---

## 1. System Architecture Overview

AyuRaksha is engineered as a **Modular Monolith** with strict interface boundaries, zero microservice network latency, and pluggable AI providers:

```
                                [Client: React 18 + Vite + TypeScript]
                                                 │
                                                 │ (SSE Streaming / REST API)
                                                 ▼
                                  [FastAPI Asynchronous Gateway]
                                                 │
             ┌───────────────────────────────────┼───────────────────────────────────┐
             │                                   │                                   │
             ▼                                   ▼                                   ▼
   [Tri-Retrieval Engine]             [Deterministic Engines]             [Knowledge Graph]
   ├── Dense: pgvector (HNSW)          ├── Product Classifier              ├── SVG Canvas
   ├── Sparse: Postgres GIN            └── ABS Compliance Wizard           └── Multi-Hop Links
   └── Local: all-MiniLM-L6-v2                                                  (STATIC_GRAPH)
             │
             ▼
   [Reciprocal Rank Fusion & Domain Reranker]
             │
             ▼
   [Pluggable Generation Gateway]
   ├── Priority 1: Google Gemini 2.5 Flash (~500ms via Google AI Studio)
   └── Priority 2: OpenRouter Failover (99.9% Uptime)
             │
             ▼
   [Citation Provenance & Entailment Engine]
```

---

## 2. Database Schema (Neon Serverless PostgreSQL + `pgvector`)

### 2.1 `sources` (Statutory Instruments & Repositories)
```sql
CREATE TABLE sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_code VARCHAR(64) UNIQUE NOT NULL,      -- e.g. 'IND_PATENTS_ACT_1970'
    title TEXT NOT NULL,
    short_title VARCHAR(128),
    authority VARCHAR(256) NOT NULL,              -- e.g. 'Office of the CGPDTM'
    authority_level INT DEFAULT 5,                -- 5=Act, 4=Rule/Form, 3=Taxonomy
    jurisdiction VARCHAR(8) NOT NULL DEFAULT 'IN',-- 'IN', 'INT', 'CROSS_BORDER'
    document_type VARCHAR(32) NOT NULL,           -- 'ACT', 'RULES', 'FORM', 'TREATY'
    effective_date DATE,
    official_url TEXT,
    sha256_hash VARCHAR(64),                      -- SHA-256 of authentic Gazette
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sources_jurisdiction ON sources(jurisdiction);
CREATE INDEX idx_sources_doc_type ON sources(document_type);
```

### 2.2 `legal_provisions` (Atomic Statutory Chunks)
```sql
CREATE TABLE legal_provisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES sources(id) ON DELETE CASCADE,
    provision_id VARCHAR(64) UNIQUE NOT NULL,     -- e.g. 'IN-PA-S3-p'
    section_number VARCHAR(64) NOT NULL,          -- e.g. 'Section 3(p)'
    heading TEXT,
    full_text TEXT NOT NULL,
    verbatim_quote TEXT,
    authority_level INT DEFAULT 5,
    domain VARCHAR(64),                           -- 'PATENTS_AND_IP', 'DRUGS_AND_COSMETICS'
    embedding vector(384),                        -- Dense MiniLM embedding
    tsv_content tsvector,                         -- Full-text GIN search vector
    ayurveda_relevance VARCHAR(32),               -- 'Critical', 'High', 'Medium', 'None'
    tk_relevance VARCHAR(32),                     -- 'Critical', 'High', 'Medium', 'None'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fast HNSW cosine similarity search index
CREATE INDEX idx_provisions_embedding ON legal_provisions 
USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

-- Full-text GIN search index for BM25/lexical retrieval
CREATE INDEX idx_provisions_tsv ON legal_provisions USING gin(tsv_content);
CREATE INDEX idx_provisions_section ON legal_provisions(section_number);
```

### 2.3 `knowledge_relations` (Relational Graph Topology)
```sql
CREATE TABLE knowledge_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    subject_source_id UUID REFERENCES sources(id),
    subject_label VARCHAR(128) NOT NULL,
    relation_type VARCHAR(64) NOT NULL,           -- 'CODIFIED_IN', 'TRIGGERS_BAR', 'OPPOSED_VIA'
    target_source_id UUID REFERENCES sources(id),
    target_label VARCHAR(128) NOT NULL,
    rationale TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 2.4 `patent_forms` (Official CGPDTM Filing Registry)
```sql
CREATE TABLE patent_forms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    form_number VARCHAR(32) UNIQUE NOT NULL,      -- 'Form 7A', 'Form 25'
    form_title TEXT NOT NULL,
    purpose TEXT NOT NULL,
    related_section_or_rule TEXT,                 -- 'Section 25(1); Rule 55'
    source_url TEXT,
    verification_status VARCHAR(32) DEFAULT 'Verified IP India',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 3. Knowledge Graph Engine & Relational Topology

In Ayurvedic regulatory affairs, legal determination is inherently multi-hop:
$$\text{Botanical} \xrightarrow{\text{Codified in}} \text{Classical Text} \xrightarrow{\text{Triggers Bar}} \text{Patents Act § 3(p)} \xrightarrow{\text{Enforced by}} \text{Form 7A Pre-Grant Opposition}$$

### Node Taxonomy
- 🌿 **Medicinal Biological Resources** (*Withania somnifera*, *Curcuma longa*, *Bacopa monnieri*, *Tinospora cordifolia*, *Picrorhiza kurroa*)
- 📜 **First Schedule Classical Books** (*Charaka Samhita*, *Sushruta Samhita*, *Bhaishajya Ratnavali*, *Ashtanga Hridaya*)
- ⚖️ **Statutory Sections** (Sections 3(p), 3(e), 10(4), 25(1)(k), 39, Rule 158B)
- 📝 **Official Filing Forms** (Patent Forms 1, 7A, 18A, 25, 27; NBA Form III)
- 🌍 **International Treaties** (WIPO GRATK Treaty 2024 Article 3)

---

## 4. Key Architecture Decision Records (ADRs)

| ADR | Title | Decision & Impact |
| :--- | :--- | :--- |
| **ADR-001** | Modular Monolith over Microservices | Co-locates API, retrievers, and decision engines in FastAPI. Zero serialization latency, unified debugging, single-process deployment. |
| **ADR-002** | Pluggable LLM Generation Gateway | Abstracts LLM behind `IGenerator`. Provides automatic circuit-breaker failover between Google AI Studio and OpenRouter. |
| **ADR-003** | Tri-Retrieval and Reciprocal Rank Fusion | Fuses dense vector embeddings, GIN full-text search, and statutory graph expansion. Prevents recall failures on legal numbers. |
| **ADR-004** | Strongly Typed Domain Contracts | All payloads enforced through Pydantic v2 schemas and TypeScript interfaces, ensuring compile-time safety across boundaries. |
| **ADR-005** | Cryptographic Gazette Provenance | Every primary legal citation links to a verified SHA-256 Gazette checksum, guaranteeing zero fabrication. |
| **ADR-006** | Direct Gemini 2.5 Flash & Local Embeddings | Pre-warms `SentenceTransformer` in RAM with `local_files_only=True` (~15ms) and queries Gemini 2.5 Flash directly, reducing TTFT from 5.5s to **~500ms**. |
| **ADR-007** | Zero-Dependency SVG Knowledge Graph Canvas | Uses native SVG and React state with Framer Motion. Zero external charting bundle weight, 60 FPS smooth physics. |
