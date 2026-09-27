
---

## C-1 / C-2 ERRATUM (APPEND-ONLY, 2026-09-24, I14A-C1C2-ERRATUM) — 第 1–127 行字节未改

> **本节更正第 91–92 行（`catalog.db` 论据）与第 97 行（行内 `#` 注释能力声明），并登记 C-1 的路线选择；原文保留于上方，按 T1-12 ① 以本节为准。**
>
> **前像自证**：本节追加前 `decision.md` = **8467 字节**，sha256 `a1a9d37478ffb42f15877ac29b9ecb044b8f402f4d77f532d1a25f1646bfda24`。
> 追加后文件的**前 8467 字节** sha256 复算必须等于该值 ⇒ **`prefix_bytes_preserved=true`**；
> 前像/后像 sha256、字节数与前缀复算记录落 `execution_runs/I14A-C1C2-ERRATUM/a20260924-01/evidence/prefix_proofs.json`。
>
> 授权与形态：`OWNER_DECISIONS.md` §十 L126 + §十一 L143；T1-12 ① + T1-21。
> 裁定依据：`execution_runs/I14A-D1-OPS-REVIEW/a20260924-01/ruling.md`（34896 B，sha256 `ede71bfa7b1a521b6f3252af539ef8aded9f645b92be82ac12460a93b11ab6c8`）§5.1(c)（C-1 OPEN ITEM 的二选一）与 §6.2/§6.3（C-2 的恢复规则：「由实现者/SLO owner 在 `decision.md` D2 与 `oracle.md` §9.3 追加更正」）。
> 本节由**修卡实现者**写入：**不代签 D1/D2/D3、不改任何 status、不宣布 I-14-A 通过、不解除晋升禁令。**

### 1) C-1 路线选择：**选 A —— 追加式更正该期望，限定到「存活 ≥ 2× 采样节拍」的夹具**

**(a) 选择**：**路线 A**（reviewer 给出的第 (i) 条路）。可执行实现落在 `I14A-C1C2-ERRATUM/a20260924-01/harness/`；封盘 `harness/fixture_spec.py:55` 的字节不动，其判读由封盘 `oracle.md` 追加节 §10.1 限定。

**(b) 选择理由**
1. **与已签裁定一致**：D1 已由独立运维 reviewer 逐项冻结并签署，其 §5.1(a)2 明写「适用域：存活 ≥ 约 2× 有效节拍（≈150 ms）的进程，PID 身份可保证」，§5.1(c) 明写「短于有效节拍的子进程可能完全不被观测到」。把期望限定到同一适用域，是**让判据与已签的物理事实对齐**，而不是放宽判据。
2. **阈值是实测可推导的，不是拍脑袋**：名义 50 ms（`iso/slo_probe_patched.py:76`）+ 有效节拍实测 64.0–75.2 ms（reviewer）与 63.67–66.92 ms（本 attempt 复算）⇒ `2 × 75.2 ms = 0.1504 s`；推导过程与两源哈希落 `evidence/threshold_derivation.json`。
3. **判据没有被消灭**（红线①）：修正后 E0 共 **14 项**绑定判据 —— `expected_raw_returncode`、`calls_failed`、`peak_rss_gt`、`peak_rss_source`、`rss_sample_count_min_gte`、`fixture_pid_identity_scope`、`rss_pids_include_child_pids`、`window_present`×4、`quick_check_outside_slo_window`、`rss_window_not_before_slo_window`、`frozen_budgets_untouched`（封盘版 13 项，本轮只增不减）；E1c 的身份断言原样保留；变异 M1/M2/M3 全部按期望打红（见下表）。
4. **不触碰已封盘、已被哈希引用的探针**：路线 A 零改动 `iso/slo_probe_patched.py`（sha256 仍 `14932c74…540e`，与 `review.md:131-132` 记录一致）。

**(c) 反例 —— 路线 B 为何被拒**
1. **B 改的是「被签署的对象」**：B 要在 `iso/slo_probe_patched.py` 里补 spawn/exit 时刻的确定性采样，而 D1 已对该探针的采样间隔与误差规则完成签署，`review.md:131-132`、`handoff.json` 与 ruling §2 都把该 sha256 当作锚。签署后再改签署对象 ⇒ 该签失效、需整体重冻重跑，成本与风险远超本卡授权（本卡授权的是**追加式更正**，不是改产品/改探针）。
2. **B 在本平台无法兑现「任何时刻可达」**：spawn 时刻的首样已经存在（`RssSampler._run` 首行即 `_collect()`），失效机理是**真实解释器尚未诞生**（venv `python.exe` 启动器 → 后代解释器）；要在任意时刻可达只能加退出时刻采样，而进程退出后 psutil 抛 `NoSuchProcess`（ruling §5.2 实测），ctypes 路径还能读到疑似 PID 复用的歧义读数（4743168 B）⇒ **B 不但改判据，还得先推翻 D1 已裁定的 peak 方式**。
3. **B 会把「测不到」伪装成「测到了」**：靠重试/忙等把短命子进程等进样本窗口，会改变被测量本身（阻塞探针、拉长 `command_total` 与采样窗口），违反 clause 3「不把合成内存量等同精确 RSS oracle」与 M1/M3 的窗口分离。
4. **B 不解决已登记的归属盲区**：ruling §5.3(c) 指出探针在样本缺被测 pid 时**不会**自动降级 `peak_rss_source`；这是机器强制的缺口，B 只会让身份断言更难失败，反而**削弱**可证伪性。

