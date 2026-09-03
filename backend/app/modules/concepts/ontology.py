"""
AyuRaksha Legal Concept Ontology
Defines domain concepts, semantic triggers, and statutory target mappings
for Indian and International AYUSH regulatory frameworks.
"""
from enum import Enum
from typing import List, Set, Dict
from pydantic import BaseModel, Field


class LegalDomain(str, Enum):
    PATENTABILITY = "PATENTABILITY"
    BIODIVERSITY_ABS = "BIODIVERSITY_ABS"
    DRUG_CLASSIFICATION = "DRUG_CLASSIFICATION"
    SAFETY_PROHIBITION = "SAFETY_PROHIBITION"
    EXPORT_INTERNATIONAL = "EXPORT_INTERNATIONAL"
    TRADEMARKS_IP = "TRADEMARKS_IP"


class ConceptDefinition(BaseModel):
    concept_id: str
    domain: LegalDomain
    name: str
    description: str
    semantic_triggers: Set[str]
    statutory_provisions: List[str]
    statutory_hooks: List[str]
    hierarchy_priority: int = 5


LEGAL_CONCEPTS_TAXONOMY: Dict[str, ConceptDefinition] = {
    # ------------------------------------------------------------------------
    # Patentability Concepts (The Patents Act, 1970)
    # ------------------------------------------------------------------------
    "INVENTIVE_STEP": ConceptDefinition(
        concept_id="INVENTIVE_STEP",
        domain=LegalDomain.PATENTABILITY,
        name="Inventive Step / Non-Obviousness",
        description="Feature of an invention that involves technical advance over existing knowledge or economic significance making it non-obvious to a person skilled in the art.",
        semantic_triggers={
            "inventive step", "inventive", "technical advance", "economic significance",
            "non-obvious", "non obvious", "skilled in the art", "advance over prior art",
            "technological superiority", "inventive feature", "superior bioavailability",
            "extraction process", "delivery system", "phytosomal delivery", "nano-emulsion"
        },
        statutory_provisions=["PATENTS_ACT_1970_SEC_2_1_JA"],
        statutory_hooks=["Section 2(1)(ja) inventive step technical advance economic significance"],
        hierarchy_priority=9
    ),

    "NOVELTY": ConceptDefinition(
        concept_id="NOVELTY",
        domain=LegalDomain.PATENTABILITY,
        name="Novelty / Industrial Application",
        description="New product or process not anticipated by prior publication or use.",
        semantic_triggers={
            "novel", "novelty", "new product", "new process", "anticipation",
            "prior publication", "prior use", "public knowledge", "industrial application",
            "patentable product", "patentable process"
        },
        statutory_provisions=["PATENTS_ACT_1970_SEC_2_1_J", "PATENTS_ACT_1970_SEC_2_1_L"],
        statutory_hooks=["Section 2(1)(j) invention product process", "Section 2(1)(l) new invention novelty"],
        hierarchy_priority=8
    ),

    "TRADITIONAL_KNOWLEDGE_EXCLUSION": ConceptDefinition(
        concept_id="TRADITIONAL_KNOWLEDGE_EXCLUSION",
        domain=LegalDomain.PATENTABILITY,
        name="Traditional Knowledge Exclusion",
        description="Invention which is traditional knowledge or aggregation of known properties is non-patentable.",
        semantic_triggers={
            "traditional knowledge", "ayurvedic", "herbal composition", "ancient text",
            "samhita", "known properties", "classical formulation", "churna", "taila",
            "rasayana", "bhasma", "ashwagandha", "brahmi", "guggulu", "nimba", "haridra",
            "curcumin", "neem", "haldi", "tulsi", "home remedy", "folk medicine", "tkdl"
        },
        statutory_provisions=["PATENTS_ACT_1970_SEC_3_P"],
        statutory_hooks=["Section 3(p) traditional knowledge aggregation known properties not an invention"],
        hierarchy_priority=10
    ),

    "MERE_ADMIXTURE_SYNERGY": ConceptDefinition(
        concept_id="MERE_ADMIXTURE_SYNERGY",
        domain=LegalDomain.PATENTABILITY,
        name="Mere Admixture vs Synergistic Interaction",
        description="Substances obtained by mere admixture resulting only in aggregation of properties are non-patentable without synergy.",
        semantic_triggers={
            "combination", "synergy", "synergistic", "admixture", "aggregate",
            "aggregation", "compound formulation", "ratio", "mixing", "combining components",
            "herbal mixture", "multi-herb", "polyherbal"
        },
        statutory_provisions=["PATENTS_ACT_1970_SEC_3_E"],
        statutory_hooks=["Section 3(e) mere admixture aggregation of properties synergistic interaction"],
        hierarchy_priority=9
    ),

    "THERAPEUTIC_EFFICACY_DERIVATIVE": ConceptDefinition(
        concept_id="THERAPEUTIC_EFFICACY_DERIVATIVE",
        domain=LegalDomain.PATENTABILITY,
        name="Known Substance Derivative / Enhanced Efficacy",
        description="New form of known substance non-patentable unless it differs significantly in properties with regard to therapeutic efficacy.",
        semantic_triggers={
            "derivative", "enhancement", "bioavailability", "nanoparticle", "isolated extract",
            "pure isolate", "polymorph", "salt", "ester", "efficacy", "enhanced efficacy",
            "therapeutic efficacy", "withaferin", "berberine", "phytochemical isolate"
        },
        statutory_provisions=["PATENTS_ACT_1970_SEC_3_D"],
        statutory_hooks=["Section 3(d) new form known substance enhanced therapeutic efficacy"],
        hierarchy_priority=9
    ),

    "METHOD_OF_TREATMENT": ConceptDefinition(
        concept_id="METHOD_OF_TREATMENT",
        domain=LegalDomain.PATENTABILITY,
        name="Method of Treatment Exclusion",
        description="Medicinal, surgical, curative, or diagnostic methods of treatment of human beings are non-patentable.",
        semantic_triggers={
            "method of treatment", "medicinal use", "treatment of patient", "curing disease",
            "administering dosage", "therapeutic method", "healing method", "clinical therapy"
        },
        statutory_provisions=["PATENTS_ACT_1970_SEC_3_I"],
        statutory_hooks=["Section 3(i) medicinal curative method of treatment human beings non-patentable"],
        hierarchy_priority=9
    ),

    "BIOLOGICAL_SOURCE_DISCLOSURE": ConceptDefinition(
        concept_id="BIOLOGICAL_SOURCE_DISCLOSURE",
        domain=LegalDomain.PATENTABILITY,
        name="Mandatory Origin Disclosure",
        description="Mandatory disclosure of source and geographical origin of biological material in patent specifications.",
        semantic_triggers={
            "disclose source", "origin of biological", "geographical origin", "collected from",
            "source of herb", "himalayan origin", "collected wild", "specification disclosure"
        },
        statutory_provisions=["PATENTS_ACT_1970_SEC_10_4"],
        statutory_hooks=["Section 10(4) mandatory disclosure source geographical origin biological material"],
        hierarchy_priority=8
    ),

    # ------------------------------------------------------------------------
    # Biodiversity & ABS Concepts (The Biological Diversity Act, 2002 / 2023)
    # ------------------------------------------------------------------------
    "COMMERCIAL_UTILIZATION_FOREIGN_ABS": ConceptDefinition(
        concept_id="COMMERCIAL_UTILIZATION_FOREIGN_ABS",
        domain=LegalDomain.BIODIVERSITY_ABS,
        name="Foreign Entity NBA Prior Approval",
        description="Mandatory approval of National Biodiversity Authority for non-citizens or foreign-incorporated entities accessing biological resources.",
        semantic_triggers={
            "foreign entity", "nri", "non-citizen", "commercial utilization", "bio-survey",
            "foreign company", "overseas access", "foreign equity", "german firm", "foreign partner",
            "multinational", "export biological"
        },
        statutory_provisions=["BDA_2002_SEC_003", "BDA_2002_SEC_019"],
        statutory_hooks=["Section 3 BDA foreign entity commercial utilization", "Section 19 Form I NBA approval"],
        hierarchy_priority=10
    ),

    "DOMESTIC_ACCESS_INTIMATION": ConceptDefinition(
        concept_id="DOMESTIC_ACCESS_INTIMATION",
        domain=LegalDomain.BIODIVERSITY_ABS,
        name="Domestic Indian Entity SBB Intimation",
        description="Prior intimation to the concerned State Biodiversity Board for Indian commercial entities.",
        semantic_triggers={
            "indian entity", "domestic commercial", "prior intimation", "state biodiversity board",
            "sbb", "indian company", "domestic manufacturer", "delhi private ltd", "kerala sbb"
        },
        statutory_provisions=["BDA_2002_SEC_007"],
        statutory_hooks=["Section 7 BDA prior intimation State Biodiversity Board Indian commercial"],
        hierarchy_priority=9
    ),

    "TRADITIONAL_PRACTITIONER_EXEMPTION": ConceptDefinition(
        concept_id="TRADITIONAL_PRACTITIONER_EXEMPTION",
        domain=LegalDomain.BIODIVERSITY_ABS,
        name="Local Healer & Vaidya ABS Exemption",
        description="Exemption from Section 7 intimation for local vaidyas, hakims, and traditional community growers.",
        semantic_triggers={
            "vaidya", "vaidyas", "hakim", "local practitioner", "personal use", "grower",
            "cultivator", "ayurvedic doctor", "traditional healer", "community farmer"
        },
        statutory_provisions=["BDA_2002_SEC_007_PROVISO"],
        statutory_hooks=["Section 7 Proviso BDA local vaidyas hakims traditional practitioners exemption"],
        hierarchy_priority=10
    ),

    "INTELLECTUAL_PROPERTY_APPROVAL_NBA": ConceptDefinition(
        concept_id="INTELLECTUAL_PROPERTY_APPROVAL_NBA",
        domain=LegalDomain.BIODIVERSITY_ABS,
        name="NBA Approval for IPR Application",
        description="Prior permission of NBA required before applying for intellectual property rights based on Indian biological resources.",
        semantic_triggers={
            "patent based on biological", "nba approval for patent", "form iii", "ipr approval",
            "patent outside india", "foreign patent filing", "pct application"
        },
        statutory_provisions=["BDA_2002_SEC_006"],
        statutory_hooks=["Section 6 BDA prior approval National Biodiversity Authority intellectual property rights Form III"],
        hierarchy_priority=10
    ),

    # ------------------------------------------------------------------------
    # Drug & Food Classification Concepts (DCA 1940 & FSSAI 2022)
    # ------------------------------------------------------------------------
    "CLASSICAL_AYURVEDIC_MEDICINE": ConceptDefinition(
        concept_id="CLASSICAL_AYURVEDIC_MEDICINE",
        domain=LegalDomain.DRUG_CLASSIFICATION,
        name="Classical Ayurvedic Formulation",
        description="Manufactured strictly in accordance with authoritative books listed in the First Schedule of DCA.",
        semantic_triggers={
            "classical medicine", "classical text", "first schedule", "charaka", "sushruta",
            "ashtanga", "authoritative books", "sharangadhara", "bhavaprakasha"
        },
        statutory_provisions=["DCA_1940_SEC_3_A"],
        statutory_hooks=["Section 3(a) DCA First Schedule authoritative books classical formulation"],
        hierarchy_priority=9
    ),

    "PATENT_PROPRIETARY_AYUSH_MEDICINE": ConceptDefinition(
        concept_id="PATENT_PROPRIETARY_AYUSH_MEDICINE",
        domain=LegalDomain.DRUG_CLASSIFICATION,
        name="Patent or Proprietary AYUSH Drug",
        description="Formulation containing ingredients in First Schedule but not matching classical formula; requires Rule 158B licensing.",
        semantic_triggers={
            "patent or proprietary", "proprietary medicine", "rule 158b", "modified ratio",
            "modified formula", "ayurvedic proprietary", "safety proof", "pilot clinical"
        },
        statutory_provisions=["DCR_1945_RULE_158B"],
        statutory_hooks=["Rule 158B Drugs and Cosmetics Rules patent proprietary licensing safety data"],
        hierarchy_priority=9
    ),

    "PHYTOPHARMACEUTICAL_DRUG": ConceptDefinition(
        concept_id="PHYTOPHARMACEUTICAL_DRUG",
        domain=LegalDomain.DRUG_CLASSIFICATION,
        name="Phytopharmaceutical Drug Pathway",
        description="Purified and standardized fraction with defined minimum four marker compounds under CDSCO Rule 122E.",
        semantic_triggers={
            "phytopharmaceutical", "standardized fraction", "rule 122e", "cdsco", "form ct-18",
            "four marker compounds", "new phytopharmaceutical", "clinical trials cdsco"
        },
        statutory_provisions=["DCR_1945_RULE_122E"],
        statutory_hooks=["Rule 122E Drugs and Cosmetics Rules Phytopharmaceutical Drug CDSCO Form CT-18"],
        hierarchy_priority=10
    ),

    "AYURVEDA_AAHARA_BOUNDARY": ConceptDefinition(
        concept_id="AYURVEDA_AAHARA_BOUNDARY",
        domain=LegalDomain.DRUG_CLASSIFICATION,
        name="Ayurveda Aahara Food Boundary",
        description="Food supplements prepared according to authoritative books, strictly prohibiting synthetic vitamins, minerals, and disease cure claims.",
        semantic_triggers={
            "ayurveda aahara", "food supplement", "dietary supplement", "synthetic vitamins",
            "minerals prohibited", "fssai", "schedule a", "aahara logo", "no disease cure claim"
        },
        statutory_provisions=["FSSAI_AYURVEDA_AAHARA_2022_REG_2_1_A", "FSSAI_AYURVEDA_AAHARA_2022_REG_3"],
        statutory_hooks=["Regulation 2(1)(a) Ayurveda Aahara FSSAI", "Regulation 3 synthetic vitamins prohibited"],
        hierarchy_priority=9
    ),

    # ------------------------------------------------------------------------
    # Safety & Deceptive Marketing Prohibitions
    # ------------------------------------------------------------------------
    "MAGIC_REMEDIES_DECEPTIVE_CURE": ConceptDefinition(
        concept_id="MAGIC_REMEDIES_DECEPTIVE_CURE",
        domain=LegalDomain.SAFETY_PROHIBITION,
        name="Drugs and Magic Remedies Objectionable Ads",
        description="Prohibition of advertisements claiming treatment, cure, or mitigation of Schedule-listed incurable diseases.",
        semantic_triggers={
            "cure diabetes", "cure cancer", "guaranteed cure", "magic remedy", "advertisement cure",
            "miracle cure", "100% cure", "schedule j", "objectionable advertisements"
        },
        statutory_provisions=["DMRA_1954_SEC_003"],
        statutory_hooks=["Section 3 Drugs and Magic Remedies Objectionable Advertisements Act prohibition of cure claims"],
        hierarchy_priority=10
    ),

    # ------------------------------------------------------------------------
    # International & Treaties
    # ------------------------------------------------------------------------
    "WIPO_GRATK_TREATY_2024": ConceptDefinition(
        concept_id="WIPO_GRATK_TREATY_2024",
        domain=LegalDomain.EXPORT_INTERNATIONAL,
        name="WIPO GRATK Treaty Mandatory Disclosure",
        description="International treaty mandating disclosure of origin and indigenous knowledge in patent applications based on genetic resources.",
        semantic_triggers={
            "wipo gratk", "genetic resources treaty", "gratk 2024", "indigenous knowledge disclosure",
            "wipo treaty", "international disclosure of origin"
        },
        statutory_provisions=["WIPO_GRATK_TREATY_2024_ART_03"],
        statutory_hooks=["WIPO GRATK Treaty 2024 Article 3 mandatory disclosure origin genetic resources"],
        hierarchy_priority=8
    )
}
