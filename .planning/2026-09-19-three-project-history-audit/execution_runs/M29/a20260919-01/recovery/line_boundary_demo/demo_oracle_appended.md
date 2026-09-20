# M29 oracle — commercial_launch (supply-constrained commercial launch)

Card: `execution_v2/card_M29.md` · Parent I-10 · Attempt `a20260919-01` · Model `commercial_launch`
Entry point (card): `scripts/model_registry.py:308` `calculate_registered_model(model_id, base_revenue, drivers, years)`
Registration (card): `scripts/model_extensions.py:211` · Run cwd: this attempt directory (never the repo root)

This document was written **before any product call in this attempt**, and nothing in it was
produced by the function under test. Every number below is hand arithmetic on the card text.
It is frozen: the only file that may later be appended is a single `## revision r2` section,
and `revision_r2.json` records that discipline (see section 10).

## 1. Unit and convention

- Quantities are **full-year units**; `commercial_year_fraction` is the in-year fraction after the
  condition is satisfied; `net_revenue_per_unit` is net price `U/unit` (U = a common synthetic
  currency unit; no company and no currency is implied).
- `base_revenue` is part of the entry-point signature but the rowwise calculator discards it; that
  is measured as a non-gating observation (`OBS-BASE-IGNORED`), not assumed.
- No rounding happens anywhere in this oracle: tolerances are applied to the raw float path.

## 2. Formula as read back from the isolated copy

`revenue = min(eligible_units * adoption_rate, annual_supply_capacity) * commercial_year_fraction * net_revenue_per_unit`

The isolated copy `iso/checkout_scripts/model_extensions.py` (sha256
`9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911`, byte-identical to production)
registers the model with `quantity = (eligible_units, annual_supply_capacity)`,
`ratio = (adoption_rate, commercial_year_fraction)`, `revenue_per_unit = (net_revenue_per_unit)`,
`optional = ()` and `defaults = {}`.

## 3. Frozen positive (hand arithmetic)

| driver | value | dimension | effective bounds |
|---|---|---|---|
| `eligible_units` | 1000 | quantity | [0, inf) |
| `adoption_rate` | 0.2 | ratio | [0, 1] |
| `annual_supply_capacity` | 150 | quantity | [0, inf) |
| `commercial_year_fraction` | 0.5 | ratio | [0, 1] |
| `net_revenue_per_unit` | 4 | revenue_per_unit | [0, inf) |

years `[2027]`; `base_revenue` 0.

Hand work, step by step:

1. demand = `eligible_units * adoption_rate` = 1000 × 0.2 = **200**
2. conditional units = `min(demand, annual_supply_capacity)` = min(200, 150) = **150**
   (the supply side binds; this is what makes the model "supply-constrained")
3. revenue = 150 × `commercial_year_fraction` × `net_revenue_per_unit` = 150 × 0.5 × 4 = **300**

**Expected output: `[300]`.** Tolerance = 1e-9 × max(1, |300|) = 3.0e-07.

## 4. Continuity positive (two years)

`years = [2027, 2028]`, `eligible_units = [1000, 2000]`, `adoption_rate = [0.2, 0.1]`,
`annual_supply_capacity = [150, 400]`, `commercial_year_fraction = [0.5, 1.0]`,
`net_revenue_per_unit = [4, 5]`.

- FY2027: 1000 × 0.2 = 200; min(200, 150) = 150; 150 × 0.5 × 4 = **300**
- FY2028: 2000 × 0.1 = 200; min(200, 400) = 200; 200 × 1.0 × 5 = **1000**

**Expected output: `[300, 1000]`.** This model has **no stock-flow bridge**, so the continuity case
here is the ordinary two-year path; the card-specific cross-year break (`CONT-BREAK`) for this model
is therefore a *fiscal-year* break, `years = [2027, 2029]` (section 6).

## 5. Defaults case

These three cards declare **no optional driver and no default** (`optional = ()`, `defaults = {}`),
so the omitted-input case is the positive case itself; the frozen `defaults` block in `input.json`
is byte-identical to `positive` on purpose, and `defaults_expected_float` is `[300]`. A driver that
is omitted is refused (`missing drivers`) rather than silently filled with 0.0 — see also
`oq_rulings.json` OQ-02.

