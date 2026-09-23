# I-07-C — independent reviewer report (card I-07-C / attempt a20260923-01)

- **Card**: I-07-C 跨根与未知公司泛化 · **Attempt**: `execution_runs/I-07-C/a20260923-01` · **Reviewer**: independent session dispatched by parent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`.
- **Method**: sampled independent re-measurement of the dispatch's sections A–D plus the card's clause-5 holdout (which this review executes under clause 5 authority). Tools: `read` / `grep` / `pwsh` only. RF/CW/FF product trees READ-ONLY; runs only into `%TEMP%`; no state-changing git (no git command run at all); no network call made (the holdout uses registered local data only) （域：本 review 自身发起的全部工具调用与运行）.
- **This review's own writes = exactly**: (1) `<ATTEMPT>/reviewer_report.md`, (2) `<ATTEMPT>/reviewer_report.sha256`, plus (3) holdout/clause-5 artifacts under `<ATTEMPT>/evidence/reviewer_holdout/` — declared here as clause-5 reviewer authority （域：本 attempt 目录内的上述三类文件；product trees and all other plan files untouched）.
- **Verdict line location**: this file, `## VERDICT` heading below (rationale follows it).

## VERDICT — `accepted_scoped` (signed by this reviewer; implementer never signs)

Scope of the acceptance (域：本卡所测的 C 层隔离格 + 我执行的 clause-5 holdout；不授予 L 层、准确性、三市场总体通过):
per-cell signed/blocked status is transcribed in §B6 with my holdout result appended; FINDING C1 is accepted as a **downstream finding** (adapter_dispatch drops remediation reasons → `locations.error=NULL`), routed to the REMEDIATION ledger, **fix NOT this card's surface**; inherited carries F1/F2/F3 + the three verbatim exit declarations + `overall_three_market_pass=false` + zero-RevenueSourceRecord travel with this acceptance; isolated-tree cleanup (`%TEMP%\i07c` + this attempt dir) authorized **after** landing, per `recovery/README.md`; parent action = batch commit + next chain card **I-07-D**.

---

## A. Deliverable re-hash (live, at review time)

| deliverable | dispatch pin | my live sha256 | ok |
|---|---|---|---|
| oracle.md | `b051135a…` | `b051135a17c6f1f94913da445857c5db827ec167ed2abed6c9a6214c84e9d253` | ✓ |
| binding.json | `d820a3fb…` | `d820a3fb75da2461941414f2097e492fe052d61a2337a7838040d75866516e6e` | ✓ |
| commands.json | `6be2131d…` | `6be2131ddcc9dfc239111a97be52a25cc5a21128166ffd750b42197d2812da43` | ✓ |
| decision.md | `6e6f4f40…` | `6e6f4f40079e365974fbab522967fb2c5b252060f6554c4b4fe3f67729045452` | ✓ |
| changes.diff | `e81a33f9…` | `e81a33f9f028b9f2e2f4ea0e653162eff646076a7eab9dc6d6e296aefa187c1c` | ✓ |
| handoff.json | `72c1e853…` | `72c1e853f4864bc7d9640b94a1fdf7f7d3ad14497ab7e6d10b323bc0d719ac34` | ✓ |
| recovery/README.md | `5ca0c271…` | `5ca0c271c83227b75a921a59ef283d23a364d5beed4f4c876f9af525d0dabd86` | ✓ |
| evidence files | 108 claimed | **108 files live (count)** | ✓ |

- **Frozen-first (oracle)**: `oracle.md` CreationTime = LastWriteTime = **2026-09-23 14:11:33** local; binding 14:12:47; commands 14:13:35; earliest evidence file `snapshot_before.json` 14:29:55; earliest judged product run `X04/scan1` 14:31:28 ⇒ oracle frozen and never edited after the first judged run （域：文件系统时间戳 + 哈希一致）.
- **Evidence spot re-hash (all handoff-pinned files)**: snapshot_before `fa50ea02…`, snapshot_after `9c678120…`, snapshot_verdict `db666914…`, iso_final `feaa5664…`, x04_hash_verify `5fffaad5…`, no_hardcode_grep `7c2b83d7…`, non_fixture_grep `a8e5ad92…`, prod_census `c8973e9f…`, cell_summary `b8af73fa…`, X05 scan1/scan2 stdout `69b1c6a2…`/`9110df2a…`, X05 resolve1/resolve2 stdout `cc8e774b…`/`3f723869…`, UNK-adapter scan1 stderr `dbf42c99…`, UNK-kind scan1 stderr `b0547011…` → **15/15 match**; iso_initial `661cfc65… fa2c01f1… dda390a2… 0629804f… 584addbe… 011d0169… 70d527ca…` → **7/7 match** （域：本 attempt 内 handoff 点名的全部 evidence 文件）.
- **Matrix input**: `execution_v2/scenario_matrix.md` live sha `0dec23cd10f00efd6ad82cf923552bd46c1763bcf9f740422f51f4973292299f`, 6219 B == I-07-B pin == binding/handoff pins; rows **X01–X05 (+X06)** read verbatim and match the oracle's §0.1 quotes. `sample_manifest.json` = `d5d0bb92…` ✓; `card_I-07-C.md` = `c3c3f533…`, 14 lines ✓.
- **Zero product files changed**: `changes.diff` header `before=16 after=16 changed=[]`, samples `changed=[]`, catalog identity `changed=False`; **my own live re-hash of the same 16 anchors (RF/CW/FF source + production `config/source_catalog.yaml`) and of all 6 sample files (3 raw + 3 sidecar) = 0 mismatches, 0 missing** （域：snapshot.json 所列 16 anchors + manifest 3 samples 的 raw/sidecar，review 时刻实时重算）.
- **Handoff state**: `status: review_pending`, `implementer_signed: false`, `review_holdout.flag: "SEALED FOR REVIEWER"`, `exit_honesty_declaration_verbatim` byte-identical to oracle §2 and decision §0: 「每个格单独结论，无外部only实证就不签该资格；它不阻止与其无关的已验证本地读场景。」 ✓; the three inherited verbatim declarations present in handoff + decision ✓ (recovery/README carries the third, the recovery rule, by design).
- **`HELDOUT-COMPANY`**: appears only as the manifest key/flag in binding/decision/handoff/oracle; the manifest entry carries `{id, status: unbound, rule}` with **no identity fields** — nothing existed for the implementer to know (oracle attack item 6 ✓) （域：本 attempt 全部文件 + sample_manifest.json 的该条目）.

