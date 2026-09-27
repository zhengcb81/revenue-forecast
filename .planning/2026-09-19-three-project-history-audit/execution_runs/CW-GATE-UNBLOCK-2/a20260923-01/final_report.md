# FINAL REPORT — CW-GATE-UNBLOCK-2 / a20260923-01 (CLOSE-OUT, APPENDED)

Appended at close-out of the card's remaining "last gate" work. **No frozen section of
`oracle.md` or `decision.md` was edited** — everything below is new text; §0–§7.5 of
`decision.md` stand as written, and §8 is this card's appended pointer/erratum only.

Discipline attestation for this close-out: production tree read-only, zero git mutations,
zero network, no self-signature (`status=review_pending`, `implementer_signed=false`).

---

## A. Task 1 — coverage ratchet 3-row RED: BEFORE-B / AFTER-B dual judgment (raw)

### A.1 Method (same criteria, same rootdir, same pytest, same command)

- Criterion: `FC1204_COVERAGE_GATE=1 python -m pytest -q tests/contract/test_fc1204_coverage_ratchet.py`
  (identical to `36`; CI's own gate line, ci.yml L64).
- Judge code: unchanged `tests/contract/test_fc1204_coverage_ratchet.py` (sha pinned in
  oracle A.0: `FA0001209BB43BF49E63CA9B9D9463485E6F35B1B8ACCB69D0E7F78DEFE31C85`).
- Interpreter: `C:\Miniconda\python.exe` 3.13.9 / pytest 9.1.1 / cov-7.0.0 (header in both raws).
- The session sandbox denies writes to the card's iso (`%TEMP%\cwgu2\repo`), so both arms ran
  in a **byte-identical copy** of that iso: `45-judgment-iso-copy-identity.log`
  (678 files hash-compared, **0 differences**, caches excluded). Both arms share this one
  rootdir, so the two arms are equal to each other; the control arm (A) below additionally
  proves the copy reproduces `36` exactly.
- Data: `scratch\cov_beforeB.json` sha `8B18503772FF9A88358F68CDEC7AF5B8C072241BBE95C7B56206803E91532CF0`
  (1186762 B) and `scratch\cov_afterB.json` sha `7C966B73ADD6196D1DA331E83F942E6D2D717B3B742D8934C94B736CCC2C21C0`
  (1186681 B) — the two CI-equivalent full-run archives preserved from this card's earlier runs.

### A.2 Results (raw)

| arm | data file | rc | `test_tier1_critical_chain_at_95` | `test_tier2_and_frozen_do_not_regress` problems |
|---|---|---|---|---|
| A = AFTER-B control (re-judges `36`) | cov_afterB.json `7C966B73…` | **1** | PASSED (1 passed) | `observability.py 65.7% < 91% (frozen)`; `prompt_injection.py 48.4% < 73% (frozen)`; `prune_retired_evidence.py 77.8% < 87% (frozen)` |
| B = BEFORE-B | cov_beforeB.json `8B185037…` | **1** | PASSED (1 passed) | **the same three rows, identical values** + `archive_retired_evidence.py 85.4% < 95% (frozen)` |

- `39a-cov-GATE-95-judgment-AFTER-B-control.log` — reproduces `36` **exactly** (same 3 rows,
  same values, tier1 PASS) ⇒ copy/`rootdir` change proven immaterial, the dual comparison is fair.
- `39b-cov-GATE-95-judgment-BEFORE-B.log` — BEFORE-B is RED on the same three rows **with the
  same measured values**, and additionally red on the archive row (the row this card's 12 new
  tests fix).
- `38-VOID-swap-denied-AFTER-B-only.log` — first attempt at arm B was VOID (swap into the iso
  was sandbox-denied; the run therefore judged AFTER-B data again). Kept for transparency, not used.

### A.3 Per-module raw numbers, both arms (`40-cov-3modules-raw-BEFORE-AFTER-plus-bound.log`)

| module | arm | stmts | covered lines | branches | covered branches | combined/total | pct | missing lines | missing branches |
|---|---|---|---|---|---|---|---|---|---|
| observability.py | BEFORE-B | 283 | 198 | 70 | 34 | 232/353 | 65.7 | 85 | 36 |
| observability.py | AFTER-B | 283 | 198 | 70 | 34 | 232/353 | 65.7 | 85 | 36 |
| prompt_injection.py | BEFORE-B | 178 | 94 | 76 | 29 | 123/254 | 48.4 | 84 | 47 |
| prompt_injection.py | AFTER-B | 178 | 94 | 76 | 29 | 123/254 | 48.4 | 84 | 47 |
| prune_retired_evidence.py | BEFORE-B | 310 | 255 | 96 | 61 | 316/406 | 77.8 | 55 | 35 |
| prune_retired_evidence.py | AFTER-B | 310 | 255 | 96 | 61 | 316/406 | 77.8 | 55 | 35 |
| archive_retired_evidence.py | BEFORE-B | 141 | 127 | 30 | 19 | 146/171 | 85.4 | 14 | 11 |
| archive_retired_evidence.py | AFTER-B | 141 | **141** | 30 | **30** | **171/171** | **100.0** | 0 | 0 |

The three red modules are **byte-identical in coverage terms across the two arms**; only the
archive row moves (146/171 → 171/171) — i.e. the 12 new tests touched nothing outside archive.

### A.4 Attribution verdict

1. **Measured (raw):** the three rows are RED under BOTH judgments with identical values ⇒
   the RED is **not caused by this card's 12 new coverage tests**; data source = the
   CI-equivalent full-suite **run surface** (`pytest tests/ --cov … --cov-branch`), i.e.
   **归因先在**, per the TRIAGE family-C precedent (data source = 跑面). Registered as
   family pre-existing debt (see §D.2 for the rows/floors).
2. **Bounded (arithmetic, same raws):** the card's complexity splits cannot be the cause either.
   Static denominators from coverage's own parser (calibrated: parser output == `coverage.json`
   `num_statements`/`num_branches` for every one of the 4 files):

   | module | pristine(CW) stmts/branches | split(iso) stmts/branches | C_split | T_pristine | upper bound `C_split/T_pristine` | floor | bound < floor−0.5? |
   |---|---|---|---|---|---|---|---|
   | observability.py | 272/72 | 283/70 | 232 | 344 | **67.4%** | 91 | YES |
   | prompt_injection.py | 176/76 | 178/76 | 123 | 252 | **48.8%** | 73 | YES |
   | prune_retired_evidence.py | 303/92 | 310/96 | 316 | 395 | **80.0%** | 87 | YES |

   Reading: even granting the pristine module *every* unit the split file executed, its metric
   could not exceed the bound — all three bounds stay below floor−0.5, while the observed gaps
   are −25.3 / −24.6 / −9.2 points against split deltas of only +9 / +2 / +14 net units.
   ⇒ the split is quantitatively excluded as the cause.
