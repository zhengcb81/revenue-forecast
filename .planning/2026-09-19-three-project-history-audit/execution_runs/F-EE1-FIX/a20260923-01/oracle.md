# F-EE1-FIX 冻结预期（oracle）— a20260923-01

**Written BEFORE the first judged run. This file is never edited after any run.**

Card: F-EE1 (FC-704-class fake download zero) — owner directive「发现的缺陷都要全部修复」。
Ruling-face (already fixed by the card): **after a committed download the journal row's
`request_id` and the resolution's `request_id` MUST MATCH** (or the resolver must match on a
stable key); the false zero (`outcome=reused_existing` + `download_events=0` after a real
committed download ⇒ FF `downloads==0`) must die.

## 0. Scope, budgets, honesty rules (frozen)

- **Fix surface is company-wiki, NOT RF/FF** (investigated first, evidence frozen below): RF
  has no `scripts/resolver.py`; the cited skip logic `resolver.py:1021-1029` lives in
  company-wiki `src/company_wiki/source_catalog/resolver.py:1021-1029` (RF runs it via
  `PYTHONPATH=…;<CW>/src`, E2E-EXPAND oracle line 141). The two request_id mints both live in
  company-wiki (citations §1). RF/FF only PROPAGATE the false zero and must stay byte-clean.
- RF = `C:\Users\郑曾波\Projects\revenue-forecast` (READ-ONLY),
  FF = `C:\Users\郑曾波\Projects\filing-fetch` (READ-ONLY),
  CW = `C:\Users\郑曾波\Projects\company-wiki` (READ-ONLY — same live-source discipline;
  the fix lands only in an iso copy, delivered as `changes.diff`).
- Execution: iso copies under `<ATT>/iso` only; every scratch/lake/basetemp under `%TEMP%`;
  production writes = 0; **network = none, ever** (no live S1 re-run — case (a) is reproduced
  offline through the SAME writer paths = unit-harness truth, explicitly not mock-live);
  **no git mutations** (read-only `git status --porcelain` allowed for the mandated close check).
- Interpreter: `<ATT>/iso/venv/Scripts/python.exe` (copied from E2E-EXPAND's attempt venv,
  I-00-B rule 5 pattern). `PYTHONDONTWRITEBYTECODE=1`, `-B`, `-p no:cacheprovider`,
  `--basetemp %TEMP%\…` for every pytest run.
- Harness (RED → GREEN → mutation) total runtime ≤ 3 min.
- Non-vacuity: RED must reproduce the fake zero on UNMODIFIED iso; mutation (fix reverted)
  must return to the fake zero.

## 1. Frozen two-end citations (the root-ause trace the oracle judges against)

End E1 — **journal row mint** (original caller request identity):
- `CW src/company_wiki/source_catalog/acquisition_service.py:94` —
  `common = {"request_id": request.request_id, …}`; recorded for the import path at
  `acquisition_service.py:180-185` (`outcome="downloaded_new"`).
- Identity hash source: `CW …/resolver.py:625-629` — `request_id = "urn:company-wiki:
  source-request:sha256:" + _json_hash(identity_dict())` (identity_dict = resolver.py:608-623;
  deterministic & action-independent, contract test
  `CW tests/contract/test_source_catalog_resolver.py:333-361`).

End E2 — **resolution mint** (post-write "exact" verification request identity — DIFFERENT
request object ⇒ different hash):
- `CW …/canonical_writer.py:194-207` builds `exact_request` filling
  `form_type/fiscal_year/fiscal_period/language` from the candidate and
  `provider=candidate.provider, provider_document_id=candidate.provider_document_id`
  (and dropping `mode`); `canonical_writer.py:208` resolves with it;
  `resolver.py:1993-2010 _result` stamps `request_id=request.request_id` (the exact_request).
- `canonical_writer.py:222` returns THAT resolution inside `CanonicalImportResult` while the
  SAME result already claims `request_id=request.request_id` (the ORIGINAL) at
  `canonical_writer.py:217` — the intra-object inconsistency. Provenance sidecar also records
  the ORIGINAL id (`canonical_writer.py:348,374`).
