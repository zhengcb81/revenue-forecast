# I-07-A review.md

> ## PENDING independent review
> Written by the **implementer**. Nothing here is an acceptance, and no card status is signed by this
> file. The independent reviewer must re-derive at least one hash and one catalog fact, and must decide
> the three judgment calls in `decision.md` (J1 the isolated-catalog semantics, J2 whether the fifth
> root cell is bound or planned, J3/J4 the source and artifact cell shapes).
>
> **Scope of a pass:** it would accept the frozen sample matrix and the precondition-state archive, and
> nothing else. It would **not** accept any resolve behaviour, any download, any artifact recomputation,
> any prediction, or the production catalog's health — none of those were exercised.

## What this attempt delivers

- `oracle.md` — frozen before the first run: identity rule R1, read-only rules R2–R8, the frozen sample
  identities, the seven dimensions with bound/planned/blocked expectations, the command table V0–V5 and
  the falsifiable V-checks 1–7.
- `after/state_matrix.json` + `after/state_matrix.md` — the frozen matrix actually filled in.
- `iso/cases/case-0{1,2,3}-*/state.json` — the three precondition states, each labelled with its
  `state_origin`.
- `iso/catalog/` + `iso/catalog_root/` + `iso/config/` — the isolated catalog, the copied originals in
  production layout, and the one-line-rebound config copy.
- `before/`, `after/` — raw command output, reports and the V5 integrity witness.

## The frozen matrix, as measured

| dimension | cell | state | what bound it |
|---|---|---|---|
| market | A-share CN | **bound** | CN-ZIJIN-2025 raw/sidecar/request hashes + identity all match |
| market | HK | **bound** | HK-XIAOMI-2025 likewise |
| market | US | **bound** | US-MSFT-2026 likewise |
| file_state | downloaded + indexed | **bound** | CN: documents row (source_status `active`), 1 source, 3 locations, 2 artifacts |
| file_state | downloaded, not indexed | **bound** | HK + US: bytes exist and hash-match, and documents/sources/locations/artifacts are all **0 rows** |
| file_state | genuinely missing | **blocked** | every plan sample exists on disk; the missing identities are unbound in `sample_manifest.json`; only an isolated simulation exists |
| source | companies-only | **blocked** | CN is registered under `company_raw` **and** `dropbox_stock` — a real multi-root case |
| source | dayu-only | **blocked** | no plan sample is bound to the `dayu_portfolio` root |
| source | external-dir-only | **blocked** | `EXTERNAL-ONLY` is unbound; deleting the other copies to create exclusivity is forbidden |
| source | multi-root same bytes | **bound** | CN has two roots; the census found 20 such content hashes in production |
| artifact | valid | **bound** | `summary` role `completed`, content hash matches the bytes |
| artifact | missing | **planned** | no required role is absent for the indexed sample |
| artifact | stale | **bound** | `normalized` role `partial` with `quality_flags [empty_output]` in its front matter |
| artifact | tampered | **planned** | detection = hash comparison; both roles matched, so nothing bound |
| artifact | not applicable | **planned** | no NA role observed; the cell would need a justification string |
| request | exact / latest / new revision / mixed period / duplicate / concurrent | **planned** ×6 | these are resolve-time behaviours; the request artifacts are frozen and hash-verified, execution is I-07-B |
| config | installed entry | **planned** | bound and exercised by I-16-A |
| config | production config copy | **bound** | isolated copy, exactly 1 changed line, production hash unchanged |
| config | legal fifth root | **bound** | `future_lake` declared config-only with a registered adapter, `read_only: true`; directory exists; production `roots` registers 4 ids |
| fault | provider / scan / DB lock / interruption | **planned** ×4 | fault injection is I-07-D |
| generality | company not in fixture names | **blocked** | `implementation_plan.md:141` requires it; no such sample is frozen and this card may not download ⇒ handed to I-07-C |

**Counts: bound 10 / planned 14 / blocked 5 / not_applicable 0.** No cell is silently "not
applicable" (V-check 3 and V-check 7 both pass with `not_applicable == 0`).

## Findings that contradict an assumption in the plan text

1. **The CN sample is already indexed — and it is multi-root.** `sample_manifest.json` recorded CN as
   "raw reusable; review/artifact readiness incomplete". The catalog actually holds a `documents` row
   with `source_status = active`, `published_date 2026-03-20`, `first_seen_at 2026-07-31`, plus a second
   location row under the `dropbox_stock` root for the **same content hash**. So the "already indexed"
   cell binds to CN, and CN can never be presented as a companies-only sample.
