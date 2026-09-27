# I-17-B / a20260926-01 独立复审报告（终审验收 · A 级全量档）

- 复审工位：独立复审（未参与该项实施）；复审时间：2026-09-27（本地）
- 被审：`oracle.md`(10,528B) · `final_report.md`(4,615B) · `verification.json`(3,868B) · `handoff.json`(2,150B) · `six_negatives_result.json`(5,486B, UTF-16LE) · `run_six_negatives.py`(9,332B)
- 本工位只写本报告 2 新文件；被审/上游只读，收尾复哈希通过；不改卡状态；无 git 写、未运行 `git status`；未联网；未解除任何 `OPEN/BLOCKED-*`。

## 0. 判级（≤8 行摘要）

```text
VERDICT: ACCEPT —— classification=blocked 照常可 ACCEPT；无 P1（六负例判读正确·六资格有据·无封盘动·无参数放行）
六负例判读复核：正确。N1/N2/N4/N5 确未拒（closure_ready=True / unsatisfied 空，字段自核一致）；N3/N6 拒；
  9 例 3 拒、all_six_rejected=false 与脚本逻辑（N 前缀计数）吻合；组合三 sha 现算与记录一致（当前组合零漂移）、
  tmp 夹具与脚本逐字段吻合（实跑证据）；「验收门负例缺口」成立，blocked 判定符合卡文动作 2 与 oracle §4 不变式。
六资格分类核：6/6 依据在案。复用 3/3（I-16-B-02 内 3×capture_ready 实见）→来源获取 pass_scoped 合法；
  I-12 两卡 status=accepted_scoped（blocked 合格形态）→正式预测 blocked 有据；I-13-BC classification=
  research_draft_needs_review 实测、全档无 ready 值、unproven×20 且未被改写为提高→Q4/Q5 有据；
  周任务 ok=false 实证（审计窗内两连败，全序列 09-13 起三连败，报告措辞偏保守）→持续服务 blocked 有据。
五分类无掩盖核：无「全部通过，除」掩盖措辞（仅禁令引用），blocked 独立成段 5 项；但五分列不完整
  （限域通过并入「已完成（限域）」、合理退役/NA 桶缺席未显式计 0）→P3-4，无掩盖效果。
变异三臂（只读自算等价）：M2 无 ready 越权 ✓；M3 无掩盖 ✓；M1 链卡交待实质完整（动作1表列 14 + I-00-C 于
  动作2 = 15；「15/15」计数措辞不精确→P3-5）。oracle §4 冻结变异计划（MUT-1..4 + verify_i17b.ps1 + 红绿
  原始 rc 留痕）未落地→P2-2。
红线/封盘：params_released=false×2 · implementer_signed=false · releases_nothing=true · 无 OPEN/BLOCKED 解除
  · 写入面合规（attempt 目录内）· 上游 16 handoff 复哈希与 oracle §2.2 冻结表 16/16 全中。
P：P2-1 父接手（必判）；P2-2 变异留痕缺失。P3-1 UTF-16（必判）；P3-2 handoff 误记 oracle sha；P3-3
  source_hashes 缺失；P3-4 五分列不完整；P3-5 M1 计数措辞；P3-6 CTRL 字段语义反转。unverified 见 §4。
没做的事：不改卡状态 · 不解除 OPEN/BLOCKED-* · 无 git 写/git status · 未联网 · 未重跑六负例/变异（只读自算）。
```

## 1. 回源与完整性核（V2-4）

