from __future__ import annotations

from .models import SafetyState, TelemetrySample


def classify_state(risk: float, sample: TelemetrySample) -> SafetyState:
    if sample.smoke_detected or sample.bms_alarm or risk >= 0.85:
        return SafetyState.CRITICAL
    if risk >= 0.60:
        return SafetyState.WARNING
    if risk >= 0.32:
        return SafetyState.ADVISORY
    return SafetyState.NORMAL


def recommended_actions(state: SafetyState, sample: TelemetrySample) -> list[str]:
    if state is SafetyState.CRITICAL:
        return [
            "Escalate to the site emergency procedure and qualified duty engineer.",
            "Verify BMS/UPS/PLC hardwired alarms and isolation status; do not rely on AI output for actuation.",
            "Inspect fire detection, ventilation and suppression status from approved control systems.",
            "Restrict access to the affected battery area according to the site safety plan.",
        ]
    if state is SafetyState.WARNING:
        return [
            "Dispatch a qualified operator to verify the affected rack and sensor readings.",
            "Cross-check BMS, thermal, gas and power-quality telemetry for corroboration.",
            "Prepare the approved site isolation/cooling procedure if the condition worsens.",
        ]
    if state is SafetyState.ADVISORY:
        return [
            "Increase monitoring frequency for this rack.",
            "Review recent load, temperature, maintenance and battery-health history.",
            "Create a maintenance inspection if the advisory persists.",
        ]
    return ["Continue normal monitoring and scheduled maintenance."]
