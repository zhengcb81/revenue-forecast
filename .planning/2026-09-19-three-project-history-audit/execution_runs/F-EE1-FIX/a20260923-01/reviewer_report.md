# Reviewer report — F-EE1-FIX / a20260923-01 (FC-704-class fake download zero)

- **Card / attempt**: F-EE1-FIX · `a20260923-01` (status at handoff: review_pending, unsigned)
- **Reviewer**: independent review subagent of session `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`
- **Review time**: 2026-09-23 12:35–12:56 local (+01:00) / 11:35–11:56 Z
- **Mode**: sampled read/grep/pwsh re-verification; my own runs offline into `%TEMP%` (`%TEMP%\f_ee1_rev`); NO network; no product writes; no state-changing git; deliverables = this report + `.sha256` (2 files under `<ATT>`), nothing else written in any worktree.
- **Method note**: each citation in decision.md/oracle.md was re-read at the live line numbers; hashes, counts and case outcomes were re-derived by me, not taken from the attempt's claims.

## 0. Verdict — **ACCEPT (verified)**, with 1 medium-low finding (F1, reviewer-closed) + 3 low/informational (F2–F4)

The two-end root cause is real and fully proven at both ends; the delivered fix is byte-verified,
minimal, and behavior-scoped exactly as claimed; RED/GREEN/mutation and the regression families
are reproduced or re-derived from raw evidence. The attempt handoff remains **unsigned** (I do
not self-sign an attempt I did not author) — it goes to the carriers next with this report as the
review record. One undisclosed harness defect (F1) exists; I executed the skipped sub-case myself
and it passes in both arms, so the verdict does not change.

## 1. Oracle frozen-first — VERIFIED

| fact | evidence I re-read | ok |
|---|---|---|
| oracle created before any judged run | `oracle.md` CreationTime 2026-09-23 **12:06:03**; attempt dir created 12:05:11 | ✓ |
| oracle not edited after runs began | `oracle.md` LastWrite **12:11:32**, still before first judged-run artifact `evidence/red_pre_harness_fix1/` (12:13) and judged RED (12:14); fix applied 12:16, GREEN 12:16 — oracle W-time precedes each run artifact | ✓ |
| handoff's "one pre-run addition a8" | a8 present in oracle §2(a) with the in-file note; W-time consistent with pre-run edit | ✓ |
| cases (a)–(f) frozen | oracle §2: (a) a1–a8, (b) b1+b2, (c) 3-way, (d) d1–d3, (e) mutation, (f) f3a/f3b/f1/f2/f4/f5 with explicit expectations | ✓ |
| `red_pre_harness_fix1/` preservation (harness-defect preservation, oracle untouched) | dir exists (exit_code.txt `RED rc=1 elapsed_ms=1992` + stdout with `TypeError: Object of type bytes is not JSON serializable` at `json.dumps`); oracle W-time 12:11:32 predates it — oracle untouched | ✓ |

## 2. Two-end trace — citations re-read live (each confirmed)

Identity / hash source (CW = `C:\Users\郑曾波\Projects\company-wiki`):

| citation | live content I read | ok |
|---|---|---|
| `resolver.py:625-629` | `return "urn:company-wiki:source-request:sha256:" + _json_hash(self.identity_dict())` — deterministic hash | ✓ |
| `resolver.py:608-623` | `identity_dict()` with the 13 fields (schema_version…mode) as quoted | ✓ |
| `tests/contract/test_source_catalog_resolver.py:333-361` | `test_source_request_id_is_deterministic_and_action_independent` — same-id across `allow_download`, differs across security_id | ✓ |

End E1 — journal mint (ORIGINAL request):

| citation | live content | ok |
|---|---|---|
| `acquisition_service.py:94` | `"request_id": request.request_id,` inside `common = {` (line 93) | ✓ |
| `acquisition_service.py:180-185` | `attempt = self.journal.record(outcome=outcome, …, **common)` with `outcome="downloaded_new"` set at :174-176 for `IMPORTED_NEW` | ✓ |
| `acquisition_service.py:190` | `resolution=imported.resolution` on the `SourceEnsureResult` | ✓ |

