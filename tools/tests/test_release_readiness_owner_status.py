"""Release-readiness checks at the public catalog endpoint."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import release_readiness as rr  # noqa: E402


def test_c2_default_does_not_contact_the_catalog_owner(monkeypatch):
    def unexpected(*args):
        pytest.fail("default readiness contacted the catalog owner")

    monkeypatch.setattr(rr, "catalog_integrity", unexpected)
    gate = rr.run_checks()["integrity"]
    assert gate["status"] == "not_supplied"
    assert gate["ok"] is True


def test_c2_explicit_config_invokes_public_status(tmp_path, monkeypatch):
    config = tmp_path / "source catalog.yaml"
    calls = []

    def owner_status(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(
            command, 0, json.dumps({
                "documents": 0, "sources": 3, "active_locations": 2,
                "missing_locations": 1, "future_diagnostic": True,
            }), "",
        )

    monkeypatch.setattr(rr.subprocess, "run", owner_status)
    ok, detail = rr.catalog_integrity(config)
    assert ok is True
    assert "documents=0" in detail and "missing_locations=1" in detail
    assert calls == [[sys.executable, "-B", "-m", "company_wiki.source_catalog.cli",
                      "--config", str(config), "status"]]


@pytest.mark.parametrize("stdout, returncode", [
    ("not JSON", 0), ("[]", 0), ('{"documents": true}', 0), ("{}", 1),
])
def test_c2_invalid_owner_status_is_red(tmp_path, monkeypatch, stdout, returncode):
    def owner_status(command, **kwargs):
        return subprocess.CompletedProcess(command, returncode, stdout, "owner error")

    monkeypatch.setattr(rr.subprocess, "run", owner_status)
    ok, detail = rr.catalog_integrity(tmp_path / "source_catalog.yaml")
    assert ok is False
    assert "CWP" in detail


@pytest.mark.parametrize("stderr, safe_reason", [
    (json.dumps({
        "status": "failed", "error_type": "catalog_busy",
        "error": "database is locked: Bearer fake-SECRET",
        "retryable": True,
    }), "catalog_busy"),
    (json.dumps({
        "status": "failed", "error_type": "fatal",
        "error": "catalog does not exist (not created, not touched): /fake-SECRET",
        "retryable": False,
    }), "catalog_missing"),
    (json.dumps({
        "status": "failed", "error_type": "fatal", "reason": "catalog_missing",
        "error": "供应来源目录不可用：/fake-SECRET", "retryable": False,
    }), "catalog_missing"),
    (json.dumps({
        "status": "failed", "error_type": "fatal", "reason": "unrecognized",
        "error": "catalog does not exist (not created, not touched): /fake-SECRET",
    }), "fatal"),
    ("Traceback (most recent call last):\nFileNotFoundError: /fake-SECRET\n", "FileNotFoundError"),
    (json.dumps({"status": "failed", "error_type": "fake-SECRET"}), "exit 1"),
])
def test_c2_owner_status_failure_keeps_pathless_cause(tmp_path, monkeypatch, stderr, safe_reason):
    def owner_status(command, **kwargs):
        return subprocess.CompletedProcess(command, 1, "", stderr)

    monkeypatch.setattr(rr.subprocess, "run", owner_status)
    ok, detail = rr.catalog_integrity(tmp_path / "source_catalog.yaml")
    assert ok is False
    assert safe_reason in detail
    assert "fake-SECRET" not in detail
