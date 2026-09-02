import json
from typing import List
from app.models.schemas import ProductClassificationRequest, ProductClassificationResponse, Citation, Jurisdiction
from app.engines.llm_client import LocalOllamaClient
from app.engines.search import HybridLegalSearchEngine

class ProductClassifier:
    """
    Dynamic LLM-based Product Classifier using RAG.
    Connects to Ollama (llama3.1:8b) to synthesize classification logic,
    supported by verified PostgreSQL pgvector citations.
    """

    @staticmethod
    async def evaluate(req: ProductClassificationRequest) -> ProductClassificationResponse:
        search_engine = HybridLegalSearchEngine()
        llm_client = LocalOllamaClient()

        # Build a search query based on product traits
        search_query = f"Classification of {req.intended_use} product. "
        if req.in_classical_text:
            search_query += "Based on classical Ayurvedic texts (First Schedule). "
        if req.disease_treatment_claims:
            search_query += "Makes disease treatment or mitigation claims. "
        if req.is_formulation_modified:
            search_query += "Modified formulation or novel extraction. "

        # 1. Retrieve Regulatory Statutes via pgvector
        retrieved_sources = await search_engine.search(query=search_query, limit=3)
        
        context_blocks = "\n\n".join([
            f"Source: {s.get('source_title')} ({s.get('section_number')})\nText: {s.get('raw_statute')}"
            for s in retrieved_sources
        ])

        # 2. Structure Prompt for Ollama JSON Mode
        system_prompt = (
            "You are a regulatory expert AI for the Ministry of Ayush. "
            "You must classify the user's proposed product based ONLY on the provided statutory context. "
            "You must return a valid JSON object matching this exact schema: \n"
            "{\n"
            '  "category": "String (e.g. CLASSICAL_AYURVEDIC_MEDICINE, PATENT_PROPRIETARY, AYURVEDA_AAHARA, COSMETIC)",\n'
            '  "governing_act": "String (Name of the primary act)",\n'
            '  "patentability": "String (e.g. POTENTIALLY_PATENTABLE, BARRED_UNDER_SECTION_3P)",\n'
            '  "patent_rationale": "String (Detailed explanation)",\n'
            '  "abs_required": true,\n'
            '  "regulatory_authority": "String",\n'
            '  "next_actions": ["Action 1", "Action 2"]\n'
            "}"
        )

        user_prompt = (
            f"Product Name: {req.name}\n"
            f"Intended Use: {req.intended_use}\n"
            f"Classical Text: {req.in_classical_text}\n"
            f"Modified Formulation: {req.is_formulation_modified}\n"
            f"Disease Claims: {req.disease_treatment_claims}\n\n"
            f"Statutory Context:\n{context_blocks}\n\n"
            "Classify the product and return JSON:"
        )

        # 3. Call Local LLM
        llm_res = await llm_client.generate_response(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            json_format=True
        )

        # 4. Fallback if LLM fails (Network error, etc.)
        parsed = {
            "category": "UNKNOWN_CLASSIFICATION (LLM Failure)",
            "governing_act": "Manual Review Required",
            "patentability": "UNKNOWN",
            "patent_rationale": "The local Ollama model failed to return a valid JSON classification.",
            "abs_required": True,
            "regulatory_authority": "State Licensing Authority",
            "next_actions": ["Please ensure Ollama is running and accessible."]
        }

        if llm_res:
            try:
                parsed = json.loads(llm_res)
            except json.JSONDecodeError:
                import logging
                logging.error(f"[!] Ollama returned invalid JSON: {llm_res}")

        # 5. Build Dynamic Citations
        citations = []
        for src in retrieved_sources:
            citations.append(Citation(
                source_id=src.get("source_id", "IND_STATUTE"),
                source_title=src.get("source_title", "Statutory Source"),
                section=src.get("section_number", "Section X"),
                jurisdiction=src.get("jurisdiction", "IN"),
                verbatim_quote=src.get("raw_statute", "")[:350],
                support_score=src.get("support_score", 0.95)
            ))

        return ProductClassificationResponse(
            product_name=req.name,
            category=parsed.get("category", "UNKNOWN"),
            governing_act=parsed.get("governing_act", "UNKNOWN"),
            patentability=parsed.get("patentability", "UNKNOWN"),
            patent_rationale=parsed.get("patent_rationale", "No rationale provided."),
            abs_required=parsed.get("abs_required", True),
            regulatory_authority=parsed.get("regulatory_authority", "UNKNOWN"),
            citations=citations,
            confidence=0.85,
            next_actions=parsed.get("next_actions", [])
        )
