# T1-F2-FIX / a20260923-01 - carrier landing（簿记转录）

> **本文件由 carrier-landing 簿记 pass 创建；创建前本 attempt 无 `review.md`。**
> 落定前本 attempt 顶层文件清单 = `binding.json` / `changes.diff` / `decision.md` / `diff_stats.json` / `handoff.json` / `oracle.md` / `reviewer_report.md` / `reviewer_report.sha256`（`Test-Path .../review.md` = false）。
> 本文件**只转录**独立复审 `reviewer_report.md` 的裁决与实测，**自身不授予任何东西、不添加任何验收、不产生新裁决**。签署面 = `reviewer_report.md`；**落账是簿记转录，不是实现者自签**（`verdict_is_transcribed_not_authored = true`、`implementer_signed = false`）。

---

## 0. VERDICT BLOCK（裁决转录）

- **verdict** = **`ACCEPT`** —— 原文 `**VERDICT: ACCEPT**`，逐字转录自 carrier 第 **304** 行。
- **计数** = **P1 = 0 / P2 = 0 / P3 = 4**（carrier §13 发现表）；`**P1（阻断）：0 条。**`、`**P2：0 条。**`
- **4 条发现全部为 P3，均不改变结论**（carrier §15 末条逐字）：「4 条发现全部为 **P3**（证据指针/留存件/窗口外漂移/范围外遗留），**无 P1、无 P2**，且均不改变「三处修复正确、判据承重、边界干净」的结论。」
- **carrier** = `reviewer_report.md`（attempt 内相对路径 `execution_runs/T1-F2-FIX/a20260923-01/reviewer_report.md`）
- **carrier sha256** = `baa60fc402988a5f6d02f13e29343a21fc6849faba11c06a6c8096ba10cdcce9` —— **30308 B / 312 行**，落定时只读独立复算 == 侧车 `reviewer_report.sha256`（**85 B**，其自身 sha `aae00884ec35b0d5a3664e5cec0001c1694021687e4007dad1085f2008d615fa`）读回 == 派单 pin。编码 **UTF-8 无 BOM**（首 3 字节 `35 32 84` = `# T`）、**LF-only（CR 计数 = 0）**、单尾 LF。
- 侧车内容 = `baa60fc402988a5f6d02f13e29343a21fc6849faba11c06a6c8096ba10cdcce9  reviewer_report.md` —— **读回相等**。本 pass 对 carrier 与 sidecar 写入 **0 字节**。
- **reviewer / N=1** = 独立复审工位（与实现者非同一人；carrier L3-L5）；方法边界 = 只读生产树 + 全部重跑放自己的 %TEMP% 隔离副本、原 attempt 除报告两个新建文件外零写入、不联网、不改产品树（carrier §0 / §1 / 附录）。
- **nature of this file** = bookkeeping transcription：**不自签**（`implementer_signed = false`）、**裁决是转录不是创作**（`verdict_is_transcribed_not_authored = true`）、不裁 F-3、不晋升、不改 F-1/F-2/P4 修法。

**裁决/发现/未证实的位置**（1-based 行、两端包含；byte proof = 对 `carrier_sha256` 态文件的 0-based 字节偏移，区域含末行行尾 LF）：

