# reviewer_report.md — 对卡 **M-T-REVIEW / a20260923-01** 的独立复审（本卡自身的 own review）

- **复审对象**：`execution_runs/M-T-REVIEW/a20260923-01`（D9 修复审查机关：53 裁定 + 6 登记行 / M01–M31 + T1-\*）。
- **复审者**：父会话 `session-bfecd191-fbc3-4a66-8ed1-6562479bf102` 派单的**独立复审代理**（工具面 =
  read / grep / pwsh；未实现任何修复、未写本目录之外任何字节、零状态变更 git、零网络、零 harness）。**M-T-REVIEW 不自签本卡验收**
  （never self-sign）；本报告即其缺失的独立验收轮次。
- **本报告写入物**：仅 `reviewer_report.md` + `reviewer_report.sha256`（两件）。
- **词表**：house four-value map + BOOKKEEP-REPAIR D4 注记（与被审卡 oracle §1 同源）。

---

## 0. 复审判定（verdict）

**`accepted_with_conditions`（≡ accepted_scoped + carried）—— 交付级/记账级 carried，不动其 53 行矩阵的任何结论。**

- 其矩阵计数经我方**逐表重数**：M01–M20（20 行）+ M21–M31（11 行）+ T1 号（22 行）= **53 裁定**；
  `accepted_scoped` 12 / `accepted_with_conditions` 40 / `changes_required` 1（T1-10）/ `insufficient_evidence` 0；
  另 6 行 `not_applicable_with_reason` 登记（T1-3/4/9/11/12/28，不计入 53）。`decision.md` 与
  `acceptance_rulings.md` 两处计数一致，22 篇 reviews 全部带「独立审查员 M-T-REVIEW / N=1」签名行。
- **授权边界（scope-if-accepting）**：
  1. `landing_package/` 由父 landing 批次按其 `README.md` 安装（**追加不改 + 前缀哈希证明 + 只动
     `handoff.json.reviewer_status` 一键**），**且必须在本 ACCEPT 之后**执行；
  2. **T1-10 返修卡已另行派单**：`execution_runs/T1-10-FIX/a20260923-01`（其 oracle §0 明文引用本卡返修块
     `landing_package/t1_review_flips.md` L28–40，sha256 `90bcefb9aadfe098…` = 我方实测值，见 §5）；
  3. **F-MT-01 / F-MT-02 / F-MT-03 三项全队级发现 = VERIFIED**（§6），随本验收入册；
     **F-MT-02 的政策裁定由父登记**：内容基线的冻结证明（content-based freeze attestations：可逐字节重生成
     oracle.json + 生成器运行前 hash 落盘 + 记录态 mtime 序）+ **永久缺口注记**（现盘 mtime 序不可复验）；
  4. **D9 = CLOSED-via-this-agency pending install**：D9 的两件落槽已产出，待父按 README 安装后即闭合。
- carried（本复审新增，均不推翻结论）：**F-RV-01…F-RV-05**（§8）。

---

## 1. 交付面核验（deliverables）

| 项 | 声明 | 我方实测 | 判 |
|---|---|---|---|
| 冻结 oracle | `oracle.md` sha256 `ef68aaaf3e161dc0a88e35ef0503fc54336cd0bf1b4de650f090c3d16c851da9`，先于首检冻结 | 实时 `Get-FileHash` = **完全相同**；正文 §2 为四查点协议 + 固定抽样规则，§5 为判定边界，符合「先冻结后检查」形态 | ✅ |
| self_manifest | 45 文件 sha | 45 条逐条**实时重哈希 + 字节数复核：45/45 全中（0 失配）**；盘上 46 件 = 45 + `evidence/self_manifest.json` 自身（自引用不可入册，口径正常） | ✅ |
| reviews/ | M01..M20 + M21-31 表 + T1 表 + acceptance_rulings | 22 个文件（20 + `M21-M31_sampled.md` + `T1_rulings.md`），**22/22 有签名行**；`acceptance_rulings.md` 重数 = 53 + 6（见 §0） | ✅ |
| landing_package | 4 文件 + README 安装规则 | `README.md`（追加不改 / 字段对齐 / 权威出处三规则）、`review_flips_M01-M20.md`（**20 块**，块块 `status_authority` 形态）、`sampled_and_namecheck_M21-M31.md`、`t1_review_flips.md`（接受 12 + 带件 9 + 返修 1 + 登记 6 四形态） | ✅ |
| handoff | review_pending / unsigned / unmapped / unproven | `status=review_pending`、`reviewer_status="review_pending (own review …)"`、`blocked_by=[]`、`changes_required_cards=["T1-10"]`、`verdict_counts` 与我方重数一致；M 卡侧 `disclosure_adaptation=unmapped`、`accuracy=unproven` 在 M01/M09/M17 `qualification.json` 现盘复核成立 | ✅ |
| evidence/ | 8 件 + recovery/ | inventory / per_card_checks / clause_compare / hash_reattribution / pin_resolution / digests.txt / progress.md / self_manifest.json + `recovery/README.md` 全在册且入 manifest | ✅ |
| 关键 sha 抽核 | — | `acceptance_rulings.md` `257e47da…`（=manifest）、`t1_review_flips.md` `90bcefb9…`（=T1-10-FIX oracle 引值）、`review_flips_M01-M20.md` `19cb8862…` | ✅ |

