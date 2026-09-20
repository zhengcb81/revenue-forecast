# Revenue Forecast 技能审查发现

## 2026-08-18 — ZR-408 收尾发现（company-wiki，未 closure）

- 已复跑的 FC-801/FC-804 与 canonical-writer 合同表明，现有实现已经对受控 staging 做 hash/size/identity 验证，canonical writer 的路径落在 `companies/`，提交后 re-resolve，且同 binding 的重复执行为 zero-fetch reuse。不能把“已有测试”本身当作 ZR-408 closure；本轮逐项以 fetch/import/path/resolution/journal oracle 复核。
- 原 FC-804 的 single-flight 用例仅使用同进程线程，`lock timeout` 也实际是顺序重跑，未直接覆盖文件锁的跨进程语义。这是证据缺口，不是已证实的产品故障。
- 已在 `test_close_gap_concurrency_fc804.py::test_cg_c1b_cross_process_single_flight_one_fetch` 补充 Windows `spawn` 双进程合同：每个 child 重建自己的 catalog/coordinator/writer；共享 temp root/binding；adapter append-only fetch log 必须只有一条，同时两份结果的 `fetch_events` 为 `[0, 1]`，catalog documents=1。该测试首次与合集均通过。
- `ruff check --no-cache` 通过。`ruff format --check` 请求格式化整份历史 FC-804 文件（非本轮新增段落也包含既有格式差异），没有做无关全文件格式化；因此不将 format-check 记为通过。
- 默认 pytest cache / ruff cache 在 company-wiki 工作树内没有写权限；测试使用 revenue-forecast 受控 `--basetemp`，Ruff 使用 `--no-cache`。这只是环境警告，不是产品失败。
- 两次更宽的 `tests/unit` 运行都在工具约 30 秒回传边界截断，未给出退出码；不可列为成功。尝试停止遗留 Python PID 20528/25964 时被 Windows 拒绝，25964 随后已退出，20528 仍不可控。不要在没有进程所有权的情况下删除其可能使用的 temp root。

## 2026-07-26 改进实施计划编制依据

- 用户要求把审计结论转换为足够细粒度的实施计划，使较弱模型也能按固定顺序执行而不跳步。
- 本轮计划必须只描述实施，不直接修改生产代码；所有阶段必须包含：明确目标、允许修改范围、禁止事项、逐步动作、阶段内检查点、测试命令、验收条件、交付证据、失败处理和回滚边界。
- `planning-with-files` 要求后续实施者每完成一个阶段即更新 `task_plan.md` 与 `progress.md`，每两次查看/搜索后把新发现写入 `findings.md`，遇到错误执行三次不同策略后才升级给用户。
- CodeGraph 已于本轮确认正式预测链入口：`run_forecast`（`scripts/revenue_core.py:1390`）、`validate_document`（`:2290`）、`_run_forecast_core`（`:928`）、CLI `main`（`scripts/revenue_forecast.py:15`）、snapshot `create_snapshot`（`scripts/revenue_backtest.py:32`）。
- CodeGraph 已确认 filing 入口为 `AcquisitionManager`（`scripts/filing_acquisition.py:1914`），其当前顺序是本地 resolver 命中即复用，未授权下载则失败，授权后才选择市场 adapter；所有权收敛必须保持该行为不回退。
- 计划的首要依赖必须是 formal publication chain：先建立对抗性失败测试，再拆 execution/publication receipt，再补 output 独立语义重算，最后才允许修改 invest-core consumer。
- CodeGraph impact 显示 `validate_forecast_output` 三层影响 70 个符号，覆盖 CLI、Markdown renderer、snapshot/evaluation 和 management/output/constraints/end-to-end 测试；因此不得把它作为一次“大改后统一调试”，必须按 probability → target → sensitivity → field boundary → publication receipt 分批提交和回归。
- CodeGraph impact 显示 `AcquisitionManager` 三层影响 20 个符号；现有 14 个核心测试已经覆盖 reuse-before-download、无授权不调用 adapter、模糊身份、本地 snapshot、市场只路由一次、exact-hash dedup、staging 越界和 sidecar fail-closed。filing owner 收敛计划必须逐项保留这些行为。
- CodeGraph impact 显示 `run_forecast` 三层影响 115 个符号，直接连接 snapshot、CLI、示例运行器以及 driver、target、output、recognition、constraint、scenario/confidence 测试；因此 receipt/finalizer 改造必须先定义兼容过渡态，不能一次性删除旧字段后再修下游。
- CodeGraph callers 确认 `validate_source_coverage` 当前只有 `tests/test_data_contract.py` 的三个测试调用，没有任何生产调用者。计划中必须先加入一个“当前测试证明检查器本身有效”的基线，再把它接入 `validate_document`，最后新增 formal CLI 拒绝过期来源的集成测试。
- CodeGraph 文件树确认正式 Python 测试入口为 `tests/` 下 13 个 `test_*.py`，安装同步测试为 `tools/tests/test_sync_installations.py`；计划中的 targeted command 应统一使用 `python -m unittest discover -s <dir> -p "<file>" -v`，避免假定 `tests` 是可导入 package。
- 仓库没有 `pyproject.toml`、`setup.cfg`、`tox.ini` 或 `.coveragerc`；计划不得假设存在统一 task runner。静态检查继续使用显式 `python -m compileall` 与 `ruff check` 命令，coverage 作为阶段性证据而非隐式 CI 配置。

## 2026-07-26 Filing Fetch 独立技能审查

### 初始契约

- `filing-fetch` 确实是独立技能，目标是为 revenue-forecast、invest-*、industry-research 等消费者提供共享的 filing 获取入口。
- 书面所有权清晰：`filing-fetch` 应是 company-wiki acquisition engine 的薄客户端，不得自行重写 market routing、storage、hashing 或 dedup。
- 书面顺序为 identify → resolve/reuse → confirmed miss → explicit `--allow-download` → ensure；CN 由 StockInfoDLSimple/cninfo，HK/US 由 dayu-agent，canonical 写入 `companies/{entity}/raw/{kind}/`。
- 输出契约为 capture-ready handle；消费技能必须自行转换为各自 source/capture schema。
- 独立技能目录当前没有 `.codegraph/`，已按仓库规则询问用户是否初始化；在获答前用完整文件读取、原生结构分析和测试继续。

### 结构与初步实现发现

- 技能规模很小：`scripts/fetch_filing.py` 419 行、`tests/test_fetch_filing.py` 561 行、4 行配置和 9 行 changelog；没有 references 目录，也没有独立 input/output schema 文档。
- 正面设计：
  - 通过 `sys.executable -m company_wiki.source_catalog.cli` 调用 company-wiki，`shell=False`；
  - fuzzy query 必须先 identify，并拒绝 ambiguous/missing/conflict/unverified/inactive；
  - 默认调用 read-only `resolve`；
  - `--allow-download` 才加入 acquisition config 和下载授权；
  - 配置仅允许 `${USER_PROFILE}`/`${SKILL_ROOT}`，未知 token fail closed；
  - 客户端不自行实现 CN/HK/US adapter、canonical writer、hash 或 dedup，所有权方向正确。
- 高风险契约偏差 1：`allow_download=True` 时客户端直接选择 `ensure`，没有先调用一次可观察的 `resolve` 并确认缺口。当前安全性完全依赖 company-wiki `ensure` 内部仍保持 reuse-first；这与 SKILL 逐步声明的 identify → resolve → ensure 不完全一致，也无法由本技能自己的测试证明“下载前一定查索引”。
- 高风险契约偏差 2：只有 `company_query` 路径执行 verified/active identity。显式 `entity + market + security_id` 直接进入 resolve/ensure；代码没有验证 active、verified、exchange 或 security-master 记录，弱模型可通过预填猜测身份绕过 identity gate。
- handle 验证很浅：只检查 resolution status、单一 match 和 `capture_ready=True`；没有验证文档所承诺的 `canonical_path`、`snapshot_sha256`、`https_url`、文件存在/非空、路径位于 company-wiki `companies` 内、文件 hash、as-of date、provenance sidecar 或上游 response schema。
- request schema 也较浅：未知字段被静默忽略；日期、market、document kind、fiscal period/year 组合未在客户端校验；read-only explicit request 并未强制 docs 声明的 market/security_id。
- `timeout_seconds` 是每次 subprocess 的独立 900 秒，fuzzy identify + ensure 最坏可累计约 1800 秒；CLI 没有 timeout 参数或总 deadline。
- authorization 目前只是可由调用者设置的 boolean flag，没有 actor、scope、request hash、expiry 或 host-signed approval receipt，因此只能证明“调用时传了 flag”，不能证明用户真实授权。

### 测试与质量基线

- 实际测试为 13/13 通过；`python -W error::ResourceWarning -m unittest discover -s tests -v` 也通过。
- `python -m compileall -q scripts tests` 与 `ruff check scripts tests` 均通过。
- statement coverage 为 76%（`scripts/fetch_filing.py` 199 statements，47 miss），明显低于 revenue 主技能的 84% 基线。
- 未覆盖集中在：
  - config 文件不存在、非文件、JSON/字段/schema/root 错误；
  - request/identity/response 多种类型错误；
  - subprocess OSError、timeout、nonzero、invalid JSON、non-object；
  - ensure response 缺失、status/matches/capture provenance 异常；
  - CLI request-file/stdin malformed、fatal/error exit paths；
  - 真正的 `if __name__ == "__main__"` 子进程入口。
- `test_cli_main_guard_runs_and_resolves` 的名称和 docstring 声称验证 `python fetch_filing.py`，实际只是 import 后直接调用 `main(argv)`。即使删除 `__main__` guard，该测试仍会通过；CHANGELOG 所称的 guard regression 没有被真正锁定。
- `test_default_config_resolves_an_existing_company_wiki_root` 依赖当前机器真实 `${USERPROFILE}/Projects/company-wiki`，不是 hermetic test；在干净 CI、其他用户或 company-wiki 移动后会失败。

### 上游边界检查状态

- company-wiki 已有健康 CodeGraph 索引：208 files / 4083 nodes / 7633 edges，可用于核对 `source_catalog` 真正保证的行为。
- 第一次以自然语言检索 `company_wiki.source_catalog.cli` 时，CodeGraph 只返回了旧 `scripts/models` 相关符号，没有命中新 package；不能据此下结论。下一步改为先精确搜索 `ensure`/`SourceCatalog`/CLI parser 符号和 `company_wiki/source_catalog` 文件树，再读取具体节点。
- CodeGraph 的 `company_wiki/source_catalog` 路径和 `*source_catalog*` pattern 均返回空，说明这部分 package 可能被索引 ignore 规则排除或索引早于新增代码。按工具规则不把空结果当作“文件不存在”，下一步用 literal file listing 定位依赖源码，并记录索引覆盖缺口。
- 原生文件清单确认真正 package 位于 `src/company_wiki/source_catalog/`，包含 CLI、resolver、acquisition service、canonical writer、adapter process、journal 和大量 contract tests；CodeGraph 当前确实没有覆盖这一新增 src 子树。
- 上游 `cli.py`、`acquisition_service.py`、`canonical_writer.py` 已定位：
  - CLI `resolve` 和 `ensure` 是独立命令；
  - ensure 支持 `--allow-download` 和 paused worker 检查；
  - `SourceAcquisitionService.ensure` 是核心顺序 owner；
  - `CanonicalSourceWriter` 拥有 canonical path、immutable provenance、hash reuse 和 catalog registration。
- 因此 filing-fetch 应保持薄客户端，不能把上游这些实现复制回来；但它仍需要版本化 handshake、typed response validation 和可以证明调用顺序的 adapter contract。

### 上游实际保证

- company-wiki `SourceAcquisitionService.ensure` 与 `AcquisitionCoordinator.resolve_or_stage` 确实强制 reuse-first：
  1. 先调用 catalog resolver；
  2. exact/equivalent 命中立即返回，不调用 adapter；
  3. ambiguous 或 identity conflict 不下载；
  4. 未授权时 missing；
  5. 授权后按 market 选择 adapter；
  6. discovery 后用 provider identity 再 resolve 一次；
  7. 仍缺失才 fetch 到 request-specific staging；
  8. 校验 candidate/receipt、path containment、size、SHA-256、PDF magic 和 HTTP 2xx；
  9. canonical writer 再负责唯一写入。
- 所以 filing-fetch 的 `allow_download=True → ensure` 不是当前版本的实际盲下；风险在于客户端没有校验 acquisition/ensure schema 或 capability，未来上游语义漂移时无法 fail closed。计划应采用“先做版本/capability handshake 和 contract test”，而不是在客户端机械重复一次 resolve。
- company-wiki CLI 所有异常统一在 stderr 输出 `{status:"failed", error_type, error}` 并返回 1；成功 stdout 返回 JSON、exit 0。filing-fetch 当前把 nonzero stderr 截成自由文本，丢失上游结构化 error type 和 stage。
- company-wiki CLI 的 ensure 会在允许下载且 worker 为 paused 时拒绝；核心 acquisition service 会生成 journal attempt，区分 reused-before-download、reused-after-discovery、missing、ambiguous、downloaded_new、deduplicated_after_download。
- 上游当前已经严格校验市场路由、candidate、receipt 和 staging bytes，客户端不应复制这些校验公式；客户端应验证返回 handle 和 schema，以保护消费边界。
- company-wiki `SourceRequest` 会严格校验日期、fiscal year、文本和 allow_download 类型；resolver 会排除未来发布日期、identity conflict、缺失 capture trace，并只对现存 canonical primary file 生成 handle。
- canonical writer 的目标路径确实是 company root 下 `companies/{safe entity}/raw/{document-kind}/...`，使用临时文件 + size/hash 复核 + `os.replace`，写 immutable `.source.json`，扫描入 catalog，最后要求 exact provider identity 能重新 resolve。
- 上游测试覆盖 reuse-before-download、download suppression、dedup、CN e2e、adapter process、canonical writer 和 paused control；所以核心下载安全主要属于 company-wiki，filing-fetch 的测试重点应是 client/upstream contract compatibility、request normalization、authorization 和 handle validation。

### 审查错误记录

- 最小对抗复现第一次尝试在 PowerShell here-string 内加入含中文用户目录的 Python 绝对路径，运行时再次变为不可导入路径，报 `ModuleNotFoundError: fetch_filing`。这与审计阶段已知编码问题相同；不重复该方法，改为把工作目录设为 filing-fetch 并使用相对 `scripts` 路径。
- canonical 源定位首次用 `Get-ChildItem -Recurse` 扫描整个 Projects，10 秒超时；只确认 `.agents/skills/filing-fetch` 自身没有 `.git`。下一次改用有限深度或快速目录工具，不重复无界递归。

### 最小对抗复现

- 构造上游 `schema_version="999.0"`、handle 只有 `capture_ready=true` 的成功 response，filing-fetch 接受并返回；确认它未验证 resolution schema 或文档承诺的 handle 必填字段。
- 显式 request 使用猜测的 `entity="Guessed Company"`、`market="ZZ"`、`security_id="GUESSED"`、非法 `as_of_date="not-a-date"` 仍被客户端转发；客户端没有 identify，依赖上游最终拒绝。
- request 中未知字段被静默丢弃而非 fail closed，调用者可能误以为某个筛选/授权字段生效。
- `allow_download=True` 的 explicit request 只产生一次 `ensure` 调用，没有 client-visible `resolve`。当前不会盲下是因为上游 ensure 的实现保证 reuse-first，而不是因为 filing-fetch 自身验证了顺序。
- 13 个现有测试中没有：
  - request exact-field/schema 测试；
  - explicit identity verified/active 测试；
  - upstream schema/version mismatch 测试；
  - handle required-field/path/hash 测试；
  - subprocess timeout/nonzero/invalid JSON 测试；
  - CLI exit-code taxonomy 测试；
  - consumer integration 测试。

### 所有权与可移植性

- `.agents/skills/filing-fetch` 没有 `.git`，在 `Projects` 三层深度内未找到同名 canonical repo，`.codex/skills` 也没有副本。实施前必须先确定 canonical 源；否则直接修改当前目录会产生不可追溯的安装态变更。
- 当前 skill 目录含 `.pytest_cache`、`.ruff_cache`、`__pycache__`、`.coverage`、`.benchmarks` 等生成物；发布/同步流程没有显式排除规则，计划应增加 packaging hygiene 检查。
- company-wiki 的 `resolve`/`ensure` CLI 原生支持 `--company-query`，并能在同一进程中完成 identity + source resolution/ensure。filing-fetch 目前先单独 `identify`，再发 explicit source request，重复了 identity schema validation和 normalization，增加一次 subprocess、累计 timeout 和 identity snapshot 的 TOCTOU 窗口。
- 更符合“薄客户端”的目标实现应直接把 fuzzy query 传给上游原子 `resolve`/`ensure`，然后严格验证上游返回的 nested identity + resolution/ensure schema；不应继续维护第二套 identity validator。

### 上游测试证据与现有计划缺口

- 实际运行 company-wiki 的 acquisition、download suppression、canonical writer、adapter process、CN StockInfo e2e 五个 contract 文件，共 21/21 通过；这为 reuse-first 和 canonical storage 提供了比 filing-fetch 自身测试更强的证据。
- 现有 `task_plan.md` Phase 9 已正确选择 company-wiki → filing-fetch → revenue 的 ownership 方向，但粒度仍不足以指导弱模型修复独立技能；缺少：
  - filing-fetch 自身 request/input schema；
  - atomic fuzzy identity 调用迁移；
  - upstream schema/capability pinning；
  - typed error taxonomy；
  - capture-ready handle 深验证；
  - 总 deadline 和 CLI timeout；
  - authorization receipt；
  - hermetic/actual subprocess tests；
  - 76% → 90% coverage 目标；
  - consumer integration 和 packaging hygiene。

## 初始契约观察（2026-07-26）

- `revenue-forecast/SKILL.md` 声明了严格的 0–11 步工作流、formal output gate 与大量 hard failure gates。
- 契约要求 `scripts/filing_acquisition.py` 默认只读复用，只有确认缺口且用户显式授权后才允许下载。
- 契约声称 A 股通过 StockInfoDLSimple/cninfo，港美股通过 dayu-agent，并把 immutable raw + provenance 写入配置的 company-wiki 数据根。
- `invest-core` 声明收入预测是收入路径、增长驱动、目标、敏感性和回测的唯一所有者；下游只做不可变适配。
- `invest-framework` 声明依赖方向为 `revenue-forecast → invest-core → leaf invest-* → invest-framework`，禁止下游重建上游路径。
- 以上目前只是文档声明，尚需在实现与测试中核实。

## 待证实问题

- 工作流门是否全部由运行时强制，还是部分仅存在于提示词。
- 本地复用和下载是否有两套重叠实现：`revenue-forecast/scripts/filing_acquisition.py` 与独立 `filing-fetch`。
- company-wiki 的规范路径是否由配置/实现保证，而非仅由文档描述。
- invest adapter 是否真的拒绝突变、版本不兼容和目标/驱动重解释。

## 工具状态

- CodeGraph MCP 已配置但仓库尚未初始化，因此当前不能读取结构图。已询问用户是否允许 `codegraph init -i`；在此之前使用原生文件清单、AST/导入分析和测试，不把 CodeGraph 缺失误判为项目设计缺陷。

## 结构盘点