| 区域 | 行 | bytes（含尾 LF） | len | sha256 |
|---|---|---|---|---|
| 报告头（L1-L8，含角色/日期/裁决指针） | L1-L8 | 0..339 | 340 | `307f7913b99f7b0ae91fac60a82853076f10f42f26bfef93e589c9d819db9ac3` |
| §2 冻结序 | L32-L51 | 2565..4078 | 1514 | `a352e31f89342916f49cb82e19877742b710883b25b5b1618e841db4821a64e3` |
| §3 三处修复最小性 + 转录勘误 | L53-L93 | 4080..7995 | 3916 | `70ae361a1955f10efb466058aa34b5f362be81787a53492fefdd8f782cc15c1a` |
| §4 必须翻转 / 必须不变 | L97-L128 | 8002..10918 | 2917 | `ed4d9699faef029b2de73fee44af19b2faa5a324d3b04a486368bb09bc91177f` |
| §5 缺键≠畸形 | L132-L152 | 10925..12838 | 1914 | `d4dde8d71699fa84ea5528bf472b9f17c6506e9c36202e365fd2fc4cf8e30986` |
| §7 家族/棘轮数字 | L176-L200 | 14692..17257 | 2566 | `b416a3ec620663908a9065f499ffddce93b74c4c89669f0911a1f85e934ef767` |
| §10 外部 pin 振荡披露 | L226-L237 | 20151..21765 | 1615 | `8473b346a04f96d1c6fcebbf3410694b5b7fa1bc2f5e93f2588389abef852ab4` |
| §12 边界声明 | L247-L258 | 22611..23996 | 1386 | `204fd6d6daa937f50707459ab697ce5d76e52730028d3708f51ef492a1e4e579` |
| **§13 发现表（P3 四条来源）** | L260-L280 | 23998..26722 | 2725 | `47c3ac2d81e2471c519b5f0972f30b439cb6c27234cef12b36ab69f2df39e07d` |
| **§14 未证实（9 条来源）** | L284-L294 | 26729..28347 | 1619 | `b1d96eff2c06b9b306ad0801be0992d76f5c3c096c3ca641fedf23f65dff7fe0` |
| **§15 结论（含 VERDICT 行）** | L298-L304 | 28354..29194 | 841 | `0f35db315893c521e487c3229dbc1451319b05a3d430ecb24523d5c28923cec8` |
| **裁决行 `**VERDICT: ACCEPT**`** | L304-L304 | 29175..29194 | 20 | `f378376c192f6d3c42293c19d1591d6c647057e540667a9ae417294e65b36eeb` |
| └ 同行去尾 LF（纯文本 19 B） | L304-L304 | 29175..29193 | 19 | `5bfe2716576b1c3e7fba4d04058bd2ac1a7a0e2378340a526ce7ad7562df721a` |

---

## 1. 四条 P3 逐条（逐字转录，不得弱化；**4 条均不改变结论**）

### P3-1（carrier §13 表 F-1 行，L266）—— I5 环境事故的引用指针失效

> I5 环境事故的**引用指针失效**：插件 docstring 与 `decision.md §8 I5` 把首跑证据指向 `evidence/before/suites/*.stderr.txt`，但该目录 4 个 `*.stderr.txt` **全部 0 字节**，且 `evidence/**` 全树 **grep 不到 `PermissionError` / `WinError 5` / `cleanup_dead_symlinks`** 任何一处。**实质仍成立**（我在 %TEMP% 独立复现 WinError 5；`_pytest_tmp` 三个不可枚举目录是盘面佐证），只是**被引证据件不存在** → 指针需更正

- 证据栏（carrier 原文）：「我的 grep + 复现（§9）」
- 派单同条的补充细节（一并携带、不弱化）：**复审者已独立复现成功**（%TEMP% 内 `os.mkdir(p, 0o700)` → `os.listdir`/`os.rmdir` 均 `PermissionError [WinError 5]`，`chmod 0o777` 后仍 WinError 5）⇒ **需更正指针，不否定披露**。
- 是否阻断：**否**（P3，不改变 ACCEPT 结论）。
- 处置：**原样转录**；指针更正属证据面修订，本 pass 不改任何既有 evidence。

### P3-2（carrier §13 表 F-2 行，L267）—— 「首跑 before 判 FAIL」无留存件

> 「首跑 09-24 06:44 before 相位判 FAIL（I1–I3）」**无任何留存件**：923 个 evidence 文件中 **922 个 mtime 落在 21:03–21:2x**（唯一早者是 06:43:09 的 pin 表），首跑观测与首跑仪器源文件均被覆盖（pyc 头显示首跑版源 size 62921 B，交付版 66790 B，源已不存）。**披露文本在、观测不可复核** → 记「未证实」，非造假证据

- 证据栏：「evidence mtime 分布 + pyc 头（§2、§8）」
- 是否阻断：**否**。
- 处置：**原样转录**；与 §14 第 1、2 条同源，见 §5。

### P3-3（carrier §13 表 F-3 行，L268）—— 外部载体第三次漂移（本卡窗口外）

> 外部载体**第三次漂移发生在本卡窗口之外**：`T1-10-FIX/.../handoff.json` 现为 `e6b9a94a…` / 26509 B / mtime 21:37:01，**不在**本卡 §9 的三时点表内（其时点表到 21:26:25 为止）。本卡当窗披露准确、pin 表未回写；但**今天再跑 `pins --check` 会得 external_drift=1**，父方若以「0 失配」复核需注明读数时刻

