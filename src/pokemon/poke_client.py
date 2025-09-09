import requests
from functools import lru_cache
from typing import Dict, Any
import logging
logger = logging.getLogger(__name__)

POKEAPI_BASE = "https://pokeapi.co/api/v2"

class PokeAPIClient:
    def __init__(self, base_url: str = POKEAPI_BASE):
        self.base_url = base_url

    @lru_cache(maxsize=256)
    def get_pokemon(self, name_or_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/pokemon/{name_or_id.lower()}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    @lru_cache(maxsize=512)
    def get_move(self, name_or_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/move/{name_or_id.lower()}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    @lru_cache(maxsize=256)
    def get_species(self, name_or_id: str) -> Dict[str, Any]:
        name_or_id = str(name_or_id).lower()
        url = f"{self.base_url}/pokemon-species/{name_or_id}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    @lru_cache(maxsize=128)
    def get_evolution_chain(self, chain_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/evolution-chain/{chain_id}"
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()
# At the bottom of poke_client.py
# if __name__ == "__main__":
#     client = PokeAPIClient()
#     data = client.get_evolution_chain("eevee")
#     print(data)
