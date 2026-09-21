"""Reviewer tool: compare the attempt's isolated tree against a pristine git-archive copy.

Independent of the implementer harness. Read-only w.r.t. production.
Usage: python reviewer_compare.py <iso_tree> <pristine_tree>
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path


def snap(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            p = Path(dirpath) / name
            rel = str(p.relative_to(root))
            with open(p, "rb") as handle:
                out[rel] = hashlib.sha256(handle.read()).hexdigest()
    return out


def main() -> int:
    iso = snap(Path(sys.argv[1]))
    rev = snap(Path(sys.argv[2]))
    only_iso = sorted(set(iso) - set(rev))
    only_rev = sorted(set(rev) - set(iso))
    diff = sorted(k for k in set(iso) & set(rev) if iso[k] != rev[k])
    print(f"iso files={len(iso)} pristine files={len(rev)}")
    print(f"only-in-iso ({len(only_iso)}):")
    for k in only_iso:
        print("   +", k)
    print(f"only-in-pristine ({len(only_rev)}):")
    for k in only_rev:
        print("   -", k)
    print(f"content-differ ({len(diff)}):")
    for k in diff:
        a = (Path(sys.argv[1]) / k).read_bytes()
        b = (Path(sys.argv[2]) / k).read_bytes()
        same_lf = a.replace(b"\r\n", b"\n") == b.replace(b"\r\n", b"\n")
        print(f"   ! {k} crlf_normalized_equal={same_lf} size_iso={len(a)} size_pristine={len(b)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
