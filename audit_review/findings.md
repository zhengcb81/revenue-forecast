# 审查发现（历史归档）

> **2026-08-13：本文件不再是当前实施依据。** 新任务只从 [audit_review/README.md](README.md) 读取唯一计划、`current_next`、阶段顺序和文档路由；本文仅保留早期审计证据。
>
> **2026-08-22 追加归档确认：** 本文不再追加实施进度。逐卡进度与计数唯一记录于 `assurance/runs/session-*/progress.md` 与 `assurance/unified_completion/state.json`（README §14 防双写漂移规则）；本文件仅保留审计发现（根因/教训类），不复制逐卡进度。

## 2026-08-03：初始范围

- 根项目已初始化 CodeGraph；结构分析可使用项目知识图谱。
- 根目录已有历史 `AUDIT_REPORT.md`、`FILING_FETCH_AUDIT.md` 以及较大的 `task_plan.md`、`findings.md`、`progress.md`，说明本次必须核验历史“已完成”声明，而不能只做首次静态审查。
- 当前工作树在审查开始时只有 `.coverage` 为既有修改；该修改不属于本次工作，必须保留且不得覆盖。
- 同级仓库至少存在 `filing-fetch`、`company-wiki`、`invest-core`、`invest-framework`、`invest-skills`、`dayu-agent`、`StockInfoDLSimple` 等潜在依赖，最终范围以计划和实现引用为准。

## 核验矩阵

| # | 计划目标（Phase 0） | 计划状态 | 实现证据 | 测试/运行证据 | 审查结论 |
|---|---|---|---|---|---|
| 1 | 正式输出经输入对照的独立语义验证 | completed | validator 独立重算 segment path/recognition/constraint/bridge/CAGR/概率/target/sensitivity（带 input） | 18 组对抗测试通过；但无 input 路径不重跑 shock（F-02） | **部分达成**：强路径达成，弱路径不达成 |
| 2 | 语义验证成功后才签发 publication receipt | completed | `run_forecast` 实际顺序 draft→receipt→hash→validate（F-01）；docstring/CHANGELOG 自述相反（F-12） | 验证失败确会抛异常不返回 receipt；但签发语义与设计相反 | **未达成** |
| 3 | 概率/目标/敏感性/禁止字段/来源期限/回测证据不可重签绕过 | completed | 概率/目标/禁止字段无 input 也可拒绝；敏感性仅带 input 拒绝 | 动态复现：无 input ACCEPTED、snapshot 全哈希重签 ACCEPTED、invest adapter 穿透（F-02） | **未达成（Critical）** |
| 4 | schema/engine 版本兼容清晰可迁移可回测 | completed | 3.0–3.3 配对正确；3.4/3.5 绑当前 engine 过窄；snapshot 任意 engine 过宽；无统一 registry（F-10） | 仅 3.1/3.2 有配对测试；3.3/3.4/3.5 无 | **部分达成（High 缺口）** |
| 5 | 正式流程不能无痕跳过 driver tree/管理层沟通/敏感性/工具调用 | completed | driver tree 结构验证落地；但自填 tool_call_id 可出 formal、search_event 可选、completeness 仍 opt-in（F-11） | Phase 8 checklist 全 `[ ]` 而标题 completed，伪完成确证 | **未达成（Critical）** |
| 6 | 先查统一索引，确认缺口并获授权后才下载 | completed | resolve-first 默认、显式 allow_download、market/security_id 门、journal+DownloadReceipt+provenance 审计链 | filing-fetch 117/117、e2e download 通过；无客户端 gap/authorization receipt（F-14 Low） | **达成（残余 Low）** |
| 7 | 财报获取只有一个 canonical owner | completed | 新调用方链唯一（filing_fetch_client→filing-fetch→company-wiki）；旧 `filing_acquisition.py` 完整双活、可执行下载 CLI（F-04） | 仅 tests 引用旧模块；SKILL/docs 已迁移 | **未达成（High）** |
| 8 | revenue 与 invest-* 单向依赖，无第二套收入预测 | completed | manifest 禁 revenue override、runtime import 路径核对、segment 恰好覆盖一次 | invest-core 36+framework 22 全绿；CodeGraph 结构确认 | **达成**（但消费验证受 F-02 削弱，归入 #3） |
| 9 | 按职责拆分大文件且数值行为不变 | completed | publication/contracts/constraints/backtest/report 已拆；`revenue_core.py`(94)、`filing_acquisition.py`(113) 高密度为文档化停点/待废弃 | 全量测试数值行为不变 | **达成**（残余并入 F-04 处置） |
| 10 | 改动具备 RED/正向/集成/迁移测试与可保存验收证据 | completed | 五仓库测试体系完整、对抗测试存在；coverage 分模块未达标（F-07）、安装副本漂移（F-08）、filing-fetch 非 hermetic（F-06）、wiki ruff 红（F-13） | revenue 253、filing 117、wiki 1629+1、invest 58 实跑 | **部分达成** |

## 审查结论（2026-08-03）

### 总体达成度

**部分达成。** 10 项一级设计目标：3 项达成（#6/#8/#9，其中 #6 带 Low 残余）、3 项部分达成（#1/#4/#10）、4 项未达成（#2/#3/#5/#7）。计划文档声称的"全部完成"不成立：计划首页仍停留在 13 Phase/294 tests，正文 Phase 8/17/19 状态自相矛盾，164[x]/387[ ] 的勾选率本身不能作为验收凭证。

### 核心判断

1. **正式可信链的两个 Critical 支柱未兑现**：
   - F-02：敏感性等语义可通过"改结果+重算全部哈希"在无 input 验证路径绕过，且已动态复现穿透 snapshot/backtest 与 invest-core/framework 正式消费边界（结构上 invest 链无任何函数接受 input）。
   - F-11：Phase 8 trusted workflow receipt 基本未实现，自填字符串即可签发 formal，"无 trusted verifier 只能 draft"的 fail-closed 门不存在。
2. **已落地的主体修复是真实的**：validator 独立重算、filing-fetch/company-wiki 的 reuse-first+identity+单 writer+审计链、invest 单向依赖，均有实现+测试双重证据，不是伪完成。
3. **风险集中在"旧物未清"与"发布面漂移"**：旧 filing owner 双活（F-04）、`.codex` 安装副本 34 文件漂移（F-08）、SKILL/CHANGELOG/契约文档与实现相反（F-05/F-12）——即使 Critical 修复完成，旧安装与旧 CLI 仍会保留漏洞。
4. **质量门总体健康但不封口**：五仓库测试基本全绿（company-wiki 1 项竞态），coverage/分模块门、hermetic 测试、ruff 门存在 Medium 缺口。

### 分项目结论

| 项目 | 结论 | 关键残余 |
|---|---|---|
| revenue-forecast | 部分达成 | F-01/F-02/F-11 可信链缺口；F-04 旧 owner；F-07/F-10；文档漂移 |
| filing-fetch | 达成（工作树） | F-06 发布复现性；F-14 Low；关键增强未提交 |
| company-wiki | 达成 | F-09 竞态（Medium）；F-13 ruff 红；scanner 直接测试薄 |
| invest-core/framework | 达成（受 F-02 牵连） | 无独立缺口；需随 revenue 契约升级；invest-core 1 skip 兼容边界待文档化 |
| 安装/发布面 | 未达成 | F-08 多副本四种状态并存；sync 默认只查 `.agents` |

### 问题清单（按严重度）

| ID | 级别 | 摘要 | 状态 |
|---|---|---|---|
| F-02 | Critical | 无 input 弱验证路径接受重签伪造（含 snapshot/backtest/invest 穿透） | 动态复现确证 |
| F-11 | Critical | Phase 8 trusted receipt 未实现，自填凭证可出 formal | 代码+文档确证 |
| F-01 | High | publication receipt 在语义验证前构造 | 源码确证 |
| F-04 | High | 旧 filing owner 代码层双活、CLI 可下载 | 源码确证 |
| F-08 | High | 安装副本严重漂移（revenue .codex 34 文件等） | sync 工具确证 |
| F-10 | High | engine 兼容矩阵过窄（3.4）且过宽（snapshot），无 registry | CHANGELOG+源码确证 |
| F-12 | High | compliance/SKILL 文档与真实签发顺序相反 | 文档+源码确证 |
| F-03 | Medium | 版本/计划基线漂移（SKILL 3.10.0 vs 计划 3.11.0） | 常量+计划确证 |
| F-05 | Medium | SKILL/CHANGELOG/契约文档多处漂移 | 文档确证 |
| F-06 | Medium | filing-fetch 测试非 hermetic、依赖未声明 | 双解释器实跑确证 |
| F-07 | Medium | coverage 分模块目标未达成/未测量（41%/0%） | coverage 实跑确证 |
| F-09 | Medium | worker supervisor 终止 Windows 竞态 | 全量 1 红+单跑 3/3 过 |
| F-13 | Medium | company-wiki ruff 6 项失败 | ruff 实跑确证 |
| F-14 | Low | 无客户端可见 gap/authorization receipt 字段 | 源码确证 |

## 2026-08-03：计划文档内部一致性初查

- 根计划第 5 行声明“13 Phase 全部完成、294 tests”，但同一文档后来扩展到 Phase 19，且状态表已出现更高的测试基线；首页状态明显未同步。
- 多个 Phase 标题标记 `completed`，其内部验收清单仍有大量 `[ ]`，不能仅凭标题判定达成；必须逐项回到代码和测试。
- Phase 17 存在直接状态冲突：阶段标题写 `completed`，后续“当前执行状态（追加）”仍写 `pending`。
- Phase 19 也存在直接状态冲突：阶段标题写 `completed（2026-08-02）`，阶段内部 19.8 又写 `pending（仅规划，未实现）`；后续还出现重复编号的 19.5/19.6/19.7/19.8/19.9。
- Phase 18 标题声明完成，但 18.5 的文档清单仍未勾选；需核对提交 `d1d444a` 和实际文件，而不能相信状态摘要。
- 历史审查报告中的 Critical/High 缺陷是 Phase 1–13 的主要设计输入。本次应验证修复是否真正形成不可绕过的发布链，而不仅是已有测试数量增长。
- 历史 `FILING_FETCH_AUDIT.md` 指出身份门、handle 深验证、上游版本契约、授权审计、deadline 和 hermetic test 等缺陷；这些与 Phase 9 验收目标一一对应，可用作回归清单。