| 项 | 结果 |
|---|---|
| 卡文 `card_I-17-B.md`（1,297B，12 行 5 动作+退出逐字） | sha `08266a1b…` 与 oracle S1 一致；5 动作与 oracle §1 逐字核对一致 |
| `card_I-00-C.md`（2,240B，六负例定义 L2） | sha `19e9e0b3…` 与 oracle S2 一致；六负例=N1 无证据全过 / N2 READ10 错能力证据 / N3 旧 PASS 新 FAIL / N4 空commands / N5 空invariants / N6 删 CA206/301/302 原义务留缩小卡 |
| oracle S1–S4 sha 主张 | 4/4 复算命中（S3=115,984B、S4=500,372B 尺寸亦符） |
| 上游 16 份 `handoff.json`（15 链卡 + U14 历史） | **16/16 sha256 与 oracle §2.2 冻结表全中**；status：15×`accepted_scoped` + `I-16-B/a20260926-01`=`blocked`（历史，未丢弃）|
| `six_negatives_result.json` 编码 | BOM `FF FE`（UTF-16LE）实证；本工位以 utf-16 独立解码，与 `verification.json` 转写**逐字段一致**；原字节未动（5,486B 不变）|
| mtime 链 | oracle 09:30:30（冻结）→ run_six_negatives.py 09:38:30 → result/stderr 09:38:47 → final_report/handoff/verification 09:46:11（=verification `generated_at_utc 08:46:11Z`+01:00 ✓）。oracle 未在接手后被改 |
| 收尾复哈希 | 被审 7 件 + 上游 16 handoff 全部与基线一致（本报告 §6）；仅 `OWNER_DECISIONS.md` 在复审窗内被并行追加（见 §5） |

## 2. 五项全量复核

### 2.1 裁决行 + 发现清单

- 裁决行：handoff `status=review_pending`、`classification=blocked`、`blocking_primary="I-00-C 验收/关闭门负例缺口：9 例仅 3 拒（N1/N2/N4/N5 未拒）"` —— 与六负例实测一致（§2.2）。
- 发现清单：final_report 披露 4 项下一动作（关闭门补负例 / H2·STOP① 解封 / 周任务 T3 修复 / MSFT 10-K canonical 重名卡）与 handoff `next_actions` 一致；本卡新发现（验收门负例缺口）独立列为 blocked 第 5 项。**裁决与发现清单互洽。**

### 2.2 六负例判读复核（终审核心）——**判读正确**

逐例字段自核（对 UTF-16 原件独立解码，非采信转写）：

| 例 | rejected | 关键字段 | 判读 |
|---|---|---|---|
| N1_all_passed_but_no_evidence | false | `closure_ready=True unsatisfied=0` | **未拒 ✗**（无证据全过被放行）|
| N2_read10_wrong_capability_evidence | false | `closure_ready=True unsatisfied_ids=[]` | **未拒 ✗**（错能力证据被放行；脚本判拒需「非ready 且 deadline∈unsatisfied」，两条件皆不成立）|
| CTRL_read10_covering_capability | true* | `closure_ready=True (control, must be True)` | 对照例**如预期接受**（*字段语义反转，见 P3-6）|
| N3_stale_accepted_after_newer_fail | true | `verdict=changes_required`（旧 accepted 未胜出）| 拒 ✓ |
| N4_empty_commands | false | `closure_ready=True unsatisfied_ids=[]` | **未拒 ✗** |
| N5_empty_invariants | false | `closure_ready=True unsatisfied_ids=[]` | **未拒 ✗** |
| N45_both_empty（扩展）| false | 同上 | 未拒（扩展缺口）|
| N4b_receipt_layer_requires_commands（扩展）| true | `REQUIRED_BY_KIND[implementer]` 含 `commands` | 拒（回执层挡住，闭合层不挡——与 N4 不矛盾）|
| N6_original_obligations_still_pending | true | `pending=3`，CA-206/301/302 具名 | 拒 ✓ |
| N6b_narrowed_successor_flagged（扩展）| false | `narrowed_flagged=False` | 未拒（缩小后继未被标记——附加缺口）|

