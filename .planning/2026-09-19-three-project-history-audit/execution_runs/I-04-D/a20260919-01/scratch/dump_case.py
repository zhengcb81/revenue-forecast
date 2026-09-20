"""Dump everything about one I-04-D case directory, byte-exact and bounded."""

from __future__ import annotations

import json
from pathlib import Path
import sys

case = Path(sys.argv[1])
print(f"case: {case}")
print(f"exists: {case.exists()}")
if case.exists():
    for path in sorted(case.iterdir()):
        print(f"  {path.name} size={path.stat().st_size if path.is_file() else '<dir>'}")
    wiki = case / "wiki"
    catalog = wiki / ".source_catalog"
    print(f"wiki exists={wiki.exists()} catalog exists={catalog.exists()}")
    if catalog.exists():
        for path in sorted(catalog.iterdir()):
            print(f"    catalog/{path.name} size={path.stat().st_size if path.is_file() else '<dir>'}")
for name in sorted(p.name for p in case.glob("report.*.json")) if case.exists() else []:
    path = case / name
    print(f"--- {name} ---")
    try:
        print(json.dumps(json.loads(path.read_text(encoding="utf-8")), ensure_ascii=False, indent=1)[:3000])
    except ValueError as exc:
        print(f"<unparsable: {exc}> {path.read_text(encoding='utf-8', errors='replace')[:800]}")
for name in sorted(p.name for p in case.glob("stderr.*.txt")) if case.exists() else []:
    text = (case / name).read_text(encoding="utf-8", errors="replace")
    print(f"--- {name} --- {text[:1500] if text else '<empty>'}")
if len(sys.argv) > 2:
    trace = Path(sys.argv[2])
    if trace.exists():
        print(f"--- trace {trace} ---")
        print(trace.read_text(encoding="utf-8")[:4000])
