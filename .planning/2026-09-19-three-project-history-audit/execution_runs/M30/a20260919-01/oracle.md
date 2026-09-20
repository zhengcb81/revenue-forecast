# M30 oracle — finite_adoption (finite market adoption)

Card: `execution_v2/card_M30.md` · Parent I-10 · Attempt `a20260919-01` · Model `finite_adoption`
Entry point (card): `scripts/model_registry.py:308` `calculate_registered_model(model_id, base_revenue, drivers, years)`
Registration (card): `scripts/model_extensions.py:216` · Run cwd: this attempt directory (never the repo root)

This document was written **before any product call in this attempt**, and nothing in it was
produced by the function under test. Every number below is hand arithmetic on the card text.
It is frozen: the only file that may later be appended is a single `## revision r2` section, and
`revision_r2.json` records that discipline (see section 10).

## 1. Unit and convention

- The unserved market and every flow are **deduplicated, first-adoption units** of the same
  population; `net_revenue_per_unit` is net price `U/first-adoption unit` (U = a common synthetic
  currency unit; no company, currency or physical unit is implied).
- The card's own two-year case is used verbatim as the continuity positive (section 4).
- `base_revenue` is discarded by the rowwise calculator; that is measured as a non-gating
  observation (`OBS-BASE-IGNORED`), not assumed.
- No rounding happens anywhere in this oracle.

## 2. Formula as read back from the isolated copy

`revenue = adopted_units * net_revenue_per_unit` **and** the bridge identity
`closing_unserved_market = opening_unserved_market + new_eligible_units - removed_eligible_units - adopted_units`,
with the cross-year continuity `opening(t) = closing(t-1)`.

The isolated copy `iso/checkout_scripts/model_extensions.py` (sha256
`9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911`, byte-identical to production)
registers the model with `quantity = (opening_unserved_market, new_eligible_units,
removed_eligible_units, adopted_units, closing_unserved_market)`,
`revenue_per_unit = (net_revenue_per_unit)`, `optional = ()` and `defaults = {}`.

## 3. Frozen positive (hand arithmetic)

Input (verbatim from `card_M30.md` L11-40): `opening_unserved_market = 500`,
`new_eligible_units = 100`, `removed_eligible_units = 50`, `adopted_units = 200`,
`closing_unserved_market = 350`, `net_revenue_per_unit = 3`; `years = [2027]`; `base_revenue = 0`.

