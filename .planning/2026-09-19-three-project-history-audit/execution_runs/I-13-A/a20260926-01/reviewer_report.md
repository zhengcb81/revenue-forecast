# I-13-A · 买方交付逐项评分 —— 独立买方 reviewer 复审报告

- 被审 attempt：`execution_runs/I-13-A/a20260926-01`（`status=review_pending`，实现者判 `classification=blocked`）
- 复审人：独立买方 reviewer（不参与该预测设定；本件只出报告，**不写卡状态**）
- 报告面：本文件 + 同目录 `reviewer_report.sha256`（写入面 = 2 个新文件，其余零改动）

---

**VERDICT: ACCEPT —— P1×0（数值/红线/封盘三项全过）；P2×1、P3×4 随附。核心裁定 `HB3 = not_established` ⇒ 分类按卡文规则机械降为 `research_draft_needs_review`（非 `buy_side_review_ready`，亦非 `blocked`）。分类是卡的交付物，本报告只作裁定与发现登记，不改任何 `status`/`decision`。**

---

## 一、回源面（V2-4 只读清单，全部实际读到）

| # | 件 | 结果 |
|---|---|---|
| 1 | `oracle.md` 22,070 B · sha `d4292eff…` | ✅ 与 handoff `written_files` 一致 |
| 2 | `evidence/I-13-A/buy_side_scorecard.json` 15,169 B · `e74631c7…` | ✅ |
| 3 | `evidence/I-13-A/blocking_issues.json` 12,694 B · `c9c6030c…` | ✅ |
| 4 | `evidence/I-13-A/artifact_references.json` 8,337 B · `62d440fe…` | ✅ |
| 5 | `verification.json` 11,968 B · `ffa2f814…` | ✅ |
| 6 | `handoff.json` 17,120 B（自指，不记自身 sha） | ✅ |
| 7 | 卡文 `execution_v2/card_I-13-A.md` 1,383 B · `daaf300e…`；评分尺（B01–B08 / 7 hard_blocks / 分类规则）由 `common_research_cards.md` §「I-13评分和硬阻断」L291-L312 与 oracle §2 逐字比对 | ✅ 逐字一致 |
| 8 | 上游 `I-12-A` 三件（**仅 sha**，不读任何测试/准确性结果） | `evaluation_design.json` 22,317 B `203dd4a8…`；`professional_approval.json` 5,334 B `0befb154…`；`design_manifest.json` 5,618 B `ad46a6e6…` |
| 9 | `OPEN6B-TOLERANCE-RULING/a20260926-01`（154 kg） | 关键断言见 §二 |
| 10 | `OPEN6H4-IND-COUNTERSIGN/a20260926-01` **及其 `-R2`**（口径桥） | 关键断言见 §二 |

---

## 二、⭐ HB3 裁定（本复审核心职权）

### 裁定

> **`HB3 = not_established`**（实现者判 `established`，本人回源后推翻）。

### HB3 原文（卡文硬阻断第 3 条，逐字）
「存量桥、收入对账、产销/供需约束失败**且未获明确适用性裁决**。」——**合取条件**，两支都须成立。

### 逐支核

**A 支 · 收入对账 → 不失败**：`584,049,229,264 − 234,970,146,412 = 349,079,082,852`，差 = 0（本人自算，见 §三②）。

**B 支 · 产销主恒等式 → 不失败**：Cu `878,180+6,763 = 884,943`、Au `82,743+418 = 83,161`（本人自算，见 §三②）。

**C 支 · 存量桥/口径桥「未获明确适用性裁决」→ 该前提不成立（两支均有有权方明文裁决，且在本 run 冻结前执行完毕）**

