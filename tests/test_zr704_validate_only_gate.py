"""ZR-704 acceptance tests: REV-05 validate-only pure read-only gate.

  C1  success path: --validate-only with a valid input leaves the file
      tree empty (no output/markdown/registry files created) and the
      publication_registry hash chain unchanged.
  C2  failure path: --validate-only with an invalid input (missing
      required field) exits 2, leaves the file tree empty and the
      registry hash chain unchanged.
  C3  malformed JSON: --validate-only with non-JSON input exits 2,
      leaves the file tree empty and the registry hash chain unchanged.
  C4  pre-existing registry: --validate-only with an existing
      registry file present does NOT modify it (hash chain byte-identical).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import publication_registry  # noqa: E402
from test_recognition_bridge import forecast_document  # noqa: E402


def _run_validate_only(
    tmp_path: Path, input_file: Path, *, env: dict | None = None
) -> subprocess.CompletedProcess:
    env = env or {}
    env.setdefault("REVENUE_PUBLICATION_REGISTRY", str(tmp_path / "publications.jsonl"))
    return subprocess.run(
        [sys.executable, "scripts/revenue_forecast.py", str(input_file),
         "--validate-only"],
        cwd=str(ROOT), text=True, capture_output=True, env=env, timeout=120,
    )


def _registry_sha(reg_path: Path) -> str | None:
    """Content-addressed hash of the entire registry file (byte-identical
    comparison)."""
    if not reg_path.exists():
        return None
    import hashlib
    return hashlib.sha256(reg_path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# C1 — success path zero-residue (REV-05 success)
# ---------------------------------------------------------------------------


def test_c1_validate_only_success_zero_residue(tmp_path):
    input_file = tmp_path / "valid.json"
    input_file.write_text(json.dumps(forecast_document()), encoding="utf-8")
    reg_path = tmp_path / "publications.jsonl"
    proc = _run_validate_only(tmp_path, input_file)
    assert proc.returncode == 0
    assert proc.stdout.strip() == "valid"
    # no output/markdown files created
    assert [p.name for p in tmp_path.iterdir() if p.suffix in (".json", ".md", ".jsonl")
            and p.name != "valid.json"] == []
    # registry never created
    assert not reg_path.exists()


# ---------------------------------------------------------------------------
# C2 — failure path zero-residue (REV-05 failure)
# ---------------------------------------------------------------------------


def test_c2_validate_only_failure_zero_residue(tmp_path):
    invalid_doc = {"schema_version": "3.7"}  # missing required fields
    input_file = tmp_path / "invalid.json"
    input_file.write_text(json.dumps(invalid_doc), encoding="utf-8")
    reg_path = tmp_path / "publications.jsonl"
    proc = _run_validate_only(tmp_path, input_file)
    assert proc.returncode == 2
    assert "missing required field" in proc.stderr.lower() or proc.stderr
    # zero residue
    assert [p.name for p in tmp_path.iterdir() if p.suffix in (".json", ".jsonl")
            and p.name != "invalid.json"] == []
    assert not reg_path.exists()


# ---------------------------------------------------------------------------
# C3 — malformed JSON zero-residue (REV-05 boundary)
# ---------------------------------------------------------------------------


def test_c3_malformed_json_zero_residue(tmp_path):
    input_file = tmp_path / "bad.json"
    input_file.write_text("{invalid json!!!", encoding="utf-8")
    reg_path = tmp_path / "publications.jsonl"
    proc = _run_validate_only(tmp_path, input_file)
    assert proc.returncode == 2
    assert not reg_path.exists()


# ---------------------------------------------------------------------------
# C4 — pre-existing registry not modified (REV-05 defense)
# ---------------------------------------------------------------------------


def test_c4_preexisting_registry_unchanged(tmp_path, monkeypatch):
    reg_path = tmp_path / "publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(reg_path))
    # seed a real entry (draft mode avoids auto-registration)
    from revenue_forecast import prepare_forecast
    result = prepare_forecast(forecast_document(), mode="draft")
    publication_registry.register_publication(result, note="pre-seed")
    entries_before = publication_registry._read_entries()
    sha_before = _registry_sha(reg_path)
    assert sha_before is not None
    # now validate-only (subprocess with same registry env)
    input_file = tmp_path / "valid.json"
    input_file.write_text(json.dumps(forecast_document()), encoding="utf-8")
    proc = _run_validate_only(tmp_path, input_file, env={
        "REVENUE_PUBLICATION_REGISTRY": str(reg_path),
    })
    assert proc.returncode == 0
    # registry untouched
    assert _registry_sha(reg_path) == sha_before
    entries_after = publication_registry._read_entries()
    assert len(entries_after) == len(entries_before)


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
