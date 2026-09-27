# 与 revenue-forecast 三项目大计划的交叉及执行门禁

> 2026-09-27 只读刷新：读取 revenue-forecast `.planning/2026-09-19-three-project-history-audit/progress.md`（Round 120）、`REMEDIATION_REGISTER.md`（§161）、`OWNER_DECISIONS.md`（§38）、I-05-C/I-06-A 执行卡与当前 attempt 收据。本文件只记录本方案的协调规则；未改对方计划、卡片、状态或产品文件。每次 G0 前重查源文件和卡级最新状态。

## 已确认的交叉范围

| 工作 | 与本方案的关系 | 当前处理 |
|---|---|---|
| revenue I-11-B 收入参数幅度/联合情景校准 | 现行卡主体是收入预测研究证据和情景；不需要改本轮 F0–F2 的 SQLite 文件替换工具 | 可继续；本轮 `prepared.json` 只证明旧 DB 与候选/备份，不宣称对方计划通过 |
| revenue I-05-C 按需求最小补产 | 执行卡 header 仍为 `planned`；盘上 attempt 有 `accepted_scoped`，但 review 仍携带 GAP-1 真实 producer 尚未实施、GAP-2 RF `consumer_analysis` owner/入口待给、GAP-3 InvocationTracker 事件 schema 待 reviewer 批准；`consumer_analysis` 不得用 mock 冒充真实能力 | 与未来 W0–W6 的 producer/role/event 直接重叠。G0 前不接共享目录/producer；G0 要核真实 owner、角色定义、D-W05 活动 DAG、事件字段/版本和复用行为，不只看 `accepted_scoped` 标签 |
| revenue I-06-A 持久需求/幂等键 | 执行卡 header 仍为 `planned`；最新 `a20260922-02` 有 `accepted_scoped`，但 reviewer 范围只含 store-side lifecycle；RF caller wiring、CLI c8/c9/c10、跨进程 claim、OPEN-4/6 runtime probe、I-06-B consumption face 等仍为 carried-open，生产晋升还需 owner commit | 不再把它笼统描述为“D-W06 全部未决定”。具体的剩余调用/消费/并发语义仍与 Worker claim、重试、崩溃恢复重叠；G0 前不写第二套队列或 schema，须对照正式 accepted scope 与剩余 contract 核定唯一 job owner/API |
| filing-fetch → company-wiki `resolve` → revenue-forecast | 依赖本仓 `SourceResolver`、`SourceCatalog.query`、来源身份、根策略及原文路径；StockWiki company-wiki provider 目前 disabled | F3 用旧/候选的相同配置做 no-download resolve 与 metadata query 差分；F4/F5 前重核消费入口 SHA。StockWiki 启用前另测导出合同 |
| 其他 agent 往 company-wiki raw 写 Microsoft 8-K 文件/sidecar、紫金 AR2023 PDF/sidecar | 2026-09-27 D0 发现 5 个近新增文件，合计 16,120,320 B，均尚未登记到 catalog locations；原文添加不会自动更新 catalog，但若擅自 scan/normalize 会改变生产 DB/WAL，并可能干扰对方材料登记 | D0 仅 stat 与确切路径只读查询；这些路径保持 `hold`，不删、不移动、不扫描、不 normalize。待材料 owner 完成当前工作并确认登记状态，再由 G0/相应卡决定如何接入 |

## 本轮硬门禁与责任边界

1. F3 `consumer_audit.json` 冻结本仓配置与 14 个核心源码文件（包含 `artifact_dag.py`、`service.py`、`processing_demand.py`、`store.py`）及 StockWiki 配置、filing-fetch/RF 入口的 SHA。F4、两次烟测和 F5 逐项重核；任何另一任务落地代码都会阻止旧库删除，先重新审计或重新准备。旧库的 SHA/WAL 变化则必须重新准备，因为候选数据已过时。
2. F0–F5 只替换 `.source_catalog/catalog.sqlite3` 为“所有非 span 行 + active 旧 span”的等 schema 库，并保留完整压缩旧库；不修改 I-05-C/I-06-A 的产品文件、源原文、DAG、Worker、对方 PWF 或跨仓数据库。`catalog_meta` 的 active-only 标记仅驱动缺失旧证据的归档错误，不是投资研究状态。
3. 在 F5 前，旧物理 DB 保持可按 `cutover-intent.json` 精确切回。若别的 agent 的迁移先落生产，F4/F5 暂停，重新检查 schema/索引/表行摘要、消费者返回值及恢复路径。不能把其模型/卡片历史 accepted 当作新 DB 可用性的证明。
4. W0 冻结新的 `NarrativeEvidencePackage/v1` 前，先与 I-05-C/06-A 的**最新正式产品合同**作角色映射：来源包 = 上游非投资资料投影；`summary`/`sections` 复用或升级现有 producer，`consumer_analysis` 归下游；确定唯一 job owner、请求身份、attempt/outbox、缓存失效和版本 pin。若对方尚在候选/blocked，W0 只在隔离夹具做评估，不自行把候选提升为生产规范。
5. 两边各写各自仓库/计划，跨仓只通过版本化只读 export/ID/hash；不复用共享可变 SQLite，也不修改对方正在进行的 PWF 状态。本方案发现契约冲突时留下精确文件/hash/返回值并停在相应门禁，不以“计划互不冲突”的笼统判断放行。

## 目前结论

**Phase 17 F0–F5 已结束；G1 目前完成的仍是隔离离线试点**：v16 主样本 1,289/1,289 locator 回读、18/18 锚点通过，v11 回归集 401/401 回读、5/5 锚点通过；13 条来源摘要草稿通过机械引用/角色检查并经实施者核源，但保持 `needs_review`。没有改 revenue-forecast、StockWiki、invest-quick-scan 或 company-wiki 共享 DAG/store/service/producer/processing_demand/Worker。

**G0 当前不放行共享集成**。Revenue-forecast 最新可见计划到 Round 120 / register §161：I-05-C 的盘上 `accepted_scoped` 不抹去 review 携带的真实 producer、`consumer_analysis` owner/入口和 InvocationTracker 事件 schema 开放项；I-06-A 的后续 `accepted_scoped` 只覆盖 store-side lifecycle，caller/CLI、跨进程 claim 与 I-06-B consumption face 等仍在 carried-open，生产晋升另需 owner commit。故本专题不接 export/检索、共享 producer/DAG/store/Worker，也不写对方计划。G0 要按卡级最新正式裁定冻结唯一 source producer、持久 job owner、请求/attempt 身份、事件/schema/API 和消费端映射；状态标签本身不足以放行。

## F 阶段执行后的核对与后续节奏

2026-09-26 的 F3 对 18 个本仓/跨仓合同文件冻结 SHA，6 组 query 与 12 组 no-download resolve 的旧/新库响应一致；F4 两轮生产烟测和 F5 前重核合同文件未变化。F5 19:06:54 UTC 已删除精确旧库，保留新库与完整备份，Worker 继续 paused。此结论只覆盖已审计的读接口，不代表 revenue-forecast 全业务预测、StockWiki consumer 或 invest-quick-scan 已完成端到端回归。

后续改用 [G0–G4 大节点审查](milestone_review_cadence.md)：G0 一次核 I-05-C/I-06-A 最新正式产品合同与 job owner，G2 仅在新 export/检索合同变动时让受影响消费者跑一次只读夹具，G3 复用 R4/v5 对基础 Worker 的已通过收据。不因对方 PWF 文字更新重做全库哈希；实际共享代码、schema、来源身份或消费者行为改变才重开受影响节点。
