"""Build changes.diff for PROMOTION-EXEC a20260922-01 (repo-prefixed sections).

Net production changes only: before-image -> current target.
B-6c nets to zero (promoted then reverted to the same before-image) and is
recorded as an explicit NO-OP section.
"""
import difflib
import hashlib
import sys
from pathlib import Path

AT = Path(sys.argv[1])
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")

ROWS = [
    ("RF", AT / "recovery/before_images/B-1/revenue_core.py", RF / "scripts/revenue_core.py", "B-1"),
    ("RF", AT / "recovery/before_images/B-1/revenue_publication.py", RF / "scripts/revenue_publication.py", "B-1"),
    ("RF", AT / "recovery/before_images/B-1/revenue_report.py", RF / "scripts/revenue_report.py", "B-1"),
    ("RF", AT / "recovery/before_images/B-2/company_wiki_source.py", RF / "scripts/company_wiki_source.py", "B-2"),
    ("RF", AT / "recovery/before_images/B-2/source_preparation.py", RF / "scripts/source_preparation.py", "B-2"),
    ("RF", AT / "recovery/before_images/B-6c/model_registry.py", RF / "scripts/model_registry.py", "B-6c(REVERTED)"),
    ("CW", AT / "recovery/before_images/B-3/observability.py", CW / "src/company_wiki/source_catalog/observability.py", "B-3"),
    ("CW", None, CW / "conftest.py", "B-4(NEW)"),
    ("CW", None, CW / "tests/contract/test_short_basetemp_convention.py", "B-4(NEW)"),
    ("CW", AT / "recovery/before_images/B-5/prune_retired_evidence.py", CW / "src/company_wiki/source_catalog/prune_retired_evidence.py", "B-5"),
    ("CW", AT / "recovery/before_images/B-5/archive_retired_evidence.py", CW / "src/company_wiki/source_catalog/archive_retired_evidence.py", "B-5"),
]


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


out = []
out.append("# PROMOTION-EXEC a20260922-01 — net changes.diff (before-image -> current production)\n")
out.append("# owner ruling: OWNER_DECISIONS.md §十八「B: 全批」; no git commits performed\n")
cur_repo = None
for repo, before, after, row in ROWS:
    if repo != cur_repo:
        out.append(f"\n=== REPO: {'revenue-forecast' if repo == 'RF' else 'company-wiki'} ===\n")
        cur_repo = repo
    after_bytes = after.read_bytes()
    rel = after.relative_to(RF if repo == "RF" else CW).as_posix()
    if before is None:
        a_lines = b"".join([b"\n"]) * 0  # placeholder, replaced below
        a_text_lines = []
        b_text_lines = after_bytes.decode("utf-8").splitlines(keepends=True)
        diff = list(difflib.unified_diff(a_text_lines, b_text_lines,
                                         fromfile="/dev/null", tofile=f"b/{rel}"))
        hdr_before = "--- /dev/null"
    else:
        before_bytes = before.read_bytes()
        same = before_bytes == after_bytes
        a_text_lines = before_bytes.decode("utf-8").splitlines(keepends=True)
        b_text_lines = after_bytes.decode("utf-8").splitlines(keepends=True)
        diff = list(difflib.unified_diff(a_text_lines, b_text_lines,
                                         fromfile=f"a/{rel}", tofile=f"b/{rel}"))
        hdr_before = f"a/{rel}"
    out.append(f"\n--- row {row} --- {hdr_before} -> b/{rel}\n")
    out.append(f"# before_sha256: {sha(before.read_bytes()) if before else 'ABSENT'}\n")
    out.append(f"# after_sha256:  {sha(after_bytes)}\n")
    if before is not None and before.read_bytes() == after_bytes:
        out.append("# NET: NO-OP (reverted to identical before-image; promotion did not land)\n")
    out.extend(diff)

target = AT / "changes.diff"
target.write_text("".join(out), encoding="utf-8")
print("wrote", target, target.stat().st_size, "bytes", sha(target.read_bytes()))