---

## 2. 方法论抽查（核心）：5 卡四查点由我方**独立重做**

抽样卡：**M01**（mtime 记录矛盾 case）/ **M09**（`in_card_transcription_owed` 清账）/ **M17**（r2 态补验收）/
**T1-10**（changes_required）/ **T1-13**（accepted_scoped）。四查点 = (a) 冻结时序、(b) hash 抽点、
(c) 规格符合、(d) 证据一致性。**规格源说明**：M 卡的期望输出原文在 `execution_v2/model_cards.md`（31 处
`期望输出`）与其抽取件 `card_MXX.md`；`research_cards.md` / `root_cards.md` 为 I-11+ 与 I-00 系卡源、
**不含** M 卡期望行（我方 grep：两文件 `期望输出`=0、`direct_growth`=0）——被审卡引 `card_MXX.md` 正确。

### 2.1 M01 · `accepted_with_conditions` — **裁定成立（earned）**

- **(a) 冻结时序**：`evidence/M01/oracle.json` mtime **2026-09-20T14:52:13Z** < `stdout.txt` 14:52:14Z
  （现盘顺序成立）；但同目录 7 个 attempt 级文件全在 14:52:12–14:52:16 同批 ⇒ 属 09-20 批量重写后顺序。
  **记录态原值**：`review.md`「`oracle.json` mtime 01:18:24」+ `first_run_forensics.json`/`revision_r2.json`
  的 `mtimes_supporting_the_sequence`（01:15:15 / 01:18:22 / 01:18:24）——与 F-MT-02 的引值一致（见 §6.2）。
- **(b) hash 抽点**：handoff 键为非路径式（`evidence_input_json`/`evidence_oracle_json`/`evidence_cases_json`）。
  我方实测 raw：`8db050134ace…` / `92f8f6206b0f…` / `462ea30cfbb7…`（与 pin 的 pin 值均**不**等），
  **LF→CRLF 重序列化后 = `22910b38da85…` / `cb60e60d07c7…` / `0e1f55af5d4b…` 三者全中** ⇒ 3/3 CRLF；
  且我方 raw 值与其 `pin_resolution.json` 记录的 raw 值**逐字节相同**。iso `model_registry.py` =
  `9ec6529550f1…` == binding pin == 卡锚；`model_extensions.py` = `9939480b717d…`。
- **(c) 规格子句**：① `card_M01.md:31`/`model_cards.md`「手算：200×1.10=220；220×0.50=110；110×0=0。
  **期望输出：`[220,110,0]`**」== `oracle.json` 期望 `220,110,0` == handoff `positive_expected [220,110,0]` ✅；
  ② `negative_results.json` 11 案、`verdict` 全 `PASS_rejected`、异常全为 `ModelRegistryError`（nonTarget=0）✅；
  ③ A–C 九件（`card_M01.md:61` 清单）**9/9 在盘** ✅；④ `qualification.json` formula=`accepted_scoped`、
  disclosure=`unmapped`、accuracy=`unproven` ✅；⑤ `changes.diff` 无 `+++` 产品路径（1554 B，paths=[]）✅。
