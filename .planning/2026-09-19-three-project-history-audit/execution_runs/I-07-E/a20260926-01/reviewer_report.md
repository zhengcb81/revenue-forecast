# reviewer_report.md — I-07-E / a20260926-01（V3 B 级轻复审 · 独立复审工位）

> 复审对象：`execution_runs/I-07-E/a20260926-01/` 五件（`oracle.md` · `calibration_validation_summary.md` · `verification.json` · `handoff.json` · `_verify_summary.ps1`）
> 复审形态：**V3 B 级轻复审（汇总/登记类卡）** —— 只写本报告 + `reviewer_report.sha256`，**不写卡状态、不落定**（落定=父直写）。
> 回源面：仅 5 件被审 + `I-11-B/a20260926-01/calibration_plan.json`（18 槽位）+ `I-11-C/a20260926-01/parameter_mapping.json`（18 映射，仅 sha/关键数）+ 卡文 `execution_v2/card_I-07-E.md` 判据行 + `OWNER_DECISIONS.md §三十四`（L745-L780）。
> **未做**：未跑全量测试、未重跑手算（仅 3 处 spot-check 自算）、未跑变异/不重跑 M1-M5、未重跑 `_verify_summary.ps1`、未回源 AR 原文（p327/p328 等）、未联网、未 git（含 `git status`）。

---

VERDICT: **ACCEPT**（可带 P2/P3 —— 本判 0×P1 / 0×P2 / 2×P3；数值无错、红线未破、封盘未动）

---

## 1. 五项轻核结果

| # | 项 | 结果 |
|---|---|---|
| 1 | 裁决行定位 | 本报告 **L10**（`VERDICT: ACCEPT`，就一行；P 清单见 §4） |
| 2 | 发现清单 | **2×P3（见 §4）**，无 P1/P2 |
| 3 | 3 处关键数 spot-check | ①②③ **全过**（见 §2） |
| 4 | OPEN-2 红线 | **只登记未消费**，`handoff.open2_ban_observed=true` **属实**（见 §3） |
| 5 | 封盘 + 收尾复哈希 | **✓**（见 §5） |

## 2. 三处关键数 spot-check（B 级：只抽 3 处，自算口径见括注）

| # | 抽查项 | 汇总件（`calibration_validation_summary.md`） | 回源原值 | 判 |
|---|---|---|---|---|
| ① | I-11-B 数值：`ZIJIN_SEG_SMELT_EXTERNAL_REVENUE_FY2027`（B1 行 2，L37） | 原值 165,858,644,874；拟定 157,565,712,630 / 165,858,644,874 / 174,151,577,118；`mapped_not_released` | `calibration_plan.json` L49/L54：`original_value=165,858,644,874`，`new_value={157565712630, 165858644874, 174151577118}`，`value_state=proposed_not_released` | ✅ 逐位一致（自算 ±5%：×0.95=157,565,712,630.30→…630；×1.05=174,151,577,117.70→…118，round-to-nearest 成立） |
| ② | I-11-C 映射值：`MSFT_PBP_REVENUE_FY2027`（B1 行 14，L54） | 0.16；拟定 0.102 / 0.16 / 0.218（g_low=51/500、g_high=109/500）；`mapped_not_released` | `parameter_mapping.json` `mapping_rows` 同名行：`original_value=0.16…`，`new_value={0.102,0.16,0.218}`，`value_state=mapped_not_released`，`propagation=allowed_not_released` | ✅ 逐位一致（自算：1.16×0.95−1=0.102=51/500；1.16×1.05−1=0.218=109/500） |
| ③ | 恒等式自算（D2 分部加总） | 584,049,229,264 − 234,970,146,412 = 349,079,082,852（差=0） | CP L171 RECON `original_value` 同式 | ✅ 自算差=0；**加算两路复核亦过**：四分部毛总计 138,271,672,956+189,683,879,295+170,521,025,777+85,572,651,236=584,049,229,264 ✅；差额法 349,079,082,852−165,858,644,874−29,212,610,830−44,030,270,803=109,977,556,345 ✅ |

（附证：PM `action_1_summary` = 18 槽位 / 13 executable / 5 not_executable，5 条明细与汇总件 B2 小计「REALIZED_UNIT + 两分金属实现价 + MSFT_CLOUD + MSFT_LICENSING」逐条对得上 ✅。）

## 3. OPEN-2 红线核验（`124,248.63` 及 ±5% 带是否只登记未消费）

- **判定：只登记、未消费 ✓；`handoff.open2_ban_observed=true` 属实。**
- `124,248.63` 及 ±5% 带（`118,036.2 / 130,461.06`）在被审 5 件中的全部出现点仅为登记/模板转录语境：
  - `calibration_validation_summary.md` L40（B1 行 5）：原值列登记除法成立值，`拟定 low/base/high = **传播值 = null / null / null**`，`I-11-B proposed 118,036.2 / 124,248.63 / 130,461.06 仅存档于登记区，禁消费`，状态 `registered_not_consumed` + `not_executable_no_propagation`；
  - L67（EA-2 模板转录，`release_state=not_released`，blocked_by=OPEN-2）；L143-L145（§F 红线登记区，`registered_not_consumed` / `传播值 = null`）。
- 全 5 件**零** `consumed_for_forecast` 标记；该值**未**进入任何收入路径/年度路径/分部加总/敏感性产出/情景产出/下游映射（本卡无任何 forecast 产出，§E 三公司结果全部登记态/blocked）。
- 回源印证：`parameter_mapping.json` 同名行 `new_value={null,null,null}`、`value_state=not_executable_no_propagation`、`propagation=blocked_no_propagation`、`i11b_proposed_values` 仅存档；`calibration_plan.json` L87 注「OPEN-2 明令该值放行=BLOCKED」。±5% 带自算：124,248.63×0.95=118,036.2、×1.05=130,461.06（与存档三档逐位一致，但**仅存档**）。
- `38,175.95` 对照值、`3.25×/3.26×` 差异、EA-2 系数差分（−10,670.89）同为登记项（D2 明注「登记（禁消费）」）——自算复核：109,977,556,345/885,141=124,248.6297；109,977,556,345/2,880,807=38,175.95；884,943+83,161×24=2,880,807 ≠ 885,141（unverified-N2 成立）。