**(d) 兼容影响**
- **不变**：预算 `BUDGETS` 5/5/5/2；退出码 0/1/2/3/4 语义；报告字段结构；E1a/E1b/E1c/E2/E3/E4/E4b/E5/E6/E7 的期望；探针与封盘 harness 的字节。
- **变**：`fixture_pid_is_in_samples` 的适用域由「无条件」改为「寿命 ≥ 0.1504 s」；短命调用改为 `fixture_pid_identity_scope = not_claimed_sub_cadence` + 逐调用实测寿命入档；**新增（加固）** `rss_pids_include_child_pids` 接线（原本是死键，见封盘 `oracle.md` 追加节 §10.1）。
- **残留风险**：`elapsed_seconds` ≥ fixture 真实寿命 ⇒ 寿命落在阈值附近的调用可能被误判入域（**方向是更严**，产生假红而非假绿）；处置是复核寿命，**不得**为此下调阈值。
- **三代表并存**：封盘当时绿（`after/E0-baseline-F4/verdict.json` `all_ok=true`）／reviewer 会话 6 红 1 绿／本 attempt 修前 3 红 2 绿（E0×5）与套件 1 failed/11 passed/1 skipped、修后 E0×5 绿 + 全扫绿 + 套件 12 passed。**新绿不覆盖旧绿**。

**(e) 恢复规则**
1. 改阈值/适用域 ⇒ 新独立理由 + 新 oracle + 按 T1-12 ① 追加新节，**不回改**本卡任何历史字节；**不得**为让判据通过而放宽（clause 4 同源纪律）。
2. 回退＝恢复封盘 `harness/fixture_spec.py`（前像 sha256 `cd049eec…7d86a`）与 `harness/run_probe_cases.py`（前像 sha256 `6360a578…df678`）的原字节；二者当前只在本 attempt 的复制件上被修改，补丁与前后哈希在 `evidence/route_a_patch.diff` / `route_a_patch_hashes.json`。
3. 探针侧无回退需求（未改动）；若将来走路线 B ⇒ 属「采样方法变更」，须新独立理由 + 新 oracle，并重新取得 D1 签署。

**实测摘要（raw 全在 `I14A-C1C2-ERRATUM/.../evidence/`）**

| 臂 | 实测 rc / 结果 |
|---|---|
| 修前 E0 ×5（封盘 harness 复制件） | 3 红 / 2 绿，红的失败项恒为 `fixture_pid_is_in_samples` |
| 修前 pytest 套件 | rc=1，1 failed（E0）/ 11 passed / 1 skipped |
| 修后 E0 ×5 / `--all` 全扫 / binding / percentiles / pytest | 0 / 0 / 0 / 0 / **0（12 passed, 1 skipped）** |
| M1 不采样 | **红** `failed = {peak_rss_gt, peak_rss_source, rss_sample_count_min_gte, rss_pids_include_child_pids}` |
| M2 只记启动器 pid（跑 E1c） | **红** `failed = {fixture_pid_is_in_samples}`（唯一） |
| M3 F4 延寿 0.4 s + 同变异探针（跑 E0） | **红** `failed = {fixture_pid_is_in_samples}`（6 调用寿命 0.458–0.497 s 入域） |
| M4 F4 延寿 + 原探针（对照） | **绿**，identity 以 `alive_ge_2x_effective_cadence` 入域执行 |

### 2) C-2 更正一：`catalog.db` 论据（**第 91–92 行**）

