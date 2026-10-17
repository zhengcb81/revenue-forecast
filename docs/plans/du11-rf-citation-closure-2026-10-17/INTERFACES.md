# DU11-RF-CITATION-CLOSURE — frozen consumption interface (node A)

This file freezes what node A decided. Node B implements exactly this; a later change is
a contract change and must be recorded here with its compatibility note.

Baseline: `568fb925` · branch `codex/du11-rf-citation-closure`.

## 1. Input compatibility (unchanged)

| input wire | meaning for RF |
|------------|----------------|
| `revenue-narrative-context/1` + no `reading_context` | legacy legal single-span path; behaviour and every existing field unchanged |
| `revenue-narrative-context/1` + `du-production-reading/1` | same list; RF records the source-owned reading **group** only |
| `revenue-narrative-context/1` + `du-production-reading/2` | same list; RF resolves the source-owned **citation view** (support vs context) |
| `revenue-narrative-context/3` (projected `/3` request) | same list with `parent_source_refs`; every dependency binds the actual captured parent plus the original `source_locator`/`pointer` |

No CWP wire is upgraded or rewritten. `company_wiki_narrative_contracts` stays the only
wire validator; the new resolver re-checks **only** the invariants it consumes
(group membership is transported, view partition is disjoint and complete) and reports a
named refusal otherwise — it never re-implements the wire schema, byte or identity checks.

## 2. New optional binding fields (only these two)

| field | type | rule |
|-------|------|------|
| `citation_group_id` | `str` | optional; when the bound span occurs in more than one source group this names the chosen `group_id`. Must be a group that contains the span. |
| `citation_view` | `int` (not `bool`) | optional 0-based index into the chosen group's `citation_views`. Required only when the span is `support` in more than one legal view. The named view must contain the span in `support_evidence_ids`. |

Entry 1's binding set therefore becomes
`{span_id, claim_id, parameter_id, support_type}` **plus** optionally
`citation_group_id` / `citation_view`; any other extra field stays
`narrative_citation_binding_fields`. Entry 2 keeps its existing free-form binding and reads
the same two optional keys. Neither entry guesses a view.

## 3. Named error codes (frozen)

All are raised by `scripts/narrative_citation_context.py` as
`NarrativeCitationError(ValueError)` with `str(exc) == "<code>: <detail>"`.

| code | when |
|------|------|
| `narrative_citation_binding_fields` | unknown/extra or wrongly typed citation selection field |
| `narrative_citation_span_unknown` | the bound span is not a transported span of this context |
| `narrative_citation_reading_invalid` | a `reading_context` the resolver would have to trust is malformed: unknown schema, non-list groups, group member not transported, view partition not disjoint/complete, duplicate or missing id |
| `narrative_citation_group_unknown` | `citation_group_id` does not name a group that contains the span |
| `narrative_citation_group_ambiguous` | in a `du-production-reading/2` context the span is `support` in more than one legal group and no `citation_group_id` was given |
| `narrative_citation_view_unknown` | `citation_view` out of range for the resolved group (or named while the reading context has no views) |
| `narrative_citation_view_not_support` | the explicitly named view has the span in `context_evidence_ids` (or nowhere) |
| `narrative_citation_view_ambiguous` | no explicit view, but the span is `support` in more than one legal view of one group |
| `narrative_citation_span_invalid` | a projected `/3` span lacks its own `parent_content_sha256`, `source_locator` or `pointer` |
| `narrative_citation_context_only` | no legal view has the span as support; it is only ever `context` |
| `narrative_citation_source_role_refused` | the span's transported `source_role` is `analyst` or `investor_question`, so it cannot be support for an RF parameter claim |

**Groups-only reads never become an ambiguity gate.** `du-production-reading/1` publishes
no support/context partition, so a span that belongs to several groups is consumed with the
published-first group recorded deterministically (`closure: "reading_group"`, its
`group_id`); `citation_group_id` may name another. Nothing is promoted and nothing is
silently invented.

Entry 1 raises these as `ValueError` (they are `ValueError`s) and keeps its existing
messages for the pre-existing failures. Entry 2 converts them to `ForecastInputError`
(the public input-contract error of that entry).

Nothing else becomes a refusal: unread pages, opaque pages, deferred packages, sampling
`limited`, an incomplete layout, a missing `reading_context`, or a span outside every group
are **diagnostics**, never a prediction permission gate.

## 4. Trace object (frozen): `revenue-narrative-citation-trace/1`

One versioned object per read, `citation_trace`, added to the consumption receipt
(`source_narrative_context.narrative_read_receipt` and `consume_narrative_input`) and to the
`bind_parameter_evidence` result. It is the only place the closure lives: the RF input
document, every claim field, `receipt["dependencies"]` and the existing formula refs are
unchanged, and the trace is joined to them by `claim_id`.

