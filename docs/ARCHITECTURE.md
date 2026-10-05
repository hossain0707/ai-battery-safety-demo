# Production architecture

## Safety boundary

The platform is intentionally **advisory-first**. AI can identify weak precursors and rank risk, but it is not the authority for emergency isolation. Existing BMS, UPS, PLC, fire detection/suppression and approved emergency procedures remain authoritative.

```text
Sensors / BMS / UPS / Fire panel
        |  read-only, authenticated
        v
Protocol gateway (MQTT TLS / SNMPv3 / OPC UA / Modbus read-only)
        |
        v
Telemetry API --> validation --> feature/risk engine --> safety policy
        |                                      |
        v                                      v
 time-series/audit store                  operator recommendations
        |                                      |
        +--> dashboards / SIEM / CMMS <--------+

Hardwired BMS / PLC / Fire system ----------------> physical safety actions
                         (independent of AI service)
```

## Recommended production services

1. **Edge gateway** close to the battery room for protocol normalization, buffering and clock synchronization.
2. **Telemetry service** with schema validation, freshness checks, device identity and replay protection.
3. **Transparent risk engine** for interpretable precursor scoring; ML models can be added behind the same contract.
4. **Deterministic policy service** that maps risk to operational state and runbook recommendations.
5. **Immutable audit trail** for incident investigation, maintenance and model governance.
6. **Fleet dashboard** for site/rack/cell views, trend correlation and acknowledgement workflow.
7. **Observability**: service health, ingestion lag, sensor dropouts, model drift and alert delivery SLOs.

## Bangladesh / Grameenphone-aligned deployment profile

Public information describes Grameenphone's Sylhet Super Core facility as Tier III-standard with a 4 MW load and high-tech monitoring. This repository therefore assumes redundant power infrastructure and emphasizes integration rather than replacing existing controls. It is not an official Grameenphone system and contains no confidential GP design information.
