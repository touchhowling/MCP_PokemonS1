# MCP Pokémon Server

An MCP-compliant server that provides Pokémon data (via PokéAPI) and a battle simulator.

## Features
- `/resources/pokemon/{name}` → normalized Pokémon data
- `/resources/move/{name}` → move data
- `/resources/pokemon?search={query}` → search Pokémon
- `/tools/battle` → simulate a battle between two Pokémon
- Caching support (`seed_db.py`) for offline usage
- Structured MCP manifest (`/manifest`)

## Run
```bash
pip install -r requirements.txt
uvicorn src.server:app --reload
