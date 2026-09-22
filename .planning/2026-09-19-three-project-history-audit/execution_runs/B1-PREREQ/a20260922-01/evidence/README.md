# Evidence protocol — B1-PREREQ (freezes REM-43 / review F4)

This directory is **write-once per label**. It exists so that every RED/GREEN
arm of this attempt is independently auditable from raw bytes, which B1's r1
RED run was not (its stdout was overwritten before archiving).

## Rules (frozen in `oracle.md` §3.4 before any run)

1. Each run gets a **distinct label**; outputs are
   `evidence/<label>.stdout.txt`, `evidence/<label>.stderr.txt`,
   `evidence/<label>.rc.txt`, captured byte-forbatim by
   `runner/run_arm.ps1`, which **refuses to run a label whose files already
   exist** (exit 99). Re-runs use a new label and are disclosed in
   `handoff.json`.
2. Probes, append proofs and integrity checks print to stdout and are captured
   the same way (labels: `probe_e21`, `append_r5`, `append_r6`, `m6_build`,
   `final_integrity_check`).
3. `SHA256SUMS.txt` pins every byte stream here after the runs complete.
4. `commands.json` (byte-frozen in `freeze.json`) records argv + **expected**
   outcomes; observed outcomes live in `handoff.json` + these raw files —
   never by editing frozen files.

## Disclosed historical gap (NOT closable, NOT claimed closed)

B1's r1 RED stdout ("10 failed / 2 passed" — the warrant for oracle revision
r2) and the r1 test file (18236 B / `e6c0949c…`) were overwritten/removed
before archiving. `SRC/before/b1_unfixed.stdout.txt`
(30580 B / `58863ffb…`) is the **final** 11-failed/1-passed output, not r1's.
No later card can recreate those bytes; the gap stays open and disclosed
(oracle §3.4 item 4, `decision.md` §F4).

## Labels used by this attempt

| label | arm | expected |
|---|---|---|
| `arm1_node_on_fixed` | R13-equiv node on `SRC/iso/fixed/rf` | 2 passed, rc 0 |
| `arm2_node_on_m6` | R13-equiv node on the M6 mutant | 1 failed + 1 passed, rc 1 |
| `arm3_frozen12_on_m6` | B1's frozen 12-node file (byte-identical copy) on the M6 mutant | 12 passed, rc 0 (blind spot `{}`==`{}`) |
| `arm4_node_on_unfixed` | R13-equiv node on `SRC/iso/rf` | 1 failed + 1 passed, rc 1 |
| `probe_e21` | E21/result_sha256 feasibility probe (read-only) | rc 0, JSON report |
| `append_r5` / `append_r6` | SRC oracle append-only proofs | `frozen_prefix_untouched: true` |
| `m6_build` | mutant construction proof | pre-hash match, single-file delta |
| `final_integrity_check` | SRC pins + production zero-write + 10-field measurement | all match |
