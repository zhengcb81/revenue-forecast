# 多根 Filing Data Lake — 逐工作单实施卡

> 状态：runbook_complete_ready_for_review  
> 绑定计划：task_plan.md 2.1-full-refactor-execution-cards  
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
8. 推送前 CI 预检（task_plan「推送前 CI 预检」七项）：忽略文件检查、CI=true 等价干跑、新 step 首次预检、平台差异确认、跨仓时序（producer 先推且绿）、未跟踪文件确认、预检记录入 receipt；任一失败先修再推。

## 文件边界

CP0 必须用当前 HEAD/CodeGraph 生成精确 allowlist；下列是允许模块族上限，CP0 只能收窄，扩大必须修订计划：

- Phase 1：revenue audit_review/tools/tests，company-wiki tests/fixtures/helpers；禁止产品runtime。
- Phase 2：三仓 docs/contracts/schema fixtures/architecture tests；禁止行为切换。
- Phase 3：company-wiki source_catalog config/control/startup/authorization、配置schema/doctor；filing/revenue只允许policy reader与compat tests。
- Phase 4：company-wiki store/assertion_service/models/normalizer/legacy bridge及contract tests；只additive schema。
- Phase 5~8：company-wiki scanner/adapters/admission/resolver/source_bundle/gap/query/indexes及对应tests。
- Phase 9：company-wiki migration/restore/journal/control和复制库工具；真实catalog apply需另行授权。
- Phase 10~11：company-wiki CLI/contracts、filing scripts/contracts/tests、revenue source client/orchestrator/contracts/tests；forecast calculator只允许纯输入contract适配，不允许I/O。
- Phase 12~14：三仓 tests/e2e/tools/workflows/release control；生产canary与CI隔离。
- Phase 15：明确列出的legacy模块、docs/config注释；删除按scanner/resolver/protocol/config四提交。

永久禁止目标：

- 三个真实外部资产根中的任何文件/sidecar写入、移动、重命名或删除。
- 未获生产变更授权时的真实catalog migration/apply/restore。
- 用户非本任务脏文件、llm_cost_log.csv、source_manifests/archive。
- 任意环境中的密钥、凭据、Dropbox内容副本或未redact路径写入receipt。
- 与本计划无关的格式化、依赖升级、重命名或技术债顺手修复。

## Reviewer 与审计角色

- Contract reviewer：Phase 2/3/4/10，检查schema、兼容性、版本与安全语义。
- Test-strength reviewer：每个WU在RED冻结前检查断言、负例、side-effect budget和mutation。
- Catalog/migration reviewer：Phase 4/8/9，独立检查DDL、事务、对账、backup/restore。
- Security reviewer：Phase 3/5/7/8/11，检查path/hash/identity/provenance/status/authorization。
- Cross-repo reviewer：Phase 10~12，检查真实子进程边界和commit matrix。
- Production canary reviewer：Phase 13，核验真实样本资格、隐私和只读探针。
- Release/adversarial reviewer：Phase 14/15，不依赖作者摘要，重跑mutation/rollback/CodeGraph。

同一模型可实施多个WU，但不得自任该WU独立reviewer。Phase 9 apply/restore、Phase 13真实canary、Phase 14发布至少需要两类不同reviewer共同签字。

## 证据目录约定

- receipts/WU-ID.json：机器状态与命令结果。
- baselines/：commit/config/collection/CodeGraph/真实根privacy-safe基线。
- red/WU-ID/：RED命令、退出码、失败摘要和commit。
- test-results/WU-ID/：focused/repo/cross-repo、collection、coverage和spy JSONL。
- diffs/WU-ID/：v1/v2结构化diff、known-bad分类和review。
- mutations/WU-ID/：mutation diff、杀手测试、恢复hash。
- migrations/WU-ID/：dry-run/journal/reconciliation/backup ID，禁止存真实DB副本。
- reviews/WU-ID/：reviewer findings与最终decision。
- incidents/：stop-the-line/breaker/override/rollback。

证据必须引用不可变commit/config/policy/schema/catalog snapshot hash；日志摘要不能代替原始机器结果。任何目录缺失或hash不匹配，卡片状态退回对应最早检查点。

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
- RED/Focused：无 owner finding、无测试关闭条件、旧 config-only 声明、错误 plan hash、runbook 缺卡/重复/空字段必须失败。
- Mutation：删除 F-051 mapping；删除 WU-704 卡片 Rollback 字段；复制一个 WU ID；把 superseded 结论改为 completed。
- Audit：finding→WU→test→receipt 图、74卡集合/字段/version/hash与 orphan/duplicate report。
- Rollback：revert verifier/mapping 提交；不触碰历史审查原文。
- Accept：27 条 finding 全部唯一映射；74卡完整；claim/card四类mutation被拒；reviewer查无 orphan。

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

### WU-400

