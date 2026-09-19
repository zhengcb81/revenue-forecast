# I-03-D Oracle — 运行前冻结（独立预期，未调用被测函数生成）

- 冻结时刻：2026-09-19，先于 iso/override 任何修改与任何 harness 运行。
- 输入契约：P0/A0 继承 I-03-C 冻结（P0.SHA=`b9c1847975c88dd226ef061d72630bb498be5374f80ac9c4553120583c84ba24`，POLICY_HASH_P=`7b94b34cbb0596ed87c97f06ff1a337ea55d56fce839a19ee805f91cd58f3ea0`，epoch "Q" = sha256(b"policy-epoch:Q")）；NOW0="2026-07-01T00:00:00Z"；fake provider 仅消费本卡样本；URL 仅字符串、禁止网络。
- 每条预期全部独立手工推导（I-03-A D5/D6 + 生产锚点行为 + decision.md 事件类型表），不从被测代码生成。授权 A0 基线 = I-03-C A0（provider="test"，accession ("a-new",)，max_items=1，max_bytes=100，expires_at="2027-07-01T00:00:00Z"）；本卡场景可放大 max_items/max_bytes 形成新收据，均字段显式，不续期旧收据。

## 全局不变量（每个 case）

- I-D0.1 零网络：fake provider 内存面；basetemp/write root ∈ 本次 attempt 的 tmp 子树。
- I-D0.2 生产零改动：执行前后三仓锚点 sha256 重算相等（binding/commands 留档）。
- I-D0.3 事件流分型：provider_fetch_attempt / bytes_received / raw_saved / registration_succeeded 四类齐全才可宣称"额度/注册可观测"；`CloseGapResult.fetch_events` 计数不作为事件证据本体。
- I-D0.4 校验出口 = I-03-C 冻结面：`validate_close_gap_binding(binding, authorization)`（同值同版）与 `validate_download_authorization(auth, candidate, plan_hash, now, items, bytes)`（fail-closed 七步序）。

## G-D5 — stale binding 在真实校验出口拒绝（不发流量）

- 输入：A0 绑定 P0（ACME/US，missing=[a-new]，url /a，filed 2026-04-01，policy epoch P）。执行序：锁前 rediscover → **barrier（确定性插入点）** → 锁内 rediscover → 校验出口。三个变体逐一：V1 仅 URL /a→/b；V2 仅 filed_at→2026-04-02；V3 仅 policy epoch P→Q（plan 级位变更）。
- 预期（对每变体）：
  1. 锁内 rematerialized plan 的 gap_hash ≠ binding.gap_plan_hash（D6 恒等式：资格字段/policy epoch 任一变化 ⇒ hash 不同）；
  2. `validate_close_gap_binding(old_binding, old_auth)`：**通过**（binding 与收据同值同版）——变异发生在 provider 侧元数据，不在 binding 对象内；
  3. 旧 binding 在真实校验出口 fail-closed：stale_gap_hash 门拒绝，status=rejected，reason="stale_gap_hash"；
  4. fetch=0：provider_fetch_attempt=0、bytes_received=0、raw_saved=0、registration_succeeded=0（无新增 raw / 注册行；
  5. 对候选逐个独立 validate_download_authorization（plan_hash=锁内新 hash）返回 "authorization is bound to a different gap plan (stale_gap_hash)"——证明拒绝来自授权校验出口而非 harness 短路。
- 附：barrier=None（常态）时两计划同 hash、不拒绝（正例对照，G-D7a 复用该路径）。

## G-D6 — 两缺期、max_items=1：只 1 个获准，另一个显式待补

- 输入：remote 两候选 period A=`annual_report|2024-07-01|2025-06-30`（filed 2026-04-01，id a-pA）、period B=`annual_report|2023-07-01|2024-06-30`（filed 2025-04-01，id a-pB），本地空；授权 allowed_accessions=(a-pA, a-pB)，max_items=1，max_bytes=1000。
- 预期：
  1. `MAX_BATCH_SIZE=8` 单据化为常量；本场景实际上限 = min(max_items=1, 8) = **1**（非 8；语义单据必须写明）；
  2. 批内按 D5 序（period_start DESC 新期间优先）：A 先获准；
  3. A：fetch_attempt 恰 1、bytes_received 全链、raw_saved=1、registration_succeeded=1，`gap_items[a-pA].state=completed`；
  4. B：无任何 fetch 事件，`gap_items[a-pB].state=pending_next_batch`；
  5. 事务 status=`completed_partial`，processed_count=1，remaining_count=1，pending 列表=[a-pB]；
  6. `remaining_gap>0`：B 期间不得报 covered；**不得宣称全计划 gap 关闭**（禁止单候选下载后报 completed/gap_closed_downloaded）。