- 仓库主体为 9 个运行脚本、11 份参考契约、13 个主测试文件和 1 个安装同步工具测试。
- `revenue_core.py` 约 2324 行，集中拥有输入验证、来源与证据、参数、模型路径、识别、聚合、敏感性、主题分析、置信度、研究覆盖、增长驱动树、管理目标和工作流回执；虽然函数化明显，但文件级职责高度集中，需重点审查“逻辑模块化但物理未拆分”的维护风险。
- `filing_acquisition.py` 约 2080 行，内部已拆成配置、请求、身份解析、文件系统复用、适配器、规范写入和 manager 等对象，但单文件很大。
- `model_registry.py` 是独立注册表和纯计算器，核心通过注册表调用，符合文档中的扩展点设计。
- CLI `revenue_forecast.py` 只有约 43 行，入口薄；报告验证/渲染独立在 `revenue_report.py`，约束独立在 `revenue_constraints.py`，回测独立在 `revenue_backtest.py`。
- `run_forecasts.py` 明确包含 Tencent/Microsoft 示例构造器，需确认它是示例/开发工具而非正式运行时依赖，避免形成公司硬编码污染。
- `config/company_wiki.json` 使用可展开 token，无绝对用户路径；CN adapter 指向 StockInfoDLSimple 的 `src.company_wiki_adapter_cli`，HK/US adapter 指向 dayu CLI。

## 契约分层观察

- 数据治理明确承认：URL、capture receipt 和 claim 结构只能证明内部链接与防篡改，不能证明外部内容真实、工具确实被调用或证据在经济上支持参数；这是一项重要且诚实的信任边界。
- 九维研究覆盖是“遗漏门”而非打分项；每维必须映射到实际使用参数、登记 data gap，或给出对预测期不重要的理由。
- 增长驱动树不另建收入预测，而是把 Base 参数、证据/反证、领先指标、falsifier 和终值增量归因连接起来；每个 segment 的 root 权重要求精确和为 1。
- 正式输出治理采用 schema-3.4 workflow receipt、冻结输入/来源/claim 哈希和只读 renderer，声明禁止自由文本增加或覆盖正式数字与结论。
- 仍需通过实现核对：上述门是否在 `run_forecast` 与 `validate_forecast_output` 两端独立重算，而不是只检查自报字段。

## 模型、管理目标与输入输出契约

- 模型库含 23 个跨行业模型，覆盖直接增长、销量、产能、订阅、平台、服务、项目 backlog、资源、基础设施、银行、资管、零售、交通、租赁、许可、广告、游戏、交付、保险服务和 reserve depletion；选择基于 segment economic identity，而非公司枚举。
- 管理目标契约区分 annual、期末 run-rate、跨期 cumulative 和 ambiguous，并要求 comparable in-horizon target 必须进入情景且数值满足；这能减少把 bookings/ARR/GMV 误当收入的风险。
- 输入 schema 要求 exactly six 官方沟通类别、exactly nine 核心研究维度、参数级 claim/capture 哈希、三情景同模型、识别元数据、增长驱动树和目标 ledger。
- 输出验证文档声称独立重算模型、识别、约束、bridge、CAGR、敏感性、置信度、目标 attainment、增长驱动归因和 workflow receipt；实现审查将重点确认“独立”程度。
- 回测是独立 schema-2.0 immutable snapshot/actual/evaluation 流程，后续预测只允许导入哈希链接的 accuracy record。
- `resource-business-guidance.md` 的乱码来自当前 PowerShell 输出解码，而非文件损坏：Python 已确认全部参考文档可按 UTF-8 解码，资源指南开头是正确中文。该项不构成技能缺陷。

## 运行时入口与核心结构

- 当前运行时版本与 changelog 一致：`SKILL_VERSION=3.10.0`、`FORECAST_SCHEMA_VERSION=3.4`，schema 与技能版本独立。
- `ModelSpec` 是 frozen dataclass，registry 和内部 mapping 使用 `MappingProxyType`；重复 driver、维度不全、default/ratio 指向未知 driver、重复 model ID 均 fail-fast。
- `revenue_forecast.py` 是薄入口：读 JSON → `run_forecast` → `validate_forecast_output` → 写 JSON/renderer Markdown；`--validate-only` 仍完整运行计算与输出验证。
- `validate_document` 串联 top-level、sources、parameters、evidence、history、base reconciliation、research coverage、growth-driver tree、management targets 和 constraints；不是只靠提示词。
- `_run_forecast_core` 再次调用 `validate_document`，而 `run_forecast` 在进入 core 前也调用一次，形成重复验证（安全但有性能/维护重复）；之后才计算目标、场景、驱动、敏感性、主题、置信度和 workflow receipt。
- `validate_forecast_output` 是 362 行的独立入口，调用模型计算、识别/约束相关计算、置信度、驱动分析、capture 与 receipt 重算，并检查禁止投资字段；需要继续核对它是否错误地复用了过多生产计算函数，导致共同缺陷无法被测试发现。

## 输入、来源、参数与证据实现

- 顶层验证强制 current schema、公司/日期/币种/单位/财年、连续预测年，以及 history/sources/parameters/segments/research/driver tree/management/evidence 等核心字段；预测年必须从 base+1 连续开始。
- 历史收入除 pre-revenue 外至少两期、必须连续且包含 base year，并绑定 exact-value claims；base history 与 reported total 允许配置的 reconciliation tolerance。
- 当前来源验证拒绝未知 source type、非 HTTPS、占位/搜索域名、缺失 locator/publisher/title 和 as-of 之后的发布日期；capture 是否必需取决于调用参数，需在 `validate_document` 确认 current schema 是否强制传 `require_capture=True`。
- derived fact 使用受限 AST 算术、循环检测和重算，不执行任意代码；driver parameter 同时强制 scenario、FY period、dimension、ratio/nonnegative 边界。
- 模型 formula dispatch 已完全通过注册表，唯一残留模型特例是 `retail_franchise` 两个可选 driver 必须成对出现，属于跨字段结构约束而非公式分派，合理但应在 registry spec 层表达会更内聚。
- 潜在契约偏差：source-linked `analyst_assumption` / `scenario_stress` 只要求“存在任意 linked claim”，没有强制 `support_type="rationale_support"`；因此一个 `exact_value` claim 也能通过，与 `input-schema.md` 的文字要求不完全一致。需用负向测试验证。

## 计算、识别、聚合与敏感性

- segment 层强制 low/base/high 三情景使用同一模型；project backlog / delivery pipeline 还把首期 opening 与 base fact 对齐。
- 每个 segment 强制 recognition metadata、policy claim、gross/net presentation 一致；over-time 强制 progress 参数，lagged activity 强制正整数 lag 和逐情景 carry-in。
- 计算顺序正确落实为 modeled activity → recognized revenue → cross-segment constraints → company aggregation；company bridge 与 terminal incremental contribution 都进行数值 reconciliation。
- 情景排序同时在 segment effective revenue 和 company revenue 层强制 `low <= base <= high`；概率默认不存在，启用后强制三情景和为 1 且有 rationale-support claim。
- 明确缺陷候选：`referenced_parameter_ids` 只包含 segment drivers、lag carry-in 和 forecast adjustments，遗漏 over-time progress 参数及 revenue constraint/cap/weight 参数。因此正式敏感性框架不能覆盖“识别进度”和“跨 segment 硬约束”这些可能决定收入的 Base 参数，与“shock each base parameter”的设计目标不完全一致。
- 明确设计限制：敏感性只允许直接被 Base 路径引用的 assumption/stress；若 assumption 先进入 derived fact，再由 derived fact 进入模型，该 assumption 不在 `base_refs`，而 derived fact 又不是可测试 kind，因此派生链敏感性无法自然传播。
- 纯度问题：`calculate_sensitivities` 会就地给缺少 `name` 的测试字典写入名称。`run_forecast` 已在此前计算 `input_sha256`，这导致调用者传入对象在哈希后被突变；虽未直接改变正式计算值，但破坏函数纯度和快照心智模型，应改为局部 normalized copy。

## 置信度、来源覆盖与增长驱动辅助图

- 置信度由 claim quality/coverage、freshness、explicit-model share、immutable backtest 和 sensitivity coverage 构成；增长幅度没有参与，研究/识别/情景等作为已通过的 quality gates，方向正确。
- 置信度权重把一个 segment 终值平均分配给其所有引用参数，这是可解释的简化启发式，但并非真实弹性或边际贡献；周期更长、参数更多的模型会机械稀释单参数权重，跨模型比较时要谨慎解释。
- `parameter_revenue_weights` 同样遗漏 revenue constraint 参数，因此约束即使决定 effective revenue，也不会进入 claim coverage 或 sensitivity coverage 的权重；这与增长驱动 helper（后者明确包含 constraints）不一致，是跨模块口径漂移。
- `validate_source_coverage` 能识别 source `covers_until` 早于 forecast parameter period，但全仓调用只出现在它自己的测试里；`validate_document`、`run_forecast` 和 confidence 均未消费其结果。因此用户可提供已过覆盖期的来源而正式预测仍通过，这是“有检查器但没有接入强制工作流”的明确缺口。
- 增长驱动的 Base parameter helper 比敏感性更完整：会展开 derived inputs，并把 recognition progress、carry-in、forecast adjustments 和 constraints 都纳入；segment 归因也把 constraint 参数映射到受影响 segment。
- `validate_base_reconciliation` 对未知 `base_adjustment_parameter_id` 直接索引，可能抛 `KeyError` 而非受控 `ForecastInputError`；仍会阻断输出，但 CLI 错误处理与失败消息不稳定。它也未显式禁止重复 adjustment ID。

## 研究覆盖、驱动树与管理目标强制性

- `validate_document` 对 current schema 明确调用 `validate_sources(..., require_capture=True)`；capture receipt 并非可选，这一点实现与契约一致。
- 九维研究记录的“结构完整”被硬强制，但“研究已完成”不是：每一维可声明 `data_gap` 或 `immaterial` 后继续正式出数。增长驱动树甚至允许整个 `status="data_gap"`、零 drivers 仍生成正式 forecast。它会公开 limitation，但不能防止调用者用泛化理由跳过实质研究。
- `growth_driver_tree=data_gap` 时 analysis 的 driver attributed increment 固定为 0，reconciliation difference 通常非 0；这说明该降级路径刻意允许不归因，而不是 hard fail。与 `SKILL.md` “缺少 modeled growth-driver tree 阻断”的表述存在明显张力。
- 自定义 research dimension 的 validator 未要求 `dimension` 是非空字符串；首次出现的 `null`、空字符串或任意对象可越过 line 1991/1992 的检查并进入正式输出。核心九维不受影响，但扩展接口不够 fail-closed。
- 管理沟通六类别和 target ID 全等关系被硬强制；material + in-horizon + comparable 目标必须进入 scenario，annual/run-rate/cumulative 的 measurement arithmetic 也会重算。
- 但“搜索完整性”依赖调用者自报：所有 communication category 都可声明 `not_available`/`not_applicable` 并提供文字 rationale（`not_available` 再加文字 search_description），没有 host-signed 搜索记录；这属于无法仅靠 JSON runtime 证明的信任边界。
- 目标 lineage 存在弱绑定：`mapped_parameter_ids` 只需是任意已进入 forecast 的参数，未检查它们影响目标 scope、measurement periods 或 `mapped_scenarios`，也未检查 parameter scenario 与 mapped scenario 一致。只要最终 company/segment 数值碰巧满足目标，调用者可挂接无关参数 ID 并通过。
- target claim 的 source 不要求属于引用该 target 的 communication record 的 `source_ids`；目标和沟通类别在 ID 层相连，但来源层未闭环。

## 输出独立验证的关键缺口

- 高严重度回归：输入 validator/changelog 允许九个核心维度之外的 custom research dimensions，但 `validate_forecast_output` 强制 `len(dimensions)==9` 且顺序恰为九个核心维度。任何 custom dimension 都会在正式 CLI 的第二道门失败，v3.9 声明的资源行业扩展实际上不可正式交付。
- 输出 validator 的禁止字段扫描只递归 `consolidated_forecast`、`confidence`、`theme_analysis`、`probability_weighted_forecast`、`growth_driver_analysis`，没有递归 segments、research、management targets、parameter/source/claim traces 等。由于输入对象普遍允许 extra keys，非收入字段可嵌入未扫描区域并进入正式 JSON，scope boundary 不是全树 fail-closed。
- 概率输出只重算 weighted arithmetic，未重新检查概率非负、三项齐全、和为 1、rationale/claim；一个被重新哈希的变造 artifact 可带无效概率仍通过 output validator。
- 管理目标 output validation 重算了 modeled value 和 ratio，但没有根据 `comparison` 与 tolerance 重算 `meets_target`，只要求存储值为 `true`；它也没有重验 perimeter、material in-horizon treatment、mapped parameter relevance 或 claim raw value。其“独立重算 attainment”声明强于实现。
- 敏感性 output validation 只从存储的 down/up terminal 重新计算 max impact/relative impact，未按 shock 重新跑模型，也未验证 requested/effective/clamp 或 parameter kind/path；被重新哈希的变造 artifact 可伪造整组终值并自洽通过。
- result/workflow 哈希提供防意外突变的内部一致性，但没有签名；当攻击者能同时重算字段和哈希时，必须依靠上述独立语义重算。当前恰在概率、目标 attainment 和敏感性处存在语义重算缺口。

## Constraints 与回测

- `revenue_constraints.py` 是相对独立、严格的模块：每种 constraint 拒绝 extra keys，验证 segment、scenario/year/dimension/sign、固定权重和为 1，并按声明顺序应用且生成 before/adjustment/after audit。
- 轻微接口漂移：constraints 接受 parameter scenario `"shared"`，但输入文档只描述 `low/base/high/all`；核心 `validate_parameters` 本身未枚举校验 scenario。跨模块可接受值应统一注册。
- 高严重度快照缺陷：`calculate_sensitivities` 的原地 auto-name 突变与 `create_snapshot` 的哈希时序组合后，会产生自相矛盾快照——forecast result 的 `input_sha256` 在突变前计算，snapshot `input_sha256` 在突变后计算，随后 `validate_snapshot` 必然失败。
- 长期回测兼容性缺陷：`validate_snapshot` 要求 snapshot `engine_version == 当前 ENGINE_VERSION`。技能每次 minor release 后，旧 snapshot 即使其 forecast output 属于受支持 legacy schema/engine，也无法再评估；这与“immutable historical snapshots、跨期回测”目标直接冲突。
- actuals evidence 比 forecast 弱：`validate_actuals` 调用 `validate_sources` 时未启用 capture，actual claim 只要求 64 字符 content hash，不要求 lowercase hex、capture receipt 或与 source snapshot 相等。由此生成的 hash-linked accuracy record 可进入未来 confidence，但其原始实际值证据没有 schema-3.4 同等级的捕获绑定。
- segment backtest 使用 `recognized_revenue`，忽略 constraints 后的 `effective_revenue`；有 elimination、sum cap 或 linked ratio 时，company forecast 与 segment accuracy 使用不同收入口径。

## 现有测试基线

- `python -m unittest discover -s tests -v`：158 个测试全部通过，约 5 秒。
- 覆盖面较好：全 23 个模型、负向数据契约、capture/claim、识别、constraints、driver tree、targets、output tamper、snapshot/backtest、CLI 端到端均有测试。
- `test_filing_acquisition` 的 HK/US 外部进程测试出现 2 个 `ResourceWarning: unclosed file`，说明 dayu CLI subprocess pipe 生命周期仍有资源泄漏；测试未将 warning 升级为失败。
- 当前 suite 没有覆盖：custom research dimension 的 formal output、auto-named sensitivity snapshot、自旧 engine snapshot 的后续评估、actuals capture binding、constraint-aware segment backtest、output validator 的语义重哈希攻击。
- `tools/tests` 另有 4 个安装同步测试，全部通过；主测试 discovery 不会自动包含这 4 个，完整基线为 162 个测试。

## 安装一致性

- 同步检查器确认 canonical repo 与 `C:\Users\郑曾波\.agents\skills\revenue-forecast` 完全一致（38 files）。
- 对 `C:\Users\郑曾波\.codex\skills` 运行同一检查器返回 `<missing installation>`；PowerShell 进一步确认 `.codex\skills` 存在但其 `revenue-forecast` 子目录不存在。当前技能 catalog 同时列出一个不存在的 `.codex` locator，属于环境/catalog 陈旧重复，不是 canonical repo 代码漂移。

## Filing acquisition 配置层

- 配置 schema 严格拒绝 extra/missing fields，company-wiki root 必须真实存在，staging 必须解析到该 root 内，timeout 必须为正，adapter 必须恰为 CN/HK/US。
- token 展开仅允许明确定义的 `${SKILL_ROOT}`、`${USER_PROFILE}`、`${PYTHON_EXECUTABLE}`、`${CONFIG_DIR}`、`${COMPANY_WIKI_ROOT}`；路径统一 resolve，避免 prompt/代码硬编码机器路径。
- CN interface 被固定为 `json_command_v1`，HK/US 固定为 `dayu_cli_v1`；显式拒绝 adapter command 调用 `company_wiki.source_catalog`，落实“company-wiki 仅作为数据根，不导入/启动其代码”。
- Adapter project/config root 在配置加载时只解析、不要求存在；这允许 read-only reuse 在下载工具未安装时继续工作，是合理的延迟依赖策略，下载阶段需再 fail closed。

## Filing identity 与请求层

- Fuzzy `company_query` 路径严格：NFKC/casefold 归一化，读取本地 CN/HK/US security-master snapshot，exact match 优先；fuzzy 需 ≥0.90 且领先第二名 ≥0.03，随后强制 active、HTTPS provenance，并冻结 canonical market/security ID。
- Fuzzy 查询显式禁止同时传 `entity` 或 `security_id`，避免调用者先入为主污染解析；ambiguous/missing/inactive 均在任何 source lookup/adapter 前失败。
- 但显式请求路径 `entity + market + security_id` 不经过 security-master 验证，且 `SourceRequest` 允许 market/security_id 为空。独立 `filing-fetch` 契约把显式 identity 视为可接受输入，但从“防止工具偷工减料”角度，agent 可故意不用 `company_query` 绕过 verified-active identity gate。
- Security-master 文件只验证基本 schema/market/record 字段，没有验证 snapshot 自身发布日期、hash 或签名；身份来源 URL 会进入返回 identity，但本地 master 的 freshness/immutability 属于外部治理责任。

## 本地文档复用实现

- `FilesystemSourceResolver` 明确从 `${company_wiki_root}/companies/{entity}/**/*.source.json` 开始扫描，并兼容 `.source_catalog/revenue-forecast/aliases`；不存在 companies 目录时返回 miss，不触发任何下载。
- 匹配会核对 entity、document kind、可选 market/security/fiscal year/period/form/language/provider/document ID，拒绝 as-of 之后的 filing/capture。
- 复用不是“只信索引”：resolver 将 canonical path 限制在 company-wiki root 内，重算文件 SHA-256、核对 byte size、HTTPS source URL、retrieved timestamp 和 sidecar metadata；缺失、篡改或 identity conflict 都 fail closed。
- 多个匹配若字节 hash 相同则稳定返回第一条；若内容不同则拒绝自动选择，避免静默挑错 amendment/version。
- CN `JsonCommandAdapter` 使用结构化 JSON stdin/stdout、固定 schema/status/adapter identity/version、`shell=False`、request-specific staging 参数和超时；确实是在调用 StockInfoDLSimple 的版本化 CLI，而非复制其下载逻辑。

## HK/US dayu adapter

