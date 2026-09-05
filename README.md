# Spectre Meltdown Transient Agent

> **Domain:** Clinical Decision Support & Hardware Security  
> **Standards:** CAP / CLSI / ISO / CISA / CERT Speculative Execution Guidelines

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

Spectre Meltdown Transient Agent is a multi-agent orchestration platform that evaluates task payloads across specialized worker agents, producing cryptographically signed consensus dossiers. It provides:

- **Clinical & Biomedical AI** evaluation pipeline (Pydantic-based `agents` package)
- **Hardware Security** speculative execution verifier (dataclass-based `spectre_meltdown` package)
- **Zero-PHI Outbound Guard** preventing sensitive data leakage
- **HMAC-SHA256 Tamper-Evident Audit Trail** with signature verification
- **FastAPI REST API** with Prometheus telemetry

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED_RISK, CRITICAL_STAT_PANIC) with automated action recommendations.
- **Validation & Guardrails**: Input bounds checking, control character sanitization, and anomaly detection.
- **Multi-Worker Consensus**: InvariantQCWorker, SafetyEscalationWorker, ProtocolConformanceWorker.

---

## 💻 Installation

```bash
pip install -e .
# For web/API support:
pip install -e ".[web]"
# For development:
pip install -e ".[dev]"
```

---

## 💻 CLI Quickstart & Usage

### 1. Single Task Evaluation
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Supervisory Chat Query
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Parameter Reference
| Argument | Description | Default |
|:---------|:------------|:--------|
| `--task-id` | Unique task identifier | `TASK-2026-001` |
| `--target` | Target entity identifier | `KEY-TARGET-01` |
| `--primary` | Primary measurement (float) | `28.5` |
| `--secondary` | Secondary metric (float) | `14.2` |
| `--critical` | Flag as critical | `False` |
| `--status` | Status descriptor | `DISCORDANT` |

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `task_id` | Parameter / observation metric | Required, max 128 chars |
| `target_identifier` | Parameter / observation metric | Required, max 128 chars |
| `primary_metric` | Primary measurement value | Required (float) |
| `secondary_metric` | Secondary measurement value | Optional (float) |
| `is_critical_flag` | Emergency escalation flag | Optional (bool) |
| `status_descriptor` | Status code descriptor | Optional, max 64 chars |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs with full signature verification for every evaluation.
* **Input Sanitization:** Control character stripping, length limits, and whitespace normalization on all text fields.
* **Secure Defaults:** Random session-based HMAC keys (no hardcoded secrets in source code).
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py -n 1000
```

---

## 🐳 Container Deployment

```bash
docker build -t spectre-meltdown-transient-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key spectre-meltdown-transient-agent
```

Or with Docker Compose:

```bash
docker-compose up -d
```

---

## 📁 Project Structure

```
spectre_meltdown_transient_agent/
├── agents/                  # Clinical & Biomedical AI package
│   ├── api.py               # FastAPI REST endpoints
│   ├── base.py              # Security, PHI guard, HMAC audit
│   ├── models.py            # Pydantic schemas with validation
│   ├── supervisor.py        # Multi-agent orchestrator
│   ├── workers.py           # Specialized evaluation workers
│   ├── llm_factory.py       # LLM provider abstraction
│   ├── metrics.py           # Prometheus metrics collector
│   ├── learning.py          # Bayesian calibration engine
│   └── streamer.py          # WebSocket telemetry broadcaster
├── spectre_meltdown/        # Hardware Security package
│   ├── agents.py            # Sub-agent coordinators
│   ├── engine.py            # Core algorithmic engine
│   ├── models.py            # Dataclass schemas
│   ├── cli.py               # Frontier CLI
│   └── server.py            # Frontier FastAPI server
├── tests/                   # Pytest test suite
├── web/index.html           # Operations console UI
├── cli.py                   # Main CLI entry point
├── simulator.py             # Load testing simulator
├── enrichment.py            # Domain enrichment engines
├── Dockerfile               # Container build
└── docker-compose.yml       # Container orchestration
```