- **(d) 证据一致性**：`per_card_checks.json` 的 mtime/hash 记录与我方实测**同值**（含 `match:false` 原始不匹配
  如实记录）；golden-hash 族 21 pins 与其 review「21 pins」一致；`first_run_forensics.json`/`revision_r2/r3/r4`
  均在盘。
- **裁定 earned**：✅ 其 `accepted_with_conditions`（carried：F-MT-01/02/03 + M01-1 首冻 hash 永久缺口 +
  M01-2 双 r2 记账噪声）与我方独立复核一致；M01-1 的「永久缺口」在其 `open_questions` 原文在案，非新降级。

### 2.2 M09 · `accepted_with_conditions` — **裁定成立（earned）**

- **(a)** `oracle.json` 14:53:22Z < `stdout.txt` 14:53:23Z（同批重写序，F-MT-02 同限制）。
- **(b)** handoff 路径式 pin：`8d3bed650f26…`/`55fbc73fe250…`/`d0613d34d089…` **raw 直配 3/3**（LF 形态，
  `crlf_only_count=0`）+ `scripts/oracle_cards_M09_M12.py` `54f3cdb1…`、`run_card.py` `997c553b…` raw 中。
  ⇒ 与「M09–M16 pin 为 LF 形态直配」的分族声明一致。
- **(c)** ① `card_M09.md:33`「30×4+2=122。期望输出 `[122]`」== oracle `122.0` == handoff `positive_expected
  [122.0]` ✅；② 11/11 全拒 ✅；③ 九件 9/9 ✅；④ formula `accepted_scoped` / `unmapped` / `unproven` ✅；
  ⑤ `changes.diff` 无产品路径 ✅。
- **(d)** 其所引既有终裁载体 **实测相符**：`evidence/M09/reviewer_report_m09m12.md` sha256 =
  `5a44fd4e1e4dca5f8ad06d17fc759154741a6a22469145a837bcdf1615d21c4c`、**40679 B**，与其 review 及
  `status_authority.carrier` 声明**完全相同**；`qualification.json`/`handoff` 中
  `in_card_transcription_owed=true` 现盘在案（F-MT-04 属实）；golden pins 24 == review「24 pins」。
- **裁定 earned**：✅（carried = F-MT-02/03/04；卡内裁决区补录由 flip 块闭合，见 §3）。

### 2.3 M17 · `accepted_with_conditions` — **裁定成立（earned）**

- **(a)** `oracle.json` 14:54:46Z < `stdout.txt` 14:54:52Z（同批）。
- **(b)** raw `5b157a342189…`/`c868cf7d6b18…`/`e09bdc8938f1…` 均≠pin，**CRLF 重序列化后 =
  `9bb97f5f69af…`/`8dbcece9b1ae…`/`0af2f9f15712…` 三中**；`scripts/oracle_M17.py` `495573f9…`、
  `run_card.py` `94619a98…` raw 中；iso == `9ec65295…`。
- **(c)** ① `card_M17.md:39`「40×2+15+5+10=110。期望输出 `[110]`」== oracle `110.0` == handoff `[110.0]` ✅；
  ② 11/11、期望比较为**精确类型名**（非 isinstance）✅；③ 九件 9/9 ✅；④ 三栏纪律 ✅；⑤ `changes.diff` 无
  产品路径 ✅。
- **(d)** 其 review/handoff 引的**裁定块字节范围**：`review.md` [32643,42998) 10355 B 我方切片重哈希 =
  `e383f5e89bd6737fe520bdb3b0f4bd01fc517cfd17a326564db06ea60b39c248` —— 与声明**完全相同**；批载体
  `M17-M20/a20260919-01/transcription_proof_batch_r3.json`（1181 B）、`final_validation_after_r3_accepted.txt`
  （2498 B）**在盘**（其 review 所引）；`reviewer_status`「formula remains review_pending until the reviewer
  confirms the r2 fixes」 vs `handoff.status=accepted_scoped` ⇒ **F-MT-05 矛盾现盘属实**；golden pins 22 == 22。
  ⚠ 新见（非其 review 所引）：M17 卡自身 `byte_equality_proof_sha256=6096771a…` 与现盘
  `transcription_proof_r3.json`= `9d21f855…` **不符** ⇒ 记 **F-RV-04**（他卡记录，另行登记）。
