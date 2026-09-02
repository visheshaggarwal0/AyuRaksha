from typing import Dict, Any, List

class RetrievalPlanner:
    """
    Formulates optimized retrieval strategies based on intent, jurisdiction, and extracted entities.
    Determines query reformulations, filtering criteria, and knowledge graph expansion depth.
    """

    @classmethod
    def plan(cls, normalized_query: str, route: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        jurisdiction = route.get("jurisdiction", "IN")
        intent = route.get("intent", "GENERAL_RESEARCH")

        # 1. Expand query terms with botanical scientific names
        expanded_terms = [normalized_query]
        for bot in entities.get("botanicals", []):
            sci = bot.get("scientific_name")
            sans = bot.get("sanskrit_name")
            if sci:
                expanded_terms.append(sci)
            if sans:
                expanded_terms.append(sans)

        # 2. Add intent-specific statutory hooks
        if intent == "PATENTABILITY_ASSESSMENT":
            expanded_terms.extend(["Section 3(p) Traditional Knowledge", "Section 3(e) Synergistic Admixture", "Novelty"])
        elif intent == "ABS_ASSESSMENT":
            expanded_terms.extend(["Biological Diversity Act Section 7 SBB", "Section 3 NBA Approval", "Fair and Equitable Benefit Sharing"])
        elif intent == "PRODUCT_CLASSIFICATION":
            expanded_terms.extend(["Drugs & Cosmetics Act Section 3(a)", "Rule 158B", "FSSAI Ayurveda Aahara Regulation"])
        elif intent == "EXPORT_ASSESSMENT":
            expanded_terms.extend(["Directive 2004/24/EC", "US FDA Dietary Supplement", "Export Compliance"])

        reformulated_query = " ".join(dict.fromkeys(" ".join(expanded_terms).split()))

        # 3. Domain filtering & graph traversal strategy
        domain_filter = None
        if intent == "PATENTABILITY_ASSESSMENT":
            domain_filter = "PATENTS"
        elif intent == "ABS_ASSESSMENT":
            domain_filter = "BIODIVERSITY_ABS"
        elif intent == "PRODUCT_CLASSIFICATION":
            domain_filter = "DRUGS_COSMETICS"

        # Determine whether to traverse knowledge graph relations
        enable_graph_expansion = intent in ["PATENTABILITY_ASSESSMENT", "ABS_ASSESSMENT", "PRODUCT_CLASSIFICATION"] or entities.get("has_biological_resources", False)

        return {
            "reformulated_query": reformulated_query,
            "dense_query": normalized_query,
            "sparse_query": reformulated_query,
            "jurisdiction": jurisdiction,
            "domain_filter": domain_filter,
            "enable_graph_expansion": enable_graph_expansion,
            "max_candidates": 15
        }
