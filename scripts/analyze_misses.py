import json

with open("data/evaluation/benchmark_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total scenarios: {data.get('total_scenarios_tested')}")
print(f"Statutory Recall: {data.get('statutory_citation_recall_pct')}%")
print(f"Precision: {data.get('citation_precision_pct')}%")

results = data.get("results", [])
misses = [r for r in results if r.get("missing_sections")]

print(f"\nTotal cases with missing sections: {len(misses)}")
for m in misses:
    print(f"\n[{m['id']}] Domain: {m.get('domain')} | Mode: {m.get('execution_mode')}")
    print(f"  Query: {m.get('query')}")
    print(f"  Required: {m.get('required_citations')}")
    print(f"  Missing: {m.get('missing_sections')}")
    print(f"  Retrieved count: {len(m.get('retrieved_sections', []))}")