- Owner/Targets：company-wiki source_catalog/store.py、assertion_service.py、schema migration tests；仅 additive schema。
- Inputs：Phase 2 schema、WU-301 policy、生产 schema 只读快照。
- RED/Focused：旧/新 schema owner 漂移、缺 visibility/epoch、重复 writable truth source 必须失败。
- Mutation：再建第二 assertion 表；让 verified+shadow 可见。
- Audit：单一 DDL owner、migration SQL/hash、v1 row compatibility、index/query plan。
- Rollback：fixture/temp DB 恢复；生产未 apply。未来 apply 后只回 reader/visibility，不 drop columns。
- Accept：现表可表达 v2 全字段和 rollout visibility，初始化/upgrade DDL 不漂移。

### WU-401

- Owner/Targets：company-wiki source_catalog/models.py、normalizer.py、schema helpers/tests。
- Inputs：WU-400、META golden。
- RED/Focused：META-01~12、round-trip、property tests。
- Mutation：canonical hash 包含绝对路径/扫描时间，或排除 security_id。
- Audit：serialization vectors、hash vectors、unknown version/errors。
- Rollback：v2 model 未接生产 writer；revert模块和 fixtures。
- Accept：同语义跨 root hash 一致，影响复用的任一字段变化都会改 normalized hash。

### WU-402

- Owner/Targets：company-wiki CatalogStore transaction/persister 与并发 tests。
- Inputs：WU-401、temp catalog fixture。
- RED/Focused：TX-01~03 及每个写步骤 fault injection。
- Mutation：在 document 写后故障但提交；移除幂等 unique key。
- Audit：事务 trace、行数 before/after、并发结果、foreign_key_check。
- Rollback：失败事务自动 rollback；revert writer flag，保留已审计历史。
- Accept：零部分提交、零重复 active assertion、metadata change 形成可审计新 assertion。

### WU-403

- Owner/Targets：company-wiki scanner/normalizer URL enrichment 与 assertion tests。
- Inputs：WU-402、同公司多期间不同 bytes fixture。
- RED/Focused：N-06、多期间 URL/period/provider_document_id 强绑定测试。
- Mutation：恢复 company_name→first URL map。
- Audit：每个 backfill join key/evidence pointer、unresolved remediation queue。
- Rollback：关闭新 backfill；不恢复错误广播，不覆盖旧审计记录。
- Accept：没有强文档键就不补 URL，错误 legacy 测试被正确 RED 替代。

### WU-404

- Owner/Targets：company-wiki legacy bridge、resolver v1 filter、visibility/activation tests。
- Inputs：WU-400~403、v1 golden。
- RED/Focused：VIS-01~05、legacy/v2 parity。
- Mutation：v1 读取 verified+shadow v2；请求中途切 epoch。
- Audit：bridge_hits、visibility state transitions、per-request snapshot trace。
- Rollback：关闭 bridge/v2 writer；v1 固定读 v1 schema，v2 rows保留不可见。
- Accept：shadow row绝不影响 active response，激活/回退原子且不删 assertion。

## Phase 5 卡片

### WU-500

- Owner/Targets：company-wiki scanner entry/facade 与 characterization tests；只机械 seam。
- Inputs：Phase 4、WU-104 golden。
- RED/Focused：SEAM-01~05。
- Mutation：在搬移提交顺手改变排序/错误码；默认启 v2 stub。
- Audit：before/after trace、DB/file stat、latency、diff。
- Rollback：关闭 facade或 revert单一机械提交，v1源码/行为恢复。
- Accept：expected_good canonical等价，测试收集不变，p95劣化不超5%。

### WU-501

- Owner/Targets：company-wiki scanner orchestration、adapters base ports、persister ports及 tests。
- Inputs：WU-500、WU-205 target graph。
- RED/Focused：SPI-01~04。
- Mutation：scanner按 root_id 分支；adapter拿 CatalogStore writer。
- Audit：CodeGraph依赖、五步pipeline trace、side-effect ports。
- Rollback：v2 shadow flag关闭，facade继续v1；不删v2代码以便诊断。
- Accept：v2 pipeline可独立运行，orchestrator无来源语义分支。

### WU-502

- Owner/Targets：company-wiki tests/helpers adapter conformance kit；registry hook。
- Inputs：WU-501、fake adapter、fixture pack。
- RED/Focused：determinism、grouping、path、encoding、fault、read-only、no-network全套。
- Mutation：交换primary/sidecar、允许symlink越界、返回重复candidate、写fixture。
- Audit：每adapter capability/mandatory case receipt。
- Rollback：未通过adapter不注册；revert测试框架不影响v1。
- Accept：fake adapter和后续每个真实adapter同套测试，四个高风险mutation全被杀死。

### WU-503

- Owner/Targets：company-wiki admission.py/profile registry/tests。
- Inputs：WU-502、financial_evidence_v1契约。
- RED/Focused：ADM-01~10。
- Mutation：按Dropbox root放宽、把retired当active、弱身份当强。
- Audit：同candidate换root的结果diff、reason taxonomy。
- Rollback：v2 admission未active；关闭profile，v1不变。
- Accept：业务安全门来源无关，只由candidate事实和RootPolicy授权决定。

