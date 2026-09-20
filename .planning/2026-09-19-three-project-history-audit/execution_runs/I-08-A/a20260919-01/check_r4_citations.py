"""r4 citation audit: recompute every file:line cited by review.md's revision tables.

Read-only. For each citation target, locate the current line(s) that actually
contain the marker, and report match/miss plus the corrected anchor. Also reports
the observation-id census (rows vs distinct ids) so the "35 observations" wording
can be corrected against measured data.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent
DOCS = {
    name: (ATTEMPT / name).read_text(encoding="utf-8").splitlines()
    for name in ("decision.md", "oracle.md", "review.md", "commands.json", "handoff.json")
}


def find(name: str, *markers: str) -> list[int]:
    """Line numbers (1-based) of the first line containing ALL markers."""
    out = []
    for i, line in enumerate(DOCS[name], start=1):
        if all(m in line for m in markers):
            out.append(i)
    return out


# (label, doc, markers) — the anchor each citation SHOULD point at
TARGETS = [
    ("F-01 §6.0", "decision.md", ("### 6.0",)),
    ("F-01 §6.1", "decision.md", ("### 6.1",)),
    ("F-01 §6.2", "decision.md", ("### 6.2",)),
    ("F-01 E26", "decision.md", ("| E26 |",)),
    ("F-01 E27", "decision.md", ("| E27 |",)),
    ("F-01 G3a row", "decision.md", ("**G3a",)),
    ("F-01 G3b row", "decision.md", ("**G3b",)),
    ("F-01 oracle NEG-LEGACY-3", "oracle.md", ("| NEG-LEGACY-3 |", "E26")),
    ("F-01 oracle NEG-LEGACY-4", "oracle.md", ("| NEG-LEGACY-4 |", "E27")),
    ("F-02 §2.5", "decision.md", ("### 2.5",)),
    ("F-02 E31 row", "decision.md", ("| E31 |",)),
    ("F-02 §2.4", "decision.md", ("### 2.4",)),
    ("F-02 consistency rule", "decision.md", ("一致性规则（码值唯一来源）",)),
    ("F-02 oracle header", "oracle.md", ("错误码唯一来源",)),
    ("F-03 W row", "decision.md", ("`W` 是参数",)),
    ("F-04 E29 row", "decision.md", ("| E29 |",)),
    ("F-04 §6.3", "decision.md", ("### 6.3",)),
    ("F-04 §6.4", "decision.md", ("### 6.4",)),
    ("F-04 OPEN-D6 #1", "decision.md", ("OPEN-D6", "§7 scope 外")),
    ("F-04 OPEN-D6 #2", "decision.md", ("- **OPEN-D6",)),
    ("F-05 §3 block", "decision.md", ("\"trust_domain_schema_version\"",)),
    ("F-06 §7.1", "decision.md", ("### 7.1",)),
    ("F-06 §7", "decision.md", ("## 7. F01/F02",)),
    ("F-06 §10 item 8", "decision.md", ("F-I08A-03",)),
    ("F-09 oracle §6", "oracle.md", ("## 6. 措辞修订",)),
    ("F-09 oracle A-D1 row", "oracle.md", ("| **A-D1** |",)),
    ("R-BIND-2 §7.1 end", "decision.md", ("每条用例的 raw rc",)),
    ("R-BIND-2 oracle A-D1 row", "oracle.md", ("| **A-D1** |",)),
    ("N-R2-04 §10", "decision.md", ("10. 交付给 I-08-B/C",)),
    ("N-R2-05 E29 row", "decision.md", ("| E29 |",)),
    ("N-R2-07 review §4 item 8", "review.md", ("8. **`check_r2_consistency.py`",)),
    ("N-R2-07 review §5.1", "review.md", ("§4 第 8 条与 §5.3",)),
]

print("== current anchors ==")
anchors: dict[str, list[int]] = {}
for label, doc, markers in TARGETS:
    hits = find(doc, *markers)
    anchors[label] = hits
    print(f"  {label:32s} {doc}:{hits}")

# --- observation census: rows vs distinct ids -------------------------------
probe = (ATTEMPT / "after" / "c3_probe.stdout.txt").read_text(encoding="utf-8")
ids: list[str] = []
for line in probe.splitlines():
    if line.startswith("EXP:") and not line.startswith("EXP-SUMMARY"):
        ids.append(json.loads(line[4:])["id"])
dupes = sorted({i for i in ids if ids.count(i) > 1})
print("\n== observation census ==")
print(f"  exp_lines={len(ids)} distinct_ids={len(set(ids))}")
print(f"  duplicated_ids={dupes}")
for i in dupes:
    print(f"    {i} appears {ids.count(i)} times")
print(f"  EXP-SUMMARY line present={'EXP-SUMMARY:' in probe}")

# --- handoff / commands text items -----------------------------------------
print("\n== text items ==")
print("  handoff reviewer_must_do ->", find("handoff.json", "reviewer_must_do"))
print("  handoff implementer_note ->", find("handoff.json", "implementer_note"))
print("  handoff reviewer_status  ->", find("handoff.json", "reviewer_status"))
cmd = json.loads((ATTEMPT / "commands.json").read_text(encoding="utf-8"))
for c in cmd["commands"]:
    if c["id"] in ("I08A-c10-r2-consistency", "I08A-c13-check-r3-pairs"):
        print(f"  {c['id']}: expected_returncode={c.get('expected_returncode')!r} "
              f"raw={c.get('raw_returncode')!r}")
print("  decision three-params line ->", find("decision.md", "三个参数"))
print("  review 35-observation mentions ->", find("review.md", "35 条观测"))
print("  oracle 35-observation mentions ->", find("oracle.md", "35 条观测"))
print("  decision 35-observation mentions ->", find("decision.md", "35 条观测"))
print("  handoff 35-observation mentions ->", find("handoff.json", "35 条观测"))
print("  commands 35-observation mentions ->", find("commands.json", "35 "))
