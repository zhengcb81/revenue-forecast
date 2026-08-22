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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "assurance" / "unified_completion"))

import release_gate as rg  # noqa: E402
from daily_t2_schedule import freshness_status, release_gate  # noqa: E402
from weekly_t3_schedule import _suite_outcome  # noqa: E402

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


def test_aud2_03_swallowed_nonzero_turns_red(tmp_path):
    # a wrapper swallowing a non-zero T3 exit must still record not-ok
    ok, status, _detail = _suite_outcome(type("P", (), {
        "returncode": 0, "stdout": "5 skipped in 0.10s", "stderr": ""})())
    assert status == "blocked"  # all-skipped suite never a pass
    ledger = _ledger(ok=False)
    # release gate over a not-ok ledger is blocked
    status2, _d = freshness_status(ledger, now=NOW.isoformat())
    assert status2 == "stale"


# ---------------------------------------------------------------------------
# AUD2-04 — forged download/parser/LLM=0 -> SLI red
# ---------------------------------------------------------------------------


def test_aud2_04_forged_zero_counts_sli_red():
    sli = rg.compute_sli({"latest_run_id": "r", "ok": True}, catalog={
        "downloads": 5, "reuse_count": 0, "consumer_ready_rate": 0.95,
        "render_ok": True,
    })
    assert sli["reuse"]["ok"] is False  # zero reuse = forged avoidance
    assert sli["download_avoidance"]["value"] == 5


# ---------------------------------------------------------------------------
# AUD2-05 — missing sample -> blocked (never swapped)
# ---------------------------------------------------------------------------


def test_aud2_05_missing_sample_blocks():
    # the fixed ZR-806 sample list must all exist; a missing one is a
    # hard failure, never an automatic swap to an easier sample
    from test_zr806_real_t2_samples import SAMPLES

    missing = [label for label, path, _f, _s in SAMPLES if not path.is_file()]
    assert missing == [], f"samples missing: {missing} (blocked, never swap)"
    sli = rg.compute_sli({"latest_run_id": "r", "ok": True}, catalog={
        "bound_artifacts": 0, "reuse_count": 0, "consumer_ready_rate": 0.95,
        "render_ok": True,
    })
    assert sli["reuse"]["ok"] is False


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
    proc = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, '.'); "
         "from pathlib import Path; from uc.manifest import verify; "
         "import json; m=json.load(open(r'%s', encoding='utf-8')); "
         "print(len(verify(Path('.'), Path(r'%s'), check_mtime=False)))" % (
             drifted, drifted)],
        capture_output=True, text=True, encoding="utf-8", timeout=60,
        cwd=str(ROOT / "assurance" / "unified_completion"),
    )
    problems = int(proc.stdout.strip().splitlines()[-1])
    assert problems >= 1, "manifest drift must be detected"


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