End E2 — resolution mint (SYNTHESIZED exact request):

| citation | live content | ok |
|---|---|---|
| `canonical_writer.py:194-207` | `exact_request = SourceRequest(...)` filling `form_type/fiscal_year/fiscal_period/language` from `request or candidate`, `provider/provider_document_id` from `candidate`, `mode` not carried (→ dropped) | ✓ |
| `canonical_writer.py:208` | `resolution = SourceResolver(self.catalog).resolve(exact_request)` | ✓ |
| `resolver.py:1993-2010` | `_result` stamps `request_id=request.request_id` — of the exact_request | ✓ |
| `canonical_writer.py:217` | `request_id=request.request_id` — **ORIGINAL** | ✓ |
| `canonical_writer.py:222` | `resolution=resolution` — **SYNTHESIZED exact-keyed** → intra-object inconsistency in the same result | ✓ |
| `canonical_writer.py:348` / `:374` | sidecar `"request_id": request.request_id` / `"request": request.to_dict()` — **ORIGINAL** | ✓ |

Skip → structural false zero:

| citation | live content | ok |
|---|---|---|
| `resolver.py:1021-1029` | `download_events = 0` at :1021; loop `if attempt.request_id != resolution.request_id: continue` at :1025-1027 ⇒ downloaded_new row skipped | ✓ |
| `resolver.py:754-760` | `_STRUCTURAL_OUTCOME[REUSED_EXACT] = "reused_existing"` (:755) | ✓ |
| `resolver.py:1018` | `outcome = _STRUCTURAL_OUTCOME.get(resolution.status)` before the loop | ✓ |
| `resolver.py:976-983` (FC-704 spec, quoted by decision §2) | verbatim: "Journal entry for ``request_id`` wins (the real outcome, e.g. downloaded_new after an ensure); without an entry the outcome is structural … Reads the journal only" | ✓ |
| `cli.py:812-819` | ensure-face `build_resolution_envelope(ensured.resolution, …, journal=AcquisitionJournal(...))` | ✓ |
| `cli.py:1170-1177` + `:1188` | read-only face resolves with `request` from `source_request()`, envelope built from that resolution | ✓ |

Propagation:

| citation | live content | ok |
|---|---|---|
| FF `fetch_filing.py:663-666` | "`stats["downloads"]` is the download event count from the final resolution envelope (0 unless a download actually committed)" — READ-10 | ✓ |
| FF `fetch_filing.py:622-629` | `_record_download_events`: `stats["downloads"] = envelope.download_events` | ✓ |
| FF `fetch_filing.py:880` | `handle["request_id"] = resolution.get("request_id")` (the field the false zero poisons) | ✓ |
| FF `fetch_filing.py:865-871` | exactly-one-match requirement (fix does not touch `matches` ⇒ behavior identical) | ✓ |
| FF `fetch_filing.py:706-715` | FF identity normalization adds `entity/market/security_id` (validates the E1 reconstruction) | ✓ |
| RF `source_preparation.py:129-133` | `download_events` validated ∈ {0,1}, fail-closed raise | ✓ |
| RF `source_preparation.py:171-184` | `record["reuse_receipt"]["download_calls"] = download_events` (:174) from the envelope | ✓ |
| RF `source_preparation.py:134-138` | FC-904 "SOURCED from the envelope … (never a blind full recompute)" | ✓ |
| `.github/workflows/quality.yml:26` | `PYTHONPATH=$SIBLING_DIR/company-wiki/src` (CI-faithful) | ✓ |
| CW `tests/contract/test_resolution_envelope_fc704.py:238-249` | ENV-08 envelope build never writes journal (oracle d3 semantics) | ✓ |
| card-premise: RF has no `scripts/resolver.py` | confirmed by directory listing; E2E-EXPAND oracle line 141 shows `PYTHONPATH = <spy>;<RF>/scripts;<CW>/src` | ✓ |

