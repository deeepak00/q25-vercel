from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
import os

app = FastAPI()
# Enable CORS

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_methods=["POST", "GET", "OPTIONS"],
allow_headers=["Content-Type", "Authorization"],
expose_headers=["Access-Control-Allow-Origin"],
)
# Load telemetry data
DATA_FILE = "telemetry.json"
try:
    df = pd.read_json(DATA_FILE)
except:
    df = pd.DataFrame()

@app.get("/")
def home():
    return {"message": "Latency API running"}

@app.post("/api/latency")
async def latency(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)
    results = []
    for region in regions:
        region_data = df[df["region"] == region]
        if len(region_data) == 0:
            continue
        latency_values = region_data["latency_ms"]
        uptime_values = region_data["uptime_pct"]
        results.append({
            "region": region,
            "avg_latency": float(latency_values.mean()),
            "p95_latency": float(np.percentile(latency_values,95)),
            "avg_uptime": float(uptime_values.mean()),
            "breaches": int((latency_values > threshold).sum())
        })
    return {"regions": results}
