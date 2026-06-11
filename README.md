# SNTL — Edge AI Threat Reasoning Agent

> A multi-agent system that certifies field device integrity for network
> engineers operating in degraded African network environments — using
> grounded reasoning via Microsoft Foundry IQ to classify RF and sensor
> telemetry before field deployment.

**Agents League Hackathon 2026 · Reasoning Agents Track · Microsoft Foundry**

🚀 **[Live Demo → sntl-agent.streamlit.app](https://sntl-agent.streamlit.app)**

---

## The Problem

Telecoms field engineers across Africa deploy and maintain network equipment
in environments where signal degradation, physical tampering, and hostile RF
conditions are routine. Before deployment, engineers need to certify that their
devices are operating within safe signal parameters — but standard tools assume
persistent cloud connectivity that simply does not exist in many African field
environments.

When a device is physically tampered with or enters a hostile RF environment,
the cloud connection dies first. HTTP timeout loops are too slow. The device
goes dark before any certification alert is sent.

## What SNTL Does

SNTL is a multi-agent field certification system that monitors raw RF telemetry
(RSRP, SNR) and on-device sensor data (accelerometer, voltage) to assess device
integrity and certify field readiness — then triggers a compressed SOS payload
over USSD before complete hardware failure if a hostile event is detected.

It bypasses HTTP/TCP entirely, operating at OSI Layer 1–2 where 2G channels
survive when 4G has already dropped.

## Multi-Agent Architecture

SNTL implements a 4-agent pipeline. Each agent has a defined responsibility
and hands off to the next in sequence:

### Agent 1 — Signal Analysis Agent

**Responsibility:** Evaluate incoming RF telemetry (RSRP, SNR) and compute
channel capacity using the Shannon-Hartley theorem.  
**Grounding:** Queries Foundry IQ for RF degradation signatures and normal
variance thresholds.  
**Output:** Signal anomaly verdict + computed channel capacity (Mbps)

### Agent 2 — Correlation Agent

**Responsibility:** Cross-reference accelerometer and voltage readings against
the RF anomaly verdict from Agent 1.  
**Grounding:** Queries Foundry IQ for sensor correlation rules that distinguish
physical tamper from environmental dead zones.  
**Output:** Correlation verdict — tamper hypothesis confirmed or rejected

### Agent 3 — Classification Agent

**Responsibility:** Classify the device event into one of four certification
states based on combined signal and sensor evidence.  
**Grounding:** Queries Foundry IQ threat taxonomy for cited classification rules.  
**Output:** Certification level with confidence score

| Level | Classification | Trigger Conditions |
|-------|---------------|-------------------|
| 3 | 🔴 HOSTILE TAMPER | RSRP ≤ -115, SNR ≤ 0, Accel > 2.0g, Voltage < 3.4V |
| 2 | 🟡 FALSE POSITIVE | Accel > 2.0g, RSRP > -105, Voltage ≥ 3.5V |
| 1 | 🔵 ENVIRONMENTAL DEAD ZONE | RSRP ≤ -110, SNR ≤ 5, Accel < 1.5g, Voltage > 3.5V |
| 0 | 🟢 NORMAL | All other conditions |

### Agent 4 — Response Agent

**Responsibility:** Recommend and execute the appropriate field response based
on the classification from Agent 3.  
**Grounding:** Queries Foundry IQ for response protocols mapped to each
certification level.  
**Output:** Recommended action — continue, hold, or dispatch USSD SOS payload

---

## Orchestration Flow

```
Field Engineer Device
        ↓
Raw Telemetry (RSRP · SNR · Accelerometer · Voltage)
        ↓
┌─────────────────────────────────┐
│  Agent 1: Signal Analysis       │ ← Foundry IQ: RF Signatures
│  Shannon-Hartley computation    │
└────────────────┬────────────────┘
                 ↓
┌─────────────────────────────────┐
│  Agent 2: Correlation           │ ← Foundry IQ: Sensor Rules
│  RF + Sensor cross-reference    │
└────────────────┬────────────────┘
                 ↓
┌─────────────────────────────────┐
│  Agent 3: Classification        │ ← Foundry IQ: Threat Taxonomy
│  Level 0–3 with confidence %    │
└────────────────┬────────────────┘
                 ↓
┌─────────────────────────────────┐
│  Agent 4: Response              │ ← Foundry IQ: Response Protocols
│  Action recommendation          │
│  USSD SOS dispatch if Level 3   │
└────────────────┬────────────────┘
                 ↓
     Streamlit Dashboard
  (sntl-agent.streamlit.app)
```

---

## How Foundry IQ Powers SNTL

Foundry IQ serves as the grounded knowledge retrieval layer across all 4 agents.
The knowledge base contains three synthetic documents:

- **Threat Taxonomy** — classification rules for all 4 threat levels
- **RF Degradation Signatures** — known signal patterns for tamper vs dead zone
- **Sensor Correlation Rules** — how accelerometer and voltage relate to RF events

At each reasoning step, the active agent queries Foundry IQ for cited, grounded
context before making a decision. This eliminates hallucination in a
safety-critical setting where a false negative means silence during a real attack.

---

## Reasoning Chain

1. **Signal Analysis** — Is this RF drop within normal variance or anomalous?
2. **Cross-sensor Correlation** — Does accelerometer/voltage data confirm it?
3. **Threat Classification** — Hostile tamper, environmental dead zone, or false positive?
4. **Response Recommendation** — Compress and transmit, hold, or discard?

## Knowledge Base (Synthetic Data)

All data used in this project is synthetic and for demonstration purposes only.
No real customer data, PII, or proprietary information is included.

The Foundry IQ knowledge base contains:

- `threat_taxonomy.md` — synthetic threat classification rules
- `rf_degradation_signatures.md` — synthetic RF signal patterns
- `sensor_correlation_rules.md` — synthetic sensor-RF correlation rules

---

## Architecture

```
Raw Telemetry (RSRP · SNR · Accelerometer · Voltage)
                        ↓
            Python Telemetry Simulator
                        ↓
         Azure AI Foundry — SNTL-Reasoning-Agent
                        ↓
          Microsoft Foundry IQ (Knowledge Base)
          · Threat Taxonomy
          · RF Degradation Signatures
          · Sensor Correlation Rules
                        ↓
         4-Stage Reasoning Output
         STAGE 1 Signal Analysis
         STAGE 2 Cross-Sensor Correlation
         STAGE 3 Threat Classification
         STAGE 4 Response Recommendation
                        ↓
              Streamlit Dashboard
         (Live at sntl-agent.streamlit.app)
                        ↓
        USSD SOS Payload Dispatch (Layer 1-2)
```

## Stack

- **Microsoft Foundry IQ** — grounded knowledge retrieval
- **Azure AI Foundry** — agent orchestration (Sweden Central)
- **Python** — telemetry simulation + agent logic
- **Streamlit** — live demo dashboard

## Repository Structure

```
SNTL/
├── agent/
│   └── sntl_agent.py          # 4-agent reasoning pipeline
├── data/
│   └── telemetry_simulator.py # Synthetic telemetry generator
├── knowledge/
│   ├── threat_taxonomy.md
│   ├── rf_degradation_signatures.md
│   └── sensor_correlation_rules.md
├── dashboard/
│   └── dashboard.html         # Frontend dashboard (Kesar Bavaria)
├── streamlit_app.py           # Live demo interface
├── requirements.txt
└── README.md
```

---

## Responsible AI

SNTL is designed with safety-critical deployment in mind. Three core
guardrails are built into the multi-agent pipeline:

- **False Positive Protection:** Agent 3 applies a strict 4-condition
  classification threshold before escalating to Level 3 HOSTILE TAMPER.
  A single anomalous sensor reading is never sufficient — all four
  conditions (RSRP, SNR, accelerometer, voltage) must breach their
  respective thresholds simultaneously. This prevents wasted alerts
  and unnecessary USSD dispatch in noisy environments.

- **Human Oversight:** SNTL recommends and prepares the USSD SOS payload
  but surfaces the classification reasoning transparently at every stage.
  The confidence score and 4-stage reasoning chain are always visible to
  the operator before any action is taken. No alert is dispatched without
  a clear, cited justification from the Foundry IQ knowledge base.

- **Observability and Telemetry:** All agent runs are logged automatically
  via Azure AI Foundry's built-in telemetry. Agent run volume, success
  rates, token usage, and response latency are tracked in the Foundry
  Operate dashboard — providing full auditability of every classification
  decision made by the pipeline.

All data used in this system is synthetic. No real user data, PII, or
proprietary network information is included in any part of the pipeline.

## Built by

[Ayomide Adesanya](https://linkedin.com/in/adesanya-ayomide)
Edge AI & Signal Processing · Lagos, Nigeria

[Kesar Bavaria](https://linkedin.com/in/kesar-bavaria-140707kb)
Frontend Engineer · Dashboard Design
