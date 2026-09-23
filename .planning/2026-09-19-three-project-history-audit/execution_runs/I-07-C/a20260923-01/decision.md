# I-07-C decision — per-cell × per-clause measured conclusions

Attempt `a20260923-01`. Every claim below quotes captured evidence; expected-vs-raw
rc are kept separate; product rcs are raw (commands.json legend). Oracle
(`oracle.md`) was frozen BEFORE the first judged run and never edited.

## 0. Exit-honesty declaration (verbatim, carries into handoff)

「每个格单独结论，无外部only实证就不签该资格；它不阻止与其无关的已验证本地读场景。」

Inherited verbatim declarations from I-07-B (its handoff, must accompany citing artifacts):

1. 三公司仅来源准备通过，仍未授予正式预测资格。
2. 缺一市场/真实路径不得总体写三市场通过。
3. 恢复：保留已取得raw，只回退当前隔离变更。

## 1. Per-cell verdict table (one conclusion per cell; the exit rule's requirement)

| Cell | Clause | Level actually run | Conclusion (own, not extrapolated) |
|---|---|---|---|
| **X04 multi-root, same bytes** | 1 | C — isolated roots, real manifest-pinned bytes (read-only copies) | **CONCLUDED / signed at C level**: identical filing bytes in 2 distinct roots are **NOT counted as distinct sources** — measured `1 sources row` (content-sha UNIQUE), `1 documents row`, `2 location rows` under roots `companies_root_a`/`companies_root_b`; both copies independently re-hashed equal to the manifest pin; `resolve` returned `one_existing_source_satisfies_semantic_request` (one reusable source). Root count never becomes source count. |
| **X05 fifth isomorphic root** | 2 | C — isolated config with the 4 production root entries + a 5th | **CONCLUDED / signed at C level**: a hitherto-unnamed root `i07c_fifth_lake` (name proven absent from PLAN/CW scopes) with a non-fixture company (name proven absent from every fixture/expectation scope) completes **scan + resolve through the frozen supported adapter/profile** (`sidecar_filing_v1` + `financial_evidence_v1`): scan strategy `i07c_fifth_lake: "adapter"`, rc0; resolve2 `status: reused_equivalent`, `outcome: reused_existing`, `qualification {label: verified_input, gaps: []}`. First attempt's `capture_incomplete` exclusion (my fixture lacked `source_url`) is kept as evidence — see §3. Not a name whitelist: harness company literals = 0. |
| **Unknown layout (3 probes)** | 3 | C | **CONCLUDED with one finding**: (a) unknown `adapter_id` → explicit refusal `CatalogConfigError: … 'unknown_layout_v9' not registered (CFG-01)`, product rc1 on BOTH scan and resolve (raw traceback — config load runs before cli.py's try at :868 vs :951); (b) unknown root `kind` → explicit refusal `ValueError: unsupported root kind: unknown_layout_probe` (models.py:141-142 over `ROOT_KINDS`) on both entries — **no identity/adapter guessing can occur because the config never loads**; (c) malformed sidecar layout → roles degrade explicitly (`indexed_only` for invalid sidecars; `original_primary` for the valid and the sidecar-less files), entities stay `unresolved:<root>` (no filename-guessed identity). **FINDING C1**: the "exact remediation reason" promised by `adapters/sidecar.py:6-7` (`missing_sidecar`, `sidecar_parse_failed`, `content_hash_mismatch`, `path_escape`, `missing_identity:…`) is computed but **dropped** — `adapter_dispatch._to_scanner_candidate` (adapter_dispatch.py:57-76) copies only `normalized`, never `evidence`; measured: `locations.error = NULL` for all 4 probes and `documents.metadata_json.acquisition` carries no `remediation` key (broken sidecar ⇒ `acquisition: null`). So "明确unsupported" holds at load/role level, but the CAUSE is not observable by a catalog reader. |
| **X01 companies-only** | 4 | C — isolated construction only | **ISOLATED eligibility signed**: config with the single `company_raw` root; scan rc0; unique location holds bytes whose sha = manifest pin `01819e1c…`; `resolve` reused it. **Production companies-only NOT signed** — I-07-A measured CN uniqueness DISPROVED (same hash under `company_raw` AND `dropbox_stock`), cited, not overridden. Root name never substitutes for qualification. |
| **X02 dayu-only** | 4 | C — isolated construction only | **ISOLATED eligibility signed**: config with the single `dayu_portfolio` root; isomorphic `portfolio/<ticker>/filings/<id>/` tree built from a frozen sample's REAL bytes (`e3de0053…` = manifest pin) with `meta.json` derived from its real sidecar; scan rc0 registers `original_primary` + `metadata` locations under `dayu_portfolio`; `resolve` reused (`reused_existing`). **Production dayu-only NOT signed** — no reviewer-frozen identity exists for that root (I-07-A blocked cell), even though the read-only census shows 3660 registered dayu locations. |
| **X03 external-only** | 4 | **none — no sample exists** | **BLOCKED (not NA)**: `sample_manifest.EXTERNAL-ONLY = status "unbound"` ("Reviewer selects and freezes identity/period/as_of/provider/raw-state … never delete production copies to manufacture absence"). Blocked-proof bundle: (i) manifest unbound rule; (ii) I-07-A blocked cell `source.external_dir_only`; (iii) my read-only production census (`evidence/prod_census.json`, mode=ro+query_only): ALL registered locations verified — `company_raw 33092 / dayu_portfolio 3660 / dropbox_stock 9853 / future_lake 1`, documents 23530, and **6411 structural candidates** whose locations are exclusively under external dir roots — existence ≠ eligibility: none is reviewer-frozen, none was qualification-checked, exclusivity manufacture is forbidden. Per exit rule: no external-only 实证 ⇒ that qualification is NOT signed, and this blocked cell does not block the unrelated verified local read scenarios (X01/X02/X04 conclusions stand). No isolated construction was built for X03 (no tree exists — oracle attack item 5). |

**Reviewer holdout (clause 5, NOT mine): SEALED FOR REVIEWER.** As of this attempt
`sample_manifest.unbound_live_samples["HELDOUT-COMPANY"]` is `status: unbound`
and carries **no identity at all** — there is nothing for this attempt to know,
read or target; the independent reviewer freezes it before/at review. This
attempt did not swap any sample: fixture selection is mechanical (X04 =
`min(byte_size)` ⇒ HK sample; X01 = `market=="CN"`; X02 = `market=="US"`).

## 2. Adapter/profile support freeze (oracle §0.2, derived from product evidence BEFORE tests)

Frozen supported set (files+lines+hashes pinned in `binding.json.product_adapter_dispatch`):

- scanner-capable adapters = `{sidecar_filing_v1, company_raw_v1, dayu_filing_v1}`
  — `adapter_dispatch.py:29-33`; `generic_document_v1` is registered
  (`adapters/registry.py:42-47`) but `adapter_for` fails closed for it
  (`adapter_dispatch.py:48-53`).
- admission profiles = `{financial_evidence_v1, generic_document_v1}`
  — `registry.py:10-21`.
- config-time: CFG-01 unknown adapter ⇒ `CatalogConfigError` (`config.py:127-131`);
  CFG-02 unknown profile (`config.py:132-136`); **root `kind` is NOT validated by
  config** (`config.py:166`) — the model is: `models.py:39 ROOT_KINDS =
  {"company_raw","directory","dayu_portfolio"}`, `models.py:141-142` raises
  `unsupported root kind`.
- scan selection: `scanner.py:855 use_adapter = v2_scan_shadow or
  root.adapter_id is not None`; adapter branch fails closed, per-ROOT
  (`scanner.py:866-884, 1941-1953`).
- resolve: `cli.py:403-422` flags; `--entity` passes through (`cli.py:934-948`);
  entity anchor accepts sidecar `company_name` (`resolver.py:1726-1734`);
  capture-ready gate needs an `https://` URL + published date + sha + capture
  trace (`resolver.py:1919-1965`).
- dedup primitives: `store.py:136-142 sources.content_sha256 UNIQUE`;
  `scanner.py:1046 INSERT OR IGNORE INTO sources`; `scanner.py:83-84
  document_id = document:sha256:<content tail>`; `scanner.py:1089-1091
  locations ON CONFLICT(root_id, relative_path)`.

RF side: `grep adapter RF/scripts/*.py` → only a docstring mention
(`trust_anchor.py:5`); RF does no adapter dispatch — it reaches this surface
only through the CW CLI (I-00-B contract).

## 3. The four clause evidence highlights (measured, with quotes)

### (1) Same-bytes multi-root proof — `evidence/x04_hash_verify.json`
- `content_sha_equal_between_roots: true`, `both_equal_manifest_pin: true`
  (both copies sha256 = `ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c`,
  4 405 561 bytes each).
- `distinct_root_locations: ["companies_root_a","companies_root_b"]` — two
  location rows, same relative path, distinct roots, both
  `role=original_primary, status=active`, **same `source_id`
  `…:ffd73376…` and same `document_id` `…:ffd73376…`**.
- `sources rows for that content = 1` (the 2nd sources row in the cell is the
  sidecar's own bytes `8228741d…`, a different logical file), `documents = 1`.
- Measured conclusion: **one logical document, multiple valid locations, zero
  duplicate source counting** — the product DOES reach X04's expectation
  (`scenario_matrix.md` X04), asserted here as measured behavior (schema quotes
  §2 explain why: content-sha identity everywhere).
- resolve: `reason: one_existing_source_satisfies_semantic_request`.

### (2) Fifth-root success/behavior — `evidence/X05-fifthroot/scan1|2, resolve1|2`
- Config loads with 5 roots (CFG-01/02/05/07 pass); scan rc0 report strategy:
  `{"company_raw":"legacy","dayu_portfolio":"legacy","dropbox_stock":"legacy",
  "future_lake":"adapter","i07c_fifth_lake":"adapter"}` — the new root is read
  by the supported adapter, no product code changed.
- Registered: 1 document (`document_kind annual_report`, `source_status active`),
  1 source, 1 location under `i07c_fifth_lake`, entity row
  `unresolved:i07c_fifth_lake` (adapter path anchors entities only from
  company_raw dir names — `scanner.py:196-204`; the resolve anchor came from
  the sidecar `company_name`, `resolver.py:1726-1734`, `entity_gate_rejected: 0`).
- **resolve1 (kept)**: `outcome: missing`, trace `…: capture_incomplete` —
  quoted resolver.py:1570-1576: a handle without `https://` URL cannot be
  capture-ready. Cause = MY fixture sidecar lacked `source_url` (every real
  production sidecar has one; an isomorphic sidecar must too). Fixture
  completed (+`source_url: https://example.invalid/…`, RFC-2606 reserved host),
  `scan2`/`resolve2` captured ALONGSIDE (never over) run1.
- **resolve2**: `status: reused_equivalent`, `outcome: reused_existing`,
  `qualification {label: verified_input, gaps: []}`, `capture_ready: true`,
  `canonical_path: ${PROJECT_ROOT}\i07c_fifth_lake\…`, `prompt_injection_status:
  not_reviewed` (inherited F3 shape — resolve reports it, does not fake it).
- No name whitelist: `evidence/no_hardcode_grep.txt` = **0 matches** (run1's 5
  CJK hits were the Windows USERNAME inside absolute paths — preserved as
  `no_hardcode_grep.run1_username_falsepositive.txt`; the checker now masks the
  runtime home path, which is machine identity, not a company identifier).

### (3) Unknown-layout measured response — `evidence/UNK-*/scan1|resolve1`
- **UNK-adapter**: product rc1 both entries; stderr (raw, captured verbatim):
  `company_wiki.source_catalog.config.CatalogConfigError: roots[0] adapter_id
  'unknown_layout_v9' not registered (CFG-01)` — explicit unsupported, and the
  raw-traceback (not structured-envelope) shape itself confirms the load runs
  before cli.py's try.
- **UNK-kind**: product rc1 both entries:
  `ValueError: unsupported root kind: unknown_layout_probe` at
  `models.py:142` — the card's 不自动猜 is satisfied here BY REFUSAL: the
  scanner's guessing machinery I had hand-predicted (`scanner.py:506 else-branch`,
  `scanner.py:528 ticker = parts[0]`, filename-text classifier
  `scanner.py:116-169`) is never reached for an unknown kind. Oracle §13c
  explicitly allowed either outcome; measured = refusal.
- **UNK-sidecar**: scan rc0; roles after fixture-hash correction (scan2, run1
  kept): `clean_probe → original_primary`, `broken_sidecar_probe →
  indexed_only`, `mismatch_probe → indexed_only`, `no_sidecar_probe →
  original_primary`; entities `unresolved:*` for all four (never a guessed
  company/ticker); resolve envelope `status: missing, reason:
  no_existing_source_satisfies_request` (explicit, `matches: []`).
  **FINDING C1** (reason strings dropped — see §1) and **observation**: a file
  WITHOUT a sidecar registers as full `original_primary` (sidecar.py's
  missing-sidecar candidate) and, with its remediation dropped, nothing in the
  catalog shows the sidecar was absent.

### (4) Three-only matrix — `evidence/X01-*/…`, `evidence/X02-*/…`, `evidence/prod_census.json`
- X01: 1 root, 2 locations (raw+sidecar) under `company_raw` only, sha =
  manifest pin, resolve reused ⇒ isolated eligibility; production companies-only
  stays unsigned (I-07-A SQL: CN hash exists under TWO roots).
- X02: 1 root, real sample bytes under `dayu_portfolio` only, entity
  `ticker:MSFT` via `path_ticker`, `document_kind annual_report` via
  `form_type "10-k"` (`scanner.py:148`), resolve reused ⇒ isolated eligibility;
  production dayu-only stays unsigned (no frozen identity).
- X03: BLOCKED with the census above (6411 structural candidates ≠ a frozen
  sample). Census run1 hit a harness threading bug
  (`prod_census.run1_threaderror.json` preserved); run2 fixed
  `check_same_thread=False` and answered all 3 steps in 6.3 s, still mode=ro.

## 4. Non-fixture proof for the fifth root (`evidence/non_fixture_grep.txt/.json`)

- Fifth-root identity lives ONLY in `inputs/fifth_root_company.json` (data):
  company name (CJK) + `ascii_aliases` + root id `i07c_fifth_lake`.
- **Fixture/expectation scopes scanned (12 scopes, ~1700 text files):
  0 matches** for the company name, the ASCII aliases, the root id and the
  security id — PLAN/execution_v2 (cards+matrix+manifest), PLAN/execution_runs
  I-07-A/I-07-B/I-00-A/I-00-B, RF/audit_review, RF/scripts, RF/tools, CW/src,
  CW/tests, CW/config, filing-fetch repo.
- **Positive control PASSED (17 hits)**: the three fixture company dir names DO
  appear in those same scopes — proving the scopes really see fixture text, so
  the 0 is meaningful, not an empty-scan artifact.
- Disclosed separately (NOT a fixture/expectation): 8 hits of the ticker/alias
  inside filing-fetch **e2e `.runs/…/.source_catalog/security_master/hk.json`**
  — a copy of the full securities-universe listing inside historical run
  artifacts; virtually every listed company appears there, so absence from such
  a file is impossible for a real listed issuer. First-run output (before this
  classification) preserved as `non_fixture_grep.run1.txt`.
- Rejected candidates (recorded in binding): 贵州茅台 (CW routing.py:187-189 +
  filing-fetch task_plan.md), 宁德时代/300750 (filing-fetch fixtures), 万华化学
  (CW production company), 000858/600519 (CW test_zr501 fixture ids).

## 5. No-hardcode grep of MY construction (clause-5 obligation) — published output

`evidence/no_hardcode_grep.txt` (run2): **TOTAL MATCHES: 0** across
`build_iso.py, i07c_common.py, make_changes_diff.py, non_fixture_grep.py,
prod_census.py, run_stage.py, show_rows.py, snapshot.py, summarize_cells.py,
verify_x04.py` (checker excluded as self-referential; machine-username path
masks derived at runtime, disclosed in the header). Patterns: any CJK codepoint
+ ascii tokens derived from the manifest/fifth-root data
(`601899, 1810, MSFT, 12127452, 0001193125-26-323660, NVO, i07c-x05-0001,
isolated-i07c-0001`). run1 (5 username false positives) preserved.
[F-REV-4 correction: that published pattern list is 7 tokens — the checker's `len>=4` filter drops the 3-char token `NVO`, so `NVO` was never in the executed set; the reviewer's raw probe found `NVO` absent from all 10 harness .py files (reviewer_report.md §C3), so the 0-match PASS conclusion is unaffected; the original wording above is retained unedited]

## 6. Missing-input / inherited-carry notes

- **Card input 输入：矩阵X01—X05 — LOCATED, not missing**: it is
  `execution_v2/scenario_matrix.md` §根目录与泛化 rows X01–X05, byte-pinned
  sha256 `0dec23cd10f00efd6ad82cf923552bd46c1763bcf9f740422f51f4973292299f`
  (identical to I-07-B's pin and to validation.json). Had it been absent this
  attempt would have stopped rather than invent it (per the card instruction).
  Row X06 (reviewer holdout row) is the reviewer's, untouched.
- **Inherited carries from I-07-B (accepted_scoped)**: F1 entry-never-scans
  (this card registers only via `cli scan`, exactly that shape); F2 no
  structured recovery (all refusals measured here carry only
  `error_code/error/retryable`-class text or raw load errors — no
  candidates/next-action anywhere in this card's envelopes); F3 no review CLI
  (`prompt_injection_status: not_reviewed` appears in every resolve envelope —
  reported, never faked); the three verbatim exit declarations (§0);
  `overall_three_market_pass=false`; zero-RevenueSourceRecord fact.
  F5/REM-86 eol-pin note for `I-07-A/after/state_matrix.json` carried into
  `binding.json` (both pin variants recorded; no measurement depends on it).
- **New observation for the parent**: cells whose `resolve` returned `missing`
  show `document_fingerprint_state` +1 in the isolated catalog (X05 between
  scan1↔scan2, UNK-sidecar), while `reused` cells show 0 — this looks like the
  persistent-demand registration behind I-07-B's inherited "document_fingerprint_state+1
  not root-caused" open item (timing-consistent association, not proven causal).

## 7. Specialized-decision / judgment-call register

- J1 (own call): X05 fixture completed ONCE (+`source_url`) after the measured
  `capture_incomplete` exclusion; motivation = resolver.py:1919-1965 + the fact
  that production sidecars all carry a URL (isomorphism demanded it). NOT an
  oracle edit, NOT a sample swap (same company/root/bytes); run1 evidence kept.
- J2 (own call): UNK-sidecar `clean_probe` sidecar hash corrected from the
  pre-newline-translation string hash to the FILE hash (my fixture bug; the
  product had correctly demoted it — run1 kept). run2 gives the intended
  valid/invalid contrast.
- J3 (own call): X02 built as an ISOLATED dayu-shaped tree from real sample
  bytes instead of scanning the 2.04 GB real dayu root — the card limits
  isolated constructions to isolated eligibility anyway, and the real external
  root is therefore never opened at all (binding.real_roots).
- J4 (own call): the three UNK cells' `resolve_request.json` files were written
  as request INPUTS after their builders (builders emit requests only for cells
  whose config loads); UNK-sidecar's entity derives from that cell's own
  sidecar; the other two use a neutral non-company token because their configs
  cannot load at all — the product answered with the same CFG-01/ROOT_KINDS
  refusals.
- J5 (declared-expectation deviation, disclosed): `commands.json` declared
  expected product rc=0 for the UNK-kind scan ("config LOADS"); measured rc=1.
  Cause: the freeze-time read stopped at `config.py:166` (kind is not
  validated THERE) and missed `models.py:39/141-142 ROOT_KINDS`, which refuses
  the kind at RootSpec construction. The refusal is precisely what card
  clause 3 asks for (不自动猜), so the clause verdict is positive — but the
  pre-declared rc was wrong and is recorded as wrong; the oracle is not edited.
- Specialist decisions (lock/transaction, review-receipt contract, statistics,
  deployment qualification): NOT APPLICABLE — this card runs no producer, no
  lock, no download, no statistical claim; F2/F3 remain routed as inherited.

## 8. Unverified / not claimed by this attempt

- No production resolve/scan was run (49.7 GB catalog touched read-only only);
  production rows were not re-derived per document.
- The 6411 external-only structural candidates were NOT qualification-checked
  (identity/period/provenance gates) — existence only, and explicitly not an
  eligibility claim.
- The reviewer holdout sample has not been run (sealed) — clause 5's actual
  generalization run belongs to the independent reviewer.
- No live (L) level qualification of any kind was attempted or is asserted;
  network was disabled for every bound command.
