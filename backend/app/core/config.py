import os
from typing import List
from pathlib import Path

# Try to load dotenv if available, otherwise read directly from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    # Manual .env reader fallback
    env_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "AyuRaksha")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    
    # Neon Serverless Postgres
    NEON_PROJECT_ID: str = os.getenv("NEON_PROJECT_ID", "")
    NEON_ORG_ID: str = os.getenv("NEON_ORG_ID", "")
    NEON_BRANCH: str = os.getenv("NEON_BRANCH", "main")
    NEON_API_KEY: str = os.getenv("NEON_API_KEY", "")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DIRECT_URL: str = os.getenv("DIRECT_URL", "")
    
    # CORS
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173")
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
        
    # AI / Embedding settings
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION: int = int(os.getenv("EMBEDDING_DIMENSION", "384"))
    RERANKER_MODEL: str = os.getenv("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # OpenRouter LLM
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "google/gemma-4-31b-it:free")
    
    # Groq LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    
    # Digital India Bhashini Multilingual Service
    BHASHINI_API_KEY: str = os.getenv("BHASHINI_API_KEY", "")
    BHASHINI_USER_ID: str = os.getenv("BHASHINI_USER_ID", "")
    BHASHINI_PIPELINE_ID: str = os.getenv("BHASHINI_PIPELINE_ID", "")
    BHASHINI_INFERENCE_URL: str = os.getenv(
        "BHASHINI_INFERENCE_URL",
        "https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
    )

settings = Settings()
