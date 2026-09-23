# F-EE1-FIX / a20260923-01 — review.md (carrier landing, bookkeeping transcription)

**This file is a bookkeeping transcription. It adds no acceptance of its own.**
It transcribes the verdict, verifications, findings and routing of the independent
reviewer's signed report; it does not review, does not re-rule, and does not sign.
**No self-signing**: the implementer did not self-accept (handoff pre-image measured below:
`status=review_pending`, `signed=false`), this carrier does not sign a verdict, and the sole
signer of the verdict remains the independent reviewer subagent (parent
`session-bfecd191-fbc3-4a66-8ed1-6562479bf102`), signature block of `reviewer_report.md`
lines 313–319. `verdict_is_transcribed_not_authored: true`.

## 0. Verdict block (transcribed)

**ACCEPT (verified)** — verbatim from `reviewer_report.md` §0 line 9: "## 0. Verdict —
**ACCEPT (verified)**, with 1 medium-low finding (F1, reviewer-closed) + 3 low/informational
(F2–F4)" and §12 line 317: "Verdict: **ACCEPT (verified)** per §0; attempt `a20260923-01`
remains unsigned (owner/carrier countersignature path per plan protocol)."

| pin | value |
|---|---|
| source authority (the report carrying the verdict) | `reviewer_report.md`, this attempt dir |
| byte proof | **25 635 B** (live measured at landing = dispatch-declared size) |
| sha256 (live re-hash at landing) | `588f8d955f4f06db1fc262aa3a490071604681f4f6a679dcfd65962846ecf652` |
| sidecar `reviewer_report.sha256` (86 B) | content-match: `588f8d95…  reviewer_report.md` == live re-hash ✓ |
| verdict line ranges | §0 = lines 9–16 (verdict heading line 9); §12 signature = 313–319 (verdict restated 317) |
| carrier of this transcription | this file `review.md`; its sha256 is recorded in `handoff.json.status_authority` and `evidence/F-EE1-FIX/qualification.json` (a file cannot embed its own hash) |

