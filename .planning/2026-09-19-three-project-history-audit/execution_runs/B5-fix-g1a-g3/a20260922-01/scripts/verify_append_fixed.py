"""F-7 fix (B5-fix-g1a-g3): corrected frozen-anchor operand for the START_HERE.md append proof.

B5's scripts/verify_append.py carried an `orig_table` list of only 9 substring entries with a
duplicate operand, so its `frozen_original_lines_all_intact` check was weaker than the
"10 frozen anchor lines" phrasing suggested (reviewer finding F-7). THIS copy:

  1. embeds the FULL VERBATIM line text of the frozen rc-table region (START_HERE.md lines
     inside the T1-19 frozen prefix, bytes [0, 9895)), as the check's operand;
  2. asserts the embedded list is DISTINCT (a duplicate can never silently weaken the check
     again);
  3. asserts the embedded list equals the lines extracted live from the byte-verified frozen
     prefix (so the operand cannot drift from the real frozen region);
  4. checks every anchor as a full line in BOTH the frozen prefix and the current file;
  5. keeps B5's two-route chain proof (PRE/POST1 prefix sha + single-insert opcodes).

Read-only on START_HERE.md; output goes to this attempt's evidence/ only.
"""
from __future__ import annotations

import difflib
import hashlib
import json
import os

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-fix-g1a-g3", "a20260922-01")
TARGET = os.path.join(PLAN, "execution_v2", "START_HERE.md")

PRE_SHA, PRE_BYTES = "1bdfbd9190d6ae956d6ad025792a4ffa487f0e41258f80922c752f783cf22835", 9895
POST1_SHA, POST1_BYTES = "e7cb90fc5c4cc51f2dfe97f1bfef55750ee1459e07bf3078890d227b1c441557", 16314

SECTION_HEAD = "## rc 码表（冻结；owner 裁定 T1-19 / §13）"
SECTION_TAIL_MARK = "再推广 runner。"

# Full verbatim lines of the frozen rc-table region (transcribed from the frozen bytes; the
# script asserts equality against the live extraction below, so a transcription typo fails loud).
FROZEN_ANCHORS = [
    "## rc 码表（冻结；owner 裁定 T1-19 / §13）",
    "同一批内 rc 语义必须自洽，但**跨批历史 rc 不回改**。今后各批**必须**在自身证据里带一份",
    "自描述 `exit_code_legend`，并在 `commands.json` / `case_results.json` 中按本表归类。",
    "**冻结码表（本包唯一规范值）**",
    "| rc | 含义 | 判据 |",
    "|---|---|---|",
    "| `0` | 通过 | 命令正常结束，且**业务判定为通过**（外层 runner 退出 0 不能覆盖子命令失败） |",
    "| `1` | harness 失败 | 测试/运行器自身出错：导入失败、夹具错误、期望文件缺失、路径未绑定 |",
    "| `2` | 无裁决 / 预期拒绝 | 用例是负例且**业务上被正确拒绝**；或该命令不产生裁决（如只读查询） |",
    "| `3` | 未达预期 | 正例未通过，或负例**未被拒绝**；即\"应红未红 / 应绿未绿\" |",
    "**已知的历史偏差（只登记、不回改）**",
    "- M05–M08 用 `2 = harness`。",
    "- M09–M16 等用 `1 = harness / 2 = no-verdict / 3 = negative`。",
    "- ⇒ 同一个 `rc=2` 在两类批里语义不同。**跨批聚合前必须先读该批的 `exit_code_legend`**，",
    "  不得假设码表一致。历史 rc 与其证据**一律不动**。",
    "**与 runner 推广的四项前置的关系（T1-8）**",
    "`expected` 只能是**裸类型名**（如 `'ModelRegistryError'`）；复合写法（如",
    "`\"ModelRegistryError/continuity\"`）会假红。当前 `cases.json` 缺 `expected` 时的归类",
    "（现为 `rc=3`，而登记口径写 `rc=2`）须先按本表**统一到 `rc=2`**，再推广 runner。",
]

ADDITIVE_1 = [
    "## rc 码表·实测各批码位登记（REM-22 / B5+B6 追加节；owner 裁定 T1-19）",
    "94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252",
    "5307d2cc",
    "一律不回改",
]
ADDITIVE_2 = [
    "## rc 码表·追加节 2：`expected` 缺失的实测归类更正（B5+B6；owner 裁定 T1-19）",
    "跨批聚合方不得假设「缺 `expected` = rc=3」",
]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def append_check(post, post_txt, pre_bytes, label):
    prefix = post[:pre_bytes]
    pre_lines = prefix.decode("utf-8").splitlines(keepends=True)
    post_lines = post_txt.splitlines(keepends=True)
    sm = difflib.SequenceMatcher(None, pre_lines, post_lines, autojunk=False)
    ops = [{"op": t, "i1": i1, "i2": i2, "j1": j1, "j2": j2}
           for t, i1, i2, j1, j2 in sm.get_opcodes()]
    non_equal = [o for o in ops if o["op"] != "equal"]
    return {
        "prefix_ends_at_line_boundary": prefix.endswith(b"\n"),
        "prefix_sha256_matches_recorded": sha(prefix) == (PRE_SHA if label == "PRE" else POST1_SHA),
        "opcodes": [o["op"] for o in ops],
        "non_equal_opcode_count": len(non_equal),
        "only_opcode_is_single_insert": len(non_equal) == 1 and non_equal[0]["op"] == "insert",
        "deleted_lines": sum(o["i2"] - o["i1"] for o in ops if o["op"] in ("delete", "replace")),
        "inserted_lines": sum(o["j2"] - o["j1"] for o in ops if o["op"] in ("insert", "replace")),
    }


