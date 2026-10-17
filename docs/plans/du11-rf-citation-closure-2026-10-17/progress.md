# DU11-RF-CITATION-CLOSURE — progress log

## Session 1 — 2026-10-17

### Baseline / isolation

- Main repo HEAD = main = origin/main = `568fb9256885eb31a0f76d9ead59fd0f98575073`;
  main-repo WIP (`assurance/runs/*`, untracked `output/`) only observed.
- Created this worktree on the fixed commit:
  `git worktree add -b codex/du11-rf-citation-closure C:/Users/郑曾波/Projects/revenue-forecast-du11-citation-closure 568fb925`
  → clean status, branch `codex/du11-rf-citation-closure`.
- (The command reported exit code 1 from the git progress writer; `rev-parse HEAD`,
  branch name and a clean `status --porcelain` were verified afterwards.)

### Node A — investigation and RED

- CodeGraph on the initialised main repo: 246 indexed files, `scripts`/`tests`/`tools` empty,
  every narrative symbol query returns `[]`. Gap recorded; index not rebuilt (card forbids it).
- Located both real entry points (`consume_narrative_input`, `bind_parameter_evidence`) and
  their callers; established that `_reading_context` already validates `/1` and `/2` but both
  consumers drop the closure and the coverage diagnostics.
- New synthetic legal wire for the card: `tests/fixtures/du11_narrative_citation/synthetic_reading2.json`
  + `tests/test_du11_narrative_citation_wire.py` (built from the descriptor, validated by the
  real `validate_narrative_response`; `/2`, `/1` and no-reading variants).
- RED (18 failures, saved to `receipts/A-red-baseline.txt`):
  `KeyError: 'citation_trace'` (closure/coverage lost), `DID NOT RAISE` for a context-only
  table header, a question span used as a management fact and two legal views taken silently,
  and the projected-wire parent refusal. No assertion checked for a source string.
- Froze `INTERFACES.md` (selection fields, trace schema, error codes, compatibility matrix).

### Node B — implementation

- New pure module `scripts/narrative_citation_context.py`: `reading_trace`, `resolve_span`,
  `citation_dependency`, `citation_trace`, `selection`, `trace_status`,
  `NarrativeCitationError` (codes in `INTERFACES.md` §3). No IO/clock/network/model; only the
  invariants it consumes are re-checked, the wire contract stays with
  `company_wiki_narrative_contracts`.
- `scripts/source_narrative_context.py`: keeps every old receipt key/value and the exact old
  binding-field message, resolves each span through the shared adapter, adds `citation_trace`.
- `scripts/research/input_evidence.py`: `_bind_narrative_span` now resolves the same closure,
  resolves the real parent/pointer for `/3`, and returns `citation_trace`; the four existing
  result keys are unchanged.
- Card tests: `tests/test_du11_narrative_citation_context.py` (pure adapter, 18 cases),
  `..._consumption.py` (both entries, 18 cases), `..._projection.py` (projected `/3`, 4 cases),
  `..._e2e.py` (isolated E2E, 6 cases).

### Test evidence (authoritative commands)

