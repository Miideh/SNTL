# SNTL — Edge AI Threat Reasoning Agent

> A multi-step reasoning agent that classifies physical device tamper
> events from raw RF and sensor telemetry — built for extreme network
> environments where the cloud is unreachable and 2G is the last line
> of communication.

**Agents League Hackathon 2026 · Reasoning Agents Track · Microsoft Foundry**

🚀 **[Live Demo → sntl-agent.streamlit.app](https://sntl-agent.streamlit.app)**

---

## The Problem

In high-risk environments across Africa, standard mobile security apps
fail at the worst moment. When a device is physically tampered with,
the cloud connection dies first. HTTP timeout loops are too slow.
The device goes dark before any alert is sent.

## What SNTL Does

SNTL monitors raw RF telemetry (RSRP, SNR) and on-device sensor data
(accelerometer, voltage) to detect hostile tamper events — then triggers
a compressed SOS payload over USSD before complete hardware failure.

It bypasses HTTP/TCP entirely, operating at OSI Layer 1–2 where 2G
channels survive when 4G has already dropped.

## How Foundry IQ Powers It

Foundry IQ serves as the grounded knowledge retrieval layer — storing
the threat taxonomy, RF degradation signatures, and sensor correlation
rules. At each reasoning step, the agent queries Foundry IQ for cited,
grounded context before making a classification decision.

## Reasoning Chain

1. **Signal Analysis** — Is this RF drop within normal variance or anomalous?
2. **Cross-sensor Correlation** — Does accelerometer/voltage data confirm it?
3. **Threat Classification** — Hostile tamper, environmental dead zone, or false positive?
4. **Response Recommendation** — Compress and transmit, hold, or discard?

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

## Threat Classification Levels

| Level | Classification | Trigger Conditions |
|-------|---------------|-------------------|
| 3 | 🔴 HOSTILE TAMPER | RSRP ≤ -115, SNR ≤ 0, Accel > 2.0g, Voltage < 3.4V |
| 2 | 🟡 FALSE POSITIVE | Accel > 2.0g, RSRP > -105, Voltage ≥ 3.5V |
| 1 | 🔵 ENVIRONMENTAL DEAD ZONE | RSRP ≤ -110, SNR ≤ 5, Accel < 1.5g, Voltage > 3.5V |
| 0 | 🟢 NORMAL | All other conditions |

## Stack

- **Microsoft Foundry IQ** — grounded knowledge retrieval
- **Azure AI Foundry** — agent orchestration (Sweden Central)
- **Python** — telemetry simulation + agent logic
- **Streamlit** — live demo dashboard

## Built by

[Ayomide Adesanya](https://linkedin.com/in/adesanya-ayomide)
Edge AI & Signal Processing · Lagos, Nigeria

[Kesar Bavaria](https://linkedin.com/in/kesar-bavaria-140707kb)
Frontend Engineer · Dashboard Design
