"""APPEND-ONLY transcription of the independent reviewer's r2 verdict into each card's
review.md, plus the r3 sidecar that records the append and the four P3 wording corrections.

Hard rules honoured by this script:
  * review.md (and every frozen artefact) is opened in BINARY APPEND mode only. The existing
    bytes are never rewritten, so the new file is guaranteed to have the old file's bytes as
    an exact prefix.
  * The prefix property is MEASURED (new_bytes.startswith(old_bytes)) and recorded, not
    asserted.
  * Nothing under recovery/precorrection/ is touched (those are v1 CRLF bytes by design).
  * No product file is touched.

Run (twice, once with --check-only first if you like):
  python -X utf8 -B scripts/apply_review_r3.py --card M25 --attempt-root <attempt> --check-only
  python -X utf8 -B scripts/apply_review_r3.py --card M25 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os

# ---------------------------------------------------------------- reviewer §8.2 fill-ins
FILL = {
    "M25": {
        "expected_guard_message": "retired_units exceeds opening installed cohort: FY2027",
        "positive": "[300.0]",
        "continuity": "[300.0, 330.0]",
        "defaults": "[0.0]",
        "in_sha": "4cacbf92a6883d3a688a61d68f565b3c33134fe12c3bf07fd5f8613e4a02a592",
        "or_sha": "35f1dba3ccb0a067dd16476c2a855eb6f945bf231a7111d2bbaf28d6fd9b5311",
        "cases_sha": "268c8a47b9b5cccae7053914c2dc0d6929242d18f1da63054aac76937ed936cb",
        "rr_sha": "e90b65da1f15c075e0e74a361989dbbec433039c725751f6932d1cfe827680fb",
        "model": "installed_base_aftermarket",
        "prefix_sha": "ead3c3024b7721bbd535fe0974b1f18d02633fb435d3cad2da8421d018c69a86",
        "prefix_size": 10104,
        "defaults_note": ("（本卡 defaults 案例是全零恒等输入，`optional = ()`；r1 的 300 是生成器缺陷，"
                          "已在 r1 更正为 0，non-gating）"),
    },
    "M26": {
        "expected_guard_message": "opening_stores stock-flow balance failed: FY2027",
        "positive": "[205.0]",
        "continuity": "[205.0, 230.0]",
        "defaults": "[0.0]",
        "in_sha": "72045bf780034e63cb1f813d1c77aff887912f7e610ae9333ea40aa8b9d4fbc0",
        "or_sha": "90e99bc2f32e18cfd8a847b39c6e62c29327af3ba3d3469c77cfb7147b074d10",
        "cases_sha": "f3e86ef0eed59fd9a4e2cc4ace408859458c793a1b15fd52deadb926d241b1e1",
        "rr_sha": "092dcabbc1e22a7f857f4721e32fc7156fc82f4f9dc86483716a8b63e0fd729f",
        "model": "store_cohorts",
        "prefix_sha": "f98a4589e3ff4819709c5e915f98d7830e8ebe91ccab1d248a0dc66703b2c8a4",
        "prefix_size": 9895,
        "defaults_note": "（本卡 defaults 案例是全零恒等输入，`optional = ()`）",
    },
    "M27": {
        "expected_guard_message": "period_hours must be positive: FY2027",
        "positive": "[264000.0]",
        "continuity": "[264000.0, 564100.2]",
        "defaults": "[262800.0]",
        "in_sha": "44f217af85a25c688aad12940abc38d175eedbb505cea0612df6f38956e23223",
        "or_sha": "00cbaab6992ad1da5e572052fbb78db1515707406bfec57d41d7c40e31fd531e",
        "cases_sha": "482a4f160d384e16887bf7ff3fc1180eb1ae8004c445d24e1b105cd926dec4de",
        "rr_sha": "f7287494fd2830277d3784fce693b6e7268b02da5c700dc3721ef8cbd6fe3a2c",
        "model": "renewable_generation",
        "prefix_sha": "03ce281b293a37d2f81dd3313e2c273d0493591bbf6b54eb4a5c2e8eb92214b3",
        "prefix_size": 10500,
        "defaults_note": "（本卡 defaults 案例省略 `other_revenue`）",
    },
    "M28": {
        "expected_guard_message": "opening_aum stock-flow balance failed: FY2027",
        "positive": "[11.5]",
        "continuity": "[11.5, 10.5]",
        "defaults": "[9.5]",
        "in_sha": "12d17d7090cd35e0787f8edb2f1c3e7ffc31c920f92688aef015eb257a52c810",
        "or_sha": "bd4d6875c2d2a72c475fcd534d50fde61124d1968068568dfff207e550565ccf",
        "cases_sha": "64a8a3374b7e6c72dc92f5d65c5245e01b5355de5681856ac3182d0e48ccc82f",
        "rr_sha": "33d1b9797bee0f2895c6df25cf0716a8c59b18bcb0a9a58df613fd7f14c1fd96",
        "model": "aum_fee_bridge",
        "prefix_sha": "5d17e90ac0ac7790f7021dd262e835460b81f6331183a192d0c9e13500b006b2",
        "prefix_size": 10027,
        "defaults_note": "（本卡 defaults 案例省略 `recognized_performance_fees`）",
    },
}

REVIEWER_RUNNER_SHA = "eab0116220df3f3c925551183b65144ea2ffbdbebdfa33a57f155adda21b4fd6"
REVIEWER_GENERATOR_SHA = "d092ab16f050401ea05931cda34dc01251ef729f3123d65ec8385a101aa0f0de"
PROD_REGISTRY_SHA = "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"
PROD_EXTENSIONS_SHA = "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911"

BLOCK_TEMPLATE = """
---

