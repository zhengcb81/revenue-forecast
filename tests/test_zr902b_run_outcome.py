"""ZR-902 daily schedule: the blocked/not-ok outcome split (owner decision 2026-09-13).

The weekly T3 loop got this split first (F-B01-10): ``not-ok`` is a statement about
the PRODUCT, ``blocked`` says the run could not be evaluated here.  The owner decided
the daily T2 loop gets the same treatment, so this file pins the daily behaviour and
the fact that the two vocabularies are identical.

Hermetic: no subprocess, no real catalog, no network.  ``run_outcome`` is a pure
function over (runner result, observation result, report path).
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
import weekly_t3_schedule as w3  # noqa: E402


def _proc(returncode: int, out: str = "", err: str = "") -> SimpleNamespace:
    return SimpleNamespace(returncode=returncode, stdout=out, stderr=err)


def _report(tmp_path: Path, payload: dict | None) -> Path:
    path = tmp_path / "report.json"
    if payload is not None:
        path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_zr902b_a_good_run_is_ok(tmp_path):
    ok, outcome, _detail = d2.run_outcome(
        _proc(0, "done"), _proc(0), _report(tmp_path, {"ok": True, "problems": []}))
    assert ok is True and outcome == "ok"


def test_zr902b_a_verdict_of_bad_health_is_not_ok(tmp_path):
    """A report with ok=false or a non-empty problems list is a statement about the
    product - never 'blocked'."""
    ok, outcome, detail = d2.run_outcome(
        _proc(1), _proc(0),
        _report(tmp_path, {"ok": False, "problems": ["triplet drift: wiki head differs"]}))
    assert ok is False and outcome == "not-ok" and "triplet drift" in detail


def test_zr902b_no_report_with_environment_evidence_is_blocked(tmp_path):
    """Nothing was evaluated and the output names a missing catalog: the record must
    say 'could not run here', not 'the product is broken'."""
    proc = _proc(2, "", "FileNotFoundError: [WinError 2] 系统找不到指定的文件。\n")
    ok, outcome, detail = d2.run_outcome(proc, _proc(0), _report(tmp_path, None))
    assert ok is False and outcome == "blocked", (outcome, detail)
    assert "heuristic" in detail, detail


def test_zr902b_no_report_and_no_marker_stays_not_ok(tmp_path):
    """The conservative direction: an unexplained crash is a code failure, not an
    environment one."""
    ok, outcome, _detail = d2.run_outcome(
        _proc(3, "", "Traceback ...\nAssertionError: invariant broken\n"),
        _proc(0), _report(tmp_path, None))
    assert ok is False and outcome == "not-ok"


def test_zr902b_the_sentinel_is_authoritative(tmp_path):
    ok, outcome, detail = d2.run_outcome(
        _proc(1, f"{d2.ENVIRONMENT_SENTINEL}: catalog not mounted\n"),
        _proc(0), _report(tmp_path, None))
    assert ok is False and outcome == "blocked" and "sentinel" in detail


def test_zr902b_an_observer_failure_is_never_blamed_on_the_environment(tmp_path):
    """The observer is part of the mechanism under test: if it fails while the runner
    passed, the FC-705 window did not advance - that is not-ok, even if the observer's
    complaint happens to mention a path."""
    ok, outcome, detail = d2.run_outcome(
        _proc(0, "done"), _proc(1, "", "FileNotFoundError: legacy_periods.json not found"),
        _report(tmp_path, {"ok": True, "problems": []}))
    assert ok is False and outcome == "not-ok", (outcome, detail)
    assert "FC-705" in detail


def test_zr902b_an_empty_problems_list_with_ok_true_is_a_pass(tmp_path):
    ok, outcome, _detail = d2.run_outcome(
        _proc(0, "done"), _proc(0), _report(tmp_path, {"ok": True, "problems": []}))
    assert ok is True and outcome == "ok"


def test_zr902b_the_daily_and_weekly_vocabularies_are_identical():
    """They are mirrored on purpose (weekly imports daily, so a shared constant would
    invert the dependency).  Mirrored means 'must not drift': this case fails the
    moment one list is edited without the other."""
    assert set(d2.ENVIRONMENT_MARKERS) == set(w3.ENVIRONMENT_MARKERS)
    assert d2.ENVIRONMENT_SENTINEL != w3.ENVIRONMENT_SENTINEL  # different loops, different tokens
    assert d2.ENVIRONMENT_SENTINEL.endswith("COULD-NOT-RUN")
    assert w3.ENVIRONMENT_SENTINEL.endswith("COULD-NOT-RUN")


def test_zr902b_a_real_run_still_executes_the_same_gate_path(tmp_path, monkeypatch):
    """The split must not change the gate: run_daily still returns the non-zero exit
    and still writes a ledger with ok=False when the runner fails."""
    ledger = tmp_path / "daily_manifest.json"
    alerts = tmp_path / "daily_alert.jsonl"
    report_root = tmp_path / "runs"

    monkeypatch.setattr(d2, "window_wait_seconds", lambda *_a, **_k: 0)
    monkeypatch.setattr(d2, "next_period_number", lambda *_a, **_k: 7)
    monkeypatch.setattr(d2, "_head", lambda *_a, **_k: "0" * 40)

    def fake_run(cmd, **kwargs):
        if "daily_t2_runner.py" in " ".join(str(part) for part in cmd):
            (report_root / d2.datetime.now(d2.UTC).strftime("%Y%m%dT%H%M%SZ")).mkdir(
                parents=True, exist_ok=True)
            return subprocess.CompletedProcess(cmd, 2, "", "no such file: catalog.sqlite3")
        return subprocess.CompletedProcess(cmd, 0, "", "")

    monkeypatch.setattr(d2.subprocess, "run", fake_run)
    rc = d2.run_daily(tmp_path / "c.sqlite3", tmp_path / "m.json", report_root,
                      ledger, alerts, periods_path=tmp_path / "periods.json")
    assert rc == 2
    data = d2.read_ledger(ledger)
    assert data["ok"] is False
    entry = json.loads(alerts.read_text(encoding="utf-8").strip().splitlines()[0])
    assert entry["outcome"] == "blocked" and entry["exit_code"] == 2
