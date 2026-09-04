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
            "traditional knowledge", "patent traditional knowledge", "tkdl", "3(p)", "section 3(p)",
            "aggregation of known properties", "prior art ayurveda", "patent classical",
            "patent herbal formulation", "patenting ayurveda", "tk prior art"
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

    "METHOD_OF_TREATMENT_BAR": ConceptDefinition(
        concept_id="METHOD_OF_TREATMENT_BAR",
        domain=LegalDomain.PATENTABILITY,
        name="Method of Treatment / Medicinal Process Exclusion",
        description="Any process for the medicinal, surgical, curative, prophylactic, diagnostic, therapeutic or other treatment of human beings or animals is statutory non-patentable.",
        semantic_triggers={
            "method of administering", "method of treatment", "treatment method",
            "cure", "curing", "therapeutic treatment", "prophylactic", "curative",
            "dosage regimen", "new indication", "dose", "administering", "administer",
            "new use", "previously unknown indication", "second medical use", "new medical use"
        },
        statutory_provisions=["PATENTS_ACT_1970_SEC_003_I", "PATENTS_ACT_1970_SEC_3_I"],
        statutory_hooks=["Section 3(i) medicinal curative prophylactic diagnostic therapeutic treatment human beings animals"],
        hierarchy_priority=10
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
    ),

    "PATENT_DISCLOSURE_BIOLOGICAL_SOURCE": ConceptDefinition(
        concept_id="PATENT_DISCLOSURE_BIOLOGICAL_SOURCE",
        domain=LegalDomain.PATENTABILITY,
        name="Mandatory Source / Origin Disclosure",
        description="Requirement to disclose the specific geographical origin of biological material in patent specifications, failure of which invites revocation under 64(1)(p).",
        semantic_triggers={
            "disclose where", "source of biological", "origin disclosure", "western ghats",
            "himachal pradesh", "failed to disclose", "geographic origin", "source of herb",
            "wild kutki", "collected wild", "revocation", "grounds for revocation", "section 10(4)"
        },
        statutory_provisions=["PATENTS_ACT_1970_SEC_10_4", "PATENTS_ACT_1970_SEC_64_1_P"],
        statutory_hooks=["Section 10(4) Patents Act disclosure of biological material origin", "Section 64(1)(p) revocation for non-disclosure"],
        hierarchy_priority=9
    ),

    "PLANT_VARIETIES_AND_ORGANISMS": ConceptDefinition(
        concept_id="PLANT_VARIETIES_AND_ORGANISMS",
        domain=LegalDomain.PATENTABILITY,
        name="Plant Varieties & Living Organisms Exclusion",
        description="Plants and animals in whole or any part thereof including seeds, varieties and species are not inventions under Section 3(j); protectable under PPV&FR.",
        semantic_triggers={
            "plant variety", "cultivated variety", "high-yield variety", "species", "seeds",
            "living entity", "microorganism", "wild fungus", "ppvfr", "plant variety protection"
        },
        statutory_provisions=["PATENTS_ACT_1970_SEC_3_J", "PPVFR_ACT_2001"],
        statutory_hooks=["Section 3(j) plants animals varieties species not inventions", "PPV&FR Act 2001 plant variety protection"],
        hierarchy_priority=9
    ),

    "AGRICULTURAL_HORTICULTURAL_METHOD": ConceptDefinition(
        concept_id="AGRICULTURAL_HORTICULTURAL_METHOD",
        domain=LegalDomain.PATENTABILITY,
        name="Method of Agriculture or Horticulture Exclusion",
        description="A method of agriculture or horticulture is excluded from patentability under Section 3(h).",
        semantic_triggers={
            "method of agriculture", "agricultural method", "cultivating", "hydroponic",
            "vertical farm", "farming technique", "harvesting method", "horticulture"
        },
        statutory_provisions=["PATENTS_ACT_1970_SEC_3_H"],
        statutory_hooks=["Section 3(h) method of agriculture or horticulture not an invention"],
        hierarchy_priority=9
    ),

    "PRE_GRANT_OPPOSITION_TK": ConceptDefinition(
        concept_id="PRE_GRANT_OPPOSITION_TK",
        domain=LegalDomain.PATENTABILITY,
        name="Pre-Grant Opposition on Origin / TK Grounds",
        description="Opposition grounds under Section 25(1)(j) (non-disclosure of origin) and Section 25(1)(k) (traditional knowledge in public domain).",
        semantic_triggers={
            "pre-grant opposition", "oppose the grant", "opposition under section 25",
            "prior publication opposition", "failed to mention the geographical origin"
        },
        statutory_provisions=["PATENTS_ACT_1970_SEC_25_1_J", "PATENTS_ACT_1970_SEC_25_1_K"],
        statutory_hooks=["Section 25(1)(j) opposition non-disclosure of origin", "Section 25(1)(k) opposition traditional knowledge in public domain"],
        hierarchy_priority=8
    ),

    "FOREIGN_FILING_LICENSE_REQ": ConceptDefinition(
        concept_id="FOREIGN_FILING_LICENSE_REQ",
        domain=LegalDomain.PATENTABILITY,
        name="Foreign Filing License (Section 39)",
        description="Mandatory prior written permission from CGPDTM before an Indian resident files a patent application outside India.",
        semantic_triggers={
            "foreign filing license", "foreign patent filing", "filing abroad", "file in us first",
            "file patent in germany", "pct application without", "section 39", "ffl"
        },
        statutory_provisions=["PATENTS_ACT_1970_SEC_39", "PATENTS_ACT_1970_SEC_40"],
        statutory_hooks=["Section 39 Patents Act foreign filing license written permit", "Section 40 liability for contravention"],
        hierarchy_priority=9
    ),

    "PATENT_RULES_2024_TIMELINES": ConceptDefinition(
        concept_id="PATENT_RULES_2024_TIMELINES",
        domain=LegalDomain.PATENTABILITY,
        name="Patents Rules 2024 Procedural Timelines",
        description="Reduced 31-month timeline for Request for Examination (Rule 24B) and triennial Form 27 commercial working statement (Rule 131).",
        semantic_triggers={
            "patents rules 2024", "request for examination", "form 18", "rule 24b", "31 months",
            "form 27", "working statement", "statement of commercial working", "three financial years"
        },
        statutory_provisions=["PATENTS_RULES_2024_RULE_24B", "PATENTS_RULES_2024_RULE_131"],
        statutory_hooks=["Rule 24B Patents Amendment Rules 2024 Request for Examination 31 months", "Rule 131 Form 27 once every three financial years"],
        hierarchy_priority=8
    ),

    "RESEARCH_RESULTS_FOREIGN_TRANSFER": ConceptDefinition(
        concept_id="RESEARCH_RESULTS_FOREIGN_TRANSFER",
        domain=LegalDomain.BIODIVERSITY_ABS,
        name="Transfer of Research Results (Section 4)",
        description="Prohibition against transferring biological research results to foreign entities without prior NBA approval under Section 4.",
        semantic_triggers={
            "transfer biological research", "transfer results", "foreign university",
            "collaborative research", "foreign collaborator", "send data abroad"
        },
        statutory_provisions=["BDA_2002_SEC_004", "BDA_2002_SEC_019"],
        statutory_hooks=["Section 4 Biological Diversity Act transfer of research results approval", "Section 19 application to NBA"],
        hierarchy_priority=9
    ),

    "NORMALLY_TRADED_COMMODITIES_EXEMPTION": ConceptDefinition(
        concept_id="NORMALLY_TRADED_COMMODITIES_EXEMPTION",
        domain=LegalDomain.BIODIVERSITY_ABS,
        name="Normally Traded Commodities (NTAC List)",
        description="Notification under Section 40 exempting commonly traded agricultural commodities, spices, and pulses from ABS provisions.",
        semantic_triggers={
            "normally traded", "ntac", "spices", "ginger", "black pepper", "turmeric export",
            "agricultural commodities exempt", "section 40"
        },
        statutory_provisions=["BDA_2002_SEC_040"],
        statutory_hooks=["Section 40 Biological Diversity Act normally traded commodities NTAC exemption"],
        hierarchy_priority=9
    ),

    "ABS_TURNOVER_BENEFIT_SHARING": ConceptDefinition(
        concept_id="ABS_TURNOVER_BENEFIT_SHARING",
        domain=LegalDomain.BIODIVERSITY_ABS,
        name="ABS Benefit Sharing Calculation Formula",
        description="Regulations 11 & 12 establishing 0.1% to 0.5% of annual gross ex-factory sales as fair and equitable benefit sharing.",
        semantic_triggers={
            "percentage of ex-factory", "benefit sharing percentage", "annual turnover abs",
            "benefit sharing formula", "nba abs regulations 2014", "how much to pay abs"
        },
        statutory_provisions=["NBA_ABS_REGS_2014_REG_11", "NBA_ABS_REGS_2014_REG_12"],
        statutory_hooks=["Regulation 11 NBA ABS Regulations 2014 benefit sharing percentage turnover", "Regulation 12 ex-factory sale"],
        hierarchy_priority=8
    ),

    "LOCAL_BMC_CONSULTATION": ConceptDefinition(
        concept_id="LOCAL_BMC_CONSULTATION",
        domain=LegalDomain.BIODIVERSITY_ABS,
        name="Biodiversity Management Committees (BMC)",
        description="Section 41 mandate for local BMC establishment, consultation, and benefit distribution by NBA/SBB.",
        semantic_triggers={
            "biodiversity management committee", "bmc", "panchayat level", "local body",
            "panchayat demand", "peoples biodiversity register", "pbr"
        },
        statutory_provisions=["BDA_2002_SEC_041", "BDA_2002_SEC_021"],
        statutory_hooks=["Section 41 Biological Diversity Act Biodiversity Management Committees BMC", "Section 21 equitable benefit sharing"],
        hierarchy_priority=8
    ),

    "CIVIL_PENALTIES_DECRIMINALIZED": ConceptDefinition(
        concept_id="CIVIL_PENALTIES_DECRIMINALIZED",
        domain=LegalDomain.BIODIVERSITY_ABS,
        name="Decriminalized Civil Penalties (2023 Amendment)",
        description="Replacement of imprisonment with civil monetary penalties up to 50 lakh adjudicated by Joint Secretary level Adjudicating Officers.",
        semantic_triggers={
            "penalty", "penalties", "monetary penalty", "50 lakh", "decriminalized",
            "decriminalization", "adjudicating officer", "arrest without trial"
        },
        statutory_provisions=["BDA_2002_SEC_055", "BDA_2002_SEC_055A"],
        statutory_hooks=["Section 55 Biological Diversity Act penalties 2023 amendment", "Section 55A Adjudicating Officer civil penalties"],
        hierarchy_priority=9
    ),

    "SCHEDULE_E1_POISONS_AND_GMP": ConceptDefinition(
        concept_id="SCHEDULE_E1_POISONS_AND_GMP",
        domain=LegalDomain.DRUG_CLASSIFICATION,
        name="Schedule E(1) Poisons & Schedule T GMP",
        description="Schedule E(1) list of poisonous Ayurvedic plants requiring cautionary labels and Schedule T Good Manufacturing Practices mandatory for manufacturing ASU drugs.",
        semantic_triggers={
            "schedule e(1)", "schedule e1", "poisonous substances", "hazardous substances",
            "cautionary label", "schedule t", "good manufacturing practices", "gmp premises"
        },
        statutory_provisions=["DCR_1945_SCHEDULE_E1", "DCR_1945_SCHEDULE_T"],
        statutory_hooks=["Schedule E(1) Drugs and Cosmetics Rules poisonous substances", "Schedule T Good Manufacturing Practices ASU"],
        hierarchy_priority=9
    ),

    "INTERNATIONAL_EXPORT_REGULATORY_COMPLIANCE": ConceptDefinition(
        concept_id="INTERNATIONAL_EXPORT_REGULATORY_COMPLIANCE",
        domain=LegalDomain.EXPORT_INTERNATIONAL,
        name="Export Compliance (DSHEA, THMPD, CITES)",
        description="US FDA DSHEA 21 CFR 111 75-day NDI notification, EU THMPD 30-year traditional evidence (15 in EU), and CITES Appendix II permits.",
        semantic_triggers={
            "dshea", "ndi", "new dietary ingredient", "75 days", "21 cfr 111", "thmpd",
            "directive 2004/24/ec", "30 years", "15 years", "heavy metal limits", "lead and cadmium",
            "cites appendix ii", "cites permit", "novel food", "regulation eu 2015/2283"
        },
        statutory_provisions=["US_FDA_DSHEA_21_CFR_111", "EU_DIRECTIVE_2004_24_EC", "CITES_APPENDIX_II"],
        statutory_hooks=["US FDA DSHEA 21 CFR 111 New Dietary Ingredient 75-day notification", "Directive 2004/24/EC Traditional Herbal Medicinal Products 30-year evidence", "CITES Appendix II export permit"],
        hierarchy_priority=9
    ),

    "TRADEMARK_DISTINCTIVENESS_AND_GI": ConceptDefinition(
        concept_id="TRADEMARK_DISTINCTIVENESS_AND_GI",
        domain=LegalDomain.TRADEMARKS_IP,
        name="Trademark Distinctiveness, Infringement & Geographical Indications",
        description="Prohibition of descriptive marks under Section 9, relative grounds under Section 11, exclusive rights under Section 28, infringement and trade dress protection under Section 29, Rule 28 logo representation, and GI registration under GI Act 1999.",
        semantic_triggers={
            "trademark", "trade mark", "exclusive name", "descriptive name", "word mark",
            "device mark", "geographical indication", "gi tag", "gi act 1999", "class 5",
            "kesh king", "bottle design", "copy the distinctive", "distinctive bottle", "trade dress",
            "passing off", "malabar pepper", "giloy-ceutical", "section 11", "section 29", "rule 28", "distinctive logo"
        },
        statutory_provisions=["TMA_1999_SEC_009", "TMA_1999_SEC_011", "TMA_1999_SEC_013", "TMA_1999_SEC_028", "TMA_1999_SEC_029", "TMR_2017_RULE_028", "GI_ACT_1999_SEC_002"],
        statutory_hooks=[
            "Section 9 Trade Marks Act absolute grounds for refusal",
            "Section 11 Trade Marks Act relative grounds for refusal deceptive similarity",
            "Section 28 Trade Marks Act exclusive rights conferred by registration",
            "Section 29 Trade Marks Act infringement identical trade dress bottle design passing off",
            "Rule 28 Trade Marks Rules representation of trade mark logo",
            "Geographical Indications of Goods Act 1999 Section 11 registration of GI"
        ],
        hierarchy_priority=9
    ),

    "OBJECTIONABLE_ADVERTISEMENTS_PROHIBITION": ConceptDefinition(
        concept_id="OBJECTIONABLE_ADVERTISEMENTS_PROHIBITION",
        domain=LegalDomain.SAFETY_PROHIBITION,
        name="Prohibition of Misleading & Magic Remedies Advertisements",
        description="Statutory ban under Section 3 and Section 4 of the Drugs and Magic Remedies Act against advertising cures for specified diseases (diabetes, cancer, obesity).",
        semantic_triggers={
            "magic remedies", "advertisement", "objectionable advertisement", "claim 100% cure",
            "cure for cancer", "cure diabetes", "cure obesity", "newspaper claim", "section 3(d)",
            "misleading claims", "100% cure"
        },
        statutory_provisions=["DMRA_1954_SEC_003", "DMRA_1954_SEC_004"],
        statutory_hooks=["Section 3 Drugs and Magic Remedies Act prohibition of advertisements for certain diseases", "Section 3(d) cure for cancer diabetes obesity prohibited"],
        hierarchy_priority=10
    ),

    "GOOD_MANUFACTURING_PRACTICES_SCHEDULE_T": ConceptDefinition(
        concept_id="GOOD_MANUFACTURING_PRACTICES_SCHEDULE_T",
        domain=LegalDomain.DRUG_CLASSIFICATION,
        name="Good Manufacturing Practices (GMP) / Schedule T",
        description="Mandatory manufacturing standard, factory premises specifications, and quality control hygiene prescribed under Rule 157 and Schedule T for all ASU drug manufacturing.",
        semantic_triggers={
            "gmp", "good manufacturing practices", "manufacturing premises standard", "factory standard",
            "commercial factories", "commercial factory", "ayurvedic factories", "schedule t",
            "rule 157", "bhasmas", "swarna", "rajata", "premises standard"
        },
        statutory_provisions=["DRUGS_COSMETICS_RULES_1945_RULE_157", "DRUGS_COSMETICS_RULES_1945_SCHED_T"],
        statutory_hooks=["Rule 157 Drugs and Cosmetics Rules factory premises requirements", "Schedule T Good Manufacturing Practices ASU medicines"],
        hierarchy_priority=9
    )
}
