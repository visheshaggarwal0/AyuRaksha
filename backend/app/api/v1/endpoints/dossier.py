"""
FastAPI Endpoints for Active Compliance Dossier Generation & Export (SIH 26045)
Provides one-click generation of audit-ready regulatory dossiers.
"""
from fastapi import APIRouter, HTTPException, Response
from app.models.dossier import DossierGenerationRequest, ComplianceDossierResponse
from app.engines.dossier_generator import ComplianceDossierGenerator

router = APIRouter(prefix="/dossier", tags=["Active Compliance Dossier"])


@router.post("/generate", response_model=ComplianceDossierResponse)
async def generate_compliance_dossier(req: DossierGenerationRequest):
    """
    Synthesizes an audit-ready regulatory and IP compliance roadmap for an Ayurvedic product.
    Integrates botanical taxonomy, deterministic classification, ABS tree, milestone fees,
    and cryptographically verified citations.
    """
    try:
        dossier = ComplianceDossierGenerator.generate_dossier(req)
        return dossier
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dossier generation failed: {str(e)}")


@router.post("/export-markdown")
async def export_dossier_markdown(req: DossierGenerationRequest):
    """
    Generates and returns the compliance dossier formatted as a downloadable Markdown document.
    """
    try:
        dossier = ComplianceDossierGenerator.generate_dossier(req)
        filename = f"{req.product_name.lower().replace(' ', '_')}_compliance_dossier.md"
        return Response(
            content=dossier.markdown_report,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dossier export failed: {str(e)}")


@router.get("/sample", response_model=ComplianceDossierResponse)
async def get_sample_dossier():
    """
    Generates an instant sample compliance dossier for a modern Phytopharmaceutical formulation.
    """
    sample_req = DossierGenerationRequest(
        product_name="AshwaCurcumin Standardized Neuro-Protective Extract",
        ingredients=["Ashwagandha", "Turmeric", "Black Pepper"],
        in_classical_text=False,
        is_formulation_modified=True,
        is_purified_standardized_fraction=True,
        intended_use="therapeutic",
        disease_treatment_claims=True,
        is_indian_entity=True,
        target_market="CROSS_BORDER"
    )
    return ComplianceDossierGenerator.generate_dossier(sample_req)
