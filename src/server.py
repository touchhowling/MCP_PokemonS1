import os
import json
from fastapi import FastAPI, HTTPException, Query
from fastapi import Body, HTTPException
from typing import Any, Dict
from typing import List
from src.pokemon.models import PokemonResource, MoveShort
from src.pokemon.poke_client import PokeAPIClient
from src.pokemon.normalizer import normalize_pokemon
from fastapi import Body
from src.battle.simulator import simulate_battle

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

app = FastAPI(title="MCP Pokémon Server")
client = PokeAPIClient()

def load_from_cache(name: str):
    """Check if Pokémon JSON is cached locally."""
    path = os.path.join(DATA_DIR, f"{name.lower()}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

def save_to_cache(name: str, data: dict):
    """Save normalized Pokémon JSON to cache."""
    path = os.path.join(DATA_DIR, f"{name.lower()}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

@app.get("/resources/pokemon/{name}", response_model=PokemonResource)
def get_pokemon_resource(name: str):
    try:
        # 1. Try cache
        cached = load_from_cache(name)
        if cached:
            return cached

        # 2. Fallback to PokéAPI
        raw = client.get_pokemon(name)
        normalized = normalize_pokemon(raw)
        data = normalized.dict()

        # 3. Save to cache
        save_to_cache(normalized.name, data)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/resources/move/{name}", response_model=MoveShort)
def get_move_resource(name: str):
    try:
        move_raw = client.get_move(name)
        return MoveShort(
            name=move_raw["name"],
            type=move_raw["type"]["name"],
            power=move_raw.get("power"),
            accuracy=move_raw.get("accuracy"),
            pp=move_raw.get("pp"),
            damage_class=move_raw["damage_class"]["name"],
            short_effect=move_raw["effect_entries"][0]["short_effect"]
                if move_raw.get("effect_entries") else None,
            move_resource_uri=f"/resources/move/{move_raw['name']}"
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/resources/pokemon", response_model=List[str])
def search_pokemon(search: str = Query(..., description="Search substring in Pokémon names")):
    try:
        cached_names = [f[:-5] for f in os.listdir(DATA_DIR) if f.endswith(".json")]
        filtered = [n for n in cached_names if search.lower() in n.lower()]
        if filtered:
            return filtered

        # fallback to PokeAPI
        import requests
        url = f"{client.base_url}/pokemon?limit=2000"
        resp = requests.get(url)
        resp.raise_for_status()
        all_pokemon = [p["name"] for p in resp.json()["results"]]
        return [n for n in all_pokemon if search.lower() in n.lower()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/battle", response_model=None)  
def battle_tool(payload: Dict[str, Any] = Body(...)):
    """
    Run a battle simulation between two Pokémon.
    """
    try:
        p1 = payload.get("pokemon1")
        p2 = payload.get("pokemon2")
        level = int(payload.get("level", 50))
        deterministic = bool(payload.get("deterministic", True))
        result = simulate_battle(p1, p2, level=level, deterministic=deterministic)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/manifest")
def get_manifest():
    import json
    import os
    manifest_path = os.path.join(os.path.dirname(__file__), "mcp_manifest.json")
    with open(manifest_path, "r") as f:
        return json.load(f)