# E2E-EXPAND decision.md — attempt a20260923-01 (nine-step protocol → review_pending)

Implementer did NOT self-accept; status = `review_pending`, independent review follows.
Scope delivered: **two new RF files** (`e2e/run_cross_repo_chain_e2e.py`,
`tests/test_cross_repo_chain_e2e.py`) + **one contract edit** (`tests/contract/
host_assumption_allowlist.json`, the host-assumption guard's own sanctioned registration
mechanism — see J-E2) + this attempt directory. CW/FF repos untouched (proven by
pre/post snapshots). Production writes = 0 (production catalog never opened — stat-only).
No git commands anywhere in the registry. Network: S1 only, all invocations recorded
(one disclosed deviation, J-D2).

## 0. Scenario matrix — final results (oracle frozen before the first judged run)

| scenario | result | key evidence |
|---|---|---|
| **S1** real cninfo download → verify → DELETE → verify-gone | **SKIP** in every default/CI run (`live_gate_never`, reason recorded, `network_scope: none`); **FAIL** when authorized (`RF_E2E_LIVE_DOWNLOAD=1`) — see F-EE1 below | R3: `evidence/run_live_pytest/s1/` — 24/25 checks green: probe 200, exit 0, branch B1, real file 2 043 710 B (`c1527297…`), all provenance/sidecar/hash/document_id checks true, spy `provider` events ≥2 (real adapter invoked), journal `downloaded_new`=1, no staged bytes, no operation.lock, teardown `post_absent=true`. The single red check is the frozen contract `s1.downloads: expected 1, got 0` |
| **S2** isolated lake (REAL CW bytes) → FF parse → source_preparation → review-gate refusal | **PASS** ×2 (runner R1b + nested in R2-final) | `evidence/run_offline/s2/` — lake built from `isolated_lake.py` subclass, copy re-hash = `b4f1713d…`/`601349fd…` pins, zero synthetic bytes, receipt removed (production-mirror, recorded `receipt_removal.json`), stageA exit 0 `capture_ready` handle byte_size 2 070 073 / sha `b4f1713d…` / cninfo / pdoc 1222806982 / downloads 0, stageB exit **3** with `error_code=upstream`, message `prompt injection not reviewed … prompt_injection_status=not_reviewed`, explicit-missing-info true, **structured actionable fields absent (F2 observed)**, `catalog_count_delta={}`, raw unchanged |
| **S3** second run: reuse / no re-download / no dup registration / no re-produce | **PASS** ×2 | `evidence/run_offline/s3/` — stageA rerun `downloads==0`; stageB refusal message byte-identical; counters **provider 0, scan 0, producer 0** (wiring.json shows all wraps installed, producer wraps `wrapped`), read recorded, `catalog_count_delta={}`, lake tree byte-identical (volatile sqlite/lock files excluded per I-07-B disclosure; artifacts rows + producer_events rows + derived bytes unchanged) |
| **S4** restore invariants (always last) | **PASS** ×5 (R1b, nested ×2, accidental run, R3) | `evidence/run_offline/s4/` + protocol snapshots — temp storage absent (s1-wiki, s2-lake, work root all gone), CW real files re-hash == pins, production catalog stat-only identical, FF config/scripts/e2e/tests listing diff `{}`, FF config bytes identical, CW storage-top diff `{}`, CW entity listing identical, RF diff: no unexpected new / no changed / no deleted (only the two deliverables, both present in BEFORE) |
| **S5** bad filing id (FY1999 + nonexistent provider id) | **PASS** ×2 | `evidence/run_offline/s5/` — exit **2**, structured `status=not_found`, error names the missing condition, no `handle`, `downloads=0` |
| **S6** company not found | **PASS** ×2 | `evidence/run_offline/s6/` — exit **2**, structured `status=identity_error` (identity stage precedes filing lookup; within the frozen set `{identity_error, not_found}`), honest error, no handle, `downloads=0` |

7 scenarios defined (cap 8) · 1 company (宁德时代/300750) · 2 filings (offline FY2024
2 070 073 B read-only copy + S1 FY2025 download 2 043 710 B, deleted) · total real bytes
touched ≈ 8.2 MB (≤ 50 MB) · runner total 36.2 s offline (≤ 4 min budget) · tests file
82.7 s full, 41.9–84.4 s across runs.

