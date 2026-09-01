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
        
        # 2. Vector similarity search using pgvector (L2 distance: <->)
        # We query DocumentChunk and join with SourceSection and Source for citation metadata
        stmt = (
            select(DocumentChunk)
            .filter(DocumentChunk.jurisdiction == request.jurisdiction)
            .order_by(DocumentChunk.embedding.l2_distance(query_embedding))
            .limit(request.top_k)
        )
        
        result = await db.execute(stmt)
        chunks = result.scalars().all()
        
        # 3. Format citations
        citations = []
        for i, chunk in enumerate(chunks):
            # In a real app, we'd eager load the relations. Here we simulate the metadata
            citations.append(
                CitationModel(
                    id=str(chunk.id),
                    text=chunk.text,
                    source_title=chunk.chunk_metadata.get("source_title", "Unknown Source"),
                    section_number=chunk.chunk_metadata.get("section_number", "Unknown Section"),
                    similarity=0.95 - (i * 0.05) # Simulated similarity score since we didn't fetch the exact distance in the ORM
                )
            )
            
        return RAGResponse(
            answer="This is a raw retrieval test. Orchestrator handles LLM generation.",
            citations=citations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