2. **HK and US are present but *completely* unregistered** — not "partially registered": 0 rows in
   `documents`, `sources`, `locations` **and** `artifacts`. Their raw files and sidecars hash exactly as
   the plan recorded, so I-07-B needs no re-download, only registration.
3. **The artifact state is mixed, not clean.** `normalized` is `partial` with an `empty_output` quality
   flag while `summary` is `completed`; both files are complete on disk and hash as recorded. A reader
   who treats "artifact exists and hashes" as "artifact valid" would miss the partial flag.
4. **The `--catalog`/config defect in `slo_probe.py` has a real, reachable trigger** (recorded here
   because this card read the tool as an anchor): the probe's resolve argv omits `--as-of-date`, which
   `CW/src/company_wiki/source_catalog/cli.py:411` requires, so every measured resolve child exits 2
   through argparse. That is I-14-A's subject; this card only records the anchor and its hash.

## Independent-oracle discipline

- The matrix is derived by `harness/i07a_matrix.py` from the raw evidence files only
  (`before/snapshot.json`, `after/rehash.json`, `after/observe_readonly.json`, `iso/isolated_state.json`,
  `iso/config_rebind.json`). It re-computes no expectation from a function under test, and the expected
  cell states were written in `oracle.md` before V1 ran.
- The three identities were re-derived from the bytes, not from the manifest strings: a mismatch would
  have produced `all_match=false` and a drift finding. All three matched.
- The catalog observation records its own read-only basis (`mode=ro` URI + `PRAGMA query_only=ON`) and
  the before/after `(bytes, mtime)` equality inside the same payload.

## Scope / safety statement

- Product code changed: **none**. `git status --porcelain -- tools` (revenue-forecast) and
  `-- src config scripts tests` (company-wiki) are both empty at V5.
- Production catalog: **opened read-only** (this card does require it — the state cells cannot be
  decided otherwise). `(bytes, mtime, -wal size)` identical before and after; every statement was a
  `SELECT`; the payload records `writes_issued: 0`.
- Production bytes: copied into `iso/catalog_root`, **never moved**; each original was re-hashed after
  the copy and still matches the manifest.
- Worker/provider/network: untouched. Downloads: zero.
- No `git add/commit/restore/stash` in any product repo.

## Open gaps / not verified

1. **No live "genuinely missing" sample.** Blocked, not NA. The isolated simulation is labelled
   `simulated_in_isolation` and must never be cited as live.
2. **No external-only, dayu-only or companies-only sample exists** in this frozen set; all three cells
   are blocked for concrete, different reasons.
3. **The provider document id for CN is taken from the file name only** (`1225023658`); unlike HK and US
   it was not cross-checked against a provider registry in this card.
4. **`is_artifact_stale` is bound on a producer-declared flag**, not on an independently recomputed
   expectation. Whether `partial` should force a recompute is an I-02/I-05 decision.
5. **The isolated catalog is a minimal schema**, not a copy of production (see `decision.md` J1). No
   resolve was run against it.
6. **`multi_root_same_bytes` is bound from the production census** (20 hashes, top row spanning
   `company_raw`, `dayu_portfolio`, `dropbox_stock`), but the card's requirement that "多根不冒充only"
   is only *recorded* here; the resolve-time consequence is I-07-B/I-07-C.
7. **The 49.7 GB catalog was not integrity-checked.** `PRAGMA quick_check` was deliberately not run
   (full-file scan); the no-write witness is `(bytes, mtime, WAL)` plus the absence of any write
   statement in the helper module.

## reviewer: attack first

1. Re-derive one raw sha256 yourself and confirm it equals `after/rehash.json` **and** the plan
   manifest; then confirm the urn is built from that hash and not from a filename.
2. Confirm the catalog was genuinely read-only: compare `before/snapshot.json` and
   `after/snapshot.json` (`bytes`, `mtime_iso`, `wal_bytes`) and check `after/observe_readonly.json`
   records the read-only URI.
3. Confirm the CN multi-root fact by reading the three location rows for the CN document id in
   `after/observe_readonly.json` — and confirm the helper never issued a DELETE.
4. Attack the `not_applicable == 0` claim and the blocked reasons: any cell whose reason reduces to
   "out of scope" rather than a concrete missing precondition is a defect.
5. Decide J1/J2 in `decision.md`; both change which cells count as bound.
6. Confirm the isolated copies are byte-identical to their sources and that the production originals
   still exist (`iso/isolated_state.json:copied[].source_still_present_after_copy`).

---

## r2 — disposition of the independent review's findings (APPEND-ONLY)

The independent review returned **accepted_scoped** with six non-blocking corrections. All six are
dispositioned below; the frozen oracle (`oracle.md` §1–§6) was **not** edited — the corrections are
recorded in `oracle.md` §7 and machine-readably in `after/state_matrix.json:r2_corrections`.

