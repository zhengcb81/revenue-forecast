# T1-F3-FIX / a20260925-01 - carrier landing（簿记转录）

> **本文件由 carrier-landing 簿记 pass 创建；创建前本 attempt 无 `review.md`。**
> 落定前本 attempt 顶层 = 目录 `after/` `baseline/` `before/` `evidence/` `recovery/` `scripts/` `worktree/` `_pytest_tmp/` + 文件 `binding.json` `changes.diff` `commands.json` `decision.md` `diff_stats.json` `handoff.json` `oracle.md` `reviewer_report.md` `reviewer_report.sha256`（`Test-Path .../review.md` = **False**；`Test-Path .../evidence/T1-F3-FIX/qualification.json` = **False**）。
> 本文件**只转录**独立复审 `reviewer_report.md` 的裁决与实测，**自身不授予任何东西、不添加任何验收、不产生新裁决**。签署面 = `reviewer_report.md`；**落账是簿记转录，不是实现者自签**（`verdict_is_transcribed_not_authored = true`、`implementer_signed = false`）。

---

## 0. VERDICT BLOCK（裁决转录）

- **verdict** = **`ACCEPT`** —— 原文 `VERDICT: ACCEPT`，逐字转录自 carrier 第 **7** 行（报告全文共 **288** 行，裁决在文件头部独立成行）。
- **计数** = **P1 = 0 / P2 = 0 / P3 = 8**（carrier §13：`**P1：无。P2：无。**` + `P3（不阻断，供父方/下轮参考）：` 8 条编号项）+ **未验证/限制（§14）**，见 §2。
- **carrier** = `reviewer_report.md`（attempt 内相对路径 `execution_runs/T1-F3-FIX/a20260925-01/reviewer_report.md`）
- **carrier sha256** = `e992c1f1e5882d77e45c90bb84aa8acd2e5a00f57096e15b4743fa89c8ba8ba4` —— **32516 B / 288 行**，落定时只读独立复算 == 侧车 `reviewer_report.sha256`（**85 B**，其自身 sha `b0605bc62ef984cb7dcce29e22dfd8b8d52256019f91762a7611f777217ba8db`）读回 == 派单 pin。编码 **UTF-8 无 BOM**（首 3 字节 `35 32 84` = `# T`）、**LF-only（CR 计数 = 0）**、单尾 LF。
- 侧车内容 = `e992c1f1e5882d77e45c90bb84aa8acd2e5a00f57096e15b4743fa89c8ba8ba4  reviewer_report.md` —— **读回相等**。本 pass 对 carrier 与 sidecar 写入 **0 字节**。
- **reviewer / N=1** = 独立复审工位（与实现者非同一人；carrier L3-L5「独立复审（与实现者非同一人）」）；写入面 = 本 attempt 内两个新建文件 `reviewer_report.md` + `reviewer_report.sha256`（除此之外零字节写入，carrier L5）。
- **nature of this file** = bookkeeping transcription：**不自签**（`implementer_signed = false`）、**裁决是转录不是创作**（`verdict_is_transcribed_not_authored = true`）、不裁 B1/B4/B5/B3 四条边界、不裁是否落库/合并、不晋升。

**裁决 / 发现 / 未验证的位置**（1-based 行、两端包含；byte proof = 对 `carrier_sha256` 态文件的 0-based 字节偏移，区域含末行行尾 LF）：

| 区域 | 行 | bytes（含尾 LF） | len | sha256 |
|---|---|---|---|---|
| 报告头（L1-L8，含角色/写入面/裁决） | L1-L8 | 0..466 | 467 | `67cc640a6df751339cc18e02735884cf30da0f0b34db921ca7f94608139afc5f` |
| §0 复审方法 | L11-L27 | 472..2903 | 2432 | `fd0b19829f7ff697f70cd6f9b6f8fdaf160e0d1be54e6a345b1ad934f31a0aed` |
| §1 逐项核验表 + 驱动聚合 | L28-L51 | 2904..7288 | 4385 | `05034146bb4320976c115e8b8cc4253aa99e0f9ab8516f47857e1df8d4605ea3` |
| §2 词表 16→17 | L52-L66 | 7289..8703 | 1415 | `cfd9a14dfb763734a461cd9803ccab3cf38eb02e00b7a85979a48772075a7fe7` |
| §3 四变异臂 + 批次负控 | L67-L88 | 8704..10801 | 2098 | `46cd074ff783bf60c86b7ed8c1f12fb9886b02c174cdbff51c5afc31932f38e4` |
| §4 行不交界独立重算 | L89-L107 | 10802..12826 | 2025 | `00d3c53cb114467a46cb38359c7b57522bed5845a919c767729d5ad4dc7e8faf` |
| §5 合并链重建 | L108-L120 | 12827..13465 | 639 | `0d99a1febe5a76bf146e232e7c252acac422f9d6a9ad47642fdb4155674ee94d` |
| §6 changes.diff 判定 | L121-L131 | 13466..14596 | 1131 | `863ca365daf931827a38598591523dc9adcefbe91ead81887efd76387e1bf586` |
| §7 oracle 先冻后跑 + 两条 erratum | L132-L164 | 14597..18609 | 4013 | `9e016a2fa59358111792ae1f0da50d659a11d47d9c09d00642689c971e30d568` |
| §8 不自填 B1/B4/B5/B3 | L165-L187 | 18610..20620 | 2011 | `edb254fdaf014d1d2617ec6606bf0c5dcf04e0ee4a87cd30a24de9d8e1ffd05d` |
| §9 仪器纠偏 IC-1/2/3 | L188-L196 | 20621..21948 | 1328 | `a81a792dd9c90d2d0597a54868e5e4f4979648c2a7914c9ff247db7064442f47` |
| §10 未跟踪路径披露核对 | L197-L206 | 21949..23320 | 1372 | `3e8e8c7a8e02a57a2435a4668e2f918132e14efa2c97d9ad60ff94bd2db6589d` |
| §11 复审自身只读边界 | L207-L215 | 23321..24286 | 966 | `0807353e408efb5bf4662430f0c35feb20a7153f7bfe1c6f54585a2a80335978` |
| §12 哈希复核表 | L216-L246 | 24287..26056 | 1770 | `97d1ae53436299289b5a44ab6159d7e1df81eaac6cf48e121669ac2653238fa4` |
| **§13 发现分级（P3 八条来源）** | L247-L263 | 26057..28966 | 2910 | `02c02a48a9644356084dc3cfdd6ce2cd4dd2543aea17fc98507a20ca60cf124d` |
| └ §13 编号条目正文（P3-1..P3-8） | L253-L260 | 26153..28960 | 2808 | `43a360a3a83e4bd8e710b4dfbc013247a4ad7e7de2e5e53fdfbfd83da5486cef` |
| **§14 未验证 / 限制（原文 8 条来源）** | L264-L276 | 28967..31190 | 2224 | `06f7069a0843ae60ae1063ccdb3a34556b53cdb2b3cb49276e47445b864d180e` |
| └ §14 编号条目正文（1..8） | L266-L273 | 29010..31184 | 2175 | `96c7918d7312913accd1cff429272621ec153d14accc37b51db9c2c9973e1f4f` |
| §15 我没有做的事 | L277-L288 | 31191..32515 | 1325 | `a00ad2ff13a702dffb2695409681f78022122f1848af9217258c28832798f64f` |
| **裁决行 `VERDICT: ACCEPT`** | L7-L7 | 450..465 | 16 | `ffd796ea6572fdaf4dce6d9984e6e9294cf8c0c564ce345d73132bf29aa1b3b4` |
| └ 同行去尾 LF（纯文本 15 B = `VERDICT: ACCEPT`） | L7-L7 | 450..464 | 15 | `f422a3f09f3f34867781b3d435ff517074b87f9ef6852bd7732ef50f8b95d1e7` |

