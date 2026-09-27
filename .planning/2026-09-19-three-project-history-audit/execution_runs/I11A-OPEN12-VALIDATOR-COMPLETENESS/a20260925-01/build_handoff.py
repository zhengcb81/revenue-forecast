"""Build handoff.json for I11A-OPEN12-VALIDATOR-COMPLETENESS/a20260925-01.

Kept as provenance: it is the literal source of handoff.json (UTF-8, no BOM, LF,
re-parsed with json.load immediately after writing).
"""

from __future__ import annotations

import hashlib
import io
import json
import os

D = os.path.dirname(os.path.abspath(__file__))


def sha(path):
    return hashlib.sha256(io.open(path, "rb").read()).hexdigest()


def written_files():
    rels = [
        "oracle.md", "ruling.md", "changes.diff",
        "run_cases.py", "run_mutations.py", "patch_open12.py", "build_handoff.py",
        "logs/source_manifest_before.sha256", "logs/red_run.log", "logs/green_run.log",
        "logs/mutations.log",
        "red/baseline_run.log", "red/baseline_validation_report.json",
        "red/cases_original.json", "red/cases_original_run1_with_harness_defect.json",
        "green/patched_run.log", "green/patched_validation_report.json",
        "green/cases_patched.json",
        "mut/mutation_results.json",
        "iso_patched/tools/validate_hypotheses.py",
    ]
    rels += ["mut/M%d/cases_mutation.json" % i for i in range(1, 11)]
    rels += ["mut/M%d/validate_hypotheses.py" % i for i in range(1, 11)]
    out = []
    for rel in rels:
        p = os.path.join(D, rel.replace("/", os.sep))
        if not os.path.isfile(p):
            raise SystemExit("missing expected file: %s" % rel)
        out.append({"path": rel, "sha256": sha(p), "bytes": os.path.getsize(p)})
    return out


