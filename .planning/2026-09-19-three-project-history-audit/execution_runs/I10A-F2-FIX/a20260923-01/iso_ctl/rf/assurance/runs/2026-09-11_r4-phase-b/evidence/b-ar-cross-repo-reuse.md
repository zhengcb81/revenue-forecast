# R4：跨仓端到端（filing-fetch 真实入口 → wiki 解析，**只读复用**）

> 收口 [b-ar-record.md](../b-ar-record.md) §5「端到端（filing/revenue 真实入口）：**未做**」那一行。
> 授权：owner 2026-09-18 选择 **A**（[owner-scope-decisions-2026-09-18.md](../owner-scope-decisions-2026-09-18.md)）——
> 先**读码把写面逐条查清并报告**，再跑 `fetch_filing.py --no-pause-worker`。
> 生产 catalog **零写入**（主库大小与 mtime 逐字段未变）。
> **本文件已按独立复审 `B.VR-r4`（0×P0/0×P1/4×P2/4×P3）改写**：F-R4-02（写面表唯一"REACHED"那一行是错的）、
> F-R4-01（`no_download_requested` 是空断言）、F-R4-03（暂停文件那条的理由写错）、F-R4-04/-05（本节曾描述**另一次执行**的
> `ran_at`/`-shm`/HEAD）、F-R4-06/-07/-08（"未变"的口径比字面窄）。

## 1. 走的入口与为什么这是"真实入口"

`C:\Users\郑曾波\Projects\filing-fetch\scripts\fetch_filing.py`，配置 `filing-fetch/config/company_wiki.json`
（`company_wiki_root = ${USER_PROFILE}/Projects/company-wiki`）。它的默认就是**只读复用**：
`--allow-download` 的帮助文本是 *"allow a market-routed download if the filing is missing
(default: read-only reuse)"*（`fetch_filing.py:1037-1041`），本次**没有**加这个 flag，所以
`action = "resolve"`（而不是联网的 `ensure`）——`fetch_filing.py:704-716`。

调用链：`fetch_filing.py` →（子进程）`python -m company_wiki.source_catalog.cli identify …`
→（子进程）`… resolve …` → 返回 handle + `resolution_envelope` 给消费者。

## 2. 写面清查（**先读码，后执行**；每条带锚点）

| 写面 | 本次是否触及 | 锚点 |
|---|---|---|
| worker 暂停文件（`filing_fetch_pause.refcount/.owner`，写在 catalog 目录） | **未触及**：`PausedWorkerScope` **只在 `if allow_download:` 内**（以及 `_close_gap` 里）构造，复用分支根本不建它 ⇒ `--no-pause-worker` 在本次是**惰性的**，而本次也**不比 skill 默认更弱** | `fetch_filing.py:736-750, 988-999`；复用分支 `:758-765`；文件 `:455-457, 572, 584-585` |
| close-gap 的 binding 临时文件 | **未触及**：只有下载/获取路径会走到 | `fetch_filing.py:961-1008` |
| 下载 / 网络 | **未触及**：无 `--allow-download` ⇒ `action="resolve"` | `fetch_filing.py:704-716` |
| wiki `identify` 的身份缓存写 | **未触及**：未传 `--refresh`，只跑 `store.load()`；唯一的写者是 `write_market` | `cli.py:1080-1097`；`security_identity.py:319-356`（写）/`:358+`（读） |
| wiki `resolve` 追加 acquisition journal | **未触及**：该命令**读**journal，不追加 | `cli.py:1183-1195`；`acquisition_journal.py:128` 在 `record()` 内 |
| 经产品 store 对 catalog 的任何写入 | **未触及（更正 `F-R4-02`）**：resolve 路径传给 resolver 的是**只读 reader**，它 `mode=ro` + `PRAGMA query_only=ON` ⇒ **没有** mkdir / WAL 切换 / 增量迁移 / commit；**第一版把它写成"按构造会触及"是错的**，据此引用的 A05/A06 类比也已删除 | `cli.py:1193`（`store=get_catalog().reader`）；对照 `:762` 的 `ensure` 与 `:1216` 的 `close-gap` 才 `get_catalog().store`；`reader.py:165/188` |
| `-shm` 的 mtime | **会动**：只读 WAL reader 本身**足以**造成它动，本机无人操作时也会动 ⇒ **只登记、不归因** | 见 §5 |

