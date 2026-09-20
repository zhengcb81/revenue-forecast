# I-07-A oracle.md — FROZEN BEFORE ANY RUN

Card: `PLAN/execution_v2/card_I-07-A.md` (固定样本与前置状态建档)
Parent obligation: `PLAN/implementation_plan.md` item **I-07** (fixed matrix + new-sample rotation; the six dimensions)
Dependency: **I-00-B is the binding baseline** (`execution_runs/I-00-B/a20260919-01/{binding.json,review.md}`) — sample identities/hashes are reused read-only.
Attempt: `a20260919-01`. Frozen at 2026-09-20 (local) / written before the first measurement command of this attempt.

> This file is the independent expectation. **No expected value below was produced by running the
> tooling under test**; the identities come from the plan's frozen `sample_manifest.json` and from
> I-00-B's rehash receipt, which this attempt re-derives independently (D1) rather than trusting.

## 0. Scope statement (what this attempt does and does not claim)

Delivers: the **frozen sample matrix** (dimension → cells → bound / planned / blocked with a concrete
reason each) plus **precondition-state archiving** for the three already-recorded samples, with real
hashes and an isolated catalog for the two manufactured states.

Does **not** claim: any prediction success, any live missing-sample qualification, any external-only
sample, any download, any production mutation. `blocked` is a first-class matrix value; an absent
external sample is **blocked**, never silently "not applicable" (§5, V7).

## 1. Ground rules (frozen)

- **R1 Identity over filename.** A sample matches only when the file bytes hash AND the request's
  `market` / `fiscal_year` / `document_kind` / `company_query` / `as_of_date` match the frozen
  manifest entry. A filename match alone is never a match.
- **R2 Read-only production.** Any production access is read-only. The production catalog is opened
  with SQLite `mode=ro` + `PRAGMA query_only=ON` (the product's own read-only path,
  `CW/src/company_wiki/source_catalog/store.py:551,556`). This attempt performs **no** INSERT /
  UPDATE / DELETE against production and does not delete or move any production copy.
- **R3 No downloads.** No provider call, no network fetch. Only the three already-present originals.
- **R4 States are manufactured only in the isolated catalog.** Copying production bytes into the
  attempt's own `iso/catalog_root` is a copy, not a move; the production file stays in place and is
  re-hashed afterwards to prove it.
- **R5 Simulation labels are honest.** Any state that this attempt fabricates is labelled
  `simulated_in_isolation` and may not be read as a live sample. The card says the third state
  ("确实缺失") for the existing samples is **only** an isolated simulation and must not be called a
  real live missing sample (`card_I-07-A.md` clause 3; `sample_manifest.json.unbound_live_samples`).
- **R6 as-of discipline.** The frozen as-of for old-failure recovery is `2026-09-18`. Capture times
  fetched after 2026-09-19 keep their **real** value. Historical reconstruction that the current
  contract cannot support is recorded as **not supported** — time is never back-filled
  (`card_I-07-A.md` clause 4; `sample_manifest.json.capture_rule`).
- **R7 External-only stays blocked.** No production copy is deleted to manufacture an only-location
  sample (`card_I-07-A.md` clause 5).
- **R8 No product edit.** company-wiki is read-only for this card. `git add/commit/restore/stash` is
  forbidden in all three product repos.

## 2. Frozen sample identities (from the plan manifest; re-derived in D1)

| sample id | market | FY | provider | raw path (production) | frozen raw sha256 (manifest) | frozen sidecar sha256 | frozen request sha256 |
|---|---|---|---|---|---|---|---|
| CN-ZIJIN-2025 | CN | 2025 | cninfo | `companies\紫金矿业\raw\financial_reports\annual\2026-03-20_cninfo_1225023658_紫金矿业集团股份有限公司2025年年度报告.pdf` | `01819e1c…f343d` | `7f7570fe…20b5` | `08fb9a92…1799` |
| HK-XIAOMI-2025 | HK | 2025 | hkexnews | `companies\小米集團－Ｗ\raw\financial_reports\annual\2026-04-28_hkexnews_12127452_2025年度報告.pdf` | `ffd73376…2da7c` | `8228741d…8da71` | `891b3261…7655c` |
| US-MSFT-2026 | US | 2026 | sec | `companies\MICROSOFT CORP\raw\financial_reports\annual\2026-07-29_sec_0001193125-26-323660_MICROSOFT CORP 10-K 2026-06-30.htm` | `e3de0053…ecfff` | `1cbfb1a2…abb6a` | `369f4682…f64d` |

