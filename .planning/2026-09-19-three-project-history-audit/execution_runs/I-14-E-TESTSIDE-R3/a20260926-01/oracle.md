# I-14-E-TESTSIDE-R3 / a20260926-01 — oracle.md（冻结：门 -1 收窄判据 + R2 §3/§4 逐字携带）

**冻结时刻：2026-09-26T18:54Z（UTC）** —— 先于本 attempt 的**任何**门 -1 测量与**任何一次**
pytest 运行（红/绿/变异）（`before/freeze_instant.json` 记录本文件 sha256）。
冻结后只允许**追加式** erratum（`oracle-addendum-*.md`）；上文一字不改。

本文件**不重算任何 expected**：判据权威仍在
`execution_runs/I-14-E-TESTSIDE/a20260924-01/oracle.md`
（sha256 `4c15948e24a2650bf055dddd02b5cc230b561b89de1cf0f34c9a0e293b28f658`）+
`oracle-addendum-A.md`（basetemp 落点）+ `oracle-addendum-C.md`（会话环境阻断与三臂降级）。
本文件 = **R2 oracle（`I-14-E-TESTSIDE-R2/a20260926-01/oracle.md`）§3/§4 的逐字携带** +
**本轮派单给定的门 -1 收窄判据（逐字）** + 本 attempt 的执行口径登记。

---

## 0. 回源（本 attempt 引用的权威，只读）

| 源 | 路径 | 用途 |
|---|---|---|
| R2 oracle | `execution_runs/I-14-E-TESTSIDE-R2/a20260926-01/oracle.md` | §3 施加步骤清单、§4 预注册变异（M1/M2-upper）—— 本文件 §2/§3 逐字携带 |
| R2 handoff | `execution_runs/I-14-E-TESTSIDE-R2/a20260926-01/handoff.json` | `blocked_by_env = ENV-OPENPROCESS-ALLACCESS-DENIED`、`source_catalog_worker.ps1:341` |
| R2 retry_result | `execution_runs/I-14-E-TESTSIDE-R2/a20260926-01/retry_result.json` | 门 -1 四步原始输出（spawn/open/close/wait） |
| 源卡 | `execution_v2/card_I-14-E.md` | 时序抖动归因（负载相关、非树差异）、expected 只许手算 |
| 施加卡 | `execution_v2/card_I-14-E-TESTSIDE.md` | 写入边界、九步、变异证明、不代签 |
| R1 attempt | `execution_runs/I-14-E-TESTSIDE/a20260924-01/` | 冻结判据正文（oracle.md）+ addendum A/C + 复用 harness + iso 副本来源 |

## 1. 门 -1 收窄判据（**本轮派单逐字**，取代上一轮过严口径）

```
旧（过严）：OpenProcess(ALL_ACCESS) 否 ⇒ 全停
新（收窄）：**直接尝试运行三臂 pytest** ——
  a) pytest 能启动、能跑完、能出 rc ⇒ **继续施加**（worker handle 与 pytest 无关）
  b) 仅当**具体步骤**确实被 worker handle / Start-Process 卡住 ⇒ 记录该步骤、其余照跑
  c) 全部步骤被卡 ⇒ 判 `blocked`（合格）
**原始输出全程留档**（每步 rc/耗时/报错）
```

执行含义（不改判据原文，只是把口径钉死，避免事后辩解）：

- 门 -1 的测量动作 = **直接跑三臂 pytest**（红臂第一次运行即门 -1 的实测载体），不再以
  `OpenProcess(ALL_ACCESS)` 探针的成败提前全停；探针输出仅作**记录**（背景证据），不再作闸门。
- (a) 成立的判据：pytest **进程能启动、单次运行能跑完、能给出 rc**（rc 含 1=失败；"出 rc"不等于"绿"）。
- (b) 的"具体步骤"以**单步**为单位登记：哪一步被 worker handle / `Start-Process` 卡住就记哪一步
  （步骤编号 = §2 清单 1–6），其余步骤照跑；被卡步骤的原始报错逐字入 `retry_result.json`。