```json
{
  "schema_version": "revenue-narrative-citation-trace/1",
  "status": "not_consumed | closed | group_only | partial | ungrouped",
  "reading": {
    "present": true,
    "schema_version": "du-production-reading/2",
    "attribution": "absent | groups_only | source_owned_views",
    "group_count": 2,
    "citation_view_count": 4,
    "unread": {
      "counts": {"opaque_pages": 5, "deferred_pages": 4, "deferred_unit_ids": 0,
                 "unassigned_unit_ids": 1},
      "limited": true,
      "opaque_pages": 1, "deferred_pages": 1, "deferred_unit_ids": 0,
      "unassigned_unit_ids": 1,
      "native_scan": "complete",
      "structure_complete": false
    },
    "deferred": {"count": 3, "listed": 1, "limited": true},
    "selection_diagnostics": [{"code": "BOUND", "count": 2}],
    "layout_complete": false,
    "coverage_note": "diagnostic_only_not_a_permission_gate"
  },
  "dependencies": [
    {
      "claim_id": "du11_cl",
      "parameter_id": "0_base_2026",
      "span_id": "urn:company-wiki:evidence-span:sha256:...",
      "closure": "citation_view | reading_group | ungrouped",
      "group_id": "urn:company-wiki:reading-group:sha256:...",
      "group_kind": "qa_exchange",
      "section_role": "business",
      "view_index": 0,
      "source_role": "management",
      "support_evidence_ids": ["..."],
      "context_evidence_ids": ["..."],
      "context_evidence": [
        {"span_id": "...", "locator": "loc:v1/paragraph:2/chars:33-92",
         "source_role": "investor_question"}
      ],
      "context_evidence_count": 1,
      "context_evidence_limited": false,
      "projected": null
    }
  ],
  "counts": {"dependencies": 1, "view_closed": 1, "group_only": 0, "ungrouped": 0,
             "context_evidence": 1, "context_evidence_unknown": 0,
             "context_evidence_limited": 0}
}
```

Rules frozen with the shape:

- **Coverage parsing never gates.** The reading groups/views decide support vs context and
  are strict. Every *coverage* value (the `unread` block, `deferred`/`deferred_count`/
  `deferred_limited`, `selection_diagnostics`, `layout_coverage`) is a diagnostic: a value
  the adapter cannot read as a count/boolean/list is reported as `null`, never as a refusal.
  A legal wire with `layout_coverage = {"complete": "partial"}` still consumes.
- `status`: `not_consumed` with no dependency; `closed` when every dependency is
  `citation_view`; `group_only` when every dependency is `reading_group`; `ungrouped` when
  every dependency is `ungrouped`; `partial` for any mixture.
- `reading.attribution`: `absent` (no `reading_context`), `groups_only`
  (`du-production-reading/1`), `source_owned_views` (`du-production-reading/2` with views).
- **Unknown stays `null`**, never `0`/`false`: without the optional sampling block
  `unread.counts`, `unread.limited`, `deferred.count`, `deferred.limited` and
  `selection_diagnostics` are `null`; with no reading context the page/unit counts are
  `null` and `deferred.listed` is `null`; a non-view closure has
  `context_evidence_ids`, `context_evidence_count`, `context_evidence` **and**
  `context_evidence_limited` all `null` (there is no partition to bound). The trace `counts`
  block therefore separates `context_evidence` (sum over dependencies that do have a
  published partition) from `context_evidence_unknown` (dependencies without one).
- `context_evidence` is a bounded projection (cap **32** entries) of the chosen view's
  context spans: transported `span_id`, `locator` and `source_role` only — no source text is
  copied into RF. Over the cap, `context_evidence_limited` is `true` and
  `context_evidence_count` still reports the full count.
- `group_kind`/`section_role`/`source_role`/`projected` are `null` when the wire (or the
  chosen closure) does not carry them. `projected` is
  `{"parent_source_id", "parent_sha256", "source_locator", "pointer"}` for a `/3` span and
  `null` otherwise; it always comes from that span's own binding, never from another parent.
  Entry 2 additionally requires both the span's `source_id` **and**
  `parent_content_sha256` to match one `parent_source_refs` entry (the same identity the wire
  validator enforces) and the span's `projection_id` to match the subject `item_key`, so a
  re-signed span cannot borrow another original.
- **Both directions of a two-view group are supported.** A `du-production-reading/2` group
  whose two views point in opposite directions resolves each side to its own
  support/context pair. For a Q/A pair the view that makes the analyst question the support
  is structurally legal but is then refused by the `source_role` rule (a question is not a
  company fact); a two-view group over two company statements consumes in both directions.
- `coverage_note` is a constant label, not a judgement: RF never claims complete reading
  coverage, including when no `reading_context` exists.
- Entry 2 can technically receive several different narrative reads in one call. Its
  `citation_trace.reading` then describes the **first** narrative read of that call while
  every dependency keeps its own group/view closure, and the existing `lineage` entries keep
  the per-claim `narrative_artifact`. RF does not merge reads; a consumer that needs the
  coverage of a second read must read it again. Entry 1 always has exactly one read.
