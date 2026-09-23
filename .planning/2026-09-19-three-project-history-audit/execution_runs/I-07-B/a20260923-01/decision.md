# I-07-B decision.md — attempt a20260923-01 (九步 protocol → review_pending)

Implementer did NOT self-accept; status = `review_pending`, independent review follows separately.
All runs used the real entry (`RF/scripts/source_preparation.py`) in an isolated chain.
Product writes = 0; CW writes = 0; production catalog opened only `mode=ro`/stat; no git in the
command registry (see J7 for one disclosed pre-binding git deviation); network only for the
card-scoped live reachability probe and the C-level frozen provider simulation.

## 0. The three exit-honesty declarations (verbatim, from card line 14) + measured reality

1. `三公司仅来源准备通过，仍未授予正式预测资格。`
2. `缺一市场/真实路径不得总体写三市场通过。`
3. `恢复：保留已取得raw，只回退当前隔离变更。`

**Overall three-market statement: NEGATIVE (no overall pass is claimed).** Per declaration 2,
the L (live) row is blocked for all three markets (unbound sample identity + no download
authority), so an overall "三市场通过" is forbidden regardless of S-cell results. Per the
measured results below, **not even a source-preparation record was produced for any of the
three companies**: every entry run ended rc=3 at the prompt-injection review gate or at
resolve-missing. Declaration 1 is carried verbatim as the card's ceiling language; the measured
state is below it and stricter (no `RevenueSourceRecord` exists anywhere in this attempt).

## 1. What was executed (commands are registry-bound in commands.json)

- 11 isolated case trees (9 matrix cells + 2 registration-failure cases) under
  `%TEMP%\i07b\cases\<id>\cwroot`, each with a **product-isomorphic 18-table catalog** created
  by the product's own `CatalogStore._initialize` (I-07-A prohibition satisfied), a rebound
  config, real sample bytes (hash-checked at build), and the production security-master JSONs.
- Judged runs (frozen argv, wrapper evidence `evidence/cases/<id>/runN/argv.json`):
  S-*-1 ×2, S-*-2 ×2, S-*-3 ×3 per market (unauthorized / authorized+frozen-sim / repeat),
  REGFAIL-{HK,US}: scan-under-lock → scan-after-release → entry ×2. Total entry runs: 12+9+4 = 25;
  scan-stage runs: 4; plus WPROBE, LIVE-PROBE, SNAPSHOT before/after, ISO base/case/final, DRIFT.
- Registration stage uses the product's OWN registration entry
  (`python -m company_wiki.source_catalog.cli … scan`, cwd = isolated root) because
  **code map Q2: neither `resolve` nor `ensure` ever scans** — measured independently by every
  state-2 entry run returning `missing / no_existing_source_satisfies_request` with
  `catalog_delta = {}` (no scan counter, no rows).

## 2. Case matrix results (per cell × per clause)

Legend for stages: ✅ pass measured · ❌ measured fail · ➖ precondition unmet/blocked · n/a not reached.
"recovery" = C2.2 structured actionable-recovery parser result. Counters = run1/run2 deltas
(`provider/scan/read/producer`); all counts are call-spy counts from `sitecustomize` wrappers
(wprobe: `zero_insert_proof=true`).

