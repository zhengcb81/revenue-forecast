"""Read-only static scan: does the skill runtime depend on repo-only roots?"""

from __future__ import annotations

import re
import pathlib

root = pathlib.Path(__file__).resolve().parents[3]
runtime_dirs = ["scripts", "agents", "config", "references"]
repo_only = [
    "tests",
    "tools",
    "assurance",
    "audit_review",
    "compatibility",
    "e2e",
    "examples",
]
suffixes = {".py", ".yaml", ".yml", ".json", ".md", ".txt", ".toml", ".cfg", ".ini", ""}

hits = {k: [] for k in repo_only}
scanned = 0
for d in runtime_dirs:
    base = root / d
    if not base.is_dir():
        raise SystemExit(f"runtime directory missing (scan would be vacuous): {base}")
    for p in base.rglob("*"):
        if not p.is_file() or p.suffix not in suffixes:
            continue
        if "__pycache__" in p.parts:
            continue
        scanned += 1
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print("READFAIL", p, exc)
            continue
        for k in repo_only:
            patterns = (
                rf"\bfrom\s+{k}\b",
                rf"\bimport\s+{k}\b",
                rf"['\"]{k}/",
                rf"sys\.path[^\n]*{k}",
            )
            for pat in patterns:
                for m in re.finditer(pat, text):
                    line = text.count("\n", 0, m.start()) + 1
                    hits[k].append(f"{p.as_posix()}:{line}: {m.group(0)[:70]}")

print(f"scanned root: {root}")
print(f"scanned files: {scanned}")
for k, v in hits.items():
    print(f"== {k}: {len(v)}")
    for item in v[:15]:
        print("   ", item)
