# I-07-C review.md — CARRIER LANDING (verdict transcribed by the carrier-landing executor; never self-signed)

Status: **`accepted_scoped`** (card `I-07-C` / attempt `a20260923-01`). The independent reviewer
(独立复核) wrote the verdict in `reviewer_report.md` — the byte-pinned carrier — **not** in this file.
This file is the carrier-landing bookkeeping of that verdict: it transcribes the verdict and, in
substance, the carrier's sections A–D, findings register, unverified list and scope, so the
attempt's `review.md` slot exists. **It is a bookkeeping transcription: it adds no acceptance of
its own.** Read `reviewer_report.md` itself (204 lines) for the reviewer's own words. No verdict,
review, or acceptance was authored in this pass.

`review.md` did not previously exist in this attempt (no implementer stub to preserve); this file
was created by the carrier-landing pass — not by the implementer and not by the reviewer.

## Verdict block (transcribed)

- Card: **I-07-C / attempt `a20260923-01`** (`<PLAN>\execution_runs\I-07-C\a20260923-01`).
- Verdict: **`accepted_scoped`** — the reviewer's literal label is at carrier **line 8**:
  `## VERDICT — \`accepted_scoped\` (signed by this reviewer; implementer never signs)`, with the
  acceptance scope at carrier **lines 10–11**: per-cell signed/blocked status transcribed in §B6
  with the holdout result appended; FINDING C1 accepted as a **downstream finding** routed to the
  REMEDIATION ledger, **fix NOT this card's surface**; inherited carries F1/F2/F3 + the three
  verbatim exit declarations + `overall_three_market_pass=false` + zero-RevenueSourceRecord travel
  with this acceptance; isolated-tree cleanup (`%TEMP%\i07c` + this attempt dir) authorized
  **after** landing per `recovery/README.md`; parent action = batch commit + next chain card
  **I-07-D**.
- Verdict author: **独立复核** — the independent reviewer session dispatched by parent session
  `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`, N=1 signer (carrier lines 3–5: reviewer method =
  read/grep/pwsh only, product trees read-only, runs only into `%TEMP%`, no git command at all, no
  network call; the reviewer's own writes = exactly `reviewer_report.md` + `reviewer_report.sha256`
  + `evidence/reviewer_holdout/**` under declared clause-5 authority). The implementer did not and
  cannot self-sign: this pass measured the handoff pre-image **before any write**: **19156 B /
  sha256 `72c1e853f4864bc7d9640b94a1fdf7f7d3ad14497ab7e6d10b323bc0d719ac34`**, `status:
  review_pending`, `implementer_signed: false`, `review_holdout.flag: "SEALED FOR REVIEWER"`.
- Clause-5 holdout: **SEALED → EXECUTED by the reviewer** (frozen-first, then run) — SCAN arm PASS,
  RESOLVE arm MEASURED NEGATIVE (declared before run, no swap); see §C below and
  `evidence/reviewer_holdout/**` (35 files, declared reviewer write surface — presence verified at
  landing, content not re-opened by this pass).
- This pass **does not self-sign**: `implementer_signed: false`,
  `implementer_never_signs_acceptance: true`; the verdict is **transcribed, not authored**
  (`verdict_is_transcribed_not_authored: true`); this file is a **bookkeeping transcription, adds
  no acceptance of its own**.

### Carrier (byte-pinned)

