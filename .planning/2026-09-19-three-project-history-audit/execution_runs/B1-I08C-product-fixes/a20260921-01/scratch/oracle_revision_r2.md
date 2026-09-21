
## Revision r2 — correction of one frozen RED expectation, recorded BEFORE the r2 RED run

**Date of revision:** written after the r1 RED run and before the r2 RED run.
**Reason:** the r1 RED run exposed an imprecision in the r1 freeze, not a defect
in the fix. This revision narrows one expectation; it does **not** relax any
security expectation and does **not** touch the r1 byte range.

### R2-1. What happened

The r1 oracle §4 marked node **R8** (`test_rem01_h_signed_record_is_repeatable_and_stable`)
as `FAIL` on the unfixed tree. In the r1 test file, R8 asserted only that the
label reads `host_signed` and that two consecutive reads are accepted. On the
unfixed tree that assertion is **trivially satisfied**: the label is set from a
boolean, no record is required, and `validate_publication_receipt` /
`validate_forecast_output` accept it. R8 therefore **PASSED** on the unfixed
tree, and the r1 RED run reported `10 failed, 2 passed` instead of the frozen
`11 failed, 1 passed`.

### R2-2. Adjudication — this is a test-strength defect, and it is fixed

The r1 R8 assertion was **too weak to measure REM-01**: a node that passes on a
tree where `host_signed` carries no signature cannot be the regression guard for
"`host_signed` must carry a verifiable record". The correct reading of the r1
freeze is the one stated in the r1 §4 table itself, which already required for
AFTER: *"label `host_signed`; record present; exact field set; signature
verifies"*. R8 is therefore **strengthened** to assert the record's presence and
its exact field set in addition to repeatability. Its r1 expectation text
("PASS after the fix") is **unchanged**; only the assertion set that measures it
was brought up to what r1 already said.

Consequence, frozen for the r2 RED run: **R1-R10 and R12 FAIL, R11 PASSES →
`11 failed, 1 passed`, runner rc 1.** R11 (`test_rem03_honest_package_still_accepted`)
is a deliberate positive control and is expected GREEN on both trees; it is the
node that proves the new gates do not break honest artifacts.

### R2-3. What this revision does NOT change

- No expectation in r1 §4 is relaxed. R8's frozen AFTER expectation is identical.
- No §3 design field, code, or rule is changed. §3.1-§3.6, the §3.4 wire
  contract, the §5 mutation table and the §6 run protocol stand as frozen.
- §7's not-closed list stands unchanged.
- The E27 code spelling, the `attestation_missing_record` message and the
  `segment base revenue mismatch` message are unchanged.

### R2-4. Honest blemish recorded

The r1 test file (sha256 `e6c0949c3b7d0d9c3bad101dc90a62cb8702dc4616715adfc2227dda60aa8f75`,
18236 bytes) was written and hashed **before** the r1 RED run, together with the
r1 oracle (`81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281`,
27697 bytes). Both r1 hashes remain recorded in `before/frozen_artifacts.json`
and `before/b1_unfixed.*` is preserved as the r1 RED run's raw stdout. The r2
test file is stronger, not different in intent: the added lines assert the
record that the r1 prose already required. This is disclosed rather than
silently re-baselined, and the r1 RED stdout is **not** overwritten.

### R2-5. Append-only proof for this revision

Recorded in `scratch/append_oracle_r2.stdout.json`:
`append_marker_offset`, `frozen_body_bytes_on_disk_now`,
`frozen_body_sha256_on_disk_now`, `frozen_body_untouched`.