- (c) 仅当 §2 清单 1–6 **全部**步骤被卡 ⇒ `status=blocked`（合格结果）。
- **原始输出全程留档**：每步 rc / 耗时 / 报错逐字进 `evidence/` 与 `retry_result.json`。

## 2. R2 oracle §3 逐字（施加步骤清单；原文照抄，不重推导）

> ## 3. 施加步骤清单（**携带给下一个有权会话**，不重推导）
>
> 以下步骤在上一轮已冻结（`a20260924-01/oracle.md` §2/§4/§5 + reviewer_report §8 S8-2），
> 本文件**逐字携带要点**、不改变任何判据；下一个会话只需：
>
> 1. **门 -1 自证**（同款探针，判据①或②任一通过即可，本 attempt 用的是双判据更严口径）；
> 2. **SUT 复位**：iso 拷贝自 `a20260924-01/iso`（或重拷真仓），tests 文件必须复位为原始字节
>    sha256 `32515aa60d5fbfbca0778ee68e778ada7ff3bcf238f91930bb621d84aec005c1`（= 真仓
>    `company-wiki/tests/contract/test_source_catalog_worker_bootstrap.py` 现值，本 attempt
>    只读复核仍同值）；启动器 sha `5c12cd740cc36abf95f3b9559485472d9d9a760143d27de46e3aaa7b4bbc311`
>    （本 attempt 只读复核仍同值）；
> 3. **三臂**按冻结 §4：C1=cpu8（8 忙循环）、每臂 N=6、driver 超时 90 s、basetemp
>    `%TEMP%` 内 52–60 字符（addendum-A 口径）、`-p tside_probe` shim 统一生效；
>    - 红（修前，写死 0.5 s）：判据 §3.C——≥1 红（期望 6/6），红形态 = `assert … == 2` /
>      `TimeoutExpired`（**不再是** `launcher_exception`）；
>    - 绿（施加后 `H = min(max(2.0, 4*t0), t0+3)`）：§3.D 四条子判据 + 6/6；
> 4. **红绿双向变异（≥2，见 §4）**；
> 5. 交付 `after/changes.diff`（只含 `tests/**`，逐文件披露）+ `retry_result.json` +
>    `handoff.json`（`status=review_pending`、`implementer_signed=false`、不代签、不晋升）；
> 6. 边界自证：`iso/src`、`iso/scripts`、真仓全部锚点逐字节不变；
>    `git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` = 0。

（注：清单第 1 条"门 -1 自证"的口径在本轮被 §1 的收窄判据**替换为"直接跑三臂 pytest"**；
清单第 2–6 条逐字有效、不改。）

## 3. R2 oracle §4 逐字（预注册变异清单；原文照抄，expected 不重算）

> ## 4. 变异清单（红绿双向，为下一个有权会话预注册）
>
> | 变异 | 改动（唯一被变异元素） | 预注册预期红 | 判别对象 |
> |---|---|---|---|
> | **M1**（冻结 §3.E 原样） | 导出公式退回写死 `0.5`（t0 探针与记录保留） | cpu8 下子进程②寿命 0.642–2.486 s > 0.5 ⇒ 被杀 ⇒ `child_started ≥ 3` ⇒ `assert … == 2` 红 | **下界**：H 必须盖住启动带宽上尾 |
> | **M2-upper**（本文件新预注册） | 语义上界钳制 `t0 + 3.0` → `t0 + 10.0`（其余一字不改） | H ≥ t0+10 > t0+5 ⇒ 子进程①（count 落盘后睡 5 s 自净退）先于看门狗退出 ⇒ 事件缺 `child_unresponsive` ⇒ `next()` 抛 `StopIteration` ⇒ 红（墙钟 ≈ t0+5+ε < 15 s） | **上界**：钳制是节点语义必需（oracle §2.3），去掉必红 |
>
> - 两个变异**各自只动一个元素**，把绿判据从两侧夹住：M1 证"太小必红"、M2-upper 证"太大必红"、
>   绿证"公式本身恰好不红"。
> - 派单"变异 ≥2"由 M1 + M2-upper 满足；冻结 §3.E 的可选 M2（`H=2.0` 只留地板）仍**不纳入**
>   （概率性、无判别力，原文理由不变）。

