# I-03-A 兼容矩阵 — 旧版本兼容与授权失效迁移

范围：旧实现 = 冻结锚点版本（gap_plan `d18391b7…`、authorization `f858a369…`、close_gap `117c8166…`）。新契约 = decision.md D1—D6。实施动作全部归 I-03-B/C；本表仅声明迁移语义，不改产品。

## 1. 行为迁移表

| # | 旧行为（冻结版本） | 新契约（D 条款） | 兼容性 | 迁移动作 | 执行卡 |
|---|---|---|---|---|---|
| M1 | 按 `fiscal_year` 单整数分组（gap_plan L143-157） | `(kind, period_start, period_end)` 三元组键；fiscal_year 派生标签（D1） | **不兼容**（分组语义变更） | gap 计划分组键重建；旧计划输出不迁移，直接按新键重算 | I-03-B |
| M2 | 缺 fiscal_year 候选/句柄静默丢弃（L145-147, L154-156） | 显式 `period_confidence=explicit_unknown` 桶（D1） | 不兼容 | 增补 unknown 桶；历史静默丢弃项重新枚举 | I-03-B |
| M3 | `max(accession 字典序, amended)` 定新近（L167-170） | `filed_at`(+修订链) 定新近；禁 ID 序（D3） | **不兼容**（persisting defect 修复） | 新近性函数重写；正向/反向 oracle C01/C02 复验 | I-03-B |
| M4 | `not_published` 单布尔混三态（L188） | not_published / already_covered / no_gap 独立字段 + latest_status 五值枚举（D4） | **不兼容**（输出 schema 变更） | GapPlan/结果 schema 增字段；消费端（filing、revenue source_preparation）同步读取新字段 | I-03-B / I-03-D |
| M5 | future 候选仅从 gap 剔除（L136-141） | 不变语义，保留 future 桶 + 不阻断 as_of 时点 not_published | **兼容**（语义延续） | 无需迁移；加 oracle C13 固化 | —（保留） |
| M6 | provider_error → provider_unavailable=true，保留本地不称 up-to-date（L113-133） | 同语义升格为 `latest_status=unknown_provider_failed` | 兼容（字段化） | 布尔映射到枚举值；oracle C11 固化 | I-03-B |
| M7 | `_hash_gap` 仅含 request_id/as_of/fiscal_year/accession/布尔（L214-246） | canonical JSON + 全资格字段 + policy epoch（D6） | **不兼容**（hash 值全域变化） | 见 §2 授权失效迁移 | I-03-C |
| M8 | close-gap 取 `actionable[0]` 单候选、`gap_closed_downloaded` 收尾（close_gap L263, L486-490） | 有界批次 max_batch_size=8、completed_partial + remaining 保留（D5） | **不兼容**（事务语义变更） | CloseGap 事务改批次执行；结果 schema 增 processed/remaining | I-03-C |
| M9 | `CloseGapBinding`/`DownloadAuthorization` 仅绑 accession 成员 | 绑定面继承 D6 全资格字段 | 不兼容 | binding/authorization 增字段，validate fail-closed | I-03-C |
| M10 | ZR-406 capture_ready 过滤、FC-801 policy_hash 校验、DL 系列失败拒绝 | **保留不变** | 兼容（窄正确性不回退） | 无 | —（保留） |

## 2. 旧授权 / 旧 gap_hash 失效迁移表

| 旧产物 | 旧 hash 是否继续有效 | 判定 | 消费行为 |
|---|---|---|---|
| 旧 `_hash_gap` 生成的 gap_hash（request_id/as_of/年/accession 组合） | **否** | hash_schema_version 不同 + 资格字段面不同 → 新验证路径必判不匹配 | 一律按 D6 重建 GapPlan → 新 hash → 新授权；禁止重算旧授权续期 |
| 旧 `DownloadAuthorization`（authorization.py v1.0 收据） | **否** | gap_plan_hash 绑定的旧计划已无法复现（M1/M3/M7 三重失效） | validate 判 `stale_gap_hash`，fetch=0，fail-closed |
| 旧 `CloseGapBinding` | **否** | 同上 | 重建 binding；已 staged 未提交字节按 DL-07 清理，不绕道提交 |
| 旧计划中已 completed 的下载（canonical 已入库，content_sha256 幂等） | 内容**保留** | 下载结果不因契约变更回滚（DL-09 幂等不变） | 本地文档继续可用（already_covered 成立）；其 provenance 记录保留旧 hash 作历史，不作活授权 |
| 旧计划中未完成候选（missing/newer_revision 残留） | **否** | 不丢弃、不静默（D5） | 下一事务重建计划时重新进入 missing/newer_revision |
| 旧 RuntimePolicySnapshot | **保留** | 唯一策略源不变（D6 不自创第二策略源） | policy_hash 继续作为 epoch 绑定输入 |

## 3. 兼容保证底线

- 失效全部 **fail-closed**：任何旧 hash/旧授权在新验证路径下只产生拒绝（stale_gap_hash / expired / not authorized），不产生静默放行。
- 不回写旧 PASS、不重算旧授权使之继续有效、不删除已入库文档（仅其授权记录退役）。
- 消费端（I-03-D）在读取到 `hash_schema_version < 1` 的计划时必须拒绝并触发重建，不得按旧语义解释。
