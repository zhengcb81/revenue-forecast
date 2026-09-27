# DECISION — CW-GATE-UNBLOCK-2 / a20260923-01 (LIVING DOC — framework landed first, filled per run)

## 0. Predecessor-death disclosure

`CW-GATE-UNBLOCK/a20260923-01` died mid-work of a **subagent infrastructure failure (NOT a
process violation)**. Frozen at: RC-1 gate encoding fix DONE (`06-gate-crash-GREEN.log`),
archive split DONE (19→≤6, `15-ratchet-GREEN.log`), observability 27→6 DONE
(`24-CC-observability-AFTER.log`, family `23==26` unchanged), prompt_injection 17→15 DONE
(`24-CC-prompt_injection-AFTER.log`), prune refactor PARTIAL — its dying analysis flagged
F821 `absent`/`deleted`; diagnosed from its artifacts
(`24-ruff-three.log`: `prune_retired_evidence.py:605` `absent`, `:630` `deleted`;
`24-CC-prune-AFTER.log` FILE-MAX 17; `20-ratchet-ALL-violations-GREEN.log` prune 17>12).
Predecessor attempt preserved READ-ONLY; its `%TEMP%\cwgu1\repo` iso treated as frozen and
copied (identity-verified) to `%TEMP%\cwgu2\repo` where all continuation work happens.

## 1. PR4 completion story (RC-2d) ✅ DONE

Diagnosis (from predecessor artifacts + source): the CW original defines `deleted = 0`
(orig. line 461) and builds local `absent` (orig. 468-482) before its inline batch loop
(504-534) and its `_plan_todo` helper (549). Predecessor's PR1-PR3 extracted
`_resolve_active_plan` / `_base_report` / `_verify_plan_states` / `_delete_batches`
(verbatim bodies) but left the ORIGINAL loop duplicated in main — whose references to
`absent`/`deleted` were then orphaned (their definitions moved into
`_verify_plan_states`/`_delete_batches`) → F821 ×2 (iso lines 605/630) and main stuck at
17>12. **PR4 = replace the duplicated loop with the `_delete_batches` call**
(`deleted = _delete_batches(config, active_plan, states, already_absent, receipt_file…)`),
eliminating both F821s by construction (the correct names are the helper's parameters /
return). Zero behavior change: same `todo` construction (`_plan_todo(..., already_absent)`
≡ original `absent` content), same per-batch transaction/re-verify/delete/receipt-write
order, same `PruneReport` fields (`deleted_rows`, `receipt_path`, `already_absent`).
Result: `prune_retired_evidence` 17→9, FILE-MAX 12 (`_build_plan`) ≤ frozen 12;
ruff clean; compile clean; ratchet 2 passed; all-rows scan 0 violations
(evidence `11-prune-F821-inherited-RED`, `12-prune-CC-AFTER-PR4`, `13-ratchet-ALL-AFTER-PR4`,
`14-ratchet-GREEN-AFTER-PR4`). Mutation: merged `_delete_batches` split back inline →
main 17 → ratchet RED `17 exceeds frozen 12` (`15-MUT-prune-CC`, `15b-MUT-prune-ratchet-RED`);
restored → 2 passed (`15c`); restored-file sha `CE35EAB4…` = pinned after-sha.

## 2. Full enumeration table — RC-2 4-row family (FINAL numbers)

