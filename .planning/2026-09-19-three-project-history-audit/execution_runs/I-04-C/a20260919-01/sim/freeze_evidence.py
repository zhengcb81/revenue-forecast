"""Freeze the attempt evidence: hashes of every artifact + a machine summary.

Run last; writes evidence/hashes.txt and evidence/run-summary.json.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

ATTEMPT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTION = r"C:\Users\郑曾波\Projects\filing-fetch\scripts\fetch_filing.py"
EXPECTED_PRODUCTION = "046cc7dc4e3ff2f4f59be05def8961a85a12e6290adef43a3c53103c63b9d088"


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def walk(root):
    for base, _dirs, files in os.walk(root):
        for name in sorted(files):
            yield os.path.join(base, name)


def main():
    lines = []
    # 1. the frozen design inputs
    for relative in ("binding.json", "oracle.md", "decision.md", "commands.json"):
        path = os.path.join(ATTEMPT, relative)
        if os.path.exists(path):
            lines.append(f"{sha256(path)}  {relative}")
    # 2. the simulation harness
    sim = os.path.join(ATTEMPT, "sim")
    for path in walk(sim):
        if path.endswith(".pyc"):
            continue
        lines.append(f"{sha256(path)}  sim/{os.path.relpath(path, sim).replace(os.sep, '/')}")
    # 3. raw evidence (top level only; per-case dirs are listed separately)
    evidence = os.path.join(ATTEMPT, "evidence")
    for path in walk(evidence):
        if os.sep + "run" + os.sep in path:
            continue
        lines.append(f"{sha256(path)}  evidence/{os.path.relpath(path, evidence).replace(os.sep, '/')}")
    # 4. the production truth
    production_hash = sha256(PRODUCTION)
    lines.append(f"{production_hash}  PRODUCTION filing-fetch/scripts/fetch_filing.py")
    lines.append(f"{EXPECTED_PRODUCTION}  EXPECTED production hash (card anchor)")
    lines.append("PRODUCTION_UNCHANGED=" + str(production_hash == EXPECTED_PRODUCTION).lower())
    with open(os.path.join(evidence, "hashes.txt"), "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")

    summary = {
        "attempt": "I-04-C/a20260919-01",
        "production_hash": production_hash,
        "production_unchanged": production_hash == EXPECTED_PRODUCTION,
        "artifacts_hashed": len(lines) - 2,
    }
    with open(os.path.join(evidence, "run-summary.json"), "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=1, sort_keys=True)
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["production_unchanged"] else 1


if __name__ == "__main__":
    sys.exit(main())
