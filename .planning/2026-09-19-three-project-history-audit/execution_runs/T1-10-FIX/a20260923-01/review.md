# T1-10-FIX / a20260923-01 - carrier landing (bookkeeping transcription)

## VERDICT BLOCK

- **verdict** = **`accepted_scoped`** - **transcribed verbatim** from the carrier `## 1. 裁定（verdict）` (L14-L29): 缺陷①（claim.basis 枚举校验非全函数）已在其**全部 3 个入口**（E1 载体读取 / E2 J16 守卫 / E3 `basis_registered`）**结构性**闭合；fabricated-green 负控**双向成立**（18>=11 两向皆非绿，正对照绿）；良构行为逐字节不变；缺陷② 区零交集。随附裁定 = **F-3 显式裁权（reviewer-owned，取 (b)+(c) 否 (a)）**，原文见本文件 §2。
- **carrier** = `reviewer_report.md`（attempt 内相对路径 `execution_runs/T1-10-FIX/a20260923-01/reviewer_report.md`）
- **carrier sha256** = `96847e0a9e2d01db44b882ae38b43541131865c55a95e4171e8bbb7ef4272a69` - **30247 B / 318 行**，落定时只读独立复算 == 侧车 `reviewer_report.sha256` 读回 == 登记册「一一四」所记 `96847e0a…`；编码 **UTF-8 无 BOM**（首 3 字节 `35 32 49` = `# T`）、**LF-only（CR=0）**、单尾 LF。
- **pin** = `reviewer_report.sha256`（**85 B**）内容 = `96847e0a9e2d01db44b882ae38b43541131865c55a95e4171e8bbb7ef4272a69  reviewer_report.md` —— **读回相等**。本 pass 对 carrier 与 sidecar 写入 **0 字节**。
- **reviewer / N=1** = 独立 reviewer（父 `session-bfecd191-fbc3-4a66-8ed1-6562479bf102` 派单，报告 L3-L4）；方法边界 = read / grep / pwsh 只读 + %TEMP% 自跑、产品与卡树零写、无网络、无 state-changing git（L6-L8）；REM-79 自检 rc=0 / 0 violations（L315-L316）。
- **nature of this file** = bookkeeping transcription（簿记转录）：本文件转录独立复审的裁决词与发现处置，**自身不授予任何东西、不添加任何验收**。签署面 = `reviewer_report.md`；**落账是簿记转录，不是实现者自签**（`verdict_is_transcribed_not_authored = true`；`implementer_signed = false`；`implementer_never_signs_acceptance = true`；独立复审 **N=1**）。
- `review.md` **此前不存在于本 attempt**（无实现方 stub，落定前 `Test-Path` = false）；由 carrier-landing 簿记 pass **创建** —— 既非实现方所写、也非复审员所写（复审员的原词在 `reviewer_report.md`，本 pass 0 字节触碰）；因此本文件无「前缀」可破坏，`prefix_bytes_preserved = true`（新文件，空前像）。

**ruling location**（1-based 行、两端包含；byte proof = 对 carrier_sha256 态文件的 0-based 字节偏移，多行区域含内部 LF、不含该区末行的行尾 LF）：

| 区域 | 行 | bytes | len | sha256 |
|---|---|---|---|---|
| `## 1. 裁定（verdict）` 标题 | L14-L14 | 923..947 | 25 | `35f07830e8c5135daf8965d2896889d17651852516b300a9172b1a45eb1f4c7a` |
| **裁决首句（ACCEPT…）** | L16-L16 | 950..1108 | 159 | `88dc9c01bb0b2896ab40775f5322f7f699452a62d785e743f00565dd5e5c7ce9` |
| **§1 裁定整节（verbatim 转录源，本文件 §1）** | L14-L29 | 923..2429 | 1507 | `152c17e202b4fe6fbb090a3207dff53c16d555f0fa8d8730420e0ef34cc819ab` |
| **§7 发现与处置整节（verbatim 转录源，本文件 §2）** | L136-L216 | 12052..20135 | 8084 | `c5de1e5fe6cf50936ddefbda93b663a655d41428089eba5768f77ef1d65e24bc` |
| └ 其中 **§7.3 F-3 显式裁权** | L159-L216 | 13980..20135 | 6156 | `9c9b4e0375ef56adea3779573bd11119f7f6594db784723ef2ca7a51f6ef0466` |
| **§10 未核验/限制（verbatim 转录源，本文件 §3）** | L256-L271 | 24533..26350 | 1818 | `65810d833cf9286d9134224074b5c28ee85e27b0b3e4ed5522b01f111d91f5ed` |
| **§11 ACCEPT 的 scope（verbatim 转录源，本文件 §4）** | L275-L289 | 26358..28116 | 1759 | `52f58a40094eca417ac05929ecf5cc1b8abb59cd3fa1ddafe5f86b1c511715b6` |

