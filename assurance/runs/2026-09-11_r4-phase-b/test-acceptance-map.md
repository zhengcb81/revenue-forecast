# B 阶段测试与验收映射（test-acceptance-map）

> 测试 ID 全部取自 [R4 测试矩阵](../../../../company-wiki/docs/plans/painpoint-outcome-audit-2026-09-05/simplified-test-matrix.md)，**不新造 ID**。
> "层"指矩阵的真实性分层：D0 诊断 / R1 真实本地 / R2 真实外部 / R3 真实持续（handbook §4）。B 阶段只涉及 **D0 机制层 + R1 真实本地**。

## 1. B 步骤 → 测试 → 验收

| 步骤 | 必测 ID | 矩阵原文的关键验收点（逐字摘） | 本 run 设计对应 | 需要什么条件 |
|---|---|---|---|---|
| **B01** | L11（当前协议与**未知版本拒绝**；**N-1 未定义**）、L04（未知 adapter/deny/未注册） | **L04 原文**："合法第五根无需消费者代码改动；未知/deny 拒绝，不以平权绕过能力限制"；L11："支持兼容由单 adapter 转换且来源不变；未知拒绝，无 companies 静默 fallback，无第二权限语义" | [b-design §B01](b-design.md) 字段 owner 表（14 行）+ 旧字段映射 | D0 可测；R1 需隔离副本 |
| **B02** | **L01**、L02、L03、L04 | L01"四副本分别单独索引→query→open；再四副本同时存在，调换 priority"→"同 source 版本/业务投影/字节；非 companies 也可用；**零网络**/原文件修改"；L03"有合格副本自动切换且引用不变；全失效 unavailable，不取另修订、不自动下载" | 四段式候选选择（资格≠排序）；`service._annotate_locations` + `resolver._handle` 同改 | D0 可测；R1 需真实四 root |
| **B03** | **L05**、L06 | L05"只返回验证版本字节或明确失败，TOCTOU 不混读；越界零读/写，无 mtime 冒充 hash"；L06"明确原因与同版本副本选择；有限资源/可取消" | 句柄固定 + **读后复验** → 受控快照 → 五值失败；**预算与取消见 [b-design §B02/§B03](b-design.md)（B-DR2-11）** | D0 可测（注入替换/拒绝）；云场景**如实标限制** |
| **B04** | L03、**L07** | L07"原引用仍指原字节；新修订独立版本，不能只因 mtime/accession 词序决定新旧；未知关系 **ambiguous**" | 位置退出身份；搬家建新 location，引用链不断 | D0 可测；R1 需隔离副本内移动 |
| **B05** | **L08** | "业务事实不随位置改变；可信字段有来源，冲突保留而非按 priority 默选" | provenance + 冲突保留；**覆盖 `scanner.py:1007-1099` 全部写入点**（`:1009-1027` INSERT、`:1073-1077` `prefer_new`、`:1078-1081` UPDATE、`:1095-1099` 重扫）并按 §B05 的逐列合并规则断言；**另加 `json_extract` 回归**（fiscal_year 过滤 + prompt_injection_review 门）与"先缺后补"分支 | D0 可测（交换 priority/扫描顺序） |
| **B06** | **L09**、L10 | L09"preview 可读并标 provenance 缺口；正式合同缺身份/期间则不通过；不伪造 URL、不默认联网"；L10"只检查所需能力；原文不因无 summary 消失；LLM/正式分析不能继承 preview 许可" | preview vs verified_input 资格标签（**不含** VR-N21：R-4 属独立工作包，S-2） | D0 可测；R1 需真实本地 PDF |
| **B07** | **L11**、L12 | L11 原文见上；L12"查询零写/联网/worker 控制；不以 ensure 填缺。原文读取可产生实际读 I/O，不能声称零成本；二次 0parser/LLM/download 由独立观察证明" | 版本化读取合同（**wiki 侧**）+ payload hash 不变；**消费者侧 adapter/fallback 不在 B 签名内（归 C，见 [b-design §B07](b-design.md) 范围表）**；L12 的"二次 0 parser"必须观察 `normalizer.py:516` 的 multiprocessing spawn（A-VR-09） | D0 可测；L12 独立观察需 B08 |
| **B08** | L01–L12 全量 + 必要旧 C01–C10 | "不用人工构造 catalog 结果冒充真实 parser/索引；特殊 cloud 无法测标限制" | B.VR 在**新隔离环境**重跑 | **需隔离副本（G8）** |
| **B09** | 真实四 root + 第五 root 端到端 | "独立 AR 从原文重新核身份与 hash；仅隔离副本变化，不改用户原文件" | B.AR 最小读取 | **需 G8 + G7** |
| **B10** | 切换与回退 | "变更独立审查后才切换；回退代码/配置不回滚原始数据和历史来源证据。无法兼容则停切换，不永久默默双跑" | 单一读取链 + 显式版本 adapter | **前序门通过后** |

