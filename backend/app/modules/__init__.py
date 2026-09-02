"""
AyuRaksha Architecture Modules Package (SIH 26045)
Consolidated, clean access to the 10 logical modules:
1. data_module
2. embedding_module
3. retrieval_module (with independent vector, keyword, and graph retrievers)
4. reranking_module
5. generation_module (with pluggable Gemini, Groq, and Ollama providers)
6. citation_module
7. guardrails_module
8. knowledge_module
9. evaluation_module
10. orchestration_module
"""
from app.modules.data import data_module
from app.modules.embeddings import embedding_module
from app.modules.retrieval import (
    retrieval_module,
    IndependentVectorRetriever,
    IndependentKeywordRetriever,
    IndependentGraphRetriever,
    CompositeRetrievalModule
)
from app.modules.reranking import reranking_module
from app.modules.generation import (
    generation_module,
    GeminiProvider,
    GroqProvider,
    LocalOllamaProvider,
    DeterministicStatutoryProvider
)
from app.modules.citations import citation_module
from app.modules.guardrails import guardrails_module
from app.modules.knowledge import knowledge_module
from app.modules.evaluation import evaluation_module
from app.modules.orchestration import orchestration_module

__all__ = [
    "data_module",
    "embedding_module",
    "retrieval_module",
    "IndependentVectorRetriever",
    "IndependentKeywordRetriever",
    "IndependentGraphRetriever",
    "CompositeRetrievalModule",
    "reranking_module",
    "generation_module",
    "GeminiProvider",
    "GroqProvider",
    "LocalOllamaProvider",
    "DeterministicStatutoryProvider",
    "citation_module",
    "guardrails_module",
    "knowledge_module",
    "evaluation_module",
    "orchestration_module",
]
