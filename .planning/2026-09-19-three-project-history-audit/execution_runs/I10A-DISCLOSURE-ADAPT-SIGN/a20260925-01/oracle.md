# I10A-DISCLOSURE-ADAPT-SIGN oracle.md — FROZEN (written BEFORE any judged run)

Station: `execution_runs/I10A-DISCLOSURE-ADAPT-SIGN/a20260925-01/`
Card: `execution_v2/card_I-11-B.md` premise line 2 (C7) · Owner of `card_I-10-A.md` = 行业/会计reviewer主责
Role of this station: **行业/会计专业 reviewer（非实现者）** · `implementer_signed = false`
Freeze discipline: this file's criteria, mutation list, expected rc table, adopted-list source pins
and the exact signed ruling line are frozen here **before** `check_signoff.py` is written and before
any GREEN/RED/MUT arm is executed. This file is **not edited after the first judged run**.
A re-edit after any judged run invalidates every rc recorded in `handoff.json`.

---

## 0. Frozen source pins (measured read-only at this station; sha256 lowercase, bytes)

All paths are relative to `execution_runs/I-10-A/a20260923-01/` (SEALED attempt — read-only for me).

| # | file | sha256 | bytes | why pinned |
|---|---|---|---|---|
| S1 | `evidence/I-10-A/disclosure_qualification.json` | `6c42e9a8c56be66ffb7b3f0021bd467bb87541856183a7aabe7430bc3bb3e7fb` | 8603 | **superseded source** of `disclosure_adaptation_v2.json` |
| S2 | `evidence/I-10-A/selected_model_manifest.json` | `96b0f56e7ab6505f2189efe25d7da77c439740df7c93e531a8a1dceb0f71ef49` | 22358 | the ONLY authoritative "实际采用" list (frozen before first judged run) |
| S3 | `evidence/I-10-A/historical_reconciliation.json` | `ce222355e2190dd4e956d85e7dd72e7176d1d149aa6002f8c209571ff16a0abc` | 16485 | E residuals + STOP facts |
| S4 | `evidence/I-10-A/oracle_expected.json` | `bf212696259d8c289262b50d544278573544be57c68526a58742d6db37fd9d01` | 7017 | frozen tolerances (set before residuals) |
| S5 | `evidence/I-10-A/historical_mapping_probe.json` | `b4ef9b96c2578f070cc7945e63ab26b41b4a9f20a1587398c54d8c11ed87b75a` | 8944 | probe wiring counts + low/base/high identity |
| S6 | `evidence/I-10-A/qualification.json` | `2a2a14158bb020d042b8f8bebbbc5d6ef0b264214c9ae5d84d92d52ed202f444` | 32841 | landing mirror: `disclosure_adaptation="unmapped"` L21, `signed_machine_face=false` L23, `accuracy="unproven"` L24 |
| S7 | `evidence/I-10-A/disclosure_mapping.json` | `7e03ea748cb99d74038daeef3b529b824f1300c17ee841aaf8fc19b9f1501e0b` | 65783 | D per-field mapping; `review_signature.signed=false` at L768/L1095/L1253/L1409/L1479/L1570 |
| S8 | `oracle.md` (I-10-A) | `5cdd733189686996a264d674ea70d17bbb471b55c611110b969f0b3c449de6dd` | 13121 | frozen expectations + tolerance basis |
| S9 | `reviewer_report.md` | `6bd90c83634624fafe81ddf0a91498102951932e26776fd1b4172ae1c214decb` | 35164 | carrier verdict L15 + sign-off table L236–L243 + signature block L292–L298 |
| S10 | `handoff.json` (I-10-A) | `a3f2208ac8601e1a1711d3f6aa30b3e935148bb93017c8a21d350c10dbea3c58` | 40574 | `status=accepted_scoped`, `implementer_signed=false` L11, machine face note L151/L161 |
| S11 | `review.md` | `dbe63410b09e1732c73726c6ba44e54a8d2b38d25440515cf17cc447374cd2c3` | 29452 | landing transcription (machine face stays unmapped — L139/L156) |
| S12 | `decision.md` | `63afc8dd8707b3353ca205fe8b711ea3149a767d3ed5ae62753ff0c6660a815d` | 18035 | implementer decision + F-REV erratum |

