# 多根 Filing Data Lake — 逐工作单实施卡

> 状态：runbook_in_progress  
> 绑定计划：task_plan.md 2.0-full-refactor-safety  
> 权限边界：本轮仅编制计划；本文件不是立即实施授权。

## 使用规则

每个 WU 必须有一张完整实施卡。实施者只可执行一张卡；不得把卡片中的 inherited gate 理解为可选。卡片字段为：

- Owner/Targets：唯一 owner 仓和允许触碰的模块族；精确文件清单须在 CP0 按当前 CodeGraph/HEAD 生成。
- Inputs：依赖 receipt、ADR/schema/config/fixture/commit。
- RED/Focused：实现前失败的测试 ID 与 focused gate。
- Mutation：至少一个能证明测试强度的错误改动。
- Audit：必须产生的 diff、计数、spy、hash、migration 或调用图证据。
- Rollback：可执行的恢复点；仅写 git revert 而无数据/flag 说明不合格。
- Accept：本卡独立放行条件；同时继承 task_plan 的 repo/cross-repo/reviewer 门。

## 全局继承门

所有卡片均继承：

1. CP0~CP8、WU 状态机和机器可读 receipt。
2. 三仓 HEAD/status、collection manifest、真实根 before/after。
3. focused GREEN → owner repo GREEN → 受影响仓 GREEN → cross-repo GREEN。
4. network/download/parser/LLM/external/canonical write 精确预算。
5. 定向 mutation 必须先使指定测试失败，恢复后再全绿。
6. 独立 reviewer 不得是实现者；有 finding 时退回最早失效状态。
7. 外部根只读、无授权不下载、不自动 restore、不 silent fallback。

## 命令与路径字典

以下为命令 alias；实施时 receipt 必须保存展开后的完整命令、cwd、环境变量和 exit code。

### 通用

- GIT-BASE：三个仓分别运行 git status --short、git rev-parse HEAD、git branch --show-current。
- CG-BASE：三个仓分别记录 CodeGraph status/index timestamp；结构影响用 context/impact，不用 grep 代替。
- PLAN-GATE：验证 task_plan、runbook、receipt schema、WU 唯一性、依赖、plan hash、开放占位项。
- ROOT-PROBE：三个真实根的 privacy-safe inventory/mtime/hash 探针；默认只读。
- SPY-GATE：核对 network/download/parser/LLM/external_write/canonical_write 的精确预算。
- COLLECTION-GATE：按仓保存 pytest collect-only node IDs；任何消失、skip、xfail 变化需解释。

### company-wiki 当前基线

- CW-LINT：ruff check src tests/unit tests/contract scripts。
- CW-COMPILE-CONFIG：python -m compileall -q src scripts tests；python scripts/config_doctor.py。
- CW-UNIT：python -m pytest tests/unit -q --tb=short。
- CW-CONTRACT：python -m pytest tests/contract -q --tb=short。
- CW-UNIQUE：python tools/check_unique_test_symbols.py。
- CW-MUTATION-BASE：现有 artifact_handle/source_bundle/download_authorization/gap_plan/fail_closed/determinism 六文件集合。

### company-wiki 目标新增门

- CW-INTEGRATION：python -m pytest tests/integration tests/acceptance -q --tb=short。
- CW-SOURCE-FOCUSED：运行本计划新增的 config/metadata/adapter/resolver/migration/bundle 测试 node IDs。
- CW-FULL：CW-LINT + CW-COMPILE-CONFIG + CW-UNIT + CW-CONTRACT + CW-INTEGRATION + CW-UNIQUE + CW-MUTATION-BASE。
- CW-PY-MATRIX：至少在 3.11/3.12/3.13 跑 source contract/schema/adapter/resolver 关键集合。

### filing-fetch 当前基线

- FF-LINT：ruff check scripts tests tools e2e；python -m compileall -q scripts tests tools e2e。
- FF-HERMETIC：python -m pytest tests -q --tb=short，排除 test_real_tool_conformance.py 与 test_e2e_download.py；排除事实必须写 receipt。
- FF-BASE-E2E：python e2e/run_companies_reuse_only_e2e.py。
- FF-SYNC：python tools/sync_installs_b3.py --check。

