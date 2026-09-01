import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

try:
    import asyncpg
    print("asyncpg imported successfully")
except Exception as e:
    print("Failed to import asyncpg:", e)

from app.core.config import settings
print("DATABASE_URL:", settings.DATABASE_URL)

from app.db.session import engine
print("Engine is:", engine)