## Phase 6 卡片

### WU-601

- Owner/Targets：company-wiki adapters/company_raw、scanner v1 extraction boundary、adapter tests。
- Inputs：Phase 5、company_raw v1 golden/fixtures。
- RED/Focused：company_raw conformance + A/HK/US/期间/多location parity。
- Mutation：目录名覆盖sidecar security冲突；把write权限写进adapter。
- Audit：逐document v1/v2 candidate diff和CodeGraph。
- Rollback：company_raw cohort回v1，v2 assertion保持shadow。
- Accept：合法样本等价，冲突更严格fail closed，无writer依赖。

### WU-602

- Owner/Targets：company-wiki adapters/dayu、dayu metadata mapping/tests。
- Inputs：WU-601、dayu golden/meta fixtures。
- RED/Focused：dayu conformance、provider/document/URL/period强绑定。
- Mutation：unknown root落入dayu；按company_name补URL。
- Audit：group selection、identity evidence、rejection reason parity。
- Rollback：dayu cohort回v1；不修改dayu文件。
- Accept：dayu能力来自显式adapter，最终else和横向URL补洞消失。

### WU-603

- Owner/Targets：company-wiki scanner shadow comparator/receipts。
- Inputs：WU-601/602、真实根只读sample、fixture全量。
- RED/Focused：任何未登记diff、宽松比例、漏reason均失败。
- Mutation：隐藏一个v2额外candidate或少一个candidate。
- Audit：逐document/candidate/status/location/reason diff及known-bad owner。
- Rollback：关闭v2_scan_shadow；无production persistence。
- Accept：expected_good零未解释diff，安全收紧均有RED/reviewer。

### WU-604

- Owner/Targets：company-wiki flag/cohort、v2 persister、root rollout tests。
- Inputs：WU-603 accepted、backup/visibility机制。
- RED/Focused：company_raw/dayu各自三次运行、fault/concurrency/rollback。
- Mutation：同时切两root；让candidate直接active可见。
- Audit：per-root对账、assertion hash、latency、integrity和incident。
- Rollback：单root ingest flag回v1；v2 rows保持shadow，不反向迁移。
- Accept：两个root按顺序分别accepted，上一root未soak不得启动下一root。

## Phase 7 卡片

### WU-701

- Owner/Targets：company-wiki adapters/sidecar_filing schema/parser/tests。
- Inputs：Phase 6、synthetic sidecar fixtures、Normalized v2。
- RED/Focused：完整/缺字段/损坏/unknown version/path traversal/standalone sidecar cases。
- Mutation：用文件名补强period或identity；允许绝对artifact path。
- Audit：字段evidence映射、indexed_only remediation reasons、no-write spy。
- Rollback：adapter不注册或route不开启；现有directory v1不变。
- Accept：完整sidecar可入admission，缺证据保持可索引但绝不可复用。

### WU-702

- Owner/Targets：company-wiki RootPolicy routes、focus cleanup/admission special-case removal tests。
- Inputs：WU-701、Dropbox/future_root fixture routes。
- RED/Focused：A-01/04/05/08/10、DBX-09/10。
- Mutation：硬编码dropbox_stock/重点关注；重叠route双扫描。
- Audit：route match trace、policy hash、source literal/CodeGraph inventory。
- Rollback：route cohort关闭回v1；真实Dropbox配置不在本卡改变。
- Accept：同adapter用于不同目录名只改配置；普通内容可index但不可filing。

### WU-703

- Owner/Targets：company-wiki entity resolver/assertion service/tests。
- Inputs：WU-702、security registry、新公司/重名fixtures。
- RED/Focused：DBX-ENT-01~05、N-04/05/10。
- Mutation：恢复company_raw目录词典主导；模糊display_name自动选首项。
- Audit：每个identity assertion strength/evidence/conflict trace。
- Rollback：新实体保持candidate/unbound；关闭v2 route，不删除assertions。
- Accept：外部root可贡献新强实体，重名/冲突fail closed。

### WU-704

- Owner/Targets：company-wiki fixture integration/E2E support，调用resolver/bundle但不用真实根。
- Inputs：WU-701~703、DBX fixture pack。
- RED/Focused：DBX-01~14。
- Mutation：把broker放行为annual；忽略sidecar hash；重算有效summary。
- Audit：handle/bundle/path/hash和六类side-effect spy。
- Rollback：sidecar route flag关闭；temp catalog删除。
- Accept：14场景先RED后GREEN，future_root产品代码diff=0，真实根无写。

## Phase 8 卡片

### WU-801

