import asyncio
import json
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.agents.orchestrator import AyuRakshaOrchestrator

TARGET_IDS = {
    "BENCH_031", "BENCH_035", "BENCH_038", "BENCH_041", "BENCH_050",
    "BENCH_051", "BENCH_056", "BENCH_071", "BENCH_078", "BENCH_079",
    "BENCH_091", "BENCH_092", "BENCH_094", "BENCH_097"
}

async def main():
    orch = AyuRakshaOrchestrator()
    cases = []
    with open("data/evaluation/benchmark_200.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            data = json.loads(line)
            if data["id"] in TARGET_IDS:
                cases.append(data)

    print(f"Testing {len(cases)} previously failing benchmark cases...")
    recovered = 0
    for c in cases:
        qid = c["id"]
        q = c["query"]
        jur = c.get("jurisdiction", "IN")
        req_cits = c.get("required_citations", [])
        
        t0 = time.time()
        ans = await orch.process_query(query=q, user_jurisdiction=jur)
        lat = round(time.time() - t0, 2)
        
        retrieved_sections = [
            f"{cit.section} ({cit.source_title})" for cit in (ans.citations or [])
        ]
        
        missing = []
        for req in req_cits:
            clean_req = req.lower().replace("section", "").replace("rule", "").replace("regulation", "").strip()
            found = False
            for sec_str in retrieved_sections:
                sec_lower = sec_str.lower()
                if req.lower() in sec_lower or clean_req in sec_lower:
                    found = True
                    break
            if not found:
                missing.append(req)
                
        status = "PASSED" if not missing else "FAILED"
        if not missing:
            recovered += 1
        print(f"[{qid}] {status} ({lat}s) Mode: {ans.diagnostics.get('execution_mode', getattr(ans, 'execution_mode', 'N/A'))}")
        print(f"   Expected: {req_cits}")
        if missing:
            print(f"   Missing:  {missing}")
            print(f"   Got:      {retrieved_sections[:5]}")

    print(f"\nTargeted Recovery Rate: {recovered}/{len(cases)} ({recovered/len(cases)*100:.1f}%)")

if __name__ == "__main__":
    asyncio.run(main())