---

## 1. 裁决原文（verbatim 转录自 carrier §1，L14-L29）

## 1. 裁定（verdict）

**ACCEPT —— 缺陷①（claim.basis 枚举校验非全函数）已在其**全部 3 个入口**（E1 载体读取 / E2 J16 守卫 / E3 `basis_registered`）
闭合，且**结构性**地闭合（MUT-G4 证明「只补一个守卫点」不够、tuple+载体守卫一次覆盖三处）；fabricated-green 负控**双向成立**
（18≥11 声明毒化两向皆非绿，正对照绿）；良构行为逐字节不变；缺陷② 区零交集。

据此我**签发独立验收**：T1-10 的 `changes_required` 返修块四项交付（补全覆盖 / 畸形 basis 负例族 / 裁决机关不可被单例炸毁的
负控 / T1-8 式 fabricated-green 负控）在本 attempt **全部达成且经我自跑复现**。T1-10 可按返修块原文收口。

随附裁定（我拥有的唯一裁权，详见 §7.3）：**F-3 = 畸形时间戳 rc=4 的 schema 级 rc 归属 = reviewer-owned，现予裁定**：
单 case 字段的类型/格式错误属 **per-case 拒绝（rc=0、报告写出、整批全裁决）**，rc=2 只属文档/调用域，rc=4 只留真内部错误；
需以**追加式 oracle §11.8** 落文（原文见 §7.3），并把 F-3 放入**独立修轨**（T1-F3-FIX），P4 已登记的容器族则并入
**T1-F2-FIX**（父已派）。

范围与身份：本卡 `handoff.json` 仍 `review_pending` / `implementer_signed=false`（实现者未自签）；我的 ACCEPT 是**复审侧**裁定，
不改写该卡任何 status 字段（边界=只写本报告与其 sidecar）。

---

## 2. 发现与处置原文（verbatim 转录自 carrier §7，L136-L216）——含 F-1 / F-2 / P4 容器族 / F-3 显式裁权与追加文原文

## 7. 发现与处置（对应原令 §Verify-6）

### 7.1 F-1（新发现）→ T1-F2-FIX（父已派，本报告只引用）

`clock_source` 的 `TRUSTED_CLOCKS`（**set**，基线 :56 / 修复后同文本）成员测试 **基线 :338 / 修复后 :360**：
`if clock_source not in TRUSTED_CLOCKS:  # J7`。我**在修复后 SUT 上自跑** `clock_source=["system_utc"]` →
**rc=4、无报告、`internal_error: unhashable type: 'list'`**（与记录 `adjacent_discovery.clock_source_container_J7` 同值）。
reviewer P4 未点名此落点（P4 只点了 windows/sampled_at/claim/ledger），故属**新发现**，与缺陷①同族、判据不同（J7）。
**处置：并入父方已派的 T1-F2-FIX**（父令 05:56 明示该卡已派，F-1/F-2 覆盖）；同款 tuple 修法不破坏 MUT-7 锚
（`mutate.r2.py` MUT-7 锚 = `if clock_source not in TRUSTED_CLOCKS:  # J7`，我实读）。注：复审时 `execution_runs/T1-F2-FIX`
目录尚未落盘（我列目录未见），故仅按父令引用、不核其内容。

### 7.2 F-2 → 同一 T1-F2-FIX