| row | file | hot fn BEFORE | frozen | BEFORE max | AFTER max | RED | GREEN | MUTATION | family unchanged |
|---|---|---|---|---|---|---|---|---|---|
| RC-2a | archive_retired_evidence.py | `archive_retired_evidence` 19 | 7 | 19 | **6** (`_write_snapshot`) | inherited (`03`/`20`-series) | `16c-MUT-archive-restore-GREEN` (ratchet 2 passed + own family 4 passed) | inline `_write_snapshot` → main 10 → RED `10 exceeds frozen 7` (`16`/`16b`) → restore GREEN | ✅ |
| RC-2b | observability.py | `_redact_assignments` 27 | 6 | 27 | **6** | inherited `20-ratchet-ALL` (27>6) + `21b` provenance (introduced ac4ebd0-era; hot at HEAD) | `23c-MUT-obs-restore-GREEN` (2 passed) + `24-CC-observability-AFTER` (predecessor) | merge `_find_closing_quote` into `_value_span` → 8 → RED `8 exceeds frozen 6` (`23`/`23b`) → restore GREEN | ✅ `23==26` families |
| RC-2c | prompt_injection.py | `record_prompt_injection_review` 17 (hot `_disposal_gate` decomposition, 5d72529-introduced) | 15 | 17 | **15** | inherited `20-ratchet-ALL` (17>15) + `22-CC-prompt_injection-f39bd5a/HEAD` provenance | `24c-MUT-pi-restore-GREEN` (2 passed) + guard unit 17 + fc906a family green | merge `_parse_metadata` into writer → 19 → RED `19 exceeds frozen 15` (`24`/`24b`) → restore GREEN | ✅ GUARD-MERGE face: zero semantics change (tests stay green) |
| RC-2d | prune_retired_evidence.py | `prune_retired_evidence` 27 (+`_load_verified_archives` 16, ac4ebd0-introduced) | 12 | 27 | **12** (main 9; `_build_plan` 12) | inherited `20-ratchet-ALL` (27>12) + `20-GREEN-full` (17>12) + F821 inherited-RED `11` | `12-CC-AFTER-PR4`, `13-ALL-AFTER-PR4` (0 violations), `14-GREEN` (2 passed) | merge `_delete_batches` back inline → 17 → RED `17 exceeds frozen 12` (`15`/`15b`) → restore GREEN (`15c`) | ✅ `23==26` (3 prune-face fails were the `now=` test-face, lane 3, now GREEN `22`) |

Frozen table sha `BCD01361…` before == after (no row value touched; splits do not
need table edits; downward re-record NOT needed and NOT performed).

## 3. Per-file justification groups (13-15 changed files)

### Group RC-1 (gate)
| file | justification | status |
|---|---|---|
| `tools/pre_push_gate.py` | encoding-safe tail print (utf-8/errors=replace) so non-GBK step output cannot crash the gate on GBK consoles; rc propagation unchanged (repro exit == child rc == 3) | ✅ predecessor GREEN (re-verify) |

### Group RC-2a–d (product splits — pure code motion, zero behavior change)
| file | justification | status |
|---|---|---|
| `src/.../archive_retired_evidence.py` | split 19-complexity monolith into ≤7 helpers (predecessor reached ≤6) | ⏳ re-verify+mutation |
| `src/.../observability.py` | split `_redact_assignments` 27 → helpers, max 6 | ⏳ re-verify+mutation |
| `src/.../prompt_injection.py` | split hot `_disposal_gate`/writer decomposition, max 15; GUARD-MERGE face — zero semantics change | ⏳ re-verify+mutation |
| `src/.../prune_retired_evidence.py` | complete PR4 batch-loop replacement + F821 fix; max ≤12 | 🔄 |

### Group TEST-faces (test-only adaptations to new contracts; zero product edits)

Provenance: 8 of the 9 faces were adapted by the PREDECESSOR in its iso (its RED
raws `08a–f`/`08-stale6`, worker GREEN `17` — reused); the prune face is adapted
by THIS attempt (fresh RED `20`, GREEN `22`). Per-lane RED/GREEN/MUTATION is
completed by this attempt's batch mutation cycle (`25`–`25e`: all 9 faces
reverted to their CW stale originals → per-file RED, restored → per-file GREEN;
backup shas `25`, restore verification `25d`).

