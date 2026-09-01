import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum, JSON
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db.session import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_code = Column(String(128), nullable=True, unique=True, index=True)
    title = Column(String(255), nullable=False)
    authority = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False) # ACT, RULE, REGULATION, TREATY
    jurisdiction = Column(String(10), nullable=False, default="IN") # IN, INT, US, EU
    source_url = Column(String(512), nullable=True)
    publication_date = Column(DateTime, nullable=True)
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    current_status = Column(String(50), default="ACTIVE")
    content_hash = Column(String(64), nullable=True)
    authority_level = Column(Integer, default=5) # 1-5 hierarchy
    created_at = Column(DateTime, default=datetime.utcnow)

    versions = relationship("SourceVersion", back_populates="source", cascade="all, delete-orphan")

class SourceVersion(Base):
    __tablename__ = "source_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    version_label = Column(String(50), nullable=False, default="1.0")
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    content_hash = Column(String(64), nullable=True)
    storage_uri = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    source = relationship("Source", back_populates="versions")
    sections = relationship("SourceSection", back_populates="version", cascade="all, delete-orphan")

class SourceSection(Base):
    __tablename__ = "source_sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_version_id = Column(UUID(as_uuid=True), ForeignKey("source_versions.id", ondelete="CASCADE"), nullable=False)
    parent_section_id = Column(UUID(as_uuid=True), ForeignKey("source_sections.id", ondelete="SET NULL"), nullable=True)
    section_number = Column(String(50), nullable=False) # e.g. "3(p)", "Section 7"
    heading = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    page_start = Column(Integer, nullable=True)
    page_end = Column(Integer, nullable=True)

    version = relationship("SourceVersion", back_populates="sections")
    chunks = relationship("DocumentChunk", back_populates="section", cascade="all, delete-orphan")

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    section_id = Column(UUID(as_uuid=True), ForeignKey("source_sections.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=True) # sentence-transformers 384-dim
    token_count = Column(Integer, nullable=True)
    language = Column(String(10), default="en")
    jurisdiction = Column(String(10), default="IN")
    chunk_metadata = Column(JSONB, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

    section = relationship("SourceSection", back_populates="chunks")

class KnowledgeRelation(Base):
    """Traceable relationships between authoritative sources and provisions."""
    __tablename__ = "knowledge_relations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject_source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), nullable=False)
    object_source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="CASCADE"), nullable=True)
    subject_section_id = Column(UUID(as_uuid=True), ForeignKey("source_sections.id", ondelete="SET NULL"), nullable=True)
    relation_type = Column(String(80), nullable=False)  # IMPLEMENTS, AMENDS, GOVERNS, REFERENCES
    target_label = Column(String(255), nullable=True)   # Resource or IP concept when no source is the target
    jurisdiction = Column(String(10), nullable=False, default="IN")
    evidence = Column(Text, nullable=True)
    metadata_payload = Column(JSONB, default={})
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(128), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    intended_use = Column(String(100), nullable=True)
    target_market = Column(String(50), default="IN")
    created_at = Column(DateTime, default=datetime.utcnow)

    classifications = relationship("ProductClassification", back_populates="product")
    ip_assessments = relationship("IPAssessment", back_populates="product")
    abs_assessments = relationship("ABSAssessment", back_populates="product")

class ProductClassification(Base):
    __tablename__ = "product_classifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    category = Column(String(100), nullable=False)
    confidence = Column(Float, default=1.0)
    rationale = Column(Text, nullable=True)
    regulatory_act = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="classifications")

class IPAssessment(Base):
    __tablename__ = "ip_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    ip_type = Column(String(50), nullable=False) # PATENT, TRADEMARK, GI, etc.
    applicability = Column(String(50), nullable=False) # POSSIBLE, APPLICABLE, NOT_APPLICABLE
    confidence = Column(Float, default=1.0)
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="ip_assessments")

class ABSAssessment(Base):
    __tablename__ = "abs_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE"), nullable=True)
    biological_resource = Column(String(255), nullable=False)
    origin = Column(String(100), default="India")
    purpose = Column(String(100), default="commercial")
    traditional_knowledge = Column(Boolean, default=False)
    foreign_involvement = Column(Boolean, default=False)
    assessment = Column(String(50), nullable=False) # HIGH_RISK, SBB_INTIMATION, NBA_APPROVAL, EXEMPT
    confidence = Column(Float, default=1.0)
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="abs_assessments")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_id = Column(String(128), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(128), nullable=True)
    metadata_payload = Column(JSONB, default={})
    ip_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
