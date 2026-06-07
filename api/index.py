from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import numpy as np

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry data once
with open("q-vercel-latency.json", "r") as f:
    telemetry = json.load(f)

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: float


@app.post("/")
def analyze_latency(body: RequestBody):

    result = {}

    for region in body.regions:

        region_rows = [
            row for row in telemetry
            if row["region"] == region
        ]

        if not region_rows:
            continue

        latencies = [row["latency_ms"] for row in region_rows]
        uptimes = [row["uptime"] for row in region_rows]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 4),
            "breaches": sum(
                1 for x in latencies
                if x > body.threshold_ms
            )
        }

    return result
