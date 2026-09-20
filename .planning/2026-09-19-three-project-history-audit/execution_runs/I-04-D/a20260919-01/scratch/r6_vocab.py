"""r6: vocabulary alignment in qualification.json, then re-seal.

Semantics unchanged: the plan's fixed vocabulary is `unmapped` (that stage produced
nothing) / `unproven` (no accuracy assessment was done).  The previous values are kept
and a note explains that this is vocabulary alignment, not a conclusion change.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import pathlib
import time

A = pathlib.Path(__file__).resolve().parents[1]
QUAL = A / "evidence" / "I-04-D" / "qualification.json"


def sha(rel: str) -> str:
    return hashlib.sha256((A / rel).read_bytes()).hexdigest()


def size(rel: str) -> int:
    return (A / rel).stat().st_size


qual = json.loads(QUAL.read_text(encoding="utf-8"))
before = {"sha256": sha("evidence/I-04-D/qualification.json"), "bytes": size("evidence/I-04-D/qualification.json")}

# capture the grants/reservations exactly as they are, to prove they are untouched
grants_before = json.dumps(qual["grants"], ensure_ascii=False, sort_keys=True)
reserved_before = json.dumps(qual["reserved_not_closed"], ensure_ascii=False, sort_keys=True)

qual["disclosure_adaptation_before_bookkeeping_fix"] = qual.get("disclosure_adaptation")
qual["accuracy_before_bookkeeping_fix"] = qual.get("accuracy")
qual["disclosure_adaptation"] = "unmapped"
qual["accuracy"] = "unproven"
qual["vocabulary_note"] = (
    "本文件的阶段词表按全计划统一口径：`unmapped` = 该阶段零产出；`unproven` = 未做任何准确性"
    "评估。原值（disclosure_adaptation/accuracy = not_assessed）保留在 *_before_bookkeeping_fix。"
    "**这是词表归一，不改变任何结论、不改变授予范围、也不关闭任何保留项。**"
)
QUAL.write_text(json.dumps(qual, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
after = {"sha256": sha("evidence/I-04-D/qualification.json"), "bytes": size("evidence/I-04-D/qualification.json")}

reloaded = json.loads(QUAL.read_text(encoding="utf-8"))
grants_same = json.dumps(reloaded["grants"], ensure_ascii=False, sort_keys=True) == grants_before
reserved_same = json.dumps(reloaded["reserved_not_closed"], ensure_ascii=False, sort_keys=True) == reserved_before
print(f"qualification.json  before: {before['sha256']} {before['bytes']} B")
print(f"qualification.json  after : {after['sha256']} {after['bytes']} B")
print(f"grants unchanged          : {grants_same}  ({len(reloaded['grants'])} items)")
print(f"reserved unchanged        : {reserved_same}  ({len(reloaded['reserved_not_closed'])} items)")
print(f"disclosure_adaptation     : {reloaded['disclosure_adaptation']} (was {reloaded['disclosure_adaptation_before_bookkeeping_fix']})")
print(f"accuracy                  : {reloaded['accuracy']} (was {reloaded['accuracy_before_bookkeeping_fix']})")

# ---- re-seal
SEAL = [
    "binding.json", "oracle.md", "decision.md", "commands.json", "changes.diff",
    "handoff.json", "review.md", "recovery/README.md", "recovery/r2_corrections.md",
    "evidence/I-04-D/reviewer_report_r4.md", "evidence/I-04-D/qualification.json",
    "iso/filing-fetch/scripts/fetch_filing.py", "iso/filing-fetch/scripts/i04d_schedule.py",
    "iso/filing-fetch/scripts/i04d_participant.py", "iso/filing-fetch/scripts/i04d_fake_worker.py",
    "iso/filing-fetch/tests/test_fetch_filing_lease.py", "scratch/patch_i04d.py",
    "before/i04d-red.txt", "before/test_fetch_filing_lease.delivered.py",
    "after/i04d-green.txt", "after/i04d-suite-final.txt", "after/scheduler-run-final.txt",
    "after/handoff_json_revalidation.txt", "after/all_json_parse_check.txt",
    "after/hash_regeneration.txt", "after/p3_literal_check.txt",
    "after/r4_verdict_transcription.json", "after/stable_seal_proof.txt",
    "evidence/phase-wall.txt", "evidence/negative-case-ledger.txt",
    "evidence/negative-case-detail.txt", "evidence/i04d_schedule.delivered.py",
]
rows, structure_failures = [], []
for rel in SEAL:
    path = A / rel
    if not path.exists():
        rows.append((rel, "MISSING", 0))
        structure_failures.append(f"{rel}: MISSING")
        continue
    rows.append((rel, sha(rel), size(rel)))
    if path.suffix == ".json":
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            structure_failures.append(f"{rel}: {type(exc).__name__}")

stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
header = [
    "# I-04-D a20260919-01 — SEALED canonical hashes (FINAL; vocabulary-aligned re-seal)",
    "#",
    f"# sealed_at_utc: {stamp}",
    f"# rows: {len(rows)}",
    f"# structure_failures: {len(structure_failures)}",
    f"# structure_failures_detail: {structure_failures if structure_failures else 'NONE'}",
    "#",
    "# status: accepted_scoped —— 裁决由 reviewer 撰写、实现者按字节转录进 review.md；冻结源副本",
    "# evidence/I-04-D/reviewer_report_r4.md；载体 evidence/I-04-D/qualification.json。",
    "#",
    "# 自校验：(a) 每行与磁盘一致；(b) 清单内每个 *.json 可 json.load。handoff.json 不自称自身哈希。",
    "# 零写入谓词：ZW(s,E) ≡ 「<A> 下除 E 之外没有文件 mtime > s」，s = 本文件 mtime，",
    "# E = {after/stable_seal_proof.txt}。",
    "#",
    "# 本轮唯一改动：qualification.json 的阶段词表归一并保留原值（不改语义、不关闭保留项）。",
    "#",
    "# 编码注意：evidence/negative-case-*.txt 为 UTF-16LE。",
    "#",
    "# 本 attempt 已关闭：不再写入本目录；再写入即判定失效、需重新点审。",
    "",
]
hashes_path = A / "evidence" / "hashes.txt"
hashes_path.write_text(
    "\n".join(header + [f"{s}  {n:>8}  {r}" for r, s, n in rows]) + "\n", encoding="utf-8"
)
seal_mtime = hashes_path.stat().st_mtime
print()
print(f"sealed_at_utc      : {stamp}")
print(f"rows               : {len(rows)}   structure_failures: {structure_failures if structure_failures else 'NONE'}")

print("\nwaiting 135 s to re-prove ZW...")
time.sleep(135)
newer = [
    p.relative_to(A).as_posix()
    for p in A.rglob("*")
    if p.is_file()
    and p.stat().st_mtime > seal_mtime
    and "venv" not in p.parts
    and p.relative_to(A).as_posix() != "after/stable_seal_proof.txt"
]
checked_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
lines = [
    "I-04-D FINAL stable-seal proof (ZW predicate) — after vocabulary alignment",
    f"sealed_at_utc : {stamp}",
    f"checked_at_utc: {checked_at}",
    "wait_seconds  : 135",
    "ZW(s,E): no file under <A> other than E={after/stable_seal_proof.txt} has mtime > s",
    f"violations    : {len(newer)}",
]
lines += [f"  NEWER  {rel}" for rel in newer]
if not newer:
    lines.append("  (none - ZW holds)")
(A / "after" / "stable_seal_proof.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
