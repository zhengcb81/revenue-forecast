# 动态审核、业务 SLI 与长期防回归计划

## 1. “有脚本”不等于“动态审核已运行”

每层必须证明五件事：runner存在、真实调度存在、运行环境/权限可用、报告新鲜且完整、release gate实际消费。任一缺失，状态为 `blocked/stale`，不能显示绿色。

| 层 | 真实触发 | 必跑 | 新鲜度 | 失败动作 |
|---|---|---|---|---|
| PR | 三仓任一PR/commit | T0、T1、current-triplet、contract/docs、quality、architecture、receipt、critical mutation | result triplet当次 | 阻断合并 |
| Daily T2 | 有三真实root权限的Windows runner每日 | production只读三roots、live worker exact reuse、broker/artifact samples、root fingerprint、SLO、health | 正常目标<=24h；硬失效36h | 阻断release并告警 |
| Weekly T3 | 每周及发布前 | CN/HK/US真实provider→临时wiki；首次下载+第二次零下载；并发/授权负例 | 正常目标<=7d；硬失效9d | blocked/failed；不得沿用旧绿 |
| Monthly business shadow | 每月、相关schema/model变更后 | 紫金完整draft：filing+broker+web+mine facts+backtest+renderer；registry零写 | 正常目标<=30d；硬失效35d | 相关release blocked |
| Release T4 | 每个cohort授权窗口 | before/apply/after/rollback/restored、用户旅程、SLO、side effects | 当次窗口 | 自动停波/回滚 |

## 2. 绝对零容忍 SLI

以下任一非零即 P0/P1：

- unauthorized provider fetch / canonical write；
- external-root write（dayu/Dropbox等）；
- Reader mkdir/WAL/DDL/migration/seed/commit attempt；
- exact/current filing 的意外重复下载；
- invalid/legacy-unbound/tampered artifact 被消费；
- 新 artifact 缺 mandatory source SHA/producer lineage；
- `.source.json` 作为primary document；
- root/policy hash mismatch 被接受；
- valid reuse 时不必要 parser/LLM；
- broker material entity misattribution；
- material resource/reserve、actual/estimate、ownership basis 混淆；
- draft 写publication registry或invest接受draft；
- 2028 source claim支撑2029/2030参数；
- T2 production catalog/source-root写入；
- mandatory scenario skip/xfail/expected-failure。

## 3. 趋势与质量 SLI

| SLI | 分组/说明 | 门槛策略 |
|---|---|---|
| exact/latest reuse success | root/market/kind | mandatory canary 100%；总体低于冻结baseline即finding |
| download avoidance | exact/current/second-run | mandatory样本100%；任何不符零容忍 |
| consumer-ready rate | document role/root | 每phase只升不降；下降超过冻结error budget阻断 |
| artifact reuse hit | role/generator | 对ready样本100%；全局趋势ratchet |
| legacy-unbound | count/bytes/hits | hits不得增长；migration后burn-down；不可通过伪绑定改善 |
| prompt-review coverage | role/root/policy version | consumer-ready样本100%；过期单列 |
| broker identity/table fidelity | entity/date/table/cell/unit | material错归/错列=0；关键table recall=100%；关键cell≥99%且material cell=100% |
| processing demand | latency/dedupe/retry/fairness/cost | ZR-508冻结数字；重复producer=0；private export violation=0 |
| mine fact coverage/conflict | asset/commodity/metric/basis | accepted material facts locator/basis=100%；unresolved conflict阻断模型 |
| explicit model share/residual | segment/revenue weight | 由ZR-609/709冻结阈值；未达只允许draft+cap，不得隐藏residual |
| rolling backtest | company/segment/horizon | 报告sample/error/recency；缺失触发cap；误差恶化超policy阻断formal |
| draft/formal render | mode/schema | mandatory corpus 100%；draft registry writes=0；formal orphan=0 |
| Reader SLO | query/resolve/bundle、catalog size | ZR-206冻结绝对p95/p99和内存；之后不得提高，回归预算<=20%且仍低于绝对门 |
| scan/catalog health | errors/interrupted/stale locations | baseline+owner+deadline；增量/连续失败超预算阻断 |

