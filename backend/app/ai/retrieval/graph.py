import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import KnowledgeRelation, Source

logger = logging.getLogger("AyuRaksha.GraphRetriever")

class GraphRetriever:
    """
    Traverses statutory knowledge graph relations (AMENDS, IMPLEMENTS, GOVERNS, REFERENCES).
    Expands direct retrieval candidates with interconnected regulatory provisions.
    """

    # Static authoritative knowledge links for offline resilience
    STATIC_STATUTORY_GRAPH = {
        "IND_PATENTS_ACT_1970": [
            {
                "relation_type": "REFERENCES",
                "target_source": "TKDL_AYURVEDA_BOOKS",
                "target_label": "First Schedule Classical Books",
                "evidence": "Section 3(p) excludes traditional knowledge documented in classical texts."
            },
            {
                "relation_type": "GOVERNED_BY",
                "target_source": "IND_BIOLOGICAL_DIVERSITY_ACT_2002",
                "target_label": "BDA Section 6 (Form III Patent Mandate)",
                "evidence": "Filing patents on Indian biological resources requires NBA approval under Section 6."
            },
            {
                "relation_type": "AMENDED_BY_RULES",
                "target_source": "IND_PATENTS_AMENDMENT_RULES_2024",
                "target_label": "Patents (Amendment) Rules, 2024",
                "evidence": "Modernizes Form 3 foreign filing reporting and accelerates RFE timeline to 31 months under Rule 24B."
            },
            {
                "relation_type": "ALIGNED_WITH",
                "target_source": "INT_WIPO_GRATK_TREATY_2024",
                "target_label": "WIPO GRATK Treaty (2024)",
                "evidence": "Article 3 internationalizes mandatory disclosure of genetic resources and traditional knowledge in patent filings."
            }
        ],
        "INT_WIPO_GRATK_TREATY_2024": [
            {
                "relation_type": "IMPLEMENTS_PRINCIPLE_OF",
                "target_source": "IND_PATENTS_ACT_1970",
                "target_label": "Patents Act, 1970 (Section 10(4)(ii)(D))",
                "evidence": "Mandates worldwide disclosure of country of origin for biological resources and traditional knowledge."
            },
            {
                "relation_type": "RECOGNIZES_DATABASE",
                "target_source": "TKDL_AYURVEDA_BOOKS",
                "target_label": "Traditional Knowledge Digital Library (TKDL)",
                "evidence": "Article 6 provides formal international legal sanction for TKDL databases in global patent examination."
            }
        ],
        "IND_PATENTS_AMENDMENT_RULES_2024": [
            {
                "relation_type": "AMENDS_PROCEDURE_OF",
                "target_source": "IND_PATENTS_ACT_1970",
                "target_label": "Patents Act, 1970 (Sections 8, 11B, 146)",
                "evidence": "Amends Form 3 (Rule 12), Form 18 RFE to 31 months (Rule 24B), and Form 27 to 3-year cycle (Rule 131)."
            }
        ],
        "IND_BIOLOGICAL_DIVERSITY_ACT_2002": [
            {
                "relation_type": "AMENDED_BY",
                "target_source": "IND_BDA_AMENDMENT_2023",
                "target_label": "Biological Diversity (Amendment) Act, 2023",
                "evidence": "Amended Section 7 exempting registered Ayush practitioners from SBB prior intimation."
            }
        ],
        "IND_DRUGS_COSMETICS_ACT_1940": [
            {
                "relation_type": "IMPLEMENTS",
                "target_source": "IND_DRUGS_COSMETICS_RULES_1945",
                "target_label": "Drugs and Cosmetics Rules, 1945 (Rule 158B)",
                "evidence": "Prescribes licensing, proof of effectiveness, and safety studies for ASU medicines."
            },
            {
                "relation_type": "REFERENCES",
                "target_source": "TKDL_AYURVEDA_BOOKS",
                "target_label": "First Schedule (56 Authoritative Classical Texts)",
                "evidence": "Section 3(a) defines classical ASU drugs as those manufactured strictly according to First Schedule texts."
            }
        ]
    }

    @classmethod
    async def expand_candidates(cls, candidates: List[Dict[str, Any]], max_hops: int = 1) -> List[Dict[str, Any]]:
        """
        Expands top candidate sources with relational links from knowledge_relations.
        """
        if not candidates:
            return []

        expanded = list(candidates)
        seen_keys = {c.get("source_id") for c in candidates}
        top_candidates = candidates[:5]
        source_codes = [c.get("source_id") for c in top_candidates if c.get("source_id")]

        # Single batch query to DB for all top sources
        db_relations_by_src: Dict[str, List[Dict[str, Any]]] = {}
        if source_codes:
            try:
                async with AsyncSessionLocal() as session:
                    stmt = (
                        select(KnowledgeRelation, Source.source_code)
                        .join(Source, KnowledgeRelation.subject_source_id == Source.id)
                        .where(Source.source_code.in_(source_codes))
                    )
                    res = await session.execute(stmt)
                    for kr, sc in res.all():
                        db_relations_by_src.setdefault(sc, []).append({
                            "relation_type": kr.relation_type,
                            "target_label": kr.target_label,
                            "evidence": kr.evidence or "",
                            "confidence": kr.confidence
                        })
            except Exception as e:
                logger.debug(f"DB knowledge_relations batch query bypassed: {e}")

        for candidate in top_candidates:
            src_id = candidate.get("source_id")
            if not src_id:
                continue

            db_relations = db_relations_by_src.get(src_id, [])
            static_relations = cls.STATIC_STATUTORY_GRAPH.get(src_id, [])
            all_relations = db_relations + static_relations

            for rel in all_relations:
                target_src = rel.get("target_source") or rel.get("target_label")
                if target_src and target_src not in seen_keys:
                    seen_keys.add(target_src)
                    expanded.append({
                        "source_id": f"GRAPH_RELATION_{target_src}",
                        "source_title": f"Statutory Relation: {rel.get('relation_type')} -> {target_src}",
                        "section_number": f"Rel: {rel.get('relation_type')}",
                        "heading": f"Statutory Link: {rel.get('target_label')}",
                        "raw_statute": rel.get("evidence", ""),
                        "text": f"[Statutory Relation: {rel.get('relation_type')}]\nSource: {src_id}\nConnected Law: {target_src}\nStatutory Evidence: {rel.get('evidence')}",
                        "authority_level": candidate.get("authority_level", 4) - 1,
                        "support_score": candidate.get("support_score", 0.5) * 0.85,
                        "is_graph_expanded": True,
                        "relation_type": rel.get("relation_type")
                    })

        return expanded

    @staticmethod
    async def _fetch_db_relations(source_code: str) -> List[Dict[str, Any]]:
        relations = []
        try:
            async with AsyncSessionLocal() as session:
                stmt = (
                    select(KnowledgeRelation, Source.source_code)
                    .join(Source, KnowledgeRelation.subject_source_id == Source.id)
                    .where(Source.source_code == source_code)
                )
                res = await session.execute(stmt)
                rows = res.all()
                for kr, sc in rows:
                    relations.append({
                        "relation_type": kr.relation_type,
                        "target_label": kr.target_label,
                        "evidence": kr.evidence or "",
                        "confidence": kr.confidence
                    })
        except Exception as e:
            logger.debug(f"DB knowledge_relations query bypassed: {e}")
        return relations

    @classmethod
    def get_full_knowledge_graph(cls) -> Dict[str, Any]:
        """
        Returns the full multi-hop statutory & traditional knowledge graph
        connecting botanicals, classical texts, patent provisions, official forms,
        and international treaties.
        """
        nodes = [
            # 🌿 Botanicals
            {
                "id": "BOTANICAL_ASHWAGANDHA",
                "label": "Withania somnifera (Ashwagandha)",
                "category": "botanical",
                "authority": "TKDL Botanical Taxonomy / Ayurvedic Pharmacopoeia",
                "section_reference": "API Part I, Vol. I",
                "badge": "Medicinal Plant",
                "official_url": "https://www.tkdl.res.in/",
                "description": "Rasayana and Balya root documented across classical treatises. Regulated biological resource under BDA 2002 and subject to Section 3(p) prior art scrutiny."
            },
            {
                "id": "BOTANICAL_HARIDRA",
                "label": "Curcuma longa (Haridra / Turmeric)",
                "category": "botanical",
                "authority": "TKDL Botanical Taxonomy / USPTO Revocation Precedent",
                "section_reference": "API Part I, Vol. I",
                "badge": "Medicinal Plant",
                "official_url": "https://www.tkdl.res.in/",
                "description": "Historic wound-healing botanical. Landmark CSIR/TKDL case study revoking US Patent 5,401,504 based on classical Ayurvedic references."
            },
            {
                "id": "BOTANICAL_BRAHMI",
                "label": "Bacopa monnieri (Brahmi)",
                "category": "botanical",
                "authority": "TKDL Botanical Taxonomy",
                "section_reference": "API Part I, Vol. II",
                "badge": "Medicinal Plant",
                "official_url": "https://www.tkdl.res.in/",
                "description": "Medhya Rasayana herb for memory and cognitive enhancement. Bacoside extracts frequently encounter Section 3(d) and 3(p) examination scrutiny."
            },
            {
                "id": "BOTANICAL_GUDUCHI",
                "label": "Tinospora cordifolia (Guduchi / Giloy)",
                "category": "botanical",
                "authority": "TKDL Botanical Taxonomy",
                "section_reference": "API Part I, Vol. I",
                "badge": "Medicinal Plant",
                "official_url": "https://www.tkdl.res.in/",
                "description": "Jwaraghna and Vayasthapana herb. Classical formulations include Amritarishta and Guduchi Satva. Governed by BDA for commercial bio-prospecting."
            },
            {
                "id": "BOTANICAL_KUTKI",
                "label": "Picrorhiza kurroa (Kutki)",
                "category": "botanical",
                "authority": "TKDL Botanical Taxonomy / CITES Appendix II",
                "section_reference": "API Part I, Vol. II",
                "badge": "Threatened Herb",
                "official_url": "https://www.tkdl.res.in/",
                "description": "High-altitude Himalayan hepatoprotective herb. Strict SBB prior intimation and export clearance required under Biological Diversity Act."
            },

            # 📜 Classical Authoritative Texts (First Schedule DCA 1940)
            {
                "id": "TEXT_CHARAKA_SAMHITA",
                "label": "Charaka Samhita",
                "category": "classical_text",
                "authority": "Agnivesha / Charaka (First Schedule, DCA 1940)",
                "section_reference": "First Schedule Entry 1",
                "badge": "Authoritative Book",
                "official_url": "https://www.tkdl.res.in/",
                "description": "Foundational Brihat-trayi Ayurvedic text establishing fundamental rasayana, dravyaguna, and therapeutics recognized under DCA Section 3(a)."
            },
            {
                "id": "TEXT_SUSHRUTA_SAMHITA",
                "label": "Sushruta Samhita",
                "category": "classical_text",
                "authority": "Sage Sushruta (First Schedule, DCA 1940)",
                "section_reference": "First Schedule Entry 2",
                "badge": "Authoritative Book",
                "official_url": "https://www.tkdl.res.in/",
                "description": "Foundational surgical and pharmacological treatise cited in landmark TKDL patent rejections worldwide."
            },
            {
                "id": "TEXT_BHAISHAJYA_RATNAVALI",
                "label": "Bhaishajya Ratnavali",
                "category": "classical_text",
                "authority": "Govinda Das Sen (First Schedule, DCA 1940)",
                "section_reference": "First Schedule Entry 8",
                "badge": "Authoritative Book",
                "official_url": "https://www.tkdl.res.in/",
                "description": "Exhaustive formulary of compound classical ASU recipes (Asava, Arishta, Avaleha, Bhasma). Core citation benchmark for Rule 158B Classicals."
            },
            {
                "id": "TEXT_ASHTANGA_HRIDAYA",
                "label": "Ashtanga Hridaya",
                "category": "classical_text",
                "authority": "Acharya Vagbhata (First Schedule, DCA 1940)",
                "section_reference": "First Schedule Entry 4",
                "badge": "Authoritative Book",
                "official_url": "https://www.tkdl.res.in/",
                "description": "Harmonized synthesis of internal medicine and surgery, heavily indexed in TKDL for prior art matching against foreign patent claims."
            },

            # ⚖️ Statutory Primary Acts & Provisions
            {
                "id": "STATUTE_PATENTS_ACT",
                "label": "The Patents Act, 1970",
                "category": "statute",
                "authority": "Office of the CGPDTM, India",
                "section_reference": "Act No. 39 of 1970",
                "badge": "Primary Statute",
                "official_url": "https://ipindia.gov.in/",
                "description": "Primary legislative statute governing patent grant criteria, patentable subject matter exclusions, opposition, and revocation in India."
            },
            {
                "id": "SEC_PA_3P",
                "label": "Section 3(p) TK Patent Exclusion",
                "category": "section",
                "authority": "The Patents Act, 1970",
                "section_reference": "Patents Act § 3(p)",
                "badge": "TK Bar",
                "official_url": "https://ipindia.gov.in/acts/patent-act-1970/section-3",
                "description": "Expressly declares that an invention which in effect is traditional knowledge or an aggregation/duplication of known properties is NOT patentable."
            },
            {
                "id": "SEC_PA_3E",
                "label": "Section 3(e) Mere Admixture Bar",
                "category": "section",
                "authority": "The Patents Act, 1970",
                "section_reference": "Patents Act § 3(e)",
                "badge": "Synergy Required",
                "official_url": "https://ipindia.gov.in/acts/patent-act-1970/section-3",
                "description": "Bars substances obtained by mere admixture resulting only in aggregation of component properties. Requires demonstrated synergistic bio-activity."
            },
            {
                "id": "SEC_PA_10_4",
                "label": "Section 10(4)(ii)(D) Origin Disclosure",
                "category": "section",
                "authority": "The Patents Act, 1970",
                "section_reference": "Patents Act § 10(4)(ii)(D)",
                "badge": "Mandatory Disclosure",
                "official_url": "https://ipindia.gov.in/acts/patent-act-1970/section-10",
                "description": "Mandates disclosure of source and geographical origin of any biological material used in the specification from India."
            },
            {
                "id": "SEC_PA_25_1_K",
                "label": "Section 25(1)(k) TK Pre-Grant Opposition",
                "category": "section",
                "authority": "The Patents Act, 1970",
                "section_reference": "Patents Act § 25(1)(k)",
                "badge": "Pre-Grant Challenge",
                "official_url": "https://ipindia.gov.in/acts/patent-act-1970/section-25",
                "description": "Statutory ground for third parties to oppose pending patent applications on grounds of anticipation by oral or written traditional knowledge."
            },
            {
                "id": "SEC_PA_39",
                "label": "Section 39 Foreign Filing License",
                "category": "section",
                "authority": "The Patents Act, 1970",
                "section_reference": "Patents Act § 39",
                "badge": "Export Clearance",
                "official_url": "https://ipindia.gov.in/acts/patent-act-1970/section-39",
                "description": "Requires Indian residents to obtain prior written permit (Form 25) from the Controller before filing a patent abroad if not filed first in India."
            },

            # 📝 Official Filing Forms (CGPDTM & NBA)
            {
                "id": "FORM_PA_1",
                "label": "Patent Form 1",
                "category": "form",
                "authority": "CGPDTM Patents Rules 2003",
                "section_reference": "Rules 20(1), Sections 7, 54, 135",
                "badge": "Grant Application",
                "official_url": "https://ipindia.gov.in/acts/patent-rules-2003/form-1",
                "description": "Standard application for grant of patent filed by innovator or startup."
            },
            {
                "id": "FORM_PA_7A",
                "label": "Patent Form 7A",
                "category": "form",
                "authority": "CGPDTM Patents Rules 2003 (Rule 55)",
                "section_reference": "Patents Act § 25(1); Rule 55",
                "badge": "Opposition Filing",
                "official_url": "https://ipindia.gov.in/acts/patent-rules-2003/form-7a",
                "description": "Official representation form for filing pre-grant opposition against biopiracy or TK-misappropriating patent claims."
            },
            {
                "id": "FORM_PA_18A",
                "label": "Patent Form 18A",
                "category": "form",
                "authority": "CGPDTM Patents Rules (Rule 24C / 2024)",
                "section_reference": "Patents Rules Rule 24C",
                "badge": "Fast-Track Examination",
                "official_url": "https://ipindia.gov.in/acts/patent-rules-2003/form-18a",
                "description": "Expedited examination request available for recognized DPIIT AYUSH startups, female applicants, and small entities."
            },
            {
                "id": "FORM_PA_25",
                "label": "Patent Form 25",
                "category": "form",
                "authority": "CGPDTM Patents Rules 2003",
                "section_reference": "Patents Act § 39; Rule 71",
                "badge": "Foreign License",
                "official_url": "https://ipindia.gov.in/acts/patent-rules-2003/form-25",
                "description": "Formal request for permission to file patent application outside India for inventions originating in India."
            },
            {
                "id": "FORM_PA_27",
                "label": "Patent Form 27",
                "category": "form",
                "authority": "CGPDTM Patents (Amendment) Rules, 2024",
                "section_reference": "Patents Act § 146; Rule 131",
                "badge": "Working Statement",
                "official_url": "https://ipindia.gov.in/writereaddata/Portal/ev/rules/pdf/Patents_Rules_2003.pdf",
                "description": "Statement regarding the working of a patented invention on a commercial scale in India (amended in 2024 to a 3-year filing frequency)."
            },

            # 🌿 Biodiversity Authority (BDA & NBA)
            {
                "id": "STATUTE_BDA_2002",
                "label": "Biological Diversity Act, 2002 / 2023",
                "category": "statute",
                "authority": "National Biodiversity Authority (NBA)",
                "section_reference": "Act No. 18 of 2003 (Amended 2023)",
                "badge": "ABS Regime",
                "official_url": "http://nbaindia.org/",
                "description": "Regulates access to Indian biological resources and mandates fair and equitable benefit sharing (ABS)."
            },
            {
                "id": "SEC_BDA_6",
                "label": "BDA Section 6 (Mandatory NBA Approval)",
                "category": "section",
                "authority": "National Biodiversity Authority",
                "section_reference": "Biological Diversity Act § 6",
                "badge": "IPR Approval",
                "official_url": "http://nbaindia.org/",
                "description": "Bars any person from applying for any IPR in or outside India for any invention based on biological resource obtained from India without prior NBA approval."
            },
            {
                "id": "FORM_NBA_III",
                "label": "NBA Form III",
                "category": "form",
                "authority": "National Biodiversity Authority",
                "section_reference": "Biological Diversity Rules, 2004 (Rule 18)",
                "badge": "Patent ABS Clearance",
                "official_url": "http://nbaindia.org/",
                "description": "Mandatory statutory form for obtaining prior approval from NBA before the grant of a patent based on Indian biological resources."
            },

            # 💊 Drug Regulatory Framework (DCA & FSSAI)
            {
                "id": "STATUTE_DCA_1940",
                "label": "The Drugs & Cosmetics Act, 1940",
                "category": "statute",
                "authority": "Ministry of Ayush / CDSCO",
                "section_reference": "Act No. 23 of 1940",
                "badge": "Drug Licensing",
                "official_url": "https://cdsco.gov.in/",
                "description": "Governs manufacturing standards, adulteration, misbranding, and Form 25D licensing for Ayurvedic, Siddha, and Unani drugs."
            },
            {
                "id": "RULE_DCA_158B",
                "label": "Rule 158B ASU Formulation Tiers",
                "category": "section",
                "authority": "Drugs & Cosmetics Rules, 1945",
                "section_reference": "D&C Rules Rule 158B",
                "badge": "Form 25D Dossier",
                "official_url": "https://ayush.gov.in/",
                "description": "Defines proof of safety, published literature, and clinical trial requirements across Tier I (Classical), Tier II (Modified Form), and Tier III (New ASU)."
            },
            {
                "id": "REG_FSSAI_AAHARA",
                "label": "FSSAI Ayurveda Aahara Regs, 2022",
                "category": "statute",
                "authority": "Food Safety and Standards Authority of India",
                "section_reference": "FSS Regulations, 2022",
                "badge": "Food Supplement",
                "official_url": "https://fssai.gov.in/",
                "description": "Governs foods prepared in accordance with classical recipes. Strictly prohibits claiming prevention or cure of human diseases under Regulation 5."
            },

            # 🌍 International Treaties
            {
                "id": "TREATY_WIPO_GRATK",
                "label": "WIPO GRATK Treaty, 2024",
                "category": "treaty",
                "authority": "World Intellectual Property Organization (Geneva)",
                "section_reference": "Treaty on IP, GR and TK (2024)",
                "badge": "Global Norm",
                "official_url": "https://www.wipo.int/",
                "description": "Landmark multilateral treaty adopted in May 2024 establishing mandatory global patent disclosure of country of origin for genetic resources."
            },
            {
                "id": "ART_WIPO_GRATK_3",
                "label": "WIPO GRATK Article 3 (Mandatory Disclosure)",
                "category": "treaty",
                "authority": "World Intellectual Property Organization",
                "section_reference": "GRATK Treaty Article 3",
                "badge": "Global Disclosure",
                "official_url": "https://www.wipo.int/",
                "description": "Obligates all contracting parties to mandate patent applicants disclose country of origin of genetic resources and associated traditional knowledge."
            }
        ]

        edges = [
            # Ashwagandha links
            {
                "source": "BOTANICAL_ASHWAGANDHA",
                "target": "TEXT_CHARAKA_SAMHITA",
                "relation": "CODIFIED_IN",
                "rationale": "Described in Charaka Samhita Chikitsa Sthana as Balya and Rasayana formulation ingredient."
            },
            {
                "source": "BOTANICAL_ASHWAGANDHA",
                "target": "TEXT_BHAISHAJYA_RATNAVALI",
                "relation": "CODIFIED_IN",
                "rationale": "Core botanical in Ashwagandhadya Ghrita and Ashwagandharishta recipes."
            },
            {
                "source": "BOTANICAL_ASHWAGANDHA",
                "target": "SEC_BDA_6",
                "relation": "GOVERNED_BY",
                "rationale": "Regulated biological resource originating from India; patent claims require NBA approval."
            },

            # Haridra links
            {
                "source": "BOTANICAL_HARIDRA",
                "target": "TEXT_CHARAKA_SAMHITA",
                "relation": "CODIFIED_IN",
                "rationale": "Classified under Lekhaniya Mahakashaya and Kushtaghna vargas."
            },
            {
                "source": "BOTANICAL_HARIDRA",
                "target": "SEC_PA_3P",
                "relation": "TRIGGERED_PRECEDENT",
                "rationale": "CSIR cited classical texts to revoke US turmeric patent 5,401,504, inspiring Section 3(p)."
            },

            # Brahmi links
            {
                "source": "BOTANICAL_BRAHMI",
                "target": "TEXT_ASHTANGA_HRIDAYA",
                "relation": "CODIFIED_IN",
                "rationale": "Described in Uttara Tantra for memory enhancement and rasayana therapeutics."
            },
            {
                "source": "BOTANICAL_BRAHMI",
                "target": "SEC_PA_3E",
                "relation": "SUBJECT_TO_BAR",
                "rationale": "Polyherbal memory syrups combining Brahmi with Shankhpushpi must prove synergistic efficacy."
            },

            # Classical Texts -> DCA & Patents Act
            {
                "source": "TEXT_CHARAKA_SAMHITA",
                "target": "STATUTE_DCA_1940",
                "relation": "RECOGNIZED_UNDER",
                "rationale": "Listed in First Schedule of DCA 1940 as authoritative classical book under Section 3(a)."
            },
            {
                "source": "TEXT_BHAISHAJYA_RATNAVALI",
                "target": "STATUTE_DCA_1940",
                "relation": "RECOGNIZED_UNDER",
                "rationale": "Listed in First Schedule of DCA 1940 for Shastriya ASU drug formulations."
            },
            {
                "source": "STATUTE_DCA_1940",
                "target": "SEC_PA_3P",
                "relation": "CREATES_PATENT_BAR",
                "rationale": "Formulations adhering strictly to First Schedule texts are barred from patenting under Section 3(p)."
            },

            # Patents Act Section 3(p) -> Pre-Grant Opposition Form 7A
            {
                "source": "SEC_PA_3P",
                "target": "SEC_PA_25_1_K",
                "relation": "ENFORCED_VIA",
                "rationale": "Section 25(1)(k) enables third-party pre-grant opposition based on Section 3(p) traditional knowledge anticipation."
            },
            {
                "source": "SEC_PA_25_1_K",
                "target": "FORM_PA_7A",
                "relation": "IMPLEMENTED_BY_FORM",
                "rationale": "Pre-grant opposition under Section 25(1) is formally filed using Form 7A under Rule 55."
            },

            # Patents Act -> Section 10(4) -> NBA Section 6 -> NBA Form III
            {
                "source": "STATUTE_PATENTS_ACT",
                "target": "SEC_PA_10_4",
                "relation": "MANDATES",
                "rationale": "Section 10(4)(ii)(D) requires specification to disclose geographical origin of biological resources."
            },
            {
                "source": "SEC_PA_10_4",
                "target": "SEC_BDA_6",
                "relation": "INTERLOCKS_WITH",
                "rationale": "Patent disclosure triggers mandatory Section 6 compliance with National Biodiversity Authority."
            },
            {
                "source": "SEC_BDA_6",
                "target": "FORM_NBA_III",
                "relation": "IMPLEMENTED_BY_FORM",
                "rationale": "Prior approval from NBA for IPR applications is applied for using NBA Form III."
            },

            # Patents Act Section 39 -> Form 25
            {
                "source": "STATUTE_PATENTS_ACT",
                "target": "SEC_PA_39",
                "relation": "ENFORCES",
                "rationale": "Section 39 prohibits Indian residents from filing patents abroad without prior permit."
            },
            {
                "source": "SEC_PA_39",
                "target": "FORM_PA_25",
                "relation": "IMPLEMENTED_BY_FORM",
                "rationale": "Permission for filing outside India is formally requested using Form 25."
            },

            # Patents Act -> Form 18A (Expedited Examination)
            {
                "source": "STATUTE_PATENTS_ACT",
                "target": "FORM_PA_18A",
                "relation": "PROCEDURAL_BENEFIT",
                "rationale": "Recognized Ayush and biotechnology startups can request expedited examination under Rule 24C via Form 18A."
            },

            # DCA 1940 -> Rule 158B Licensing
            {
                "source": "STATUTE_DCA_1940",
                "target": "RULE_DCA_158B",
                "relation": "IMPLEMENTS",
                "rationale": "Rule 158B specifies documentary evidence and safety data required for ASU manufacturing licenses."
            },

            # DCA 1940 vs FSSAI Ayurveda Aahara
            {
                "source": "STATUTE_DCA_1940",
                "target": "REG_FSSAI_AAHARA",
                "relation": "REGULATORY_BOUNDARY",
                "rationale": "DCA governs therapeutic drugs (Form 25D); FSSAI governs food supplements (Ayurveda Aahara) with no medicinal claims allowed."
            },

            # WIPO GRATK Treaty 2024 -> Section 10(4) & Section 3(p)
            {
                "source": "TREATY_WIPO_GRATK",
                "target": "ART_WIPO_GRATK_3",
                "relation": "CODIFIES",
                "rationale": "Article 3 of WIPO GRATK mandates worldwide disclosure of country of origin."
            },
            {
                "source": "ART_WIPO_GRATK_3",
                "target": "SEC_PA_10_4",
                "relation": "GLOBAL_HARMONY",
                "rationale": "India's Section 10(4)(ii)(D) served as the international template for Article 3 of WIPO GRATK 2024."
            },
            {
                "source": "ART_WIPO_GRATK_3",
                "target": "FORM_NBA_III",
                "relation": "COMPLIANCE_VERIFICATION",
                "rationale": "International patent offices verify origin through NBA ABS clearance certificates."
            }
        ]

        clusters = [
            {"id": "botanicals", "name": "Medicinal Biological Resources", "count": 5, "color": "#059669"},
            {"id": "classical_texts", "name": "First Schedule Classical Books", "count": 4, "color": "#d97706"},
            {"id": "statutory_acts", "name": "Primary Legislation & Sections", "count": 8, "color": "#4f46e5"},
            {"id": "regulatory_forms", "name": "Official Procedural Forms", "count": 6, "color": "#0284c7"},
            {"id": "international_treaties", "name": "International Multilateral Norms", "count": 2, "color": "#9333ea"}
        ]

        return {
            "nodes": nodes,
            "edges": edges,
            "clusters": clusters,
            "total_nodes": len(nodes),
            "total_edges": len(edges)
        }
