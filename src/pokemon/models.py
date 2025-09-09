from typing import List, Optional, Dict
from pydantic import BaseModel

class MoveShort(BaseModel):
    name: str
    type: Optional[str]
    power: Optional[int]
    accuracy: Optional[int]
    pp: Optional[int]
    damage_class: Optional[str]
    short_effect: Optional[str]
    move_resource_uri: Optional[str]

class PokemonResource(BaseModel):
    id: int
    name: str
    types: List[str]
    base_stats: Dict[str, int]   # hp, attack, defense, special_attack, special_defense, speed
    abilities: List[str]
    moves: List[MoveShort]
    evolution_chain: List[str]
    height: Optional[int]
    weight: Optional[int]
    sprite_url: Optional[str]