| field | value |
|---|---|
| carrier file | `reviewer_report.md` (single round; verdict `accepted_scoped`) |
| path inside attempt | `execution_runs/I-07-C/a20260923-01/reviewer_report.md` |
| sha256 | `d5e3e661f9638048e1fc38308f6bb00a7b0b71389d9623bc42b8b54e8e58ecd6` |
| bytes | 40851 (== dispatch figure exactly) |
| lines | 204 (UTF-8 without BOM; LF-only, 0 CR; single trailing LF) |
| pin sidecar | `reviewer_report.sha256` (present, 87 B, sha256 `062b9e8097bf84103850db7cb2948a2d45f8f7b0a5eb3bdedbcb7d011d1cdd57`, content `d5e3e661f9638048e1fc38308f6bb00a7b0b71389d9623bc42b8b54e8e58ecd6  reviewer_report.md`) — **content-match**: equals this pass's independent read-only re-hash ⇒ 0 bytes written by this pass |
| verdict heading line | 8 — byte region start 1184 .. end_incl 1266 (83 B), sha256 `ab20b46455607b9e8bb72c80617f418644b6c3677724f2797e83bb2efcbbc710` |
| acceptance-scope paragraph lines | 10–11 (bytes 1269..2025, 757 B, sha256 `59e4c33bcb1493ad382ca37556178e4b13e2c563cee69390830613a1415034de`) |
| header + method lines | 1–6 (bytes 0..1181, 1182 B, sha256 `1b8944d204735467ae5a1b2776eb2cc183773b43c4093efb2880d280adfea365`) |
| §A lines | 15–33 (bytes 2033..5644, 3612 B, sha256 `e95f885f1f206bb902e463810dab90825761ab5b60e24529d091cc69c2ce6f79`); §A2 35–51 (5647..7681, 2035 B, `55da11073193442d0cbdda7a8262b6c5b7214e9c109a8adb310d2339534d4945`) |
| §B lines | 55–104 (bytes 7689..18290, 10602 B, sha256 `8e74a5ceaaad930e96513ed4211c1aac009cefc63a53fad8b70772e3f1fee012`) |
| §C lines | 108–151 (bytes 18298..28529, 10232 B, sha256 `db1c8264acc8551066d90db680602ce36b78d09d81459b5dac7969cfc1674d18`) |
| §D lines | 155–171 (bytes 28537..34385, 5849 B, sha256 `a22707cfabe8d0456b7f290ae3963545934b41df7f29c559f90c1efa239760b4`) |
| Findings register lines | 173–184 (bytes 34388..38309, 3922 B, sha256 `c245ef75a7172b847162d3a0865d20d6094118716af7f2838ed33a4ee8751ab9`) |
| Unverified list lines | 186–193 (bytes 38312..39309, 998 B, sha256 `be73d8b44df3b8922e892bad4d166fc4d0746fcbf7825ba172b804cf00a8163c`) |
| Authority/writes/cleanup lines | 200–204 (bytes 39964..40849, 886 B, sha256 `f5a14629d1a29f050a9b9bbff11531de6b36cfd76570354fcb2bb080030596ea`) |
| holdout write surface | `evidence/reviewer_holdout/**` = 35 files, 51,522 B, tree-agg sha256 `a94157d09670b58b1be9ba2050dcbcff5e83805f531cd5919d5dce7ecc737164` (presence declared + verified; content not re-opened) |

region definition: byte offsets 0-based against the file as it stands at the recorded sha256;
multi-line regions include internal LFs and exclude the final LF.

## A. Deliverable re-hash (transcribed in substance)

- **8/8 deliverable pins re-hashed live at review and matched**: oracle `b051135a…`, binding
  `d820a3fb…`, commands `6be2131d…`, decision `6e6f4f40…` (pre-annotation pin; post-F-REV-4
  annotation `0fc21ff0…`, see record fixes), changes.diff `e81a33f9…`, handoff `72c1e853…`
  (pre-landing pre-image), recovery/README `5ca0c271…` (pre-annotation pin; post-F-REV-3
  annotation `5d7819f2…`), evidence count 108/108 live files.
- **22/22 evidence pins**: all 15 handoff-pinned evidence files (`fa50ea02…`, `9c678120…`,
  `db666914…`, `feaa5664…`, `5fffaad5…`, `7c2b83d7…`, `a8e5ad92…`, `c8973e9f…`, `b8af73fa…`,
  X05 scan1/scan2 `69b1c6a2…`/`9110df2a…`, X05 resolve1/resolve2 `cc8e774b…`/`3f723869…`,
  UNK-adapter stderr `dbf42c99…`, UNK-kind stderr `b0547011…`) = 15/15 match + all 7 iso_initial
  (`661cfc65… fa2c01f1… dda390a2… 0629804f… 584addbe… 011d0169… 70d527ca…`) = 7/7 match.
- **Frozen-first**: `oracle.md` CreationTime = LastWriteTime = **2026-09-23 14:11:33**; binding
  14:12:47; commands 14:13:35; earliest evidence `snapshot_before.json` 14:29:55; earliest judged
  product run `X04/scan1` 14:31:28 ⇒ oracle frozen before the first judged run and never edited.
