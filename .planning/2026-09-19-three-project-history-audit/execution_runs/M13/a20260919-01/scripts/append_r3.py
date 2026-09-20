"""Append the SINGLE revision-r3 section to oracle.md and record revision_r3.json.

r3 is the response to the independent review of 2026-09-20 (findings F-01..F-05 plus the
observation-(c) and unit-labelling notes). Rules enforced here, identical in spirit to the r2
append:

  * exactly ONE r3 boundary marker and ONE "修订 r3" heading exist after this runs, and the r2
    section is untouched;
  * the bytes ABOVE the r3 marker still hash to ``revision_r2.json``'s recorded
    ``oracle_md_sha256_after_append``, so the pre-r3 hash is reproducible at a real line boundary
    (one baseline, no competing values);
  * no expectation, tolerance, case or refusal condition is touched - the frozen body above the r2
    marker is byte-unchanged, which ``verify_r2_boundary.py`` re-checks afterwards;
  * no product file is touched.

Refuses to run if an r3 marker already exists. Prints ASCII only.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time

MARKER = "<!-- R3-APPEND-BOUNDARY: everything above this line is the r2-reviewed frozen oracle body -->"
R3_HEADING = "## 修订 r3"


def sha256_bytes(payload):
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path):
    return sha256_bytes(open(path, "rb").read())


def load_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def build_body(card, selfcheck, before_fixes, repack, current_hashes):
    matrix = selfcheck.get("exit_code_matrix", {})
    matrix_rows = "\n".join("| %s | %s |" % (rc, ", ".join(matrix[rc])) for rc in sorted(matrix))
    repack_text = ("`evidence/%s/cases.json` 追加了**只增不改**的标注字段（观察项 (c)）："
                   "旧 sha256 `%s` → 新 sha256 `%s`，差异经脚本 `build_cases_annotation_repack.py` "
                   "证明**仅为该字段**；`input.json` / `oracle.json` 逐字节未变，所有期望值/容差/"
                   "拒绝条件未变。"
                   % (card, repack["old_revision"]["sha256"], repack["new_revision"]["sha256"])
                   if repack else
                   "本卡没有对 `input.json` / `cases.json` / `oracle.json` 做任何写入；三者的 "
                   "sha256 与冻结时完全一致。")
    return """本节由修订 r3 **追加**，是 `oracle.md` 中**唯一**的一节「修订 r3」。
上方正文（v1 冻结版）与 r2 节逐字未改；产品仓库一行未动。r3 节的追加前 hash 记录在
`evidence/%s/revision_r3.json` 的 `boundary.sha256_of_bytes_before_the_marker`，并可由
`scripts/verify_r2_boundary.py` 在**真实行边界**（本标记行处）重新复现。本文件对每个修订只有
一个基准，不存在互斥的"追加前 hash"。

### 触发：独立复核（2026-09-20）判定 `accepted_scoped`（仅 formula）+ 5 项整改

独立复核者自写脚本、未调用本 attempt 的任何脚本，独立复算正例、自造 35 条负例（应拒而被接受 0 例）、
自建 harness replay、独立复现本 attempt 的验证脚本、逐字节复核冻结前缀 hash 与 1 字节边界修复，
并给出 **F-01…F-05 + 观察项 (c) + 计数单位** 整改清单。r3 逐条处置如下（工具层与证据层改动，
**不改任何冻结期望/容差/拒绝条件**）：

| 编号 | 处置 |
|---|---|
| F-01 | `run_card.py` 增加 **期望声明一致性**：逐 case 校验 `expected` 是否等于本 runner 实际据以判定的类型、case 数量与 id 集合是否与 `oracle.json` 的 `negative_count`/`negative_ids` 一致，并校验 kind/base_input；任何不一致 → `expectation_declaration_inconsistent` → **rc=2**，不再静默 rc=0。rev r1（只 `isinstance` 判定）保留在 `recovery/runner_before_F01_fix.py` 作为对照。 |
| F-02 | `enumerate_driver_bounds.py` 的 ratio 谓词改为**权威**的 `spec.dimensions[driver] == "ratio"`（并同时记录旧谓词 `ratio_drivers` 集合的计数与两者全部分歧条目），注册表口径由 40/3 更正为 **41/4**，与 M05–M08 r3 更正口径一致；`oq_enumeration.json` / `oq_rulings.json` 已重生成。 |
| F-03 | `oq_rulings.json` 的 OQ 列表改为**与 `handoff.json:open_questions` 一一对应**（编号同源），`decision.md`/`review.md` 的编号同步；并对全部文档指针做了可执行审计（`scripts/audit_doc_pointers.py` → `evidence/%s/doc_pointer_audit.json`）。 |
| F-04 | `finalize_hashes.py` 先写自产物再清点，且**把 `after/rerun_sha256.json` 自身排除**在清单与 combined digest 之外，新增 `self_reference_note` 与 `combined_digest_scope`，并对并发的 `after/git_status_*.txt` 标记 `concurrently_mutable`。 |
| F-05 | `recovery/README.md` 显式声明：首次 rc=1 调用（runner 的 `NameError`）与 `setup_isolation.ps1` 早期修订的**原始字节未留存**，只有 `raw_rc` 与叙述为证；今后首次失败调用一律把 stdout/stderr 原样另存。 |
| (c) | 观察项 `OBS-SIGNED-PERF-FEE` 按复核建议做**追加式标注**（不改语义）。%s |
| 计数单位 | `oq_rulings.json` 新增 `enumerated_counts_with_units`，把 registry 级计数标成 slot（(model,driver) 对）与 model 两种单位：31 slot / 24 model。 |

