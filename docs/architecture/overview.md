# AyuRaksha Architecture Overview

AyuRaksha (IP-SAKTI Sahayak — SIH Problem Statement 26045) is an authoritative, multilingual, source-grounded regulatory navigation platform for Ayurvedic innovation across national and international legal regimes.

---

## 1. Architectural Style: Modular Monolith

AyuRaksha adheres strictly to a **Modular Monolith** pattern. All components reside within a unified codebase, share zero-cost in-memory data structures where appropriate, and interact through strictly typed interfaces. 

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FRONTEND (React 18)                                  │
│                 Wizards (Classification, ABS)  │  Chat & Active Dossier                 │
└────────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │ HTTP / JSON
┌────────────────────────────────────────────▼────────────────────────────────────────────┐
│                                   FASTAPI ROUTER (/api/v1)                              │
│         /chat/query  │  /classification/evaluate  │  /abs/evaluate  │  /corpus/*        │
└────────────────────────────────────────────┬────────────────────────────────────────────┘
                                             │
┌────────────────────────────────────────────▼────────────────────────────────────────────┐
│                                    ORCHESTRATION LAYER                                  │
│                 Coordinates the 10 core modules with complete trace audit               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                     10 CORE MODULES                                     │
│                                                                                         │
│  ┌──────────────────────┐  ┌──────────────────────┐  ┌───────────────────────────────┐  │
│  │         DATA         │  │      EMBEDDINGS      │  │           RETRIEVAL           │  │
│  │  Manifests, Chunks,  │  │  Dense Vectorizers   │  │  Vector, Keyword (BM25),      │  │
│  │  Statutes & Gazettes │  │  (SentenceTransform) │  │  Graph Retrieval (Independent)│  │
│  └──────────┬───────────┘  └──────────┬───────────┘  └───────────────┬───────────────┘  │
│             │                         │                              │                  │
│  ┌──────────▼───────────┐  ┌──────────▼───────────┐  ┌───────────────▼───────────────┐  │
│  │       RERANKING      │  │      KNOWLEDGE       │  │          GENERATION           │  │
│  │  Authority Hierarchy │  │  TKDL Taxonomy,      │  │  Provider-Agnostic Gateway    │  │
│  │  & Reciprocal Fusion │  │  Plants & Entities   │  │  (Gemini, Groq, Local Ollama) │  │
│  └──────────┬───────────┘  └──────────┬───────────┘  └───────────────┬───────────────┘  │
│             │                         │                              │                  │
│  ┌──────────▼───────────┐  ┌──────────▼───────────┐  ┌───────────────▼───────────────┐  │
│  │      GUARDRAILS      │  │      CITATIONS       │  │          EVALUATION           │  │
│  │  Biopiracy Gate,     │  │  Sentence Mapping,   │  │  Entailment Verification,     │  │
│  │  Safe Abstention     │  │  SHA-256 Provenance  │  │  Grounding Rate Calibration   │  │
│  └──────────────────────┘  └──────────────────────┘  └───────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Principles & Boundaries

1. **Deterministic Precedence**: Primary statutory exclusions (Patents Act Section 3(p), Drugs & Cosmetics Rule 158B, CDSCO Rule 122E Phytopharmaceuticals) are governed by rule engines. LLMs synthesize contextual guidance and explanation, but never override statutory bars.
2. **Strict Jurisdiction Isolation**: India Domestic law (BDA 2002, Patents Act 1970) and International Regimes (WIPO GRATK Treaty 2024, US FDA DSHEA, EU THMPD) are maintained as separate postures and never conflated.
3. **Cryptographic Provenance**: Every citation carries a verifiable SHA-256 digest computed from the raw statute or Gazette file on disk.
4. **Provider-Agnostic Generation**: Upstream LLM providers (Gemini, Groq, Ollama, OpenRouter) can be swapped without touching business logic.
5. **Independent Tri-Retrieval**: Dense vector search, sparse keyword search, and knowledge graph retrieval can be tested, executed, and evaluated independently.
