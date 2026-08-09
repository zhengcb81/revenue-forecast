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
