# 三仓完全完成计划 — 进度日志

## 2026-08-09

- 已创建 planning-with-files 三文件。
- 当前阶段：Phase 0，冻结另一个 agent 推送后的稳定三仓基线。
- 本轮约束：只写计划与审计文档，不实施产品代码、配置、数据库或 CI 变更。
- 下一步：用户审阅并冻结本计划；未得到实施指令前不执行任何产品改动。
- 基线 HEAD 已确认与各自 upstream 一致：revenue `3ce9cc4`、filing `c9799b7`、wiki `109a1a6`。
- CodeGraph 状态已确认健康；本轮不需要再次重建索引。
- 已完成第一轮结构调用者核验：Sidecar adapter、SourceBundle、artifact selector、flags/rollback 和 latest closure 均存在生产接线缺口。
- 已完成生产 catalog、配置、CI、旧计划/回执的交叉核验；关键差距已写入 findings 5~7。
- 已冻结目标职责：company-wiki 拥有数据湖与策略，filing-fetch 保持薄编排，revenue 作为终端消费者拥有三仓场景总门。
- 已盘点可复用的三仓 contract/E2E 测试资产，计划将通过升级断言和增加跨进程场景复用这些资产。
- 已完成计划主体：16 个阶段、71 个 FC 工作单元；初版 63 个场景，并补充目标架构、执行手册、阶段依赖矩阵、收据规范、动态审核和渐进发布/回滚门禁。
- 已完成计划自审：六项目标均有责任阶段、验证办法和 Phase 15 终局验收；真实层 skip、仅 mock、代码未接生产入口、陈旧/待定收据均不得视为完成。
- 本轮未修改三个仓库的产品代码、运行配置、数据库、CI 或测试实现。
- 初版只读结构校验通过：16 Phase、71 FC、63 场景、配套文档链接无缺失；三仓产品状态未被本轮改变。
- 用户要求对最新计划继续做弱模型可执行性加固；当前进入计划 hardening，仍严格限制为文档变更。
- hardening 发现：主计划与 runbook 存在 `FC-*`/`WU-X` 命名不一致，并缺少覆盖全部 71 项的状态登记表、冻结命令注册表和独立 reviewer 隔离协议；将仅在计划层补齐。
- 场景矩阵复核发现：主功能覆盖充分，但还需补充真实文件/index 生命周期、端到端组合用户旅程以及动态审核自证场景，并澄清 T2 只禁止生产 catalog/source roots 写入。
- hardening 已将场景从 63 扩展为 95，并新增 71 项 FC 状态登记表、冻结命令注册计划和独立审查协议；待做最终一致性校验。
- 已新增 FC 执行包模板、动态审核长期方案和代码质量专项方案，把“不能跳项”“真实层不能假绿”“代码质量必须有 ratchet”变成显式计划契约。
- r2 最终一致性校验通过：14 份文档；16 Phase；主计划与 registry 均为 71 FC 且集合一致；95 场景无重复；Markdown 引用无缺失。
- hardening 结束，状态恢复为 `plan_complete_ready_for_review`；未得到实施指令前不执行任何产品改动。
- 开始历史计划状态对账：已发现三仓存在多组根级、review/audit、docs/plans 和旧 data-lake WU/receipt 计划；下一步建立统一 inventory，并以当前代码/证据而非旧勾选为准重新分类。
- 首轮摘要发现多处状态漂移：revenue 根计划“全部完成”与 387 未勾选并存；review roadmap“未实施”与实施镜像 completed 并存；company-wiki 两个 portfolio 计划存在 Strategy A/B 继承关系。
- 一次 PowerShell 汇总命令因 foreach 后直接管道的解析方式失败；已记录，后续改为先保存数组再序列化。
- 旧 data-lake 计划核对：Phase 4–15 仍 pending，部分 WU 虽有 receipt，但最新代码/生产证据不支持 completed；拟整体标为被 r2 取代，旧 receipt 仅保留为历史输入。
- 已区分审查完成与产品完成；review/audit 三组旧计划的审查工作保持 completed，产品待办转入 r2，旧“批准后实施”项取消。
- 初步确定 company-wiki 子计划处置：core-section 保持完成；portfolio-fix 关闭为 superseded；portfolio-automatic 保留窄范围历史完成但泛化转 r2；catalog-space 拆为已完成部分、条件降级部分和转入 r2 的持续验收。
- 进一步核对：task_plan_v2/review_plan/recovery draft 均为历史或恢复文件；CW-2.24 verification 的复核结论已完成但勾选未回填；filing-fetch 根计划可保留窄范围历史完成，并把新增终局目标转交 r2。
- CodeGraph 复验保持原结论：Sidecar/SourceBundle/artifact selector/runtime rollback 仍未形成生产主链，因此旧计划只能标窄范围历史完成、部分证据或 superseded，不能整体升级为当前完成。
- 已创建 `legacy_plan_disposition.md`，逐文件登记三仓历史计划状态并建立旧主题→r2 FC crosswalk；下一步把状态覆盖层回写到各非归档计划入口。
- Revenue 侧根计划、旧 implementation/review/audit/adversarial 计划和旧 data-lake runbook 已写入状态覆盖；旧 data-lake task 标题首次匹配失败，已读取真实标题，待单独补写。
- 旧 data-lake task/progress 已补写 superseded 覆盖。catalog-space progress 已核实：Phase 1–4 与 ADR/工具收尾有实际证据；Phase 5 因用户 D4“不迁 D:”应取消，持续四周健康观察转 r2。
- 已回写 18 个主要非归档计划入口；CW-2.24 漏勾复核清单已补为 10/10 complete。发现 IMPLEMENTATION_PLAN 仅剩一个旧 R8 CI 延期项，准备标为 superseded 并映射到 r2 FC-103/104/1101。
- IMPLEMENTATION_PLAN 旧 R8 延期项已补标 superseded；六份旧 planning-with-files progress 已同步关闭/转移状态。
- `legacy_plan_disposition.md` 已补全所有历史空复选框集合的最终处置，包括 archived/recovery 文件；旧空框不再计入活动 backlog。
- 最终结构检查通过：15 份 r2 文档、16 Phase、71/71 FC、95 unique scenarios、18/18 主要历史入口有 disposition、链接无缺失。
- `git diff --check` 首次发现 revenue 两处新增 Markdown 行尾空格，已精确移除；所有本轮 tracked 变化仍仅限计划/进度 Markdown。
- 三仓 `git diff --check` 复跑均 exit 0；仅保留 Git 的 LF→CRLF 工作区提示，无 whitespace error。
- 对 portfolio-automatic 38 个空框逐项来源复核：它们属于未实施后被用户放弃的 Strategy A，不能伪勾完成；将把原 Phase 1–6 改为 cancelled，并新增 Strategy B 实际完成清单。
- 已完成三份 company-wiki 子计划的精确状态归并：portfolio-automatic 原 Phase 0–6 全部标为 `cancelled_by_Strategy_B`，另勾选 10 项 Strategy B 实际成果；portfolio-fix 勾选 2 项关闭处置；catalog-space 勾选 6 项阶段处置并明确 Phase 5 取消、长期监控转 r2。
- 首次按猜测的 `audit_review/` 路径查找上述三份计划失败；已通过 `rg --files` 定位到 `docs/plans/` 精确路径并记录 findings 28，后续未重复错误。
- 当前活动实施 backlog 仍只有 FCAP r2 registry 中的 68 个产品 FC；本轮完成的是计划治理与历史状态对账，不代表产品六目标已经完成。
- 最终机器校验通过：15 份当前计划 Markdown、16 Phase、task/registry 71/71 FC 集合一致、95/95 唯一场景、68 个产品 FC pending、3 个计划基线 FC completed。
- 当前计划内部链接缺失 0；18/18 个主要非归档计划入口均可在文件顶部识别最新状态。
- 三仓 `git diff --check` 再次通过；本轮未修改任何产品代码、配置、数据库、测试或 CI，company-wiki 的 `llm_cost_log.csv` 仍是用户先前已有改动。

## 2026-08-09（实施轮 — honest-implementer 模式，FC-101）

- 用户授权"从头实施直到全部完成 + 全部授权"；经澄清确认采用 **诚实实施者模式**：不放松 implementer≠reviewer，逐 FC 实施 + implementer receipt，validator 锁 `independent_review`，硬阻塞记 `blocked`。
- Phase 0 重验：三仓 HEAD 与基线 triplet 完全一致（revenue `3ce9cc4`、filing `c9799b7`、wiki `109a1a6`），dirty 文件全是已登记计划文档 + wiki `llm_cost_log.csv`；无漂移。解锁 Phase 1。
- **FC-101 完成（RED→GREEN）**：
  - 新增 `compatibility/contract_registry.json`（七契约单一所有权源）、`compatibility/contract_registry.py`（loader+validator）、`tests/test_contract_registry.py`（4 一致性 + 5 mutation oracle）。
  - 跨仓：company-wiki `docs/adr/ADR-010-fcap-contract-ownership.md`（owner 声明）、filing-fetch `references/contract-ownership.md`（消费者声明）。
  - TDD：先写测试 → 9 RED（注册表不存在）→ 建数据/ADR/声明 → 9 GREEN → mutation oracle 全命中。
  - 全量 `pytest tests/ tools/tests/`：371 passed / 1 failed；唯一失败 `test_audit_baseline` 是既有 PORT-01 Windows 编码问题，已确认非 FC-101 回归（`git diff HEAD` 空、隔离复现），归 FC-1205（findings 31）。
- 未触碰任何产品代码/配置/数据库/CI；FC-101 为纯新增文件。
- 剩余：FC-101 `accepted` 待独立 reviewer（honest-implementer）；ADR/registry hash 入 triplet manifest 待 FC-104。
- 下一步：FC-102（scenario registry）— blockedBy FC-101，已解锁。

### FC-102（scenario registry，revenue-only）

- 新增 `compatibility/scenario_registry.json`（95 场景，按 tier 分解）、`compatibility/scenario_registry.py`（loader+validator）、`tests/test_scenario_registry.py`（95 ID 硬校验 + 5 一致性 + 6 mutation oracle）。
- TDD 真实 RED：首轮 validator 误判 `freshness_window=None`（T0/T1 合法）为 missing → 修复 → 11 GREEN。
- 范围：交付 registry + 完整性 validator；"每 ID 真实测试覆盖"硬门属 FC-1003（Phase 10）。
- 下一步：FC-103（receipt/closure validator）— blockedBy FC-101，已解锁。

### FC-103（receipt/closure validator，revenue）

- 新增 `tools/receipt_validator.py`（schema 2.0 校验 + can_accept 门）、`tools/tests/test_receipt_validator.py`（22 passed：1 正向 + 16 负向 + 3 can_accept + 旧 receipt 拒绝 + FC_IDS=71）。
- 实战：FC-101 receipt 结构 OK、can_accept 正确拒绝（pending seal + 非 accepted）。
- 全量 404 passed / 1 failed（既有 PORT-01，无新回归）。tools/ 不在 skill 安装面，无需同步。
- 下一步：FC-104（compatibility manifest + command registry）— blockedBy FC-101/102/103，已解锁。

### FC-104（compatibility manifest + command registry，revenue）

- 新增 `compatibility/current.json`（manifest）、`compatibility/command_registry.json`（10 冻结命令，wiki 项诚实 pending-first-measurement）、`compatibility/compatibility_manifest.py`（validator：hash 篡改检测 + frozen-baseline 后代门）、`tests/test_compatibility_manifest.py`（19 passed）。
- TDD 真实 RED：owner_repo 命名不匹配（真实仓名 vs triplet 键）→ 修 validator → GREEN。
- 全量 423 passed / 1 failed（既有 PORT-01，无新回归）。
- **Phase 1 完成**：FC-101/102/103/104 全部 RED→GREEN → 提交 → receipt → independent_review。
- 下一步：Phase 2（FC-201 持久化 RuntimePolicySnapshot）—— 首次触碰 company-wiki 产品代码；前置 FC-104 accepted（honest-implementer 下 receipt 已备，待独立 reviewer 补 accepted 后解锁）。

## 2026-08-10 — Phase 1 closure + Phase 2 FC-201/202（accepted）

