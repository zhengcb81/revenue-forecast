# 多根 Filing Data Lake 解耦与端到端闭环 — 实施计划

> 计划日期：2026-08-09  
> 计划版本：2.0-full-refactor-safety  
> 当前状态：plan_complete_ready_for_review_v2  
> 本轮授权：仅调查与写计划；禁止修改产品代码、产品配置、测试、生产 catalog 和三处真实资产目录。  
> 逐工作单执行卡：同目录 implementation_runbook.md；任何 WU 无有效卡片不得启动。  
> 适用仓库：`company-wiki`、`filing-fetch`、`revenue-forecast`。  
> 依据：`audit_review/2026-08-08_adversarial_plan/findings.md` 的 F-034~F-060 及当前 HEAD/生产只读证据。

## 0. 目标、边界与完成定义 — 状态：completed

### 0.1 最终目标

- [ ] `company-wiki/companies` 继续作为唯一 canonical write store。
- [ ] `dayu-agent/workspace/portfolio`、`Dropbox/Stock` 及未来明确授权且成功 index 的外部根，可通过配置选择已注册 adapter/profile，成为只读、来源无关的复用根。
- [ ] resolver 只消费统一的 normalized filing metadata，不识别 `company_raw/dayu/dropbox` 来源名或来源专有 JSON 容器。
- [ ] 已有合格 filing 优先零下载复用；旧版本仍保留，同时 latest/gap 只补缺期或更新 revision。
- [ ] 已验证的 normalized/summary/sections/consumer_analysis 进入真实 company-wiki → filing-fetch → revenue-forecast 主链，避免重复解析或总结。
- [ ] 不合格、缺 provenance、retired、quarantined、identity 冲突或路径越界资产始终 fail closed。

### 0.2 非目标

- [ ] 不把“所有 indexed 文件”自动升级为 filing/evidence。
- [ ] 不允许外部根成为 writer 或被自动搬运/重命名。
- [ ] 不以复制 Dropbox metadata 到 `acquisition` 作为最终架构。
- [ ] 不删除 retire/restore、identity、hash、as-of、path fence 等安全门。
- [ ] 不在本计划阶段实施任何产品改动。

### 0.3 全局完成定义

- [ ] 所有阶段必须按依赖顺序完成，任何阶段不得以“代码存在”“单测绿色”“文档声明完成”代替端到端验收。
- [ ] 每个工作单元具有：基线、RED、最小实现、focused GREEN、仓库 GREEN、跨仓 GREEN、mutation proof、审计回执、独立 reviewer、回滚点。
- [ ] 三个真实根只读 hash/mtime/inventory 探针前后一致；网络、下载、parser、LLM、写入调用计数符合场景预算。
- [ ] 最终真实 Dropbox-only filing canary 返回 capture-ready handle，canonical path 位于 Dropbox，download=0、company_raw 写入=0。
- [ ] 最终真实 processed artifact canary 证明 parser/LLM=0；任一 binding/version/provenance 改变时只重算失效角色。
- [ ] 全部历史相关问题映射到 closure ledger，并由测试 ID、receipt 和当前 HEAD 证据闭环。

### 0.4 强制工作单状态机

每个 WU 只允许按下列状态单向前进：

planned → baseline_captured → red_proved → contract_frozen → implemented → focused_green → repo_green → cross_repo_green → mutation_proved → independently_reviewed → accepted

- 任一状态缺证据时保持原状态；禁止先勾选、后补证据。
- RED 必须在实现提交之前失败，且失败原因必须命中待修行为；导入失败、fixture 路径错误、环境缺依赖不算有效 RED。
- implemented 只表示代码存在，不表示功能完成。
- reviewer 不能只复述作者回执；必须重跑指定测试、查看 diff、执行至少一个反例 mutation，并给出 findings 或明确 no-findings。
- 失败后从第一个失效状态重新开始；不得跳过 repo/cross-repo 门。

### 0.5 每个工作单的机器可读回执

实施时在 audit_review/receipts/WU-xxx.json 生成并由 schema 校验器验证，至少包含：

- wu_id、plan_version、plan_hash、owner、reviewer、status、started_at、completed_at。
- 三仓 baseline_commit、current_commit、dirty_paths_before、dirty_paths_after。
- allowed_files、actual_changed_files、forbidden_path_check。
- red_test_ids、red_command、red_exit_code、red_failure_excerpt、red_commit。
- focused/repo/cross_repo 命令、exit_code、collected/passed/failed/skipped/xfail、duration。
- mutation_id、mutation_description、expected_failure_test、observed_failure、revert_proof。
- fixture_manifest_hash、config_hash、policy_hash、catalog_schema_version。
- network_calls、download_calls、parser_calls、llm_calls、external_write_calls、canonical_write_calls。
- real_root_probe_before/after、catalog_probe_before/after、backup_id、rollback_point。
- reviewer_findings、open_risks、admission_decision。

回执缺字段、命令不可复现、测试数减少、出现未解释 skip/xfail 或真实根探针变化，一律拒绝 accepted。

实施者不得只读取本文件中的单个 WU 段落。启动前必须同时读取 implementation_runbook.md 中同 ID 卡片；卡片与本计划 plan_version/plan_hash 不一致、必填字段为空或目标文件已漂移时，状态保持 planned 并先更新计划。

### 0.6 已知审查结论的实施覆盖台账

| Finding | 计划 owner | 关键测试/证据 | 关闭条件 |
|---|---|---|---|
| F-034 config-only 已被证伪 | Phase 3/7 | A-01/02、DBX-10 | 同构新 root 只改配置；当前 Dropbox 经 adapter 后可用 |
| F-035 HEAD 已漂移 | WU-101/103 | BASE-01/04 | 当前三仓 commit 与 plan/receipt 绑定 |
| F-036 无统一 filing metadata | Phase 2/4/8 | META、TX、N 系列 | resolver normalized-only |
| F-037 directory 非 adapter | Phase 3/5/7 | SPI、A 系列 | adapter registry + conformance |
| F-038 sidecar 语义丢失 | WU-701~704 | N-01、DBX-01 | sidecar→v2 assertion→handle |
| F-039 path fence 不是适配层 | WU-301/503/801 | CFG、ADM | policy/admission/adapter 职责分离 |
| F-040 配置已开仍失败 | WU-103/1302 | shadow reason 统计 | 文档删除“待打开白名单”误述 |
| F-041 revenue 根无关但受上游限制 | Phase 10 | PROCESS-E2E | source-preparation 实际消费 bundle |
| F-042 已索引但无可复用财报 | Phase 9/13 | M-02/03、真实 canary | 合格样本显式恢复并通过；否则保持 blocker |
| F-043 关键词假阳性 | WU-503/701/704 | N-07、DBX-12 | official/provenance 门拒绝 |
| F-044 必要 ownership 与坏耦合混杂 | WU-201/1501 | ARCH、F-09 | canonical writer 保留，读取特例归零 |
| F-045 focus 被 admission 排除且不透明 | WU-702/1305 | A-05、reason metrics | route 配置化且逐 reason 可观察 |
| F-046 admission 专例硬编码 | WU-503/702 | ADM、A-01 | profile 可复用于 future_root |
| F-047 测试说明与断言矛盾 | WU-103/1503 | executable docs | 危险注释清除且 claim gate 通过 |
| F-048 config invariant 不证明功能 | Phase 12 | R-03/R-04 | 配置 + 跨进程行为同时验证 |
| F-049 绿测固化 MISSING | WU-704/1202 | DBX-01 先 RED 后 GREEN | 正向 reuse 断言及负例并存 |
| F-050 artifacts 有数据但源不可达 | Phase 8/10 | B-01/07/09 | handle 与 bundle 同 snapshot 可达 |
| F-051 SourceBundle 能力孤岛 | WU-1000~1004 | PROCESS-E2E-01~03 | CodeGraph 有产品 caller，跨进程 spy 通过 |
| F-052 company-name URL 错绑 | WU-403 | N-06、mutation 3 | 只允许文档级强键 |
| F-053 entity 依赖 company_raw | WU-703 | N-04/05/10 | 新公司与歧义场景正确 |
| F-054 错误 enrichment 被测试保护 | WU-403/1501 | 多期间不同 bytes RED | 旧错误测试被替换为 provenance 断言 |
| F-055 retired 不应自动复活 | WU-903/904 | M-02/03/06/07 | restore 逐文档、有回执、可审计 |
| F-056 dayu 成功不能外推 | WU-502/602 | A-01/02/08 | 能力来自注册 adapter，不来自 else |
| F-057 gap 根无关但输入不全 | Phase 8/11 | L-01~10 | 全部允许根的有效 handles 进入 coverage |
| F-058 物理 catalog 基础良好 | WU-201/400 | parity/迁移 | 不重写 source/document/location/artifact 所有权 |
| F-059 耦合集中 scanner | WU-501/1501 | SPI-02/F-09/CodeGraph | scanner 仅 orchestration |
| F-060 语义 data lake 未成立 | 项目总门 | A/N/R/L/B/M/F + canary | adapter→normalized→resolver→bundle 全链闭环 |

### 0.7 全面重构裁决与边界

本计划明确允许并推荐对 semantic ingest → resolver → SourceBundle → revenue source-preparation 做完整架构替换。不得因担心 diff 大而选择以下伪修复：

- 给 Dropbox 再加一个 scanner if 分支。
- 把 directory sidecar 塞进 acquisition 冒充 company_raw。
- 让 resolver 再认识第三个 metadata_json 容器。
- 在三仓分别增加新的 root allowlist。
- 保留 helper-only 的 SourceBundle，再让技能文档手工拼接。

必须重构的职责：

1. scanner 中 layout、sidecar、entity、classification、admission、persistence 混合的单体流程。
2. acquisition/dayu_meta 等来源特定 filing 语义容器。
3. root kind 同时承担物理布局、业务语义和授权的配置模型。
4. resolver 读取来源特定 JSON 与公司名补 URL 的横向耦合。
5. company-wiki、filing-fetch、revenue 之间靠人工步骤拼接的生产链。

明确保留并演进而非重写：

1. roots/sources/documents/locations/artifacts/evidence 的物理 catalog 所有权。
2. 内容 hash、多 location、canonical writer、external read-only、status、path fence。
3. 已验证的 latest/gap、ArtifactHandle/SourceBundle 校验逻辑；先 drift audit，再接线或修正。
4. source_metadata_assertions 的不可变 assertion/supersession 思路；只做 v2 additive 演进。

全面重构完成的结构标准：新增第五个同构 root 只改 RootPolicy；新增一种新 layout 只实现一个 adapter 并通过 conformance；resolver、admission、persister、filing-fetch、revenue 不改代码。

### 0.8 Strangler 渐进替换拓扑

旧链命名为 v1，目标链命名为 v2。v2 不能直接覆盖 v1，必须依次经过：

| 波次 | v1 状态 | v2 状态 | 允许写入 | 流量 | 退出证据 | 回滚 |
|---|---|---|---|---|---|---|
| R0 基线冻结 | active | 不存在 | v1 原行为 | 100% v1 | characterization/golden/调用预算 | 回到基线 commit |
| R1 建 seam | active | facade 后未启用 | v1 only | 100% v1 | 输出字节级等价、性能不劣化 | 关闭 facade |
| R2 pure shadow | active | enumerate/normalize 内存运行 | v1 only | v1 响应；v2 旁路 | candidate/diff receipt | 关闭 v2 shadow |
| R3 fixture persistence | active | 写临时 catalog | temp only | v1 响应 | transaction/migration/conformance | 删除 temp DB |
| R4 production dry shadow | active | 真实根只读、零持久化 | 无新增生产写 | v1 响应 | per-root diff/reason/性能 | 关闭 shadow |
| R5 assertion candidate | active | v2 assertion 追加但 resolver 不读 | catalog candidate only | v1 响应 | 对账、backup、幂等 | 禁止 v2 writer；保留历史 |
| R6 per-root resolve | active fallback flag | v2 依次启 company_raw→dayu→sidecar | catalog read-only | 每次只切一个 root cohort | 0 未解释 diff + canary | operator/自动 gate 切回 v1；不静默逐请求 fallback |
| R7 v2 resolver default | standby | active | 既定 catalog 写 | 100% v2 resolve | soak/SLO/legacy hit 下降 | 全局 reader flag 回 v1 |
| R8 per-consumer | standby | company CLI→filing→revenue 逐个切 | canonical writer 仅授权下载 | 每次一个 consumer | cross-process E2E + spy | consumer version/flag 回旧协议 |
| R9 migration/recovery | standby | v2 backfill/restore | 获批 catalog transaction | 受控批次 | reconciliation + restore audit | DB snapshot + reader 回退 |
| R10 retire v1 | disabled | active | v2 only | 100% v2 | 两验证周期 legacy_hits=0、rollback 演练完成 | 仅 release rollback；源码暂不删 |
| R11 delete legacy | removed | active | v2 only | 100% v2 | 独立复审、备份可恢复、compat 期满足 | revert 独立清理提交 |

