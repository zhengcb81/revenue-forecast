# review.md — I-07-D-REPRO a20260923-01 — verdict TRANSCRIPTION (carrier landing)

## Verdict block

**VERDICT = `accepted_scoped`** — scope = the D3 objective + the card's own frozen
oracle §7 attack list, with 3 findings (1 MEDIUM, 2 LOW). This file is a
**transcription-only** landing written by the carrier: the verdict is AUTHORED by the
independent reviewer (separate face from the implementer; the implementer never signs
acceptance, no self-signing anywhere in this landing — the reviewer's own verdict file
remains `reviewer_report.md`, whose write boundary was report + `.sha256` sidecar only).

- **Carrier pin**: `reviewer_report.md` = **28058 B**, sha256
  `db051f23305deb8e18c65bb69b42195869cac7f23549d217f946bbdde5a84cfb` — re-hashed at
  landing, equals the `reviewer_report.sha256` sidecar content (sidecar file itself:
  86 B, sha256 `7c40cbe95aab02d729c4d0a0dcf9ab149a6cb2df31ea843dd9250e7eecd32d3e`).
- **N = 1** — one independent reviewer; the report's method boundary: read/grep/pwsh
  only, zero product writes, zero state-changing git, no network, REM-79 self-check
  exit 0 (0 violations).
- **Verified section byte ranges inside the pinned report (UTF-8 bytes)**: VERDICT line
  450–531; §9 Findings header 20769–20813 (Findings sub-header 20816–20854; F-01
  20857–22021; F-02 22022–22383; F-03 22384–22936); Observations header 22937–22967;
  Rulings header 23658–23690 (R-1 23693–24278; R-2 24279–24419; R-3 24420–24565);
  Unverified/limits header 24566–24599; §10 Scope-if-accepting 25502–25551
  (`**D3 = FIXED**` marker 25580–25593).
- **Handoff pre-image at landing**: `status = "review_pending (implementer never signs
  acceptance)"`, `reviewer_status = "review_pending / unsigned /
  verdict_is_transcribed_not_authored"`, 7025 B, sha256
  `cefe4567e4bcb3f4bfe32b6b33e9fd976a5629314bfe6f4d5a1ff128872592bd` (flip recorded in
  handoff.json: status → accepted_scoped + status_before + status_authority).

## Attack results transcribed from the pinned report (8/8)

1. **Attack 1 — deliverables + oracle frozen-first: PASS.** Freeze order (mtimes):
   `oracle.md` 22:45:47 → `binding.json` 22:48:00 → snapshot_before 22:48:40 → cell
   build 22:48:45-58 → wprobe 22:49:13 (`zero_insert_proof:true`) → first judged run
   22:49:27 (N=9 judged product runs) — oracle (live sha `b320ebdd…267`, 20989 B ==
   decision §1) + binding precede judged-run-1; oracle §7 attack list self-evidently
   predates results. **Copy-fidelity 9/9 byte-equal** (I-07-D original vs this attempt's
   copy, equal to both binding pins AND the live originals). **Argv verbatim**:
   `CMD-REPRO-F02/F03/F04` argv arrays equal I-07-D's `CMD-D-*`
   (`["<PY>","harness/run_d_matrix.py","f02"|"f03"|"f04"]`), expected rc tables equal
   ({0,3,0,3} / {1,0} / {3,0,3}), nested product argv == `product_argv_forms_frozen`,
   F04 kill-manifest argv[0] + tail byte-equal to I-07-D's verdict manifest.
   `changes.diff` EMPTY substantiated independently: 20 hashed anchors `changed: []` +
   6 plan pins re-hashed 6/6 at corrected paths → "26/26 unchanged (not 26 hashed)" is
   accurate; **0 product hunks**, writes confined to `ATT/**` + `%TEMP%\i07d/**`;
   handoff pre-image `review_pending/unsigned` + N=7 declarations present ✓;
   recovery/README + evidence/ complete (raws_manifest, repro_verdicts,
   scratch_gone_recompute_proof, snapshots, anchor_compare, wprobe, build
   `product_edits: 0`).
