# Deployment guide

## Local / pilot

```bash
cp .env.example .env
# replace BATTERY_SAFETY_API_KEY with a long random secret
docker compose up --build
```

Open `http://localhost:8080`. API documentation is available at `/docs`.

## Production checklist

- Deploy inside the data-center management network; no public ingress to telemetry endpoints.
- Terminate TLS at an approved reverse proxy/API gateway.
- Use SSO/RBAC at the gateway and unique credentials for gateways/services.
- Use read-only protocol integration with BMS/UPS/fire systems wherever possible.
- Replace SQLite with PostgreSQL/TimescaleDB or the organization's approved telemetry platform for multi-site scale.
- Send logs and incidents to SIEM/CMMS/NOC tooling.
- Add redundant service instances and monitored message buffering at the edge.
- Run site acceptance tests with injected sensor faults, stale telemetry, network loss and known alarm scenarios.
- Calibrate analytics against manufacturer data and real GP operational history before relying on alert thresholds.
- Complete fire, electrical, cybersecurity and functional-safety reviews before any pilot becomes operational.

## Example telemetry

```bash
curl -X POST http://localhost:8080/api/v1/telemetry \
  -H 'Content-Type: application/json' \
  -H 'X-API-Key: YOUR_KEY' \
  -d '{
    "site_id":"sylhet-reference",
    "rack_id":"UPS-A-R01",
    "chemistry":"LFP",
    "ambient_temp_c":25,
    "max_cell_temp_c":29,
    "min_cell_temp_c":27,
    "h2_ppm":8,
    "co_ppm":2,
    "pack_voltage_v":512,
    "expected_pack_voltage_v":512,
    "current_a":75,
    "soc_pct":93,
    "internal_resistance_mohm":1.9
  }'
```
