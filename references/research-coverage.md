# Nine-dimension revenue research coverage

Use this layer before numerical forecasting. Its purpose is to prevent omitted research, not to add points to CAGR or confidence.

The nine dimensions test coverage, not research depth or economic validity. Read [buy-side-methodology.md](buy-side-methodology.md) for independent benchmarks, falsifiable hypotheses, model-risk review and forecast evaluation, and [industry-lifecycle-routing.md](industry-lifecycle-routing.md) for segment-level industry and lifecycle routing. Those research standards are not additional runtime gates unless explicitly implemented.

This layer is necessary but not sufficient for forward statements. Complete the separate management-communication and target ledger in `management-targets.md`; do not hide a dated management target inside the generic `growth_curve` narrative.

It is also not the growth-driver explanation. The nine dimensions are a flat omission gate; the separate `growth_driver_tree` selects the material causal mechanisms, links them to Base parameters, branches into checked evidence and counterevidence, and ranks them by modeled revenue increment.

## Required dimensions

| Dimension | Question | Typical revenue mapping |
|---|---|---|
| `company_foundation` | What is the reported revenue perimeter and segment base? | reported total, segment base, signed base adjustments |
| `growth_curve` | Which operating variables create the forecast path? | volume, price, customers, activity, utilization, backlog conversion |
| `industry_market` | Does the addressable market constrain or support modeled demand? | eligible demand or market-share driver, never TAM alone |
| `competition` | How does competition change share, price, win rate, or retention? | units, price, bookings, churn, conversion |
| `capacity` | What can actually be delivered and recognized? | commissioned capacity, utilization, billable hours, stores |
| `technology` | Does technology change yield, acceptance, price, or adoption timing? | yield, unit revenue, launch timing, customer qualification |
| `policy` | Does policy create a traceable order, tariff, approval, or restriction? | bookings, approved volume, tariff, recognition timing |
| `customers` | Which customer behaviors drive revenue? | customers, ARPU, retention, concentration-adjusted orders |
| `demand` | What end demand converts into recognized revenue? | units, usage, activity, bookings followed by conversion |

## Allowed statuses

- `modeled_driver`: the conclusion maps to one or more parameters actually used by the revenue graph.
- `data_gap`: the dimension is material but evidence is insufficient. It may list partially modeled parameters, but must state the remaining gap.
- `immaterial`: the dimension is not material to the stated forecast horizon and must explain why. It cannot map parameters.

## Record schema

```json
{
  "dimension": "capacity",
  "status": "modeled_driver",
  "conclusion": "Commissioned lines cap 2027 shipments",
  "revenue_mechanism": "commissioned capacity × utilization × yield × unit revenue",
  "parameter_ids": ["capacity_2027_base", "utilization_2027_base"],
  "source_ids": ["fy2025_filing", "capacity_release"],
  "rationale": "Optional for modeled_driver; required for data_gap or immaterial"
}
```

Provide exactly one record for each required dimension.

## Hard gates

- A `modeled_driver` parameter must exist and be used by the reported/base bridge, a segment scenario, recognition carry-in, or a company forecast adjustment.
- `company_foundation` must map to at least one reported or base parameter.
- `growth_curve` must map to at least one forecast driver, recognition carry-in, or forecast adjustment.
- A `modeled_driver` record requires source IDs. Parameter-level facts and assumptions retain their own evidence identities.
- A `data_gap` or `immaterial` record requires a rationale.
- An `immaterial` record cannot hide a parameter used by the model.
- Every `data_gap` conclusion is copied into the standard forecast `data_gaps` output.

## Causal discipline

Do not convert a research narrative directly into CAGR. Translate it through an operating identity:

```text
policy or market change
→ customer budget or demand
→ orders / users / activity
→ deliverable capacity and timing
→ accounting recognition
→ revenue
```

Do not force all nine dimensions into the formula. A well-supported `immaterial` conclusion is preferable to an invented driver.

## Depth review: connect evidence to a falsifiable forecast

