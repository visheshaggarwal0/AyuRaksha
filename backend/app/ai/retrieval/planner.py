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
        q_lower = normalized_query.lower()
        if intent == "PATENTABILITY_ASSESSMENT":
            expanded_terms.extend(["Section 3(p) Traditional Knowledge", "Section 3(e) Synergistic Admixture", "Novelty"])
            if any(w in q_lower for w in ["process", "extraction", "novel", "inventive", "nano", "method of manufacture"]):
                expanded_terms.extend(["Section 2(1)(j) Invention", "Section 2(1)(ja) Inventive Step", "Section 3(d) New Form Efficacy"])
            if any(w in q_lower for w in ["treatment", "cure", "administer", "doctor", "disease", "ulcer", "patient"]):
                expanded_terms.extend(["Section 3(i) Method of Treatment"])
            if any(w in q_lower for w in ["disclose", "source", "origin", "where", "collected", "himachal", "geographical"]):
                expanded_terms.extend(["Section 10(4) Source of Biological Material", "Section 6 BDA Approval"])
        elif intent == "ABS_ASSESSMENT":
            expanded_terms.extend(["Biological Diversity Act Section 7 SBB", "Section 3 NBA Approval", "Fair and Equitable Benefit Sharing"])
            if any(w in q_lower for w in ["indian", "domestic", "vaidya", "local", "delhi", "manufacturing"]):
                expanded_terms.extend(["Section 7 SBB Prior Intimation"])
            if any(w in q_lower for w in ["foreign", "nri", "overseas", "foreign company"]):
                expanded_terms.extend(["Section 3 NBA Approval", "Form I"])
        elif intent == "PRODUCT_CLASSIFICATION":
            expanded_terms.extend(["Drugs & Cosmetics Act Section 3(a)", "Rule 158B", "FSSAI Ayurveda Aahara Regulation"])
            if any(w in q_lower for w in ["synthetic", "vitamin", "mineral", "food", "aahara"]):
                expanded_terms.extend(["Regulation 3 Prohibitions", "Regulation 2(1)(a) Definition"])
        elif intent == "EXPORT_ASSESSMENT":
            expanded_terms.extend(["Directive 2004/24/EC", "US FDA Dietary Supplement", "Export Compliance"])

        reformulated_query = " ".join(dict.fromkeys(" ".join(expanded_terms).split()))

        # 3. Domain filtering & graph traversal strategy
        # Use a set of candidate domains so international treaties (INTELLECTUAL_PROPERTY)
        # are not excluded when filtering to PATENTS for patentability questions.
        domain_filters = None
        if intent == "PATENTABILITY_ASSESSMENT":
            domain_filters = ["PATENTS", "INTELLECTUAL_PROPERTY", "PATENTS_AND_IP"]
        elif intent == "ABS_ASSESSMENT":
            domain_filters = ["BIODIVERSITY_ABS"]
        elif intent == "PRODUCT_CLASSIFICATION":
            domain_filters = ["AYUSH_DRUG_REGULATION", "DRUGS_COSMETICS", "FOOD_AYURVEDA_AAHARA"]
        domain_filter = domain_filters[0] if domain_filters and len(domain_filters) == 1 else domain_filters

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
