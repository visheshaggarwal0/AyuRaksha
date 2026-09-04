# AyuRaksha — SIH Presentation Truth (Problem Statement #26045: IP-SAKTI Sahayak)
*Authoritative Single Source of Truth for System Architecture, Capabilities, Benchmarks, and Claims*

---

## 1. Problem
Ayurvedic innovation in India operates at a perilous intersection of four divergent legal and regulatory regimes:
1. **Traditional Knowledge Patent Exclusions**: Section 3(p), 3(c), and 3(e) of the Indian Patents Act, 1970 strictly bar patenting traditional knowledge, natural products, and mere admixtures lacking proven synergistic technical advance.
2. **Biodiversity & Benefit Sharing (ABS) Mandates**: The Biological Diversity Act, 2002 (amended 2023) imposes strict approval requirements (NBA Form I/III for foreign entities, SBB Section 7 prior intimation for domestic commercialization) with penal liabilities for unauthorized commercial exploitation of Indian bio-resources.
3. **ASU Drug Licensing vs Food/Nutraceutical Boundaries**: Formulations must navigate the razor-thin boundary between Classical ASU Drugs (Section 3(a) & First Schedule 56 texts), Proprietary ASU Medicines (Rule 158B), CDSCO Phytopharmaceuticals (Rule 122E / GSR 918(E)), and FSSAI Ayurveda Aahara Regulations 2022 (prohibiting therapeutic disease claims).
4. **International Treaty Compliance**: Foreign market entry requires aligning domestic access records with US FDA 21 CFR Part 111 (DSHEA NDI 75-day notification), EU Directive 2004/24/EC (30-year traditional use rule), and the newly ratified **WIPO GRATK Treaty 2024** (mandatory disclosure of country of origin in patent specifications).

Innovators, Vaidyas, startups, and MSMEs currently face fragmented legal advice, accidental biopiracy risks, unpatentable claim rejections, and export border seizures due to lack of a unified statutory navigator.

---

## 2. Solution
**AyuRaksha (आयुसुरक्षा)** is an authoritative, citation-grounded, multi-agent statutory decision engine designed specifically for Ayurvedic innovation. 

Rather than functioning as a free-form conversational LLM, AyuRaksha combines:
- **Deterministic Statutory Decision Trees** for product licensing classification and Biological Diversity Act ABS pathfinding.
- **Tri-Retrieval Engine** (Dense pgvector + Sparse Lexical tsvector + Relational Statutory Graph) fused via Reciprocal Rank Fusion (RRF) with a 5-tier statutory authority hierarchy.
- **Pre-Generation Safety Guardrails** that enforce non-negotiable safe abstention against biopiracy evasion and illegal magic cure claims.
- **Post-Generation Sentence-Level Directional Entailment Verification** that verifies every assertion against authentic Gazette text checksums.
- **Audit-Ready Active Compliance Dossier Generation** mapping full evidentiary provenance for State Licensing Authorities (SLA), CDSCO, NBA, and the Indian Patent Office (CGPDTM).

---

## 3. Target Users
1. **Ayurvedic Startups, Innovators & D2C Brands**: Need rapid clarity on whether their formulation is a Classical ASU Drug, Proprietary Medicine, Phytopharmaceutical, or Ayurveda Aahara food supplement.
2. **Ayurvedic Researchers, Formulators & Pharma R&D**: Need to know how to overcome Section 3(p) TK bars by establishing synergistic efficacy exceeding mere admixture under Section 3(e).
3. **Vaidyas & Traditional AYUSH Practitioners**: Need accessible guidance in Hindi or Sanskrit on Section 7 SBB exemptions and traditional medicine compounding boundaries.
4. **Patent Attorneys & AYUSH IP Facilitators**: Need 1-click audit dossiers with Gazette citations, SHA-256 provenance hashes, and statutory form requirements (CGPDTM Forms 1, 3, 18, 27; NBA Forms I, III, A).
5. **State Licensing Authorities (SLA) & Regulators**: Need standardized statutory checklists verifying compliance with Schedule T GMP, Rule 158B proof of effectiveness, and BDA benefit-sharing compliance.

