"""Legacy gate isolation (CA-109).

The old closure tools may only survive as MIGRATION READERS or be explicitly
replaced.  This module scans the three repos' workflow/hook/tool surface for
callers; legacy tools' own files and their tests are excluded (they are the
subject, not callers).  Every remaining reference becomes a registered
finding with a successor work unit (CI rewiring belongs to CA-201 per the
frozen plan).  Historical ledgers remain read-only display.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

LEGACY_TOOLS = (
    "closure_gate",
    "receipt_validator",
    "scenario_coverage",
    "verify_closure_ledger",
    "closure_ledger",
)

LEGACY_TOOL_FILES = {
    "closure_gate.py",
    "receipt_validator.py",
    "verify_closure_ledger.py",
    "closure_ledger.py",
}

SCAN_DIRS = (".github", ".githooks", "tools", "scripts", "e2e")


def scan_callers(repo_roots: dict[str, Path]) -> dict[str, Any]:
    """Find references to legacy gate tools in gate-relevant files, excluding
    the legacy tools themselves and their test suites."""
    callers: dict[str, list[dict[str, Any]]] = {}
    for repo_name, root in repo_roots.items():
        for rel in SCAN_DIRS:
            base = root / rel
            if not base.is_dir():
                continue
            for path in sorted(base.rglob("*")):
                if not path.is_file():
                    continue
                if path.name in LEGACY_TOOL_FILES or "test" in path.name.lower():
                    continue
                if path.suffix not in (".yml", ".yaml", ".py", ".sh", ""):
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                for tool in LEGACY_TOOLS:
                    if tool in text:
                        lines = [
                            i + 1
                            for i, line in enumerate(text.splitlines())
                            if tool in line
                        ]
                        callers.setdefault(repo_name, []).append(
                            {
                                "file": str(path.relative_to(root)),
                                "tool": tool,
                                "lines": lines,
                            }
                        )
    return callers


def classify(callers: dict[str, Any]) -> dict[str, Any]:
    """Every caller becomes a registered finding with a successor (CI rewiring
    is CA-201 scope; nothing here silently passes)."""
    findings: list[dict[str, Any]] = []
    for repo_name, references in sorted(callers.items()):
        for reference in references:
            findings.append(
                {
                    "id": f"LEGACY-CALLER-{len(findings) + 1:03d}",
                    "repo": repo_name,
                    "file": reference["file"],
                    "tool": reference["tool"],
                    "lines": reference["lines"],
                    "severity": "P2",
                    "successor": "CA-201",
                    "summary": (
                        "legacy closure tool referenced outside its own files; "
                        "CI/production rewiring belongs to CA-201"
                    ),
                }
            )
    return {
        "callers": callers,
        "findings": findings,
        "isolated": not findings,
    }


def report(repo_roots: dict[str, Path]) -> dict[str, Any]:
    verdict = classify(scan_callers(repo_roots))
    return {
        "schema_version": 1,
        "verdict": "isolated" if verdict["isolated"] else "callers_found",
        **verdict,
    }
