"""r4 FINAL anchor verification: every citation token printed in review.md's
revision tables must resolve to its expected marker on the cited line.

Read-only. Exit 0 only when every checked anchor matches.
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
TEXT = (ATTEMPT / "review.md").read_text(encoding="utf-8")

# (doc, line, marker) — the normative anchors cited by review.md §5.1/§5.3/§5.6
ANCHORS: list[tuple[str, int, str]] = [
    ("decision.md", 74, "W` 是参数"),
    ("decision.md", 76, "### 2.5"),
    ("decision.md", 79, "编号规则"),
    ("decision.md", 85, "| E02 |"),
    ("decision.md", 86, "| E32 |"),
    ("decision.md", 90, "| E06 |"),
    ("decision.md", 109, "| E25 |"),
    ("decision.md", 110, "| E26 |"),
    ("decision.md", 111, "| E27 |"),
    ("decision.md", 113, "| E29 |"),
    ("decision.md", 117, "三个参数"),
    ("decision.md", 119, "一致性规则"),
    ("decision.md", 139, "### 2.4"),
    ("decision.md", 146, "`L` bytes"),
    ("decision.md", 145, "超时"),
    ("decision.md", 153, "E02"),
    ("decision.md", 154, "E32"),
    ("decision.md", 172, "trust_domain_schema_version"),
    ("decision.md", 186, "revoked_at"),
    ("decision.md", 193, "12 个字段"),
    ("decision.md", 194, "无条件必填（10）"),
    ("decision.md", 209, "撤销（r3"),
    ("decision.md", 263, "`expires_at` 的真实含义"),
    ("decision.md", 275, "### 6.0"),
    ("decision.md", 278, "### 6.1"),
    ("decision.md", 293, "### 6.2"),
    ("decision.md", 305, "### 6.3"),
    ("decision.md", 315, "OPEN-D6"),
    ("decision.md", 317, "### 6.4"),
    ("decision.md", 323, "## 7. F01/F02"),
    ("decision.md", 355, "### 7.1"),
    ("decision.md", 361, "E32"),
    ("decision.md", 375, "raw rc"),
    ("decision.md", 391, "- **OPEN-D6"),
    ("decision.md", 397, "OPEN-D7"),
    ("decision.md", 406, "### 8.0"),
    ("decision.md", 418, "批次约束"),
    ("decision.md", 444, "N-R2-04"),
    ("decision.md", 472, "10. 交付给 I-08-B/C"),
    ("decision.md", 496, "### 11.1"),
    ("oracle.md", 32, "EXP-BASE-2"),
    ("oracle.md", 42, "E32"),
    ("oracle.md", 53, "错误码唯一来源"),
    ("oracle.md", 57, "NEG-PROV-1"),
    ("oracle.md", 59, "NEG-PROV-1b"),
    ("oracle.md", 63, "NEG-PROV-4"),
    ("oracle.md", 92, "NEG-REPLAY-8"),
    ("oracle.md", 81, "NEG-TRUST-1"),
    ("oracle.md", 84, "NEG-TRUST-4"),
    ("oracle.md", 96, "NEG-LEGACY-3"),
    ("oracle.md", 97, "NEG-LEGACY-4"),
    ("oracle.md", 99, "NEG-LEGACY-6"),
    ("oracle.md", 113, "| **A-D1** |"),
    ("oracle.md", 126, "RED（缺口成立）"),
    ("oracle.md", 127, "provider 协议从未被调用"),
    ("oracle.md", 146, "test_recognition_bridge"),
    ("oracle.md", 150, "## 6. 措辞修订"),
    ("review.md", 23, "35 行 / 32 个 id"),
    ("review.md", 27, "35 行 / 32 个 id"),
    ("review.md", 40, "provider 协议"),
    ("review.md", 96, "35 行 / 32 个 id"),
    ("review.md", 100, "## 5.1 revision r2"),
    ("review.md", 104, "check_r2_consistency"),
    ("review.md", 117, "F-I08A-09"),
    ("review.md", 135, "R-BIND-1"),
    ("review.md", 141, "限制声明"),
    ("review.md", 246, "8. **`check_r2_consistency.py`"),
    ("review.md", 249, "两个脚本都"),
]

fails = 0
for doc, line, marker in ANCHORS:
    lines = DOCS[doc]
    if line > len(lines):
        print(f"FAIL {doc}:{line} out of range")
        fails += 1
        continue
    if marker not in lines[line - 1]:
        print(f"FAIL {doc}:{line} lacks {marker!r} :: {lines[line-1][:90]!r}")
        fails += 1

print(f"anchors_checked={len(ANCHORS)} failures={fails}")

# every cited token must at least exist in the cited document range
print("\n== cited token inventory ==")
for doc in ("decision.md", "oracle.md", "review.md"):
    nums = sorted({int(n) for n in re.findall(r"`" + doc.replace(".", r"\.") + r":(\d+)`", TEXT)})
    over = [n for n in nums if n > len(DOCS[doc])]
    print(f"  {doc}: {nums} out_of_range={over}")
    fails += len(over)

# observation census restated from the frozen probe output
import json  # noqa: E402

probe = (ATTEMPT / "after" / "c3_probe.stdout.txt").read_text(encoding="utf-8")
ids = [json.loads(l[4:])["id"] for l in probe.splitlines()
       if l.startswith("EXP:") and not l.startswith("EXP-SUMMARY")]
print(f"\nobservation_census: rows={len(ids)} distinct_ids={len(set(ids))} "
      f"duplicate_ids={sorted({i for i in ids if ids.count(i) > 1})}")
sys.exit(1 if fails else 0)
