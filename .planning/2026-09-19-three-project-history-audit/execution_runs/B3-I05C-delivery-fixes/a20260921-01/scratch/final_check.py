"""Final verification: JSON validity, hash stability, deliverable inventory."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
SKIP = ("scratch/runs", "scratch/mutants", "scratch/vacuity", "scratch/extra_")

failures = []
print("=== JSON validity ===")
for path in sorted(ATTEMPT.rglob("*.json")):
    rel = path.relative_to(ATTEMPT).as_posix()
    if any(rel.startswith(s) for s in SKIP):
        continue
    try:
        json.loads(path.read_text(encoding="utf-8"))
        print(f"  OK   {rel}")
    except Exception as exc:  # pragma: no cover
        failures.append(f"{rel}: {exc}")
        print(f"  FAIL {rel}: {exc}")

print("\n=== deliverable inventory ===")
REQUIRED = [
    "binding.json", "decision.md", "commands.json", "oracle.md",
    "changes.diff", "case_results.json", "handoff.json",
    "before/company_wiki_source.py", "before/artifact_dag.py",
    "after/source_hashes.json", "after/test_results.json",
    "after/integrity.json", "after/evidence_hashes.json",
]
for rel in REQUIRED:
    path = ATTEMPT / rel
    if path.is_file():
        sha = hashlib.sha256(path.read_bytes()).hexdigest().upper()
        print(f"  OK   {rel:38s} {sha[:12]} ({path.stat().st_size} bytes)")
    else:
        failures.append(f"missing deliverable {rel}")
        print(f"  MISS {rel}")

print("\n=== frozen-tree integrity ===")
for rel in ("iso/fixed/rf_scripts/company_wiki_source.py",
            "iso/fixed/tests/retry-count-vs-artifact-count.json",
            "iso/fixed/cw_source_catalog/artifact_dag.py"):
    sha = hashlib.sha256((ATTEMPT / rel).read_bytes()).hexdigest().upper()
    print(f"  {rel}\n      {sha}")

print("\n=== production read-only check ===")
PROD = {
    "RF scripts/company_wiki_source.py":
        Path("C:/Users/郑曾波/Projects/revenue-forecast/scripts/"
             "company_wiki_source.py"),
    "RF tests/test_fc904_artifact_selection.py":
        Path("C:/Users/郑曾波/Projects/revenue-forecast/tests/"
             "test_fc904_artifact_selection.py"),
    "CW artifact_dag.py":
        Path("C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/"
             "source_catalog/artifact_dag.py"),
}
EXPECTED = {
    "RF scripts/company_wiki_source.py":
        "225FECDD7E48938A97C68724318F0860602A4B86A8D9E834A257243480094294",
    "RF tests/test_fc904_artifact_selection.py":
        "8C0B8E390307C33B8C03D51FD742CA984BA6774B84638500FD8D7CDD7D46BF3F",
    "CW artifact_dag.py":
        "0C8B1D6D1A28C94F27EA8FFE52A98D67B84F0A49653931B9C9317E27DA6C20D1",
}
for label, path in PROD.items():
    sha = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    ok = sha == EXPECTED[label]
    if not ok:
        failures.append(f"production drift: {label}")
    print(f"  {'OK  ' if ok else 'DRIFT'} {label}")

print()
if failures:
    print("FAILURES:")
    for item in failures:
        print("  -", item)
    raise SystemExit(1)
print("ALL FINAL CHECKS PASSED")
