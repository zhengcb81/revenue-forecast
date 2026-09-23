# M02 · accounting / specialist decision record

Card: M02 (`direct_revenue`), Parent I-10. Attempt `execution_runs/M02/a20260919-01`.
Author: implementer. Status: **proposed, NOT approved**. Card step D is `[professional_decision_required]`.

---

## DEC-M02-1 — Which revenue definition anchors the `revenue` driver

- **Choice**: consolidated group **营业收入** (annual recognised revenue) for a disclosed closed period;
  the probe uses ZJ FY2025 = `349,079,082,852` CNY (FY2025 report page 15).
- **Alternatives rejected**:
  - (a) 营业总收入 — the term does not appear in the report text (probe hit count 0); the issuer presents a
    single 营业收入 line, so choosing it would be inventing a second line.
  - (b) segment revenue — that is what the segment mapping (`calculate_model_path`) needs, not a group total;
    mixing the two would silently change the consolidation boundary.
  - (c) 保险服务收入 / premium / net interest income for financial issuers — those are different revenue
    definitions under IFRS 17 / bank presentation and must be mapped by the insurance or banking specialist,
    not by analogy to 营业收入.
- **Counter-example**: order intake, GMV, insurance premium and cash receipts are NOT revenue. Card_M02.md
  line 8 states the unit explicitly as an annual recognised amount U, not orders/GMV/premium/receipts.
- **Compatibility impact**: changing the revenue definition, the consolidation scope or the period
  invalidates every downstream consumer of this adaptation version.
- **Recovery rule**: if the reviewer picks another definition, re-freeze `oracle.md` §7 and re-derive the
  mapping; do not edit recorded evidence.

## DEC-M02-2 — Does a constructive (identity) reconciliation satisfy the card's reconciliation requirement?

- **Choice made**: **NO**. The card (step E) asks for a closed-period reconciliation; for `direct_revenue`
  the input *is* the disclosed output, so the residual is identically zero and carries no information.
- **Reason**: I-10-A item 3 explicitly forbids back-solving a parameter from the revenue figure and then
  calling the same-formula result independent verification. Recording the zero as "reconciliation passed"
  would be exactly that error.
- **Decision requested**: the reviewer rules that `direct_revenue` can only earn a disclosure adaptation via
  (i) a source-provenance chain for the revenue figure itself (report → page → table → line, plus the
  issue-date/availability evidence), and (ii) an *independent* build of the same segment whose sum is
  compared with an explained residual. Neither is delivered here.
- **Rejected alternative**: treating "the model reproduced the number it was given" as the reconciliation.

## DEC-M02-3 — Should an ignored field (`base_revenue`) still have to satisfy its domain?

- **Observation (recorded, not scored)**: with `base_revenue = -5` the product raises
  `ModelRegistryError: direct_revenue.base_revenue cannot be negative`, even though `_direct_revenue`
  never reads `base_revenue`. With `base_revenue = 999` the output is unchanged.
- **Why this needs a decision**: two defensible semantics exist —
  (A) "validate everything the caller passes, even if unused" (current behaviour: fail-closed, catches
  caller mistakes), or (B) "an unused field is semantically absent and must be ignored".
- **Implementer position**: (A) is the safer default and requires **no** code change; the observation is
  recorded so the reviewer can confirm or overturn it. This attempt deliberately did **not** change the
  product, because card_M02.md line 65 forbids rewriting the formula without an independent counter-example
  and an agreed specification.
- **Compatibility impact if changed to (B)**: callers that pass a negative base "because it is ignored"
  would start succeeding; that loosens a guard, so it needs an explicit reviewer sign-off, not a silent fix.

## DEC-M02-4 — Unidentifiable parameters

| Not identifiable | Consequence for use |
|---|---|
| any operating driver (volume, price, capacity, customers, backlog) | the model provides no causal explanation of revenue, and cannot test whether an input path is plausible |
| the revenue figure's own reasonableness | cannot detect a wrong but syntactically valid revenue estimate |
| production/sales/inventory bridge | no way to check revenue against physical activity |
| growth decomposition | cannot attribute change to organic/M&A/FX |

**Decision requested**: the reviewer confirms that a `direct_revenue` path may never be presented as
"driven by" anything, and that its confidence must not be raised because the formula is simple
(card_M02.md line 37).

## DEC-M02-5 — Special review flags

| Flag | Content | Requested specialist |
|---|---|---|
| SR-M02-A | Is the chosen revenue line the correct one for this issuer's reporting framework (PRC ASBE vs IFRS 17 for insurers)? | accounting reviewer |
| SR-M02-B | For an insurer with IFRS 17 insurance service result, is `direct_revenue` admissible at all, or must the reconciliation of CSM/coverage units be done first? | accounting + actuarial reviewer |
| SR-M02-C | Confirm the "not orders/GMV/premium/receipts" wording is enforced at the mapping layer, not just documented. | industry reviewer |

## What this file is NOT

- Not an approval. `disclosure_adaptation` remains **unmapped**.
- Not an accuracy claim. The model has no driver, so it cannot be evaluated for forecast skill.

## r2 追加：F-M02-01（跨模型一致性，**等待 owner/专业裁定，未自决**）

独立复审指出的行为不一致（本 attempt 实测，未改产品）：

| 观察点 | 实测内容 | 出处 |
|---|---|---|
| 校验器层面 | `calculate_registered_model` 在 dispatch 之前统一执行 `base < 0 -> ModelRegistryError`，对**所有**模型一致，不看该模型是否真的使用 `base_revenue` | `iso/checkout_scripts/model_registry.py`（sha256 9ec65295…），`evidence/M02/run_result.json` 的 `OBS-NEG-BASE` |
| 实现层面 | `_direct_revenue` 首行 `del base_revenue`（完全不用）；`_direct_growth` 用 `current = base_revenue` 递推（真实使用） | 同上（只读） |
| 实测 A | `base_revenue = 999` → 输出与正例**完全一致**，证明 `direct_revenue` 不把 base 用作项 | M02 `observations[BASE-INDEPENDENCE]` |
| 实测 B | `base_revenue = -5` → 仍抛 `ModelRegistryError: direct_revenue.base_revenue cannot be negative` | M02 `observations[OBS-NEG-BASE]` |

**为什么不自决**：这是"被忽略的输入字段是否仍须满足域约束"的**契约语义**问题，
涉及跨模型一致性（direct_growth 需要该字段，direct_revenue 不需要），
按 `START_HERE.md` 属于必须交专业审查的边界，且卡 L65 禁止在无独立反例与审定规格时改写实现。
两种候选语义及其后果已写在 DEC-M02-3；**本 attempt 不做任何代码改动**，
该议题已登记在 `handoff.json.open_questions`，标注 `requires_owner_or_specialist_ruling`。
