# 与 revenue-forecast 三项目大计划的交叉及执行门禁

> 2026-09-26 只读检查其 `.planning/2026-09-19-three-project-history-audit/` 的 `task_plan.md`、`progress.md`（最新可见 Round 117）、`execution_v2/card_I-05-C.md`、`card_I-11-B.md` 以及本仓现状。本文件只记录本方案的协调规则；不改对方计划、卡片、状态或产品文件。其他 agent 之后的实际进度可能变化，每次 W0/F4/F5 前重查真实输入。

## 已确认的交叉范围

| 工作 | 与本方案的关系 | 当前处理 |
|---|---|---|
| revenue I-11-B 收入参数幅度/联合情景校准 | 现行卡主体是收入预测研究证据和情景；不需要改本轮 F0–F2 的 SQLite 文件替换工具 | 可继续；本轮 `prepared.json` 只证明旧 DB 与候选/备份，不宣称对方计划通过 |
| revenue I-05-C 按需求最小补产 | 明列 CW `artifact_dag.py`、`service.py`、`processing_demand.py` 为可修改范围，涉及 normalize/sections/summary/consumer_analysis 角色 | 与未来 W0–W6 直接重叠。W0 必须读取其最新 D-W05 活动 DAG、producer 入口、事件和版本裁定；共用一个 producer/任务所有权，不另造平行角色或全量补产路径 |
| revenue I-06-A 持久需求/幂等键 | rev2 候选拟按 CW `store.py` additive migration 形状落库，仍有上游决定/签收门 | 与未来并发 Worker 的 job claim、重试、崩溃恢复重叠。W6 不抢先写第二套队列或 schema；先核其正式裁定与实际产品落点 |
| filing-fetch → company-wiki `resolve` → revenue-forecast | 依赖本仓 `SourceResolver`、`SourceCatalog.query`、来源身份、根策略及原文路径；StockWiki company-wiki provider 目前 disabled | F3 用旧/候选的相同配置做 no-download resolve 与 metadata query 差分；F4/F5 前重核消费入口 SHA。StockWiki 启用前另测导出合同 |
| 其他 agent 往 company-wiki raw 写 Microsoft 8-K 文件/sidecar | 原文文件添加不会修改已冻结 SQLite；但若随即 scan/normalize，会改变旧 DB 或 WAL | F0–F3 期间保留操作锁和源 DB SHA/stat/WAL 检查。F4/F5 若旧 DB 有变化必须停止、重新准备，不把新 raw 静默漏进切换快照 |

## 本轮硬门禁与责任边界

1. F3 `consumer_audit.json` 冻结本仓配置与 14 个核心源码文件（包含 `artifact_dag.py`、`service.py`、`processing_demand.py`、`store.py`）及 StockWiki 配置、filing-fetch/RF 入口的 SHA。F4、两次烟测和 F5 逐项重核；任何另一任务落地代码都会阻止旧库删除，先重新审计或重新准备。旧库的 SHA/WAL 变化则必须重新准备，因为候选数据已过时。
2. F0–F5 只替换 `.source_catalog/catalog.sqlite3` 为“所有非 span 行 + active 旧 span”的等 schema 库，并保留完整压缩旧库；不修改 I-05-C/I-06-A 的产品文件、源原文、DAG、Worker、对方 PWF 或跨仓数据库。`catalog_meta` 的 active-only 标记仅驱动缺失旧证据的归档错误，不是投资研究状态。
3. 在 F5 前，旧物理 DB 保持可按 `cutover-intent.json` 精确切回。若别的 agent 的迁移先落生产，F4/F5 暂停，重新检查 schema/索引/表行摘要、消费者返回值及恢复路径。不能把其模型/卡片历史 accepted 当作新 DB 可用性的证明。
4. W0 冻结新的 `NarrativeEvidencePackage/v1` 前，先与 I-05-C/06-A 的**最新正式产品合同**作角色映射：来源包 = 上游非投资资料投影；`summary`/`sections` 复用或升级现有 producer，`consumer_analysis` 归下游；确定唯一 job owner、请求身份、attempt/outbox、缓存失效和版本 pin。若对方尚在候选/blocked，W0 只在隔离夹具做评估，不自行把候选提升为生产规范。
5. 两边各写各自仓库/计划，跨仓只通过版本化只读 export/ID/hash；不复用共享可变 SQLite，也不修改对方正在进行的 PWF 状态。本方案发现契约冲突时留下精确文件/hash/返回值并停在相应门禁，不以“计划互不冲突”的笼统判断放行。

## 目前结论

**当前 F0–F2 与 I-11-B 没有直接文件冲突；F4/F5 有时间窗口风险，W0–W6 有真实设计重叠。** 用上述数据/源码哈希门禁可以使旧库提前退役在另一计划继续推进时安全停住；W 阶段必须以对方当时的正式合同为输入，不并行发布重复 producer、DAG 或 Worker 状态机。

## F 阶段执行后的核对与后续节奏

2026-09-26 的 F3 对 18 个本仓/跨仓合同文件冻结 SHA，6 组 query 与 12 组 no-download resolve 的旧/新库响应一致；F4 两轮生产烟测和 F5 前重核合同文件未变化。F5 19:06:54 UTC 已删除精确旧库，保留新库与完整备份，Worker 继续 paused。此结论只覆盖已审计的读接口，不代表 revenue-forecast 全业务预测、StockWiki consumer 或 invest-quick-scan 已完成端到端回归。

后续改用 [G0–G4 大节点审查](milestone_review_cadence.md)：G0 一次核 I-05-C/I-06-A 最新正式产品合同与 job owner，G2 仅在新 export/检索合同变动时让受影响消费者跑一次只读夹具，G3 复用 R4/v5 对基础 Worker 的已通过收据。不因对方 PWF 文字更新重做全库哈希；实际共享代码、schema、来源身份或消费者行为改变才重开受影响节点。
