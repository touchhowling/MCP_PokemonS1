import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from fastapi.testclient import TestClient
from src.server import app

client = TestClient(app)

def test_battle_draw_or_winner():
    payload = {"pokemon1": "pikachu", "pokemon2": "eevee", "level": 50, "deterministic": True}
    r = client.post("/tools/battle", json=payload)
    assert r.status_code == 200
    j = r.json()
    assert "winner" in j and "log" in j
    assert isinstance(j["log"], list)