- Owner/Targets：company-wiki resolver.py/query/store indexes/tests。
- Inputs：Phase 7、v2 assertions/visibility schema。
- RED/Focused：N/R query cases；禁止acquisition/dayu_meta读取的architecture test。
- Mutation：SQL恢复json_extract旧容器；按display name直接查询。
- Audit：SQL/params、EXPLAIN、rejected reasons、source literal scan。
- Rollback：v2_resolve_active=false，v1 reader保持。
- Accept：resolver仅查询normalized assertions/locations/policy，所有过滤fail closed。

### WU-802

- Owner/Targets：company-wiki resolver ranking/location selector/tests。
- Inputs：WU-801、排序ADR、多location fixtures。
- RED/Focused：R-02/05、N-09/14、ambiguous/tie cases。
- Mutation：排序加入root类型名；忽略missing/hash位置。
- Audit：完整ranking key、selected/rejected location trace。
- Rollback：cohort回v1；不改catalog。
- Accept：来源无关且稳定排序，同document只返回一个handle并保留locations。

### WU-803

- Owner/Targets：company-wiki resolver/source_bundle/artifact_handle/tests。
- Inputs：WU-802、WU-204 contract。
- RED/Focused：B-01~12中snapshot/hash/path/binding contract。
- Mutation：filing与artifact分两snapshot查询；忽略policy hash。
- Audit：单read transaction ID、bundle canonical hash、zero side effects。
- Rollback：v2_bundle_active=false，仅返回v1 handle。
- Accept：filing/artifacts同snapshot，query只读且不触发producer。

### WU-804

- Owner/Targets：company-wiki v1/v2 resolver shadow comparator。
- Inputs：WU-803、v1 golden、fixture/真实只读sample。
- RED/Focused：未分类 selected/rejected/status/reason diff 必须失败。
- Mutation：丢弃一个v2拒绝原因；宽松只比成功率。
- Audit：逐request diff、known-bad link、latency。
- Rollback：关闭v2_resolve_shadow；v1响应唯一。
- Accept：company/dayu expected_good零diff，Dropbox/future新增能力均有场景owner。

### WU-805

- Owner/Targets：company-wiki store indexes/performance fixtures/query-plan tests。
- Inputs：WU-804、大合成catalog。
- RED/Focused：exact/latest SLO、内存、关键表全扫检测。
- Mutation：删除一个关键索引或Python全量物化。
- Audit：p50/p95/p99、RSS、EXPLAIN、DB lock。
- Rollback：revert index/query commit；reader flag回v1。
- Accept：绝对阈值和相对基线均满足，删索引mutation被杀死。

### WU-806

- Owner/Targets：company-wiki resolver cohort/flag/breaker tests。
- Inputs：WU-804/805、六级切换顺序。
- RED/Focused：RES-CUT-01~08。
- Mutation：同请求silent fallback；同时切多个root。
- Audit：每cohort v1/v2 diff、handle hash、incident、下一请求flag。
- Rollback：cohort flag回v1，不改assertions；在下一请求生效。
- Accept：六步逐项accepted，任何未解释diff阻止扩容。

## Phase 9 卡片

### WU-901

- Owner/Targets：company-wiki source_catalog migration module/CLI/journal/tests。
- Inputs：Phase 8、schema hash、backup规范、temp catalog。
- RED/Focused：MIG-01~08。
- Mutation：忽略plan hash续跑；batch中途提交半记录。
- Audit：dry-run/apply/verify/resume journal、batch hashes、integrity。
- Rollback：默认dry-run；apply失败回backup或forward resume，绝不触碰外部文件。
- Accept：故障注入全通过，重跑幂等，不同代码/plan拒绝续跑。

### WU-902

- Owner/Targets：company-wiki migration backfill v1 company/dayu→v2 assertions。
- Inputs：WU-901、legacy snapshot copy、strong-key规则。
- RED/Focused：M-01、URL/identity/period unresolved cases。
- Mutation：猜测缺URL或把conflict算success。
- Audit：root/status/kind/year对账和逐document parity。
- Rollback：reader保持v1；删除复制库，生产apply尚未发生。
- Accept：计数闭合、无猜测、active可复用集零未解释差异。

### WU-903

- Owner/Targets：company-wiki Dropbox migration dry-run/remediation reporting。
- Inputs：WU-902、真实Dropbox只读enumeration、retire audit。
- RED/Focused：M-02/03、缺identity/provenance/hash/ambiguity分桶。
- Mutation：自动写sidecar或自动恢复retired。
- Audit：privacy-safe分桶、remediation reason、外部write spy。
- Rollback：纯dry-run/candidate shadow关闭；不改真实Dropbox或状态。
- Accept：只有强证据候选可生成v2 shadow，retired保持终态。

### WU-904

- Owner/Targets：company-wiki restore service/CLI/audit event/tests。
- Inputs：WU-903、明确document/location/assertion和reviewer授权。
- RED/Focused：REST-01~06、M-06/07。
- Mutation：允许company-wide restore或hash变化。
- Audit：immutable restore event、旧retire原因、actor/time/policy hash。
- Rollback：追加新的状态事件恢复retired；不删除历史事件。
- Accept：逐文档、强证据、双审、可审计，任何模糊恢复拒绝。

