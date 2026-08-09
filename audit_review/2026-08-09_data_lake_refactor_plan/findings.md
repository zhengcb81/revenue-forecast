# 多根 Filing Data Lake 改进计划 — 设计依据与决策台账

## 证据来源

- 当前代码与 CodeGraph：三仓 2026-08-09 HEAD。
- 生产 catalog：只读 SQLite 查询；未触发扫描或写入。
- 前序审查：`audit_review/2026-08-08_adversarial_plan/findings.md` F-001~F-060。

## 已冻结的核心判断

### D-001：物理数据湖保留，语义摄取层重构

- `roots/sources/documents/locations/artifacts/evidence`、内容寻址和多 location 是可复用基础。
- 重构重点为 scanner adapter、normalized metadata、resolver、SourceBundle 主链。

### D-002：配置-only 是目标能力，不是当前事实

- 当前两侧 Dropbox 配置已开启仍不可复用，证明当前 config-only 不成立。
- 目标状态为：新 root 若使用已注册且兼容的 adapter/profile，只需增加 root-id 级配置；新增一种未知 layout/schema 仍需实现并审核 adapter。

### D-003：安全门与来源适配必须分离

- identity/provenance/status/hash/as-of/path fence 属于统一安全合同。
- root-specific layout、sidecar、provider 字段映射属于 adapter。
- resolver 不得按 root 名称或来源容器分支。

### D-004：战术 Dropbox 特例不得冒充最终完成

- 仅把 directory metadata 写入 `acquisition` 可以作为 RED 诊断或短期兼容桥，但不能作为 Phase 7/8 完成证据。

### D-005：processed artifact 必须通过真实主链复用

- helper、表和 fixture E2E 不等于产品功能。
- 必须由 company-wiki resolve 组装 SourceBundle，filing-fetch 保真转发，revenue 生产入口实际消费。

## 已冻结的原待决事项

- normalized metadata：扩展现有 source_metadata_assertions 为唯一 v2 ledger，字段与 evidence/binding 见 WU-202/400。
- adapter registry：静态受审注册表；配置只引用 ID/version/profile，不动态导入任意代码。
- legacy bridge：仅迁移 shadow 窗口使用；v2 active 且连续两个验证周期 bridge_hits=0 后退役。
- 真实 Dropbox canary：只使用已经存在且 provenance 完整的候选；无合格样本时显式 blocked，不修改真实 sidecar 伪造证据。

## 旧计划可继承与必须废止的部分

### D-006：继承证据状态机，不继承 config-only 结论

- 继承旧计划的 WU 状态机、机器可读回执、文件 allowlist、RED/mutation/reviewer、真实根只读保护、测试 collection/coverage 禁降级。
- 旧 §2.4/Phase 2A“Dropbox runtime diff=0 即可启用”已被当前 probe 和生产配置证伪，标记为 `superseded`；不得继续作为实施约束。

### D-007：继承 latest/gap 和 artifact validator，补齐未接主链部分

- latest/gap、active-only resolver、SQL pushdown、ArtifactHandle/SourceBundle helper 已有实现与测试，计划必须先做 drift audit，禁止重写一套。
- SourceBundle query/selector 没有产品调用者，新的计划应以“垂直主链接入”为工作单元，而不是再次新增 helper。

### D-008：旧 E2E ID 可复用语义，但必须纠正伪 E2E

- 保留 R/L/D/F/DBX 场景意图。
- 所有标为跨仓 E2E 的场景必须经过真实子进程边界和实际生产入口；直接构造 handle/bundle 只能命名为 contract/component test。

### D-009：当前不存在真正接通的跨仓生产编排链

- revenue-forecast 的 resolve_filing 当前只有 CLI main 与测试调用者。
- build_revenue_source_record、select_reusable_artifacts 当前也只有测试调用者。
- scripts/revenue_forecast.py 是纯计算/校验 CLI，不是采集、解析与工件复用的生产编排器。
- 当前实际工作流主要由 SKILL.md 指示模型/操作者先调用 filing-fetch，再手工把结果传给 revenue source record；这不是可由端到端测试完整约束的产品调用链。
- 因此不能把“若干 helper 已存在且测试通过”等同于 SourceBundle、处理工件复用已经在实际使用中生效。

**规划约束：** 必须先用 ADR 冻结唯一的生产集成边界，再写跨进程 RED 测试。不得把 I/O 偷塞进纯计算的 revenue_forecast.py；推荐新增显式的 source-preparation 编排入口，并让技能文档只调用该入口。

### D-010：不能假定当前 Dropbox 已有可直接用于最终验收的合格样本

- 当前审查只证明 Dropbox 中存在大量已索引文档；没有证明存在一个“仅 Dropbox 命中、active、官方财报、来源字段齐全、可复用”的真实样本。
- 真实验收不得伪造生产证据，也不得为了让测试通过而未经授权修改 Dropbox 文件或 sidecar。

**规划约束：** 把“只读发现 canary”和“获批后的迁移/恢复 canary”分开；如果真实根目录没有满足前置条件的样本，最终生产 canary 必须明确标记为阻塞，不能用 hermetic fixture 冒充。

