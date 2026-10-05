# Security policy

This project is a safety-monitoring reference implementation, not a certified protection system.

## Production rules

- Keep actuation disabled unless an independent functional-safety review explicitly approves an integration.
- Put the API behind a private network, reverse proxy and enterprise identity provider.
- Rotate `BATTERY_SAFETY_API_KEY`; never commit secrets.
- Prefer one-way/read-only collection from BMS, UPS, PLC, SNMP, Modbus or OPC UA gateways.
- Segment OT and IT networks; do not expose battery controllers directly to the public Internet.
- Forward logs to the organization's SIEM and retain an immutable incident/audit trail.
- Validate sensor authenticity, timestamp freshness and range plausibility before using data operationally.

Report security issues privately to the repository owner. Do not publish exploitable details in a public issue.
