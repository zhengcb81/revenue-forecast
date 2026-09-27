# B1-I08C-product-fixes review.md — CARRIER LANDING（补建落定槽；簿记转录 —— 实现者从不自签）

Status: **`accepted_with_conditions`**（attempt `a20260921-01`，reviewer 原词）。独立复核（独立 reviewer）
把裁决写在 `reviewer_report.md`（字节钉载体）**L16–L18**——**不是**本文件。本文件是该裁决的**落定簿记转录**，
补建 D4 所记缺失的 `review.md` 落定槽（此前 attempt 无 review.md）；并配合 DEV-2.2 的 B1 原卡
`review_pending` 状态回填（见 `handoff.json` 的 `status_flip_bookkeeping`）。**纯簿记转录：不新增任何接受。**
`verdict_is_transcribed_not_authored: true`；`implementer_signed: false`；`implementer_never_signs_acceptance: true`。

## Verdict block（转录，不改判）

- Card / attempt：**B1 — I-08-C product defects REM-01/02/03 / `execution_runs\B1-I08C-product-fixes\a20260921-01`**。
- verdict（载体 L14 `## VERDICT`，L16–L18 逐字）：
  **`` `accepted_with_conditions` — the card's security claims are CONFIRMED; three non-security
  documentation defects and two evidence-completeness defects are recorded below and must be
  closed before/at promotion. ``**
- 裁决作者：**独立复核（独立 reviewer）**，2026-09-21，N=1；本文件作者=BOOKKEEP-REPAIR 簿记执行者（父派单），
  **从不自签**；本 pass 翻转前 handoff 预像 = `status: review_pending`、`implementer_self_acceptance: false`
  （26788 B / `c5696e780a9470cf22dd41333e05c24a82783080b7fd006862e181c25e624259`）。
- 主张对表（载体 L20–L31，7 行）：claim 1 生产零写=**CONFIRMED（复验两次）**；claim 2 oracle 先冻结=**CONFIRMED（哈希证）**、
  freeze *order* 仅部分可证=F5；claim 3 RED 11F/1P rc1 → GREEN 12P rc0=**CONFIRMED（reviewer 双臂自跑）**；
  4a/4b/4c/4d REM-01/02/03=**CONFIRMED**（含 reviewer 自构攻击仍拒）；claim 5 变异 M1–M5=**CONFIRMED（独立复现逐项相等）**、
  M6（reviewer 自增）→ `{}`；claim 6 回归 100P→99P+恰 1 必要失败（该测未改写）=**CONFIRMED**；
  claim 7=**PARTIALLY CONFIRMED**（`result_sha256` 可证不可绑定、保持 unbound=F6；oracle r3 文本字段计数错=F4）。
- Findings（载体 §6，L317 起）：**F1**（MEDIUM, documentation）冻结件 attestation 字段数自相矛盾；
  **F2**（MEDIUM, evidence）冻结证明集测不到「present record is ignored」回归；**F3**（LOW, documentation）
  拒绝码有文档无抛出；**F4**（LOW, evidence）r1 RED raw 不可独立审计；**F5**（LOW, pre-registration）freeze order 靠 mtime、
  decision.md 无 freeze hash；**F6**（INFORMATIONAL, disclosed residual）`result_sha256` 不可绑定、保持 unbound；
  **F7**（adjudication）REM-02「documented, no runtime warning」可接受、caller trap 未闭。
- 结论域（载体 L33–L39 逐字要义）：三缺陷已在 **iso/fixed 树**内于产品面闭合；声明的范围收缩（reduced provider protocol /
  label binding 仅本仓 / 无生产信任锚 / 无晋升）诚实且表述正确。**本报告不授予任何晋升**：
  晋升 `iso/fixed/rf/scripts/{revenue_core,revenue_publication,revenue_report}.py` = 独立 owner 决定，且 F1–F5 应先闭。

## Conditions（转录：载体 §9「Required before promotion (in order)」L536–L553）

1. **F1** — append oracle revision r5 更正 §R3-2/R3-3 字段计数为 10 fields 并说明 `result_sha256` 仅随 request 携带、钉至 sentinel（append-only：r1–r4 字节不动）。
2. **F2** — 补「present record is verified even when the label is `unattested`」节点（R13 等价）+ 变异表补 M6。
3. **F3** — 实现 E21（`issuer`/`key_id` vs resolved trust entry）或删除 docstring 的 E21 主张并列入 not closed。
4. **F7** — REM-02 记为 documented limitation、caller-side trap 仍开，裁 (a)/(b)/(c)；不得称 REM-02 fully closed。
5. **F4/F5** — 下一 attempt 协议内以不同标签留存 raw run 输出、给 `decision.md` freeze-time hash。
6. 然后才由 owner 决定是否晋升 `iso/fixed/rf/scripts/` 三文件。

