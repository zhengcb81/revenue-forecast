"""Full JSON parse check across the attempt, then SEAL with a structural self-check.

The previous seal only compared hashes, so an unparseable handoff.json still reported
"mismatches: NONE".  The seal now also runs json.load on every *.json in the manifest
and fails loudly if any of them is not valid JSON.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import sys

A = pathlib.Path(__file__).resolve().parents[1]
EXCLUDE_PARTS = {"venv", "__pycache__", ".i04d-test-runs"}


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- 1. full JSON check
checked = 0
failures: list[tuple[str, str]] = []
for path in sorted(A.rglob("*.json")):
    parts = set(path.relative_to(A).parts)
    if parts & EXCLUDE_PARTS or "site-packages" in parts:
        continue
    checked += 1
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - any failure is a finding
        failures.append((path.relative_to(A).as_posix(), f"{type(exc).__name__}: {exc}"))

lines = [
    "I-04-D full JSON parse check",
    f"root      : {A}",
    f"excluded  : {sorted(EXCLUDE_PARTS)} and site-packages (iso/venv)",
    f"checked   : {checked}",
    f"failures  : {len(failures)}",
    "",
]
for rel, err in failures:
    lines.append(f"FAIL  {rel}\n      {err}")
if not failures:
    lines.append("all checked files parsed with json.load")
(A / "after" / "all_json_parse_check.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))

# ---------------------------------------------------------------- 2. seal with structure check
FILES = {
    "binding.json": A / "binding.json",
    "oracle.md": A / "oracle.md",
    "decision.md": A / "decision.md",
    "commands.json": A / "commands.json",
    "changes.diff": A / "changes.diff",
    "handoff.json": A / "handoff.json",
    "review.md": A / "review.md",
    "recovery/README.md": A / "recovery" / "README.md",
    "recovery/r2_corrections.md": A / "recovery" / "r2_corrections.md",
    "iso/filing-fetch/scripts/fetch_filing.py": A / "iso" / "filing-fetch" / "scripts" / "fetch_filing.py",
    "iso/filing-fetch/scripts/i04d_schedule.py": A / "iso" / "filing-fetch" / "scripts" / "i04d_schedule.py",
    "iso/filing-fetch/scripts/i04d_participant.py": A / "iso" / "filing-fetch" / "scripts" / "i04d_participant.py",
    "iso/filing-fetch/scripts/i04d_fake_worker.py": A / "iso" / "filing-fetch" / "scripts" / "i04d_fake_worker.py",
    "iso/filing-fetch/tests/test_fetch_filing_lease.py": A / "iso" / "filing-fetch" / "tests" / "test_fetch_filing_lease.py",
    "scratch/patch_i04d.py": A / "scratch" / "patch_i04d.py",
    "before/i04d-red.txt": A / "before" / "i04d-red.txt",
    "before/test_fetch_filing_lease.delivered.py": A / "before" / "test_fetch_filing_lease.delivered.py",
    "after/i04d-green.txt": A / "after" / "i04d-green.txt",
    "after/handoff_json_revalidation.txt": A / "after" / "handoff_json_revalidation.txt",
    "after/all_json_parse_check.txt": A / "after" / "all_json_parse_check.txt",
    "evidence/phase-wall.txt": A / "evidence" / "phase-wall.txt",
    "evidence/negative-case-ledger.txt": A / "evidence" / "negative-case-ledger.txt",
    "evidence/negative-case-detail.txt": A / "evidence" / "negative-case-detail.txt",
    "evidence/i04d_schedule.delivered.py": A / "evidence" / "i04d_schedule.delivered.py",
    "before/00-git-heads.txt": A / "before" / "00-git-heads.txt",
    "before/01-anchor-hashes.txt": A / "before" / "01-anchor-hashes.txt",
    "before/02-catalog-invariant.txt": A / "before" / "02-catalog-invariant.txt",
}

rows = []
structure_failures = []
for rel, path in sorted(FILES.items()):
    if not path.exists():
        rows.append((rel, "MISSING", 0))
        structure_failures.append(f"{rel}: MISSING")
        continue
    rows.append((rel, digest(path), path.stat().st_size))
    if path.suffix == ".json":
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            structure_failures.append(f"{rel}: json.load -> {type(exc).__name__}: {exc}")

stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
header = [
    "# I-04-D a20260919-01 — SEALED canonical hashes (r2 rework, second seal)",
    "#",
    f"# sealed_at_utc: {stamp}",
    f"# rows: {len(rows)}",
    f"# structure_failures: {len(structure_failures)}",
    "#",
    "# 封盘自校验覆盖两项：(a) 每一行的 sha256/字节数与磁盘一致；(b) 清单里每个 *.json 都能",
    "# 被 json.load 解析（第一版封盘只做了 (a)，因此一份不可解析的 handoff.json 也曾被标为",
    "# mismatches: NONE —— 该缺陷已由 recovery/r2_corrections.md 记录并修复）。",
    "#",
    "# 编码注意：evidence/negative-case-*.txt 为 UTF-16LE。",
    "#",
    "# 封盘纪律：本文件写入后 attempt 目录不再写入；此后再写入即判定本轮失效、需重新点审。",
    "",
]
body = [f"{sha}  {length:>8}  {rel}" for rel, sha, length in rows]
(A / "evidence" / "hashes.txt").write_text("\n".join(header + body) + "\n", encoding="utf-8")

print()
print(f"sealed_at_utc      : {stamp}")
print(f"rows               : {len(rows)}")
print(f"structure_failures : {structure_failures if structure_failures else 'NONE'}")
print(f"json files in manifest: {sum(1 for r, p in FILES.items() if p.suffix == '.json')}")
if structure_failures:
    sys.exit(1)