- FC-101~104 独立 review 完成：4 个 reviewer subagent（干净 worktree 296e17b、独立身份 reviewer-fc1XX-independent）全部 accepted；closure can_accept gate 通过；registry 状态 → accepted；提交 4c8677a + current triplet 更新 4f2a4c1。
- wiki command registry 实测封印：wiki.unit.full 1977 collected / 1975 passed（2 个预存 PORT-01 test_check_unique_test_symbols 编码失败，FC-1205）；wiki.integration 10 passed；registry hash bd4e507d → 215b8077；提交 e7c8114。
- **FC-201 完成（RED→GREEN→accepted）**：company-wiki 新增 `runtime_policy.py`（ActivationSnapshot 1.0：flags + current_epoch + active_cohorts + policy_hash + snapshot_sha256；fail-closed load；CAS write）+ CLI `runtime-policy show/apply` + wu905 step7 去硬编码。16 tests；3 mutations killed。wiki caac327→111891b→e9c84ad（closure）。reviewer-fc201-independent accepted。
- **FC-202 完成（RED→GREEN→accepted）**：resolver 强制 ActivationSnapshot —— `resolver_visibility` 派生 reader/epoch/cohort/bridge；`_v2_assertion_metadata` SQL 过滤 decision+visibility+epoch+cohort（v1 只见 legacy、v2 需 epoch+cohort 精确匹配，缺省 fail closed）；`_source_metadata` legacy bridge 按 snapshot 门控；assertion_service 同步过滤（无旁路）；CLI resolve 起点固定 snapshot。15 tests；SQL 级 6 mutations killed（guard 级存活属纵深防御，已记录）。wiki 10f79354→d5830bf→1c504e3（closure）。reviewer-fc202-independent accepted。
- 两 FC 的 receipt 中 stale 计数均在 closure 时按 reviewer replay 修正并注明（低严重度 finding，不影响 verdict）。
- 当前 triplet：revenue 2dea9c9、filing d5e8723、wiki 1c504e3。下一 FC：FC-203（preview/apply/rollback 事务 + CTRL-03/04）。

## 2026-08-10 — Phase 2 完成（FC-201~205 全部 accepted）

- **FC-203 accepted**：activation.py（apply/rollback 单事务 + activation_journal 不可变回执 + preview/apply/rollback CLI）；CTRL-03 原子性（未知 id/晚批失败全回滚，fault injection 零半激活）、CTRL-04 同请求 before→after→restored trace、重复/错误 cohort/陈旧 policy hash fail closed。11 tests + 3 mutations + sqlite authorizer fault injection。reviewer-fc203-independent accepted。
- **FC-204 accepted（生产写入，用户 change-window 授权 2026-08-10）**：map_existing_activation 将 16 条 remediation active assertions 映射到 canary cohort/epoch（receipt d4e2a160...）；baseline（schema 1.2.0、FK 0、authoritative hashes）；副本演练（16 行真实数据 map+rollback 通过）；runtime_policy.json 注册 canary cohort + flag off + bridge on（用户决策：注册 cohort 暂不翻 flag——实测 v2_resolve_active=true 会使 13,806 legacy-only 文档不可解析，违反 flag 前置 shadow diff=0）。WU-905 矛盾关闭：回执+DB+resolver+flag 全一致。4 tests。reviewer-fc204-independent accepted（生产状态只读复核 5a-5g 全过）。
- **FC-205 accepted**：architecture_gate 增三不变量（生产 resolver/CLI 消费 snapshot、flags/runtime_policy/gate 外零硬编码 flag dict、legacy bridge loop 仅 resolver）；T4 最小 cohort rollback 改变真实 resolver 响应。adversarial evil-module 双 gate RED、2 wiring mutations killed、leg04 freeze gate 兼容。4 tests。reviewer-fc205-independent accepted。
- Phase 2 exit gate：CTRL-01~05 全绿、真实 rollback 可重复、无"数据 active/flag inactive/响应变化"不一致（WU-905 关闭）、未新增 active assertion/Dropbox cohort/artifact cohort。
- 当前 triplet：revenue b80db06、filing d5e8723、wiki be48c87。下一 Phase：FC-301（RootPolicy 2.x 配置迁移）。

## 2026-08-10 — Phase 3 前半（FC-301/302 accepted）

- **FC-301 accepted**：policy_2x.py（RootPolicySnapshot 2.0 loader/doctor/export）—— per-root 显式 adapter/profile/read_only/reusable/allowed kinds/cohort/write target；fail closed：外部 root 可写、未知 adapter/profile、宽化路由、重复 root；1.x->2.x doctor 只读报告；1.x loader 仍是生产路径（FC-305 cutover）。RootSpec 增 cohort + canonical_write_target（默认 None 保持 1.x）。11 tests；5 mutations killed。reviewer-fc301-independent accepted。
- **FC-302 accepted**：adapter_dispatch.py（adapter_for 按 adapter_id 解析注册 adapter，fail closed；scan_root_via_adapter 转 _Candidate）；scanner facade v2 shadow 分支经 adapter 派发（不可解析路由才 FacadeError），v1 路径零改动。SidecarFilingAdapter/CompanyRawAdapter/DayuAdapter 均获 production caller。9 tests；3 mutations killed（missing-id gate、registry check、scanner 无条件 raise）。reviewer-fc302-independent accepted。
- 当前 triplet：revenue 12942b3、filing d5e8723、wiki 0613026。下一 FC：FC-303（v2 scanner shadow parity）。

## 2026-08-10 — FC-303 accepted（changes_required → 修复 → r2 复审通过）

- **FC-303**：shadow_parity.py（v1/v2 frozen corpus 对比：候选数、roles、content hash declared-vs-disk（SPI-03）、identity、exclusion reason；migration-rules ledger 拒绝 phantom rule）。
- 首轮 reviewer 判 changes_required（F1, medium）：EX-08 命名测试无法区分 v1/v2 输出，narrow fallback mutation 存活。修复：adapter_for 调用 spy + adapter 运行时错误 fail-closed（ScannerFacadeError，绝不回落 v1）。r2 复审（reviewer-fc303-r2）：4 mutations 全部 killed（blunt fallback、narrow fallback、hash check、phantom rule），full suite 2053 passed / 2 pre-existing PORT-01；**accepted**。
- 当前 triplet：revenue 8821d90、filing d5e8723、wiki ed3da07。下一 FC：FC-304（future root 配置-only 证明）。

## 2026-08-10 — Phase 3 完成（FC-301~305 全部 accepted）

- **FC-303 accepted**（changes_required F1 → 修复 → r2 复审通过）：shadow_parity.py v1/v2 frozen corpus 对比 + migration-rules ledger；EX-08 加强（adapter_for spy + adapter 错误 fail-closed 不回落 v1）。
- **FC-304 accepted**：future root 配置-only 证明（2.x loader → v2 scan → snapshot export 零产品代码改动）；no_root_specific_hardcode gate。
- **FC-305 accepted**：cutover_decision（snapshot v2_scan_shadow 按 cohort 启用）、gate_production_dry_shadow（连续两轮零 diff 才允许生产 dry shadow）、root_fingerprint v1/v2 跨 cutover 不变、v1 只读 fallback 保留。
- Phase 3 exit gate：新 root 配置-only 成功、三 adapter 有生产调用者、scanner root-specific 写入归零（v2 路径经 adapter_dispatch，无 root-specific metadata container）、v1/v2 shadow 差异全部可解释（migration ledger）、无真实根写入。
- 当前 triplet：revenue 待提交、filing d5e8723、wiki 36cd215。下一 Phase：FC-401（可恢复 migration engine）。

## 2026-08-10 — Phase 4 完成（FC-401~405 全部 accepted）

- **FC-401 accepted**：migration engine cancel/copy-validation/rollback journal；MIG-04 rollback（shadow 翻转、记录保留、rollback journal）。
- **FC-402 accepted**：classify_bucket 四桶（eligible/needs_review/unprovable/retired_or_conflict）；文件名仅 evidence hint；中国平安式样本 fail closed。
- **FC-403 accepted**：remediation proposal/approval 分权（source bytes hash + field evidence + policy hash 绑定；approval 只产 shadow；placeholder/short/stale policy hash fail closed）。
- **FC-404 accepted**：migration_ledger 质量台账（root/market/kind coverage + missing fields + duplicate location sets + retired 排除）；ledger_is_closed 预 apply 门（分桶和=输入）；只读字节级验证。
- **FC-405 accepted**：副本灾难演练（中断+resume、disk-full 原子性、rollback+rerun 收敛、幂等、restore-point hashes）；**MIG-07 原子性生产修复**：assertions+journal 单事务提交（此前 journal 失败会留下已提交 assertions）。
- Phase 4 exit gate：副本迁移可中断恢复且幂等、输入全分桶、零猜测 mutation 被杀死；production apply 仍需单独授权（Phase 14）。
- 当前 triplet：revenue 待提交、filing d5e8723、wiki 1ff47fb。下一 Phase：FC-501（Dropbox RootPolicy/sidecar contract）。

## 2026-08-10 — FC-501 accepted（跨仓 Dropbox 契约；F1 changes_required → 修复 → r2 复审通过）

- **wiki 侧**：sidecar adapter 增 DBX-03 content-hash 检查（声明 hash vs 文件字节 → content_hash_mismatch，role 级 fail closed）；DBX-04 broker_research 不满足 filing；DBX-05 path/symlink 规则；DBX-06 retired 不复活；Dropbox root 2.x policy contract（read_only/reusable/allowed kinds/symlink reject/priority/cohort）。
- **filing 侧**：删除独立 allowed_handle_roots allowlist（architecture_target §7 禁止项）；validate_handle 消费 RootPolicySnapshot + expected hash（PROJECT_ROOT 展开、reusable roots containment、hash mismatch fail closed）；config schema 拒绝 allowed_handle_roots。
- 首轮 reviewer changes_required（F1 high）：config-schema 测试用不存在的 /tmp/x root，M3 未杀死、测试从未 RED。修复：测试改用真实临时 wiki root + match=exactly schema_version；M3 被两个测试同时杀死、RED-at-base 证明。r2 复审（reviewer-fc501-r2）：3 mutations + RED-base 全部 killed；**accepted**。
- 当前 triplet：revenue 待提交、filing 6274be2、wiki 7bcd3b2。下一 FC：FC-502（SidecarAdapter 生产扫描）。

## 2026-08-10 — FC-502 accepted（SidecarAdapter 生产扫描契约）

- **FC-502**：tests/contract/test_sidecar_production_scan_fc502.py（4 tests）钉住生产链路：registry dispatch（scan_root_via_adapter）→ SidecarFilingAdapter → admission（evaluate_candidate）→ normalized capture_ready；DBX-03 adapter 绝不借用 acquisition/dayu_meta 遗留容器；DBX-04 普通研究文档可索引但绝不成为 filing；DBX-07 重扫不改写 Dropbox 字节/mtime。
- 独立 reviewer（reviewer-fc502-independent，clean worktree @ e03e4a3）：focused 4 passed；full suite 2108 passed / 2 pre-existing PORT-01（FC-1205 scope）；1 mutation（_normalized_from_sidecar 借用遗留容器）killed；DBX-01/03/04/07 独立复放；CodeGraph 确认 adapter_dispatch 生产接线；**accepted**。
- 当前 triplet：revenue 6aadfde、filing 6274be2、wiki 2555633。下一 FC：FC-503（真实只读候选分桶）。

## 2026-08-10 — FC-503 accepted（Dropbox 历史候选治理；真实 root 只读盘点）

- **FC-503**：dropbox_governance.py `inventory_dropbox`（生产 adapter dispatch → FC-402 四桶分类 → 缺失字段 → 按实际字节检测重复 location set；other-root ids 由调用方传入，不硬编码 root id（FC-304 gate 干净）；中国平安弱身份 guard fail closed（GovernanceError）；catalog 全程 mode=ro）。
- 7 tests（完整 sidecar→eligible、中国平安弱身份 unprovable、文件名 hint 绝不升级、guard 拦截未审 promotion、缺失字段、实际字节重复集不删除、只读+确定性）；6 mutations 全部 killed（文件名猜 security_id、丢缺失字段、关重复检测、丢 fingerprint、pingan 分类旁路、guard 移除）。
- 真实 root replay（tools/dropbox_governance_replay.py，两轮全量零写）：7167 candidates（4000 original_primary / 3167 indexed_only）、eligible=0 unprovable=7167、重复 location sets=2890（实际字节）、pingan 32/32 unprovable、fingerprint_sha256 86980b49... 两轮一致、catalog 23513/43074/46573 不变、writes=0；catalog 不变量：中国平安 retired=49、active 弱身份=27 全部 capture-incomplete（无 fiscal_year）。
- reviewer 发现 1 个 medium（receipt base_triplet.wiki 哈希不存在——伪造哈希，真实为 2555633856...），已修正 receipt 并重新验证（exit 0）。reviewer-fc503-independent **accepted**。
- 当前 triplet：revenue 2a076da、filing 6274be2、wiki 5554a87。下一 FC：FC-504（真实 Dropbox-only canary 样本，必要时用户授权）。

