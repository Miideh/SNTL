# RF Degradation Signatures

## Normal Degradation (Environmental)

- Gradual RSRP decline over 5-30 seconds
- SNR degrades proportionally with RSRP
- No sudden step-changes
- Pattern: slow slope downward
- Example: driving into a tunnel, entering a basement

## Hostile RF Suppression

- Sudden RSRP drop of more than 20 dBm within 200ms
- SNR collapses independently of RSRP (jammer signature)
- Step-change pattern — not a slope
- May occur before physical tamper event

## SIM Ejection Signature

- Instantaneous RSRP drop to noise floor (-140 dBm or below)
- SNR becomes undefined or returns -999
- Accompanies voltage anomaly
- Accel-Z spike confirms physical action

## 2G Survival Window

- When RSRP is between -110 and -120 dBm, 2G/USSD channels
  remain viable while 4G/LTE has already dropped
- This is the transmission window for the SOS payload
- USSD requires minimum SNR of -7 dB to complete
- Payload must be transmitted within this window before
  RSRP falls below -125 dBm