---

## 4. Core User Journey
```
[User Input: Formulation / Regulatory Query / Market Intent]
                         │
                         ▼
       [1. Digital India Bhashini Language Gateway]
       ├── Devanagari Hindi / Sanskrit Script Detection
       └── Statutory Lexicon Normalization
                         │
                         ▼
       [2. Pre-Retrieval Safety & Guardrail Firewall]
       ├── Check 1: Biopiracy Evasion / Illegal Smuggling Filter
       ├── Check 2: Drugs & Magic Remedies 1954 Prohibited Disease Claims
       └── If Adversarial -> SAFE ABSTENTION & Facilitator Escalation Brief
                         │
                         ▼
       [3. Execution Mode Determination]
       ├── Mode A: DIRECT_STATUTORY (Exact Section/Rule Lookup)
       ├── Mode B: GUIDED_RAG (Standard Compliance Evaluation)
       └── Mode C: MULTI_HOP_PLANNER (Cross-Border / Multi-Pillar Decomposition)
                         │
                         ▼
       [4. Tri-Retrieval & Reciprocal Rank Fusion]
       ├── Dense Stream: Neon pgvector (HNSW Cosine Similarity)
       ├── Sparse Stream: PostgreSQL GIN tsvector / Section Regex Index
       ├── Graph Stream: Relational Knowledge Graph Traversal
       └── RRF Merging with 5-Tier Statutory Authority Weighting
                         │
                         ▼
       [5. Grounded Legal Synthesis]
       ├── Primary: Google Gemini 2.5 Flash / Gemma 4 31B
       └── Fallback: Pluggable Gateway (OpenRouter / Local Ollama / Deterministic Engine)
                         │
                         ▼
       [6. Post-Generation Directional Entailment Verification]
       ├── Sentence-level Decomposition & Term Overlap Checking
       ├── Polarity Reversal & High-Stakes Legal Assertion Guardrails
       └── Calibrated Confidence Scoring (High / Moderate / Low + Caveats)
                         │
                         ▼
       [7. Output Generation & User Presentation]
       ├── Structured Decision Brief (Direct Answer, Assessment Table, Next Actions)
       ├── Interactive Citations (Verbatim Quotes, Official URLs, SHA-256 Hashes)
       ├── Right Slide-Over Evidence Inspector Drawer
       └── 1-Click Exportable Active Compliance Dossier
```

---

## 5. Actual Technical Architecture
- **Architecture Style**: Modular Monolith (10 decoupled logical domain contracts behind formal Python Abstract Base Classes with zero internal microservice overhead).
- **Frontend**: React 18, Vite, TypeScript, Tailwind CSS, Lucide Icons, Framer Motion animations.
- **Backend API**: FastAPI (Python 3.10+ async), Pydantic v2 schemas, Server-Sent Events (SSE) streaming.
- **Database & Storage**: Neon Serverless PostgreSQL 16+ with `pgvector` extension and GIN full-text indexes.
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors).
- **LLM Gateway**: Pluggable multi-provider architecture with automatic circuit breaker failover:
  - Priority 1: Google Gemini 2.5 Flash (Google AI Studio)
  - Priority 2: Gemma 4 31B / Llama 3.3 70B (OpenRouter)
  - Priority 3: Local Ollama (Local/Offline deployment)
  - Priority 4: Deterministic Statutory Rule Synthesizer (Zero-network fallback)

---

