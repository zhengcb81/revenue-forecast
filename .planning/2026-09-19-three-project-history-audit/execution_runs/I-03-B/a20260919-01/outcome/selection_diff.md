# I-03-B 调用图差异与字典序删除证明 — attempt a20260919-01

## 1. 调用图差异（副本 vs 生产 gap_plan.py）

生产冻结锚点 `gap_plan.py` = `d18391b7fa7adf06bf882d013cd9ccae48b9fad24429c3ac66d61b68d907c79f`。
修改副本 = `iso/override/gap_plan.py` = `f0452bea4a5ca9701947582c6bdf7cd76ffd6501bbaef1f2ca3bcbf642076547`（完整 diff 在 `../changes.diff`，926 行）。

| 生产符号 | 副本状态 | 说明 |
|---|---|---|
| `build_gap_plan`（L95） | **保留，签名不变** | 调用者（acquisition/service/close_gap）无需修改，继续消费唯一输出；内部逻辑重写（新增三关键字：request_id/as_of_date/document_kind/entity/market/local_handles/remote_candidates/provider_error 全部保留） |
| `_candidate_filed`（L77） | 重写 | 改为 `_candidate_dates`（filed_at → filing_date → published_date 受信映射 + accepted_at）返回 (filed, accepted) |
| `_candidate_year`（L73） | **删除** | fiscal_year 单整数分组键废弃（D1/M1），改为 `_period_key`（kind\|period_start\|period_end 三元组）+ `_derived_fy`（period_end 年派生展示标签） |
| `_candidate_accession`（L81） | 重命名 `_candidate_id` | 仅作哈希确定性 tiebreak 与身份，**不再决定新近性** |
| `_candidate_amended`（L85） | 保留 | 用途收窄：仅同日修订链判定（D2），不再作 max() 次级键 |
| `_usable_handles`（L89） | 重写 `_usable_handles_split` | ZR-406 语义保留；capture_ready=False 句柄显式进 `unusable_local` 审计桶（不再静默消失） |
| `max(remotes, key=(accession 字典序, amended))`（**L167-170**） | **删除** | 由 `_newest_remote` 取代：按受信 filed_at 分箱 → max 日期 → `_same_day_state`（恰一 amended 子文档+基准则 ordered，否则 ambiguous_same_day）；**代码中不存在任何按 accession 排序的新近性判定** |
| `local_by_year` / `remote_by_year`（L143-157） | **删除** | `_families`：按三元组期间键分组；缺 period/缺日期/日期冲突 → 显式 explicit_unknown / conflicting / unknown_missing_date 桶（旧 `continue` 静默丢弃行为删除） |
| `not_published = not missing and not newer_revision`（**L188**） | **降格** | not_published 保守恒 False（I-03-A 遗留：adapter 无穷尽知识声明）；三态拆为独立字段 `already_covered` / `not_published` / `no_gap` + `latest_status` 五值枚举 |
| `future` 过滤（L136-141） | 语义保留升格 | filed_at > as_of → 显式 `future` 桶，不阻断 as_of 视图（C13），不再参与 eligible |
| `_hash_gap`（**L214-246**） | 重写（D6） | canonical JSON（sort_keys, ensure_ascii=False, 紧凑分隔符）SHA-256；全资格字段入 hash：entity/market/kind/period_start/period_end/fiscal_year/provider/id/filed_at/accepted_at/revision/amended/url + 计划级 request_id/as_of/not_published/provider_unavailable/provider_reason/latest_status/no_gap/hash_schema_version=1；候选仅在哈希排序键（D6 冻结序）内出现 provider id，**仅保证确定性，不参与新近性**。授权 epoch/policy_hash 绑定归 I-03-C，未触碰 |
| 新增 | `_candidate_dates`、`_date_state`、`_period_key`、`_derived_fy`、`_families`、`_same_day_state`、`_newest_remote`、`_batch_key`、`_invert`、`_candidate_note`、`_qualification`、`_notes_payload` | D1/D2/D5/D6 纯函数支撑面 |

## 2. 新近性领域 字典序删除证明

- 旧实现 `max(remotes_here, key=lambda c: (_candidate_accession(c), _candidate_amended(c)))`：.accession 字符串字典序直接决定"最新修订"，被 probes `newer_date_lower_id` / `older_only_remote` 双向证伪。
- 新实现 `_newest_remote`：`by_date.setdefault(_date_state(c)[1])` 按**受信披露日期**分箱 → `max(by_date)` 选最新日期 → 同日按 `_same_day_state` 冻结链规则。accession 只出现在：
  1. `_sort_key`（哈希确定性 tiebreak，位置优先级最低之一，D6 冻结）；
  2. `_batch_key` 尾位（period_start DESC、filed_at DESC 之后的等值 tiebreak）。
  两处都保证"允许的重排不改变语义输出"（C01/C03 reverse_order_equivalent 断言 pass）。
- `_batch_key` 的 DESC 用倒码 `_invert`（0x10FFFF−ord）实现纯函数全序，未引入外部状态。

## 3. 修前/修后（after/gapbefore-after-results.json 摘要）

- 修前（baseline 副本）：21 例中 20 fail / 1 pass。
- 修后（override 副本）：21/21 pass。
- 唯一修前 pass = `C05`：missing **集合**恰好三个候选、经 sorted() 排序后与固定 expected 相同——旧行为撞中集合结果但**无三元组期间键结构**（missing_period_keys 断言依赖新字段，属 not_applicable 域；修后结构断言真实覆盖）。G-B5a/B5b 修前 fail 仅因新增审计字段（unusable_local / latest_status）缺失，其字典序无影响域的部分如实标注。
