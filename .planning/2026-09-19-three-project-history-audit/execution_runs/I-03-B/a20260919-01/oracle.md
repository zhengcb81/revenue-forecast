# I-03-B Oracle — 本卡 level 冻结预期（per case）

- 契约唯一语义来源：I-03-A `decision.md`（D1—D6）+ `oracle.md` C01—C15。
- **引用 hash**：
  - decision.md = `963229846b06ed3b4f48d0d3192b444101b5e16e5a4989d53abdbd1a983e910d`
  - oracle.md = `dd5a57692a74f8bb664ef4b83b5a97dafad94cb519698037c4578a3cf8ec6358`
  - oracle-inputs.csv = `6b070c8eb979390bf455094713d2a59815c29dcbe01fa50cdfa31a832822bc18`
- 所有 expected 由 D1—D6 独立推导（见下），**不调用被测 planner 生成**。
- 本卡只实施**纯选择**：D5 的批次执行/事务语义归 I-03-C，不在本卡 planner 输出面（但保留 missing 排序 period_start DESC 以供消费）。
- I-03-A 遗留依赖沿用：`not_published=true` 需 adapter 穷尽知识声明（不存在）→ 本卡 planner 中 not_published 恒 false（保守侧）；C10/C13 保守分支按此验收。

## G-B1（=oracle C01 正向）— 远端更新、provider ID 字典序与日期相反

- 输入：L=z-old/2026-03-01/FY2025 capture_ready；R=[z-old(2026-03-01), a-new(2026-04-01)]；as_of=2026-07-31。
- expected（固定）：
  - `newer_revision == [a-new]`（精确单元素，id=a-new）
  - `reuse == [z-old]`（provenance 保留）
  - `missing == []`
  - `latest_status == "newer_remote_available"`
  - `not_published == false`
  - 修前必然失败：旧实现 max(accession 字典序) 选 z-old 为 newest → z-old ∈ local_accessions → reuse、not_published=true。
- 引用：I-03-A oracle.md C01（hash dd5a5769…）。

## G-B2（=oracle C02 反向）— 本地更新、远端仅旧

- 输入：L=a-new/2026-04-01 capture_ready；R=[z-old(2026-03-01)]。
- expected（固定）：
  - `newer_revision == []`（z-old filed 更早，不可能构成更新修订）
  - `reuse == [a-new]`（本地不降级）
  - `latest_status == "unknown_if_remote_confirmed_newer"`
  - `missing == []`
  - `not_published == false`（远端未确认最新，不得宣称）
  - 修前必然失败：旧实现选 z-old（唯一 remote，字典序 max）≠ local a-new → newer_revision=[z-old]。
- 引用：C02。

## G-B3（=oracle C01 缺本地 + D3 顺序等价）— 本地空、同期两修订、顺序反转

- 输入：L=[]；R=[z-old, a-new] 同 period_key（同一受信期间，period 齐全）。
- expected（固定）：
  - `missing == [a-new]`（恰一个：同族内新近性选择后仅最新进 gap；a-new filed 2026-04-01 > z-old 2026-03-01）
  - `newer_revision == []`（本地无旧版本，无"替换"语义）
  - 顺序反转（R=[a-new, z-old]）输出 id 集合与排序**完全相同**（日期定新近，与输入顺序无关）
  - `latest_status == "newer_remote_available"`
  - 修前必然失败：旧实现同 FY 两候选都进 missing（L180-182 整组并入），missing 含 2 个元素。
- 引用：C01 + probe `missing_same_period_two_revisions`（C03/C04 结构面）。

## G-B4（=oracle C13）— future 披露

- 输入：L=[]；R=[a-future filed 2026-08-01 > as_of 2026-07-31]。
- expected（固定）：
  - `future == [a-future]`（显式 future 集状态，非静默丢弃）
  - `missing == []`、`newer_revision == []`
  - future 候选不进任何可下载/可复用当期集合
  - `not_published == false`（无穷尽知识声明，保守侧恒 false）
  - `latest_status == "unknown_empty_success"`（等效保守级：响应无 eligible 候选、最新性未知）