### filing-fetch 目标新增门

- FF-FOCUSED：运行新增 bundle-v2、policy-hash、exact/latest/download、subprocess protocol 测试。
- FF-REAL-CONFORMANCE：仅在显式网络/真实工具授权的隔离 job 运行 test_real_tool_conformance.py。
- FF-DOWNLOAD-E2E：仅在显式下载授权的隔离 job 运行 test_e2e_download.py；未授权时必须 reported-not-run，不能伪绿。
- FF-FULL：FF-LINT + FF-HERMETIC + FF-BASE-E2E + FF-FOCUSED + FF-SYNC。

### revenue-forecast 当前基线

- RF-LINT：ruff check scripts tests tools e2e；python -m compileall -q scripts tests tools e2e；python tools/check_unique_test_symbols.py。
- RF-TEST：python -m pytest tests tools/tests -q。
- RF-COVERAGE：python tools/run_coverage_gates.py。
- RF-ENGINE-E2E：python e2e/run_revenue_forecast_e2e.py。
- RF-SYNC-MUTATION：python tools/sync_installations.py；python tools/mutation_patrol.py --samples 5。
- RF-AUDIT：python scripts/publication_registry.py audit；运行 plan claim 与 closure ledger gate。

### 三仓目标新增门

- XR-CONTRACT：按 release manifest checkout 三仓 commit matrix，运行 N-1/current 协议矩阵。
- XR-E2E：从 revenue source-preparation 子进程启动 filing-fetch 与 company-wiki，运行 Phase 12 mandatory cross-repo IDs。
- XR-MUTATION：运行 12 个定向业务 mutation 与 RF-01~12 对应切换 mutation。
- XR-FULL：CW-FULL + FF-FULL + RF-LINT/RF-TEST/RF-COVERAGE/RF-ENGINE-E2E/RF-SYNC-MUTATION/RF-AUDIT + XR-CONTRACT + XR-E2E + XR-MUTATION。

当前 CI 不包含的门不得标记 passed；只能标 not_run_with_reason，且对应 Phase 不能 accepted。

## Phase 1 卡片

### WU-101

- Owner/Targets：revenue audit tooling；只读三仓 git/CodeGraph/config/test collection，新建 baseline receipt/validator，禁止产品模块。
- Inputs：三仓当前 HEAD/status、既有用户脏路径、task plan hash。
- RED/Focused：BASE-01~04；先证明 HEAD/config/test 删除/plan drift 能使 validator 失败。
- Mutation：伪造一个 commit、移除一个 node ID、把用户脏文件列入 allowed files。
- Audit：三仓 commit/config hash/collection/CodeGraph 状态和 dirty allowlist。
- Rollback：删除本 WU 新生成的临时 baseline/receipt；不清理用户文件，不改变三仓 HEAD。
- Accept：validator 杀死三种 mutation，独立 reviewer 复算 hash，产品 diff=0。

### WU-102

- Owner/Targets：company-wiki tests/helpers 与 tests/fixtures/source_lake_v2；只放合成文件、manifest 和 factory。
- Inputs：WU-101 accepted、Normalized 目标字段草案、三根布局清单。
- RED/Focused：FIX-01~04；fixture 泄漏真实绝对路径、字节/hash 不一致、future_root 特例、产生外部副作用时失败。
- Mutation：篡改一份 PDF bytes、不改 manifest；把真实 Dropbox 路径写入 fixture。
- Audit：fixture tree、sha256 manifest、可重建命令、三次生成 hash。
- Rollback：移除 temp fixture build；仓库中只 revert 本卡 fixture/helper 提交。
- Accept：Windows 非 ASCII 路径可重复构建，真实根 probe 不变，reviewer 随机复算至少五个 hash。

### WU-103

- Owner/Targets：revenue audit_review 与 plan verifier；closure mapping/claim gate，不改产品文档声明。
- Inputs：WU-101、F-034~060、D-001~021、旧计划 superseded 清单。
- RED/Focused：无 owner finding、无测试关闭条件、旧 config-only 声明或错误 plan hash 必须失败。
- Mutation：删除 F-051 mapping；把 superseded 结论改为 completed。
- Audit：finding→WU→test→receipt 图和 orphan/duplicate report。
- Rollback：revert verifier/mapping 提交；不触碰历史审查原文。
- Accept：27 条 finding 全部唯一映射，claim mutation 被拒，reviewer 查无 orphan。

