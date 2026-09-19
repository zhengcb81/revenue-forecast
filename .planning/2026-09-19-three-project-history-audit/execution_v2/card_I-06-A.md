本卡由[wiki_cards.md](wiki_cards.md)原文抽取。先读[执行协议](START_HERE.md)、[wiki_cards.md共用规则](common_wiki_cards.md)和[独立验收](review_and_handoff.md)；不需要读取全册。状态planned，运行cwd必须由I-00-B绑定。

### I-06-A — 安全阻断前登记可持久恢复的需求

parent：I-06；status：planned；owner：wiki 持久需求 owner；RF 消费实施者。

依赖：I-02-E。设计前置：D-W06。证据目录：`execution_runs/I-06-A/<attempt-id>/`。

**当前源码锚点（只读核查）**

- [revenue-forecast/scripts/source_preparation.py:31](<C:/Users/郑曾波/Projects/revenue-forecast/scripts/source_preparation.py:31>) `_preparation_demands / _submit_preparation_demand / prepare_source`：module 全局内存队列；not_reviewed 在 _submit 前 raise。 SHA256 `5ec16eaf0fe480126b680f6e069717ebfc218ae39531372a380cfcc9b91bce46`。
- [revenue-forecast/scripts/processing_demand.py:47](<C:/Users/郑曾波/Projects/revenue-forecast/scripts/processing_demand.py:47>) `DemandQueue`：独立内存实现，不能跨进程完成。 SHA256 `fcdfcad8ebd1fc20febf3c157dcd20ad92708fd69d00373ef9a943e5a820afc1`。
- [company-wiki/src/company_wiki/source_catalog/processing_demand.py:67](<C:/Users/郑曾波/Projects/company-wiki/src/company_wiki/source_catalog/processing_demand.py:67>) `DemandQueue`：wiki 也纯内存；现有测试证实状态语义，未实现持久调度。 SHA256 `90f232edb7804f78a16c6b4e865255cd607a1d0dc30384fc1cd6faa1833ac88b`。

**必读原证据**

- [audit_review/2026-09-18_real_company_skill_audit/runs/02_zijin_source_reuse/run.json](<C:/Users/郑曾波/Projects/revenue-forecast/audit_review/2026-09-18_real_company_skill_audit/runs/02_zijin_source_reuse/run.json>)： 第一次 not_reviewed 合理阻断，但不可恢复路径未完成
- [../company-wiki/tests/contract/test_zr507_processing_demand.py](<C:/Users/郑曾波/Projects/company-wiki/tests/contract/test_zr507_processing_demand.py>)： 纯内存 lease/retry/terminal 合同
- [scripts/source_preparation.py](<C:/Users/郑曾波/Projects/revenue-forecast/scripts/source_preparation.py>)： 从真实 CLI 返回到安全拒绝/提交的顺序

**只允许修改**

- RF:scripts/source_preparation.py
- RF:scripts/processing_demand.py（改为获准单 owner 适配，不增第二持久实现）
- CW:src/company_wiki/source_catalog/processing_demand.py
- D-W06 明确列出的 store/migration/CLI adapter 文件；未冻结具体文件禁止猜建
- 对应隔离跨进程测试

**固定样本**

- 新样本不含人工 review；相同原 request 两个独立进程调用；第三次变化 source hash 或 review policy。
- request 缺身份/非法参数与合格 source 尚未 review 分开：垃圾输入不可无限建任务。

**独立预期：在修改前冻结，不调用被测函数生成 expected**

- **W06A-P1 / positive**：合格来源但 not_reviewed，从实际 source-preparation CLI 发起。
  预期：在返回明确阻断前持久需求存在；包含 source/hash/policy、缺口、原请求绑定、下一动作；没有伪造 review。
- **W06A-P2 / positive**：退出进程后第二进程重提完全相同需求。
  预期：同一 active demand ID 可读且只有一项待办；不是每进程 pd-0 伪同一。
- **W06A-N1 / negative**：source/hash/policy 或请求角色集合改变。
  预期：旧完成回执不得关掉新需求；按冻结键新建或可审计版本化。
- **W06A-N2 / negative**：持久 DB 写失败/数据非法/权限不足。
  预期：不报告 demand_queued；原安全门保持，给结构化失败；不得 silently fallback 内存。
- **W06A-N3 / negative**：worker 处于 paused。
  预期：登记/查询不自动 resume 或启动后台；显式一次消费权限另由 D-W06 定义。

**按序执行**

1. D-W06 先指定单一持久 owner 与迁移及 API；没有 schema 不能让执行者自行选 SQLite/文件队列。
2. 保留现有纯队列的状态单测，新增跨进程登记查询作为独立 oracle。
3. 将合法需求登记移到安全阻断之前，确保失败顺序可观测；不修改安全 verdict。
4. 新进程确认需求存在；重复、变更、DB 失败、paused 分别验证。

**失败停止与恢复界限**

- 发现现有自然 worker 自动扫/消费新增需求，暂停本次隔离测试查明配置，不触碰真实 control。
- 迁移失败保留副本和 journal；仅恢复隔离数据库快照，不删除生产 pending。

入口：`CMD-W08`、`CMD-W05`。新案例尚无现成 nodeid 时，由 I-00-B 在批准实现后补绑定，不发明 CLI。

共同证据外还须保存：`demand.cross-process.json`、`request-to-demand-binding.json`、`paused-before-after.json`。

**退出判据**：阻断产生可见持久需求和下一动作；本卡只证明登记可恢复，不声称已完成审核/补产。
