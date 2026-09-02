# ADR-003: Independent Tri-Retrieval (Vector, Keyword, Graph) and Reciprocal Rank Fusion

## Status
Accepted

## Context
Ayurvedic regulatory queries require three distinct retrieval capabilities:
1. **Semantic conceptual understanding** (e.g. "anti-inflammatory herbal roots" -> *Withania somnifera* / *Curcuma longa*).
2. **Exact statutory lexical precision** (e.g. "Section 3(p)", "Form CT-18", "Rule 158B").
3. **Relational statutory traversal** (e.g. Patents Act Section 3(p) references Biological Diversity Act Section 6, which mandates NBA Form III approval).

In earlier implementations, retrieval was entangled in monolithic functions, making it impossible to evaluate or test vector, lexical, or graph components in isolation.

## Decision
We decouple retrieval into three **independent, standalone retriever interfaces**:
- `IVectorRetriever`: Queries dense vector indexes (Postgres pgvector or local embeddings).
- `IKeywordRetriever`: Queries sparse lexical indexes (Postgres tsvector or BM25).
- `IGraphRetriever`: Traverses relational statutory knowledge graphs.

A composite retriever executes each modality independently and merges the results using **Reciprocal Rank Fusion (RRF)** combined with statutory authority hierarchy weighting (Acts > Rules > Guidelines > Taxonomy).

## Rationale
- Each retrieval engine can be benchmarked and evaluated independently for precision and recall.
- If the vector database is offline or un-indexed, the keyword and graph retrievers continue operating without crashing the pipeline.
- RRF eliminates score scale discrepancies between cosine similarity (0 to 1), BM25 scores (0 to 40+), and graph hop distances.

## Consequences
- Requires a deduplication step across retrieved candidates based on canonical source ID and section number.