### WU-104

- Owner/Targets：revenue cross-repo audit/e2e tooling；company scanner/resolver、filing CLI、revenue 当前入口只读 trace adapter。
- Inputs：WU-101/102、现有 v1 命令与合成 fixture。
- RED/Focused：CHR-01~04；同输入 trace 不确定、未标 known-bad、调用预算变化、越权读取均失败。
- Mutation：交换候选排序；隐藏一次 parser 调用；把 known-bad 标 expected_good。
- Audit：expected_good/known_bad/compatibility_only golden trace pack、三次 canonical hash、调用预算。
- Rollback：关闭 trace adapter/revert audit harness；v1 产品响应始终不变。
- Accept：每个现有 root/入口均有正常和失败 trace，known-bad 全有后续 RED owner。

## Phase 2 卡片

### WU-201

- Owner/Targets：company-wiki architecture ADR；三仓只增加 architecture contract tests。
- Inputs：Phase 1 receipts、D-001~021。
- RED/Focused：ARCH-01~05 先构造 adapter→store、resolver→adapter、calculator→network 等逆向依赖并失败。
- Mutation：在 resolver 导入 scanner；在 adapter 注入 CatalogStore。
- Audit：职责/禁止依赖图、保留/重构/删除模块清单、三仓 reviewer sign-off。
- Rollback：仅 revert ADR/tests；此阶段无 runtime 改动。
- Accept：所有边界无开放选择，architecture RED 能阻止逆向依赖。

### WU-202

- Owner/Targets：company-wiki source_catalog schema/models 设计文件与 contract fixtures。
- Inputs：WU-201、现有 assertion 字段、市场/期间/form 语义。
- RED/Focused：META-01~12 和 v1/v2 compatibility golden。
- Mutation：删除 security_id 或 content hash；交换 period_end；允许 unknown schema。
- Audit：JSON Schema、字段 evidence 规则、canonical hash vectors、compatibility matrix。
- Rollback：revert schema/fixture 提交；无 DB migration。
- Accept：所有必需/空值/冲突/版本规则机器可验证，filing/revenue reviewer 能消费 fixture。

### WU-203

- Owner/Targets：company-wiki gap/resolver contract ADR，filing-fetch request contract tests。
- Inputs：WU-202、现有 latest/gap 行为刻画。
- RED/Focused：exact 不应 discovery、latest 只补 gap、revision 保留、授权 hash 失效场景。
- Mutation：让 exact 调 discovery；把 covered period 加入 missing。
- Audit：exact/latest 状态机、GapPlan 字段、side-effect budget 表。
- Rollback：revert ADR/tests；不改现有 gap runtime。
- Accept：每条复用/发现/下载转换有唯一条件和负例，三仓语义一致。

### WU-204

- Owner/Targets：company-wiki source_bundle/artifact_handle contract；filing/revenue compatibility fixtures。
- Inputs：WU-202、现有 artifacts/evidence schema和 producer versions。
- RED/Focused：B-01~12 contract vectors，DAG invalidation golden。
- Mutation：忽略 producer version、input hash 或 policy hash。
- Audit：bundle schema、artifact role DAG、selected/rejected reason、N-1/current fixtures。
- Rollback：revert additive contract fixtures；现有 v1 reader不变。
- Accept：每种 hash/version/binding 变化产生最小且确定的重算集合。

### WU-205

- Owner/Targets：company-wiki architecture_gate 与三仓 import/caller fitness tests。
- Inputs：WU-201~204 frozen ADR。
- RED/Focused：ARC-FIT-01~06；每条禁止依赖和 legacy 新 caller 都可检测。
- Mutation：给 v1 scanner 增加新 root caller；让 revenue calculator import filesystem client。
- Audit：目标模块图、CodeGraph caller/impact baseline、保留/新增/删除清单。
- Rollback：revert fitness tests/blueprint；runtime 仍无改动。
- Accept：目标架构可执行检查覆盖所有关键边界，独立 reviewer 确认无第四套平行框架。