### WU-905

- Owner/Targets：company-wiki migration/control/resolver release procedure。
- Inputs：WU-901~904、backup、shadow parity。
- RED/Focused：切换前任一对账/backup/resolver shadow失败均阻止。
- Mutation：跳过backup或直接active v2 reader。
- Audit：七步切换receipt、flag/policy/schema hash。
- Rollback：reader flag回v1，legacy数据保留，v2数据不删。
- Accept：复制库切换/回退均可重复，exact/latest/bundle/worker通过。

### WU-906

- Owner/Targets：company-wiki migration recovery harness；只对两份snapshot copy。
- Inputs：WU-905、独立backup copies。
- RED/Focused：路径A~E crash/resume/mismatch/restore/stale journal。
- Mutation：恢复后少一行或接受旧journal。
- Audit：RTO、hash/count/integrity、reviewer独立命令。
- Rollback：销毁测试copies；禁止对生产执行破坏演练。
- Accept：五路径全部通过，数据丢失/错误restore=0。

## Phase 10 卡片

### WU-1000

- Owner/Targets：三仓ADR；冻结company CLI→filing CLI/client→revenue source-preparation，forecast calculator保持纯。
- Inputs：Phase 9、当前caller graph、PROCESS-RED-01。
- RED/Focused：从实际revenue入口启动子进程，当前缺编排应准确失败。
- Mutation：直接import helper冒充E2E；让calculator访问catalog。
- Audit：目标调用图、CLI contract、退出码/side-effect边界。
- Rollback：本卡仅ADR/RED，不改runtime。
- Accept：唯一入口无开放选择；若不可行必须回Phase 2修plan。

### WU-1001

- Owner/Targets：company-wiki resolver/source_bundle/cli及contract tests。
- Inputs：WU-1000、WU-803 bundle。
- RED/Focused：同snapshot bundle、JSON stdout、退出码、zero side effects。
- Mutation：日志混stdout；artifact另开snapshot。
- Audit：CLI canonical JSON/hash、stderr/exit、transaction ID。
- Rollback：v2 bundle flag关闭，v1 CLI envelope继续。
- Accept：company CLI原子返回handle+bundle且只读。

### WU-1002

- Owner/Targets：filing-fetch scripts/fetch_filing.py、filing_contracts.py、bundle compat tests。
- Inputs：WU-1001 current/N-1 fixtures、policy snapshot。
- RED/Focused：B-06/08/09/10、unknown version/path/hash/status。
- Mutation：丢字段、重算hash、bundle放松handle。
- Audit：byte/canonical round-trip、拒绝reason、调用预算。
- Rollback：filing client默认v1 envelope；关闭current reader。
- Accept：保真转发并二次验证，下载结果必须capture后再resolve。

### WU-1003

- Owner/Targets：revenue scripts/filing_fetch_client.py、company_wiki_source.py、source-preparation orchestrator/contracts/tests。
- Inputs：WU-1002、artifact DAG、recompute producers ports。
- RED/Focused：PROCESS-E2E-01~03、B-01~12 selection。
- Mutation：有效summary仍调LLM；失效summary重跑parser；无记录直接读PDF。
- Audit：RevenueSourceRecord、selected/recompute roles、producer spy。
- Rollback：source-preparation current flag关闭，旧显式入口保留；calculator不变。
- Accept：按角色最小复用/重算，所有source记录绑定handle/bundle/as-of。

### WU-1004

- Owner/Targets：三个SKILL.md、docs/examples/CLI help和executable docs tests。
- Inputs：WU-1003跨进程GREEN。
- RED/Focused：旧手工拼接、过度生产声明、示例不执行必须失败。
- Mutation：文档写“所有indexed均可复用”或跳过source-preparation。
- Audit：claim verifier、示例命令/输出、deprecated清单。
- Rollback：恢复上一版文档；runtime不变。不得用文档回滚改变协议。
- Accept：文档只描述已由E2E证明的入口和限制。

### WU-1005

- Owner/Targets：三仓protocol adapters/flags/compat tests，按company→filing→revenue→skill顺序。
- Inputs：WU-1001~1004、commit matrix。
- RED/Focused：version negotiation、malformed、timeout、partial、tamper、rollback。
- Mutation：同时切两个consumer；compat adapter重解释provenance。
- Audit：每consumer v1/v2 diff、protocol/hash、flag/incident。
- Rollback：单consumer回旧协议；producer继续双读/双格式兼容，不回数据。
- Accept：六步逐项accepted，compat层只映射字段且有删除owner。

## Phase 11 卡片

### WU-1101

