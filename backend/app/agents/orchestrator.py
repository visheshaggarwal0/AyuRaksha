import re
from typing import Dict, Any, List
from app.agents.router import QueryRouterAgent
from app.engines.safety import SafetyGuardrailEngine
from app.engines.search import HybridLegalSearchEngine
from app.engines.verifier import CitationEntailmentVerifier
from app.engines.llm_client import OpenRouterLLMClient
from app.models.schemas import StructuredAnswer, Citation, ClaimVerification

class AyuRakshaOrchestrator:
    """
    Central Multi-Agent Decision Engine for AyuRaksha:
    1. Query Router Agent (Intent + Language + Jurisdiction)
    2. Safety & Guardrail Engine (Safe Abstention + Biopiracy Check)
    3. Hybrid Legal Search (PostgreSQL full-text + pgvector + RRF)
    4. OpenRouter Google Gemma 4 31B LLM Synthesis (with fallback)
    5. Citation Entailment Verification
    """

    def __init__(self):
        self.router = QueryRouterAgent()
        self.safety = SafetyGuardrailEngine()
        self.search_engine = HybridLegalSearchEngine()
        self.verifier = CitationEntailmentVerifier()
        self.llm_client = OpenRouterLLMClient()

    async def process_query(
        self,
        query: str,
        user_jurisdiction: str = "IN",
        language: str = "en"
    ) -> StructuredAnswer:
        # Step 1: Safety & Guardrail Check
        is_safe, safety_category, safety_msg = self.safety.evaluate_query_safety(query)
        if not is_safe:
            return StructuredAnswer(
                direct_answer=f"⚠️ SAFE ABSTENTION ACTIVATED: {safety_msg}",
                jurisdiction=user_jurisdiction,
                assessment_table={"Safety Status": "NON_COMPLIANT / BLOCKED", "Violation Type": safety_category},
                verified_claims=[
                    ClaimVerification(
                        claim=safety_msg,
                        is_supported=False,
                        confidence_score=0.0,
                        supporting_citations=[]
                    )
                ],
                recommended_next_action="Consult an official State Biodiversity Board or AYUSH legal facilitator. Ensure all biological resources are legally accessed under BDA 2002 guidelines.",
                safe_abstention=True,
                abstention_reason=safety_msg
            )

        # Step 2: Intelligent Routing
        route_meta = self.router.route_query(query, user_jurisdiction)
        effective_jurisdiction = route_meta["jurisdiction"]
        intent = route_meta["intent"]
        botanicals = route_meta["detected_botanicals"]

        # Step 3: Hybrid Search Retrieval
        retrieved_sources = await self.search_engine.search(
            query=query,
            jurisdiction=effective_jurisdiction,
            limit=4
        )

        # Step 4: Build Context for LLM / Evidence Synthesis
        context_blocks = "\n\n".join([
            f"Source: {s.get('source_title')} ({s.get('section_number')})\nStatutory Text: {s.get('raw_statute')}"
            for s in retrieved_sources
        ])

        # Step 5: Generate Synthesis via OpenRouter Gemma 4 31B if available
        direct_ans = None
        if self.llm_client.api_key:
            system_prompt = (
                "You are AyuRaksha, a helpful and highly detailed AI IP & Regulatory Navigator for Ayurvedic Innovation "
                "under the Ministry of Ayush. Answer the user query using the provided statutory context. "
                "Be highly descriptive, supportive, and structure your answer in easy-to-read paragraphs. "
                "At the end of each paragraph or claim, add a citation marker like [1], [2] corresponding to the statutory sources used. "
                "NEVER hallucinate non-existent law. "
                "Provide ONLY the final user-facing response. Do NOT include internal chain-of-thought, hidden reasoning, scratchpad analysis, prompt analysis, instructions, or meta-commentary. Do not describe how you analyzed the question. Start directly with the answer intended for the user. You may use normal Markdown headings, lists, tables, and citations such as [1], [2]."
            )
            user_msg = f"User Question: {query}\n\nStatutory Context:\n{context_blocks}\n\nProvide a detailed and helpful response with inline [1] citations:"
            llm_res = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.1
            )
            if llm_res and len(llm_res.strip()) > 30:
                direct_ans = llm_res.strip()

        # Deterministic Fallback if LLM is unavailable or unconfigured
        if not direct_ans:
            if intent == "PATENTABILITY_ASSESSMENT":
                if not retrieved_sources:
                    direct_ans = (
                        "No authoritative statutory provisions were retrieved for this patentability query. "
                        "Please consult official patent examination guidelines under the relevant jurisdiction."
                    )
                else:
                    top_src = retrieved_sources[0]
                    sec_num = top_src.get("section_number", "Statutory Provision")
                    src_title = top_src.get("source_title", "Applicable Patent Statute")
                    raw_quote = (top_src.get("raw_statute") or "").strip()

                    if raw_quote:
                        direct_ans = (
                            f"Assessing patentability under {sec_num} of the {src_title} establishes the statutory standard: "
                            f"\"{raw_quote}\" [1]."
                        )
                    else:
                        direct_ans = (
                            f"Assessing patentability relates to {sec_num} of the {src_title} [1]. "
                            "An authoritative statutory provision was retrieved, but its text was unavailable for display."
                        )
            elif intent == "ABS_ASSESSMENT":
                direct_ans = (
                    "Navigating Access and Benefit Sharing (ABS) is a crucial step in ethical Ayurvedic commerce. Here is how the law applies to your case:\n\n"
                    "Under the Biological Diversity Act, 2002 (as amended in 2023), Indian commercial entities must submit "
                    "Prior Intimation to the respective State Biodiversity Board (SBB) under Section 7 [1]. If you are a foreign entity or "
                    "a company with foreign shareholding, you will require prior approval directly from the National Biodiversity Authority (NBA) under Section 3 [2].\n\n"
                    "Let me know if you need help initiating the NBA forms!"
                )
            elif intent == "PRODUCT_CLASSIFICATION":
                direct_ans = (
                    "I'd be happy to help you classify your herbal formulation. The regulatory pathway depends heavily on your ingredients and how you intend to market it.\n\n"
                    "Under the Drugs & Cosmetics Act 1940, if your formulation strictly follows recipes in First Schedule texts "
                    "(like Charaka or Sharangadhara Samhita), it is classified as a Classical ASU Drug under Section 3(a) [1]. However, if it contains modified ratios or new extraction methods, "
                    "it requires a Patent/Proprietary license under Rule 158B [1].\n\n"
                    "Alternatively, if you plan to market it as a food product without specific disease-curing claims, it falls under the FSSAI Ayurveda Aahara 2022 regulations [2]. Let's walk through the Product Classifier tool together if you want to be sure!"
                )
            elif intent == "EXPORT_ASSESSMENT":
                direct_ans = (
                    "Exporting Ayurvedic formulations is an exciting step! To do so successfully, you must satisfy both domestic and international standards.\n\n"
                    "First, you need to meet Indian manufacturing standards (WHO-GMP / Schedule T) before leaving the country [1]. Once in the destination market, local frameworks apply. "
                    "For example, in the US, products typically enter under US FDA DSHEA as Dietary Supplements with allowable Structure/Function claims [2]. In the EU, compliance with heavy metal limits and THMPD (Directive 2004/24/EC) is strictly required [2].\n\n"
                    "Would you like to generate a detailed compliance dossier for a specific country?"
                )
            else:
                direct_ans = (
                    f"I have carefully evaluated your query against {len(retrieved_sources)} verified statutory authorities "
                    f"under the {effective_jurisdiction} regulatory namespace [1].\n\n"
                    "Based on the analysis, you are currently operating within a highly regulated space. Please review the detailed citations below to understand the exact statutory provisions."
                )

        # Assessment Table
        assessment_table = {
            "Jurisdiction": f"{effective_jurisdiction} Regulatory Namespace",
            "Intent Category": intent.replace("_", " ").title(),
            "Statutory Sources Evaluated": f"{len(retrieved_sources)} Official Provisions",
            "LLM Synthesizer": "Google Gemma 4 31B (OpenRouter)" if self.llm_client.api_key else "Deterministic Baseline"
        }

        # Step 6: Build Verified Citations
        citations = []
        for src in retrieved_sources:
            cit = Citation(
                source_id=src.get("source_id", "IND_STATUTE"),
                source_title=src.get("source_title", "Statutory Source"),
                section=src.get("section_number", "Section X"),
                jurisdiction=src.get("jurisdiction", "IN"),
                official_url=src.get("official_url"),
                support_score=src.get("support_score", 0.95),
                verbatim_quote=src.get("raw_statute", "")[:350]
            )
            citations.append(cit)

        # Step 7: Verify Claims via Entailment
        # Validate distinct answer claims against retrieved statutory text.
        candidate_claims = [
            claim.strip()
            for claim in re.split(r"(?<=[.!?])\s+|\n{2,}", direct_ans)
            if len(claim.strip()) >= 40
        ][:5]
        verified_claims = [self.verifier.verify(claim, citations) for claim in candidate_claims]
        supported_claims = [claim for claim in verified_claims if claim.is_supported]

        total_claims = len(verified_claims)
        supported_count = len(supported_claims)

        if total_claims == 0:
            confidence_level = "LOW"
            support_ratio = 0.0
        else:
            support_ratio = supported_count / total_claims
            if support_ratio >= 0.85:
                confidence_level = "HIGH"
            elif support_ratio >= 0.60:
                confidence_level = "MEDIUM"
            else:
                confidence_level = "LOW"

        assessment_table["Claim Verification Ratio"] = f"{supported_count}/{total_claims} ({int(support_ratio * 100)}%)"

        caveats = []
        if not citations:
            caveats.append("No authoritative provision was retrieved. Treat this response as general guidance only.")
        elif len(supported_claims) != len(verified_claims):
            caveats.append("Some generated statements could not be matched to the retrieved statutory text and require human review.")

        return StructuredAnswer(
            direct_answer=direct_ans,
            jurisdiction=effective_jurisdiction,
            assessment_table=assessment_table,
            verified_claims=verified_claims,
            citations=citations,
            confidence_level=confidence_level,
            caveats=caveats,
            recommended_next_action="Run the interactive Product Classification Journey to lock regulatory status. Verify botanical ingredients against the National Biodiversity Authority ABS Form requirements.",
            safe_abstention=False
        )
