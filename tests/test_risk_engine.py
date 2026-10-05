from datetime import datetime, timedelta, timezone

from backend.app.models import Chemistry, SafetyState, TelemetrySample
from backend.app.risk_engine import score_sample
from backend.app.safety_policy import classify_state


def sample(**overrides):
    base = dict(
        site_id="bd-telco-dc",
        rack_id="UPS-A-R01",
        chemistry=Chemistry.LFP,
        timestamp=datetime.now(timezone.utc),
        ambient_temp_c=24,
        max_cell_temp_c=27,
        min_cell_temp_c=25,
        h2_ppm=5,
        co_ppm=2,
        pack_voltage_v=512,
        expected_pack_voltage_v=512,
        current_a=60,
        soc_pct=90,
        internal_resistance_mohm=1.5,
    )
    base.update(overrides)
    return TelemetrySample(**base)


def test_nominal_sample_is_low_risk():
    s = sample()
    risk, factors, reasons, confidence = score_sample(s)
    assert risk < 0.32
    assert classify_state(risk, s) is SafetyState.NORMAL
    assert confidence > 0.7


def test_multisensor_anomaly_escalates():
    s = sample(max_cell_temp_c=58, min_cell_temp_c=39, h2_ppm=120, co_ppm=65, pack_voltage_v=485)
    risk, *_ = score_sample(s)
    assert risk >= 0.60
    assert classify_state(risk, s) in (SafetyState.WARNING, SafetyState.CRITICAL)


def test_smoke_forces_critical():
    s = sample(smoke_detected=True)
    risk, *_ = score_sample(s)
    assert risk >= 0.98
    assert classify_state(risk, s) is SafetyState.CRITICAL


def test_temperature_rate_is_used():
    t0 = datetime.now(timezone.utc)
    prev = sample(timestamp=t0, max_cell_temp_c=28)
    current = sample(timestamp=t0 + timedelta(minutes=1), max_cell_temp_c=38)
    _, factors, *_ = score_sample(current, prev)
    assert factors["temperature_rate"] == 1.0