- **裁定 earned**：✅（carried = F-MT-01/02/03/04/05；r2 态由本卡补足独立验收的主张成立）。

### 2.4 T1-10 · **`changes_required` — 裁定成立（earned，非捏造）**

- **(a) 时序**：`run_a/run_b` 22:18:07/22:18:24Z → `t1_10_defect_verification.json` 22:33:50 →
  `decision.md` 22:34:19 → `append_only_proof_round57.json` 22:36:14 → `handoff.json` 22:36:18（先测后判，
  序合理；同为 09-20 批）。
- **(b) hash 抽点**：`t1_10_defect_verification.json` 实测 `22ead5c549311ace…` == 其 `decision.md` 自记
  「连跑 4 次同哈希 `22ead5c5…`」；`handoff.json`/`decision.md` 在盘且内容可解析。
- **(c) 规格子句（owner 裁定原文 3–5 条）**：`decision.md` 的逐字引用 == `OWNER_DECISIONS.md:216`
  （§13 T1-10 行）**逐字相同**：① 授权立卡修复 ①`claim.basis` 枚举校验 ②union/sum 计入 quick_check
  并以**追加式 provenance** 更正期望、**不回改冻结正文**。核对：②已修（`W1 union_seconds` 新 1740 /
  `expected_superseded` 保留 2220）✅；**① 非全函数 = 未闭合** ✅。
- **(d) 缺陷真实性（我方独立核）**：
  - `I-14-B/a20260919-01/iso/natural_window.py` 中 `BASIS_REGISTRY = { … }` **确为 set**；同族变异件名
    `MUT-15-J16-basis-enumeration.py` 证实 **J16 = basis 枚举守卫**；
  - `t1_10_defect_verification.json` 实测：`basis=["union_of_registered"]`/dict → **rc=4、无报告、
    `internal_error: unhashable type: 'list'`**；标量五探针（未登记串/空串/null/非串标量）5/5 行 rc=0 +
    `reject_claim`/`R-BASIS-UNKNOWN`；**爆炸半径臂 A（13 例）0 裁决 vs 臂 B（13 例）13 裁决**、
    跨 class 臂 C 亦然；`overall=PASS`、`failed_propositions=[]`、P-3/P-4 命题 `holds=true`。
  - ⇒ 「畸形 basis 可炸 J16 整个裁决机关、护栏成单点故障」**为真**，非被审卡捏造。
- **裁定 earned**：✅ `changes_required` 成立（与其矩阵中唯一 changes_required 行一致）；返修要求已成块
  （`t1_review_flips.md` L28–40）并**已被 `T1-10-FIX/a20260923-01` 引为修复源**（sha 吻合）。

### 2.5 T1-13 · `accepted_scoped` — **裁定成立（earned）**

- **(a)** `decision.md` 19:05:45 → `handoff.json` 19:06:24 → `t13_changes.diff`/`t13_line80_verification.json`
  19:08:01（同批；终检件在 handoff 后 95 s 落盘 = 收尾定稿形态，如实记，不构成冻结序问题——T1 卡无产品 run）。
- **(b)** `t13_line80_verification.json` 实测 `5f97d54fc778de95…` == 其 review 引值 `5f97d54f…`；
  `t13_changes.diff` 在盘（`6f513476…`）；handoff 含 `hashes`/`boundaries` 键。
- **(c)** `decision.md` 的逐字引用 == `OWNER_DECISIONS.md:219`（§13 T1-13 行）**逐字相同**，三边界
  （只改出处列 / 不动数值 / 不动其余字节）+ 前像 hash + diff 齐。
- **(d)** `t13_line80_verification.json`：`overall=PASS`，B-1…B-4 全 `holds=true`（`all_hold=true`）——
  仅第 [2] 格（出处列）变、指标格字节相同且数字多重集不变、仅第 80 行变且行数 300==300、前像带 errata R-1
  声明的缺陷 ⇒ 与「卡内自纠一次判据错误并如实登记」的自述相容；`handoff.status=planned` = 实现者未自签，
  独立验收即本裁定。
- **裁定 earned**：✅。