1. **H4 口径桥（269 t / 534 kg）**
   - `OWNER_DECISIONS.md §三十六`（L820-L848；现算 sha `17c0db1d…`/109,029 B —— **与本 run oracle §3 所记同一份**）：owner 明文授权追加支「残差 ≤ 量级上界 且 方向一致 ⇒ 视为已解释，不单独构成会签阻断；翻转事实须如实登记」，并指定「**修订后重跑 Q2 → 会签**」。
   - 执行件 `OPEN6H4-IND-COUNTERSIGN-R2/a20260926-01`：oracle 先冻结（`d9a437e7…`，17:46:50+01:00），交付 **18:08:14+01:00** ⇒ `q2_status="pass"`、`countersigned=true`、`basis=addendum_condition5_r2`、`flip_registered.not_hidden=true`、`threshold_review_status` 仍 `not_reviewed`、`releases_nothing=true`；变异 7/7 命中 `OVERALL_rc=0`；所记五件 sha 本人逐件复算全部一致。
   - **时序**：R2 交付 18:08 < 本 run gate0 **20:24:23+01:00** < oracle 冻结 20:27:33 < 打分 20:29:31 ⇒ 打分时点该裁决**已在盘面生效 2h16m**。
   - ⇒ 实现者 HB3 basis③ 与 scorecard `B04.why_not_2` 的「**§三十六 已授权但 Q2 重跑未做 / 会签未成**」为**过期陈述**（见发现 F-1/F-5）。

2. **存货桥 154 千克（BLOCKED-6b / OPEN-11）**
   - `OPEN6B-TOLERANCE-RULING` 关键断言（本人复算其件 sha：`ruling_6b.md` `e5d1efce…`/28,628 B、`tolerance_signed.json` `3ad403ba…`/18,082 B、`oracle.md` `1efb584f…`/15,055 B 全部一致）：R2=`H-CN-ZIJIN-VOL-03` 实测残差金 +154 千克 ⇒ **`NOT_SIGNED`（insufficient_evidence）**，`signed_count=3/4`，`blocked_6b_status="still_blocked"`；恢复三路径 (a)/(b)/(c)，L110「整条 BLOCKED 的状态由 owner/编排层在 R2 解决后重判」。
   - **适用性已由 owner 明文裁决**：`OWNER_DECISIONS §三十三`（L716-L741）owner 原话 **「确认适用 (c) 不改规则（建议）」** —— 字面即「适用性」裁定；执行映射授权编排层退 `unquantified`。
   - **裁决已执行**：`OPEN6B-R2-REVERT-UNQUANTIFIED/a20260926-01`（16:16:09+01:00，早于 gate0 4h08m）`revert_applied=true`，`hypotheses[2] H-CN-ZIJIN-VOL-03.state: pending_professional_decision → unquantified`；封盘原件 `f2178768…`/51,697 B **零字节**，新版本 `57dc6469…`/54,975 B（本人复算一致）。
   - ⇒ 被裁对象已**撤回数量主张、零传播**，且处置是明文裁决 + 已落地，非「未获裁决」。

**D 支 · 实现者自己登记的反证与 overturn 条件，本人逐条回源复核为真**
- 收入对账差=0、Cu/Au 主恒等式逐位闭合 → ✅ 自算通过（§三②）。
- 受影响参数零传播 → ✅ `params_released=false`、`rows_claiming_released=0`、`new_value` 全表不含 124,248.63（`verification.structure_probe`）。
- 上游按「登记不阻断」ACCEPT → ✅ `I-11-C/handoff.json L233` 逐字「登记不阻断映射算术」；`I-07-E/handoff.json L118`「BLOCKED-6a/6b/6c…未解（不解除）」。
- `scorecard.classification_derivation.overturn_condition` 两条触发例：
  - 「§三十六 追加支覆盖该残差并完成 Q2 重跑」→ **实测为真**（18:08 交付）。
  - 「6b 的 154 千克容差已由有权方明文裁决」→ **实测为真**（§三十三 明文「确认适用 (c)」+ 16:16 执行；τ 本身 NOT_SIGNED 是裁决的**结果**，不是「未裁决」）。

**E 支 · 为什么实现者会判 established（成因，如实登记）**
实现者回源面为 V2-4 只读清单，**不含** `OPEN6B-*` / `OPEN6H4-*` 两族工位；其唯一可用时点状态来自 `I-11-C` 上游，而 **`I-11-C/oracle.md` 冻结于 18:02:41，早于 R2 交付 6 分钟**，其 C5-②「会签未成」冻结时为真、交付（19:43:50）时已过期。实现者在 oracle §6 P6 中如实标注「fail-closed 从严读法」并把裁定权移交本工位，**非伪造、非豁免**。

