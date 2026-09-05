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
    logger.info(f"Starting {settings.APP_NAME}...")
    # Defer heavy model loading to keep startup memory < 100MB and ensure instant port binding
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
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Trace-ID"]
)

class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or f"REQ-{uuid.uuid4().hex[:8].upper()}"
        request.state.request_id = req_id
        import asyncio
        try:
            response = await asyncio.wait_for(call_next(request), timeout=120.0)
        except asyncio.TimeoutError:
            from starlette.responses import JSONResponse
            return JSONResponse({"error": "Request timeout"}, status_code=504)
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
    db_configured = bool(settings.DATABASE_URL)
    db_reachable = False
    if db_configured:
        try:
            from app.db.session import get_engine
            from sqlalchemy import text
            engine = get_engine()
            if engine:
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                db_reachable = True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database_configured": db_configured,
        "database_reachable": db_reachable
    }