> **新增断言的落点（v0.1.3，B-DR3-04）**：本表新增/收紧的断言（显式 `false`、L08 逐列合并 + **json_extract 回归**、`B-payload-hash`、`B-ratchet`、B02 预算与取消）全部落在 **file-scope F10 的新增测试文件**里；**S-1 已批准 F10**（owner 2026-09-12），故这些断言有落笔处；限制仍是：仅新增文件，不改既有断言。

### 1c. 附加必测项（v0.1.2 补，B-DR2-12）

| 测试 ID | 内容 | 依据 | 通过判据 |
|---|---|---|---|
| **`B-coverage`**（本包登记，v0.1.6 补，B-DR6-07） | `FC1204_COVERAGE_GATE=1 pytest tests/contract/test_fc1204_coverage_ratchet.py -q` 必须通过（**TIER1 `policy.py`/`service.py` = 95、TIER2 `resolver.py` = 86**） | [b-design §B0x](b-design.md) | 通过；B05 改 `service.py`、B02 改 `resolver.py` 均影响该门 |
| **`B-ratchet`**（本包登记） | 实施后 `pytest tests/contract/test_fc1204_complexity_ratchet.py -q` 必须通过（**`NEW_FILE_MAX = 10`**） | [b-design §B0x](b-design.md)（`config.py` 46/46、`scanner.py` 140/140、`policy.py` 5/5 顶格） | 通过；若需新增判定点则停止并走 S-7 |
| **`B-payload-hash`**（本包新登记，非矩阵 ID） | `resolve` 输出的 **policy_export payload 的字节/hash 不变** | A 合同明文要求：`operation-contract.md` §2.3 第 2 条"**resolve 是只读但产生对外契约产物**；B02/B04 改动 resolve 时必须保持该 payload 的字节/hash 契约"，且该 payload 是 filing-fetch FC-501 containment 的唯一来源（`filing_contracts.py:450/461-497`） | 改动前后对同一配置重算 `policy_hash` 与 payload 字节，**必须逐字节相同**；不同即**阻断合入**（除非同时提交跨仓迁移）。⚠️ **v0.1.6（B-DR5-04）：当前不可执行** —— 包内**没有该 payload 的冻结基线**，且取值需要 `--help` 之外的 CLI（属 [command-manifest-readonly.json](../2026-09-11_r4-phase-a/command-manifest-readonly.json) 的**待批**范围）。因此 S-3 的验证手段**在实施前必须先在隔离副本上冻结基线**；在此之前它只登记不判过。 |

> 说明：矩阵没有"payload 字节契约"这一 ID，但 A 合同把它列为 **B02/B04 的必测项**；按"不新造矩阵 ID"的纪律，本项以 **`B-payload-hash`** 之名登记在**本包**（不进矩阵），并在 B.DR/B.VR 的检查表里逐次引用。

### 1b. owner 裁定项的测试绑定（v0.1.1 补，B-DR-15）

v0.1 未把改判项绑定到测试 ID，现补齐：