| file | justification (what the new contract demands) | status |
|---|---|---|
| `tests/contract/test_fc906a_producer_binding_metadata.py` | GUARD-MERGE P5-a (5d72529): `evidence_payload` mandatory, `evidence_sha256` must hash those bytes (fixture supplies the content_sha256 string as payload — byte-identical receipt otherwise) | adapted (predecessor) + verified |
| `tests/contract/test_source_catalog_archive_retired.py` | D2/D3 (ac4ebd0): `now=` injected; snapshot name is the unique-token regex `retired-evidence-[0-9a-f]{16}.jsonl.gz`, not the legacy fixed name | adapted (predecessor) + verified |
| `tests/contract/test_source_catalog_prune_retired.py` | D1/D3 (ac4ebd0): `now=` injected AND bare dated dirs authorise nothing — fixtures plant a REAL verified archive through the writer; `oldest_archive` is the full snapshot path (legacy `"2026-05-01"` day-name pin preserved as a path substring) | adapted (THIS attempt) |
| `tests/contract/test_fc905_receipt_envelope.py` | P5-a payload binding + P5-c dual source/policy binding; P5-b disposal row direct-planted (`cryptography` is not a CI dependency — host-assumption class F-B01-9 avoided) | adapted (predecessor) + verified |
| `tests/contract/test_gp003_llm_exit_receipt_privacy_gate.py` | same P5-a/P5-c writer-contract face | adapted (predecessor) + verified |
| `tests/contract/test_r4b05_metadata_provenance.py` | same P5-a/P5-c writer-contract face | adapted (predecessor) + verified |
| `tests/contract/test_source_catalog_focus_admission.py` | same P5-a/P5-c writer-contract face | adapted (predecessor) + verified |
| `tests/contract/test_source_catalog_worker.py` | same P5-a/P5-c writer-contract face (predecessor GREEN `17` reused) | adapted (predecessor) + verified |
| `tests/contract/test_zr1003_shadow_assertions.py` | P5-a/P5-c: `"e"*64` has no sha256 preimage — hash derives from the benign payload | adapted (predecessor) + verified |

### Group COVERAGE (test-only, one vehicle)
| file | justification | status |
|---|---|---|
| NEW `tests/contract/test_archive_retired_evidence_fail_closed.py` | cover archive file's NEW exception paths to ≥95 (frozen floor unchanged) — 12 tests, sha `90443A6B7AC568DF97ABA675568F5B86FC94ECD76015EF9B2F91C8E9707CA12C` | ✅ DONE (before 85.38 → after 100.0, judged PASS) |

## 4. Coverage lane numbers (metric = the coverage ratchet's own: round(100·(covered_lines+covered_branches)/(num_statements+num_branches),1); floor 95 FROZEN — untouched)

| measurement | command scope | archive entry | combined | raw |
|---|---|---|---|---|
| BEFORE (frozen anchor, predecessor) | archive family + `--cov-branch` | 127/141 lines, 19/30 branches | **85.38% → reported 85.4%** | predecessor `16b` |
| BEFORE-A (reproduced this attempt) | archive family + `--cov-branch` | 127/141, 19/30 | **85.38%** (exact reproduction) | `30` |
| BEFORE-B (CI-equivalent `pytest tests/`, 2894 items) | full suite, before new tests | 127/141, 19/30 (identical missing map) | **85.38%** | `33b`/`35` |
| AFTER-A (family-union) | archive+prune+new fail-closed tests | 141/141, 30/30 (missing=[] both) | **100.0%** | `32` |
| AFTER-B (CI-equivalent `pytest tests/`, 2906 items) | full suite — JUDGED source | 141/141, 30/30 (missing=[] both) | **100.0%** | `34`/`35` |
| **95-floor judgment** | `FC1204_COVERAGE_GATE=1 pytest test_fc1204_coverage_ratchet.py` on AFTER-B's fresh coverage.json | **PASS**: `test_tier1_critical_chain_at_95` PASSED (1 passed); archive absent from `test_tier2_and_frozen_do_not_regress` problems | 100.0 ≥ 95 (frozen, untouched) | `36` |

New tests = exactly one coverage vehicle: NEW file `tests/contract/test_archive_retired_evidence_fail_closed.py`
(12 tests over the refactored file's NEW exception arms: `_publish` exists/race/link-fallback,
`_verify_snapshot` blank-line/duplicate-id, `_validate_now`, `_snapshot_paths` collision,
`_write_snapshot` progress, `_reconcile`, `_verify_then_publish` digest mismatch, `finally`
temp-residue cleanup, `ArchiveReport.to_dict`) — all 25 previously-missing units
(14 lines + 11 branch arcs) covered (family-union measured 141/141+30/30). No threshold
change; 95 stays 95; no self-lowering anywhere.

## 5. Gate full-run + CI prediction table

### Gate status table — `tools/pre_push_gate.py` FULL default invocation (iso final tree, raw `50-gate-fullrun.log`)

