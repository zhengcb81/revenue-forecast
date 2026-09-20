"""Step 3+4: land the carrier (qualification.json + handoff status) and seal.

Lands the TRANSCRIBED reviewer verdict (not a self-signature):
  * evidence/I-05-A/qualification.json  (new; structure follows the plan's
    existing qualification.json carriers)
  * handoff.json.status -> accepted_scoped, previous value kept
  * four P3 corrections and four owner items preserved verbatim
  * seal record with the sealed_at_utc, manifest line count, structural check and
    the exact zero-write predicate (excluding the seal proof itself)

Usage: <py> -X utf8 -B scripts/r4_land_carrier.py
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import subprocess
from pathlib import Path

CARD = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-05-A\a20260919-01"
)
PLAN = CARD.parents[2]
CW = Path(r"C:\Users\郑曾波\Projects\company-wiki")
RF = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")

P3_ITEMS = [
    {
        "id": "P3-1",
        "reviewer_text": "oracle 附录 C 的前像字节数 14924 B 有误（实测 r3 末态 23204 B）",
        "disposition": "corrected by append (oracle 附录 D)；C 正文未改",
        "owner_item": False,
    },
    {
        "id": "P3-2",
        "reviewer_text": "after/prod-anchor-hashes-after.json.attempt_fixed 由 r3 的三元组变为 null",
        "disposition": "r4 三元组已补写回该字段（追加式：旧值保留在 attempt_fixed_before_bookkeeping_fix）",
        "owner_item": False,
    },
    {
        "id": "P3-3",
        "reviewer_text": "evidence/p1-mutations.json 键名 I1_offsets_plus_one 对应 delta=2",
        "disposition": "键名注记追加进 evidence/README.md 与 oracle 附录 D",
        "owner_item": False,
    },
    {
        "id": "P3-4",
        "reviewer_text": "binding.json 仍记旧 RF HEAD 7d7ea1ed…（影响为零）",
        "disposition": "HEAD 补记追加进 binding.json.downstream_head_note（不改既有键）+ oracle 附录 D",
        "owner_item": False,
    },
]

OWNER_ITEMS = [
    {
        "id": "OWNER-1",
        "question": "C13 是否立卡",
        "status": "UNDECIDED — owner 裁定；实现者未代裁",
        "reviewer_position": "不阻塞其判定",
    },
    {
        "id": "OWNER-2",
        "question": "~25% 抖动是否立卡",
        "status": "UNDECIDED — owner 裁定；实现者未代裁",
        "reviewer_position": "不阻塞其判定",
    },
    {
        "id": "OWNER-3",
        "question": "深路径 WinError 206 是否改短 basetemp 约定",
        "status": "UNDECIDED — owner 裁定；实现者未代裁",
        "reviewer_position": "不阻塞其判定",
    },
    {
        "id": "OWNER-4",
        "question": "C12 形式",
        "status": "UNDECIDED — owner 裁定；实现者未代裁",
        "reviewer_position": "不阻塞其判定",
    },
]

SCOPE_GRANTED = [
    "sections 消费者资格门（FROZEN-1/2）＋反例闭合：c0–c8、n2a/n2c、p2、n3；"
    "m1/m2/m2b/m2c/m3/m3b/m4/m4b/m7；被审方 I1/I2/I3；"
    "reviewer 自造 only_second / midline / fabricated / plus1_content / roleswap",
    "reviewer 原话：第三轮的 P1-A/P1-B/P1-C（同一根因：记录偏移从未与内容强制比对）经独立复算确认已关闭",
]

SCOPE_NOT_GRANTED = [
    "D-W05 OPEN-1..7 的一切决策（含历史无哈希工件的回填/重算、as_of_date 口径）",
    "I-05-B / I-05-C 不得据此开工",
    "disclosure_adaptation / accuracy 按原登记另行验收",
]

SCOPE_LIMITS = [
    "偏移 +1 且内容不变的声明仍可被解释为另一个合法 origin（文本完全相同，非内容旁路），"
    "故 char_start 不应被当作精确索引",
    "role/title 不参与绑定校验（roleswap2 会把另一节文本以本节的 role/title 服务），"
    "这是设计边界而非本次缺陷；SectionEntry 文档与附录应写明 "
    "'role/title 由 index 声明、不参与绑定校验'",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    transcription = json.loads(
        (CARD / "after" / "r4_verdict_transcription.json").read_text(encoding="utf-8")
    )
    freeze = json.loads(
        (CARD / "evidence" / "I-05-A" / "reviewer_report_r4.freeze.json").read_text(
            encoding="utf-8"
        )
    )
    review_bytes = (CARD / "review.md").read_bytes()

    # ---------------- qualification.json ---------------------------------
    qual_dir = CARD / "evidence" / "I-05-A"
    qual = {
        "card_id": "I-05-A",
        "attempt_id": "a20260919-01",
        "formula": {
            "state": "accepted_scoped",
            "state_before_bookkeeping_fix": "review_pending",
        },
        "disclosure_adaptation": "unmapped",
        "accuracy": "unproven",
        "round": 4,
        "carrier": {
            "card_copy_of_report": str(
                qual_dir / "reviewer_report_r4.md"
            ),
            "card_copy_sha256": freeze["card_copy_sha256"],
            "card_copy_bytes": freeze["card_copy_bytes"],
            "byte_identical_to_source": freeze["byte_identical"],
            "source_path_at_freeze": freeze["source_path"],
            "source_bytes_at_freeze": freeze["source_bytes"],
            "source_sha256_at_freeze": freeze["source_sha256"],
            "cited_by_parent": freeze["cited_by_parent"],
            "cited_vs_live_discrepancy": freeze["discrepancy"],
            "verdict_block_in_report": {
                "identified_by": freeze["block_locator"],
                "line_range_inclusive_1_based": freeze["verdict_block"][
                    "start_line_1based"
                ],
                "line_range_end_1_based": freeze["verdict_block"]["end_line_1based"],
                "bytes": freeze["verdict_block"]["bytes"],
                "sha256": freeze["verdict_block"]["sha256"],
                "signature_tokens": freeze["verdict_block"]["signature_tokens_present"],
            },
            "transcribed_into_review_md": {
                "review_md": str(CARD / "review.md"),
                "byte_offset_start": transcription["appended_region_in_review_md"][
                    "start_byte_offset"
                ],
                "byte_offset_stop": transcription["appended_region_in_review_md"][
                    "stop_byte_offset"
                ],
                "start_line_1based": transcription["appended_region_in_review_md"][
                    "start_line_1based"
                ],
                "before_bytes": transcription["before_bytes"],
                "before_sha256": transcription["before_sha256"],
                "after_bytes": transcription["after_bytes"],
                "after_sha256": transcription["after_sha256"],
                "old_bytes_are_exact_prefix": transcription[
                    "old_bytes_are_exact_prefix"
                ],
                "block_byte_identical_to_report": transcription[
                    "block_byte_identical_to_report"
                ],
                "no_normalisation": transcription["no_normalisation"],
            },
        },
        "declarations": {
            "implementer_signed": False,
            "implementer_never_signs_acceptance": True,
            "authority": "acceptance was written by an independent reviewer, not by the implementer",
        },
        "scope": {
            "granted": SCOPE_GRANTED,
            "not_granted": SCOPE_NOT_GRANTED,
            "disclosed_limits": SCOPE_LIMITS,
            "reviewer_verdict_word": "accepted_scoped",
        },
        "open_reviewer_findings": {
            "P3_non_blocking": P3_ITEMS,
            "owner_items_undecided": OWNER_ITEMS,
        },
        "unsigned_gates_preserved": {
            "section_extractor": (
                "iso/fixed/section_extractor.py 仍只有 sec.status='completed'（328/341），"
                "无 generator 版本比较"
            ),
            "decision_md": "D-W05 OPEN-1..5 未签、§7 OPEN-7 仍在",
            "blocked_by": "D-W05 七项专业决策未签：I-05-B/I-05-C 在签名前不得开工",
        },
        "bookkeeping": {
            "recorded_by": "carrier-landing bookkeeping pass (delegated subagent), 2026-09-20",
            "what_this_pass_did": (
                "froze the reviewer report into the card, transcribed its verdict block "
                "byte-exactly into review.md, and landed the carrier fields; no product code, "
                "no oracle body, no frozen appendix was modified"
            ),
        },
        "not_verified": [
            "未跑真实跨仓消费入口（sections-list CLI→业务后果）；artifact_read 语义属 I-05-B",
            "未测生产规模（25.7M 行 / 49.7 GB）与并发/锁；未跑 CW 全量套件",
            "role/title ↔ 内容一致性的可行性未评估",
            "旧 RED 原字节不可恢复，机器可核性无法补证",
            "_slice_roots=(derived,) 未与 service.query_source_bundle 真实传参交叉验证",
            "attempt 目录 MAX_PATH 行为未系统测",
        ],
    }
    (qual_dir / "qualification.json").write_text(
        json.dumps(qual, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )

    # ---------------- handoff.json ---------------------------------------
    handoff_path = CARD / "handoff.json"
    handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
    before_status = handoff["status"]
    handoff["status_before_bookkeeping_fix"] = before_status
    handoff["status"] = "accepted_scoped"
    handoff["reviewer_status"] = (
        "accepted_scoped by the independent reviewer (round 4). The implementer did not sign; "
        "the verdict text is transcribed verbatim into review.md and its carrier is "
        "evidence/I-05-A/qualification.json."
    )
    handoff["accepted_scoped_scope"] = {
        "granted": SCOPE_GRANTED,
        "not_granted": SCOPE_NOT_GRANTED,
        "disclosed_limits": SCOPE_LIMITS,
        "disclosure_adaptation": "unmapped",
        "accuracy": "unproven",
    }
    handoff["reviewer_findings_open"] = {
        "P3_non_blocking": P3_ITEMS,
        "owner_items_undecided": OWNER_ITEMS,
        "unsigned_gates_preserved": qual["unsigned_gates_preserved"],
    }
    handoff["carrier"] = {
        "qualification_json": "execution_runs/I-05-A/a20260919-01/evidence/I-05-A/qualification.json",
        "reviewer_report_card_copy": "execution_runs/I-05-A/a20260919-01/evidence/I-05-A/reviewer_report_r4.md",
        "reviewer_report_sha256": freeze["card_copy_sha256"],
        "verdict_block_in_review_md": {
            "start_byte_offset": transcription["appended_region_in_review_md"][
                "start_byte_offset"
            ],
            "start_line_1based": transcription["appended_region_in_review_md"][
                "start_line_1based"
            ],
            "block_sha256": transcription["block"]["sha256"],
            "review_md_before_sha256": transcription["before_sha256"],
            "review_md_after_sha256": transcription["after_sha256"],
            "old_bytes_are_exact_prefix": transcription["old_bytes_are_exact_prefix"],
        },
    }
    handoff_path.write_text(
        json.dumps(handoff, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )

    # ---------------- P3 corrections (append-only) ------------------------
    oracle = CARD / "oracle.md"
    text = oracle.read_text(encoding="utf-8")
    assert "附录 D" not in text
    appendix_d = """
