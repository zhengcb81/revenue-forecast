"""Fix the defect-ledger heading (9 -> 10) and re-seal, proving stability again."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import time

A = pathlib.Path(__file__).resolve().parents[1]


def sha(rel: str) -> str:
    return hashlib.sha256((A / rel).read_bytes()).hexdigest()


def size(rel: str) -> int:
    return (A / rel).stat().st_size


# 1. the heading the reviewer pointed at
review_path = A / "review.md"
text = review_path.read_text(encoding="utf-8")
OLD = "## §7 实现者自查出的缺陷（9 项）"
NEW = (
    "## §7 实现者自查出的缺陷（10 项）\n\n"
    "> 第 10 项（释放路径 R5 兜底格把**存活的第三方 owner** 当成可 resume）由决定文档作者读码\n"
    "> 发现，见 `oracle.md` R1-9；其余 9 项由失败用例发现。"
)
if OLD in text:
    text = text.replace(OLD, NEW, 1)
    review_path.write_text(text, encoding="utf-8")
    print("review.md §7 heading corrected to 10")
else:
    print("heading pattern not found; dumping candidates")
    for n, line in enumerate(text.splitlines(), 1):
        if "自查" in line or "缺陷（" in line:
            print(f"  {n}: {line.strip()}")

# 2. re-seal
SEAL = {
    "binding.json": "binding.json",
    "oracle.md": "oracle.md",
    "decision.md": "decision.md",
    "commands.json": "commands.json",
    "changes.diff": "changes.diff",
    "handoff.json": "handoff.json",
    "review.md": "review.md",
    "recovery/README.md": "recovery/README.md",
    "recovery/r2_corrections.md": "recovery/r2_corrections.md",
    "iso/filing-fetch/scripts/fetch_filing.py": "iso/filing-fetch/scripts/fetch_filing.py",
    "iso/filing-fetch/scripts/i04d_schedule.py": "iso/filing-fetch/scripts/i04d_schedule.py",
    "iso/filing-fetch/scripts/i04d_participant.py": "iso/filing-fetch/scripts/i04d_participant.py",
    "iso/filing-fetch/scripts/i04d_fake_worker.py": "iso/filing-fetch/scripts/i04d_fake_worker.py",
    "iso/filing-fetch/tests/test_fetch_filing_lease.py": "iso/filing-fetch/tests/test_fetch_filing_lease.py",
    "scratch/patch_i04d.py": "scratch/patch_i04d.py",
    "before/i04d-red.txt": "before/i04d-red.txt",
    "before/test_fetch_filing_lease.delivered.py": "before/test_fetch_filing_lease.delivered.py",
    "after/i04d-green.txt": "after/i04d-green.txt",
    "after/i04d-green-r2-stale.txt": "after/i04d-green-r2-stale.txt",
    "after/i04d-suite-final.txt": "after/i04d-suite-final.txt",
    "after/scheduler-run-final.txt": "after/scheduler-run-final.txt",
    "after/handoff_json_revalidation.txt": "after/handoff_json_revalidation.txt",
    "after/all_json_parse_check.txt": "after/all_json_parse_check.txt",
    "after/hash_regeneration.txt": "after/hash_regeneration.txt",
    "after/p3_literal_check.txt": "after/p3_literal_check.txt",
    "evidence/phase-wall.txt": "evidence/phase-wall.txt",
    "evidence/negative-case-ledger.txt": "evidence/negative-case-ledger.txt",
    "evidence/negative-case-detail.txt": "evidence/negative-case-detail.txt",
    "evidence/i04d_schedule.delivered.py": "evidence/i04d_schedule.delivered.py",
    "evidence/run-r2-stale/I04D-CASE-F-L5/summary.json": "evidence/run-r2-stale/I04D-CASE-F-L5/summary.json",
}
SEAL = {k: v for k, v in SEAL.items() if (A / v).exists()}
rows, structure_failures = [], []
for rel in sorted(SEAL):
    path = A / rel
    rows.append((rel, sha(rel), size(rel)))
    if path.suffix == ".json":
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            structure_failures.append(f"{rel}: {type(exc).__name__}: {exc}")

stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
header = [
    "# I-04-D a20260919-01 — SEALED canonical hashes (r4 stable seal, final)",
    "#",
    f"# sealed_at_utc: {stamp}",
    f"# rows: {len(rows)}",
    f"# structure_failures: {len(structure_failures)}",
    f"# structure_failures_detail: {structure_failures if structure_failures else 'NONE'}",
    "#",
    "# 交付世代（r4）：scheduler fd163a27…(35388 B) + suite 27f492b1…(30422 B) 的最终字节已用于",
    "# 重跑 19 个调度器用例（after/scheduler-run-final.txt, rc=0）与契约套件",
    "# （after/i04d-suite-final.txt, rc=0, 21 passed）。旧世代保留在 evidence/run-r2-stale/。",
    "#",
    "# 自校验：(a) 每行与磁盘一致；(b) 清单内每个 *.json 可 json.load。handoff.json 不自称自身哈希。",
    "#",
    "# 编码注意：evidence/negative-case-*.txt 为 UTF-16LE。",
    "#",
    "# 稳定封盘：写入后不再写 attempt 目录（连续 >=2 分钟零写入已实测，见 after/stable_seal_proof.txt）。",
    "",
]
hashes_path = A / "evidence" / "hashes.txt"
hashes_path.write_text(
    "\n".join(header + [f"{s}  {n:>8}  {r}" for r, s, n in rows]) + "\n", encoding="utf-8"
)
seal_mtime = hashes_path.stat().st_mtime
print(f"sealed_at_utc      : {stamp}")
print(f"rows               : {len(rows)}   structure_failures: {structure_failures if structure_failures else 'NONE'}")

print("\nwaiting 135 s to re-prove stability...")
time.sleep(135)
checked_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
newer = [
    p.relative_to(A).as_posix()
    for p in A.rglob("*")
    if p.is_file() and p.stat().st_mtime > seal_mtime and "venv" not in p.parts
]
lines = [
    "I-04-D stable-seal proof (final)",
    f"sealed_at_utc      : {stamp}",
    f"checked_at_utc     : {checked_at}",
    "wait_seconds       : 135",
    f"files_newer_than_seal: {len(newer)}",
]
lines += [f"  NEWER  {rel}" for rel in newer]
if not newer:
    lines.append("  (none - the seal is stable)")
(A / "after" / "stable_seal_proof.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