顺序不可交换。特别禁止：在 R4 前写生产 assertion，在 R6 前让 v2 返回用户结果，在 R8 前更新技能声称生产接通，在 R10 前删除旧代码。

### 0.9 每个重构切片的统一安全检查点

每个 slice 只能跨越一个 architectural seam，并必须有九个检查点：

1. CP0 Scope：冻结 input/output contract、文件 allowlist、基线 commit、回滚 commit。
2. CP1 Characterization：旧链正常/异常/边界行为形成 golden trace；错误行为标 known-bad，不能误锁为目标。
3. CP2 RED：目标行为或 architecture rule 在旧实现上有效失败。
4. CP3 Seam：先建立可切换边界，默认仍调用 v1；此提交必须行为等价。
5. CP4 Shadow：相同 immutable input 同跑 v1/v2，比较结构化输出、side effects 和 latency。
6. CP5 Fault：在 DB、文件、subprocess、timeout、cancel、并发边界注入故障，验证原子性。
7. CP6 Canary：只给一个 fixture/root/request/consumer cohort，观察 error budget。
8. CP7 Cutover：明确 flag/policy hash 后放量；禁止 silent fallback 隐藏 v2 错误。
9. CP8 Cleanup-ready：legacy hit、bridge hit、shadow diff 连续满足门槛后才允许另立清理提交。

CP0~CP8 每项均写入 WU receipt。任何一个缺失时切片不得 accepted。

### 0.10 Stop-the-line 与自动回退条件

以下任一发生立即停止当前波次，不进入下一 root/consumer：

- 任一未分类的 selected document、entity、kind、period、revision、status、location 或 artifact 差异。
- v2 比 v1 多放行一个不安全候选，或少返回一个经人工确认合法的候选。
- external_write_calls > 0，或未授权 network/download/canonical write > 0。
- catalog integrity_check、foreign_key_check、迁移对账不通过。
- 部分事务、重复 active assertion、bundle snapshot 错配或 hash 不一致。
- 真实根 hash/mtime/inventory 非预期变化。
- focused/repo/cross-repo 测试数下降，出现新增 skip/xfail，定向 mutation 存活。
- p95/p99、内存、DB lock 超过该波次冻结阈值。
- rollback 演练失败、feature flag 组合非法或旧 reader 已无法恢复。
- 用户既有脏文件出现在 diff。

自动回退仅切 cohort/root/consumer 的版本 flag，并发出结构化 incident receipt；不得自动反向迁移 DB、删除 v2 assertions、重写外部文件或逐请求静默 fallback。回退后必须完成 root-cause、RED 和 reviewer 复核才能再推进。

### 0.11 临时兼容层的债务预算

允许的临时层只有 ScannerFacade、legacy metadata reader bridge、v1/v2 protocol adapter、feature flags。每一个必须登记：

- 引入 WU、owner、调用者、指标名称、默认状态。
- 允许存在的最晚波次与删除 WU。
- legacy_hits/bridge_hits 的归零条件。
- 禁止新增功能的 freeze test。

禁止 temporary_v2、new_resolver2、dropbox_fix、compat_final 等无 owner 平行模块。R10 时兼容层数量必须为 0 或有明确 N-1 协议义务；R11 通过 CodeGraph 与 architecture gate 删除死链。

### 0.12 三仓提交与版本演进纪律

三仓不能原子提交，因此所有协议变化采用 expand → migrate → contract：

1. producer 先增加 additive schema/字段，旧输出不变。
2. consumers 先升级为同时理解 N-1/current，默认仍走旧协议。
3. producer 在 fixture/shadow/cohort 中开始发 current。
4. consumers 分别切 current 默认；旧协议仍可显式回退。
5. release manifest 证明所有受支持 consumer 已升级后，producer 才停止 N-1 默认。
6. Phase 15 最后删除 N-1 adapter/字段读取；历史数据不 destructive purge。

提交规则：

- 每个提交必须在单仓独立可安装、可测试、可回退；跨仓依赖由 commit matrix 和 release manifest 表达。
- 机械移动、additive schema、writer shadow、reader cutover、consumer cutover、legacy cleanup 分开提交。
- 需要跨仓协同的 WU 可有多个按序子提交，但每个子提交都有独立 receipt/rollback，WU 仅在全部 matrix 组合通过后 accepted。
- 不允许先提交 breaking producer 再要求其他仓“随后跟上”。
- catalog migration 代码提交、migration apply、reader cutover 是三个独立变更事件。
- 大重构不设置人为文件数上限；若超过原 allowed_files，先更新 impact/allowlist/reviewer，但不得用拆成无意义小文件来规避审查。

## Phase 1（基线冻结与计划防漂移）— 状态：pending

### 目标

在任何实现前建立可重复的三仓、三根、catalog、测试和调用图基线；保证后续弱模型不会把既有用户修改、过期文档结论或假 E2E 当作完成证据。

### WU-101：三仓不可变基线与脏工作区保护

依赖：无。改动范围：只允许新增 audit 工具、fixture manifest 与计划回执；不得清理用户文件。

1. 记录三仓绝对路径、HEAD、branch、git status --short、Python/runtime/依赖锁摘要、CodeGraph 状态与索引时间。
2. 明确保留 company-wiki 已存在的 llm_cost_log.csv 修改及 source_manifests/archive 未跟踪内容；任何工作单碰到这些路径立即停止。
3. 记录 source_catalog.yaml、source_catalog_worker.yaml、两侧 company_wiki.json 的字节 hash 和解析后 canonical hash。
4. 保存 pytest --collect-only 的 node ID 清单和数量；按 unit/contract/integration/E2E/real-canary 分类，不以总数掩盖类别减少。
5. 对所有计划输入先做路径存在性检查；缺失文档记录为缺失，不得用同名猜测路径。

RED/审计测试：

- BASE-01：任一仓 HEAD 与回执不一致时 gate 失败。
- BASE-02：actual_changed_files 包含基线脏文件时 gate 失败。
- BASE-03：删掉一个测试或把测试改成 skip/xfail 后 collection gate 失败。
- BASE-04：plan_hash 与当前 task_plan.md 不一致时禁止下一 WU。

退出标准：三仓基线回执被独立 reviewer 复核；本阶段没有产品行为变化。

### WU-102：生产形态、完全隔离的多根 fixture

依赖：WU-101。

建立临时测试树，不复制真实机密内容，最少包含：

- company_raw 根：官方年报、季度报告、sidecar、已处理 MD、摘要、sections。
- dayu 根：provider metadata、同公司多期间、相同文件多 location。
- sidecar 通用根：模拟 Dropbox 的中文/英文路径、重点与非重点子树、新公司、重名公司、缺字段、恶意路径。
- 第四个 future_root：与 sidecar 通用根采用完全相同 adapter/profile，但 root_id 与路径均不同，用于证明真正 config-only 接入。
- catalog fixture：active/retired/quarantined/missing、重复 hash、同期间不同 revision、旧版 artifact、binding 失效。

每个文件使用合成字节并由 manifest 声明 sha256、entity、kind、period、expected admission、expected canonical location；fixture builder 必须每次生成相同 hash。

RED/审计测试：

- FIX-01：fixture 泄漏任一真实绝对路径时失败。
- FIX-02：篡改一个文件字节但不更新 manifest 时失败。
- FIX-03：future_root 在代码中出现专有分支或专有名称时 architecture gate 失败。
- FIX-04：fixture 构造器产生网络、parser、LLM 或外部写入时失败。

退出标准：fixture 可在全新 temp 目录由单条命令重建；Windows 非 ASCII 路径通过；真实三根 hash/mtime 不变。

### WU-103：审查结论与计划防漂移清单

依赖：WU-101。

1. 把前序 F-034~F-060、D-001~D-013 与旧计划仍有效问题逐项映射到 owner phase、测试 ID、完成证据。
2. 标明 superseded 结论，尤其是 Dropbox runtime diff=0/config-only 已完成。
3. 建立 forbidden-claim gate：没有对应产品调用者和跨进程 E2E 时，不得在文档写“生产已接入”“完整复用”“只改配置即可”。
4. 冻结 Phase 1 的 plan_version；任何后续计划改动必须增加版本并让未完成回执重新核验依赖。

退出标准：closure ledger 无 orphan finding、无无测试 owner 的高风险项。

### WU-104：v1 行为刻画与 golden trace pack

依赖：WU-101/102。

在任何 seam/refactor 前为当前 v1 建立结构化行为刻画：

- scanner：每个 root 的 enumerated group、document/source/location/assertion 写入和 reason code。
- resolver：selected/rejected candidates、ranking key、handle、失败类型。
- filing-fetch：exact/latest/missing/authorized download 的命令、退出码和 side-effect budget。
- revenue：当前实际 CLI/helper 调用边界，明确哪些是产品行为、哪些仅为测试能力。

每条 trace 标记 expected_good、known_bad_to_fix 或 compatibility_only：

- expected_good 在 v2 必须等价。
- known_bad_to_fix 必须先有单独 RED，不能被 golden 误当成必须兼容。
- compatibility_only 只在声明的 N-1 窗口保留。

测试：

- CHR-01 同一输入连续三次 trace canonical hash 一致。
- CHR-02 删除/新增候选、改变调用预算或错误码会使 golden diff gate 失败。
- CHR-03 known_bad 没有对应 RED owner 时禁止 Phase 2。
- CHR-04 trace 捕获不得读取未授权真实文件、不得触发网络/下载/LLM。

### Phase 1 放行门

- WU-101~104 均 accepted。
- baseline 与 fixture 的复核者不是同一实现者。
- 未修改生产配置、catalog 或三处真实资产。

## Phase 2（目标契约与架构决策）— 状态：pending

### WU-201：冻结职责边界 ADR

依赖：Phase 1。

ADR 必须明确：

- RootPolicy：这个 root 是否允许扫描/复用、用哪个已注册 adapter/profile、路径和路由范围；不解释财报语义。
- SourceAdapter：只枚举文件组并把来源布局转为 NormalizedCandidate；不写 DB、不决定下载、不绕过 admission。
- NormalizedFilingMetadata：来源无关的财报事实和逐字段 evidence。
- AdmissionPolicy：统一执行 identity、provenance、kind、period、status、hash、path、as-of 安全门。
- Catalog persister：事务、幂等、location/artifact/assertion 持久化；不含 root 特例。
- Resolver：只查询 active normalized facts 与允许 root；不解析 sidecar，不按 source 名分支。
- SourceBundle：把 filing、artifact 与 binding 一次性输出给消费方。
- filing-fetch：reuse-first、latest/gap 与授权下载；不重新猜 catalog 语义。
- revenue source-preparation：唯一 I/O 编排入口；revenue_forecast.py 继续保持纯计算。

ADR 同时列出禁止依赖：resolver→adapter、adapter→store、revenue calculator→network、config→任意动态 Python import、外部 root→canonical writer。

RED：ARCH-01~05 用 import graph/AST gate 制造上述五种逆向依赖并证明测试失败。

### WU-202：NormalizedFilingMetadata v2 契约 ADR

依赖：WU-201。

冻结必需字段及语义：

- schema_version。
- canonical_entity_id、display_name、market、security_id；禁止仅用模糊公司名作为强身份。
- document_kind、regulatory_form、fiscal_year、period_end、period_kind。
- provider、provider_document_id、source_url、published_at、filed_at、accepted_at。
- language、is_amended、revision_id、supersedes_document_id。
- content_sha256、metadata_sha256、adapter_id、adapter_version、normalization_status。
- 每个关键字段的 evidence：origin、source_pointer、asserted_value、assertion_method、confidence、observed_at。

不进入语义身份的字段：root_id、绝对路径、company_raw/dayu/dropbox 名称、扫描时间。它们留在 location/source 记录。

