# 旧计划与既有完成声明的只读处置投影

> 因其他程序仍在修改旧计划，本文件只做新计划视角的状态映射，不修改 `2026-08-09_full_completion_assurance_plan/`。真正更新旧计划必须由其owner按CAS协议单独执行。

## 1. 状态词典

- `KEEP_AS_GOVERNANCE`：资产继续使用，但不继承业务完成状态。
- `ALREADY_SATISFIED_CANDIDATE`：当前代码看似存在；须ZR-001/current-triplet重放和独立review。
- `REOPEN`：最新生产用户旅程直接反驳完成声明。
- `EXTEND`：旧范围有效但不足以满足新需求。
- `SUPERSEDED`：新ZR以更统一架构替代旧待办；旧项保留历史。
- `DEPRIORITIZE`：仍有价值但不在关键闭环；不得阻塞高优先主链。
- `CANCEL_CANDIDATE`：只有ADR证明不再需要且目标被等价覆盖后才能取消。
- `IN_PROGRESS_EXTERNAL_OWNER`：其他程序正在实施；本计划不写其状态。

## 2. 旧计划资产

| 文件/资产 | 处置 | 理由/新落点 |
|---|---|---|
| `architecture_target.md` (`49c2...bd5`) | KEEP_AS_GOVERNANCE | 三仓职责/RootPolicy/Bundle不变量继续有效；扩展为本计划architecture |
| `implementation_runbook.md` (`faae...cff`) | KEEP_AS_GOVERNANCE | FC生命周期/独立review成熟；新手册增加计划并发、用户旅程优先、数据迁移顺序 |
| `scenario_matrix.md` (`21e9...3c5`) | KEEP_AS_GOVERNANCE | 95场景全部冻结继承；新增READ/BR/MINE/REV/ZJ/AUD2 |
| `dynamic_assurance_plan.md` (`5c14...fd4`) | EXTEND | 机制设计保留；新增真实schedule、broker/mine/revenue SLI和自然时间门 |
| independent review/receipt/command/execution packet | KEEP_AS_GOVERNANCE | 由ZR-002/103/105升级validator，不另造松散流程 |

## 3. 旧 Phase/FC 状态投影

| 旧项 | 旧声明 | 新处置 | 依据 | 新落点 |
|---|---|---|---|---|
| FC-901 artifact backfill | accepted，生产apply/canary曾完成 | REOPEN | shadow `artifact_bindings`无生产reader；validator/source字段真源漂移 | ZR-304/305/1005 |
| FC-902 SourceBundle进入resolver | accepted | EXTEND | bundle存在但需要唯一reusable view、阶段readiness、generic roots | ZR-304/306/307 |
| FC-903 filing透明转发 | accepted | REOPEN/EXTEND | policy snapshot未完整传；default companies allowlist阻Dropbox/dayu | ZR-404/405 |
| FC-904 revenue selector | accepted | EXTEND | canary可读不等于旧artifact/ProcessingDemand/真实broker/minimal DAG闭环 | ZR-306/706 |
| FC-905 safety receipt | accepted | REOPEN/EXTEND | 紫金真实source仍not_reviewed；reuse成功被顶层错误遮蔽 | ZR-302/303/307 |
| FC-906 artifact canary | complete | KEEP_AS_HISTORICAL_CANARY | 证明特定v2样本，不证明legacy迁移/七PDF/当前triplet | ZR-003/305/806 |
| Phase 10三仓E2E | complete | EXTEND | 旧runner/companies canary范围有限，真实Dropbox/broker/live-lock/draft仍失败 | ZR-102/801~806 |
| Phase 11动态审核 | complete | REOPEN/EXTEND | runner存在但实际schedule/新鲜运行未证明 | ZR-901~905/1104 |
| FC-1201 root hardcode | accepted但遗留R9 | REOPEN | resolver kind/default companies与通用root仍断 | ZR-401~409/906/1009 |
| FC-1202单一策略源 | accepted | EXTEND | 配置doctor不等于生产RootPolicy 3.0接线 | ZR-401/404/405/907 |
| FC-1203模块边界 | complete/accepted声明 | REVALIDATE | legacy `IngestedDB`/source_catalog并存；生产caller需当前CodeGraph | ZR-104/906/1102 |
| FC-1204类型/覆盖/复杂度 | accepted/继续ratchet | ALREADY_SATISFIED_CANDIDATE + EXTEND | 当前质量门较强，但新模块和critical paths需冻结 | ZR-104/906 |
| FC-1205错误/编码 | accepted | ALREADY_SATISFIED_CANDIDATE + EXTEND | 新reason taxonomy/Windows read URI/worker errors仍需场景 | ZR-204/804/906 |
| Phase 13 observability/SLO | complete | KEEP_AS_BASELINE + EXTEND | 复用框架；新增Reader/broker/mine/revenue业务SLI | ZR-206/904 |
| Phase 14 rollout | 其他程序实施中 | IN_PROGRESS_EXTERNAL_OWNER | 当前存在Phase-14 ledger/assurance runs并发变化 | 本计划ZR-1001启动前协调；不得并发生产writer |
| Phase 15终审 | pending | SUPERSEDED | 新需求和新场景更广 | ZR-1101~1105 |

## 4. Revenue旧项投影

| 能力 | 处置 | 新落点 |
|---|---|---|
| formal强验证/receipt/input anchor | ALREADY_SATISFIED_CANDIDATE | ZR-001/705/710只重验和补故障；不无故重写 |
| centralized MODEL_REGISTRY | ALREADY_SATISFIED_CANDIDATE | ZR-610/707扩展组合而非新增公司分支 |
| immutable snapshot/backtest基础 | ALREADY_SATISFIED_CANDIDATE | ZR-708重验；ZR-713接紫金rolling-origin |
| generator/linter/docs/schema | REOPEN | ZR-701~703 |
| validate-only零写 | REOPEN | ZR-704 |
| draft renderer | REOPEN | ZR-705 |
| mining resource/reserve_depletion | EXTEND | ZR-610/611/707/711，不删除基础模型 |
| confidence | EXTEND | ZR-712反博弈和policy版本化 |

## 5. 取消/降级候选

- 任何为特定root建立的第二套policy/allowlist：`CANCEL_CANDIDATE`，由RootPolicy 3.0统一替代后删；删除前caller/hit=0。
- 只被测试调用、已有生产入口等价覆盖的helper/canary wrapper：`DEPRIORITIZE`至ZR-906/1009统一清理，不能在功能主链中顺手删。
- 旧固定数字（artifact数、error数、worker backlog、HEAD/行号）：`SUPERSEDED`为ZR-001实时基线，不作为任务目标。
- “把所有legacy artifact强行绑定”：`CANCEL_CANDIDATE`；目标改为可证明才绑定，否则按需重处理。
- “逐矿收入无论资料是否充分都必须输出”：`CANCEL_CANDIDATE`；由会计桥闭合或明确gap替代，避免伪精确。

## 6. 状态同步协议

当旧计划owner希望更新状态时：

1. 读取旧文件最新hash/mtime/HEAD；
2. 对照本文件但不直接复制结论；
3. 只在旧owner确认无并发writer后做小补丁；
4. 每个完成标记附current triplet、ZR/旧FC receipt、场景和reviewer；
5. 冲突即停止合并，不能整文件覆盖；
6. 本计划不以旧文件是否同步作为实现完成证据，唯一真相仍是machine registries/receipts。