**Sealed-attempt rule**: S1–S12 are read-only inputs. Zero bytes of `I-10-A/a20260923-01` may change
(including its `handoff.json` / `qualification.json` / `review.md` / `oracle*` / `evidence/**`).

**Write face**: only `execution_runs/I10A-DISCLOSURE-ADAPT-SIGN/a20260925-01/**`.

---

## 1. Enumeration (frozen vocabulary for `disclosure_adaptation`)

| token | meaning | who may set it |
|---|---|---|
| `unmapped` | 初始/未达成：无完整 D+E+probe 证据链，或 STOP | default; retained for non-grants |
| `mapped` | 已达成并经签署：D 逐字段 + E 一个已结束期间对账 + 生产 forecast 入口映射 + 独立审阅 | **only** a non-implementer 行业/会计 reviewer |
| `not_granted` | 显式不授予（I-11-A hypotheses 用语） | reviewer |
| `not_applicable_with_reason` | 不适用（本轮用在 `actuarial_reviewer`：三家公司均无保险报告分部） | reviewer |
| `professional_decision_required` | 注册层待专业决策（M 卡 D 段登记态，非结论态） | — |

`accuracy` is a **separate** qualification and must stay `unproven`. `formula` stays
`accepted_scoped (M01–M31, not extrapolated)` and is out of scope here.

---

## 2. 判据 (G1–G10) — `check_signoff.py` implements exactly these; frozen before first run

- **G1 adopted_membership** — every `case_id` in the v2 `cases` object equals the 6 adopted case_ids
  parsed from S2 (`segments[*].status=="adopted" → adopted_models[*].case_id`); order and key set must
  match S1. No case may be added, dropped or renamed. Violation → **reject**.
- **G2 preservation** — for every case, all keys other than `disclosure_adaptation`
  (`company_id`, `segment`, `model_id`, `formula`, `accuracy`) are value-identical to S1; all top-level
  keys other than the added `provenance` (`artifact`, `card`, `attempt_id`,
  `three_qualifications_are_independent`, `company_level`, `carries`, `card_grants`) are
  value-identical to S1. Violation → **reject**.
- **G3 grant_evidence** — for each case with `disclosure_adaptation.signed == true`:
  (a) S3 `E_status` is not `STOP_DISCLOSURE_ADAPTATION`;
  (b) S3 `within_frozen_tolerance == true` and `matches_oracle_expected_residual == true`;
  (c) `abs(residual)/sum_disclosed <= ` S4 `aggregate_tolerance_rel`;
  (d) S5 `counts_ok == true` and `low_base_high_identical == true`;
  (e) the `reviewer_determination.evidence` block I wrote equals the values measured from S3/S4/S5.
  Violation → **reject**.
- **G4 fail_closed_stop** — for each case whose S3 `E_status == STOP_DISCLOSURE_ADAPTATION`
  (MS-PBP-M05, MS-IC-M06): v2 must keep `status == "unmapped"` **and** `signed == false`.
  Any promotion of a STOP case → **reject**.
- **G5 no_overclaim** — v2 must contain no `"accuracy": "proven"`, no
  `"formal_company_forecast_cleared": true`, no `"overall_three_market_pass": true`, no literal
  `三情景预测` / `准确性通过` / `三市场通过` outside a negated/quoted context, and `card_grants.accuracy`
  must remain the S1 verbatim `NOT granted…` string. → **reject** on hit.
- **G6 provenance** — `provenance.supersedes_sha256` == measured sha of S1;
  `provenance.supersedes_bytes` == measured bytes of S1; `provenance.supersedes_file` == the S1
  relative path; `provenance.modified_indices`/`unchanged_indices` == the indices actually measured
  different/equal to S1; `provenance.new_file_sha256` is `null` (self-reference is impossible).
  Violation → **reject**.
- **G7 signature_block** — every case carries `reviewer_determination` with
  `role == "industry_or_accounting_reviewer"`, `date == "2026-09-25"`,
  `decision_sha256` == independently recomputed value (see §4),
  non-empty integer `basis_lines`, and a `permits`/`forbids` pair. Missing/incorrect → **reject**.
