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
    
    # asyncpg does not support query parameters (sslmode, ssl, channel_binding) in the connection string via SQLAlchemy
    if "?" in db_url:
        db_url = db_url.split("?")[0]

    # Neon requires TLS. The default context validates both the certificate and host.
    ssl_context = ssl.create_default_context()

    import sys
    from sqlalchemy.pool import NullPool

    is_testing = "pytest" in sys.modules or bool(os.environ.get("PYTEST_CURRENT_TEST"))
    pool_kwargs = {"poolclass": NullPool} if is_testing else {"pool_pre_ping": True, "pool_recycle": 300}

    engine = create_async_engine(
        db_url,
        echo=False,
        connect_args={
            "ssl": ssl_context,
            "prepared_statement_cache_size": 0,
            "statement_cache_size": 0,
            "server_settings": {"application_name": "AyuRaksha_Backend"}
        },
        **pool_kwargs
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
    logging.warning(f"Database engine offline or not configured: {e}")
    engine = None
    AsyncSessionLocal = None

class MockSession:
    def __init__(self):
        import logging
        logging.getLogger("AyuRaksha.DB").warning(
            "Database not configured — using MockSession. All DB operations are no-ops."
        )
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
