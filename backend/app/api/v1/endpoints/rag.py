from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.db.models import DocumentChunk, Source
from app.engines.vector_store import generate_deterministic_embedding

router = APIRouter()

class RAGQuery(BaseModel):
    query: str
    jurisdiction: str = "IN"
    top_k: int = 5

class CitationModel(BaseModel):
    id: str
    text: str
    source_title: str
    section_number: str
    similarity: float

class RAGResponse(BaseModel):
    answer: str
    citations: List[CitationModel]

@router.post("/query", response_model=RAGResponse)
async def query_rag(request: RAGQuery, db: AsyncSession = Depends(get_db)):
    """
    Given a user query, generate a vector embedding, search the pgvector database
    for the most relevant DocumentChunks, and return the context.
    (Note: The actual LLM generation is handled by the Orchestrator agent, 
    but this endpoint serves as the raw retrieval engine test).
    """
    try:
        # 1. Generate query embedding
        query_embedding = generate_deterministic_embedding(request.query)
        
        # 2. Vector similarity search using pgvector (Cosine distance: <=>)
        # We query DocumentChunk and compute cosine similarity
        distance = DocumentChunk.embedding.cosine_distance(query_embedding).label("distance")
        stmt = (
            select(DocumentChunk, distance)
            .filter(DocumentChunk.jurisdiction == request.jurisdiction)
            .filter(DocumentChunk.embedding.is_not(None))
            .order_by(distance)
            .limit(request.top_k)
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        # 3. Format citations
        citations = []
        for row in rows:
            chunk = row[0]
            dist = float(row[1]) if row[1] is not None else 1.0
            similarity = round(max(0.0, min(1.0 - dist, 1.0)), 4)
            metadata = chunk.chunk_metadata or {}
            citations.append(
                CitationModel(
                    id=str(chunk.id),
                    text=chunk.text,
                    source_title=metadata.get("source_title", "Unknown Source"),
                    section_number=metadata.get("section_number", "Unknown Section"),
                    similarity=similarity
                )
            )
            
        return RAGResponse(
            answer="This is a raw retrieval test. Orchestrator handles LLM generation.",
            citations=citations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
