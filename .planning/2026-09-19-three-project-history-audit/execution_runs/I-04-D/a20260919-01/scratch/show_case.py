"""Inspect one I-04-D case directory in detail (paths are long, so read in Python)."""

from __future__ import annotations

import json
from pathlib import Path
import sys

case = Path(sys.argv[1])
print(f"case dir : {case}")
if not case.exists():
    print("MISSING")
    raise SystemExit(1)
for path in sorted(case.iterdir()):
    size = path.stat().st_size if path.is_file() else -1
    print(f"  {path.name}  bytes={size}")
for tag in ("A", "B", "C", "nest", "user", "prober", "holder", "probe"):
    for kind in ("report", "stdout", "stderr"):
        path = case / f"{kind}.{tag}.json" if kind == "report" else case / f"{kind}.{tag}.txt"
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            print(f"--- {path.name} ({len(text)} chars) ---")
            if kind == "report":
                try:
                    payload = json.loads(text)
                except ValueError:
                    print(text[:800])
                    continue
                print(
                    json.dumps(
                        {
                            k: v
                            for k, v in payload.items()
                            if k not in {"before_enter", "after_enter", "after_exit",
                                         "after_inner_enter", "after_inner_exit",
                                         "after_third_enter", "after_third_exit",
                                         "after_error"}
                        },
                        ensure_ascii=False,
                        indent=1,
                    )[:2500]
                )
            else:
                print(text[:1500] if text else "<empty>")
gate = case / "gate.enter_lock_held.B.reached"
print(f"gate.enter_lock_held.B.reached exists={gate.exists()} mtime={gate.stat().st_mtime if gate.exists() else None}")