| command | result |
|---------|--------|
| `python -m pytest -q tests/test_du11_narrative_citation_*.py` (5 modules, 74 cases: 5/32/26/5/6) | all passed; see `receipts/B-final-tests.json` |
| card 12-module central regression command | 279 passed, 3 skipped |
| authoritative 20-module run (`--basetemp` in an owned temp dir, `DU11_PWF_RECEIPTS` set) | **374 passed, 4 skipped**, exit 0, 85.79 s (`receipts/B-final-tests.log`) |
| `python -m ruff check scripts tests tools` | all checks passed |
| `python -m mypy scripts/contracts/ scripts/schema_compatibility.py scripts/filing_fetch_client.py scripts/trust_anchor.py` | success, 11 files |
| `python tools/pre_push_gate.py` (the repo's own CI gate: ruff + mypy + 30 smoke modules) | GREEN — `416 passed, 36 subtests passed`, exit 0 (`receipts/C-prepush-gate.txt`) |

### Node C — isolated E2E

- Fake layer is only the CWP reader module path on `PYTHONPATH`; the RF reader still starts a
  real bounded child process and validates its bytes. Frozen public wire: `actual-090`
  (synthetic `Acme business update`, no company original bytes).
- Positive: reader → validated context → consume → `revenue_forecast.py` CLI twice
  (baseline vs linked) → identical `consolidated_forecast`/`segments`, new claim present,
  trace `group_only` with the wire's real unread/deferred/layout diagnostics.
- `narrative_source_preparation.py --company-wiki-catalog-config` read CLI exports the same
  complete `reading_context`.
- Negative controls: bad bytes (`artifact_bytes_mismatch`), unavailable provider, reader
  timeout, wrong as-of (`receipt_request_mismatch`), foreign parent (`does not bind to the
  input source capture`), stale as-of input. Offline guard hard-fails any socket/urlopen.
- Restore receipts: every E2E test starts from an owned root with a sentinel + pre-existing
  output entry, records SHA/mtime, and asserts the byte-identical start state after cleanup.

### Node D — independent review

- Round 1 (independent agent, not the author): **FAIL** — 1 blocking (a free-form
  `layout_coverage.complete` on a wire-valid context became a hard refusal, i.e. exactly the
  forbidden coverage gate), 6 should-fix (groups-only ambiguity gate + stale matrix; three
  legacy entry-2 error texts; stale RED receipt; owned E2E root not deleted; projected parent
  matched only the content SHA; stale/premature PWF). Report: `receipts/D-reviewer-1.md`.
- Fixes at the shared root cause: coverage parsing is lenient by construction; groups-only is
  deterministic; the legacy message pair and texts are restored and locked by a test;
  projected parent identity is `source_id` + `parent_content_sha256` + subject `projection_id`;
  the E2E deletes its owned root and the basetemp deletion is receipted; the RED was
  regenerated against byte-exact baseline consumers (27 failed / 10 passed, all behavioural);
  the PWF and handoff were reconciled and the status kept `IMPLEMENTED_REVIEW_PENDING`.
- Author round-1 commit: `1ada02e4`; round-1 fixes: `1ae6c3b5`.
- Round 2 (same agent): 0 blocking, 1 new should-fix (a valid `unread.counts` plus one
  unreadable page/unit list raised a raw `TypeError` instead of `null` — a regression in the
  B1 leniency fix), 2 doc nits; every round-1 finding verified FIXED
  (`receipts/D-reviewer-2.md`). Fixed: availability `None` keeps the counts unknown, 8-case
  regression over the four unread lists, the error-code table re-joined, the case count
  corrected. Round-2 fixes are committed as the third implementation commit and re-reviewed
  by the same agent against the final SHAs.

### Errors encountered (session)

| Error | Attempt | Resolution |
|-------|---------|------------|
| `git worktree add` exit 1 while the checkout succeeded | 1 | Verified HEAD/branch/clean tree; progress-writer stderr, not a failure |
| CodeGraph returns `[]` for all narrative symbols | 1 | Recorded the index gap, read the files instead of rebuilding the index |
| Test helpers indexed a `NarrativeContext` object | 1 | Added an `as_value()` helper accepting both the object and its dict |
| `section_heading` reported `context_only` although it is in no group | 1 | Real bug: `ungrouped` must be resolved before the context-only branch |
| `_projected` treated every `source_locator` as a projected binding | 1 | Made projection explicit on `revenue-narrative-context/3`; `/1` HTML spans keep `projected: null` |
| `--reader-executable` needs a real executable on Windows | 1 | Dropped that test-only seam and the `reader_command` parameter; the E2E now stubs the published CWP module path on `PYTHONPATH` |
| E2E teardown left created directories | 1 | Snapshot records files; teardown now reaps empty test-created directories bottom-up |
| Review round 1: coverage value refused a legal wire (blocking) | 1 | Lenient coverage parsing + validated-wire regression |
| Review round 1: `/1` two-group gate, legacy texts, stale RED, owned root, loose parent, stale PWF | 1 each | Fixed at the shared root cause; see `findings.md` §10 |
| `Expand-Archive` of a whole-repo `git archive` failed on long `.planning` paths | 1 | Built the RED scratch tree from `scripts/` + `tests/` + the frozen wire plus the two byte-exact baseline consumer files |
