# DU11-RF-CITATION-CLOSURE — findings

All evidence below was read from the fixed baseline `568fb925` in this worktree.
No original company document, provider call, model call or network read was made.

## 1. Baseline and isolation

- `git rev-parse HEAD` = `git rev-parse main` = `git rev-parse origin/main`
  = `568fb9256885eb31a0f76d9ead59fd0f98575073`.
- Main-repo WIP (`M assurance/runs/daily_alert.jsonl`, `M assurance/runs/weekly_alert.jsonl`,
  `M assurance/runs/weekly_manifest.json`, `?? output/`) was only observed, never touched,
  and is not present in this worktree (`git status --porcelain` → empty after
  `git worktree add -b codex/du11-rf-citation-closure <path> 568fb925`).

## 2. CodeGraph structural query — recorded index gap

`codegraph status -j` on the initialised main repo:
`{"initialized":true,"fileCount":246,"nodeCount":4486,...,"languages":["python"]}`.

`codegraph files -p .` shows `scripts`, `tests`, `tools` as **empty** nodes, and every
narrative symbol returns `[]`:

| query | result |
|-------|--------|
| `consume_narrative_input` | `[]` |
| `narrative` | `[]` |
| `read_narrative_context` | `[]` |
| `bind_parameter_evidence` | `[]` |
| `_bind_narrative_span` | `[]` |
| `narrative_read_receipt` | `[]` |

Gap recorded instead of re-indexing (card forbids creating/altering the index). The call
graph below was produced from the located source files.

## 3. Two real parameter-binding entry points

### Entry 1 — `scripts/source_narrative_context.py::consume_narrative_input`
`read_narrative_context` (real subprocess + `validate_narrative_response`) → `_captured_parent`
→ per-binding `_claim` → receipt `narrative_read_receipt`.
Binding shape is **exactly** `{span_id, claim_id, parameter_id, support_type}`
(`if set(binding) != {...}: raise ValueError`). `_claim` copies `span["raw_text"]` and the
span locator; the receipt keeps `selection`, `quality_status` and a flat `dependencies`
list (`span_id`, `locator`, parser, source, claim/parameter, `formula_refs`, and for
`context/3` also `source_locator`/`pointer`/`subject_ref`).
Callers: `tools/run_narrative_consumption_e2e.py`, `tools/build_auditable_case.py`,
`tests/test_source_preparation_complete_result.py`, `tests/test_architecture_dependency_uses.py`,
`tests/test_w04_public_consumer.py`, `tests/test_source_clock.py`.

`narrative_read_receipt` is also used by `scripts/source_preparation.py` (the
`source-preparation-result/1.narrative` sidecar) — a second consumer of the same receipt.

### Entry 2 — `scripts/research/input_evidence.py::bind_parameter_evidence`
`binding["narrative_context"]` → `_bind_narrative_span` re-checks `output_sha256`/`span_id`,
manifest↔source hash and the source clock, then derives a **formal revenue source+capture**
and claim. Callers: `tests/test_evidence_input_lineage.py`, `tests/test_input_semantics_e2e.py`
(no production caller of this helper in this repo; it is the documented public parameter
binding entry of `research.input_evidence`, cf. `docs/implementation/cmrf-input-semantics-20261008`).

### Where the semantic loss is
Neither entry reads `reading_context`. `company_wiki_narrative_contracts._reading_context`
already validates `/1` and `/2` (groups, and for `/2` the
`citation_views` partition `support ∪ context == evidence_ids`, no overlap, unique support
identity, one parent per group, transported spans only). That closure is validated and then
**dropped** by both consumers:

- `consume_narrative_input`: no group/view/context ID anywhere in `dependencies`;
  a context span (an analyst question, a table header/footnote) is consumed identically to a
  support span; nothing records unread/deferred/opaque/layout diagnostics.
- `_bind_narrative_span`: same, and it cannot read `revenue-narrative-context/3` at all —
  it requires `context["source_ref"]` and `context["manifest"]`, which only exist on `/1`
  (`require(... "narrative_context is missing its source or narrative reference")`).
