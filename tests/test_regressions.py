"""Regression tests for input handling, API access, and audit isolation."""
import csv

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from agents.api import app
from agents.base import AuditTrail
from agents.models import SystemTaskPayload
from spectre_meltdown.cli import main as frontier_main


@pytest.mark.parametrize("metric", [float("inf"), float("-inf"), float("nan")])
def test_nonfinite_metrics_rejected(metric):
    for field in ("primary_metric", "secondary_metric"):
        fields = {"task_id": "T", "target_identifier": "K", "primary_metric": 2.0}
        fields[field] = metric
        with pytest.raises(ValidationError):
            SystemTaskPayload(**fields)


def test_blank_identifiers_rejected_after_sanitizing():
    for field in ("task_id", "target_identifier", "status_descriptor"):
        fields = {"task_id": "T", "target_identifier": "K", "primary_metric": 2.0}
        fields[field] = " \x00\t "
        with pytest.raises(ValidationError):
            SystemTaskPayload(**fields)


def test_audit_trail_returns_isolated_entries():
    trail = AuditTrail(secret_key="test-only")
    entry = trail.log("actor", "tier", "event", {"result": "OK"})
    entry["current_hash"] = "CHANGED"
    other = trail.get_trail()
    other[0]["current_hash"] = "CHANGED"
    assert trail.verify_integrity()


def test_audit_log_api_requires_configured_token(monkeypatch):
    client = TestClient(app)
    monkeypatch.delenv("AUDIT_LOG_READ_TOKEN", raising=False)
    assert client.get("/api/audit/logs").status_code == 503
    monkeypatch.setenv("AUDIT_LOG_READ_TOKEN", "test-log-token")
    assert client.get("/api/audit/logs").status_code == 403
    assert client.get("/api/audit/logs", headers={"X-Audit-Token": "wrong"}).status_code == 403
    response = client.get("/api/audit/logs", headers={"X-Audit-Token": "test-log-token"})
    assert response.status_code == 200
    assert response.json()["verified"] is True


def test_chat_phi_rejected_without_revealing_input():
    response = TestClient(app).post("/api/chat", json={"query": "MRN-123456789"})
    assert response.status_code == 400
    assert "123456789" not in response.text


def test_frontier_batch_false_string_does_not_trigger_critical(tmp_path):
    src = tmp_path / "in.csv"
    dest = tmp_path / "out.csv"
    src.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,status_descriptor,is_critical_flag\n"
        "T-1,KEY-1,10,2,NOMINAL,False\n", encoding="utf-8"
    )
    assert frontier_main(["batch", "-i", str(src), "-o", str(dest)]) == 0
    with dest.open(newline="", encoding="utf-8") as file:
        row = next(csv.DictReader(file))
    assert row["overall_status"] == "NOMINAL_OPTIMAL"


def test_audit_api_rejects_phi_with_client_error():
    response = TestClient(app).post("/api/audit", json={
        "task_id": "MRN-123456789",
        "target_identifier": "KEY-1",
        "primary_metric": 10,
    })
    assert response.status_code == 400
    assert "123456789" not in response.text


def test_unimplemented_external_llm_providers_are_rejected():
    from agents.llm_factory import LLMFactory
    for provider in ("openai", "ollama", "claude", "unknown"):
        with pytest.raises(ValueError, match="Unsupported"):
            LLMFactory.create(provider)


def test_concurrent_audit_records_keep_valid_chain():
    from concurrent.futures import ThreadPoolExecutor

    trail = AuditTrail(secret_key="test-only")
    def record(i):
        trail.log("test", "worker", "CONCURRENT", {"index": i})

    with ThreadPoolExecutor(max_workers=12) as executor:
        list(executor.map(record, range(200)))
    assert len(trail.get_trail()) == 200
    assert trail.verify_integrity()
