# Spectre / Meltdown Transient Agent

A Python project containing two **illustrative metric-classification pipelines** and a static browser demo. Despite the repository name, this code does **not** probe speculative execution, measure cache timing, exploit vulnerabilities, enumerate microcode, or verify CPU mitigations. The rules use supplied numerical metrics and descriptor keywords; they are not established clinical or hardware-security thresholds.

## Browser demonstration

Open `web/index.html` in a modern browser (or use the GitHub Pages deployment after it has been enabled and verified). Enter a task identifier, target identifier, two metrics, a descriptor, and an optional critical flag. The browser returns a JSON report and allows exporting it.

- Runs entirely in JavaScript; no backend, account, or Pyodide is required.
- Thresholds: primary metric **> 25**; secondary metric **> 12**; critical flag overrides urgency; descriptor terms such as `ANOMALY`, `DISCORDANT`, `FAIL`, and `REJECT` raise warnings.
- Results are **not** signed and are not evidence of actual Spectre/Meltdown susceptibility.
- Page input is not transmitted to an API or stored by this application. Do **not** enter identifiable patient data or secrets.

The browser demo is distinct from the Python API and is intended for education and checking the example classification rules. Its JavaScript implementation mirrors the `agents` worker thresholds.

## Python installation

Requires Python 3.9 or newer.

```bash
python -m pip install -e ".[web,dev]"
python -m pytest -q
node --test tests/browser-smoke.cjs  # optional: Node.js 18+
```

To install only the core CLI, use `python -m pip install -e .`.

## Command line

```bash
spectre-meltdown-transient-agent audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --status DISCORDANT --critical
spectre-meltdown-transient-agent chat "What is the status?"
spectre-meltdown-transient-agent batch -i sample.csv -o results.csv
spectre-meltdown-transient-agent verify-audit

spectre-meltdown-frontier audit --primary 29.4 --secondary 15.1
python simulator.py -n 100
```

The main entry point invokes `cli:main` and the frontier entry point invokes `spectre_meltdown.cli:main`. The `agents` pipeline uses Pydantic models, three rule workers, an in-memory HMAC audit chain, and a deterministic mock chat adapter. The `spectre_meltdown` pipeline uses dataclasses and a separate three-agent rule coordinator. Their thresholds and output schemas are not identical.

CSV batch files must use the schema shown in `sample.csv`; Boolean values can be `true`, `1`, or `yes` (case-insensitive). Invalid rows are skipped by the primary batch CLI with diagnostics. The audit chain exists **only within a running Python process**; invoking `verify-audit` in a new process verifies that process's in-memory chain, not previous invocations.

## Local API

```bash
python -m pip install -e ".[web]"
python cli.py serve --host 127.0.0.1 --port 8000
```

The FastAPI service provides `GET /health`, `POST /api/audit`, `POST /api/chat`, `GET /metrics`, and `GET /api/audit/logs`. The metrics endpoint returns **JSON**, not Prometheus exposition text. API state and the audit trail are in memory and reset on restart.

Audit-log reads are disabled by default. To enable this administrative endpoint, set `AUDIT_LOG_READ_TOKEN` in the server environment and send that value via the `X-Audit-Token` request header. Protect this token, use a private network or authenticated reverse proxy for deployments, and do not expose the audit, chat, or metrics endpoints to an untrusted network without additional controls. The environment variable `AUDIT_SECRET_KEY` sets the HMAC key; otherwise the process generates a nonpersistent random key.

The regex-based identifier guard only recognizes **selected patterns** and must not be considered reliable de-identification or HIPAA-compliant PHI detection. The chat adapter is a deterministic mock and **does not connect** to Ollama, OpenAI, Anthropic, or other providers.

## Containers

```bash
docker build -t spectre-meltdown-transient-agent .
docker run --rm -p 127.0.0.1:8000:8000 spectre-meltdown-transient-agent
# or, using local-only port binding:
docker compose up --build
```

The container runs as a non-root user. Docker Compose binds port 8000 to localhost by default.

## Structure and technology

- `agents/`: Pydantic schemas, CLI/API orchestration, HMAC audit, workers, and mock chat adapter.
- `spectre_meltdown/`: independent dataclass-based evaluator and CLI/API.
- `enrichment.py`: threshold-demo classes labelled with transient-execution concepts; **no hardware probes**.
- `web/`: standalone HTML/CSS/JavaScript browser demo.
- `tests/`: Python tests and Node.js regression tests.
- `.github/workflows/`: test pipeline and static GitHub Pages deployment workflow.

The static page targets current Chromium, Firefox, and Safari versions; browser testing is limited to the included JavaScript checks unless a live deployment is subsequently verified. GitHub Pages requires the repository's Pages source to be configured for GitHub Actions; a deployment workflow alone does not establish a working live URL.

## License

[MIT](LICENSE).
