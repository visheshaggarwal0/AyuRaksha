import json
import uuid
from fastapi import APIRouter, Request, Response
from starlette.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.models.schemas import StructuredAnswer, Jurisdiction
from app.agents.orchestrator import AyuRakshaOrchestrator

router = APIRouter(prefix="/chat", tags=["Ask AyuRaksha (RAG)"])
orchestrator = AyuRakshaOrchestrator()


class ChatQueryRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=2000, description="User legal/regulatory inquiry")
    jurisdiction: Jurisdiction = Jurisdiction.INDIA
    language: str = "en"


@router.post("/query", response_model=StructuredAnswer)
async def ask_ayuraksha(req: ChatQueryRequest, request: Request, response: Response):
    """
    Multi-agent, jurisdiction-isolated, citation-grounded RAG query endpoint.
    Integrates Hybrid Search, Gemma 4 31B, Citation Entailment Verification, and Safe Abstention.
    """
    req_id = request.headers.get("X-Request-ID") or f"REQ-{uuid.uuid4().hex[:8].upper()}"
    jurisdiction_str = req.jurisdiction.value if hasattr(req.jurisdiction, "value") else str(req.jurisdiction)
    result = await orchestrator.process_query(
        query=req.query,
        user_jurisdiction=jurisdiction_str,
        language=req.language,
        request_id=req_id
    )
    trace_id = (result.assessment_table or {}).get("Trace ID") or "TRC-NONE"
    response.headers["X-Request-ID"] = req_id
    response.headers["X-Trace-ID"] = trace_id
    return result


@router.post("/stream")
async def ask_ayuraksha_stream(req: ChatQueryRequest, request: Request):
    """
    Server-Sent Events (SSE) streaming endpoint emitting real-time multi-stage pipeline
    transitions, token streams, and final structured legal findings.
    """
    req_id = request.headers.get("X-Request-ID") or f"REQ-{uuid.uuid4().hex[:8].upper()}"
    jurisdiction_str = req.jurisdiction.value if hasattr(req.jurisdiction, "value") else str(req.jurisdiction)

    async def event_generator():
        async for event in orchestrator.stream_query(
            query=req.query,
            user_jurisdiction=jurisdiction_str,
            language=req.language,
            request_id=req_id
        ):
            yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Request-ID": req_id
        }
    )
