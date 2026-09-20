# I-07-A decision.md

## No specialist decision is required for this card — with one recorded judgment call

The card's own text does not open a professional decision gate: it fixes the sample identities
(inherited from the plan manifest), fixes as-of 2026-09-18, forbids downloads and production writes,
and fixes the three state labels. There is no schema change, no transaction boundary, no statistical
threshold, no financial-period or revenue-definition question, and no deployment or migration choice.
Per `START_HERE.md` (line 47) those are the categories that require a `decision.md`, and none applies.

**`decision.md` status: NA for a specialist decision.** The reason is recorded above rather than left
implicit.

## Judgment calls recorded for the reviewer (not specialist gates)

**J1 — `catalog_dir` semantics for the isolated config.** The isolated config's `catalog_dir` was
rebound to a *directory* (`iso/catalog`), matching the product's own `CatalogConfig.catalog_dir`
(`CW/config/source_catalog.yaml` uses `catalog_dir: "${PROJECT_ROOT}/.source_catalog"`, a directory).
The card says states are built "只在隔离catalog构建" ("only in the isolated catalog"), and a directory
is what the product calls a catalog. Implementer position: the isolated catalog is the **directory**,
and its sqlite file is a minimal, attempt-owned schema — not a copy of the 49.7 GB production
database, which is neither necessary for the three state labels nor permitted to be duplicated for a
documentation card. Reviewer may disagree and require a table-filtered copy (I-00-B's
`isolated_binding_plan` contemplates that for run cards); that is a valid `changes_required`.

**J2 — the fifth root counts as `bound` at existence + declaration level.**
`implementation_plan.md:138` asks for "合法第五root" and `CW/config/source_catalog.yaml` declares
`root_id: future_lake` with `kind: directory`, `adapter_id: sidecar_filing_v1`, `read_only: true`,
`reusable_for_filing: true`; the directory exists and the production `roots` table registers all four
root ids including `future_lake`. Implementer position: the *config* cell is bound (declaration +
existence both verified read-only), while whether the adapter actually ingests from that root is a
scan/ingest question and belongs to I-07-C. Reviewer may narrow the cell to `planned`; that is also a
valid outcome and does not change any other cell.

**J3 — the CN sample cannot be `companies_only`.** The observation found the same bytes registered
under `company_raw` **and** `dropbox_stock`. The card forbids deleting other copies to manufacture
exclusivity, so the implementer recorded the real multi-root fact and marked `source.companies_only`
**blocked**. Marking it `not_applicable`, or reporting the CN sample as companies-only because the
company-wiki copy is the "primary" location, would both be wrong.

**J4 — one artifact cannot be reduced to a single state word.** The indexed sample's artifacts are
`summary: completed` and `normalized: partial` with `quality_flags: [empty_output]` in its front
matter, while both files hash exactly as recorded. The implementer therefore bound both the `valid`
cell (completed) and the `stale` cell (producer-declared `normalization_status: partial`) and left
`tampered` as `planned` with the hash-comparison result recorded. Collapsing this to "artifact valid"
would hide the partial flag.

---

## r2 — disposition of the judgment calls after independent review (APPEND-ONLY)

Added 2026-09-20 after the independent re-read. **The text of §J1–§J4 above is the r1 record and is
left byte-intact; where a call was overruled, the ruling below is authoritative.** A successor who
reads only this file must read this section before acting on §J2.

| call | r1 position above | **r2 ruling (authoritative)** |
|---|---|---|
| **J1** — isolated `catalog_dir` semantics | implementer proposed a directory holding a minimal attempt-owned schema; reviewer was invited to require a table-filtered copy | **Accepted as scoped-usable**, with an explicit prohibition added: `iso/catalog/catalog.sqlite3` is 5 tables vs production's 18 (5/5 `CREATE` differ), so it **cannot carry a resolve or a registration** and **must not** be reused by I-07-B, which must bind a production-isomorphic or table-filtered catalog. Recorded in `state_matrix.json:isolated_catalog_prohibition` and `handoff.json.blocked_by`. |
| **J2** — fifth root | *"the fifth root counts as `bound` at existence + declaration level"* | **OVERRULED — this `bound` claim was rejected by the review.** `config.legal_fifth_root` is **`planned`**. The declared-and-existing root is not ingest capability: the only location under it is the placeholder `future_lake/README.md` (545 B, `document_kind = broker_research` — note the kind is `broker_research`, not `broker_repository`). The authoritative cell state is in `state_matrix.json`/`.md` and `oracle.md` §7; see also `review.md` (r2 section). **§J2 above must not be cited as the card's conclusion.** |
| **J3** — CN cannot be `companies_only` | blocked, because the same bytes sit under two roots | **Unchanged.** The review found no fault. The disproval is now backed by SQL: two `original_primary` rows, `observed_size 79925886` each. |
| **J4** — one artifact cannot be one word | bound both `valid` and `stale`, left `tampered` planned | **Unchanged.** Not challenged; the recompute question stays I-02/I-05 scope. |

Counts after the J2 ruling: **bound 9 / planned 15 / blocked 5 / not_applicable 0** (the r1 figure was
bound 10 / planned 14). The single changed cell is `config.legal_fifth_root`.
