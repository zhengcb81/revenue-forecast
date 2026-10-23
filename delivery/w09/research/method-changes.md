# W09 方法卡改动记录

三张卡的最小必要改动。原则：只写通用研究判据，不写本公司规则；不新增第四套方法、不加新门禁、不改任何验证器。

## `references/evidence-role-calibration.md`

| 改动 | 内容 | 为什么是通用问题 |
|---|---|---|
| 新增小节 "Where the page slice comes from, and why a page prefix is not own-scope support" | 页首固定切片是检索产物，不是摘录；必须定位命名目标业务的小节，取含主体/期间/机制/最近限定语的连续区间；超长按段落边界拆，不得截断或整页兜底 | 任何"按页取前 N 字符"的作者化流程都会产生同样的错范围引用，与行业、语言无关 |
| 新增小节 "Expected future recognition is not an actual, and an actual is not a floor" | 同一段可能同时含存量/发行人预期/无实绩；预期=management_guidance，存量=时点事实；预期不得与 H1 实际或新订单相加、不得私分子业务；不得用"未来年度"关键词一刀切 | RPO、合同负债、订阅 renewal、订单 backlog 都适用 |
| 新增小节 "Role changes must survive a negative control" | 三路审查集合中本来就有正确条目；修复前先列"角色不得变"的清单并断言前后计数；跨范围价格是合法的 conversion_assumption，前提是写明跨业务转移 | 防止"修一个错、造一个错"，任何多来源审查集合都会遇到 |
| 新增小节 "Honest weakening beats a fabricated mechanism" | 无前瞻机制时降为 history_base/counterevidence，保留零/负贡献，让 driver 报告自述无机制；不写诊断字符串进 enum，不凑配额 | 历史下降行、终止经营注、零收入范围在任何公司都会出现 |

未改：角色枚举、support_type 约束、校准投影规则、置信权重。原有段落未删改，只在末尾追加并去重（"Role counterexamples" 表保持原样）。

## `references/buy-side-methodology.md`

| 改动 | 内容 | 为什么是通用问题 |
|---|---|---|
| 新增 §10 "最大增量必须能拆到可比组件" | 6 步：互斥分区 → 只用已识别数量 → 条件推论写成条件 → 敏感性写成算术 → 三个分母不混用 → 反证必须改变东西；点名"用管理层指引反推 Base"这一失败模式 | 任何"一个大分部贡献大部分增量"的公司都适用，不限于 CDMO |
| 新增 §11 "未来不可观测量的诚实处理" | 条件预测可以有非空值；null 不是谨慎的同义词；每个未知量登记限制的结论与金额暴露；无同口径区间则 observed_range 保持 null；执行完整性≠经济认证 | 通用买方研究标准 |

未改：§1–§9 原文；未新增字段、未新增门禁、未把任何公司/分部名称变成规则。

## `references/input-construction.md`

| 改动 | 内容 | 为什么是通用问题 |
|---|---|---|
| 新增 "Repairing an existing authored input (citation / role / kind)" | 四个前提：不覆盖封存记录 + 新旧 SHA 并列；每条改动摘录从页字节重算偏移与哈希；修角色时保持算术不变并要求情景总额逐位相同；语义变了才改 kind 并声明是否有 DAG 消费 | 任何"复制封存输入再修"的流程都需要这四条，否则修复会悄悄变成重预测 |
| 同节 "Two traps" | 500 字摘录上限（按段落边界拆，不截断）；诊断字符串（如 `unknown_mechanism_no_role_fix`）不是 enum 成员，不得写入 | 原生 schema 限制，与公司无关 |
| 同节 "Minimal repair ledger" | 每条改动记录 10 个字段；未改动条目也要记录"已核验不变"及理由；行数必须等于审查集合基数 | 账本只列改动无法证明没漏项 |

未改：命名约定表、enum 速查、哈希环说明、构建脚本骨架、各 schema 版本小节。

## 没有做的事

- 没有修改 `scripts/` 下任何产品代码：本次未观察到需要 RED 证明的通用确定性 bug（500 字上限与 enum 约束都是既有正确契约，被违反的是作者输入，不是验证器）。
- 没有新增审批层、canary、签收文件或第二计算引擎。
- 没有把 D&M、公司名或任何中文标题词写进代码或方法规则；泛化用 `research/generalization-probe.json` 的合成例（订阅平台 + 项目服务）检验。
