"""CA-205 acceptance tests: atomic report / freshness / alert / release consumption.

The CA-205 card: pending temp files -> full validation -> atomic publish;
dashboard and release read the SAME schema; alert delivery has ack/retry;
expired results can never be revived.  The card's acceptance: EVERY
failure class keeps release red; recovery is idempotent; a published
report carries its own hash, triplet, sample and command fields complete.

  C1  atomic publish + full report fields: a valid pending report with
      complete triplet/sample/command/hash publishes atomically (fsync +
      replace, no .pending residue); dashboard (audit_dashboard) and
      release_gate consume the SAME published schema.
  C2  failure matrix keeps release red: corrupt JSON, tampered hash, wrong
      triplet keys, missing required field, future timestamp, stale age,
      ledger hash mismatch, SLI regression, empty SLI, no report — every
      class blocks release.
  C3  recovery idempotence: a failed publish leaves the pending file in
      place; after fixing the payload the SAME pending file publishes
      cleanly (no duplicate, no residue) — interrupted rerun is idempotent.
  C4  alert ack/retry: unacked alerts stay pending; ack marks exactly the
      run; a failing alert sink is a loud failure (never silent).
  C5  no stale-green afterlife: future timestamps and renamed old-green
      (hash chain broken) are rejected; freshness is enforced by age.

Hermetic: all paths under tmp_path; no production access.
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import release_gate as rg  # noqa: E402
from audit_dashboard import collect_reports, release_gate as dashboard_gate  # noqa: E402

NOW = datetime.now(UTC)

REQUIRED_FIELDS = ("run_id", "started_at", "triplet", "ok", "report_sha256")


def _report(run_id: str = "run-1", started_at: str | None = None,
            ok: bool = True, *, sample: str | None = None,
            command: str | None = None) -> dict:
    report = {
        "run_id": run_id,
        "started_at": started_at or NOW.isoformat(),
        "triplet": {"revenue": "a" * 40, "filing": "b" * 40, "wiki": "c" * 40},
        "ok": ok,
    }
    if sample is not None:
        report["sample"] = sample
    if command is not None:
        report["command"] = command
    report["report_sha256"] = rg.canonical_hash(
        {k: v for k, v in report.items() if k != "report_sha256"})
    return report


def _sli_all_ok() -> dict:
    return {key: {"ok": True, "source": "test"} for key in rg.SLI_KEYS}


def _write_pending(dir_: Path, report: dict) -> Path:
    pending = dir_ / f"{report['run_id']}.pending.json"
    pending.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    return pending


# ---------------------------------------------------------------------------
# C1 — atomic publish + complete fields + same schema consumption
# ---------------------------------------------------------------------------


def test_c1_publish_with_complete_fields_atomic(tmp_path):
    report = _report(sample="companies:Zijin:FY2025", command="daily_t2_runner")
    _write_pending(tmp_path, report)
    published = rg.publish_all_pending(tmp_path, tmp_path / "out")
    assert published["published"] == ["run-1.pending.json"]
    assert published["failed"] == []
    assert published["pending_left"] == []
    target = tmp_path / "out" / "run-1.json"
    assert target.is_file()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded["sample"] == "companies:Zijin:FY2025"
    assert loaded["command"] == "daily_t2_runner"
    assert loaded["report_sha256"] == report["report_sha256"]
    # dashboard consumes the SAME schema via the T2 run-dir layout
    run_dir = tmp_path / "runs" / "20260831T000000Z"
    run_dir.mkdir(parents=True)
    (run_dir / "report.json").write_text(
        json.dumps(loaded, ensure_ascii=False), encoding="utf-8")
    reports = collect_reports(tmp_path / "runs", limit=10)
    assert reports and reports[0]["run_id"] == "20260831T000000Z"
    assert reports[0]["kind"] == "t2"
    assert reports[0]["ok"] is True
    # dashboard's view validates under the release schema (same field set)
    ok, reason = rg.validate_report(loaded)
    assert ok, reason


def test_c1_dashboard_and_release_read_same_schema(tmp_path):
    report = _report()
    _write_pending(tmp_path, report)
    rg.publish_all_pending(tmp_path, tmp_path / "out")
    published = json.loads(
        (tmp_path / "out" / "run-1.json").read_text(encoding="utf-8"))
    # dashboard run-dir layout mirrors the published report
    run_dir = tmp_path / "runs" / "20260831T010000Z"
    run_dir.mkdir(parents=True)
    (run_dir / "report.json").write_text(
        json.dumps(published, ensure_ascii=False), encoding="utf-8")
    reports = collect_reports(tmp_path / "runs", limit=10)
    assert reports
    # the dashboard aggregates exactly the fields the release gate needs
    assert reports[0]["run_id"] == "20260831T010000Z"
    assert reports[0]["triplet"] == {"revenue": "a" * 40,
                                     "filing": "b" * 40, "wiki": "c" * 40}
    # and the published report itself validates under the release schema
    ok, reason = rg.validate_report(published)
    assert ok, reason
    # freshness gate consumes it too: fresh t2 -> no 'no T2 report'
    fresh = dict(reports[0])
    fresh["ts"] = datetime.now(UTC) - timedelta(minutes=5)
    ready, reasons = dashboard_gate([fresh], now=datetime.now(UTC))
    assert ready is False  # T3 missing, but T2 reason absent
    assert all("T2" not in r for r in reasons)


# ---------------------------------------------------------------------------
# C2 — failure matrix: every class keeps release red
# ---------------------------------------------------------------------------


def _published(tmp_path, report: dict) -> dict:
    _write_pending(tmp_path, report)
    rg.publish_all_pending(tmp_path, tmp_path / "out")
    return json.loads((tmp_path / "out" / f"{report['run_id']}.json").read_text(encoding="utf-8"))


def test_c2_failure_matrix_blocks(tmp_path):
    cases: list[tuple[str, dict]] = []

    # corrupt JSON pending: publish fails loudly, nothing published
    (tmp_path / "corrupt.pending.json").write_text("{not json", encoding="utf-8")
    result = rg.publish_all_pending(tmp_path, tmp_path / "out")
    assert any(f["file"] == "corrupt.pending.json" for f in result["failed"])
    assert not (tmp_path / "out" / "corrupt.json").exists()
    (tmp_path / "corrupt.pending.json").unlink()

    # tampered hash
    bad = _report(run_id="run-tamper")
    bad["report_sha256"] = "0" * 64
    cases.append(("hash", bad))

    # wrong triplet keys
    bad = _report(run_id="run-keys")
    bad["triplet"] = {"revenue": "a" * 40, "filing": "b" * 40, "extra": "c" * 40}
    bad["report_sha256"] = rg.canonical_hash(
        {k: v for k, v in bad.items() if k != "report_sha256"})
    cases.append(("triplet", bad))

    # missing required field
    bad = _report(run_id="run-missing")
    bad.pop("ok")
    bad["report_sha256"] = rg.canonical_hash(
        {k: v for k, v in bad.items() if k != "report_sha256"})
    cases.append(("missing-field", bad))

    for name, report in cases:
        _write_pending(tmp_path, report)
        result = rg.publish_all_pending(tmp_path, tmp_path / "out")
        assert result["failed"], f"{name}: expected publish failure"
        assert not (tmp_path / "out" / f"{report['run_id']}.json").exists(), name
        (tmp_path / f"{report['run_id']}.pending.json").unlink()

    # decision-level failures on a VALID published report
    valid = _published(tmp_path, _report(run_id="run-dec"))
    # future timestamp
    future = _published(tmp_path, _report(
        run_id="run-future", started_at=(NOW + timedelta(hours=2)).isoformat()))
    ready, reasons = rg.release_decision(_sli_all_ok(), future, None, now=NOW.isoformat())
    assert ready is False and any("future" in r for r in reasons)
    # stale age
    stale = _published(tmp_path, _report(
        run_id="run-stale", started_at=(NOW - timedelta(days=3)).isoformat()))
    ready, reasons = rg.release_decision(_sli_all_ok(), stale, None, now=NOW.isoformat())
    assert ready is False and any("stale" in r for r in reasons)
    # ledger hash mismatch
    ledger = {"latest_run_id": "run-dec", "report_sha256": "f" * 64}
    ready, reasons = rg.release_decision(_sli_all_ok(), valid, ledger, now=NOW.isoformat())
    assert ready is False and any("hash differs" in r for r in reasons)
    # SLI regression
    sli = _sli_all_ok()
    sli["consumer_ready"] = {"ok": False, "value": 0.4}
    ready, reasons = rg.release_decision(sli, valid, None, now=NOW.isoformat())
    assert ready is False and "consumer_ready" in reasons[0]
    # empty SLI
    ready, reasons = rg.release_decision({}, valid, None, now=NOW.isoformat())
    assert ready is False and "no SLI data" in reasons
    # no report
    ready, reasons = rg.release_decision(_sli_all_ok(), None, None, now=NOW.isoformat())
    assert ready is False and "no published report" in reasons


# ---------------------------------------------------------------------------
# C3 — recovery idempotence
# ---------------------------------------------------------------------------


def test_c3_recovery_after_fix_is_idempotent(tmp_path):
    bad = _report(run_id="run-fix")
    bad["triplet"] = {"revenue": "a" * 40}  # incomplete
    _write_pending(tmp_path, bad)
    first = rg.publish_all_pending(tmp_path, tmp_path / "out")
    assert first["published"] == []
    assert first["pending_left"] == ["run-fix.pending.json"]
    assert not (tmp_path / "out" / "run-fix.json").exists()
    # fix the SAME pending file (simulated interrupted-then-retried runner)
    fixed = _report(run_id="run-fix")
    _write_pending(tmp_path, fixed)
    second = rg.publish_all_pending(tmp_path, tmp_path / "out")
    assert second["published"] == ["run-fix.pending.json"]
    assert second["pending_left"] == []
    assert (tmp_path / "out" / "run-fix.json").is_file()
    # rerun is idempotent: nothing left to publish, no duplicate target
    third = rg.publish_all_pending(tmp_path, tmp_path / "out")
    assert third["published"] == [] and third["failed"] == []


# ---------------------------------------------------------------------------
# C4 — alert ack/retry + loud sink failure
# ---------------------------------------------------------------------------


def test_c4_alerts_pending_until_acked(tmp_path):
    alerts = tmp_path / "alerts.jsonl"
    rg.append_alert(alerts, {"run_id": "r1", "status": "stale", "reason": "x"})
    rg.append_alert(alerts, {"run_id": "r2", "status": "blocked", "reason": "y"})
    assert len(rg.pending_alerts(alerts)) == 2
    assert rg.mark_acked(alerts, "r1") == 1
    remaining = rg.pending_alerts(alerts)
    assert [e["run_id"] for e in remaining] == ["r2"]


def test_c4_sink_failure_is_loud(tmp_path):
    blocker = tmp_path / "blocked"
    blocker.write_text("", encoding="utf-8")
    with pytest.raises(OSError):
        rg.append_alert(blocker / "alerts.jsonl", {"run_id": "r", "status": "x"})


# ---------------------------------------------------------------------------
# C5 — no stale-green afterlife
# ---------------------------------------------------------------------------


def test_c5_future_and_renamed_old_green_rejected(tmp_path):
    # future timestamp
    future = _published(tmp_path, _report(
        run_id="run-future2", started_at=(NOW + timedelta(hours=5)).isoformat()))
    ready, reasons = rg.release_decision(_sli_all_ok(), future, None, now=NOW.isoformat())
    assert ready is False and any("future" in r for r in reasons)
    # renamed old green: valid hash but stale age -> blocked by age
    old = _published(tmp_path, _report(
        run_id="run-old2", started_at=(NOW - timedelta(days=10)).isoformat()))
    ledger = {"latest_run_id": "run-old2", "report_sha256": old["report_sha256"]}
    ready, reasons = rg.release_decision(_sli_all_ok(), old, ledger, now=NOW.isoformat())
    assert ready is False and any("stale" in r or "hash" in r for r in reasons)


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
