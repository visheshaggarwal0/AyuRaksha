import asyncio
import uuid
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.models import Source, SourceVersion, SourceSection, DocumentChunk, KnowledgeRelation
from app.corpus.chunker import LegalDocumentChunker
from app.corpus.validation import validate_normalized_document
from app.engines.vector_store import generate_deterministic_embedding

async def ingest_corpus():
    print("=" * 60)
    print("AyuRaksha (IP-SAKTI Sahayak) — Provenance-Preserving Ingestion")
    print("=" * 60)

    chunker = LegalDocumentChunker()
    sources_meta = chunker.parse_manifest()
    print(f"[*] Found {len(sources_meta)} verified statutory sources in manifest.")

    total_chunks_inserted = 0
    total_sections_inserted = 0

    async with AsyncSessionLocal() as session:
        for src_meta in sources_meta:
            src_id_str = src_meta["source_id"]
            title = src_meta["title"]
            authority = src_meta["authority"]
            doc_type = src_meta.get("document_type", "ACT")
            jurisdiction = src_meta.get("jurisdiction", "IN")
            auth_level = src_meta.get("authority_level", 5)
            rel_path = src_meta.get("normalized_file") or src_meta.get("file_path", "")
            sha256_hash = src_meta.get("sha256", "")
            storage_uri = src_meta.get("storage_uri", "")
            official_url = src_meta.get("official_url", "")

            print(f" -> Ingesting: {title} [{jurisdiction}] (SHA-256: {sha256_hash[:10]}...)")

            source_data = chunker.parse_source_file(rel_path)
            validation_warnings = validate_normalized_document(source_data)
            for warning in validation_warnings:
                print(f"    [warning] {warning}")

            # Check if source already exists
            stmt = select(Source).where(Source.source_code == src_id_str)
            res = await session.execute(stmt)
            source = res.scalars().first()

            if not source:
                source = Source(
                    id=uuid.uuid4(),
                    source_code=src_id_str,
                    title=title,
                    authority=authority,
                    document_type=doc_type,
                    jurisdiction=jurisdiction,
                    authority_level=auth_level,
                    current_status="ACTIVE",
                    source_url=official_url,
                    content_hash=sha256_hash,
                    publication_date=datetime.utcnow()
                )
                session.add(source)
                await session.flush()
            else:
                source.title = title
                source.authority = authority
                source.source_url = official_url
                source.content_hash = sha256_hash
                source.current_status = "ACTIVE"

            # A source version is immutable. Re-ingesting an unchanged hash is a no-op.
            stmt_v = select(SourceVersion).where(
                SourceVersion.source_id == source.id,
                SourceVersion.content_hash == sha256_hash,
            )
            res_v = await session.execute(stmt_v)
            version = res_v.scalars().first()

            if version:
                print("    [skip] identical source version is already indexed")
                continue

            version = SourceVersion(
                id=uuid.uuid4(),
                source_id=source.id,
                version_label=source_data.get("version", {}).get("version_label", "Extracted"),
                effective_from=datetime(2024, 1, 1),
                content_hash=sha256_hash,
                storage_uri=storage_uri
            )
            session.add(version)
            await session.flush()

            # Parse and insert sections & chunks
            chunks = chunker.extract_chunks_from_source(source_data)

            for chunk_data in chunks:
                sec_num = chunk_data["section_number"]
                heading = chunk_data["heading"]
                raw_text = chunk_data["raw_statute"]
                full_text = chunk_data["text"]
                location = chunk_data.get("location", {})

                # Create section
                section = SourceSection(
                    id=uuid.uuid4(),
                    source_version_id=version.id,
                    section_number=sec_num,
                    heading=heading,
                    text=raw_text,
                    page_start=location.get("page_start"),
                    page_end=location.get("page_end")
                )
                session.add(section)
                await session.flush()
                total_sections_inserted += 1

                # Generate 384-dim semantic vector
                embedding_vec = generate_deterministic_embedding(full_text)

                # Create document chunk
                chunk = DocumentChunk(
                    id=uuid.uuid4(),
                    section_id=section.id,
                    text=full_text,
                    embedding=embedding_vec,
                    token_count=len(full_text.split()),
                    language="en",
                    jurisdiction=jurisdiction,
                    chunk_metadata={
                        "source_id": src_id_str,
                        "source_title": title,
                        "authority": authority,
                        "authority_level": auth_level,
                        "domain": chunk_data.get("domain", "GENERAL"),
                        "section_number": sec_num,
                        "heading": heading,
                        "source_url": chunk_data.get("source_url", official_url),
                        "source_sha256": chunk_data.get("source_sha256", sha256_hash),
                        "page_start": location.get("page_start"),
                        "topics": chunk_data.get("topics", [])
                    }
                )
                session.add(chunk)
                total_chunks_inserted += 1

            # Source-to-source and source-to-concept relations form the knowledge layer.
            for relation_data in source_data.get("knowledge_relations", []):
                target_code = relation_data.get("target_source_id")
                target_source = None
                if target_code:
                    target_result = await session.execute(
                        select(Source).where(Source.source_code == target_code)
                    )
                    target_source = target_result.scalars().first()
                session.add(KnowledgeRelation(
                    id=uuid.uuid4(),
                    subject_source_id=source.id,
                    object_source_id=target_source.id if target_source else None,
                    relation_type=relation_data.get("relation_type", "REFERENCES"),
                    target_label=relation_data.get("target_label") or target_code,
                    jurisdiction=jurisdiction,
                    evidence=relation_data.get("evidence"),
                    metadata_payload=relation_data.get("metadata", {}),
                    confidence=relation_data.get("confidence", 1.0),
                ))

        await session.commit()

        # Ingest and embed CSV taxonomy records
        tax_sections, tax_chunks = await ingest_taxonomy_csvs(session, chunker)
        total_sections_inserted += tax_sections
        total_chunks_inserted += tax_chunks

    print("=" * 60)
    print(f"[✓] Provenance Ingestion Complete!")
    print(f"    - Total Sections (Statutory + Taxonomy): {total_sections_inserted}")
    print(f"    - Total Vector Chunks (pgvector): {total_chunks_inserted}")
    print("=" * 60)