2. **Attack 2 — preserved-raws re-hash: PASS (10/10).** All 10 files re-hashed live
   against `raws_manifest.json` triplets (sha256 + bytes): raw `ffd73376…2da7c`
   4405561 B ×4 (F02, F03, F04 staged fetch, F04 canonical), state2 sidecar
   `8228741d…8da71` 2590 B ×2 (F02/F03), F04 product provenance `e26fb2ef…25b22`
   2361 B, 3 × `catalog.sqlite3` (290816 / 282624 / 245760 B). **Byte-link**: those shas
   are exactly what I-07-D itself recorded (decision L48/L50/L194 + oracle L111; sidecar
   pinned in I-07-D `initial_state.json` + `build_iso.py` L59) — two independent raw
   byte-links for F04. Preserve-immediately-per-case ordering holds via directory mtimes
   22:51:24 / 23:00:46 / 23:08:34 (each after its run, before the next case).
3. **Attack 3 — reviewer's OWN recomputes: PASS, verdict equality ×3.** Method kept
   write-free inside the attempt: `robocopy` clone → `%TEMP%\i07drepro_revclone`, input
   copy-fidelity verified (3 × `verdict_recomputed_from_preserved.json` sha-equal in
   clone), same venv Python 3.13.9, `TEMP/TMP/TMPDIR = \\?\<ATT>\evidence\preserved\temp`,
   and `%TEMP%\i07d` renamed away during each run. Results: **f02v rc0**
   `{"cell":"F02","all_ok":true,"failed":[]}` structurally identical to their recorded
   file (`decided_at` aside); **f03v rc3** re-measures the SAME single red
   `lock_held_across_scan` (10/11) — checks/raw_rcs/model_prediction_checks equal;
   **f04v rc0** `all_ok:true, killed:1, failed:[]` identical (only
   `trigger.committed_raw_path` = scratch vs preserved, exactly their claim).
   Attempt's `verdict*.json` mtimes untouched (spot-checked).
4. **Attack 4 — scratch-absent reproduction: PASS.** Their
   `scratch_gone_recompute_proof.txt` (f02v rc0 / f03v rc3 same red / f04v rc0 killed1)
   consistent with the reviewer's own runs; live state `%TEMP%\i07d` present +
   `i07d.scratch-gone-proof` absent matches decision §6.3; **the reviewer re-ran all
   three recomputes with scratch ABSENT himself** (each succeeded against the preserved
   tree alone, scratch restored + re-verified after) ⇒ D3's dual re-computability proof
   (TEMP-redirect AND scratch-absent) independently reproduced, not merely transcribed.
5. **Attack 5 — bidirectional tables: PASS (mechanical scripts, one honest gap = F-01).**
   REPRO→I-07-D: **F02 MATCH** across invariants (check-key set 15/15, red `[]`,
   `raw_rcs {0,3,0,3}`, fault 7-key delta shape, **`trigger.error_details` byte-identical**
   incl `PermissionError: [Errno 13]` + `root_id company_raw` + `unchanged:false`, hold ∩
   scan1 margins 0.088 s / 0.126 s, recovery `scan2` delta **byte-equal to I-07-D's own
   scan2 evidence**, provider 0/0, D-1 `model_prediction_checks:false` equal);
   **F03 MATCH on invariants with the single recorded red** `lock_held_across_scan`
   (11/11 → 10/11, `all_ok` false vs true — divergence is exactly one check, never
   re-run to green), `raw_rcs {1,0}`, error_doc semantics equal, recovery delta
   byte-equal, `hold_s 75.0`, elapsed 56.406 s vs 34.515 s both ≥25 s gate (record-only);
   **F04 MATCH** (15/15, `raw_rcs {3,0,3}`, kill count 1, **gate checks identical 5/5** =
   `manifest_present, manifest_path_in_argv, manifest_path_in_cwd, alive_before:true,
   alive_after:false`, `kill {ok:true, exit_code_set:4242}`, `released_marker_present:false`,
   `timed_out:false`, 4242 chain in product's own stderr with `error_code:"upstream"`,
   `raw_sha_after:null`, counters `{provider:2, scan:1}`, canonical ≠ manifest name = D-3
   quirk reproduced). I-07-D→REPRO: every transcribed invariant has a REPRO counterpart —
   **sole exception = I-07-D §6's census kill-scope proof (`real_source_catalog_gone=0`)
   → finding F-01**; §7.1 correctly scoped OUT of the comparison (not a target, not
   re-created).
