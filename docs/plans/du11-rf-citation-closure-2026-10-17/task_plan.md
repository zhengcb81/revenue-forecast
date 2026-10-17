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
**Status:** in_progress

- [x] Confirm baseline / main-repo WIP untouched; worktree + branch from the fixed commit.
- [x] CodeGraph structural query on the initialised RF index; record the index gap.
- [x] Locate both real parameter-binding entry points and their call chains.
- [ ] Determine how format/claim validators carry the new trace (avoid a second validator).
- [ ] RED on a legal public bundle through `validate_narrative_response` → real consume:
      consumed claim forms but context closure and coverage diagnostics are lost.
- [ ] Independent hand calculation counterexamples: question span as management fact,
      first-view-wins on several legal views, table row losing its unit/header/footnote.
- [ ] Freeze the optional view-selection field, trace schema, error codes and the
      compatibility matrix in `INTERFACES.md`.

### Phase B — shared root-cause implementation and central regression
**Status:** pending

- [ ] One pure view/context closure adapter (`scripts/narrative_citation_context.py`)
      used by both entry points; no second authoritative copy of parameter/formula/source state.
- [ ] Cover: legacy legal single span without `reading_context`; `reading/1`;
      `reading/2` Q/A both directions and explicit wrong attribution; table row +
      unit/header/footnote; several groups under one parent; ambiguous view;
      missing/duplicate/cross support-context ID; foreign parent / source SHA;
      projected v3 `source_locator`/`pointer`; unread/opaque/deferred and sampling
      counts/`limited`; empty binding / `not_consumed`; unique context choice tied to the
      real formula dependency.
- [ ] Unread material is not a refusal condition; real binding errors are named refusals;
      no extra original read and no LLM call.
- [ ] Parameter/formula/prediction values provably unchanged on identical input.
- [ ] Central regression: new card tests + `test_source_preparation_complete_result`,
      `test_architecture_dependency_uses`, `test_w04_public_consumer`,
      `test_citation_attribution_narrative_contract`,
      `test_shared_reading_narrative_contract`, `test_source_clock`,
      `test_evidence_input_lineage`, `test_input_semantics_e2e`,
      `test_narrative_source_preparation_transport/e2e`,
      `test_company_wiki_narrative_reader`, plus ruff/mypy gates.

### Phase C — isolated E2E and delivery
**Status:** pending

- [ ] Independent temporary tree: real RF public reader → byte verification → consume →
      existing input validation / public calculation entry, with a frozen legal public
      bundle and a local fake reader *only* at the public CWP process boundary.
- [ ] `narrative_source_preparation.py` read CLI run; exported context still complete.
- [ ] Same old input: prediction values unchanged and the new trace semantics correct.
- [ ] Negative controls: bad bytes/SHA, wrong parent/as-of, source unavailable, read timeout.
      No extra download, parse or model call.
- [ ] Real hierarchy recorded; no fake source described as real company quality acceptance.
- [ ] Restore receipts (sentinel / manifest / bytes / mtime / cleanup) executed.

### Phase D — independent final quality review and handoff
**Status:** pending

- [ ] Freeze the source commit; hand the complete diff to an independent reviewer agent.
- [ ] Fix every finding at its shared root cause, re-run the related tests, have the same
      reviewer re-check the final reviewed source SHA.
- [ ] 0 unresolved issues → COMPLETE + `handoff.md` / `handoff.json` / `receipts/`.
- [ ] Only author-branch commits; no merge, no push, no cleanup of this worktree; STOP.

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
| D9 | `consume_narrative_input` gains optional `reader_command` forwarded to the existing reader | Card: reuse the existing process transport/validator; fake reader must sit at the public CWP process boundary, so the reader seam must be reachable from the real consumption entry |

## Errors encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| `git worktree add` reported exit code 1 although the checkout finished | 1 | Verified `rev-parse HEAD` / branch / clean status; exit code was the progress-writer stderr, not a checkout failure |
| CodeGraph `query` returns `[]` for every narrative symbol | 1 | Recorded the index gap (246 indexed files, `scripts/`/`tests/`/`tools/` empty); used the located source files instead of rebuilding an index (card forbids creating/altering it) |

## Next Step

Finish Phase A: confirm how validators carry the new trace, write the RED tests, freeze
`INTERFACES.md`.
