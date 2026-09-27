# I-12-A / a20260926-01 · V3 B 级独立轻复审（reviewer_report）

VERDICT: ACCEPT —— P1 = 0（无数值错 / OPEN-2 红线未破 / 封盘未被动）；附 P3 × 3（P-a、P-b、P-c）

- 复审工位：独立复审（B 级轻复审）· 时间 2026-09-26 20:31–20:36（UTC+01）· 只写本文件 + `reviewer_report.sha256`（写入面 = 2 新文件）
- 判级规则：P1 仅限 数值错 / 红线被破 / 封盘被动 ⇒ `changes_required`；否则 `ACCEPT`（可带 P2/P3）。本轮 P1 计数 **0**。
- 被审 3 件基线（本工位实测 sha256 / bytes / mtime；**复审以此为准**）：

| 件 | bytes | sha256 | mtime |
|---|---|---|---|
| `oracle.md` | 16,649 | `08723ab0f62c07cbf0f9a7563b8fc6382bff41da8a3f7c72ab14b81cfc7e76ee` | 20:19:02 |
| `handoff.json` | **15,267** | `c6ce61c9d3429dbd899f81889667ea617e1c2eb94155d5f1c6b4e2006e119063` | **20:30:42** |
| `_verify_design.ps1` | 8,026 | `6cc12fdda9fb019a73709704a50e4324026c22997f3b29f914204de5cc9e2d39` | 20:27:08 |

## §1 裁决行定位

- 本文件裁决行 = **L3**（`VERDICT: ACCEPT …`），判级依据见 L5 规则行。
- `ACCEPT` 语义边界：本报告只出复审裁决，**不写任何卡 `status`/`decision`/`decision_sha256`**；卡级登记 `BLOCKED_PROFESSIONAL_DECISION` 的解除权仍在编排层/双 reviewer。

## §2 发现清单（P3 × 3；无 P1/P2）

- **P-a（记录性，非缺陷）**：派单给的 `handoff.json` = 14,326 B，但实现者在复审窗口内仍在定稿 —— 初读（~20:29）时 `raw_exit_codes`/`expected_exit_codes.match`/`written_files` 全为 `TBD`，20:30:42 定稿后已填 `0/3/3/3/3/3/0`、`match=true`、`written_files` 6 件 sha；终态 15,267 B。⇒ 复审基线以 L3 表 sha 为准；父落定请复哈希该 sha，勿用派单的 14,326 B。
- **P-b（措辞）**：`handoff.completed_steps[2]` 称读到 `calibration_validation_summary.md`「§A-§F 与 J1-J5 判据」。实测 summary 有 **§A…§G**（§G=边界自宣），全文**无 `J1`-`J5` 字样**（J1-J5 应属 `I-07-E/verification.json` 面，本工位未回读）⇒ 断言中 §A-§F 部分成立，"J1-J5 判据"归属应改为 I-07-E verification.json；不涉数值、不涉红线。
- **P-c（后续提示）**：`_verify_design.ps1` J4（L95-L96）对 `stop_condition.code == 'BLOCKED_PROFESSIONAL_DECISION'` 为**无条件断言**，不接受"已签署"态 ⇒ 绿臂仅在当前未签署状态下成立；双 reviewer 签署后必须换版本校验器并重冻 manifest（与 oracle §6「冻结」及 handoff `next_action ②` 一致，但复审/编排层需知悉此换版依赖）。

## §3 五项轻核

**① 裁决行定位**：见 §1（L3）。**② 发现清单**：见 §2（P3 × 3，P1 = 0）。

**③ 三处 spot-check**

- **SC-①（handoff 上游断言 vs `I-07-E/a20260926-01/calibration_validation_summary.md` 原文）**
  - sha/bytes 断言：`handoff.input_hashes` = `a2304fdd…` ⇒ 本工位实测 `a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb` / **26,132 B** ⇒ 与 oracle §2 第 4 行**逐字节一致 ✅**
  - 关键断言：`handoff.dispatch_verbatim` 转引「OPEN-2 base **124,248.63**（真值 **38,175.95**）」vs summary **L143**「109,977,556,345 ÷ 885,141 ≈ **124,248.6297**」、**L40**「按合成分母（884,943+83,161×24 = 2,880,807）商 ≈ **38,175.95**，差 3.25×/3.26×」⇒ 本工位自算 109,977,556,345÷885,141 = **124,248.63**、÷2,880,807 = **38,175.95** ⇒ **与原文逐位吻合 ✅**
- **SC-②（`_verify_design.ps1` 判据自算 —— 静态复算，不执行脚本）**
  - `J1_release_lock`：以 handoff 实测值自算 5 项 —— `params_released=false` / `implementer_signed=false` / `releases_nothing=true` / `status=review_pending` / `params_released_count=0` ⇒ **5/5 满足 ⇒ J1 = OK**
  - `J2_open2_ban` oracle 行扫描自算：全文含 `consumed_for_forecast` 的行 = **L95 / L113 / L129**；L95 含 `M2`、L113 含 `J2_open2_ban`、L129 含 `M2` ⇒ 三行全落在校验器 L54 的冻结豁免面（M2/J2 定义行）内 ⇒ **J2 oracle 分支 OK**；`handoff.open2_ban_observed=true`（L11）**✅**
