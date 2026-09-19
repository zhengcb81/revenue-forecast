# I-03-C Oracle — 运行前冻结（独立预期，未调用被测函数生成）

- 契约来源：I-03-A decision.md（D1—D6，hash `96322984…`）+ oracle.md（`dd5a5769…`）+ compat-matrix（`09040e46…`）；I-03-B override planner（`f0452bea…`，继承入口/边界）。
- **先于实施冻结**：canonical bytes 与 SHA 由 `scripts/canonical_p0_ref.py` 独立序列化代码计算（自写 canonical-JSON sorted-keys walker，未 import 任何被测模块，未调用 `_hash_gap`/生产 helper），并自校验与 stdlib canonical 形式逐字节一致。产物 = `canonical/p0.expected.json`。

## P0 冻结值（canonical/p0.expected.json 为准）

| 项 | 冻结值 |
|---|---|
| POLICY_HASH_P（epoch "P" = sha256(b"policy-epoch:P")） | `7b94b34cbb0596ed87c97f06ff1a337ea55d56fce839a19ee805f91cd58f3ea0` |
| canonical bytes 长度 | 786 |
| **P0 SHA-256** | **`b9c1847975c88dd226ef061d72630bb498be5374f80ac9c4553120583c84ba24`** |

### P0 payload 逐字段映射表（canonical JSON，sort_keys 语义； tutti 资格字段 = I-03-A D6 白名单）

| payload 键 | 值/来源 |
|---|---|
| `hash_schema_version` | 1（D6） |
| `request_id` / `as_of_date` | "req-p0" / "2026-07-31"（计划级 D6） |
| `document_kind` / `entity` / `market` | "annual_report" / "ACME" / "US" |
| `latest_status` | "newer_remote_available"（missing 非空 → D4/I-03-B 判定表） |
| `not_published` / `provider_unavailable` / `provider_reason` | false / false / null（I-03-B 保守侧） |
| `no_gap` | false |
| `policy_hash` | POLICY_HASH_P（**本卡新增的 D6 计划级绑定**，I-03-B 暂存位闭合，epoch P） |
| `missing[0]` | `{entity:ACME, market:US, kind:annual_report, period_start:"2024-07-01", period_end:"2025-06-30", fiscal_year:2025, provider:"test", id:"a-new", filed_at:"2026-04-01", accepted_at:"", revision:"", amended:false, url:"https://fixture.invalid/a"}` —— 恰 13 键，D6 资格白名单，缺一/多一均违规 |
| `reuse[] / newer_revision[] / future[] / superseded_remote[] / unusable_local[] / ambiguous_candidates[] / conflicting_candidates[] / unknown_candidates[]` | 全空（本地空、恰一 eligible 候选） |

- URL 仅字符串；provider="test" 与 A0.provider 相等（decision.md §1 裁决）。

## A0 冻结（指向 P0 哈希）

`schema_version="1.1"`, hash_schema_version=1, request_id="req-p0", gap_plan_hash=P0.SHA, policy_hash=POLICY_HASH_P, provider="test", allowed_accessions=("a-new",), max_items=1, max_bytes=100, expires_at="2027-07-01T00:00:00Z"。冻结时钟 NOW0="2026-07-01T00:00:00Z"（字符串参数注入；过期 1 秒用 NOW_EXPIRED="2026-07-01T00:00:01Z"）。

## 修前（对 iso/baseline = 生产锚点副本）真实失败断言（RED 域）

| ID | 注入 | 独立预期 | 修前实际域 |
|---|---|---|---|
| PRE-C1a | 仅 URL /a→/b 后重建计划（旧 `_hash_gap`） | gap_hash 必须不同 | **fail：hash 相同**（current_recheck `url_and_date_changed_same_gap_hash` 反例域本卡复现） |
| PRE-C1b | filing_date 2026-04-01→2026-04-02 | 同上 | fail：hash 相同 |
| PRE-C1c | A0(旧版 receipt 绑旧 hash) 验 P1 候选 | 必须拒 | fail：validate 返回 None（授权仍通过 = 缺陷） |
| PRE-C4a | candidate 缺 provider（None/""） | 必须拒 | fail：旧 validate `if provider and…` 空 provider 跳过 → 放行 |
| PRE-C4b | 旧版收据（schema_version="1.0" 收据构造，bootup-version 缺 hash_schema_version） | 必须显式拒绝/重授 | fail：旧 validate 无版本检查 → 放行 |
| PRE-C4c | expires_at 已过期（now>expires） | 拒 | not_applicable（旧 validate 已拒 — 已正确窄面，如实记录不造 RED） |
| PRE-C4d | 额度：used1/max1；used90+size20/max100 | 拒 | not_applicable（旧 validate 已拒） |

## 修后（iso/override）正反例

| Case | 输入 | 独立预期 |
|---|---|---|
| CANON-P0 | override planner 建 P0（policy_hash=POLICY_HASH_P） | gap_hash == `b9c18479…`（canonical-bytes-vs-ref.json 记录 payload canonical bytes 逐字节比对） |
| A0-POS | A0 验 candidate a-new（provider test） | None（通过）；fetch spy=0 |
| G-C1a | 仅 URL→/b 重建计划 | gap_hash ≠ P0.SHA **且** validate(A0, P1候选) 返回拒绝串；fetch=0 |
| G-C1b | 仅 filed_at→2026-04-02 | 同上 |
| G-C2 | 逐一单字段变异：entity→ACME2、market→HK、kind→interim_report、period_start→2024-07-02、period_end→2025-06-29、fiscal_year→2024、provider→other、id→b-new、filed_at→2026-04-02、accepted_at→"2026-04-03"、revision→"r1"、amended→true、policy_hash(epoch P→Q 同 plan 级位) | 每次恰一变异：hash ≠ P0.SHA 且 validate 拒（不得借相同 accession 跨对象复用 A0）；共 14 变异（13 资格字段 + policy epoch） |
| G-C3a | 候选列表逆序重建 | gap_hash == P0.SHA（等价重排 canonical 不变；accession 仅在确定性排序键内） |
| G-C3b | A0x 允许集 ("a-new","b-extra") vs 重排 | receipt_hash 相等（集合重排不变） |
| G-C3c | P1-part = P0 加本地句柄使 a-new 走 newer_revision 分区（同 accession） | 缺 in missing→newer_revision 状态分区改变 → gap_hash ≠ P0.SHA（分区不隐形） |
| G-C4a | items_already_fetched=1（max=1） | "item cap reached"；fetch=0 |
| G-C4b | used 90 bytes + 候选 remote_size=20（max 100） | "byte cap exceeded"；fetch=0 |
| G-C4c | 旧版收据（schema_version="1.0"） | "unsupported authorization schema_version"（显式失效路径，不 auto-upgrade）；fetch=0 |
| G-C4d | expires_at=NOW0 且 now=NOW0+1s | "authorization expired"；fetch=0 |
| G-C4e | candidate provider 缺 | "provider not authorized: <missing>"；fetch=0 |
| RECEIPT-TAMPER | A0.receipt_hash 改一位 | receipt hash 重算自检拒 |
| BINDING-OK | CloseGapBinding(hash_schema_version=1) 全字段同 A0 | validate_close_gap_binding → None |
| BINDING-MISMATCH | 各字段逐项改一（7 变体 + 版本 0） | 每次拒绝串；fetch=0 |

## 未决/记录

- C15 执行面批次截断与 close-gap 全事务（resolver/journal/lock）不在本卡（handoff 声明）。
- provider 裁决（"provider=a-new" vs 卡 A0 provider=test）见 decision.md §1，open_questions 单列。