async def ingest_taxonomy_csvs(session, chunker: LegalDocumentChunker):
    print("\n[*] Ingesting and embedding TKDL CSV Taxonomy datasets...")
    csv_chunks = chunker.extract_chunks_from_csvs()
    print(f"[*] Found {len(csv_chunks)} total taxonomy chunks from CSVs.")

    chunks_by_source = {}
    for c in csv_chunks:
        sid = c["source_id"]
        chunks_by_source.setdefault(sid, []).append(c)

    taxonomy_sources_meta = {
        "TKDL_AYURVEDA_BOOKS": {
            "title": "First Schedule Classical Ayurvedic Texts",
            "authority": "Drugs & Cosmetics Act, 1940 (First Schedule) / CSIR",
            "document_type": "CATALOGUE",
            "authority_level": 4,
            "url": "https://www.tkdl.res.in/"
        },
        "TKDL_MEDICINAL_PLANTS": {
            "title": "TKDL Medicinal Plants & Botanical Taxonomy",
            "authority": "Council of Scientific & Industrial Research (CSIR) & Ministry of Ayush",
            "document_type": "TAXONOMY",
            "authority_level": 3,
            "url": "https://www.tkdl.res.in/"
        },
        "TKDL_AYURVEDIC_GLOSSARY": {
            "title": "TKDL Ayurvedic Clinical & Regulatory Glossary",
            "authority": "CSIR & Ministry of Ayush",
            "document_type": "GLOSSARY",
            "authority_level": 3,
            "url": "https://www.tkdl.res.in/"
        }
    }

    total_tax_chunks = 0
    total_tax_sections = 0

    for sid, chunk_list in chunks_by_source.items():
        meta = taxonomy_sources_meta.get(sid, {
            "title": chunk_list[0]["source_title"],
            "authority": chunk_list[0]["authority"],
            "document_type": chunk_list[0].get("document_type", "TAXONOMY"),
            "authority_level": chunk_list[0].get("authority_level", 3),
            "url": chunk_list[0].get("source_url", "https://www.tkdl.res.in/")
        })

        stmt = select(Source).where(Source.source_code == sid)
        res = await session.execute(stmt)
        source = res.scalars().first()
        if not source:
            source = Source(
                id=uuid.uuid4(),
                source_code=sid,
                title=meta["title"],
                authority=meta["authority"],
                document_type=meta["document_type"],
                jurisdiction="IN",
                authority_level=meta["authority_level"],
                current_status="ACTIVE",
                source_url=meta["url"],
                publication_date=datetime.utcnow()
            )
            session.add(source)
            await session.flush()

        stmt_v = select(SourceVersion).where(
            SourceVersion.source_id == source.id,
            SourceVersion.version_label == "1.0"
        )
        res_v = await session.execute(stmt_v)
        version = res_v.scalars().first()
        if not version:
            version = SourceVersion(
                id=uuid.uuid4(),
                source_id=source.id,
                version_label="1.0",
                effective_from=datetime(2024, 1, 1),
                storage_uri="data/corpus/csv files"
            )
            session.add(version)
            await session.flush()

        print(f" -> Embedding & indexing {len(chunk_list)} entries for {meta['title']}...")
        for c in chunk_list:
            sec_num = c["section_number"]
            heading = c["heading"]
            raw_text = c["raw_statute"]
            full_text = c["text"]

            section = SourceSection(
                id=uuid.uuid4(),
                source_version_id=version.id,
                section_number=sec_num,
                heading=heading,
                text=raw_text
            )
            session.add(section)
            await session.flush()
            total_tax_sections += 1

            embedding_vec = generate_deterministic_embedding(full_text)

            chunk = DocumentChunk(
                id=uuid.uuid4(),
                section_id=section.id,
                text=full_text,
                embedding=embedding_vec,
                token_count=len(full_text.split()),
                language="en",
                jurisdiction="IN",
                chunk_metadata={
                    "source_id": sid,
                    "source_title": meta["title"],
                    "authority": meta["authority"],
                    "authority_level": meta["authority_level"],
                    "domain": c.get("domain", "GENERAL"),
                    "section_number": sec_num,
                    "heading": heading,
                    "source_url": meta["url"],
                    "topics": c.get("topics", [])
                }
            )
            session.add(chunk)
            total_tax_chunks += 1

    await session.commit()
    print(f"[✓] Successfully embedded {total_tax_chunks} taxonomy vector records.")
    return total_tax_sections, total_tax_chunks

if __name__ == "__main__":
    asyncio.run(ingest_corpus())