- `acquisition_service.py:190` returns `resolution=imported.resolution` (exact-keyed) for the
  `SourceEnsureResult`.

Skip → fake zero:
- `CW …/cli.py:812-819` builds the envelope from `ensured.resolution` against the journal;
- `CW …/resolver.py:1021-1029` — `for attempt in journal.read_all(): if
  attempt.request_id != resolution.request_id: continue` ⇒ the downloaded_new row is skipped;
  outcome stays structural `_STRUCTURAL_OUTCOME[REUSED_EXACT]="reused_existing"`
  (`resolver.py:754-760,1018`), `download_events` stays `0` (`resolver.py:1021`).

Propagation (contract violated):
- FF `scripts/fetch_filing.py:663-666` (READ-10: `stats["downloads"]` = envelope event count,
  "0 unless a download actually committed") + `_record_download_events:622-629` +
  `fetch_filing.py:880` (handle request_id = resolution request_id);
- RF `scripts/source_preparation.py:129-133,171-184` (ENV-11: receipt may never silently
  claim zero downloads — `download_calls := envelope.download_events`).

Evidence pins (E2E-EXPAND `<E2E-ATT>/evidence/run_live_pytest/s1/`):
- `journal_rows.json` → request_id `urn:company-wiki:source-request:sha256:e8177b37…d53ecb`
  (outcome `downloaded_new`, content_sha256 `c1527297…`, provider cninfo / 1225002214);
- `envelope.json` → `outcome=reused_existing`, `download_events=0`,
  `response_downloads_field=0`, `handle_request_id=…47c3a925…e993`;
- `s1_fetch1_stdout.txt` → FF response `status=capture_ready`, `downloads: 0`, `calls: 3`
  after a committed 2 043 710 B download (`deletion_proof.json` sha `c1527297…`);
- `request.json` → the original request identity
  `{schema 1.1, company_query 300750, market CN, annual_report, fiscal_year 2025,
  as_of_date 2026-09-23}` (+ FF identity normalization: entity 宁德时代, security_id 300750).

## 2. Judged cases (frozen expectations)

Harness: `<ATT>/harness/run_cases.py`, run against `<ATT>/iso/cw/src` (iso company-wiki).
It constructs state locally through the SAME production writer paths —
`SourceAcquisitionService.ensure` → `AcquisitionCoordinator.resolve_or_stage` →
`CanonicalSourceWriter.import_staged` → `AcquisitionJournal.record` →
`build_resolution_envelope(…, journal=…)` exactly as `cli.py:789-819` does — in a fresh
`%TEMP%` catalog with a controlled local adapter (controlled inputs; no network; no live claim).

### (a) committed download must be truthful — RED before fix, GREEN after
- a1 `ensured.status == imported` (the download path was taken; adapter fetch_calls == 1);
- a2 journal latest row: `outcome == "downloaded_new"` AND
  `row.request_id == request.request_id` (E1 mint — must hold in BOTH arms);
- a3 `ensured.resolution.request_id == row.request_id` (**the two IDs MATCH** — the ruling face);
- a4 envelope `outcome == "downloaded_new"`;
- a5 envelope `download_events == 1` (≥1);
- a6 FF `_record_download_events(stats, {"resolution_envelope": envelope.to_dict()})`
  ⇒ `stats["downloads"] == 1` (READ-10 truth; equivalence of E2E-EXPAND's frozen S1
  `downloads==1` check — S1 itself is live-only and NOT re-run: network forbidden);
- a7 FF `validate_resolution_envelope(envelope.to_dict())` accepts the envelope
  (`downloaded_new` ∈ taxonomy, `fetch_filing … filing_contracts.py:235-246`) — no consumer break;
- a8 **read-only resolve face, right after ensure#1** (the `cli.py:1188` shape, journal already
  holding the one `downloaded_new` row): envelope `outcome == "downloaded_new"` and
  `download_events == 1` — GREEN in BOTH arms: this face keys the resolution on the original
  request (never broken), proving the defect is exactly the ensure face's swapped resolution
  identity, not the journal/envelope machinery.

