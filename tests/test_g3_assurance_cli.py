"""G3-RF-ASSURANCE: uc.cli quality reporting surface.

The quality report CLI takes isolated, explicit inputs (``--root`` /
``--baseline``) so it never reads or writes production control state by
accident, and check-only execution writes zero files.  Corrupt or missing
explicit input fails with a non-zero exit code and is never repaired in
place.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UC_ROOT = ROOT / "assurance" / "unified_completion"
sys.path.insert(0, str(UC_ROOT))

REPO_ROOT = ROOT


def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "uc.cli", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        cwd=str(cwd or UC_ROOT),
    )


def _snapshot(root: Path) -> dict[str, tuple[int, int, str]]:
    return {
        path.relative_to(root).as_posix(): (
            path.stat().st_size,
            path.stat().st_mtime_ns,
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _make_rf_repo(tmp_path: Path) -> Path:
    """Minimal revenue repo whose CI workflow delegates to the type entry."""
    root = tmp_path / "revenue-forecast"

    contracts = root / "scripts" / "contracts"
    contracts.mkdir(parents=True)
    (contracts / "__init__.py").write_text("", encoding="utf-8")
    (root / "scripts" / "schema_compatibility.py").write_text("", encoding="utf-8")
    (root / "scripts" / "filing_fetch_client.py").write_text("", encoding="utf-8")
    (root / "scripts" / "trust_anchor.py").write_text("", encoding="utf-8")

    workflow = root / ".github" / "workflows"
    workflow.mkdir(parents=True)
    (workflow / "quality.yml").write_text(
        "jobs:\n  verify:\n    steps:\n      - run: python tools/pre_push_gate.py\n",
        encoding="utf-8",
    )

    tools = root / "tools"
    tools.mkdir()
    (tools / "pre_push_gate.py").write_text(
        "import sys\n"
        "gates = (\n"
        '    ([sys.executable, "-m", "mypy", "scripts/contracts/"],'
        ' "public contract types"),\n'
        ")\n",
        encoding="utf-8",
    )
    (tools / "run_coverage_gates.py").write_text(
        "PER_MODULE_MINIMUM = {}\n", encoding="utf-8"
    )
    (root / ".coveragerc").write_text("[report]\nfail_under = 0\n", encoding="utf-8")
    gate_test = root / "tests" / "test_fc1101_ci_manifest.py"
    gate_test.parent.mkdir(parents=True)
    gate_test.write_text(
        'import re\n\nSHA1 = re.compile(r"[0-9a-f]{40}")\n', encoding="utf-8"
    )
    return root


def _freeze_scratch_baseline(root: Path, path: Path) -> dict:
    from uc.quality import compute_baseline

    payload = compute_baseline(root)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


def test_quality_report_uses_isolated_explicit_inputs_and_writes_nothing(tmp_path):
    root = _make_rf_repo(tmp_path)
    baseline = root / "baseline.json"
    payload = _freeze_scratch_baseline(root, baseline)

    before = _snapshot(root)
    proc = _run(
        "quality-report",
        "--root",
        str(root),
        "--baseline",
        str(baseline),
        "--json",
    )
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out[-800:]

    report = json.loads(proc.stdout)
    assert report["failures"] == [], report["failures"]
    assert report["scope"]["revenue"]["status"] == "computed"
    assert report["scope"]["filing"]["status"] == "not_available"
    assert report["baseline"]["unit"] == payload["unit"]
    assert _snapshot(root) == before  # check-only: zero file writes


def test_quality_report_missing_explicit_baseline_fails_without_creating_it(
    tmp_path,
):
    root = _make_rf_repo(tmp_path)
    missing = tmp_path / "absent-baseline.json"

    proc = _run("quality-report", "--root", str(root), "--baseline", str(missing))
    out = proc.stdout + proc.stderr
    assert proc.returncode == 1, out[-800:]
    assert not missing.exists()


def test_quality_report_corrupt_baseline_fails_and_is_not_repaired(tmp_path):
    root = _make_rf_repo(tmp_path)
    baseline = root / "baseline.json"
    baseline.write_text("{ not json", encoding="utf-8")
    damaged = baseline.read_bytes()

    proc = _run("quality-report", "--root", str(root), "--baseline", str(baseline))
    out = proc.stdout + proc.stderr
    assert proc.returncode == 1, out[-800:]
    assert baseline.read_bytes() == damaged


def test_quality_report_rejects_invalid_config(tmp_path):
    root = _make_rf_repo(tmp_path)
    baseline = root / "baseline.json"
    baseline.write_text(
        json.dumps({"schema_version": 1, "unit": "WRONG-UNIT"}), encoding="utf-8"
    )

    proc = _run("quality-report", "--root", str(root), "--baseline", str(baseline))
    out = proc.stdout + proc.stderr
    assert proc.returncode == 1, out[-800:]
    assert "WRONG-UNIT" in out, out[-800:]


def test_quality_report_missing_root_fails(tmp_path):
    root = _make_rf_repo(tmp_path)
    baseline = root / "baseline.json"
    _freeze_scratch_baseline(root, baseline)

    proc = _run(
        "quality-report",
        "--root",
        str(tmp_path / "no-such-repo"),
        "--baseline",
        str(baseline),
    )
    out = proc.stdout + proc.stderr
    assert proc.returncode == 1, out[-800:]


def test_quality_verify_stays_green_and_exposes_diagnostics():
    """The historical ``quality-verify`` command now reports; only real
    failures can turn it red."""
    baseline = UC_ROOT / "quality" / "quality_baseline.json"
    proc = _run("quality-verify")
    out = proc.stdout + proc.stderr
    assert baseline.is_file()
    assert proc.returncode == 0, out[-800:]
    assert "QUALITY-NOTE" in out, out[-800:]
    assert "QUALITY-VIOLATION" not in out, out[-800:]


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