**5/5 抽查裁定均成立；未发现虚报 pin、虚报子句或虚报证据。**

---

## 3. M01–M20 矛盾闭合核验（要求 ≥3 卡，我方实测 7 卡）

`handoff.status=accepted_scoped` 与 review.md/reviewer_status 的 `review_pending` 并存，现盘逐卡：

| 卡 | handoff.status | reviewer_status 关键句 | review.md `review_pending` 命中 |
|---|---|---|---|
| M05 | accepted_scoped | 「returned for point review」 | 2（含「Status after r2: `formula` = review_pending (point review of r2)」原文） |
| M06 | accepted_scoped | 同上 | 2 |
| M07 | accepted_scoped | 同上 | 2 |
| M17 | accepted_scoped | 「formula remains review_pending until the reviewer confirms the r2 fixes」 | 5 |
| M18 | accepted_scoped | 同上族 | 6 |
| M19 | accepted_scoped | 同上族 | 5 |
| M20 | accepted_scoped | 同上族 | 5 |

**7/7 属实**（≥3 达标）⇒ F-MT-05 矛盾主张成立。

**翻转块能否真正闭合**（读 `landing_package/review_flips_M01-M20.md` 的 BLOCK M05 / M17）：

- `status_authority` 形态齐：`{ status, reviewer_status, carrier, implementer_signed:false, supersedes }`；
  `supersedes` 精确指向矛盾源（`"review_pending (point review of r2)"` / `"review_pending (r2 fixes awaiting
  reviewer)"`），`status=accepted_scoped` 与现值一致 ⇒ 按 README 规则**只动 `reviewer_status` 一键**即可闭合、
  不需回改任何裁决字节 ⇒ **矛盾可被闭合**；
- carrier pin：块顶总则指向 `../evidence/self_manifest.json`（`reviews/<卡>.md` + `acceptance_rulings.md`
  的 sha 已封印，我方 45/45 重验通过）——但**块内未逐块引 sha**（README 写「块内引 sha256」）⇒ 记 **F-RV-02**；
- `verdict_is_transcribed` 旗标期望：块内有 `implementer_signed:false` 与「本块即 owed 的卡内裁决区补录
  （追加式，附前缀哈希证明）」的散文，但**无** AUDIT-INTEGRITY 载体 schema 使用的显式
  `verdict_is_transcribed_not_authored` 键 ⇒ 记 **F-RV-03**（父安装时补记该键即可，非阻断）。
- **结论：闭合机制成立**（append-only + prefix proof + 单键对齐），两处形式性缺口入 carried。

---

## 4. M21–M31 终裁存在性（11/11）— 我方自 grep + 自重哈希

- `review.md` 内 `accepted_scoped` 命中数 + `handoff.status`（我方实测）：M21 ×3 / M22 ×3 / M23 ×3 /
  M24 ×2 / M25 ×3 / M26 ×3 / M27 ×3 / M28 ×3 / M29 ×2 / M30 ×2 / M31 ×2，**11/11 `handoff.status=accepted_scoped`**
  ——与其 `reviews/M21-M31_sampled.md` 表一**逐格相同**。
- **点名 sha 重哈希（要求的 5 个 + 附带 5 个，10/10 全中）**：
  `05f5fe10d42b12ec…`→M22 `verdict_transcription_check.txt` ✓；`bd76f1053438da80…`→M23 ✓；
  `5ff449274be8f840…`→M24 ✓；`58e614d533e6be73…`→M29 ✓；`dfb854b4cc085b76…`→M30 ✓；
  另 `aee6d601c2c44e59…`(M21)、`c57d50061510e548…`/`f41b2fc71f8b7605…`(M31 双证)、
  `4ff7a53b7a999974…`/`a0992cfea58efad5…`(M29/M30 确认件) 全部命中实际文件。
- ⇒ **支持（不是反驳）AUDIT-DESIGN 更正后的普查**：`AUDIT-DESIGN/…/audit_report.md:120` 与 `:179` 的更正口径
  =「M21–M31 终裁在案（经事故记录佐证）、**M01–M20 独立验收载体未定位 ⇒ D9 UNVERIFIED**」。本卡把缺口面
  **恰好限定在 M01–M20** 并逐卡补齐，M21–M31 只抽验不改写 —— 范围裁定正确。

