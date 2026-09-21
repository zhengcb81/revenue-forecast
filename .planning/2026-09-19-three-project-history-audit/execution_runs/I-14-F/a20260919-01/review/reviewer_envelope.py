"""Reviewer tool: extract the exact generated-path lengths from raw RED tracebacks and
retained unrelocated artifacts, so the reserve/threshold arithmetic is measured, not hand-counted.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent
TEMP = Path(os.environ["TEMP"])

RED_LOGON = ATTEMPT / "before" / "deep" / "pad55" / "P0-logon_wrapper_quoted-1"
RED_CHILD = ATTEMPT / "before" / "deep" / "pad55" / "P0-child_without_runtime-1"
MUT = TEMP / "i14f-rev-mut" / ("a" * 95)
PROBE116 = TEMP / "i14f-normal116"
SHORT_GREEN = TEMP / "i14f-short-green"
BOUNDARY76 = TEMP / "n"

BASETEMP_LIMIT = 86  # BASETEMP_MAX_CHARS shipped: len > 86 relocates


def attempted_paths(stdout: Path, basetemp: Path) -> list[tuple[int, int, str]]:
    text = stdout.read_text(encoding="utf-8", errors="replace")
    bt = str(basetemp)
    out = []
    for raw in set(re.findall(r"'([A-Za-z]:\\\\[^']+)'", text)):
        p = raw.replace("\\\\", "\\")
        if p.startswith(bt):
            out.append((len(p), len(p) - len(bt), p[len(bt):]))
    return sorted(out)


def deepest_existing(basetemp: Path) -> tuple[int, int, str]:
    bt = str(basetemp)
    best = (0, 0, "")
    for dirpath, dirnames, filenames in os.walk(basetemp):
        for name in list(dirnames) + list(filenames):
            full = str(Path(dirpath) / name)
            if len(full) > best[0]:
                best = (len(full), len(full) - len(bt), full[len(bt):])
    return best


def report(title: str, basetemp: Path) -> None:
    print(f"\n=== {title}")
    print(f"    basetemp len={len(str(basetemp))}")
    d = deepest_existing(basetemp)
    print(f"    deepest existing: total={d[0]} suffix={d[1]}  {d[2]}")
    print(f"    -> at the largest UNROUTED basetemp ({BASETEMP_LIMIT}): total={BASETEMP_LIMIT + d[1]}")


for title, bt in [
    ("RED child (basetemp 174, unrelocated artifacts retained)", RED_CHILD / "pytest"),
    ("RED logon (basetemp 173, mkdir died)", RED_LOGON / "pytest"),
    ("my mutation child (basetemp 174, disabled)", MUT / "P0-child_without_runtime-1" / "pytest"),
    ("my mutation logon (basetemp 173, disabled)", MUT / "P0-logon_wrapper_quoted-1" / "pytest"),
    ("116 probe child (basetemp 116, unrouted -> degraded)", PROBE116),
    ("boundary76 controls (basetemp 75/74, unrouted, logon PASSED)", BOUNDARY76),
    ("short-green controls (basetemp 82/81, unrouted, logon PASSED)", SHORT_GREEN),
]:
    if bt.exists():
        report(title, bt)
    else:
        print(f"\n=== {title}: MISSING {bt}")

print("\n=== exact attempted (failing) paths in the RED logon traceback")
for total, suffix, rel in attempted_paths(RED_LOGON / "stdout.txt", RED_LOGON / "pytest"):
    print(f"    total={total} suffix={suffix}  {rel}")
print("\n=== exact attempted paths in the RED child traceback")
for total, suffix, rel in attempted_paths(RED_CHILD / "stdout.txt", RED_CHILD / "pytest"):
    print(f"    total={total} suffix={suffix}  {rel}")