日历载体 `claim.status` 读取 **基线 :343 / 修复后 :360 邻近行**：`claim_status = (fields.get("_claim") or {}).get("status")`
无类型守卫。我**在修复后 SUT 上自跑** `claim=["pending"]` → **rc=4、`'list' object has no attribute 'get'`**（= P4「claim 为 list」
的日历落点，本卡只修了 basis 落点 E1）。**处置：T1-F2-FIX**。

**附带实测（P4 已登记未复测的容器族，我补测于修复后 SUT）**：
`windows` 为 dict → rc=4 `string indices must be integers, not 'str'`；`sampled_at` 为 dict → rc=4 `Invalid isoformat string: 'a'`；
`ledger.daily` 为 dict → rc=4 `string indices must be integers, not 'str'`。三者同为**字段形状/载体**类非全函数，
与 F-1/F-2 同机制 ⇒ **建议并入 T1-F2-FIX 同卡**（父裁）；其拒绝语义按 §7.3 的 §11.8 规则执行。

### 7.3 **F-3 = 我的显式裁权：schema 级 rc 归属（reviewer-owned）**

**被裁对象**：`started_at="not-a-timestamp"` → `_parse` 抛 `ValueError: Invalid isoformat string` → `main()` 内部错误处理器
→ **rc=4、无报告、整批 0 裁决**（我在修复后 SUT 自跑复现：rc=4、`report=False`）。该形状在 P4 与本卡 oracle I-5 中被显式
**留待 reviewer**（`review.md:353`：「并在 oracle §11 明确"字段类型错误"属 schema 级 rc 2 还是 per-case 拒绝」；
本卡 `oracle.md` I-5「不自填」、§7 E-adj-4「reviewer 归属」）。**故所有权在我，现裁如下。**

**我读到的 rc 域文本（裁定依据）**：
- I-14-B `oracle.md:177-180`（§8）：`0`=全部 case 已判定且无不合规 accept；`2`=输入畸形/schema 不符（fail-closed）；`4`=内部错误。
- `oracle.md:188`（§8-errata，运行前写成）：`0`=报告已写出且每个 case 都已判定；`2`=输入畸形（fail-closed）；`4`=内部错误。
- `oracle.md:461-466`（实现）：**文档级**畸形（`json.loads` / 缺 `cases` / `frozen_now_utc` 不可解析）已在进入判定前走 **rc=2 `malformed_input`** —— 即 rc=2 的既有落点就是**调用/文档域**。
- `review.md:352`（P4）：rc4 在 §8 已登记、fail-closed、对「不合规被 accept」而言非阻断；但同一段同时提请 §11 澄清归属 —— 就归属措辞而言，P4 自身并未把 rc4 判为终局。
- `decision.md §6 F-3` 行：实测 rc=4、归属「schema 级 rc 归属 = reviewer 专属口径」。

**裁定（选 (b) + 需要 (c) 追加，不取 (a)）**：

1. **rc=2 = 文档/调用域专属**：只覆盖「在进入任何 case 判定之前就失败」的形状（现有 `main()` L461–466 路径）。
   此时本就没有任何裁决存在，故 fail-closed 不构成剥夺。
2. **rc=4 = 真正的内部错误专属**。用户提供的**单 case 字段**类型/格式错误**不是内部错误**；记成 rc=4 会
   (i) 误分类，(ii) **复现缺陷①的剥夺裁决形态**（报告不写、整批 0 裁决），这正是 M-T-REVIEW 已裁定为缺陷的那一种观测面。
   ⇒ (a)「rc=4 schema-class 正确并保留」**被否**：畸形时间戳属**输入**而非内部错误，且其爆炸半径与缺陷①同形。
3. **单 case 字段的类型/格式错误 = per-case 拒绝（rc=0、报告写出、整批全部裁决）**，与 §11.3 标量校验同语义；
   时间戳畸形需**一个新拒绝码 `R-TIMESTAMP-MALFORMED`**（现有 16 码词表中无对应码；缺陷①因存在同语义邻码才免增码），
   该码由下列 §11.8 追加文**唯一授权**入 §11.3 词表，受影响 `computed` 时间字段置 `null`、其余派生量按可得事实计算。