worker 相关的一个前提也核过：`worker_control.json` 的 `desired_state = "paused"`、`operation.lock` 不存在；
暂停守卫只拦 `ensure --allow-download`（`cli.py:765-771`）与 `close-gap`（`cli.py:1218-1222`），
**不拦 `resolve`** ⇒ 复用路径不会被暂停态挡住。

## 3. 四条腿（**本条记录的这一次**：`ran_at_utc = 2026-09-18T19:28:50Z`）

| id | 请求 | 退出码 | stdout 字节 / sha256[:16] | 结果 |
|---|---|---|---|---|
| **L1** | `company_query=09988`、`market=HK`、`annual_report`、`as_of_date=2026-09-18`（exact、不指定财年） | **0** | 6,207 / `d8aa34311d6ac8cf` | **`capture_ready`**：canonical = `companies\阿里巴巴－Ｗ\raw\financial_reports\annual\2026-06-18_hkexnews_12207997_2026財務年度報告.pdf`，`content_sha256 = e39fbf9c…`（= B08 第②级从真实字节核出的那一份）、`byte_size = 4,172,424`、`fiscal_year = 2026`、`capture_ready = true`、`source_status = active` |
| **L2** | 同上 + `fiscal_year=2026`（把 L1 报出的财年钉死 ⇒ 可复现请求） | **0** | 6,207 / `b64f11b6df89745b` | **`capture_ready`**（同一份文档） |
| **L3** | 同上 + `fiscal_year=2019`（catalog 里不存在的财年） | **2** | 455 / `8433b7efdc5db1fc` | **`not_found`**：`source is not reusable: missing / no_existing_source_satisfies_request` ⇒ 复用优先**不会**退化成抓取 |
| **L4** | `company_query=zzz-no-such-issuer-zzz`（身份控制） | **2** | 246 / `5c6492b7c12b0a70` | **`identity_error`**：`company identity is not uniquely resolved: missing / no_verified_identity_candidate` ⇒ 身份门在解析**之前**就 fail-closed |

四条腿的调用计数：L1/L2/L3 各 **2** 次 wiki 子进程调用（`identify` + `resolve`），L4 **1** 次（身份即失败）。
⚠️ **口径（`F-R4-01`）**：`payload.downloads` 是消费者**初始化的计数器**（`fetch_filing.py:1106`），
**本身不构成证据**；可判定的是"本次从未传 `--allow-download`"（`invariants.allow_download_never_passed`）
与"每条腿都报 0 次下载"（`every_leg_reports_zero_downloads`）。

### 3bis. 身份与决定（L1 的原文，逐字段）

- 身份：`canonical_name = 阿里巴巴－Ｗ`、`security_id = 09988`、`market = HK`、`exchange = HKEX`、
  `match_basis = ticker_exact`、`verified = true`、`active = true`、`source_name = hkex`
  （来源 `activestock_sehk_c.json`）⇒ 与 B.AR 身份腿用的**同一份交易所登记册快照**一致。
- 决定（`handle.resolution_envelope`）：`outcome = "reused_existing"`、
  `qualification.label = "verified_input"`、`activation_epoch = "epoch-canary-2026-08-10"`、
  `cohorts = ["canary-2026-08-10"]`、`policy_hash = c773099b3dcf…`（与 A06-2 `runtime-policy show`
  报的 `policy_hash c773099b…` **同一个**）、`download_events = 0`、
  `candidate_exclusion_trace = ["entity_gate_rejected: 45", "2026財務年度報告: matched"]`。
- `bundle_status = "available"`、`bundle_hash = f21c88e1bf826044…`，但 **`valid_handles` 为空**，
  两个派生产物被判**不可复用**：`normalized → artifact_status_not_completed`、
  `summary → artifact_source_sha_missing`（见 §6 的观察项）。
- ⚠️ `envelope.llm_calls = 1` / `parser_calls = 1` 来自 **producer_events journal 的历史记录**
  （`resolver.py:940`），**不是**本次调用发生的 LLM/解析动作。

## 4. 不变量（**11/11** 成立；数字取自本条记录）