def main():
    mut = json.load(io.open(os.path.join(D, "mut", "mutation_results.json"), encoding="utf-8"))
    h = {
        "card_id": "I11A-OPEN12-VALIDATOR-COMPLETENESS",
        "attempt_id": "a20260925-01",
        "role": "statistical_or_engineering_reviewer",
        "implementer_signed": False,
        "status": "review_pending",
        "authorized_by": "OWNER_DECISIONS §二十八（2026-09-25，选项式问答原话「是，另立校验器专业卡（建议）」）",
        "authorization_chain": {
            "original_definition": "execution_runs/I-11-A/a20260919-01/decision.md L408 (sha256 e9c96f02118514b8596620b3c0e235a797747fcd3bcf59d1a0fd20aa70166951)",
            "merge_ruling": "execution_runs/I11A-OPEN-MERGE/a20260924-01/merge_ruling.md L362 (G3) (sha256 2d214bab861be4ff30ebb7118705d23183fb2eec3e58f987d52287d0bab2e5c1)",
            "inline_erratum": "OWNER_DECISIONS.md §二十七 行内勘误（父侧第 18 起：转述时改变所指）",
            "owner_answer": "OWNER_DECISIONS.md §二十八：是，另立校验器专业卡（建议）",
            "contract_card": "execution_v2/card_I11A-OPEN12-VALIDATOR-COMPLETENESS.md (sha256 191c0ec5099bb893bf91b50a4acc573ed69c2e072872b0f44becf90f4d811090)",
        },
        "scope": "只裁 P2-5/P2-6/P2-7/P2-8/P2-9 这批校验器完备性问题 + I-11-C 是否复用同一校验器",
        "verdict_summary": (
            "P2-5 = partial（reviewer 的 8 个原变异中 7 个现被拒，字面第 8 个「两条同 parameter_id 的相同命题」"
            "仍被放行；且我构造的 11 个同族反例全部被现有校验器放行 ⇒ 完备性判据不成立）；"
            "P2-6/P2-7/P2-8/P2-9 = 已处置（逐条回源核对）。"
            "decision.md L408 的断言「P2-5…P2-9 已在本 attempt 内处置」只对 P2-5 部分成立。"),
        "p2_5_to_p2_9_status": {
            "P2-5": {
                "status": "partial",
                "reason": (
                    "反例套件 14→21 与四类新检查确已落地（我独立复现 8 个原变异：7 拒），且 oracle R2-1 / "
                    "mechanism_review §5.8 / decision DEC-14 显式声明「仍不完备」；但 "
                    "(a) REPORT.md L233 字面那一条「两条同 parameter_id 的相同命题」现仍被放行"
                    "（REPRO-8 实测），review.md §5.1「全部固化并现已被拒」在字面上不成立；"
                    "(b) 按完备性判据，CE-01…CE-11 共 11 条同族反例被现有校验器 11/11 放行。"),
                "evidence": ["red/cases_original.json (11/11 accepted, rc=0)",
                             "red/cases_original.json REPRO-8 rejected=false",
                             "mut/mutation_results.json", "changes.diff (G1..G10)"],
                "repair": "changes.diff（10 个 marker 化新判据块）；补后 11/11 被拒、10/10 变异翻红",
            },
            "P2-6": {
                "status": "disposed",
                "reason": ("hypotheses.json H-CN-ZIJIN-SEG-02.conversion_formula 已改为「每 +1 吨/千克 ⇒ "
                           "当量分母 +83,161 吨 ⇒ −10,670.89 元/吨」并注明两点差分≠偏导"
                           "（含分母单独 +1 吨约 0.14 元/吨的对照）"),
                "evidence": ["evidence/I-11-A/hypotheses.json (sha256 f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28)"],
                "note": "校验器对该族无机器检查；规则面把复算交给 verify_arithmetic.py（O-12），本卡不要求校验器承担",
            },
            "P2-7": {
                "status": "disposed",
                "reason": ("source_map.not_readable_in_this_attempt.reason 已按建议重写"
                           "（415 classic page objects / 前 30 页 30 条内容流 / 抽样页 0 字符 / pdftotext mojibake）"
                           "并带 measured_facts + correction_note；probe_xiaomi.py 实测三档"
                           "（file_level_byte_counts / 全流 decode_streams / 页面 /Contents 流）分别落盘"),
                "evidence": ["evidence/I-11-A/source_map.json (sha256 3ce2e20acffa26dc08ca7c563c27fe19d1771594b2c2612b748252ad30112ecf)",
                             "iso/tools/probe_xiaomi.py"],
                "residual_out_of_scope": ("binding.json L26 仍写「0 classic page objects found by this attempt "
                                          "scanner」（原文含所有格），与 probe_xiaomi 的 415 实测矛盾；"
                                          "该残留原文归 P1-3（不在本卡裁权内），仅登记"),
            },
            "P2-8": {
                "status": "disposed",
                "reason": ("H-CN-ZIJIN-VOL-03.falsifier.threshold 已改为「期初库存须由上一期披露的期末库存量取得 + "
                           "与库存量同比变动方向一致」的判定式，缺上期数据则转 STOP_DISCLOSURE_ADAPTATION；"
                           "falsifier.observability_note 存在并登记 OPEN-11"),
                "evidence": ["evidence/I-11-A/hypotheses.json",
                             "evidence/I-11-A/mechanism_review.md §5 第 9 条 (sha256 70c3ca91c16bacedb719fbe8033ee169a490017e9da3099906879e222f8c6d26)"],
                "note": "跨期可得性 = OPEN-11，归矿业行业 reviewer，本卡不裁；observable 具体性原无机器检查（CE-10 证明），已由 G9 补上",
            },
            "P2-9": {
                "status": "disposed",
                "reason": ("state_before.json / state_after.json 的 plan_reviews.entries 各 285 条"
                           "（path/byte_size/mtime_local）+ file_count + listing_note + newest_file"
                           "（second_wave/final_review_checks.json, 2026-09-19 10:05:32, 14385 B），"
                           "声称与归档对称"),
                "evidence": ["evidence/I-11-A/state_before.json", "evidence/I-11-A/state_after.json"],
            },
        },
        "completeness_test": {
            "counterexamples_frozen": 11,
            "accepted_by_current_validator": 11,
            "rejected_after_patch": 11,
            "reviewer_original_mutations_replicated": 8,
            "reviewer_mutations_now_rejected": 7,
            "reviewer_mutations_still_accepted": [
                "REPRO-8 (two propositions sharing parameter_id, otherwise identical; REPORT.md L233)"],
            "own_suite": {"cases": 21, "rejected": 21, "accepted_by_mistake": 0,
                          "identical_to_archived_validation_report": True},
            "positive_case": "pass (0 errors)",
        },
        "red_green_mutation_rcs": {
            "baseline_main_rc": 0,
            "red_rc": 0,
            "red_meaning": ("all 11 pre-registered counterexamples ACCEPTED by the current validator (leak proven); "
                            "positive passes; own suite 21/21; REPRO-1..7 rejected; REPRO-8 accepted"),
            "green_rc": 0,
            "green_meaning": ("all 11 counterexamples REJECTED with their expected error codes; all 8 REPRO rejected; "
                              "positive passes; own suite 21/21"),
            "patched_main_rc": 0,
            "mutation_rcs": {r["mutation"]: r["rc"] for r in mut},
            "mutations_met_frozen_expectation": "%d/%d" % (
                sum(1 for r in mut if r["rc"] == 0 and r["phase_expectation_met"]), len(mut)),
            "mutation_operator": "delete exactly one # <OPEN12-Gn> ... # </OPEN12-Gn> block from the patched validator",
            "logs": ["red/baseline_run.log", "red/cases_original.json", "logs/red_run.log",
                     "green/patched_run.log", "green/cases_patched.json", "logs/green_run.log",
                     "logs/mutations.log", "mut/mutation_results.json"],
        },
        "i11c_reuse_conclusion": {
            "conclusion": "不建议在当前形态下直接复用（not_reusable_as_is）；若复用必须先满足 conditions 全部 5 条",
            "reasons": [
                "判据族不同：I-11-C 验收「可执行触发器 + 反方判断 + 保留历史的更新规则」，产物 schema"
                "（challenge_review.md / falsifiers.json / change_policy.json / qualitative_decision.json）"
                "与错误码族（STOP_REVIEW / STOP_LINEAGE）都不同",
                "现校验器对 I-11-C 的两条停止条件恰为盲区：「反证只有空泛风险词 → STOP_REVIEW」= 本卡 CE-10 的缺口；"
                "「触发更新改写旧预测 → STOP_LINEAGE」在本校验器中完全没有对应判据（无版本/谱系检查）",
                "decision.md DEC-14 的兼容影响只写了 I-11-B 复用条件（阈值依据三分类 + 更严参数唯一性），未覆盖 I-11-C；"
                "合并裁 G3 亦登记为「I-11-C 是否复用同一校验器未定」",
            ],
            "conditions": [
                "1) 先落地本卡 changes.diff 的 G1..G10，并以本卡红/绿/变异日志为回归基线",
                "2) 扩展而非替换：新增 STOP_REVIEW（空泛风险词，与 G9 同族）与 STOP_LINEAGE（旧快照被改写）两族判据，"
                "且同样先冻结 oracle 再跑再变异",
                "3) schema 适配层独立：不得直接拿 validate_hypotheses.py 跑 falsifiers.json / change_policy.json；"
                "须写 I-11-C 自己的绑定与错误码闭集并同步进其 oracle §7（DEC-14 恢复规则：改判据必须重跑全部反例并重新计数）",
                "4) 签署不可复用：approved_frozen 的独立 reviewer 身份 + decision_sha256 封缄（G8）继续生效，不得互签",
                "5) 不产生 I-11-C 的 ACCEPT、不解锁任何下游卡",
            ],
            "grants_nothing": True,
        },
        "releases_nothing": True,
        "does_not_claim_I11A_acceptance": True,
        "open12_status": "RULED_WITH_BLOCKED_VALUE（维持；本卡交付不自动解除，须 owner/独立 reviewer 裁定）",
        "does_not_unblock": ["I-11-A 再审", "I-11-B", "I-11-C",
                             "任何 BLOCKED（OPEN-2/3/5/6/11 等）", "任何参数/阈值/threshold_basis"],
        "changes_diff": {
            "file": "changes.diff",
            "touched_files": 1,
            "touched_paths": [".planning/2026-09-19-three-project-history-audit/execution_runs/"
                              "I-11-A/a20260919-01/tools/validate_hypotheses.py "
                              "(applied only to the iso_patched copy inside this attempt)"],
            "src_touched": 0,
            "scripts_touched": 0,
            "note": "只出 diff、不写真仓；原判据一律保留，只新增 10 个 marker 化判据块（可被变异逐条删除）",
            "src_sha256": "cb49360d15bc044dd46a3233c8ae0dd53eb3d95e2942bf2e6ac63d6937be17ac",
            "patched_sha256": "6427a26253bd0930321d4d51ab4794074834e41ffc05f5cf7da5912a64dba45f",
        },
        "sealed_source_verification": {
            "path": "execution_runs/I-11-A/a20260919-01",
            "files_hashed": 103,
            "manifest": "logs/source_manifest_before.sha256",
            "recheck": "工作前后逐文件 sha256 相等，差异 0（封盘未被改动）",
        },
        "git_diff_non_planning": 0,
        "git_diff_total_path_lines": 3826,
        "git_status_used": False,
        "git_writes": 0,
        "network_used": False,
        "unverified": [
            "P2-5 计数口径三处不一致（REPORT 正文 7/5 vs 其表格 8 行 6 放行 vs mechanism_review §5.8 与 DEC-14 "
            "「5 个未拒绝」却列 6 项），未证实任一口径",
            "CE-09（approved_frozen 编造 reviewer + 非 64-hex decision_sha256）按 §7「reviewer 非独立 → 拒绝」判，"
            "但 R2-1 字面只写「未填」——置信：边界",
            "CE-11（evidence_path 必须是已归档输出）来自 O-3 与字段语义，非逐字错误码行——置信：中",
            "本卡补丁 G1/G3/G9 为关键词/字典型有界代理，同样不构成完备性证明",
            "未覆盖的族：double_count_exclusion 语义质量、refuted_by 内容是否有意义、falsifier_candidates 为空、"
            "hypothesis_id 唯一性、O-8 与 R2-1 的内部张力",
        ],
        "not_done": [
            "未解除 OPEN-12、未改任何 status、未产生任何 ACCEPT",
            "未放行参数/阈值、未改 threshold_basis",
            "未代签（implementer_signed=false）",
            "未写五份计划文件",
            "未改 I-11-A 任何字节（103 文件 sha256 前后相等）",
            "未联网、未 git 写、未使用 git status",
            "未读取/采信 OPEN12-CUTOFF-ANNOUNCE-ACQUISITION 交付作为本卡证据",
            "未触碰 src/ 与 scripts/",
        ],
        "written_files": written_files(),
        "written_files_note": ("handoff.json 自身除外（自指不可自证）；iso/ 为封盘源的逐字节副本（103 文件，"
                               "见 logs/source_manifest_before.sha256），iso_patched/ 为补丁副本"),
        "next_action": "报父派独立复审；ACCEPT 只能由未参与本卡的独立 reviewer 签署",
    }
    p = os.path.join(D, "handoff.json")
    with io.open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(h, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    back = json.load(io.open(p, encoding="utf-8"))  # re-parse gate
    raw = io.open(p, "rb").read()
    print("handoff.json bytes=%d keys=%d reparsed=True BOM=%s CRLF=%s"
          % (len(raw), len(back), raw[:3] == b"\xef\xbb\xbf", b"\r\n" in raw))
    print("status=%s implementer_signed=%s releases_nothing=%s written_files=%d"
          % (back["status"], back["implementer_signed"], back["releases_nothing"],
             len(back["written_files"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
