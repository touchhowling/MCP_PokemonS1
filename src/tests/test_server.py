import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import pytest
from fastapi.testclient import TestClient
from src.server import app

client = TestClient(app)

def test_get_pokemon_endpoint():
    response = client.get("/resources/pokemon/pikachu")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "pikachu"
    assert "types" in data
    assert "base_stats" in data

def test_search_endpoint():
    response = client.get("/resources/pokemon?search=char")
    assert response.status_code == 200
    results = response.json()
    # ensure it returns at least one known char* Pokémon
    assert any(r in results for r in ["charmander", "charmeleon", "charizard"])


def test_move_endpoint():
    response = client.get("/resources/move/thunderbolt")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "thunderbolt"
    assert "power" in data
