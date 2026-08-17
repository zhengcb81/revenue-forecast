# ZR-206 工作单元卡（preflight）— live writer + 49GB级只读 SLO/压力验收（阶段 C 出口卡）

- 领取时间：2026-08-16T22:10Z（UTC）
- 唯一入口：`audit_review/README.md` §0 `current_next=ZR-206`；units.ZR-205.status=accepted + closure.next=ZR-206；`uc next` 解锁列表含 ZR-206。
- 依赖：ZR-203~205（均 accepted ✅）。Registry 依赖列=ZR-203~205。

## 领取前五问（弱模型清单 §1）

1. **推进哪个用户目标/痛点？** 阶段 C 出口：生产 Reader 零写 + typed queries + 锁 taxonomy/retry 已就绪（ZR-201~205），但尚无 **live writer 并发**与 **49GB 级大 catalog** 的真实验收：README-06（live writer 长事务 + exact resolve 有界完成、不抢 BEGIN IMMEDIATE、download=0）、README-11（49GB/大证据表 p50/p95/p99、内存、锁等待在冻结 SLO、无 Python 全表扫描）、README-12（删接线 mutation 门必须红）、生产 T2 零写指纹。本卡把这些钉成数字并在真实 catalog（49.6GB、27.2M evidence_spans）上复放。
2. **production entrypoint 是什么？** `src/company_wiki/source_catalog/reader.py` 的 `ReadOnlyCatalogReader`（11 个 typed 方法）、`service.py` 的 `reader` 接线（status/query/query_filing_candidates/query_source_bundle/bundle_for_resolution/semantic_duplicate_groups）、CLI 只读命令（resolve/status/query/health）；writer 侧 `store.py`/`operation.lock`；真实 catalog `.source_catalog/catalog.sqlite3`（49.62GB，schema 1.2.0，evidence_spans 27.2M 行）。
3. **哪个 current-triplet 行为是 RED？** 无 live-writer 长事务并发验收测试；无 49GB 级 SLO 数字（README-11 未冻结）；无生产 T2 零写指纹；50 并发无 deadlock/下载/串线未验证（task_plan 出口要求）。基线测量（本机 2026-08-16）：status p95≈8.0s（证据表 COUNT 走 covering index，无 Python 全表扫描）、query p95≈1.8ms、entities_like p95≈0.6ms、location_counts p95≈33ms、document/source_sha/artifacts_for p95≤0.3ms、scan_health p95≈2.6ms。
4. **允许改哪些文件？** company-wiki `tests/contract/test_zr206_*.py`（新测试/验收脚本）+ `tests/unit/`（如需 reader 小工具，最小 diff）+ 只读验收运行器 `assurance/unified_completion/t2/`（revenue 侧，跑真实 catalog 只读测量，不改产品代码）；revenue 侧 receipts/ZR-206/** 与 state.json。禁止：改 reader 查询语义、改锁、改 schema、写真实 catalog（T2 只读）、下载。
5. **下一单元解锁条件？本单元不解决什么？** 本卡是阶段 C 出口：通过后进入阶段 D（ZR-301 首卡）。本卡不解决 status() 8s 本身（若超冻结预算则记 finding + successor；不在本卡改 reader 实现）。

## 领取前机械门（弱模型清单 §2）

- [x] ZR-203/204/205 accepted（机器状态；closure.next=ZR-206）。
- [x] triplet 冻结（领取时重读）：revenue `679fc33…`（docs commit 后）、filing `0e5d209…`、wiki `ad54026…`。
- [x] 基线预研（代码事实 + 本机实测）：reader 11 个 typed 方法全部 zero-write（mode=ro + query_only）；status() 8 个 COUNT 走 covering index（EXPLAIN: SCAN evidence_spans USING COVERING INDEX idx_spans_document）——无 Python 全表扫描；真实 catalog 49.62GB / evidence_spans 27,178,657 行；worker 当前无运行进程（最后一次 cycle completed）。

## 冻结 SLO 数字（dynamic_assurance_plan §3：实现前写成数字并由 reviewer 接受）

实测于 2026-08-16（真实 catalog 49.62GB，ReadOnlyCatalogReader，warm cache，n=11，毫秒）：

| 查询 | p50 | p95 | p99 | 冻结绝对门（p95×1.5 取整） |
|---|---|---|---|---|
| status | 7737 | 7974 | 7974 | **12000** |
| health | 7766 | 8002 | 8002 | **12000** |
| scan_health | 1.8 | 2.6 | 2.6 | **50** |
| query(kind,limit=100) | 1.3 | 1.8 | 1.8 | **50** |
| entities_like | 0.5 | 0.6 | 0.6 | **50** |
| location_counts(company_raw) | 20.0 | 33.1 | 33.1 | **250** |
| location_counts(dropbox_stock) | 7.5 | 11.8 | 11.8 | **250** |
| document/source_sha/artifacts_for/resolve_handle | ≤0.3 | ≤0.3 | ≤0.3 | **50** |

- 内存冻结门：Python 峰值分配（tracemalloc）**≤ 256 MB**（status/health 全量 COUNT 只物化 8 个 int）。
- 锁等待：live writer 持锁期间 reader 查询**有界完成**：p95 ≤ 12000ms 且不抢 `BEGIN IMMEDIATE`（writer 事务不被 reader 打断）；锁释放后成功；download=0。
- 回归预算：之后任何运行 p95 不得超过冻结门；daily 回归预算 ≤20% 且仍低于绝对门（dynamic_assurance_plan §3）。
- 50 并发 exact resolve：无 deadlock、无重复下载（download=0）、无结果串线（每请求 request_id 匹配自身）。
- 生产 T2 零写指纹：真实 catalog 读会话前后 `.source_catalog` 目录指纹（DB/WAL/SHM 字节 + 文件清单 + mtime）逐字节一致。

## 卡片字段（runbook §4）

- **Owner repo**：company-wiki（测试/验收）+ revenue（assurance 运行器 + receipt）。
- **Current-state drift verdict**：`still_missing`——live-writer 并发验收、49GB SLO 数字、T2 零写指纹、50 并发均未落地。
- **Acceptance criteria**：
  - `tests/contract/test_zr206_live_writer.py`（T1，hermetic）：writer 长事务持锁 → reader exact resolve 有界完成、不抢 BEGIN IMMEDIATE（writer 提交成功）、download=0；锁持续超过 deadline → 结构化失败不超时（复用 ZR-205 语义）；50 并发 resolve 无 deadlock/下载/串线。
  - `tests/contract/test_zr206_slo_49gb.py`（T1 可 hermetic 大表合成 + T2 真实 catalog 只读运行器）：p50/p95/p99 全部 ≤ 冻结门；tracemalloc 峰值 ≤256MB；EXPLAIN QUERY PLAN 无 Python 全表扫描断言（关键查询走索引）。
  - `assurance/unified_completion/t2/zr206_t2_probe.py`（revenue 侧运行器）：真实 catalog 只读指纹 before/after 逐字节一致 + SLO 实测落 JSON 证据；不修改产品代码。
  - READ-12 变异门：删除某只读入口 Reader 接线 → architecture/production-caller gate 红（复用 ZR-203 既有 gate，本卡补 mutation 测试若缺）。
  - wiki unit/contract 全绿；复杂度 ratchet 新文件 ≤10；独立 reviewer 复放 T2 运行器。
- **Stop conditions / handoff**：写真实 catalog、改锁语义、改 reader 查询语义、真实下载 → 立即停止。若 status() 实测超冻结门：记 finding + successor（不改实现）。

## Annex：T2 运行方式（只读）

- 真实 catalog：`C:\Users\郑曾波\Projects\company-wiki\.source_catalog\catalog.sqlite3`（49.62GB）。
- 运行器只做：打开 ReadOnlyCatalogReader（mode=ro + query_only）→ 11 个 typed 方法各测 n 次 → 指纹 before/after（catalog.sqlite3/-wal/-shm + 目录清单）→ 输出 JSON 证据到 `assurance/unified_completion/t2/evidence/`。
- 禁止任何 `store` 访问、scan、migration、download；worker 保持 enabled 状态不动（T2 真实现状，指纹窗口内若 worker 写 WAL 会如实记录在证据中并重新判定）。