---

## 1. 八条 P3 逐条（逐字转录，不得弱化；**均不阻断**）

> 每条 = carrier §13 原文（`verbatim`，一字不改）+ 派单同条的携带口径（`dispatch`，一并携带、不弱化）。是否阻断：**否**（全部 P3，不改变 ACCEPT）。处置：**只原样转录**，本 pass 不做任何处置。

### P3-1（文档精度）

> **P3-1（文档精度）** 冻结 oracle §3 表中 T1-F2-FIX 的「**新侧全 hunk** = `53–63 / 364–379 / 458–476`」与 difflib 头本身不符（`@@ -53,7 +53,14 @@` 的新侧全 hunk 实为 `53–66`；另两处实为 `364–382`、`458–479`）—— 该列实际给的是「上下文起点 → 改动终点」。**受影响的断言口径是「新增内容 = 56–63 / 367–379 / 461–476」，我重算完全正确；且即便按整 hunk 包络加严，交集仍为 ∅** ⇒ 结论不受影响。

- dispatch（携带口径）：oracle §3「新侧全 hunk」列与 difflib 头差 3 行（实为 `53-66/364-382/458-479`，其断言口径「新增内容」正确、结论不受影响）。
- source：`reviewer_report.md` §13 行 253（区域 26153..28960 内）。

### P3-2（判据覆盖）

> **P3-2（判据覆盖）** `cmd_mutations` 对臂 4 的红判据只要求 `TS1/TS5 == rc=4`，**不校验 `TS2/3/4` 仍 rc=0**（E2-c 声称其为预期）。实测确为 0/0/0，但驱动未把该预期固化为 check。

- dispatch：驱动臂 4 **不校验 `TS2/3/4` 仍 rc=0**。
- source：§13 行 254。

### P3-3（判据覆盖）

> **P3-3（判据覆盖）** `cmd_batch` after 相的 `B-BYTE-2` check 是硬编码 `ok=True` 占位（真正跨相比较放在 `invariants`）；我已**自行逐字节验证**良构-only 报告 sha 前后相等，故事实成立，但该子命令单独跑时会给人「B-BYTE-2 已验」的错觉。

- dispatch：`cmd_batch` 的 `B-BYTE-2` 在 after 相是 **`ok=True` 占位**（真比较在 `invariants`，复审已自行验证）。
- source：§13 行 255。

### P3-4（披露精度）

> **P3-4（披露精度）** `handoff.boundary.untracked_non_planning_disclosure` 把 `.tmp-r41-mutation/**` 记作 **(46)**，我实测 **45**（总数 50 正确：45+1+2+2）。

- dispatch：`handoff` 未跟踪分组标签 **(46) 实为 45**（总数 50 对）。
- source：§13 行 256。

### P3-5（复现性提示）

> **P3-5（复现性提示）** 驱动的 `probes/gates/ncmissing/vocab/batch` 的 `--sut` **默认指向 worktree（修复像）**，复审者若不显式传 `--sut <left image>` 会把 `--phase before` 静默跑在修复像上；`commands.json` 里 before 相显式带了 `--sut`，故实现者没错，但这是驱动的易错点（我复跑时全部显式传参）。

- dispatch：驱动 `--sut` **默认指向修复像**，复审者漏传会把 before 跑错像。
- source：§13 行 257。

### P3-6（表述计数）

> **P3-6（表述计数）** oracle §5 I-7 / handoff / decision.md 称「**11 个 harness pin**」，而 `binding.json.harness_pins_byte_identical_through_the_run` 实为 **10 个 harness 文件**（另含 1 条 I-14-B oracle + 2 条目录级 0 字节声明 + 1 条 note，共 14 键）；若把 oracle 计入则为 11 个被 pin 文件，但那样 §5 又把它与「I-14-B oracle」并列重复计数。实质（全部 pin 三次 sha 相等）我已验证成立。

- dispatch：「11 个 harness pin」**实为 10 个 harness 文件 + I-14-B oracle**（实质已全验）。
- source：§13 行 258；corroboration §12 末行「`binding.json` 的 harness pin 与 `freeze.json.harness_pins`（10 个 harness 文件）**逐项相等且等于 binding 登记值**（`I-7a/I-7b` 我复跑均 PASS）」。

### P3-7（观测口径）

> **P3-7（观测口径）** `evaluate_probes` 的 GREEN `computed` 比较只比对冻结期望表里**列出的键**（多余键不会失败）；良构路径的字节同一性由 `gates` 另行覆盖，故风险有限。

- dispatch：`evaluate_probes` **只比期望表列出的 `computed` 键**。
- source：§13 行 259。

### P3-8（证据易碎性，非产品缺陷）

> **P3-8（证据易碎性，非产品缺陷）** `invariants` 的 temporal 检查读的是 `evidence/before/**` 的 **mtime**；我在第一份副本上**就地重跑 before 相**后该项翻红（30/31），把原始 before 证据原样还原后即回 31/31，且生产树上该检查本为真（101 文件最晚 `21:31:38` < SUT `21:33:43`，晚于者 0）。⇒ 该 check 对「复审者就地重跑」敏感，建议将来改用证据内嵌的 run 时间戳或在 after 相重新落盘前先快照 before。