---

## 5. T1 矩阵核验

- **22 号裁定面**：T1-1/2/5/6/7/8/10/13/14/15/16/17/18/19/20/21/22/23/24/25/26/27 = 22 ✓；6 个 owner
  裁决号仅登记 ✓（与 `OWNER_DECISIONS.md:209/210/215/217/218/234` 的「暂不签/已落地闭合/暂不授权/不授权/
  规则采纳/全部维持」逐条对得上）。
- **引 sha 抽 6（我方全部命中）**：
  | 引值 | 落点 | 实测 |
  |---|---|---|
  | `f93a1832…` | `T1-1-T1-2/a20260920-01/t1_1_t1_2_verification.json` | `f93a183232e77216…` ✓ |
  | `2cd7efa9…` | `T1-6/…/t16_verification.json` | `2cd7efa92d9ea4e4…` ✓ |
  | `a6353411…` | `T1-7/…/t17_ruling_landing.json` | `a6353411b4fddb65…` ✓ |
  | `5f97d54f…` | `T1-13/…/t13_line80_verification.json` | `5f97d54fc778de95…` ✓ |
  | `252d2b34…` | pdftotext.exe 注册值（T1-14 引「入 binding」） | 出现于 `t14_register_verification.json`
  的 `registered_sha256=252d2b345662ba6d…`（64-hex、路径绝对、P-1 holds）✓ |
  | `4231bf05…` | `T1-23-T1-25/…/t1_23_t1_25_verification.json` | `4231bf052deecc88…` ✓ |
- **T1-10 返修块**：`landing_package/t1_review_flips.md` L28–40 存在、sha256 `90bcefb9aadfe098…`，
  且 `T1-10-FIX/a20260923-01/oracle.md` §0 **逐字引用该块与其 sha** ⇒「修复卡另行派单」属实、可引证。

---

## 6. 三项全队级发现：**逐项 VERIFIED / NOT**

### 6.1 F-MT-01（CRLF 形态 pin vs LF 盘面）— **VERIFIED**

- 我方独立按「raw vs LF→CRLF 重序列化」复算：**M01 3/3 仅 CRLF 中 + M17 3/3 仅 CRLF 中（合计 6 个 pin ≥ 要求的 2 个）**
  + M09 3/3 raw-LF 直配；iso/脚本类 pin raw 中 ⇒ 「全队 pin 为 CRLF 形态、盘上 LF、分族直配」成立。
- **唯二例外的账本**：`pin_resolution.json` 31 卡中 `all_pins_reproduced=false` **恰为 M08、M13 两卡**
  （其 `cases.json` raw 与 CRLF 均≠pin）；账本实证：
  - M08：`evidence/M08/docfix_r3.json` 内含前像 `e6c36cf4c3cc…` 与新值 `57459a8f…`（另见
    `recovery/docfix-r3/`、`source_manifest.json`）；
  - M13：`evidence/M13/cases_annotation_repack.json` 内含 repack 前 `0353e544234e…` 与新值 `54399cd2…`，
    且前像文件 `recovery/before_fixes/cases.json` **在盘**。
- ⇒ 「100% 复现，唯二例外为**已登记的注释性 repack**」**成立**。

### 6.2 F-MT-02（mtime 冻结序灭失）— **VERIFIED**

- 记录态：M01 `review.md`「`oracle.json` mtime **01:18:24** 早于 r2/r3 两轮修订」；
  `first_run_forensics.json`/`revision_r2.json` 记 01:15:15 / 01:18:22 / 01:18:24 序列。
- 现盘：M01 `evidence/M01/oracle.json` mtime = **2026-09-20T14:52:13Z**（与 F-MT-02 引值 14:52:13 相同）；
  M09 14:53:22Z、M17 14:54:46Z，各卡 attempt 级文件同分钟批量 ⇒ **原始冻结序在现盘不可复验**，
  T1-24 第三腿只能以记录态 manifest 为凭 —— 与该发现主张一致。
  （附注：`first_run_forensics.json` 把 01:18:24 归给 `stderr.txt`，`review.md` 归给 `oracle.json` ——
  M01 自身记录的小出入，记 **F-RV-05**，不动 F-MT-02 实质。）
