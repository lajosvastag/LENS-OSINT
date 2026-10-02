from app.collectors.base import DataSourceAdapter
class ProviderUnavailable(RuntimeError): pass
class ShodanAdapter(DataSourceAdapter):
    def __init__(self, api_key=None): self.api_key=api_key
    def get_source_name(self): return "shodan"
    def health_check(self): return bool(self.api_key)
    def collect(self,target,**kwargs):
        if not self.api_key: raise ProviderUnavailable("provider_unavailable: SHODAN_API_KEY is not configured")
        raise ProviderUnavailable("provider_unavailable: adapter requires explicit provider integration")