- Entry 2's trace covers the narrative-span bindings of that call only: a classic
  `excerpt`/`locator` binding carries no reading closure and is not listed.

## 5. Old → new minimal JSON (entry 1)

Before (baseline, `du-production-reading/2` wire, support span bound):

```json
{"schema_version": "revenue-narrative-consumption/1", "status": "consumed",
 "narrative_ref": {"...": "..."}, "read_at": "2026-10-03T00:00:00Z",
 "quality_status": "verified", "selection": {"status": "selected", "coverage_complete": true},
 "dependencies": [{"span_id": "urn:...:7b47fb", "locator": "loc:v1/paragraph:3/chars:93-154",
                   "parser_name": "du11-fixture-parser", "parser_version": "1.0.0",
                   "source_id": "urn:company-wiki:source:sha256:...",
                   "source_sha256": "...", "claim_id": "du11_cl",
                   "parameter_id": "0_base_2026", "formula_refs": [{"segment": "Segment A"}]}]}
```

After (same call; every old key and value above is unchanged, one key is added):

```json
{"schema_version": "revenue-narrative-consumption/1", "status": "consumed",
 "...": "identical old fields ...",
 "citation_trace": {"schema_version": "revenue-narrative-citation-trace/1",
                    "status": "closed",
                    "reading": {"present": true, "schema_version": "du-production-reading/2",
                                "attribution": "source_owned_views", "...": "..."},
                    "dependencies": [{"claim_id": "du11_cl", "parameter_id": "0_base_2026",
                                      "closure": "citation_view", "view_index": 0,
                                      "context_evidence_ids": ["urn:...:q"], "...": "..."}],
                    "counts": {"dependencies": 1, "view_closed": 1}}}
```

## 6. Old → new minimal JSON (entry 2)

Before: `{"parameter": {...}, "claims": [...], "sources": [...], "lineage": [...]}` — the
narrative span binding produced a claim and a formal source with **no** closure information.

After: the same four keys with identical values, plus
`"citation_trace": {"schema_version": "revenue-narrative-citation-trace/1", "status": "closed",
"reading": {...}, "dependencies": [{"claim_id": "claim_0_base_2026_0", "parameter_id":
"0_base_2026", "closure": "citation_view", "view_index": 0, "...": "..."}], "counts": {...}}`.

## 7. Compatibility matrix

| # | wire | entry 1 | entry 2 | trace |
|---|------|---------|---------|-------|
| C1 | `/1`, no `reading_context` | unchanged consume | unchanged | `reading.present=false`, `attribution="absent"`, deps `ungrouped`, counts/limited `null` |
| C2 | `/1`, `reading/1` | consume; group closure only (several groups → the published-first group is recorded, `citation_group_id` may name another) | same | `group_only`, no support/context ids |
| C3 | `/1`, `reading/2` | support view required; context-only/ambiguous/question refused | same codes | `closed`, view ids preserved |
| C4 | `/3`, `reading/1` | consume; parent + original `source_locator`/`pointer` recorded | span parent resolved, then named source-clock refusal (below) | deps carry `projected` |
| C5 | `/3`, `reading/2` | as C4 with view ids | as C4 | `closed` + `projected` |
| C6 | any, span outside every group | consume per old path | same | dep `ungrouped`; `partial`/`ungrouped` |
| C7 | any, empty bindings | `not_consumed` | not applicable | `not_consumed`, reading diagnostics still reported |

### Known upstream limitation (reported to ROOT, not patched)

Entry 2 must derive a formal RF source, which the source clock only accepts with a
publication fact (`qualify_source_information`) or an availability proof. `narrative-ref/3`
and `narrative-read-receipt/3` publish neither (only `observed_at`), so a projected `/3`
context resolves its real parent/pointer and then **names** the gap:
`source_availability_unknown`. Reproduction:
`tests/test_du11_narrative_citation_consumption.py::test_entry_two_projected_wire_resolves_parent_and_names_the_publication_gap`.
Interface need: CWP to publish the publication/availability fact for `official_json`
projections (same shape as the `/1` manifest or the availability DTO).

## 8. Public function additions (compat)

- new pure module `scripts/narrative_citation_context.py`
  (`reading_trace`, `resolve_span`, `citation_dependency`, `citation_trace`,
  `selection`, `trace_status`, `NarrativeCitationError`, `TRACE_SCHEMA`; no IO, no clock,
  no network, no model)
- `source_narrative_context.consume_narrative_input` signature is **unchanged**; only the
  returned receipt gains `citation_trace`
- `source_narrative_context.narrative_read_receipt` keeps every old key and gains
  `citation_trace`
- `research.input_evidence.bind_parameter_evidence` keeps `parameter`/`claims`/`sources`/
  `lineage` and gains the `citation_trace` result key

The Phase C fake reader sits behind the *existing* published CWP module path
(`company_wiki.source_catalog.narrative_transport_cli` placed on `PYTHONPATH`), so no new
CLI/transport/permission seam is added to production code.
