import sys
import time
import asyncio

sys.path.insert(0, "backend")
from app.ai.gateway.gateway import llm_gateway

async def run_profile():
    print("--- Profiling Gateway Providers ---")
    
    t0 = time.perf_counter()
    r_gemini = await llm_gateway.gemini.generate_completion([{"role": "user", "content": "Ping"}])
    dt_gemini = time.perf_counter() - t0
    print(f"Gemini: {dt_gemini:.2f}s (Success: {bool(r_gemini)})")

    t0 = time.perf_counter()
    r_openrouter = await llm_gateway.openrouter.generate_completion([{"role": "user", "content": "Ping"}])
    dt_openrouter = time.perf_counter() - t0
    print(f"OpenRouter: {dt_openrouter:.2f}s (Success: {bool(r_openrouter)})")

    t0 = time.perf_counter()
    r_ollama = await llm_gateway.ollama.generate_completion([{"role": "user", "content": "Ping"}])
    dt_ollama = time.perf_counter() - t0
    print(f"Ollama: {dt_ollama:.2f}s (Success: {bool(r_ollama)})")

if __name__ == "__main__":
    asyncio.run(run_profile())
