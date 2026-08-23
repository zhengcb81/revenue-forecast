"""Drift patrol (R6.4) — scheduled self-checks across versions, installations,
configs, docs, and dependencies.  Any red item -> exit code 1.

Checks:
  1. Version drift: Unreleased CHANGELOG entries older than 14 days (N-08).
  2. Installation drift: revenue sync check (all targets).
  3. Config drift: company-wiki config_doctor (adjacent checkout, when present).
  4. Doc drift: SKILL.md still references removed/legacy modules (R3 guard).
  5. Dependency drift: filing-fetch CLI contract snapshot vs installed copy.

Usage:
    python tools/drift_patrol.py [--json]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )


def check_version_drift() -> list[str]:
    """Unreleased entries older than 14 days are versioning debt (N-08)."""
    changelog = ROOT / "CHANGELOG.md"
    if not changelog.is_file():
        return ["CHANGELOG.md missing"]
    text = changelog.read_text(encoding="utf-8")
    if "Unreleased" not in text:
        return []
    problems: list[str] = []
    from datetime import date

    today = date.today()
    for match in re.finditer(r"(\d{4}-\d{2}-\d{2})", text):
        year, month, day = map(int, match.groups()[0].split("-"))
        age = (today - date(year, month, day)).days
        if age > 14:
            problems.append(
                f"CHANGELOG entry {match.group(1)} is {age} days old while still "
                "marked Unreleased — bump the version (R7 discipline)"
            )
            break
    return problems


def check_installation_drift() -> list[str]:
    completed = _run(
        [sys.executable, str(ROOT / "tools" / "sync_installations.py")], ROOT
    )
    if completed.returncode != 0:
        return ["installation sync drift:" + completed.stdout[-400:]]
    return []


def check_config_drift() -> list[str]:
    wiki = ROOT.parent / "company-wiki"
    doctor = wiki / "scripts" / "config_doctor.py"
    if not doctor.is_file():
        return []  # company-wiki not checked out; nothing to verify
    completed = _run([sys.executable, str(doctor)], wiki)
    if completed.returncode != 0:
        return ["company-wiki config unhealthy:" + completed.stdout[-400:]]
    return []


def check_doc_drift() -> list[str]:
    skill = ROOT / "SKILL.md"
    if skill.is_file() and "filing_acquisition" in skill.read_text(encoding="utf-8"):
        return ["SKILL.md still references the removed legacy filing owner (R3)"]
    return []


def check_dependency_drift() -> list[str]:
    filing = ROOT.parent / "filing-fetch"
    if not (filing / "scripts" / "filing_fetch_client.py").is_file():
        return []  # filing-fetch not checked out; nothing to verify
    client = ROOT / "scripts" / "filing_fetch_client.py"
    canonical = client.read_text(encoding="utf-8") if client.is_file() else ""
    installed = (filing / "scripts" / "filing_fetch_client.py").read_text(
        encoding="utf-8"
    )
    if canonical and canonical != installed:
        return ["filing-fetch client contract drifted from revenue's copy"]
    return []


# --- ZR-907: schema version literal + manifest reference-hash gates ---------

# "3.6" was purged from docs/help by ZR-703; the only legal remaining
# occurrences are the SUPPORTED/EMIT enums in constants.py and
# schema_compatibility.py (schema source of truth).
KNOWN_LEGACY_SCHEMAS = ("3.6",)
SCHEMA_SOURCE_FILES = {"constants.py", "schema_compatibility.py"}


def check_schema_drift() -> list[str]:
    """Stale 'schema 3.6' doc/help literals outside the schema source files
    are drift (ZR-703 cleaned them once; this gate keeps them gone)."""
    problems: list[str] = []
    for path in sorted((ROOT / "scripts").rglob("*.py")):
        if path.name in SCHEMA_SOURCE_FILES:
            continue
        for number, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r'["\']3\.6["\']', line):
                problems.append(
                    f"{path.relative_to(ROOT)}:{number}: stale schema "
                    f"literal '3.6'")
    return problems


def check_manifest_drift() -> list[str]:
    """Referenced-file hashes must match the machine manifest (uc)."""
    uc_root = ROOT / "assurance" / "unified_completion"
    completed = _run(
        [sys.executable, "-m", "uc.cli", "manifest-verify"], uc_root
    )
    if completed.returncode != 0:
        return ["machine manifest drift:" + (completed.stderr or completed.stdout)[-300:]]
    return []


def patrol() -> list[dict]:
    checks = {
        "version": check_version_drift,
        "installation": check_installation_drift,
        "config": check_config_drift,
        "docs": check_doc_drift,
        "dependencies": check_dependency_drift,
        "schema": check_schema_drift,      # ZR-907
        "manifest": check_manifest_drift,  # ZR-907
    }
    results = []
    for name, fn in checks.items():
        problems = fn()
        results.append({"check": name, "problems": problems, "ok": not problems})
    return results


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):  # pragma: no cover - non-reconfigurable
        pass
    parser = argparse.ArgumentParser(description="Drift patrol (R6.4)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    results = patrol()
    problems = [entry for entry in results if entry["problems"]]
    if args.json:
        print(json.dumps({"ok": not problems, "results": results}, indent=2, sort_keys=True))
        return 1 if problems else 0
    for entry in results:
        marker = "OK  " if not entry["problems"] else "FAIL"
        print(f"{marker} {entry['check']}")
        for problem in entry["problems"]:
            print(f"     {problem}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
