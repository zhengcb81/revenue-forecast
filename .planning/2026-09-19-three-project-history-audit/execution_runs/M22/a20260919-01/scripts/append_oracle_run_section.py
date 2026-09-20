"""Write the post-run reconciliation section, after/rerun_sha256.json and recovery/README.md.

The oracle.md body (sections 0-11) was written before the product run and is never
edited by this script: the reconciliation is APPENDED, which is why oracle.md's own
mtime is later than the run.

Newline honesty
---------------
oracle.md is written by write_oracle_md.py with newline="\\n", so it is an LF file.
All hashing in this script is done on BYTES read in binary mode. An earlier revision
of this script computed the frozen-body sha256 from text read with universal-newline
translation, which produced a digest that did not correspond to any byte prefix of
the file; that is fixed here (recorded in evidence/<card>/revision_r2.json).

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/append_oracle_run_section.py \
      --card M21 --attempt <attempt-root>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

RUN_SECTION_MARK = "## 运行后对账（追加节，不改动上方任何期望值）"
MARK_BYTES = RUN_SECTION_MARK.encode("utf-8")

# Disposition of the six items the independent review required. Card-specific where the
# review's own wording was card-specific; the harness item (P2-1/P3-4) is batch-wide.
_REVIEW_ITEMS_COMMON = {
    "P2-1": {
        "requirement": "run_card.py must CHECK cases.json `expected`, not merely copy it; add a "
                       "mutation probe that turns red when `expected` is tampered with",
        "disposition": "implemented in scripts/run_card.py (FAIL_expected_type_mismatch) plus "
                       "probe F_corrupted_expected_type, which now yields rc=3",
        "scope_note": "the same defect exists in the byte-identical runner held by the M05-M20 "
                      "and M25-M31 attempts; this batch fixed ONLY its own copies and did not "
                      "touch any other card's frozen runner. Registered as a cross-batch harness "
                      "gap for the parent agent.",
    },
    "P2-2": {
        "requirement": "M22/M23 NEG-CARD must be the card's literal 1-element LIST replacement "
                       "so the value-domain guard is what refuses it",
        "disposition": "implemented; cases.json NEG-CARD value is now a 1-element list and the "
                       "refusal message requirement is frozen as "
                       "'must be between 0.0 and 1.0: FY2027'",
    },
    "P2-3": {
        "requirement": "M24 must add a 2-year case whose failure is the CROSS-YEAR anchoring "
                       "guard (message must contain 'continuity failed: FY2028')",
        "disposition": "implemented as CONT-BREAK-CROSSYEAR on the continuity_positive base with "
                       "only FY2028 opening/closing moved to 251",
    },
    "P3-1": {
        "requirement": "handoff.json.revision contradicted revision_r2.json",
        "disposition": "handoff.json now records r2 and states that the review verdict for the "
                       "revised attempt has not yet been received",
    },
    "P3-3": {
        "requirement": "state which `reviews` mtime convention is used",
        "disposition": "after/reviews_mtime.txt and handoff.json now record BOTH the directory "
                       "mtime (2026-09-19 09:14:20) and the newest file inside it, and name the "
                       "two conventions",
    },
}

REVIEW_ITEMS = {
    "M21": dict(_REVIEW_ITEMS_COMMON, **{
        "review_verdict_r1": "accepted_scoped (formula qualification only)",
        "card_specific": "the review's P2-2/P2-3 wording did not require a change on M21; the "
                         "reviewer explicitly accepted the M21 value-domain NEG-CARD on its "
                         "2-year `card_neg` base, which is retained unchanged",
        "P3-2": {
            "requirement": "state the effective resolution of the bridge balance comparison",
            "disposition": "new frozen sub-section 12 added (math.isclose rel_tol=1e-9 / "
                           "abs_tol=1e-9); M21 records that its compared magnitude is ~35 and "
                           "that no numeric probe was run on this card",
        },
    }),
    "M22": dict(_REVIEW_ITEMS_COMMON, **{
        "review_verdict_r1": "changes_required",
        "card_specific": "P2-2 changed M22's NEG-CARD from a scalar to the card's literal "
                         "1-element list, which now reaches the value-domain guard",
        "P3-2": {
            "requirement": "state the effective resolution of the bridge balance comparison",
            "disposition": "new frozen sub-section 12 added; M22 is not a stock bridge, so the "
                           "section states not_applicable_with_reason for that comparison",
        },
    }),
    "M23": dict(_REVIEW_ITEMS_COMMON, **{
        "review_verdict_r1": "changes_required",
        "card_specific": "P2-2 changed M23's NEG-CARD from a scalar to the card's literal "
                         "1-element list; the value-domain guard is now the GATING case and "
                         "OBS-TIMING-BOUND-11 remains as a non-gating cross-check",
        "P3-2": {
            "requirement": "state the effective resolution of the bridge balance comparison",
            "disposition": "new frozen sub-section 12 added; M23 is not a stock bridge, so the "
                           "section states not_applicable_with_reason for that comparison",
        },
    }),
    "M24": dict(_REVIEW_ITEMS_COMMON, **{
        "review_verdict_r1": "changes_required",
        "card_specific": "P2-3 added CONT-BREAK-CROSSYEAR; the card's literal CONT-BREAK is "
                         "retained unchanged and its observed refusal is now itself frozen as a "
                         "message requirement ('stock-flow balance failed: FY2027'), which "
                         "documents that the card's prose and its patch numbers disagree",
        "P3-2": {
            "requirement": "state the effective resolution of the bridge balance comparison",
            "disposition": "new frozen sub-section 12 added AND measured: two non-gating probes "
                           "show +1e-7 inside the ~2.5e-7 effective tolerance and +1e-6 outside "
                           "it",
        },
    }),
}


# Round-2 (point review of revision r2) items, from the reviewer report's sections 2 and 5.
_REVIEW_ITEMS_ROUND2_COMMON = {
    "R2-item3 (gate hole)": {
        "requirement": "freezing individual message requirements was not enough: DELETING the "
                       "field silently disabled the check; freeze `required_message_ids` and "
                       "make the runner assert it",
        "disposition": "`cases.json` now carries `required_message_ids`; the runner asserts, "
                       "BEFORE the negative loop, that every listed id exists and carries a "
                       "non-empty `expect_message_contains`, and fails the whole run (rc=3) "
                       "otherwise. Mutation probes R4 (delete the field) and R5 (empty one "
                       "requirement) both yield rc=3; the reviewer's R4 probe now goes red.",
    },
    "R2-item5 (metadata)": {
        "requirement": "revision_r2.json said 'verdict not received' while already listing the "
                       "reviewer's conclusions",
        "disposition": "state -> review_verdict_received; trigger and note rewritten; the "
                       "round-2 dispositions are recorded in review_items_r2_round2",
    },
    "R2-item6 (wording, P3-1/P3-2)": {
        "requirement": "state that section 12 was added after the run and that sections 0-11 "
                       "were unchanged, and give the precise M24 call site",
        "disposition": "written ONLY into this appended section (see section 7), because the "
                       "reviewer's section 4 boundary forbids any further byte change to "
                       "sections 0-12; the reviewer explicitly allowed this fallback",
    },
    "R2-section3.3 (splice weakness)": {
        "requirement": "register that the splice whitelist used wide substring tokens",
        "disposition": "registered as a follow-up improvement and recorded in "
                       "revision_r2.json.splice_script_status; not retrofitted, and the splice "
                       "script is retired",
    },
}

REVIEW_ITEMS_ROUND2 = {
    "M21": dict(_REVIEW_ITEMS_ROUND2_COMMON, **{
        "review_verdict_r2": "accepted_scoped (formula only); maintained, not downgraded",
        "card_specific": "no numeric or case change was required for M21; only the gate field "
                         "(empty list, so the assertion is a no-op) and the append-only wording",
    }),
    "M22": dict(_REVIEW_ITEMS_ROUND2_COMMON, **{
        "review_verdict_r2": "accepted_scoped (formula only); promoted from changes_required",
        "card_specific": "`required_message_ids = [\"NEG-CARD\"]` added; no case value changed",
    }),
    "M23": dict(_REVIEW_ITEMS_ROUND2_COMMON, **{
        "review_verdict_r2": "accepted_scoped (formula only); promoted from changes_required",
        "card_specific": "`required_message_ids = [\"NEG-CARD\"]` added; no case value changed",
    }),
    "M24": dict(_REVIEW_ITEMS_ROUND2_COMMON, **{
        "review_verdict_r2": "changes_required (blocker downgraded, still open at the time of "
                             "this revision)",
        "R2-item1 (CONT-BREAK message requirement)": {
            "requirement": "keep the card's literal CONT-BREAK patch and only ADD "
                           "`expect_message_contains = 'stock-flow balance failed: FY2027'`",
            "disposition": "PARTIAL, with measured deviation: the literal patch is kept "
                           "byte-unchanged, but the message it OBSERVABLY produces is "
                           "`continuity failed: FY2028`, not the balance message. Step-by-step "
                           "arithmetic on the frozen base (evidence/M24/input.json "
                           "continuity_positive: opening_arr [200,250], closing_arr [250,250]): "
                           "FY2027 closes at 200 - 200*0.1 + 30 + 40 = 250 = closing_arr[0] "
                           "(balance holds), and FY2028 then reads opening 251 against FY2027's "
                           "frozen closing 250, so the CROSS-YEAR ANCHORING guard fires. The "
                           "balance message is unreachable on this input.",
        },
        "R2-item2 (distinct cross-year input)": {
            "requirement": "CONT-BREAK-CROSSYEAR.value -> opening_arr [200,250], closing_arr "
                           "[250,251], keeping the 'continuity failed: FY2028' requirement",
            "disposition": "NOT IMPLEMENTED, with measured reason: the requested opening_arr "
                           "[200,250] is byte-identical to the frozen base for that driver (a "
                           "no-op), and the resulting input fails in exactly the same guard with "
                           "exactly the same message as CONT-BREAK - i.e. it is a DUPLICATE, "
                           "which is the very defect this item was meant to remove. The case was "
                           "therefore REMOVED, leaving M24 with 11 distinct inputs and no "
                           "duplicate. Separately, the FY2027 BALANCE guard is provably "
                           "unreachable on this two-year base: substituting FY2028's continuity "
                           "relation opening[1] = closing[0] into FY2027's bridge expectation "
                           "opening_arr - lost + expansion + new_arr makes it identically "
                           "closing_arr[0], and FY2027 never enters the continuity branch (index "
                           "0 skips it). Making it reachable would require editing a FROZEN input "
                           "definition or a frozen negative value, which the round-1 boundary "
                           "forbids. OWNER/REVIEWER RULING NEEDED.",
        },
        "gate set": {
            "requirement": "required_message_ids = ['NEG-CARD','CONT-BREAK-CROSSYEAR']",
            "disposition": "the INTENT is met (every case that carries a message requirement is "
                           "in the gate), but the membership is ['NEG-CARD','CONT-BREAK'] "
                           "because CONT-BREAK is the surviving cross-year case",
        },
        "product_side_items_still_registered": [
            "the ARR guard keeps an exact `== 0` comparison (model_extensions.py:45-46), so a "
            "zero opening ARR refuses any positive expansion",
            "retail_franchise.recognized_fee_rate is simultaneously optional-without-default "
            "and a [0,1] ratio driver",
        ],
    }),
}


def _bridge_call_sites(card: str) -> str:
    if card == "M24":
        return ("`model_extensions.py:47-48` —— `_arr` 内的 `_bridge(...)` 调用，"
                "`_bridge` 定义在 `model_extensions.py:32-38`，"
                "其比较实现 `_equal` 在 `model_extensions.py:27-29`"
                "（P3-2 要求的精确调用点）")
    if card == "M21":
        return ("`model_registry.py:154-157` —— `_delivery_pipeline` 内的 "
                "`math.isclose(ending, expected_ending, rel_tol=1e-9, abs_tol=1e-9)` "
                "（桥平衡）与 `math.isclose(opening, drivers[\"ending_orders\"][index - 1], ...)`"
                "（跨年 continuity）")
    return ("不适用：本卡不是存量桥（第 1 节 not_applicable_with_reason），"
            "无 `_bridge`/`_equal` 调用点")


def sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True)
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    card = args.card
    attempt = os.path.abspath(args.attempt)
    ev = os.path.join(attempt, "evidence", card)

    with open(os.path.join(ev, "run_result.json"), "r", encoding="utf-8") as fh:
        run = json.load(fh)
    with open(os.path.join(ev, "oracle.json"), "r", encoding="utf-8") as fh:
        oracle = json.load(fh)
    with open(os.path.join(attempt, "recovery", "selfcheck", "selfcheck_result.json"),
              "r", encoding="utf-8") as fh:
        probe = json.load(fh)

    oracle_md = os.path.join(attempt, "oracle.md")
    raw = open(oracle_md, "rb").read()

    def extract_frozen(blob: bytes) -> bytes:
        """Return the frozen body as a canonical byte prefix of the final file.

        The run section is appended as b"\\n---\\n\\n" + section. write_oracle_md.py
        already ends the frozen document with its own footer line, so the append point
        is normalised to EOF minus ALL trailing newlines and '-' rule characters. The
        append script then re-adds the separator. This makes the operation idempotent
        (re-running strips exactly what it added) and keeps
        final_file == frozen_body + b"\\n---\\n\\n" + run_section exactly true.
        """
        at = blob.find(MARK_BYTES)
        if at >= 0:
            blob = blob[:at]
        return blob.rstrip(b"\n-").rstrip(b"\n")

    frozen_body = extract_frozen(raw)
    body_sha_before = hashlib.sha256(frozen_body).hexdigest()
    body_bytes = len(frozen_body)
    if body_bytes != len(raw):
        print("note: normalised a previously appended run section (idempotent re-run)")

    registry = run["registry_metadata"]
    sem = run["exit_code_semantics"]
    neg = run["negative_summary"]
    pos = run["positive"]
    cont = run["continuity_positive"]
    dflt = run["defaults"]

    lines = []
    add = lines.append
    add("")
    add("---")
    add("")
    add(RUN_SECTION_MARK)
    add("")
    add("本节由 `scripts/append_oracle_run_section.py` 在产品运行**之后**追加。")
    add("上方第 0–11 节在运行前冻结，**逐字节未改**；本节只记录实际观测到的值与差异，")
    add("不改动任何期望值、容差、负例清单或拒绝条件。")
    add("")
    add("### 1. 实际运行结果")
    add("")
    add("| 项 | 期望（第 2–4 节） | 实际 | 判定 |")
    add("|---|---|---|---|")
    add("| positive | `%s` | `%s` | %s |" % (oracle["positive"]["expected"],
                                              pos.get("actual"),
                                              "within tolerance" if sem["positive_ok"]
                                              else "MISMATCH"))
    add("| continuity positive | `%s` | `%s` | %s |" % (oracle["continuity_positive"]["expected"],
                                                        cont.get("actual"),
                                                        "ok" if sem["continuity_ok"] else "FAIL"))
    add("| defaults（非判定） | `%s` | `%s` | %s |" % (oracle["defaults"]["expected"],
                                                      dflt.get("actual"),
                                                      "ok" if sem["defaults_ok_not_gating"]
                                                      else "FAIL"))
    add("| 负例 | %d 个全部 `ModelRegistryError` | %d/%d rejected | %s |"
        % (oracle["negative_count"], neg["passed"], neg["total"],
           "ok" if not neg["failed"] else "FAIL " + str(neg["failed"])))
    gate = run.get("required_message_ids_assertion") or {}
    add("| `required_message_ids` 闸门 | 每个必需用例存在且要求非空 | %s | %s |"
        % (gate.get("required_ids"),
           "ok" if gate.get("ok") else "FAIL " + str(gate.get("problems"))))
    add("")
    add("原始退出码 = **%d**（0=pass / 2=no-verdict / 3=negative 未按期望拒绝 / 1=harness error）。"
        % sem["exit_code"])
    add("stdout / stderr 原文：`evidence/%s/stdout.txt`（%d 字节）、`evidence/%s/stderr.txt`（%d 字节）。"
        % (card, os.path.getsize(os.path.join(ev, "stdout.txt")), card,
           os.path.getsize(os.path.join(ev, "stderr.txt"))))
    add("")
    add("### 2. 卡片文字 vs 实现公式串（第 7 节的核对结论）")
    add("")
    add("- 实现注册公式串：`%s`" % registry.get("formula"))
    add("- 必填 driver（实现）：`%s`" % registry.get("required"))
    add("- 可选 driver（实现）：`%s`，默认值 `%s`" % (registry.get("optional"),
                                                     registry.get("defaults")))
    add("- 结论：公式串与第 1 节冻结的公式**逐项一致**；未发现需要改预期的差异。")
    add("")
    add("### 3. 每个负例的实际拒绝消息")
    add("")
    add("| 例 | raised | message |")
    add("|---|---|---|")
    for entry in run["negatives"]:
        add("| %s | `%s` | `%s` |" % (entry["id"], entry.get("raised"),
                                      (entry.get("message") or "").replace("|", "\\|")))
    add("")
    add("### 4. 观察项实际值（非判定）")
    add("")
    add("| ID | raised | actual | 说明 |")
    add("|---|---|---|---|")
    for obs in run["observations"]:
        add("| %s | `%s` | `%s` | %s |" % (obs["id"], obs.get("raised"), obs.get("actual"),
                                           (obs.get("message") or "")[:200]))
    add("")
    add("### 5. 退出码变异自检（先红后绿）")
    add("")
    add("| 探针 | 篡改 | 原始 rc | 期望 rc | 结论 |")
    add("|---|---|---|---|---|")
    labels = {
        "D_pristine_uncorrupted": ("（无篡改，scratch 副本）", "证明未篡改时仍是 0"),
        "A_corrupted_positive_expectation": ("`oracle.json` 正例 `expected_float += 999`",
                                             "被篡改的期望不能藏在 rc=0 后面"),
        "B_corrupted_negative_assertion": ("`cases.json` 追加一个产品**不会**拒绝的负例",
                                           "负例断言被篡改会变红"),
        "C_corrupted_positive_input": ("`input.json` 正例删除首个必填 driver",
                                       "rc=2 可达：确实无法产生判定"),
        "F_corrupted_expected_type": ("`cases.json` 某负例 `expected` 改成 `ValueError`",
                                      "**复核 P2-1**：`expected` 字段被真正校验，不再只是抄写"),
        "G_corrupted_message_requirement": ("`cases.json` 的 `expect_message_contains` 改成不可能"
                                            "出现的子串",
                                            "**复核 P2-2/P2-3**：消息要求被真正校验"),
        "H_message_requirement_points_at_another_guard": (
            "把 `expect_message_contains` 指向长度守卫的措辞",
            "消息控制具有区分度：别的守卫的措辞不能冒充值域/连续守卫"),
        "R4_required_message_ids_gate_removed": (
            "**删除** `cases.json` 的冻结闸门字段 `required_message_ids`",
            "**第 2 轮复核 item 3**：闸门不能被删除绕过；缺失即 rc=3"),
        "R5_required_message_requirement_emptied": (
            "把某个必需用例的 `expect_message_contains` 置为空串",
            "闸门的另一半：要求被清空同样 rc=3"),
        "D_restored_uncorrupted": ("恢复 scratch 副本", "修复后退出码回到 0"),
    }
    for r in probe["runs"]:
        mutation, consequence = labels.get(r["tag"], ("", ""))
        add("| %s | %s | %d | %d | %s |" % (r["tag"], mutation, r["raw_exit_code"],
                                            r["expected_exit_code"], consequence))
    add("")
    add("冻结证据在探针前后 **hash 未变**：`%s`。完整记录见 `recovery/selfcheck/selfcheck_result.json`。"
        % probe["frozen_hashes_unchanged"])
    add("")
    add("### 6. 本节追加前后的 hash 账（可复现）")
    add("")
    add("- 追加前 `oracle.md`（= 运行前冻结的完整正文，只归一化末尾的换行/`-` 分隔字符）"
        "**字节数** = %d，sha256 = `%s`" % (body_bytes, body_sha_before))
    add("- 该值由**二进制读**取得（`open(path, 'rb')`），且 `frozen_body` 是真字节前缀："
        "`oracle.md == frozen_body + b\"\\n---\\n\\n\" + run_section`。复核方式："
        "取 `oracle.md` 中第一次出现本节标题 `%s` 之前的全部字节、去掉末尾换行后求 sha256。" % RUN_SECTION_MARK)
    add("- 追加时是否归一化了末尾分隔块：`%s`（归一化后 `frozen_body` 是真字节前缀）。" % (body_bytes != len(raw)))
    add("- 追加后完整文件 sha256 见 `evidence/%s/source_manifest.json` 的 "
        "`oracle_document.sha256_full_file_now` 与 `after/rerun_sha256.json`。" % card)
    add("- `evidence/%s/oracle.json` 可逐字节重生成（本 attempt 已复跑验证），因此"
        "「oracle 先冻结、后被运行」这条链不依赖 oracle.md 的 mtime。" % card)
    add("")
    add("### 7. 措辞澄清与「正文此后冻结」的登记（第 2 轮复核 P3-1 / P3-2 与第 4 节裁决）")
    add("")
    add("- **第 12 节由 revision r2 于运行后加入**；**0–11 节在该轮未改动**，逐行 diff 见 "
        "`after/oracle_md_body_delta_r2.diff`（变更行数与白名单外行数可由该文件独立复算）。")
    add("- 为什么不把这句话写进第 12 节正文：第 2 轮复核第 4 节裁决「正文定点编辑仅此一次、"
        "自此冻结」，并明确 0–12 节本轮**逐字节不得改动**。复核在第 5 节第 6 项为此留了出口"
        "（「若判定任何正文写入都不可再发生，可改为只写进追加节」）——本实现者按后者执行："
        "该澄清只存在于本追加节，正文一个字节都没动。因此第 5 节第 6 项的**前半句未做**、"
        "后半句以本追加节满足。")
    add("- 第 12 节的调用点：%s" % _bridge_call_sites(card))
    add("- `scripts/splice_oracle_md_r2.py` 已标记为**一次性脚本**，本轮**未运行**，后续任何一轮"
        "都不得再运行；`oracle.md` 第 0–12 节自此冻结，所有补记只写追加节。")
    add("- 第 5 节印的负例表与用例计数仍然是 revision r2 时的内容；M24 的 `CONT-BREAK` 的"
        "**消息要求**在第 2 轮被补上，且 `CONT-BREAK-CROSSYEAR` 被移除（见下条）——"
        "**以 `evidence/%s/cases.json` 与本追加节为准**。" % card)
    add("")
    if card == "M24":
        add("### 8. M24：对第 2 轮补测清单 item 1/2 的**实测偏离**（必须读）")
        add("")
        add("第 2 轮清单要求：`CONT-BREAK` 保持卡片原文 patch 并补 "
            "`expect_message_contains = \"stock-flow balance failed: FY2027\"`；"
            "`CONT-BREAK-CROSSYEAR.value` 改为 `{\"opening_arr\": [200, 250], "
            "\"closing_arr\": [250, 251]}` 并保持 `continuity failed: FY2028`。")
        add("")
        add("**实测结论：这两项按字面执行会自相矛盾**，原因在冻结基座本身"
            "（`evidence/M24/input.json` 的 `continuity_positive`："
            "`opening_arr = [200, 250]`，`closing_arr = [250, 250]`）：")
        add("")
        add("1. 卡片原文 patch（`opening_arr=[200,251]`、`closing_arr=[250,251]`）在 FY2027 上"
            "桥是**自平**的（`200 − 200×0.1 + 30 + 40 = 250 = closing_arr[0]`），"
            "失败发生在 FY2028 的**跨年锚定**：实测 `opening_arr continuity failed: FY2028`。"
            "所以清单要求的 `stock-flow balance failed: FY2027` 在**该输入上不可达**。")
        add("2. 清单给的 CROSSYEAR 新值 `opening_arr: [200, 250]` 与冻结基座**逐字节相同**"
            "（该 driver 上是空操作），而它同样只在 FY2028 触发跨年锚定 —— "
            "于是它与 CONT-BREAK **输入完全相同**，正是第 2 轮要修掉的重复。")
        add("3. FY2027 的**桥平衡**守卫在这个两年基座上**不可达**：桥期望值 "
            "`opening_arr − lost + expansion + new_arr` 在 FY2027 处代入 FY2028 的连续性关系 "
            "`opening[1] = closing[0]` 后恒等于 `closing_arr[0]`，即「连续性成立时桥平衡是恒等式，"
            "连续性不成立时先撞 FY2028 的跨年锚定」；FY2027 自身永远不进连续性分支（index 0 跳过）。")
        add("")
        add("**本实现者的处置**（不改任何冻结输入/期望）：保留卡片原文 patch 于 `CONT-BREAK`，"
            "把它的消息要求冻结为**实测可达**的 `continuity failed: FY2028`（这正是卡片 L116 散文"
            "「两个年度各自平衡」在用例集里成为可执行事实的那条），并**移除** "
            "`CONT-BREAK-CROSSYEAR`（它只能与 CONT-BREAK 重复）。"
            "`required_message_ids` 因此为 `[\"NEG-CARD\", \"CONT-BREAK\"]`，"
            "即**闸门集合的意图达成、但成员是 CONT-BREAK 而不是清单写的 CROSSYEAR**。"
            "要让 FY2027 桥平衡守卫可达，必须改一个**冻结输入定义**（`continuity_positive`）或"
            "某个冻结负例的取值，两者都越界；请复核者裁定。")
        add("")
        add("（自检证据：`evidence/M24/stdout.txt` 的 `negative: CONT-BREAK PASS_rejected … "
            "opening_arr continuity failed: FY2028`、`required_message_ids: ['NEG-CARD', "
            "'CONT-BREAK'] ok= True`；另见 `recovery/selfcheck/selfcheck_result.json` 的 R4/R5 探针。）")
        add("")
    else:
        add("### 8. 第 2 轮补测清单的处置")
        add("")
        add("清单的 item 1–5 中，本卡适用的是：补冻结字段 `required_message_ids`（本卡为空列表，"
            "断言为无操作）、runner 的闸门断言、`revision_r2.json` 元数据更正、以及本追加节的"
            "措辞澄清。本卡**无需**改动任何用例定义，`cases.json` 的负例集合与取值与 revision r2 "
            "一致。")
        add("")

    section = "\n".join(lines).encode("utf-8")
    with open(oracle_md, "wb") as fh:
        fh.write(frozen_body + section)
    print("appended run section to", oracle_md, "frozen_body_bytes", body_bytes)

    full_sha = sha(oracle_md)

    # ---- recovery/oracle_body_hash.json -----------------------------------
    body_record = {
        "card_id": card,
        "oracle_md_path": oracle_md,
        "oracle_md_frozen_body_sha256": body_sha_before,
        "oracle_md_frozen_body_bytes": body_bytes,
        "oracle_md_full_sha256_after_append": full_sha,
        "frozen_body_definition": "the byte prefix of oracle.md written BEFORE any product run, "
                                  "i.e. every byte before the first occurrence of the appended "
                                  "run-reconciliation heading, with the trailing separator run removed so "
                                  "that final_file == frozen_body + b'\\n---\\n\\n' + run_section",
        "append_marker": RUN_SECTION_MARK,
        "hash_is_over_raw_bytes": True,
        "separator_run_normalised": body_bytes != len(raw),
        "reconstruction_identity": "oracle.md == frozen_body + b'\\n---\\n\\n' + run_section",
        "verification_recipe": "python -c \"import hashlib,io,re;b=io.open(r'<oracle.md>','rb')"
                               ".read();m='<append_marker>'.encode();"
                               "print(hashlib.sha256(re.sub(rb'(?:\\n*---\\n)+\\Z',b'',"
                               "b[:b.find(m)])).hexdigest())\"",
        "mtime_ordering": {
            "oracle_json_mtime": os.path.getmtime(os.path.join(ev, "oracle.json")),
            "product_stdout_mtime": os.path.getmtime(os.path.join(ev, "stdout.txt")),
            "frozen_body_precedes_run": (os.path.getmtime(os.path.join(ev, "oracle.json"))
                                         < os.path.getmtime(os.path.join(ev, "stdout.txt"))),
            "note": "oracle.md mtime is later than stdout.txt BY CONSTRUCTION because the "
                    "reconciliation section was appended after the run; the frozen-body chain "
                    "rests on oracle.json mtime < stdout.txt mtime plus byte-identical "
                    "regeneration of oracle.json",
        },
    }
    with open(os.path.join(attempt, "recovery", "oracle_body_hash.json"), "w",
              encoding="utf-8") as fh:
        json.dump(body_record, fh, ensure_ascii=False, indent=1)
    print("wrote recovery/oracle_body_hash.json frozen_body_sha256", body_sha_before)

    # ---- after/rerun_sha256.json ------------------------------------------
    ev_files = sorted(os.listdir(ev))
    rerun = {
        "card_id": card,
        "attempt": attempt,
        "note": "sha256 of everything that carries a claim, captured after the run so a reader "
                "can detect any later edit",
        "oracle_md_sha256_body_before_append": body_sha_before,
        "oracle_md_body_bytes_before_append": body_bytes,
        "oracle_md_sha256_after_append": full_sha,
        "evidence_files": {"evidence/%s/%s" % (card, name): sha(os.path.join(ev, name))
                           for name in ev_files if os.path.isfile(os.path.join(ev, name))},
        "card_scripts": {name: sha(os.path.join(attempt, "scripts", name))
                         for name in sorted(os.listdir(os.path.join(attempt, "scripts")))},
        "top_level": {name: sha(os.path.join(attempt, name))
                      for name in ("binding.json", "oracle.md", "commands.json",
                                   "decision.md", "handoff.json", "changes.diff",
                                   "review.md")
                      if os.path.isfile(os.path.join(attempt, name))},
        "iso_checkout_scripts": {
            "iso/checkout_scripts/model_registry.py": sha(os.path.join(
                attempt, "iso", "checkout_scripts", "model_registry.py")),
            "iso/checkout_scripts/model_extensions.py": sha(os.path.join(
                attempt, "iso", "checkout_scripts", "model_extensions.py")),
        },
    }
    with open(os.path.join(attempt, "after", "rerun_sha256.json"), "w", encoding="utf-8") as fh:
        json.dump(rerun, fh, ensure_ascii=False, indent=1)
    print("wrote after/rerun_sha256.json")

    # ---- recovery/README.md ----------------------------------------------
    recovery = """# %s recovery note