> **Carrier-landing annotations (F-RV-09 / F-RV-10 — numbers kept, basis annotated):**
> `82.7 s` is NOT raw-derivable (raw pytest stdout not preserved; closest raw record =
> final run's nested runner `evidence/run_pytest_offline_nested/summary.json` 73.322 s;
> reviewer's independent re-run = 44.40 s for the identical 2 passed + 1 skipped rc=0) —
> original value retained, qualitative claim (2 passed + 1 skipped, rc=0) re-proven.
> `≈ 8.2 MB` double-counts the 2 filings (unique real bytes = 4.1 MB; 6.2 MB counting the
> accidental J-D2 download too) — original value retained; conservative vs the 50 MB budget.

### Deletion-proof line (the owner's restore rule, asserted by the suite itself)

- Authorized run R3: `evidence/run_live_pytest/s1/deletion_proof.json` →
  `pre_delete_inventory` **15 files**, `deleted_paths` **2** (the downloaded PDF
  `c1527297…` 2 043 710 B + its sidecar `5a02bb27…` 3 214 B, each with pre-delete
  sha256), **`post_absent: true`, `asserted: true`** (whole `<work>/s1-wiki` rmtree
  verified absent; S4 then confirms the work root itself is gone).
  - **F-RV-02 record fix (carrier landing, 原值留痕)**: original line cited R3's sidecar
    pre-delete sha as `e319f62f…` — retained here verbatim: "its sidecar `e319f62f…`
    3 214 B". That digest is the ACCIDENTAL run's sidecar
    (`evidence/accidental_auto_gate_run/s1/deletion_proof.json`, `retrieved_at`
    09:36:12Z); R3's own proof reads
    `5a02bb271cf6a09de23c6baba53c118ea53c4d332f7c9fc10f4b19779a2bfff2`
    (retrieved_at 09:41:43Z). Corrected in place above; PDF `c1527297…` correct in
    both proofs. Evidence files were correct as-is and were NOT touched.
- Disclosed auto-gate run (J-D2): same shape — `evidence/accidental_auto_gate_run/
  s1/deletion_proof.json` (15/2/`post_absent=true`).
- Default/CI runs: no file ever created; proof still written with
  `post_absent=true` (path never existed).

### Restore invariants (S4 + independent protocol cross-check)

- Runner S4: all five groups pass in every run (table above).
- Protocol snapshots `snapshot_before.json` vs `snapshot_after.json` (python, taken
  around ALL runs): **`DIFF_KEYS: []`** — CW real hashes, production catalog
  size+mtime_ns (stat-only, never opened), FF config listing, CW storage top, CW
  entity file listing, RF scripts/e2e/tests + top-level file set: byte-for-byte and
  set-for-set identical.

## 1. CI-safety choice (frozen in oracle §3; justification)

**Choice: offline-by-default tests + auto-run-if-reachable with skip-on-fail in the
standalone runner; skip counts as pass-with-reason (exit 0), never failure, never a
fabricated pass.**

- The **tests file** (the only artifact CI collects): S1 executes **only** under
  `RF_E2E_LIVE_DOWNLOAD=1` (honest `skipif` reason otherwise) and the offline test
  passes `--live never` explicitly (belt and braces — proven by
  `test_live_download_scenario_is_opt_in`, which asserts the nested runner reports
  `live_gate_never` and `network_scope: none`). CI step9 default path: **no network,
  no mock, no live code executed**. Verified: final run `2 passed, 1 skipped, rc=0`.
- The **runner** default (env unset) is *auto*: probe → run if reachable → provider
  failure ⇒ `skip(reason)` recorded in `summary.json`. This matches the card's
  recommendation and is CI-safe because the runner is **not wired into CI** — no new
  job, no workflow edit, no gate change, no baseline addition (不大张旗鼓). Evidence:
  `quality.yml` untouched; the only CI step that runs e2e files is
  `python e2e/run_revenue_forecast_e2e.py` (unchanged).
- step9-surface proof on the final code: `ruff check` rc0 · `compileall` rc0 ·
  `tools/host_assumption_guard.py` rc0 `new=0` · `test_fc1307a` (no-new-host-
  assumptions + rationale + baseline) 3 passed · gate/inventory test subset
  44 passed (2 failures pre-existing, J-C1).

### Env-gate mapping (J-E1)

Card phrasing: “add env gate `RF_E2E_LIVE_DOWNLOAD=1` to FORCE-skip locally”. Implemented
tri-state: **unset = auto**, **`0` = force skip** (no probe, no network), **`1` = force
attempt / opt-in for the tests file**. Rationale: `=1` universally reads as *enable*,
the same card requires `=1`-style opt-in for the tests file's live part, and a boolean
`0` is the natural force-skip value — both readings of the card are honored by the
tri-state and the mapping is documented in oracle §1. Deliberate, recorded here as the
single interpretation call.

## 2. Product findings (measured, NOT fixed — card rule)

- **F-EE1 (new, replicated ×2): committed download reports a false zero.** After a real
  cninfo download (journal row `outcome=downloaded_new`, file+sidecar imported,
  snapshot verified), CW's envelope reconciliation (resolver.py:1025-1029) skips the
  journal row because **`attempt.request_id` (`e8177b37…`) ≠ `resolution.request_id`
  (`47c3a925…`)** → envelope `outcome=reused_existing`, `download_events=0` → FF's
  response `downloads=0`. This violates FF's own documented contract (filing_fetch
  docstring: “`stats['downloads']` … 0 unless a download actually committed”, READ-10)
  and would make `source_preparation`'s `reuse_receipt.download_calls` claim 0 after a
  real download — exactly the fake-zero class FC-704 exists to prevent. Evidence:
  `evidence/run_live_pytest/s1/{journal_rows.json,envelope.json,s1_fetch1_stdout.txt}`;
  in `evidence/accidental_auto_gate_run/s1/` the mismatch SUBSTANCE is present via
  `s1_fetch1_stdout.txt` + `journal_outcomes.json` — the `journal_rows.json` /
  `envelope.json` pair is absent there (F-RV-06 correction). Original wording retained
  (原值留痕): "and the same pair in `evidence/accidental_auto_gate_run/s1/`" — pointer
  imprecision only; the ×2 replication claim is substantively upheld. FF's own live tests
  (test_fc805, test_e2e_download) assert only the journal, never this field, so the
  gap is untested upstream. Consequence for this suite: **S1 fails its frozen
  `downloads==1` check whenever live-authorized**; the restore/deletion half of S1 is
  fully green. Offline/CI path unaffected (opt-in only).