- 证据栏：「我逐行 pin 复算（§2、§10）」
- 派单同条的补充口径（一并携带、不弱化）：此刻 `pins --check` 的 `external_drift=1`、**attempt_internal 仍 0**；**本卡当窗三时点披露准确、pin 表未回写 = 好实践**；以「0 失配」复核时**必须注明读数时刻**。
- 是否阻断：**否**（漂移晚于本卡窗口、非本卡产生）。
- 处置：**原样转录**；本 pass 不回写 `evidence/pin_hashes.sha256.tsv`（36 行、sha `135d71dc3dbdb673f79cb82e745100a956427190a54645c4222050b3d780945b`，仍未改）。
- 落定时刻复核（本 pass 只读再测，供读数时刻标注）：`T1-10-FIX/a20260923-01/handoff.json` = **26509 B / `e6b9a94a40313b9ad600ba09011b64dfebb7d683b0b590fc4e2f78c10269433e` / mtime 2026-09-24 21:37:01** —— 与 carrier 所记一致，本 pass 未测到第四次漂移。

### P3-4（carrier §13 表 F-4 行，L269）—— 范围外遗留，不构成本卡违约

> **范围外遗留（不构成本卡违约，交父方决定是否跟进）**：dict claim 内 `status` 为**非字符串**（如 `{"status": ["complete"]}`）时按「非 complete」读入 —— 我实测 C2(pending 事实) → `accept []`（无 `R-CLAIM-EXCEEDS`），C1 → `reject [R-EMPTY-EVIDENCE,R-FUTURE-CLOCK,R-SAME-INSTANT]`（时钟类检查**未被绕过**、**不崩溃**）。该形态**不在本卡 oracle §3 冻结面内**（§3/§3.2 冻结的是「载体真值非字典」），J11 行又受「一字未动」约束 → 属**既有未变行为**，本卡既未承诺也未触及

- 复审者实测原文（carrier §13 引文块 L271-L278，fixed SUT `9b1ebda2…`）：

```
C2+claim{status:[complete]}  -> accept_claim []
C2+claim{status:{x:1}}       -> accept_claim []
C2+claim{status:True}        -> accept_claim []
C2+claim{}                   -> accept_claim []
C1+claim{status:[complete]}  -> reject_claim ['R-EMPTY-EVIDENCE','R-FUTURE-CLOCK','R-SAME-INSTANT']
```

- 是否阻断：**否**。
- 处置：**只原样转录，不做任何处置**（复审者未裁；是否登记跟进 = 父方决定）。

---

## 2. 复审者实测 rc 清单（逐条抄录，一个数字都不改）

### 2.1 probe 两相位

| 相位 | 实测 |
|---|---|
| `probe --phase before` | **rc=0**、**66 checks / 0 failed / PASS** |
| `probe --phase after` | **rc=0**、**73 checks / 0 failed / PASS** |

（复审者在 %TEMP% 隔离副本重跑；`checks[].name` 与 recorded evidence 完全一致，差分条目 before 30 / after 58 **逐条都是绝对路径串**，无一条是 rc/verdict/refusals 判据。）

### 2.2 套件 / 继承 / 门

| 面 | before | after |
|---|---|---|
| r1 族套件 | **32 passed / 0 failed** | **32 / 0** |
| r2 族套件 | **18 / 0** | **18 / 0** |
| T1-10 23 测试（basis23） | **23 / 0** | **23 / 0** |
| 本卡新 29 测试（container29） | **13 passed / 16 failed** | **29 / 0** |
| T1-10 探针（inherit） | **39/39 PASS**，adjacent `rc4/rc4/rc4` | **39/39 PASS**，adjacent **`rc0/rc0/rc4`** |
| r2 冻结门（reports） | rc0、ok、mismatch0、**34/34**、`sut_report` `beb06495…` | **同 sha `beb06495…`**、34/34 |
| r1 门（既有 superseded） | rc1、mismatch1=`W1`、`sut_report` `6fa04855…` | **字段全等**、同 sha `6fa04855…`（既有态，不判绿） |

> **adjacent 末位仍 `rc4` = F-3 pending**（`malformed_timestamp_schema` 未被本卡改判）。

### 2.3 变异 / 负控 / 不变量