- **SC-③（卡文判据 vs 实现）**
  - 卡文验收「evaluation_design_fields 全部完成或有获批 not_applicable；SHA256 冻结在结果解封前」+ 停止①「任何关键统计选项/阈值未签署→BLOCKED_PROFESSIONAL_DECISION」
  - 实现：`handoff.completed_steps[6]` 登记 13 字段 = 9 filled + 1 filled_threshold_unsigned + 3 PENDING + 0 not_applicable（**合计 13 ✅ 自洽**）⇒ 验收**未达成** ⇒ `handoff.card_stop.code=BLOCKED_PROFESSIONAL_DECISION`、`triggered=true`、`second_stop_triggered=false`；并由 `_verify_design.ps1` J4（L95-L96）固化为 rc=3 必检 ⇒ **fail-closed 一致 ✅**；`status=review_pending`、`implementer_signed=false` 与卡文 Owner 栏「统计reviewer和行业reviewer共同签字」及"实现者不自签"一致 ✅

**④ OPEN-2 红线**：`handoff.open2_ban_observed = true` **属实**（L11）。`124,248.63` 及 ±5% 带（本工位自算 ×0.95 = **118,036.20**、×1.05 = **130,461.06**，与 oracle §4 L91「118,036.2 / 124,248.63 / 130,461.06」逐位一致）在 oracle 中**仅出现于 §0 声明 + §4 登记表**（`registered_not_consumed` / `proposed_not_released` / 传播值 = null / 禁入 endpoint·baseline·actual·权重·分层·情景包含率），handoff 中仅出现于 `dispatch_verbatim` 转引；handoff 全文**无** `consumed_for_forecast`。⇒ **只登记未消费，红线未破（P1 不成立）**。

**⑤ 封盘**：`I-11-A/a20260919-01/evidence/I-11-A/hypotheses.json` 本工位**自算** sha256 = `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28`、**51,697 B** ⇒ 与派单 `f2178768…` 逐字节一致，**零字节改动 ✅**（封盘未被动 = P1 不成立）。旁证（超出清单的只读动作，如实披露）：store `OPEN2-C2-REGISTRATION/a20260926-01/hypotheses_v3.json` = `b2063ac8…` / 61,231 B 一致；卡文 `card_I-12-A.md` = `a4d4b2dc…` / 1,467 B 与 oracle §2 行 1、handoff `input_hashes` 一致 ✅。**时序旁证**：mtime 顺序 oracle 20:19:02 → evaluation_design 20:21:58 → professional_approval 20:22:19 → design_manifest 20:22:49 → `_verify_design.ps1` 20:27:08 → verification 20:30:19 → handoff 20:30:42 ⇒「oracle 先冻结、manifest 后于三证」由 mtime 佐证。**收尾复哈希**（本文件写入后执行，结果见 §5）。

## §4 unverified（超出回源清单，未验证，不背书）

1. `design_manifest.json` / `evaluation_design.json` / `professional_approval.json` / `verification.json` 的**内容与 sha** 未由本工位直读 ⇒ `J3`（11 件上游复算）、`J5`/`J6`（3 件冻结指纹）仅经**校验器静态审阅 + mtime 顺序旁证**，未独立复算；`J4` 对 `professional_approval` 三个 reviewer 块形状的断言同样未直读原文件。
2. 红臂 `M1-M5` 的**实跑 rc 与 `verifier_output.txt` 原文未回读、未重跑**；handoff 登记的 `0/3/3/3/3/3/0 + match=true` 未由本工位复现（派单禁止重跑变异）。
3. `I-07-E` 其余上游件（`verification.json`/`handoff.json`/`oracle.md`/`qualification.json`/`reviewer_report.md`）、`research_cards.json`、`OWNER_DECISIONS.md` 的 sha **未复算**；`J1-J5` 归属（P-b）未回源确认。
4. `evaluation_design.json` 的 OPEN-2 块（`registration_state` / `consumed_in_design=false` / `test_results_sealed`）**未直读**，仅由校验器 J2/J5 断言覆盖。
5. 测试集/准确性结果**未读**（按纪律封存），`accuracy=unproven` 未评估。

## §5 收尾复哈希（只读件；写入本报告后实测）

| 件 | bytes | sha256 | 结论 |
|---|---|---|---|
| `oracle.md` | 16,649 | `08723ab0f62c07cbf0f9a7563b8fc6382bff41da8a3f7c72ab14b81cfc7e76ee` | 与 L3 基线一致 ✅ |
| `handoff.json` | 15,267 | `c6ce61c9d3429dbd899f81889667ea617e1c2eb94155d5f1c6b4e2006e119063` | 与 L3 基线一致 ✅ |
| `_verify_design.ps1` | 8,026 | `6cc12fdda9fb019a73709704a50e4324026c22997f3b29f914204de5cc9e2d39` | 与 L3 基线一致 ✅ |
| `I-11-A/…/hypotheses.json`（封盘） | 51,697 | `f217876804c96335cddab6aa95df00abadc294d7bbd066daaebe4d5108f79a28` | 与派单一致 ✅ |
| `card_I-12-A.md` | 1,467 | `a4d4b2dcce2aa1de04ab6aff757de0fb6e75fa21bc5cf0ab0151e5d1e940470f` | 与 oracle §2 一致 ✅ |
| `I-07-E/…/calibration_validation_summary.md` | 26,132 | `a2304fdd082583e7a0395955db9629106b546df549f2f560218f7bd8a8b906eb` | 与 handoff `input_hashes` 一致 ✅ |

## §6 没做的事（纪律自宣）

不跑全量校验器 · **不重跑手算**（仅对既有数字做 spot 自算）· **不做变异**（`_mut/**` 未触碰、未执行）· 只写 `reviewer_report.md` + `reviewer_report.sha256` 两件、**不写卡状态**（零 `status`/`decision`/`decision_sha256` 改动）· 只读件零改动（§5 复哈希佐证）· **禁 git（含 `git status`，零 git 调用）** · **禁联网（零外部检索）** · 未读测试集/准确性结果 · 未读回源清单之外的实现件（见 §4）· 不派卡、不触发任何 falsifier/自动动作。