6. **Attack 6 — F03 root cause: CONFIRMED at source; no verdict-chasing.** Exact
   numbers: driver mark 21:57:46.049762 → `locked_at` 21:57:47.113789 = **1.064027 s**
   (their "1.06 s" exact); spawn ≈21:57:44.05 → BEGIN EXCLUSIVE = **≈3.064 s** (their
   "3.06 s" exact) with the frozen `f03_runs` `time.sleep(2.0)` immediately before the
   mark at `run_d_matrix.py` **L1153-1154** (their byte-identical harness copy); frozen
   formula L1199-1211: `47.113789 < 46.049762` = false ⇒ marker-placement artifact, not
   product semantics; mechanical containment: spy scan event pid 26128 @21:57:59.73
   (12.616 s after lock) + run end 21:58:43.62 both inside hold
   [21:57:47.113789, 21:59:02.145573], and the `database is locked` error after the
   56.4 s wait is only possible against the held single-holder BEGIN EXCLUSIVE; I-07-D's
   original flipped true (lock +1.95 s < its mark). **Single-window no-rerun proof**:
   F03 evidence within 22:57:46→23:00:52 only (run, verdict 22:59:17, preserved 23:00:46);
   verdict.json 23:11:02 = disclosed verdict-ONLY recompute; **scratch F03 newest mtime =
   22:59:16** — no product process touched that cell again; the reviewer re-ran no
   product case either (verdict-chasing ban honored on both sides).
7. **Attack 7 — R-1 / R-2 / R-3: each verified accurate (N=3).** **R-1** everything in
   decision §5 measured true (2.0 s sleep L1153, 1.064 s mark→locked, 3.064 s
   spawn→BEGIN, events.jsonl containment, single red preserved) — RULED timing-family
   non-gating per frozen rule §4.3(i); harness improvement routed as a REM row (parent).
   **R-2** host registry re-checked **live: `LongPathsEnabled=0`** ✓; first-recompute
   `FileNotFoundError`, manifest attempt-1 undercount, scratch rename-back glitch all
   recorded with no evidence loss; `\\?\` convention validated by the reviewer's own
   three recomputes. **R-3** correction note present twice (decision §5 R-3 +
   `raws_manifest.json sidecar_expectation_note`), F04 manifest
   `expected_sidecar_sha256: null` with own `e26fb2ef…` triplet; I-07-D's actual pin
   scope (existence-only provenance) verified from source; frozen comparison values
   unchanged.
8. **Attack 8 — boundary: PASS (with census exception F-01).** **I-07-D original
   untouched**: recursive mtime scan → **no file newer than 2026-09-23 22:45** (0 writes
   by this card); **13 pinned inputs (N=13) re-hash equal** to binding.json's pre-run
   pins. **Production**: 20/20 anchors re-hash ok + 6 plan pins 6/6 at corrected paths;
   catalog bytes+mtime_ns identical; `-wal` identical; `-shm` bytes same + mtime changed
   (the disclosed read-only WAL side effect, measured as disclosed); 3/3 samples
   raw+sidecar match both sides ⇒ changes.diff's empty-product-diff basis stands.
   **No network verbs**: `CMD-REPRO-NOT-RUN` explicitly excludes live provider/git/
   production writes; grep over attempt JSON/text (excluding `iso/`) found no
   `Invoke-WebRequest|curl|git commit|push|add|checkout|stash`; `requests.` hits are spy
   wrap-registration names; F04 `simulated_provider: true`, F02/F03 provider deltas 0 —
   absence argued from command/evidence domains (not packet capture; listed as limit).
   **No git verbs** in any command; reviewer ran no state-changing git. **F04 attempt-1
   not recreated**: nothing attempt-1-shaped exists (no `*.pre_*`/timeout-shaped kill
   records under `evidence/cases/F04/`); oracle §0 + decision §4 keep §7.1/FR-1 as the
   **sole account** ✓.

## Findings dispositions (transcribed; recorded, never absorbed)

- **F-01 (MEDIUM — census leg gap)**: frozen oracle §6 R6 census ground rule never
  executed/recorded; not retro-repairable. Disposition = landing disclosure appended to
  `decision.md` `## F erratum (landing)` item 1 + **census policy REM row — parent
  register** (REM-98, REMEDIATION_REGISTER §99: future kill-bearing cards MUST
  run+record census before/after). "No real worker touched" now rests on the reviewer's
  kill-record verification (exactly 1 kill pid 19452, gate 5/5, manifest paths in scratch
  F04, harness kills manifest-registered PIDs exclusively). Does not touch D3.
