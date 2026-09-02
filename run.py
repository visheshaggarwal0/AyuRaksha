"""
AyuRaksha Backend Runner
Convenience launcher that sets the PYTHONPATH to include backend/ automatically.
Usage: python run.py
"""
import os
import sys
import uvicorn

if __name__ == "__main__":
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    print("=" * 60)
    print("  Starting AyuRaksha (IP-SAKTI Sahayak) FastAPI Backend  ")
    print("  Port: 8000 | App Directory: backend                   ")
    print("  Docs: http://localhost:8000/docs                      ")
    print("=" * 60)

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        app_dir=backend_dir
    )
