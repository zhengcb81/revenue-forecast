# model_cards_append · 追加内容 + 前像/后像 sha + 前缀不变证明

- 工位：`execution_runs/OPEN2-C2-REGISTRATION/a20260926-01`（角色 `implementer_registration`）
- 目标文件：`execution_v2/model_cards.md`（**本计划内文件**；`.planning` 之外 0 字节）
- 形态：**T1-12 ①** —— 只在**文件末尾追加**新节，**既有行一字不动**；追加前记前像、追加后证前缀
- 判据冻结件：同目录 `oracle.md`（sha256 `a87d491fb562a246be6a04ab5e112f5ab196e45d9478dc601f967447a8115dd9`，15,831 B）
- 授权出处（逐字）：
  - `execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json` L54：「走替代口径则新 parameter_id 须在 model_cards.md 注册并通过 REGISTERED 检查」
  - 同文件 L119（C2 题面）：「OPEN-2：系数取值解 BLOCKED（S1/A 级证据 + 双签）或落实『分部对外收入 + 分金属销量』替代口径并注册新 parameter_id」
  - `execution_runs/OPEN2-SUBSTITUTE-CALIBER/a20260925-01/handoff.json` L21：「model_cards.md 新增 parameter_id 注册 + hypotheses.json 新版本 + decision.decision_sha256（均属实现者/编排层写入面，本工位无该权限）」

---

## ① 前像 / 后像（本机 `SHA256` 实测，非引用）

| 项 | 值 |
|---|---|
| 前像 sha256 | `855b5e2d06cc02a1c103316224a428fcfc7a1cc8fb3cfbf07f1f066a552855ab` |
| 前像字节 | 165,695 |
| 后像 sha256 | `cc24be67c06d250342d7624ad7d0190a21f67505317dc4e749d3e809deb0748d` |
| 后像字节 | 171,460 |
| 追加字节 | 5,765 |
| 追加方式 | 读取前像原始字节 → 断言 sha256 与字节数与上表一致（不一致即中止，fail-closed）→ 仅追加 → 复算 |
| 编码 | UTF-8 无 BOM（首三字节 `35,32,73` = `## `）、全文 `CR` 字节数 = 0（纯 LF） |

**前像 sha 在开工前的独立对照**：本工位冻结 `oracle.md` **之前**实测 `model_cards.md = 855b5e2d…`（165,695 B），与 `execution_v2/validation.json.document_hashes["model_cards.md"]`（2026-09-21 实测值）逐字符相同 ⇒ 前像自上一次计划级验证以来未被改动。

## ② 前缀不变证明（T1-12 ① / 本计划 append-3 同形）

- 方法：取**后像文件的前 165,695 字节**，复算其 sha256，与**前像 sha256** 比对；
- 实测：`prefix_sha256_recomputed = 855b5e2d06cc02a1c103316224a428fcfc7a1cc8fb3cfbf07f1f066a552855ab` ⇒ **`prefix_bytes_unchanged = true`**（后像字节 = 前像字节 + 追加字节，前像逐字节保留）；
- 追加前后各复算一次（追加脚本内一次、收尾 `final_check` 再一次），两值相同；
- 既有行核对：`grep -c` 层面，追加只增加 1 个 `##` 标题及其下文；`dispatch.json` 的 32 个卡标题绑定位置全部未变（见 §③）。

## ③ 追加的完整内容（逐字，未删改一字）

`````markdown
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
`````

（以上即追加文本全文；文件末尾以 `LF` 结束，无尾随空行。）

## ④ 已知副作用：段绑定失配（如实实测，不回改、不越权修复）

同一判定式的只读复现（逐行照抄 `validate_execution_pack.py` L25–L36，**不执行该脚本**——它会覆写 `execution_v2/validation.json`，超出本工位写入面）：

| 时点 | 绑定段数 | 错误 |
|---|---|---|
| 追加前（基线） | 32 | `[]`（0 错） |
| 追加后 | 32 | `["stale:I-10-B", "clone:I-10-B"]` |

- **原因（机械、可预期）**：`I-10-B` 是 `source_document = model_cards.md` 的**最后一个**卡片标题，其段终点是 `len(source)`；任何末尾追加都会扩段 ⇒ 段 sha 与 `card_I-10-B.md` 正文比对同时失配。**这正是 `oracle.md` §6 第 1 条在追加前冻结的预期结果**（预测 2 条，实测 2 条，逐条同名）。
- **不修复的理由**：修复需要改 `dispatch.json.source_section_sha256` 与 `card_I-10-B.md`，两者**不在本工位写入面**（写入面 = 本 attempt 5 件 + `model_cards.md` 追加）。
- **移交项（给编排层）**：按 T1-12 ① 同步刷新 `I-10-B` 的 `source_section_sha256` 与卡文正文（或把本追加节纳入 `I-10-B` 段的正式勘误流程），再重跑 `validate_execution_pack.py`。
- **对既有红/绿状态的影响**：`execution_v2/validation.json`（2026-09-21T19:28:12Z）**本就有 32 条** `source binding changed or missing`（产品仓 `scripts/*.py` 漂移）⇒ 该验证器**在本轮之前即不通过**；本轮不改变其红/绿结论，但**新增 2 条可归因于本追加的错误**，故登记而非隐瞒。

## ⑤ 边界

1. `model_cards.md` **只追加、不改动既有行**（前缀证明见 §②）；
2. 未修改 `dispatch.json` / `card_*.md` / `model_cards.json` / `validate_execution_pack.py` 任何字节；
3. 4 条新 id 全部 `low/base/high = null`、`released = false`、`state = pending_professional_decision` —— **不放行任何参数**；
4. 未新增任何换算系数、未使用跨层相除、未移除任何 `_PLACEHOLDER`、未关闭任何 `BLOCKED-*`；
5. `.planning` 之外写入 = 0 字节；git 写 = 0；`git status` 未执行；网络请求 = 0。
