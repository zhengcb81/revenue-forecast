"""r4 targeted citation fixes + verification of every normative anchor.

Fixes the three citations the generic audit flagged, then verifies the complete
normative anchor set (each token must exist AND its marker must sit on the cited
line). Marker-less tokens (ranges, section shortcuts) are reported separately.
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
REVIEW = ATTEMPT / "review.md"
text = REVIEW.read_text(encoding="utf-8")

FIXES = [
    ("`decision.md:361`–`decision.md:368`（§7.1）", "`decision.md:361`–`decision.md:375`（§7.1）"),
    ("`oracle.md:42`、`oracle.md:57`–`oracle.md:59`、`oracle.md:113`",
     "`oracle.md:42`、`oracle.md:57`–`oracle.md:59`（含 `NEG-PROV-1a`/`1b` 在 :58/:59）、`oracle.md:113`"),
    ("`decision.md:496`（§11.1）；`oracle.md:144`", "`decision.md:496`（§11.1）；`oracle.md:146`"),
]
for old, new in FIXES:
    c = text.count(old)
    print(f"{'applied' if c == 1 else 'SKIP x' + str(c)}: {old[:70]}")
    if c == 1:
        text = text.replace(old, new, 1)
REVIEW.write_text(text, encoding="utf-8", newline="\n")

DOCS["review.md"] = REVIEW.read_text(encoding="utf-8").splitlines()

# normative anchors with explicit markers
ANCHORS = [
    ("decision", 74, "W` 是参数"), ("decision", 76, "### 2.5"), ("decision", 79, "编号规则"),
    ("decision", 85, "| E02 |"), ("decision", 86, "| E32 |"), ("decision", 90, "| E06 |"),
    ("decision", 109, "| E25 |"), ("decision", 110, "| E26 |"), ("decision", 111, "| E27 |"),
    ("decision", 113, "| E29 |"), ("decision", 117, "三个参数"), ("decision", 119, "一致性规则"),
    ("decision", 139, "### 2.4"), ("decision", 142, "限额"), ("decision", 146, "`L` bytes"),
    ("decision", 153, "E02"), ("decision", 154, "E32"), ("decision", 172, "trust_domain_schema_version"),
    ("decision", 186, "revoked_at"), ("decision", 193, "12 个字段"), ("decision", 194, "无条件必填（10）"),
    ("decision", 209, "撤销（r3"), ("decision", 275, "### 6.0"),
    ("decision", 278, "### 6.1"), ("decision", 293, "### 6.2"), ("decision", 305, "### 6.3"),
    ("decision", 315, "OPEN-D6"), ("decision", 317, "### 6.4"), ("decision", 323, "## 7. F01/F02"),
    ("decision", 355, "### 7.1"), ("decision", 361, "E32"), ("decision", 372, "OPEN-D7"),
    ("decision", 375, "raw rc"), ("decision", 391, "- **OPEN-D6"), ("decision", 406, "### 8.0"),
    ("decision", 418, "批次约束"), ("decision", 444, "N-R2-04"), ("decision", 472, "10. 交付给 I-08-B/C"),
    ("decision", 496, "### 11.1"),
    ("oracle", 32, "EXP-BASE-2"), ("oracle", 42, "E32"), ("oracle", 53, "错误码唯一来源"), ("oracle", 81, "NEG-TRUST-1"), ("oracle", 84, "NEG-TRUST-4"), ("oracle", 126, "RED（缺口成立）"), ("oracle", 127, "provider 协议从未被调用"),
    ("oracle", 57, "NEG-PROV-1"), ("oracle", 59, "NEG-PROV-1b"), ("oracle", 63, "NEG-PROV-4"),
    ("oracle", 96, "NEG-LEGACY-3"),
    ("oracle", 97, "NEG-LEGACY-4"), ("oracle", 99, "NEG-LEGACY-6"), ("oracle", 113, "| **A-D1** |"),
    
    ("oracle", 146, "test_recognition_bridge"), ("oracle", 150, "## 6. 措辞修订"),
    ("review", 23, "35 行 / 32 个 id"), ("review", 27, "35 行 / 32 个 id"),
    ("review", 40, "provider 协议"), ("review", 96, "35 行 / 32 个 id"),
    ("review", 100, "## 5.1 revision r2"), ("review", 104, "check_r2_consistency"),
    ("review", 117, "F-I08A-09"), ("review", 135, "R-BIND-1"), ("review", 141, "限制声明"),
    ("review", 244, "8. **`check_r2_consistency.py`"), ("review", 247, "两个脚本都"),
]

fails = 0
print("\n== normative anchor verification ==")
for doc, line, marker in ANCHORS:
    doc_lines = DOCS[doc + ".md"]
    if line > len(doc_lines):
        print(f"FAIL {doc}.md:{line} out of range")
        fails += 1
        continue
    if marker not in doc_lines[line - 1]:
        print(f"FAIL {doc}.md:{line} lacks {marker!r} :: actual={doc_lines[line-1][:80]!r}")
        fails += 1
print(f"anchors_checked={len(ANCHORS)} failures={fails}")

# tokens cited in review.md whose target must contain a marker
print("\n== cited tokens in review.md (must resolve) ==")
for doc in ("decision.md", "oracle.md", "review.md"):
    nums = sorted({int(n) for n in re.findall(
        r"`" + doc.replace(".", r"\.") + r":(\d+)`", text)})
    print(f"  {doc}: {nums}")
sys.exit(1 if fails else 0)
