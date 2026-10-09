# W05 implementation handoff

Functional commit: `5bcee2f5e2eb4617c24ab19b7a528335823f8d89`; base: `a7c2c73758e7b7bbb6454c2955390f179f2d5f28`.

Quarterly range and YoY targets now use typed comparison bases. Quarterly observations map to used native revenue parameters for that exact measurement period and scenario; no x4 conversion. YoY uses each scenario's own prior-period revenue. Raw statement/date/unit remain visible; any derived monetary benchmark is labeled `analyst_derived`. Missing/zero denominator stays null with a reason. Legacy annual target output and the five golden hashes are unchanged.

Checked scopes record category, interval, selected/read business originals, skipped items and reasons. Partial coverage produces `incomplete`. Opt-in legacy diagnostics report `semantically_unverified`; source presence does not establish completeness. These diagnostics do not authorize model access or impose human review.

## Actual verification

- RED: 6 failed / 1 passed, 0.57s, exit 1.
- GREEN: 66 passed, 3.06s, exit 0; exact commands and path hashes in `handoff.json`.
- Ruff `--no-cache` PASS; mypy seven public contract files PASS.
- The actual native CLI fixture recipe ran validate-only, compute/render and immutable snapshot, all exit 0. Inputs are synthetic engineering arithmetic fixtures, not a current company forecast.
- Normal git commit. Configured `.githooks` directory is absent in this worktree; no hook ran. MAIN owns canonical pre-push/CI. No hook copied, installed or bypassed.

## Reproduce

`python -X utf8 -B tools/run_target_measurement_e2e.py --input <typed-input.json> --output-root <absent-owned-output>`

The new contract is documented in `references/target-measurement-comparison.md`. No installation was performed. MAIN should install the exact runtime closure in the JSON while preserving config/output.

All tests used a short initially absent owned TEMP restored absent in finally. New supplier/model/download calls: 0. Raw originals, sealed audit outputs and adjacent repositories unchanged. Live economic adequacy, current official reads and M2 remain MAIN responsibilities.

## Honest boundary and category follow-up

Functional commit `cbbb0c2f3495ae6b038a553672c338c86d52282d`. RED 1 failed / 11 passed, 1.51s; GREEN 13 passed, 1.33s, exit 0. An annual filing at the interval start does not prove subsequent announcement content complete. A filing cannot prove a checked call category. These produce `incomplete` diagnostics, not model-access or human-approval gates. Ruff --no-cache PASS; normal commit executed no missing hook.

Current integrated path hashes and both installed old/new SHA values are in the JSON. W06 also extends the shared renderer; its SHA is therefore the integrated branch value. No installation or live research run was performed.
