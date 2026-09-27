# I14A-C1C2-ERRATUM oracle.md — FROZEN BEFORE ANY RUN

> 本文件在本 attempt 的**第一次运行命令之前**写定；写定后不再编辑正文（如需追加 provenance，
> 按 T1-21 只允许追加式登记，禁止改写为「从未编辑」）。

| 项 | 值 |
|---|---|
| 卡 | `I-14-A`（性能测量先验证失败分支）—— 本卡的**追加式更正轮**（erratum round） |
| 本 attempt（唯一新建写入面） | `execution_runs/I14A-C1C2-ERRATUM/a20260924-01/` |
| 被更正的封盘 attempt（**只许追加**） | `execution_runs/I-14-A/a20260919-01/` |
| 我的角色 | **修卡实现者**（implementer of the append-only correction）。**不是**签署人：不签 D1/D2/D3、**不改任何 status**、**不宣布 I-14-A 通过** |
| 更正范围 | **仅** C-1（冻结期望失效 / D1 OPEN ITEM）与 C-2（`decision.md` 两处原文被推翻 + 1 处读法更正登记） |
| 冻结时刻 | 写定于第一次运行命令之前（UTC 记录在 `handoff.json.frozen_utc`） |

## 0. 授权与依据（本 attempt 逐条引用，不靠转述）

| 依据 | 原文要点 / 校验值 |
|---|---|
| 裁定载体（**只读**） | `execution_runs/I14A-D1-OPS-REVIEW/a20260924-01/ruling.md` = **34896 B**，sha256 `ede71bfa7b1a521b6f3252af539ef8aded9f645b92be82ac12460a93b11ab6c8`（本 attempt 起始时复算一致） |
| 裁定载体 handoff（**只读**） | 同目录 `handoff.json` = **7166 B**，sha256 `1890d8207aa74141ca061c9363893a056a95d6a00cd805d54319b2c7e6a9bd1d`（复算一致） |
| 授权链 | `OWNER_DECISIONS.md` **§十 L126**：「**I-14-A D1/D2** | **指派**：运维 owner 签 D1、SLO/探针 owner 签 D2 \| 编排层按此派单（**D1 必须由非本探针作者签**）；未签前 `iso/slo_probe_patched.py` **不得**进 `RF/tools/`」 |
| 授权链 | `OWNER_DECISIONS.md` **§十一 L143**：「1 \| I-14-A D1/D2 \| **派新 subagent** 当独立运维/SLO reviewer \| 编排层创建独立 reviewer subagent（**D1 必须非本探针作者**）」 |
| 更正形态 | 登记册口径 **T1-12 ①**（`OWNER_DECISIONS.md` L218）：「一律采用 **① 形态**（追加新节 + 行级「第 X 行已过时，以本节为准」标注）；**不外扩**就地编辑授权」 |
| 更正形态 | 登记册口径 **T1-21**（`OWNER_DECISIONS.md` L227）：「允许**追加式 provenance 登记**（写明何时、为何、新 hash），**禁止**回改为『从未编辑』」 |
| reviewer 原话边界 1 | 「我不改封盘 attempt，只登记」（ruling §5.1(c)：**本人不修改封盘 attempt，故只登记、不代改**） |
| reviewer 原话边界 2 | 「E0 期望的更正只能由**实现者/owner 追加执行**」（ruling §5.1(c) 二选一由实现者执行并追加式登记） |
| reviewer 原话边界 3 | 「**本人不宣布 I-14-A 通过**」（ruling §5 总裁定 / handoff `does_not_declare_card_pass: true`） |

## 1. 纪律冻结（违反即本卡失败；每条附自查方式）

1. **封盘 attempt 只许追加**：`oracle.md` / `decision.md` / `review.md` / `binding.json` / `commands.json` / `evidence/**` 的**既有字节一个都不改**；任何更正 = 在文件**末尾追加新节**，节内写明「本节更正第 X 行 / Y 句，原文保留于上方、按 T1-12 ① 以本节为准」。
   自查：每处追加登记**前像 sha256 + 字节数**，追加后**前缀证明** = 前 N 字节 sha256 必须等于前像 sha256 ⇒ `prefix_bytes_preserved=true`（复算落 `evidence/prefix_proofs.json`）。
