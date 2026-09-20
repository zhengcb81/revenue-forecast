"""r4 citation repair (round 3) — final anchor corrections, then full verification."""

from __future__ import annotations

import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent
DOCS = {
    name: (ATTEMPT / name).read_text(encoding="utf-8").splitlines()
    for name in ("decision.md", "oracle.md", "review.md")
}
REVIEW_PATH = ATTEMPT / "review.md"
text = REVIEW_PATH.read_text(encoding="utf-8")

REPAIRS = [
    # §11.1 moved to 496 by the r4 paste/insertions
    ("`decision.md:445`（§11.1）；`oracle.md:144`", "`decision.md:496`（§11.1）；`oracle.md:144`"),
    ("`commands.json:68`–`commands.json:83`；`decision.md:445`（§11.1）",
     "`commands.json:68`–`commands.json:83`；`decision.md:496`（§11.1）"),
    # §10 heading is at 472; §8.2 r3 record row is at 444
    ("`decision.md:430`（§10 第 8 项）", "`decision.md:472`（§10 第 8 项）"),
    ("`decision.md:436`（§10）", "`decision.md:472`（§10）"),
    ("`decision.md:445`（§8.2）", "`decision.md:444`（§8.2）"),
    # review.md §4 item 8 now sits at 221; §5.3 N-R2-07 row covers 221-224
    ("`review.md:181`–`review.md:187`", "`review.md:221`–`review.md:224`"),
    ("`review.md:184`（§4 第 8 条）、`review.md:104`（§5.1）、`decision.md:445`（§8.2）",
     "`review.md:221`（§4 第 8 条）、`review.md:104`（§5.1）、`decision.md:444`（§8.2）"),
]

applied = 0
for old, new in REPAIRS:
    if old not in text:
        print(f"SKIP (not found): {old}")
        continue
    if text.count(old) != 1:
        print(f"SKIP (ambiguous x{text.count(old)}): {old}")
        continue
    text = text.replace(old, new, 1)
    applied += 1
    print(f"applied: {old}  ->  {new}")
REVIEW_PATH.write_text(text, encoding="utf-8", newline="\n")
print(f"repairs_applied={applied}")