- **G8 implementer_never_signs** — every case keeps `implementer_never_signs == true` and
  `signature_authority` verbatim from S1; no field may name an implementer as signer; v2 must declare
  `implementer_signed == false`. Violation → **reject**.
- **G9 releases_nothing** — v2 must not introduce any non-null `low`/`base`/`high`, any
  `threshold_basis`, any `threshold_review_status`, or any `formal_company_forecast_cleared: true`.
  Violation → **reject**.
- **G10 sealed_unchanged** — measured sha of S1, S6, S9, S10, S11, S8 must equal the §0 pins.
  Any drift → **reject** (this would mean I wrote into the sealed attempt).

**rc convention (frozen)**

| rc | meaning |
|---|---|
| 0 | judge ACCEPTS the artifact (all G pass) |
| 1 | harness error (never counted as a pass or a kill) |
| 2 | judge CORRECTLY REJECTS the artifact (a G violation was found) — the expected rc for every RED/MUT arm |
| 3 | an expected violation was NOT detected (vacuous criterion) — must never occur |

---

## 3. 变异清单 (frozen) — expected rc before running

### 3.1 RED / MUT arms (full judge must reject → **rc 2**)

| id | injected defect into a copy of the real v2 (in memory) | G that must catch it | expected rc |
|---|---|---|---|
| M1 | promote `MS-PBP-M05` → `status=mapped, signed=true` | G4 | 2 |
| M2 | promote `MS-IC-M06` → `status=mapped, signed=true` | G4 | 2 |
| M3 | rename case `ZJ-MIN-M09` → `ZJ-TRADE-M02` (a non-adopted combination) | G1 | 2 |
| M4 | corrupt `ZJ-MIN-M09` `reviewer_determination.evidence.residual_disclosed_minus_rebuilt` to `-70000000` (outside frozen ±0.05%) | G3(e)+G3(c) | 2 |
| M5 | set `company_level["CN-ZIJIN-2025"].formal_company_forecast_cleared = true` | G5 | 2 |
| M6 | set `cases["XM-EV-M03"].accuracy.status = "proven"` | G2 (accuracy verbatim) + G5 | 2 |
| M7 | set `provenance.supersedes_sha256` to a wrong 64-hex value | G6 | 2 |
| M8 | delete `reviewer_determination` from `ZJ-SMT-M09` | G7 | 2 |
| M9 | set `cases["XM-PHONE-M03"].disclosure_adaptation.implementer_never_signs = false` | G8 | 2 |
| M10 | inject `"low": 100, "base": 200, "high": 300` into `ZJ-MIN-M09` | G9 | 2 |
| M11 | change `company_level["US-MSFT-2026"].note` (drift outside `disclosure_adaptation`) | G2 | 2 |
| M12 | set `provenance.supersedes_sha256` correctly but `modified_indices` to `[0]` (false provenance claim) | G6 | 2 |

### 3.2 Weakened-criteria arms (W) — 判据改弱后，一个**不该被接受**的口径必须能通过 → **rc 0**

Each W arm disables exactly one G in the judge and then runs the judge against an artifact that is
**knowingly unacceptable**. rc 0 there proves that G is load-bearing (not a decorative rule).

| id | disabled G | unacceptable artifact fed to the weakened judge | expected rc |
|---|---|---|---|
| W1 | G4 disabled | real v2 with `MS-PBP-M05` promoted to `mapped/signed=true` (an adaptation granted without any disclosed operating quantity) | 0 |
| W2 | G3 disabled | real v2 with `ZJ-MIN-M09` residual claimed as `-70,000,000` (3.4× the frozen tolerance) still marked `signed=true` | 0 |
| W3 | G6 disabled | real v2 with `supersedes_sha256` = wrong value (provenance lie) | 0 |
| W4 | G5 disabled | real v2 with `accuracy.status="proven"` (accuracy smuggled through a disclosure signature) | 0 |
| W5 | G10 disabled | real v2 checked while a sealed I-10-A file has drifted (simulated pin swap) | 0 |

### 3.3 GREEN

The real `disclosure_adaptation_v2.json` against the FULL judge → expected **rc 0**.

Expected overall: GREEN rc0 · M1–M12 rc2 (12/12) · W1–W5 rc0 (5/5, each proving its G non-vacuous).

---

## 4. `decision_sha256` 求值方式 (frozen here, before it exists anywhere)