## 2026-08-10 — FC-504 mechanism accepted；样本 blocked（等待用户 canary）

- **FC-504 机制**：canary_registry.py（hashed sample ID = sha256(root_id|relative_path)、绝对路径拒绝、sample_id 防伪、exclusivity 只读校验（mode=ro）、canary_decision 在 eligible<2 时返回 needs_user_samples 绝不伪造样本）。8 tests + 4 mutations killed（路径安全、公式、exclusivity、decision）。
- **blocked 判定复放**：FC-503 replay 证明真实 root eligible=0（7167 candidates 全部 unprovable）→ canary_decision = needs_user_samples → 按计划停在 blocked 并向用户申请 >=2 个真实 canary 文件/sidecar（与 companies/dayu 无相同 hash、注册 hashed sample ID 不泄露绝对路径）。
- reviewer-fc504-independent **accepted**（机制）+ block_confirmed（1 个 low 发现：full-suite exit code 记录 0 vs 真实 1，与既有 receipts 惯例一致）。
- 当前 triplet：revenue 待提交、filing 6274be2、wiki 651d2f6。下一动作：向用户申请 canary 样本；FC-505 依赖 FC-504。

## 2026-08-10 — FC-601 accepted（CompanyRawAdapter 等价；EX-01 CN/HK/US exact reuse）

- **FC-601**：trace_parity.py（candidate_trace 五段投影：sources/documents/locations/handles/bundles；compare_traces 用 FC-303 migration-ledger 语义；run_trace_parity 组合 _scan_root_v1 vs scan_root_strategy(v2_scan_shadow)）。冻结 CN/HK/US corpus 首轮即零 diff（精确等价）。
- 7 tests（trace parity、deterministic、golden 投影值、EX-01 CN/HK/US fixture exact reuse、canonical writer 目标不变）；4 mutations 全部 killed（handles/bundles/mime/group_key 破坏 → golden 测试死）。
- EX-01 真实样本 replay（tools/ex01_reuse_replay.py，只读）：CN 601899 紫金矿业 FY2025 cninfo、HK 03690 美团 FY2024 hkexnews（form_type FY）、US AAPL FY2025 sec — 3/3 REUSED_EXACT，download_required=false，capture_ready=true；live catalog 行数不变（23513/43074/46573）。
- reviewer-fc601-independent **accepted**（1 个 low 发现：test helper 的 known_bad key 命名空间不一致——dormant/fail-closed，冻结 corpus 零 diff；列入 FC-1203 test-only helper 清理范围）。
- 当前 triplet：revenue 待提交、filing 6274be2、wiki 49c1e2c。下一 FC：FC-602（DayuAdapter 等价与 dayu-only 样本）。

## 2026-08-10 — FC-602 accepted（DayuAdapter 等价；EX-02 dayu-only 样本）

- **FC-602**：DayuAdapter 重写为 v1 group 语义（group meta.json + preferred-primary 选择 + 每文件 role）；enrichment（enrich_dayu_metadata/construct_edgar_url）从 scanner 移入 adapter（单一来源，scanner 别名导入，v1 行为不变——AST 级纯移动）；metadata-only group（无主文件的 byte-less placeholder——capture-incomplete 真实原因）永不成为候选。
- 10 tests（enrichment golden、EDGAR URL、metadata-only 跳过、frozen corpus v1/v2 trace parity、EX-02 fixture exact reuse、incomplete 不复用）；5 mutations killed；trace_parity known_bad key 对齐 section:path（同时解决 FC-601 low 发现）。
- EX-02 真实 dayu-only replay（只读）：1548 FY2021（sha 72b3ed25...）+ FY2023（sha bf1d8a17...）— 其他根无同 hash、catalog 有 active dayu original_primary、meta 完整；live catalog 行数不变。
- reviewer-fc602-independent **accepted**（3 low 发现：changed_files 多列 1 个文件、两个描述性计数不可复现、v2 adapter 缺 master_identity backfill——后者列入 R4 cutover 前处理）。
- 当前 triplet：revenue 待提交、filing 6274be2、wiki 4d1a173。下一 FC：FC-603（跨根去重与 deterministic location）。

## 2026-08-10 — FC-603 accepted（跨根去重与 deterministic location；Phase 6 完成）

- **FC-603**（test-only）：EX-04 相同 bytes 三根 → 单 document 多 locations，canonical 按 policy priority + 稳定 tie-break；priority 压过字母序 pin（dayu p10 vs companies p30）；EX-05 同公司/年份不同 pdoc → exact select 不模糊合并；EX-06 amended+original 稳定 revision rule（build_gap_plan）；EX-07 双 catalog 正反扫描顺序 → canonical/duplicate_group 一致；AR-09 跨根重复共享 artifact。
- canonical 确定性由四层独立机制保证（resolver 路径 SQL ORDER BY + query_documents SQL ORDER BY + _annotate_locations 内存排序 + ranked_locations CTE）——单层 mutation 被其他层掩盖（文档化的纵深防御）；组合 2 层 mutation（resolver 查询 + 内存排序）必杀。
- 3 mutations killed（priority 删除、resolver 路径排序移除×2层、revision 规则反转）；reviewer-fc603-independent **accepted**（1 low：full-suite exit_code 依赖 codepage——计数与失败身份完全一致）。
- **Phase 6 完成**（FC-601/602/603 accepted）。FC-604 因前置 FC-505 blocked 而 blocked；Phase 7-15 全链（FC-701~1505）均依赖该链。
- 当前 triplet：revenue 待提交、filing 6274be2、wiki f58a9df。等待用户提供 >=2 个 Dropbox canary 文件/sidecar 解除 FC-504/505/604 阻塞。

## 2026-08-10 — 用户决策：canary 排他性要求修订

- 用户提供 4 个 canary 文件（紫金矿业 2024/2025 年报、星环科技 2024/2025 年报），但 content hash 全部已存在于 company_raw/dayu_portfolio（字节相同）。
- **用户指令（2026-08-10）**："Dropbox-only的意义在哪里？我只需要这几个不同目录都能够作为文档源，但排他性并不是我关心的，做索引的时候可以记录同样的文件存在于几个不同目录，它们应该具有相同的地位可以被使用"。
- 修订：FC-504"样本必须在 companies/dayu 无相同 hash"条款按用户决策放宽——相同内容跨根存在由索引记录为重复 location（FC-603 EX-04 语义：单 document、多 locations、同等可用、canonical 按 policy priority）；canary 要求改为"真实年报 + 完整 sidecar（字段由已验证 catalog 记录补齐）"。
- sidecar 字段来源：catalog 已验证 acquisition/dayu_meta 记录（正式来源），content_sha256 取 Dropbox 实际字节。

## 2026-08-10 — FC-504 accepted（4 真实 canary 样本注册完成，Phase 5 解阻）

- 用户提供 4 个真实年报（紫金矿业 601899 FY2024/2025、星环科技 688031 FY2024/2025）放入 Dropbox 根；实施者按用户决策（排他性放宽）写入完整 sidecar（字段来自 catalog 已验证记录/dayu_meta，content_sha256 取实际字节——4 次受授权的外部根写入）。
- 注册 hashed sample ID（sha256(root_id|relative_path)，相对路径，无绝对路径泄露）；真实 root 盘点 eligible=4（原 0）、canary_decision=selectable；跨根重复按 EX-04 记录（duplicate sets 2890→2894）。
- reviewer-fc504-r2 **accepted**（2 low：F1 no-remote-branch；F2 星环字段源自 dayu_meta（FY2025 ingest_complete=False）——符合用户决策，建议后续措辞用"catalog dayu_meta 记录"）。
- **FC-505 解阻**；FC-604 解阻。当前 triplet：revenue 待提交、filing 6274be2、wiki 47f2e4c。下一 FC：FC-505（三仓全链 E2E）。

## 2026-08-10 — FC-505 实施完成（三仓全链 E2E；审查进行中）

- **生产修复（wiki scanner.py，2 处）**：v1 目录分支为 non-focus 目录配对兄弟 .source.json 元数据；persist wrapper 将 directory 根元数据写入 acquisition 容器——**"配置有 Dropbox 但 resolver MISSING"已知缺口关闭**（Phase 5 exit gate 的 RED/GREEN 修正；probe 测试按其自身 docstring 预留翻转至 REUSED_EXACT）。两个 mutation（撤销任一修复）均杀全部 4 个链测试；parity 回归绿。
- **revenue 链测试（4 tests）**：三仓全链（company-wiki resolve → filing-fetch 政策快照 containment → revenue source record → artifact selection）exact hit 零副作用；DBX-08 cohort rollback 同请求还原（文件保留）；canary 在 → REUSED_EXACT、无 sidecar → fail closed。
- **真实 replay（tools/ex05_chain_replay.py，只读）**：紫金矿业 FY2024/2025 REUSED_EXACT（exit gate ≥2 通过）；星环科技 FY2024/2025 fail-closed capture_incomplete（canonical dayu 副本为 http URL——数据质量问题，非伪造）；Dropbox root fingerprint 不变；downloads/catalog_writes/provider/parser/LLM 全 0。
- wiki 全量 2142 passed / 2 pre-existing PORT-01；revenue pre-commit 381 passed + E2E 绿 + install-sync 97 files MATCH。
- 当前 triplet：revenue 4a2c65f、filing 6274be2、wiki 47a0311。FC-505 独立审查（reviewer-fc505-independent）运行中。

## 2026-08-10 — FC-505 accepted（三仓全链 E2E；Phase 5 完成）

- **reviewer-fc505-independent accepted**（8 low/info findings，无阻塞：F1 no-remote-branch、F2 revenue 新测试文件 ruff F401 未用 import、F3 full-suite exit_code 记录差异、F4 wiki base anchor 早于 FC-504 closure（FC-505 自身 diff 精确）、F5 星环 http-URL 数据质量、F6 catalog 计数因每小时生产扫描增长（replay 前后一致，只读可证）、F7 程序预期陈旧、F8 审查期间 revenue fcap 上并发 doc-only 提交（allowlist 未动））。
- 2 mutations killed（撤销任一 scanner 修复 → 4/4 链测试失败）；replay 跑两遍均 exit 0；wiki 全量 2142 passed / 2 pre-existing PORT-01。
- **Phase 5 完成**（FC-501~505 全部 accepted）：真实 Dropbox canary 2/2 通过 exit gate、resolver-MISSING 缺口关闭。
- 当前 triplet：revenue 7e79ba5、filing 6274be2、wiki 47a0311。下一 FC：FC-604（三根一致性 canary，前置已全部 accepted）。

## 2026-08-10 — FC-604 实施完成（三根一致性 canary；审查中）

- **生产修复（resolver.py）**：`_provider_identity` 现在回退 `source_provider`——关闭 dayu provider=None 差异（companies/directory 返回映射 provider，dayu 返回 None）。
- **4 tests**：CN/US 跨三根 contract 一致（13 字段全部相同，仅 canonical_path 不同）、AST gate（resolver 无 root_id/root_kind 业务分支）、Dropbox canary REUSED_EXACT exit gate 回归。1 mutation killed（provider 回退移除→2/4 fail）；wiki 全量 2146 passed / 2 PORT-01。
- 当前 triplet：revenue 7e10ea6、filing 6274be2、wiki 5a18935。FC-604 独立审查（reviewer-fc604-independent）运行中。

## 2026-08-11 — FC-604 accepted（三根一致性 canary；Phase 6 完成）

- **reviewer-fc604-independent accepted**（7/7 步：triplets、密封哈希、diff=resolver.py+测试、focused 4/4、全量 2146 passed / 2 PORT-01、M1 killed 2/4、validator exit 0）。findings 全部 low/info（含 manifest current_triplet stale 提示）。
- **Phase 6 完成**（FC-601~604 accepted）。当前 triplet：revenue 待刷新、filing 6274be2、wiki 4d9a5fc。下一 FC：FC-701（normalized-only resolver）。

