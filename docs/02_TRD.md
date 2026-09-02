# AyuRaksha — Technical Requirements Document (TRD)

**Document:** 02_TRD.md  
**Product:** AyuRaksha (आयुसुरक्षा)  
**Version:** 2.0 (Consolidated)  
**Status:** Canonical Engineering Specification  

---

## 1. Architectural Philosophy

1. **Retrieval-First, Generation-Second**: The Large Language Model (LLM) is strictly restricted from synthesizing statutory guidance ungrounded. Generation is constrained exclusively to verified evidence chunks retrieved from the authoritative legal corpus.
2. **Deterministic Rules Over Generative Hallucination**: Regulatory classification (Classical vs Proprietary vs Phytopharm vs Ayurveda Aahara) and ABS compliance (Form I vs Form III vs SBB intimation) execute on deterministic decision trees.
3. **Multi-Modal Tri-Retrieval**: Dense semantic embeddings alone fail on verbatim section numbers and obscure botanical binomials. Tri-retrieval fuses:
   - Dense vector embeddings (cosine similarity via `pgvector` HNSW).
   - Sparse lexical search (PostgreSQL GIN full-text `tsvector`).
   - Relational statutory graph traversal (`GraphRetriever`).
4. **Offline Resilience & Zero Network Cold-Starts**: Embedding models load strictly from local RAM caches (`local_files_only=True`), avoiding runtime HTTP HEAD requests to Hugging Face Hub.
5. **Circuit-Breaker LLM Fallback**: Primary generation queries `gemini-2.5-flash` directly via Google AI Studio (~500ms TTFT); automatically fails over to OpenRouter upon any HTTP failure.

---

## 2. Technology Stack Breakdown

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend Web** | React 18 + Vite + TypeScript | High-speed rendering, strict type safety, zero runtime overhead |
| **Styling & Motion** | Tailwind CSS + Lucide Icons + Framer Motion | Government-grade editorial visual language with 60 FPS spring animations |
| **Backend API** | Python 3.11+ + FastAPI (Async) | Native async I/O, OpenAPI auto-generation, high-concurrency SSE streaming |
| **Relational & Vector DB** | Neon Serverless PostgreSQL + `pgvector` | Serverless autoscaling, pooled connections, HNSW indexing & GIN indices |
| **Embedding Engine** | `sentence-transformers/all-MiniLM-L6-v2` | Lightweight 384-dimensional vector encoding pre-warmed in RAM (~15ms) |
| **Knowledge Graph** | Pure React + SVG + Force-Directed Layout | Zero-bundle-overhead interactive canvas with real-time coordinate recalculation |
| **Primary LLM** | Google Gemini 2.5 Flash (`v1beta`) | Direct AI Studio integration delivering ~500ms TTFT and 3,000-token capacity |
| **Fallback LLM Gateway** | OpenRouter (`gemini-2.5-flash`, `llama-3.3-70b`) | Circuit breaker ensuring 99.9% uptime during API quota or network issues |

---

## 3. Detailed Dataflow & Processing Pipeline

```
User Query (Chat / Classification / ABS)
             │
             ▼
      [Stage 1: Query Normalization]
      ├── Language Detection (EN / HI / SA)
      ├── Jurisdiction Isolation (IN / INT / Cross-Border)
      └── Domain Intent Classification (DCA, Patents, BDA, FSSAI)
             │
             ▼
      [Stage 2: Tri-Retrieval Engine]
      ├── Dense Vector Search: Neon pgvector HNSW (top 10 candidates)
      ├── Sparse Lexical Search: PostgreSQL GIN tsvector (top 10 candidates)
      └── Relational Graph Search: STATIC_STATUTORY_GRAPH multi-hop expansion
             │
             ▼
      [Stage 3: Reciprocal Rank Fusion & Domain Reranking]
      ├── RRF Fusion: RRF_Score = sum(w_m / (60 + rank_m))
      ├── Domain-Intent Score Adjustments:
      │     +0.25 bonus for DCA/FSSAI on classification queries
      │     -0.35 penalty for Trade Marks on drug questions
      └── Deduplication on (source_id, section_number)
             │
             ▼
      [Stage 4: Pluggable Generation Gateway]
      ├── Priority 1: GeminiProvider (gemini-2.5-flash via Google AI Studio ~500ms)
      └── Priority 2: OpenRouterProvider (Failover Gateway on HTTP error)
             │
             ▼
      [Stage 5: Citation Provenance & Entailment Engine]
      ├── Sentence-level claim verification against retrieved evidence
      ├── Cryptographic SHA-256 Gazette checksum cross-referencing
      └── Real-time Server-Sent Events (SSE) streaming to client
```

---

## 4. Latency Optimization & Cold-Start Elimination

Early testing revealed a 5.5-second response latency caused by two compounding factors:
1. **Hugging Face Hub Checks**: `SentenceTransformer` was making remote HEAD requests on every invocation checking for `adapter_config.json 404`, adding ~1.2s.
   - *Fix*: Pre-warmed `SentenceTransformer` in FastAPI's `lifespan` startup with `local_files_only=True`. Embedding now runs in **~15ms in RAM**.
2. **Sequential Model Failover**: The backend was testing 9 legacy model names sequentially before reaching a valid endpoint.
   - *Fix*: Discovered `gemini-2.5-flash` via `v1beta` is provisioned on the user's AI Studio key. Established `gemini-2.5-flash` as Candidate #1. The very first POST request succeeds in **~500ms**, eliminating 4.5s of retry delay.

---

## 5. Security, Provenance & Integrity

1. **Cryptographic Gazette Provenance**: Every primary statute chunk is tied to a SHA-256 hash computed directly from authentic Gazette PDFs downloaded from `egazette.gov.in` and `indiacode.nic.in`.
2. **Strict Authority Hierarchy**:
   - Level 5: Primary Parliamentary Acts (Patents Act, BDA, DCA).
   - Level 4: Statutory Subordinate Rules & Official Forms (Patents Rules, Rule 158B, Form 7A).
   - Level 3: Authoritative First Schedule Books & TKDL Taxonomic Records.
3. **Zero-Hallucination Circuit Breakers**: If candidate evidence relevance scores fall below $0.65$ or contradictory statutory provisions exist, the system triggers mandatory abstention and provides a human escalation brief.
