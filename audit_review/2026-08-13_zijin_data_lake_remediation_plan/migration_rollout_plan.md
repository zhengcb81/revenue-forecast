# 渐进迁移、影子运行、切换与安全回滚

> 本文只设计未来发布。任何生产写入、真实下载、worker状态变化或配置激活都需要当次显式授权。

## 1. 总原则

1. 先修无数据变更的 Reader/契约，再做 additive schema，再做数据 migration，最后切 consumer。
2. 每一波固定 current triplet、plan/policy/schema/cohort/hash；请求期间不得漂移。
3. 固定顺序：副本演练→shadow→diff review→用户批准→最小cohort→T2/T4→观察→扩大。
4. rollback优先改变路由/可见性，不删除记录/文件；migration全additive。
5. companies/dayu/Dropbox原文永不删除或原地覆盖；坏location退役仍保留审计。
6. 不可证明lineage的legacy artifact不绑定；按需从已核验raw重新生成。
7. 同一波失败立即停止；不得因“下一波可能修好”继续扩大。

## 2. 生产变更前置包

ZR-1001必须产生：

- 三仓clean result triplet与远端可获取证明；
- 所有mandatory ZR/场景/动态报告的新鲜receipt；
- production DB/WAL/SHM、schema、row counts、root fingerprints、worker desired/actual状态；
- 可验证catalog副本，`integrity_check`/schema/关键query通过；
- migration/processing容量：预计rows/bytes/time/temporary disk/lock；
- backup可读性和在独立临时路径的restore rehearsal；
- 每波命令ID、授权scope、cohort、side-effect budget、超时、owner/reviewer；
- 自动rollback命令和同一request before/restored oracle；
- 用户dirty/其他agent文件allowlist。

任何占位hash、未填数字SLO/容量、不可读backup、过期动态报告都阻断窗口。

## 3. 发布波次

| 波次 | 内容 | 进入条件 | 执行与观察 | 退出条件 | 自动回滚 |
|---|---|---|---|---|---|
| R0 | governance/registries/PR gates | ZR-001~105 | 仅CI/assurance，不触数据 | command/scenario/receipt自测绿 | revert workflow/manifest |
| R1 | `CatalogReader` shadow | ZR-201~206 | 每个读请求双读，new结果不参与响应；采样性能/差异 | curated 100% parity；差异全解释；write attempts=0 | 关shadow flag |
| R2 | Reader active 小cohort | R1两周期绿 | 1%→10%→50%→100% query/resolve/status；Writer不变 | T2/live-writer/SLO全绿；旧reader hit可观测 | route回旧reader；零数据回滚 |
| R3 | lifecycle/safety/reusable view shadow | ZR-301~307,R2 | additive assertions；旧active响应不变；双算readiness/bundle | 两周期diff全解释；source SHA/producer journal完整 | 关view/activation；保留rows |
| R4 | RootPolicy/eligible-location shadow | ZR-401~405,R2 | v1/v3双评估；不扩大权限 | companies/dayu/Dropbox/future fixture全解释；policy toggle有效 | 切回v1 snapshot |
| R5 | root cohort cutover | R4 | companies→dayu→Dropbox→future_lake逐root；每步T2/T4 | 用户入口exact复用、external write=0、同request rollback恢复 | cohort off；assertions/locations保留 |
| R6 | freshness/gap/download v2 | ZR-406~408,R5 | 先T3临时wiki，再最小provider cohort | old+latest/newer revision、single-flight、二次零下载全绿 | latest flag off；exact继续可用；不删新来源 |
| R7 | artifact legacy canary | ZR-304~306,R3 | 先dry-run；provably_bindable>0才1→小批；bundle真实读取 | 100%分桶、幂等/resume、valid reuse零producer | deactivate/delete shadow binding；不删artifact |
| R8 | broker processing canary | ZR-501~510,R3/R5/R7 | 七份紫金按1份天风→长江负例→3→7；privacy门 | identity/table/chunk/tag质量、成本/SLO、rollback | router/view回旧；新artifacts保留不可见 |
| R9 | mine facts/model shadow | ZR-601~713,R8 | 只draft；旧direct与新mine bridge并跑，不发布 | 紫金+第二矿企，reconciliation/backtest/confidence/diff全解释 | 关schema3.8/model/confidence flags |
| R10 | revenue source/draft/formal cutover | ZR-704~710,R6~R9 | validate-only/draft先，formal最后小cohort | ZJ全旅程、formal原子、registry integrity、SLO、side effects | route回3.7/direct/旧source path；旧artifact不改 |
| R11 | dynamic schedule硬门 | ZR-901~905,R10 | 实际Daily/Weekly/Monthly运行和告警演练 | 7 Daily、2 Weekly、1 Monthly、1告警链 | release资格blocked；不回滚数据 |
| R12 | legacy route/code删除 | R11+ZR-906/907 | 先禁用再观察；最后单独删除 | ≥2完整动态周期hit=0；CodeGraph caller=0；N-1终止批准；全矩阵绿 | revert删除commit/临时恢复compat flag |