- dispatch：`invariants` 的 temporal 检查**读 mtime**，复审者就地重跑 before 相会误报（复审在副本上先误红 30/31，还原原始 before 证据后 31/31；**生产树上该判据为真**）。
- source：§13 行 260；同源 §14 第 8 条。

---

## 2. 未验证 / 限制（carrier §14 逐条转录）

**计数对账（如实标注，不裁剪）**：派发单记「**6 项未验证**」；carrier §14（L264-L273）**原文编号为 8 条**。本文件按原文 **8 条全量逐字转录、一字不删**；并按各条原文自身措辞标注类别以对上派发单的 6：**§14.1 / §14.2 / §14.3 / §14.5 / §14.6 / §14.7 = 6 项「未验证」**；**§14.4**（原文为「**未裁** …… 均属父方/owner」= 裁权边界声明）与 **§14.8**（原文为 30/31 的**成因说明**，「**这不是实现者的缺陷**」）属「限制 / 说明」类。若父方对「6 项」的取法不同，8 条均在下方、可直接重取。

### 2.1 原文 §14 全量（8 条，逐字）

1. **`evidence/before/*` 由脚本早期版本生成**（handoff 自曝的三处差异：S9 码序表、TS4 GREEN 表、变异臂定义）—— 旧版本未留存，**我无法逐字节比对两版脚本**；但我在隔离副本上**独立复跑 before 相全部判据**（probes 12/12、gates、suites 32/18/23/29、ncmissing 7/7、vocab 16、batch B-NEG、mut20 20/20），结果与其登记值一致 ⇒ 该披露对结论无实质影响。
2. **未复跑 `freeze` 与 `diff` 子命令**（二者会覆写 `evidence/freeze.json` / `changes.diff` / `diff_stats.json`，越我写入面）；改为对这些产物做哈希与内容独立核验。
3. **新测试族 16144 B 我未逐行通读**：实读到 **15 个 `def test_*`**，其中 1 个按 `TS_CASES = {TS1…TS5}`（5 例）参数化 ⇒ **14 + 5 = 19 例**；TS-4 断言值为 `[0, 10]`（`[0, 0]` 断言 0 处）；并以 empirically RED（6 passed/13 failed）→ GREEN（19 passed/0 failed）验证。
4. **未裁** `changes.diff` 是否落库/合并、未裁 B1/B4/B5/B3 四条边界的最终归属、未裁 F-1/F-2/P4 复审结论 —— 均属父方/owner。
5. 解释器差异：实现者用 I-14-B venv `python.exe`，我用系统 `python`（同为 3.13.9，pytest 同为 9.1.1），结果逐项一致，但我未逐文件比对两解释器环境。
6. `probe_root_m700/` 因权限不可枚举，我只能确认其**存在**与 git 无法列出，未核其内容（父方已登记「删不掉」）。
7. 实现者称「4 个未跟踪文件 mtime 落在本卡时间窗内」—— 现存项中最早的 `h2.log` 为 `21:01:12`（早于 freeze `21:25:10`），被移走的两个 `probe_root_m777*` 我已无法取其原 mtime，**该句只作部分核实**。
8. 我在 `%TEMP%` 副本上的**第一次** `invariants` 出现 30/31（唯一红 = temporal），原因见 P3-8：是我先在同一副本重跑了 before 相，把 `evidence/before/**` 的 mtime 刷新到 SUT 修改之后。**这不是实现者的缺陷**：还原原始 before 证据后 31/31，未动的干净副本亦 31/31，且我独立在生产树上算过该判据为真。报告中所有 31/31 均指还原后/干净副本的结果。

### 2.2 类别标注（对上派发单 6 项）

| §14 条 | 原文性质 | 归入 |
|---|---|---|
| 1 | 无法逐字节比对两版脚本 | **未验证（1/6）** |
| 2 | 未复跑 freeze / diff 子命令 | **未验证（2/6）** |
| 3 | 新测试族未逐行通读 | **未验证（3/6）** |
| 4 | **未裁**三项（归父方/owner） | 限制 / 裁权边界（不计入 6） |
| 5 | 解释器环境未逐文件比对 | **未验证（4/6）** |
| 6 | `probe_root_m700/` 内容未核 | **未验证（5/6）** |
| 7 | mtime 句**只作部分核实** | **未验证（6/6）** |
| 8 | 30/31 的成因说明（非缺陷） | 限制 / 说明（不计入 6） |

---

## 3. 复审的独立复跑方式（carrier §0 逐字转录）

**回源读（不是读转述）**

1. `execution_runs/I-14-B/a20260919-01/oracle.md` 的 `### 11.8`（L274–294；文件 28930 B / `b1eb5d0cf83dd8f0…` = 派发登记值，只读）。另验：该文件**前 26554 B 的 sha256 = `bdd0407ab577ed45…`**（登记的前像），且 `### 11.8` 恰好起于偏移 **26554** ⇒ §11.8 是纯追加、其前字节一字未改。
2. `T1-10-FIX/a20260923-01/review.md` §7（L73–131，sha `1ab78c3d712ecef4…`/24335 B ✓）与 `reviewer_report.md` §7.3（L159–216，sha `96847e0a9e2d01db…`/30247 B ✓），两处内容互为逐字副本（amendment text 一致）。
3. 本卡 `oracle.md`（31227 B / `ba17f83740104190…`，含两条 append-only erratum）、`handoff.json`（19808 B）、`decision.md`、`evidence/after/invariants.json`（9093 B / `c608fce75d9abe99…`）、`binding.json`、`commands.json`、`evidence/freeze.json`、`evidence/line_zones.json`、`evidence/after/line_disjointness.json`、`evidence/instrument_runs/README.md`。

**隔离复跑（测试只在 `%TEMP%` 副本，生产树只读）**

