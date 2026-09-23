"""E2E-EXPAND: cross-repo chain E2E via the standalone runner.

CI-step9-safe by default: the offline scenarios (S2/S3/S5/S6/S4) perform no
network calls, and the live download scenario S1 executes ONLY when
``RF_E2E_LIVE_DOWNLOAD=1`` — otherwise it is an honest pytest skip with the
reason on the marker (never a mock, never a silent pass).

The heavy lifting lives in ``e2e/run_cross_repo_chain_e2e.py`` (oracle:
.planning/<plan>/execution_runs/E2E-EXPAND/<attempt>/oracle.md).  This module
only invokes it as a subprocess against ``tmp_path`` and asserts the frozen
expectations, so collection itself never imports the chain.

Default offline test runs the runner with ``--live never`` (belt and braces:
no probe, no download, whatever the environment says).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "e2e" / "run_cross_repo_chain_e2e.py"
FF_SIBLING = REPO.parent / "filing-fetch"
CW_SIBLING = REPO.parent / "company-wiki"


def _chain_deps_available() -> tuple[bool, str]:
    """Environment probe for the offline chain (imports only, no network)."""
    if not (FF_SIBLING / "scripts" / "fetch_filing.py").is_file():
        return False, "filing-fetch sibling repo absent"
    if not (CW_SIBLING / "src" / "company_wiki").is_dir():
        return False, "company-wiki sibling repo absent"
    if not RUNNER.is_file():
        return False, "runner e2e/run_cross_repo_chain_e2e.py absent"
    try:
        import yaml  # noqa: F401
    except Exception as exc:  # noqa: BLE001
        return False, f"PyYAML unavailable: {type(exc).__name__}: {exc}"
    saved = list(sys.path)
    try:
        sys.path.insert(0, str(CW_SIBLING / "src"))
        sys.path.insert(0, str(REPO / "scripts"))
        import company_wiki.source_catalog.cli  # noqa: F401
        import company_wiki.source_catalog.resolver  # noqa: F401
        import company_wiki_source  # noqa: F401
    except Exception as exc:  # noqa: BLE001
        return False, f"chain import failed: {type(exc).__name__}: {exc}"
    finally:
        sys.path[:] = saved
    return True, ""


_AVAILABLE, _WHY = _chain_deps_available()


def _run_runner(args: list[str], tmp: Path, timeout: float):
    evidence = tmp / "ev"
    work = tmp / "work"
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    env.pop("RF_E2E_SPY_DIR", None)
    proc = subprocess.run(
        [sys.executable, "-B", str(RUNNER), *args,
         "--work-root", str(work), "--evidence-dir", str(evidence)],
        cwd=str(tmp), env=env, capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=timeout, check=False,
    )
    summary_path = evidence / "summary.json"
    summary = (json.loads(summary_path.read_text(encoding="utf-8"))
               if summary_path.is_file() else None)
    return proc, summary, evidence


def _by_id(summary) -> dict:
    return {s["id"]: s for s in summary["scenarios"]}


def test_offline_chain_scenarios(tmp_path):
    """S2 full chain + S3 reuse + S5/S6 refusals + S4 restore invariants."""
    if not _AVAILABLE:
        pytest.skip(f"chain dependencies unavailable: {_WHY}")
    proc, summary, _ = _run_runner(
        ["--scenarios", "S2,S3,S5,S6,S4", "--live", "never"], tmp_path,
        timeout=420)
    assert summary, (
        f"runner produced no summary (rc={proc.returncode})\n"
        f"stdout tail: {proc.stdout[-3000:]}\n"
        f"stderr tail: {proc.stderr[-3000:]}")
    by = _by_id(summary)
    for sid in ("S2", "S3", "S5", "S6", "S4"):
        assert sid in by, f"{sid} not executed; ran {sorted(by)}"
        assert by[sid]["status"] == "pass", (
            f"scenario {sid} did not pass: {json.dumps(by[sid], ensure_ascii=False)}")
    assert summary["live_gate"] == "never"
    assert summary["production_writes"] == 0
    assert proc.returncode == 0, (
        f"runner exit {proc.returncode}\n{proc.stdout[-3000:]}")


def test_live_download_scenario_is_opt_in(tmp_path):
    """Without RF_E2E_LIVE_DOWNLOAD=1 the live scenario must not run.

    Proves the CI-step9 default path performs no network: the runner is only
    ever asked for S1 here under the explicit opt-in below.
    """
    if not _AVAILABLE:
        pytest.skip(f"chain dependencies unavailable: {_WHY}")
    if os.environ.get("RF_E2E_LIVE_DOWNLOAD") == "1":
        pytest.skip("live authorized in this environment — covered by "
                    "test_live_download_and_delete_restore")
    proc, summary, _ = _run_runner(["--scenarios", "S1,S4", "--live", "never"],
                                   tmp_path, timeout=120)
    assert summary, f"no summary: rc={proc.returncode}\n{proc.stderr[-2000:]}"
    by = _by_id(summary)
    assert by["S1"]["status"] == "skip", by["S1"]
    assert by["S1"]["reason"]["code"] == "live_gate_never", by["S1"]
    assert summary["network_scope"].startswith("none"), summary["network_scope"]
    assert by["S4"]["status"] == "pass", by["S4"]
    assert proc.returncode == 0


@pytest.mark.skipif(
    os.environ.get("RF_E2E_LIVE_DOWNLOAD") != "1",
    reason="opt-in live download: set RF_E2E_LIVE_DOWNLOAD=1 "
           "(default step9 path performs no network; live is never mocked)",
)
def test_live_download_and_delete_restore(tmp_path):
    """Authorized S1: real download, verification, deletion proof, S4 clean."""
    if not _AVAILABLE:
        pytest.skip(f"chain dependencies unavailable: {_WHY}")
    proc, summary, evidence = _run_runner(["--scenarios", "S1,S4"], tmp_path,
                                          timeout=420)
    assert summary, (
        f"runner produced no summary (rc={proc.returncode})\n"
        f"stdout tail: {proc.stdout[-3000:]}\n"
        f"stderr tail: {proc.stderr[-3000:]}")
    by = _by_id(summary)
    s1 = by.get("S1")
    assert s1, f"S1 not executed: {sorted(by)}"
    proof = json.loads(
        (evidence / "s1" / "deletion_proof.json").read_text(encoding="utf-8"))
    # the owner's restore rule FIRST — it must hold whatever the product did:
    assert proof["post_absent"] is True, proof
    assert proof["asserted"] is True, proof
    s4 = by.get("S4")
    assert s4 and s4["status"] == "pass", json.dumps(s4, ensure_ascii=False)
    # then the product contract: pass, or an honest provider-classified skip —
    # never a fabricated pass (a frozen-contract violation surfaces as fail)
    assert s1["status"] in ("pass", "skip"), json.dumps(s1, ensure_ascii=False)
    if s1["status"] == "skip":
        assert s1["reason"] and s1["reason"].get("code"), s1
    if s1["status"] == "pass":
        assert proof["deleted_paths"], "downloaded files must be listed and deleted"
        assert proof["pre_delete_inventory"], "pre-delete inventory must be recorded"
        for rec in proof["deleted_paths"]:
            assert len(rec["sha256"]) == 64
    assert proc.returncode == 0, f"runner exit {proc.returncode}\n{proc.stdout[-3000:]}"
