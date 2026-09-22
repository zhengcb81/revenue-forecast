"""Verify the M6 mutant differs from B1's fixed tree in EXACTLY one file.

Usage: python verify_m6_delta.py <src_rf_root> <mutant_rf_root> <proof.json out>
Read-only except the proof file.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(root: Path) -> dict[str, str]:
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[str(p.relative_to(root)).replace("\\", "/")] = sha256_file(p)
    return out


def main() -> int:
    src = Path(sys.argv[1])
    mut = Path(sys.argv[2])
    proof_path = Path(sys.argv[3])
    a, b = manifest(src), manifest(mut)
    only_src = sorted(set(a) - set(b))
    only_mut = sorted(set(b) - set(a))
    changed = sorted(k for k in set(a) & set(b) if a[k] != b[k])
    proof = {
        "src_root": str(src),
        "mutant_root": str(mut),
        "files_src": len(a),
        "files_mutant": len(b),
        "only_in_src": only_src,
        "only_in_mutant": only_mut,
        "changed": changed,
        "exactly_one_changed_file": changed
        == ["scripts/revenue_publication.py"]
        and not only_src
        and not only_mut,
        "changed_file_sha256_src": a.get("scripts/revenue_publication.py"),
        "changed_file_sha256_mutant": b.get("scripts/revenue_publication.py"),
    }
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    proof_path.write_text(json.dumps(proof, indent=2), encoding="utf-8")
    print(json.dumps(proof, indent=2))
    if not proof["exactly_one_changed_file"]:
        raise SystemExit("MUTANT DELTA NOT ISOLATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
