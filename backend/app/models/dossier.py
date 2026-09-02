"""
AyuRaksha Active Compliance Dossier Models (SIH 26045)
Defines strongly typed schemas for generating, auditing, and exporting
official Regulatory & IP Compliance Dossiers for Ayurvedic products.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.models.schemas import Citation


class DossierGenerationRequest(BaseModel):
    """Request payload to generate a complete compliance dossier."""
    product_name: str = Field(..., description="Trade or formulation name")
    ingredients: List[str] = Field(default_factory=list, description="List of botanical or mineral ingredients")
    in_classical_text: bool = Field(default=False, description="Whether formulation is from authoritative classical text")
    is_formulation_modified: bool = Field(default=False, description="Whether traditional formula/ratio is modified")
    is_purified_standardized_fraction: bool = Field(default=False, description="Whether product is a standardized fraction (Phytopharmaceutical)")
    intended_use: str = Field(default="therapeutic", description="therapeutic, supplement, cosmetic, food")
    disease_treatment_claims: bool = Field(default=True)
    is_indian_entity: bool = Field(default=True, description="Whether applicant is Indian citizen/entity with no foreign equity")
    target_market: str = Field(default="IN", description="IN, INT, CROSS_BORDER, US, EU")
    language: str = Field(default="en")


class FilingMilestone(BaseModel):
    """Actionable statutory filing milestone with statutory authority, form, fee, and timeline."""
    step_number: int
    title: str
    authority: str
    mandatory_form: str
    statutory_timeline: str
    fee_estimate: str
    action_details: str


class ComplianceDossierResponse(BaseModel):
    """Complete, audit-ready compliance dossier ready for regulatory submission."""
    dossier_id: str
    generated_at: datetime
    product_profile: Dict[str, Any]
    regulatory_classification: Dict[str, Any]
    abs_roadmap: Dict[str, Any]
    filing_roadmap: List[FilingMilestone]
    verifiable_citations: List[Citation]
    cross_border_posture: Optional[Dict[str, str]] = None
    markdown_report: str
