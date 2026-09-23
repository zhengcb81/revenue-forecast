# I-07-C oracle — frozen BEFORE the first judged run

Card: `execution_v2/card_I-07-C.md` (14 lines, sha256 `c3c3f5333a2f9fd68eb83bf17ba4a83ab700b73d8100e445ce7e288fe4704124`).
Attempt: `execution_runs/I-07-C/a20260923-01`. One observable result (step 1): **five clause cells + the
three-only matrix each produce their own measured conclusion from real `cli scan` / `cli resolve` runs on
isolated roots, with the external-only cell staying BLOCKED.**

This file is frozen at step 4 and MUST NOT be edited after the first judged run (binding.forbidden).

---

## 0. Frozen inputs this oracle is pinned to

### 0.1 Matrix input — the card's 输入：矩阵X01—X05 (LOCATED, not invented)

The card says `输入：矩阵X01—X05`. The matrix lives in the PLAN file
`execution_v2/scenario_matrix.md` §根目录与泛化 (rows X01–X05 plus X06), byte-pinned here:

- path: `PLAN/execution_v2/scenario_matrix.md`
- sha256: `0dec23cd10f00efd6ad82cf923552bd46c1763bcf9f740422f51f4973292299f` (6219 bytes; identical to
  the value I-07-B pinned and to `execution_v2/validation.json`).
- consumed rows (verbatim from that file):

| ID | 层级/准备 | 操作与预期 |
|---|---|---|
| X01 | C/R companies-only | 从唯一合格location读取；原件hash匹配；root名称不能代替资格 |
| X02 | C/R dayu-only | 新raw仍写canonical规则不变；已有外部root可复用；不把读规则当写规则 |
| X03 | L external-only，现缺合格样本 | 先验证所有已注册位置再认定only；不能删其它副本；未绑定则blocked |
| X04 | R 多root相同bytes | 解析一个逻辑document和多个有效locations；不重复下载/不重复计收入来源 |
| X05 | C 新第五root+新公司名 | 已支持adapter同构布局成功；未知layout另例明确unsupported；不按名称白名单造绿 |

Related pinned inputs: `sample_manifest.json` sha256 `d5d0bb92da9eee92666459ccf344d549343008db8bf32fd1257dbf6f5f3ec851`
(carries the unbound `EXTERNAL-ONLY` and `HELDOUT-COMPANY` live samples — both `status: unbound`,
reviewer-frozen before any execution); I-07-A `after/state_matrix.json` disk sha256
`de784cb2f94cb2ed7a3b13a315063fb4fc7b746519db939ea58e6707abbe8684` (the inherited pin `dc72776f…` is the
LF→CRLF variant of the same bytes — F5/REM-86 note carried from I-07-B); I-00-B contract files
`binding.json` `fdb2a59890e64c42f4a4566c8aaa6eefaec8e867c01779974178048d9fbf75f0`,
`commands.json` `f8a397ecd306b03f03385ad25c28667338c85e3301277414ddf4013f3c9a24df`,
`oracle.md` `e9c82fe46ed21cc80db7948b8872f35af7c07d994c65310501accdd615693a64`.

### 0.2 ADAPTER/PROFILE SUPPORT FREEZE (section 1 of the oracle, derived from PRODUCT EVIDENCE)

This is the support scope the high-level reviewer freezes before tests. It is **read out of the product
code as it stands**, not aspirational. Every line below was read before any run; file hashes are pinned
in `binding.json.product_adapter_dispatch`.

**Scan-side dispatch (the only scan path):**

