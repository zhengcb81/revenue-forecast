# `B.VR-r4` 复审发现处置表（R4：跨仓端到端只读）

复审记录：[reviews/B.VR-r4.json](../reviews/B.VR-r4.json) — **`approve_with_findings`**，0×P0 / 0×P1 / **4×P2** / **4×P3**。
复审身份：独立只读会话（自己的 temp 目录，只写这一个 JSON 记录）。它**独立重跑**了 harness（四条腿的 stdout
**逐字节相同**：`d8aa3431…`/`b64f11b6…`/`8433b7ef…`/`5c6492b7…`）、复现 8/8 不变量与 12,476/33,122 与 `wiki_src`
指纹，并**自己哈希了那份年报**（4,172,424 B / `e39fbf9c…`，与 L1、与 B08-L2 一致）；`--verify` 5/5。
**C1–C4、C6 = confirmed，C5 = partly**（"零写入"的证据链有三条腿有缺陷）。

| # | 严重度 | 复审发现（摘要） | 处置 |
|---|---|---|---|
| **F-R4-02** | **P2** | 写面表里**唯一一行 "REACHED" 是错的**：resolve 路径**从不构造可写 store**——`cli.py:1165-1200` 不碰 `get_catalog().store`（对照 `:762` 的 ensure、`:1216` 的 close-gap），而是传 `store=get_catalog().reader`（`:1193`），reader 是 `mode=ro` + `PRAGMA query_only=ON`（`reader.py:165/188`）⇒ **没有** mkdir/WAL/迁移/commit；据此引用的 A05/A06 类比也不成立。该错句已传播到 `findings.md`/`progress.md` | **接受并已改（三处）**：harness docstring 的写面表、记录里的 `write_surface` 字段、[evidence/b-ar-cross-repo-reuse.md](b-ar-cross-repo-reuse.md) §2，以及 `findings.md`/`progress.md` 的对应行——全部改为"经产品 store 的 catalog 写入 **NOT REACHED**（只读 reader）"，并明写 `-shm` **只登记不归因**（只读 WAL reader 本身即足以造成） |
| **F-R4-01** | **P2** | `invariants.no_download_requested` 是**空断言**：harness 读 `summary['download_required']`，而 `summarise()` 从不产出该键；且 L3/L4 的 `downloads: 0` 只是**初始化的计数器**（`fetch_filing.py:1106`），不能单独当证据 | **接受并已改**：删掉该键，换成**可判定**的两条——`every_leg_reports_zero_downloads`（逐腿读 `downloads`）与 `allow_download_never_passed`（四条腿 argv 均不含 `--allow-download`）；记录里另加 `per_leg_downloads` 映射，并在 md §3 写明"`downloads` 是初始化计数器，本身不构成证据" |
| **F-R4-03** | **P2** | 暂停文件那行的**理由写错**：`--no-pause-worker` 在本次**是惰性的**（`PausedWorkerScope` 只在 `if allow_download:` 内 `:736-750` 与 `_close_gap` `:990-999` 构造，复用分支 `:758-765` 根本不建） | **接受并已改**：改写为"复用分支根本不构造该 scope ⇒ 该 flag 惰性、本次不比 skill 默认更弱"，锚点改为 `allow_download` 门 |
| **F-R4-04** | P3 | 正文的 `ran_at 19:08:52Z` 与 `-shm` 数值对来自**更早的一次执行**（记录是 `19:10:16Z`；正文的 after = 记录的 before），等于描述的不是被审对象 | **接受并已改**：正文改为**以本条记录为准**（`19:28:50Z`；`…163372751100 → …671162009900`），并显式写出"harness 每跑一次都会动一次 `-shm`、三次运行各动一次" |
| **F-R4-05** | P3 | 正文 §4 写 revenue-forecast head `801d5de`，记录与实时 git 都是 `51f1e05` | **接受并已改**：改为 `51f1e05`（同一陈旧串在 R5 文档与 R3 文档里也一并改掉，见 `F-R5-03`） |
| **F-R4-06** | **P2** | "三仓未变"比字面窄：harness 自己往仓库写 5 个**未跟踪**证据文件，`git status --porcelain` 看不见其内容重写 | **接受并已改（口径）**：md §4 在该行**逐条标注口径**（判据是 porcelain pre/post 相等，看不见未跟踪文件的内容重写，且本 harness 自身会写 5 个未跟踪文件） |
| **F-R4-07** | P3 | `_tree_fingerprint` 跳过 `__pycache__`，而子进程**没有** `PYTHONDONTWRITEBYTECODE` ⇒ "源码未变"依赖一个未被测量的目录（经验上闭合：最新 `.pyc` 时间早于本次运行） | **接受并已改（两处）**：子进程现在带 `PYTHONDONTWRITEBYTECODE=1`（`run_fetch` 传 env），**并且**把三仓 `.pyc` 的（路径+大小+mtime）摘要纳入 pre/post 快照 ⇒ 新不变量 `pyc_caches_unchanged: true`（wiki 3,087 / revenue 611 / filing 82） |
| **F-R4-08** | P3 | `companies` 摘要是**路径+大小**（只对文件），同大小覆盖与新增空目录不可见 | **接受并已改**：md §4 明确写出该口径，并把它作为记录字段 `companies_digest_scope` 固定下来；同时把主张收窄为"没有**新文件**落地" |
| **C5 = partly** | — | 上述 F-R4-01/-02/-06/-07 即 C5 的缺口 | 全部处置后**重跑** harness：**11/11 不变量**成立（原 8 条 + 新增的 `pyc_caches_unchanged`、`every_leg_reports_zero_downloads`、`allow_download_never_passed`），`--verify` 5/5 |

## 处置后的状态

- harness 重跑（`ran_at 2026-09-18T19:28:50Z`）：四条腿结果与复审复现的**完全一致**，不变量 **11/11**。
- 生产侧：`catalog.sqlite3` `49,677,344,768 B` / `mtime_ns 1788902601072747300` 未变、`-wal` 0 B；
  三仓 HEAD 与 porcelain 未变；`wiki_src` 143 文件指纹未变；catalog 目录 12,476 条里**仅** `-shm` 的 mtime 推进（同大小）。
- **R4 = 通过（消费者链路只读；复审 8 条全部处置）**；未覆盖项见 md §7。
