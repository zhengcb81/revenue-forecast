"""I-14-F-R1: verify the constructed path lengths used in the unit-test case table.

Frozen expectations (owner §16 E-1: GENERATION_RESERVE=150, threshold 60):
relocate iff len(resolved_basetemp) + 150 > 210  <=>  len(resolved_basetemp) > 60.
"""
from __future__ import annotations

import os

THRESHOLD = 60
RESERVE = 150
LIMIT = 210

SUF_ABS = "\\run\\pytest"   # 11 chars
SUF_REL = "\\pytest"        # 7 chars

CASES = [
    # (comment-label, cwd-expr, requested-expr, expected-relocate)
    ("deep absolute (174)", "C:\\" + "d" * 160, "C:\\" + "d" * 160 + SUF_ABS, True),
    ("falsifier band (154)", "C:\\" + "n" * 140, "C:\\" + "n" * 140 + SUF_ABS, True),
    ("addendumC probe (119)", "C:\\" + "b" * 105, "C:\\" + "b" * 105 + SUF_ABS, True),
    ("BOUNDARY 60 (unrelocated)", "C:\\" + "b" * 46, "C:\\" + "b" * 46 + SUF_ABS, False),
    ("BOUNDARY 61 (relocated)", "C:\\" + "b" * 47, "C:\\" + "b" * 47 + SUF_ABS, True),
    ("FLIP 84 -> relocate", "C:\\" + "b" * 70, "C:\\" + "b" * 70 + SUF_ABS, True),
    ("FLIP 82 -> relocate", "C:\\" + "s" * 68, "C:\\" + "s" * 68 + SUF_ABS, True),
    ("over-deep relative (360)", "C:\\" + "x" * 350, "pytest", True),
    ("FLIP 78 -> relocate (relative)", "C:\\" + "s" * 68, "pytest", True),
]


def resolve(cwd: str, requested: str) -> str:
    if os.path.isabs(requested) or (len(requested) > 1 and requested[1] == ":"):
        return requested
    return cwd + "\\" + requested


def main() -> int:
    ok = True
    print(f"criterion: relocate iff len(resolved) + {RESERVE} > {LIMIT}  <=>  len > {THRESHOLD}")
    print(f"{'case':34s} {'cwd':>4s} {'resolved':>8s} {'sum(+150)':>9s} {'expect':>7s} {'calc':>6s}")
    for label, cwd, requested, expected in CASES:
        resolved = resolve(cwd, requested)
        calc = len(resolved) + RESERVE > LIMIT
        match = calc is expected
        ok = ok and match
        print(f"{label:34s} {len(cwd):4d} {len(resolved):8d} {len(resolved)+RESERVE:9d} "
              f"{str(expected):>7s} {str(calc):>6s} {'' if match else '  <-- MISMATCH'}")
    # decide() test dirs
    # decide() test dirs — emulate pathlib EXACTLY (correction: str(Path('C:\\') / name)
    # has no extra separator, so len = 3 + len(name); the pre-freeze version of this script
    # used 3+1+len(name) and was off by one for these three dirs only — the criterion-table
    # values above were always string concatenation and were correct).
    from pathlib import Path as _P
    for label, name in (("decide mid61s (frozen 64)", "s" * 61),
                        ("decide small41w (frozen 44)", "w" * 41),
                        ("decide deep201d (frozen 204)", "d" * 201)):
        p = str(_P("C:\\") / name)
        print(f"{label:30s} len={len(p):3d} relocate={len(p) > THRESHOLD}")
    for label, name in (("decide old60s (I14F)", "s" * 60),
                        ("decide old40w", "w" * 40),
                        ("decide old200d", "d" * 200)):
        p = str(_P("C:\\") / name)
        print(f"{label:30s} len={len(p):3d} relocate={len(p) > THRESHOLD}")
    # hook within-budget basetemp
    temp = os.environ.get("TEMP", "")
    within = temp + "\\cw-i14f-unit-within-budget"
    print(f"hook within-budget: TEMP={len(temp)} path={len(within)} relocate={len(within) > THRESHOLD}")
    print("ALL_TABLE_EXPECTATIONS_MATCH" if ok else "TABLE_MISMATCH")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
