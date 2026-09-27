# ZR-205 工作单元卡（preflight）— deadline-aware retry + 阶段错误透明转发

- 领取时间：2026-08-16T21:10Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-205`；units.ZR-204.status=accepted + closure.next=ZR-205；`uc next` 解锁列表含 ZR-205。
- 依赖：ZR-204（accepted ✅）。Registry 依赖列=ZR-204。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 C 锁 taxonomy 的消费侧闭环。ZR102-F2（fresh 证据）证明 filing 侧只认识结构化 `CatalogOperationLockedError` 类名形态，raw `database is locked` 被标 fatal/不可重试；ZR-204 已在 wiki 建立统一 taxonomy 并发射规范 code（catalog_busy/catalog_locked/db_timeout/worker_paused/fatal + retryable），本卡让 filing 消费这些规范 code，并把 retry 做成 deadline-aware（指数退避 + jitter + 上限 + 无 sleep 超 deadline），最终成功/失败都保留零下载与调用次数证据（READ-09/READ-10）。
2. **production entrypoint 是什么？** filing-fetch `scripts/fetch_filing.py` 的 `_run_company_wiki_json`（wiki CLI 调用 + 结构化 stderr 分类）、`_run_company_wiki_json_retry`（retry 循环，目前只认 catalog_locked、无 jitter/上限）、`resolve_filing`（五个调用点：identify/ensure/resolve/close-gap + PausedWorkerScope worker-status/pause/resume）、`main()` 响应信封（成功/失败都需带 calls/downloads/stage/attempts）。
3. **哪个 current-triplet 行为是 RED？** 规范 code `catalog_busy`/`db_timeout` 目前被 filing 标 fatal（`error_type != "CatalogOperationLockedError"` → fatal），与 ZR-204 taxonomy 的 retryable 相矛盾；backoff 无 jitter、无上限；失败信封无 stage/attempts/calls/downloads 对账证据。
4. **允许改哪些文件？** filing-fetch `scripts/fetch_filing.py`、`scripts/filing_contracts.py`（FilingFetchError retryable 集合 + stage/attempts 字段）、`tests/test_fetch_filing.py`、`tests/test_e2e_isolated_wiki.py`（e2e 断言改为规范发射形态）；revenue 侧 receipts/ZR-205/** 与 state.json。禁止：改 wiki taxonomy、改锁语义、改请求 schema、真实下载。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-206（live writer + 49GB 只读 SLO/压力验收）。本卡不实现 ZR102-F1（exact 模式无授权下载 → 移交 ZR-407 authorization-bound GapPlan，阶段 D）；不改 wiki 发射。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-204 accepted（机器状态；closure.next=ZR-205）。
- [x] triplet 冻结（领取时重读）：revenue `217b303…`（ZR-204 closure 后）、filing `83c638e…`、wiki `ad54026…`。
- [x] 现状代码事实：`_run_company_wiki_json` 仅映射 `CatalogOperationLockedError`→catalog_locked、`RuntimeError`+"paused"→worker_paused，其余→fatal；retry 只认 `catalog_locked`，backoff=5s×2^n 无 cap/jitter，sleep=min(backoff, remaining) 已有 deadline 约束；`FilingFetchError.retryable = {upstream_error, worker_paused, catalog_locked}`。

## 卡片字段（runbook §4）

- **Owner repo**：filing-fetch（产品）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——filing 未消费 ZR-204 规范 code，retry 无 jitter/上限/对账证据。
- **Acceptance criteria**：
  - `_classify_wiki_error(stderr)`：规范 code 直通（catalog_locked/catalog_busy/db_timeout/worker_paused/fatal）；N-1 类名形态（CatalogOperationLockedError→catalog_locked、RuntimeError+"paused"→worker_paused）保留；非 JSON/非对象/未知→fatal（fail closed，非锁错误不得 retryable）。
  - `FilingFetchError.retryable` 增加 catalog_busy、db_timeout；`FilingFetchError` 增加可选 stage/attempts。
  - retry 集合 = {catalog_locked, catalog_busy, db_timeout}；worker_paused/fatal 不自动重试（既有测试钉死）。
  - backoff：指数退避 5s×2^n、±20% uniform jitter、上限 60s、wait=min(jittered, remaining)（无 sleep 超 deadline）；每 attempt 打印尝试序号。
  - 信封对账：成功 envelope 增加 `calls`（wiki 子进程调用总数，含 retry 与 worker 编排）与 `downloads`（来自最终 resolution envelope 的 download_events，复用=0）；失败 envelope 增加 `stage`/`attempts`/`calls`/`downloads`（READ-09 attempt/jitter/elapsed 可对账；READ-10 到期失败保留证据）。
  - hermetic 测试：分类矩阵（规范 code + N-1 + 非 JSON）、catalog_busy/db_timeout retry 成功、jitter 边界、cap、deadline 耗尽（stage/attempts）、成功/失败信封对账、worker_paused 不自动重试；filing 全套测试绿（complexity ratchet 不恶化：fetch_filing.py ≤34）。
- **Stop conditions / handoff**：改 wiki taxonomy、改锁语义、请求 schema 变更、真实下载 → 立即停止。ZR102-F1 移交 ZR-407，不在本卡。