| case | raw | 注册 | 资格 | review | 适用工件 | 消费 | refusal message (measured) | recovery (C2.2) | counters r1 / r2 | provider downloads | cell verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S-CN-1 | ✅ rehash=01819e1c… | ✅ (prod-copy rows, 0 delta both runs) | ✅ handle built (read=2 byte verification) | ❌ `not_reviewed` | n/a | ❌ rc3 | `prompt injection not reviewed … blocked per policy` | ❌ explicit missing info (NL) but NO structured field | read2/read2, scan0/0, provider0/0, producer0/0 | 0 / 0 | **NOT passed** — matrix input state ("真实审核已合格") does not exist in production (measured `prompt_injection_review` absent); chain refuses at review gate |
| S-HK-1 | ✅ rehash=ffd73376… | ➖ 0 rows in production observation | ❌ | ➖ | ➖ | ❌ rc3 | `missing / no_existing_source_satisfies_request` | ❌ (reason string only) | all 0 | 0 / 0 | **NOT passed** — precondition "已索引" unmet (production fact); refusal itself is correct + names missing source |
| S-US-1 | ✅ rehash=e3de0053… | ➖ 0 rows | ❌ | ➖ | ➖ | ❌ rc3 | same not_found | ❌ | all 0 | 0 / 0 | **NOT passed** — same as HK |
| S-CN-2 | ✅ | ➖ not registered; **entry cannot register (F1)** | ❌ | ➖ | ➖ | ❌ rc3 | not_found | ❌ | all 0, catalog delta {} | 0 / 0 | **NOT passed** — matrix operation "第一次从入口恢复注册" is not achievable by the current product entry (resolve/ensure never scan; only `cli scan` registers) |
| S-HK-2 | ✅ | ➖ same | ❌ | ➖ | ➖ | ❌ rc3 | not_found | ❌ | all 0 | 0 / 0 | **NOT passed** (F1) |
| S-US-2 | ✅ | ➖ same | ❌ | ➖ | ➖ | ❌ rc3 | not_found | ❌ | all 0 | 0 / 0 | **NOT passed** (F1) |
| S-CN-3 | ✅ after sim download hash=01819e1c… | ✅ run2: documents+1, sources+2, locations+2, roots+1 | ✅ (reached review) | ❌ `not_reviewed` | n/a | ❌ rc3 | run1 not_found; run2/3 `not_reviewed` | ❌ structured / ✅ explicit missing info | r1 all0; r2 provider2(read4); r3 provider0(read2) | **0 / 1 (discover+fetch spy; fetch=1, `simulated:true`) / 0 repeat** | **matrix criteria PASS at C level** (0/1/0 downloads, registration qualified, spy counts, C-qualification only); chain still refuses at review gate |
| S-HK-3 | ✅ (registered; canonical path name differs from manifest name — see open items) | ✅ same deltas | ✅ | ❌ | n/a | ❌ rc3 | same pattern | ❌ / ✅ | same as CN-3 | 0 / 1 (simulated) / 0 | **matrix criteria PASS at C level** (same caveats) |
| S-US-3 | ✅ hash=e3de0053… | ✅ same deltas | ✅ | ❌ | n/a | ❌ rc3 | same pattern | ❌ / ✅ | same as CN-3 | 0 / 1 (simulated) / 0 | **matrix criteria PASS at C level** (same caveats) |
| REGFAIL-HK | ✅ unchanged both runs | ❌→✅ scan1 under lock: rc1 `catalog_busy retryable=true`, 0 rows; scan2 after release: rc0, documents+1/sources+2/locations+2 | ✅ entry reached review | ❌ `not_reviewed` (explicit missing info) | n/a | ❌ rc3 | scan1 `{"error":"database is locked","error_type":"catalog_busy","retryable":true}`; entry `not_reviewed` | ❌ structured (only error_type/retryable) / ✅ explicit missing info | scan1 scan1; scan2 scan1+read2, **provider0 (no re-download)**; entry r1/r2 read2,provider0,scan0,producer0, catalog delta {} | 0 / 0 (0 new) | **PASS on the recovery mechanics** (raw kept, failure structured, idempotent recovery without download, old-failure sample returns to same user entry with explicit missing info); C2.2 structured-recovery FAIL recorded |
| REGFAIL-US | same as HK | same | same | same | n/a | ❌ | same | same | same | 0 / 0 | **PASS on recovery mechanics**, same C2.2 FAIL |
| L-CN / L-HK / L-US | ➖ | ➖ | ➖ | ➖ | ➖ | ➖ | no chain run: `sample_manifest.unbound_live_samples` identity unbound, no download authority for this card | n/a | n/a | live call: NONE | **blocked** (reachability probe only: CN 200, HK 200, US 403-but-reachable; `unreachable_markets=[]`) — a blocked market forbids the overall pass (declaration 2) |