- Dayu adapter 只允许 HK/US，要求 security ID + fiscal year，按 HKEX/SEC 文档类型映射 forms，并通过 `dayu.cli download` 写入独立临时 workspace；不 import、不修改 dayu-agent。
- 它从 Dayu `meta.json` 选择 HK 原始 PDF或 US primary document，核对 provider、form、fiscal year、as-of、source URL、文件 SHA-256/size，并再次复制到 request-specific staging 后复核 hash/size。
- 现有 ResourceWarning 根因清晰：`Popen(... stdout=PIPE, stderr=PIPE)` 在成功/早停路径 `wait/kill` 后没有关闭两个 pipe；`close()` 只清 workspace。属于资源管理缺陷，长批处理可能积累句柄。
- `discover()` 本身执行 dayu 的 download 命令，因此授权门必须位于调用 `discover` 之前；manager 顺序将决定“默认只读”是否真实，下一步核对。

## Canonical write、dedup 与授权顺序

- Manager 顺序正确且硬编码：normalize/identity → `FilesystemSourceResolver.resolve` → 若命中立即返回 `reused_before_download` → 若 miss 且无 `allow_download` 则失败 → 只有授权后才构造 adapter 并调用 `discover/fetch`。
- 因此默认命令是严格只读；`--allow-download` 位于 CLI 层并传入 manager。运行时能证明 flag 存在，但不能证明该 flag 来源于用户本人授权，这仍依赖 host/agent 行为。
- 下载时再次要求 market + security ID、恰好一个 candidate、candidate identity 一致，然后只允许 request-specific staging。
- Writer 强制 staged path 位于 request staging，重算 size/SHA-256，PDF 还检查 magic bytes；随后 exact-hash 全库去重。
- 新文件的目标路径明确为 `${company_wiki_root}/companies/{safe_entity}/raw/{financial_reports/...}/{filename}`，并写同目录 immutable `.source.json`；跨公司相同字节用 `.source_catalog/revenue-forecast/aliases` 指向唯一 raw，满足文档复用与 canonical storage 要求。
- Raw 与 sidecar 采用临时文件 + `os.replace`，sidecar commit 失败会删除刚写 raw；sidecar 冲突拒绝覆盖。此处实现质量较高。
- 但 manager 的 “explicit download requires verified market and security_id” 只验证字段非空；若调用者走 explicit identity 旁路，未经过 security master 也会被称为 verified。应把 verified identity token/receipt 纳入 request contract，或明确把 explicit path 标为 trusted override。

## Invest suite 书面协作契约

- 所有权矩阵清晰且合理：revenue 唯一拥有收入路径/识别/情景/CAGR/目标/增长驱动/回测；financials 只推利润现金流；moat/management/distribution 各自定性边界；valuation/SOTP/compare 只消费已验证上游。
- 依赖方向和 artifact lineage 设计成熟：`revenue-forecast → invest-core → leaf → framework`，scenario manifest、target summary、growth-driver summary 和 upstream hashes 均不可变传递。
- Segment adapter 明确优先消费 revenue-owned `effective_revenue`，旧 schema 才回退 `recognized_revenue`，与 constraints 的所有权边界一致。
- Framework 要求 manifest 覆盖每个 revenue segment 恰好一次、定量依赖不可跳、全部叶子先在内存验证再原子发布，能有效防止下游重算或漏 segment。
- 但 invest-core 文档声称 revenue output validator 会独立重算 sensitivity、management-target attainment 等；本审查已实证这些部分只做局部算术检查。下游 revenue reference 先调用该 validator，因此会继承其“验证强度被高估”的问题。

## 与独立 filing-fetch 的重复与冲突

- 独立 `filing-fetch` 是约 419 行 thin client，调用 `company_wiki.source_catalog.cli identify/resolve/ensure`；company-wiki 自己负责索引查询、路由、去重和落盘。
- revenue v3.10 的 `filing_acquisition.py` 是约 2080 行自包含重实现，不调用 company-wiki 代码，只扫描 filesystem sidecars，并直接编排 StockInfoDLSimple/dayu、dedup 和 canonical writer。
- 两者不只是“相邻模块”，而是同一业务能力的两套 owner：identity、reuse-first、authorization、market routing、capture-ready handle 和 canonical storage 均重复，且配置 schema/runtime 依赖不同。Changelog 显示 v3.8 曾抽出、v3.10 又回迁，架构方向发生反转。
- 这造成正式指令冲突：`filing-fetch` 声称 revenue/invest 应使用它；revenue SKILL 又要求先用 bundled acquisition。Agent 触发两个技能时没有唯一仲裁规则，测试也不能保证两套语义长期一致。
- 对用户第 4 点需精确表述：v3.10 确实“先查本地已有文档”，但它查的是 `company-wiki/companies` 下 sidecar 文件树，不是 company-wiki 的真实 catalog/index API。若索引含有未按该 sidecar 约定落盘的可复用文档，bundled resolver 可能漏命中并建议下载。
- 推荐的架构应只保留一个 acquisition owner：要么独立 `filing-fetch` + company-wiki index 是统一入口；要么把当前 standalone runtime 下沉为共享库/CLI，供 revenue、invest 和 filing-fetch 都调用，而不是复制。

## Invest runtime 结构盘点

- `invest-core` 的 `invest_contracts.py` 约 1400 行，集中 runtime discovery、revenue adapter、scenario manifest、source/claim/parameter contract、management/moat qualitative schema、artifact envelope/hash/compliance 和 CLI；与 revenue core 类似，逻辑函数化但文件级职责过度集中。
- 各 leaf 的定量公式总体独立：financials 359 行、distribution 156、valuation 521、SOTP 246、compare 304；moat/management 主要通过 invest-core 的 qualitative finalizer，没有另建收入计算器。
- `invest-core` 重复实现 canonical hash、restricted formula evaluator、URL/source/claim/parameter validation。部分重复是跨 artifact contract 所需，但 capture/evidence 基础原语应考虑抽成唯一 shared contract package，防止 revenue 与 invest 对同一概念产生版本漂移。
- Revenue adapter 测试已覆盖 company/segment、effective path 优先、forecast tamper、management-target summary 和 growth-driver summary/hash；下一步核对实现是否只复制而不重算。

## Invest-core runtime discovery 与 revenue reference

- `revenue_runtime()` 通过定位 skill 目录、把 scripts 插到 `sys.path` 后执行 `import_module("revenue_core")`。它没有验证已载入模块的 `__file__` 属于所选 skill；若进程先加载了另一份同名 `revenue_core`，Python `sys.modules` 会静默复用错误版本。多安装/测试宿主中存在 version confusion 风险。
- Revenue reference 首先调用 revenue output validator，然后只复制 schema/engine/input/result hash、workflow receipt hash、完整 target block hash/compact summary、完整 driver analysis hash/compact summary；没有重算收入，所有权边界实现正确。
- 当前/legacy 状态区分合理：只有 runtime 当前 schema + workflow receipt 才标 `current_validated`，旧 schema 保留 `legacy_read_only_validated`。
- Scenario manifest 可在调用者未提供时自动生成通用 low/base/high 文本。虽然有 hash，但定义过于空泛，不能证明下游场景在经济含义上与 revenue 的 low/base/high 一致；framework strict manifest 是否覆盖这一点需继续核对。

## Revenue adapter 与 leaf 边界

- `adapt_revenue` 先创建已验证 reference，再按 company 复制 consolidated annual revenue，或按 segment 优先复制 `effective_revenue`；不含公式、不接受 override，符合唯一收入 owner 原则。
- Reference validators 对 target/driver summary 字段、hash、ID、rank、direction、period semantics 和 reconciliation shape 做了严格检查，但 target 只要求 `meets_target` 是 bool，并不重新判断真假；SOTP 又明确只消费该 bool。因此 revenue output validator 的 forged-attainment 缺口会完整传导到 valuation/SOTP/framework。
- Leaf SKILL 职责整体清晰、重复较少：financials 只做利润/现金流 DAG；moat 引用 driver 不重排；management 只评估执行；distribution 只算资本分配；valuation 不重建 revenue/profit；SOTP 纯聚合；compare 只对齐已验证 artifacts；psychology 完全 DAG 外置。
- 交叉边界也写得具体：management 不重算资本分配，moat 不把标签变估值溢价，valuation 不把 driver rank/management target 变默认参数，SOTP 不重算 segment，compare 不重新研究。未发现 leaf 之间明显的第二套收入模型。
- 主要重复集中在基础设施而非业务公式：evidence/capture/hash/parameter contract 在 revenue 与 invest-core 各一套；filing acquisition 在 revenue 与 filing-fetch/company-wiki 各一套。

## Framework 强制编排实现

- Manifest identity 必须与 frozen revenue forecast 的公司、日期、币种/单位、财年和预测期完全一致；required constraint IDs 必须按顺序等于 revenue constraints。
- Manifest segments 必须与 revenue segments 集合和数量完全一致；每个 segment 必须声明 financial + valuation，SOTP selection/ownership 也必须覆盖全部 segment。
- Scenario policy 强制 exactly low/base/high 且每个有定义，并转成唯一 hashed scenario manifest 注入所有 financial/valuation/bundle；下游一致性强，但 policy 仍是用户声明，未与 revenue 内的具体假设语义做机器映射。
- Full-company bundle 不能把 financials/valuation/SOTP 降为 optional；supplemental management/moat/distribution 的 required/optional 与 artifact ID/hash/scope 均由 manifest 冻结。
- Orchestrator 先 deepcopy forecast 并验证，在内存依序运行每个 segment financials → valuation → SOTP → bundle，随后要求 bundle revenue ref 精确等于 frozen forecast reference，再由只读 renderer 生成 report 和完整 state-transition receipt。
- 综合判断：`revenue-forecast` 与 invest-* 的协作架构是本项目最成熟的部分；核心弱点不是重算收入，而是 revenue 自身 validator 的语义缺口会被“可信 reference”放大，以及 runtime import/version confusion。

## 跨技能测试基线

- `invest-core`：29/29 tests 通过，包含 current capture、artifact receipt、legacy contracts、revenue adapter、effective path、target/driver transfer。
- `invest-framework`：22/22 tests 通过，包含 heterogeneous segments + constraints + SOTP 端到端、hash drift、segment coverage、secret rejection、atomic output、state transition 和 freeform report override。
- 这 51 个跨技能测试证明当前 revenue v3.10 / invest suite 5.2 在正常路径上兼容；它们没有覆盖已复现的 revenue forged probability/target/sensitivity 语义攻击，因此“adapter 通过”仍依赖上游 validator 的真实强度。
- 8 个 leaf 技能另有 55/55 tests 全部通过（financials 9、moat 4、management 5、distribution 4、valuation 11、SOTP 6、compare 9、psychology 7）。

## 泛化与硬编码扫描

- 核心 model registry、core、report、backtest、constraints 和 acquisition 没有公司名称分支；23 模型按 driver identity 工作，跨公司/行业泛化总体良好。
- 唯一公司硬编码集中在 `scripts/run_forecasts.py`：完整内置腾讯和微软输入、claims、研究文字及输出名。它不被正式 SKILL workflow 引用，但放在 `scripts/` 顶层容易被误认为正式运行器；应移动到 `examples/` 或测试 fixtures，并标明非正式示例。
- 正式核心没有 `if/elif model` 公式 dispatcher；只有 `retail_franchise` 可选字段成对约束这一处 model-specific schema rule。
- 无 TODO/FIXME/HACK/NotImplemented 残留。
- 配置没有用户绝对路径，但 dayu command 写死 Windows `.venv/Scripts/python.exe`，且假设 company-wiki、dayu-agent、StockInfoDLSimple 是相邻项目目录。前者是明显平台耦合；后者可编辑但部署拓扑假设较强。对“模块泛化”而言，业务泛化强、环境泛化中等。

## 静态质量

- `python -m compileall -q scripts tests tools` 通过。
- 全量 Ruff 仅在 `scripts/run_forecasts.py` 报 4 项：unused import、2 个 import-order、无占位符 f-string；排除该公司示例脚本后，所有正式 scripts/tests/tools 静态检查通过。
- 这进一步支持把 `run_forecasts.py` 移出正式 `scripts/`：它同时是唯一公司硬编码源和唯一 lint 不洁净文件。

## 测试覆盖率

- 主 suite 在 `--source=scripts` 下 statement coverage 为 84%。
- 核心模块覆盖较强：`revenue_core.py` 96%、`revenue_constraints.py` 96%、`model_registry.py` 89%、`revenue_backtest.py` 88%、`revenue_report.py` 85%。
- `filing_acquisition.py` 77%，大量异常分支、真实 CLI failure/timeout/cleanup 路径未覆盖；这与已出现的 pipe ResourceWarning 相符。
- `revenue_forecast.py` 在 coverage 中为 0%，因为 CLI 测试通过子进程执行、未被当前 coverage process 跟踪；并不代表 CLI 没测试。`run_forecasts.py` 也为 0%。
- 高 statement coverage 没有捕捉本审查复现的语义缺口，说明下一步应增加 mutation/adversarial contract tests，而不只是继续提高行覆盖。

## Required workflow 强制性矩阵

| 步骤 | 运行时强制程度 | 主要缺口 |
|---|---|---|
| 0 九维覆盖 | 结构硬门 | 可把全部实质问题声明为 data gap/immaterial；custom type 与 output 不一致 |
| 1 信息集冻结 | 强 | 工具调用真实性和来源完整性仍由 host 保证 |
| 1A 管理沟通/目标 | 中强 | 六类别结构强；not_available/not_applicable 可自报，mapped parameter 与 scope/scenario 弱绑定 |
| 2 历史/base | 强 | 未知 base adjustment 可能抛 KeyError；segment base kind 未显式限制为 fact |
| 3 来源/参数/claim | 强结构、弱真实性 | capture/hash/date 强；tool_call_id/manual_open 可自报，assumption claim support 类型未强制 |
| 4 收入曲线拆分 | 中 | 至少一个 segment、模型 schema 强；“经济上应拆分几条”无法机器证明 |
| 5 收入确认 | 强 | policy claim、timing/trigger/presentation/progress/lag 均硬门 |
| 6 三情景 | 强结构 | 同模型、driver/rationale/order 强；rationale 经济合理性无法验证 |
| 6A 因果驱动树 | 可降级 | modeled 时很强，但整个树可设 `data_gap` 后继续正式出数 |
| 7 聚合/bridge | 强 | 模型→确认→constraints→公司 bridge/增量均重算 |
| 8 敏感性/theme | 弱到中 | sensitivity 可完全省略；遗漏 progress/constraint/derived-chain；output 不重跑 shock |
| 9 置信度 | 强计算 | 权重是平均启发式且遗漏 constraints |
| 10 验证/交付 | CLI 路径强，函数路径可绕 | `run_forecast` 在 output validation 前就签发 pass receipt |
| 11 冻结/回测 | 可选且有缺陷 | auto-name snapshot 自失效；同 schema 旧 engine 不兼容；actuals capture 较弱 |

## Workflow receipt 的实质缺陷

- `run_forecast` 直接调用 `build_workflow_compliance_receipt`，receipt 固定写入 `status="pass"` 和 `gate_ids` 中的 `output_recomputation`，但此时 `validate_forecast_output` 尚未执行。
- CLI 确实在下一步调用 output validator，但任何直接 Python 调用都可拿到带 pass receipt 的未验证 result；custom-dimension 复现已经产生“receipt pass、随后 output validator fail”的实际例子。
- 因此 receipt 当前证明的是“输入运行时完成”，不是它声称的“完整 formal-output 路径完成”。应由 CLI/finalizer 在 output validation 成功后签发最终 receipt，或拆成 input execution receipt + publication receipt。

## 最小复现结果

- Custom dimension：`run_forecast` 接受 `research_coverage += reserves`，但紧接着 `validate_forecast_output` 抛出 `research_coverage output must contain nine dimensions`，正式 CLI 必然失败。
- Auto-name snapshot：为合法 Base 参数添加不带 `name` 的 sensitivity，`create_snapshot` 可返回对象，但随后 `validate_snapshot` 抛出 `forecast result input fingerprint mismatch`。
- Scope bypass：在已验证 result 的 `parameter_trace[0]` 嵌入 `valuation=123` 并重算 `result_sha256` 后，`validate_forecast_output` 通过，确认禁止字段扫描并非全树。
- Probability bypass：把有效结果改为 `{low:2, base:0, high:0}`（和为 2），同步重算 weighted path 与 result hash 后，`validate_forecast_output` 通过，确认没有独立概率契约复验。
- Target bypass：把有效的 144 目标在 output 中改为 1000，保留实际 modeled value、重算 attainment ratio、强行设置 `meets_target=true` 并重算 result hash 后，output validator 通过；确认它没有执行 comparison/tolerance 判定。
- Sensitivity bypass：把合法 sensitivity 的 down/up terminal 改为 1/999，仅同步重算 max impact/relative impact 和 result hash 后，output validator 通过；确认没有重新运行 shock。
- 现有 `test_parameter_trace_custom_key_is_not_prohibited` 甚至明确允许在 parameter trace 内嵌 `profit`。这可能是为了保留来源词汇，但实现没有区分“引用文字/定义”与“正式投资结论字段”，因此 arbitrary structured valuation data 也被同样放行。
- Source-linked assumption：把其 claim 从 `rationale_support` 改为带匹配 value/unit/period 的 `exact_value`，完整正式 forecast 仍通过，确认契约偏差。
- Source horizon：给全部来源设置 `covers_until=FY2025`，预测 FY2026–2027 仍通过正式 output validation，确认 coverage checker 未接线。
- Custom dimension type：追加 `dimension=null` 的 data-gap record 后 `validate_document` 通过，确认 custom extension 未做字符串类型约束。
- 版本兼容：把当前 schema-3.4 artifact 的 engine 改为 3.9.0 并重哈希后，validator 直接报 engine mismatch。由于 v3.5–v3.10 都使用 schema 3.4，旧 3.4 forecasts/snapshots 会在每次 skill release 后失效；不仅是 snapshot 层问题。

## 2026-07-28 — Phase 1.1 基线冻结发现

### 发现：基线并非审计所述的 158/158（plan drift，已修）

- 实跑 `python -m unittest discover -s tests` 在修复前为 **158 tests, errors=2**，与 findings 旧记录"158 个测试全部通过"不符。审计当晚（2026-07-26）确实通过，但测试是**时间相关**的，两天后即失败。
- 失败的是 `test_hk_and_us_dayu_cli_contracts_run_in_external_processes`（HK/US），报 `new canonical source did not resolve`。
- 根因链（均已读源码确认）：
  1. `FilesystemSourceResolver._load`（`scripts/filing_acquisition.py:1046-1055`）强制 `filing_date <= captured_date <= request.as_of_date`，否则返回 `(None, False)` → `resolve` 返回 None。
  2. `CanonicalSourceWriter.import_staged`（`:1908-1910`）写完 canonical 后调用 `resolver.resolve(request)`，None 即抛 `FilingAcquisitionError("new canonical source did not resolve")`。
  3. dayu 真实子进程 adapter 在 `:1608` 用 `retrieved_at=_utc_now()`（真实当前 UTC，`_canonical_utc`/`datetime.now(UTC)`，`:120`）。
  4. `tests/test_filing_acquisition.py:_request` 把 `as_of_date` 硬编码为审计日 `"2026-07-26"`（`:146`）。
  5. 审计当天 `now(2026-07-26) <= as_of(2026-07-26)` 边界成立 → 通过（仅 2 ResourceWarning）；今天 `now(2026-07-28) > as_of` → 越界失败。
