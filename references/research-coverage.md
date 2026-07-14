# Nine-dimension revenue research coverage

Use this layer before numerical forecasting. Its purpose is to prevent omitted research, not to add points to CAGR or confidence.

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
