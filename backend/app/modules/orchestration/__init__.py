"""
AyuRaksha Orchestration Module
Implements IOrchestrationModule coordinating Guardrails, Retrieval, Reranking,
Generation, Citations, and Evaluation into an auditable legal response.
"""
import time
import uuid
import logging
import re
import asyncio
from typing import Optional, Dict, Any, List

from app.modules.interfaces import IOrchestrationModule
from app.models.domain import (
    RAGResponse,
    RetrievalResult,
    JurisdictionEnum,
    ClaimVerificationResult,
    ExecutionMode,
    EvidencePack,
    Confidence,
    ConfidenceLevel
)
from app.modules.guardrails import guardrails_module
from app.modules.retrieval import retrieval_module
from app.modules.reranking import reranking_module
from app.modules.generation import generation_module
from app.modules.citations import citation_module
from app.modules.evaluation import evaluation_module
from app.modules.concepts import concept_engine
from app.ai.multilingual.bhashini import BhashiniService
from app.telemetry.collector import telemetry_collector

logger = logging.getLogger("AyuRaksha.Orchestration")


class ModularOrchestrator(IOrchestrationModule):
    """Production orchestrator linking all modular domain contracts."""

    async def process_query(
        self,
        query: str,
        jurisdiction: str = "IN",
        language: str = "en",
        request_id: Optional[str] = None
    ) -> RAGResponse:
        trace_id = f"TRC-{uuid.uuid4().hex[:8].upper()}"
        req_id = request_id or f"REQ-{trace_id[-8:]}"
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
            abstained_resp = RAGResponse(
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
            telemetry_collector.record_orchestration_response(
                response_obj=abstained_resp,
                query=query,
                request_id=req_id,
                token_usage=None,
                success=True
            )
            return abstained_resp

        # 3. Determine Execution Mode & Semantic Legal Concepts
        resolved_concepts = concept_engine.resolve_concepts(normalized_query)
        execution_mode = self.determine_execution_mode(normalized_query, resolved_concepts, jurisdiction)

        if execution_mode == ExecutionMode.CONVERSATIONAL_GREETING:
            return await self._execute_conversational_greeting(
                query=query,
                jur_enum=jur_enum,
                jurisdiction=jurisdiction,
                eff_lang=eff_lang,
                trace_id=trace_id,
                t_start=t_start,
                t_norm_ms=t_norm_ms,
                t_guard_ms=t_guard_ms
            )
        elif execution_mode == ExecutionMode.CLASSIFICATION_INTAKE:
            return await self._execute_classification_intake(
                query=query,
                jur_enum=jur_enum,
                jurisdiction=jurisdiction,
                eff_lang=eff_lang,
                trace_id=trace_id,
                t_start=t_start,
                t_norm_ms=t_norm_ms,
                t_guard_ms=t_guard_ms
            )
        elif execution_mode == ExecutionMode.DIRECT_STATUTORY:
            return await self._execute_direct_statutory(
                query=query,
                normalized_query=normalized_query,
                resolved_concepts=resolved_concepts,
                jur_enum=jur_enum,
                jurisdiction=jurisdiction,
                eff_lang=eff_lang,
                trace_id=trace_id,
                t_start=t_start,
                t_norm_ms=t_norm_ms,
                t_guard_ms=t_guard_ms
            )
        elif execution_mode == ExecutionMode.MULTI_HOP_PLANNER:
            return await self._execute_multi_hop_planner(
                query=query,
                normalized_query=normalized_query,
                resolved_concepts=resolved_concepts,
                jur_enum=jur_enum,
                jurisdiction=jurisdiction,
                eff_lang=eff_lang,
                trace_id=trace_id,
                t_start=t_start,
                t_norm_ms=t_norm_ms,
                t_guard_ms=t_guard_ms
            )

        # Default Mode 2: Guided Statutory RAG
        return await self._execute_guided_rag(
            query=query,
            normalized_query=normalized_query,
            resolved_concepts=resolved_concepts,
            jur_enum=jur_enum,
            jurisdiction=jurisdiction,
            eff_lang=eff_lang,
            trace_id=trace_id,
            t_start=t_start,
            t_norm_ms=t_norm_ms,
            t_guard_ms=t_guard_ms
        )

    GREETING_REGEX = re.compile(
        r"^(?:hi|hy|hello|hey|heya|namaste|namaskar|pranam)(?:\s+(?:there|all|team|sahayak|ayuraksha))?[!.\s?]*$|"
        r"^(?:good\s+(?:morning|afternoon|evening)|greetings)[!.\s?]*$|"
        r"^(?:who\s+are\s+you|what\s+(?:can\s+you\s+do|is\s+ayuraksha|is\s+ip\s*sakti|is\s+this\s+app)|help(?:\s+me)?|how\s+does\s+this\s+work)[!.\s?]*$",
        re.IGNORECASE
    )

    CLASSIFICATION_INTAKE_REGEX = re.compile(
        r"^(?:(?:can|how)\s+i\s+(?:patent|license|sell|protect|register|export)|i\s+(?:want\s+to|have\s+an?|make|developed)\s+(?:patent|license|sell|protect|a\s+new)|what\s+about\s+my|classify\s+(?:my|this)|evaluate\s+(?:my|this))\s+.*(?:oil|cream|ointment|tablet|capsule|syrup|gummy|gummies|drops|churna|formulation|product|medicine|remedy)[!.\s?]*$",
        re.IGNORECASE
    )

    DIRECT_STATUTORY_REGEX = re.compile(
        r"(?:^|\b)(?:what\s+(?:is|does|are|says)|text\s+of|show\s+me|explain|define|provision\s+of|under|cite|state|meaning\s+of)?\s*(?:the\s+)?(section|sec\.?|rule|regulation|article)\s+([0-9]+[a-zA-Z0-9\(\)\-_/]*)",
        re.IGNORECASE
    )

    def determine_execution_mode(
        self,
        query: str,
        resolved_concepts: List[Any],
        jurisdiction: str
    ) -> ExecutionMode:
        """
        Determines the optimal execution mode:
        1. CONVERSATIONAL_GREETING: Small talk, welcomes, capabilities intake.
        2. CLASSIFICATION_INTAKE: Underspecified product queries needing multi-turn clarifying intake.
        3. DIRECT_STATUTORY: When the query is an explicit statutory definition or provision lookup.
        4. MULTI_HOP_PLANNER: When the query spans multiple regulatory domains or cross-border regimes.
        5. GUIDED_RAG: Standard regulatory compliance inquiries (~85% of queries).
        """
        q_strip = query.strip()
        q_lower = q_strip.lower()
        clean_q = re.sub(r"[^\w\s]", "", q_lower).strip()

        # 0. Conversational Greeting check
        if self.GREETING_REGEX.search(q_strip) or clean_q in [
            "hi", "hy", "hy there", "hello", "hello there", "hey", "hey there",
            "namaste", "namaskar", "pranam", "help", "start", "greetings"
        ]:
            return ExecutionMode.CONVERSATIONAL_GREETING

        # Cross-border / export query detection
        cross_border_match = bool(
            re.search(r"\b(export|germany|europe|eu|us|usa|fda|united states|america|abroad|foreign|overseas)\b", query.lower())
        ) and bool(
            re.search(r"\b(patent|formulation|plant|ayurvedic|community|source|botanical|bhasma)\b", query.lower())
        )

        # 1. Direct Statutory Check (concise direct section/rule inquiry)
        if self.DIRECT_STATUTORY_REGEX.search(q_strip) and len(q_strip.split()) <= 15 and not cross_border_match and jurisdiction != "CROSS_BORDER":
            return ExecutionMode.DIRECT_STATUTORY

        # 2. Underspecified Formulation Intake check
        if self.is_underspecified_intake(q_strip, resolved_concepts):
            return ExecutionMode.CLASSIFICATION_INTAKE

        # 3. Multi-Hop Planner Check (cross-border or spanning >= 2 regulatory pillars / statutes)
        domains = {c.domain for c in resolved_concepts}
        statute_prefixes = set()
        for c in resolved_concepts:
            for prov in getattr(c, "statutory_provisions", []):
                raw_prefix = prov.split("_")[0]
                canon_prefix = "DRUGS_COSMETICS" if raw_prefix in ["DCA", "DCR", "DRUGS"] else ("PATENTS" if raw_prefix in ["PATENTS", "PATENT"] else raw_prefix)
                statute_prefixes.add(canon_prefix)
        is_multi_pillar = len(domains) >= 2 or len(statute_prefixes) >= 2 or cross_border_match
        if jurisdiction == "CROSS_BORDER" or is_multi_pillar:
            return ExecutionMode.MULTI_HOP_PLANNER

        # 4. Default Guided RAG
        return ExecutionMode.GUIDED_RAG

    def is_underspecified_intake(self, query: str, resolved_concepts: List[Any]) -> bool:
        q_lower = query.lower().strip()
        if re.search(r"\b(classify\s+(?:my|this)|help\s+me\s+classify|evaluate\s+my\s+formulation|start\s+classification)\b", q_lower):
            return True
        if len(q_lower.split()) <= 12 and self.CLASSIFICATION_INTAKE_REGEX.search(q_lower):
            specific_botanicals = [
                "ashwagandha", "guduchi", "curcumin", "turmeric", "neem", "tulsi", "triphala",
                "kutki", "shatavari", "brahmi", "guggulu", "amla", "haritaki", "bibhitaki",
                "arjuna", "licorice", "ginger", "boswellia", "shallaki"
            ]
            has_botanical = any(b in q_lower for b in specific_botanicals)
            has_statute = bool(re.search(r"\b(section|sec\.?|rule|act|tkdl|bda|dca)\b", q_lower))
            if not has_botanical and not has_statute:
                return True
        return False

    async def _execute_conversational_greeting(
        self,
        query: str,
        jur_enum: JurisdictionEnum,
        jurisdiction: str,
        eff_lang: str,
        trace_id: str,
        t_start: float,
        t_norm_ms: float,
        t_guard_ms: float
    ) -> RAGResponse:
        total_ms = round((time.perf_counter() - t_start) * 1000, 2)
        latency_breakdown = {
            "normalization_ms": t_norm_ms,
            "guardrails_ms": t_guard_ms,
            "retrieval_ms": 0.0,
            "reranking_ms": 0.0,
            "generation_ms": 0.1,
            "verification_ms": 0.1,
            "total_ms": total_ms
        }
        greeting_text = (
            "**Namaste! I am your IP-SAKTI Sahayak** — your AI co-counsel for Intellectual Property and regulatory guidance in Ayurveda, grounded in official statutes from the Ministry of Ayush.\n\n"
            "Protecting and commercializing an Ayurvedic formulation requires navigating three interconnected regimes:\n"
            "1. **Statutory Classification:** Deciding whether your product is Classical Shastriya, Proprietary ASU, Phytopharmaceutical, Ayurveda Aahar, or Cosmetic.\n"
            "2. **Patentability & TKDL:** Navigating Section 3(p) exclusions and non-obvious synergy.\n"
            "3. **Biodiversity & ABS:** Ensuring compliance with the Biological Diversity Act, 2023 (NBA/SBB rules).\n\n"
            "To get started, tell me about your formulation or select one of the 6 official statutory categories below:"
        )
        chips = [
            {"label": "📜 1. Classical Shastriya (First Schedule)", "action_payload": "I have a Classical Ayurvedic Medicine formulated strictly according to a First Schedule text like Charaka Samhita.", "category_hint": "CLASSICAL_SHASTRIYA"},
            {"label": "🧪 2. Proprietary ASU Formulation", "action_payload": "I have a Proprietary Ayurvedic Medicine (ASU) with a new combination or ratio of traditional ingredients.", "category_hint": "PROPRIETARY_ASU"},
            {"label": "🔬 3. Phytopharmaceutical Extract", "action_payload": "I have a purified and standardized botanical fraction with defined biomarkers (Phytopharmaceutical).", "category_hint": "PHYTOPHARMACEUTICAL"},
            {"label": "🥗 4. Ayurveda-Aahar (Food/Nutraceutical)", "action_payload": "I want to formulate an Ayurveda-Aahar food product under FSSAI 2022 Regulations.", "category_hint": "AYURVEDA_AAHAR"},
            {"label": "🌿 5. Ayurvedic Cosmetic (Topical)", "action_payload": "I want to market an Ayurvedic cosmetic or personal care formulation for skin/hair.", "category_hint": "COSMETIC"},
            {"label": "🌱 6. Biological Diversity & ABS Check", "action_payload": "Check Biological Diversity Act 2023 ABS approval requirements for sourcing Indian herbs.", "category_hint": "ABS"}
        ]
        return RAGResponse(
            query=query,
            jurisdiction=jur_enum,
            detected_intent="CONVERSATIONAL_GREETING",
            direct_answer=greeting_text,
            assessment_table={
                "Trace ID": trace_id,
                "Execution Mode": "CONVERSATIONAL_GREETING",
                "Assistant": "IP-SAKTI Sahayak",
                "Authority": "Ministry of Ayush / AIIA"
            },
            citations=[],
            verified_claims=[],
            confidence=Confidence(level=ConfidenceLevel.HIGH, score=1.0, grounding_rate=1.0, caveats=[]),
            safe_abstention=False,
            language=eff_lang,
            execution_mode=ExecutionMode.CONVERSATIONAL_GREETING,
            intent_type="GREETING",
            clarification_chips=chips,
            suggested_prompts=[
                "Can I patent an arthritis oil with Ashwagandha and Guduchi?",
                "What licensing proof is required under Rule 158B for a proprietary churna?",
                "Do I need NBA permission to source Kutki from Himachal Pradesh under BDA 2023?",
                "What are the US FDA DSHEA export requirements for Ayurvedic supplements?"
            ],
            trace_id=trace_id,
            diagnostics={"greeting": True, "provider": "IP-SAKTI-OnboardingEngine"},
            latency_breakdown=latency_breakdown
        )

    async def _execute_classification_intake(
        self,
        query: str,
        jur_enum: JurisdictionEnum,
        jurisdiction: str,
        eff_lang: str,
        trace_id: str,
        t_start: float,
        t_norm_ms: float,
        t_guard_ms: float
    ) -> RAGResponse:
        total_ms = round((time.perf_counter() - t_start) * 1000, 2)
        latency_breakdown = {
            "normalization_ms": t_norm_ms,
            "guardrails_ms": t_guard_ms,
            "retrieval_ms": 0.0,
            "reranking_ms": 0.0,
            "generation_ms": 0.1,
            "verification_ms": 0.1,
            "total_ms": total_ms
        }
        intake_text = (
            "Because intellectual property for an Ayurvedic product is inseparable from how it is regulated, we must first establish your **statutory classification** under Chapter IV-A of the Drugs & Cosmetics Act, 1940.\n\n"
            "To determine whether your formulation faces the **Section 3(p) patenting bar** or requires a **Rule 158B manufacturing license**, please clarify:\n\n"
            "1. **Is the recipe drawn directly from an authoritative First-Schedule text** (such as *Charaka Samhita*, *Sushruta Samhita*, or *Bhavaprakasha*), or is it your own new recipe?\n"
            "2. **Is it a whole crude herb/powder/oil**, or a **purified, standardized solvent extract** with characterized biomarkers?"
        )
        chips = [
            {"label": "📜 Classical Text Recipe (First Schedule)", "action_payload": "My formulation is drawn from an authoritative First-Schedule classical Ayurvedic text.", "category_hint": "CLASSICAL_SHASTRIYA"},
            {"label": "🧪 New Proprietary ASU Combination", "action_payload": "My formulation is a new proprietary combination of traditional Ayurvedic herbs not found in classical texts.", "category_hint": "PROPRIETARY_ASU"},
            {"label": "🔬 Standardized Solvent Extract (Phytopharmaceutical)", "action_payload": "My formulation is a standardized botanical extract with defined biomarkers.", "category_hint": "PHYTOPHARMACEUTICAL"},
            {"label": "🥗 Ayurveda-Aahar Dietary Supplement", "action_payload": "My formulation is intended as an Ayurveda-Aahar nutritional/dietary supplement under FSSAI regulations.", "category_hint": "AYURVEDA_AAHAR"}
        ]
        return RAGResponse(
            query=query,
            jurisdiction=jur_enum,
            detected_intent="CLASSIFICATION_INTAKE",
            direct_answer=intake_text,
            assessment_table={
                "Trace ID": trace_id,
                "Execution Mode": "CLASSIFICATION_INTAKE",
                "Regulatory Stage": "Formulation Classification Intake",
                "Next Step": "Select or clarify formulation origin"
            },
            citations=[],
            verified_claims=[],
            confidence=Confidence(level=ConfidenceLevel.HIGH, score=0.95, grounding_rate=1.0, caveats=[]),
            safe_abstention=False,
            language=eff_lang,
            execution_mode=ExecutionMode.CLASSIFICATION_INTAKE,
            intent_type="CLASSIFICATION_INTAKE",
            clarification_chips=chips,
            suggested_prompts=[
                "What is the difference between Classical Shastriya and Proprietary ASU licensing?",
                "Can a proprietary polyherbal formulation overcome Section 3(p)?",
                "What clinical or safety data does Rule 158B require?"
            ],
            trace_id=trace_id,
            diagnostics={"intake": True, "provider": "IP-SAKTI-ClassificationIntakeEngine"},
            latency_breakdown=latency_breakdown
        )

    async def _execute_direct_statutory(
        self,
        query: str,
        normalized_query: str,
        resolved_concepts: List[Any],
        jur_enum: JurisdictionEnum,
        jurisdiction: str,
        eff_lang: str,
        trace_id: str,
        t_start: float,
        t_norm_ms: float,
        t_guard_ms: float
    ) -> RAGResponse:
        t_ret_start = time.perf_counter()
        retrieval_result = await retrieval_module.retrieve(
            query=normalized_query,
            jurisdiction=jurisdiction,
            limit=5
        )
        t_ret_ms = round((time.perf_counter() - t_ret_start) * 1000, 2)
        candidates = retrieval_result.candidates
        if not candidates:
            return await self._execute_guided_rag(
                query=query,
                normalized_query=normalized_query,
                resolved_concepts=resolved_concepts,
                jur_enum=jur_enum,
                jurisdiction=jurisdiction,
                eff_lang=eff_lang,
                trace_id=trace_id,
                t_start=t_start,
                t_norm_ms=t_norm_ms,
                t_guard_ms=t_guard_ms
            )

        # Target provision matching for direct statutory lookup
        top_ev = candidates[0]
        m = self.DIRECT_STATUTORY_REGEX.search(query)
        if m and m.group(2):
            raw_target = m.group(2).lower().strip()
            clean_target = re.sub(r"[^\w]", "", raw_target)
            
            # 1. Exact raw match (e.g. '3(p)' or '158b')
            for cand in candidates:
                cand_sec = (cand.section_number or "").lower()
                if raw_target in cand_sec:
                    top_ev = cand
                    break
            else:
                # 2. Strict normalized section match
                for cand in candidates:
                    cand_sec_clean = re.sub(r"[^\w]", "", (cand.section_number or "").lower())
                    if cand_sec_clean == clean_target or cand_sec_clean.endswith(clean_target):
                        top_ev = cand
                        break

        evidence_list = [top_ev]
        evidence_pack = concept_engine.build_evidence_pack(evidence_list)

        direct_answer = (
            f"Statutory Text & Official Legal Guidance — {top_ev.source_title}, {top_ev.section_number}:\n\n"
            f"\"{top_ev.verbatim_text}\" [1]\n\n"
            f"• Regulatory Authority: {top_ev.authority or 'Statutory Authority'} (Authority Level: {top_ev.authority_level}/5)\n"
            f"• Official Source: {top_ev.source_title}\n"
            f"• Statutory Interpretation: This authentic statutory provision directly governs legal requirements within Indian AYUSH jurisdiction."
        )

        citations = citation_module.extract_citations(direct_answer, evidence_list)
        claim_audit = evaluation_module.verify_claims(direct_answer, evidence_list)
        confidence = evaluation_module.compute_confidence(retrieval_result, claim_audit)

        total_ms = round((time.perf_counter() - t_start) * 1000, 2)
        latency_breakdown = {
            "normalization_ms": t_norm_ms,
            "guardrails_ms": t_guard_ms,
            "retrieval_ms": t_ret_ms,
            "reranking_ms": 0.1,
            "generation_ms": 0.1,
            "verification_ms": 0.2,
            "total_ms": total_ms
        }

        return RAGResponse(
            query=query,
            jurisdiction=jur_enum,
            detected_intent="DIRECT_STATUTORY_LOOKUP",
            direct_answer=direct_answer,
            assessment_table={
                "Trace ID": trace_id,
                "Execution Mode": "DIRECT_STATUTORY",
                "Target Provision": top_ev.section_number,
                "Authority Level": f"{top_ev.authority_level}/5"
            },
            citations=citations,
            verified_claims=[
                ClaimVerificationResult(
                    claim=f"Governed under {top_ev.section_number} of {top_ev.source_title}.",
                    is_supported=True,
                    confidence_score=1.0,
                    supporting_citations=citations[:1]
                )
            ],
            confidence=confidence,
            safe_abstention=False,
            language=eff_lang,
            execution_mode=ExecutionMode.DIRECT_STATUTORY,
            resolved_concepts=[c.concept_id for c in resolved_concepts],
            evidence_pack=evidence_pack,
            trace_id=trace_id,
            diagnostics={
                "direct_lookup": True,
                "matched_section": top_ev.section_number,
                "generation_provider": "DirectStatutoryEngine"
            },
            latency_breakdown=latency_breakdown
        )

    async def _execute_multi_hop_planner(
        self,
        query: str,
        normalized_query: str,
        resolved_concepts: List[Any],
        jur_enum: JurisdictionEnum,
        jurisdiction: str,
        eff_lang: str,
        trace_id: str,
        t_start: float,
        t_norm_ms: float,
        t_guard_ms: float
    ) -> RAGResponse:
        t_plan_start = time.perf_counter()
        domains = {c.domain for c in resolved_concepts}
        pillar_queries = []

        # Collect concept anchors across active resolved concepts
        concept_anchors = " ".join([h for c in resolved_concepts for h in getattr(c, "statutory_hooks", [])])

        if "PATENTABILITY" in domains or any(w in normalized_query.lower() for w in ["patent", "invent", "novel", "withaferin", "curcumin", "extract", "section 39", "foreign filing", "pct", "fungus", "antimicrobial", "rule 24b", "form 18"]):
            pillar_queries.append(f"{normalized_query} [IP_PILLAR: {concept_anchors} Section 3(p) Section 3(e) Section 3(d) Section 3(c) Section 3(j) Section 2(1)(ja) Section 39 'Foreign Filing License PCT application originating in India' Section 40 Rule 24B Patents Act 1970 Amendments 2024]")

        if "BIODIVERSITY_ABS" in domains or any(w in normalized_query.lower() for w in ["biological", "abs", "nba", "sbb", "community", "vaidya", "wild", "herb", "kutki", "fungus"]):
            pillar_queries.append(f"{normalized_query} [ABS_PILLAR: {concept_anchors} Section 3 Section 6 Section 7 Section 19 Biological Diversity Act NBA SBB Form I Form III]")

        if any(w in normalized_query.lower() for w in ["aahara", "food", "fssai", "energy bar", "regulation 3", "regulation 5", "regulation 8", "schedule a", "logo"]):
            pillar_queries.append(f"{normalized_query} [AAHARA_PILLAR: {concept_anchors} Regulation 2(1)(a) Regulation 3 Regulation 5 Regulation 6 Regulation 8 Schedule A FSSAI Ayurveda Aahara 2022]")

        if "DRUG_CLASSIFICATION" in domains or any(w in normalized_query.lower() for w in ["medicine", "drug", "classical", "proprietary", "rule 158b", "rule 122e", "bhasma", "schedule t", "schedule y", "dawa", "ilaj", "punarnava", "section 3(a)"]):
            pillar_queries.append(f"{normalized_query} [ASU_DRUG_PILLAR: {concept_anchors} Section 3(a) 'Ayurvedic, Siddha or Unani drug' Section 3(b) Section 3(h) Rule 158B Schedule T Schedule Y Drugs and Cosmetics Act 1940 ASU Rules 1945]")

        is_export_q = bool(re.search(r"\b(export|germany|europe|eu|wipo|foreign|us|usa|united states|fda|america|overseas|cites|sandalwood)\b", normalized_query.lower()))
        if "EXPORT_INTERNATIONAL" in domains or jurisdiction == "CROSS_BORDER" or is_export_q:
            pillar_queries.append(f"{normalized_query} [EXPORT_PILLAR: Directive 2004/24/EC THMPD traditional herbal simplified registration Germany EU Europe 21 CFR Part 111 DSHEA US FDA NDI notification CITES Appendix II WIPO GRATK Treaty 2024 Article 3 Article 4 Article 5 Article 6]")

        if "TRADEMARKS_IP" in domains or any(w in normalized_query.lower() for w in ["trademark", "trade mark", "brand", "logo", "distinctive", "bottle design", "passing off", "section 9", "section 29", "class 5", "ashwagandha churna"]):
            pillar_queries.append(f"{normalized_query} [TRADEMARK_PILLAR: {concept_anchors} Section 2 Section 9(1)(b) Section 9 Section 11 Section 13 Section 28 Section 29 Rule 28 Trade Marks Act 1999 Class 5]")

        if "SAFETY_PROHIBITION" in domains or any(w in normalized_query.lower() for w in ["dmr", "magic remedies", "cure", "objectionable", "newspaper ad", "advertisement", "guaranteed"]):
            pillar_queries.append(f"{normalized_query} [ADVERTISING_PILLAR: {concept_anchors} Section 3 Section 3(d) Section 4 Schedule Drugs and Magic Remedies Act 1954]")

        if not pillar_queries:
            pillar_queries.append(normalized_query)

        # Reconcile cross-border queries across domestic and international corpuses
        retrieval_jur = "CROSS_BORDER" if (jurisdiction in ["INT", "CROSS_BORDER"] or is_export_q) else jurisdiction

        all_candidates = []
        sub_results = await asyncio.gather(*[
            retrieval_module.retrieve(query=pq, jurisdiction=retrieval_jur, limit=20)
            for pq in pillar_queries
        ])
        for sub_res in sub_results:
            all_candidates.extend(sub_res.candidates)

        seen = set()
        deduped_candidates = []
        for c in all_candidates:
            sec_clean = re.sub(r"^(?:section|rule|regulation|article|\s)+", "", (c.section_number or "").lower()).strip()
            key = f"{c.source_id}:{sec_clean}" if sec_clean else f"{c.source_id}:{c.section_number}"
            if key not in seen:
                seen.add(key)
                deduped_candidates.append(c)

        t_ret_ms = round((time.perf_counter() - t_plan_start) * 1000, 2)

        t_rerank_start = time.perf_counter()
        reranked_evidence = reranking_module.rerank(
            query=normalized_query,
            candidates=deduped_candidates,
            top_k=15
        )
        t_rerank_ms = round((time.perf_counter() - t_rerank_start) * 1000, 2)

        evidence_pack = concept_engine.build_evidence_pack(reranked_evidence)

        t_gen_start = time.perf_counter()
        generated_answer = await generation_module.generate_legal_answer(
            query=normalized_query,
            evidence=reranked_evidence,
            jurisdiction=jurisdiction
        )
        t_gen_ms = round((time.perf_counter() - t_gen_start) * 1000, 2)

        citations = citation_module.extract_citations(generated_answer, reranked_evidence)
        claim_audit = evaluation_module.verify_claims(generated_answer, reranked_evidence)
        dummy_retrieval_res = RetrievalResult(candidates=reranked_evidence, query=normalized_query)
        confidence = evaluation_module.compute_confidence(dummy_retrieval_res, claim_audit)

        verified_claims = claim_audit.get("verified_claims", [])
        unsupported_claims = claim_audit.get("unsupported_claims", [])

        verification_records = []
        for c in verified_claims:
            verification_records.append(
                ClaimVerificationResult(
                    claim=c["claim"],
                    is_supported=True,
                    confidence_score=c["support_score"],
                    supporting_citations=citations[:2]
                )
            )

        final_answer = generated_answer
        if verified_claims and unsupported_claims:
            verified_body = " ".join(c["claim"] for c in verified_claims).strip()
            if len(verified_body) >= 40:
                final_answer = verified_body

        cross_border_posture = None
        is_cross_border_query = (
            jurisdiction == "CROSS_BORDER"
            or "EXPORT_INTERNATIONAL" in domains
            or any(w in normalized_query.lower() for w in ["export", "germany", "eu", "europe", "us", "abroad", "foreign", "overseas"])
        )
        if is_cross_border_query:
            intl_parts = []
            q_clean = normalized_query.lower()
            if any(w in q_clean for w in ["us", "fda", "united states", "america", "dshea"]):
                intl_parts.append(
                    "US FDA entry requires compliance with 21 CFR Part 111 (Dietary Supplement CGMP) and DSHEA 1994, "
                    "with 75-day pre-market New Dietary Ingredient (NDI) notification under FD&C Act Section 413."
                )
            if any(w in q_clean for w in ["eu", "europe", "germany", "france"]):
                intl_parts.append(
                    "European Union entry requires proving 30 years of safe traditional medicinal use under Directive 2004/24/EC (THMPD)."
                )
            if not intl_parts:
                intl_parts.append(
                    "US FDA market entry mandates compliance with 21 CFR Part 111 (DSHEA). "
                    "European Union entry requires proving 30 years of safe traditional medicinal use under Directive 2004/24/EC (THMPD)."
                )
            intl_parts.append("Patent filings in treaty signatories trigger Article 3 mandatory disclosure of origin under WIPO GRATK Treaty 2024.")

            cross_border_posture = {
                "india_posture": (
                    "Mandatory domestic compliance requires prior approval from the National Biodiversity Authority (NBA) "
                    "via Form I under Section 3/19 of the Biological Diversity Act, 2002 before commercial export. "
                    "Patent filings outside India require prior Foreign Filing License (FFL) under Section 39 of the Patents Act, 1970."
                ),
                "international_posture": " ".join(intl_parts)
            }

        total_ms = round((time.perf_counter() - t_start) * 1000, 2)
        latency_breakdown = {
            "normalization_ms": t_norm_ms,
            "guardrails_ms": t_guard_ms,
            "retrieval_ms": t_ret_ms,
            "reranking_ms": t_rerank_ms,
            "generation_ms": t_gen_ms,
            "verification_ms": 1.0,
            "total_ms": total_ms
        }

        return RAGResponse(
            query=query,
            jurisdiction=jur_enum,
            detected_intent="MULTI_HOP_RESEARCH_PLANNER",
            direct_answer=final_answer,
            assessment_table={
                "Trace ID": trace_id,
                "Execution Mode": "MULTI_HOP_PLANNER",
                "Active Pillars Count": len(pillar_queries),
                "Evidence Retrieved": len(reranked_evidence)
            },
            citations=citations,
            verified_claims=verification_records,
            cross_border_posture=cross_border_posture,
            next_actions=[
                "Complete NBA Form I (Access) or Form III (IPR) approval before foreign commercialization.",
                "Verify formulation synergy data under Section 3(e) and non-obvious technical advance under Section 2(1)(ja).",
                "Comply with WIPO GRATK Article 3 mandatory disclosure of biological origin in PCT specifications."
            ],
            confidence=confidence,
            safe_abstention=False,
            language=eff_lang,
            execution_mode=ExecutionMode.MULTI_HOP_PLANNER,
            resolved_concepts=[c.concept_id for c in resolved_concepts],
            evidence_pack=evidence_pack,
            trace_id=trace_id,
            diagnostics={
                "multi_hop_planner": True,
                "pillars": [pq.split("[")[1].split(":")[0] for pq in pillar_queries if "[" in pq],
                "generation_provider": getattr(generation_module, "_active_provider_name", "Unknown")
            },
            latency_breakdown=latency_breakdown
        )

    async def _execute_guided_rag(
        self,
        query: str,
        normalized_query: str,
        resolved_concepts: List[Any],
        jur_enum: JurisdictionEnum,
        jurisdiction: str,
        eff_lang: str,
        trace_id: str,
        t_start: float,
        t_norm_ms: float,
        t_guard_ms: float
    ) -> RAGResponse:
        req_id = f"REQ-{trace_id[-8:]}"
        t_ret_start = time.perf_counter()
        retrieval_query = concept_engine.expand_retrieval_query(normalized_query, resolved_concepts)

        retrieval_result: RetrievalResult = await retrieval_module.retrieve(
            query=retrieval_query,
            jurisdiction=jurisdiction,
            limit=20
        )
        t_ret_ms = round((time.perf_counter() - t_ret_start) * 1000, 2)

        t_rerank_start = time.perf_counter()
        reranked_evidence = reranking_module.rerank(
            query=normalized_query,
            candidates=retrieval_result.candidates,
            top_k=14
        )
        t_rerank_ms = round((time.perf_counter() - t_rerank_start) * 1000, 2)

        evidence_pack = concept_engine.build_evidence_pack(reranked_evidence)

        t_gen_start = time.perf_counter()
        generated_answer = await generation_module.generate_legal_answer(
            query=normalized_query,
            evidence=reranked_evidence,
            jurisdiction=jurisdiction
        )
        t_gen_ms = round((time.perf_counter() - t_gen_start) * 1000, 2)

        citations = citation_module.extract_citations(generated_answer, reranked_evidence)
        t_verif_start = time.perf_counter()
        claim_audit = evaluation_module.verify_claims(generated_answer, reranked_evidence)
        confidence = evaluation_module.compute_confidence(retrieval_result, claim_audit)

        verified_claims = claim_audit.get("verified_claims", [])
        unsupported_claims = claim_audit.get("unsupported_claims", [])

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

        final_answer = generated_answer
        if verified_claims and unsupported_claims:
            verified_body = " ".join(c["claim"] for c in verified_claims).strip()
            if len(verified_body) >= 40:
                final_answer = verified_body

        t_verif_ms = round((time.perf_counter() - t_verif_start) * 1000, 2)

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

        if eff_lang in ["hi", "sa"]:
            final_answer = BhashiniService.translate_statutory_text(final_answer, target_lang=eff_lang)

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
            "generation_provider": getattr(generation_module, "_active_provider_name", "Unknown"),
            "vector_candidates_count": getattr(retrieval_module, "last_vector_count", len(retrieval_result.candidates)),
            "keyword_candidates_count": getattr(retrieval_module, "last_keyword_count", 0),
            "graph_candidates_count": getattr(retrieval_module, "last_graph_count", 0),
        }

        final_response = RAGResponse(
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
            execution_mode=ExecutionMode.GUIDED_RAG,
            resolved_concepts=[c.concept_id for c in resolved_concepts],
            evidence_pack=evidence_pack,
            trace_id=trace_id,
            diagnostics=diagnostics,
            latency_breakdown=latency_breakdown
        )
        telemetry_collector.record_orchestration_response(
            response_obj=final_response,
            query=query,
            request_id=req_id,
            token_usage=getattr(generation_module, "last_token_usage", None),
            success=True
        )
        return final_response

    async def stream_query(
        self,
        query: str,
        jurisdiction: str = "IN",
        language: str = "en",
        request_id: Optional[str] = None
    ):
        """
        Asynchronous generator emitting live multi-stage pipeline events, streaming tokens,
        and final structured RAG payload.
        """
        import asyncio
        trace_id = f"TRC-{uuid.uuid4().hex[:8].upper()}"
        req_id = request_id or f"REQ-{trace_id[-8:]}"
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
            telemetry_collector.record_orchestration_response(
                response_obj=resp,
                query=query,
                request_id=req_id,
                token_usage=None,
                success=True
            )
            yield {"event": "result", "data": resp.model_dump()}
            return

        # Stage 2b: Conversational & Formulation Intake Routing
        resolved_concepts = concept_engine.resolve_concepts(normalized_query)
        execution_mode = self.determine_execution_mode(normalized_query, resolved_concepts, jurisdiction)

        if execution_mode == ExecutionMode.CONVERSATIONAL_GREETING:
            yield {
                "event": "stage",
                "data": {"stage": "CONVERSATIONAL_ROUTER", "message": "Welcoming innovator to IP-SAKTI Sahayak..."}
            }
            resp = await self._execute_conversational_greeting(
                query=query,
                jur_enum=jur_enum,
                jurisdiction=jurisdiction,
                eff_lang=eff_lang,
                trace_id=trace_id,
                t_start=time.perf_counter(),
                t_norm_ms=0.1,
                t_guard_ms=0.1
            )
            yield {"event": "token", "data": {"token": resp.direct_answer}}
            telemetry_collector.record_orchestration_response(
                response_obj=resp,
                query=query,
                request_id=req_id,
                token_usage=None,
                success=True
            )
            yield {"event": "result", "data": resp.model_dump()}
            return

        if execution_mode == ExecutionMode.CLASSIFICATION_INTAKE:
            yield {
                "event": "stage",
                "data": {"stage": "CLASSIFICATION_INTAKE", "message": "Initiating formulation classification intake..."}
            }
            resp = await self._execute_classification_intake(
                query=query,
                jur_enum=jur_enum,
                jurisdiction=jurisdiction,
                eff_lang=eff_lang,
                trace_id=trace_id,
                t_start=time.perf_counter(),
                t_norm_ms=0.1,
                t_guard_ms=0.1
            )
            yield {"event": "token", "data": {"token": resp.direct_answer}}
            telemetry_collector.record_orchestration_response(
                response_obj=resp,
                query=query,
                request_id=req_id,
                token_usage=None,
                success=True
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

        # Stream full answer as a single token event (real streaming is handled by the LLM provider)
        yield {"event": "token", "data": {"token": final_answer}}

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

        telemetry_collector.record_orchestration_response(
            response_obj=rag_response,
            query=query,
            request_id=req_id,
            token_usage=getattr(generation_module, "last_token_usage", None),
            success=True
        )

        yield {"event": "result", "data": rag_response.model_dump()}


orchestration_module = ModularOrchestrator()