- 对照：`_FakeAdapter.fetch` 用固定 `retrieved_at="2026-07-26T12:00:00Z"`（`:88`），`_existing` 用 `"2026-07-01T..."`（`:183/:204`），均为固定历史值，故其余 ~14 个 filing 测试不受时钟影响。`test_capture_after_as_of_is_not_reused`（`:678-689`）自行把 as_of 覆盖为 `"2026-06-30"`，独立于默认值。
- 修复（test-only）：`_request.as_of_date` 改为 `(date.today()+timedelta(days=7)).isoformat()`。7 天余量吸收本地/UTC 时差。未改任何断言、未改生产代码、未放宽检查；属合法 test fixture 维护，与 0.3 规则 6 禁止的"改写失败测试以掩盖实现缺陷"截然不同。
- 影响：此 bug 与 Phase 1 的 4 类 publication/validation 绕过无关（那些在 `revenue_core`/`revenue_report`），但必须先修才能满足 1.1「结果与审计一致」与 1.3「原有测试全绿」检查点。dayu pipe 的 2 个 ResourceWarning 仍存，留待 Phase 9。

### 发现：计划"268 项基线"是跨仓库合计

- `task_plan.md` 多处引用"268/268 测试基线"，但 revenue 本地实跑为 158（tests/）+ 4（tools/tests）= **162**。
- 268 = 162（revenue）+ 29（invest-core）+ 22（invest-framework）+ 55（8 个 leaf 技能）跨仓库合计，对应 Phase 11/13 的跨技能验收。
- Phase 1 只修改 revenue-forecast，因此 Phase 1 的有效基线是 **162/162**；后续阶段跨仓库时再各自跑。

## 2026-07-30 — 实施后审查：画蛇添足判定

实施全 13 Phase 后发现，审计建议不等同于实施任务。以下原计划子项经代码验证判定为过度工程：

### 9.5 Atomic company-wiki commands

审计建议 "resolve 使用一个命令: --company-query 直接"。已验证 `resolve --company-query` 原子命令可用（real-tool conformance test），但**不采用**。原因：`identify`→`resolve` 两步是 thin client 的正确契约边界——`identify` 显式验证身份（market/security_id/verified/active），`resolve` 按已验证身份查询。合并为原子命令使 filing-fetch 假设上游 internal response format（`identity` + `source_resolution` 嵌套），违反薄客户端原则。

### 9.6 Gap/authorization receipt

审计建议 "bare boolean allow_download 不够，要结构化 gap receipt + authorization receipt with request hash/expiry/scope"。**不采用**。原因：`allow_download` boolean 是薄客户端正确的最小授权——filing-fetch 本身不执行下载，它委托给 company-wiki。结构化 receipt 需要 host 签名才能不可伪造（= Phase 8 同款 infra 边界），本地构造只是自欺欺人。

### 10 全 11 模块提取

审计建议 revenue_core.py（~2300 lines）拆为 11 个子模块。**仅提取无循环依赖的 contracts/evidence.py（~200 lines）**。原因：提取 forecast/compute.py 时触发循环 import（_run_forecast_core ↔ calculate_sensitivities ↔ _run_forecast_core），已尝试并 git revert。剩余 9 个子模块的依赖图是单向的：_run_forecast_core → all，无法在不创建 cycle 的前提下移动 leaf functions。

### 11.3/11.4 Scenario/constraint de-dup

审计建议 "scenario manifest 绑定 revenue publication receipt" 和 "list all duplicate primitives"。**已完成**。前者通过 `publication_receipt_sha256` 在 `revenue_reference` 中实现（invest_contracts.py:617-626）。后者通过 7 个 cross-skill conformance tests（test_cross_skill_conformance.py）证明两 repo 的 `canonical_sha256`/`text_sha256`/JSON round-trip 一致。

### 真正的残余

| 残余 | 类型 | 操作 |
|---|---|---|
| invest-framework 2 skips | 跨 repo fixture gap | 标记 skip，不影响 production |
| invest-core 1 skip | superseded by publication gate | 标记 skip |
| filing-fetch 2 flaky skips | company-wiki 状态依赖 | 标记 skip |
| Phase 8 host-signed receipt | trusted agent infra 边界 | 结构化字段已就位，真实验证需运行时配合 |

---

## 2026-07-30：恒运昌 (688785) 从零构建输入实战分析

- 来源：恒运昌营收预测全流程（23 次 exit code 2，最终第 25 次成功）
- 输入规模：6 sources、29 claims、27 parameters、2 segments、5 growth drivers、3 sensitivities
- 最终结果：Base FY2028 97,663 万 (CAGR 22.6%)，置信度 Medium (60.6/100)

### 发现 A：23 次失败的三类根因

```
Schema 字段不匹配  ████████████████  15次 (65%)
跨引用完整性失败  ██████            6次 (26%)
哈希自洽性失败    ██                2次 (9%)
```

**15 次字段问题**的核心是 schema 3.5 有大量反直觉命名约定，无一能从文档独立推测：

| 约定 | 直觉写法（错误） | 正确写法 |
|---|---|---|
| Capture 版本字段 | `schema_version` | `capture_schema_version` |
| Capture 日期字段 | `capture_date` | `captured_date` |
| Prompt 注入状态 | `none_detected` | `not_detected` |
| 历史数据 target_id | `history_2022` | `historical_revenue:2022` |
| 收入确认 target_id | `recognition_policy` | `recognition:segmentName` |
| 收入确认 support_type | `rationale_support` | `policy_support` |
| 敏感性字段名 | `shock` | `shock_type` |
| percentage_point 参数 | `down_value/up_value` | `shock_value`（正数） |
| derived_fact | 仅 `x0/x1/formula` | 还需 `input_parameter_ids` |
| not_available 沟通 | 仅 `rationale` | 还需 `conclusion/checked_date/search_description` |

**6 次引用完整性失败**暴露了 claim↔parameter↔source 的严格双向约束——一个 claim 只能有一个 `target_type`+`target_id`，如果同一事实既要支撑参数又要支撑增长驱动证据，必须创建两个独立 claim。

**2 次哈希失败**源于 schema 3.5 的四层哈希引用环（source.snapshot → claim.content → source.capture.receipt → claim.capture_receipt），手工维护在每次编辑后都不可行。

### 发现 B：fail-fast 是最直接的效率瓶颈

21 个独立验证函数每个都在第一个违规处 `raise ValueError`。23 次往返 ÷ 3 类错误 = 如果一次报告所有违规，理论上 2-4 次往返即可完成。

### 发现 C：引擎内置的 21 个验证函数覆盖完整

```
validate_document()                      ← 入口
├── validate_top_level()                 ← schema_version, 基本字段
├── validate_sources()                   ← source结构+page_or_section
├── validate_source_capture()            ← capture对象+receipt hash
├── validate_evidence_claims()           ← claim结构+excerpt hash
├── validate_claim_ids()                 ← 跨引用完整性 ← 最多次触发
├── validate_parameters()                ← 参数类型/公式/场景
├── validate_historical_revenue()        ← 历史数据+连续性
├── validate_base_reconciliation()       ← 基期对账
├── validate_research_coverage()         ← 九维研究覆盖
├── validate_management_target_coverage() ← 管理层沟通
├── validate_growth_driver_tree()        ← 增长驱动树（含4个子验证）
├── validate_recognition_metadata()      ← 收入确认元数据
├── validate_revenue_constraints()       ← 跨分部约束
├── validate_scenario_probabilities()    ← 情景概率
├── validate_source_coverage()           ← source引用完整性
└── validate_historical_accuracy_records() ← 历史回测记录
```

这些函数的逻辑正确，不需要修改。改进方向应该是报错模式（fail-fast → collect-all）而非验证逻辑。

### 发现 D：direct_growth 模型的置信度代价

恒运昌两个 segment 都用了 `direct_growth`（缺乏公开出货量/产能数据），这直接导致 `revenue_weighted_explicit_models` = 0.0/20，总置信度被拉低至 60.6/100（Medium）。引擎正确地惩罚了缺乏运营因果解释的模型选择，这是设计意图而非缺陷。

---

## 2026-07-31 紫金矿业档案获取会话发现

> 触发：`/revenue-forecast 紫金矿业` 获取 FY2025 年报。会话日志见 `progress.md` 2026-07-31 段；修复计划见 `task_plan.md` Phase 15；实时分析文档 `C:\Users\郑曾波\Projects\Research\zijin_filing_problem_analysis.md`。
> 四层根因：**管道语义断层（F3/F10）→ fail-closed 无逃生通道（F2/F4/F5）→ worker 锁协调（F6）→ 基础设施健康（F7）**。其中 F2/F4/F5 是"缺元数据"与"真冲突"被合并为同一枚举所致。

### 发现 F1：双重上市身份歧义，错误信息无消歧引导

- **内容**：`company_query="紫金矿业"` → `ambiguous / multiple_verified_exact_identities`。security_master 同时注册 CN 601899 与 HK 02899（`cn.json`/`hk.json`，均 active）。`SecurityIdentityResolver.identify()` 多命中返回 ambiguous 是**正确的安全行为**。
- **影响**：错误信息没有提示"补充 market/exchange/ticker 可消歧"，脚本化调用直接死路。属体验缺陷，非逻辑缺陷。
- **证据**：`C:\Users\郑曾波\Projects\company-wiki\.source_catalog\security_master\cn.json`（org_id 9900004143）、`hk.json`；`filing-fetch/scripts/fetch_filing.py:283-306`。

### 发现 F2：缺身份元数据被计为 identity_mismatch（误报冲突的机制）

- **内容**：`resolver._identity_matches()`（CW-3.5 严格模式）对 metadata 缺 market/security_id 返回 `missing_fail_closed`；断言兜底块里 `if not assertion_matched: identity_mismatch += 1; continue` —— **无断言 = 计一次 mismatch**。5 条 601899 annual_report 占位文档全部命中 → `IDENTITY_CONFLICT`。
- **关键**：这是"元数据缺失"而非"身份冲突"，两种情形共用同一枚举与文案，误导排查方向（本次一度误查 security_master 与 assertions 表）。
- **证据**：`resolver.py:325-355`（`if not assertion_matched` 在 `if market_match == "missing_fail_closed"` 内、`if assertion` 外——读缩进确认）、`resolver.py:449-478`（`_identity_matches`）、`resolver.py:428-434`（IDENTITY_CONFLICT 结果）。

### 发现 F3：dayu portfolio 占位文档污染目录（管道语义断层，根因之首）

- **内容**：2026-07-22 dayu 扫描后目录出现 11 条 601899 "文档"（FY2021-2025 年报、2025 半年报、Q1/Q3、2026Q1），全部 `files: []`、`primary_source_id: NULL`、无 fingerprint、无断言、`ingest_complete: false`、`staging_pdf_sha256: null`。机制：
  1. dayu-agent `cn_pipeline_download_v1.0.0` 只写 **meta.json + manifest.json**（含 cninfo 精确 URL 与 source_id 1225023658），**从未下载 PDF 字节**；
  2. company-wiki `scanner.py` 把 meta.json 按 role=`metadata` **摄入为正式文档**，无 preferred 文件 → `source_status="incomplete"`；
  3. 身份信息在源头存在（portfolio 级 `601899/meta.json` 含 `market:"CN"`；每条占位含 `provider_company_id: "CNINFO:9900004143"` == security_master org_id），**摄入时未传播**。
- **影响**：占位文档是 F2/F4 的触发器；**删除后下次 portfolio scan 会重新生成**（复发风险，见 F10）。
- **证据**：`scanner.py:371-389`（`preferred is None` → `incomplete`；meta.json role 判定在 386-394）；dayu meta.json 实测：`ingest_complete:false`、`primary_document: "fil_cn_...pdf"`（不存在）、`files:[]`。

### 发现 F4：identity_conflict 同时阻断复用与下载（fail-closed 无逃生通道）

- **内容**：`acquisition.resolve_or_stage()` 中 `IDENTITY_CONFLICT` → `AcquisitionStatus.MISSING` + reason `identity_conflict_no_download` —— 不尝试适配器。CLI `ensure` 无 force/override 参数（cli.py:275-309）。
- **影响**：标准流程（reuse → 下载）对元数据残缺的目录 100% 死锁；本次唯一出路是裸 SQL 改共享库（用户批准后执行）。
- **证据**：`acquisition.py:313-326`。

### 发现 F5：断言修复路径结构上不可用于无源文档（修复路也是断的）

- **内容**：设计者预留的逃生通道是 `identity-enrichment`（preview→verify 断言绑定身份），但 `get_verified_assertion(store, source_id, content_sha256)` 按 **primary_source_id** 查询（service.py 查询结果 `source_id = primary_source_id`），占位文档该字段为 NULL → SQL `WHERE source_id = NULL` 永不命中。实测 0 条 assertions、无绕过路径。
- **影响**：无受支持手段修复占位文档 → 只能删或改库。
- **证据**：`assertion_service.py:75-108`（`_get_active_verified_assertions` / `get_verified_assertion`）、`service.py:216-218`。

### 发现 F6：worker 锁抖动 + 锁错误被标为不可重试

- **内容**：worker（pid 5568）`backfill_text_fingerprints` pending ~21979，分批次持有 `operation.lock`，批间窗口极短；本次 ≥4 次 `CatalogOperationLockedError`。更关键：`filing_contracts.py` `retryable = code in {"upstream_error", "worker_paused"}` —— 锁竞争被归类 `fatal / retryable:false`，调用方按契约**不应重试**。另有 TOCTOU：检测到锁释放与真正发请求之间 worker 重新拿锁。
- **影响**：获取文件靠碰运气抢窗口（本次 bash 循环 6 次抢到 1 次）；worker 活跃期交互式获取基本不可用。
- **证据**：`filing_contracts.py:46`、`fetch_filing.py:426-432`（fatal 输出）、`worker_state.json`（last_fingerprint_report pending 21979）。

### 发现 F7：磁盘 99% 满，备份基础设施不可用

- **内容**：`catalog.sqlite3` **20.2GB**（会话期间仍在增长）；`.source_catalog` 共 62GB（`.bak-bg5-*` 3 份 ≈ 28.6GB、cw-226 3.4GB、cw-225 1.2GB、cw-228 仅 73MB 可疑地小）；C 盘 476G 总量 **99% 满**（3.9→5.2GB 余量）；`cp` 备份在 4.1GB 处失败（No space left on device），留下 4.1GB 半成品文件。
- **影响**：删除占位文档时**无新鲜备份兜底**（恢复点仅 07-26 的 cw-228）；worker 回填 22k 项随时可能写满磁盘 → 整库不可用。
- **证据**：`du -sh .source_catalog` = 62G；`df -h /c` = 99%；备份失败 stderr。

### 发现 F8：执行侧过程瑕疵（记录供后续改进）

- 锁门控未真正执行：`test -f operation.lock && echo "LOCKED - abort" || ...` 只 echo，Python 删除在锁存在时照样跑完（结果正确、事务干净，但并发窗口改共享库是风险）；
- Git Bash `/tmp` 与 Windows Python 路径解析不一致，handle 文件写丢一次；
- 第一次撞锁后没有立即设计带退避的循环，多跑 2 次无谓失败；后续循环抢窗口成功属运气。

### 发现 F9：控制台中文乱码（次要）

- GBK console 与 UTF-8 数据流不匹配（`紫金矿业` 显示为 `�Ͻ��ҵ`）；`PYTHONUTF8=1` 可缓解。纯展示问题，不影响数据。

### 发现 F10：修复是临时的，占位文档会复发

- 删除 11 条占位后 fetch FY2025 立即成功（capture_ready，80MB，source active）—— 证明根因判断正确。但 dayu portfolio 磁盘上 meta.json 原件仍在，**下一次 scan 会重新摄入**，F2/F4 死锁复发。根治需 F3 的修复方向（scanner 不摄入 / 打 planned 状态 / 传播身份）或 dayu 管道真正完成下载。
- **恢复点说明**：删除内容非永久丢失（meta.json 原件在 dayu portfolio 可重建）；catalog 恢复点 cw-228（07-26，73MB）。

### 发现 F15：scan 同 group 多 primary 时 metadata 取排序第一个（F13 治理中发现）

- **内容**：同一 group（relative path 前 3 段相同）存在多个 `original_primary` 文件时（如旧路径 `financial_reports/宁德时代：2024年年度报告.pdf` + 新路径 `financial_reports/annual/2025-03-14_cninfo_...pdf`），scanner 用 `next(...)` 取排序后第一个 candidate 的 group_metadata → 文档 metadata 可能被旧 sidecar（无 URL）覆盖刷新，新 sidecar 的完整 metadata 丢失。
- **处置（本次）**：删除冗余旧文件（同 hash 假源）后重扫解决（宁德时代实例）。**scanner 的 group metadata 选择逻辑（取"最优"而非"第一个"）未修**——待单独决策（现无 regulatory 残留，影响面 = 知识库多 root 重复文档的 metadata 质量）。
- **证据**：宁德时代 b4f1713d 两次 scan 后 metadata 仍无 source_url，删旧文件后刷新成功。

### 发现 F14：dayu HK 下载路径环境性不可用（Phase 15.6.3 发现）

- **内容**：HK 路由（dayu-hkex-cli）下载 FY2024 年报在三次不同参数下均超时：`--timeout-seconds 600`（腾讯）598s、`--timeout-seconds 600`（小米）598s、`--timeout-seconds 1800`（小米，配置注释明示 dayu 需 5-15 分钟 + Docling 转换、30 分钟充足）1580s 仍未完成。dayu workspace 30 分钟内**零新文件**；数个大内存 python 进程（2.6GB/2.5GB/1.4GB）疑似 Docling/RapidOCR 转换卡住。
- **影响**：HK 下载在本环境不可用（非锁问题——锁重试已正常工作；非参数问题——1800s 也超时）。超时被 filing-fetch 子进程级杀掉，company-wiki journal 无记录。与 07-24 `dayu-hkex-cli immutable provenance sidecar conflict` 历史失败无关（彼为 HKEX 旧文档写入冲突，已过去）。
- **处置**：如实记录；HK 项未达 15.6 验收。属 dayu-agent 侧环境/性能问题（15.8 非目标：不动 dayu 仓库），待单独决策（延长超时/诊断 Docling/换下载路径）。

### 发现 F13：旧摄入 sidecar 缺 https URL 阻塞复用路径（Phase 15.6.3 发现）

- **内容**：2026-07-21 前后批量摄入的一批公司 raw 文件（如宁德时代 300750、贵州茅台 600519），其 `.source.json` sidecar 为极简字段：有的**完全没有 `source_url`**（宁德时代 2024 年报，真实 2MB PDF），有的为 **http://static.cninfo.com.cn/...**（茅台 2023/2024，当时为 59 字节 placeholder stub——已 retire+删除）。`resolver._handle` 对缺 URL/http URL → `https_url=None` → `missing_capture_fields=["https_url"]` → filing-fetch 复用与下载路径均拒绝。
- **影响**：这些公司即便已有真实文件也无法复用；`ensure` 也会在 reuse-first 处卡死（与 F4 占位死锁同性质，但对象是真实文件）。宁德时代 FY2024 下载尝试报 `source lacks capture provenance: https_url`。
- **处置（本次）**：茅台 stub（59B 假文件）已 retire 文档 + 删文件；宁德时代等真实文件保留，仅记录。**批量数据修复（补 sidecar URL 或 resolver 容错）不在 Phase 15 范围**，待单独决策。
- **证据**：`companies/宁德时代/raw/financial_reports/宁德时代：2024年年度报告.pdf.source.json`（无 source_url）；`https://static.cninfo.com.cn/` 已验证支持 HTTPS（200 + PDF）。

### 发现 F12：filing-fetch stdin 管道用 GBK 解码破坏中文查询（Phase 15.3.7 发现）