- **Adapter-freeze (§A2) all line-reads confirmed**: every oracle §0.2 claim re-read at the live
  product file — `adapter_dispatch.py:29-33/39-53`, `registry.py:10-21/23-48`,
  `config.py:127-136/113-115/166`, `models.py:39/141-142`, `scanner.py:855/1941-1953/866-884/1046/
  83-84/1089-1091`, `store.py:136-142`, `sidecar.py:5-7` — all ✓, hashes match
  `binding.json.product_adapter_dispatch`.
- **16 anchors + 6 sample files (3 raw + 3 sidecar) double re-hash by the reviewer = 0 mismatches,
  0 missing**; `changes.diff` before=16 after=16 changed=[]; matrix `0dec23cd…`, manifest
  `d5d0bb92…`, card `c3c3f533…` (14 lines) all match.
- **Handoff state at review** = the pre-image recorded above; exit-honesty declaration
  byte-identical to oracle §2 and decision §0; three inherited verbatim declarations present.
  `HELDOUT-COMPANY` carried no identity fields before the freeze (nothing existed to know).

## B. Per-cell re-verification (transcribed in substance; reviewer's own executions)

- **B1 X04 (clause 1)**: both fixture copies re-hashed live (each 4,405,561 B, `ffd73376…` ==
  manifest; sidecars `8228741d…`); **own sqlite query** (mode=ro + query_only): sources=1,
  documents=1, locations=2 across distinct roots, both `original_primary/active/error=NULL` ⇒
  claim confirmed; **own resolve re-run** rc 0, `reused_equivalent`,
  `one_existing_source_satisfies_semantic_request`, no catalog row-count change.
- **B2 X05 (clause 2)**: **independent 12-scope recompute** (own script, their rules):
  0 fixture matches / 8 universe-dump matches / 17 positive-control scopes / **PASS** —
  reproduces their numbers exactly (1,650 scope files; controls 81/32/24 for
  紫金矿业/小米集團－Ｗ/MICROSOFT CORP); the 8 `security_master` hits classified by the reviewer =
  4 files × tokens {NOVO, NVO}; raws verified (265 B payload + 1,014 B sidecar carrying the J1
  `source_url` completion); J1 run1 preserved and coherent (`capture_incomplete`, `outcome:
  missing`, `matches: []`); scan2 strategy `i07c_fifth_lake: adapter`, 1 document/1 source/1
  location; **own resolve2 re-run** rc 0, `reused_equivalent` / `reused_existing` /
  `qualification: verified_input`, no row-count change.
- **B3 clause 3 + C1**: **four byte-identical own re-runs** of the two refusals (frozen argv) —
  UNK-adapter scan & resolve rc 1 with `CatalogConfigError: … not registered (CFG-01)`
  (`config.py:129` via `cli.py:868`); UNK-kind scan & resolve rc 1 with `ValueError: unsupported
  root kind` (`models.py:142`) — stderr byte-identical to the evidence in all four; UNK-sidecar
  scan deliberately NOT re-run (state kept for observation (d); C1 substance verified read-only).
  **C1 confirmed**: promise `sidecar.py:5-7`, reasons computed at `sidecar.py:60/74`
  (`_validate_sidecar:90-119`), `NormalizedCandidate.evidence` exists (`adapters/interface.py:26`),
  but `adapter_dispatch._to_scanner_candidate:57-76` copies only `normalized` and never `evidence`
  / never sets `_Candidate.error` (`scanner.py:67`, wiring `scanner.py:1099` exists) ⇒ **catalog
  query: all 4 probe locations `error=NULL`, no remediation key anywhere** — role-level explicit,
  reason-level invisible; severity = measured downstream defect, **not this card's fix surface**.
- **B4 X01 / X02 scoping quotes**: X01 `resolve1` rc 0, 1 match, `content_sha256 01819e1c…` ==
  pin; the scoping quote (*production companies-only NOT signed — I-07-A CN uniqueness DISPROVED*,
  same content hash as original_primary under company_raw AND dropbox_stock, 79,925,886 B) verified
  against I-07-A `handoff.json` + `after/state_matrix.md` + `r2_review_facts.json`; X02 `resolve1`
  rc 0, `content_sha256 e3de0053…` == pin, `entity_ids: [ticker:MSFT]`; *production dayu-only NOT
  signed — no frozen identity, 3660 dayu locations* matches I-07-A's carrier and the reviewer's own
  census ⇒ both signed **only at isolated-eligibility level**.
