# RF-RATCHET-REST-A — carrier landing (bookkeeping transcription)

## VERDICT BLOCK

- **verdict** = `ACCEPT` (**no blockers**) → landed as `accepted_scoped` — **7 findings, all LOW/INFO documentation or EOL-label issues: none of them changes the delivered bytes, the gate numbers, or the merge decision.**
- **carrier** = `reviewer_report.md`
- **carrier sha256** = `0282f01cd858c410bc1194faff47a20606968f6d04938884fbd7c58a50ebdac3` — **26208 B**, 181 lines + single trailing LF, UTF-8 without BOM (`# R…` first bytes), LF-only (0 CR).
- **pin** = `reviewer_report.sha256` (85 B; sidecar's own sha256 `624cbcd53cc3f40f98b59f8af865deecd0608584b30650e9fdd1b20b77e6034d`) content = `0282f01cd858c410bc1194faff47a20606968f6d04938884fbd7c58a50ebdac3  reviewer_report.md` — verified read-only at landing: independent re-hash == sidecar == dispatch pin (26208 B == dispatched) ✓.
- **ruling location** = `reviewer_report.md` §1 Verdict heading **L11**, the verdict statement **L13**, findings table **L15–L23** (F-01..F-07 at L17/L18/L19/L20/L21/L22/L23), not-re-executed list **L108–L116**, F-01 evidence detail **L120–L141**, scope-if-merging **L145–L155**, reviewer's own runs **L159–L177**, REM-79 self-check **L179–L181**.
- **byte proof** (0-based byte offsets against the file as it stands at carrier_sha256; multi-line regions include internal LFs and exclude the final LF):

| region | lines | start..end_inclusive | length | sha256 |
|---|---|---|---|---|
| meta (title + card/attempt/reviewer/method/sign-off) | L1–L10 | 0..1054 | 1055 | `e3a429f238b82452db357905daa3efaa5fce8bff560542c493f48c56a2529838` |
| verdict heading `## 1. Verdict` | L11 | 1056..1068 | 13 | `6c789b0be03b36f84b54be4e23f09dc09f731d36e70f658260a45ff74a31a6d4` |
| verdict statement (`**ACCEPT (no blockers).** …`) | L13 | 1071..1342 | 272 | `57c89db254b51ad47a0bcbca3d5a5a7eb1012bb7676fc8e760bf3d40e08d6873` |
| findings table F-01..F-07 | L15–L23 | 1345..3271 | 1927 | `c27d1ece7c5f8f91beda93dfed42b86fa899f7dfcb331bdaeb801fa7b01c97fc` |
| **verdict block (heading + statement + findings)** | **L11–L24** | **1056..3272** | **2217** | `f7a4e778c8b50da3adc78ede25c4fb96cbe43510b8c0f8d131b1e39b974bd392` |
| §3 unverified / not re-executed | L108–L116 | 18507..20140 | 1634 | `e2f4c8818e38bac438ea7e8879f447b2e9d6465294061b09726a0a70b456fed4` |
| §4 F-01 evidence detail | L120–L141 | 20148..22044 | 1897 | `c68f65533bab6b178a6314b8d268b1182aec11bf9a9aad5579e21e0c43dc13a7` |
| §5 scope if ACCEPTING (merge batch) | L145–L155 | 22052..24443 | 2392 | `942096eb08e480999fbc6258b91c63bc2d4ead94a6efa1451099fded818a2596` |
| §6 reviewer's own runs | L159–L177 | 24451..25987 | 1537 | `64f5f5931c803f08af1331225cc8671d770f9d0e6c3af723f4d18e3458a4fad5` |
| §7 REM-79 self-check | L179–L181 | 25990..26206 | 217 | `6e7cfeeb5caafb1817e17ec7855fe4a88a65f4847cbceb9ce417195d6d03251f` |

- **reviewer / 独立复核 N=1** = one independent reviewer subagent of parent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`, 2026-09-23; methods read/grep/pwsh only, **no product writes** (RF `scripts|tools|tests` untouched), scratch confined to `%TEMP%`, no network, **no state-changing git** (`log`/`status`/`diff --cached`/`show`/`rev-parse`/`hash-object`/`apply --check` = read-mode only), reviewer write boundary = `reviewer_report.md` + `reviewer_report.sha256` **only**. Sign-off note at carrier L7: handoff stays `review_pending`/`signed:false` — the reviewer **does not self-sign**; the parent applies the signature on this ACCEPT, which is exactly this landing.
- **handoff pre-image at landing** = `handoff.json` **6684 B**, sha256 `7d684a072c6cff2ebae6434338be96f641c0955fd2d1a34bf6489163f940721a`, `status = review_pending`, `signed = false` ✓.
- **nature of this file** = bookkeeping transcription, adds no acceptance of its own. The implementer never signs; the reviewer never signs the card face; this landing pass never signs. **Verdict transcribed, not authored.**

`review.md` did not previously exist in this attempt (no implementer stub); created by the carrier-landing pass — not by the implementer and not by the reviewer. 0 bytes were written to `reviewer_report.md` or its sidecar by this pass.

## What the review established (transcribed from `reviewer_report.md`)

### V2 — CC numbers: 18 / 9 / 72 (dual implementation, 43 files, 0 disagreements)
- Instrument = the ratchet test's own `_max_complexity` **imported live** from RF `tools/tests/test_complexity_ratchet.py` (sha `EB1A36CF…`) **plus a reviewer-written independent twin** (ast.walk, same branch semantics), run over both their `refactored/` copies and the live tree → **agreement 43/43 files, 0 disagreements (both scans)**.
- Delivered: `forecast/calc.py` **18** (cap 21; driver `collect_parameter_roles` 22→17, new `_recognition_parameter_ids` **6**, file max now `base_segment_parameter_ids` 18) · `generate_input_template.py` **9** (cap 9; `build_template` 17→9, `main` 8 untouched) · `research/targets.py` **72** (cap 88; `_validate_management_target` 72 + `_normalize_communication_coverage` 35 + orchestrator 9, `add_management_target_analysis` 12 untouched).
- **Live originals re-measured = 22 / 17 / 114** ✓; the 12 function-level numbers in `decision.md`/`handoff.json` match the reviewer's independent measurement (F-07 concerns the card's paraphrase only).
- **Iso full-row scan, own rows = 0 failing**: final-byte iso with the real unmodified frozen table → 5 failing rows, all sibling-owned (`confidence 32`, `model_registry 28`, `revenue_core 23`, `revenue_publication 16`, `model_extensions 27`); REST-A's 3 rows pass ✓.
- **8 → 5 verified**: live production scan (both impls) = the same 8 failing rows as their `scan_red.json`; final-byte iso = 5 → the 8→5 claim reproduces. **Caveat transcribed: the live repo still shows 8 because no diff has been applied yet; 5 is the iso-state number and 0 arrives with the merge batch (§Scope-if-merging).**
- **Frozen table 4-way `EB1A36CFD54A8B96E3B5DCA6CA4B7A89CA6B1E1605D22EEDB69F643245EDD10A`**: live test file == their `sha_reverify_final.txt` == the sha inside their `scan_green_iso.json` == the reviewer's iso copy — before == after, **no cap changed** ✓.
- Sibling rows untouched: the 5 sibling files byte-identical to live production in **all 5 of their trees → 25/25 hash checks** ✓; only sibling ratchet rows were re-pinned, scratch-only; my caps **21/9/88 byte-identical in each of the 5 scratch tables**; no table edit in `changes.diff` ✓.

### V3 — Family: 55 lines byte-identical + aggregate formula reverse-engineered
- `evidence/family_shas_before.txt` and `family_shas_after.txt` are **byte-identical** (55 lines each, both sha256 `365b509478c067c94817512ef215465cd3062bf914324565107bcccbfc6233da` — re-hashed at landing ✓) and **each of the 55 recorded per-file sha256s matches the live RF test file** (0 mismatches in 55).
- The aggregate `947AB2EC03BA8082514413E5314F1F5DAF9FB8B6133F3C197B615B7218715387` (before == after) **reproduces exactly under the formula the reviewer reverse-engineered**: sha256 over the lines `"<SHA256>  <path>"` joined with `"\n"`, no trailing newline. Formula not documented by the card → recorded as a documentation gap (cannot prove it is the formula they used, but it matches and before/after files are byte-identical anyway).
- Supplement family (6 files): **4 failed / 42 passed / 3 skipped both sides**, `all_outcome_changes {}` / `regressions []` ✓.
- **Reviewer's own family re-run on the final-byte iso (fresh `%TEMP%` copy, `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`): `14 failed / 554 passed / 3 skipped / 130 subtests` (360.6 s)** — matches their baseline and their after run exactly; compared against **both jupiters**: vs their before → `all_outcome_changes {}` / `regressions []` / `only_* []`, rc 0; vs their after → `{}` / `[]` ✓. Supplement re-run: **4F/42P/3S** (82.6 s) → vs their `supp_before`: `{}` / `[]` ✓. Landing re-read `compare_before_after.json`: before 554/14/3 == after 554/14/3, all empty change sets ✓.
- **12 pre-existing**: identical 14 failing ids in their before, their after, and the reviewer's re-run (2 of the 14 = the ratchet body itself). TRIAGE corroboration = **6/12 → F-01** (two spot-read raws confirm the two named ids FAIL at `rf_sha=b0d016a6…`, and `git diff --stat b0d016a6..HEAD -- scripts tests tools` touches 2 unrelated files outside the 55-family, so those two bind to HEAD).
- **2 ratchet-body reds = KEEP-RED**: ratchet test on live production → first `AssertionError analysis/confidence.py max 32 > 23`, then `model_extensions.py max 27 > 10` (REST-A's rows never reached at abort); the same two abort first in the iso; supplement wrapper `test_ca303::test_c3_complexity_ratchet_green` carries the same RED both sides.

### V4 — Type gate: 67 ≤ 69 (own run) + targeted 5 → 3
- Incident recorded in `decision.md` §"Type gate (mypy, C4) incident": `dict[str, Any]` annotation widened `target.get(...)` to `Any|None` and invented 8 errors → fixed to `target: Any` (matches original inference); net −2 on the 3 owned files.
- **Reviewer's own targeted replication** (`--follow-imports=skip`, fresh `%TEMP%` cache, production bytes vs refactored): **originals 5 errors → refactored 3**, the 2 dropped are the original's coverage-shape errors, the 3 kept are pre-existing in untouched blocks → **no new error introduced** ✓.
- **Reviewer's own full re-run** `mypy scripts --no-error-summary --ignore-missing-imports` in the final-byte iso = **67** errors (≤ `MYPY_BASELINE` 69) — independent of their `evidence/mypy_full_after.txt` (landing re-counts 67 `: error:` lines ✓).
- Family re-run happened on FINAL bytes (mtimes: last edit 22:36:11 → `changes.diff` 22:37:28 → probes 22:38:20 → mypy 22:38:43 → iso scan 22:39:06 → mutations 22:39:12-27 → `family_after/junit.xml` 22:43:39 → `supp_after` 22:44:12 → `sha_reverify_final` 22:44:43 → `handoff.json` 22:47:58) ✓.

### V5 — Strategy proof: pre-images ARE real git objects
- `evidence/compare_before_vs_pre70dd.json`: before `14F/554P/3S`, pre-70dd `20F/548P/3S` → **8 green→red regressions** + **33 failing subtests**, junit totals 571/571 both sides, 2 spurious improvements (zr601 pair) ⇒ tests distinguish ⇒ revert disqualified ⇒ refactor mandatory (revert-tested-not-shipped) ✓.
- `git log 70dd9f6e..HEAD -- <the 3 files>` empty ⇒ live content == checkpoint content (the pre-70dd images really are the pre-images).
- **Pre-image authenticity:** `git rev-parse 70dd9f6e^:<path>` = **`15a4d644d824cb970e1019751f38b250699b9657`** (calc) / **`49fb703fae152e0004bd568e71a9b3c29c0a3022`** (template) / **`f8b8844694aad160c728a5982ad884de4812c1a9`** (targets), each `type=blob`; `git hash-object pre70dd/*.blob` returns **the same three ids** ⇒ the `.blob` files hold the exact git pre-image bytes. The three *recorded* shas are sha256 digests of those blobs, not object ids → **F-02 label correction** (both sets point at the same bytes).

### V6 — Mutation non-vacuity: row 1 replicated end-to-end by the reviewer
- GREEN case: scratch ratchet (sibling rows re-pinned only; my caps byte-identical 21/9/88) → **both ratchet tests `ok`, `Ran 2 tests … OK`, rc 0** ✓; iso scan `my_rows_failing []` ✓.
- **Reviewer's own replication of row 1** in `%TEMP%`: verified `scripts/forecast/calc.py` == production original (`BC4F33D9…`), other two == refactored, table diff = confidence + NEW_FILE_MAX only → ran the test → **rc 1, first `AssertionError: 22 not less than or equal to 21 : forecast/calc.py max 22 > 21`** — matches both the reviewer's live measurement (22) and the card's claim ✓. Rows 2/3 accepted from raws + tree classification (each `mut_*` swaps exactly one file back to production original — 9/9 hash checks).
- **Differential probes:** the reviewer re-ran `diff_probe.py` **twice** — ORIG (live production) vs NEW (final-byte iso): **my ORIG == my NEW (25 probes), and both equal their stored `probe_orig.json`/`probe_new.json`** (diff key list empty) ✓. The **`sorted()` fix is disclosed** (`decision.md`/`handoff.json`) and present at `diff_probe.py:402-404` with rationale (`MANAGEMENT_COMMUNICATION_STATUSES` is a `set` → `list()` order hash-randomized); both `probe_*.err` are 0 B. Landing re-reads `probe_compare.json`: `identical: true, n_probes: 25, diffs: []` ✓.

### V7/V8 — Boundary at close (re-checked twice)
- **Production 3 before-shas re-verified live, twice** (direct `Get-FileHash` and the copies fed to `git apply --check`): `BC4F33D92738029A…`, `F7C57911D5F85204…`, `1C885DEAF4168BAC…` ⇒ production sources never written ✓ (landing re-reads `sha_reverify_final.txt`: identical values + `family_55_aggregate_unchanged=True` ✓).
- Frozen table live = `EB1A36CF…` ✓; `changes.diff` contains **no skip/xfail markers** ✓; **zero git writes by the attempt** (newest reflog entry = pre-attempt commit `b7a6a116` 19:51 vs attempt start 20:53; nothing staged; `git status --porcelain -- scripts tools tests` = 0 entries) ✓.
- **Reviewer's own `git apply --check`** against fresh `%TEMP%` copies of the 3 live production files: `Checking patch …×3`, **rc = 0** (run twice, incl. `--verbose`) ✓; applying under RF-equivalent EOL rules (`.gitattributes` `*.py text eol=lf`) reproduces **calc `605BE6E8…` and template `06591BE0…` byte-exactly**, while `targets` lands as LF `5BE517C9…` vs their pinned CRLF `E7E8ED6B…` → **F-03** (content equal after normalization, verified both directions).
- tmp/`__pycache__` rescan of the attempt root: **0 / 0** ✓; attempt root = 13 files + 4 dirs at review close (the "12" count is F-06); RF product surface clean (only 2 non-`.planning` porcelain entries, both pre-dating the attempt).

## Findings and dispositions (carrier L15–L23, corrections appended to `decision.md §F-07 erratum (landing)`)

| ID | 级 | Finding (transcribed) | Disposition at this landing |
|---|---|---|---|
| F-01 | **LOW** | "12/12 pre-existing failures corroborated by RF-STEP9-TRIAGE `win_head` evidence" is **overstated**: an exact test-id search over the whole TRIAGE attempt finds **6 of the 12**; the other 6 appear nowhere in TRIAGE | **CORRECTED (wording only): 6/12 corroborated by TRIAGE raws**; missing ids = `zr1102::test_c1_no_orphaned`, `dropbox fc505`, `zr1103 c2`, `zr1103 c3`, `zr803`, `zr804`. The **"pre-existing" verdict STANDS** on the other legs: baseline iso of production bytes + the reviewer's identical re-run (three junit comparisons, all `{}`/`[]`). Corrected wording recorded in `decision.md` erratum + `handoff.json family.all_preexisting_corroboration` (original preserved as `*_historical_pre_verdict`). |
| F-02 | **LOW** | Recorded pre-image shas `98f2b591…/e4593b14…/f8b6f073…` are **sha256 of `pre70dd/*.blob`**, not git object ids; real pre-image blobs `15a4d644…/49fb703f…/f8b88446…` verified byte-identical to their `.blob` files | **LABEL CORRECTION recorded** (both value sets point at the same bytes); git blobs are authoritative for object identity; originals retained, no re-pin, no evidence impact. |
| F-03 | **LOW** | `binding.json sources_after_sha256["scripts/research/targets.py"] = E7E8ED6B…` is a **CRLF-byte** hash (refactored copy = 661 CRLF / 0 LF; production = LF); applying `changes.diff` under `.gitattributes` yields LF `5BE517C9E7196AC1…` — content identical after normalization; calc/template reproduce byte-exactly | **Recorded = document-not-repin**: binding stays sealed; **authority for after-bytes at apply = git-committed LF content**; **both shas recorded** (`E7E8ED6B…` CRLF-pinned / `5BE517C9…` LF-on-apply) so future checks don't false-flag; ratchet/probes/CC/family unaffected. |
| F-04 | INFO | `handoff.changes_diff.diff_bytes = 43880` is the **character** count; the file is **43882 bytes** (one U+2014 em dash) | Recorded with both counts in handoff bookkeeping (landing re-measured chars 43880 / bytes 43882 ✓); no diff regeneration. |
| F-05 | INFO | `evidence/README.md` cites 3 non-existent mutation filenames; actual = `mutation_forecast_calc.py.txt` / `mutation_generate_input_template.py.txt` / `mutation_research_targets.py.txt` (other 25 of 28 resolve) | Correct names recorded in this landing (handoff + qualification); README original retained untouched. |
| F-06 | INFO | `decision.md` says "the 12 intended artifacts"; attempt root actually holds **13 files** (7 step artifacts + 6 tooling scripts) + the 4 dirs it names | Corrected count recorded in the decision erratum (13 at review close; 15 incl. reviewer's 2; 16 incl. this `review.md`); original text retained (append-only erratum, prefix-proven). |
| F-07 | INFO | Card text says calc helper `_recognition_parameter_ids`(5); measured ratchet-semantics cc = **6** (= 1 + the 5 branch points) | `decision.md`/`handoff.json` already say 6 — **their docs are right, the card paraphrase is loose**; recorded; no gate-number change (file max 18 ≤ 21). |

## Unverified / not re-executed by the reviewer (carrier §3, L108–L116)

*The dispatch frames this as "5 items"; the carrier's §3 enumerates **7 numbered entries** — transcribed in full here so nothing is dropped (entries #1/#2/#4/#5 are literal non-re-executions, #3/#6/#7 are missing-evidence / provenance / coverage-scope caveats):*

1. **The pre-70dd revert family run itself** (50F/551P, 5:19) — read and cross-checked from stored raws + compare + git-object authenticity, **not re-executed** (internally consistent: 571 testcases both sides, 8 regressions, −33 passing subtests).
2. **Mutation rows 2 and 3** — verified from raws + tree/table classification, **not re-executed**; only row 1 was replicated end-to-end.
3. **TRIAGE corroboration for 6 of the 12 ids** (fc505, zr1103 ×2, zr803, zr804, zr1102::test_c1_no_orphaned) — **no such raws exist** anywhere in `RF-STEP9-TRIAGE` (F-01); the "pre-existing" property rests on the baseline run + the reviewer's identical re-run, which *were* verified.
4. **Sibling card diffs** (`RF-RATCHET-REST-B`, `RF-RATCHET-FIX-2`, `RF-STEP9-TRIAGE`) — content not reviewed (out of scope); only file counts and handoff statuses were read (§5).
5. **Non-`.py` fixtures in the iso** — 200 `.py` files under `tests|tools|scripts` re-hashed (exactly the 3 shipped differ); JSON/YAML/other fixtures **not individually re-hashed**.
6. **The family aggregate-sha formula** — not documented by the card; reproduced as `sha256(lines "<SHA256>  <path>" joined "\n", no trailing newline)` = `947AB2EC…`, but **cannot be proven** to be the formula they used (it matches; before/after files byte-identical anyway).
7. **Probe coverage** = the card's 25 probes (re-executed twice by the reviewer); behavior equivalence beyond probe+family+supplement scope **accepted as the card's method, not proven exhaustively**.

## Scope-if-merging (carrier §5, L145–L155, with the snapshot's corrections)

- **This card ships exactly 3 files**: `scripts/forecast/calc.py`, `scripts/generate_input_template.py`, `scripts/research/targets.py` — `changes.diff` **43882 B** (43880 chars), difflib-style headers, LF-only, **`git apply --check` rc 0 by the reviewer** (twice).
- **Merge batch composition (this landing's snapshot):**
  - `RF-RATCHET-FIX-2/a20260923-01` — **2 files** (`scripts/analysis/confidence.py`, `scripts/model_extensions.py`), 12078 B, `status=accepted_scoped` ✓ (landed).
  - `RF-RATCHET-REST-A/a20260923-01` — **3 files** (this card), 43882 B, `accepted_scoped` **by this landing**.
  - `RF-RATCHET-REST-B/a20260923-01` — **3 files** (`scripts/model_registry.py`, `scripts/revenue_core.py`, `scripts/revenue_publication.py`), 23626 B, `status=accepted_scoped` ✓ (its reviewer verdict was still `review_pending` at the REST-A reviewer's snapshot; landed by its own carrier pass at 2026-09-24 00:01).
  - `RF-STEP9-TRIAGE/a20260923-01` — **8 files** (6 tests + `tools/daily_t2_runner.py` + `tools/mutation_patrol.py`; `changes.diff` 11211 B / 9 hunks, guard-narrowing face `tests/test_single_owner_guard.py` entered the diff at 23:46 per the reviewer's snapshot, live mtime 23:58:11), `status=accepted_scoped` ✓ — **the card's "TRIAGE 7" framing is stale: plan for 8.**
  - (`RF-RATCHET-FIX` has no `changes.diff` — superseded by FIX-2.)
- **One apply + one commit + one push batch** = **8 `scripts/` files = exactly the 8 ratchet rows → 8/8 rows green**, plus TRIAGE's **8** step9-intrinsic files ⇒ **16 files** at this snapshot (vs the card's 12-file framing).
- **All four ratchet-family reviews are now ACCEPT (FIX-2, REST-A, REST-B, TRIAGE) ⇒ ratchet residual = 0 rows** in the merge batch. The REST-A reviewer's conditional ("residual would be 3 rows if REST-B's review rejects") **does not trigger** — REST-B is `accepted_scoped`.
- **KEEP-RED row-pass posture transcribed:** today's overall gate RED is caused only by sibling rows (`analysis/confidence 32>23`, `model_extensions 27>10` = FIX-2; `model_registry 28>9`, `revenue_core 23>6`, `revenue_publication 16>10` = REST-B). REST-A's 3 rows are green **under the test's own code** (iso full-row scan = 0 of my rows failing; scratch-pinned green case rc 0; per-row mutations naming each file/message). The live repo still scans **8** because nothing is applied yet — "8 → 5" is the verified iso-state claim; **"8 → 0" happens at the batch** (CF-RES-1 queue item ⑧ per `REMEDIATION_REGISTER.md` §94/§96).

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent of `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`), 2026-09-23.
- Status transition: `review_pending` → `accepted_scoped` in `handoff.json` (pre-image **6684 B / sha256 `7d684a072c6cff2ebae6434338be96f641c0955fd2d1a34bf6489163f940721a`**, `status=review_pending` / `signed=false`); the verdict itself was authored only by 独立复核 at `reviewer_report.md` L13 — never by the implementer and never by this file's author. The reviewer deliberately left the handoff unsigned for the parent to record (carrier L7) — **this landing is that recording; `signed` stays `false`** (no self-signing).
- **Exactly three files written + one decision erratum:**
  1. `review.md` — created (this file), transcription only;
  2. `handoff.json` — `status` → `accepted_scoped` + `status_before` + `status_authority` (carrier sha/pin, line ranges, byte proofs) + `bookkeeping` (F-01..F-07 with before/after values, merge-batch composition, EOL double-sha notation, files written, never-touched, no-git) + `carries` (unmapped/unproven + 70dd lineage) + `reviewer_status` + `next_action`; stale pre-verdict prose superseded under `*_historical_pre_verdict`; JSON re-parsed after write;
  3. `evidence/RF-RATCHET-REST-A/qualification.json` — created (dir created), `formula.state = accepted_scoped` (+ before) with carrier/F/merge-composition/EOL mirrors;
  4. **decision erratum (append-only)** — `## F-07 erratum (landing)` appended to `decision.md`.
- **sha256 before → after per file:**

| file | sha256 before | sha256 after |
|---|---|---|
| `decision.md` (append-only erratum, incl. the appended git-disclosure line) | `8eb31a32f48f50bf7d6839e4a80c093befcf7c9ad00ffb3cb1d9893339239cf4` (11160 B) | `b9651314d1d7a9a40689cf6c4af4c755ea25d6379b916d63527cf9b84ce8ab01` (18627 B; prefix-proof: first 11160 bytes still hash to the pre-image sha; +7467 B appended) |
| `handoff.json` | `7d684a072c6cff2ebae6434338be96f641c0955fd2d1a34bf6489163f940721a` (6684 B) | *(post-edit hash reported to the parent and mirrored in `qualification.json`)* |
| `review.md` | absent (none) | *(created; hash reported to the parent and mirrored in `qualification.json`)* |
| `evidence/RF-RATCHET-REST-A/qualification.json` | absent (none) | *(created; hash reported to the parent)* |

- **Untouched originals re-hashed at landing (0 bytes written):** `reviewer_report.md` `0282f01c…dac3` / 26208 B ✓, `reviewer_report.sha256` `624cbcd5…34d` / 85 B ✓, `ORACLE.md` `599a09a1…e77`, `binding.json` `fe84943b…41f3`, `commands.md` `99604de5…da84`, `changes.diff` `48ed4fec…782d0` / 43882 B ✓, `recovery.md` `b9ac51db…1a9f`, `evidence/README.md` `57868650…2d4a`, plus all evidence originals (`family_shas_*` `365b5094…`, `probe_compare.json`, `mutation_green.json`, `scan_green_iso.json`, `mypy_full_after.txt`, jupiters, `pre70dd/*`, `refactored/*`, `scratch/*`).
- **Git disclosure (corrected):** this landing pass executed exactly **one** git command, read-only — `git status --porcelain -- scripts tools tests` during pre-landing verification (empty output, before any write). **No state-changing git verb: 0 git writes, no index/HEAD/worktree mutation, nothing staged, no apply;** `git status` may refresh the `.git/index` stat-cache only (mtime, no content change — the same disclosure the reviewer made at carrier L104). Every other git fact in this file is transcribed from `reviewer_report.md`, not re-executed here. **0 production bytes written; 0 signatures produced;** `implementer_signed: false`; `implementer_never_signs_acceptance: true`; `verdict_is_transcribed_not_authored: true`; 独立复核 **N=1**.
