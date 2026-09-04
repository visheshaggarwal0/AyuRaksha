# AyuRaksha (आयुरक्षा)

### **AI-Powered IP & Regulatory Navigator for Ayurvedic Innovation**
*Built for Smart India Hackathon (Problem Statement #26045: IP-SAKTI Sahayak)*  
*Sponsored by the Ministry of Ayush & All India Institute of Ayurveda (AIIA)*

---

## 🌟 Overview

**AyuRaksha** is an authoritative, citation-grounded decision-support platform engineered to help Ayurvedic innovators, researchers, startups, MSMEs, Vaidyas, and patent attorneys navigate the complex convergence of:
- **Traditional Knowledge Exclusions**: Section 3(p), 3(c), and 3(e) of the Indian Patents Act, 1970.
- **Biodiversity & Benefit Sharing**: Sections 3, 6, and 7 of the Biological Diversity Act, 2002 (as amended 2023).
- **ASU Drug Licensing vs Food Boundaries**: Drugs & Cosmetics Act 1940 (Rule 158B) vs FSSAI Ayurveda Aahara Regulations 2022 (Regulation 5 disease claim prohibitions).
- **Procedural Filing Routing**: Instant guidance on official CGPDTM forms (Form 1, 7A, 18A, 25, 27) and NBA Form I/III.

> **Ask → Classify → Research → Verify → Act**

---

## 🚀 Key Features

### 1. Ultra-Fast Copilot Chat (~500ms TTFT)
- Powered by **Google Gemini 2.5 Flash** with direct AI Studio routing and automatic OpenRouter failover.
- Real-time Server-Sent Events (SSE) streaming with multi-stage progress badges (`TRI_RETRIEVAL`, `RERANKING`, `GENERATION`, `CITATION_PROVENANCE`).
- Zero legal hallucination with mandatory citation grounding against authentic Gazette checksums.

### 2. Interactive Statutory Knowledge Graph Visualizer
- Native SVG force-directed interactive topology canvas.
- Connects **28 nodes** across Botanicals, First Schedule Classical Books, Statutory Sections, Official Filing Forms, and WIPO Treaties.
- Real-time node search, category cluster filtering, smooth dragging, and a sliding legal inspector drawer with Gazette links.

### 3. Product Classification Decision Wizard
- Deterministic 4-tier decision tree evaluating:
  - **Classical ASU Drug** (§ 3(a), First Schedule 56 texts, Form 25D).
  - **Patent / Proprietary ASU Medicine** (§ 3(h), Rule 158B safety dossier).
  - **Phytopharmaceutical Drug** (CDSCO Rule 122E, Form CT-18 + clinical trials).
  - **FSSAI Ayurveda Aahara** (FoSCoS registration, strictly barred from disease claims).

### 4. ABS Compliance Check
- Evaluates Indian vs foreign applicant pathways under the **Biological Diversity Act 2002/2023**.
- Automatically checks Section 7 SBB exemptions for registered Ayush practitioners.
- Identifies mandatory **NBA Form III** approval triggers before patent grants under Section 6.

### 5. IP Opportunity Matrix
- Multi-dimensional assessment across Patents, Trademarks (Nice Class 5 vs 30), Trade Secrets, GIs, Copyright, and Plant Variety Protection (PPV&FR).

### 6. Active Compliance Dossier
- One-click exportable regulatory audit trail with cryptographic SHA-256 Gazette hashes ready for state licensing authority submission.

---

## 🏗️ Architecture & Tech Stack

```
                                [Client: React 18 + Vite + TypeScript]
                                                 │
                                                 │ (SSE / REST API)
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
```

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | React 18, Vite, TypeScript, Tailwind CSS, Framer Motion | High-performance, accessible regulatory workspace |
| **Backend** | Python 3.11+, FastAPI (Async), Pydantic v2 | High-throughput streaming API and decision trees |
| **Database** | Neon Serverless PostgreSQL 16+ with `pgvector` | Unified relational metadata, GIN indices & vector embeddings |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` | Fast 384-dimensional vector embeddings cached in RAM (~15ms) |
| **Primary LLM** | Google Gemini 2.5 Flash (`v1beta`) | High-speed, high-context generation (~500ms TTFT) |
| **Fallback LLM**| OpenRouter Gateway | Instant circuit-breaker failover |

---

## ⚡ Quick Start

### Prerequisites
- **Node.js**: v18.0 or higher
- **Python**: v3.11 or higher
- **PostgreSQL**: Local instance or free [Neon Serverless PostgreSQL](https://neon.tech)

### 1. Clone & Configure Environment
```bash
git clone https://github.com/visheshaggarwal0/AyuRaksha.git
cd AyuRaksha

# Copy and update environment variables
cp .env.example .env
```
Key `.env` variables:
```ini
DATABASE_URL=postgresql://user:password@ep-sample-123456.us-east-2.aws.neon.tech/neondb?sslmode=require
GEMINI_API_KEY=your_google_ai_studio_api_key
OPENROUTER_API_KEY=your_openrouter_api_key  # Optional fallback
```

### 2. Backend Setup
```bash
# Navigate to backend
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI development server with hot-reload
uvicorn app.main:app --reload --port 8000
```
Interactive Swagger API documentation will be live at: `http://localhost:8000/docs`.

### 3. Frontend Setup
```bash
# Open a new terminal and navigate to frontend
cd frontend

# Install npm packages
npm install

# Start Vite development server
npm run dev
```
Open your browser at: `http://localhost:5173`.

---

## 📖 Centralized Documentation Hub

All product specifications, technical architectures, interaction designs, and regulatory guides are consolidated directly in the [`docs/`](./docs/README.md) directory:

| Document | File Link | Core Content |
| :--- | :--- | :--- |
| **SIH Presentation Truth (Master Source)** | [`docs/SIH_PRESENTATION_TRUTH.md`](./docs/SIH_PRESENTATION_TRUTH.md) | Authoritative single source of truth for presentation claims, verified benchmarks, 19-source corpus, and ranked USPs. |
| **Product Requirements (PRD)** | [`docs/01_PRD.md`](./docs/01_PRD.md) | Product vision, target user personas, problem statement, core capabilities, and success metrics. |
| **Technical Requirements (TRD)** | [`docs/02_TRD.md`](./docs/02_TRD.md) | Architecture principles, technology stack, dataflow pipeline, latency optimizations, and security models. |
| **App Flow & Journeys** | [`docs/03_APP_FLOW.md`](./docs/03_APP_FLOW.md) | Screen map, information architecture, and core user journeys (Inquiry, Classification, ABS, Matrix, Dossier). |
| **UI/UX Design Specification** | [`docs/04_UIUX_SPEC.md`](./docs/04_UIUX_SPEC.md) | Editorial design ethos, color tokens, typography, Framer Motion spring physics, and custom component specifications. |
| **Architecture & Database Schema** | [`docs/05_ARCHITECTURE_AND_SCHEMA.md`](./docs/05_ARCHITECTURE_AND_SCHEMA.md) | Modular monolith diagram, Neon Serverless PostgreSQL + `pgvector` tables, Knowledge Graph engine, and key ADR summaries. |
| **Regulatory & Innovation Guide** | [`docs/06_REGULATORY_AND_INNOVATION_GUIDE.md`](./docs/06_REGULATORY_AND_INNOVATION_GUIDE.md) | Detailed analysis of Patents Act 1970/2024, DCA 1940, BDA 2023, FSSAI 2022, WIPO GRATK Treaty 2024, and official forms. |
| **Master Documentation Index** | [`docs/README.md`](./docs/README.md) | Central Documentation Hub Index & Quick Navigation Portal. |

---

## 🏆 SIH 26045 Golden Evaluation Scorecard
*Evaluated against `data/evaluation/benchmark_200.jsonl` (105 curated golden statutory scenarios) using `scripts/run_eval_benchmark.py`:*

| Evaluation Metric | Target Threshold | AyuRaksha Measured Benchmark | Status |
| :--- | :---: | :---: | :---: |
| **Jurisdiction Leakage Rate (JLR)** | 0.00% | **0.00%** (Zero cross-border contamination) | **PASSED** |
| **Safe Abstention Accuracy** | 100.00% | **100.00%** (8/8 biopiracy & illegal cure queries intercepted) | **PASSED** |
| **Citation Grounding Precision** | ≥ 90.00% | **100.00%** (All citations grounded in authentic Gazette text) | **EXCEEDED** |
| **Statutory Citation Recall** | ≥ 85.00% | **90.59%** (85/94 required statutory provisions retrieved) | **PASSED** |
| **P50 Inference Latency** | < 3.00s | **2.42s** (Median end-to-end multi-stage pipeline) | **PASSED** |
| **P95 Inference Latency** | < 6.00s | **5.97s** (Tail latency under complex multi-hop planning) | **PASSED** |

---

## 📜 License & Compliance

Built for the **Smart India Hackathon (SIH Problem Statement #26045: IP-SAKTI Sahayak)** under the auspices of the **Ministry of Ayush** and **All India Institute of Ayurveda (AIIA)**.  
*Disclaimer: AyuRaksha is an AI-powered regulatory and IP decision-support system. It is designed to assist innovators and practitioners and does not constitute formal legal counsel.*
