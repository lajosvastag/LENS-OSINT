from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health(): assert client.get("/health").json()["status"]=="ok"
def test_demo_and_login():
    r=client.post("/api/v1/demo/seed"); assert r.status_code==200
    r=client.post("/api/v1/auth/login",json={"email":"admin@lens.local","password":"ChangeMe123!"}); assert r.status_code==200