3. **UNVERIFIED (stated, not guessed):** a direct re-measurement of the three modules *at
   pristine CW source* under the same suite (the `37` diagnostic) was **not obtained**:
   the original run died on a `coverage sqldata INTERNALERROR` (`37-DIAG-…log`, UTF-16, 416 B),
   and this session cannot execute a CI-equivalent full suite at all — pytest's tmp machinery
   is blocked by the sandbox (raw probes in `49-BLOCKED-pytest-tmp-sandbox.log`). So
   "the same three rows are also red at CW HEAD unmodified" is **未证实**; items 1–2 are the
   measured basis actually in hand.

---

## B. Task 2 — was the fix "add fail-closed exception-path tests"? **NO — no tests added**

Decision: **不补测**, for three independent reasons:

1. The card's own decision rule: BEFORE-B judges the same three rows RED → 归因先在 →
   do not add tests; register the rows as family pre-existing debt with the data source
   disclosed (§D.2). Adding tests would be manufacturing coverage for debt this card did not
   create, while the frozen floors (91/73/87) and the 95 threshold are **untouched** — all
   four rows are recorded below exactly as measured, **zero self-lowering, zero frozen-value
   edits** (ratchet table sha `BCD01361…`, coverage-ratchet file sha `FA000120…` unchanged).
