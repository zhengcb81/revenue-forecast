#!/usr/bin/env python3
"""生成 verification.json 与 handoff.json（只读汇总 + 写本 attempt 目录）。"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[2]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(p: Path) -> str:
    return str(p.relative_to(HERE)).replace("\\", "/")


def load(name: str) -> dict:
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def git(repo: str, *args: str) -> str:
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    return r.stdout.decode("utf-8", "replace").strip()


def main() -> int:
    mut = load("_mut/mutation_summary.json")
    drill = load("recovery_drill.json")
    man = load("combo_manifest.json")
    final = load("_live/result_final.json")
    gate0 = (HERE / "gate0_raw.txt").read_text(encoding="utf-8")

    deliverables = [
        "oracle.md", "deployment_proposal.md", "impact_scope.json", "combo_manifest.json",
        "recovery_drill.json", "snapshot_manifest.json", "gate0_raw.txt",
        "_probe_newprocess.py", "_bind_combo.py", "_recovery_drill.py", "_verify_combo.py",
        "_run_mutations.py", "_mut/mutation_summary.json", "_live/result_final.json",
        "probe_bind.json",
    ]
    written = {}
    for name in deliverables:
        p = HERE / name
        if p.exists():
            written[name] = {"bytes": p.stat().st_size, "sha256": sha(p)}

    inputs = {}
    for name in (
        "execution_v2/card_I-16-A.md",
        "execution_v2/common_root_cards.md",
        "execution_v2/START_HERE.md",
        "OWNER_DECISIONS.md",
    ):
        p = PLAN / name
        if p.exists():
            inputs[name] = sha(p)

    upstream = {}
    for card, attempt in (("I-07-D", "a20260923-01"), ("I-07-E", "a20260926-01"),
                          ("I-13-A", "a20260926-01"), ("I-13-BC", "a20260926-01")):
        p = PLAN / "execution_runs" / card / attempt / "handoff.json"
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            upstream[f"{card}/{attempt}"] = {"sha256": sha(p), "status": data.get("status")}

    repos_final = {}
    for key, path in (("RF", r"C:\Users\郑曾波\Projects\revenue-forecast"),
                      ("CW", r"C:\Users\郑曾波\Projects\company-wiki"),
                      ("DAYU", r"C:\Users\郑曾波\Projects\dayu-agent\dayu-agent")):
        diff = [x for x in git(path, "-c", "core.quotepath=false", "diff", "HEAD",
                               "--name-only").splitlines() if x.strip()]
        npl = [x for x in diff if not x.startswith(".planning")]
        repos_final[key] = {
            "head": git(path, "rev-parse", "HEAD"),
            "diff_total": len(diff),
            "diff_non_planning": len(npl),
            "staged": len([x for x in git(path, "-c", "core.quotepath=false", "diff",
                                          "--cached", "--name-only").splitlines() if x.strip()]),
        }

    arms = mut["arms"]
    red_arms = [a for a in arms if a["expected_rc"] == 3]
    green_arms = [a for a in arms if a["expected_rc"] == 0]

    verification = {
        "card_id": "I-16-A",
        "attempt_id": "a20260926-01",
        "role": "implementer_i16a",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "exit_code_legend": {
            "0": "pass（命令正常结束且全部不变量成立）",
            "1": "harness 失败（脚本/绑定/路径错误）",
            "2": "无裁决（冻结期望缺失/不可用，判定前发出）",
            "3": "不变量违例（具名 Jx）＝红臂证明“能发现版本错配”",
            "note": "本批 legend 为规范值；跨批聚合前必须先读本表",
        },
        "red_green_mutations": {
            "green_arms": green_arms,
            "red_arms": red_arms,
            "red_arm_count": len(red_arms),
            "meets_at_least_3_red": len(red_arms) >= 3,
            "all_rc_match": mut["all_rc_match"],
            "all_expected_violations_present": mut["all_expected_violations_present"],
            "original_artifacts_untouched": mut["original_artifacts_untouched"],
            "summary_path": "_mut/mutation_summary.json",
        },
        "three_repo_sha_consistency": {
            "gate0_observed": {
                "RF": "b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb",
                "CW": "bf0c8b27e83c3ee7e533c6031fefad8e27e5e121",
                "DAYU": "2115c86d5a9027bb51cbbc8a4d0175080732e4e6",
                "note": "门0 时刻；CW 于 21:08Z 复测时仍为 bf0c8b27（staged=1）",
            },
            "bound": {
                "RF": man["repos"]["RF"]["head"],
                "CW": man["repos"]["CW"]["head"],
                "DAYU": man["repos"]["DAYU"]["head"],
                "bound_at": man["bound_at_utc"],
            },
            "final_recheck": repos_final,
            "dirty_content_digest": {
                k: man["repos"][k]["dirty_content_digest_sha256"] for k in man["repos"]
            },
            "drift_detected": True,
            "drift_detail": (
                "CW HEAD bf0c8b27… → dbe47450…（外部会话提交）；CW 两文件内容在两次校验之间变化；"
                "CW untracked 50 → 51；CW/DAYU staged 1 → 0。本卡零 git 写，漂移来自外部写入方。"
            ),
            "consistent_at_final_verify": final["rc"] == 0,
            "final_verify_path": "_live/result_final.json",
        },
        "recovery_drill": {
            "path": "recovery_drill.json",
            "all_checks_ok": drill["all_checks_ok"],
            "checks": drill["checks"],
            "recovery_provable": drill["recovery_provable"],
            "migration_reversible": drill["migration_reversible"],
            "compat_boundary": drill["compat_boundary"],
            "production_catalog_anchor": drill["production_catalog_anchor"],
            "fail_closed_no_strict_gate_disabled": True,
        },
        "final_live_verification": {
            "rc": final["rc"],
            "mode": final["mode"],
            "checks": [{"id": c["id"], "ok": c.get("ok"), "status": c.get("status")}
                       for c in final["checks"]],
            "violations": final["violations"],
        },
        "upstream_inputs": upstream,
        "input_hashes": inputs,
        "gate0": {"passed": True, "raw_output": gate0, "raw_path": "gate0_raw.txt"},
        "written_files": written,
        "boundaries": {
            "git_status_run": False,
            "git_writes": 0,
            "network_used": False,
            "params_released": False,
            "writes_outside_planning": 0,
            "writes_outside_planning_detail": "项目内写入仅 .planning/**（本 attempt 目录 + 其内隔离副本/快照）；"
                                               "另在会话 %TEMP% 放置若干只读汇总用临时脚本（平台临时区，非产品非项目）；"
                                               "产品三仓 0 写",
            "product_repos_writes": 0,
            "production_change_executed": False,
            "open2_registered_not_consumed": True,
            "sealed_zero_byte_change": True,
            "i16b_dispatched": False,
        },
        "open_findings": [
            {"id": "u-I16A-0", "severity": "high",
             "text": "三仓组合在绑定期间被外部写入方改动（HEAD/内容/untracked/staged 四类漂移）；"
                     "复审者须在安静时刻复跑 J1，仍红则不得开部署窗口"},
            {"id": "u-I16A-1", "severity": "medium",
             "text": "2026-08-08 worker 运行组合的 4 个模块字节已不可重建（git 历史+磁盘均未命中）⇒ 禁止用作恢复目标"},
            {"id": "u-I16A-2", "severity": "low",
             "text": "一次 drill 重跑对着过期 snapshot 清单出现 R1=False；重绑后三次 drill 全绿"},
            {"id": "I14-E-unverified", "severity": "medium",
             "text": "OpenProcess DENIED ⇒ TESTSIDE 三臂不可证、进程命令行不可读；按 §三十八 以 unverified 登记，不作开工阻断"},
            {"id": "u-I16A-skillcopy", "severity": "low",
             "text": "skill 安装副本（Junction 目标）本会话不可读 ⇒ 该子项 unverified"},
        ],
        "status": "review_pending",
    }
    (HERE / "verification.json").write_text(
        json.dumps(verification, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    written["verification.json"] = {
        "bytes": (HERE / "verification.json").stat().st_size,
        "sha256": sha(HERE / "verification.json"),
    }

    authorized_verbatim = (
        "OWNER_DECISIONS.md §三十八 裁定一（L879-L886，逐字）：「裁定一：`I-16-A` 开工门槛 —— "
        "「授权开工（建议）」。依据卡文：`card_I-16-A.md` L5 `依赖：I-07-E、I-07-D、I-08、I-09、"
        "I-13、I-14、I-15`。开工判据（owner 明文改判，`§三十四` 同款）：1. 已 `accepted`：`I-07-D` · "
        "`I-07-E` · `I-09` · `I-13-A` · `I-13-BC` · `I-15-A` ✓ 2. `I-08-A`：按 `task_plan` 清单 `[x]` "
        "视为满足（其 `review_pending` 是复审明令「`not-granted` 项 3 禁写 `accepted`」的刻意状态，非未完成）"
        "3. `I-14` 家族：`A/B/C/D` 已落（`D` 的 `R2` 凭证修复 2026-09-26 `accepted_scoped`）；`E` 被 "
        "`OpenProcess` 环境阻断 ⇒ 以 `unverified` 登记，不作开工阻断 4. 红线（不因开工而放宽）：`I-16-A` "
        "自身动作 3「不能证明恢复则 `blocked`，不以关闭严格门回滚」维持 fail-closed；动作 4「真正未授权影响"
        "再向用户说明具体请求」维持 5. 不授予：不代 `I-14-E` 出结论 · 不解 `TESTSIDE` 环境阻断 · "
        "不放行参数 · 产出仍须独立复审」"
    )

    handoff = {
        "card_id": "I-16-A",
        "attempt_id": "a20260926-01",
        "parent": "I-16",
        "role": "implementer_i16a",
        "parent_agent_id": "session-19074bf0-0205-4315-af73-9db57597275a",
        "objective": "绑定拟部署完整组合：三仓源 commit+dirty 内容 hash、安装副本 hash、解释器/依赖、"
                     "config/policy/flags/schema 版本与真实加载模块；新进程加载路径验证 + 旧加载模块负例；"
                     "上个可恢复完整组合/迁移可逆/兼容边界；部署影响范围与可逆准备。生产变更不执行。",
        "authorized_by": {
            "source": "OWNER_DECISIONS.md §三十八 裁定一",
            "verbatim": authorized_verbatim,
            "dispatch_quote": "开工授权：OWNER_DECISIONS §三十八 裁定一 —— 你开工即持此授权，无需再核 7 项依赖",
            "owner_decision_s37": "OWNER_DECISIONS.md §三十七（L852-L871）：「给你授权所有的沙箱操作，不要再问我了」；"
                                  "边界：git add/commit/push 不在授权内、生产零未授权改动纪律不变",
        },
        "status": "review_pending",
        "implementer_signed": False,
        "releases_nothing": True,
        "releases_nothing_detail": "不产生 ACCEPT · 不放行任何参数（low/base/high 全 null、_PLACEHOLDER 维持）· "
                                   "不触发 falsifier/自动动作 · 不代 I-14-E 出结论 · 不解 TESTSIDE 阻断 · "
                                   "不派 I-16-B · 不写五份计划文件 · 不写 .planning 外 · 零 git 写 · 零网络 · "
                                   "封盘 f2178768… 与 store b2063ac8… 零字节变化 · 未执行任何生产变更",
        "params_released": False,
        "open2_ban_observed": True,
        "open2_ban_detail": "ZIJIN_MINERAL_REALIZED_UNIT_REVENUE base 124,248.63（真值 38,175.95）只登记不消费；"
                            "本卡未引用为部署输入",
        "i14e_env_blocked_registered": True,
        "i14e_env_blocked_detail": "OpenProcess DENIED（本会话实测 Get-CimInstance/Win32_Process 拒绝访问）"
                                   "⇒ TESTSIDE 三臂不可证，以 unverified 登记，不作开工阻断（§三十八 逐字）",
        "gate0_passed": True,
        "gate0_raw_output": gate0,
        "gate0_note": "写/回读/删三步本会话自探 + 封盘/store 只读复算 + 三仓 git diff 只读计数（含追加复测段，原始输出不删改）",
        "completed_steps": [
            "1 领取/回源：card_I-16-A.md（sha fa2884fa…）+ common_root_cards + START_HERE + "
            "OWNER_DECISIONS §三十八裁定一/§三十七 逐字回源 + 上游 4 份 handoff sha/status 只读",
            "2 门 0 自探留档：写/回读/删 + 封盘 f2178768…（51,697 B）+ store b2063ac8…（61,231 B）"
            "+ 三仓 diff 只读计数（gate0_raw.txt，含 CW 瞬时读数复测段）",
            "3 oracle 先冻结：卡文 L6/L8-L11/L13 逐字 + §三十八授权逐字 + 上游 sha + P1-P6 正例 + "
            "M1-M5 变异（≥3）+ rc 码表 + 红线 + 环境限制（写于任何验证运行之前）",
            "4 动作1：三仓 commit + dirty/untracked 逐文件 sha256（109 条）+ 安装层 12 件 hash + "
            "双解释器/依赖 + config/policy/flags/schema 值 + 新进程真实加载模块（combo_manifest.json）",
            "5 动作2：新进程探针 → live 校验 rc=0；M1 旧加载模块/M2 config/M3 schema 常量/M4 解释器/"
            "M5 安装副本 五臂 rc=3 具名命中；原件前后 sha 一致",
            "6 动作3：可逆准备（snapshot 109 文件）+ 隔离恢复演练 R1-R5 全绿；"
            "registry 前向无守卫、2026-08-08 运行态 4 模块字节不可重建分别登记",
            "7 动作4：impact_scope.json（写入/停重启/恢复步骤；production_change_executed=false；"
            "unauthorized_impact=false）+ 部署提案 deployment_proposal.md",
            "8 交审：verification.json（红绿 7 臂 + 三仓 sha 一致性 + 漂移登记）+ 本 handoff，"
            "status=review_pending（实现者不自签）",
        ],
        "next_step_number": 9,
        "next_action": "独立复审（另派，非本工位）按 review_and_handoff.md 复核：① 重跑 _verify_combo.py live 臂"
                       "（重点 J1_repo_source —— 若在安静时刻仍红 ⇒ 组合不稳定，不得开部署窗口，交 owner 裁定）；"
                       "② 复跑 _run_mutations.py 核 5 红 2 绿与具名命中；③ 复跑 _recovery_drill.py 核 R1-R5；"
                       "④ 裁定 u-I16A-1（2026-08-08 运行态不可重建）是否需另立补救卡；"
                       "⑤ 核 skill 安装副本与进程命令行两个 unverified 项的窗口内补检方式。"
                       "复审接受后由父直写落定；本卡不派 I-16-B（依赖顺序另派）。",
        "actions_done": {
            "action1_three_repo_manifest": True,
            "action2_newprocess_loadpath_negative": True,
            "action3_recovery_reversibility_compat": True,
            "action4_impact_scope_and_reversible_prep": True,
        },
        "recovery_verification_achieved": True,
        "recovery_evidence": "recovery_drill.json：R1 snapshot 还原 109 文件逐 sha 相等；R2 backup→migrate→restore 字节相等；"
                             "R3 更高 user_version fail-closed 文件不变；R4 结构漂移 fail-closed 只读；R5 registry 边界实测。"
                             "all_checks_ok=true ⇒ 恢复可证，未触发 blocked，且未关闭任何严格门。",
        "mutation_rc": {
            "legend": {"0": "pass", "1": "harness", "2": "no_verdict", "3": "invariant_violation"},
            "GREEN": 0, "M1_old_loaded_module": 3, "M2_config_drift": 3,
            "M3_schema_constant_drift": 3, "M4_interpreter_mismatch": 3,
            "M5_install_copy_drift": 3, "GREEN_FINAL": 0,
            "expected_match": mut["all_rc_match"],
        },
        "three_repo_sha": {
            "gate0": {"RF": "b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb",
                      "CW": "bf0c8b27e83c3ee7e533c6031fefad8e27e5e121",
                      "DAYU": "2115c86d5a9027bb51cbbc8a4d0175080732e4e6"},
            "bound_and_final": {k: man["repos"][k]["head"] for k in man["repos"]},
            "final_recheck": repos_final,
            "drift": "CW 由外部会话在本卡运行期间提交（bf0c8b27 → dbe47450）；本卡零 git 写",
        },
        "git_diff_non_planning": 0,
        "git_diff_non_planning_measured": (
            "git -c core.quotepath=false diff HEAD --name-only（只读，多轮）→ RF total=3830/non_planning=0；"
            "CW total=8/non_planning=8、DAYU total=1/non_planning=1 均为**既存产品改动/外部会话所为**，"
            "本卡写入面 = execution_runs/I-16-A/a20260926-01/**（.planning 内），"
            "产品仓零写 ⇒ 归因于本卡的 non_planning 改动 = 0；禁 git status 未跑；零 git 写"
        ),
        "written_files": written,
        "evidence_paths": [
            "oracle.md（门 0 原始输出 + §三十八授权逐字 + 判据/变异/rc 码表先冻结）",
            "deployment_proposal.md（动作 1-4 四段：三仓 manifest · 加载路径验证 · 恢复组合+可逆性 · 影响范围与步骤）",
            "verification.json（红绿 7 臂 + 三仓 sha 一致性 + 漂移登记 + 输入 sha）",
            "combo_manifest.json（组合绑定：31 artifacts / 109 dirty 条目 / 安装层 / 双解释器 / 数据层锚点）",
            "recovery_drill.json（R1-R5 隔离恢复演练）",
            "snapshot_manifest.json + snapshot/**（可逆准备：dirty/untracked 层字节快照）",
            "_mut/**（M1-M5 变异副本 + 各臂 verifier_output + mutation_summary.json）",
            "_live/result_final.json（最终 live 校验 rc=0）",
            "impact_scope.json（动作 4 影响范围清单）",
        ],
        "open_questions": [
            "u-I16A-0（高）：三仓组合并发漂移 —— 复审须在安静时刻复跑 J1；仍红则不得开部署窗口（owner 裁定）",
            "u-I16A-1（中）：2026-08-08 worker 运行组合 4 个模块字节不可重建（git 14/22/8/21 rev + 磁盘 669 文件均未命中）"
            "⇒ 禁止作恢复目标；是否需补救卡由 owner/编排层定",
            "u-I16A-2（低）：一次 drill 重跑对着过期 snapshot 清单出现 R1=False，重绑后三次全绿",
            "I14-E-unverified / u-I16A-skillcopy：两个 unverified 子项的窗口内补检方式由复审定",
            "registry 前向兼容无 fail-closed 守卫（R5 实测）：是否要求部署窗口先备份 registry —— 交复审/owner",
        ],
        "blocked_by": [],
        "status_authority_note": "实现者不自签；status=review_pending 是证据齐全的进入形态，不是验收；落定走父直写（V3 轻格式）",
        "boundary_self_declaration": {
            "no_auto_actions": True,
            "no_falsifier_triggered": True,
            "no_status_decision_changed": True,
            "production_change_executed": False,
            "writes_outside_planning": 0,
            "writes_outside_planning_detail": "项目内写入仅 .planning/**（本 attempt 目录 + 其内隔离副本/快照）；"
                                               "另在会话 %TEMP% 放置若干只读汇总用临时脚本（平台临时区，非产品非项目）；"
                                               "产品三仓 0 写",
            "git_writes": 0,
            "git_status_run": False,
            "network_used": False,
            "params_released": False,
            "five_plan_files_untouched": True,
            "sealed_hypotheses_untouched": {"sha256": "f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28",
                                            "bytes": 51697, "zero_byte_change": True},
            "store_untouched": {"sha256": "b2063ac8533a96ba0be8095293e30191cc0796a7eb84dcd16dac0b71aff413ff",
                                "bytes": 61231, "low_base_high_all_null": True},
            "not_dispatched": ["I-16-B"],
        },
        "final_live_verify_rc": final["rc"],
        "final_live_verify_violations": final["violations"],
    }
    (HERE / "handoff.json").write_text(
        json.dumps(handoff, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print("verification.json + handoff.json written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
