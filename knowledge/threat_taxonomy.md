# SNTL Threat Taxonomy

## Threat Levels

### LEVEL 0 — Normal Operation

- RSRP between -80 and -100 dBm
- SNR between 10 and 25 dB
- Accel-Z between 0.9 and 1.1g (device stationary)
- Voltage between 3.6 and 4.2V
- No action required.

### LEVEL 1 — Environmental Dead Zone

- RSRP drops below -110 dBm
- SNR drops below 5 dB
- Accel-Z remains normal (0.9 to 1.1g) — device not physically disturbed
- Voltage remains stable
- Cause: geographic signal shadow, building interference, network outage
- Action: monitor and wait. Do NOT trigger SOS.

### LEVEL 2 — False Positive (Physical Impact, No Threat)

- Accel-Z spike above 2.0g
- RSRP and SNR remain within normal or mild degradation range
- Voltage stable
- Cause: device dropped, bumped, or moved by user
- Action: log event, do NOT trigger SOS.

### LEVEL 3 — Hostile Tamper (CRITICAL)

- RSRP drops below -115 dBm AND
- SNR drops below 0 dB AND
- Accel-Z spike above 2.0g AND
- Voltage drop below 3.4V
- All four conditions must correlate within a 500ms window
- Cause: SIM ejection, forced power removal, physical seizure of device
- Action: IMMEDIATELY compress and transmit SOS payload via USSD.

## The Shannon-Hartley Threshold

Channel capacity C = B * log2(1 + S/N).
When computed capacity drops below 10% of baseline within 200ms,
combined with accelerometer and voltage anomalies,
classify as LEVEL 3 regardless of individual thresholds.