| 不变量 | 值 |
|---|---|
| `production_db_unchanged` | true（`49,677,344,768 B` / `mtime_ns 1788902601072747300`，pre = post） |
| `production_wal_unchanged` | true（`-wal` 0 B） |
| `no_pause_files` | true（`filing_fetch_pause.refcount/.owner` **都不存在**） |
| `no_new_file_under_companies` | true（**口径 `F-R4-08`**：33,122 个文件的**相对路径 + 大小**摘要未变 ⇒ 没有新文件落地；**同大小覆盖不在此口径内**） |
| `repos_unchanged_during_run` | true — **口径 `F-R4-06`**：判据是 `git status --porcelain` 的 pre/post 相等，**看不见**未被跟踪文件的内容重写；本 harness 自己会往仓库写 5 个证据文件（未跟踪） |
| `heads_unchanged` | true（company-wiki `8665c8c`、revenue-forecast **`51f1e05`**、filing-fetch `d35b6f5`） |
| `product_source_unchanged` | true（wiki `src` 143 个 `.py` 的树指纹未变） |
| `pyc_caches_unchanged` | true — **口径 `F-R4-07`**：三仓 `.pyc` 的（路径+大小+mtime）摘要未变（wiki 3,087 / revenue 611 / filing 82），且子进程现在带 `PYTHONDONTWRITEBYTECODE=1` |
| `every_leg_reports_zero_downloads` | true（L1–L4 全 0） |
| `allow_download_never_passed` | true（四条腿的 argv 都不含 `--allow-download`） |
| `companies_digest_scope` | 记录性字段：`relative path + size for every file (not content)` |

`--verify`（事后只读复核）**5/5**：生产主库、`-wal`、`companies` 摘要、三仓 HEAD、wiki `src` 都仍与记录相符。

## 5. catalog 目录的**逐条**差异（不允许只写"变了/没变"）

目录共 **12,476** 个条目，本条记录 pre/post 差异 **恰好 1 条**，且是同一大小的 `-shm`：

| 条目 | before | after |
|---|---|---|
| `catalog.sqlite3-shm` | `(32768, 1789759163372751100)` | `(32768, 1789759671162009900)` |

**新增 0、删除 0**。只读 WAL reader 足以造成这次推进（阶段 A 也记录过"本机无人操作时 `-shm` 亦会动"），
因此**只登记、不归因**：既不能说"这次调用写了它"，也不能说"这次调用没碰它"。

⚠️ **`F-R4-04` 的更正**：本文件早先写的是另一次（更早的）执行的 `ran_at` 与 `-shm` 数值对
（`19:08:52Z`、`…353733321 → …508591531`），而记录里是这一次（`19:28:50Z`，
`…163372751100 → …671162009900`）。harness 每跑一次都会动 `-shm`，三次运行各动一次；
**以记录文件为准**，本文件已对齐。

## 6. 观察项（**不是**缺陷主张，登记待判）

- **`F-BAR-12`：派生产物对该文档不可复用** —— `normalized → artifact_status_not_completed`、
  `summary → artifact_source_sha_missing`，于是 `bundle_status = available` 但 `valid_handles` 为空。
  与 B.AR 的既有事实同族（sections 覆盖 **0/66**、`summarize` 覆盖有限），
  但**本步没有**量化生产里有多少文档处于同一状态 ⇒ 只登记。
- **`entity_gate_rejected: 45`**：本次请求只给了 ticker，解析器排除 45 个候选才落到这一份 —— 正常的实体门行为。

## 7. 本步**没有**覆盖什么

1. **revenue-forecast 侧的真实入口**未调用（该仓的 skill 入口需要输入/模型，不属于"复用读取"这条链路）；
   本步覆盖的是 `filing-fetch → wiki` 这条**消费者**链路。
2. **没有**验证云端（`dropbox_stock`）文档的跨仓读取（R5 单独处理）。
3. **没有**触发任何下载路径（`ensure`/`close-gap`），因此那些路径的写面（binding 文件、worker 暂停）
   只是**读码结论**，不是本次实测。
4. **没有**对生产 catalog 内的四根做端到端读取（那部分依据仍是既有 B.AR 证据）。
5. 不变量口径之外的情形（同大小覆盖、未跟踪文件的内容重写、空目录新增）**均未覆盖**（§4 已逐条标注）。

## 8. 复跑

```powershell
$E = "C:\Users\郑曾波\Projects\revenue-forecast\assurance\runs\2026-09-11_r4-phase-b\evidence"
C:\Miniconda\python.exe "$E\run_r4_cross_repo_reuse.py"            # 主跑（写 b-ar-cross-repo-reuse.json + 4 个 stdout 侧文件）
C:\Miniconda\python.exe "$E\run_r4_cross_repo_reuse.py" --verify   # 只读复核
```
⚠️ 复跑会覆盖记录文件（并且**每跑一次都会动一次 `-shm`**）；复核时请加 `--out "$env:TEMP\<自己的路径>.json"`。
