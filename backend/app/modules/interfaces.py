"""
AyuRaksha Architecture Interfaces (SIH 26045)
Formal Abstract Base Classes (ABCs) defining decoupled contracts for all 10 logical modules:
1. Data
2. Embeddings
3. Retrieval (Vector, Keyword, Graph, Composite)
4. Reranking
5. Generation (Pluggable Providers: Gemini, Groq, Local Ollama, OpenRouter)
6. Citations
7. Guardrails
8. Knowledge
9. Evaluation
10. Orchestration
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from app.models.domain import (
    SourceDocument,
    DocumentVersion,
    Provision,
    CorpusChunk,
    Evidence,
    Citation,
    GraphEntity,
    GraphRelationship,
    RetrievalResult,
    RAGResponse,
    Confidence,
    AbstentionReason,
)


# ============================================================================
# 1. Data Module Interface
# ============================================================================

class IDataModule(ABC):
    """Responsible for source manifests, raw statute loading, and chunk extraction."""

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


# ============================================================================
# 2. Embeddings Module Interface
# ============================================================================

class IEmbeddingModule(ABC):
    """Responsible for dense vectorization of legal queries and document chunks."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding vector dimension (e.g. 384)."""
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        """Generates dense vector for search query."""
        pass

    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generates dense vectors for batch of document chunks."""
        pass


# ============================================================================
# 3. Retrieval Module Interfaces (Independent & Composite)
# ============================================================================

class IVectorRetriever(ABC):
    """Independent dense semantic retrieval."""

    @abstractmethod
    async def retrieve_vector(
        self,
        query: str,
        jurisdiction: str = "IN",
        limit: int = 10,
        domain_filter: Optional[str] = None
    ) -> List[Evidence]:
        pass


class IKeywordRetriever(ABC):
    """Independent sparse lexical (BM25 / tsvector) retrieval."""

    @abstractmethod
    async def retrieve_keyword(
        self,
        query: str,
        jurisdiction: str = "IN",
        limit: int = 10,
        domain_filter: Optional[str] = None
    ) -> List[Evidence]:
        pass


class IGraphRetriever(ABC):
    """Independent relational statutory graph retrieval."""

    @abstractmethod
    async def retrieve_graph(
        self,
        entities: List[str],
        limit: int = 10
    ) -> List[Evidence]:
        pass


class IRetrievalModule(ABC):
    """Composite multi-modal retrieval coordinator."""

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        jurisdiction: str = "IN",
        limit: int = 5,
        domain_filter: Optional[str] = None
    ) -> RetrievalResult:
        """Fused multi-modal retrieval combining vector, keyword, and graph."""
        pass


# ============================================================================
# 4. Reranking Module Interface
# ============================================================================

class IRerankingModule(ABC):
    """Reranks candidate evidence using statutory authority hierarchy and relevance."""

    @abstractmethod
    def rerank(
        self,
        query: str,
        candidates: List[Evidence],
        top_k: int = 5
    ) -> List[Evidence]:
        pass


# ============================================================================
# 5. Generation Module Interfaces (Pluggable Provider Pattern)
# ============================================================================

class ILLMProvider(ABC):
    """Pluggable adapter interface for specific LLM engines (Gemini, Groq, Ollama)."""

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
    """High-level legal synthesis service."""

    @abstractmethod
    def register_provider(self, provider: ILLMProvider, priority: int = 10) -> None:
        """Registers an LLM provider with a given priority."""
        pass

    @abstractmethod
    async def generate_legal_answer(
        self,
        query: str,
        evidence: List[Evidence],
        jurisdiction: str = "IN"
    ) -> str:
        """Synthesizes grounded legal answer strictly from provided evidence."""
        pass


# ============================================================================
# 6. Citations Module Interface
# ============================================================================

class ICitationModule(ABC):
    """Verifies and extracts citations linked to evidence."""

    @abstractmethod
    def extract_citations(
        self,
        answer_text: str,
        evidence: List[Evidence]
    ) -> List[Citation]:
        pass

    @abstractmethod
    def verify_provenance(self, citation: Citation) -> bool:
        """Cryptographically verifies that verbatim quote exists in primary document."""
        pass


# ============================================================================
# 7. Guardrails Module Interface
# ============================================================================

class IGuardrailModule(ABC):
    """Statutory abstention and safety enforcement."""

    @abstractmethod
    def evaluate_safety(
        self,
        query: str,
        jurisdiction: str = "IN"
    ) -> Optional[AbstentionReason]:
        pass


# ============================================================================
# 8. Knowledge Module Interface
# ============================================================================

class IKnowledgeModule(ABC):
    """Botanical taxonomy, First Schedule book catalogs, and entity resolution."""

    @abstractmethod
    def lookup_botanical(self, name_or_synonym: str) -> Optional[GraphEntity]:
        pass

    @abstractmethod
    def is_classical_formulation(self, formulation_name: str) -> bool:
        pass

    @abstractmethod
    def get_related_provisions(self, section_number: str) -> List[GraphRelationship]:
        pass


# ============================================================================
# 9. Evaluation Module Interface
# ============================================================================

class IEvaluationModule(ABC):
    """Sentence entailment verification and calibrated confidence scoring."""

    @abstractmethod
    def verify_claims(
        self,
        answer: str,
        evidence: List[Evidence]
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def compute_confidence(
        self,
        retrieval_result: RetrievalResult,
        claim_verification: Dict[str, Any]
    ) -> Confidence:
        pass


# ============================================================================
# 10. Orchestration Module Interface
# ============================================================================

class IOrchestrationModule(ABC):
    """End-to-end pipeline coordinator."""

    @abstractmethod
    async def process_query(
        self,
        query: str,
        jurisdiction: str = "IN",
        language: str = "en"
    ) -> RAGResponse:
        pass