空值规则：

- identity、document_kind、period、content hash 任一缺失时不得 capture-ready。
- source_url 不是所有本地历史文件绝对必需，但必须有等价不可变 provenance 组合；允许的组合要在 profile 中明列，不能靠 if root_id 放宽。
- 不可解析或冲突字段保留 indexed 状态与 reason codes，不静默填猜测值。

兼容规则：reader 支持 v1/v2 的时间窗、unknown version fail closed、序列化 golden fixture、字段新增/删除策略、hash canonicalization 均写入 schema compatibility matrix。

RED：META-01~12 覆盖缺身份、同名不同证券、同期间多 revision、错误日期、未知 kind、字段冲突、未知版本、证据指针断裂、hash 被篡改、模糊名称、旧 reader、新 reader。

### WU-203：复用与最新语义 ADR

依赖：WU-202。

冻结以下不变量：

- exact 请求：只解析指定 period/revision；命中有效 handle 时 network=download=0，也不做 latest discovery。
- latest 请求：先解析现有覆盖，再只读 discover 最新可得期，生成 GapPlan；只有缺期/更新 revision 可进入下载候选。
- 旧财报永不因新财报出现而删除；同期间更正版按 revision/accepted_at 排序且保留 supersession 链。
- “已 index”不等于“可复用”；只有 active、capture-ready、路径存在、hash 正确、root policy 允许的 handle 才可返回。
- 下载授权绑定 request、gap plan、policy/config hash、目标 canonical 路径和时效；计划变化后旧授权失效。
- 所有外部根始终只读；新下载只写 company-wiki canonical store。

### WU-204：SourceBundle 与 ArtifactHandle v2 ADR

依赖：WU-202。

SourceBundle 必须包含：

- filing handle 与 normalized metadata snapshot。
- catalog snapshot/version、root_id、location、content hash、capture state。
- artifact 角色 normalized、markdown、summary、sections、consumer_analysis 的候选与选择结果。
- 每个 artifact 的 artifact_hash、input_document_hash、parent_artifact_hash、producer_name/version、schema_version、prompt/model/config hash、created_at、status、evidence binding。
- reuse decision、拒绝 reason、需要重算的最小角色集合。

失效规则：

- 原文 hash 改变：所有派生工件失效。
- normalized schema/producer 改变：normalized 及其下游失效。
- summary prompt/model/config 改变：summary 和依赖 summary 的下游失效，不应重跑 PDF parser。
- evidence binding 或 section schema 改变：只失效依赖该 binding/section 的角色。
- retired/quarantined/missing filing：所有工件均不可复用。

### WU-205：目标架构蓝图与可执行 fitness functions

依赖：WU-201~204。

交付一份目标包/模块/依赖图，逐个标明保留、演进、新增、兼容、删除：

- company-wiki：RootPolicy/registry、scanner facade、v1 scanner、v2 orchestrator、adapters、normalizer、admission、assertion ledger、resolver v1/v2、bundle。
- filing-fetch：protocol client、reuse/latest/download coordinator、canonical capture。
- revenue：source-preparation orchestrator、validated source record、纯 forecast calculator。

蓝图同时生成可执行 architecture tests：

- scanner v2 只能依赖 adapter interfaces、normalizer、admission、persister ports。
- adapters 不依赖 CatalogStore、resolver、download、parser、LLM。
- resolver v2 不依赖 scanner/adapters，也不读取 legacy metadata keys。
- filing-fetch/revenue 不依赖 company-wiki 私有 Python 模块，只经版本化 CLI/contract。
- calculator 不依赖 filesystem/network/catalog。
- legacy modules 只能被 facade/compat tests 调用，不得获得新产品 caller。

ARC-FIT-01~06 分别删除一条边界、加入一条反向依赖、让 legacy 获得新调用者，均必须使 CI 失败。

### Phase 2 放行门

- 四份契约 ADR 与一份目标架构蓝图由三仓 owner 和独立 reviewer 签字；不存在开放占位项或尚未冻结的关键选择。
- schema golden、compatibility matrix、architecture RED 全部存在并有效失败。
- 任何实现代码仍未开始；contract_frozen 回执记录 plan/schema hash。

## Phase 3（RootPolicy 与 Adapter 配置模型）— 状态：pending

### WU-301：RootPolicy v2 schema

依赖：Phase 2。

目标字段：

- root_id：稳定授权键，重命名必须视为安全策略变化。
- path 或受控 path_token；禁止未解析变量、相对逃逸和网络路径默认启用。
- enabled、scan_enabled、read_only、reusable_for_filing、priority。
- adapter_id、adapter_version_range、admission_profile_id。
- routes：有序 include/exclude glob、对应 adapter/profile、明确 first-match 语义。
- allowed_document_kinds、allowed_artifact_roles、allowed_statuses。
- symlink_policy、max_file_size、sidecar_suffixes、encoding、privacy_class。

关键设计：root kind 不再承担授权和 parser 分发；同一 Dropbox/Stock 可用配置路由把 sidecar 完整的财报子树交给 sidecar_filing_v1，其余内容交给 generic_document_v1 且 reusable_for_filing=false。重叠路由在加载时拒绝或按已冻结优先级唯一匹配，不能扫描两次。

RED：

- CFG-01 未注册 adapter。
- CFG-02 未知 admission profile。
- CFG-03 root_id 重复。
- CFG-04 路径越界/未解析变量。
- CFG-05 可复用外部 root 却 read_only=false。
- CFG-06 route 重叠且无唯一顺序。
- CFG-07 generic_document 被错误允许作 filing。
- CFG-08 同一物理文件被两个 route 接纳。

### WU-302：受控 adapter/profile registry

依赖：WU-301。

- registry 为代码内受审、带版本和 capabilities 的静态清单；配置只引用 ID，不允许 module/class path 动态导入。
- capabilities 至少声明 supported metadata schema、grouping、document roles、identity strength、provenance modes、read-only guarantee。
- 启动时对配置与 registry 做完整兼容检查；任何未知项使该 root fail closed，并输出机器可读 reason。
- 新增同构 future_root 只改测试配置即可工作；新增未知 layout 必须新增 adapter + conformance，清楚界定“配置化”的真实边界。

### WU-303：单一安全策略导出与跨仓消费

依赖：WU-301。

- company-wiki 成为 RootPolicy 权威来源，输出版本化、canonical JSON policy snapshot 及 sha256。
- filing-fetch 和 revenue 只消费该快照或 resolver 回执中的 policy hash，不各自维护 Dropbox/dayu allowlist。
- policy export 不包含不必要的本机私密路径；允许 path token 与受控解析结果分离。
- config doctor 同时报告配置文件 hash、解析后 policy hash、registry version、不可用 root 与 reason。

RED：POL-01 修改任一消费者本地 allowlist 不得扩大权限；POL-02 policy hash 不一致拒绝复用；POL-03 过期 snapshot 拒绝下载授权。

### WU-304：迁移开关与 shadow 模式

依赖：WU-303。

定义独立开关：v2_scan_shadow、v2_persist_assertions、v2_resolve_shadow、v2_resolve_active、v2_bundle_active、legacy_bridge_enabled。每个开关有默认值、依赖、观测指标、回滚行为；禁止一个总开关同时改变扫描、持久化、解析和下载。

### WU-305：flag 状态机、cohort 与 circuit breaker

依赖：WU-304。

- 用一个版本化状态机验证所有 flag 组合；非法组合启动即失败。
- cohort 只能按 fixture、root_id、只读 request sample、consumer 选择，不按公司名或路径临时硬编码。
- scan/persist/resolve/bundle/download 分别有 error budget 与 breaker；下游 flag 不得在上游未 accepted 时启用。
- breaker 只执行安全 flag rollback，不修改 catalog/文件；保留 incident ID、触发指标、前后 policy hash。
- 配置重载必须原子，正在处理的请求固定使用启动时 snapshot，不能半请求切版本。

测试 FLAG-01~08：非法依赖、未知 cohort、并发 reload、breaker 触发、breaker 自身失败、stale config、回退后 v1 parity、外部写入异常。

### Phase 3 放行门

- CONFIG-E2E-01：在 future_root 放置合法 sidecar fixture，仅新增 root 配置即可 index→resolve→reuse，产品代码 diff=0。
- CONFIG-E2E-02：在相同配置中改成未知 adapter，启动失败且不会回退成 dayu 或 generic filing。
- RootPolicy conformance、config doctor、跨仓 policy-hash、flag state-machine/circuit-breaker tests 全绿并通过 mutation。

## Phase 4（统一 NormalizedFilingMetadata）— 状态：pending

### WU-400：冻结并演进唯一 assertion ledger

依赖：Phase 3。

现有 source_metadata_assertions 冻结为唯一 normalized fact owner，不新建第二个 writable assertion 表：

- 保留 assertion_id、source_id、document_id、content_sha256、decision、supersession、created_by/at 和 schema_version。
- 用 additive migration 增加 v2 必需的 published/accepted 日期、period_end、language、amended/revision、adapter/version、normalized hash、normalization status、visibility_state、activation_epoch/cohort 等列和查询索引。
- decision 只表达 candidate/verified/rejected 证据状态；visibility_state/activation_epoch 独立表达 shadow/canary/active reader 可见性。verified+shadow 不得被任何 active resolver 返回。
- evidence_json v2 使用版本化逐字段 evidence 结构；高频筛选字段同时物化为列，resolver 不在热路径扫描 JSON。
- v1 行不原地改写；backfill 生成新的 v2 candidate/verified assertion 并通过 supersession 链关联。
- raw acquisition/dayu/sidecar payload 继续不可变保留，但只供 adapter/migration 审计，不是第二真相源。
- store.py 的 schema 初始化与 migration 必须共用一份 schema owner；禁止 CREATE TABLE 定义和 upgrade 定义继续手工漂移。

### WU-401：领域对象、JSON Schema 与 canonical hash

依赖：WU-400。

- 在 company-wiki source_catalog 现有 models/normalizer/schema 体系内实现，不复制一套 contracts。
- 构造器拒绝非法组合；反序列化 unknown fields/version 遵循 WU-202 矩阵。
- canonical hash 排除扫描时间与绝对路径，包含所有影响复用的语义字段和 assertion evidence。
- 任何 adapter-specific 原始 metadata 仅作为 immutable raw payload 留存，resolver 不读取它。

测试 META-01~12 加 golden round-trip、property-based 日期/period/hash 测试和 schema mutation。

### WU-402：事务化 assertion 持久化

依赖：WU-401。

- 同一次扫描中 source/location/document/normalized assertion 要么全部提交，要么全部回滚。
- 幂等键必须绑定 content hash、adapter/version、metadata hash；重复扫描不得生成重复 active assertion。
- 新 assertion 与旧 assertion 冲突时并存并进入 conflict 状态，不覆盖历史。
- 持久层禁止以 root_id 选择 JSON container。

RED：TX-01 在每个写步骤注入异常验证零部分提交；TX-02 并发扫描同一文件只有一个有效结果；TX-03 metadata 改变生成新 assertion 且旧记录可审计。

### WU-403：来源 URL 与文档身份绑定修复

依赖：WU-402。

- 先写 RED：同一公司三份不同期间财报，只有其中一份有 URL；任何按 company_name 广播 URL 的实现都必须失败。
- backfill 只允许用 provider_document_id、内容 hash 或已验证的一对一 immutable key 绑定；无强键则保留 missing provenance 并进入 remediation queue。
- URL、published_at、period 任一来自不同文档时 admission 拒绝，并记录 field-level evidence 冲突。

### WU-404：legacy reader bridge 与 shadow parity

依赖：WU-403。

- legacy bridge 只在 normalized v2 缺失时读取旧 acquisition/dayu_meta，再立即产出内存 v2 candidate；resolver 主 SQL 不允许继续直接读旧容器。
- 在任何 verified v2 assertion 写入生产 catalog 前，v1 reader 必须显式固定为 v1 schema/legacy visibility；v2 reader 必须要求 current activation_epoch + active cohort。
- 对 company_raw/dayu 当前有效样本进行旧/新结果 parity：entity、kind、period、hash、status、canonical path 必须一致；差异进入清单，不能用宽松比较忽略。
- bridge 有指标、调用计数和退役条件；新写入不得再依赖 bridge。