**独立复核 (carrier's own independent re-checks at landing, read-only):**
re-hashed `reviewer_report.md` → 25 635 B + `588f8d95…` matches the declared size and the
sidecar byte-for-byte; grepped the verdict string `ACCEPT (verified)` present at §0 L9 and
§12 L317; read the `handoff.json` pre-image → `status="review_pending"`, `signed=false`,
`signatures=[]`, `reviewer_of_record=null` (5 477 B, sha256
`c60dcc752cfffc5716aef5671b0b973facb8c0a5e187ab1e36d9d9ab6ca8e525`) — measured before any
landing write; spot re-read **live** `RF/tests/test_source_preparation.py:186-197` → the
ENV-11 docstring sentence "the receipt may never silently claim zero downloads" sits at
**:187-189** exactly as the F2 correction states (docstring of
`test_env11_missing_envelope_fails_closed`); spot re-read **live**
`harness/run_cases.py:95` (`companies.mkdir(parents=True)`, no `exist_ok`) + `:364`
(`raw.mkdir(parents=True)` creating `b2_root/project/companies`) + `:377`
(`_make_catalog(b2_root)`) → the F1 FileExistsError mechanism exists exactly as transcribed;
`oracle.md` re-measured = 11 079 B / sha256
`0fd9f5517850c4c13690f58765eb83e97deaf2bc2b541aa3acc71da637b646ed` — **untouched by this
landing** (frozen-first invariant); `reviewer_report.md` + sidecar re-hashed **after all
landing writes** to confirm unchanged (§5 below).

## 1. The eight verify items transcribed in substance (report §1–§8)

1. **Oracle frozen-first — VERIFIED (§1).** `oracle.md` CreationTime 12:06:03 (attempt dir
   12:05:11); LastWrite **12:11:32** still before the first judged-run artifact
   (`evidence/red_pre_harness_fix1/` 12:13, judged RED 12:14; fix 12:16, GREEN 12:16); the
   disclosed pre-run addition a8 present in oracle §2(a) with its in-file note; cases (a)–(f)
   frozen with explicit expectations; **`red_pre_harness_fix1/` preserved** (exit_code.txt
   `RED rc=1 elapsed_ms=1992` + stdout `TypeError: Object of type bytes is not JSON
   serializable` at `json.dumps`) and the oracle W-time predates it ⇒ oracle untouched.
2. **Two-end trace — every line re-read live at three repos, each confirmed (§2).** CW:
   `resolver.py:625-629/608-623`, contract test `:333-361`, `acquisition_service.py:94,
   180-185, 190`, `canonical_writer.py:194-208, 217, 222, 348, 374`, `resolver.py:1993-2010,
   1021-1029, 754-760, 1018, 976-983`, `cli.py:812-819, 1170-1177, 1188`; FF:
   `fetch_filing.py:663-666, 622-629, 880, 865-871, 706-715`; RF:
   `source_preparation.py:129-133, 171-184, 134-138`; CI `.github/workflows/quality.yml:26`;
   CW `test_resolution_envelope_fc704.py:238-249`; card-premise RF-has-no-`scripts/resolver.py`
   confirmed by listing + E2E-EXPAND oracle line 141. **Exactly one attribution slip found =
   F2** (the quoted ENV-11 sentence is `tests/test_source_preparation.py:187-189`, not
   `scripts/source_preparation.py` — mechanism lines themselves cited correctly).
3. **Evidence integrity — the reviewer's OWN independent re-hash of BOTH identity dicts
   from RAW files (§3).** Its throwaway script (its own code, not the attempt's verifier)
   imported `SourceRequest` from the iso CW src and rebuilt both identity dicts **from the
   raw frozen E2E-EXPAND s1 files** (`journal_rows.json`, `envelope.json`,
   `s1_fetch1_stdout.txt`, `request.json`), re-hashed: **E1 original → `…e8177b37…d53ecb`**
   == journal-row `request_id` (`downloaded_new`) == `two_end_mints.json` E1 — match;
   **E2 exact → `…47c3a925…e993`** == `envelope.handle_request_id` == FF response
   `handle.request_id` == `two_end_mints.json` E2 — match; ids differ from each other;
   **divergence fields = the 5** (`fiscal_period, form_type, language, provider,
   provider_document_id`) and its identity dicts **byte-equal** the artifact's; observed
   truth from the same raw files (journal `downloaded_new`, envelope `reused_existing` /
   `download_events=0`, FF `downloads=0` after a 2 043 710 B committed download); harness
   ids matched by artifact (`f9f96300…`/`7e4be4ca…`, same shape as live
   `e8177b37…`/`47c3a925…`) ⇒ **`both_ends_proven` stands.**
4. **The fix — byte-verified, D1 shape confirmed, manifest re-derived (§4).** Live
   `canonical_writer.py` = `c23a9358…c258` re-hashed at review close: unchanged; iso fixed
   copy + pinned `iso/canonical_writer.py.fixed` = `4bc65372…c6bc` (equal); `changes.diff`
   = 42 lines / 1 file / 2 hunks — the reviewer **applied the hunks to the LIVE bytes with
   its own parser: reconstructed sha256 = `4bc65372…` BYTE-EXACT** ⇒ the diff is the whole
   change; **D1 shape confirmed** (dataclass `replace` import added; exact resolve kept as
   write-gate with unchanged `REUSED_EXACT` raise; `replace(exact_resolution,
   request_id=request.request_id)` re-keys only the answering identity; `_remove_staged`
   retained; hunk ends before `:217`/`:222` ⇒ result fields provably untouched);
   **manifest 635 files compared / exactly 1 mismatch** (`canonical_writer.py`) re-derived;
   **22/22 live pins re-hashed at reviewer close: 0 changed.**
5. **Cases — raw evidence read + the reviewer's own re-runs (§5).** RED `cases_red.json`
   (rc=1, 2 243 ms) fails exactly **a3/a4/a5/a6 + c1/c2/c4** with a1/a2/a7/a8 (and b1/d)
   passing ⇒ the RED is the fake zero, not a broken harness; GREEN (rc=0) all-pass;
   mutation `exit_codes.txt` `reverted_sha=c23a9358…` **== live (re-hashed)**,
   `restored_sha=4bc65372…`, failure-set equality RED == mutation-revert, rc sequence
   **1 → 0 → 1 → 0**; the reviewer's **own re-runs of both arms** (its exact argv, its own
   `%TEMP%` dirs, offline): RED on the pristine copy **rc=1 with the identical failure set**
   (a3/a4/a5/a6 + c1/c2/c4, id pair reproduced) and GREEN on the fixed copy **rc=0 all
   pass**, arm shas verified before+after each run.
6. **Regressions — raw evidence re-read + the two mandated re-runs (§6).** Raw: f3a
   `23 passed in 8.26s` rc=0, f3b `23 passed in 7.79s`, f1 `11 passed in 3.51s` (+ the
   disclosed no-PYTHONPATH artifact `5 failed, 6 passed` + `ModuleNotFoundError` preserved),
   f2 `116 passed, 1 skipped, 39 subtests`, f4 summary exit 0 / S2-S6-S4 pass /
   `production_writes 0` / `network_scope "none (live gate never)"` / preflight `drift=[]`,
   f5 `2 passed, 1 skipped`; **the reviewer re-ran (a)-harness on both arms** (rc1/rc0, §5)
   **and the E2E tests file** → `2 passed, 1 skipped in 45.47s`, rc=0 (live test
   honest-skip) — matches f5.
7. **D1/D2/D3 rationale — quotes verified verbatim (§7).** FC-704 `resolver.py:976-983`
   journal-wins "e.g. downloaded_new after an ensure" supports id-match-on-ensure while the
   strict-equality skip stays untouched; every sibling path (`canonical_writer.py:157`,
   `close_gap.py:460/430/446`, `cli.py:1170-1177`, sidecar `:348/:374`, result `:217`)
   keys to the ORIGINAL request ⇒ D1 needs no special-casing; D2 rejected consistently
   (per-request append-only contract; stable-key matching would widen download claims);
   **D3 rejected by contract with the quotes verified**: FF `test_fetch_filing.py:285-288`
   "forwarded verbatim (no independent re-derivation of download evidence)" + `:315-318`
   impossible-count rejection + RF FC-904 `source_preparation.py:134-138` "never a blind
   full recompute" + ENV-11 fail-closed (quote file = F2); minimal-change claim holds
   (byte-exact diff + (b)/(d) green both arms + 23-test CW family green both arms).
8. **Boundaries — re-checked at the reviewer's close (§8).** RF porcelain: only the attempt
   dir + 2 pre-existing leftovers (mtimes 09-20/09-21, predating attempt creation 09-23
   12:05), no modified/deleted tracked file; FF porcelain empty; CW porcelain 3 pre-existing
   modifications (all 09-23 02:13, ~10 h before the attempt); live pins 22/22 unchanged;
   **zero network — each of the 25 `commands.json` entries carries
   `network: "disabled"`** (E2E summary `network_scope "none"`; neither the attempt nor the
   review holds a reachability artifact); **git: the sole verb is the read-only
   `git status --porcelain` (PORCELAIN-01)** — `recovery.md`'s `git apply -R` /
   `git checkout --` lines are recovery instructions for a future carrier, not executed
   commands (the reviewer's own git usage: read-only `status --porcelain` ×3); reviewer
   product writes = 0 (scratch solely in `%TEMP%\f_ee1_rev`, `-B` + no pycache).

## 2. Findings F1–F4 with dispositions (transcribed §9 + landing actions)

| id | sev | finding (substance) | disposition after this landing |
|---|---|---|---|
| F1 | MEDIUM-LOW | Undisclosed harness `FileExistsError` (`run_cases.py:95` via `:377`; `:362-364` already created `project/companies`) ⇒ oracle **(b)-b2 never executed in any of the 4 judged runs** (`context.harness_exception` in every case JSON); decision §4 showed "(b) PASS (5/5)" without flagging it; §7 omitted it | **reviewer-closed**: the reviewer executed b2 itself on **BOTH arms** → `reused_equivalent` / 0 journal rows / envelope `reused_existing` / `download_events` 0 / FF `downloads` 0 — **expectation HOLDS**, bounded (fires after all other checks; ruling face unaffected). **Record-fixed during this landing**: §7 item 7 disclosure added, §4 "(5/5)" claim annotated (retained), reviewer output attached as `evidence/reviewer_b2_execution.json` (labeled reviewer-executed post-hoc, source = report sha) |
| F2 | LOW | Quote "receipt may never silently claim zero downloads" attributed inside `scripts/source_preparation.py:129-133,171-184`; the sentence is `tests/test_source_preparation.py:187-189` (ENV-11 docstring) | **Record-fixed during this landing**: decision.md §1 Propagation attribution corrected (mechanism citations unchanged and verified), original phrasing retained verbatim in the note; `oracle.md` §1's identical pre-run wording left byte-untouched by design (frozen-first; correction of record = decision.md + this file + qualification mirror); carrier spot-checked the corrected lines live |
| F3 | LOW (info) | decision.md §4/§5 runtimes ≠ raw pytest in-run times (wall-clock vs in-run; `commands.json` agrees with raw) | **Record-fixed during this landing**: §4 and §5 annotated (raw in-run = 8.26/7.79, 3.51, 16.10, 40.20 s; commands.json matches raw); **annotation only — no number deleted** |
| F4 | INFO | Disclosed §7 defects 3/4/5 have prose disclosure without preserved raw artifacts (superseded runs) | **noted** (acknowledged): unverifiable by the reviewer, but the superseding runs carry the recorded results (23/23 files, parsed JSONs, re-run compile) |

## 3. Unverified / carried forward (transcribed §10)

- **Live S1 `downloads==1` E2E check** — not re-run (network forbidden by card);
  offline equivalence stands (reviewer's §3 recompute + its a6 GREEN flip + frozen live
  pins). **Live S1 re-run = owner re-authorize post-landing.**
- **Full CW CLI subprocess ensure face** — not run offline end-to-end; the judged harness
  drives `SourceAcquisitionService.ensure` → writer → journal → envelope directly
  (card-sanctioned unit-harness truth); E2E runner covers the no-download chain
  (S2/S3/S5/S6 green).
- **RF/FF end-to-end receipt for a `downloads==1` envelope** — covered transitively (RF
  ENV-09 events=1 → download_calls=1; FF READ-10 families), not by a live chain.
- **CW 23-family / RF 11 / FF 116 families** — re-verified **from raw evidence alone**;
  the reviewer re-executed only the two mandated runs ((a)-harness both arms + E2E tests
  file).
- **b2 as a judged arm** — vacuous in the attempt (F1); executed by the reviewer, not by
  the attempt (carried as `evidence/reviewer_b2_execution.json`).
- **Attempt signature** — stays unsigned (`signed=false`); **carriers countersign** per
  plan protocol; this report is the review record.

## 4. Routing recommendation transcribed (§11) + parent landing update

- **Fix surface = company-wiki**: one file `src/company_wiki/source_catalog/canonical_writer.py`,
  delivered as `<ATT>\changes.diff` (**byte-verified**: diff-applied-to-live reconstruction
  = `4bc65372…`). **RF and FF stay byte-clean by contract (D3)** — their porcelain at close
  confirms zero attempt writes.
- **Parent route (of the two offered): CW-native commit by the parent**, plus an
  **annotation in the plan register mapping card `F-EE1-FIX` → `<ATT>` → CW commit sha**
  (rationale: defect, both mints, fix and contract tests are CW-internal; a re-cut CW-native
  card would orphan this attempt's frozen oracle/evidence chain; re-cut becomes preferable
  only if the register forbids cross-repo mapping notes).
- **After landing**: owner re-authorizes the live S1 re-run (§10); commit recovery =
  `git apply -R <ATT>\changes.diff` (byte-verified inverse).
- **Attempt → carriers** with: report + `.sha256`, F1 disclosure addendum, F2/F3 wording
  corrections at landing.
- **Parent landing update (received mid-landing from the parent agent; source = parent
  message, recorded in `handoff.json` `bookkeeping.parent_commit`)**: CW commit landed =
  **`bf0c8b2`** (branch `fcap`, 1 file 20+/3−, hooks config-doctor/host-guard/unique/ruff/
  mypy all pass, 4-file test family 35 passed + ruff rc0); live `canonical_writer.py` after
  = **`4bc653725febcc755e3a01ac48227a6b0799c4c262968356b356f8cb42d3c6bc`** / 18 380 B —
  equal to the iso fixed copy as the reviewer's byte-exact reconstruction predicted;
  disclosed application detail: `changes.diff` carries difflib path-label suffixes
  `(live/pristine)`/`(F-EE1-FIX)` that `git apply` requires truncating (path-line labels
  only, zero content change); register **§58** cross-repo mapping annotation written
  (card → attempt → commit sha; route = keep frozen chain, no card re-cut).

## 5. Record fixes + carrier write surface (this landing)

**Record fixes on `decision.md` (history-retaining; full chain, measured in order):**

| step | bytes | sha256 |
|---|---|---|
| pre-image (as reviewed) | 14 899 | `95eccc06da95140d6699c90a0657c16291adcdb51b7e572b8f96c464484d07f6` |
| after F1 (§4 (b) annotation + §7 item 7) | 16 273 | `caeb47cc160f4fb07c64f905e17fd50a9a48d39b325cc55da623138da7a52068` |
| after F2 (§1 attribution fix, original retained) | 17 180 | `bd6d2a715e906d6d2cfcb37e96c15d3914abb7c56b06880c38b05fe11c268f3b` |
| after F3 (§4+§5 runtime annotations) — final | 18 267 | `74f8c2869a9a1ce24c6b2c788d3a5756365a17de7fb0f59b8c6d30b8ac6a2a76` |

Plus one new evidence file: `evidence/reviewer_b2_execution.json` (new — no pre-image),
3 616 B, sha256
`2ff9e69f00cd9e1aae1885e780024384568504de813032cd27a973712bb22323`.

**This carrier's write surface for the landing = exactly**: F1/F2/F3 record fixes to
`decision.md` + `evidence/reviewer_b2_execution.json` (attached evidence) + the three
carriers — `review.md` (this file), `handoff.json`, `evidence/F-EE1-FIX/qualification.json`.
**Untouched**: `reviewer_report.md` (25 635 B / `588f8d95…`) and `reviewer_report.sha256`
(86 B / `855c44db…`) — re-hashed after all writes to confirm; `oracle.md` (frozen-first);
`oracle`-adjacent artifacts `binding_before/after.json`, `commands.json`, `recovery.md`,
`changes.diff`, `harness/*`, all pre-existing `evidence/**` raw files. **No git (zero git
verbs executed by this landing); no self-signing; no product writes; no network.**

- Status transition recorded in `handoff.json`: `review_pending` → `accepted_scoped`
  (`status_before_bookkeeping_fix = review_pending`); the verdict itself was authored only
  in `reviewer_report.md` (§0 L9 / §12 L317) by 独立复核 — never by the implementer and
  never by this file's author.
- `implementer_signed: false`; `carrier_signed: false`;
  `verdict_is_transcribed_not_authored: true`; no signature produced.
  **Bookkeeping transcription, adds no acceptance of its own.**
