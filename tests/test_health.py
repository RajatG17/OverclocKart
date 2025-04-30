import pathlib, sys
from fastapi.testclient import TestClient


gateway_dir = pathlib.Path(__file__).resolve().parents[1] / "api-gateway"
sys.path.append(str(gateway_dir))

from main import app          # api-gateway/main.py exports `app`

client = TestClient(app)

def test_gateway_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}