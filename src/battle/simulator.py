# src/battle/simulator.py
import random
import math
from typing import Dict, Any, List, Tuple, Optional

# Reuse your existing client/normalizer
from src.pokemon.poke_client import PokeAPIClient
from src.pokemon.normalizer import normalize_pokemon
from src.pokemon.models import PokemonResource, MoveShort

client = PokeAPIClient()

# Basic type effectiveness chart (extendable)
TYPE_CHART = {
    # Attacking type: {defending_type: multiplier}
    "normal": {"rock": 0.5, "ghost": 0.0, "steel": 0.5},
    "fire": {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 2.0, "bug": 2.0, "rock": 0.5, "dragon": 0.5, "steel": 2.0},
    "water": {"fire": 2.0, "water": 0.5, "grass": 0.5, "ground": 2.0, "rock": 2.0, "dragon": 0.5},
    "electric": {"water": 2.0, "electric": 0.5, "grass": 0.5, "ground": 0.0, "flying": 2.0, "dragon": 0.5},
    "grass": {"fire": 0.5, "water": 2.0, "grass": 0.5, "poison": 0.5, "ground": 2.0, "flying": 0.5, "bug": 0.5, "rock": 2.0, "dragon": 0.5, "steel": 0.5},
    "ice": {"fire": 0.5, "water": 0.5, "grass": 2.0, "ice": 0.5, "ground": 2.0, "flying": 2.0, "dragon": 2.0, "steel": 0.5},
    "fighting": {"normal": 2.0, "ice": 2.0, "rock": 2.0, "dark": 2.0, "steel": 2.0, "poison": 0.5, "flying": 0.5, "psychic": 0.5, "bug": 0.5, "ghost": 0.0, "fairy": 0.5},
    "poison": {"grass": 2.0, "poison": 0.5, "ground": 0.5, "rock": 0.5, "ghost": 0.5, "steel": 0.0, "fairy": 2.0},
    "ground": {"fire": 2.0, "electric": 2.0, "grass": 0.5, "poison": 2.0, "flying": 0.0, "bug": 0.5, "rock": 2.0, "steel": 2.0},
    "flying": {"electric": 0.5, "grass": 2.0, "fighting": 2.0, "bug": 2.0, "rock": 0.5, "steel": 0.5},
    "psychic": {"fighting": 2.0, "poison": 2.0, "psychic": 0.5, "dark": 0.0, "steel": 0.5},
    "bug": {"fire": 0.5, "grass": 2.0, "fighting": 0.5, "poison": 0.5, "flying": 0.5, "psychic": 2.0, "ghost": 0.5, "dark": 2.0, "steel": 0.5, "fairy": 0.5},
    "rock": {"fire": 2.0, "ice": 2.0, "fighting": 0.5, "ground": 0.5, "flying": 2.0, "bug": 2.0, "steel": 0.5},
    "ghost": {"normal": 0.0, "psychic": 2.0, "ghost": 2.0, "dark": 0.5},
    "dragon": {"dragon": 2.0, "steel": 0.5, "fairy": 0.0},
    "dark": {"fighting": 0.5, "psychic": 2.0, "ghost": 2.0, "dark": 0.5, "fairy": 0.5},
    "steel": {"fire": 0.5, "water": 0.5, "electric": 0.5, "ice": 2.0, "rock": 2.0, "fairy": 2.0, "steel": 0.5},
    "fairy": {"fire": 0.5, "fighting": 2.0, "poison": 0.5, "dragon": 2.0, "dark": 2.0, "steel": 0.5}
}

def type_effectiveness(move_type: str, defender_types: List[str]) -> float:
    m = 1.0
    move_type = (move_type or "").lower()
    for d in defender_types:
        d = d.lower()
        if move_type in TYPE_CHART and d in TYPE_CHART[move_type]:
            m *= TYPE_CHART[move_type][d]
    return m

