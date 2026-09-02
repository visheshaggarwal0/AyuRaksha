# ADR-001: Modular Monolith Architecture Over Microservices

## Status
Accepted

## Context
AyuRaksha (SIH 26045) must handle multi-modal legal retrieval, complex taxonomy search across hundreds of classical texts and botanicals, deterministic statutory rule checking, sentence-level entailment verification, and multilingual translation.

In early discussions, breaking the system into microservices (e.g. separate RAG service, separate Taxonomy service, separate Translation service, separate Classification service) was considered.

## Decision
We reject a microservices architecture and commit to a **Modular Monolith** pattern within a single FastAPI application.
All 10 functional modules (`data`, `retrieval`, `embeddings`, `reranking`, `generation`, `citations`, `guardrails`, `orchestration`, `knowledge`, `evaluation`) will live within `backend/app/modules/`.

## Rationale
1. **Low Latency & Zero Serialization Overhead**: A complete RAG query evaluates 11 pipeline stages. In-process function calls take microseconds, whereas REST/gRPC network hops between 4-5 microservices would add 200–600ms of latency per query.
2. **Deterministic Precedence Enforcement**: The decision trees (Rules 1, 1B, 2, 3, 4) must atomically inform and constrain retrieval and generation. A shared memory space enables immediate constraint propagation.
3. **Operational Simplicity for SIH Evaluation**: Running and demonstrating AyuRaksha requires a single command (`uvicorn app.main:app`) without Docker Compose orchestration hurdles, service discovery failures, or distributed transaction bugs.
4. **Strong Typing with Zero Contract Drift**: Pydantic v2 domain models can be shared directly across modules without requiring protobuf compilers or IDL maintenance.

## Consequences
- Modules must communicate through defined interfaces (`backend/app/modules/interfaces.py`) rather than reaching into private internals.
- Circular dependencies between modules are strictly forbidden.
