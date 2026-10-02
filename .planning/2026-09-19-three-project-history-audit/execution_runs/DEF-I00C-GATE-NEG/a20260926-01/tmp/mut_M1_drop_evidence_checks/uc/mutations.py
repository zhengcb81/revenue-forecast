"""Critical mutation suite (CA-108).

Each mutation builds a VALID fixture, applies one targeted defect IN PLACE,
and must turn the corresponding verifier RED.  The suite reports
total/killed/alive; the acceptance criterion is kill=100%.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from uc.closure import classify_unit
from uc.ledger import append_entry, read_ledger, verify_summary
from uc.receipt import canonical_hash, sign, validate as receipt_validate
from uc.revision import select as revision_select
from uc.scenarios import NEW_MATRIX, OLD_MATRIX, build as scenarios_build
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
    make_valid: Callable[[Path], Path]
    mutate: Callable[[Path], None]
    check: Callable[[Path], list[str]]
    expect: str


def _write(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _implementer(**overrides) -> dict:
    payload = {
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
    payload.update(overrides)
    return payload


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


def _unit_fixture(tmp: Path, name: str) -> Path:
    unit = tmp / name
    unit.mkdir(parents=True, exist_ok=True)
    impl = sign(_implementer())
    _write(unit / "11_implementer_receipt.json", impl)
    _write(unit / "12_reviewer_receipt.json", sign(_reviewer(canonical_hash(impl))))
    return unit


def _receipt_check(unit: Path) -> list[str]:
    return receipt_validate(unit / "11_implementer_receipt.json", REPO_ROOTS)


def _reviewer_check(unit: Path) -> list[str]:
    return receipt_validate(unit / "12_reviewer_receipt.json", REPO_ROOTS)


def _pair_check(unit: Path) -> list[str]:
    _, problems = revision_select(unit)
    return problems


def _state_fixture(tmp: Path, name: str) -> Path:
    path = tmp / f"{name}.json"
    _write(
        path,
        {
            "units": {
                "D-0": {"status": "accepted"},
                "X-1": {"status": "pending", "implementer": "impl"},
            }
        },
    )
    return path


def _state_check(state_path: Path) -> list[str]:
    state = _read(state_path)
    return validate_transition("X-1", state, "accepted", deps=["D-0"], reviewer="rev-B")


def _ledger_fixture(tmp: Path, name: str) -> Path:
    ledger = tmp / f"{name}.jsonl"
    for _ in range(3):
        append_entry(ledger, "parser_call", "parser", {})
    return ledger


def _ledger_check(ledger: Path, declared: dict) -> list[str]:
    return verify_summary(read_ledger(ledger), declared)


def _scenario_repo(tmp: Path, name: str) -> Path:
    repo = tmp / name
    for rel in (OLD_MATRIX, NEW_MATRIX):
        dest = repo / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOTS["revenue"] / rel, dest)
    return repo


def _scenario_check(repo: Path, registry: Path) -> list[str]:
    return scenarios_verify(repo, registry)


def _closure_check(unit: Path) -> list[str]:
    verdict = classify_unit(unit.parent, unit.name)
    return verdict["problems"]


def mutations() -> list[Mutation]:
    def m(name: str, make_valid, mutate, check, expect: str) -> Mutation:
        return Mutation(name, make_valid, mutate, check, expect)

    def replace_impl(unit: Path, transform) -> None:
        impl = transform(_implementer())
        _write(unit / "11_implementer_receipt.json", impl)

    def replace_review(unit: Path, transform) -> None:
        impl = sign(_implementer())
        _write(unit / "12_reviewer_receipt.json", transform(impl))

    suite: list[Mutation] = []
    # --- receipt.validate (8) ---
    suite.append(
        m(
            "receipt-tamper",
            lambda t: _unit_fixture(t, "receipt-tamper"),
            lambda u: replace_impl(u, lambda d: {**d, "implementer": "impl-X"}),
            _receipt_check,
            "canonical_hash",
        )
    )
    suite.append(
        m(
            "receipt-unsigned",
            lambda t: _unit_fixture(t, "receipt-unsigned"),
            lambda u: replace_impl(u, lambda d: d),
            _receipt_check,
            "missing canonical_hash",
        )
    )
    suite.append(
        m(
            "receipt-bad-version",
            lambda t: _unit_fixture(t, "receipt-bad-version"),
            lambda u: replace_impl(u, lambda d: {**d, "schema_version": 99}),
            _receipt_check,
            "schema_version",
        )
    )
    suite.append(
        m(
            "receipt-empty-commands",
            lambda t: _unit_fixture(t, "receipt-empty-commands"),
            lambda u: replace_impl(u, lambda d: {**d, "commands": []}),
            _receipt_check,
            "commands",
        )
    )
    suite.append(
        m(
            "receipt-missing-touched",
            lambda t: _unit_fixture(t, "receipt-missing-touched"),
            lambda u: replace_impl(
                u, lambda d: {k: v for k, v in d.items() if k != "touched_files"}
            ),
            _receipt_check,
            "touched_files",
        )
    )
    suite.append(
        m(
            "receipt-policy-placeholder",
            lambda t: _unit_fixture(t, "receipt-policy-placeholder"),
            lambda u: replace_impl(
                u, lambda d: {**d, "policy_sha256": "not-applicable"}
            ),
            _receipt_check,
            "policy_sha256",
        )
    )
    suite.append(
        m(
            "receipt-fake-triplet",
            lambda t: _unit_fixture(t, "receipt-fake-triplet"),
            lambda u: replace_impl(
                u, lambda d: {**d, "result_triplet": {"revenue": "f" * 40}}
            ),
            _receipt_check,
            "not a real git object",
        )
    )
    suite.append(
        m(
            "receipt-bad-verdict",
            lambda t: _unit_fixture(t, "receipt-bad-verdict"),
            lambda u: replace_review(
                u, lambda impl: {**_reviewer(canonical_hash(impl)), "verdict": "maybe"}
            ),
            _reviewer_check,
            "verdict",
        )
    )
    # --- revision pairing (7) ---
    suite.append(
        m(
            "revision-stale-review",
            lambda t: _unit_fixture(t, "revision-stale-review"),
            lambda u: replace_review(u, lambda impl: _reviewer("a" * 64)),
            _pair_check,
            "no reviewer receipt references the latest",
        )
    )
    suite.append(
        m(
            "revision-self-review",
            lambda t: _unit_fixture(t, "revision-self-review"),
            lambda u: replace_review(
                u, lambda impl: _reviewer(canonical_hash(impl), reviewer="impl-A")
            ),
            _pair_check,
            "reviewer identity equals implementer",
        )
    )
    suite.append(
        m(
            "revision-p1-no-successor",
            lambda t: _unit_fixture(t, "revision-p1-no-successor"),
            lambda u: replace_review(
                u,
                lambda impl: _reviewer(
                    canonical_hash(impl),
                    findings=[{"id": "F1", "severity": "P1", "summary": "x"}],
                ),
            ),
            _pair_check,
            "unclosed P1",
        )
    )
    suite.append(
        m(
            "revision-fork",
            lambda t: _fork(t),
            lambda u: None,
            _pair_check,
            "fork",
        )
    )
    suite.append(
        m(
            "revision-unknown-supersedes",
            lambda t: _unknown_supersedes(t),
            lambda u: None,
            _pair_check,
            "supersedes unknown",
        )
    )
    suite.append(
        m(
            "revision-duplicate",
            lambda t: _duplicate(t),
            lambda u: None,
            _pair_check,
            "duplicate revision",
        )
    )
    suite.append(
        m(
            "revision-missing-reviewer",
            lambda t: _unit_fixture(t, "revision-missing-reviewer"),
            lambda u: (u / "12_reviewer_receipt.json").unlink(),
            _pair_check,
            "no reviewer receipt",
        )
    )
    # --- strict state machine (7) ---
    suite.append(
        m(
            "state-pending-to-accepted",
            lambda t: _state_fixture(t, "state-pending"),
            lambda s: None,
            _state_check,
            "illegal transition",
        )
    )
    suite.append(
        m(
            "state-dep-gate",
            lambda t: _state_fixture(t, "state-dep"),
            lambda s: _mutate_state(
                s, lambda p: p["units"]["D-0"].update({"status": "pending"})
            ),
            _state_check,
            "dependencies unsatisfied",
        )
    )
    suite.append(
        m(
            "state-reviewer-self",
            lambda t: _state_fixture(t, "state-self"),
            lambda s: _mutate_state(
                s, lambda p: p["units"]["X-1"].update({"status": "independent_review"})
            ),
            lambda s: validate_transition(
                "X-1", _read(s), "accepted", deps=["D-0"], reviewer="impl"
            ),
            "reviewer must differ",
        )
    )
    suite.append(
        m(
            "state-reviewer-missing",
            lambda t: _state_fixture(t, "state-norev"),
            lambda s: _mutate_state(
                s, lambda p: p["units"]["X-1"].update({"status": "independent_review"})
            ),
            lambda s: validate_transition(
                "X-1", _read(s), "accepted", deps=["D-0"], reviewer=None
            ),
            "reviewer identity",
        )
    )
    suite.append(
        m(
            "state-bad-current",
            lambda t: _state_fixture(t, "state-bad"),
            lambda s: _mutate_state(
                s, lambda p: p["units"]["X-1"].update({"status": "in-limbo"})
            ),
            _state_check,
            "current state not in enum",
        )
    )
    suite.append(
        m(
            "state-accepted-terminal",
            lambda t: _state_fixture(t, "state-terminal"),
            lambda s: _mutate_state(
                s, lambda p: p["units"]["X-1"].update({"status": "accepted"})
            ),
            _state_check,
            "illegal transition",
        )
    )
    suite.append(
        m(
            "state-unknown-target",
            lambda t: _state_fixture(t, "state-unknown"),
            lambda s: None,
            lambda s: validate_transition(
                "X-1", _read(s), "accepted_today", deps=["D-0"]
            ),
            "unknown state",
        )
    )
    # --- ledger (3) ---
    suite.append(
        m(
            "ledger-overreport",
            lambda t: _ledger_fixture(t, "ledger-over"),
            lambda ledger_path: None,
            lambda ledger_path: _ledger_check(ledger_path, {"parser_call": 9}),
            "declared parser_call=9",
        )
    )
    suite.append(
        m(
            "ledger-underreport",
            lambda t: _ledger_fixture(t, "ledger-under"),
            lambda ledger_path: None,
            lambda ledger_path: _ledger_check(ledger_path, {"parser_call": 0}),
            "declared parser_call=0",
        )
    )
    suite.append(
        m(
            "ledger-unclaimed",
            lambda t: _ledger_fixture(t, "ledger-unclaimed"),
            lambda ledger_path: None,
            lambda ledger_path: _ledger_check(ledger_path, {}),
            "unclaimed parser_call",
        )
    )
    # --- scenario registry (3) ---
    suite.append(
        m(
            "scenario-source-drift",
            lambda t: _scenario_fixture(t, "scenario-src"),
            lambda pair: _tamper(pair[0] / NEW_MATRIX, "# drift\n"),
            lambda pair: _scenario_check(pair[0], pair[1]),
            "source drift",
        )
    )
    suite.append(
        m(
            "scenario-set-drift",
            lambda t: _scenario_fixture(t, "scenario-set"),
            lambda pair: _mutate_json(
                pair[1],
                lambda p: p["scenarios"].update(
                    {"FAKE-01": {"status": "pending", "source": "old95"}}
                ),
            ),
            lambda pair: _scenario_check(pair[0], pair[1]),
            "scenario set differs",
        )
    )
    suite.append(
        m(
            "scenario-count-drift",
            lambda t: _scenario_fixture(t, "scenario-count"),
            lambda pair: _mutate_json(
                pair[1], lambda p: p["counts"].update({"new102": 101})
            ),
            lambda pair: _scenario_check(pair[0], pair[1]),
            "counts drifted",
        )
    )
    # --- closure (2) ---
    suite.append(
        m(
            "closure-missing-reviewer",
            lambda t: _unit_fixture(t, "closure-norev"),
            lambda u: (u / "12_reviewer_receipt.json").unlink(),
            _closure_check,
            "no reviewer receipt",
        )
    )
    suite.append(
        m(
            "closure-tampered-verdict",
            lambda t: _unit_fixture(t, "closure-tamper"),
            _tamper_verdict,
            _closure_check,
            "canonical_hash mismatch",
        )
    )
    return suite


def _tamper_verdict(unit: Path) -> None:
    """Byte-level tamper of the SIGNED reviewer receipt: the verdict text
    swaps, so the canonical hash no longer recomputes."""
    path = unit / "12_reviewer_receipt.json"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace('"accepted"', '"maybe"', 1), encoding="utf-8")


def _fork(tmp: Path) -> Path:
    unit = tmp / "fork"
    unit.mkdir(parents=True, exist_ok=True)
    r1 = sign(_implementer(revision="r1"))
    r2a = sign(_implementer(revision="r2a", supersedes="r1"))
    r2b = sign(_implementer(revision="r2b", supersedes="r1"))
    _write(unit / "11_r1.json", r1)
    _write(unit / "11_r2a.json", r2a)
    _write(unit / "11_r2b.json", r2b)
    _write(unit / "12_reviewer_receipt.json", sign(_reviewer(canonical_hash(r2a))))
    return unit


def _unknown_supersedes(tmp: Path) -> Path:
    unit = tmp / "unknown-sup"
    unit.mkdir(parents=True, exist_ok=True)
    r2 = sign(_implementer(revision="r2", supersedes="r0-missing"))
    _write(unit / "11_r2.json", r2)
    _write(unit / "12_reviewer_receipt.json", sign(_reviewer(canonical_hash(r2))))
    return unit


def _duplicate(tmp: Path) -> Path:
    unit = tmp / "dup"
    unit.mkdir(parents=True, exist_ok=True)
    r1 = sign(_implementer())
    _write(unit / "11_r1.json", r1)
    _write(unit / "11_r1_dup.json", r1)
    _write(unit / "12_reviewer_receipt.json", sign(_reviewer(canonical_hash(r1))))
    return unit


def _mutate_state(path: Path, transform) -> None:
    payload = _read(path)
    transform(payload)
    _write(path, payload)


def _mutate_json(path: Path, transform) -> None:
    payload = _read(path)
    transform(payload)
    _write(path, payload)


def _tamper(path: Path, suffix: str) -> None:
    path.write_text(path.read_text(encoding="utf-8") + suffix, encoding="utf-8")


def _scenario_fixture(tmp: Path, name: str) -> tuple[Path, Path]:
    repo = _scenario_repo(tmp, f"{name}-repo")
    registry = tmp / f"{name}-registry.json"
    scenarios_build(repo, registry)
    return repo, registry


def run_suite(tmp: Path) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for mutation in mutations():
        try:
            fixture_dir = tmp / mutation.name.replace(" ", "_")
            fixture_dir.mkdir(parents=True, exist_ok=True)
            fixture = mutation.make_valid(fixture_dir)
            if mutation.mutate is not None:
                mutation.mutate(fixture)
            problems = mutation.check(fixture)
            killed = any(mutation.expect in p for p in problems)
            results.append(
                {
                    "name": mutation.name,
                    "killed": killed,
                    "problems": problems[:2] if not killed else [],
                }
            )
        except Exception as exc:
            results.append(
                {"name": mutation.name, "killed": False, "problems": [repr(exc)]}
            )
    total = len(results)
    killed_count = sum(1 for r in results if r["killed"])
    alive = [r for r in results if not r["killed"]]
    return {
        "total": total,
        "killed": killed_count,
        "alive": alive,
        "results": results,
    }