- 驱动：**`scripts/verify_t1_f3_fix.py`（59379 B / `c311fe9722158bc9…` = 登记值）**；我在 `%TEMP%\f3rev` 下按**相同目录深度**复制整个 attempt（排除 ACL 坏掉的 `_pytest_tmp`）+ `invariants` 需要经 `ATTEMPT.parents[2]` 解析的 5 个前置被 pin 文件（I-14-B `oracle.md`、两前置卡的 `changes.diff`+`handoff.json`；另多复制了 T1-10 的 `review.md`/`reviewer_report.md` 供回源读），并在 `%TEMP%\f3rev2` 再建一份**完全未动的干净副本**作对照。
- 复跑子命令：**`probes / gates / suites / ncmissing / vocab / batch / mutations / invariants`**（**before 相一律显式 `--sut <baseline/natural_window.t1_f2fixed.pristine.py>`**；after 相用默认 worktree SUT）；**`mut20` 因不接 `--sut`，在第二份副本上先换回左像跑 before、再换回修复像跑 after**（见 §3 末）。
- 解释器：系统 `python 3.13.9` + `pytest 9.1.1`（实现者用 I-14-B venv `python.exe` 3.13.9，`commands.json` 登记 pytest 9.1.1 ⇒ 同版本；**结果与其实测逐项一致**）。
- **独立算法**（**不运行对方的 `analyze_chain.py`**）：**自写 unified-diff 应用器 + hunk 解析器 + `difflib` 行号映射 + 词表正则 + oracle 前缀哈希 + mtime 时序检查**（脚本留在 `%TEMP%`，不属交付物）。

**驱动聚合（复审者复跑，carrier §1 末）**：`probes` before **12/12**、after **22/22**；`gates` before==after（r2 `runner_rc=0/ok/34/34/mismatch 0`、`sut_report sha beb06495fcd93b2c…`；r1 `runner_rc=1/mismatch [W1]/sha 6fa04855e76205fa…`）；`suites` before `32/18/23/29` 全 0 failed + 新族 `6 passed/13 failed`，after `32/18/23/29` 全 0 failed + 新族 **`19 passed/0 failed`**；`ncmissing` 两相全绿；`vocab` 两相 check=true；`batch` 两相全绿；`invariants` **31 checks / 31 passed / PASS**（在「原始 RED 证据 + 我自己的 GREEN 复跑」的副本上与「完全未动的原始副本」上各跑一次，均 31/31）。

**mut20 换像复跑（carrier §3 末，附加）**：20 臂变异棘轮 `mut20` —— 在第二份副本上**把左像还原进 worktree**后跑 before、再还原修复像跑 after：两相均 `mutation_count=20 / all_mutants_red_again=true / all_expected_cases_red=true / load_bearing=20`。（说明：该子命令不接 `--sut`，相位标签取决于当时 worktree 内的 SUT，故必须换像才能诚实复现 before。）

---

## 4. 词表独立验证（carrier §2，逐字）

我的独立脚本（**不引用驱动的 `vocab_of`**）在两像上各跑两条正则：

| 口径 | 左像 `9b1ebda2…` | 修复像 `d1ced6ac…` | 集合差 |
|---|---|---|---|
| `\bR-[A-Z0-9-]+\b`（冻结口径） | **16** | **17** | `after−before = {R-TIMESTAMP-MALFORMED}`、`before−after = ∅` |
| `R-[A-Z0-9-]+`（裸式） | **17** | **18** | 同上多一个新码；bare-only 恒为 `{R-UNKNOWN}` |

- 16 码（`\b` 口径，两像共有）：`R-ANCHOR-NOT-SHARED, R-BASIS-UNKNOWN, R-CLAIM-EXCEEDS, R-DUP-RUN-ID, R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-LABEL-ANCHOR, R-NO-INTERVAL, R-NO-SAMPLES, R-POSTHOC-CAPTURE, R-QC-IN-OBS, R-SAME-INSTANT, R-SAMPLE-OUTSIDE, R-SIMULATED-CLOCK, R-SUM-OVERLAP, R-TOTAL-AS-OBS` —— 与 **T1-10-FIX `reviewer_report.md` §7 列出的 16 码逐字一致**。
- **实现者说法核验**：左像上裸式确为 17、带 `\b` 确为 16，且差集恰为 `R-UNKNOWN`（`R-UNKNOWN_CLASS` 中 `_` 是 word char，`\b` 版本在 `N` 与 `_` 之间无边界，因此整 token 被排除；裸式则被截成 `R-UNKNOWN`）。⇒ **该说法成立，`\b` 口径是唯一能复现 reviewer 16 码表的口径**。dispatch 携带口径：**裸=17、带`\b`=16、多计一个假码** ⇒ 成立。
- 1c：既有 16 码未被改 —— 16 个码在两像均原样存在；集合差双向为空（词表层）；`R-UNKNOWN_CLASS` 两像均仍在源码中。
- 归属：新增码的唯一授权来源是 §11.8 ③b（原文：「本节为该码的唯一授权来源；词表自 16 码增至 17 码」）；源码中**未出现第二个时间戳码**。

---

## 5. 四变异臂（carrier §3，各 anchor 1 次，mutant sha 记入）

| 臂 | 变异（驱动 anchor 出现次数=1） | mutant sha256（前16）/ 字节 | 复审实测 | 冻结期望 | 判定 |
|---|---|---|---|---|---|
| MUT-F3-A | 整个 `_parse` 还原为修前原文 | `47788debe8b32622` / 30048 | TS1=4, TS2=4, TS3=4, TS4=4, TS5=4，全部 `report_written=false`、0 裁决 | **5/5 回 rc=4 / 无报告 / 0 裁决** | ✅ 真红 |
| MUT-F3-B | 删掉 `refusals.append("R-TIMESTAMP-MALFORMED")` | `bb2a3d136a166e11` / 30857 | 五臂全 rc=0，`verdict=accept_claim`、`refusals=[]` | **5/5 rc=0 但 `verdict=accept_claim`、`refusals=[]`（危险 accept）** | ✅ 真红 |
| MUT-F3-C | `_echo_ts` 改回 `fields.get(key)` | `9fdf20649345971e` / 30785 | TS1 `computed.started_at = "not-a-timestamp"`；TS5 = 其列表原值 ⇒ **均非 null**（verdict 仍 reject） | **TS1/TS5 非 null**（G2 红） | ✅ 真红 |
| MUT-F3-D | 删 `if started is None: obs_finished = None` 降级 | `a4f4987283275560` / 30849 | **TS1=4、TS5=4**（无报告）；**TS2=0、TS3=0、TS4=0**（仍 reject + 新码） | **TS1=4、TS5=4、TS2/3/4=0**（§6：TS-1 回 rc=4；ERRATUM-2 E2-c：TS-5 也须红，TS-2/3/4 仍绿属预期） | ✅ 真红 |

