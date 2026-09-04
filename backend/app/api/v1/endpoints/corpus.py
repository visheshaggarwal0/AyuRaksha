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

@router.get("/patent-forms")
async def get_patent_forms(
    query: str = Query(default="", description="Search patent forms by number, title, or purpose")
) -> List[Dict[str, Any]]:
    """
    Returns official CGPDTM Patent Filing Forms (Form 1 to Form 30) from Patents Rules 2003/2024.
    """
    import csv
    from pathlib import Path
    forms_path = Path(__file__).resolve().parents[5] / "data" / "IPINDIA" / "patent_forms.csv"
    if not forms_path.exists():
        forms_path = Path(__file__).resolve().parents[4] / "data" / "IPINDIA" / "patent_forms.csv"
    if not forms_path.exists():
        return []

    results = []
    q_lower = query.lower().strip()
    with open(forms_path, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            form_num = row.get("form_number", "")
            form_title = row.get("form_title", "")
            purpose = row.get("purpose", "")
            rel = row.get("related_section_or_rule", "")
            if not q_lower or (q_lower in form_num.lower() or q_lower in form_title.lower() or q_lower in purpose.lower() or q_lower in rel.lower()):
                results.append(row)
    return results

@router.get("/patent-provisions")
async def get_patent_provisions(
    query: str = Query(default="", description="Search by section, rule, title, or topic"),
    relevance_filter: Optional[str] = Query(default=None, description="Filter by ayurveda or tk relevance")
) -> List[Dict[str, Any]]:
    """
    Returns canonical sections and rules from Patents Act 1970 and Patents Rules 2003.
    """
    import csv
    from pathlib import Path
    provisions_path = Path(__file__).resolve().parents[5] / "data" / "IPINDIA" / "patents_act_rules_full.csv"
    if not provisions_path.exists():
        provisions_path = Path(__file__).resolve().parents[4] / "data" / "IPINDIA" / "patents_act_rules_full.csv"
    if not provisions_path.exists():
        return []

    results = []
    q_lower = query.lower().strip()
    with open(provisions_path, "r", encoding="utf-8", errors="replace") as f:
        for row in csv.DictReader(f):
            sec_rule = row.get("section_or_rule", "")
            title = row.get("title", "")
            summary = row.get("summary", "")
            ayur = row.get("relevance_to_ayurveda", "")
            tk = row.get("relevance_to_traditional_knowledge", "")

            if relevance_filter == "ayurveda" and ayur in ("None", ""):
                continue
            if relevance_filter == "tk" and tk in ("None", ""):
                continue

            if not q_lower or (q_lower in sec_rule.lower() or q_lower in title.lower() or q_lower in summary.lower()):
                results.append(row)
                if len(results) >= 100:
                    break
    return results

@router.get("/graph")
async def get_statutory_knowledge_graph() -> Dict[str, Any]:
    """
    Returns the complete multi-hop statutory & traditional knowledge graph
    linking botanicals, classical texts, patent exclusions, filing forms, and treaties.
    """
    from app.ai.retrieval.graph import GraphRetriever
    return GraphRetriever.get_full_knowledge_graph()