- 计数核：脚本 L235 `negatives`=全部 N 前缀例=9；`negatives_rejected`=N3+N4b+N6=**3** ✓；`all_six_rejected`=false ✓（按 9 例计，标签口径瑕疵见 P3-6，判定不受影响）。脚本 L264 未全拒⇒exit 3，与 blocked 结论一致。
- 实跑证据：组合三 sha（scenarios.py `524fc1e6…` / closure.py `952abfe0…` / registry `d25e6f06…`）**本工位现算与记录逐字一致**——六负例确在「当前有效组合」跑、且组合至今零漂移；`tmp/i17b_n3_*` 4 份回执（canonical_hash 链完整）与 `tmp/i17b_n6_*` legacy.json 及三个 root 夹具与脚本 L111–L215 逐字段吻合；`patch_gate_present=false` 与缺口方向自洽。
- 结论：**「验收/关闭门不能捕获 4/6 类负例」判读正确，负例缺口成立**；依卡文动作 2「缺真实场景/自然观察/证据映射必须继续阻断」与 oracle §4 冻结不变式（实测有未拒⇒如实 blocked，不改判据），本终审判 `blocked` **正确且 fail-closed**。**不构成 P1。**

### 2.3 六资格分类复核——**6/6 依据在案，分类成立**

| 资格 | 报告值 | 依据（在案核验） | 复核 |
|---|---|---|---|
| 来源获取 | 限域通过 | `I-16-B/a20260926-02`：`verification.json` 3×`"status":"capture_ready"` + `deployment_record.md:15`「已有复用 ✅ 3/3」实见 | ✓ `pass_scoped`≈`GRANTED_SCOPED`（oracle §6 允许值）；摄取 3 失败列为另开缺陷卡（下一动作④）|
| 数据湖/工件 | 通过（限域） | 同 run `r5_fullpath_result.json` / `recovery_drill.json` / `snapshot_manifest.json` 在案 | ✓（8191/R5 GREEN 数值未逐项深读，见 unverified）|
| 正式预测 | blocked | `I-12-A`/`I-12-BE` handoff `status=accepted_scoped`（与 oracle U9/U10 一致）；`params_released=false` 与本档一致 | ✓ blocked 合格形态；「四段全 blocked」内部细节未深读（上游只读 status 纪律）|
| 买方质量 | blocked | `I-13-BC/final_scorecard.json` **实测 `classification="research_draft_needs_review"`** | ✓ 非 ready，不授完成资格 |
| 准确性证据 | blocked（unproven 如实） | 同件含 `unproven`×20、**无任何 ready 值**（实测）；final_report/handoff 仅表述「未证明优于基准…不改写为提高」 | ✓ **合法准确性结论未被改写**（P1 项排除）|
| 持续服务 | blocked | `assurance/runs/weekly_manifest.json` `ok=false`（run 20260927T033001Z）；`weekly_alert.jsonl` 09-13/09-20/09-27 三连 `T3 suite exit 1`（两份日志根因一致：Playwright chromium 缺失，1 failed 3 passed）；`I-17-A/requirement_register.json` 在案；日报 `20260926T210002Z/report.json` checks **实测 =7** | ✓ blocked 有据（报告「两连败」指窗内 09-20/09-27，措辞保守，不影响判定）|

六格互不代偿、`accuracy` 用词未越三值域、无「提高」改写。**不构成 P1。**

### 2.4 五分类无掩盖核——**无掩盖；分列不完整（P3-4）**

- 全文检索「全部通过」：仅出现于动作 5 标题的**禁令引用**、oracle 卡文引用、verification M3 expectation——**无任何掩盖性使用**。
- blocked 独立成段：动作 5 列 5 项（正式预测/买方质量/准确性证据/持续服务/验收门负例缺口），与 handoff `five_categories.blocked` 一致；结论行以 blocked 收束。
- 缺陷：卡文动作 5 与 oracle A5 要求五分类**分列**，实际仅三桶——「限域通过」并入「已完成（限域）」（限域项在动作 3 表有区分）、「合理退役/NA」桶缺席且未显式计 0。**无掩盖效果，判 P3-4。**

### 2.5 变异三臂（只读自算等价复核）——**三臂实质成立；留痕缺失（P2-2）**

