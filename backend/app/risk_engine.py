from __future__ import annotations

import math
from dataclasses import dataclass

from .models import Chemistry, TelemetrySample


@dataclass(frozen=True)
class AnalyticsProfile:
    # Early-warning analytics reference points only. These are NOT certified trip setpoints.
    temp_ref_c: float
    temp_spread_ref_c: float
    h2_ref_ppm: float
    co_ref_ppm: float
    voltage_dev_ref_pct: float
    resistance_ref_mohm: float


PROFILES: dict[Chemistry, AnalyticsProfile] = {
    Chemistry.LFP: AnalyticsProfile(45.0, 8.0, 100.0, 50.0, 4.0, 8.0),
    Chemistry.NMC: AnalyticsProfile(42.0, 7.0, 80.0, 40.0, 4.0, 8.0),
    Chemistry.VRLA: AnalyticsProfile(35.0, 6.0, 1000.0, 50.0, 5.0, 15.0),
}


def _sigmoid(x: float, midpoint: float, scale: float) -> float:
    scale = max(scale, 1e-6)
    return 1.0 / (1.0 + math.exp(-(x - midpoint) / scale))


def _ratio_score(value: float, reference: float) -> float:
    if reference <= 0:
        return 0.0
    return min(1.0, max(0.0, value / reference))


def score_sample(sample: TelemetrySample, previous: TelemetrySample | None = None) -> tuple[float, dict[str, float], list[str], float]:
    p = PROFILES[sample.chemistry]
    temp = _sigmoid(sample.max_cell_temp_c, p.temp_ref_c, 5.0)
    temp_spread = _ratio_score(sample.max_cell_temp_c - sample.min_cell_temp_c, p.temp_spread_ref_c)
    h2 = _ratio_score(sample.h2_ppm, p.h2_ref_ppm)
    co = _ratio_score(sample.co_ppm, p.co_ref_ppm)
    voltage_dev_pct = abs(sample.pack_voltage_v - sample.expected_pack_voltage_v) / sample.expected_pack_voltage_v * 100.0
    voltage = _ratio_score(voltage_dev_pct, p.voltage_dev_ref_pct)
    resistance = 0.0 if sample.internal_resistance_mohm is None else _ratio_score(sample.internal_resistance_mohm, p.resistance_ref_mohm)

    temp_rate = 0.0
    if previous is not None and previous.rack_id == sample.rack_id:
        dt = (sample.timestamp - previous.timestamp).total_seconds()
        if dt > 0:
            rate_c_per_min = max(0.0, (sample.max_cell_temp_c - previous.max_cell_temp_c) / dt * 60.0)
            temp_rate = _ratio_score(rate_c_per_min, 5.0)

    factors = {
        "temperature": round(temp, 4),
        "temperature_spread": round(temp_spread, 4),
        "temperature_rate": round(temp_rate, 4),
        "hydrogen": round(h2, 4),
        "carbon_monoxide": round(co, 4),
        "voltage_deviation": round(voltage, 4),
        "internal_resistance": round(resistance, 4),
    }
    weights = {
        "temperature": 0.20, "temperature_spread": 0.11, "temperature_rate": 0.18,
        "hydrogen": 0.14, "carbon_monoxide": 0.12, "voltage_deviation": 0.14,
        "internal_resistance": 0.11,
    }
    risk = sum(factors[k] * weights[k] for k in factors)
    if sample.smoke_detected:
        risk = max(risk, 0.98)
    if sample.bms_alarm:
        risk = max(risk, 0.90)
    if sum(1 for v in factors.values() if v >= 0.65) >= 3:
        risk = min(1.0, risk + 0.12)

    reasons = [k.replace("_", " ") for k, v in sorted(factors.items(), key=lambda item: item[1], reverse=True) if v >= 0.50][:4]
    if sample.smoke_detected:
        reasons.insert(0, "smoke detector active")
    if sample.bms_alarm:
        reasons.insert(0, "BMS alarm active")
    if not reasons:
        reasons = ["telemetry within configured analytics envelope"]
    present = 7 - (1 if sample.internal_resistance_mohm is None else 0)
    confidence = min(0.99, 0.55 + present * 0.055 + (0.05 if previous else 0.0))
    return round(min(1.0, risk), 4), factors, reasons, round(confidence, 3)