- Owner/Targets：company-wiki gap_plan/resolver、filing latest代码drift report。
- Inputs：Phase 10、WU-203、现有latest/gap tests。
- RED/Focused：missing/incorrect/unwired逐项测试owner。
- Mutation：重写一套重复planner或遗漏现有正确规则。
- Audit：contract diff、复用模块清单、CodeGraph caller。
- Rollback：仅报告/测试；不改runtime。
- Accept：所有差异分类，无重复owner，无未经测试重写。

### WU-1102

- Owner/Targets：company-wiki resolver/gap、filing exact coordinator/tests。
- Inputs：WU-1101、allowed roots fixtures。
- RED/Focused：EXACT-01~08。
- Mutation：exact命中仍discovery；无授权自动下载。
- Audit：每root handle和六类side-effect=0。
- Rollback：exact v2 flag回旧实现；无文件/DB变更。
- Accept：命中零副作用，未命中返回明确gap/reason。

### WU-1103

- Owner/Targets：company-wiki gap planner、filing discovery coordinator/tests。
- Inputs：WU-1102、多root coverage/remote metadata fixtures。
- RED/Focused：LATEST-01~08。
- Mutation：忽略外部root coverage；同revision重复下载。
- Audit：covered/missing/stale/candidate deterministic plan。
- Rollback：latest discovery flag关闭；exact复用继续。
- Accept：只发现不下载，所有root覆盖合并且as-of正确。

### WU-1104

- Owner/Targets：filing-fetch authorization/download coordinator；company canonical capture/second resolve tests。
- Inputs：WU-1103、immutable GapPlan、显式授权fixture。
- RED/Focused：DL-01~08。
- Mutation：省略second resolve；两个并发各写一次。
- Audit：authorization hash、provider/temp/capture trace、write/download count。
- Rollback：关闭download_authorized flag；清理受控temp，不删成功canonical文件，状态由审计事件处理。
- Accept：无授权零下载；授权后每缺口最多一次原子写并返回resolver handle。

### WU-1105

- Owner/Targets：三仓source-preparation latest+artifact E2E。
- Inputs：WU-1104、旧期Dropbox artifact+新期remote fixture。
- RED/Focused：旧期复用/新期下载/第二次全复用组合。
- Mutation：重算旧期artifact；把新期写外部root。
- Audit：两期coverage、location、download/write/producer spy两次运行。
- Rollback：关闭latest/download，保留已有复用；temp fixture删除。
- Accept：首次只补新期，第二次零下载，旧期工件全复用。

## Phase 12 卡片

### WU-1201

- Owner/Targets：revenue e2e/run_source_preparation_e2e.py及tests/e2e support；调用真实三仓子进程。
- Inputs：Phase 11、temp roots/catalog、spy executables、commit matrix。
- RED/Focused：真实subprocess argv/stdout/stderr/exit/timeout；禁止direct helper。
- Mutation：把子进程替换为import；spy漏记一次调用；使用本机浮动checkout。
- Audit：每case command、commit/config/policy/catalog/fixture hash和JSONL spy。
- Rollback：kill子进程、删除temp环境；真实根/生产catalog从不接入。
- Accept：Windows路径/锁/超时可靠，跨仓失败正确传播，无僵尸进程。

### WU-1202

- Owner/Targets：revenue scenario registry/runner/receipt validator，三仓测试node映射。
- Inputs：WU-1201、A/N/R/L/B/M/F/RF全部ID。
- RED/Focused：删case、重复ID、层级伪标、未运行mandatory必须失败。
- Mutation：把B-01改component却仍标E2E；跳过RF-09。
- Audit：84场景owner/layer/node/RED/GREEN/mutation矩阵。
- Rollback：不切生产；恢复scenario registry。
- Accept：72业务+12重构场景全部有状态，mandatory cross-repo集合三次稳定。

## Phase 13 卡片

### WU-1301

- Owner/Targets：company-wiki read-only probe tooling/tests；三个真实根仅读。
- Inputs：Phase 12、隐私redaction/salted path规则、用户授权边界。
- RED/Focused：probe漏文件、泄漏绝对路径、写入/mtime变化必须失败。
- Mutation：probe创建cache文件或记录原始文件名。
- Audit：快速/完整inventory、hash/mtime before-after、write spy。
- Rollback：probe无写入；停止进程并删除独立temp日志。
- Accept：三个根前后一致，receipt不泄漏敏感路径/内容。

### WU-1302

- Owner/Targets：company-wiki config doctor/enumerate/normalize/resolver shadow。
- Inputs：WU-1301、production catalog/root只读、v2 shadow flags。
- RED/Focused：只读discovery对账、每root/route reason分布、零副作用。
- Mutation：shadow写candidate或触发parser。
- Audit：候选/admitted/indexed/conflict/error分桶和legacy diff。
- Rollback：关闭shadow；无production data change。
- Accept：whole-root generic与filing route边界清楚，真实根probe不变。

### WU-1303

