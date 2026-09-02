# ADR-004: Strongly Typed Domain Contracts (Pydantic v2)

## Status
Accepted

## Context
The prior AI pipeline relied heavily on untyped Python dictionaries (`dict[str, Any]`). Different components used inconsistent keys (`source_id` vs `doc_id`, `relevance_score` vs `support_score`, `section` vs `section_number`). Glue code in `orchestrator.py` spent excessive complexity mapping between dicts and Pydantic models, causing silent key errors during refactoring.

## Decision
We establish **12 Strongly Typed Domain Models** in `backend/app/models/domain.py` using Pydantic v2:
1. `SourceDocument`
2. `DocumentVersion`
3. `Provision`
4. `CorpusChunk`
5. `Evidence`
6. `Citation`
7. `GraphEntity`
8. `GraphRelationship`
9. `RetrievalResult`
10. `RAGResponse`
11. `Confidence`
12. `AbstentionReason`

All inter-module communication must use these domain models. Dictionary-passing between modules is prohibited.

## Rationale
- Guaranteed compile-time and runtime data validation.
- Auto-generated OpenAPI JSON schemas for frontend synchronization.
- Eliminates KeyError bugs and hidden string mutations.

## Consequences
- Modules must parse external API inputs into these validated models immediately at the boundary.
