"""Tool routing table for Route.X MCP Router."""

SPATIAL = "http://localhost:3001"
AGENT = "http://localhost:3002"
EXCHANGE = "http://localhost:3003"

TOOL_ROUTES = {
    "parcel_get_place_hierarchy": {
        "url": f"{SPATIAL}/placeHierarchy",
        "method": "get",
        "query_params": ["lat", "lon"]
    },
    "parcel_get_parcel": {
        "url": f"{SPATIAL}/parcel/:parcel_id",
        "method": "get"
    },
    "parcel_list_layers": {
        "url": f"{SPATIAL}/layers",
        "method": "get"
    },
    "parcel_get_features": {
        "url": f"{SPATIAL}/collections/:layer_id",
        "method": "get"
    },
    "parcel_plan_route_between_parcels": {
        "url": f"{SPATIAL}/routeBetweenParcels",
        "method": "post"
    },
    "parcel_get_agent_state": {
        "url": f"{AGENT}/agent/:parcel_id",
        "method": "get"
    },
    "parcel_update_goals": {
        "url": f"{AGENT}/agent/:parcel_id/goals",
        "method": "post"
    },
    "parcel_get_usdx_balance": {
        "url": f"{EXCHANGE}/wallet/:parcel_id",
        "method": "get"
    },
    "parcel_propose_usdx_incentive_contract": {
        "url": f"{EXCHANGE}/contract/propose",
        "method": "post"
    },
    "parcel_sign_contract": {
        "url": f"{EXCHANGE}/contract/:contract_id/sign",
        "method": "post"
    },
    "parcel_get_contract_status": {
        "url": f"{EXCHANGE}/contract/:contract_id",
        "method": "get"
    },
    "parcel_send_agent_message": {
        "url": f"{EXCHANGE}/message/send",
        "method": "post"
    }
}
