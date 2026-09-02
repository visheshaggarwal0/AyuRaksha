import re
from typing import Dict, Any, List
from app.agents.router import QueryRouterAgent
from app.engines.safety import SafetyGuardrailEngine
from app.engines.search import HybridLegalSearchEngine
from app.engines.verifier import CitationEntailmentVerifier
from app.engines.llm_client import LocalOllamaClient
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
        self.llm_client = LocalOllamaClient()

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

        # Step 5: Generate Synthesis via Local Ollama (llama3.1:8b)
        direct_ans = None
        system_prompt = (
            "You are AyuRaksha, a highly detailed AI IP & Regulatory Navigator for Ayurvedic Innovation "
            "under the Ministry of Ayush. Answer the user query using ONLY the provided statutory context. "
            "Be highly descriptive, supportive, and structure your answer in easy-to-read paragraphs. "
            "At the end of each paragraph or claim, add a citation marker like [1], [2] corresponding to the statutory sources used. "
            "NEVER hallucinate non-existent law. If the context does not answer the question, state that."
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
        else:
            # Fallback only if the LLM connection completely fails
            direct_ans = (
                f"I have carefully evaluated your query against {len(retrieved_sources)} verified statutory authorities "
                f"under the {effective_jurisdiction} regulatory namespace.\n\n"
                "However, the Local AI Synthesis Engine (Ollama) failed to respond. Please review the detailed citations below to understand the exact statutory provisions."
            )

        # Assessment Table
        assessment_table = {
            "Jurisdiction": f"{effective_jurisdiction} Regulatory Namespace",
            "Intent Category": intent.replace("_", " ").title(),
            "Statutory Sources Evaluated": f"{len(retrieved_sources)} Official Provisions",
            "LLM Synthesizer": "llama3.1:8b (Ollama Local)"
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
        confidence_level = "HIGH" if supported_claims else "LOW"
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
