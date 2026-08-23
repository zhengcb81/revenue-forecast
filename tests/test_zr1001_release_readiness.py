"""ZR-1001 acceptance tests: release readiness — fingerprint / integrity /
capacity / backup / rollback dry-run / authorization (stage I first card).

  C1  fingerprints: three repo HEADs recorded and consistent (real git).
  C2  integrity: production catalog PRAGMA integrity_check == ok (read-only).
  C3  capacity: assurance/runs within the frozen space budget.
  C4  backup + rollback dry-run: backup dir readable; rollback point written
      with current HEADs (nothing executes).
  C5  authorization: no authorization -> release blocked; after issue-auth ->
      ready (release window may open).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import release_readiness as rr  # noqa: E402


# ---------------------------------------------------------------------------
# C1 — fingerprints
# ---------------------------------------------------------------------------


def test_c1_three_repo_heads_recorded():
    fps = rr.head_fingerprints()
    assert set(fps) == {"revenue", "filing", "wiki"}
    for name, sha in fps.items():
        assert len(sha) == 40 and all(c in "0123456789abcdef" for c in sha), (
            f"{name} HEAD not a 40-hex sha: {sha}")


# ---------------------------------------------------------------------------
# C2 — catalog integrity
# ---------------------------------------------------------------------------


def test_c2_catalog_integrity_ok():
    ok, detail = rr.catalog_integrity()
    assert ok, detail


# ---------------------------------------------------------------------------
# C3 — capacity budget
# ---------------------------------------------------------------------------


def test_c3_capacity_within_budget():
    ok, detail = rr.capacity_ok()
    assert ok, detail
    assert "MB" in detail


# ---------------------------------------------------------------------------
# C4 — backup readability + rollback dry-run
# ---------------------------------------------------------------------------


def test_c4_backup_readable():
    ok, detail = rr.backup_readable()
    assert ok, detail


def test_c4_rollback_point_written(tmp_path):
    orig = rr.ROLLBACK_PATH
    rr.ROLLBACK_PATH = tmp_path / "rollback_manifest.json"
    try:
        ok, detail = rr.write_rollback_point()
        assert ok
        data = json.loads(rr.ROLLBACK_PATH.read_text(encoding="utf-8"))
        assert set(data["heads"]) == {"revenue", "filing", "wiki"}
        assert data["recorded_at_utc"]
    finally:
        rr.ROLLBACK_PATH = orig


# ---------------------------------------------------------------------------
# C5 — authorization gate
# ---------------------------------------------------------------------------


def test_c5_without_authorization_release_blocked(tmp_path):
    orig = rr.AUTH_PATH
    rr.AUTH_PATH = tmp_path / "release_authorization.json"
    try:
        ok, detail = rr.authorization()
        assert ok is False
        assert "missing" in detail
    finally:
        rr.AUTH_PATH = orig


def test_c5_issue_authorization_then_ready(tmp_path):
    orig = rr.AUTH_PATH
    rr.AUTH_PATH = tmp_path / "release_authorization.json"
    try:
        rr.issue_authorization("release-owner", "ZR-1001 window")
        ok, detail = rr.authorization()
        assert ok is True
        assert "release-owner" in detail
    finally:
        rr.AUTH_PATH = orig


def test_c5_cli_reports_all_gates():
    proc = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tools" / "release_readiness.py")],
        capture_output=True, text=True, encoding="utf-8", timeout=120,
    )
    out = proc.stdout + proc.stderr
    for gate in ("fingerprints", "integrity", "capacity", "backup",
                 "rollback", "authorization"):
        assert gate in out, f"gate {gate} missing from CLI output"
