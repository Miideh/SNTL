import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.telemetry_simulator import TelemetryEvent, generate_event
import math

# Shannon-Hartley channel capacity
def compute_channel_capacity(snr_db: float, bandwidth_mhz: float = 5.0) -> float:
    snr_linear = 10 ** (snr_db / 10)
    capacity = bandwidth_mhz * math.log2(1 + snr_linear)
    return round(capacity, 2)

# Format telemetry for the agent
def format_telemetry(event: TelemetryEvent) -> str:
    capacity = compute_channel_capacity(event.snr)
    return f"""INCOMING TELEMETRY EVENT
------------------------
Timestamp: {event.timestamp:.2f}
RSRP: {event.rsrp:.1f} dBm
SNR: {event.snr:.1f} dB
Computed Channel Capacity: {capacity} Mbps
Accelerometer Z-axis: {event.accel_z:.2f}g
Battery Voltage: {event.voltage:.2f}V
"""

# The simulated reasoning agent (Mocking Foundry/Gemini logic)
def run_sntl_agent(event: TelemetryEvent):
    capacity = compute_channel_capacity(event.snr)
    
    # STAGE 1: Signal Analysis
    if event.rsrp > -100 and event.snr > 10:
        stage1 = "RSRP and SNR are within normal operating parameters. Channel capacity is stable."
    elif event.rsrp <= -115 and event.snr <= 0:
        stage1 = "CRITICAL DROP: RSRP has fallen below -115 dBm and SNR is depleted. Channel capacity is nearing zero."
    else:
        stage1 = "Moderate signal degradation detected. RSRP and SNR are dropping."

    # STAGE 2: Cross-Sensor Correlation
    if event.accel_z > 2.0 and event.voltage < 3.4:
        stage2 = "ANOMALY CONFIRMED: High kinetic force (Accel-Z spike) correlates with a sudden voltage drop, indicating physical tampering or hardware removal."
    elif event.accel_z > 2.0 and event.voltage >= 3.5:
        stage2 = "Kinetic force detected (Accel-Z spike), but voltage remains stable. Likely a physical impact (dropped device) rather than hardware removal."
    elif event.accel_z < 1.5 and event.voltage > 3.6:
        stage2 = "Sensors stable. No physical disturbance or voltage anomaly detected."
    else:
        stage2 = "Sensors show slight variance but no critical correlation."

    # STAGE 3 & 4: Classification and Response
    # Hostile Tamper (Level 3)
    if event.rsrp <= -115 and event.snr <= 0 and event.accel_z > 2.0 and event.voltage < 3.4:
        stage3 = "Level 3 — HOSTILE TAMPER | Confidence: 98%"
        stage4 = "IMMEDIATELY compress and transmit SOS payload via USSD before complete hardware failure."
    # False Positive (Level 2)
    elif event.accel_z > 2.0 and event.rsrp > -105 and event.voltage >= 3.5:
        stage3 = "Level 2 — FALSE POSITIVE (Physical Impact) | Confidence: 92%"
        stage4 = "Log event. Do NOT trigger SOS. Monitor for secondary impacts."
    # Environmental Dead Zone (Level 1)
    elif event.rsrp <= -110 and event.snr <= 5 and event.accel_z < 1.5 and event.voltage > 3.5:
        stage3 = "Level 1 — ENVIRONMENTAL DEAD ZONE | Confidence: 89%"
        stage4 = "Monitor and wait. Do NOT trigger SOS. Attempt to reconnect when signal improves."
    # Normal (Level 0)
    else:
        stage3 = "Level 0 — NORMAL OPERATION | Confidence: 99%"
        stage4 = "No action required."

    return f"""STAGE 1 | SIGNAL ANALYSIS: {stage1}
STAGE 2 | CROSS-SENSOR CORRELATION: {stage2}
STAGE 3 | THREAT CLASSIFICATION: {stage3}
STAGE 4 | RESPONSE RECOMMENDATION: {stage4}"""

# Run all four scenarios
if __name__ == "__main__":
    scenarios = ["normal", "environmental_dead_zone", "hostile_tamper", "false_positive"]
    
    for scenario in scenarios:
        event = generate_event(scenario)
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario.upper()}")
        print(format_telemetry(event))
        print("AGENT REASONING:")
        print("-" * 40)
        result = run_sntl_agent(event)
        print(result)
        print()