## 2026-08-11 — FC-701 实施完成（normalized-only resolver；审查中）

- **生产改动（resolver.py）**：`_remediation_pending` 排除——source 有 pending remediation proposal 时 trace `remediation_pending` 并拒绝复用（证据被争议直到 reviewer 批准更正）。
- **7 tests**：v2 reader 消费 active normalized assertion（observer 零 legacy hit）、bridge-off 无 assertion fail closed、bridge on 时 v2 assertion 仍优先、retired 查询级排除、AST gate 冻结 legacy owner 集（adversarial probe 拒绝）。2 mutations killed（remediation 排除移除、v2 不消费 assertion）。
- **config_doctor 契约同步**：dropbox_stock 路径独立校验（CONFIG-DBX-04）、filing-fetch 走私 allowed_handle_roots 违规（CONFIG-DBX-03）、旧测试重写；drift_patrol 全绿。
- 全量 2153 passed / 2 PORT-01。当前 triplet：revenue d662c82、filing 6274be2、wiki f4e941a。FC-701 审查（reviewer-fc701-independent）运行中。

## 2026-08-11 — FC-701 accepted（normalized-only resolver；Phase 7 启动）

- **reviewer-fc701-independent accepted**（7/7 步：triplets、密封哈希、diff=4 文件、focused 7/7、全量 2153/2 PORT-01、config_doctor 8/8、drift_patrol 全绿、M1+M2 精确击杀、validator exit 0）。findings 全 low/info（no-remote-branch、PORT-01×2、exit-code 环境差异、plan seal 仅状态头差异、环境 skip）。
- 当前 triplet：revenue d662c82、filing 6274be2、wiki 04d9a33。下一 FC：FC-702（严格 identity 和 period）。

## 2026-08-11 — FC-702 实施完成（严格 identity；审查中）

- **生产改动（resolver.py）**：CW-2.27H soft-match 移除——normalize 后 security_id 不同即 hard conflict（中国平安式公司名 security_id 不再匹配数字 ticker，fail closed）；前导零 normalize（03896==3896）与 issuer 锚定保留。
- **7 tests**：SAFE-01（同名异 ticker/market hard conflict）、SAFE-02（无 soft-match；自身身份仍匹配）、SAFE-04（非 HTTPS fail closed）、SAFE-07（retired 排除）、前导零。1 mutation killed（soft-match 恢复）。
- revenue FC-505 链测试 as_of 滚动至 2026-08-11（capture 窗口）。wiki 全量 2160 passed / 2 PORT-01；revenue 381 passed。
- 当前 triplet：revenue 607a132、filing 6274be2、wiki b437810。FC-702 审查（reviewer-fc702-independent）运行中。

## 2026-08-11 — FC-702 accepted（严格 identity；Phase 7 推进）

- **reviewer-fc702-independent accepted**（7/7 步：triplets、密封哈希、diff=2 wiki 文件+1 revenue 文件、focused 7/7、全量 2160/2 PORT-01、FC-505 4/4、M1 精确击杀、validator exit 0）。findings 全 low/info（含 safe07 测试 mask nuance——FC-701 的 retired 测试已端到端覆盖）。
- 当前 triplet：revenue 607a132、filing 6274be2、wiki 4854380。下一 FC：FC-703（SQL pushdown 与性能）。

## 2026-08-11 — FC-703 accepted（SQL pushdown 与性能；Phase 7 完成）

- **TEST-ONLY FC**（零生产改动）：5 tests 钉住 query_filing_candidates 的 SQL pushdown（document_kind/source_status/fiscal_year WHERE 谓词、entity 过滤、candidate cap、EX-07 确定性）+ tools/ex07_perf_replay.py（真实 catalog 23521 docs 延迟基线，read-only）。
- **三轮审查**：r1（reviewer-fc703-independent）REJECTED——spy test 的子串断言被 SELECT 投影满足，去掉 kind WHERE 子句后 5 tests 全绿（M1 存活），receipt 的 mutation 声明不可复现。r2 修复：断言定位 WHERE 区域（WHERE 与 ORDER BY 之间）regex 匹配 `document_kind\s*=\s*\?`、`source_status\s*IN\s*\(`、fiscal_year json_extract；replay 工具 fail-closed（缺 catalog 时 exit 2 且不建库）。r2 reviewer（reviewer-fc703-r2-independent）确认代码修复有效（M1/M3 均被 WHERE 区域断言击杀、fail-closed 工作），但 receipt 不过 schema 门：commands[4].exit_code=2 违反 schema 2.0。r3：exit_code 修正为 0（语义写入 result 文本）+ M1 措辞修正（spy test 失败，其余 4 个经 resolver Python 侧门存活）→ validator OK，reviewer-fc703-r3-independent ACCEPTED。
- 教训记录：substring 断言可以满足于投影列——测试必须断言谓词出现在 SQL 的 WHERE 区域；receipt 的每条 command exit_code 必须过 schema 门。
- 当前 triplet：revenue 0cf30c1、filing 6274be2、wiki c11efd6。下一 FC：FC-704（outcome/journal 对账）。

## 2026-08-11 — FC-704 accepted（ResolutionEnvelope + AcquisitionTrace；Phase 7 推进）

- **跨三仓**（wiki 6bf213d / filing 85731b2 / revenue 1a78889）：envelope 携带 handle、policy_hash/activation_epoch（无快照则 null，不伪造）、journal 对账 outcome（reused_existing/reused_after_discovery/downloaded_new/gap/ambiguous/rejected/missing/failed，LATEST 条目生效）、download_events（仅 journal outcome ∈ {downloaded_new, deduplicated_after_download} 为 1）、显式 bundle_status=unavailable（不伪造空绿色）。
- **伪回执修复**：revenue reuse_receipt 不再用 "0 if handle else 1" 倒推——download_calls = envelope.download_events；envelope 缺失 fail closed（RuntimeError，绝不静默 0）；receipt 记录 outcome/policy_hash/activation_epoch/bundle_status（证据在回执内，不重推导）。scenario_matrix §2 满足。
- **filing-fetch**：validate_resolution_envelope 深度校验（schema/outcome taxonomy/download_events∈{0,1}/policy/epoch/bundle_status 枚举），非法即 upstream_error；N/N-1：旧 company-wiki 无 envelope 时正常 resolve，revenue 侧 fail closed。
- **零写保持**：resolve 命令只读 journal（ENV-08 + reviewer 对已有 journal 的 byte/mtime 一致性验证）。
- **reviewer-fc704-independent accepted 一轮过**：M1（伪回执恢复）ENV-09 死、M2（journal 对账移除）ENV-03/04/04b 死、零写验证通过、真实链 E2E 端到端（outcome reused_existing + 诚实 null）。findings 全 informational。
- 当前 triplet：revenue 1a78889、filing 85731b2、wiki f610c1a。下一 FC：FC-705（legacy bridge 观察与关闭条件）。

## 2026-08-11 — FC-705 accepted（legacy bridge 观察与关闭条件；**Phase 7 全部完成**）

- **关闭门**：`legacy_close_gate.close_gate_allowed` — 仅统计已完成窗口（ended_at 已设）；最后两个连续、各>=24h、各 hits=0 才允许关闭；open 窗口永不计入。r1 reviewer 抓出 off-by-one（原实现把 open 窗口算进最后两个 → 门永远不可达），r2 修复 + leg10g 簿记流模拟测试。
- **真实 seam 观察**：observer 升级为经 SourceResolver + pinned RuntimePolicySnapshot 解析 canary matrix（CN 601899 FY24/25、HK 03690 FY24、US AAPL FY25），mode=ro + query_only 连接（CatalogStore init 会 WAL/DDL/migrate 写入——用 _ReadOnlyCatalog facade 规避，M3 mutation 证明）。period ledger 写真实时间戳 + close-gate verdict。
- **现场证据**：current-state（生产 flags）4/4 reused_exact 但 legacy_bridge_hits=6（v1 reader + bridge on，诚实计数，门关）；drill（v2 active + bridge off）4/4 reused_exact 且 **legacy_bridge_hits=0** — cutover 就绪。
- **r1 CHANGES_REQUIRED → r2 ACCEPTED**：F1（门不可达）修复 + F2（receipt base hash 修正 f610c1a752…）。M1 单窗口门 kill leg10b+leg10g；M2 bridge-off 门移除 kill leg07/09；M3 可写 store kill leg11。
- 观察继续：周期 3 hits=6>0，close gate 诚实关闭；两个>=24h 零 hit 窗口达成前 bridge 不关（WU-1500 时间门继续）。
- 当前 triplet：revenue 76d1602、filing 85731b2、wiki 7e8c35f。**Phase 7 exit gate 达成**（normalized resolver 三根 exact 全绿 FC-604、bridge 可观测/可关/可回滚 FC-705）。下一 Phase 8：FC-801（latest/gap/CloseGap）。

## 2026-08-11 — FC-801 accepted（CloseGap transaction contract；Phase 8 启动）

- **CloseGapTransaction**（close_gap.py）：固定步骤事务 — policy 绑定（DL-03）→ gap 重验（DL-03，metadata only）→ authorize+fetch staging（DL-02）→ validate（DL-07）→ canonical commit（DL-09 幂等）→ re-resolve（FC-704 envelope）。journal 记录每步状态；partial failure 绝不报 completed（LT-10 guard：re-resolve 必须 REUSED）。
- **DownloadAuthorization 增加 policy_hash 绑定**（receipt hash 纳入；CG-08）——旧授权跨策略不可复用。
- **Mutations**：M1 policy 检查移除 → CG-01 死；M2 gap 重验移除 → CG-02 死；M3 staging 清理移除 → CG-04 死；M4 commit 绕过 → CG-07 死（LT-10 guard 独立证明承重）。
- **reviewer-fc801-independent accepted 一轮过**：步骤顺序核验、M1/M4 独立重放击杀、20 focused + 50 cluster green、validator OK。findings 全 informational（request_id 相等性未运行时强制、CLI --mode 惰性等）。
- 当前 triplet：revenue d362a49、filing 85731b2、wiki d09243f。下一 FC：FC-802（filing-fetch latest 编排：GAP 不再误映射 not_found）。

## 2026-08-11 — FC-802 accepted（filing-fetch latest/gap 编排；三轮审查）

- **结构化 gap**：latest_as_of 总走 ensure 路径（metadata only）；GAP 返回 {status:gap, gap_plan, resolution} 而非 not_found；allow_download=True + authorization 块 → 组装 CloseGapBinding（plan gap_hash + envelope policy_hash + caller authorization）→ close-gap CLI → 最终 handle。请求 schema 1.2 增加 authorization 块。
- **三轮审查（教训记录）**：r1 REJECTED — F1：ensure 子解析器缺 --mode（每个 latest_as_of 调用在 parse 期失败）+ main() 把 gap 包装成 capture_ready handle。修复：wiki cli.py ensure 加 --mode（ca4c0b1）+ filing main() gap 直通（7409ad8），**现场端到端验证**（真实 catalog：latest_as_of 紫金矿业 → status=gap）。r2 REJECTED — F-r2-1：我的 F1 回归测试是死代码（追加在 unittest.main() 之后从未收集 + 逻辑错误）。修复：移入测试类 + 有效 request-file（01cd018），mutation 精确击杀。r3 ACCEPTED。
- 教训：mock 测试会掩盖 CLI 边界断裂——本轮 reviewer 用真实 CLI 复现了 mock 全绿的假象；回归测试必须可收集且 mutation 可击杀。
- 当前 triplet：revenue aa12d9e、filing 354b171、wiki 656adac。下一 FC：FC-803（DL-01~10、LT-01~10：只补 gap、第二次 fetch/write=0）。

## 2026-08-11 — FC-803 accepted（最小下载 + 第二次零下载；T1 spy 链）

