from typing import List, Dict
from src.pokemon.models import PokemonResource, MoveShort
from src.pokemon.poke_client import PokeAPIClient
import traceback

client = PokeAPIClient()

def _parse_evolution_chain(chain: Dict) -> List[str]:
    """Flatten evolution chain into a list of names."""
    result = []

    def traverse(node):
        result.append(node["species"]["name"])
        for evo in node.get("evolves_to", []):
            traverse(evo)

    traverse(chain["chain"])
    return result

def normalize_pokemon(raw: Dict) -> PokemonResource:
    """Convert PokéAPI raw JSON into our PokemonResource schema."""

    # Base stats
    stats = {s["stat"]["name"]: s["base_stat"] for s in raw["stats"]}
    base_stats = {
        "hp": stats.get("hp", 0),
        "attack": stats.get("attack", 0),
        "defense": stats.get("defense", 0),
        "special_attack": stats.get("special-attack", 0),
        "special_defense": stats.get("special-defense", 0),
        "speed": stats.get("speed", 0),
    }

    # Types
    types = [t["type"]["name"] for t in raw["types"]]

    # Abilities
    abilities = [a["ability"]["name"] for a in raw["abilities"]]

    # Moves (limit to first 5 with details)
    moves: List[MoveShort] = []
    for move_entry in raw["moves"][:5]:
        move_name = move_entry["move"]["name"]
        try:
            move_raw = client.get_move(move_name)
            moves.append(
                MoveShort(
                    name=move_raw["name"],
                    type=move_raw["type"]["name"],
                    power=move_raw.get("power"),
                    accuracy=move_raw.get("accuracy"),
                    pp=move_raw.get("pp"),
                    damage_class=move_raw["damage_class"]["name"],
                    short_effect=move_raw["effect_entries"][0]["short_effect"]
                        if move_raw.get("effect_entries") else None,
                    move_resource_uri=f"/resources/move/{move_name}"
                )
            )
        except Exception:
            moves.append(
                MoveShort(
                    name=move_name,
                    type=None,
                    power=None,
                    accuracy=None,
                    pp=None,
                    damage_class=None,
                    short_effect=None,
                    move_resource_uri=f"/resources/move/{move_name}"
                )
            )

    # Evolution chain
    try:
        species = client.get_species(raw["id"])
        # print(f"[DEBUG] species keys: {species.keys()}", flush=True)
        # print(f"[DEBUG] evolution_chain URL: {species.get('evolution_chain')}", flush=True)

        evo_chain_url = species["evolution_chain"]["url"]
        evo_chain_id = evo_chain_url.rstrip("/").split("/")[-1]
        # print(f"[DEBUG] evo_chain_id = {evo_chain_id}", flush=True)

        evo_raw = client.get_evolution_chain(evo_chain_id)
        # print(f"[DEBUG] evo_raw keys: {evo_raw.keys()}", flush=True)

        evolution_chain = _parse_evolution_chain(evo_raw)
        # print(f"[DEBUG] parsed evolution_chain: {evolution_chain}", flush=True)
    except Exception as e:
        # print(f"[DEBUG] Evolution chain fetch failed: {type(e).__name__}: {e}", flush=True)
        # traceback.print_exc()
        evolution_chain = []
    return PokemonResource(
        id=raw["id"],
        name=raw["name"],
        types=types,
        base_stats=base_stats,
        abilities=abilities,
        moves=moves,
        evolution_chain=evolution_chain,
        height=raw.get("height"),
        weight=raw.get("weight"),
        sprite_url=raw["sprites"]["front_default"] if raw.get("sprites") else None,
    )
