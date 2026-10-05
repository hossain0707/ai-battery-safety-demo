# AI Battery Safety Platform for Telecom Data Centers

Production-oriented reference implementation for **AI-assisted stationary battery safety**, designed around telecom/data-center operations in Bangladesh and the public operating context of Grameenphone infrastructure.

> **Safety boundary:** this software is an early-warning and operator decision-support layer. It is **not** a certified BMS, fire panel, PLC, protection relay or emergency shutdown controller. Physical protection remains the responsibility of validated hardwired systems and approved site procedures.


## 🚀 Live Demo

**[▶ Open the Battery Safety Simulation Demo](https://raw.githack.com/hossain0707/ai-battery-safety-demo/main/index.html)**

The interactive browser demo visualizes the telecom/data-center battery fleet, AI risk scoring, multi-sensor anomaly detection, incident escalation, thermal/risk trends, and the recommendation-only safety architecture.

> Demo mode uses simulated telemetry for demonstration purposes. It is not connected to a real Grameenphone data center or live battery equipment.


## What changed

The original repository was a single browser simulation showing how AI might detect battery anomalies before a traditional threshold. This upgrade keeps the concept and adds a serious pilot foundation:

- FastAPI telemetry service with strict schema/range validation
- LFP, NMC and VRLA analytics profiles
- multi-sensor risk fusion using temperature, temperature spread/rate, H2, CO, voltage deviation and internal resistance
- deterministic escalation for smoke/BMS alarm evidence
- transparent factor-level risk score, confidence and explanations
- `NORMAL / ADVISORY / WARNING / CRITICAL` operational states
- recommendation-only safety policy with `control_permitted=false`
- persistent telemetry/incident audit store for pilot use
- operator acknowledgement workflow
- API-key protection for write operations
- liveness/readiness/config/status endpoints
- Docker/Compose deployment
- automated tests and GitHub Actions CI
- browser operations dashboard with a safe test-anomaly simulation
- architecture, safety-case, security and deployment documentation

## Grameenphone-aligned reference context

Grameenphone publicly describes its Sylhet Super Core facility as a Tier III-standard data center with a 4 MW load, high-tech monitoring and automatic fire suppression. Grameenphone has also publicly reported deploying Li-ion batteries across thousands of telecom sites. This project therefore supports lithium and legacy VRLA operating profiles and assumes integration with existing BMS/UPS/fire systems rather than replacing them.

This is **not an official Grameenphone product**, is not endorsed by Grameenphone, and contains no confidential GP design information.

## API

| Endpoint | Purpose |
|---|---|
| `GET /healthz` | service liveness |
| `GET /readyz` | readiness and safety mode |
| `GET /api/v1/config` | supported chemistries / safety notice |
| `POST /api/v1/telemetry` | ingest telemetry and return risk assessment |
| `GET /api/v1/status` | latest rack/fleet status |
| `GET /api/v1/incidents` | incident history |
| `POST /api/v1/incidents/{id}/ack` | operator acknowledgement |

## Run locally

```bash
cp .env.example .env
# replace BATTERY_SAFETY_API_KEY with a long random secret
docker compose up --build
```

Open `http://localhost:8080` for the dashboard and `http://localhost:8080/docs` for interactive API documentation.

## Industrial integration path

For a real data center, deploy an edge gateway that reads approved BMS/UPS/fire telemetry using **MQTT/TLS, SNMPv3, OPC UA or read-only Modbus TCP**, buffers data during network loss, authenticates device telemetry, and forwards it to this service.

At multi-site scale, replace SQLite with the organization's approved PostgreSQL/time-series platform and connect warnings/incidents to NOC, SIEM and CMMS workflows.

See:
- [Production architecture](docs/ARCHITECTURE.md)
- [Safety case](docs/SAFETY_CASE.md)
- [Deployment guide](docs/DEPLOYMENT.md)
- [Security policy](SECURITY.md)

## Standards / engineering reference set

The design is informed by IEC 62619 for industrial lithium batteries including telecom/UPS, IEC 63056 for stationary energy-storage batteries, UL 9540A for thermal-runaway fire propagation testing, NFPA 855 for stationary ESS installation/fire protection where applicable, IEEE 1188-2025 for VRLA maintenance/testing, and Bangladesh National Building Code / local fire-authority requirements.

**Referencing a standard is not a claim of certification.** Final thresholds, alarms and emergency procedures must be validated against battery/UPS/BMS manufacturer data, the site fire strategy, Grameenphone engineering requirements and the authority having jurisdiction.

## Recommended path to a real GP pilot

1. Obtain a sanitized telemetry dictionary from the target BMS, UPS and fire systems.
2. Confirm battery chemistry, module topology, manufacturer limits and maintenance procedure for every rack family.
3. Build a read-only edge connector and historical backfill pipeline.
4. Calibrate/train the risk model on actual normal/fault history with strict holdout validation.
5. Run the AI service in **shadow mode** first; compare its alerts with operator/BMS outcomes without any control authority.
6. Complete cybersecurity, fire, electrical, operational and functional-safety reviews.
7. After acceptance testing, connect alerts to approved NOC/CMMS incident workflows.

## Current validation

The included automated test suite covers nominal behavior, multi-sensor anomaly escalation, smoke-forced critical state, temperature-rate features, API health and ingestion/status flow.

No safety certification is claimed. Treat this repository as an engineering reference and pilot foundation, not as a finished certified life-safety product.
