"""
FastAPI REST API Server for Spectre Meltdown Transient Agent.
"""
import os
import secrets
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from .base import AuditLogger, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Spectre Meltdown Transient Agent API",
    description="Demonstration metric-rule evaluator. No clinical validation or CPU vulnerability detection.",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "spectre-meltdown-transient-agent", "domain": "Clinical & Biomedical AI", "standard": "Illustrative rules (not validated standards)", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException:
        raise HTTPException(status_code=400, detail="Input contains a prohibited identifier")


@app.get("/api/audit/logs")
def api_audit_logs(x_audit_token: Optional[str] = Header(default=None)):
    configured = os.getenv("AUDIT_LOG_READ_TOKEN")
    if not configured:
        raise HTTPException(status_code=503, detail="Audit log access is disabled")
    if x_audit_token is None or not secrets.compare_digest(x_audit_token.encode("utf-8"), configured.encode("utf-8")):
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
