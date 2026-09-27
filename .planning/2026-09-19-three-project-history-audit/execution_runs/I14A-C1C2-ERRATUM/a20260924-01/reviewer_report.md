# I14A-C1C2-ERRATUM 独立复审报告（C-1 + C-2 追加式更正轮）

| 项 | 值 |
|---|---|
| 复审角色 | 独立复审工位（与实现者非同一人）；**只写复审报告，不写卡状态** |
| 被审 attempt | `execution_runs/I14A-C1C2-ERRATUM/a20260924-01/`（交付 2026-09-24 22:36，此前无任何 `reviewer_report`） |
| 本报告写入面 | 本 attempt 内 **仅两个新建文件**：`reviewer_report.md` + `reviewer_report.sha256` |
| 复审执行时刻 | 2026-09-25（UTC，复审会话）；所有复跑均在 `%TEMP%` 隔离副本内完成 |
| 结论依据 | 全部结论来自本人的**独立复算 / 隔离副本重跑**；缺证据处写「未证实」 |

## 结论

VERDICT: ACCEPT

理由：八项重点全部核毕，**无 P1**（两处封盘追加的前缀自证成立，追加**未越界**；封盘树其余字节与 HEAD 逐 blob 相等；`git diff HEAD --name-only` 非 `.planning` = 0）。发现 **2 项 P2、3 项 P3**，均为自述文字/数值与盘上 raw 不符或论据方向错误，**不改变任何绿色证据的成立性**，按 T1-21 追加式更正即可，不构成本卡失败。

---

## 一、逐项核验表（八项）

