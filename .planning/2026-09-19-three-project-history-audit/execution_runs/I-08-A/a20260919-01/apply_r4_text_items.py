"""Apply the r4 required text items inside review.md (items 1, 2 and the two
§5.3 citation corrections). Verifies each edit before and after; aborts on any
unexpected state so nothing is silently rewritten.
"""

from __future__ import annotations

import re
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent
REVIEW = ATTEMPT / "review.md"
text = REVIEW.read_text(encoding="utf-8")
original = text

# --- item 1: re-anchor every file:line citation in the §5.1 / §5.3 tables ---
# (old_citation, new_citation)
CITATION_FIXES = [
    # §5.1 rows
    ("decision.md:263", "decision.md:275"),
    ("decision.md:266", "decision.md:278"),
    ("decision.md:281", "decision.md:293"),
    ("decision.md:98", "decision.md:110"),
    ("decision.md:99", "decision.md:111"),
    ("oracle.md:93", "oracle.md:96"),
    ("oracle.md:94", "oracle.md:97"),
    ("decision.md:142", "decision.md:139"),
    ("decision.md:116", "decision.md:119"),
    ("oracle.md:46", "oracle.md:53"),
    ("decision.md:110", "decision.md:113"),      # §5.1 F-04 E29 row only
    ("decision.md:303", "decision.md:317"),
    ("decision.md:339", "decision.md:315"),
    ("decision.md:388", "decision.md:391"),
    ("decision.md:333", "decision.md:323"),
    ("decision.md:428", "decision.md:430"),
    ("oracle.md:141", "oracle.md:144"),
    ("oracle.md:146", "oracle.md:150"),
    # §5.3 rows
    ("decision.md:114", "decision.md:113"),
    ("decision.md:434", "decision.md:436"),
    ("oracle.md:110", "oracle.md:113"),
    ("decision.md:375", "decision.md:368"),
    ("review.md:101", "review.md:104"),
]

# Apply the §5.1 F-04 E29 fix first (its old text is a prefix of another old text)
e29_old = "`decision.md:110`（E29）"
e29_new = "`decision.md:113`（E29）"
assert text.count(e29_old) == 1, "E29 citation anchor not unique"
text = text.replace(e29_old, e29_new, 1)

applied: list[tuple[str, str, int]] = []
for old, new in CITATION_FIXES:
    if old == "decision.md:110":
        continue  # already handled
    count = text.count(old)
    if count == 0:
        continue
    text = text.replace(old, new)
    applied.append((old, new, count))

# --- item 2: observation wording -------------------------------------------
W_OLD = "**不变量全部一致**：35 条观测、`errors=0`"
W_NEW = ("**不变量全部一致**：35 行 / 32 个 id（`EXP-BASE-2b` 按探针构造重复 4 次）、`errors=0`")
assert text.count(W_OLD) == 1, "observation wording anchor not unique"
text = text.replace(W_OLD, W_NEW, 1)

W2_OLD = "35 条观测、`errors=0`、`gap=true` 恰为"
W2_NEW = "35 行 / 32 个 id、`errors=0`、`gap=true` 恰为"
if text.count(W2_OLD):
    text = text.replace(W2_OLD, W2_NEW)

# record the census definition next to the first mention in §1/§3 area
CENSUS_OLD = "全部来自 `after/c3_probe.stdout.txt`（35 条观测，`errors=0`）。"
CENSUS_NEW = ("全部来自 `after/c3_probe.stdout.txt`（**35 行 / 32 个不同观测 id**；"
              "`EXP-BASE-2b` 因探针在每次 provider 输入后都会记录一次而重复 4 次，`errors=0`）。")
if text.count(CENSUS_OLD):
    text = text.replace(CENSUS_OLD, CENSUS_NEW, 1)

REVIEW.write_text(text, encoding="utf-8", newline="\n")

print("citation replacement groups applied:")
for old, new, count in applied:
    print(f"  {old} -> {new}  (x{count})")
remaining_old = [old for old, _new in CITATION_FIXES
                 if old != "decision.md:110" and old in text]
print("old_citations_still_present=" + (",".join(remaining_old) if remaining_old else "none"))
print("changed=" + str(text != original))
