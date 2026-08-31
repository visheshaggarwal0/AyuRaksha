"""Text extraction for official PDF and HTML sources, with optional OCR fallback."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import List


class ExtractionError(RuntimeError):
    pass


@dataclass(frozen=True)
class ExtractedDocument:
    text: str
    mime_type: str
    page_count: int | None = None
    ocr_used: bool = False


class _HtmlTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: List[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript"}:
            self._ignored_depth += 1
        elif tag in {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "tr"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth:
            self.parts.append(data)


def extract_html(path: Path) -> ExtractedDocument:
    parser = _HtmlTextExtractor()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    text = "\n".join(line.strip() for line in "".join(parser.parts).splitlines() if line.strip())
    if not text:
        raise ExtractionError(f"No readable text found in HTML source: {path}")
    return ExtractedDocument(text=text, mime_type="text/html")


def extract_pdf(path: Path, enable_ocr: bool = True) -> ExtractedDocument:
    try:
        import fitz
    except ImportError as error:
        raise ExtractionError("PDF extraction requires PyMuPDF. Install backend requirements.") from error

    pdf = fitz.open(path)
    pages = [page.get_text("text").strip() for page in pdf]
    text = "\n\n".join(page for page in pages if page)
    if text:
        return ExtractedDocument(text=text, mime_type="application/pdf", page_count=len(pdf))
    if not enable_ocr:
        raise ExtractionError(f"PDF has no selectable text and OCR is disabled: {path}")

    try:
        import pytesseract
        from PIL import Image
    except ImportError as error:
        raise ExtractionError("OCR requires pytesseract and Pillow. Install backend requirements.") from error

    ocr_pages = []
    for page in pdf:
        pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        image = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
        ocr_pages.append(pytesseract.image_to_string(image).strip())
    text = "\n\n".join(page for page in ocr_pages if page)
    if not text:
        raise ExtractionError(f"OCR produced no text for: {path}")
    return ExtractedDocument(text=text, mime_type="application/pdf", page_count=len(pdf), ocr_used=True)


def extract_document(path: Path, enable_ocr: bool = True) -> ExtractedDocument:
    suffix = path.suffix.lower()
    if suffix in {".html", ".htm"}:
        return extract_html(path)
    if suffix == ".pdf":
        return extract_pdf(path, enable_ocr=enable_ocr)
    if suffix in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8", errors="replace").strip()
        if text:
            return ExtractedDocument(text=text, mime_type="text/plain")
    raise ExtractionError(f"Unsupported or empty source format: {path}")