测试 VIS-01 v1 忽略 v2 shadow；VIS-02 v2 忽略未激活 assertion；VIS-03 root cohort 激活全有或全无；VIS-04 rollback 只切 visibility/epoch 不删记录；VIS-05 并发请求固定各自 activation snapshot。

### Phase 4 放行门

- normalized facts 成为唯一新写语义源。
- schema/transaction/URL binding/shadow parity 测试全绿。
- mutation 删除任一关键字段、交换两个 period 的 URL、恢复双写时均被测试捕获。

## Phase 5（SourceAdapter SPI 与 adapter conformance）— 状态：pending

### WU-500：先建立 v1/v2 seam，零行为改变

依赖：Phase 4。

在 scanner 对 root 的处理入口建立唯一 facade/strategy seam：

- 默认和生产配置始终选择 v1。
- v1 实现体先原样移到 seam 后；本 WU 禁止同时重排、清理或修 bug。
- facade 固定输入 RootPolicy snapshot/scan context，输出 ScanReceipt；v1 额外输出 characterization trace adapter。
- v2 此时只有 unavailable stub；误启用必须 fail closed。
- 本提交不得改变 catalog schema、扫描计数、错误码、日志语义、线程/锁或文件访问。

检查点：

- SEAM-01 WU-104 全部 expected_good trace 字节级或 canonical 等价。
- SEAM-02 三仓聚焦测试和 company-wiki 全仓测试收集数不变。
- SEAM-03 性能 p95 不劣化超过 5%，无额外 DB transaction/file stat。
- SEAM-04 关闭 facade 或 revert 单一提交即可回到基线。
- SEAM-05 legacy v1 获得 freeze gate：以后只能做安全修复，禁止新增 root/layout 功能。

### WU-501：拆分 scanner orchestration

依赖：WU-500。

把当前大型、按 root kind 分支的 scanner 职责拆成明确流水线：

1. RootPolicy 解析并产生 route。
2. adapter.enumerate 只返回稳定排序的文件组与 role。
3. adapter.normalize 产生 NormalizedCandidate 和逐字段 evidence。
4. admission.evaluate 产生 admitted/rejected/indexed_only 及 reason codes。
5. persister 在事务中写 catalog。

SourceAdapter 方法签名、异常类型、迭代顺序和资源预算由 Protocol/ABC 固定。adapter 不接收 store writer、download client、parser 或 LLM；scanner 不读取 adapter-specific 字段。

RED：

- SPI-01 adapter 尝试 DB 写入或外部写入时 conformance spy 失败。
- SPI-02 scanner 中新增 root_id ==、kind == dayu、Dropbox 字面分支时 architecture gate 失败。
- SPI-03 adapter 返回未排序/重复候选时结果仍确定或明确拒绝。
- SPI-04 未知 root 不得落入最后一个 else adapter。

### WU-502：通用 adapter conformance kit

依赖：WU-501。

每个 adapter 必须运行完全相同的参数化套件：

- 确定性 enumerate：同一树两次输出、candidate hash、role 分组一致。
- 文件组：primary 唯一，sidecar/markdown/summary/sections 不得误作 original。
- 非 ASCII、长路径、大小写、同名文件、隐藏文件、临时文件。
- sidecar 缺失、损坏、unknown schema、编码错误、恶意 JSON、超大文件。
- symlink/junction 越界、相对路径逃逸、TOCTOU 替换。
- 身份/period/kind 冲突、弱身份、同名不同证券。
- 幂等、并发、取消、单文件失败不污染其他事务。
- read_only：adapter 运行前后 fixture inode/mtime/hash 不变。
- 无网络、无下载、无 parser、无 LLM。
- 输出必须能通过 NormalizedFilingMetadata schema；不能通过 raw metadata 绕开。

套件输出 adapter conformance receipt；少一个 mandatory capability 即不能加入 registry。

### WU-503：admission profile conformance

依赖：WU-502。

financial_evidence_v1 对所有 root 一视同仁执行：

- accepted official provider/provenance 组合。
- entity/security、period、kind、content hash 完整。
- location 位于已授权 route 且文件存在、hash 校验通过。
- active 状态；retired/quarantined/missing/conflict 全部拒绝。
- as-of 与 revision 规则。

用同一 candidate 只改变 root_id，admission 结果应相同；只改变 RootPolicy 权限时仅授权结论变化。测试 ADM-01~10 防止 “Dropbox 放宽”“company_raw 特权”。

### Phase 5 放行门

- WU-500 seam 零行为改变证明 accepted；scanner orchestration 与 adapter 实现可单独测试，source-specific 条件不再位于 scanner/persister/admission/resolver。
- conformance kit 至少对一个最小 fake adapter 先 RED 后 GREEN，并能杀死：删除 hash 校验、交换 sidecar role、允许路径越界、返回重复 candidate 四个 mutation。

## Phase 6（现有 company_raw/dayu adapter 等价迁移）— 状态：pending

### WU-601：company_raw adapter 提取

依赖：Phase 5。

- 从 scanner 迁出现有 company directory/layout/sidecar 解析，保持当前合格文件的 entity、kind、period、hash、status、priority 和 canonical location。
- company_raw 仍是唯一 writable root，但 write 权限来自 canonical writer policy，不写进 adapter。
- 原目录名只能作为一条 identity assertion；若 sidecar/security_id 冲突则进入 conflict，不能目录名强压。
- 运行全套 adapter/admission conformance。

Parity 样本必须覆盖 A/HK/US、annual/quarterly/semiannual、中文路径、已处理工件、同文件多 location。

### WU-602：dayu adapter 提取

依赖：WU-601。

- 把 dayu provider metadata 和文件分组映射移入 dayu adapter；不再使用 scanner 最终 else。
- 处理 company_name、ticker、provider_document_id、URL、accepted_at 的强弱证据优先级。
- 禁止跨 period/company_name URL 广播；无强绑定时 indexed_only。
- dayu 仍只读，download 路径和 adapter 扫描路径完全分离。

### WU-603：双跑 shadow parity

依赖：WU-602。

- 在 hermetic 全量 fixture 与真实根只读分层样本上同时执行 legacy scanner 与 v2 adapter，但 v2 先不作为 active resolver 输入。
- 比较 candidate 数、document hash、entity、kind、period、status、location、admission reason。
- 允许差异只有预先列明的 bug fix；每一差异需独立 reviewer 认可并有 RED 测试。
- 对 legacy 能错误放行而 v2 拒绝的情况记录 security improvement，不为了 100% 数字 parity 降低门槛。

### WU-604：逐 root ingest 切换

依赖：WU-603。

每次只切一个 root 的 enumerate/normalize/persist cohort，顺序固定：

1. hermetic company_raw。
2. hermetic dayu。
3. 真实 company_raw 的纯 shadow。
4. 真实 dayu 的纯 shadow。
5. 真实根 v2 candidate assertion 追加，resolver 仍只读 v1。

每一 cohort 都需：

- 三次无变更运行输出相同 candidate/assertion hash。
- 输入、成功、indexed_only、conflict、error 对账闭合。
- v1/v2 expected_good 逐 document parity；known-bad 差异命中既定 RED。
- DB fault/concurrency/取消测试无部分提交、无重复 active assertion。
- scan latency/error budget 满足冻结阈值。
- 单独 flag rollback 后 v1 行为和 catalog integrity 不变。

禁止同时切 company_raw 与 dayu；前一个 root 至少完成一轮 reviewer/soak 才能开始下一个。

### Phase 6 放行门

- 所有当前有效 company_raw/dayu 可复用场景无功能回归。
- scanner 删除 company_raw/dayu 大分支后 conformance 和 parity 仍绿。
- WU-604 两个 root 逐项 accepted；legacy 分支仍保留在 shadow flag 后，尚不删除；回滚只切 reader/scan flag，不反向迁移数据。

## Phase 7（Dropbox/通用 sidecar filing adapter）— 状态：pending

### 设计结论

实现名使用 sidecar_filing_v1，不使用 dropbox_adapter。Dropbox 是第一个真实使用者，不是语义特例。整个 Dropbox/Stock 可被 index，但只有匹配财报 route、sidecar/provenance/identity 完整并通过 admission 的文件才可作为 filing；其他文档仍可由 generic_document_v1 发现，但 reusable_for_filing=false。

### WU-701：sidecar schema v1

依赖：Phase 6。

sidecar 至少声明 schema_version、primary relative path/content hash、entity/security identity、document kind、fiscal period、provider/provenance、published/filed/accepted date、artifact roles 及各自 hash/binding。路径只允许相对当前文件组，禁止绝对路径和 ..。

兼容规则：

- 完整 sidecar → 可进入 admission。
- 缺 identity/period/kind/hash/provenance → 仍可 indexed_only，并输出确切 remediation reason；不得从文件名补成强事实。
- sidecar 解析失败 → 文件保持 generic/indexed，不得 crash 全 root。
- standalone sidecar 永远不是 original document。

### WU-702：基于配置的 route 与 focus 范围

依赖：WU-701。

- 把 root_id=dropbox_stock 和 重点关注 字面逻辑从 scanner/focus cleanup 移到 RootPolicy routes。
- 配置明确 route 匹配、排除、优先级和 profile；非重点子树仍可被 generic adapter index。
- 新增第二个完全不同目录名的 fixture root，复用 sidecar_filing_v1；只改配置完成同样行为。
- 同一文件只能由一个 route 负责；route 变更产生新 policy hash 并触发 shadow reconciliation。

### WU-703：实体解析去 company_raw 依赖

依赖：WU-702。

- 先以 security_id/market 和受控 entity registry 解析；display_name 仅辅助。
- Dropbox 中出现 company_raw 从未有目录的新公司仍可建立未绑定或已验证 entity assertion，不得因不在 companies 目录而消失。
- 同名公司、简称、繁简体、ticker 复用必须产生 ambiguous/conflict，需显式断言后才 capture-ready。

RED：DBX-ENT-01 新公司；02 同名不同市场；03 文件夹名与 sidecar security_id 冲突；04 只给模糊中文名；05 恶意把券商研报命名为年报。

### WU-704：Dropbox fixture 端到端行为

依赖：WU-703。

必须覆盖：

- DBX-01 仅 Dropbox 有完整官方财报：REUSED、download=0、canonical write=0。
- DBX-02 company_raw 和 Dropbox 同 hash：选一份 document、多 location，按 policy priority 返回且不重复。
- DBX-03 Dropbox 有旧年报，latest 缺新年：复用旧版并只下载新年到 company_raw。
- DBX-04 原文与有效 MD/summary/sections：SourceBundle 选择工件，parser/LLM=0。
- DBX-05 summary producer/version 过期：原文和 MD 复用，只重算 summary 及依赖下游。
- DBX-06 缺 source URL 且无等价 provenance：indexed_only、no download suppression claim。
- DBX-07 retired/quarantined：不可复用。
- DBX-08 sidecar hash 错：拒绝且不自动重写 sidecar。
- DBX-09 非重点子树普通文档：可 index，不可作为 filing。
- DBX-10 future_root 使用同 adapter/profile：只改配置通过。
- DBX-11 重名/歧义实体：fail closed。
- DBX-12 broker report 带年报文件名：fail closed。
- DBX-13 路径越界/symlink：fail closed。
- DBX-14 同期间正式版与更正版：选择规则正确且两者保留。

### Phase 7 放行门

- 代码中没有 Dropbox root 名或重点关注语义分支。
- DBX-01~14 先 RED 后 GREEN，future_root 证明 config-only 目标。
- 外部 fixture 与三个真实根均无写入；真实 Dropbox 功能尚不能仅凭 fixture 宣称完成。

## Phase 8（Resolver/SQL 来源无关化）— 状态：pending

### WU-801：normalized-only query model

依赖：Phase 7。

- resolver SQL 连接 normalized assertions、documents、locations、roots/policy snapshot；禁止读取 acquisition/dayu_meta 或 adapter raw payload。
- identity、kind、period、status、as-of、root authorization 尽量 SQL pushdown，Python 仅做最终 deterministic ranking 和 handle 构造。
- 查询参数必须使用 canonical_entity_id/security_id；display name lookup 是独立解析步骤并返回歧义。
- 结果说明所有 rejected reason，不能静默跳过到下载。

### WU-802：来源无关 ranking 与 canonical location

依赖：WU-801。

排序键按 ADR 冻结，例如：identity strength、exact period、revision、active status、root priority、provenance quality、content hash 稳定 tie-break。排序键不得包含 source 类型名称。