`original_observation` recorded by the plan for all three: CN = "raw reusable; review/artifact
readiness incomplete"; HK/US = "raw saved; scan/registration failed". I-07-A's job is to turn those
prose observations into falsifiable state records. **None of the three is an "already-indexed"
assumption** — the indexed state must be observed per sample (V2), not inferred.

Provider document ids from the manifest: CN `1225023658` (from the filename only — see C4),
HK `12127452`, US `0001193125-26-323660`.

## 3. Frozen dimensions and cells

Dimension names follow `implementation_plan.md:131-139` verbatim (市场 / 文件状态 / 来源 / 工件 /
请求 / 配置 / 故障). Every cell gets exactly one of `bound` / `planned` / `blocked`, and every
non-bound cell must name a concrete reason. Sub-cells that the card text requires but the parent
table does not name (e.g. `not-applicable` artifacts, mixed periods) are kept because this card's
own note enumerates them.

### 3.1 市场 (market)

| cell | expected identity evidence | this attempt's status (frozen before runs) |
|---|---|---|
| A 股 (CN) | request `market=CN`, `company_query=601899`, FY2025, document_id urn carries the frozen sha256 | **bound** (real raw rehash; state observation V2) |
| 港股 (HK) | request `market=HK`, `company_query=1810`, FY2025, provider `hkexnews`, provider doc id `12127452` | **bound** (real raw rehash; state observation V2) |
| 美股 (US) | request `market=US`, `company_query=MSFT`, FY2026, provider `sec`, provider doc id `0001193125-26-323660` | **bound** (real raw rehash; state observation V2) |

Expected: 3/3 raw sha256 == manifest, 3/3 sidecar sha256 == manifest, 3/3 request sha256 == manifest,
and 3/3 request `(market, fiscal_year, document_kind, company_query)` == manifest. Any mismatch is a
**drift** finding, not a green.

### 3.2 文件状态 (file state)

| cell | expected | status |
|---|---|---|
| 已下载已索引 (downloaded + indexed) | a `documents` row whose `document_id` is the urn built from the frozen sha256, i.e. `urn:company-wiki:document:sha256:<sha256>`; plus `sources`/`locations` rows for the same content | **planned → observed in V2.** Frozen prediction: at most one of the three (CN 紫金) is indexed; the plan records HK/US as "scan/registration failed". A cell stays `planned` if no sample satisfies it. |
| 已下载未索引 (downloaded, not indexed) | raw bytes present and hash-matching; **0** rows in `documents` for that document_id | **bound** (real bytes + real read-only catalog query; whichever samples are not indexed become this cell) |
| 确实缺失 (genuinely missing) | no raw file on disk at the queried identity | **blocked for live** (all three originals are present; `sample_manifest.json.unbound_live_samples` leaves CN/HK/US-NEW-MISSING unbound). Manufactured only as `simulated_in_isolation` (V3). |

Zero-re-download requirement for the first two cells is **not** testable here without a live resolve
run; it is I-07-B's obligation (`card_I-07-B.md`). This attempt only freezes the state record that
I-07-B will consume — recorded, not claimed.

### 3.3 来源 (source / root)

| cell | expected | status |
|---|---|---|
| companies-only | the sample's only location row has `root_id=company_raw` and no other location row for the same `document_id` | **planned** (observed read-only in V2; "only" qualification needs a full location census) |
| dayu-only | only location row `root_id=dayu_portfolio` | **blocked** — root path `../dayu-agent/workspace/portfolio` exists but no sample in the plan manifest is bound to it; no identity frozen |
| 外部目录-only (external dir only) | only location row `root_id=dropbox_stock` or `future_lake` | **blocked** — `sample_manifest.json.unbound_live_samples[EXTERNAL-ONLY]` unbound; deleting other copies to manufacture exclusivity is forbidden (R7) |
| 多根同 bytes (multi-root, same bytes) | ≥2 location rows across distinct `root_id` for one `content_sha256`; uniqueness by hash, and multi-root must **not** be reported as "only" | **planned → observed read-only in V2** (a real multi-root hit is reported if the production catalog has one; otherwise `planned`) |

### 3.4 工件 (artifact)

| cell | expected | status |
|---|---|---|
| 有效 (valid) | an `artifacts` row with `status` indicating usable, whose `content_sha256` matches the row's recorded hash | **planned → observed in V2** |
| 缺失 (missing) | no `artifacts` row for a required role | **planned → observed in V2** |
| 版本过期 (stale) | artifact exists but generated by an older generator_version than the current one, or bound to a changed source hash | **planned → observed in V2** |
| 内容篡改 (tampered) | recorded `content_sha256` ≠ actual bytes on disk | **planned → detected read-only in V2 if present** (detection is a hash comparison, no write) |
| 不适用 (not applicable) | role legitimately not required for that document kind | **planned → observed in V2** |

