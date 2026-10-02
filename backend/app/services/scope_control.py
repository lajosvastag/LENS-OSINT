from dataclasses import dataclass
from ipaddress import ip_address
import socket
from urllib.parse import urlparse

class ScopeViolation(ValueError): pass
@dataclass(frozen=True)
class ScopeControl:
    root_domain: str
    authorized: bool
    allow_active_http: bool=False
    def normalize_domain(self, value: str) -> str:
        value=value.strip().lower().rstrip('.')
        if not value or len(value)>253 or value.startswith('.') or '..' in value: raise ScopeViolation("invalid domain")
        labels=value.split('.')
        if any(not label or len(label)>63 or not all(c.isalnum() or c=='-' for c in label) or label.startswith('-') or label.endswith('-') for label in labels): raise ScopeViolation("invalid domain")
        if value != self.root_domain and not value.endswith('.'+self.root_domain): raise ScopeViolation("domain outside authorized scope")
        return value
    def assert_active_allowed(self):
        if not self.authorized or not self.allow_active_http: raise ScopeViolation("active collection requires authorized scope")

def resolve_and_validate_host(host: str) -> list[str]:
    try: infos=socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc: raise ScopeViolation("host resolution failed") from exc
    ips=sorted({item[4][0] for item in infos})
    for raw in ips:
        ip=ip_address(raw)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or raw in {"169.254.169.254","100.100.100.200"}: raise ScopeViolation("destination resolves to blocked network")
    return ips

def validate_remote_url(url: str, scope: ScopeControl) -> str:
    parsed=urlparse(url)
    if parsed.scheme not in {"http","https"} or not parsed.hostname: raise ScopeViolation("only HTTP(S) URLs are allowed")
    scope.normalize_domain(parsed.hostname)
    scope.assert_active_allowed()
    resolve_and_validate_host(parsed.hostname)
    return url