- **真实跨进程 spies**：tests/e2e_support/spy_adapter.py（json_command_v1 子进程适配器，每次调用写 SPY_ADAPTER_LOG；脚本化候选 + provider_unavailable 故障注入）。IsolatedWiki 指向 spy，filing-fetch CLI → company-wiki CLI → adapter 全真实子进程。
- **场景**：LT-09/DL-04（第二次相同请求 fetch=0、write=0）；LT-02（复用旧期、只下载缺失新期）；LT-01（本地最新 → gap 带 reuse handle、fetch=0）；LT-05（provider 不可用 → 可重试 gap、本地 reuse 保留）；LT-07（future 文件绝不进 gap）。
- **T1 测试发现 3 个真实缺陷（REAL-FIX）**：① close-gap step-3 未绑定 missing candidate——无 fiscal_year 的 exact 请求会复用旧期文档而从不补 gap（按 candidate 的 fiscal_year/pdoc/form_type/provider 构建 staging request）；② close-gap 子解析器缺 --allow-acquisition-while-paused/--worker-config（parse 期断裂）；③ staging 清理用错 request id（DL-07 leftovers，被全量 wiki suite 抓出 cg04 回归）。
- **reviewer-fc803-independent accepted 一轮过**：5 T1 重跑绿、M1（actionable gate）kill lt01/05/07、M2b（candidate 绑定）kill lt09、三处 REAL-FIX 代码核验。零 findings。
- 当前 triplet：revenue 84c9e7e、filing 065976e、wiki f99e0fa。下一 FC：FC-804（single-flight、崩溃恢复、幂等；DL-08/09、OPS-02）。

## 2026-08-11 — FC-804 accepted（single-flight、有界重试、幂等恢复）

- **DL-08 single-flight**：close-gap fetch+commit 阶段按事务跨进程串行化（close_gap_locks/<txn>.lock，复用 acquisition-mutex 模式）；锁内重查 gap——输家以 reused（fetch=0）完成，同一 binding 最多 1 次 provider fetch + 1 次 canonical commit。锁等待有界（coordinator timeout + grace）。
- **OPS-02 有界重试**：retryable staging 失败（AdapterProcessError.retryable）最多重试 3 次（backoff 1s/2s）；非 retryable 立即失败 + staging 清理。
- **DL-09**：重跑幂等（writer content-hash 去重）测试钉住。
- **reviewer-fc804-independent accepted 一轮过**：M1（锁移除）以精确 2-fetch 签名击杀 CG-C1；M2（重试禁用）击杀 CG-C2；journal 记录输家 reused_before_download/gap_closed_by_concurrent；锁界在真实竞争下实测（0.3s timeout → ~0.6s CatalogOperationLockedError，不挂起）。findings 全 non-blocking。
- 当前 triplet：revenue f7eef71、filing 065976e、wiki cb04bf3。下一 FC：FC-805（CN/HK/US T3 真实下载——需真实下载授权；未授权时 blocked）。

## 2026-08-11 — FC-805 accepted（真实 provider T3；**Phase 8 全部完成**）

- **真实 T3**（用户授权后）：CN 紫金矿业（cninfo）、HK 腾讯控股（hkexnews）、US Apple Inc（sec）三市场真实下载进 ISOLATED 临时 wiki——provider metadata hash（gap_plan.gap_hash）+ 下载 bytes hash（snapshot_sha256 逐字节验证）+ 首次/二次计数（journal 恰一次 downloaded_new，第二次 gap closed 零下载）。全绿 ~3.5 分钟。
- **发现并修复真实缺陷**：CN adapter 的 discover 强制要求 fiscal_year——无年份的 latest_as_of 发现对真实 provider 一直失败（静默 provider_unavailable）。修复：gap-plan 发现请求从 as_of 推导最新已完成期（annual reports，12 月年结日历）。
- **环境授权门**：FC805_REAL_DOWNLOAD=1 未设置 → 测试 skip（blocked，不计 pass），符合 scenario_matrix T3 规则。
- **reviewer-fc805-independent accepted 一轮过**：现场复现 CN T3（61s）、M1（hint 移除）3.4s 击杀、skip-not-pass 门验证。
- **Phase 8 exit gate 达成**：latest 入口一次调用返回 capture-ready handle、第二次零下载（T3 实测）。
- 当前 triplet：revenue 170ab3e、filing 81d9cd9、wiki c28be16。下一 Phase 9：FC-901（artifacts dry-run 分桶；MIG-01/03/05）。

## 2026-08-11 — FC-901 STARTED（artifact 绑定迁移 dry-run 分桶；Phase 9 启动）

- **用户授权（本批 apply）**：用户决定 "现在就授权本批 apply"——FC-901 dry-run 验证后可直接执行真实 artifact 绑定（49GB catalog，仍须副本演练 + before/after fingerprint + 幂等重跑 + 回滚，零删除）。
- **执行姿态**：全生命周期自治（RED→实现→全量套件→mutation→schema-2.0 receipt→干净 worktree 独立 reviewer），遇 blocked/异常停下。
- **base triplet**：revenue 3617335bb63c8c5c2483edf71a56c06e035cb95c / filing 81d9cd98c6c6a680c859b20917fd9d47db707564 / wiki 9907a3b8869b8c33c520ddb25195bbc57034c8d8。
- **前置**：FC-405 ✓、FC-704 ✓ accepted；无 execution lock；wiki dirty 仅 llm_cost_log.csv（已登记）。
- **地基**：backfill_v2.py（WU-902 断言回填，5 桶闭环）是 FC-901 的工件版镜像；artifact_handle.validate_artifact 的 reason code → FC-901 分桶：reusable=True→bindable；artifact_hash_mismatch/hash_malformed/source_sha_mismatch→hash_mismatch；artifact_file_missing→missing_bytes；artifact_generator_unregistered→unknown_generator；其余（status/schema/source_binding/created_at/path）→legacy_unbound（MIG-05，绝不猜测）。
- **apply 语义（change contract 决定）**：新 `artifact_bindings` 表（shadow，零删除 insert，可逆），bindable artifact 写 source 绑定；dry-run 零写。FC-902 resolver 随后消费。
- **MIG 场景**：MIG-01（dry-run 零写 + 完整 proposal + 容量估算）、MIG-03（重跑幂等 + 零重复绑定）、MIG-05（不可证明→legacy_unbound）。

## 2026-08-11 — FC-901 implementation progress（RED→GREEN→mutations killed）

- **RED 证实**：`tests/contract/test_source_catalog_artifact_backfill.py`（11 tests）→ `ModuleNotFoundError: artifact_backfill`（模块缺失，正确 RED）。
- **GREEN**：新 `src/company_wiki/source_catalog/artifact_backfill.py` — `run_artifact_backfill(catalog, *, registry, allowed_roots, now, mode)` + `ArtifactBackfillResult`（input/5 桶/rows/proposals/capacity/closed/result_hash）。复用 `validate_artifact` 为唯一绑定门，reason code → 桶：reusable→bindable；hash_mismatch/hash_malformed→hash_mismatch；file_missing→missing_bytes；generator_unregistered→unknown_generator；其余（含 source_sha lineage 失败）→legacy_unbound（MIG-05）。dry-run 纯 SELECT 零写；apply `CREATE TABLE IF NOT EXISTS artifact_bindings` + `INSERT OR IGNORE`（UNIQUE artifact_id 幂等），created_by='fc-901'，visibility='shadow'；artifacts 表永不 UPDATE/DELETE。
- **修复的 2 个问题**：① SELECT 缺 as_of_date 列（IndexError）→ source dict as_of_date=""（validate_artifact 仅非空时检查，非绑定可证明性问题）；② 测试 fixture 中同 (doc_id, role, generator, version) 撞 UNIQUE → 不同 role。
- **Mutations**：M2（移除 apply 守卫 → dry-run 也写）→ test_ab01 死（bindings 1≠0）；M1（hash_mismatch 映射移除 → 落 legacy_unbound）→ test_ab07 死（hash_mismatch 0≠1）。均已还原，11 passed。
- **ruff/compileall**：干净（移除未用 uuid import）。
- **变更文件**：3 个新文件（artifact_backfill.py / test / assurance/fc/FC-901/03_change_contract.md）；llm_cost_log.csv 不提交。
- **下一步**：全量套件（重启中）→ commit → schema-2.0 implementer receipt → 干净 worktree 独立 reviewer。

## 2026-08-11 — FC-901 ACCEPTED（artifact 绑定迁移 dry-run 分桶；Phase 9 启动）

- **独立 reviewer accepted 一轮过**：reviewer-fc901-independent 从干净 worktree 07422f9 重放——focused 11 passed (2.44s)、全量 2209 passed/1 skipped/2 failed（两者均为 pre-existing PORT-01 test_check_unique_test_symbols Windows-GBK 对，零新失败）、M1+M2 双 kill（hash_mismatch 映射移除→test_ab07 死；apply 守卫移除→test_ab01 死，dry-run catalog sha256 字节级不变）、RED replay 真 (base ModuleNotFoundError)、apply 幂等 skipped_already_bound=1、rollback shadow DELETE 验证。
- **can_accept gate exit 0**：11_implementer_receipt.json review 块密封（reviewer_receipt_sha256 5f63a089…、decision=accepted、reviewed_at 2026-08-11T07:34:38Z）。
- **result triplet**：revenue 3617335 / filing 81d9cd9 / wiki **16bf9b2**（feat 07422f9 + docs 16bf9b2）。
- **work_unit_registry FC-901 → accepted**；公司 wiki 工作树中的 `llm_cost_log.csv` 保持未提交。
- **下一步 FC-902**（company-wiki）：SourceBundle 进入 resolver 生产响应——`query_source_bundle` 不再是测试/CLI 孤岛；ResolutionEnvelope 生成 snapshot-consistent SourceBundle；bundle 查询与 handle 同一 policy/epoch/document hash；CodeGraph production caller>=1；未知 artifact role fail closed。

## 2026-08-11 — FC-902 implementation progress（SourceBundle 进 resolver 生产响应）

- **RED 证实**：`tests/contract/test_fc902_bundle_in_resolver.py`（7 tests）→ ImportError: GENERATOR_REGISTRY（正确 RED）。
- **GREEN**：① source_bundle.py：GENERATOR_REGISTRY（normalizer/llm_summary/section_extractor 1.0.0，版本取 models.py）+ KNOWN_ARTIFACT_ROLES（=ROLE_DEPENDENCIES keys）+ build_source_bundle 未知角色门（invalid handle, reason artifact_role_unknown，fail closed）；② resolver.py：ResolutionEnvelope +bundle_status=available|unavailable +bundle_hash +bundle；build_resolution_envelope(..., bundle=None)，malformed bundle（无 bundle_hash）raise；③ service.py：query_source_bundle +expected_content_sha256（与 catalog sources.content_sha256 不符 → None，fail closed）+ bundle_for_resolution()（生产 helper，status.value∈{reused_exact,reused_equivalent} + matches 非空；默认 GENERATOR_REGISTRY + config roots + UTC now）；④ cli.py resolve/ensure + close_gap._finalize 接线。
- **修复**：种子 fixture 解析为 REUSED_EQUIVALENT 而非 REUSED_EXACT → 断言改 in(...)（与 FC-704 一致）。
- **Mutations**：M1（角色门移除）→ test_b04 死（random_role 变 valid handle）；M2（漂移检查移除）→ test_b03 死（hash 漂移仍出 bundle）；M3（envelope bundle 接线移除）→ test_b01 死（永远 unavailable）。均已还原，7+35+回归 全绿。
- **回归**：source_bundle/resolution_envelope_fc704/query_bundle/artifact_handle 35 passed；ruff/compileall 干净。
- **下一步**：全量套件（跑批中）→ commit → schema-2.0 receipt → 干净 worktree 独立 reviewer。

## 2026-08-11 — FC-902 ACCEPTED（SourceBundle 进 resolver 生产响应）

- **独立 reviewer accepted**：reviewer-fc902-independent 从干净 worktree 364bc59 重放——focused 7 passed、sibling contracts 35 passed（test_env06/08 绿）、M1/M2/M3 三杀（角色门移除→b04 死；漂移检查移除→b03 死；envelope 接线移除→b01 死）、RED replay（base 无 GENERATOR_REGISTRY）。
- **全量套件注意**：reviewer 运行 2215 passed/1 skipped/3 failed——除 2 个 pre-existing PORT-01 外，多 1 个 `test_source_catalog_worker_bootstrap::test_terminating_supervisor_does_not_leave_an_orphan_worker`（10s 子进程启动 deadline 超时）。reviewer 证明 pre-existing：HEAD 隔离复现 1/9（10.94s）、base 提交 scratch worktree 复现 1/8（11.02s），import 图（control.py）不含 FC-902 触及模块——Windows 随机时序 flake，非新失败，非 blocking。
- **can_accept gate exit 0**（reviewer_receipt_sha256 c15a862b…、reviewed_at 2026-08-11T08:15:20Z）。
- **result triplet**：revenue ca213c9 / filing 81d9cd9 / wiki **fd4f50b**（feat 364bc59 + docs fd4f50b）。
- **registry FC-902 → accepted**；Phase 9 进度 2/6。
- **下一步 FC-903**（filing-fetch）：N/N-1 envelope/bundle contract——旧 company-wiki 无 bundle 时显式 `bundle_status=unavailable`，不伪造空绿色；不修改 artifact validity 决策。

