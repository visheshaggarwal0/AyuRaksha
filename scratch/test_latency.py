import sys
import asyncio
sys.path.insert(0, "backend")
from app.agents.orchestrator import AyuRakshaOrchestrator

async def main():
    o = AyuRakshaOrchestrator()
    print("--- Running Query 1 ---")
    ans1 = await o.process_query("Can I patent an Ayurvedic churna combining Ashwagandha and Brahmi?")
    print("Query 1 Latency:", ans1.latency_breakdown)
    
    print("\n--- Running Query 2 ---")
    ans2 = await o.process_query("Can I patent an Ayurvedic churna combining Ashwagandha and Brahmi?")
    print("Query 2 Latency:", ans2.latency_breakdown)

if __name__ == "__main__":
    asyncio.run(main())