- 引用：C13。

## G-B5（复合）— capture_ready=False + provider_error；合格多根同 bytes；不同期间同 FY

三个子断言（一个 case 编号，三段独立输入）：
- **B5a**：L=[capture_ready=False 句柄] + provider_error="x" → 该句柄不得出现在 reuse（ZR-406 保留）；`provider_unavailable=true`；`latest_status=="unknown_provider_failed"`；not_published=false。修前已 pass（旧实现 L89-92 已过滤）→ not_applicable 域，如实记录。
- **B5b**：两个本地根含同一 capture_ready 句柄（同 accession、同 period）+ R=[同 accession] → reuse 恰含 1 个去重句柄（多根同 bytes 复用，不产生重复下载计划）；`latest_status=="local_is_latest_confirmed"`（accession 命中确证）。修前部分 pass（reuse 集合行为近同但无去重与 latest_status 语义），以新字段断言为准判修前 fail。
- **B5c**：同 FY2025、两个不同 period_key（annual 2024-07-01→2025-06-30 与 interim 2024-07-01→2024-12-31）+ R 含两期各一候选 → 两期**分别**产出 gap 状态（各期 missing/newer 独立），不合并；period_key 各自 `kind|start|end`；planner 面排序按 D5 批次键 `(period_start DESC, filed_at DESC, provider_document_id)`（kind 为请求级已同质）：两期 period_start 相同（2024-07-01），filed_at DESC 决定 → r-annual（filed 2026-03-01）先于 r-interim（filed 2025-02-15）。
- 引用：C05（不合并）、C11/C12（latest_status）、ZR-406。

## I-03-A C01—C15 可复用子集（纯选择域）声明

| oracle 格 | 可复用性 | 本卡映射 |
|---|---|---|
| C01 | ✅ 直接复用 | G-B1 |
| C02 | ✅ 直接复用 | G-B2 |
| C03（同日有链→ordered） | ✅ 纯选择 | 追加用例 A-C03 |
| C04（同日无链→ambiguous） | ✅ 纯选择 | 追加用例 A-C04 |
| C05（三文种同 FY 不合并） | ✅ 纯选择 | G-B5c |
| C06（period 齐 FY 缺→键由三元组+派生FY） | ✅ 纯选择 | 追加用例 A-C06 |
| C07（缺 period→explicit_unknown 桶） | ✅ 纯选择 | 追加用例 A-C07 |
| C08（双日期缺→unknown_missing_date） | ✅ 纯选择 | 追加用例 A-C08 |
| C09（accepted<filed→conflicting） | ✅ 纯选择 | 追加用例 A-C09 |
| C10（空成功→unknown_empty_success, not_published=false） | ✅ 纯选择 | 追加用例 A-C10 |
| C11（provider 异常→unknown_provider_failed） | ✅ 纯选择 | B5a |
| C12（accession 命中→local_is_latest_confirmed） | ✅ 纯选择 | B5b |
| C13（future） | ✅ 纯选择 | G-B4 |
| C14（3 缺口全批，排序 period_start DESC） | ⚠️ 部分：planner 只产出排序后的 missing（D5 批次事务归 I-03-C） | 追加用例 A-C14（planner 面：missing 排序） |
| C15（9 缺口截断 max_batch=8） | ⚠️ 部分：批次截断/completed_partial 属执行面（I-03-C），本卡仅验证 missing 可完整产出且排序确定 | 声明为 out_of_scope(I-03-C)，不做截断断言 |
| C01/C12 hash 断言（url/date 入 hash） | ✅ 纯选择（D6 hash 面：本卡按 hash_schema_version=1 canonical 序列化重写 _hash_gap） | 追加用例 A-HASH |

**不可复用格**：C15 执行面（批次截断、completed_partial、remaining_count）→ I-03-C。
