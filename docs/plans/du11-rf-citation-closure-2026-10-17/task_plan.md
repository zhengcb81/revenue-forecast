# DU11-RF-CITATION-CLOSURE — task plan

Card: `company-wiki/docs/plans/document-understanding-2026-10-13/parallel/du11-2026-10-17/du11_rf_citation_closure.md`
PLAN_ID: `du11-rf-citation-closure-2026-10-17`
PWF_PLAN_ROOT: `docs/plans` (this worktree)
Base commit: `568fb9256885eb31a0f76d9ead59fd0f98575073`
Branch: `codex/du11-rf-citation-closure`
Worktree: `C:/Users/郑曾波/Projects/revenue-forecast-du11-citation-closure`

## Goal

Reuse the source owner's support/context views so RF keeps citation closure and bounded
coverage diagnostics inside its real claim / parameter / formula dependencies, and stops
promoting questions, table headers, units or footnotes into independent support facts.
Never re-route, re-slice or re-parse an original; never derive new investment conclusions
or parameter values; incomplete reading coverage stays a diagnostic, never a new
prediction permission gate.

## Write whitelist (card §精确写白名单)

- `scripts/source_narrative_context.py`
- `scripts/research/input_evidence.py`
- `scripts/company_wiki_narrative_contracts.py` (only if RF consumption trace/version
  compatibility truly needs it; upstream wire, byte and identity checks stay untouched)
- new pure module `scripts/narrative_citation_context.py`
- new `tests/test_du11_narrative_citation_*.py`
- new `tests/fixtures/du11_narrative_citation/`
- this PWF dir `docs/plans/du11-rf-citation-closure-2026-10-17/**`

Everything else is read-only. No forecast/model formula, research target, release gate,
install dir, existing golden rewrite, CWP/FF/ET code. Existing tests are acceptance,
never rewritten to make a change pass.

## Phases

### Phase A — investigation and real-behaviour RED
**Status:** complete

- [x] Confirm baseline / main-repo WIP untouched; worktree + branch from the fixed commit.
- [x] CodeGraph structural query on the initialised RF index; record the index gap.
- [x] Locate both real parameter-binding entry points and their call chains.
- [x] Determine how format/claim validators carry the new trace (avoid a second validator).
- [x] RED on a legal public bundle through `validate_narrative_response` → real consume:
      consumed claim forms but context closure and coverage diagnostics are lost.
- [x] Independent hand calculation counterexamples: question span as management fact,
      first-view-wins on several legal views, table row losing its unit/header/footnote.
- [x] Freeze the optional view-selection field, trace schema, error codes and the
      compatibility matrix in `INTERFACES.md`.

### Phase B — shared root-cause implementation and central regression
**Status:** complete

- [x] One pure view/context closure adapter (`scripts/narrative_citation_context.py`)
      used by both entry points; no second authoritative copy of parameter/formula/source state.
- [x] Cover: legacy legal single span without `reading_context`; `reading/1`;
      `reading/2` Q/A both directions and explicit wrong attribution; table row +
      unit/header/footnote; several groups under one parent; ambiguous view;
      missing/duplicate/cross support-context ID; foreign parent / source SHA;
      projected v3 `source_locator`/`pointer`; unread/opaque/deferred and sampling
      counts/`limited`; empty binding / `not_consumed`; unique context choice tied to the
      real formula dependency.
- [x] Unread material is not a refusal condition; real binding errors are named refusals;
      no extra original read and no LLM call.
