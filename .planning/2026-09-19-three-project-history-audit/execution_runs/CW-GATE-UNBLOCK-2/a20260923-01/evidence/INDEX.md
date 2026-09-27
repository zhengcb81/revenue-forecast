# EVIDENCE INDEX — CW-GATE-UNBLOCK-2 / a20260923-01

Predecessor evidence (READ-ONLY, cited):
`execution_runs\CW-GATE-UNBLOCK\a20260923-01\evidence\` — key raws reused:
`01-gate-crash-RED.log` `06-gate-crash-GREEN.log` (RC-1 RED/GREEN),
`20-ratchet-ALL-violations.log` (pre-fix 4-row: obs 27>6, pi 17>15, prune 27>12, new-file 0),
`20-ratchet-ALL-violations-GREEN.log` (prune 17>12 residue),
`21b-observability-CC-HEAD.log` / `22-CC-*-f39bd5a/HEAD.log` (git provenance),
`23-families-BEFORE.log` `26-families-AFTER.log` (families unchanged),
`24-CC-*-AFTER.log` `24-ruff-three.log` (F821 dying-note),
`25-ratchet-GREEN-full.log` `16b` `16c` (coverage before 85.38 + missing map),
`08-stale6-RED.log` `08a–f` `17-worker-node-GREEN.log` (test-face RED/GREEN).

This attempt's raws (`<attempt>\evidence\`):

| log | content |
|---|---|
| `10-iso-identity-check.log` | cwgu1→cwgu2 iso copy sha identity (7 pinned files) |
| `11-prune-F821-inherited-RED.log` | inherited broken prune state reproduced (F821 absent/deleted) |
| `12-prune-CC-AFTER-PR4.log` `12b` `12c` | PR4 measurement: FILE-MAX 12, ruff clean, compile clean |
| `13-ratchet-ALL-AFTER-PR4.log` | all-rows scan: 0 frozen + 0 new violations |
| `14-ratchet-GREEN-AFTER-PR4.log` | ratchet 2 passed |
| `15-MUT-prune-CC.log` `15b` `15c` | RC-2d mutation: merged split → 17>12 RED → restore GREEN |
| `16-MUT-archive-CC.log` `16b` `16c` | RC-2a mutation: merged `_write_snapshot` → 10>7 RED → restore GREEN (family 4 passed, cov ratchet 2 skipped in-suite) |
| `20-prune-test-RED-now-missing.log` | prune test lane RED (`now=` missing) |
| `21-prune-test-GREEN-now.log` | prune test after now=-only fix: 2 failed (D1 manifest-gating diagnosis) |
| `22-prune-test-GREEN-v2.log` | prune test fully adapted: 3 passed |
| `23-MUT-obs-CC.log` `23b` `23c` | RC-2b mutation: merged `_find_closing_quote` → 8>6 RED → restore GREEN |
| `24-MUT-pi-CC.log` `24b` `24c` | RC-2c mutation: merged `_parse_metadata` → 19>15 RED → restore GREEN |
| `25-MUT-testfaces-backup-shas.log` `25b` `25d` `25e` | test-face batch mutation: 9 faces reverted → 22 RED per lane → restored (shas verified) → GREEN |
| `00-RC1-GREEN-reverify.log` `00b` | RC-1 GREEN re-verify (E01 predecessor iso + E02 my iso): payload printed, rc 3 propagated |
| `E02_gate_crash_repro_myiso.py` | repro variant targeting my iso's gate |
| `30-cov-BEFORE-A-family-run.log` | family-scoped before: **85.38%** (127/141, 19/30 — reproduces the frozen 85.4% exactly) |
| `31-cov-newtests-RED-GREEN-validation.log` | the 12 new fail-closed tests: 12 passed |
| `32-cov-AFTER-A-familyunion-run.log` | family-union after: **100.0%** (141/141, 30/30, missing=[] both) |
| `33-cov-BEFORE-B-CI-equiv-full.log` | first CI-equivalent full run attempt — KILLED by session freeze at ~47% (kept for transparency) |
| `33b-cov-BEFORE-B-CI-equiv-full.log` | CI-equivalent full run (2894 items) before new tests — COMPLETED; archive entry **85.38%** (identical missing map to family-scoped) |
| `34-cov-AFTER-B-CI-equiv-full.log` | CI-equivalent full run (2906 items) after new tests — COMPLETED (2833 passed / 63 pre-existing fails / 10 skipped, 18.5 min) — judged source |
| `35-cov-BEFORE-B-AFTER-B-entries.log` | both archive entries: BEFORE-B 127/141+19/30=85.38% → AFTER-B 141/141+30/30=**100.0%**, missing=[] |
| `36-cov-GATE-95-judgment.log` | FC1204 gate check on AFTER-B's fresh coverage.json: tier1 **PASSED**, archive absent from tier2 problems (=**95-floor judgment PASS**); tier2/frozen RED on 3 OTHER modules → §7.5 NEW finding |
| `36a-VOID-stale-json-judgment.log` | VOID first judgment attempt (stale coverage.json; `--cov-data-file` unsupported) — kept for transparency |
| `37-DIAG-cworig-3modules-full.log` | attribution diagnostic: same full run with obs/pi/prune replaced by pristine CW versions (§7.5 cause a vs b) |
| `50-gate-fullrun.log` | gate 6-step + whole-gate + unique-symbols: ALL GREEN |
| `40`–`44` | changes.diff build + header check + apply-check (default + autocrlf-false probe) + content-identity 15/15 |
| `26-iso-root-config-fidelity.log` `26b` | iso-fidelity fix: tracked root config files copied; worker config test GREEN |
| `measure_cc.py` `enumerate_ratchet.py` `E01_gate_crash_repro.py` | measurement/repro tools (predecessor copies) |

### Close-out batch (attribution / last-gate), appended by the close-out pass

| log | content |
|---|---|
| `38-VOID-swap-denied-AFTER-B-only.log` | VOID: swap of BEFORE-B json into the iso was sandbox-denied; run judged AFTER-B data again. Kept for transparency, NOT used |
| `39a-cov-GATE-95-judgment-AFTER-B-control.log` | dual-judgment control arm — reproduces `36` exactly (tier1 PASS + the same 3 rows red) |
| `39b-cov-GATE-95-judgment-BEFORE-B.log` | dual-judgment arm 2 — **same 3 rows red, identical values** + archive 85.4<95 |
| `40-cov-3modules-raw-BEFORE-AFTER-plus-bound.log` | per-module raw both arms (identical) + static denominators + split upper-bound |
| `attr_3modules.py` | read-only script behind `40` (coverage 7.12 parser) |
| `45-judgment-iso-copy-identity.log` | writable judgment copy = 678 files hash-identical to the iso (0 diffs) |
| `46-zr409-extra-failure-isolated-rerun.log` | the +1 AFTER-B failure isolated: re-run green ×2; new tests write only tmp_path |
| `47-final-15-file-shas.log` | 15-file final table: before/after sha256 + bytes; changes.diff sha/bytes |
| `49-BLOCKED-pytest-tmp-sandbox.log` | pytest tmp machinery unusable in this session ⇒ no full-suite/diagnostic run here |
| `51-CI-equiv-dual-run-completeness.log` | both CI-equivalent runs COMPLETE (footer+counts); killed `33` stays VOID |
| `52-AFTER-B-failure-classification.log` | 63 failures classified: 34 missing-file / 12 relevance / 17 other; **0 in card test files** |
| `53-iso-artifacts-exist-in-CW-tree.log` | 17/18 + sibling "missing" paths EXIST in CW ⇒ iso-copy artifacts, not CI failures |
| `classify_afterB_failures.py` | UTF-16/CRLF-aware parser behind `52` |

Close-out narrative: `<attempt>\final_report.md` (sections A–F).