| 面 | 实测 |
|---|---|
| `mutation` | **PASS / 12 checks / 0 failed**；输出 `mutation_results.json` 与 recorded **sha 逐字节相同** = `cb6ed2a213f528bb…` |
| `mutation_semantic_arms` | **PASS / 21 checks / 0 failed**；结果 sha `6dd122885a6bae7e…` 与 recorded **逐字节相同** |
| └ MUT-SEM-1（fail-closed→静默） | `{"status":"complete"}` → `{"status":"pending"}` ⇒ S1/S2/S3 三条冻结 GREEN **全红 = 3/3 PASS** |
| └ MUT-SEM-2（缺键也当畸形） | `if not isinstance(claim, dict):` → `… or "status" not in claim:`（锚点断言 count==1）⇒ S7a/S7c 必须 accept、S8 必须 reject 且不含 `R-CLAIM-EXCEEDS` **三条 STABLE 全红** + **S10 不动** = **4/4 PASS** |
| └ control + NC-MISSING | control 7 条 + **NC-MISSING 7 条**（`K7, S7a, S7b, S7c, S8, S9, S10` **7/7 `equal=True`**）= 21/21 |
| `nc`（双向负控） | **PASS / 6 checks / 0 failed**；check 名与 holds 序列与 recorded 完全相同：PC rc0/ok/mismatch0；NC-1 SUT rc0 **34/34** 而 runner rc1/ok=false/{C3,C2} + sha 通道失配；NC-2 runner rc1/ok=false/≥4 行含 {C5,C4}、**从不 rc0** |
| `mutate.r2` 20 臂（两树） | before（SUT `064e5381…`）与 after（SUT `9b1ebda2…`）各 **`mutation_count=20` / `all_mutants_red_again=true` / `all_expected_cases_red=true` / `load_bearing=20`**；逐臂 `cases_red` 复跑 == recorded（0 差异），且 before==after（`MUT-7→C5`、`MUT-15→X1,X2,X3,X4`、`MUT-11→C1,C4,C6,C7,X12,X13,X14`） |
| `invariants` | 在**真实 attempt 上**只读执行（`--out` 指向 %TEMP%）→ **PASS / 37 checks / 0 failed** |
| 棘轮 | `frozen_expectations.r2.json` sha `a24d8ab3444dd1c7…`、`cases.r2.json` sha `23d89fb27bbdb599…`（pin 行），r2 门期望/输入均未动且 34/34 绿 |

### 2.4 必须翻转：**14 个崩溃形态全 rc4 → rc0，且拒码逐条命中**

| 探针 | before（rc / verdict / refusals / report / decided） | after（rc / verdict / refusals / report / decided） |
|---|---|---|
| K1 | 4 / — / — / False / 0 | **0 / reject / `[R-SIMULATED-CLOCK]` / True / 1** |
| K2 | 4 / — / — / False / 0 | **0 / reject / `[R-SIMULATED-CLOCK]`** |
| K3 | 4 / — / — / False / 0 | **0 / reject / `[R-SIMULATED-CLOCK]`** |
| S1 | 4 / — / — / False / 0 | **0 / reject / `[R-CLAIM-EXCEEDS]`** |
| S2 | 4 / — / — / False / 0 | **0 / reject / `[R-CLAIM-EXCEEDS, R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-SAME-INSTANT]`** |
| S3 | 4 / — / — / False / 0 | **0 / reject / `[R-CLAIM-EXCEEDS]`** |
| S4 | 4 / — / — / False / 0 | **0 / reject / `[R-CLAIM-EXCEEDS]`** |
| S5 | 4 / — / — / False / 0 | **0 / reject / `[R-CLAIM-EXCEEDS]`** |
| S6 | 4 / — / — / False / 0 | **0 / accept / `[]`** |
| P4-W1 | 4 / — / — / False / 0 | **0 / accept / `[]`** |
| P4-W2★ | 4 / — / — / False / 0 | **0 / reject / `[R-CLAIM-EXCEEDS]`** |
| P4-S1★ | 4 / — / — / False / 0 | **0 / reject / `[R-NO-SAMPLES]`** |
| P4-L1★ | 4 / — / — / False / 0 | **0 / reject / `[R-CLAIM-EXCEEDS]`** |
| P4-L2 | 4 / — / — / False / 0 | **0 / accept / `[]`** |

批/臂（复审者重跑的 green_batch 判据全 PASS）：J1 rc0 **5/5** rej{BAD-F1,BAD-F2}；J1b 同；J2 rc0 **5/5** rej{P4-W2,P4-S1,P4-L1}；J3 rc0 **8/8** rej{5 BAD}；ArmA rc0 **7/7** rej{BAD-F1}；ArmC rej{BAD-F1,BAD-F2}；ArmD rej{P4-S1}；ArmB 对照 rc0 **7/7** 仅 BAD-STR-CONTRAST 被拒。

### 2.5 必须不变：**13 行 13/13 `equal=True`**

