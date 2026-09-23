# F-EE1-FIX 决策记录（decision）— a20260923-01

## 1. Root cause — two-end trace (line-cited, both ends independently verified)

**Defect (FC-704-class)**: after a committed download the envelope reported
`outcome=reused_existing` + `download_events=0`; FF's response `downloads=0`
(`s1_fetch1_stdout.txt`: `"downloads": 0` after a 2 043 710 B committed download,
`status=capture_ready`, `calls=3`) — a documented-contract-violating false zero,
replicated ×2 by E2E-EXPAND and confirmed by reviewer `de849e1a…`
(REMEDIATION_REGISTER §57).

`request_id` is **not** a random correlation token: it is the deterministic SHA-256 of the
request's identity dict — `CW src/company_wiki/source_catalog/resolver.py:625-629`
(`"urn:company-wiki:source-request:sha256:" + _json_hash(identity_dict())`, identity =
resolver.py:608-623; contract: `CW tests/contract/test_source_catalog_resolver.py:333-361`
"deterministic and action-independent"). Two DIFFERENT request objects therefore hash
differently — and the ensure flow mints the journal row and the returned resolution from
two different request objects:

### End E1 — journal row mint (the CALLER's original request)
- `CW …/acquisition_service.py:94` — `common = {"request_id": request.request_id, …}`,
  recorded for the import path at `acquisition_service.py:180-185`
  (`outcome="downloaded_new"`). Evidence row: `journal_rows.json` request_id
  `urn:company-wiki:source-request:sha256:e8177b37…d53ecb`.

### End E2 — resolution mint (a synthesized post-write "exact" request)
- `CW …/canonical_writer.py:194-207` builds `exact_request`, filling
  `form_type/fiscal_year/fiscal_period/language` from the downloaded candidate and
  `provider/provider_document_id` from the candidate (and dropping `mode`);
- `canonical_writer.py:208` resolves with it; `_result` stamps
  `request_id=request.request_id` of THAT exact request (`resolver.py:1993-2010`);
- `canonical_writer.py:222` returns it as `CanonicalImportResult.resolution` — while the
  SAME result already claims the ORIGINAL id at `canonical_writer.py:217`
  (`request_id=request.request_id`) and the provenance sidecar records the ORIGINAL id at
  `canonical_writer.py:348,374`. The inconsistency is intra-object.
- `acquisition_service.py:190` surfaces it as `SourceEnsureResult.resolution`;
  `CW …/cli.py:812-819` builds the FC-704 envelope from it against the journal.
- Evidence: `envelope.json`/`s1_fetch1_stdout.txt` handle request_id
  `…47c3a925…e993`.

### Skip → false zero
- `CW …/resolver.py:1021-1029`: `for attempt in journal.read_all(): if
  attempt.request_id != resolution.request_id: continue` ⇒ the `downloaded_new` row is
  skipped; outcome stays the structural `_STRUCTURAL_OUTCOME[REUSED_EXACT] =
  "reused_existing"` (`resolver.py:754-760, 1018`); `download_events` stays `0`
  (`resolver.py:1021`).