- **F2 re-observed (I-07-B carry)**: the review-gate refusal carries explicit
  missing-info (`prompt_injection_status=not_reviewed`) but **no structured actionable
  recovery fields** — asserted as absent in S2/S3 (observed-not-fixed).
- **F3 re-observed**: no CLI exists to record a prompt-injection review — this is why
  the suite's state construction REMOVES the builder-written receipt to mirror
  production (I-07-B J1 measured production has none); `receipt_removal.json` records
  `receipt_present_before=true → absent_after=true`.
- **F1 re-observed**: the entry cannot recover registration (resolve/ensure never scan)
  — asserted as `documents≥1` from the builder's own real scan + `catalog_delta={}`
  through every entry run.
- **Pre-existing CI-surface reds outside this card's write surface (J-C1), measure-only**:
  (a) `test_fc1307a_the_three_vendored_copies_are_byte_identical` fails on this dev
  machine (RF `tools/host_assumption_guard.py` `9294dc7c…` vs CW/FF copies
  `20c9da56…`; CI skips it — siblings absent there); (b) `test_single_owner_guard`
  fails on `scripts/revenue_core.py` importing subprocess; (c) `tools/tests/
  test_complexity_ratchet.py` red (`analysis/confidence.py` 32>23,
  `model_extensions.py` 27>10) — the ratchet scans `scripts/` only, and my files are
  in `tests/`+`e2e/`. All three were red before this attempt (files untouched); none is
  affected by or caused by the new files.

## 3. Judgment calls