---

# 附录 D（追加式，2026-09-19 第四轮复审后；**不修改正文、附录 A/B/C**）

本附录只做**记账更正**，不改写任何已冻结正文。第四轮复审裁决 `accepted_scoped`，
以下 4 项为其"不阻塞、建议随下一卡追加更正"的 P3。

## D.1 P3-1 附录 C 的前像字节数更正

附录 C 开头写"`oracle.md` 在 r3 结尾时为 14924 B"。**该数字有误**：复审实测 r3 末态为
**23204 B**（附录 A 起点 16119、B 起点 20726、C 起点 23212）；14924 落在正文 §5
"未签专业决策"之内。**C 正文不改**，以本条为准。追加性本身已由复审以字节前缀比对独立证明
（`r4[:23204] == r3 全文`）。

## D.2 P3-2 `attempt_fixed` 字段补写

`after/prod-anchor-hashes-after.json.attempt_fixed` 在 r3 曾是三元组，r4 一度变成 `null`。
现已**追加式补回** r4 的三元组（`section_query.py` = `06a1a6ea…ebceb7`、
`section_extractor.py` = `0f201c68…39f3f0`、`max_function_complexity_section_query` = `11`），
旧值（`null`）保留在同文件的 `attempt_fixed_before_bookkeeping_fix`。

