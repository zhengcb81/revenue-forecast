# FC-904 Change Contract — source_preparation 消费 selector（DAG 最小重算）

> Owner: revenue · Base triplet: revenue `07578a3` / filing `959d04c` / wiki `fd4f50b`
> Dependencies: FC-903 (accepted) · Scenario IDs: AR-01~09

## Intended behavior delta (observable)

`source_preparation.py` (the single production entry) derives artifact
selection from the FC-902 **envelope bundle** through a DAG-minimal selector
instead of the unsourced `payload.get("selected_artifacts", [])` path (which
always returned `[]` from a dict that never carried the key).

The reuse receipt records, with a source:
- `artifact_read` — roles whose verified artifact is in the envelope bundle's
  `valid_handles` (provenance-matched for consumer_analysis);
- `producer_events` — roles that must be (re)produced = the DAG closure
  (role + transitive dependents over the frozen ROLE_DEPENDENCIES) of the
  non-reusable roles — never a blind full recompute.

## Selector semantics (AR-01..09 mapping)

| Scenario | Behavior |
|---|---|
| AR-01 | valid normalized/markdown/sections/summary → artifact_read includes them; producer_events excludes them (parser/LLM=0, artifact read > 0) |
| AR-02 | only summary missing → producer_events = [summary, consumer_analysis] (DAG closure); other roles read, hashes unchanged |
| AR-03 | normalized not reusable → producer_events = all roles deriving from normalized (DAG invalidation), never blind full recompute of valid siblings |
| AR-04 | no artifact reusable (raw source changed) → artifact_read=[] , producer_events=all roles |
| AR-05 | tampered artifact (invalid entry) → not read (fail closed) |
| AR-06 | consumer_analysis provenance mismatch → not read; markdown etc. continue to be read |
| AR-08 | legacy_unbound (invalid entry) → not read; never trusted |
| AR-07/09 | T2 real samples + cross-root sharing: bundle semantics inherited from FC-902 (no path-based duplication) |

`bundle=None` (bundle_status=unavailable) → artifact_read=[], producer_events=all
roles (honest: nothing reusable, everything must be produced).

## Single source of truth

`ROLE_DEPENDENCIES` is IMPORTED from `company_wiki.source_catalog.artifact_dag`
(the frozen DAG contract) — the transitive closure is computed from the
imported constant, so no second copy can drift. `company_wiki` is installed
in the revenue env (editable package pointing at the company-wiki repo).

## Allowed symbols / files

- `scripts/company_wiki_source.py` — `select_artifact_roles` (new) +
  `select_reusable_artifacts` reads the envelope bundle (FC-902 move) +
  `_bundle_from_handle` helper.
- `scripts/source_preparation.py` — call the selector, record
  artifact_read/producer_events, DELETE the unsourced
  `payload.get("selected_artifacts", [])` line.
- NEW `tests/test_fc904_artifact_selection.py`.
- `assurance/fc/FC-904/` (receipts live in revenue-forecast/assurance/fc/).

## Forbidden changes

- Re-validating artifact content in revenue (validity is decided by
  company-wiki; revenue consumes the bundle's valid/invalid verdict).
- Re-introducing an unsourced `selected_artifacts` default.
- Duplicating ROLE_DEPENDENCIES as a literal (must import).
- Any write to catalog/roots.

## Expected call-edge delta

- NEW production call: `source_preparation.prepare_source` →
  `company_wiki_source.select_artifact_roles` (production caller >= 1).
- `select_reusable_artifacts` switches its data source to the envelope bundle.

## Side-effect budget

| Effect | Budget |
|---|---|
| catalog writes | 0 |
| external root writes | 0 |
| file reads | 0 new (selection is over the envelope bundle only) |

## Rollback

Additive receipt fields + new selector; revert = revert commits.

## Diff budget

2 production scripts + 1 test file (≤250 lines). Exceeds → split.
