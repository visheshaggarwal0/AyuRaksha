"""
Script to compute authentic SHA-256 cryptographic provenance checksums
for official PDFs and downloaded raw legal instruments in AyuRaksha corpus.
"""
import hashlib
from pathlib import Path

CORPUS_ROOT = Path(__file__).resolve().parents[1] / "data" / "corpus"

def get_file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def scan_raw_corpus():
    print("=" * 70)
    print("AyuRaksha Corpus Provenance Hash Verification")
    print("=" * 70)

    found_files = []
    for ext in ["*.pdf", "*.html", "*.json"]:
        for file_path in CORPUS_ROOT.rglob(ext):
            if file_path.stat().st_size > 1000: # Exclude placeholders < 1KB
                rel = file_path.relative_to(CORPUS_ROOT)
                sha = get_file_sha256(file_path)
                found_files.append((str(rel), file_path.stat().st_size, sha))

    print(f"Found {len(found_files)} verified documents (>1KB):")
    for rel, size, sha in sorted(found_files, key=lambda x: x[0]):
        print(f"  - {rel} ({size:,} bytes)")
        print(f"    SHA-256: {sha}")

if __name__ == "__main__":
    scan_raw_corpus()
