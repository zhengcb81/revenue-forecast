"""Both closure CLI exits must fail on evidence that fails byte replay."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import uc.scenarios as scenarios
from conftest import REPO_ROOT


CONTROL_CODE = REPO_ROOT / "assurance" / "unified_completion"


def _invalid_registry(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "revenue"
    for matrix in (scenarios.OLD_MATRIX, scenarios.NEW_MATRIX):
        target = root / matrix
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(REPO_ROOT / matrix, target)
    for sibling in ("filing-fetch", "company-wiki"):
        (tmp_path / sibling / "assurance" / "fc").mkdir(parents=True)
    control = root / "assurance" / "unified_completion"
    registry = control / "scenarios" / "scenario_registry.json"
    registry.parent.mkdir(parents=True)
    scenarios.build(root, registry)
    evidence_rel = "assurance/unified_completion/scenarios/evidence/proof.json"
    evidence = root / evidence_rel
    evidence.parent.mkdir(parents=True)
    evidence.write_bytes(b'{"proof":1}\n')
    digest = hashlib.sha256(evidence.read_bytes()).hexdigest()
    payload = json.loads(registry.read_text(encoding="utf-8"))
    for info in payload["scenarios"].values():
        info.update(status="passed", evidence_path=evidence_rel, fixture_hash=digest)
    first = next(iter(payload["scenarios"].values()))
    first["fixture_hash"] = "0" * 64  # well-formed, but not the file hash
    registry.write_text(json.dumps(payload), encoding="utf-8")
    legacy = control / "legacy" / "legacy_disposition.json"
    legacy.parent.mkdir(parents=True)
    legacy.write_text('{"fc_entries":[]}', encoding="utf-8")
    return root, registry


def _run_cli(root: Path, command: str) -> subprocess.CompletedProcess[str]:
    code = (
        "import sys; from pathlib import Path; import uc.cli as cli; "
        "cli.REPO_ROOT=Path(sys.argv[1]); "
        "cli.CONTROL_ROOT=cli.REPO_ROOT/'assurance'/'unified_completion'; "
        "cli.SCENARIO_REGISTRY_PATH=Path(sys.argv[2]); "
        "raise SystemExit(getattr(cli, sys.argv[3])(None))"
    )
    env = dict(os.environ)
    env["PYTHONPATH"] = str(CONTROL_CODE)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", "-c", code, str(root),
         str(root / "assurance/unified_completion/scenarios/scenario_registry.json"), command],
        cwd=root, env=env, capture_output=True, text=True, encoding="utf-8",
        timeout=30, check=False,
    )


def test_scenario_verify_cli_exits_nonzero_for_wrong_evidence_hash(tmp_path):
    root, _registry = _invalid_registry(tmp_path)
    result = _run_cli(root, "cmd_scenario_verify")
    assert result.returncode == 1, result.stdout + result.stderr
    assert json.loads(result.stdout)["closure_ready"] is False


def test_three_repo_closure_cli_exits_nonzero_for_wrong_evidence_hash(tmp_path):
    root, _registry = _invalid_registry(tmp_path)
    result = _run_cli(root, "cmd_closure_report")
    assert result.returncode == 1, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["old_plan_verdict"] == "incomplete"
    assert report["scenario_summary"]["closure_ready"] is False
