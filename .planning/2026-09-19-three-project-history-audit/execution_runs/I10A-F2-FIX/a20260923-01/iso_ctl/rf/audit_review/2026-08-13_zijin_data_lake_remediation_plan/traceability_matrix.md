# 用户目标—缺陷—工作单元—测试—证据追踪矩阵

## 1. 六个顶层目标

| Goal | 用户期望 | 当前计划基线 | 工作单元 | Mandatory 场景 | 关闭证据 |
|---|---|---|---|---|---|
| G1 | 重构完全成功，不是半成品 | 旧计划多项accepted，但紫金真实旅程暴露断点 | ZR-001~409, ZR-1001~1009, ZR-1101~1105 | 旧95全量 + READ + ZJ-01/08/10 | current-triplet closure；shadow/active/rollback；legacy caller/hit=0；自然观察期 |
| G2 | Dropbox 功能层面真正加入 filing/research | root物理配置存在，filing handle默认companies；研报无语义处理 | ZR-401~510 | EX/DBX + BR-01~26 + ZJ-01/03 | Dropbox-only filing与broker两条旅程分别成功；external writes=0；配置开关可拒绝/恢复 |
| G3 | 功能和原始目标全部实现 | 文件复用、处理复用、最新补齐、矿山/网络研究仍不闭环 | ZR-301~713 | LT/DL/AR/UJ + BR/MINE/REV/ZJ | 分阶段receipt；只补真实缺口；有效artifact零重算；矿山能答则模型、不能答则gap；web来源可沉淀 |
| G4 | 完善动态审核持续检查主要功能 | runner/CI资产存在，但实际schedule与业务旅程未证明 | ZR-901~907, ZR-1104 | AUD/AUD2 | PR+实际Daily/Weekly/Monthly；freshness与release硬门；自测能让发布红 |
| G5 | E2E覆盖更多真实场景 | 旧fixture/canary不等于紫金真实用户旅程 | ZR-003, ZR-801~806 | 全矩阵，尤其ZJ-01~10 | 三真实进程、七PDF、三roots、live writer、provider、第二次调用；权威side-effect账本 |
| G6 | 全面提升代码质量、消除硬编码/紧耦合 | root kind、默认companies、legacy设施/重复契约仍存在 | ZR-104/203/401~409/701~703/906/907/1009/1102 | READ-12, MINE-24, REV-01~04/21, AUD2-07 | CodeGraph caller/impact；AST禁止门；complexity/type/coverage ratchet；docs/schema drift=0 |

## 2. 文件复用与时效补齐

| Requirement | 设计责任 | 工作单元 | 正例 | 负例/故障 | 完成定义 |
|---|---|---|---|---|---|
| companies/dayu/Dropbox 都可复用 | wiki RootPolicy+resolver；filing透明转发 | ZR-401~405,ZR-409 | EX-01/02/03, ROOT等旧场景, ZJ-01 | policy false、unknown root、path traversal、global canonical失效 | 任一policy允许root同逻辑；Dropbox/dayu-only从revenue入口成功；无产品root特判 |
| 同内容跨root只处理一次 | wiki document identity/artifact sharing | ZR-403,ZR-306,ZR-510 | EX-04, AR-09, BR-20 | 随机扫描顺序、位置移动/失效 | 一个document/source/bundle；多个locations；artifact/producer不按路径复制 |
| 已有旧报告，补最新而不重下旧文件 | wiki freshness/gap；filing授权close-gap | ZR-406~408 | LT-02/03/08/09, ZJ-07 | provider unknown/future/同期间修订/授权过期/并发 | old reuse可见；仅newer period/revision下载；第二次fetch/write=0 |
| 未授权绝不下载 | filing authorization | ZR-407 | DL-01, ZJ-07无授权 | stale/invalid auth/gap变更 | discover/fetch权限按合同；未授权fetch=0且输出gap |
| filing成功但下游安全/处理失败仍报告复用 | staged envelope | ZR-307,ZR-706 | REV-10, ZJ-01/02 | safety not reviewed、processing partial | 顶层保留reused/download=0/blocker/next action，不吞上游证据 |

## 3. 已处理文档复用

| Requirement | 工作单元 | 场景 | 强证据 | 禁止伪绿 |
|---|---|---|---|---|
| valid MD/summary/sections/chunks/tables/facts按role复用 | ZR-304~307,ZR-504~508 | AR-01/02/03/07/09, BR-19/22/23, REV-11/20 | artifact_read>0；producer/LLM/parser this request=0；hash/DAG匹配 | 返回handle或文件存在不能推断零调用 |
| source/producer版本变化只最小失效 | ZR-306 | AR-03/04/05/06, BR-19, MINE-22 | 受影响role集合与DAG独立oracle一致 | 禁止盲全量重算或继续用坏artifact |
| legacy artifact安全迁移 | ZR-304/305,ZR-1005 | AR-08, MIG-01~08, ZJ-02 | 唯一validator/view；100%分桶；真实bundle读取；幂等/rollback | 仅写无人读取shadow表不算成功；不能伪造lineage |
| consumer可请求优先处理 | ZR-507/508,ZR-706 | BR-22~24 | demand receipt、dedupe、预算、TTL、公平性、privacy | revenue不得直接改worker全局priority；private无授权不外发 |

## 4. 研报、网络与矿山研究

