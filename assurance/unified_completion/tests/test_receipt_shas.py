"""Regression guard against fabricated git shas in receipts.

Every 40-hex value in a receipt's triplet/commit fields must resolve to a
real git object in the CORRECT repository (revenue / filing / wiki).
Fabricated shas already slipped through twice (CA-003's b06cfbfc…, CA-004's
f4320231d3b3…); this test makes a third impossible.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from conftest import REPO_ROOT

RECEIPTS_DIR = REPO_ROOT / "assurance" / "unified_completion" / "receipts"
REPOS = {
    "revenue": REPO_ROOT,
    "filing": REPO_ROOT.parent / "filing-fetch",
    "wiki": REPO_ROOT.parent / "company-wiki",
}
# Fields whose 40-hex values are git objects (not content hashes).
GIT_SHA_FIELDS = ("base_triplet", "result_triplet")


def _git_object_exists(repo: Path, sha: str) -> bool:
    proc = subprocess.run(
        ["git", "-C", str(repo), "cat-file", "-t", sha],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    return proc.returncode == 0


def _walk(obj, path: str):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from _walk(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            yield from _walk(value, f"{path}[{index}]")
    else:
        yield path, obj


def test_receipt_triplet_shas_are_real_git_objects():
    problems: list[str] = []
    for receipt_path in sorted(RECEIPTS_DIR.rglob("*.json")):
        try:
            # Reviewer receipts may carry a UTF-8 BOM from PowerShell writes.
            payload = json.loads(receipt_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{receipt_path.name}: unreadable ({exc})")
            continue
        for field in GIT_SHA_FIELDS:
            for path, value in _walk(payload.get(field, {}), field):
                if not (
                    isinstance(value, str)
                    and len(value) == 40
                    and all(ch in "0123456789abcdef" for ch in value)
                ):
                    continue
                repo_key = path.split(".")[1] if "." in path else ""
                repo = REPOS.get(repo_key)
                if repo is None or not _git_object_exists(repo, value):
                    problems.append(
                        f"{receipt_path.name}: fabricated sha at {path}: {value}"
                    )
        indexed = payload.get("codegraph", {}).get("indexed_commit")
        if isinstance(indexed, dict):
            for repo_name, value in indexed.items():
                repo = REPOS.get(repo_name)
                if (
                    isinstance(value, str)
                    and len(value) == 40
                    and (repo is None or not _git_object_exists(repo, value))
                ):
                    problems.append(
                        f"{receipt_path.name}: fabricated indexed_commit "
                        f"for {repo_name}: {value}"
                    )
    assert problems == [], "; ".join(problems)
