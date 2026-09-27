# 需求—痛点—工作单元—测试—关闭证据追踪矩阵

> 任何一行没有当前、可重放、指定层级的证据时均为未完成。  
> 场景详细oracle见冻结 `scenario_matrix.md`；本文定义用户目标级组合验收。

## 1. 六个最终问题

| 最终问题 | 必须完成的工作单元 | 组合验收 | 关闭证据 |
|---|---|---|---|
| 1. 重构完全成功 | CA-001～109；ZR-101～409；ZR-906/907；ZR-1001～1009；CA-303/304 | 真Reader；同一RuntimeContext；v1/v2 parity；两个动态周期legacy hit=0；R9四RED转绿；rollback | exact triplet、CodeGraph/runtime caller=0、R9分批receipts、rollback restored |
| 2. Dropbox功能层加入filing | ZR-401～409、ZR-501～510、ZR-802/806；CA-302 | revenue入口物理排他Dropbox-only exact reuse；selected root/location为Dropbox；download=0；外部root零写；sidecar不污染 | T1/T2 trace、root fingerprints、policy snapshot、filing handle receipt、broker artifacts |
| 3. 所有功能/目标实现 | ZR-201～806、ZR-701～713 | existing/partial/missing/stale/amended；artifact/worker；broker/web；draft/formal；矿业bridge或诚实gap；二次零昂贵调用 | 197场景结果、三类公司journeys、stage/side-effect ledgers、model reconciliation |
| 4. 完善动态审核 | ZR-901～905、CA-201～206 | PR current-triplet；真实Daily/Weekly/Monthly；missed/stale/half/alert故障自测 | 7 Daily、2 Weekly、1 Monthly、1 alert drill，全部新鲜且原子 |
| 5. E2E覆盖真实场景 | ZR-801～806、CA-105/106/302 | 三真实进程、三roots+future、live writer、真实PDF/provider/worker、Windows/Linux、三类公司 | test result registry、sample hashes、process trace、独立oracle、zero-skip |
| 6. 全面代码质量 | ZR-104/906/907、CA-003/201/303 | core hardcode=0、strict type、critical coverage、CC单调下降、docs/schema/skill一致、无双真源 | CodeGraph/AST/quality reports、threshold history、drift mutation、independent review |

## 2. 文件复用、时效和下载决策

| 用户情形 | 入口与期望 | 场景 | 必须断言 |
|---|---|---|---|
| companies已有完整、当前财报 | revenue→filing→wiki | 旧EX + ZJ-01/REV-19/20 | exact reused；provider discover/fetch=0；selected location正确；第二次同结果 |
| dayu-only已有财报 | 同上 | ZR-409/802/806真实21份候选中的unique sample | handle通过policy；download=0；不复制到companies；外部root零写 |
| Dropbox-only已有合法财报 | 同上 | ZJ-01 + root-exclusive变体 | 不是companies副本；sidecar身份合法；policy允许才复用；download=0 |
| 同SHA跨三个roots | 同上 | BR-20/EX矩阵 | 一个document/一套artifacts；按request eligible location选择；处理一次 |
| preferred位置临时失效 | 同上 | location fallback mutation | 选择同SHA下一eligible副本；不可选被policy拒绝root；全失效才gap |
| 本地exact且provider无新版 | same | LT/DL矩阵 | no actionable gap；授权有无都不下载 |
| 本地旧期间，provider有新期间 | same | ZJ-07/DL | 无授权0下载并报告missing；有授权只补缺期；第二次0下载 |
| 同期间有更正/新revision | same | REV/DL amendment | `newer_revision` actionable；按filed_at/revision选真实新版；旧版保留 |
| provider返回更旧但ID字典序更大 | same | revision负例 | 不下载/不覆盖；禁止字符串排序误判 |
| 多期间/多修订缺口 | same | 多gap | 受max_items/bytes限制稳定处理；未闭合返回remaining，不伪complete |
| future/not-published/provider unavailable | same | LT/DL | 精确状态；不猜、不下载；历史阶段receipt保留 |
| 未授权 | same | DL授权负例 | discover/fetch/commit=0；仅本地判断 |
| 两并发同缺口 | same | single-flight | 至多一次discover/fetch/commit；两个调用取得同一canonical结果 |

## 3. 已处理成果与最小重算

| 起始状态 | 预期 | 关键场景 | 证据 |
|---|---|---|---|
| 原文+valid MD/summary/table/chunk/tag/facts | 全复用 | REV-11/20、ZJ-10 | artifact reads有；parser/LLM/demand=0；source/producer/schema hashes匹配 |
| 只有原文 | 提交所需角色需求 | BR-22～24、ZR-507/706 | 真demand row、worker claim、attempt journal、产物持久化、second-run-zero |
| MD已有，缺chunk/tag/table | 只补缺失DAG | BR-19/23 | normalized read；只运行缺角色及依赖；未失效summary不重算 |
| summary-only或partial | fail closed/最小补齐 | REV-11 | 不能绕过必需normalized/safety；next action明确 |
| legacy产物缺source SHA | 不直接用 | ZJ-02 | verified/recompute/quarantine分类；原文件不删；计数守恒 |
| source bytes改变 | 精确失效 | BR-19/MINE-22 | 全部依赖旧SHA的节点stale；不影响无关document/asset/year |
| producer/schema/model/prompt变更 | 按兼容合同失效 | ZR-306 | 只重算受影响role；compatibility decision可审计 |
| worker失败/崩溃/重复请求 | 有界恢复 | BR-22～24 | heartbeat/lease/retry/idempotency；不重复外发/LLM |

## 4. Broker、网页和矿山资料