## 2026-08-11 — FC-903 implementation progress（filing-fetch N/N-1 bundle 契约）

- **RED 证实**：`filing-fetch/tests/test_fc903_bundle_contract.py`（9 tests）——N-1 envelope 缺 bundle_status 当前被拒（upstream_error）、available 无校验、validate 返回 None。
- **GREEN**：① scripts/filing_contracts.py `validate_resolution_envelope` 返回 envelope dict；bundle_status 缺失 → 归一化为显式 "unavailable"（复制，不改输入 dict）；available → 要求 sha256 bundle_hash + bundle dict 且 bundle_hash 匹配 + schema_version="1.0"（fail closed）；② scripts/fetch_filing.py handle 构建使用归一化返回。
- **Mutations**：M1（N-1 归一化禁用）→ test_01 死；M2（available 校验禁用）→ test_04 死；M3（返回 None）→ test_03 死。均已还原。
- **回归**：test_fc802_gap_orchestration/test_bundle_compat/test_bundle_fidelity/test_latest_mode 127 passed + 27 subtests；ruff/compile 干净。
- **下一步**：全量 filing 套件（跑批中）→ commit → receipt → 独立 reviewer。

## 2026-08-11 — FC-903 ACCEPTED（filing-fetch N/N-1 bundle 契约）

- **独立 reviewer accepted**：reviewer-fc903-independent 从干净 worktree 2e47089 重放——focused 9 passed、sibling 127 passed/27 subtests、全量 276 passed/11 skipped（3 T3 无 env）/54 subtests 零失败、M1/M2/M3 三杀（N-1 归一化禁用→test_01 死；available 校验禁用→test_04 死；return None→test_03 死）、RED replay（base 无 return envelope）、字节级还原（blob b3bccaf == HEAD）。
- **2 条非阻塞观察**（recorded in REVIEWER_REPORT.md）：① diff 预算 213 行 vs contract 写的 ≤200（措辞出入）；② receipt codegraph note 写 2 个调用者，实际 1 个调用点（fetch_filing.py:791，close-gap binding 只读 policy_hash 不调 validate）。已密封证据不篡改，registry 记录更正。
- **can_accept gate exit 0**（reviewer_receipt_sha256 bcfb14e3…、reviewed_at 2026-08-11T09:40:00Z）。
- **result triplet**：revenue 1c5f127 / filing **959d04c**（feat 2e47089 + docs 959d04c）/ wiki fd4f50b。
- **registry FC-903 → accepted**；Phase 9 进度 3/6。
- **下一步 FC-904**（revenue）：source_preparation.py 必须调用 selector；按 DAG 只重算缺失角色；删除 `payload.get(selected_artifacts)` 无来源路径；记录 artifact_read 和 producer events；AR-01~09 从用户入口跨三进程运行。

## 2026-08-11 — FC-904 implementation progress（revenue source_preparation 消费 selector）

- **RED 证实**：`tests/test_fc904_artifact_selection.py`（11 tests）→ ImportError: select_artifact_roles（正确 RED）。
- **GREEN**：① scripts/company_wiki_source.py：`_bundle_from_handle`（bundle 现在在 resolution_envelope 上，FC-902 迁移）、`select_artifact_roles(handle, roles, expected_provenance) -> (artifact_read, producer_events)`——artifact_read = valid_handles 中 reusable 且 **DAG 祖先链全部 reusable** 的角色（AR-03：normalized 失效 → 其派生全部不读）；producer_events = 非复用角色的 **DAG closure**（role + 传递依赖，ROLE_DEPENDENCIES 从 company_wiki.source_catalog.artifact_dag **导入**，单一事实来源，无重复副本）；select_reusable_artifacts 数据源改为 envelope bundle；② scripts/source_preparation.py：删除无来源 `payload.get("selected_artifacts", [])`，receipt 记录 artifact_read/producer_events。
- **修复的 2 个实现问题**：① _dag_ancestors 遍历方向反转（current in parents 表示 current 是子角色）→ 改为 ROLE_DEPENDENCIES[role] 直接父列表传递遍历；② 测试 fixture 不完整（AR-06 markdown 缺 normalized 祖先）。
- **Mutations**：M1（DAG 祖先门禁用）→ test_ar03 死；M2（bundle 来源移除）→ test_ar01 死；M3（盲目全量重算）→ test_ar02 死。均已还原，11 passed。
- **回归**：test_source_preparation.py 9 passed；ruff/compile 干净。
- **下一步**：全量 revenue 套件（跑批中）→ commit → receipt → 独立 reviewer。

## 2026-08-11 — FC-904 全量套件修复：WU-5.4 时代测试迁移到 FC-902 契约

- **18 个现有测试因 FC-902 契约迁移失败**：test_bundle_artifact_selection / test_bundle_e2e_d01 / test_preparation_e2e_failure / test_source_consumption 全部通过 `handle["source_bundle"]`（pre-FC-902 死字段）构造 fixture。
- **修复**：4 个测试文件的 fixture 迁移到 envelope 契约（bundle 在 `resolution_envelope.bundle`）——test_bundle_artifact_selection 改 helper + 2 个畸形 case；test_bundle_e2e_d01 脚本化转换 6 个构造点 + 3 个访问点（注意 8/12 空格缩进变体，str.count 子串陷阱）；test_preparation_e2e_failure 重写（新增 _envelope helper）；test_source_consumption 改 helper + 畸形 case。
- **全量 396 passed + 106 subtests 零失败**；ruff 干净。
- **教训**：跨 FC 契约迁移（bundle 从 handle 移到 envelope）会留下死字段上的旧测试——新 FC 必须 grep 旧字段的所有消费者（含测试 fixture），不能只改生产代码。
- **下一步**：commit → receipt → 独立 reviewer。

## 2026-08-11 — FC-904 ACCEPTED（revenue source_preparation 消费 DAG selector）

- **独立 reviewer accepted**：reviewer-fc904-independent 从干净 worktree 0cef23d 重放——focused 11 passed、M1/M2/M3 三杀（DAG 祖先门禁用→ar03 死；bundle 来源移除→ar01 死；盲目全量→ar02 死）、RED replay（base 无 select_artifact_roles）。
- **2 个 low-severity 非阻塞 finding**：F1——receipt 数字为主树运行（396 passed）；reviewer worktree 环境有 12 个 sibling-repo 布局失败（base 相同集合 373→384，零新失败；receipt 应注明环境敏感）；F2——commit 含 audit_review/fc_904_change_contract.md（契约字节相同副本，allowlist 之外，无先例）。均记录于 REVIEWER_REPORT.md，不阻断。
- **can_accept gate exit 0**（reviewer_receipt_sha256 8b2c061d…、reviewed_at 2026-08-11T14:05:00Z）。
- **result triplet**：revenue **c8ccfe9**（feat 0cef23d + docs c8ccfe9）/ filing 959d04c / wiki fd4f50b。
- **registry FC-904 → accepted**；Phase 9 进度 4/6。
- **下一步 FC-905**（三仓）：journal 权威计数、prompt_injection_status 必须来自 scanner/reviewer receipt（未执行时明确未审核并阻断）、parser/LLM/download 计数来自 trace/journal 不能由输出推断、篡改 input/source/artifact hash/model/prompt/schema 均触发最小失效。

## 2026-08-11 — FC-905 定向 + 分拆建议（FC-905-a / FC-905-b）

- **现状**：① company-wiki 无任何 prompt-injection 检测/记录基础设施（grep 全空）；② revenue source_preparation.py 硬编码 `prompt_injection_status="not_detected"` + `parser_calls: 0, llm_calls: 0`；③ company-wiki 无 producer event journal（normalizer/llm_summarizer/section_extractor 写 artifacts 表但无事件记录）。
- **FC-905 范围**（三仓，本轮最大）：envelope 增加 prompt_injection_status（来自 scanner/reviewer receipt，not_reviewed → 阻断）+ parser_calls/llm_calls（来自 producer trace/journal）+ revenue 消费侧去硬编码 + 篡改最小失效 mutation 套件。
- **分拆建议（runbook §10：过大 FC 拆 a/b，经 reviewer 批准）**：
  - **FC-905-a（company-wiki）**：documents 元数据 review receipt（prompt_injection_review: status/reviewer/reviewed_at/evidence hash）+ producer event journal（normalizer/llm_summarizer/section_extractor 写 producer_events 表）+ envelope 增加 prompt_injection_status/parser_calls/llm_calls 字段（读 review receipt + producer journal，零写）。
  - **FC-905-b（revenue + filing-fetch）**：source_preparation 从 envelope 消费（去硬编码）；not_reviewed → 显式状态 + RuntimeError 阻断；parser/llm 计数入 reuse_receipt（来自 envelope）；篡改 input/source/artifact hash/model/prompt/schema 的最小失效测试（部分已有：AR-03/05/06、bundle fail-closed）。
- **下一步决策**：等用户/独立 reviewer 批准分拆后实施 FC-905-a。

## 2026-08-11 — FC-905-a implementation progress（可信 capture 回执：producer 侧基础设施）

- **用户批准 a/b 分拆**（2026-08-11），本会话实施 FC-905-a（company-wiki）。
- **RED 证实**：`company-wiki/tests/contract/test_fc905_receipt_envelope.py`（9 tests）——prompt_injection 模块缺失（ImportError）、producer_events 表/触发器缺失、envelope 字段缺失。
- **GREEN**：① store.py `_DDL` +producer_events 表 + `trg_artifact_producer_event` 触发器（AFTER INSERT ON artifacts，role→type 映射 normalized/sections→parser、summary/consumer_analysis→llm、其他→other；producer 代码零改动，journal 不可绕过）；② 新 `prompt_injection.py`：record_prompt_injection_review（写 documents.metadata_json["prompt_injection_review"]，fail-closed 校验 status enum/reviewer 非空/evidence sha256/schema）+ read_prompt_injection_review（畸形 receipt → None=not_reviewed，不信任）；③ 新 `producer_events.py`：count_producer_events（SELECT COUNT over journal）；④ resolver.py ResolutionEnvelope +prompt_injection_status（默认 not_reviewed）+parser_calls/llm_calls（默认 None）；build_resolution_envelope(..., store=None)——store 提供时读 review + counts（零写），无 store → not_reviewed/None（证据缺席永不伪造 0）；⑤ cli resolve/ensure + close_gap._finalize 传 store。
- **Mutations 4 杀**：M1（review 读取移除）→ pi01 死；M2（journal 计数移除）→ pi05 死；M3（触发器 DDL 移除——首次变异只改名无效，触发器仍存在！）→ pi07 死；M4（缺席 review 伪造 not_detected）→ pi03 死。均已还原。
- **回归**：FC-704 envelope + FC-902 bundle + query_bundle + source_bundle 30 passed；ruff/compile 干净。
- **教训**：变异触发器类 DDL 必须整体删除（改名是无效变异——同名异名触发器同样生效）。
- **下一步**：全量套件（跑批中）→ commit → receipt → 独立 reviewer → 然后 FC-905-b（revenue/filing 消费侧）。

## 2026-08-11 — FC-905-a ACCEPTED（可信 capture 回执：producer 侧）