## 独立复核 r2（定点再复核，reviewer 署名：独立会话，非实现者）

> 转录说明（实现者）：本节由 reviewer 的报告 `%TEMP%\\m25m28-review-20260920-035254\\REPORT-r2.md`
> 第 8.1 节原文转录，`<>` 占位符按第 8.2 节逐卡填入。**只追加**：追加前的 `review.md`
> sha256 = `<PREFIX_SHA>`（`<PREFIX_SIZE>` B），追加后新文件以该旧文件字节为前缀（脚本实测
> `new_bytes.startswith(old_bytes)`，记录见 `evidence/<CARD>/append_record_r3.json`）。
> 本节的裁决由独立 reviewer 作出，**不是实现者的签名**。

**verdict: accepted_scoped —— 仅 `formula`。**
`disclosure_adaptation = unmapped`、`accuracy = unproven` 维持；本裁决不涉及 D/E/F。

### 复核范围与方法（可复现）
- 解释器：本 attempt `iso/venv/Scripts/python.exe`，`-B -X utf8`；只读生产与冻结证据，reviewer 只写 `%TEMP%\\m25m28-review-20260920-035254\\`。
- **r1 冻结内容的不可变基线**：commit `ddc81ab6`（及 `e954449`）的 blob 经 CRLF 还原后，与本 reviewer 在 r1 记录的四件套 sha256 逐项相等（16/16），故以该提交为 r1 基准做逐字段 diff。
- 独立重跑：reviewer 用同一 argv 重跑 `scripts/run_card.py`，`rc=0`，且新生成的 `run_result.json` 与冻结件**逐字节相同**（sha256 见下）。
- 期望值复算：reviewer 以自造输入 + `Fraction` 精确算术独立复算正例/连续性/defaults（未采信本卡 oracle.json 的推导过程）。

### 对上一轮发现的处置核验
- **P2-1（NEG-CARD 覆盖声明）已闭合**。r1→r2 的 `cases.json` **唯一** per-case 改动是 `NEG-CARD.value` 由 `{"__float__": X}` 改为单元素列表 `[X]`（`expected`、id 清单与其他 10 例 value 全部不变），并新增 `case_contract`。
  - 实测拒绝机制（reviewer 复跑）：`<EXPECTED_GUARD_MESSAGE>`，即本卡专属守卫**确实**被求值；第 8 节 R1 的"是（NEG-CARD）"现在成立。
  - `negative_summary = {total: 11, passed: 11, failed: []}`；正例 `<POSITIVE>`、连续性 `<CONTINUITY>`、defaults `<DEFAULTS>` 全部与 r1 一致<DEFAULTS_NOTE>。
- **P2-2（oracle 事故叙述）已按更正清单改写**：撤回"no oracle.json was produced at all"（v1 `oracle.json` 存在且与冻结件逐字节相同）；撤回"correction before oracle.md"（mtime 不支持），改为"闸门期望在首次产品运行前已定稿 / M25 的 non-gating defaults 块在首次运行之后更正 / 定版运行在冻结件写入之后"。reviewer 独立复核了首次运行 `run_result.json` 的期望值，支持上述口径。v1 生成器源码与 traceback **未留档**已如实登记为 provenance gap。
- **P3-1..P3-8** 已逐条处置；其中三处措辞与一处残留见下"遗留观察"。