### Propagation (contract violated downstream)
- FF READ-10 `scripts/fetch_filing.py:663-666` ("`stats["downloads"]` … 0 unless a download
  actually committed") + `_record_download_events:622-629` + `fetch_filing.py:880`
  (handle request_id := resolution request_id);
- RF ENV-11 mechanism: `scripts/source_preparation.py:129-133,171-184` (receipt
  `download_calls := envelope.download_events`). **[F2 landing fix — attribution only]** The
  quoted contract sentence "receipt may never silently claim zero downloads" is
  `tests/test_source_preparation.py:187-189` (ENV-11 test **docstring**; ENV-11 test at
  `:186-197`), NOT `scripts/source_preparation.py` (carrier spot-checked live at landing).
  原文留痕 — original pre-fix line retained verbatim: "RF ENV-11
  `scripts/source_preparation.py:129-133,171-184` (receipt `download_calls :=
  envelope.download_events`; \"receipt may never silently claim zero downloads\")." Mechanism
  citations `:129-133,171-184` are unchanged and were verified by the reviewer; the same
  pre-run wording sits in `oracle.md` §1 (Propagation) and is deliberately left
  byte-untouched — the oracle self-declares "never edited after any run" and the reviewer's
  §1 frozen-first W-time proof depends on it; correction of record = this line + review.md +
  evidence/F-EE1-FIX/qualification.json.

### Executable proof of BOTH mints (offline, product's own hash code)
`evidence/two_end/two_end_mints.json` — `verify_evidence_hashes.py` reconstructs the two
identities from the frozen evidence and recomputes with the real `SourceRequest`:
- E1 original identity → `…e8177b37…` **match** (journal row);
- E2 exact identity → `…47c3a925…` **match** (resolution/handle);
- divergence fields: `fiscal_period, form_type, language, provider,
  provider_document_id` (all candidate-filled; `mode` dropped by exact_request but None in
  both for schema 1.1).
`both_ends_proven=true`.

## 2. Fix direction (evidence-first)

Candidate directions considered:

| # | Direction | Verdict |
|---|---|---|
| D1 | **Re-key the returned resolution to the caller's request at the mint** (`canonical_writer.import_staged`, IMPORTED_NEW branch): keep the exact resolve as the write-gate, return `replace(exact_resolution, request_id=request.request_id)` | **CHOSEN** |
| D2 | Resolver-side stable-key matching (document_id+target+source) in `resolver.py:1021-1029` | Rejected |
| D3 | Consumer-side compensation in FF/RF (re-read journal, recompute counts) | Rejected (contract-forbidden) |

**Why D1 is consistent with the existing contracts:**
1. **FC-704's own spec** (`resolver.py:976-983`): "Journal entry for `request_id` wins (the
   real outcome, e.g. **downloaded_new after an ensure**)". The design *intends* the ensure
   envelope to pick up the `downloaded_new` row — i.e. the two ids are *supposed* to match
   after an ensure. The defect violated that intent; D1 restores it. The skip logic itself
   (strict equality) stays as-is — after D1 it is correct by construction.
2. **Every sibling path already keys to the ORIGINAL request**: the dedup branch
   (`canonical_writer.py:157` resolves with `request`), `close_gap._finalize`
   (`close_gap.py:460` resolves with `request`; journal keyed `binding.request_id` =
   original, `close_gap.py:430,446`), the read-only resolve face (`cli.py:1170-1177`), the
   provenance sidecar (`canonical_writer.py:348,374`) and `CanonicalImportResult.request_id`
   (`canonical_writer.py:217`). Only the IMPORTED_NEW branch returned an id that disagreed
   with the operation it belongs to. D1 makes the branch consistent with all of them; D2 or
   a second journal key would have had to special-case every face.
3. **Minimal + fail-closed + no no-download behavior change**: one expression in the one
   divergent branch. The REUSED paths, the dedup path, the read-only path, close-gap, and
   all no-download states are untouched — proven by cases (b)/(d) green in BOTH arms and by
   the 23-test CW contract family green in BOTH arms (pristine and fixed).
4. **Handle/status selection unchanged**: `status`, `matches`, `reason` are the verified
   exact resolution's (the write-gate's own output) — only the *answering request identity*
   is corrected. FF's exactly-one-match requirement (`fetch_filing.py:865-871`) therefore
   behaves identically. A "re-resolve with the original request" variant was considered and
   rejected as strictly more behavior change (it could select a different handle).
5. **D2 (stable-key matching) rejected**: journal-wins is a *per-request* contract
   (append-only rows keyed by request); matching on document/target/source would attach
   `downloaded_new` rows to unrelated requests that happen to resolve to the same document,
   widening who claims a download they did not perform — the opposite direction of the
   honesty rule, and a larger change to frozen reconciliation logic.