## 4. 发现清单（P 分级；P1 仅限数值错误/红线被破/封盘被动）

- **P3-1（元数据时点差，非数值错误）**：本次复审派单所列字节数 `verification.json 7,236B`、`handoff.json 12,781B` 与定稿实测 **10,089B / 13,219B** 不符。定稿自述一致可解释：`verification.json` 自注「`mutation_results` 节为运行后补记」，且 `handoff.written_files` 记 `verification.json=10,089B / 237bc2d3…`（与实测逐位一致）；`handoff.json` 为自指文件、按其自述不记自身 sha。⇒ **sha 面无矛盾，仅派单快照早于定稿**；建议父落定登记时以实测字节为准。
- **P3-2（引用尾行 1 行之差，cosmetic）**：汇总件 B1 行 8 引 `CP L115-L124`，`calibration_plan.json` 该槽位实际 L115-L125（下一 parameter_id 起于 L126）；其余抽查引用（L38-L48/L49-L59/L60-L70/L71-L81/L82-L92/L93-L103/L104-L114/L126-L135/L137-L146/L148-L157/L159-L169/L171-L180/L182-L192/L193-L203/L204-L214/L215-L225/L226-L235）逐条命中。不影响任何数值。
- **P1 = 0**（三处 spot-check 全过 ⇒ 无数值错误；OPEN-2 红线未破；封盘零字节变动）。

## 5. 封盘 + 被审 5 件收尾复哈希（本会话自算，只读）

| 文件 | 字节 | sha256（收尾实测） | 与被审件自记比对 |
|---|---|---|---|
| `I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json`（**封盘**） | 51,697 | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | **= `f2178768…` ✓ 封盘未动** |
| `oracle.md` | 18,913 | `5f3685e0b7f628a089636e2226fd03eef95952d0d6b2ba22f3cb7a7cee5ca7fc` | = handoff `written_files` ✓ |
| `calibration_validation_summary.md` | 26,132 | `a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb` | = handoff/verification ✓ |
| `verification.json` | 10,089 | `237bc2d394ec5726c05adc00f6b7de2b88e302aafe658300f64fbac5dd25671c` | = handoff `written_files` ✓ |
| `handoff.json` | 13,219 | `6ca09368ff0f47ecb317a3604876a32c17f88950c3b69d1d6f55ef815aa0f9e4` | 自指件，无自记 sha（本报告为首次留痕） |
| `_verify_summary.ps1` | 5,099 | `d03da4048033997dbd0242863a5ec63877b5ec2f6d9fdd0eaaab5c830b7f53a2` | = handoff `written_files` ✓ |

封盘 ✓；store（`OPEN2-C2-REGISTRATION/…/hypotheses_v3.json`）按 V2-4 回源范围未复读（其 sha `b2063ac8…` 由 J3 绿臂记载，本次**未独立复算**，见 §7）。

## 6. unverified（本轻复审不裁、原样转交）

- `u-N4`：store `US-MSFT-10K-FY2026.doc_sha256` 63 位转录缺陷 —— 登记形态正确，**不裁**（未回源 store/I-07-B）。
- `u-N5`/unverified-N1：store H-01 `original_value=349,079,082,852` 与矿产品分部语义张力 —— **不裁**（需 AR p327/p328 回源，B 级未做）。
- `u-N6`/unverified-N3：EA-4 注记区间 [320,763, 348,432] 与自身带换算不符（注记层）—— **不裁**。
- `gap-U1/U2`（小米 FY2027 槽位缺位 / 披露日未登记）：fail-closed 处置与卡文 L12「不因一家成功写 3/3」一致，**不裁缺位事实本身**。
- `gap-U3/U4`（H1 锁定 / 微软重述无已审载体 ⇒ 显式保留）：与卡文 L11 + fail-closed 一致，**不代为定位载体**。
- **卡级 `STOP_CALIBRATION` 严格读法之争**（字面读法=任一 not_executable 槽位即整卡 blocked）：实现者已登记在案并明言「裁定权=独立复审」。按本次 B 级判据（P1 仅限数值错误/红线被破/封盘被动）**本轮不裁、随卡转有权方**；若采严格读法则本卡+I-11-B 应转 blocked（回滚=作废映射行，零封盘/零 store 改动）——此为已登记的分支，非本次发现。

## 7. 没做的事（明示边界）

- 未跑全量测试 / 未重跑 `_verify_summary.ps1` 绿臂 / 未重跑红臂 M1-M5（变异结果仅作文本内审，未复演）。
- 未重跑手算（超出 3 处 spot-check 与红线恒等式自算以外的算术未复核，如 ±10% 量带、MSFT IC/MPC 换算、EA-6 联合档）。
- 未做变异、未回源 AR/10K 原文（p327/p328、table 74/76 未开卷）、未独立复算 store `hypotheses_v3.json` 与 I-11-B 其余 16 槽位/I-11-C 其余 16 映射（仅抽查 ①② 两行 + PM `action_1_summary` 计数）。
- 未写卡状态、未落定、未产生 `ACCEPT` 落定记录、未改任何 status/decision/decision_sha256、未动封盘/store、未写五份计划文件、未 git、未联网。
- 写入面 = 本目录 2 个新文件：`reviewer_report.md` + `reviewer_report.sha256`。
