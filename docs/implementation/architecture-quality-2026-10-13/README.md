# RF 架构质量改造交接（2026-10-13）

本包对应 CWP `docs/plans/architecture-quality-2026-10-13/results/revenue-forecast/report.md`，原基线 `b9208a2117b8423f4b355dfca885aaf0d56a05bb`。仅在独立 RF worktree 实施；ROOT 统一并线、推送、定点安装与跨仓验收。

## 已实施的共用职责

- `installation_manifest.py` 是可安装 runtime 的唯一 owned 文件清单与字节 manifest；CLI `--version` 与安装工具使用同一接口。`manifest_sha256` 文本格式保持，含义修正为真实 owned 内容；工程目录、output、cache 和已退休影子队列不参与。
- `forecast/dependencies.py` 区分直接 `ParameterUse.input_year`/`recognized_year` 与最终 `SegmentDependency`；只传播 ID，金额只由原模型计算。派生 ancestry 使用迭代集合，不复制递归算法。直接输入根用于参数用途/输入校准；有效依赖用于增长归属与 native scope；Narrative 可链接进度/carry-in/调整/约束及跨分部作用。
- 约束传播遵循原声明/应用顺序：linked exact 跟来源分部及比例，maximum 保留两侧候选金额；proportional cap 仅传播声明分部共享分母；fixed weights 的金额/激活条件分开；elimination 局部。图是结构性可用操作数，不能声称某个分支在真实世界必然发生。
- direct_growth 的累积输入/基础收入依赖由 ModelSpec 声明，其余模型仍按本来显式 stock/flow 驱动；不把库存、余额、比率等统一改成收入参数。lag 的期外 tail 不得当作当期收入增长驱动。旧通用测试夹具独立按显式 lag 窗口构造驱动树，而不是抄生产 visitor 答案。
- 同物理引文可以含不同业务/期间事实；同一命题换 ID 正反重标仍拒绝。不同结论共享引文只记录 `NOT_EVALUATED`，机械检查不替代原独立经济审查。
- 数值共同边界正确报告非法实数算术和巨整数转换；合法负数整数幂/有限大数保持。scenario order 仅允许最多4 binary64 ULP的舍入逆序，runtime/output 共用，不排序、夹平或修改金额，不放松收入对账。
- RF 无消费者进程内队列已从生产路径退休；CWP AUTO 是处理任务 owner。`tools/legacy/processing_demand.py` 仅供旧契约回放、不再安装；现有安装残留可保留但不参与 runtime manifest，也不被新代码调用。
- 提交 hook 用当前 PATH 的 Python/Git、POSIX sh 参数，无机器路径；保留真正 pre-commit 检查。仅三个快速根因回归进入现有 CI smoke，完整安装/原生矩阵仍只在大节点。

## 验收记录

初始根因 RED 11 failed/7 passed →18 passed；mixed table RED 1 failed/2 passed；影子任务 tripwire RED 1 failed；peer 跨分部/clock RED 4 failed。有效依赖反例的 Base-only shock 曾正确违反情景顺序，改为同一业务冲击应用于三情景；其后真正1 ULP误拒由共同数值边界修复，没有放松排序到业务容差。

最终集中 core：151 passed、2 subtests（13.37s）；受影响 native scope/SourceRef/Narrative/model-registry/安装/W07-W08工具边界：217 passed、62 subtests、8 skipped（24.58s）。8 skip 是既有 scalar mutation helper 不适用于特殊/拒绝案例，真实31-case矩阵全跑。

`verification.json` 保留最终原主线/候选各31 native（20 PASS/11 REJECT_OK）和31个实际 observed 精确一致记录；各3公开 CLI 返回预期，scratch/readonly 恢复。中微、腾讯、微软冻结输入重算与原正式输出的货币、单位、财年、历史收入、每分部完整输出、合并路径、敏感性、管理目标逐项精确一致，输入/原输出 SHA 不变。腾讯只新增共享引用的语义限制。ruff、mypy 11 public modules、现有 sh syntax 与 host-assumption guard 通过。

可复现的现有工程入口：

```powershell
python -B -m pytest -q tests/test_architecture_dependency_uses.py tests/test_architecture_numeric_errors.py tests/test_shared_excerpt_claim_semantics.py tools/tests/test_architecture_runtime_manifest.py
python -B tools/model_generalization_matrix/run.py --owned-root <独立临时scratch路径> --out-root <不同的临时report路径> --e2e
python -B tools/pre_push_gate.py
```

测试资料放独立 TemporaryDirectory，--basetemp 指向其子目录，结束恢复原样；原31向量与原真实公司文件不改。此记录是离线工程/数学验收，不是3家公司全技能业务审查或预测准确性认证，母计划 G2/G4/G5 仍由 ROOT 执行。

## ROOT 定点安装清单

runtime 共14个文件（2新增，12修改）：

- `scripts/installation_manifest.py`、`scripts/forecast/dependencies.py`（新增）
- `scripts/analysis/confidence.py`、`scripts/contracts/evidence.py`、`scripts/forecast/calc.py`、`scripts/forecast/segments.py`
- `scripts/model_registry.py`、`scripts/research/drivers.py`、`scripts/research/native_dependencies.py`
- `scripts/research_support_diagnostics.py`、`scripts/revenue_forecast.py`、`scripts/revenue_report.py`
- `scripts/source_narrative_context.py`、`scripts/source_preparation.py`

以 handoff 的 installation_files 精确清单为准。旧 `scripts/processing_demand.py` 退休，不用本次 --file 复制；新 manifest 忽略其旧安装残留，ROOT 如清理可只删除验为旧 owned SHA 的该单个文件。仓内 tools/tests/hooks/docs 不安装。安装工具自己的共享依赖已在 runtime，runtime 不反向依赖 tools。

当前 skill/engine 保持4.3.0、schema不变，历史快照不改。若 ROOT 选择 patch 发布，必须先在 schema_compatibility 保留历史4.3.0的3.7/3.8/3.9 emitter；不能只改动态 ENGINE_VERSION 而抹去历史，也不能重算历史 golden。

## 未扩大实施的范围

历史原文路径/artifact helper 与 attestation 有真回放和兼容读者，不仅因名字旧而删；个人路径只剩已说明的旧工程回放工具，不是默认 skill/CI 入口。大 report/document 文件分拆没有复现的收益证据，先不为行数拆文件。真实来源语义、经济假设、买方标准和完整公司 loop 仍是独立验收责任；本包没有 LLM、下载、真实安装或生产写入。
