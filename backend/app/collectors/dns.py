import dns.resolver
from app.collectors.base import DataSourceAdapter, CollectedItem
class DNSAdapter(DataSourceAdapter):
    TYPES=("A","AAAA","CNAME","MX","NS","TXT","SOA")
    def get_source_name(self): return "dns"
    def health_check(self): return True
    def collect(self,target,**kwargs):
        out=[]
        for rtype in self.TYPES:
            try:
                for answer in dns.resolver.resolve(target,rtype):
                    value=str(answer).rstrip('.')
                    kind="ip" if rtype in {"A","AAAA"} else "dns_record"
                    out.append(CollectedItem(kind,value,"dns",f"dns://{target}/{rtype}",value,0.9))
            except (dns.resolver.NoAnswer,dns.resolver.NXDOMAIN,dns.resolver.NoNameservers,dns.exception.Timeout): pass
        return out
