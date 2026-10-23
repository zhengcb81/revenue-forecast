# W09-RF-RESEARCH 进度

## 2026-10-23 ROOT交包准备

已创建独立稀疏工区、核实branch/base且实际检出，写START_HERE与本独立PWF。此前no-checkout工区仅有.git的问题已在派发前修正，初始产品代码无改动。施工本身尚未开始；A/B/C均pending。无需等ROOT逐小步签收。

最终必须调用独立agent审查，修复及复审后按固定handoff接口交ROOT，不能把开工包已准备当任务完成。

## 2026-10-23 A 大节点：冻结与独立基准

- 核实工区：`revenue-forecast-r1-research`，分支 `codex/r1-w09-research-20261023`，start HEAD `42393ea1`，代码 base `10bf6111`，起始 `git status --short` 为空。
- `delivery/w09/inputs/readonly-inputs.json`：29 项只读输入，真实绝对路径 + SHA-256 + 字节数 + 用途；卡上给出预期 SHA 的 18 项全部一致，`mismatch_logical_names: []`。
- 环境：`C:/Miniconda/python.exe` 3.13.9，RF engine 4.3.0 / schema 3.10，`manifest_sha256=ce8325f496badf75`；recorder 两个脚本 SHA 已记入 `inputs/consumed-inputs.json`。
- 先存 `--help`：`revenue_forecast.py`、`revenue_backtest.py create`、`audit_run.py`（init/capture）、`execution_request.py build`、`lint_input.py`、`fix_hashes.py`。
- 预写判据 `research/acceptance-checkpoints.json` 在任何新数字之前落盘。
- 独立组件桥 `research/component-bridge.json`：全部 Decimal 重算，未采信准备包 PASS 布尔值。

## 2026-10-23 B 大节点：修复与原生执行

### 引用重绑

发现旧输入的核心缺陷是**页首固定切片**：H1 p12 页首是 TIDES 服务客户数 + Testing 段，而 9 条 Biology activity claim 与 `claim_driver_biology` 都引用了它。同类还有 3 条 Biology H2 rebase 引用了年报 p14 的 D&M 段、`claim_driver_non_tides` 引用了分部收入表表头。

修复：从已核验页字节取目标业务自己的连续段，重算偏移与两种哈希（raw 与 stripped），记录物理页与页文本 SHA。p11 化学段 593 字超过 500 上限，按段落边界拆成 263 + 330 两段连续区间。

### 角色

31 mechanism → 26 mechanism + 2 history_base + 3 conversion（Biology rebase）；18 conversion → 21 conversion。**18 条价格 claim 原本就是 conversion_assumption，全部保留**，并补写跨业务间接风险的范围说明。

`claim_driver_other` / `claim_driver_discontinued` 只有历史下降行与终止分类注，降为 `history_base`；零/负贡献保留，native 报告现在明说这两个 driver 无未来机制证据。未向 enum 写入 `unknown_mechanism_no_role_fix`。

### RPO

`rpo_expected_2026_opening_cohort`：`reported_fact`→`management_guidance`，`history_base`→`value_range`，数值 42,207.0646 不变，无收入 DAG 消费。FY2025 年末 RPO 存量仍是时点事实。

### 经营桥

non-TIDES = D&M + 残余，六分区互斥、TIDES 只计一次。H1 D&M +72.7% 对残余 +5.62%；残余 H2 重复可比期时 D&M H2 隐含 +35.30%；残余保持 FY25 时 FY2028 D&M 需 2.05 倍；non-TIDES 占集团**净**增量 65.82%，与 native 正向 driver 份额 61.57% 分母不同、分别标注。

### 原生链

主/压力各 validate→compute/render→snapshot，6 次调用全部 exit 0、`child_started`/`input_complete`/`output_complete` 全 true、冻结消费 SHA == builder request SHA。registry 6 条链式记录。输出与封存旧输出**逐位相同**（三情景 segment_subtotal），证明本次是引用/角色修复而非重预测。

压力测试非改文件名：同一验收扰动（9,000 CNYm Q4 队列、50% 暴露、80% 追回、20% 取消）只施加一次到 TIDES(3,000) 与 non-TIDES(6,000) 两个互斥池。结果 FY2026 −4,500 / FY2027 +3,600 / FY2028 0，与封存旧压力逐位相同。

### 方法卡与泛化

三张卡各补通用段落（页首切片不是自身范围；预期/存量/实绩三分；反控不可"修"；诚实弱化优于造机制；最大增量必须拆到可比组件；修复既有输入的四个前提与两个陷阱）。泛化用不同业务结构（订阅平台+项目服务）离线合成例，含 1 正例 3 反例。

## 2026-10-23 自查发现并修复的问题

1. `author_main_input.py` 早期版本把 `return` 写在 observations 赋值之前，导致 66 条 typed observation 全部丢失（native  adequacy 显示 0 条 observation）。已修复并复跑全链。
2. RPO 纠正原本没有落在 `claim-changes.json` 里（它不在 49 union 内），已补 `out_of_union_requirement_repairs` 段。
3. 发现 Testing activity claim 也有同样的页首切片缺陷（不在 49 union 内），已修复并单列为 `out_of_union_repairs`，明确不计入 49。
4. 早期把 `forecast_version` 与 snapshot `--version` 写成不同字符串，导致快照 input SHA 与 forecast input SHA 不一致；已统一为同一版本串并重跑。

## 2026-10-23 C 大节点

- **第一轮独立审查（FAIL→修复）**：独立 agent 实跑 22 个探针，数字/语义/链全过，但抓到两个真缺陷——(1) 拆分片段的 `contiguous_range_sha256` 记成父切片哈希（污染 10 行账本）；(2) memo 引用早期迭代的 request SHA。两个 MAJOR + 两个 MINOR 全部修复（`verify_excerpts.py` 加自检断言），并从零重建整条链。审查报告原样保留于 `delivery/w09/review/independent-review.{md,json}`，修复记录见 `review/review-fixes.md`。
- **第二轮最终复审（PASS_WITH_MINOR）**：新 agent 实跑 19 个探针 + 2 次工具真实重跑，6 项修复逐项机械验证通过（50/50 账本哈希重放 0 错、三情景独立重算相同、冻结字节逐字节复核、0 回归），报告见 `review/final-independent-review.{md,json}`。三条新 MINOR/INFO（自检循环位置、memo 一处措辞、修复说明字段名笔误）均已收尾处理且不触发重建。
- **清理**：`delivery/w09/cleanup/receipt.json`（tmp 清空、scratch 移除、被取代的 request attempt 删除，六个正式 capture 保留；`restored=true`）。交付体积 22.91 MiB < 32 MiB 上限。