### D-011：配置驱动不等于从配置动态导入任意代码

- 用户要求同类已索引目录能够通过配置接入，但任意 Python import/class path 会扩大供应链和本地代码执行面。
- 泛化点应是受版本管理的 adapter/profile 注册表；配置只选择已审核的 adapter、路由与安全策略。

**规划约束：** 未注册 adapter、未知 schema version、未知 admission profile 必须 fail closed；新增 adapter 仍需代码和 conformance suite，而使用已有 adapter 接入新的同构根目录才应做到配置化。

### D-012：最近两次计划工具错误

- 一次组合检索引用了不存在的 README.md，命令返回路径错误；有效证据来自现存 SKILL.md、源码和 CodeGraph。
- 两次计划补丁未应用：第一次是 Markdown 反引号与 JavaScript 模板字符串冲突，第二次是预期标题文本不匹配。
- 上述失败均未修改产品文件。

**处理：** 不重复失败命令；后续只引用存在的路径，先读取精确标题再补丁，并使用无反引号的补丁载荷。

### D-013：实现落点应复用现有模块，不再建立第四套平行框架

- company-wiki 已有 source_catalog/config.py、scanner.py、models.py、normalizer.py、admission.py、resolver.py、source_bundle.py、gap_plan.py、artifact_handle.py、assertion_service.py、architecture_gate.py、store.py 与大量 contract tests。
- filing-fetch 的主要边界集中在 scripts/fetch_filing.py、scripts/filing_contracts.py 及现有 latest/bundle/E2E tests。
- revenue-forecast 已有 scripts/filing_fetch_client.py、scripts/company_wiki_source.py、contracts 与 bundle/artifact tests，但缺显式生产编排入口。

**规划约束：** 每个工作单必须先标明复用或演进哪个现有模块；创建新模块需要 ADR 证明现有职责不适合，并由 architecture gate 防止出现 legacy/new/temporary 三条长期并行路径。

### D-018：用户明确接受必要的全面重构，安全性优先于 diff 大小

- 现计划已覆盖 RootPolicy、adapter SPI、normalized assertions、resolver、SourceBundle 和三仓生产编排，实质上已是对 semantic ingest/consumption 的系统重构，而非 Dropbox 局部补丁。
- 仍需把隐含的安全策略显式化：旧链冻结、v2 strangler、characterization、shadow、逐 root 切换、逐 consumer 切换、自动回退、旧链最后退役。
- “渐进”不能退化成长期双实现；每个兼容桥必须有 owner、指标、截止门和删除条件。
- “全面”也不等于重写正确的物理 catalog、安全门、latest/gap 和 artifact validator；重构边界应由 F-058/F-059 约束。

**冻结方向：** 对 company-wiki semantic ingest 到三仓消费边界进行完整但分波次的替换；保留验证正确的物理存储与安全不变量。计划新增重构安全主干、切片模板、stop-the-line 条件、逐 root/逐 consumer 切换和清理门。

### D-019：全面重构的主要风险不是改动量，而是同时改变多个 seam

- 将旧函数搬到 facade、改变 metadata schema、切 resolver、迁移 catalog、切 consumer 若混在一个提交，即使总测试绿色也难以定位回归和可靠回滚。
- 机械移动与语义修复必须分开：seam 提交先证明零行为变化；known-bad 修复单独 RED；清理又是独立可 revert 提交。
- active v2 出错后若同一请求 silent fallback 到 v1，会让指标看似正常并掩盖新链缺陷；应 fail closed、记录 incident，再对后续请求显式切 cohort flag。
- legacy 源码应先 disabled 观察两个验证周期，再分层删除；不可一切 v2 就立即删。

**规划落实：** WU-500、604、806、906、1005、1406、1500 与 RF-01~12 分别固化 seam、逐 root、逐 resolver、迁移恢复、逐 consumer、波次控制和延迟删除。

### D-020：v2 assertion 必须把“可信”与“对 reader 可见”分开

- 现有 decision=candidate/verified/rejected 表示证据审核状态，不足以安全表达 shadow/canary/active rollout。
- 若 v2 verified row 在 resolver 切换前就能被 v1 查询读到，所谓 shadow write 会提前改变生产行为。

**冻结决策：** v2 assertion 增加独立 visibility_state/activation_epoch/cohort；R5 可 verified 但保持 shadow，v1 reader 在任何 v2 verified 写入前先固定只读 v1 schema/legacy facts，v2 resolver 只读当前请求 snapshot 中 active epoch。激活/回退是小事务状态切换，不删除 assertions。

### D-021：全局规则不足以约束只读取单个 WU 的弱模型

- 自动扫描 74 个 WU 正文后，许多工作单依赖全局 0.3/0.4/0.5 才具备 rollback、mutation 或测试要求；并非每段都显式重复。
- 强模型通常会继承全局约束，但弱模型可能只截取自己的 WU，遗漏基线命令、允许文件、RED、mutation、回滚或 reviewer。