**重复请求 (second run of same input)** — measured for every case:
- `provider` delta run2 == **0** for all state1/state2/REGFAIL cases (valid raw never downloaded twice; neither run downloads without `--allow-download`); the authorized S-3 arm's *repeat* is run3: provider delta **0** after run2's simulated download+registration.
- `producer` delta **0 in every run of every case** (valid artifacts never re-produced; the chain plans producers but does not run them).
- No duplicate registration: post-run1 → pre-run2 catalog row counts **identical** (REGFAIL entry r2 `catalog_delta={}`; S-3 run3 grows only `document_fingerprint_state` (a normalizer-state row), never documents/sources/locations).
- Read-only queries non-zero (`read=2` per resolve re-verification) — explicitly allowed by the card.
- Asset bytes: production raw/sidecar 3/3 unchanged (before vs after snapshot); isolated raw unchanged in every state1/state2/REGFAIL run.

## 3. Card's five clauses — verdicts

- **C1 (freeze initial state + real invocation counters)**: **PASS**. Per-case
  `initial_state.json` (asset hashes, 18-table catalog counts, worker-control absent) frozen
  before run1; `counters/before_runN.json` + `after_runN.json` baselines per run; wiring targets
  frozen in `binding.json:counter_wiring`; WPROBE proves each counter increments on a real
  wrapped invocation with **zero INSERTs** (`evidence/wprobe.json:zero_insert_proof=true`,
  totals scan2/read2/provider2). Producer wiring is proven by wrap status + 0 measured
  invocations (cannot be inertly invoked without a real document — recorded, not hidden).
  No reported count derives from an artifact/producer_events INSERT.
- **C2 (one frozen-argv run + stage evidence + actionable recovery on refusals)**: stages
  evidenced per run (`evidence/cases/*/runN/evidence.json:stages`), **but C2's refusal clause
  FAILS for every refusal**: the only structured fields ever emitted are
  `{error_code,error,retryable}` / `{error_type,retryable}` — no `candidates`/`next_action`/
  `required`/`gap_plan` on any failure path (matches code map Q7 and I-06-A's unsigned
  recovery interface). Refusals DO name the missing condition in natural language
  ("prompt injection not reviewed" / "no_existing_source_satisfies_request"), which satisfies
  the explicit-missing-info arm of clause 4, not the structured-recovery requirement of clause 2.
- **C3 (second run)**: **PASS** per the 重复请求 block above (downloads 0, no re-registration,
  producer 0, read-only queries allowed non-zero, bytes unchanged).
- **C4 (deep verification beyond json fields)**: **partially exercised, honestly unexecuted at
  its value arm**: no run emitted a `RevenueSourceRecord`, so handle/period/receipt value
  assertions (`deep_verification`) have nothing to verify and are recorded as
  `skip_reason: refusal path — C4.2 arm applies`. The C4.2 arm (explicit missing info) passes
  wherever the refusal names the missing condition (it does, in all refusals). The
  identity/hash/period deep-reads DID occur inside the chain (spy `read` events = real
  byte reads re-verified by the product: CN rehash matched, S-3 post-download rehash matched
  the frozen sha), but no consumer output exists to check. Reviewer should treat C4's value arm
  as **not yet earned** — it is gated by the review receipt (D-W06/I-06), not by this card.
- **C5 (live provider)**: **PASS as a record**: `evidence/live/reachability.json` records each
  host, URL, auth-target description, header NAMES only, status/latency; CN 200, HK 200,
  US 403 (network reachable; SEC refused the request), `unreachable_markets=[]`. No live call
  was simulated and no simulated event was labelled live (every spy event carries
  `simulated:true/false`; all sim events are `true`). L cells stay blocked for unbound
  identity/authority — reachability alone never grants them.

## 4. Exit-honesty assertions (explicit, per the card)

- **Per-company**: CN / HK / US each have actual results for S-1, S-2, S-3 (and REGFAIL for
  HK/US) — measured, per-case, in §2. None produced a `RevenueSourceRecord`.
- `三公司仅来源准备通过，仍未授予正式预测资格。` — carried verbatim; measured reality is
  stricter (see §0): no company even reached source-record production.
