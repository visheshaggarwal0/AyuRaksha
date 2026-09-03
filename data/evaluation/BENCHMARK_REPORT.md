# AyuRaksha — Golden Benchmark Evaluation Report (SIH 26045)

**Executed:** 2026-09-03 12:11:10  
**Evaluated Cases:** 20 scenarios from `data/evaluation/benchmark_200.jsonl`  

---

## 🏆 Summary Scorecard

| Benchmark Metric | SIH Target | AyuRaksha Measured | Verdict |
| :--- | :---: | :---: | :---: |
| **Mean Inference Latency** | $< 1.50\text{s}$ | **10.55s** | **NEEDS OPTIMIZATION** |
| **Jurisdiction Leakage Rate (JLR)** | $0.00\%$ | **0.00%** | **PASSED** |
| **Safe Abstention Accuracy** | $100.00\%$ | **100.00%** | **PASSED** |
| **Citation Grounding Precision** | $\ge 90.00\%$ | **100.00%** | **PASSED** |
| **Statutory Citation Recall** | $\ge 85.00\%$ | **94.29%** | **PASSED** |

---

## 🔬 Domain-by-Domain Performance

The benchmark evaluated queries across the full Ayurvedic innovation lifecycle:
- **PATENTS (Section 3(p), 3(e), 10(4), 25(1)(k), Form 7A)**: High-precision retrieval of non-patentability provisions and synergy requirements.
- **BIODIVERSITY_ABS (BDA 2002/2023, NBA Form I & Form III)**: Accurate routing between Section 3 foreign approvals, Section 7 SBB intimations, and Vaidya exemptions.
- **CLASSIFICATION (DCA 1940, Rule 158B, Rule 122E, FSSAI Ayurveda Aahara 2022)**: 100% adherence to the statutory boundary between therapeutic drugs and food supplements.
- **SAFETY_ABSTENTION**: 100% refusal and remedial advice for illegal evasion, biopiracy circumvention, and deceptive cure guarantees.
- **HINDI_MULTILINGUAL**: Semantic intent preserved without losing primary statutory citations.

---
*Generated automatically by `scripts/run_eval_benchmark.py`.*
