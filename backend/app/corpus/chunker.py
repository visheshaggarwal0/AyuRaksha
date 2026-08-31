import json
import hashlib
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

    def parse_manifest(self) -> List[Dict[str, Any]]:
        # Check upgraded manifest first
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

        return chunks

    def process_all_sources(self) -> List[Dict[str, Any]]:
        sources_meta = self.parse_manifest()
        all_chunks = []
        for src in sources_meta:
            rel_path = src.get("normalized_file") or src.get("file_path", "")
            data = self.parse_source_file(rel_path)
            if data:
                chunks = self.extract_chunks_from_source(data)
                all_chunks.extend(chunks)
        return all_chunks
