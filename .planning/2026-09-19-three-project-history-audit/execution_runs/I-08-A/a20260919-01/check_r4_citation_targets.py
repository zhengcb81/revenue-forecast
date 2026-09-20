"""r4 citation verifier: for every revision-table row, check that the first
cited line of the primary document actually contains the expected marker.

If a citation is stale, report the correct line. With --fix, rewrite only the
citation token (never the prose). Read-only otherwise.
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
CITE = re.compile(r"(document\.md|oracle\.md|review\.md):(\d+)")

# (row_prefix, doc, cited_line_after_r4, marker that MUST appear on that line)
EXPECT: list[tuple[str, str, int, str | None]] = [
    # §5.1 r2 table
    ("F-I08A-01", "decision.md", 275, "### 6.0"),
    ("F-I08A-02", "decision.md", 76, "### 2.5"),
    ("F-I08A-03", "decision.md", 74, "W` 是参数"),
    ("F-I08A-04", "decision.md", 305, "### 6.3"),
    ("F-I08A-05", "decision.md", 172, "trust_domain_schema_version"),
    ("F-I08A-06", "decision.md", 355, "### 7.1"),
    ("F-I08A-07", "binding.json", 92, None),
    ("F-I08A-08", "commands.json", 68, None),
    ("F-I08A-09", "oracle.md", 150, "## 6. 措辞修订"),
    # §5.3 r3 table
    ("R-BIND-1", "decision.md", 186, "revoked_at"),
    ("R-BIND-2", "decision.md", 85, "E02"),
    ("N-R2-04", "decision.md", 90, "E06"),
    ("N-R2-05", "decision.md", 79, "编号规则"),
    ("N-R2-06", "oracle.md", 32, "EXP-BASE-2"),
    ("N-R2-07", "review.md", 184, "check_r2_consistency"),
]


def line_of(doc: str, number: int) -> str:
    lines = DOCS.get(doc)
    if lines is None:
        return "<not a checked doc>"
    return lines[number - 1] if 1 <= number <= len(lines) else "<out of range>"


def locate(doc: str, marker: str) -> list[int]:
    lines = DOCS.get(doc)
    if lines is None:
        return []
    return [i + 1 for i, l in enumerate(lines) if marker in l]


problems: list[str] = []
fixes: list[tuple[str, str, str]] = []

for row_prefix, doc, cited, marker in EXPECT:
    if marker is None:
        continue
    if marker in line_of(doc, cited):
        print(f"OK   {row_prefix:12s} {doc}:{cited} contains {marker!r}")
        continue
    candidates = locate(doc, marker)
    problems.append(f"{row_prefix}: {doc}:{cited} lacks {marker!r}; candidates={candidates}")
    print(f"MISS {row_prefix:12s} {doc}:{cited} lacks {marker!r}; should be {candidates}")

if "--fix" in sys.argv:
    text = REVIEW.read_text(encoding="utf-8")
    # only the first citation of each row is normative for structure; repair the
    # specific stale tokens identified above
    for row_prefix, doc, cited, marker in EXPECT:
        if marker is None or marker in line_of(doc, cited):
            continue
        candidates = locate(doc, marker)
        if len(candidates) != 1:
            print(f"SKIP {row_prefix}: ambiguous marker {marker!r} -> {candidates}")
            continue
        old = f"`{doc}:{cited}`"
        new = f"`{doc}:{candidates[0]}`"
        if text.count(old) == 1:
            text = text.replace(old, new, 1)
            fixes.append((row_prefix, old, new))
    REVIEW.write_text(text, encoding="utf-8", newline="\n")
    print("fixes_applied=" + str(len(fixes)))
    for row, old, new in fixes:
        print(f"  {row}: {old} -> {new}")

print("citation_problems=" + str(len(problems)))
sys.exit(1 if problems and "--fix" not in sys.argv else 0)
