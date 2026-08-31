from typing import List
from app.models.schemas import ABSAssessmentRequest, ABSAssessmentResponse, Citation, Jurisdiction

class ABSDecisionTree:
    """
    Evaluates obligations under the Biological Diversity Act, 2002
    (including 2023 Amendments & Decriminalization Provisions).
    """

    @staticmethod
    def evaluate(req: ABSAssessmentRequest) -> ABSAssessmentResponse:
        citations: List[Citation] = []
        mandatory_steps: List[str] = []

        # Case 1: Foreign Entity / Non-Indian / NRI / Foreign Equity
        if not req.is_indian_entity or req.is_export_intended:
            authority = "National Biodiversity Authority (NBA, Chennai)"
            approval_type = "Prior Approval (Section 3 & Form I)"
            risk = "HIGH_COMPLIANCE_MANDATE"
            
            citations.append(Citation(
                source_id="IND_BIOLOGICAL_DIVERSITY_ACT_2002",
                source_title="Biological Diversity Act, 2002 (Amended 2023)",
                section="Section 3",
                jurisdiction=Jurisdiction.INDIA,
                verbatim_quote="No person who is not a citizen of India or a body corporate not incorporated in India, or having non-Indian participation in share capital, shall obtain any biological resource occurring in India or knowledge associated thereto for research or for commercial utilisation without previous approval of the National Biodiversity Authority.",
                support_score=1.0
            ))
            citations.append(Citation(
                source_id="IND_BIOLOGICAL_DIVERSITY_ACT_2002",
                source_title="Biological Diversity Act, 2002 (Amended 2023)",
                section="Section 6",
                jurisdiction=Jurisdiction.INDIA,
                verbatim_quote="No person shall apply for any intellectual property right in or outside India for any invention based on any research or information on a biological resource obtained from India without obtaining previous approval of the National Biodiversity Authority.",
                support_score=1.0
            ))

            mandatory_steps = [
                "File NBA Form I (Access to Biological Resources) with NBA Chennai before obtaining the biological resource.",
                "Execute Access and Benefit Sharing (ABS) Agreement with NBA.",
                "If applying for a patent, file NBA Form III before the grant of the patent.",
                "Maintain full batch provenance chain of raw biological material."
            ]

            return ABSAssessmentResponse(
                resource=req.biological_resource,
                trigger_detected=True,
                governing_statute="Biological Diversity Act, 2002 (Section 3 & Section 6)",
                applicable_authority=authority,
                approval_type=approval_type,
                benefit_sharing_applicable=True,
                risk_level=risk,
                statutory_citations=citations,
                mandatory_next_steps=mandatory_steps
            )

        # Case 2: Indian Citizen / Domestic Indian MSME
        authority = f"State Biodiversity Board ({req.sourced_from_state or 'Respective SBB'})"
        approval_type = "Prior Intimation (Section 7 & Form A)"
        risk = "STANDARD_DOMESTIC_COMPLIANCE"

        citations.append(Citation(
            source_id="IND_BIOLOGICAL_DIVERSITY_ACT_2002",
            source_title="Biological Diversity Act, 2002 (Amended 2023)",
            section="Section 7",
            jurisdiction=Jurisdiction.INDIA,
            verbatim_quote="No person who is a citizen of India or a body corporate registered in India shall obtain any biological resource for commercial utilisation... except after giving prior intimation to the State Biodiversity Board concerned.",
            support_score=1.0
        ))
        citations.append(Citation(
            source_id="IND_BIOLOGICAL_DIVERSITY_ACT_2002",
            source_title="Biological Diversity Act, 2002 (Amended 2023)",
            section="Section 23 & 24",
            jurisdiction=Jurisdiction.INDIA,
            verbatim_quote="Functions of State Biodiversity Board include advising state government and regulating access by granting approvals/intimations for commercial utilization of biological resources.",
            support_score=0.95
        ))

        mandatory_steps = [
            f"Submit Form 1 (Prior Intimation) to the {authority}.",
            "Ascertain whether the biological resource is procured from registered farmers/cultivators (exempt under 2023 amendments).",
            "Maintain verifiable invoices from certified Ayurvedic raw material mandis or cultivators.",
            "If applying for Patent grant in India, submit Form III to NBA before grant."
        ]

        return ABSAssessmentResponse(
            resource=req.biological_resource,
            trigger_detected=True,
            governing_statute="Biological Diversity Act, 2002 (Section 7)",
            applicable_authority=authority,
            approval_type=approval_type,
            benefit_sharing_applicable=True,
            risk_level=risk,
            statutory_citations=citations,
            mandatory_next_steps=mandatory_steps
        )
