"""
ETL Step 1: Source Downloader & Extractor
Reads the expanded manifest, downloads PDFs, and extracts raw text using PyMuPDF.
"""

import json
import hashlib
import pathlib
import sys
import logging
import urllib.request
import urllib.error
import time
import random
from datetime import datetime, timezone
from PIL import Image
import pytesseract

try:
    import pymupdf as fitz  # PyMuPDF
except ImportError:
    try:
        import fitz
    except ImportError:
        print("PyMuPDF is required. Please install it using `pip install PyMuPDF`.")
        sys.exit(1)

# Disable SSL verification for unstable government sites
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Set up paths
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MANIFEST_IN = ROOT / "data" / "corpus" / "manifests" / "source_manifest_expanded_150.json"
MANIFEST_OUT = ROOT / "data" / "corpus" / "manifests" / "source_manifest_extracted.json"
RAW_DIR = ROOT / "data" / "corpus" / "raw_downloads"
EXTRACTED_DIR = ROOT / "data" / "corpus" / "extracted"

RAW_DIR.mkdir(parents=True, exist_ok=True)
EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)
MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
}

def sha256_file(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def extract_pdf_text(pdf_path: pathlib.Path) -> str:
    """Extracts all text from a PDF file using PyMuPDF, with OCR fallback for scanned images."""
    text = ""
    try:
        doc = fitz.open(str(pdf_path))
        for page in doc:
            page_text = page.get_text().strip()
            if page_text:
                text += page_text + "\n\n"
            else:
                # OCR Fallback for image-based PDFs (e.g. API_VOL_1)
                try:
                    pix = page.get_pixmap(dpi=150)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_text = pytesseract.image_to_string(img)
                    if ocr_text.strip():
                        text += ocr_text.strip() + "\n\n"
                except Exception as ocr_err:
                    logger.debug(f"OCR failed on page {page.number} of {pdf_path.name}: {ocr_err}")
                    
        doc.close()
    except Exception as e:
        logger.error(f"Failed to extract text from {pdf_path.name}: {e}")
    return text.strip()

def fetch_url_with_retry(url: str, dest_path: pathlib.Path, doc_id: str, max_retries: int = 3):
    """Downloads a file with exponential backoff to bypass aggressive anti-bot firewalls (WinError 10054/10060)."""
    delay = 2
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=30, context=ctx) as response, dest_path.open("wb") as out_file:
                out_file.write(response.read())
            return True
        except urllib.error.HTTPError as e:
            if e.code in [404, 410]: # Permanent errors
                logger.error(f"Failed to download {doc_id} (Attempt {attempt+1}/{max_retries}): HTTP Error {e.code}")
                return False
            logger.warning(f"HTTP Error {e.code} for {doc_id}. Retrying in {delay}s...")
        except Exception as e:
            logger.warning(f"Connection error for {doc_id} (Attempt {attempt+1}/{max_retries}): {e}. Retrying in {delay}s...")
        
        time.sleep(delay + random.uniform(0.5, 1.5))
        delay *= 2
        
    logger.error(f"Failed to download {doc_id} after {max_retries} attempts.")
    return False

def download_and_extract(limit: int = None):
    if not MANIFEST_IN.exists():
        logger.error(f"Input manifest not found: {MANIFEST_IN}")
        return

    with MANIFEST_IN.open("r", encoding="utf-8") as f:
        data = json.load(f)
    
    sources = data.get("sources", [])
    if limit:
        sources = sources[:limit]
        logger.info(f"Limiting to first {limit} sources for testing.")
    
    success_count = 0
    
    for idx, source in enumerate(sources):
        doc_id = source.get("document_id", "UNKNOWN")
        src_meta = source.get("source", {})
        url = src_meta.get("url")
        
        if not url or url.startswith("http://example.com"):
            logger.info(f"[{idx+1}/{len(sources)}] Skipping {doc_id} (No valid URL)")
            src_meta["extraction_status"] = "SKIPPED_NO_URL"
            continue
            
        file_name = src_meta.get("file_name", f"{doc_id.lower()}.pdf")
        if not file_name.endswith(".pdf"):
            file_name += ".pdf"
            
        raw_path = RAW_DIR / file_name
        txt_path = EXTRACTED_DIR / f"{doc_id.lower()}.txt"
        
        # 1. Download
        if not raw_path.exists():
            logger.info(f"[{idx+1}/{len(sources)}] Downloading {doc_id} from {url}...")
            
            # Anti-bot delay before request to avoid IP ban (TKDL is very strict)
            time.sleep(random.uniform(1.0, 3.0))
            
            success = fetch_url_with_retry(url, raw_path, doc_id)
            if not success:
                src_meta["extraction_status"] = "FAILED_DOWNLOAD"
                continue
        else:
            logger.info(f"[{idx+1}/{len(sources)}] {doc_id} already exists locally.")

        # 2. Extract
        if raw_path.exists() and not txt_path.exists():
            logger.info(f"[{idx+1}/{len(sources)}] Extracting text from {doc_id}...")
            raw_text = extract_pdf_text(raw_path)
            if raw_text:
                with txt_path.open("w", encoding="utf-8") as out_txt:
                    out_txt.write(raw_text)
            else:
                logger.warning(f"Extracted text was empty for {doc_id}.")
                src_meta["extraction_status"] = "FAILED_EXTRACTION_EMPTY"
                continue
        
        # 3. Update Metadata
        if raw_path.exists() and txt_path.exists():
            src_meta["sha256"] = sha256_file(raw_path)
            src_meta["file_size_bytes"] = raw_path.stat().st_size
            src_meta["extraction_status"] = "SUCCESS"
            
            source["local_path"] = str(raw_path.relative_to(ROOT)).replace("\\", "/")
            source["extracted_text_path"] = str(txt_path.relative_to(ROOT)).replace("\\", "/")
            success_count += 1
            
    # Save the updated manifest
    data["sources"] = sources
    with MANIFEST_OUT.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    logger.info(f"Finished! Successfully extracted {success_count}/{len(sources)} documents.")
    logger.info(f"Updated manifest saved to: {MANIFEST_OUT}")

if __name__ == "__main__":
    # If an argument is provided, limit the number of downloads (e.g. `python script.py 3`)
    limit_val = None
    if len(sys.argv) > 1:
        try:
            limit_val = int(sys.argv[1])
        except ValueError:
            pass
    download_and_extract(limit=limit_val)