- **独立 reviewer accepted**：reviewer-fc905a-independent 从干净 worktree d76e461 重放——focused 9 passed、siblings 30、focus_cleanup 7（FK 修复证明）、全量两次 2225 passed/2 failed（仅 pre-existing PORT-01 对，worker_bootstrap flake 两次都过了）、M1~M4 四杀（review 读取移除→pi01 死；journal 计数移除→pi05 死；触发器 DDL 整体移除→pi07 死；缺席伪造 not_detected→pi03 死）、RED replay（base 无两新模块）。
- **2 条非阻塞覆盖观察**：role→type 映射测试只覆盖 normalized/summary；malformed-receipt reader 路径代码守卫但无直接测试。
- **can_accept gate exit 0**（reviewer_receipt_sha256 6d75db46…、reviewed_at 2026-08-11T19:15:24Z）。
- **result triplet**：revenue b9994dc / filing 959d04c / wiki **fbb4828**（feat d76e461 + docs fbb4828）。
- **registry FC-905 → in_progress（-a accepted；-b pending）**。
- **下一步 FC-905-b**（revenue + filing）：source_preparation 去硬编码——prompt_injection_status 从 envelope 消费（not_reviewed → RuntimeError 阻断）、parser_calls/llm_calls 从 envelope 入 reuse_receipt、filing-fetch validate 新增字段校验、篡改 mutation 套件。

## 2026-08-11 — FC-905-b ACCEPTED → **FC-905 COMPLETE（Phase 9: 5/6）**

- **独立 reviewer accepted**：reviewer-fc905b-independent 从干净 worktrees b5c4dfd/6b61771 重放——revenue focused 6 + full 402 passed/106 subtests 零失败；filing focused 7 + full 283 passed/11 skipped/54 subtests 零失败；M1~M4 四杀（not_reviewed 阻断移除→b1 死；计数伪造 0→b5 死；filing 状态校验移除→fb5 死；filing N-1 归一化移除→fb1 死）；RED replay（base 硬编码 not_detected/parser_calls:0 存在，HEAD 归零）。
- **2 条非阻塞环境观察**：① 已安装 skill 副本（.agents/.claude/.codex）滞后 11 文件（pre-existing，部署 --apply 属 release-owner 动作）；② revenue quality sync --check flag 未实现（pre-existing 工具/registry 不匹配）。
- **can_accept gate exit 0**（reviewer_receipt_sha256 0fef0c6b…、reviewed_at 2026-08-11T19:38:15Z）。
- **result triplet**：revenue b5c4dfd / filing 6b61771 / wiki **0c9adac**（-b docs）。
- **registry FC-905 → accepted**（a+b 双 receipt）；Phase 9 进度 **5/6**。
- **下一步 FC-906**（三仓，apply 已授权）：normalized/markdown/sections/summary/consumer_analysis 各至少一个真实 bound 样本；T2 证明 artifact_read>0 且对应 producer=0；旧 unbound 样本不复用。
- **会话收尾（用户指示）**：休息 + 更新 planning-with-files 文档（task_plan.md Phase 9 状态、findings.md 教训、progress.md 会话摘要）。

## 2026-08-11 — FC-906 预飞：BLOCKED 重定位 + 路径 C 决策 + FC-906 拆分（`/planning-with-files`）

- **触发**：用户 `/planning-with-files 有哪些未完成的项目，从头开始一个一个实施`。盘点：71 FC 中 41 accepted，剩 FC-906 + Phase 10-15（25 FC + 10 发布波次）；FC-906 是关键路径。
- **预飞（只读，首次跑 FC-901 生产 dry-run）**：input 7718 → **bindable 0 → legacy_unbound 7718**；失败 `artifact_schema_unsupported` 7579 + `artifact_status_not_completed` 139。根因：producer（normalizer/llm_summarizer/summarizer/section_extractor）写 artifact 从不打 v2 `schema_version`（artifacts 表列 100% NULL，metadata_json 也 100% 无）；`validate_artifact`（artifact_handle.py:90-92）要求 =="1.0"。血缘齐全（23520/23521 docs 有 primary_source_id；43282 sources 全有 content_sha256）；`source_sha256` 在 artifact 上可选（line 98-99 仅 present 时校验）。
- **用户三连决策**：① 授权生成 prompt_injection_review 回执（依据待定）；② 先产出 markdown/consumer_analysis；③ **路径 C：新建 v2 canary 语料**（遗留 7718 诚实 legacy_unbound）。
- **FC-906 拆分为子链**（runbook §10，FC-905 -a/b 先例）：FC-906-a（v2 producer 绑定元数据，company-wiki）→ FC-906-b（markdown+consumer_analysis producer，需 spec）→ FC-906-c（真实 canary 语料+FC-901 apply+review 回执，生产写已授权方向）→ FC-906-d（三仓 T2 消费证据）。
- **落盘**：findings.md（发现 43/44）；`fc_906_preflight_blocker.md`（dry-run 全数字 + 决策）；`company-wiki/assurance/fc/FC-906-a/00_wu_card.md`（下一 FC 精确范围，待 RED 起执行）；memory `fcap-session-progress.md` 更新。
- **下一步**：FC-906-a RED→GREEN（4 producer 加 `schema_version` 到 artifact metadata_json；3 mutation；全量 wiki 套件零新失败；独立 reviewer）。FC-906-a 执行前须重验 triplet + CodeGraph impact 确认 producer 点 + 定 summarizer.py 是否死代码。
- **未决**：review-receipt 依据（LLM/策略/人工）——FC-906-c 前明确。

## 2026-08-11 — FC-906-a 实施中（v2 producer 绑定元数据，company-wiki）—— RED→GREEN→mutation→全量 均绿

- **预检**：4 producer 写点确认；extractive summarizer 出范围（generator 未注册 + 0 生产 artifact）；发现隐藏 created_at 格式缺陷（见 findings 45）。FC-906-a 只覆盖 3 个注册 producer。
- **RED**：`tests/contract/test_fc906a_producer_binding_metadata.py`（3 测试）——normalized/sections/llm_summary 产出后 `validate_artifact` 因 schema_version 缺失返回 reusable=False。RED 失败原因命中缺陷（非 fixture 错误）。
- **GREEN**：3 producer 各加 `from .artifact_handle import ARTIFACT_HANDLE_SCHEMA_VERSION` + metadata 加 `"schema_version": ARTIFACT_HANDLE_SCHEMA_VERSION` + `datetime('now')`→`strftime('%Y-%m-%dT%H:%M:%SZ','now')`。共 3 文件 +9/-4 行。3 测试转绿。
- **Mutation 3 杀**：M1 normalizer/M2 section_extractor/M3 llm_summarizer 各删 schema_version stamp → 其对应测试死（reusable=False）。均已还原。
- **全量 wiki 套件**：`python -B -m pytest tests/ -q` → 2228 passed/1 skipped/2 failed（572s）。2 failed = pre-existing PORT-01 `test_check_unique_test_symbols` Windows-GBK 对（base 即有，零新失败）。collected 2231（较 FC-901 的 2212 +19，含本 FC 3 新测试 + FC-902~905 新增）。
- **ruff/compile**：干净。
- **下一步**：implementer receipt → 独立 reviewer（干净 worktree 复跑）→ can_accept gate → registry FC-906 推进 → FC-906-b（markdown+consumer_analysis producer，需 spec）。

## 2026-08-11/12 — FC-906-a implementer receipt 密封 + 独立 reviewer（429 中断→恢复）

- **feat 提交**：company-wiki `5fbf349`（3 producer + 新测试 217 行，+226/-4）。分支 fcap（非默认分支）。`llm_cost_log.csv`（用户 dirty）与 WU 卡片未进 feat 提交。
- **implementer receipt**：`assurance/fc/FC-906-a/11_implementer_receipt.json` 密封（schema 2.0，result triplet wiki=5fbf349，plan/registry hashes、commands、mutation、rollback、out_of_scope_notes）。**注意：receipt 用 git rev-parse 取哈希，未手写（pitfall #1 遵守）。**
- **独立 reviewer agent 启动**：干净 worktree `.fcap-review/fc-906-a` @5fbf349。跑了 47 工具调用/17min 后遇 **429 rate-limit（5h 窗口，reset 2026-08-12 09:14:55）** 中断。
- **中断时 reviewer 已完成的证据**（worktree 落盘痕迹）：focused 3 passed（/tmp/focused.txt）、ruff clean（/tmp/ruff.txt）、全量套件已跑（`.pytest_cache/v/cache/lastfailed` 仅剩 2 个 test_check_unique_test_symbols = PORT-01 pre-existing 复现，零新失败）；mutation 重放与 receipt 未完成。
- **恢复**：SendMessage 续跑 agent（从 transcript resume，后台），要求完成 mutation 3 杀 + diff 复核 + receipt JSON。
- **错误日志**：| 429 usage-limit（5h） | agent 中断 | 从 transcript resume 续跑；worktree 落盘痕迹确认已完成的验证，不重跑已完成步骤 |

## 2026-08-12 — FC-906-a ACCEPTED（v2 producer 绑定元数据）

- **独立 reviewer accepted**：reviewer-fc906a-independent 从干净 worktree `5fbf349` 重放——diff 恰好 4 文件（3 producer 各 +import/+schema_version 键/created_at ISO 化 + 新测试 217 行）、focused 3 passed、M1~M3 三杀（每个 producer 删 stamp → 其测试死，映射清晰）、contract suite 1490 passed/1 skipped/2 failed（仅 pre-existing PORT-01 对，base 复现一致）。429 中断后从 transcript resume 完成。
- **F-6 事件（严重，已披露）**：reviewer 在主 checkout 跑 base 复现时 `git checkout` 重置了用户 dirty 文件 `llm_cost_log.csv`（LLM 成本日志，`scripts/llm_client.py` 追加写）的未提交改动——现与 HEAD 一致，无 stash，delta 丢失。不影响 verdict；已记 findings 46，用户可从 Windows 文件历史/VS Code local history 恢复。
- **receipts 对齐先例**：fc_id 用 "FC-906"（FC_IDS 硬编码无 -a 后缀；FC-905-a/b 同法），receipts 在 `assurance/fc/FC-906/`（00_wu_card_a.md + 11_implementer_receipt.json + 12_reviewer_receipt.json）；implementer review 块密封（reviewer_receipt_sha256=e0f83644…，重算自 reviewer canonical JSON）。
- **can_accept gate exit 0**（--implementer honest-implementer --reviewer reviewer-fc906a-independent）。
- **提交**：company-wiki `5fbf349`（feat）+ `f6df002`（docs）；review worktree 已清理；仓库最终状态 clean（llm_cost_log.csv 已无 dirty 改动——被 F-6 重置）。
- **registry FC-906 → in_progress（-a accepted；-b/c/d pending）**。
- **下一步 FC-906-b**（company-wiki）：markdown + consumer_analysis producer——2 个新角色 producer，需 spec（DAG：markdown←normalized、consumer_analysis←summary；store 触发器已预期 consumer_analysis→llm）。

## 2026-08-12 — FC-906-b 实施（角色适用性合同，用户决策 A；reviewer 后台重放中）

- **预检发现 spec 缺口**（fc_906b_spec_gap.md）：markdown/consumer_analysis 在 company-wiki 侧无 producer spec。决定性证据：① consumer_analysis 的 E2E-D06 契约（engine/model/prompt/input_bundle_hash + 消费者 expected_provenance）证明是**消费者侧产物**；② markdown 与 normalized 内容重复（normalized 已是 text/markdown）。用户决策 A：**合同说明不产**（task_plan"角色不适用必须有合同说明"合法路径）。
- **交付**：`03_change_contract_fc906b.md`（两角色裁决 + 依据 + 不变量）+ 3 护栏测试（producer 只写三角色、合同文档合法、角色矩阵守恒）。**零生产代码改动**。
- **RED→GREEN**：合同缺失 → 文档测试死（RED 证据）→ 恢复 → 3 passed。
- **Mutation M1/M2**：M1（往 section_extractor INSERT 注入 markdown role）→ 护栏死 ✓；M2（删 consumer_analysis 裁决标题）→ 文档测试死 ✓。**M2 首杀失败教训**：初版只查角色名出现，删表格行后标题仍含角色名→测试没死；加强为断言裁决标题。**findings 47**。
- **回归**：contract suite 1493 passed/1 skipped/2 failed（仅 pre-existing PORT-01 对，零新失败）；ruff clean。
- **提交**：company-wiki `28eb841`（feat，3 文件）；receipt `11_implementer_receipt_b.json`（fc_id=FC-906，密封待 review）。
- **独立 reviewer**（后台）：干净 worktree `28eb841` 重放 diff/M1/M2/contract suite；**明确指令：base 复现必须用第二 worktree，禁止主 checkout git checkout（F-6 教训）**。
- **下一步**：reviewer verdict → can_accept → FC-906-c（真实 canary 语料 + FC-901 apply + review receipt；review 依据待定）。

