# review.md — M-T-REVIEW / a20260923-01 的独立验收落卡（own review 结果转录）

> 本卡是审查机关卡，**永不自签本卡验收**（never self-sign）。本文件 = 对本卡 own review 裁决的**转录**
> （verdict_is_transcribed_not_authored: true），裁决文字出自父会话 `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`
> 派单的独立复审代理，载体 = `reviewer_report.md` + `reviewer_report.sha256`。

## 0. 裁决块（verdict block · 转录）

- **裁决：`accepted_with_conditions`（≡ `accepted_scoped` + carried）—— 交付级/记账级 carried，其 53 行矩阵的
  任何结论均不改动。**
- 载体（carrier）：`reviewer_report.md`，27477 B，sha256
  `6aedddcc029922f348fdf36a0c67eeb11872fe9a687fe97940094e4fd7e10467` —— 本落卡实测 `Get-FileHash` 与
  `reviewer_report.sha256` sidecar 行（64-hex + 文件名）**完全一致**；sidecar 自身 85 B。
- 复审人：父会话派单的**独立复审代理**（工具面 read / grep / pwsh；零修复、零状态变更 git、零网络、零 harness）；
  **N = 1**；本卡不代其签、其不代本卡签。
- 字节范围锚（本落卡实算 UTF-8 byte offset，总 27477 B）：
  - verdict 段 `## 0. 复审判定` → `## 1.` = **[816, 2560)**；
  - 授权边界段（scope-if-accepting，`**授权边界` → carried 行）= **[1470, 2468)**，其中 D9 条起 2344；
  - F-RV 发现段 `## 8.` → `## 9.` = **[22776, 24719)**（表体起 22899）；
  - unverified 段 `## 9.` → `## 10.` = **[24719, 25929)**（条目 1–7 起 24776/25116/25265/25397/25530/25718/25842）；
  - 总签段 `## 11.` → EOF = **[26554, 27477)**。
- handoff 预像（本落卡实测，改前）：`status = review_pending`；`reviewer_status = "review_pending (own review of
  this review follows per dispatch: matrix contains changes_required)"`；**unsigned**（`status_note` 自记 own review
  另行）；`blocked_by=[]`；`changes_required_cards=["T1-10"]`；handoff.json 改前 sha256 =
  `665990aadc526595b1cb6798e7140abe4f91c3da48ac0a17b22848ac082d4e06`（5505 B，= self_manifest 记载值）。
- `verdict_is_transcribed_not_authored: true`；`implementer_signed: false`；supersedes =
  `review_pending (own review … matrix contains changes_required)`。

## 1. 关键核验（own review 实测，逐项转录）

1. **self_manifest 45/45**：45 文件 sha256 + 字节数逐条实时重哈希全中（0 失配）；盘上 46 件 =
   45 + `evidence/self_manifest.json` 自身（自引用不入册，口径正常）。
2. **计数 53 + 6**：M01–M20（20）+ M21–M31（11）+ T1 号（22）= **53 裁定**；
   `accepted_scoped` 12 / `accepted_with_conditions` 40 / `changes_required` 1（T1-10）/ `insufficient_evidence` 0；
   另 **6** 行 `not_applicable_with_reason`（T1-3/4/9/11/12/28，不计入 53）。`decision.md` 与
   `acceptance_rulings.md` 两处计数一致（`acceptance_rulings.md` 实测 sha256 `257e47da…` = manifest 值）；
   22 篇 reviews 全带「独立审查员 M-T-REVIEW / N=1」签名行。
3. **5/5 抽查裁定 earned**（含 pin 复现形态事实）：
   - **M01**：raw 三 pin ≠ pin 值，**LF→CRLF 重序列化后 3/3 全中**（`22910b38…`/`cb60e60d…`/`0e1f55af…`），
     且 raw 与 `pin_resolution.json` 记录逐字节相同；iso `9ec65295…` == binding == 卡锚；期望 `[220,110,0]` 三方一致；
     负例 11/11 全 `ModelRegistryError`；九件 9/9。
   - **M09**：路径式 pin **raw 直配 3/3（LF 形态，`crlf_only_count=0`）**；引既有终裁载体
     `reviewer_report_m09m12.md` sha256 `5a44fd4e…`、40679 B 实测相符；`in_card_transcription_owed=true` 在案。
   - **M17**：raw ≠ pin，**CRLF 重序列化 3/3 中**（`9bb97f5f…`/`8dbcece9…`/`0af2f9f1…`）；裁定块字节范围
     `[32643,42998)` 切片重哈希 = `e383f5e8…` 完全吻合（本落卡独立复算确认）；F-MT-05 矛盾现盘属实。
   - **T1-10**：`changes_required` earned 非捏造 —— `t1_10_defect_verification.json` 实测 `22ead5c5…` == decision.md
     自记 4 次同哈希；`decision.md` 逐字引用 == `OWNER_DECISIONS.md:216`；缺陷②已修（1740 / `expected_superseded`
     保留 2220）、① 非全函数未闭合；独立核：`BASIS_REGISTRY` 确为 set、J16=basis 枚举守卫、畸形 basis
     rc=4 无报告 `unhashable type: 'list'`、爆炸半径臂 A 13 例 0 裁决 vs 臂 B 13 例 13 裁决。
   - **T1-13**：`t13_line80_verification.json` 实测 `5f97d54f…` == 其 review 引值，`overall=PASS`、B-1…B-4 全
     `holds=true`；`decision.md` 引用 == `OWNER_DECISIONS.md:219` 逐字；`handoff.status=planned`（实现者未自签）。
