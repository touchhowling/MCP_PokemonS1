# 🐉 MCP Pokémon Server

An **MCP-compliant server** that exposes **Pokémon data** from [PokéAPI](https://pokeapi.co) and provides a **battle simulator tool**.  
Built with **FastAPI**, **Pydantic**, and **Docker**, this project demonstrates how MCP manifests and tools can make APIs auto-discoverable and LLM-friendly.

---

## ✨ Features

### 📊 Pokémon Data Endpoints
- `GET /resources/pokemon/{name}` → Fetch normalized Pokémon data (stats, types, abilities, moves, evolution chain, sprite)
- `GET /resources/move/{id}` → Get detailed move info (type, power, accuracy, effect)
- `GET /resources/pokemon?search={query}` → Search Pokémon by substring  
  - Uses **local cache** if available  
  - Falls back to **PokéAPI** if not cached  

### ⚔️ Battle Simulator Tool
- `POST /tools/battle` → Simulate a Pokémon battle  
- Returns structured, turn-by-turn battle logs in JSON format  

### 📦 MCP Manifest
- `GET /manifest` → Exposes a machine-readable JSON manifest describing all **resources** and **tools**  
- Enables **auto-discovery** for LLMs and MCP clients

---

## 🗂️ Project Structure

\`\`\`
mcp-pokemon-server/
├─ src/
│  ├─ server.py            # FastAPI entrypoint
│  ├─ pokemon/             # Pokémon data client, normalizer, models
│  ├─ battle/              # Battle simulator logic
│  ├─ mcp_manifest.json    # MCP manifest
│
├─ tests/                  # Pytest unit + integration tests
├─ requirements.txt
├─ Dockerfile
├─ .dockerignore
└─ README.md
\`\`\`

---

## 🚀 Getting Started

### 1. Clone & Install
\`\`\`bash
git clone https://github.com/yourusername/mcp-pokemon-server.git
cd mcp-pokemon-server
pip install -r requirements.txt
\`\`\`

### 2. Run Server
\`\`\`bash
uvicorn src.server:app --reload
\`\`\`

Server runs at:  
👉 http://127.0.0.1:8000  

Swagger UI docs at:  
👉 http://127.0.0.1:8000/docs  

---

## 🔎 Usage Examples

### Fetch a Pokémon
\`\`\`bash
curl http://127.0.0.1:8000/resources/pokemon/pikachu
\`\`\`

### Fetch a Move
\`\`\`bash
curl http://127.0.0.1:8000/resources/move/25
\`\`\`

### Search Pokémon
\`\`\`bash
curl "http://127.0.0.1:8000/resources/pokemon?search=char"
\`\`\`

### Simulate a Battle
\`\`\`bash
curl -X POST http://127.0.0.1:8000/tools/battle \
  -H "Content-Type: application/json" \
  -d '{"pokemon1":"charizard","pokemon2":"blastoise","level":50,"deterministic":true}'
\`\`\`

Response (simplified):
\`\`\`json
{
  "winner": "blastoise",
  "log": [
    {"turn":1,"actor":"charizard","move":"flamethrower","damage":30,"target":"blastoise","hp_after":120},
    {"turn":1,"actor":"blastoise","move":"hydro-pump","damage":65,"target":"charizard","hp_after":0,"action":"faint"}
  ]
}
\`\`\`

---

## 📑 MCP Manifest

Visit http://127.0.0.1:8000/manifest  

Example:
\`\`\`json
{
  "name": "pokemon-data",
  "version": "0.1.0",
  "description": "MCP server exposing Pokémon data from PokéAPI with caching and battle simulation.",
  "resources": [
    {"name":"pokemon","endpoint":"/resources/pokemon/{name}"},
    {"name":"move","endpoint":"/resources/move/{name}"},
    {"name":"pokemon-search","endpoint":"/resources/pokemon?search={query}"}
  ],
  "tools": [
    {"name":"battle-simulator","endpoint":"/tools/battle"}
  ]
}
\`\`\`

---

## 🧪 Testing

Run tests with:
\`\`\`bash
pytest -v
\`\`\`

Covers:
- Models
- Endpoints
- Battle simulation


## 💡 Future Improvements
- Smarter move selection (AI strategy)  
- More status effects (sleep, freeze, confusion)  
- Support for items & abilities  
- Multi-Pokémon battles  

---

## 👨‍💻 Author
Built as a learning project to explore **MCP**, **API design**, and **Pokémon mechanics**.  
Feedback & contributions welcome!