- **No overall three-market pass is asserted**: `缺一市场/真实路径不得总体写三市场通过。`
  The L row is blocked for all three markets ⇒ the overall statement is negative, and it is
  negative in this decision.
- **Recovery**: `恢复：保留已取得raw，只回退当前隔离变更。` — see recovery/README.md; raw
  obtained this attempt (isolated copies + the three simulated-download canonical imports)
  are retained; only isolation artifacts are reverted (the `%TEMP%` trees may be deleted only
  after review, per README).

## 5. Before/after hashes (measured)

- production catalog `C:\…\company-wiki\.source_catalog\catalog.sqlite3`: **49 677 344 768 B**,
  `mtime_ns 1789799495406919100` — **identical before and after**; `-wal` 0 B both; `-shm`
  32768 B both, its **mtime advanced** (read-only connections touch the shm index — disclosed,
  not hidden; no write statement ever issued against production: SELECT-only + `query_only=ON`).
- product/plan anchors: 20 hashed anchors **identical before/after** (sha256 listed in
  `evidence/snapshot_{before,after}.json`; e.g. `source_preparation.py 91a6dc32…`,
  `fetch_filing.py 046cc7dc…`, `store.py 1a783240…`, `CW/config/source_catalog.yaml f9eb72a6…`).
- production samples: raw 3/3 and sidecar 3/3 **match the frozen manifest in both snapshots**
  (CN `01819e1c…` 79 925 886 B, HK `ffd73376…` 4 405 561 B, US `e3de0053…` 8 585 615 B).
- frozen plan inputs (corrected capture — see J8): card `bd09eb6c…`, scenario_matrix
  `0dec23cd…` (matches `validation.json`), sample_manifest `d5d0bb92…`, I-00-B contract
  binding `fdb2a598…` / commands `f8a397ec…` / oracle `e9c82fe4…`, this attempt's oracle
  `b92b6650…` (written before the first judged run).

## 6. Judgment calls (recorded for the reviewer)

- **J1 — state-1 precondition is unmet for ALL three markets, measured.** Production CN has
  registration + 2 artifacts but **no `prompt_injection_review` receipt**; HK/US have 0
  registration rows. The matrix forbids hand-filling green, and no CLI exists to record a
  review (code map Q4; Python-only `record_prompt_injection_review`; D-W06 OPEN-4 unsigned).
  I did not fabricate any state: S-*-1 ran against the real production-observation state and
  its result is recorded as measured (refusal at the true furthest stage reached).