4. **需要 (c) oracle 追加**：§11 本就是「追加式勘误」节（`oracle.md:211-213`），故不改 §1–§10、不回改 §6.1 冻结四行，
   只追加 §11.8。**本卡 oracle 已冻结（sha `afe8b61a…`）且我零写入** ⇒ 追加文交**父/owner** 落到 I-14-B `oracle.md` 末尾
   （或按父方惯例落到承接修卡的 binding 引用），我不落笔。

**追加文原文（我裁定的 amendment text，逐字可用）**：

```markdown
### 11.8 rc 归属裁定：schema 级 vs per-case（reviewer-owned，追加式；触发 = T1-10-FIX F-3 + review.md:353 提请）

- **rc=2 = 仅「文档/调用域」的输入畸形**：`--cases` 不可解析、顶层缺 `cases`/`frozen_now_utc`、
  或 `frozen_now_utc` 本身不可解析 —— 即 `main()` 在**进入任何 case 判定之前**失败的那批形状
  （既有实现 L461–466）。判定对象是本次调用；fail-closed 在此不剥夺任何裁决（此时本无裁决）。
- **rc=4 = 仅真正的内部错误**（实现自身缺陷）。**用户提供的单 case 字段**类型/格式错误不属于 rc=4：
  把它记成 rc=4 既属误分类，又复现缺陷①的「剥夺裁决」形态（报告不写出、整批 0 裁决）。
- **单 case 字段的类型/格式错误 = per-case 拒绝**：该 case 记 `reject_claim`、整批照常裁决、
  报告照常写出、SUT rc=0；与 §11.3 标量校验同语义：
  - `basis` 容器 / `claim` 载体非对象 / `clock_source` 容器 / `windows`、`sampled_at`、`ledger.daily` 为容器
    → 按既有码拒绝（basis/载体族 = `R-BASIS-UNKNOWN`；时钟 = `R-SIMULATED-CLOCK`；载体不可读 ≡ 缺键）；
  - 时间戳畸形（`_parse` 抛 `ValueError`，如 `started_at="not-a-timestamp"`）→ `reject_claim` +
    **新码 `R-TIMESTAMP-MALFORMED`**（本节为该码的唯一授权来源；词表自 16 码增至 17 码），
    无法解析的时间字段在 `computed` 中置 `null`，其余派生量按可得事实计算。
- **变异/回归要求（承接修卡）**：任一畸形单 case 字段不得使任何其他 case 的裁决丢失 —— 回归面同缺陷①：
  批次臂 rc=0、坏 case 单独被拒、良构 case 输出逐字节不变；且须带「单畸形 case 不可炸批」的批次负控。
- 触发与授权链：I-14-B `review.md:353`（P4 提请 §11 明确归属）→ T1-10-FIX `oracle.md §7 E-adj-4 / I-5`
  （实现卡拒绝自填、显式留待 reviewer）→ 本裁定（T1-10-FIX 独立 reviewer，2026-09-24，N=1）。
- 落点分工：**F-3（时间戳 `_parse` 非全函数）→ 独立修轨 T1-F3-FIX**（机制=解析全函数化，与 F-1/F-2 的
  成员/载体守卫不同，且 T1-F2-FIX 已派未含此项）；**F-1/F-2 与 P4 容器族 → T1-F2-FIX**；
  两卡共用本节文本，先落者写入、后落者只引用。
```

**F-3 是否解锁**：**解锁**。所有权争点（reviewer-owned）已由本裁定闭合：F-3 不再是「等 oracle 裁定」的挂起项。
轨道选择 = **独立修轨（T1-F3-FIX）**，理由：机制不同（`_parse` 全函数化 + 新拒绝码 + 新测试族）、
T1-F2-FIX 已派且未含此项（重开范围需父改派）；但 §11.8 文本两卡共用。若父选择合并，本裁定不反对 —— 只要求
合并后仍带 (i) §11.8 追加、(ii) 批次负控、(iii) 良构字节不变三项验收面。

---

## 3. 未核验 / 限制原文（verbatim 转录自 carrier §10，L256-L271）

## 10. 未核验 / 限制（如实）

1. **MUT-G4 构造脚本未留档**：`commands.json` step 15 写「see file for full script」，但 `MUT-G4_*.json` 内仅含
   description + probes，缺内联脚本（INFO 级）；所幸**变体文件本体在盘且 sha 与声称完全相等**，行为我已自跑复现，故证据链仍闭合。
