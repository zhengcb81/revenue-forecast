"""Public filing-fetch receipt handoff exercised through RF's normal entry points."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CASES = ("cn_annual", "hk_annual", "us_annual", "corrupt_original")
OWNER_RUN = "recorded-ff-run"


def receipt(**changes):
    return {
        "schema_version": "ff-t3-assurance/1",
        "run_id": OWNER_RUN,
        "owner_revision": "a" * 40,
        "mode": "live",
        "state": "completed",
        "completed_at": (datetime.now(UTC) - timedelta(hours=1)).isoformat(),
        "cases": {name: {"outcome": "passed", "evidence_ref": f"ff-t3/{OWNER_RUN}/{name}",
                          "reason": None} for name in CASES},
        **changes,
    }


@pytest.fixture
def owner(tmp_path):
    root = tmp_path / "ff-tool"
    script = root / "scripts" / "ff_t3_receipt.py"
    script.parent.mkdir(parents=True)
    receipts = tmp_path / "ff-receipts"
    receipts.mkdir()
    script.write_text(
        """import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--receipts-dir", type=Path, required=True)
sub = parser.add_subparsers(dest="command", required=True)
get = sub.add_parser("get")
source = get.add_mutually_exclusive_group(required=True)
source.add_argument("--run-id")
source.add_argument("--latest", action="store_true")
args = parser.parse_args()
data = json.loads((args.receipts_dir / "next.json").read_bytes())
assert args.run_id == data["requested"]
print(json.dumps(data["reply"]))
raise SystemExit(data["code"])
""", encoding="utf-8",
    )

    def configure(reply, *, code=0, requested=None):
        (receipts / "next.json").write_text(
            json.dumps({"reply": reply, "code": code, "requested": requested}, ensure_ascii=False),
            encoding="utf-8",
        )
        return ["--filing-fetch-root", str(root), "--receipts-dir", str(receipts)]

    return configure


def weekly(tmp_path, flags):
    ledger = tmp_path / "rf" / "weekly_manifest.json"
    alerts = ledger.with_name("weekly_alert.jsonl")
    process = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tools" / "weekly_t3_schedule.py"),
         "--ledger", str(ledger), "--alerts", str(alerts), "run-weekly", *flags],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", timeout=20, check=False,
    )
    assert ledger.exists(), process.stderr
    state = json.loads(ledger.read_bytes())
    report = json.loads(ledger.with_name(state["report_path"]).read_bytes())
    return process, state, report, alerts


def test_public_latest_uses_owner_completion_and_keeps_distinct_rf_reports(tmp_path, owner):
    payload = receipt()
    flags = owner(payload)
    first, previous, original, alerts = weekly(tmp_path, flags)
    second, current, reread, _ = weekly(tmp_path, flags)
    assert first.returncode == second.returncode == 0
    assert previous["ok"] is current["ok"] is True
    assert previous["started_at"] == current["started_at"] == payload["completed_at"]
    assert previous["report_path"] != current["report_path"]
    assert original["receipt"] == reread["receipt"] == payload and not alerts.exists()


def test_owner_revision_unavailable_is_diagnostic_for_complete_proof(tmp_path, owner):
    payload = receipt(owner_revision="unknown")
    process, ledger, report, _ = weekly(tmp_path, owner(payload))
    assert process.returncode == 0 and ledger["ok"] is True
    assert report["receipt"]["owner_revision"] == "unknown"


def test_public_evidence_preserves_owner_run_ids_with_colon(tmp_path, owner):
    owner_id = "a:"
    payload = receipt(run_id=owner_id)
    for name, case in payload["cases"].items():
        case["evidence_ref"] = f"ff-t3/{owner_id}/{name}"
    process, ledger, report, _ = weekly(tmp_path, owner(payload))
    assert process.returncode == 0 and ledger["ok"] is True
    assert report["receipt"] == payload


@pytest.mark.parametrize(
    "area, value, detail",
    [
        ("mode", "offline", "owner_receipt_offline"),
        ("state", "running", "owner_receipt_incomplete"),
        ("cases", {}, "owner_cases_incomplete"),
        ("completed_at", "2026-01-01T01:00:00Z", "owner_receipt_stale"),
        ("completed_at", "2099-12-31T23:59:00Z", "owner_completion_time_invalid"),
        ("run_id", "wrong-owner-run", "owner_run_mismatch"),
    ],
)
def test_unconfirmed_stale_or_different_run_is_blocked(tmp_path, owner, area, value, detail):
    flags = owner(receipt(**{area: value}), requested=OWNER_RUN)
    process, ledger, report, alerts = weekly(tmp_path, [*flags, "--run-id", OWNER_RUN])
    assert process.returncode != 0 and not ledger["ok"]
    assert report["status"] == "blocked" and report["detail"] == detail
    events = [json.loads(line) for line in alerts.read_text(encoding="utf-8").splitlines()]
    assert events[-1]["status"] == "blocked" and events[-1]["reason"] == detail


def test_owner_failure_is_kept_when_another_case_is_blocked(tmp_path, owner):
    payload = receipt()
    payload["cases"]["cn_annual"].update(outcome="failed", reason="original_sha_mismatch")
    payload["cases"]["hk_annual"].update(outcome="blocked", reason="provider_not_configured",
                                         evidence_ref=None)
    diagnostic = {"schema_version": "ff-failure-detail/1", "reason": "assertion_failed",
                  "causes": [{"type": "AssertionError", "relation": "raised",
                              "frames": [{"file": "owner_case.py", "function": "execute",
                                          "line": number}]} for number in range(300)]}
    payload["diagnostic"] = diagnostic
    payload["cases"]["cn_annual"]["diagnostic"] = diagnostic
    payload["debug"] = "credential FICTITIOUS_PRIVATE_MESSAGE"
    process, ledger, report, alerts = weekly(tmp_path, owner(payload))
    assert process.returncode == 1 and not ledger["ok"]
    assert report["status"] == "not-ok" and report["detail"] == "owner_case_failed"
    assert report["receipt"]["cases"] == payload["cases"]
    assert report["receipt"]["diagnostic"] == diagnostic
    assert "cost_state" not in report
    assert "FICTITIOUS_PRIVATE_MESSAGE" not in json.dumps(report)
    assert "original_sha_mismatch" in json.dumps(report)
    assert json.loads(alerts.read_text(encoding="utf-8"))["status"] == "not-ok"


@pytest.mark.parametrize(
    "state, ff_code, owner_reason",
    [("missing", 2, None), ("unknown", 0, "receipt_unreadable"), ("unknown", 1, "receipt_io_failed")],
)
def test_missing_and_unknown_owner_receipts_stay_visible(tmp_path, owner, state, ff_code, owner_reason):
    payload = {"schema_version": "ff-t3-assurance/1", "run_id": None, "state": state}
    if owner_reason is not None:
        payload["reason"] = owner_reason
    process, ledger, report, alerts = weekly(tmp_path, owner(payload, code=ff_code))
    assert process.returncode == 2 and not ledger["ok"]
    assert report["detail"] == (owner_reason or "owner_receipt_missing")
    assert report["receipt"] == payload and report["owner_exit_code"] == ff_code
    assert json.loads(alerts.read_bytes())["reason"] == report["detail"]


def test_manual_legacy_force_only_reads_named_owner_receipt(tmp_path, owner):
    payload = receipt()
    flags = owner(payload, requested=OWNER_RUN)
    report_root = tmp_path / "rf-manual"
    process = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tools" / "weekly_t3_runner.py"),
         "--report-root", str(report_root), "--run-id", "local-rf-run",
         "--force", "--owner-run-id", OWNER_RUN, *flags],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", timeout=20, check=False,
    )
    assert process.returncode == 0, process.stderr
    report = json.loads((report_root / "local-rf-run" / "t3_report.json").read_bytes())
    assert report["status"] == "passed" and report["receipt"] == payload


def test_manual_repeat_preserves_the_archived_report_and_uses_a_new_observation(tmp_path, owner):
    report_root = tmp_path / "rf-manual"
    old = report_root / "local-rf-run" / "t3_report.json"
    old.parent.mkdir(parents=True)
    archived = b'{"status":"blocked","reason":"old report"}\n'
    old.write_bytes(archived)
    flags = owner(receipt())
    process = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tools" / "weekly_t3_runner.py"),
         "--report-root", str(report_root), "--run-id", "local-rf-run", *flags],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8", timeout=20, check=False,
    )
    assert process.returncode == 0, process.stderr
    assert old.read_bytes() == archived
    (new,) = [path for path in report_root.rglob("t3_report.json") if path != old]
    value = json.loads(new.read_bytes())
    assert value["run_id"] == new.parent.name and new.parent.name.startswith("local-rf-run-")
    assert value["status"] == "passed" and new.parent.name in process.stdout
