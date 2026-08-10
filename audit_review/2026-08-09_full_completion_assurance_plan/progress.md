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
