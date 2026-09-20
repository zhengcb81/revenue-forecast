"""r4 citation repair (round 2): the round-1 replacements mutated each other, so
some tokens ended up pointing at the wrong line. This script repairs the
remaining stale citations with exact, verified substitutions, then verifies each
repaired (doc, line) against a content marker.

Only citation tokens are rewritten; no prose is touched.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent
DOCS = {
    name: (ATTEMPT / name).read_text(encoding="utf-8").splitlines()
    for name in ("decision.md", "oracle.md", "review.md")
}
REVIEW_PATH = ATTEMPT / "review.md"
text = REVIEW_PATH.read_text(encoding="utf-8")

# exact repair: (stale token, correct token, marker that must be on the new line)
REPAIRS: list[tuple[str, str, str]] = [
    ("`decision.md:168`–`decision.md:190`（§3）", "`decision.md:172`–`decision.md:194`（§3）", "trust_domain_schema_version"),
    ("`decision.md:107`（E25）", "`decision.md:109`（E25）", "E25"),
    ("`decision.md:343`（§7.1 四条前置）", "`decision.md:355`（§7.1 四条前置）", "### 7.1"),
    ("`decision.md:443`（§11.1）；`oracle.md:144`", "`decision.md:445`（§11.1）；`oracle.md:144`", "### 11.1"),
    ("`commands.json:68`–`commands.json:83`；`decision.md:443`（§11.1）",
     "`commands.json:68`–`commands.json:83`；`decision.md:445`（§11.1）", "### 11.1"),
    ("`oracle.md:150`（§6）、`oracle.md:109`（A-D1 行）；`decision.md:107`（E02 备注）",
     "`oracle.md:150`（§6）、`oracle.md:113`（A-D1 行）；`decision.md:109`（E02 备注）", "## 6. 措辞修订"),
    ("`review.md:181`–`review.md:187`", "`review.md:184`–`review.md:187`", "8. **`check_r2_consistency.py`"),
    ("`review.md:184`（§4 第 8 条）、`review.md:104`（§5.1）、`decision.md:443`（§8.2）",
     "`review.md:184`（§4 第 8 条）、`review.md:104`（§5.1）、`decision.md:445`（§8.2）", "8. **`check_r2_consistency.py`"),
    # decision.md E04/E01 note earlier in §5.1 row 1 keeps working; §5.1 F-01 E26/E27 already correct
]

applied: list[tuple[str, str]] = []
for old, new, marker in REPAIRS:
    if old not in text:
        print(f"SKIP (not found): {old}")
        continue
    assert text.count(old) == 1, f"ambiguous anchor: {old}"
    text = text.replace(old, new, 1)
    m = re.search(r"`(decision|oracle|review)\.md:(\d+)`", new)
    if m:
        doc = m.group(1) + ".md"
        line = int(m.group(2))
        line_text = DOCS[doc][line - 1] if line <= len(DOCS[doc]) else ""
        status = "OK" if marker in line_text else "MARKER-MISS"
        print(f"{status} {old} -> {new}")
    applied.append((old, new))

REVIEW_PATH.write_text(text, encoding="utf-8", newline="\n")
print(f"repairs_applied={len(applied)}")

# --- full re-verification of every revision-table row -----------------------
CHECKS = [
    ("§5.1 F-01 marker", "`decision.md:275`（§6.0）", "decision.md", 275, "### 6.0"),
    ("§5.1 F-01 E26", "`decision.md:110`（E26）", "decision.md", 110, "| E26 |"),
    ("§5.1 F-01 E27", "`decision.md:111`（E27）", "decision.md", 111, "| E27 |"),
    ("§5.1 F-01 G3a/G3b", "`decision.md:293`（§6.2）", "decision.md", 293, "### 6.2"),
    ("§5.1 F-02 §2.4", "`decision.md:139`（§2.4）", "decision.md", 139, "### 2.4"),
    ("§5.1 F-02 consistency", "`decision.md:119`（一致性规则）", "decision.md", 119, "一致性规则"),
    ("§5.1 F-03 W", "`decision.md:74`（§2.2）", "decision.md", 74, "W` 是参数"),
    ("§5.1 F-04 §6.3", "`decision.md:305`（§6.3）", "decision.md", 305, "### 6.3"),
    ("§5.1 F-04 E29", "`decision.md:113`（E29）", "decision.md", 113, "| E29 |"),
    ("§5.1 F-04 §6.4", "`decision.md:317`（§6.4）", "decision.md", 317, "### 6.4"),
    ("§5.1 F-04 OPEN-D6", "`decision.md:391`（OPEN-D6）", "decision.md", 391, "OPEN-D6"),
    ("§5.1 F-05 §3", "（§3）", "decision.md", 172, "trust_domain_schema_version"),
    ("§5.1 F-05 E25", "`decision.md:109`（E25）", "decision.md", 109, "| E25 |"),
    ("§5.1 F-06 §7.1", "`decision.md:355`（§7.1 四条前置）", "decision.md", 355, "### 7.1"),
    ("§5.1 F-06 §7", "`decision.md:323`（§7）", "decision.md", 323, "## 7. F01/F02"),
    ("§5.1 F-06 §10", "`decision.md:430`（§10 第 8 项）", "decision.md", 430, "F-I08A-03"),
    ("§5.1 F-07 §11.1", "`decision.md:445`（§11.1）", "decision.md", 445, "### 11.1"),
    ("§5.1 F-09 oracle §6", "`oracle.md:150`（§6）", "oracle.md", 150, "## 6. 措辞修订"),
    ("§5.1 F-09 oracle A-D1", "`oracle.md:113`（A-D1 行）", "oracle.md", 113, "| **A-D1** |"),
    ("§5.3 R-BIND-1", "`decision.md:186`（示例条目", "decision.md", 186, "revoked_at"),
    ("§5.3 R-BIND-2 E02", "`decision.md:85`（E02 收窄）", "decision.md", 85, "| E02 |"),
    ("§5.3 R-BIND-2 E32", "`decision.md:86`（E32 新增）", "decision.md", 86, "| E32 |"),
    ("§5.3 R-BIND-2 §2.4", "`decision.md:153`–`decision.md:154`", "decision.md", 153, "E02"),
    ("§5.3 R-BIND-2 §7.1 range", "`decision.md:361`–`decision.md:368`", "decision.md", 361, "E32"),
    ("§5.3 R-BIND-2 oracle A-D1", "`oracle.md:113`", "oracle.md", 113, "| **A-D1** |"),
    ("§5.3 N-R2-04 E06", "`decision.md:90`（E06）", "decision.md", 90, "| E06 |"),
    ("§5.3 N-R2-04 §2.4", "`decision.md:146`（§2.4）", "decision.md", 146, "`L` bytes"),
    ("§5.3 N-R2-04 §10", "`decision.md:436`（§10）", "decision.md", 436, "N-R2-04"),
    ("§5.3 N-R2-05 编号规则", "`decision.md:79`（编号规则）", "decision.md", 79, "编号规则"),
    ("§5.3 N-R2-05 E29", "`decision.md:113`（E29 行）", "decision.md", 113, "| E29 |"),
    ("§5.3 N-R2-05 OPEN-D6", "`decision.md:391`（OPEN-D6）", "decision.md", 391, "OPEN-D6"),
    ("§5.3 N-R2-05 §8.0", "`decision.md:406`–`decision.md:418`（§8.0）", "decision.md", 406, "### 8.0"),
    ("§5.3 N-R2-06", "`oracle.md:32`、`oracle.md:150`（§6）", "oracle.md", 32, "EXP-BASE-2"),
    ("§5.3 N-R2-07", "`review.md:184`–`review.md:187`", "review.md", 184, "8. **`check_r2_consistency.py`"),
    ("§5.3 limit statement", "`review.md:184`（§4 第 8 条）", "review.md", 184, "8. **`check_r2_consistency.py`"),
    ("§5.3 limit §8.2", "`decision.md:445`（§8.2）", "decision.md", 445, "### 11.1"),
]

fails = 0
print("\n== re-verification ==")
for label, token, doc, line, marker in CHECKS:
    present = token in text
    line_text = DOCS[doc][line - 1] if line <= len(DOCS[doc]) else ""
    ok = present and marker in line_text
    if not ok:
        fails += 1
    print(f"{'OK  ' if ok else 'FAIL'} {label:32s} token_present={present} marker_on_line={marker in line_text}")
print(f"verification_failures={fails}")
sys.exit(1 if fails else 0)