Reading artifacts is `SELECT`-only. No minimal recomputation is performed in this card (that is
I-02/I-05 scope); this card only freezes the state that a later card must act on.

### 3.5 请求 (request)

| cell | expected | status |
|---|---|---|
| exact | request carries `fiscal_year`; resolve asks exact | **planned** (execution is I-07-B) |
| latest | request uses `mode=latest_as_of` with an `as_of_date` | **planned** |
| 新修订 (new revision) | a newer revision of the same identity is selected; no future information used | **planned** |
| 混合期间 (mixed period) | ambiguous period must be reported as ambiguous, not silently guessed | **planned** |
| 重复 (duplicate) | repeated request is idempotent and the second call fully reuses | **planned** |
| 并发 (concurrent) | concurrent identical requests do not double-download or corrupt | **planned** |

Only the **frozen request artifacts** are in scope here: the three `requests/*.json` files are
hash-verified (V1) so the later cards run against a pinned request. No resolve is executed.

### 3.6 配置 (configuration)

| cell | expected | status |
|---|---|---|
| 安装入口 (installed entry) | the installed `revenue`/skill entry resolves the same modules as the repo checkout | **planned** — belongs to I-16-A (`card_I-16-A.md`); this card only records the entry the future card must bind |
| 生产配置副本 (production config copy) | an isolated config whose semantic content equals the production config, with `catalog_dir` pointed at the isolated catalog | **bound** — produced by V4 (copy + path rebind, production file untouched) |
| 合法第五 root (legal fifth root) | a root declared by config only, `kind: directory` + `adapter_id: sidecar_filing_v1`, `read_only: true`, no product code change | **bound (existence + config declaration)** — `CW/config/source_catalog.yaml` declares `root_id: future_lake` at `path: ${PROJECT_ROOT}/future_lake`; V4 records the path's existence and the config hash. Whether the adapter actually ingests is **planned** (I-07-C scope). |

### 3.7 故障 (fault)

| cell | expected | status |
|---|---|---|
| provider 失败 | provider error is preserved raw and never reported as success | **planned** (needs live provider; I-07-D) |
| scan 失败 | scan failure is recorded as failure; registration does not silently succeed | **planned** (I-07-D) |
| DB 锁 (DB lock) | a locked DB produces a clear error, no partial write | **planned** (I-07-D) |
| 进程中断 (process interruption) | interruption is recoverable; no false success | **planned** (I-07-D) |

This card freezes **the cells and what would count as evidence**; it does not inject the faults. A
card that ran a fault injection here would be running I-07-D out of order.

## 4. Frozen command expectations (indices used in `commands.json`)

| id | what it does | expected rc | expected business result |
|---|---|---|---|
| V0 | capture production catalog `(size, mtime, -wal/-shm presence)` + all three repos' `HEAD`/`porcelain` + the sha256 of every anchor file | 0 | before-state recorded; nothing written |
| V1 | rehash all three samples (raw + sidecar) and the three request files; compare against the manifest constants in §2 | 0 | `all_match=true`; identity fields match §2; any mismatch ⇒ `all_match=false` and the finding is reported, not hidden |
| V2 | read-only observation of the production catalog for the three frozen document ids (documents / sources / locations / artifacts / assertions) + the full multi-root census | 0 | counts recorded per sample; each of §3.2/§3.3/§3.4 resolved to bound/planned/blocked with the observed numbers |
| V3 | build the isolated `iso/catalog_root` and manufacture the three state cases (`indexed_ok`, `present_unregistered`, `simulated_missing`) from **copies**; prove with hashes | 0 | each case directory has its own snapshot json; copy hashes == source hashes; the production originals still hash to §2 afterwards |
| V4 | copy the production `source_catalog.yaml` into `iso/config/` with `catalog_dir` rebound to the isolated catalog; record both hashes and the semantic diff | 0 | exactly one differing line (`catalog_dir`); production config hash unchanged |
| V5 | post-observation integrity: re-hash the three production raw files, the sidecars, the production config, the catalog `(size, mtime, -wal/-shm)`; re-run `git status --porcelain` on all three repos | 0 | byte-identical to V0; `porcelain` unchanged |

A **non-zero** rc anywhere is a raw finding. V1/V2/V4 are expected rc 0 because they are read-only;
V3 is expected rc 0 because it only writes under `<attempt>/iso/`.