| Evidence | Line(s) | Frozen fact |
|---|---|---|
| `CW/src/company_wiki/source_catalog/adapter_dispatch.py` | 29–33 | `_ADAPTER_FACTORIES = {sidecar_filing_v1, company_raw_v1, dayu_filing_v1}` — **exactly these 3** scanner-capable adapters |
| `adapter_dispatch.py` | 39–53 | `adapter_for()`: `adapter_id is None` → `AdapterDispatchError("no adapter_id (2.x policy required)")`; not in registry → `"not registered"`; registered but not in factories (i.e. `generic_document_v1`) → `"has no scanner adapter implementation"` — **fail closed, no fallback** |
| `CW/src/company_wiki/source_catalog/adapters/registry.py` | 23–48 | `REGISTERED_ADAPTERS` = 4 ids: `sidecar_filing_v1` 1.0.0, `dayu_filing_v1` 1.0.0, `company_raw_v1` 1.0.0, `generic_document_v1` 1.0.0 (registered but NOT scanner-capable) |
| `registry.py` | 10–21 | Admission profiles = **exactly 2**: `financial_evidence_v1` (official providers `example-filing, dayu, sec, hkex, cninfo`; allows_filing; read_only_required), `generic_document_v1` |
| `CW/.../config.py` | 127–131 | Config-time CFG-01: unknown `adapter_id` → `CatalogConfigError("not registered")` (explicit unsupported at load) |
| `config.py` | 132–136 | CFG-02: unknown `admission_profile_id` → `CatalogConfigError` |
| `config.py` | 113–115 | unknown root fields → `CatalogConfigError`; **`kind` is NOT validated** (`kind=str(item.get("kind",""))`, config.py:166) |
| `CW/.../scanner.py` | 848–856 | selection: `use_adapter = v2_scan_shadow or root.adapter_id is not None` → strategy `"adapter"` else `"legacy"` |
| `scanner.py` | 1928–1960 | adapter branch: `AdapterDispatchError` → `ScannerFacadeError("v2 scanner unavailable (fail closed)")`; any adapter runtime failure → `"fail closed, no legacy fallback"` |
| `scanner.py` | 866–884 | per-ROOT fail-closed: a broken adapter root contributes nothing, `error_details` records `scan_root_strategy: …`, the batch continues |
| `scanner.py` | 283 / 377 / 506 | legacy dispatch by free-text `kind`: `company_raw` → companies-dir walk; `directory` → os.walk; **`else` (any other kind, incl. `dayu_portfolio` AND unknown kinds) → portfolio grouping** (`ticker = parts[0]`, scanner.py:528) |
| `scanner.py` | 144–185 | legacy kind classifier guesses `document_kind` from path/title/form TEXT (年度报告/10-K/季度… heuristics; `root_kind == "directory"` → `broker_research` fallback, line 181–182) |
| `scanner.py` | 188–193 | `_entity`: `[A-Za-z0-9._-]+` → `ticker:<NAME>`; else `company-name:<NAME>`; else `unresolved:<root_id>` (confidence 0.0) |
| `scanner.py` | 196–204 | `_company_names` reads ONLY `kind == "company_raw"` roots' `companies/<dir>/raw` dirs |
| `CW/.../adapters/sidecar.py` | 21, 26–28, 90–119 | sidecar contract: schema `1.0`; required identity `canonical_entity_id, market, security_id`; required facts `document_kind, fiscal_year, period_end, content_sha256`; required provenance `provider, provider_document_id`; declared hash must equal bytes (`content_hash_mismatch`); absolute/`..` paths rejected (`path_escape`); **"Missing fields degrade to indexed_only with an exact remediation reason — never guessed from the filename (F-043)"** (sidecar.py:6–7) |
| `CW/.../admission.py` | 133–140 | `evaluate_admission` returns a decision ONLY for the FOCUS subtree; every other root (all of this card's roots) → `None` (no policy exclusion) |

**Resolve-side (the only read path):**

| Evidence | Line(s) | Frozen fact |
|---|---|---|
| `CW/.../cli.py` | 403–422, 1165–1200 | `resolve` requires `--entity` OR `--company-query`, `--document-kind`, `--as-of-date`; `--company-query` goes through the security-master identity (`identify_company`, cli.py:900–927) and raises if unresolved; `--entity` passes the string straight into `SourceRequest.entity` (cli.py:934–948) |
| `resolver.py` | 1705–1747 | `_entity_matches` compares the request against document entities **and** `metadata.ticker / security_id / company_name` (normalized) — the sidecar's own `company_name` is an accepted anchor |
| `resolver.py` | 1659–1697 | identity gate: no identity filter → `match`; identity present but candidate has none → `missing_fail_closed` (blocks, never guesses) |
| `resolver.py` | 788–829 | qualification gaps `identity_missing / period_missing / source_missing` block reuse (fail-closed) |
| `store.py` (schema) | 136–142 | **`sources.content_sha256 TEXT NOT NULL UNIQUE`** |
| `scanner.py` | 1046 | `INSERT OR IGNORE INTO sources(…)` — identical bytes collapse to ONE source row |
| `scanner.py` | 83–84, 997–1001 | `document_id = "urn:company-wiki:document:sha256:" + content-sha tail` (`source_manifest.source_id_for_sha256`) — identical bytes ⇒ ONE logical document |
| `scanner.py` | 1089–1099 | `INSERT INTO locations … ON CONFLICT(root_id, relative_path)` — one row PER root+path ⇒ distinct roots ⇒ distinct locations |
| `source_manifest.py` | 16, 55 | `SOURCE_ID_PREFIX = "urn:company-wiki:source:sha256:"`, `source_id_for_sha256(content_sha256)` |

**RF side:** `grep adapter` over `RF/scripts/*.py` → only a docstring mention in `trust_anchor.py:5`
("invest-core adapter"); RF does **no** adapter/profile dispatch — it reaches scan/resolve only through
the CW CLI (I-00-B entry contract). Download-side adapters (out of scope here, no download in this card):
`acquisition_config.py:73–75,175–176` pins cn→`json_command_v1`, hk/us→`dayu_cli_v1`, exact `cn/hk/us` keys.

**Frozen supported set for this card (what "supported adapter/profile" means below):**
scanner-capable adapters = `{sidecar_filing_v1, company_raw_v1, dayu_filing_v1}`; profiles =
`{financial_evidence_v1, generic_document_v1}`; legacy reader = free-text `kind ∈ {company_raw,
directory, dayu_portfolio-shaped else-branch}`. Anything else must fail closed — if it does not, that is
a recorded finding, not a pass.

---

## 1. Per-clause expected shapes (hand-reasoned from §0.2 BEFORE running)

Rc conventions (I-07-B legend, this batch): harness rc 0 = evidence written; product rc recorded RAW —
`cli`: 0 = ok / 1 = failure (structured envelope on stderr for in-`try` errors, raw traceback for
config-load errors, which happen BEFORE the try at cli.py:868 vs 951) / resolve prints an envelope and
returns 0 regardless of found-vs-not_found.

### Clause 1 — X04 same-bytes-multi-root
Construction: isolated config with TWO `kind: company_raw` roots (`companies_root_a`,
`companies_root_b`), each containing a BYTE-IDENTICAL copy of one frozen sample (raw + its sidecar,
copied from the manifest-declared production paths; no company literal in harness code).
Expected (schema-derived, §0.2):
1. per-root verification: the two copied files hash EQUAL to each other and to the manifest sample sha;
   `locations` holds ≥2 rows for that content sha with DISTINCT `root_id` and DISTINCT `absolute_path`.
2. dedup conclusion the product actually reaches: `sources` rows for that content sha = **1**
   (UNIQUE + INSERT OR IGNORE), `documents` rows = **1** (content-derived document_id) ⇒ same bytes
   in 2 roots are **NOT counted as distinct sources**; they are one logical document with multiple valid
   locations.
3. `resolve --entity <name-from-sidecar>` returns ONE resolution; if the product instead produced two
   sources/documents, record that as measured behavior verbatim — the conclusion asserts the MEASURED
   result, never a preferred one.

### Clause 2 — X05 fifth isomorphic root + non-fixture company
Construction: isolated config containing the four production root entries (ids/kinds/adapters kept,
paths rebound to isolated dirs, all present so scan sees real directories) **plus a fifth, hitherto-unnamed
root** `i07c_fifth_lake` (name proven absent from PLAN/CW by grep — see decision.md non-fixture proof):
`kind: directory + adapter_id: sidecar_filing_v1 + admission_profile_id: financial_evidence_v1 +
read_only: true + reusable_for_filing: true`, containing ONE payload file with an adapter-contract sidecar
for the non-fixture company **诺和诺德** (proven absent from every fixture/expectation scope by grep;
payload bytes are a clearly-labelled SYNTHETIC isolated payload — no real financial document is
fabricated, no financial fact about that company is asserted).
Expected:
1. config loads (CFG-01/CFG-02/CFG-05/CFG-07 all pass — registered adapter + filing capability +
   read_only).
2. scan rc0; scan report strategy for `i07c_fifth_lake` = `adapter`; ≥1 document + ≥1 location
   registered under that root; other four roots contribute 0 rows without errors (empty dirs exist).
3. sidecar validation passes (role `original_primary`, remediation empty) because the authored sidecar
   carries schema/identity/facts/provenance + matching `content_sha256`.
4. `resolve --entity 诺和诺德 --document-kind annual_report --as-of-date …` anchors via the sidecar
   `company_name` (resolver.py:1726–1734) and returns the isolated document (reuse envelope), OR an
   explicit fail-closed envelope — either is recorded raw; an entity/name WHITELIST bypass (green without
   this construction) would be a finding.
5. No company-name whitelist: harness source grep (§3 below) must come back EMPTY for company literals.

### Clause 3 — unknown layout → explicit unsupported (three sub-probes)
3a `UNK-adapter`: root declares `adapter_id: unknown_layout_v9` (never registered).
Expected: config load REFUSES — non-zero product rc, stderr/traceback contains
`adapter_id 'unknown_layout_v9' not registered (CFG-01)` (config.py:127–131). No scan runs, no rows.
3b `UNK-sidecar`: registered adapter (`sidecar_filing_v1`) over a MALFORMED layout — file without
sidecar, sidecar that is not JSON, sidecar whose declared hash ≠ bytes (+ path escape / missing
identity).
Expected: scan rc0 but each file degrades to an EXPLICIT remediation (`missing_sidecar`,
`sidecar_parse_failed`, `content_hash_mismatch`, `path_escape:…`, `missing_identity:…`) with role
`indexed_only` for invalid sidecars — **never a filename-guessed identity/kind** (sidecar.py:6–7).
3c `UNK-kind`: root declares an unknown free-text `kind: unknown_layout_probe` and NO adapter, holding
a probe file named to bait the heuristics.
Expected (hand-reasoned): config LOADS (config.py:166 does not validate `kind`) and the legacy
`else` branch (scanner.py:506) processes it — the product is EXPECTED to (i) take the first path segment
as a ticker (scanner.py:528 `ticker = parts[0]`) and/or (ii) classify `document_kind` from filename text
(scanner.py:144–185). Per card clause 3 (`不自动猜身份/adapter`), **any such guess is a FINDING with exact
quotes**, not a pass. A clean explicit refusal would satisfy the clause; the oracle does not presume it.

### Clause 4 — three-only matrix (each cell its own conclusion)
- **X01 companies-only (isolated construction):** config roots = `[company_raw]` only, holding one
  frozen CN sample (bytes+sidecar copied, hash re-verified against the manifest). Expected: scan rc0,
  resolve reads from the UNIQUE qualified location with `content_sha256` equal to the manifest sha.
  Conclusion may only be signed at **isolated eligibility** level; the production companies-only cell is
  NOT signed here — I-07-A measured CN uniqueness DISPROVED (same hash under `company_raw` AND
  `dropbox_stock`), cited, not overridden.
- **X02 dayu-only (isolated construction):** config roots = `[dayu_portfolio]` only, holding an
  isomorphic `portfolio/<ticker>/filings/<id>/…` tree built from a frozen sample's REAL bytes with
  `meta.json` facts derived from that sample's real sidecar (data-driven, no literals). Expected:
  scan rc0 registers ≥1 document from the dayu root; resolve reads from it. Conclusion only at
  **isolated eligibility** level; production dayu-only stays unsigned (I-07-A: no frozen identity).
- **X03 external-only:** NO construction is built (fabricating exclusivity = deleting other copies =
  forbidden; sample_manifest `EXTERNAL-ONLY` is `status: unbound`). Expected outcome = **BLOCKED with
  reason**, NOT NA, with the blocked-proof bundle: manifest unbound rule text + I-07-A blocked-cell
  record + (best-effort) a read-only production location census — if that census cannot complete in its
  bound timeout, that too is recorded as measured (not as a pass).

### Clause 5 — reviewer holdout (NOT mine)
`sample_manifest.unbound_live_samples["HELDOUT-COMPANY"]` is frozen by the INDEPENDENT REVIEWER before
review; it is **SEALED FOR REVIEWER** — this attempt neither reads nor targets it and must not know it.
My only obligation here: prove MY construction is company-agnostic. Frozen check:
`harness/no_hardcode_check.py` greps every `harness/*.py` for (a) CJK ranges, (b) the fixture company
identifiers, (c) ticker/numeric ids, (d) the chosen fifth-root company — expected **0 matches** (harness
derives every company/asset name from `sample_manifest.json`, the sidecars it copies, and
`inputs/fifth_root_company.json` data). Output is published in `evidence/no_hardcode_grep.txt`.
Sample swapping is impossible by construction: all fixture bytes come from the pinned manifest, chosen
data-driven (smallest by `byte_size` for X04, `market=="CN"` for X01, `market=="US"` for X02).

---

## 2. Exit-honesty declaration (verbatim, carries into handoff)

「每个格单独结论，无外部only实证就不签该资格；它不阻止与其无关的已验证本地读场景。」

## 3. Per-cell verdict table schema (filled in decision.md, one conclusion per cell)

| cell | clause | level actually run | conclusion (own) |
|---|---|---|---|
| X04 multi-root | 1 | C (isolated roots + real sample bytes) | … |
| X05 fifth-root | 2 | C | … |
| UNK-adapter / UNK-sidecar / UNK-kind | 3 | C | … |
| X01 companies-only | 4 | C | … |
| X02 dayu-only | 4 | C | … |
| X03 external-only | 4 | none (no sample) | **BLOCKED** … |

## 4. Attack list for the independent reviewer (oracle §7 analogue)

1. Re-hash the two X04 copies yourself; confirm `sources` has exactly 1 row for that sha.
2. Confirm `i07c_fifth_lake` name is absent from PLAN/CW before this attempt (grep it again).
3. Read `harness/*.py` for company literals; rerun `no_hardcode_check.py`.
4. Confirm UNK-adapter stderr really carries CFG-01 (not a harness-invented message).
5. Confirm X03 produced NO isolated construction (directory absent) and the blocked proof is documentary.
6. Confirm the holdout: `HELDOUT-COMPANY` never appears in any of this attempt's files.
7. Confirm snapshot-before == snapshot-after for every product anchor and the three sample hashes.
