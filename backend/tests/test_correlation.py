from app.correlation.engine import CorrelationEngine
def test_candidate_language_and_explicit_confidence():
    c=CorrelationEngine().candidate("a","CVE-1","high","nginx",False)
    assert c["status"]=="candidate_vulnerability"
    assert c["confidence"]==0.3
    assert "candidate only" in c["rationale"]