- **内容**：`echo '<含中文 JSON>' | python scripts/fetch_filing.py` 时 identify 返回 `missing / no_verified_identity_candidate`；同一查询经 `--request-file`（`read_text(encoding="utf-8")`）则完全正常。直接调 company-wiki identify CLI（argv 传参，Windows wide-char API）也正常。
- **机制**：Windows 下 Python 对 pipe 型 stdin 默认用 locale 编码（中文系统 = GBK）解码 UTF-8 字节 → 中文查询 mojibake → identity 无候选。filing-fetch 只给**子进程**设了 `PYTHONUTF8=1`，自身 stdin 未 reconfigure。
- **影响**：管道传中文查询在中文 Windows 上不可用；`--request-file` 是干净路径。属 F9（控制台编码）同族，**非 15.2/15.3 改动引入**（基线即如此）。修复（stdin reconfigure 或按 bytes 解码）不在 Phase 15 范围，记录待单独决策。
- **验证**：`--request-file` + 中文「紫金矿业」FY2024 → identify resolved → resolve `missing / no_existing_source_satisfies_request`（15.3.7 通过，exit 2 not_found 语义正确，无 identity_conflict）。

### 发现 F11：紫金 FY2025 年报最终获取成功（会话唯一正面结果）

- 删除占位后 `fetch_filing.py --allow-download` 成功：`capture_ready`，80MB PDF 入 `companies/紫金矿业/raw/financial_reports/annual/2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf`；source `urn:company-wiki:source:sha256:01819e1c...`，status `active`；handle 已保存 `C:\Users\郑曾波\Projects\Research\zijin_handle.json`。
- **FY2024 年报未获取**（撞锁后用户叫停）—— 恢复预报的第一个前置依赖。

---

## 2026-07-31 — Phase 15.1.1 磁盘清点与 bg5 备份背景核对

### 磁盘现状（15.1 先决）

- C: **99% 满，余量 5.0GB**（2026-07-31 22:42 实测；会话结束时 5.2GB，持续恶化）
- D: 932G，余量 **92G**（91% 用）——「移到其他盘」选项的唯一可行目标
- G: 476G，**100% 满**，余量 4.8G（不在 Phase 15 范围，但值得单独关注）

### `.source_catalog` 下全部 `*.bak*` 清点（15.1.1）

| 文件 | 大小 | mtime | 判断 |
|---|---|---|---|
| `catalog.sqlite3.bak-bg5-20260728T194409Z` | 9.4G | 07-28 10:12 | BG-5 apply 前更早一份备份（19:44Z） |
| `catalog.sqlite3.bak-bg5-apply-`（无后缀） | 9.4G | 07-28 10:12 | **疑似半成品中间产物**（无时间戳命名） |
| `catalog.sqlite3.bak-bg5-apply-20260728T194951Z` | 9.4G | 07-28 10:12 | receipt 记录的官方 pre-apply 备份 |
| `catalog.sqlite3.bak-cw225-20260722-205901` (+shm/wal) | 1.2G | 07-22 20:59 | 旧备份（wal 0 字节=已干净 checkpoint，shm 32K 遗留） |
| `catalog.sqlite3.bak-cw226-20260723-191312` (+shm/wal) | 3.3G | 07-23 19:13 | 旧备份（同上） |
| `catalog.sqlite3.bak-cw228-20260726T102302` (+shm/wal) | 74M | 07-26 10:23 | findings F7 记录的恢复点 |
| `backups/catalog-before-phase4r-1785095525.sqlite3` | 7.4G | 07-26 20:52 | 手工备份（phase4r 前），不在删除计划范围 |

### bg5 生成背景（已核实，操作已结案）

- BG-5 = company-wiki §10.6.9/§10.7.6 artifact reconciliation **apply 已成功**：2026-07-28，2685 new artifacts 插入 54.3s，0 conflict/detached/mismatch；全回归 99P/4skip/0F；ruff/compileall green。
- receipt：`artifacts/gates/source-catalog-bg/bg5-apply-result-20260728T195200Z.json`，其中 `backup_path` 明确指向 `bak-bg5-apply-20260728T194951Z`（9.4G≈10GB）。
- company-wiki `task_plan.md` **0 unchecked checkboxes**，BG-5 已结案；三份 bak-bg5 均属该已结案操作的产物，可弃（待用户确认，15.1.2）。
- 后续仍有活跃工作：`wr-10-7-*` receipts（07-31 21:51）——company-wiki 自身 worker 可靠性门禁仍在推进，删除操作注意避开 worker 活跃窗口。

### worker_state.json（15.1.7 初步检查）

- `backfill_text_fingerprints`：eligible 21970 / **pending 21967**（会话结束时 21979，仅 -12）/ completed 3 / terminal 27 —— **未收敛**，进度极慢（约 12/小时级）。
- worker `last_error: CatalogOperationLockedError: pid=15536` —— **锁竞争仍在持续**，坐实 15.2（可重试化）的紧迫性。
- `last_scan_report`：files_seen 46781 / reused 46780 / **errors=1** / locations_active 46780（07-31 22:07 左右）。
- `worker_control.json`：desired_state=enabled，但 `stop_requested_for` 有值（07-31 21:06 supervisor 切换痕迹，company-wiki 自身 WR-10-7 范畴，不在本 Phase）。

---

## 2026-08-01 — MongoDB 预测研究数据（FY2025 10-K，截至 2025-01-31）

### 从 FY2025 10-K 提取（mdb-20250131.htm，EDGAR 归档 0001441816-25-000057）

- 总收入：FY2025 **$2,006.4M**（+19%）、FY2024 $1,683.0M（+31%）、FY2023 $1,284.0M
- 客户：>54,500（2025-01-31）；**$100K+ ARR 客户 2,396**（FY2025）/ 2,052 / 1,651
- Atlas 占收入 70%（FY2025）、66%、63%
- Subscription 占 ~97%（$1,943M）；Direct Sales Customers 占 subscription 88%
- 无定量收入指引（10-K 内）；license 点时间确认，subscription = term license + DBaaS（usage-basis）
- 财年截至 1-31；FY2026 结束于 2026-01-31

### 档案获取链路问题（MongoDB 触发，已修复）

- **F13 治理粗糙面**：374 个 dayu 摄入的 SEC 文档（含 MongoDB 全部 20 个：FY2022-2025 10-K/季报/8-K）被批量 retire（metadata 无 source_url）——但 **accession_number + company_id + primary_document 可确定性构造 EDGAR URL**（`https://www.sec.gov/Archives/edgar/data/{cik:0>10}/{accession}/`，已验证 200）。已批量恢复 374 个（注入 URL + company_name + market/security_id，来自 portfolio 级 meta.json）。
- **resolver 复用契约缺口**：dayu portfolio 文档路径在 `companies/` 外，filing-fetch handle 契约拒绝 → ensure reuse-first 死锁。已修：resolver 只对 company_raw root 的 location 构建复用 handle（1530 tests 全绿，提交 88c67f2）。
- 待办：CN/HK dayu 文档的 URL 构造方式不同（cninfo/hkex），保持 retired 待单独决策。

---

## 2026-08-01 — MongoDB 会话后全面复盘（Phase 16 编制依据）

### R1：F13 批量治理被 worker 旧代码整体复活（最严重）

- **事实**：当前 10,185 个 active regulatory 文档中 **9,574 个仍缺 source_url**（CN 9,484 + 其他 90）；9,576 个治理对象几乎全部被复活为 active 但**未修复**——filing-fetch 复用路径对它们依旧卡死（宁德时代同类问题仍在 9,000+ 个公司存在）。
- **机制链**：批量治理 retire（09:03）→ worker（pid 7916，09:07 启动，加载的是**旧 scanner 代码**——无 15.6 终态保护）scan → UPDATE source_status 复活 → active 但 metadata 仍旧 sidecar（无 URL）。
- **次生**：374 个 US 恢复文档中 **373 个的 URL 注入被 scan 覆盖**（旧 sidecar 重写 metadata_json——scanner 的 update 分支用 group 的 sidecar metadata 覆盖注入值）；112 个 meta.json 占位被旧 scan 复活（primary 为 json）。
- **根因**：a) 治理与 worker scan 无版本/时序协调；b) worker 长进程不热更新代码；c) scanner 无条件重写 metadata（外部注入值无持久化）。

### R2：CN 9,484 个真实文件的 URL 可构造性未评估

- 这些是 ≥500B 的真实 PDF（如宁德时代/联影医疗等），dayu meta 无 announcement_id 信号（字段名待查）——**需检查 CN meta.json 实际字段**，决定能否确定性构造 cninfo URL（如 announcementId + stockCode）。

### R3：retire 缺少对称的反向命令

- 374 个恢复靠直接 SQL（无审计、无工具化）；`documents restore` 不存在。恢复操作不可复现。

### R4：worker 代码版本漂移（运维协议缺失）

- worker 进程加载启动时磁盘代码；15.6 期间 3 次代码修复（终态保护/resolver/dedup）提交后 worker 未重启即继续用旧逻辑 → 行为漂移。**需要重启协议 + runtime 记录代码版本**。

### R5：F12（stdin GBK）与 F15（group metadata 取第一个）仍未修

- F12：管道中文查询破坏（--request-file 是干净路径）。
- F15：同 group 多 primary 时 metadata 取排序第一个（宁德时代曾用删除旧文件绕过；scanner 逻辑未改）。

### R6：company-wiki git 跟踪不完整

- `src/company_wiki/source_catalog/` 仅 4 个文件被跟踪，其余（含全部 Phase 15 修复依赖的模块）从未提交——提交纪律与可追溯性缺口。

### R7：恢复/注入操作无审计

- 374 URL 恢复 + 769 company_name/market 注入直接 SQL——无审计表、无 created_by/reason。

### 关键量化（2026-08-01 复盘时点）

| 项 | 数量 |
|---|---|
| active regulatory 文档 | 10,185 |
| 其中缺 source_url | **9,574**（CN 9,484） |
| 有 URL（新 canonical） | 39 |
| US 恢复后 URL 被 scan 覆盖 | 373 |
| 占位复活（primary=json） | 112 |
| retired（茅台 stub，正确保留） | 2 |

## 2026-08-01 阿里巴巴会话发现（Phase 17 编制依据）

> 会话：`/revenue-forecast 阿里巴巴`（信息截止 2026-08-01）。引擎产出全部硬门通过（1 次 valid、publication receipt 重算通过、输入构建 4 轮校验往返），全面审查后记录 A1-A17。完整审查见 `Research\alibaba-forecast\REVIEW.md`。已并入 Phase 17 计划。

### A1：无源事实混入正式 conclusion（×3，P0）

- **事实**：`research_coverage[policy].conclusion` 含"美國取消小額包裹關稅豁免（de minimis）"（本会话未在任何已打开来源核验）；`research_coverage[industry_market].conclusion` 含"（約人民幣15-17萬億）"（来自模型自身知识）；`management_communication_coverage[announcements].conclusion` 含具体回购日期/授权日（来自 WebSearch 摘要）。
- **机制链**：引擎只校验 conclusion 的结构（parameter_ids/source_ids 存在），不校验文本内数字是否有 claim 背书 → 无源事实可进入正式工件。
- **影响**：违反硬门"a fact or management guidance lacks a source"；若被 invest-* 下游引用会污染评估。→ 17.1.1 修正。

### A2：来源"注册但未打开"（P0）

- **事实**：`src_buyback_jul2026` 捕获 582,641 字节，但正文为 JS 渲染，文本提取仅 214 行、只含标题；结论引用的回购日期/金额/授权日均不在捕获内容中。
- **影响**：违反硬门"a citation was not opened and checked"。→ 17.1.2 补核或降级。

### A3：自报工具调用 → formal 发布（P0，信任边界）

- **事实**：8 个来源 `tool_call_id` 均为模型自填字符串、`verified_by` 自报，无宿主签名事件日志；输出 `formal_output_mode=formal`。
- **设计意图**：task_plan Phase 8.4"无 trusted verifier 的环境只能输出 draft"；13.4B"self-reported tool call 不能 formal publication"。引擎按 compliance-contract 字面合规（记录 host attestation 缺失），但保证强度与用户感知存在落差。
- **影响**：正式标签的保证范围（结构/哈希/重算）≠ "工具确实被调用"。→ 17.1.5/17.7 信任边界声明。

### A4：`t_ai_share_50pct` 测量期间映射偏差（P0）

- **事实**："in about one year"（2026-05-13 起）≈ 2027-05，落在 **FY2028**；输入映射为 `run_rate_at_period_end: FY2027`。
- **影响**：目标期间判定偏早一年（perimeter mismatch 未入情景，处理正确，影响限于数据缺口文案）。→ 17.1.3 改 ambiguous 或 FY2028。

### A5：FY2024 下载超时 = 已知 F14 环境性失败，未预判（P0）

- **事实**：FY2024 年报下载 1499s 超时；findings.md F14 已记录同型（dayu HK 三次超时 598s/598s/1580s、30 分钟零新文件、Docling 疑似卡死）。
- **影响**：0.3 规则1（开工读 findings）未执行导致未预判；数据由 FY2025 AR 对比数覆盖（无损失），但失败原因未诊断未记录。→ 17.2 会话检查单。

### A6：快照不可变语义弱化（P0）

- **事实**：因敏感性参数重定向，删除并重建**同版本号** `2026-08-01-v1` 快照（内容不同）。
- **影响**：早期消费者引用的 v1 指纹失效。→ 17.1.4 用 v2；17.5 固化版本纪律。

### A7：accg_other 合并两条经济上不同的曲线（P1）

- **事实**：直營、物流及其他（105,518，+2%）与中国批发（26,312，+8%）合并为单一 direct_growth。
- **影响**：违反"每流一分部"；批发增速被直营拖低，驱动树归因混叠。→ 17.8 backlog。

### A8：CIG direct_growth 可选改进（P1，双刃）

- **事实**：Q4 外部 +40%、AI 产品收入 8,971 百万（占外部 30%）已披露，可支撑基期 AI/非 AI 两流拆分。
- **反方**：AI 年度绝对值需从 Q4 外推（假设叠加假设）——"更多参数≠更準確"。→ 17.8 backlog（注明反方观点）。

### A9：GMV 基数构造性循环（P1）

- **事实**：GMV_base = 343,867 ÷ 4.0% = 8,596,675，基期精确对齐由**构造**保证而非独立证据。
- **影响**：应注册为 `derived_fact`（公式 CMR÷take_rate）显式化循环性。→ 17.8 backlog。

### A10：负向驱动无法进入正式 headwinds（P1，引擎能力缺口）

- **事实**：归因权重限 `(0,1]`，负权重被拒；商家补贴 contra-revenue 转为 contrary 证据节点 + data_gaps 文字，输出 `headwinds: []`。
- **影响**：设计意图"Preserve negative roots as revenue headwinds"未量化呈现。→ 17.6 schema 3.6 提案。

### A11：敏感性传导语义盲区（P1，已修正）

- **事实**：初版 3 项 shock 作用于 FY2028 绝对水平型驱动（usage_platform activity/monetization、adjustments），终期影响恒为 0（引擎重算正确，0 即正确结果）；已重定向至 FY2031 终期参数。
- **教训**：敏感性参数选择需传导语义检查，引擎无提示。→ 17.4 lint 预检。

### A12：CIG over_time progress=1.0 全周期（P1，轻微）

- **事实**：progress 全年 1.0 使 over_time 与 modeled_as_recognized 等价（标签式，会计表述诚实，progress 参数已入依赖图）。
- **影响**：无实质影响，记录。

### A13：builder 脚本自身两个 bug（P2）

- **事实**：sed 式字符串替换截断文件尾部（恢复后正常）；StockAnalysis 来源哈希初始为占位符（已修正）。
- **教训**：build 流程需写入后立即 lint 的完整性校验。

### A14：会话未维护 findings/progress（P2）

- **事实**：0.3 规则4（每 2 次查看/搜索写 findings）未执行——本会话无 findings 记录。
- **影响**：复盘依赖事后重构。→ 17.2 检查单固化。

### A15：两个来源零 claim 绑定（P2）

- **事实**：`src_ir_earnings`、`src_buyback_jul2026` 注册但无任何 claim 引用（"registered but unused"弱绑定；buyback 另有 A2）。

### A16：FY2025 AR URL 事后字节验证 MATCH（P2）

- **事实**：注册时未验证 URL；事后 curl 比对 HKEX 下载与本地文件 4,630,060 bytes / sha256 8ab12348… **一致**。
- **教训**：注册流程应内置"URL→字节"核验步骤（下次直接复用 HKEX URL 时先 curl 比对再注册）。

### A17：杂项小问题（P2）

- GBK 控制台多次 UnicodeEncodeError（deliverable 无影响）；markdown 简繁混排（模板简体/摘录繁体）；CodeGraph 未用（skill 仓库未建索引，按规则应询问 init）；模板工具首调参数误用；主题 rationale 未随输出传播（input 正确、engine 输出形状不含 rationale）。

## 2026-08-01 Phase 17 实施记录

### P17-1：修正前交付物备份与指纹（17.0）

- 备份：`Research\alibaba-forecast\backup-pre-phase17\{input,forecast,snapshot}.json`（修正前，字节一致）。
- 修正前指纹：`validated_input_sha256 = 00dd17c3...bcde54`（forecast.json receipt）；snapshot.json 内 `input_sha256 = 1ecbc908...f9255`（口径与 receipt 不同，v2 重建时验证）。
- input.json 修正点定位：L6848 policy conclusion（de minimis 表述）、L6790 industry_market conclusion（15-17萬億）、L6962 announcements conclusion（具体回购日期/授权日）、L6968-6998 `t_ai_share_50pct`（measurement_basis=run_rate_at_period_end/FY2027）、L7417 growth driver leading indicator 亦含「關稅政策（de minimis）」（17.1.1 grep 0 命中测试需一并处理）。

### P17-2：执行顺序决策（17.3/17.4 先于 17.1）

- 17.3/17.4 实证要求「修正前 input 命中 3 处/3 项」——先实现工具（对备份的修正前版本实证），再做 17.1 修正（对修正后版本实证 0 命中），最后 17.1.4 快照 v2。

### P17-3：Phase 17 实施与独立审查发现

- **17.3 实证偏差（vs 计划"命中 3 处"）**：`--check-conclusion-facts` 对修正前 input 命中 **6 处**——A1 的 industry_market（15/17）✓、announcements（纯日期表达被排除，靠 grep 测试兜底）、policy（无数字不适用）；另发现 capacity/customers/demand/earnings_call/strategy 5 处"来源已注册但数字未摘录"（A15 同型）。修正后 5 处（A1 范围内 2 处清零）。教训：conclusion 数字无 claim 摘录是系统性现象，不止 A1 的 3 处。
- **单位表述差异误报**：结论"3,800億" vs 英文 excerpt "RMB 380 billion" 数值不等 → 告警（warn-only 设计内）；启发式不做单位归一（已记 docstring）。
- **token 排除边界**：漏检方向（YoY9.5% 字母粘连、5000萬 4 位数字被当年份）；误报侧（每週6天）。
- **崩溃回归（独立审查发现）**：`float("1.2.3")` ValueError → lint 崩溃，违反 "never raises"；已修复（_token_numeric_value None 守卫）+ 回归测试。
- **测试编码**：subprocess 测试未显式 encoding 时，PYTHONIOENCODING=utf-8 环境下父进程 gbk 解码失败；已修复（encoding="utf-8" + env）。
- **17.1.2 实现偏差**：schema 3.5 claim target 枚举（parameter/historical_revenue/recognition_policy/scenario_probability/management_target/growth_driver）均需真实模型对象，回购事件无挂载点（挂参数违反 revenue_core.py:442 source 注册约束）→ 记录级 source_ids 绑定替代（A2 实质达成）。
- **快照 hash 口径**：snapshot.input_sha256 = canonical(input+forecast_version)（revenue_backtest.py:36 设计），≠ receipt.validated_input_sha256（v1 时代亦然）；验证用 validate_snapshot + 确定性重跑。
- **17.4 实证**：磁盘无 A11 会话初版（已重定向）；RED 实证用 A11 事实还原构造（3 项命中），当前 input 0 命中。