def extract_section_lines(prefix_txt):
    lines = prefix_txt.splitlines()
    start = lines.index(SECTION_HEAD)
    end = next(i for i, ln in enumerate(lines) if SECTION_TAIL_MARK in ln)
    return [ln for ln in lines[start:end + 1] if ln.strip()]


def main():
    post = open(TARGET, "rb").read()
    post_txt = post.decode("utf-8")
    prefix = post[:PRE_BYTES]
    prefix_txt = prefix.decode("utf-8")

    # --- F-7: the operand itself ---------------------------------------------------------
    distinct_ok = len(set(FROZEN_ANCHORS)) == len(FROZEN_ANCHORS)
    extracted = extract_section_lines(prefix_txt)
    extraction_matches = extracted == FROZEN_ANCHORS
    in_prefix = [a for a in FROZEN_ANCHORS if a not in prefix_txt]
    in_current = [a for a in FROZEN_ANCHORS if a not in post_txt]
    # every anchor must also be a full LINE (not a substring) in both
    prefix_line_set = set(prefix_txt.splitlines())
    current_line_set = set(post_txt.splitlines())
    full_line_in_prefix = all(a in prefix_line_set for a in FROZEN_ANCHORS)
    full_line_in_current = all(a in current_line_set for a in FROZEN_ANCHORS)

    proof = {
        "target": os.path.relpath(TARGET, PLAN).replace("\\", "/"),
        "fix_card": "B5-fix-g1a-g3 / F-7",
        "chain": [
            {"step": "PRE", "sha256": PRE_SHA, "bytes": PRE_BYTES,
             "source": "T1-19 handoff.json artifact_under_verification.pre_sha256"},
            {"step": "POST1", "sha256": POST1_SHA, "bytes": POST1_BYTES,
             "source": "B5's append 1 (recorded; this card re-verifies the prefix)"},
            {"step": "POST2", "sha256": sha(post), "bytes": len(post),
             "source": "B5's append 2 (recorded); no further append by this card"},
        ],
        "append_1_check_vs_PRE": append_check(post, post_txt, PRE_BYTES, "PRE"),
        "append_2_check_vs_POST1": append_check(post, post_txt, POST1_BYTES, "POST1"),
        "frozen_anchor_check": {
            "operand_count": len(FROZEN_ANCHORS),
            "operand_distinct_count": len(set(FROZEN_ANCHORS)),
            "operand_is_distinct": distinct_ok,
            "operand_equals_live_extraction_from_frozen_prefix": extraction_matches,
            "all_anchors_in_frozen_prefix": not in_prefix,
            "all_anchors_in_current_file": not in_current,
            "all_anchors_full_lines_in_prefix": full_line_in_prefix,
            "all_anchors_full_lines_in_current": full_line_in_current,
            "missing_from_prefix": in_prefix,
            "missing_from_current": in_current,
        },
        "content_checks": {
            "frozen_anchor_lines_all_intact": (distinct_ok and extraction_matches
                                               and not in_prefix and not in_current
                                               and full_line_in_prefix and full_line_in_current),
            "append_1_content_present": all(s in post_txt for s in ADDITIVE_1),
            "append_2_content_present": all(s in post_txt for s in ADDITIVE_2),
        },
    }
    proof["APPEND_ONLY"] = (
        proof["append_1_check_vs_PRE"]["only_opcode_is_single_insert"]
        and proof["append_1_check_vs_PRE"]["prefix_sha256_matches_recorded"]
        and proof["append_1_check_vs_PRE"]["prefix_ends_at_line_boundary"]
        and proof["append_2_check_vs_POST1"]["only_opcode_is_single_insert"]
        and proof["append_2_check_vs_POST1"]["prefix_sha256_matches_recorded"]
        and proof["append_2_check_vs_POST1"]["prefix_ends_at_line_boundary"]
        and all(proof["content_checks"].values())
    )

    dest = os.path.join(ATTEMPT, "evidence", "start_here_append_proof_fixed.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(proof, fh, indent=1, ensure_ascii=False)
        fh.write("\n")

    print("anchors: %d embedded / %d distinct / live-extraction match=%s"
          % (len(FROZEN_ANCHORS), len(set(FROZEN_ANCHORS)), extraction_matches))
    print("anchors in prefix=%s in current=%s full-line=%s/%s"
          % (not in_prefix, not in_current, full_line_in_prefix, full_line_in_current))
    c1, c2 = proof["append_1_check_vs_PRE"], proof["append_2_check_vs_POST1"]
    print("append1 vs PRE  : +%d/-%d prefix_ok=%s insert_only=%s"
          % (c1["inserted_lines"], c1["deleted_lines"],
             c1["prefix_sha256_matches_recorded"], c1["only_opcode_is_single_insert"]))
    print("append2 vs POST1: +%d/-%d prefix_ok=%s insert_only=%s"
          % (c2["inserted_lines"], c2["deleted_lines"],
             c2["prefix_sha256_matches_recorded"], c2["only_opcode_is_single_insert"]))
    print("content checks:", json.dumps(proof["content_checks"], ensure_ascii=False))
    print("APPEND_ONLY =", proof["APPEND_ONLY"])
    print("wrote", dest)
    return 0 if proof["APPEND_ONLY"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