**冻结决策：** 新增 implementation_runbook.md，给 74 个 WU 每项一张实施卡索引；卡片明确 owner/目标文件、输入、RED/focused gate、mutation、审计证据、回滚与放行。task_plan 将把“卡片存在且 schema 完整”设为启动前置。

### D-022：现有 CI 可作为基线，不能直接充当新重构的完整验收门

- company-wiki 当前 CI 跑 Ruff、compileall/config doctor、unit、contract、少量 mutation canary；未把 integration/acceptance 和新的跨仓 E2E 作为同一必过门。
- filing-fetch 当前 hermetic suite 明确排除 real_tool_conformance 和 e2e_download；其 companies-reuse-only E2E 不覆盖 dayu/Dropbox/latest/artifact consumer。
- revenue-forecast 当前 CI 已包含 Ruff、全测试、coverage gates、engine E2E、sync、mutation patrol、publication/plan/ledger，但 engine E2E 不是本次 source-preparation 三仓 E2E。
- company-wiki 在 Python 3.11/3.12/3.13 矩阵运行；filing/revenue 当前主要为 3.12。

**规划约束：** runbook 同时保存 current baseline aliases 与 target gates。被当前 CI 排除的测试必须在对应 WU/发布门显式运行；不能用“CI 绿色”宣称真实下载、跨根或跨仓闭环已验证。

### D-023：逐 WU runbook 已达到结构完整

- task_plan 与 runbook 均为 74 个 WU，集合完全一致，无重复、无缺卡、无额外卡。
- 74 张卡的 Owner/Targets、Inputs、RED/Focused、Mutation、Audit、Rollback、Accept 七字段均非空。
- runbook 状态已改为 complete-ready-for-review，并已补充统一文件边界、七类审查角色、九类证据目录和当前/目标命令 alias。
- 完整性 validator 归入 WU-103；未来删卡、重复 ID、空字段、计划版本漂移都必须使 Phase 1 失败。

### D-014：计划自身第一次对抗检查结果

- 当前 task_plan 已包含 64 个 WU 标题和 72 个表格场景。
- 未发现真实遗留占位事项；搜索命中仅来自放行门的禁止性文字。
- 发现 Phase 3/4/6/7/8/9/11/13/14 的退出条件虽已有正文，但标题格式不统一；需要统一成显式 Phase X 放行门，便于机器检查。
- revenue 当前改动仅为旧/new audit_review 计划文件；filing-fetch 无改动；company-wiki 的 llm_cost_log.csv 与 source_manifests/archive 是既有用户状态，本轮未触碰。

**规划约束：** 最终计划审计必须数出 Phase 1~15 各一个显式放行门，且产品仓状态与本轮授权一致。

### D-015：normalized schema owner 仍需以现有表能力作最终选择

- CodeGraph 确认 CatalogStore 是 catalog schema/transaction 中心，现有 source_contract EvidenceSpan 具备不可变 source binding 与 canonical hash 约束。
- CodeGraph 未解析出 AssertionService/upsert symbol，只通过 focus cleanup 证明 source_metadata_assertions 是 document child table；仅凭当前图结果不足以决定“扩展旧表”还是“新建 v2 表”。

**处理完成：** 已目标读取 assertion_service.py 与 store.py，并在 D-016 冻结单一方案；不把 schema owner 选择留给实施模型。

### D-016：冻结 schema owner——演进现有 source_metadata_assertions

- 现表已经包含 assertion_id、source/document/content 绑定、entity/market/security、kind/form/period、provider/document ID/URL/date、evidence_json、decision、supersession、schema_version。
- assertion_service 已有 candidate → verified/rejected 的不可变追加与冲突 fail-closed 语义；resolver 已把 verified assertion 作为身份恢复来源。
- 因而新建第二个 writable v2 assertion 表会制造双真相源和迁移期外的长期复杂度。

**冻结决策：** 现有 source_metadata_assertions 作为唯一 normalized assertion ledger；用 additive columns/indexes 与 v2 evidence_json schema 演进，v1 行不原地覆盖，新事实以 v2 assertion/supersession 追加。raw adapter metadata 继续保留但 resolver 不读。

### D-017：旧审查的核心风险均可映射到当前阶段

- F-034/F-036/F-038/F-060 的 semantic data lake 缺口由 Phase 2~8 覆盖。
- F-037/F-046/F-056/F-059 的 scanner/source profile 硬编码由 Phase 3/5/6/7/15 覆盖。
- F-047/F-048/F-049 的矛盾测试与伪绿色由 Phase 1/12/14/15 覆盖。
- F-050/F-051 的 artifact 孤岛由 Phase 10/12/13 覆盖。
- F-052/F-054 的 URL 错绑由 WU-403、N-06 和定向 mutation 覆盖。
- F-053 的 company_raw 实体依赖由 WU-703/N-04/N-05 覆盖。
- F-055 的 retired 终态由 Phase 9/M-02/03/06/07 覆盖。
- F-057 的 gap 输入集合问题由 Phase 8/11 覆盖。
- F-058 的良好物理 catalog 基础被明确保留，不进行无谓重写。

**完成情况：** task_plan.md 的 0.6 已添加 F-034~F-060 共 27 条逐项 owner/test/关闭条件映射。
