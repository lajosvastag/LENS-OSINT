from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.db import Base,engine
from app.api import router
from app import models

Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.app_name,version="0.1.0",description="Defensive OSINT inventory with evidence and explicit uncertainty")
app.add_middleware(CORSMiddleware,allow_origins=[x.strip() for x in settings.cors_origins.split(',')],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(router)
@app.get("/health")
def health(): return {"status":"ok","service":"lens-api"}