2. Authorisation: standing rule for this card is "no unauthorized test additions to those
   modules" (`decision.md` §7.5) — a follow-up card/owner ruling is required for obs/pi/prune.
3. Feasibility in this session: pytest cannot create usable tmp dirs under the sandbox
   (`49`), so no new test could be executed, i.e. no honest RED/GREEN could be produced here.
   No test file was created or modified; `changes.diff` is byte-identical to the reviewed one.

The one card-authored coverage vehicle (`test_archive_retired_evidence_fail_closed.py`,
12 tests) already lands its row at **100.0% ≥ 95** and is unchanged.

---

## C. Task 3 — CI-equivalent dual runs: both COMPLETE (`51-CI-equiv-dual-run-completeness.log`)

| run | log | bytes | items | footer | verdict |
|---|---|---|---|---|---|
| killed attempt | `33-cov-BEFORE-B-CI-equiv-full.log` | 27 418 | 2894 (partial) | **no footer** | **VOID — not used as an artifact** |
| BEFORE-B | `33b-cov-BEFORE-B-CI-equiv-full.log` | 631 418 | 2894 | `62 failed, 2822 passed, 10 skipped … 1117.38s (0:18:37)` | COMPLETE |
| AFTER-B | `34-cov-AFTER-B-CI-equiv-full.log` | 624 448 | 2906 | `63 failed, 2833 passed, 10 skipped … 1110.03s (0:18:30)` | COMPLETE — judged source |

Delta = +12 items (the 12 new archive tests), +11 passed, **+1 failed** — that single extra
failure is `tests/contract/test_zr409_fourth_root_real_journeys.py::test_c2_journey_dayu_only_real_sample`
(a fingerprint race over the real `dayu_portfolio` root; the test's own comments document
concurrent-writer noise). Isolated re-run **passes twice** (`46-zr409-extra-failure-isolated-rerun.log`);
the 12 new tests write only under pytest `tmp_path` (grep raw in the same log) ⇒ not caused by
this card. Failure-set identity before/after otherwise re-verified at raw level.

---

## D. The three close-out deliverables

### D.1 15-file final table (delivery = `changes.diff`, sha256 `100B19202F551A7B16137CA2A83B5D732FB17490B7802D6C9FC0972D2B04E611`, 66 831 bytes; full detail in `47`)

Full table with before/after sha256 and byte sizes: `evidence/47-final-15-file-shas.log`
(before = CW production tree, READ-ONLY hash; after = card iso).

