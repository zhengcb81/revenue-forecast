# I14A-C1C2-ERRATUM — 追加式更正轮报告（C-1 + C-2）

| 项 | 值 |
|---|---|
| 卡 | `I-14-A`（追加式更正轮，**非**验收轮） |
| 本 attempt | `execution_runs/I14A-C1C2-ERRATUM/a20260924-01/` |
| 角色 | **修卡实现者** —— **不自签、不改 status、不宣布 I-14-A 通过** |
| 被更正封盘 attempt | `execution_runs/I-14-A/a20260919-01/`（**只追加** `oracle.md` + `decision.md` 各一节） |
| 裁定依据 | `execution_runs/I14A-D1-OPS-REVIEW/a20260924-01/ruling.md`（34896 B，sha256 `ede71bfa…ab6c8`）+ 其 `handoff.json`（7166 B，sha256 `1890d820…bd1d`） |
| 授权 | `OWNER_DECISIONS.md` §十 L126 + §十一 L143；形态 T1-12 ① + T1-21 |

---

## 1. C-1：选 **路线 A**（追加式更正期望，限定到「存活 ≥ 2× 有效节拍」的夹具）

**理由（正式版在封盘 `decision.md` 追加节 §1）**：D1 已由独立运维 reviewer 签署并**冻结了采样节拍的适用域**（ruling §5.1(a)2「存活 ≥ 约 2× 有效节拍（≈150 ms）」、§5.1(c)「短于节拍者可能完全不被观测」）⇒ 让判据与已签的物理事实对齐；阈值可由两源实测节拍推出（**0.1504 s = 2 × 75.2 ms**，推导落 `evidence/threshold_derivation.json`）；且路线 A **零改动**已被 `review.md:131-132` 哈希引用的探针（sha256 仍 `14932c74…540e`）。

**反例（路线 B 为何被拒）**：① B 改的是**已被 D1 签署的对象**（探针本体），签署后改签署对象 ⇒ 签署失效、须整体重冻重跑；② B 在本平台无法兑现「任何时刻可达」—— spawn 首样**已经存在**，失效机理是真实解释器尚未诞生，退出时刻采样会撞上 psutil `NoSuchProcess` 与 ctypes 的 PID 复用歧义读数（ruling §5.2 实测 4743168 B）；③ 忙等/重试会改变被测量本身，违反 clause 3 与窗口分离；④ B 解决不了 ruling §5.3(c) 的**归属盲区**，反而让身份断言更难失败。

**兼容影响**：预算 5/5/5/2 未动、退出码语义未动、其余 9 个反例期望一字未改；E0 由 13 项判据变 **14 项**（只增不减）；残留风险 = `elapsed` 高估真实寿命 ⇒ 阈值附近可能假红（**方向更严**，处置是复核寿命而非下调阈值）。

**恢复规则**：改阈值 ⇒ 新独立理由 + 新 oracle + T1-12 ① 追加；回退 = 恢复封盘 harness 两文件原字节（前像 sha 已登记于 `evidence/route_a_patch_hashes.json`）；探针侧无回退需求（未改动）。

### 修前 / 修后 / 变异（raw rc）

