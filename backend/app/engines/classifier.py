import inspect
from typing import List, Optional
from app.models.schemas import ProductClassificationRequest, ProductClassificationResponse, Citation, Jurisdiction

class ProductClassifier:
    """
    Deterministic Statutory Regulatory Decision Tree for Ayurvedic Formulations:
    - Rule 1: Classical ASU Medicine (Shastriya) — Sec 3(a) & First Schedule + Sec 3(p) Patent Bar
    - Rule 2: Patent / Proprietary ASU Medicine (Anubhuta / Modified) — Sec 3(h) / Rule 158B + Sec 3(e) Synergy
    - Rule 3: Ayurveda Aahara (Food Supplement) — FSSAI 2022 Reg 3 / Schedule A
    - Rule 4: Ayurvedic Cosmetic — Cosmetics Rules 2020
    """

    @staticmethod
    def evaluate(req: ProductClassificationRequest) -> ProductClassificationResponse:
        # Rule 1 — Classical ASU Medicine (Shastriya)
        # Authoritative texts in First Schedule, unmodified formulation, no novel excipients.
        # Takes precedence even if intended_use is supplement and no disease claims are made.
        if req.in_classical_text and not req.is_formulation_modified and not req.has_novel_excipients:
            return ProductClassificationResponse(
                product_name=req.name,
                category="CLASSICAL_AYURVEDIC_MEDICINE (Shastriya)",
                governing_act="Drugs & Cosmetics Act, 1940 (First Schedule & Sec 3(a))",
                patentability="BARRED_UNDER_SECTION_3P",
                patent_rationale=(
                    "Section 3(p) of the Patents Act, 1970 bars patentability of traditional knowledge "
                    "or an aggregation/duplication of known properties of traditionally known components. "
                    "Since this formulation is strictly prepared according to classical authoritative texts "
                    "in the First Schedule, it is public traditional knowledge and not patentable as a novel chemical entity."
                ),
                abs_required=True,
                regulatory_authority="State Licensing Authority (AYUSH)",
                citations=[
                    Citation(
                        source_id="IND_DRUGS_AND_COSMETICS_ACT_1940",
                        source_title="Drugs and Cosmetics Act, 1940",
                        section="Section 3(a)",
                        jurisdiction=Jurisdiction.INDIA,
                        verbatim_quote=(
                            "Ayurvedic, Siddha or Unani drug includes all medicines intended for internal or "
                            "external use for or in the diagnosis, treatment, mitigation or prevention of disease "
                            "or disorder in human beings or animals, and manufactured exclusively in accordance with "
                            "the formulae described in the authoritative books of Ayurvedic, Siddha and Unani Tibb systems "
                            "of medicine, specified in the First Schedule."
                        ),
                        support_score=1.0
                    ),
                    Citation(
                        source_id="IND_PATENTS_ACT_1970",
                        source_title="The Patents Act, 1970",
                        section="Section 3(p)",
                        jurisdiction=Jurisdiction.INDIA,
                        verbatim_quote=(
                            "An invention which in effect is traditional knowledge or which is an aggregation or "
                            "duplication of known properties of traditionally known component or components is "
                            "not an invention within the meaning of this Act."
                        ),
                        support_score=1.0
                    )
                ],
                confidence=1.0,
                next_actions=[
                    "Apply for Classical Ayurvedic Manufacturing License (Form 25D) with the State Licensing Authority (AYUSH).",
                    "Ensure raw materials comply strictly with Ayurvedic Pharmacopoeia of India (API) standards.",
                    "Submit prior intimation to the State Biodiversity Board (SBB) under Section 7 of the Biological Diversity Act, 2002.",
                    "Comply with Good Manufacturing Practices (GMP) under Schedule T of the Drugs & Cosmetics Rules, 1945."
                ]
            )

        # Rule 1B — Phytopharmaceutical Drug (CDSCO / GSR 918(E) & New Drugs Rules 2019)
        # Purified, standardized fractions with defined marker compounds from medicinal plants,
        # intended for therapeutic disease treatment claims. Legally distinct from Proprietary ASU.
        is_phytopharmaceutical = (
            getattr(req, "is_purified_standardized_fraction", False)
            and req.intended_use == "therapeutic"
            and req.disease_treatment_claims
            and not req.in_classical_text
        )

        if is_phytopharmaceutical:
            return ProductClassificationResponse(
                product_name=req.name,
                category="PHYTOPHARMACEUTICAL_DRUG (CDSCO / GSR 918E)",
                governing_act="Drugs and Cosmetics Rules, 1945 (Rule 122E / GSR 918(E)) & New Drugs Rules 2019",
                patentability="PATENTABLE_SUBJECT_TO_NOVELTY_AND_EFFICACY",
                patent_rationale=(
                    "High patentability potential under Section 2(1)(j) of the Patents Act, 1970 as an isolated, "
                    "purified, and standardized herbal bioactive fraction. Must overcome Section 3(p) prior art "
                    "by demonstrating non-obvious therapeutic activity exceeding raw crude plant material and "
                    "Section 3(e) synergistic efficacy."
                ),
                abs_required=True,
                regulatory_authority="Central Drugs Standard Control Organization (CDSCO) / DCGI",
                citations=[
                    Citation(
                        source_id="IND_DRUGS_COSMETICS_RULES_1945_GSR_918E",
                        source_title="Drugs and Cosmetics Rules, 1945 (Gazette G.S.R. 918(E))",
                        section="Rule 122E / Fourth Schedule",
                        jurisdiction=Jurisdiction.INDIA,
                        verbatim_quote=(
                            "Phytopharmaceutical drug means a purified and standardized fraction with defined minimum "
                            "four bioactive or analytical marker compounds of an extract of a medicinal plant or its part, "
                            "for internal or external use of human beings or animals for diagnosis, treatment, mitigation "
                            "or prevention of any disease or disorder, but does not include administration by parenteral route."
                        ),
                        support_score=1.0
                    ),
                    Citation(
                        source_id="IND_PATENTS_ACT_1970",
                        source_title="The Patents Act, 1970",
                        section="Section 2(1)(j) & Section 3(p)",
                        jurisdiction=Jurisdiction.INDIA,
                        verbatim_quote=(
                            "Invention means a new product or process involving an inventive step and capable of industrial "
                            "application, distinguished from mere aggregation of traditional knowledge."
                        ),
                        support_score=0.95
                    )
                ],
                confidence=0.98,
                next_actions=[
                    "Submit Investigational New Drug (IND) Application in Form CT-18 / CT-21 to CDSCO (DCGI).",
                    "Develop Common Technical Document (CTD) dossier establishing chemical fingerprinting with minimum 4 analytical/bioactive marker compounds.",
                    "Conduct non-clinical safety pharmacology, toxicology, and Phase I-III human clinical trials as per New Drugs and Clinical Trials Rules, 2019.",
                    "Obtain National Biodiversity Authority (NBA) approval on Form III prior to patent grant under Section 6 of BDA 2002."
                ]
            )

        # Rule 2 — Patent / Proprietary ASU Medicine (Anubhuta / Modified)
        # Classical formulation modified OR non-classical with disease claims OR novel excipients with disease claims.
        is_modified_classical = req.in_classical_text and req.is_formulation_modified
        is_novel_therapeutic = not req.in_classical_text and req.disease_treatment_claims
        is_novel_excipients_therapeutic = req.has_novel_excipients and req.disease_treatment_claims

        if is_modified_classical or is_novel_therapeutic or is_novel_excipients_therapeutic:
            return ProductClassificationResponse(
                product_name=req.name,
                category="PATENT_OR_PROPRIETARY_ASU_MEDICINE (Anubhuta / Modified)",
                governing_act="Drugs & Cosmetics Act, 1940 (Rule 158B & Sec 3(h))",
                patentability="POTENTIALLY_PATENTABLE_WITH_EVIDENCE",
                patent_rationale=(
                    "Potentially patentable under the Patents Act, 1970 if novel extraction, non-obvious "
                    "synergistic efficacy (surpassing mere aggregation under Section 3(e)), and technical "
                    "advancement are demonstrated with comparative experimental data."
                ),
                abs_required=True,
                regulatory_authority="State Licensing Authority (AYUSH)",
                citations=[
                    Citation(
                        source_id="IND_DRUGS_AND_COSMETICS_ACT_1940",
                        source_title="Drugs and Cosmetics Rules, 1945",
                        section="Rule 158B",
                        jurisdiction=Jurisdiction.INDIA,
                        verbatim_quote=(
                            "Guidelines for issue of license with respect to patent or proprietary ayurvedic medicine. "
                            "Proof of effectiveness and safety data as per published literature or pilot clinical trial "
                            "required depending on category."
                        ),
                        support_score=0.95
                    ),
                    Citation(
                        source_id="IND_PATENTS_ACT_1970",
                        source_title="The Patents Act, 1970",
                        section="Section 3(e)",
                        jurisdiction=Jurisdiction.INDIA,
                        verbatim_quote=(
                            "A substance obtained by a mere admixture resulting only in the aggregation of the properties "
                            "of the components thereof or a process for producing such substance is not an invention."
                        ),
                        support_score=0.95
                    )
                ],
                confidence=0.95,
                next_actions=[
                    "Apply for Proprietary Ayurvedic Medicine License under Rule 158B with proof of safety/efficacy data.",
                    "File patent application demonstrating non-obvious synergistic therapeutic effect under Section 3(e)."
                ]
            )

        # Rule 3 — Ayurveda Aahara (Food Supplement)
        # Not in classical texts, NO disease treatment claims, intended for food or supplement use.
        if not req.in_classical_text and not req.disease_treatment_claims and req.intended_use in ["supplement", "food"]:
            return ProductClassificationResponse(
                product_name=req.name,
                category="AYURVEDA_AAHARA (Food Supplement)",
                governing_act="Food Safety and Standards (Ayurveda Aahara) Regulations, 2022",
                patentability="NOT_PATENTABLE_UNDER_SECTION_3E",
                patent_rationale=(
                    "Conventional food supplement formulations are generally considered admixtures under Section 3(e) "
                    "unless a non-obvious proprietary delivery mechanism or specialized synergistic formulation is demonstrated."
                ),
                abs_required=True,
                regulatory_authority="Food Safety and Standards Authority of India (FSSAI)",
                citations=[
                    Citation(
                        source_id="IND_FSSAI_AYURVEDA_AAHARA_2022",
                        source_title="Food Safety and Standards (Ayurveda Aahara) Regulations, 2022",
                        section="Regulation 3 & Schedule A",
                        jurisdiction=Jurisdiction.INDIA,
                        verbatim_quote=(
                            "Ayurveda Aahara specifies food prepared in accordance with the recipes or books specified "
                            "in Schedule A of these regulations, and does not include ayurvedic drugs. No disease prevention "
                            "or cure claims are permitted."
                        ),
                        support_score=0.92
                    )
                ],
                confidence=0.92,
                next_actions=[
                    "Apply for FSSAI Central License under the Ayurveda Aahara category.",
                    "Affix the mandatory Ayurveda Aahara logo and print disclaimer: 'This product is not intended to diagnose, treat, cure or prevent any disease.'",
                    "Ensure all botanical ingredients are listed in Schedule A of the Ayurveda Aahara Regulations.",
                    "Maintain complete supply chain provenance and FSSAI FoSTaC compliance."
                ]
            )

        # Rule 4 — Cosmetic Fallback
        # Cosmetics Rules 2020: for cosmetic use or non-disease non-supplement intent.
        return ProductClassificationResponse(
            product_name=req.name,
            category="AYURVEDIC_COSMETIC",
            governing_act="Cosmetics Rules, 2020 (under Drugs and Cosmetics Act, 1940)",
            patentability="CONDITIONAL (Formulation / Delivery mechanism)",
            patent_rationale=(
                "Cosmetic topical applications are not patentable for known herbal properties, "
                "but novel delivery matrices or stabilization techniques may qualify under the Patents Act, 1970."
            ),
            abs_required=True,
            regulatory_authority="State Licensing Authority (Cosmetics)",
            citations=[
                Citation(
                    source_id="IND_COSMETICS_RULES_2020",
                    source_title="Cosmetics Rules, 2020",
                    section="Rule 2 & Part II",
                    jurisdiction=Jurisdiction.INDIA,
                    verbatim_quote=(
                        "Cosmetic means any article intended to be rubbed, poured, sprinkled or sprayed on, "
                        "or introduced into, or otherwise applied to, the human body or any part thereof for "
                        "cleansing, beautifying, promoting attractiveness, or altering the appearance."
                    ),
                    support_score=0.88
                )
            ],
            confidence=0.88,
            next_actions=[
                "Obtain Cosmetic Manufacturing License (Form COS-8) from State Licensing Authority.",
                "Ensure compliance with Bureau of Indian Standards (BIS) for cosmetic safety and heavy metal limits.",
                "Refrain from making medicinal or therapeutic disease treatment claims on packaging."
            ]
        )

    @classmethod
    async def evaluate_async(cls, req: ProductClassificationRequest) -> ProductClassificationResponse:
        """Async convenience alias for async callers."""
        return cls.evaluate(req)
