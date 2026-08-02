# 提案：负向驱动（headwind）进入正式输出 — schema 3.6

状态：**已评审通过 — 方案 A（2026-08-01，用户裁决）**；**已于 2026-08-02 实现为 schema 3.6**（走规则 10 完整变更流程：schema 版本、input/output/compliance/backtesting 文档、3.5 旧 schema 只读兼容测试、CHANGELOG）
编制：2026-08-01（Phase 17.6）
依据：findings A10、REVIEW.md F10、阿里巴巴会话（2026-08-01）

## 1. 问题

`growth_driver_tree` 的归因权重限定 `(0,1]`（正权重），负向根无法量化进入正式输出。阿里巴巴会话中，商家补贴（contra-revenue，Q4 使 CMR 增速从 +8% 降至 +1%）只能转为 `contrary` 证据节点 + `data_gaps` 文字，正式输出 `headwinds: []`。

设计意图（`references/growth-driver-tree.md`）："Preserve negative roots as revenue headwinds"——负向驱动应**量化**呈现，而非只存在于文字缺口。

## 2. 候选方案

### 方案 A：允许 `weight ∈ [-1, 1]`

- **schema 字段**：`growth_driver_tree.drivers[].segment_attribution[].weight` 范围从 `(0,1]` 放宽到 `[-1,1]`；segment 权重和仍归一为 1（正负抵消）。
- **验证器改动点**：权重范围检查（`> 0` → `!= 0` 或允许负）；归一化逻辑（现有 `abs(total - 1.0)` 校验）；driver 正负标记推导（`weight < 0` → headwind）。
- **输出形状**：`growth_driver_analysis` 增加 `headwinds[]`（driver_id、-weight、受影响 segment/年份）；现有 `drivers[]` 保留正驱动。
- **迁移影响**：现有输入全部为正权重 → 向后兼容（权重 ∈ (0,1] 仍合法）；schema 版本 3.6；需要新 fixture（负权重）+ 迁移测试。
- **优点**：最小 schema 变化；负根与正根同构。
- **缺点**：权重语义从"分配占比"变为"净贡献"，解读变复杂；segment 内正负混合时归一含义需明确定义。

### 方案 B：driver 级 `direction: positive|negative` 字段 + 输出拆分

- **schema 字段**：`growth_driver_tree.drivers[].direction`（枚举）；权重保持 `(0,1]`（绝对值）；输出按 direction 拆分 `drivers[]` / `headwinds[]`。
- **验证器改动点**：direction 枚举校验；负向 driver 的 evidence 必须是 `contrary`/`official_operating_data` 类（防误标）；输出拆分逻辑。
- **迁移影响**：现有输入无 direction 字段 → 默认 `positive`（向后兼容）；schema 3.6。
- **优点**：权重语义不变（仍是占比，direction 显式化正负）；contra-revenue 与增长负贡献可分别表达。
- **缺点**：一个 segment 的正负驱动相加需定义"净归因"；字段新增。

### 方案 C：维持现状 + 文档声明

- 保持权重 `(0,1]`；负向机制只能作为 `contrary` 证据节点 + `data_gaps` 文字。
- 在 `output-schema.md` 明确声明 `headwinds` 的语义（当前为空 = 无量化负向驱动，不代表无风险）。
- **优点**：零改动。
- **缺点**：A10 问题继续存在（负向机制无法量化进入正式驱动分析），设计意图不落地。

## 3. 评审结论

**2026-08-01 用户裁决：方案 A（`weight ∈ [-1, 1]`）通过。** 实现列为后续工作（新 Phase），实施前必须完成规则 10 全部变更流程：schema 3.6 版本、input/output/compliance/backtesting 文档、旧 schema fixture、迁移/只读兼容测试、CHANGELOG。实现要点（评审时确认）：负权重根的显式 headwind 输出、segment 权重和仍归一为 1、正负混合时的净归因语义定义、现有正权重输入向后兼容。

## 4. 评审问题清单（原）

- 谁评审：用户 + 引擎维护者（schema 变更走 task_plan 0.3 规则 10 完整流程：schema 版本、文档、fixture、迁移/只读兼容测试、CHANGELOG）。
- 何时评审：下个涉及驱动树扩展的 Phase 之前，或用户要求时。
- 通过标准：选定方案 A 或 B；明确负权重/负方向的归一语义与输出展示；反向兼容旧输入；负向驱动 fixture 齐全。
- 未评审通过前：**不实现任何代码**，不触碰 `revenue_core.py` / `input-schema.md` 的 schema 定义。

## 4. 登记

- 阿里巴巴会话中该案例的输入（contra-revenue 补贴机制、take-rate 驱动的 contrary 节点）已保留在 `Research\alibaba-forecast\input.json`，可作为方案验证 fixture 原型。
