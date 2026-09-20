"""Seal the attempt: recompute canonical hashes LAST and write the sealed manifest.

Order matters: the stale-value repair edits the documents, so the manifest must be
regenerated after it.  This script also records the seal time and a self-verification
pass so the manifest is provably consistent with the delivered bytes.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import pathlib

A = pathlib.Path(__file__).resolve().parents[1]

FILES = {
    "binding.json": A / "binding.json",
    "oracle.md": A / "oracle.md",
    "decision.md": A / "decision.md",
    "commands.json": A / "commands.json",
    "changes.diff": A / "changes.diff",
    "handoff.json": A / "handoff.json",
    "review.md": A / "review.md",
    "recovery/README.md": A / "recovery" / "README.md",
    "iso/filing-fetch/scripts/fetch_filing.py": A / "iso" / "filing-fetch" / "scripts" / "fetch_filing.py",
    "iso/filing-fetch/scripts/i04d_schedule.py": A / "iso" / "filing-fetch" / "scripts" / "i04d_schedule.py",
    "iso/filing-fetch/scripts/i04d_participant.py": A / "iso" / "filing-fetch" / "scripts" / "i04d_participant.py",
    "iso/filing-fetch/scripts/i04d_fake_worker.py": A / "iso" / "filing-fetch" / "scripts" / "i04d_fake_worker.py",
    "iso/filing-fetch/tests/test_fetch_filing_lease.py": A / "iso" / "filing-fetch" / "tests" / "test_fetch_filing_lease.py",
    "scratch/patch_i04d.py": A / "scratch" / "patch_i04d.py",
    "before/i04d-red.txt": A / "before" / "i04d-red.txt",
    "before/test_fetch_filing_lease.delivered.py": A / "before" / "test_fetch_filing_lease.delivered.py",
    "after/i04d-green.txt": A / "after" / "i04d-green.txt",
    "evidence/phase-wall.txt": A / "evidence" / "phase-wall.txt",
    "evidence/negative-case-ledger.txt": A / "evidence" / "negative-case-ledger.txt",
    "evidence/negative-case-detail.txt": A / "evidence" / "negative-case-detail.txt",
    "evidence/i04d_schedule.delivered.py": A / "evidence" / "i04d_schedule.delivered.py",
    "before/00-git-heads.txt": A / "before" / "00-git-heads.txt",
    "before/01-anchor-hashes.txt": A / "before" / "01-anchor-hashes.txt",
    "before/02-catalog-invariant.txt": A / "before" / "02-catalog-invariant.txt",
}


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


rows = []
for rel, path in sorted(FILES.items()):
    if not path.exists():
        rows.append((rel, "MISSING", 0))
        continue
    rows.append((rel, digest(path), path.stat().st_size))

stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
lines = [
    "# I-04-D a20260919-01 — SEALED canonical hashes (r2 rework)",
    "#",
    f"# sealed_at_utc: {stamp}",
    "#",
    "# 封盘纪律（reviewer 要求）：本文件写入后，attempt 目录不再写入；此后再写入即判定本轮",
    "# 失效、需重新点审。",
    "#",
    "# 编码注意：evidence/negative-case-*.txt 为 UTF-16LE（PowerShell 5.1 重定向默认编码）。",
    "",
]
for rel, sha, length in rows:
    lines.append(f"{sha}  {length:>8}  {rel}")
manifest = "\n".join(lines) + "\n"
(A / "evidence" / "hashes.txt").write_text(manifest, encoding="utf-8")

# self-verification
bad = []
for rel, sha, length in rows:
    path = FILES[rel]
    if not path.exists() or digest(path) != sha or path.stat().st_size != length:
        bad.append(rel)
print(f"sealed_at_utc: {stamp}")
print(f"rows: {len(rows)}   mismatches: {bad if bad else 'NONE'}")
print()
width = max(len(rel) for rel, _, _ in rows)
for rel, sha, length in rows:
    print(f"{sha[:12]}  {length:>8}  {rel}")
