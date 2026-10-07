"""Release checklist (R7) — one thin delegation point for shipping a version.

Nothing here re-implements a check.  Each delegate is an existing tool and
its REAL return code decides, so a pytest that exits 2 (collection error),
fails to launch, or times out blocks the release even when it printed no
``FAILED`` line.

Delegates, in order:

  1. ``CHANGELOG`` carries a section for the current ``SKILL_VERSION``
     (a real content/config error, not a document-presence rite);
  2. ``tools/pre_push_gate.py`` — the shared daily offline gate;
  3. ``tools/release_readiness.py`` — read-only optional readiness;
  4. ``scripts/publication_registry.py audit`` — read-only registry audit.

Deliberately NOT per-release qualification any more (each stays an explicit,
standalone command): the fixed pytest red-exemption allowance, the frozen
historical migration document, the installation-copy MATCH/apply rite, and the
mutation sweep.  The full test suite is not copied here — run it as an
explicit central command when a milestone needs it.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from revenue_core import SKILL_VERSION  # noqa: E402


def _delegate(args: list[str | Path], label: str, timeout: int = 900) -> int:
    """Run one existing check and return its real exit code."""
    print(f"=== {label} ===")
    try:
        proc = subprocess.run(
            [str(part) for part in args],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        print(f"{label} timed out after {timeout}s")
        return 1
    except OSError as exc:
        print(f"{label} could not start: {exc}")
        return 1
    tail = (proc.stdout or "")[-2000:] + (proc.stderr or "")[-1000:]
    print(tail.rstrip()[-1200:] or "ok")
    if proc.returncode != 0:
        print(f"{label} returned exit code {proc.returncode}")
    return proc.returncode


def _changelog_problem() -> str | None:
    changelog = ROOT / "CHANGELOG.md"
    try:
        text = changelog.read_text(encoding="utf-8")
    except OSError as exc:
        return f"CHANGELOG unreadable: {exc}"
    release_heading = f"## {SKILL_VERSION} "
    if release_heading not in text:
        return (
            f"CHANGELOG has no release section for {SKILL_VERSION} "
            "(Unreleased entries must be closed into a versioned section)"
        )
    return None


def _delegates() -> list[tuple[str, list[str | Path]]]:
    return [
        ("pre-push gate", [sys.executable, ROOT / "tools" / "pre_push_gate.py"]),
        (
            "release readiness",
            [
                sys.executable,
                "-B",
                ROOT / "tools" / "release_readiness.py",
            ],
        ),
        (
            "publication registry audit",
            [
                sys.executable,
                ROOT / "scripts" / "publication_registry.py",
                "audit",
            ],
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Release checklist (R7): thin delegation, real exit codes"
    )
    parser.parse_args(argv)
    problems: list[str] = []
    changelog_problem = _changelog_problem()
    if changelog_problem:
        problems.append(changelog_problem)
    for label, args in _delegates():
        exit_code = _delegate(args, label)
        if exit_code != 0:
            problems.append(f"{label} returned exit code {exit_code}")
    for problem in problems:
        print(f"RELEASE-BLOCK: {problem}")
    if not problems:
        print(f"OK: {SKILL_VERSION} is releasable")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