## 6. Actual Retrieval Architecture ("Tri-Retrieval")
AyuRaksha's retrieval system combines three independent retrieval modalities executed concurrently and merged via Reciprocal Rank Fusion:
1. **Dense Semantic Retrieval**: Executes HNSW cosine similarity search over 384-dimensional MiniLM-L6-v2 embeddings stored in Neon `pgvector`.
2. **Sparse Lexical Retrieval**: Executes PostgreSQL GIN full-text `tsvector` matching combined with exact statutory section regular expression parsing (`3(p)`, `158B`, `122E`, `CT-18`).
3. **Relational Statutory Graph Retrieval**: Traverses codified statutory relationships (`KnowledgeRelation`) connecting parent Acts to implementing Rules, statutory forms, and classical treatise First Schedule references (e.g. Patents Act § 3(p) ↔ First Schedule Treatises ↔ BDA § 6).
4. **Reciprocal Rank Fusion (RRF) with Authority Weighting**: Candidates are ranked using $RRF = \sum \frac{1}{60 + \text{rank}} + \text{AuthorityBoost}$, where Level 5 Primary Acts outrank Level 4 Rules and Level 3 Guidelines, preventing secondary documents from crowding out primary law.

---

## 7. Actual Regulatory Decision Engines
AyuRaksha contains deterministic legal decision engines that run independently of LLMs:
1. **Product Classifier (`ProductClassifier`)**:
   - **Classical Ayurvedic Medicine (Shastriya)**: Governed under Drugs & Cosmetics Act § 3(a) & First Schedule; strictly barred from patentability under Patents Act § 3(p); requires Form 25D manufacturing license.
   - **Phytopharmaceutical Drug**: Governed under CDSCO Rule 122E / GSR 918(E) & New Drugs Rules 2019; requires min. 4 standardized bioactive markers, CTD chemical fingerprinting, Form CT-18, and Phase I-III clinical trials; potentially patentable under § 2(1)(j).
   - **Patent / Proprietary ASU Medicine (Anubhuta)**: Governed under Rule 158B & § 3(h); potentially patentable if synergistic technical advance exceeding mere admixture is proven under § 3(e).
   - **Ayurveda Aahara (Food Supplement)**: Governed under FSSAI Regulations 2022 (Schedule A); strictly prohibited from making disease prevention or cure claims under Regulation 5.
   - **Ayurvedic Cosmetics**: Governed under Cosmetics Rules 2020.
2. **ABS Compliance Decision Tree (`ABSDecisionTree`)**:
   - **Foreign Entities / Non-Indian Participation / Export Intent**: Triggers mandatory National Biodiversity Authority (NBA Chennai) Prior Approval on Form I under Section 3, mandatory benefit-sharing agreement, and Form III approval prior to patent grant under Section 6.
   - **Indian Citizens / Domestic MSMEs**: Triggers State Biodiversity Board (SBB) Prior Intimation on Form A under Section 7, with automatic statutory checks for 2023 amendment exemptions (cultivated medicinal plants and registered Ayush practitioners).
3. **Safety & Abstention Guardrail Engine (`SafetyGuardrailEngine`)**:
   - Intercepts biopiracy evasion attempts, illegal extraction instructions, fee evasion loopholes, and prohibited disease cure claims under the Drugs and Magic Remedies Act 1954.

---

## 8. Actual Trust / Verification Layer
1. **Sentence-Level Claim Verification (`ModularEvaluationEngine`)**: Decomposes legal synthesis into atomic sentences and computes term-overlap and directional entailment against cited statutory evidence.
2. **Directional Entailment & Polarity Firewall**: Checks for ungrounded high-stakes assertions (e.g. falsely claiming GI tags or blanket immunity) and polarity reversals (claiming an activity is freely permitted when the statute prohibits it).
3. **Calibrated Multi-Dimensional Confidence Scoring**:
   $$\text{Confidence Score} = (\text{Grounding Rate} \times 0.7) + (\min(1.0, \frac{\text{Candidates}}{3}) \times 0.3)$$
   - $\ge 80\% \rightarrow \text{HIGH}$
   - $55\% - 79\% \rightarrow \text{MODERATE}$
   - $< 55\% \rightarrow \text{LOW}$ (accompanied by explicit statutory caveats)
