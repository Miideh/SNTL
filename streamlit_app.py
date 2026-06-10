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
    .stApp { background-color: #0a0a0a; color: #00ff88; }
    .stSlider > div { color: #00ff88; }
    div[data-testid="stMetricValue"] { color: #00ff88; }
    .preset-active { background-color: #00ff88 !important; color: #000 !important; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ SNTL — Edge AI Threat Reasoning Agent")
st.caption("Microsoft Foundry IQ · Agents League Hackathon 2026 · Built for African network environments")

# Initialize session state
if "rsrp" not in st.session_state:
    st.session_state.rsrp = -90.0
if "snr" not in st.session_state:
    st.session_state.snr = 18.0
if "accel" not in st.session_state:
    st.session_state.accel = 1.0
if "voltage" not in st.session_state:
    st.session_state.voltage = 3.9
if "active_preset" not in st.session_state:
    st.session_state.active_preset = None

def compute_capacity(snr_db):
    snr_linear = 10 ** (snr_db / 10)
    return round(5.0 * math.log2(1 + snr_linear), 2)

def get_bearer_token():
    tenant_id = st.secrets.get("AZURE_TENANT_ID") or os.getenv("AZURE_TENANT_ID")
    client_id = st.secrets.get("AZURE_CLIENT_ID") or os.getenv("AZURE_CLIENT_ID")
    client_secret = st.secrets.get("AZURE_CLIENT_SECRET") or os.getenv("AZURE_CLIENT_SECRET")
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://ai.azure.com/.default"
    }
    r = requests.post(url, data=data)
    r.raise_for_status()
    return r.json()["access_token"]

def run_agent(rsrp, snr, accel, voltage):
    endpoint = st.secrets.get("AZURE_PROJECT_ENDPOINT") or os.getenv("AZURE_PROJECT_ENDPOINT")
    agent_id = st.secrets.get("AZURE_AGENT_ID") or os.getenv("AZURE_AGENT_ID")
    token = get_bearer_token()
    headers = {
        "Authorization": f"Bearer {token}",
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
        r = requests.post(f"{base}/threads{API_VERSION}", headers=headers, json={})
        r.raise_for_status()
        thread_id = r.json()["id"]

        requests.post(f"{base}/threads/{thread_id}/messages{API_VERSION}", headers=headers,
                      json={"role": "user", "content": prompt})

        r = requests.post(f"{base}/threads/{thread_id}/runs{API_VERSION}", headers=headers,
                          json={"assistant_id": agent_id})
        r.raise_for_status()
        run_id = r.json()["id"]

        for _ in range(30):
            time.sleep(2)
            r = requests.get(f"{base}/threads/{thread_id}/runs/{run_id}{API_VERSION}", headers=headers)
            status = r.json().get("status")
            if status == "completed":
                break
            if status in ["failed", "cancelled", "expired"]:
                return f"Run failed with status: {status}"

        r = requests.get(f"{base}/threads/{thread_id}/messages{API_VERSION}", headers=headers)
        messages = r.json().get("data", [])
        for msg in messages:
            if msg["role"] == "assistant":
                return msg["content"][0]["text"]["value"]

        return "No response received"

    except Exception as e:
        return f"Error: {str(e)[:200]}"

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📡 Sensor Input")

    rsrp = st.slider("RSRP (dBm)", -140, -40,
                     value=int(st.session_state.rsrp), key="slider_rsrp")
    snr = st.slider("SNR (dB)", -20, 30,
                    value=int(st.session_state.snr), key="slider_snr")
    accel = st.slider("Accelerometer Z-axis (g)", 0.5, 7.0,
                      value=float(st.session_state.accel), key="slider_accel")
    voltage = st.slider("Battery Voltage (V)", 2.5, 4.5,
                        value=float(st.session_state.voltage), key="slider_voltage")
    st.metric("Channel Capacity", f"{compute_capacity(snr)} Mbps")

    st.subheader("⚡ Preset Scenarios")

    presets = {
    "🟢 NORMAL": {"rsrp": -90, "snr": 18, "accel": 1.0, "voltage": 3.9},
    "🔵 ENVIRONMENTAL DEAD ZONE": {"rsrp": -123, "snr": 3, "accel": 1.0, "voltage": 3.85},
    "🟡 FALSE POSITIVE": {"rsrp": -91, "snr": 16, "accel": 2.8, "voltage": 3.95},
    "🔴 HOSTILE TAMPER": {"rsrp": -132, "snr": -5, "accel": 4.5, "voltage": 3.1},
}

    for label, values in presets.items():
        is_active = st.session_state.active_preset == label
        if st.button(
            f"{'✅ ' if is_active else ''}{label}",
            use_container_width=True,
            type="primary" if is_active else "secondary"
        ):
            st.session_state.rsrp = values["rsrp"]
            st.session_state.snr = values["snr"]
            st.session_state.accel = values["accel"]
            st.session_state.voltage = values["voltage"]
            st.session_state.active_preset = label
            st.rerun()

    run_analysis = st.button("▶ RUN FOUNDRY IQ ANALYSIS", type="primary", use_container_width=True)

with col2:
    st.subheader("🧠 Foundry IQ Reasoning Engine")
    if st.session_state.active_preset:
        st.caption(f"Active scenario: **{st.session_state.active_preset}**")
    if run_analysis:
        with st.spinner("Foundry IQ agent reasoning through threat classification..."):
            result = run_agent(
                st.session_state.rsrp,
                st.session_state.snr,
                st.session_state.accel,
                st.session_state.voltage
            )
        st.markdown(result)
    else:
        st.info("Select a preset or set sensor values, then click RUN FOUNDRY IQ ANALYSIS.")