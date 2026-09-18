# `B.VR-r3` 复审发现处置表（R3：第五 root 隔离注册）

复审记录：[reviews/B.VR-r3.json](../reviews/B.VR-r3.json) — **`approve_with_findings`**，0×P0 / 0×P1 / **3×P2** / **3×P3**。
复审身份：独立只读会话（自己的 temp 目录、只写这一个 JSON 记录）。它**独立重跑**了主跑 / 变异 / `--verify`，
逐个复现了记录里的数字（`scan` 290 B / `49456e04…`、counts `roots 1 documents 2 sources 2 locations 2`、
两条 `reused_exact`、两次 `verified` 59 B、candidates 2、未注册 root exit 1、CFG-01、deny `['missing','missing']`），
并**重算磁盘摘要**确认 `open` 返回的确实是磁盘字节；唯一不可复现项是 `runtime_snapshot.snapshot_sha256`
（内含 `updated_at`，设计上每次不同——复审自己也这么判定）。

**C1/C2/C3/C4/C6 = confirmed**；**C5 = partly**（两条原因都变成了下面的 P2/P3 处置）。

| # | 严重度 | 复审发现（摘要） | 处置 |
|---|---|---|---|
| **F-R3-01** | **P2** | deny 只证明 **resolver 的决定**；**同一个 catalog 的字节入口** `SourceResolver.read_verified_bytes()` 用该 catalog 自己的 location 行建 handle 后仍返回 `ok=True / status="verified"`（只查根包含性 `resolver.py:2022`，从不查 `reusable_root_ids`）⇒ L04 的「不以平权绕过能力限制」只被覆盖了一条读取入口 | **接受并已改（两条都做）**：① **实测入证**——harness 新增 `deny.byte_entry_point`，用**deny catalog 自己的 location 行**重建 handle 后调用该入口，记录 `verified / 59 B / sha256 与磁盘相符`（另写入 `summary.deny_byte_entry_point_statuses = ['verified','verified']`）；② **收窄表述**——证据文件新增 §3bis 的**分层表**（决定层拒绝 / 枚举层不适用 / 字节层放行 / 消费者侧在 filing-fetch），并把 L04 对照行的「不以平权绕过」改为"覆盖一条入口 + 缺口登记"。产品边界登记为 **`F-BAR-11`**（findings.md） |
| **F-R3-02** | **P2** | 本次执行的授权依据（"owner choices 2026-09-17"）在 run 目录里**没有任何落盘物**；`r4-final-status.md:40` 当时仍把第五 root 注册列为**未授权** | **接受并已改**：新增 [owner-scope-decisions-2026-09-18.md](../owner-scope-decisions-2026-09-18.md)（两个问题的原文、owner 的两个答案、我据答案所做的**一处更正**、以及这份口径**授权/不授权**的清单）；harness 的 `authorisation_basis` 指向它；`r4-final-status.md` §1 同步改写。**另更正我自己的一处日期错误**：owner 的选择发生在 **2026-09-18**（本机时钟），我原先写成 `2026-09-17`，已全量改回 |
| **F-R3-03** | **P2** | 证据文件用**完成时**宣布了两处账本改动（"新增 F-BAR-10"、"新增 R3 行"），而当时 `findings.md` 没有 F-BAR-10、`progress.md` 没有 R3 行、`b-ar-record.md:104` 仍写"未做"；且 `F-BAR-1` 在本 run 里**同号两义**（`b-ar-record.md:84` = `.pdf.source` 文档；`findings.md:44` = 我的记账 bug） | **接受并已改**：三处账本**真的改了**（findings.md 新增 R3 节含 `F-BAR-10`/`F-BAR-11`；progress.md 新增 R3 行；b-ar-record.md §5 行改为"达成（隔离副本）"）；证据文件 §9 的引用改为"已落盘"，并**显式标注 `F-BAR-1` 同号两义**，避免再被读成同一件事 |
| **F-R3-04** | P3 | 隔离守卫只在主跑与 M1 上调用，**M2–M5 的变异树没有过守卫**（纵深防御缺口，非越界：变异树由硬编码模板在 `%TEMP%` 下生成） | **接受并已改**：`observe()` 现在对**每一棵**隔离树先跑 `guard_paths_are_isolated()` 并把返回的隔离事实写进观测记录；M2–M5 重跑仍 5/5 KILLED |
| **F-R3-05** | P3 | 正文把"2 个 `document_id`"记在 **CLI `query` 腿**上，而该腿保留的 `stdout` 已截断、`stdout_head` 只有 1 个 id | **接受并已改**：正文改引 `query_api.count = 2` 与该腿**截断前**解析出的 `document_ids`，并明写 `stdout_truncated: true` 与 `stdout_head` 的局限 |
| **F-R3-06** | P3 | 守卫返回的 `catalog_is_production` 是**硬编码** `False`，而判据就在上一行 | **接受并已改**：改为由同一条比较派生（`catalog_dir == PRODUCTION_DB.parent`），`isolation.catalog_is_production` 现在是算出来的 |
| **C5 = partly** | — | 未注册 root id 是由**空选择**分支（`scanner.py:760-761`）拒的，专属的 `unknown root_ids:` 分支（`:762-765`）对"整组未知"**不可达** | **接受并已改**：新增 `mixed-root-id-cli` 腿（`--root-id r4_fifth_root --root-id does_not_exist`）打到**专属分支**，实测 `unknown root_ids: ['does_not_exist']` exit 1，且 `scan_runs` 仍为 **1** ⇒ 合法根**没有**被顺带扫描。记录里同时保留两种拒绝消息，不再含糊 |

## 复审未要求、但本步自己登记的两条产品边界

- **`F-BAR-10`**：无 `runtime_policy.json` 时，声明了 sidecar 适配器的 `directory` 根走 **v1 目录遍历**，
  `.source.json` 侧车被当**独立文档**入库（M5 实测）。**不**声称它是生产那 3 份 `.pdf.source`
  （`b-ar-record.md:84` 的 F-BAR-1）的已证成因——生产快照是 `v2_scan_shadow=true`。
- **`F-BAR-11`**：deny 的效力边界（决定层 vs 字节层），见上表 F-R3-01。

## 处置后的状态

- harness：主跑 7/7 不变量、变异 **5/5 KILLED**、`--verify` 4/4（全部在处置后**重跑**）。
- 生产侧：`catalog.sqlite3` 49,677,344,768 B / mtime_ns `1788902601072747300` 未变，`-wal` 未动；
  三仓 HEAD 与 `git status --porcelain` 未变；`company-wiki/src` 143 文件树指纹未变。
- **R3 = 通过（隔离副本内）**；未做的仍是 **R4（跨仓端到端，需 owner 确认命令）**、
  **R5（`dropbox_stock` 3 份字节核验，需 owner 接受水合副作用）**、**R6（残余风险登记）**。
