"""ZR-902 daily schedule: the blocked/not-ok outcome split (owner decision 2026-09-13).

The weekly T3 loop got this split first (F-B01-10): ``not-ok`` is a statement about
the PRODUCT, ``blocked`` says the run could not be evaluated here.  The owner decided
the daily T2 loop gets the same treatment, so this file pins the daily behaviour.

Hermetic: no subprocess, no real catalog, no network.  ``run_outcome`` is a pure
function over (runner result, persisted report).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import daily_t2_schedule as d2  # noqa: E402


def _proc(returncode: int, out: str = "", err: str = "") -> SimpleNamespace:
    return SimpleNamespace(returncode=returncode, stdout=out, stderr=err)


def test_zr902b_a_good_run_is_ok():
    ok, outcome, _detail = d2.run_outcome(
        _proc(0, "done"), {"ok": True, "problems": []})
    assert ok is True and outcome == "ok"


def test_zr902b_a_verdict_of_bad_health_is_not_ok():
    """A report with ok=false or a non-empty problems list is a statement about the
    product - never 'blocked'."""
    ok, outcome, detail = d2.run_outcome(
        _proc(1),
        {"ok": False, "problems": ["triplet drift: wiki head differs"]})
    assert ok is False and outcome == "not-ok" and "triplet drift" in detail


def test_zr902b_no_report_with_environment_evidence_is_blocked():
    """Nothing was evaluated and the output names a missing catalog: the record must
    say 'could not run here', not 'the product is broken'."""
    proc = _proc(2, "", "FileNotFoundError: [WinError 2] 系统找不到指定的文件。\n")
    ok, outcome, detail = d2.run_outcome(proc, None)
    assert ok is False and outcome == "blocked", (outcome, detail)
    assert "heuristic" in detail, detail


def test_zr902b_no_report_and_no_marker_stays_not_ok():
    """The conservative direction: an unexplained crash is a code failure, not an
    environment one."""
    ok, outcome, _detail = d2.run_outcome(
        _proc(3, "", "Traceback ...\nAssertionError: invariant broken\n"),
        None)
    assert ok is False and outcome == "not-ok"


def test_zr902b_the_sentinel_is_authoritative():
    ok, outcome, detail = d2.run_outcome(
        _proc(1, f"{d2.ENVIRONMENT_SENTINEL}: catalog not mounted\n"),
        None)
    assert ok is False and outcome == "blocked" and "sentinel" in detail


def test_zr902b_owner_unavailable_receipt_remains_blocked():
    ok, outcome, detail = d2.run_outcome(
        _proc(2),
        {"ok": False, "outcome": "blocked",
                           "problems": ["owner_command_timeout"]},
    )
    assert ok is False and outcome == "blocked" and detail == "owner_command_timeout"


def test_zr902b_an_empty_problems_list_with_ok_true_is_a_pass():
    ok, outcome, _detail = d2.run_outcome(
        _proc(0, "done"), {"ok": True, "problems": []})
    assert ok is True and outcome == "ok"


def test_zr902b_a_real_run_still_executes_the_same_gate_path(tmp_path, monkeypatch):
    """The split must not change the gate: run_daily still returns the non-zero exit
    and still writes a ledger with ok=False when the runner fails."""
    ledger = tmp_path / "daily_manifest.json"
    alerts = tmp_path / "daily_alert.jsonl"
    report_root = tmp_path / "runs"

    def fake_run(cmd, **kwargs):
        assert Path(cmd[2]).name == "daily_t2_runner.py"
        return subprocess.CompletedProcess(cmd, 2, "", "no such file: owner_config")

    monkeypatch.setattr(d2.subprocess, "run", fake_run)
    rc = d2.run_daily(tmp_path / "source_catalog.yaml", report_root, ledger, alerts)
    assert rc == 2
    data = d2.read_ledger(ledger)
    assert data["ok"] is False
    report = json.loads(Path(data["report_path"]).read_bytes())
    assert report["outcome"] == "blocked" and report["run_id"] == data["latest_run_id"]
    entry = json.loads(alerts.read_text(encoding="utf-8").strip().splitlines()[0])
    assert entry["outcome"] == "blocked" and entry["exit_code"] == 2
