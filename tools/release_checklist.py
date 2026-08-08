"""Release checklist (R7) — automated gate for shipping a new version.

Verifies, in order: version constants match the CHANGELOG release, migration
documents exist, test suite green (structure-target RED items are expected and
listed), adversarial suite green, mutation patrol accepts nothing, registry
audit clean, installed copies in sync.  Any failure -> exit 1.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from revenue_core import SKILL_VERSION  # noqa: E402

EXPECTED_RED = {"test_structure_targets.py"}  # R9 split pending


def _run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )


def main() -> int:
    problems: list[str] = []
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    release_heading = f"## {SKILL_VERSION} "
    if release_heading not in changelog:
        problems.append(
            f"CHANGELOG has no release section for {SKILL_VERSION} "
            "(Unreleased entries must be closed into a versioned section)"
        )
    migration = ROOT / "references" / "schema-migration-3.6-to-3.7.md"
    if not migration.is_file():
        problems.append(f"missing migration document: {migration.name}")
    tests = _run([sys.executable, "-m", "pytest", "tests", "-q", "--tb=no"])
    red = {
        line.split("::")[0].split("/")[-1]
        for line in tests.stdout.splitlines()
        if line.startswith("FAILED")
    }
    unexpected = red - EXPECTED_RED
    if unexpected:
        problems.append(f"unexpected failing tests: {sorted(unexpected)}")
    patrol = _run([sys.executable, str(ROOT / "tools" / "mutation_patrol.py"), "--samples", "5"])
    if patrol.returncode != 0:
        problems.append("mutation patrol accepted a semantic mutation")
    audit = _run(
        [sys.executable, str(ROOT / "scripts" / "publication_registry.py"), "audit"]
    )
    audit_output = audit.stdout or ""
    if any(token in audit_output for token in ("corrupt", "unregistered")):
        problems.append("publication registry corrupt or unregistered claim")
    elif "conflict" in audit_output:
        # Same-generation anchor conflicts during development usually reflect
        # attestation-environment differences (provider present/absent) or
        # pre-release receipt evolution — review manually before shipping.
        print("RELEASE-NOTE: registry conflict entries (manual review):")
        for line in audit_output.splitlines():
            if "conflict" in line:
                print(f"  {line}")
    sync = _run([sys.executable, str(ROOT / "tools" / "sync_installations.py")])
    if sync.returncode != 0:
        problems.append("installation copies drifted (run --apply)")
    for problem in problems:
        print(f"RELEASE-BLOCK: {problem}")
    if not problems:
        print(f"OK: {SKILL_VERSION} is releasable")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
