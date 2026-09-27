# A06 基线计划（L01–L12 本地测试 + 小型只读 trace/profile）—— 待批

> 依据：执行计划 §A06「冻结 L01–L12 等本地测试及接口错误状态；生成基线小型只读 trace 和 profile，**禁止整库重复扫描**」→ 交付"每例基线结果"。
> 现状：**A06 未执行**。本文件给出执行方案、隔离方式、以及**现有测试资产盘点**（实测文件名），不含任何测试结果。

## 1. 现有测试资产盘点（实测，wiki `tests/`）

与 B 阶段 L01–L12 直接相关的既有测试文件（**只列名，未运行**）：

| 关注点 | 既有测试文件 |
|---|---|
| resolver / canonical 选择 | `tests/contract/test_source_catalog_resolver.py`（23.5 KB）、`test_resolver_normalized.py`、`test_resolver_shadow_gate.py`、`test_resolver_activation_snapshot.py` |
| 位置切换 | `tests/contract/test_location_switch.py` |
| 去重 / 语义重复 | `test_source_catalog_duplicate_cleanup.py`、`test_source_catalog_semantic_duplicates.py`、`test_zr403_dedupe_resolver_generalization.py` |
| 只读 reader | `tests/unit/test_catalog_reader.py`、`tests/unit/test_catalog_reader_queries.py`、`tests/contract/test_readonly_canary.py`、`test_zr1002_reader_first.py`、`test_zr203_reader_rewire.py` |
| root 准入 / 第五根 | `test_root_policy_2x.py`、`test_root_policy_v2.py`、`test_future_root_config_only.py`、`test_admission_profile.py`、`test_dropbox_root_policy_fc501.py`、`test_source_catalog_focus_admission.py` |
| 身份/元数据绑定 | `test_source_catalog_identity_resolver.py`、`test_fc906a_producer_binding_metadata.py`、`test_zr501_broker_metadata_contract.py` |
| 只读 ensure 语义 | `test_zr407_ensure_readonly.py` |

**结论（待 A06 执行时确认）**：L01–L12 的**机制层**大概率已被上述测试部分覆盖，但矩阵要求的**真实本地层（R1）逐例基线**没有对应产物；A06 的任务是"**冻结**每例的基线结果 + 明确哪些是"已正确 → 记保留回归"，**不要求所有 case 都红**"（执行计划 §A06 原文）。

## 2. 执行方案（待批准后按此执行）

| 阶段 | 动作 | 输出 | 约束 |
|---|---|---|---|
| A06-a | 对每个 L01–L12 **指明**映射到的既有测试（若有）与**缺口**（无覆盖则标 `no-test-yet`） | `baseline/l-map.json` | 只读仓库，不运行产品代码 |
| A06-b | 在**新建的隔离 catalog** 上跑机制层用例（用仓库既有测试的 tmp-catalog 机制，**不碰生产库**） | `baseline/D0/*.json`（每例 rc/stdout 摘要/耗时） | 隔离；**禁止**指向 `company-wiki/.source_catalog` |
| A06-c | 用 A05 的真实样本做**小型只读 trace**：`query → open`（各 ≤ 10 次），记录每步的真实读 I/O 与耗时，**不做全库扫描** | `baseline/R1/trace.json` + profile | 生产库**只读**（需 [command-manifest-readonly.json](command-manifest-readonly.json) 批准）；`open` 的字节读必须在隔离副本上做 |
| A06-d | 冻结"基线结果"文件（每例：期望 / 实测 / 是否已正确 / 需要的独立复审） | `baseline/baseline.json` | 不允许把 skip/unknown/空输出记为通过 |

## 3. 与 B 的关系（为什么先做 A06 再实施 B）

- B02–B07 的每一次改动都要与 **A06 冻结的基线**比较（"基线已正确者记保留回归"）；
- 没有 A06，"B 改好了"无法被独立验证——这正是执行计划把 A06 排在 B 之前的原因；
- B08 要求独立 VR **重跑 L01–L12**：其"基线"就是 A06 的产物，二者必须是同一批用例与同一隔离方式。

## 4. 阻断与依赖

| 依赖 | 状态 |
|---|---|
| 只读数据命令 manifest（A05/A06 用） | **待 owner 批准**（[command-manifest-readonly.json](command-manifest-readonly.json)） |
| 隔离副本（机制层与 open 字节读） | **待建**（门 G8）：可以是"新目录 + 既有测试的 tmp-catalog 机制"，**不需要**复制 49.7 GB 生产库 |
| A05 真实样本清单 | 依赖上一条，**待 owner 逐项确认**（门 G7） |
| 独立 reviewer（A07/A08 与 B.VR） | 已在 stage A 建立流程；A07/A08 可立即基于现有合同启动 |
