# reviewer_report.md — independent review of I-07-D-REPRO / a20260923-01

Card `I-07-D-REPRO` (D3 substantive fix: F02/F03/F04 re-run with judged raws preserved
in-attempt → verdicts re-computable) · Attempt `a20260923-01` · Face = independent
reviewer (separate from implementer; implementer never signs acceptance; this report is
the reviewer's own verdict, `review.md` remains the implementer's untouched stub per the
reviewer's write boundary).

**VERDICT = `accepted_scoped`** — scope = the D3 objective + the card's own frozen
oracle §7 attack list, with 3 findings (1 MEDIUM, 2 LOW) + 2 observations recorded below.
Reviewer method boundary honored: actions were limited to read/grep/pwsh; zero product writes; zero
state-changing git; no network; the 2 files written inside the attempt are this report
and its `.sha256` sidecar; the f02v/f03v/f04v recomputes (N=3) ran on a `%TEMP%` clone (see §3);
`%TEMP%\i07d` scratch was renamed away and restored during the proof (state re-verified
after). REM-79 self-check run on this file (REM79 `tools/check_domain_assertions.py`,
`PYTHONIOENCODING=utf-8`) — result recorded in §10.

## 1. Deliverables + oracle frozen-first (attack 1) — PASS

- **Freeze order (mtimes, local)**: `oracle.md` 22:45:47 → `binding.json` 22:48:00 →
  `snapshot_before` captured 21:48:40Z (=22:48:40) → cell build 22:48:45-58 → wprobe
  22:49:13 (`zero_insert_proof:true`) → **first judged product run** F02 `scan1_fault`
  `started_at` 21:49:27.828Z (=22:49:27). Oracle + binding precede judged-run-1 of this attempt's N=9 judged product runs ✓.
- `oracle.md` live sha256 = `b320ebddf6c9041061d830ce142e0f98c19f1f31ea1b39403a59131e74cde267`
  (20989 B) == decision §1 freeze record ✓. Its §7 attack list predates results (content
  self-evidently frozen: it names the exact future checks I executed).
- **Copy-fidelity pins — re-hashed I-07-D original vs this attempt's copy: 9/9
  byte-equal**: `run_d_matrix.py 40b9f87a…334a`, `run_case.py aae0f21e…906c`,
  `common.py 79e36607…d7bc`, `build_iso.py 172ca0b3…8daa`, `hold_file.py 4a6cf71f…7fed`,
  `lock_catalog.py af33d1b8…ed50`, `spy/sitecustomize.py 7b3b9cbe…2508d`,
  `fixtures/HK-XIAOMI-2025.provider.json 8215b360…76f8`,
  `fixtures/fixtures_manifest.json cac0af3b…a870` — 9/9 equal to both binding.json pins
  and the live I-07-D files.
- **Commands argv diff vs I-07-D `CMD-D-F02/F03/F04`**: `CMD-REPRO-F02/F03/F04` argv
  arrays are verbatim `["<PY>","harness/run_d_matrix.py","f02"|"f03"|"f04"]`, equal to
  I-07-D's; `expected_raw_product_rc` equal ({0,3,0,3} / {1,0} / {3,0,3}); build/wprobe/
  snap argv forms likewise verbatim. Nested product argv verified live: scan argv ==
  `product_argv_forms_frozen`; F04 kill-manifest argv[0] and argv tail byte-equal to
  I-07-D's verdict manifest (cross-compare §5: `manifest argv tail equal: True`).
  Observation O-3 below concerns commands.json's timestamp, not its argv.
- **`changes.diff` EMPTY assertion = no-op substantiated (independently, not taken on
  trust)**: `snapshot_before` vs `snapshot_after` compared by me → 20 hashed anchors
  `changed: []`; 6 PLAN anchors `missing==missing` (the FR-2-class `parents[1]` snapshot
  defect visibly reproduced in the JSON paths `…\execution_runs\execution_v2\…`) —
  disclosed honestly; I re-hashed those 6 at corrected paths: **6/6 match frozen pins**
  (card_I-07-D `b54f4bc8…8c553`, scenario_matrix `0dec23cd…2299f`, sample_manifest
  `d5d0bb92…`, I-00-B commands `f8a397ec…24df` / binding `fdb2a598…75f0`, I-07-A
  state_matrix `de784cb2…e8684`); I additionally **live re-hashed the 20 hashed anchors (N=20)
  now: 20/20 equal** to both snapshots. Production catalog bytes 49677344768 + mtime_ns
  identical; `-wal` identical; `-shm` bytes 32768 identical / mtime changed (the
  disclosed read-only WAL-reader side effect — measured exactly as disclosed); 3
  production samples raw+sidecar `all_match=true` both sides. Honest count "20 hashed +
  6 pin-verified = 26/26 unchanged (not 26 hashed)" ✓ accurate. File is 3005 B of
  prose-assertion (not zero-byte) — the attack intent (EMPTY = zero product hunks) is
  what I verified: **0 product hunks**, writes confined to `ATT/**` + `%TEMP%\i07d/**`.
- **handoff**: `status = review_pending (implementer never signs)` ✓, `reviewer_status =
  review_pending / unsigned / verdict_is_transcribed_not_authored` ✓, the 7 carried (N=7)
  declarations present (I-07-B F1/F2/F3; I-09-C F12/F5; J6 anchor drift; HK-3/D-3
  reproduced; **F-F06-audit + F-F05-cause NOT absorbed**; **F04 attempt-1 bytes remain
  unrecoverable = §7.1 sole account**; D-1 kept visible) ✓.
- **recovery/README.md** present with 4 crash rules + re-run repro command (finding F-02
  concerns its stale incident line). **evidence/** complete: per-run
  argv/stdout/stderr/evidence.json/scan_runs/counters/hold/lock/state manifests,
  `raws_manifest.json`, `repro_verdicts.json`, `scratch_gone_recompute_proof.txt`,
  snapshots, `anchor_compare.txt`, `wprobe.json`, `build.json` (iso_rf 197 files,
  `product_edits: 0`).

## 2. Re-hash of preserved raws (attack 2) — PASS (10/10)

The 10 files below re-hashed by me (N=10) with `\\?\` long-path reads; live sha == manifest
`raws_manifest.json` triplet (sha256 + bytes); 10/10 matched:

| file (preservation-site) | live sha256 | bytes | manifest |
|---|---|---|---|
| F02 `…\annual\2026-04-28_hkexnews_12127452_2025年度報告.pdf` | `ffd73376…2da7c` | 4405561 | = |
| F02 `…pdf.source.json` (state2 sidecar) | `8228741d…8da71` | 2590 | = |
| F03 raw (same name) | `ffd73376…2da7c` | 4405561 | = |
| F03 state2 sidecar | `8228741d…8da71` | 2590 | = |
| F04 staged fetch `.source_catalog\staging\cf4d7291…\12127452.pdf` | `ffd73376…2da7c` | 4405561 | = |
| F04 canonical raw `…_小米集團－Ｗ 2025年度報告.pdf` | `ffd73376…2da7c` | 4405561 | = |
| F04 product provenance `….source.json` | `e26fb2ef…25b22` | 2361 | = |
| F02 / F03 / F04 `catalog.sqlite3` | `9f98a9a4…` / `0e4d1a15…` / `65adf399…` | 290816 / 282624 / 245760 | = |

**Byte-link to I-07-D's transcriptions**: `ffd73376…2da7c` is the sha recorded inside
I-07-D itself (its decision.md L48/L50/L194 + oracle L111 "raw+sidecar present (sha ==
manifest `ffd73376…2da7c`)"); `8228741d…8da71` is the value pinned inside I-07-D's
`evidence/cases/F02|F03/initial_state.json` L34 + `harness/build_iso.py` L59 +
production-sample snapshots — i.e. the preserved bytes are byte-equal to the shas
I-07-D recorded for those raws/sidecars. Two independent raw byte-links for F04 (staged +
canonical) both equal `ffd73376…` ✓.

**Preserve-immediately-after-per-case timing (dir mtimes)**: F02 preserved 22:51:24 (run
ended 22:50:51, next case F03 ran 22:57+) ✓; F03 preserved 23:00:46 (run ended 22:59:17,
F04 ran 23:04+) ✓; F04 preserved 23:08:34 (run ended 23:06:33) ✓ — the frozen
preservation plan §5-2 ordering holds. Observation O-4: manifest field `preserved_at`
(=22:18:5x UTC for each of the 3 cases) records the R-3-corrected manifest regeneration moment,
not the preservation moment; use the directory mtimes for preserve timing.

## 3. Reviewer's own recompute (attack 3) — PASS (verdict equality confirmed ×3)

Method (kept write-free inside the attempt): `robocopy` of the attempt →
`%TEMP%\i07drepro_revclone` (evidence copied; preserved excluded — TEMP targets the
ORIGINAL attempt's preserved root, exactly the documented convention), copy fidelity of
the inputs verified (their 3 × `verdict_recomputed_from_preserved.json` sha-equal in the
clone), same venv Python 3.13.9, `cwd=clone`, **`TEMP/TMP/TMPDIR =
\\?\`\<ATT\>`\evidence\preserved\temp`**, and — during each of the 3 recomputes —
**`%TEMP%\i07d` renamed away** (scratch ABSENT; restored and re-verified afterwards,
including that `i07d.scratch-gone-proof` stays absent).

| run | rc | stdout | vs their `verdict_recomputed_from_preserved.json` | vs their `verdict_run_time.json` |
|---|---|---|---|---|
| `f02v` | 0 | `{"cell":"F02","all_ok":true,"failed":[]}` | **IDENTICAL** (structurally, `decided_at` aside) | IDENTICAL |
| `f03v` | 3 | `{"cell":"F03","all_ok":false,"failed":["lock_held_across_scan"]}` | **IDENTICAL** | identical except `trigger.scan_window_utc` (run-time stores the live `time.time()` marker; the recompute reconstructs it from `argv.json started_at` — a record-field difference present identically in their own recomputed file; **checks/raw_rcs/model_prediction_checks equal**) |
| `f04v` | 0 | `{"cell":"F04","all_ok":true,"killed":1,"failed":[]}` | **IDENTICAL** | identical except `trigger.committed_raw_path` = `%TEMP%` scratch (run-time) vs `\\?\…\evidence\preserved\…` (recompute) — exactly their claim that the recomputed byte-level checks read the preserved file |

⇒ F02/F04 **all-invariant MATCH with `all_ok:true`**; F03 re-measures the **SAME single
red check** `lock_held_across_scan` (10/11) — the reproducible-measurement claim holds,
**verdict equality with their recorded files confirmed independently**. The three
byte-level checks D3 is about (`raw_preserved`, `raw_intact_after_recovery`,
`provenance_committed`) evaluate `true` on the preserved in-attempt bytes in my runs.
My runs wrote into the clone alone; the attempt's `verdict*.json` mtimes were left
untouched (spot-checked after: F02 23:10:59 / F03 23:11:02 / F04 23:11:04 unchanged).

## 4. Scratch-absent proof (attack 4) — PASS

- Read `evidence/scratch_gone_recompute_proof.txt`: `f02v rc=0 all_ok true` /
  `f03v rc=3 failed [lock_held_across_scan]` / `f04v rc=0 all_ok true killed 1` ✓
  consistent with my own runs above.
- **Independent live state check**: `%TEMP%\i07d` **present** and
  `%TEMP%\i07d.scratch-gone-proof` **absent** — matching decision §6.3's account (the
  proof rename was restored; the proof-rename target name is gone). Scratch F02/F03/F04
  newest file mtimes = 22:50:51 / 22:59:16 / 23:06:33 (≤ their run windows; nothing
  later — see attack 6).
- **I re-ran the recompute-without-scratch myself**: with `i07d` renamed away, each of the 3
  recomputes (§3) succeeded against the preserved tree alone; scratch then restored
  (`i07d` present, away-name absent) and re-verified. D3's dual re-computability proof
  (scratch present with TEMP-redirect, and scratch absent) is therefore independently
  reproduced, not merely transcribed.

## 5. Bidirectional comparison table (attack 5) — PASS (one honest gap: census, F-01)

Cross-comparison was executed mechanically (reviewer script over the two verdict JSONs +
the raw evidence files), not by eye:

**(a) REPRO → I-07-D (their MATCH claims):**

- **F02 — MATCH across the invariant set**: check-key set 15/15 equal, red `[]` both,
  `raw_rcs {0,3,0,3}` equal, `fault_catalog_delta` 7-key shape equal
  ({document_entities:1, documents:1, entities:1, locations:2, roots:1, scan_runs:1,
  sources:1}), `model_prediction_checks.oracle_literal…:false` equal (D-1 stays visible),
  `trigger.error_details` **identical** (incl. `PermissionError: [Errno 13] …`, `root_id
  company_raw`, relative_path, `unchanged:false`), status `completed_with_errors` +
  count 1 equal, hold `ok/label/share_mode:0/released_by "release marker"` equal, refusal
  stderr `not_found` + `source is not reusable: missing / no_existing_source_satisfies_request`
  + stdout 0 B, recovery `scan2` `catalog_count_delta {scan_runs:1, sources:1}` +
  `counter_delta {read:1, scan:1}` **byte-equal to I-07-D's own scan2 evidence** (the
  decision prose "registrations land documents+1 locations+2" is the cumulative-from-
  initial view — both attempts' per-run recovery delta is identical), provider 0/0 via
  `recovery_no_download` true. hold ∩ scan1 arithmetic: hold
  `21:49:27.739955 → 21:49:35.316842` ⊇ scan1 `21:49:27.828145 → 21:49:35.190828`
  (margins 0.088 s / 0.126 s) — `hold_window_valid:true` both attempts. Timing
  record-only: held 7.577 s vs 12.956 s ✓ recorded in their decision.
- **F03 — MATCH on the invariant fields / DIVERGE on the single timing-formula check** (ruling
  §7): check-key set 11/11 equal; red = `["lock_held_across_scan"]` here vs `[]` in
  I-07-D (10/11 vs 11/11, `all_ok` false vs true) — **the divergence is exactly one
  check, recorded, never re-run to green**; `raw_rcs {1,0}` equal; `error_doc` equal
  semantics (`database is locked` / `catalog_busy` / `retryable:true` / `failed`),
  stdout empty, fault delta `{}` equal, recovery `scan2` delta 7-key
  ({document_entities:1, documents:1, entities:1, locations:2, roots:1, scan_runs:1,
  sources:2}) + `counter_delta {read:2, scan:1}` **byte-equal to I-07-D's scan2
  evidence**; `hold_s 75.0`, BEGIN-EXCLUSIVE lock text, `ok:true` equal; elapsed
  56.406 s vs 34.515 s (both ≥ the frozen 25 s gate — timing record-only ✓ recorded).
- **F04 — MATCH across the invariant set**: 15/15 keys, red `[]`, `raw_rcs {3,0,3}` equal,
  kill count 1, gate checks identical 5/5 (`manifest_present, manifest_path_in_argv,
  manifest_path_in_cwd, alive_before:true, alive_after:false`), `kill {ok:true,
  exit_code_set:4242}` equal, `released_marker_present:false`, `timed_out:false` equal,
  manifest `point`/`armed`/`note`/argv equal, `committed_raw_path` basename equal
  (canonical ≠ manifest name — D-3/HK-3 quirk reproduced), `filename_note` equal,
  product's own error chain carries `…company-wiki ensure exited 4242…` with
  `error_code:"upstream"` (quoted from stderr/evidence), `raw_sha_after:null` at fault
  reproduced (= I-07-D's transcription), fault `catalog_count_delta {}` equal, counters
  `{provider:2, scan:1}` equal, recovery provider 0 via check true. Timing record-only:
  pid 19452 vs 42124, timestamps ✓ recorded.

**(b) I-07-D → REPRO (no transcribed invariant silently missing):** I walked I-07-D
decision §2 rows / §4 delta table / §6 kill evidence / §7.1 + its three pinned
verdict.json against their §3 table: error classes ✓, rc tables ✓, delta shapes ✓ (per-run
+ cumulative), raw/provenance bytes ✓, verdict check-key sets and counts
(15/15 · 11-key-with-one-recorded-red · 15/15) ✓, trigger proof shapes ✓ (hold
discipline; `hold.json` overlap + rc1 + ≥25 s; barrier+manifest+gate+4242), provider
deltas 0/0 · 0/0 · +2/0 ✓, D-1 ✓ and D-3 ✓ reproduced-and-visible, §7.1 correctly scoped
OUT of the comparison (not a target, not re-created) ✓. **The single transcribed
invariant with no REPRO counterpart = I-07-D §6's census kill-scope proof
(`real_source_catalog_gone=0`)** — see finding F-01 (census was neither run nor recorded
here).

## 6. F03 divergence ruling material (attack 6) — root cause CONFIRMED; no verdict-chasing

- `lock/hold.json`: `locked_at 21:57:47.113789`, `released 21:59:02.145573`,
  `hold_s 75.0`, `lock "BEGIN EXCLUSIVE acquired (isolation-only target)"`, `ok:true`.
- `counters/events.jsonl` count-on-entry scan event **pid 26128 at t=1790200679.73 =
  21:57:59.730** → **12.616 s after `locked_at`**, i.e. the product's actual scan call
  ran INSIDE the hold; product run `recorded_after_run 21:58:43.621` < `released` (also
  inside). The recovery scan event (pid 44052, 21:59:13.09) sits AFTER release —
  ordering discipline correct.
- Run-time driver marker (`verdict_run_time.json scan_window_utc[0]`)
  `1790200666.049762 = 21:57:46.049762`; `locked_at − mark = 1.064027 s` → their **"1.06 s"
  claim exact**. With `f03_runs` `time.sleep(2.0)` immediately before the mark
  (`run_d_matrix.py` L1153-1154, in their byte-identical harness copy), spawn ≈
  21:57:44.05 and **spawn→BEGIN EXCLUSIVE = 47.113789 − 44.05 ≈ 3.064 s → their "3.06 s"
  claim exact**; `hold.json started 21:57:46.962547` shows interpreter+import startup
  finishing ~2.91 s after spawn — i.e. **after** the driver's 2 s mark. Root cause =
  **fixed-sleep(2.0) assumption vs variable lock-helper startup** confirmed at source.
- Frozen formula (`run_d_matrix.py` L1199-1211): `overlap = locked_at < t_scan_start AND
  released > t_scan_end` ⇒ `47.113789 < 46.049762` = false ⇒ `lock_held_across_scan:false`
  — a marker-placement artifact, not product semantics. I-07-D's original: its helper
  acquired within ~2 s of spawn (locked 17:29:31.742 < its mark 17:29:33.695, +1.95 s)
  ⇒ true. Mechanism of the flip fully explained both directions.
- **56.4 s claim**: `scan1_fault/evidence.json elapsed_seconds 56.406` (== argv.json) —
  the in-transaction `database is locked` failure after that wait is possible solely while
  the single-holder `BEGIN EXCLUSIVE` was held (hold spans the run end). ≥25 s frozen
  gate met. (Precision note: 56.406 s is total scan1 wall time, of which the
  in-transaction wait is the dominant component — non-gating wording, recorded O-5.)
- **They did NOT re-run to paint green — verified**: F03 evidence files lie within the
  single window 22:57:46→23:00:52 (run 22:57:46-22:59:17, verdict 22:59:17, preserved
  23:00:46); verdict.json 23:11:02 is a verdict-ONLY recompute (disclosed §6.4);
  **scratch F03 newest mtime = 22:59:16** — no product process touched that cell again.
  I-07-D's decision §6.3 keeps I-09-C-style no-retry discipline; here too the red check
  survived to landing. I did not re-run any product case either (verdict-chasing ban
  honored on both sides).

## 7. Disclosures R-1 / R-2 / R-3 (attack 7) — each verified accurate (N=3)

- **R-1** (fixed-sleep timing artifact): everything in decision §5 R-1 measured true
  (§6 above): 2.0 s sleep at L1153, 1.064 s mark→locked gap, 3.064 s spawn→BEGIN,
  containment via events.jsonl, single red check preserved. Classified per frozen rule
  §4.3(i) as timing-family non-gating — see ruling §9.
- **R-2** (`LongPathsEnabled=0` + `\\?\`): host registry re-checked live =
  **LongPathsEnabled 0** ✓; the first-recompute `FileNotFoundError` incident is recorded
  (decision §6.1 + commands.json precedent note) with no evidence loss — corroborated:
  `verdict_run_time.json` snapshots precede each recompute (F02 22:50:51 < 22:56:47);
  manifest attempt-1 undercount incident recorded (§6.2); scratch rename-back glitch
  recorded (§6.3) with current state exactly as claimed. My own three recomputes ran
  under the same `\\?\` convention successfully — the convention is validated.
- **R-3** (retention-tool expectation correction): correction note present twice (decision
  §5 R-3 + `raws_manifest.json sidecar_expectation_note`), F04 manifest has
  `expected_sidecar_sha256: null` with `e26fb2ef…` as its own triplet, F02/F03 keep the
  `8228741d…` expectation. **I-07-D's actual pin scope verified from source**: its
  oracle L172 requires "`sha == manifest` + `.source.json` provenance **present**" and
  its decision asserts a content sha for the raw exclusively — i.e. provenance pinned by existence alone.
  The first-version mis-pin (expecting `8228741d…` for F04's product-generated
  provenance) was theirs, corrected by them, frozen comparison values unchanged ✓.

## 8. Boundary (attack 8) — PASS with census exception F-01

- **I-07-D original untouched**: recursive mtime scan of
  `execution_runs/I-07-D/a20260923-01` → **no file newer than 2026-09-23 22:45** (this
  attempt's start); 13 pinned inputs (N=13) re-hash equal to binding.json's pre-run pins
  (decision `ba6e4a1d…`/31292, oracle `576ddfc5…`/27211, commands `458c62c3…`/13107,
  binding `30ea8a7b…`/19758, handoff `82bb03ac…`, review `b7dba0d4…`, reviewer_report
  `1a1d1c05…`, verdicts `8d6e7a8b…`/`6f5b6e6f…`/`f043c080…`) — 0 writes by this card.
- **Production anchors**: 20/20 live re-hash ok; before/after `changed: []`; catalog
  bytes+mtime_ns identical; `-wal` identical; `-shm` bytes same + mtime changed (the
  disclosed read-only WAL side effect — measured as disclosed, not taken on trust);
  3/3 samples raw+sidecar match both sides; **plan 6 钉 6/6 at corrected paths** (§1) ⇒
  honest "26/26 unchanged" ✓. changes.diff's empty-product-diff basis stands.
- **No network verbs**: in commands.json (domain: this attempt's command registry)
  `CMD-REPRO-NOT-RUN` explicitly excludes live provider/git/production writes; a grep
  over the attempt's JSON/text (excluding `iso/`) found no `Invoke-WebRequest|curl|git
  commit|push|add|checkout|stash` invocation; the only `requests.` hits are spy
  **wrap-registration names** in `wiring.json` (count-on-entry instrumentation), F04
  evidence records `simulated_provider: true`, F02/F03 provider deltas are 0. (Absence
  argued from command/evidence domains above — not from packet capture; listed as limit.)
- **No git mutations**: no git verb in any command (domain as above); snapshot tool note
  "git is NOT run by this card" consistent; reviewer ran no state-changing git.
- **F04 attempt-1 bytes**: nothing attempt-1-shaped exists in this attempt (no `*.pre_*`
  or timeout-shaped kill records under `evidence/cases/F04/`); oracle §0 scopes it out;
  decision §4 "What D3 does NOT claim" keeps §7.1/FR-1 as the **sole account** — this
  card did NOT recreate anything for it ✓.

## 9. Findings, observations, rulings, limits

### Findings (recorded, never absorbed)

- **F-01 (MEDIUM, attack-list/boundary): frozen census ground rule not executed.**
  oracle §6 R6 ("…census before/after; no real worker touched") and oracle §7-3 /
  handoff `next_action` ("attack F04 kill-gate **+ census**") are unsatisfiable: **no
  census artifact exists anywhere in this attempt** (domain: attempt tree excluding
  `iso/` — the sole `census` hits are the oracle/decision/handoff sentences themselves),
  and commands.json has no census command. Consequence: I-07-D §6's
  `real_source_catalog_gone=0` kill-scope proof has no REPRO counterpart (the one gap in
  the bidirectional walk, §5b), and "no real worker touched" rests solely on the
  kill-record substitute: I verified exactly one kill (pid 19452, gate 5/5, manifest
  paths inside scratch F04, no other kill record anywhere) via a harness path that kills
  manifest-registered PIDs exclusively. The omission is undisclosed in decision/handoff/
  changes.diff. Not re-workable retroactively (a "before" census cannot be taken now) ⇒
  route: parent registers + landing disclosure line; future kill-bearing cards keep
  census in-scope. Does not touch D3's re-computability conclusion.
- **F-02 (LOW): `recovery/README.md` incident line stale.** "Incidents this attempt:
  _(no incidents yet)_" contradicts decision §6's three recorded incidents (FileNotFoundError
  recompute attempt-1; manifest attempt-1 undercount; scratch rename-back glitch).
  README's own anti-death rule 1 wants incidents kept — one pointer line to decision §6
  fixes it.
- **F-03 (LOW, claim precision): commands.json `binding_status "bound before judged
  runs"` not timestamp-verifiable.** `commands.json` mtime 23:16:45 post-dates every
  judged run (it necessarily carries post-run precedent notes, e.g. R-2's incident). The
  pre-run freeze actually carried by `oracle.md` (22:45:47) + `binding.json` (22:48:00),
  whose pins/values already fix each expectation (expected rc tables are verbatim from
  the pre-pinned I-07-D commands.json `458c62c3…`), so **no expectation-value exposure
  was found** — wording-level.

### Observations (non-findings)

- **O-1**: manifest `preserved_at` = manifest-regeneration time (each of the 3 cases ≈23:18:5x
  during the R-3 correction), not preservation time; preserve timing = directory mtimes
  (§2). **O-2**: `commands.json`/`decision.md` are living files (mtimes post-run) — the
  frozen-first guarantee rests on oracle+binding, which verified. **O-3**: F03's "56.4 s
  in-transaction wait" = total scan1 wall time (56.406 s) with the wait as its dominant
  component; gate is on elapsed anyway. **O-4**: REPRO's recompute `scan_window_utc`
  differs from run-time by the argv-reconstruction method — deterministic, disclosed
  scope in their "checks-identical" claim (checks-only) is accurate.

### Rulings requested by the card

- **R-1 — RULED: accept `lock_held_across_scan:false` as timing-family, non-gating, per
  the FROZEN comparison rule oracle §4.3(i)** (invariant fault semantics all MATCH;
  flip fully explained as fixed-sleep marker placement; not re-run to green). Route the
  harness improvement as a REM row (parent to register): `f03_runs` should derive
  `t_scan_start` from a lock-helper handshake (e.g. read `hold.json locked_at`/ready
  file) instead of `time.sleep(2.0)` — future cards reusing `f03_runs` inherit the
  artifact until fixed; the fix must land OUTSIDE this frozen harness copy.
- **R-2 — ACCEPTED** (host fact re-verified live; convention validated by reviewer's own
  runs; incidents disclosed with no evidence loss).
- **R-3 — ACCEPTED** (their correction is accurate against I-07-D's actual existence-only
  provenance pin; frozen comparison values unchanged).

### Unverified / limits (explicit)

1. Full-tree production byte census: not performed by card or reviewer — surface covered
   = 26 anchors (20 hashed live by me + 6 pin-verified) + 3 samples + catalog stat
   (same residual class as I-07-D's precedent FR-2 handling).
2. Census leg (F-01): "no real worker touched" has no census-diff evidence and cannot be
   retro-verified; the kill-record/gate inference stands alone.
3. Network absence argued from command registry + evidence flags (domains in §8), not
   from packet capture.
4. I did not replay `build`/`wprobe`/`snap-*` drivers (verdict-relevant work = the three
   `f0Xv` recomputes, run by me ×3 + scratch-absent ×3-equivalent); build claims
   spot-checked via `build.json`/`initial_state.json` presence + zero_insert proof.
5. Their scratch-gone proof file is a 3-line summary; I reproduced an equivalent proof
   myself rather than byte-replaying their exact transcript.

## 10. Scope-if-accepting + reviewer method ledger

**Scope-if-accepting:**
- **D3 = FIXED** — F02/F03/F04 verdicts re-computable from preserved in-attempt raws:
  **YES ×3, dual-proven** (TEMP-redirected recompute AND scratch-absent recompute, each
  independently reproduced by the reviewer; verdict equality to their recorded files
  confirmed; raw byte-links `ffd73376…`/`8228741d…`/`e26fb2ef…` re-hashed 10/10).
- **R-1 = parent-ruled timing-family non-gating per frozen rule §4.3(i)** + harness-
  improvement REM row (parent to register: fixed-sleep(2.0) vs 3.06 s lock-helper
  startup in `f03_runs`).
- **changes.diff empty → nothing rides the merge batch** (0 product hunks verified).
- **Carry I-07-D's declarations unchanged**: F1/F2/F3, HK-3/D-3,
  F-F06-audit/F-F05-cause NOT absorbed, F04-attempt-1 unrecoverable = §7.1 sole account;
  plus disclosure_adaptation=unmapped, accuracy=unproven.
- Findings F-01/F-02/F-03 + observations O-1..O-4 for parent registration/landing notes.

**Reviewer method ledger (what this reviewer actually did):** read/grep/pwsh over
I-07-D-REPRO + I-07-D (read-only) + plan pins; live SHA-256 of 10 preserved files, 9
copy-fidelity pairs, 13 I-07-D pins, 20 production anchors, 6 plan pins, 7 deliverables;
3 independent verdict recomputes on a `%TEMP%` clone with `\\?\` TEMP redirect while
`%TEMP%\i07d` was renamed away (restored + re-verified); 2 reviewer comparison scripts
(live in the `%TEMP%` clone); recursive mtime scans of I-07-D and scratch cells; no
product run re-executed; no writes inside the attempt except this report and its
sidecar; no network; no state-changing git; never self-signed.

**REM-79 self-check (mechanized)**: `REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py`
v1.2.0-correction2 with `PYTHONIOENCODING=utf-8` run on this file after the reviewer's
own domain-qualifier pass → **0 violations (exit 0)**; the checker's first run reported
34 unqualified universal-quantifier lines were re-scoped to carry their domain (this is
the documented checker lifecycle: prose → tool → iterate → clean).
