import logging
import uuid
from typing import Dict, Any, Optional, List
from app.ai.routing.normalizer import QueryNormalizer
from app.ai.routing.router import JurisdictionIntentRouter
from app.ai.extraction.entity_extractor import EntityExtractor
from app.ai.retrieval.planner import RetrievalPlanner
from app.ai.retrieval.hybrid import HybridRetriever
from app.ai.guardrails.abstention import AbstentionGate
from app.ai.gateway.gateway import llm_gateway
from app.ai.verification.verifier import SentenceClaimVerifier
from app.ai.verification.confidence import ConfidenceCalibrator
from app.ai.multilingual.bhashini import BhashiniService

logger = logging.getLogger("AyuRaksha.AIPipeline")

class AyuRakshaAIPipeline:
    """
    Production 11-Stage AI Pipeline for AyuRaksha (SIH 26045):
    1. Multilingual Query Routing & Bhashini Translation
    2. Query Normalization
    3. Intent Classification & Jurisdiction Boundary Enforcement
    4. Regulatory & Botanical Entity Extraction
    5. Retrieval Planning
    6. Hybrid Retrieval (Vector + Full-Text + Graph)
    7. Candidate Fusion & Legal Authority Reranking
    8. Evidence Sufficiency & Statutory Safety Gate
    9. Context Assembly
    10. Multi-Provider LLM Synthesis (Gemini / Groq / OpenRouter / Ollama)
    11. Sentence-Level Claim & Citation Entailment Verification
    12. Calibrated Confidence & Dual-Pane Cross-Border Posture Synthesis
    """

    def __init__(self):
        self.retriever = HybridRetriever()

    async def execute(
        self,
        query: str,
        jurisdiction: str = "IN",
        language: str = "en"
    ) -> Dict[str, Any]:
        pipeline_trace_id = str(uuid.uuid4())

        # Stage 0: Multilingual Ingestion & Translation via Bhashini
        search_query, detected_lang = await BhashiniService.process_incoming_query(query, user_lang=language)
        target_language = language if language != "en" else detected_lang

        # Stage 1: Query Normalization
        norm_result = QueryNormalizer.process(search_query)
        normalized_query = norm_result["normalized_query"]

        # Stage 2: Intent & Jurisdiction Isolation
        route = JurisdictionIntentRouter.route(normalized_query, requested_jurisdiction=jurisdiction)
        effective_jurisdiction = route["jurisdiction"]

        # Stage 3: Entity Extraction
        entities = EntityExtractor.extract_entities(normalized_query)

        # Stage 4: Retrieval Planning
        plan = RetrievalPlanner.plan(normalized_query, route, entities)

        # Stage 5 & 6: Hybrid Retrieval & Legal Reranking
        candidates = await self.retriever.retrieve(normalized_query, plan, top_k=5)

        # Stage 7: Evidence Sufficiency Gate & Statutory Safety Check
        abstention = AbstentionGate.evaluate(normalized_query, candidates, route)
        if abstention["should_abstain"]:
            return self._build_abstention_response(
                query=query,
                abstention=abstention,
                route=route,
                candidates=candidates,
                trace_id=pipeline_trace_id,
                language=target_language
            )

        # Stage 8: Context Assembly
        statutory_context_blocks = []
        taxonomy_context_blocks = []

        for idx, s in enumerate(candidates):
            marker = f"[{idx + 1}]"
            source_title = s.get("source_title", "Authoritative Source")
            section_num = s.get("section_number", "")
            raw_text = s.get("raw_statute") or s.get("text") or ""
            block = f"{marker} Source: {source_title} ({section_num})\nStatutory / Reference Content: {raw_text}"

            if s.get("authority_level", 3) >= 4 and s.get("domain") not in ["BOTANICAL_TAXONOMY", "GLOSSARY"]:
                statutory_context_blocks.append(block)
            else:
                taxonomy_context_blocks.append(block)

        full_context = ""
        if statutory_context_blocks:
            full_context += "=== PRIMARY STATUTORY PROVISIONS ===\n" + "\n\n".join(statutory_context_blocks) + "\n\n"
        if taxonomy_context_blocks:
            full_context += "=== BOTANICAL & TRADITIONAL KNOWLEDGE CONTEXT ===\n" + "\n\n".join(taxonomy_context_blocks)

        # Stage 9: Multi-Provider LLM Synthesis
        system_prompt = (
            "You are AyuRaksha (IP-SAKTI Sahayak), an authoritative AI regulatory navigator for Ayurvedic innovation "
            "under the Ministry of Ayush. Answer using ONLY the provided verified statutory context. "
            "Be descriptive, precise, and supportive. Structure your answer in logical paragraphs. "
            "At the end of every claim or paragraph, add numerical citation markers like [1], [2] corresponding strictly to the provided sources. "
            "NEVER hallucinate non-existent sections, rules, or treaties. "
            "Always maintain strict jurisdiction awareness: do not conflate Indian domestic law with international regimes."
        )
        user_prompt = f"User Question: {query}\n\nVerified Context:\n{full_context}\n\nProvide an evidence-grounded regulatory response with inline [1] citation markers:"

        generated_answer = await llm_gateway.generate_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1
        )

        # Stage 10: Sentence-Level Claim & Citation Entailment Verification
        verification = SentenceClaimVerifier.verify(generated_answer, candidates)

        # Stage 11: Calibrated Confidence & Caveats
        calibration = ConfidenceCalibrator.calibrate(route, candidates, verification)

        # Build Formatted Citations
        citations = []
        for idx, c in enumerate(candidates):
            citations.append({
                "citation_id": f"CIT-{idx + 1:03d}",
                "source_id": c.get("source_id", "UNKNOWN"),
                "source_title": c.get("source_title", "Statutory Source"),
                "section": c.get("section_number", ""),
                "authority": c.get("authority", "Statutory Authority"),
                "authority_level": c.get("authority_level", 4),
                "verbatim_quote": c.get("raw_statute") or c.get("text", "")[:280],
                "official_url": c.get("source_url") or c.get("official_url", "https://ayush.gov.in"),
                "document_sha256": c.get("source_sha256") or c.get("chunk_hash", ""),
                "relevance_score": c.get("calibrated_score", 0.5)
            })

        # Synthesize Next Actions based on Intent
        next_actions = self._determine_next_actions(route, entities)

        # Stage 12: Dual-Pane Cross-Border Isolation (Task 4)
        cross_border_posture = None
        if effective_jurisdiction == "CROSS_BORDER":
            cross_border_posture = self._build_cross_border_posture(route, entities)

        # Stage 13: Bhashini Output Translation if non-English requested
        final_answer = generated_answer
        final_actions = next_actions
        if target_language != "en":
            final_answer = BhashiniService.translate_statutory_text(generated_answer, target_language)
            final_actions = [BhashiniService.translate_statutory_text(a, target_language) for a in next_actions]
            if cross_border_posture:
                cross_border_posture = {
                    "india_posture": BhashiniService.translate_statutory_text(cross_border_posture["india_posture"], target_language),
                    "international_posture": BhashiniService.translate_statutory_text(cross_border_posture["international_posture"], target_language)
                }

        return {
            "query": query,
            "detected_intent": route["intent"],
            "jurisdiction": effective_jurisdiction,
            "detected_language": target_language,
            "direct_answer": final_answer,
            "confidence_score": calibration["confidence_score"],
            "confidence_level": calibration["confidence_level"],
            "citations": citations,
            "next_actions": final_actions,
            "cross_border_posture": cross_border_posture,
            "caveats": calibration["caveats"],
            "disclaimer": "Statutory Disclaimer: AyuRaksha provides AI-assisted regulatory and IP guidance based on indexed legislation. It does not constitute formal legal representation. Verify with SLA or patent counsel before commercial filing.",
            "pipeline_metadata": {
                "trace_id": pipeline_trace_id,
                "active_llm_provider": llm_gateway.active_provider_name,
                "entities_detected": entities,
                "target_language": target_language,
                "grounding_rate": verification["grounding_rate"],
                "claims_verified_count": verification["verified_claims_count"],
                "verification_status": verification["status"]
            }
        }

    def _build_cross_border_posture(self, route: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, str]:
        """
        Builds visibly separated domestic vs destination market postures
        to ensure legal requirements are never conflated (SIH 26045 mandate).
        """
        botanicals = entities.get("botanicals", [])
        botanical_names = ", ".join([b.get("scientific_name", "") for b in botanicals[:2]]) if botanicals else "Indian biological material"

        india_posture = (
            f"**🇮🇳 India Domestic Regulatory & IP Posture:**\n"
            f"1. **Biological Diversity Act, 2002 (Section 3 & 19):** Accessing {botanical_names} for export or foreign entity utilization requires mandatory prior approval from the National Biodiversity Authority (NBA) on Form I.\n"
            f"2. **Patents Act, 1970 (Section 39):** Mandatory Foreign Filing License (FFL) must be obtained from the Controller of Patents if filing abroad before filing in India, or wait 6 weeks after Indian filing.\n"
            f"3. **Ayush Export Clearance:** Requires Certificate of Pharmaceutical Product (CoPP) or WHO-GMP certification from State Licensing Authority (SLA) under Rule 158B."
        )

        international_posture = (
            f"**🌐 International Destination Market Posture:**\n"
            f"1. **WIPO GRATK Treaty (2024, Article 3):** Mandatory statutory disclosure of Country of Origin (India) and traditional knowledge origin in all PCT and international patent offices.\n"
            f"2. **United States (FDA / DSHEA 1994):** Marketed as Dietary Supplement. Requires New Dietary Ingredient (NDI) 75-day notification under 21 CFR 190.6 if herb was not marketed in US prior to Oct 15, 1994. Strict prohibition against disease treatment claims.\n"
            f"3. **European Union (EMA / THMPD Directive 2004/24/EC):** Traditional Herbal Medicinal Products registration requires documented proof of 30-year medicinal use (with at least 15 years within the EU)."
        )

        return {
            "india_posture": india_posture,
            "international_posture": international_posture
        }

    def _determine_next_actions(self, route: Dict[str, Any], entities: Dict[str, Any]) -> List[str]:
        intent = route.get("intent")
        actions = []
        if intent == "PATENTABILITY_ASSESSMENT":
            actions.extend([
                "Perform TKDL First Schedule prior art clearance",
                "Conduct comparative experimental synergy studies under Section 3(e)",
                "Submit NBA Form III prior approval before patent grant if Indian herbs are claimed"
            ])
        elif intent == "ABS_ASSESSMENT":
            actions.extend([
                "Identify sourcing state and file SBB Form 1 prior intimation (domestic)",
                "Verify whether any ingredients are classified as Normally Traded Commodities under Section 40",
                "If exporting or foreign entity, apply for NBA Form I approval"
            ])
        elif intent == "PRODUCT_CLASSIFICATION":
            actions.extend([
                "Verify recipe in Drugs & Cosmetics Act First Schedule classical texts",
                "Apply for Rule 158B licensing if proprietary ASU formulation",
                "Comply with FSSAI Ayurveda Aahara 2022 logo & disclaimer requirements if marketed as dietary supplement"
            ])
        else:
            actions.append("Consult the Ayush State Licensing Authority (SLA) for statutory clearance")
        return actions

    def _build_abstention_response(
        self,
        query: str,
        abstention: Dict[str, Any],
        route: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        trace_id: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        explanation = abstention["explanation"]
        if language != "en":
            explanation = BhashiniService.translate_statutory_text(explanation, language)

        return {
            "query": query,
            "detected_intent": route["intent"],
            "jurisdiction": route["jurisdiction"],
            "detected_language": language,
            "direct_answer": f"**AyuRaksha Regulatory Abstention Notice**\n\n{explanation}",
            "confidence_score": 0.0,
            "confidence_level": "LOW",
            "citations": [],
            "next_actions": abstention.get("facilitator_brief", {}).get("recommended_next_steps", []),
            "cross_border_posture": None,
            "caveats": [f"Reason: {abstention['reason_code']}"],
            "disclaimer": "Statutory Notice: The system abstains from generating legal hypotheses when statutory support is insufficient or circumvention is attempted.",
            "pipeline_metadata": {
                "trace_id": trace_id,
                "abstained": True,
                "abstention_code": abstention["reason_code"],
                "facilitator_brief": abstention["facilitator_brief"]
            }
        }

# Global singleton pipeline instance
ai_pipeline = AyuRakshaAIPipeline()
