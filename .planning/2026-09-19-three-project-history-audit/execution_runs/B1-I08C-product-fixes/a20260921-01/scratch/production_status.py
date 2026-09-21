"""Production status: hashes + `git status --porcelain` for the read-only scope.

Never writes inside the production tree.  Never runs a git WRITE command.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

PROD = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()

SCOPE = ["scripts", "tests", "config", "artifacts"]
rels = [
    "scripts/revenue_publication.py",
    "scripts/revenue_core.py",
    "scripts/revenue_report.py",
    "scripts/contracts/evidence.py",
    "scripts/contracts/document.py",
    "scripts/forecast/segments.py",
    "scripts/publication_registry.py",
    "tests/test_attestation.py",
    "tests/test_recognition_bridge.py",
    "tests/test_data_contract.py",
    "config/trusted_signer_public_keys.json",
    "artifacts/registry/publications.jsonl",
]

lines: list[str] = []
lines.append(f"production_root = {PROD}")
lines.append("")
lines.append("--- file hashes (read-only re-hash after every bound command) ---")
for rel in rels:
    path = PROD / rel.replace("/", "\\")
    if path.is_file():
        data = path.read_bytes()
        lines.append(f"{hashlib.sha256(data).hexdigest()}  {len(data):>8}  {rel}")
    else:
        lines.append(f"{'ABSENT':<64}  {'-':>8}  {rel}")

lines.append("")
lines.append("--- git status --porcelain (scope: scripts/ tests/ config/ artifacts/) ---")
status = subprocess.run(
    ["git", "status", "--porcelain", "--", *SCOPE],
    cwd=str(PROD),
    capture_output=True,
    check=False,
    text=True,
)
lines.append(f"argv = ['git','status','--porcelain','--',{', '.join(repr(s) for s in SCOPE)}]")
lines.append(f"raw_returncode = {status.returncode}")
lines.append(f"stdout = {status.stdout!r}")
lines.append(f"stderr = {status.stderr!r}")

head = subprocess.run(
    ["git", "rev-parse", "HEAD"], cwd=str(PROD), capture_output=True, check=False, text=True
)
lines.append(f"git_head = {head.stdout.strip()!r} (rc {head.returncode})")

lines.append("")
lines.append("--- git write commands executed by this card ---")
lines.append("NONE (no add / commit / restore / stash / checkout)")

text = "\n".join(lines) + "\n"
OUT.write_text(text, encoding="utf-8")
print(text)
