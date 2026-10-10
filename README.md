<p align="center">
  <img src="assets/hero-banner.svg" alt="Interview Copilot Banner" width="100%" />
</p>

# 🎙️ Interview Copilot Suite
### Low-Latency Streaming Audio Transcription, Knowledge Retrieval & Technical Assistant

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![WebSockets](https://img.shields.io/badge/WebSockets-Real--Time-010101?logo=socketdotio&logoColor=white)](https://websockets.readthedocs.io/)
[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)](https://python.org)
[![Whisper STT](https://img.shields.io/badge/Whisper-Low--Latency_STT-green?logo=openai&logoColor=white)](https://github.com/openai/whisper)
[![Latency](https://img.shields.io/badge/Latency-Sub--500ms-00e676?style=flat)](https://github.com/omniversodigital/interview-copilot)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Interview Copilot Suite** is a low-latency, real-time AI assistant and speech-to-text transcription engine. It captures system loopback audio, transcribes live speech, evaluates conversation context, and retrieves verified architectural concepts in sub-second inference cycles.

---

## 🏛️ System Architecture

```mermaid
flowchart LR
    classDef audio fill:#1a237e,stroke:#3949ab,stroke-width:2px,color:#fff
    classDef stt fill:#004d40,stroke:#00897b,stroke-width:2px,color:#fff
    classDef rag fill:#bf360c,stroke:#ff7043,stroke-width:2px,color:#fff
    classDef ui fill:#263238,stroke:#546e7a,stroke-width:2px,color:#fff

    Mic["Microphone / Loopback Audio Stream"]:::audio --> PyAudio["PyAudio Circular Buffer (16kHz PCM)"]:::audio
    PyAudio --> Whisper["Whisper Real-Time Streaming STT"]:::stt
    Whisper --> Engine["Contextual Knowledge Engine"]:::rag
    
    subgraph KB ["Indexed Knowledge Base"]
        Engine <--> VectorKB["Indexed Architectural Topics (knowledge_base.json)"]:::rag
    end

    Engine --> WebSocket["FastAPI WebSocket Broadcaster (/ws/transcribe)"]:::ui
    WebSocket --> Overlay["Stealth Real-Time HUD Overlay / Browser UI"]:::ui
```

---

## ⚡ Core Capabilities

- **Sub-500ms Speech Ingestion**: Streaming circular buffer with voice activity detection (VAD) minimizes speech turnaround time.
- **Semantic Domain Matching**: Real-time evaluation against a curated knowledge base covering systems design, distributed consensus, policy latency, and microservices architecture.
- **Stealth Floating HUD**: Low-memory GUI overlay rendered over active coding environments with minimal window-switching friction.
- **WebSocket Event Bus**: Full bi-directional streaming protocol supporting multiple simultaneous subscriber interfaces.

---

## 📡 API Specification

| Endpoint | Method | Description |
| :--- | :---: | :--- |
| `/` | `GET` | Serves the glassmorphic real-time Copilot console interface |
| `/api/topics` | `GET` | Returns all pre-indexed technical system architecture topics |
| `/api/query` | `POST` | Performs semantic question matching with confidence scoring |
| `/ws/transcribe` | `WS` | Streaming WebSocket for real-time speech packets and AI responses |

---

## 🛠️ Quickstart Guide

### 1. Installation
```bash
git clone https://github.com/omniversodigital/interview-copilot.git
cd interview-copilot

pip install -r requirements.txt || uv pip install -r requirements.txt
```

### 2. Launch the Copilot Server
```bash
python server.py
# Server runs locally on http://127.0.0.1:8888
```

### 3. Run Automated Endpoint Verification
```bash
python test_copilot.py
```

---

## 📄 License
MIT License © Omniverso Digital. All rights reserved.
