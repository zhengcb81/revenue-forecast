"""r5c: record the transcribed verdict as a CARRIER (not a self-signature) and re-seal.

The verdict was written by the reviewer and transcribed byte-for-byte by the implementer.
This script only records bookkeeping: status, the qualified scope (9 grants), the 6
reserved items (copied verbatim in substance, none closed), the P3 notes, and the seal.
"""

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


proof = json.loads((A / "after" / "r4_verdict_transcription.json").read_text(encoding="utf-8"))

GRANTS = [
    "gate 修复经 reviewer 自造探针独立验证（`gate:NO-SUCH-POINT@A` 未创建 .reached、rc=0、stderr 0 字节）",
    "GREEN 21 passed / rc=0，且 READ 对交付版套件自跑 18 failed / 1 passed / 2 skipped / rc=1",
    "主证据与最终 harness 字节同源复核（19 个 summary mtime 全晚于 scheduler；同字节重跑 rc=0、19/19 harness_error 空、18/19 可观测量逐一相同）",
    "F-L5 共存性（pause=1/resume=1、B.after_enter 两条同代 gen=1）",
    "M5 单点反例证明不变量可红（mutant 82b4fdc4… ⇒ test_fetch_filing_lease.py:103 assert 0 == 1）—— 本卡唯一的变异证据",
    "封盘 30 数据行逐行对盘、无自指行；零写入谓词 ZW(s,E) 成立（三次采样 + 171.8 分钟后复采仍为 0）",
    "handoff.json 合法 JSON（52 键）、不自称自身哈希、defect_ledger_count=10",
    "生产三仓零写入与 <PLAN>\\reviews 未写（两次采样）",
    "recovery/r2_corrections.md 的 sha256 恰等于移动时记录的 appendix sha256（7d080f68…），15/15 非空行逐行一致",
]
RESERVED = [
    "无实现者侧变异证明（M1–M11 未跑；仅有 reviewer 的 M5 反例）",
    "N5/N6/N7 无调度器级原始记录（仅 pytest 断言）",
    "无“存活第三方 owner”专用用例",
    "无“A 释放与 B 获取并发”的确定性用例",
    "POSIX/SMB 与真实 worker/catalog/provider/联网 未执行",
    "oracle.md R2-3 的 owner 裁定项原样移交，未自裁",
]
CARRIER_NOTE = (
    "本裁决由 reviewer 撰写、实现者按字节转录（transcription，非自签）。实现者未写 verdict、"
    "未关闭任何保留范围、未自裁 R2-3。三条固定声明（不改变生产仓字节 / 不删除临时 owner 状态 / "
    "reviewer 未写 PLAN\\reviews 且未跑 git 写命令）逐字保留在转录块内。"
)