For each material dimension, review the following before assigning its status. This checklist is an analyst responsibility; the runtime does not understand the underlying economics merely because the record is complete.

| Dimension | Quantitative cross-check | Qualitative challenge |
|---|---|---|
| `company_foundation` | Reported versus comparable history, organic/FX/M&A bridge, gross/net and recognition basis | Is reported growth caused by perimeter or accounting changes? |
| `growth_curve` | Segment stage, observed unit economics, saturation/replacement/decline limits | What ends the current mechanism, and when would the model need changing? |
| `industry_market` | Served demand, eligible customers, comparable penetration and cycle history | Does the reference class include failed entrants and delayed adoption? |
| `competition` | Same-customer retention, net price, win/loss, substitute price/performance | Could share gains be temporary subsidies or channel loading? |
| `capacity` | Commissioned capacity, time in service, bottlenecks, available inventory | Is supply actually qualified, staffed, financed and deliverable? |
| `technology` | Qualification time, yield, performance at commercial scale, obsolescence | Does a lab/demo advantage survive customers' total-cost and reliability tests? |
| `policy` | Eligible budget, legal implementation, tariff/approval and fulfillment dates | Is the policy enacted and executable, or only an announcement? |
| `customers` | Concentration, contract duration, additions, churn, usage and purchasing cadence | Who decides and pays; can customers postpone, cancel or substitute? |
| `demand` | Sell-through, repeat purchase, inventory, bookings quality and cancellations | Is apparent demand pull-forward, restocking or recurring consumption? |

For material claims record an alternative explanation, the affected parameter and period, a leading indicator, and a falsifier with an observable trigger. Map these into the existing growth-driver tree and parameter evidence rather than creating a parallel source ledger. Distinguish independent evidence from repeated versions of one original announcement.

Prioritize gaps by potential revenue impact and decision sensitivity, not by the number of missing fields. Use the existing `rationale` to explain why a gap could alter volume, price, timing or model choice and what evidence would resolve it. Unknown does not mean zero impact; it also does not justify inserting an arbitrary downside number.

## Lifecycle and changing-business review

Assign lifecycle at product/segment level in the research rationale: pre-revenue, commercialization, expansion, maturity, cyclical recovery/contraction, decline, or transformation. These are research labels, not new enum values. Preserve the original schema statuses.

- For pre-revenue streams, investigate launch prerequisites and explicit zero-revenue years; never infer a CAGR from zero.
- For mature streams, explain replacement, retention, net pricing and market limits instead of assuming persistent new-customer growth.
- For cyclical streams, compare quantities, price, inventory and utilization over a relevant cycle; a rebound from a depressed base is not automatically structural growth.
- For declining streams, include customer loss, patent expiry, closures and residual service demand. Negative revenue growth is a valid forecast result.
- For transformation, separate old/new streams and account for customer migration and cannibalization exactly once.

## Custom dimensions

The nine core dimensions are required. For resource-business forecasts (mineral reserves, drug pipeline, land bank, capacity plan), additional custom dimensions may be added to capture domain-specific research:

| Custom dimension | Use when |
|---|---|
| `reserves` | 地质储量、资源分级、储量寿命 |
| `processing` | 回收率、选冶能力、冶金复杂度 |
| `regulatory_permits` | 采矿权、环保审批、土地使用权 |
| `pipeline` | 药物管线阶段、临床试验进展 |
| `land_bank` | 土地储备构成、开发权、规划条件 |
| `installed_base` | 设备、客户或门店存量及更新/服务机会 |
| `channel_inventory` | 生产、进货、动销与渠道库存变化 |
| `lifecycle_transition` | 商业化、成熟、衰退或新旧业务迁移 |
| `reference_class` | 同类成功/失败样本与外部基准的可比性 |

Custom dimensions follow the same schema as core dimensions (status, conclusion, revenue_mechanism, parameter_ids, source_ids, rationale). They do not replace core dimensions. The engine outputs custom dimensions after the nine core ones.
