import asyncio
import uuid
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from sqlalchemy import select, func
from app.db.session import AsyncSessionLocal
from app.db.models import Source, SourceVersion, SourceSection, DocumentChunk, KnowledgeRelation
from app.corpus.chunker import LegalDocumentChunker
from app.corpus.validation import validate_normalized_document
from app.modules.embeddings import embedding_module

async def ingest_corpus():
    print("=" * 60)
    print("AyuRaksha (IP-SAKTI Sahayak) -- Provenance-Preserving Ingestion")
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

            print(f"\n -> Processing Source: {title} [{jurisdiction}]")

            source_data = chunker.parse_source_file(rel_path)
            if not source_data:
                print(f"    [warn] File not found or empty: {rel_path}")
                continue

            validation_warnings = []
            if "provisions" in source_data and "source" in source_data:
                validation_warnings = validate_normalized_document(source_data)
            for warning in validation_warnings:
                print(f"    [warning] {warning}")

            # 1. Upsert Source entity
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
                    publication_date=datetime.now()
                )
                session.add(source)
                await session.flush()
            else:
                source.title = title
                source.authority = authority
                source.source_url = official_url
                source.content_hash = sha256_hash
                source.current_status = "ACTIVE"

            # 2. Extract statutory chunks
            chunks = chunker.extract_chunks_from_source(source_data)
            if not chunks:
                print(f"    [warn] No chunks extracted for {title}")
                continue

            # 3. Check SourceVersion and existing chunks
            stmt_v = select(SourceVersion).where(
                SourceVersion.source_id == source.id,
                SourceVersion.content_hash == sha256_hash,
            )
            res_v = await session.execute(stmt_v)
            version = res_v.scalars().first()

            if version:
                stmt_c_count = select(func.count(DocumentChunk.id)).join(
                    SourceSection, DocumentChunk.section_id == SourceSection.id
                ).where(SourceSection.source_version_id == version.id)
                res_c = await session.execute(stmt_c_count)
                existing_count = res_c.scalar() or 0
                if existing_count >= len(chunks) and len(chunks) > 0:
                    print(f"    [skip] Source version already indexed ({existing_count}/{len(chunks)} chunks)")
                    continue
                else:
                    print(f"    [re-indexing] Found partial chunks ({existing_count}/{len(chunks)}), completing index...")
            else:
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

            # 4. Batch embed chunks using SentenceTransformer / ModularEmbeddingEngine
            print(f"    -> Generating dense embeddings for {len(chunks)} chunks in batch...")
            texts_to_embed = [c["text"] for c in chunks]
            embeddings = await embedding_module.embed_documents(texts_to_embed)

            for chunk_data, embedding_vec in zip(chunks, embeddings):
                sec_num = chunk_data["section_number"]
                heading = chunk_data["heading"]
                raw_text = chunk_data["raw_statute"]
                full_text = chunk_data["text"]
                location = chunk_data.get("location", {})
                section_id = uuid.uuid4()

                # Create section
                section = SourceSection(
                    id=section_id,
                    source_version_id=version.id,
                    section_number=sec_num,
                    heading=heading,
                    text=raw_text,
                    page_start=location.get("page_start"),
                    page_end=location.get("page_end")
                )
                session.add(section)
                total_sections_inserted += 1

                # Create document chunk
                chunk = DocumentChunk(
                    id=uuid.uuid4(),
                    section_id=section_id,
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

            # 5. Insert Knowledge Relations
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
            print(f"    [OK] Committed {len(chunks)} statutory chunks for {title}")

        # Ingest and embed CSV taxonomy records
        tax_sections, tax_chunks = await ingest_taxonomy_csvs(session, chunker)
        total_sections_inserted += tax_sections
        total_chunks_inserted += tax_chunks

    print("\n" + "=" * 60)
    print(f"[OK] Provenance Ingestion Complete!")
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
                publication_date=datetime.now()
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

        stmt_c_count = select(func.count(DocumentChunk.id)).join(
            SourceSection, DocumentChunk.section_id == SourceSection.id
        ).where(SourceSection.source_version_id == version.id)
        res_c = await session.execute(stmt_c_count)
        existing_count = res_c.scalar() or 0
        if existing_count >= len(chunk_list) and len(chunk_list) > 0:
            print(f"    [skip] {existing_count} taxonomy chunks already indexed for {meta['title']}")
            continue

        print(f" -> Generating embeddings & indexing {len(chunk_list)} entries for {meta['title']} in batch...")
        texts_to_embed = [c["text"] for c in chunk_list]
        embeddings = await embedding_module.embed_documents(texts_to_embed)

        for c, embedding_vec in zip(chunk_list, embeddings):
            sec_num = c["section_number"]
            heading = c["heading"]
            raw_text = c["raw_statute"]
            full_text = c["text"]
            sec_id = uuid.uuid4()

            section = SourceSection(
                id=sec_id,
                source_version_id=version.id,
                section_number=sec_num,
                heading=heading,
                text=raw_text
            )
            session.add(section)
            total_tax_sections += 1

            chunk = DocumentChunk(
                id=uuid.uuid4(),
                section_id=sec_id,
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
        print(f"    [OK] Committed {len(chunk_list)} taxonomy vector records for {meta['title']}.")

    print(f"[OK] Successfully processed {total_tax_chunks} taxonomy vector records.")
    return total_tax_sections, total_tax_chunks


if __name__ == "__main__":
    asyncio.run(ingest_corpus())
