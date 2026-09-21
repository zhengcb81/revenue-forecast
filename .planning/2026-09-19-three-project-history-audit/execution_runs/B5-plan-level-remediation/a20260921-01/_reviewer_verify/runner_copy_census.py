"""Reviewer check of the '68/68 historical runner copies unchanged' claim.

Enumerates every run_card.py under execution_runs/M01..M31, groups by the bound sha256
recorded in each batch's evidence.json / the contract, and verifies byte equality.
"""
import glob
import hashlib
import json
import os
import re

PLAN = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
        r"\2026-09-19-three-project-history-audit")
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BOUND = {
    "M01-M04": ("M01", "b5fcc68563f5"),
    "M05-M08": ("M05", "fd3a11c9226a"),
    "M09-M12": ("M09", "997c553b0b9e"),
    "M13-M16": ("M13", "9e4a6450d6ab"),
    "M17-M20": ("M17", "94619a98f576"),
    "M21-M24": ("M21", "a5ee7599c37e"),
    "M25-M28": ("M25", "eab0116220df"),
    "M29-M31": ("M29", "9ea69c72dced"),
}


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


files = glob.glob(os.path.join(PLAN, "execution_runs", "M*", "*", "**", "run_card.py"),
                  recursive=True)
files = [f for f in files if re.search(r"\\M\d\d\\", f)]
print("run_card.py paths under M01..M31: %d" % len(files))

# per card, which copies exist
by_card = {}
for f in files:
    card = re.search(r"\\M(\d\d)\\", f).group(1)
    by_card.setdefault("M" + card, []).append(f)

print("\nper-card copy count and distinct hashes:")
grid = {}
for card in sorted(by_card):
    hs = sorted({sha(p) for p in by_card[card]})
    grid[card] = hs
    print("  %s  copies=%d  distinct_sha=%d  %s" % (card, len(by_card[card]), len(hs),
                                                    ",".join(h[:12] for h in hs)))

total_copies = sum(len(v) for v in by_card.values())
print("\ntotal copies under M01..M31 = %d" % total_copies)

# which cards belong to which batch, and does every copy of a card share one sha?
print("\nper-batch: all copies of all member cards byte-identical?")
groups = {"M01-M04": ["M01", "M02", "M03", "M04"], "M05-M08": ["M05", "M06", "M07", "M08"],
          "M09-M12": ["M09", "M10", "M11", "M12"], "M13-M16": ["M13", "M14", "M15", "M16"],
          "M17-M20": ["M17", "M18", "M19", "M20"], "M21-M24": ["M21", "M22", "M23", "M24"],
          "M25-M28": ["M25", "M26", "M27", "M28"], "M29-M31": ["M29", "M30", "M31"]}
n_ok = 0
n_copies = 0
for batch, cards in groups.items():
    shas = set()
    cnt = 0
    for c in cards:
        for h in grid.get(c, []):
            shas.add(h)
            cnt += 1
    rep, prefix = BOUND[batch]
    ok = len(shas) == 1 and list(shas)[0].startswith(prefix)
    n_ok += 1 if ok else 0
    n_copies += cnt
    print("  %-9s copies=%2d distinct_sha=%d bound_prefix=%s  consistent=%s" % (
        batch, cnt, len(shas), prefix, ok))
print("\nbatches consistent = %d/8 ; total copies counted = %d" % (n_ok, n_copies))
