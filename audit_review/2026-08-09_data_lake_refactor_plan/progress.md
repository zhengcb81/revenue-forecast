# 多根 Filing Data Lake 改进计划 — 规划进度

## 2026-08-09

- 已完整读取 `planning-with-files/SKILL.md`。
- 已建立独立三文件工作区，避免把新架构计划混入已发生实施漂移的旧审查计划。
- 当前仅开展计划编制；未修改产品代码、配置、测试、生产 catalog 或真实资产。
- 当前阶段：Phase 0，细化目标、工作包、测试矩阵、弱模型执行闸门和审计回执。
- 已对照旧计划的执行协议、目标契约、37 个场景和最终验收门；决定继承证据状态机/latest/artifact 合同，废止已被证伪的 Dropbox config-only/runtime-diff=0 前提。
- 用 CodeGraph 与现存 SKILL.md 复核 revenue 侧生产调用链：resolve_filing 只有 CLI/测试调用者，build_revenue_source_record 与 select_reusable_artifacts 只有测试调用者；已记为 D-009。
- 明确真实 Dropbox canary 的证据边界：fixture 只能证明实现行为，不能替代真实根目录中合格样本的生产验收。
- 记录工具错误：不存在的 README.md 路径，以及两次未应用的计划补丁；没有产品文件受到修改。
- 已盘点三仓现有实现与测试落点；计划将以演进 source_catalog、filing-fetch 主脚本、revenue source client 为主，禁止另起不接生产调用链的平行 helper。
- 已完成计划主体初稿：64 个工作单标题、72 个表格化对抗场景、跨进程 E2E/真实 canary 分层、20 步弱模型协议。
- 第一次计划自审发现若干 Phase 放行门标题格式不统一；将在最终冻结前统一并加机器检查。
- 已复核三仓状态：本轮未改 filing-fetch 产品文件；company-wiki 仅显示既有用户文件状态；revenue 仅 planning/audit 文档有改动。
- 开始收敛 WU-400 的 schema owner 决策：CodeGraph 已确认 CatalogStore/EvidenceSpan 基础，但 assertion service 符号解析不足，需对指定源码做一次目标只读检查后冻结选择。
- 已读取现有 assertion 表和 service：其字段、candidate/verified/rejected 与 supersession 语义足以演进；计划冻结为扩展现表而非新建第二真相源。
- 第二次计划自审当时发现 Phase 15 标题格式不统一；现已修正为 15/15，WU ID 无重复，未发现遗留开放选择。
- 已重读旧审查 F-034~F-060，确认新计划覆盖 semantic ingest、adapter、resolver、retire、URL binding、entity、artifact 主链和测试真实性。
- 已补齐 F-034~F-060 共 27 条逐项实施映射。
- 最终结构自审得到：Phase 1~15 各有一个显式放行门，64 个 WU，Phase 12 有 72 个表格化场景，WU ID 无重复。
- 自审命令有一次参数错误：把三个路径以逗号拼成 rg 的单一路径；不影响此前成功的计数，已记录并改用逐路径参数重跑。
- 计划编制已完成，等待用户审阅；没有开始任何产品实施。
- 最终机器检查：三个 planning 文件存在；15 个唯一 Phase 放行门；64 个 WU；Phase 12 共 72 个场景；F-034~F-060 共 27 条逐项映射；无重复 WU。
- 开放标记搜索最后仅命中一条禁止性说明，已改写以消除自动检查误报。

## 2026-08-09 — 全面重构安全补充

- 用户明确表示必要时可以全面重构，要求设计渐进、安全、测试检查点充分的步骤。
- 已重新完整读取 planning-with-files 技能并复核当前 task_plan 的目标、状态机与 15 个阶段。
- 当前计划的技术范围已经是 semantic ingest/consumer 全链重构；本轮将补齐显式 strangler 波次、characterization、per-root/per-consumer cutover、stop/rollback 和临时桥退役约束。
- 本轮仍只更新 planning Markdown，不实施代码或配置。
- 已加入 0.7~0.11：全面重构边界、R0~R11 strangler 波次、CP0~CP8 切片检查点、stop-the-line/自动回退、临时兼容层债务预算。
- 一次跨 Phase 5~10 的大补丁因 Phase 6 上下文文本与实际文件不完全一致而未应用；改为读取精确区段后分阶段小补丁，未修改任何产品文件。
- 已新增 WU-500/604/806/906/1005：零行为 seam、逐 root ingest、逐 root resolver、迁移破坏恢复、逐 consumer 协议切换。
- 已新增 RF-01~12 重构专项场景、WU-1406 波次控制器和 WU-1500“先禁用观察、再删除 legacy”门。
- 计划结构复核：新增后为 74 个 WU、15 个唯一 Phase 门、72 个原业务场景 + 12 个重构切换场景，无重复 WU。
- 发现并补上 shadow assertion 的关键隔离：证据 verified 与 reader visibility 必须分离，避免 v2 数据在切 resolver 前被 v1 提前读到。
- 已补充三仓 expand→migrate→contract 演进纪律；生产者、消费者、迁移 apply、reader cutover、legacy 删除均为独立可回退事件。
- 最终自审：三个 planning 文件存在，15 个唯一 Phase 放行门，74 个 WU，72 个业务场景 + 12 个重构切换场景，27 条 finding 映射，无重复 WU、无开放占位项。
- filing-fetch 仍无工作区改动；company-wiki 只显示既有 llm_cost_log.csv 与 source_manifests/archive 状态；本轮未触碰产品文件。
- 全面重构安全计划修订完成，等待用户审阅；未开始实施。

## 2026-08-09 — 弱模型逐工作单收敛

- 用户再次要求依据最新计划形成弱模型也不易跑偏的完整实施计划；本轮仍只做计划。
- 已重新完整读取 planning-with-files 技能并复核 task_plan/progress。
- 自动审计 74 个 WU 的局部字段，发现多数工作单依赖全局规则表达 rollback/test；决定增加逐 WU implementation runbook，避免模型只读局部时漏门。
- 首次创建 runbook 的补丁因 Markdown 反引号与 JavaScript 模板字符串冲突而未执行；改用无反引号补丁，不重复失败形式。
- 已读取三仓当前 CI/pytest 配置与现有 tools/e2e 入口；确认它们可做基线，但 filing 排除真实工具/下载、company 未覆盖完整 integration/acceptance、现有 E2E 不等于本次三仓 source-preparation E2E。
- 已完成74张逐WU卡片；机器核对task_plan/runbook集合一致、无重复/缺卡，七字段全部非空。
- 已冻结当前/目标测试命令alias、Phase文件边界、永久禁区、七类reviewer和九类证据目录。
- 最终机器自审通过：4个planning文件、74/74卡、七字段完整、15个唯一Phase门、72+12场景、27条finding映射、无开放占位项。
- 三个产品仓最终status均无本轮改动；本次仅修改该planning目录的四个Markdown文件。
- runbook完整性validator已明确归入WU-103的RED/mutation/Phase 1门。