### 初步文档风险

| 风险 | 证据 | 初判 |
|---|---|---|
| 状态摘要漂移 | 首页仍停留在 13 Phase/294 tests，正文已到 Phase 19 | 高 |
| “completed” 与未勾选验收项并存 | Phase 9、13、18、19 等 | 高 |
| 同一 Phase 状态自相矛盾 | Phase 17、19 | 高 |
| 编号/内容重复 | Phase 19.5–19.9 重复追加 | 中 |

## 2026-08-03：基线状态补充

- 根计划的状态表显示 Phase 0–16 完成，后续追加表先把 Phase 17 标成 pending，又在更晚的追加表改成 completed；Phase 19 也先在阶段内部写 pending、后在末尾写 completed。时间顺序可能解释状态演进，但未回写旧状态，导致文档不具备单一可信当前状态。
- Phase 20 已出现在追加状态表中，但此前的标题抽取未显示 Phase 20；需继续定位完整章节与验收内容。
- `revenue-forecast` CodeGraph 健康：39 个 Python 文件、1024 个符号节点、1335 条边，可用于核心架构与调用关系核验。
- PowerShell `Get-Content` 对根计划给出的行数/阶段识别与 `rg` 行号不一致（1229 vs 至少 2404），说明该文件可能存在特殊换行或编码表现；后续以 `rg`/Python 二进制 UTF-8 解析为准。

## 2026-08-03：计划 checklist 与代码结构

- 通过 `rg` 流式解析得到 20 个 Phase 段落。Phase 1/15/16/16.10/17 的清单已勾选；Phase 2–14、18、19 在“completed”标题下仍合计保留大量未勾选项。
- 全计划统计：164 个 `[x]`、387 个 `[ ]`。其中 Phase 9 有 5 checked / 139 unchecked，Phase 13 有 0 / 52，Phase 19 有 0 / 28。即使部分未勾选只是没有回填，计划文档也不足以作为验收凭证。
- CodeGraph 显示根项目 39 个 Python 文件：15 个核心/工具脚本、20 个主要测试文件、同步安装工具与示例。核心模块拆分已在物理结构上出现（publication、contracts/evidence、constraints、backtest、report 等），但 `revenue_core.py` 与 `filing_acquisition.py` 仍是高符号密度文件（分别 94、113 个符号），需核验是否符合 Phase 10“因循环依赖停止拆分”的合理边界。
- 测试文件结构覆盖 publication、schema/data contract、sources、filing、backtest、constraints、model registry、input construction、documentation 和 sync installations，表面上与计划目标匹配；后续必须通过实际测试和关键断言内容判断深度。

## 2026-08-03：跨项目 CodeGraph 基线

- `filing-fetch` CodeGraph 健康：6 个 Python 文件、234 个节点、283 条边。
- `company-wiki` CodeGraph 健康：328 个 Python 文件、7161 个节点、11715 条边，是本次审查中实现面最大的仓库。
- 三个核心仓库均已初始化 CodeGraph，无需新增索引；可以按 AGENTS.md 直接进行结构取证。

## 2026-08-03：跨项目结构

- `filing-fetch` 物理结构非常小：2 个实现文件、4 个测试文件。与 Phase 9 的“thin client / 不复制上游业务逻辑”目标表面一致；关键在于这两个实现文件是否严格校验 company-wiki 契约并 fail closed。
- `company-wiki` 的 source catalog 只是一个大型项目中的子系统；相关实现位于 `src/company_wiki/source_catalog/`，相关 contract tests 数量充足，并有 identity、resolver、operation lock、worker、URL enrichment、schema migration、retire 等专门测试文件。
- `company-wiki/tests/` 根下保留大量 `_check*`、`_test*`、`debug_resolver*` 等临时/诊断脚本；这不一定影响正式 pytest，但反映测试卫生和仓库治理仍需核验。
- company-wiki 的范围远大于本次目标。审查将聚焦被 revenue/filing-fetch 依赖的 source catalog、identity/resolver/ensure、canonical writer、worker/scanner、assertion/retire/restore、CLI/contract，而不把整个研究管线泛化为本次设计目标。

## 2026-08-03：正式设计基线（Phase 0）

根计划定义了 10 项一级设计目标，后续核验矩阵以它们为主轴：

1. 正式输出必须经过输入对照的独立语义验证。
2. 语义验证成功后才可签发 publication receipt。
3. 概率、目标、敏感性、禁止字段、来源期限、回测证据不可通过改结果并重算 hash 绕过。
4. schema/engine 版本兼容清晰、可迁移、可回测。
5. 正式流程不能无痕跳过 driver tree、管理层沟通、敏感性和工具调用。
6. 公司文档先查统一索引，确认缺口并获授权后才下载。
7. 财报获取只有一个 canonical owner。
8. revenue 与 invest-* 单向依赖，不生成第二套收入预测。
9. 按职责拆分大文件且数值行为不变。
10. 所有改动具备 RED、正向、集成、迁移测试和可保存验收证据。

发布基线是 skill 3.11.0、正式 schema 3.5、schema 3.4 legacy read-only；计划明确禁止用宽泛版本范围接收未知 engine。通用质量门要求根测试、tools 测试、compileall、ruff、coverage ≥84%，新增模块 coverage ≥90%。

计划显式范围还包括 `invest-core`、`invest-framework` 和 canonical skill/安装副本同步；因此这三项不能从最终结论中省略，哪怕重点仍是 revenue/filing/company-wiki。

## 2026-08-03：根项目核心结构初证

- publication 已拆到 `scripts/revenue_publication.py`：receipt 明确绑定 schema、engine、input hash、payload hash、validator 版本、固定 gate_ids、formal mode 和 `freeform_override_allowed=False`；验证器会重算 payload/receipt hash。结构上满足“签发后防静默篡改”的一部分目标。
- workflow receipt 仍由 `revenue_core.build_workflow_compliance_receipt` 直接构造 `status="pass"`。是否不可绕过取决于其调用顺序、正式输出 validator 是否从输入独立重算每个 gate，以及调用方是否能绕过；单看 builder 不能判定达标。
- 根仓库仍保留 `scripts/filing_acquisition.py`，其中 `AcquisitionConfig` 直接包含 CN/HK/US adapter command specs。若该模块仍可被正式/文档路径调用，就与“filing-fetch 是唯一 canonical owner、消费者不得 fallback 到旧 downloader”冲突；需查 callers、CLI/文档和测试后裁定。
- `company_wiki_source.py` 与 `filing_fetch_client.py` 也存在，说明当前至少有三层 acquisition 相关代码。下一步要区分正式 thin client、legacy compatibility 和实际可达的双 owner。
- CodeGraph 未解析出 `run_forecast` 的 callees，也未解析出 `build_publication_receipt` 的 callers；这可能是模块别名/局部导入造成的图解析限制。此处不能据此声称函数未被调用，需改用 `codegraph_context`/具体源码与测试取证。

## F-01（暂定高）：publication receipt 实际在语义验证前构造

- 计划目标 2 明确要求“只有语义验证成功后才能签发 publication receipt”。
- `scripts/revenue_core.py:1348` 的 `run_forecast` 实际顺序是：`_build_forecast_draft` → `build_publication_receipt` → `result_sha256` → `validate_forecast_output`。
- docstring 却声称“only published after passing validator”，与实现顺序不一致。
- 正式模式验证失败会抛异常，receipt 不会返回给调用者，因此当前证据证明的是“内部签发语义与设计不符”，尚未证明失败 receipt 可被外部获取或下游接受。
- draft 分支也先生成 formal receipt，验证失败后才重建并手工改为 draft；需进一步核验 hash 绑定和 draft consumer gate。

## 验证器入口初查

- `validate_forecast_output(result, data=None)` 的输入 `data` 是可选的；该函数除 `run_forecast` 外还被 backtest、examples、constraints 和多组测试直接导入。必须核验 `data=None` 是否形成弱验证路径，以及正式 consumer 是否强制重新验证原始输入。

## 验证器结构补充

- validator 会重算 segment model path、recognition、constraint audit、effective revenue、consolidated bridge、CAGR/growth、概率加权结果、source capture/claim hash 等，已明显超越旧审计所说的“只做字段存在/hash”状态；目标 1/3 的主体修复有真实实现证据。
- 版本分支包含 `FORECAST_SCHEMA_VERSION` 以及显式 `3.5/3.4/3.3/3.2/3.1`。其中 3.4/3.5 分支要求 `engine_version == ENGINE_VERSION`，表面上可能与 Phase 0“3.4 只接受 CHANGELOG 列出的历史 engine、legacy read-only”不一致；需先核实当前常量和后续 validator 逻辑再定性。
- validator 当前要求 `result_sha256`，而 `run_forecast` 又在验证前建立 receipt/result hash，解释了当前实现为何先签发再校验。但这正说明“验收函数把验证候选与已签发工件混在同一对象模型中”，设计目标 2 尚未真正落地为两阶段签发。

## F-02（暂定高）：无原始输入的公开验证路径弱于 receipt 所声称的 gate

- `validate_forecast_output` 只有在 `data is not None` 时才会重新运行每个 sensitivity shock；sensitivity completeness 也只在提供原始 `data` 时执行。
- 正式 `run_forecast` 会传入 `data`，因此正常生成路径确实经过强验证；但测试和其它消费者存在 `validate_forecast_output(result)` 的无输入调用。
- publication receipt 的固定 `gate_ids` 只有 `output_recomputation`，且 `build_publication_receipt` 是普通公开函数、receipt 是无外部签名的自哈希对象。任何能重算 receipt/result hash 的调用方都能构造“看似完整 gate”的候选；无输入 validator 是否能拒绝伪造 sensitivity 仍需用现有对抗测试/新诊断复现确认。
- `tests/test_publication_pipeline.py` 的正常 receipt 测试在 `run_forecast` 后再次调用的是 `validate_forecast_output(result)`（不带原始 input），说明下游示例本身采用较弱路径。

