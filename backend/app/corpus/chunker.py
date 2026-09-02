import csv
import json
import hashlib
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

class LegalDocumentChunker:
    """
    Hierarchical chunker for legal statutes, rules, and regulatory frameworks.
    Preserves Act -> Part -> Section/Rule -> Provision hierarchy with exact page/location metadata.
    """

    def __init__(self, corpus_root: Optional[Path] = None):
        self.corpus_root = corpus_root or Path(__file__).resolve().parents[3] / "data" / "corpus"

    def compute_sha256(self, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @staticmethod
    def compute_file_sha256(filepath: Path) -> str:
        hasher = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def parse_manifest(self) -> List[Dict[str, Any]]:
        # Check layer 2 manifest first
        manifest_v2 = self.corpus_root / "manifest" / "sources_manifest.json"
        if manifest_v2.exists():
            with open(manifest_v2, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("sources", [])

        # Fallback to base manifest
        manifest_v1 = self.corpus_root / "corpus_manifest.json"
        if manifest_v1.exists():
            with open(manifest_v1, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("sources", [])

        return []

    def parse_source_file(self, relative_path: str) -> Dict[str, Any]:
        full_path = Path(__file__).resolve().parents[3] / relative_path
        if not full_path.exists():
            return {}
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def extract_chunks_from_source(self, source_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts atomic, searchable statutory chunks with full legal hierarchy attached.
        """
        chunks = []
        source_id = source_data.get("document_id", "UNKNOWN_SOURCE")
        title = source_data.get("title", "")
        authority = source_data.get("authority", "")
        jurisdiction = source_data.get("jurisdiction", "IN")
        doc_type = source_data.get("document_type", "ACT")
        authority_level = source_data.get("authority_level", 5)
        domains = source_data.get("domain", ["GENERAL"])
        if isinstance(domains, str):
            domains = [domains]

        source_meta = source_data.get("source", {})
        source_url = source_meta.get("url", "")
        source_sha256 = source_meta.get("sha256", "")
        raw_file_name = source_meta.get("file_name", "")

        # Compute authentic cryptographic hash from disk file if available
        raw_rel = source_data.get("extracted_text_path") or source_meta.get("extracted_text_path")
        if raw_rel:
            full_raw = Path(__file__).resolve().parents[3] / raw_rel
            if full_raw.exists():
                try:
                    source_sha256 = self.compute_file_sha256(full_raw)
                except Exception:
                    pass

        # Format 1: Upgraded Normalized Provisions (Layer 2)
        if "provisions" in source_data:
            for prov in source_data["provisions"]:
                prov_id = prov.get("provision_id", "")
                p_type = prov.get("type", "SECTION")
                p_num = prov.get("number", "")
                heading = prov.get("heading", "")
                text = prov.get("text", "")
                location = prov.get("location", {})
                significance = prov.get("statutory_significance", "")
                topics = prov.get("topics", [])

                loc_str = ""
                if location.get("chapter"):
                    loc_str += f"[{location.get('chapter')}] "
                if location.get("part"):
                    loc_str += f"[{location.get('part')}] "
                if location.get("page_start"):
                    loc_str += f"(Page {location.get('page_start')}) "

                combined_text = f"{title} — {p_type} {p_num}: {heading}\n{loc_str}\n{text}"
                if significance:
                    combined_text += f"\nStatutory Significance: {significance}"

                chunks.append({
                    "source_id": source_id,
                    "provision_id": prov_id,
                    "source_title": title,
                    "authority": authority,
                    "jurisdiction": jurisdiction,
                    "document_type": doc_type,
                    "authority_level": authority_level,
                    "domain": domains[0] if domains else "GENERAL",
                    "section_number": f"{p_type} {p_num}".strip(),
                    "heading": heading,
                    "text": combined_text,
                    "raw_statute": text,
                    "location": location,
                    "source_url": source_url,
                    "source_sha256": source_sha256,
                    "raw_file_name": raw_file_name,
                    "topics": topics,
                    "chunk_hash": self.compute_sha256(combined_text)
                })

        # Format 2: Standard sections
        elif "sections" in source_data:
            for sec in source_data["sections"]:
                sec_num = sec.get("section_number", "")
                heading = sec.get("heading", "")
                text = sec.get("text", "")
                relevance = sec.get("relevance", "")

                combined_text = f"[{title} - {sec_num}: {heading}]\n{text}"
                if relevance:
                    combined_text += f"\nStatutory Relevance: {relevance}"

                chunks.append({
                    "source_id": source_id,
                    "source_title": title,
                    "authority": authority,
                    "jurisdiction": jurisdiction,
                    "document_type": doc_type,
                    "authority_level": authority_level,
                    "domain": domains[0] if domains else "GENERAL",
                    "section_number": sec_num,
                    "heading": heading,
                    "text": combined_text,
                    "raw_statute": text,
                    "source_url": source_url,
                    "source_sha256": source_sha256,
                    "chunk_hash": self.compute_sha256(combined_text)
                })

        # Format 3: Rules
        elif "rules" in source_data:
            for rule in source_data["rules"]:
                rule_num = rule.get("rule_number", "")
                heading = rule.get("heading", "")
                text = rule.get("text", "")
                relevance = rule.get("relevance", "")

                combined_text = f"[{title} - {rule_num}: {heading}]\n{text}"
                if relevance:
                    combined_text += f"\nStatutory Relevance: {relevance}"

                chunks.append({
                    "source_id": source_id,
                    "source_title": title,
                    "authority": authority,
                    "jurisdiction": jurisdiction,
                    "document_type": doc_type,
                    "authority_level": authority_level,
                    "domain": domains[0] if domains else "GENERAL",
                    "section_number": rule_num,
                    "heading": heading,
                    "text": combined_text,
                    "raw_statute": text,
                    "source_url": source_url,
                    "source_sha256": source_sha256,
                    "chunk_hash": self.compute_sha256(combined_text)
                })

        # Format 4: Regulations (e.g. FSSAI Ayurveda Aahara, NBA ABS)
        elif "regulations" in source_data:
            for reg in source_data["regulations"]:
                reg_num = reg.get("regulation_number", "")
                heading = reg.get("heading", "")
                text = reg.get("text", "")
                relevance = reg.get("relevance", "")

                combined_text = f"[{title} - {reg_num}: {heading}]\n{text}"
                if relevance:
                    combined_text += f"\nStatutory Relevance: {relevance}"

                chunks.append({
                    "source_id": source_id,
                    "source_title": title,
                    "authority": authority,
                    "jurisdiction": jurisdiction,
                    "document_type": doc_type,
                    "authority_level": authority_level,
                    "domain": domains[0] if domains else "GENERAL",
                    "section_number": reg_num,
                    "heading": heading,
                    "text": combined_text,
                    "raw_statute": text,
                    "source_url": source_url,
                    "source_sha256": source_sha256,
                    "chunk_hash": self.compute_sha256(combined_text)
                })

        # Format 5: Articles (e.g. International Treaties)
        elif "articles" in source_data:
            for art in source_data["articles"]:
                art_num = art.get("article_number", "")
                heading = art.get("heading", "")
                text = art.get("text", "")
                relevance = art.get("relevance", "")

                combined_text = f"[{title} - {art_num}: {heading}]\n{text}"
                if relevance:
                    combined_text += f"\nStatutory Relevance: {relevance}"

                chunks.append({
                    "source_id": source_id,
                    "source_title": title,
                    "authority": authority,
                    "jurisdiction": jurisdiction,
                    "document_type": doc_type,
                    "authority_level": authority_level,
                    "domain": domains[0] if domains else "GENERAL",
                    "section_number": art_num,
                    "heading": heading,
                    "text": combined_text,
                    "raw_statute": text,
                    "source_url": source_url,
                    "source_sha256": source_sha256,
                    "chunk_hash": self.compute_sha256(combined_text)
                })

        # Format 6: Classical Texts (e.g. First Schedule Authoritative Books)
        elif "classical_texts" in source_data:
            for txt in source_data["classical_texts"]:
                txt_id = txt.get("id", "")
                name = txt.get("name", "")
                author = txt.get("author", "Classical Author")
                period = txt.get("period", "Classical")
                desc = f"First Schedule Authoritative Ayurvedic Text: {name} by {author} ({period}). Recognized under Section 3(a) of Drugs and Cosmetics Act, 1940 for classical Ayurvedic formulation manufacturing and prior art defense under Patents Act Section 3(p)."

                chunks.append({
                    "source_id": source_id,
                    "source_title": title,
                    "authority": authority,
                    "jurisdiction": jurisdiction,
                    "document_type": doc_type,
                    "authority_level": authority_level,
                    "domain": "CLASSICAL_TEXTS",
                    "section_number": f"First Schedule: {name}",
                    "heading": name,
                    "text": desc,
                    "raw_statute": desc,
                    "source_url": source_url,
                    "source_sha256": source_sha256,
                    "chunk_hash": self.compute_sha256(desc)
                })

        # Format 7: Export jurisdictions (e.g. US FDA & EU EMA)
        elif "jurisdictions" in source_data:
            for jur in source_data["jurisdictions"]:
                mkt = jur.get("market", "")
                pathway = jur.get("regulatory_pathway", "")
                for r in jur.get("rules", []):
                    clause = r.get("clause", "")
                    text = r.get("text", "")
                    relevance = r.get("relevance", "")
                    combined = f"[{mkt} ({pathway}) - {clause}]\n{text}"
                    if relevance:
                        combined += f"\nStatutory Relevance: {relevance}"
                    chunks.append({
                        "source_id": source_id,
                        "source_title": title,
                        "authority": authority,
                        "jurisdiction": "INT",
                        "document_type": doc_type,
                        "authority_level": authority_level,
                        "domain": "INTERNATIONAL_IP",
                        "section_number": f"{mkt}: {clause}",
                        "heading": clause,
                        "text": combined,
                        "raw_statute": text,
                        "source_url": source_url,
                        "source_sha256": source_sha256,
                        "chunk_hash": self.compute_sha256(combined)
                    })

        return chunks

    def extract_chunks_from_csvs(self) -> List[Dict[str, Any]]:
        """
        Extracts semantic, searchable chunks from TKDL CSV taxonomy datasets:
        - plants.csv (Botanical taxonomy, vernaculars, BDA biological resource context)
        - ayurveda_books.csv (First Schedule classical authoritative books)
        - glossary.csv (Ayurvedic clinical and statutory definitions)
        - minerals.csv (Rasashastra mineral substances)
        """
        import csv
        chunks = []
        csv_dir = self.corpus_root / "csv files"
        if not csv_dir.exists():
            return chunks

        # 1. Plants (plants.csv)
        plants_path = csv_dir / "plants.csv"
        if plants_path.exists():
            try:
                with open(plants_path, "r", encoding="utf-8", errors="replace") as f:
                    for row in csv.DictReader(f):
                        sci = row.get("scientific_name", "").strip()
                        sans = row.get("sanskrit_name", "").strip()
                        common = row.get("common_name", "").strip()
                        unani = row.get("unani_name", "").strip()
                        siddha = row.get("siddha_name", "").strip()
                        eid = row.get("entity_id", "TKDL-E")

                        if not sci and not sans:
                            continue

                        heading = f"{sci} ({sans})" if sans else sci
                        combined_text = (
                            f"[TKDL Botanical Entity: {heading}]\n"
                            f"Scientific / Botanical Binomial: {sci}\n"
                            f"Sanskrit Nomenclature: {sans}\n"
                            f"Common English Vernaculars: {common}\n"
                            f"Unani / Tibb Synonym: {unani}\n"
                            f"Siddha Synonym: {siddha}\n"
                            f"Statutory Relevance: Biological resource originating from India governed by Section 3 and "
                            f"Section 7 of the Biological Diversity Act, 2002. Commercial utilization requires SBB prior "
                            f"intimation (for Indian entities) or NBA approval (for foreign entities/exports). Subject to "
                            f"Section 3(p) prior art assessment when claimed in patent applications."
                        )
                        chunks.append({
                            "source_id": "TKDL_MEDICINAL_PLANTS",
                            "source_title": "TKDL Medicinal Plants & Botanical Taxonomy",
                            "authority": "Council of Scientific & Industrial Research (CSIR) & Ministry of Ayush",
                            "jurisdiction": "IN",
                            "document_type": "TAXONOMY",
                            "authority_level": 3,
                            "domain": "BOTANICAL_TAXONOMY",
                            "section_number": f"Plant: {sci}",
                            "heading": heading,
                            "text": combined_text,
                            "raw_statute": f"{sci} ({sans}) - Vernaculars: {common}. Regulated biological resource under BDA 2002.",
                            "source_url": "https://www.tkdl.res.in/",
                            "source_sha256": self.compute_sha256(combined_text),
                            "chunk_hash": self.compute_sha256(combined_text),
                            "topics": ["botanical_taxonomy", "biological_resource", "medicinal_plants"]
                        })
            except Exception as e:
                pass

        # 2. Classical Books (ayurveda_books.csv)
        books_path = csv_dir / "ayurveda_books.csv"
        if books_path.exists():
            try:
                with open(books_path, "r", encoding="utf-8", errors="replace") as f:
                    for row in csv.DictReader(f):
                        title = row.get("title", "").strip()
                        author = row.get("author", "").strip()
                        publisher = row.get("publisher", "").strip()
                        pub_year = row.get("publication_year", "").strip()
                        edition = row.get("edition", "").strip()
                        description = row.get("description", "").strip()
                        tkdl_url = row.get("tkdl_url", "").strip()
                        bid = row.get("source_text_id", "TKDL-BK")

                        if not title:
                            continue

                        combined_text = (
                            f"[First Schedule Classical Ayurvedic Text: {title}]\n"
                            f"Text Title: {title}\n"
                            f"Author / Sage: {author or 'Traditional Authority'}\n"
                            f"Publisher & Edition: {publisher} ({edition}, {pub_year})\n"
                            f"Details: {description}\n"
                            f"Statutory Legal Standing: Recognized under the First Schedule of the Drugs and Cosmetics Act, "
                            f"1940 (Section 3(a)). Formulations prepared strictly in accordance with recipes in this authoritative "
                            f"text are categorized as Classical (Shastriya) Ayurvedic medicines and are subject to the Section 3(p) "
                            f"Traditional Knowledge patent bar under the Indian Patents Act, 1970."
                        )
                        chunks.append({
                            "source_id": "TKDL_AYURVEDA_BOOKS",
                            "source_title": "First Schedule Classical Ayurvedic Texts",
                            "authority": "Drugs & Cosmetics Act, 1940 (First Schedule) / CSIR",
                            "jurisdiction": "IN",
                            "document_type": "CATALOGUE",
                            "authority_level": 4,
                            "domain": "CLASSICAL_TEXTS",
                            "section_number": f"Book: {title}",
                            "heading": title,
                            "text": combined_text,
                            "raw_statute": f"{title} (Author: {author}). Recognized under First Schedule, Drugs & Cosmetics Act 1940.",
                            "source_url": tkdl_url or "https://www.tkdl.res.in/",
                            "source_sha256": self.compute_sha256(combined_text),
                            "chunk_hash": self.compute_sha256(combined_text),
                            "topics": ["classical_texts", "first_schedule", "shastriya_ayurveda"]
                        })
            except Exception as e:
                pass

        # 3. Glossary Terms (glossary.csv)
        glossary_path = csv_dir / "glossary.csv"
        if glossary_path.exists():
            try:
                with open(glossary_path, "r", encoding="utf-8", errors="replace") as f:
                    for row in csv.DictReader(f):
                        term = row.get("term", "").strip()
                        category = row.get("category", "").strip()
                        definition = row.get("definition", "").strip()
                        gid = row.get("glossary_id", "GLOS")

                        if not term or not definition:
                            continue

                        combined_text = (
                            f"[Ayurvedic Concept & Terminology: {term}]\n"
                            f"Term: {term}\n"
                            f"Category / Branch: {category}\n"
                            f"Definition: {definition}\n"
                            f"Statutory Context: Standardized under Traditional Knowledge Digital Library (TKDL) and "
                            f"Ayush clinical practice frameworks for therapeutic claims evaluation."
                        )
                        chunks.append({
                            "source_id": "TKDL_AYURVEDIC_GLOSSARY",
                            "source_title": "TKDL Ayurvedic Clinical & Regulatory Glossary",
                            "authority": "CSIR & Ministry of Ayush",
                            "jurisdiction": "IN",
                            "document_type": "GLOSSARY",
                            "authority_level": 3,
                            "domain": "GLOSSARY",
                            "section_number": f"Term: {term}",
                            "heading": f"{term} ({category})",
                            "text": combined_text,
                            "raw_statute": f"{term} ({category}): {definition}",
                            "source_url": "https://www.tkdl.res.in/",
                            "source_sha256": self.compute_sha256(combined_text),
                            "chunk_hash": self.compute_sha256(combined_text),
                            "topics": ["ayurvedic_glossary", "clinical_terminology", category.lower()]
                        })
            except Exception as e:
                pass

        # 4. Official CGPDTM Patents Act, Rules, Forms & Amendments (data/IPINDIA)
        ipindia_dir = Path(__file__).resolve().parents[3] / "data" / "IPINDIA"
        if ipindia_dir.exists():
            # A. Full Canonical Patents Act & Rules Provisions
            patents_full_path = ipindia_dir / "patents_act_rules_full.csv"
            if patents_full_path.exists():
                try:
                    with open(patents_full_path, "r", encoding="utf-8", errors="replace") as f:
                        for row in csv.DictReader(f):
                            prov_id = row.get("provision_id", "").strip()
                            instrument = row.get("instrument", "Patents Act").strip()
                            sec_rule = row.get("section_or_rule", "").strip()
                            title = row.get("title", "").strip()
                            summary = row.get("summary", "").strip()
                            prov_type = row.get("provision_type", "Section").strip()
                            ayur_rel = row.get("relevance_to_ayurveda", "None").strip()
                            tk_rel = row.get("relevance_to_traditional_knowledge", "None").strip()
                            bio_rel = row.get("relevance_to_biodiversity", "None").strip()
                            pat_rel = row.get("relevance_to_patentability", "None").strip()
                            source_url = row.get("source_url", "").strip()

                            if not sec_rule or not summary:
                                continue

                            is_act = "Act" in instrument
                            source_id = "IND_PATENTS_ACT_1970" if is_act else "IND_PATENTS_RULES_2003"
                            source_title = "The Patents Act, 1970 (as amended 2024)" if is_act else "The Patents Rules, 2003 (as amended 2024)"
                            auth_level = 5 if is_act else 4

                            combined_text = (
                                f"[Official Patent Provision: {instrument} {prov_type} {sec_rule} - {title}]\n"
                                f"Statute: {source_title}\n"
                                f"Provision: {prov_type} {sec_rule} ({title})\n"
                                f"Statutory Content: {summary}\n"
                                f"Relevance: Traditional Knowledge: {tk_rel} | Ayurveda: {ayur_rel} | Biodiversity: {bio_rel} | Patentability: {pat_rel}\n"
                                f"Authority: Controller General of Patents, Designs and Trade Marks (CGPDTM), India."
                            )

                            chunks.append({
                                "source_id": source_id,
                                "source_title": source_title,
                                "authority": "Office of the Controller General of Patents, Designs and Trade Marks (CGPDTM)",
                                "jurisdiction": "IN",
                                "document_type": "ACT" if is_act else "RULES",
                                "authority_level": auth_level,
                                "domain": "PATENTS_AND_IP",
                                "section_number": f"{prov_type} {sec_rule}",
                                "heading": title,
                                "text": combined_text,
                                "raw_statute": f"{prov_type} {sec_rule} ({title}): {summary}",
                                "source_url": source_url or "https://ipindia.gov.in/",
                                "source_sha256": self.compute_sha256(combined_text),
                                "chunk_hash": self.compute_sha256(combined_text),
                                "topics": ["patents", "ipindia", prov_type.lower(), tk_rel.lower(), ayur_rel.lower()]
                            })
                except Exception:
                    pass

            # B. Official Patent Filing Forms (patent_forms.csv)
            forms_path = ipindia_dir / "patent_forms.csv"
            if forms_path.exists():
                try:
                    with open(forms_path, "r", encoding="utf-8", errors="replace") as f:
                        for row in csv.DictReader(f):
                            form_num = row.get("form_number", "").strip()
                            form_title = row.get("form_title", "").strip()
                            purpose = row.get("purpose", "").strip()
                            related_sec = row.get("related_section_or_rule", "").strip()
                            source_url = row.get("source_url", "").strip()

                            if not form_num or not form_title:
                                continue

                            combined_text = (
                                f"[Official CGPDTM Patent Form: {form_num} - {form_title}]\n"
                                f"Form Number: {form_num}\n"
                                f"Form Title: {form_title}\n"
                                f"Official Purpose: {purpose}\n"
                                f"Governing Sections & Rules: {related_sec}\n"
                                f"Issuing Authority: Office of the Controller General of Patents, Designs and Trade Marks (CGPDTM), India\n"
                                f"Regulatory Function: Statutory procedural filing prescribed under The Patents Rules, 2003 (as amended 2024)."
                            )

                            chunks.append({
                                "source_id": "IND_PATENT_FORMS_CGPDTM",
                                "source_title": "Official CGPDTM Patent Filing Forms (Patents Rules 2003/2024)",
                                "authority": "Office of the Controller General of Patents, Designs and Trade Marks (CGPDTM)",
                                "jurisdiction": "IN",
                                "document_type": "FORM",
                                "authority_level": 4,
                                "domain": "PATENTS_AND_IP",
                                "section_number": f"Form: {form_num}",
                                "heading": form_title,
                                "text": combined_text,
                                "raw_statute": f"{form_num} - {form_title}: {purpose}. Governing: {related_sec}",
                                "source_url": source_url or "https://ipindia.gov.in/",
                                "source_sha256": self.compute_sha256(combined_text),
                                "chunk_hash": self.compute_sha256(combined_text),
                                "topics": ["patent_forms", "filing_procedure", form_num.lower(), "cgpdtm"]
                            })
                except Exception:
                    pass

            # C. Patent Amendments (patent_amendments.csv)
            amends_path = ipindia_dir / "patent_amendments.csv"
            if amends_path.exists():
                try:
                    with open(amends_path, "r", encoding="utf-8", errors="replace") as f:
                        for row in csv.DictReader(f):
                            amend_name = row.get("amendment_name", "").strip()
                            amend_year = row.get("amendment_year", "").strip()
                            affected = row.get("affected_section_or_rule", "").strip()
                            summary = row.get("change_summary", "").strip()
                            source_url = row.get("official_gazette_url", "").strip()

                            if not amend_name:
                                continue

                            combined_text = (
                                f"[Official Patent Legislative Reform: {amend_name} ({amend_year})]\n"
                                f"Statutory Reform: {amend_name}\n"
                                f"Affected Provisions: {affected}\n"
                                f"Summary of Legal Changes: {summary}\n"
                                f"Authority: Ministry of Commerce & Industry (DPIIT) / Ministry of Law & Justice, India."
                            )

                            chunks.append({
                                "source_id": "IND_PATENTS_AMENDMENTS",
                                "source_title": f"{amend_name} ({amend_year})",
                                "authority": "Ministry of Commerce and Industry (DPIIT) / Ministry of Law and Justice",
                                "jurisdiction": "IN",
                                "document_type": "AMENDMENT",
                                "authority_level": 5,
                                "domain": "PATENTS_AND_IP",
                                "section_number": f"Reform: {amend_name}",
                                "heading": amend_name,
                                "text": combined_text,
                                "raw_statute": f"{amend_name}: {summary}",
                                "source_url": source_url or "https://egazette.gov.in/",
                                "source_sha256": self.compute_sha256(combined_text),
                                "chunk_hash": self.compute_sha256(combined_text),
                                "topics": ["patent_amendments", "legal_reforms", amend_year]
                            })
                except Exception:
                    pass

        return chunks

    def extract_chunks_from_extracted_text(
        self,
        extracted_rel_path: str,
        source_meta: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Parses full authentic statute text into atomic section chunks using standard India Code formatting.
        Extracts all enacted sections, titles, and verbatim text.
        """
        full_path = Path(__file__).resolve().parents[3] / extracted_rel_path
        if not full_path.exists():
            return []

        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception:
            return []

        source_id = source_meta.get("source_id", "UNKNOWN_SOURCE")
        title = source_meta.get("title", source_meta.get("short_title", ""))
        authority = source_meta.get("authority", "")
        jurisdiction = source_meta.get("jurisdiction", "IN")
        doc_type = source_meta.get("document_type", "ACT")
        authority_level = source_meta.get("authority_level", 5)
        source_url = source_meta.get("official_url", "")
        file_sha256 = self.compute_file_sha256(full_path)

        chunks = []

        # Locate where enacted sections start (skip Table of Contents / Arrangement of Sections)
        enacted_start = 0
        match_enact = re.search(
            r"(?:BE it enacted|CHAPTER I\s*\n\s*PRELIMINARY|CHAPTER I\s*\n\s*INTRODUCTORY)",
            content,
            re.IGNORECASE
        )
        if match_enact:
            enacted_start = match_enact.start()

        body_content = content[enacted_start:]

        # Standard India Code section pattern: "<num>. <heading>.—<text>"
        sec_pattern = re.compile(
            r"\n\s*(?P<sec_num>\d+[A-Z]?)\.\s+(?P<heading>[^—\n\.\?]{3,80}?)(?:[—\.\-]|(?:\.\s*—))\s*(?P<body>[\s\S]*?)(?=\n\s*\d+[A-Z]?\.\s+[^—\n\.\?]{3,80}?(?:[—\.\-]|(?:\.\s*—))|\n\s*THE SCHEDULE|\Z)"
        )

        for match in sec_pattern.finditer(body_content):
            sec_num = match.group("sec_num").strip()
            heading = match.group("heading").strip()
            body = match.group("body").strip()

            # Clean out page headers and standalone page numbers
            clean_body = re.sub(r"Central Drugs Standard.*Page \d+ of \d+", "", body, flags=re.IGNORECASE)
            clean_body = re.sub(r"\n\s*\d+\s*\n", "\n", clean_body)
            clean_body = re.sub(r"\s+", " ", clean_body).strip()

            if len(clean_body) < 15:
                continue

            sec_display = f"Section {sec_num}"
            combined_text = f"[{title} — {sec_display}: {heading}]\n{clean_body[:1200]}"

            chunks.append({
                "source_id": source_id,
                "provision_id": f"{source_id}_SEC_{sec_num}",
                "source_title": title,
                "authority": authority,
                "jurisdiction": jurisdiction,
                "document_type": doc_type,
                "authority_level": authority_level,
                "domain": source_meta.get("domain", "PATENTS"),
                "section_number": sec_display,
                "heading": heading,
                "text": combined_text,
                "raw_statute": clean_body[:1000],
                "source_url": source_url,
                "source_sha256": file_sha256,
                "chunk_hash": self.compute_sha256(combined_text)
            })

        return chunks

    def process_all_sources(self) -> List[Dict[str, Any]]:
        sources_meta = self.parse_manifest()
        all_chunks = []
        for src in sources_meta:
            covered_sections = set()
            rel_path = src.get("normalized_file") or src.get("file_path", "")
            data = self.parse_source_file(rel_path)
            if data:
                chunks = self.extract_chunks_from_source(data)
                all_chunks.extend(chunks)
                for c in chunks:
                    sec_str = c.get("section_number", "")
                    if sec_str:
                        covered_sections.add(sec_str.lower().strip())

            # Parse full-text statute from disk if available to achieve comprehensive section coverage
            extracted_rel = src.get("extracted_text_path")
            if extracted_rel:
                raw_chunks = self.extract_chunks_from_extracted_text(extracted_rel, src)
                for rc in raw_chunks:
                    rc_sec = rc.get("section_number", "").lower().strip()
                    # Include if not already covered by high-precision curated provision
                    if rc_sec not in covered_sections:
                        all_chunks.append(rc)
                        covered_sections.add(rc_sec)

        # Include structured taxonomy chunks from CSVs
        csv_chunks = self.extract_chunks_from_csvs()
        all_chunks.extend(csv_chunks)

        return all_chunks
