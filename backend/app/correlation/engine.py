from dataclasses import dataclass
@dataclass
class ConfidencePolicy:
    ct_discovery: float=0.70
    dns_resolve: float=0.15
    http_response: float=0.15
    def combined(self,*signals): return min(1.0, round(sum(getattr(self,s) for s in signals),2))
class CorrelationEngine:
    def __init__(self, policy=None): self.policy=policy or ConfidencePolicy()
    def candidate(self, asset_id, cve_id, severity, technology, kev=False):
        confidence=self.policy.combined("dns_resolve","http_response") if technology else self.policy.ct_discovery
        return {"asset_id":asset_id,"cve_id":cve_id,"severity":severity,"kev":kev,"confidence":confidence,"status":"candidate_vulnerability","rationale":f"Technology observed: {technology}; CVE correlation is a candidate only."}
