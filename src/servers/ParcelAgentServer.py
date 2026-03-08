"""ParcelAgentServer — FastAPI server for parcel agent state and optimization goals."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime
import random

app = FastAPI(title="ParcelAgentServer", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# In-memory store — replace with DB in production
agent_store: dict = {}

def init_agent(parcel_id: str) -> dict:
    return {
        "parcel_id": parcel_id,
        "goals": ["maximize_community_engagement", "minimize_utility_risk"],
        "metrics": {
            "visit_score": random.randint(20, 100),
            "risk_score": round(random.uniform(0.1, 0.9), 2),
            "stikk_points": random.randint(50, 400),
            "budget_usdx": 200.0,
            "spend_last_30d_usdx": round(random.uniform(0, 80), 2)
        },
        "suggested_actions": [
            {
                "title": "Add micro-reward for off-peak visits",
                "description": "Offer 2 USDx per check-in between 2pm-5pm to boost foot traffic.",
                "type": "incentive",
                "estimated_cost_usdx": 20.0
            },
            {
                "title": "Flag underground risk zone",
                "description": "High-density utilities detected. Review before any construction permit.",
                "type": "safety",
                "estimated_cost_usdx": 0.0
            }
        ],
        "wallet_address": f"0x{parcel_id.replace('-','')[:40].ljust(40,'0')}",
        "contracts": [],
        "last_updated": datetime.utcnow().isoformat()
    }

@app.get("/agent/{parcel_id}")
def get_agent(parcel_id: str):
    if parcel_id not in agent_store:
        agent_store[parcel_id] = init_agent(parcel_id)
    return agent_store[parcel_id]

class GoalsUpdate(BaseModel):
    goals: List[str]

@app.post("/agent/{parcel_id}/goals")
def update_goals(parcel_id: str, body: GoalsUpdate):
    if parcel_id not in agent_store:
        agent_store[parcel_id] = init_agent(parcel_id)
    agent_store[parcel_id]["goals"] = body.goals
    agent_store[parcel_id]["last_updated"] = datetime.utcnow().isoformat()
    return {"ok": True, "parcel_id": parcel_id, "goals": body.goals}

@app.get("/agents")
def list_agents():
    return {"agents": list(agent_store.keys()), "count": len(agent_store)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3002)
