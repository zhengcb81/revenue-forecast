"""Write the frozen oracle.md for one M21-M24 attempt, BEFORE any product run.

This script reads only the independently generated evidence/<card>/oracle.json
(produced by scripts/oracle_<card>.py, stdlib only) and renders the frozen
expectation document. It never imports the product.

Run:
  <attempt>/iso/venv/Scripts/python.exe -X utf8 -B scripts/write_oracle_md.py \
      --card M21 --attempt <attempt-root>
"""

from __future__ import annotations

import argparse
import json
import os
import sys

META = {
    "M21": {
        "title": "M21 · delivery_pipeline · 实物订单交付桥",
        "card_line": "Card M21（`execution_v2/card_M21.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。",
        "registry_line": "入口 `scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册 `scripts/model_registry.py:241`。",
        "unit_line": "订单与交付同件/套单位；价格 U/已确认交付单位。",
        "required_line": "`opening_orders`、`new_orders`、`cancellations`、`deliveries`、`ending_orders`、`unit_revenue`",
        "optional_line": "`timing_factor`（默认 1）、`other_revenue`（默认 0）",
        "formula_text": "revenue = deliveries × unit_revenue × timing_factor + other_revenue；桥约束 opening_orders + new_orders − cancellations − deliveries = ending_orders",
        "formula_source": "`card_M21.md` L8、L48「手算：50+30−5−40=35；40×3+2=122」",
        "scope": "设备、汽车、航空、房地产交付。",
        "card_neg_reason": "`timing_factor` 是卡片 L9 列出的可选**比例**项，本卡沿用现行 ratio 契约 [0,1] 作为拒绝条件，**不声称**经济上永不可能（`common_model_cards.md` L11）。该例在专门的 2 年输入 `card_neg`（= 第 4 节连续性正例）上把 `timing_factor[1]` 置为 `1.5`，使**值域守卫**而不是长度守卫成为拒绝原因；卡片 L50 在同一 1 年正例上替换 `ending_orders=[36]` 的负例被记为**非判定性观察项** `OBS-CARD-NEG-ENDING`（冻结预期同样是 `ModelRegistryError`，见第 6 节）。",
        "bridge_reason": "`delivery_pipeline` 是**存量桥**：逐年存在 `opening_orders + new_orders − cancellations − deliveries = ending_orders` 的平衡约束，且 `opening_orders[t]` 必须等于 `ending_orders[t−1]`。因此 STOP_BRIDGE 在本卡**适用**（不是 not_applicable），并落地为第 4、5 节的连续性正例与断裂负例。",
        "business_rejects": [
            ("R8-BIZ", "已全年交付数再乘经营时间比例", "**业务拒绝**：需 `special_review`，本卡记录为披露缺口", "否（不是运行时契约）"),
            ("R9-BIZ", "交付不当然等于收入确认（控制权转移/验收条件未满足）", "**业务拒绝**：需 `special_review`", "否"),
            ("R10-BIZ", "取消订单未在桥中显式扣除", "**业务拒绝**：桥必须平衡", "否"),
        ],
        "disclosure_items": "订单桥、取消、交付验收、净价、控制权转移、交付与确认差额（`card_M21.md` L52）。",
        "base_anchor": "无（本卡卡片未给基期锚点字段；存量桥的锚点是 `opening_orders`，须来自已披露期初订单）。",
        "continuity_note": "连续性断裂 patch 只改 `opening_orders`、`ending_orders` 的第 2 个元素：两个年度各自平衡，但 FY2028 opening = 36 ≠ FY2027 closing = 35。",
    },
    "M22": {
        "title": "M22 · milestone_royalty · 里程碑与销售分成",
        "card_line": "Card M22（`execution_v2/card_M22.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。",
        "registry_line": "入口 `scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册 `scripts/model_registry.py:242`。",
        "unit_line": "合同可分成销售 U × 分成率；里程碑/服务是已确认 U。",
        "required_line": "`eligible_sales`、`royalty_rate`",
        "optional_line": "`milestone_revenue`（默认 0）、`service_revenue`（默认 0）",
        "formula_text": "revenue = eligible_sales × royalty_rate + milestone_revenue + service_revenue",
        "formula_source": "`card_M22.md` L8、L36「手算：500×0.08+12+3=55」",
        "scope": "授权药物、专利、内容，开发授权至成熟。",
        "card_neg_reason": "`royalty_rate` 是卡片 L9 的必填比例项；`1.01` 越出 ratio 契约 [0,1]，冻结预期为 `ModelRegistryError`。",
        "bridge_reason": "`milestone_royalty` **不是存量桥**（无期初/期末对账项），STOP_BRIDGE → **not_applicable_with_reason**；适用的连续性检查只有财年连续性。",
        "business_rejects": [
            ("R8-BIZ", "概率加权潜在付款当作已确认收入", "**业务拒绝**：需 `special_review`，本卡记录为披露缺口", "否（不是运行时契约）"),
            ("R9-BIZ", "研发事件与商业条件未分开", "**业务拒绝**：需 `special_review`", "否"),
            ("R10-BIZ", "阶梯分成率被压成单一费率而未披露", "**业务拒绝**：需 `special_review`", "否"),
        ],
        "disclosure_items": "分成基础、阶梯率、地域期限、里程碑触发、义务与确认金额（`card_M22.md` L40）。",
        "base_anchor": "无（本卡卡片未给基期锚点字段）。",
        "continuity_note": "本卡无存量桥，故 CONT-BREAK 采用**财年断裂**：`years = [2027, 2029]`（缺 2028），预期 `ModelRegistryError`。",
    },
    "M23": {
        "title": "M23 · insurance_service · 保险服务披露映射",
        "card_line": "Card M23（`execution_v2/card_M23.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。",
        "registry_line": "入口 `scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册 `scripts/model_registry.py:243`。",
        "unit_line": "覆盖单位必须披露定义；U/覆盖单位不能拿保费充当。",
        "required_line": "`coverage_units`、`revenue_per_coverage_unit`",
        "optional_line": "`timing_factor`（默认 1）、`other_revenue`（默认 0）",
        "formula_text": "revenue = coverage_units × revenue_per_coverage_unit × timing_factor + other_revenue",
        "formula_source": "`card_M23.md` L8、L36「手算：100×2×0.5+10=110」",
        "scope": "仅有可验证覆盖单位与收入映射的保险业务；复杂 IFRS17 需精算/会计审批。",
        "card_neg_reason": "`timing_factor` 是卡片 L9 的可选比例项；`1.1` 越出 ratio 契约 [0,1]，冻结预期为 `ModelRegistryError`。",
        "bridge_reason": "`insurance_service` **不是存量桥**（无期初/期末对账项），STOP_BRIDGE → **not_applicable_with_reason**；适用的连续性检查只有财年连续性。",
        "business_rejects": [
            ("R8-BIZ", "CSM、亏损合同或投资成分不明就做适配", "**业务拒绝**：需精算/会计 `special_review`，本卡记录为披露缺口", "否（不是运行时契约）"),
            ("R9-BIZ", "拿保费充当 U/覆盖单位", "**业务拒绝**：需 `special_review`", "否"),
            ("R10-BIZ", "把本模型当成完整 IFRS17 引擎", "**业务拒绝**：卡片 L42 明示不是", "否"),
        ],
        "disclosure_items": "保险服务收入、覆盖单位、CSM/风险调整释放、投资成分排除、再保边界（`card_M23.md` L40）。",
        "base_anchor": "无（本卡卡片未给基期锚点字段）。",
        "continuity_note": "本卡无存量桥，故 CONT-BREAK 采用**财年断裂**：`years = [2027, 2029]`（缺 2028），预期 `ModelRegistryError`。",
    },
    "M24": {
        "title": "M24 · subscription_arr_bridge · ARR 存量与收入时点",
        "card_line": "Card M24（`execution_v2/card_M24.md`），Parent I-10，状态 planned，调度依赖 I-00-B、I-00-C。",
        "registry_line": "入口 `scripts/model_registry.py:308 calculate_registered_model(model_id, base_revenue, drivers, years)`；注册 `scripts/model_extensions.py:180`。",
        "unit_line": "ARR 为年化运行率 U；当期收入用各变动的时间分数。",
        "required_line": "`opening_arr`、`expansion_arr`、`new_arr`、`closing_arr`、`gross_retention_rate`、`lost_arr_revenue_fraction`、`expansion_revenue_fraction`、`new_arr_revenue_fraction`",
        "optional_line": "`usage_revenue`（默认 0）",
        "formula_text": "revenue = opening_arr − opening_arr × (1 − gross_retention_rate) × lost_arr_revenue_fraction + expansion_arr × expansion_revenue_fraction + new_arr × new_arr_revenue_fraction + usage_revenue；桥约束 opening_arr − lost + expansion_arr + new_arr = closing_arr，其中 lost = opening_arr × (1 − gross_retention_rate)",
        "formula_source": "`card_M24.md` L8、L51「手算：流失200×0.1=20；期末200−20+30+40=250；收入200−15+15+10+5=215」",
        "scope": "有 ARR 桥的 SaaS 增长/成熟/收缩。",
        "card_neg_reason": "`closing_arr` 是必填对账项；改成 `[251]` 使 FY2027 桥不平衡，冻结预期为 `ModelRegistryError`（桥平衡守卫）。",
        "bridge_reason": "`subscription_arr_bridge` 是**存量桥**：逐年存在 `opening_arr − lost + expansion_arr + new_arr = closing_arr` 的平衡约束，且 `opening_arr[t]` 必须等于 `closing_arr[t−1]`；卡片 L59 另给基期锚点 `{\"field\":\"base_arr_parameter_id\",\"driver\":\"opening_arr\",\"dimension\":\"revenue\"}`。STOP_BRIDGE 在本卡**适用**。",
        "business_rejects": [
            ("R8-BIZ", "NRR 当作 GRR", "**业务拒绝**：需 `special_review`，本卡记录为披露缺口", "否（不是运行时契约）"),
            ("R9-BIZ", "ARR 当作收入", "**业务拒绝**：卡片 L57 明示 ARR ≠ 收入", "否"),
            ("R10-BIZ", "没有存续期初 ARR 却给存量扩张", "**业务拒绝**：卡片 L57 明示", "否"),
        ],
        "disclosure_items": "ARR 桥、GRR 定义、存续客户扩张、新增、各发生月份、用量与基期锚点（`card_M24.md` L55）。",
        "base_anchor": "`{\"field\":\"base_arr_parameter_id\",\"driver\":\"opening_arr\",\"dimension\":\"revenue\"}`（`card_M24.md` L59；亦见生产 `scripts/model_extensions.py:18` 的 `EXTENSION_OPENING_BALANCES`）。",
        "continuity_note": "连续性断裂 patch 只改 `opening_arr`、`closing_arr` 的第 2 个元素。卡片 L116 描述为「两个年度各自平衡」，但 `closing_arr=[250,251]` 同时改动了 FY2027 的 closing，故实际先触发的是 **FY2027 桥平衡守卫**而不是 FY2028 连续性守卫；两者都是 `ModelRegistryError`，冻结要求是**异常类型**，不是具体消息（见第 4 节与第 11 节）。",
    },
}