2. **`commands.json` 非执行日志**：无终端 transcript 落盘；步序与 mtime 序不完全一致（probe 在 before 相位实际最后跑）。
   我以「记录证据 + 我的全量自跑复现」替代逐字执行核对（所有头号数字均已复现）。
3. **T1-8 对照为读录级**：未重跑 `verify_t8_pre3.py`（会写其卡树），依据 `decision.md:22` 与
   `t8_pre3_cost_reconciliation.json:330` 原文。
4. **deletions=0 不可全证**：只能以「两树各 344 文件俱在 + recovery 声明 + 我未见缺失路径」支持（域=本 attempt 目录树）。
5. **T1-F2-FIX 内容未核**：复审时该卡目录在 `execution_runs/` 下未出现（父令称已派）；我只引用不核验。
6. **changes.diff 未落地**：我只做 `git apply --check`（rc=0），未执行任何 apply/merge（无授权）。
7. **I-14-H 同体副本的传播未裁**（见 §11），属父/owner 决策，不在我的裁权内。
8. **并行写入的 pin 漂移（非本卡、非我）**：pin #4 `M-T-REVIEW/…/decision.md` 在我复审期间被他方追加
   F-RV 节而变更（§9 已给双方哈希与时刻）；本报告中一切以「22 pin 相等」为前提的结论，其**取证时点**
   分别标注为「卡跑后 `23:19:19Z`」与「本复审会话开始」两次（两次皆 0/22 失配）。
   若父需在落定批次里重跑该 pin，请以**追加式注记**登记该漂移来源，而非改判 T1-10-FIX 的边界声明。

---

## 4. ACCEPT 的 scope 原文（verbatim 转录自 carrier §11，L275-L289）

## 11. 若 ACCEPT 的 scope（对应原令 Scope-if-accepting）

1. **缺陷① CLOSED at all 3 entries**（E1/E2/E3），且是 **G4-proven 的结构性闭合**（单守卫点不够：B1 仍崩于 E3、B3 仍崩于 E1；
   tuple 一次闭合 E2+E3 + 载体守卫闭合 E1）。交付 = `changes.diff` 两文件（`625ecfe4…`，+229 −4，`git apply --check` rc0）。
2. **NC 非伪造绿成立**：PC 绿 + NC-1/NC-2 双向红（18≥11），与 T1-8 的 11-毒化 rc=0/11-11 绿方向相反。
3. **F-1 / F-2 → T1-F2-FIX**（父已派，本报告 §7.1/7.2 引用；P4 容器族我建议同卡并入，父裁）。
4. **F-3 → 按 §7.3 裁定**：per-case 拒绝 + oracle §11.8 追加（原文已给）→ **独立修轨 T1-F3-FIX**（或父改派合并，验收面三项不减）。
5. **changes.diff 两文件的落点（application route，我实测）**：
   - diff 头为 `a/iso/natural_window.py` 与 `b/harness/tests/test_i14b_natural_window_basis_total.py`，
     **path base = I-14-B attempt 根**（`execution_runs/I-14-B/a20260919-01/`，其布局恰为 `iso/` + `harness/`）；
   - 左侧 sha `7fff6f0c…` == **I-14-B 规范源**（pin10）**且 == `I-14-H/a20260919-01/iso/natural_window.py`（逐字节同体）**
     ⇒ 对 I-14-B 可直接 apply；对 I-14-H 亦同体可 apply，**是否传播由父裁**；`I-14-I/.../natural_window.py` = `9edb9515…`
     （另一修订）⇒ 在其上不能直接 apply，需另行 rebase；
   - **产品树外零 SUT**：全项目 `natural_window.py` 仅出现在 `.planning/...` 内（I-14-B / I-14-H / I-14-I / 本卡两棵副本），
     即本 diff **不是对生产源的修改**；新测试文件与 SUT 同 base、**同波次**骑行即可（无需单独迁移通道）。
---

## 5. Bookkeeping（落定簿记 — 本 pass 的写入面与自证；本节为追加，前 4 节字节不动）

### 5.1 写入清单（仅限本 attempt 目录；越界写入 = 0）

