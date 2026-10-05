import os

os.environ["BATTERY_SAFETY_ALLOW_INSECURE_DEMO"] = "true"
os.environ["BATTERY_SAFETY_DB"] = "/tmp/battery_safety_test.db"

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def payload():
    return {
        "site_id": "bd-telco-dc",
        "rack_id": "UPS-A-R01",
        "chemistry": "LFP",
        "ambient_temp_c": 24,
        "max_cell_temp_c": 28,
        "min_cell_temp_c": 26,
        "h2_ppm": 5,
        "co_ppm": 2,
        "pack_voltage_v": 512,
        "expected_pack_voltage_v": 512,
        "current_a": 45,
        "soc_pct": 91,
        "internal_resistance_mohm": 1.8
    }


def test_health():
    assert client.get("/healthz").status_code == 200


def test_ingest_and_status():
    response = client.post("/api/v1/telemetry", json=payload())
    assert response.status_code == 200
    body = response.json()
    assert body["control_permitted"] is False
    status = client.get("/api/v1/status?site_id=bd-telco-dc").json()
    assert status["rack_count"] >= 1
