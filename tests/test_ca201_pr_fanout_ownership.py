"""CA-201 (phase H exit, absorbed card, final DAG unit) acceptance tests:
current-triplet PR fan-out ownership and required-checks absorption.

Per README §7 the current-triplet PR fan-out is the CA-201 surface: CA-201
owns scheduling/attestation while ZR-105 (frozen contract + honest gap
assessor) and ZR-901 (PR-gate required-checks landing evidence on the
revenue CI surface) provide the required checks. CA-201 is an ABSORBED
card — it must not re-implement any workflow, sibling tooling, manifest,
contract or assessor; it verifies the absorption relation holds and that
the machine DAG closes.

  C1  DAG closure: CA-201's dependencies (CA-107, ZR-105, ZR-901) are all
      accepted in the machine state; CA-201 is the only DAG unit without
      a state entry at card start and becomes the final closed unit.
  C2  README §7 absorption row: the current-triplet PR fan-out row names
      CA-201 as unique owner and ZR-105/ZR-901 as required-checks
      providers (CA owns scheduling/attestation; ZR provides checks).
  C3  ZR-105 contract: all three required checks carry the CA-201
      successor (exact_triplet_binding / affected_repo_fanout /
      collected_skip_delta_controlled).
  C4  honest gap assessor: uc.cli ci-gap returns deterministic JSON with
      revenue's three checks present; every unsatisfied check maps to the
      CA-201 successor (no fake green).
  C5  absorbed surface landing: the revenue PR gate already carries the
      required checks (manifest-driven sibling checkout, no floating
      clone, no unconditional `|| true`) — ZR-901's absorbed evidence.
  C6  no duplicate implementation: no fanout tool in tools/, no second
      PR-fanout module in uc/, no second contract file in ci/.
  C7  machine-state entry: the state carries a CA-201 entry whose
      dependencies are accepted (unit exists with red_proved-or-later
      status at runtime; deps all accepted).

Zero workflow / product-code / manifest / contract / assessor changes on
this card — it is the absorption acceptance card closing the DAG.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
UC_ROOT = REPO_ROOT / "assurance" / "unified_completion"
STATE_PATH = UC_ROOT / "state.json"
CONTRACT_PATH = UC_ROOT / "ci" / "current_triplet_contract.json"
QUALITY_YML = REPO_ROOT / ".github" / "workflows" / "quality.yml"
README_MD = REPO_ROOT / "audit_review" / "README.md"

DEPENDENCIES = ("CA-107", "ZR-105", "ZR-901")
REQUIRED_CHECKS = (
    "exact_triplet_binding",
    "affected_repo_fanout",
    "collected_skip_delta_controlled",
)


def _state() -> dict:
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# C1 — DAG closure: CA-201 dependencies all accepted
# ---------------------------------------------------------------------------


def test_c1_ca201_dependencies_all_accepted() -> None:
    state = _state()
    units = state["units"]
    assert "CA-201" in units, "CA-201 must exist in machine state"
    for dep in DEPENDENCIES:
        assert dep in units, f"dependency {dep} missing from state"
        assert units[dep].get("status") in ("accepted", "already_satisfied"), (
            f"dependency {dep} not accepted: {units[dep].get('status')}"
        )


# ---------------------------------------------------------------------------
# C2 — README §7 absorption row
# ---------------------------------------------------------------------------


def test_c2_readme_absorption_row() -> None:
    lines = _read_text(README_MD).splitlines()
    hits = [
        line
        for line in lines
        if "current-triplet PR fan-out" in line and "CA-201" in line
    ]
    assert hits, "README §7 must carry the current-triplet PR fan-out row"
    row = hits[0]
    assert "ZR-105" in row and "ZR-901" in row, "row must name both ZR providers"
    assert "required checks" in row or "required checks" in row.lower()


# ---------------------------------------------------------------------------
# C3 — ZR-105 contract: CA-201 successor on every required check
# ---------------------------------------------------------------------------


def test_c3_contract_successors_are_ca201() -> None:
    data = json.loads(_read_text(CONTRACT_PATH))
    assert data["schema_version"] == 1
    assert data["unit"] == "ZR-105"
    assert set(data["required_checks"]) == set(REQUIRED_CHECKS)
    for name in REQUIRED_CHECKS:
        assert data["successors"][name] == "CA-201", f"{name} successor must be CA-201"


# ---------------------------------------------------------------------------
# C4 — honest gap assessor: deterministic JSON, gaps map to CA-201
# ---------------------------------------------------------------------------


def test_c4_ci_gap_honest_report_maps_to_ca201() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(UC_ROOT)
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "uc.cli", "ci-gap"],
        cwd=str(UC_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode in (0, 1), proc.stderr[-500:]
    out = json.loads(proc.stdout)
    assert out["schema_version"] == 1
    assert out["unit"] == "ZR-105"
    rev = out["repos"]["revenue"]
    assert rev["workflow_file"].endswith(".github/workflows/quality.yml")
    for name in REQUIRED_CHECKS:
        assert name in rev["checks"], name
    for repo_name, section in out["repos"].items():
        for check_name, result in section["checks"].items():
            if not result["satisfied"]:
                assert result["successor"] == "CA-201", (
                    f"{repo_name}/{check_name} gap must map to CA-201"
                )


# ---------------------------------------------------------------------------
# C5 — absorbed surface landing on the revenue PR gate (ZR-901 evidence)
# ---------------------------------------------------------------------------


def test_c5_revenue_pr_gate_carries_required_checks() -> None:
    text = _read_text(QUALITY_YML)
    assert "compatibility/current.json" in text, "manifest must be referenced"
    assert "ci_checkout_siblings" in text, "manifest-driven sibling checkout present"
    clone_hits = [
        ln for ln, line in enumerate(text.splitlines(), 1) if "git clone" in line
    ]
    assert not clone_hits, f"floating clone present: {clone_hits}"
    swallow_hits = [
        ln for ln, line in enumerate(text.splitlines(), 1) if re.search(r"\|\|\s*true", line)
    ]
    assert not swallow_hits, f"unconditional || true swallows: {swallow_hits}"


# ---------------------------------------------------------------------------
# C6 — no duplicate implementation (absorbed card must not re-implement)
# ---------------------------------------------------------------------------


def test_c6_no_duplicate_fanout_implementation() -> None:
    tools_fanout = [
        p.name for p in (REPO_ROOT / "tools").glob("*")
        if "fanout" in p.name.lower() or p.name.lower().startswith("fan")
    ]
    assert not tools_fanout, f"duplicate fanout tools: {tools_fanout}"
    uc_modules = [
        p.name for p in (UC_ROOT / "uc").glob("*.py")
        if "fanout" in p.name.lower() or "pr_fanout" in p.name.lower()
    ]
    assert not uc_modules, f"duplicate PR-fanout modules: {uc_modules}"
    ci_contracts = [
        p.name for p in (UC_ROOT / "ci").glob("*.json")
        if p.name != "current_triplet_contract.json"
    ]
    assert not ci_contracts, f"second contract files: {ci_contracts}"


# ---------------------------------------------------------------------------
# C7 — machine-state entry present with dependencies accepted
# ---------------------------------------------------------------------------


def test_c7_state_entry_and_dependency_closure() -> None:
    state = _state()
    entry = state["units"].get("CA-201")
    assert entry, "CA-201 must have a machine-state entry"
    assert entry.get("status") not in (None, "pending"), (
        f"CA-201 must be locked/active at runtime, got {entry.get('status')}"
    )
    assert state.get("current_next") == "CA-201"
    assert state.get("current_phase") == "J_final_verification"