- **B5 X03 blocked + census**: blocked wording complete (BLOCKED not NA; unbound-rule quote;
  existence ≠ eligibility / exclusivity manufacture forbidden; does not block unrelated verified
  local read scenarios; no isolated tree built) ✓; `%TEMP%\i07c\cells\` shows exactly 7 cells, no
  X03 tree; **census SQL re-run identical** by the reviewer (same SQL, read-only): `company_raw
  33092 / dayu_portfolio 3660 / dropbox_stock 9853 / future_lake 1`, `documents 23530`,
  `external_only_candidates 6411` — identical to their records and to I-07-A r2 facts.
- **B6 per-cell verdict table** — see Scope section below (7 rows, holdout row appended).

## C. Clause-5 HOLDOUT — reviewer-frozen 洛阳钼业 603993 FY2021 (transcribed in substance)

- **C0/C1 freeze-first**: pool = every registered active `original_primary` ≤ 25,000,000 B
  sidecar/meta-bearing row across the three sidecar-shaped roots (7,509 / 9,211 / 49 ⇒ **10,596**
  after layout filters), census methodology only, no big bytes opened before the chosen small file
  was hashed; screening = implementer's exact `non_fixture_grep.py` rules (12 scopes, 1,650 files,
  positive control 81/32/24 ✓). Sample **frozen and recorded in the report BEFORE any product
  run**: 洛阳钼业 (CMOC Group) **603993**, CN, FY2021 `annual_report`; file 6,610,553 B sha256
  `dfeb7c54c3b7c658030851fd406f538a28d4e9a9d04eac2eab8179854725e12a`; filing meta 2,802 B
  `4f99016d21b246484ff134f25d4effc0c6ed90fffb11fa19e0bf279e197d92cb`; entity meta 241 B
  `5ec07ea534544726b311eaf60fb0627e92289e1115f458c832ee8482d2a1f786`; registered real location
  (dayu_portfolio, `original_primary`, active, `annual_report`, published 2022-03-18, provider
  cninfo, source_id 1212626342, `document_id urn:company-wiki:document:sha256:dfeb7c54…`).
  Criteria: **(i) 0 fixture hits** across all 12 scopes + `named_in_attempt []` (only disclosed
  universe-dump hits) with the positive control passing on the same run; **(ii) differs** from the
  implementer's fifth-root company **诺和诺德** and from every recorded rejected candidate (贵州茅台,
  宁德时代/300750, 万华化学/600309, 000858, 600519); (iii) real registered location, small file.
  Construction = their cell-harness pattern with holdout root `reviewer_holdout_lake`
  (`dayu_portfolio` + `dayu_filing_v1` + `financial_evidence_v1`, read_only, reusable — all inside
  oracle §0.2's frozen set); builder carries **0 company literals** (grep-verified before running).
  **Expectation declared before running**: scan rc0 with strategy `adapter`; resolve expected
  `missing` because the sample's registered `source_url` is `http://static.cninfo.com.cn/…` and
  `resolver.py:1919-1925` nulls non-`https://` URLs ⇒ if measured so, recorded as a **MEASURED
  NEGATIVE with exact quotes — no sample swap** (swap forbidden by card + binding).
- **SCAN arm — PASS (generalization)**: my execution after the freeze — rc **0**, errors 0,
  files_seen 2; product's own strategy map
  `{"…":"legacy", "future_lake":"adapter", "reviewer_holdout_lake":"adapter"}` ⇒ **the same
  adapter/profile dispatch ran** (`dayu_filing_v1` + `financial_evidence_v1`), no product code
  changed; registered 1 document (`洛阳钼业2021年年度报告`), 1 source, 2 locations
  (`original_primary` + `metadata`, both `error=NULL`), entity
  `unresolved:reviewer_holdout_lake`, **`document_id` == the production document id for the same
  bytes** (content-addressed identity held across roots).
- **RESOLVE arm — MEASURED NEGATIVE, declared before run, no swap**: rc 0, **no row-count
  change**; envelope: `status: missing`, `reason: no_existing_source_satisfies_request`,
  `outcome: missing`, `matches: []`, `qualification: null`, `download_allowed: false`,
  `prompt_injection_status: not_reviewed`,
  `debug_trace: ["entity_gate_rejected: 0", "洛阳钼业2021年年度报告: capture_incomplete"]` ⇒
  **entity gate accepted the previously-unnamed company with 0 rejections = no company-name
  hardcoding was needed**; the single exclusion is the **capture gate on the sample's cninfo
  `http://` source URL** (`resolver.py:1919-1925`), exactly as declared. Extra corroboration for
  observation (d): after this missing resolve, `document_fingerprint_state = 0`.