| Requirement | 工作单元 | 场景 | 完成定义 |
|---|---|---|---|
| 七份Dropbox研报有MD/表格/chunk/tag | ZR-501~510,ZR-1006 | BR-01~24,ZJ-03 | 7/7 metadata、source-bound artifacts；关键表/实体/单位黄金门；可按mine/country/metric/period检索 |
| 比较报告不跨实体错归 | ZR-503/506 | BR-06/07, ZJ-03 | 陕西煤业行永不归紫金；歧义进入review；misattribution=0 |
| 新闻/公告可下载、索引、处理、保存 | ZR-509 | BR-25/26,ZJ-04 | 有效网页capture→review→artifact→search；错误title/entity页拒绝；authorization/privacy按来源合同 |
| 矿种、矿山/聚合体、国家、resource/reserve容易找到 | ZR-601~604 | MINE-01~12/23 | stable asset/alias；subject scope；country/region；resource/reserve/basis/conflict/locator完整 |
| 逐矿年度贡献只有会计桥闭合才输出 | ZR-605~611,ZR-707/711 | MINE-13~22, REV-12/16/17/21/22 | mine×commodity×product；ownership/consolidation/internal elimination；与外部分部对账；否则gap/fallback |
| 不把2028事实伪延至2030 | ZR-602/605/701 | MINE-20, REV-17 | fact/claim horizon enforcement；外推为analyst assumption且无越界source claim |

## 5. revenue 工具闭环

| Known issue | 工作单元 | 场景 | 关闭标准 |
|---|---|---|---|
| schema 3.7/3.6、capture 10/9漂移 | ZR-701/703/907 | REV-01/03 | machine truth唯一；docs/skill/sample自动校验；漂移CI红 |
| generator无效 | ZR-702 | REV-02/04 | generator→filler→lint→validate→draft一次通过；不伪造source/receipt |
| linter false-clean | ZR-701~703 | REV-03/04 | 随机字段mutation false-clean=0；稳定error code |
| validate-only会发布 | ZR-704 | REV-05 | pure prepare；sign/register/network/subprocess/write调用=0；registry/filesystem不变 |
| draft renderer失败 | ZR-705 | REV-06/08/18 | current Zijin draft可validate/render；明确draft；篡改拒绝 |
| formal半发布 | ZR-710 | REV-07/09 | prepare/commit原子；故障可恢复；成功精确一次committed |
| 矿业模型过粗 | ZR-610/611/707/711 | MINE全组, REV-12/16/21/22 | ADR+3.8 opt-in；通用multi-mine；3.7零回归；无公司硬编码 |
| 缺真实backtest | ZR-708/713 | REV-14/15 | rolling-origin、无future actual、immutable四层hash；无法形成则rating cap |
| confidence可博弈 | ZR-712 | REV-12~14 | versioned policy；duplicate/split/plug/single-observation mutations全杀 |

## 6. Known-defect closure ledger

| Defect ID | 描述 | 严重度 | Owner ZR | 回归场景 | 关闭前不得做什么 |
|---|---|---|---|---|---|
| KD-01 | Reader构造隐含WAL/DDL/migration/seed | P0 | ZR-201~203 | READ-01~06/12 | 不得上线新root/扩大并发 |
| KD-02 | raw lock落fatal | P0 | ZR-204/205 | READ-07~10,ZJ-08 | 不得称reuse链可靠 |
| KD-03 | policy/handle默认companies断Dropbox/dayu | P0 | ZR-401~405 | EX-02/03, ZJ-01 | 不得用config存在称功能已接入 |
| KD-04 | newer_revision不进入close-gap | P1 | ZR-406/407 | LT revision, ZJ-07 | 不得称latest闭环 |
| KD-05 | safety not_reviewed阻断且吞阶段结果 | P0 | ZR-302/303/307 | SAFE, REV-10,ZJ-01 | 不得绕过/硬编码not_detected |
| KD-06 | shadow artifact binding无生产reader/validator漂移 | P0 | ZR-304/305 | AR-07/08,ZJ-02 | 不得先apply migration |
| KD-07 | artifact INSERT事件冒充parser/LLM调用 | P0 | ZR-304 | BR-23, REV-11/20 | 不得报告伪零/伪调用 |
| KD-08 | sidecar当primary、Dropbox隐私默认 | P0 | ZR-401/502/507 | BR-02/03/21 | 不得批量处理真实研报 |
| KD-09 | 研报无表格/多实体/chunk/tag | P1 | ZR-501~510 | BR全组,ZJ-03 | 不得称数据湖可消费 |
| KD-10 | 逐矿事实/会计桥缺失 | P1 | ZR-601~611/707 | MINE全组,ZJ-05/06 | 不得发布伪逐矿营收 |
| KD-11 | generator/linter/docs不一致 | P0 | ZR-701~703 | REV-01~04 | 不得让模板作为官方入口 |
| KD-12 | validate-only写registry | P0 | ZR-704 | REV-05 | 不得在真实registry迭代 |
| KD-13 | draft renderer不闭合 | P0 | ZR-705 | REV-06/08/18 | 不得伪造formal receipt |
| KD-14 | 动态runner未证明实际调度 | P1 | ZR-902~905 | AUD2-01~06 | 不得称动态审核完善 |
| KD-15 | 置信度/真实backtest不足 | P1 | ZR-708/712/713 | REV-12~15 | 不得将low证据包装high |
| KD-16 | root特判/legacy/重复contract/真实sibling测试 | P1 | ZR-104/906/907/1009 | READ-12,MINE-24,REV-01,AUD2 | 不得删除legacy前先证明caller/hit=0 |

## 7. Closure 规则

- 每个 Goal 只有其所有映射 ZR accepted、所有 mandatory scenario 指定层级 fresh passed、side-effect预算满足、独立review accepted时才为 pass。
- Goal不能由另一Goal间接推断；例如G2 Dropbox filing绿不意味着broker research绿，G5大量E2E不意味着G4 schedule真实运行。
- Known defect 不允许 `won't fix` 直接关闭；cancel必须证明用户目标由另一accepted ZR等价覆盖，并有ADR/reviewer。
- 最终 `closure_ledger.json` 由工具从registries/receipts生成，不手写布尔值。

