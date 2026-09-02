# AyuRaksha Module Interface Contracts

This document formalizes the interface contracts (Protocols / Abstract Base Classes) for the 10 logical modules in AyuRaksha.

---

## 1. Data Module (`IDataModule`)
Responsible for loading, normalizing, chunking, and maintaining the cryptographic integrity of legal sources.

```python
class IDataModule(ABC):
    @abstractmethod
    def get_registered_sources(self) -> List[SourceDocument]:
        """Returns all registered official sources from canonical manifests."""
        pass

    @abstractmethod
    def load_document_version(self, source_id: str) -> Optional[DocumentVersion]:
        """Loads specific document version with verified file SHA-256."""
        pass

    @abstractmethod
    def get_provisions(self, source_id: str) -> List[Provision]:
        """Returns parsed provisions for a source."""
        pass

    @abstractmethod
    def extract_chunks(self) -> List[CorpusChunk]:
        """Processes and returns atomic statutory chunks for indexing."""
        pass
```

---

## 2. Embeddings Module (`IEmbeddingModule`)
Responsible for dense vectorization of legal queries and document chunks.

```python
class IEmbeddingModule(ABC):
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns embedding vector dimension (e.g. 384)."""
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Generates dense vector for search query."""
        pass

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates dense vectors for batch of document chunks."""
        pass
```

---

## 3. Retrieval Module (`IRetrievalModule`)
Supports independent and composable execution across dense, sparse, and graph modalities.

```python
class IVectorRetriever(ABC):
    @abstractmethod
    async def retrieve_vector(self, query: str, jurisdiction: str, limit: int = 10) -> List[Evidence]:
        """Independent dense semantic retrieval."""
        pass

class IKeywordRetriever(ABC):
    @abstractmethod
    async def retrieve_keyword(self, query: str, jurisdiction: str, limit: int = 10) -> List[Evidence]:
        """Independent sparse lexical (BM25 / tsvector) retrieval."""
        pass

class IGraphRetriever(ABC):
    @abstractmethod
    async def retrieve_graph(self, entities: List[str], limit: int = 10) -> List[Evidence]:
        """Independent relational statutory graph retrieval."""
        pass

class IRetrievalModule(ABC):
    @abstractmethod
    async def retrieve(self, query: str, jurisdiction: str, limit: int = 5) -> RetrievalResult:
        """Fused multi-modal retrieval across all active engines."""
        pass
```

---

## 4. Reranking Module (`IRerankingModule`)
Responsible for fusing independent retrieval results, applying statutory hierarchy weighting, and exact-section boosts.

```python
class IRerankingModule(ABC):
    @abstractmethod
    def rerank(self, query: str, candidates: List[Evidence], top_k: int = 5) -> List[Evidence]:
        """Reranks candidate evidence using authority levels and semantic relevance."""
        pass
```

---

## 5. Generation Module (`IGenerationModule`)
Provider-agnostic interface for LLM synthesis. Allows swapping between Google Gemini, Groq, local Ollama, and OpenRouter without altering application logic.

```python
class ILLMProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.1,
        max_tokens: int = 1500,
        response_format: Optional[str] = None
    ) -> Optional[str]:
        pass

class IGenerationModule(ABC):
    @abstractmethod
    async def generate_legal_answer(
        self,
        query: str,
        evidence: List[Evidence],
        jurisdiction: str
    ) -> str:
        """Synthesizes grounded legal answer strictly from provided evidence."""
        pass
```

---

## 6. Citations Module (`ICitationModule`)
Responsible for parsing citation markers (`[1]`, `[2]`), extracting verbatim excerpts, validating document integrity, and building public citations.

```python
class ICitationModule(ABC):
    @abstractmethod
    def extract_citations(self, text: str, evidence: List[Evidence]) -> List[Citation]:
        """Extracts and verifies citations referenced in generated text."""
        pass

    @abstractmethod
    def verify_provenance(self, citation: Citation) -> bool:
        """Cryptographically verifies that verbatim quote exists in primary document."""
        pass
```

---

## 7. Guardrails Module (`IGuardrailModule`)
Safety and compliance enforcement prior to generation and output.

```python
class IGuardrailModule(ABC):
    @abstractmethod
    def evaluate_safety(self, query: str, jurisdiction: str) -> Optional[AbstentionReason]:
        """Detects biopiracy circumvention, illegal medical claims, or ungrounded queries."""
        pass
```

---

## 8. Knowledge Module (`IKnowledgeModule`)
Maintains the classical Ayurvedic texts, botanical taxonomy, and cross-statutory relationships.

```python
class IKnowledgeModule(ABC):
    @abstractmethod
    def lookup_botanical(self, name_or_synonym: str) -> Optional[GraphEntity]:
        """Resolves botanical species across scientific, Sanskrit, and vernacular names."""
        pass

    @abstractmethod
    def is_classical_formulation(self, formulation_name: str) -> bool:
        """Verifies presence in First Schedule authoritative Ayurvedic books."""
        pass

    @abstractmethod
    def get_related_provisions(self, section_number: str) -> List[GraphRelationship]:
        """Traverses statutory relationships (e.g. Sec 3(p) -> Rule 158B)."""
        pass
```

---

## 9. Evaluation Module (`IEvaluationModule`)
Sentence-level natural language claim verification and confidence scoring.

```python
class IEvaluationModule(ABC):
    @abstractmethod
    def verify_claims(self, answer: str, evidence: List[Evidence]) -> Dict[str, Any]:
        """Decomposes answer into sentence claims and evaluates entailment support."""
        pass

    @abstractmethod
    def compute_confidence(
        self,
        retrieval_result: RetrievalResult,
        claim_verification: Dict[str, Any]
    ) -> Confidence:
        """Computes multi-dimensional calibrated confidence rating."""
        pass
```

---

## 10. Orchestration Module (`IOrchestrationModule`)
Coordinates the 9 specialized modules into an auditable end-to-end pipeline.

```python
class IOrchestrationModule(ABC):
    @abstractmethod
    async def process_query(
        self,
        query: str,
        jurisdiction: str = "IN",
        language: str = "en"
    ) -> RAGResponse:
        """Executes full RAG workflow and returns complete structured response."""
        pass
```
