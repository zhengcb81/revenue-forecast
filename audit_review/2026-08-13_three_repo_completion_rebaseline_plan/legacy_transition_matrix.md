# 旧计划逐项迁移与关闭矩阵

> 目的：让旧计划可以停止继续领取工作，同时不伪造“已 complete”。  
> 本文件只表达新版视角；真正向旧目录写 terminal notice 必须等 `CA-306`，并由旧计划单一 owner 执行。

## 1. 审计口径

严格 current-triplet 分类的71项结果：

| 分类 | 数量 | 含义 |
|---|---:|---|
| `implemented_not_independently_verified` | 31 | 有代码/机制资产，但没有当前triplet独立证据 |
| `contradicted_by_current_behavior` | 26 | 当前源码、真实用户链或强RED直接反证旧完成范围 |
| `stale_evidence` | 9 | 旧triplet可能成立，但当前组合、数据、配置或索引已漂移 |
| `pending` | 5 | FC-1501～1505 明确未完成 |
| `verified_complete_current` | 0 | 无一项可直接继承旧标签宣称当前完整 |

`verified_complete_current=0` 不等于“所有代码都没做”，而是拒绝把历史 receipt 自动当作当前保证。保留资产在新计划通过 `already_satisfied` 快速路径复验，不重复重写。

## 2. 71 FC 逐项分类与 successor

缩写：`I`=implemented_not_independently_verified，`C`=contradicted，`S`=stale，`P`=pending。

| 旧项 | 类 | 最小可保留资产/当前反例 | 新 successor |
|---|---|---|---|
| FC-000 | S | 历史仓库基线 | CA-002/004 |
| FC-001 | S | 历史数据/问题基线 | CA-002/004、ZR-001 |
| FC-002 | S | 旧计划完整性清单 | CA-001/004 |
| FC-101 | I | contract registry骨架 | CA-101/102、ZR-101 |
| FC-102 | C | command登记不等于本次执行 | CA-104 |
| FC-103 | C | structural receipt被误作accept验证 | CA-102/103/107/108 |
| FC-104 | C | current manifest陈旧且只验baseline descendant | CA-002、ZR-105、CA-201 |
| FC-201～205 | I | RuntimePolicy/CAS/apply/rollback资产 | ZR-101、ZR-401/404、ZR-1002/1003；CA-003验证每个flag真caller |
| FC-301 | I | RootPolicy schema基础 | ZR-401 |
| FC-302 | I | adapter registry基础 | ZR-402 |
| FC-303 | I | scanner/admission seam | ZR-402/403 |
| FC-304 | C | v2 shadow/active与生产路径分叉 | ZR-403/404、CA-003 |
| FC-305 | I | shadow parity工具 | ZR-409、ZR-1003/1004、CA-304 |
| FC-401～405 | I | migration bucket/journal/rollback资产 | ZR-304/305、ZR-1005；不得强绑不可证明产物 |
| FC-501 | C | external root handle目标未贯穿filing | ZR-401/404/405 |
| FC-502 | I | sidecar adapter资产 | ZR-501/502 |
| FC-503 | I | path/identity候选资产 | ZR-402/403/501/502 |
| FC-504 | S | canary非排他且receipt revision混乱 | CA-103、ZR-409、ZR-802/806 |
| FC-505 | C | 实际选中companies，不证明Dropbox-only | ZR-405/409、ZR-806、CA-302 |
| FC-601 | I | companies adapter | ZR-402/409 |
| FC-602 | C | dayu master identity/consumer边界未闭合 | ZR-403/405/409 |
| FC-603 | I | dayu resolver canary资产 | ZR-409/802/806 |
| FC-604 | C | 三root一致性只到wiki resolver | ZR-405/409/802、CA-302 |
| FC-701～704 | I | identity/pushdown/envelope/trace基础 | ZR-201～205、ZR-403/404、ZR-307 |
| FC-705 | S | legacy observer历史证据 | CA-003、ZR-1003/1009、CA-304 |
| FC-801 | I | local match/gap骨架 | ZR-406 |
| FC-802 | C | latest/freshness尚未正交 | ZR-406 |
| FC-803 | I | download authorization/staging基础 | ZR-407/408 |
| FC-804 | C | `newer_revision`不action；多gap未闭合 | ZR-406/407/408 |
| FC-805 | S | provider历史canary | ZR-805、CA-203 |
| FC-901 | C | shadow binding无生产reader、空source SHA可过 | ZR-304/305/1005 |
| FC-902 | C | SourceBundle存在但真源/readiness/DAG断裂 | ZR-304/306/307 |
| FC-903 | I | 运输结构可留；policy snapshot未贯穿 | ZR-307/404/405 |
| FC-904 | I | revenue artifact selector可留 | ZR-306/706 |
| FC-905 | C | 安全review生产接线缺失 | ZR-302/303/307 |
| FC-906 | C | 少量v2 canary不代表存量/研报/当前triplet | ZR-003/305/510/806 |
| FC-1001 | I | IsolatedLake fixture | ZR-102/801～804 |
| FC-1002 | C | marker/fixture不证明真实全链 | CA-105/106、ZR-802 |
| FC-1003 | C | companies-only/旁路用户旅程 | ZR-802/806、CA-302 |
| FC-1004 | C | Windows中文/长路径现有回归 | ZR-804 |
| FC-1005 | S | 真实canary证据陈旧/范围窄 | ZR-805/806、CA-202～204 |
| FC-1101～1105 | C | runner工具存在，schedule/report/alert/soak未运行 | ZR-901～905、CA-201～206 |
| FC-1201 | C | hardcode只冻结，R9仍4 RED | ZR-401～409、ZR-906、CA-303/304 |
| FC-1202 | C | 配置doctor不等于同一immutable policy接全请求 | ZR-401/404/405/907、CA-003 |
| FC-1203 | I | 模块边界检查资产 | ZR-104/906、CA-303 |
| FC-1204 | C | 高复杂度/覆盖债务主要冻结 | ZR-104/906、CA-303 |
| FC-1205 | C | Windows encoding/path仍失败 | ZR-804/906 |
| FC-1301 | I | taxonomy工具资产；旧DAG自依赖 | CA-101、ZR-204/904 |
| FC-1302 | S | scan health历史样本 | ZR-206/904、CA-202 |
| FC-1303 | I | SLO框架可留；latest/RSS代理不真 | ZR-206/904、CA-202/205 |
| FC-1304 | S | 容量/趋势证据未持续 | ZR-206/904、CA-202/206 |
| FC-1501 | P | 旧closure原型漏检 | CA-107～109 |
| FC-1502 | P | 独立审查未做 | CA-301/303 |
| FC-1503 | P | 真实用户旅程未闭合 | CA-302 |
| FC-1504 | P | 自然时间/rollback未闭合 | CA-206/304 |
| FC-1505 | P | final ledger/旧计划关闭未做 | CA-305/306 |