### 保留与边界（不因 overturn 而消失，登记不隐藏）
- **P3**：`BLOCKED-6b` 登记条仍 `signed_count=3/4`，是否转 `accepted` 尚待按 `ruling_6b L110` 另判；**本裁定不解除任何 `OPEN-2/3/5/6/11`、不解除任何 `BLOCKED-*`、不放行任何参数、不产生 `ACCEPT`**。
- **HB2**：本人复核维持 `not_established`（交付面引用 I-07-B 实测 64 位；63 位缺陷位于只读 store、已登记并随附正确值；无信息泄漏）。若买方从严按字面读作「hash错」⇒ HB2 转 `established`、分类仍 `blocked`（不改本报告结论的数值/红线/封盘三项）；本人不采纳该读法，理由已列 F-3。
- 卡文 STOP（L19）随 `HB3` 翻转而**不触发**；L20「未证明准确性只能写 unproven」始终未被用作 `blocked` 依据（实现者已声明，本人复核属实）。

---

## 三、三处 spot-check（本人自算）

**① 评分 8 维相加 = 9/16 自算**
`B01..B08 = 1,1,1,1,1,1,2,1` → `Σ = 9`；`total_max = 8×2 = 16` ⇒ **9/16** ✅
与 `buy_side_scorecard.total=9` / `total_max=16` / `zeros_present=0` 及 `handoff.score_summary` 逐字段一致；`total_is_display_only=true`，未被用作放行阈值。

**② 一条恒等式自算（收入对账主恒等式 + 附证）**
- 四分部对外相加：`138,271,672,956 + 189,683,879,295 + 170,521,025,777 + 85,572,651,236 = 584,049,229,264`（逐位命中）✅
- `584,049,229,264 − 234,970,146,412 = 349,079,082,852`，**差 = 0** ✅
- 附：Cu `878,180+6,763=884,943` ✅；Au `82,743+418=83,161` ✅；MSFT FY2026 `139,996+137,791+54,052=331,839` ✅；`884,943+83,161×24 = 2,880,807` ✅；红线两值 `109,977,556,345÷885,141 = 124,248.63`、`÷2,880,807 = 38,175.95` ✅
- 引用行核对：`I-07-E summary L111`（差=0 + 毛总计和逐位）、`L43/L44`（产销与库存释放）、`L143/L144`（红线两值）**均可定位**。

**③ 上游 sha 对照**
- `verification.upstream_inputs` **13/13 逐件复算一致**（`Get-FileHash SHA256` + 字节数），含**封盘** `f2178768…/51,697 B` 与 **store** `b2063ac8…/61,231 B`。
- 本 run `handoff.written_files` **7/7 逐件复算一致**（oracle / 三 evidence / verification / 两 py）。
- 两件裁定载体自身 sha 复算一致：`ruling_6b.md`、`tolerance_signed.json`、`ind_countersign.json`、`q2_revised.json`、`ruling_h4_ind_r2.md`、`hypotheses_r2_v1.json`。
- 加验（只读重跑）：`python -B _verify_i13a.py` → **GREEN rc=0 `ALL_INVARIANTS_OK`**；`_mut/M2` **rc=3**（`J2: classification='blocked' but rule-derived='research_draft_needs_review'`）；`_mut/M4` **rc=3**（`J3`+`J4`）。无 `__pycache__` 残件（`python -B`）。

---

## 四、OPEN-2 红线 + 封盘

**红线（`base 124,248.63` / 真值 `38,175.95`，OPEN-2 前禁消费）→ ✅ 未破**

| 检查 | 结果 |
|---|---|
| `consumed_for_forecast` 消费主张 | 0（`oracle.md`/`verification.json` 中仅规则与变异描述语境，落在校验器 `BAN_RULE_CONTEXT` 白名单；五件产物正文无消费主张） |
| `"params_released": true` | 0 |
| `124248.63` 以 JSON 数值形态出现 | 0（校验器 `REDLINE_NUMBERS` 扫描通过） |
| `124,248.63` 出现处语境 | 6 处，全部为 `registered_not_consumed` / 禁消费 / 只登记 / 存档 |
| `open2_ban_observed` | `true` |
| `classification` 非 `buy_side_review_ready` | ✅（红线强制项） |
| 分值表引用 | `artifact_references.red_line_refs` 明写 `registered_not_consumed` |

**封盘 → ✅ 零字节**：`execution_runs/I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json` = `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`，**51,697 B**（收尾复哈希一致）；store `hypotheses_v3.json` = `b2063ac8…1413ff`，61,231 B（零改动）。