### 动态复现结论（F-02 升级为 Critical）

- 使用现有 `forecast_document`、现有 `_republish`（公开 builder + 全 hash 重算）构造伪造 sensitivity terminals。
- `validate_forecast_output(forged)` 输出 `ACCEPTED`。
- `validate_forecast_output(forged, original_input)` 输出 `REJECTED:sensitivity down terminal recomputation mismatch`。
- 这直接违反设计目标 3“敏感性不可通过修改结果后重算 hash 绕过”，并证明 receipt 的 `output_recomputation` gate 在无输入验证路径中会过度声明。
- 影响面至少包括所有只持有 forecast artifact、不持有原始 input 的下游 consumer、markdown 渲染和独立工件审计。修复方向应是：正式工件携带足以自包含重算的不可变输入/快照引用，或 consumer 强制同时提供并核验原始 input，且 receipt 只能由强验证返回的验证上下文签发。

## Filing-fetch 结构索引

- 核心入口集中在 `resolve_filing` / `_run_company_wiki_json` / `load_company_wiki_root`，契约集中在 `filing_contracts.validate_request` 与 `validate_handle`。
- handle 专门测试覆盖路径越界、sha256、文件缺失、非 HTTPS、发布时间、byte size、resolve error 与扩展字段；这与 Phase 9 的 capture-ready 深验证目标高度吻合。
- 存在 4 个真实工具 conformance 场景以及显式 `FILING_FETCH_E2E_DOWNLOAD=1` 下载门，表面上符合“默认不产生外部下载、真实下载显式 opt-in”。

## Filing-fetch 实现审查（CodeGraph explore）

- `resolve_filing` 默认只调用 company-wiki `resolve`；只有显式 `allow_download=True` 才调用 `ensure --allow-download --acquisition-config ...`。reuse-first 与显式授权边界已真实实现。
- 每个请求先经 `identify`，再把 canonical_name/market/security_id 写入规范化请求；下载前还要求 market/security_id，身份 gate 不再被显式路径绕过。
- identify、resolve/ensure 共用单一 overall deadline，catalog lock 使用指数退避且受同一 deadline 约束；Phase 9/15 的 timeout 与锁竞争目标已实现。
- 客户端显式验证 resolve/ensure/identity/config schema versions，非预期 schema 会 fail closed；上游契约漂移保护已实现。
- 只接受 `reused_exact` / `reused_equivalent`、恰好一个 match、`capture_ready=True`，随后进入 `validate_handle` 深验证。handle 会验证 companies 子树、真实常规文件、HTTPS、sha256 格式/内容、byte size 等；旧审计 High-1/2/3 的核心缺口已有实质修复。
- filing-fetch 没有自身 market adapter/writer；下载由 company-wiki ensure 路由，符合 thin client / 单 owner 的目标。

### 待确认点

- 根 revenue 仓库仍保留旧 `filing_acquisition.py`；filing-fetch 自身虽正确，不代表全系统 owner 已唯一化。
- 授权 receipt、gap receipt、request_id 与返回响应状态的完整字段未在 explore 可见片段全部展示，需由测试/实际调用继续核验。

## Company-wiki 核心符号索引

- 发行人归一相关核心符号为 `source_catalog/resolver.py::_entity_matches`。
- 下载/复用 owner 为 `source_catalog/acquisition_service.py::SourceAcquisitionService.ensure`，契约版本 `SOURCE_ENSURE_SCHEMA_VERSION="1.0"`。
- contract test 明确存在“首次下载并记录、后续零调用复用”场景，可用于验证 ensure 的幂等/reuse-first 行为。

## Company-wiki 实现审查（CodeGraph explore）

- `SourceAcquisitionService.ensure` 的职责边界清晰：coordinator 先 `resolve_or_stage`，只有 staged candidate + receipt 才交给唯一 `CanonicalSourceWriter.import_staged`，并把 reused/missing/ambiguous/downloaded/deduplicated/failed 全部写入 journal。单 writer 与授权/尝试审计目标已真实落地。
- resolver 只查询，不触发 acquisition side effect；只接受 `company_raw` 下 active + canonical + original_primary location，排除 dayu portfolio 外部路径，符合 filing-fetch 对 canonical companies 子树的安全边界。
- resolver 对 market/security_id、verified assertion、fiscal year/form/period/language/provider、published_date≤as_of、capture_ready、强 provider identity 分层筛选；无身份的 placeholder 会落到 MISSING 以允许授权下载，而具有可复用文件但身份不可验证时仍 fail closed。Phase 15 的“缺身份占位不误判冲突”与安全边界兼顾已有实现证据。
- Phase 18 的 issuer index 会把同一 canonical issuer 的 ticker/alias/security_id 归一，并对跨 issuer 共享 token 设置 ambiguous sentinel、拒绝作为 anchor；双类股/多地上市设计已真实实现，而非只写文档。
- ensure 的 acquisition journal 记录 request、adapter、candidate、provider、URL、content hash、canonical path 与结果，覆盖 gap/download 授权的可审计链主体。
- debug_trace 记录 entity gate 数量和逐候选排除原因，Phase 19.6 可观测性已落地于 resolver。

### Company-wiki 风险/边界

- resolver 为兼容旧数据，把“非数字开头的候选 security_id 与请求不一致”视为 soft match；安全性依赖前置 entity/issuer gate 和其它文档条件。当前设计意图合理，但应有跨 issuer 反例测试持续钉住。
- explore 未返回 assertion retire/restore 与 scanner 的主体代码，因此这两项只能依赖专门 contract tests 和运行结果判断，证据强度低于 resolver/ensure。

## 旧 acquisition owner 可达性索引

- 根仓库 `scripts/filing_acquisition.py` 不是一个小兼容 shim：它仍包含 config、adapter registry、canonical writer、acquisition manager 和公开 `resolve_filing`，符号规模显示是一套完整 owner 实现。
- CodeGraph 目前只发现 `tests/test_filing_acquisition.py` 导入它；新的正式 client 是 `scripts/filing_fetch_client.py::resolve_filing`。若 SKILL/docs/CLI 已完全迁移且旧模块明确废弃，运行时 owner 可视为唯一；否则目标 7 未达成。

## F-04（High）：财报获取 owner 在文档层唯一、代码层仍双活

- SKILL 和 references 已把正式路径统一到 `filing_fetch_client.py → filing-fetch → company-wiki`，并明确标记旧模块 deprecated。
- 但 `scripts/filing_acquisition.py` 仍导出完整 `resolve_filing`、包含 CN/HK/US adapter/writer，并保留可执行 `main()`/`--allow-download` CLI；它不是不可调用的 fixture-only 代码。
- 因此“新调用方的 canonical owner”已经唯一，但设计目标 7 的更强表述“财报获取只有一个 canonical owner”尚未在代码/发布包层实现。旧 CLI 可被误用并绕开 filing-fetch/company-wiki 的新 identity、journal、contract 与治理门。
- 建议验收应要求：从发布包/安装 manifest 删除旧 owner，或把所有公开入口改成 hard-fail/转发 thin shim；测试 fixture 移入 tests，不再保留能直接下载/写 canonical 的生产 CLI。

## F-05（Medium）：SKILL/CHANGELOG/运行时版本与契约文档漂移

- SKILL Versioning 声称 schema 3.6 的 receipt “signed after output validation”，与 `run_forecast` 实际顺序冲突。
- SKILL Formal output gate 仍写“schema-3.4 workflow receipt”，而当前正式 schema 已是 3.6；schema 3.5 才是 legacy read-only。
- SKILL 的 deterministic tools 列表重复列出 `revenue_forecast.py` 与 `revenue_backtest.py`，且 input helpers 仍标注 schema 3.5。
- CHANGELOG v3.10.0 记录把 acquisition 内置 revenue 并移除 filing-fetch/company-wiki runtime，当前 Unreleased 又反向恢复 standalone filing-fetch，但 `SKILL_VERSION` 仍停在 3.10.0。当前安装物处于“版本号仍指向旧架构、Unreleased 文档指向新架构”的状态。
- 这些漂移不会直接改变数值结果，但会误导消费者选择验证/获取路径，降低设计契约的可执行性。

## 工作树/发布基线

- revenue：`main` 与 origin 对齐，既有 `.coverage` 修改；本次新增 `audit_review/`。HEAD `6ebbc38`（schema 3.6）。
- filing-fetch：`main` 与 origin 对齐，但有多项未提交/未跟踪改动，包括 `.gitignore`、CHANGELOG、real conformance test、pyproject、e2e support/tests 和计划文件；HEAD `fd95d30`。因此当前工作树能力高于已提交发布基线的可能性很大。
- company-wiki：`master` 与 origin 对齐，只有 `llm_cost_log.csv` 既有修改；HEAD `0793fbd`。
- invest-core / invest-framework 均为本地 master（无 upstream 显示），工作树干净。
- `.agents` 与 `.codex` 下的 revenue/filing skill 均是普通目录，不是 junction；安装同步必须靠复制/manifest 校验，不能假定自动跟随 canonical repo。

## Targeted 测试实跑

- revenue publication pipeline：16/16 通过。
- output report 对抗测试：18/18 通过。
- filing-fetch client：4/4 通过。
- SKILL CLI 文档一致性：3/3 通过。
- 这些结果确认现有断言稳定，但不会推翻动态发现的 F-02：现有 sensitivity 对抗测试只走带 input 强路径，因此测试全绿与无 input 漏洞可以同时成立。

## 全量测试实跑（第一轮）

