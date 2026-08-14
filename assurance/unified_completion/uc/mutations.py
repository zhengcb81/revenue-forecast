"""Critical mutation suite (CA-108).

Each mutation takes a VALID fixture, applies one targeted defect, and must
turn the corresponding verifier RED.  The suite reports total/killed/alive;
the acceptance criterion is kill=100%.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from uc.closure import classify_unit
from uc.ledger import verify_summary
from uc.receipt import canonical_hash, sign, validate as receipt_validate
from uc.revision import select as revision_select
from uc.scenarios import verify as scenarios_verify
from uc.strict_state import validate_transition

REPO_ROOTS = {
    "revenue": Path(__file__).resolve().parents[3],
    "filing": Path(__file__).resolve().parents[3].parent / "filing-fetch",
    "wiki": Path(__file__).resolve().parents[3].parent / "company-wiki",
}


@dataclass
class Mutation:
    name: str
    make_valid: Callable[[Path], None]
    mutate: Callable[[Path], None]
    check: Callable[[Path], list[str]]
    expect: str


def _implementer() -> dict:
    return {
        "schema_version": 1,
        "unit": "CA-M",
        "kind": "implementer",
        "created_at_utc": "2026-08-14T00:00:00Z",
        "revision": "r1",
        "implementer": "impl-A",
        "base_triplet": {"revenue": "0" * 40},
        "result_triplet": {"revenue": "0" * 40},
        "plan_sha256": "a" * 64,
        "commands": [{"command": "pytest", "exit_code": 0}],
        "touched_files": ["x.py"],
        "side_effect_counts": {"downloads": 0},
    }


def _reviewer(target_hash: str, **overrides) -> dict:
    payload = {
        "schema_version": 1,
        "unit": "CA-M",
        "kind": "reviewer",
        "created_at_utc": "2026-08-14T00:00:00Z",
        "reviewer": "rev-B",
        "verdict": "accepted",
        "reviewed_object_sha256": target_hash,
        "commands": [{"command": "pytest", "exit_code": 0}],
        "findings": [],
    }
    payload.update(overrides)
    return payload


def _write(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _receipt_fixture(tmp: Path, include_reviewer: bool = True) -> Path:
    unit = tmp / "unit"
    unit.mkdir(parents=True, exist_ok=True)
    impl = sign(_implementer())
    _write(unit / "11_implementer_receipt.json", impl)
    if include_reviewer:
        _write(
            unit / "12_reviewer_receipt.json",
            sign(_reviewer(canonical_hash(impl))),
        )
    return unit


def _state_fixture(tmp: Path) -> Path:
    state = tmp / "state.json"
    _write(
        state,
        {
            "units": {
                "D-0": {"status": "accepted"},
                "X-1": {"status": "pending", "implementer": "impl"},
            }
        },
    )
    return state


def _ledger_fixture(tmp: Path) -> tuple[Path, list]:
    from uc.ledger import append_entry

    ledger = tmp / "ledger.jsonl"
    for _ in range(3):
        append_entry(ledger, "parser_call", "parser", {})
    return ledger, ["parser_call"] * 3


def _scenario_fixture(tmp: Path) -> Path:
    registry = tmp / "scenarios.json"
    _write(
        registry,
        {
            "schema_version": 1,
            "sources": {"old95": "s" * 64, "new102": "n" * 64},
            "counts": {"old95": 95, "new102": 102, "unique_total": 197},
            "scenarios": {"AR-01": {"status": "pending", "source": "old95"}},
        },
    )
    return registry


def _receipt_problems(path: Path) -> list[str]:
    return receipt_validate(path, REPO_ROOTS)


def _revision_problems(unit: Path) -> list[str]:
    _, problems = revision_select(unit)
    return problems


def _state_problems(state_path: Path) -> list[str]:
    state = _read(state_path)
    return validate_transition(
        "X-1", state, "accepted", deps=["D-0"], reviewer="rev-B"
    )


def _closure_problems(unit: Path) -> list[str]:
    verdict = classify_unit(unit, "unit")
    return verdict["problems"]


def _scenario_problems(registry: Path, repo: Path) -> list[str]:
    return scenarios_verify(repo, registry)


def _ledger_problems(fixture: tuple[Path, list], declared: dict) -> list[str]:
    from uc.ledger import read_ledger

    return verify_summary(read_ledger(fixture[0]), declared)


def _state_read_write(tmp: Path, transform: Callable[[dict], None]) -> None:
    path = tmp / "state.json"
    payload = _read(path)
    transform(payload)
    _write(path, payload)


# ---- mutations ----

def mutations() -> list[Mutation]:
    return [
        # receipt.validate (10)
        Mutation("receipt-tamper", _receipt_fixture,
                 lambda tmp: _write(_receipt_fixture(tmp) / "11_implementer_receipt.json",
                                    {**_implementer(), "implementer": "impl-X"}),
                 lambda tmp: _receipt_problems(_receipt_fixture(tmp) / "11_implementer_receipt.json"),
                 "canonical_hash"),
        Mutation("receipt-unsigned",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: _write(_receipt_fixture(tmp) / "11_implementer_receipt.json", _implementer()),
                 lambda tmp: _receipt_problems(_receipt_fixture(tmp) / "11_implementer_receipt.json"),
                 "missing canonical_hash"),
        Mutation("receipt-bad-version",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: _write(_receipt_fixture(tmp) / "11_implementer_receipt.json",
                                    {**_implementer(), "schema_version": 99}),
                 lambda tmp: _receipt_problems(_receipt_fixture(tmp) / "11_implementer_receipt.json"),
                 "schema_version"),
        Mutation("receipt-empty-commands",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: _write(_receipt_fixture(tmp) / "11_implementer_receipt.json",
                                    {**_implementer(), "commands": []}),
                 lambda tmp: _receipt_problems(_receipt_fixture(tmp) / "11_implementer_receipt.json"),
                 "commands"),
        Mutation("receipt-missing-touched",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: _write(_receipt_fixture(tmp) / "11_implementer_receipt.json",
                                    {k: v for k, v in _implementer().items() if k != "touched_files"}),
                 lambda tmp: _receipt_problems(_receipt_fixture(tmp) / "11_implementer_receipt.json"),
                 "touched_files"),
        Mutation("receipt-policy-placeholder",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: _write(_receipt_fixture(tmp) / "11_implementer_receipt.json",
                                    {**_implementer(), "policy_sha256": "not-applicable"}),
                 lambda tmp: _receipt_problems(_receipt_fixture(tmp) / "11_implementer_receipt.json"),
                 "policy_sha256"),
        Mutation("receipt-fake-triplet",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: _write(_receipt_fixture(tmp) / "11_implementer_receipt.json",
                                    {**_implementer(), "result_triplet": {"revenue": "f" * 40}}),
                 lambda tmp: _receipt_problems(_receipt_fixture(tmp) / "11_implementer_receipt.json"),
                 "not a real git object"),
        Mutation("receipt-bad-verdict",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: _write(_receipt_fixture(tmp) / "12_reviewer_receipt.json",
                                    {**_reviewer("0" * 64), "verdict": "maybe"}),
                 lambda tmp: _receipt_problems(_receipt_fixture(tmp) / "12_reviewer_receipt.json"),
                 "verdict"),
        # revision pairing (7)
        Mutation("revision-stale-review",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: _write(_receipt_fixture(tmp) / "12_reviewer_receipt.json",
                                    sign(_reviewer("a" * 64))),
                 lambda tmp: _revision_problems(_receipt_fixture(tmp)),
                 "no reviewer receipt references the latest"),
        Mutation("revision-self-review",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: _write(_receipt_fixture(tmp) / "12_reviewer_receipt.json",
                                    sign(_reviewer(canonical_hash(sign(_implementer())), reviewer="impl-A"))),
                 lambda tmp: _revision_problems(_receipt_fixture(tmp)),
                 "reviewer identity equals implementer"),
        Mutation("revision-p1-no-successor",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: _write(_receipt_fixture(tmp) / "12_reviewer_receipt.json",
                                    sign(_reviewer(canonical_hash(sign(_implementer())),
                                                   findings=[{"id": "F1", "severity": "P1", "summary": "x"}]))),
                 lambda tmp: _revision_problems(_receipt_fixture(tmp)),
                 "unclosed P1"),
        Mutation("revision-fork",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: None,
                 lambda tmp: _revision_problems(_fork_fixture(tmp)),
                 "fork"),
        Mutation("revision-unknown-supersedes",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: None,
                 lambda tmp: _revision_problems(_unknown_supersedes_fixture(tmp)),
                 "supersedes unknown"),
        Mutation("revision-duplicate",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: None,
                 lambda tmp: _revision_problems(_duplicate_fixture(tmp)),
                 "duplicate revision"),
        Mutation("revision-missing-reviewer",
                 lambda tmp: _receipt_fixture(tmp, include_reviewer=False),
                 lambda tmp: None,
                 lambda tmp: _revision_problems(_receipt_fixture(tmp, include_reviewer=False)),
                 "no reviewer receipt"),
        # strict state machine (7)
        Mutation("state-pending-to-accepted",
                 lambda tmp: _state_fixture(tmp),
                 lambda tmp: None,
                 lambda tmp: _state_problems(_state_fixture(tmp)),
                 "illegal transition"),
        Mutation("state-unknown-status",
                 lambda tmp: _state_fixture(tmp),
                 lambda tmp: _state_read_write(tmp, lambda s: s["units"].update({"X-2": {"status": "accepted_today"}})),
                 lambda tmp: _state_problems2(_state_fixture(tmp)),
                 "unknown state"),
        Mutation("state-dep-gate",
                 lambda tmp: _state_fixture(tmp),
                 lambda tmp: _state_read_write(tmp, lambda s: s["units"]["D-0"].update({"status": "pending"})),
                 lambda tmp: _state_problems(_state_fixture(tmp)),
                 "dependencies unsatisfied"),
        Mutation("state-reviewer-self",
                 lambda tmp: _state_fixture(tmp),
                 lambda tmp: _state_read_write(tmp, lambda s: s["units"]["X-1"].update({"status": "independent_review"})),
                 lambda tmp: _state_problems_self(_state_fixture(tmp)),
                 "reviewer must differ"),
        Mutation("state-reviewer-missing",
                 lambda tmp: _state_fixture(tmp),
                 lambda tmp: _state_read_write(tmp, lambda s: s["units"]["X-1"].update({"status": "independent_review"})),
                 lambda tmp: _state_problems_norev(_state_fixture(tmp)),
                 "reviewer identity"),
        Mutation("state-bad-current-state",
                 lambda tmp: _state_fixture(tmp),
                 lambda tmp: _state_read_write(tmp, lambda s: s["units"]["X-1"].update({"status": "in-limbo"})),
                 lambda tmp: _state_problems(_state_fixture(tmp)),
                 "current state not in enum"),
        Mutation("state-accepted-terminal",
                 lambda tmp: _state_fixture(tmp),
                 lambda tmp: _state_read_write(tmp, lambda s: s["units"]["X-1"].update({"status": "accepted"})),
                 lambda tmp: _state_problems(_state_fixture(tmp)),
                 "illegal transition"),
        # ledger (3)
        Mutation("ledger-overreport",
                 lambda tmp: _ledger_fixture(tmp),
                 lambda tmp: None,
                 lambda tmp: _ledger_problems(_ledger_fixture(tmp), {"parser_call": 9}),
                 "declared parser_call=9"),
        Mutation("ledger-underreport",
                 lambda tmp: _ledger_fixture(tmp),
                 lambda tmp: None,
                 lambda tmp: _ledger_problems(_ledger_fixture(tmp), {"parser_call": 0}),
                 "declared parser_call=0"),
        Mutation("ledger-unclaimed",
                 lambda tmp: _ledger_fixture(tmp),
                 lambda tmp: None,
                 lambda tmp: _ledger_problems(_ledger_fixture(tmp), {}),
                 "unclaimed parser_call"),
        # scenario registry (3)
        Mutation("scenario-source-drift",
                 lambda tmp: _scenario_fixture(tmp),
                 lambda tmp: None,
                 lambda tmp: _scenario_problems(_scenario_fixture(tmp), Path(__file__).resolve().parents[3]),
                 "source drift"),
        Mutation("scenario-set-drift",
                 lambda tmp: _scenario_fixture(tmp),
                 lambda tmp: None,
                 lambda tmp: _scenario_problems(_scenario_set_drift(tmp), Path(__file__).resolve().parents[3]),
                 "scenario set differs"),
        Mutation("scenario-count-mismatch",
                 lambda tmp: _scenario_fixture(tmp),
                 lambda tmp: None,
                 lambda tmp: _scenario_problems(_scenario_count_drift(tmp), Path(__file__).resolve().parents[3]),
                 "counts drifted"),
        # closure (3)
        Mutation("closure-missing-reviewer",
                 lambda tmp: _receipt_fixture(tmp, include_reviewer=False),
                 lambda tmp: None,
                 lambda tmp: _closure_problems(_receipt_fixture(tmp, include_reviewer=False)),
                 "no reviewer receipt"),
        Mutation("closure-tampered-verdict",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: None,
                 lambda tmp: _closure_problems(_tampered_unit(tmp)),
                 "canonical_hash mismatch"),
        Mutation("closure-legacy-clean",
                 lambda tmp: _receipt_fixture(tmp),
                 lambda tmp: None,
                 lambda tmp: [p for p in _closure_problems(_legacy_unit(tmp))],
                 ""),
    ]


# ---- fixture builders for mutation-time construction ----

def _fork_fixture(tmp: Path) -> Path:
    unit = tmp / "fork"
    unit.mkdir(parents=True, exist_ok=True)
    r1 = sign({**_implementer(), "revision": "r1"})
    r2a = sign({**_implementer(), "revision": "r2a", "supersedes": "r1"})
    r2b = sign({**_implementer(), "revision": "r2b", "supersedes": "r1"})
    _write(unit / "11_r1.json", r1)
    _write(unit / "11_r2a.json", r2a)
    _write(unit / "11_r2b.json", r2b)
    _write(unit / "12_reviewer_receipt.json", sign(_reviewer(canonical_hash(r2a))))
    return unit


def _unknown_supersedes_fixture(tmp: Path) -> Path:
    unit = tmp / "unknown"
    unit.mkdir(parents=True, exist_ok=True)
    r2 = sign({**_implementer(), "revision": "r2", "supersedes": "r0-missing"})
    _write(unit / "11_r2.json", r2)
    _write(unit / "12_reviewer_receipt.json", sign(_reviewer(canonical_hash(r2))))
    return unit


def _duplicate_fixture(tmp: Path) -> Path:
    unit = tmp / "dup"
    unit.mkdir(parents=True, exist_ok=True)
    r1 = sign(_implementer())
    _write(unit / "11_r1.json", r1)
    _write(unit / "11_r1_dup.json", r1)
    _write(unit / "12_reviewer_receipt.json", sign(_reviewer(canonical_hash(r1))))
    return unit


def _tampered_unit(tmp: Path) -> Path:
    unit = tmp / "tampered"
    unit.mkdir(parents=True, exist_ok=True)
    impl = sign(_implementer())
    review = _reviewer(canonical_hash(impl))
    review["verdict"] = "maybe"
    _write(unit / "11_implementer_receipt.json", impl)
    _write(unit / "12_reviewer_receipt.json", review)
    return unit


def _legacy_unit(tmp: Path) -> Path:
    unit = tmp / "legacy"
    unit.mkdir(parents=True, exist_ok=True)
    _write(unit / "11_implementer_receipt.json", {"fc_id": "FC-903", "status": "accepted"})
    return unit


def _state_problems2(state_path: Path) -> list[str]:
    state = _read(state_path)
    return validate_transition(
        "X-2", state, "accepted", deps=[], reviewer="rev-B"
    )


def _state_problems_self(state_path: Path) -> list[str]:
    state = _read(state_path)
    return validate_transition(
        "X-1", state, "accepted", deps=["D-0"], reviewer="impl"
    )


def _state_problems_norev(state_path: Path) -> list[str]:
    state = _read(state_path)
    return validate_transition("X-1", state, "accepted", deps=["D-0"], reviewer=None)


def _scenario_set_drift(tmp: Path) -> Path:
    registry = tmp / "scenarios.json"
    payload = _read(registry)
    payload["scenarios"]["FAKE-01"] = {"status": "pending", "source": "old95"}
    _write(registry, payload)
    return registry


def _scenario_count_drift(tmp: Path) -> Path:
    registry = tmp / "scenarios.json"
    payload = _read(registry)
    payload["counts"]["new102"] = 101
    _write(registry, payload)
    return registry


def run_suite(tmp: Path) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for mutation in mutations():
        try:
            unit_tmp = tmp / mutation.name.replace(" ", "_")
            unit_tmp.mkdir(parents=True, exist_ok=True)
            mutation.make_valid(unit_tmp)
            if mutation.mutate is not None:
                mutation.mutate(unit_tmp)
            problems = mutation.check(unit_tmp)
            killed = any(mutation.expect in p for p in problems)
            results.append(
                {
                    "name": mutation.name,
                    "killed": killed,
                    "problems": problems[:2] if not killed else [],
                }
            )
        except Exception as exc:  # a crashing verifier still fails the check
            results.append(
                {"name": mutation.name, "killed": False, "problems": [repr(exc)]}
            )
    total = len(results)
    killed = sum(1 for r in results if r["killed"])
    alive = [r for r in results if not r["killed"]]
    return {"total": total, "killed": killed, "alive": alive, "results": results}
