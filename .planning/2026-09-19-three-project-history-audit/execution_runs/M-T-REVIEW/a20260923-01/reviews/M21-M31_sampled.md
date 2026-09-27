# M21–M31 抽验子审查（3 深验 + 8 点名）— 独立审查员 M-T-REVIEW / N=1

**执行口径**（父方范围更正）：M21–M31 已有有效终裁 —— 本审查先以**自 grep 实证终裁存在性**（不信普查转述），
再做 3 张深验（M21/M25/M31：pin + 签名行 + 落定形态）+ 8 张清单式点名（引 sha）。

## 0. 终裁存在性实证（11/11 在案）

| 卡 | review.md 内 accepted_scoped 引用数 | 转录逐字节证明 | 确认追加证明 | handoff.status |
|---|---|---|---|---|
| M21 | 3 | `verdict_transcription_check.txt` `aee6d601c2c44e59…` | — | accepted_scoped |
| M22 | 3 | `05f5fe10d42b12ec…` | — | accepted_scoped |
| M23 | 3 | `bd76f1053438da80…` | — | accepted_scoped |
| M24 | 2 | `5ff449274be8f840…` | — | accepted_scoped |
| M25 | 3 | （r2 翻转块 append-only，`review.md` 83–131 行；`artifact_sha256.txt` 族） | — | accepted_scoped |
| M26 | 3 | 同 M25 族 | — | accepted_scoped |
| M27 | 3 | 同 M25 族 | — | accepted_scoped |
| M28 | 3 | 同 M25 族 | — | accepted_scoped |
| M29 | 2 | `58e614d533e6be73…` | `4ff7a53b7a999974…` | accepted_scoped |
| M30 | 2 | `dfb854b4cc085b76…` | `a0992cfea58efad5…` | accepted_scoped |
| M31 | 2 | `c57d50061510e548…` | `f41b2fc71f8b7605…` | accepted_scoped |

⇒ 父方普查更正（M21–M31 有终裁）**经本审查员独立实证成立**；无一张按缺验收处理。

## 1. 深验 M21（M21–M24 批族）

- **pin**：3/3 复现（CRLF 形态）；iso == binding == 锚 `9ec65295…`。
- **签名行/落定形态**：round-3 bounded final review 的裁定**逐字转录**入 `review.md`（round 2 = 120–130 行、
  round 3 = 131–140 行），`verdict_transcription_check.txt`（`aee6d601c2c44e59…`）证逐字节一致；
  `handoff.status=accepted_scoped`；实现者明记 "The implementer never writes 'accepted'"。
- **子句抽点**：`[122]` 三方一致 ✅ / 负例 11/11 ✅ / 九件齐 ✅ / 三栏纪律 ✅ / 无产品改动 ✅。
- **终裁演化核验**：round 1（M21 accepted；M22/23/24 changes_required）→ round 2（M22/23 转正、M24 仍
  changes_required）→ round 3（四卡全 accepted_scoped；M24 的偏差被独立维持、round-2 清单错误由 reviewer 自认）。
  演化自洽、无「改期望凑过」痕迹。
- **裁定：`accepted_with_conditions`（仅 formula、仅本 attempt、仅锚）**；carried：F-MT-01/02/03。
  — 独立审查员 M-T-REVIEW / N=1，2026-09-23

## 2. 深验 M25（M25–M28 批族 · r2 受控重冻代）

- **pin**：3/3 复现（**LF 形态直配**，`artifact_sha256.txt` + handoff 双族）；iso == binding == 锚。
- **签名行/落定形态**：r2 点复审四卡全 accepted_scoped（P1=0），裁定文本 **APPEND-ONLY 转录**入 `review.md`
  83–131 行；曾被一次**外部生产回滚**短暂作废、由 owner 恢复（`production_drift_window_and_restoration` 在案）
  —— 该事件被登记而非抹去，符合 T1-21 口径。
- **子句抽点**：`[300]` 三方一致 ✅ / 负例 11/11 ✅ / 九件齐 ✅ / 三栏纪律 ✅ / 无产品改动 ✅。
- **裁定：`accepted_with_conditions`（仅 formula、仅本 attempt、仅锚）**；carried：F-MT-02/03。
  — 独立审查员 M-T-REVIEW / N=1，2026-09-23

