# I-03-D review.md — 独立 reviewer 复核（a20260919-01）

- Reviewer：独立 reviewer（非实施者）；日期：2026-09-19。权限遵守：三仓零写（`git -C company-wiki status --porcelain src/company_wiki/source_catalog/` = 空，rc=0）；本目录除本 review.md 外零写；无网络；重跑临时输出放 `%TEMP%`（reviewer run 后未回写 attempt）。

## 结论：accepted_scoped

资格授予 = **来源链 close-gap 资格，且仅限隔离副本（iso/override）与 A 内 fake 面**。未获资格（如实保留）：
1. 真实 provider / live 下载资格、生产写入能力 = I-07 范围（fake 通过不覆盖）。
2. "恢复缺失阶段"的生产重试注册接线（register_existing_raw 生产化/CLI）在 I-02 owner 完成前，G-D8 仅到消费面证据；按关闭标准原文，**本卡不得以 accepted 完全关闭任何生产恢复项，父项 I-03 不可因本卡标注全完成**（handoff blocked_by 如实列出，确认无误）。
3. 生产 raw/生产 catalog/生产 authorization 全程零触碰（锚点重算：close_gap `117c8166…`、authorization `f858a369…`、gap_plan `d18391b7…`，与卡一致）。

## 独立重跑（iso venv）

`iso\venv\Scripts\python.exe -X utf8 -B scripts\w03d_cases.py <reviewer-temp-out> <reviewer-temp-scratch>` → **rc=0，36/36 pass，stderr 空**，与 `raw-cli-logs/harness-run1.*` 及 `after/*` 逐项等价（除 recorded_at、scratch 路径占位与重跑副本场景下 G-D8/G-D6 幂等位 idempotent=true——即 reviewer 复跑同 content 再注册触发了**幂等路径**，反而独立验证了 R7/idempotent 分支）。

## 抽验逐点（读 ISO 副本源码 + after JSON 交叉）

1. **G-D5**：锁前计划 hash=P0、锁内三变体（url/filed/policy-epoch Q）每个 in-lock hash 均不同且存档（ledger per-case `plan_before_lock_hash`/`plan_in_lock_hash`/`binding_hash`）；`validate_close_gap_binding` 同值同版通过（变异不在 binding 内），拒绝发生在真实校验出口（stale_gap_hash 门 + `authorization_probe`="authorization is bound to a different gap plan (stale_gap_hash)" 为独立调用 `validate_download_authorization` 的返回）；fetch 事件全 0，catalog before==after；stream	if reached 反有 fail（harness `fail_on_call_stream` 断言）。✓
2. **G-D6**：MAX_BATCH_SIZE=8 单据化；场景 cap=max_items=1 演示同一截断选择器；A（新期间优先）fetch=1/bytes=2/raw_saved=1/registered=1 → completed；B 零 fetch 事件 → pending_next_batch；status=completed_partial、processed=1、remaining=1、pending=[a-pB]；`remaining-gap-semantic.json` 按期 covered/pending、remaining_gap=1、claim_allowed=false —— 未对全计划报绿。✓
3. **G-D7**：两场景各恰 2 条 bytes_received（60→120 如实记录，chunk2 over_cap=true/stream_stopped=true，物理 120 留档，单 chunk 超额另记 over_cap_chunks）；raw_saved=0/registered=0、status=failed、reason=byte_cap_exceeded_in_stream、catalog 无新行、commit=0；provider 消费恰 2 chunk（流在超额处停）。✓
4. **G-D8**：run1 fetch=1/bytes=1(40B)/raw_saved=1/registered=0、status=failed、raw+sidecar 保留（自然标签 `a-reg_c7ab8ff37152.pdf(.source.json)`，无按名清洗）；run2 `resume_registration` 仅恢复注册：无 provider_fetch_attempt/bytes_received 新事件、fetch_events=0、R 门重验成功、registration_succeeded(idempotent=false)、status=completed；`resume_refused` 无 prior raw_saved 证据的拒绝分支在代码在场。✓（见问题 2 的 gates 计数偏差）
5. **G-D9**：三变体事件全 0；变体1 provider_error + 本地 capture_ready → 完全 reuse、provider_unavailable=true、not_published=false（保守终值）；变体2 空成功 → unknown_empty_success、missing=[]、不宣称 not_published；变体3 本地可复用(local file 更新) vs 远端旧档 → 只 reuse，零下载。✓
6. **changes.diff**：仅含 close_gap.py + authorization.py 两条 diff 轴（baseline→override 与 生产原件→override）；gap_plan.py 零改动（override sha `81b08aab…` == I-03-C override 实测字节一致）。生产 hash + porcelain 实测如上。未借用生产 config（commands.json config_paths=[]，harness 内构造 tmp binding/auth/case 树）；fake provider/samples 最小 catalog/sqlite 壳、oracle 预期、事件 ledger 全部在 A 内。✓
7. **oracle.md 冻结性**：mtime 序 oracle.md 19:02:29 < authorization override 19:04:13 < close_gap override 19:22:01 < after 19:26:09 —— oracle 先于实现落盘；每例含独立手推预期与数值表；after 的错误码（stale_gap_hash/byte_cap_exceeded_in_stream/raw_saved_registration_pending/…）与四事件类型逐一与 decision §1 事件表对齐，`fetch_events` 数字仅作兼容计数不替代事件流。✓
8. **越权检查**：未重造 production writer（ MinimalRegistrar 的 R1–R7 为 attempt 内最小引用壳，见问题 4）；未为防重复另建生产 file registry（documents 表仅限 tmp case 树 + attempt-internal，声明"不出借给生产"）；未在未批准下采用多候选策略（批次 = D5 冻结有界 min(max_items,8)）。✓
9. **_BARRIER_HOOK**：iso 副本模块级 `_BARRIER_HOOK=None`、恒 no-op 默认；harness 仅 G-D5 注入模块属性以在两条 rediscover 之间变异世界；产品零改动（生产锚点重算一致）。不构成产品允诺边界改动——**不是产品行为变更**（隔离侧测试 seam，decision §3 + iso_patching §2 单据化）。✓