- revenue：253/253 通过；tools sync suite 4/4 通过。运行中旧 `filing_acquisition.py` 触发未关闭 subprocess stream 的 `ResourceWarning`，是低级资源卫生问题，也再次说明 deprecated owner 仍在全量生产测试面内。
- filing-fetch：105 tests，6 failures、2 errors、4 skips，当前全量门不通过。
  - `test_e2e_isolated_wiki` 收集失败：`ModuleNotFoundError: company_wiki`。
  - UTF-8 中文 stdin 测试最终因子进程无法导入 company_wiki 而失败。
  - 多个 real-tool conformance 测试的 subprocess 输出解码发生 `UnicodeDecodeError`，随后 rc/stderr 断言失败。
  - 4 个真实下载测试按设计因未设置 `FILING_FETCH_E2E_DOWNLOAD=1` 跳过，不计为回归失败。
- 第一轮使用 Codex bundled Python。需检查项目预期解释器/安装方式；若默认 `python` 或项目环境能通过，则归类为 hermetic/环境声明缺口，若仍失败则是直接回归。

## F-06（待分级）：filing-fetch 当前测试与安装环境不自包含

- 新 isolated-wiki e2e 文件直接 import `company_wiki`，但 filing-fetch 仓库本身未提供可解析的 src path/依赖安装，违反 Phase 9“hermetic tests、不依赖真实默认 company-wiki”的目标至少一部分。
- real-tool conformance 对 Windows 子进程编码处理不稳，在非 UTF-8 stderr 下 reader thread 崩溃并把 stderr 变成 None；这使测试无法可靠区分业务失败与编码失败。

### 解释器差异

- PATH `python` 是 `C:\Miniconda\python.exe`（3.13.9），可 import 本地 company-wiki；Codex bundled Python 3.12.13 不可 import。
- filing-fetch 的 untracked `pyproject.toml` 只有 ruff/coverage 配置，没有项目依赖、editable install 或 test pythonpath 声明。
- 因此 bundled Python 失败更准确地表明“测试依赖隐式全局安装/路径”，不是所有用户环境都会立刻发生的业务回归。已按计划文档的原始命令用 PATH `python` 复跑，当前 isolated-wiki 用例开始通过，等待完整汇总。

### 第二轮结论（F-06 定级 Medium）

- 按计划原始命令、使用 PATH Miniconda Python 运行：117 tests 全部通过，5 skipped，耗时 88.1s。
- skips 中 4 项是真实下载显式门，1 项是生产 catalog 测试时锁定；其余 isolated-wiki、UTF-8 中文 stdin、identity CN/HK/US、生产 round-trip 均通过。
- 因此 filing-fetch 当前工作树的功能回归门在预期用户环境中为绿；F-06 不是功能 No-Go，而是“测试/发布依赖未声明、非 hermetic Python 环境会失败”的可移植性与复现性缺口。
- 计划/状态表仍声称 64/66/67 tests，已严重落后于当前 117 tests；当前新增 e2e 又是未提交文件，不能把 117 作为已发布 commit `fd95d30` 的证据。

## Revenue 完整质量门

- compileall 与 ruff 全绿。
- 253/253 tests 通过；coverage 使用独立临时 data file，未覆盖用户已有 `.coverage`。
- 总 statement coverage 87%，通过计划的 ≥84% 总门。
- 但计划还要求“新模块 coverage ≥90%”：`filing_fetch_client.py` 41%、`company_wiki_source.py` 81%、`model_registry.py` 89%、`revenue_backtest.py` 89%，`revenue_forecast.py` 在当前非 subprocess coverage 采集方式下为 0%。因此逐模块目标未达成或未被正确测量。

## F-07（Medium）：coverage 验收被总数掩盖

- 状态表用“coverage 87%”宣称完成，但它只证明总门；没有证明 Phase 0 对新增模块 ≥90% 的要求。
- 尤其新的正式 filing-fetch client 和 CLI 是跨项目关键边界，却分别只有 41%/0% 的直接 coverage。现有 CLI 测试虽通过，但 coverage 配置未采集子进程，且 library error/contract 分支仍有大量未覆盖行。
- 应按模块设 CI threshold，或明确修改计划目标；subprocess CLI 需启用 coverage multiprocessing/subprocess 支持或增加 in-process main tests。

## Company-wiki 全量门启动

- 使用 PATH Python 3.13.9 / pytest 9.0.1 收集 1630 项，正在运行；这是比根计划“1522/1543+”更高的当前基线。

## Filing-fetch 完整质量门

- compileall 与 ruff 全绿。
- 117/117 tests 通过，5 skipped；coverage 96%，通过 ≥90% 门，核心两个实现文件分别 96%/97%。
- 这是当前工作树的强证据，说明 Phase 9 的核心契约与大部分 Phase 15–19 修复在预期环境中质量较高。
- 限制仍是：e2e/pyproject 等关键增强未提交，依赖 Miniconda 的隐式 company-wiki 可导入状态；发布/新环境复现性尚未封口。

## Critical F-02 的跨项目影响确认（invest-core / framework）

- `invest-core/scripts/invest_contracts.py::validate_revenue_forecast` 调用 `report.validate_forecast_output(result)`，没有原始 input。
- `adapt_revenue` 随后只检查 receipt 自哈希、formal mode、freeform flag 和 `output_recomputation` gate 字样；它无法补做 sensitivity shock 的输入对照重算。
- 因而动态复现的伪造 sensitivity 工件不仅能通过独立 revenue validator，也能进入 invest-* 的 canonical adapter。这把 F-02 从“可能影响下游”升级为“已确认影响正式跨技能消费边界”。
- invest-framework 的 `bundle_validator`、`company_orchestrator` 继续复用 `validate_revenue_forecast`/`revenue_reference`，所以完整 bundle/receipt 的 hash 链会忠实绑定一个语义上已被弱验证接受的伪造 revenue 工件；hash lineage 不能修复上游验证缺口。

## Invest 单向依赖与去重初查

- 文档和实现都明确 revenue-forecast 是收入唯一 owner；invest-core 只适配冻结的 recognized/effective paths、target summary 和 growth-driver hashes，不重算收入。
- runtime import 会核对实际 `revenue_core.py` 路径与期望安装目录，Phase 11 的“防错误版本 import”已实现。
- framework manifest 禁止 revenue/profit/cash-flow override 与 scenario probabilities，要求每个 revenue segment 恰好覆盖一次；结构上满足单向依赖目标 8。
- 由于 invest-core 未初始化 CodeGraph，这部分是字面/运行证据，最终计划仍应包含为该仓库建立结构索引与 CI 影响分析的治理项。

## Invest 质量门

- invest-core：compileall/ruff 全绿，36 tests 通过、1 skipped。skip 是旧 schema 3.3 growth-driver 检查被 normalizer 自动补成 legacy summary 的设计项，需在计划中明确其兼容边界而不是长期用乱码原因文本跳过。
- invest-framework：compileall/ruff 全绿，22/22 tests 通过；异构 segments + constraints + SOTP 端到端用例已不再 skip，与根计划旧状态“18 OK / 4 skip”相比有进展。
- 两仓库的现有测试没有覆盖“可重签的伪造 sensitivity 在无 input revenue validator 下被 invest adapter/bundle 接受”。改进计划必须增加 revenue→invest-core→framework 的跨仓库 RED conformance test，随后统一修复上游验证契约。

## Revenue 安装同步核验

- `tools/sync_installations.py` 默认只检查一个 destination root；当前 `.agents/skills` 与 canonical revenue manifest 完全一致（58 files，exit 0）。
- 这证明 `.agents` 普通目录目前未漂移，但尚未证明 `.codex/skills`；需用显式 `--destination` 补查，并在改进计划中把所有受支持安装根加入同一 CI matrix。

## F-08（High）：安装副本严重漂移，发布同步目标未达成

- revenue `.codex/skills` 显式检查失败：34 个文件与 canonical 不一致，包含 SKILL、CHANGELOG、schema/migration/compliance 文档、核心脚本和测试；还出现 canonical 当前文件树没有的旧 `scripts/forecast/compute.py` 痕迹。
- revenue 默认 sync 命令只检查 `.agents`，因此日常“exit 0 / MATCH”会漏掉 `.codex`；这正是计划要防止的多安装副本漂移。
- filing-fetch `.agents` 与 `.codex` 都是复制目录且含运行产生的 `__pycache__`。`.agents` 缺当前 `references/identity.md` 与新增 e2e；`.codex` 甚至缺 SKILL.md、CHANGELOG、config 和 references，只剩 scripts/tests。
- canonical filing-fetch 的 e2e/pyproject 等又尚未提交，导致“canonical worktree / git HEAD / Agents 安装 / Codex 安装”至少四种状态并存。
- 影响：不同 Codex/Agents surface 会执行不同契约、版本和文档；F-02/F-04 即使未来只修 canonical，也可能在旧安装继续存在。
- 改进计划需先定义每个 skill 的唯一 canonical manifest，再让 `.agents`/`.codex` 两端都作为默认 `--check` 目标；拒绝 pycache/coverage/计划底稿进入安装包，并在发布前用哈希 manifest fail closed。

## Company-wiki 全量测试结论

- 1630 tests 中 1629 passed、1 failed，耗时 383.81s。
- 唯一失败：`tests/contract/test_source_catalog_worker_bootstrap.py::test_terminating_supervisor_does_not_leave_an_orphan_worker`。
- 失败点不是业务断言，而是测试读取 `.source_catalog/worker_launcher_events.jsonl` 时收到 Windows `PermissionError`。该场景的目的恰是验证终止 supervisor 后不留 orphan worker，因此文件仍被占用可能代表清理竞态/孤儿进程，也可能是测试时序 flaky；不能简单归为无关环境噪声。
- resolver、retire、security identity、URL enrichment、worker、source compatibility 等本次相关主体套件均通过，说明 Phase 15–18 的大部分修复没有广泛回归。

## F-09（暂定 Medium）：worker supervisor 终止/事件日志清理存在 Windows 竞态

- 全量门当前为红，且失败直接落在 Phase 16 worker 版本/进程治理目标上。
- 需 targeted 重跑并检查是否有残留进程/句柄；改进计划应包含确定性 teardown handshake、句柄关闭确认、进程树终止与可重复压力测试，而不是增加盲目 sleep。

### F-09 复现分级