> **第 91–92 行已过时，以本节为准**（原文保留于上方）。被更正句：「(`catalog.sqlite3`, `catalog.db` — the product's config uses the former and **`RF/tools/release_readiness.py` the latter**)」。

**本 attempt 自己的只读实测（`evidence/c2_measurements.json`）**

| # | 实测 |
|---|---|
| 1 | `tools/*.py` 共 **24** 个文件，正则 `\.db\b` **0 命中**（含 `catalog.db`） |
| 2 | `tools/release_readiness.py:37` = `CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"`（该文件 sha256 已记入证据） |
| 3 | 全工作树（排除 `.planning`/`.git`）`catalog.db` **4 命中**，**均非产品代码**：`.review-zr407-20260818/company-wiki/task_plan.md:1985`、同快照 `task_plan_cw_recovery_20260725.md:383`（均为 `.review-*` 快照内文档）、`assurance/runs/2026-09-11_r4-phase-b/reviews/G5-boundary-observation.json:53`、`audit_review/2026-08-12_zijin_skill_run_audit/progress.md:91`（均为历史记录） |
| 4 | 绑定实测：`--catalog <dir>/catalog.db` 被判 `consistent=true` 并执行 6 次 resolve，而解析器按 config 打开 `catalog.sqlite3` |

**后果（clause 6）**：`--catalog` 与 config「**证实实际目标一致**」这一分支，**对 `catalog.db` 这一名称并未达成** —— 白名单放行了一个与实际解析目标不同名的文件。**本卡只登记更正，不改代码**：把 `consistent` 收紧为「文件名必须等于 `configured_catalog_file`」属产品/探针代码变更，须另开受控卡（ruling §6.3 恢复规则的另一分支），本卡无此授权。
**生产影响（不夸大）**：现有生产配置只用 `catalog.sqlite3`，resolver 实际打开的与 config 一致；这是**探针白名单的名称一致性缺口**，不是生产解析错档。

### 3) C-2 更正二：行内 `#` 注释能力声明（**第 97 行**）

> **第 97 行已过时，以本节为准**（原文保留于上方）。被更正短语：「…a quoted or bare scalar, `${PROJECT_ROOT}` / `${USER_PROFILE}` expansion, **inline `#` comments**…」。

**本 attempt 实测（`evidence/c2_measurements.json`，`evidence/c2/cfg_*.yaml` + 每例 raw rc/report）**

| 配置形态 | raw rc | 结果 |
|---|---|---|
| `catalog_dir: "<dir>"`（引号，无注释） | **2** | 接受，`consistent=true` |
| `catalog_dir: "<dir>"  # c`（**引号 + 行内注释**） | **3** | **被拒**；`configured_catalog_dir` 保留字面引号；顶层 `error=catalog_config_mismatch` |
| `catalog_dir: <dir>  # c`（**裸标量 + 行内注释**） | **2** | **被接受**（`_strip_scalar` 的 `elif " #"` 分支生效）⇒ 能力声明须收窄为「仅裸标量」 |
| `catalog_dir: "${PROJECT_ROOT}/…${UNRESOLVED}"` | **3** | `binding.error=config_unreadable_by_probe_parser`，`binding.detail=unresolved variable in catalog_dir: …` |
| 缺 `catalog_dir` 键 | **3** | `binding.error=config_unreadable_by_probe_parser`，`binding.detail=catalog_dir not found in …` |

**性质**：**fail-closed**（拒绝而非猜测），方向安全；但**原文能力声明不准确**，带行内注释的**引号**配置会被误拒（生产表现为探针拒测、exit 3）。
**影响面（必须写明、不得夸大）**：真实生产配置 `.review-zr407-20260818/company-wiki/config/source_catalog.yaml:2` = `catalog_dir: "${PROJECT_ROOT}/.source_catalog"`，**不含行内注释**；`.planning` 之外全树仅此一份 `source_catalog.yaml` ⇒ **当前生产不受影响**。
机理（源码只读核对）：`iso/slo_probe_patched.py:82-88` `_strip_scalar` 的引号分支先 `return`，行内注释在该分支**不再剥除** ⇒ 引号残留 ⇒ 目录比对不通过。

### 4) 读法更正（登记，非缺陷；ruling §6.1）

顶层 `error` **恒为** `catalog_config_mismatch`（`iso/slo_probe_patched.py:522` 字面量）；parser 自身原因在 **`binding.error` / `binding.detail`**（实测两种：`config_unreadable_by_probe_parser` + `unresolved variable…` / `catalog_dir not found…`）。对「解析成功但目录不符」的一类（含带引号的行内注释），原因体现在 `binding.configured_catalog_dir`（引号残留）与 `binding.same_directory: false`。**引用 D2 时必须引 `binding.*`，不能只引顶层 `error`。**

### 5) D2 复签不在本卡

- **`D2_resign_pending = true`**：本卡只完成更正与证据准备；`confirmation_D2` 的复签归 SLO/探针 owner（ruling §6.3 的「更正 + 复签」两步中的第二步）。
- 第 12 行的 D2 状态与第 9–13 行表格记录的是**当时**状态，按 T1-21 **不回改**。
- 本节**不代签 D1/D2/D3、不改 status、不宣布 I-14-A 通过**；`iso/slo_probe_patched.py` 的晋升禁令继续有效。
