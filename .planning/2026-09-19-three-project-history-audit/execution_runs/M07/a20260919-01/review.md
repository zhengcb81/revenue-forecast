# M07 · implementer review record

Card M07 (`services`), Parent I-10. Attempt `execution_runs/M07/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M07/source_manifest.json` |
| B positive | `[122.0]` vs independent oracle `[122]`, within `1e-9*max(1,|e|)` | `evidence/M07/formula_result.json` |
| continuity positive | actual `[122.0, 165.00000000000003]` vs oracle `[122, 165]` | `evidence/M07/negative_results.json` |
| defaults case | actual `[120.0]` vs oracle `[120]` (not gating) | `evidence/M07/negative_results.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M07/negative_results.json` |
| D mapping | one real disclosed mapping with page, span, unit, period and PDF sha256; professional decisions written as PROPOSED only | `evidence/M07/disclosure_mapping.json`, `evidence/M07/accounting_decision.md` |
| E probe | recorded as `blocked` with the concrete reason; NOT a scenario set and NOT accuracy evidence | `evidence/M07/historical_mapping_probe.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M07/qualification.json` |

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M07.py`, which imports only `argparse`, `hashlib`, `json`, `os`
  and `decimal` (see the `import_lines` list inside `evidence/M07/oracle_selfcheck.json`).
  It never imports `model_registry` or `model_extensions`; `product_import_present` is `false`.
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations only from
  `evidence/M07/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped through a JSON
  parser - so a JSON-parser rejection cannot masquerade as a model rejection (N01a uses a real `bool`,
  N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`, `ModuleNotFoundError` and
  `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The same `run_card.py` (sha256 `fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a`) was used for M05-M08;
  there is no card-specific runner to drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = billable_capacity * utilization * billing_rate * timing_factor + other_revenue`
- Registry required: `['billable_capacity', 'utilization', 'billing_rate']`; optional: `['timing_factor', 'other_revenue']`; defaults: `{'timing_factor': 1.0}`; driver_bounds: `{}`
- Rejections and their messages:
  - `NEG-CARD`: ModelRegistryError - `driver services.utilization must be between 0.0 and 1.0: FY2027`
  - `N01a`: ModelRegistryError - `services.billable_capacity.FY2027 must be numeric`
  - `N01b`: ModelRegistryError - `services.billable_capacity.FY2027 must be finite`
  - `N01c`: ModelRegistryError - `services.billable_capacity.FY2027 must be finite`
  - `N01d`: ModelRegistryError - `services.billable_capacity.FY2027 must be finite`
  - `N02`: ModelRegistryError - `driver services.billable_capacity must contain one value per forecast year`
  - `N03`: ModelRegistryError - `missing drivers for services: billable_capacity`
  - `N04`: ModelRegistryError - `unsupported drivers for services: unknown_driver`
  - `N05a`: ModelRegistryError - `services.years must contain fiscal years`
  - `N05b`: ModelRegistryError - `services.years must contain fiscal years`
  - `CONT-BREAK`: ModelRegistryError - `services.years must be consecutive and increasing`

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

- `OBS-BASE-IGNORED`: raised=None actual=[122.0] matches_compared=True expect_equal=None matches_expected=None
  - why: rowwise calculator discards base_revenue; design observation only
- `OBS-DEFAULT-EQUIV`: raised=None actual=[120.0] matches_compared=True expect_equal=None matches_expected=True
  - why: explicit 1/0 equals the omitted default; makes the documented default falsifiable

## 5. Judgement calls the reviewer should attack first

1. **The utilisation denominator is not disclosed.** 93.5% is printed, but not whether the denominator is
   average or period-end capacity. In a year with capacity expansion the two differ materially. The mapping
   records the ratio as `reported` and the denominator question as DEC-M07-2.
2. **`billable_capacity` is a LOWER BOUND, annualised by the implementer.** The report says monthly capacity
   *exceeded* 1 million 8-inch-equivalent wafers; multiplying by 12 is an implementer assumption, labelled
   `derived`, and it ignores intra-year additions. A reviewer could reasonably reject this as not being the
   issuer's own annual figure.
3. **The implied billing rate (≈6,000.27 CNY/wafer) is arithmetic, not a driver.** It mixes the capacity lower
   bound, the utilisation ratio and a revenue figure that includes non-wafer items. Reading it back into the
   formula reproduces the disclosed revenue by construction - a constructive identity, not a reconciliation.
4. **Mapped-driver count, stated precisely.** Of the 3 required drivers, 1 is `reported` (`services.utilization` = 93.5%) and 1 is `derived` (`services.billable_capacity`, an annualised capacity LOWER BOUND built by the implementer), and 1 is `missing` (`services.billing_rate`). The `mapped_vs_missing` counter in `disclosure_mapping.json` counts only the `reported` one (1/3); counting `derived` as mapped would give 2/3, and this review does NOT do that, because `derived` rests on an implementer assumption rather than on an issuer statement.

5. **Isolated-checkout provenance.** I-00-B binds the isolation *plan* and the two-stage command rule but
   does not materialise a checkout tree; this attempt therefore materialises its own read-only snapshot
   (`iso/checkout_scripts`, hashes equal to production). If the intended binding is a checkout materialised by
   I-00-B, that is a scope deviation to record - the code under test is byte-identical either way.
6. **Disclosure receipt strength.** Unlike the cninfo sidecars used by M01, the company-wiki sidecars for
   these documents carry no publisher content hash, so `local_hash_matches_publisher_receipt` is
   `NOT_VERIFIABLE` for all four cards. Stated as a gap.

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review plus a production
  forecast-entry-point mapping reviewed independently.
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated specification,
  the existing implementation is retained.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M07.py --card M07 --out-root <attempt>` in a scratch tree and diff the generated
   `oracle.json` against the frozen one; then re-run `scripts/run_card.py` and diff `run_result.json`.
2. Confirm the isolated copy hashes still equal production (`evidence/M07/source_manifest.json`).
3. Confirm `oracle.md` was not edited after the run (hash in `commands.json` / `source_manifest.json`).
4. Pick a case the implementer did not use and freeze its expectation BEFORE running.
5. Adjudicate the DEC items in `evidence/M07/accounting_decision.md`.

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

Independent review of r1: **accepted_scoped (formula qualification only)**.

The nine r1 findings were handled as follows (nothing frozen was rewritten, no product file was touched):

- F-M07-01 (source_manifest wording)
- F-M07-02 (mapped vs derived driver count)
- OQ-02 ruling

Details per finding (file:line) are in `evidence/M07/revision_r2.json`; the OQ-02 / OQ-04 rulings are in
`evidence/M07/oq_rulings.json`; the owner's three-step index remediation for M08 is in `handoff.json`.

New hashes after r2: `oracle.md`, `commands.json`, `after/rerun_sha256.json` and `evidence/M07/*` were all
re-hashed; see `evidence/M07/evidence_hashes.json` and `after/rerun_sha256.json`.

Status after r2: `formula` = review_pending (point review of r2), `disclosure_adaptation` = unmapped, `accuracy` = unproven.

---