- 驱动聚合：**`all_arms_red=true`，rc=0**（派发口径：驱动 `all_arms_red=true`）。
- 冲突提示（原文携带）：P3-2 —— 驱动臂 4 的红判据**不校验 `TS2/3/4` 仍 rc=0**（实测确为 0/0/0，但未固化为 check）。

---

## 6. 批次负控（carrier §3，逐字）

| 臂 | 复审实测 |
|---|---|
| B-NEG（before `[BAD,W1,X5,C1]`） | rc=**4**、`report_written=false`、**0 裁决**（炸批，区分度在） |
| B-POS（after 同批） | rc=**0**、报告写出、**4 条 verdict**；`verdicts[0] = reject_claim + ["R-TIMESTAMP-MALFORMED"]`；**accept 恰 2 条 = W1、X5 `accept []`**，**C1 仍按既有四码 reject**，**BAD 单独 `reject + 新码`** |
| B-BYTE-1 | `json(verdicts[1:]) == json(good_only.verdicts)` ⇒ **逐字节相同 = true** |
| B-BYTE-2 | 良构-only 报告 sha 前后相等 = **`41bf0a402ee3cc23b9be49920f1546f04852604ce048c6ca617f6406d6a99648`**（**复审两像 + 实现者登记值三方相同**） |

- 冲突提示（原文携带）：P3-3 —— `cmd_batch` after 相的 `B-BYTE-2` 是硬编码 `ok=True` 占位，真比较在 `invariants`；复审已自行逐字节验证。

---

## 7. 修前 / 修后（carrier §1 第 3 行，逐字）

**修前（before）TS1–TS5**：rc=**4**、`report_written=false`、stdout `{"ok": false, "error": "internal_error", "detail": "Invalid isoformat string: 'not-a-timestamp'"}`（**TS5 = `"'list' object has no attribute 'endswith'"`**）、**0 裁决**、直调 `classify()` 抛 `ValueError`（**Traceback 5/5**）。

**修后（after）TS1–TS5**：**rc=0、报告写出、`reject_claim`、`["R-TIMESTAMP-MALFORMED"]`、受影响时间字段 null**。

**域不变（两像逐字节同）**：
- **DOC-2 两像均 rc=2** `malformed_input`（`"Invalid isoformat string: 'not-a-timestamp'"`）**逐字节同** ⇒ rc=2 域未被吃掉。
- **CTRL-4 两像均 rc=4** `"'str' object has no attribute 'get'"` **逐字节同** ⇒ rc=4 域未被吃掉。

**suites（两像 0 failed + 新族翻绿）**：`32 / 18 / 23 / 29` 两像**全 0 failed**；新族 **`6 passed / 13 failed` → `19 passed / 0 failed`（6p13f → 19p0f）**。

**gates**：before == after —— r2 `runner_rc=0 / ok / 34/34 / mismatch 0`、`sut_report sha beb06495fcd93b2c…`；r1 `runner_rc=1 / mismatch [W1]`、`sha 6fa04855e76205fa…`（**W1 既有态**）。

**NC-MISSING 7 行逐字节全等（before==after）**：`S7a / S7b / S7c = accept_claim []`；**`S8 = reject [R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-SAME-INSTANT]`，不含 `R-CLAIM-EXCEEDS`**；`K7 = [R-SIMULATED-CLOCK]`；`S9 = 四码`；`S10 = accept []`。

**invariants**：**31 checks / 31 passed / PASS**。

**mut20**：两像各 **20 / 20 all red**（`mutation_count=20 / all_mutants_red_again=true / all_expected_cases_red=true / load_bearing=20`）。

**probes 聚合**：before **12/12**、after **22/22**。

---

## 8. 行不交界独立重算（carrier §4，逐字）

方法（原文）：解析 D1/D2 的 hunk 头与 hunk 体 → 取**新侧 added/replaced 行**（仅 `' '`/`'+'` 消耗新侧行号）→ T1-F2 的新侧本来就在 L2，直接用；T1-10 的新侧在 L1，用 `difflib.SequenceMatcher(L1, L2)` 做等长/替换/删除/插入映射到 L2；defect-2 区 `{182–205}@L1` 同样映射。我的改动行集由 `difflib(L2, 修复像)` 按与他们相同的保守插入口径（插入记为前后两行）算出。

| 区 | 派发/实现者登记值 @L2 | **复审重算** | 相等 |
|---|---|---|---|
| T1-10-FIX 新增 | `{67–75, 81, 214–224}` | `{67–75, 81, 214–224}` | ✅ |
| T1-F2-FIX 新增 | `{56–63, 367–379, 461–476}` | `{56–63, 367–379, 461–476}` | ✅ |
| defect-2 | `{189–212}` | `{189–212}` | ✅ |
| `_parse` 本体 | `{89–95}` | L2:89 = `def _parse(ts: str) -> datetime:`（修前体） ⇒ 确为 `_parse` 本体 | ✅ |
| 复审改动+插入行集 | `89-92,104-105,123-124,130,132,134-135,150-151,152,167,170-173,249-250,253,259,287-288,417-419,424,489-490,515-516` | 同一集合（其合并表示把 `150-151,152` 合成 `150-152`，行集相同） | ✅ |

- **三项与登记值全等** ✓（**T1-10 `{67-75,81,214-224}`、T1-F2 `{56-63,367-379,461-476}`、defect-2 `{189-212}`**）。
- **交集**：复审行集 ∪ 三个外部区 = **∅**（`foreign_hits = {}`）；与 `{89–95}` 的关系 = **包含**（**`89–92 ⊆ 89–95`**，即 `_parse` 本体 `{89-95} ⊇ {89-92}`）。
- **加严复核**：即使把外部区放大到**含上下文的整 hunk 包络**（**T1-10 `64–84 / 211–227`，T1-F2 `53–66 / 364–382 / 458–479`**），**交集仍为 ∅** ⇒ 结论对口径不敏感。
- **内容抽查**（L2 实读）：`67–75/81` = T1-10 的 `BASIS_REGISTRY = (`…`)` 注释+元组；`56–63` = T1-F2 的 `TRUSTED_CLOCKS = (...)` 注释+元组；`189–195` = defect-2 的 quick_check/`[(started, obs_finished)]` 区；`461–464` = T1-F2 的 P4 容器归一块 —— 与 oracle §3 的描述逐条吻合。
- 与 `evidence/after/line_disjointness.json`（`715021966b9ed8fa…`）记录值**一致**。