| 裁定 | 绑定测试 | 说明 |
|---|---|---|
| **R-2**（显式 `false` 生效；**三处实现对齐语义**，第三处在在产导出路径内不可删） | **L01**（调换 priority 不改业务投影）+ **L08**（业务事实不随位置改变）+ L04（deny 不被平权绕过） | 对齐后必须同时满足"`false` 关闭复用"与"policy_hash 迁移同步" |
| ~~**R-4**（默认不外发 + 无门出口）~~ | **不属于 B**（S-2 已裁定；[b-design §B01.3](b-design.md)）。**B 不产出"合成 `privacy_class` 配置"断言，也不做 VR-N21**（B-DR4-02）——它们归 owner 的独立整改工作包与 A07 | — |
| ~~**R-1**（`symlink_policy`/`read_only` 处置）~~ | **v0.1.3 移出：处置不属于 B**；但 B 的 **L05/L04** 仍需覆盖 symlink 逃逸与 deny 的**读取行为**（B 侧）。注：本机 symlink 测试因宿主不支持而 **skip**（A06 基线），须在支持 symlink 的环境验证 | — |
| **R-6**（路径不入身份投影） | **L03**（撤首选自动切换、引用不变）+ **L07**（搬家后旧引用仍解引用） | 与 B02/B04 同一批验收 |

## 2. 反向覆盖检查（矩阵 → B，确保没有遗漏）

| 矩阵 ID | 归属阶段 | B 是否覆盖 | 说明 |
|---|---|---|---|
| L01–L04、L07–L09、L11 | 按矩阵逐行：L01 A/B、L02 B、L03 B、L04 B、L07 B、L08 B、L09 A/B、L11 B/C（v0.1.2 逐行照抄，B-DR2-04） | ✅ | 见上表 |
| `L05`、`L06` | **L05 = B/C；L06 = B**（矩阵原文 `:32`/`:33`） | ✅ | B03 覆盖两者；L05 的 C 部分（消费者侧重复 hash）归 C |
| `L06`（反覆盖表） | **= B**（矩阵 `:33` 原文即 `L06 B`；本表统一为 **B**） | ✅ | — |
| `L10`、`L12` | **L10 = A/B/C；L12 = A/B/C**（矩阵原文 `:37`/`:39`） | ✅（B 的部分） | preview 许可不继承、查询零写在 B06/B07 验收 |
| P01–P03 | **矩阵 `:88` 原文**："L01–L12、P01/P02/P03 只读部分 … **B 和 C 本地栏**对真实原文与既有 root 覆盖独立核验；不要求网络/worker" | ⚠️ 部分 | 进程边界与字节合同在 C；B 只保证"不多起 Python/不套壳"的设计约束 |
| P04–P08 | C | ❌ 不属 B | 队列/真实外发/删锁属 C 与 D.SAFE |
| **O03** | D | ⚠️ **交叉**（v0.1.1 更正，B-DR-20）：O03 的"位置变化不能洗掉安全拒绝"**直接约束 B02/B04 的候选资格段**，因此 **B 必须实现该约束**（拒绝不因换 root 而放行），只是**不执行 O03 的完整验收**（那属 D） | 设计已写死 → 见 [b-design §B02](b-design.md) 第 2 段与 [risk-and-stop-rules.md](risk-and-stop-rules.md) §2 |
| O01–O02、O04–O08 | D | ❌ 不属 B | |
| M01–M08 | M | ❌ 不属 B | 收入模型与 broker 解析 |

> **v0.1.1 更正（B-DR-20）**：v0.1 把 O03 标为"❌ 不属 B"却在风险文件里承认"直接交叉"，自相矛盾；上表改为"⚠️ 交叉：实现约束属于 B，完整验收属于 D"。另：**阶段列一律以矩阵原文为准**——本表 v0.1.6 复核后的取值：**L06 = B**、**L11 = B/C**、L05 = B/C、L10/L12 = A/B/C（v0.1.1 那次更正把 L06 误写为 B/C，现更正；见 F-B01-6）

## 3. 每个 B 步骤的"完成"定义（防"勾成完成"）

一个 B 步骤只有在**同时**满足下列四项时才可标 `completed`：
1. 设计的**允许文件**内改动完成，且 diff 只在批准范围内（越界即停）；
2. 该步骤的**必测 ID 全部真跑**（禁 skip/unknown/rc0 空输出），且结果**原始 stdout/rc/时间**入证据；
3. **独立复审**（B.DR 或 B.VR）就同一输入 hash 出具 verdict；
4. checkpoint 记录 `last_completed_step`、`pending_review`、`actual side effects`、`failed/unknown`、`next_step`。

**明确不算完成**：设计文档写完、测试通过但跳过故障例、只跑 D0 却宣称 R1、用人工构造 catalog 结果代替真实 parser/索引、把"preview 可读"当"正式输入可用"。
