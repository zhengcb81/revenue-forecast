# R3：合法第五 root 在**隔离副本**内按配置注册 + `query → open → consumer` 最小读取

> 这一步收口 [b-ar-record.md](../b-ar-record.md) §5「**第五 root**：未做」那一行，以及
> [r4-final-status.md](../r4-final-status.md) §1 里"未获授权的写动作"中的第一条。
> 授权依据落盘在 [owner-scope-decisions-2026-09-18.md](../owner-scope-decisions-2026-09-18.md)
> （owner 的选择：**(A) 隔离副本** + 第五根**沿用 `future_lake` 占位的形状**）。
> 生产 catalog **零写入**：本步全部动作发生在 `%TEMP%` 下的隔离项目根里。

## 0. 为什么必须隔离、为什么第五根不是 `future_lake`

- 注册一个 root = scanner 往 catalog 的 `roots` 表 `INSERT`（`scanner.py:847-854`）。用生产
  config 跑，就是写 `company-wiki/.source_catalog/catalog.sqlite3`（**49,677,344,768 B**）——
  本会话授权之外；只读 manifest 自己的隔离声明也写明行为探针
  "**must NOT use the production catalog: they require the isolated copy in gate G8**"
  （`2026-09-11_r4-phase-a/command-manifest-readonly.json:108`）。
- **`future_lake` 已经是第四根**：生产 config 里四条 root 是
  `company_raw` / `dayu_portfolio` / `dropbox_stock` / `future_lake`，且
  `future_lake/README.md:1` 写的是 "ZR-409 **fourth-root** fixture (EX-08)"。
  直接拿它当"第五根"会重演既有审计已经否掉的口径
  （`docs/plans/painpoint-outcome-audit-2026-09-05/filing-audit.md:49`）。因此第五根**沿用它的形状**
  （`kind: directory` + 已注册的 `sidecar_filing_v1` 适配器 + `read_only` + `reusable_for_filing`）
  但**用新 id `r4_fifth_root`**，指向隔离工作根下的真样例目录。

## 1. 复跑命令（只在 `%TEMP%` 与 evidence 目录里写）

```powershell
$E = "C:\Users\郑曾波\Projects\revenue-forecast\assurance\runs\2026-09-11_r4-phase-b\evidence"
# 主跑：写 evidence\b-ar-fifth-root-isolated.json
C:\Miniconda\python.exe "$E\run_bar_fifth_root_isolated.py"
# 变异矩阵：写 evidence\b-ar-fifth-root-mutations.json（5 个变异，证明这些腿不是恒真/恒假）
C:\Miniconda\python.exe "$E\run_bar_fifth_root_isolated.py" --mutations
# 只读复核已记录的那一次跑（生产快照必须仍逐字段相符）
C:\Miniconda\python.exe "$E\run_bar_fifth_root_isolated.py" --verify
```