- 同一测试单独连续运行 3 次，3/3 通过（约 1.5–1.6s/次）。
- 因此它更像全量套件负载/前序状态触发的竞态，而非稳定功能错误；维持 Medium，不把 company-wiki 主体功能判为失败。
- 但全量 CI 仍不应标绿：改进计划要用 stress/repeat 与进程/句柄观测使该场景确定化，并验证无残留 worker，而不是把测试简单标 flaky/skip。

## Critical F-02 进一步扩展：snapshot/backtest 也走弱验证

- `revenue_backtest.validate_snapshot` 的 snapshot 明明同时包含 `input_document` 和 `forecast_result`，却调用 `validate_forecast_output(snapshot["forecast_result"])` 而没有传 `snapshot["input_document"]`。
- 因此 snapshot 具备强验证所需输入却未使用，理论上同一 sensitivity 伪造可在重算 `forecast_result_sha256` / `snapshot_id` 后通过；这会污染后续 backtest、accuracy record 和 confidence 证据链。
- 改进计划应把 validator API 拆成明确的 `validate_published_forecast(result, input)` 强入口；current schema 的 snapshot/invest/framework 一律必须传入并核对 input，只有显式 legacy read-only 路径才允许受限的 output-only 验证。

- `create_snapshot` 先通过 `run_forecast(frozen_input)`（强路径）生成结果，但随后又调用一次无 input validator；snapshot identity 只哈希 input/result hashes 等字段。攻击者若能同时改 result 并重算自哈希，最终安全性完全取决于 `validate_snapshot` 的弱调用。
- 现有 snapshot tamper tests 很可能只覆盖未同步重算所有相关 hash 的修改；改进计划需要新增“伪造 sensitivity + 重签 publication/result/snapshot 全部 hash”的 RED 用例。

## F-10（High）：legacy engine 兼容策略实际过宽 — 已精确取证

- Phase 0 要求 legacy schema 只接受 CHANGELOG 明列的 engine 版本，并禁止任意未知 engine。
- output validator 内联矩阵（`revenue_report.py:105-132`）：3.0→3.0.0、3.1→3.1.0、3.2→{3.2.0,3.2.1,3.3.0}、3.3→3.4.0、**3.4→当前 ENGINE_VERSION(3.10.0)**、**3.5→当前 ENGINE_VERSION**、3.6→当前。
- CHANGELOG 取证：schema 3.4 由 **v3.5.0**（2026-07-14）引入，并在 v3.6.0–v3.10.0 持续为当前 schema。因此真实 schema-3.4 工件可由 engine **3.5.0–3.10.0** 签发；当前代码只接受 3.10.0，会**错误拒绝真实历史工件**（过窄，兼容性回归）。
- 反向不一致：`validate_snapshot`（`revenue_backtest.py:72-75`）对非当前 schema **接受任意 engine**（过宽），与 output validator 的严格配对矛盾；同一工件在两条验证路径下结论可相反。
- 测试缺口：legacy 测试仅覆盖 3.1/3.1.0、3.2/{3.2.0,3.2.1,3.3.0}（`test_management_targets.py:142-179`）；**无** 3.3/3.4.0、3.4/{3.5.0..3.9.0}、3.5 任何配对用例。
- 根因：兼容策略硬编码在两个文件的 if-elif 链中且规则互相矛盾，无单一 immutable registry。改进计划需抽出共享 `(schema_version, engine_version, mode)` compatibility registry（含 CHANGELOG 溯源），由 forecast/output/snapshot/invest conformance 共用，并补齐 3.3/3.4/3.5 全配对测试。

## 正向确认：workflow/backtest 主体

- growth-driver tree 对 base 参数可达性、segment attribution、权重范围/和、evidence/反证等有实质结构验证；schema 3.6 headwind 负权重设计已落地。
- actuals 验证绑定 capture source/claim、as_of、币种单位、预测 horizon 与财年，历史审计所说的 actuals evidence 缺口主体已修复。

## F-11（Critical）：Phase 8 被标 completed，但 trusted workflow receipt 目标基本未实现

- Phase 8 明确要求：无 trusted verifier 的环境只能输出 draft；六类 communication 必须有 machine-generated event；`not_available` 缺 event 必须失败；自填 tool_call_id 不能代替 host receipt。
- 当前 capture contract 只要求非空字符串 `tool_name/tool_call_id`；测试 fixture 直接填 `test-browser`/`fixture-*` 即可产出 formal artifact。
- management `not_available.search_event` 在代码中是可选的；只有存在时才校验字段。自由文本 `search_description` 足以通过，正与 Phase 8.3 的禁止项冲突。
- `references/compliance-contract.md` 公开承认 tool invocation、search exhaustiveness、source retrieval truth 均依赖 host trust；但 runtime 仍可签发 `formal_output_mode="formal"`，没有 trusted verifier/fail-to-draft gate。
- sensitivity completeness 仍是 `require_sensitivity_completeness` opt-in；formal artifact 可以不证明所有 Base assumption/stress parameter 已测试或结构化排除，与顶层“正式流程不能无痕跳过敏感性”冲突。
- 根计划 Phase 8 的全部 checklist/验收项仍是 `[ ]`，而标题/状态表写 completed；这是本次最典型的伪完成。

### F-11 改进方向约束

- 不应在纯 Python schema validator 内伪造“可信 host 签名”；需要明确定义 runtime capability：有 trusted verifier → formal，无 → draft/unattested 且 invest 拒绝。
- host receipt 必须绑定 normalized request/response hash、tool/action、timestamp、environment、issuer，并由不可由输入作者调用的 verifier 验证。
- communication/search、capture/open、exception approval 与 sensitivity exclusion 应共享同一 attestation contract，而不是继续增加自填字符串字段。

## F-12（High）：compliance-contract 与真实签发顺序相反

- compliance 文档明确写“validator then signs”，SKILL 也写“signed after validation”；代码实际先 `build_publication_receipt` 再 validator。
- 这不是普通文案过时，而是正式可信链的核心顺序被文档错误陈述。改进计划必须先修两阶段 API/测试，再更新文档；不能只改说明去适配当前顺序。

## F-13（Medium）：Company-wiki 静态质量门不通过

- compileall 通过；`ruff check src scripts tests` 失败，共 6 项：5 个 unused import、1 个 unused local。
- 问题集中在 `test_source_catalog_download_suppression.py` 与 `test_source_catalog_retire.py`，都属于本次设计范围的 contract tests。
- 根计划/进度曾声称 company-wiki ruff 全绿，因此当前工作树或未提交测试演进已造成质量门回归。
- 改进计划应把 ruff 作为 company-wiki PR 必跑门，并清理/确认 unused test helper 不代表测试夹具未真正接入断言。

## Worker 进程观测

- 全量测试结束后没有发现 pytest 临时目录下的孤儿 worker；仅看到 production `source_catalog_worker.ps1` 与其 Python worker，使用 canonical project/config 且带 120s startup delay。
- 这支持 F-09 是测试负载/句柄关闭竞态，而非本次运行稳定遗留 orphan；仍需确定性 teardown 机制。

## F-03（中）：版本/计划基线漂移

- 当前代码常量是 `SKILL_VERSION=ENGINE_VERSION="3.10.0"`、`FORECAST_SCHEMA_VERSION="3.6"`；Phase 0 仍写目标 skill 3.11.0、正式 schema 3.5。
- 后续 Phase 20 状态表声称 schema 3.6 已完成，能解释 schema 更新，但未解释 skill 版本为何倒退到 3.10.0，也未同步 Phase 0 发布决策。
- validator 对 3.4/3.5 的 engine 兼容均绑定当前 `ENGINE_VERSION`，与 Phase 0 的“3.4 只接受列入 CHANGELOG 的历史 engine”表述不同。需结合 CHANGELOG/迁移测试判断是设计演进还是兼容回归。

## 对抗测试索引

- 已存在三类“修改语义后重算所有 hash”的测试：非法概率、伪造管理目标比较、伪造敏感性 terminal。
- publication suite 还包含 `test_public_api_never_returns_pass_receipt_before_output_validation`、draft receipt、receipt tampering、CLI 验证失败不写 JSON 等测试。
- 这些测试名称说明计划中的核心威胁模型已被编码，但是否覆盖无输入 validator/公开 receipt builder 的组合仍需读断言与动态复现；测试名称本身不是通过证明。

## Publication 测试深度

- `test_public_api_never_returns_pass_receipt_before_output_validation` 实际检查的是 `workflow_compliance_receipt` 不得同时含 `status=pass` 和 `output_recomputation` gate；它没有监控 `build_publication_receipt` 与 validator 的调用顺序。
- 因此该测试可以在当前“publication receipt 先构造、validator 后调用”的实现下通过，不能关闭 F-01。
- CodeGraph 对 `test_rehashed_forged_sensitivity_terminals_are_rejected` 返回的代码主体却是 management-target 伪造用例，符号名与源码内容明显不一致。对该具体测试需改用已定位文件的字面读取/实际执行，避免基于错配片段下结论。

## 对抗测试字面核验

- sensitivity 伪造测试确实存在，但最终调用是 `validate_forecast_output(forged, data)`；它只证明带原始输入的强验证会拒绝伪造，没有覆盖 `validate_forecast_output(forged)`。
- 测试辅助 `_republish` 直接调用公开 `build_publication_receipt` 并重算 `result_sha256`，与 F-02 的攻击/误用模型完全一致；因此可直接用现有 fixture 做无输入诊断复现。
- `test_draft_carries_no_publication_receipt` 测的是私有 `_build_forecast_draft`，不是 `run_forecast(mode="draft")`；测试名可能让读者误以为公开 draft 模式不携带 receipt，实际未证明。
- 多处正常测试和 markdown 渲染调用 `validate_forecast_output(result)`，确认无输入路径是正式可见行为，而非仅内部遗留。

## F-02 扩展到 snapshot/backtest：动态复现确认（Critical 维持）

- 探针 `audit_review/probe_snapshot_forgery.py`（只读诊断，不进产品测试套件）：
  1. `create_snapshot` 正常生成含 sensitivity_tests 的 snapshot；
  2. 篡改 `forecast_result.sensitivities[0]` 的 down/up terminal 并重算派生 impact 字段；
  3. 用公开 `build_publication_receipt` + `canonical_sha256` 重算 receipt、`result_sha256`、`forecast_result_sha256`、`snapshot_id` 全部哈希。