6. **D3 rejected by contract**: FF READ-10 forwards envelope evidence verbatim ("no
   independent re-derivation of download evidence", `test_fetch_filing.py:285-288`) and RF
   FC-904/ENV-11 forbid receipt re-derivation (`source_preparation.py:134-138`). Consumers
   may not fix producer evidence.

The ruling-face offered by the card ("the two IDs must MATCH after a committed download,
OR resolver must match on a stable key") — D1 implements the first (matching) option.

## 3. Touched set (minimal) + file list before/after sha

| file (iso copy) | live sha256 (before == after) | iso pristine sha | iso FIXED sha |
|---|---|---|---|
| `company-wiki/src/company_wiki/source_catalog/canonical_writer.py` | `c23a935852cce71a9f1cc2454337cb714ec185b0823c33ddcc50407b7687c258` | same as live | `4bc653725febcc755e3a01ac48227a6b0799c4c262968356b356f8cb42d3c6bc` |

- Final iso-vs-live manifest: **635 files compared, exactly 1 mismatch**
  (`canonical_writer.py`) — `binding_after.json`.
- Live re-hash of all 22 binding pins after the attempt: **0 changed** —
  `binding_after.json.live_pins_changed_vs_before=0`.
- **RF and FF: ZERO files touched (justified)**: the card guessed the mint might live in
  "RF resolver.py / FF fetch_filing.py" — investigation proved otherwise: RF has no
  `scripts/resolver.py` at all (the cited `resolver.py:1021-1029` is company-wiki's; RF runs
  it via `PYTHONPATH=…;<CW>/src`, E2E-EXPAND oracle line 141), and FF only *forwards* the
  envelope (`fetch_filing.py:622-629, 663-666, 880`) — contract-forbidden to compensate
  (see D3). Both mints live in company-wiki; one file fixed there.
- company-wiki itself treated as a READ-ONLY live source (same discipline as RF/FF): the fix
  exists only in the iso copy + `changes.diff` (42 lines, difflib, touched set only); it is
  NOT landed in the live worktree (see handoff/unmapped).

## 4. Judged case table (oracle cases a–f)

| case | expectation (frozen) | RED (pristine iso) | GREEN (fixed iso) | mutation (fix reverted → restored) |
|---|---|---|---|---|
| (a) committed download truthful | a1..a8 all ok: status imported, 1 fetched journal row keyed to original request, **ids match (a3)**, envelope `downloaded_new` (a4), `download_events=1` (a5), **FF `downloads=1` (a6)**, FF accepts envelope (a7), read-only face reports `downloaded_new`/1 (a8) | **FAIL** — a3 ✗ (`f9f96300…` ≠ `7e4be4ca…`), a4 ✗ `reused_existing`, a5 ✗ 0, a6 ✗ 0 = **fake zero reproduced**; a1,a2,a7,a8 ✓ | **PASS** (8/8) | revert → FAIL (same 4 checks); restore → PASS |
| (b) genuine reuse honest zero | b1 second ensure → `reused_existing`/0/FF downloads 0; b2 fresh seeded catalog resolve → `reused_existing`/0 | PASS (5/5) **[F1 landing annotation: those 5 recorded checks are b1 alone — oracle (b)-b2 never executed in-attempt in ANY of the 4 judged runs (harness FileExistsError, §7 item 7); reviewer executed b2 post-hoc on BOTH arms → b2 expectation HOLDS; attached `evidence/reviewer_b2_execution.json`; original "(5/5)" claim retained, not deleted]** | PASS | revert → PASS; restore → PASS |
| (c) request_id equality after download | journal row == resolution dict id == original request id (3-way, the field FF copies at `:880`) | **FAIL** c1,c2,c4 (c3 ✓: E1 mint itself consistent) | PASS (4/4) | revert → FAIL (c1,c2,c4); restore → PASS |
| (d) retry/second-resolve idempotency | fetch_calls stay 1; one `downloaded_new` row; 2 rows total deterministic; envelope rebuild byte-identical; envelope build writes no journal bytes; second read-only face deterministic `reused_existing`/0 | PASS (8/8) | PASS | revert → PASS; restore → PASS |
| (e) mutation non-vacuity | revert ⇒ (a)/(c) return to fake zero | — | — | **rc: red=1 → restored green=0**, identical failure set to RED |
| (f) contract families | all green | — | see §5 | — |

Harness verdict runtimes: RED 2 243 ms, GREEN 2 263 ms, MUTATION-RED 1 977 ms,
MUTATION-RESTORED 2 263 ms → **8.7 s total ≤ 3 min budget**; zero network (no network code
in path; local adapter writes local bytes); all scratch under `%TEMP%`.
**[F3 landing annotation — §4/§5 runtimes]** these §4 figures are the harness's own in-run
`elapsed_ms` values recorded in the case JSONs (raw); §5's parenthesized regression times
are whole-invocation wall-clock (interpreter startup included), whose raw in-run pytest
counterparts are listed in the §5 annotation below. Annotation only; every number retained.

Artifacts: `evidence/red/cases_red.json`, `evidence/green/cases_green.json`,
`evidence/mutation/cases_mutation_{red,restored_green}.json` (+ stdout captures +
`exit_codes.txt`).

## 5. Regression results (all green, offline, `--basetemp %TEMP%`, `-p no:cacheprovider`, `-B`, `PYTHONDONTWRITEBYTECODE=1`)

| id | surface | result | evidence |
|---|---|---|---|
| f3a | CW own contracts on **pristine** iso (canonical_writer, resolution_envelope_fc704, source_catalog_acquisition) | **23 passed** (9.68 s) rc=0 | `evidence/regression/cw_contract_baseline_pristine.txt` |
| f3b | same 3 files on **fixed** iso | **23 passed** (9.26 s) rc=0 | `evidence/regression/cw_contract_fixed.txt` |
| f1 | RF ENV-11 family `tests/test_source_preparation.py` (CI-faithful `PYTHONPATH=company-wiki/src`, `quality.yml:26`) | **11 passed** (4.7 s) rc=0 | `evidence/regression/rf_env11_family.txt` |
| f2 | FF READ-10 family `tests/test_fetch_filing.py` (includes `:315-318` impossible-count rejection + envelope forwarding) | **116 passed, 1 skipped, 39 subtests** (17.3 s) rc=0 | `evidence/regression/ff_read10_family.txt` |
| f4 | E2E-EXPAND offline runner `S2,S3,S5,S6,S4 --live never`, evidence → this attempt, work → `%TEMP%` | **rc=0**, 5/5 scenarios pass, `live_gate=never`, `production_writes=0`, preflight CODE_PINS drift=`[]` (40.4 s) | `evidence/regression/e2e_runner/{summary,preflight}.json`, `e2e_runner_exit.txt` |
| f5 | E2E-EXPAND tests file `tests/test_cross_repo_chain_e2e.py`, `RF_E2E_LIVE_DOWNLOAD` unset | **2 passed, 1 skipped** (live honest-skip) rc=0 (41.4 s) | `evidence/regression/e2e_tests_file.txt` |

**[F3 landing annotation — wall-clock vs in-run pytest times]** The parenthesized times in
the table above are whole-invocation wall-clock (interpreter startup included); the raw
evidence files record the in-run pytest self-reported times: CW pristine **8.26 s** / CW
fixed **7.79 s** (vs 9.68/9.26 above), RF ENV-11 **3.51 s** (vs 4.7), FF READ-10 **16.10 s**
(vs 17.3), E2E tests file **40.20 s** (vs 41.4). `commands.json` already matches the raw
values (no command record disagrees); f4's 40.4 s already comes from the runner's own exit
artifact (`e2e_runner_exit.txt` = 40 438 ms, raw). No outcome impact; original wall-clock
numbers retained unchanged — annotation only, per reviewer F3 (low/informational).

## 6. Porcelain + re-hash close

- `git status --porcelain` at close (`evidence/porcelain_at_close.txt` + attribution):
  - **filing-fetch: empty** (fully clean).
  - **revenue-forecast**: no modified/deleted tracked file; untracked = my attempt dir
    ` .planning/…/execution_runs/F-EE1-FIX/` (deliverables) + two PRE-EXISTING leftovers
    (`.tmp-r41-mutation/` mtime 2026-09-20, `assurance/…/plan_inputs.json.bak`
    mtime 2026-09-21 — both predate the attempt created 2026-09-23 12:05 local).
  - **company-wiki**: 3 modified files (`CLAUDE.md`, `README.md`,
    `src/…/artifact_dag.py`, all LastWrite 2026-09-23 02:13 local, ~10 h **before** the
    attempt; diff-stat 16 insertions/2 deletions) — **pre-existing, not written by this
    attempt** (I never opened any live file for write).
- Live pins re-hash after close: **22/22 unchanged** (`binding_after.json`).
- Network: zero (no probe, no download; runner `--live never`; CW hermetic conftest active
  for CW pytest runs).
- Git: read-only `git status`/`git diff --stat` only — no git mutations.

## 7. Disclosed defects/deviations of THIS attempt (harness-level, oracle untouched)

1. `evidence/red_pre_harness_fix1/` — first RED attempt failed writing its JSON (d3 recorded
   raw journal `bytes`); harness fixed to record sha256 (equality semantics preserved),
   oracle NOT edited; re-run produced the judged RED. (Same handling as E2E-EXPAND's
   documented harness-fix precedent.)
2. `evidence/regression/rf_env11_family_MISSING_PYTHONPATH_attempt.txt` — first RF family
   invocation omitted CI's `PYTHONPATH=company-wiki/src` → 5 `ModuleNotFoundError` failures
   (environment artifact, not product); CI-faithful re-run: 11/11 passed. Both preserved.
3. First CW contract invocation passed relative test paths with wrong cwd → pytest rc=4
   usage error ("no tests ran"); absolute-path re-run produced the recorded results.
4. A post-hoc `Get-Content | python` pretty-print of the E2E summary failed with
   `Invalid \escape` (console codepage mangling of UTF-8 backslash escapes in the PIPE, not
   the file — the file parses; read-tool verification shown in transcript). The runner's own
   exit artifact `rc=0` + `summary.json` are authoritative.
5. Compile-check first attempt used unexpanded `$TEMP` (tooling slip); re-run `compile ok`.
6. The live S1 E2E `downloads==1` check itself was NOT re-executed (network forbidden by
   the card): case (a)/a6 establishes the same FF-level fact offline through the same writer
   paths + the frozen live evidence pins (see handoff/unproven).
7. **F1 (reviewer-found; disclosed during carrier landing, record fix with history
   retention)**: `run_cases.py:95` `FileExistsError` (`companies.mkdir(parents=True)`, no
   `exist_ok`) via `:377` (`_make_catalog(b2_root)`, after `:362-364` had already created
   `project/companies`) aborted the b2 sub-check in **ALL 4 judged runs**
   (`context.harness_exception` in every case JSON — red, green, mutation_red,
   mutation_restored_green); oracle **(b)-b2 never executed in-attempt**;
   **reviewer executed b2 on BOTH arms** — expectation **HOLDS** (fresh seeded catalog →
   `reused_equivalent`, 0 journal rows, envelope `reused_existing`, `download_events` 0,
   FF `downloads` 0); original §4 "(b) PASS (5/5)" claim annotated to note the b2 gap
   (annotation-only, nothing deleted); reviewer's b2 output attached as
   `evidence/reviewer_b2_execution.json` (clearly labeled reviewer-executed post-hoc
   evidence, source = reviewer report sha256
   `588f8d955f4f06db1fc262aa3a490071604681f4f6a679dcfd65962846ecf652`).