## 4. 本 attempt 执行口径（登记，不改任何判据）

1. **落点**：一切自有产物写在本 attempt 目录
   `execution_runs/I-14-E-TESTSIDE-R3/a20260926-01/`。iso 为 R1 `a20260924-01/iso` 的字节副本；
   复用 harness（`run_band.py`/`load.py`/`tside_probe.py`/`apply_fix.py`/`make_diff.py`/`hashes.py`）
   逐字复制进本 attempt `harness/`，仅允许改**非判据性**标识（attempt 名、输出载荷 attempt 字段、
   临时工作根名）；判据性代码（公式、锚点、shim 语义、run 协议）一字不改。
2. **解释器**：venv 由 R1 `a20260924-01/venv` 字节副本而来（python 3.13.9 / pytest 9.1.1），
   落在本 attempt `venv/`，不写任何旧 attempt 目录。
3. **臂与 N**（冻结 §4 原样）：红 N=6（修前 0.5 s）、绿 N=6（`H = min(max(2.0, 4*t0), t0+3)`）、
   变异 M1 N=6、变异 M2-upper N=6（M2-upper 按 R2 §4 预注册同形运行；派单"各 1 条"=
   两条预注册变异各作为 1 条变异定义执行，运行计数按冻结 N=6 全量记录）。
   条件 C1=cpu8（8 忙循环）、driver 超时 90 s（超时计红、不重跑掩盖）、逐次全新 basetemp、
   `-p tside_probe` shim、stripped env 同冻结 §4。**每臂给 pytest rc + 通过/失败计数**。
4. **basetemp/工作根**：addendum-A 口径（`%TEMP%` 内 52–60 字符、`within-budget` 不迁移）。
   本 attempt 用**全新**工作根 `%TEMP%\i14ets-r3`（不触碰 R1 的 `i14ets`/`i14ets-b` 及其
   既存不可删目录）。偏差照 addendum-A §A3 如实登记：这两处 scratch 在 `.planning` 外、
   由被测测试框架创建/删除，源卡 M-B 同形。
5. **变异实现**（唯一被变异元素，锚点替换失败即大声报错，不许静默）：
   - M1：绿版公式处替换为写死 `0.5`（t0 探针与 `_record_timing_trace` 保留）；
   - M2-upper：`_exported_hang_timeout` 的上界钳制 `t0_seconds + 3.0` → `t0_seconds + 10.0`
     （其余一字不改，含地板 2.0 与系数 4）。
6. **记录**：每步 rc/耗时/报错原始输出入 `evidence/`（逐字）；每臂 `band-*.json` + `captures/`；
   施加前后逐字节自证（`before/hashed_before.json` → `after/hashed_after.json`）；
   `changes.diff` 只含 `tests/**`。

## 5. 交付与纪律（原卡 + 派单，逐条硬性）

1. 产出四件：`oracle.md`（本文件）· `three_arms_result.json` · `retry_result.json` · `handoff.json`
   （`status`、`gate1_scoped_verdict`、`implementer_signed=false`、`releases_nothing=true`、
   `written_files`、`git_diff_non_planning=0`）。
2. **不产生 `ACCEPT`**（独立复审另派）· **不代签** · **不放行参数** · **不解除任何无关项** ·
   **不写五份计划文件**。
3. **产品仓只读**：`company-wiki`（真仓）与 `iso/src`、`iso/scripts` 零写入；施加只发生在
   iso 的 `tests/**` 副本上，以 `after/changes.diff` 交付（应用属晋升，另授权）。
   若发现施加必须写产品仓 ⇒ 停、报 `blocked`（父可代行落点）。
4. **禁 git 写**、**禁 `git status`**（只允许只读 `rev-parse`/`diff --name-only`）· **禁联网**。
5. `git -c core.quotepath=false diff HEAD --name-only` 非 `.planning` **= 0**（结束前自证）。
6. expected 不得由重跑生成；缺证据写"未证实"，**不造绿色样例**。
