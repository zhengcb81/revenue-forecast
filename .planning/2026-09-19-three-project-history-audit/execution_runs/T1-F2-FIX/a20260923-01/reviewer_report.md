# T1-F2-FIX 独立复审报告（reviewer · a20260923-01）

卡：**T1-F2-FIX** / attempt `a20260923-01`。
角色：独立复审工位（与实现者非同一人）。**本文件只写复审结论，不写卡状态、不落定、不晋升、不改任何修法。**
日期：2026-09-24（本地）。裁决：见文末 `VERDICT`。

---

## 0. 范围与裁权边界

**在范围内**（逐条按派单 1–12 复算）：冻结序、三处修复最小性、必须翻转/必须不变两清单、缺键≠畸形语义、变异证明有效性、家族/棘轮数字、仪器勘误、环境披露、外部 pin 振荡披露、自删披露、边界、发现分级。

**明确不在本复审裁权内**：
- **F-3（畸形时间戳 rc 归属）不重新裁**。只核两件事：①本卡是否**保持 pending-routed 而未自填**；②PT-1/PT-2 是否仍 rc=4 记录、未被改判。F-3 裁决正文载体按派单指向 `T1-10-FIX/a20260923-01/reviewer_report.md` §7.3，我只核其存在性与指纹，不读其裁决内容作二次裁断。
- **不裁任何 status、不落定、不晋升、不改 F-1/F-2/P4 的修法**。
- 不联网、不改产品树、不碰 `.planning` 之外任何文件。

---

## 1. 方法