4. **Verbatim Quotation Integrity**: Citations display authentic verbatim statutory text directly extracted from primary legislation.
5. **Cryptographic SHA-256 Provenance**: Every citation carries the SHA-256 hash of the authentic Gazette publication.

---

## 9. Actual Knowledge Corpus
- **Total Searchable Chunks**: **1,493 atomic chunks**
- **Total Unique Primary Sources**: **19 authoritative statutory instruments**:
  1. *The Patents Act, 1970* (as amended, with § 3(p), 3(c), 3(e), 3(d), 10(4), 25(1), 39)
  2. *The Patents Rules, 2003*
  3. *The Patents (Amendment) Rules, 2024* (Form 3, Rule 12, Rule 24B RFE acceleration, Form 27 triennial cycles)
  4. *Official CGPDTM Patent Forms* (Forms 1, 2, 3, 5, 7A, 18, 18A, 25, 27)
  5. *The Biological Diversity Act, 2002* (Sections 3, 4, 6, 7, 19, 21, 23, 24)
  6. *The Biological Diversity (Amendment) Act, 2023* (Decriminalization, Ayush practitioner & cultivated plant exemptions)
  7. *National Biodiversity Authority (NBA) ABS Regulations, 2014 & Forms* (Forms I, II, III, IV, A)
  8. *The Drugs and Cosmetics Act, 1940 (ASU Provisions)* (Sections 3(a), 3(h), 33EEB, 33N)
  9. *The Drugs and Cosmetics Rules, 1945 (ASU Provisions)* (Rule 158B, Rule 122E / GSR 918(E), Schedule T GMP)
  10. *First Schedule Authoritative Classical Ayurvedic Books* (56 statutory treatises including Charaka Samhita, Sushruta Samhita, Ashtanga Hridaya, Sharangadhara Samhita, Bhavaprakasha, Bhashejyaratnavali)
  11. *FSSAI (Ayurveda Aahara) Regulations, 2022* (Regulations 3, 5, 6, 8, 9 & Schedule A)
  12. *The Geographical Indications of Goods Act, 1999*
  13. *The Trade Marks Act, 1999 (Nice Classification Class 5 vs Class 30)*
  14. *The Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954*
  15. *WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge (GRATK), 2024* (Article 3 Mandatory Disclosure of Origin)
  16. *US FDA 21 CFR Part 111 & DSHEA 1994 (Botanical Dietary Supplement Guidelines)*
  17. *EU Directive 2004/24/EC (Traditional Herbal Medicinal Products Directive - THMPD)*
  18. *TKDL Ayurvedic Glossary (421 terms & disease classifications)*
  19. *TKDL Botanical Taxonomy (333 medicinal plant taxa with Sanskrit names & scientific binomials)*

---

## 10. Actual Technologies
- **Language**: Python 3.10+, TypeScript 5.0+
- **Frontend Stack**: React 18, Vite 6, Tailwind CSS 3, Lucide React, Framer Motion
- **Backend Stack**: FastAPI, Uvicorn, Pydantic v2, SQLAlchemy 2 (Async), Asyncpg, HTTPX
- **Database Layer**: Neon Serverless PostgreSQL, `pgvector`, GIN Indexing
- **AI Models & Libraries**: Sentence-Transformers (`all-MiniLM-L6-v2`), Google GenAI SDK (`gemini-2.5-flash`), OpenRouter Gateway (`gemma-4-31b-it`, `llama-3.3-70b-instruct`)
- **Evaluation & Testing**: Pytest, Pytest-Asyncio, Custom Golden Benchmark Harness

---

## 11. Actual Unique Differentiators (Ranked USPs)