## 6. Negative list (frozen before the run) — 11 cases, each on a NEW deepcopy

| # | id | base input | mutation | expected |
|---|---|---|---|---|
| 1 | `NEG-CARD` | positive | `adoption_rate = [1.1]` | `ModelRegistryError` — ratio domain [0,1] |
| 2 | `N01a` | positive | `eligible_units[0] = True` | `ModelRegistryError` — bool is not a numeric driver value |
| 3 | `N01b` | positive | `eligible_units[0] = float('nan')` | `ModelRegistryError` — non-finite |
| 4 | `N01c` | positive | `eligible_units[0] = float('inf')` | `ModelRegistryError` — non-finite |
| 5 | `N01d` | positive | `eligible_units[0] = float('-inf')` | `ModelRegistryError` — non-finite |
| 6 | `N02` | positive | `eligible_units = []` | `ModelRegistryError` — one value per forecast year |
| 7 | `N03` | positive | delete `eligible_units` | `ModelRegistryError` — missing drivers |
| 8 | `N04` | positive | add `unknown_driver = [1]` | `ModelRegistryError` — unsupported drivers |
| 9 | `N05a` | positive | `years = []` | `ModelRegistryError` — years must contain fiscal years |
| 10 | `N05b` | positive | `years[0] = True` | `ModelRegistryError` — years must contain fiscal years |
| 11 | `CONT-BREAK` | continuity_positive | `years = [2027, 2029]` | `ModelRegistryError` — years must be consecutive and increasing |

Only the target exception (`model_registry.ModelRegistryError`) counts as a pass; an ImportError,
a FileNotFoundError or any other exception type is recorded as a failure by the runner (rc 3).

## 7. Output shape (asserted, not just the numbers)

- a flat Python `list` of length **1** for the positive case (equal to `len(years)` and to
  `len(expected)`);
- every element a plain finite number (`int`/`float`, never `bool`);
- year labels are **not** observable from the returned list, so `len(output) == len(years)` is the
  only year-linked property that can be asserted; that limitation is recorded in the result doc
  instead of being papered over.

## 8. Tolerance rule

`abs(actual - expected) <= 1e-9 * max(1, abs(expected))`, applied per element, after checking the
path length. No value is rounded before the comparison.

## 9. How this oracle is produced and why it is independent

- `scripts/oracle_M29.py` is standard-library only (`argparse`, `hashlib`, `json`, `os`, `decimal`)
  and **never imports the product**; `evidence/M29/oracle_selfcheck.json` records its import list and
  the `product_import_present = false` verdict.
- `evidence/M29/{input.json,oracle.json,cases.json}` are written by that script and are
  **regenerable byte-for-byte** (`evidence/M29/oracle_regen_proof.json`).
- `iso/oracle_card.md` is a byte-identical pointer copy of the same script (written by
  `oracle_M29.py --emit-script`, stdout kept in `evidence/M29/runs/A2a-emit-oracle-script/`); the
  freeze step hashes that FILE before generation (`evidence/M29/oracle_document_freeze.json`), and
  the ordering `oracle.json mtime < stdout.txt mtime` is measured in `source_manifest.json`.

## 10. Revision discipline

At most ONE `## revision r2` section may ever exist in this file. If one is appended, any recorded
"hash before the append" must be reproducible at a **real line boundary** (truncating the appended
file at the byte offset where the appended section's first line begins). No r2 section exists yet;
`revision_r2.json` proves the rule on a scratch copy and records the honest baseline.

## 11. What this oracle does NOT claim

- It does not claim any disclosure adaptation: the mapping from real filings to these drivers is
  **unmapped** (D is a professional decision) — the calculator producing a number is not an
  adaptation.
- It does not claim accuracy: no information-time sample, no baseline, no statistical uncertainty.
- The card's business negative ("a conditional revenue is not a probability-weighted expectation of
  approval"; "demand and supply ramps that are out of step need a professional time model") is **not
  runtime-enforceable** by this calculator and is recorded as an open question, not as a pass.

## revision r2 (mechanism demonstration, scratch copy only)

This section exists only to prove the reproducibility rule.
