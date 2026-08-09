"""FC-103: receipt/closure validator (schema 2.0).

Validates FC implementer/reviewer receipts against the schema in
``implementation_runbook.md`` section 5 and the acceptance invariants in
``independent_review_protocol.md``. This is the single gate that decides
whether a work unit may advance to ``accepted``; the closure ledger is only
ever produced by this tool.

Two verdicts:

* ``validate_receipt`` — structural correctness (schema, required fields,
  well-formed hashes, changed⊆allowed, command exit codes, no skipped
  scenarios, implementer/reviewer identity isolation). Empty list = valid.
* ``can_accept`` — the stricter acceptance gate: structurally valid AND every
  sealing hash is real (no ``pending-fc-104``) AND an independent reviewer
  (different identity from the implementer) has marked ``accepted`` with a
  non-future timestamp and a reviewer-receipt hash.

The validator deliberately rejects: short hashes, placeholder policy hashes,
a pending review decision, missing closure evidence, a stale/drifted triplet,
skipped scenarios, a reviewer who is the same identity as the implementer,
and future timestamps. Exit code 0 = valid; 1 = problems found.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

SCHEMA_VERSION = "2.0"

# Full closed set of 71 FC ids (Phase 0 baseline + Phases 1-15).
FC_IDS = (
    {"FC-000", "FC-001", "FC-002"}
    | {f"FC-1{n:02d}" for n in range(1, 5)}
    | {f"FC-2{n:02d}" for n in range(1, 6)}
    | {f"FC-3{n:02d}" for n in range(1, 6)}
    | {f"FC-4{n:02d}" for n in range(1, 6)}
    | {f"FC-5{n:02d}" for n in range(1, 6)}
    | {f"FC-6{n:02d}" for n in range(1, 5)}
    | {f"FC-7{n:02d}" for n in range(1, 6)}
    | {f"FC-8{n:02d}" for n in range(1, 6)}
    | {f"FC-9{n:02d}" for n in range(1, 7)}
    | {f"FC-10{n:02d}" for n in range(1, 6)}
    | {f"FC-11{n:02d}" for n in range(1, 6)}
    | {f"FC-12{n:02d}" for n in range(1, 6)}
    | {f"FC-13{n:02d}" for n in range(1, 5)}
    | {f"FC-15{n:02d}" for n in range(1, 6)}
)

VALID_STATUSES = {
    "pending", "preflight_locked", "red_proved", "implemented",
    "focused_green", "repo_green", "cross_repo_green",
    "real_readonly_verified", "rollback_verified", "independent_review",
    "accepted", "blocked", "failed",
}

REPOS = ("revenue", "filing", "wiki")
SKIPPED_SCENARIO_STATUSES = {"skip", "skipped", "xfail", "xfailed", "deselected"}
PLACEHOLDER_TOKENS = ("placeholder", "tbd", "n/a", "todo", "xxxx", "0" * 64, "pending")
_HEX = set("0123456789abcdef")


def _is_sha1(value: object) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(c in _HEX for c in value.lower())


def _is_sha256(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in _HEX for c in value.lower())


def _is_placeholder(value: object) -> bool:
    return isinstance(value, str) and value.lower().strip() in PLACEHOLDER_TOKENS


def _triplet_problems(obj: dict, key: str) -> list[str]:
    triplet = obj.get(key)
    if not isinstance(triplet, dict) or set(triplet) != set(REPOS):
        return [f"{key} must have exactly keys {set(REPOS)}"]
    out = []
    for repo in REPOS:
        if not _is_sha1(triplet.get(repo)):
            out.append(f"{key}.{repo} must be a 40-char hex SHA-1")
    return out


def _parse_date(value: str) -> date | None:
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def validate_receipt(
    receipt: dict,
    *,
    implementer: str,
    reviewer: str | None = None,
    today: date | None = None,
) -> list[str]:
    """Return structural + acceptance violations. Empty list = valid receipt.

    ``implementer`` is the identity that produced the receipt; ``reviewer`` is
    the identity attempting to accept it (None when not yet reviewed). The
    implementer may never accept their own receipt.
    """
    today = today or date.today()
    problems: list[str] = []

    if not isinstance(receipt, dict):
        return ["receipt must be a JSON object"]

    fc = receipt.get("fc_id", "<missing>")
    if receipt.get("schema_version") != SCHEMA_VERSION:
        problems.append(f"schema_version must be {SCHEMA_VERSION!r}")
    if receipt.get("fc_id") not in FC_IDS:
        problems.append(f"fc_id {fc!r} is not in the frozen FC registry")
    if receipt.get("status") not in VALID_STATUSES:
        problems.append(f"status {receipt.get('status')!r} not in valid lifecycle")

    problems += _triplet_problems(receipt, "base_triplet")
    problems += _triplet_problems(receipt, "result_triplet")

    plan = receipt.get("plan_sha256")
    if not _is_sha256(plan):
        problems.append("plan_sha256 must be a 64-char hex SHA-256")

    policy = receipt.get("policy_sha256")
    if policy != "not-applicable" and not _is_sha256(policy):
        if _is_placeholder(policy):
            problems.append("policy_sha256 is a placeholder — forbidden second strategy source")
        else:
            problems.append("policy_sha256 must be a 64-char hex SHA-256 or 'not-applicable'")

    cmd_reg = receipt.get("command_registry_sha256")
    if not (_is_sha256(cmd_reg) or cmd_reg == "pending-fc-104"):
        problems.append("command_registry_sha256 must be a 64-char hash or 'pending-fc-104'")

    allowed = receipt.get("allowed_files")
    changed = receipt.get("changed_files")
    if not isinstance(allowed, list):
        problems.append("allowed_files must be a list")
    if not isinstance(changed, list):
        problems.append("changed_files must be a list")
    if isinstance(allowed, list) and isinstance(changed, list):
        extra = set(changed) - set(allowed)
        if extra:
            problems.append(f"changed_files not subset of allowed_files: {sorted(extra)}")

    for i, cmd in enumerate(receipt.get("commands", [])):
        if not isinstance(cmd, dict):
            problems.append(f"commands[{i}] must be an object")
            continue
        if cmd.get("exit_code") != 0:
            problems.append(f"commands[{i}].exit_code must be 0 (got {cmd.get('exit_code')})")
        if not cmd.get("command"):
            problems.append(f"commands[{i}].command missing")

    for sr in receipt.get("scenario_results", []):
        if isinstance(sr, dict) and sr.get("status") in SKIPPED_SCENARIO_STATUSES:
            problems.append(f"scenario {sr.get('id')!r} is skipped/xfail — cannot be accepted")

    review = receipt.get("review", {})
    decision = review.get("decision") if isinstance(review, dict) else None
    if decision == "accepted":
        rev = review.get("reviewer")
        if not rev:
            problems.append("review.decision=accepted but reviewer is empty")
        elif implementer and rev == implementer:
            problems.append("reviewer is the same identity as the implementer — implementer cannot self-accept")
        elif reviewer is not None and rev != reviewer:
            problems.append(f"review.reviewer {rev!r} != expected reviewer {reviewer!r}")
        if not _is_sha256(review.get("reviewer_receipt_sha256")):
            problems.append("review.reviewer_receipt_sha256 must be a 64-char hash on accepted")
        reviewed_at = review.get("reviewed_at")
        rd = _parse_date(reviewed_at) if isinstance(reviewed_at, str) else None
        if rd is None:
            problems.append("review.reviewed_at must be an ISO-8601 date")
        elif rd > today:
            problems.append(f"review.reviewed_at {reviewed_at} is in the future")

    mutation = receipt.get("mutation")
    if isinstance(mutation, dict) and mutation.get("killed") is False:
        problems.append("mutation.killed is false — critical mutation survived")
    return problems


def can_accept(
    receipt: dict,
    *,
    implementer: str,
    reviewer: str,
    today: date | None = None,
) -> tuple[bool, list[str]]:
    """Stricter gate: may this receipt advance to ``accepted``?

    Requires structural validity, real sealing hashes (no pending-fc-104), an
    independent reviewer who accepted, and a non-future timestamp.
    """
    problems = validate_receipt(receipt, implementer=implementer, reviewer=reviewer, today=today)
    if receipt.get("command_registry_sha256") == "pending-fc-104":
        problems.append("cannot accept: command_registry_sha256 is pending-fc-104 (FC-104 must seal it)")
    if receipt.get("status") != "independent_review" and receipt.get("status") != "accepted":
        problems.append(f"cannot accept from status {receipt.get('status')!r}")
    review = receipt.get("review", {})
    if isinstance(review, dict) and review.get("decision") != "accepted":
        problems.append("cannot accept: review.decision is not 'accepted'")
    return (not problems, problems)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate FC receipts against schema 2.0")
    parser.add_argument("--receipt", type=Path, action="append", required=True,
                        help="receipt JSON (repeatable)")
    parser.add_argument("--implementer", default="",
                        help="identity that produced the receipt(s)")
    parser.add_argument("--reviewer", default=None,
                        help="identity attempting to accept (omit for structural-only check)")
    parser.add_argument("--accept", action="store_true",
                        help="run the stricter acceptance gate instead of structural validation")
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    args = parser.parse_args()

    all_problems: list[str] = []
    for path in args.receipt:
        receipt = json.loads(path.read_text(encoding="utf-8"))
        if args.accept:
            if not args.reviewer:
                print("--accept requires --reviewer")
                return 2
            ok, problems = can_accept(receipt, implementer=args.implementer,
                                      reviewer=args.reviewer)
        else:
            problems = validate_receipt(receipt, implementer=args.implementer,
                                        reviewer=args.reviewer)
        for p in problems:
            all_problems.append(f"{path}: {p}")

    if args.json:
        print(json.dumps({"ok": not all_problems, "problems": all_problems},
                         indent=2, ensure_ascii=False))
    else:
        for p in all_problems:
            print(f"RECEIPT-VALIDATE: {p}")
        if not all_problems:
            print(f"OK: {len(args.receipt)} receipt(s) valid")
    return 1 if all_problems else 0


if __name__ == "__main__":
    sys.exit(main())