## Phase 3 卡片

### WU-301

- Owner/Targets：company-wiki source_catalog/config.py、config schema/doctor、对应 contract tests。
- Inputs：Phase 2、现有 source_catalog YAML/config baseline。
- RED/Focused：CFG-01~08。
- Mutation：允许重复 root_id、unknown adapter、external read_only=false 或 route 重叠。
- Audit：解析后 RootPolicy canonical JSON/hash、错误 reason、配置 golden。
- Rollback：默认继续加载 v1 config；revert additive v2 parser，生产配置不改。
- Accept：无效配置 fail closed；同物理文件唯一 route；旧配置兼容矩阵通过。

### WU-302

- Owner/Targets：company-wiki adapters registry/capabilities 与 conformance registration tests。
- Inputs：WU-301、WU-205 boundary。
- RED/Focused：unknown ID/version/capability 不匹配、动态 import 字符串必须拒绝。
- Mutation：让 registry fallback 到最后 adapter；允许配置 module path。
- Audit：注册 ID/version/capability 表及每个 adapter conformance receipt 绑定。
- Rollback：v1 默认；移除未启用 registry 提交即可。
- Accept：配置只能选择受审 ID；future_root 可复用已注册能力，unknown layout 不误解析。

### WU-303

- Owner/Targets：company-wiki policy export；filing-fetch/revenue policy snapshot readers及兼容测试。
- Inputs：WU-301/302、三仓当前 allowlist baseline。
- RED/Focused：POL-01~03；consumer 本地 allowlist 不得扩大权限。
- Mutation：篡改 policy hash、使用过期 snapshot、增加未授权 path。
- Audit：canonical export、隐私 redaction、三仓 round-trip 与单一 owner 调用图。
- Rollback：consumers 默认继续 v1 配置；关闭 v2 policy reader，无配置迁移。
- Accept：三仓同一 policy hash，重复 allowlist 不再具有授权效力。

### WU-304

- Owner/Targets：company-wiki config/control/startup 与 flag contract tests。
- Inputs：WU-303、R0~R11 波次。
- RED/Focused：每个独立 flag 的默认、依赖、观测和回滚测试。
- Mutation：用一个总开关同时启 scan/persist/resolve/download。
- Audit：flag graph、默认值、每状态允许的读写预算。
- Rollback：全部 v2 flags 默认 false；revert flag parser 不影响 v1。
- Accept：非法组合启动失败，任何单 flag 可独立关闭且不改数据。

### WU-305

- Owner/Targets：company-wiki control/config_doctor/wave state；incident receipt tests。
- Inputs：WU-304、cohort schema、error budgets。
- RED/Focused：FLAG-01~08。
- Mutation：breaker 反向迁移 DB；并发 reload 让单请求读两个 snapshot。
- Audit：状态机、cohort isolation、incident/rollback receipt、原子 config reload trace。
- Rollback：breaker 仅将后续请求 flag 切 v1；恢复上一个签名 policy snapshot。
- Accept：八类异常均阻止推进；无 silent fallback、无 catalog/外部文件反向修改。

## Phase 4 卡片

待补齐 WU-400~404。

## Phase 5 卡片

待补齐 WU-500~503。

## Phase 6 卡片

待补齐 WU-601~604。

## Phase 7 卡片

待补齐 WU-701~704。

## Phase 8 卡片

待补齐 WU-801~806。

## Phase 9 卡片

待补齐 WU-901~906。

## Phase 10 卡片

待补齐 WU-1000~1005。

## Phase 11 卡片

待补齐 WU-1101~1105。

## Phase 12 卡片

待补齐 WU-1201~1202。

## Phase 13 卡片

待补齐 WU-1301~1306。

## Phase 14 卡片

待补齐 WU-1401~1406。

## Phase 15 卡片

待补齐 WU-1500~1505。

## Runbook 完整性门

- 74/74 WU 卡片存在。
- 每张卡七字段非空且 owner/target/依赖与 task_plan 一致。
- 不存在开放占位项。
- machine validator 可检测删卡、重复 ID、空字段、错误依赖、plan hash 漂移。