1. bridge: 500 + 100 − 50 − 200 = **350**, which equals the stated closing balance, so the year
   balances (the product's `_bridge` check has nothing to refuse);
2. revenue: `adopted_units * net_revenue_per_unit` = 200 × 3 = **600**.

**Expected output: `[600]`.** Tolerance = 1e-9 × max(1, |600|) = 6.0e-07.

## 4. Continuity positive (the card's own two-year case)

`card_M30.md` L52-106, used as frozen: `opening_unserved_market = [500, 350]`,
`new_eligible_units = [100, 0]`, `removed_eligible_units = [50, 0]`, `adopted_units = [200, 0]`,
`closing_unserved_market = [350, 350]`, `net_revenue_per_unit = [3, 3]`; `years = [2027, 2028]`.

- FY2027: bridge 500 + 100 − 50 − 200 = 350 = closing; revenue 200 × 3 = **600**
- FY2028: no new / removed / adopted flow; opening = prior closing = 350, so
  350 + 0 − 0 − 0 = 350 = closing; revenue 0 × 3 = **0**

**Expected output: `[600, 0]`.** Because year 2 carries no flow, the card's own words
("opening = prior closing; revenue 0") are exactly what the product must reproduce.

## 5. Defaults case

These three cards declare **no optional driver and no default** (`optional = ()`, `defaults = {}`),
so the omitted-input case is the positive case itself; the frozen `defaults` block in `input.json`
is byte-identical to `positive` on purpose, and `defaults_expected_float` is `[600]`. An omitted
driver is refused (`missing drivers`) instead of being silently filled with 0.0 — see
`oq_rulings.json` OQ-02.

## 6. Negative list (frozen before the run) — 11 cases, each on a NEW deepcopy

| # | id | base input | mutation | expected |
|---|---|---|---|---|
| 1 | `NEG-CARD` | positive | `closing_unserved_market = [351]` | `ModelRegistryError` — stock-flow balance failed (500+100−50−200 = 350 ≠ 351) |
| 2 | `N01a` | positive | `opening_unserved_market[0] = True` | `ModelRegistryError` — bool is not a numeric driver value |
| 3 | `N01b` | positive | `opening_unserved_market[0] = float('nan')` | `ModelRegistryError` — non-finite |
| 4 | `N01c` | positive | `opening_unserved_market[0] = float('inf')` | `ModelRegistryError` — non-finite |
| 5 | `N01d` | positive | `opening_unserved_market[0] = float('-inf')` | `ModelRegistryError` — non-finite |
| 6 | `N02` | positive | `opening_unserved_market = []` | `ModelRegistryError` — one value per forecast year |
| 7 | `N03` | positive | delete `opening_unserved_market` | `ModelRegistryError` — missing drivers |
| 8 | `N04` | positive | add `unknown_driver = [1]` | `ModelRegistryError` — unsupported drivers |
| 9 | `N05a` | positive | `years = []` | `ModelRegistryError` — years must contain fiscal years |
| 10 | `N05b` | positive | `years[0] = True` | `ModelRegistryError` — years must contain fiscal years |
| 11 | `CONT-BREAK` | continuity_positive | `opening_unserved_market = [500, 351]`, `closing_unserved_market = [350, 351]` | `ModelRegistryError` — continuity failed in FY2028: year 2 both balances on its own (351+0−0−0 = 351) and opens 1 above year 1's closing 350 |

Only the target exception (`model_registry.ModelRegistryError`) counts as a pass; an ImportError,
a FileNotFoundError or any other exception type is recorded as a failure by the runner (rc 3).

## 7. Output shape (asserted, not just the numbers)

- a flat Python `list` of length **1** for the positive case (equal to `len(years)` and to
  `len(expected)`), length **2** for the continuity case;
- every element a plain finite number (`int`/`float`, never `bool`);
- year labels are **not** observable from the returned list, so `len(output) == len(years)` is the
  only year-linked property that can be asserted; that limitation is recorded in the result doc
  instead of being papered over.

## 8. Tolerance rule

`abs(actual - expected) <= 1e-9 * max(1, abs(expected))`, applied per element, after checking the
path length. No value is rounded before the comparison. The bridge/continuity check inside the
product uses `math.isclose(rel_tol=1e-9, abs_tol=1e-9)`; its tolerant side is measured as a
non-gating probe (`PROBE-CONTINUITY-TOLERANCE`), its strict side is the frozen `CONT-BREAK` case.

## 9. How this oracle is produced and why it is independent

- `scripts/oracle_M30.py` is standard-library only (`argparse`, `hashlib`, `json`, `os`, `decimal`)
  and **never imports the product**; `evidence/M30/oracle_selfcheck.json` records its import list and
  the `product_import_present = false` verdict. The script asserts that the frozen bridge balances
  (500+100−50−200 == 350) before it emits anything, so a non-balancing frozen input would abort the
  generation instead of being silently accepted.
- `evidence/M30/{input.json,oracle.json,cases.json}` are written by that script and are
  **regenerable byte-for-byte** (`evidence/M30/oracle_regen_proof.json`).
- `iso/oracle_card.md` is a byte-identical pointer copy of the same script (written by
  `oracle_M30.py --emit-script`, stdout kept in `evidence/M30/runs/A2a-emit-oracle-script/`); the
  freeze step hashes that FILE before generation (`evidence/M30/oracle_document_freeze.json`), and
  the ordering `oracle.json mtime < stdout.txt mtime` is measured in `source_manifest.json`.

## 10. Revision discipline

At most ONE `## revision r2` section may ever exist in this file. If one is appended, any recorded
"hash before the append" must be reproducible at a **real line boundary** (truncating the appended
file at the byte offset where the appended section's first line begins). No r2 section exists yet;
`revision_r2.json` proves the rule on a scratch copy and records the honest baseline.

## 11. What this oracle does NOT claim

- It does not claim any disclosure adaptation: which reported figure is a first adoption, and how a
  renewal or a replacement is separated from it, is a **professional disclosure question** — the
  calculator cannot see it (recorded as OQ-03, `disclosure_adaptation = unmapped`).
- It does not claim accuracy: no information-time sample, no baseline, no statistical uncertainty.
- The card's business negative is only partly enforceable: the pool identity and the cross-year
  continuity are enforced, but "the same TAM may not be adopted over and over" is enforced only to
  the extent that a re-count breaks the bridge. That is registered as an open question.

## errata r1 (appended by the implementer after independent review; APPEND-ONLY, the frozen body above is byte-unchanged)

- appended_utc: 2026-09-20T03:20:48.486905+00:00
- oracle_md_sha256_before_this_append: aaa7faf7bef4d3f6a3ba4e572a7cd2e704c535f0b4d5d7d0d952852e97994f01
- rule: nothing above this line was rewritten; where an erratum supersedes a sentence of the frozen body, this section says so explicitly.

### E-1 (F-04, all three cards): what the freshness chain does and does not claim

- The mtime comparison in `evidence/M30/source_manifest.json` is a **POST-HOC stat comparison**, not evidence of pre-run freezing.
- The object anchored before the generator ran is the **generator code** `scripts/oracle_M30.py` (sha256 `3177247f95f7554920ac43b4e076f28b5ef78250059c130de1f5e8dee2e4c09e`), recorded through the byte-identical pointer `iso/oracle_card.md` in `evidence/M30/oracle_document_freeze.json`.
- **This document is not part of the anchor scope and carries no gating expectation.** The pipeline never reads or validates it; every gated expectation lives in `evidence/M30/oracle.json`, which is regenerable byte-for-byte from the anchored code.
- Independent-reviewer ruling on OQ-05: it does **not** block the formula signature and does **not** require a new attempt **provided the owner claims formula only**; if the owner wants this document treated as pre-run frozen evidence, this attempt is insufficient and a re-run is required. This document must never be described as pre-run frozen evidence.

### E-3 (registration, not a fix): cross-batch gaps recorded in handoff.json

- F-01 (`run_card.py` never compares `cases.json[*].expected`) and the P3 list F-05..F-10 are batch-level concerns; they are registered in `handoff.json.cross_batch_gaps` and were deliberately **not** fixed inside this attempt.
- The exit-code convention of this batch (`0=pass / 1=harness / 2=no-verdict / 3=negative`) differs from the M05-M08 batch (`2=harness`); the difference is registered and no historical rc is rewritten.