---

## 9. 合并链独立重建（carrier §5，逐字节）

用**自写的 unified-diff 应用器**（非 `analyze_chain.py`）：

| 步 | 输入 | 复审算出的 sha256 | 目标 | 结果 |
|---|---|---|---|---|
| 1 | `apply(D1 625ecfe45f3d713a…, L0 7fff6f0c1e8ab202…)` 20293 B | `064e5381444d35a8…` | L1（`T1-10-FIX/.../worktree/i14b/iso/natural_window.py` 21416 B） | **逐字节相等 = True** |
| 2 | `apply(D2 bc87bf81bc53aad1…, L1)` | `9b1ebda2b75c4d11…` | L2（本卡 `baseline/…pristine.py` 与 `T1-F2-FIX` worktree，均 23534 B） | **逐字节相等 = True** |

前置齐备、可复现，本卡确实从合并末态起算。合并序 = **`625ecfe4 → bc87bf81 → 693d6239`（本卡第 3 腿，`merge_order_position = 3_of_3`）**。

---

## 10. `changes.diff` 判定（carrier §6，逐字）

- **29067 B** · sha256 **`693d6239fd958545bc05ad8d246758f2bb47a4ca10de37187c2f9454fadaf5ba`** = 派发/登记值 ✓
- 独立计数：**`lines_added=539`、`lines_removed=23`、文件数=2** ✓（`+++ b/` 头：`iso/natural_window.py`（修改）、`harness/tests/test_i14b_natural_window_timestamp_total.py`（新增））
- **`+++ b/src/` 0 条、`+++ b/scripts/` 0 条** ✓（不动生产 `src/`、不把脚本夹带进 diff）
- **可逆重建**：把 diff 应用到左像 `9b1ebda2…` ⇒ **逐字节重建** `d1ced6ac566d41cb…` 的 SUT（与修复后 SUT 逐字节相同）；**新增测试重建 sha `5e6644fa508a185c…`** 与 `worktree/.../test_i14b_natural_window_timestamp_total.py` **逐字节相同** ✓
- `diff_stats.json`（2530 B / `cfcfe46d…`）与复审独立重数五项（bytes/sha/added/removed/files）全部相等（驱动 `invariants` 对应 check 亦 PASS）。
- 判定（原文）：**diff 与登记值、与两像状态完全自洽，可作为落库/合并候选交父方裁**（合并序 D1 `625ecfe4…` → D2 `bc87bf81…` → 本卡 `693d6239…`）。**本复审不裁是否落库。** 本落定 pass 同样**不裁**。

---

## 11. ⭐ ERRATUM-1 性质判定 = **合法的追加式更正、非事后改期望**（carrier §7.1，三条理由逐字）

1. **可从冻结输入独立重算**：✓ 复审用 §4 冻结常量 + 修复后 SUT 自身定义（`offset = _secs(anchor_at, sampled)`、`offsets.append(int(round(offset)))`、`errors.append(abs(offset - float(label["name"])))`、`label_count = len(labels)`）**独立手算**：label0 offset=**0**、label1 `sampled_at` 畸形 ⇒ 不贡献时序事实、label2 offset=`00:00:10−00:00:00`=**10** ⇒ **`label_offsets_seconds = [0, 10]`**；`errors = [0,0]` ⇒ **`max_error = 0.0`**；latency `max = 0.0`；**`label_count = 3`** —— **与观测无关地**得出同一值。
2. **只动该单值**：✓ **冻结体内仍是 `label_offsets_seconds=[0,0]`**（**字节级确认**：`[0,0]` 在前 24326 B 内为真、`[0,10]` 为假），更正只存在于追加段；前缀哈希证明其余期望一字未改。
3. **其余期望一字未改**：✓ 同上前缀证明；**TS-1/2/3/5、DOC-2、CTRL-4、§5 九条不变量、§6 四臂、§7 批次负控、§8 边界均在冻结体内**。

**结论（原文）**：该笔误（把 offsets 写成 errors）**唯一由冻结输入决定**，且实现者已如实披露「GREEN 首跑发现该红之后追加」「该条不作为先于观测冻结的证据、标注更正后复测」——`handoff.unverified` 亦重申。这是**合法的 append-only 更正，不是按结果改 oracle**。同步改到测试断言（新族中 `label_offsets_seconds == [0,10]`，`[0,0]` 断言 0 处）与 erratum 同源同值 ✓。

**前缀证明数字**：冻结体前 24326 B sha = **`539dbb389c3e70b9df68004c93b5ccce9091046dc2fcd130f90d051eda81ef63`**，**仍是当前 31227 B 文件的不间断前缀**；**`ERRATUM-1` 起于偏移 24332、`ERRATUM-2` 起于 27082**（均 > 24326 ⇒ 纯追加；文件无 BOM、无 CRLF）。

> ERRATUM-2 逐条核（carrier §7.2）一并携带：E2-a 改动面比计划更小（`318–357` 段 0 行）；E2-b MUT-F3-A 取法 = 整函数还原，是实现冻结期望的**必要手段且未放宽判据**；E2-c TS-5 要求**更严非放宽**；E2-d B5 两形（`"abc"` / `null`）两像均 rc=4 逐字节同；E2-e §3 实测行集与 diff 统计**逐项相等**。**ERRATUM-2 未改动任何冻结判据。**

---

## 12. ⭐「不自填 B1/B4/B5/B3」判定 = **正确**（carrier §8，逐字）

**授权相交的读法（回源）**

- **§11.8 ③b（唯一授权来源）**只给：`_parse` 抛 `ValueError` 的**时间戳畸形**形状 + **一个**新码 `R-TIMESTAMP-MALFORMED`（「本节为该码的唯一授权来源」）+ 受影响时间字段置 null。
- §11.8 ③a 把容器/载体族划给 T1-F2-FIX；§11.8 rc=2 的枚举只列「`--cases` 不可解析 / 顶层缺 `cases`/`frozen_now_utc` / `frozen_now_utc` 不可解析」三形，**未列类型错**。
- 本卡冻结 oracle §5 **I-2「缺键行为不变（NC-MISSING）」**、§8 项 1 明写「缺键路径一字不改」。⇒ **两令相交 ⇒ 不自填是对的**；给非时间戳字段配码 = 引入第二个新码 = 越权。