## 2026-08-01 Alphabet 会话（17.2 检查单试点）发现 — 双类股/多地上市身份泛化（Phase 18 编制依据）

### G1：双类股 ticker 未归一导致复用死锁（核心）

- **事实**：Alphabet（NASDAQ GOOGL/GOOG 双类股）FY2025 10-K 下载成功（canonical `companies/Alphabet Inc/raw/...`，sha256 c2f63010…，CIK 1652044），但 filing-fetch reuse-first 持续 not_found。
- **根因链**（三层）：
  1. `resolver._entity_matches`（resolver.py:542）精确匹配 request.entity 与文档 entities/metadata ticker——request 用 GOOGL 时文档只有 ticker:GOOG/Alphabet Inc → 不匹配；
  2. `_identity_matches` 对 metadata 缺 market/security_id 返回 missing_fail_closed（SEC dayu sidecar 只写 security_id=GOOGL 不写 market）→ 断言兜底（resolver.py:359-383）要求 `request.market and request.security_id` 且与断言 **精确相等**——GOOGL vs GOOG 不相等 → 兜底失败；
  3. scanner 摄入补全（16.1 URL 模式）不覆盖身份；metadata 更新分支（scanner.py:983 prefer_new）只认 URL——已存在文档（hash 未变）永不重摄入，身份补全无法生效。
- **用户裁决（2026-08-01）**："双类股应该可以共享文档，因为是一家公司，仅仅是上市ticker不同" → 泛化逻辑入改进清单（Phase 18 规划），**不立即实现**。
- **影响**：GOOGL/GOOG 及任何多 ticker 发行人（如多地上市 CN/HK 同发行人）的复用路径受同样影响；本次以 local_document 备用路径继续（文件已在 canonical）。

### G2：`verify_assertion` 的 supersedes 实现与 docstring 不符

- `assertion_service.verify_assertion`（:277-316）docstring 称"supersedes previous verified if exists"，实现 `supersedes_assertion_id=assertion_id`（被 verify 的 candidate）——**不链接旧 verified**；同一 document 出现 2 条 verified 时 `get_verified_assertion_by_document` fail-closed（多命中无 supersedes 链 → None）→ 断言兜底整体失效（15.5 的"多命中 fail closed"与 verify 语义冲突）。
- 影响：身份更正（如 GOOGL→GOOG）无法通过 supersedes 链表达；需 reject 或新机制。

### G3：scanner 对已存在文档的身份补全不可达

- scanner 对 hash 未变文件不重摄入（幂等），metadata 更新仅在"新路径摄入"或 prefer_new 触发；已摄入文档缺身份时无法通过重扫修复（本次靠 identity-enrichment 断言补）。
- 16.10"契约变更影响面清单"应含此模式。

### G4：SEC dayu sidecar 缺 market（16.1 系列残余）

- SEC adapter 的 sidecar（canonical_writer 产出）写 security_id 不写 market；dayu_meta 无 market/security_id（15.4 身份传播只覆盖 provider_company_id 映射，SEC 无 provider_company_id）。→ 本次给文档 verify 断言（market=US/security_id=GOOG）补身份。

## 2026-08-01 Alphabet 会话全面复盘（Phase 19 编制依据）

> 复盘对象：`/revenue-forecast alphabet` 完整会话（17.2 检查单试点）。G1-G4（双类股身份）已入 Phase 18；本节 G5-G10 为**新暴露的工具链/流程问题**。

### G5：filing_fetch_client.py 无 CLI 入口（SKILL.md 示例与实现不符）

- **事实**：SKILL.md 示例 `python scripts/filing_fetch_client.py`（echo 管道）——模块**无 `__main__` 入口**（仅 `resolve_filing()` 函数），直接运行静默 exit 0 无输出；首次调用浪费 2 轮才发现需 in-process 调用。
- **根因**：Phase 9.11 迁移后客户端只作为模块使用，SKILL.md 示例未同步（文档/实现漂移）。
- **影响**：用户按 SKILL 调用必踩；G10 无一致性测试放大。

### G6：客户端错误诊断丢失（stdout 错误 JSON 未解析）

- **事实**：`resolve_filing` 失败分支（filing_fetch_client.py:75）只读 `completed.stderr`——而 filing-fetch 的错误 JSON（status/error_code/error/retryable）输出在 **stdout**（实测 stderr=0 bytes）→ 客户端报 "exited 2: no stderr"，关键诊断（request_error/identity_error）全丢。本次 ambiguous 定位多花 3 轮。
- **修复方向**：returncode != 0 时优先解析 stdout 的 error JSON。

### G7：ambiguous 消歧提示缺失（15.7 远期项复发）

- **事实**：Alphabet 请求报 `ambiguous / multiple_verified_exact_identities` 但**无候选列表**（security_master 4 条 active：GOOGL/GOOG/2 优先股）；需手工查库才知用 ticker 消歧。15.7 已登记"错误信息引导"远期项，本次复发。
- **修复方向**：identity_error 响应携带 candidates（ticker/canonical_name/market/exchange）+ 消歧提示。

### G8：引擎字段枚举速查缺失（输入构建 8 轮迭代）

- **事实**：build_input.py 经历 **8 轮** validate 修复（10 类结构错误）：tree.status、horizon 对象、persistence_rationale、attribution 权重 (0,1]、evidence_nodes 字段名、growth_driver target claims、历史 claim unit "USD million"、货币参数 currency/scale、dimension "ratio"（非 "growth_rate"）、time_basis "annual"（非 "fiscal_year"）、scale == 顶层 unit、modeled_presentation、recognition basis_claim_ids、sensitivity 仅 base 参数。
- **根因**：`generate_input_template` 只给骨架不给枚举值；`input-construction.md` 无枚举速查；引擎枚举散落 revenue_core.py 常量。
- **影响**：每次新公司构建都重复踩（恒运昌 23 轮、阿里 4 轮、Alphabet 8 轮——工具链已减轮次但枚举仍是盲区）。

### G9：搜索摘要数字不可靠（Q2 YouTube 数据冲突）

- **事实**：Q2 2026 YouTube 广告收入两来源冲突（investing.com 两篇：$11.1B +13% vs $7.3B -1%）；输入仅登记未深究（采用 FY 全年 10-K 数据，未受影响）。
- **教训**：WebSearch 摘要数字不能直接作为 claim 内容；官方 release（abc.xyz investor）优先，新闻转述仅引导（A16"URL 未验证"同族）。

### G10：SKILL.md 示例无一致性测试

- **事实**：SKILL.md 的 CLI 示例命令（`python scripts/filing_fetch_client.py` 等）从未被测试钉住——G5 类"文档示例失效"无回归保护（9.13 actual CLI guard 的同类缺口，但针对 skill 文档示例）。
- **修复方向**：静态检查测试——读 SKILL.md 的 `python scripts/*.py` 示例 → 断言脚本存在 + 有 `__main__` 入口（或标注模块用法）。

## 2026-08-01 Alphabet 会话深度反思（Phase 19 扩编）

> 第一轮复盘（G5-G10）覆盖工具链直接缺陷；本节为流程方法论/执行纪律层面的深层反思（A1-A6 + 执行自省）。

### A1：检查单的结构性盲区——"事后处置"而非"事前预判"

- **事实**：17.2 检查单 §2 预判了下载路径（US dayu 正常 ✓）但**未预判身份解析风险**；本次最大耗时恰是身份问题（8+ 轮）。检查单由本会话编制者（我）编写——第一版设计盲区。
- **根因**：检查单按"已知失败清单"组织（F14/m14/F6），对"**这类公司会遇到什么**"缺乏模式化预判。
- **改进**：§2 增"身份解析预判"——知名多 ticker/多上市名单（GOOGL/GOOG、9988/BABA、601899/02899、AMZN 无、TSLA 单 ticker 等）+ ambiguous 标准操作（identify 候选 → 选主 ticker → market hint）。

### A2：执行纪律——0.3 规则 12 的"3 次"被突破为 8+ 轮

- **事实**：身份问题诊断 8+ 轮才由用户主动喊停转规划；0.3 规则 12 规定"同一错误最多 3 次，3 次仍失败 → 标记 blocked 请求用户决定"——**规则存在但未执行**。
- **根因**：会话级"卡住感"被"快好了"的乐观驱动；单轮诊断看似进展（每轮排除一个因素）但整体无收敛。
- **改进**：检查单 §1 增"会话级 3 次/30 分钟规则"——同一主题（非同一命令）3 轮未解 → 停下报告现状 + 请用户裁决（含"切换备用路径"选项）。

### A3：备用路径正当性无规则

- **事实**：final 交付以 local_document 注册 canonical 文件绕过 filing-fetch handle（合理且 TRUST_BOUNDARY 已说明），但流程无规则——"何时允许绕过获取链路"未定义。
- **改进**：规则草案——filing-fetch N 轮（默认 3）未获 capture-ready handle，且**文件已在 company-wiki canonical（sha256 可独立核验）**→ 允许 local_document 注册 + TRUST_BOUNDARY 说明；文件未落 canonical → 必须修复获取链路，不得手工注册。

### A4：resolve 诊断不可观测（G6 的延伸）

- **事实**：8 轮定位靠手工 grep/SQL 重放 resolver 循环；无"每个候选被排除原因"的单一视图。
- **改进**：filing-fetch/company-wiki resolve 增加 `--debug`：输出每候选排除打点（entity_matches/identity/year/form/location/capture_ready 各步），一次看清全链。

### A5："每公司写一个 build_input.py"模式

- **事实**：恒运昌/阿里/Alphabet 各写临时构建脚本；参数命名、claim 循环、来源注册模式重复。
- **改进**：input-construction.md 增"构建脚本骨架"节（参数命名规范、claim 生成循环模式、来源注册模式、validate 迭代流程）——**文档化骨架而非框架化**（避免过度工程）。

### A6：启发式工具用得太晚

- **事实**：17.3/17.4（--check-conclusion-facts / --check-sensitivity-propagation）在**交付前**才跑（命中 6 处全部事后登记）；若**构建中每轮**跑，数字摘录问题更早暴露。
- **改进**：检查单 §4/§5 改为"构建中每轮跑启发式"（input 修改后即跑），交付前只是最终确认。

### B 级（登记）

- B1：Subscriptions 分部有 325M 订阅数披露，本可用 `subscription` 模型（6 段全 direct_growth 偏保守）——下次 Alphabet 迭代可选（A8"更多参数≠更準確"反方观点同样适用）。
- B2：构建轮次 KPI：检查单命中记录表强化为每会话必填（轮次/错误类别分布）——恒运昌 23 / 阿里 4 / Alphabet 8 已记录，19.3 落地后应验证下降。

### 执行自省（本会话执行者）

- G5（客户端无 CLI）第一调用即踩、第二调用仍踩——**未先读源码/--help 确认调用方式**（违反 0.3 规则 3"修改/调用代码前先确认"）；后续调用一律先 `--help` 或读入口。
- 检查单 §2 只预判下载路径——**自写检查单的第一版盲区**（A1），试点价值正在于此：检查单暴露了自己的盲区。



## 2026-08-03 — 设计目标达成审查（audit_review 合并）

> 独立审查底稿，来源 `audit_review/findings.md`。

### 2026-08-03：初始范围

- 根项目已初始化 CodeGraph；结构分析可使用项目知识图谱。
- 根目录已有历史 `AUDIT_REPORT.md`、`FILING_FETCH_AUDIT.md` 以及较大的 `task_plan.md`、`findings.md`、`progress.md`，说明本次必须核验历史“已完成”声明，而不能只做首次静态审查。
- 当前工作树在审查开始时只有 `.coverage` 为既有修改；该修改不属于本次工作，必须保留且不得覆盖。
- 同级仓库至少存在 `filing-fetch`、`company-wiki`、`invest-core`、`invest-framework`、`invest-skills`、`dayu-agent`、`StockInfoDLSimple` 等潜在依赖，最终范围以计划和实现引用为准。

### 核验矩阵

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

### 审查结论（2026-08-03）

#### 总体达成度

**部分达成。** 10 项一级设计目标：3 项达成（#6/#8/#9，其中 #6 带 Low 残余）、3 项部分达成（#1/#4/#10）、4 项未达成（#2/#3/#5/#7）。计划文档声称的"全部完成"不成立：计划首页仍停留在 13 Phase/294 tests，正文 Phase 8/17/19 状态自相矛盾，164[x]/387[ ] 的勾选率本身不能作为验收凭证。

#### 核心判断

1. **正式可信链的两个 Critical 支柱未兑现**：
   - F-02：敏感性等语义可通过"改结果+重算全部哈希"在无 input 验证路径绕过，且已动态复现穿透 snapshot/backtest 与 invest-core/framework 正式消费边界（结构上 invest 链无任何函数接受 input）。
   - F-11：Phase 8 trusted workflow receipt 基本未实现，自填字符串即可签发 formal，"无 trusted verifier 只能 draft"的 fail-closed 门不存在。
2. **已落地的主体修复是真实的**：validator 独立重算、filing-fetch/company-wiki 的 reuse-first+identity+单 writer+审计链、invest 单向依赖，均有实现+测试双重证据，不是伪完成。
3. **风险集中在"旧物未清"与"发布面漂移"**：旧 filing owner 双活（F-04）、`.codex` 安装副本 34 文件漂移（F-08）、SKILL/CHANGELOG/契约文档与实现相反（F-05/F-12）——即使 Critical 修复完成，旧安装与旧 CLI 仍会保留漏洞。
4. **质量门总体健康但不封口**：五仓库测试基本全绿（company-wiki 1 项竞态），coverage/分模块门、hermetic 测试、ruff 门存在 Medium 缺口。

#### 分项目结论

| 项目 | 结论 | 关键残余 |
|---|---|---|
| revenue-forecast | 部分达成 | F-01/F-02/F-11 可信链缺口；F-04 旧 owner；F-07/F-10；文档漂移 |
| filing-fetch | 达成（工作树） | F-06 发布复现性；F-14 Low；关键增强未提交 |
| company-wiki | 达成 | F-09 竞态（Medium）；F-13 ruff 红；scanner 直接测试薄 |
| invest-core/framework | 达成（受 F-02 牵连） | 无独立缺口；需随 revenue 契约升级；invest-core 1 skip 兼容边界待文档化 |
| 安装/发布面 | 未达成 | F-08 多副本四种状态并存；sync 默认只查 `.agents` |

#### 问题清单（按严重度）

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

### 2026-08-03：计划文档内部一致性初查

- 根计划第 5 行声明“13 Phase 全部完成、294 tests”，但同一文档后来扩展到 Phase 19，且状态表已出现更高的测试基线；首页状态明显未同步。
- 多个 Phase 标题标记 `completed`，其内部验收清单仍有大量 `[ ]`，不能仅凭标题判定达成；必须逐项回到代码和测试。
- Phase 17 存在直接状态冲突：阶段标题写 `completed`，后续“当前执行状态（追加）”仍写 `pending`。
- Phase 19 也存在直接状态冲突：阶段标题写 `completed（2026-08-02）`，阶段内部 19.8 又写 `pending（仅规划，未实现）`；后续还出现重复编号的 19.5/19.6/19.7/19.8/19.9。
- Phase 18 标题声明完成，但 18.5 的文档清单仍未勾选；需核对提交 `d1d444a` 和实际文件，而不能相信状态摘要。
- 历史审查报告中的 Critical/High 缺陷是 Phase 1–13 的主要设计输入。本次应验证修复是否真正形成不可绕过的发布链，而不仅是已有测试数量增长。
- 历史 `FILING_FETCH_AUDIT.md` 指出身份门、handle 深验证、上游版本契约、授权审计、deadline 和 hermetic test 等缺陷；这些与 Phase 9 验收目标一一对应，可用作回归清单。

#### 初步文档风险

| 风险 | 证据 | 初判 |
|---|---|---|
| 状态摘要漂移 | 首页仍停留在 13 Phase/294 tests，正文已到 Phase 19 | 高 |
| “completed” 与未勾选验收项并存 | Phase 9、13、18、19 等 | 高 |
| 同一 Phase 状态自相矛盾 | Phase 17、19 | 高 |
| 编号/内容重复 | Phase 19.5–19.9 重复追加 | 中 |

### 2026-08-03：基线状态补充

- 根计划的状态表显示 Phase 0–16 完成，后续追加表先把 Phase 17 标成 pending，又在更晚的追加表改成 completed；Phase 19 也先在阶段内部写 pending、后在末尾写 completed。时间顺序可能解释状态演进，但未回写旧状态，导致文档不具备单一可信当前状态。
- Phase 20 已出现在追加状态表中，但此前的标题抽取未显示 Phase 20；需继续定位完整章节与验收内容。
- `revenue-forecast` CodeGraph 健康：39 个 Python 文件、1024 个符号节点、1335 条边，可用于核心架构与调用关系核验。
- PowerShell `Get-Content` 对根计划给出的行数/阶段识别与 `rg` 行号不一致（1229 vs 至少 2404），说明该文件可能存在特殊换行或编码表现；后续以 `rg`/Python 二进制 UTF-8 解析为准。

### 2026-08-03：计划 checklist 与代码结构

- 通过 `rg` 流式解析得到 20 个 Phase 段落。Phase 1/15/16/16.10/17 的清单已勾选；Phase 2–14、18、19 在“completed”标题下仍合计保留大量未勾选项。
- 全计划统计：164 个 `[x]`、387 个 `[ ]`。其中 Phase 9 有 5 checked / 139 unchecked，Phase 13 有 0 / 52，Phase 19 有 0 / 28。即使部分未勾选只是没有回填，计划文档也不足以作为验收凭证。
- CodeGraph 显示根项目 39 个 Python 文件：15 个核心/工具脚本、20 个主要测试文件、同步安装工具与示例。核心模块拆分已在物理结构上出现（publication、contracts/evidence、constraints、backtest、report 等），但 `revenue_core.py` 与 `filing_acquisition.py` 仍是高符号密度文件（分别 94、113 个符号），需核验是否符合 Phase 10“因循环依赖停止拆分”的合理边界。
- 测试文件结构覆盖 publication、schema/data contract、sources、filing、backtest、constraints、model registry、input construction、documentation 和 sync installations，表面上与计划目标匹配；后续必须通过实际测试和关键断言内容判断深度。

### 2026-08-03：跨项目 CodeGraph 基线

- `filing-fetch` CodeGraph 健康：6 个 Python 文件、234 个节点、283 条边。
- `company-wiki` CodeGraph 健康：328 个 Python 文件、7161 个节点、11715 条边，是本次审查中实现面最大的仓库。
- 三个核心仓库均已初始化 CodeGraph，无需新增索引；可以按 AGENTS.md 直接进行结构取证。

### 2026-08-03：跨项目结构