def choose_move(pokemon: PokemonResource, defender: PokemonResource, deterministic: bool = True) -> Optional[MoveShort]:
    """
    Choose a move prioritizing:
    1. STAB moves
    2. Super-effective moves
    3. Highest power
    """
    if not pokemon.moves:
        return None

    scored = []
    for move in pokemon.moves:
        if move.power is None:
            continue
        score = move.power

        # STAB bonus
        if move.type.lower() in [t.lower() for t in pokemon.types]:
            score *= 1.5

        # Type effectiveness bonus
        mult = type_effectiveness(move.type, defender.types)
        score *= mult

        scored.append((score, move))

    if not scored:
        return pokemon.moves[0]

    # Deterministic = pick best, else random weighted choice
    scored.sort(key=lambda x: x[0], reverse=True)
    if deterministic:
        return scored[0][1]
    else:
        return random.choice(scored[:min(3, len(scored))])

def load_pokemon(poke_input: Any) -> PokemonResource:
    """
    Accept either a name (str) or a full PokemonResource-like dict.
    Returns a PokemonResource object.
    """
    if isinstance(poke_input, dict):
        return PokemonResource(**poke_input)
    if isinstance(poke_input, PokemonResource):
        return poke_input
    # else assume name and fetch + normalize
    raw = client.get_pokemon(str(poke_input))
    return normalize_pokemon(raw)

def compute_damage(attacker: PokemonResource, defender: PokemonResource,
                   move: MoveShort, level: int, attacker_status: List[str],
                   deterministic: bool) -> Tuple[int, Dict[str, Any]]:
    """
    Returns (damage, detail_dict)
    detail_dict contains breakdown: base, stab, type_mult, final_damage
    """
    power = move.power or 0
    if power == 0:
        return 0, {"reason": "move has no power"}

    # Determine whether move is physical or special (damage_class)
    is_physical = (move.damage_class == "physical")
    # Choose attack/defense stat
    atk = attacker.base_stats["attack"] if is_physical else attacker.base_stats["special_attack"]
    defe = defender.base_stats["defense"] if is_physical else defender.base_stats["special_defense"]

    # Core damage formula (simplified)
    # base = (((2 * L / 5) + 2) * power * atk / defe) / 50 + 2
    base = (((2 * level) / 5) + 2) * power * (atk / max(1, defe))
    base = base / 50.0 + 2

    # STAB
    stab = 1.5 if (move.type and move.type.lower() in [t.lower() for t in attacker.types]) else 1.0

    # type effectiveness
    type_mult = type_effectiveness(move.type, defender.types)

    # random factor
    if deterministic:
        rand = 1.0
    else:
        rand = random.uniform(0.85, 1.0)

    modifier = stab * type_mult * rand

    # Burn halves physical attack damage (classic behavior)
    if is_physical and ("burn" in attacker_status):
        modifier *= 0.5

    damage = math.floor(base * modifier)
    if damage < 1:
        damage = 1
    detail = {
        "base": base,
        "stab": stab,
        "type_mult": type_mult,
        "rand": rand,
        "modifier": modifier,
        "final_damage": damage
    }
    return damage, detail

def apply_status_end_of_turn(pokemon: Dict[str, Any], status: List[str]) -> Tuple[int, str]:
    """
    Apply poison/burn end-of-turn damage.
    pokemon is a dict with 'max_hp' and 'current_hp'
    Returns (damage_applied, message)
    """
    damage = 0
    msg = ""
    max_hp = pokemon["max_hp"]
    if "poison" in status:
        dmg = math.floor(max_hp / 8)
        pokemon["current_hp"] -= dmg
        damage += dmg
        msg += f"Poison deals {dmg} damage. "
    if "burn" in status:
        dmg = math.floor(max_hp / 16)
        pokemon["current_hp"] -= dmg
        damage += dmg
        msg += f"Burn deals {dmg} damage. "
    return damage, msg.strip()

