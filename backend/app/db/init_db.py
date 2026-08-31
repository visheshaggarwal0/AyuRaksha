import asyncio
import logging
from sqlalchemy import text
from app.db.session import engine, Base
import app.db.models  # Import all models to ensure they are registered with Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AyuRaksha_DB_Init")

async def init_neon_database():
    """
    Connects to Neon Postgres, activates pgvector extension, and creates all tables.
    """
    logger.info("Connecting to Neon Postgres (Project: AyuRaksha)...")
    async with engine.begin() as conn:
        logger.info("Enabling pgvector extension on Neon Postgres...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
        
        logger.info("Creating all tables in Neon Postgres...")
        await conn.run_sync(Base.metadata.create_all)
        # Keep local hackathon databases compatible without requiring a migration tool.
        await conn.execute(text("ALTER TABLE sources ADD COLUMN IF NOT EXISTS source_code VARCHAR(128);"))
        await conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_sources_source_code ON sources (source_code);"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_document_chunks_jurisdiction ON document_chunks (jurisdiction);"))
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_document_chunks_embedding_hnsw "
            "ON document_chunks USING hnsw (embedding vector_cosine_ops);"
        ))
        
    logger.info("Database initialization complete! Connected successfully to Neon.")

if __name__ == "__main__":
    asyncio.run(init_neon_database())