| # | 核验点 | 我的独立实测 | 判定 |
|---|---|---|---|
| 1 | 阈值 0.1504 s 是「导出」还是「调到刚好通过」 | 三源全部在盘且可复算：① 名义 50 ms = 封盘 `iso/slo_probe_patched.py:76` `RSS_SAMPLE_INTERVAL_SECONDS = 0.05`（直读第 76 行）；② reviewer 节拍 64.0–75.2 ms = `I14A-D1-OPS-REVIEW/.../evidence/e1c_samples_inside_life.json`（1965 B，sha256 `7d7455eb…c4375` 复算一致，文件内 `spacing_ms_min=64.0 / max=75.2`）；③ 本会话节拍 63.67–66.92 ms = 我对该 attempt `evidence/green/sweep/E1c-F3-alive-allocate/report.json`（sha256 `da224f3c…f3c834` 复算一致）按 `window/(count-1)` **自行重算**得 `63.67, 64.93, 66.46, 64.13, 66.92, 65.52`，与 `threshold_derivation.json` 逐行一致。阈值 = `2 × max(75.2, 66.92) = 0.1504` 复算一致 | **导出成立**（详见二.1） |
| 1b | `2×` 系数有无依据 | `2×` 与 `≈150 ms` **逐字来自 D1 已签署裁定**：`ruling.md:174`「适用域：存活 ≥ 约 2×有效节拍（≈150 ms）的进程，PID 身份可保证」；`ruling.md:185(i)` 直接给出路线「限定到『存活 ≥ 2×有效节拍』的夹具」。D1 attempt 最新文件 mtime = `2026-09-24T20:55:57Z`，**早于**本 attempt 首次写入 `21:15:46Z` | **有依据（外部签署在先）** |
| 1c | 先冻后跑 | `oracle.md` LastWriteTimeUtc = `2026-09-24T21:15:46Z`；最早 evidence `copied_inputs_sha256.json` = `21:17:30Z`、首份运行证据 `red/e0_repeat/run1.stderr.txt` = `21:17:44Z` ⇒ 冻结早于首跑 2 分钟 | **成立** |
| 1d | 其余 9 个反例期望一字未改 | 我用 `git diff --no-index --numstat` 独立比对封盘↔本 attempt：`fixture_spec.py` **+27 / −0**（纯新增 `IDENTITY_SCOPE_MIN_SECONDS`/`IDENTITY_SCOPE_RULE` 与注释，**期望字典零删除零改动**）；`run_probe_cases.py` **+58 / −5**，5 行删除**全部**落在原 `fixture_pid_is_in_samples` 身份块内 | **成立** |
| 1e | E0 判据 13→14 只增不减 | 修前（封盘语义）13 键：`expected_raw_returncode, calls_failed, peak_rss_gt, peak_rss_source, rss_sample_count_min_gte, fixture_pid_is_in_samples, window_present×4, quick_check_outside_slo_window, rss_window_not_before_slo_window, frozen_budgets_untouched`；修后 14 键 = 上述 13 中 `fixture_pid_is_in_samples` 由域内/域外两分支之一承接（E0 走 `fixture_pid_identity_scope`，E1c 仍走 `fixture_pid_is_in_samples`）**+ 新增 `rss_pids_include_child_pids`** ⇒ 12 项原样、身份断言保留、净 +1 | **成立** |
| 2 | 修前/修后/四变异臂 | **隔离副本自跑**（见三）：修前 E0×5 = **3 红/2 绿**、失败项恒 `fixture_pid_is_in_samples`、13 键；修前 pytest = **1 failed/11 passed/1 skipped, rc=1**；修后 E0×3 全绿 14 键 rc=0；`--all` **rc=0**（7/7 all_ok，probe rc `2/4/4/2/2/2/2`）；binding-mismatch/binding-ok/percentiles **rc=0/0/0**；修后 pytest **12 passed/1 skipped, rc=0**；**M1 红（4 项）· M2 红（唯一 `fixture_pid_is_in_samples`）· M3 红（唯一 `fixture_pid_is_in_samples`，寿命入域）· M4 绿** | **全部复现** |
| 3 | 三代并存是否如实披露 | Gen-1：封盘 `after/E0-baseline-F4/verdict.json` `all_ok=true`、13 键（在盘）；Gen-2：`ruling.md:131`「本会话 E0 身份断言：**6 红 / 1 绿**（唯一绿＝`--all` 首跑）」+ reviewer `evidence/suite_patched_stdout.txt`(9176 B)、`evidence/e0_repeat/run1..5`（30 文件）在盘；Gen-3：本 attempt `evidence/red/`（3红2绿 + 套件 1 failed）与 `evidence/green/`（5 绿 + 全扫绿）在盘、按目录/时刻可辨 | **成立，未用新绿覆盖旧绿** |
| 4 | 自曝假绿是否留档 | `evidence/mutations/{m1,m2,m3,m4}/run1_driver_bug/` **四目录均在**（mtime `21:22:17Z–21:22:30Z`，早于修正后重跑 `21:23:01Z–21:23:19Z`）；`report.md`/`handoff.json` 引用的是重跑结果，**未把 run1 当证据** | **留档成立**；但自述「4 臂全假绿」与 raw 不符 → **P2-2** |
| 5 | 第 3 处原文更正是否成立且只加固 | 死键证实：封盘 `fixture_spec.py:54,89` 声明 `"rss_pids_include_child_pids": True`，封盘 `run_probe_cases.py:111` 读的是 `rss_pids_match_child_pids`，全封盘树**无任何 case 声明该键** ⇒ 该期望自封盘起**从未被评估**；封盘 `oracle.md:119-120`「Both are checked …」**确不成立**。接线只加不减：`run_probe_cases.py` 仅 +58/−5（5 行均在原身份块），新增分支 `if exp.get("rss_pids_include_child_pids")`。封盘 harness 字节未动（见七） | **成立，纯加固** |
| 6 | C-2 两处复测 | ① `tools/*.py` = **24** 文件、`\.db\b` **0 命中**；`tools/release_readiness.py:37` = `CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"`；全树（排 `.planning`/`.git`）`catalog.db` = **4 命中**且**全非产品代码**（2 处 `.review-*` 快照文档 + `assurance/.../G5-boundary-observation.json:53` + `audit_review/.../progress.md:91`），与自述四处逐一相同。② 我在隔离副本实跑：`catalog_dir: "<dir>"  # c` ⇒ **rc=3**、`binding.configured_catalog_dir` 保留字面引号、`same_directory=false`、顶层 `error=catalog_config_mismatch`；`catalog_dir: <dir>  # c` ⇒ **绑定被接受**（`consistent=true`、无引号残留）；`catalog_dir: "<dir>"`（无注释）⇒ **绑定被接受**。③ 生产配置 `.review-zr407-20260818/company-wiki/config/source_catalog.yaml:2` = `catalog_dir: "${PROJECT_ROOT}/.source_catalog"`，**不含行内注释**；④ 我另跑 `--catalog <dir>/catalog.db` ⇒ `consistent=true, catalog_filename_allowed=true, basis=catalog_file_within_config_catalog_dir, calls.total=6`，同时解析目标按 config 指向 `catalog.sqlite3` ⇒ clause 6 对 `catalog.db` **确未达成** | **成立**（rc 差异见四.6） |
| 7 | 两处封盘追加前缀自证 | 我**自行复算**（见四.1）：`oracle.md` 前 20457 B sha256 = `87775f2f…84bb7`（等于前像）；全文 31256 B sha256 = `4dc8600f…9c204`；`decision.md` 前 8467 B sha256 = `a1a9d374…bfda24`；全文 20545 B sha256 = `11cf8334…dc772`；四值与自述**逐一相符**。另：把两前缀字节 `git hash-object` 后与 `HEAD:` blob 比对 **相等**（`2cd1926d…` / `89f5d936…`），即前像 = 提交原像。`git status --porcelain -- execution_runs/I-14-A`（cwd = 计划目录）**只有 2 行 M** | **成立，未越界** |
| 8 | `review.md` 未追加的理由 | 全文检索：**无** `catalog.db` 主张；**无**「inline `#` comments」能力表述（`inline` 仅出现在 `inline maps`）；`RF/tools/release_readiness.py` 仅出现于 `:96` 的 quick_check 生产说明，与被推翻两处无关；F-I14A-05 行仍在 `review.md:121/:169`，内容为「边界未文档化 + 已在 oracle/decision 列明所解析与所拒绝的形态」，不重复被推翻原文 | **理由成立** |

