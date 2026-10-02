from types import SimpleNamespace
from app.collectors.certificate_transparency import CertificateTransparencyAdapter
from app.collectors.rdap import RDAPAdapter
from app.collectors.http_metadata import HTTPMetadataAdapter
from app.services.scope_control import ScopeControl, ScopeViolation

def test_ct_normalizes_and_deduplicates(monkeypatch):
    response = SimpleNamespace(url="https://crt.sh/?q=x", json=lambda: [{"id": 1, "name_value": "API.Example.com\n*.api.example.com"}], raise_for_status=lambda: None)
    monkeypatch.setattr("httpx.get", lambda *a, **k: response)
    items = CertificateTransparencyAdapter().collect("example.com")
    assert [x.normalized_value for x in items] == ["api.example.com"]
    assert items[0].confidence == 0.70

def test_rdap_404_is_empty(monkeypatch):
    response = SimpleNamespace(status_code=404)
    monkeypatch.setattr("httpx.get", lambda *a, **k: response)
    assert RDAPAdapter().collect("example.com") == []

def test_http_adapter_requires_scope(monkeypatch):
    monkeypatch.setattr("httpx.get", lambda *a, **k: SimpleNamespace(status_code=200, text="<title>Example</title>", headers={}))
    with __import__("pytest").raises(ScopeViolation):
        HTTPMetadataAdapter().collect("https://example.com", scope=ScopeControl("example.com", False, False))
