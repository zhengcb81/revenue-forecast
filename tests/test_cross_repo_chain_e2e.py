"""W14-RF-CLEAN-CHAIN: cross-repo chain E2E via the standalone runner.

The heavy lifting lives in ``e2e/run_cross_repo_chain_e2e.py`` and its
behavior contract is pinned by ``tests/test_w14_portable_chain_runner.py``.
This module keeps the suite entry contract: the offline scenario set runs
the REAL three-repo chain from frozen Git objects against the synthetic
fixture lake — with no personal production lake, no credentials, and zero
network — and the opt-in live download stays explicitly gated.

Everything here runs the runner as a subprocess; collection never imports
the chain.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "e2e" / "run_cross_repo_chain_e2e.py"
CWP_REPO = REPO.parent / "company-wiki"
FF_REPO = REPO.parent / "filing-fetch"
RF_COMMIT = "599d17b89d8baee42ce203747496731ace2d0148"
CWP_COMMIT = "a31300a70215319e6bcf3a03d32b2882bdf1aeaa"
FF_COMMIT = "7f6a9268da90281c28b55d437860bc2d2b60106e"


def _commit_present(repo: Path, commit: str) -> bool:
    if not repo.is_dir():
        return False
    return subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-e", f"{commit}^{{commit}}"],
        capture_output=True, check=False).returncode == 0


def _inputs_available() -> tuple[bool, str]:
    for role, repo, commit in (("rf", REPO, RF_COMMIT),
                               ("cwp", CWP_REPO, CWP_COMMIT),
                               ("ff", FF_REPO, FF_COMMIT)):
        if not _commit_present(repo, commit):
            return False, (f"{role} repository/commit unavailable: "
                           f"{repo} @ {commit}")
    return True, ""


_AVAILABLE, _WHY = _inputs_available()


def _run_runner(args: list[str], tmp: Path, timeout: float):
    evidence = tmp / "evidence"
    work = tmp / "work"
    env = dict(os.environ)
    env.pop("RF_E2E_LIVE_DOWNLOAD", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    proc = subprocess.run(
        [sys.executable, "-B", str(RUNNER), *args,
         "--rf-repo", str(REPO), "--rf-commit", RF_COMMIT,
         "--cwp-repo", str(CWP_REPO), "--cwp-commit", CWP_COMMIT,
         "--ff-repo", str(FF_REPO), "--ff-commit", FF_COMMIT,
         "--work-root", str(work), "--evidence-dir", str(evidence)],
        cwd=str(tmp), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout, check=False)
    attempts = sorted(p for p in evidence.iterdir() if p.is_dir()) if \
        evidence.is_dir() else []
    summary = None
    if attempts:
        path = attempts[-1] / "summary.json"
        if path.is_file():
            summary = json.loads(path.read_text(encoding="utf-8"))
    return proc, summary, evidence


def test_usage_errors_do_not_touch_directories(tmp_path):
    """Usage errors (unknown scenario, unknown flag) exit 2 and never
    allocate anything under the caller's roots; a shuffled selection is
    canonicalized to the frozen order instead (historical behavior)."""
    for bad_args in (["--scenarios", "S9"], ["--nope"]):
        proc, summary, evidence = _run_runner(bad_args, tmp_path, timeout=60)
        assert proc.returncode == 2, bad_args
        assert summary is None
        assert not (tmp_path / "work").exists()
        assert not evidence.exists()


def test_offline_chain_scenarios(tmp_path):
    """S2 success + S3 reuse + S5/S6 refusals + S4 restore, offline, from
    frozen three-repo code with zero network."""
    if not _AVAILABLE:
        pytest.skip(f"chain inputs unavailable: {_WHY}")
    proc, summary, evidence = _run_runner(
        ["--live", "never", "--scenarios", "S2,S3,S5,S6,S4"], tmp_path,
        timeout=600)
    assert summary, (f"runner produced no summary (rc={proc.returncode})\n"
                     f"stdout tail: {proc.stdout[-3000:]}\n"
                     f"stderr tail: {proc.stderr[-3000:]}")
    by = {s["id"]: s for s in summary["scenarios"]}
    for sid in ("S2", "S3", "S5", "S6", "S4"):
        assert sid in by, f"{sid} not executed; ran {sorted(by)}"
        assert by[sid]["status"] == "pass", (
            f"scenario {sid} did not pass: "
            f"{json.dumps(by[sid], ensure_ascii=False)}")
    assert summary["live_gate"] == "never"
    assert summary["network_scope"].startswith("none")
    # production writes are MEASURED from this process's git verb log (all
    # verbs must be read-only), not a hardcoded constant (W14 F2/F8)
    pw = summary["production_writes"]
    assert pw["measured"] is True and pw["count"] == 0, pw
    assert set(pw["git_verbs_used"]) <= {"rev-parse", "status", "archive"}, pw
    assert not list(evidence.rglob("net_attempts.json"))
    assert proc.returncode == 0, (
        f"runner exit {proc.returncode}\n{proc.stdout[-3000:]}")


def test_live_download_scenario_is_opt_in(tmp_path):
    """Without --live force the live scenario must not touch the network."""
    if not _AVAILABLE:
        pytest.skip(f"chain inputs unavailable: {_WHY}")
    proc, summary, _ = _run_runner(
        ["--scenarios", "S1,S4"], tmp_path, timeout=300)
    assert summary, f"no summary: rc={proc.returncode}\n{proc.stderr[-2000:]}"
    by = {s["id"]: s for s in summary["scenarios"]}
    assert by["S1"]["status"] == "skip", by["S1"]
    assert by["S1"]["reason"]["code"] == "live_gate_never", by["S1"]
    assert summary["live_gate"] == "never"
    assert summary["network_scope"].startswith("none")
    assert by["S4"]["status"] == "pass", by["S4"]
    assert proc.returncode == 0


def test_offline_failure_is_never_hidden_as_skip(tmp_path):
    """A real failure must fail the whole run (exit 1): fixture bytes
    tampered against their manifest are detected at load and reported as a
    failure — never as a skip or pass."""
    if not _AVAILABLE:
        pytest.skip(f"chain inputs unavailable: {_WHY}")
    fixture_root = tmp_path / "fixtures"
    fixture_root.mkdir()
    for path in (REPO / "tests" / "fixtures" / "w14_chain").iterdir():
        target = fixture_root / path.name
        target.write_bytes(path.read_bytes())
    tampered = fixture_root / "fixture_fy2024q3_quarterly.txt"
    tampered.write_bytes(tampered.read_bytes() + b"tampered\n")
    evidence = tmp_path / "evidence"
    work = tmp_path / "work"
    proc = subprocess.run(
        [sys.executable, "-B", str(RUNNER), "--live", "never",
         "--scenarios", "S2,S4", "--fixture-root", str(fixture_root),
         "--rf-repo", str(REPO), "--rf-commit", RF_COMMIT,
         "--cwp-repo", str(CWP_REPO), "--cwp-commit", CWP_COMMIT,
         "--ff-repo", str(FF_REPO), "--ff-commit", FF_COMMIT,
         "--work-root", str(work), "--evidence-dir", str(evidence)],
        cwd=str(tmp_path), capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=600, check=False)
    assert proc.returncode == 1, (
        f"tampered fixture must fail the run, got {proc.returncode}\n"
        f"{proc.stdout[-2000:]}")
    attempts = sorted(p for p in evidence.iterdir() if p.is_dir())
    summary = json.loads((attempts[-1] / "summary.json")
                         .read_text(encoding="utf-8"))
    assert "fixture_failure" in summary
    assert summary["statuses"] == {}


def test_overlapping_work_and_evidence_dirs_are_usage_error(tmp_path):
    """E06: --work-root inside/equals --evidence-dir could delete receipts
    during scratch cleanup — refused as a usage error before any directory
    is created (W14 A-finding 2 / static F11)."""
    shared = tmp_path / "shared"
    env = dict(os.environ)
    env.pop("RF_E2E_LIVE_DOWNLOAD", None)
    proc = subprocess.run(
        [sys.executable, "-B", str(RUNNER), "--scenarios", "S4",
         "--rf-repo", str(REPO), "--rf-commit", RF_COMMIT,
         "--cwp-repo", str(CWP_REPO), "--cwp-commit", CWP_COMMIT,
         "--ff-repo", str(FF_REPO), "--ff-commit", FF_COMMIT,
         "--work-root", str(shared), "--evidence-dir",
         str(shared / "inside")],
        cwd=str(tmp_path), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=60, check=False)
    assert proc.returncode == 2, proc.stdout[-1000:] + proc.stderr[-1000:]
    assert "disjoint" in proc.stderr
    assert not shared.exists(), "usage error must not allocate anything"


def test_delivery_receipt_fixture_shas_match_manifest():
    """Static integrity of the handoff receipt (W14 F1): the fixture SHAs
    recorded in delivery/w14/replay-receipts.json must equal the fixture
    manifest bytes — a mistyped SHA can never pass again."""
    receipts = REPO / "delivery" / "w14" / "replay-receipts.json"
    if not receipts.is_file():
        pytest.skip("delivery receipt not present (pre-handoff state)")
    data = json.loads(receipts.read_text(encoding="utf-8"))
    manifest = json.loads(
        (REPO / "tests" / "fixtures" / "w14_chain" /
         "w14_fixture_manifest.json").read_text(encoding="utf-8"))
    assert data["fixture_shas"]["pdf"] == \
        manifest["documents"]["annual_pdf"]["sha256"], data["fixture_shas"]
    assert data["fixture_shas"]["txt"] == \
        manifest["documents"]["quarterly_txt"]["sha256"], data["fixture_shas"]
