# Safety case and operating constraints

## Intended use

Early detection, risk prioritization, operator decision support, trend analysis, incident logging and predictive maintenance for stationary batteries used in telecom/data-center environments.

## Not intended use

The service must not independently open contactors, disable UPS systems, discharge extinguishing agents, stop ventilation or perform any other physical safety action. Those actions belong to validated BMS/PLC/fire protection systems and approved site procedures.

## Hazards considered

- cell/module overheating and abnormal temperature rise
- thermal propagation precursors for lithium systems
- hydrogen/off-gas accumulation
- abnormal voltage spread or pack deviation
- rising internal resistance / degradation
- smoke or upstream BMS alarms
- sensor failure, stale data and missing telemetry
- false positive / false negative AI assessments
- cyber compromise of telemetry or operator workflow

## Controls

- recommendation-only default; `control_permitted=false` in every assessment
- deterministic escalation of smoke/BMS alarm evidence to CRITICAL
- chemistry-specific analytics profiles (LFP, NMC, VRLA)
- transparent factor-level risk explanation
- input bounds and schema validation
- authenticated write API in production
- durable incident log and operator acknowledgement
- fail-safe design: loss of the AI service must not disable primary protection

## Standards reference set

Engineering teams should validate the final system against the applicable editions and local authority requirements, including IEC 62619 for industrial lithium batteries, IEC 63056 for stationary energy storage, NFPA 855 where adopted/used as a design reference, UL 9540A test evidence for thermal-runaway propagation where applicable, IEEE 1188 for VRLA maintenance/testing, and Bangladesh National Building Code / fire authority requirements.

Referencing a standard here is not a claim of certification or compliance.
