"""CLI for the authoritative-source pipeline: raw -> normalized -> validated."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from app.corpus.extraction import extract_document
from app.corpus.normalizer import normalize_document
from app.corpus.validation import validate_normalized_document, validate_raw_source


PROJECT_ROOT = Path(__file__).resolve().parents[3]
CORPUS_ROOT = PROJECT_ROOT / "data" / "corpus"


def _find_raw_file(source: Dict[str, Any]) -> Path:
    configured_path = source.get("local_path") or source.get("raw_file_name")
    if configured_path:
        direct_path = CORPUS_ROOT / configured_path
        if direct_path.is_file():
            return direct_path
        matches = list((CORPUS_ROOT / "raw").rglob(Path(configured_path).name))
        if len(matches) == 1:
            return matches[0]
    raise FileNotFoundError(f"No raw file found for {source['source_id']}")


def normalize_manifest(manifest_path: Path, enable_ocr: bool = True) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sources = manifest.get("sources", [])
    processed = 0
    for source in sources:
        raw_path = _find_raw_file(source)
        expected_hash = source.get("sha256") or source.get("source", {}).get("sha256")
        sha256 = validate_raw_source(raw_path, expected_hash or None)
        normalized = normalize_document(source, extract_document(raw_path, enable_ocr=enable_ocr), sha256)
        warnings = validate_normalized_document(normalized)
        output = PROJECT_ROOT / source.get(
            "normalized_file", f"data/corpus/normalized/generated/{source['source_id'].lower()}.json"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(normalized, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Normalized {source['source_id']} -> {output.relative_to(PROJECT_ROOT)}")
        for warning in warnings:
            print(f"  warning: {warning}")
        processed += 1
    return processed


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize verified official sources for AyuRaksha RAG.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=CORPUS_ROOT / "manifest" / "sources_manifest.json",
    )
    parser.add_argument("--no-ocr", action="store_true", help="Fail instead of applying OCR to scanned PDFs.")
    args = parser.parse_args()
    count = normalize_manifest(args.manifest, enable_ocr=not args.no_ocr)
    print(f"Validated and normalized {count} authoritative sources.")


if __name__ == "__main__":
    main()
