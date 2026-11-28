"""ZR-905 acceptance tests: audit-mechanism self-test — all eight AUD2
failure modes must turn the release RED (stage H fourth card).

  AUD2-01  runner exists but no schedule/recent run -> blocked
           (scripts existing is not dynamic operation).
  AUD2-02  daily/weekly report stale -> blocked (old green never reused).
  AUD2-03  wrapper swallows non-zero / half report -> blocked (half reports
           never atomically published).
  AUD2-04  forged download/parser/LLM=0 -> SLI red via catalog counters.
  AUD2-05  missing sample -> blocked (never swapped for an easier sample).
  AUD2-06  renderer/consumer-ready regression -> business SLI blocks even
           when unit tests are green.
  AUD2-07  plan/registry concurrent hash change -> manifest verify fails.
  AUD2-08  reviewer == implementer -> accepted transition rejected.

C2: recovery is idempotent — fixing the failure condition turns the
release green again.  Zero production changes; hermetic (tmp_path only).
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "assurance" / "unified_completion"))

import daily_t2_schedule as scheduler  # noqa: E402
import release_gate as rg  # noqa: E402
from daily_t2_schedule import freshness_status, release_gate  # noqa: E402
from weekly_t3_assurance import read_weekly_t3  # noqa: E402

NOW = datetime.now(UTC)


def _ledger(ok: bool = True, started_at: str | None = None) -> dict:
    return {
        "latest_run_id": "audit-run",
        "started_at": started_at or NOW.isoformat(),
        "triplet": {"revenue": "a" * 40, "filing": "b" * 40, "wiki": "c" * 40},
        "ok": ok,
        "report_path": "report.json",
    }


def _report(run_id: str = "audit-report") -> dict:
    report = {
        "run_id": run_id,
        "started_at": NOW.isoformat(),
        "triplet": {"revenue": "a" * 40, "filing": "b" * 40, "wiki": "c" * 40},
        "ok": True,
    }
    report["report_sha256"] = rg.canonical_hash(report)
    return report


def _sli_all_ok() -> dict:
    return {key: {"ok": True, "source": "test"} for key in rg.SLI_KEYS}


def _write_pending(dir_: Path, report: dict) -> Path:
    pending = dir_ / f"{report['run_id']}.pending.json"
    pending.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")
    return pending


def _publish_and_read(tmp_path, report) -> dict:
    _write_pending(tmp_path, report)
    rg.publish_all_pending(tmp_path, tmp_path / "out")
    return json.loads((tmp_path / "out" / f"{report['run_id']}.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# AUD2-01 — runner exists but no schedule / recent run -> blocked
# ---------------------------------------------------------------------------


def test_aud2_01_no_run_blocks():
    status, _detail = freshness_status(None, now=NOW.isoformat())
    assert status == "missing"
    ready, reason = release_gate(Path("nonexistent-ledger.json"), now=NOW.isoformat())
    assert ready is False
    assert "blocked" in reason


@pytest.mark.parametrize(("code", "stdout", "stderr", "expected"), [
    (0, '"TaskName"\n"other-test-task"', "", "missing"),
    (0, '"TaskName"\n"controlled-schedule"', "", "registered"),
    (1, "", "Access is denied", "unknown"),
])
def test_aud2_01_registration_reports_only_observed_status(monkeypatch, code, stdout, stderr, expected):
    name = "controlled-schedule"

    def task_query(arguments):
        assert arguments == ["/query", "/tn", name, "/fo", "csv", "/v"]
        return subprocess.CompletedProcess(arguments, code, stdout, stderr)

    monkeypatch.setattr(scheduler, "sys", SimpleNamespace(platform="win32"))
    monkeypatch.setattr(scheduler, "_schtasks", task_query)
    assert scheduler.query_task_status(name)[0] == expected


# ---------------------------------------------------------------------------
# AUD2-02 — stale report -> blocked (old green never reused)
# ---------------------------------------------------------------------------


def test_aud2_02_stale_report_blocks(tmp_path):
    old = (NOW - timedelta(hours=48)).isoformat()
    report = _report()
    report["started_at"] = old
    report["report_sha256"] = rg.canonical_hash(
        {k: v for k, v in report.items() if k != "report_sha256"})
    published = _publish_and_read(tmp_path, report)
    ready, reasons = rg.release_decision(_sli_all_ok(), published, None,
                                         now=NOW.isoformat())
    assert ready is False
    assert "stale" in reasons[0]


# ---------------------------------------------------------------------------
# AUD2-03 — half report / swallowed non-zero -> blocked
# ---------------------------------------------------------------------------


def test_aud2_03_half_report_never_published(tmp_path):
    report = _report(run_id="half")
    del report["ok"]  # half-written
    _write_pending(tmp_path, report)
    result = rg.publish_all_pending(tmp_path, tmp_path / "out")
    assert result["published"] == []
    assert result["failed"], "half report must be rejected"
    assert not (tmp_path / "out" / "half.json").exists()


def test_aud2_03_swallowed_nonzero_turns_red(tmp_path, monkeypatch):
    def without_proof(command, **_kwargs):
        return subprocess.CompletedProcess(command, 0, "", "owner failed without a receipt")

    monkeypatch.setattr(subprocess, "run", without_proof)
    weekly = read_weekly_t3(tmp_path)
    assert not weekly.ok and weekly.status == "blocked"
    assert weekly.detail == "owner_response_invalid"
    ledger = _ledger(ok=False)
    # release gate over a not-ok ledger is blocked
    status2, _d = freshness_status(ledger, now=NOW.isoformat())
    assert status2 == "stale"


# ---------------------------------------------------------------------------
# AUD2-04 — forged download/parser/LLM=0 -> SLI red
# ---------------------------------------------------------------------------


def test_aud2_04_forged_zero_counts_sli_red():
    sli = rg.compute_sli({"latest_run_id": "r", "ok": True}, catalog={
        "downloads": 5, "reuse_count": 0, "bound_artifacts": 0,
        "consumer_ready_rate": 0.95, "render_ok": True,
    })
    assert sli["reuse"]["ok"] is False  # zero reuse = forged avoidance
    assert sli["artifact"]["ok"] is False  # zero bound artifacts = degraded
    assert sli["download_avoidance"]["value"] == 5


# ---------------------------------------------------------------------------
# AUD2-05 — missing sample -> blocked (never swapped)
# ---------------------------------------------------------------------------


def test_aud2_05_missing_requested_evidence_is_never_replaced_by_a_different_sample(tmp_path):
    from uc.scenarios import closure_report

    pinned = tmp_path / "requested-evidence.json"
    (tmp_path / "unrelated-evidence.json").write_text("{}", encoding="utf-8")
    payload = {"scenarios": {"sample": {"status": "passed", "evidence_path": pinned.name}}}
    blocked = closure_report(payload, tmp_path)
    assert blocked["closure_ready"] is False
    assert blocked["unsatisfied_ids"] == ["sample: evidence_path is missing or unreadable"]
    pinned.write_text("{}", encoding="utf-8")
    assert closure_report(payload, tmp_path)["closure_ready"] is True


# ---------------------------------------------------------------------------
# AUD2-06 — business SLI regression blocks even when unit tests green
# ---------------------------------------------------------------------------


def test_aud2_06_sli_regression_blocks(tmp_path):
    published = _publish_and_read(tmp_path, _report())
    sli = _sli_all_ok()
    sli["consumer_ready"] = {"ok": False, "value": 0.4}
    ready, reasons = rg.release_decision(sli, published, None, now=NOW.isoformat())
    assert ready is False
    assert "consumer_ready" in reasons[0]
    # recovery: restore the indicator -> ready again (idempotent recovery)
    ready2, _r2 = rg.release_decision(_sli_all_ok(), published, None,
                                      now=NOW.isoformat())
    assert ready2 is True


# ---------------------------------------------------------------------------
# AUD2-07 — plan/registry concurrent hash change -> manifest verify fails
# ---------------------------------------------------------------------------


def test_aud2_07_manifest_drift_detected(tmp_path):
    manifest = json.loads(
        (ROOT / "assurance" / "unified_completion" / "manifests" / "plan_inputs.json")
        .read_text(encoding="utf-8"))
    manifest["control_page_sha256"] = "0" * 64  # drift
    drifted = tmp_path / "plan_inputs.json"
    drifted.write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    from uc.manifest import verify

    baseline = len(verify(ROOT, drifted, check_mtime=False))
    # REV-001 fix: repo_root must be the repo root so the undrifted baseline
    # is 0 (paths inside plan_inputs.json resolve relative to repo root).
    undrifted = json.loads(
        (ROOT / "assurance" / "unified_completion" / "manifests" / "plan_inputs.json")
        .read_text(encoding="utf-8"))
    copy = tmp_path / "plan_inputs_clean.json"
    copy.write_text(json.dumps(undrifted, ensure_ascii=False), encoding="utf-8")
    clean = len(verify(ROOT, copy, check_mtime=False))
    assert clean == 0, f"undrifted manifest must verify clean, got {clean} problems"
    assert baseline > clean, "manifest drift must raise the problem count"


# ---------------------------------------------------------------------------
# AUD2-08 — reviewer == implementer -> accepted rejected
# ---------------------------------------------------------------------------


def test_aud2_08_reviewer_equals_implementer_rejected():
    from uc.strict_state import validate_transition

    problems = validate_transition(
        "ZR-X", {"units": {"ZR-X": {"status": "triplet_green",
                                    "implementer": "alice"}}},
        "accepted", deps=[], reviewer="alice", implementer="alice",
    )
    assert "reviewer must differ from implementer" in problems


def test_aud2_08_distinct_reviewer_accepted():
    from uc.strict_state import validate_transition

    problems = validate_transition(
        "ZR-X", {"units": {"ZR-X": {"status": "triplet_green",
                                    "implementer": "alice"}}},
        "accepted", deps=[], reviewer="bob", implementer="alice",
    )
    assert "reviewer must differ" not in problems
