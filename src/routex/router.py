"""Route.X Router — Unified MCP front door for all Parcel OS tools."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict
import httpx
from .tool_routes import TOOL_ROUTES

app = FastAPI(title="RouteX MCP Router", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class ToolCall(BaseModel):
    tool_name: str
    args: Dict[str, Any] = {}

@app.post("/mcp/tool")
async def call_tool(call: ToolCall):
    route = TOOL_ROUTES.get(call.tool_name)
    if not route:
        raise HTTPException(404, f"Unknown tool: {call.tool_name}")

    url = build_url(route, call.args)
    method = route.get("method", "get").lower()

    async with httpx.AsyncClient(timeout=10.0) as client:
        if method == "get":
            resp = await client.get(url, params=route_query_params(route, call.args))
        elif method == "post":
            resp = await client.post(url, json=call.args)
        else:
            raise HTTPException(400, f"Unsupported method: {method}")

        if resp.status_code >= 400:
            raise HTTPException(resp.status_code, resp.text)

        return {"tool_name": call.tool_name, "result": resp.json()}

def build_url(route: dict, args: dict) -> str:
    url = route["url"]
    for key, val in args.items():
        url = url.replace(f":{key}", str(val))
    return url

def route_query_params(route: dict, args: dict) -> dict:
    qp = route.get("query_params", [])
    return {k: args[k] for k in qp if k in args}

@app.get("/mcp/tools")
def list_tools():
    return {"tools": list(TOOL_ROUTES.keys()), "count": len(TOOL_ROUTES)}

@app.get("/health")
def health():
    return {"status": "ok", "service": "RouteX MCP Router"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4000)