- 结果：`validate_snapshot(forged)` → **ACCEPTED**；`validate_forecast_output(forged_result, input_document)` → **REJECTED:sensitivity down terminal recomputation mismatch**。
- 结论：`revenue_backtest.py:78` 的 `validate_snapshot` 在持有 `input_document` 的情况下仍走弱验证路径，F-02 确认污染 snapshot/backtest/accuracy record 证据链。现有 snapshot tamper tests 未覆盖"伪造语义+全哈希重签"组合。

## F-14（Low）：filing-fetch 授权链完整但无客户端可见 gap/authorization receipt

- `fetch_filing.py:419-474`：`allow_download=True` 才走 `ensure --allow-download --acquisition-config`，且强制 market/security_id；响应只接受 `reused_exact`/`reused_equivalent`，其它 status fail-closed 并带 reason/debug_trace。
- `request_id` 由 resolution 注入 handle，`filing_contracts.validate_handle` 强制非空 trimmed；缺失有专门测试拒绝（test_fetch_filing.py:1874）。
- 下载授权/审计链在 company-wiki 侧真实存在：`acquisition.py:389-437` 验证 DownloadReceipt（candidate/provider/URL/sha256/byte_size/mime/HTTP 2xx），`canonical_writer.py` 二次校验并写 provenance（含 receipt 全字段），journal 记录 downloaded_new 等 outcome；e2e `test_e2e_download.py` 实跑通过。
- 残余缺口（Low）：filing-fetch 返回契约中没有一等 gap receipt / authorization receipt 字段；"确认缺口→获授权→下载"的证据只在 company-wiki journal/provenance 服务端，不随 handle 返回给 revenue 消费方做本地留档。计划中"授权审计"目标以 flag+journal 形式落地，审计算可追溯，但消费端无法自证本次调用经过授权。
- 此前"返回状态字段未全部展示"的待确认点已关闭：状态门与 request_id 门均有实现+测试证据。

## Company-wiki retire/restore 与 scanner 证据补强（原待确认点关闭）

- retire/restore：`store.py:334-414` 实现确认。软删除（documents/locations 置 retired）、事务内写 `document_retire_audit`/`document_restore_audit`（reason/actor/time）、restore 只允许从 retired 态恢复；`tests/contract/test_source_catalog_retire.py` 6/6 通过。证据强度从"仅测试"升级为"实现+测试"。
- scanner（1266 行）：虽只有 2 个直接命名测试（focus admission），但 `canonical_writer.py:185` 在每次 canonical 写入后调用 `scan_catalog` 重扫目录并立即 exact re-resolve（`canonical_writer.py:205-209` 失败即 CanonicalImportError）。因此 scanner 处于 ensure/download 热路径，被全部 import 契约测试与 filing-fetch e2e 间接覆盖。resolver/resolve 热路径不经过 scanner。结论：scanner 证据强度可接受，不再列为缺口；但建议改进计划为 scan_catalog 增加 1-2 个确定性直接单测（当前直接断言面薄）。

## Invest 结构证据补强（CodeGraph 已初始化，用户授权）

- invest-core CodeGraph：6 文件、183 节点、177 边，索引健康。
  - `validate_revenue_forecast(result)` 定义于 `scripts/invest_contracts.py:258`，签名**只有 result，无 input 参数**。
  - `adapt_revenue(result, scope, segment_name)` 定义于 `invest_contracts.py:631`，同样**无 input 参数**。
- invest-framework CodeGraph：149 节点、143 边，索引健康。
  - `company_orchestrator.py:27` 与 `bundle_validator.py:24` 均从 invest-core import `validate_revenue_forecast`/`revenue_reference`。
- 结构性结论：整个 invest 消费链上**没有任何函数接受原始 input document**，强验证在 invest 侧结构上不可能补做。F-02 跨项目穿透从"字面证据"升级为"字面+结构双重确认"，修复必须在 revenue 侧让正式工件自包含可验证（或 receipt 由强验证上下文签发），invest 侧只需消费新契约。

## 范围工具限制

- `invest-core` 未初始化 CodeGraph，结构性审查暂不能按项目 AGENTS.md 的首选路径进行。需用户授权初始化，或在最终报告中把该部分证据强度降级并仅做字面/运行核验。

## ZR-204/ZR-205（2026-08-16 恢复会话）

- ZR-204 accepted（锁/错误 taxonomy）：独立复核 7 项检查全过；分类矩阵正确、双 CLI 发射点 canonical、15 单测绿；受影响 contract 批量 3 失败均为已知既有（security_identity×2 HK-refresh stale_cache + extraction_quality unsupported），无回归。**error_type 从异常类名改为 canonical 码是跨消费方契约变更**（ZR204-IMPL-001），filing 侧 N-1 类名映射仅为旧 wiki 保留。
- ZR-205 implemented → independent_review：
  - **ZR102-F2 filing 侧根因关闭**（ZR205-IMPL-002）：raw SQLite lock 文本现在映射 retryable catalog_busy（canonical 直通或 N-1 OperationalError 文本路径），不再 fatal。
  - **ZR102-F1 移交 ZR-407**（ZR205-IMPL-003，原 successor=ZR-205 修正）：exact 模式 + --allow-download 无 authorization 即下载，属 authorization-bound GapPlan/CloseGap 范围（阶段 D），不在本 retry 卡。
  - 信封契约扩展（READ-09/READ-10）：成功 envelope 新增 calls/downloads；失败 envelope 新增 stage/attempts/calls/downloads——对账字段为 additive，revenue client 按 key 读取不受影响。
  - 验证：filing 328 passed/6 skipped、branch coverage 91.45%（≥90）、complexity 34≤34、mypy 干净、companies-reuse E2E golden identical、pre-commit 全绿（470 passed revenue 侧）。filing commit 0e5d209；revenue receipt commit 40d0c04。

## ZR-306/ZR-307/ZR-401（2026-08-17~18 阶段 D closure）

- ZR-306 accepted：role DAG 最小失效 property tests（wiki a608980）：document_hash 全失效、producer-key 变更=传递下游闭包、缺失子树只重算依赖、幂等+手工闭包对照、DAG 无环、PRODUCER_KEYS 覆盖 prompt/model/config hash。
- ZR-307 accepted：filing 分阶段 envelope + resolution trace（filing df66796）：_resolution_trace/_handle_from_resolution trace、main() 错误信封（FilingFetchError + resolution_trace）、5 新测试；338 tests 绿。
- ZR-401 accepted（RootPolicy 3.0，wiki 251615e）：3.0 strict loader（schema 门拒绝 1.x/2.x 并给迁移提示、external→private_user / company_raw→public、external 写目标/未知字段/非只读复用 fail closed、导出版本化+隐私脱敏+确定性 sha256）；12 tests + 787 unit 绿；McCabe max 8。
- 复核 5 findings（全非阻断）：REV-001 privacy_class 隐式默认（company_raw 缺省走 2.x public 默认，无权限扩大）；REV-002 contract 计数过报（43 vs 实际 28+1 skipped）；REV-003 生产 config 未切 3.0（显式决策：延期至 ZR-402/403 或阶段 D 出口，回滚纪律保持）；REV-004 环境（mypy 用 base python）；REV-005 plan_sha256 漂移（卡片冻结后更新）。
- 阶段 D：8/16 closure（ZR-301~307 + ZR-401）；current_next=ZR-402（adapter registry）。

## ZR-402~406（2026-08-18 阶段 D 收官）

- **ZR-402**（adapter 路由契约，wiki 57cd72e）：RED 探针三幸存突变体——S2 kind 路由（canonical 配对只测同配）、S3 conformance determinism 无负例、S4 路由五模块零 kind 分支无机械门（FC-1201 是 token-mention ratchet 且 adapter_dispatch/admission 在 allowlist 内=盲区）；S1 诚实负例（facade 失败封闭已被 seam02+ex08×2 钉死）。M1~M9 击杀表含进程内突变体重放 kill 证明。
- **ZR-403**（dedupe/resolver 泛化，wiki 87ee0ac）：health 先于 priority 结构成立但无 killer → retired/.rejections 高优先级竞争测试钉死；locations 表无 is_canonical 列（canonical 纯读时派生）；future_lake 入四上下文矩阵。
- **ZR-404**（envelope 加性，wiki f45f7ed）：schema 保持 "1.0"，新字段纯加性，filing validate_resolution_envelope 对未知键宽容（跨仓透传测试）；policy_snapshot 严格形状与 filing 校验器逐字同规则；路径脱敏 ${PROJECT_ROOT}/${USER_PROFILE}；mypy 基线 2 条既有错误继承（移交后续质量卡）。
- **ZR-405**（跨仓 policy containment，wiki e56eb5f + filing 3087f28）：最大设计教训——初版 subprocess 方案致 89 个既有 mock 测试失败，改为 wiki resolve/ensure 响应内嵌 `policy_export`（零额外调用）后零改动通过；policy hash 契约修正为对 policy DOCUMENT 计算（排除 policy_hash 键，与 uc canonical 纪律一致）；token 化 path_ref 破坏字节级 hash 契约 → export payload verbatim；1.x 最小配置 reusable_for_filing=None 致 export 全 None → 两 exporter 归一化 resolver-consistent effective reusable。
- **ZR-406**（gap-plan 矩阵，wiki 45ae721）：首轮 changes_required 暴露 claim 不实（"13 tests"实为 12、"5×6 全格"实为 24/30）→ 真·数据驱动 itertools.product 30 格参数化 + cells-distinct 完备性守卫 → delta accepted。语义澄清：newer_revision 列在无可用 local 时为 genuine missing；capture_ready 防御过滤须覆盖全部早退分支（首版漏 provider_error 分支被测试抓出）。
- **教训**：claim 计数一律实跑后写（第二次 count overclaim）；跨仓契约设计先查既有 mock/测试面；字节级 hash 契约禁止 payload 重塑；防御过滤覆盖全部早退分支；复杂度 ratchet 维护用 helper 提取。

