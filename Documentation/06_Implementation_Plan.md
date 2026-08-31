# AyuRaksha — Implementation Plan

## 1. Delivery Strategy

Build vertically, not by isolated components.

The first working slice must be:

> User question → India jurisdiction → authoritative retrieval → answer
> → exact citation → verification → confidence.

Everything else builds on that.

## 2. Phase 0 — Product & Architecture

### Deliverables

- PRD;
- TRD;
- app flow;
- UI system;
- database schema;
- API contract;
- corpus strategy;
- evaluation specification.

### Exit criteria

The whole team can explain the system architecture and MVP boundary.

## 3. Phase 1 — Corpus Foundation

### Work

1.  Identify authoritative sources.
2.  Download/ingest.
3.  Hash documents.
4.  Parse.
5.  Extract hierarchy.
6.  Store metadata.
7.  Chunk by legal structure.
8.  Embed.
9.  Build retrieval index.
10. Create source viewer.

### Testing

- extraction correctness;
- section-number preservation;
- metadata accuracy;
- duplicate detection;
- version handling.

## 4. Phase 2 — RAG MVP

Build:

- query normalization;
- jurisdiction detection;
- intent classification;
- hybrid retrieval;
- reranking;
- context assembly;
- answer generation;
- citations.

### Exit test

A benchmark question should produce a correct source-backed answer
without relying on generic model knowledge.

## 5. Phase 3 — Verification & Safety

Build:

- claim extraction;
- citation validation;
- contradiction detection;
- confidence engine;
- abstention;
- prompt injection defenses.

### Key test

Inject irrelevant/malicious instructions into retrieved documents and
verify that the model treats them as data.

## 6. Phase 4 — Product Classification

Build deterministic decision trees for:

- classical;
- proprietary;
- new/non-classical;
- phytopharmaceutical;
- Ayurveda-Aahara;
- cosmetic;
- uncertain.

Use RAG for definitions/evidence and LLM for explanations.

## 7. Phase 5 — IP Navigator

Implement:

- patent;
- trademark;
- GI;
- copyright;
- design;
- trade secret;
- plant variety.

Return structured opportunity cards.

## 8. Phase 6 — ABS/TK

Implement:

- biological resource questions;
- provenance;
- traditional knowledge;
- commercialisation;
- foreign involvement;
- assessment;
- evidence;
- escalation.

Explicitly label the result as preliminary.

## 9. Phase 7 — International

Start with a small number of high-value regimes:

- TRIPS;
- CBD;
- Nagoya;
- WIPO GRATK;
- PCT;
- Madrid;
- Hague;
- Budapest.

Then add destination-market coverage selectively.

## 10. Phase 8 — Knowledge Graph

Create ontology:

``` text
Authority
Document
Section
Rule
Amendment
Case
Product
Biological Resource
Traditional Knowledge
IP Right
Jurisdiction
```

Add relationships.

Use graph retrieval only where it improves multi-hop questions.

## 11. Phase 9 — Agentic Orchestration

Introduce planner only after deterministic workflows work.

Agents:

- Router;
- IP researcher;
- Regulatory researcher;
- ABS/TK researcher;
- International researcher;
- verifier.

All agents must return structured evidence, not free-form conclusions.

## 12. Phase 10 — Multilingual

### English/Hindi

Pipeline:

``` text
User language
→ semantic normalization
→ legal retrieval
→ reasoning
→ structured answer
→ target-language rendering
```

Evaluate terminology separately from general translation quality.

## 13. Phase 11 — UI Integration

Implement in this order:

1.  Home;
2.  Ask;
3.  Answer;
4.  Sources;
5.  Product Journey;
6.  IP Matrix;
7.  ABS;
8.  Export;
9.  Cases;
10. Settings.

## 14. Phase 12 — Evaluation

Create a minimum expert-reviewed benchmark.

Suggested starting set:

- 40 patent/IP;
- 30 product classification;
- 30 ABS/TK;
- 20 drug/food/cosmetic;
- 20 international;
- 20 source/citation;
- 20 multilingual;
- 20 adversarial/abstention.

Total: 200.

For each record:

``` json
{
  "question": "...",
  "jurisdiction": "IN",
  "expected_intent": "PATENTABILITY",
  "required_sources": [],
  "must_include": [],
  "must_not_claim": [],
  "risk": "HIGH"
}
```