## 问题清单（均非阻断）

1. **binding.json 标签漂移**：`inputs_sha256."gap_plan.py(inherited I-03-C override)" = f0452bea…` 实为 **I-03-B** override hash；实际继承文件重算 = `81b08aab…`，恰为 I-03-C override（实测字节一致，P0.SHA 复算链路仍成立）。属记录性笔误，建议后继更正标注（hash 本体在 iso_override_sha256 正确）。
2. **Gates 证据缺 R7 行**：oracle/decision 预期 registration_succeeded "gates=R1..R7"；实际 `gates` dict 仅记录 R1–R6（R7 的谓词逻辑存在：retired/quarantined 拒、已注册幂等拒绝/成功，但 R7 名下结果未写入 gates）。R7 行为由 MinimalRegistrar 代码 G-D8 idempotent 分支间接验证，建议后继补 R7 键或在单据中修正口径。
3. **G-D7 授权输入偏差**：oracle 输入写 `max_items=1`，harness 实用 `max_items=2`（单候选场景下两值可观测行为等价：批内仅 1 流），但与冻结 oracle 字面不一致——宜在 oracle.md 或 harness 注释落地一处修正/说明。
4. **G-D8 run1 顶层 reason 措辞**：实际 top-level reason="remaining_gap > 0 (explicit pending retained)"，注入的 Failure 原因位于 gap_items.reason（"registration: …Gate-F5…")与 ledger `run1_registrar_injected` 注记中；oracle 预期 phrasing 为"txn 失败理由=registration: injected Gate-F5"。语义一致、字面错位，可接受。
5. **open_questions 三条如实**（C15 8-截断未以 max_items≥9 独立场景证明——与 I-03-B review 一致的遗留；G-D9 空成功/无本地为名义授权收据的静态模拟；policy epoch Q 经 plan 级 policy_hash 传播未设第二策略源）。未见隐瞒。

## 保留案例（实现者未用变化，供后继复验）

- 复跑同 scratch 的 G-D8+G-D6 二次注册路径：同 content_sha256 再注册 → `registration_succeeded(idempotent=true)`、零 raw 重写、catalog 单行——本 reviewer 重跑已实际触发并记录 PASS（见重跑 diff：ids/piggyback 字段唯一差异为 idempotent=true）。
- 后继卡（尤其 I-02 生产化与 I-03-C/D 合入）应重放：max_items=3 三缺期批选择（验证 D5 排序批切分 + completed_partial 计数）与 remote_size 超 max_bytes 的 plan 级预拒（负例）。

## 资格声明复述

- 本 review 仅授予来源链 close-gap 的隔离资格；生产资格、真实 provider/liv e 下载资格显式不授予（I-07）。
- I-02 对应恢复项（生产 register_existing_raw 接线）未完成 → 本卡按关闭标准**不得宣布完全关闭**；**父项 I-03 不能因本卡标注全完成**——handoff blocked_by 与卡关闭标准一致，确认如实。