| # | step | command | rc | result |
|---|---|---|---|---|
| 1 | ruff (CI WU-1.2 full scope) | `ruff check src tests/unit tests/contract scripts` | 0 | ✅ GREEN |
| 2 | compileall | `python -m compileall -q src scripts tests` | 0 | ✅ GREEN |
| 3 | config_doctor (CI WU-7.1) | `python scripts/config_doctor.py` | 0 | ✅ GREEN |
| 4 | FC-1204 complexity ratchet (CI meta-gate) | `pytest tests/contract/test_fc1204_complexity_ratchet.py -q` | 0 | ✅ GREEN (2 passed) |
| 5 | host assumption guard (FC-1307-a) | `python scripts/host_assumption_guard.py` | 0 | ✅ GREEN |
| 6 | contract tests + meta gates | `pytest -q --timeout=180 <6 files>` | 0 | ✅ GREEN (99 passed) |
| — | WHOLE GATE | `python tools/pre_push_gate.py` | **0** | ✅ **pre-push gate GREEN** (RC-1 fix in place throughout; rc propagation intact) |
| + | unique test symbols (CI WU-1.1, extra check) | `python tools/check_unique_test_symbols.py` | 0 | ✅ GREEN (new `test_fcw_*` symbols clean) |

### CI prediction — `.github/workflows/ci.yml` (read in full; 4 jobs, `test` matrixed 3.11/3.12/3.13)

