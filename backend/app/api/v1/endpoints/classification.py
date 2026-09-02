from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas import ProductClassificationRequest, ProductClassificationResponse
from app.engines.classifier import ProductClassifier
from app.db.session import get_db
from app.db.models import Product, ProductClassification

router = APIRouter(prefix="/classification", tags=["Product Classification"])

@router.post("/evaluate", response_model=ProductClassificationResponse)
async def evaluate_product_classification(
    req: ProductClassificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Evaluates an Ayurvedic formulation and returns a deterministic classification,
    statutory governing act, patentability analysis, and verified citations.
    """
    try:
        result = await ProductClassifier.evaluate(req)
        
        # Persist to Neon Postgres
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
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")
