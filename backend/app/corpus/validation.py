"""Integrity checks for provenance-preserving legal corpus records."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List


class CorpusValidationError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source_file:
        for block in iter(lambda: source_file.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_raw_source(path: Path, expected_sha256: str | None = None) -> str:
    if not path.is_file() or path.stat().st_size == 0:
        raise CorpusValidationError(f"Raw source is missing or empty: {path}")

    actual_hash = sha256_file(path)
    if expected_sha256 and expected_sha256.lower() != actual_hash:
        raise CorpusValidationError(
            f"SHA-256 mismatch for {path.name}: expected {expected_sha256}, got {actual_hash}"
        )
    return actual_hash


def validate_normalized_document(document: Dict[str, Any]) -> List[str]:
    required = ("document_id", "title", "jurisdiction", "authority", "source")
    missing = [field for field in required if not document.get(field)]
    if missing:
        raise CorpusValidationError(f"Normalized document is missing: {', '.join(missing)}")

    provisions = document.get("provisions", [])
    if not provisions:
        raise CorpusValidationError("Normalized document has no provisions")

    identifiers: set[str] = set()
    warnings: List[str] = []
    for position, provision in enumerate(provisions, start=1):
        provision_id = provision.get("provision_id")
        if not provision_id or provision_id in identifiers:
            raise CorpusValidationError(f"Invalid or duplicate provision_id at position {position}")
        identifiers.add(provision_id)
        if not provision.get("text", "").strip():
            raise CorpusValidationError(f"Provision {provision_id} has no text")
        if not provision.get("number"):
            warnings.append(f"Provision {provision_id} has no section/rule number")

    source_hash = document["source"].get("sha256")
    if not source_hash:
        warnings.append("Document is not linked to a SHA-256 raw-source hash")
    return warnings
