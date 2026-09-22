# M04 · accounting / specialist decision record

Card: M04 (`capacity_utilization`), Parent I-10. Attempt `execution_runs/M04/a20260919-01`.
Author: implementer. Status: **proposed, NOT approved**. Card step D is `[professional_decision_required]`.
Mapping basis: SMIC FY2024 annual report, pages 6 / 8 / 13 / 34 / 84.

**This card carries an ACTIVE `STOP_DISCLOSURE_ADAPTATION` finding (DEC-M04-1).**

---

## DEC-M04-1 — Capacity denominator: period-end vs full-year average (ACTIVE STOP)

- **What the model documents**: `capacity` = **full-year gross capacity in pieces** (card_M04.md line 8:
  满年毛产能件数).
- **What the issuer discloses**: only **period-end** monthly capacity — `94.8 万片/月 折合8英寸标准逻辑`
  at 2024-12-31 (pages 6 and 84). No monthly or quarterly capacity series and no year-average capacity.
- **The probe result**: annualising the period-end figure (`948,000 × 12 = 11,376,000`) and applying the
  disclosed utilisation `0.856` gives `9,737,856` good wafers, versus the disclosed shipment volume of
  `8,021,000` wafers — a gap of `+1,716,856` wafers = **21.4045%**, versus the 0.5% tolerance frozen
  before the run in `oracle.md` §7. The reconciliation **FAILS**.
- **Diagnosis**: SMIC was expanding through 2024 (period-end 948,000/month vs an implied average of roughly
  781,000/month, 82.37% of period-end annualised). "Period-end capacity × 12" is therefore not a usable
  stand-in for the model's documented input.
- **Decision requested** (industry + accounting reviewer):
  1. reject the period-end annualisation as the `capacity` input; **and**
  2. state which of the following is acceptable, with reasons:
     - (a) obtain a disclosed average/available capacity series (annual report capacity table, quarterly
       results, or a prospectus) — preferred;
     - (b) build an explicit **capacity-ramp bridge** (commissioning dates × months available) as a separate,
       reviewed artefact, and feed the *average* into `capacity`, keeping `timing_factor = 1`;
     - (c) use the model only where the issuer itself discloses an average capacity.
- **Rejected alternatives**:
  - back-solving `capacity` from disclosed shipment volume and utilisation (this is how the 9,370,327 figure
    was obtained) and then presenting it as a disclosed parameter — explicitly forbidden by I-10-A item 3;
  - silently lowering the tolerance so the 21.4% gap "passes";
  - relabelling the period-end figure as an average.
- **Compatibility impact**: if (b) is chosen, the ramp bridge becomes a required input for this model and any
  consumer must reference its version; if (a) is unavailable for other issuers, this model must be marked
  `not_applicable_with_reason` per issuer rather than force-fitted.
- **Recovery rule**: the gap evidence is retained as-is; a later attempt may add a ramp bridge, but it must
  re-run this comparison and must not overwrite this record.

## DEC-M04-2 — Yield: why it is 1, and why that is not a filled-in disclosure

- **Fact**: a full-text probe of the 222-page report for 良率 returned **2 hits, both qualitative**
  (page 13 "产品良率提升"; page 34 "产品良率保证"). No numeric yield is disclosed.
- **Choice**: `yield = 1.0`, on the ground that the disclosed 产能利用率 is an
  effective-output/available-capacity ratio, i.e. yield loss is already inside it. Multiplying by a numeric
  yield would deduct yield **twice**, which card_M04.md line 48 forbids ("合格产能不能重复扣良率").
- **Why this is not a loophole**: the field is recorded as **missing**, not as reported. A reviewer may
  overturn the choice, in which case `capacity` must be re-expressed on an **input (started wafer)** basis
  and a numeric yield source becomes mandatory.
- **Counter-example that would flip the decision**: if the issuer's utilisation denominator is *nameplate*
  capacity rather than *available* capacity, yield is **not** inside the ratio and `yield = 1` would
  overstate output. The report does not define the denominator — this is exactly why SR-M04-A is raised.
- **Decision requested**: confirm whether 产能利用率 already embeds yield for this issuer; if unknown, keep
  the card at `STOP_DISCLOSURE_ADAPTATION`.

## DEC-M04-3 — Commissioning time must not be counted twice

- `timing_factor = 1.0` because `capacity` is already a full-year figure. I-10 states that average
  commissioned capacity already contains the commissioning time and must not be multiplied by a commissioning
  ratio again (card_M04.md line 48).
- **Cross-check**: two of BYD's and SMIC's disclosures in this card bundle show the same trap from the other
  direction — M03 requires `timing_factor = 1` because the volume is full-year. Both cards therefore end up
  with `timing_factor = 1`, and any future scenario that lowers it must justify why the base figure is *not*
  full-year.
- **Decision requested**: confirm the rule "`timing_factor = 1` unless the capacity/volume input is explicitly
  a partial-year figure".

## DEC-M04-4 — Production volume is not sales volume

`capacity_utilization` ends at **good output**. Turning output into revenue requires a
production → shipment → confirmed sales bridge including inventory change, which this model does not contain
(card_M04.md line 48; I-10 table: 产销差须桥接).

- For SMIC the disclosed shipment volume (`8,021,000`) is *sold* wafers, so the 21.4% gap in DEC-M04-1 mixes
  **two** effects: (i) the wrong capacity basis, and (ii) output-versus-sales. This attempt does **not**
  attribute the gap between the two, because the disclosure does not provide an inventory/wafer stock bridge.
- **Decision requested**: confirm that no part of the gap may be attributed without an inventory bridge, and
  that the gap must remain unexplained rather than split by assumption.

## DEC-M04-5 — Unidentifiable parameters

| Not identifiable | Consequence |
|---|---|
| actual production volume | cannot be recovered from capacity × utilisation without a yield and basis definition |
| sold vs produced | no inventory bridge; revenue could be built on unsold output |
| multi-fab / multi-node split | one blended utilisation hides per-fab ramp and per-node yield |
| design vs effective vs available capacity | the report discloses neither a nameplate nor an average |
| wafer-size and process mix | 8-inch-equivalent conversion blends different ASPs |

## DEC-M04-6 — Special review flags

| Flag | Content | Requested specialist |
|---|---|---|
| SR-M04-A | Does the disclosed 产能利用率 use nameplate, available, or effective capacity as its denominator, and is yield inside it? | accounting + industry reviewer |
| SR-M04-B | Partial provenance: this PDF's sidecar is a 5-line stub with no provider receipt or URL, so the document identity cannot be cross-checked against a publisher hash. Is the company-wiki copy acceptable as disclosure evidence? | filing/provenance reviewer |
| SR-M04-C | Should `capacity` be redefined to require "average available capacity" as a hard input contract, with a ramp bridge as a separate artefact? | industry reviewer |
| SR-M04-D | Is a single blended utilisation/unit price admissible for a multi-fab issuer, or must it be split per fab/node? | industry reviewer |

## What this file is NOT

- Not an approval. `disclosure_adaptation` remains **unmapped** and this card records an active stop.
- Not an accuracy claim.