- Owner/Targets：revenue source-preparation真实canary配置；company/filing只读链。
- Inputs：WU-1302、人工确认的Dropbox-only合格官方filing；若无则blocker。
- RED/Focused：真实path/root/hash/status/provenance和全部副作用0。
- Mutation：偷偷使用company_raw副本或修改sidecar制造样本。
- Audit：候选资格review、两次handle/bundle、root probe。
- Rollback：canary只读；关闭cohort即可。
- Accept：真实Dropbox-only两次稳定复用；无样本则明确BLOCKED，不能替代。

### WU-1304

- Owner/Targets：revenue真实processed-artifact canary；只在catalog snapshot copy模拟失效。
- Inputs：WU-1303或独立合格filing、MD/summary artifact。
- RED/Focused：有效工件parser/LLM=0；版本/binding改变只出最小recompute plan。
- Mutation：有效summary仍调用LLM；真实artifact被改写。
- Audit：artifact/hash/binding/producer spy和copy恢复。
- Rollback：销毁snapshot copy；真实文件/catalog只读。
- Accept：复用与最小失效均由真实链证明，生产资产不变。

### WU-1305

- Owner/Targets：company-wiki metrics/reason enums，filing/revenue telemetry mapping/tests。
- Inputs：WU-1302、reason taxonomy和privacy规则。
- RED/Focused：unknown reason、自由文本断言、路径/token泄漏失败。
- Mutation：日志写绝对路径或公司文档内容；漏legacy_hits。
- Audit：指标schema、redaction样例、root/route/adapter/role聚合。
- Rollback：telemetry exporter关闭不影响核心行为；本地buffer安全清理。
- Accept：每个拒绝/复用/下载/重算有版本化reason且可观察。

### WU-1306

- Owner/Targets：company-wiki/revenue性能与soak harness；合成数据。
- Inputs：WU-1305、WU-805基线、10并发/24h配置。
- RED/Focused：SLO、内存、DB lock、重复下载、僵尸进程。
- Mutation：无变更扫描全量rehash；删索引；泄漏子进程。
- Audit：p50/p95/p99/RSS/locks/CPU/hash count/soak趋势。
- Rollback：停止合成soak、删除temp DB；不连生产writer。
- Accept：绝对阈值和≤10%相对劣化均满足，三次稳定。

## Phase 14 卡片

### WU-1401

- Owner/Targets：三仓workflow、test manifests、cross-repo matrix tooling。
- Inputs：Phase 13、当前CI baseline、XR aliases。
- RED/Focused：删test、skip/xfail、浮动sibling checkout、unsupported matrix失败。
- Mutation：filing继续排除新增mandatory而不报告；company不跑integration。
- Audit：PR/nightly/real-canary job边界、collection/coverage、commit matrix。
- Rollback：workflow revert；runtime flags不变，不能以回滚CI跳过质量门。
- Accept：每仓和跨仓门实际执行，未授权real job明确not_run并阻止相应claim。

### WU-1402

- Owner/Targets：三仓mutation patrol/canary tests。
- Inputs：WU-1401、12定向mutation及RF映射。
- RED/Focused：逐mutation指定唯一杀手测试。
- Mutation：就是计划列出的12个错误实现，逐个临时应用。
- Audit：mutation ID、diff、失败node、恢复hash和GREEN。
- Rollback：每个mutation立即revert并验证clean diff；残留即stop。
- Accept：12/12被杀死，自动分数只作辅助。

### WU-1403

- Owner/Targets：company-wiki wave/control config，三仓release procedure。
- Inputs：WU-1402、R波次、root/consumer cohort。
- RED/Focused：跳步、同窗口切3/5/7/9、缺soak/go-no-go失败。
- Mutation：直接启Dropbox resolver+download+revenue。
- Audit：每步smoke/metrics/error budget/reviewer decision。
- Rollback：只回当前root/consumer/feature flag，保留v2数据。
- Accept：九步逐项accepted，任何一步可独立暂停/回退。

### WU-1404

- Owner/Targets：三仓rollback scripts/runbooks和复制库演练。
- Inputs：WU-1403、backup/journal/旧CLI/flags。
- RED/Focused：ROLLBACK-01~05。
- Mutation：回滚删除v2数据或静默自动下载。
- Audit：RTO、未完成请求、数据diff、恢复后smoke。
- Rollback：本卡即验证路径；失败则不发布并恢复到前一accepted波次。
- Accept：schema/resolver/Dropbox/bundle/download五类演练成功。

### WU-1405

- Owner/Targets：revenue release manifest/validator，引用三仓。
- Inputs：WU-1404、commits/schema/adapter/config/policy/migration/test receipts。
- RED/Focused：任一commit/hash/limitation/rollback缺失失败。
- Mutation：改一个仓HEAD或隐藏未完成canary。
- Audit：签名manifest和兼容矩阵。
- Rollback：manifest失效不改变runtime；重新生成需重跑受影响门。
- Accept：manifest唯一绑定发布状态，任一漂移自动失效。