## D.3 P3-3 键名注记

`evidence/p1-mutations.json` 的键名 `I1_offsets_plus_one` 实际对应
`mutation_detail.delta = 2`（+1 位移在冻结 trim 语义下仍可能复现同一段文本，故取 +2 作为决定性伪造）。
键名**不改**（改键会破坏既有字据的稳定引用），注记见 `evidence/README.md` 与 `evidence/p1-mutations.json.key_naming_note`。

## D.4 P3-4 HEAD 补记

`binding.json` 仍记 attempt 开始时的 RF HEAD `7d7ea1ed…`；该值作为**历史绑定**保留不改。
live HEAD 已多次推进（复审实测 `cc78c5298acd5a5ff8b898d9aa237fc5a8559979`；
本记账时刻实测见 `after/r4_seal.json` 的 `seal_reference`），影响为零：
本卡只做只读 git 查询。
"""
    oracle.write_text(text.rstrip() + "\n" + appendix_d, encoding="utf-8", newline="\n")

    # binding.json: append-only note
    binding_path = CARD / "binding.json"
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    binding["downstream_head_note"] = (
        "prod_git_baselines.RF.HEAD (7d7ea1ed…) is the attempt-start binding and is kept "
        "unchanged. The live HEAD has advanced many times since (reviewer measured "
        "cc78c5298acd5a5ff8b898d9aa237fc5a8559979; see after/r4_seal.json). This card only "
        "performed read-only git queries; impact on the evidence is zero."
    )
    binding_path.write_text(
        json.dumps(binding, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )

    # evidence README + p1-mutations key note (append-only)
    readme = CARD / "evidence" / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8").rstrip()
        + "\n\n## 键名注记（第四轮复审 P3-3）\n\n"
        "`p1-mutations.json` 的键名 `I1_offsets_plus_one` 实际对应 `mutation_detail.delta = 2`。\n"
        "原因：冻结的 trim 语义会剥掉边界换行符，+1 位移在修复后仍可能复现同一段文本；\n"
        "因此取 +2 作为决定性伪造。键名不改（避免破坏既有字据的稳定引用）。\n",
        encoding="utf-8",
        newline="\n",
    )
    p1_path = CARD / "evidence" / "p1-mutations.json"
    p1 = json.loads(p1_path.read_text(encoding="utf-8"))
    p1["key_naming_note"] = (
        "I1_offsets_plus_one carries mutation_detail.delta = 2 (see evidence/README.md); "
        "noted per round-4 review P3-3, the key is intentionally left unchanged."
    )
    p1_path.write_text(
        json.dumps(p1, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )

    # prod-anchor-hashes-after.json: restore the r4 triple additively
    anchor_path = CARD / "after" / "prod-anchor-hashes-after.json"
    anchors = json.loads(anchor_path.read_text(encoding="utf-8"))
    anchors["attempt_fixed_before_bookkeeping_fix"] = anchors.get("attempt_fixed")
    anchors["attempt_fixed"] = {
        "iso/fixed/section_query.py": sha(CARD / "iso" / "fixed" / "section_query.py"),
        "iso/fixed/section_extractor.py": sha(CARD / "iso" / "fixed" / "section_extractor.py"),
        "max_function_complexity_section_query": 11,
    }
    anchor_path.write_text(
        json.dumps(anchors, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )

    # ---------------- seal ------------------------------------------------
    manifest = sorted(
        str(p.relative_to(CARD)).replace("\\", "/")
        for p in CARD.rglob("*")
        if p.is_file() and "iso/venv" not in str(p).replace("\\", "/")
    )
    bad_json = []
    for rel in manifest:
        if rel.endswith(".json"):
            try:
                json.loads((CARD / rel).read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                bad_json.append({"path": rel, "error": str(exc)[:120]})

    porcelain = {}
    for name, repo in (("CW", CW), ("RF", RF)):
        result = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        porcelain[name] = sorted(l for l in result.stdout.splitlines() if l.strip())
    heads = {}
    for name, repo in (("CW", CW), ("RF", RF)):
        heads[name] = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True, text=True,
        ).stdout.strip()

    plan_reviews = PLAN / "reviews"
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    seal = {
        "card_id": "I-05-A",
        "attempt_id": "a20260919-01",
        "sealed_at_utc": stamp,
        "statement": "No further writes to this attempt directory after this seal.",
        "manifest_line_count": len(manifest),
        "manifest": manifest,
        "structural_check": {
            "rule": "every .json inside the manifest must json.load",
            "json_files_checked": sum(1 for rel in manifest if rel.endswith(".json")),
            "failures": bad_json,
            "all_ok": not bad_json,
        },
        "zero_write_predicate": {
            "text": (
                "no file under the product repos changed, i.e. git status --porcelain shows only "
                "the pre-existing entries plus this attempt's own directory; the seal proof file "
                "itself (after/r4_seal.json) is EXCLUDED from its own manifest by construction"
            ),
            "product_repo_porcelain": porcelain,
            "product_repo_heads": heads,
            "cw_porcelain_expected": [" M CLAUDE.md", " M README.md"],
            "cw_porcelain_matches_expected": porcelain["CW"] == [" M CLAUDE.md", " M README.md"],
            "rf_non_attempt_lines": [
                line for line in porcelain["RF"]
                if "I-05-A" not in line and "I-06-A" not in line
            ],
            "plan_reviews_written": False,
            "git_write_commands_run": [],
        },
        "seal_reference": {
            "review_md_sha256": hashlib.sha256(review_bytes).hexdigest(),
            "qualification_json_sha256": sha(qual_dir / "qualification.json"),
            "reviewer_report_sha256": freeze["card_copy_sha256"],
        },
        "not_decided_here": [item["question"] for item in OWNER_ITEMS],
    }
    seal["zero_write_predicate"]["rf_non_attempt_lines_count"] = len(
        seal["zero_write_predicate"]["rf_non_attempt_lines"]
    )
    (CARD / "after" / "r4_seal.json").write_text(
        json.dumps(seal, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    print(json.dumps({
        "qualification": str(qual_dir / "qualification.json"),
        "handoff_status": handoff["status"],
        "status_before": before_status,
        "sealed_at_utc": stamp,
        "manifest_line_count": len(manifest),
        "json_files_checked": seal["structural_check"]["json_files_checked"],
        "json_failures": bad_json,
        "cw_porcelain": porcelain["CW"],
        "cw_ok": seal["zero_write_predicate"]["cw_porcelain_matches_expected"],
        "rf_non_attempt_lines": seal["zero_write_predicate"]["rf_non_attempt_lines_count"],
        "rf_head": heads["RF"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
