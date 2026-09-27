# binding_erratum_20260923.md — B5 历史 attempt 完整性失配勘误（追加式；原 binding 不动）

- by：BOOKKEEP-REPAIR / a20260923-01（父派单 #10；AUDIT-DESIGN **D7**、AUDIT-GOAL §3.5 开放项①、登记册 §72(3)/§76 表 D7 行）
- 对象：`execution_runs/B5-plan-level-remediation/a20260921-01/binding.json`（B5 原始卡的 binding）
- 形态：**追加式勘误文件**（本文件新建）；`binding.json`、`boundary_verification.json` 及其余历史件 **0 字节触碰**。
- 原则：**原值留痕**——记录值与实测值并存，不静默改钉、不回改任何历史记录。

## 1. 失配宣告（两哈希全值并列）

| 角色 | sha256（全值） | bytes | 出处 |
|---|---|---|---|
| **记录值**（B5 自记） | `06ff80641682d526c0b87f0ac153a60a1995fcd5c3bcf8acf98dd0d2c30ecb73` | （未记） | `B5-plan-level-remediation/a20260921-01/handoff.json:35/:38`——B5 自己 handoff 内对 `binding.json` 的自钉（handoff 写于 B5-fix 存在之前） |
| **实测值 #1**（B5-fix 测） | `96733875e7556f0606220bda8ea1fbaea7d462f66b392132538dafc8c53d499a` | 22652 | `B5-fix-g1a-g3/a20260922-01/evidence/boundary_verification.json` → `b5_attempt_read_only_proof.mismatches[0]`（`match: false`；同文件自注 "a mismatch would mean B5's tree changed after its handoff - reported, never repaired by this card"） |
| **实测值 #2**（本 pass 复算） | `96733875e7556f0606220bda8ea1fbaea7d462f66b392132538dafc8c53d499a` | 22652 | BOOKKEEP-REPAIR 2026-09-23 `Get-FileHash` 只读复算 = 实测值 #1 **逐字相同** ⇒ 自 B5-fix 检查以来该文件未再变 |

⇒ **失配成立且持续存在**：`binding.json` 在 B5 自己 handoff（记录 `06ff8064…`）之后、B5-fix 检查（实测 `96733875…`）之前被改动，且至今保持改动后状态。

## 2. 改者归因（best-known，如实标注不确定）

- **改动窗口**：2026-09-21（B5 handoff 写就）→ 2026-09-22（B5-fix `boundary_verification` 实测）之间。
- **best-known 归因 = 后续父批/落定面**（计划层簿记面）：候选动作 = B5 原始卡忠实回填（登记册 §二十五，2026-09-22「B5 原始卡忠实回填完成」）或相邻父簿记批次对该树的落定触碰。**精确改动者与时点无法从现有计划记录定位**——以 AUDIT-INTEGRITY 时间线面（登记册 §72 已挂「待 AUDIT-INTEGRITY 面定位」、§78 BL 面结论）为权威定位件。
- **排除项（有据）**：B5-fix-g1a-g3 **未**写该树（其自证 `b5_attempt_read_only_proof.PASS_of_what_this_card_controls: true`、17/18 一致）；AUDIT-DESIGN 复跑事故两文件已 %TEMP% 前像**逐字节还原**（`7c4c95dc…`/`0aacaac8…` == B5 handoff:94-95 记录值，净影响仅 mtime），**不是**本失配的成因（本失配对象= binding.json，且 B5-fix 在审计事故之前即已实测失配）。
- **性质**：历史 attempt 树在其 handoff 后被改动（**事后改史面**），非捏造（两值均在案、自报留痕）。

## 3. 实测现值复算入表（2026-09-23，只读）

| 文件 | sha256（2026-09-23 实测） | bytes | 备注 |
|---|---|---|---|
| `B5-plan-level-remediation/a20260921-01/binding.json` | `96733875e7556f0606220bda8ea1fbaea7d462f66b392132538dafc8c53d499a` | 22652 | = 实测值 #1；**≠ 记录值 `06ff8064…`** |
| `B5-plan-level-remediation/a20260921-01/handoff.json` | `ca69b8f46d275fdb3509d26a49b42585a7825d24723fd5fd97f98bcd7da17de3` | 31133 | 记录值出处件；只读 |
| `B5-fix-g1a-g3/a20260922-01/evidence/boundary_verification.json` | `0aacaac8199975a5fc823f15aadd80f61e1c407a6f5dbc6fe9a05f73ef931ea6` | 8059 | 失配自报件；只读 |
| `B5-fix-g1a-g3/a20260922-01/binding.json` | `c6ef61034a0c2f0382bdb6de6901df8a805cbd25c4eb78e959eea5accc56136` | 12490 | 本 attempt 自身 binding；只读、未触碰 |

## 4. 边界声明

- 本勘误**不修复**失配本体（历史字节不可回改；恢复 `06ff8064…` 对应字节=对象已不可考，不做替代品填充——同 REM-59 家族纪律「悬空引用不用替代品去填」）。
- 0 字节写入上表四文件、任何 reviewer 载体、任何产品树、任何 git 状态。
- 登记行（供父折入 `REMEDIATION_REGISTER.md`）：**D7 收口**——B5 binding 失配=追加式勘误在案（`binding_erratum_20260923.md`：记录 `06ff8064…`/实测 `96733875…` 全值并列、现值复算入表、改者=后续父批/落定面 best-known、精确时间线待/依 AUDIT-INTEGRITY 面），原 binding 不动、原值留痕。