⚠️ 复跑会**覆盖**记录文件；复核时请加 `--out "$env:TEMP\<自己的路径>.json"`（`--mutations` 把结果写在
`--out` 的**同目录**，所以 `--out` 要指向临时目录，别指向 `evidence\`）。独立复审 `B.VR-r3` 就是这么复跑的。

## 2. 隔离设计（可机械核对，不靠承诺）

| 项 | 实现 | 证据字段 |
|---|---|---|
| 工作根 | `%TEMP%\r4-bar-fifth-root`，**不在任何仓库内** | `isolation.workdir`、`isolation.inside_a_repo: []` |
| 五条 root | 四条 stand-in（空目录，**从不扫描**）+ 第五根 `r4_fifth_root`（真样例） | `config_text`、`isolation.root_paths` |
| 路径守卫 | `guard_paths_are_isolated()` 检查**已加载的 config**：任一根路径或 `catalog_dir` 越出工作根即 `SystemExit`；`catalog_dir` 等于生产目录也拒绝；**返回值由同一条比较派生**（`catalog_is_production`） | 变异 **M1** 将其打成"拒绝"；`observe()` 对**每一棵**隔离树先跑守卫（含 M2–M5） |
| 生产快照 | `catalog.sqlite3` / `-wal` / `-shm` 的 `{size, mtime_ns}` 逐字段 pre/post 相等 | `invariants.production_catalog_unchanged` |
| 扫描模式 | 隔离 catalog 的 `runtime_policy.json` 由**产品自己**的 `build_snapshot` 生成，`v2_scan_shadow=true` ⇒ 走适配器派发 | `runtime_snapshot`、`scan_mode` |
| 样例 | 两份真文件 + 各一份 `.source.json` 侧车（完整身份、https `source_url`、`published_at`） | `fixtures` |

生产 catalog 快照（pre 与 post 相同）：`catalog.sqlite3 {size: 49677344768, mtime_ns: 1788902601072747300}`、
`-wal {size: 0}`、`-shm {size: 32768}`。

## 3. 腿与结果（本次跑 `ran_at_utc = 2026-09-18T18:37:10Z`）

| id | 调用（mode） | 退出码 | stdout 字节 | sha256[:16] | 结果 |
|---|---|---|---|---|---|
| `scan` | `scan --root-id r4_fifth_root`（cli） | 0 | 290 | `e9171aa83f0a797a` | **注册发生**：roots 1 行、documents 2、sources 2、locations 2、scan_runs 1 |
| `status` | `status`（cli） | 0 | 178 | `6c157e574435b8e7` | 注册后的计数 |
| `query` | `query --limit 20`（cli） | 0 | 24,117 | `3c0f154cdcebd256` | 第五根的文档可见：该腿自己的 `document_ids` 字段（**在截断前**从完整 stdout 解析）有 **2** 个 id；保留的 `stdout` 已截断（`stdout_truncated: true`），`stdout_head` 只有 1 个 id，**机器可核对的口径是** `query_api.count = 2` 与该 `document_ids` |
| `consumer-resolve` | `SourceResolver.resolve(SourceRequest(mode="exact"))`（api） | — | — | — | **FY2024 / FY2025 各 `reused_exact`**，各 1 match、`capture_ready=[true]`，理由 `one_existing_source_matches_provider_identity`，canonical 落在第五根下 |
| `open` | `SourceResolver.read_verified_bytes(handle)`（api） | — | — | — | **两份都 `ok=True` / `status="verified"`**：59 B，返回字节 sha256 = 磁盘文件 sha256（`e34a69ef…` / `46391d16…`） |
| `consumer-candidates` | `SourceCatalog.query_filing_candidates(root_ids=("r4_fifth_root",))`（api） | — | — | — | 2 行（filing-fetch 的复用接缝能列到新根） |
| `unregistered-root-cli` | `scan --root-id does_not_exist`（cli） | **1** | 0 | `e3b0c442…`（空） | `{"error": "no configured roots matched root_ids", "error_type": "fatal", "retryable": false, "status": "failed"}` |
| `mixed-root-id-cli` | `scan --root-id r4_fifth_root --root-id does_not_exist`（cli） | **1** | 0 | `e3b0c442…`（空） | `{"error": "unknown root_ids: ['does_not_exist']"}` —— 选择集非空，因此打到的是**专属的 unknown-id 分支**（`scanner.py:762-765`）；`scan_runs` 仍为 **1** ⇒ 合法根**没有**被顺带扫描 |
| `unknown-adapter`（api） | `load_catalog_config(adapter_id="not_registered_v1")` | — | — | — | **fail-closed**：`CatalogConfigError: roots[3] adapter_id 'not_registered_v1' not registered (CFG-01)` |
| `deny`（api） | 同一份字节、只把 `reusable_for_filing` 改成 `false` 的第二个隔离 catalog | — | — | — | `resolve` → **`missing`（FY2024/FY2025 都是）**；policy export 的 reusable 只有原来四条；第五根条目 `reusable_for_filing: false` |
| `deny` 的**字节入口**（api） | 用**该 deny catalog 自己的 location 行**重建 handle 后调用 `read_verified_bytes` | — | — | — | **`ok=True / status="verified"` ×2（59 B，sha256 与磁盘相符）** —— 见下面 §3bis 的口径 |

### 3bis. deny 到底覆盖到哪一层（`B.VR-r3` F-R3-01 实测复现）

| 层 | deny 生效吗 | 证据 |
|---|---|---|
| `SourceResolver.resolve()`（复用**决定**） | **生效**：`missing` | `deny.resolutions = ['missing','missing']`，理由链 `no_reusable_root_location` |
| `SourceCatalog.query_filing_candidates(root_ids=…)` | 不适用：这是 **root 维度的候选枚举**，不查 reusable | deny catalog 里仍返回 **2 行** |
| `SourceResolver.read_verified_bytes()`（**字节**入口） | **不生效**：`verified` ×2 | 它只查**根包含性**（`resolver.py:2016-2041` 的 `_inside_configured_roots`），**从不**查 `reusable_root_ids` |
| 消费者侧包含性 | 不在本仓：`filing-fetch validate_handle` + `policy_snapshot.path_ref` | 产品 docstring（`resolver.py:1958-1963`）把该原语限定为"向本 resolver 要字节的调用方" |

⇒ 因此本记录**不**声称"deny 在所有读取入口都拒绝"；它声称的是**决定被拒**、并**实测**了字节入口按包含性
放行这一事实。这条已登记为产品边界发现 **`F-BAR-11`**（[findings.md](../findings.md)）。

## 4. 注册证据：写入的 roots 行

| root_id | path | kind | priority | last_scan_run | last_scanned_at |
|---|---|---|---|---|---|
| `r4_fifth_root` | `<TEMP>\r4-bar-fifth-root\roots\fifth_root` | `directory` | 50 | `scan-447ddc39c9a14480aa7949d8cc865ca1` | `2026-09-18T18:37:06Z` |

四条 stand-in 根**没有**出现在 `roots` 表里（只扫了第五根）：
`four_stand_in_roots_absent_from_roots_table: true`。

## 5. 不变量（7/7 成立）

| 不变量 | 值 |
|---|---|
| `production_catalog_unchanged` | true（size + mtime_ns + `-wal` + `-shm` 全等） |
| `production_wal_untouched` | true |
| `repos_unchanged_during_run` | true（三仓 `git status --porcelain` pre = post） |
| `heads_unchanged` | true（company-wiki `8665c8c`、revenue-forecast `801d5de`、filing-fetch `d35b6f5`） |
| `product_source_unchanged` | true（`company-wiki/src` **143** 个 `.py`，树指纹 `d201140eabd226e44fb5895aceed10c9ace1088eda12754b2d8082db81c8b716`） |
| `fifth_root_registered` | true |
| `four_stand_in_roots_absent_from_roots_table` | true |

`--verify`（事后只读复核）4/4：生产 catalog 与 pre、post 都仍逐字段相符，`wiki_src` 未变，三仓 HEAD 未变。

**本地两个 CI 步骤**（照 `company-wiki/.github/workflows/ci.yml` 的两条命令跑；本步 **wiki 树零改动**，所以这两步是**回归门**）：
unit **799 passed**（120.28s，[r3-ci-step1-unit.txt](r3-ci-step1-unit.txt)）、
contract **1905 passed / 8 skipped**（762.79s，[r3-ci-step2-contract.txt](r3-ci-step2-contract.txt)）。
**远端 CI**：revenue-forecast `4dfdc02`（交付提交）workflow `quality` run **`35382672249`** = **success**
（`real-roots` + `verify` 两个 job 全绿）；company-wiki 零改动，HEAD 仍 `8665c8c`（run `35325679266` = success）。

## 6. 变异矩阵：**5/5 KILLED**（`b-ar-fifth-root-mutations.json`）

R3 不改产品代码，所以变异打在**harness 自己**身上：一条腿如果在机制被破坏时答案不变，它就是装饰。
**每一棵**变异树在扫描前都先过隔离守卫（F-R3-04 的处置）。

| 变异 | 期望 | 实测 | 判定 |
|---|---|---|---|
| **M1** 第五根路径移出工作根（`${PROJECT_ROOT}/../../roots/fifth_root`） | 守卫拒绝 | `SystemExit: refusing to run: root paths outside the isolated workdir: [{'root_id': 'r4_fifth_root', 'path': '…\\Temp\\roots\\fifth_root'}]` | **KILLED** |
| **M2** deny 根翻回 `reusable_for_filing: true` | 消费者改为服务它 | `['reused_exact', 'reused_exact']` | **KILLED**（⇒ 主跑里 deny 的 `missing` 是**有区分力**的，不是恒假） |
| **M3** 侧车去掉 `published_at` | 不再 `reused_exact` | `['ambiguous', 'ambiguous']` | **KILLED** |
| **M4** 侧车 `content_sha256` 与磁盘不符 | 不再 `reused_exact` | `['missing', 'missing']` | **KILLED** |
| **M5** 删掉 `runtime_policy.json`（退回 v1 目录遍历） | 适配器路径消失、侧车被当文档 | titles `['2024-annual', '2024-annual.pdf.source', '2025-annual', '2025-annual.pdf.source']` | **KILLED** |

> M5 的**边界**（不夸大因果）：它只证明"**没有快照时** v1 遍历会把 `.source.json` 当成独立文档"。
> 生产 catalog 的 `runtime-policy show`（A06-2）显示 `v2_scan_shadow=true`，所以 M5 **不构成**生产里
> 那 3 份 `.pdf.source` 文档（`b-ar-record.md:84` 的 F-BAR-1）的已证成因——只是同族的**候选机制**之一；
> 已登记为 **`F-BAR-10`**（[findings.md](../findings.md)）。

## 7. 这一步**没有**覆盖什么（范围诚实）

1. **隔离 catalog 是空的**：生产四根的数据**不在这里**。因此"真实四 root 端到端"那一半的依据仍是既有
   证据（[b-ar-record.md](../b-ar-record.md) §1/§3：四根各有候选 39/19/4/4、真实根只读旅程），
   **不是**这一步的产出。本步产出的是"**第五根按配置加入 + 可被消费者读取**"这一半。
2. **"生产四根 + 第五根共存"未验证**：需要 46.3 GiB 的副本（本机可用 63 GB）或 owner 批准一次生产
   catalog 写入——两者都未做。
3. 四个 stand-in 根**不是**真实根；第五根指向的是**隔离样例目录**，不是用户数据。
4. 只跑了 `query → open → consumer` 最小读取；`normalize` / `summarize` / `extract-sections` 未跑
   （不需要，且会写派生）。
5. `dropbox_stock` 的云占位仍未被哈希（R5，需 owner 接受水合副作用）。
6. 跨仓（filing-fetch / revenue-forecast 真实入口）端到端仍**未做**（R4，需 owner 确认命令）。

## 8. 对 L04 验收句的逐条对照（`simplified-test-matrix.md:31`）

> 「合法第五根无需消费者代码改动；未知/deny 拒绝，不以平权绕过能力限制」

| 分句 | 本步证据 |
|---|---|
| **合法第五根** | 纯配置加入（`config_text`），产品源码零改动（143 文件树指纹不变）⇒ 注册行由**未改动的 scanner** 写出 |
| **无需消费者代码改动** | 读取用的是产品自己的接缝：`SourceResolver.resolve` → `reused_exact`；`read_verified_bytes` → `verified`；`query_filing_candidates` → 2 行 |
| **未知拒绝** | 未注册适配器 → 配置加载期 `CatalogConfigError (CFG-01)`；未注册 root id **两种分支**都被拒（空选择 / 混合选择打到专属分支），合法根未被顺带扫描 |
| **deny 拒绝（决定层）** | `reusable_for_filing: false` → `resolve` = `missing`（M2 反证：翻回 true 即 `reused_exact`） |
| **不以平权绕过能力限制** | **按层说清**：复用**决定**被拒（resolver）；policy export 的 reusable 集合**不含**被 deny 的第五根（同 kind ≠ 同权限）；但**字节入口** `read_verified_bytes` 只查根包含性、**仍放行**（§3bis 实测）⇒ 该分句在本步覆盖**一条**读取入口，缺口登记为 `F-BAR-11` |

## 9. 与既有记录的挂接（**已落盘**，`B.VR-r3` F-R3-03 的处置）

- [b-ar-record.md](../b-ar-record.md) §5「第五 root」行 → 已改为"**达成（隔离副本）**"，并指向本文件。
- [findings.md](../findings.md) → 新增 **`F-BAR-10`**（v1 无快照时把侧车当文档，M5 实测）与
  **`F-BAR-11`**（deny 不覆盖字节入口，B.VR-r3 F-R3-01 实测）。
- [progress.md](../progress.md) → 新增 R3 行（实施 + 变异 + 本地两个 CI 步骤 + 远端 CI + 独立复审）。
- [evidence/b-vr-r3-disposition.md](b-vr-r3-disposition.md) → 复审 6 条发现的逐条处置。
