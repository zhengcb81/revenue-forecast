
---

## 10. APPEND-ONLY CORRECTION (I14A-C1C2-ERRATUM, 2026-09-24) — §1–§9 above are byte-for-byte unchanged

> **本节更正第 117–122 行（无条件身份断言）、第 119–120 行的「Both are checked」主张、第 85 行的适用域，并更正 §9.3 第 219–220 行的能力声明；原文保留于上方，按 T1-12 ① 以本节为准。**
>
> **前像自证**：本节追加前 `oracle.md` = **20457 字节**，sha256 `87775f2f4ff025e4d104fd1dfe23d7f7bfc75a20520f8859732133e96ec84bb7`。
> 追加后文件的**前 20457 字节** sha256 复算必须等于该值 ⇒ **`prefix_bytes_preserved=true`**；
> 前像/后像 sha256、字节数与前缀复算记录落 `execution_runs/I14A-C1C2-ERRATUM/a20260924-01/evidence/prefix_proofs.json`。
>
> 授权与形态：`OWNER_DECISIONS.md` §十 L126 + §十一 L143；T1-12 ①（追加新节 + 行级「已过时，以本节为准」）+ T1-21（追加式 provenance，禁止回改）。
> 裁定依据：`execution_runs/I14A-D1-OPS-REVIEW/a20260924-01/ruling.md`（34896 B，sha256 `ede71bfa7b1a521b6f3252af539ef8aded9f645b92be82ac12460a93b11ab6c8`）§4.3、§5.1(c)、§6.2。
> 本节**不改变任何 status、不代签 D1/D2/D3、不宣布 I-14-A 通过、不解除晋升禁令**。

### 10.1 C-1 — E0/F4 身份断言的适用域更正（**路线 A**，D1 OPEN ITEM 的处置）

**被更正的原文（全部保留于上方，一个字节未删）**

| 位置 | 原文要点 | 更正（以本节为准） |
|---|---|---|
| **第 117–122 行** | 「the sampler's `rss_sampled_pids` must *contain* the fixture's self-reported `os.getpid()` …」——**无条件**表述 | **第 117–122 行已过时**：该身份断言的适用域为**存活 ≥ 2× 有效节拍**的调用（阈值 **0.1504 s**）。寿命短于阈值的调用**不主张**身份，改为在 verdict 中逐调用登记实测寿命并标 `identity-not-claimed`；该调用的其余判据（rc、失败计数、`peak_rss_gt`、`peak_rss_source == live_sample`、`rss_sample_count_min ≥ 1`、四个窗口判据、预算未动、`child_pid ∈ rss_sampled_pids`）**全部照旧绑定** |
| **第 85 行（§4 E1c 行）** | E1c 要求 `rss_sampled_pids` contains the fixture's `os.getpid()` | **仍有效，适用域由本节限定**：F3 实测寿命 1.734–1.816 s ≥ 0.1504 s ⇒ **域内**，断言原样执行（本 attempt 实测 6/6 调用 `fixture_reported_pids ⊆ sampled`，绿） |
| **第 119–120 行** | 「Both are checked in `run_probe_cases.py` (`fixture_pid_is_in_samples`, `rss_pids_include_child_pids`)」 | **该句对 `rss_pids_include_child_pids` 不成立**：封盘 `harness/run_probe_cases.py:111` 分支读的键是 `rss_pids_match_child_pids`，而 `harness/fixture_spec.py` 声明的键是 `rss_pids_include_child_pids` ⇒ **没有任何 case 声明 runner 实际读取的键**，该期望自封盘起**从未被评估**（死键）。本 attempt 已在**自己的复制件**上接线并实测（**加固，非削弱**）；封盘 harness 字节未动 |
| `harness/fixture_spec.py:55`（封盘可执行期望，**未修改**） | `"fixture_pid_is_in_samples": True`（对 E0 无条件成立） | 该可执行期望的**判读方式**由本节限定；封盘文件保持原字节（按 T1-12 ① 不就地编辑）。修正后的可执行实现位于 `I14A-C1C2-ERRATUM/a20260924-01/harness/`（补丁与前后哈希见证据） |

**阈值推导（落盘 `I14A-C1C2-ERRATUM/.../evidence/threshold_derivation.json`）**

