from __future__ import annotations

import hmac
import os
from collections import defaultdict
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse

from .models import AckRequest, RiskAssessment, SafetyState, TelemetrySample
from .risk_engine import PROFILES, score_sample
from .safety_policy import classify_state, recommended_actions
from .store import Store

APP_VERSION = "1.0.0"
ROOT = Path(__file__).resolve().parents[2]
DB_PATH = os.getenv("BATTERY_SAFETY_DB", str(ROOT / "data" / "battery_safety.db"))
API_KEY = os.getenv("BATTERY_SAFETY_API_KEY", "")
ALLOW_INSECURE_DEMO = os.getenv("BATTERY_SAFETY_ALLOW_INSECURE_DEMO", "false").lower() == "true"
SITE_PROFILE = os.getenv("BATTERY_SAFETY_SITE_PROFILE", "bangladesh-telco-reference")

app = FastAPI(
    title="AI Battery Safety Platform",
    version=APP_VERSION,
    description="AI-assisted early warning for stationary telecom/data-center batteries. Recommendation-only by default.",
)
store = Store(DB_PATH)
last_samples: dict[tuple[str, str], TelemetrySample] = {}
latest_assessments: dict[tuple[str, str], RiskAssessment] = {}


def require_write_auth(x_api_key: Annotated[str | None, Header()] = None) -> None:
    if ALLOW_INSECURE_DEMO:
        return
    if not API_KEY:
        raise HTTPException(status_code=503, detail="Server write API is locked until BATTERY_SAFETY_API_KEY is configured")
    if not x_api_key or not hmac.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/")
def dashboard() -> FileResponse:
    return FileResponse(ROOT / "index.html")


@app.get("/healthz")
def health() -> dict:
    return {"status": "ok", "version": APP_VERSION}


@app.get("/readyz")
def ready() -> dict:
    return {"status": "ready", "database": "sqlite", "site_profile": SITE_PROFILE, "actuation": "recommendation_only"}


@app.get("/api/v1/config")
def config() -> dict:
    return {
        "version": APP_VERSION,
        "site_profile": SITE_PROFILE,
        "actuation_mode": "recommendation_only",
        "supported_chemistries": list(PROFILES.keys()),
        "safety_notice": "Analytics thresholds are reference values, not certified protection setpoints. Hardwired BMS/UPS/PLC/fire systems remain authoritative.",
    }


@app.post("/api/v1/telemetry", response_model=RiskAssessment, dependencies=[Depends(require_write_auth)])
def ingest(sample: TelemetrySample) -> RiskAssessment:
    key = (sample.site_id, sample.rack_id)
    previous = last_samples.get(key)
    risk, factors, reasons, confidence = score_sample(sample, previous)
    state = classify_state(risk, sample)
    assessment = RiskAssessment(
        site_id=sample.site_id, rack_id=sample.rack_id, timestamp=sample.timestamp,
        risk_score=risk, state=state, confidence=confidence, risk_factors=factors,
        reasons=reasons, recommended_actions=recommended_actions(state, sample),
        control_permitted=False,
    )
    last_samples[key] = sample
    latest_assessments[key] = assessment
    store.save_assessment(sample.model_dump(mode="json"), risk, state, reasons)
    return assessment


@app.get("/api/v1/status")
def status(site_id: str | None = None) -> dict:
    items = [a for (site, _), a in latest_assessments.items() if site_id is None or site == site_id]
    counts = defaultdict(int)
    for item in items:
        counts[item.state.value] += 1
    order = [SafetyState.NORMAL, SafetyState.ADVISORY, SafetyState.WARNING, SafetyState.CRITICAL]
    worst = SafetyState.NORMAL if not items else max((a.state for a in items), key=lambda s: order.index(s))
    return {
        "site_id": site_id or "all", "overall_state": worst, "rack_count": len(items),
        "counts": {state.value: counts[state.value] for state in order}, "racks": items,
    }


@app.get("/api/v1/incidents")
def incidents(limit: int = Query(default=50, ge=1, le=500)):
    return store.list_incidents(limit)


@app.post("/api/v1/incidents/{incident_id}/ack", dependencies=[Depends(require_write_auth)])
def acknowledge(incident_id: int, request: AckRequest) -> dict:
    if not store.acknowledge(incident_id, request.operator, request.note):
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"ok": True, "incident_id": incident_id}