**复审行为实测（两像对照，证明「没碰」是真的没碰）**

| 边界 | 形状 | before | after | 判定 |
|---|---|---|---|---|
| B1 | window case 缺 `fields["started_at"]` | rc=4、无报告、`detail "'started_at'"` | **逐字节相同** | 未自填 ✓ |
| B4 | 顶层 `"cases":"abc"`（CTRL-4） | rc=4、`"'str' object has no attribute 'get'"` | **逐字节相同** | 未自填 ✓ |
| B5 | `labels[].name = "abc"` / `= null` | rc=4、`could not convert string to float: 'abc'` / `float() argument must be … not 'NoneType'` | **逐字节相同（两形）** | 未自填 ✓ |
| B3 | `windows = ["x"]` / `ledger.daily = ["x"]` | rc=4、`string indices must be integers, not 'str'` | **逐字节相同（两形）** | 未自填 ✓ |

- 四条**是否该改成 per-case 拒绝、配哪个码** = **裁权在 owner，本复审不裁**；仅确认实现者「未自填、如实登记为 open_questions」这一处置**正确**。本落定 pass **同样不裁**（归父/owner）。
- 补充证据：新测试族里专设 **`test_missing_required_timestamp_key_still_raises_keyerror`**（`test_i14b_natural_window_timestamp_total.py:334`），把「**缺键仍 KeyError→rc=4**」**钉成断言** ⇒ 「不自填」不是漏做，而是被测试固化的有意边界。

---

## 13. 仪器纠偏时序 IC-1 / IC-2 / IC-3（carrier §9，逐字）

- **全部在 SUT 修改之前**：`evidence/instrument_runs/**` 最晚 mtime **`21:30:47Z`**，SUT 修改 **`21:33:43Z`**，**晚于 SUT 的文件数 = 0**；README 自述「三次仪器运行期间 SUT 字节恒为 `9b1ebda2…`」与 `freeze.json.sut_worktree_at_freeze`（`9b1ebda2…`、`equals_baseline=true`）一致。
- **只改仪器不改判据**：IC-1 改的是 direct-classify 子探针的输入切片（`['cases']` → `['cases'][0]`）并整族重跑；IC-2 改的是**期望表的码序**（`sorted`），实测值自始未变 —— 复跑的 `S9 = [R-CLAIM-EXCEEDS, R-EMPTY-EVIDENCE, R-FUTURE-CLOCK, R-SAME-INSTANT]`（字典序）与之一致；IC-3 只加 pytest 目录 mode 的插件。
- **IC-3 插件 sha**：本卡 `scripts/pytest_tmp_acl_plugin.py` = **`e96890fe3275a6ef72063b0c112afdd6607a2b4ae50c08cdd8664594f0002aa3` / 1725 B**，与 **`T1-F2-FIX` 目录内同名文件逐字节相同**，且等于其 `decision.md` 的登记值 ✓。
- **复审的复跑也依赖它**：在 `%TEMP%` 副本上，去掉 `_pytest_tmp` 父目录会精确复现 IC-3 描述的 `FileNotFoundError [WinError 3]`；补上父目录后 5 个套件计数与登记值完全一致 —— 插件与旁路（`g1_` 前缀）确实只影响目录 mode，不影响断言。

---

## 14. oracle「先冻后跑」时序（carrier §7，逐字）

| 序 | 时点（UTC） |
|---|---|
| oracle 冻结体 mtime | **21:15:15** |
| `freeze.json` 落盘 | **21:25:10** |
| `evidence/before` 最晚 | **21:31:38**（**101 个文件，晚于 SUT 修改的 = 0**） |
| **SUT 修改** | **21:33:43** |
| oracle 两条 erratum | **21:40:49** |
| `changes.diff` | **21:41:40** |
| `decision.md` | 21:42:48 |
| `handoff.json` | **21:45:57** |

- `evidence/instrument_runs/**` 最晚 `21:30:47`，**晚于 SUT 修改的 = 0**。
- 冻结体 = 前 **24326 B** / `539dbb389c3e70b9…`，**当前 31227 B 文件的不间断字节前缀**（见 §11）。

---

## 15. 未跟踪披露核对（carrier §10，只核、不删）

- 强制项 `git -c core.quotepath=false diff HEAD --name-only`：**total = 3826、非 `.planning` = 0**（与 `freeze.json.git_boundary_before_run` 记录的 `3826 / 0` 相同）。**本落定 pass 复测亦为 `3826 / 0`。**
- 额外 `git ls-files --others --exclude-standard`：**非 `.planning` 可见条目 = 48**（**`.tmp-r41-mutation/**` 45** + `h2.log` + `h2.log.err` + `assurance/unified_completion/manifests/plan_inputs.json.bak`），另有 `probe_root_m700/` 因权限 git 无法枚举（warning: Permission denied）。
- 与实现者披露的 50 对账：**`45 + 1 + 2 + 2 = 50`**（45 = `.tmp-r41-mutation/**`、1 = `plan_inputs.json.bak`、2 = `h2.log` + `h2.log.err`、2 = `probe_root_m777/f.txt` + `probe_root_m777kw/f.txt` 各 1 B）**与其披露总数吻合 ⇒ 如实**；这 2 个 `probe_root_m777*` **已按父处置移入 `I-14-E-TESTSIDE/a20260924-01/evidence/probe_root_removed_from_repo_root/`** 并从仓库根消失（复审实读到两份 1 B `f.txt`）⇒ 现在 48 = 50 − 2 ✓。
- **归属与处置**：`h2.log` mtime `2026-09-25 21:01:12`（早于本卡 freeze `21:25:10`）、`.tmp-r41-mutation/**` mtime `2026-09-20`、`plan_inputs.json.bak` `2026-09-21` ⇒ **均非本卡命令产物**；**无一落在 `execution_runs/T1-F3-FIX/**`**；实现者「只披露不删除」的处置**如实且恰当**（删除他卡文件本就越界）。
- 唯一瑕疵 = **P3-4**（分组标签 `(46)` 实为 45，总数 50 正确）。

---

## 16. carrier §11 / §12 / §15 摘要（边界与哈希）

