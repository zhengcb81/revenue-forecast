"""ZR-105 (phase C exit) gate tests: current-triplet CI required-checks
contract and honest gap assessor.

The contract freezes what a current-triplet CI gate MUST enforce; the
fan-out implementation belongs to CA-201, so these tests pin:

(a) contract schema/immutability (fixed frozen_at, exact triplet);
(b) workflow-file hash binding;
(c) evaluator determinism;
(d) negative fixtures per check (stale manifest, floating clone, single-repo
    trigger, silent `|| true` skip swallow → gap; compliant fixtures → green);
(e) the REAL three workflows evaluated honestly — the current state is
    expected to carry gaps, each mapping to the CA-201 successor.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from uc.ci_contract import (
    REPOS,
    REPO_ROOT,
    WORKFLOW_RELS,
    assess,
    evaluate,
    load_contract,
)

FROZEN_TRIPLET = {
    "revenue": "19cb45aed2807374abf3de783b709f403bf51a27",
    "filing": "83c638e76e40890262746cdf02b6df495dcb4031",
    "wiki": "b6617553b6cb787e8b59dbb2dac51d0570ee4ddc",
}


def _sha256_bytes(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def _repo_workflow_bytes(repo_name: str) -> bytes:
    return (REPOS[repo_name] / WORKFLOW_RELS[repo_name]).read_bytes()


# ---------------------------------------------------------------------------
# (a) contract schema and immutability
# ---------------------------------------------------------------------------


def test_contract_schema_valid() -> None:
    data = load_contract()
    assert data["schema_version"] == 1
    assert data["unit"] == "ZR-105"
    assert data["frozen_at"] == "2026-08-14T00:00:00+00:00"
    assert data["triplet"] == FROZEN_TRIPLET
    for name in (
        "exact_triplet_binding",
        "affected_repo_fanout",
        "collected_skip_delta_controlled",
    ):
        assert name in data["required_checks"], name
        assert data["successors"][name] == "CA-201", name


# ---------------------------------------------------------------------------
# (b) workflow-file hash binding
# ---------------------------------------------------------------------------


def test_workflow_files_match_frozen_hashes() -> None:
    data = load_contract()
    for repo_name, spec in data["workflow_files"].items():
        current = _sha256_bytes(_repo_workflow_bytes(repo_name))
        assert current == spec["sha256"], (
            f"{repo_name} workflow changed since freeze: {current} != {spec['sha256']}"
        )


# ---------------------------------------------------------------------------
# (c) evaluator determinism
# ---------------------------------------------------------------------------


def test_evaluator_is_deterministic() -> None:
    first = assess()
    second = assess()
    stripped_first = {k: v for k, v in first.items() if k != "evaluated_at_utc"}
    stripped_second = {k: v for k, v in second.items() if k != "evaluated_at_utc"}
    assert stripped_first == stripped_second


# ---------------------------------------------------------------------------
# (d) negative/positive fixtures per check
# ---------------------------------------------------------------------------


def _fixture_contract(tmp_path: Path, overrides: dict | None = None) -> dict:
    data = load_contract()
    if overrides:
        data.update(overrides)
    return data


def test_stale_manifest_is_a_gap(tmp_path: Path) -> None:
    # A revenue-style workflow with a stale manifest triplet must be a gap.
    contract = _fixture_contract(tmp_path)
    contract["triplet"] = dict(FROZEN_TRIPLET, revenue="0" * 40)
    report = evaluate(REPO_ROOT, contract)
    check = report["repos"]["revenue"]["checks"]["exact_triplet_binding"]
    assert not check["satisfied"]
    assert check["successor"] == "CA-201"


def test_floating_clone_is_a_gap(tmp_path: Path) -> None:
    # filing workflow contains a git clone with no pinned sha -> gap.
    report = evaluate(REPO_ROOT, load_contract())
    filing_check = report["repos"]["filing"]["checks"]["exact_triplet_binding"]
    # Ground truth today: filing clones a remote without a pinned sha.
    assert not filing_check["satisfied"]
    assert any("floating" in line for line in filing_check["evidence"])


def test_fanout_markers_green_vs_gap(tmp_path: Path) -> None:
    from uc.ci_contract import _check_affected_repo_fanout

    contract = load_contract()
    gap = _check_affected_repo_fanout("on:\n  push:\n  pull_request:\n", contract)
    assert not gap["satisfied"]
    green = _check_affected_repo_fanout(
        "on:\n  repository_dispatch:\n    types: [sibling-pushed]\n", contract
    )
    assert green["satisfied"]


def test_true_swallow_is_a_skip_delta_gap(tmp_path: Path) -> None:
    from uc.ci_contract import _check_collected_skip_delta

    contract = load_contract()
    gap = _check_collected_skip_delta("run: pytest tests -q || true\n", contract)
    assert not gap["satisfied"]
    assert any("|| true" in line for line in gap["evidence"])
    green = _check_collected_skip_delta(
        "run: pytest tests -q --collect-only > collected.txt\n"
        "run: python tools/compare_skip_delta.py collected.txt baseline.json\n",
        contract,
    )
    assert green["satisfied"]


# ---------------------------------------------------------------------------
# (e) the REAL workflows are evaluated honestly (gaps expected today)
# ---------------------------------------------------------------------------


def test_real_workflows_have_honest_gap_report() -> None:
    report = assess()
    assert report["schema_version"] == 1
    assert report["successor"] == "CA-201"
    # Ground truth at the frozen triplet: every check is a gap (the fan-out
    # implementation is CA-201's phase-H job).  The evaluator must say so
    # honestly instead of rubber-stamping green.
    assert len(report["gaps"]) == 9, report["gaps"]
    for repo_name in ("revenue", "filing", "wiki"):
        for check_name, result in report["repos"][repo_name]["checks"].items():
            assert result["successor"] == "CA-201"
            assert result["evidence"], check_name
    drift = report["workflow_drift"]
    for repo_name in ("revenue", "filing", "wiki"):
        assert drift[repo_name]["unchanged"] is True, repo_name


def test_cli_gap_reports_json_and_exits_1() -> None:
    import os

    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONPATH"] = str(REPO_ROOT / "assurance" / "unified_completion")
    completed = subprocess.run(
        [sys.executable, "-B", "-m", "uc.cli", "ci-gap"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        check=False,
        timeout=120,
    )
    assert completed.returncode == 1, "current state must exit 1 (gaps exist)"
    payload = json.loads(completed.stdout)
    assert payload["unit"] == "ZR-105"
    assert payload["gaps"], "report must list the honest gaps"