```
preimage = UTF8-no-BOM(source_sha256_of_S1) + 0x0A + UTF8-no-BOM(ruling_line)   # no trailing newline
source_sha256_of_S1 = 6c42e9a8c56be66ffb7b3f0021bd467bb87541856183a7aabe7430bc3bb3e7fb   (64 bytes)
decision_sha256 = lowercase_hex( SHA256(preimage) )
```

`ruling_line` = the single line between the two markers below, byte-exact (frozen in this oracle,
repeated verbatim in `ruling.md` §4.3 markers and in `disclosure_adaptation_v2.json`
`provenance.ruling_text` / every `reviewer_determination.ruling_text`):

--- BEGIN C7 RULING TEXT ---
RULING｜C7/I-10-A disclosure_adaptation → 本 reviewer 裁定（裁定人：非实现者 行业/会计专业 reviewer；授权：execution_v2/card_I-11-B.md L9 前提第二行 逐字「I-11-A命题已批准；I-10-A已为实际采用的公司/分部/模型签署披露适配口径。」+ execution_runs/I11A-OPEN-MERGE/a20260924-01/handoff.json L124 C7 逐字「card_I-11-B.md L9：I-10-A 为实际采用的公司/分部/模型签署披露适配口径（现 review.md 记 disclosure_adaptation = NOT granted）」；作用域仅限 disclosure_adaptation，不含 accuracy、不含任何参数/阈值放行、不产生 I-11-B 的 ACCEPT）。裁定一（实际采用）：以 evidence/I-10-A/selected_model_manifest.json（sha256 96b0f56e7ab6505f2189efe25d7da77c439740df7c93e531a8a1dceb0f71ef49，22358 B，冻结于首个判据运行前）为唯一清单来源，实际采用 = 6 case / 3 公司 / 6 分部 / 4 model_id：ZJ-MIN-M09（CN-ZIJIN-2025 矿产品分部 resource/M09）、ZJ-SMT-M09（CN-ZIJIN-2025 冶炼产品分部 resource/M09）、XM-PHONE-M03（HK-XIAOMI-2025 智能手機 unit_sales/M03）、XM-EV-M03（HK-XIAOMI-2025 智能電動汽車及AI等創新業務分部 unit_sales/M03）、MS-PBP-M05（US-MSFT-2026 Productivity and Business Processes subscription/M05）、MS-IC-M06（US-MSFT-2026 Intelligent Cloud usage_platform/M06）；6 个未采用分部与 27 个 model_id not_selected 带理由，不宣称适配。裁定二（授予 4）：ZJ-MIN-M09 / ZJ-SMT-M09 / XM-PHONE-M03 / XM-EV-M03 判 mapped 并签署——本 reviewer 独立复算 FY2025 同口径「披露量×披露实售价」复建与残差分别为 −2,032,271、−95,486、−21,463,000、+17,635,978 元，逐位等于冻结 oracle 期望，且 |残差|/披露合计 = 0.0015456%、0.0000519%、0.0115120%、0.0166268%，分别落在先冻结的 ±0.05%、±0.05%、±0.05%、±0.10% 内；historical_mapping_probe 计数 24/9/3/3 且 low/base/high 同值；效力仅限该公司/分部/该口径/FY2025，且仅限清单所列 adaptation_scope 的主要产品线 E 口径。裁定三（不授予 2）：MS-PBP-M05 与 MS-IC-M06 维持 status=unmapped、signed=false（本判定签署，资格不授予）——FY2026 10-K 未按所需粒度披露经营量价，7 个字段全 missing、zero_filled=false ×7、zero_filled=true ×0、E 未执行（level1=null、residual=null）、probe 未运行；按 card_I-10-A.md L26 停止条款3 保留 D 段局部结果但不放行 US-MSFT-2026 正式预测。裁定四（fail-closed 收口）：不授予 accuracy（维持 unproven）、不放行任何公司（formal_company_forecast_cleared=false ×3）、不放行任何参数（low/base/high 仍 null）、不改 threshold_basis/threshold_review_status、不解除 OPEN-2/3/5/6 与任何 BLOCKED-*、不产生 I-11-B 的 ACCEPT、不改 I-10-A 封盘任何字节、不代签任何其他角色、implementer_signed=false；AD-7 special_review（仅涉未采用分部）、紫金 L2 范围桥 partially_explained（+6,782,172,956 / +5,695,369,295 元）、F-I10A-2 产品缺陷（fix-card I10A-F2-FIX）与 OPEN-11 矿业库存跨期判定式全部维持开放。
--- END C7 RULING TEXT ---