def render(card: str, oracle: dict, attempt: str) -> str:
    m = META[card]
    pos = oracle["positive"]
    cont = oracle["continuity_positive"]
    dflt = oracle["defaults"]
    ids = oracle["negative_ids"]
    lines = []
    add = lines.append
    add("# %s — 冻结 oracle（运行前写定）" % m["title"])
    add("")
    add(m["card_line"])
    add("Attempt: `execution_runs/%s/a20260919-01`。" % card)
    add("本文在**任何产品代码运行之前**写定；写入后不得为贴合结果而修改，"
        "运行后的对账只允许以**追加**节形式补记（见文末「运行后对账」节）。")
    add("")
    add("## 0. 独立性声明（最重要）")
    add("")
    add("- 第 1–5 节的**全部数值预期来自手算**，并由本 attempt 内独立脚本")
    add("  `scripts/oracle_%s.py` 用 Python 标准库（`decimal`/`json`/`hashlib`/`os`/`argparse`）复算。" % card)
    add("  该脚本**不 import** 产品任何模块（`model_registry` / `model_extensions` 均不出现），")
    add("  自检记录见 `evidence/%s/oracle_selfcheck.json`。" % card)
    add("- **绝不**通过调用被测函数 `calculate_registered_model` 或任何产品 helper 生成 expected。")
    add("- 公式来源：%s。" % m["formula_source"])
    add("- %s 该入口仅在冻结之后用于定位调用点。" % m["registry_line"])
    add("- `evidence/%s/oracle.json` 可由该脚本**逐字节重生成**（无时间戳、无随机量、无字典序依赖）。" % card)
    add("")
    add("## 1. 公式 / 单位 / 口径")
    add("")
    add("| 项 | 冻结内容 | 出处 |")
    add("|---|---|---|")
    add("| 公式（卡片文字） | %s | `card_%s.md` L8 |" % (m["formula_text"], card))
    add("| 必填 driver | %s | `card_%s.md` L9 |" % (m["required_line"], card))
    add("| 可选 driver / 默认 | %s | `card_%s.md` L9 |" % (m["optional_line"], card))
    add("| 单位 | %s | `card_%s.md` L8 |" % (m["unit_line"], card))
    add("| 适用 | %s | `card_%s.md` L7 |" % (m["scope"], card))
    add("| 硬约束 | 输出长度 = `len(years)`；逐年检查；非有限值/布尔冒充数值一律拒绝 | 通用契约 |")
    add("| 比例域 | 维度为 `ratio` 的 driver 默认域 [0,1]；本卡**不声称**经济上永不可能 | `common_model_cards.md` L11 |")
    add("| 存量桥 | %s | `card_%s.md` L133 |" % (m["bridge_reason"], card))
    add("")
    add("## 2. 合成正例（positive）")
    add("")
    add("输入 = `card_%s.md` 合成输入原文（逐字段一致）：" % card)
    add("")
    add("```json")
    add(json.dumps(oracle["_positive_input"], ensure_ascii=False, indent=1))
    add("```")
    add("")
    add("手算（逐步，未取整）：")
    add("")
    add("- %s" % oracle["hand_notes"]["positive"])
    add("")
    add("**期望输出 = `%s`**（与卡片手算一致）。" % pos["expected"])
    add("- 输出长度 = %d = `len(years)`；输出年份应为 `%s`。" % (len(pos["years"]), pos["years"]))
    add("- 逐值容差 = `1e-9 × max(1, |expected|)` = `%s`。" % pos["tolerances"])
    add("- 除数值外还比对**输出结构**：类型为 list、长度等于 `len(years)`、每个元素为有限 float（见 `formula_result.json` 的 `structure_checks`）。")
    add("")
    add("## 3. 默认值案例（defaults）")
    add("")
    add("只给必填 driver，省略全部可选 driver：")
    add("")
    add("```json")
    add(json.dumps(oracle["_defaults_input"], ensure_ascii=False, indent=1))
    add("```")
    add("")
    add("手算：%s。" % oracle["hand_notes"]["defaults"])
    add("")
    add("**期望输出 = `%s`**，长度 %d。" % (dflt["expected"], len(dflt["years"])))
    add("- 该案例证明默认值确实被应用，且**没有**被错当成「必填缺失」。")
    add("- 默认值不是缺披露时填零/一的授权（`common_model_cards.md` L22）；本案例只检验契约行为。")
    add("- 默认值案例**不参与**运行器退出码判定（`defaults_ok_not_gating`）。")
    add("")
    add("## 4. 连续性案例（continuity）")
    add("")
    add(m["continuity_note"])
    add("")
    if card == "M21":
        add("")
        add("本卡同时冻结第二个 2 年输入 `card_neg`（= 本节的连续性正例，逐字段相同），供 NEG-CARD 在**存在 index 1** 的路径上检验 `timing_factor` 的值域守卫；card_neg 的期望输出与连续性正例相同，两例都必须在同一 attempt 内可运行。")
    add("- Continuity positive：`years = %s`；手算：" % cont["years"])
    for i, hw in enumerate(cont["hand_work"]):
        add("  - FY%s = %s → %s" % (cont["years"][i], hw, cont["expected"][i]))
    add("  期望 = `%s`。此例**先**运行通过，才允许应用断裂 patch。" % cont["expected"])
    add("- Continuity 断裂 patch：%s" % _cont_patch_text(card))
    add("  → 预期 `ModelRegistryError`。")
    add("")
    add("## 5. 负例（card-specific + N01–N05）")
    add("")
    add("首个必填 driver = `%s`。每个负例使用**新的 deepcopy 独立输入**，互不共享可变对象；"
        "全部在内存中构造，**不经 JSON 解析器**（避免解析器代拒）。" % oracle["_first_required_driver"])
    add("")
    add("| 例 | 变换（在冻结输入基础上只改这一处） | 冻结预期 |")
    add("|---|---|---|")
    for row in oracle["_case_rows"]:
        add("| %s | %s | `%s` |" % (row["id"], row["mutation"], row["expected"]))
    add("")
    add("合计 **%d 个负例**。通过判据：目标异常类型必须是 `ModelRegistryError`；"
        "`ImportError`/`ModuleNotFoundError`/`FileNotFoundError` **不得**计为通过。" % oracle["negative_count"])
    add("")
    add("NEG-CARD 语义：%s" % m["card_neg_reason"])
    add("")
    add("## 6. 观察项（非 pass/fail 设计观察）")
    add("")
    add("| ID | 变换 | 预期 | 说明 |")
    add("|---|---|---|---|")
    for obs in oracle["_observation_rows"]:
        add("| %s | %s | %s | %s |" % (obs["id"], obs["mutation"], obs["expectation"], obs["why"]))
    add("")
    add("## 7. 卡片文字 vs 实现公式串（须核对，不得为对齐而改预期）")
    add("")
    add("卡片 L8/L51/… 只给出算式与手算结果，未给实现公式串。运行后从隔离副本读取")
    add("`MODEL_REGISTRY[\"%s\"].formula`，与第 1 节公式逐项比对；" % oracle["model_id"])
    add("若不一致，记录差异而**不是**修改期望值（见文末「运行后对账」节）。")
    add("")
    add("## 8. 拒绝条件（本卡记录并执行）")
    add("")
    add("| ID | 拒绝条件 | 冻结预期 | 本卡是否可运行时执行 |")
    add("|---|---|---|---|")
    add("| R1 | 必填 driver 长度 ≠ `len(years)`（含 `[]`） | `ModelRegistryError` | 是（N02） |")
    add("| R2 | 缺必填 driver | `ModelRegistryError` | 是（N03） |")
    add("| R3 | 未注册 driver | `ModelRegistryError` | 是（N04） |")
    add("| R4 | `years` 为空/非整数财年 | `ModelRegistryError` | 是（N05a/N05b） |")
    add("| R5 | `years` 非连续递增 | `ModelRegistryError` | 是（CONT-BREAK） |")
    add("| R6 | 非有限值（nan/inf/-inf，含 bool 冒充数值） | `ModelRegistryError` | 是（N01a-d） |")
    add("| R7 | 卡片专属的**运行时**拒绝条件 | `ModelRegistryError` | 是（NEG-CARD） |")
    for row in m["business_rejects"]:
        add("| %s | %s | %s | %s |" % row)
    add("")
    add("R8-BIZ–R10-BIZ 是**业务拒绝**条件（卡片「专业决策/业务负例」节），不在运行时契约内，"
        "因此在运行时负例表里不计入 pass/fail；它们属于 `disclosure_adaptation` 的 STOP 条件。")
    add("## 9. 披露采集与基期锚点（D/E 输入，不在本卡授予资格）")
    add("")
    add("- 披露采集项：%s" % m["disclosure_items"])
    add("- 基期锚点：%s" % m["base_anchor"])
    add("- 本卡只交付 A–C 公式证据；D/E 由 I-10-A 先行执行，F 需 I-12 冻结设计。")
    add("")
    add("## 10. 三种资格（本卡只填 formula）")
    add("")
    add("- `formula`：由本卡 A–C 结果决定（见 `evidence/%s/qualification.json`）；实现者**不自签** accepted。" % card)
    add("- `disclosure_adaptation`：保持 **unmapped**。D 需逐字段映射经行业/会计 reviewer 签署，"
        "且需「一个已结束期间的收入对账 + 生产 forecast 入口映射经独立审阅」。")
    add("- `accuracy`：保持 **unproven**。F 需 I-12 冻结设计（信息时点样本、baseline、统计不确定性），"
        "该设计不存在；本卡不作准确性主张。")
    add("")
    add("## 11. 停止条件自检（卡片「停止条件」节）")
    add("")
    add("- positive 不等或应拒绝负例未被拒绝 → `STOP_FORMULA`，**先记录反例，不重写实现**。")
    add("- 披露缺出处/单位/期间/总净额不明或 special_review 未决 → `STOP_DISCLOSURE_ADAPTATION`。")
    add("- 存量桥：%s" % ("本卡适用，落地为第 4/5 节。" if card in ("M21", "M24")
                          else "**not_applicable_with_reason**（第 1 节）。"))
    add("- 准确性：`STOP_ACCURACY`（无 I-12 冻结设计）。")
    add("")
    add("## 12. 桥平衡的有效分辨率（独立复核要求补记；见文末追加节的来源说明）")
    add("")
    if card in ("M21", "M24"):
        add("存量桥的平衡与跨年锚定不是精确等号比较，而是 "
            "`math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)`"
            "（%s）。"
            % ("`model_registry.py:154-157`：桥平衡 + 跨年 continuity" if card == "M21"
               else "`model_extensions.py:27-38` 的 `_equal` / `_bridge`（桥平衡 + 跨年 continuity）"))
        add("")
        add("- **有效绝对容差 = `max(abs_tol, rel_tol × max(|a|, |b|))` = "
            "`max(1e-9, 1e-9 × max(|closing|, |expected_closing|))`**；相对项非负，故下界为 1e-9。")
        if card == "M24":
            add("- 本卡合成例的被比较量级 |closing_arr| ≈ 250，故有效绝对容差 ≈ **2.5e-7**"
                "（比 1e-9 宽约 3 个量级）。")
            add("- 实测（本 attempt scratch 探针，**非判定性**）：正例 `closing_arr` 加 **+1e-7 → 通过**；"
                "加 **+1e-6 → 被拒绝**（`opening_arr stock-flow balance failed: FY2027`）。"
                "即 1e-7 在容差内、1e-6 在容差外。")
        else:
            add("- 本卡合成例的被比较量级 |ending_orders| ≈ 35，故有效绝对容差由 1e-9 的绝对项决定"
                "（相对项 3.5e-8 更大时以相对项为准）。")
            add("- 本卡未对该分辨率做数值探针；M24 同源比较的探针结果（1e-7 通过 / 1e-6 拒绝）在 M24 "
                "attempt 内记录，本卡不复制其结论。")
    else:
        add("本卡**不是存量桥**（第 1 节：not_applicable_with_reason），故桥平衡比较不适用；"
            "本卡的数值比较只有第 2/3 节的 `1e-9 × max(1, |expected|)` 容差。")
    add("")
    add("---")
    add("")
    add("（以下为运行后追记节，由 `scripts/append_oracle_run_section.py` 追加；")
    add("上方正文在运行前冻结，追加不改动任何期望值。）")
    add("")
    return "\n".join(lines)


