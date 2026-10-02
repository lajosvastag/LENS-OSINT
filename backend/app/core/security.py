from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from app.core.config import settings

pwd=CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
def hash_password(value): return pwd.hash(value)
def verify_password(value, hashed): return pwd.verify(value, hashed)
def create_token(user_id, role, organization_id):
    return jwt.encode({"sub":user_id,"role":role,"org":organization_id,"exp":datetime.now(timezone.utc)+timedelta(hours=8)}, settings.secret_key, algorithm="HS256")
def decode_token(token):
    try: return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as exc: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token") from exc