**收尾复哈希（报告写入前一刻）**：上游 13 件 **13/13 一致**；封盘/store 如上；本 run 已交付 7 件 bytes+sha 全一致。

---

## 五、发现清单

| id | 级 | 发现 | 处置建议 |
|---|---|---|---|
| **F-1** | **P2** | `scorecard.B04.why_not_2` 与 `blocking_issues.HB3.basis③` 称「§三十六 已授权但 Q2 重跑未做 / 会签未成」——在打分时点已不成立（`OPEN6H4-IND-COUNTERSIGN-R2` 18:08:14+01:00 交付 `countersigned=true`，早于 gate0 20:24:23）。成因：回源面不含该工位 + 上游 `I-11-C` oracle 18:02:41 冻结早于 R2 交付 6 分钟；实现者已如实写明「在本站授权回源面内未见该裁决落地」。**不改变任何维度分值**（B04 另有 MSFT 适配不授予、6b 未签、小米缺位三条依据），但**触发 HB3 overturn**。 | 后继卡以追加式更正该时点陈述；不回改本 attempt |
| **F-2** | P3 | `BLOCKED-6b` 仍 `signed_count=3/4`、`still_blocked`，未按 `ruling_6b L110` 重判（§三十三 边界明列）。 | 交有权方/编排层另判；残余不隐藏 |
| **F-3** | P3 | HB2 字面缺陷：store 内 `US-MSFT-10K-FY2026.doc_sha256` 63 位 vs 实测 64 位（只读、已登记、随附正确值）。本人判 `not_established`。 | store 侧勘误（本工位只读不可改） |
| **F-4** | P3 | 8 维中 7 维为 1（`gap-U1..U4`、`u-N4/u-N5/u-N6`、`I-07-E` 8 项 open_questions、小米 blocked-缺位）⇒ 无论如何够不到 `buy_side_review_ready`。 | 逐项补证后重打分 |
| **F-5** | P3 | 上游登记过期：`I-11-C/handoff.json C5-②`（19:43:50 交付）仍写「会签未成」，与其 oracle 18:02 冻结相符、与盘面 18:08 事实不符。 | 追加式更正，供后继卡回源 |
| **F-6** | — | **P1 = 0**：无数值错、无红线破、无封盘动。 | — |

---

## 六、分类最终判定（机械推导，按卡文 L13 / oracle §2.3）

```
established_hard_blocks = []            （HB3 → not_established；HB1/2/4/5/6/7 维持 not_established）
zeros_present = 0                        （B01..B08 无 0）
存在 1 的维度 = 7（B01,B02,B03,B04,B05,B06,B08）
⇒ 「没有0但存在1」 ⇒ classification = research_draft_needs_review
（非 buy_side_review_ready：7 维为 1，且未获独立全维签署）
```

与实现者 `overturn_condition` 预告的降级路径**完全一致**（亦与重跑 `_mut/M2` 时校验器给出的 `rule-derived='research_draft_needs_review'` 一致）。
本报告**不写卡状态**：落定与 `status` 变更由父直写。

---

## 七、边界（没做的事）

- **写入面 = 2 个新文件**：`reviewer_report.md` + `reviewer_report.sha256`；attempt 内原有 **38 件**（含 `_mut/**`）字节与 mtime 零改动（写后复点：目录共 40 件 = 38 + 2；`handoff.json` 仍 17,120 B / 20:40:28.987）。
- **不写卡状态**：无 `status`/`decision`/`decision_sha256` 写入，不产生 `ACCEPT`，不改 `review_pending`。
- **只读件收尾复哈希**：上游 13 件 + 封盘 + store 复算一致（见 §四）。
- **禁 git 写、禁 `git status`**：全程未执行任何 git 命令；无 `git add/commit/push`。
- **禁联网**：0 次网络请求（`provenance` 四件未触发）。
- **不读测试/准确性结果（封存）**：`I-12-A` 三件**只取 sha**，未读其内容；未打开任何测试目录（含被拒访问目录）。
- **不解除** 任何 `OPEN-*` / `BLOCKED-*`；**不放行任何参数**；**不触发任何 falsifier/自动动作**；**不派 `I-13-B`**（派发由编排层按本裁定决定）；不写 `.planning` 之外、不写五份计划文件。