---

## 二、阈值「导出」判定（本卡最可能被打的点）

**判定：是「导出」，不是「调到刚好通过」。** 四条相互独立的证据：

1. **系数与锚点是外生的、签署在先**：`2×` 与 `≈150 ms` 出自 D1 运维 reviewer 已签署的 `ruling.md` §5.1(a)2（第 174 行），且 §185(i) 直接授权了「限定到存活 ≥ 2× 有效节拍的夹具」这一路线；D1 载体最后写入 `2026-09-24T20:55:57Z`，早于本 attempt 首写 `21:15:46Z`。系数不是本轮为了出绿而发明的。
2. **数值在首跑前已完全确定**：`0.1504 = 2 × 75.2 ms`，其中 75.2 ms 是 reviewer 的、**先于本 attempt 存在**的实测值；oracle 于 `21:15:46Z` 冻结，第一份运行证据 `21:17:44Z`。本会话自己的节拍（63.67–66.92，出自 21:20 的 E1c 报告）按冻结公式 `2 × max(...)` 代入后**不会**改变阈值。
3. **阈值不在「成败刀口」上**：我把公式里的 `max` 换成 `min` 得 `0.1338 s`，对全部 10 次 E0（盘上 5 修前 + 5 修后）、`--all`、以及 M1–M4 四臂**逐调用重判，结论不变**——唯一 ≥0.1338 的调用是修后 run2 的 `0.135917 s`，该 run 的 fixture pid 全集 ⊆ 采样集（我复算 `missing=[]`），即使入域仍绿。也就是说观测结果在 `0.1338 ~ 0.458` 整段阈值区间内稳定，`0.1504` 并非「刚好通过」的取值。
4. **绿不是靠放松判据拿到的**：修后 5 次 E0 中有 **4 次**若按修前的**无条件**身份断言会红（我复算 reported⊄sampled，run1 缺 2 个、run3 缺 5 个、run4 缺 2 个、run5 缺 4 个），域门确实改变了判定——但这正是裁定授权的更正本身；而域门的**活性**由 M3 打红、身份判据的**可打红性**由 M2 打红共同背书（我隔离副本复现）。