同 document 多 location：

- 只返回一个 handle，但保留 locations 列表。
- 首选存在、hash 正确、policy 允许的最高优先位置。
- 首选位置丢失可切换到另一有效位置；不存在任何有效位置则 missing/fail closed。

### WU-803：ArtifactHandle/SourceBundle 查询接合

依赖：WU-802。

- resolver 返回 capture-ready handle 后，在同一 catalog snapshot 上查询 artifact DAG，避免 filing 与 artifact 跨事务错配。
- handle 包含 normalized metadata hash、policy hash、catalog snapshot/version；消费者二次验证。
- SourceBundle 查询不得改变 DB，不触发 parser/LLM。

### WU-804：shadow resolver 差异门

依赖：WU-803。

- legacy 与 v2 同请求双跑，记录 selected document/location/reason/status。
- company_raw/dayu 合法样本必须 parity；Dropbox/future_root 是预期新增能力。
- legacy 错误放行、v2 拒绝是安全改进；v2 错误放宽是阻断缺陷。
- 未解释 diff=0 后才能切 v2_resolve_active；不得仅看成功率。

### WU-805：性能与查询计划

依赖：WU-804。

在 100,000 documents、300,000 locations、500,000 assertions、1,000,000 artifacts 合成库上：

- exact resolve warm p95 ≤ 300ms，latest/gap p95 ≤ 750ms；阈值可在基线后收紧，不得未经 ADR 放宽。
- EXPLAIN QUERY PLAN 必须命中已声明索引，禁止全表扫描关键表。
- 内存峰值 ≤ 256MB；不得把全 catalog 加载到 Python。

### WU-806：逐 root/请求 cohort 切换 resolver

依赖：WU-804/805。

切换顺序：

1. hermetic company_raw exact。
2. hermetic dayu exact。
3. hermetic sidecar/future_root exact。
4. 真实只读 company_raw sample。
5. 真实只读 dayu sample。
6. fixture latest/bundle 查询；生产 latest/bundle 仍关闭，等待 Phase 10/11。

每一步保存 v1/v2 selected/rejected 全量 diff、reason、SQL plan、latency、handle hash；任何未解释 diff 都 stop-the-line。active v2 请求失败时对用户 fail closed 并触发 breaker/告警，不得在同一请求中悄悄回 v1；回滚通过 cohort flag 对下一请求生效。

RES-CUT-01~08 覆盖 cohort isolation、并发 flag change、v2 timeout、v1 rollback、ambiguous、missing location、policy snapshot change、catalog snapshot change。

### Phase 8 放行门

- normalized-only 静态 gate、SQL pushdown tests、shadow diff、性能门、逐 root resolver cutover 和删索引 mutation 均通过。

## Phase 9（历史 catalog 迁移、治理与显式恢复）— 状态：pending

### WU-901：可恢复 migration 工具

依赖：Phase 8。

- 支持 dry-run、shadow-write、apply、verify、resume；默认 dry-run。
- 迁移前生成 SQLite 一致性 snapshot/backup、schema/version/hash、roots/config/policy hash和行数基线。
- 每批事务记录 journal、last key、输入/输出 hash、created assertion IDs；中断可从已提交边界恢复。
- migration 只写 catalog，不触碰任何外部文件或 sidecar。
- 重跑不产生重复 assertion；不同代码/plan hash 不能无提示续跑。

故障测试 MIG-01~08：每批边界 crash、磁盘满、DB lock、schema mismatch、配置变化、重复执行、校验失败、rollback flag。

### WU-902：company_raw/dayu 历史 backfill

依赖：WU-901。

- 只从强绑定 legacy 字段构造 v2 assertions。
- 无法证明的 URL/identity/period 放入 remediation queue，不猜测补齐。
- backfill 后按 root/status/kind/year 对账：输入、成功、indexed_only、conflict、skipped、error 数量之和严格等于候选数。
- legacy active 可复用集与 v2 active 可复用集逐项 parity；差异附 document ID 和 reason。

### WU-903：Dropbox 历史 backfill 与治理

依赖：WU-902。

- 先只读 enumerate/dry-run，报告 complete、missing identity、missing provenance、hash mismatch、ambiguous、non-filing 等分桶。
- 只对已有完整 sidecar/强 catalog assertion 的文件生成 v2 active candidate；不得为通过 canary 自动写 sidecar。
- 当前 retired 资产保持 retired。不能因为新 adapter 能解析就自动 restore。
- 对疑似官方财报给 remediation receipt：所缺字段、可接受证据、人工审查入口，不把文件内容或隐私路径写入普通日志。

### WU-904：显式 restore 流程

依赖：WU-903。

restore 必须满足：

- 指定 document/location/assertion ID，不支持 company-wide 模糊恢复。
- 文件仍存在且 content hash 与被审记录一致。
- v2 normalized metadata 完整、provenance 通过、root policy 允许。
- reviewer 明确批准并生成 immutable restore receipt。
- 状态变化保留原 retire reason、restore reason、actor/time/policy hash；可通过新事件回退，不删除历史。

RED：REST-01 缺 URL/等价 provenance；02 hash 变化；03 root 不允许；04 模糊批量；05 retired 自动扫描；06 reviewer/receipt 缺失，全部拒绝。

### WU-905：catalog 切换与验证

依赖：WU-904。

依次执行：

1. backup integrity check。
2. v2 assertions shadow 完整迁移。
3. parity 和 reconciliation 零未解释差异。
4. resolver shadow。
5. 只把 v2 reader 切 active；legacy 数据不删除。
6. 验证 exact/latest/bundle/worker。
7. 保留 feature-flag rollback 到 legacy reader。

### WU-906：迁移破坏演练与恢复证明

依赖：WU-905。

在两份独立生产 snapshot copy 上演练：

- 路径 A：完整 migrate→verify→v2 read→flag rollback→v1 read，业务结果保持。
- 路径 B：中批次 crash→resume→verify。
- 路径 C：故意制造 reconciliation mismatch，确认切换被阻止。
- 路径 D：恢复 backup 到新路径，integrity/hash/count 与迁移前完全一致。
- 路径 E：迁移代码已升级但 journal/plan hash 旧，必须拒绝 resume。

恢复目标：数据丢失/错误 restore=0；复制库 RTO 在基线测量后冻结，发布不得超过；演练命令由非实现 reviewer 独立执行。禁止用恢复生产库的方式测试。

### Phase 9 放行门

- 迁移在全量合成库和两份独立生产 snapshot copy 上成功，WU-906 五条破坏/恢复路径 accepted；真实生产 apply 需要独立变更窗口和明确授权，不能由本计划预先视作完成。

## Phase 10（SourceBundle 生产主链接入）— 状态：pending

### 先决结论

当前 company-wiki 的 SourceBundle query、revenue 的 build_revenue_source_record/select_reusable_artifacts 与 filing-fetch client 主要由测试或手工技能步骤调用。Phase 10 的完成标准不是再增加 helper，而是让一个用户实际调用的显式入口跨越三仓并可由子进程 E2E 观察。

### WU-1000：冻结唯一生产编排入口

依赖：Phase 9。

ADR 推荐方案：

- company-wiki resolve CLI/API 在同一 catalog snapshot 中返回 FilingHandle + SourceBundle。
- filing-fetch 的 fetch/resolve 生产 CLI 保真校验并转发 bundle，同时执行 exact/latest/gap/download 决策。
- revenue-forecast 新增明确的 source-preparation 命令/服务边界，接受 FilingRequest，调用 filing-fetch，验证 SourceBundle，选择可复用 artifact，输出 RevenueSourceRecord 与 reuse receipt。
- SKILL.md 只调用 source-preparation，不再要求模型手工串接多个 helper。
- scripts/revenue_forecast.py 保持纯计算，输入是已准备并验证的 source record；不得加入网络、catalog 或下载。

在实现前先写 PROCESS-RED-01：从 revenue 用户入口启动真实子进程；当前代码应因不存在完整编排而失败。直接 import helper 或测试内构造 bundle 不算 RED。

该入口边界在本计划中冻结。若实现证据证明不可行，必须停止并返回 Phase 2 修订 ADR/plan hash；实施者和 reviewer 均不得在 WU-1000 内自行改成另一条生产链。

### WU-1001：company-wiki 原子 SourceBundle 输出

依赖：WU-1000。

- 扩展现有 resolver/source_bundle/cli，不创建平行 catalog client。
- 在一个 read transaction/snapshot 中选择 filing 与 artifacts，输出 schema_version、snapshot、normalized hash、policy hash。
- artifact selection 返回 selected/rejected 及 reason；不隐藏旧工件。
- JSON stdout 只含协议，诊断写 stderr；退出码区分 NOT_FOUND、NOT_ADMISSIBLE、AMBIGUOUS、STALE_BUNDLE、INTERNAL。
- query 只读，network/parser/LLM/write=0。

### WU-1002：filing-fetch 保真转发与二次验证

依赖：WU-1001。

- 复用 scripts/fetch_filing.py 和 filing_contracts.py；不维护自己的来源分支。
- 校验 schema compatibility、document/artifact hash、path fence、root/policy/snapshot、status、binding。
- 对未知 artifact role/version fail closed；对可理解但不可复用的工件保留 filing handle 并列出 recompute roles。
- bundle 字段不得丢失、重命名或重算；增加 byte/canonical JSON round-trip golden。
- download 路径返回的新文档也必须重新经过 catalog capture/resolve，不能手工构造“可信 handle”。

### WU-1003：revenue source-preparation 实际消费

依赖：WU-1002。

- 演进 filing_fetch_client.py、company_wiki_source.py 与 contracts；新增编排 CLI 需要独立文件且只做 orchestration。
- 输出 RevenueSourceRecord 必须绑定 FilingHandle、normalized source、selected artifact、as-of、producer/config hash。
- 若 MD/summary/sections/consumer_analysis 有效，直接复用；每个角色分别决定，禁止 all-or-nothing。
- 若工件失效，只调用对应 producer；调用次数写 receipt。
- 不允许 fallback 到直接打开原始 PDF 并无记录解析；fallback 必须显式产生 recompute plan。

### WU-1004：文档与技能入口切换

依赖：WU-1003 且跨进程 E2E 已绿。

- 更新三个 SKILL.md/使用文档，删除手工 helper 拼接说明。
- 每个示例由 executable documentation test 调用实际 source-preparation。
- forbidden-claim gate 检查：只有 PROCESS-E2E 通过后才能写“生产已接通”。
- 对旧入口标 deprecation，保留明确兼容期；不得文档先行宣称完成。

### WU-1005：逐 consumer 协议切换

依赖：WU-1001~1004。

顺序固定：

1. company-wiki CLI v2 仅 shadow 输出，与 v1 响应比较。
2. filing-fetch client 接受 v2 bundle 但仍返回 v1-compatible envelope。
3. filing-fetch 默认 v2，旧 client compatibility tests 继续。
4. revenue source-preparation 在 fixture cohort 使用 v2。
5. revenue 默认 v2；旧手工步骤只保留显式 deprecated 命令，不 silent fallback。
6. SKILL.md/实际用户入口最后切换。

每个 consumer 需 contract version negotiation、malformed/unknown version、stdout 污染、timeout、partial response、policy/hash 篡改、rollback tests。切换期间协议 adapter 只做字段映射，不允许重新解释 identity/provenance 或放宽 handle。

### Phase 10 放行门

- 从 revenue source-preparation 子进程到 filing-fetch 子进程/CLI，再到 company-wiki catalog fixture 的真实边界可观测。
- PROCESS-E2E-01 命中已有 filing/artifact 时 network=download=parser=LLM=write=0。
- PROCESS-E2E-02 artifact 过期时只调用预期 producer。
- PROCESS-E2E-03 bundle hash/policy/snapshot 篡改时三层至少一层拒绝，且绝不静默重读原文。
- CodeGraph/调用图证明 product entrypoint 调用链存在；helper-only caller gate 不再触发。
- WU-1005 每个 consumer 独立切换/回滚通过，compat adapter 没有安全语义分支。

## Phase 11（latest/gap/下载抑制闭环）— 状态：pending

### WU-1101：现有 latest/gap drift audit

依赖：Phase 10。

先对 gap_plan.py、现有 latest tests、filing-fetch latest 实现做 contract diff；满足 WU-203 的逻辑直接保留，不重写。把差异分成 missing、incorrect、unwired 三类，每项有测试 owner。

