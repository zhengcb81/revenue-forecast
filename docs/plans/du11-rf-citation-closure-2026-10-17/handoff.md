# DU11-RF-CITATION-CLOSURE — handoff

Status: **IMPLEMENTED_REVIEW_PENDING** — source is frozen and every card artifact exists,
but the independent review gate is not closed yet: round 1 returned FAIL (1 blocking + 6
should-fix), all findings were fixed at their shared root cause, and the same reviewer is
re-checking the new source SHA. Only a clean round 2 turns this into COMPLETE.

| item | value |
|------|-------|
| card | `company-wiki/docs/plans/document-understanding-2026-10-13/parallel/du11-2026-10-17/du11_rf_citation_closure.md` |
| repo / worktree | `C:/Users/郑曾波/Projects/revenue-forecast-du11-citation-closure` |
| branch | `codex/du11-rf-citation-closure` |
| base commit | `568fb9256885eb31a0f76d9ead59fd0f98575073` |
| implementation commits | round 1 `1ada02e41c2f16717f8fd0013d972cd279370714`; round 2 (review fixes) = the commit carrying this file's reviewed source SHAs, see `receipts/B-final-tests.json` |
| delivery | one pure-documentation handoff commit after the review closes; ROOT verifies `git rev-parse HEAD` and the frozen source SHAs |
| PWF | `docs/plans/du11-rf-citation-closure-2026-10-17/` (`task_plan.md`, `findings.md`, `progress.md`, `INTERFACES.md`, `receipts/`) |

## What changed (exactly the card whitelist)

Modified:

- `scripts/source_narrative_context.py` — `consume_narrative_input` resolves every bound
  span through the shared adapter, keeps the old receipt keys/values and the old
  binding-field refusal, and adds `citation_trace`; `narrative_read_receipt` adds the same
  trace for the metadata-only read.
- `scripts/research/input_evidence.py` — `_bind_narrative_span` resolves the same closure,
  binds the real parent/locator/pointer for a projected `/3` span, and
  `bind_parameter_evidence` returns `citation_trace` next to the untouched
  `parameter`/`claims`/`sources`/`lineage`.

New:

- `scripts/narrative_citation_context.py` — pure support/context closure + bounded coverage
  diagnostics (no IO, clock, network, model or source re-parse).
- `tests/test_du11_narrative_citation_{wire,context,consumption,projection,e2e}.py`
- `tests/fixtures/du11_narrative_citation/synthetic_reading2.json` (synthetic, no company
  original bytes)

Untouched (deliberately): `scripts/company_wiki_narrative_contracts.py` (the only wire
validator, `git diff` empty), every forecast/formula module, every existing test, CWP/FF/ET,
install directories, `assurance/runs/**`.

## Contract (frozen in `INTERFACES.md`)

- Input compatibility: `revenue-narrative-context/1` and `/3`, with no `reading_context`,
  `du-production-reading/1`, or `du-production-reading/2` — all old wire shapes keep working;
  no CWP schema was upgraded or rewritten.
- Optional binding fields: `citation_group_id` (str), `citation_view` (0-based int). Nothing
  else is accepted as a selection field.
- Output: existing claims / sources / parameter claims / formula refs are byte-identical; a
  new versioned `revenue-narrative-citation-trace/1` object carries the closure and the
  coverage diagnostics, joined to the real dependencies by `claim_id`.
- Named refusals only for real misuse: context-only support, question/analyst role as
  support, an ambiguous view without an explicit selection, a bad explicit selection, a
  foreign parent, a malformed reading context, or a `/3` span without its own
  parent/locator/pointer. Unread/opaque/deferred/limited material, an incomplete layout, no
  `reading_context`, or an ungrouped span are **diagnostics**, never a gate.

## Evidence

- RED before the change: `receipts/A-red-baseline.txt` — **27 failed, 10 passed** on
  byte-exact baseline consumers, every failure behavioural (no harness crash).
- Final: `receipts/B-final-tests.json` and `receipts/B-final-tests.log` —
  `374 passed, 4 skipped`, exit 0, 85.79 s (5 card modules = 74 cases, plus the 15-module
  central regression), `ruff` 0, `mypy` 0.
