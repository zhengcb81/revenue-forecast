# ZR-204 工作单元卡（preflight）— DB busy/locked/operation lock/timeout/paused 统一 taxonomy

- 领取时间：2026-08-14T13:30Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-204`；units.ZR-203.status=accepted + closure.next=ZR-204。
- 依赖：ZR-203（accepted ✅）。Registry 依赖列=ZR-203。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 C 锁 taxonomy。ZR102-F2 已证明：raw `database is locked`（OperationalError）被 filing 标 fatal/不可重试，而结构化 `CatalogOperationLockedError` 才被映射 retryable；08-12 发现 37/39 同一问题。本卡在 wiki 建立唯一分类真源：所有 raw 形态（SQLite OperationalError/busy/locked、operation lock、timeout、paused）映射到统一 code+retryable；**非锁错误不得误标 retryable**。
2. **production entrypoint 是什么？** wiki CLI 错误发射点（resolve/ensure/close-gap 的 `{"error_type": type(exc).__name__, "error": ...}` 形态——现对 raw OperationalError 发射 `OperationalError`，filing 无法识别）；`lock.py` 的 CatalogOperationLockedError；CLI 的 paused RuntimeError 文本。
3. **哪个 current-triplet 行为是 RED？** raw SQLite lock 形态无结构化映射（ZR102-F2 fresh 证据：filing 侧 fatal）；CLI 发射的 error_type 形态不统一（OperationalError/RuntimeError/...）。
4. **允许改哪些文件？** wiki `src/company_wiki/source_catalog/error_taxonomy.py`（新模块）+ `cli.py`（错误发射点接入分类器，最小 diff）+ `lock.py`（如需，仅加分类引用）+ `tests/unit/test_error_taxonomy.py`；revenue 侧 receipts/ZR-204/** 与 state.json。禁止：改锁获取语义、改 filing（ZR-205 消费）、真实 catalog 写。
5. **下一单元解锁条件？本单元不解决什么？** 解锁 ZR-205（filing deadline-aware retry 消费统一 code）。本卡不实现 filing 侧 retry；不改锁本身。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-203 accepted（机器状态；closure.next=ZR-204）。
- [x] triplet 冻结：revenue `26d70c5c…` 之后的最新 closure 提交（领取时重读）；filing `83c638e…`；wiki `354f5566…`。
- [x] 分类矩阵预研（代码事实）：wiki CLI 错误发射 `error_type=type(exc).__name__`（identity_cli.py:69、normalizer.py:335 等形态）；lock.py CatalogOperationLockedError；paused 以 RuntimeError 文本出现（control.py:886、cli.py:1035-1036）；SQLite busy/locked 现仅 CatalogStore busy_timeout 缓解。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（产品）+ revenue（assurance 收 receipt）。
- **Current-state drift verdict**：`still_missing`——无统一错误 taxonomy。
- **Acceptance criteria**：`classify_error()` 覆盖 raw 形态矩阵：sqlite3.OperationalError("database is locked"/"database is busy")→catalog_busy(可重试)；CatalogOperationLockedError→catalog_locked(可重试)；timeout 类→db_timeout(可重试，有界)；paused 文本→worker_paused(可重试)；其余一切→fatal(不可重试)——**非锁错误不得 retryable**；CLI 错误发射统一为结构化 `{error_type:<code>, error, retryable, status}`；taxonomy 版本化（schema_version + N/N-1：未知 error_type→fatal）；hermetic 测试 + wiki unit 绿。
- **Stop conditions / handoff**：改锁语义、filing 侧改动、真实 catalog 写 → 立即停止。
