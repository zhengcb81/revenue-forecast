# W09-RF-RESEARCH 研究备忘

状态：**内部研究修复完成；经验校准仍未验证**。本包不是经济质量签收，也不是整个公司或主线的通过。

## 1. 这次修的是什么

三路审查（storage 13 / process 28 / analyst 28）的并集是 **49 个不同 claim**，旧角色为 31 个 `mechanism_direction` + 18 个 `conversion_assumption`。真正的问题不是"角色标签写错"，而是**引用选段与目标业务不匹配**，以及**预期/实绩/存量三种语义被压成一个 `reported_fact`**。

修复后的角色分布：`mechanism_direction` 26、`conversion_assumption` 21、`history_base` 2。**18 个化学/TIDES 价格 claim 原本就是正确的 `conversion_assumption`，本次全部保留**——这是反控，不是待修项。

### 1.1 引用错在哪

旧输入的摘录多数是**页首固定 650 字符切片**。以 H1 p12 为例：页首是 TIDES 服务客户数 + Testing 业务段，`（3）生物学业务` 在本页下半。9 条 Biology activity claim 和 `claim_driver_biology` 全都引用了页首切片，于是"生物学业务机制"的支撑文字里没有一个字是讲生物学的。

同类问题还有：3 条 Biology H2 rebase 引用了**年报 p14 的小分子 D&M 段**（与 Biology 无关）；`claim_driver_non_tides` 引用的是分部收入表表头（只支持历史，不支持未来机制）。

修复方式：从**已核验页文本**里取目标业务自己的连续段，重新计算偏移与 `excerpt_sha256`，记录物理页与页文本 SHA。Biology 用 p12 下半 285 字；non-TIDES 用 p11 化学段（因超过 500 字上限，按段落边界拆成 263 + 330 两段连续区间）；TIDES 用 p12 的客户/分子句；价格用 p16 的 Testing/Biology 毛利段。

### 1.2 预期不是实绩

年报 p184 同一段同时给出：FY2025 年末 RPO 存量 **5,800,478.75 万元**（时点事实）、其中 **4,220,706.46 万元预计 2026 年确认**（发行人预期）、以及**没有任何 2026 年实际兑现**。

旧输入把预期值写成 `reported_fact` / `history_base`。本次改为 `management_guidance` / `value_range` + `exact_value`，数值不变（42,207.0646 CNY million）。该参数**没有任何收入 DAG 消费**，所以纠正本身不改任何预测数字——这一点必须明说，不能把角色纠正包装成预测改善。

存量本身仍是时点事实，不能因为"未来年度"关键词就拒绝；反过来，预期也不能被当成全年硬下限，不能与 H1 实际或新订单相加，不能私自分给子业务。

### 1.3 两条无法修复、只能诚实弱化的机制

`claim_driver_other` 与 `claim_driver_discontinued` 的原文只有：一条历史收入下降行（3,904.68 vs 8,662.95 万元，-54.93%）和一条终止经营分类注（本期 0，上期 127,377.57 万元）。这两者都**不含任何前瞻经营机制**。

处置：重新绑定到各自真实存在的那一行，角色降为 `history_base`。收入加总、零收入和负贡献全部保留；native 增长驱动报告现在会明说这两个 driver **没有未来机制证据**。没有向 native enum 写入 `unknown_mechanism_no_role_fix`（那是准备包的诊断字符串，不是合法字段值），也没有为了凑覆盖数量造机制。

## 2. 最大驱动：non-TIDES 必须拆开看

六个互斥分区不变，TIDES 只在 Chemistry 内计一次。真正的问题是：集团净增量主要来自 non-TIDES，而旧 Base 用一个混合活动量指数同时覆盖小分子 D&M 和残余化学服务，掩盖了两者**披露节奏完全不同**。

独立复算（`research/component-bridge.json`，全部用 Decimal 从原生 pointer 与已核验页偏移重算，未复用准备脚本的 PASS 布尔值）：

| 量 | 值（CNY million / 比率） | 性质 |
|---|---:|---|
| FY2025 non-TIDES | 25,095.84688297 | 推导（Chemistry 精确 − TIDES 四舍五入） |
| FY2025 小分子 D&M | 19,920 | 披露（199.2 亿元，0.1 亿元舍入） |
| FY2025 残余 | 5,175.84688297 | 推导（差额） |
| H1 FY2026 D&M | 14,990 | 披露（149.9 亿元，+72.7%） |
| H1 FY2026 残余 | 2,735.95323039 | 推导 |
| H1 残余同比 | **+5.62%** | 推导（小残差，舍入放大） |
| H2 FY2026 non-TIDES（旧 Base） | 17,793.62636871753 | 旧 Base 条件路径 |
| 残余 H2 重复可比期时，D&M H2 隐含同比 | **+35.30%** | 条件推论 |
| FY2028 non-TIDES（旧 Base） | 46,008.51713785671 | 旧 Base 条件路径 |
| 残余保持 FY2025 时，D&M 需为 FY2025 的 | **2.05 倍** | 条件推论 |
| non-TIDES 占集团**净**增量 | **65.82%** | 推导 |
| 旧输出正向 driver 增量份额 | 61.57% | native（**不同分母**） |

关键读法：+35.30% 与 2.05x 是**在"残余重复可比期"这一条件下的分解恒等式**，不是对 D&M 的预测，也不是新 Base。残余假设 ±10% 时，隐含 D&M H2 同比在 +37.60% / +35.30% / +33.00% 之间移动，FY2028 倍数在 2.076 / 2.050 / 2.024 之间——这是条件算术，不是经验区间。

