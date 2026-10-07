"""Real-subprocess acceptance for the RF optional engineering tools.

Every case drives the shipped entry point; nothing here is a mocked PASS.

  E1  the default release-readiness CLI is check-only: exit 0, one accurate
      status per gate, and the repository (file list, content SHA, mtime and
      ``git status``) is byte-identical before and after.
  E2  an isolated checkout with no filing-fetch / company-wiki / backup /
      197-scenario material still defaults green and stays write-free;
      ``--record-rollback`` is the single explicit writer.
  E3  illegal configuration and an explicitly supplied bad HEAD SHA exit
      non-zero; a legal committed registry and a tampered one are told apart
      by the existing RF verifier.
  E4  final_ratchet's default mode never starts a coverage run; the explicit
      full mode refuses to run without its own scratch and writes every
      coverage file inside it.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

READINESS = ROOT / "tools" / "release_readiness.py"
RATCHET = ROOT / "tools" / "final_ratchet.py"
REGISTRY = (
    ROOT / "assurance" / "unified_completion" / "scenarios" / "scenario_registry.json"
)
SHORT_TARGET = "tests/test_schema_compatibility.py"


def _run(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict | None = None,
    timeout: int = 600,
) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(cwd or ROOT),
        env=env,
        timeout=timeout,
    )


def _tree_state(directory: Path) -> dict[str, tuple[str, int]]:
    state: dict[str, tuple[str, int]] = {}
    if not directory.exists():
        return state
    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        stat = path.stat()
        state[path.relative_to(directory).as_posix()] = (
            hashlib.sha256(path.read_bytes()).hexdigest(),
            stat.st_mtime_ns,
        )
    return state


def _coverage_root_state() -> dict[str, str]:
    """Coverage DATA files at the repository root (``.coveragerc`` is config)."""
    state: dict[str, str] = {}
    for path in sorted(ROOT.iterdir()):
        if not path.is_file():
            continue
        if path.name != ".coverage" and not path.name.startswith(".coverage."):
            continue
        state[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    return state


def _git_status(repo: Path) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain", "-uall"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return proc.stdout


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


# ---------------------------------------------------------------------------
# E1 — the default CLI is check-only and write-free
# ---------------------------------------------------------------------------


def test_e1_default_cli_is_zero_write_and_green():
    before_runs = _tree_state(ROOT / "assurance")
    before_cov = _coverage_root_state()
    before_status = _git_status(ROOT)
    proc = _run([str(READINESS)])
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out
    assert "NOT_SUPPLIED" in out
    assert "authorization" not in out
    assert _tree_state(ROOT / "assurance") == before_runs, (
        "check-only readiness must not create, modify or delete anything"
    )
    assert _coverage_root_state() == before_cov
    assert _git_status(ROOT) == before_status


def test_e1_default_cli_json_carries_one_status_per_gate():
    proc = _run([str(READINESS), "--json"])
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert set(payload) == {
        "fingerprints",
        "integrity",
        "scenario_evidence",
        "capacity",
        "backup",
        "rollback",
    }
    for name, gate in payload.items():
        assert gate["status"] in {"ok", "red", "not_supplied", "diagnostic"}, name
        assert isinstance(gate["problems"], list), name


# ---------------------------------------------------------------------------
# E2 — isolated checkout: no siblings, no backup, no 197 samples
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def isolated_rf(tmp_path_factory) -> Path:
    iso = tmp_path_factory.mktemp("g2-iso") / "revenue-forecast"
    (iso / "tools").mkdir(parents=True)
    shutil.copyfile(READINESS, iso / "tools" / "release_readiness.py")
    assert _git(iso, "init", "-q").returncode == 0
    assert _git(iso, "add", "tools/release_readiness.py").returncode == 0
    assert (
        _git(
            iso,
            "-c",
            "user.name=g2",
            "-c",
            "user.email=g2@example.invalid",
            "commit",
            "-q",
            "-m",
            "isolated rf",
        ).returncode
        == 0
    )
    return iso


def test_e2_isolated_default_is_green_and_write_free(isolated_rf):
    tool = isolated_rf / "tools" / "release_readiness.py"
    before_status = _git_status(isolated_rf)
    proc = _run([str(tool)], cwd=isolated_rf)
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out
    assert "NOT_SUPPLIED" in out
    assert "RED" not in out
    assert _git_status(isolated_rf) == before_status, (
        "an isolated default run must leave the checkout untouched"
    )


def test_e2_isolated_has_no_sibling_or_scenario_material(isolated_rf):
    assert not (isolated_rf.parent / "filing-fetch").exists()
    assert not (isolated_rf.parent / "company-wiki").exists()
    assert not (isolated_rf / "assurance").exists()


def test_e2_record_rollback_is_the_only_explicit_writer(isolated_rf):
    tool = isolated_rf / "tools" / "release_readiness.py"
    target = isolated_rf / "rollback_point.json"
    proc = _run([str(tool), "--record-rollback", str(target)], cwd=isolated_rf)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(target.read_text(encoding="utf-8"))
    assert payload["heads"]["revenue"]
    assert payload["recorded_at_utc"]


# ---------------------------------------------------------------------------
# E3 — explicit inputs: illegal configuration and bad SHAs fail
# ---------------------------------------------------------------------------


def test_e3_illegal_budget_is_a_configuration_error():
    proc = _run([str(READINESS), "--budget-mb", "not-a-number"])
    assert proc.returncode == 2, proc.stdout + proc.stderr


def test_e3_malformed_expect_head_is_a_configuration_error():
    proc = _run([str(READINESS), "--expect-head", "no-equals-sign"])
    assert proc.returncode == 2, proc.stdout + proc.stderr


def test_e3_explicit_mismatched_head_sha_is_nonzero():
    head = _git(ROOT, "rev-parse", "HEAD").stdout.strip()
    wrong = ("0" if head[0] != "0" else "1") + head[1:]
    proc = _run([str(READINESS), "--expect-head", f"revenue={wrong}"])
    out = proc.stdout + proc.stderr
    assert proc.returncode == 1, out
    assert "RED" in out


def test_e3_matching_head_sha_is_green():
    head = _git(ROOT, "rev-parse", "HEAD").stdout.strip()
    proc = _run([str(READINESS), "--expect-head", f"revenue={head}"])
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_e3_legal_committed_registry_is_accepted():
    proc = _run([str(READINESS), "--scenario-registry", str(REGISTRY)])
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out
    line = next(
        line for line in out.splitlines() if line.startswith("scenario_evidence:")
    )
    assert "NOT_SUPPLIED" not in line, line
    assert "scenarios" in line, line


def test_e3_tampered_registry_is_rejected(tmp_path):
    payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    broken = None
    for info in payload["scenarios"].values():
        if info.get("evidence_path"):
            broken = info
            break
    assert broken is not None, "the committed registry must carry evidence paths"
    broken["evidence_path"] = "g2/does/not/exist.json"
    tampered = tmp_path / "scenario_registry.json"
    tampered.write_text(json.dumps(payload), encoding="utf-8")
    proc = _run([str(READINESS), "--scenario-registry", str(tampered)])
    out = proc.stdout + proc.stderr
    assert proc.returncode == 1, out
    assert "RED" in out


def test_e3_missing_supplied_registry_is_nonzero(tmp_path):
    proc = _run([str(READINESS), "--scenario-registry", str(tmp_path / "no.json")])
    assert proc.returncode == 1, proc.stdout + proc.stderr


def test_e3_explicit_backup_dir_is_probed_without_writing(tmp_path):
    owner = tmp_path / "keep.bin"
    owner.write_bytes(b"owner bytes")
    before = _tree_state(tmp_path)
    proc = _run([str(READINESS), "--backup-dir", str(tmp_path)])
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert _tree_state(tmp_path) == before


def test_e3_missing_backup_dir_is_nonzero(tmp_path):
    proc = _run([str(READINESS), "--backup-dir", str(tmp_path / "absent")])
    assert proc.returncode == 1, proc.stdout + proc.stderr


def test_e3_explicit_catalog_is_probed(tmp_path):
    import sqlite3

    catalog = tmp_path / "catalog.sqlite3"
    with sqlite3.connect(catalog) as con:
        for table in ("documents", "sources", "locations"):
            con.execute(f"CREATE TABLE {table} (id INTEGER PRIMARY KEY)")
    proc = _run([str(READINESS), "--catalog", str(catalog)])
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_e3_missing_catalog_is_nonzero(tmp_path):
    proc = _run([str(READINESS), "--catalog", str(tmp_path / "absent.sqlite3")])
    assert proc.returncode == 1, proc.stdout + proc.stderr


# ---------------------------------------------------------------------------
# E4 — final_ratchet: light default, explicit full mode
# ---------------------------------------------------------------------------


def test_e4_default_is_green_and_never_touches_coverage():
    before_cov = _coverage_root_state()
    before_runs = _tree_state(ROOT / "assurance")
    proc = _run([str(RATCHET), "--print-json"])
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out[-4000:]
    payload = json.loads(proc.stdout)
    assert payload["coverage"]["status"] == "not_supplied"
    assert payload["coverage"]["ok"] is True
    assert payload["type"]["status"] in {"ok", "diagnostic"}
    assert payload["type"]["ok"] is True
    assert _coverage_root_state() == before_cov
    assert _tree_state(ROOT / "assurance") == before_runs


def test_e4_full_mode_requires_an_explicit_scratch():
    proc = _run([str(RATCHET), "--full"])
    assert proc.returncode != 0, proc.stdout + proc.stderr
    assert "coverage-scratch" in (proc.stdout + proc.stderr)


def test_e4_full_mode_writes_only_into_its_scratch(tmp_path):
    scratch = tmp_path / "cov"
    before_cov = _coverage_root_state()
    proc = _run(
        [
            str(RATCHET),
            "--full",
            "--coverage-scratch",
            str(scratch),
            "--coverage-target",
            SHORT_TARGET,
        ]
    )
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out[-4000:]
    produced = [p.name for p in scratch.iterdir() if p.is_file()]
    assert produced, out[-2000:]
    assert all(name.startswith(".coverage") for name in produced), produced
    assert _coverage_root_state() == before_cov
    assert "coverage: OK" in out


def test_e4_scanners_only_is_still_green():
    proc = _run([str(RATCHET), "--scanners-only"])
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out[-4000:]
    for gate in ("hardcode", "legacy", "encoding"):
        assert f"{gate}: OK" in out, gate
