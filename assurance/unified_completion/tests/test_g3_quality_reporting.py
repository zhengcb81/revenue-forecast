"""G3-RF-ASSURANCE: the quality layer reports; it no longer gates on numbers.

Covered here (each item maps to the G3 card's RED list):

  * the RF type target set follows the CURRENT mypy entry — the CI workflow
    delegates to ``tools/pre_push_gate.py`` and the resolver follows that
    delegation instead of looking for an inline ``python -m mypy`` line that
    no longer exists in the workflow;
  * a sibling repository that is not present is reported as
    ``not_available`` + scope — never as a fabricated zero set, never by
    silently copying revenue's target set;
  * the retired coverage gate (fail_under 84 -> 0, PER_MODULE_MINIMUM eight
    floors -> {}) is a *diagnostic* and no longer blocks verification;
  * an invalid baseline payload (schema/unit) is still a failure;
  * a real process that exits 2 without ever printing ``FAILED`` is judged
    failed from its exit code, not from its text.

Determinism and the frozen import API of ``uc.quality`` stay intact.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from uc.quality import (
    MAX_CRITICAL_COMPLEXITY,
    compute_baseline,
    freeze,
    product_tree_sha,
    strict_targets,
    verify,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
QUALITY_PATH = Path(__file__).resolve().parents[1] / "quality" / "quality_baseline.json"


def _load_baseline() -> dict:
    return json.loads(QUALITY_PATH.read_text(encoding="utf-8"))


def _build_report(root: Path, frozen: dict) -> dict:
    """Deferred import: the G3 report helper is part of this card's delivery."""
    from uc.quality_report import build_report

    return build_report(root, frozen)


def _make_rf_repo(tmp_path: Path) -> Path:
    """Minimal revenue repo whose CI workflow DELEGATES the type check to
    ``tools/pre_push_gate.py`` — the shape the real workflow has today."""
    root = tmp_path / "revenue-forecast"

    contracts = root / "scripts" / "contracts"
    contracts.mkdir(parents=True)
    (contracts / "__init__.py").write_text("", encoding="utf-8")
    (contracts / "value.py").write_text(
        "def value(x: int) -> int:\n    return x\n", encoding="utf-8"
    )
    (root / "scripts" / "schema_compatibility.py").write_text("", encoding="utf-8")
    (root / "scripts" / "filing_fetch_client.py").write_text("", encoding="utf-8")
    (root / "scripts" / "trust_anchor.py").write_text("", encoding="utf-8")

    workflow = root / ".github" / "workflows"
    workflow.mkdir(parents=True)
    (workflow / "quality.yml").write_text(
        "name: quality\n"
        "jobs:\n"
        "  verify:\n"
        "    steps:\n"
        "      - run: python tools/pre_push_gate.py\n",
        encoding="utf-8",
    )

    tools = root / "tools"
    tools.mkdir()
    (tools / "pre_push_gate.py").write_text(
        "import sys\n"
        "gates = (\n"
        '    ([sys.executable, "-m", "mypy", "scripts/contracts/",'
        ' "scripts/schema_compatibility.py"], "public contract types"),\n'
        ")\n",
        encoding="utf-8",
    )
    (tools / "run_coverage_gates.py").write_text(
        "# Historical report decoder (AST-read by uc.quality._revenue_coverage).\n"
        "PER_MODULE_MINIMUM = {}\n",
        encoding="utf-8",
    )

    (root / ".coveragerc").write_text("[report]\nfail_under = 0\n", encoding="utf-8")

    gate_test = root / "tests" / "test_fc1101_ci_manifest.py"
    gate_test.parent.mkdir(parents=True)
    gate_test.write_text(
        'import re\n\nSHA1 = re.compile(r"[0-9a-f]{40}")\n', encoding="utf-8"
    )
    return root


# ---------------------------------------------------------------------------
# 1. RF type targets follow the current (delegated) mypy entry
# ---------------------------------------------------------------------------


def test_revenue_type_targets_follow_current_mypy_entry():
    workflow = (REPO_ROOT / ".github" / "workflows" / "quality.yml").read_text(
        encoding="utf-8"
    )
    gate = (REPO_ROOT / "tools" / "pre_push_gate.py").read_text(encoding="utf-8")

    # the workflow delegates; it carries no inline mypy line any more
    assert "python -m mypy" not in workflow
    assert "python tools/pre_push_gate.py" in workflow
    # the delegated entry really is the RF type definition
    for token in (
        "scripts/contracts/",
        "scripts/schema_compatibility.py",
        "scripts/filing_fetch_client.py",
        "scripts/trust_anchor.py",
    ):
        assert token in gate

    expected = sorted(
        {
            path.relative_to(REPO_ROOT).as_posix()
            for path in (REPO_ROOT / "scripts" / "contracts").rglob("*.py")
        }
        | {
            "scripts/schema_compatibility.py",
            "scripts/filing_fetch_client.py",
            "scripts/trust_anchor.py",
        }
    )
    assert strict_targets("revenue", REPO_ROOT) == expected


def test_scratch_workflow_delegation_resolves_type_targets(tmp_path):
    root = _make_rf_repo(tmp_path)
    assert strict_targets("revenue", root) == [
        "scripts/contracts/__init__.py",
        "scripts/contracts/value.py",
        "scripts/schema_compatibility.py",
    ]