**F2 (LOW, citation slip)**: the quoted sentence "receipt may never silently claim zero
downloads" lives in `RF tests/test_source_preparation.py:187-189` (ENV-11 test docstring, ENV-11
test at :186-197), not in `scripts/source_preparation.py` where decision.md §2.6 / oracle §1
place it inside the `:129-133,171-184` parenthetical. The mechanism lines themselves are cited
correctly; only the quoted sentence's file attribution is one file off. 域 = quote attribution.

## 3. Evidence integrity — BOTH ids re-computed by me with the product's own hash

Independent throwaway script `%TEMP%\f_ee1_rev\two_end_recheck.py` (my own code, not the
attempt's `verify_evidence_hashes.py`): imports `SourceRequest` from the iso CW src, rebuilds
both identity dicts **from the raw frozen E2E-EXPAND s1 files** (`journal_rows.json`,
`envelope.json`, `s1_fetch1_stdout.txt`, `request.json`), re-hashes:

- E1 original identity → `urn:company-wiki:source-request:sha256:e8177b377da8…d53ecb`
  == journal row `request_id` (outcome `downloaded_new`) **and** == `two_end_mints.json` E1 — **match**
- E2 exact identity → `urn:company-wiki:source-request:sha256:47c3a925dc2a…e993`
  == `envelope.handle_request_id` == FF response `handle.request_id` **and** == `two_end_mints.json` E2 — **match**
- ids differ from each other; divergence fields = `fiscal_period, form_type, language, provider, provider_document_id` (== the artifact's list); my identity dicts are byte-equal to the artifact's identity dicts
- observed truth from the same raw files: journal `downloaded_new`, envelope `reused_existing` / `download_events=0`, FF `downloads=0` after a 2 043 710 B committed download (handle `byte_size`, `content_sha256 c1527297…`)
- harness-side ids matched **by artifact** as instructed: `cases_red/green.json` carry
  `f9f96300…` (original) vs `7e4be4ca…` (exact) — same shape as the live pair
  `e8177b37…`/`47c3a925…`, different identity inputs. **both_ends_proven stands.**

## 4. The fix — byte-verified, D1 shape confirmed, manifest re-derived

- live `company-wiki/src/company_wiki/source_catalog/canonical_writer.py` =
  `c23a935852cce71a9f1cc2454337cb714ec185b0823c33ddcc50407b7687c258` — re-hashed by me at review close: **unchanged**
- iso fixed copy + pinned `iso/canonical_writer.py.fixed` =
  `4bc653725febcc755e3a01ac48227a6b0799c4c262968356b356f8cb42d3c6bc` (both equal)
- `changes.diff`: **42 lines, 1 file, 2 hunks** (`@@ -2,7 +2,7 @@`, `@@ -205,11 +205,28 @@`). I applied the hunks to the LIVE bytes with my own parser: reconstructed sha256 =
  `4bc65372…` = delivered fixed file, **BYTE-EXACT** ⇒ the diff is the whole change, nothing else.
- D1 shape, read in the diff and in the fixed file:
  1. `from dataclasses import dataclass, replace` (import added);
  2. exact resolve kept as the **write-gate**: `exact_resolution = …resolve(exact_request)` +
     unchanged `if exact_resolution.status is not ResolutionStatus.REUSED_EXACT: raise CanonicalImportError(...)` (a post-write verification failure still fails closed);
  3. `resolution = replace(exact_resolution, request_id=request.request_id)` — the answering
     identity alone is re-keyed to the caller;
  4. `_remove_staged(staged)` retained (the attempt's self-caught restore is present);
  5. hunk ends before `:217`/`:222` ⇒ `CanonicalImportResult.request_id`, `status`, `matches`,
     `reason` and the rest of the file are provably untouched (byte-exact
     reconstruction guarantees this for the 405-line file).
- **binding_after 635/1 re-derived by me**: enumerated `iso/cw` (excluding caches) →
  **635 files compared, exactly 1 mismatch** = `canonical_writer.py` (live `c23a9358…` vs iso `4bc65372…`). Before-manifest: 0/635 mismatches at binding time (recorded).
- **22/22 live pins re-hashed at MY close**: `binding_before.json` and `binding_after.json` each
  hold 22 pins; my re-hash vs both files: **0 changed** (`live_pins_changed=0` confirmed by me).

## 5. Cases (a)–(e): raw evidence read + my own RED/GREEN/mutation re-runs

Raw evidence read (4 case JSONs + stdout/exit artifacts):

- **RED** `cases_red.json` (rc=1, 2243 ms): (a) fails **exactly a3/a4/a5/a6**
  (ids `f9f96300…` ≠ `7e4be4ca…`, outcome `reused_existing`, `download_events 0`, FF `downloads 0`)
  while a1/a2 (status imported, fetch_calls 1, journal row keyed original), a7 (FF accepts
  envelope), a8 (read-only face reports `downloaded_new`/1) pass ⇒ the RED is the fake zero,
  not a broken harness. (c) fails c1/c2/c4, c3 passes (E1 mint internally consistent).
  (b1) and (d) pass (d: fetch_calls stays 1, 1 downloaded_new row, 2 rows total, envelope
  rebuild byte-identical, journal bytes unchanged via sha256 compare, second read-only face
  `reused_existing`/0).
- **GREEN** `cases_green.json` (rc=0, 2263 ms): a1–a8 ok (11 checks), (b) 5 checks,
  (c) 4-way equality ok, (d) 9 checks ok.
- **mutation (e)**: `exit_codes.txt` records
  `reverted_sha=c23a9358… mutation_red_rc=1 restored_sha=4bc65372… restored_rc=0` — the
  revert hash **equals live `c23a9358…`** (re-hashed by me); I programmatically compared
  failure dicts: **RED failure set == mutation-revert failure set** (a3/a4/a5/a6 + c1/c2/c4),
  mutation-restored and GREEN failure sets empty. rc sequence across the attempt:
  **1 → 0 → 1 → 0** as required.

**My own re-runs** (their exact argv from `commands.json`, two `%TEMP%` dirs, offline):

| arm | artifact | result |
|---|---|---|
| RED on live-sha copy (`iso_pristine`, sha `c23a9358…` verified before+after) | `%TEMP%\f_ee1_rev\rev_cases_red.json` | **rc=1**, failures = a3/a4/a5/a6 + c1/c2/c4 — identical to their RED; id pair `f9f96300…`/`7e4be4ca…` reproduced |
| GREEN on fixed copy (`iso_fixed`, sha `4bc65372…` verified before+after) | `%TEMP%\f_ee1_rev\rev_cases_green.json` | **rc=0**, (a)(b)(c)(d) all PASS |
| mutation arm re-run (= the pristine arm above) | same RED run | rc=1, revert-hash == live `c23a9358…` ⇒ non-vacuity independently re-confirmed |

**F1 (MEDIUM-LOW, UNDISCLOSED harness defect — bounded, reviewer-closed):**
in **each** judged artifact (`red`, `green`, `mutation_red`, `mutation_restored_green`, and my
re-runs) `context.harness_exception` records `FileExistsError` at `run_cases.py:95`
(`companies.mkdir(parents=True)`) called from `:377` for `b2_root`, because `:362-364` had
already created `project/companies`. Consequence: **oracle case (b)-b2 ("fresh seeded catalog,
empty journal → read-only resolve `reused_existing`/0) never executed in any attempt arm**;
case (b)'s 5 recorded checks consist of b1 alone, while decision.md §4 presents b2 under "(b) … PASS
(5/5)" without flagging the gap, and §7 does not list this defect (its disclosure list has
5 defects + item 6; this is a 6th). Bounded because: the exception fires after all (a)/(c)/(d)/(b1)
checks are recorded (b2 is the last block), ctx.update is skipped (each of the 4 JSONs shows context keys
`['harness_exception','request_id']` as its keys), and the ruling face (a)/(c) is unaffected.
**Reviewer closure**: I executed (b)-b2 myself (`%TEMP%\f_ee1_rev\b2_independent.py`, product
APIs, harness envelope helper) on BOTH arms → `readonly_status=reused_equivalent`, journal
`0 rows`, envelope `reused_existing`, `download_events 0`, FF `downloads 0` — b2's frozen
expectation holds pristine and fixed. Owner action: register this as disclosed harness defect
#5 (or an addendum to §7) and attach my b2 output. 域 = disclosure completeness of §7.

## 6. Regressions — raw evidence re-read + the two mandated re-runs

Re-verified from raw artifacts (no re-execution mandated):

| id | raw evidence I read | ok |
|---|---|---|
| f3a CW pristine | `cw_contract_baseline_pristine.txt`: `23 passed in 8.26s` rc=0 | ✓ |
| f3b CW fixed | `cw_contract_fixed.txt`: `23 passed in 7.79s` rc=0 | ✓ |
| f1 RF ENV-11 family | `rf_env11_family.txt`: `11 passed in 3.51s` rc=0; CI PYTHONPATH line 26 verified; disclosed no-PYTHONPATH attempt preserved with `5 failed, 6 passed` + `ModuleNotFoundError: No module named 'company_wiki'` | ✓ |
| f2 FF READ-10 family | `ff_read10_family.txt`: `116 passed, 1 skipped, 39 subtests passed` rc=0 | ✓ |
| f4 E2E runner | `summary.json` (parsed by me): exit_code 0, S2/S3/S5/S6/S4 status `pass`, `production_writes 0`, `network_scope "none (live gate never)"`; `preflight.json`: `drift=[]`, 8 pins; `e2e_runner_exit.txt` `rc=0 elapsed_ms=40438` | ✓ |
| f5 E2E tests file | `e2e_tests_file.txt`: `2 passed, 1 skipped` rc=0 | ✓ |

My own re-runs (the mandated two):

- **(a)-case harness**: both arms — see §5 table (RED rc=1 / GREEN rc=0, identical failure sets).
- **E2E tests file**: `RF tests/test_cross_repo_chain_e2e.py`, `%TEMP%\f_ee1_rev\bt_e2e`
  basetemp, `-p no:cacheprovider`, `-B`, `PYTHONPATH=company-wiki/src` (CI form),
  `RF_E2E_LIVE_DOWNLOAD` unset → **`2 passed, 1 skipped in 45.47s`, rc=0** (live test honest-skip) — matches f5.

**F3 (LOW/informational)**: decision.md §4/§5 wall-clock runtimes differ from the pytest
self-reported times in the raw files (CW 9.68/9.26 s vs 8.26/7.79 s; RF 4.7 s vs 3.51 s;
FF 17.3 s vs 16.10 s; tests file 41.4 s vs 40.20 s) — `commands.json` matches the raw files,
so §5 numbers read as whole-invocation wall-clock (interpreter startup included). No outcome
impact; suggest the owner align the table wording at landing.

## 7. D1/D2/D3 rationale sanity — VERIFIED

- **FC-704 spec supports id-match-on-ensure**: `resolver.py:976-983` (read above) states the
  journal entry for `request_id` wins "e.g. downloaded_new after an ensure" ⇒ the design intends
  envelope and journal to agree on the ensure's id; D1 restores that intent while leaving the
  strict-equality skip logic (in the code, `:1025-1027`) untouched.
- **Sibling paths already key to the ORIGINAL request** — each cite re-read, each uses the
  original-request id (not the synthesized one): `canonical_writer.py:157`
  (`resolve(request)` in the dedup branch), `close_gap.py:460` (`resolve(request)`) with journal
  keyed `binding.request_id` at `close_gap.py:430` and `:446`, `cli.py:1170-1177` (read-only face),
  sidecar `canonical_writer.py:348` (`request.request_id`) and `:374` (`request.to_dict()`),
  result `canonical_writer.py:217` (`request.request_id`). The IMPORTED_NEW branch alone disagreed;
  D1 makes it consistent ⇒ no face needs special-casing. ✓
- **D2 rejected consistently**: journal-wins is a per-request contract (append-only rows keyed by
  request; `resolver.py:1023-1027` comments say so); stable-key matching would attach
  `downloaded_new` rows to unrelated requests resolving to the same document — widening download
  claims, opposite the honesty rule, and a bigger change to frozen reconciliation. Rejection
  consistent with the contracts I read. ✓
- **D3 rejected by contract, quotes verified verbatim**: FF `test_fetch_filing.py:285-288`
  "forwarded verbatim (no independent re-derivation of download evidence)" ✓;
  `test_fetch_filing.py:315-318` impossible-count rejection (consumer fails closed) ✓;
  RF FC-904 `source_preparation.py:134-138` "never a blind full recompute" + ENV-11 test
  `:186-197` fail-closed (quote file = F2 above) ✓. Consumers may not re-derive producer
  evidence ⇒ compensation in FF/RF is contract-forbidden. ✓
- **Minimal-change claim** holds: byte-exact diff (§4) + (b)/(d) green in both arms + 23-test CW
  family green in both arms.

## 8. Boundaries — re-checked at MY close

- **RF porcelain** (my close, after my runs): `?? .planning/…/execution_runs/F-EE1-FIX/` (the
  attempt = deliverables) + 2 pre-existing leftovers — `.tmp-r41-mutation/` (mtime
  2026-09-20 18:31) and `assurance/…/plan_inputs.json.bak` (mtime 2026-09-21 07:09), both
  predating attempt creation 2026-09-23 12:05. No modified/deleted tracked file. ✓
- **FF porcelain**: empty. ✓
- **CW porcelain**: ` M CLAUDE.md`, ` M README.md`, ` M src/…/artifact_dag.py`, all LastWrite
  2026-09-23 **02:13:17** — ~10 h before the attempt; pre-existing, not attempt writes. ✓
- **Live pins**: 22/22 unchanged at my close (re-hashed against both binding files, 0 diff). ✓
- **Zero network**: `commands.json` — each of the 25 command entries carries `network: "disabled"`
  (legend: zero probes, zero downloads); attempt's E2E regression summary declares
  `network_scope "none"`; the attempt holds no reachability artifact of its own (not needed —
  nothing probed). My review used no network tool and ran offline by construction. ✓
- **No git mutations**: the sole git verb executed in `commands.json` is
  `git status --porcelain` (PORCELAIN-01); `recovery.md` contains `git apply -R` /
  `git checkout --` lines as **recovery instructions for a future carrier**, not as executed
  commands. My own git usage this review: `git status --porcelain` read-only ×3. ✓
- **No product writes by me**: RF/FF/CW porcelain at my close identical to the attempt's
  close-state; no `__pycache__` directory with mtime after my runs appeared in RF/FF/CW
  (my runs used `-B` + `PYTHONDONTWRITEBYTECODE=1`); my scratch lives solely in `%TEMP%\f_ee1_rev`. ✓

**The 4 disclosed harness/invocation defects (+2 disclosures) in decision.md §7 — judged:**

1. `red_pre_harness_fix1/` bytes-serialization failure → **ack-or-flag: ACK**. Raw artifact
   preserved, oracle W-time proves no oracle edit, and the fix (record sha256 of bytes in
   `_check`, `run_cases.py:184-193`) preserves equality semantics (hash equality ⇔ byte
   equality for the compared journal blobs). Judged RED came from the re-run.
2. RF no-PYTHONPATH first attempt → **ACK**. Raw artifact preserved (5 failed/6 passed,
   `ModuleNotFoundError`), CI line `quality.yml:26` verified, faithful re-run 11/11. Environment
   artifact honestly labeled, not hidden.
3. CW relative-path rc=4 usage error → **F4-ACK**: disclosed in decision §7 + `commands.json`,
   **no raw artifact preserved** (superseded run) — unverifiable by me, but the superseding
   absolute-path results are in the recorded 23/23 files.
4. `Get-Content | python` `Invalid \escape` pretty-print → **ACK**: claimed file-level parse
   holds — I parsed `summary.json` and `preflight.json` myself (both valid JSON); runner's own
   `rc=0` + summary are authoritative, as stated.
5. compile-check unexpanded `$TEMP` first attempt → **ACK**: trivial tooling slip, re-run
   disclosed, no artifact (F4 same class), no bearing on any judged result.
6. live S1 `downloads==1` not re-executed → **ACK**: correct under the card's network ban;
   listed in `unproven` with equivalence evidence that I independently re-verified (§3 + a6
   flips to 1 in my GREEN run).

## 9. Findings summary

| id | sev | finding | disposition |
|---|---|---|---|
| F1 | MEDIUM-LOW | Undisclosed harness `FileExistsError` (`run_cases.py:95/377`) ⇒ oracle (b)-b2 never executed in each of the 4 judged runs; decision §4 shows "(b) PASS (5/5)" without flagging it; §7 omits it | Bounded (fires after the other cases' checks are recorded; ruling face unaffected). Reviewer executed b2 on both arms — expectation HOLDS. Owner: disclose as harness defect #6/#5-list + attach my b2 output |
| F2 | LOW | Quote "receipt may never silently claim zero downloads" attributed inside `source_preparation.py:129-133,171-184` parenthetical; the sentence is `tests/test_source_preparation.py:187-189` (ENV-11 docstring) | Correct attribution at landing; mechanism citations themselves verified |
| F3 | LOW | decision.md §4/§5 runtimes ≠ raw pytest times (wall-clock vs in-run); `commands.json` agrees with raw | Align wording at landing; no outcome impact |
| F4 | INFO | Disclosed defects §7 items 3/4/5 have prose disclosure without preserved raw artifacts | Acknowledged; superseding runs carry recorded results |

## 10. Unverified / not re-executed (honest carry-forward)

- **Live S1 `downloads==1` E2E check**: not re-run (network forbidden by card) — offline
  equivalence stands (my §3 recompute + my a6 GREEN flip + frozen live evidence pins).
  Live S1 re-run = **owner re-authorize after landing**.
- **Full CW CLI subprocess ensure face**: not run offline end-to-end; judged harness drives
  `SourceAcquisitionService.ensure` → writer → journal → envelope directly (card-sanctioned
  unit-harness truth); E2E runner covers the chain on no-download paths (S2/S3/S5/S6 green).
- **RF/FF end-to-end receipt for a `downloads==1` envelope**: covered transitively
  (RF ENV-09 `:162-173` events=1 → download_calls=1; FF READ-10 families) — not by a live chain.
- **CW 23-family / RF 11 / FF 116**: re-verified from raw evidence alone; I re-executed just the
  two mandated runs ((a)-harness both arms + E2E tests file).
- **b2 as a judged arm**: vacuous in the attempt (F1) — executed by me, not by the attempt.
- **Attempt signature**: stays unsigned here (never self-sign); carriers next, this report is the
  review record.

## 11. Scope if accepted + routing recommendation

- **Fix surface = company-wiki**: one file, `src/company_wiki/source_catalog/canonical_writer.py`,
  delivered as `<ATT>\changes.diff` (byte-verified in §4). RF and FF stay byte-clean by contract
  (D3) — their porcelain at close confirms zero attempt writes.
- **Recommendation (of the two parent routes): CW-native commit by parent**, with an annotation
  in the plan register mapping card `F-EE1-FIX` → `<ATT>` + the CW commit sha. Rationale: the
  defect, both mints, the fix, and its contract tests are CW-internal; a re-cut CW-native
  card would orphan this attempt's frozen oracle/evidence chain and re-litigate already-frozen
  expectations, while a register annotation preserves traceability at zero process cost. The
  re-cut option becomes preferable solely if the register forbids cross-repo mapping notes.
- **After landing**: owner re-authorizes the live S1 re-run (§10); recovery path for the commit
  is `git apply -R <ATT>\changes.diff` (already byte-verified inverse).
- **Attempt → carriers next** with: this report + `.sha256`, F1 disclosure addendum, F2/F3
  wording corrections at landing.

## 12. Signature

- Reviewer: independent review subagent (session `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`)
- Report: `<ATT>\reviewer_report.md` + `reviewer_report.sha256`
- Verdict: **ACCEPT (verified)** per §0; attempt `a20260923-01` remains unsigned (owner/carrier
  countersignature path per plan protocol).
- Signed: 2026-09-23 12:56 +01:00 (11:56 Z).