| # | sev | the finding | file:line | disposition |
|---|---|---|---|---|
| F-I07A-01 | medium | `config.legal_fifth_root` was `bound` on a program structure, and its reason claimed "the production roots table registers all four root ids" — a program output, not a SELECT | cell in `harness/i07a_matrix.py` (`legal_fifth_root`); original evidence `after/observe_readonly.json:roots` | **ACCEPTED.** Cell downgraded to **`planned`**. The roots table is now recorded as SQL **with its output** (`after/r2_review_facts.json:roots_table` — 4 rows, `future_lake` included) plus per-root location counts (`company_raw` 33092 / `dayu_portfolio` 3660 / `dropbox_stock` 9853 / `future_lake` 1). Ingest feasibility left with I-07-C. **Correction to the r1 review's mechanism, already conceded by the reviewer in r2:** r1 stated `future_lake` has *0* location rows; **corrected — the catalog has exactly 1** (`future_lake/README.md`, 545 bytes, `observed_size 545`, `document_id …sha256:66a9aff6…edaca`, `document_kind broker_research` — note `broker_research`, not `broker_repository`; the on-disk file hashes to 545 B as recorded). Only a `relative_path NOT LIKE '%README%'` filter yields 0. The r2 review confirmed this was its own query/read defect, not a catalog fact. The disposition never depended on it: a placeholder README is not ingest capability. See `oracle.md` §7 / §8 "Reviewer-claim divergence". |
| F-I07A-02 | medium | the multi-root census carried `LIMIT 20` while the write-up presented 20 as the total | `harness/i07a_helpers.py:358` (`LIMIT 20`) and `:365` (documents census) | **ACCEPTED.** Reported **untruncated: 3440** content hashes with ≥2 distinct roots (3436 documents) — a ~172× undercount in the first pass. The first-pass query is relabelled top-20-of-many in `state_matrix.json:r2_corrections.F-I07A-02`, and the untruncated total now appears in the `source.multi_root_same_bytes` cell text. The r2 review reproduced **3440** independently with its own SQL (`GROUP BY l.source_id HAVING COUNT(DISTINCT l.root_id) >= 2`), matching both of this attempt's counting methods, and confirmed the "172×" figure survives undiminished in all four places that state it. |
| F-I07A-03 | low | the isolated catalog is not production-isomorphic (production 18 tables vs iso 5; 5/5 `CREATE` differ) | `harness/i07a_helpers.py` schema block (`CREATE TABLE` ×5); `CW/src/company_wiki/source_catalog/store.py` (18 unique tables) | **ACCEPTED as scoped-usable (J1)** with an explicit prohibition added: `state_matrix.json:isolated_catalog_prohibition` states the iso catalog cannot carry a resolve or a registration and **must not** be reused by I-07-B, which must bind a production-isomorphic or table-filtered catalog (as I-00-B's `isolated_binding_plan` already contemplates). |
| F-I07A-04 | low | case-02 had no isolated build of its own | `harness/i07a_matrix.py` (`case02` record); `iso/cases/case-02-present-unregistered/state.json` | **ACCEPTED as a documentation fix.** The record now carries `record_type: "OBSERVATION RECORD, NOT an isolated build"` and `isolated_catalog_rows_for_this_case: 0`. No fabricated rows were added: this state is *defined* by the absence of registration rows, so inventing them would create a false record. |
| F-I07A-05 | low | the `companies_only = blocked` reasoning should state the disproval explicitly | `after/r2_review_facts.json:cn_sample_locations` (SQL + 3 rows) | **ACCEPTED.** Recorded in the cell reason and in `case-01…/state.json:derived_state.source_only_qualification.uniqueness_disproved_by_SQL`: the CN content hash is an `original_primary` location under **both** `company_raw` and `dropbox_stock`, each `observed_size 79925886`. Any product document or code path presenting CN as a companies-only unique source is contradicted by this evidence. |
| F-I07A-06 | low | the dimension count was stated inconsistently | `oracle.md` §3 and §7; `implementation_plan.md:131-139` vs `:141`; `state_matrix.json:dimension_alignment` | **ACCEPTED as documentation, and the r1 phrasing is corrected here.** The plan's table at `implementation_plan.md:131-139` has **seven rows** (市场/文件状态/来源/工件/请求/配置/故障) — the r1 wording "six plan dimensions" was wrong. Line 141 adds an eighth family, `generality`, whose cells belong to none of the seven. Implemented: **8 dimension families, 29 cells**. Authoritative record: `state_matrix.json:dimension_alignment` (`plan_table_rows.count = 7`, `implemented_dimension_count = 8`). |

### J1 / J2 rulings applied

- **J1** (isolated catalog semantics): accepted as **scoped usable**, with the prohibition above now
  explicit. The minimal schema was **not** replaced with a filtered production copy — that copy is an
  I-07-B prerequisite and building it here would duplicate 49.7 GB of production state for a
  documentation card.
- **J2** (fifth root): **cell downgraded to `planned`**, as the review ruled. `decision.md` originally
  argued for `bound` at existence+declaration level; that position was **overruled**, and `decision.md`
  now carries an append-only r2 section stating the ruling so a successor who reads only `decision.md`
  cannot act on the withdrawn claim.
- **J3 / J4** were not challenged and stand as written in `decision.md`.

### r2 follow-up (P1–P3): document-consistency fixes

The r2 re-read returned **changes_required for document consistency only** — the matrix, the evidence
and all four accepted corrections passed (the reviewer independently reproduced 3440 with its own SQL,
confirmed the "172×" figure in all four places, confirmed the iso-catalog prohibition in both places,
and conceded that the r1 "0 future_lake locations" claim was its own query defect: the catalog has
exactly 1). Three text defects were fixed, with **no cell state and no number changed**:

| # | defect | fix |
|---|---|---|
| P1 | `decision.md` had not been touched by the r2 pass and its §J2 still read "the fifth root counts as `bound`" — a successor following `review_and_handoff.md` reads `decision.md` first and would have found the opposite of the card's conclusion | appended an r2 section to `decision.md` (original §J1–§J4 left byte-intact) that marks §J2 **OVERRULED**, states `planned`, and points at this file's J1/J2 ruling |
| P2 | this file's F-I07A-06 row said "six plan dimensions", contradicting `state_matrix.json:dimension_alignment` (7 rows) and `state_matrix.md` ("8 dimensions") | the row now says **seven rows (plus the line-141 `generality` obligation)** |
| P3 | this file's F-I07A-01 row quoted the review's "*0* location rows" claim without the correction, while `state_matrix.md` already said "exactly one" | the row now states the correction inline: **1 row** (`future_lake/README.md`, 545 B, `broker_research`) |

`oracle.md` §7 is inside the append-only errata block and its frozen body was **not** edited; the
dimension-count correction for the frozen §3 line is carried by `state_matrix.json:dimension_alignment`
and by the F-I07A-06 row above (see also the "frozen text correction" note in `oracle.md` §8).

### Reviewer's remaining un-verified list — carried forward verbatim, NOT treated as proven

The r2 review listed eight items it did **not** verify. They are reproduced here so no successor reads
them as established:

1. the per-root location counts were not recomputed row by row;
2. only the first row of the r2 census top-5 was checked;
3. the US-MSFT raw artifact was not re-hashed by the reviewer;
4. the resolve path remains unmeasurable in isolation (no live resolve was run);
5. the `state.json` sub-fields were not checked field by field;
6. the r2-produced evidence cannot be externally anchored (it is this attempt's own output);
7. the substantive merits of D1 are outside the reviewer's scope;
8. the r1 re-run conclusions remain valid only because the tool's bytes did not change.

### Limited reservation accepted (not blocking)

`after/snapshot.json` was captured at `2026-09-20T02:14:43Z`, when the parent agent had not yet deleted
the leaked `git_filing-fetch.txt`; its `porcelain["filing-fetch"] = ["?? git_filing-fetch.txt"]` is
therefore **stale but conservative**, while `porcelain_product_only["filing-fetch"]` is correctly empty.
It is not a fabricated value. This was not refreshed: a re-run would be a new command and the value is
already the stricter one.

### Superseding counts

**bound 9 / planned 15 / blocked 5 / not_applicable 0** (29 cells, 8 dimension families). The five
blocked cells are unchanged; the only move is `config.legal_fifth_root` from bound to planned. All
V-checks still pass except `V6_generality_cell`, which is `blocked` by design.

### New evidence from this pass

| id | command | raw rc | result |
|---|---|---|---|
| V7 | `harness/i07a_r2_review_facts.py` → `after/r2_review_facts.json` (read-only; `mode=ro` + `PRAGMA query_only=ON`) | **0** | roots SQL (4 rows), per-root location counts, CN location SQL (3 rows incl. two `original_primary`), multi-root totals 3440 / 3436, untruncated top-5; catalog `(bytes, mtime, wal)` unchanged |
| V5′ | `harness/i07a_helpers.py snapshot --out after` (re-run after V7) | **0** | anchors, heads and product-only porcelain still identical to V0 |