- **→ F-REV-7 (medium, downstream)**: across all **10,596** registered active ≤25 MB
  sidecar/meta-bearing rows, **`criterion-(i)-eligible ∩ https-source_url-capable = 0`** (eligible
  6,443; https-capable 45 rows all belonging to fixture-visible companies) — a downstream
  product/data gap (capture-readiness of non-fixture companies), **not this card's fix surface**;
  routed to the REMEDIATION ledger with the holdout envelope as evidence.
- **C3 no-hardcode recompute (clause-5 obligation)**: reviewer's own recompute over the same 10
  harness files: **5 unmasked CJK matches = `C:\Users\<USERNAME>\…` path artifacts**
  (`i07c_common.py` L15/16/17, `snapshot.py` L44/45), **run1 preserved**
  (`no_hardcode_grep.run1_username_falsepositive.txt`); **masked = 0, TOTAL 0** reproducing the
  published `7c2b83d7…`; extra probes `NVO` / `Novo Nordisk` / `诺和诺德` / `i07c_fifth_lake` =
  **0 occurrences in all 10 files** (documentation defect F-REV-4 noted).

## D. Disclosures & boundaries (transcribed in substance)

- **J5 coherent**: `commands.json` pre-declared rc 0 for UNK-kind, measured 1 raw in both entries;
  oracle §1 3c hand-reasoned config loads (kind not validated at `config.py:166`); decision J5 +
  handoff `expected_exit_codes` record deviation + cause (`models.py:39/141-142` ROOT_KINDS missed
  at freeze); **oracle hash unchanged** ⇒ declared-vs-measured recorded raw, oracle untouched,
  refusal satisfies clause 3.
- **Three rc=1 statuses**: (3) prod_census run1 thread error — artifact preserved
  (`prod_census.run1_threaderror.json`, PARTIAL, `catalog_bytes 49677344768`) with fixed run2 3/3
  OK; (1) first UNK-resolve attempts before `resolve_request.json` existed and (2)
  `summarize_cells` run1 KeyError — **declared in `handoff.raw_exit_codes` only, no run1 artifact
  exists for either** ⇒ recorded as partially evidenced, not a measurement defect (both failures
  wrote no evidence by definition).
- **Observation (d) — REFINED**: isolated catalogs show `document_fingerprint_state` = 1 only in
  X05 + UNK-sidecar; timing from their own dumps puts the +1 at the **second scan**, not at the
  missing resolve (dump after resolve1 = 0); the reviewer's own **discriminator probe** on the
  reused cell X01 (frozen scan argv): 0→1 with `scan_runs 1→2` ⇒ **a second scan alone creates the
  row**; cross-check of I-07-B's carrier shows a third, scan-free trigger (RF `source_preparation`
  ensure path, `S-CN-3/run3`). **Classification: the missing-resolve theory is dropped** — for the
  parent's inherited I-07-B open item, **the parent must check scan/ensure triggers** for the
  `document_fingerprint_state+1` item; still timing-consistent, causal unproven for I-07-B itself.
- **Catalog size RESOLVED**: true size = **49,677,344,768** (reviewer live stat, mtime
  2026-09-19T06:31:35.406919Z; snapshots before/after; prod_census + run1; census re-run — all
  agree); the figure `…476` occurs in **exactly one place, `recovery/README.md` line 41 = F-REV-3**
  (digit transposition, fixed at landing by annotation — see record fixes).
