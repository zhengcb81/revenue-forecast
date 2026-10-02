"""Review-side independent recomputation of the FC-1204 gate metric.

Imports the gate's OWN `_max_complexity` / `_mccabe` from
tests/contract/test_fc1204_complexity_ratchet.py so the number is not
re-implemented (no drift between reviewer and gate).

All hashes are over RAW FILE BYTES (`read_bytes()`), matching `Get-FileHash`.
NOTE: observability.py is the one target that carries CRLF in the working copy,
so its raw-byte hash (18DDCEC4…) differs from its LF-normalised hash
(C2622DC3…); the LF-normalised value is the one that matches the carrier's
post_image and the `git diff` blob, because git normalises on checkout.
Columns below print BOTH so no reader is misled.

Read-only. Writes nothing into company-wiki.
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
SRC = WIKI / "src" / "company_wiki" / "source_catalog"
GATE = WIKI / "tests" / "contract" / "test_fc1204_complexity_ratchet.py"

spec = importlib.util.spec_from_file_location("fc1204_gate", GATE)
gate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(gate)

_max_complexity = gate._max_complexity
_mccabe = gate._mccabe
FROZEN_MAX = gate.FROZEN_MAX


def per_function(text: str) -> list[tuple[str, int]]:
    """(name, complexity) for every top-level FunctionDef, gate-style."""
    tree = ast.parse(text)
    out = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("test_"):
            seg = ast.get_source_segment(text, node) or ""
            out.append((node.name, 1 + _mccabe(ast.parse(seg))))
    return sorted(out, key=lambda kv: -kv[1])


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest().upper()


def hashes(p: Path) -> tuple[str, str]:
    raw = p.read_bytes()
    norm = raw.replace(b"\r\n", b"\n")
    return sha256_bytes(raw), sha256_bytes(norm)


TARGETS = [
    ("archive_retired_evidence.py", 7),
    ("observability.py", 6),
    ("prune_retired_evidence.py", 12),
    ("../../../tests/contract/test_observability.py", None),  # test-side face
]

report: dict[str, object] = {"gate_module": str(GATE), "files": {}}
files: dict[str, object] = {}

print("=" * 78)
print("A. CURRENT WORKING-TREE VALUES (gate metric _max_complexity)")
print("=" * 78)
for rel, frozen in TARGETS:
    p = (SRC / rel).resolve()
    if not p.exists():
        print(f"\n{rel}: NOT FOUND at {p}")
        continue
    text = p.read_text(encoding="utf-8")
    actual = _max_complexity(text)
    fns = per_function(text)
    raw_h, lf_h = hashes(p)
    print(f"\n{rel}")
    if frozen is None:
        print(f"  (test file — no frozen budget; source metric shown for context)")
    else:
        ok = actual <= frozen
        print(f"  frozen(<=) = {frozen}   actual = {actual}   "
              f"{'PASS' if ok else 'FAIL'}")
    print(f"  sha256 raw bytes (CRLF) = {raw_h}")
    print(f"  sha256 LF-normalised    = {lf_h}")
    print(f"  top functions: {fns[:6]}")
    files[rel] = {
        "frozen": frozen,
        "actual": actual,
        "pass": (actual <= frozen) if frozen is not None else None,
        "sha256_raw": raw_h,
        "sha256_lf": lf_h,
        "top_functions": fns,
        "frozen_table_value_matches_assignment":
            (FROZEN_MAX.get(rel) == frozen) if frozen is not None else None,
    }

report["files"] = files

print()
print("=" * 78)
print("B. HEAD (committed) VALUES — via `git show HEAD:<path>`")
print("=" * 78)
import subprocess

for rel, frozen in TARGETS[:3]:
    gitrel = f"src/company_wiki/source_catalog/{rel}"
    cp = subprocess.run(
        ["git", "-C", str(WIKI), "show", f"HEAD:{gitrel}"],
        capture_output=True,
    )
    if cp.returncode != 0:
        print(f"{rel}: git show failed rc={cp.returncode}")
        continue
    text = cp.stdout.decode("utf-8")
    actual = _max_complexity(text)
    print(f"{rel}: HEAD actual = {actual}  (frozen {frozen})  "
          f"top={per_function(text)[:4]}")
    files[rel]["head_actual"] = actual  # type: ignore[index]

print()
print("=" * 78)
print("C. UPSTREAM pre_image / post_image HASHES + METRIC")
print("=" * 78)
C_RUN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
         r"\2026-09-19-three-project-history-audit\execution_runs"
         r"\RATCHET-FIX-C\a20260927-01")
carrier: dict[str, dict[str, dict[str, object]]] = {}
for sub in ("pre_image", "post_image"):
    d = Path(C_RUN) / sub
    for p in sorted(d.glob("*.py")):
        t = p.read_text(encoding="utf-8")
        raw_h, lf_h = hashes(p)
        print(f"{sub}/{p.name}: raw={raw_h} lf={lf_h} "
              f"max_complexity={_max_complexity(t)}")
        carrier.setdefault(p.name, {})[sub] = {
            "sha256_raw": raw_h, "sha256_lf": lf_h,
            "max_complexity": _max_complexity(t),
        }

print()
print("=" * 78)
print("D. WORKTREE vs CARRIER post_image (LF-normalised)")
print("=" * 78)
for name, d in sorted(carrier.items()):
    if "post_image" not in d:
        continue
    p = SRC / name
    if not p.exists():
        continue
    raw_h, lf_h = hashes(p)
    same = lf_h == d["post_image"]["sha256_lf"]  # type: ignore[index]
    print(f"{name}: worktree_lf == post_image_lf -> {same}")
    files[name]["worktree_equals_post_image"] = same  # type: ignore[index]

print()
print("=" * 78)
print("E. JSON")
print("=" * 78)
print(json.dumps(report, ensure_ascii=False, indent=2))