**§11 复审自身只读边界**：生产树零写入；本 attempt 内仅新建 `reviewer_report.md` + `reviewer_report.sha256`；未触 `handoff.json`/status/任何既有字节（18 个登记 sha 全部复核）；**未使用 `git status`**，git 调用仅两条只读（`diff HEAD --name-only`、`ls-files --others --exclude-standard`）；无 add/commit/checkout/restore/reset/stash；无联网；测试全在 `%TEMP%` 隔离副本；未修改 I-14-B `oracle.md`、两前置卡、五份计划文件。

**§12 关键哈希（复核实算 = 登记值）**：`oracle.md` `ba17f83740104190`/31227；冻结体（前 24326 B）`539dbb389c3e70b9`；`handoff.json` `b636707f23a44774`/19808；`decision.md` `cb848f058258f23c`/12296；`binding.json` `a89f3bd2b9ba21c6`/8866；`commands.json` `90117d88fb834966`/9381；`changes.diff` `693d6239fd958545`/29067；`diff_stats.json` `cfcfe46d1b5ab791`/2530；左像 `9b1ebda2b75c4d11`/23534；修复后 SUT `d1ced6ac566d41cb`/30210；新测试族 `5e6644fa508a185c`/16144；`scripts/verify_t1_f3_fix.py` `c311fe9722158bc9`/59379；`scripts/analyze_chain.py` `6eb4ddede5808140`/8687；`scripts/pytest_tmp_acl_plugin.py` `e96890fe3275a6ef`/1725；`evidence/after/invariants.json` `c608fce75d9abe99`（31/31 PASS）/9093；`evidence/after/line_disjointness.json` `715021966b9ed8fa`/2146；`evidence/after/mutations/results.json` `8859313a136456d1`/801；`evidence/instrument_runs/README.md` `137b1459ba22b15e`/3404；`recovery/README.md` `7914ed64b63f3510`/2069；**I-14-B `oracle.md`（权威）`b1eb5d0cf83dd8f0`/28930**；T1-10-FIX `changes.diff`/`handoff.json` = `625ecfe45f3d713a`/`e6b9a94a40313b9a` = 11534/26509；T1-F2-FIX `changes.diff`/`handoff.json` = `bc87bf81bc53aad1`/`662b7895114399c1` = 20153/43425；T1-10-FIX `review.md`/`reviewer_report.md` = `1ab78c3d712ecef4`/`96847e0a9e2d01db` = 24335/30247。
`binding.json` 的 harness pin 与 `freeze.json.harness_pins`（10 个 harness 文件）**逐项相等且等于 binding 登记值**（`I-7a/I-7b` 复跑均 PASS）—— 同时是 **P3-6** 的实质面。

**§15 复审「我没有做的事」（10 条，逐字要点）**：① 未改本 attempt 任何既有字节；② **没有写 `handoff.json`、没有改 status、没有替实现者落定，没有在 handoff 里写任何 verdict 词**；③ 未裁 B1/B4/B5/B3；④ 未修改 `I-14-B/oracle.md`（§11.8 只读未追加）、未改两前置卡；⑤ 未写五份计划文件（`task_plan.md`/`findings.md`/`progress.md`/`REMEDIATION_REGISTER.md`/`OWNER_DECISIONS.md`）；⑥ 未执行任何有状态 git 命令、**未用 `git status`**、未 apply/晋升任何 `changes.diff`（零生产合并）；⑦ 未联网；⑧ 未删除或改动任何未跟踪路径；⑨ 测试未在生产树上跑；⑩ 未把复审中间产物写进 attempt 或生产树。

---

## 17. Bookkeeping（本 pass 的写入面与自证）

### 17.1 写入清单（写入面 = 本 attempt 目录，越界写入 = 0）

| 文件 | 改前 sha256 / 字节 | 改后 sha256 / 字节 | 动作 |
|---|---|---|---|
| `review.md` | （不存在；`Test-Path` = **False**） | 见交付回执 | **新建**（本节声明：由 carrier-landing 簿记 pass 创建，创建前本 attempt 无 `review.md`） |
| `handoff.json` | **`b636707f23a44774e320e1b2aece121401c4bbd410e3b040f7bd5fec970591ef` / 19808 B**（mtime 2026-09-25 22:45:57） | 见交付回执 | `status` `review_pending → accepted_scoped` + 追加 `status_before` / `status_authority` / `status_history` / `reviewer_status` / `carried_findings` / `unverified`（= §14）/ `unverified_pre_verdict_retained` / `merge_order_position` / `verdict_is_transcribed_not_authored` / `bookkeeping`；改后 JSON 重解析 |
| `evidence/T1-F3-FIX/qualification.json` | （不存在；本卡原无任何 qualification 文件） | 见交付回执 | **新建**（目录 `evidence/T1-F3-FIX/` 一并新建） |
| `reviewer_report.md` / `reviewer_report.sha256` | `e992c1f1…8ba4` / 32516 B；`b0605bc6…a8db` / 85 B | **同左，0 字节** | 只读复核 |
| 既有 carrier（`oracle.md` / `changes.diff` / `decision.md` / `binding.json` / `commands.json` / `diff_stats.json` / `evidence/**` 既有件 / `scripts/**` / `worktree/**` / `baseline/**` / `before/**` / `after/**` / `recovery/**` / `_pytest_tmp/**`） | 见 `handoff.json.sha256` | **同左，0 字节** | 只读复核 |
| 五份计划文件（`REMEDIATION_REGISTER.md` / `progress.md` / `findings.md` / `task_plan.md` / `OWNER_DECISIONS.md`） | — | — | **本 pass 写入 = 0**（父折入） |

### 17.2 三资格与不自签

- `formula` = **`not_applicable_with_reason`**（本卡不是公式卡：被判据化的是 F-3 修复的**证据与判据**）
- `disclosure_adaptation` = **`unmapped`**（原值保持）
- `accuracy` = **`unproven`**（原值保持）
- `implementer_signed = false`、`implementer_never_signs_acceptance = true`、`verdict_is_transcribed_not_authored = true`

### 17.3 不授予 / 不做

- **不裁 B1/B4/B5/B3 四条边界**（归父 / owner）；**不裁「是否落库 / 合并」**（归父）；**不晋升**。
- **不碰 `I-14-B/oracle.md`**（`§11.8` 只读）**与两前置卡**。
- **不改复审报告与既有 carrier**（`handoff.json` 状态转录除外）；**不写五份计划文件**；**零 git 写**、**未用 `git status`**；**不联网**；**不跑测试**。
- JSON 写后重解析；新文件记 sha256 + 字节（见交付回执）。
