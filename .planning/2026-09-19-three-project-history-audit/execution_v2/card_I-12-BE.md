# card_I-12-BE —— 合并卡（`I-12-B` + `I-12-C` + `I-12-D` + `I-12-E`）

> **性质**：**owner 授权的执行单元合并**（`2026-09-26` 「先做甲，然后做乙」）—— **不改原四卡的判据一字**，仅把它们作为**四段串行阶段**装进一个执行单元（一次复审 + 一次落定）。
> **原卡文（判据权威）**：`card_I-12-B.md` · `card_I-12-C.md` · `card_I-12-D.md` · `card_I-12-E.md` —— **全部只读、零字节改动**。
> **归并理由**（甲 分析）：四卡是同一数据管线的四段（样本 → 建模基线 → 指标 → 判定），输入输出严格串行、共用同一 `sample` 与 `origin` 边界、共用同一 `OPEN-2` 红线与 `freeze-before-read` 规则 —— **分四次派单/复审/落定是纯仪式开销**。
> **不并的边界**：`I-16-A/B`（隔离要求新 `attempt`）、`I-17-A/B`（真实时间窗口与终审独立性）**维持分立**。

## 依赖
`I-07-E`（accepted_scoped）+ `I-12-A`（accepted_scoped，**双签在飞**）+ 上游 `I-11-B`/`I-11-C`

## Owner（合并后）
`I-12-B` 的数据执行者 + `I-12-D` 的统计复算 reviewer + `I-12-E` 的统计与行业 reviewer —— **实现者不自签**，独立复审由编排层另派。

## 四段动作（**逐段判据以原卡为准，此处仅索引**）

### 阶段 B（数据准备）—— 原卡 `card_I-12-B.md`
1. `sample_id` 唯一生成 + 筛选/排除全量表
2. `source version/hash/available_at` 逐条验证 `available_at<=origin`；疑义隔离；**禁事后补当时不可得数据**
3. 真实 vintage 保留原预测；重建实验单列 `reconstructed` + 全部假设

### 阶段 C（建模基线）—— 原卡 `card_I-12-C.md`
1. 同 sample 只用 origin 前资料构造驱动；保存模型/配置/参数/source manifest hash/运行日志
2. 按冻结规则产生各 baseline；缺历史期标 `not_applicable`，**禁未来资料补齐**
3. **读实际值前冻结** forecast、low/base/high 语义、预测时间、版本、hash；重跑须有原因并留旧版

### 阶段 D（指标计算）—— 原卡 `card_I-12-D.md`
0. **先跑 `metric_numeric_oracle` + 负例**（`evidence/I-12-BE/metric_oracle_result.json`）合格才碰真实样本
1. 逐样本 `signed_error`/`abs_error` 明细；`metric_definitions` 处理零分母/缺失/异常/边界
2. 成对评 model vs baseline；分行业/阶段/市场/horizon 报 `n_companies`/`n_origins`

### 阶段 E（判定）—— 原卡 `card_I-12-E.md`
1. 按冻结阈值判 `supported/unsupported/inconclusive`（保留负 skill 与失败层）
2. 限定到数据集/模型版本/行业/生命周期/披露质量/horizon；未覆盖分层标 `unproven`
3. 三栏合并（公式资格/披露适配/准确性）—— **禁一栏 PASS 盖另一栏**

## 停止条件（**四段任一触发即整卡 `STOP`，fail-closed**）
- 阶段 B：`available_at>origin` 的疑义无法隔离 ⇒ `STOP`
- 阶段 C：缺历史期且卡文明示 `not_applicable` 不足 ⇒ `STOP`
- 阶段 D：`metric_numeric_oracle` 或负例失败 ⇒ `STOP`（**先跑 oracle 是硬前置**）
- 阶段 E：任一阈值无法定 ⇒ `inconclusive`（**非 `STOP`**，如实登记）
- **全局 `OPEN-2` 红线**：`124,248.63`（真值 38,175.95）只登记不消费

## 验收
四段各自判据全达成 + 每段独立 `oracle` 冻结点 + 全局红绿变异 ≥3（覆盖四段）+ 封盘 `f2178768…` 零字节

## 状态
`planned` →（实现后）`review_pending` →（一次复审）→（一次落定）`accepted_scoped`
**四段的判定结论全部登记在同一 handoff，`status_authority` 引用同一复审报告**