**附带论据错误（→ P2-1）**：`oracle.md:65` 与封盘追加节 §10.1 写「取两者较大值……阈值只会更大（更严）」，方向说反了——在 `elapsed >= threshold` 才入域的规则下，**阈值越大、需证明身份的调用越少，域门越宽松**。取 `max` 的正当理由应是「以最坏节拍上界兑现『存活 ≥ 2 节拍 ⇒ 必有一次周期采样』的保证」，而不是「更严」。该句论据不成立，但结论（导出、非调到刚好通过）不依赖它。

---

## 三、修前 / 修后 / 四变异臂：我在隔离副本的自跑结果

环境：把本 attempt 的 `iso/ company-wiki/ harness/ mutations/` 整份 robocopy 到 `%TEMP%\i14a_c1c2_rev`；把**封盘** `I-14-A/a20260919-01` 的 `iso/ company-wiki/ harness/` 整份 robocopy 到 `%TEMP%\i14a_sealed_rev`；均用副本内 `venv\Scripts\python.exe` 执行，**封盘树与本 attempt 树零写入**（两棵树 `mtime ≥ 2026-09-25` 的文件数 = 0）。

| 臂 | 我的自跑 | 盘上 raw（我复算） | 自述 |
|---|---|---|---|
| 修前 E0 ×5（封盘字节复制件） | `R,G,G,R,G` ⇒ **3 红/2 绿**，13 键，红时 failed 恒 `fixture_pid_is_in_samples`，runner rc 红=1/绿=0 | `绿,红,绿,红,红` ⇒ **3 红/2 绿**，同上（排列不同属竞态随机，比例一致） | 3 红/2 绿 ✅ |
| 修前 冻结 pytest | **rc=1：1 failed**（`test_frozen_case[E0-baseline-F4]`）/ 11 passed / 1 skipped | `red/suite/stdout.txt` 尾部 `1 failed, 11 passed, 1 skipped` | 一致 ✅ |
| 修后 E0 ×3（我跑 3 次） | **3/3 全绿，14 键，rc=0** | 5/5 全绿，14 键 | 5/5 绿 ✅ |
| 修后 `--all` | **rc=0**，7/7 `all_ok`，probe rc `E0=2,E1a=4,E1b=4,E1c=2,E2=2,E3=2,E7=2` | `green/sweep.stdout.json` 同值 | 一致 ✅ |
| 修后 binding-mismatch / binding-ok / percentiles | **rc=0 / 0 / 0** | 三份 stdout 均 `all_ok=true`（盘上未存 rc，我已自跑补证） | 一致 ✅ |
| 修后 冻结 pytest | **rc=0：12 passed / 1 skipped** | `green/suite/stdout.txt` `12 passed, 1 skipped` | 一致 ✅ |
| **M1 不采样** | driver rc=1，**红** `failed={peak_rss_gt, peak_rss_source, rss_sample_count_min_gte, rss_pids_include_child_pids}` | 同（4 项完全一致） | 一致 ✅ |
| **M2 只记启动器 pid（E1c）** | driver rc=1，**红且唯一** `failed={fixture_pid_is_in_samples}`；入域寿命 1.794–2.061 s | 唯一红；入域寿命 1.734–1.816 s | 一致 ✅ |
| **M3 F4 延寿 + 变异探针（E0）** | driver rc=1，**红且唯一** `failed={fixture_pid_is_in_samples}`；入域寿命 **0.461–0.484 s** | 唯一红；入域寿命 **0.458–0.473 s** | 自述 0.458–**0.497** ⇒ 上限不符（P3-1） |
| **M4 对照（延寿 + 原探针）** | driver rc=0，**绿**；入域寿命 0.468–0.541 s | 绿；入域寿命 0.462–0.497 s | 一致 ✅ |

结论：**「E0 没变成空断言」的关键证据 M2/M3 都真打红了**（我在自己的副本上独立复现），M1 也按预期打红 4 项、M4 对照为绿。

---

## 四、我实测的 rc 与哈希（原始数值）