- **J-E2 — allowlist edit is the third RF file.** The literal content-hash pins the
  protocol requires made `tools/host_assumption_guard.py` (run in CI step9 via
  `test_fc1307a`) report 11 new `unregistered-frozen-hash` violations. The guard's own
  remediation text sanctions exactly one route: register genuinely host-independent
  digests with rationale in `tests/contract/host_assumption_allowlist.json`. The
  alternatives were rejected: string-splitting the literals to dodge the AST rule is
  explicitly the “CONCATENATED … outside this gate's reach” evasion the guard warns
  about, and dropping pins would break the binding contract. `changes.diff` contains
  this edit; the registry test (`test_fc1307a_every_registered_digest_carries_a_rationale`)
  passes.
- **J-D2 — disclosed network deviation.** RUN-R2's first execution hit a code bug in
  `test_live_download_scenario_is_opt_in`: it omitted `--live never`, so the runner's
  default **auto** gate probed cninfo and executed one real download outside the
  frozen registry scope. The download itself fully succeeded (evidence preserved at
  `evidence/accidental_auto_gate_run/`,16 files) and first exposed F-EE1. Fixed by
  adding `--live never`; R2b/R2-final prove the no-network default. Effective network
  ledger: 2 probes + **2 real downloads** (1 disclosed accident + 1 authorized R3),
  each with full evidence; both deleted with verified proofs.
- **J1 — company choice: 宁德时代 (CATL), not the card's example biren.** CATL is the
  real company inside FF's own E2E expectations (CN row of
  `expected-biren-e2e-v1-*.json` = stockCode 300750; `test_e2e_download` CN sample with
  FF's determinism note “CATL yields exactly one”), it is the card's first-listed
  option (A-share annual via cninfo), its FY2024 annual is a 2 MB real filing in CW with
  a complete provenance sidecar, and the cninfo adapter path has no dayu Docling/RapidOCR
  conversion wait (5-15 min note in CW's `source_acquisition.yaml`) that would blow the
  ≤4-min budget and force a skip on the card's biren/HK path. 1 company × 2 filings as
  the card froze.
- **J2 — review-gate state construction.** The card freezes “refusal at the review gate
  per I-07-B”. RF's `isolated_lake._preset_v2_artifacts` WRITES a review receipt (its
  own matrix needs the green arm); keeping it would hand-author a review no operator
  can perform (F3). The suite removes the receipt key after build and records
  before/after (`receipt_removal.json`) — constructing the PRODUCTION state, not a
  green one. Measured result matches I-07-B byte-for-byte in message shape.
- **J3 — harness-fix iterations (oracle untouched).** Run1 of R1 failed 4 scenarios on
  two harness defects while the product behaved per oracle: (a) `parse_json_docs`
  parsed only single-line JSON but FF prints indent=2 multi-line stdout; (b) S3's lake
  tree comparison included volatile sqlite/lock files (db/-shm/-wal/
  `operation.lock.acquire`) that read connections legitimately touch (I-07-B disclosed
  the shm advance). Superseded run preserved at `evidence/run_offline.pre_harness_fix1/`.
  No oracle line changed after any run.
- **J4 — attempt venv + dependency copies (no pip, no network).** The per-attempt iso
  venv was copied from I-07-B's template (same python 3.13.9); the real stockinfo-cninfo
  adapter fails to import without `playwright` (`NameError: Page` — measured), so
  playwright/playwright_stealth/greenlet/pyee/typing_extensions/selenium were **copied
  from the local Miniconda site-packages** (file copies only — pip/PyPI would violate
  the network budget). Recorded in commands.json ENV-02. No product file touched.
- **J5 — pwsh `ConvertTo-Json` unusable on this host** (10 strings ≈ 20 s, 100 strings
  timed out): the protocol snapshot was rewritten in Python (`evidence/snapshot.py`);
  both `.ps1` drafts deleted. Also: a UTF-8 `.ps1` without BOM is decoded as GBK by
  this harness — the BOM fix was verified before the switch to Python.
- **J6 — S1 classification table frozen pre-run** (oracle §1): identity/config/request
  errors and any committed-download verification failure = FAIL; unreachable/timeout/
  provider-refused/tool-missing = SKIP with reason; teardown failure = FAIL
  (restore violated). Only the F-EE1 contract check ever triggered the FAIL arm.

