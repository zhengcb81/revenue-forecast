"""G5-RF-INSTALL: explicit ``--file`` scope, zero-write ``--plan``, real partial failure.

The three behaviours framed RED first (card §5), before the tool is extended:

  1. the real CLI does not accept a two-file ``--file`` selection — and once it
     does, it must touch exactly those files and leave every other installable
     file alone;
  2. a repeat sync must not rewrite the mtime of an installed file whose bytes
     are already identical;
  3. a controlled replace failure must produce an accurate partial result
     (written / not-written / conflict) instead of a traceback.

Temp hygiene under a failing copy/replace was already correct in the previous
tool (``finally: temporary.unlink(missing_ok=True)`` plus ``TemporaryDirectory``);
it is asserted here as an EXISTING GREEN rather than re-faked as a RED.

The remaining unit and E2E cases follow the same file once the extension lands.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from sync_installations import (  # noqa: E402
    PLAN_SCHEMA,
    RESULT_SCHEMA,
    SKILL_NAME,
    ScopeError,
    apply_target,
    installable_files,
    installation_diff,
    plan_target,
    resolve_file_scope,
    sync_installation,
)

RUNTIME_DIRECTORIES = ("agents", "config", "references", "scripts")


def _skill(root: Path, marker: str, *, with_tests: bool = True) -> Path:
    """Synthetic installable root shaped like the real one."""
    root.mkdir(parents=True)
    for name in (".gitignore", "CHANGELOG.md", "SKILL.md"):
        (root / name).write_text(f"{name}:{marker}\n", encoding="utf-8")
    for directory in RUNTIME_DIRECTORIES:
        path = root / directory
        path.mkdir()
        (path / f"{directory}.py").write_text(
            f"{directory} = {marker!r}\n", encoding="utf-8"
        )
    if with_tests:
        tests = root / "tests"
        tests.mkdir()
        (tests / "test_engineering_gate.py").write_text(
            "from tools import pre_push_gate\n", encoding="utf-8"
        )
    return root


def _cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            "-B",
            str(REPO_ROOT / "tools" / "sync_installations.py"),
            *args,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        cwd=str(REPO_ROOT),
    )


def _is_junction(entry: os.DirEntry) -> bool:
    checker = getattr(entry, "is_junction", None)
    if checker is None:
        return False
    try:
        return bool(checker())
    except (OSError, NotImplementedError):
        return False


def _snapshot(root: Path) -> dict[str, tuple[int, int, str]]:
    """Byte/mtime inventory that never descends through a link or reparse point."""
    inventory: dict[str, tuple[int, int, str]] = {}
    stack = [root]
    while stack:
        current = stack.pop()
        with os.scandir(current) as entries:
            for entry in entries:
                path = Path(entry.path)
                relative = path.relative_to(root).as_posix()
                if entry.is_symlink():
                    inventory[relative] = (0, 0, "link")
                elif entry.is_dir(follow_symlinks=False):
                    if _is_junction(entry):
                        inventory[relative] = (0, 0, "junction")
                    else:
                        stack.append(path)
                else:
                    stat = entry.stat(follow_symlinks=False)
                    inventory[relative] = (
                        stat.st_size,
                        stat.st_mtime_ns,
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                    )
    return inventory


def _obstruct(target: Path, relative: str) -> None:
    """Occupy an installed package path with a directory.

    A directory in the way makes ``os.replace(file, path)`` fail on Windows
    (PermissionError) and on POSIX (IsADirectoryError), so the controlled
    failure is host-neutral.  Making the file read-only would only fail on
    Windows and would be a host assumption.
    """
    path = target / relative
    path.unlink()
    path.mkdir()


def _no_temp_residue(destination: Path, target: Path) -> list[str]:
    residue = [
        entry.name
        for entry in destination.iterdir()
        if entry.name.startswith(f".{SKILL_NAME}-stage-")
    ]
    residue += [str(p) for p in target.rglob("*.syncing")]
    return residue


# ---------------------------------------------------------------------------
# RED 1 — the real CLI cannot select two files
# ---------------------------------------------------------------------------


def test_cli_selects_only_the_named_files(tmp_path: Path) -> None:
    canonical = _skill(tmp_path / "canonical", "new")
    destination = tmp_path / "skills"
    target = _skill(destination / SKILL_NAME, "old")

    proc = _cli(
        "--canonical",
        str(canonical),
        "--destination",
        str(destination),
        "--file",
        "scripts/scripts.py",
        "--file",
        "SKILL.md",
        "--apply",
    )

    assert proc.returncode == 0, f"stdout={proc.stdout}\nstderr={proc.stderr}"
    assert (target / "SKILL.md").read_text(encoding="utf-8") == "SKILL.md:new\n"
    assert (target / "scripts" / "scripts.py").read_text(encoding="utf-8") == (
        "scripts = 'new'\n"
    )
    # every file outside the two-file scope is untouched
    untouched = {
        ".gitignore": ".gitignore:old\n",
        "CHANGELOG.md": "CHANGELOG.md:old\n",
        "agents/agents.py": "agents = 'old'\n",
        "config/config.py": "config = 'old'\n",
        "references/references.py": "references = 'old'\n",
    }
    for relative, expected in untouched.items():
        assert (target / relative).read_text(encoding="utf-8") == expected, relative


# ---------------------------------------------------------------------------
# RED 2 — a repeat sync rewrites the mtime of identical bytes
# ---------------------------------------------------------------------------


def test_repeat_apply_leaves_identical_bytes_mtime_untouched(tmp_path: Path) -> None:
    canonical = _skill(tmp_path / "canonical", "same")
    destination = tmp_path / "skills"
    target = _skill(destination / SKILL_NAME, "same")

    source = canonical / "SKILL.md"
    installed = target / "SKILL.md"
    assert source.read_bytes() == installed.read_bytes()

    # installed copy is older than the source; identical bytes must not be
    # touched at all, so the (deliberately stale) mtime has to survive.
    stale = source.stat().st_mtime - 5000.0
    os.utime(installed, (stale, stale))
    before = _snapshot(destination)

    sync_installation(canonical, destination)

    after = _snapshot(destination)
    assert after == before, "identical bytes were rewritten (mtime/size/content)"


# ---------------------------------------------------------------------------
# RED 3 — a controlled replace failure has no partial report
# ---------------------------------------------------------------------------


def test_failed_replace_reports_accurate_partial_result(tmp_path: Path) -> None:
    canonical = _skill(tmp_path / "canonical", "new")
    destination = tmp_path / "skills"
    target = _skill(destination / SKILL_NAME, "old")
    _obstruct(target, "scripts/scripts.py")

    proc = _cli(
        "--canonical",
        str(canonical),
        "--destination",
        str(destination),
        "--file",
        "scripts/scripts.py",
        "--file",
        "SKILL.md",
        "--apply",
        "--json",
    )

    assert proc.returncode != 0, proc.stdout
    # stdout must be exactly one JSON value; diagnostics go to stderr
    payload = json.loads(proc.stdout)
    assert payload["schema"] == "rf-install-result/1"

    entry = payload["targets"][0]
    assert entry["status"] == "partial", entry
    assert entry["written"] == ["SKILL.md"], entry
    assert entry["unchanged"] == [], entry
    assert [item["path"] for item in entry["failed"]] == ["scripts/scripts.py"]
    assert entry["failed"][0]["reason"] in {"write_error", "conflict"}
    assert entry["remaining_selected_drift"] == 1
    assert proc.returncode == 1

    # the completed file really landed, the obstructed one really did not
    assert (target / "SKILL.md").read_text(encoding="utf-8") == "SKILL.md:new\n"
    assert _no_temp_residue(destination, target) == []


# ---------------------------------------------------------------------------
# EXISTING GREEN — temp hygiene was already correct in the previous tool
# ---------------------------------------------------------------------------


def test_failed_replace_leaves_no_stage_or_syncing_residue(tmp_path: Path) -> None:
    canonical = _skill(tmp_path / "canonical", "new")
    destination = tmp_path / "skills"
    target = _skill(destination / SKILL_NAME, "old")
    _obstruct(target, "scripts/scripts.py")

    with pytest.raises(OSError):
        sync_installation(canonical, destination)

    assert _no_temp_residue(destination, target) == []


# ---------------------------------------------------------------------------
# scope validation: normalization, ordering, duplicates, bad input
# ---------------------------------------------------------------------------


def _sha_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_file_scope_normalizes_deduplicates_and_sorts(tmp_path: Path) -> None:
    canonical = _skill(tmp_path / "canonical", "one")

    scope = resolve_file_scope(
        canonical,
        [
            "scripts/scripts.py",
            "./scripts/scripts.py",
            "scripts\\scripts.py",
            "SKILL.md",
            "scripts/scripts.py",
        ],
    )

    assert scope == ["SKILL.md", "scripts/scripts.py"]


def _link_directory(source: Path, destination: Path) -> None:
    """Create a directory link, or skip when the host forbids them."""
    try:
        os.symlink(source, destination, target_is_directory=True)
        return
    except OSError:
        pass
    try:
        proc = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(destination), str(source)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
    except OSError:
        proc = None
    if proc is None or proc.returncode != 0 or not destination.exists():
        pytest.skip("directory links are not permitted on this host")


def test_bad_scope_is_rejected_before_any_destination_is_written(
    tmp_path: Path,
) -> None:
    canonical = _skill(tmp_path / "canonical", "new")
    destination = tmp_path / "skills"
    target = _skill(destination / SKILL_NAME, "old")
    canonical_before = _snapshot(canonical)
    destination_before = _snapshot(destination)

    for bad in (
        str(canonical / "SKILL.md"),
        "",
        "../outside.md",
        "references/../SKILL.md",
        "scripts",
        "tests/test_engineering_gate.py",
        "not-in-the-closure.md",
    ):
        with pytest.raises(ScopeError):
            resolve_file_scope(canonical, [bad])

    assert _snapshot(canonical) == canonical_before
    assert _snapshot(destination) == destination_before

    # the real CLI refuses a bad scope before it touches a single file
    proc = _cli(
        "--canonical",
        str(canonical),
        "--destination",
        str(destination),
        "--file",
        "../outside.md",
        "--apply",
    )
    assert proc.returncode == 2
    assert proc.stdout == ""
    assert _snapshot(destination) == destination_before
    assert (target / "SKILL.md").read_text(encoding="utf-8") == "SKILL.md:old\n"


def test_scope_rejects_a_link_that_escapes_the_installation_target(
    tmp_path: Path,
) -> None:
    canonical = _skill(tmp_path / "canonical", "new")
    destination = tmp_path / "skills"
    target = _skill(destination / SKILL_NAME, "old")
    outside = tmp_path / "outside"
    outside.mkdir()
    shutil.rmtree(target / "references")
    _link_directory(outside, target / "references")
    before = _snapshot(destination)

    proc = _cli(
        "--canonical",
        str(canonical),
        "--destination",
        str(destination),
        "--file",
        "references/references.py",
        "--apply",
    )

    assert proc.returncode == 2
    assert proc.stdout == ""
    # rejected because the link leaves the installation target, not because the
    # path is outside the canonical closure
    assert "escapes the installation target" in proc.stderr
    assert "outside the installable runtime closure" not in proc.stderr
    assert _snapshot(destination) == before
    assert (target / "SKILL.md").read_text(encoding="utf-8") == "SKILL.md:old\n"


# ---------------------------------------------------------------------------
# missing installation, plan schema, flag exclusions, exit codes
# ---------------------------------------------------------------------------


def test_missing_installation_check_keeps_old_semantics_and_plan_reports_new(
    tmp_path: Path,
) -> None:
    canonical = _skill(tmp_path / "canonical", "new")
    destination = tmp_path / "skills"

    check = _cli("--canonical", str(canonical), "--destination", str(destination))
    assert check.returncode == 0
    assert "MATCH" in check.stdout
    assert not destination.exists()

    plan = _cli(
        "--canonical",
        str(canonical),
        "--destination",
        str(destination),
        "--file",
        "SKILL.md",
        "--plan",
    )
    assert plan.returncode == 0
    entry = json.loads(plan.stdout)["targets"][0]
    assert entry["installed"] is False
    assert entry["selected_drift"] == 1
    assert entry["files"] == [
        {
            "path": "SKILL.md",
            "operation": "new",
            "before_sha256": None,
            "source_sha256": _sha_of(canonical / "SKILL.md"),
            "size": (canonical / "SKILL.md").stat().st_size,
        }
    ]
    # a plan never creates the destination
    assert not destination.exists()


def test_plan_is_zero_write_and_reports_operations_and_drift_counts(
    tmp_path: Path,
) -> None:
    canonical = _skill(tmp_path / "canonical", "new")
    destination = tmp_path / "skills"
    target = _skill(destination / SKILL_NAME, "old")
    (target / "SKILL.md").write_text("SKILL.md:new\n", encoding="utf-8")
    before = _snapshot(destination)

    proc = _cli(
        "--canonical",
        str(canonical),
        "--destination",
        str(destination),
        "--file",
        "SKILL.md",
        "--file",
        "scripts/scripts.py",
        "--file",
        "references/references.py",
        "--plan",
    )

    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["schema"] == PLAN_SCHEMA
    assert payload["selected"] == [
        "SKILL.md",
        "references/references.py",
        "scripts/scripts.py",
    ]
    entry = payload["targets"][0]
    assert entry["selected_drift"] == 2
    assert entry["unselected_drift"] == 4
    by_path = {item["path"]: item for item in entry["files"]}
    for item in entry["files"]:
        assert set(item) == {
            "path",
            "operation",
            "before_sha256",
            "source_sha256",
            "size",
        }
        assert item["operation"] in {"new", "replace", "unchanged"}
    assert by_path["SKILL.md"]["operation"] == "unchanged"
    assert by_path["scripts/scripts.py"]["operation"] == "replace"
    assert by_path["scripts/scripts.py"]["before_sha256"] == _sha_of(
        target / "scripts" / "scripts.py"
    )
    assert by_path["scripts/scripts.py"]["source_sha256"] == _sha_of(
        canonical / "scripts" / "scripts.py"
    )
    assert (
        by_path["scripts/scripts.py"]["size"]
        == (canonical / "scripts" / "scripts.py").stat().st_size
    )
    assert _snapshot(destination) == before


def test_plan_and_result_modes_reject_conflicting_flags(tmp_path: Path) -> None:
    canonical = _skill(tmp_path / "canonical", "new")
    other = _skill(tmp_path / "other", "new")
    destination = tmp_path / "skills"
    _skill(destination / SKILL_NAME, "old")
    before = _snapshot(canonical)

    for extra in (
        ("--apply",),
        ("--print-manifest",),
        ("--import-from", str(other)),
    ):
        plan_proc = _cli(
            "--canonical",
            str(canonical),
            "--destination",
            str(destination),
            "--file",
            "SKILL.md",
            "--plan",
            *extra,
        )
        assert plan_proc.returncode == 2, extra
        assert plan_proc.stdout == "", extra

    for flag, value in (("--file", "SKILL.md"), ("--json", "unused")):
        for extra in (("--print-manifest",), ("--import-from", str(other))):
            proc = _cli(
                "--canonical",
                str(canonical),
                "--destination",
                str(destination),
                flag,
                value,
                *extra,
            )
            assert proc.returncode == 2, (flag, extra)
            assert proc.stdout == "", (flag, extra)

    assert _snapshot(canonical) == before


def test_selected_drift_sets_the_exit_code_and_unselected_drift_does_not(
    tmp_path: Path,
) -> None:
    canonical = _skill(tmp_path / "canonical", "new")
    destination = tmp_path / "skills"
    target = _skill(destination / SKILL_NAME, "old")
    (target / "SKILL.md").write_text("SKILL.md:new\n", encoding="utf-8")

    clean = _cli(
        "--canonical",
        str(canonical),
        "--destination",
        str(destination),
        "--file",
        "SKILL.md",
    )
    assert clean.returncode == 0
    match_lines = [
        line for line in clean.stdout.splitlines() if line.startswith("MATCH")
    ]
    assert match_lines and match_lines[0].endswith(": 1 selected files")
    # a clean subset must never print the whole-runtime MATCH
    assert "7 files" not in clean.stdout
    assert any("unselected" in line for line in clean.stdout.splitlines())

    (target / "SKILL.md").write_text("SKILL.md:old\n", encoding="utf-8")
    drifting = _cli(
        "--canonical",
        str(canonical),
        "--destination",
        str(destination),
        "--file",
        "SKILL.md",
    )
    assert drifting.returncode == 1
    assert "1 of 1 selected files" in drifting.stdout

    as_json = _cli(
        "--canonical",
        str(canonical),
        "--destination",
        str(destination),
        "--file",
        "SKILL.md",
        "--json",
    )
    assert as_json.returncode == 1
    payload = json.loads(as_json.stdout)
    assert payload["schema"] == RESULT_SCHEMA
    assert payload["mode"] == "check"
    entry = payload["targets"][0]
    assert entry["status"] == "completed"
    assert entry["remaining_selected_drift"] == 1
    assert entry["remaining_unselected_drift"] == 6


# ---------------------------------------------------------------------------
# identical bytes: no stage copy, no replace, mtime evidence plus a spy
# ---------------------------------------------------------------------------


def test_identical_bytes_get_no_stage_copy_and_no_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    canonical = _skill(tmp_path / "canonical", "same")
    destination = tmp_path / "skills"
    target = _skill(destination / SKILL_NAME, "same")
    source = canonical / "SKILL.md"
    installed = target / "SKILL.md"
    stale = source.stat().st_mtime - 5000.0
    os.utime(installed, (stale, stale))
    before = _snapshot(destination)

    replacements: list[str] = []
    real_replace = os.replace

    def spy(src, dst):
        replacements.append(str(dst))
        return real_replace(src, dst)

    monkeypatch.setattr(os, "replace", spy)
    result = sync_installation(canonical, destination)

    assert replacements == []
    assert _snapshot(destination) == before
    assert result["written"] == []
    expected_scope = [
        path.relative_to(canonical).as_posix() for path in installable_files(canonical)
    ]
    assert result["unchanged"] == expected_scope
    assert installation_diff(canonical, destination) == []


# ---------------------------------------------------------------------------
# byte-level concurrency: source/target changing after the plan
# ---------------------------------------------------------------------------


def test_target_edit_landing_after_the_plan_is_reported_as_conflict(
    tmp_path: Path,
) -> None:
    canonical = _skill(tmp_path / "canonical", "new")
    destination = tmp_path / "skills"
    target = _skill(destination / SKILL_NAME, "old")
    plan = plan_target(canonical, destination, ["SKILL.md"])
    (target / "SKILL.md").write_text("SKILL.md:newer user edit\n", encoding="utf-8")

    result = apply_target(canonical, destination, plan)

    assert result["written"] == []
    assert result["unchanged"] == []
    assert [item["path"] for item in result["failed"]] == ["SKILL.md"]
    assert result["failed"][0]["reason"] == "conflict"
    assert result["conflicts"] == ["SKILL.md"]
    assert result["status"] == "failed"
    assert (target / "SKILL.md").read_text(encoding="utf-8") == (
        "SKILL.md:newer user edit\n"
    )
    assert _no_temp_residue(destination, target) == []


def test_source_edit_landing_after_the_plan_is_reported_as_conflict(
    tmp_path: Path,
) -> None:
    canonical = _skill(tmp_path / "canonical", "new")
    destination = tmp_path / "skills"
    target = _skill(destination / SKILL_NAME, "old")
    plan = plan_target(canonical, destination, ["SKILL.md"])
    (canonical / "SKILL.md").write_text(
        "SKILL.md:revised canonical\n", encoding="utf-8"
    )

    result = apply_target(canonical, destination, plan)

    assert result["failed"][0]["reason"] == "conflict"
    assert result["conflicts"] == ["SKILL.md"]
    assert result["written"] == []
    assert (canonical / "SKILL.md").read_text(encoding="utf-8") == (
        "SKILL.md:revised canonical\n"
    )
    assert (target / "SKILL.md").read_text(encoding="utf-8") == "SKILL.md:old\n"


# ---------------------------------------------------------------------------
# rerun converges on the remainder; protected state survives
# ---------------------------------------------------------------------------


def test_rerun_after_a_partial_failure_only_writes_the_remainder(
    tmp_path: Path,
) -> None:
    canonical = _skill(tmp_path / "canonical", "new")
    destination = tmp_path / "skills"
    target = _skill(destination / SKILL_NAME, "old")
    _obstruct(target, "scripts/scripts.py")
    scope = ["--file", "SKILL.md", "--file", "scripts/scripts.py"]

    first = _cli(
        "--canonical",
        str(canonical),
        "--destination",
        str(destination),
        *scope,
        "--apply",
        "--json",
    )
    assert first.returncode == 1
    partial = json.loads(first.stdout)["targets"][0]
    assert partial["status"] == "partial"
    assert partial["written"] == ["SKILL.md"]
    landed_mtime = (target / "SKILL.md").stat().st_mtime_ns
    assert _no_temp_residue(destination, target) == []

    (target / "scripts" / "scripts.py").rmdir()

    second = _cli(
        "--canonical",
        str(canonical),
        "--destination",
        str(destination),
        *scope,
        "--apply",
        "--json",
    )
    assert second.returncode == 0
    recovered = json.loads(second.stdout)["targets"][0]
    assert recovered["status"] == "completed"
    assert recovered["written"] == ["scripts/scripts.py"]
    assert recovered["unchanged"] == ["SKILL.md"]
    assert recovered["remaining_selected_drift"] == 0
    # the file written by the first run is not touched again
    assert (target / "SKILL.md").stat().st_mtime_ns == landed_mtime
    remaining = set(installation_diff(canonical, destination))
    assert remaining.isdisjoint({"SKILL.md", "scripts/scripts.py"})


def test_selective_apply_preserves_output_config_and_repository_residue(
    tmp_path: Path,
) -> None:
    canonical = _skill(tmp_path / "canonical", "new")
    destination = tmp_path / "skills"
    target = _skill(destination / SKILL_NAME, "old")
    output = target / "output"
    output.mkdir()
    artifact = output / "forecast.json"
    artifact.write_text('{"keep": true}\n', encoding="utf-8")
    user_config = target / "config" / "user_local.json"
    user_config.write_text('{"mine": true}\n', encoding="utf-8")
    residue = target / "tests" / "test_engineering_gate.py"
    residue.write_text("from tools import pre_push_gate\n", encoding="utf-8")
    notes = target / "NOTES.md"
    notes.write_text("do not delete\n", encoding="utf-8")
    protected_before = _sha_of(artifact)

    proc = _cli(
        "--canonical",
        str(canonical),
        "--destination",
        str(destination),
        "--file",
        "scripts/scripts.py",
        "--apply",
    )

    assert proc.returncode == 0
    assert (target / "scripts" / "scripts.py").read_text(encoding="utf-8") == (
        "scripts = 'new'\n"
    )
    assert (target / "references" / "references.py").read_text(encoding="utf-8") == (
        "references = 'old'\n"
    )
    assert _sha_of(output / "forecast.json") == protected_before
    assert user_config.read_text(encoding="utf-8") == '{"mine": true}\n'
    assert residue.read_text(encoding="utf-8") == "from tools import pre_push_gate\n"
    assert notes.read_text(encoding="utf-8") == "do not delete\n"


# ---------------------------------------------------------------------------
# E2E: three tmp installation roots built from a Git-exported frozen runtime
# ---------------------------------------------------------------------------

# The card's live update list.  The drift applied to the tmp roots below is
# SYNTHETIC: it only mirrors the shape of the real investigation and never
# claims that a real installation has been updated.
CARD_SCOPE = (
    ".gitignore",
    "SKILL.md",
    "agents/openai.yaml",
    "references/extended-models.md",
    "references/input-construction.md",
    "references/model-library.md",
    "references/schema-migration-3.6-to-3.7.md",
    "scripts/revenue_forecast.py",
)
# Deliberately outside the update list: proves unselected drift is reported
# truthfully and can never fail a completed selected sync.
UNSELECTED_DRIFT = "references/output-schema.md"
SYNTHETIC_MARK = "\n# g5 synthetic installation drift\n"
SENTINELS = (
    "NOTES.md",
    "config/user_local.json",
    "output/forecast.json",
    "tests/test_engineering_gate.py",
)


def _frozen_runtime(owner: Path) -> Path:
    commit = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
        check=True,
    ).stdout.strip()
    archive = owner / "runtime.zip"
    subprocess.run(
        [
            "git",
            "-C",
            str(REPO_ROOT),
            "archive",
            "--format=zip",
            "-o",
            str(archive),
            commit,
            ".gitignore",
            "CHANGELOG.md",
            "SKILL.md",
            "agents",
            "config",
            "references",
            "scripts",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
        check=True,
    )
    root = owner / "runtime"
    root.mkdir()
    with zipfile.ZipFile(archive) as handle:
        handle.extractall(root)
    return root


def _install_frozen(frozen: Path, root: Path) -> Path:
    target = root / SKILL_NAME
    shutil.copytree(frozen, target)
    for relative in (*CARD_SCOPE, UNSELECTED_DRIFT):
        with open(target / relative, "a", encoding="utf-8", newline="") as handle:
            handle.write(SYNTHETIC_MARK)
    (target / "NOTES.md").write_text("do not delete\n", encoding="utf-8")
    (target / "config" / "user_local.json").write_text(
        '{"mine": true}\n', encoding="utf-8"
    )
    (target / "output").mkdir()
    (target / "output" / "forecast.json").write_text(
        '{"keep": true}\n', encoding="utf-8"
    )
    (target / "tests").mkdir()
    (target / "tests" / "test_engineering_gate.py").write_text(
        "from tools import pre_push_gate\n", encoding="utf-8"
    )
    return target


def test_e2e_three_tmp_roots_plan_apply_idempotence_and_recovery(
    tmp_path: Path,
) -> None:
    frozen = _frozen_runtime(tmp_path)
    roots = [tmp_path / "roots" / name for name in ("one", "two", "three")]
    targets = []
    for root in roots:
        root.mkdir(parents=True)
        targets.append(_install_frozen(frozen, root))

    scope_args = [item for relative in CARD_SCOPE for item in ("--file", relative)]
    destination_args = [item for root in roots for item in ("--destination", str(root))]

    def sentinel_shas() -> list[str]:
        return [
            _sha_of(target / relative) for target in targets for relative in SENTINELS
        ]

    sentinels_before = sentinel_shas()
    snapshots_before = [_snapshot(root) for root in roots]

    # --- 1. zero-write plan -------------------------------------------------
    plan_proc = _cli(
        "--canonical", str(frozen), *destination_args, *scope_args, "--plan"
    )
    assert plan_proc.returncode == 0, plan_proc.stderr
    plan = json.loads(plan_proc.stdout)
    assert plan["schema"] == PLAN_SCHEMA
    assert plan["selected"] == sorted(CARD_SCOPE)
    assert len(plan["targets"]) == 3
    for entry in plan["targets"]:
        assert entry["installed"] is True
        assert entry["selected_drift"] == len(CARD_SCOPE)
        assert entry["unselected_drift"] == 1
        operations = {item["path"]: item["operation"] for item in entry["files"]}
        assert set(operations) == set(CARD_SCOPE)
        assert set(operations.values()) == {"replace"}
        assert all(item["before_sha256"] for item in entry["files"])
        assert all(item["source_sha256"] for item in entry["files"])
        assert all(item["size"] > 0 for item in entry["files"])
    assert [_snapshot(root) for root in roots] == snapshots_before

    # --- 2. apply writes exactly the eight selected files -------------------
    apply_proc = _cli(
        "--canonical", str(frozen), *destination_args, *scope_args, "--apply", "--json"
    )
    assert apply_proc.returncode == 0, apply_proc.stderr
    applied = json.loads(apply_proc.stdout)
    assert applied["schema"] == RESULT_SCHEMA
    assert applied["mode"] == "apply"
    assert applied["status"] == "completed"
    assert len(applied["targets"]) == 3
    for entry in applied["targets"]:
        assert entry["written"] == sorted(CARD_SCOPE)
        assert entry["unchanged"] == []
        assert entry["failed"] == []
        assert entry["remaining_selected_drift"] == 0
        # the file deliberately left outside the scope stays drifted
        assert entry["remaining_unselected_drift"] == 1
    assert sentinel_shas() == sentinels_before

    # --- 3. a second apply writes nothing and moves no mtime ----------------
    snapshots_after_first = [_snapshot(root) for root in roots]
    repeat = _cli(
        "--canonical", str(frozen), *destination_args, *scope_args, "--apply", "--json"
    )
    assert repeat.returncode == 0, repeat.stderr
    repeated = json.loads(repeat.stdout)
    for entry in repeated["targets"]:
        assert entry["written"] == []
        assert entry["unchanged"] == sorted(CARD_SCOPE)
        assert entry["remaining_selected_drift"] == 0
    assert [_snapshot(root) for root in roots] == snapshots_after_first
    assert sentinel_shas() == sentinels_before

    # --- 4. one controlled replace failure reports partial, then converges --
    victim_root = roots[0]
    victim = targets[0]
    with open(victim / "SKILL.md", "a", encoding="utf-8", newline="") as handle:
        handle.write(SYNTHETIC_MARK)
    _obstruct(victim, "agents/openai.yaml")

    broken = _cli(
        "--canonical",
        str(frozen),
        "--destination",
        str(victim_root),
        *scope_args,
        "--apply",
        "--json",
    )
    assert broken.returncode == 1
    partial = json.loads(broken.stdout)["targets"][0]
    assert partial["status"] == "partial"
    assert partial["written"] == ["SKILL.md"]
    assert [item["path"] for item in partial["failed"]] == ["agents/openai.yaml"]
    assert partial["failed"][0]["reason"] == "write_error"
    assert partial["remaining_selected_drift"] == 1
    assert (victim / "SKILL.md").read_bytes() == (frozen / "SKILL.md").read_bytes()
    assert _no_temp_residue(victim_root, victim) == []
    assert sentinel_shas() == sentinels_before

    (victim / "agents" / "openai.yaml").rmdir()

    recovered = _cli(
        "--canonical",
        str(frozen),
        "--destination",
        str(victim_root),
        *scope_args,
        "--apply",
        "--json",
    )
    assert recovered.returncode == 0, recovered.stderr
    final = json.loads(recovered.stdout)["targets"][0]
    assert final["status"] == "completed"
    assert final["written"] == ["agents/openai.yaml"]
    assert len(final["unchanged"]) == len(CARD_SCOPE) - 1
    assert final["remaining_selected_drift"] == 0
    assert sentinel_shas() == sentinels_before
    for target in targets:
        for relative in CARD_SCOPE:
            assert (target / relative).read_bytes() == (frozen / relative).read_bytes()

    # --- 5. the installed entry points run without the development repo -----
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in {"PYTHONPATH", "PYTHONHOME"}
    }
    for target in targets:
        entry = target / "scripts" / "revenue_forecast.py"
        help_run = subprocess.run(
            [sys.executable, "-B", str(entry), "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
            cwd=str(target),
            env=env,
        )
        assert help_run.returncode == 0, help_run.stderr[-800:]
        assert "usage" in (help_run.stdout + help_run.stderr).lower()

        version_run = subprocess.run(
            [sys.executable, "-B", str(entry), "--version"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=300,
            cwd=str(target),
            env=env,
        )
        assert version_run.returncode == 0, version_run.stderr[-800:]
        assert version_run.stdout.startswith("revenue-forecast ")

    probe = subprocess.run(
        [sys.executable, "-B", "-c", "import json,sys;print(json.dumps(sys.path))"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        cwd=str(targets[0]),
        env=env,
    )
    child_paths = json.loads(probe.stdout.strip().splitlines()[-1])
    repo_root = os.path.normcase(str(REPO_ROOT))
    assert not any(
        os.path.normcase(str(item)).startswith(repo_root)
        for item in child_paths
        if item
    )
