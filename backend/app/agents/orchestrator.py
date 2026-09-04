"""
AyuRaksha Orchestrator Adapter
Bridges FastAPI endpoints to the production 10-module orchestration_module,
guaranteeing 100% backwards compatibility with existing UI contracts.
"""
import logging
from typing import Dict, Any, List, Optional

from app.modules.orchestration import orchestration_module
from app.models.schemas import StructuredAnswer, Citation, ClaimVerification

logger = logging.getLogger("AyuRaksha.Orchestrator")


class AyuRakshaOrchestrator:
    """
    Central Decision Engine for AyuRaksha.
    Delegates to the decoupled 10-module orchestration_module while preserving
    existing FastAPI and frontend response schemas.
    """

    def __init__(self):
        self.orchestrator = orchestration_module

    async def process_query(
        self,
        query: str,
        user_jurisdiction: str = "IN",
        language: str = "en",
        request_id: Optional[str] = None
    ) -> StructuredAnswer:
        resp = await self.orchestrator.process_query(
            query=query,
            jurisdiction=user_jurisdiction,
            language=language,
            request_id=request_id
        )

        jur_val = resp.jurisdiction.value if hasattr(resp.jurisdiction, "value") else str(resp.jurisdiction)

        # Map Citations
        citations = [
            Citation(
                source_id=c.source_id,
                source_title=c.source_title,
                section=c.section,
                subsection=c.subsection,
                jurisdiction=jur_val,
                official_url=c.official_url,
                support_score=c.support_score,
                verbatim_quote=c.verbatim_quote
            )
            for c in resp.citations
        ]

        # Map Verified Claims with genuine sentence-to-citation links
        verified_claims = [
            ClaimVerification(
                claim=vc.claim,
                is_supported=vc.is_supported,
                confidence_score=vc.confidence_score,
                supporting_citations=[
                    Citation(
                        source_id=sc.source_id,
                        source_title=sc.source_title,
                        section=sc.section,
                        jurisdiction=jur_val,
                        official_url=sc.official_url,
                        support_score=sc.support_score,
                        verbatim_quote=sc.verbatim_quote
                    )
                    for sc in vc.supporting_citations
                ]
            )
            for vc in resp.verified_claims
        ]

        recommended_action = (
            " · ".join(resp.next_actions)
            if resp.next_actions
            else "Consult the State Licensing Authority (SLA) or an empaneled patent attorney."
        )

        return StructuredAnswer(
            direct_answer=resp.direct_answer,
            jurisdiction=jur_val,
            assessment_table=resp.assessment_table,
            verified_claims=verified_claims,
            citations=citations,
            confidence_level=resp.confidence.level.value if hasattr(resp.confidence.level, "value") else str(resp.confidence.level),
            caveats=resp.confidence.caveats,
            recommended_next_action=recommended_action,
            safe_abstention=resp.safe_abstention,
            abstention_reason=resp.abstention_reason.description if resp.abstention_reason else None,
            cross_border_posture=resp.cross_border_posture,
            language=resp.language,
            execution_mode=getattr(resp, "execution_mode", "GUIDED_RAG"),
            resolved_concepts=getattr(resp, "resolved_concepts", []),
            evidence_pack=resp.evidence_pack.model_dump() if getattr(resp, "evidence_pack", None) else None,
            diagnostics=resp.diagnostics,
            latency_breakdown=resp.latency_breakdown
        )

    async def stream_query(
        self,
        query: str,
        user_jurisdiction: str = "IN",
        language: str = "en",
        request_id: Optional[str] = None
    ):
        """Streams multi-stage pipeline events, tokens, and final StructuredAnswer."""
        async for event in self.orchestrator.stream_query(
            query=query,
            jurisdiction=user_jurisdiction,
            language=language,
            request_id=request_id
        ):
            if event["event"] == "result":
                raw_resp = event["data"]
                jur_val = raw_resp.get("jurisdiction", user_jurisdiction)
                citations = [
                    Citation(
                        source_id=c.get("source_id", "STATUTE"),
                        source_title=c.get("source_title", "Statutory Source"),
                        section=c.get("section", "Section X"),
                        subsection=c.get("subsection"),
                        jurisdiction=jur_val,
                        official_url=c.get("official_url"),
                        support_score=c.get("support_score", 0.9),
                        verbatim_quote=c.get("verbatim_quote", "")
                    )
                    for c in raw_resp.get("citations", [])
                ]
                verified_claims = [
                    ClaimVerification(
                        claim=vc.get("claim", ""),
                        is_supported=vc.get("is_supported", True),
                        confidence_score=vc.get("confidence_score", 0.9),
                        supporting_citations=citations[:1]
                    )
                    for vc in raw_resp.get("verified_claims", [])
                ]
                next_acts = raw_resp.get("next_actions", [])
                recommended_action = " · ".join(next_acts) if next_acts else "Consult the State Licensing Authority (SLA)."
                conf = raw_resp.get("confidence", {})
                conf_lvl = conf.get("level", "MODERATE")
                if hasattr(conf_lvl, "value"):
                    conf_lvl = conf_lvl.value

                structured = StructuredAnswer(
                    direct_answer=raw_resp.get("direct_answer", ""),
                    jurisdiction=jur_val,
                    assessment_table=raw_resp.get("assessment_table", {}),
                    verified_claims=verified_claims,
                    citations=citations,
                    confidence_level=str(conf_lvl),
                    caveats=conf.get("caveats", []),
                    recommended_next_action=recommended_action,
                    safe_abstention=raw_resp.get("safe_abstention", False),
                    abstention_reason=raw_resp.get("abstention_reason", {}).get("description") if raw_resp.get("abstention_reason") else None,
                    cross_border_posture=raw_resp.get("cross_border_posture"),
                    language=raw_resp.get("language", language)
                )
                yield {"event": "result", "data": structured.model_dump()}
            else:
                yield event