| # | file | group | before sha256 (first 16) | after sha256 (first 16) | after bytes |
|---|---|---|---|---|---|
| 1 | `src/company_wiki/source_catalog/archive_retired_evidence.py` | RC-2a split | `BBE855E4495E82D2` | `2A236072E0C3CB3C` | 11 847 |
| 2 | `src/company_wiki/source_catalog/observability.py` | RC-2b split | `EDCBECCB9B13778E` | `D398F92176AA91B4` | 45 262 |
| 3 | `src/company_wiki/source_catalog/prompt_injection.py` | RC-2c split | `88154DE4AB763060` | `815691D1EB2B2A89` | 20 638 |
| 4 | `src/company_wiki/source_catalog/prune_retired_evidence.py` | RC-2d split | `0C99BBE0C5F4EF16` | `CE35EAB403F709D2` | 25 723 |
| 5 | `tests/contract/test_archive_retired_evidence_fail_closed.py` | NEW coverage vehicle | (absent) | `90443A6B7AC568DF` | 6 933 |
| 6 | `tests/contract/test_fc905_receipt_envelope.py` | test face | `555D15C1B8474A24` | `429DCA0FCE477419` | 14 745 |
| 7 | `tests/contract/test_fc906a_producer_binding_metadata.py` | test face | `5D1B23FD369551E9` | `5C4E3FCB8F4CE04A` | 12 656 |
| 8 | `tests/contract/test_gp003_llm_exit_receipt_privacy_gate.py` | test face | `6DC6A87885D45930` | `768CF10D102D15C5` | 8 461 |
| 9 | `tests/contract/test_r4b05_metadata_provenance.py` | test face | `BD87715433ECDEF5` | `7FCC2F91D82BF21C` | 37 323 |
| 10 | `tests/contract/test_source_catalog_archive_retired.py` | test face | `0A4195B1CF5493EF` | `CF5D8D1A0C6606E9` | 4 135 |
| 11 | `tests/contract/test_source_catalog_focus_admission.py` | test face | `62F35F780E647800` | `F6A5B932A3A77C75` | 16 141 |
| 12 | `tests/contract/test_source_catalog_prune_retired.py` | test face | `E0727C70414B1555` | `D70EECF3CE70CD6D` | 4 900 |
| 13 | `tests/contract/test_source_catalog_worker.py` | test face | `0993C90E0AFEF8BC` | `970FD40855549B5B` | 62 906 |
| 14 | `tests/contract/test_zr1003_shadow_assertions.py` | test face | `8853FC7157F695E4` | `3185F67630D28356` | 10 420 |
| 15 | `tools/pre_push_gate.py` | RC-1 gate | `28338622CC3BFBD0` | `D3F308B4A63B37D1` | 5 361 |

Counts: **5 product/tool + 9 test faces + 1 NEW coverage test = 15**; all 15 `changed=True`.
Product/tool files outside this allowlist: **0** (content-identity 15/15 in `44`).

### D.2 4-row final values (thresholds untouched; all values measured, none lowered)