## 5. Frozen falsifiable checks (the card's acceptance conditions, restated as V-checks)

- **V-check 1 (state is verifiable from file+hash):** for each sample, `documents`-row existence must
  agree with "raw bytes exist AND hash matches the urn". A sample whose bytes are absent but whose
  `documents` row exists (or vice versa) must be reported as an inconsistency, not smoothed over.
- **V-check 2 (simulation vs live are labelled separately):** every state json carries
  `"state_origin": "live_production_observation"` or `"simulated_in_isolation"`. A simulated state
  claiming live origin is a failed check.
- **V-check 3 (missing is blocked, not NA):** the live genuinely-missing cell must appear as
  `blocked` with a reason string, and no cell in this attempt may be marked
  `not_applicable` without an explicit justification string.
- **V-check 4 (no production mutation):** production catalog `(size, mtime)` and the three raw/
  sidecar hashes and `git status --porcelain` are byte-identical before/after. The 49.7 GB catalog is
  **read-only at most**; this attempt does query it read-only (V2) and must say so.
- **V-check 5 (as-of discipline):** the three frozen requests keep `as_of_date = 2026-09-18`; no
  capture time is rewritten. If a state cannot be reconstructed under the current contract, the
  record says `historical_reconstruction_supported: false` rather than inventing a time.
- **V-check 6 (generality cell):** the plan requires a company/file **not** appearing in fixture
  names (`implementation_plan.md:141`). This attempt cannot bind it (no such sample is frozen and no
  download is allowed) ⇒ **blocked** with that reason, and listed as a residual for I-07-C.
- **V-check 7 (no silent NA):** the count of `not_applicable` cells must be 0 unless accompanied by a
  written justification; the count of `blocked` cells must equal the number of unbound live samples
  the plan declares (CN/HK/US-NEW-MISSING, EXTERNAL-ONLY, HELDOUT-COMPANY) plus any cell blocked by a
  missing prerequisite discovered in V2.

## 6. Reviewer attack list (frozen before results)

1. Re-derive at least one raw sha256 yourself and confirm it equals the value in `binding.json` and
   in the plan's `sample_manifest.json`; then confirm the urn is built from that hash and not from a
   filename.
2. Confirm the production catalog was opened **read-only**: re-run the `-wal`/`-shm` mtime check and
   the `(size, mtime)` comparison in `after/` against `before/`; a WAL bump would be a real defect.
3. Confirm `simulated_missing` is labelled as simulated and that the production file for the same
   identity still exists and still hashes to §2.
4. Check the `not_applicable` count is 0 (or justified), and that every `blocked` cell names a
   concrete reason — attack any cell whose reason is "not applicable" or "out of scope".
5. Attack the fifth-root claim: `future_lake` is declared in config and its directory exists — is
   that enough to call the cell `bound`, or should it be `planned`? The implementer's position is
   stated in §3.6 (existence + declaration = bound; ingestion = planned). Disagreeing is a valid
   review outcome.

---

## 7. Errata and review dispositions (APPEND-ONLY — frozen oracle left intact above)

The independent review returned **accepted_scoped** for this card's evidence scope with six
non-blocking corrections. Nothing in §1–§6 above was edited; every correction is recorded here and
in `after/state_matrix.json:r2_corrections`. Two of the six changed a cell state, so the frozen counts
in §5's V-check 7 are superseded by the table below.

| # | severity | correction | disposition |
|---|---|---|---|
| F-I07A-01 | medium | `config.legal_fifth_root` was `bound` on a program structure, and its reason asserted "the production roots table registers all four root ids" (a program output, not a SELECT) | **cell downgraded to `planned`**; the roots table is now recorded as SQL with its output, plus per-root location counts (`after/r2_review_facts.json:roots_table`, `:root_location_counts`) |
| F-I07A-02 | medium | the multi-root census carried `LIMIT 20` and both `review.md` and `state_matrix.md` wrote "20" as if it were the total | **reported untruncated: 3440** content hashes with ≥2 distinct roots (3436 documents); the first pass is relabelled top-20-of-many with the ~172× undercount stated (`after/r2_review_facts.json:multi_root_same_bytes_total`) |
| F-I07A-03 | low | the isolated catalog is not production-isomorphic (production 18 tables vs iso 5; 5/5 `CREATE` differ) | J1 accepted as scoped-usable; an explicit **prohibition** is now recorded in `state_matrix.json:isolated_catalog_prohibition`: it cannot carry a resolve or a registration and I-07-B must bind a production-isomorphic (or table-filtered) catalog |
| F-I07A-04 | low | case-02 had no isolated build of its own | relabelled an **OBSERVATION RECORD** (`record_type`, `isolated_catalog_rows_for_this_case: 0`); no fabricated rows were added, because inventing registration rows for a state defined by *absence* of registration would be a false record |
| F-I07A-05 | low | `companies_only = blocked` accepted, but the disproval must be written out | recorded with SQL: the CN content hash is an `original_primary` location under **both** `company_raw` and `dropbox_stock`, each `observed_size 79925886`; any product document/code claiming CN is a companies-only unique source is contradicted by this evidence |
| F-I07A-06 | low | six plan dimensions vs seven implemented | kept; `state_matrix.json:dimension_alignment` now states that `implementation_plan.md:131-139` names six rows while line 141 adds the `generality` obligation, whose cells belong to none of them |

