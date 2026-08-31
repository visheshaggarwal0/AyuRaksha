"""
ETL Step 2: Semantic Chunker & Embedder
Reads extracted text, chunks it, generates embeddings, and inserts into Neon PostgreSQL.
"""

import asyncio
import json
import pathlib
import sys
import logging
from typing import List

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import Source, SourceVersion, SourceSection, DocumentChunk
from app.engines.vector_store import generate_deterministic_embedding

MANIFEST_PATH = ROOT / "data" / "corpus" / "manifests" / "source_manifest_extracted.json"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Simple Recursive Character-like Splitter."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        
        # Try to find a natural break (newline or period) if not at the very end
        if end < len(text):
            break_point = max(text.rfind("\n\n", start, end), text.rfind(". ", start, end))
            if break_point != -1 and break_point > start + (chunk_size // 2):
                end = break_point + 1 # Include the period or first newline
                
        chunk = text[start:end].strip()
        if len(chunk) > 50: # Skip tiny fragments
            chunks.append(chunk)
            
        start = end - overlap if end < len(text) else len(text)
    return chunks

async def process_and_embed():
    if not MANIFEST_PATH.exists():
        logger.error(f"Manifest not found: {MANIFEST_PATH}")
        return

    with MANIFEST_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    sources = data.get("sources", [])
    success_sources = [s for s in sources if s.get("source", {}).get("extraction_status") == "SUCCESS"]
    
    logger.info(f"Found {len(success_sources)} successfully extracted documents to process.")

    async with AsyncSessionLocal() as session:
        for idx, source_meta in enumerate(success_sources):
            doc_id = source_meta.get("document_id")
            title = source_meta.get("title")
            jurisdiction = source_meta.get("jurisdiction", "IN")
            authority = source_meta.get("authority", "Unknown")
            doc_type = source_meta.get("document_type", "UNKNOWN")
            url = source_meta.get("source", {}).get("url", "")
            txt_rel_path = source_meta.get("extracted_text_path")
            
            if not txt_rel_path:
                continue
                
            txt_path = ROOT / txt_rel_path
            if not txt_path.exists():
                logger.warning(f"Text file missing for {doc_id}: {txt_path}")
                continue

            with txt_path.open("r", encoding="utf-8") as f:
                raw_text = f.read()

            if not raw_text.strip():
                logger.warning(f"Text file empty for {doc_id}")
                continue

            logger.info(f"[{idx+1}/{len(success_sources)}] Processing {doc_id} ({len(raw_text)} chars)...")

            # 1. Upsert Source
            stmt = select(Source).where(Source.source_code == doc_id)
            result = await session.execute(stmt)
            db_source = result.scalars().first()
            if not db_source:
                db_source = Source(
                    source_code=doc_id,
                    title=title,
                    authority=authority,
                    document_type=doc_type,
                    jurisdiction=jurisdiction,
                    source_url=url,
                    authority_level=source_meta.get("authority_level", 3)
                )
                session.add(db_source)
                await session.flush()

            # 2. Upsert SourceVersion
            stmt = select(SourceVersion).where(SourceVersion.source_id == db_source.id)
            result = await session.execute(stmt)
            db_version = result.scalars().first()
            if not db_version:
                db_version = SourceVersion(source_id=db_source.id, version_label="1.0")
                session.add(db_version)
                await session.flush()

            # 3. Create a generic SourceSection (since we don't have deep structure detection yet)
            stmt = select(SourceSection).where(SourceSection.source_version_id == db_version.id)
            result = await session.execute(stmt)
            db_section = result.scalars().first()
            if not db_section:
                db_section = SourceSection(
                    source_version_id=db_version.id,
                    section_number="Full Document",
                    heading=title,
                    text="<Full document text split into chunks>"
                )
                session.add(db_section)
                await session.flush()
            else:
                # If section exists, let's clear old chunks to avoid duplicates during re-runs
                logger.info(f"  Clearing old chunks for {doc_id}...")
                await session.run_sync(lambda sync_session: sync_session.query(DocumentChunk).filter(DocumentChunk.section_id == db_section.id).delete())

            # 4. Chunking
            chunks = chunk_text(raw_text)
            logger.info(f"  Split into {len(chunks)} chunks. Generating embeddings...")

            # 5. Embedding & Insertion
            for c_idx, chunk_text_content in enumerate(chunks):
                # Generate deterministic offline embedding (1536 dim)
                vector = generate_deterministic_embedding(chunk_text_content)
                
                db_chunk = DocumentChunk(
                    section_id=db_section.id,
                    text=chunk_text_content,
                    embedding=vector,
                    token_count=len(chunk_text_content.split()),
                    jurisdiction=jurisdiction,
                    chunk_metadata={"domain": "STATUTE", "source_id": doc_id, "chunk_index": c_idx}
                )
                session.add(db_chunk)

            await session.commit()
            logger.info(f"  Saved {len(chunks)} chunks for {doc_id} to Neon DB.")

    logger.info("ETL Step 2 Completed Successfully!")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(process_and_embed())