- **Close boundary**: 16 anchors + 6/6 samples re-hash 0 mismatches; production catalog size+mtime
  unchanged; **four real-root manifests identical** (CW/companies 33126 / 25,173,794,322;
  CW/future_lake 1 / 545 + full sha; dayu portfolio 3,732 / 2,044,173,414; Dropbox/Stock 10,342 /
  15,742,131,522 — counts/bytes/max-mtime each ✓) ⇒ **`no_mutation: true`**; **cell-tree diff =
  exactly 1 of 95 pinned files, its own disclosed observation-(d) probe** (`X01 … catalog.sqlite3`
  245,760 → 258,048 B; all other reviewer re-runs changed no row count); **git_commands_run = 0**
  (no git verb in any recorded argv; the only git string is binding's forbidden-list line);
  **network = 0** (`network: disabled by construction` on every entry; no `download` /
  `--allow-download` in any recorded argv; reviewer's own runs local-only).

## Findings (reviewer register F-REV-1..8 — dispositions transcribed)

| id | severity | finding (substance) | disposition |
|---|---|---|---|
| **F-REV-1** | medium, downstream | C1 confirmed by independent re-execution: reasons computed (`sidecar.py:60/74`) but dropped at `adapter_dispatch._to_scanner_candidate:57-76` ⇒ `locations.error=NULL` ×4; reader sees `indexed_only` but never the cause | accepted as this card's recorded FINDING C1 → **REMEDIATION ledger**; **fix NOT I-07-C's surface** (clause 3 = explicit refusal/no-guessing, satisfied) |
| **F-REV-2** | low | `handoff.completed_steps[6]` said "9 product CLI runs (7 scans … 7 resolves)"; measured = **9 scan dirs + 8 resolve dirs = 17** (`commands_executed`/`raw_exit_codes` already correct) | **FIXED HERE during landing**: count fields corrected (re-counted live: 9+8=17); original text retained in `__history`; no measurement depends on it |
| **F-REV-3** | low | `recovery/README.md` line 41 recorded 49,677,344,476 while every measurement says 49,677,344,768 (digit transposition) | **FIXED HERE during landing**: correction line appended after line 41 (`[F-REV-3 correction: true size=49,677,344,768 …evidence…]`); pinned figure NOT rewritten; pinned pre-image `5ca0c271…` retained, post-annotation sha in handoff bookkeeping |
| **F-REV-4** | low | decision §5 listed `NVO` among patterns; published list = 7 tokens, checker `len>=4` drops the 3-char ticker | **FIXED HERE during landing**: one-line annotation appended after §5's paragraph; original wording retained; conclusion unaffected (reviewer probe: `NVO` absent from all 10 harness files) |
| **F-REV-5** | medium (parent's open item) | observation (d)'s suggested mechanism not supported by I-07-C timing: +1 at the **second scan**, scan-count alone suffices; I-07-B shows a third scan-free (RF ensure) trigger | **carried to parent as a refined lead** for I-07-B's inherited `document_fingerprint_state+1 not root-caused` item: **missing-resolve theory dropped; check scan/ensure triggers** |
| **F-REV-6** | info | "…before construction" wording: published non-fixture evidence (14:51–14:52) postdates cell build (14:21) and first scans (14:31); no pre-construction artifact | noted — substance independently re-verified by the reviewer (0 fixture hits, control pass); only the timing word unevidenced |
| **F-REV-7** | medium, downstream (from the holdout) | `eligible ∩ https-source_url-capable = 0` across **10,596** rows; capture gate requires `https://` while eligible metadata has none or `http://static.cninfo…`; measured end-to-end by the holdout (scan rc0 adapter; resolve missing/capture_incomplete with `entity_gate_rejected: 0`) | downstream product/data gap, **not this card's fix surface** → **REMEDIATION ledger** with the holdout envelope as evidence |
| **F-REV-8** | info | dayu-path adapter provenance not persisted: holdout document `metadata_json.acquisition = null` (no `adapter_id`), unlike X05's `sidecar_filing_v1`; strategy map is the only carrier | noted only (observability family with C1); no action required for I-07-C |

## Unverified / not claimed (carried, transcribed)

1. Production rows were not re-derived per document; no production write of any kind (mode=ro +
   `query_only` for every catalog open the reviewer made).
2. The 6,411 external-only structural candidates were not qualification-checked (existence only —
   same scope as the implementer's §8).
3. Evidence files: **22 of 108** re-hashed (all 15 handoff-pinned + all 7 iso_initial); the
   remaining 86 were read/spot-checked but not individually hashed.
4. rc=1 harness events (1) and (2) have no preserved artifact — declared only.
5. No live (L) level qualification attempted or granted; `overall_three_market_pass=false` and the
   zero-RevenueSourceRecord fact travel unchanged.
6. The holdout result is a **C-level** statement about this product build at these hashes; nothing
   about accuracy or three-market readiness.

## Scope (per-cell table + holdout row; cleanup authorized after landing)

Source: carrier §B6 table (lines 94–104) + verdict scope (lines 10–11); the acceptance is WITH
this scope.

| Cell | Clause | Level | Implementer conclusion | Reviewer status |
|---|---|---|---|---|
| X04 multi-root | 1 | C | CONCLUDED/signed: 1 source + 1 document + 2 locations, both copies == pin, resolve `one_existing_source_satisfies_semantic_request` | **SIGNED** (independently re-verified: hashes + own SQL + own resolve re-run) |
| X05 fifth-root | 2 | C | CONCLUDED/signed: unnamed root + non-fixture company completes scan(strategy=adapter) + resolve(reused_existing, verified_input); J1 disclosed, run1 kept | **SIGNED** (independently re-verified: 12-scope grep recompute + raws + own resolve re-run) |
| Unknown layout ×3 | 3 | C | CONCLUDED with FINDING C1 (load-time refusals explicit; remediation reasons dropped) | **CONCURRED**; C1 re-verified live (4 own runs + code + catalog) |
| X01 companies-only | 4 | C | ISOLATED eligibility signed; production companies-only NOT signed (I-07-A uniqueness disproved) | **SIGNED at isolated level** (scoping verified vs carriers) |
| X02 dayu-only | 4 | C | ISOLATED eligibility signed; production dayu-only NOT signed (no frozen identity) | **SIGNED at isolated level** (scoping verified vs carriers) |
| X03 external-only | 4 | none | **BLOCKED (not NA)**, documentary + census proof | **BLOCKED confirmed** (no tree; census reproduced; wording complete) |
| **Clause-5 holdout (reviewer)** | 5 | C | not run by implementer (SEALED) | **executed by the reviewer** — SCAN **PASS** (strategy adapter, `document_id` == production id); RESOLVE **MEASURED NEGATIVE** declared-before-run, no swap (`entity_gate_rejected: 0`; exclusion = capture gate on cninfo `http://` URL, `resolver.py:1919-1925`) → F-REV-7 |

- Exit declarations carried with the acceptance: `exit_honesty_declaration_verbatim`
  (「每个格单独结论…」) + the three inherited verbatim declarations + `overall_three_market_pass=false`
  + zero-RevenueSourceRecord; `disclosure_adaptation: unmapped`; `accuracy: unproven` unchanged.
- Findings routing: F-REV-1 and F-REV-7 → REMEDIATION ledger; F-REV-2/3/4 fixed HERE at landing;
  F-REV-5 carried to the parent as the I-07-B open-item lead; F-REV-6/8 noted.
- **Cleanup authorized after landing** per `recovery/README.md` (`%TEMP%\i07c` + this attempt dir),
  followed by the README's post-recovery re-hash witness; parent next = **batch commit +
  I-07-D**.

## Record fixes applied at this landing (F-REV-2/3/4 — corrected + original retained)

| file | fix | sha256 before → after |
|---|---|---|
| `handoff.json` | F-REV-2: `completed_steps[6]` counts "9 runs /7 scans /7 resolves" → measured "17 runs (9 scans + 8 resolves)" (re-counted live: 9 scan dirs + 8 resolve dirs); original retained in `__history`; `commands_executed`/`raw_exit_codes` untouched (already correct) | `72c1e853f4864bc7d9640b94a1fdf7f7d3ad14497ab7e6d10b323bc0d719ac34` → (final sha recorded in `evidence/I-07-C/qualification.json`; self-excluded inside handoff.json) |
| `recovery/README.md` | F-REV-3: correction line appended after line 41; pinned wrong figure retained, not rewritten | `5ca0c271c83227b75a921a59ef283d23a364d5beed4f4c876f9af525d0dabd86` → `5d7819f215c75b5c88a214ba7875f9503a7e4752a2a3a3d577d019bdb6519bcf` (3,595 B) |
| `decision.md` | F-REV-4: one-line annotation appended after §5; original pattern-list sentence retained | `6e6f4f40079e365974fbab522967fb2c5b252060f6554c4b4fe3f67729045452` → `0fc21ff056267bb4b39213ff30840f9bde7b20eaf4416a600d0ea9aa09ba7340` (20,277 B) |

Reviewer surfaces untouched by this landing: `reviewer_report.md` (40,851 B / `d5e3e661…`),
`reviewer_report.sha256` (87 B / `062b9e80…`), `evidence/reviewer_holdout/**` (35 files / 51,522 B
/ tree-agg `a94157d0…`); git writes 0; network 0; product/production writes 0.
