from __future__ import annotations

import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

from .models import Incident, SafetyState


class Store:
    def __init__(self, db_path: str) -> None:
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        with self.conn:
            self.conn.executescript("""
                CREATE TABLE IF NOT EXISTS telemetry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
                    site_id TEXT NOT NULL, rack_id TEXT NOT NULL, payload TEXT NOT NULL,
                    risk_score REAL NOT NULL, state TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_telemetry_rack ON telemetry(site_id, rack_id, id DESC);
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL,
                    site_id TEXT NOT NULL, rack_id TEXT NOT NULL, state TEXT NOT NULL,
                    risk_score REAL NOT NULL, summary TEXT NOT NULL,
                    acknowledged INTEGER NOT NULL DEFAULT 0, ack_operator TEXT,
                    ack_note TEXT, ack_at TEXT
                );
            """)

    def save_assessment(self, payload: dict, risk_score: float, state: SafetyState, reasons: list[str]) -> int | None:
        now = datetime.now(timezone.utc).isoformat()
        with self.lock, self.conn:
            self.conn.execute(
                "INSERT INTO telemetry(created_at,site_id,rack_id,payload,risk_score,state) VALUES(?,?,?,?,?,?)",
                (now, payload["site_id"], payload["rack_id"], json.dumps(payload, default=str), risk_score, state.value),
            )
            if state in (SafetyState.WARNING, SafetyState.CRITICAL):
                cur = self.conn.execute(
                    "INSERT INTO incidents(created_at,site_id,rack_id,state,risk_score,summary) VALUES(?,?,?,?,?,?)",
                    (now, payload["site_id"], payload["rack_id"], state.value, risk_score, ", ".join(reasons[:4])),
                )
                return int(cur.lastrowid)
        return None

    def list_incidents(self, limit: int = 50) -> list[Incident]:
        rows = self.conn.execute(
            "SELECT id,created_at,site_id,rack_id,state,risk_score,summary,acknowledged FROM incidents ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            Incident(id=row["id"], created_at=datetime.fromisoformat(row["created_at"]),
                     site_id=row["site_id"], rack_id=row["rack_id"], state=SafetyState(row["state"]),
                     risk_score=row["risk_score"], summary=row["summary"],
                     acknowledged=bool(row["acknowledged"]))
            for row in rows
        ]

    def acknowledge(self, incident_id: int, operator: str, note: str) -> bool:
        now = datetime.now(timezone.utc).isoformat()
        with self.lock, self.conn:
            cur = self.conn.execute(
                "UPDATE incidents SET acknowledged=1, ack_operator=?, ack_note=?, ack_at=? WHERE id=?",
                (operator, note, now, incident_id),
            )
            return cur.rowcount == 1
