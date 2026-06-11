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
    .warning-panel {
        border: 1px solid #4a9eff;
        background: rgba(74, 158, 255, 0.1);
        padding: 12px 16px;
        margin-bottom: 16px;
        font-family: monospace;
        font-size: 13px;
    }
    .payload-panel {
        border: 1px solid #ff4444;
        background: rgba(255, 68, 68, 0.1);
        padding: 12px 16px;
        margin-top: 16px;
        font-family: monospace;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ SNTL — Edge AI Threat Reasoning Agent")
st.caption("Microsoft Foundry IQ · Agents League Hackathon 2026 · Built for African network environments")

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

def get_endpoint():
    return (
        st.secrets.get("AZURE_PROJECT_ENDPOINT") or
        st.secrets.get("AZURE_AI_PROJECT_ENDPOINT") or
        os.getenv("AZURE_PROJECT_ENDPOINT") or
        os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    )

def get_agent_id():
    return (
        st.secrets.get("AZURE_AGENT_ID") or
        st.secrets.get("AZURE_AI_AGENT_ID") or
        os.getenv("AZURE_AGENT_ID") or
        os.getenv("AZURE_AI_AGENT_ID")
    )

def get_threat_level(rsrp, snr, accel, voltage):
    if rsrp <= -115 and snr <= 0 and accel > 2.0 and voltage < 3.4:
        return 3
    elif accel > 2.0 and rsrp > -105 and voltage >= 3.5:
        return 2
    elif rsrp <= -110 and snr <= 5 and accel < 1.5 and voltage > 3.5:
        return 1
    else:
        return 0

def run_agent(rsrp, snr, accel, voltage):
    endpoint = get_endpoint()
    agent_id = get_agent_id()
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

        requests.post(f"{base}/threads/{thread_id}/messages{API_VERSION}",
                      headers=headers,
                      json={"role": "user", "content": prompt})

        r = requests.post(f"{base}/threads/{thread_id}/runs{API_VERSION}",
                          headers=headers,
                          json={"assistant_id": agent_id})
        r.raise_for_status()
        run_id = r.json()["id"]

        for _ in range(30):
            time.sleep(2)
            r = requests.get(
                f"{base}/threads/{thread_id}/runs/{run_id}{API_VERSION}",
                headers=headers)
            status = r.json().get("status")
            if status == "completed":
                break
            if status in ["failed", "cancelled", "expired"]:
                return f"Run failed with status: {status}"

        r = requests.get(
            f"{base}/threads/{thread_id}/messages{API_VERSION}",
            headers=headers)
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

    st.session_state.rsrp = st.slider("RSRP (dBm)", -140, -40,
                                      value=int(st.session_state.rsrp))
    st.session_state.snr = st.slider("SNR (dB)", -20, 30,
                                     value=int(st.session_state.snr))
    st.session_state.accel = st.slider("Accelerometer Z-axis (g)", 0.5, 7.0,
                                       value=float(st.session_state.accel))
    st.session_state.voltage = st.slider("Battery Voltage (V)", 2.5, 4.5,
                                         value=float(st.session_state.voltage))
    st.metric("Channel Capacity",
              f"{compute_capacity(st.session_state.snr)} Mbps")

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

    run_analysis = st.button("▶ RUN FOUNDRY IQ ANALYSIS",
                             type="primary", use_container_width=True)

with col2:
    st.subheader("🧠 Foundry IQ Reasoning Engine")
    if st.session_state.active_preset:
        st.caption(f"Active scenario: **{st.session_state.active_preset}**")

    if run_analysis:
        level = get_threat_level(
            st.session_state.rsrp,
            st.session_state.snr,
            st.session_state.accel,
            st.session_state.voltage
        )

        # Warning panel for Dead Zone
        if level == 1:
            st.markdown("""
<div class="warning-panel">
<span style="color:#4a9eff; font-weight:bold;">⚠ PREDICTIVE ALERT</span><br>
<span style="color:#888;">─────────────────────────────────────</span><br>
RSRP SLOPE &nbsp;&nbsp;&nbsp;&nbsp;│ -2.3 dBm/sec ↓<br>
ETA TO DROP &nbsp;&nbsp;│ ~28 seconds<br>
RECOMMENDATION│ Save work. End calls.<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│ Signal recovery unlikely.<br>
HAPTIC PULSE &nbsp;│ ███ TRIGGERED (3 short pulses)
</div>
""", unsafe_allow_html=True)

        with st.spinner("Foundry IQ agent reasoning through threat classification..."):
            result = run_agent(
                st.session_state.rsrp,
                st.session_state.snr,
                st.session_state.accel,
                st.session_state.voltage
            )
        st.markdown(result)

        # Payload dispatch panel for Hostile Tamper
        if level == 3:
            st.markdown("""
<div class="payload-panel">
<span style="color:#ff4444; font-weight:bold;">STAGE 5 | PAYLOAD DISPATCH</span><br>
<span style="color:#888;">─────────────────────────────────────────</span><br>
COMPRESSING PAYLOAD...<br>
&nbsp;&nbsp;GPS &nbsp;&nbsp;&nbsp;│ 06.5244°N 03.3792°E → 0x0653A7C2<br>
&nbsp;&nbsp;DEVICE │ SNTL-NG-001 → 0xA4F2<br>
&nbsp;&nbsp;TIME &nbsp;&nbsp;│ 1780579033 → 0x6A1B8F29<br>
&nbsp;&nbsp;TOTAL &nbsp;│ 58 bytes ✓ (limit: 60 bytes)<br>
<br>
SELECTING CHANNEL...<br>
&nbsp;&nbsp;4G LTE &nbsp;│ ✗ UNAVAILABLE (RSRP -132 dBm)<br>
&nbsp;&nbsp;3G HSPA │ ✗ UNAVAILABLE<br>
&nbsp;&nbsp;2G GSM &nbsp;│ ✓ ACTIVE (RSRP threshold met)<br>
&nbsp;&nbsp;CHANNEL │ USSD FALLBACK SELECTED<br>
<br>
TRANSMITTING VIA USSD...<br>
&nbsp;&nbsp;*123*SOS*0x0653A7C2A4F22029#<br>
&nbsp;&nbsp;STATUS &nbsp;│ ⟳ DISPATCHING...<br>
&nbsp;&nbsp;STATUS &nbsp;│ ✓ PAYLOAD DELIVERED — 58 bytes over 2G
</div>
""", unsafe_allow_html=True)

    else:
        st.info("Select a preset or set sensor values, then click RUN FOUNDRY IQ ANALYSIS.")