| 文件 | 改前 sha256 / 字节 | 改后 sha256 / 字节 | 动作 | `prefix_bytes_preserved` |
|---|---|---|---|---|
| `review.md` | （不存在，`Test-Path` = false） | 见交付回执（本节写入后的终值） | **新建**（I-10-A 落定先例：`review.md` 此前不存在于本 attempt ⇒ 由簿记 pass 创建并声明） | `true`（新文件、空前像；无既有前缀可破坏） |
| `handoff.json` | `f3f4dd2bc5c08f09f69261a1069a5ec3eedab1206d02951ea6b84195c661a445` / **7708 B** | 见交付回执 | 两处授权值替换（L4 `status`、L5 `reviewer_status`）+ 纯后缀追加 `status_before` / `status_authority` / `status_history` / `verdict_is_transcribed_not_authored` / `notes` / `bookkeeping` | **前缀自证**：删去追加块 + 回滚那两处值后 == 改前镜像**逐字节相同**（`f3f4dd2b…` / 7708 B 复现成功）；除 L4、L5 两个值串外**无任何既有字节被改** |
| `evidence/T1-10-FIX/qualification.json` | （不存在，本卡原无任何 qualification 文件） | `f34175b6c97dfcd5d40f31a0a1c4faa2cfd3060c073b3d201f41ec2eba179189` / **8042 B** | **新建**（三资格镜像） | `true`（新文件、空前像） |
| `reviewer_report.md` + `reviewer_report.sha256` | `96847e0a9e2d01db44b882ae38b43541131865c55a95e4171e8bbb7ef4272a69` / 30247 B；`c7ee5775acb72153729288ddcefb3d56607e4f8fe2d7dfaeb9350512a0353288` / 85 B | **同左，0 字节** | 只读复核 | `true`（未写） |
| 任何 `oracle.md` | — | — | **本 pass 写 oracle = 0**（本卡 oracle 仍 `afe8b61a3274e2473fe08db116e362bacf30e7c99facc90ec13d9453c929e4fb` / 10758 B） | `true`（未写） |

### 5.2 三资格（`qualification.json` 镜像，逐字口径）

- `disclosure_adaptation` = **`unmapped`**（原值保持；登记册 §708 通则：缺字段补 canonical 值 = 补必需字段而非改字段）
- `accuracy` = **`unproven`**（原值保持）
- `formula` = **`accepted_scoped`（仅 formula）**——转录自复审 ACCEPT（carrier §1 + §11 scope），非本 pass 自授
- 三个 flag：`implementer_signed = false`、`implementer_never_signs_acceptance = true`、`verdict_is_transcribed_not_authored = true`

### 5.3 两条 pin 漂注记（分列，不得合并）

1. **pin #4 `M-T-REVIEW/a20260923-01/decision.md`**：`91f6f21b…`(8473 B) → `43936ff6…`(11672 B)、mtime `2026-09-24T05:07:05Z`。**照录登记册「一一四」原文口径**：「我方落定批追加 F-RV 节、`:53` 载体行与修复源 `90bcefb9` 未变 = **注记不改判**」；登记册 L2103 另记「并行漂移注记（M-T decision `91f6f21b→43936ff6`）=我方 D9 落定批、已由本卡边界两时点0 失配取证覆盖」。⇒ 不改判本卡边界声明。
2. **pin #19 `I-14-B/a20260919-01/oracle.md`**：`bdd0407ab577ed4564b8e948d8e3954b663c795dbcd7a3035485424ae753baf3`(26554 B) → `b1eb5d0cf83dd8f059d7f011427447a4b79b211c19167f0190b2c140cb34ade6`(28930 B)、`delta = +2376 B`。**成因 = 父按登记册 §114 / 复审 §7.3 落笔追加 §11.8（纯后缀），非本卡改动**：`written_by_this_attempt = false`；该 pin 属本卡 22 个 input pin 之一，**#19 失配归因于父追加、不属本卡运行窗**（本卡运行窗止于 `2026-09-23T23:24Z`）。与 pin #4 **性质相同（后置他方追加）、成因不同，两条分列**。