- **政策处置（父登记）**：内容基线的冻结证明（逐字节可重生成 + 生成器运行前 hash + 记录态 mtime 序）
  + **永久缺口注记**（现盘 mtime 序不可复验，不得以现盘顺序充当事前冻结证据）。

### 6.3 F-MT-03（`model_registry.py` 锚漂移）— **VERIFIED（含 git 佐证）**

- 现盘 RF 生产：`scripts/model_registry.py` sha256 = **`62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081`**
  （= 其声明的 production_now）；`model_extensions.py` = `9939480b717d…`（未变）。
- git（**只读** `cat-file blob` + 内容 sha256）：
  | commit | 日期 | `scripts/model_registry.py` 内容 sha256 |
  |---|---|---|
  | `69df60d6` | 2026-07-13 | `cdf2e4c7…` |
  | `4a8b454e` | 2026-07-25 | `1f2639e1…` |
  | **`5db4734a`** | **2026-09-20**（owner-authorized 纳管） | **`9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f` = 全部被审卡的锚** |
  | **`5fd82de7`** | **2026-09-22**（promote B-6c，提交信息自带 `62f864b9`） | **`62f864b9…` = 现盘值** |
- ⇒ **9ec65295 = 晋升前锚（旧版内容）、62f864b9 = 晋升后现值**，漂移发生在 2026-09-22，**晚于全部被审
  attempt（09-19/09-20）** —— 发现的时点与定性均成立；「复跑须显式重新锚定」的边界随之成立。

---

## 7. 边界核验（boundary）

| 断言 | 我方实测 | 判 |
|---|---|---|
| RF/plan/旧 attempt 未被本卡写入 | `git status --porcelain`（只读）：M01–M31 / T1-\* / 三个批目录 **0 条修改**；tracked 修改仅 3 处、均属并发兄弟卡（B1-I08C handoff、I-14-F-R1 review、RF-STEP9-TRIAGE oracle）；`?? M-T-REVIEW/`、`?? T1-10-FIX/` 为新建未跟踪目录 | ✅ |
| 交叉佐证（不依赖 git） | 全部被审/批 attempt 中 **mtime ≥ 2026-09-23 的文件 = 0**；本卡 46 件自身 mtime 全在 09-23 22:38–23:26 | ✅ |
| 「未跑任何 harness」 | `commands.json`：**0** 处 `git`/`python`/`pytest`/`run_card`/网络命令，明记 read-only；attempt 树**无** `rc.json`/junit/`stdout.txt`/`stderr.txt`/`.pyc` 等 run 产物；`scripts/` 仅 5 个 `.ps1` | ✅ |
| 零状态变更 git | 本复审自身亦仅用 `status`/`log`/`cat-file blob`/`rev-parse`/`hash-object`（全部只读），无 add/commit/checkout/stash | ✅ |
| self-manifest 完整 | 45/45 重哈希 + 字节全中（差集 = 仅其自身，见 §1） | ✅ |
| 本复审写入面 | 仅 `reviewer_report.md` + `reviewer_report.sha256` | ✅ |

---

## 8. 本复审新增发现（carried，均不推翻被审卡结论）

