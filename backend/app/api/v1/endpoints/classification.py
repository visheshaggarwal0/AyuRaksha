import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import ProductClassificationRequest, ProductClassificationResponse
from app.engines.classifier import ProductClassifier
from app.db.session import get_db
from app.db.models import Product, ProductClassification

logger = logging.getLogger("AyuRaksha.ClassificationEndpoint")
router = APIRouter(prefix="/classification", tags=["Product Classification"])

@router.post("/evaluate", response_model=ProductClassificationResponse)
async def evaluate_product_classification(
    req: ProductClassificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates an Ayurvedic formulation and returns a deterministic classification,
    statutory governing act, patentability analysis, and verified citations.
    Persists evaluation records to Neon PostgreSQL.
    """
    try:
        # 1. Deterministic regulatory evaluation
        result = ProductClassifier.evaluate(req)

        # 2. Persist to Neon Postgres with robust error recovery
        if db is not None:
            try:
                product = Product(
                    name=req.name,
                    intended_use=req.intended_use,
                    target_market=req.target_market
                )
                db.add(product)
                await db.flush()

                classification = ProductClassification(
                    product_id=product.id,
                    category=result.category,
                    confidence=result.confidence,
                    rationale=result.patent_rationale,
                    regulatory_act=result.governing_act
                )
                db.add(classification)
                await db.commit()
                await db.refresh(product)
            except Exception as db_err:
                logger.warning(f"Database persistence skipped or failed ({type(db_err).__name__}): {db_err}")
                await db.rollback()

        return result
    except Exception as e:
        logger.error(f"Classification failure: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")
