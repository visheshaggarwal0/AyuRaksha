from fastapi import APIRouter
from pydantic import BaseModel
from app.models.schemas import StructuredAnswer, Jurisdiction
from app.agents.orchestrator import AyuRakshaOrchestrator

router = APIRouter(prefix="/chat", tags=["Ask AyuRaksha (RAG)"])
orchestrator = AyuRakshaOrchestrator()

class ChatQueryRequest(BaseModel):
    query: str
    jurisdiction: Jurisdiction = Jurisdiction.INDIA
    language: str = "en"

@router.post("/query", response_model=StructuredAnswer)
async def ask_ayuraksha(req: ChatQueryRequest):
    """
    Multi-agent, jurisdiction-isolated, citation-grounded RAG query endpoint.
    Integrates Hybrid Search, OpenRouter Gemma 4 31B, Citation Entailment Verification, and Safe Abstention.
    """
    jurisdiction_str = req.jurisdiction.value if hasattr(req.jurisdiction, "value") else str(req.jurisdiction)
    result = await orchestrator.process_query(
        query=req.query,
        user_jurisdiction=jurisdiction_str,
        language=req.language
    )
    return result