`K4 K5 K6 K7 K8 S7a S7b S7c S8 S9 S10 P4-STAB-W P4-STAB-S` —— 按 `(rc, verdict, refusals, report_written, cases_decided)` 逐行比对 before/after：**13/13 `equal=True`，mismatch 清单为空**。

具体值：K4 `accept[]`；K5–K8 `reject[R-SIMULATED-CLOCK]`；S7a/S7b/S7c `accept[]`；S8 `reject[R-EMPTY-EVIDENCE,R-FUTURE-CLOCK,R-SAME-INSTANT]`；S9 `reject[四码]`；S10 `accept[]`；P4-STAB-W / P4-STAB-S `accept[]`。**ArmB 批行亦相等。**

### 2.6 pending-routed：**PT-1 / PT-2 rc4 → rc4，未自填**

- `PT-1` before **rc4** → after **rc4**；`PT-2` before **rc4** → after **rc4**（verdict/refusals 均空、report 未写出）—— **未被本卡改判、未自填** ✓。
- 继承的 T1-10 探针 adjacent 三行：before `rc4/rc4/rc4` → after **`rc0/rc0/rc4`**，**末位 `malformed_timestamp_schema` 仍 rc4 = F-3 pending**；复审者副本内重跑 `inherit` 得到**完全相同**的三行。

### 2.7 缺键 ≠ 畸形（本卡核心语义，after 相位）

| 探针 | claim 形态 | after verdict | after refusals | 含 `R-CLAIM-EXCEEDS` |
|---|---|---|---|---|
| **S2** | 畸形载体（list）+ C1 攻击事实 | reject | `[R-CLAIM-EXCEEDS, R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-SAME-INSTANT]` | **是 ✓** |
| **S7a** | 缺键 / `claim={}` + C2 事实 | **accept** | `[]` | 否 |
| **S7b** | 缺键 | **accept** | `[]` | 否 |
| **S7c** | 缺键 | **accept** | `[]` | 否 |
| **S8** | `claim={}` + **同一 C1 攻击事实** | **reject** | `[R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-SAME-INSTANT]` | **否 ✓（不含）** |
| S9 | 正常载体 + C1 | reject | 四码 | 是 |
| S10 | 正常载体（真有 status） | accept | `[]` | 否 |

⇒ **S2 与 S8 在同一 C1 事实下以 `R-CLAIM-EXCEEDS` 的有无成对可判**：present-but-malformed → 结构化拒；真缺键 → 不多出该码且行字节不变。父裁判据成立，复审者自测确认。

---

## 3. 独立取证两处（复审者自算，**非采信自述**）

### 3.1 冻结序（carrier §2）

| 项 | 实测 |
|---|---|
| `oracle.md` sha256 | `ea63701c288fdc890cd985b077dce37c4a53aebd438e1548add9d047714f30ce`（**31224 B**）= binding 记录 = handoff 记录 = pin 表行 → **三方一致，一字未改** |
| `oracle.md` mtime | 2026-09-24 **06:30:23**（本地） |
| `evidence/**` 文件数 | **923** |
| `evidence/**` 中 mtime **早于** oracle 的文件数 | **0** |
| 最早的 evidence 文件 | `evidence/pin_hashes.sha256.tsv`，**06:43:09** |
| 首次解释执行 verify 脚本 | `scripts/__pycache__/verify_t1_f2_fix.cpython-313.pyc` mtime **06:41:34**、pyc 头内嵌源 size = **62921 B**（交付版 66790 B） |
| 顺序结论 | **oracle(06:30) → 首次编译/执行(06:41) → pins(06:43) → 首次 before 相位(自述 06:44)** —— **冻结先于运行，成立** |

> 注：本落定 pass 新建 `evidence/T1-F2-FIX/qualification.json` 后，evidence 文件数在**落定时刻**由 923 变为 924；上表 923 = **复审取证时点**的读数，转录不改。

### 3.2 「冻结预测 13/16 → 29/0 先于运行存在」的独立来源（carrier §7）

- `oracle.md` §8 只冻结 r1/r2/23/39/r2门/20 臂，**没有**新 29 测试的数字行；`binding.json` 也不 pin 新测试文件 ⇒ 表面找不到冻结预测。
- **独立来源** = 复审者在**首跑前**落下的 `scripts/__pycache__/verify_t1_f2_fix.cpython-313.pyc`（**mtime 06:41:34，早于首跑**，内嵌源 size **62921 B**），在其中**反汇编出首跑版 `cmd_invariants` 的该 check**，字节码为：
  `nb.get('failed',0) >= 16` → `nb.get('passed',0) == 13` → `na.get('failed') == 0`（常量池含 **16 / 13 / 29**），check 名即 `"(>=16 failed: …) and fully green post-fix (29 passed)"`。
