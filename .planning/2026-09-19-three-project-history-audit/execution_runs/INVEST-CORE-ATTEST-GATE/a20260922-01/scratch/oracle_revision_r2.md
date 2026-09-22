

---

## Revision r2 (append-only; r1 byte range untouched)

Appended after IC-c3/IC-c4, i.e. after the first regression measurements, to
execute the two commitments r1 §5 pre-registered. **No r1 security
expectation is relaxed by this revision**: the node table (§4), the mutation
declaration (§6) and the boundaries (§10) are untouched. Proof of append-only:
sha256 of `oracle.md[0:16936]` remains
`7eaf81b925f21c21ba3f320111f3ea57c54dd74292a4ec5697111d0476f47796`
(the frozen r1 digest), recorded in `scratch/append_oracle_r2.json`.

### r2.1 — §5 pristine contingency ACTIVATED (measured baseline recorded)

Measured pristine arm (UNFIXED consumer, `before/suite_pristine.stdout.txt`,
raw rc 1): **6 failed / 35 passed / 1 skipped / 7 subtests passed**.

The six failures: `test_company_adapter_copies_validated_paths`,
`test_management_target_summary_is_hashed_and_transferred`,
`test_segment_adapter_copies_recognized_revenue`,
`test_segment_adapter_prefers_revenue_owned_effective_path`,
`test_tampered_forecast_is_rejected`,
`test_unregistered_anchor_opt_out_is_explicit_and_traced`.
Every one is the PRE-EXISTING default-policy rejection: in a clean
environment (no `REVENUE_ATTESTATION_PROVIDER` anywhere — verified at IC-c0)
`run_forecast` fixtures are `unattested`, and these six tests expect
`adapt_revenue`'s default `require_attestation=True` to SUCCEED
(`test_tampered_forecast` fails only because the `unattested` rejection
preempts its expected `invalid revenue forecast` message). This is
pre-existing suite behavior in a clean environment — it reproduces on the
UNFIXED consumer, so this card cannot be its cause. Fix-attribution is
therefore by DELTA pristine→fixed, exactly as the r1 §5 contingency
prescribes.

### r2.2 — §5 fixed-arm declared set CORRECTED from 2 to 3 (r1 under-count disclosed)

Measured fixed arm (`after/suite_fixed.stdout.txt`, raw rc 1):
**9 failed / 32 passed / 1 skipped**. Delta vs pristine =
**exactly 3 new failures, 0 disappeared** (Compare-Object of the FAILED
lists), all three raised through `verify_host_signed_attestation` with the
identical coded message `attestation_missing_record … (E27)`:

1. `test_current_revenue_workflow_receipt_is_transferred` — **as declared in
   r1** (the mutator: it rebuilds a receipt with `attestation_status=
   "host_signed"` via production `build_publication_receipt`, which cannot
   carry a record; fails at its own `adapt_revenue` call, test line 130).
2. `test_growth_driver_summary_tampering_is_rejected` — **as declared in r1**
   (cascade: consumes the module-cached `"growth"` fixture the mutator
   mutated in place).
3. `test_growth_driver_tree_is_hashed_and_compacted` — **NOT declared in r1**.
   Same root cause, same cache: alphabetical method order runs the mutator
   first, and this is the SECOND later consumer of the polluted cached
   fixture (`growth_driver_summary` < `growth_driver_tree`; r1 counted only
   the first). Disclosed as an r1 under-count of the declared cascade, not
   absorbed silently. No test byte changed in either arm — `tests/` and
   `tests_support/` are byte-identical across arms (5/5 files,
   `after/tests_identity.json`).

The authoritative fixed-arm expectation is now: 6 pre-existing failures (r2.1)
+ these 3 fix-attributable failures = 9 failed, rc 1, with `tests/`
unmodified. Reviewer adjudication requested specifically on r2.2: is
counting the third cascade consumer as the same declared root cause
legitimate, or should the mutator test's in-place fixture mutation be called
out separately as a test-design finding against the shipping suite?