- 名义间隔 50 ms（封盘 `iso/slo_probe_patched.py:76`，D1 签署值）。
- 有效节拍实测：D1 reviewer 64.0–75.2 ms/样（6 次 E1c 调用，其 `e1c_samples_inside_life.json` sha256 已记入推导文件）；本 attempt 独立复算 **63.67–66.92 ms**（`window / (count − 1)`，同 6 次调用）。
- **阈值 = 2 × max(两源最大值) = 2 × 75.2 ms = 0.1504 s**（与 ruling §5.1(a)2「存活 ≥ 约 2× 有效节拍（≈150 ms）」一致）。
- 机理：周期首样落在 spawn 后约 1 个节拍；存活 ≥ 2 个节拍 ⇒ 至少一次周期采样落在存活期内 ⇒ fixture pid 必被采到；寿命更短者只被 spawn 时刻的竞态样覆盖，本平台身份**不可保证**（ruling §4.3 的实测反例）。
- 寿命代理用探针报告的 per-call `elapsed_seconds`（子进程墙钟）≥ fixture pid 真实寿命 ⇒ 该域**只会多算（更严）**，不存在「放宽到空」的方向。

**修前 / 修后 / 变异实测（全部 raw 落 `I14A-C1C2-ERRATUM/.../evidence/{red,green,mutations}/`）**

| 臂 | 内容 | 实测 |
|---|---|---|
| Gen-1（封盘 2026-09-19） | `after/E0-baseline-F4/verdict.json` | **绿** `all_ok=true`（6 个 fixture pid 全在样本中）——**保留，不被新绿覆盖** |
| Gen-2（reviewer 2026-09-24） | ruling §4.3 | **6 红 1 绿**（套件 1 红 + 单例 5/5 红；唯一绿 = `--all` 首跑）——**保留** |
| **A0 修前红（本 attempt）** | 字节相同的封盘 harness 复制件，E0 ×5 | **3 红 / 2 绿**；红的失败项**只有** `fixture_pid_is_in_samples`（run1 绿、run2 红、run3 绿、run4 红、run5 红） |
| **A0-s 修前红（套件）** | 同上复制件跑冻结 pytest | rc=**1**，**1 failed**（`test_frozen_case[E0-baseline-F4]`）/ 11 passed / 1 skipped —— 与 ruling §4.3 一致 |
| **A1 修后绿** | 修正后复制件 | E0 ×5 **全绿**；`--all` 全扫 rc=0（E0=2, E1a=4, E1b=4, E1c=2, E2=2, E3=2, E7=2，全 `all_ok`）；binding mismatch/ok、percentiles 各 rc=0；pytest **rc=0，12 passed / 1 skipped** |
| **M1 变异·不采样** | E0 + `--rss-sampler none` | **红**：`failed = {peak_rss_gt, peak_rss_source, rss_sample_count_min_gte, rss_pids_include_child_pids}` ⇒ E0 **不是空断言** |
| **M2 变异·只记启动器 pid** | 去掉进程树遍历的探针副本跑 **E1c** | **红**：`failed = {fixture_pid_is_in_samples}`（**唯一**红，其余 13 项全绿）⇒ 域内身份判据**仍可被打红** |
| **M3 变异·F4 延寿 0.4 s** | 延寿夹具 + 同一变异探针跑 **E0** | **红**：`failed = {fixture_pid_is_in_samples}`，6 次调用寿命 0.458–0.497 s 全部**入域** ⇒ **域门是活的** |
| **M4 变异对照** | 延寿夹具 + 原探针跑 E0 | **绿**，且 identity 检查以 `alive_ge_2x_effective_cadence` **入域执行**（寿命 0.462–0.497 s）⇒ M3 的红来自域门本身 |

**红线自查**：本更正**未**把期望改成「无论如何都绿」——修正后 E0 共 **14 项**绑定判据（`expected_raw_returncode`、`calls_failed`、`peak_rss_gt`、`peak_rss_source`、`rss_sample_count_min_gte`、`fixture_pid_identity_scope`、`rss_pids_include_child_pids`、`window_present`×4、`quick_check_outside_slo_window`、`rss_window_not_before_slo_window`、`frozen_budgets_untouched`；封盘版为 13 项），E1c 的身份判据原样绑定且被 M2 打红，域门本身被 M3 打红。**任一 GREEN 均附上述变异证明**；缺证据处按「未证实」处理。

