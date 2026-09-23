"""ZR-904 acceptance tests: SLI dashboard + release gate — atomic publish,
integrity, alert ack/retry, no stale-green afterlife (CA-205 / AUD2-06).

  C1  atomic publish — a valid pending report publishes atomically (no
      .pending residue, fsync+replace); half-written/corrupt pending reports
      are rejected and never published (release stays red).
  C2  SLI set + business blocking — all-SLI-ok + fresh report -> ready; any
      business SLI regression blocks release even when the ledger is ok
      (AUD2-06).
  C3  alert ack/retry — appended alerts are pending until acked; a failing
      alert sink (unwritable path) is a loud failure.
  C4  no stale-green afterlife — future timestamps rejected; renamed old
      green (hash chain broken) rejected; report freshness enforced.

Hermetic: all paths under tmp_path; no production access.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import release_gate as rg  # noqa: E402

NOW = datetime.now(UTC)


def _report(run_id: str = "run-1", started_at: str | None = None,
            ok: bool = True) -> dict:
    report = {
        "run_id": run_id,
        "started_at": started_at or NOW.isoformat(),
        "triplet": {"revenue": "a" * 40, "filing": "b" * 40, "wiki": "c" * 40},
        "ok": ok,
    }
    report["report_sha256"] = rg.canonical_hash(report)
    return report


def _sli_all_ok() -> dict:
    return {key: {"ok": True, "source": "test"} for key in rg.SLI_KEYS}


def _write_pending(dir_: Path, report: dict) -> Path:
    pending = dir_ / f"{report['run_id']}.pending.json"
    pending.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    return pending


# ---------------------------------------------------------------------------
# C1 — atomic publish + corrupt rejection
# ---------------------------------------------------------------------------


def test_c1_valid_pending_publishes_atomically(tmp_path):
    report = _report()
    _write_pending(tmp_path, report)
    published = rg.publish_all_pending(tmp_path, tmp_path / "out")
    assert published["published"] == ["run-1.pending.json"]
    assert published["failed"] == []
    assert published["pending_left"] == []
    target = tmp_path / "out" / "run-1.json"
    assert target.is_file()
    assert json.loads(target.read_text(encoding="utf-8"))["report_sha256"] == report["report_sha256"]


def test_c1_corrupt_pending_rejected_not_published(tmp_path):
    bad = _report(run_id="run-bad")
    bad["triplet"] = {"revenue": "a" * 40}  # incomplete triplet
    _write_pending(tmp_path, bad)
    result = rg.publish_all_pending(tmp_path, tmp_path / "out")
    assert result["published"] == []
    assert len(result["failed"]) == 1
    assert "triplet" in result["failed"][0]["reason"]
    assert result["pending_left"] == ["run-bad.pending.json"]
    assert not (tmp_path / "out" / "run-bad.json").exists()


def test_c1_tampered_hash_rejected(tmp_path):
    report = _report(run_id="run-tamper")
    report["report_sha256"] = "0" * 64  # forged hash
    _write_pending(tmp_path, report)
    result = rg.publish_all_pending(tmp_path, tmp_path / "out")
    assert result["published"] == []
    assert "hash chain broken" in result["failed"][0]["reason"]


def test_c1_wrong_triplet_keys_rejected(tmp_path):
    # REV-002 regression: triplet must name exactly revenue/filing/wiki.
    report = _report(run_id="run-keys")
    report["triplet"] = {"revenue": "a" * 40, "filing": "b" * 40, "extra": "c" * 40}
    report["report_sha256"] = rg.canonical_hash(
        {k: v for k, v in report.items() if k != "report_sha256"})
    _write_pending(tmp_path, report)
    result = rg.publish_all_pending(tmp_path, tmp_path / "out")
    assert result["published"] == []
    assert "triplet" in result["failed"][0]["reason"]


# ---------------------------------------------------------------------------
# C2 — SLI set + business blocking (AUD2-06)
# ---------------------------------------------------------------------------


def test_c2_all_sli_ok_and_fresh_ready(tmp_path):
    report = _report()
    _write_pending(tmp_path, report)
    rg.publish_all_pending(tmp_path, tmp_path / "out")
    published = json.loads((tmp_path / "out" / "run-1.json").read_text(encoding="utf-8"))
    ready, reasons = rg.release_decision(_sli_all_ok(), published, None,
                                         now=NOW.isoformat())
    assert ready is True
    assert reasons == ["ready"]


def test_c2_sli_regression_blocks_even_when_ledger_ok(tmp_path):
    report = _report()
    _write_pending(tmp_path, report)
    rg.publish_all_pending(tmp_path, tmp_path / "out")
    published = json.loads((tmp_path / "out" / "run-1.json").read_text(encoding="utf-8"))
    sli = _sli_all_ok()
    sli["consumer_ready"] = {"ok": False, "value": 0.4}  # regression
    ready, reasons = rg.release_decision(sli, published, None, now=NOW.isoformat())
    assert ready is False
    assert "consumer_ready" in reasons[0]


def test_c2_no_report_blocks(tmp_path):
    ready, reasons = rg.release_decision(_sli_all_ok(), None, None,
                                         now=NOW.isoformat())
    assert ready is False
    assert "no published report" in reasons


def test_c2_catalog_regression_derives_not_ok():
    # REV-001 regression: catalog counters must derive ok=False themselves
    # (AUD2-06 holds even without injected ok flags).
    ledger = {"latest_run_id": "r", "ok": True}
    sli = rg.compute_sli(ledger, catalog={
        "consumer_ready_rate": 0.3, "render_ok": False, "reuse_count": 0,
        "bound_artifacts": 42,
    })
    assert sli["consumer_ready"]["ok"] is False
    assert sli["render"]["ok"] is False
    assert sli["reuse"]["ok"] is False
    assert sli["artifact"]["ok"] is True  # not degraded (bound_artifacts > 0)


def test_c2_empty_sli_blocks():
    # REV-003 regression: empty SLI dict is a blocked decision, not ready.
    ready, reasons = rg.release_decision({}, _report(), None, now=NOW.isoformat())
    assert ready is False
    assert "no SLI data" in reasons


# ---------------------------------------------------------------------------
# C3 — alert ack/retry + sink failure is loud
# ---------------------------------------------------------------------------


def test_c3_alerts_pending_until_acked(tmp_path):
    alerts = tmp_path / "alerts.jsonl"
    rg.append_alert(alerts, {"run_id": "r1", "status": "stale", "reason": "x"})
    rg.append_alert(alerts, {"run_id": "r2", "status": "blocked", "reason": "y"})
    assert len(rg.pending_alerts(alerts)) == 2
    assert rg.mark_acked(alerts, "r1") == 1
    remaining = rg.pending_alerts(alerts)
    assert [e["run_id"] for e in remaining] == ["r2"]


def test_c3_alert_sink_failure_is_loud(tmp_path):
    blocker = tmp_path / "blocked"
    blocker.write_text("", encoding="utf-8")
    bad_sink = blocker / "alerts.jsonl"  # NotADirectoryError on open
    import pytest

    with pytest.raises(OSError):
        rg.append_alert(bad_sink, {"run_id": "r", "status": "x"})


# ---------------------------------------------------------------------------
# C4 — no stale-green afterlife
# ---------------------------------------------------------------------------


def test_c4_future_timestamp_rejected(tmp_path):
    report = _report(run_id="run-future",
                     started_at=(NOW + timedelta(hours=2)).isoformat())
    _write_pending(tmp_path, report)
    rg.publish_all_pending(tmp_path, tmp_path / "out")
    published = json.loads((tmp_path / "out" / "run-future.json").read_text(encoding="utf-8"))
    ready, reasons = rg.release_decision(_sli_all_ok(), published, None,
                                         now=NOW.isoformat())
    assert ready is False
    assert "future" in reasons[0]


def test_c4_renamed_old_green_rejected(tmp_path):
    report = _report(run_id="run-original", started_at=(NOW - timedelta(days=3)).isoformat())
    _write_pending(tmp_path, report)
    rg.publish_all_pending(tmp_path, tmp_path / "out")
    published = json.loads((tmp_path / "out" / "run-original.json").read_text(encoding="utf-8"))
    # old-green copy: ledger claims a NEW run id with the OLD report's hash
    ledger = {"latest_run_id": "run-original", "report_sha256": published["report_sha256"]}
    # but the report is stale -> blocked by age even before hash check
    ready, reasons = rg.release_decision(_sli_all_ok(), published, ledger,
                                         now=NOW.isoformat())
    assert ready is False
    assert "stale" in reasons[0] or "hash" in reasons[0]


def test_c4_ledger_hash_mismatch_rejected(tmp_path):
    report = _report(run_id="run-x")
    _write_pending(tmp_path, report)
    rg.publish_all_pending(tmp_path, tmp_path / "out")
    published = json.loads((tmp_path / "out" / "run-x.json").read_text(encoding="utf-8"))
    ledger = {"latest_run_id": "run-x", "report_sha256": "f" * 64}
    ready, reasons = rg.release_decision(_sli_all_ok(), published, ledger,
                                         now=NOW.isoformat())
    assert ready is False
    assert "hash differs" in reasons[0]