## 4. Reader 与 schema 特殊安全规则

- R1/R2 不得包含schema/data migration，确保Reader问题可独立回滚。
- live DB不能盲用`immutable=1`；sealed副本与live WAL模式分开测试。
- additive schema在副本验证unknown/future version零部分写后才能进入R3。
- request读取固定snapshot；并发writer发生时只能看到完整before或after，不能混合source/bundle。

## 5. Artifact migration 决策树

```text
统一生产 reusable view/validator 已上线？
  否 -> 禁止migration
  是 -> mode=ro dry-run 100%分桶
       provably_bindable == 0？
         是 -> 禁止apply；按需重处理；shadow表退役/只作审计
         否 -> 独立抽查（<50全查，否则每桶>=10+风险样本）
              -> 最小shadow binding
              -> SourceBundle真实读取+consumer零producer
              -> 双读diff
              -> 扩大
```

- backfill和SourceBundle使用同一字段projection/validator；不能metadata/columns两套真源。
- migration journal按batch记录before/after、resume token、counts/hashes；kill/restart和二次执行必须幂等。
- `legacy_untrusted`可人工查阅但consumer不可用；新可信artifact用supersedes关联，不覆盖旧bytes。

## 6. Broker真实七PDF迁移

1. 获取maintenance/processing锁，只在安全点暂停相关writer；Reader继续服务。
2. 备份catalog/activation/artifact registry；冻结7 source hashes和页数。
3. shadow scan验证sidecar不再primary、文档identity/multi-entity/date。
4. 先处理一份表格丰富的天风报告；黄金表门绿。
5. 再处理长江比较报告；错归率必须0。
6. 扩至三份，再七份；每波检查privacy、parser/LLM预算、SLO、artifact绑定。
7. sidecar污染document只reversible retire/tombstone，不物理删除。
8. rollback切旧view/router；原PDF hash和外部root fingerprint必须不变。

## 7. Mine/revenue shadow

- schema 3.8、mining bridge、ConfidencePolicy均独立feature flags；3.7/direct路径保持canonical hash。
- 新模型先用合成multi-mine，再紫金，再第二矿企；不允许只为紫金过关。
- 紫金shadow输出明确为modeled contribution；不把未披露逐矿收入写成事实。
- material assets缺consolidation/product/unit/period、critical conflict未解、segment reconciliation失败均只能draft。
- cutover前旧/新每年/分部/终值/confidence/backtest差异必须逐项reason-coded；“模型更高级”不是解释。

## 8. 每波 release receipt

```json
{
  "wave_id": "R?",
  "base_triplet": {},
  "result_triplet": {},
  "plan_policy_schema_hashes": {},
  "authorization_id": "...",
  "cohort_before_after": {},
  "root_fingerprints_before_after": {},
  "catalog_integrity_before_after": {},
  "scenario_results": [],
  "side_effect_ledger": {},
  "performance": {},
  "shadow_diffs": [],
  "rollback": {"executed": true, "restored_trace_sha256": "..."},
  "implementer": "...",
  "reviewer": "...",
  "verdict": "..."
}
```

receipt必须机器拒绝：未授权、short hash、cohort越界、外部root变化、未解释diff、rollback未证明、mandatory场景blocked/skip、reviewer不独立。

## 9. 停波与事件处理

立即停波：

- reader write/DDL/migration attempt；
- 外部root变化、重复下载/commit、越权授权；
- 错entity/period/basis、invalid artifact、隐私外发；
- shadow diff未解释或new/old混合snapshot；
- migration integrity/journal/resume失败；
- SLO/内存/lock wait越界；
- registry孤儿/半formal publication；
- worker未恢复desired state；
- plan/manifest/HEAD并发漂移。

处理：冻结扩大→保存原始trace→按本波自动rollback→验证同request restored→创建新ZR revision和增强场景→独立review后重新从最小cohort开始，不能从失败百分比继续。