GapPlan 至少包含 requested periods、covered periods/revisions、missing periods、stale revisions、discovery evidence、download candidates、authorization requirement、plan/config/policy hash。

### WU-1102：exact 零副作用

依赖：WU-1101。

- 命中任一允许 root 的有效 exact filing 时：discovery=network=download=canonical write=parser=LLM=0。
- exact 未命中且无下载授权：返回 NOT_FOUND + gap reason，不做“帮用户顺便”下载。
- exact 命中旧 revision 但请求明确 latest_revision 时才允许 discovery。

测试 EXACT-01 company_raw；02 dayu；03 sidecar/Dropbox；04 future_root；05 hash mismatch；06 retired；07 ambiguous；08 policy hash mismatch。

### WU-1103：latest 覆盖与只补缺口

依赖：WU-1102。

- 先聚合全部允许 root 的已有 coverage，不因 canonical store 为空就忽略外部 root。
- discovery 只获得元数据/候选版本，不下载。
- 同 fiscal period 已有相同 revision/hash 时 gap 为空。
- 发现更正/新 revision 时只下载新 revision；旧文件与其 artifacts 保留。
- 多个缺期形成确定、去重、排序的 download candidates。

测试 LATEST-01 全覆盖零下载；02 Dropbox 旧期+远端新期；03 dayu/company_raw 分散覆盖；04 同期间相同 hash；05 更正版；06 provider 重复候选；07 as-of 截止；08 discover failure。

### WU-1104：下载授权与单次写入

依赖：WU-1103。

- 授权必须显式，绑定 immutable GapPlan；授权后再次 resolve，避免竞态下重复下载。
- provider 下载到临时区，校验 hash/类型/identity/period 后仅由 canonical writer 原子写 companies 路径。
- capture 完成后再次走 v2 resolver；失败不得返回人工构造 handle。
- 网络重试、并发请求、进程 crash 不得生成重复或半文件。
- 外部根写入计数始终 0。

测试 DL-01 无授权；02 plan 过期；03 两进程竞态；04 下载后校验失败；05 canonical write crash；06 provider 重复响应；07 capture 失败；08 成功只写一次。

### WU-1105：旧文档与已处理工件协同

依赖：WU-1104。

场景：Dropbox 有 FY2024 原文、MD、summary；latest 发现 FY2025。期望：

- FY2024 原文和所有有效 artifact 继续复用。
- 只下载 FY2025 到 company_raw。
- FY2025 只运行缺失 producer。
- 返回 coverage 同时包含两个 root/location；不搬运 FY2024。
- 第二次运行两个期间均零下载，且已生成 FY2025 artifact 可复用。

### Phase 11 放行门

- EXACT/LATEST/DL tests 及跨进程 spy 全绿；删除一次 second resolve、篡改 GapPlan hash、把 missing 改成 all periods 三个 mutation 均被杀死。

## Phase 12（三仓跨进程 E2E 与场景矩阵）— 状态：pending

### 12.1 测试层级的强制定义

- component：单进程直接调用一个对象，可 mock 相邻边界。
- contract：验证 schema、CLI、adapter、policy 或 DB 协议，可用 fake 实现。
- integration：一个仓内多个真实组件和临时 DB/文件系统，不得 mock 被测内部链。
- cross-repo E2E：从 revenue 用户入口启动真实子进程，使用三个仓当前源码、真实 CLI/JSON 协议、临时 catalog 和 fixture 根；只可替换最外部下载 provider、parser、LLM 为记录调用的 spy。
- real canary：连接真实只读 catalog/root；不等同 CI E2E。

任何直接构造 FilingHandle/SourceBundle 的测试禁止命名 E2E。E2E 必须在回执中保存完整命令、子进程 argv/exit、协议摘要和 spy log。

### 12.2 共用 spy 与预算断言

统一 spy 捕获 network、discovery、download、canonical writer、external writer、PDF parser、normalizer producer、summary LLM、sections producer、consumer analysis producer。每个场景声明精确调用次数；不允许只断言“结果成功”。

全场景共用不变量：

- 未授权 external write=0。
- reuse 场景 download=0。
- 有效 artifact 场景对应 producer=0。
- 所有返回路径必须位于对应 RootPolicy route。
- 所有返回 hash 与 fixture manifest 一致。
- 第二次幂等运行除明确更新场景外，catalog 行数与调用预算不增加。

### 12.3 配置与 adapter 场景

| ID | 前置 | 行为 | 必须断言 |
|---|---|---|---|
| A-01 | future_root 使用 sidecar_filing_v1 | 仅新增配置并 resolve | 产品代码 diff=0；REUSED |
| A-02 | unknown adapter | 启动 | fail closed；不 fallback |
| A-03 | 相同路径不同 root_id/policy | resolve | 授权隔离，policy hash 不串用 |
| A-04 | routes 重叠 | load config | 按冻结规则拒绝或唯一匹配 |
| A-05 | generic route 普通 PDF | resolve filing | indexed_only，不冒充 filing |
| A-06 | symlink/junction 越界 | scan | 拒绝；目标文件无读取/写入 |
| A-07 | 外部 root read_only=false | load config | 配置拒绝 |
| A-08 | adapter schema version 超范围 | scan | root unavailable + reason |
| A-09 | 两次无变更扫描 | scan twice | candidate/catalog hash 稳定 |
| A-10 | 单文件 sidecar 损坏 | scan root | 该文件拒绝，其他文件继续 |

### 12.4 Normalized metadata 与身份场景

| ID | 前置 | 行为 | 必须断言 |
|---|---|---|---|
| N-01 | 完整官方 sidecar | scan | active capture-ready |
| N-02 | 缺 period | scan | indexed_only，MISSING_PERIOD |
| N-03 | content hash 错 | scan | HASH_MISMATCH |
| N-04 | 新公司不在 companies | scan | 用强 security_id 建立/绑定 assertion |
| N-05 | 同名不同证券 | resolve by name | AMBIGUOUS，零下载 |
| N-06 | 三期间仅一条 URL | backfill | URL 只绑定正确文档 |
| N-07 | 券商研报伪装年报 | admission | NOT_OFFICIAL/NON_FILING |
| N-08 | standalone sidecar | scan | role=metadata，不建 original |
| N-09 | 同期间正式版/更正版 | resolve | revision 选择和 supersession 正确 |
| N-10 | entity 文件夹名与 sidecar 冲突 | scan | CONFLICT，不覆盖 |
| N-11 | unknown schema version | scan | fail closed，raw payload 保留 |
| N-12 | published_at 晚于 as-of | resolve | 不可见 |
| N-13 | metadata hash 篡改 | consume | bundle 拒绝 |
| N-14 | 同一 hash 多 location | resolve | 单 document、多 location |

### 12.5 复用、最新与下载场景

| ID | 前置 | 行为 | 必须断言 |
|---|---|---|---|
| R-01 | company_raw exact 命中 | prepare | REUSED；全部副作用 0 |
| R-02 | dayu exact 命中 | prepare | REUSED；全部副作用 0 |
| R-03 | Dropbox-only exact 命中 | prepare | path 在 fixture Dropbox；download/write 0 |
| R-04 | future_root exact 命中 | prepare | 与 R-03 等价且代码无特例 |
| R-05 | 首选 location 丢失、次选有效 | prepare | 切换次选；不下载 |
| R-06 | retired/quarantined | prepare | 拒绝；不自动 restore |
| R-07 | 路径存在但 hash 变化 | prepare | 拒绝；不读作可信 |
| R-08 | policy snapshot 过期 | prepare | STALE_POLICY |
| L-01 | 多根覆盖所有期 | latest | gap 空、download 0 |
| L-02 | Dropbox 旧期、远端新期 | latest authorized | 旧期复用，只写新期 |
| L-03 | company/dayu 分散覆盖 | latest | 合并 coverage，不下载 |
| L-04 | 同期同 revision 重复候选 | latest | 去重 |
| L-05 | 同期出现更正版 | latest | 只下更正版，旧版保留 |
| L-06 | as-of 早于新披露 | latest | 不下载未来文档 |
| L-07 | discovery 暂时失败 | latest | 不把失败当无缺口，也不盲下 |
| L-08 | 两并发授权相同 gap | latest | 单次 canonical write |
| L-09 | 下载内容 period 不符 | capture | 隔离/拒绝，不返回 handle |
| L-10 | 第二次运行 | latest | 全部复用，download 0 |

### 12.6 Artifact 与 SourceBundle 场景

| ID | 前置 | 行为 | 必须断言 |
|---|---|---|---|
| B-01 | 原文+有效 MD+summary+sections | prepare | parser/LLM/sections producer=0 |
| B-02 | summary producer 过期 | prepare | 仅 summary 与依赖下游重算 |
| B-03 | PDF parser 版本变 | prepare | MD/sections/downstream 按 DAG 失效 |
| B-04 | consumer_analysis 过期 | prepare | 只重算 consumer_analysis |
| B-05 | artifact input hash 不匹配 | prepare | 不复用该 artifact |
| B-06 | artifact path 越界 | prepare | bundle 拒绝 |
| B-07 | artifact status retired | prepare | 不复用；原文仍可用 |
| B-08 | unknown artifact schema | prepare | fail closed，不 fallback 静默解析 |
| B-09 | filing 与 artifact snapshot 错配 | prepare | STALE_BUNDLE |
| B-10 | bundle 在 filing-fetch 转发 | round trip | canonical JSON/hash 保真 |
| B-11 | evidence binding 仅 sections 改变 | prepare | 只失效依赖 roles |
| B-12 | 同角色两个有效候选 | prepare | deterministic ranking + rejection reasons |

### 12.7 迁移、故障与对抗场景

| ID | 前置 | 行为 | 必须断言 |
|---|---|---|---|
| M-01 | legacy company/dayu catalog | dry-run/apply | 对账闭合、幂等 |
| M-02 | Dropbox 缺 provenance | migrate | remediation，不 active |
| M-03 | retired 官方文件可解析 | migrate | 仍 retired |
| M-04 | batch 中途 crash | resume | 无重复/部分记录 |
| M-05 | plan/config hash 变化 | resume | 拒绝旧 journal |
| M-06 | restore 合格资产 | restore | 新事件+receipt，历史保留 |
| M-07 | restore hash 已变 | restore | 拒绝 |
| M-08 | rollback reader flag | resolve | legacy 可恢复，v2 数据不破坏 |
| F-01 | company-wiki 子进程非零退出 | prepare | 原错误传播，不触发下载 fallback |
| F-02 | stdout 混入日志/无效 JSON | prepare | 协议拒绝 |
| F-03 | filing-fetch timeout | prepare | 有界失败、无半写 |
| F-04 | parser/LLM spy 被 reuse 场景调用 | prepare | 测试失败 |
| F-05 | external write spy 任一调用 | 全场景 | 测试失败 |
| F-06 | TOCTOU：resolve 后换字节 | consume | 二次 hash 校验拒绝 |
| F-07 | SQL 索引移除 | performance | query-plan/SLO gate 失败 |
| F-08 | 测试被 skip/阈值放宽 | CI | plan/collection gate 失败 |
| F-09 | 把 root 名硬编码进 resolver | architecture | 静态 gate 失败 |
| F-10 | 删除一个 admission 校验 | mutation | 对应负例失败 |

### 12.8 重构切换专项场景

| ID | 前置 | 行为 | 必须断言 |
|---|---|---|---|
| RF-01 | ScannerFacade 默认 v1 | seam commit | v1 golden/side-effect/性能等价 |
| RF-02 | v1/v2 同输入 | pure shadow | expected_good 结构化输出一致 |
| RF-03 | 已登记 known-bad | v1/v2 shadow | v2 仅按对应 RED 改正 |
| RF-04 | v2 多放行一项 | cutover gate | stop-the-line、cohort 不放量 |
| RF-05 | v2 少返回一项 | cutover gate | 必须分类解释，否则停止 |
| RF-06 | production dry shadow | scan/resolve | catalog/file/network/write 全为 0 |
| RF-07 | 只启一个 root cohort | scan/resolve | 其他 root 仍走 v1 且输出不变 |
| RF-08 | breaker 触发 | 下一请求 | flag 原子回退；无 DB 反向迁移 |
| RF-09 | migration 中途 crash | resume | journal 幂等、零部分/重复 active |
| RF-10 | consumer v2 协议异常 | request | fail closed；可显式回旧协议 |
| RF-11 | legacy disabled 窗口 | soak | legacy/bridge hit=0；v2 SLO 达标 |
| RF-12 | 删除 legacy 独立提交 | revert cleanup | 可恢复源码且 v2 数据不变 |