### A2. Adapter-freeze integrity — oracle §0.2 vs product LIVE code (my own reads)

Every cited set/line confirmed at the live file (hashes also match `binding.json.product_adapter_dispatch`) （域：下表逐行引用的 oracle §0.2 行号）:

| claim | live confirmation |
|---|---|
| `adapter_dispatch.py:29-33` `_ADAPTER_FACTORIES` = exactly `{sidecar_filing_v1, company_raw_v1, dayu_filing_v1}` | ✓ read |
| `adapter_dispatch.py:39-53` `adapter_for` fail-closed: no adapter_id → `no adapter_id (2.x policy required)`; not registered → `not registered`; registered-not-scanner → `has no scanner adapter implementation` | ✓ read |
| `registry.py:10-21` admission profiles = exactly 2 (`financial_evidence_v1` providers `example-filing, dayu, sec, hkex, cninfo`, allows_filing, read_only_required; `generic_document_v1`) | ✓ read |
| `registry.py:23-48` 4 registered adapters, `generic_document_v1` at :42-47 (registered, not scanner-capable) | ✓ read |
| `config.py:127-131` CFG-01 `not registered (CFG-01)`; `:132-136` CFG-02; `:113-115` unknown fields; `:166` `kind=str(item.get("kind",""))` (kind NOT validated here) | ✓ read |
| `models.py:39` `ROOT_KINDS = frozenset({"company_raw","directory","dayu_portfolio"})`; `:141-142` `unsupported root kind` | ✓ read |
| `scanner.py:855` `use_adapter = v2_scan_shadow or root.adapter_id is not None` (+ :856 strategy) | ✓ read |
| `scanner.py:1941-1953` adapter branch → `v2 scanner unavailable (fail closed)` / `fail closed, no legacy fallback`; `:866-884` per-ROOT fail-closed with `scan_root_strategy: …` | ✓ read |
| `store.py:136-142` `sources.content_sha256 TEXT NOT NULL UNIQUE` | ✓ read |
| `scanner.py:1046` `INSERT OR IGNORE INTO sources`; `:83-84` `document_id = urn:company-wiki:document:sha256:<tail>`; `:1089-1091` `locations … ON CONFLICT(root_id,relative_path)` | ✓ read |
| `sidecar.py:5-7` "Missing fields degrade to indexed_only with an exact remediation reason — never guessed from the filename (F-043)" | ✓ read (see C1) |

---

## B. Per-cell re-verification (my own execution where the card requires it)

