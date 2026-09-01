import json
import pathlib
import sys
import logging

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import fitz  # PyMuPDF
import pytesseract

# Explicitly set Tesseract path so you don't have to restart your terminal/IDE
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

from PIL import Image
import io

RAW_DIR = ROOT / "data" / "corpus" / "raw_downloads"
EXTRACTED_DIR = ROOT / "data" / "corpus" / "extracted"
MANIFEST_OUT = ROOT / "data" / "corpus" / "manifests" / "source_manifest_extracted.json"

EXTRACTED_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def extract_pdf_text(pdf_path: pathlib.Path) -> str:
    text_content = []
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text = page.get_text("text")
                if text.strip():
                    text_content.append(text)
                else:
                    try:
                        pix = page.get_pixmap()
                        img = Image.open(io.BytesIO(pix.tobytes("png")))
                        ocr_text = pytesseract.image_to_string(img)
                        text_content.append(ocr_text)
                    except Exception as e:
                        logger.warning(f"OCR failed on page {page.number} of {pdf_path.name}: {e}")
    except Exception as e:
        logger.error(f"Failed to read PDF {pdf_path.name}: {e}")
        return ""
    return "\n\n".join(text_content)

def run():
    # Load existing extracted manifest
    if MANIFEST_OUT.exists():
        with MANIFEST_OUT.open("r", encoding="utf-8") as f:
            manifest = json.load(f)
    else:
        manifest = {"sources": []}
        
    existing_docs = {s.get("document_id") for s in manifest.get("sources", [])}
    
    pdfs = list(RAW_DIR.glob("*.pdf"))
    tkdl_pdfs = [p for p in pdfs if not p.name.startswith("ind_") and not p.name.startswith("int_") and "PATENTS_ACT" not in p.name.upper()]
    
    logger.info(f"Found {len(tkdl_pdfs)} TKDL case PDFs to process...")
    
    for idx, pdf_path in enumerate(tkdl_pdfs):
        doc_id = f"TKDL_CASE_{pdf_path.stem.replace(' ', '_').upper()}"
        
        if doc_id in existing_docs:
            continue
            
        txt_path = EXTRACTED_DIR / f"{doc_id.lower()}.txt"
        
        # Extract text
        if not txt_path.exists():
            logger.info(f"[{idx+1}/{len(tkdl_pdfs)}] Extracting {doc_id}...")
            text = extract_pdf_text(pdf_path)
            
            if not text.strip():
                logger.warning(f"[{idx+1}/{len(tkdl_pdfs)}] No text extracted for {doc_id}")
                continue
                
            with txt_path.open("w", encoding="utf-8") as f:
                f.write(text)
        else:
            logger.info(f"[{idx+1}/{len(tkdl_pdfs)}] {doc_id} already extracted.")
            
        # Add to manifest
        manifest["sources"].append({
            "document_id": doc_id,
            "category": "TKDL_CASE_STUDIES",
            "jurisdiction": "INT",
            "source": {
                "title": f"TKDL Case Outcome: {pdf_path.stem}",
                "url": "https://tkdl.res.in",
                "file_name": pdf_path.name,
                "extraction_status": "SUCCESS"
            },
            "embedding_status": "PENDING"
        })
        existing_docs.add(doc_id)
        
    with MANIFEST_OUT.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    logger.info("Finished processing TKDL cases into extracted manifest!")

if __name__ == "__main__":
    run()