## G-D7 — max_bytes=100；fake chunks 60+60；remote_size 未知或谎报 80

- 输入：两场景共用：候选分块 60/60（总 120 实发）；场景 α `remote_size=None`（未知远端大小，按批准政策：validate 层不因未知大小预拒，额度在流内强制）；场景 β `remote_size=80`（谎报实发 120）。授权 max_bytes=100，max_items=1。
- 预期（α、β 各自）：
  1. validate 阶段（start 前）：α None→0 计入（0 ≤ 100 放行）；β 80 ≤ 100 放行 —— 计划/额度边界**不预拒**（"+size ≤ cap" 在验收口径下成立）；
  2. chunk1（60，累计 60）：bytes_received 恰 1 条（chunk_index=0, cumulative=60, over_cap=false）；
  3. chunk2（60，累计 120）：**事件照发**（cumulative=120 如实记录，over_cap=true，stream_stopped=true）；不得声称物理从未收到 >100；
  4. 发现超额即停：fake provider 流被 break，无 chunk3 及以后（stream seam 记录消耗序列，恰 2 个 chunk 由 provider 发出）；
  5. 合格 handle=0、raw_saved=0、registration_succeeded=0、status=failed，reason="byte_cap_exceeded_in_stream"；已收 120 字节的计数留档（可能单 chunk 超额在 bytes_received.over_cap 单独另记）；
  6. commit=0：临时 catalog 无新 registered 行。

## G-D8 — 下载成功+注册注入失败 → 重试只恢复注册（fetch 新增=0）

- 输入：单 missing 候选（40 字节 single-chunk）；一次成功的 raw 落盘后，注册面注入失败（R 门序之一拒绝）。
- 第一次执行预期：provider_fetch_attempt=1、bytes_received=1 条（40 bytes）、raw_saved=1（raw+sidecar 保留现场，不清洗）、registration_succeeded=0、status=failed、txn 失败理由=registration: injected Gate-F5；
- 第二次执行（同一 raw 现场，新 txn）预期：**新增 fetch=0**（无 provider_fetch_attempt、无 bytes_received）——R1–R7 门序重验通过（引用 I-02-C review.md 第 6 条与 I-02-C override canonical_writer.py 实现）、registration_succeeded=1（gates=R1..R7）、status=completed；无 raw 重写下（幂等）。
- 依赖标注：生产接线归 I-02 owner；本卡为"重试只恢复注册"的消费面证据。

## G-D9 — provider 异常 vs 空列表；本地可复用旧件 → 不触发未授权下载

- 变体 1（异常 + 本地 z-old capture_ready）：完全走 reuse、零 fetch（latest_status=unknown_provider_failed 继承 I-03-A C11 语义）；plan `provider_unavailable=true`、`not_published=false`；不写 not_published。
- 变体 2（空成功 + 无本地）：`latest_status=unknown_empty_success`，missing=[]；计划级 no_gap 处置成立；不宣称 not_published（穷尽性声明依赖未落地）；不触发无授权下载。
- 变体 3（本地可复用旧件 + 正常远端 stale 数据，非同一 accession）：无下载触发、只 reuse 本地（fetch=0 保持）；**不因本地可复用而触发任何 provider 下载**。
- 全三变体：`provider_fetch_attempt=0` 与 `raw_saved=0`、`registration_succeeded=0`；事件 ledger 中零 fetch 事件可重放。

## 数值预期（手算汇总）

| 场景 | 计数预期 |
|---|---|
| G-D5 | fetch=0；三变体 gap_hash 均不同；reason=stale_gap_hash |
| G-D6 | processed=1；remaining=1；pending=[a-pB]；A fetched、B unfetched |
| G-D7 | 累计=120；bytes_received 恰 2；合格 handle=0；raw_saved=0；registration=0 |
| G-D8 | run1: fetch=1 raw_saved=1 reg=0；run2: fetch=0 reg=1（gates R1..R7） |
| G-D9 | 三变体均 fetch=0；missing=[] 或 local_is_latest；无 not_published=true |

## 未决/依赖（blocked 登记）

- G-D8 生产接线（真实重试注册）依赖 I-02 owner 未完成项 → 本卡 evidence 到消费面 orb；真实 production 重试在 I-02 完成前不得由本卡宣称完成。
- provider 穷尽知识声明（I-03-A 遗留）→ not_published=false 为终值。
