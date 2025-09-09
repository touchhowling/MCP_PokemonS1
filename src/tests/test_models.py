import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from src.pokemon.models import PokemonResource, MoveShort

def test_pokemon_model():
    move = MoveShort(
        name="tackle",
        type="normal",
        power=40,
        accuracy=100,
        pp=35,
        damage_class="physical",
        short_effect="Inflicts damage.",
        move_resource_uri="/resources/move/tackle"
    )
    pokemon = PokemonResource(
        id=25,
        name="pikachu",
        types=["electric"],
        base_stats={"hp": 35, "attack": 55, "defense": 40, "special_attack": 50, "special_defense": 50, "speed": 90},
        abilities=["static", "lightning-rod"],
        moves=[move],
        evolution_chain=["pichu", "pikachu", "raichu"],
        height=4,
        weight=60,
        sprite_url="http://example.com/pikachu.png"
    )
    assert pokemon.name == "pikachu"
    assert pokemon.types[0] == "electric"
    assert pokemon.moves[0].name == "tackle"