def simulate_battle(p1_input: Any, p2_input: Any, level: int = 50,
                    deterministic: bool = True, max_turns: int = 200) -> Dict[str, Any]:
    """
    Simulate a battle between p1 and p2.
    Returns: {
        'winner': 'p1'/'p2'/'draw',
        'log': [ ... ],
        'final_states': {...}
    }
    """
    if not deterministic:
        random.seed()

    p1 = load_pokemon(p1_input)
    p2 = load_pokemon(p2_input)

    # Initialize simple battle state
    state1 = {
        "name": p1.name,
        "max_hp": p1.base_stats["hp"],
        "current_hp": p1.base_stats["hp"],
        "types": p1.types,
        "status": [],  # burn, poison, paralysis
        "pokemon": p1
    }
    state2 = {
        "name": p2.name,
        "max_hp": p2.base_stats["hp"],
        "current_hp": p2.base_stats["hp"],
        "types": p2.types,
        "status": [],
        "pokemon": p2
    }

    log: List[str] = []
    turn = 1

    while turn <= max_turns:
        log.append(f"--- Turn {turn} ---")
        # Determine effective speeds
        s1 = p1.base_stats["speed"]
        s2 = p2.base_stats["speed"]
        if "paralysis" in state1["status"]:
            s1 = math.floor(s1 * 0.5)
        if "paralysis" in state2["status"]:
            s2 = math.floor(s2 * 0.5)

        if s1 > s2:
            order = [(state1, state2), (state2, state1)]
        elif s2 > s1:
            order = [(state2, state1), (state1, state2)]
        else:
            # speed tie
            if deterministic:
                order = [(state1, state2), (state2, state1)]
            else:
                if random.random() < 0.5:
                    order = [(state1, state2), (state2, state1)]
                else:
                    order = [(state2, state1), (state1, state2)]

        for attacker_state, defender_state in order:
            if attacker_state["current_hp"] <= 0 or defender_state["current_hp"] <= 0:
                continue  # skip if someone has fainted mid-turn

            attacker: PokemonResource = attacker_state["pokemon"]
            defender: PokemonResource = defender_state["pokemon"]

            # Choose move
            move = choose_move(attacker)
            if not move:
                log.append(f"{attacker_state['name']} has no moves and struggles (skip).")
                continue

            # Paralysis check: 25% chance to be fully paralyzed
            if "paralysis" in attacker_state["status"]:
                stuck_roll = 0.25 if deterministic else random.random()
                if (not deterministic and random.random() < 0.25) or (deterministic and stuck_roll <= 0.25):
                    log.append(f"{attacker_state['name']} is paralyzed and can't move!")
                    continue

            # Execute move
            damage, detail = compute_damage(attacker, defender, move, level, attacker_state["status"], deterministic)
            defender_state["current_hp"] -= damage
            log.append(f"{attacker_state['name']} uses {move.name} (power={move.power}). Damage: {damage}. Detail: {detail}")
            log.append(f"{defender_state['name']} HP: {max(0, defender_state['current_hp'])}/{defender_state['max_hp']}")

            if defender_state["current_hp"] <= 0:
                log.append(f"{defender_state['name']} fainted!")
                winner = attacker_state["name"]
                return {"winner": winner, "log": log, "final_states": {"p1": state1, "p2": state2}}

        # End-of-turn effects
        d1, msg1 = apply_status_end_of_turn(state1, state1["status"])
        if d1:
            log.append(f"{state1['name']} end-of-turn: {msg1} Now HP: {max(0, state1['current_hp'])}/{state1['max_hp']}")
        d2, msg2 = apply_status_end_of_turn(state2, state2["status"])
        if d2:
            log.append(f"{state2['name']} end-of-turn: {msg2} Now HP: {max(0, state2['current_hp'])}/{state2['max_hp']}")

        if state1["current_hp"] <= 0 and state2["current_hp"] <= 0:
            log.append("Both Pokémon fainted — draw.")
            return {"winner": "draw", "log": log, "final_states": {"p1": state1, "p2": state2}}
        if state1["current_hp"] <= 0:
            return {"winner": state2["name"], "log": log, "final_states": {"p1": state1, "p2": state2}}
        if state2["current_hp"] <= 0:
            return {"winner": state1["name"], "log": log, "final_states": {"p1": state1, "p2": state2}}

        turn += 1

    # max turns reached -> draw
    log.append("Max turns reached -> draw.")
    return {"winner": "draw", "log": log, "final_states": {"p1": state1, "p2": state2}}