| 臂 | 实测 |
|---|---|
| **修前** E0 ×5（封盘 harness 字节相同复制件） | probe rc 恒 **2**；runner：**3 红 / 2 绿**（run1 绿、run2 红、run3 绿、run4 红、run5 红），红的失败项**只有** `fixture_pid_is_in_samples` |
| **修前** 冻结 pytest 套件 | **rc=1**，**1 failed**（`test_frozen_case[E0-baseline-F4]`）/ 11 passed / 1 skipped |
| **修后** E0 ×5 | **5/5 绿**（runner rc=0），probe rc 恒 2 |
| **修后** `--all` 全扫 | **rc=0**：E0=2、E1a=4、E1b=4、E1c=2、E2=2、E3=2、E7=2，全 `all_ok` |
| **修后** binding-mismatch / binding-ok / percentiles | 各 runner **rc=0** |
| **修后** pytest 套件 | **rc=0**，**12 passed / 1 skipped** |
| **M1 变异·不采样**（E0 + `--rss-sampler none`） | **红** `failed = {peak_rss_gt, peak_rss_source, rss_sample_count_min_gte, rss_pids_include_child_pids}` ⇒ E0 **非空断言** |
| **M2 变异·只记启动器 pid**（去树遍历探针，跑 E1c） | **红** `failed = {fixture_pid_is_in_samples}`（**唯一**红）⇒ 域内身份判据**可被打红** |
| **M3 变异·F4 延寿 0.4 s**（+ 同变异探针，跑 E0） | **红** `failed = {fixture_pid_is_in_samples}`，6 调用寿命 0.458–0.497 s **入域** ⇒ **域门是活的** |
| **M4 对照·F4 延寿 + 原探针** | **绿**，identity 以 `alive_ge_2x_effective_cadence` 入域执行（0.462–0.497 s） |

**三代并存（未用新绿覆盖旧绿）**：Gen-1 封盘 2026-09-19 **绿**（`after/E0-baseline-F4/verdict.json` `all_ok=true`）｜Gen-2 reviewer 2026-09-24 **6 红 1 绿**｜Gen-3 本 attempt 修前 **3 红 2 绿** + 套件 1 failed、修后 **全绿**。

**一处披露的自家失误**：变异驱动脚本首跑把 spec 补丁打在了本脚本自己的 `SPEC` 上（runner 有自己的模块实例）⇒ 首跑 4 臂全假绿。**已原样保留**在 `evidence/mutations/*/run1_driver_bug/`，修正后重跑，结果如上表。

---

## 2. C-2：两处原文被推翻的**自己实测值**（只读，`evidence/c2_measurements.json`）

| # | 我的实测 |
|---|---|
| **1** | `tools/*.py` 共 **24** 文件，正则 `\.db\b`（含 `catalog.db`）＝ **0 命中**；`tools/release_readiness.py:37` ＝ `CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"` ⇒ **封盘 `decision.md:91-92`「`RF/tools/release_readiness.py` the latter（`catalog.db`）」不成立**，clause 6 的「证实实际目标一致」**对 `catalog.db` 这一名称未达成**。全树（排除 `.planning`/`.git`）`catalog.db` 4 命中、**全非产品代码**（2 处 `.review-*` 快照文档 + `assurance/runs/2026-09-11_r4-phase-b/reviews/G5-boundary-observation.json:53` + `audit_review/2026-08-12_zijin_skill_run_audit/progress.md:91`） |
| **2** | `catalog_dir: "<dir>"  # c`（**引号 + 行内注释**）⇒ **rc=3 被拒**，`configured_catalog_dir` **保留字面引号**，顶层 `error=catalog_config_mismatch`；机理 `_strip_scalar`（`iso/slo_probe_patched.py:82-88`）**引号分支先返回**。**本轮新增实测**：`catalog_dir: <dir>  # c`（**裸标量 + 行内注释**）⇒ **rc=2 被接受** ⇒ 能力声明须收窄为「仅裸标量」 |
| **3（读法更正登记）** | 顶层 `error` **恒为** `catalog_config_mismatch`（源 `:522`）；parser 原因在 `binding.error`/`binding.detail`（实测 `config_unreadable_by_probe_parser` + `unresolved variable in catalog_dir: …` / `catalog_dir not found in …`）；「解析成功但目录不符」类的原因在 `binding.configured_catalog_dir`（引号残留）+ `binding.same_directory=false` |
| **4（影响面，不夸大）** | 生产配置 `.review-zr407-20260818/company-wiki/config/source_catalog.yaml:2` ＝ `catalog_dir: "${PROJECT_ROOT}/.source_catalog"`，**不含行内注释**；`.planning` 之外全树仅此一份 `source_catalog.yaml` ⇒ **当前生产不受影响** |