## ZR-407/ZR-408（2026-08-18 晚：closure 补提交 + 验收钉死）

- **ZR-407**（authorization-bound GapPlan/CloseGap，filing+wiki 双仓）：RED 为 filing 与 wiki 两侧都只认 `missing` 为 actionable，newer_revision-only 授权计划零 close-gap/fetch。修复：wiki `_actionable_candidates` = missing ∪ newer_revision（外锁/内锁重验统一 + staging 选候选统一）；filing `_gap_plan_has_actionable_candidate` 同语义。owner 修复（用户授权）：exact/no-download `ensure` 走 reader 返回 attempt=null，不触 writer initializer/journal（real-tool conformance 只读路径修复，`_run_ensure_command` 抽取保持 ratchet）。复核 accepted（reviewer-zr407-independent）→ closure→ZR-408。三仓产物本会话补提交（wiki bdffc54、filing 5a1c18f、revenue 6145dad）。
- **ZR-408**（CloseGap staging→validate→canonical commit/recovery 验收）：无产品 RED——既有 FC-801/FC-804/canonical-writer oracle 已覆盖 C1~C4；唯一证据缺口是 single-flight 仅同进程线程覆盖。补强：Windows spawn 双进程 oracle（共享 append-only fetch log 恰一条、fetch_events=[0,1]、documents=1）——现有 `_acquisition_mutex` 文件锁被进程级验证。22 contract + 787 unit 绿；复核 accepted（3 info）→ closure→ZR-409。
- **教训**：① receipt 的 result_triplet 手写 sha 再次出错（71aa798d31… 非真实对象）——必须 git rev-parse 注入（第 8 次伪 sha 类事件）；② pre-commit skill-sync 检查要求 sync 在 filing 仓库 CWD 运行（在 revenue CWD 跑 `tools/sync_installs_b3.py` 会路径失败并被拦截）；③ 并发跑三个重 pytest 进程会让既有线程级 single-flight 测试 flake（SQLite InterfaceError）——单跑绿，非本卡回归。

## ZR-409（2026-08-19 阶段 D 出口）

- **future_lake 仅配置接入**：生产 config 第四根（directory+sidecar_filing_v1、read_only、reusable、p40，${PROJECT_ROOT}/future_lake）+ 仓库内 fixture——EX-08 生产版；产品 src diff=0（git diff -- src/ 空）。
- **三真实 root 只读旅程**：companies 紫金 601899/2025 exact；dayu-only 金斯瑞 HK1548/2021（内容 72b3ed25… companies 零 location，前提测试钉死，满足 exec plan T2 样本规则）；Dropbox 星环 688031/2024 **fail-closed**（http URL → capture_incomplete → MISSING，生产数据现状：Dropbox 独有 annual 无 capture-ready——378 内容中 53 独有，2 http+51 无 URL）；紫金跨根共享 canonical=companies（p10<p30）。
- **零写证据口径**：根浅指纹（top-level）+ 样本文件 (size,mtime,sha256)；catalog-DIR 零写不断言（后台 worker 并发写，ZR-206 教训）；full rglob 指纹在真实根上超时（首次实现即超时，改用浅指纹）。
- **场景映射方法论**：EX/LT/DL/IDX/UJ 44 场景→测试映射表钉死入 receipt；T3 项（DL-04~06/UJ-03/05/08）移交 ZR-802/806。
- **教训**：真实根旅程样本以 catalog 实际元数据为准（form_type='FY'、实体名金斯瑞、URL scheme 决定 capture_ready）——外部知识臆断导致连环失败；区分"产品缺陷"与"数据现状"（http URL 是数据现状，fail-closed 是正确行为）。
- ZR401-REV-003（3.0 loader 生产切换）显式再延期 → CA-303/阶段 I（产品代码变更违反本卡 core-diff=0）。

## ZR-502（2026-08-19）：sidecar 角色分离闭环 + 首页身份验证
- 判定信号：归一化子串包含（否决 token 交集/4-gram 滑窗；CJK 无空格 + 通用片段假阳性教训）。
- published_date 链路：sidecar published_at->filing_date 映射；缺 date fail-closed AMBIGUOUS。
- 词汇注册闭环：QualityFlag + REASONS/STAGES_BY_REASON（fc1301 gate 抓出 3 个未注册码）。
- _frontmatter 双形态（sqlite3.Row JSON 字符串列 vs dict）：isinstance 分支 + json.loads。
- identity flag 仅进 frontmatter，artifact metadata 不混入。
- 既有基线失败登记：corrupt pdf/xls（fitz）、dropbox_config_invariants（future_lake 漂移）、security_identity（stale_cache）、worker_bootstrap（时序）、integration（fitz）、pipeline 'parser_failed' 未注册（stash 对照证非本卡）。
## ZR-701（2026-08-19）：F1 入口（revenue）
- validate-only 零写是真实产品缺口（run_forecast formal 自动注册）→ draft mode 修复（强验证 + 零注册）。
- prepare_forecast 纯函数（formal/draft 显式模式）。
- publication_registry validation_status 加性键（draft/validated + 旧条目兼容 + 原子绑定）。
- ProcessingDemand 跨仓同契约（revenue 独立实现 + prepare_source enqueue dedupe）。
- 复杂度 ratchet（FC-1204-b）与 skill-sync（R4.2）是 scripts 改动的双前置门。
## ZR-602（2026-08-21）：asset facts basis 契约（revenue）
- 探针三缺口：resource≠reserve 语义隔离机制已存在（unsupported drivers 拒绝）→ 钉死；basis 元数据全仓零词汇 → 真实缺口；unit 无一致性门 → 真实缺口（基础版）。
- basis 设计为加性声明契约（携带即强制完整、缺省兼容既有——golden/industry e2e 零破坏实证）；单位一致性按维度分组（归一化等价，kt-vs-t 漂移拒绝；换算表归 ZR-610 ADR）。
- ratchet 两次触发（document.py 33>32、segments.py 17>15）均以 helper 提取解决——加性校验也会推高主函数 McCabe，新校验一律 helper。
- REV-001 修复（delta c9b0cfc）：`basis["ownership_basis"] in 枚举` 对 unhashable 值抛 TypeError 而非 ForecastInputError → isinstance(str) guard 统一异常类型，+5 回归 tests（20 passed）。教训：成员测试前先类型守卫。
## ZR-603（2026-08-22）：ownership/consolidation timeline + geography hierarchy（revenue）
- ownership timeline 契约（effective-dated fractions, fail-closed 回溯, pro-rata 日加权）+ apply-once 权益门（Kamoa/Porgera 双重折算防线）+ geography 层级索引。
- 词汇陷阱：`consolidated_forecast`/`segment_attribution`/`equity_share` 均为无关同名。
- REV-001~004 delta 修复（03d716e）：isinstance guard（第二次重犯"in 运算符对 unhashable 抛 TypeError"）、missing period key、None revenue、非 dict 地理容器。
- REV-005 minor（container 形状硬化，超出验收范围）→ 登记 ZR-607 会计桥后续。
## ZR-604（2026-08-22）：冲突保存与人工 review（revenue）
- semantic_groups 硬失败→双 assertion+resolution status 加性扩展；冲突参数均带 resolution_status + ≤1 accepted → 允许共存，否则原行为硬失败。
- 零 McCabe 增量模式第三次复用成功（helper 提取+纯调用+None 早退）。
- ZR-604 closure：reviewer accepted（17/17，1 minor null resolution_status 语义——登记后续）；state accepted 65/117；closure-advance -> ZR-610。
## ZR-610（2026-08-22）：会计 ADR 冻结（revenue，无产品代码）
- ADR 文档冻结 8 条会计决策（逐矿贡献=模型估计/resource≠reserve/basis/ownership timeline/单位一致性/冲突解决/地区层级/边界）；独立会计 reviewer accepted（8/8 会计合理性，2 info）。
## ZR-605（2026-08-22）：MineYearOperation 输入合同（revenue）
- 七字段必填 gap-on-missing（不默认 0）；derive_saleable_volume=volume×grade×recovery×payable；to_resource_model_drivers 映射 resource 模型。
## ZR-606（2026-08-22）：商业量价层（revenue）
- CommercialTerm provenance（value/source/assumption/period）；finite_number 加固（ZR-605 REV-001 落地）；byproduct 独立加项不重复计价；纯函数敏感性重算。
- ZR-606 closure：delta 47fe715（REV-001 saleable_volume finite_number）；delta 复审 staged-not-committed 教训；implementer receipt 重封；state accepted 68/117；closure-advance -> ZR-607。
## ZR-607（2026-08-22）：internal flow 会计桥（revenue）
- InternalFlow 八字段可追踪 + gross/net elimination 桥（net=external 内部消除不重复计）；period/scenario 过滤；与 ZR-606 商业量价组合。
## ZR-608（2026-08-22）：asset→segment→group reconciliation（revenue）
- reconcile_layer 容差门（|diff| ≤ max(1.0,|ref|)×tol → reconciled_modeled，否则 gap 不伪造差值）；fallback_segment_listing（分部并列 + 显式 gap）；gap_report 防伪收入（NaN/inf 拒绝、缺资产=gap）。ZR-608 closure：reviewer accepted（46/46）；state accepted 70/117；closure-advance -> ZR-611。
## ZR-611（2026-08-22）：通用多矿合成 E2E（revenue）
- 八类场景（控股/权益法/多金属/内供/跨币种/爬坡/gap/residual）全链确定性可重算 + 手算对照；生产代码零硬编码验证。ZR-611 closure：reviewer accepted（独立数学重算 + 八类非空洞）；state accepted 71/117；closure-advance -> ZR-609。
## ZR-609（2026-08-22）：紫金 pilot + 第二家泛化（revenue）
- 紫金三主要资产（卡莫阿-卡库拉权益链 0.396/巨龙全资/紫金山金+银副产品）逐矿可回答走 F2 全链 + 第二家纯金矿商泛化零硬编码；test-only。
- ZR-609 closure：reviewer accepted；REV-001 修正（ZR-611 closure 实际独立落地 404a2bb——流程偏差记录有误已更正）；REV-002 receipt 重封 ee6dd908；state accepted 72/117；closure-advance -> ZR-711。
## ZR-711（2026-08-23）：additive schema 3.8 opt-in（revenue）
- 3.8 opt-in（OPT_IN_SCHEMA_VERSION + EMIT + 版本门 {3.7,3.8} + operating_units 复用 ZR-605 契约 + converter 加 gap 不猜值）；REV-001 capture-integrity 门修复（版本门扩展须扫描全部 ==3.7 分支）；closure→ZR-707。
## ZR-707（2026-08-23）：mixed recognition/gross-net + multi-commodity（revenue）
- validate_mixed_recognition（混合 mode 合法）+ validate_commodity_matrix（multi-commodity 分段）+ validate_presentation_consistency（gross/net 声明）；词汇复用 constants 真源。ZR-707 closure：reviewer accepted（11/11）；state accepted 74/117；closure-advance -> ZR-708。
## ZR-708（2026-08-23）：already_satisfied 重验（revenue，零产品改动）
- snapshot 不可变/accuracy→confidence 消费链/四层 hash/未来 actual 拒绝——已有能力当前 triplet 全绿，test-only 重验钉死。ZR-708 closure：reviewer accepted（4 info）；state accepted 75/117；closure-advance -> ZR-712。
## ZR-712（2026-08-23）：版本化 ConfidencePolicy + 反博弈（revenue）
- policy 数据化（version/weights/rating_caps，未知版本 fail-closed，默认与 legacy 一致）；六类博弈检测（duplicate/split/plug/zero-impact/one-observation/wrong-record）；recompute_rating caps 驱动（80/55 一致）。ZR-712 closure：reviewer accepted（首轮 accepted → REV-001/002/004 minor delta 修复 1c04684 → delta accepted）；state accepted 76/117；closure-advance -> ZR-713。

