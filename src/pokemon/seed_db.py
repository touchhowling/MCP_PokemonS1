import json
import os
from src.pokemon.poke_client import PokeAPIClient
from src.pokemon.normalizer import normalize_pokemon

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def seed(limit: int = 151):
    client = PokeAPIClient()
    for i in range(1, limit + 1):
        try:
            raw = client.get_pokemon(i)
            normalized = normalize_pokemon(raw)
            out_path = os.path.join(OUTPUT_DIR, f"{normalized.name}.json")
            with open(out_path, "w") as f:
                json.dump(normalized.dict(), f, indent=2)
            print(f"Seeded {normalized.name}")
        except Exception as e:
            print(f"Failed to seed {i}: {e}")

if __name__ == "__main__":
    seed(151)  # Kanto Pokémon