2. **只读生产树**：不改 `.planning\` 之外任何文件；禁止 `git add/commit/checkout/stash/restore/reset`；禁止联网。结束前 `git -c core.quotepath=false diff HEAD --name-only` 的**非 `.planning` 计数必须 = 0**。
3. **不改 status、不代签、不宣布 I-14-A 通过**：本 attempt 的 `handoff.json` 顶层 `status` 写 `review_pending`、`implementer_signed=false`、`does_not_claim_I14A_acceptance=true`。
4. **任何 GREEN 必附变异证明**；缺证据写「未证实」，**不造绿色样例**；观测到与预测不符时**如实登记**，不回改预测文本。
5. **先冻结本 oracle 再跑第一次**；所有 JSON 写后重新解析校验。
6. **不碰** `I14A-D1-OPS-REVIEW/`（裁定载体只读）、**不写**五份计划文件（`task_plan.md`/`findings.md`/`progress.md`/`implementation_plan.md`/`audit_report.md`）、**不碰** `RF/tools/` 或任何产品路径、**不晋升**、**不联网**。
7. **复跑隔离**：`harness/fixture_spec.ensure_fixture_root()` 会 unlink 并重建 `iso/fixture_root/**` ⇒ 所有复跑必须在**本 attempt 自己的复制件**上进行，封盘 attempt 一个字节都不碰（复制品 sha256 逐件对照源，落 `evidence/copied_inputs_sha256.json`）。

## 2. C-1 事实基线（**两代并存，如实披露**）

| 代 | 时刻 | E0/F4 身份断言 `fixture_pid_is_in_samples` | 证据 |
|---|---|---|---|
| **Gen-1（封盘当时）** | 2026-09-19 | **绿**（`all_ok=true`，6 项身份 pid 全部在样本中） | 封盘 `I-14-A/a20260919-01/after/E0-baseline-F4/verdict.json` |
| **Gen-2（reviewer 会话）** | 2026-09-24 | **6 红 1 绿**：冻结套件 1 红 + 单例复跑 5/5 红；唯一绿 = `--all` 首跑 | ruling §4.3；`evidence/suite_patched_stdout.txt`、`evidence/e0_repeat/run1..5` |
| **Gen-3（本 attempt）** | 本会话 | **待测**（见 §5 A0/A0-s 臂） | 本 attempt `evidence/red/` |

**冻结纪律**：新绿**不得**覆盖旧绿记录；三代数值必须同时出现在本 attempt 的 handoff 与封盘追加节中。
失败机理（ruling §4.3，可核）：E0 失败样本的 `rss_sampled_pids` 只含 Popen 启动器 pid，fixture 自报 `os.getpid()` 不在其中 —— venv `python.exe` 是启动器、真实解释器是其后代，F4 生命周期短于实测节拍 ⇒ 首样（spawn 时刻）只见启动器，`sample_now` 触发时子进程已退出。

## 3. C-1 路线**预承诺**：选 **路线 A**（追加式更正期望，限定到「存活 ≥ 2× 有效节拍」的夹具）

> 正式的选择理由 + 反例（B 为何被拒）+ 兼容影响 + 恢复规则，按授权落在**封盘 `decision.md` 追加节**；
> 本节是运行前的预承诺，用于避免「看到结果再选路线」。

- **A（选定）**：追加式更正 `fixture_spec`/`oracle` 中 F4 的身份断言，限定域 = **存活 ≥ 2× 有效节拍**的夹具。
- **B（拒绝）**：补 spawn/exit 时刻的确定性采样，不改期望。
- 预承诺的判定：A 被选中的**决定性理由** = D1 已由独立运维 reviewer **签署并冻结了采样节拍的适用域**（ruling §5.1(a)2「适用域：存活 ≥ 约 2× 有效节拍（≈150 ms）的进程，PID 身份可保证」）⇒ 更正期望使其**与已签裁定一致**；而 B 要求改动**已封盘、且其 sha256 被 `review.md:131-132` 引用**的 `iso/slo_probe_patched.py`（`14932c74…`），等于签署后改签署对象。

## 4. 阈值推导（**必须落盘**，见 `evidence/threshold_derivation.json`）

- 名义间隔：`RSS_SAMPLE_INTERVAL_SECONDS = 0.05`（50 ms，封盘 `iso/slo_probe_patched.py:76`，D1 签署值）。
- **有效节拍实测**（reviewer，`I14A-D1-OPS-REVIEW/.../evidence/e1c_samples_inside_life.json`）：`spacing_ms_min = 64.0`、`spacing_ms_max = 75.2`（6 次 E1c 调用，n=26–29 样 / 1.70–2.06 s）。
- **本 attempt 独立复算**：对每次 E1c 调用算 `spacing = rss_sample_window_seconds / (rss_sample_count - 1)`，与上表同法；取本会话最大值 `cadence_max_own`。
- **阈值**：`IDENTITY_SCOPE_MIN_SECONDS = 2 × max(cadence_max_reviewer, cadence_max_own)`；按 reviewer 数值 = `2 × 0.0752 = 0.1504 s`（150.4 ms，与 ruling 的「≈150 ms」一致）。**取两者较大值**，故本会话节拍偏慢时阈值只会更大（更严），不会更小。
- **机理**：节拍 `c`、存活 `L` ⇒ spawn 后第 1 次周期采样落在 `c`、第 2 次落在 `2c`…；`L ≥ 2c` ⇒ 至少一次周期采样落在存活期内 ⇒ fixture pid **必**被采到（spawn 竞态样不再是唯一机会）；`L < 2c` ⇒ 只有 spawn 时刻的竞态样 ⇒ 身份**不可保证**，因此不得作为判据。
- **用哪个寿命**：判据用探针报告的 per-call `elapsed_seconds`（子进程墙钟，含进程创建开销）作为寿命代理。它 **≥** fixture pid 真实寿命 ⇒ 该代理只会把调用**多算进域内**（更严），不会把本该在域内的调用算出域 ⇒ **不存在「放宽到空」的方向性风险**；反之若用更小的估计才会产生漏判。
- 观测到的数值对照：封盘 E0（F4）6 次调用 `elapsed = 0.051–0.078 s` **< 0.1504**（域外）；E1c（F3）`elapsed = 1.70–2.15 s` **≥ 0.1504**（域内）。

## 5. 修正后的期望（冻结；本 attempt 的可执行实现 = 本 attempt `harness/` 复制件）

对 `expect_business.fixture_pid_is_in_samples` 的**修正语义**（E0 与 E1c 共用同一条规则，按调用逐条判定）：

- `in_scope(call) := call.elapsed_seconds >= 0.1504`
- **存在域内调用** ⇒ 检查名仍为 `fixture_pid_is_in_samples`：这些调用自报的 fixture pid 必须 ⊆ 报告的 `rss_sampled_pids`（**全局并集语义与原断言完全一致，不放宽**）。
- **不存在域内调用** ⇒ 检查名 `fixture_pid_identity_scope`，`ok=true`，detail 必须写 `status=not_claimed_sub_cadence` + 阈值 + **逐调用实测寿命数组**（可审计，不是空白跳过）。
- **E0 其余判据一字不改地保留**：`expect_rc=2`、`calls_failed=0`、`peak_rss_gt>0`、`peak_rss_source=="live_sample"`、`rss_sample_count_min>=1`、4 项 `window_present:*`、`quick_check_outside_slo_window`、`rss_window_not_before_slo_window`、`frozen_budgets_untouched`。
- **加固（非削弱）**：接线 spec 里**已声明但从未被 runner 评估**的 `rss_pids_include_child_pids`（每个调用的 `child_pid` ⊆ `rss_sampled_pids`；`run_probe_cases.py:111` 只读 `rss_pids_match_child_pids`，而没有任何 case 声明该键 ⇒ 该期望**一直是死键**）。接线后若出现红 ⇒ **如实登记为新发现**，不回退、不粉饰、不改本节。

**红线 ① 自查（为何这不是「无论如何都绿」的空断言）**：
(a) E0 的 6 项测量判据 + 接线后的 pid 判据仍然绑定；(b) E1c（域内）的 `fixture_pid_is_in_samples` 仍然原样绑定；(c) §6 的变异臂**必须**把 E0 打红 —— 任一不成立即本卡失败。

## 6. 期望的臂（每臂的期望与判据；raw rc 为实测记录，不预填）

| 臂 | 内容 | 期望 |
|---|---|---|
| **A0**（RED） | **字节相同**的封盘 harness 复制件，跑 `--case E0-baseline-F4` ×5 | **≥1 次** `all_ok=false` 且 `failed_checks` 含 `fixture_pid_is_in_samples`；若 5/5 绿 ⇒ 如实登记「本会话未复现红」，**不造红** |
| **A0-s**（RED） | 同上复制件跑冻结 pytest 套件 | rc=1；1 failed（`test_frozen_case[E0-baseline-F4]`）/ 11 passed / 1 skipped（与 ruling §4.3 一致；不符则如实登记） |
| **A1**（GREEN） | 修正后 harness：`--case E0-baseline-F4` ×5、`--all` 全扫、`--binding-mismatch`、`--binding-ok`、`--percentiles`、pytest 套件 | 全部 `all_ok=true` / 套件 rc=0 |
| **M1**（变异·不采样） | E0 加 `--rss-sampler none` | runner rc=1，`failed_checks ⊇ {peak_rss_gt, peak_rss_source, rss_sample_count_min_gte}` ⇒ **证明 E0 不是空断言** |
| **M2**（变异·只记启动器 pid） | 探针复制件移除进程树遍历（`_collect` 只记 `self._pid`）跑 **E1c** | `failed_checks == {fixture_pid_is_in_samples}`（唯一红，其余全绿）⇒ **证明域内身份判据仍可被打红** |
| **M3**（变异·F4 延寿 0.4 s） | F4 复制件 `sleep(0.4)` + 同一变异探针跑 **E0** | `failed_checks == {fixture_pid_is_in_samples}` ⇒ **证明域门是活的**（寿命过线后身份判据重新生效并打红） |
| **M4**（变异对照） | F4 `sleep(0.4)` + **原探针**跑 E0 | 绿，且 detail 中域内调用数 = 6 ⇒ 证明 M3 的红来自域门而非其他破坏 |

> GREEN 臂（A1）**只有在 M1/M2/M3 至少一条按期望打红时**才被承认；否则按「未证实」处理，不得报绿。

## 7. C-2 冻结预测（自己只读复测；被推翻则如实登记，不改预测）

| # | 预测 | 判定方式 |
|---|---|---|
| P1 | `tools/*.py` 中 `.db`（含 `catalog.db`）命中 = **0** | `Select-String '\.db\b' tools\*.py` |
| P2 | `tools/release_readiness.py:37` = `CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"` | 直读第 37 行 |
| P3 | 封盘 `decision.md:91-92` 的原文主张（「`RF/tools/release_readiness.py` the latter（`catalog.db`）」）与 P1/P2 矛盾 ⇒ **clause 6「证实实际目标一致」对 `catalog.db` 这一名称未达成** | 对照 P1/P2 实测 |
| P4 | `catalog_dir: "<dir>"  # c` ⇒ 探针 **rc=3**（fail-closed），`configured_catalog_dir` 保留字面引号；具体原因在 `binding.error` / `binding.detail`，顶层 `error` 恒为 `catalog_config_mismatch` | 本 attempt 实跑（复制件） |
| P5 | 真实生产配置 `.review-zr407-20260818/company-wiki/config/source_catalog.yaml:2` = `catalog_dir: "${PROJECT_ROOT}/.source_catalog"`，**不含行内注释** ⇒ **当前生产不受影响**（**不夸大为生产缺陷**） | 直读第 2 行 + 全树枚举 `source_catalog.yaml` |
| P6 | 能力声明不准确：`decision.md:95-99` / `oracle.md:219-224` 声称 parser 处理「inline `#` comments」，实测**被拒** | P4 实测 + `_strip_scalar` 源码（封盘 `iso/slo_probe_patched.py:82-88`：引号分支先返回，`#` 注释不再剥除 ⇒ 引号残留） |

**D2 复签不在本卡**：本 attempt 只做更正并把复核证据备好 ⇒ `handoff.D2_resign_pending=true`。

## 8. 本 attempt **明确不做**的事

1. 不改封盘 attempt 的任何既有字节（只 `oracle.md` + `decision.md` 各追加一节；`review.md` 经查**未重复**被推翻的两处原文 ⇒ 不追加，判定理由记入 handoff）。
2. 不碰 `I14A-D1-OPS-REVIEW/`（裁定载体只读）；不写五份计划文件；不碰 `RF/tools/` 与任何产品路径；不晋升 `iso/slo_probe_patched.py`。
3. 不签 D1/D2/D3、不改任何 `status`、不宣布 I-14-A 通过、不代 reviewer 复签 D2。
4. 不做 git 写操作、不联网、不改预算（`BUDGETS` 5/5/5/2 全程只读核对）。