1. **封盘前缀复算**（核心）
   - `I-14-A/a20260919-01/oracle.md`：全文 **31256 B** sha256 `4dc8600f2bbbd40b93585788cd0e6f2b2dc5b2501487e2eeb71377e092b9c204`；前 **20457 B** sha256 `87775f2f4ff025e4d104fd1dfe23d7f7bfc75a20520f8859732133e96ec84bb7` = 前像 ✅；前缀 `git hash-object` = `2cd1926dd496862ee1a53317f7ed1700d0597d5d` = `HEAD:` blob ✅（追加 +10799 B）
   - `I-14-A/a20260919-01/decision.md`：全文 **20545 B** sha256 `11cf83342484165308445ad085ba4e1f296bb8d7ad08b5afa81feb57e28dc772`；前 **8467 B** sha256 `a1a9d37478ffb42f15877ac29b9ecb044b8f402f4d77f532d1a25f1646bfda24` = 前像 ✅；前缀 blob = `89f5d936744ed8a039d01efcbf9abb7411c3782a` = `HEAD:` blob ✅（追加 +12078 B）
   - 追加段与登记的追加源**逐字节相等**：`oracle.md[20457:]` == `evidence/append_oracle_section.md`（10799 B）；`decision.md[8467:]` == `evidence/append_decision_section.md`（12078 B）
2. **封盘树未越界**：`git ls-tree -r HEAD` 得封盘内 **85 个被跟踪文件**，逐个 `git hash-object` 比对 ⇒ **仅 2 个不等**（正是 `oracle.md`/`decision.md`）；`git status --porcelain -- execution_runs/I-14-A`（cwd = `.planning/2026-09-19-three-project-history-audit`）⇒ **恰好 2 行 M**；封盘全树 `mtime ≥ 2026-09-21` 的文件**只有** `oracle.md`/`decision.md`（均 `2026-09-24T21:30:46Z`），其余 1578 件仍为封盘当时（≤2026-09-20）
3. **git 边界**：`git -c core.quotepath=false diff HEAD --name-only` = **3826 行**，其中非 `.planning` = **0**；未跟踪非 `.planning` 项 = `.tmp-r41-mutation/`（2026-09-20）、`assurance/.../plan_inputs.json.bak`（2026-09-21）两项（均早于本 attempt 并已在 handoff 登记）+ `h2.log`、`h2.log.err`、`probe_root_m777/`、`probe_root_m777kw/`（mtime **2026-09-25**，晚于本 attempt 交付，非本 attempt 产生）
4. **attempt 自述文件哈希**：`oracle.md` 14450 B `f31d23fa…c081a7` ✅、`report.md` 9594 B `77047dd1…646aea` ✅、`evidence/*` 8 件（`prefix_proofs/threshold_derivation/c2_measurements/route_a_patch.diff/route_a_patch_hashes/copied_inputs/append_oracle_section/append_decision_section`）字节数与 sha256 **全部与 handoff 声明相符**
5. **只读依据哈希**：`ruling.md` 34896 B `ede71bfa…11ab6c8` ✅、其 `handoff.json` 7166 B `1890d820…6a9bd1d` ✅、封盘/本 attempt 探针 `iso/slo_probe_patched.py` 均 `14932c74…aaa3540e`（与 `review.md:131-132` 引用一致）、封盘 `harness/fixture_spec.py` 8439 B `cd049eec…9b77d86a`、封盘 `harness/run_probe_cases.py` 18263 B `6360a578…0e6bbdf678`（= `route_a_patch_hashes.json` 登记的前像），补丁后 10250 B `f0d243ce…`、21502 B `3fd909a8…`；`harness/tests/test_i14a_failure_branches.py` 封盘↔本 attempt **同哈希** `4dcb0206…b15bf980`
6. **C-2 rc 实测**（隔离副本）
   - `catalog_dir: "<dir>"  # c` ⇒ **rc=3**，`configured_catalog_dir` 带字面引号、`same_directory=false`、`consistent=false`、顶层 `error=catalog_config_mismatch` ✅（与自述一致）
   - `catalog_dir: <dir>  # c` ⇒ **绑定接受**（`consistent=true`、无引号残留）。**我的 rc=4 而非 2**：因 PowerShell→原生进程的参数层无法把自述那条含内嵌引号与非 ASCII 路径的 `--resolve-cmd` JSON 正确传递（两次尝试分别 rc=1 + `json.JSONDecodeError`），我改用探针**默认** resolver 模板（`company_wiki.source_catalog.cli`，本副本不可运行）⇒ 业务失败 rc=4。**绑定/解析层结论与自述完全一致**，rc 差异属我这侧的调用方式，已如实登记
   - `catalog_dir: "<dir>"`（无注释）⇒ 绑定接受（对应自述 rc=2 例）
   - `--catalog <dir>/catalog.db` ⇒ `consistent=true / allowed=true / basis=catalog_file_within_config_catalog_dir / calls.total=6` ✅
   - `_strip_scalar` 实测（直接调用）：`'"C:/x/catalog"  # c' → '"C:/x/catalog"'`（注释**被剥除**、引号**保留**）；`'C:/x/catalog  # c' → 'C:/x/catalog'` ⇒ 机理表述见 P3-3