### B1. X04 multi-root (SIGNED cell) — my re-verification
- **Both fixture copies re-hashed live**: `companies/…2025年度報告.pdf` and `companies_mirror/…2025年度報告.pdf` → each **4,405,561 B**, sha `ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c` == manifest pin; sidecars each `8228741d…` == `x04_hash_verify.json` （域：该 cell 两份 fixture 副本）.
- **My own sqlite query on the isolated catalog** (`mode=ro` + `PRAGMA query_only`): `sources` for that content_sha = **1** (table total 2 — the 2nd row is the sidecar's own bytes), `documents` = **1**, `locations` for that source_id = **2** with distinct `root_id` `{companies_root_a, companies_root_b}`, same relative path, both `role=original_primary / location_status=active / observed_size=4405561`, `error=NULL` ⇒ claim **sources=1 / documents=1 / locations=2 confirmed by me**.
- **My own re-run of their documented resolve** (frozen `argv.json`, cwd = cell cwroot, outputs into `%TEMP%\i07c\reviewer\x04\`): **rc 0**, `status: reused_equivalent`, **`reason: one_existing_source_satisfies_semantic_request`**, 1 match — identical to their `resolve1` (status/reason equal: true); my run changed **no catalog row count** （域：该 cell 的18表计数，我的运行前后）.
- ⇒ X04's C-level signature stands (signed at C).

### B2. X05 fifth-root (SIGNED cell) — my re-verification
- **Non-fixture claim recomputed independently** (my own script, their 12 scopes + their rules): `TOTAL FIXTURE/EXPECTATION MATCHES: 0`, `TOTAL UNIVERSE-DUMP MATCHES: 8`, `SCOPES WITH POSITIVE CONTROL HIT: 17`, `RECOMPUTED VERDICT: PASS` — reproduces their numbers exactly (1650 scope files at their exact skip-set; positive control 81/32/24 file hits for 紫金矿业/小米集團－Ｗ/MICROSOFT CORP).
- **The 8 disclosed security_master hits classified by me**: 4 distinct files — `filing-fetch\e2e\.runs\{biren-e2e-v1-08154ff2c106\run-1, run-2, biren-e2e-v1-9fb7f4276ba1\run-8, run-9}\.source_catalog\security_master\hk.json`, each **1,062,358 B**, each containing tokens `NOVO` and `NVO` ⇒ 4×2 = **8** hits; path markers (`.source_catalog`/`security_master`/`.runs`) justify their "securities-universe dump = data, disclosed" classification （域：这8个hit对应的4个文件；每文件2 token）.
- **Raws verified**: payload 265 B + sidecar 1,014 B carrying `source_url: https://example.invalid/…` (the J1 completion), full contract fields, `content_sha256 783b6bee…`; the other four roots hold **0 files** ⇒ "other four roots contribute 0 rows without errors" ✓.
- **J1 disclosure coherent**: run1 artifacts exist and are preserved (`scan1/` + `resolve1/` with all 5 files each); `resolve1` shows `debug_trace: [… capture_incomplete]`, `matches: []`, `outcome: missing` ✓; run2 captured alongside (`scan2/`, `resolve2/`).
- **scan2 report** (read): strategy `i07c_fifth_lake: "adapter"`, `errors: 0`, `files_seen 1`; catalog dump: 1 document / 1 source / 1 location under `i07c_fifth_lake`, entity `unresolved:i07c_fifth_lake` ✓.
- **My own re-run of their documented resolve2**: **rc 0**, `status reused_equivalent`, `reason one_existing_source_satisfies_semantic_request`, `outcome reused_existing`, `qualification {label: verified_input, gaps: []}`, `prompt_injection_status: not_reviewed` — same status/outcome as theirs; no catalog row-count change （域：X05 cell 18表计数）.
- ⇒ X05's C-level signature stands (signed at C), with J1/J2 run1 evidence intact.

### B3. Unknown layout (clause 3) + FINDING C1
- **My own re-execution of BOTH quotes** (their frozen argv, outputs into `%TEMP%\i07c\reviewer\unk\`), **stderr byte-identical to their evidence and rc identical (1)** in all four runs （域：我重跑的这4次 UNK 运行）:
  - `UNK-adapter` **scan**: rc 1, `company_wiki.source_catalog.config.CatalogConfigError: roots[0] adapter_id 'unknown_layout_v9' not registered (CFG-01)` (raised from `config.py:129`, loaded at `cli.py:868` — before the try).
  - `UNK-adapter` **resolve**: rc 1, same stderr.
  - `UNK-kind` **scan**: rc 1, `ValueError: unsupported root kind: unknown_layout_probe` at `models.py:142`.
  - `UNK-kind` **resolve**: rc 1, same stderr.
  (These two probes fail at config load ⇒ no catalog write; I therefore did **not** re-run the UNK-sidecar scan, to keep that cell's state intact for observation (d) — C1's substance was verified read-only.)
- **C1 substance verified by me**:
  - Promise: `adapters/sidecar.py:5-7` docstring ("exact remediation reason … never guessed from the filename (F-043)"); the adapter computes them at `sidecar.py:60` `evidence={"remediation": "missing_sidecar"}` and `sidecar.py:74` `evidence={"remediation": ";".join(problems)}` (`_validate_sidecar:90-119` yields `sidecar_parse_failed / missing_identity:* / missing:* / missing_provenance:* / content_hash_mismatch / path_escape:* / unknown_schema_version`).
  - Drop: `adapter_dispatch._to_scanner_candidate` (`:57-76`) builds `_Candidate(root, path, relative_path, group_key, role, entity_name, group_metadata=dict(item.normalized or {}), source_status)` — it copies `normalized` and **never `item.evidence`**, and never sets `error`; `NormalizedCandidate.evidence` exists (`adapters/interface.py:26`) and `_Candidate.error: str | None` exists (`scanner.py:67`) with the locations INSERT wiring `error=excluded.error` (`scanner.py:1099`) ⇒ the plumbing exists, the value is lost at the dispatch seam.
  - **Measured on the live isolated catalog (my own read-only query)**: all 4 probe locations → `role ∈ {original_primary, indexed_only}`, **`error = NULL`**, `metadata_json` contains no `remediation`; `documents.metadata_json` has no `remediation` key in `acquisition`, and the broken/no-sidecar documents carry `acquisition: null` ⇒ **evidence-not-copied confirmed; role-level explicit, reason-level invisible**.
  - **Severity (my classification)**: measured downstream product defect (observability of remediation causes), reproducible by quote; **NOT this card's fix surface** → route to the REMEDIATION ledger (card clause 3 asks only for explicit unsupported/no-guessing, which the load-time refusals satisfy — 域：clause 3 的要求范围). I concur with the implementer's C1 wording.

### B4. X01 / X02 conclusion scoping
- **X01**: my read of `scan1` (rc0, 2 files hashed, strategy `company_raw: legacy`) and `resolve1` (rc0, 1 match, `content_sha256 01819e1c…` == manifest pin, capture_ready true); decision's scoping quote — *production companies-only NOT signed because I-07-A measured CN uniqueness DISPROVED* — verified against **I-07-A carriers**: `handoff.json` blocked cell `source.companies_only`: "CN uniqueness empirically DISPROVED: the same content hash is an original_primary location under company_raw AND dropbox_stock, each observed_size 79925886"; `after/state_matrix.md` line 14 same wording; `after/r2_review_facts.json` holds the SQL. Decision's citation matches the carrier ✓ (cited, not overridden).
- **X02**: my read of `scan1` (rc0, strategy `dayu_portfolio: legacy`) and `resolve1` (rc0, 1 match, `content_sha256 e3de0053…` == pin, `entity_ids: [ticker:MSFT]`, `document_kind annual_report` via `form_type 10-K`, resolve reused); decision's *production dayu-only NOT signed — no frozen identity, census shows 3660 dayu locations* matches **I-07-A `handoff.json`**: "no plan sample is bound to the dayu_portfolio root (root has 3660 location rows but no frozen identity)" ✓ and the 3660 count matches my own census re-run (B5) ✓.
- Both cells signed **only at isolated-eligibility level** — correct scoping （域：X01/X02 两格的签署层级）.

### B5. X03 BLOCKED + census
- **Blocked wording (decision §1 row X03 + handoff per_cell)**: contains "BLOCKED (not NA)", the manifest unbound rule quote ("Reviewer selects and freezes identity/period/as_of/provider/raw-state … never delete production copies to manufacture absence"), "existence ≠ eligibility … exclusivity manufacture is forbidden", "no external-only 实证 ⇒ that qualification is NOT signed, and this blocked cell does not block the unrelated verified local read scenarios", and "No isolated construction was built for X03 (no tree exists)" — all four required elements present ✓. My check of `%TEMP%\i07c\cells\` shows **exactly 7 cells, no X03 tree** ✓ (attack item 5).
- **Census re-verified from their raw AND re-executed by me**: their `prod_census.json` (mode=ro + `PRAGMA query_only`, 6.3 s) = `company_raw 33092 / dayu_portfolio 3660 / dropbox_stock 9853 / future_lake 1`, `documents 23530`, `external_only_candidates 6411`. **I ran their three documented SQL steps myself** (same SQL text, same read-only mode, reviewer copy → `%TEMP%`) and got **33092 / 3660 / 9853 / 1, 23530, 6411 — identical**, and independently equal to I-07-A's r2 facts (33092/3660/9853/1) （域：production catalog 的这三步只读查询）.

### B6. Per-cell verdict table (transcribed from decision.md, my status appended)

| Cell | Clause | Level | Implementer conclusion | My status |
|---|---|---|---|---|
| X04 multi-root | 1 | C | CONCLUDED/signed: 1 source + 1 document + 2 locations, both copies == pin, resolve `one_existing_source_satisfies_semantic_request` | **SIGNED (independently re-verified: hashes + own SQL + own resolve re-run)** |
| X05 fifth-root | 2 | C | CONCLUDED/signed: unnamed root + non-fixture company completes scan(strategy=adapter) + resolve(reused_existing, verified_input); J1 disclosed, run1 kept | **SIGNED (independently re-verified: 12-scope grep recompute + raws + own resolve re-run)** |
| Unknown layout ×3 | 3 | C | CONCLUDED with FINDING C1 (load-time refusals explicit; remediation reasons dropped) | **CONCURRED; C1 re-verified live (4 own runs + code + catalog)** |
| X01 companies-only | 4 | C | ISOLATED eligibility signed; production companies-only NOT signed (I-07-A uniqueness disproved) | **SIGNED at isolated level (scoping verified vs carriers)** |
| X02 dayu-only | 4 | C | ISOLATED eligibility signed; production dayu-only NOT signed (no frozen identity) | **SIGNED at isolated level (scoping verified vs carriers)** |
| X03 external-only | 4 | none（域：该格的层级列原值） | **BLOCKED (not NA)**, documentary + census proof | **BLOCKED confirmed (no tree; census reproduced; wording complete)（域：X03 单格）** |
| **Clause-5 holdout (reviewer)** | 5 | C | not run by implementer (SEALED) | **executed by me — see §C** |

---

## C. Clause-5 HOLDOUT — reviewer-executed generalization test

### C0. Selection method (read-only, before any run)
Pool = every registered **active** `original_primary` location in the production catalog (`mode=ro` + `query_only`) with its sidecar/meta present, ≤ 25,000,000 B, across the three sidecar-shaped roots (company_raw 7,509 / dropbox_stock 9,211 / dayu_portfolio 49 such rows; pool = 10,596 after layout filters) — **census methodology, availability only, no big bytes opened before hashing the chosen small file**. Screening used the implementer's exact `non_fixture_grep.py` rules (12 scopes, text extensions, their skip dirs, 2 MB cap, universe-dump path markers = disclosed data, positive control = the three fixture company dir names; 1,650 scope files scanned, positive control 81/32/24 ✓). Identity tokens per their token groups = company name(s) + security id (provider ids NOT used — their `tokens()` does not include them).

### C1. FREEZE — recorded here BEFORE any product run (freeze time: this file, before `evidence/reviewer_holdout/{build,scan,resolve}*`)

**Reserved generalization sample (HELDOUT-COMPANY bound by this reviewer):**

- **Company**: 洛阳钼业 (CMOC Group) — security id/ticker **603993**, market CN.
- **Filing file (one)**: `C:\Users\郑曾波\Projects\dayu-agent\workspace\portfolio\603993\filings\fil_cn_783bede49b6c322ae6bf798648ffe487cd9c81e6\fil_cn_783bede49b6c322ae6bf798648ffe487cd9c81e6.pdf`
  - **bytes 6,610,553** · **sha256 `dfeb7c54c3b7c658030851fd406f538a28d4e9a9d04eac2eab8179854725e12a`**
- **Filing metadata (its own registered `meta.json`)**: same directory · bytes 2,802 · **sha256 `4f99016d21b246484ff134f25d4effc0c6ed90fffb11fa19e0bf279e197d92cb`**
- **Entity metadata (`portfolio/603993/meta.json`)**: bytes 241 · **sha256 `5ec07ea534544726b311eaf60fb0627e92289e1115f458c832ee8482d2a1f786`**
- **Registered real location (my own catalog query, mode=ro+query_only)**: root `dayu_portfolio`, `role=original_primary`, `location_status=active`, `observed_size=6610553`, `document_id=urn:company-wiki:document:sha256:dfeb7c54…`, `document_kind=annual_report`, `source_status=active`, `published_date=2022-03-18` (form `FY`, filing_date `2022-03-18`, fiscal_year 2021, provider `cninfo`, source_id `1212626342`).
- **Criteria evidence**:
  - (i) **absent from fixture/expectation scopes**: tokens `[洛阳钼业, 603993]` → `fixture_hits = {}` over all 12 scopes (1,650 files, their exact rules) and `named_in_attempt = []`; only disclosed universe-dump hits: `洛阳钼业` inside 4 `filing-fetch\e2e\.runs\…\.source_catalog\security_master\hk.json` files (their data classification); positive control PASSED on the same run.
  - (ii) **differs** from the implementer's fifth-root company 诺和诺德 and from every recorded rejected candidate (贵州茅台, 宁德时代/300750, 万华化学/600309, 000858, 600519) — none of these tokens is 603993/洛阳钼业 (screened out at pool build).
  - (iii) **real registered location confirmed read-only** (row above) and the file is small (6.6 MB); it is an `annual_report`, so the bound read-stage flag `--document-kind annual_report` is used unchanged.
- **Construction (their cell-harness pattern)**: isolated cwroot under `%TEMP%\i07c\cells\REVIEWER-HOLDOUT`, product-initialized 18-table catalog, four production-shaped roots rebound to isolation **plus** holdout root `reviewer_holdout_lake` = `kind: dayu_portfolio` + `adapter_id: dayu_filing_v1` + `admission_profile_id: financial_evidence_v1` + `read_only: true` + `reusable_for_filing: true` (all inside the frozen support set of oracle §0.2 — 域：oracle §0.2 的冻结支持集); REAL bytes + REAL registered meta copied in (identity read from those files at runtime — **no company literal exists in my builder**, verified by grep before running).
- **Declared expectation BEFORE running (honest, static)**: scan is expected rc0 with strategy `adapter` (registration generalization). The sample's own registered `source_url` is **`http://static.cninfo.com.cn/finalpage/2022-03-19/1212626342.PDF`** (http, not https), and `resolver.py:1919-1925` nulls non-`https://` URLs (`missing: https_url`) with `resolver.py:1570-1576` then tracing `capture_incomplete` and skipping the match ⇒ **the resolve arm is expected to come back `status: missing / reason: no_existing_source_satisfies_request`**. If measured so, it is recorded as a **MEASURED NEGATIVE with exact quotes — no sample swap** (a swap to a previously-successful company is forbidden by the card and by binding.forbidden).
- **Population note (measured during selection, domain: the 10,596 registered active ≤25 MB sidecar/meta-bearing rows)**: `criterion-(i)-eligible ∩ https-source_url-capable = 0`. Eligible rows = 6,443; https-capable rows = 20 (company_raw: Apple Inc, NVIDIA CORP, 北方华创, 微软, 比亚迪, 美團－Ｗ, 腾讯, 安踏體育 …) + 23 (dayu: MSFT, 1548, 2020 …) + 2 (dropbox) — **every** https-capable filing belongs to a company whose identity does appear in fixture/expectation scopes. This is finding **F-REV-7**.

### C2. Execution (my own runs; artifacts in `evidence/reviewer_holdout/`, 35 files)

Built and executed by me **after** the freeze in §C1 (cell `%TEMP%\i07c\cells\REVIEWER-HOLDOUT\cwroot`):
- **Build**: product-initialized catalog **18 tables** (`CatalogStore._initialize`), config sha `0723c803b7e59337086351eb2ea93796b9ad187ff6fa6227f6e9b3515b4de6db`; all three copies **`matches_freeze: true`** (raw `dfeb7c54…`, filing meta `4f99016d…`, entity meta `5ec07ea5…`); identity read from the copied files at runtime → `{"entity": "洛阳钼业", "document_kind": "annual_report", "as_of_date": "2026-09-23"}`. My builder carries **0 CJK hits and 0 company/ticker token hits** (one `annual_report` *document-kind* fallback literal exists — a kind, not a company identifier, disclosed).
- **SCAN arm — SUCCESS (generalization) — my execution**: product rc **0**, elapsed 1.712 s, `errors: 0`, `error_details: []`, `files_seen: 2`; the product's own scan report strategy =
  `{"company_raw":"legacy","dayu_portfolio":"legacy","dropbox_stock":"legacy","future_lake":"adapter","reviewer_holdout_lake":"adapter"}` ⇒ **the same adapter/profile dispatch ran** (`dayu_filing_v1` + `financial_evidence_v1`, both inside oracle §0.2's frozen set), **no product code changed** (16 anchors unchanged at close).
  Registered under the holdout root: **1 document** (`document_kind annual_report`, `source_status active`, `published_date 2022-03-18`, title `洛阳钼业2021年年度报告`), **1 source**, **2 locations** (`original_primary` + `metadata`, both `active`, both `error=NULL`), entity `unresolved:reviewer_holdout_lake`, `document_id urn:company-wiki:document:sha256:dfeb7c54…` (= the production document id for the same bytes ⇒ content-addressed identity held across roots).
- **RESOLVE arm — MEASURED NEGATIVE (exactly the pre-declared reason) — my execution**: rc **0**, **no catalog row-count change**, envelope verbatim:
  `status: missing`, `reason: no_existing_source_satisfies_request`, `resolution_envelope.outcome: missing`, `matches: []`, `qualification: null`, `download_allowed: false`, `download_required: true`, `prompt_injection_status: not_reviewed`,
  **`debug_trace: ["entity_gate_rejected: 0", "洛阳钼业2021年年度报告: capture_incomplete"]`**.
  Interpretation (quoted, not inferred): the **entity gate accepted the previously-unnamed company with 0 rejections** — identity anchored from the sample's own registered metadata, i.e. **(b) no company-name hardcoding was needed** — and the single exclusion is the capture gate on the sample's `http://` source URL, exactly as §C1 declared before the run. **No sample swap** (card/binding forbid it); recorded as a measured negative with quotes → feeds **F-REV-7**.
- **which-arm sha256 (my artifacts)**: `scan/stdout.txt 3052e569…`, `scan/result.json 3ced386e…`, `scan/argv.json 149099c1…`, `resolve/stdout.txt 52e76643…`, `resolve/result.json 42fd83a5…`, `resolve/argv.json 4c167001…`, `verify.json b6c0254c…`, `build.json efdc336a…` (full list in `evidence/reviewer_holdout/holdout_artifact_shas.json`).
- **(c) conclusion as my own execution**: the scan/resolve envelopes above are outputs of runs I launched from the frozen argv form (`<iso-python> -X utf8 -B -m company_wiki.source_catalog.cli --config <cfg> scan|resolve …`, cwd = the isolated cwroot, `PYTHONPATH=<CW>/src`, no `--allow-download`), captured by my builder — not copies of the implementer's evidence.
- Extra corroboration for observation (d): after this cell's **missing** resolve, `document_fingerprint_state = 0` (domain: my holdout catalog) — a second data point that a missing resolve does not create that row.

### C3. No-hardcode grep of the implementer's construction (clause-5 obligation) — recomputed by me
- **My independent recompute over the same 10 `harness/*.py` files (checker excluded)** with their token-derivation rule and their home-path masking:
  - **unmasked = 5 CJK matches**, at exactly the lines their run1 published: `i07c_common.py` L15/L16/L17 and `snapshot.py` L44/L45 — every one is a `C:\Users\<USERNAME>\…` absolute path （域：这5处未掩码命中） ⇒ **run1's 5 CJK hits are USERNAME path artifacts** (confirmed line-by-line) and are preserved as `no_hardcode_grep.run1_username_falsepositive.txt` (+ `no_hardcode_result.run1.json`).
  - **masked = 0 matches** across all 10 files, and **TOTAL 0** ⇒ reproduces published `no_hardcode_grep.txt` (`7c2b83d7…`, "3 mask(s)").
  - Extra probes by me: `NVO`, `Novo Nordisk`, `诺和诺德`, `i07c_fifth_lake` occur **0 times in all 10 harness .py files** (raw counts, domain: the same 10 files).
- **Documentation defect (F-REV-4)**: decision §5 lists `NVO` among the patterns "601899, 1810, MSFT, 12127452, 0001193125-26-323660, NVO, …"; the published pattern list has **7 tokens without `NVO`** (the checker's `len>=4` filter drops the 3-char ticker). My raw probe shows `NVO` is absent from those files anyway, so the PASS conclusion is unaffected — the pattern list in decision §5 is overstated (LOW).

---

## D. Disclosures & boundaries

- **J5 coherence**: `commands.json` pre-declared `expected_product_returncode` "0 for … UNK-kind …"; measured **1** (raw, both entries); oracle §1 3c hand-reasoned "config LOADS (config.py:166 does not validate kind)"; decision J5 + handoff `expected_exit_codes.product_negative_cases` record the deviation and its cause (`models.py:39/141-142` ROOT_KINDS missed at freeze); **oracle hash unchanged** (`b051135a…`, never edited) ⇒ story coherent: declared-vs-measured recorded raw, oracle untouched, refusal actually satisfies clause 3 ✓.
- **Three harness rc=1 events (spot)**: (3) prod_census run1 — **artifact preserved**: `prod_census.run1_threaderror.json` carries `status: PARTIAL`, `ProgrammingError: SQLite objects created in a thread can only be used in that same thread …`, mode `ro + PRAGMA query_only`, `catalog_bytes 49677344768`, and the fixed run2's numbers ✓. (1) first UNK-resolve attempts before `resolve_request.json` existed and (2) `summarize_cells` run1 KeyError — **declared in `handoff.raw_exit_codes` only; no run1 artifact exists for either** （域：rc=1 事件 (1)(2) 的证据留存） (grep for `KeyError` / "missing cell state" finds only the declaration). Recorded as partially evidenced (not a measurement defect: both failures wrote no evidence by definition).
- **Observation (d) — raw values + timing, and my discriminator probe**:
  - Live isolated catalogs (my read-only query): `document_fingerprint_state` = **1** in X05-fifthroot and UNK-sidecar; **0** in X01, X02, X04, UNK-adapter, UNK-kind — matches the implementer's claim （域：7个隔离catalog 的该表行数）.
  - Timing from their own dumps: X05 `scan1:0 → resolve1:0 → scan2:1 → resolve2:1`; UNK-sidecar `scan1:0 → resolve1:0 → scan2:1`. **The +1 does NOT appear at the missing resolve** (dump taken right after resolve1 = 0) — it appears at the **second scan**.
  - **My discriminator probe (my own run, their frozen scan argv, on the REUSED cell X01)**: fingerprint_state `0 → 1`, scan_runs `1 → 2`, `files_reused: 2`, rc 0 ⇒ **a second scan alone creates the row without any missing resolve**.
  - Cross-check of I-07-B's carrier: `S-CN-3/run3` shows `document_fingerprint_state 0 → 1` with `scan_runs` constant at 1 (entry = `RF/scripts/source_preparation.py`, run blocked by policy) ⇒ a third, scan-free trigger exists on the RF ensure path.
  - **Classification (refines, does not refute, the implementer's hedge)**: their wording is honest ("timing-consistent association, not proven causal"), but the suggested mechanism (*persistent-demand from a missing resolve*) is **not supported by I-07-C's own timing**: the missing resolves left the count at 0, and scan-count alone suffices. For the parent's inherited I-07-B open item: two triggers are now measured (a second CW scan; an RF source_preparation run) and the missing-resolve theory should be dropped unless a missing-resolve-only case is produced. Still **timing-consistent, causal unproven** for I-07-B specifically (its run3 has no scan, so its trigger is the RF ensure path).
- **Production catalog byte figure — discrepancy resolved by evidence**:
  - My live stat: **49,677,344,768 B**, mtime **2026-09-19T06:31:35.406919Z** (creation 2026-07-18).
  - Their records: `snapshot_before`/`snapshot_after` **49677344768**, `prod_census.json` **49677344768**, `prod_census.run1_threaderror.json` **49677344768**, my census re-run **49677344768**.
  - The figure **49,677,344,476 appears in exactly one place**: `recovery/README.md` line 41 (grep over `execution_runs`, md/json/txt) — a digit transposition in prose. **Verdict: 49,677,344,768 is right** (live stat == every measurement == the earlier plan-wide figure; 域：本次实测 + 全部四份记录) ; the README figure is wrong and, because the README is pinned `5ca0c271…` in handoff, it is **recorded (F-REV-3), not edited**.
- **Boundaries re-checked by me at close**: the 16 anchors + 3 samples (6 files) re-hash unchanged (0 mismatches); production catalog identity unchanged (size+mtime as above); **git**: no git verb appears in any `commands.json` entry or any recorded argv (the only "git add/commit/…" string in the whole attempt is `binding.json`'s own forbidden-list line) ⇒ `git_commands_run: 0` corroborated; **network**: `commands.json` carries `network: disabled by construction for every command below` on every entry, `binding.network.default = disabled` with `case_scoped_exceptions: []`, and **no recorded argv contains `download`/`--allow-download` (0 hits)**; my own runs made no network call (local paths only) （域：本 attempt 记录的全部 argv + 我自己的运行）.
- **Cell-tree integrity vs `iso_final.json` (95 pinned files)**: 94 byte-identical; **exactly one changed: `X01-companies-only\cwroot\.source_catalog\catalog.sqlite3` (245,760 → 258,048 B) — caused by my observation-(d) probe** (adds 1 scan_run + 1 fingerprint_state row). No file missing, no file added; all product trees untouched. My other re-runs (X04/X05 resolves, the four UNK quote runs) changed **no row count** in their cells (measured before/after) （域：%TEMP% 隔离树；product trees 不在其中）.
- **Real-root manifests: compared at close against `snapshot_before.json`** (file count / total bytes / max mtime, full sha for `future_lake`): `CW/companies` **33126 / 25173794322 / 1789793579.374166 ✓**, `CW/future_lake` **1 / 545 / 1787162453.047714 + full sha ✓**, `dayu-agent/workspace/portfolio` **3732 / 2044173414 / 1787085171.915866 ✓**, `Dropbox/Stock` **10342 / 15742131522 / 1786394574.484714 ✓** — all four identical （域：这四个 real root 的清单字段）. **Close verdict: no_mutation = true** (16 anchors 0 mismatches, 6/6 samples unchanged, catalog size+mtime unchanged).

## Findings (reviewer register)

| id | severity | finding | disposition |
|---|---|---|---|
| **F-REV-1** | medium, downstream | **C1 confirmed by independent re-execution**: `sidecar_filing_v1` computes exact remediation reasons (`sidecar.py:60/74`, promise `:5-7`) but `adapter_dispatch._to_scanner_candidate:57-76` never copies `NormalizedCandidate.evidence` (and never sets `_Candidate.error`) ⇒ `locations.error=NULL` for all 4 probes; a catalog reader sees `indexed_only` but never the cause. | accepted as this card's recorded FINDING C1; **route to REMEDIATION ledger; fix NOT I-07-C's surface** (card clause 3 = explicit refusal/no-guessing, satisfied). |
| **F-REV-2** | low | `handoff.completed_steps[6]` says "9 product CLI runs (7 scans … 7 resolves)"; measured evidence = **9 scan dirs + 8 resolve dirs = 17 product runs** (`commands_executed`/`raw_exit_codes` are correct). | bookkeeping only （域：handoff 文本里的计数）; parent may correct in the batch commit; no measurement depends on it. |
| **F-REV-3** | low | `recovery/README.md` line 41 records catalog size **49,677,344,476** while every measurement (live stat, snapshots, census, census run1) says **49,677,344,768** (digit transposition). | recorded, not edited (README pinned `5ca0c271…`); live evidence is authoritative. |
| **F-REV-4** | low | decision §5 lists `NVO` as a no-hardcode pattern; the published run used 7 tokens and the checker's `len>=4` filter drops `NVO`. | conclusion unaffected (my raw probe: `NVO` absent from all 10 harness files); wording overstated — correct in the batch commit. |
| **F-REV-5** | medium (for the parent's open item) | Observation (d)'s suggested mechanism is not supported by I-07-C's timing: +1 appears at the **second scan**, not at the missing resolve (dump-after-resolve1 = 0), and my probe shows **scan-count alone suffices** on a reused cell; I-07-B's own carrier shows a third (scan-free, RF ensure) trigger. | carry to parent as a refined lead for I-07-B's inherited "document_fingerprint_state+1 not root-caused" item: **missing-resolve theory dropped; check scan/ensure triggers**. |
| **F-REV-6** | info | The non-fixture proof's "…before construction" wording: published evidence (`non_fixture_grep.*`, 14:51–14:52) postdates cell build (14:21) and the first scans (14:31); no pre-construction artifact exists. | substance independently re-verified by me at review time (0 fixture hits, positive control pass); only the timing word is unevidenced （域：before-construction 这个时间词）. |
| **F-REV-7** | medium, downstream (from the holdout) | **Criterion-(i)-eligible companies cannot reach resolve reuse in this build**: across all 10,596 registered active ≤25 MB sidecar/meta-bearing filings （域：这10,596行的交集统计）, `eligible ∩ https-source_url-capable = 0`; the capture gate (`resolver.py:1919-1925`, `:1570-1576`) requires `https://`, while eligible companies' registered metadata carries either no `source_url` (company_raw/dropbox sidecars) or `http://static.cninfo…` (dayu meta). **Measured end-to-end by my holdout run (§C2): scan rc0 + strategy adapter + document registered; resolve `missing` / `capture_incomplete` with `entity_gate_rejected: 0`.** | downstream product/data gap (capture-readiness of non-fixture companies); **not this card's fix surface**; route to REMEDIATION ledger with the holdout envelope as evidence. |
| **F-REV-8** | info | Adapter provenance is not persisted for the dayu path: my holdout document's `metadata_json.acquisition` is **null** (no `adapter_id`), unlike X05's sidecar-scanned document (`acquisition.adapter_id: sidecar_filing_v1`); the scan report's `strategy` map is the only carrier of which adapter read a root （域：dayu 路径写入的文档元数据）. | recorded only （域：本条仅为信息记录） (observability family with C1); no action required for I-07-C. |

## Unverified / not claimed by this review

- Production rows were not re-derived per document; no production write of any kind (mode=ro + `query_only` for every catalog open I made) （域：我的全部 catalog 打开）.
- The 6,411 external-only structural candidates were not qualification-checked (existence only — 域：这6,411个候选) — same scope as the implementer's §8.
- Evidence files: **22 of 108** re-hashed (all 15 handoff-pinned + all 7 iso_initial — 域：108个evidence文件中的这22个); the remaining 86 were read/spot-checked but not individually hashed.
- rc=1 harness events (1) and (2) have no preserved artifact (see D) — declared only （域：这两个rc=1事件）.
- No live (L) level qualification was attempted or is granted; `overall_three_market_pass=false` and the zero-RevenueSourceRecord fact travel unchanged.
- Holdout result is a **C-level** statement about this product build at these hashes; nothing about accuracy or three-market readiness.

## REM-79 self-check

Tool: `execution_runs/REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py` v`1.2.0-correction2` (the REM79 attempt's `tools/` copy), stdlib, read-only, run as `PYTHONIOENCODING=utf-8 <iso-python> -X utf8 -B <checker> reviewer_report.md` from this attempt directory.
Result on this final text: **`0 violation(s) across 1 file(s)`, exit 0** — the first pass reported 18 detections, each fixed by putting the same-line domain on the offending line; this section is part of the checked text （域：本报告单文件的自检）. Re-run after the final edit returned exit 0 (recorded in the message to the parent).

## Authority, writes, cleanup

- Writes: exactly `reviewer_report.md`, `reviewer_report.sha256`, and `evidence/reviewer_holdout/**` (35 files, ~52 KB: freeze records, selection-screen summary, holdout build/scan/resolve/verify + artifact shas, my clause-5 recomputes `clause5_nohardcode_recheck.txt` / `clause5_nonfixture_recheck.txt`, my X04/X05 resolve re-run captures, my four UNK quote re-runs, my X01 fingerprint probe) （域：本 attempt 目录）. Product trees (RF/CW/FF/dayu/Dropbox) read-only; `%TEMP%\i07c\**` holds all runs.
- Isolated-tree cleanup authorized **after this review lands**, per `recovery/README.md` (`Remove-Item -Recurse -Force "$env:TEMP\i07c"` + this attempt dir), followed by the README's post-recovery re-hash witness (my close run already measured no_mutation=true).
- I sign this review; the implementer does not (`implementer_signed: false` stands).
