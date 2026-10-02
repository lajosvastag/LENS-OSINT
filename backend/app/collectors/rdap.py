"""RDAP adapter. rdap.org provides standards-based redirects to authoritative servers."""
import httpx
from app.collectors.base import CollectedItem, DataSourceAdapter

class RDAPAdapter(DataSourceAdapter):
    endpoint = "https://rdap.org/domain/"
    def get_source_name(self) -> str: return "rdap"
    def health_check(self) -> bool: return True
    def collect(self, target: str, **kwargs) -> list[CollectedItem]:
        response = httpx.get(self.endpoint + target, timeout=kwargs.get("timeout", 5.0), follow_redirects=True)
        if response.status_code == 404: return []
        response.raise_for_status()
        data = response.json()
        handle = str(data.get("handle") or data.get("ldhName") or target)
        return [CollectedItem("rdap_record", handle, self.get_source_name(), str(response.url), handle, 0.90, data.get("objectClassName"))]