| 臂 | 记录 | 本工位等价自算 | 结果 |
|---|---|---|---|
| M2「ready 越权」rc=3 | 六资格表 accuracy=blocked unproven、非 ready | final_report 动作3表、handoff `six_qualifications`、`final_scorecard.json` 三处均无 ready 越权（§2.3 实测）| **检测性质成立** |
| M3「掩盖 blocked」rc=3 | 五分类含 blocked 独立段落 | §2.4 实测无掩盖措辞、blocked 独立成段 | **成立** |
| M1「上游清单缺卡」rc=0 | final_report 枚举 15/15 | 动作1表列 **14** 卡（I-07-B/C/D/E=4、I-10-A、I-11-B/C、I-12-A/BE、I-13-A/BC、I-16-A、I-16-B(-02)、I-17-A）+ I-00-C 于动作2/下一动作覆盖 = 15 链卡全有交待；U14 blocked 历史在 oracle §2.2 登记（本工位 16/16 sha 复算佐证）| **实质成立**；「15/15」对动作1表不精确 → P3-5 |

- **P2-2**：oracle §4 冻结变异计划为 MUT-1..4 + 校验器 `verify_i17b.ps1`（本目录）+「红绿均留 rc 原始输出」；实测该 .ps1 全树不存在、无任何 MUT 原始输出档，`verification.json.mutations` 以 M1/M2/M3 描述性记录替代（M2/M3 的 rc=3 属「若存在即拒」的反事实记法，与 §5 rc 语义表的对应无原始输出支撑；`red_green` 计数 bookkeeping 亦无档可对）。三臂实质已由本工位独立确认，故不升级 P1，但留痕不符合冻结计划 → **P2**。

## 3. 红线/封盘核

- 不放行参数：`params_released=false`（handoff+verification 一致）✓
- 不自签：`implementer_signed=false`，角色 `…_parent_completed`，待独立复审（本报告即该环节）✓
- 不代签/不解除：`releases_nothing=true`；被审档无任何 `OPEN/BLOCKED-*` 解除语句；上游 16 handoff 复哈希与冻结值全中＝状态未被动 ✓
- 封盘动：无——分类=blocked、四资格受限，未授予任何产品完成资格；`sealed_sha256 f2178768…` 获复审窗内账本新增段落交叉引用（§5），封存对象定义仍在档外（unverified）
- 写入面：attempt 目录内 7 文件 + `tmp/` 夹具，未越面；本复审写入面=2 新文件 ✓
- 禁 git 写 / 禁 `git status`：本工位未执行；被审档无 git 写痕迹（`git_diff_non_planning=0` 为其自报，本工位无法独立验证，见 unverified）

## 4. P 清单 + unverified

**P2**
1. **（必判）原工位 1e4ed02b 于六负例执行后、报告写作阶段崩溃，父会话接手补齐 final_report/verification/handoff**——handoff `implementation_note` 如实披露；mtime 链（09:38:47 → 09:46:11）与 oracle/六负例件为其原产出的事实自洽。
2. **变异臂留痕缺失**：oracle §4 冻结计划（MUT-1..4 + `verify_i17b.ps1` + 红绿原始 rc 输出）未落地，以 M1/M2/M3 描述性等价记录替代（§2.5）；实质经本工位独立确认成立，但留痕不符冻结计划。

