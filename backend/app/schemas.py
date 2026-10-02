from pydantic import BaseModel, Field
class LoginIn(BaseModel): email: str; password: str
class TokenOut(BaseModel): access_token: str; token_type: str="bearer"
class OrgIn(BaseModel): name: str = Field(min_length=2,max_length=200)
class ScopeIn(BaseModel): organization_id: str; root_domain: str; authorized: bool=False; allow_active_http: bool=False
class ScanIn(BaseModel): scope_id: str
