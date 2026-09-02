"""
AyuRaksha Data Module
Implements IDataModule for source manifests, verified legal documents,
and atomic chunk extraction.
"""
from typing import List, Optional
from pathlib import Path

from app.modules.interfaces import IDataModule
from app.models.domain import (
    SourceDocument,
    DocumentVersion,
    Provision,
    CorpusChunk,
    JurisdictionEnum,
    DocumentTypeEnum
)
from app.corpus.chunker import LegalDocumentChunker


class ModularDataEngine(IDataModule):
    """Production data module managing official manifests and authentic source files."""

    def __init__(self):
        self.chunker = LegalDocumentChunker()

    def get_registered_sources(self) -> List[SourceDocument]:
        manifest_sources = self.chunker.parse_manifest()
        docs = []
        for s in manifest_sources:
            jur = JurisdictionEnum.CROSS_BORDER if s.get("jurisdiction") == "CROSS_BORDER" else JurisdictionEnum(s.get("jurisdiction", "IN"))
            doc_type_raw = s.get("document_type", "ACT")
            doc_type = DocumentTypeEnum(doc_type_raw) if doc_type_raw in DocumentTypeEnum.__members__ else DocumentTypeEnum.ACT

            docs.append(
                SourceDocument(
                    source_id=s.get("source_id", "UNKNOWN"),
                    title=s.get("title", ""),
                    short_title=s.get("short_title", s.get("title", "")),
                    authority=s.get("authority", "Government Authority"),
                    jurisdiction=jur,
                    document_type=doc_type,
                    authority_level=s.get("authority_level", 5),
                    official_url=s.get("official_url"),
                    current_status="ACTIVE"
                )
            )
        return docs

    def load_document_version(self, source_id: str) -> Optional[DocumentVersion]:
        sources = self.chunker.parse_manifest()
        target = next((s for s in sources if s.get("source_id") == source_id), None)
        if not target:
            return None

        # Determine authentic hash from disk if available
        content_hash = target.get("sha256", "")
        raw_path = target.get("extracted_text_path")
        if raw_path:
            full_raw = Path(__file__).resolve().parents[4] / raw_path
            if full_raw.exists():
                content_hash = self.chunker.compute_file_sha256(full_raw)

        return DocumentVersion(
            version_id=f"VER-{source_id}-2024",
            source_id=source_id,
            version_label=target.get("short_title", "2024 Edition"),
            content_hash=content_hash,
            storage_uri=target.get("storage_uri")
        )

    def get_provisions(self, source_id: str) -> List[Provision]:
        sources = self.chunker.parse_manifest()
        target = next((s for s in sources if s.get("source_id") == source_id), None)
        if not target or not target.get("normalized_file"):
            return []

        data = self.chunker.parse_source_file(target.get("normalized_file"))
        raw_provisions = data.get("provisions", [])
        provisions = []
        for p in raw_provisions:
            provisions.append(
                Provision(
                    provision_id=p.get("provision_id", f"{source_id}_{p.get('number')}"),
                    source_id=source_id,
                    section_number=p.get("number", ""),
                    heading=p.get("heading"),
                    text=p.get("text", ""),
                    chapter=p.get("location", {}).get("chapter"),
                    statutory_significance=p.get("statutory_significance"),
                    topics=p.get("topics", [])
                )
            )
        return provisions

    def extract_chunks(self) -> List[CorpusChunk]:
        raw_chunks = self.chunker.process_all_sources()
        corpus_chunks = []
        for c in raw_chunks:
            jur = JurisdictionEnum.CROSS_BORDER if c.get("jurisdiction") == "CROSS_BORDER" else JurisdictionEnum(c.get("jurisdiction", "IN"))
            corpus_chunks.append(
                CorpusChunk(
                    chunk_id=c.get("chunk_id", "CHK-001"),
                    source_id=c.get("source_id", "UNKNOWN"),
                    section_number=c.get("section_number"),
                    text=c.get("text", ""),
                    raw_statute=c.get("raw_statute"),
                    jurisdiction=jur,
                    authority_level=c.get("authority_level", 4),
                    chunk_hash=c.get("chunk_hash") or self.chunker.compute_sha256(c.get("text", "")),
                    token_count=c.get("token_count"),
                    metadata=c
                )
            )
        return corpus_chunks


data_module = ModularDataEngine()
