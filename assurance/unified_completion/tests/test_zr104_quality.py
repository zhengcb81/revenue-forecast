"""ZR-104 (phase C) gate tests: three-repo quality baseline ratchet.

Covers the ZR-104 acceptance gates:

(a) a tampered baseline (coverage lowered, allowlist grown, complexity
    raised) is REJECTED by :func:`uc.quality.verify`;
(b) an improved baseline (coverage raised, complexity lowered, allowlist
    shrunk) verifies green;
(c) baseline recomputation is deterministic — two freezes are identical and
    reproduce the committed baseline;
(d) the critical-function complexity gate
    :func:`uc.quality.check_critical_complexity` flags functions above the
    frozen max (AST McCabe, no third-party deps) on synthetic functions;
(e) public contracts are strict-typed: every file in the frozen revenue
    strict-mypy set exists, and top-level functions in ``scripts/contracts``
    carry parameter and return annotations (generator functions, whose
    return type mypy infers, are exempt — the repo's CI mypy command passes
    0 errors on the whole strict set).

Ratchet semantics under test: the frozen baseline must *match-or-improve*
the recomputed state — the frozen value must be at least as strict as the
value recomputed from the repos and the toolchain today.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

from uc.quality import (
    MAX_CRITICAL_COMPLEXITY,
    check_critical_complexity,
    compute_baseline,
    freeze,
    verify,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
QUALITY_PATH = Path(__file__).resolve().parents[1] / "quality" / "quality_baseline.json"

FROZEN_TRIPLET = {
    "revenue": "313638b25c9dd109af442b666765f4340de2fb8b",
    "filing": "83c638e76e40890262746cdf02b6df495dcb4031",
    "wiki": "b6617553b6cb787e8b59dbb2dac51d0570ee4ddc",
}


def _load_baseline() -> dict:
    return json.loads(QUALITY_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# (a) tampered baseline is rejected
# ---------------------------------------------------------------------------


def test_tampered_baseline_is_rejected():
    frozen = _load_baseline()
    # coverage lowered (84.0 -> 80.0)
    frozen["repos"]["revenue"]["coverage"]["total_floor"] -= 4.0
    # allowlist grown (a new file joins the frozen set)
    frozen["repos"]["wiki"]["hardcoding"]["allowlist"] = sorted(
        frozen["repos"]["wiki"]["hardcoding"]["allowlist"] + ["new_owner.py"]
    )
    # complexity raised (acquisition.py frozen max 26 -> 99)
    frozen["repos"]["wiki"]["complexity"]["frozen_max"]["acquisition.py"] = 99
    problems = verify(REPO_ROOT, frozen)
    assert problems, "tampered baseline must be rejected"
    joined = "\n".join(problems)
    assert "revenue/coverage" in joined, joined
    assert "wiki/hardcoding" in joined, joined
    assert "wiki/complexity" in joined, joined


# ---------------------------------------------------------------------------
# (b) improved baseline verifies green
# ---------------------------------------------------------------------------


def test_improved_baseline_verifies_green():
    frozen = _load_baseline()
    # coverage raised
    frozen["repos"]["revenue"]["coverage"]["total_floor"] += 5.0
    frozen["repos"]["filing"]["coverage"]["total_floor"] += 1.0
    frozen["repos"]["wiki"]["coverage"]["floors"]["policy.py"] = 99
    # complexity lowered
    frozen["repos"]["wiki"]["complexity"]["frozen_max"]["acquisition.py"] = 10
    # allowlist shrunk
    frozen["repos"]["wiki"]["hardcoding"]["allowlist"].remove("cli.py")
    problems = verify(REPO_ROOT, frozen)
    assert problems == [], f"improved baseline must verify green: {problems}"


# ---------------------------------------------------------------------------
# (c) baseline recomputation determinism
# ---------------------------------------------------------------------------


def test_two_freezes_are_identical(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    freeze(REPO_ROOT, first)
    freeze(REPO_ROOT, second)
    assert first.read_bytes() == second.read_bytes(), (
        "two freezes of the same state must be byte-identical"
    )
    payload = json.loads(first.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["unit"] == "ZR-104"
    assert payload["triplet"] == FROZEN_TRIPLET
    committed = _load_baseline()
    assert payload == committed, (
        "recomputed baseline drifted from the committed baseline"
    )


def test_committed_baseline_verifies_green():
    problems = verify(REPO_ROOT, _load_baseline())
    assert problems == [], f"committed baseline must verify green: {problems}"


# ---------------------------------------------------------------------------
# (d) new/changed critical functions complexity gate
# ---------------------------------------------------------------------------


def _branchy_function(name: str, branches: int) -> str:
    lines = [f"def {name}(x: int) -> int:"]
    for i in range(branches):
        lines.append(f"    if x == {i}:")
        lines.append("        x += 1")
    lines.append("    return x")
    return "\n".join(lines)


def test_check_critical_complexity_flags_over_max():
    simple = "def f(a: int, b: int) -> int:\n    return a + b\n"
    assert check_critical_complexity(simple) == []
    # 9 branches -> complexity 10 == max: green
    assert check_critical_complexity(_branchy_function("at_limit", 9)) == []
    # 10 branches -> complexity 11 > 10: flagged
    violations = check_critical_complexity(_branchy_function("over_limit", 10))
    assert violations, "complexity 11 must exceed the frozen max 10"
    assert any("over_limit" in v for v in violations)
    # methods are critical functions too
    classy = (
        "class Worker:\n"
        "    def run(self, x: int) -> int:\n"
        + "".join(f"        if x == {i}:\n            x += 1\n" for i in range(11))
        + "        return x\n"
    )
    violations = check_critical_complexity(classy)
    assert violations and any("run" in v for v in violations)
    # custom threshold and unparseable input
    assert (
        check_critical_complexity(_branchy_function("x", 12), max_complexity=20) == []
    )
    assert check_critical_complexity("def broken(:\n")


def test_check_critical_complexity_matches_frozen_constant():
    assert MAX_CRITICAL_COMPLEXITY == 10


# ---------------------------------------------------------------------------
# (e) public contracts strict type (frozen revenue strict set)
# ---------------------------------------------------------------------------


def _is_generator(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Generators (incl. @contextmanager) get their return type inferred by
    mypy, so an explicit return annotation is not required there."""
    return any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(fn))


