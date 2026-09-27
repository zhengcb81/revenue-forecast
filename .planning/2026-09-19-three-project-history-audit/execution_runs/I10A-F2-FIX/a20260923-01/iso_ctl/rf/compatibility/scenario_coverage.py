"""FC-1003: machine coverage gate for the 95 mandatory scenarios.

Coverage evidence (union):
  1. test-file docstrings carrying ``SCENARIO: EX-01 EX-02 ...`` markers
     (a marker may be composite like ``LT-09/DL-04`` — split on ``/``);
  2. FC receipts' ``scenario_results`` ids across the three repos.

Scope filter: a scenario is REQUIRED only when its declared tier's
``owner_fc`` belongs to an already-accepted FC (or is itself the current
phase's).  Scenarios owned by future phases (AUD->FC-1105, UJ->FC-1503,
IDX->FC-1004, PORT->FC-1205/1004) are exempt from THIS gate and reported
separately as deferred — never silently dropped.

Exit code: 0 when every required scenario is covered; 1 with the gap list
otherwise.  Runs from the revenue repo root; sibling repos are located via
``../company-wiki`` and ``../filing-fetch``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCENARIO_RE = re.compile(r"^(EX|DBX|DL|LT|AR|SAFE|CTRL|OPS|PORT|IDX|UJ|AUD|MIG)-\d+$")
MARKER_RE = re.compile(r"SCENARIO:\s*([^\n]+)")
ROOT = Path(__file__).resolve().parents[1]
SIBLINGS = (ROOT, ROOT.parent / "company-wiki", ROOT.parent / "filing-fetch")

# owner_fc prefixes that are deferred (not gaps of THIS gate):
# Phase 11 (FC-110x), Phase 12 (FC-120x), Phase 13 (FC-130x), Phase 15 (FC-150x),
# and FC-1004 (platform/install shape — its PORT-02 etc. ship with FC-1004).
# Everything else (incl. UJ->FC-1003, IDX->FC-303, AUD-07->FC-103) is required.
_DEFERRED_FC = ("FC-110", "FC-120", "FC-130", "FC-150", "FC-1004")


def _split_id(raw: str) -> set[str]:
    out = set()
    for token in re.split(r"[\s,;]+", raw.strip()):
        for part in token.split("/"):
            part = part.strip()
            if SCENARIO_RE.match(part):
                out.add(part)
    return out


def collect_test_markers() -> set[str]:
    """SCENARIO markers from all test files under the three repos.

    FC-1003 F2: a marked file MUST parse — a marker in a non-compiling file
    would prop the gate with un-runnable coverage.  Parse failures raise.
    """
    import ast

    found: set[str] = set()
    for root in SIBLINGS:
        dirs = [(root / "tests"), (root / "tools" / "tests")]
        for d in dirs:
            if not d.is_dir():
                continue
            for path in d.rglob("test_*.py"):
                try:
                    text = path.read_text(encoding="utf-8")
                    ast.parse(text)
                except (OSError, UnicodeDecodeError):
                    continue
                except SyntaxError as exc:
                    raise SystemExit(
                        f"F2: marked test file does not parse: {path} — {exc}"
                    ) from exc
                for m in MARKER_RE.finditer(text):
                    found |= _split_id(m.group(1))
    return found


def collect_receipt_ids() -> set[str]:
    """scenario_results ids from all implementer+reviewer receipts."""
    found: set[str] = set()
    for root in SIBLINGS:
        for path in (root / "assurance" / "fc").glob("FC-*/1[12]_*.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            for sr in payload.get("scenario_results") or []:
                sid = str(sr.get("id") or "")
                if "/" in sid:
                    found |= _split_id(sid)
                elif SCENARIO_RE.match(sid):
                    found.add(sid)
    return found


def load_registry() -> dict:
    return json.loads((ROOT / "compatibility" / "scenario_registry.json").read_text(
        encoding="utf-8"))


def accepted_fcs() -> set[str]:
    """FCs with an accepted reviewer receipt (scanned, no registry write)."""
    accepted: set[str] = set()
    for root in SIBLINGS:
        for path in (root / "assurance" / "fc").glob("FC-*/12_*.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if payload.get("verdict") == "accepted" or (
                isinstance(payload.get("review"), dict)
                and payload["review"].get("decision") == "accepted"
            ):
                accepted.add(str(payload.get("fc_id") or ""))
    return {f for f in accepted if f}


def coverage_report() -> dict:
    registry = load_registry()
    markers = collect_test_markers()
    receipts = collect_receipt_ids()
    covered = markers | receipts

    required_gaps: list[str] = []
    deferred: list[str] = []
    matrix: dict[str, dict] = {}
    for scenario in registry["scenarios"]:
        sid = scenario["id"]
        owners = {
            t.get("owner_fc", "") for t in scenario.get("tier_entries", {}).values()
        }
        # required = has an owner AND no owner is future-phase (AUD/UJ/IDX/PORT
        # owners are deferred to their phases; everything else must be covered
        # by markers or receipts NOW)
        required = bool(owners) and not any(
            owner.startswith(_DEFERRED_FC) for owner in owners)
        matrix[sid] = {
            "owners": sorted(owners),
            "covered_by": sorted(c for c in ("markers", "receipts")
                                 if (c == "markers" and sid in markers)
                                 or (c == "receipts" and sid in receipts)),
        }
        if any(owner.startswith(_DEFERRED_FC) for owner in owners):
            deferred.append(sid)
        if required and sid not in covered:
            required_gaps.append(sid)

    return {
        "total_mandatory": registry["total_mandatory"],
        "covered": sorted(covered),
        "required_gaps": sorted(required_gaps),
        "deferred_future_phase": sorted(set(deferred)),
        "matrix": matrix,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="machine-readable report")
    args = parser.parse_args(argv)
    report = coverage_report()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"mandatory: {report['total_mandatory']} | covered: {len(report['covered'])}")
        print(f"required gaps: {len(report['required_gaps'])}")
        for sid in report["required_gaps"]:
            print(f"  MISSING {sid}")
        print(f"deferred (future phase): {len(report['deferred_future_phase'])}")
        for sid in report["deferred_future_phase"]:
            print(f"  deferred {sid}")
    return 1 if report["required_gaps"] else 0


if __name__ == "__main__":
    sys.exit(main())