## 验收词词汇映射注记（BOOKKEEP-REPAIR #4/#5；现值语义映射表）

**`accepted_with_conditions` ≡ `accepted_scoped` 带遗留件**（canonical 映射 = `accepted_scoped` + carried_findings：
F1/F2/F3/F4/F5/F7 = carried（§9 条件），F6 = disclosed residual）。冻结契约 `review_and_handoff.md:15` 的四值结论域
不含 `accepted_with_conditions`——该词为 reviewer 原词，本转录**不改判、不换词**，只登记映射（全表见
`BOOKKEEP-REPAIR/a20260923-01/decision.md` §5）。

## Carrier（byte-pinned；2026-09-23 本 pass 复算）

| field | value |
|---|---|
| carrier file | `reviewer_report.md`（单轮；verdict `accepted_with_conditions`） |
| sha256（盘上字节 as-stands） | `6bfd2922cdf3418416731e62098567d20ab1dcdc98429d8cc1e899e721e7951b`（37224 B） |
| reviewer 自带重构钉（PENDING-form） | `73feb0593b44ffeb448bc5f5b1cea9800f4cc9fb59f40ca19e9aae8038c104fa`（37086 B）——**本 pass 独立复算 MATCH** |
| 钉法（载体 §10 + `reviewer/report_pin.json`） | 末行 `REPORT_SHA256: \`<digest>\`` 退回 sentinel `REPORT_SHA256: \`PENDING\`` 后哈希；替换是唯一允许差 |
| pin sidecars | `reviewer/report_pin.json`（verdict 字段=`accepted_with_conditions`、`bytes_hashed: 37086`、`bytes_on_disk: 37224`）、`reviewer/REPORT_PIN_VALUE.txt`（单行 `73feb059…`） |
| verdict line | 16–18（§0 VERDICT 块 L14–L39） |
| conditions | §9 L536–L553；findings §6 L317–L481 |
| decision.md（implementer 件） | sha256 `4a1d39b42d9787e506ae36e47fa9aa68d082e96c5149e3ad41645c468fe968a1`（16236 B） |
| producer | 独立复核 only —— 从不是 implementer、从不是本文件作者 |

钉法复核注记（诚实披露）：报告 §10 自带的 PowerShell 片段以 `$t -replace ('pat','rep')` 数组形传参——该形**静默不替换**
（RHS 二元数组被拼接为单一 pattern），直接照抄会得到「未替换」的假象；本 pass 用 `[regex]::Replace` 等价重跑得
`73feb059…` 精确 MATCH（37086 B）。另：报告正文 §10 写「37135 bytes」，`report_pin.json` 记 `bytes_hashed: 37086`——
以 JSON 钉值+本 pass 实测（37086）为准，正文数字为笔误级差异（49 B=注记尾缀），不影响钉成立。

## Bookkeeping

- 落定者：BOOKKEEP-REPAIR / a20260923-01 簿记执行者（delegated subagent），2026-09-23，父派单
  （parent session `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`；AUDIT-DESIGN D4 #4 + GOAL DEV-2.2 #7）。
- 本文件=**新建**（此前 attempt 无 review.md——即 D4「缺 review.md 落定槽」的修复本体）；
  `handoff.json` 同步回填（`status: review_pending → accepted_with_conditions`，原值留痕字段在 JSON 内）。
- **0 字节写入** `reviewer_report.md`、`reviewer/report_pin.json`、`reviewer/REPORT_PIN_VALUE.txt`、`commands.json`、
  `decision.md`、`oracle.md`、`binding.json`、既有 evidence、任何产品树、任何 git 状态。**无自签**：
  本文件只转录 reviewer 的裁决与条件，不关闭任何 carried 件、不授予晋升
  （`disclosure_adaptation = unmapped`、`accuracy = unproven` 维持）。
- D1b 附注：本 attempt `commands.json:35` 登记的 `before/production_anchors.txt` **全树不存在**（登记时点即缺）——
  已按禁补件铁律另立 `evidence_erratum_20260923.md`（本文件不改 commands.json 原行）。
