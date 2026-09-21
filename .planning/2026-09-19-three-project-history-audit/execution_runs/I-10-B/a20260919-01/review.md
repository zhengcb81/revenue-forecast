# I-10-B —— 独立裁决载体（review.md）

card_id: I-10-B · attempt_id: a20260919-01 · 载体性质：**独立裁决的转录**
本文件由 **carrier-landing 记账执行器**建立并写入。**实现者未参与本卡的独立审查、未改写任何结论、不自签验收**
（`review_and_handoff.md` 第 9 条；START_HERE「实现者不能自签 accepted」）。

裁决本体见下方 **§2 裁决块**（保留原样转录，**未改写结论文字**）。
执行器在 §3 只登记**可在盘上复核的事实**（行号、字节数、哈希、命令运行目录清单），**§4 不构成新裁决**。

---

## §1 载体落定说明（执行器自述）

| 项 | 值 |
|---|---|
| 落定动作 | **创建** `review.md`（本文件此前**不存在**；本 attempt 根目录只有 `binding.json`/`changes.diff`/`commands.json`/`compatibility_cells.json`/`compatibility_impact.md`/`decision.md`/`frozen_impact_scan.json`/`frozen_regression_rerun.json`/`handoff.json`/`oracle.md`/`t16_reachability_probe.json`/`verification_after.json`/`verification_before.json`） |
| 裁决来源 | 独立 reviewer 的裁决**经编排层（父 agent）转达**给本执行器：verdict=`accepted_scoped`、independent、**7 项 verified**、**2 项 minor（非阻断）**= `F-R1`/`F-R2` |
| **诚实边界（必须保留）** | 本执行器**未在本机找到**该 reviewer 报告的逐字节留档件（已在 `%TEMP%`、`C:\*-rv*`、`_isolation_incidents`、`reviews/`、本 attempt 全树检索，均无）。故本文件**不具备**「报告 sha256 固化」的证明形态（对比：I-11-A 报告 `e8b7d223…`、M09–M12 报告 `5a44fd4e…` 均按字节留档） |
| 执行器**做了**什么 | ①定位并读出裁决点名的证据；②复算承载文件哈希；③逐条比对裁决陈述与在盘事实（见 §3）；④落 `handoff.json` 载体字段与 `evidence/I-10-B/qualification.json` |
| 执行器**没有**做什么 | ①**没有**重新审查本卡、**没有**复算 oracle、**没有**改变裁决；②**没有**触碰任何生产文件；③**没有**编辑任何冻结件；④**没有**代签任何资格 |

## §2 裁决块（独立 reviewer 原样转录；**非执行器所写**）