| 目标 | 强制测试 | 通过条件 |
|---|---|---|
| 七份紫金研报可用 | BR-01/06/11/12/15/16/18、ZJ-03 | 7/7身份/日期/page/table/chunk/tag；material cell错列/单位/实体为0 |
| sidecar不成为正文 | BR-02/03/05 | 一个document group；JSON primary=0；hash mismatch/relation冲突fail |
| 多实体不串公司 | BR-06/07 | 长江紫金/陕西煤业section/table/row attribution准确；错归=0 |
| 表格可回源 | BR-11～17 | page/table/row/column/merged/footnote/bbox；Markdown只是view，typed grid为真源 |
| 私人资料不越权外发 | BR-21 + malicious prompt suite | `private_user+not_reviewed+无授权` egress=0；控制流/工具/secret不受文内指令影响 |
| 官方网页保存复用 | BR-25/26、ZJ-04 | 错entity/title的200页拒绝；有效页capture→review→index→artifacts→second-run-zero |
| 资产/国家/矿种可查 | MINE-01～05/23、ZJ-05 | asset scope/alias/region/commodity/resource/reserve/basis/measurement date可回源 |
| 口径冲突不静默覆盖 | MINE-10～12 | 双assertion+conflict+residual；不能擅自择一/分配 |

## 5. Revenue合同、模型和发布

| 能力 | RED/测试 | 验收标准 |
|---|---|---|
| schema单一真源 | REV-01/03 | constants/validator/linter/generator/docs/help/fixtures一致；3.6只在migration allowlist |
| generator有效 | REV-02/04 | generate→test filler→lint→validate_document→draft full run一次通过；生产无test filler |
| validate-only纯只读 | REV-05 | success/failure都无sign/registry/network/subprocess/write；文件树和registry hash不变 |
| draft/formal分离 | REV-06～08 | draft可render不发布；formal强门+签名；互换/重hash攻击失败 |
| publication事务 | REV-09 | sign/render/write/fsync/rename/registry/进程中断每点故障无孤儿/重复；恢复幂等 |
| 分阶段来源错误 | REV-10/11 | safety/processing失败仍显示reuse/download；next action精确 |
| 矿业显式模型 | MINE-14～22、REV-12/16/22 | mine×product商业层、ownership/consolidation/internal elimination与external segment勾稽 |
| 诚实fallback | MINE-19/20、ZJ-06 | 缺bridge只输出指标/range/gap；2028来源不支撑2029/30；confidence cap |
| 置信度抗博弈 | REV-13/14 | duplicate/split/plug/one observation/wrong company/snapshot不能提分 |
| rolling backtest | REV-15、ZR-713 | 多origin、strict as-of、四层hash、actual/accounting basis一致 |

## 6. 三条最终公司旅程

### Journey A：紫金矿业复杂canary

- T2复用FY2024/FY2025财报；报告root/location、safety/artifact阶段；无缺期时零下载。
- 处理并消费七份Dropbox研报和有效官方网页；拒绝错误strategy页。
- 建立主要资产/地区/矿种/resource/reserve/ownership口径；逐矿可回答范围与gap清楚。
- 对有会计桥部分输出mine-year贡献并勾稽；不足部分分部fallback且置信度受限。
- draft可render、registry零写；formal原子发布；第二次请求原文/产物/事实/兼容分析按合同复用。

### Journey B：第二家异构矿企

- 必须包含与紫金不同的ownership/consolidation、产品形态或内部流转。
- 只换配置、来源和输入数据，不改产品代码/conditionals。
- 同样通过资源/储量、商业层、会计桥、backtest/confidence和second-run-zero。

### Journey C：非矿业公司

- 验证平台升级未把revenue系统变成矿业专用。
- 使用不同root组合、不同filing period和非矿业显式driver；不加载矿业必填字段。
- 复用/下载/processing/draft/formal/dynamic audit均与同一通用合同兼容。

## 7. 动态审核和质量验收

| 周期 | 强制内容 | 新鲜度/次数 | 自毁测试 |
|---|---|---|---|
| PR | candidate triplet T0/T1、schema/docs、architecture、receipt、critical mutations | 每次变更 | sibling漏跑、old pin、collection下降、`|| true` |
| Daily | Windows T2、unique roots、Reader/live WAL、reuse/readiness、zero-write/SLO | ≤24h；连续7次 | schedule缺失、半报告、旧绿、SQL代理、样本非unique |
| Weekly/Release | CN/HK/US T3、amendment、single-flight、provider drift、rollback | ≤7d；2次 | 无凭据被pass、写真实wiki、吞provider rc |
| Monthly | broker rotation、紫金shadow、第二矿企、非矿企、backtest/confidence | ≤35d；1次 | 公司/路径硬编码、黄金样本缺失、错归被均值掩盖 |
| Alert | missed/stale/failure delivery | 1次drill | sink失败/无ack/重试失效 |

质量出口：产品核心root/company/path硬编码0；legacy production caller0；新/改关键函数CC≤10；历史高CC每波下降；strict typing覆盖关键contract；critical path branch coverage按冻结阈值；docs/schema/skill/sample hash drift让CI红。

## 8. 证据新鲜度和关闭规则

- T0/T1/PR证据绑定candidate triplet，任一仓变更立即stale。
- T2 ≤24h，T3 ≤7d，Monthly ≤35d；过期不能复用旧绿。
- real sample必须在registry中unique，缺失为blocked；blocked不计pass。
- required场景skip/xfail=0；基础设施错误需修复/重试或保持blocked。
- reviewer receipt必须引用唯一implementer revision hash；finding closure可追。
- 六问题必须各自machine pass；总体“99%”也不能关闭剩余1%。
