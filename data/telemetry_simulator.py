import random
import time
from dataclasses import dataclass
from typing import Literal

@dataclass
class TelemetryEvent:
    timestamp: float
    rsrp: float        # Reference Signal Received Power (dBm). Normal: -80 to -100
    snr: float         # Signal-to-Noise Ratio (dB). Normal: 10 to 25
    accel_z: float     # Accelerometer Z-axis force (g). Normal: 0.9 to 1.1
    voltage: float     # Battery voltage (V). Normal: 3.6 to 4.2
    scenario: str      # Label for what this event represents

def generate_event(scenario: Literal[
    "normal",
    "environmental_dead_zone",
    "hostile_tamper",
    "false_positive"
]) -> TelemetryEvent:

    if scenario == "normal":
        return TelemetryEvent(
            timestamp=time.time(),
            rsrp=random.uniform(-80, -95),
            snr=random.uniform(15, 25),
            accel_z=random.uniform(0.95, 1.05),
            voltage=random.uniform(3.8, 4.2),
            scenario=scenario
        )

    elif scenario == "environmental_dead_zone":
        # Signal drops but no physical disturbance
        return TelemetryEvent(
            timestamp=time.time(),
            rsrp=random.uniform(-115, -130),
            snr=random.uniform(-3, 5),
            accel_z=random.uniform(0.95, 1.05),  # steady — nobody touched it
            voltage=random.uniform(3.7, 4.1),
            scenario=scenario
        )

    elif scenario == "hostile_tamper":
        # RF drops AND physical spike AND voltage anomaly — all three together
        return TelemetryEvent(
            timestamp=time.time(),
            rsrp=random.uniform(-120, -140),
            snr=random.uniform(-10, 0),
            accel_z=random.uniform(2.5, 6.0),   # sudden force — device grabbed
            voltage=random.uniform(2.8, 3.3),   # drop — SIM ejected or power tampered
            scenario=scenario
        )

    elif scenario == "false_positive":
        # Strong force but signal and voltage are fine — user just dropped phone
        return TelemetryEvent(
            timestamp=time.time(),
            rsrp=random.uniform(-85, -100),
            snr=random.uniform(10, 20),
            accel_z=random.uniform(2.0, 4.0),   # impact but...
            voltage=random.uniform(3.7, 4.1),   # ...voltage is stable
            scenario=scenario
        )

def run_simulation(scenario: str, count: int = 5):
    print(f"\n--- Scenario: {scenario.upper()} ---")
    for _ in range(count):
        event = generate_event(scenario)
        print(f"  RSRP: {event.rsrp:.1f} dBm | "
              f"SNR: {event.snr:.1f} dB | "
              f"Accel-Z: {event.accel_z:.2f}g | "
              f"Voltage: {event.voltage:.2f}V")

if __name__ == "__main__":
    for s in ["normal", "environmental_dead_zone", "hostile_tamper", "false_positive"]:
        run_simulation(s)