# M01 · accounting / specialist decision record

Card: M01 (`direct_growth`), Parent I-10. Attempt `execution_runs/M01/a20260919-01`.
Author: implementer. Status: **proposed, NOT approved** — every decision below is submitted for the
industry/accounting reviewer (and I-10-A) to sign, reject, or amend. The implementer does not sign.

Card step D is `[professional_decision_required]`. Per `START_HERE.md` §"允许弱模型自行决定与必须交专业审查的边界",
period/restatement/gross-net attribution and unidentifiable model parameters must be written here first and
decided by the named specialist. This file is the implementer's input to that decision, not the decision.

---

## DEC-M01-1 — Which revenue line anchors `base_revenue` (period / restatement / gross-net)

- **Choice made for the probe**: consolidated group **营业收入** for FY2024 as printed in the FY2025
  report's comparative column, `303,639,957,153` CNY (page 15, table 主要会计数据).
- **Alternatives rejected**:
  - (a) FY2024 report's own FY2024 figure as originally filed — same number in this case, but a
    *different document version*; using the later report keeps the pair on one restatement basis.
  - (b) 营业总收入 / segment revenue / 归属于母公司口径 — `营业总收入` does not appear in the PDF text at all
    (probe term hit count 0), so the issuer presents a single 营业收入 line; picking a segment instead
    would break comparability with the disclosed YoY column.
  - (c) 归属于上市公司股东的净利润 — wrong statement (profit, not revenue) and wrong gross/net dimension.
- **Counter-example / risk**: if the FY2024 report's original figure differed from the FY2025 restated
  comparative, a growth rate computed across the two documents would be a mixed-basis bridge and must be
  rejected. This attempt checked both documents (`historical_reconciliation.json`).
- **Compatibility impact**: any downstream consumer of a `direct_growth` parameter set that anchored on a
  different line (segment, 营业总收入, gross-vs-net) must be invalidated and re-run.
- **Recovery rule**: if the reviewer chooses a different anchor, re-freeze `oracle.md` §7 and re-run the
  probe; do not edit the recorded residual.
- **Rejected alternative**: "best practice" is explicitly not an acceptable substitute for this decision.

## DEC-M01-2 — Whether one disclosed growth rate may be reused as a constant CAGR

- **Choice made**: **NO**. `direct_growth` requires one `growth_rate` per forecast year. A single
  historical rate may be used for a *historical_mapping_probe* only (low/base/high keys holding the same
  value, per card step E), and must be labelled `historical_mapping_probe`.
- **Reason**: I-10's rule that a constant CAGR must not paper over a cycle or a transition, and the
  measured residual in `disclosure_adaptation` of `disclosure_mapping.json`
  (CNY -14.59m on a CNY 349.08bn base, i.e. -0.0042%) which shows the single-rate path is already
  unreliable over one closed year for a cyclical miner.
- **Counter-example**: FY2023 -> FY2024 for the same issuer was a different growth rate regime
  (the FY2025 report prints 2023 = `293,403,242,878` and 2024 = `303,639,957,153`, i.e. +3.49%,
  versus +14.96% in 2025). A constant rate therefore cannot be reconciled with two consecutive disclosed
  periods — this is the concrete falsifier.
- **Compatibility impact**: a three-scenario deck that merely relabels one historical rate as low/base/high
  must not be consumed as a real scenario set (card stop condition `STOP_QUALIFICATION_SCOPE`).
- **Recovery rule**: if a scenario set is later calibrated by I-11-B, it must reference this adaptation
  version or create a new one; changing the rate value under the same accounting basis is a parameter
  delta, changing the revenue line or period is a new adaptation version.

## DEC-M01-3 — Unidentifiable parameters (must stay explicitly unidentifiable)

`direct_growth` cannot identify, and no mapping may imply it can:

| Not identifiable | Consequence for use |
|---|---|
| volume vs price decomposition | cannot attribute growth to either; must not be described as a volume or price model |
| equity production / attributable vs consolidated share | consolidated revenue already embeds the group share; the rate cannot re-express it |
| intercompany elimination | the disclosed consolidated line is post-elimination; the rate cannot reproduce a pre-elimination build |
| M&A consolidation vs organic growth | a step-change acquisition enters the rate as if organic |
| FX translation | foreign-currency segments are translated before the rate is computed |
| capacity / inventory / order backlog | invisible to the model |

**Decision requested**: the reviewer confirms this list is complete for the intended uses and that no
caller may claim otherwise. If a use case needs any of these, the correct action is a different model
(e.g. M03/M04 or the resource family), not reinterpreting `growth_rate`.

## DEC-M01-4 — Special review flags

| Flag | Content | Requested specialist |
|---|---|---|
| SR-M01-A | Is the FY2025 comparative of FY2024 on the same PRC ASBE basis as the FY2024 report's own FY2024 figure? (restatement_mapping above) | accounting reviewer |
| SR-M01-B | For a cyclical miner, is a single-rate `direct_growth` ever admissible as a "short-term fallback for a mature stable business", or does the commodity cycle disqualify it by definition? | industry reviewer |
| SR-M01-C | Zero-base commercialisation (`base_revenue = 0`) must never be presented as revived by this model; confirm the negative case wording. | industry reviewer |

## What this file is NOT

- Not an approval. `disclosure_adaptation` remains **unmapped** until a named specialist signs and an
  independent reviewer confirms.
- Not an accuracy claim. See card stop condition `STOP_ACCURACY`.
