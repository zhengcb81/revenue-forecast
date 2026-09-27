"""Before/After family stdout identity check with a precise normalizer.

Normalizes ONLY volatile run metadata: pytest timing suffixes (`in 12.34s`,
`(0:01:18)`, `s in setup/teardown` style suffixes) and nothing else. Everything
else — progress, test ids, failure text, counts — must be byte-identical.
Usage: python -B compare_families.py
"""
from __future__ import annotations

import re
from pathlib import Path

A = Path(r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
         r"\execution_runs\RF-RATCHET-REST-B\a20260923-01")
FAMS = ["F0_ratchet", "F1_b1battery", "F2_i08c13", "F3_modelbattery", "F5_golden",
        "F6_needles", "F7_models", "F8_adversarial", "F9_backtest"]

TIME_PATS = [
    re.compile(r"in \d+\.\d+s( \(\d+:\d+:\d+\))?"),   # "in 57.50s (0:01:18)"
    re.compile(r"\d+\.\d+s\b(?= (?:setup|teardown))"),
]

lines_out: list[str] = []
diffs = 0
for fam in FAMS:
    b = (A / "evidence" / "families_before" / f"{fam}_stdout.txt").read_text(encoding="utf-8")
    a = (A / "evidence" / "families_after" / f"{fam}_stdout.txt").read_text(encoding="utf-8")
    rc_b = (A / "evidence" / "families_before" / f"{fam}_rc.txt").read_text(encoding="utf-8").strip()
    rc_a = (A / "evidence" / "families_after" / f"{fam}_rc.txt").read_text(encoding="utf-8").strip()
    for pat in TIME_PATS:
        b = pat.sub("in <T>", b)
        a = pat.sub("in <T>", a)
    same = b == a
    rc_same = rc_b == rc_a
    if not (same and rc_same):
        diffs += 1
    lines_out.append(f"{fam}: rc {rc_b}->{rc_a} identical_rc={rc_same} identical_stdout_stripped={same}")
    if not same:
        bl, al = b.splitlines(), a.splitlines()
        for i in range(max(len(bl), len(al))):
            x = bl[i] if i < len(bl) else "<EOF>"
            y = al[i] if i < len(al) else "<EOF>"
            if x != y:
                lines_out.append(f"  first diff at line {i+1}:")
                lines_out.append(f"    before: {x!r}")
                lines_out.append(f"    after : {y!r}")
                break
lines_out.append("")
lines_out.append(f"families_with_diff = {diffs}")
(A / "evidence" / "families_before_after_identity.txt").write_text(
    "\n".join(lines_out) + "\n", encoding="utf-8")
print("\n".join(lines_out))