## 3. 深验 M31（M29–M31 批族 · status_authority 落定形态样版）

- **pin**：3/3 复现（CRLF 形态）；iso == binding == 锚。
- **签名行/落定形态**：reviewer 裁定**逐字转录** `review.md` 43–98 行 + bounded-text 确认追加 100–118 行，
  双证明 `c57d50061510e548…`/`f41b2fc71f8b7605…`；`handoff.reviewer_status` 为机器可读落定块
  （`implementer_signed=False`、`implementer_never_signs_acceptance=True`、`set_by=implementer on orchestration
  instruction`、`qualification_scope=formula only @ 9ec65295…`）——**status_authority 形态齐备**，carrier 字段
  可由 `restore_status_carrier_fields.py` 从转录证明重建。
- **子句抽点**：`[160]` == oracle.expected_float ✅（handoff 无 `positive_expected` 键 —— 记账省缺，不改结论）/
  负例 11/11（`negative_results.json` 计）✅ / 九件齐 ✅ / 三栏纪律 ✅ / 无产品改动 ✅。
- **勘误链核验**：T1-23 勘误（必填清单不含 `net_revenue_per_unit` = 原裁定不成立的误读）已闭合（OWNER_DECISIONS
  §14.3 登记）；T1-25 R-1/R-2 已清除（`t1_23_t1_25_verification.json` `4231bf052dee…` 八命题 holds）。
- **裁定：`accepted_with_conditions`（仅 formula、仅本 attempt、仅锚）**；carried：F-MT-02/03、handoff 缺
  `positive_expected` 键（记账补键建议，非实质）。
  — 独立审查员 M-T-REVIEW / N=1，2026-09-23

## 4. 点名 8 张（终裁在案，引 sha；M22/M23/M24/M26/M27/M28/M29/M30）

| 卡 | 终裁载体（sha 前 16 位） | 本审查员抽点 | 裁定 |
|---|---|---|---|
| M22 | 转录证明 `05f5fe10d42b12ec…`；round-3 全批转正 | ① `[55]` 三方一致 ② 11/11 ③ 九件 ④ 三栏 ⑤ 无产品改动；pin 3/3 CRLF | **accepted_with_conditions**（F-MT-01/02/03） |
| M23 | `bd76f1053438da80…` | ① `[110]` ② 11/11 ③④⑤ ✅；pin 3/3 CRLF | **accepted_with_conditions**（F-MT-01/02/03） |
| M24 | `5ff449274be8f840…`（M24 偏差被 round-3 独立维持） | ① `[215]` ② 11/11 ③④⑤ ✅；pin 3/3 CRLF | **accepted_with_conditions**（F-MT-01/02/03；round-2→3 翻转的 reviewer 自认记录采信） |
| M26 | r2 append-only 块（M25 族） | ① `[205]` ② 11/11 ③④⑤ ✅；pin 3/3 LF | **accepted_with_conditions**（F-MT-02/03） |
| M27 | r2 append-only 块 | ① `[264000]` ② 11/11 ③④⑤ ✅；pin 3/3 LF | **accepted_with_conditions**（F-MT-02/03） |
| M28 | r2 append-only 块 | ① `[11.5]` ② 11/11 ③④⑤ ✅；pin 3/3 LF | **accepted_with_conditions**（F-MT-02/03） |
| M29 | `58e614d533e6be73…` + 确认 `4ff7a53b7a999974…`；status 落定块（OQ-05 经 T1-24 裁定不阻断） | ① `[300]`==oracle ② 11/11（negative_results 计）③④⑤ ✅；pin 3/3 CRLF | **accepted_with_conditions**（F-MT-01/02/03；handoff 缺 `positive_expected` 键） |
| M30 | `dfb854b4cc085b76…` + `a0992cfea58efad5…` | ① `[600]`==oracle ② 11/11 ③④⑤ ✅；pin 3/3 CRLF | **accepted_with_conditions**（同 M29 备注） |

— 独立审查员 M-T-REVIEW / N=1，2026-09-23