# ---------------------------------------------------------------- qualification.json
qual_path = A / "evidence" / "I-04-D" / "qualification.json"
qual = {
    "card_id": "I-04-D",
    "attempt_id": "a20260919-01",
    "status": "accepted_scoped",
    "status_before_bookkeeping_fix": "review_pending",
    "verdict_author": "independent reviewer (r4 final point review)",
    "verdict_carrier": {
        "file": "review.md",
        "block": "## §10 独立验收最终裁决 ... ### 恢复规则",
        "report_copy_path": proof["report_copy"]["path"],
        "report_copy_sha256": proof["report_copy"]["sha256"],
        "report_copy_bytes": proof["report_copy"]["bytes"],
        "review_md_sha256_before": proof["review_md"]["sha256_before"],
        "review_md_bytes_before": proof["review_md"]["bytes_before"],
        "review_md_sha256_after": proof["review_md"]["sha256_after"],
        "review_md_bytes_after": proof["review_md"]["bytes_after"],
        "old_bytes_are_exact_prefix": proof["review_md"]["old_bytes_are_exact_prefix"],
        "transcription_deviation": proof["criterion_deviation"],
    },
    "reviewer_frozen_revision": {
        "review.md": "37191 B / 81516b2ac06a41dca5978e744b540f8b2f33d7ba28297e7c792c32f9c50fcf09 (before the append)",
        "handoff.json": "55936 B / 733cb40d…",
        "oracle.md": "42257 B / 428a0a96…",
        "evidence/hashes.txt": "3977 B / 9f6810bb…",
        "impl": "a72546c5… / 126274 B",
        "scheduler": "fd163a27… / 35388 B",
        "suite": "27f492b1… / 30422 B",
        "after/scheduler-run-final.txt": "3df2bcc3…",
        "after/i04d-suite-final.txt": "6503819d…",
        "after/stable_seal_proof.txt": "def44bf2…",
        "recovery/r2_corrections.md": "7d080f68…",
    },
    "grants": GRANTS,
    "reserved_not_closed": RESERVED,
    "p3_notes": [
        "r3 对 oracle.md 追加区做过两处就地编辑（已在 handoff.oracle_frozen_region_in_place_edits 登记并附前像）"
        "⇒ r2 认证的“内容上只追加”自 r3 起不再成立；冻结 §0–§4 正文未受影响。",
        "after/all_json_parse_check.txt 的计数（763）是 r4 新增约 62 个 case JSON 之前的旧快照；"
        "reviewer 自跑为 825 个、0 失败 —— 事实成立但计数陈旧，如实登记。",
        "零写入谓词的精确定义：ZW(s,E) ≡ 「<A> 下除 E 之外没有文件 mtime > s」，"
        "s = 封盘文件 mtime 05:31:21.623，E = {after/stable_seal_proof.txt}；证明文件自身写在 04:33:37Z，"
        "比其记录的 checked_at_utc 晚 1 秒。",
    ],
    "status_note": CARRIER_NOTE,
    "formula": "accepted_scoped",
    "accuracy": "not_assessed",
    "disclosure_adaptation": "not_assessed",
}
qual_path.write_text(json.dumps(qual, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
print(f"qualification.json written: {size('evidence/I-04-D/qualification.json')} B")

# ---------------------------------------------------------------- handoff.status
handoff_path = A / "handoff.json"
handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
handoff["status_before_bookkeeping_fix"] = handoff.get("status")
handoff["status"] = "accepted_scoped"
handoff["reviewer_status"] = (
    "r4 stable-seal final point review = accepted_scoped (supersedes the r1 and r2 "
    "changes_required). Transcribed by the implementer; the verdict text lives in review.md "
    "and its frozen source copy is evidence/I-04-D/reviewer_report_r4.md."
)
handoff["review_carrier"] = {
    "verdict_in": "review.md (transcribed block)",
    "report_copy": "evidence/I-04-D/reviewer_report_r4.md",
    "report_copy_sha256": proof["report_copy"]["sha256"],
    "qualification": "evidence/I-04-D/qualification.json",
    "grants": GRANTS,
    "reserved_not_closed": RESERVED,
    "reserved_note": "六项保留范围一项未关闭、未弱化；oracle.md R2-3 原样移交 owner。",
}
handoff["attempt_closed"] = True
handoff["final_writes"] = (
    "本次为 attempt 的最后一次写入：review.md 追加裁决块（字节前缀已证）、"
    "qualification.json、handoff.json 记账、evidence/hashes.txt 重新封盘。"
    "此后不再写入本 attempt 目录。"
)
handoff_path.write_text(json.dumps(handoff, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
print(f"handoff.json: status=accepted_scoped, {size('handoff.json')} B")

# ---------------------------------------------------------------- final seal
SEAL = {
    rel: rel
    for rel in (
        "binding.json",
        "oracle.md",
        "decision.md",
        "commands.json",
        "changes.diff",
        "handoff.json",
        "review.md",
        "recovery/README.md",
        "recovery/r2_corrections.md",
        "evidence/I-04-D/reviewer_report_r4.md",
        "evidence/I-04-D/qualification.json",
        "iso/filing-fetch/scripts/fetch_filing.py",
        "iso/filing-fetch/scripts/i04d_schedule.py",
        "iso/filing-fetch/scripts/i04d_participant.py",
        "iso/filing-fetch/scripts/i04d_fake_worker.py",
        "iso/filing-fetch/tests/test_fetch_filing_lease.py",
        "scratch/patch_i04d.py",
        "before/i04d-red.txt",
        "before/test_fetch_filing_lease.delivered.py",
        "after/i04d-green.txt",
        "after/i04d-suite-final.txt",
        "after/scheduler-run-final.txt",
        "after/handoff_json_revalidation.txt",
        "after/all_json_parse_check.txt",
        "after/hash_regeneration.txt",
        "after/p3_literal_check.txt",
        "after/r4_verdict_transcription.json",
        "after/stable_seal_proof.txt",
        "evidence/phase-wall.txt",
        "evidence/negative-case-ledger.txt",
        "evidence/negative-case-detail.txt",
        "evidence/i04d_schedule.delivered.py",
    )
    if (A / rel).exists()
}
rows, structure_failures = [], []
for rel in sorted(SEAL):
    path = A / rel
    rows.append((rel, sha(rel), size(rel)))
    if path.suffix == ".json":
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001
            structure_failures.append(f"{rel}: {type(exc).__name__}")

stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
header = [
    "# I-04-D a20260919-01 — SEALED canonical hashes (FINAL, attempt closed)",
    "#",
    f"# sealed_at_utc: {stamp}",
    f"# rows: {len(rows)}",
    f"# structure_failures: {len(structure_failures)}",
    f"# structure_failures_detail: {structure_failures if structure_failures else 'NONE'}",
    "#",
    "# status: accepted_scoped —— 裁决由 reviewer 撰写，实现者按字节转录进 review.md；",
    "# 冻结源副本 evidence/I-04-D/reviewer_report_r4.md，载体 evidence/I-04-D/qualification.json。",
    "#",
    "# 自校验：(a) 每行与磁盘一致；(b) 清单内每个 *.json 可 json.load。handoff.json 不自称自身哈希。",
    "# 零写入谓词：ZW(s,E) ≡ 「<A> 下除 E 之外没有文件 mtime > s」，s = 本文件 mtime，",
    "# E = {after/stable_seal_proof.txt}。",
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
print(f"sealed_at_utc      : {stamp}")
print(f"rows               : {len(rows)}   structure_failures: {structure_failures if structure_failures else 'NONE'}")

print("\nwaiting 135 s to prove ZW...")
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
    "I-04-D FINAL stable-seal proof (ZW predicate)",
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
