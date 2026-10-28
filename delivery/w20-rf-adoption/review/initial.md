# W20 独立初审报告（S1+S2，2026-10-28）

审查对象：`git diff 0991e25d..5f88ac3f`（A=`c71b79e2`，B=`65af44b9`）。两个互相独立的审查 agent 并行执行：S1=需求符合度/架构/边界语义，S2=测试真实性/错误路径/清理/断言强度。以下为两报告合并（原文由各 agent 产出，作者未改写实质内容）。

## S1：需求符合度 / 架构 / 边界语义

### 发现清单

**[P0] F1：/4 阅读能力位（`reading_support_use`）被错误聚合——异常回执可把 context_only 来源 span 判成 `used`，且要求的 `context_span_bound_as_support` 诊断不发出**
- 位置：`tools/narrative_adoption_audit/audit.py:546-578`（`_span_support_use`），消费点 `audit.py:765-789`。
- 问题：冻结基线 `0991e25d` 的合同语义是：视图级 `reading_support_use` 限定其 `support_evidence_ids` 的能力，只有 `== "support"` 的视图才授予独立事实支撑。`_span_support_use` 只特判 `"unresolved"`，`"context_only"` 标记的视图落入 `else: saw_support = True` 分支。实测探针（真实 DU11 链 + 真实 `consume_narrative_input` 回执，仅把 reading 升级为 /4 并将该 span 所在视图标为 `context_only`）：span 状态 = `used`，`context_span_bound_as_support` 未发出。/4 下未分组 span 按读者合同是 `unresolved`（不可支撑），审计返回 `None` → `not_observed`。
- 期望：该 span 应为 `not_used_when_provable`（context/unresolved partition 不可支撑族），有回执绑定时必须发 `context_span_bound_as_support` 且不得判 `used`。

**[P0] F2：elimination 约束参数不在 wired 闭包内——合法输入被出具虚假的 `not_used_when_provable` 结构证明**
- 位置：`audit.py:388-402`（约束家族只索引 `scenario_parameter_ids`/`weight_parameter_ids`，漏掉 `segment_adjustment_parameter_ids`）。
- 问题：`scripts/forecast/dependencies.py:128-131` 对 `type=="elimination"` 读取 `segment_adjustment_parameter_ids`（segment → {scenario: [ids]}）。实测探针：引擎 `parameter_formula_refs` 对该参数返回 3 条 refs，审计 `wired_parameter_ids` 不含 → claim/span 均被判 `not_used_when_provable`，与同 run intact 回执判定自相矛盾。

**[P2] F3：回执缺 `formula_refs` 时静默跳过 run 比对**，宽松政策未"记录未知"（`audit.py:496`）。
**[P2] F4：必要测试包未覆盖 /4 能力位**（无 `reading_support_use` 构造）——F1 逃逸的原因。
**[P3] F5**：`KNOWN_CONSUMPTION_FIELDS` 与真实 /3 回执不匹配（缺 `subject_ref`/`parent_count`/`lineage_sha256`）→ 多余 info 噪音。
**[P3] F6**：/3 projected context 的 span 条目丢失 `source_sha256`（`context.get("source_ref")` 对 /3 为 null）。
**[P3] F7**：`resource.items_capped` 恒为 False（死字段）。
**[P3] F8**：度数二次的成员扫描（受节点度数约束，n/2n 实测 1.31s→2.43s 近线性，满足卡的"线性或可说明"）。
**[P3] F9**：`used` 节点家族略宽于 A2 冻结列举（R3 允许"与现有等价状态"，README 已披露）。

### R1-R6 逐项结论

| 要求 | 结论 |
|---|---|
| R1 输入显式/只写显式输出/无扫描联网DB模型 | 满足 |
| R2 canonical ID/display key/support区分/hash政策 | 部分满足（F1） |
| R3 四状态族/actual IDs/named reason/报告定位 | 部分满足（F2） |
| R4 不猜用/不测心/不强制采用/失败与缺观察分开 | 满足 |
| R5 只核绑定口径/不另算收入/不LLM/不rating | 满足 |
| R6 无新DB调度权限/版本化report/资源界/线性 | 满足 |
| 架构（纯核心/CLI分层/复用既有纯接口） | 基本满足（唯一重造点 `_span_support_use` 与既有语义分叉=F1 根因） |
| allowlist | 满足（diff 恰为 allowlist 内 10 文件） |