4. **7/7 矛盾 + 翻转块闭合**：M05/M06/M07/M17/M18/M19/M20 逐卡现盘复核（handoff.status=accepted_scoped vs
   reviewer_status/review.md 的 `review_pending` 关键句，本落卡 grep 复核 7/7 属实，review.md 命中数
   2/2/2/5/6/5/5）；读 `landing_package/review_flips_M01-M20.md` 的 BLOCK M05/M17 确认
   `status_authority` 形态齐、`supersedes` 精确指向矛盾源、`status=accepted_scoped` 与现值一致 ⇒
   **按 README 只动 `reviewer_status` 一键即可闭合、不回改任何裁决字节 ⇒ 矛盾可被闭合**（安装实测见 §4）。
5. **11/11 M21–M31 + shas**：review.md `accepted_scoped` 命中 + `handoff.status` 实测 11/11 =
   `accepted_scoped`，与其表一逐格相同；点名 sha 重哈希 10/10 全中（`05f5fe10…`M22 / `bd76f105…`M23 /
   `5ff44927…`M24 / `58e614d5…`M29 / `dfb854b4…`M30 + `aee6d601…`M21 / `c57d5006…`+`f41b2fc7…`M31 双证 /
   `4ff7a53b…`+`a0992cfe…`M29/M30 确认件）；支持 AUDIT-DESIGN 更正口径：缺口面恰好限定 M01–M20。
6. **6/6 T1 引 sha + T1-10 fix-card 引证**：`f93a1832…`(T1-1/2) / `2cd7efa9…`(T1-6) / `a6353411…`(T1-7) /
   `5f97d54f…`(T1-13) / `252d2b34…`(T1-14 `registered_sha256`，64-hex 路径绝对) / `4231bf05…`(T1-23/25) 全命中实际文件；
   T1-10 返修块 `landing_package/t1_review_flips.md` L28–40 sha256 `90bcefb9aadfe098…` 且
   `T1-10-FIX/a20260923-01/oracle.md` §0 逐字引用该块与其 sha ⇒ 修复卡另行派单属实。
7. **F-MT-01/02/03 = VERIFIED**：
   - **F-MT-01**：独立按 raw vs LF→CRLF 复算 = M01 3/3 仅 CRLF 中 + M17 3/3 仅 CRLF 中（6 pin ≥ 要求 2）
     + M09 3/3 raw-LF 直配；`pin_resolution.json` 31 卡中 `all_pins_reproduced:false` 恰 **2** = M08、M13
     （本落卡复核计数=2），账本在案：M08 `docfix_r3.json` 含前像 `e6c36cf4c3cc8e6e…` 与新值 `57459a8f5ea298e1…`
     （`recovery/docfix-r3/` 在盘）；M13 `cases_annotation_repack.json` 含 `0353e544234eb8ea…`→`54399cd26596421e…`
     且前像 `recovery/before_fixes/cases.json` 在盘（四值本落卡全部实读命中）。
   - **F-MT-02**：记录态 M01 `review.md`「`oracle.json` mtime 01:18:24 早于 r2/r3」+ forensics/revision_r2 序列
     01:15:15/01:18:22/01:18:24 在案（本落卡实读）；现盘 mtime 已批量重写（M01 14:52:13Z / M09 14:53:22Z /
     M17 14:54:46Z，attempt 级文件同分钟批）⇒ **原始冻结序现盘不可复验**，T1-24 第三腿以记录态 manifest 为凭。
     政策裁定（父登记）：content-based freeze attestations（可逐字节重生成 + 生成器运行前 hash 落盘 + 记录态
     mtime 序）+ **永久缺口注记**（现盘 mtime 序不可复验，不得充当事前冻结证据）。
   - **F-MT-03**：现盘生产 `scripts/model_registry.py` = `62f864b9ab3f144e…`；只读 git 佐证表：
     `69df60d6`(07-13) `cdf2e4c7…` → `4a8b454e`(07-25) `1f2639e1…` → **`5db4734a`(09-20 owner-authorized)
     `9ec65295… = 全部被审卡的锚`** → **`5fd82de7`(09-22 promote B-6c) `62f864b9… = 现盘值`** ⇒ 漂移晚于全部被审
     attempt；「复跑须显式重新锚定」边界成立。
8. **边界（boundary）**：`git status --porcelain`（只读）M01–M31 / T1-* / 三批目录 **0 条修改**（tracked 修改仅
   3 处、均属并发兄弟卡）；`?? M-T-REVIEW/`、`?? T1-10-FIX/` 为新建未跟踪；全部被审/批 attempt 中
   mtime ≥ 2026-09-23 的文件 = **0**；`commands.json` 0 处 git/python/pytest/run_card/网络命令、无 run 产物；
   本复审写入面 = 仅 `reviewer_report.md` + `reviewer_report.sha256` 两件；self-manifest 45/45 重哈希 + 字节全中。

