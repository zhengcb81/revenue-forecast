"""G3-RF-ASSURANCE: the installable skill package is the runtime closure.

Covered here (each item maps to the G3 card's RED list):

  * ``installable_files`` is delimited by what the skill entry points
    actually need — repository engineering tests and ``tools/`` stay in the
    repository and no longer ship in the distribution package;
  * removing ``tests/**`` from the package cannot drop a real runtime
    import (a static closure scan proves the runtime never imports them);
  * check mode writes zero files; explicit sync updates only the files it
    owns inside a tmp staging area and preserves unknown files, user
    configuration and ``output`` — no whole-directory replacement;
  * ``installation_diff`` compares only the responsible runtime, so old
    repository-only residue is neither drift nor a usage permit;
  * a tmp installation built from the new set runs the real public entry
    points with no ``tools/`` present, and a missing runtime dependency
    fails loudly.
"""

from __future__ import annotations

import hashlib
import inspect
import json
import re
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from sync_installations import (  # noqa: E402
    SKILL_NAME,
    import_installation,
    installable_files,
    installation_diff,
    main,
    manifest,
    sync_installation,
    unique_destinations,
)

# The six engineering tests that G2 just synced and that read repo-only
# ``tools/`` — an installation consistent with them would still be unusable.
G2_ENGINEERING_TESTS = (
    "tests/test_rf_coverage_report.py",
    "tests/test_rf_optional_tools_e2e.py",
    "tests/test_rf_release_checklist.py",
    "tests/test_zr1001_release_readiness.py",
    "tests/test_zr906_final_ratchet.py",
    "tests/test_ca303_arch_quality.py",
)

RUNTIME_DIRECTORIES = ("agents", "config", "references", "scripts")


def _skill(root: Path, marker: str, *, with_tests: bool = True) -> Path:
    """Synthetic skill root shaped like the real one."""
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


# ---------------------------------------------------------------------------
# 1. packaging responsibility = runtime closure of the skill entry points
# ---------------------------------------------------------------------------


def test_installable_set_is_the_runtime_closure():
    files = installable_files(REPO_ROOT)
    relative = {path.relative_to(REPO_ROOT).as_posix() for path in files}

    assert "SKILL.md" in relative
    assert "CHANGELOG.md" in relative
    assert ".gitignore" in relative
    for directory in RUNTIME_DIRECTORIES:
        assert any(item.startswith(f"{directory}/") for item in relative), directory

    # repository engineering control plane stays in the repository
    assert not any(item.startswith("tests/") for item in relative)
    assert not any(item.startswith("tools/") for item in relative)
    assert not any(item.startswith("assurance/") for item in relative)
    assert not any(item.startswith("audit_review/") for item in relative)
    assert not any(item.startswith(".github/") for item in relative)
    for test_path in G2_ENGINEERING_TESTS:
        assert test_path not in relative, test_path


def test_synthetic_root_drops_repo_only_tests_directory():
    with TemporaryDirectory() as temporary:
        skill = _skill(Path(temporary) / "skill", "one")
        relative = {
            path.relative_to(skill).as_posix() for path in installable_files(skill)
        }

    assert "tests/test_engineering_gate.py" not in relative
    assert "config/config.py" in relative
    assert "scripts/scripts.py" in relative