```text
reviewer_verdict:            accepted_scoped
reviewer_independence:       独立 reviewer（未参与 I-10-B 的实现；结论由实现者以外的他方出具）
verified_items_count:        7
minor_findings_count:        2   （均非阻断；不改变 verdict）
carried_open_questions:      OQ-I10B-1 / OQ-I10B-2 / OQ-I10B-3

verified:
  (1) 隔离副本内的两项修复（缺陷①省缺即抛、缺陷②按语义角色定符号）按卡文负例成立；
      负例 R-B1-N1 / R-B2-N1 击杀两个真回归，R-B1-N3 / R-B1-P1 / R-B1-P1b / R-B2-P1 / R-B2-N2 保持绿
  (2) `verification_after.json` 7/7、raw rc = 0
  (3) 变异自检 control 7/7；MUT-1（回退补 0）与 MUT-2（回退按名字定符号）被冻结 oracle 击杀；
      MUT-3（去 dimension 闸门）SURVIVED 并**如实登记为等价变异体**
  (4) 四象限 RED→GREEN 重跑成立，两个 rc=3 均为**刻意**反向臂
  (5) 值域变更恰好 5 个 cell、全部为下界放宽、126 个 driver 未变
  (6) 两项确定性工件（`verification_after.json`、`compatibility_cells.json`）在独立 venv 下逐字节复现
  (7) 未落地生产、未回改冻结件、`model_extensions.py` 与生产逐字节相同

minor_findings:
  F-R1  `command_runs/r2-verify-before/` 目录存在（含 `verification_before.json` 1799 B /
        `d074572fec208f008f5114ab8894a26fd65fda9bb6cafc630073344f81ab6805`、`stdout.txt`、
        `iso/rf/scripts/**`、`scripts/verify_i10b.py`），但**未被** `handoff.json.evidence_paths` 列出，
        且不被任何 `raw_exit_codes` 键引用 —— 属**未登记的 command-run 目录**（记账缺口，非结论缺口）
  F-R2  MUT-3（去 dimension 闸门）的**等价变异体地位未被独立枚举**：reviewer 未独立枚举
        「角色表名字 × 不合格 dimension」的声明空间来确认不存在反例；即**接受**该等价性论证
        **但未独立复现其完备性**（已在 `handoff.json` 的 F-I10B-6 与 OQ-I10B-1 如实登记）

qualifications_granted:
  仅 `formula`（**限定范围**）= 「隔离副本内的注册层契约（省缺即抛 + 按语义角色定符号）」成立。
  该资格**不外推**：不含生产合并、不含披露适配、不含准确性。

qualifications_not_granted:
  `disclosure_adaptation` = unmapped（**未授予**）
  `accuracy`              = unproven（**未授予**）
  生产落地（把 iso 修复写入生产 `RF/scripts/model_registry.py`）= **未授权、未授予**，
    属**独立 owner 决策**
  E-1…E-7 勘误 = **未落地**（本卡不得自行改冻结件；交编排层按 T1-12 ① 形态追加式落地）

scope_and_boundaries:
  本裁决**不授权**任何生产写入、不授权自签、不解除 OQ-I10B-1/2/3。
  `implementer_signed = false`；实现者在本卡**从不签署验收**。
  **生产晋升是独立的 owner 决策** —— 本卡的 `accepted_scoped` **不构成**把该修复写入生产的授权。
```

**转录声明**：以上裁决块由独立 reviewer 作出，经编排层转达、由执行器**原样转录**；执行器**未**改动任何结论文字。

## §3 执行器在盘可核事实（供复核；**非裁决**）

| 复核项 | 在盘事实 |
|---|---|
| 裁决对象前像 | `scripts/model_registry.py` = 26446 B / `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f`；`scripts/model_extensions.py` = 14475 B / `9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911`（与 `handoff.input_hashes` 一致） |
| 修复后副本 | `iso/rf/scripts/model_registry.py` = 30116 B / `62f864b9ab3f144eacff43448897d2c31abc217e17ed3b0e3f58894cdd985081` |
| (2) after 相位 | `verification_after.json` = 1766 B / `b7a925f5b5a9e4af4cf77532999521427b79edbc6c51c7bd1aaf2a03c270da86`，`total=7 / failed=0`；与 `command_runs/r2-verify-after/verification_after.json` **同哈希** ⇒ 逐字节复现成立 |
| (1)(4) before 相位 | `verification_before.json` = 1551 B / `46e8758b5d980fa19fcbad50f40db7a6dbe50be5714993e416e7902649a2f95a`；`command_runs/r2-verify-before/stdout.txt` 实测 `phase = before \| total = 7 \| passed = 5 \| failed = 2`，恰为 `R-B1-N1` 与 `R-B2-N1` ⇒ 「缺陷在修复前可见」在盘成立 |
| (3) 变异 | `command_runs/r2-mutation/mutation_proof.json` = 4896 B / `d74e26588e4eeb5fe56e806deb5708d07bc18f13b31b5f2d2fdd82590a134bd5`；`arms/` 含 `control`、`MUT-1_revert_silent_zero`、`MUT-2_revert_name_sign`、`MUT-3_drop_dimension_gate` 四个独立 arm |
| (4) 反向臂 | `r2-red_afterexp_before_reg/verification_after.json` = 1758 B / `87693527d4ae6bff1671598cbdc71179ff87f85ef5cdf21cb3158f0c917573aa`；`r2-xcheck_beforeexp_after_reg/verification_before.json` = 1799 B / `d074572fec208f008f5114ab8894a26fd65fda9bb6cafc630073344f81ab6805` |
| **F-R1 在盘复核** | `command_runs/` 实有 **7** 个子目录：`r2-char_beforeexp_before_reg`、`r2-mutation`、`r2-red_afterexp_before_reg`、`r2-repro-compat`、`r2-verify-after`、**`r2-verify-before`**、`r2-xcheck_beforeexp_after_reg`；而 `handoff.json.evidence_paths` **只列 6 个**，**缺 `command_runs/r2-verify-before/`** ⇒ **F-R1 在盘复现成立**。补充实测：该目录的两件产物分别与 `r2-xcheck…/verification_before.json`、`r2-verify-after/verification_after.json` **同哈希**，即它是**重复臂的原始运行记录**，不含新结论 —— 故判为记账缺口而非结论缺口 |
| **F-R2 在盘复核** | `handoff.json` 的 `F-I10B-6` 已如实登记 `MUT-3 … SURVIVED`、`mutation_proof_valid=true`，且 `OQ-I10B-1` 已提出「等价变异体地位是否可接受」⇒ F-R2 与既有登记**一致**，属**如实披露**而非隐瞒 |
| 勘误未落地 | `compatibility_impact.md` §5 的 E-1…E-7 清单在盘可读；`handoff.errata_pending.items` 与之对应；**未做任何编辑** |
| 生产零写入 | 生产锚点仍为前像 `9ec65295…`（`handoff.input_hashes` 与 `not_done.product_promotion` 一致） |

## §4 资格边界与待办（**不构成新裁决**）

1. **本卡授予**：仅 `formula` 的**限定范围** —— 隔离副本内的注册层契约成立。
2. **本卡不授予**：`disclosure_adaptation`（保持 `unmapped`）、`accuracy`（保持 `unproven`）、任何生产落地资格。
3. **生产晋升是独立的 owner 决策**：本卡的 `accepted_scoped` **不授权**把 iso 修复写入生产
   `RF/scripts/model_registry.py`；该动作须由 owner 单独裁定。
4. **E-1…E-7 勘误**登记为 `PENDING-orchestration`，**本卡未落地**（禁改冻结件；按 T1-12 ① 追加式）。
5. **随卡移交的开放项**：`OQ-I10B-1`（MUT-3 等价变异体）、`OQ-I10B-2`（M14 OQ-03 D/E 追认）、
   `OQ-I10B-3`（`model_extensions.py` untracked 残余风险）、`F-R1`、`F-R2` —— 均**未被本卡解除**。