- **F-02 (LOW)**: `recovery/README.md` incident line "(none yet)" stale vs decision §6's
  3 incidents. Disposition = pointer note in decision erratum item 2; README left as-is
  (note-here-only preferred, no edit made).
- **F-03 (LOW)**: commands.json `binding_status "bound before judged runs"` not
  timestamp-verifiable (mtime 23:16:45 post-runs, carries post-run notes); actual pre-run
  freeze carried by oracle+binding mtimes (22:45:47 / 22:48:00 < first run 22:49:27);
  no expectation-value exposure found. Disposition = wording note in decision erratum
  item 3; commands.json untouched.

## Unverified / limits (transcribed)

1. **Census impossible retroactively** (F-01): "no real worker touched" has no
   census-diff evidence and cannot be re-verified; the kill-record/gate inference stands
   alone. Full-tree production byte census not performed by card or reviewer (surface =
   26 anchors + 3 samples + catalog stat — same residual class as I-07-D's FR-2
   precedent).
2. **Network absence argued, not packet-captured** (command registry + evidence flags
   domains in §8).
3. **build / wprobe / snap drivers not replayed** by the reviewer (verdict-relevant work
   = the three `f0Xv` recomputes, run ×3 + scratch-absent ×3-equivalent); build claims
   spot-checked via `build.json`/`initial_state.json` presence + zero_insert proof.
4. **Scratch-proof = equivalent, not byte-replay**: their proof file is a 3-line
   summary; the reviewer reproduced an equivalent proof himself rather than byte-replaying
   their exact transcript.

## Scope-if-accepting (transcribed)

- **D3 = FIXED — verdicts re-computable YES ×3, dual-proven**: TEMP-redirected recompute
  AND scratch-absent recompute **each independently reproduced by the reviewer**; verdict
  equality to the recorded files confirmed (f02v rc0 / f03v rc3 same single red / f04v
  rc0, structurally identical ×3); raw byte-links `ffd73376…`/`8228741d…`/`e26fb2ef…`
  re-hashed 10/10; the three named byte-level checks (`raw_preserved`,
  `raw_intact_after_recovery`, `provenance_committed`) evaluate true on preserved
  in-attempt bytes.
- **changes.diff empty → nothing rides the merge batch** (0 product hunks verified).
- **I-07-D declarations carried unchanged**: F1/F2/F3, HK-3/D-3,
  F-F06-audit/F-F05-cause NOT absorbed, F04-attempt-1 unrecoverable = §7.1 sole account;
  plus disclosure_adaptation=unmapped, accuracy=unproven (both carried in handoff).
- R-1 = parent-ruled timing-family non-gating per frozen rule §4.3(i) (parent-confirmed
  §89) + **REM-97** as the fix track (`f03_runs` handshake for `t_scan_start` instead of
  `sleep(2.0)`); R-2 / R-3 = accepted disclosures; F-01/F-02/F-03 + O-1..O-4 for parent
  registration/landing notes.

---
Transcription integrity: written by the carrier at landing. Originals untouched —
`reviewer_report.md`, `reviewer_report.sha256`, `oracle.md`, `binding.json`,
`commands.json`, `changes.diff`, `recovery/README.md`, and all `evidence/**` originals;
the only edits to pre-existing attempt files are this stub→transcription flip and the
append-only `## F erratum (landing)` section in `decision.md`. No git, no network.
