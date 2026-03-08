"""ParcelOptimizationGraph — LangGraph-style sequential optimization flow for parcels."""
import httpx
from datetime import datetime
from typing import TypedDict, List, Optional

ROUTEX_URL = "http://localhost:4000"

class ParcelState(TypedDict):
    parcel_id: str
    raw_context: dict
    metrics: dict
    suggested_actions: List[dict]
    goals: List[str]
    last_updated: str
    error: Optional[str]

async def call_tool(tool_name: str, args: dict) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{ROUTEX_URL}/mcp/tool",
            json={"tool_name": tool_name, "args": args}
        )
        resp.raise_for_status()
        return resp.json().get("result", {})

# --- Node 1: Fetch context from MCP ---
async def fetch_context_node(state: ParcelState) -> ParcelState:
    parcel_id = state["parcel_id"]
    try:
        parcel = await call_tool("parcel_get_parcel", {"parcel_id": parcel_id})
        agent = await call_tool("parcel_get_agent_state", {"parcel_id": parcel_id})
        state["raw_context"] = {"parcel": parcel, "agent": agent}
    except Exception as e:
        state["error"] = f"FetchContextNode error: {e}"
    return state

# --- Node 2: Compute metrics (non-LLM) ---
def compute_metrics_node(state: ParcelState) -> ParcelState:
    agent = state["raw_context"].get("agent", {})
    metrics = agent.get("metrics", {})
    visit_score = metrics.get("visit_score", 0)
    risk_score = metrics.get("risk_score", 0.5)
    stikk_points = metrics.get("stikk_points", 0)
    budget_usdx = metrics.get("budget_usdx", 0)

    # Composite engagement index
    engagement_index = round((visit_score * 0.6 + stikk_points * 0.4 / 10), 2)
    risk_level = "high" if risk_score > 0.7 else "medium" if risk_score > 0.4 else "low"

    state["metrics"] = {
        "visit_score": visit_score,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "stikk_points": stikk_points,
        "engagement_index": engagement_index,
        "budget_usdx": budget_usdx
    }
    return state

# --- Node 3: Recommend actions (rule-based, replace with LLM call in production) ---
def recommend_actions_node(state: ParcelState) -> ParcelState:
    m = state["metrics"]
    actions = []

    if m["engagement_index"] < 40:
        actions.append({
            "title": "Launch off-peak incentive campaign",
            "description": f"Engagement index is {m['engagement_index']}. Offer 2 USDx per check-in between 2pm-5pm.",
            "type": "incentive",
            "estimated_cost_usdx": 20.0
        })

    if m["risk_level"] in ["high", "medium"]:
        actions.append({
            "title": "Schedule underground utility review",
            "description": f"Risk score is {m['risk_score']} ({m['risk_level']}). Coordinate with utility agent before any construction.",
            "type": "safety",
            "estimated_cost_usdx": 0.0
        })

    if m["budget_usdx"] > 100 and m["stikk_points"] < 100:
        actions.append({
            "title": "Propose data-sharing contract with Stikk",
            "description": "Low Stikk engagement but budget available. Propose 10 USDx data-sharing agreement.",
            "type": "contract",
            "estimated_cost_usdx": 10.0
        })

    state["suggested_actions"] = actions[:2]  # Return top 2
    return state

# --- Node 4: Persist updated state ---
async def persist_state_node(state: ParcelState) -> ParcelState:
    state["last_updated"] = datetime.utcnow().isoformat()
    # In production: write to ParcelAgentServer store
    # For now: just return the updated state
    return state

# --- Main runner ---
async def run_parcel_optimization(parcel_id: str, goals: List[str] = None) -> ParcelState:
    state: ParcelState = {
        "parcel_id": parcel_id,
        "raw_context": {},
        "metrics": {},
        "suggested_actions": [],
        "goals": goals or ["maximize_community_engagement", "minimize_utility_risk"],
        "last_updated": "",
        "error": None
    }
    state = await fetch_context_node(state)
    if state.get("error"):
        return state
    state = compute_metrics_node(state)
    state = recommend_actions_node(state)
    state = await persist_state_node(state)
    return state

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(run_parcel_optimization("us-ca-sf-001234-005-06"))
    import json
    print(json.dumps(result, indent=2))
