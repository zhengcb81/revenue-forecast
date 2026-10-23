# W09-RF-RESEARCH 交接

状态：**COMPLETE（含外部资料外限）**。包内完成；这不构成整个公司或主线的通过，也不构成经济质量认证。

## 1. 标识

| 项 | 值 |
|---|---|
| package_id | W09-RF-RESEARCH |
| 代码 base | `10bf611166013bd68ce14bfa19bb70e89a92dd5b`（卡冻结值；无产品代码改动） |
| start HEAD | `42393ea1ca75dc28e751308246dbf856180882bd`（开工文档提交，非代码偏离） |
| 实施 commit | `4fdaa86b`（references 3 张方法卡 + delivery/w09 + 专属 PWF） |
| handoff commit | 见 handoff.json `final_head`（本提交） |
| 分支 | `codex/r1-w09-research-20261023` |
| 工区 | `C:/Users/郑曾波/Projects/revenue-forecast-r1-research` |

## 2. 需求 → 状态 → 证据

| # | 卡要求 | 状态 | 证据（路径 / locator） |
|---|---|---|---|
| R1 | 49 并集逐条真角色与 target（T09-target-scope-role） | PASS | `research/claim-changes.json`：49 行无重复；old 31+18 → new 26/21/2；`price_negative_control` 18/18 保留；`out_of_union_repairs`（9 Testing）与 `out_of_union_requirement_repairs`（RPO）明确不计入 49 |
| R2 | 31 机制条用自身业务段；18 价格条保留 conversion（反控） | PASS | `research/excerpts.json`（22 模板，全部从页字节重切、双哈希、自检断言）+ `claim-changes.json` 每行 `contiguous_span`/`contiguous_range_sha256` |
| R3 | RPO 预期→management_guidance，不进收入 DAG，不改数值 | PASS | `claim-changes.json` `rpo_correction`：kind corrected、值 42207.0646 不变、`revenue_dag_consumers: []`；两轮审查独立确认 0 DAG 消费 |
| R4 | 其他/退出不用同一正向链，如实弱化 | PASS | `claim_driver_other`/`claim_driver_discontinued` → history_base；native 输出新增 "no future-mechanism evidence" 限制；零/负贡献保留在收入加总中 |
| R5 | 最大驱动经营桥（T09-largest-driver-bridge） | PASS | `research/component-bridge.json`：独立 Decimal 重算 19 项；+72.7% vs +5.62% 双节奏；条件隐含 +35.30% H2 / 2.05x FY2028；65.82%（净增量分母）与 61.57%（native 正向分母）分开 |
| R6 | 敏感性与反证 | PASS | `research/sensitivity.json`：native 7 项敏感 + 残余 ±10% 条件算术（+33.0%/+35.3%/+37.6%）+ 压力事件（FY2026 −4500 / FY2027 +3600 / FY2028 0）；每个 falsifier 带可观察触发 |
| R7 | 主/压力原生 validate/compute/render/snapshot 真实执行 | PASS | `research/native-chain.json` + `recorder/`：6 次调用全 clean，冻结 SHA==request SHA；快照与 forecast `input_sha256` 一致 |
| R8 | 修复不改变预测数字（引用/角色修复而非重预测） | PASS | 三情景 `segment_subtotal` 与封存输出逐位相同（§"逐位相同的确切含义"见 memo §3）；置信分不变 |
| R9 | 未知保留，不编造 | PASS | `research/remaining-unknowns.json` 8 项，每项含限制的结论与金额暴露；`observed_range` 全 null、12 校准全 `unverified`；无 ASP/利用率/取消率/队列编造 |
| R10 | 经验写回三张方法卡，通用化 | PASS | `references/{buy-side-methodology,evidence-role-calibration,input-construction}.md` 各补最小必要段落（`research/method-changes.md` 逐条记录）；泛化例 `research/generalization-probe.json` 用订阅平台+项目服务结构，1 正例 3 反例 |
| R11 | 独立审查 + 修复 + 复审 | PASS | 第一轮 FAIL（`review/independent-review.{md,json}`，2 MAJOR）→ `review/review-fixes.md` 全修复 + 全链重建 → 第二轮 PASS_WITH_MINOR（`review/final-independent-review.{md,json}`，6/6 VERIFIED）；3 条尾项已收尾 |
| R12 | 临时目录恢复、不复制原件 | PASS | `cleanup/receipt.json`：`restored=true`；0 raw PDF 复制；交付 22.91 MiB < 32 MiB |

## 3. 外部资料外限（不是缺陷，不可被"通过"掩盖）

- **无 H2/年度子业务拆分**：D&M 与残余的期间拆分未披露，+35.30% 与 2.05x 只能是条件推论。
- **无实现净价/组合序列**：18 条价格 claim 只能停留在跨业务间接 conversion_assumption。
- **无利用率/良率/合格交付**：>4,000kL、>100,000L 是存量，不能转吞吐。
- **无取消率/队列兑现节奏**：压力测试的 80%/20% 是条件；RPO 预期无实际兑现可对账。
- **无经验校准**：`observed_range` 全 null，`unverified` 是真实状态。**本包交付的是内部研究改进，不是校准通过。**

## 4. 明确未完成（ROOT 责任）

- W08 新摘要未发布、未被本包消费（`consumed-inputs.json` `actually_consumed=false`、`new_w08_consumed=false`，版本为 old_paid_w07）。
- 未导入中央 run；W12 四路审查未跑；主线未合并、未 push、未安装同步。
- 新公司泛化与母 PWF 主状态由 ROOT 处理。

## 5. 尾注

- 交付中 `review/_probe*/` 的空白字符是两轮审查 agent 的原始输出凭据，**按字节原样保留**（`git diff --check` 对这些文件的告警是有意的）。
- `unknown_mechanism_no_role_fix` 是准备包诊断字符串，未写入任何 native enum（两轮审查均验证 0 次出现）。
- 详细交接 JSON（含全部 artifact SHA、native call 明细、测试与清理清单）见 [handoff.json](handoff.json)。