def test_public_contracts_strict_type_annotations():
    targets = _load_baseline()["repos"]["revenue"]["types"]["strict_mypy_targets"]
    assert targets, "frozen revenue strict-mypy target set must not be empty"
    for rel in targets:
        assert (REPO_ROOT / rel).is_file(), f"frozen strict target missing: {rel}"
    contract_files = sorted(
        rel for rel in targets if rel.startswith("scripts/contracts/")
    )
    assert contract_files, "scripts/contracts/* must be in the strict set"
    for rel in contract_files:
        tree = ast.parse((REPO_ROOT / rel).read_text(encoding="utf-8"))
        for fn in tree.body:
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if fn.name.startswith("test_"):
                continue
            args = [
                a
                for a in (
                    list(fn.args.posonlyargs)
                    + list(fn.args.args)
                    + list(fn.args.kwonlyargs)
                )
                if a.arg not in ("self", "cls")
            ]
            if fn.args.vararg is not None:
                args.append(fn.args.vararg)
            if fn.args.kwarg is not None:
                args.append(fn.args.kwarg)
            missing = [a.arg for a in args if a.annotation is None]
            assert not missing, (
                f"{rel}:{fn.name} missing parameter annotations: {missing}"
            )
            if not _is_generator(fn):
                assert fn.returns is not None, (
                    f"{rel}:{fn.name} missing return annotation"
                )


def test_compute_baseline_is_machine_computed():
    """No hand-written values: recomputation equals the committed baseline
    and every dimension carries the machine provenance it was derived from."""
    payload = compute_baseline(REPO_ROOT)
    assert payload == _load_baseline()
    for repo_name in ("revenue", "filing", "wiki"):
        section = payload["repos"][repo_name]
        assert section["types"]["strict_mypy_targets"]
        assert section["coverage"]
        assert section["complexity"]
        assert "frozen_tokens" in section["hardcoding"]
    assert payload["dead_callers"]["input_hash"]