**兼容影响**：预算 `BUDGETS` 5/5/5/2 未动（`frozen_budgets_untouched` 在每份 verdict 中复算）；探针与封盘 harness 的字节未改；E1c/E2/E3/E7/E4/E4b/E6 的期望一字未改。**风险残留**：寿命落在 0.1504 s 附近的调用会因 `elapsed` 高估真实寿命而被判入域（**方向是更严**，可能出现假红；假红时应复核寿命而非放宽阈值）。

**恢复规则**：① 阈值/适用域若再改 ⇒ 必须给出新的独立理由 + 新 oracle，并按 T1-12 ① 追加新节，不回改本节或 §1–§9；② 回退＝恢复封盘 `harness/fixture_spec.py` 与 `harness/run_probe_cases.py` 的原字节（其前像哈希已在 `I14A-C1C2-ERRATUM/.../evidence/route_a_patch_hashes.json` 登记）；③ 探针侧无需回退（本更正**未改** `iso/slo_probe_patched.py`，sha256 仍 `14932c744839c89f8af126b8d7eba11bafe9192dd73c3b5277a41ef6aaa3540e`）。

### 10.2 C-2 — §9.3 能力声明更正 + 读法更正登记（ruling §6.2 / §6.1）

> **本节更正 §9.3 第 219–220 行；原文保留于上方，按 T1-12 ① 以本节为准。**

| 位置 | 原文 | 更正（以本节为准） |
|---|---|---|
| **第 219–220 行** | `config_catalog_dir()` handles … "a top-level scalar, quoted or bare, with `${PROJECT_ROOT}` / `${USER_PROFILE}` expansion **and inline `#` comments**" | **第 219–220 行的「inline `#` comments」已过时**：实测（本 attempt，`evidence/c2_measurements.json`）`catalog_dir: "<dir>"  # c` ⇒ **rc = 3 被拒**，`configured_catalog_dir` **保留字面引号**（`"\"…\\catalog\""`)；机理为 `_strip_scalar`（`iso/slo_probe_patched.py:82-88`）**引号分支先返回**，`#` 注释不再剥除。**同轮新增实测**：**裸标量** + 行内注释 `catalog_dir: <dir>  # c` ⇒ **rc = 2 被接受** ⇒ 能力声明必须收窄为「**仅裸标量**支持行内注释；**带引号**标量 + 行内注释被拒（fail-closed）」 |

- **性质**：**fail-closed**（拒绝而非猜测），方向安全；但**能力声明不准确**，且带行内注释的**引号**配置会被误拒（表现为探针拒测、exit 3）。
- **影响面（不夸大）**：真实生产配置 `.review-zr407-20260818/company-wiki/config/source_catalog.yaml:2` = `catalog_dir: "${PROJECT_ROOT}/.source_catalog"`，**不含行内注释**；全树（`.planning` 之外）仅此一份 `source_catalog.yaml` ⇒ **当前生产不受影响**，不得记为生产缺陷。
- **读法更正（登记，非缺陷）**：顶层 `error` **恒为** `catalog_config_mismatch`（`iso/slo_probe_patched.py:522` 字面量）；parser 自身原因在 `binding.error` / `binding.detail`（实测 `config_unreadable_by_probe_parser` + `unresolved variable in catalog_dir: …` / `catalog_dir not found in …`）；而「解析成功但目录不符」的一类（含带引号的行内注释）原因体现在 `binding.configured_catalog_dir`（引号残留）与 `binding.same_directory: false`。引用 D2 时不得只引顶层 `error`。

### 10.3 本节的边界（逐条）

1. 封盘 `oracle.md` / `decision.md` / `review.md` / `binding.json` / `commands.json` / `evidence/**` 的**既有字节零改动**；本节是 `oracle.md` 的唯一追加节。
2. 封盘 `harness/**`、`iso/**` **未修改**（本 attempt 的可执行更正全部发生在自己的复制件上）。
3. D2 的**复签不在本卡**：`D2_resign_pending=true`（本 attempt 只做更正并备妥复核证据）。
4. D1 已由独立运维 reviewer 在其载体签署；**本节不是签署**，也**不宣布 I-14-A 通过**（E0 退出条件的关闭须由有权方判定）。
5. 三代 E0 记录（封盘绿 / reviewer 6红1绿 / 本 attempt 修前 3红2绿 → 修后绿）**并存披露**，未用新绿覆盖旧绿。
