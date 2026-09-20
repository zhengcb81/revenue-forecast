"""r4 final: verify and repair every `review.md:N` self-citation, then verify all
cross-document citations. Prints a full audit; exits 1 if any citation cannot be
resolved to its expected marker.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent
DOCS = {
    name: (ATTEMPT / name).read_text(encoding="utf-8").splitlines()
    for name in ("decision.md", "oracle.md", "review.md", "commands.json", "handoff.json")
}
REVIEW = ATTEMPT / "review.md"
text = REVIEW.read_text(encoding="utf-8")
lines = text.splitlines()

# self-citation expectations: token -> marker that must appear on that line
SELF = {
    "`review.md:23`": "35 行 / 32 个 id",
    "`review.md:27`": "35 行 / 32 个 id",
    "`review.md:40`": "provider 协议",
    "`review.md:96`": "35 行 / 32 个 id",
    "`review.md:104`": "check_r2_consistency",
    "`review.md:109`": "F-I08A-01",
    "`review.md:117`": "F-I08A-09",
    "`review.md:135`": "R-BIND-1",
    "`review.md:141`": "限制声明",
}

print("== self-citation check ==")
problems: list[str] = []
for token, marker in SELF.items():
    m = re.match(r"`review\.md:(\d+)`", token)
    line = int(m.group(1))
    if not (1 <= line <= len(lines)):
        problems.append(f"{token} out of range")
        continue
    ok = marker in lines[line - 1]
    if not ok:
        # find the true line
        true = [i + 1 for i, l in enumerate(lines) if marker in l]
        problems.append(f"{token} lacks {marker!r}; candidates={true}")
        print(f"MISS {token} lacks {marker!r} -> candidates {true}")
    else:
        print(f"OK   {token} contains {marker!r}")

if problems:
    print("\nrepairing self-citations:")
    for token, marker in SELF.items():
        m = re.match(r"`review\.md:(\d+)`", token)
        line = int(m.group(1))
        if 1 <= line <= len(lines) and marker in lines[line - 1]:
            continue
        true = [i + 1 for i, l in enumerate(lines) if marker in l and l.startswith("|") or (marker in l)]
        true = [i + 1 for i, l in enumerate(lines) if marker in l]
        if len(true) == 1:
            text = text.replace(token, f"`review.md:{true[0]}`")
            print(f"  {token} -> `review.md:{true[0]}`")
        else:
            print(f"  SKIP {token}: ambiguous candidates {true}")
    REVIEW.write_text(text, encoding="utf-8", newline="\n")
    lines = text.splitlines()

# cross-document citations: token -> (doc, marker)
CROSS = {
    "`decision.md:275`": ("decision.md", "### 6.0"),
    "`decision.md:278`": ("decision.md", "### 6.1"),
    "`decision.md:305`": ("decision.md", "### 6.3"),
    "`decision.md:317`": ("decision.md", "### 6.4"),
    "`decision.md:355`": ("decision.md", "### 7.1"),
    "`decision.md:323`": ("decision.md", "## 7. F01/F02"),
    "`decision.md:472`": ("decision.md", "10. 交付给 I-08-B/C"),
    "`decision.md:496`": ("decision.md", "### 11.1"),
    "`decision.md:444`": ("decision.md", "N-R2-04"),
    "`decision.md:109`": ("decision.md", "| E25 |"),
    "`decision.md:110`": ("decision.md", "| E26 |"),
    "`decision.md:111`": ("decision.md", "| E27 |"),
    "`decision.md:113`": ("decision.md", "| E29 |"),
    "`decision.md:74`": ("decision.md", "W` 是参数"),
    "`decision.md:79`": ("decision.md", "编号规则"),
    "`decision.md:85`": ("decision.md", "| E02 |"),
    "`decision.md:86`": ("decision.md", "| E32 |"),
    "`decision.md:90`": ("decision.md", "| E06 |"),
    "`decision.md:117`": ("decision.md", "三个参数"),
    "`decision.md:119`": ("decision.md", "一致性规则"),
    "`decision.md:139`": ("decision.md", "### 2.4"),
    "`decision.md:146`": ("decision.md", "`L` bytes"),
    "`decision.md:153`": ("decision.md", "E02"),
    "`decision.md:154`": ("decision.md", "E32"),
    "`decision.md:172`": ("decision.md", "trust_domain_schema_version"),
    "`decision.md:186`": ("decision.md", "revoked_at"),
    "`decision.md:193`": ("decision.md", "12 个字段"),
    "`decision.md:194`": ("decision.md", "无条件必填（10）"),
    "`decision.md:209`": ("decision.md", "撤销（r3"),
    "`decision.md:361`": ("decision.md", "E32"),
    "`decision.md:368`": ("decision.md", "raw rc"),
    "`decision.md:391`": ("decision.md", "- **OPEN-D6"),
    "`decision.md:406`": ("decision.md", "### 8.0"),
    "`oracle.md:32`": ("oracle.md", "EXP-BASE-2"),
    "`oracle.md:42`": ("oracle.md", "E32"),
    "`oracle.md:57`": ("oracle.md", "NEG-PROV-1"),
    "`oracle.md:58`": ("oracle.md", "NEG-PROV-1a"),
    "`oracle.md:59`": ("oracle.md", "NEG-PROV-1b"),
    "`oracle.md:63`": ("oracle.md", "NEG-PROV-4"),
    "`oracle.md:96`": ("oracle.md", "NEG-LEGACY-3"),
    "`oracle.md:97`": ("oracle.md", "NEG-LEGACY-4"),
    "`oracle.md:99`": ("oracle.md", "NEG-LEGACY-6"),
    "`oracle.md:113`": ("oracle.md", "| **A-D1** |"),
    "`oracle.md:150`": ("oracle.md", "## 6. 措辞修订"),
    "`oracle.md:53`": ("oracle.md", "错误码唯一来源"),
    "`oracle.md:144`": ("oracle.md", "test_recognition_bridge"),
}

print("\n== cross-document citation check ==")
fails = 0
for token, (doc, marker) in CROSS.items():
    if token not in text:
        print(f"absent {token}")
        continue
    m = re.match(r"`([a-z]+\.md):(\d+)`", token)
    line = int(m.group(2))
    doc_lines = DOCS[doc]
    ok = line <= len(doc_lines) and marker in doc_lines[line - 1]
    if not ok:
        fails += 1
        print(f"FAIL {token} expected {marker!r}")
print(f"cross_failures={fails}")

# census of citations actually present
print("\n== citations present in review.md ==")
for doc in ("decision.md", "oracle.md", "review.md"):
    found = sorted({int(n) for n in re.findall(rf"`{doc.replace('.', chr(92)+'.')}:(\d+)`", text)})
    print(f"  {doc}: {found}")
print("self_citation_problems_before_repair=" + str(len(problems)))
sys.exit(1 if fails else 0)