- **J2 — registration is unreachable from the entry (finding F1).** `resolve` is a strict
  read-only catalog lookup and `ensure` never scans either (code map Q2/Q3): a present-but-
  unregistered raw can only be registered by `cli scan` (the worker's path). The matrix's
  S-*-2 operation ("第一次从入口恢复注册") therefore **cannot pass on the current product**;
  recorded as the cell's measured failure, not worked around. The registration stage was
  nevertheless exercised through the product's own scan entry in the REGFAIL cases.
- **J3 — registration-failure injection choice.** The F02 shape (`scan → completed_with_errors`)
  would require fabricating a scan result (forbidden); I used the F03 shape the matrix also
  sanctions (scratch-only DB write lock on the ISOLATED catalog): real product failure path,
  real structured error, raw preserved, idempotent recovery after release with 0 downloads.
- **J4 — case trees live in `%TEMP%\i07b\cases`.** The attempt path + US file names exceed the
  Windows 260-char limit and the PRODUCT opens them with plain APIs (would fail regardless of
  harness). Allowed by the card's write scope (`%TEMP%/isolation only`); recorded in binding +
  recovery README.
- **J5 — frozen provider simulation** (S-*-3 b/c) replaces the four adapter `discover/fetch`
  entry points with fixture-serving implementations (fixture identity taken from each sample's
  own frozen sidecar + on-disk bytes). Every event is spy-labelled `simulated:true`; this is
  the C-level arm the matrix itself prescribes ("provider使用冻结模拟返回") and is never cited
  as live. Isolation scaffolding created only the **empty** declared adapter project_root dirs
  (`acquisition_config` + adapter `__init__` do `resolve(strict=True)`) — no fabricated
  executables, no fabricated data files (`evidence/adapter_scaffolding.json`).
- **J6 — anchor drift vs I-00-B is real and recorded, not hidden** (`binding.json.anchor_drift_vs_I00B`):
  `source_preparation.py 5ec16eaf→91a6dc32` (W05-B verify_artifact_reads added),
  `revenue_forecast.py 6b3d960e→2a2dfede` (EOL-only text diff), `CW cli.py 2f5c5740→fad88c60`
  (no I-00-B-era copy available without git ⇒ content diff not reconstructable here), plus
  `filing_fetch_client.py`/`company_wiki_source.py` drift vs I-06-A's pristine copies
  (257-line diff for company_wiki_source). Diffs in `evidence/anchor_drift/`. Per START_HERE
  this requires the dispatcher to refresh the I-00-B anchor table and the reviewer to re-check
  the oracle against current bytes — **open item, carried**. No product file was written by
  this attempt (before/after anchors identical).
- **J7 — disclosed process deviation:** BEFORE this binding was written I ran one read-only
  `git diff --no-index` (to compare two RF scripts), which the card's "no git" command rule
  forbids as a *command*. Its two outputs were immediately **replaced** by the difflib harness
  (`CMD-I07B-DRIFT`) and the deviation is recorded here and in binding.json's forbidden list.
  No git repo state was touched (no add/commit/status/restore/stash).
- **J8 — snapshot bug recorded:** `harness/snapshot.py` resolved the 6 PLAN-input anchor paths
  one level too deep, so `snapshot_{before,after}.json` mark them `missing:true`. Those inputs
  (card/scenario_matrix/manifest/I-00-B/I-07-A) are read-only and were hashed correctly by a
  separate capture (`evidence/plan_anchor_hashes.json`); the 20 product anchors and the whole
  production-identity/sample sections of both snapshots are valid and were compared
  byte-for-byte. The captured observations were NOT rewritten.
- **J9 — mid-attempt isolation fixes, each preserving prior evidence:** (a) YAML double-quoted
  path bug (invalid `\U` escape) found by the first judged run → config template switched to
  single quotes → all case trees rebuilt BEFORE any successful run (evidence dir cleared, no
  green lost); (b) authorized-arm failures (`WinError 3` on adapter roots, missing fixture
  `candidate_id`) → scaffolding/fixture fixes with every superseded run directory preserved as
  `run2.pre_scaffold*/run2.pre_fix2*`. No oracle expectation was changed after any run.

## 7. Findings handed downstream

- **F1**: the entry cannot recover registration for a present-unregistered raw (S-*-2 fails by
  product shape; only `cli scan` registers).
- **F2**: no refusal returns structured actionable-recovery requirements (C2.2 fails on every
  refusal; only `error_code/error/retryable` or `error_type/retryable` + a natural-language
  reason). Ties to I-06-A's unsigned recovery interface (OPEN-5).
- **F3**: the prompt-injection review receipt has **no CLI** and no signed method (D-W06 OPEN-4)
  ⇒ the review stage is unreachable for every market ⇒ no `RevenueSourceRecord` can currently
  be produced for any frozen sample ⇒ no source-preparation qualification, no prediction
  qualification.
- **F4**: L row blocked for all three markets (unbound `*-NEW-MISSING` identity + no download
  authority); reachability alone (CN 200/HK 200/US 403-reachable) does not change that.

## 8. Unverified / reviewer to attack (honest list)

- HK-3's canonical file name after the simulated import differs from the manifest file name
  (its registered hash/identity was not independently re-derived by this implementer).
- The `document_fingerprint_state +1` insert observed on S-3 run3 (post-registration re-resolve)
  was recorded but not root-caused.
- Producer wrap is proven by wiring status only (no producer was ever invoked — correct for
  these cases, but an actual producer invocation has no counter proof in this attempt).
- The six corrected plan-anchor hashes (J8) are post-run captures of read-only inputs.
- `read=2` per resolve is asserted as "byte re-verification" from the code map; the two events'
  exact call sites (`_sha256_of_file` vs `_read_verified_bytes`) were not individually
  attributed in the decision table.
