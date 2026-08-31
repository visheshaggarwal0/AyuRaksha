"""Convert extracted legal text into the normalized provision format used by RAG."""

from __future__ import annotations

import re
from datetime import date
from typing import Any, Dict, List

from app.corpus.extraction import ExtractedDocument


PROVISION_START = re.compile(
    r"(?im)^\s*(?P<type>section|rule|article|regulation)\s+(?P<number>[\d]+(?:\([\w\d]+\))*(?:[A-Za-z-]+)?)\s*[.:-]?\s*(?P<heading>[^\n]{0,180})$"
)


def _provision_id(document_id: str, provision_type: str, number: str, index: int) -> str:
    safe_number = re.sub(r"[^A-Za-z0-9]+", "_", number).strip("_")
    return f"{document_id}_{provision_type}_{safe_number or index:>03}".replace(" ", "_").upper()


def detect_provisions(document_id: str, text: str) -> List[Dict[str, Any]]:
    matches = list(PROVISION_START.finditer(text))
    provisions: List[Dict[str, Any]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if len(body) < 20:
            continue
        provision_type = match.group("type").upper()
        number = match.group("number")
        heading = match.group("heading").strip(" .:-")
        provisions.append({
            "provision_id": _provision_id(document_id, provision_type, number, index + 1),
            "type": provision_type,
            "number": number,
            "heading": heading or f"{provision_type.title()} {number}",
            "text": body,
            "location": {},
            "topics": [],
            "statutory_significance": "Extracted from authoritative source; human review pending.",
        })

    if not provisions and text.strip():
        provisions.append({
            "provision_id": _provision_id(document_id, "DOCUMENT", "1", 1),
            "type": "DOCUMENT",
            "number": "1",
            "heading": "Extracted document text",
            "text": text.strip(),
            "location": {},
            "topics": [],
            "statutory_significance": "Whole-document fallback; section structure requires review.",
        })
    return provisions


def normalize_document(source: Dict[str, Any], extracted: ExtractedDocument, sha256: str) -> Dict[str, Any]:
    document_id = source["source_id"]
    source_metadata = source.get("source", {})
    return {
        "document_id": document_id,
        "title": source["title"],
        "short_title": source.get("short_title", source["title"]),
        "jurisdiction": source.get("jurisdiction", "IN"),
        "authority": source["authority"],
        "issuing_body": source.get("issuing_body", ""),
        "domain": source.get("domain", ["GENERAL"]),
        "document_type": source.get("document_type", "ACT"),
        "authority_level": source.get("authority_level", 5),
        "source": {
            "url": source.get("official_url") or source_metadata.get("url", ""),
            "source_type": source_metadata.get("source_type", "OFFICIAL"),
            "retrieved_at": str(date.today()),
            "file_name": source.get("raw_file_name") or source_metadata.get("file_name", ""),
            "sha256": sha256,
            "mime_type": extracted.mime_type,
            "ocr_used": extracted.ocr_used,
            "page_count": extracted.page_count,
            "storage_uri": source.get("storage_uri", ""),
        },
        "version": source.get("version", {"version_label": "Extracted"}),
        "provisions": detect_provisions(document_id, extracted.text),
        "knowledge_relations": source.get("knowledge_relations", []),
    }