**`D2_resign_pending = true`**：本卡只做更正与证据准备，**不代签 D2**（复签归 SLO/探针 owner）。

---

## 3. 封盘追加的前像 → 后像（`prefix_bytes_preserved`）

| 文件 | 前像（sha256 / 字节） | 追加字节 | 后像（sha256 / 字节） | 前缀保全 |
|---|---|---|---|---|
| `I-14-A/a20260919-01/oracle.md` | `87775f2f4ff025e4d104fd1dfe23d7f7bfc75a20520f8859732133e96ec84bb7` / **20457** | +10799 | `4dc8600f2bbbd40b93585788cd0e6f2b2dc5b2501487e2eeb71377e092b9c204` / **31256** | **true**（前 20457 字节 sha 复算相等；写前内存复算 + 落盘复算各一次） |
| `I-14-A/a20260919-01/decision.md` | `a1a9d37478ffb42f15877ac29b9ecb044b8f402f4d77f532d1a25f1646bfda24` / **8467** | +12078 | `11cf83342484165308445ad085ba4e1f296bb8d7ad08b5afa81feb57e28dc772` / **20545** | **true**（同上） |

`git status --porcelain -- execution_runs/I-14-A` ⇒ **只有 `oracle.md` 与 `decision.md` 两行 M**；`review.md`/`binding.json`/`commands.json`/`handoff.json`/`evidence/**`/`harness/**`/`iso/**` **零改动**。
`review.md` **未追加**（判定：review.md 未重复被推翻的两处原文，其 F-I14A-05 行仍准确 ⇒ 无更正需求）。

---

## 4. 边界（本 attempt **没有做**的事）

1. **未改封盘任何既有字节**（只两处追加，前缀证明见上）；未碰 `I14A-D1-OPS-REVIEW/`（裁定载体只读）。
2. **未写**五份计划文件；**未碰** `RF/tools/`、`tools/` 或任何产品路径（C-2 全程只读）。
3. **未做**任何 git 写操作（仅 `diff`/`status`/`hash` 读命令）；**未联网**。
4. **未代签** D1/D2/D3；**未改**任何 `status`；**未宣布 I-14-A 通过**；**未晋升** `iso/slo_probe_patched.py`。
5. 预算 `BUDGETS` 5/5/5/2 全程只读核对，未改。
6. 结束核对：`git -c core.quotepath=false diff HEAD --name-only` ⇒ **3826 行，非 `.planning` = 0**（ruling 计数为 3824 行，+2 正是本轮追加的 `oracle.md`/`decision.md` 两个文件；另有 2 个非 `.planning` 的 **untracked** 项 `.tmp-r41-mutation/`、`assurance/unified_completion/manifests/plan_inputs.json.bak`，mtime 分别为 2026-09-20 / 2026-09-21，**早于本轮**、非本 attempt 产生）。
7. **两处本会话观察（非本 attempt 所为，如实登记）**：① 五份计划文件中只有 `progress.md` 显示 `M`，其 mtime `2026-09-24T21:03:08Z` **早于本 attempt 首次写入（21:15:46Z）**，且本轮从未写它（我的写入面只有两个 attempt 目录）；② `.planning` 之外的 gitignored 缓存（`.ruff_cache` 有 `21:32:39Z` 的条目）本轮**未由我产生**——我执行的命令清单里没有任何 ruff/lint/formatter 调用；两者都不影响 `git diff HEAD --name-only` 的非 `.planning` 计数（=0）。
8. `execution_runs/I14A-D1-OPS-REVIEW/`（裁定载体）目录内**最新文件时间 = 2026-09-24T20:55:57Z**，早于本 attempt 首次写入 ⇒ **只读未碰**；封盘 `I-14-A/` 内除 `oracle.md`/`decision.md`（21:30:46Z）外**所有文件 mtime 仍为 2026-09-20** ⇒ 未被复跑污染（全部复跑都在本 attempt 自己的复制件上）。