1. **只读生产树**；全部重跑放在**我自己的 %TEMP% 隔离副本**：
   `C:\Users\郑曾波\AppData\Local\Temp\dsh-GxKdpE\rev_t1f2\2026-09-19-three-project-history-audit\`
   （副本结构 = 计划目录骨架 + 本 attempt 的 `oracle.md / binding.json / changes.diff / diff_stats.json / decision.md / handoff.json / evidence / scripts / worktree / worktree_before` + `T1-10-FIX/.../changes.diff`；**不含** `_pytest_tmp*`）。原 attempt 除本报告两个新建文件外**零写入**。
2. 用本卡自带 `scripts/verify_t1_f2_fix.py` 的全部子命令（`pins/probe/suites/inherit/reports/mutation/nc/invariants`）+ `scripts/mutation_semantic_arms.py` + 冻结 runner `harness/mutate.r2.py` 在副本内重跑；所有输出落 `review_scratch/`，**不写副本内既有 evidence**。
3. 独立复算（不采信自述）：changes.diff 重建、difflib 改动行号、T1-10-FIX diff 新侧行区、哈希、pin 表逐行重算、R-* 词表正则重算、evidence mtime 序、pre-run `.pyc` 反汇编。
4. `invariants --out` 指向 %TEMP%，因此该子命令是在**真实 attempt 上只读执行**（只读 evidence/pin/worktree，唯一写入 = 我的 temp 输出）。
5. 运行时：`I-14-B/a20260919-01/iso/venv/Scripts/python.exe`（Python 3.13.9），只读复用，`-X utf8 -B -p no:cacheprovider`。

---

## 2. 冻结序（派单要求 1）

| 项 | 我的实测 |
|---|---|
| `oracle.md` sha256 | `ea63701c288fdc890cd985b077dce37c4a53aebd438e1548add9d047714f30ce`（31224 B）= binding 记录 = handoff 记录 = pin 表行 → **三方一致，一字未改** |
| `oracle.md` mtime | 2026-09-24 **06:30:23**（本地） |
| `evidence/**` 文件数 | **923** |
| `evidence/**` 中 mtime **早于** oracle 的文件数 | **0** |
| 最早的 evidence 文件 | `evidence/pin_hashes.sha256.tsv`，**06:43:09**（= binding 所称「pins --write 先于 phase=before」） |
| 首次解释执行 verify 脚本 | `scripts/__pycache__/verify_t1_f2_fix.cpython-313.pyc` mtime **06:41:34**，pyc 头内嵌源 size = **62921**（交付版 66790 B）→ 首跑 06:41:34 > oracle 06:30:23，且佐证脚本在首跑后确被改过（与勘误披露一致） |
| 顺序结论 | **oracle(06:30) → 首次编译/执行(06:41) → pins(06:43) → 首次 before 相位(自述 06:44)** —— 冻结先于运行，成立 |

`binding.json` 自身 sha `836fbd099b6bc5c917ab420bba19e0681c48d465c8a237ac8b74985673a2bddf`（11178 B）= handoff 登记值 ✓。

**pin 表独立复算**（`evidence/pin_hashes.sha256.tsv`，sha `135d71dc3dbdb673f79cb82e745100a956427190a54645c4222050b3d780945b`，36 行 = 28 attempt-internal + 8 external）：
- attempt-internal **28/28 匹配，0 失配**；
- external **7/8 匹配、1 失配**（见 F-3 外部漂移）。
→ 表本身**未被回写**（sha 与 handoff/decision 登记值相同）。

---

## 3. 三处修复的最小性（派单要求 2）

### 3.1 changes.diff 自算

- 20153 B / sha `bc87bf81bc53aad17f5c2f1047db467c64a92ec0b431499d94a438e8cbd3f3ca`（= 自述）；**+415 −2**（我逐行计数 = 415/2，一致）；**2 个文件**；生成器 `scripts/make_diff.py` = **difflib、无 git**（读码确认，sha `12b30d4a…` 与登记一致）。
- hunk 旧/新区间（我按 `@@` 头 + 块体逐行核，old_blk/new_blk 与 header count 全部断言通过）：

| # | 旧侧行区间 | 新侧行区间 | 归属 |
|---|---|---|---|
| 1 | **53–59**（7 行） | 53–66（14 行） | F-1，被替换的只有**旧 56** |
| 2 | **357–363**（7 行） | 364–382（19 行） | F-2，被替换的只有**旧 360** |
| 3 | **439–444**（6 行） | 458–479（22 行） | P4，**首尾原样、纯插入** |
| 4 | `/dev/null` 0–0 | 1–378 | 新增测试文件 |

- **把 diff 应用到 baseline `064e5381…` → 得到的文本与 `worktree/i14b/iso/natural_window.py`（`9b1ebda2…`）逐字节相同 = True**；新增测试文件也**逐字节重建成功**（16333 B）。
- difflib 重算本卡改动的**旧侧行号 = `{56, 360}`**；P4 为插入式（旧 441/442 之间）。

### 3.2 「守卫行一字未动 / J11 一字未动 / 缺键不动」

| 断言 | 我的实测 |
|---|---|
| J7 守卫行未动 | `    if clock_source not in TRUSTED_CLOCKS:  # J7` 在 **baseline 行 355**、fixed 亦恰 **1 次**；355 ∉ 改动集 {56,360} → **一字未动** |
| J11 守卫行未动 | `    if claim_status == "complete" and computed_status != "complete":  # J11` 在 **行 361**，恰 **1 次**；361 ∉ {56,360} → **一字未动** |
| 被改的定义行 | 旧 **56** = `TRUSTED_CLOCKS = {...}` → `("system_utc","scheduler_trusted")`；`TRUSTED_CLOCKS = (` 恰 1 次、`sorted(TRUSTED_CLOCKS)` 恰 1 次 |
| J16 守卫/`BASIS_REGISTRY` | `BASIS_REGISTRY = (` 恰 1 次（前置层，未回退）；J16 守卫恰 1 次 |
| 缺键不动（P4） | 逐行读 diff：`for _key in ("windows","sampled_at"): if _key in fields …`、`if "ledger" in fields:` —— **三处都有 `in fields` 前置**，缺键完全不进归一分支；13 条稳定行实测全等（§4） |

> **转录勘误（不计发现）**：派单转述的自述写的是「**BASIS_REGISTRY** 定义行 56 set→tuple」。**本卡行 56 改的是 `TRUSTED_CLOCKS`**；`BASIS_REGISTRY` 是 T1-10-FIX 的前置层（其 diff 新侧行 60–74），本卡未触碰。实现者自己的 `decision.md §3.1` / `handoff.json` 写的是 `TRUSTED_CLOCKS`，**正确**——该误写来自转述层，不是本卡文件。

### 3.3 与前置/第三层的不交性（我自己算，不照抄）

我解析 **T1-10-FIX changes.diff（sha `625ecfe4…`）** 自算其在 fixed iso 上的**新侧触及行** = **57–77 与 204–220**（其 `@@` 旧侧为 57–69、196–203；自述引用的 `60–74`/`207–217` 是其中**新增块**的子区，二者均被我的实测覆盖）。

| 排除区（fixed iso 行号） | 我算出的来源 | 与本卡 `{56,360}`（及插入点 441/442）交集 |
|---|---|---|
| T1-10 新增块 60–74 / 207–217（全触及 57–77 / 204–220） | T1-10-FIX diff 自算 | **∅**（56<57、360>220） |
| defect-2 **182–205** | 我读 fixed iso 行 182–205 = `J1/J3/P2` 注释 + intervals 推导 + `R-SAMPLE-OUTSIDE/R-NO-SAMPLES/R-NO-INTERVAL/R-QC-IN-OBS/R-FUTURE-CLOCK` 拒绝块（与 `inherit_probe` 的 174–197 为**同一区间的两种行号系**：T1-10 净 +8 行，174+8=182、197+8=205，**自洽**） | **∅** |
| `_parse` **82–88** | 我读 fixed iso 行 82–88 = `def _parse(ts: str) … return dt.astimezone(...)`（标签正确） | **∅** |
| 本卡自身域 {50–59, 354–364, 439–446} | — | **{56,360} ⊆ 该域 = True** |

**不交性成立（我自算）**。第三腿 T1-F3-FIX 的 `changes.diff` **尚不存在**（见 §12 未证实）。

---

## 4. 必须翻转 / 必须不变两清单（派单要求 3）

**在 %TEMP% 隔离副本内用本卡 verify 脚本自跑**：`probe --phase before` rc=0、**66 checks / 0 failed / PASS**；`probe --phase after` rc=0、**73 checks / 0 failed / PASS**。我重跑的 `checks[].name` 与 recorded evidence 完全一致，仅 `stdout_head/traceback/detail` 内的**绝对路径**不同（隔离副本路径 vs 原路径）——差分条目 before 30 / after 58，**逐条都是路径串**，无一条是 rc/verdict/refusals 判据。

### 4.1 必须翻转（14 个崩溃形态；数据取自 recorded evidence，与我重跑判据一致）

| 探针 | before（rc / verdict / refusals / report / decided） | after |
|---|---|---|
| K1 | 4 / — / — / False / 0 | 0 / reject / `[R-SIMULATED-CLOCK]` / True / 1 |
| K2 | 4 / — / — / False / 0 | 0 / reject / `[R-SIMULATED-CLOCK]` |
| K3 | 4 / — / — / False / 0 | 0 / reject / `[R-SIMULATED-CLOCK]` |
| S1 | 4 / — / — / False / 0 | 0 / reject / `[R-CLAIM-EXCEEDS]` |
| S2 | 4 / — / — / False / 0 | 0 / reject / `[R-CLAIM-EXCEEDS, R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-SAME-INSTANT]` |
| S3 | 4 / — / — / False / 0 | 0 / reject / `[R-CLAIM-EXCEEDS]` |
| S4 | 4 / — / — / False / 0 | 0 / reject / `[R-CLAIM-EXCEEDS]` |
| S5 | 4 / — / — / False / 0 | 0 / reject / `[R-CLAIM-EXCEEDS]` |
| S6 | 4 / — / — / False / 0 | 0 / **accept** / `[]` |
| P4-W1 | 4 / — / — / False / 0 | 0 / accept / `[]` |
| P4-W2★ | 4 / — / — / False / 0 | 0 / reject / `[R-CLAIM-EXCEEDS]` |
| P4-S1★ | 4 / — / — / False / 0 | 0 / reject / `[R-NO-SAMPLES]` |
| P4-L1★ | 4 / — / — / False / 0 | 0 / reject / `[R-CLAIM-EXCEEDS]` |
| P4-L2 | 4 / — / — / False / 0 | 0 / accept / `[]` |

批/臂（我重跑的 green_batch 判据全 PASS）：J1 rc0 5/5 rej{BAD-F1,BAD-F2}；J1b 同；J2 rc0 5/5 rej{P4-W2,P4-S1,P4-L1}；J3 rc0 8/8 rej{5 BAD}；ArmA rc0 7/7 rej{BAD-F1}；ArmC rej{BAD-F1,BAD-F2}；ArmD rej{P4-S1}；ArmB 对照 rc0 7/7 仅 BAD-STR-CONTRAST 被拒。

### 4.2 必须不变（13 行）

`K4 K5 K6 K7 K8 S7a S7b S7c S8 S9 S10 P4-STAB-W P4-STAB-S` —— 我按 `(rc, verdict, refusals, report_written, cases_decided)` 逐行比对 before/after：**13/13 `equal=True`，mismatch 清单为空**（具体值：K4 accept[]；K5–K8 reject[R-SIMULATED-CLOCK]；S7a/b/c accept[]；S8 reject[R-EMPTY-EVIDENCE,R-FUTURE-CLOCK,R-SAME-INSTANT]；S9 reject[四码]；S10 accept[]；P4-STAB-W/S accept[]）。ArmB 批行亦相等。

### 4.3 pending-routed（不判）

`PT-1` before rc4 → **after rc4**；`PT-2` before rc4 → **after rc4**（verdict/refusals 均空、report 未写出）。**未被本卡改判、未自填** ✓。继承的 T1-10 探针 adjacent 三行：before `rc4/rc4/rc4` → after **`rc0/rc0/rc4`**（末位 `malformed_timestamp_schema` 仍 rc4）——我在副本内重跑 `inherit` 得到**完全相同**的三行。

---

## 5. 缺键≠畸形（派单要求 4，本卡核心语义）

after 相位实测（recorded + 我重跑判据一致）：

| 探针 | claim 形态 | after verdict | after refusals | 含 `R-CLAIM-EXCEEDS` |
|---|---|---|---|---|
| **S2** | 畸形载体（list）+ C1 攻击事实 | reject | `[R-CLAIM-EXCEEDS, R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-SAME-INSTANT]` | **是** |
| **S7a** | 缺键 / `claim={}` + C2 事实 | **accept** | `[]` | 否 |
| **S7b** | 缺键 | **accept** | `[]` | 否 |
| **S7c** | 缺键 | **accept** | `[]` | 否 |
| **S8** | `claim={}` + **同一 C1 攻击事实** | **reject** | `[R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-SAME-INSTANT]` | **否** |
| S9 | 正常载体 + C1 | reject | 四码 | 是 |
| S10 | 正常载体（真有 status） | accept | `[]` | 否 |

⇒ **S2 与 S8 在同一 C1 事实下以 `R-CLAIM-EXCEEDS` 的有无成对可判**：present-but-malformed → 结构化拒；真缺键 → 不多出该码且行字节不变。**父裁判据成立，我自测确认。**

**MUT-SEM-2 真的能打红这条判据** —— 我在副本内自跑 `scripts/mutation_semantic_arms.py`：
- 结果 sha `6dd122885a6bae7e…` 与 recorded **逐字节相同**，`PASS / 21 checks / 0 failed`。
- 读其毒化源码：`if not isinstance(claim, dict):` → `if not isinstance(claim, dict) or "status" not in claim:`，锚点断言 `count==1`；判据为 `S7a/S7c 必须 accept`、`S8 必须 reject 且不含 R-CLAIM-EXCEEDS` 三条 STABLE **在变异体上必须翻红**，且 `S10`（真有 status 键）**必须保持**。
- 实测：MUT-SEM-2 三条 STABLE 全红 + S10 不动 = 4/4 PASS；MUT-SEM-1（`{"status":"complete"}` → `{"status":"pending"}`）使 S1/S2/S3 三条冻结 GREEN 全红 = 3/3 PASS；control 7 条 + NC-MISSING 7 条 = 21/21。
- **NC-MISSING**：`K7, S7a, S7b, S7c, S8, S9, S10` **7/7 `equal=True`**（我另用 §4.2 的独立比对交叉验证同 7 行）。

---

## 6. 变异证明有效性（派单要求 5）

在副本内自跑 `verify mutation --sut <fixed> --baseline <pristine>`：**PASS / 12 checks / 0 failed**，输出 `mutation_results.json` 与 recorded **sha 逐字节相同**（`cb6ed2a213f528bb…`）。逐条：

| 臂 | 实测（我重跑） |
|---|---|
| **MUT-F1**（tuple→set） | K1/K2/K3 崩溃回归 → PASS（非空洞） |
| **MUT-F2**（守卫块→原单行） | S1/S3 崩溃回归 → PASS |
| **MUT-P4**（入口归一移除） | P4-W2 / P4-S1 / P4-L1 三形状崩溃回归 → PASS |
| **MUT-A1** | MUT-7 / MUT-11 / MUT-15 / MUT-16 / `sorted_TRUSTED` 五锚在 fixed==baseline 各恰 1 次且文本相同 → PASS |
| **MUT-A2** | `TRUSTED_clocks` tuple 形态恰 1、`BASIS_REGISTRY = (` 在 fixed **与 baseline** 都恰 1（前置层未回退）、fix 块恰 1、baseline 仍是 set 形态 → PASS |

**不是「碰巧通过」的证据**：每个回退臂都要求**崩溃形态真的回来**（rc=4/无报告/0 裁决），锚臂要求**文本级相等**；三臂的失败即 check 变红，我重跑得到的是全绿且**字节等同**于落盘件。

**20 臂机关（MUT-A3）**：我在副本内重跑 `harness/mutate.r2.py` 两轮 —— before（SUT `064e5381…`）与 after（SUT `9b1ebda2…`）各 `mutation_count=20 / all_mutants_red_again=true / all_expected_cases_red=true / load_bearing=20`；**逐臂 `cases_red` 我的重跑 == recorded（0 差异）**，且 before==after（`MUT-7→C5`、`MUT-15→X1,X2,X3,X4`、`MUT-11→C1,C4,C6,C7,X12,X13,X14`）。

**双向负控**：副本内自跑 `nc` → `PASS / 6 checks / 0 failed`，check 名与 holds 序列与 recorded **完全相同**：PC rc0/ok/mismatch0；NC-1 SUT rc0 34/34 而 runner rc1/ok=false/{C3,C2} + sha 通道失配；NC-2 runner rc1/ok=false/≥4 行含 {C5,C4}、**从不 rc0**。

---

## 7. 家族/棘轮数字（派单要求 6）

**我重跑（副本内 `suites` 两相位 + `reports` 两相位）**：

| 面 | before（我的实测） | after（我的实测） | 与自述 |
|---|---|---|---|
| r1 族套件 | **32 passed / 0 failed** | **32 / 0** | 一致 |
| r2 族套件 | **18 / 0** | **18 / 0** | 一致 |
| T1-10 23 测试 | **23 / 0** | **23 / 0** | 一致 |
| **本卡新 29 测试** | **13 passed / 16 failed** | **29 / 0** | 一致 |
| T1-10 探针 | **39/39 PASS**，adjacent rc4/rc4/rc4 | **39/39 PASS**，adjacent **rc0/rc0/rc4** | 一致 |
| r2 冻结门 | rc0、ok、mismatch0、**34/34**、`sut_report` `beb06495…` | **同 sha `beb06495…`**、34/34 | 一致 |
| r1 门（既有 superseded） | rc1、mismatch1=`W1`、`sut_report` `6fa04855…` | **字段全等**、同 sha `6fa04855…` | 一致（既有态，不判绿） |

**棘轮 18==frozen**：`frozen_expectations.r2.json` sha `a24d8ab3444dd1c7…`（pin 行）、`cases.r2.json` sha `23d89fb27bbdb599…`（pin 行），r2 门期望/输入均未动且 34/34 绿 ✓。

**「与冻结预测逐值相同」是否真有冻结预测 —— 我做了独立取证**：
- `oracle.md` §8 只冻结 r1/r2/23/39/r2门/20臂，**没有**新 29 测试的数字行；`binding.json` 也不 pin 新测试文件 → 表面上找不到冻结预测。
- 但 `scripts/__pycache__/verify_t1_f2_fix.cpython-313.pyc`（**mtime 06:41:34，早于首跑**，内嵌源 size 62921 B）中我**反汇编出首跑版 `cmd_invariants` 的该 check**，字节码为：
  `nb.get('failed',0) >= 16` → `nb.get('passed',0) == 13` → `na.get('failed') == 0`（常量池含 `16,13,29`），check 名即 `"(>=16 failed: …) and fully green post-fix (29 passed)"`。
- ⇒ **冻结预测 before=13/≥16、after=29/0 确实先于任何运行存在**；我的重跑 = **13/16 → 29/0**，**逐值命中**。该取证是**实现者自述之外**的独立来源，反证其「互证」说法成立。

**词表零新码（我自己算）**：对 baseline 与 fixed SUT 源跑同一正则 `"(R-[A-Z0-9-]+)"` → 两边**同为 16 个码**（`R-ANCHOR-NOT-SHARED, R-BASIS-UNKNOWN, R-CLAIM-EXCEEDS, R-DUP-RUN-ID, R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-LABEL-ANCHOR, R-NO-INTERVAL, R-NO-SAMPLES, R-POSTHOC-CAPTURE, R-QC-IN-OBS, R-SAME-INSTANT, R-SAMPLE-OUTSIDE, R-SIMULATED-CLOCK, R-SUM-OVERLAP, R-TOTAL-AS-OBS`），**集合相等、无 `R-TIMESTAMP-*`** ✓。

**invariants**：在**真实 attempt 上**执行 `invariants --out %TEMP%` → **PASS / 37 checks / 0 failed**（唯一写入在我 temp）✓。

---

## 8. 仪器勘误三处（派单要求 7）

**oracle 期望是否真的未被改**：`oracle.md` sha `ea63701c…` = binding = handoff = **pin 表内 attempt-internal 行**（28/28 全匹配，含 `oracle.md`、两树 `oracle.md`、`frozen_expectations*.json`、`cases*.json`、三套既有测试）→ **冻结期望一字未改，成立**（这是 pin 门证明的，不是自述证明的）。

**三处勘误是否对准冻结文本（我读 oracle 原文核）**：
- **I1 `_batch(n=6→7)`**：oracle §A.2 Arm-D 冻结为「**6× W1-GOOD + 1× P4-S1**」；交付脚本 L282/283/286 三处 `_batch(..., 7, 3, ...)`（armA/armB/armD），并在 L279 留有 `first draft of _batch(n=6, replace-at-3) built only 6` 注记 → **勘误如实留档，且方向 = 对准 oracle** ✓。
- **I2 `sampled_at range(0,30,2)→range(0,30)`**：oracle §A.2 `P4-STAB-S` 冻结为「`sampled_at` **正常 30 串**」；交付 L71 = `range(0, 30)` = 30 串 ✓。
- **I3 `P4-STAB-W` 改用 cases.r2 的 W5 夹具**：oracle §A.2 `P4-STAB-W` 冻结为「**W5 形：union 2400**」；交付 L232/L237 按 `P4-STAB-W`/`P4-STAB-S` 分支取夹具 ✓（新测试文件里同样引用 `BY_ID["W5"]`/`BY_ID["W1"]`，见 changes.diff L380–383）。
- **勘误披露**：`decision.md §8` 有 **I1–I6 六行表**（含「是否动了期望」列全为「否」）+ verify 脚本 sha `b903a9f6…` → `a464f67d…` 的变更说明；`handoff.json.instrument_corrections.policy/items` 同样 6 条 → **如实留档** ✓。
- **「新 29 测试恰好落到冻结预测」互证成立**（见 §7 的 pyc 反汇编）✓。

---

## 9. 环境披露（派单要求 8）

- `scripts/pytest_tmp_acl_plugin.py`（sha `e96890fe…` = 登记值）**我逐行读过**：只把 `pathlib.Path.mkdir` / `os.mkdir` 收到的 `mode & 0o777 == 0o700` 替换成 `0o777`，**不读不写任何断言/夹具/测试/SUT 字节**，且只由 `cmd_suites` 以 `-p pytest_tmp_acl_plugin` 加载（PYTHONPATH = 本 attempt `scripts/`），SUT 与冻结 harness 不导入它 → **「只改权限」成立**。
- **我独立复现了该环境**：在 %TEMP% 内 `os.mkdir(p, 0o700)` 后 `os.listdir(p)` 抛 `PermissionError [WinError 5] 拒绝访问`，`os.rmdir` 同样抛错，`chmod 0o777` 后仍 WinError 5 → 沙箱 mode→ACL 映射异常**真实存在**。
- `_pytest_tmp` **3 个不可删空目录如实留存**：`before_suite_basis23`、`before_suite_container29`、`mode_test_700`（我递归枚举 `_pytest_tmp` 得到 `Access denied` 于这三个目录，与自述一致）；`_pytest_tmp2` 4 个目录可正常枚举（15 条递归项）→ 「根换代」披露与盘面一致。
- **附带披露**：我这次复现也留下一个不可删的 %TEMP% 目录 `C:\Users\郑曾波\AppData\Local\Temp\dsh-GxKdpE\rev_acl_probe_700`（**在 %TEMP% 内、不在仓内**，为该 ACL 本身所致）。

---

## 10. 外部 pin 振荡披露（派单要求 9 —— 属好实践，予以确认）

| 核点 | 我的实测 |
|---|---|
| pin 表是否被回写 | **否**。`evidence/pin_hashes.sha256.tsv` sha `135d71dc3dbdb673f79cb82e745100a956427190a54645c4222050b3d780945b`（36 行），与 handoff/decision 登记值相同 |
| `pins --check` 0 失配 | **attempt_internal = 0 失配（28/28）**（我逐行重算，非采信）；副本内跑 `pins --mode check` 亦 `ok:true, attempt_internal_mismatches:[]` |
| 披露是否完整 | `decision.md §9` 三时点表（06:43 `f3f4dd2b…`/7708B → 21:15:08 `bffebc01…`/22194B → 21:26:25 回 `f3f4dd2b…`）+ `handoff.json.external_pin_drift`（同三时点、`written_by_this_card:false`、`handling:绝不回写`）+ `evidence/boundary_check.json`（mtime **21:30:54**，早于 handoff 21:31:15，`external_carrier_drift:[]`）→ **时点、双 sha、mtime、触发者、影响面俱全，且方向是「披露而非回写」——确认为好实践** |
| 中间态可核性 | `bffebc01…`（21:15:08）与 21:26:25 的复位**属历史瞬态，我无法重测**（见 §12） |

**新观察（复审窗口内出现的第三次外部漂移）**：`T1-10-FIX/a20260923-01/handoff.json` 现为 **26509 B / sha `e6b9a94a40313b9ad600ba09011b64dfebb7d683b0b590fc4e2f78c10269433e` / mtime 2026-09-24 21:37:01**（本卡 handoff 落盘 21:31:15 **之后**）。因此**此刻** `pins --check` 的 `external_carrier_drift` 长度为 **1**（attempt_internal 仍 0）。该漂移**晚于本卡窗口、非本卡产生**，本卡当窗披露不受影响；记为 F-3。

---

## 11. 自删披露（派单要求 10）

- `recovery/` **现存 = 空目录**（递归 0 条目），与 `handoff.changed_paths` 第 13 条「recovery/ (空目录，误删后同轮原样重建)」及 `decision.md §11-附注` **一致**。
- 交叉参照：同族 `T1-10-FIX/a20260923-01/recovery` 也是 0 条目（`I-14-H` 同样 0）→「attempt 根 `recovery/` 为空」在本仓是常态形态，**原样重建说辞与盘面不矛盾**。
- 「除该处外零删除」：我核 `handoff.changed_paths` 列出的 13 个路径**全部在盘**、attempt 顶层 7 个目录（evidence/recovery/scripts/worktree/worktree_before/_pytest_tmp/_pytest_tmp2）齐全，未发现缺失件；**但本 attempt 没有 `commands.json`**（不同于 T1-10-FIX），也没有独立删除日志 → 该断言只能**部分证实**（见 §12）。

---

## 12. 边界声明（派单要求 11）

| 核点 | 我的实测 |
|---|---|
| `git -c core.quotepath=false diff HEAD --name-only` | 复审开始时 **3821 行**、结束时 **3824 行**，两次**非 `.planning` = 0**（我把 stdout/stderr 分流后统计，避免 CRLF 警告混入）。+3 是复审期间**其他并行批次**改的 `.planning` 内文件：`I-00-A/a20260919-01/handoff.json`、`I-00-A/a20260919-01/review.md`、`PROMOTION-PREP/a20260922-01/handoff.json`（集合差分实测，**非本复审所写**） |
| changes.diff 是否被 apply（零生产合并） | `iso/natural_window.py` **不在工作树**（untracked/absent），且非 `.planning` diff = 0 → **未合入** ✓ |
| 词表零新码 | 16 == 16，集合相等 ✓（§7） |
| PT-1/PT-2 pending-routed | rc4 → rc4，未入 PASS/FAIL、未自填 ✓（§4.3） |
| 合并序 | T1-10-FIX `625ecfe45f3d713a08b5873c6cb3df258c25279d4c5bf3f4e25295cd441199ac`（我实测）→ 本卡 `bc87bf81bc53aad1…`（我实测）→ T1-F3-FIX **（尚无 changes.diff）** |
| 我用过的 git 命令 | 仅 `git -c core.quotepath=false diff HEAD --name-only`（2 次）、`git log -1`（1 次，HEAD 仍为 `b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb` / 2026-09-23 19:51，**复审期间零提交**）；**未使用 `git status`**；**未执行任何 add/commit/checkout/stash/restore/reset**；**未联网** |

---

## 13. 发现表

**P1（阻断）：0 条。**

| # | 级别 | 发现 | 证据 |
|---|---|---|---|
| F-1 | **P3** | I5 环境事故的**引用指针失效**：插件 docstring 与 `decision.md §8 I5` 把首跑证据指向 `evidence/before/suites/*.stderr.txt`，但该目录 4 个 `*.stderr.txt` **全部 0 字节**，且 `evidence/**` 全树 **grep 不到 `PermissionError` / `WinError 5` / `cleanup_dead_symlinks`** 任何一处。**实质仍成立**（我在 %TEMP% 独立复现 WinError 5；`_pytest_tmp` 三个不可枚举目录是盘面佐证），只是**被引证据件不存在** → 指针需更正 | 我的 grep + 复现（§9） |
| F-2 | **P3** | 「首跑 09-24 06:44 before 相位判 FAIL（I1–I3）」**无任何留存件**：923 个 evidence 文件中 **922 个 mtime 落在 21:03–21:2x**（唯一早者是 06:43:09 的 pin 表），首跑观测与首跑仪器源文件均被覆盖（pyc 头显示首跑版源 size 62921 B，交付版 66790 B，源已不存）。**披露文本在、观测不可复核** → 记「未证实」，非造假证据 | evidence mtime 分布 + pyc 头（§2、§8） |
| F-3 | **P3** | 外部载体**第三次漂移发生在本卡窗口之外**：`T1-10-FIX/.../handoff.json` 现为 `e6b9a94a…` / 26509 B / mtime 21:37:01，**不在**本卡 §9 的三时点表内（其时点表到 21:26:25 为止）。本卡当窗披露准确、pin 表未回写；但**今天再跑 `pins --check` 会得 external_drift=1**，父方若以「0 失配」复核需注明读数时刻 | 我逐行 pin 复算（§2、§10） |
| F-4 | **P3** | **范围外遗留（不构成本卡违约，交父方决定是否跟进）**：dict claim 内 `status` 为**非字符串**（如 `{"status": ["complete"]}`）时按「非 complete」读入 —— 我实测 C2(pending 事实) → `accept []`（无 `R-CLAIM-EXCEEDS`），C1 → `reject [R-EMPTY-EVIDENCE,R-FUTURE-CLOCK,R-SAME-INSTANT]`（时钟类检查**未被绕过**、**不崩溃**）。该形态**不在本卡 oracle §3 冻结面内**（§3/§3.2 冻结的是「载体真值非字典」），J11 行又受「一字未动」约束 → 属**既有未变行为**，本卡既未承诺也未触及 | 我的额外直调探针（见下） |

> F-4 实测原文（我自跑，fixed SUT `9b1ebda2…`）：
> ```
> C2+claim{status:[complete]}  -> accept_claim []
> C2+claim{status:{x:1}}       -> accept_claim []
> C2+claim{status:True}        -> accept_claim []
> C2+claim{}                   -> accept_claim []
> C1+claim{status:[complete]}  -> reject_claim ['R-EMPTY-EVIDENCE','R-FUTURE-CLOCK','R-SAME-INSTANT']
> ```

**P2：0 条。** 所有派单 1–11 的核点上，我没有测到任何与实现者自述**相冲突**的数值、哈希或 rc。

---

## 14. 未证实 / 不在我的复核面内

1. **首跑 06:44 FAIL 观测**（无留存件，见 F-2）；同理 I4 修正前的 `before 12/17 / after 28/1` 也无留存件。
2. **binding 记录的 pre-run verify 脚本 sha `b903a9f6…`**：源文件已不存在，无法直接验 sha；仅 pyc 头 `size=62921 / mtime 06:41:34` 佐证「首跑时确为另一版本」。
3. **外部 pin 两个中间态**（`bffebc01…` @21:15:08 与 21:26:25 的复位值）—— 历史瞬态，我只能核 pin 时点值（`f3f4dd2b…`）与**当前值**（`e6b9a94a…`）。
4. **合并序第三腿 T1-F3-FIX**：该卡 `changes.diff` 尚不存在，第三腿仅为声明；`_parse 82-88` 的「不交」我按**本卡改动集**核过为 ∅，但无法与其实际 diff 对撞。
5. **「除 recovery/ 外零删除」**：只能证伪不能证真（本 attempt 无 `commands.json`、无独立删除日志）；我核到的是「handoff 所列 13 路径全在、顶层 7 目录齐全」。
6. **登记册盘上回执**：handoff 已自列为移交项，运行期间未见落册 —— 与我观察一致（未见新回执件）。
7. **r1 门 rc=1 / W1 mismatch**：我复跑 before/after **字段全等**，但按 oracle 口径它是既有 superseded 态，**其绿度我不判**。
8. **`defect-2 {182-205}` 的上游出处**：我核了它的**内容语义**（quick_check/J15/J6 拒绝块）与**行号自洽**（= r2 基线 174–197 + 8），但未找到产生该区间的原始缺陷卡文件。
9. **F-3 裁决内容**：按裁权边界**我不读判、不复述**，只核本卡保持 pending-routed（已核）。

---

## 15. 结论

- 14 个崩溃形态 rc4→rc0、13 条稳定行 before==after 全等、PT-1/PT-2 维持 rc4 未自填、66/66 → 73/73、invariants 37/37、12+21+6 三组变异/负控判定、20 臂两树全红且逐臂相等、四套件 32/18/23/13→29、39 探针 adjacent rc4/rc4/rc4→rc0/rc0/rc4、r2 门 34/34 同 sha、词表 16==16 —— **全部由我在 %TEMP% 隔离副本内独立重跑或独立复算得到，与自述一致**。
- 冻结先于运行、oracle 一字未改、changes.diff 可逆重建且行不交、pin 表未回写、勘误对准冻结文本 —— **均以哈希/字节级证据成立**。
- 4 条发现全部为 **P3**（证据指针/留存件/窗口外漂移/范围外遗留），**无 P1、无 P2**，且均不改变「三处修复正确、判据承重、边界干净」的结论。

**VERDICT: ACCEPT**

---

### 附：我做了什么、没做什么

**做了**：只读解析；%TEMP% 隔离副本内重跑 `pins --mode check / probe×2 / suites×2 / inherit×2 / reports×2 / mutation / nc / invariants`（invariants 的 `--out` 指向 %TEMP%，故在真实 attempt 上是只读执行）、`mutation_semantic_arms.py`、`harness/mutate.r2.py`×2；changes.diff 与 T1-10-FIX diff 的独立重建/行区自算；pin 表 36 行逐行重算；R-* 词表正则重算；oracle/evidence mtime 序统计；pre-run `.pyc` 反汇编；0o700 ACL 独立复现；`git ... diff HEAD --name-only` 边界取证。

**没做**：**未创建/修改 `handoff.json`**；**未改任何 status**；**未改本 attempt 任何既有字节**（oracle/binding/decision/handoff/changes.diff/diff_stats/evidence/scripts/worktree 全只读）；**未 git add/commit/checkout/stash/restore/reset**；**未用 `git status`**；**未联网**；**未改产品树**；**未裁 F-3、未落定、未晋升、未改 F-1/F-2/P4 修法**。写入面 = 本文件 + `reviewer_report.sha256` 两个新建文件。结束时非 `.planning` diff = **0**。
