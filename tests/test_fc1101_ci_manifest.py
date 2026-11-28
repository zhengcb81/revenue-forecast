"""FC-1101: check out the exact composition pins using real offline Git."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from test_compatibility_manifest import ancestry_fixture, fixture_git


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHECKOUT_TOOL = PROJECT_ROOT / "tools" / "ci_checkout_siblings.py"
SHA1 = re.compile(r"\b[0-9a-f]{7,40}\b")
OWNER_DIRECTORY = {"revenue": "revenue-forecast", "filing": "filing-fetch", "wiki": "company-wiki"}


def test_owner_workflow_has_no_hardcoded_sibling_pins():
    text = (PROJECT_ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
    assert not SHA1.findall(text)


def test_pin_scan_catches_abbreviated_pins():
    assert SHA1.search("git checkout ad62592")
    assert SHA1.search("git checkout " + "a" * 40)
    assert not SHA1.search("python tools/ci_checkout_siblings.py")


def test_composition_cli_selects_real_pins_even_when_supplier_heads_are_newer(tmp_path):
    with ancestry_fixture() as (record, local_remotes):
        pinned = record["frozen_baseline_triplet"]
        manifest = tmp_path / "manifest.json"
        manifest.write_text(
            json.dumps({"current_triplet": pinned,
                        "remotes": {owner: str(path) for owner, path in local_remotes.items()}}),
            encoding="utf-8",
        )
        target = tmp_path / "checkout"
        target.mkdir()
        proc = subprocess.run(
            [sys.executable, "-B", str(CHECKOUT_TOOL), "--manifest", str(manifest), "--sibling-root", str(target)],
            stdin=subprocess.DEVNULL, capture_output=True, timeout=75,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")
        for owner, name in OWNER_DIRECTORY.items():
            assert fixture_git(target / name, "rev-parse", "HEAD") == pinned[owner]
            assert fixture_git(local_remotes[owner], "rev-parse", "HEAD") == record["current_triplet"][owner]
            assert record["current_triplet"][owner] != pinned[owner]


def test_checkout_tool_requires_manifest():
    proc = subprocess.run(
        [sys.executable, "-B", str(CHECKOUT_TOOL)], stdin=subprocess.DEVNULL,
        capture_output=True, text=True, timeout=30,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    assert proc.returncode == 2
    assert "--manifest" in proc.stderr