- The repository's own CI gate `python tools/pre_push_gate.py` is GREEN
  (`416 passed, 36 subtests passed`, exit 0) — `receipts/C-prepush-gate.txt`.
- Round-1 independent review: `receipts/D-reviewer-1.md` (FAIL, 1 blocking + 6 should-fix;
  every finding fixed at the shared root cause, see `findings.md` §10).
- Isolated E2E: real reader → real byte/SHA validation → real consume → `revenue_forecast.py`
  CLI twice; identical `consolidated_forecast` and `segments`, new claim present, trace
  `group_only` carrying the frozen wire's real `unread`/`deferred`/`layout` diagnostics;
  `narrative_source_preparation.py` read CLI exports the same complete `reading_context`.
- Negative controls: bad bytes (`artifact_bytes_mismatch`), provider unavailable, reader
  timeout, wrong as-of (`receipt_request_mismatch`), foreign parent, stale input as-of.
  `socket`/`urlopen` hard-fail during every E2E test; reader child-process calls are counted.
- Restore receipts: 6 × `receipts/restore-*.json` (owned root, sentinel + pre-existing output,
  SHA/mtime before and after, created/removed lists, `restored: true`, `root_removed: true`)
  plus `receipts/C-basetemp.txt` (owned pytest basetemp created, deleted, verified absent).

## Real layer vs fake layer (do not overclaim)

Real: the RF narrative reader adapter, its byte/SHA/receipt validator, both RF consumption
entries, the RF input contract and the revenue calculation CLI, the
`narrative_source_preparation.py` CLI, and the bounded child-process containment.

Fake: the CWP reader implementation behind the published module path
`company_wiki.source_catalog.narrative_transport_cli`, plus the frozen public wire it
replays. The wire is the synthetic `Acme business update` fixture, so this is a
contract/transport acceptance — **not** real company-data quality acceptance.

## Known limitations / ROOT wiring notes

1. Entry 2 (`bind_parameter_evidence`) cannot finish a formal source for a projected `/3`
   context: `narrative-ref/3` + `narrative-read-receipt/3` publish no publication or
   availability fact and RF will not invent one. It resolves the real parent/pointer and then
   refuses with `source_availability_unknown`; reproduction is
   `tests/test_du11_narrative_citation_consumption.py::test_entry_two_projected_wire_resolves_parent_and_names_the_publication_gap`.
   Interface need for ROOT: CWP publishes the publication/availability fact for
   `official_json` projections (same shape as the `/1` manifest or the availability DTO).
2. Entry 2's `citation_trace.reading` describes the first narrative read of that call
   (per-claim artifact binding stays in the existing `lineage`). Entry 1 always has one read.
3. RF does not interpret DU layout/semantic coverage; it only retains bounded counts and
   never claims complete reading coverage.
4. The `/2` citation-view closure is proven with the synthetic descriptor wire (built by the
   tests, validated by the real contract); the frozen public `actual-090` wire is `/1`
   (group-only closure). Both run through `validate_narrative_response`.
5. No CWP/ET source, company root, transcript or real config was extracted or copied; the
   declared upstream commits are
   `34a7dd71aaa49d18c13fcdd300ce79581114ca5b` (CWP) and
   `2584b7eed062a9a30254bc06b4f19ab5471b414e` (ET), used only as interface references.
6. Installed skill copies / release gates / publication registries were not touched; ROOT
   performs merge, push and installation synchronization after acceptance.

## Independent review

- Round 1: `receipts/D-reviewer-1.md` — FAIL (1 blocking, 6 should-fix, 10 nits).
  All blocking/should-fix findings fixed at the shared root cause; nits either fixed
  (fixture now has a separate unit span; two-view groups consume in both directions
  positively; the wire module carries its own contract tests; null-vs-zero tightened;
  RED/handoff/receipt hygiene corrected) or recorded with their reason in
  `findings.md` §10.
- Round 2: the same reviewer re-checks the new frozen source SHA. `handoff.json` records its
  identity, report path, reviewed SHAs and the unresolved count; it is written only after a
  clean round 2.