> 复审自身两次取证时点（卡跑后 `23:19:19Z`、本复审会话开始）均为 **22/22 相等**；复审报告 §10.8 明写：若父需在落定批次重跑该 pin，应以**追加式注记**登记漂移来源，**而非改判 T1-10-FIX 的边界声明**——本节即照此执行。

### 5.4 oracle §11.8（item 3：本 pass **不写**，只做簿记）

- 追加文原文 = 复审报告 **§7.3 全文**（amendment 代码块 byte 区 `17226..19600` / 2375 B / `a94ba5c24ba7903e9873b5e2d3f59b78bf41643c5dc70ac79822740f99ea853a`）。
- 落点 = **I-14-B canonical `oracle.md` 末尾**，**由父落笔**（复审 §7.3 第 4 点原文：「追加文交父/owner 落到 I-14-B `oracle.md` 末尾 …… **我不落笔**」；登记册 §114：「父落笔、§1-§10 与 §6.1 冻结四行不动」）。
- 父已执行（脚本 `.planning/_pwf_tmp/append_i14b_118.py`，6 条后置判据全 OK）：前像 `bdd0407a…`/26554 B → 后像 `b1eb5d0c…`/28930 B；`prefix_bytes_preserved`、**§6.1 冻结四行（L128-131）sha `06f399e3fa082d9c82377d84a1a0912988c54e42e9ec339c33cb247f20f69f26` 前后相同**、§1-§10（L23-L210）`9c153b26…` 前后相同、`## N.` 标题数不变、`### 11.8 ` 恰 1 处、纯后缀。
- **本 pass 的写界**：派单硬性纪律 2 = 写入范围仅限本 attempt 目录 ⇒ 我**不写任何 oracle**（canonical 与 `worktree/i14b/oracle.md` 副本均不碰，后者是 diff/证据基线副本）。已向父报冲突并由父裁定 = C（父落笔）。

### 5.5 diff 路基注记（同步写入 `handoff.json` `notes.diff_route`）

- 本卡 `changes.diff` 路基 = **I-14-B attempt 根** `execution_runs/I-14-B/a20260919-01/`（布局恰为 `iso/` + `harness/`）；左 sha `7fff6f0c1e8ab202d3034540ca3b2b6cb6be17b4661bc726f7f5261159e4e796` = **canonical pin10 = I-14-H 同体**（对 I-14-B / I-14-H 可直接 apply；**是否传播 I-14-H 由父裁，未做**）；**I-14-I 另修订 `9edb9515…` 不能直接 apply**（需另行 rebase = 父传播裁，**未做**）。
- **非生产源**：全项目 `natural_window.py` 仅出现在 `.planning/` 内（I-14-B / I-14-H / I-14-I / 本卡两棵副本）⇒ 本 diff **不是对生产源的修改**。
- **合并序** = T1-10（`changes.diff` `625ecfe45f3d713a08b5873c6cb3df258c25279d4c5bf3f4e25295cd441199ac`）→ T1-F2-FIX → T1-F3-FIX，**行不交界声明**入各自 oracle；本 pass **不 apply / 不 merge / 不 rebase**（复审只做过 `git apply --check` rc=0，见其 §10.6）。

### 5.6 边界与不授予

- **零自签**：本 pass 只转录，`implementer_signed = false`；**未发明任何 ACCEPT**——`accepted_scoped` 全部溯源自 carrier §1/§11。
- **git**：只读（`diff` / `status` / `cat-file` / `grep`）；**零 state-changing git**；`git diff HEAD --name-only` **非 `.planning` = 0（落定前实测：total 3820、non-`.planning` = 0）**，落定后复测见交付回执。
- 未触碰：`REMEDIATION_REGISTER.md` / `progress.md` / `task_plan.md` / 任何其他卡的目录 / 任何生产树文件 / `reviewer_report.md` 及其 sidecar / 本卡 `oracle.md`、`decision.md`、`changes.diff`、`binding.json`、`commands.json`、既有 `evidence/**`（仅新建 `evidence/T1-10-FIX/qualification.json`）。
- **JSON 自验**：`handoff.json` 与 `qualification.json` 写后均 `json.load` 重解析通过。

`review.md` 终值 sha/字节与 `handoff.json` 改后 sha/字节**见交付回执**（文件不含自引用哈希）。