### Reviewer-claim divergence recorded (not silently accepted)

F-I07A-01's correction stated that `future_lake` has **0 location rows**. The catalog says otherwise:
there is exactly **1** row — `future_lake/README.md`, 545 bytes, `location_status active`,
`document_id` NOT NULL, its `documents` row `document_kind = broker_research`, `title = README`. Only a
`relative_path NOT LIKE '%README%'` filter yields 0. The reviewer's stated **mechanism** therefore does
not match the catalog, but the recommended **disposition** is adopted unchanged, because a placeholder
README is not filing-ingest capability: the cell is `planned` either way. Recorded in
`state_matrix.json:r2_corrections.F-I07A-01.reviewer_claim_check`.

### Superseding counts (replaces §5 V-check 7's numeric expectation)

**bound 9 / planned 15 / blocked 5 / not_applicable 0** (29 cells, 8 dimension families:
the plan's 市场/文件状态/来源/工件/请求/配置/故障 plus `generality`). The five blocked cells are
unchanged and each still names a concrete missing precondition; `not_applicable` remains 0.

### New evidence produced by the correction pass

| id | command | raw rc | result |
|---|---|---|---|
| V7 | `harness/i07a_r2_review_facts.py` (read-only, `mode=ro` + `query_only=ON`) | 0 | roots SQL (4 rows incl. `future_lake`), per-root location counts (company_raw 33092 / dayu_portfolio 3660 / dropbox_stock 9853 / future_lake 1), CN location SQL (3 rows), census totals (3440 / 3436), untruncated top-5; catalog identity unchanged |

## 8. Frozen-text correction note (APPEND-ONLY; the §1–§6 body above is unchanged)

The frozen body of this oracle contains **two statements of the dimension count that are wrong**, and
the r2 re-read required them to be corrected without touching the frozen text. They are corrected here;
the authoritative record lives in `state_matrix.json:dimension_alignment`.

| frozen location | what it says | correct value |
|---|---|---|
| `oracle.md:4` (header, in §0's preamble) | "the **six** dimensions" | `implementation_plan.md:131-139` has **seven** table rows: 市场 / 文件状态 / 来源 / 工件 / 请求 / 配置 / 故障 |
| `oracle.md:223` (F-I07A-06 row inside this append-only §7) | "`implementation_plan.md:131-139` names **six** rows" | **seven** rows; `implementation_plan.md:141` adds an eighth family, `generality`, whose cells belong to none of the seven |
| `oracle.md:211` (first line of §7, inside this append-only block) and `review.md:133` (first line of its r2 section) | "…with **six** non-blocking corrections" / "six non-blocking corrections" | **Not a dimension count and NOT an error.** Both sentences count *findings* (F-I07A-01…06 = six findings). They are retained as the r2 original wording. Because the same §7 table contains the corrected dimension wording two rows below, a successor could misread `:211` as a dimension count — so: **for any dimension/row-count question, this §8 and `state_matrix.json:dimension_alignment` (7 plan rows / 8 implemented families / 29 cells) are authoritative, never the word "six" anywhere.** |

Implemented families: **8**; cells: **29**. The counts of bounded/planned/blocked cells above are
unaffected — only the description of the plan's table was wrong. A successor should read this note
rather than the two lines it corrects. (Review residue N1 closed here.)

### Additional reviewer concession confirmed

The r2 review confirmed that its earlier claim — that `future_lake` has 0 location rows — was a defect
in **its own** query/reading, not a catalog fact. The catalog has exactly 1
(`future_lake/README.md`, 545 B, `observed_size 545`, `document_kind = broker_research` — **not**
`broker_repository`). This is recorded so the divergence in the section above is not later misread as an
unresolved dispute: it is resolved, in the catalog's favour.

