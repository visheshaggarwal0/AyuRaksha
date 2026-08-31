from typing import List, Dict, Any
from app.models.schemas import ProductClassificationRequest, ProductClassificationResponse, Citation, Jurisdiction

class ProductClassifier:
    """
    Deterministic rule engine for classifying Ayurvedic products under:
    - Drugs & Cosmetics Act, 1940 (First Schedule & ASU provisions)
    - FSSAI (Ayurveda Aahara) Regulations, 2022
    - Cosmetics Rules, 2020
    - Patents Act, 1970 (Section 3 exclusions)
    """

    @staticmethod
    def evaluate(req: ProductClassificationRequest) -> ProductClassificationResponse:
        citations: List[Citation] = []
        next_actions: List[str] = []

        # Rule 1: Classical Ayurvedic Medicine (Shastriya formulation)
        if req.in_classical_text and not req.is_formulation_modified and not req.has_novel_excipients:
            category = "CLASSICAL_AYURVEDIC_MEDICINE (Shastriya)"
            governing_act = "Drugs & Cosmetics Act, 1940 (First Schedule)"
            patentability = "BARRED_UNDER_SECTION_3P"
            patent_rationale = (
                "Classical Ayurvedic formulations verbatim from First Schedule texts are known traditional "
                "knowledge and statutorily barred from patenting under Section 3(p) and Section 3(e) of the Indian Patents Act."
            )
            abs_req = True
            reg_authority = "State Licensing Authority (AYUSH)"
            
            citations.append(Citation(
                source_id="IND_PATENTS_ACT_1970",
                source_title="Patents Act, 1970",
                section="Section 3(p)",
                jurisdiction=Jurisdiction.INDIA,
                verbatim_quote="An invention which in effect is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components is not an invention.",
                support_score=1.0
            ))
            citations.append(Citation(
                source_id="IND_DRUGS_COSMETICS_ACT_1940",
                source_title="Drugs and Cosmetics Act, 1940",
                section="Section 3(a)",
                jurisdiction=Jurisdiction.INDIA,
                verbatim_quote="Ayurvedic, Siddha or Unani drug includes all medicines intended for internal or external use for or in the diagnosis, treatment, mitigation or prevention of disease... manufactured exclusively in accordance with the formulae described in the authoritative books specified in the First Schedule.",
                support_score=1.0
            ))
            
            next_actions = [
                "Obtain Classical Ayurvedic Manufacturing License from State AYUSH Licensing Authority.",
                "Ensure strict batch manufacturing adherence to Ayurvedic Pharmacopoeia of India (API) monographs.",
                "Protect brand and packaging through Trademark and Design registration (Patents are barred).",
                "Submit prior intimation to State Biodiversity Board (SBB) for biological resource sourcing."
            ]

            return ProductClassificationResponse(
                product_name=req.name,
                category=category,
                governing_act=governing_act,
                patentability=patentability,
                patent_rationale=patent_rationale,
                abs_required=abs_req,
                regulatory_authority=reg_authority,
                citations=citations,
                confidence=1.0,
                next_actions=next_actions
            )

        # Rule 2: Patent or Proprietary Ayurvedic Medicine (Anubhuta / Modified)
        if (req.in_classical_text and req.is_formulation_modified) or (not req.in_classical_text and req.disease_treatment_claims):
            category = "PATENT_OR_PROPRIETARY_ASU_MEDICINE (Anubhuta / Modified)"
            governing_act = "Drugs & Cosmetics Act, 1940 (Section 3(h)) & Rule 158B"
            patentability = "POTENTIALLY_PATENTABLE_WITH_EVIDENCE"
            patent_rationale = (
                "Formulation may be patentable ONLY if you can demonstrate a novel synergistic efficacy, "
                "novel extraction process, or non-obvious therapeutic effect to overcome Section 3(e) (mere admixture) and Section 3(p)."
            )
            abs_req = True
            reg_authority = "State Licensing Authority (AYUSH) + CDSCO (if Phytopharmaceutical)"
            
            citations.append(Citation(
                source_id="IND_PATENTS_ACT_1970",
                source_title="Patents Act, 1970",
                section="Section 3(e)",
                jurisdiction=Jurisdiction.INDIA,
                verbatim_quote="A substance obtained by a mere admixture resulting only in the aggregation of the properties of the components thereof or a process for producing such substance is not patentable.",
                support_score=0.95
            ))
            citations.append(Citation(
                source_id="IND_DRUGS_COSMETICS_ACT_1940",
                source_title="Drugs and Cosmetics Act, 1940",
                section="Section 3(h) & Rule 158B",
                jurisdiction=Jurisdiction.INDIA,
                verbatim_quote="Patent or Proprietary medicine in relation to Ayurvedic, Siddha or Unani systems means a drug which is a remedy or prescription... not included in the First Schedule.",
                support_score=0.98
            ))
            
            next_actions = [
                "Conduct quantitative synergy / efficacy study to defeat Section 3(e) prior to filing patent.",
                "Conduct prior-art search across public TKDL and Ayurvedic literature.",
                "Apply for Proprietary ASU Drug License under Rule 158B with proof of safety and effectiveness.",
                "Ensure Mandatory NBA Form III filing before seeking patent grant if Indian biological resources are utilized."
            ]

            return ProductClassificationResponse(
                product_name=req.name,
                category=category,
                governing_act=governing_act,
                patentability=patentability,
                patent_rationale=patent_rationale,
                abs_required=abs_req,
                regulatory_authority=reg_authority,
                citations=citations,
                confidence=0.95,
                next_actions=next_actions
            )

        # Rule 3: Ayurveda Aahara (Food / Health Supplement)
        if req.intended_use in ["supplement", "food"] and not req.disease_treatment_claims:
            category = "AYURVEDA_AAHARA (Food Supplement)"
            governing_act = "Food Safety and Standards (Ayurveda Aahara) Regulations, 2022"
            patentability = "NOT_RECOMMENDED (Food composition exclusions)"
            patent_rationale = (
                "Food supplement formulations are generally excluded unless a novel manufacturing method is established. "
                "Cannot claim disease treatment/mitigation without AYUSH Drug licensing."
            )
            abs_req = True
            reg_authority = "FSSAI (Food Safety and Standards Authority of India)"
            
            citations.append(Citation(
                source_id="IND_FSSAI_AYURVEDA_AAHARA_2022",
                source_title="FSSAI (Ayurveda Aahara) Regulations, 2022",
                section="Regulation 3 & Schedule A",
                jurisdiction=Jurisdiction.INDIA,
                verbatim_quote="Ayurveda Aahara means food prepared in accordance with recipes or ingredients specified in authoritative books of Ayurveda... shall not include Ayurvedic drugs or synthetic vitamins/minerals.",
                support_score=1.0
            ))
            
            next_actions = [
                "Apply for FSSAI Central License under Ayurveda Aahara category with dedicated Ayurveda Aahara logo.",
                "Ensure labelling states: 'This product is not intended to diagnose, treat, cure or prevent any disease'.",
                "Comply with biological resource access rules (SBB notification)."
            ]

            return ProductClassificationResponse(
                product_name=req.name,
                category=category,
                governing_act=governing_act,
                patentability=patentability,
                patent_rationale=patent_rationale,
                abs_required=abs_req,
                regulatory_authority=reg_authority,
                citations=citations,
                confidence=0.92,
                next_actions=next_actions
            )

        # Rule 4: Cosmetic
        category = "AYURVEDIC_COSMETIC"
        governing_act = "Cosmetics Rules, 2020 / D&C Act"
        patentability = "CONDITIONAL (Formulation / Delivery mechanism)"
        patent_rationale = "Cosmetic formulations can be branded and protected via Trademarks and Industrial Designs."
        reg_authority = "State Licensing Authority (Cosmetics)"
        
        citations.append(Citation(
            source_id="IND_COSMETICS_RULES_2020",
            source_title="Cosmetics Rules, 2020",
            section="Rule 2 & Chapter III",
            jurisdiction=Jurisdiction.INDIA,
            verbatim_quote="Cosmetic means any article intended to be rubbed, poured, sprinkled or sprayed on... the human body for cleansing, beautifying, promoting attractiveness.",
            support_score=0.90
        ))
        
        return ProductClassificationResponse(
            product_name=req.name,
            category=category,
            governing_act=governing_act,
            patentability=patentability,
            patent_rationale=patent_rationale,
            abs_required=True,
            regulatory_authority=reg_authority,
            citations=citations,
            confidence=0.88,
            next_actions=[
                "Apply for Cosmetic Manufacturing License.",
                "File Trademark for brand name and Design for cosmetic container/packaging."
            ]
        )