| ID | 级 | 内容 | 处置 |
|---|---|---|---|
| **F-RV-01** | P3 记账 | **中间机检层与终稿自述不一致**：`clause_compare.json` 对 M01/M09/M17 记 `exp_ok:false`（`oracle_expected_float:null`，提取器路径错）、M09/M17 记 `hash_missing_pin:true`、`per_card_checks.json` 记 `pin_present:false`、`qual:""`；而**终稿 review 所据的 `pin_resolution.json` 与我方独立复算均为真**（引值与实测逐项相符）。⇒ `clause_compare`/`per_card_checks` 的 exp/hash/pin 字段**不得**被后续引用为裁决依据 | 登记勘误（追加式注记），引用面固定为 `pin_resolution.json` + 本报告 |
| **F-RV-02** | P3 交付 | `landing_package/README.md` 称「块内引 sha256」，实际 20 块仅在**文件顶总则**指向 `../evidence/self_manifest.json`（pin 可得、已 45/45 复核），块内无逐块 sha | 父安装时按 manifest 补记每块载体 sha（一行即可），不改块体 |
| **F-RV-03** | P3 形式 | 翻转块 `status_authority` 缺显式 `verdict_is_transcribed_not_authored` 键（AUDIT-INTEGRITY 载体 schema 用键）；现以 `implementer_signed:false` + 前缀哈希证明条款承担同一语义 | 父安装时补记该键 |
| **F-RV-04** | P2 他卡记录 | **M17 卡自身**声明 `byte_equality_proof_sha256=6096771a…`，现盘 `evidence/M17/transcription_proof_r3.json`= `9d21f855…`（不符）；但其**裁定块本体**字节范围哈希 `e383f5e8…` 我方切片复算**完全吻合** ⇒ 属证明件自身被重写/重记的记录漂移，非裁决字节问题 | 单独登记，交 M17 系/落定批次核销（不在本卡欠账内） |
| **F-RV-05** | P3 他卡记录 | M01 `first_run_forensics.json` 把 01:18:24 归给 `stderr.txt`，`review.md` 与 F-MT-02 引文归给 `oracle.json`（同秒双归属） | 追加式注记；F-MT-02 实质不受影响 |

---

## 9. 未做 / 未验证（unverified，如实划界）

1. **48/53 张卡的四查点未逐卡重跑**：我方深做 5 卡（§2）+ M21–M31 存在性与 10 个 sha（§4）+ T1 六 sha（§5）+
   三项全队发现（§6）；其余裁定行的支撑 = 其机检证据在册、入 manifest 封印、抽核层与其自述一致 —— 属
   sampled-verification 语义，非全量复算。
2. **M08「117/117 前存叶子零改动」未逐叶复算**：我方核到账本文件与前后像 sha 在案（§6.1），未重算全部叶子。
3. **T1-5「commit-green」未复跑**（其 review 亦如实声明未复跑并 carried）；本复审同样不跑任何 harness。
4. **CRLF 批量重写的「写者」未取证**：09-20 ~14:52 UTC 同批 mtime 为强旁证，但本复审未做取证级归因。
5. **M25–M28 的 r2 块行号区间未逐块切片重哈希**（其点名形态为「M25 族」引用，无逐卡 sha）；我方仅核
   `review.md` 终裁在场 + `handoff.status`。
6. **网络**：无法从盘面证明历史无网络调用；仅能证 `commands.json` 无网络命令、无网络产物。
7. F-RV-04 所涉 M17 证明件漂移的**根因**未查（超出本卡面）。

---

## 10. REM-79 自检

- 工具：`execution_runs/REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py`
  （stdlib、`exit 0/1`）；运行方式 `PYTHONIOENCODING=utf-8 python <tool> reviewer_report.md`。
- 结果（本文件实跑）：首轮 2 检出（L4 工具列句 `[only]`、L125 中文数词句 `[全部]`）→ 依 REM-79 口径改写为
  同句域形态后复跑：**0 violation(s) / rc=0**（域：本报告单文件、checker v1.2.0-correction2）。
- 本报告写作口径：全称句均带**同句域**（卡号枚举 / 计数 / 路径），与 REM-79「结论句必须带域」一致。

---

## 11. 总签

**裁定：`accepted_with_conditions`（≡ accepted_scoped + carried）—— 对 `M-T-REVIEW / a20260923-01` 的
独立验收成立；其 53 行矩阵（含唯一 `changes_required` = T1-10）与三件全队级发现（F-MT-01/02/03）经本复审
抽验后维持。** D9 = **CLOSED-via-this-agency pending install**；`landing_package/` 仅在本 ACCEPT 之后由父按
README 安装（append-only + prefix proof）；T1-10 返修走已派单的 `T1-10-FIX/a20260923-01`；F-MT-02 政策
裁定（content-based freeze attestations + 永久缺口注记）由父登记。
**未授予**：任何 D/E/F、真实公司适配、准确性、外推；本复审亦不代被审卡签任何超出其词表的状态。

— **独立复审代理（父会话 `session-bfecd191-fbc3-4a66-8ed1-6562479bf102` 派单），2026-09-23**
（被审卡 M-T-REVIEW 不自签本卡验收；本签名即其 own review 落点。）