### 遗留观察（P3，不影响本次签收；只许追加修正）
1. 新闸门 rc 归类：`expected`/`expected_count`/`expected_ids`/缺 `case_contract` → **rc=1**；**机制子串不匹配或声明无反引号片段 → rc=3**。本卡 r2 修订节写的"一律 rc=1"与此不符，应改为两类分别表述（reviewer 实测：G5/G6/G7/G8 均 rc=3）。
2. `evidence/<CARD>/line_ending_and_blob_hashes.json` 的 25 条中有 3 条（`evidence_hashes.json`、该文件自身、`revision_r2.json`）为自指条目，写入后即不可复现（reviewer 复算 22/25 一致）；冻结四件套全部可复现。
3. `revision_r2.json.p3_7_precorrection_is_not_uniform` 的 `identical:false` 是 CRLF-vs-LF 的裸字节比较，与同段"byte-identical"叙述冲突；LF 归一后确为逐字节相同（reviewer 用 git 基线与 CRLF 还原两法证明）。
4. LF 修复未覆盖 `recovery/**`（仍有 72 个 CRLF JSON：selfcheck scratch、`rerun_check.json` 等）；`recovery/precorrection/*` 保留 CRLF 属**正确**的 v1 冻结字节。

### 签收范围与失效条件
- 签收值：`formula`（A–C）。基于以下复算值：正例 `<POSITIVE>`、连续性 `<CONTINUITY>`、defaults `<DEFAULTS>`（non-gating）、负例 11/11 全部 `ModelRegistryError`。
- 冻结件哈希（reviewer 复核时点，LF 版本）：
  `input.json=<IN_SHA>`、`oracle.json=<OR_SHA>`、`cases.json=<CASES_SHA>`、`run_result.json=<RR_SHA>`。
- **失效条件**：上述任一冻结件、`iso/checkout_scripts/{model_registry,model_extensions}.py`（须恒等于生产 `9ec65295…/9939480b…`）、或 `scripts/run_card.py`（`eab01162…`）发生任何变化，本裁决自动失效并须重新复核。
- 本裁决**不**覆盖：D 披露映射（`unmapped`）、E 历史对账、F 精度/回测（`unproven`），也不得据此外推为行业级准确度。

### 实现者补充（非裁决的一部分；只作对本次转录与 P3 更正的定位说明）
- 本次追加不含任何期望值、阈值或判定条件的改动；四卡冻结件（`input.json`/`oracle.json`/
  `cases.json`/`run_result.json`）**未触碰**，哈希见 `evidence/<CARD>/append_record_r3.json` 的
  `frozen_four_piece_unchanged_after_append`。
- 对遗留观察 1–4 的**只追加更正**落在 `evidence/<CARD>/revision_r3.json`（含 P3-A 两类 rc 归类、
  P3-B 自指条目与 `files_with_crlf` 口径、P3-C 字段命名更正、P3-D LF 覆盖边界），并在
  `evidence/<CARD>/revision_r3.json` 中给出改前→改后对照与仍存缺口。
- 四卡通用：`status` 保持 `review_pending`（本文件不构成实现者签名）；
  `disclosure_adaptation = unmapped`、`accuracy = unproven` 不外推。