RED (unmodified iso) expectation: a3..a7 FAIL with the fake zero
(`reused_existing` / `download_events=0` / `downloads=0`, resolution id ≠ journal id);
a1/a2 pass ⇒ the RED is the fake zero itself, not a broken harness.

### (b) genuine reuse must stay an honest zero — GREEN in BOTH arms (no fabrication)
- b1 second `ensure` of the same request (document now present): status `reused`,
  latest journal row `reused_before_download`, envelope
  `outcome == "reused_existing"` and `download_events == 0` ⇒ `downloads == 0`;
- b2 fresh catalog seeded by scan only (no journal download row) + read-only
  `SourceResolver.resolve` envelope: `outcome == "reused_existing"`, `download_events == 0`.

### (c) request_id equality after a committed download — RED before, GREEN after
Same join as a3, additionally asserted on the envelope-facing resolution dict the FF handle
copies (`fetch_filing.py:880`): `resolution["request_id"] == journal_row["request_id"]
== request.request_id`, all three equal.

### (d) retry / second-resolve idempotency not broken — GREEN in BOTH arms
- d1 after ensure#2: `adapter.fetch_calls == 1` still; journal `downloaded_new` rows == 1;
  journal total rows == 2 (append-only, deterministic);
- d2 `build_resolution_envelope` twice on the same resolution ⇒ byte-identical `to_dict()`;
- d3 read-only resolve envelope (the `cli.py:1188` shape) succeeds and
  **building the envelope does not write the journal** (FC-704 zero-write, CW
  `tests/contract/test_resolution_envelope_fc704.py:238-249` semantics).

### (e) mutation (non-vacuity) — judged
Revert the iso fix ⇒ re-run ⇒ (a)/(c) return to the fake zero (RED again); re-apply ⇒ GREEN.
A mutation that stays green invalidates the fix (non-vacuous RED required).

### (f) contract families stay green — regression (post-fix unless noted; no network, %TEMP% basetemp)
- f3a **CW own contracts at RED baseline** (pristine iso): `tests/contract/
  test_source_catalog_canonical_writer.py`, `test_resolution_envelope_fc704.py`,
  `test_source_catalog_acquisition.py` — must already be green (fix introduces no drift);
- f3b same three files against the FIXED iso — green (fix changes no existing contract);
- f1 RF `tests/test_source_preparation.py` (ENV-09..12 incl. **ENV-11** at :159-197 region)
  in the RF worktree (read-only execution, `--basetemp %TEMP%…`);
- f2 FF `tests/test_fetch_filing.py` (READ-10 at :315-318 + envelope forwarding) in the FF
  worktree (read-only execution, `--basetemp %TEMP%…`);
- f4 E2E-EXPAND offline runner:
  `RF e2e/run_cross_repo_chain_e2e.py --scenarios S2,S3,S5,S6,S4 --live never
  --work-root %TEMP%\f-ee1-e2e-work --evidence-dir <ATT>/evidence/regression/e2e_runner`
  ⇒ exit 0, every scenario pass, production_writes 0 (preflight CODE_PINS must match live —
  they will: live sources untouched);
- f5 E2E-EXPAND tests file `RF tests/test_cross_repo_chain_e2e.py` with default env
  (`RF_E2E_LIVE_DOWNLOAD` unset) ⇒ `2 passed + 1 skipped` (live test honest-skip), rc=0,
  all scratch under `--basetemp %TEMP%…`.

## 3. Honesty rules (frozen)

- No network at any point; the CW hermetic conftest (socket block) backs the pytest runs.
- No mocks used to claim a live outcome: case (a) is a unit-harness construction through the
  same writer functions (explicitly sanctioned by the card), and the historical live proof is
  the frozen E2E-EXPAND evidence pinned in §1 — both must tell the same story.
- Live sources RF/FF/CW stay byte-clean: verified by `git status --porcelain` + re-hash of the
  pinned files at close (before == after).
- Skips are recorded with reasons; a failed preflight (pin drift) ⇒ do not run, rebind first.
