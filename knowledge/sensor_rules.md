# Cross-Sensor Correlation Rules

## Rule 1 — Single Sensor Anomaly: IGNORE

If only one sensor is anomalous, do not classify as threat.

- RF drop alone = environmental
- Accel spike alone = user movement
- Voltage drop alone = normal battery discharge

## Rule 2 — Two Sensor Anomaly: MONITOR

If two sensors are anomalous simultaneously, elevate to watch state.

- RF + Accel = possible physical move into dead zone
- RF + Voltage = possible hardware fault
- Accel + Voltage = possible impact damage

## Rule 3 — Three Sensor Anomaly: HOSTILE TAMPER

If RF + Accel + Voltage all anomalous within 500ms window:

- Classify immediately as LEVEL 3 Hostile Tamper
- Begin payload compression
- Transmit via USSD within available window

## Rule 4 — Correlation Window

All anomalies must occur within 500 milliseconds of each other.
An RF drop at T=0 and an Accel spike at T=3000ms are unrelated events.

## Rule 5 — False Positive Override

If Accel-Z spikes but RSRP remains above -105 dBm AND
voltage remains above 3.5V:

- Classify as false positive regardless of spike magnitude
- Log and continue monitoring