"""


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(FILL))
    parser.add_argument("--attempt-root", required=True)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    card = args.card
    attempt = args.attempt_root
    ev = os.path.join(attempt, "evidence", card)
    review_path = os.path.join(attempt, "review.md")
    fill = FILL[card]

    with open(review_path, "rb") as handle:
        old_bytes = handle.read()
    old_sha = sha256_bytes(old_bytes)
    prefix_ok_declared = (old_sha == fill["prefix_sha"] and len(old_bytes) == fill["prefix_size"])

    block = BLOCK_TEMPLATE
    for key, value in (
        ("<CARD>", card),
        ("<MODEL>", fill["model"]),
        ("<EXPECTED_GUARD_MESSAGE>", fill["expected_guard_message"]),
        ("<POSITIVE>", fill["positive"]),
        ("<CONTINUITY>", fill["continuity"]),
        ("<DEFAULTS>", fill["defaults"]),
        ("<DEFAULTS_NOTE>", fill["defaults_note"]),
        ("<IN_SHA>", fill["in_sha"]),
        ("<OR_SHA>", fill["or_sha"]),
        ("<CASES_SHA>", fill["cases_sha"]),
        ("<RR_SHA>", fill["rr_sha"]),
        ("<PREFIX_SHA>", fill["prefix_sha"]),
        ("<PREFIX_SIZE>", str(fill["prefix_size"])),
    ):
        block = block.replace(key, value)
    block = block.replace("<CARD>", card)
    append_bytes = block.encode("utf-8")

    frozen = {}
    for name in ("input.json", "oracle.json", "cases.json", "run_result.json"):
        with open(os.path.join(ev, name), "rb") as handle:
            frozen[name] = sha256_bytes(handle.read())

    if args.check_only:
        print("check-only for", card)
        print("  current review.md sha256 =", old_sha, len(old_bytes), "B")
        print("  matches the reviewer's declared prefix:", prefix_ok_declared)
        print("  block bytes to append:", len(append_bytes))
        print("  frozen four-piece now:", frozen)
        return 0 if prefix_ok_declared else 1

    if not prefix_ok_declared:
        print("REFUSING to append: review.md does not match the reviewer's declared prefix")
        print("  declared", fill["prefix_sha"], fill["prefix_size"], "B")
        print("  actual  ", old_sha, len(old_bytes), "B")
        return 1

    # BINARY APPEND: the existing bytes can not be rewritten.
    with open(review_path, "ab") as handle:
        handle.write(append_bytes)

    with open(review_path, "rb") as handle:
        new_bytes = handle.read()
    new_sha = sha256_bytes(new_bytes)
    prefix_preserved = new_bytes.startswith(old_bytes)
    grew_by = len(new_bytes) - len(old_bytes)

    # line number of the appended block start (1-based) in the new file
    start_line = new_bytes[:len(old_bytes)].count(b"\n") + 1
    end_line = new_bytes.count(b"\n") + (0 if new_bytes.endswith(b"\n") else 1)

    frozen_after = {}
    for name in ("input.json", "oracle.json", "cases.json", "run_result.json"):
        with open(os.path.join(ev, name), "rb") as handle:
            frozen_after[name] = sha256_bytes(handle.read())

    record = {
        "card_id": card,
        "attempt_id": "a20260919-01",
        "revision": "r3",
        "operation": ("APPEND-ONLY transcription of the independent reviewer's r2 verdict into "
                      "review.md (reviewer REPORT-r2.md section 8.1, placeholders filled from "
                      "section 8.2)"),
        "review_md": {
            "sha256_before": old_sha,
            "size_bytes_before": len(old_bytes),
            "sha256_after": new_sha,
            "size_bytes_after": len(new_bytes),
            "grew_by_bytes": grew_by,
            "append_started_at_line": start_line,
            "appended_block_lines": end_line - start_line + 1,
            "new_file_has_old_file_as_exact_prefix": prefix_preserved,
            "prefix_sha256_declared_by_the_reviewer": fill["prefix_sha"],
            "prefix_size_declared_by_the_reviewer": fill["prefix_size"],
            "prefix_matched_the_declared_value_before_appending": prefix_ok_declared,
            "append_method": "open(path, 'ab') binary append; no seek, no truncate, no rewrite",
            "appended_bytes_sha256": sha256_bytes(append_bytes),
            "appended_bytes_size": len(append_bytes),
        },
        "prefix_proof_method": ("the OLD file bytes are read before the append and the NEW file "
                               "bytes are read after it; the proof is the measured predicate "
                               "new_bytes.startswith(old_bytes), not an assertion"),
        "frozen_four_piece_unchanged_after_append": {
            "before": frozen,
            "after": frozen_after,
            "identical": frozen == frozen_after,
        },
        "reference_hashes_at_transcription_time": {
            "scripts/run_card.py": REVIEWER_RUNNER_SHA,
            "scripts/oracle_M25_M28.py": REVIEWER_GENERATOR_SHA,
            "production scripts/model_registry.py": PROD_REGISTRY_SHA,
            "production scripts/model_extensions.py": PROD_EXTENSIONS_SHA,
        },
        "not_signed_by_the_implementer": True,
        "implementer_note": ("transcription only; the verdict is the reviewer's. status remains "
                             "review_pending and the implementer does not sign accepted."),
    }
    os.makedirs(ev, exist_ok=True)
    with open(os.path.join(ev, "append_record_r3.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=1)

    print("appended the reviewer verdict to", review_path)
    print("  before:", old_sha, len(old_bytes), "B")
    print("  after :", new_sha, len(new_bytes), "B")
    print("  prefix preserved:", prefix_preserved, "| appended block lines:",
          start_line, "-", end_line)
    print("  frozen four-piece unchanged:", frozen == frozen_after)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
