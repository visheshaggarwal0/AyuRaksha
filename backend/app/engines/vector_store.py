from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import hashlib
import math
import logging

from sqlalchemy import func, select

from app.db.session import AsyncSessionLocal
from app.db.models import DocumentChunk, Source, SourceSection, SourceVersion

logger = logging.getLogger(__name__)

def get_embedding_model():
    from app.modules.embeddings import embedding_module
    return embedding_module._get_model()

def generate_deterministic_embedding(text_content: str, dim: int = 384) -> List[float]:
    """
    Generates a 384-dimensional embedding.
    Uses unified SentenceTransformer('all-MiniLM-L6-v2') singleton when available;
    otherwise falls back to a deterministic 384-dimensional unit vector.
    """
    from app.modules.embeddings import embedding_module
    import os
    if os.getenv("LIGHTWEIGHT_EMBEDDINGS", "1").lower() in ("1", "true", "yes"):
        return embedding_module._fallback_vector(text_content)

    model = get_embedding_model()
    if model is not None:
        raw_vector = model.encode(text_content, normalize_embeddings=True)
        return [float(val) for val in raw_vector]
    
    return embedding_module._fallback_vector(text_content)

# Alias for semantic clarity
generate_embedding = generate_deterministic_embedding


class BaseVectorStore(ABC):
    @abstractmethod
    async def search(
        self,
        query_vector: List[float],
        jurisdiction: str = "IN",
        limit: int = 10,
        domain_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        pass


class NeonPgVectorStore(BaseVectorStore):
    """Neon/Postgres retrieval over normalized, provenance-bearing chunk records."""

    @staticmethod
    def _base_statement():
        return select(
            DocumentChunk.id.label("chunk_id"),
            DocumentChunk.text,
            DocumentChunk.jurisdiction,
            DocumentChunk.chunk_metadata,
            SourceSection.text.label("raw_statute"),
            SourceSection.section_number,
            SourceSection.heading,
            Source.source_code,
            Source.title.label("source_title"),
            Source.source_url,
            Source.authority,
            Source.authority_level,
        ).join(
            SourceSection, DocumentChunk.section_id == SourceSection.id
        ).join(
            SourceVersion, SourceSection.source_version_id == SourceVersion.id
        ).join(
            Source, SourceVersion.source_id == Source.id
        ).where(Source.current_status == "ACTIVE")

    @staticmethod
    def _apply_filters(statement, jurisdiction: str, domain_filter):
        if jurisdiction and jurisdiction != "CROSS_BORDER":
            statement = statement.where(DocumentChunk.jurisdiction == jurisdiction)
        if domain_filter:
            if isinstance(domain_filter, (list, tuple, set)):
                domains = list(domain_filter)
                if len(domains) == 1:
                    statement = statement.where(DocumentChunk.chunk_metadata["domain"].astext == domains[0])
                else:
                    statement = statement.where(
                        DocumentChunk.chunk_metadata["domain"].astext.in_(domains)
                    )
            else:
                statement = statement.where(DocumentChunk.chunk_metadata["domain"].astext == domain_filter)
        return statement

    @staticmethod
    def _serialize_row(row: Any, score: float) -> Dict[str, Any]:
        metadata = row.chunk_metadata or {}
        return {
            "chunk_id": str(row.chunk_id),
            "source_id": row.source_code or metadata.get("source_id", "UNKNOWN_SOURCE"),
            "text": row.text,
            "raw_statute": row.raw_statute,
            "jurisdiction": row.jurisdiction,
            "section_number": row.section_number,
            "heading": row.heading,
            "source_title": row.source_title,
            "official_url": row.source_url or metadata.get("source_url"),
            "authority": row.authority,
            "authority_level": row.authority_level,
            "metadata": metadata,
            "support_score": round(max(0.0, min(score, 1.0)), 4),
        }

    async def search(
        self,
        query_vector: List[float],
        jurisdiction: str = "IN",
        limit: int = 10,
        domain_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not AsyncSessionLocal or not query_vector:
            return []

        distance = DocumentChunk.embedding.cosine_distance(query_vector).label("distance")
        statement = self._apply_filters(self._base_statement().add_columns(distance), jurisdiction, domain_filter)
        statement = statement.where(DocumentChunk.embedding.is_not(None)).order_by(distance).limit(limit)
        try:
            async with AsyncSessionLocal() as session:
                rows = (await session.execute(statement)).all()
            return [self._serialize_row(row, 1.0 - float(row.distance)) for row in rows]
        except Exception as error:
            logger.warning("Vector retrieval unavailable: %s", error)
            return []

    async def search_lexical(
        self,
        query_text: str,
        jurisdiction: str = "IN",
        limit: int = 10,
        domain_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not AsyncSessionLocal or not query_text.strip():
            return []

        document_vector = func.to_tsvector("english", DocumentChunk.text)
        query = func.websearch_to_tsquery("english", query_text)
        rank = func.ts_rank_cd(document_vector, query).label("lexical_rank")
        statement = self._apply_filters(self._base_statement().add_columns(rank), jurisdiction, domain_filter)
        statement = statement.where(document_vector.op("@@")(query)).order_by(rank.desc()).limit(limit)
        try:
            async with AsyncSessionLocal() as session:
                rows = (await session.execute(statement)).all()
            return [self._serialize_row(row, float(row.lexical_rank)) for row in rows]
        except Exception as error:
            logger.warning("PostgreSQL full-text retrieval unavailable: %s", error)
            return []


class PineconeVectorStore(BaseVectorStore):
    """Reserved adapter for deployments that elect to use an external vector store."""

    def __init__(self, api_key: str = "", index_name: str = "ayuraksha"):
        self.api_key = api_key
        self.index_name = index_name

    async def search(
        self,
        query_vector: List[float],
        jurisdiction: str = "IN",
        limit: int = 10,
        domain_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        return []