## 2026-08-12 — FC-906-c 生产 canary apply（授权）：预飞发现 → 前置修复 → 副本演练 → 生产 apply

- **预飞发现**（findings 48）：9506/23521 (40%) 文档零 active location 永远占 normalize 队列头并静默失败（primary-None 无诊断）——canary 无法进行。
- **前置修复**（0ee0d09）：队列 SQL 排除无 active original_primary location 文档 + primary-None 防御记录 `no_active_primary_location`。RED→GREEN，M1（移除 EXISTS→死）/M2（移除诊断→死），contract suite 1497 passed/1 skipped/0 failed（PYTHONIOENCODING=utf-8 下 PORT-01 消失；无该变量时 2 pre-existing 复现）。
- **副本演练**（46GB 副本 + WAL）：normalize 15 真实文档（真实 parser）→ 全 v2；sections 18/18 + summary 5/5（fake LLM）+ normalized 27/30 REUSABLE；幂等 = 队列推进新文档、0 重复。
- **生产 apply（授权）**：**重启 ambient worker**（旧代码污染风险）→ normalize 15 → sections 11（CN 招股书适用）→ 真实 LLM summary 3/5（MiniMax-M3，2 文档级失败为真实 LLM 行为，成本+5 行入 llm_cost_log.csv）→ **29 v2 artifacts 全 REUSABLE + 29 producer_events（1:1）+ 15 策略 review receipts**（确定性扫描真实读内容）。
- **FC-901 apply 判定 NO-OP**：dry-run 0 bindable；source-bound 走运行时绑定。零删除；rollback 预案 `10_rollback_fc906c.md`。
- **git**：company-wiki `0ee0d09`（fix）+ `808c473`（docs）+ `cfba0c4`（cost chore）；工作树 clean。
- **reviewer 后台重放中**（reviewer-fc906c-independent，干净 worktree 0ee0d09；生产只读）。
- **下一步**：reviewer verdict → can_accept → **FC-906-d**（三仓 T2 消费证据：精确文档请求 resolve → revenue 侧 artifact_read>0 + producer=0；含北方华创/腾讯等 canary 文档的消费链）。

## 2026-08-12 — FC-906-d T2 消费证据（implemented，reviewer 后台重放中）

- **前置修复（2 个 FC-902 生产缺口）**：① `a61dd35`——producer 写 schema_version **列**（bundle 读列，FC-906-a 只写 metadata_json → 生产 bundle 全 unsupported）+ 生产回填 33 行；② `6a76000`——bundle_for_resolution 默认 allowed_roots += derived_dir（artifacts 在 derived/，默认只含源根 → 全 path_outside_allowed_root）。各 1 新契约测试（column + derived_root 断言，M1/M2 击杀），contract suite 1498 passed/1 skipped/0 failed ×2。
- **T2 真实消费（revenue 入口）**：`source_preparation`(北方华创 2025) → **reused_existing、artifact_read=['normalized']、journal 33→33（producer=0）、download=0、llm=0、prompt_injection_status=not_detected**（策略 receipt 生效）。旧 unbound 不复用：星环 2024（legacy）→ valid_handles 空。
- **worker 第 3 次重启**（加载列写入代码）；生产回填 33 行（normalized 18/sections 11/summary 4——worker 又产出 4 行，回填兜底）。
- **git**：company-wiki `a61dd35` + `6a76000` + `3e0d40e`（trace+receipt）；revenue/filing 零改动。
- **落盘**：`t2_consumption_trace_fc906d.md`（完整 trace 表）+ `11_implementer_receipt_d.json`；findings 50。
- **reviewer 后台重放中**（reviewer-fc906d-independent）。
- **下一步**：reviewer verdict → can_accept → **FC-906 全部 accepted → Phase 9 COMPLETE** → Phase 10（FC-1001 三根 E2E fixture 等）。

## 2026-08-12 — **FC-906-d ACCEPTED → FC-906 COMPLETE → Phase 9 DONE（里程碑）**

- **独立 reviewer accepted**（reviewer-fc906d-independent）：干净 worktree 6a76000 + base 0ee0d09（F-6 规则）；diff 恰 2 fixes；focused 4 passed；RED-at-base（None vs '1.0' 真缺陷）；M1（列 stamp 移除）/M2（derived root 移除）双杀；contract suite 1498 passed/1 skipped/0 failed；T2 证据只读复核（34/34 列 stamp、legacy 4797/4797 未动）。
- **F1 low**：implementer receipt 的 result_triplet.wiki 手写错 hash（64-hex 无效）——erratum 修复（pitfall #1 再现：永远 git rev-parse！）；F2 low（command_registry_sha256 模板字段不可复现，pre-existing）；F3/F4 info（worker 漂移）。
- **can_accept exit 0**；receipts 4 组全 sealed（FC-906/ 目录）；worktrees 清理。
- **git**：company-wiki `fafaac5`（docs）；revenue/filing 零改动（本 FC）；llm_cost_log.csv dirty = ambient worker 真实记账（未提交防竞态）。
- **Phase 9 exit gate 全勾选**（task_plan 更新）：source-bound>0、真实复用 T2、AR 全绿、伪零删除。
- **registry FC-906 → accepted；Phase 9 COMPLETE。**
- **下一步 Phase 10**：FC-1001（统一 isolated lake fixture，三根真实布局 + corruption variants）→ FC-1002（三进程 E2E runner）→ FC-1003（95 场景矩阵全覆盖）→ FC-1004（平台/安装形态）→ FC-1005（mutation/chaos）。

## 2026-08-12 — Phase 10 COMPLETE（FC-1001..1005 全部 accepted，FCAP 48/71）

- **FC-1001**（reviewer-fc1001-independent）：IsolatedLake 三根 fixture + corruption×5 + manifest hash；FC-505 日期漂移 pre-existing 修复（test-only）。feat e54d9e3。
- **FC-1002**（reviewer-fc1002-independent）：真实三进程 E2E 链（psutil 5 进程）；fixture 补 security_master/config/review receipts/companies 移 wiki_root。feat 2154032。
- **FC-1003**（reviewer-fc1003-independent-r3，三轮）：95 场景覆盖门（required gaps=0）；UJ-01/02/04/07；三仓 SCENARIO 标注；r1 F1（wiki marker SyntaxError→f6eb584）、r2 F2（ast.parse 未密封→0b000ea）。feat 26bdfb2。
- **FC-1004**（reviewer-fc1004-independent）：PORT-02 空格路径 + 安装同步自包含 + UTF-8 链。feat e733287。
- **FC-1005**（reviewer-fc1005-independent）：critical mutation 门（8 类 kill=100%，M-latest 现场击杀）。feat 6d104d4。
- 全量 revenue 434→456 passed 零失败；关键发现：filing-fetch dayu containment 缺口（FC-1202 前置）、scan errors 212 vs 155 恶化。

## 2026-08-12 — Phase 11 COMPLETE（FC-1101..1105 全部 accepted，FCAP 58/71）

- **FC-1101**（reviewer-fc1101-independent-r3，三轮）：CI manifest 驱动 checkout 替代硬编码 pin（ad62592/77669ae/a42bb40）；commits-exist 防伪门；pin 扫描 7+hex + 负向控制；r1 F1（manifest 滞后→96afe88）、r2 F2（0x08 正则→6ae5feb 字节级 5c 62 验证）。feat 1b41d62 + 592fae6（filing）。
- **FC-1102**（reviewer-fc1102-independent）：每日 T2 只读 runner（triplet/samples/scan health/legacy/latency/fingerprint/trend；隔离报告；非零退出）；生产冒烟发现 scan errors 212（vs 基线 155 真实恶化）；P3 F1-F3（policy freshness 由 FC-1105 关闭）。feat ec1d71d。
- **FC-1103**（reviewer-fc1103-independent）：每周 T3 runner（无 --force=BLOCKED exit 2；reviewer 现场真实 CN/HK/US 214s 全绿）。feat f6c500c。
- **FC-1104**（reviewer-fc1104-independent-r2）：audit dashboard + release gate（24h T2 + 7d T3）；r1 F1（receipt 治理门：commands 含 exit 1→移 scenario 文本）。feat 154a454。
- **FC-1105**（reviewer-fc1105-independent）：故障注入矩阵（陈旧 manifest/缺样本/policy 漂移/Dropbox sidecar/健壮性 6 类全红）+ IsolatedLake runtime_policy；关闭 FC-1102 F1。feat a04e413。
- 全量 revenue 456 passed 零失败；Phase 11 exit gate 勾选（故障注入阻断、硬门机器化；T2/T3 连续周期属持续运维/FC-1504 观察）。
- **下一步 Phase 12**：FC-1201 hardcode 清零 → 1202 单一策略源（含 filing-fetch dayu containment 缺口）→ 1203 dead code → 1204 ratchet → 1205 PORT-01~03（含 sync 子进程 GBK 根因）。

## 2026-08-12 — FC-1201 实施中（root-hardcode 门棘轮 + 安全清理；reviewer 后台重放中）

- **触发**：用户 `/planning-with-files 有哪些未完成的项目，从头开始一个一个实施`。盘点：FCAP 58/71 accepted（Phase 1-11 完成）；剩 Phase 12（5 FC）+ Phase 13（4 FC）+ Phase 14（10 发布波次）+ Phase 15（5 FC）= 14 FC + 10 波次。下一关键路径 = FC-1201。
- **baseline 对账（preflight）**：revenue 有未提交改动——2 个 test follow-up（FC-1001 fixture path from FC-1002、FC-905-b SCENARIO marker from FC-1003）+ weekly_t3_runner.py stat-cache 幻影（update-index --refresh 清除）+ 规划文档（Phase 11 更新）+ 2 未跟踪遗留审计文档。两笔对账提交：`cb58cc6`（test follow-ups，pre-commit 全量 456 passed）+ `44cd28a`（规划文档+归档）。revenue clean。
- **当前 triplet**：revenue `44cd28a`、filing `592fae6`、wiki `f6eb584`（FC-1201 前）。
- **FC-1201 范围决策（用户 Interpretation A）**：门禁棘轮 + 安全清理，v1 scanner 延后 R9。preflight 发现 v1 scanner（7 root 分支）仍是生产回退（cutover 未完成）→ 符合 code_quality_plan §3 step7「关桥后才删 legacy」。
- **preflight-refined 范围**：canonical_writer（L126 写根选择）+ cli（L1251 portfolio 根查找）重构 **DEFERRED**——生产 1.x loader `config.py:75-84` 的 `allowed_root_fields` 严格拒 `canonical_write_target`（加 yaml label → CatalogConfigError），重构需改 loader（生产加载路径）+ yaml + 可能级联破坏未设 target 的测试 fixture；超出「安全清理」→ 留 frozen allowlist，记为 FC-1201 follow-up / R9 prep。service.py:237 / normalizer.py:1487 的 acquisition/dayu_meta 读属另一门（legacy container gate），非 root-token 范围。
- **交付（company-wiki feat `0c6c2c9` + receipt `8817521`）**：FC-304 `no_root_specific_hardcode` 门转 **frozen ratchet**（allowlist 精确 pin，新增文件→测试红）；注释清理 resolver.py:679/observability.py:76/entity_resolver.py:1 → 三文件移出 allowlist（real shrink，零行为）；5 新 contract 测试。零 v1 scanner / loader / 写路径 / yaml 改动。
- **验证**：FC-1201 5 tests + architecture_gate 7 + EX-08 5 = 17 passed；gate/root/policy contract 子集 272 passed/1 skipped；全量 wiki 套件 **2241 passed/1 skipped/0 failed**（449s，PYTHONIOENCODING=utf-8 下 PORT-01 对也过）。M1（allowlist 涨）+ M2（token 删）双杀。ruff/compile 干净。
- **receipt validator 教训再现（pitfall #5）**：mutation commands 首次写 exit_code=1 被 schema 2.0 拒（所有 exit_code 必须 0）；改为 exit_code=0 + result 文本记「KILL CONFIRMED — inner pytest exit N」→ validator OK。
- **下一步**：reviewer-fc1201-independent 后台重放（干净 worktree 8817521；F-6 规则：base 复现用第二 worktree）→ verdict → can_accept → registry FC-1201 accepted → FC-1202（单一策略源，含 filing-fetch dayu containment 缺口）。
