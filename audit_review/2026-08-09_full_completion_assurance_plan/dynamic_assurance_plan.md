# 动态审核与长期防回归计划

## 1. 四层审核闭环

| 层 | 触发 | 输入 | 必跑内容 | 失败动作 | 证据新鲜度 |
|---|---|---|---|---|---|
| PR gate | 三仓任一 PR/commit | current compatibility manifest | T0、T1、contract、quality、architecture、receipt validator | required check 阻断合并 | 当前 result triplet |
| Daily T2 | 本地 Windows runner 每日 | 真实 catalog、companies/dayu/Dropbox 只读权限 | real samples、root fingerprint、bundle、scan health、legacy hit、SLO | 阻断 release；创建结构化 finding | <=24h |
| Weekly T3 | 每周及发布前 | provider 凭据、临时 wiki | CN/HK/US 首次下载、二次零下载、provider contract | blocked/failed 告警；不得沿用旧绿 | <=7d |
| Release T4 | 每个发布波次 | 明确授权、最小 cohort、rollback | before/apply/after/rollback、真实用户旅程、SLO | 自动停波次并回滚 | 当次窗口 |

## 2. 每次动态审核的强制检查

- Triplet：报告必须绑定三个完整 commit、contract/schema/command/scenario/policy hashes。
- Samples：companies-only、dayu-only、Dropbox-only 各>=2 且 uniqueness/freshness 有效。
- Behavior：exact/latest/artifact 用户旅程结果和 reason taxonomy 正确。
- Side effects：下载、写入、解析、LLM、artifact read 与预算逐项对账。
- Safety：production catalog/source roots 指纹不变；T2 只写隔离 audit output。
- Health：scan error/interrupted 增量、artifact binding、legacy hits、SLO、provider drift。
- Integrity：report 原子完成、签名/hash 正确、无 skip/xfail/partial output。
- Trends：与前一合格报告比较，不只看绝对绿色；关键指标恶化超预算即失败。

## 3. 动态审核产物

```text
assurance/runs/{run_id}/
  run_manifest.json
  triplet.json
  scenario_results.json
  sample_registry_snapshot.json
  side_effect_ledger.json
  root_fingerprints.json
  scan_health.json
  performance.json
  provider_contracts.json
  findings.json
  verdict.json
```

`verdict` 只能是 `pass`、`failed`、`blocked`。报告必须先写临时目录，校验完整后原子发布；半报告不能替换最近一次完整报告，也不能延长其 freshness。

## 4. 失败分级与响应

| 级别 | 例子 | 响应 |
|---|---|---|
| P0 | 未授权外部写、数据损坏、越权下载 | 立即停止/回滚、冻结发布、用户告警 |
| P1 | Dropbox/dayu-only 回归、错误复用、latest 错报、artifact 篡改仍命中 | 阻断合并/发布，创建修复 FC，24h 内 owner |
| P2 | scan health/SLO/绑定率显著恶化、真实层过期 | 阻断发布，限定时间恢复；不得豁免为绿色 |
| P3 | 非关键趋势或文档偏差 | 登记 owner/期限；下一周期验证，不得无限延期 |

P0/P1 发生后，修复不仅要加回归测试，还要新增对应 AUD/UJ/功能 scenario 或增强 oracle，保证同类错误以后由动态审核自动发现。

## 5. 样本轮换与防失真

- 样本按 hashed ID 管理，不依赖绝对路径；每次运行重新验证 root uniqueness、source bytes 和 provenance。
- 每个 root 至少两份样本，避免单文件偶然通过；每季度或发生 provider/schema 变化时轮换其中一份。
- 固定样本验证确定性，轮换样本验证泛化；两类都必须通过。
- 样本移动、删除、重复到其他 root、sidecar 过期或失去权限时，审核状态 blocked，不得自动换成容易通过的样本。
- 真实内容不得上传到 CI artifact；保存 hashes、脱敏 metadata、trace 和本地 evidence locator。

## 6. 审核系统自测

AUD-01~08 是 required test。每次修改 audit runner、report schema、freshness、sample registry 或 release gate 时，必须注入：陈旧报告、错误 triplet、缺样本、root fingerprint 变化、health 恶化、provider 无权限、receipt 篡改、runner 半报告。每种故障都必须让 release gate 非零退出。

## 7. 长期关闭标准

项目不能因为一次发布绿色就停止审核。Phase 15 完成后仍持续：每 PR T0/T1、每日 T2、每周 T3、每波 T4。若动态审核连续失效或证据过期，项目“发布资格”自动降为 blocked；历史 complete 只代表当时已验收，不代表当前仍健康。

