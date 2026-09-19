# I-03-C iso 补丁与逐文件映射批准记录 — attempt a20260919-01

## 1. iso 副本范围（允许改动面 = 三文件）

| 文件 | baseline（= 生产锚点字节，已复验） | override 覆盖内容 |
|---|---|---|
| `gap_plan.py` | `d18391b7…` | 基于 I-03-B override（`f0452bea…`）副本；**唯一改动**：`_hash_gap` payload 增计划级 `"policy_hash"`（D6 冻结字段，I-03-B 暂存位闭合），`build_gap_plan` 增 kw-only `policy_hash=""` 并透传两处调用点；其余（期间键/四态/newest/D5 排序/canonical JSON）原样继承 |
| `authorization.py` | `f858a369…` | schema `"1.0"`→`"1.1"`；`DownloadAuthorization` 增 `hash_schema_version=1`；build fail-closed（provider 必填、64 位小写 hex、canonical `…Z` 时点、正整数额度、非空 accession）；`receipt_hash` 改 canonical-JSON 嵌套 payload（accession 集 hash 内排序 → 获准集重排不变）；validate 顺序 fail-closed：版本门（旧收据显式失效、不 auto-upgrade/不补字段）→ receipt 自检重算 → stale_gap_hash → 过期（1 秒即过期）→ candidate.provider 必填（缺 provider 不再放行）→ accession → item/byte 额度 |
| `close_gap.py` | `117c8166…` | 仅绑定校验边界：`CloseGapBinding` 增 `hash_schema_version=1`（同版）；新增纯函数 `validate_close_gap_binding(binding, authorization)`（全共享字段同一值 + 同版，任一不同 → 精确拒绝，DL-03 fetch=0）。Gap 事务执行面（resolver/journal/lock 依赖）不复制，归 C15 执行面（handoff 声明 out_of_scope） |

## 2. 字段映射（继承 I-03-B 批准 + 本卡新增）

- candidate/handle 侧字段映射全部继承 I-03-B iso_patching.md §2（filed_at→filing_date→published_date；accepted_at/revision 影子 attr；kind 请求级+候选级；fiscal_year 派生标签；capture_ready ZR-406 语义）。
- 本卡唯一新增映射：`build_gap_plan(..., policy_hash=…)` → `_hash_gap(payload["policy_hash"])` —— 取值 = RuntimePolicySnapshot 的 `policy_hash`（**唯一策略源**，D6：不增设第二策略来源）；P0 fixture 取 epoch "P" 的冻结常量 `7b94b34c…`。
- close_gap `CloseGapBinding`（生产版 13-6 字段）与授权的同构绑定面 + `hash_schema_version`，由本卡 `validate_close_gap_binding` 消费——生产 close_gap.py（未复制）在 I-03-C 全事务绑定后可直接换用该纯函数校验（接口：两端对象、返回 str|None）。

## 3. 时间桩

- validate 的时钟以 `now: str` 参数注入（冻结时钟 NOW0="2026-07-01T00:00:00Z"、过期例 NOW_EXPIRED_1S=NOW0+1s）；**无 time 模块依赖、零生产修改** —— 面向纯函数面的冻结时钟注入桩（非生产时钟改动）。

## 4. 左界与停止条件遵守

- 三仓源码/测试/配置零改动（执行前后锚点 sha256 逐一重验相等）。
- 不自创第二策略源；不重算/续期旧授权（旧收据显式 invalidation 路径 = G-C4c）。
- 不为绿灯删断言：修前 5 项真实缺陷域全部如实 RED 记录（before/pre_fix_assertions.json），已正确窄面（过期/额度）not_applicable 如实标注。
