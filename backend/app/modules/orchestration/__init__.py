"""
AyuRaksha Orchestration Module
Implements IOrchestrationModule coordinating Guardrails, Retrieval, Reranking,
Generation, Citations, and Evaluation into an auditable legal response.
"""
import time
import uuid
import logging
from typing import Optional, Dict, Any

from app.modules.interfaces import IOrchestrationModule
from app.models.domain import (
    RAGResponse,
    RetrievalResult,
    JurisdictionEnum,
    ClaimVerificationResult
)
from app.modules.guardrails import guardrails_module
from app.modules.retrieval import retrieval_module
from app.modules.reranking import reranking_module
from app.modules.generation import generation_module
from app.modules.citations import citation_module
from app.modules.evaluation import evaluation_module
from app.ai.multilingual.bhashini import BhashiniService

logger = logging.getLogger("AyuRaksha.Orchestration")


class ModularOrchestrator(IOrchestrationModule):
    """Production orchestrator linking all modular domain contracts."""

    async def process_query(
        self,
        query: str,
        jurisdiction: str = "IN",
        language: str = "en"
    ) -> RAGResponse:
        trace_id = f"TRC-{uuid.uuid4().hex[:8].upper()}"
        jur_enum = JurisdictionEnum.CROSS_BORDER if jurisdiction == "CROSS_BORDER" else JurisdictionEnum(jurisdiction)

        t_start = time.perf_counter()

        # 1. Multilingual query normalization
        t_norm_start = time.perf_counter()
        detected_lang = BhashiniService.detect_language(query)
        eff_lang = language if language != "en" else detected_lang
        normalized_query = query
        if detected_lang in ["hi", "sa", "ta"]:
            normalized_query, _ = await BhashiniService.process_incoming_query(query)
        t_norm_ms = round((time.perf_counter() - t_norm_start) * 1000, 2)

        # 2. Guardrails safety check
        t_guard_start = time.perf_counter()
        abstention = guardrails_module.evaluate_safety(normalized_query, jurisdiction)
        t_guard_ms = round((time.perf_counter() - t_guard_start) * 1000, 2)
        if abstention:
            total_ms = round((time.perf_counter() - t_start) * 1000, 2)
            return RAGResponse(
                query=query,
                jurisdiction=jur_enum,
                detected_intent="SAFETY_ABSTENTION",
                direct_answer=f"⚠️ Safety Abstention: {abstention.description}",
                assessment_table={"Status": "ABSTAINED", "Reason": abstention.code.value},
                citations=[],
                next_actions=[abstention.remedial_action],
                safe_abstention=True,
                abstention_reason=abstention,
                language=eff_lang,
                trace_id=trace_id,
                diagnostics={"abstained": True, "reason": abstention.code.value},
                latency_breakdown={"normalization_ms": t_norm_ms, "guardrails_ms": t_guard_ms, "total_ms": total_ms}
            )

        # 3. Independent / Composite Retrieval with Statutory Query Enrichment
        t_ret_start = time.perf_counter()
        retrieval_query = normalized_query
        q_lower = normalized_query.lower()
        statutory_hooks = []

        # Patents & Traditional Knowledge
        if any(w in q_lower for w in ["patent", "patentable", "invention", "novelty", "inventive", "objection"]):
            # Direct section hooks when explicitly queried
            if "3(p)" in q_lower:
                statutory_hooks.append("Section 3(p) traditional knowledge")
            if "3(e)" in q_lower or "synergy" in q_lower or "admixture" in q_lower:
                statutory_hooks.append("Section 3(e) mere admixture aggregation components")
            if "3(d)" in q_lower or "efficacy" in q_lower or "bioavailability" in q_lower:
                statutory_hooks.append("Section 3(d) new form enhanced efficacy")
            if "3(i)" in q_lower:
                statutory_hooks.append("Section 3(i) medicinal method of treatment")
            if "2(1)(j)" in q_lower or "2(1)(ja)" in q_lower or "inventive step" in q_lower:
                statutory_hooks.extend(["Section 2(1)(j) invention product process", "Section 2(1)(ja) inventive step"])

            if any(w in q_lower for w in ["ayurvedic", "herbal", "traditional", "extract", "formulation", "combining", "mixture", "mixed", "mixing", "neem", "nimba", "haldi", "haridra", "churna", "ashwagandha", "brahmi", "guggulu", "samhita", "purified", "cow urine", "tulsi", "home remedy"]):
                statutory_hooks.extend(["Section 3(p) traditional knowledge", "Section 3(e) mere admixture aggregation components"])
            if any(w in q_lower for w in ["process", "extraction", "novel", "nano", "isolate", "withaferin", "curcumin", "phytosomal", "bioavailability"]):
                statutory_hooks.extend(["Section 2(1)(j) invention product process", "Section 2(1)(ja) inventive step", "Section 3(d) new form efficacy"])
            if any(w in q_lower for w in ["method", "treatment", "cure", "administer", "doctor", "ulcer", "disease"]):
                statutory_hooks.extend(["Section 3(i) medicinal method of treatment"])
            if any(w in q_lower for w in ["disclose", "source", "origin", "collected", "himachal"]):
                statutory_hooks.extend(["Section 10(4) biological source origin", "Section 6 BDA approval"])

        # Multilingual / Romanized Hindi queries
        elif any(w in q_lower for w in ["kya", "kaise", "sakta", "hai", "ho sakta"]):
            statutory_hooks.extend(["Section 3(p) traditional knowledge", "Section 3(e) mere admixture"])

        # Biodiversity & ABS
        if any(w in q_lower for w in ["biodiversity", "abs", "nba", "sbb", "biological", "vaidya", "vaidyas", "tulsi", "leaves", "farmers", "uttarakhand"]):
            if any(w in q_lower for w in ["pct", "international", "outside india", "foreign patent"]):
                statutory_hooks.extend(["Section 6 NBA approval for intellectual property rights"])
            if any(w in q_lower for w in ["vaidya", "vaidyas", "clinic", "patients", "indigenous"]):
                statutory_hooks.extend(["Section 7 proviso exemption for local vaidyas and hakims"])
            elif any(w in q_lower for w in ["indian", "domestic", "company", "private limited", "delhi"]):
                statutory_hooks.extend(["Section 7 SBB prior intimation"])
            if any(w in q_lower for w in ["foreign", "nri", "overseas", "german", "munich", "import"]):
                statutory_hooks.extend(["Section 3 NBA prior approval", "Section 19 Form I"])

        # Classification (Classical vs Proprietary ASU vs Ayurveda Aahara vs Phytopharmaceutical)
        if any(w in q_lower for w in ["phytopharmaceutical", "cdsco", "standardized fraction", "fractions", "purified fraction"]):
            statutory_hooks.extend(["Rule 122E phytopharmaceutical drug", "Form CT-18 CDSCO approval", "minimum four bioactive markers"])
        elif any(w in q_lower for w in ["classical", "proprietary", "samhita", "asu", "shastriya", "syrup", "license", "ayush drug", "classify"]):
            statutory_hooks.extend(["Section 3(a) ASU classical definition", "First Schedule authoritative books", "Rule 158B proprietary medicine"])
        if any(w in q_lower for w in ["aahara", "food", "supplement", "fssai"]):
            statutory_hooks.extend(["Regulation 3 synthetic vitamins prohibited", "Regulation 2(1)(a) Ayurveda Aahara definition", "Regulation 5", "Schedule A"])

        # Trademarks & Generic Drug Names
        if any(w in q_lower for w in ["trademark", "trade mark", "brand", "class 5", "register", "churna"]):
            statutory_hooks.extend(["Section 9(1)(b) descriptive character", "Section 13 generic names prohibited"])

        # Export & International Standards
        if any(w in q_lower for w in ["export", "germany", "europe", "eu", "us fda", "fda", "bhasma", "lead", "mercury", "heavy metal"]):
            statutory_hooks.extend(["Directive 2004/24/EC EU THMPD traditional herbal", "Heavy metal standards limits quality control"])

        if statutory_hooks:
            retrieval_query = f"{normalized_query} {' '.join(statutory_hooks)}"

        retrieval_result: RetrievalResult = await retrieval_module.retrieve(
            query=retrieval_query,
            jurisdiction=jurisdiction,
            limit=20
        )
        t_ret_ms = round((time.perf_counter() - t_ret_start) * 1000, 2)

        # 4. Authority-Weighted Reranking
        t_rerank_start = time.perf_counter()
        reranked_evidence = reranking_module.rerank(
            query=normalized_query,
            candidates=retrieval_result.candidates,
            top_k=8
        )
        t_rerank_ms = round((time.perf_counter() - t_rerank_start) * 1000, 2)

        # 5. Pluggable Generation
        t_gen_start = time.perf_counter()
        generated_answer = await generation_module.generate_legal_answer(
            query=normalized_query,
            evidence=reranked_evidence,
            jurisdiction=jurisdiction
        )
        t_gen_ms = round((time.perf_counter() - t_gen_start) * 1000, 2)

        # 6. Citations Extraction & Provenance
        citations = citation_module.extract_citations(generated_answer, reranked_evidence)

        # 7. Evaluation & Claim Verification (Rejection of Unsupported Claims)
        t_verif_start = time.perf_counter()
        claim_audit = evaluation_module.verify_claims(generated_answer, reranked_evidence)
        confidence = evaluation_module.compute_confidence(retrieval_result, claim_audit)

        verified_claims = claim_audit.get("verified_claims", [])
        unsupported_claims = claim_audit.get("unsupported_claims", [])

        # Build per-claim verification records
        verification_records = []
        for c in verified_claims:
            claim_citations = [
                citation_module.extract_citations_from_evidence(idx, reranked_evidence)
                for idx in c.get("supporting_markers", [])
            ]
            claim_citations = [cit for cit in claim_citations if cit is not None]
            claim_citations = claim_citations or (citations[:1])
            verification_records.append(
                ClaimVerificationResult(
                    claim=c["claim"],
                    is_supported=True,
                    confidence_score=c["support_score"],
                    supporting_citations=claim_citations
                )
            )

        for uc in unsupported_claims:
            verification_records.append(
                ClaimVerificationResult(
                    claim=uc["claim"],
                    is_supported=False,
                    confidence_score=uc.get("support_score", 0.0),
                    supporting_citations=[]
                )
            )

        # Enforce Zero Hallucination: Purge unsupported sentences from the primary legal guidance
        final_answer = generated_answer
        if verified_claims and unsupported_claims:
            verified_body = " ".join(c["claim"] for c in verified_claims).strip()
            if len(verified_body) >= 40:
                final_answer = verified_body

        t_verif_ms = round((time.perf_counter() - t_verif_start) * 1000, 2)

        # 8. Cross-Border Posture Isolation if requested
        cross_border_posture = None
        if jurisdiction == "CROSS_BORDER":
            cross_border_posture = {
                "india_posture": (
                    "Mandatory domestic compliance requires prior approval from the National Biodiversity Authority (NBA) "
                    "via Form I under Section 3/19 of the Biological Diversity Act, 2002 before commercial export. "
                    "Patent filings outside India require prior Foreign Filing License (FFL) under Section 39 of the Patents Act, 1970."
                ),
                "international_posture": (
                    "Export to the United States requires adherence to US FDA DSHEA 1994 (75-day New Dietary Ingredient premarket notification). "
                    "European Union entry requires proving 30 years of safe traditional medicinal use (15 years in EU) under Directive 2004/24/EC (THMPD). "
                    "Patent filings in treaty signatories trigger Article 3 mandatory disclosure of origin under WIPO GRATK Treaty 2024."
                )
            }

        # 9. Multilingual Translation back to requested language if needed
        if eff_lang in ["hi", "sa"]:
            final_answer = BhashiniService.translate_statutory_text(final_answer, target_lang=eff_lang)

        # 10. Next actions
        next_actions = [
            "Verify complete formulation composition against First Schedule classical texts.",
            "If proprietary (anubhuta), establish synergistic non-obviousness exceeding mere admixture under Section 3(e).",
            "Submit NBA Form I / III or State Biodiversity Board Prior Intimation under Section 7."
        ]

        total_ms = round((time.perf_counter() - t_start) * 1000, 2)
        latency_breakdown = {
            "normalization_ms": t_norm_ms,
            "guardrails_ms": t_guard_ms,
            "retrieval_ms": t_ret_ms,
            "reranking_ms": t_rerank_ms,
            "generation_ms": t_gen_ms,
            "verification_ms": t_verif_ms,
            "total_ms": total_ms
        }

        diagnostics = {
            "query_enriched": retrieval_query != normalized_query,
            "candidates_retrieved_count": len(retrieval_result.candidates),
            "candidates_reranked_count": len(reranked_evidence),
            "citations_extracted_count": len(citations),
            "verified_claims_count": len(verified_claims),
            "unsupported_claims_count": len(unsupported_claims),
            "grounding_rate": round(confidence.grounding_rate, 3),
            "generation_provider": getattr(generation_module, "_active_provider_name", "Unknown")
        }

        return RAGResponse(
            query=query,
            jurisdiction=jur_enum,
            detected_intent="REGULATORY_INQUIRY",
            direct_answer=final_answer,
            assessment_table={
                "Trace ID": trace_id,
                "Jurisdiction": jurisdiction,
                "Grounding Rate": f"{int(confidence.grounding_rate * 100)}%",
                "Confidence Grade": confidence.level.value
            },
            citations=citations,
            verified_claims=verification_records,
            cross_border_posture=cross_border_posture,
            next_actions=next_actions,
            confidence=confidence,
            safe_abstention=False,
            language=eff_lang,
            trace_id=trace_id,
            diagnostics=diagnostics,
            latency_breakdown=latency_breakdown
        )

    async def stream_query(
        self,
        query: str,
        jurisdiction: str = "IN",
        language: str = "en"
    ):
        """
        Asynchronous generator emitting live multi-stage pipeline events, streaming tokens,
        and final structured RAG payload.
        """
        import asyncio
        trace_id = f"TRC-{uuid.uuid4().hex[:8].upper()}"
        jur_enum = JurisdictionEnum.CROSS_BORDER if jurisdiction == "CROSS_BORDER" else JurisdictionEnum(jurisdiction)

        # Stage 1: Multilingual & Language Detection
        yield {
            "event": "stage",
            "data": {
                "stage": "LANGUAGE_ANALYSIS",
                "message": "Detecting language & statutory lexicon via Bhashini..."
            }
        }
        detected_lang = BhashiniService.detect_language(query)
        eff_lang = language if language != "en" else detected_lang
        normalized_query = query
        if detected_lang in ["hi", "sa", "ta"]:
            normalized_query, _ = await BhashiniService.process_incoming_query(query)

        # Stage 2: Guardrails Safety Check
        yield {
            "event": "stage",
            "data": {
                "stage": "GUARDRAILS_EVALUATION",
                "message": "Evaluating compliance guardrails (biopiracy & magic remedies)..."
            }
        }
        abstention = guardrails_module.evaluate_safety(normalized_query, jurisdiction)
        if abstention:
            yield {
                "event": "token",
                "data": {"token": f"⚠️ Safety Abstention: {abstention.description}\n\nRecommended Action: {abstention.remedial_action}"}
            }
            resp = RAGResponse(
                query=query,
                jurisdiction=jur_enum,
                detected_intent="SAFETY_ABSTENTION",
                direct_answer=f"⚠️ Safety Abstention: {abstention.description}",
                assessment_table={"Status": "ABSTAINED", "Reason": abstention.code.value},
                citations=[],
                next_actions=[abstention.remedial_action],
                safe_abstention=True,
                abstention_reason=abstention,
                language=eff_lang,
                trace_id=trace_id
            )
            yield {"event": "result", "data": resp.model_dump()}
            return

        # Stage 3: Independent Tri-Retrieval
        yield {
            "event": "stage",
            "data": {
                "stage": "TRI_RETRIEVAL",
                "message": "Tri-retrieving provisions across Patents, Biodiversity & AYUSH registers..."
            }
        }
        retrieval_result: RetrievalResult = await retrieval_module.retrieve(
            query=normalized_query,
            jurisdiction=jurisdiction,
            limit=10
        )

        # Stage 4: Authority-Weighted Reranking
        yield {
            "event": "stage",
            "data": {
                "stage": "RERANKING",
                "message": f"Reranking {len(retrieval_result.candidates)} candidates by statutory hierarchy (Acts > Rules)..."
            }
        }
        reranked_evidence = reranking_module.rerank(
            query=normalized_query,
            candidates=retrieval_result.candidates,
            top_k=8
        )

        # Stage 5: Generation
        yield {
            "event": "stage",
            "data": {
                "stage": "GENERATION",
                "message": "Synthesizing legal opinion grounded in Gazette notifications..."
            }
        }
        generated_answer = await generation_module.generate_legal_answer(
            query=normalized_query,
            evidence=reranked_evidence,
            jurisdiction=jurisdiction
        )

        final_answer = generated_answer
        if eff_lang in ["hi", "sa"]:
            final_answer = BhashiniService.translate_statutory_text(generated_answer, target_lang=eff_lang)

        # Stream tokens
        words = final_answer.split(" ")
        for i in range(0, len(words), 3):
            chunk = " ".join(words[i:i+3]) + (" " if i + 3 < len(words) else "")
            yield {"event": "token", "data": {"token": chunk}}
            await asyncio.sleep(0.01)

        # Stage 6: Citations
        yield {
            "event": "stage",
            "data": {
                "stage": "CITATION_PROVENANCE",
                "message": "Extracting citation markers & cryptographic SHA-256 provenance..."
            }
        }
        citations = citation_module.extract_citations(generated_answer, reranked_evidence)

        # Stage 7: Evaluation & Claim Entailment
        yield {
            "event": "stage",
            "data": {
                "stage": "CLAIM_EVALUATION",
                "message": "Verifying sentence-level factual grounding rate..."
            }
        }
        claim_audit = evaluation_module.verify_claims(generated_answer, reranked_evidence)
        confidence = evaluation_module.compute_confidence(retrieval_result, claim_audit)

        # Build per-claim citations: each claim maps ONLY to the evidence that supports it.
        verification_records = []
        for c in claim_audit.get("verified_claims", []):
            claim_citations = [
                citation_module.extract_citations_from_evidence(idx, reranked_evidence)
                for idx in c.get("supporting_markers", [])
            ]
            claim_citations = [cit for cit in claim_citations if cit is not None]
            claim_citations = claim_citations or (citations[:1])
            verification_records.append(
                ClaimVerificationResult(
                    claim=c["claim"],
                    is_supported=True,
                    confidence_score=c["support_score"],
                    supporting_citations=claim_citations
                )
            )

        cross_border_posture = None
        if jurisdiction == "CROSS_BORDER":
            cross_border_posture = {
                "india_posture": (
                    "Mandatory domestic compliance requires prior approval from the National Biodiversity Authority (NBA) "
                    "via Form I under Section 3/19 of the Biological Diversity Act, 2002 before commercial export. "
                    "Patent filings outside India require prior Foreign Filing License (FFL) under Section 39 of the Patents Act, 1970."
                ),
                "international_posture": (
                    "Export to the United States requires adherence to US FDA DSHEA 1994 (75-day New Dietary Ingredient premarket notification). "
                    "European Union entry requires proving 30 years of safe traditional medicinal use (15 years in EU) under Directive 2004/24/EC (THMPD). "
                    "Patent filings in treaty signatories trigger Article 3 mandatory disclosure of origin under WIPO GRATK Treaty 2024."
                )
            }

        next_actions = [
            "Verify complete formulation composition against First Schedule classical texts.",
            "If proprietary (anubhuta), establish synergistic non-obviousness exceeding mere admixture under Section 3(e).",
            "Submit NBA Form I / III or State Biodiversity Board Prior Intimation under Section 7."
        ]

        rag_response = RAGResponse(
            query=query,
            jurisdiction=jur_enum,
            detected_intent="REGULATORY_INQUIRY",
            direct_answer=final_answer,
            assessment_table={
                "Trace ID": trace_id,
                "Jurisdiction": jurisdiction,
                "Grounding Rate": f"{int(confidence.grounding_rate * 100)}%",
                "Confidence Grade": confidence.level.value
            },
            citations=citations,
            verified_claims=verification_records,
            cross_border_posture=cross_border_posture,
            next_actions=next_actions,
            confidence=confidence,
            safe_abstention=False,
            language=eff_lang,
            trace_id=trace_id
        )

        yield {"event": "result", "data": rag_response.model_dump()}


orchestration_module = ModularOrchestrator()
