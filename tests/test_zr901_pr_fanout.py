"""ZR-901 (phase J exit, absorbed card) gate tests: current-triplet PR gate
required-checks landing evidence on the revenue CI surface.

Per README §7 the current-triplet PR fan-out is owned by CA-201
(scheduling/attestation) and absorbed from ZR-105 (frozen contract + honest
gap assessor) and ZR-901 (this card: the PR-gate required-checks evidence).
ZR-105 froze what a current-triplet CI gate MUST enforce; this card pins
that the revenue PR surface actually carries the required checks landing
evidence:

(a) quality.yml references the manifest-driven sibling checkout
    (compatibility/current.json + tools/ci_checkout_siblings.py);
(b) quality.yml has no floating `git clone` and no unconditional `|| true`
    swallow;
(c) tools/ci_checkout_siblings.py is driven only by the manifest
    current_triplet (no hardcoded pin) and its CLI runs;
(d) the manifest triplets (frozen baseline + current) are well-formed and
    the revenue legs resolve in this repo's object store;
(e) the ZR-105 contract carries all three required checks with the
    CA-201 successor and byte-binds the revenue workflow file;
(f) the uc ci-gap assessor reports honestly (deterministic JSON, every
    unsatisfied check maps to the CA-201 successor; no fake green);
(g) README §7 documents the absorption (CA-201 owns, ZR-105/ZR-901
    provide required checks).

Zero product-code / workflow-file changes on this card.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
QUALITY_YML = REPO_ROOT / ".github" / "workflows" / "quality.yml"
SIBLING_TOOL = REPO_ROOT / "tools" / "ci_checkout_siblings.py"
CURRENT_JSON = REPO_ROOT / "compatibility" / "current.json"
CONTRACT_JSON = (
    REPO_ROOT / "assurance" / "unified_completion" / "ci" / "current_triplet_contract.json"
)
UC_DIR = REPO_ROOT / "assurance" / "unified_completion"
README_MD = REPO_ROOT / "audit_review" / "README.md"

SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_cat_file_ok(repo: Path, commit: str) -> bool:
    try:
        subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", f"{commit}^{{commit}}"],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


# ---------------------------------------------------------------------------
# (a) manifest-driven sibling checkout referenced from quality.yml
# ---------------------------------------------------------------------------


def test_quality_yml_uses_manifest_driven_sibling_checkout() -> None:
    text = _read_text(QUALITY_YML)
    assert "compatibility/current.json" in text, "workflow must reference the manifest"
    assert "ci_checkout_siblings" in text, (
        "workflow must run the manifest-driven sibling checkout tool"
    )
    assert "current_triplet" in text or "current.json" in text


def test_quality_yml_has_no_floating_clone_no_swallow() -> None:
    text = _read_text(QUALITY_YML)
    clone_hits = [
        ln for ln, line in enumerate(text.splitlines(), 1) if "git clone" in line
    ]
    assert not clone_hits, f"floating git clone present: {clone_hits}"
    swallow_hits = [
        ln for ln, line in enumerate(text.splitlines(), 1) if re.search(r"\|\|\s*true", line)
    ]
    assert not swallow_hits, f"unconditional || true swallows: {swallow_hits}"


# ---------------------------------------------------------------------------
# (b) sibling checkout tool: manifest-only, CLI runs
# ---------------------------------------------------------------------------


def test_sibling_tool_is_manifest_driven_only() -> None:
    text = _read_text(SIBLING_TOOL)
    assert 'manifest["current_triplet"]' in text or "current_triplet" in text, (
        "tool must read the current triplet from the manifest"
    )
    hardcoded = [sha for sha in SHA40.findall(text) if sha not in ("0" * 40,)]
    assert not hardcoded, f"hardcoded pinned shas in tool: {hardcoded}"


def test_sibling_tool_cli_runs() -> None:
    proc = subprocess.run(
        [sys.executable, str(SIBLING_TOOL), "--help"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr[-500:]
    assert "--manifest" in proc.stdout


# ---------------------------------------------------------------------------
# (c) manifest triplets well-formed and revenue legs resolvable
# ---------------------------------------------------------------------------


def test_manifest_triplets_well_formed_and_resolvable() -> None:
    data = json.loads(_read_text(CURRENT_JSON))
    assert data["schema_version"] == "1.0"
    for field in ("frozen_baseline_triplet", "current_triplet"):
        triplet = data[field]
        assert set(triplet) == {"revenue", "filing", "wiki"}, field
        for repo, sha in triplet.items():
            assert SHA40.match(sha), f"{field}.{repo} not a full sha: {sha!r}"
            if repo == "revenue":
                assert _git_cat_file_ok(REPO_ROOT, sha), (
                    f"{field}.revenue {sha} does not resolve in this repo"
                )
    assert data["remotes"]["revenue"].startswith("https://")
    assert len(data["remotes"]) == 3


# ---------------------------------------------------------------------------
# (d) ZR-105 contract: three required checks, CA-201 successor, byte-binding
# ---------------------------------------------------------------------------


def test_contract_three_required_checks_and_workflow_binding() -> None:
    data = json.loads(_read_text(CONTRACT_JSON))
    assert data["schema_version"] == 1
    assert data["unit"] == "ZR-105"
    expected = {
        "exact_triplet_binding",
        "affected_repo_fanout",
        "collected_skip_delta_controlled",
    }
    assert set(data["required_checks"]) == expected
    for name in expected:
        check = data["required_checks"][name]
        assert check["machine_rules"], name
        assert data["successors"][name] == "CA-201", name
    rev = data["workflow_files"]["revenue"]
    assert rev["rel_path"] == ".github/workflows/quality.yml"
    assert rev["sha256"] == _sha256_bytes(QUALITY_YML.read_bytes()), (
        "contract byte-binding for the revenue workflow drifted"
    )


# ---------------------------------------------------------------------------
# (e) ci-gap assessor honest report (deterministic, gap -> CA-201)
# ---------------------------------------------------------------------------


def test_ci_gap_assessor_honest_report() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(UC_DIR)
    proc = subprocess.run(
        [sys.executable, "-B", "-m", "uc.cli", "ci-gap"],
        cwd=str(UC_DIR),
        capture_output=True,
        text=True,
        env=env,
    )
    # exit 1 is the honest state when gaps remain (successor=CA-201), 0 when green.
    assert proc.returncode in (0, 1), proc.stderr[-500:]
    out = json.loads(proc.stdout)
    assert out["schema_version"] == 1
    assert out["unit"] == "ZR-105"
    assert "evaluated_at_utc" in out
    rev = out["repos"]["revenue"]
    assert rev["workflow_file"].endswith(".github/workflows/quality.yml")
    assert re.fullmatch(r"[0-9a-f]{64}", rev["workflow_sha256"])
    for name in (
        "exact_triplet_binding",
        "affected_repo_fanout",
        "collected_skip_delta_controlled",
    ):
        assert name in rev["checks"], name
    gaps = out.get("gaps", [])
    for gap in gaps:
        assert "revenue" in gap or "filing" in gap or "wiki" in gap
    for repo_name, section in out["repos"].items():
        for check_name, result in section["checks"].items():
            if not result["satisfied"]:
                assert result["successor"] == "CA-201", (
                    f"{repo_name}/{check_name} gap must map to the CA-201 successor"
                )


# ---------------------------------------------------------------------------
# (f) README §7 absorption documented
# ---------------------------------------------------------------------------


def test_readme_section7_documents_absorption() -> None:
    lines = _read_text(README_MD).splitlines()
    hits = [
        line
        for line in lines
        if "current-triplet PR fan-out" in line and "CA-201" in line
    ]
    assert hits, "README §7 must carry the current-triplet PR fan-out absorption row"
    row = hits[0]
    assert "ZR-105" in row and "ZR-901" in row, (
        "absorption row must name ZR-105 and ZR-901 as required-checks providers"
    )
    assert "ZR" in row and "CA" in row
