本卡由[model_cards.md](model_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[model_cards.md共用规则](common_model_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

## I-10-B — model_registry 的静默补 0 与按名字定符号

Parent：I-10。依赖：I-00-B。Owner：模型注册维护者；独立 reviewer。

来源：`OWNER_DECISIONS.md` §5 第 1/2 项 + §13 **T1-22**（授权立卡，**两项同卡**）。

锚点：RF/scripts/model_registry.py 的 `MODEL_REGISTRY` 与 `driver_value_bounds`。
本卡**不改任何 M01–M31 的公式**、**不动任何冻结件**。

1. **缺陷①：`model_registry.py:335` 静默补 0。**
   现行 `values = drivers.get(driver, [spec.defaults.get(driver, 0.0)] * len(years))`
   ⇒ 无显式 default 的 optional driver 被补 `0.0`（**31 个槽位 / 24 个模型**）。
   这把"**不存在**"与"**没找到**"编码成**同一输入**，D 阶段会直接产出错误映射。
   修复：省缺即抛 `ModelRegistryError`；**仅当** `spec.defaults` 有显式值时才允许省缺。
   注意：把隐式 0 变显式 0 **仍无法区分**"没找到"，故不采用"补显式 0"方案。
2. **缺陷②：`_SIGNED_DRIVERS` 按名字定符号。**
   现状：`other_revenue` signed 而 `usage_revenue` 非 signed；而
   `franchise_system_sales`/`supply_revenue`/`recognized_performance_fees` 同属
   "**可冲回已确认金额**"却在 `[0, inf)` ⇒ 名字与语义不符。
   修复：改为基于**语义角色**的规则（例如按 dimension 与显式的"可冲回"角色位判定），
   不按 driver 名字硬编码集合。
3. **兼容性（必须先声明）**：改②会改变部分 driver 的值域上下界。
   25 个既有 driver 的边界是否受影响须**逐个列出**；任何边界变化都要附"哪个 M 卡的哪个用例会受影响"。
   受影响的历史期望**一律追加更正、不回改**（沿用 T1-12 的统一规则）。
4. 负例（可失败用例）：①某个只有 optional driver 且无显式 default 的模型，省缺时**必须抛**；
   ②`franchise_system_sales` 传入负值时必须**被接受**（语义角色为可冲回）；
   ③一个名不在任何角色表里的新 driver 必须**不得**静默获得"按名字猜测"的符号。
5. 不得为本卡扩大 allowlist 去改 31 张 M 卡的正文或证据；
   本卡产出的是**注册层契约**，由 I-10-A 在后续复验中消费。
6. `code_root` 锚点按事故教训**每次复算**：`scripts/model_registry.py` 与
   `scripts/model_extensions.py` 的哈希必须与本卡绑定值一致；不一致即停止并登记漂移。

退出：省缺不再静默补 0；符号按语义角色判定且兼容性影响逐项列出。
恢复：回退注册层改动；保留边界影响清单与全部负例输出。

## 附录 A · parameter_id 注册（OPEN-2 C2 第二分支，实现者追加 · T1-12 ① 形态）

> 追加人：`execution_runs/OPEN2-C2-REGISTRATION/a20260926-01`（角色 `implementer_registration`）。
> 授权：`I11A-OPEN-MERGE/a20260924-01/handoff.json` L119（C2 题面）与 L54（「走替代口径则新 parameter_id 须在 model_cards.md 注册并通过 REGISTERED 检查」）＋ `OPEN2-SUBSTITUTE-CALIBER/a20260925-01/handoff.json` L21（注册属实现者写入面）。
> 本节只追加 4 个新 `parameter_id` 条目；既有行一字未改（前像/后像 sha 与前缀不变证明见 `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/model_cards_append.md`）。
> 本节不放行任何参数：4 条 `low/base/high` 全为 `null`、`released = false`、`state = pending_professional_decision`；不改任何 `threshold_basis`、不移除任何 `_PLACEHOLDER`、不关闭任何 `BLOCKED-*`、不产生 `I-11-B` 的 ACCEPT、不构成 `OPEN-2` 解除。
> 落点规则：`decision.md` DEC-5（只落到本文件已注册的 `model_id`/`driver_name`）；唯一性规则：`validate_hypotheses.py` L197–L213（一个 id 只能表示一条命题 × 一个 driver × 一个 `effective_period`）。
> 口径来源：`OPEN2-SUBSTITUTE-CALIBER/a20260925-01/substitute_caliber.json`（sha256 `649a9ff8d1a4490aedbe863ee52a338ba7b30c50408d7ca5f0a9361daa622e72`）`new_parameter_id`（主 id + 3 伴随）；条件 C-1…C-5 的逐条回源复核见该注册 attempt 的 `registration.md`。

### A.1 注册表（4 条新 parameter_id）

| parameter_id | model_id | driver_name | unit | unit_basis | factor_basis | base_period | effective_period | low / base / high | released |
|---|---|---|---|---|---|---|---|---|---|
| `ZIJIN_MINERAL_COPPER_REALIZED_UNIT_REVENUE_FY2027` | `resource` | `realized_price` | 人民币元/吨（不含税） | `disclosed_same_table_pairing` | `none` | FY2023–FY2025 | FY2027 | `null` / `null` / `null` | `false` |
| `ZIJIN_MINERAL_GOLD_REALIZED_UNIT_REVENUE_FY2027` | `resource` | `realized_price` | 人民币元/克（不含税） | `disclosed_same_table_pairing` | `none` | FY2023–FY2025 | FY2027 | `null` / `null` / `null` | `false` |
| `ZIJIN_MINERAL_ZINC_SALEABLE_VOLUME_FY2027` | `resource` | `saleable_volume` | 吨 | `disclosed_production_sales_table` | `none` | FY2023–FY2025 | FY2027 | `null` / `null` / `null` | `false` |
| `ZIJIN_MINERAL_SILVER_SALEABLE_VOLUME_FY2027` | `resource` | `saleable_volume` | 千克 | `disclosed_production_sales_table` | `none` | FY2023–FY2025 | FY2027 | `null` / `null` / `null` | `false` |

### A.2 口径与约束（照 substitute_caliber.json 逐条）

1. **两槽独立（C-1）**：收入槽 `ZIJIN_SEG_MINERAL_EXTERNAL_REVENUE_FY2027`（`direct_revenue` / `revenue`）与量槽（`resource` / `saleable_volume`）分别落参数；**禁止跨层相除** —— 不得用分部对外收入除以分金属销量合成「元/吨」类单位收入（该读法属被拒构造，前一工位 `RED_B` 在 STRICT 下实测拒绝）。本节 4 条字段内**不含任何跨层相除合成式**。
2. **同表同注（C-2）**：两个 `realized_price` 槽的分子分母同出 `按产品划分的销售详情` 同一张表与同一条表注（「本表不含非控股企业的相关数据。」）；披露单价为公司原文值，混合单价为由披露值复算并标 `derived`；`单价 × 销售数量 ≈ 金额` 实测相对误差 0.000616% ≤ 0.1%。两个 `saleable_volume` 槽的单位是 `②产销量情况分析表` 直接披露单位（表注「本表不含非控股企业相关数据。」），非换算值；`substitute_caliber.json` 只对单位经济学槽定义 `unit_basis = disclosed_same_table_pairing`，量槽无该字段，故此处显式登记 `unit_basis = disclosed_production_sales_table`（取值归属本注册节，非既有枚举）。
3. **单收入路径（C-3）**：`direct_revenue`（分部对外收入）与 `resource`（销量 × 单位实现收入）二选一进收入路径，另一侧只作对账（`Σ分产品收入 − 内部抵消数 = 合并营业收入`；`Σ分部对外收入 = 合并营业收入`）；价格变化不得再作为额外收入叠加；同一笔销量不得重复计入。
4. **零系数（P2）**：`factor_basis = none`、`conversion_factor_value = null`、`factor_source_in_filing = not_applicable_no_conversion_used`、`cross_company_comparable = not_applicable`（本口径不含任何跨公司输入）；任何换算系数在任何路径出现即判违例。
5. **单位尺度（非金属换算）**：金/银披露单价为 元/克、披露销量为 千克，模型相乘须显式登记 ×1000 比例因子并标 `unit_scale_only = true`。
6. **落位**：4 条 id 均为**新增**，不新增命题、不新增模型、不改既有 14 个 id；`hypotheses` 侧落位与 `decision_sha256` 见 `execution_runs/OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json`。
7. **状态**：4 条均 `state = pending_professional_decision`、`threshold_basis_touched = false`、`placeholder_suffix_removed = false`；幅度（`low`/`base`/`high`）留给 I-11-B 校准，本节不给。

### A.3 段绑定副作用登记（追加前先声明，不回改）

本节按 T1-12 ① 在文件**末尾**追加 ⇒ `validate_execution_pack.py` L25–L36 以「卡片标题 → 下一个卡片标题（最后一个到文件尾）」提取段并比对 `dispatch.json.source_section_sha256` 与 `card_*.md` 正文，**最后一个卡片段 `I-10-B`** 的段哈希将因此失配。追加前实测基线：32 个段绑定、0 错、最后绑定卡 = `I-10-B`。追加后实测与移交项见 `model_cards_append.md` §③；`dispatch.json` 与 `card_I-10-B.md` 不在本工位写入面，**不修改**。