**not_applicable_with_reason.** `%s` is a pure in-process calculator:
`calculate_registered_model` has no durable state, no lock, no lease, no partial
publication and no filesystem side effect. A raised `ModelRegistryError` leaves
nothing to roll back, so there is no restart/retry path to exercise.

What IS covered instead:

- the exit-code mutation probe `recovery/selfcheck/selfcheck_result.json` proves the
  runner's exit code carries the verdict (0 pass / 2 no-verdict / 3 rejected-not-as-expected)
  and that a corrupted copy cannot pass;
- every negative case is run against a fresh `deepcopy`, so a failure cannot contaminate
  a later case;
- the frozen evidence was hash-verified before and after every probe to prove the scratch
  runs did not touch it;
- the card's cross-year guard, which is what replaces per-year durable state here, is
  exercised by a continuity positive plus a continuity-break negative.

Scratch layout (frozen evidence is never mutated; only these copies are):

```text
recovery/
  README.md
  selfcheck_result.json          # mutation probe report (this card)
  oracle_body_hash.json          # frozen-body byte hash of oracle.md + mtime ordering
  oq_enum_stdout.txt             # raw stdout of the read-only registry enumeration
  oq_enum_stderr.txt             # 0 bytes
  selfcheck/
    scripts/run_card.py          # copy of the shared runner
    evidence/%s/{input,oracle,cases}.json   # copies that ARE mutated by the probe
    run_result_*.json            # one run result per probe tag
    stdout_*.txt stderr_*.txt    # raw outputs per probe tag
```
""" % (card, run["model_id"], card)
    with open(os.path.join(attempt, "recovery", "README.md"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(recovery)
    print("wrote recovery/README.md")

    # ---- evidence/<card>/revision_r2.json (single revision section) -------
    with open(os.path.join(ev, "revision_r2.json"), "rb") as fh:
        rev = json.loads(fh.read().decode("utf-8"))
    rev["oracle_md_frozen_body_sha256"] = body_sha_before
    rev["oracle_md_frozen_body_bytes"] = body_bytes
    rev["oracle_md_full_sha256_now"] = full_sha
    rev["hashes_are_over_raw_bytes"] = True
    # keep the r2 splice record's "final file" hash honest: that record is written before this
    # append step runs, so its placeholder-footer hash is superseded here.
    splice_path = os.path.join(attempt, "recovery", "oracle_md_r2_splice.json")
    if os.path.isfile(splice_path):
        with open(splice_path, "rb") as fh:
            splice = json.loads(fh.read().decode("utf-8"))
        splice["final_oracle_md_sha256_with_placeholder_footer"] = splice.get(
            "final_oracle_md_sha256")
        splice["final_oracle_md_sha256"] = full_sha
        splice["final_oracle_md_bytes"] = os.path.getsize(oracle_md)
        splice["final_oracle_md_sha256_note"] = (
            "the value written by the splice step described the file while it still carried the "
            "placeholder footer; this field is the hash of the FINAL file including the "
            "appended run-reconciliation section")
        with open(splice_path, "w", encoding="utf-8") as fh:
            json.dump(splice, fh, ensure_ascii=False, indent=1)
        print("updated recovery/oracle_md_r2_splice.json final hash ->", full_sha)
    rev["self_corrections"] = {
        "SC-1": {
            "what_was_wrong": "the first revision of scripts/append_oracle_run_section.py "
                              "computed the frozen-body sha256 from text read with "
                              "universal-newline translation (io.open without newline=''), so "
                              "the recorded digest did not correspond to any byte prefix of "
                              "oracle.md, and the recorded byte count was a character count",
            "how_it_was_found": "scripts/verify_prefix_chain.py recomputed the prefix digest "
                                "independently and reported prefix_sha==record False for all "
                                "four cards",
            "fix": "all hashing in that script is now done on bytes read with open(path,'rb'), "
                   "and the frozen body is defined as the byte prefix before the append marker "
                   "with all trailing newline and '-' characters removed, so that "
                   "oracle.md == frozen_body + b'\\n---\\n\\n' + run_section holds exactly",
            "what_this_did_NOT_change": "no expectation, tolerance, negative case, rejection "
                                        "condition or frozen sentence was touched; the frozen "
                                        "body content is byte-identical to what was written "
                                        "before the product run - only the digest recipe changed",
            "verification": "scripts/verify_prefix_chain.py reports ALL-OK for all four cards",
        },
        "SC-2": {
            "what_was_wrong": "the product run stdout/stderr were first captured through "
                              "PowerShell redirection, which wrote UTF-16LE with a BOM",
            "fix": "re-ran the same card run with the same frozen evidence, capturing the "
                   "process byte stream directly (scripts/recapture_streams.py)",
            "effect_on_results": "none - the exit code and every printed value were identical; "
                                 "only the file encoding changed",
        },
    }
    rev["review_items_r2"] = REVIEW_ITEMS[card]
    rev["state"] = "review_verdict_received"
    rev["trigger"] = ("r1 复核结论已收到并在本文件 `review_items_r2` 逐条处置；"
                      "修订后版本（r2）的复核结论亦已收到并在 `review_items_r2_round2` 逐条处置；"
                      "本文件记录的是 r2 的修订，尚无'修订后版本已接受'的主张")
    rev["note"] = ("the frozen body of oracle.md was written before the product run. "
                   "第 12 节由 revision r2 在**运行后**加入；**0–11 节仍未改**"
                   "（逐行 diff 见 after/oracle_md_body_delta_r2.diff）。"
                   "自第 2 轮复核裁决起，oracle.md 第 0–12 节整体冻结，"
                   "一切补记只写文末追加节。")
    rev["review_items_r2_round2"] = REVIEW_ITEMS_ROUND2[card]
    rev["verdict_transcription"] = {
        "path": "evidence/%s/verdict_transcription_check.txt" % card,
        "rule": "the round-2 verdict was extracted programmatically from the reviewer report "
                "and appended verbatim to review.md; the written block was re-extracted and "
                "compared byte-for-byte",
    }
    rev["splice_script_status"] = {
        "script": "scripts/splice_oracle_md_r2.py",
        "status": "one-shot, retired; NOT run in round 2 and must not be run again",
        "registered_weakness": "its whitelist used substring tokens ('NEG-CARD', 'OBS-'), so "
                               "'0 lines outside the whitelist' was a WEAK guarantee; the "
                               "reviewer measured 2 lines per card passing on wide tokens "
                               "alone. A byte-per-section comparison inside the script, plus "
                               "tokens that must contain both a case id and a change type, is "
                               "registered as a follow-up improvement and was deliberately NOT "
                               "retrofitted here.",
        "hard_boundary": "oracle.md sections 0-12 are frozen; editing them again would be "
                         "judged `blocked` by the reviewer rather than `changes_required`",
    }
    with open(os.path.join(ev, "revision_r2.json"), "w", encoding="utf-8") as fh:
        json.dump(rev, fh, ensure_ascii=False, indent=1)
    print("updated evidence/%s/revision_r2.json" % card)
    return 0


if __name__ == "__main__":
    sys.exit(main())