# ---------------------------------------------------------------------------
# 2. sibling repository absent -> not_available + scope (never 0, never copied)
# ---------------------------------------------------------------------------


def test_sibling_repo_absent_reports_not_available_with_scope(tmp_path):
    root = _make_rf_repo(tmp_path)
    baseline = compute_baseline(root)

    for name in ("filing", "wiki"):
        types = baseline["repos"][name]["types"]
        assert types["status"] == "not_available", types
        assert types["strict_mypy_targets"] == []
        assert types["scope"]
        # a product subtree that cannot be resolved is None, with the scope
        # that explains it kept alongside
        assert baseline["product_trees"][name] is None
        assert baseline["product_tree_scopes"][name]
        for dimension in ("coverage", "complexity", "hardcoding"):
            section = baseline["repos"][name][dimension]
            assert section["status"] == "not_available", (name, dimension, section)
            assert section["scope"]

    # never an implicit copy of the revenue set, never an invented number
    revenue_targets = baseline["repos"]["revenue"]["types"]["strict_mypy_targets"]
    assert revenue_targets
    assert baseline["repos"]["filing"]["types"]["strict_mypy_targets"] != (
        revenue_targets
    )
    assert baseline["repos"]["wiki"]["coverage"] != {"total_floor": 0}


def test_revenue_dimension_is_computed_in_scratch_repo(tmp_path):
    root = _make_rf_repo(tmp_path)
    baseline = compute_baseline(root)
    revenue = baseline["repos"]["revenue"]
    assert revenue["types"]["status"] != "not_available"
    assert revenue["types"]["strict_mypy_targets"]
    assert revenue["coverage"]["total_floor"] == 0.0
    assert revenue["hardcoding"]["scan"]["name"] == "fc1101_workflow_sha_pins"
    assert baseline["dead_callers"]["input_hash"]
    assert baseline["schema_version"] == 1
    assert baseline["unit"] == "ZR-104"


# ---------------------------------------------------------------------------
# 3. retired engineering thresholds are diagnostics, not qualification gates
# ---------------------------------------------------------------------------


def test_retired_coverage_gate_no_longer_blocks_verify():
    """G2 retired the coverage gate (fail_under 0 / PER_MODULE_MINIMUM {});
    the old ratchet layer must not turn that retirement into a failure."""
    assert verify(REPO_ROOT, _load_baseline()) == []


def test_retired_coverage_gate_is_reported_as_diagnostic():
    report = _build_report(REPO_ROOT, _load_baseline())
    assert report["failures"] == []
    joined = "\n".join(report["diagnostics"])
    assert "revenue/coverage" in joined, joined
    # the frozen floors are still visible — as history, not as a gate
    assert "scripts/revenue_core.py" in joined


def test_numeric_ratchet_change_is_diagnostic_not_failure():
    frozen = _load_baseline()
    frozen["repos"]["revenue"]["coverage"]["total_floor"] -= 4.0
    report = _build_report(REPO_ROOT, frozen)
    assert report["failures"] == []
    joined = "\n".join(report["diagnostics"])
    assert "revenue/coverage" in joined, joined


def test_invalid_baseline_payload_is_still_a_failure():
    for bad in (
        {"schema_version": 99, "unit": "ZR-104"},
        {"schema_version": 1, "unit": "OTHER-UNIT"},
    ):
        report = _build_report(REPO_ROOT, bad)
        assert report["failures"], bad
        assert report["failures"] != report["diagnostics"]


# ---------------------------------------------------------------------------
# 4. a real process is judged by its exit code, never by a FAILED keyword
# ---------------------------------------------------------------------------


def test_probe_failure_is_judged_by_exit_code_not_text():
    from uc.quality_report import run_probe

    result = run_probe([sys.executable, "-c", "print('quietly'); raise SystemExit(2)"])
    assert result["returncode"] == 2
    assert result["ok"] is False
    assert "FAILED" not in result["output"]

    green = run_probe([sys.executable, "-c", "print('ok')"])
    assert green["returncode"] == 0
    assert green["ok"] is True


# ---------------------------------------------------------------------------
# 5. frozen API / determinism / complexity gate stay intact
# ---------------------------------------------------------------------------


def test_two_freezes_stay_deterministic(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    freeze(REPO_ROOT, first)
    freeze(REPO_ROOT, second)
    assert first.read_bytes() == second.read_bytes()
    payload = json.loads(first.read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["unit"] == "ZR-104"
    assert payload["product_trees"]["revenue"] == product_tree_sha(REPO_ROOT, "scripts")
    committed = _load_baseline()
    assert (
        payload["repos"]["revenue"]["types"]["strict_mypy_targets"]
        == (committed["repos"]["revenue"]["types"]["strict_mypy_targets"])
    )


def test_committed_baseline_has_no_failures():
    report = _build_report(REPO_ROOT, _load_baseline())
    assert report["failures"] == [], report["failures"]


def test_check_critical_complexity_gate_unchanged():
    assert MAX_CRITICAL_COMPLEXITY == 10
    from uc.quality import check_critical_complexity

    assert check_critical_complexity("def f(a: int) -> int:\n    return a\n") == []


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