## ZR-713（2026-08-23）：紫金 rolling-origin 历史回测（revenue）
- 严格 as-of 无 future actual（每窗口仅用 published ≤ as_of 的 actuals，泄漏 fail-closed）；company/segment/mine-volume 三层独立评估（segment 层用 actual_segment_revenue 合并 wape；mine-volume 层走 ZR-605 契约 validate_mine_year_operation/derive_saleable_volume，缺口 fail-closed，无预测对照 wape=None）；四层 immutable hash 链（snapshot_id=快照身份、record_sha256 绑定 {level, as_of}——重贴标签/改期破链）；窗口不足 → capped + rating hint 不伪造 metrics。ZR-713 closure：reviewer 首轮 changes_required（REV-001 blocking 三层 byte-identical 非独立评估 + REV-002 minor hash 绑定）→ delta 3479718 修复 → delta accepted（21/21 探针）；state accepted 77/117；closure-advance -> ZR-709（F2 合流卡，F2 常规链全闭）。

- 阶段 G 会话补充发现（2026-08-23，详见 session findings F-G1~F-G4）：journal 计数型 oracle 需注入式非空洞性证明（ZRR805-REV-001 教训）；连续推进时卡片五态（card/receipt/review/closure/游标）任一缺失即不得领取下一卡（ZRR805-REV-002 教训）；--version manifest 含 tests/** 故安装副本身份比对必须 sync-first；嵌套 checkout 的 sibling 解析失败按位置性 info 分类（主仓同 HEAD 复跑为准）。

## ZR-806（2026-08-22）：真实 T2 三 root/broker/artifact/mine/forecast 样本（revenue，test-only）
- 固定 5 样本清单（companies 紫金 FY2025 cninfo:1225023658/FY2024 cninfo:1222870413、dayu 1548 HK FY2021 hkexnews:10225111、Dropbox 星环 688031 FY2024 cninfo:1223325316/东吴研报 PDF）——content_sha256 跨 root 唯一、filing_date ≤ today、声明 hash 匹配实测；缺失样本 → 套件 fail（AUD2-05：blocked 不自动换样本）。
- 三 root 只读旅程：紫金 FY2025/FY2024 + dayu 1548 → REUSED_EXACT（download=0）；Dropbox 星环 → MISSING fail-closed（http URL 不伪造 handle）；旅程前后浅指纹 + catalog documents/sources/locations 行数不变（生产零写）。
- Zijin .source.json 契约（fiscal_year/company_name/security_id/pdoc/content_sha256==实测/byte_size==实测/fiscal_period=FY）→ F2 链 FY 语义可消费；星环 sidecar content_sha256 绑定（schema 较窄，info）；broker PDF 无 sidecar 诚实 raw。
- ZR-806 closure：reviewer-zr806-independent accepted（15 commands；AUD2-05 temp 变体 3 failed/7 passed；回归 30 + 全量 813+106 复跑；2 info）；state accepted 83/117；closure-advance -> ZR-902（阶段 H 首卡：实际调度每日 Windows T2）。
- **CRLF 教训**：README CRLF 行尾 → closure-advance CAS-CONFLICT（read_text().encode() 的 LF hash vs manifest 原始字节 CRLF hash 口径不一）→ README 转 LF + manifest-build CAS 重建解决；控制页文件须保持 LF。

## ZR-702~706/710（2026-08-19~21）：F1 全链（revenue）——docs 一致性补齐条目
- F1 入口链 7/7 全闭（2026-08-21）：ZR-702 schema 单一真源（schema_fields.py 冻结 REQUIRED 元组，lint/template/validator 一致）；ZR-703 文档/argparse 漂移清理（"schema 3.6" 6 处移除）；ZR-704 validate-only 零写门（prepare_forecast 纯函数 + draft 模式）；ZR-705 draft/formal 分轨（REV-06/08a 真实缺口修复：draft 可渲染 + formal→draft 降级重算 hash 拒绝）；ZR-706 FC-904 selector 契约补全（test-only）；ZR-710 publication 事务 + 原子写（_atomic_write_text tmp+fsync+os.replace、registry 故障注入、幂等）。F1 出口：ZR-701~706 + ZR-710 7/7 全闭（2026-08-21）。

## ZR-709（2026-08-23）：F2 合流——紫金五年预测用户旅程终验 fixture（revenue，test-only）
- J1 真实 source_preparation 子进程链复用财报/研报（reuse_receipt 全链可解释：outcome=reused_existing/bundle_status/download/parser/llm=0/producer_events DAG 角色；缺失 kind fail-closed exit 3 + ProcessingDemand 补齐路径）；J2 五年 FY2026-2030 输入由 F2 契约函数代数推导（MineYearOperation→commercial terms→权益链 0.396→realized_price 恒等闭合），reconcile_layer 10/10 reconciled_modeled、未建模白银 +120 = 诚实 gap 不冒充收入、schema 3.8 零漂移；J3 draft 渲染零注册、formal 位级重放 + snapshot 回放。复核 accepted（12/12 对抗探针，4 info）；**F 阶段 24/24 全闭**；state accepted 78/117；closure-advance -> ZR-802（G 首卡；ZR-801 machine registry 由 CA-105 唯一实现吸收）。

## ZR-802（2026-08-23）：组合旅程 existing/partial/missing/stale/conflict across roots（revenue，test-only）
- 五状态×跨根组合旅程（三进程真实链）：existing FY2024 exact 复用 download/parser/llm=0；partial 只含已有角色 artifact_read + 缺失角色 DAG 闭包（不盲跑全量）；missing 结构化 not_found 零伪造；stale 不以旧充新（fiscal_year_mismatch）；conflict 跨根双候选 ambiguous fail-closed 不择一；C2 第二次调用幂等（同 source 身份、零下载）；C3 八阶段 receipt 投影真实键。复核 accepted（11 探针，1 minor+3 info）；state accepted 79/117；closure-advance -> ZR-803。

## ZR-803（2026-08-23）：chaos/property/mutation 六类故障×幂等恢复（revenue，test-only）
- 锁（WAL 写事务不阻只读旅程、释放后同身份复用）、中断（崩溃前注册零孤儿、重跑精确一次）、磁盘（不可写结构化 exit-2 无半写/父目录、有效路径恢复）、篡改（单字节 hash 拒绝、原工件仍有效）、顺序（evaluate-before-create 拒绝、正常评估可跑）、时钟（未来 captured_date 信息集外）；每类故障后幂等恢复断言。复核 accepted（13 探针，2 minor+2 info）；state accepted 80/117；closure-advance -> ZR-804。

## ZR-804（2026-08-23）：平台与安装形态缺口（revenue，test-only）
- Windows 大小写变体同 source_id（golden 身份一致）、缺省配置 fail-closed 无静默 sibling fallback、安装副本 sync-first 身份逐字一致（R4.2 manifest 含 tests/，未同步新文件 legitimately 不同）、活跃脚本无 Windows-only 构造（CREATE_NO_WINDOW 允许为跨平台守卫）。回填 receipt 后联合复核 accepted（A-V1~V5）；**流程偏差登记：本卡曾跳过 receipt/复核直接开 ZR-805，由 ZRR805-REV-002 抓出后闭环（F-G2）**；state accepted 82/117；closure-advance -> ZR-805（与 ZR-805 联合 closure 9784c18）。

## ZR-805（2026-08-23）：T3 下载授权语义（filing + assurance，test-only）
- T3 真实执行唯一 owner=filing-fetch opt-in 门（FILING_FETCH_E2E_DOWNLOAD=1，CN/US/HK + 损坏拒绝 + 二次零下载标记结构钉死）；未授权 missing 请求 journal 零 downloaded_new（acquisition_attempts.jsonl 独立 oracle，AUD2-04；篡改注入证明非空洞）；revenue 入口显式 --allow-download 默认 False 无第二下载器。首轮 accepted（fc646953；REV-001 oracle 接线传文件致断言空洞即修 + REV-002 簿记漂移即 F-G2 流程偏差）→ delta 295f138 → delta accepted（B-V1~V4）；state accepted 82/117；closure-advance -> ZR-806（与 ZR-804 联合 closure 9784c18）。
