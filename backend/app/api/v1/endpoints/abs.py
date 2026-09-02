import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import ABSAssessmentRequest, ABSAssessmentResponse
from app.engines.abs_tree import ABSDecisionTree
from app.db.session import get_db
from app.db.models import ABSAssessment

logger = logging.getLogger("AyuRaksha.ABSEndpoint")
router = APIRouter(prefix="/abs", tags=["ABS & Biodiversity Navigator"])

@router.post("/evaluate", response_model=ABSAssessmentResponse)
async def evaluate_abs_compliance(
    req: ABSAssessmentRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates Access and Benefit Sharing (ABS) obligations under the Biological Diversity Act,
    returning whether SBB Prior Intimation or NBA Prior Approval is mandated.
    Persists evaluation records to Neon PostgreSQL.
    """
    try:
        # 1. Deterministic ABS Evaluation
        result = ABSDecisionTree.evaluate(req)

        # 2. Persist to Neon Postgres with robust error recovery
        if db is not None:
            try:
                abs_record = ABSAssessment(
                    biological_resource=req.biological_resource,
                    origin=req.origin_country,
                    purpose="commercial" if req.is_commercial_utilization else "research",
                    traditional_knowledge=req.is_traditional_knowledge_associated,
                    foreign_involvement=not req.is_indian_entity or req.is_export_intended,
                    assessment=result.approval_type,
                    confidence=1.0,
                    rationale=f"Governing statute: {result.governing_statute}"
                )
                db.add(abs_record)
                await db.commit()
                await db.refresh(abs_record)
            except Exception as db_err:
                logger.warning(f"ABS assessment persistence skipped or failed ({type(db_err).__name__}): {db_err}")
                await db.rollback()

        return result
    except Exception as e:
        logger.error(f"ABS evaluation failure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"ABS evaluation error: {str(e)}")