## 15. Testing Strategy

### Unit tests

- classification rules;
- metadata filters;
- API validation;
- permission checks;
- confidence calculations.

### Integration tests

- ingestion → retrieval;
- retrieval → LLM;
- answer → citation validator;
- product → IP matrix.

### RAG evaluation

- Recall@k;
- Precision@k;
- MRR;
- nDCG;
- citation precision;
- citation recall;
- groundedness.

### Safety evaluation

- jurisdiction leakage;
- fabricated citation;
- unsupported legal claim;
- stale-source retrieval;
- contradictory source handling;
- prompt injection;
- malicious uploads.

### UI tests

- onboarding;
- journey completion;
- source opening;
- language switch;
- dark mode;
- accessibility.

## 16. CI/CD

Every pull request:

``` text
lint
→ type checks
→ unit tests
→ security scan
→ API tests
→ build
```

Main branch:

``` text
tests
→ container build
→ staging deployment
→ smoke tests
→ production approval
```

Corpus changes should use a separate ingestion pipeline.

## 17. Deployment

### Development

Docker Compose:

- API;
- PostgreSQL;
- Redis;
- worker.

### Staging

Managed: - PostgreSQL; - object storage; - containers; - secrets; -
monitoring.

### Production

Add: - autoscaling; - WAF/rate limiting; - backups; - alerts; - audit
retention; - disaster recovery.

## 18. Rough Timeline

### Week 1

- architecture;
- repo setup;
- corpus inventory;
- UI wireframes;
- database migration.

### Week 2

- ingestion pipeline;
- source metadata;
- PostgreSQL/pgvector;
- basic retrieval.

### Week 3

- hybrid RAG;
- reranker;
- citation display;
- initial API.

### Week 4

- verification;
- confidence;
- abstention;
- benchmark v1.

### Week 5

- product classification;
- IP matrix;
- frontend workflows.

### Week 6

- ABS/TK;
- human escalation;
- source viewer.

### Week 7

- international;
- knowledge graph;
- multilingual.

### Week 8

- agentic orchestration;
- evaluation;
- performance tuning.

### Week 9

- security;
- deployment;
- accessibility;
- failure-state polish.

### Week 10

- full benchmark;
- demo scenarios;
- presentation;
- final QA.

If the SIH deadline is shorter, cut scope rather than cutting evaluation
and citation verification.

## 19. Git Repository Structure

``` text
ayuraksha/
├── apps/
│   ├── mobile/
│   └── web/
├── backend/
│   ├── api/
│   ├── auth/
│   ├── workflows/
│   ├── rag/
│   ├── agents/
│   ├── verification/
│   └── services/
├── data/
│   ├── ingestion/
│   ├── schemas/
│   └── evaluation/
├── corpus/
│   ├── manifests/
│   └── validators/
├── graph/
├── infra/
│   ├── docker/
│   ├── terraform/
│   └── monitoring/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── rag/
│   └── safety/
├── docs/
└── README.md
```

## 20. Team Ownership

### AIML 1

RAG + retrieval + reranking.

### AIML 2

Reasoning + workflows + verification + agents.

### Data Science

Corpus + ontology + benchmark + evaluation.

### Cloud

Backend platform + infrastructure + security + deployment.

### App 1

Core app + chat + sources.

### App 2

Product journey + IP + ABS + export workflows.

## 21. Definition of Done

A feature is complete only when:

- backend implemented;
- API documented;
- frontend integrated;
- error states handled;
- permissions tested;
- logs/audit requirements addressed;
- unit tests pass;
- integration test exists;
- evaluation case exists where AI behaviour is involved;
- documentation updated.

## 22. SIH Release Gate

Before presenting:

### Functional

- all primary journeys complete;
- no dead-end screens;
- demo data prepared;
- source links work.

### AI

- citations verified;
- abstention works;
- jurisdiction firewall tested;
- benchmark results recorded.

### Security

- secrets removed;
- production credentials isolated;
- rate limits enabled;
- sensitive logs reviewed.

### Presentation

Prepare three stories:

1.  Patentability;
2.  ABS/TK;
3.  International/export.

Also demonstrate one deliberate abstention.

## 23. Product Principle

The final product should demonstrate:

> **AyuRaksha does not merely generate answers. It constructs
> evidence-backed regulatory pathways.**