### 变异自检矩阵（先红后绿；冻结件未动）

| 实测 rc | 场景 |
|---|---|
%s

其中 `G/H-...` 为 F-01 新增场景；`G/H-pre-fix-runner-...` 是**修复前** runner 修订在同一份被污染副本上的
实测结果（rc=0，即复核报告所述缺陷的可复现证据）。详见 `recovery/selfcheck_result.json`
（含 `exit_code_matrix`、`pre_fix_runner_revision` 与冻结件前后 hash）。

### 本次改动的旧→新 hash（工具层与证据层）

| 文件 | 旧 sha256 | 新 sha256 |
|---|---|---|
%s

### 未改动的内容（防止误读为"为过审而改"）

- **正例/连续性/默认值期望值、容差、11 个负例及其期望错误、拒绝条件、停止条件一律未改**；
  上述表中 `input.json` / `oracle.json` 两行若显示旧=新，即为证据。
- 产品仓零改动；`changes.diff` 仍为 NO PRODUCT CHANGE 声明。
- `formula` 仍为 `review_pending`（实现者不自签，r3 后交回复核者点验），
  `disclosure_adaptation` 仍为 `unmapped`，`accuracy` 仍为 `unproven`。
""" % (card, card, repack_text, matrix_rows, current_hashes)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()

    card = args.card
    attempt = os.path.abspath(args.attempt)
    evidence = os.path.join(attempt, "evidence", card)
    oracle_md = os.path.join(attempt, "oracle.md")
    revision2 = load_json(os.path.join(evidence, "revision_r2.json"))
    expected_before = revision2["boundary"]["oracle_md_sha256_after_append"]

    payload = open(oracle_md, "rb").read()
    if MARKER.encode("utf-8") in payload:
        print("oracle.md already carries the r3 boundary marker: refusing to append a SECOND r3 "
              "section (two competing baselines are forbidden)")
        return 21
    digest_before = sha256_bytes(payload)
    if digest_before != expected_before:
        print("oracle.md does not match revision_r2's recorded post-append hash (now=%s "
              "recorded=%s): refusing to append" % (digest_before, expected_before))
        return 22

    selfcheck = load_json(os.path.join(attempt, "recovery", "selfcheck_result.json"))
    repack_path = os.path.join(evidence, "cases_annotation_repack.json")
    repack = load_json(repack_path) if os.path.isfile(repack_path) else None

    # old -> new hash table for the files this revision changed
    table = []
    pairs = [
        ("scripts/run_card.py", os.path.join(attempt, "recovery", "runner_before_F01_fix.py")),
        ("evidence/%s/oq_enumeration.json" % card,
         os.path.join(attempt, "recovery", "before_fixes", "oq_enumeration.json")),
        ("evidence/%s/oq_rulings.json" % card,
         os.path.join(attempt, "recovery", "before_fixes", "oq_rulings.json")),
        ("evidence/%s/input.json" % card,
         os.path.join(attempt, "recovery", "before_fixes", "input.json")),
        ("evidence/%s/oracle.json" % card,
         os.path.join(attempt, "recovery", "before_fixes", "oracle.json")),
        ("evidence/%s/cases.json" % card,
         os.path.join(attempt, "recovery", "before_fixes", "cases.json")),
        ("evidence/%s/run_result.json" % card,
         os.path.join(attempt, "recovery", "before_fixes", "run_result.json")),
        ("evidence/%s/stdout.txt" % card,
         os.path.join(attempt, "recovery", "before_fixes", "stdout.txt")),
        ("after/rerun_sha256.json",
         os.path.join(attempt, "recovery", "before_fixes", "rerun_sha256.json")),
        ("oracle.md", os.path.join(attempt, "recovery", "before_fixes", "oracle.md")),
    ]
    for label, old_path in pairs:
        new_path = os.path.join(attempt, label.replace("/", os.sep))
        old_hash = sha256_file(old_path) if os.path.isfile(old_path) else "(not kept)"
        new_hash = sha256_file(new_path) if os.path.isfile(new_path) else "(absent)"
        table.append("| `%s` | `%s` | `%s` |" % (label, old_hash, new_hash))

    body = build_body(card, selfcheck, None, repack, "\n".join(table))
    offset = len(payload)
    heading_line = R3_HEADING + "（对独立复核 F-01…F-05 的处置，非重写）"
    addition = (MARKER + "\n\n" + heading_line + "\n\n" + body).encode("utf-8")
    with open(oracle_md, "wb") as handle:
        handle.write(payload + addition)
    after = open(oracle_md, "rb").read()

    text_after = after.decode("utf-8")
    prefix_hash = sha256_bytes(after[:offset])
    reproducible = prefix_hash == expected_before
    marker_occurrences = text_after.count(MARKER)
    heading_occurrences = text_after.count(R3_HEADING)
    r2_marker_occurrences = text_after.count(
        revision2["boundary"]["marker_line"])

    revision = {
        "card_id": card,
        "model_id": revision2.get("model_id"),
        "revision": "r3",
        "single_revision_node": True,
        "competing_baselines_present": False,
        "trigger": "independent review of attempt a20260919-01, 2026-09-20: accepted_scoped "
                   "(formula only) plus findings F-01..F-05, observation (c) and the unit-labelling "
                   "note",
        "frozen_expectations_unchanged": True,
        "product_files_changed": [],
        "boundary": {
            "marker_line": MARKER,
            "byte_offset": offset,
            "sha256_of_bytes_before_the_marker": prefix_hash,
            "sha256_recorded_in_revision_r2_after_its_append": expected_before,
            "reproduces_the_r2_post_append_hash": reproducible,
            "marker_occurrences_in_oracle_md": marker_occurrences,
            "r2_heading_occurrences_in_oracle_md": text_after.count("## 修订 r2"),
            "r3_heading_occurrences_in_oracle_md": heading_occurrences,
            "r2_marker_still_present_exactly_once": r2_marker_occurrences == 1,
            "oracle_md_sha256_after_append": sha256_bytes(after),
            "oracle_md_bytes_after_append": len(after),
            "verification_command": "<attempt>/iso/venv/Scripts/python.exe -X utf8 -B "
                                    "<attempt>/scripts/verify_r2_boundary.py --card %s "
                                    "--attempt <attempt>" % card,
        },
        "items": {
            "F-01": "run_card.py now cross-checks each case's declared `expected` against the type "
                    "the runner actually counts, and the case count / id set against oracle.json; "
                    "any inconsistency is an expectation gap and yields rc=2. Pre-fix revision kept "
                    "at recovery/runner_before_F01_fix.py and demonstrated red on the same "
                    "corrupted scratch copy.",
            "F-02": "ratio predicate corrected to spec.dimensions[driver] == 'ratio'; registry "
                    "totals 40/3 -> 41/4 (direct_growth.growth_rate (-1, inf) recovered); "
                    "oq_enumeration.json and oq_rulings.json regenerated.",
            "F-03": "oq_rulings.json OQ list now mirrors handoff.json:open_questions 1:1 (same "
                    "numbering); decision.md / review.md numbering aligned; document pointers "
                    "audited by scripts/audit_doc_pointers.py.",
            "F-04": "finalize_hashes.py writes its own by-products before the inventory, excludes "
                    "the manifest itself, and declares self_reference_note / combined_digest_scope "
                    "/ concurrently_mutable.",
            "F-05": "recovery/README.md states explicitly that the raw bytes of the first failed "
                    "invocations were not retained.",
            "observation-c": "append-only annotation on OBS-SIGNED-PERF-FEE"
                             if repack else "not applicable to this card (no invalid observation)",
            "unit-labels": "oq_rulings.json carries enumerated_counts_with_units (31 slots / 24 "
                           "models registry-wide).",
        },
        "cases_annotation_repack": repack,
        "written_at_unix": time.time(),
        "written_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    with open(os.path.join(evidence, "revision_r3.json"), "w", encoding="utf-8", newline="\n") as handle:
        json.dump(revision, handle, ensure_ascii=False, indent=1)
        handle.write("\n")

    print("r3 appended: boundary byte offset=%d" % offset)
    print("sha256 of bytes before the r3 marker = %s (revision_r2 recorded %s)"
          % (prefix_hash, expected_before))
    print("reproduces the r2 post-append hash: %s" % reproducible)
    print("r3 markers=%d r3 headings=%d r2 headings=%d"
          % (marker_occurrences, heading_occurrences, text_after.count("## 修订 r2")))
    print("oracle.md sha256 after r3 = %s" % revision["boundary"]["oracle_md_sha256_after_append"])
    return 0 if (reproducible and marker_occurrences == 1 and heading_occurrences == 1
                 and r2_marker_occurrences == 1) else 23


if __name__ == "__main__":
    raise SystemExit(main())