7. **final_verification.json**：`checks` **25 个键、25 个 `true`、`failed_checks=[]`** ⇒「25/25 通过」属实（但其中若干为实现者自查项，其依据已由我在上表逐条独立复算）

---

## 五、发现分级

### P1
无。（追加未越界：前缀 + `HEAD:` blob + 封盘 mtime 三重证据齐备。）

### P2（需按 T1-21 追加式更正，不阻断本卡）

- **P2-1 阈值「更大 ⇒ 更严」方向说反**：`oracle.md:65`（已冻结正文）与封盘追加节 `oracle.md` §10.1 表述「取两者较大值……阈值只会更大（更严）」不成立——在 `elapsed >= threshold` 才入域的规则下阈值越大域门越宽松。正确论据是「取最坏节拍上界才兑现『≥2 节拍必有一次周期采样』的保证」。影响：论据错误，不改变「导出而非调到刚好通过」的结论（见二），但该句会被误读为安全裕度。
- **P2-2 「首跑 4 臂全假绿」与盘上 raw 不符**：`report.md:41` 与 `handoff.json.C1_execution.mutation_first_run_disclosed.issue` 称首跑「4 臂全假绿」；实际 `evidence/mutations/*/run1_driver_bug/arm.stdout.json` 为 `m1: all_ok=true`（假绿）、`m2: all_ok=false, failed=[fixture_pid_is_in_samples]`（**红**，其变异打在探针文件上、不受该驱动 bug 影响）、`m3: all_ok=true`（假绿）、`m4: all_ok=true`（对照臂**本就应绿**）。准确表述应为「2 臂（m1/m3）假绿、m4 应绿、m2 本就红」。影响：披露文字失真，**不影响**绿的准入（准入依据是修正后 m1/m2/m3 均打红，我已独立复现）。

### P3（记录在案，供后续追加更正）

- **P3-1 M3 寿命上限自述 0.497 s，raw 为 0.473486 s**（`evidence/mutations/m3/E0-baseline-F4/verdict.json` 与 `arm.stdout.json` 两处一致：0.473486/0.471959/0.466426/0.471499/0.464713/0.458451）；`0.497` 实为 M4 的上限（0.496813）。出现在 `report.md:36`、`handoff.json`、封盘追加节 §10.1 三处。**不影响**「6 调用全部入域（>0.1504）」的结论。
- **P3-2 `handoff.json` 的 `e0_identity_branch` 写「per-call lifetimes recorded (0.055-0.099 s)」**，盘上 5 次绿 run 的实测区间为 `0.0515–0.1359 s`（单次最大 0.135917 s，见 run2）。**不影响**判定（全部 < 0.1504，走 `not_claimed_sub_cadence` 分支，我已复算）。
- **P3-3 `_strip_scalar` 机理表述不准**：`report.md:50`、`decision.md` 追加节 §3 写「引号分支先返回 ⇒ `#` 注释不再剥除」；我直接调用实测为——引号+注释输入因首尾字符不同**不进**引号分支，而是走 `elif " #"` 分支**剥掉注释、保留引号** ⇒ 引号残留（结论与 rc=3 观测正确，机理描述错误；同节对裸标量例又写「`elif " #"` 分支生效」，前后自相矛盾）。

### 未证实 / 未逐件复算（如实登记）