### USP 1 (P1 — Strongest Differentiator)
- **NAME**: Unified Multi-Pillar Ayurvedic Regulatory & IP Convergence Engine
- **WHAT IS ACTUALLY IMPLEMENTED**: Single unified evaluation pipeline connecting Patentability (§ 3(p) TK bar / § 3(e) synergy), Biodiversity ABS (NBA Form I/III vs SBB § 7), Drug Licensing (Classical vs Modified Rule 158B vs Phytopharmaceutical Rule 122E), and Food Safety (FSSAI 2022).
- **CODE / MODULE**: `backend/app/engines/classifier.py`, `backend/app/engines/abs_tree.py`, `backend/app/modules/orchestration/__init__.py`.
- **WHY IT IS UNIQUE**: General AI answers legal questions in isolation. AyuRaksha executes the statutory cross-walk across all four governing statutes simultaneously.
- **HOW TO EXPLAIN IT TO A JUDGE**: "If you bring a new Ashwagandha extract, ChatGPT doesn't know that modifying the extraction changes your licensing from AYUSH Shastriya to CDSCO Rule 122E, triggers NBA Form III before patent grant, and bars FSSAI food claims. AyuRaksha solves this four-way legal collision deterministically."

### USP 2 (P2 — Second Strongest)
- **NAME**: Tri-Retrieval with Authority Hierarchy & Reciprocal Rank Fusion
- **WHAT IS ACTUALLY IMPLEMENTED**: Simultaneous Dense Vector (pgvector) + Sparse Lexical (tsvector / section regex) + Relational Statutory Graph traversal, fused with RRF and 5-tier statutory authority weighting.
- **CODE / MODULE**: `backend/app/modules/retrieval/composite.py`, `vector.py`, `keyword.py`, `graph.py`.
- **WHY IT IS UNIQUE**: Eliminates the legal section hallucinations common in pure vector search while expanding semantic synonyms and enforcing primary statutory precedence.
- **HOW TO EXPLAIN IT TO A JUDGE**: "We do not rely on standard embedding similarity alone. Our Tri-Retrieval merges vector semantics, exact section numbers, and relational statutory graphs so primary legislation always outranks secondary commentary."

### USP 3 (P3 — Supporting)
- **NAME**: Pre-Generation Guardrails & Sentence-Level Directional Entailment Verification
- **WHAT IS ACTUALLY IMPLEMENTED**: Pre-retrieval biopiracy evasion & magic cure filter + post-generation sentence claim decomposition, polarity reversal checks, and calibrated confidence grading.
- **CODE / MODULE**: `backend/app/modules/guardrails/`, `backend/app/modules/evaluation/`, `backend/app/engines/safety.py`.
- **WHY IT IS UNIQUE**: Prevents adversarial circumvention of biodiversity laws and guarantees that every displayed sentence is factually grounded in authentic Gazette text.
- **HOW TO EXPLAIN IT TO A JUDGE**: "AyuRaksha cannot be jailbroken to assist in biopiracy. Every output is split into sentences and mathematically verified against cited Gazette text before reaching the user."

### USP 4 (P4 — Supporting)
- **NAME**: Dual-Pane Cross-Border & International Regulatory Navigator (WIPO GRATK 2024 / US FDA / EU THMPD)
- **WHAT IS ACTUALLY IMPLEMENTED**: Synchronized dual-pane posture comparing Indian domestic requirements (NBA Form I, Patent § 39 FFL) with destination export markets (US FDA 21 CFR 111, EU 2004/24/EC, WIPO GRATK Treaty 2024 Article 3 mandatory disclosure).
- **CODE / MODULE**: `backend/app/modules/orchestration/__init__.py`, `frontend/src/components/international/InternationalView.tsx`.
- **WHY IT IS UNIQUE**: First platform to incorporate the May 2024 WIPO Treaty on Genetic Resources and Associated Traditional Knowledge into domestic Ayurvedic export routing.
- **HOW TO EXPLAIN IT TO A JUDGE**: "Exporting Ayurvedic formulations requires satisfying both Indian ABS laws and foreign FDA/EU regulations. AyuRaksha provides dual-pane domestic vs international posture analysis including the new 2024 WIPO Genetic Resources Treaty."

