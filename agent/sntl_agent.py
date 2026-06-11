import sys
import os
import time
import math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.telemetry_simulator import TelemetryEvent, generate_event
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

def compute_channel_capacity(snr_db: float, bandwidth_mhz: float = 5.0) -> float:
    snr_linear = 10 ** (snr_db / 10)
    capacity = bandwidth_mhz * math.log2(1 + snr_linear)
    return round(capacity, 2)

def format_telemetry(event: TelemetryEvent) -> str:
    capacity = compute_channel_capacity(event.snr)
    return f"""INCOMING TELEMETRY EVENT
------------------------
RSRP: {event.rsrp:.1f} dBm
SNR: {event.snr:.1f} dB
Computed Channel Capacity: {capacity} Mbps
Accelerometer Z-axis: {event.accel_z:.2f}g
Battery Voltage: {event.voltage:.2f}V"""

def run_sntl_agent(event: TelemetryEvent) -> str:
    # Support both naming conventions
    endpoint = (
        os.getenv("AZURE_PROJECT_ENDPOINT") or
        os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    )
    agent_id = (
        os.getenv("AZURE_AGENT_ID") or
        os.getenv("AZURE_AI_AGENT_ID")
    )

    client = AgentsClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential()
    )

    telemetry = format_telemetry(event)

    for attempt in range(3):
        try:
            thread = client.threads.create()

            client.messages.create(
                thread_id=thread.id,
                role="user",
                content=f"""Analyze this telemetry event and classify the threat:

{telemetry}

Respond using exactly 4 stages:
STAGE 1 | SIGNAL ANALYSIS
STAGE 2 | CROSS-SENSOR CORRELATION
STAGE 3 | THREAT CLASSIFICATION
STAGE 4 | RESPONSE RECOMMENDATION"""
            )

            run = client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent_id
            )

            messages = client.messages.list(thread_id=thread.id)
            for msg in messages:
                if msg.role == "assistant":
                    return msg.content[0].text.value

            return f"Run status: {run.status}"

        except Exception as e:
            if attempt < 2:
                print(f"  Attempt {attempt+1} failed, retrying...")
                time.sleep(3)
            else:
                return f"Error after 3 attempts: {str(e)[:100]}"

if __name__ == "__main__":
    scenarios = ["normal", "environmental_dead_zone", "hostile_tamper", "false_positive"]

    for scenario in scenarios:
        event = generate_event(scenario)
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario.upper()}")
        print(format_telemetry(event))
        print("\nFOUNDRY IQ AGENT REASONING:")
        print("-" * 40)
        result = run_sntl_agent(event)
        print(result)