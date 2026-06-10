import streamlit as st
import math
import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="SNTL — Edge AI Threat Reasoning Agent",
    page_icon="🛡️",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0a0a0a; }
    .stApp { background-color: #0a0a0a; color: #00ff88; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ SNTL — Edge AI Threat Reasoning Agent")
st.caption("Microsoft Foundry IQ · Agents League Hackathon 2026 · Built for African network environments")

def compute_capacity(snr_db):
    snr_linear = 10 ** (snr_db / 10)
    return round(5.0 * math.log2(1 + snr_linear), 2)

def run_agent(rsrp, snr, accel, voltage):
    endpoint = st.secrets.get("AZURE_PROJECT_ENDPOINT") or os.getenv("AZURE_PROJECT_ENDPOINT")
    agent_id = st.secrets.get("AZURE_AGENT_ID") or os.getenv("AZURE_AGENT_ID")
    api_key = st.secrets.get("AZURE_API_KEY") or os.getenv("AZURE_API_KEY")

    headers = {
        "api-key": api_key,
        "Content-Type": "application/json"
    }
    base = endpoint.rstrip("/")
    API_VERSION = "?api-version=v1"

    prompt = f"""Analyze this telemetry event and classify the threat:

INCOMING TELEMETRY EVENT
------------------------
RSRP: {rsrp} dBm
SNR: {snr} dB
Computed Channel Capacity: {compute_capacity(snr)} Mbps
Accelerometer Z-axis: {accel}g
Battery Voltage: {voltage}V

Respond using exactly 4 stages:
STAGE 1 | SIGNAL ANALYSIS
STAGE 2 | CROSS-SENSOR CORRELATION
STAGE 3 | THREAT CLASSIFICATION
STAGE 4 | RESPONSE RECOMMENDATION"""

    try:
        # Create thread
        r = requests.post(f"{base}/threads{API_VERSION}", headers=headers, json={})
        r.raise_for_status()
        thread_id = r.json()["id"]

        # Add message
        requests.post(f"{base}/threads/{thread_id}/messages{API_VERSION}", headers=headers,
                      json={"role": "user", "content": prompt})

        # Create run
        r = requests.post(f"{base}/threads/{thread_id}/runs{API_VERSION}", headers=headers,
                          json={"assistant_id": agent_id})
        r.raise_for_status()
        run_id = r.json()["id"]

        # Poll for completion
        for _ in range(30):
            time.sleep(2)
            r = requests.get(f"{base}/threads/{thread_id}/runs/{run_id}{API_VERSION}", headers=headers)
            status = r.json().get("status")
            if status == "completed":
                break
            if status in ["failed", "cancelled", "expired"]:
                return f"Run failed with status: {status}"

        # Get messages
        r = requests.get(f"{base}/threads/{thread_id}/messages{API_VERSION}", headers=headers)
        messages = r.json().get("data", [])
        for msg in messages:
            if msg["role"] == "assistant":
                return msg["content"][0]["text"]["value"]

        return "No response received"

    except Exception as e:
        return f"Error: {str(e)[:150]}"

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📡 Sensor Input")
    rsrp = st.slider("RSRP (dBm)", -140, -40, -90)
    snr = st.slider("SNR (dB)", -20, 30, 18)
    accel = st.slider("Accelerometer Z-axis (g)", 0.5, 7.0, 1.0)
    voltage = st.slider("Battery Voltage (V)", 2.5, 4.5, 3.9)
    st.metric("Channel Capacity", f"{compute_capacity(snr)} Mbps")

    st.subheader("⚡ Preset Scenarios")
    if st.button("🟢 NORMAL", use_container_width=True):
        st.session_state.update({"rsrp": -90, "snr": 18, "accel": 1.0, "voltage": 3.9})
    if st.button("🔵 ENVIRONMENTAL DEAD ZONE", use_container_width=True):
        st.session_state.update({"rsrp": -123, "snr": 3, "accel": 1.0, "voltage": 3.85})
    if st.button("🟡 FALSE POSITIVE", use_container_width=True):
        st.session_state.update({"rsrp": -91, "snr": 16, "accel": 2.8, "voltage": 3.95})
    if st.button("🔴 HOSTILE TAMPER", use_container_width=True):
        st.session_state.update({"rsrp": -132, "snr": -5, "accel": 4.5, "voltage": 3.1})

    run_analysis = st.button("▶ RUN FOUNDRY IQ ANALYSIS", type="primary", use_container_width=True)

with col2:
    st.subheader("🧠 Foundry IQ Reasoning Engine")
    if run_analysis:
        with st.spinner("Foundry IQ agent reasoning through threat classification..."):
            result = run_agent(rsrp, snr, accel, voltage)
        st.markdown(result)
    else:
        st.info("Set sensor values and click RUN FOUNDRY IQ ANALYSIS to get live threat classification.")