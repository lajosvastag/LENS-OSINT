"""Low-impact HTTP metadata collector. SSRF validation is mandatory."""
import re
import httpx
from app.collectors.base import CollectedItem, DataSourceAdapter
from app.services.scope_control import ScopeControl, validate_remote_url

class HTTPMetadataAdapter(DataSourceAdapter):
    def get_source_name(self) -> str: return "http-metadata"
    def health_check(self) -> bool: return True
    def collect(self, target: str, **kwargs) -> list[CollectedItem]:
        scope: ScopeControl = kwargs["scope"]
        url = validate_remote_url(target, scope)
        response = httpx.get(url, timeout=kwargs.get("timeout", 5.0), follow_redirects=False, headers={"User-Agent": "LENS-OSINT/0.1"})
        items = [CollectedItem("http_observation", str(response.status_code), self.get_source_name(), url, str(response.status_code), 0.95)]
        title = re.search(r"<title[^>]*>(.*?)</title>", response.text[:200_000], re.I | re.S)
        if title: items.append(CollectedItem("page_title", " ".join(title.group(1).split()), self.get_source_name(), url, " ".join(title.group(1).split()), 0.85))
        server = response.headers.get("server")
        if server: items.append(CollectedItem("technology", server, self.get_source_name(), url, server.lower(), 0.45))
        return items