def _cont_patch_text(card: str) -> str:
    if card == "M21":
        return "`opening_orders = [50, 36]`、`ending_orders = [35, 36]`（各自平衡但跨年 opening ≠ 上期 closing）"
    if card == "M24":
        return "`opening_arr = [200, 251]`、`closing_arr = [250, 251]`"
    return "`years = [2027, 2029]`（缺 2028，财年不连续）"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--card", required=True, choices=sorted(META))
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    card = args.card
    ev = os.path.join(args.attempt, "evidence", card)
    with open(os.path.join(ev, "oracle.json"), "r", encoding="utf-8") as fh:
        oracle = json.load(fh)
    with open(os.path.join(ev, "input.json"), "r", encoding="utf-8") as fh:
        input_doc = json.load(fh)
    with open(os.path.join(ev, "cases.json"), "r", encoding="utf-8") as fh:
        cases_doc = json.load(fh)

    oracle["_positive_input"] = input_doc["positive"]
    oracle["_defaults_input"] = input_doc["defaults"]
    oracle["_first_required_driver"] = cases_doc["first_required_driver"]

    rows = []
    for case in cases_doc["cases"]:
        expected = case["expected"]
        if case.get("expect_message_contains"):
            expected = "%s 且消息须含 `%s`" % (expected, case["expect_message_contains"])
        rows.append({"id": case["id"], "mutation": _mutation_text(case),
                     "expected": expected})
    oracle["_case_rows"] = rows

    obs_rows = []
    for obs in cases_doc.get("extra_observations", []):
        obs_rows.append({"id": obs["id"], "mutation": _mutation_text(obs),
                         "expectation": _expectation_text(obs), "why": obs.get("why", "")})
    oracle["_observation_rows"] = obs_rows
    # probe_expected is frozen from the oracle generator only; it is attached to
    # observations whose id appears there.
    probe = cases_doc.get("probe_expected", {})
    for row in obs_rows:
        if row["id"] in probe:
            row["expectation"] = probe[row["id"]]

    text = render(card, oracle, args.attempt)
    target = os.path.join(args.attempt, "oracle.md")
    with open(target, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("wrote", target, "bytes", len(text.encode("utf-8")))
    return 0


def _mutation_text(case: dict) -> str:
    kind = case["kind"]
    driver = case.get("driver")
    if kind == "set_driver_element":
        return "`%s[%d] = %s`（基于 `%s`）" % (driver, case["index"],
                                            _value_text(case["value"]), case["base_input"])
    if kind == "set_driver":
        return "`%s = %s`（基于 `%s`）" % (driver, _value_text(case["value"]), case["base_input"])
    if kind == "delete_driver":
        return "删除 `%s`（基于 `%s`）" % (driver, case["base_input"])
    if kind == "add_driver":
        return "增加 `%s = %s`（基于 `%s`）" % (driver, _value_text(case["value"]), case["base_input"])
    if kind == "set_driver_multi":
        return "%s（基于 `%s`）" % (_value_text(case["value"]), case["base_input"])
    if kind == "set_years":
        return "`years = %s`（基于 `%s`）" % (_value_text(case["value"]), case["base_input"])
    if kind == "set_base_revenue":
        return "`base_revenue = %s`（基于 `%s`）" % (_value_text(case["value"]), case["base_input"])
    if kind == "input_replay":
        return "重放 `%s`" % case["input"]
    return kind


def _value_text(value) -> str:
    if isinstance(value, dict):
        if "__float__" in value:
            return "float('%s')" % value["__float__"]
        if "__bool__first__" in value:
            return "[True, ...]"
        if "__bool__" in value:
            return "True"
    return json.dumps(value, ensure_ascii=False)


def _expectation_text(obs: dict) -> str:
    if obs.get("expect_equal") is True:
        return "与 `%s` 相同" % obs.get("compare_to")
    if obs.get("expect_equal") is False:
        return "与 `%s` 不同" % obs.get("compare_to")
    return "不设预期"


if __name__ == "__main__":
    sys.exit(main())
