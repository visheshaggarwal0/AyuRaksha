# ADR-005: Cryptographic Document Provenance & Sentence-Level Citation Grounding

## Status
Accepted

## Context
In legal and regulatory AI systems, hallucinated citations or misattributed provisions have severe legal consequences. Early prototype code used synthetic mock SHA-256 strings and blindly sliced citations (`citations[:2]`), attaching citations to claims regardless of factual alignment.

## Decision
1. **Runtime File-Byte Cryptographic Hashing**: All official statutory and treaty documents stored in `data/corpus/` must have their SHA-256 digests computed directly from physical bytes on disk (`compute_file_sha256`), eliminating synthetic placeholder hashes.
2. **Sentence-to-Citation Grounding**: Answers must reference specific numbered markers (`[1]`, `[2]`). The evaluation module decomposes answers into individual sentences and verifies that each sentence is grounded in the exact cited evidence.
3. **Safe Abstention Protocol**: If an inquiry lacks verifiable statutory backing or attempts to circumvent biopiracy safeguards under the Biological Diversity Act, the system must formally abstain rather than fabricate advice.

## Rationale
- Verifiable proof of document integrity against official Gazette of India and WIPO publications.
- Establishes genuine legal accountability for SIH 26045.
- Prevents biopiracy circumvention through proactive AI guardrails.

## Consequences
- Requires continuous maintenance of raw source files in `data/corpus/` corresponding to manifest entries.
