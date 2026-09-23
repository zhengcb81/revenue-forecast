# M03 · accounting / specialist decision record

Card: M03 (`unit_sales`), Parent I-10. Attempt `execution_runs/M03/a20260919-01`.
Author: implementer. Status: **proposed, NOT approved**. Card step D is `[professional_decision_required]`.
Mapping basis: BYD FY2024 annual report (`cninfo:1222881496`), pages 3/14/23/24/25.

---

## DEC-M03-1 — Confirmed sales volume, not production and not shipments

- **Choice**: `units` = **快报销量** (confirmed/reported sales volume) = `4,250,370` passenger vehicles,
  BYD FY2024 report page 23.
- **Alternatives rejected**:
  - (a) **产能状况 / 快报产量** = `4,281,084` — that is the year's *output*. The same table prints both the
    production figure and the sales figure side by side; using either interchangeably would put unsold
    inventory into revenue. Card_M03.md line 40 states production ≠ shipment ≠ confirmed sales.
  - (b) 合计 `4,272,145` (passenger + commercial sales) — a mixed boundary; the revenue column that belongs
    to it is a different row.
  - (c) 中国汽车工业协会 industry volumes (3,143.6 万辆 etc., page 13) — industry data, not the company's sales.
- **Counter-example**: BYD's own table shows production `4,281,084` vs sales `4,250,370` for passenger
  vehicles, a difference of `30,714` units. Using production here would have overstated volume by 0.72%.
- **Compatibility impact**: switching between production / shipment / confirmed sales changes the volume
  denominator and must create a new adaptation version, invalidating downstream results.
- **Recovery rule**: if the reviewer wants a sell-through rather than sell-in basis, the model to use is the
  inventory/sell-through family, not this one with a redefined `units`.

## DEC-M03-2 — Is a derived unit price acceptable as `unit_revenue`?

- **Choice made**: **provisionally used, explicitly flagged as the weakest link.** `unit_revenue` is derived by
  dividing the table's own revenue cell (`525,989,680,000.00`) by the same row's own volume cell
  (`4,250,370`) = `123,751.503987229` CNY/vehicle.
- **Reason this is uncomfortable**: the resulting reconciliation has a **constructive zero residual**. It
  proves the dimensional wiring and nothing else. I-10-A item 3 forbids back-solving a parameter from
  revenue and then calling the same-formula result verification.
- **Alternatives rejected**:
  - (a) an external "average selling price" from a research report — not a company disclosure, would fail the
    disclosure-evidence contract.
  - (b) a mix-weighted build from the four model lines on page 23 — the table does not print a price per line,
    so a mix-weighted price would require four more derived prices and would not add independence.
- **Decision requested**: the reviewer rules whether `unit_sales` can earn a disclosure adaptation at all
  when the per-unit net price is not disclosed. Implementer's position: **not yet** — an independent net-price
  source (price list, disclosed ASP, or a reconciled price/volume bridge) is required first.
- **Rejected alternative**: calling the derived price "disclosed net pricing".

## DEC-M03-3 — Gross vs net price and the double-counting rules (card_M03.md line 40)

The card names three separate traps. Each needs an explicit reviewer ruling:

| Trap | Rule proposed | Evidence status |
|---|---|---|
| returns/rebates/mix already inside the net price must not be deducted again | `units` and `unit_revenue` must be on one net basis; if `unit_revenue` is net, no separate returns term is added (the model has none anyway) | **OPEN**: the mapped column is labelled 销售收入, with no printed statement that it is net of returns or rebates (SR-M03-B) |
| production/shipment/confirmed-sales must not be mixed | `units` is confirmed sales only | resolved by DEC-M03-1, pending reviewer sign-off |
| repeated time scaling must stop | `timing_factor` = 1 whenever `units` is a full-year realised volume | resolved: BYD's 快报销量 is full-year, so `timing_factor = 1` |

**Decision requested**: confirm the net-price basis of BYD's 销售收入 column, or require a returns/rebate
evidence item before any adaptation version is signed.

## DEC-M03-4 — The 14.37% scope gap is a stop signal, not a residual

- **Measured**: rebuild using total vehicle unit sales at the passenger-vehicle unit price =
  `528,684,368,999.31` CNY, versus the disclosed automobile segment revenue `617,381,935,000.00` CNY →
  gap `88,697,566,000.69` CNY = **14.3667%** of the segment line, far outside the 2% tolerance frozen in
  `oracle.md` §7.
- **Interpretation**: the automobile segment revenue line also contains secondary rechargeable batteries,
  vehicle parts and other products. `unit_sales` has no term for them. Card_M03.md line 40 ("产销库存桥")
  and the I-10 requirement (production/sales/inventory bridge) mean this gap must be **bridged with
  evidence**, and it must **never** be booked as unexplained residual revenue.
- **Decision requested**: the reviewer confirms that (i) the gap is a disclosed-scope limitation, and
  (ii) any attempt to add a plug to close it is rejected.
- **Rejected alternative**: adding the gap to `other_revenue` to make the reconciliation "pass".

## DEC-M03-5 — Unidentifiable parameters

| Not identifiable | Consequence |
|---|---|
| production volume vs sales volume | no inventory bridge; cannot detect stock build or channel stuffing |
| channel inventory (dealer/export pipeline) | sell-in vs sell-out cannot be separated |
| product mix | one unit price hides sedan/SUV/MPV/commercial differences (page 23 lines) |
| return rate and rebate rate separately | only a combined net effect, if any, is visible |
| FX | export revenue translated before the price is derived |

## DEC-M03-6 — Special review flags

| Flag | Content | Requested specialist |
|---|---|---|
| SR-M03-A | Is 快报销量 the audited confirmed sales figure, or a preliminary "express" operating figure that may be restated? | accounting reviewer |
| SR-M03-B | Gross/net and tax presentation of the 销售收入 column on page 23. | accounting reviewer |
| SR-M03-C | Should the mapping be split per model line (sedan/SUV/MPV/commercial) rather than one blended unit price? | industry reviewer |
| SR-M03-D | Is the automobile segment line's battery/parts content material for the intended company use? | industry reviewer |

## What this file is NOT

- Not an approval. `disclosure_adaptation` remains **unmapped**.
- Not an accuracy claim: the FY2024 mapping is a closed, already-disclosed period.
