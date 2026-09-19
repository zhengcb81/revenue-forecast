# I-03-C 决策文档 — 授权/绑定/版本边界与 canonical 契约实施映射

- 卡片：I-03-C（父 I-03）；attempt：a20260919-01；角色：company-wiki 来源负责人；filing 为消费者 reviewer。
- 控制器约束：隔离实施。禁止修改三仓源码/测试/配置；只写 attempt 目录 A；禁止网络；禁止改真实 raw/catalog。生产锚点保持冻结字节：
  - `gap_plan.py` `d18391b7…`、`authorization.py` `f858a369…`、`close_gap.py` `117c8166…`（本次已重算，与卡内一致）。
- 继承：I-03-A D1—D6 契约 + I-03-B override planner（iso/override/gap_plan.py 以 I-03-B attempt 的 override 为基础副本，唯一改动 = 按 D6 接入 policy epoch）。I-03-B 遗留的 C15 批次执行面按 handoff 移交声明仍归后续；本卡只做绑定/授权/版本边界（D5 的批次事务技术依赖 resolver/journal/lock，非纯函数，保持 out_of_scope 记录）。

## 1. 输入冲突记录（裁决，单列不隐没）

- 执行串写 `P0 … provider=a-new、id=a-new`；卡 I-03-C 正文固定授权 `A0 provider=test、allowed_accessions=[a-new]`，且卡内 P0 仅列 `a-new`（accession）与锁定 `policy P`，未列 plan 级 provider。
- 二者不可同真：正例 `A0 授权 P0 通过` 要求被验 candidate 的 provider 等于 A0.provider（fail-closed，否则恰是 G-C4 缺 provider 默认放行缺陷被复刻）。
- 裁决（保守侧）：`id(provider_document_id)="a-new"`（卡与执行串一致）；**P0 candidate provider="test"**（与 A0.provider 相等，使卡自带正例成立）。执行串的 `provider=a-new` 按可证伪解释登记为「与 id 同指 accession」并在 open_questions 留高级 reviewer 复核。若 reviewer 改判 provider="a-new"，则所有含 provider 的字段/hash 值随之重冻结——不是静默替换，是显式重签 oracle。

## 2. P0 / A0 冻结定义（与 oracle.md、canonical/p0.expected.json 一致）

GapPlan P0 = `build_gap_plan` 对 ACME/US、kind=annual_report、as_of=2026-07-31、本地空、远端恰一候选：
`provider="test"`, `provider_document_id="a-new"`, filed_at=2026-04-01 (≤ as_of), accepted_at 缺(→ "")，revision 缺(→ "")，amended=false，url=`https://fixture.invalid/a`（仅字符串，绝不访问），period 三元组 2024-07-01→2025-06-30（FY2025，I-03-A D1），fiscal_year=2025。
预期桶：`missing=[a-new]`，`latest_status="newer_remote_available"`，`not_published=false`，`no_gap=false`，`hash_schema_version=1`，`policy_hash=POLICY_HASH_P`（epoch P，常量 = sha256(b"policy-epoch:P") hex，冻结于 oracle.md）。

A0 = `build_download_authorization(request_id="req-p0", gap_plan_hash=P0.gap_hash, policy_hash=POLICY_HASH_P, provider="test", allowed_accessions=("a-new",), max_items=1, max_bytes=100, expires_at="2027-07-01T00:00:00Z")`；冻结测试时钟 NOW0=`2026-07-01T00:00:00Z`（时钟以参数注入 validate，无 time 依赖——即时间桩；不修改生产）。

## 3. 接口映射（逐文件）

### 3.1 iso/override/gap_plan.py（基础 = I-03-B override）
| 符号 | 改动 |
|---|---|
| `_hash_gap` | payload 增加 plan 级 `"policy_hash"`（D6 冻结的计划级字段 I-03-B 暂存位）；其余 canonical 序列化/全资格字段原样继承 |
| `build_gap_plan` | 新增 kw-only `policy_hash: str = ""`，唯一透传给 `_hash_gap`；调用者契约不变（默认值向后兼容） |

### 3.2 iso/override/authorization.py
| 符号 | 新语义 |
|---|---|
| `AUTHORIZATION_SCHEMA_VERSION` | `"1.0"` → `"1.1"`（绑定面增字段 = M9 不兼容，旧收据 fail-closed） |
| `DownloadAuthorization` | 增 `hash_schema_version: int = 1` |
| `build_download_authorization` | build 期校验收紧：provider 必填（缺失 → ValueError，不默认授权）；gap/policy hash 必须 64 位小写 hex；expires_at 必须 canonical `YYYY-MM-DDTHH:MM:SSZ`；allowed_accessions 非空且逐项非空；max_items/max_bytes 正整数。receipt_hash 改为**canonical JSON 嵌套 payload** SHA-256（accession 集合在 hash 内排序 → 获准集合重排不改变 receipt），消灭旧版逐字段字符串拼接歧义 |
| `validate_download_authorization` | 顺序 fail-closed：① schema_version 必须 == 当前版本（旧版显式拒绝 + 要求重新授权，不 auto-upgrade 不补字段）；② receipt_hash 重算自检（payload 篡改即拒）；③ `gap_plan_hash != plan_hash` → `stale_gap_hash`（D6：URL/filed_at/period/provider 等任一资格字段变化 → 计划 hash 必变 → 在此拒，fetch=0）；④ expires_at 过期字符串比较拒（过期 1 秒即过期）；⑤ candidate.provider **必填**且须相等（缺 provider 不再默认放行）；⑥ accession 成员检查；⑦ item/byte 额度（used+size ≤ cap） |

### 3.3 iso/override/close_gap.py（绑定校验面）
| 符号 | 语义 |
|---|---|
| `CloseGapBinding` | 增 `hash_schema_version: int = 1`（与授权同版）；`_txn_id` 面不变 |
| `validate_close_gap_binding(binding, authorization)` | 新增纯函数：binding 与 authorization 逐字段"同一值"校验（request_id/gap_plan_hash/policy_hash/provider/max_items/max_bytes/expires_at/allowed_accessions 集合），且双方 `hash_schema_version` 必须一致 —— 同版绑定，任一不同 → 拒绝字符串（DL-03 fetch=0）。生产 close_gap.py 的执行面（resolver/journal/lock 依赖）不复制，属 C15 执行面记录 |

## 4. 高级决策遗留（不是本卡未决）

- `not_published=true` 需 adapter 穷尽知识声明（I-03-A 记录的遗留依赖）→ 保持保守 false。
- C15 批次截断/completed_partial/close-gap 全事务路径属执行面，待绑定（(avoids 生产依赖)），本卡产出同版绑定校验函数供其消费。
