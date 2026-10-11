# Model Generalization Matrix (`tools/model_generalization_matrix/`)

A finite, repeatable stress-test matrix over the **native revenue engine's
cross-mechanism combinations** (M01–M08).  It gives the parent G4/G5 new-company
forecasts *mathematical-boundary* evidence: each combination is exercised with a
legal vector and a counter/unknown vector, and the engine's output is compared to
an **independent hand-computed oracle**.

This is **not** a second forecast engine and **not** a buy-side accuracy claim.

* `source_truth_verified = false`
* `economic_reasonableness = not_evaluated`

Every case runs the real draft engine (`revenue_core.run_forecast(..., mode="draft")`)
or a real native entry (`convert_input_quantity`, `build_support_diagnostics`,
`period_flow_months`).  No network, no source DB, no third-party packages.

## Combination classes

| class | combination | boundary checked |
|---|---|---|
| M01 | quantity × price × currency/unit | scaling preserves economic amount; explicit currency labels; mixed units refused or explicitly converted (never auto-FX) |
| M02 | ARR stock → recognition + late contract/churn | closing ARR is not full-year revenue; missing driver refused, never zero-filled |
| M03 | capacity/demand/launch fraction | demand capped by capacity; launch fraction applied once; zero capacity → finite 0 |
| M04 | dated calendar H1 evidence flow | real native coverage of a partial window; out-of-window flow refused |
| M05 | zero-base commercial launch + CAGR | zero-base revenue computable; CAGR from a 0 base is `null`, never 0 |
| M06 | shared timing shock and sum cap | one shared shock applied exactly once, delta conserved; fixed shared cap that would force Low≤Base≤High is refused, not reordered |
| M07 | annual/run-rate management target | a comparable annual target keeps its value; a run-rate/period-end target is not re-labelled as the current annual figure |
| M08 | optional operating support + segment/year/scenario | support is scoped per cell; one calibrated cell never presumes another; unknown stays `null` |

Each class has ≥1 legal vector and ≥1 counter/unknown vector — 16 cases total.

## Independence guarantee

`oracle.py` computes every expected value from the **frozen `drivers`** using the
documented formula or a hand conservation law.  It never imports or calls the
engine under test.  Wrong values for declared assertions are detected; undeclared boundaries remain unverified.  The
runner keeps `expected` and `observed` strictly separate and never marks a case
that did not execute as `PASS`.

## Run

```bash
# Full matrix (offline).  --owned-root is scratch space (restored to absent);
# --out-root receives the report.
python -B tools/model_generalization_matrix/run.py \
    --owned-root ABS_NEW --out-root ABS_NEW

# Also drive the shipped CLI once (legal + rejection) and the support CLI once.
python -B tools/model_generalization_matrix/run.py \
    --owned-root ABS_NEW --out-root ABS_NEW --e2e
```

Centralized fast tests:

```bash
python -B -m pytest -q tools/tests/test_w07_model_generalization.py
```

## Output

`model-generalization-matrix/1` written to `--out-root` as
`model-generalization-matrix.json` and `.md`, containing per-case
`case_id/vector/mode/expected/observed/assertions/status/native_refs/diagnostics`,
top-level counts, actual timings, the cleanup/recovery record (scratch restored to
absent; read-only SHA unchanged), and residuals.  When `--e2e` is passed it also
carries the real CLI legal/reject and support-CLI results.

## Modules

* `bootstrap.py` — imports the shipped engine interfaces (no re-implementation).
* `native.py` — thin adapter recording each native call (request/result/exception + JSON pointer).
* `oracle.py` — standalone hand-computed oracle (driver → expected).
* `cases.py` — frozen CaseSpec: 16 vectors with `drivers`, builders, `observe`, `expected`.
* `runner.py` — runs each case against the real engine and compares to the oracle.
* `report.py` — assembles `model-generalization-matrix/1`.
* `run.py` — public entry; isolated temp handling + cleanup recovery.

## ROOT reception scope and remaining coverage

Execution `status=COMPLETE` means all **declared** vectors, requested CLI checks,
readonly hashes and scratch restoration passed. It does not certify the whole
construction card. `combination_coverage.status=PARTIAL` explicitly lists:

- CNY/HKD label and same-currency scaling vectors beyond current USD scale test.
- Acquisition/control, non-calendar cross-FY and missing-quarter ancestry.
- Correlated joint volume/price scenarios beyond a timing delay and sum cap.
- Cumulative target, net presentation and cannibalization.
- Future actual/WAPE null through final draft output beyond observed-range null.

Those are remaining ROOT planning items, not `NOT_SUPPORTED` claims about the
native engine. No fake API or copied forecast engine substitutes for them.

Each case now retains only its own actual native request/result and exceptions.
The 16 inputs are synthetic and bounded; this payload retention must not be
copied into real-company processing. Output must be a new directory, prior
evidence is never overwritten. Newly created scratch parents are removed and
existing sentinel contents remain. Infrastructure errors cannot be contract
rejections. Missing unknown fields, empty assertions/case sets, incomplete
vectors, CLI failure, readonly drift and cleanup failure cannot give success.

ROOT focused tests: `python -B -m pytest -q tools/tests/test_w07_model_generalization.py tools/tests/test_root_w07_model_boundaries.py`.
The complete matrix remains a manual milestone; no new per-commit/CI gate.
