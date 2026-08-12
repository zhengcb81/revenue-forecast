"""FC-1101: PR current-triplet gate — CI manifests must be manifest-driven.

SCENARIO: CTRL-05 (sibling drift fails red)

The CI workflows must consume the compatibility manifest's ``current_triplet``
— never hardcoded 40-hex sibling pins (revenue ad62592/77669ae and filing
a42bb40 were the pre-FC-1101 pins) and never floating main.  The gate scans
the workflow YAMLs for hardcoded pins and asserts the manifest-driven
checkout tool is wired in.  M1 (reverting to a hardcoded pin) kills the gate.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SHA1 = re.compile(r"[0-9a-f]{7,40}")  # full or abbreviated pins


def _workflow_files() -> list[tuple[str, Path]]:
    files = []
    for repo, rel in (
        ("revenue-forecast", "revenue-forecast/.github/workflows/quality.yml"),
        ("filing-fetch", "filing-fetch/.github/workflows/quality.yml"),
    ):
        p = PROJECT_ROOT.parent / rel
        if p.is_file():
            files.append((repo, p))
    return files


class TestCiManifestGate(unittest.TestCase):
    def test_no_hardcoded_sibling_pins(self):
        for repo, path in _workflow_files():
            text = path.read_text(encoding="utf-8")
            hits = SHA1.findall(text)
            self.assertEqual(
                hits, [],
                f"{repo} workflow hardcodes sibling commits: {hits[:3]} — "
                "FC-1101 requires manifest-driven checkout",
            )

    def test_manifest_driven_checkout_wired(self):
        for repo, path in _workflow_files():
            text = path.read_text(encoding="utf-8")
            self.assertIn("ci_checkout_siblings.py", text,
                          f"{repo} workflow must call the manifest-driven checkout")

    def test_manifest_triplet_matches_heads(self):
        """The manifest's current_triplet must equal the three repos' HEADs
        (drift fails red — the CI sibling checkout would pin stale code)."""
        manifest = json.loads(
            (PROJECT_ROOT / "compatibility" / "current.json").read_text(
                encoding="utf-8"))
        for repo, name in (("revenue", "revenue-forecast"),
                           ("filing", "filing-fetch"),
                           ("wiki", "company-wiki")):
            head = subprocess.run(
                ["git", "-C", str(PROJECT_ROOT.parent / name), "rev-parse", "HEAD"],
                capture_output=True, text=True).stdout.strip()
            self.assertEqual(manifest["current_triplet"][repo], head,
                             f"manifest {repo} triplet drifted from HEAD")

    def test_checkout_tool_requires_manifest(self):
        proc = subprocess.run(
            [sys.executable, "-B",
             str(PROJECT_ROOT / "tools" / "ci_checkout_siblings.py")],
            capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(proc.returncode, 0, "--manifest is required")


if __name__ == "__main__":
    unittest.main()
