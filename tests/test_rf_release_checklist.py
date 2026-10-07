"""Release checklist is a thin delegation point, judged by real return codes.

C1  the removed rites are really gone: no ``EXPECTED_RED`` pytest
    exemption, no FAILED-line parsing, no frozen schema-migration document,
    no ``sync_installations`` MATCH/--apply, no mutation patrol sweep.
C2  the checklist delegates to checks that already exist and never spawns
    its own copy of the full test suite.
C3  a delegate that exits non-zero — including pytest's collection-error
    code 2, which prints no ``FAILED`` line — blocks the release.
C4  the real CLI runs green end to end and a real gate failure is loud.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import release_checklist as rc  # noqa: E402

TOOL = ROOT / "tools" / "release_checklist.py"


def _source() -> str:
    return TOOL.read_text(encoding="utf-8")


def _cli(timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(TOOL)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(ROOT),
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# C1 — the removed per-release rites are gone
# ---------------------------------------------------------------------------


def test_c1_no_expected_red_exemption():
    source = _source()
    assert "EXPECTED_RED" not in source
    assert '"FAILED"' not in source
    assert "'FAILED'" not in source


def test_c1_no_frozen_migration_document_requirement():
    assert "schema-migration-3.6-to-3.7" not in _source()


def test_c1_no_install_sync_or_mutation_as_release_qualification():
    source = _source()
    assert "sync_installations" not in source
    assert "mutation_patrol" not in source


def test_c1_no_receipt_or_authorization_gate():
    source = _source()
    assert "release_authorization" not in source
    assert "issue-auth" not in source


# ---------------------------------------------------------------------------
# C2 — thin delegation to checks that already exist
# ---------------------------------------------------------------------------


def test_c2_delegates_to_the_existing_checks():
    labels = [label for label, _args in rc._delegates()]
    assert "pre-push gate" in labels
    assert "release readiness" in labels
    joined = " ".join(
        " ".join(str(part) for part in args) for _label, args in rc._delegates()
    )
    assert "pre_push_gate.py" in joined
    assert "release_readiness.py" in joined


def test_c2_delegation_does_not_spawn_its_own_pytest():
    for _label, args in rc._delegates():
        assert "pytest" not in [str(part) for part in args], args


def test_c2_every_delegate_is_an_existing_file():
    for label, args in rc._delegates():
        script = next(
            (
                part
                for part in args
                if isinstance(part, Path) and str(part).endswith(".py")
            ),
            None,
        )
        assert script is not None, label
        assert script.is_file(), (label, script)


# ---------------------------------------------------------------------------
# C3 — real return codes decide
# ---------------------------------------------------------------------------


def test_c3_changelog_check_matches_the_real_version():
    assert rc._changelog_problem() is None


def test_c3_delegate_exit_two_blocks_without_any_failed_line(monkeypatch, capsys):
    monkeypatch.setattr(rc, "_changelog_problem", lambda: None)
    monkeypatch.setattr(
        rc,
        "_delegates",
        lambda: [("collection error", [sys.executable, "-c", "raise SystemExit(2)"])],
    )
    assert rc.main([]) == 1
    out = capsys.readouterr().out
    assert "RELEASE-BLOCK" in out
    assert "FAILED" not in out
    assert "exit code 2" in out


def test_c3_green_delegates_pass(monkeypatch, capsys):
    monkeypatch.setattr(rc, "_changelog_problem", lambda: None)
    monkeypatch.setattr(
        rc,
        "_delegates",
        lambda: [("green", [sys.executable, "-c", "raise SystemExit(0)"])],
    )
    assert rc.main([]) == 0
    assert "OK:" in capsys.readouterr().out


def test_c3_changelog_problem_blocks(monkeypatch, capsys):
    monkeypatch.setattr(
        rc, "_changelog_problem", lambda: "CHANGELOG has no release section"
    )
    monkeypatch.setattr(rc, "_delegates", lambda: [])
    assert rc.main([]) == 1
    assert "RELEASE-BLOCK" in capsys.readouterr().out


def test_c3_unknown_argument_is_a_configuration_error():
    proc = subprocess.run(
        [sys.executable, "-B", str(TOOL), "--not-a-real-flag"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(ROOT),
        timeout=60,
    )
    assert proc.returncode == 2


# ---------------------------------------------------------------------------
# C4 — the real CLI
# ---------------------------------------------------------------------------


def test_c4_cli_green_end_to_end():
    proc = _cli()
    out = proc.stdout + proc.stderr
    hint = (
        " (the daily gate expects the sibling checkouts: set "
        "FF_V2_CODE_ROOT / CWP_V2_CODE_ROOT, or place filing-fetch and "
        "company-wiki next to this repository)"
    )
    assert proc.returncode == 0, out[-4000:] + hint
    assert "OK:" in out
    for marker in ("pre-push gate", "release readiness"):
        assert marker in out, marker


def test_c4_cli_reports_a_real_gate_failure_loudly():
    probe = ROOT / "tests" / "_g2_ruff_probe.py"
    probe.write_text("import os\n", encoding="utf-8")
    try:
        proc = _cli(timeout=300)
    finally:
        if probe.exists():
            probe.unlink()
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, out[-4000:]
    assert "RELEASE-BLOCK" in out
    assert "ruff" in out.lower()


@pytest.fixture(autouse=True)
def _probe_is_removed():
    yield
    probe = ROOT / "tests" / "_g2_ruff_probe.py"
    if probe.exists():
        probe.unlink()