**P3**
1. **（必判）`six_negatives_result.json` 为 UTF-16LE**（BOM FF FE，PowerShell 重定向编码缺陷）；父以 utf-16 解码转写，本工位独立解码比对**逐字段一致**，原字节未动。
2. handoff 登记 oracle sha 前缀 `43540638…` 与实测 `10523dade…` **不符**；mtime 链证明 oracle 未在接手后被改，属登记笔误（oracle 冻结性由内容自证：S1–S4 sha 全中）。
3. oracle §7 承诺在 `verification.json.source_hashes` 补录 S5/S6 sha——该字段不存在，S5/S6 无 sha 留痕（S1–S4 已复算命中）。
4. 五分类未逐项分列（三桶；「合理退役/NA」未显式计 0；限域通过并入已完成）——无掩盖效果。
5. M1 记录「final_report 枚举 15/15」与动作1表实列 14 卡不符（I-00-C 由动作2覆盖；U14 历史仅 oracle §2.2 登记，final_report 未重述）。
6. 脚本对 CTRL 例将 `closure_ready` 放入 `rejected` 字段（字段语义反转），final_report 转写「拒 ✓（对照例）」按字面可误读为「对照例被拒」；实义为对照例如期接受。`all_six_rejected` 按 9 个 N 例计（标签六、实九），判定不受影响。

**unverified（复审边界内未核，不影响判级）**
- I-12「四段全 blocked」内部细节（STOP① 未签 / 可评分 0 / 参数未放行的逐段证据）——上游只读 status 纪律。
- I-13-BC「14 模型 14/14=unproven」逐模型数值——分类值与「无 ready 值」已实测，数值未逐项核对。
- 复用 3/3 三个 `capture_ready` 凭证的字段级内容（3×status 已实见，字段未逐一核对）。
- `sealed_sha256 f2178768…` 的封存对象/算法无档内定义，无法复算（仅获账本交叉引用）。
- S3 `OWNER_DECISIONS.md` §三十四~§三十九、S4 `REMEDIATION_REGISTER.md` §157–§162 内容未逐节深读（sha 基线已命中）。
- 全仓 git 零写——`git status` 被禁，无法独立验证（无相反迹象）。

## 5. 复审窗内并行变更观察（A4 式留档，非被审件缺陷）

`OWNER_DECISIONS.md` 于 **2026-09-27 09:55:39（本地）被并行追加 +1,883 字节**（115,984 → 117,867B；sha `56c8992b…` → `a2e17c59…`），晚于被审 attempt 封存（09:46:11）。追加内容为新一段 owner 裁定（含「周任务 T3 两连败授权排查」「封盘 `f2178768…`」「`OPEN-6`/`BLOCKED-6a/6b/6c` 不解除」）。oracle S3 的 sha 主张在 oracle 运行时与本复审基线均命中，属历史快照有效；追加不触及被审件与上游 handoff（收尾复哈希证）。该并行写属账本正常演进，交由编排层在下一轮按 A4 重核受影响证据。

## 6. 哈希附录

被审件（收尾=基线，零变动）：

```
10523daded7c274cedc7eccf050789f400f886dad6a4b5ad837bbbfaf503eb82  oracle.md
9fea05b90bc0ccbbf50fb27ec36ce532adb33650cba71ab81c8b6cd8ee064c42  final_report.md
c732dee0192030c1752adeea6d98add15914dd9462949b3d184bed63f5ef9b03  verification.json
d7fa31c13bb46e5e8508bc3bb8157b4611a95bba63855c45b7fe0481b120fc70  handoff.json
d7dd97dc0b529a36286fb883f01568c6ed95903dc852d23784946d2691b13b80  six_negatives_result.json
660a56be68591005ad13f142c396644168690a24e905a3ae1552f9df236f2553  run_six_negatives.py
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  six_negatives_stderr.txt (0B)
```

上游 16 handoff、`card_I-17-B.md`、`card_I-00-C.md`、`REMEDIATION_REGISTER.md`：收尾=基线=oracle 冻结值（16/16 + 3/3）。`OWNER_DECISIONS.md`：见 §5。

## 7. 复审没做的事

不改卡状态（`review_pending` 未动）· 不解除任何 `OPEN/BLOCKED-*` · 无 git 写、未运行 `git status` · 未联网 · 未重跑六负例与变异臂（按任务为只读自算等价，且避免越出 2 文件写入面）· 未深读上游工位报告内容（仅 status/存在性/点名实测字段）· 未修改任何被审件。