### S1 测试执行

`python -B -m pytest -q --tb=short -p no:cacheprovider tests/test_w20_narrative_adoption_audit.py tests/test_w20_narrative_adoption_e2e.py` → 17 passed（7.51s）。

**S1 OPEN_findings = [F1, F2]**（F3/F4 应随同修复，F5-F9 备注不阻塞）。

## S2：测试真实性 / 错误路径 / 清理 / 断言强度

### 发现清单

**[P1] n/2n 测试的时长比例断言在本机永不执行**（`t1=0.022s < 0.05` 阈值；实测比例 1.86 远小于上限 4）。计数 2x 与 resource_limit 真触发是实的。
**[P1] BIREN_INPUT"fixture untouched"断言恒真**（`assert BIREN_INPUT.read_bytes()`）；无写入路径，缓解存在但应字节级对比。
**[P1] CLI 失败分支缺测试**：文件缺失、坏JSON、非对象JSON、`--max-input-bytes` 超界（覆盖拒绝/输入=输出/资源界 core 层已测）。
**[P1] `narrative_wire_refused` 全链路零测试**（CLI 捕获→refusals→诊断→继续 exit 0 的优雅降级分支）。
**[P1] `receipt_run_mismatch`（跨run拼接检测）零测试**（实现经直接探针验证行为正确）。
**[P2] offline_guard 不覆盖子进程**（四个被调入口 grep 零网络代码；建议文档声明）。
**[P2] `resource.items_capped` 死字段+对应断言恒真**。
**[P2] 其余已命名诊断无直接测试**（`duplicate_capture_sha`/`span_material_not_provided`/`span_bound_multiple_receipts`/`consumption_source_ambiguous`/`consumption_not_consumed`/`consumption_material_missing`/`input_document_binding_mismatch`/`embedded_input_absent`——抽查实现行为均正确）。
**[P3] RED-first 无法从 git 历史确认**（同 commit 引入；作者 progress.md 已记录 ModuleNotFoundError RED 证据）。
**[P3] 良性弱断言**：e2e:346 恒真断言（status 已先行断言）；unit:271 构造性恒真；`--pretty` 写路径未测试且非独占创建。

### 测试真实性结论（最重要项）

- **e2e 是真端到端**：真实子进程调用 4 个不同入口（consume 工具、revenue_forecast×2、revenue_backtest、audit CLI×5），断言真实 returncode 与真实产物内容，零 mock 调用计数断言。唯 CWP reader 传输在进程边界 stub（DU11 既定模式，模块 docstring 如实声明）。
- **无越界**：无 LLM/下载/provider；registry 钉进 owned tmp；fixtures 只读。
- **11 项卡内必测全部存在**（清单逐项核对表见原报告，第10项部分弱=时长比例）。
- **清理与恢复**：owned fixture 规范（sentinel+基线+逐项断言+只读属性处理）；三次运行前后 git status 均空，零残留。

### S2 测试执行

全套 17 passed（17.81s）；e2e 背靠背两次独立运行 2 passed / 2 passed；`--tb=long` 抽测 2 单测通过。

**S2 OPEN_findings = [n/2n时长比例断言永不执行, BIREN_INPUT未变断言恒真, CLI失败分支缺测试, narrative_wire_refused全链路零测试, receipt_run_mismatch零测试]**

## 合并处置

全部发现均在本卡范围内。修复承诺：F1/F2（P0）+F3/F4+F5/F6/F7（P2/P3 顺带）+S2 五项 P1+两项 P2（pretty 独占创建、offline_guard 文档声明）。修复后由新的独立 agent 复审最终实现。