def test_runtime_never_imports_repository_tests_or_tools():
    """Static closure evidence: nothing under the shipped runtime may import
    or open ``tests/`` or ``tools/`` — otherwise dropping ``tests/**`` would
    silently remove a real runtime import."""
    patterns = (
        re.compile(r"^\s*from\s+tests\b", re.M),
        re.compile(r"^\s*import\s+tests\b", re.M),
        re.compile(r"['\"]tests/"),
        re.compile(r"^\s*from\s+tools\b", re.M),
        re.compile(r"^\s*import\s+tools\b", re.M),
        re.compile(r"['\"]tools/"),
    )
    offenders: list[str] = []
    for directory in RUNTIME_DIRECTORIES:
        base = REPO_ROOT / directory
        assert base.is_dir(), base
        for path in sorted(base.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    line = text.count("\n", 0, match.start()) + 1
                    offenders.append(
                        f"{path.relative_to(REPO_ROOT)}:{line}: {match.group(0)}"
                    )
    assert offenders == [], offenders


def test_old_public_callers_keep_their_signatures():
    assert list(inspect.signature(installable_files).parameters) == ["root"]
    assert list(inspect.signature(manifest).parameters) == ["root"]
    assert list(inspect.signature(installation_diff).parameters) == [
        "canonical",
        "destination",
    ]
    assert list(inspect.signature(sync_installation).parameters) == [
        "canonical",
        "destination",
    ]
    assert list(inspect.signature(import_installation).parameters) == [
        "source",
        "canonical",
    ]
    assert list(inspect.signature(unique_destinations).parameters) == ["destinations"]
    assert list(inspect.signature(main).parameters) == []
    assert SKILL_NAME == "revenue-forecast"


# ---------------------------------------------------------------------------
# 2. diff compares only the responsible runtime
# ---------------------------------------------------------------------------


def test_diff_ignores_repository_only_residue_but_tracks_owned_files():
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        canonical = _skill(root / "canonical", "one")
        destination = root / "installed"
        target = _skill(destination / SKILL_NAME, "one")

        # old repository-only residue left by a previous installation
        residue = target / "tests" / "test_engineering_gate.py"
        residue.write_text("from tools import pre_push_gate\n", encoding="utf-8")
        unknown = target / "config" / "user_local.json"
        unknown.write_text("{}\n", encoding="utf-8")

        assert installation_diff(canonical, destination) == []

        # an owned file that is missing is drift
        (target / "scripts" / "scripts.py").unlink()
        differences = installation_diff(canonical, destination)
        assert differences == ["scripts/scripts.py"], differences

        # an owned file with different bytes is drift
        (target / "scripts" / "scripts.py").write_text(
            "scripts = 'one'\n", encoding="utf-8"
        )
        (target / "references" / "references.py").write_text(
            "references = 'tampered'\n", encoding="utf-8"
        )
        differences = installation_diff(canonical, destination)
        assert "references/references.py" in differences, differences
        assert "tests/test_engineering_gate.py" not in differences
        assert "config/user_local.json" not in differences


# ---------------------------------------------------------------------------
# 3. check writes nothing; explicit sync is a targeted, preserving update
# ---------------------------------------------------------------------------


def test_check_mode_writes_zero_files(monkeypatch):
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        canonical = _skill(root / "canonical", "one")
        destination = root / "installed"
        _skill(destination / SKILL_NAME, "stale")
        (destination / SKILL_NAME / "output").mkdir()
        (destination / SKILL_NAME / "output" / "forecast.json").write_text(
            "{}\n", encoding="utf-8"
        )
        before = _snapshot(destination)
        canonical_before = _snapshot(canonical)

        monkeypatch.setattr(
            sys,
            "argv",
            [
                "sync_installations.py",
                "--canonical",
                str(canonical),
                "--destination",
                str(destination),
            ],
        )
        main()

        assert _snapshot(destination) == before
        assert _snapshot(canonical) == canonical_before


def test_sync_updates_owned_files_and_preserves_everything_else():
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        canonical = _skill(root / "canonical", "new")
        destination = root / "installed"
        target = _skill(destination / SKILL_NAME, "stale")

        output = target / "output"
        output.mkdir()
        artifact = output / "forecast.json"
        artifact.write_text('{"keep": true}\n', encoding="utf-8")
        user_config = target / "config" / "user_local.json"
        user_config.write_text('{"mine": true}\n', encoding="utf-8")
        residue = target / "tests" / "test_engineering_gate.py"
        residue.write_text("from tools import pre_push_gate\n", encoding="utf-8")
        user_notes = target / "NOTES.md"
        user_notes.write_text("do not delete\n", encoding="utf-8")

        sync_installation(canonical, destination)

        # owned file updated in place
        assert (target / "scripts" / "scripts.py").read_text(
            encoding="utf-8"
        ) == "scripts = 'new'\n"
        # unknown files, user configuration, output and residue preserved
        assert artifact.read_text(encoding="utf-8") == '{"keep": true}\n'
        assert user_config.read_text(encoding="utf-8") == '{"mine": true}\n'
        assert residue.read_text(encoding="utf-8") == (
            "from tools import pre_push_gate\n"
        )
        assert user_notes.read_text(encoding="utf-8") == "do not delete\n"
        assert installation_diff(canonical, destination) == []


# ---------------------------------------------------------------------------
# 4. E2E: a tmp installation runs the real entry points without tools/
# ---------------------------------------------------------------------------


def _run(path: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(path), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
        cwd=str(path.parents[1]),
    )


def test_tmp_installation_runs_public_entry_without_repository_tools():
    with TemporaryDirectory() as temporary:
        destination = Path(temporary) / "skills"
        sync_installation(REPO_ROOT, destination)
        target = destination / SKILL_NAME

        assert not (target / "tools").exists()
        assert not (target / "tests").exists()
        assert not (target / "assurance").exists()
        assert (target / "SKILL.md").is_file()
        assert (target / "scripts" / "revenue_forecast.py").is_file()
        assert (target / "references" / "input-schema.md").is_file()

        entry = target / "scripts" / "revenue_forecast.py"
        help_run = _run(entry, "--help")
        assert help_run.returncode == 0, help_run.stderr[-800:]
        assert "usage" in (help_run.stdout + help_run.stderr).lower()

        version_run = _run(entry, "--version")
        assert version_run.returncode == 0, version_run.stderr[-800:]
        assert version_run.stdout.startswith("revenue-forecast ")

        template = target / "scripts" / "generate_input_template.py"
        generated = Path(temporary) / "template.json"
        template_run = _run(
            template,
            "--name",
            "Acme",
            "--base-year",
            "2025",
            "--forecast-years",
            "2026",
            "2027",
            "--segments",
            "Devices",
            "--output",
            str(generated),
        )
        assert template_run.returncode == 0, template_run.stderr[-800:]
        assert generated.is_file()
        rendered = generated.read_text(encoding="utf-8")
        assert "Acme" in rendered
        assert isinstance(json.loads(rendered), dict)


def test_missing_runtime_dependency_fails_loudly():
    with TemporaryDirectory() as temporary:
        destination = Path(temporary) / "skills"
        sync_installation(REPO_ROOT, destination)
        target = destination / SKILL_NAME
        entry = target / "scripts" / "revenue_forecast.py"
        assert _run(entry, "--version").returncode == 0

        (target / "scripts" / "revenue_core.py").unlink()
        broken = _run(entry, "--version")
        assert broken.returncode != 0
        assert "revenue_core" in (broken.stderr + broken.stdout)


def test_import_installation_still_preserves_repository_only_tools():
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        source = _skill(root / "source", "new")
        canonical = _skill(root / "canonical", "old")
        tools = canonical / "tools"
        tools.mkdir()
        repository_only = tools / "keep.py"
        repository_only.write_text("KEEP = True\n", encoding="utf-8")

        import_installation(source, canonical)

        assert manifest(canonical) == manifest(source)
        assert repository_only.read_text(encoding="utf-8") == "KEEP = True\n"
        assert (canonical / "tools" / "keep.py").is_file()


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
