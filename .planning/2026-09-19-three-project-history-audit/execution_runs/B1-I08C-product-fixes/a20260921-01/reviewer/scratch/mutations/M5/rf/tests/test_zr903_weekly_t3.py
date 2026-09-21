"""ZR-903 acceptance tests: weekly / pre-release T3 scheduling.

  C1  weekly ledger mechanism — ``run-weekly`` invokes the T3 suite (opt-in)
      and writes ``weekly_manifest.json`` (run_id/started_at/triplet/ok).
  C2  freshness <=7d — fresh (<=7d & ok) / stale (>7d or not-ok) / missing
      (old green never fresh, AUD2-02).
  C3  blocked alerts + release blocking — stale/missing/not-ok append to the
      weekly alert journal and block the release gate; an ALL-SKIPPED T3
      suite (missing credentials/network) records BLOCKED, never a pass
      (CA-203 RED reversal).
  C4  release gate + verify — fresh+ok -> ready; subcommands positional.

Hermetic: fake T3 runner stub via monkeypatched ``_run_t3_suite``; the real
suite, real Task Scheduler and real downloads are never touched.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import weekly_t3_schedule as w3  # noqa: E402

NOW = datetime.now(UTC)
WEEK_MAX_HOURS = 7 * 24


def _ledger(ok: bool = True, started_at: str | None = None) -> dict:
    return {
        "latest_run_id": "weekly-test",
        "started_at": started_at or NOW.isoformat(),
        "triplet": {"revenue": "a" * 40, "filing": "b" * 40, "wiki": "c" * 40},
        "ok": ok,
        "report_path": "weekly-run-test",
    }


def _old_iso(days: int) -> str:
    return (NOW - timedelta(days=days)).isoformat()


def _fake_proc(returncode: int, out: str) -> SimpleNamespace:
    return SimpleNamespace(returncode=returncode, stdout=out, stderr="")


# ---------------------------------------------------------------------------
# C1 — weekly ledger mechanism
# ---------------------------------------------------------------------------


def test_c1_run_weekly_writes_ledger(tmp_path, monkeypatch):
    ledger = tmp_path / "weekly_manifest.json"
    alerts = tmp_path / "weekly_alert.jsonl"

    def fake_suite(timeout=3600):
        return _fake_proc(0, "3 passed in 5.00s")

    monkeypatch.setattr(w3, "_run_t3_suite", fake_suite)
    rc = w3.run_weekly(ledger, alerts)
    assert rc == 0
    data = w3.read_ledger(ledger)
    assert data["ok"] is True
    assert data["latest_run_id"].startswith("20")
    assert not alerts.exists()


def test_c1_not_ok_still_recorded(tmp_path, monkeypatch):
    ledger = tmp_path / "weekly_manifest.json"
    alerts = tmp_path / "weekly_alert.jsonl"

    def fake_suite(timeout=3600):
        return _fake_proc(1, "1 failed, 2 passed")

    monkeypatch.setattr(w3, "_run_t3_suite", fake_suite)
    rc = w3.run_weekly(ledger, alerts)
    assert rc != 0
    assert w3.read_ledger(ledger)["ok"] is False
    lines = alerts.read_text(encoding="utf-8").strip().splitlines()
    assert json.loads(lines[0])["status"] == "not-ok"


def test_c1_suite_output_is_persisted_and_the_ledger_names_a_real_file(
        tmp_path, monkeypatch):
    """F-B01-10: a failed weekly run must stay diagnosable.  The ledger used to
    record `report_path="weekly-run-<id>"` with no file behind it, so the recorded
    `exit 1` could not be explained from the record — the suite's output has to be
    persisted, and the ledger has to point at it.  The recorded value is a bare file
    name (resolved against the ledger's directory), because the ledger is tracked
    and an absolute path would commit this machine's profile into the repo."""
    ledger = tmp_path / "weekly_manifest.json"
    alerts = tmp_path / "weekly_alert.jsonl"

    def fake_suite(timeout=3600):
        return _fake_proc(
            1, "FAILED tests/test_e2e_download.py::test_download - RuntimeError: no tool"
        )

    monkeypatch.setattr(w3, "_run_t3_suite", fake_suite)
    assert w3.run_weekly(ledger, alerts) != 0

    data = w3.read_ledger(ledger)
    recorded = data["report_path"]
    assert recorded == f"weekly-run-{data['latest_run_id']}.log", recorded
    assert not Path(recorded).is_absolute(), "a tracked ledger must stay portable"
    report = ledger.parent / recorded
    assert report.is_file(), "report_path must name a real file beside the ledger"
    text = report.read_text(encoding="utf-8")
    assert "RuntimeError: no tool" in text, "the failure reason must be recoverable"
    assert "status=not-ok" in text and data["latest_run_id"] in text


def test_c1_report_write_failure_never_breaks_the_assurance_run(tmp_path, monkeypatch):
    """A diagnostic side file is best-effort: if it cannot be written, the ledger
    and the alert must still be recorded (the release gate must not depend on the
    log file's fate).  Only ``.log`` writes fail here, so the ledger write is real.
    The ledger must SAY the report is missing instead of naming a file that does not
    exist (B-VR903-06's sibling)."""
    ledger = tmp_path / "weekly_manifest.json"
    alerts = tmp_path / "weekly_alert.jsonl"
    real_write_text = Path.write_text

    def fake_suite(timeout=3600):
        return _fake_proc(3, "3 errors")

    def selective(self, *args, **kwargs):
        if self.suffix == ".log":
            raise OSError("disk full")
        return real_write_text(self, *args, **kwargs)

    monkeypatch.setattr(w3, "_run_t3_suite", fake_suite)
    monkeypatch.setattr(Path, "write_text", selective)

    assert w3.run_weekly(ledger, alerts) == 3, "the suite's exit code must survive"

    data = w3.read_ledger(ledger)
    assert data["ok"] is False and data["latest_run_id"]
    assert data["report_path"] == (
        f"weekly-run-{data['latest_run_id']}.log (NOT WRITTEN: OSError)"
    ), data["report_path"]
    entry = json.loads(alerts.read_text(encoding="utf-8").strip().splitlines()[0])
    assert entry["status"] == "not-ok" and entry["exit_code"] == 3


# ---------------------------------------------------------------------------
# C5 — the classification's own edges, the sentinel, crashes and run identity
# (B.VR903-01/-02/-03/-04/-05/-06)
# ---------------------------------------------------------------------------


def test_c5_exit_zero_without_a_verdict_is_blocked():
    """Rule 1 of the classifier had ZERO coverage: the first review's surviving
    mutant deleted it and all cases still passed (B-VR903-03)."""
    ok, status, detail = w3._suite_outcome(_fake_proc(0, "collected 0 items\n"))
    assert ok is False and status == "blocked", (status, detail)


def test_c5_the_sentinel_beats_every_heuristic():
    """The authoritative signal: the suite says it could not run here."""
    proc = _fake_proc(1, f"ERROR ... {w3.ENVIRONMENT_SENTINEL}: no download credential\n")
    ok, status, detail = w3._suite_outcome(proc)
    assert ok is False and status == "blocked" and "sentinel" in detail


def test_c5_a_localized_missing_tool_is_blocked_not_not_ok():
    """B-VR903-02: on a non-English host `FileNotFoundError: [WinError 2] 系统找不到
    指定的文件。` carries no English marker at all, so the first list read it as a code
    failure.  Exception CLASS names and numeric OS codes survive localization."""
    proc = _fake_proc(2, "ERROR tests/test_e2e_download.py - FileNotFoundError: "
                         "[WinError 2] \u7cfb\u7edf\u627e\u4e0d\u5230\u6307\u5b9a\u7684"
                         "\u6587\u4ef6\u3002\n\n1 error in 0.20s\n")
    ok, status, detail = w3._suite_outcome(proc)
    assert ok is False and status == "blocked", (status, detail)


def test_c5_a_bare_localized_os_error_code_is_enough():
    """The numeric code is the language-neutral half: no exception class name and no
    English word, only ``[WinError 2]``."""
    proc = _fake_proc(2, "OSError: [WinError 2] \u7cfb\u7edf\u627e\u4e0d\u5230\u6307"
                         "\u5b9a\u7684\u6587\u4ef6\u3002\n\n1 error in 0.20s\n")
    ok, status, _detail = w3._suite_outcome(proc)
    assert ok is False and status == "blocked"


def test_c5_a_crash_is_recorded_as_a_run(tmp_path, monkeypatch):
    """B-VR903-06: a timeout used to leave no ledger, no alert and no report, so the
    previous green run kept satisfying the gate for up to seven days."""
    ledger = tmp_path / "weekly_manifest.json"
    alerts = tmp_path / "weekly_alert.jsonl"

    def exploding_suite(timeout=3600):
        raise subprocess.TimeoutExpired(cmd="pytest", timeout=timeout)

    monkeypatch.setattr(w3, "_run_t3_suite", exploding_suite)
    assert w3.run_weekly(ledger, alerts) == 124

    data = w3.read_ledger(ledger)
    assert data["ok"] is False
    report = ledger.parent / data["report_path"]
    assert report.is_file(), "a crashed run must still leave a report"
    assert "TimeoutExpired" in report.read_text(encoding="utf-8")
    entry = json.loads(alerts.read_text(encoding="utf-8").strip().splitlines()[0])
    assert entry["status"] == "not-ok" and entry["exit_code"] == 124


def test_c5_a_blocked_run_exits_non_zero_even_when_pytest_exited_zero(
        tmp_path, monkeypatch):
    """The all-skipped case: pytest exits 0, but the gate is blocked - the scheduler
    must not record a success (B-VR903: run_weekly used to return 0)."""
    ledger = tmp_path / "weekly_manifest.json"
    alerts = tmp_path / "weekly_alert.jsonl"

    def fake_suite(timeout=3600):
        return _fake_proc(0, "5 skipped in 0.10s")

    monkeypatch.setattr(w3, "_run_t3_suite", fake_suite)
    assert w3.run_weekly(ledger, alerts) != 0
    assert w3.read_ledger(ledger)["ok"] is False


def test_c5_a_second_run_in_the_same_second_gets_a_distinct_id(tmp_path):
    """B-VR903-06: a second-resolution id used to overwrite the earlier report and
    make the ledger and the alert journal disagree about that id.

    Written without freezing the clock on purpose: the property asserted is "never
    equal to the ledger's current id", which holds whether or not the second ticks.
    """
    ledger = tmp_path / "weekly_manifest.json"
    stale = "20260913T000000Z"
    ledger.write_text(json.dumps({"latest_run_id": stale}), encoding="utf-8")
    fresh = w3._unique_run_id(ledger)
    assert fresh != stale and len(fresh) >= len(stale)

    ledger.write_text(json.dumps({"latest_run_id": fresh}), encoding="utf-8")
    assert w3._unique_run_id(ledger) != fresh, "the id collided with the ledger's"


def test_c5_the_persisted_report_does_not_leak_the_machine_profile(tmp_path, monkeypatch):
    """B-VR903-05: the report is a TRACKED file, and under the scheduled task
    argv[0] is an absolute path containing the user profile.

    HOST-NEUTRAL on purpose: the first version hard-coded a ``C:\\Users\\someone\\...``
    string, and on POSIX ``Path(...).name`` keeps the whole string (backslash is not a
    separator), so the test failed on CI - the exact host-assumption class this change
    set is about.  ``tmp_path`` carries native separators and, on Windows, the real
    user profile, so asserting that it does not appear is a real check on both hosts.
    """
    ledger = tmp_path / "weekly_manifest.json"
    alerts = tmp_path / "weekly_alert.jsonl"
    script = tmp_path / "tools" / "weekly_t3_schedule.py"
    script.parent.mkdir(parents=True, exist_ok=True)
    script.write_text("# stand-in for the real CLI\n", encoding="utf-8")

    def fake_suite(timeout=3600):
        return _fake_proc(0, "4 passed in 80.00s")

    monkeypatch.setattr(w3, "_run_t3_suite", fake_suite)
    monkeypatch.setattr(w3.sys, "argv", [str(script), "run-weekly"])
    assert w3.run_weekly(ledger, alerts) == 0
    report = ledger.parent / w3.read_ledger(ledger)["report_path"]
    text = report.read_text(encoding="utf-8")
    assert "weekly_t3_schedule.py" in text, "the script name is still recorded"
    assert str(tmp_path) not in text, "an absolute host path leaked into a tracked report"
    assert "run-weekly" in text, "the arguments are still recorded"


# ---------------------------------------------------------------------------
# C2 — freshness <=7d (AUD2-02)
# ---------------------------------------------------------------------------


def test_c2_fresh_within_week():
    status, detail = w3.freshness_status(_ledger(ok=True), now=NOW.isoformat(),
                                         max_age_hours=WEEK_MAX_HOURS)
    assert status == "fresh", detail


def test_c2_stale_after_week():
    status, detail = w3.freshness_status(
        _ledger(ok=True, started_at=_old_iso(8)),
        now=NOW.isoformat(), max_age_hours=WEEK_MAX_HOURS)
    assert status == "stale", detail


def test_c2_stale_when_not_ok():
    status, _d = w3.freshness_status(_ledger(ok=False), now=NOW.isoformat(),
                                     max_age_hours=WEEK_MAX_HOURS)
    assert status == "stale"


def test_c2_missing():
    status, _d = w3.freshness_status(None, now=NOW.isoformat(),
                                     max_age_hours=WEEK_MAX_HOURS)
    assert status == "missing"


# ---------------------------------------------------------------------------
# C3 — blocked alerts + release blocking (CA-203 RED reversal)
# ---------------------------------------------------------------------------


def test_c3_all_skipped_suite_is_blocked_never_pass(tmp_path, monkeypatch):
    """Missing credentials/network -> fully skipped suite -> BLOCKED alert,
    release gate stays red (CA-203: never recorded as a pass)."""
    ledger = tmp_path / "weekly_manifest.json"
    alerts = tmp_path / "weekly_alert.jsonl"

    def fake_suite(timeout=3600):
        return _fake_proc(0, "5 skipped in 0.10s")

    monkeypatch.setattr(w3, "_run_t3_suite", fake_suite)
    ok, status, detail = w3._suite_outcome(_fake_proc(0, "5 skipped in 0.10s"))
    assert status == "blocked"
    assert ok is False
    w3.run_weekly(ledger, alerts)
    lines = alerts.read_text(encoding="utf-8").strip().splitlines()
    entry = json.loads(lines[0])
    assert entry["status"] == "blocked"
    assert "skipped" in entry["reason"]
    ready, _g = w3.release_gate(ledger, now=NOW.isoformat(),
                                max_age_hours=WEEK_MAX_HOURS)
    assert ready is False


def test_c3_missing_environment_is_blocked_not_a_code_failure():
    """F-B01-10 follow-up: a collection error caused by the environment (no tool,
    no credentials, no network) is BLOCKED - the suite never evaluated the product -
    while still blocking the release gate."""
    proc = _fake_proc(
        4,
        "ERROR tests/test_e2e_download.py - RuntimeError: download tool not found\n"
        "\n1 error in 0.42s\n",
    )
    ok, status, detail = w3._suite_outcome(proc)
    assert ok is False and status == "blocked", (status, detail)
    assert "environment" in detail and "no test reached a verdict" in detail


def test_c3_no_tests_collected_is_blocked():
    ok, status, _detail = w3._suite_outcome(_fake_proc(5, "no tests ran in 0.01s\n"))
    assert ok is False and status == "blocked"


def test_c3_an_ambiguous_collection_error_stays_not_ok():
    """An import error is ambiguous (missing dependency vs. broken code), so it must
    keep reading as a code failure - the conservative direction: never launder a
    real defect into "the environment did it"."""
    ok, status, _detail = w3._suite_outcome(_fake_proc(
        2, "ERROR tests/test_e2e_download.py - ImportError: cannot import name 'x'\n"
           "\n1 error in 0.20s\n"))
    assert ok is False and status == "not-ok"


def test_c3_a_failing_test_is_never_laundered_into_blocked():
    """A suite that RAN and failed is not-ok even when the failure text happens to
    mention the network - the verdict, not the wording, decides."""
    ok, status, _detail = w3._suite_outcome(_fake_proc(
        1, "1 failed, 3 passed in 80.11s\n"
           "FAILED tests/test_e2e_download.py::test_download - ConnectionResetError"))
    assert ok is False and status == "not-ok"


def test_c3_release_blocked_on_stale_and_missing(tmp_path):
    stale = tmp_path / "stale.json"
    w3.write_ledger(stale, "r", _old_iso(9), {}, True, "x")
    ready, _r = w3.release_gate(stale, now=NOW.isoformat(),
                                max_age_hours=WEEK_MAX_HOURS)
    assert ready is False
    ready2, _r2 = w3.release_gate(tmp_path / "absent.json", now=NOW.isoformat(),
                                  max_age_hours=WEEK_MAX_HOURS)
    assert ready2 is False


# ---------------------------------------------------------------------------
# C4 — release gate ready + positional subcommands
# ---------------------------------------------------------------------------


def test_c4_release_ready_on_fresh_ok(tmp_path):
    ledger = tmp_path / "weekly_manifest.json"
    w3.write_ledger(ledger, "r", NOW.isoformat(), {}, True, "x")
    ready, reason = w3.release_gate(ledger, now=NOW.isoformat(),
                                    max_age_hours=WEEK_MAX_HOURS)
    assert ready is True
    assert "ready" in reason


def test_c4_subcommands_positional():
    proc = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tools" / "weekly_t3_schedule.py"),
         "--help"],
        capture_output=True, text=True, encoding="utf-8", timeout=60,
    )
    for name in ("run-weekly", "register", "unregister", "query", "verify"):
        assert name in proc.stdout, f"missing subcommand {name}"