- `filing-fetch` 物理结构非常小：2 个实现文件、4 个测试文件。与 Phase 9 的“thin client / 不复制上游业务逻辑”目标表面一致；关键在于这两个实现文件是否严格校验 company-wiki 契约并 fail closed。
- `company-wiki` 的 source catalog 只是一个大型项目中的子系统；相关实现位于 `src/company_wiki/source_catalog/`，相关 contract tests 数量充足，并有 identity、resolver、operation lock、worker、URL enrichment、schema migration、retire 等专门测试文件。
- `company-wiki/tests/` 根下保留大量 `_check*`、`_test*`、`debug_resolver*` 等临时/诊断脚本；这不一定影响正式 pytest，但反映测试卫生和仓库治理仍需核验。
- company-wiki 的范围远大于本次目标。审查将聚焦被 revenue/filing-fetch 依赖的 source catalog、identity/resolver/ensure、canonical writer、worker/scanner、assertion/retire/restore、CLI/contract，而不把整个研究管线泛化为本次设计目标。

### 2026-08-03：正式设计基线（Phase 0）

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

### 2026-08-03：根项目核心结构初证

- publication 已拆到 `scripts/revenue_publication.py`：receipt 明确绑定 schema、engine、input hash、payload hash、validator 版本、固定 gate_ids、formal mode 和 `freeform_override_allowed=False`；验证器会重算 payload/receipt hash。结构上满足“签发后防静默篡改”的一部分目标。
- workflow receipt 仍由 `revenue_core.build_workflow_compliance_receipt` 直接构造 `status="pass"`。是否不可绕过取决于其调用顺序、正式输出 validator 是否从输入独立重算每个 gate，以及调用方是否能绕过；单看 builder 不能判定达标。
- 根仓库仍保留 `scripts/filing_acquisition.py`，其中 `AcquisitionConfig` 直接包含 CN/HK/US adapter command specs。若该模块仍可被正式/文档路径调用，就与“filing-fetch 是唯一 canonical owner、消费者不得 fallback 到旧 downloader”冲突；需查 callers、CLI/文档和测试后裁定。
- `company_wiki_source.py` 与 `filing_fetch_client.py` 也存在，说明当前至少有三层 acquisition 相关代码。下一步要区分正式 thin client、legacy compatibility 和实际可达的双 owner。
- CodeGraph 未解析出 `run_forecast` 的 callees，也未解析出 `build_publication_receipt` 的 callers；这可能是模块别名/局部导入造成的图解析限制。此处不能据此声称函数未被调用，需改用 `codegraph_context`/具体源码与测试取证。

### F-01（暂定高）：publication receipt 实际在语义验证前构造

- 计划目标 2 明确要求“只有语义验证成功后才能签发 publication receipt”。
- `scripts/revenue_core.py:1348` 的 `run_forecast` 实际顺序是：`_build_forecast_draft` → `build_publication_receipt` → `result_sha256` → `validate_forecast_output`。
- docstring 却声称“only published after passing validator”，与实现顺序不一致。
- 正式模式验证失败会抛异常，receipt 不会返回给调用者，因此当前证据证明的是“内部签发语义与设计不符”，尚未证明失败 receipt 可被外部获取或下游接受。
- draft 分支也先生成 formal receipt，验证失败后才重建并手工改为 draft；需进一步核验 hash 绑定和 draft consumer gate。

### 验证器入口初查

- `validate_forecast_output(result, data=None)` 的输入 `data` 是可选的；该函数除 `run_forecast` 外还被 backtest、examples、constraints 和多组测试直接导入。必须核验 `data=None` 是否形成弱验证路径，以及正式 consumer 是否强制重新验证原始输入。

### 验证器结构补充

- validator 会重算 segment model path、recognition、constraint audit、effective revenue、consolidated bridge、CAGR/growth、概率加权结果、source capture/claim hash 等，已明显超越旧审计所说的“只做字段存在/hash”状态；目标 1/3 的主体修复有真实实现证据。
- 版本分支包含 `FORECAST_SCHEMA_VERSION` 以及显式 `3.5/3.4/3.3/3.2/3.1`。其中 3.4/3.5 分支要求 `engine_version == ENGINE_VERSION`，表面上可能与 Phase 0“3.4 只接受 CHANGELOG 列出的历史 engine、legacy read-only”不一致；需先核实当前常量和后续 validator 逻辑再定性。
- validator 当前要求 `result_sha256`，而 `run_forecast` 又在验证前建立 receipt/result hash，解释了当前实现为何先签发再校验。但这正说明“验收函数把验证候选与已签发工件混在同一对象模型中”，设计目标 2 尚未真正落地为两阶段签发。

### F-02（暂定高）：无原始输入的公开验证路径弱于 receipt 所声称的 gate

- `validate_forecast_output` 只有在 `data is not None` 时才会重新运行每个 sensitivity shock；sensitivity completeness 也只在提供原始 `data` 时执行。
- 正式 `run_forecast` 会传入 `data`，因此正常生成路径确实经过强验证；但测试和其它消费者存在 `validate_forecast_output(result)` 的无输入调用。
- publication receipt 的固定 `gate_ids` 只有 `output_recomputation`，且 `build_publication_receipt` 是普通公开函数、receipt 是无外部签名的自哈希对象。任何能重算 receipt/result hash 的调用方都能构造“看似完整 gate”的候选；无输入 validator 是否能拒绝伪造 sensitivity 仍需用现有对抗测试/新诊断复现确认。
- `tests/test_publication_pipeline.py` 的正常 receipt 测试在 `run_forecast` 后再次调用的是 `validate_forecast_output(result)`（不带原始 input），说明下游示例本身采用较弱路径。

#### 动态复现结论（F-02 升级为 Critical）

- 使用现有 `forecast_document`、现有 `_republish`（公开 builder + 全 hash 重算）构造伪造 sensitivity terminals。
- `validate_forecast_output(forged)` 输出 `ACCEPTED`。
- `validate_forecast_output(forged, original_input)` 输出 `REJECTED:sensitivity down terminal recomputation mismatch`。
- 这直接违反设计目标 3“敏感性不可通过修改结果后重算 hash 绕过”，并证明 receipt 的 `output_recomputation` gate 在无输入验证路径中会过度声明。
- 影响面至少包括所有只持有 forecast artifact、不持有原始 input 的下游 consumer、markdown 渲染和独立工件审计。修复方向应是：正式工件携带足以自包含重算的不可变输入/快照引用，或 consumer 强制同时提供并核验原始 input，且 receipt 只能由强验证返回的验证上下文签发。

### Filing-fetch 结构索引

- 核心入口集中在 `resolve_filing` / `_run_company_wiki_json` / `load_company_wiki_root`，契约集中在 `filing_contracts.validate_request` 与 `validate_handle`。
- handle 专门测试覆盖路径越界、sha256、文件缺失、非 HTTPS、发布时间、byte size、resolve error 与扩展字段；这与 Phase 9 的 capture-ready 深验证目标高度吻合。
- 存在 4 个真实工具 conformance 场景以及显式 `FILING_FETCH_E2E_DOWNLOAD=1` 下载门，表面上符合“默认不产生外部下载、真实下载显式 opt-in”。

### Filing-fetch 实现审查（CodeGraph explore）

- `resolve_filing` 默认只调用 company-wiki `resolve`；只有显式 `allow_download=True` 才调用 `ensure --allow-download --acquisition-config ...`。reuse-first 与显式授权边界已真实实现。
- 每个请求先经 `identify`，再把 canonical_name/market/security_id 写入规范化请求；下载前还要求 market/security_id，身份 gate 不再被显式路径绕过。
- identify、resolve/ensure 共用单一 overall deadline，catalog lock 使用指数退避且受同一 deadline 约束；Phase 9/15 的 timeout 与锁竞争目标已实现。
- 客户端显式验证 resolve/ensure/identity/config schema versions，非预期 schema 会 fail closed；上游契约漂移保护已实现。
- 只接受 `reused_exact` / `reused_equivalent`、恰好一个 match、`capture_ready=True`，随后进入 `validate_handle` 深验证。handle 会验证 companies 子树、真实常规文件、HTTPS、sha256 格式/内容、byte size 等；旧审计 High-1/2/3 的核心缺口已有实质修复。
- filing-fetch 没有自身 market adapter/writer；下载由 company-wiki ensure 路由，符合 thin client / 单 owner 的目标。

#### 待确认点

- 根 revenue 仓库仍保留旧 `filing_acquisition.py`；filing-fetch 自身虽正确，不代表全系统 owner 已唯一化。
- 授权 receipt、gap receipt、request_id 与返回响应状态的完整字段未在 explore 可见片段全部展示，需由测试/实际调用继续核验。

### Company-wiki 核心符号索引

- 发行人归一相关核心符号为 `source_catalog/resolver.py::_entity_matches`。
- 下载/复用 owner 为 `source_catalog/acquisition_service.py::SourceAcquisitionService.ensure`，契约版本 `SOURCE_ENSURE_SCHEMA_VERSION="1.0"`。
- contract test 明确存在“首次下载并记录、后续零调用复用”场景，可用于验证 ensure 的幂等/reuse-first 行为。

### Company-wiki 实现审查（CodeGraph explore）

- `SourceAcquisitionService.ensure` 的职责边界清晰：coordinator 先 `resolve_or_stage`，只有 staged candidate + receipt 才交给唯一 `CanonicalSourceWriter.import_staged`，并把 reused/missing/ambiguous/downloaded/deduplicated/failed 全部写入 journal。单 writer 与授权/尝试审计目标已真实落地。
- resolver 只查询，不触发 acquisition side effect；只接受 `company_raw` 下 active + canonical + original_primary location，排除 dayu portfolio 外部路径，符合 filing-fetch 对 canonical companies 子树的安全边界。
- resolver 对 market/security_id、verified assertion、fiscal year/form/period/language/provider、published_date≤as_of、capture_ready、强 provider identity 分层筛选；无身份的 placeholder 会落到 MISSING 以允许授权下载，而具有可复用文件但身份不可验证时仍 fail closed。Phase 15 的“缺身份占位不误判冲突”与安全边界兼顾已有实现证据。
- Phase 18 的 issuer index 会把同一 canonical issuer 的 ticker/alias/security_id 归一，并对跨 issuer 共享 token 设置 ambiguous sentinel、拒绝作为 anchor；双类股/多地上市设计已真实实现，而非只写文档。
- ensure 的 acquisition journal 记录 request、adapter、candidate、provider、URL、content hash、canonical path 与结果，覆盖 gap/download 授权的可审计链主体。
- debug_trace 记录 entity gate 数量和逐候选排除原因，Phase 19.6 可观测性已落地于 resolver。

#### Company-wiki 风险/边界

- resolver 为兼容旧数据，把“非数字开头的候选 security_id 与请求不一致”视为 soft match；安全性依赖前置 entity/issuer gate 和其它文档条件。当前设计意图合理，但应有跨 issuer 反例测试持续钉住。
- explore 未返回 assertion retire/restore 与 scanner 的主体代码，因此这两项只能依赖专门 contract tests 和运行结果判断，证据强度低于 resolver/ensure。

### 旧 acquisition owner 可达性索引

- 根仓库 `scripts/filing_acquisition.py` 不是一个小兼容 shim：它仍包含 config、adapter registry、canonical writer、acquisition manager 和公开 `resolve_filing`，符号规模显示是一套完整 owner 实现。
- CodeGraph 目前只发现 `tests/test_filing_acquisition.py` 导入它；新的正式 client 是 `scripts/filing_fetch_client.py::resolve_filing`。若 SKILL/docs/CLI 已完全迁移且旧模块明确废弃，运行时 owner 可视为唯一；否则目标 7 未达成。

### F-04（High）：财报获取 owner 在文档层唯一、代码层仍双活

- SKILL 和 references 已把正式路径统一到 `filing_fetch_client.py → filing-fetch → company-wiki`，并明确标记旧模块 deprecated。
- 但 `scripts/filing_acquisition.py` 仍导出完整 `resolve_filing`、包含 CN/HK/US adapter/writer，并保留可执行 `main()`/`--allow-download` CLI；它不是不可调用的 fixture-only 代码。
- 因此“新调用方的 canonical owner”已经唯一，但设计目标 7 的更强表述“财报获取只有一个 canonical owner”尚未在代码/发布包层实现。旧 CLI 可被误用并绕开 filing-fetch/company-wiki 的新 identity、journal、contract 与治理门。
- 建议验收应要求：从发布包/安装 manifest 删除旧 owner，或把所有公开入口改成 hard-fail/转发 thin shim；测试 fixture 移入 tests，不再保留能直接下载/写 canonical 的生产 CLI。

### F-05（Medium）：SKILL/CHANGELOG/运行时版本与契约文档漂移

- SKILL Versioning 声称 schema 3.6 的 receipt “signed after output validation”，与 `run_forecast` 实际顺序冲突。
- SKILL Formal output gate 仍写“schema-3.4 workflow receipt”，而当前正式 schema 已是 3.6；schema 3.5 才是 legacy read-only。
- SKILL 的 deterministic tools 列表重复列出 `revenue_forecast.py` 与 `revenue_backtest.py`，且 input helpers 仍标注 schema 3.5。
- CHANGELOG v3.10.0 记录把 acquisition 内置 revenue 并移除 filing-fetch/company-wiki runtime，当前 Unreleased 又反向恢复 standalone filing-fetch，但 `SKILL_VERSION` 仍停在 3.10.0。当前安装物处于“版本号仍指向旧架构、Unreleased 文档指向新架构”的状态。
- 这些漂移不会直接改变数值结果，但会误导消费者选择验证/获取路径，降低设计契约的可执行性。

### 工作树/发布基线

- revenue：`main` 与 origin 对齐，既有 `.coverage` 修改；本次新增 `audit_review/`。HEAD `6ebbc38`（schema 3.6）。
- filing-fetch：`main` 与 origin 对齐，但有多项未提交/未跟踪改动，包括 `.gitignore`、CHANGELOG、real conformance test、pyproject、e2e support/tests 和计划文件；HEAD `fd95d30`。因此当前工作树能力高于已提交发布基线的可能性很大。
- company-wiki：`master` 与 origin 对齐，只有 `llm_cost_log.csv` 既有修改；HEAD `0793fbd`。
- invest-core / invest-framework 均为本地 master（无 upstream 显示），工作树干净。
- `.agents` 与 `.codex` 下的 revenue/filing skill 均是普通目录，不是 junction；安装同步必须靠复制/manifest 校验，不能假定自动跟随 canonical repo。

### Targeted 测试实跑

- revenue publication pipeline：16/16 通过。
- output report 对抗测试：18/18 通过。
- filing-fetch client：4/4 通过。
- SKILL CLI 文档一致性：3/3 通过。
- 这些结果确认现有断言稳定，但不会推翻动态发现的 F-02：现有 sensitivity 对抗测试只走带 input 强路径，因此测试全绿与无 input 漏洞可以同时成立。

### 全量测试实跑（第一轮）

- revenue：253/253 通过；tools sync suite 4/4 通过。运行中旧 `filing_acquisition.py` 触发未关闭 subprocess stream 的 `ResourceWarning`，是低级资源卫生问题，也再次说明 deprecated owner 仍在全量生产测试面内。
- filing-fetch：105 tests，6 failures、2 errors、4 skips，当前全量门不通过。
  - `test_e2e_isolated_wiki` 收集失败：`ModuleNotFoundError: company_wiki`。
  - UTF-8 中文 stdin 测试最终因子进程无法导入 company_wiki 而失败。
  - 多个 real-tool conformance 测试的 subprocess 输出解码发生 `UnicodeDecodeError`，随后 rc/stderr 断言失败。
  - 4 个真实下载测试按设计因未设置 `FILING_FETCH_E2E_DOWNLOAD=1` 跳过，不计为回归失败。
- 第一轮使用 Codex bundled Python。需检查项目预期解释器/安装方式；若默认 `python` 或项目环境能通过，则归类为 hermetic/环境声明缺口，若仍失败则是直接回归。

### F-06（待分级）：filing-fetch 当前测试与安装环境不自包含

- 新 isolated-wiki e2e 文件直接 import `company_wiki`，但 filing-fetch 仓库本身未提供可解析的 src path/依赖安装，违反 Phase 9“hermetic tests、不依赖真实默认 company-wiki”的目标至少一部分。
- real-tool conformance 对 Windows 子进程编码处理不稳，在非 UTF-8 stderr 下 reader thread 崩溃并把 stderr 变成 None；这使测试无法可靠区分业务失败与编码失败。

#### 解释器差异

- PATH `python` 是 `C:\Miniconda\python.exe`（3.13.9），可 import 本地 company-wiki；Codex bundled Python 3.12.13 不可 import。
- filing-fetch 的 untracked `pyproject.toml` 只有 ruff/coverage 配置，没有项目依赖、editable install 或 test pythonpath 声明。
- 因此 bundled Python 失败更准确地表明“测试依赖隐式全局安装/路径”，不是所有用户环境都会立刻发生的业务回归。已按计划文档的原始命令用 PATH `python` 复跑，当前 isolated-wiki 用例开始通过，等待完整汇总。

#### 第二轮结论（F-06 定级 Medium）

- 按计划原始命令、使用 PATH Miniconda Python 运行：117 tests 全部通过，5 skipped，耗时 88.1s。
- skips 中 4 项是真实下载显式门，1 项是生产 catalog 测试时锁定；其余 isolated-wiki、UTF-8 中文 stdin、identity CN/HK/US、生产 round-trip 均通过。
- 因此 filing-fetch 当前工作树的功能回归门在预期用户环境中为绿；F-06 不是功能 No-Go，而是“测试/发布依赖未声明、非 hermetic Python 环境会失败”的可移植性与复现性缺口。
- 计划/状态表仍声称 64/66/67 tests，已严重落后于当前 117 tests；当前新增 e2e 又是未提交文件，不能把 117 作为已发布 commit `fd95d30` 的证据。

### Revenue 完整质量门

- compileall 与 ruff 全绿。
- 253/253 tests 通过；coverage 使用独立临时 data file，未覆盖用户已有 `.coverage`。
- 总 statement coverage 87%，通过计划的 ≥84% 总门。
- 但计划还要求“新模块 coverage ≥90%”：`filing_fetch_client.py` 41%、`company_wiki_source.py` 81%、`model_registry.py` 89%、`revenue_backtest.py` 89%，`revenue_forecast.py` 在当前非 subprocess coverage 采集方式下为 0%。因此逐模块目标未达成或未被正确测量。

### F-07（Medium）：coverage 验收被总数掩盖

- 状态表用“coverage 87%”宣称完成，但它只证明总门；没有证明 Phase 0 对新增模块 ≥90% 的要求。
- 尤其新的正式 filing-fetch client 和 CLI 是跨项目关键边界，却分别只有 41%/0% 的直接 coverage。现有 CLI 测试虽通过，但 coverage 配置未采集子进程，且 library error/contract 分支仍有大量未覆盖行。
- 应按模块设 CI threshold，或明确修改计划目标；subprocess CLI 需启用 coverage multiprocessing/subprocess 支持或增加 in-process main tests。

### Company-wiki 全量门启动

- 使用 PATH Python 3.13.9 / pytest 9.0.1 收集 1630 项，正在运行；这是比根计划“1522/1543+”更高的当前基线。

### Filing-fetch 完整质量门

- compileall 与 ruff 全绿。
- 117/117 tests 通过，5 skipped；coverage 96%，通过 ≥90% 门，核心两个实现文件分别 96%/97%。
- 这是当前工作树的强证据，说明 Phase 9 的核心契约与大部分 Phase 15–19 修复在预期环境中质量较高。
- 限制仍是：e2e/pyproject 等关键增强未提交，依赖 Miniconda 的隐式 company-wiki 可导入状态；发布/新环境复现性尚未封口。

### Critical F-02 的跨项目影响确认（invest-core / framework）