65.82% 与 61.57% 是两个不同分母（集团净增量 vs 正向 driver 增量），**不能混写**，也不能互相替换来制造更高集中度。

### 2.1 不能做的事

- 不能用项目数、客户数、分子数、反应釜体积乘虚构 ASP 或利用率得到收入。管线 +699 个分子、3,731 个在管项目、>4,000 kL 与 >100,000 L 都是存量/活动量，不是收入或吞吐。
- 不能把 p139 的履约进度/控制权确认、p186 的单客户 >10% 风险分配给未披露的子业务份额。
- 不能为贴近上调后的管理层指引反推 Base。本次保持所有活动量/价格/FX/持续性数值不变，重算结果与封存旧输出**逐位相同**（见 `research/native-chain.json`）。

## 3. 主/压力原生执行

主/压力各走真实 `validate → compute+render → snapshot create`，每次调用由 `execution_request.py build` 生成冻结请求，再由 `audit_run.py capture` 消费该冻结字节。六次调用全部 `child_started=true`、`exit_code=0`、`input_complete=true`、`output_complete=true`，且**冻结消费输入 SHA == builder request SHA**（main `770cd309…`，stress `c0c45687…`，逐 call 记录在 `research/native-chain.json`）。engine 侧 input 文档哈希：main `93ba13a5…`、stress `4c82c3c1…`，快照 `input_sha256` 与 forecast 一致。三情景 `segment_subtotal` 与封存旧输出逐位相同（含义界定见 §3"逐位相同的确切含义"）。

- 主：`w09-rf-research-20261023-main-v1`，快照 `snapshots/main-v1.json`
- 压力：`w09-rf-research-20261023-stress-v1`，快照 `snapshots/stress-v1.json`
- registry：`delivery/w09/registry/publications.jsonl`（6 条链式记录，`prev_line_sha256` 连续）

压力测试不是改文件名：它把**同一个**验收/资格扰动（9,000 CNY million 的 Q4 交付队列，50% 暴露跨财年、80% 于 FY2027Q1 追回、20% 取消）**只施加一次**到 TIDES（3,000）与 non-TIDES（6,000）两个互斥池，共用同一暴露率、边界指示、追回比例与 FX 链。结果：FY2026 −4,500，FY2027 +3,600，FY2028 0；与封存旧压力输出的三情景 subtotal 相同。

**"逐位相同"的确切含义**：三情景 `segment_subtotal` 与封存旧输出逐位相同；forecast JSON 的其余差异（confidence limitations 新增两条 no-future-mechanism、research_adequacy 从 0 条 typed observation 变为 66 条、若干 calibration reason 从 conversion_assumption_not_disclosed 变为 observed_range_unknown，共约 735 个叶子）全部是本次角色/观测修复的**预期效果**，见 `research/native-chain.json` 的 `sealed_comparison`。

## 4. 剩余未知与金额暴露

详见 `research/remaining-unknowns.json`。摘要：

| 未知 | 限制了哪条结论 | 金额暴露 |
|---|---|---:|
| H2/年度子业务拆分未披露 | +35.3% 与 2.05x 是否合理 | non-TIDES H2 17,793.63；FY2028 46,008.52 |
| 实现净价/组合未披露 | 0.97–1.00 价格指数数量级 | 价格指数每差 1pp ≈ FY2026 non-TIDES 178 |
| 利用率/良率/合格交付未披露 | 产能能否物理支撑 | FY2028 non-TIDES 46,008.52 |
| 取消率/队列兑现节奏未披露 | 80%/20% 追回-取消是条件 | RPO 预期 42,207.06；压力取消 900 |
| 单客户 >10% 无精确份额 | 最大驱动是否集中于单一关系 | >2,889.75（H1 集团 10%） |
| 无冻结历史预测、无同口径观测区间 | 不能称为经验校准 | FY2028 集团 77,228.86 |

**没有任何 ASP、利用率、取消率、队列节奏或经验区间被编造。**需要而不可得的量，要么是带反证的显式分析条件，要么列在上表中。

## 5. 方法写回与泛化

三张方法卡各补最小必要段落，并去重：

- `evidence-role-calibration.md`：页首切片为何不是自身范围支撑；预期/存量/实绩三分；反控不可"修"；诚实弱化优于造机制。
- `buy-side-methodology.md`：最大增量必须拆到可比组件（6 步检查）；未来不可观测量的诚实处理。
- `input-construction.md`：修复既有输入的四个前提与两个陷阱（500 字上限、诊断字符串不得写入 enum）。

泛化用一个**不同业务结构**的离线合成例检验（`research/generalization-probe.json`：订阅平台 + 项目服务 + 遗留一次性产品），含 1 个正例与 3 个反例（错业务切片、预期当实绩、残余当独立披露）。合成例明确标注 synthetic，不伪装实证，也不进入任何发布预测。

## 6. 明确未完成

- 未消费 W08 新摘要（本包 `actually_consumed=false`，`new_w08_consumed=false`），未导入中央 run，未做 W12 四路审查。
- 未获得同口径经验区间，`observed_range` 全部保持 null，所有校准 `unverified`。
- 置信分与旧版完全相同（24.01705900038857）——因为本次是引用/角色修复，不改变证据数量与模型结构。**分数不变本身就是"没有偷改数字"的证据之一**（注意：`confidence.limitations` 与 `research_adequacy` 内容有预期变化，见上文"逐位相同的确切含义"）。
- 本包通过不等于整个公司或主线通过。