- `narrative_read_receipt`: keeps `selection`/`quality_status` only; no reading-context
  closure, and no explicit statement that RF never claims complete coverage.

Existing validators already fix the *format* questions (trace must not duplicate them):
`company_wiki_narrative_contracts` validates the wire; `contracts/document.py` +
`forecast` validate the RF input. The new trace therefore only needs to be a plain
versioned dict in the consumption receipt / bind result, not a new wire schema.

## 4. Compat anchors (existing tests that must not change)

- `tests/test_source_preparation_complete_result.py` — legal single-span consumption,
  claims/excerpt/locator/formula refs unchanged, `not_consumed` for metadata-only.
- `tests/test_architecture_dependency_uses.py` — carry/progress recognition inputs consume a
  verified narrative; `run_forecast` output equality before/after.
- `tests/test_w04_public_consumer.py` — projected `/3` parent, `source_locator` and `pointer`;
  rejects unused parameter / wrong support type / wrong source SHA / wrong as-of.
- `tests/test_citation_attribution_narrative_contract.py` — `_claim` keeps
  `context_evidence_ids` attribution; `_reading_context` accepts both Q/A views.
- `tests/test_shared_reading_narrative_contract.py` — frozen public `actual-080` / `actual-090`
  wire and the reading-context resource bounds.
- `tests/test_source_clock.py::test_T06_auto_narrative_claim_uses_actual_check_UTC_day`.
- `tests/test_evidence_input_lineage.py::NarrativeBindingTests` — entry 2 span binding.
- `tests/test_narrative_source_preparation_transport.py` / `..._e2e.py` — real subprocess
  transport with a fake provider at the CWP process boundary (reused for Phase C).

## 5. Frozen public wire available in-repo (no real originals copied)

- `docs/plans/shared-reading-consumer-2026-10-14/fixtures/actual-090-*`
  (1 request 982 B, gzip bundle 4 905 B, receipt 1 860 B) is a legal
  `revenue-narrative-context/1` public wire with `du-production-reading/1`, one
  `paragraph_event` group of two spans (an `html_heading` context span and an
  `html_paragraph` support span), `unread.counts`/`limited`, `structure_complete=false`,
  one `unassigned_unit_ids` entry, `layout_coverage.complete=false`.
- `docs/plans/shared-reading-consumer-2026-10-14/fixtures/actual-080-*` has no
  `reading_context` (legacy compat anchor).
- `tests/fixtures/cwp_narrative_transport_v1/` holds the producer golden (`/1`, one
  `management` span) and the html export.

These are the frozen public wires used by Phase A/C. The text is the synthetic
`Acme business update` fixture, not real company material.

## 6. Coverage diagnostics available on the wire (for the trace)

From `_reading_context`: `unread.{opaque_pages,deferred_pages,deferred_unit_ids,unassigned_unit_ids,
native_scan,structure_complete}` + optional sampling `unread.{counts,limited}`; optional
`deferred_count`/`deferred_limited`/`selection_diagnostics[{code,count}]`; `deferred[{package_id,reason}]`;
`layout_coverage` (free dict). `_reading_sample` proves `limited == (count > len(list))`, so
`null` (unknown) must stay `null` and is never inferred as `0`.

## 7. Upstream gaps found (reported, not patched across repos)

1. `narrative-ref/3` + `narrative-read-receipt/3` publish **no** publication or availability
   fact (only `observed_at`). Entry 2's formal source+capture needs `published_date`
   (source clock `source_availability_unknown` otherwise), so projected `/3` cannot become a
   formal RF source without inventing one. Reproduction: build the projected wire from
   `tests/test_w04_public_consumer.py::projected_wire()` and call
   `bind_parameter_evidence(..., evidence_bindings=[{"role": ..., "narrative_context": context, "span_id": ...}])`.
   Interface need for ROOT: CWP to publish a publication/availability fact for
   `official_json` projections (same shape as the `/1` manifest or the availability DTO).
2. `reading_context` `/2` gives no stable view identifier (views are anonymous list entries);
   RF therefore selects a view by `(group_id, list index)` and records both in the trace.
