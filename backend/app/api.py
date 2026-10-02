from datetime import datetime, timezone
import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import decode_token, verify_password, create_token
from app.models.entities import *
from app.schemas import *
from app.services.demo import seed
from app.services.scope_control import ScopeControl, ScopeViolation, validate_remote_url
from app.collectors.demo import DemoAdapter
from app.reporting.pdf import build_pdf

router=APIRouter(prefix="/api/v1")
def current_user(authorization: str|None=Header(default=None), db: Session=Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "): raise HTTPException(401,"authentication required")
    p=decode_token(authorization[7:]); user=db.get(User,p["sub"])
    if not user: raise HTTPException(401,"user not found")
    return user
def require_roles(*roles):
    def dep(user=Depends(current_user)):
        if user.role not in roles: raise HTTPException(403,"insufficient role")
        return user
    return dep

@router.post("/demo/seed")
def demo_seed(db: Session=Depends(get_db)): return {"organization_id":seed(db),"message":"synthetic dataset ready"}
@router.post("/auth/login",response_model=TokenOut)
def login(body: LoginIn, db: Session=Depends(get_db)):
    user=db.query(User).filter_by(email=body.email.lower()).first()
    if not user or not verify_password(body.password,user.password_hash): raise HTTPException(401,"invalid credentials")
    db.add(AuditLog(organization_id=user.organization_id,actor_id=user.id,action="login")); db.commit()
    return TokenOut(access_token=create_token(user.id,user.role,user.organization_id))
@router.get("/me")
def me(user=Depends(current_user)): return {"id":user.id,"email":user.email,"role":user.role,"organization_id":user.organization_id}
@router.post("/scopes")
def create_scope(body: ScopeIn, db: Session=Depends(get_db), user=Depends(require_roles("ADMIN","ANALYST"))):
    if body.organization_id != user.organization_id: raise HTTPException(403,"organization isolation")
    try: root=ScopeControl(body.root_domain,body.authorized).normalize_domain(body.root_domain)
    except ScopeViolation as exc: raise HTTPException(422,str(exc)) from exc
    scope=Scope(organization_id=user.organization_id,root_domain=root,authorized=body.authorized,allow_active_http=body.allow_active_http); db.add(scope); db.add(AuditLog(organization_id=user.organization_id,actor_id=user.id,action="scope_created",target=root)); db.commit(); db.refresh(scope); return scope
@router.get("/scopes")
def list_scopes(db: Session=Depends(get_db), user=Depends(current_user)): return db.query(Scope).filter_by(organization_id=user.organization_id).all()
@router.post("/scans")
def create_scan(body: ScanIn, db: Session=Depends(get_db), user=Depends(require_roles("ADMIN","ANALYST"))):
    scope=db.get(Scope,body.scope_id)
    if not scope or scope.organization_id != user.organization_id: raise HTTPException(404,"scope not found")
    job=ScanJob(scope_id=scope.id,status="RUNNING",progress=10); db.add(job); db.flush()
    for item in DemoAdapter().collect(scope.root_domain):
        asset=db.query(Asset).filter_by(scope_id=scope.id,kind=item.kind,value=item.value).first()
        if not asset: asset=Asset(scope_id=scope.id,kind=item.kind,value=item.value); db.add(asset); db.flush()
        asset.last_seen_at=datetime.now(timezone.utc)
        db.add(Evidence(asset_id=asset.id,source=item.source,source_url=item.source_url,normalized_value=item.normalized_value,raw_reference=item.raw_reference,confidence=item.confidence,collector="DemoAdapter"))
    job.progress=100; job.status="COMPLETED"; job.finished_at=datetime.now(timezone.utc); db.add(AuditLog(organization_id=user.organization_id,actor_id=user.id,action="scan_completed",target=job.id)); db.commit(); return job
@router.get("/scans/{job_id}")
def get_scan(job_id: str, db: Session=Depends(get_db), user=Depends(current_user)):
    job=db.get(ScanJob,job_id)
    if not job: raise HTTPException(404,"job not found")
    scope=db.get(Scope,job.scope_id)
    if not scope or scope.organization_id != user.organization_id: raise HTTPException(403,"organization isolation")
    return job
@router.get("/assets")
def assets(scope_id: str|None=None, db: Session=Depends(get_db), user=Depends(current_user)):
    q=db.query(Asset).join(Scope,Asset.scope_id==Scope.id).filter(Scope.organization_id==user.organization_id)
    if scope_id: q=q.filter(Asset.scope_id==scope_id)
    return q.order_by(Asset.last_seen_at.desc()).all()
@router.get("/evidence/{asset_id}")
def evidence(asset_id: str, db: Session=Depends(get_db), user=Depends(current_user)):
    asset=db.get(Asset,asset_id); scope=db.get(Scope,asset.scope_id) if asset else None
    if not asset or not scope or scope.organization_id != user.organization_id: raise HTTPException(404,"asset not found")
    db.add(AuditLog(organization_id=user.organization_id,actor_id=user.id,action="evidence_access",target=asset_id)); db.commit(); return db.query(Evidence).filter_by(asset_id=asset_id).all()
@router.get("/graph")
def graph(scope_id: str, db: Session=Depends(get_db), user=Depends(current_user)):
    scope=db.get(Scope,scope_id)
    if not scope or scope.organization_id != user.organization_id: raise HTTPException(404,"scope not found")
    assets=db.query(Asset).filter_by(scope_id=scope_id).all(); rels=db.query(Relationship).filter_by(scope_id=scope_id).all()
    return {"nodes":[{"id":a.id,"kind":a.kind,"value":a.value} for a in assets],"edges":[{"source":r.source_asset_id,"target":r.target_asset_id,"type":r.relation_type,"confidence":r.confidence,"source_name":r.source} for r in rels]}
@router.get("/vulnerabilities")
def vulnerabilities(db: Session=Depends(get_db), user=Depends(current_user)):
    return db.query(VulnerabilityCandidate).join(Asset,Asset.id==VulnerabilityCandidate.asset_id).join(Scope,Scope.id==Asset.scope_id).filter(Scope.organization_id==user.organization_id).all()
@router.get("/timeline")
def timeline(db: Session=Depends(get_db), user=Depends(current_user)):
    rows=db.query(Asset).join(Scope,Asset.scope_id==Scope.id).filter(Scope.organization_id==user.organization_id).order_by(Asset.first_seen_at).all(); return [{"date":a.first_seen_at.date().isoformat(),"event":"asset_observed","asset":a.value,"kind":a.kind} for a in rows]
@router.get("/reports/json")
def report_json(db: Session=Depends(get_db), user=Depends(current_user)):
    assets=db.query(Asset).join(Scope,Asset.scope_id==Scope.id).filter(Scope.organization_id==user.organization_id).all(); vulns=db.query(VulnerabilityCandidate).join(Asset,Asset.id==VulnerabilityCandidate.asset_id).join(Scope,Scope.id==Asset.scope_id).filter(Scope.organization_id==user.organization_id).all(); return {"summary":{"total_assets":len(assets),"candidate_vulnerabilities":len(vulns)},"methodology":"Passive/public observations and synthetic demo fixtures; candidates are not verified vulnerabilities.","assets":[{"id":a.id,"kind":a.kind,"value":a.value,"first_seen_at":a.first_seen_at,"last_seen_at":a.last_seen_at} for a in assets],"vulnerability_candidates":[{"cve_id":v.cve_id,"severity":v.severity,"kev":v.kev,"confidence":v.confidence,"status":v.status,"rationale":v.rationale} for v in vulns],"limitations":["No active verification in demo mode","External provider data may be incomplete"]}
@router.get("/reports/pdf")
def report_pdf(db: Session=Depends(get_db), user=Depends(current_user)):
    assets=db.query(Asset).join(Scope,Asset.scope_id==Scope.id).filter(Scope.organization_id==user.organization_id).all()
    vulns=db.query(VulnerabilityCandidate).join(Asset,Asset.id==VulnerabilityCandidate.asset_id).join(Scope,Scope.id==Asset.scope_id).filter(Scope.organization_id==user.organization_id).all()
    lines=["Executive summary",f"Total assets: {len(assets)}",f"Candidate vulnerabilities: {len(vulns)}","Methodology: public/non-intrusive observations; candidates are not verified vulnerabilities.","Limitations: provider coverage and observations may be incomplete.","", "Assets"]
    lines.extend(f"- {a.kind}: {a.value} | first_seen={a.first_seen_at.isoformat()}" for a in assets)
    lines.append("Candidate vulnerabilities")
    lines.extend(f"- {v.cve_id} | severity={v.severity} | confidence={v.confidence} | status={v.status}" for v in vulns)
    db.add(AuditLog(organization_id=user.organization_id,actor_id=user.id,action="report_generated",target="pdf")); db.commit()
    return Response(build_pdf("LENS OSINT Report", lines), media_type="application/pdf", headers={"Content-Disposition":"attachment; filename=lens-report.pdf"})

@router.get("/reports/csv")
def report_csv(db: Session=Depends(get_db), user=Depends(current_user)):
    assets=db.query(Asset).join(Scope,Asset.scope_id==Scope.id).filter(Scope.organization_id==user.organization_id).all(); out=io.StringIO(); w=csv.writer(out); w.writerow(["id","kind","value","status","first_seen_at","last_seen_at"]); [w.writerow([a.id,a.kind,a.value,a.status,a.first_seen_at.isoformat(),a.last_seen_at.isoformat()]) for a in assets]; return StreamingResponse(iter([out.getvalue()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=lens-report.csv"})
@router.post("/security/validate-url")
def validate_url(url: str, scope_id: str, db: Session=Depends(get_db), user=Depends(require_roles("ADMIN","ANALYST"))):
    scope=db.get(Scope,scope_id)
    if not scope or scope.organization_id != user.organization_id: raise HTTPException(404,"scope not found")
    try: return {"allowed_url":validate_remote_url(url,ScopeControl(scope.root_domain,scope.authorized,scope.allow_active_http))}
    except ScopeViolation as exc: raise HTTPException(422,str(exc)) from exc
