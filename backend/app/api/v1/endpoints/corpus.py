from fastapi import APIRouter
from typing import List, Dict, Any
from app.corpus.chunker import LegalDocumentChunker

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
            rel_path = src.get("file_path", "")
            return chunker.parse_source_file(rel_path)
    return {"error": "Source ID not found in verified corpus."}
