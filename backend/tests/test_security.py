import pytest
from app.services.scope_control import ScopeControl,ScopeViolation
def test_domain_scope():
    s=ScopeControl("example.com",True)
    assert s.normalize_domain("API.Example.com.")=="api.example.com"
    with pytest.raises(ScopeViolation): s.normalize_domain("evil.com")
def test_active_requires_authorization():
    with pytest.raises(ScopeViolation): ScopeControl("example.com",False,False).assert_active_allowed()
def test_private_url_rejected():
    with pytest.raises(ScopeViolation): __import__("app.services.scope_control",fromlist=["validate_remote_url"]).validate_remote_url("http://127.0.0.1/admin",ScopeControl("example.com",True,True))