### WU-1406

- Owner/Targets：company-wiki wave controller/dashboard，revenue audit validator。
- Inputs：WU-1405、R0~R11/CP0~CP8状态。
- RED/Focused：WAVE-01~08。
- Mutation：人工flag无incident；override hash/integrity门。
- Audit：机器状态、stop/incident/override expiry、metrics completeness。
- Rollback：controller仅切安全flag；自身失败默认停止推进。
- Accept：八类错误实际阻断，安全门不可override。

## Phase 15 卡片

### WU-1500

- Owner/Targets：company-wiki/filing/revenue legacy flags/metrics/tests；不删源码。
- Inputs：Phase 14 stable、legacy/bridge hit metrics。
- RED/Focused：RF-11、每周期v1显式回滚启动。
- Mutation：禁用后仍有隐藏legacy caller；计数归零造假。
- Audit：两个完整周期hits/error/SLO/canary和rollback receipt。
- Rollback：重新enable v1 flag；不改数据。
- Accept：连续两周期0 hits且v1仍可显式启动，出现hit则周期归零。

### WU-1501

- Owner/Targets：company-wiki legacy scanner/resolver，三仓重复protocol/helper/config；分四提交。
- Inputs：WU-1500、CodeGraph zero callers、RF-12。
- RED/Focused：forbidden source literals/import/callers和全仓/XR gate。
- Mutation：保留一个dead caller或删除仍需N-1模块。
- Audit：每提交CodeGraph/diff/test/size与revert proof。
- Rollback：每层独立revert，不回数据库。
- Accept：scanner、resolver、protocol、config/docs四层分别GREEN，无巨型混合删除。

### WU-1502

- Owner/Targets：company-wiki legacy bridge/schema reader retirement；历史raw metadata保留。
- Inputs：WU-1501、N-1窗口、backup恢复证明。
- RED/Focused：bridge hit、active filing缺v2 assertion、旧backup不可读均阻止。
- Mutation：purge历史raw或drop旧column。
- Audit：active coverage、compat matrix、backup read。
- Rollback：恢复reader adapter提交；不恢复purged数据，因为purge禁止。
- Accept：停止读写legacy但不破坏历史数据，破坏性清理另立授权计划。

### WU-1503

- Owner/Targets：三SKILL/docs/config comments/CLI help/executable docs。
- Inputs：WU-1502、最终release manifest。
- RED/Focused：config-only边界、indexed/reusable、read-only/download/latest/artifact/canary声明。
- Mutation：写“任意indexed目录无需adapter即可复用”。
- Audit：claim verifier、example execution、版本链接。
- Rollback：文档提交独立revert；不改变runtime。
- Accept：所有声明可追溯到当前测试/生产证据，无过度承诺。

### WU-1504

- Owner/Targets：独立 reviewer 的三仓只读审计、mutation与新fixture root。
- Inputs：WU-1503、全部receipts/HEAD/production stats。
- RED/Focused：随机重跑、至少6人工mutation、未知同构root/未知layout、CodeGraph/真实canary。
- Mutation：reviewer独立选择至少6个，不接受作者预选结果代替。
- Audit：P0~P3 findings、命令/输出、caller/dirty/root probe。
- Rollback：发现P0~P2则回最早失效WU/flag；审计本身不改生产。
- Accept：P0/P1/P2全关闭并有回归测试，P3有owner/理由。

### WU-1505

- Owner/Targets：revenue closure ledger/validator，引用三仓commits/receipts。
- Inputs：WU-1504、F-034~060和所有用户要求。
- RED/Focused：任一finding缺root cause/commit/RED/GREEN/mutation/E2E/canary失败。
- Mutation：删除F-038或把blocked canary写closed。
- Audit：最终ledger、release manifest、residual risks。
- Rollback：ledger失效则撤回完成声明，不回产品数据。
- Accept：27条逐项闭环；真实canary未完成时整体不得标production_dropbox_complete。

## Runbook 完整性门

- 74/74 WU 卡片存在。
- 每张卡七字段非空且 owner/target/依赖与 task_plan 一致。
- 不存在开放占位项。
- machine validator 可检测删卡、重复 ID、空字段、错误依赖、plan hash 漂移。
- 文件边界、reviewer、证据目录和命令alias均已冻结；实施时只能通过plan revision扩展。

## 基线 recapture 纪律（WU-101 P1 教训）

- 每 WU accepted 边界必须重新执行 `baseline_gate.py --capture --with-skip-counts`，
  锁定该边界的三仓 HEAD/collection/skip 计数；未 recapture 时下一个 WU 的 --check 必然红。
- --check 使用 `--with-skip-counts`（执行态 skipped/xfailed 统计）；每 WU 的
  --allowed-files 必须是该 WU receipt actual_changed_files 的同一文件。
- collection 计数变化（新增/删除测试、插件差异）视为 plan revision 事件：
  先更新计划/回执，再 recapture。
