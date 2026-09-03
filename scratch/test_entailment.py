import sys
sys.path.insert(0, "backend")
from app.modules.evaluation import ModularEvaluationEngine
from app.models.domain import Evidence

def test_entailment():
    engine = ModularEvaluationEngine()
    
    # Evidence is Patents Act Section 3(p)
    ev = Evidence(
        evidence_id="EV-1",
        source_id="PATENTS_ACT_1970",
        source_title="The Patents Act, 1970",
        section_number="SECTION 3(p)",
        verbatim_text="An invention which, in effect, is traditional knowledge or which is an aggregation or duplication of known properties of traditionally known component or components is not an invention.",
        authority="Indian Patent Office",
        authority_level=5
    )
    
    # Case A: Legitimate claim
    claim_a = "Under Section 3(p), traditional knowledge is excluded from patentability. [1]"
    res_a = engine.verify_claims(claim_a, [ev])
    print("Claim A verified:", len(res_a["verified_claims"]), "unsupported:", len(res_a["unsupported_claims"]))
    assert len(res_a["verified_claims"]) == 1, "Legitimate claim should be verified"

    # Case B: ChatGPT's exact trick claim with ungrounded GI grant
    claim_b = "Section 3(p) excludes traditional knowledge and automatically grants GI tag protection. [1]"
    res_b = engine.verify_claims(claim_b, [ev])
    print("Claim B verified:", len(res_b["verified_claims"]), "unsupported:", len(res_b["unsupported_claims"]))
    assert len(res_b["unsupported_claims"]) == 1, "Ungrounded GI grant must be flagged as unsupported!"

    print("ALL ENTAILMENT ASSERTIONS PASSED!")

if __name__ == "__main__":
    test_entailment()