1. **「`.planning` 之外全树仅此一份 `source_catalog.yaml`」**：我在可读范围内仅找到 `.review-zr407-20260818/company-wiki/config/source_catalog.yaml` 这一份；但枚举过程对若干目录被沙箱拒绝（多个 `.pytest_cache/`、`scratch/`、`.tmp-*`、`probe_root_m700/` 等 `Access denied`）⇒ **部分未证实**。同法下 `catalog.db` 全树扫描我得到与自述**完全相同的 4 处**命中。
2. **`evidence/copied_inputs_sha256.json` 的「1053/1053 逐件一致 + manifest 同哈希」**为实现者自算；我做的是**现存**逐件哈希对照（排除 `__pycache__`）：`harness` 11 件中 2 件不同（= 被补丁的两文件）、`iso` 559 件中 3 件不同（**全部**在 `iso/fixture_root/config/*.yaml`，由 `ensure_fixture_root()` 复跑重建，属预期）、`company-wiki` 2 件全同；`*.pyc` 未逐件比对。
3. **`--catalog <dir>/catalog.db` 的「6 次 resolve 调用 succeeded」**：我复测 `calls.total=6`、`consistent=true`，但因我的默认 resolver 不可运行而 `succeeded=0`；「6 次成功」未由我复现（绑定层结论已证实）。
4. **C-2 两处接受类 rc（自述 2）**：见四.6，我得到绑定接受但 rc=4（resolver 差异），非 rc=2。
5. **Gen-2「6 红 1 绿」**：为文件级核验（`ruling.md:131` + reviewer raw 在盘），**未**由我重跑 reviewer 会话。
6. **修前红的复现是概率性的**：我的 5 次为 `R,G,G,R,G`，实现者为 `绿,红,绿,红,红`——比例同为 3红2绿，排列不同属竞态随机，非矛盾。

---

## 六、边界声明：**我做了什么 / 我没有做什么**

**做了**：
- 只读生产树；全部命令为读类（`Get-ChildItem`/`Get-FileHash`/`Select-String`/`Get-Content`、`git diff`、`git status --porcelain <pathspec>`、`git ls-tree`、`git rev-parse`、`git hash-object`、`git cat-file -s`、`git diff --no-index`）。
- 测试**只在 `%TEMP%` 隔离副本**内跑：`%TEMP%\i14a_c1c2_rev`（本 attempt 复制件）与 `%TEMP%\i14a_sealed_rev`（封盘复制件），共完成 2 次 pytest 套件、`--all` 全扫、E0×3+E0×5、E1c×1、binding/percentiles 三 runner、M1–M4 四臂、5 个 C-2 配置 rc 实跑、`_strip_scalar` 直调。
- 写入面：**仅** `reviewer_report.md` 与 `reviewer_report.sha256`（两个新建文件）。

**没有做**（逐条）：
1. 未修改 `.planning\` 之外任何文件；未修改本 attempt 任何既有字节（`oracle.md`/`handoff.json`/`report.md`/`evidence/**`/`harness/**`/`iso/**`/`mutations/**` 我的会话内 mtime≥2026-09-25 的文件数 = **0**）；未修改封盘 `I-14-A/a20260919-01` 任何字节（除我复审前已存在的两处追加）。
2. 未做任何 git 写操作（无 `add/commit/checkout/stash/restore/reset`）；**本仓未执行裸 `git status`**，只执行了带 pathspec 的 `git status --porcelain -- …` 与 `git diff HEAD --name-only`。
3. 未联网。
4. 未改 `handoff.json`、未改任何 `status`、未替实现者落定、未代签 D1/D2/D3、未宣布 I-14-A 通过、未处置 D2 复签、未提产品收紧（后两者属另开受控卡）。
5. 未写五份计划文件；未碰 `RF/tools/`、`tools/` 或任何产品路径（C-2 全程只读）；未晋升探针。
6. 未在仓内留下新文件（除本报告两件）；未对封盘或本 attempt 树执行任何会触发写入的运行（复跑全部指向 `%TEMP%`）。

---

## 七、给编排方的一句话

本卡**可 ACCEPT**；建议另起一个**纯追加**的小更正登记（或并入下一轮 erratum）修正 P2-1、P2-2 与 P3-1~P3-3 五处文字/数值；D2 复签与产品侧 `consistent` 收紧**仍应另开受控卡**，本报告不作处置。
