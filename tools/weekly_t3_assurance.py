"""Read filing-fetch's published weekly T3 receipt through its public command."""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

if __package__:
    from .rf_owner_runtime import child_traceback_facts
else:
    from rf_owner_runtime import child_traceback_facts

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FILING_ROOT = PROJECT_ROOT.parent / "filing-fetch"
RECEIPT_SCHEMA = "ff-t3-assurance/1"
REPORT_SCHEMA = "rf-weekly-t3-check/1"
MAX_AGE_DAYS = 7
CASE_NAMES = ("cn_annual", "hk_annual", "us_annual", "corrupt_original")
_OUTCOME = {"ok": 0, "not-ok": 1, "blocked": 2}
_STATES = ("running", "completed", "blocked", "unknown", "missing")
_RESULT = ("passed", "failed", "blocked")
_LABEL = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]*")
_REFERENCE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/@-]*")


@dataclass(frozen=True)
class WeeklyT3Result:
    status: str
    detail: str
    observed_at: str
    receipt: dict | None = None
    owner_exit_code: int | None = None
    requested_owner_run_id: str | None = None
    cause_chain: tuple[dict[str, str | int], ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == "ok"

    @property
    def exit_code(self) -> int:
        return _OUTCOME[self.status]

    @property
    def ledger_time(self) -> str:
        # The legacy ledger's started_at controls freshness. An RF reread never
        # changes the time at which the owner completed its proof.
        return (self.receipt or {}).get("completed_at") or self.observed_at

    def report(self, run_id: str) -> dict:
        return {
            "schema_version": REPORT_SCHEMA,
            "run_id": run_id,
            "status": self.status,
            "detail": self.detail,
            "ok": self.ok,
            "observed_at": self.observed_at,
            "requested_owner_run_id": self.requested_owner_run_id,
            "owner_exit_code": self.owner_exit_code,
            "cause_chain": list(self.cause_chain),
            "receipt": self.receipt,
        }


def add_owner_options(parser: argparse.ArgumentParser, *, run_id_option: str = "--run-id") -> None:
    parser.add_argument("--filing-fetch-root", type=Path, default=FILING_ROOT,
                        help="checkout or installation containing the filing-fetch public receipt command")
    parser.add_argument("--receipts-dir", type=Path,
                        help="optional override passed to the filing-fetch owner command")
    parser.add_argument(run_id_option, dest="owner_run_id",
                        help="read an exact FF run instead of asking the owner for its latest receipt")


def receipt_label(value: object) -> str | None:
    """Return a safe opaque label from the public receipt contract."""
    return value if isinstance(value, str) and _LABEL.fullmatch(value) else None


def _reference(value: object) -> str | None:
    if not isinstance(value, str) or not _REFERENCE.fullmatch(value):
        return None
    if re.match(r"[A-Za-z]:/", value) or ".." in value.split("/"):
        return None
    return value


def _stamp(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def _unique_fields(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate receipt field")
        result[key] = value
    return result


def _reject_constant(_value):
    raise ValueError("non-finite receipt number")


def _finite_float(text: str) -> float:
    value = float(text)
    if not math.isfinite(value):
        _reject_constant(text)
    return value


def _decode(payload: str) -> dict | None:
    try:
        value = json.loads(
            payload, object_pairs_hook=_unique_fields, parse_constant=_reject_constant,
            parse_float=_finite_float,
        )
    except (TypeError, ValueError, RecursionError):
        return None
    if not isinstance(value, dict) or value.get("schema_version") != RECEIPT_SCHEMA:
        return None
    return value


def _diagnostic(value: object) -> dict | None:
    # The FF owner projects this known public diagnostic to typed, pathless
    # facts before returning it. Preserve all such facts for its cold readers.
    if isinstance(value, dict) and value.get("schema_version") == "ff-failure-detail/1":
        return value
    return None


def _project_receipt(raw: dict) -> dict:
    """Keep named owner facts, rather than child stdout, stderr or paths."""
    receipt = {"schema_version": RECEIPT_SCHEMA, "run_id": receipt_label(raw.get("run_id"))}
    for field in ("mode", "state", "owner_revision", "reason"):
        if field in raw:
            receipt[field] = receipt_label(raw[field])
    for field in ("started_at", "completed_at"):
        if field in raw:
            receipt[field] = raw[field] if _stamp(raw[field]) else None
    diagnostic = _diagnostic(raw.get("diagnostic"))
    if diagnostic is not None:
        receipt["diagnostic"] = diagnostic
    if isinstance(raw.get("cases"), dict):
        cases = {}
        for name in CASE_NAMES:
            entry = raw["cases"].get(name)
            if not isinstance(entry, dict):
                continue
            outcome = entry.get("outcome")
            case = {
                "outcome": outcome if outcome in _RESULT else "unknown",
                "reason": receipt_label(entry.get("reason")),
                "evidence_ref": _reference(entry.get("evidence_ref")),
            }
            diagnostic = _diagnostic(entry.get("diagnostic"))
            if diagnostic is not None:
                case["diagnostic"] = diagnostic
            cases[name] = case
        receipt["cases"] = cases
    return receipt


def _classify(receipt: dict, owner_exit: int, requested: str | None,
              observed: datetime) -> tuple[str, str]:
    run_id = receipt["run_id"]
    state = receipt.get("state")
    cases = receipt.get("cases", {})
    if requested is not None and run_id is not None and run_id != requested:
        return "blocked", "owner_run_mismatch"
    if state == "missing":
        return "blocked", receipt.get("reason") or "owner_receipt_missing"
    if owner_exit != 0:
        return "blocked", receipt.get("reason") or "owner_lookup_unavailable"
    if not run_id or state not in _STATES:
        return "blocked", receipt.get("reason") or "owner_run_unconfirmed"
    if any(case["outcome"] == "failed" for case in cases.values()):
        return "not-ok", "owner_case_failed"
    if receipt.get("mode") == "offline":
        return "blocked", "owner_receipt_offline"
    if state != "completed":
        return "blocked", receipt.get("reason") or "owner_receipt_incomplete"
    if receipt.get("mode") != "live":
        return "blocked", "owner_run_unconfirmed"
    completed = _stamp(receipt.get("completed_at"))
    if completed is None or completed > observed:
        return "blocked", "owner_completion_time_invalid"
    if observed - completed > timedelta(days=MAX_AGE_DAYS):
        return "blocked", "owner_receipt_stale"
    if not all(
        name in cases and cases[name]["outcome"] == "passed" and cases[name]["evidence_ref"]
        for name in CASE_NAMES
    ):
        return "blocked", "owner_cases_incomplete"
    return "ok", "owner_live_receipt_verified"


def read_weekly_t3(
    filing_fetch_root: Path = FILING_ROOT,
    *,
    receipts_dir: Path | None = None,
    owner_run_id: str | None = None,
    now: datetime | None = None,
) -> WeeklyT3Result:
    """Locate an existing owner result. This port has no acquisition operation."""
    requested = receipt_label(owner_run_id)
    try:
        argv = [sys.executable, "-B", str(filing_fetch_root.absolute() / "scripts" / "ff_t3_receipt.py")]
        if receipts_dir is not None:
            argv.extend(("--receipts-dir", str(receipts_dir.absolute())))
        argv.append("get")
        argv.extend(("--run-id", owner_run_id) if owner_run_id is not None else ("--latest",))
        process = subprocess.run(
            argv, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=30, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return WeeklyT3Result(
            "blocked", "owner_lookup_timeout", (now or datetime.now(UTC)).isoformat(),
            requested_owner_run_id=requested,
            cause_chain=({"type": type(exc).__name__},),
        )
    except (OSError, ValueError) as exc:
        return WeeklyT3Result(
            "blocked", "owner_lookup_unavailable", (now or datetime.now(UTC)).isoformat(),
            requested_owner_run_id=requested,
            cause_chain=({"type": type(exc).__name__},),
        )
    observed = now or datetime.now(UTC)
    raw = _decode(process.stdout)
    if raw is None:
        detail = "owner_response_invalid" if process.returncode == 0 else "owner_lookup_unavailable"
        return WeeklyT3Result(
            "blocked", detail, observed.isoformat(), owner_exit_code=process.returncode,
            requested_owner_run_id=requested,
            cause_chain=tuple(child_traceback_facts(process.stderr, source="ff_t3_receipt.py")),
        )
    receipt = _project_receipt(raw)
    status, detail = _classify(receipt, process.returncode, owner_run_id, observed)
    return WeeklyT3Result(
        status, detail, observed.isoformat(), receipt, process.returncode, requested,
        tuple(child_traceback_facts(process.stderr, source="ff_t3_receipt.py")) if process.returncode else (),
    )
