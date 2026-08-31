from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import ABSAssessmentRequest, ABSAssessmentResponse
from app.engines.abs_tree import ABSDecisionTree
from app.db.session import get_db
from app.db.models import ABSAssessment

router = APIRouter(prefix="/abs", tags=["ABS & Biodiversity Navigator"])

@router.post("/evaluate", response_model=ABSAssessmentResponse)
async def evaluate_abs_compliance(
    req: ABSAssessmentRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates Access and Benefit Sharing (ABS) obligations under the Biological Diversity Act,
    returning whether SBB Prior Intimation or NBA Prior Approval is mandated.
    """
    try:
        result = ABSDecisionTree.evaluate(req)
        
        # Persist to Neon Postgres
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
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ABS evaluation error: {str(e)}")