- ⇒ **互证成立**：冻结预测 before=13/≥16、after=29/0 **确实先于任何运行存在**；复审者重跑 = **13/16 → 29/0**，逐值命中。该取证在**实现者自述之外**。

---

## 4. diff 独立复算（复审者自算）

- `changes.diff` = **20153 B** / sha **`bc87bf81bc53aad17f5c2f1047db467c64a92ec0b431499d94a438e8cbd3f3ca`**；**+415 −2**（逐行计数 415/2）；**2 个文件**；生成器 `scripts/make_diff.py` = **difflib、无 git**（sha `12b30d4a…` 与登记一致）。
- **把 diff 应用到 baseline `064e5381…` → 得到的文本与 `worktree/i14b/iso/natural_window.py`（`9b1ebda2…`）逐字节相同 = True**；新增测试文件亦**逐字节重建成功**（16333 B）。
- **difflib 改动旧侧行 = `{56, 360}`**（P4 为插入式，旧 441/442 之间）⇒ **J7 守卫 @ 旧侧行 355**（`    if clock_source not in TRUSTED_CLOCKS:  # J7`，baseline 与 fixed 各恰 1 次）**、J11 守卫 @ 旧侧行 361**（`    if claim_status == "complete" and computed_status != "complete":  # J11`，恰 1 次）—— `355 ∉ {56,360}`、`361 ∉ {56,360}` ⇒ **一字未动**。
  - 本 pass 只读复测（不改字节）：baseline `064e5381…`（21416 B）行 56 = `TRUSTED_CLOCKS = {"system_utc", "scheduler_trusted"}`、行 68 = `BASIS_REGISTRY = (`、行 355 = J7 守卫、行 361 = J11 守卫；fixed `9b1ebda2…`（23534 B）J7 守卫 @362、J11 守卫 @380（= 旧侧行 + 位移，内容不变）。
- hunk 表（old / new / 归属）：

| # | 旧侧行区间 | 新侧行区间 | 归属 |
|---|---|---|---|
| 1 | **53–59**（7 行） | 53–66（14 行） | F-1，被替换的只有**旧 56** |
| 2 | **357–363**（7 行） | 364–382（19 行） | F-2，被替换的只有**旧 360** |
| 3 | **439–444**（6 行） | 458–479（22 行） | P4，**首尾原样、纯插入** |
| 4 | `/dev/null` 0–0 | 1–378 | 新增测试文件 |

- **P4 为 441/442 间纯插入，且三处归一都有 `in fields` 前置**（`for _key in ("windows","sampled_at"): if _key in fields …`、`if "ledger" in fields:`）⇒ **缺键完全不进归一分支 = 缺键不动**；13 条稳定行实测全等（§2.5）。
- **与前置/第三层不交性（复审者自算）**：T1-10-FIX diff（sha `625ecfe4…`）在 fixed iso 上新侧触及行 = **57–77 与 204–220**（新增块 60–74 / 207–217 是其子区）；defect-2 = **182–205**（= r2 基线 174–197 + 8，自洽）；`_parse` = **82–88**。与本卡 `{56, 360}`（及插入点 441/442）交集 **全部 ∅** ⇒ **不交性成立（复审者自算，非照抄）**。
- **BASIS_REGISTRY**：`BASIS_REGISTRY = (` 恰 1 次（前置层，**未回退**）、J16 守卫恰 1 次；本卡未触碰该定义（见 §7 勘误）。
- 第三腿 T1-F3-FIX 的 `changes.diff` **尚不存在**（见 §5 第 4 条）。

---

## 5. 词表（复审者正则自算）

对 baseline 与 fixed SUT 源跑同一正则 `"(R-[A-Z0-9-]+)"` → **两边同为 16 个码、集合相等、无 `R-TIMESTAMP-*`** ✓：

`R-ANCHOR-NOT-SHARED, R-BASIS-UNKNOWN, R-CLAIM-EXCEEDS, R-DUP-RUN-ID, R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-LABEL-ANCHOR, R-NO-INTERVAL, R-NO-SAMPLES, R-POSTHOC-CAPTURE, R-QC-IN-OBS, R-SAME-INSTANT, R-SAMPLE-OUTSIDE, R-SIMULATED-CLOCK, R-SUM-OVERLAP, R-TOTAL-AS-OBS`

