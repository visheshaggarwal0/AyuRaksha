from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api.v1.router import api_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AyuRaksha")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} connected to Neon Postgres (Project: {settings.NEON_PROJECT_ID})...")
    # Pre-warm embedding model once on startup to eliminate query latency
    try:
        from app.modules.embeddings import embedding_module
        embedding_module._get_model()
    except Exception as e:
        logger.warning(f"Embedding model pre-warming skipped: {e}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}...")

app = FastAPI(
    title=settings.APP_NAME,
    description="A citation-grounded, jurisdiction-isolated AI IP & Regulatory Navigator for Ayurvedic Innovation",
    version="1.0.0",
    lifespan=lifespan
)

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Enable CORS for web and mobile frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Trace-ID"]
)

class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or f"REQ-{uuid.uuid4().hex[:8].upper()}"
        request.state.request_id = req_id
        response = await call_next(request)
        if "X-Request-ID" not in response.headers:
            response.headers["X-Request-ID"] = req_id
        return response

app.add_middleware(RequestCorrelationMiddleware)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["System"])
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs": "/docs",
        "api": settings.API_V1_STR
    }

@app.get("/favicon.ico", tags=["System"])
async def favicon():
    return {}

@app.get("/health", tags=["Health"])
@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database_configured": bool(settings.DATABASE_URL)
    }