- [x] Parameter/formula/prediction values provably unchanged on identical input.
- [x] Central regression: new card tests + `test_source_preparation_complete_result`,
      `test_architecture_dependency_uses`, `test_w04_public_consumer`,
      `test_citation_attribution_narrative_contract`,
      `test_shared_reading_narrative_contract`, `test_source_clock`,
      `test_evidence_input_lineage`, `test_input_semantics_e2e`,
      `test_narrative_source_preparation_transport/e2e`,
      `test_company_wiki_narrative_reader`, plus ruff/mypy gates and
      `python tools/pre_push_gate.py` (the repository's own CI gate).

### Phase C — isolated E2E and delivery
**Status:** complete

- [x] Independent temporary tree: real RF public reader → byte verification → consume →
      existing input validation / public calculation entry, with a frozen legal public
      bundle and a local fake reader *only* at the public CWP process boundary.
- [x] `narrative_source_preparation.py` read CLI run; exported context still complete.
- [x] Same old input: prediction values unchanged and the new trace semantics correct.
- [x] Negative controls: bad bytes/SHA, wrong parent/as-of, source unavailable, read timeout.
      No extra download, parse or model call.
- [x] Real hierarchy recorded; no fake source described as real company quality acceptance.
- [x] Restore receipts (sentinel / manifest / bytes / mtime / cleanup) executed, including
      deletion of the owned root and of the owned pytest basetemp.

### Phase D — independent final quality review and handoff
**Status:** in_progress

- [x] Freeze the source commit; hand the complete diff to an independent reviewer agent.
- [x] Round 1: **FAIL** — 1 blocking (free-form `layout_coverage.complete` became a hard
      refusal, i.e. a coverage gate), 6 should-fix (groups-only ambiguity gate and stale
      matrix; three legacy entry-2 error texts; stale RED receipt; owned root not deleted;
      loose projected parent match; stale PWF/handoff). Report:
      `receipts/D-reviewer-1.md`.
- [x] Fix every finding at its shared root cause (coverage parsing is now lenient by
      construction; groups-only determinism; exact legacy messages; projected parent
      identity; RED regenerated against the frozen tests; owned root + basetemp deletion
      receipted; PWF reconciled) and re-run the card + regression suites and all gates.
- [x] Round 2: **FAIL** — 0 blocking, 1 new should-fix (a valid `unread.counts` plus one
      unreadable page/unit list raised a raw `TypeError` instead of `null`, a regression in
      the B1 leniency fix), 2 doc nits. Report: `receipts/D-reviewer-2.md`. Round-1 findings
      B1/S1–S6 all verified FIXED.
- [x] Fix R2-1 (availability `None` keeps the counts unknown) and the two doc nits; add an
      8-case regression over the four unread lists; re-run the suites and gates.
- [ ] Round 3: the same reviewer re-checks the final source SHA; 0 unresolved issues.
- [ ] Only then write COMPLETE + `handoff.json`; author-branch commits only, no merge, no
      push, no cleanup of this worktree; STOP.

## Decisions

| # | Decision | Why |
|---|----------|-----|
| D1 | New trace is a separate versioned object `revenue-narrative-citation-trace/1`; receipt `schema_version` (`revenue-narrative-consumption/1`, `/3`) is unchanged | Card: new context/coverage info goes in a versioned consumption receipt / independent trace object; old wire and old field compatibility preserved |
| D2 | Optional binding fields are `citation_group_id` (str) and `citation_view` (0-based int); no other new fields | Card: explicit optional selection field, frozen by A; a named ambiguity error is used when absent |
| D3 | Ambiguous legal views are a **named refusal**, never first-match | Card: no silent first element |
| D4 | A span that is only `context` in every legal view is refused as support evidence | Card: context must not be promoted to support |
| D5 | `source_role` in `{analyst, investor_question}` is refused as support for an RF parameter claim | Card: question span must not become a management fact; same rule in both entries |
| D6 | Reading coverage (unread / opaque / deferred / sampling / layout) is diagnostic only | Card: coverage shortfall must not become a prediction permission gate |
| D7 | Entry 2 keeps its own formal source+capture derivation; only the pure closure logic is shared | Card: do not copy a second authoritative source/parameter state |
| D8 | Entry 2 on `revenue-narrative-context/3` resolves the real span parent/pointer but ends in a named source-clock refusal (no publication fact on the projected wire) | Honest: `narrative-ref/3` + `narrative-read-receipt/3` carry no publication/availability fact; upstream interface need recorded for ROOT instead of inventing one |
| D9 | `consume_narrative_input`'s signature stays unchanged; no test-only reader seam is added | Card: do not invent a second CLI/transport/manager. The Phase C fake reader sits behind the existing published CWP module path on `PYTHONPATH`, so the real transport and validator still run |
| D10 | Coverage parsing is lenient by construction: only groups/views (the support-vs-context decision) are strict; every coverage value degrades to `null` | Review round 1 blocking finding: a free-form `layout_coverage.complete` had become a coverage gate, which the card forbids. The fix is structural, not a special case |
| D11 | For a groups-only (`reading/1`) read, a span in several groups consumes with the published-first group recorded; `citation_group_id` can name another | Groups carry no support/context semantics, so this is not a silent semantic pick; refusing would be a new gate the baseline did not have (review S1) |
| D12 | A projected `/3` span must match its parent on both `source_id` and `parent_content_sha256` (and its `projection_id` on the subject) | Review S5: a re-signed span must not borrow another original, the same identity the wire validator enforces |

## Errors encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| `git worktree add` reported exit code 1 although the checkout finished | 1 | Verified `rev-parse HEAD` / branch / clean status; exit code was the progress-writer stderr, not a checkout failure |
| CodeGraph `query` returns `[]` for every narrative symbol | 1 | Recorded the index gap (246 indexed files, `scripts/`/`tests/`/`tools/` empty); used the located source files instead of rebuilding an index (card forbids creating/altering it) |
| Independent review round 1: free-form `layout_coverage.complete` refused a legal wire | 1 | Structural fix: groups/views strict, every coverage value lenient `null`; validated-wire regression added |
| Review round 1: groups-only span in two groups became a new gate | 1 | Deterministic published-first group recorded; matrix row updated; regression added |
| Review round 1: three legacy entry-2 error texts changed | 1 | Old `require` pair and exact texts restored on the non-projected path; text-lock regression added |
| Review round 1: committed RED was stale vs the frozen tests | 1 | Regenerated against byte-exact baseline consumers in an outside scratch tree: 27 failed / 10 passed, all behavioural |
| Review round 1: E2E left its owned root and the handoff deletion claim was unreceipted | 1 | Fixture now deletes the owned root (`root_removed: true`); basetemp deletion is receipted |
| Review round 1: projected parent matched only the content SHA | 1 | Parent identity is now `source_id` + `parent_content_sha256` + subject `projection_id`; cross-parent regression added |
| Review round 1: PWF/handoff were stale or premature | 1 | Phases, decisions, matrix, receipts and handoff reconciled; status kept `IMPLEMENTED_REVIEW_PENDING` until the final round |
| Review round 2: `unread.counts` compared against a `None` availability | 1 | Availability `None` keeps the counts unknown; 8-case regression added |
| `Expand-Archive` of a `git archive` of the whole repo failed on long `.planning` paths | 1 | Abandoned the whole-repo archive; built the RED scratch tree from `scripts/` + `tests/` + the frozen wire plus the two baseline consumer files |

## Next Step

Reviewer round 2 re-checks the new frozen source SHA; if 0 unresolved, write COMPLETE and
`handoff.json`, commit only the card whitelist on the author branch, and STOP.