### WU-1201：E2E harness

依赖：Phase 11。

- 用 temp 根、temp SQLite、明确环境变量和绝对仓库路径启动三个真实 Python 子进程。
- 安装/导入方式与实际技能入口一致，不通过 PYTHONPATH 偷换测试模块。
- provider/parser/LLM spy 是独立可执行边界，记录 JSONL；测试结束校验预算。
- 每个测试有总 timeout 和子进程 kill/清理；Windows 路径/编码/文件锁均覆盖。
- stdout/stderr/exit code、fixture/config/policy/catalog hash 进入 E2E receipt。

### WU-1202：场景分层实施顺序

1. 先完成 RF-01~03、A/N contract RED，证明 seam、adapter/metadata 的失败模式。
2. 再完成 R/L integration，证明 resolver/gap。
3. 再完成 B integration，证明 artifact DAG。
4. 完成 RF-04~10，证明切换、breaker、迁移和协议回退。
5. 最后完成 R/L/B/F 的 cross-repo E2E；不得用前四级替代第五级。
6. M 与 RF-09 场景在生产 snapshot copy 上复跑。
7. RF-11/12 只能在 Phase 15 退役窗口完成。

### Phase 12 放行门

- 上表所有 mandatory ID 有 node ID、owner、层级、RED commit、GREEN receipt；不允许用参数化大测试隐藏未运行 case。
- cross-repo E2E 至少覆盖 R-01/02/03/04、L-02/05/08/10、B-01/02/06/09、F-01/02/04/05/06。
- RF-01~10 全部 accepted；RF-11/12 已有冻结测试和 Phase 15 owner。
- 每个 reuse/download/recompute 分支至少有一个 mutation proof。
- 重跑三次结果与调用预算稳定，无 flaky retry 掩盖。

## Phase 13（真实只读 canary、性能和可观测性）— 状态：pending

### WU-1301：真实根只读保护器

依赖：Phase 12。

对以下根建立受隐私保护的前后探针：

- C:/Users/郑曾波/Projects/company-wiki/companies
- C:/Users/郑曾波/Projects/dayu-agent/workspace/portfolio
- C:/Users/郑曾波/Dropbox/Stock

探针分两级：

- 快速级：文件数、总字节、目录/文件 mtime 聚合、抽样 hash、拒绝/新增事件。
- 完整级：在发布窗口对所有 candidate 路径记录相对路径 salted hash、size、mtime、content hash；receipt 不泄漏敏感文件名。

运行期间用 filesystem write spy/ACL 或受控只读 wrapper 阻止外部根写入；公司 canonical writer 只有在明确下载场景且获授权时开放。任何外部 root mtime/hash 变化立即中止并调查。

### WU-1302：只读 discovery canary

依赖：WU-1301。

在生产 catalog/root 上只运行 config doctor、enumerate shadow、normalized dry-run、resolver shadow：

- 不 apply migration、不 restore、不下载、不 parser、不 LLM。
- 按 root/route 输出候选数、admitted/indexed_only/conflict/error 及 reason code 分布。
- 对 Dropbox 验证 whole-root generic index 与 filing route 的边界。
- 对当前已知无合格 Dropbox-only active filing 的情况，结果允许为 0；这不是实现失败，但也不是生产复用已完成证明。

退出：探针前后相同，shadow 无 crash/隐私泄漏，统计可对账。

### WU-1303：真实 Dropbox-only reuse canary 的严格前置

依赖：WU-1302、Phase 9 获批 apply/restore。

候选必须是已经存在的官方 filing，且：

- 只在 Dropbox 有有效 location，company_raw/dayu 无同文有效 location。
- sidecar 或 catalog assertion 已具有强 identity、period、kind、content hash 和允许的 provenance。
- active/capture-ready，reviewer 手工核验内容与 metadata 对应。
- 测试不得写或修改 Dropbox sidecar。

若找不到此候选：

- 记录 BLOCKED_NO_ELIGIBLE_PRODUCTION_SAMPLE。
- fixture E2E 保持绿色，但不得勾选“真实 Dropbox 已验收”。
- 后续只能由用户明确授权一个 metadata remediation/restore 变更窗口；不能让实施模型自行创建证据。

合格 canary 期望：从实际 revenue source-preparation 发起，selected root=Dropbox、canonical path 在 Dropbox route、download=canonical write=parser/LLM=0；重复两次结果一致。

### WU-1304：真实 processed-artifact canary

依赖：WU-1303。

选择一个拥有至少 MD 与 summary 的真实 filing：

- 第一次运行验证 artifact hash/binding 后 parser=LLM=0。
- 通过 catalog snapshot copy 模拟 producer version 或 binding 改变，验证只产生 recompute plan；不得对真实文件写入或真的调用 LLM。
- 把复制库恢复后再次运行，确认生产只读数据未变。

### WU-1305：可观测性与 reason taxonomy

依赖：WU-1302。

结构化指标至少包括：

- scan candidates/admitted/indexed_only/conflict/error，按 root/route/adapter/version。
- resolver requests/hit/miss/ambiguous/rejected，按 reason code，不记录公司/文件私密名称。
- reuse/download_suppressed/gap/download_authorized/downloaded。
- artifact selected/rejected/recomputed，按 role/reason。
- legacy bridge hits、shadow diffs、migration remaining。
- latency p50/p95/p99、DB busy/timeout、subprocess failure。

reason codes 是版本化 enum；禁止用自由文本作为测试断言。日志需 redact 绝对路径、URL token、文档内容。

### WU-1306：容量、性能与稳定性

依赖：WU-1305。

- 使用 Phase 8 大库压测 exact/latest/bundle 和 scan incremental。
- 无变更增量扫描不得重新 hash 所有大文件；用稳定 fingerprint 策略并有 TOCTOU 安全复核。
- 10 个并发 prepare 请求无重复下载、无 DB deadlock、无跨请求 bundle 混用。
- 24 小时 soak 使用合成根，内存无单调增长、worker 无僵尸子进程。
- 阈值以 WU-805 为最低门，baseline 更优时采用“不劣化超过 10% 且绝对阈值均满足”；放宽需独立性能 ADR。

### Phase 13 放行门

- read-only discovery 必须完成；真实 Dropbox-only canary 若无合格样本保持显式 blocked，不能被忽略。只有真实 canary 完成后才可发布“Dropbox 生产复用已验证”声明。

## Phase 14（CI、mutation、发布与回滚）— 状态：pending

### WU-1401：三仓分层 CI

依赖：Phase 13 中 fixture 与只读 discovery，不要求先有真实合格样本。

每仓 PR gate：

- lint/type/schema/architecture。
- unit + contract + integration。
- collection manifest、skip/xfail、threshold 防降级。
- receipt schema/plan hash/changed-file allowlist。

跨仓 gate：

- 以明确三仓 commit matrix checkout，运行 Phase 12 cross-repo E2E。
- 不允许测试自动使用本机其他未声明 checkout。
- 协议 compatibility 覆盖 N-1 reader/current writer 与 current reader/N-1 fixture；不承诺未测试组合。

nightly：

- migration fault injection、大库性能、三次稳定性、mutation、Windows 非 ASCII 路径。
- real canary 与 CI 分离，仅在用户机器获批只读运行，不上传文件内容。

### WU-1402：定向 mutation gate

依赖：WU-1401。

至少维护下列人工 mutation：

1. 删除 content hash 校验。
2. 把 retired 当 active。
3. 用 company_name 广播 URL。
4. resolver 恢复 acquisition/dayu_meta 分支。
5. future_root fallback 到 dayu。
6. external root 写保护失效。
7. GapPlan 把 covered periods 也列为 missing。
8. 下载后省略 second resolve。
9. SourceBundle 忽略 policy hash。
10. artifact selector 忽略 producer version。
11. 把 summary 失效扩大为重跑 parser。
12. 把 subprocess E2E 改成直接 helper 调用。

每个 mutation 必须由指定测试杀死；mutation 存活即 phase 失败。自动 mutation 分数可辅助，不替代这 12 个高风险 mutation。

### WU-1403：分阶段发布

依赖：WU-1402。

发布顺序固定：

1. registry/config schema + adapter shadow，resolve 仍 legacy。
2. normalized v2 shadow persistence。
3. company_raw/dayu v2 reader shadow → active。
4. sidecar/future-root fixture active；Dropbox production 仍 shadow。
5. catalog migration dry-run → 获批 apply。
6. Dropbox resolver active，但 download 仍关闭。
7. SourceBundle/revenue source-preparation active。
8. latest discovery active。
9. 最后才启用获批 download。

每一步至少经过一轮完整 smoke、指标对账、错误预算检查和独立 go/no-go；不能在一个提交/窗口同时切 3、5、7、9。

### WU-1404：回滚与恢复演练

依赖：WU-1403。

- 回滚优先切 feature flag/reader，不删除 v2 数据、不逆向改真实文件。
- 保留 catalog backup 与 migration journal；验证在复制库恢复。
- 若 source-preparation 失败，可回退到旧显式 CLI，但不得静默改变语义或自动下载。
- 若 Dropbox 指标异常，禁用该 root 的 reusable/resolve route，generic index 可单独保留。
- 下载异常时只关闭 download_authorized path，不影响已有文件复用。

演练 ROLLBACK-01 schema reader；02 resolver；03 Dropbox route；04 bundle consumer；05 download writer。每个演练记录 RTO、数据差异和未完成请求处理。

### WU-1405：release manifest

依赖：WU-1404。

发布物记录三仓 commit、schema/adapter/profile/config/policy hash、migration ID、测试回执、known limitations、feature flags、rollback 命令、reviewer。任何仓 commit 变化使原 release manifest 失效。

### WU-1406：重构波次控制器与安全仪表盘

依赖：WU-1405。

- 把 R0~R11、CP0~CP8 与 root/consumer cohort 状态作为机器可读 release state；禁止只在 Markdown 手工勾选。
- 每次切换前验证依赖 receipt、backup、flag graph、error budget、canary、rollback command。
- 聚合 v1/v2 diff、legacy/bridge hits、candidate/rejection、external writes、latency、DB locks、incident。
- stop-the-line 条件自动阻止下一波次；人工 override 需用户明确授权、双 reviewer、原因和到期时间，且不能 override hash/path/external-write/integrity 安全门。
- 任一 flag 手工变化若没有 release/incident ID，config doctor 与 CI 失败。

测试 WAVE-01~08：跳波次、缺 receipt、stale backup、异常指标、未登记 flag、override 过期、breaker 失败、仪表盘数据缺失。

### Phase 14 放行门

- PR/nightly/cross-repo gates、12 个定向 mutation、五类回滚演练和 release manifest 均 accepted。
- 任何 feature flag 组合均通过 config dependency validator；生产默认值与发布阶段一致。
- WU-1406 能在八类错误状态下实际阻止波次推进，并能生成可审计 incident/rollback receipt。
- 尚未完成的真实 canary 必须在 release notes 中列为 blocker/limitation，不得隐去。

## Phase 15（硬编码清理、兼容退役与最终独立审计）— 状态：pending

### WU-1500：先禁用 legacy，保留源码观察

依赖：Phase 14 稳定发布。

- v1 scanner/resolver/protocol 默认 disabled，但源码和回滚 flag 保留。
- 连续两个完整验证周期内 legacy_hits=bridge_hits=0，v2 error budget/SLO/canary 均达标。
- 每周期末执行一次显式 v1 reader 回滚演练，证明旧读链仍可启动且不会误读 v2-only 状态。
- legacy freeze gate 禁止新产品 caller、新 bug fix 以外的功能、新配置语义。
- RF-11 accepted 后才允许 WU-1501；若出现 legacy hit，计时/周期从零开始并定位 caller。

### WU-1501：硬编码与死链清理

依赖：WU-1500。

只有满足 shadow/parity、回滚演练和至少两个连续发布验证周期后才可：

- 删除 scanner 中 legacy company_raw/dayu/Dropbox 分支。
- 删除 resolver 对 acquisition/dayu_meta 的读取。
- 删除 root-id/重点关注字面 focus 特例。
- 删除未被生产入口调用的重复 helper 或把其降为唯一入口内部函数。
- 删除跨仓重复 allowlist/config 解释。

