from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class Chemistry(str, Enum):
    LFP = "LFP"
    NMC = "NMC"
    VRLA = "VRLA"


class SafetyState(str, Enum):
    NORMAL = "NORMAL"
    ADVISORY = "ADVISORY"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class TelemetrySample(BaseModel):
    site_id: str = Field(min_length=1, max_length=80)
    rack_id: str = Field(min_length=1, max_length=80)
    chemistry: Chemistry
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ambient_temp_c: float = Field(ge=-20, le=80)
    max_cell_temp_c: float = Field(ge=-20, le=160)
    min_cell_temp_c: float = Field(ge=-20, le=160)
    h2_ppm: float = Field(default=0, ge=0, le=100000)
    co_ppm: float = Field(default=0, ge=0, le=100000)
    pack_voltage_v: float = Field(gt=0, le=2000)
    expected_pack_voltage_v: float = Field(gt=0, le=2000)
    current_a: float = Field(ge=-10000, le=10000)
    soc_pct: float = Field(ge=0, le=100)
    internal_resistance_mohm: float | None = Field(default=None, ge=0, le=10000)
    acoustic_rms: float | None = Field(default=None, ge=0)
    smoke_detected: bool = False
    bms_alarm: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_temperatures(self) -> "TelemetrySample":
        if self.min_cell_temp_c > self.max_cell_temp_c:
            raise ValueError("min_cell_temp_c cannot exceed max_cell_temp_c")
        return self


class RiskAssessment(BaseModel):
    site_id: str
    rack_id: str
    timestamp: datetime
    risk_score: float = Field(ge=0, le=1)
    state: SafetyState
    confidence: float = Field(ge=0, le=1)
    risk_factors: dict[str, float]
    reasons: list[str]
    recommended_actions: list[str]
    control_permitted: bool = False
    model_version: str = "transparent-rule-fusion-v1"


class Incident(BaseModel):
    id: int
    created_at: datetime
    site_id: str
    rack_id: str
    state: SafetyState
    risk_score: float
    summary: str
    acknowledged: bool = False


class AckRequest(BaseModel):
    operator: str = Field(min_length=2, max_length=120)
    note: str = Field(default="", max_length=500)