# --- final full verification: every citation token resolves to its marker ---
CHECKS = [
    ("§5.1 F-01 §6.0", "`decision.md:275`（§6.0）", "decision.md", 275, "### 6.0"),
    ("§5.1 F-01 §6.1", "`decision.md:278`（§6.1）", "decision.md", 278, "### 6.1"),
    ("§5.1 F-01 §6.2", "`decision.md:293`（§6.2）", "decision.md", 293, "### 6.2"),
    ("§5.1 F-01 E26", "`decision.md:110`（E26）", "decision.md", 110, "| E26 |"),
    ("§5.1 F-01 E27", "`decision.md:111`（E27）", "decision.md", 111, "| E27 |"),
    ("§5.1 F-01 oracle", "`oracle.md:96`、`oracle.md:97`", "oracle.md", 96, "NEG-LEGACY-3"),
    ("§5.1 F-02 §2.5", "`decision.md:76`–`decision.md:113`（§2.5）", "decision.md", 76, "### 2.5"),
    ("§5.1 F-02 §2.4", "`decision.md:139`（§2.4）", "decision.md", 139, "### 2.4"),
    ("§5.1 F-02 consistency", "`decision.md:119`（一致性规则）", "decision.md", 119, "一致性规则"),
    ("§5.1 F-02 oracle", "`oracle.md:53`–`oracle.md:97`", "oracle.md", 53, "错误码唯一来源"),
    ("§5.1 F-03 §2.2", "`decision.md:74`（§2.2）", "decision.md", 74, "W` 是参数"),
    ("§5.1 F-04 §6.3", "`decision.md:305`（§6.3）", "decision.md", 305, "### 6.3"),
    ("§5.1 F-04 E29", "`decision.md:113`（E29）", "decision.md", 113, "| E29 |"),
    ("§5.1 F-04 §6.4", "`decision.md:317`（§6.4）", "decision.md", 317, "### 6.4"),
    ("§5.1 F-04 OPEN-D6", "`decision.md:315`/`decision.md:391`（OPEN-D6）", "decision.md", 391, "- **OPEN-D6"),
    ("§5.1 F-04 oracle", "`oracle.md:95`、`oracle.md:123`", "oracle.md", 95, "NEG-LEGACY-6"),
    ("§5.1 F-05 §3", "`decision.md:172`–`decision.md:194`（§3）", "decision.md", 172, "trust_domain_schema_version"),
    ("§5.1 F-05 E25", "`decision.md:109`（E25）", "decision.md", 109, "| E25 |"),
    ("§5.1 F-06 §7.1", "`decision.md:355`（§7.1 四条前置）", "decision.md", 355, "### 7.1"),
    ("§5.1 F-06 §7", "`decision.md:323`（§7）", "decision.md", 323, "## 7. F01/F02"),
    ("§5.1 F-06 §10", "`decision.md:472`（§10 第 8 项）", "decision.md", 472, "10. 交付给 I-08-B/C"),
    ("§5.1 F-07 §11.1", "`decision.md:496`（§11.1）", "decision.md", 496, "### 11.1"),
    ("§5.1 F-09 oracle §6", "`oracle.md:150`（§6）", "oracle.md", 150, "## 6. 措辞修订"),
    ("§5.1 F-09 oracle A-D1", "`oracle.md:113`（A-D1 行）", "oracle.md", 113, "| **A-D1** |"),
    ("§5.3 R-BIND-1", "`decision.md:186`（示例条目", "decision.md", 186, "revoked_at"),
    ("§5.3 R-BIND-1 fields", "`decision.md:193`（字段集 12 项）", "decision.md", 193, "12 个字段"),
    ("§5.3 R-BIND-1 req", "`decision.md:194`（无条件必填 10 项）", "decision.md", 194, "无条件必填（10）"),
    ("§5.3 R-BIND-1 revoke", "`decision.md:209`（撤销条款改写）", "decision.md", 209, "撤销（r3"),
    ("§5.3 R-BIND-2 E02", "`decision.md:85`（E02 收窄）", "decision.md", 85, "| E02 |"),
    ("§5.3 R-BIND-2 E32", "`decision.md:86`（E32 新增）", "decision.md", 86, "| E32 |"),
    ("§5.3 R-BIND-2 §2.4", "`decision.md:153`–`decision.md:154`", "decision.md", 153, "E02"),
    ("§5.3 R-BIND-2 §7.1", "`decision.md:361`–`decision.md:368`", "decision.md", 361, "E32"),
    ("§5.3 R-BIND-2 oracle", "`oracle.md:42`、`oracle.md:57`–`oracle.md:59`、`oracle.md:113`", "oracle.md", 113, "| **A-D1** |"),
    ("§5.3 N-R2-04 E06", "`decision.md:90`（E06）", "decision.md", 90, "| E06 |"),
    ("§5.3 N-R2-04 §2.4", "`decision.md:146`（§2.4）", "decision.md", 146, "`L` bytes"),
    ("§5.3 N-R2-04 §10", "`decision.md:472`（§10）", "decision.md", 472, "10. 交付给 I-08-B/C"),
    ("§5.3 N-R2-05 编号规则", "`decision.md:79`（编号规则）", "decision.md", 79, "编号规则"),
    ("§5.3 N-R2-05 E29", "`decision.md:113`（E29 行）", "decision.md", 113, "| E29 |"),
    ("§5.3 N-R2-05 §8.0", "`decision.md:406`–`decision.md:418`（§8.0）", "decision.md", 406, "### 8.0"),
    ("§5.3 N-R2-06", "`oracle.md:32`、`oracle.md:150`（§6）", "oracle.md", 32, "EXP-BASE-2"),
    ("§5.3 N-R2-07", "`review.md:221`–`review.md:224`", "review.md", 221, "8. **`check_r2_consistency.py`"),
    ("§5.3 limit §4", "`review.md:221`（§4 第 8 条）", "review.md", 221, "8. **`check_r2_consistency.py`"),
    ("§5.3 limit §8.2", "`decision.md:444`（§8.2）", "decision.md", 444, "N-R2-04"),
]

fails = 0
print("\n== final citation verification ==")
for label, token, doc, line, marker in CHECKS:
    present = token in text
    line_text = DOCS[doc][line - 1] if line <= len(DOCS[doc]) else ""
    ok = present and marker in line_text
    if not ok:
        fails += 1
        print(f"FAIL {label:28s} token_present={present} marker_on_{doc}:{line}={marker in line_text}")
print(f"checked={len(CHECKS)} failures={fails}")
sys.exit(1 if fails else 0)