静态 forbidden token 不是唯一证明；CodeGraph 必须显示 adapter-specific symbols 只被 registry/adapter 自身引用，resolver/admission/persister 无 source-specific edge。

清理必须拆成可独立 revert 的提交：scanner legacy、resolver/metadata bridge、跨仓 protocol/helper、配置/文档；每个提交后运行全仓+跨仓+RF-12，禁止一个巨型删除提交。

### WU-1502：legacy bridge 与 schema 退役

依赖：WU-1501。

- legacy_bridge_hits 在两个验证周期内为 0。
- 所有 active filing 都有 v2 assertion 或明确豁免/blocked receipt。
- N-1 compatibility 窗口按 ADR 满足。
- 备份恢复演练可读取历史数据。
- 退役只停止读取/写入，不清空历史 raw metadata；破坏性 purge 另立计划并需用户授权。

### WU-1503：文档一致性审计

依赖：WU-1502。

逐项检查三个 SKILL.md、README/docs、示例、配置注释、CLI help：

- 对 config-only 的描述限定为“采用已注册同构 adapter/profile 的新 root”。
- 明确 indexed 与 reusable/capture-ready 的区别。
- 明确外部 root 只读、canonical write store、download 授权。
- 明确 exact/latest、artifact invalidation、真实 canary 限制。
- executable docs tests 与 release manifest 当前版本一致。

### WU-1504：独立对抗复审

依赖：WU-1503。

reviewer 从零读取当前 HEAD、计划、回执和生产只读统计，不依赖作者口头总结，并执行：

1. 随机抽取每类至少 3 个测试，重跑并核对 spy budget。
2. 手工实施 12 个定向 mutation 中至少 6 个。
3. 新增一个未在 fixture 命名中出现的同构 root，只改配置完成 resolve/reuse。
4. 构造一个新 source layout，确认没有 adapter 时 fail closed，而不是错误宣称 config-only。
5. 检查真实根 before/after、catalog migration/reconciliation、retired 恢复事件。
6. 用 CodeGraph 检查生产 caller、硬编码、逆向依赖、死 helper。
7. 对真实 Dropbox canary 重跑；无合格样本则保持 blocker。
8. 搜索 skip/xfail、阈值变化、宽松异常捕获、测试内复制生产逻辑。

所有 P0/P1/P2 findings 均关闭并新增回归测试后才能 accepted；P3 必须登记 owner/期限/非阻断理由。

### WU-1505：最终 closure ledger

依赖：WU-1504。

每条历史问题记录：

- finding ID 与原证据。
- root cause 和修复 WU/commit。
- RED/GREEN/mutation/E2E/real canary ID。
- production observation。
- reviewer 与关闭决定。
- residual risk。

至少覆盖：

- Dropbox 配置已开但不可复用。
- scanner/root kind/focus 硬编码。
- resolver source-specific JSON。
- entity 推断依赖 company_raw。
- URL 错误广播。
- retired 终态与恢复治理。
- SourceBundle/processed artifact helper 未接主链。
- latest/gap 仅对可见 handle 生效。
- 伪 E2E 与手工技能拼接。

### Phase 15 放行门/项目最终完成门

- 所有 WU accepted，closure ledger 无未解释高风险项。
- 三仓完整测试与 cross-repo E2E 当前 HEAD 全绿，collection/coverage/threshold 不低于基线。
- 定向 mutation 12/12 被杀死。
- 迁移、回滚、真实只读探针和独立审计回执齐全。
- 若 WU-1303 未完成，整体只能标记 fixture_and_architecture_complete，不能标 production_dropbox_complete。
- 最终 tag/release manifest 之后再更新“问题已解决”的用户文档。

## 弱模型总执行协议

弱模型每次只领取一个 WU，严格执行以下清单；任何一步不确定即停止并提交 blocker，不得猜测：

1. 完整读取 task_plan.md、findings.md、progress.md 与该 WU 引用的 ADR；核对 plan_hash。
2. 检查依赖 WU 的 accepted receipt；缺一个即禁止开始。
3. 记录三仓 HEAD/status；发现非基线用户改动时避开，不能 reset/checkout/删除。
4. 只列出本 WU allowed_files、明确 forbidden_files 和预计 diff；超范围先申请计划修订。
5. 先运行当前 focused/repo 基线并保存 collection；基线失败先登记，不可顺手修无关问题。
6. 先添加或启用一个能精确证明需求的 RED；验证失败命中目标行为而非环境。
7. 由 reviewer 做 test-strength review：断言结果、路径、hash、状态和调用预算，不能只断言 exit=0/非空。
8. 冻结测试；实现阶段不得删除/放宽刚冻结断言。确需改 contract 必须退回 WU-2xx 和 plan revision。
9. 做最小实现，优先演进计划指定现有模块；禁止新建 temporary_v2/final_fix/helper2 平行链。
10. 每次只改一个职责；schema、adapter、resolver、migration、orchestration 不得在一个 WU 混合。
11. 运行 focused GREEN；失败只修本 WU，不能加 broad except、fallback、skip、sleep 或扩大 timeout 掩盖。
12. 运行仓库 GREEN，再按依赖运行其他两仓与 cross-repo GREEN；保存精确 node/计数。
13. 核对 git diff 与 allowlist；搜索 root 名硬编码、source-specific JSON、动态 import、外部写入。
14. 运行真实根/fixture before-after 探针与 network/download/parser/LLM/write spy 预算。
15. 执行该 WU 指定 mutation，证明测试会在错误实现上失败，然后完整恢复 mutation 并再绿。
16. 生成 WU JSON receipt；receipt validator 必须通过。
17. 独立 reviewer 重跑、查 diff、查调用图、给 findings；实现者不能自批 accepted。
18. 有 finding 时状态退回最早失效节点；修复后重复 11~17。
19. accepted 后只更新 progress/closure ledger，不提前勾选后续 WU。
20. 一个 WU 一个原子提交/回滚点；禁止把多个半成品一起提交。
21. 标明当前 R 波次、root/consumer cohort 与前后 flag；未登记波次禁止执行。
22. 机械搬移、行为修复、数据迁移、流量切换、legacy 删除必须是不同 WU/提交。
23. seam 提交只允许 v1 等价；如果顺手修 bug，退回拆分提交。
24. shadow 比较必须使用同一 immutable request/config/policy/catalog snapshot，不能先后读取变化中的状态。
25. 每一个 v1/v2 diff 必须归类为 expected_good parity、known-bad fix 或 blocker；禁止用比例阈值吞掉少数差异。
26. 新增 compat/bridge/flag 时同步登记 owner、metrics、最晚波次、删除 WU；缺一项不合并。
27. active v2 错误不得在同请求 silent fallback；应 fail closed、写 incident，再由 breaker/操作者切下一请求。
28. Phase 15/WU-1500 前不得删除 legacy 源码或不可逆迁移历史。
29. 一次只切一个 root 或一个 consumer；上一 cohort 未 accepted 不得扩大流量。
30. stop-the-line 触发后只做诊断、回退和 RED；不得继续下一 WU“看是否自己恢复”。

### 弱模型禁止动作

- 不得根据文件名、公司目录名或 root 名猜强身份/provenance。
- 不得让 unknown adapter/schema/status 自动 fallback。
- 不得把 indexed 当 reusable，把 fixture 当生产 canary，把 helper test 当跨仓 E2E。
- 不得修改真实 Dropbox/dayu 文件或 sidecar。
- 不得自动 restore retired，不得批量清空/重建生产 catalog。
- 不得降低测试数量、coverage、性能阈值或把失败标 skip/xfail。
- 不得复制一份旧逻辑到新模块长期双写。
- 不得把机械代码移动与 semantic behavior change 混在同一提交。
- 不得给 legacy v1 增加新 root/layout/consumer 功能。
- 不得以 silent fallback、宽松 diff 比例或自动数据反迁移掩盖 v2 缺陷。
- 不得在 legacy disabled 观察期完成前删除旧实现。
- 不得在无授权时下载，也不得为“最新”请求下载已覆盖期间。
- 不得以文档更新、CodeGraph 无结果或单一成功案例代替验收。

## 实施顺序与并行限制

- 关键路径：1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14 → 15。
- 波次映射：

| Phase | 主要重构波次 | 允许达到的最高状态 |
|---|---|---|
| 1 | R0 | 基线/characterization 冻结 |
| 2 | R0 | 契约和目标架构冻结，无实现 |
| 3 | R0/R1 基础 | policy、flag、breaker 可用，默认 v1 |
| 4 | R2/R3 基础 | v2 assertion 在 fixture/temp 可验证 |
| 5 | R1~R3 | seam 等价、pure shadow、temp persistence |
| 6 | R2~R5 | company_raw/dayu 逐 root shadow/candidate |
| 7 | R2~R4 | sidecar/future_root fixture 与真实只读 shadow |
| 8 | R6/R7 | resolver 逐 root 切换并成为 default |
| 9 | R5/R9 | 受控 backfill、restore、迁移/恢复演练 |
| 10 | R8 | company CLI→filing→revenue→技能逐 consumer |
| 11 | R8 | exact/latest/download 行为在 v2 闭环 |
| 12 | 全波次测试门 | RF-01~10 与跨进程 E2E |
| 13 | R6~R9 production canary | 真实只读/获批 canary |
| 14 | R6~R10 release | 分阶段放量、breaker、回滚 |
| 15 | R10/R11 | disabled soak 后分层删除 legacy |

- 可在契约冻结后有限并行：adapter conformance fixture 与 metadata schema tests；但 scanner 持久化必须等 schema owner 决定。
- 不可并行：同一模块的机械搬移与行为修复、migration 与 schema 变化、两个真实 root 的首次切换、resolver active 与未完成 parity、两个 consumer 的首次切换、bundle consumer 与未冻结 bundle contract、真实 canary 与未完成只读保护、legacy 删除与仍在运行的 rollback 窗口。
- 每个阶段只在放行门 accepted 后启动下一阶段；进度压力不是跳门理由。

## 保证边界

完成全部 mandatory WU、包括真实 WU-1303/1304 后，可以对本计划枚举的已知缺陷给出高置信关闭结论：来源硬编码、配置接入边界、Dropbox/多根复用、latest 补缺、处理工件复用、迁移治理、真实生产调用链与伪 E2E 均有代码、测试和生产证据闭环。

全面重构不会以 diff 大小或“尽量少改”为验收目标；验收目标是职责边界正确、旧行为有刻画、每个 seam 可逆、每个 root/consumer 独立切换、迁移可恢复、旧链最终可证明删除。若局部小改无法满足目标架构，允许扩大重构范围，但必须回到 Phase 2 更新蓝图/impact/plan hash，而不是在当前 WU 越界。

仍不能数学上保证“未来没有任何未知 bug”。本计划通过 characterization、strangler、统一 adapter conformance、future_root 配置案例、shadow diff、fault injection、breaker、对抗 mutation、独立复审、可观测性和 fail-closed，把未知问题的引入概率与发现时间显著降低。若真实 Dropbox 没有合格样本，架构与 fixture 可以完成，但不能声称真实生产 Dropbox 复用已经最终验收。

## Errors Encountered

| 日期 | 错误 | 尝试 | 处理 |
|---|---|---:|---|
| 2026-08-09 | 组合检索引用不存在的 README.md | 1 | 改用存在的 SKILL.md、源码与 CodeGraph；不重复原命令 |
| 2026-08-09 | 计划补丁中的反引号与 JavaScript 模板字符串冲突 | 1 | 补丁未应用；改用无反引号载荷 |
| 2026-08-09 | 计划补丁预期标题与文件实际标题不匹配 | 1 | 补丁未应用；以 UTF-8 读取精确标题后重试 |
| 2026-08-09 | 自审时将三个 rg 路径以逗号拼成一个不存在的路径 | 1 | 计数部分已成功；改为逐路径参数重新验证，不重复错误形式 |
| 2026-08-09 | 全面重构补充的大补丁与 Phase 6 实际上下文不完全一致 | 1 | 补丁未应用；读取精确区段，改用按 Phase 拆分的小补丁 |
| 2026-08-09 | 创建 runbook 的补丁含未转义 Markdown 反引号 | 1 | 补丁未执行；改用无反引号载荷 |