---

## 6. 未验证项（carrier §14 逐条转录）+ 边界声明

### 6.1 §14 未证实 / 不在复核面内（9 条，逐条）

1. **首跑 06:44 FAIL 观测**（无留存件，见 F-2）；同理 I4 修正前的 `before 12/17 / after 28/1` 也无留存件。
2. **binding 记录的 pre-run verify 脚本 sha `b903a9f6…`**：源文件已不存在，无法直接验 sha；仅 pyc 头 `size=62921 / mtime 06:41:34` 佐证「首跑时确为另一版本」。
3. **外部 pin 两个中间态**（`bffebc01…` @21:15:08 与 21:26:25 的复位值）—— 历史瞬态，复审者只能核 pin 时点值（`f3f4dd2b…`）与**当前值**（`e6b9a94a…`）。
4. **合并序第三腿 T1-F3-FIX**：该卡 `changes.diff` 尚不存在，第三腿仅为声明；`_parse 82-88` 的「不交」按**本卡改动集**核过为 ∅，但无法与其实际 diff 对撞。
5. **「除 recovery/ 外零删除」**：只能证伪不能证真（本 attempt 无 `commands.json`、无独立删除日志）；复审核到的是「handoff 所列 13 路径全在、顶层 7 目录齐全」。
6. **登记册盘上回执**：handoff 已自列为移交项，运行期间未见落册 —— 与复审观察一致（未见新回执件）。
7. **r1 门 rc=1 / W1 mismatch**：复审复跑 before/after **字段全等**，但按 oracle 口径它是既有 superseded 态，**其绿度不判**。
8. **`defect-2 {182-205}` 的上游出处**：复审核了它的**内容语义**（quick_check/J15/J6 拒绝块）与**行号自洽**（= r2 基线 174–197 + 8），但未找到产生该区间的原始缺陷卡文件。
9. **F-3 裁决内容**：按裁权边界**复审不读判、不复述**，只核本卡保持 pending-routed（已核）。

### 6.2 边界声明（carrier §12）

| 核点 | 实测 |
|---|---|
| `git -c core.quotepath=false diff HEAD --name-only` | 复审开始时 **3821 行**、结束时 **3824 行**，两次**非 `.planning` = 0**（+3 为并行批次改的 `.planning` 内文件，非本复审所写） |
| changes.diff 是否被 apply（零生产合并） | `iso/natural_window.py` **不在工作树**，且非 `.planning` diff = 0 → **未合入** ✓ |
| 词表零新码 | 16 == 16，集合相等 ✓ |
| PT-1/PT-2 pending-routed | rc4 → rc4，未入 PASS/FAIL、未自填 ✓ |
| 合并序 | T1-10-FIX `625ecfe45f3d713a08b5873c6cb3df258c25279d4c5bf3f4e25295cd441199ac` → 本卡 `bc87bf81bc53aad1…` → T1-F3-FIX **（尚无 changes.diff）** |
| 复审用过的 git 命令 | 仅 `git diff HEAD --name-only`（2 次）、`git log -1`（1 次，HEAD 仍 `b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb`，**复审期间零提交**）；未用 `git status`；**未执行任何 add/commit/checkout/stash/restore/reset**；**未联网** |

**本落定 pass 的边界（自测）**：落定前 `git -c core.quotepath=false diff HEAD --name-only` = **3824 行、非 `.planning` = 0**；HEAD = `b7a6a1167beeac6975fa9f8fe130bdd2136ecbcb`。写入面 = 本 attempt 目录内 3 个文件（见 §8）。结束时复测。

---

## 7. 父派单转录勘误（只在本新建 `review.md` 写，**不改任何既有文件的既有字节**）

**父派单转录层的错误（本卡不受影响，如实入册）**：