## 3. R0～R9 发布波次迁移

| 波次 | 当前分类 | 当前事实 | 新处置 |
|---|---|---|---|
| R0 | C | governance/current-triplet gate与陈旧manifest、无upstream、workflow实况矛盾 | CA-001～109、CA-201 |
| R1 | I | runtime snapshot显示部分flag已应用，但production consumer不可从flag值推断 | CA-003、ZR-1002/1003 |
| R2 | I | `v2_scan_shadow=true`，CLI/service并未必传入；观察证据不完整 | CA-003、ZR-409、ZR-1003 |
| R3 | S | 账本仅写evidence，缺current独立wave receipt/T4 | ZR-1003/1004、CA-107 |
| R4 | C | filing未消费RootPolicySnapshot，dayu独有filing不可达 | ZR-404/405/409、CA-302 |
| R5 | C | Dropbox canary选中companies副本；sidecar污染仍在 | ZR-501～510、ZR-806 |
| R6 | C | 少量bound artifact不代表生产存量/consumer-ready | ZR-304～307、ZR-1005 |
| R7 | C | missing链有资产，newer revision不action | ZR-406～408、ZR-805 |
| R8 | I | bridge off状态存在，但前后路径/回滚/观察未闭合 | CA-003、ZR-1008 |
| R9 | P | 强制门当前4/4 RED；日常默认skip | ZR-1009被CA-304统一替代；现在冻结 |

## 4. 痛点到计划的无遗漏映射

| 痛点 | 直接工作单元 | 关键场景/门 |
|---|---|---|
| 假绿与历史证据漂移 | CA-001～109 | 30+ closure mutations；197场景逐tier |
| 真只读/锁 | ZR-201～206 | READ-01～12；live WAL与零写fingerprint |
| Dropbox/dayu/future root复用 | ZR-401～409 | 物理排他root；真实dayu独有filing；fourth-root core diff=0 |
| 配置/runtime策略分叉 | ZR-401/404/405、CA-003 | 同一RuntimeContext贯穿resolve/ensure/close-gap；hash可复算 |
| period/revision/最小下载 | ZR-406～408/805 | missing/newer amendment/多gap/second-run-zero |
| artifact/已处理成果复用 | ZR-301～307 | valid/partial/legacy/source-change/producer-zero |
| prompt/隐私/历史LLM处理 | ZR-302/303/501/507 | private+not_reviewed无授权外发=0；历史egress audit |
| broker PDF/表格/多实体 | ZR-501～510 | BR-01～26；七PDF逐份oracle |
| 网页/新闻沉淀 | ZR-509/510 | 错entity 200页拒绝；有效页capture→reuse |
| revenue schema/generator | ZR-701～703 | REV-01～04 |
| validate-only/draft/publication | ZR-704/705/710 | REV-05～09；故障注入/幂等 |
| ProcessingDemand | ZR-507/508/706 | 真worker、并发dedupe、第二次零处理 |
| 逐矿通用模型 | ZR-601～611/707/711 | MINE-01～24；第二矿企 |
| backtest/confidence | ZR-708/712/713 | REV-12～15；gaming mutations |
| 真实E2E/跨平台 | ZR-801～806 | ZJ-01～10；Windows/Linux；非矿企 |
| 动态审核 | ZR-901～905、CA-201～206 | 7 Daily/2 Weekly/1 Monthly/alert |
| 代码质量/R9 | ZR-104/906/907、CA-303/304 | hardcode=0、caller=0、CC下降、R9四RED转绿 |

## 5. 旧计划关闭条件

旧计划现在保持只读、状态为“正在被新版取代但尚未关闭”。只有以下都成立才能由旧owner写 terminal notice：

1. `CA-004` 的81项（71 FC+R0～R9）映射机器验证通过；
2. 所有 successor 已 accepted 或有经用户批准的非目标化 ADR；
3. `CA-305` 六问题全pass；
4. `CA-306` 锁定旧领取入口并指向新manifest；
5. 历史receipt/commit/hash原样保留。

建议终态字符串：`closed_superseded_incomplete`。它表示旧计划本身没有兑现完整目标，但遗留工作已在更强计划中完成并关闭；绝不能写 `complete` 或删除旧证据。