## 2. F-RV-01…F-RV-05 处置（carried，均不推翻结论）

| ID | 级 | 内容 | 处置 |
|---|---|---|---|
| F-RV-01 | P3 记账 | `clause_compare.json` 记 `exp_ok:false`（本落卡复核 31/31 行）、`hash_missing_pin:true` 27 处；`per_card_checks.json` 记 `pin_present:false` 81 处、`qual:""`；与终稿所据 `pin_resolution.json`（29/31 全复现，唯二 M08/M13 = 账本在案 repack）及独立重算不一致 | 勘误注记（decision.md `## F-RV erratum (landing)`）；**两机检文件 exp/hash/pin/qual 字段不得引用为裁决依据**，引用面固定 = `pin_resolution.json` + 本报告 |
| F-RV-02 | P3 交付 | README 称块内引 sha256，实际 20 块仅顶总则指 manifest，块内无逐块 sha | **本安装批逐块内联**：载体 sha（`reviews/<卡>.md` + `acceptance_rulings.md`，manifest 值经 45/45 复核）+ 追加块体自身 sha256，不改块体 |
| F-RV-03 | P3 形式 | 翻转块 `status_authority` 缺显式 `verdict_is_transcribed_not_authored` 键 | **每个安装块补记 `verdict_is_transcribed_not_authored: true`（done here）** |
| F-RV-04 | P2 他卡记录 | M17 自记 `byte_equality_proof_sha256=6096771a…` vs 现盘 `transcription_proof_r3.json=9d21f855…` 不符（本落卡实测确认两值；块段 `e383f5e8…` 切片复算吻合） | **为 M17 登记 follow-up 行（parent records）**；本卡仅 note，不动 M17 字节 |
| F-RV-05 | P3 他卡记录 | M01 `first_run_forensics.json` 把 01:18:24 归 `stderr.txt`、`review.md`/F-MT-02 归 `oracle.json`（本落卡实读确认） | 追加式注记；F-MT-02 实质不受影响 |

## 3. 未做 / 未验证（unverified 6，如实划界）

1. **48/53 卡四查点未逐卡重跑**：深做 5 卡 + M21–M31 存在性与 10 sha + T1 六 sha + 三项全队发现；
   其余裁定行支撑 = 机检证据在册、入 manifest 封印、抽核层与自述一致 —— sampled-verification 语义，非全量复算。
2. **M08「117/117 前存叶子零改动」未逐叶复算**：核到账本文件与前后像 sha 在案，未重算全部叶子。
3. **T1-5「commit-green」未复跑**（其 review 亦如实声明未复跑并 carried）；本复审不跑任何 harness。
4. **CRLF 批量重写的「写者」未取证**：09-20 ~14:52 UTC 同批 mtime 为强旁证，未做取证级归因。
5. **M25–M28 的 r2 块行号区间未逐块切片重哈希**（其点名形态为「M25 族」引用）；仅核 review.md 终裁在场 +
   `handoff.status`。
6. **网络**：无法从盘面证明历史无网络调用；仅能证 `commands.json` 无网络命令、无网络产物。
   （另：F-RV-04 所涉 M17 证明件漂移**根因未查** —— 超出本卡面，随 M17 follow-up 行核销。）

## 4. 接受后范围（scope-after-accept）

1. `landing_package/` 由父 landing 批次按其 `README.md` 安装（**追加不改 + 前缀哈希证明 + 只动
   `handoff.json.reviewer_status` 一键**），且**必须在本 ACCEPT 之后**执行 —— 本落卡即该 ACCEPT 的转录载体，
   安装随后进行（逐块前缀证明 + F-RV-02/03 装时修，账本 = `<本 attempt>\install_log.jsonl`）。
2. **T1-10 返修卡已另行派单**：`execution_runs/T1-10-FIX/a20260923-01`（其 oracle §0 明文引用本卡返修块
   `landing_package/t1_review_flips.md` L28–40，sha256 `90bcefb9aadfe098…` = 实测值）；**本安装批不翻 T1-10**。
3. **F-MT-01 / F-MT-02 / F-MT-03 = VERIFIED**，随本验收入册；F-MT-02 政策裁定（content-based freeze
   attestations + 永久缺口注记）由父登记。
4. **D9 = CLOSED-via-this-agency pending install**：两件落槽已产出，待按 README 安装后闭合
   （安装结果镜像见 `evidence/M-T-REVIEW/qualification.json` 的 d9 镜像键）。
5. **未授予**：任何 D/E/F、真实公司适配、准确性、外推；本复审不代被审卡签任何超出其词表的状态；
   carried 继承 = M 卡资格 `disclosure_adaptation=unmapped` / `accuracy=unproven`（仅 formula、锚 `9ec65295…`）。

— 落卡转录（carrier landing 批次），2026-09-23 · `verdict_is_transcribed_not_authored: true` · 裁决者 N=1 独立复审代理
