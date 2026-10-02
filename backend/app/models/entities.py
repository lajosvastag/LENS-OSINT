from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import String, Text, Float, Boolean, DateTime, ForeignKey, JSON, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.db import Base

def now(): return datetime.now(timezone.utc)
def uid(): return str(uuid4())

class User(Base):
    __tablename__="users"
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid)
    email: Mapped[str]=mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    role: Mapped[str]=mapped_column(String(20), default="VIEWER")
    organization_id: Mapped[str|None]=mapped_column(ForeignKey("organizations.id"))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class Organization(Base):
    __tablename__="organizations"
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid)
    name: Mapped[str]=mapped_column(String(200))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class Scope(Base):
    __tablename__="scopes"
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str]=mapped_column(ForeignKey("organizations.id"), index=True)
    root_domain: Mapped[str]=mapped_column(String(253), index=True)
    authorized: Mapped[bool]=mapped_column(Boolean, default=False)
    allow_active_http: Mapped[bool]=mapped_column(Boolean, default=False)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class Asset(Base):
    __tablename__="assets"
    __table_args__=(UniqueConstraint("scope_id","kind","value"), Index("ix_assets_scope_kind","scope_id","kind"))
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid)
    scope_id: Mapped[str]=mapped_column(ForeignKey("scopes.id"), index=True)
    kind: Mapped[str]=mapped_column(String(40))
    value: Mapped[str]=mapped_column(String(1024))
    status: Mapped[str]=mapped_column(String(30), default="observed_asset")
    first_seen_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    last_seen_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class Evidence(Base):
    __tablename__="evidences"
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid)
    asset_id: Mapped[str|None]=mapped_column(ForeignKey("assets.id"), index=True)
    source: Mapped[str]=mapped_column(String(100))
    source_url: Mapped[str|None]=mapped_column(String(2048))
    collected_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    raw_reference: Mapped[str|None]=mapped_column(Text)
    normalized_value: Mapped[str]=mapped_column(Text)
    confidence: Mapped[float]=mapped_column(Float)
    collector: Mapped[str]=mapped_column(String(100))
    payload_hash: Mapped[str|None]=mapped_column(String(64))

class Relationship(Base):
    __tablename__="relationships"
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid)
    scope_id: Mapped[str]=mapped_column(ForeignKey("scopes.id"), index=True)
    source_asset_id: Mapped[str]=mapped_column(ForeignKey("assets.id"))
    target_asset_id: Mapped[str]=mapped_column(ForeignKey("assets.id"))
    relation_type: Mapped[str]=mapped_column(String(60))
    confidence: Mapped[float]=mapped_column(Float)
    source: Mapped[str]=mapped_column(String(100))
    observed_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class ScanJob(Base):
    __tablename__="scan_jobs"
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid)
    scope_id: Mapped[str]=mapped_column(ForeignKey("scopes.id"), index=True)
    status: Mapped[str]=mapped_column(String(20), default="PENDING")
    progress: Mapped[int]=mapped_column(default=0)
    error: Mapped[str|None]=mapped_column(Text)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
    finished_at: Mapped[datetime|None]=mapped_column(DateTime(timezone=True))

class VulnerabilityCandidate(Base):
    __tablename__="vulnerability_candidates"
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid)
    asset_id: Mapped[str]=mapped_column(ForeignKey("assets.id"), index=True)
    cve_id: Mapped[str]=mapped_column(String(30))
    severity: Mapped[str|None]=mapped_column(String(20))
    kev: Mapped[bool]=mapped_column(Boolean, default=False)
    confidence: Mapped[float]=mapped_column(Float)
    rationale: Mapped[str]=mapped_column(Text)
    status: Mapped[str]=mapped_column(String(40), default="candidate_vulnerability")
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)

class AuditLog(Base):
    __tablename__="audit_logs"
    id: Mapped[str]=mapped_column(String(36), primary_key=True, default=uid)
    organization_id: Mapped[str|None]=mapped_column(String(36), index=True)
    actor_id: Mapped[str|None]=mapped_column(String(36))
    action: Mapped[str]=mapped_column(String(100))
    target: Mapped[str|None]=mapped_column(String(255))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), default=now)
