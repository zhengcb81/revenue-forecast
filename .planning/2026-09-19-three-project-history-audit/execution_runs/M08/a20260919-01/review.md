# M08 · implementer review record

Card M08 (`project_backlog`), Parent I-10. Attempt `execution_runs/M08/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `blocked`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M08/source_manifest.json` |
| B positive | `[50.0]` vs independent oracle `[50]`, within `1e-9*max(1,|e|)` | `evidence/M08/formula_result.json` |
| continuity positive | actual `[50.0, 0.0]` vs oracle `[50, 0]` | `evidence/M08/negative_results.json` |
| defaults case | actual `[65.0]` vs oracle `[65]` (not gating) | `evidence/M08/negative_results.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M08/negative_results.json` |
| D mapping | one real disclosed mapping with page, span, unit, period and PDF sha256; professional decisions written as PROPOSED only | `evidence/M08/disclosure_mapping.json`, `evidence/M08/accounting_decision.md` |
| E probe | recorded as `blocked` with the concrete reason; NOT a scenario set and NOT accuracy evidence | `evidence/M08/historical_mapping_probe.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M08/qualification.json` |

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M08.py`, which imports only `argparse`, `hashlib`, `json`, `os`
  and `decimal` (see the `import_lines` list inside `evidence/M08/oracle_selfcheck.json`).
  It never imports `model_registry` or `model_extensions`; `product_import_present` is `false`.
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations only from
  `evidence/M08/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped through a JSON
  parser - so a JSON-parser rejection cannot masquerade as a model rejection (N01a uses a real `bool`,
  N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`, `ModuleNotFoundError` and
  `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The same `run_card.py` (sha256 `fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a`) was used for M05-M08;
  there is no card-specific runner to drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = opening_backlog + bookings - cancellations + contract_changes + backlog_remeasurements - closing_backlog`
- Registry required: `['opening_backlog', 'bookings', 'cancellations', 'contract_changes', 'closing_backlog']`; optional: `['backlog_remeasurements']`; defaults: `{}`; driver_bounds: `{'backlog_remeasurements': [None, None]}`
- Rejections and their messages:
  - `NEG-CARD`: ModelRegistryError - `calculated revenue cannot be negative: project_backlog`
  - `N01a`: ModelRegistryError - `project_backlog.opening_backlog.FY2027 must be numeric`
  - `N01b`: ModelRegistryError - `project_backlog.opening_backlog.FY2027 must be finite`
  - `N01c`: ModelRegistryError - `project_backlog.opening_backlog.FY2027 must be finite`
  - `N01d`: ModelRegistryError - `project_backlog.opening_backlog.FY2027 must be finite`
  - `N02`: ModelRegistryError - `driver project_backlog.opening_backlog must contain one value per forecast year`
  - `N03`: ModelRegistryError - `missing drivers for project_backlog: opening_backlog`
  - `N04`: ModelRegistryError - `unsupported drivers for project_backlog: unknown_driver`
  - `N05a`: ModelRegistryError - `project_backlog.years must contain fiscal years`
  - `N05b`: ModelRegistryError - `project_backlog.years must contain fiscal years`
  - `CONT-BREAK`: ModelRegistryError - `project backlog continuity failed: FY2028`

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

- `OBS-BASE-IGNORED`: raised=None actual=[50.0] matches_compared=True expect_equal=None matches_expected=None
  - why: the backlog bridge ignores base_revenue at this entry point; design observation only
- `OBS-SIGN-B`: raised=None actual=[85.0] matches_compared=None expect_equal=None matches_expected=None
  - why: sign probe with contract_changes = +10: reading A gives 65, reading B gives 65, reading C gives 85; NO expectation and NO verdict is asserted
- `OBS-SIGN-NEG`: raised=None actual=[55.0] matches_compared=None expect_equal=None matches_expected=None
  - why: second sign probe with contract_changes = -20: reading A gives 55, reading B gives 95, reading C gives 55 - this probe separates reading B from A/C; NO expectation and NO verdict is asserted
- `OBS-REMEASURE-USED`: raised=None actual=[65.0] matches_compared=False expect_equal=None matches_expected=None
  - why: omitting backlog_remeasurements changes the result, so the remeasurement term is really used

## 5. Judgement calls the reviewer should attack first

1. **THE HEADLINE: a card / upstream-Plan conflict stops this card.** `card_M08.md` L42 prints
   `- contract_changes`, while `docs/buy_side_model_audit_2026-09-18.md:42` and
   `scripts/model_registry.py:228` both use `+ contract_changes` over signed amounts.
   `execution_v2/README.md:20` says a card/plan conflict must stop the affected card and correct the index,
   so `formula` is recorded **blocked** rather than passed. See `evidence/M08/card_conflict.json`.
2. **The two sign probes identify the implementation uniquely.** With `contract_changes=+10` the product
   returns `85.0`; with `contract_changes=-20` it returns `55.0`. Reading A (card arithmetic) predicts 65/55,
   reading B (card symbols over signed amounts) predicts 65/95, reading C (upstream) predicts 85/55.
   Only reading C matches both - the implementation is the upstream reading.
3. **Do not read the card's answer 50 as 'the implementation is right'.** 50 also follows algebraically from
   the upstream reading, so the card's *arithmetic* is consistent with the implementation while its printed
   *symbol* is not. The simplest explanation is a typographical sign error in the card, but that is an owner
   call, not the implementer's.
4. **The bridge is not revenue.** With the issuer's own disclosed numbers (closing 85.77, +12.75% vs 2022
   year-end, new contracts 45.82, service revenue 33.76 亿元) the bridge implies ≈36.12 亿元 of recognition,
   which is ≈2.36 亿元 (≈6.99%) away from the disclosed revenue. Three of the five flow drivers are
   undisclosed, so the residual is unexplained and must not be recognised as revenue (card L48).
5. **Registered formula string vs card text.** The registry string is the upstream `+` form; the card text is
   the `-` form. Recorded verbatim in `evidence/M08/formula_string_check.json`.

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review plus a production
  forecast-entry-point mapping reviewed independently.
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated specification,
  the existing implementation is retained.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M08.py --card M08 --out-root <attempt>` in a scratch tree and diff the generated
   `oracle.json` against the frozen one; then re-run `scripts/run_card.py` and diff `run_result.json`.
2. Confirm the isolated copy hashes still equal production (`evidence/M08/source_manifest.json`).
3. Confirm `oracle.md` was not edited after the run (hash in `commands.json` / `source_manifest.json`).
4. Pick a case the implementer did not use and freeze its expectation BEFORE running.
5. Adjudicate the DEC items in `evidence/M08/accounting_decision.md`.

---

## Exit-code self-check (shared runner; self-check performed on M05)

| case | mutation | raw rc | expected | proves |
|---|---|---|---|---|
| A | `oracle.json positive.expected_float -> [999]` in a scratch copy | **3** | 3 | a corrupted expectation cannot hide behind rc=0 |
| B | `input.json` positive driver deleted in a scratch copy | **2** | 2 | rc=2 is reachable: no verdict exists |
| C | uncorrupted scratch copy | **0** | 0 | the repaired exit code stays 0 for a genuinely passing card |

Details: `execution_runs/M05/a20260919-01/recovery/selfcheck_result.json`.

---

## revision r2 - response to the independent review

Independent review of r1: **blocked - and blocked is the correct outcome**; the reviewer explicitly rejected converting to reading C in order to reach a pass.

The nine r1 findings were handled as follows (nothing frozen was rewritten, no product file was touched):

- F-M08-01 (stale commands.json hash)
- F-M08-02 (disclosure impact anchored to reading C)
- F-M08-03 / F-M06-02 class (review.md title)
- F-M08-04 (L42 quotation corrected)
- F-M08-05 (sign-probe base_input)
- owner remediation three-step list
- OQ-04 named risk

Details per finding (file:line) are in `evidence/M08/revision_r2.json`; the OQ-02 / OQ-04 rulings are in
`evidence/M08/oq_rulings.json`; the owner's three-step index remediation for M08 is in `handoff.json`.

New hashes after r2: `oracle.md`, `commands.json`, `after/rerun_sha256.json` and `evidence/M08/*` were all
re-hashed; see `evidence/M08/evidence_hashes.json` and `after/rerun_sha256.json`.

Status after r2: `formula` = blocked, `disclosure_adaptation` = unmapped, `accuracy` = unproven.

---