### USP 5 (P5 — Supporting)
- **NAME**: Statutory Lexicon-Preserving Multilingual Gateway (Digital India Bhashini)
- **WHAT IS ACTUALLY IMPLEMENTED**: Language detection and translation across English, Hindi, and Sanskrit with dedicated bilingual statutory dictionaries preserving exact section numbers and classical treatise names.
- **CODE / MODULE**: `backend/app/ai/multilingual/bhashini.py`, `frontend/src/i18n/`.
- **WHY IT IS UNIQUE**: Generic machine translation mangles legal sections and Ayurvedic Sanskrit terminology. AyuRaksha preserves authentic statutory identifiers across languages.
- **HOW TO EXPLAIN IT TO A JUDGE**: "Vaidyas in rural India think in Hindi and Sanskrit. Our Bhashini integration translates complex regulatory guidance while keeping legal section numbers and Ayurvedic treatise names 100% accurate."

---

## 12. Why It Is Different From Generic RAG
| Dimension | Generic RAG Chatbot | AyuRaksha Decision Engine |
| :--- | :--- | :--- |
| **Decision Logic** | Purely probabilistic text generation | Deterministic rule trees (Classifier, ABS) + RAG synthesis |
| **Retrieval Architecture** | Single dense vector search | Tri-Retrieval (Dense + Sparse + Statutory Graph) + RRF |
| **Statutory Hierarchy** | Treats all chunks equally | 5-tier authority weighting (Primary Acts > Rules > Taxonomy) |
| **Section Pinpointing** | Frequent hallucination of section numbers | Exact regex indexing + verified Gazette quotes |
| **Adversarial Safety** | Basic conversational safety filters | Non-negotiable Biopiracy Evasion & Magic Remedies filters |
| **Output Trust** | Unverified text block | Sentence-level claim verification + Grounding Rate + Confidence |
| **Actionability** | Generic advice ("Consult a lawyer") | Exact statutory forms (Form 1, Form 3, CT-18, NBA Form I/III) |
| **Export Readiness** | Unaware of international treaties | Built-in WIPO GRATK 2024, US FDA DSHEA, and EU THMPD routing |
| **Auditability** | No persistent audit trail | Cryptographic SHA-256 provenance + 1-click Compliance Dossier |

---

## 13. Actual Benchmarks
*Evaluated on `data/evaluation/benchmark_200.jsonl` (105 curated golden statutory scenarios) using `scripts/run_eval_benchmark.py`:*

| Metric | Target | AyuRaksha Measured | Explanation |
| :--- | :---: | :---: | :--- |
| **Jurisdiction Leakage Rate (JLR)** | $0.00\%$ | **0.00%** | Zero leakage of foreign regulations into domestic Indian legal queries. |
| **Safe Abstention Accuracy** | $100.00\%$ | **100.00%** | 8/8 adversarial biopiracy and illegal cure prompts safely intercepted and refused. |
| **Citation Grounding Precision** | $\ge 90.00\%$ | **100.00%** | 100% of emitted citations match authentic verbatim Gazette text with positive support. |
| **Statutory Citation Recall** | $\ge 85.00\%$ | **90.59%** | Successfully retrieved 85 out of 94 mandatory required statutory provisions. |
| **P50 Inference Latency** | $< 3.00\text{s}$ | **2.42s** | Median end-to-end multi-stage pipeline latency. |
| **P95 Inference Latency** | $< 6.00\text{s}$ | **5.97s** | 95th-percentile tail latency under complex multi-hop planning. |

---

## 14. Actual Limitations
1. **Corpus Scope**: Currently covers 19 primary statutory frameworks (1,493 chunks). Does not yet ingest state-specific AYUSH licensing circulars for all 28 Indian states.
2. **Offline OCR**: Complex historical handwritten palm-leaf manuscripts are referenced via TKDL metadata rather than raw image OCR.
3. **Legal Disclaimer**: AyuRaksha is a statutory decision-support tool and compliance accelerator; formal legal filings require review by an empaneled patent attorney or State Licensing Authority officer.