| row (file) | floor (frozen) | measured, CI-equivalent AFTER-B | status |
|---|---|---|---|
| `archive_retired_evidence.py` | **95** (threshold, FROZEN — unchanged) | **100.0 %** (171/171; 141/141 lines, 30/30 branches, missing = ∅) | **GREEN** (was 85.4 % before this card's 12 tests) |
| `observability.py` | **91** (frozen) | 65.7 % (232/353) | RED — **pre-existing family debt**, data source = CI-equivalent run surface; identical in BEFORE-B; split bounded out (67.4 % ceiling) |
| `prompt_injection.py` | **73** (tier-2) | 48.4 % (123/254) | RED — same attribution; bound 48.8 % ceiling |
| `prune_retired_evidence.py` | **87** (frozen) | 77.8 % (316/406) | RED — same attribution; bound 80.0 % ceiling |

No floor/threshold/rounding rule was modified; the ratchet/coverage test files are untouched
(oracle A.0 shas hold). Gate step "95-floor judgment" = PASS (`36`, re-reproduced in `39a`).

### D.3 CI prediction table — updated against this card's measurements

Measured columns come from `50-gate-fullrun.log`, `33b`/`34` (+`51`, `52`, `53`).

| CI step (`.github/workflows/ci.yml`) | old prediction (decision.md §5) | **updated prediction** | measured basis |
|---|---|---|---|
| Ruff lint (WU-1.2) | PASS | **PASS** | gate step 1 rc=0 (`50`) |
| Strict type check (mypy 11 named modules) | PASS | PASS (unchanged, not re-measured) | none of the 15 files is in the mypy list |
| compileall + config_doctor | PASS | **PASS** | gate steps 2–3 rc=0 (`50`) |
| Unit tests `pytest tests/unit` | PASS (799 passed, predecessor) | **UNCERTAIN — 1 failure observed** | `tests/unit/test_contradiction_detector.py::test_detect_numeric_contradictions` fails in **both** arms (identical; untouched file); cause not investigated ⇒ pre-existing/host-scope, card-neutral |
| Contract tests `pytest tests/contract` | PASS (measured subset) / remainder inferential | **mostly PASS-predicted** | AFTER-B shows 40 contract failures = **39 iso-copy missing-file artifacts** (17/18 checked paths + the sibling golden corpus **do exist in CW** — `53`) + **1 flaky** (zr409, isolated green ×2 — `46`); **0 of the card's own 10 test files fail** (`52`) |
| Branch-coverage measurement (`… \|\| true`) | failure-tolerant | completes, **archive 100.0 %** | `34`/`35` archive entry 171/171 |
| Coverage gate `FC1204_COVERAGE_GATE=1 …` | tier1 PASS; tier2/frozen **RED on 3 rows** | **RED on the same 3 rows (65.7/48.4/77.8)** — inherited, not card-caused | dual judgment `39a`/`39b` (identical both arms) + bound (§A.4) |
| Unique test symbols (WU-1.1) | PASS | **PASS** | gate extra check rc=0 (`50`) |
| Plan claim verifier (WU-8.3) | PASS | PASS | diff touches no planning-claim file |
| Mutation canaries (WU-7.1) | PASS | PASS | canary modules untouched |
| Whole pre-push gate | rc 0 | **rc 0 measured** | `50`: all 6 steps + whole gate + unique-symbols rc=0 |
| other jobs (cli-smoke / secret-scan / markdown-lint) | PASS | PASS | no scripts/secrets/planning-root files in diff |

Net: the only CI step predicted **RED** for reasons traceable to this area is the coverage
gate's tier-2/frozen assertion, and its three rows are shown to be **pre-existing on the run
surface** (identical before/after) and **arithmetically not explainable by this card's splits**.
Follow-up owner decision required (either a dedicated card adding fail-closed exception-path
tests for obs/pi/prune, or an explicit floor re-freeze ruling) — **no self-lowering performed**.

---

## E. New evidence produced in this close-out (all under `evidence/`)

| log | content |
|---|---|
| `38-VOID-swap-denied-AFTER-B-only.log` | VOID first attempt (sandbox-denied swap), transparently relabelled |
| `39a-cov-GATE-95-judgment-AFTER-B-control.log` | control arm — reproduces `36` exactly |
| `39b-cov-GATE-95-judgment-BEFORE-B.log` | BEFORE-B arm — same 3 rows RED + archive 85.4 |
| `40-cov-3modules-raw-BEFORE-AFTER-plus-bound.log` | per-module raw both arms + static denominators + bound |
| `attr_3modules.py` | the read-only script behind `40` |
| `45-judgment-iso-copy-identity.log` | 678-file hash identity of the writable judgment copy |
| `46-zr409-extra-failure-isolated-rerun.log` | +1 failure explained; isolated re-run green ×2 |
| `47-final-15-file-shas.log` | 15-file before/after sha256 + bytes + changes.diff sha |
| `49-BLOCKED-pytest-tmp-sandbox.log` | why no full-suite/diagnostic run is executable in this session |
| `51-CI-equiv-dual-run-completeness.log` | both CI-equivalent runs complete; killed run void |
| `52-AFTER-B-failure-classification.log` | 63 failures classified; 0 in this card's test files |
| `53-iso-artifacts-exist-in-CW-tree.log` | 17/18 + sibling paths exist in CW ⇒ iso artifacts |
| `classify_afterB_failures.py` | parser behind `52` |

## F. Not done / unverified (stated explicitly)

1. Pristine-module direct re-measurement (`37` diagnostic completion) — **not executed**;
   original crashed (`37`), this session cannot run tmp_path-based suites (`49`).
2. No independent re-run of the dual judgment (self-produced in the writable iso copy).
3. No test additions for obs/pi/prune rows (§B) — parent/owner decision.
4. `zr409` fingerprint race and the 1 `tests/unit` failure — observed, isolated-green /
   uninvestigated respectively; both identical before/after.
5. CI-equivalent full runs were executed in the previous session (different sandbox
   permissions); this session only re-judged their preserved archives.
