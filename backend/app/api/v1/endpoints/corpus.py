from fastapi import APIRouter, Query
from typing import List, Dict, Any, Optional
from app.corpus.chunker import LegalDocumentChunker
from app.corpus.taxonomy import taxonomy_engine

router = APIRouter(prefix="/corpus", tags=["Statutory Corpus & Manifest"])
chunker = LegalDocumentChunker()

@router.get("/manifest")
async def get_corpus_manifest() -> List[Dict[str, Any]]:
    """
    Returns the complete list of indexed statutory acts, rules, and treaties.
    """
    return chunker.parse_manifest()

@router.get("/sources/{source_id}")
async def get_source_details(source_id: str) -> Dict[str, Any]:
    """
    Returns full section breakdown for a specific statutory document.
    """
    sources = chunker.parse_manifest()
    for src in sources:
        if src.get("source_id") == source_id:
            rel_path = src.get("normalized_file") or src.get("file_path", "")
            return chunker.parse_source_file(rel_path)
    return {"error": "Source ID not found in verified corpus."}

@router.get("/books")
async def get_classical_books(query: str = Query(default="", description="Search by title, author, or keyword"), limit: int = Query(default=50, le=200)) -> List[Dict[str, Any]]:
    """
    Returns the authoritative classical texts from the Drugs & Cosmetics Act First Schedule and TKDL catalogue.
    """
    return taxonomy_engine.search_books(query=query, limit=limit)

@router.get("/plants")
async def get_botanical_plants(query: str = Query(default="", description="Search by Sanskrit, scientific, common, Unani, or Siddha name"), limit: int = Query(default=50, le=200)) -> List[Dict[str, Any]]:
    """
    Returns medicinal plants with scientific nomenclature and vernacular synonyms from TKDL.
    """
    return taxonomy_engine.search_plants(query=query, limit=limit)

@router.get("/glossary")
async def get_glossary_terms(query: str = Query(default="", description="Search Ayurvedic clinical and legal definitions"), limit: int = Query(default=50, le=200)) -> List[Dict[str, Any]]:
    """
    Returns authentic Ayurvedic medical and legal definitions with category metadata.
    """
    return taxonomy_engine.search_glossary(query=query, limit=limit)

@router.get("/entities")
async def get_entities(query: str = Query(default="", description="Search entity canonical name or synonyms"), entity_type: str = Query(default="", description="Filter by plant, mineral, disease, property"), limit: int = Query(default=50, le=200)) -> List[Dict[str, Any]]:
    """
    Returns cross-referenced named entities across plants, minerals, karmas, and diseases.
    """
    return taxonomy_engine.search_entities(query=query, entity_type=entity_type, limit=limit)

@router.get("/stats")
async def get_corpus_statistics() -> Dict[str, Any]:
    """
    Returns counts and metrics across statutory documents, classical books, plants, and entities.
    """
    stats = taxonomy_engine.get_corpus_statistics()
    stats["statutory_manifest_count"] = len(chunker.parse_manifest())
    return stats
