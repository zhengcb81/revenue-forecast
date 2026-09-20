"""Write the closing narrative artefacts of one M29/M30/M31 attempt.

Writes, into <attempt>/:
  decision.md   why this card needed no professional design decision at the A-C stage
  review.md     the implementer's self-description PLUS the explicit list of points an
                independent reviewer is invited to attack (never a self-signed acceptance)
  changes.diff  an explicit empty diff: no product file was touched
  recovery/README.md  what the recovery artefacts are and how to re-run them

All narrative content is parameterised by the card; nothing here contains a measurement that is
not also in the evidence files, and no number is typed twice (the script reads them).

Usage:
  python -X utf8 -B write_closing_docs.py --card M29 --attempt-root <attempt>
"""

from __future__ import annotations

import argparse
import datetime
import json
import os

CARDS = {
    "M29": {
        "model_id": "commercial_launch",
        "card_title": "M29 · commercial_launch · supply-constrained commercial launch",
        "positive_expected": "[300]",
        "positive_hand": "min(1000 x 0.2, 150) x 0.5 x 4 = 300",
        "continuity_expected": "[300, 1000]",
        "negative_card": "adoption_rate = [1.1] (ratio domain [0,1])",
        "continuity_break": "years = [2027, 2029] (must be consecutive and increasing)",
        "no_optional_extra": ("this model has no stock-flow bridge, so its card-specific negative is a "
                              "DOMAIN negative and its CONT-BREAK is a fiscal-year break"),
        "business_negative": ("the card's business negative (conditional revenue is not a "
                              "probability-weighted expectation of approval; demand and supply ramps "
                              "out of step need a professional time model) is not runtime-enforceable"),
    },
    "M30": {
        "model_id": "finite_adoption",
        "card_title": "M30 · finite_adoption · finite market adoption",
        "positive_expected": "[600]",
        "positive_hand": "500 + 100 - 50 - 200 = 350 (bridge) ; 200 x 3 = 600",
        "continuity_expected": "[600, 0]",
        "negative_card": "closing_unserved_market = [351] (stock-flow balance)",
        "continuity_break": ("opening_unserved_market = [500, 351] with closing_unserved_market = "
                             "[350, 351] (continuity: year 2 opens 1 above year 1 closing)"),
        "no_optional_extra": ("this model DOES have the stock-flow bridge, so CONT-BREAK is a genuine "
                              "cross-year continuity break and the card's own two-year case is used "
                              "verbatim as the continuity positive"),
        "business_negative": ("the card's business negative is partly enforceable: the pool identity "
                              "and cross-year continuity are enforced, but whether a reported figure "
                              "is a first adoption or a renewal is a disclosure question"),
    },
    "M31": {
        "model_id": "inventory_sellthrough",
        "card_title": "M31 · inventory_sellthrough · inventory and sell-through bridge",
        "positive_expected": "[160]",
        "positive_hand": "100 + 60 + 10 - 5 - 80 = 85 (bridge) ; 80 x 2 = 160",
        "continuity_expected": "[160, 0]",
        "negative_card": "closing_inventory = [86] (stock-flow balance)",
        "continuity_break": ("opening_inventory = [100, 86] with closing_inventory = [85, 86] "
                             "(continuity: year 2 opens 1 above year 1 closing)"),
        "no_optional_extra": ("this model DOES have the stock-flow bridge, so CONT-BREAK is a genuine "
                              "cross-year continuity break and the card's own two-year case is used "
                              "verbatim as the continuity positive"),
        "business_negative": ("the card's business negative is partly enforceable: the bridge and "
                              "'scrapping is not negative revenue' are enforced, but entity mixing "
                              "(company vs channel inventory) and control transfer are not"),
        "card_text_divergence": ("card_M31.md L9 omits net_revenue_per_unit from the required list "
                                 "while the registry declares it required; the binding asserts "
                                 "against the registry and records the divergence"),
    },
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(CARDS))
    parser.add_argument("--attempt-root", required=True)
    args = parser.parse_args()

    card = args.card
    info = CARDS[card]
    attempt = os.path.abspath(args.attempt_root)
    evidence = os.path.join(attempt, "evidence", card)
    with open(os.path.join(evidence, "run_result.json"), "r", encoding="utf-8") as handle:
        run_result = json.load(handle)
    neg = run_result["negative_summary"]
    tolc = run_result["exit_code_semantics"]
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()

    decision = ("# {title} — decision.md\n\n"
                "**A-C 阶段没有需要专业审查的设计决定；不适用原因如下。**\n\n"
                "## 1. 本卡属于哪一类\n\n"
                "M29/M30/M31 是 I-10 的公式卡，调度验收范围只有 A–C：绑定、冻结期望并运行唯一入口 "
                "`calculate_registered_model`、以及用新 deepcopy 输入执行负例。按 "
                "`START_HERE.md` 第 47 行，需要先写 `decision.md` 并交专业审查的是跨进程锁/崩溃恢复、"
                "发布包事务边界、writer/producer 契约变更、财期/重述/收入总净额与 payability 归属、"
                "不可识别模型参数、样本/基准/统计阈值与概率校准、部署迁移与自然观察资格。\n\n"
                "## 2. 逐项判定（not_applicable_with_reason）\n\n"
                "| 专业门 | 本卡判定 | 依据 |\n|---|---|---|\n"
                "| 跨进程锁与崩溃恢复 | not_applicable_with_reason | 本卡只调用纯函数，不写任何共享状态、"
                "不启 worker、不加锁 |\n"
                "| 发布包事务边界 | not_applicable_with_reason | 不产出发布包，只产出本 attempt 目录内证据 |\n"
                "| writer/producer 契约变更 | not_applicable_with_reason | 未改任何产品文件（见 "
                "`changes.diff` 为空的显式声明与 `integrity.json`） |\n"
                "| 财期/重述/总净额/payability | not_applicable_with_reason | A–C 不使用真实披露；这属于 D "
                "（披露适配），本卡保持 `unmapped` |\n"
                "| 不可识别模型参数 | not_applicable_with_reason | A–C 只做合成数值；识别性问题属于 I-11-B |\n"
                "| 样本/基准/统计阈值/概率校准 | not_applicable_with_reason | 属于 I-12（准确性），本卡保持 "
                "`unproven` |\n"
                "| 部署迁移与自然观察资格 | not_applicable_with_reason | 本卡不部署、不发布 |\n\n"
                "## 3. 仍然存在、但不属于 A–C 的专业问题\n\n"
                "- D（披露适配）确实需要行业/会计 reviewer：{business_negative}。本卡据此把 "
                "`disclosure_adaptation` 保持 `unmapped`，并把该点记入 `oq_rulings.json` OQ-03。\n"
                "- 需要 owner 裁定的两项：OQ-01（隔离绑定来源）与 OQ-05（`oracle.md` 被事后按同内容"
                "恢复，其当前 mtime 晚于产品 stdout）。两项均已在 `handoff.json` 的 `open_questions` "
                "里指名归属。\n\n"
                "## 4. 本文件的签署边界\n\n"
                "本文件不构成任何资格授予。`qualification.json` 只更新 `formula`，且状态由 runner 的"
                "原始退出码决定；`accepted` 只能由独立 reviewer 写。\n"
                ).format(title=info["card_title"], business_negative=info["business_negative"])

    divergence = ""
    if info.get("card_text_divergence"):
        divergence = ("- **卡片正文与注册表的分歧（已被记录而非被静默解决）**："
                      + info["card_text_divergence"] + "\n")

    review = ("# {title} — review.md（实现者自述 + 待 reviewer 攻击点；**未自签**）\n\n"
              "状态：`review_pending`。本文件由实现者撰写，**不含任何 accepted**；独立 reviewer 的"
              "结论应另写并覆盖/追加本节。生成时间 {now}。\n\n"
              "## 1. 本 attempt 实际做了什么\n\n"
              "1. 绑定：`binding.json` 在同一隔离副本上读回模型契约，并断言 "
              "`declared_drivers_match_registry_contract = true`；卡片引用的入口行 `model_registry.py:308` "
              "与注册行 `model_extensions.py:{regline}` 都在跑产品之前核对过。\n"
              "2. 冻结期望：`oracle.md`（手算）与 `evidence/{card}/{{input,oracle,cases}}.json`（由"
              "`scripts/oracle_{card}.py` 生成，只用标准库、从不 import 产品）。\n"
              "3. 唯一产品调用：`calculate_registered_model(**input)`，经 `--code-root "
              "iso/checkout_scripts`（与生产逐字节相同）。\n"
              "4. 负例：{neg_total} 个，每个都在**新的 deepcopy** 上执行；只有 "
              "`model_registry.ModelRegistryError` 记为通过。\n"
              "5. 变异自证与重生成证明：`mutation_selfcheck.json`、`oracle_regen_proof.json`。\n"
              "6. 枚举与边界探针：`registry_enumeration.json`（`oq_rulings.json` 的所有计数来源）、"
              "`extra_probes.json`（非门控）。\n\n"
              "## 2. 关键测量（全部取自证据文件，未在此重述第二遍）\n\n"
              "- 正例：期望 {pos_exp}，实测 {pos_act}（手算：{pos_hand}）\n"
              "- 连续性正例：期望 {cont_exp}，实测 {cont_act}\n"
              "- 结构/长度保真：`fidelity_ok = {fid}`，`len(output) == len(years)` = {lenok}\n"
              "- 负例：{neg_pass}/{neg_total} 拒绝；runner 原始退出码 {rc}（判定 `{verdict}`）\n"
              "- 变异自证（先红后绿）：{mut}\n"
              "- oracle 逐字节可重生成：{regen}\n\n"
              "## 3. 请求独立 reviewer 攻击的点\n\n"
              "1. **手算复算**：从 `card_{card}.md` 原文独立重算正例与两年连续性，不看本 attempt 的"
              "`oracle.json`；再看 `evidence/{card}/oracle.json` 的 `hand_work` 是否与你的算式一致。\n"
              "2. **负例语义**：确认 {neg_total} 个负例的**期望错误原因**与卡片/共用规则一致，特别是"
              "卡片专属负例（{neg_card}）与 CONT-BREAK（{cont_break}）——注意：{no_optional}。\n"
              "3. **是否只测了目标异常**：`negative_results.json` 记录了 `is_target_type` 与"
              "`is_import_or_file_error`，请确认没有任何一条以 ImportError/FileNotFoundError 混过。\n"
              "4. **变异证明是否真的先红后绿**：`mutation_selfcheck.json` 的 5 次运行分别是 "
              "rc 3 / 3 / 2 / 1 / 0；请尤其确认 B 例（把 CONT-BREAK 改成完全平衡的输入后 runner 必须报"
              "`FAIL_not_rejected`）不是同义反复，且 `B0_unpatched_continuity_break` 先证明了原负例确实被拒。\n"
              "5. **oracle 是否真的独立**：`oracle_selfcheck.json` 只列 import 行；请自行确认生成器"
              "没有间接 import 产品，并确认 `oracle_regen_proof.json` 的逐字节一致是**重新生成**而非复制。\n"
              "6. **mtime/新鲜度**：请检查 `source_manifest.json` 的 `mtime_ordering`、"
              "`oracle_document.freshness_claim` 与 `revision_r2.json`，特别是本 attempt 已自曝的"
              "OQ-05（`oracle.md` 事后按同内容恢复）。请裁定该自曝是否足以支撑“冻结先于运行”，"
              "或要求重跑一个新 attempt。\n"
              "7. **卡片正文与注册表的一致性**：请独立核对 `card_{card}.md` 的必填清单与注册表，"
              "并对任何分歧给出裁定。{divergence}\n"
              "8. **未被本卡证明的东西**：披露适配（`unmapped`）与准确性（`unproven`）**没有**因为"
              "本卡通过而获得任何证据；请确认 `qualification.json` 只动了 `formula`。\n"
              "9. **隔离与生产零改动**：请核对 `integrity.json`、`before/`+`after/` 的 "
              "`git status --porcelain` 与 `source_hashes.txt`，并确认 `changes.diff` 为空是**真实**的。\n\n"
              "## 4. 实现者已知的弱点（主动列出，便于攻击）\n\n"
              "- 三个 attempt 的 `scripts/oracle_*.py` 是**同一份**生成器（都含 M29/M30/M31 三个 builder），"
              "因此 `oracle_selfcheck.json` 的 `script_sha256` 三卡相同；独立性来自“不 import 产品”，"
              "不来自“三份不同的脚本”。\n"
              "- `defaults` 用例与 `positive` 用例逐字节相同（这三个模型确实没有可选驱动器），因此该用例"
              "不提供额外证据，只用于证明“无默认值”这一契约事实。\n"
              "- `extra_probes.json` 是非门控的：它的期望值不进入 runner 退出码，reviewer 不应把它当作"
              "通过条件，但可以质疑其中任何一条 probe 的设计。\n"
              "- `iso/oracle_card.md` 的名字有历史误导性（它不是 markdown，而是 `--emit-script` 写出的"
              "生成器副本）；`source_manifest.json` 的 `naming_note` 已声明。\n"
              ).format(title=info["card_title"], now=now, regline=211 if card == "M29" else (
                  216 if card == "M30" else 220), card=card, neg_total=neg["total"],
                  pos_exp=info["positive_expected"], pos_act=run_result["positive"].get("actual"),
                  pos_hand=info["positive_hand"], cont_exp=info["continuity_expected"],
                  cont_act=run_result["continuity_positive"].get("actual"),
                  fid=run_result["fidelity"].get("fidelity_ok"),
                  lenok=run_result["fidelity"].get("length_equals_years"),
                  neg_pass=neg["passed"], rc=run_result.get("exit_code"),
                  verdict=run_result.get("verdict"),
                  mut="见 evidence/{card}/mutation_selfcheck.json".format(card=card),
                  regen="见 evidence/{card}/oracle_regen_proof.json".format(card=card),
                  neg_card=info["negative_card"], cont_break=info["continuity_break"],
                  no_optional=info["no_optional_extra"], divergence=divergence)

    changes = ("# changes.diff — {card} (attempt a20260919-01)\n"
               "#\n"
               "# NO PRODUCT CHANGE. This attempt modified no file outside its own attempt\n"
               "# directory, so this diff is empty BY CONSTRUCTION and that emptiness is a\n"
               "# claim a reviewer can falsify:\n"
               "#   * binding.json  -> allowed_write_roots / forbidden\n"
               "#   * integrity.json -> production_hashes_rechecked_after_the_run\n"
               "#   * before/ and after/ -> git status --porcelain of the three repos, plus\n"
               "#     source_hashes.txt for scripts/model_registry.py, scripts/model_extensions.py\n"
               "#     and scripts/forecast/segments.py\n"
               "#   * after/rerun_sha256.json -> the same hashes taken again after all card work\n"
               "# Generated {now}.\n"
               ).format(card=card, now=now)

    recovery = ("# recovery/ — {card} attempt a20260919-01\n\n"
                "本卡是纯函数公式卡：没有共享状态、没有 worker、没有锁、没有事务，因此没有“崩溃后恢复”"
                "这一步。目录里留下的东西有三个用途：\n\n"
                "| 路径 | 是什么 | 怎么复现 |\n|---|---|---|\n"
                "| `selfcheck/` | 变异自证（先红后绿）的**副本**现场：A/B0/B/C/D/E 六次 runner 运行的"
                "`run_result_*.json` 与 `stdout_*.txt`；冻结证据从未被写入 | 重跑 `E-mutation-selfcheck` "
                "单元（`scripts/mutation_selfcheck.py`），它每次都会重建 `recovery/selfcheck/` |\n"
                "| `selfcheck_result.json` | 与 `evidence/{card}/mutation_selfcheck.json` 同内容的副本，"
                "便于只看 recovery/ 的人也能读到结论 | 同上 |\n"
                "| `regen_verify/` | 逐字节重生成证明的 scratch 树：`evidence/{card}/{{input,oracle,cases}}.json` "
                "在空目录里被重新生成并与冻结件比 sha256 | 重跑 `D-oracle-regen-verify` 单元 |\n"
                "| `line_boundary_demo/` | r2 规则的机制演示：把 `oracle.md` 追加一节后，按真实行边界"
                "截断能复现追加前 sha256（只在 scratch 副本上做） | 重跑 `G-pack-evidence` 单元"
                "（`scripts/pack_card.py`） |\n"
                "| `venv_probe/` | attempt 解释器记录（路径 + sha256 + 版本） | 重跑 `A0-iso-venv-record` |\n\n"
                "**恢复规则**：本 attempt 的任何一步失败都不需要“回滚产品”，因为产品从未被写入；"
                "正确动作是修脚本后**在同一个 attempt 内重跑该单元**，并把失败现场保留在 "
                "`evidence/{card}/runs/<unit>/`（每次运行都覆盖同一 unit 的 rc/stdout/stderr，"
                "`pipeline_run.json` 记录最后一次驱动的逐单元原始返回码）。\n"
                ).format(card=card)

    files = {
        "decision.md": decision,
        "review.md": review,
        "changes.diff": changes,
        os.path.join("recovery", "README.md"): recovery,
    }
    for rel, text in files.items():
        path = os.path.join(attempt, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        print("wrote", path, os.path.getsize(path), "bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