Recompute steps anyone can run: (1) hash S1 → 64-hex; (2) take the line between the two markers
from this file (and later from `ruling.md` §4.3); (3) `preimage = sha1_of_S1_bytes + "\n" + ruling_line`;
(4) SHA-256 → must equal `provenance.decision_sha256` in the v2 file, every
`reviewer_determination.decision_sha256`, and `handoff.json.decision_sha256`.

**Evaluated once before writing the v2 file, and re-evaluated after writing it** (extraction from the
markers redone from disk); both results and the byte count are recorded in
`handoff.json.decision_sha256_verification`, and a third re-evaluation is done after `ruling.md` exists.

---

## 5. Expected verdict (frozen)

| case | company / segment / model | expected `disclosure_adaptation.status` | expected `signed` |
|---|---|---|---|
| ZJ-MIN-M09 | CN-ZIJIN-2025 / 矿产品分部 / resource (M09) | `mapped` | true |
| ZJ-SMT-M09 | CN-ZIJIN-2025 / 冶炼产品分部 / resource (M09) | `mapped` | true |
| XM-PHONE-M03 | HK-XIAOMI-2025 / 智能手機 / unit_sales (M03) | `mapped` | true |
| XM-EV-M03 | HK-XIAOMI-2025 / 智能電動汽車及AI等創新業務分部 / unit_sales (M03) | `mapped` | true |
| MS-PBP-M05 | US-MSFT-2026 / Productivity and Business Processes / subscription (M05) | `unmapped` | false |
| MS-IC-M06 | US-MSFT-2026 / Intelligent Cloud / usage_platform (M06) | `unmapped` | false |

`disclosure_adaptation_signed_count` (cases with `signed == true`) expected **4**;
`disclosure_adaptation_determination_signed_count` (cases with a signed `reviewer_determination`) expected **6**;
`disclosure_adaptation_not_granted_count` expected **2**; `cleared` expected **false**;
`accuracy` expected `unproven` in all 6 cases.

If evidence measured during the run contradicts any cell of this table, the run must be reported as
`blocked` / `insufficient_evidence` — **not** silently re-signed to fit the table.

---

## 6. 范围边界 (in / out)

**In scope**: `disclosure_adaptation` for the 6 adopted (company, segment, model) packages only —
the 取值、理由、允许披露、不允许披露、签署块、版本 provenance.

**Out of scope (explicitly not granted by this station)**: `accuracy` (stays `unproven`) ·
any parameter value (`low`/`base`/`high` stay `null`) · any `threshold_basis` /
`threshold_review_status` change · any `OPEN-2/3/5/6` or `BLOCKED-*` release · any `I-11-B` ACCEPT ·
any `formal_company_forecast_release` (0 companies) · any model_registry promotion ·
any product byte change · any `git` write · any other role's signature.

---

## 7. 行不交界声明 (relationship to the I-10-A accepted surface)

- `I-10-A/a20260923-01` is `accepted_scoped` and **sealed**: S1–S12 stay at their §0 pins for the
  whole run (G10 enforces it on 6 of them; the rest are re-hashed for the handoff table).
- The I-10-A carrier (`reviewer_report.md` L15, L236–L243, L292–L298) already recorded a
  **report-side** sign-off for the same 4 cases; its machine-readable face stayed
  `unmapped / signed=false` (S6 L21/L23, S11 L139/L156, S10 L151/L161).
  This station does **not** rewrite that face. It produces a **new superseding version in a new
  directory** (the `hypotheses_v2.json` pattern: new file + `provenance.supersedes_sha256`).
- Nothing here re-opens, re-signs or supersedes I-10-A's own verdict; nothing here is an I-10-A
  acceptance. This station's signature is a **separate, later** industry/accounting-reviewer
  determination made for C7, and it is strictly narrower than I-10-A's accepted scope.
- Line-disjointness: this station reads I-10-A only; I-10-A never references this directory.