| step (job `test`) | command | prediction | basis |
|---|---|---|---|
| Ruff lint (WU-1.2) | `ruff check src tests/unit tests/contract scripts` | **PASS** | every changed/new file ruff-verified (`12b`, `24-ruff-three`'s F821s fixed by PR4; new test file clean — gate step 1 re-verifies) |
| Strict type check (FC-1204-c) | mypy on 11 named modules | **PASS** | none of the 11 named modules is among my 15 files (artifact_handle/source_bundle/runtime_policy/activation/close_gap/policy_2x/canary_registry/normalized_meta/flags/policy/restore) — untouched |
| Compileall + config doctor (WU-7.1) | `compileall -q src scripts tests` + `config_doctor.py` | **PASS** | compile verified post-PR4 (`12c`); doctor passed on identical iso inputs (predecessor `05-baseline-step3` + root config files now copied — `26`) |
| Unit tests | `pytest tests/unit -q --tb=short` | **PASS** | predecessor `19-unit-FULL` 799 passed; the two unit faces UNTOUCHED (shas pinned); my product diffs are code-motion/behavior-neutral (families green) |
| Contract tests | `pytest tests/contract` (minus 8 CI-ignored) | **PASS** (measured subset hard; remainder inferential) | all 9 adapted faces + archive/prune families + ratchet + new file measured GREEN here (97/97 batch + per-file runs); the remaining ~190 contract files touch none of my 5 product diffs' behavior (pure code motion + gate print) — predecessor's full-contract run was truncated mid-run by its infra death (`18-*` stops at 28%), so that part is a reasoned prediction, not a measurement |
| Branch coverage ratchet (FC-1204-a) | `pytest tests/ --cov=src/.../source_catalog --cov-branch --cov-report=json \|\| true` then `FC1204_COVERAGE_GATE=1 pytest tests/contract/test_fc1204_coverage_ratchet.py` | **archive floor 95: PASS (measured 100.0, judged `36`)**; **`test_tier2_and_frozen_do_not_regress`: FAIL-ING on 3 modules (NEW finding, §7.5)** | measurement step is `\|\| true` (failure-tolerant); the gate step as a whole is predicted **RED in CI** on `observability.py 65.7<91 / prompt_injection.py 48.4<73 / prune_retired_evidence.py 77.8<87` — attribution diagnostic `37` (CW-original modules, same suite) decides pre-existing (ac4ebd0/5d72529 code growth vs 2026-08-12-frozen floors) vs split-caused; STOP-and-report per standing rule — no self-lowering, no unauthorized test additions |
| Unique test symbols gate (WU-1.1) | `python tools/check_unique_test_symbols.py` | **PASS** | new test symbols are `test_fcw_*`-prefixed (repo-unique by construction); tool run recorded in the gate window |
| Plan claim verifier (WU-8.3) | `python tools/verify_plan_claims.py --plan-dir .` | **PASS** | no planning-claim files touched |
| Mutation canaries (WU-7.1) | 6 canary test files (artifact_handle/source_bundle/download_authorization/gap_plan/fail_closed/determinism) | **PASS** | canary files untouched; the modules they mutate-test are untouched by my diffs |
| (coverage step collects `tests/acceptance` `tests/e2e` `tests/integration` too — the "e2e" lane) | within the `\|\| true` coverage run | **failure-tolerant by design** | those 5 files may fail in a targeted iso (missing heavy fixtures); CI's step cannot fail on them; not part of any judged lane here |

| other jobs | prediction | basis |
|---|---|---|
| `cli-smoke` | **PASS** | scripts untouched |
| `secret-scan` | **PASS** | no sk-/tvly- patterns in any changed file |
| `markdown-lint` | **PASS** | no planning root files touched by the diff |

Residual risks recorded (not blockers): (a) the ~190 unmeasured contract files (basis
above); (b) obs/pi/prune module-level coverage floors (91/73/87 frozen) — code-motion
neutral by construction but not re-measured per-module before this card's mandate; the
judged coverage run's gate output covers them empirically in §4's raw.

## 6. Readings recorded (frozen-table rule)

- Table updates are only ever sanctioned DOWNWARD after a deliberate split; NOT needed
  here (all AFTER max ≤ frozen values). Raising any frozen value is forbidden. The frozen
  table file sha `BCD01361…` is unchanged before==after.
- Coverage floor 95 for `archive_retired_evidence.py` unchanged; coverage restored by
  ADDING tests only.

## 7. NEW-blocker log (different species → stop-and-report)

No NEW blocker of the mandate's species. Harness incidents recorded (resolved, not blockers):
1. `--cov-data-file` unsupported in this pytest-cov → first AFTER-B invocation died at
   argument parsing (never ran); redone with `COVERAGE_FILE` env isolation (same
   semantics). A gate-judgment attempt against the stale root coverage.json is VOID and
   preserved as `36a-VOID-…` for transparency.
2. iso-fidelity: tracked root `config.yaml`/`config_rules.yaml`/`config_template.json`
   were missing from the targeted iso copy → one worker test failed on `config.yaml`;
   fixed by copying the tracked files (`26`/`26b`) — no product/test edit.
3. `git apply` under host `core.autocrlf=true` smudges EOLs — content-identity proven
   after LF normalization (15/15); repo-stored bytes unaffected (text filter).
4. Pre-existing test debt OBSERVED in untouched files during the full-suite runs
   (`test_cw1_source_contract_receipt`, `test_cw_228_receipt`, `test_fixture_packaging`,
   `test_cold_start`, `test_pdf_*`, `test_fc906b` one case, …) — identical failure sets
   before/after my diff (BEFORE-B vs AFTER-B comparison) → not introduced by this card;
   out of scope (no product behavior change in the diff); reported as CI-prediction basis.

### 7.5 NEW FINDING — different species, STOP-AND-REPORT (standing rule)

The judged coverage run (`36`) shows `test_tier2_and_frozen_do_not_regress` RED on
exactly three modules — the three ac4ebd0/5d72529-era modules:

| module | measured (CI-equiv full) | frozen floor | delta |
|---|---|---|---|
| observability.py | 65.7% | 91% (FROZEN) | −25.3 |
| prompt_injection.py | 48.4% | 73% (TIER2) | −24.6 |
| prune_retired_evidence.py | 77.8% | 87% (FROZEN) | −9.2 |

Not this card's coverage mandate (scoped to `archive_retired_evidence.py` — which JUDGED
PASS at 100.0% ≥ 95). Candidate causes: (a) the FC-1204 splits' new wrapper lines/arcs,
(b) PRE-EXISTING floor staleness — the floors froze 2026-08-12, while ac4ebd0 (DW15-REPAIR
rewrote prune wholesale + added redaction machinery to observability) and 5d72529
(GUARD-MERGE added the ed25519 disposal-gate machinery to prompt_injection — arms that
are UNTESTABLE on this host because `cryptography` is not a declared CI dependency, per
fc905's documented host-assumption reasoning) grew those modules with uncovered arms.
Attribution diagnostic `37`: identical CI-equivalent full run with the three modules
replaced by their PRISTINE CW versions (same suite, same flags) — if those measure the
same ≈65.7/48.4/77.8 → cause (b) pre-existing at CW HEAD (my splits neutral); if they
measure ≥ floors → cause (a) my splits → in-scope follow-up (tests only) needed.

Per the standing rule: STOP-and-report; NO self-lowering of any floor; NO unauthorized
test additions to those modules; the parent decides the follow-up card.

---

## 8. CLOSE-OUT APPENDIX (appended after §7.5; §0–§7.5 above are NOT modified — erratum/append only)

Full text, tables and raw pointers: **`final_report.md`** (same attempt dir). Summary:

### 8.1 §7.5 attribution — RESOLVED by the mandated BEFORE-B / AFTER-B dual judgment
- Same criteria, same command (`FC1204_COVERAGE_GATE=1 python -m pytest -q tests/contract/test_fc1204_coverage_ratchet.py`),
  same pytest 9.1.1/3.13.9, one common rootdir (byte-identical writable copy of the iso, `45`,
  678 files hash-identical, 0 diffs — the session sandbox denies writes to `%TEMP%\cwgu2\repo`).
- **Control arm AFTER-B (`39a`) reproduces `36` exactly** (tier1 PASSED; same 3 rows red) ⇒ the
  copy/rootdir change is immaterial.
- **BEFORE-B (`39b`)**: rc=1, tier1 PASSED, **the same 3 rows RED with the same values**
  (65.7 / 48.4 / 77.8) + `archive_retired_evidence.py 85.4 < 95` (the row this card fixes).
- Per-module raw in both arms are **identical** (`40`): obs 232/353, pi 123/254, prune 316/406;
  only archive moves 146/171 → 171/171.
- ⇒ **归因先在 (data source = CI-equivalent full-suite run surface), per TRIAGE family-C
  precedent; the 12 new tests are excluded as a cause (measured).**
- Split hypothesis bounded out with raw arithmetic (`40`): pristine denominators 344/252/395,
  upper bounds `C_split/T_pristine` = **67.4 / 48.8 / 80.0 %**, all < floor−0.5 (91/73/87);
  split deltas only +9/+2/+14 net units vs gaps −25.3/−24.6/−9.2 pts.
- **UNVERIFIED:** direct pristine-module re-measurement (the `37` diagnostic) not obtained —
  `37` died on a coverage `sqldata` INTERNALERROR in the previous session, and this session
  cannot run a CI-equivalent suite at all (pytest tmp machinery sandbox-blocked, `49`).

### 8.2 Fix decision — NO tests added, NO threshold/floor touched
(1) the card's own rule (BEFORE-B same-red ⇒ do not add tests, register family debt);
(2) §7.5's standing rule = no unauthorized test additions to those modules (owner decision);
(3) no test could even be executed here (`49`). `changes.diff` unchanged (sha `100B1920…`,
66 831 B); ratchet table `BCD01361…` / coverage-ratchet file `FA000120…` unchanged;
95 / 91 / 73 / 87 all recorded as measured — **zero self-lowering**.

### 8.3 CI-equivalent dual runs — both COMPLETE (`51`)
`33b` 631 418 B / 2894 items / `62 failed, 2822 passed, 10 skipped, 1117.38s`;
`34` 624 448 B / 2906 items / `63 failed, 2833 passed, 10 skipped, 1110.03s`;
the killed attempt `33` (27 418 B, no footer) stays **VOID**. Delta +12 items = the 12 new
tests; +1 failure = `test_zr409…test_c2_journey_dayu_only_real_sample` (fingerprint race,
isolated re-run green ×2, `46`), 0 failures in this card's own 10 test files (`52`).

### 8.4 The three close-out deliverables
`final_report.md` §D: (D.1) 15-file final table (before/after sha256 + bytes, `47`);
(D.2) 4-row final values = archive **100.0 ≥ 95** GREEN, obs **65.7 < 91**, pi **48.4 < 73**,
prune **77.8 < 87** (three rows = pre-existing family debt, data source = run surface);
(D.3) CI prediction table updated from measurements (`50`/`33b`/`34`/`51`/`52`/`53`) —
only the coverage gate's tier-2/frozen assertion is predicted RED, inherited not card-caused.

### 8.5 Disclosures
Sandbox denial recorded, not worked around: iso `%TEMP%\cwgu2\repo` not writable from this
session (swap attempt kept as VOID `38`), and pytest tmp dirs unusable (`49`); both full-suite
runs therefore predate this session. Zero production writes, zero git mutations, zero network.
