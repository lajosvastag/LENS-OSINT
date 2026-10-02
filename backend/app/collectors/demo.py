from app.collectors.base import DataSourceAdapter, CollectedItem
class DemoAdapter(DataSourceAdapter):
    def get_source_name(self): return "demo-fixture"
    def health_check(self): return True
    def collect(self, target, **kwargs):
        return [
            CollectedItem("domain",target,"demo-fixture",None,target,1.0),
            CollectedItem("subdomain",f"api.{target}","demo-fixture",None,f"api.{target}",0.70),
            CollectedItem("subdomain",f"portal.{target}","demo-fixture",None,f"portal.{target}",0.70),
            CollectedItem("ip","203.0.113.10","demo-fixture",None,"203.0.113.10",0.85),
            CollectedItem("technology","nginx 1.24","demo-fixture",None,"nginx 1.24",0.60),
        ]