- `invest-core/scripts/invest_contracts.py::validate_revenue_forecast` 调用 `report.validate_forecast_output(result)`，没有原始 input。
- `adapt_revenue` 随后只检查 receipt 自哈希、formal mode、freeform flag 和 `output_recomputation` gate 字样；它无法补做 sensitivity shock 的输入对照重算。
- 因而动态复现的伪造 sensitivity 工件不仅能通过独立 revenue validator，也能进入 invest-* 的 canonical adapter。这把 F-02 从“可能影响下游”升级为“已确认影响正式跨技能消费边界”。
- invest-framework 的 `bundle_validator`、`company_orchestrator` 继续复用 `validate_revenue_forecast`/`revenue_reference`，所以完整 bundle/receipt 的 hash 链会忠实绑定一个语义上已被弱验证接受的伪造 revenue 工件；hash lineage 不能修复上游验证缺口。

### Invest 单向依赖与去重初查

- 文档和实现都明确 revenue-forecast 是收入唯一 owner；invest-core 只适配冻结的 recognized/effective paths、target summary 和 growth-driver hashes，不重算收入。
- runtime import 会核对实际 `revenue_core.py` 路径与期望安装目录，Phase 11 的“防错误版本 import”已实现。
- framework manifest 禁止 revenue/profit/cash-flow override 与 scenario probabilities，要求每个 revenue segment 恰好覆盖一次；结构上满足单向依赖目标 8。
- 由于 invest-core 未初始化 CodeGraph，这部分是字面/运行证据，最终计划仍应包含为该仓库建立结构索引与 CI 影响分析的治理项。

### Invest 质量门

- invest-core：compileall/ruff 全绿，36 tests 通过、1 skipped。skip 是旧 schema 3.3 growth-driver 检查被 normalizer 自动补成 legacy summary 的设计项，需在计划中明确其兼容边界而不是长期用乱码原因文本跳过。
- invest-framework：compileall/ruff 全绿，22/22 tests 通过；异构 segments + constraints + SOTP 端到端用例已不再 skip，与根计划旧状态“18 OK / 4 skip”相比有进展。
- 两仓库的现有测试没有覆盖“可重签的伪造 sensitivity 在无 input revenue validator 下被 invest adapter/bundle 接受”。改进计划必须增加 revenue→invest-core→framework 的跨仓库 RED conformance test，随后统一修复上游验证契约。

### Revenue 安装同步核验

- `tools/sync_installations.py` 默认只检查一个 destination root；当前 `.agents/skills` 与 canonical revenue manifest 完全一致（58 files，exit 0）。
- 这证明 `.agents` 普通目录目前未漂移，但尚未证明 `.codex/skills`；需用显式 `--destination` 补查，并在改进计划中把所有受支持安装根加入同一 CI matrix。

### F-08（High）：安装副本严重漂移，发布同步目标未达成

- revenue `.codex/skills` 显式检查失败：34 个文件与 canonical 不一致，包含 SKILL、CHANGELOG、schema/migration/compliance 文档、核心脚本和测试；还出现 canonical 当前文件树没有的旧 `scripts/forecast/compute.py` 痕迹。
- revenue 默认 sync 命令只检查 `.agents`，因此日常“exit 0 / MATCH”会漏掉 `.codex`；这正是计划要防止的多安装副本漂移。
- filing-fetch `.agents` 与 `.codex` 都是复制目录且含运行产生的 `__pycache__`。`.agents` 缺当前 `references/identity.md` 与新增 e2e；`.codex` 甚至缺 SKILL.md、CHANGELOG、config 和 references，只剩 scripts/tests。
- canonical filing-fetch 的 e2e/pyproject 等又尚未提交，导致“canonical worktree / git HEAD / Agents 安装 / Codex 安装”至少四种状态并存。
- 影响：不同 Codex/Agents surface 会执行不同契约、版本和文档；F-02/F-04 即使未来只修 canonical，也可能在旧安装继续存在。
- 改进计划需先定义每个 skill 的唯一 canonical manifest，再让 `.agents`/`.codex` 两端都作为默认 `--check` 目标；拒绝 pycache/coverage/计划底稿进入安装包，并在发布前用哈希 manifest fail closed。

### Company-wiki 全量测试结论

- 1630 tests 中 1629 passed、1 failed，耗时 383.81s。
- 唯一失败：`tests/contract/test_source_catalog_worker_bootstrap.py::test_terminating_supervisor_does_not_leave_an_orphan_worker`。
- 失败点不是业务断言，而是测试读取 `.source_catalog/worker_launcher_events.jsonl` 时收到 Windows `PermissionError`。该场景的目的恰是验证终止 supervisor 后不留 orphan worker，因此文件仍被占用可能代表清理竞态/孤儿进程，也可能是测试时序 flaky；不能简单归为无关环境噪声。
- resolver、retire、security identity、URL enrichment、worker、source compatibility 等本次相关主体套件均通过，说明 Phase 15–18 的大部分修复没有广泛回归。

### F-09（暂定 Medium）：worker supervisor 终止/事件日志清理存在 Windows 竞态

- 全量门当前为红，且失败直接落在 Phase 16 worker 版本/进程治理目标上。
- 需 targeted 重跑并检查是否有残留进程/句柄；改进计划应包含确定性 teardown handshake、句柄关闭确认、进程树终止与可重复压力测试，而不是增加盲目 sleep。

#### F-09 复现分级

- 同一测试单独连续运行 3 次，3/3 通过（约 1.5–1.6s/次）。
- 因此它更像全量套件负载/前序状态触发的竞态，而非稳定功能错误；维持 Medium，不把 company-wiki 主体功能判为失败。
- 但全量 CI 仍不应标绿：改进计划要用 stress/repeat 与进程/句柄观测使该场景确定化，并验证无残留 worker，而不是把测试简单标 flaky/skip。

### Critical F-02 进一步扩展：snapshot/backtest 也走弱验证

- `revenue_backtest.validate_snapshot` 的 snapshot 明明同时包含 `input_document` 和 `forecast_result`，却调用 `validate_forecast_output(snapshot["forecast_result"])` 而没有传 `snapshot["input_document"]`。
- 因此 snapshot 具备强验证所需输入却未使用，理论上同一 sensitivity 伪造可在重算 `forecast_result_sha256` / `snapshot_id` 后通过；这会污染后续 backtest、accuracy record 和 confidence 证据链。
- 改进计划应把 validator API 拆成明确的 `validate_published_forecast(result, input)` 强入口；current schema 的 snapshot/invest/framework 一律必须传入并核对 input，只有显式 legacy read-only 路径才允许受限的 output-only 验证。

- `create_snapshot` 先通过 `run_forecast(frozen_input)`（强路径）生成结果，但随后又调用一次无 input validator；snapshot identity 只哈希 input/result hashes 等字段。攻击者若能同时改 result 并重算自哈希，最终安全性完全取决于 `validate_snapshot` 的弱调用。
- 现有 snapshot tamper tests 很可能只覆盖未同步重算所有相关 hash 的修改；改进计划需要新增“伪造 sensitivity + 重签 publication/result/snapshot 全部 hash”的 RED 用例。

### F-10（High）：legacy engine 兼容策略实际过宽 — 已精确取证

- Phase 0 要求 legacy schema 只接受 CHANGELOG 明列的 engine 版本，并禁止任意未知 engine。
- output validator 内联矩阵（`revenue_report.py:105-132`）：3.0→3.0.0、3.1→3.1.0、3.2→{3.2.0,3.2.1,3.3.0}、3.3→3.4.0、**3.4→当前 ENGINE_VERSION(3.10.0)**、**3.5→当前 ENGINE_VERSION**、3.6→当前。
- CHANGELOG 取证：schema 3.4 由 **v3.5.0**（2026-07-14）引入，并在 v3.6.0–v3.10.0 持续为当前 schema。因此真实 schema-3.4 工件可由 engine **3.5.0–3.10.0** 签发；当前代码只接受 3.10.0，会**错误拒绝真实历史工件**（过窄，兼容性回归）。
- 反向不一致：`validate_snapshot`（`revenue_backtest.py:72-75`）对非当前 schema **接受任意 engine**（过宽），与 output validator 的严格配对矛盾；同一工件在两条验证路径下结论可相反。
- 测试缺口：legacy 测试仅覆盖 3.1/3.1.0、3.2/{3.2.0,3.2.1,3.3.0}（`test_management_targets.py:142-179`）；**无** 3.3/3.4.0、3.4/{3.5.0..3.9.0}、3.5 任何配对用例。
- 根因：兼容策略硬编码在两个文件的 if-elif 链中且规则互相矛盾，无单一 immutable registry。改进计划需抽出共享 `(schema_version, engine_version, mode)` compatibility registry（含 CHANGELOG 溯源），由 forecast/output/snapshot/invest conformance 共用，并补齐 3.3/3.4/3.5 全配对测试。

### 正向确认：workflow/backtest 主体

- growth-driver tree 对 base 参数可达性、segment attribution、权重范围/和、evidence/反证等有实质结构验证；schema 3.6 headwind 负权重设计已落地。
- actuals 验证绑定 capture source/claim、as_of、币种单位、预测 horizon 与财年，历史审计所说的 actuals evidence 缺口主体已修复。

### F-11（Critical）：Phase 8 被标 completed，但 trusted workflow receipt 目标基本未实现

- Phase 8 明确要求：无 trusted verifier 的环境只能输出 draft；六类 communication 必须有 machine-generated event；`not_available` 缺 event 必须失败；自填 tool_call_id 不能代替 host receipt。
- 当前 capture contract 只要求非空字符串 `tool_name/tool_call_id`；测试 fixture 直接填 `test-browser`/`fixture-*` 即可产出 formal artifact。
- management `not_available.search_event` 在代码中是可选的；只有存在时才校验字段。自由文本 `search_description` 足以通过，正与 Phase 8.3 的禁止项冲突。
- `references/compliance-contract.md` 公开承认 tool invocation、search exhaustiveness、source retrieval truth 均依赖 host trust；但 runtime 仍可签发 `formal_output_mode="formal"`，没有 trusted verifier/fail-to-draft gate。
- sensitivity completeness 仍是 `require_sensitivity_completeness` opt-in；formal artifact 可以不证明所有 Base assumption/stress parameter 已测试或结构化排除，与顶层“正式流程不能无痕跳过敏感性”冲突。
- 根计划 Phase 8 的全部 checklist/验收项仍是 `[ ]`，而标题/状态表写 completed；这是本次最典型的伪完成。

#### F-11 改进方向约束

- 不应在纯 Python schema validator 内伪造“可信 host 签名”；需要明确定义 runtime capability：有 trusted verifier → formal，无 → draft/unattested 且 invest 拒绝。
- host receipt 必须绑定 normalized request/response hash、tool/action、timestamp、environment、issuer，并由不可由输入作者调用的 verifier 验证。
- communication/search、capture/open、exception approval 与 sensitivity exclusion 应共享同一 attestation contract，而不是继续增加自填字符串字段。

### F-12（High）：compliance-contract 与真实签发顺序相反

- compliance 文档明确写“validator then signs”，SKILL 也写“signed after validation”；代码实际先 `build_publication_receipt` 再 validator。
- 这不是普通文案过时，而是正式可信链的核心顺序被文档错误陈述。改进计划必须先修两阶段 API/测试，再更新文档；不能只改说明去适配当前顺序。

### F-13（Medium）：Company-wiki 静态质量门不通过

- compileall 通过；`ruff check src scripts tests` 失败，共 6 项：5 个 unused import、1 个 unused local。
- 问题集中在 `test_source_catalog_download_suppression.py` 与 `test_source_catalog_retire.py`，都属于本次设计范围的 contract tests。
- 根计划/进度曾声称 company-wiki ruff 全绿，因此当前工作树或未提交测试演进已造成质量门回归。
- 改进计划应把 ruff 作为 company-wiki PR 必跑门，并清理/确认 unused test helper 不代表测试夹具未真正接入断言。

### Worker 进程观测

- 全量测试结束后没有发现 pytest 临时目录下的孤儿 worker；仅看到 production `source_catalog_worker.ps1` 与其 Python worker，使用 canonical project/config 且带 120s startup delay。
- 这支持 F-09 是测试负载/句柄关闭竞态，而非本次运行稳定遗留 orphan；仍需确定性 teardown 机制。

### F-03（中）：版本/计划基线漂移

- 当前代码常量是 `SKILL_VERSION=ENGINE_VERSION="3.10.0"`、`FORECAST_SCHEMA_VERSION="3.6"`；Phase 0 仍写目标 skill 3.11.0、正式 schema 3.5。
- 后续 Phase 20 状态表声称 schema 3.6 已完成，能解释 schema 更新，但未解释 skill 版本为何倒退到 3.10.0，也未同步 Phase 0 发布决策。
- validator 对 3.4/3.5 的 engine 兼容均绑定当前 `ENGINE_VERSION`，与 Phase 0 的“3.4 只接受列入 CHANGELOG 的历史 engine”表述不同。需结合 CHANGELOG/迁移测试判断是设计演进还是兼容回归。

### 对抗测试索引

- 已存在三类“修改语义后重算所有 hash”的测试：非法概率、伪造管理目标比较、伪造敏感性 terminal。
- publication suite 还包含 `test_public_api_never_returns_pass_receipt_before_output_validation`、draft receipt、receipt tampering、CLI 验证失败不写 JSON 等测试。
- 这些测试名称说明计划中的核心威胁模型已被编码，但是否覆盖无输入 validator/公开 receipt builder 的组合仍需读断言与动态复现；测试名称本身不是通过证明。

### Publication 测试深度

- `test_public_api_never_returns_pass_receipt_before_output_validation` 实际检查的是 `workflow_compliance_receipt` 不得同时含 `status=pass` 和 `output_recomputation` gate；它没有监控 `build_publication_receipt` 与 validator 的调用顺序。
- 因此该测试可以在当前“publication receipt 先构造、validator 后调用”的实现下通过，不能关闭 F-01。
- CodeGraph 对 `test_rehashed_forged_sensitivity_terminals_are_rejected` 返回的代码主体却是 management-target 伪造用例，符号名与源码内容明显不一致。对该具体测试需改用已定位文件的字面读取/实际执行，避免基于错配片段下结论。

### 对抗测试字面核验

- sensitivity 伪造测试确实存在，但最终调用是 `validate_forecast_output(forged, data)`；它只证明带原始输入的强验证会拒绝伪造，没有覆盖 `validate_forecast_output(forged)`。
- 测试辅助 `_republish` 直接调用公开 `build_publication_receipt` 并重算 `result_sha256`，与 F-02 的攻击/误用模型完全一致；因此可直接用现有 fixture 做无输入诊断复现。
- `test_draft_carries_no_publication_receipt` 测的是私有 `_build_forecast_draft`，不是 `run_forecast(mode="draft")`；测试名可能让读者误以为公开 draft 模式不携带 receipt，实际未证明。
- 多处正常测试和 markdown 渲染调用 `validate_forecast_output(result)`，确认无输入路径是正式可见行为，而非仅内部遗留。

### F-02 扩展到 snapshot/backtest：动态复现确认（Critical 维持）

- 探针 `audit_review/probe_snapshot_forgery.py`（只读诊断，不进产品测试套件）：
  1. `create_snapshot` 正常生成含 sensitivity_tests 的 snapshot；
  2. 篡改 `forecast_result.sensitivities[0]` 的 down/up terminal 并重算派生 impact 字段；
  3. 用公开 `build_publication_receipt` + `canonical_sha256` 重算 receipt、`result_sha256`、`forecast_result_sha256`、`snapshot_id` 全部哈希。
- 结果：`validate_snapshot(forged)` → **ACCEPTED**；`validate_forecast_output(forged_result, input_document)` → **REJECTED:sensitivity down terminal recomputation mismatch**。
- 结论：`revenue_backtest.py:78` 的 `validate_snapshot` 在持有 `input_document` 的情况下仍走弱验证路径，F-02 确认污染 snapshot/backtest/accuracy record 证据链。现有 snapshot tamper tests 未覆盖"伪造语义+全哈希重签"组合。

### F-14（Low）：filing-fetch 授权链完整但无客户端可见 gap/authorization receipt

- `fetch_filing.py:419-474`：`allow_download=True` 才走 `ensure --allow-download --acquisition-config`，且强制 market/security_id；响应只接受 `reused_exact`/`reused_equivalent`，其它 status fail-closed 并带 reason/debug_trace。
- `request_id` 由 resolution 注入 handle，`filing_contracts.validate_handle` 强制非空 trimmed；缺失有专门测试拒绝（test_fetch_filing.py:1874）。
- 下载授权/审计链在 company-wiki 侧真实存在：`acquisition.py:389-437` 验证 DownloadReceipt（candidate/provider/URL/sha256/byte_size/mime/HTTP 2xx），`canonical_writer.py` 二次校验并写 provenance（含 receipt 全字段），journal 记录 downloaded_new 等 outcome；e2e `test_e2e_download.py` 实跑通过。
- 残余缺口（Low）：filing-fetch 返回契约中没有一等 gap receipt / authorization receipt 字段；"确认缺口→获授权→下载"的证据只在 company-wiki journal/provenance 服务端，不随 handle 返回给 revenue 消费方做本地留档。计划中"授权审计"目标以 flag+journal 形式落地，审计算可追溯，但消费端无法自证本次调用经过授权。
- 此前"返回状态字段未全部展示"的待确认点已关闭：状态门与 request_id 门均有实现+测试证据。

### Company-wiki retire/restore 与 scanner 证据补强（原待确认点关闭）

- retire/restore：`store.py:334-414` 实现确认。软删除（documents/locations 置 retired）、事务内写 `document_retire_audit`/`document_restore_audit`（reason/actor/time）、restore 只允许从 retired 态恢复；`tests/contract/test_source_catalog_retire.py` 6/6 通过。证据强度从"仅测试"升级为"实现+测试"。
- scanner（1266 行）：虽只有 2 个直接命名测试（focus admission），但 `canonical_writer.py:185` 在每次 canonical 写入后调用 `scan_catalog` 重扫目录并立即 exact re-resolve（`canonical_writer.py:205-209` 失败即 CanonicalImportError）。因此 scanner 处于 ensure/download 热路径，被全部 import 契约测试与 filing-fetch e2e 间接覆盖。resolver/resolve 热路径不经过 scanner。结论：scanner 证据强度可接受，不再列为缺口；但建议改进计划为 scan_catalog 增加 1-2 个确定性直接单测（当前直接断言面薄）。

### Invest 结构证据补强（CodeGraph 已初始化，用户授权）

- invest-core CodeGraph：6 文件、183 节点、177 边，索引健康。
  - `validate_revenue_forecast(result)` 定义于 `scripts/invest_contracts.py:258`，签名**只有 result，无 input 参数**。
  - `adapt_revenue(result, scope, segment_name)` 定义于 `invest_contracts.py:631`，同样**无 input 参数**。
- invest-framework CodeGraph：149 节点、143 边，索引健康。
  - `company_orchestrator.py:27` 与 `bundle_validator.py:24` 均从 invest-core import `validate_revenue_forecast`/`revenue_reference`。
- 结构性结论：整个 invest 消费链上**没有任何函数接受原始 input document**，强验证在 invest 侧结构上不可能补做。F-02 跨项目穿透从"字面证据"升级为"字面+结构双重确认"，修复必须在 revenue 侧让正式工件自包含可验证（或 receipt 由强验证上下文签发），invest 侧只需消费新契约。

### 范围工具限制

- `invest-core` 未初始化 CodeGraph，结构性审查暂不能按项目 AGENTS.md 的首选路径进行。需用户授权初始化，或在最终报告中把该部分证据强度降级并仅做字面/运行核验。
