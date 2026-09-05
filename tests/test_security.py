"""
Security-focused tests for Spectre Meltdown Transient Agent.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import AuditTrail, PHIGuard, SecurityException, AuditLogger
from agents.models import SystemTaskPayload


class TestAuditSignatureVerification:
    """Verify that HMAC signatures are correctly validated."""

    def test_audit_trail_signatures_are_valid(self):
        trail = AuditTrail(secret_key="test-secret-key")
        entry = trail.log("test_actor", "test_tier", "TEST_EVENT", {"data": "value"})
        assert entry["current_hash"] != ""
        assert trail.verify_integrity() is True

    def test_audit_trail_detects_tampered_signature(self):
        trail = AuditTrail(secret_key="test-secret-key")
        trail.log("actor", "tier", "EVENT", {"data": "original"})
        # Tamper with the stored signature
        trail.logs[0]["current_hash"] = "TAMPERED_SIGNATURE_12345"
        assert trail.verify_integrity() is False

    def test_audit_trail_detects_tampered_chain(self):
        trail = AuditTrail(secret_key="test-secret-key")
        trail.log("actor1", "tier", "EVENT1", {"data": "first"})
        trail.log("actor2", "tier", "EVENT2", {"data": "second"})
        # Break the chain by modifying prev_hash of second entry
        trail.logs[1]["prev_hash"] = "BROKEN_CHAIN_HASH"
        assert trail.verify_integrity() is False

    def test_audit_trail_detects_tampered_timestamp(self):
        trail = AuditTrail(secret_key="test-secret-key")
        trail.log("actor", "tier", "EVENT", {"data": "value"})
        # Tamper with timestamp after signing
        trail.logs[0]["timestamp"] = "2099-01-01T00:00:00+00:00"
        assert trail.verify_integrity() is False

    def test_audit_trail_empty_is_valid(self):
        trail = AuditTrail(secret_key="test-secret-key")
        assert trail.verify_integrity() is True

    def test_audit_trail_no_hardcoded_default_key(self):
        """Ensure the default key is randomly generated, not a static secret."""
        trail = AuditTrail()
        assert trail.secret_key != b"spectre-meltdown-transient-agent-master-audit-key-2026"
        # Key should be 64 hex characters (32 bytes of randomness encoded as hex)
        assert len(trail.secret_key) == 64

    def test_audit_trail_uses_env_var_when_set(self, monkeypatch):
        monkeypatch.setenv("AUDIT_SECRET_KEY", "my-custom-secret")
        trail = AuditTrail()
        assert trail.secret_key == b"my-custom-secret"


class TestInputValidation:
    """Verify input validation on SystemTaskPayload."""

    def test_control_characters_stripped(self):
        payload = SystemTaskPayload(
            task_id="TASK-001\x00\x01",
            target_identifier="KEY-01",
            primary_metric=10.0,
        )
        assert "\x00" not in payload.task_id
        assert "\x01" not in payload.task_id

    def test_whitespace_stripped(self):
        payload = SystemTaskPayload(
            task_id="  TASK-001  ",
            target_identifier="  KEY-01  ",
            primary_metric=10.0,
        )
        assert payload.task_id == "TASK-001"
        assert payload.target_identifier == "KEY-01"

    def test_max_length_enforced(self):
        with pytest.raises(Exception):
            SystemTaskPayload(
                task_id="X" * 200,
                target_identifier="KEY-01",
                primary_metric=10.0,
            )

    def test_status_descriptor_max_length(self):
        with pytest.raises(Exception):
            SystemTaskPayload(
                task_id="TASK-001",
                target_identifier="KEY-01",
                primary_metric=10.0,
                status_descriptor="X" * 100,
            )


class TestPHIGuardRedaction:
    """Test the PHI redaction utility."""

    def test_redact_phi_replaces_ssn(self):
        text = "Patient SSN 123-45-6789 noted"
        redacted = PHIGuard.redact_phi(text)
        assert "123-45-6789" not in redacted
        assert "REDACTED_IDENTIFIER" in redacted

    def test_redact_phi_replaces_email(self):
        text = "Contact user@example.com for follow-up"
        redacted = PHIGuard.redact_phi(text)
        assert "user@example.com" not in redacted

    def test_clean_text_unchanged(self):
        text = "Analytical specimen KEY-001 within normal bounds"
        assert PHIGuard.redact_phi(text) == text


class TestBatchCLI:
    """Test batch command error handling."""

    def test_batch_missing_file_returns_error(self, capsys):
        from cli import main
        result = main(["batch", "-i", "/nonexistent/path/file.csv"])
        assert result == 1
