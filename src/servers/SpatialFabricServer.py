"""SpatialFabricServer — FastAPI server for parcels, layers, features, and routing."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json, math, os

app = FastAPI(title="SpatialFabricServer", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")

def load_geojson(filename: str):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return {"type": "FeatureCollection", "features": []}
    with open(path) as f:
        return json.load(f)

@app.get("/placeHierarchy")
def place_hierarchy(lat: float, lon: float):
    parcel_id = f"us-ca-sf-{abs(round(lat*1000))}-{abs(round(lon*1000))}"
    return {
        "country": "us", "region": "ca",
        "county": "san-francisco", "city": "san-francisco",
        "parcel_id": parcel_id
    }

@app.get("/parcel/{parcel_id}")
def get_parcel(parcel_id: str):
    parcels = load_geojson("sf-parcels.geojson")
    for f in parcels["features"]:
        if f["properties"].get("parcel_id") == parcel_id:
            return f
    # Return first parcel as fallback
    if parcels["features"]:
        return parcels["features"][0]
    raise HTTPException(404, f"Parcel {parcel_id} not found")

@app.get("/layers")
def list_layers():
    return {"layers": [
        {"id": "parcels", "name": "Parcels", "type": "polygon"},
        {"id": "utilities-underground", "name": "Underground Utilities", "type": "line"},
        {"id": "stikk_spots", "name": "Stikk Spots", "type": "point"},
        {"id": "routes", "name": "Routes", "type": "line"}
    ]}

@app.get("/collections/{layer_id}")
def get_features(layer_id: str, minLon: float = None, minLat: float = None,
                 maxLon: float = None, maxLat: float = None):
    file_map = {
        "parcels": "sf-parcels.geojson",
        "utilities-underground": "sf-underground.geojson",
        "stikk_spots": "sf-stikk-spots.geojson"
    }
    if layer_id not in file_map:
        raise HTTPException(404, f"Layer {layer_id} not found")
    return load_geojson(file_map[layer_id])

class RouteRequest(BaseModel):
    from_parcel_id: str
    to_parcel_id: str
    mode: str = "walk"

@app.post("/routeBetweenParcels")
def route_between_parcels(req: RouteRequest):
    return {
        "from_parcel_id": req.from_parcel_id,
        "to_parcel_id": req.to_parcel_id,
        "mode": req.mode,
        "distance_m": 420,
        "duration_s": 310,
        "geometry": {
            "type": "LineString",
            "coordinates": [[-122.4194, 37.7749], [-122.4144, 37.7799]]
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)
