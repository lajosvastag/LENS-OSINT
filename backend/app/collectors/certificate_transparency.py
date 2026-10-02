"""Certificate Transparency adapter using the public crt.sh JSON interface.

The adapter only discovers certificate names. A discovered name remains an
observed_asset until corroborated by DNS/HTTP evidence.
"""
import httpx
from app.collectors.base import CollectedItem, DataSourceAdapter

class CertificateTransparencyAdapter(DataSourceAdapter):
    endpoint = "https://crt.sh/"
    def get_source_name(self) -> str: return "certificate-transparency"
    def health_check(self) -> bool: return True
    def collect(self, target: str, **kwargs) -> list[CollectedItem]:
        timeout = kwargs.get("timeout", 5.0)
        response = httpx.get(self.endpoint, params={"q": f"%.{target}", "output": "json"}, timeout=timeout)
        response.raise_for_status()
        items: list[CollectedItem] = []
        seen: set[str] = set()
        for row in response.json():
            names = str(row.get("name_value", "")).splitlines()
            for name in names:
                normalized = name.strip().lower().lstrip("*.").rstrip(".")
                if normalized == target or normalized.endswith("." + target):
                    if normalized not in seen:
                        seen.add(normalized)
                        items.append(CollectedItem("subdomain", normalized, self.get_source_name(), str(response.url), normalized, 0.70, str(row.get("id", ""))))
        return items