- 父派单里写「**F-1 = `BASIS_REGISTRY` 定义行 56 `set→tuple`」。
- **实际**：`changes.diff` hunk 1 中被替换的**行 56 是 `TRUSTED_CLOCKS = {"system_utc", "scheduler_trusted"}` → `("system_utc", "scheduler_trusted")`**（set → tuple）。carrier §3.2 原文：「被改的定义行 | 旧 **56** = `TRUSTED_CLOCKS = {...}` → `("system_utc","scheduler_trusted")`」。
- **`BASIS_REGISTRY` 属 T1-10 前置层**（baseline `064e5381…` 行 68 = `BASIS_REGISTRY = (`，落在 T1-10 新增块 **60–74** 内），**本卡未碰**；carrier §3.2 原文：「`BASIS_REGISTRY = (` 恰 1 次（前置层，未回退）」。
- **实现者自己的 `decision.md` §3.1（L45）写的是 `TRUSTED_CLOCKS`，是对的**：「**F-1（J7）**：`TRUSTED_CLOCKS` 由 set 改 **tuple**（定义行 56）」；`handoff.json` 亦按 `TRUSTED_CLOCKS` 登记（`mutation_arms.oracle_sec6.MUT-A1/A2` 含 `sorted(TRUSTED_CLOCKS)`）。
- ⇒ **错在父的转录层，不在本卡任何文件**。本卡 `oracle.md` / `binding.json` / `decision.md` / `handoff.json` / `changes.diff` 与复审报告**均无需更正**；本 pass **不改任何既有文件的既有字节**，只在本新建 `review.md` 留此勘误。

> 同一勘误在 carrier §3.2 亦以「**转录勘误（不计发现）**」形式留档：「派单转述的自述写的是「**BASIS_REGISTRY** 定义行 56 set→tuple」。**本卡行 56 改的是 `TRUSTED_CLOCKS`**；`BASIS_REGISTRY` 是 T1-10-FIX 的前置层（其 diff 新侧行 60–74），本卡未触碰。实现者自己的 `decision.md §3.1` / `handoff.json` 写的是 `TRUSTED_CLOCKS`，**正确** —— 该误写来自转述层，不是本卡文件。」

---

## 8. Bookkeeping（本 pass 的写入面与自证）

### 8.1 写入清单（写入面 = 本 attempt 目录，越界写入 = 0）

| 文件 | 改前 sha256 / 字节 | 改后 sha256 / 字节 | 动作 |
|---|---|---|---|
| `review.md` | （不存在；`Test-Path` = false） | 见交付回执 | **新建**（本节声明：由 carrier-landing 簿记 pass 创建，创建前本 attempt 无 `review.md`） |
| `handoff.json` | `2d7cf62d36332cab5c3672c25455b8105d14007e6802077299b6ea69a2a40304` / **23422 B**（mtime 2026-09-24 21:31:15） | 见交付回执 | `status` `review_pending → accepted_scoped` + 追加 `status_before` / `status_authority` / `status_history` / `reviewer_status` / `carried_findings` / `unverified`(=§14) / `f3_state` / `merge_order` / `verdict_is_transcribed_not_authored` / `bookkeeping`；改后 JSON 重解析 |
| `evidence/T1-F2-FIX/qualification.json` | （不存在；本卡原无任何 qualification 文件） | 见交付回执 | **新建**（目录 `evidence/T1-F2-FIX/` 一并新建） |
| `reviewer_report.md` / `reviewer_report.sha256` | `baa60fc4…cdcce9` / 30308 B；`aae00884…15fa` / 85 B | **同左，0 字节** | 只读复核 |
| 既有 carrier（`oracle.md` / `changes.diff` / `decision.md` / `binding.json` / `diff_stats.json` / `evidence/**` 既有件 / `scripts/**` / `worktree*/**`） | 见 `handoff.json.sha256` | **同左，0 字节** | 只读复核 |
| 五份计划文件（`REMEDIATION_REGISTER.md` / `progress.md` / `findings.md` / `task_plan.md` / `OWNER_DECISIONS.md`） | — | — | **本 pass 写入 = 0**（父折入） |

### 8.2 三资格与不自签

- `formula` = **`not_applicable_with_reason`**（本卡不是公式卡：被判据化的是三处修复的**证据与判据**）
- `disclosure_adaptation` = **`unmapped`**（原值保持）
- `accuracy` = **`unproven`**（原值保持）
- `implementer_signed = false`、`implementer_never_signs_acceptance = true`、`verdict_is_transcribed_not_authored = true`

### 8.3 不授予 / 不做

- **不重裁 F-3**：`f3_state = pending_routed_not_refilled`；F-3 归 T1-10-FIX reviewer 裁权；PT-1/PT-2 维持 rc4，本卡与本落定**均未自填**。
- **不晋升**、**不 apply/merge changes.diff**、**不改修法**、**不改五份计划文件**、**不碰其他卡**、**不联网**、**不跑测试**、**零 git 写**。
- JSON 写后重解析；新文件记 sha256 + 字节（见交付回执）。