## 4. Before/after hashes (measured)

| file | state | sha256 |
|---|---|---|
| `e2e/run_cross_repo_chain_e2e.py` | new deliverable (66 643 B) | `88ac9e4a4d207c02bd8163a0f3bbec743e4d28e8a32443504398637935466648` |
| `tests/test_cross_repo_chain_e2e.py` | new deliverable (7 037 B) | `3e2b39ee10947c386f21833dbf19b135619d015817c3df91757d04ef7bcc9213` |
| `tests/contract/host_assumption_allowlist.json` | edited; before = reconstructed pre-edit text (1 215 B, as read before editing, the difflib input stored in `changes.diff`), after (4 913 B) | before `bc6da8ff80bccd9093b962c5965ea9f8e2a573f43116dc831a33a45118f38424` → after `ff9db8c8cdb11f71230de3c576b7b41e65ebf69594e5ddd52d2f712d2727c219` |
| product pins (binding.json) | unchanged across ALL runs (runner preflight every run + protocol snapshots) | `source_preparation 91a6dc32…`, `fetch_filing 046cc7dc…`, `filing_contracts 2d1b2e33…`, `isolated_lake 867ac82b…`, `isolated_wiki 8966e7e1…`, CW `cli fad88c60…` |
| CW real data | unchanged (S4 + protocol snapshots) | raw `b4f1713d…`, sidecar `601349fd…`, cn.json `d9a4860f…` |
| production catalog | stat-only, unchanged | 49 677 344 768 B / wal 0 B / shm 32 768 B, mtimes identical |

\* the reconstruction is the pre-edit text as read by the implementer before editing
(the difflib input committed in `changes.diff`, sha `bc6da8ff…`, 1 215 B); no git was
available to re-verify the on-disk pre-image (card rule: no git).

## 5. Runtime & budgets

Offline runner total **36.2 s** (S2 14.2 / S3 13.2 / S5 4.1 / S6 3.4 / S4 1.3) ·
tests-file full **82.7 s** (F-RV-09: not raw-derivable — closest raw = nested runner
73.322 s; reviewer re-run 44.40 s, identical outcome) · authorized S1 (probe+download+
verify+delete+proof) **24.0 s**
· all ≤ the ~4-min suite budget. Evidence footprint **149 files / 1.7 MB** (small-scale
 honoured: 1 company, 2 filings, ≤ 8.2 MB real bytes [F-RV-10: double-count basis —
 unique 4.1 MB; 6.2 MB incl. the accidental J-D2 download], no new CI surface).

> **F-RV-03 record fix (carrier landing, 原值留痕):** original text read "Evidence
> footprint **148 files / 1.7 MB**" — retained here as superseded; reviewer's live count
> = **149 files / 1 763 067 B**, and this carrier's own re-count of `evidence/` at landing
> = 149 files / 1 763 067 B (the carrier-added `evidence/E2E-EXPAND/qualification.json`
> postdates that count).

## 6. Unverified / reviewer to attack (honest list)

- The authorized live test (`test_live_download_and_delete_restore`) currently FAILS by
  design-of-measurement (F-EE1). Whether the reviewer accepts S1's FAIL as the correct
  frozen-oracle outcome, or rules the `downloads==1` check was mis-specified against
  current CW behavior, is the central review question — the oracle was not amended
  after the run either way.
- F-EE1 root cause (journal-row request_id construction vs resolution.request_id) is
  observed at the row level but not root-caused in code-path detail (read, not fixed,
  per card).
- Linux CI execution of the offline test was not possible on this Windows host; the
  test file has no host literals (host-assumption guard rc0), paths are pathlib/sibling-
  derived, and the skipped-without-siblings case is honest — but an actual Linux step9
  run is unproven by this attempt.
- HK/dayu (dayu-agent) and US markets are out of the frozen scope (CN/cninfo only);
  no claim about them.
- `test_live_download_scenario_is_opt_in`'s inner assertion set was executed twice
  (R2b, R2-final); the authorized test executed once (R3) — a second authorized
  execution was not run (network budget discipline).
