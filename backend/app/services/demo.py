from sqlalchemy.orm import Session
from app.models.entities import Organization,User,Scope,Asset,Evidence,Relationship,VulnerabilityCandidate,ScanJob
from app.core.security import hash_password
from app.collectors.demo import DemoAdapter
from app.correlation.engine import CorrelationEngine

def seed(db: Session):
    existing=db.query(User).filter_by(email="admin@lens.local").first()
    if existing: return existing.organization_id
    org=Organization(name="Demo Organization"); db.add(org); db.flush()
    user=User(email="admin@lens.local",password_hash=hash_password("ChangeMe123!"),role="ADMIN",organization_id=org.id); db.add(user)
    scope=Scope(organization_id=org.id,root_domain="example.com",authorized=True,allow_active_http=False); db.add(scope); db.flush()
    items=DemoAdapter().collect(scope.root_domain); assets={}
    for item in items:
        asset=Asset(scope_id=scope.id,kind=item.kind,value=item.value,status="observed_asset"); db.add(asset); db.flush(); assets[(item.kind,item.value)]=asset
        db.add(Evidence(asset_id=asset.id,source=item.source,source_url=item.source_url,normalized_value=item.normalized_value,raw_reference=item.raw_reference,confidence=item.confidence,collector="DemoAdapter"))
    db.flush()
    domain=assets[("domain","example.com")]; api=assets[("subdomain","api.example.com")]; ip=assets[("ip","203.0.113.10")]; tech=assets[("technology","nginx 1.24")]
    db.add(Relationship(scope_id=scope.id,source_asset_id=domain.id,target_asset_id=api.id,relation_type="discovers",confidence=.70,source="demo-fixture"))
    db.add(Relationship(scope_id=scope.id,source_asset_id=api.id,target_asset_id=ip.id,relation_type="resolves_to",confidence=.85,source="demo-fixture"))
    db.add(Relationship(scope_id=scope.id,source_asset_id=api.id,target_asset_id=tech.id,relation_type="technology_observed",confidence=.60,source="demo-fixture"))
    db.add(VulnerabilityCandidate(asset_id=tech.id,cve_id="CVE-2024-DEMO",severity="medium",kev=False,confidence=.30,rationale="Candidate only: synthetic technology observation; not a vulnerability assertion."))
    db.commit(); return org.id
