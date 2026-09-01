import os
import ssl
from typing import AsyncGenerator
from sqlalchemy.orm import declarative_base

# Base class for SQLAlchemy ORM models
Base = declarative_base()

# Attempt to create async engine if asyncpg is present; otherwise provide zero-dependency stub
engine = None
AsyncSessionLocal = None

try:
    import asyncpg
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    from app.core.config import settings

    db_url = settings.DATABASE_URL
    if not db_url:
        raise RuntimeError("DATABASE_URL is not configured")
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Neon requires TLS. The default context validates both the certificate and host.
    ssl_context = ssl.create_default_context()

    engine = create_async_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "ssl": ssl_context,
            "server_settings": {"application_name": "AyuRaksha_Backend"}
        }
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
except Exception as e:
    import logging
    logging.error(f"Failed to initialize database engine: {e}")
    raise e
    AsyncSessionLocal = None

class MockSession:
    def add(self, *args, **kwargs):
        pass
    async def flush(self):
        pass
    async def execute(self, *args, **kwargs):
        return []
    async def commit(self):
        pass
    async def rollback(self):
        pass
    async def close(self):
        pass

async def get_db() -> AsyncGenerator:
    """
    Yields an active AsyncSession if asyncpg is configured, else yields a safe MockSession.
    """
    if AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    else:
        yield MockSession()
