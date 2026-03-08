# Web4PDA — Parcel Digital Agents

> **Open Metaverse Browser + MCP Parcel Agents + USDx Contracts**
> Every parcel is an agent. Every agent can trade, communicate, and optimize — in USD via x402 protocol.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)

---

## Overview

Web4PDA is an open spatial operating system that gives every real-world parcel its own AI agent. Each parcel agent can:

- **Optimize** itself using open data (OSM, utilities, Stikk check-ins)
- **Trade** via USDx stablecoin contracts using the x402 protocol
- **Communicate** with other agents (Stikk, utility operators, planners)
- **Plug into** any MCP-compatible AI runtime via Route.X

---

## Architecture

```
XR Client / AI Copilot
        |
  Route.X MCP Router (port 4000)
  /mcp/tool — unified tool interface
        |
   ┌───────────┬───────────┬───────────┐
   |           |           |           |
Spatial   Parcel    Exchange   Stikk
Fabric    Agent     Server     Loyalty
:3001     :3002     :3003      :3004
   |           |           |
GeoJSON  In-memory  USDx/x402
OSM/OGC  Store      Wallets+Contracts
```

---

## Repo Structure

```
Web4PDA/
├── README.md
├── corridor-config.json          # SF Frontier Corridor config
├── mcp-tools.parcel-os.json      # Unified MCP tool schema
├── src/
│   ├── servers/
│   │   ├── SpatialFabricServer.py   # Parcels, layers, routes (FastAPI :3001)
│   │   ├── ParcelAgentServer.py     # Agent state, goals (FastAPI :3002)
│   │   └── ExchangeServer.py        # USDx wallets, x402 contracts (FastAPI :3003)
│   ├── routex/
│   │   ├── router.py                # Route.X unified MCP front door (:4000)
│   │   └── tool_routes.py           # Tool → server routing table
│   ├── agents/
│   │   ├── ParcelOptimizationGraph.py  # LangGraph-style optimization loop
│   │   └── nanda_agent_facts.json      # NANDA registry entries
│   └── data/
│       ├── sf-parcels.geojson
│       ├── sf-underground.geojson
│       └── sf-stikk-spots.geojson
└── prompts/
    └── system-prompt.txt           # Spatial Copilot system prompt
```

---

## Quick Start

```bash
# Install dependencies
pip install fastapi uvicorn httpx pydantic

# Start all servers (4 terminals or use a process manager)
uvicorn src.servers.SpatialFabricServer:app --port 3001 --reload
uvicorn src.servers.ParcelAgentServer:app --port 3002 --reload
uvicorn src.servers.ExchangeServer:app --port 3003 --reload
uvicorn src.routex.router:app --port 4000 --reload

# Test the Route.X MCP front door
curl -X POST http://localhost:4000/mcp/tool \
  -H "Content-Type: application/json" \
  -d '{"tool_name": "parcel_get_place_hierarchy", "args": {"lat": 37.7815, "lon": -122.41}}'

# Run parcel optimization for demo parcel
python src/agents/ParcelOptimizationGraph.py
```

---

## MCP Tool Reference

| Tool | Server | Description |
|------|--------|-------------|
| `parcel_get_place_hierarchy` | SpatialFabric | Resolve lat/lon to parcel_id |
| `parcel_get_parcel` | SpatialFabric | Get parcel geometry + attributes |
| `parcel_list_layers` | SpatialFabric | List available map layers |
| `parcel_get_features` | SpatialFabric | GeoJSON features from a layer |
| `parcel_plan_route_between_parcels` | SpatialFabric | Walk/drive route |
| `parcel_get_agent_state` | ParcelAgent | Metrics + suggested actions |
| `parcel_update_goals` | ParcelAgent | Set optimization goals |
| `parcel_get_usdx_balance` | Exchange | USDx wallet balance |
| `parcel_propose_usdx_incentive_contract` | Exchange | Create x402 contract |
| `parcel_sign_contract` | Exchange | EIP-712 sign |
| `parcel_get_contract_status` | Exchange | Contract status + spend |
| `parcel_send_agent_message` | Exchange | x402 agent-to-agent message |
| `market_build_agent` | AgentMarket | Build digital twin agent/avatar |

---

## Parcel Agent Loop

Each parcel runs a 4-node optimization graph:

1. **FetchContextNode** — calls MCP tools for parcel + underground + Stikk data
2. **ComputeMetricsNode** — non-LLM scoring: engagement_index, risk_level
3. **RecommendActionsNode** — generates 2 suggested actions (incentive / safety / contract)
4. **PersistStateNode** — writes updated state back

Replace step 3 with an LLM call (OpenAI, Gemini, Mistral) for richer recommendations.

---

## USDx + x402 Contracts

- All agent wallets are denominated in **USDx** (maps to USDC/USDT on Polygon testnet)
- Contract types: `incentive`, `data_sharing`
- Contracts require human approval above **100 USDx**
- x402 protocol labels on all messages and contracts for interoperability

---

## NANDA Registry

Four agents registered in `src/agents/nanda_agent_facts.json`:

| Agent ID | Capabilities |
|----------|--------------|
| `agent:spatial-fabric-sf` | place.hierarchy, parcel.lookup, route.parcel |
| `agent:parcel-agents-sf` | parcel.agent_state, parcel.optimize |
| `agent:exchange-sf` | wallet.usdx_balance, contract.sign |
| `agent:metaverse-browser-sf` | scene.load, copilot.query |

---

## How to Add a New Corridor

1. Copy `corridor-config.json` and update `region_id`, `bbox`, `entry_point`
2. Add GeoJSON files to `src/data/` for parcels, underground, stikk spots
3. Update `SpatialFabricServer.py` file map to reference new data files
4. Register new NANDA agent facts in `nanda_agent_facts.json`
5. Point your XR client at the new corridor manifest

---

## Hackathon Tracks

- **Tools:** Route.X unified MCP router + open GeoJSON/OGC APIs for developer tooling
- **Places:** Real SF parcels, underground utilities, Stikk IRL loyalty spots
- **AI:** Parcel Optimization Graph + Spatial Copilot via MCP + NANDA agent registry

---

## License

MIT — AGI Corporation 2026
