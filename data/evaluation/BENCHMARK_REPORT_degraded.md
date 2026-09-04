# AyuRaksha — Golden Benchmark Evaluation Report (SIH 26045)

**Pipeline Mode:** `MODE B: DEGRADED / OFFLINE DETERMINISTIC PIPELINE`  
**Executed:** 2026-09-03 21:12:31  
**Evaluated Cases:** 105 scenarios from `data/evaluation/benchmark_200.jsonl`  

---

## 🏆 Summary Scorecard

| Benchmark Metric | SIH Target | AyuRaksha Measured | Verdict |
| :--- | :---: | :---: | :---: |
| **Mean Inference Latency** | $< 1.50\text{s}$ | **2.81s** | **NEEDS OPTIMIZATION** |
| **P50 Latency (Median)** | $< 1.20\text{s}$ | **2.02s** | **WARN** |
| **P95 Latency (Tail)** | $< 3.00\text{s}$ | **6.27s** | **WARN** |
| **Jurisdiction Leakage Rate (JLR)** | $0.00\%$ | **0.00%** | **PASSED** |
| **Safe Abstention Accuracy** | $100.00\%$ | **100.00%** | **PASSED** |
| **Citation Grounding Precision** | $\ge 90.00\%$ | **100.00%** | **PASSED** |
| **Statutory Citation Recall** | $\ge 85.00\%$ | **85.88%** | **PASSED** |

---

## 🧭 Execution Modes Distribution

| Execution Mode | Count | Share | Purpose |
| :--- | :---: | :---: | :--- |
| **DIRECT_STATUTORY** | **0** | 0.0% | Ultra-fast statutory definition and provision lookup |
| **GUIDED_RAG** | **63** | 60.0% | Standard regulatory compliance evaluation (~85%) |
| **MULTI_HOP_PLANNER** | **34** | 32.4% | Cross-border and multi-pillar compliance decomposition |
| **SAFETY_ABSTENTION** | **8** | 7.6% | Non-negotiable refusal of harmful/biopiracy prompts |

---

## 🔬 Failure Taxonomy Breakdown

| Failure Category | Occurrences | Primary Responsible Pipeline Stage |
| :--- | :---: | :--- |
| **Retrieval Misses** | **21** | `composite_retrieval` (Dense vector / BM25 / Graph) |
| **Citation Grounding Failures** | **0** | `evaluation_entailment` (Directional Entailment) |
| **Safety Abstention Failures** | **0** | `guardrails` (Clinical / Evasion Classifier) |
| **Jurisdiction Contaminations** | **0** | `jurisdiction_isolation` (Cross-Border Firewall) |

---
*Generated automatically by `scripts/run_eval_benchmark.py`.*
