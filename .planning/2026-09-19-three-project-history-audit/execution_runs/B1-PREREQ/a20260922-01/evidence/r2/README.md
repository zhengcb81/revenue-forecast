# evidence/r2 — record-only correction round (B1-PREREQ `a20260922-01`, revision **r2**)

Round purpose: close the independent review's **`changes_required`** verdict
(`../reviewer_report.md`, 25883 B, sha256 `e25a2c837009aebf4be542a89cafa13e78a0dae59b3556a7766ae8bb397376f6`):
blocker **F-REV-B1P-01**, plus **F-REV-B1P-02** (F6 wording), **F-REV-B1P-03**
(probe docstring), **F-REV-B1P-04** (disclosure carried), **F-REV-B1P-05**
(`changes.diff` comment).

**Round invariants:** no product/iso/production byte written; git read-only
subcommands only; no arm and no probe re-executed; `handoff.json.status` stays
`review_pending`; nothing self-signed. The r1 evidence set
(`../SHA256SUMS.txt`, every r1 label) is byte-untouched — everything this
round produces lives in this directory under its own manifest
(`SHA256SUMS_r2.txt`, which excludes itself).

## Index

| file | what it is |
|---|---|
| `r2_01_b1_unfixed_stdout_facts.json` | F-REV-B1P-01 fact 1 recomputed: 30580 B / `58863ffb…`, UTF-16LE+BOM, **10 FAILED / 2 PASSED**, summary `10 failed, 2 passed in 8.18s`, **no** `11 failed, 1 passed` — the file IS r1's RED stdout |
| `r2_01b_stdout_line_refs.json` | failure-block line refs `268,296,323,348,372,407,438,460` = the r1 test file's refs |
| `r2_02_git_history_b1_unfixed_stdout.json` | fact 2: single commit `980c9b7a` (2026-09-21 21:16:24); `ls-tree` blob == `hash-object` working bytes; porcelain clean; `rev-list` count 1 |
| `r2_02b_git_history_test_file.json` | `test_b1_rem.py` history: commits `980c9b7a` + `1bddfc1e`; working file 20631 B / `636b43c8…` |
| `r2_02c_reachable_blob_states.json` | every reachable **blob** per path: stdout → only 30580 B / `58863ffb…`; test file → 18611 B / `da3d29bf…` + 20631 B / `636b43c8…`, **no 18236 B / `e6c0949c…`** |
| `r2_03_provenance.json` | fact 3: mtimes 21:14:45 (stderr) / 21:15:12 (stdout) / 21:15:35 (r2 warrant); B1 `handoff.json` lines 110 / 137 / 198 verbatim |
| `r2_04_src_oracle_pre_r7_state.json` | pre-r7 SRC oracle: 47538 B / `a8f192f1…`, six pins matched, markers r2–r6 exactly once, no r7 yet |
| `r2_05_f6_procedure_sources.json` | F-REV-B1P-02 sources: this probe lines 225–251 (rewrite-only + restore control), SRC `probe_attest.py:218-240` (rewrite **+** `canonical_sha256` recompute), `revenue_report.py:343-347 + 507-509` |
| `r2_06_false_claim_locations.json` | where the false F4 sentence actually lives (SRC oracle/decision/handoff: **absent**; SRC reviewer report + this attempt's carriers: present) |
| `r2_07_append_r7_dryrun.json` | dry-run of the r7 append — no write; `dry_run_would_pass: true`, marker would sit at 47539 |
| `r2_08_append_r7_proof.json` | proof from the frozen append tool (`scratch/append_oracle_r7.stdout.json` copy): post 57911 B / `6e344a20…`, `frozen_prefix_untouched: true` |
| `r2_09_post_append_verification.json` | **four-prefix recompute** (27697/31081/35840/39287 all match) + post-r5 (43298) + post-r6 (47538) pins, marker offsets, single occurrence of every revision heading — r1–r6 untouched |
| `r2_10_probe_docstring_fix.json` | F-REV-B1P-03 byte history: frozen `10365 / 5c9f4508…` → r2 `10383 / 5f53f5bb…`; `no_other_byte_changed: true` |
| `probe_e21_binding.py.frozen_pre_r2_5c9f4508.py` | byte-exact copy of the **frozen/executed** probe (the bytes `freeze.json` entry `my_probe_e21` pins and that produced `../probe_e21.stdout.txt`) |
| `r2_11_final_integrity_check_post_r7_prefixefix.{json,stderr.txt,rc.txt}` | boundary tool (frozen `final_integrity_check_v2.py`) run **after the r7 append, probe at its pinned bytes**: rc **0**, `all_ok: true`, 14/14 incl. `freeze_chain_verifies` — proves the r7 append breaks no F5 check |
| `r2_12_final_integrity_check_post_docstring_fix.{json,stderr.txt,rc.txt}` | boundary tool run **after the commissioned docstring fix**: rc 1, `failures: ["freeze_chain_verifies"]`, detail `my_probe_e21: live 5f53f5bb… != 5c9f4508…`; the other 13 checks pass — the ONE deliberate, disclosed freeze-pin divergence of r2 |
| `r2_13_boundary_unchanged.json` | round-end boundary scan: production git porcelain (scripts/tests/config/artifacts) EMPTY, rc 0; SRC files modified since 2026-09-22 = **exactly `oracle.md`** (the r7 append); 4 production anchors + 4 fixed-tree pins + both B1 `before/` pins re-hash equal; trust file absent — `all_checks_pass: true` |
| `r2_14_false_carrier_addendum.json` | full-carrier scan of the refuted F4 wording across this attempt's text files: carriers = `oracle.md` (frozen), `decision.md` §F4, `handoff.json`, `binding.json` open-disclosures, **`evidence/README.md` lines 5/23–30 (frozen — cannot edit)**, `recovery/README.md` (corrected in place with verbatim retention), `changes.diff` context |
| `README.md` | this file |
| `SHA256SUMS_r2.txt` | manifest of every file here except itself |

## Disclosed measurement sequence (probe bytes)

1. docstring fix applied (state recorded in `r2_10…`);
2. probe **temporarily restored** to its frozen bytes (byte-exact copy from
   this directory) so the post-r7 boundary measurement `r2_11…` isolates the
   r7 effect — `all_ok: true`;
3. fix **re-applied** with the same tool and assertions → identical result
   (`5f53f5bb…`), then `r2_12…` captures the sole expected mismatch.

No other file was restored, moved or rewritten; r1 evidence labels were never
touched at any point.