---

## 15. Actual Feasibility
- **Zero Heavy Infrastructure Dependency**: Operates efficiently on Neon Serverless PostgreSQL with in-memory embedding caches; does not require high-cost multi-GPU clusters.
- **Fast Local & Edge Readiness**: Can run completely offline using Local Ollama and in-memory deterministic synthesis when internet access is unavailable in remote AYUSH centers.
- **Immediate Ministry Adoption**: Formatted directly to integrate into the Ministry of Ayush's AYUSH Grid and CGPDTM's IP-SAKTI portal.

---

## 16. Actual Impact
- **Reduces Classification Time from Weeks to Seconds**: Instant determination of ASU Shastriya vs Rule 158B vs Phytopharmaceutical status.
- **Prevents Costly Biopiracy Penalties**: Ensures full ABS compliance before commercialization or patent application.
- **Accelerates Patent Filings**: Generates structured Form 1/3/18A roadmaps and identifies Section 3(e) experimental evidence needs upfront.
- **Protects Global Exports**: Avoids customs seizures and patent disputes by ensuring compliance with WIPO GRATK 2024 and US FDA DSHEA.

---

## 17. Research / Legal Sources
- *The Patents Act, 1970 (Act No. 39 of 1970)*
- *The Patents (Amendment) Rules, 2024 (Gazette Notification G.S.R. 211(E))*
- *The Biological Diversity Act, 2002 (Act No. 18 of 2003) & Biological Diversity (Amendment) Act, 2023 (Act No. 10 of 2023)*
- *The Drugs and Cosmetics Act, 1940 & Drugs and Cosmetics Rules, 1945 (including Gazette G.S.R. 918(E) Phytopharmaceuticals)*
- *Food Safety and Standards (Ayurveda Aahara) Regulations, 2022 (F. No. Stds/SP-05/A-1.2022)*
- *WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge, May 24, 2024*
- *Ayurvedic Pharmacopoeia of India (API) & First Schedule to the Drugs and Cosmetics Act, 1940*

---

## 18. Claims Allowed in Presentation
- "Tri-Retrieval combining dense pgvector search, sparse keyword search, and relational statutory knowledge graphs."
- "Deterministic 4-tier product classification under Drugs & Cosmetics Act, Rule 158B, CDSCO Phytopharmaceuticals, and FSSAI Ayurveda Aahara."
- "100% Safe Abstention on tested adversarial biopiracy and illegal cure queries."
- "100% Citation Grounding Precision on golden benchmark scenarios with authentic Gazette verbatim text."
- "90.59% Statutory Citation Recall across 105 curated golden evaluation scenarios."
- "Dual-Pane cross-border compliance navigator incorporating the 2024 WIPO GRATK Treaty."
- "Digital India Bhashini multilingual gateway preserving statutory section lexicons in Hindi and Sanskrit."
- "1,493 atomic statutory chunks across 19 primary legal instruments with cryptographic SHA-256 provenance."

---

## 19. Claims That Must NOT Be Made (Prohibited Claims)
- ❌ **DO NOT claim "0.00% Zero Hallucination" unconditionally**: Claim instead "100% Citation Grounding Precision on tested benchmark scenarios via sentence-level directional entailment verification."
- ❌ **DO NOT claim "100% Statutory Citation Recall"**: The actual measured recall is **90.59%** (85/94 provisions retrieved on 105 test cases).
- ❌ **DO NOT claim "Real-time automatic continuous Gazette web scraper"**: The extraction pipeline is an authentic validated offline/batch pipeline, not a live web scraper daemon.
- ❌ **DO NOT claim "200 tested scenarios"**: The golden benchmark suite has **105 curated scenarios**.
- ❌ **DO NOT claim "Replaces patent attorneys or State Licensing Authorities"**: Frame it accurately as an "AI-powered regulatory decision engine and compliance co-pilot for innovators and attorneys."