ZR-206/508/609/709 必须在实现前把“待冻结阈值”写成数字并由reviewer接受；未填数字不得进入RED之后的状态。

## 4. 样本注册与轮换

- companies/dayu/Dropbox 各>=2个unique filing样本；“unique”要求其他root无同document/content hash。
- broker固定样本为七份紫金PDF，另至少2份轮换报告和1份不同公司比较报告。
- mine固定事实覆盖主要金/铜/锌铅/锂资产；另有第二矿企泛化样本。
- web固定包含2个有效官方HTML和错误strategy页面负例；轮换近期公告。
- 每次运行重新验证hash、identity、root uniqueness、privacy authorization、provenance和as-of；不信任上次登记。
- 固定样本保证确定性，季度轮换一部分验证泛化。缺失/重复/失权为blocked，不自动替换成容易样本。
- 私有内容不上传CI；报告只保存hash IDs、脱敏metadata、locator token和质量统计。

## 5. 报告结构与原子发布

```text
assurance/runs/{run_id}/
  run_manifest.json
  triplet.json
  plan_registry_hashes.json
  command_results.json
  scenario_results.json
  sample_registry_snapshot.json
  stage_receipts.json
  side_effect_ledger.json
  root_fingerprints.json
  catalog_health.json
  performance.json
  broker_quality.json
  mine_fact_quality.json
  forecast_quality.json
  provider_contracts.json
  findings.json
  verdict.json
```

- 先写临时目录，全部schema/hash校验后原子rename；半报告不能覆盖上次完整报告或延长freshness。
- verdict只有 `pass/failed/blocked`；不得有 `passed_with_skips`。
- 报告绑定current triplet、plan/scenario/command/schema/policy/sample hashes和runner identity。

## 6. Release gate

发布资格要求：

1. 当前triplet PR gate绿；
2. 最近36h内T2 pass；
3. 最近9d内T3 pass；
4. 涉及source/broker/mine/revenue模块时最近35d business shadow pass，且相关commit未使报告stale；
5. 无开放P0/P1，P2有owner/deadline且不影响本release；
6. audit self-test最近在当前runner/contract版本通过；
7. sample registry无blocked；
8. rollout时有当次T4 receipt与rollback。

相关模块commit发生后，旧报告按impact map自动stale；不能仅比较日期。

## 7. 审核系统自测

每次修改runner/report/freshness/sample/release逻辑，注入并证明release gate非零：

- schedule不存在或最近run未发生；
- 陈旧/错误triplet/错误plan hash报告；
- root/broker/mine样本缺失或失去unique；
- root fingerprint变化；
- 伪download/parser/LLM=0；
- command非零但wrapper返回0；
- renderer失败、consumer-ready下降或entity misattribution；
- provider无凭据/限流；
- receipt篡改、implementer=reviewer；
- runner超时/被杀/半报告；
- plan文件并发变化。

## 8. 告警与响应

| 级别 | 例子 | 响应 |
|---|---|---|
| P0 | 未授权写/下载、数据损坏、隐私外发 | 立即停线/回滚/冻结发布/通知用户 |
| P1 | root复用回归、错实体/口径、invalid artifact、latest错误、formal孤儿 | 阻断合并/发布；24h内owner；新增/增强场景 |
| P2 | SLO、processing SLA、coverage、legacy趋势或报告过期 | 阻断release；限定恢复时间，不可豁免绿 |
| P3 | 非关键文档/趋势偏差 | owner+期限；下一周期复验，不能无限延期 |

P0/P1修复必须增强相应场景/oracle/audit self-test，不能只改代码。

## 9. 自然时间门

动态机制不能通过一次手工运行宣布完成。最终关闭至少需要：

- 连续7次Daily T2，无silent skip；
- 连续2次Weekly T3真实隔离运行；
- 至少1次Monthly紫金完整business shadow；
- 至少1次真实告警链自测；
- 观察期内zero-tolerance指标全0、无未解释SLO/质量恶化。

未达到自然时间只能 `provisional/observing`，不能手工改complete。
