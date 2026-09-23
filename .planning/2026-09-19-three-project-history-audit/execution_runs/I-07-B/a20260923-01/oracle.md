# I-07-B oracle.md — FROZEN BEFORE ANY JUDGED RUN

Card: `PLAN/execution_v2/card_I-07-B.md` — 三市场来源链与二次复用 (14 lines; its 5 numbered
clauses + the 退出/恢复 clause are the acceptance face). Attempt: `a20260923-01`.
Frozen: 2026-09-23 (local), after isolation state construction (harness probes only) and
**before the first run of the judged entry** (`RF/scripts/source_preparation.py`) or any
`company_wiki.source_catalog.cli` resolve/ensure invocation by this attempt.

> No expected value below was produced by running the tooling under test. Case identities
> come from `execution_v2/scenario_matrix.md` (sha256 `0dec23cd10f00efd6ad82cf923552bd4
> 6c1763bcf9f740422f51f4973292299f`, verified) and `sample_manifest.json`
> (sha256 `d5d0bb92da9eee92666459ccf344d549343008db8bf32fd1257dbf6f5f3ec851`).
> Operational facts about production state come from READ-ONLY production observations
> (I-07-A frozen matrix + this attempt's `mode=ro` SELECTs), not from tool output of the
> runs this oracle governs.

## 0. The three exit-honesty declarations (verbatim from the card; binding)

1. `三公司仅来源准备通过，仍未授予正式预测资格。`
2. `缺一市场/真实路径不得总体写三市场通过。`
3. `恢复：保留已取得raw，只回退当前隔离变更。`

Any handoff/decision text must carry all three verbatim. An overall "三市场通过" is
**forbidden** unless every market's real path passed; this oracle pre-registers that a
blocked live cell or a missing market ⇒ the overall three-market statement MUST be
negative (asserted again in `decision.md`).

## 1. Ground rules (frozen)

- **R1 Entry, not helper.** Every judged run uses the frozen I-00-B argv form of the REAL
  entry: `<iso-python> -X utf8 -B <RF>/scripts/source_preparation.py --request-file <req>
  [--allow-download] --timeout-seconds <T> [--company-wiki-config <iso json>]
  [--filing-fetch-root <RF>]`. No helper script may be substituted for the entry
  (card: `不调用helper冒充`). cwd = the attempt dir (never a repo root).
- **R2 Isolation.** All writes go to the attempt dir and `%TEMP%\i07b\cases\<case>`
  (MAX_PATH: the attempt path + the US file names exceed 260 chars and the PRODUCT opens
  those paths with plain APIs). Production bytes are read-only; production writes = 0;
  CW writes = 0; no git; network only where a case clause requires a live call.
- **R3 Product-isomorphic catalog.** Each case catalog is created by the product's own
  `CatalogStore._initialize` (18 tables = production's 18). I-07-A's prohibition stands:
  `iso/catalog/catalog.sqlite3` (5 tables) must not and is not used.
- **R4 Counters are call spies, not INSERT arithmetic.** Every reported
  provider/scan/read/producer count comes from a wrapper installed on the real entry
  function in the run process (see §5). Deriving a count from `artifacts`/`producer_events`
  INSERTs is a failed check, and a wiring probe (§5 W-probe) must demonstrate the counter
  increments from a real invocation.
- **R5 Simulation labels.** A state built by this attempt is `simulated_in_isolation`;
  a state copied from a production observation is `production_observation_copy`. Live
  qualification is never signed by a mock (card clause 5).
- **R6 No hand-filled green.** No review receipt, artifact row, or review state may be
  authored by the harness. Case state either exists in the production observation or is
  produced by the product itself during a run.

## 2. Frozen sample identities (manifest; re-derived in `snapshot_before.json`)

| sample | market | FY | query | provider doc id | frozen raw sha256 (measured match) | frozen sidecar sha256 |
|---|---|---|---|---|---|---|
| CN-ZIJIN-2025 | CN | 2025 | 601899 | 1225023658 (filename only) | `01819e1c7daad939d1779a8aa729f50f02151192e609cb28c2c405634a8f343d` (79 925 886 B) | `7f7570fe…20b5` |
| HK-XIAOMI-2025 | HK | 2025 | 1810 | 12127452 | `ffd733761633f464d90f6829e9b2d3e089f2dee7054b8ebfe91ef617f222da7c` (4 405 561 B) | `8228741d…8da71` |
| US-MSFT-2026 | US | 2026 | MSFT | 0001193125-26-323660 | `e3de0053021c02b033272b55551e383b31dba288c86cc12da2e32375e40ecfff` (8 585 615 B) | `1cbfb1a2…abb6a` |

Requests: `{"document_kind":"annual_report","market":<M>,"as_of_date":"2026-09-18",
"fiscal_year":<FY>,"company_query":<Q>,"schema_version":"1.1"}` — as_of stays `2026-09-18`
(frozen per I-07-A R6; capture times are never back-filled).

## 3. Case table (frozen) — scenario_matrix §三市场×三种原件状态 + 重复请求 + 注册失败恢复

Cell IDs follow `scenario_matrix.md` (`S-CN-1…S-US-3`), plus `REP-<case>` (the second run of
each cell = the 重复请求 clause) and `REGFAIL-<M>` (注册失败恢复). `L-<M>` are the matrix's
live rows.

| case | matrix input state (frozen) | initial state actually built (evidence: `evidence/cases/<id>/initial_state.json`) | operation (frozen argv, run twice unless noted) |
|---|---|---|---|
| S-CN-1 | R: raw indexed + real review + applicable artifacts qualified, no hand-filled green | **production_observation_copy**: 1 documents/1 source/2 locations/2 artifacts copied read-only from production; `prompt_injection_review` ABSENT in metadata (production fact) ⇒ the "真实审核已合格" precondition is **NOT satisfied**; dropbox location dropped (root not in isolated config, recorded) | entry ×2, no `--allow-download` |
| S-HK-1 | same, HK | **precondition NOT satisfied**: production observation has 0 registration rows for HK; raw+sidecar present | entry ×2, no `--allow-download` |
| S-US-1 | same, US | **precondition NOT satisfied**: 0 registration rows for US; raw+sidecar present | entry ×2, no `--allow-download` |
| S-CN-2 | R: raw+sidecar present, isolated index unregistered | **simulated_in_isolation** over real bytes: identity registry copied (271 entities + catalog_meta), 0 documents/locations/artifacts rows; raw+sidecar copies hash-identical to manifest | entry ×2, no `--allow-download` |
| S-HK-2 | same, HK | same construction (0 registration rows) | entry ×2 |
| S-US-2 | same, US | same construction | entry ×2 |
| S-CN-3 | C: isolated catalog+dir lack the file; provider = frozen simulated return | raw+sidecar ABSENT (`raw_absent_exists=false`), 0 registration rows | (a) unauthorized: entry WITHOUT `--allow-download` ×1; (b) authorized: entry WITH `--allow-download` ×1 (provider served the harness's FROZEN simulated response — C level only); (c) repeat authorized entry ×1 |
| S-HK-3 | same, HK | raw absent | same (a)/(b)/(c) |
| S-US-3 | same, US | raw absent | same (a)/(b)/(c) |
| REP-* | 重复请求 | — | the second run of each cell IS the repeated-request run; its counters are asserted separately |
| REGFAIL-HK / REGFAIL-US | 注册失败恢复 (旧失败样本 = the two "scan/registration failed" samples) | state2 construction + an isolation-only fault: a second connection holds a BEGIN IMMEDIATE write transaction on the ISOLATED catalog during run 1 (scenario F03 pattern; scratch only) | run 1 with the lock held; clear the lock; run 2 |
| L-CN / L-HK / L-US | L: real genuinely-missing new file + explicit download target | **unbound** — `sample_manifest.unbound_live_samples` (CN/HK/US-NEW-MISSING) has no frozen identity and no download authority for this card; will not be re-download of manifest files | no chain run; only the live reachability probe (§6) |

### 3.1 Per-clause expectations (the card's five clauses = the acceptance face)

Clause C1 (freeze per-case initial asset/catalog/worker state and provider/scan/read/producer
event counts; real invocation counts must not be derived from artifact INSERT):
- C1.1 every case has `evidence/cases/<id>/initial_state.json` (asset hashes, catalog table
  counts + row counts, worker-control absence) taken BEFORE run 1.
- C1.2 a counter baseline snapshot exists before each run and a delta after
  (`counters/before_run<N>.json`, `counters/after_run<N>.json`).
- C1.3 wiring proof (§5 W-probe): each counter class increments on a real invocation of the
  wrapped entry point with NO database INSERT involved; a counter whose only evidence is an
  artifact row fails C1.
- C1.4 counters are per case and per run; no cross-case reuse of a baseline.

Clause C2 (one run per frozen argv; verify raw→注册→资格→review→适用工件→实际消费 with
per-stage evidence; a correct refusal must ALSO return actionable recovery requirements):
- C2.1 stages, and the evidence that counts as passing each:
  `raw` = the entry's own local-file verification of bytes present (record/`capture` hash
  evidence) + our independent re-hash; `注册` = a registration row set for the sample's
  document_id in the ISOLATED catalog (documents/sources/locations counts >0) caused by the
  run (delta from baseline); `资格` = admissibility/resolve verdict reaching a reusable
  match (`resolution.status ∈ {reused_exact, reused_equivalent}`); `review` =
  `prompt_injection_status` present in the envelope and ≠ `not_reviewed`; `适用工件` =
  `artifact_read` non-empty with `artifact_read_events` proving IO; `实际消费` = a
  RevenueSourceRecord emitted on stdout (entry rc 0) with its `reuse_receipt` populated.
- C2.2 a refusal (any run with entry rc≠0) is only "correct" if the structured error
  document carries **actionable recovery requirements**: machine-parseable fields naming
  what is missing and what to do (e.g. `error_code` + `retryable`/`candidates`/
  `next_action`/`required`/gap-plan steps). Parser: `harness/parse_refusal.py` extracts
  these from stderr/stdout JSON and asserts presence + shape (non-empty strings/list of
  non-empty strings). Absence ⇒ C2 FAIL for that case (recorded, not hidden).
- C2.3 every refusal is recorded with its raw rc AND its business verdict separately
  (frozen rc legend in `commands.json.exit_code_legend` covers harness commands; product
  rcs 0/2/3 are recorded raw).

Clause C3 (second run of the same input): expectations measured as deltas run1→run2:
- C3.1 `provider` counter delta run2 == 0 for every state1/state2 case (valid raw must not
  be downloaded twice; both runs' provider count == 0 without `--allow-download`).
- C3.2 after a first-run registration recovery, run 2 must NOT create a second registration
  of the same valid version: isolated catalog `documents`/`locations` row counts for the
  sample's document_id are unchanged from run1's post-state.
- C3.3 `producer` counter delta run2 == 0 (valid artifacts are not re-produced); also
  producer delta run1 == 0 for cases whose artifacts are valid (the chain plans producers,
  it must not run them).
- C3.4 read-only query counters MAY be non-zero (card explicitly allows; `scan`/`read`
  deltas on a pure re-query are not failures by themselves, but `scan` that re-INSERTs
  registration rows violates C3.2).
- C3.5 asset bytes unchanged after both runs (raw/sidecar/artifact sha256 == baseline).

Clause C4 (deep verification beyond json fields; old failure samples return to same-entry
success or explicit missing info):
- C4.1 when a record/handle is produced: harness re-reads `canonical_path` from disk,
  re-hashes the bytes, and asserts equality with `snapshot_sha256`; asserts
  `published_date ≤ accessed_date ≤ as_of_date` with the FROZEN manifest values
  (CN 2026-03-20 / HK 2026-04-28 / US 2026-07-29 as published_date candidates from the
  production rows; as_of 2026-09-18); asserts `document_id` urn == the frozen sha256 urn;
  asserts `provider`/`provider_document_id` match §2; recomputes
  `capture.receipt_sha256` from its own canonical serialization? — NO: the product's
  canonicalization is `_canonical_sha256` (sort_keys, separators) in
  `company_wiki_source.py`; the harness recomputes it independently with its OWN
  implementation of that documented rule and compares.
- C4.2 when NO record is produced (refusal): the refusal must state explicitly which
  information is still missing (C2.2 parser) — that is the "得到明确尚缺信息" arm; a
  silent/generic failure fails C4.
- C4.3 REGFAIL run1 (lock held): the raw bytes must survive (re-hash == manifest), no
  half-usable handle may be returned, and the error must be the product's own structured
  failure. After the lock is released, run 2 must return to same-user-entry success OR the
  explicit-missing-info arm, with `provider` delta == 0 (no new download) — the recovery
  rule of scenario F03 `释放锁后幂等恢复，不重下raw`.

Clause C5 (live provider):
- C5.1 any live network call is recorded separately with its auth target (host, URL, header
  names present — never header values/secrets) in `evidence/live/`.
- C5.2 an unreachable provider is recorded as `unreachable` — never re-signed by the mock.
- C5.3 L-CN/L-HK/L-US stay `blocked (unbound identity + no download authority)`; because a
  missing market/real path forbids an overall pass (§0 declaration 2), the overall
  three-market statement is negative regardless of S-cell results.

### 3.2 Expected business results (hand-reasoned BEFORE running; a wrong prediction is a
finding about my model, never a rewrite of this oracle)

| case | predicted first-run outcome | predicted run-2 deltas |
|---|---|---|
| S-CN-1 | refusal at `review` gate (no `prompt_injection_review` receipt in the copied production metadata ⇒ envelope `not_reviewed` ⇒ entry rc 3, `error_code=upstream`); downloads 0/0 | provider 0; producer 0; registration rows unchanged |
| S-HK-1 / S-US-1 | refusal at `资格` (nothing registered ⇒ resolve not reusable ⇒ filing-fetch not_found ⇒ entry rc 3) | same |
| S-*-2 | either (a) run 1 recovers registration then refuses at review gate, or (b) run 1 refuses at 資格 with explicit missing-info — depends on whether `resolve` scans present files (map §Q2); whichever happens, downloads 0 both runs | provider 0; no second registration; producer 0 |
| S-*-3 (a) unauthorized | refusal naming the missing authorization; provider counter 0; nothing written | n/a (single run) |
| S-*-3 (b) authorized + frozen sim | either a committed simulated download (provider/spy counter 1) + registration, or an honest failure of the acquisition path recorded as-is — C qualification only | (c) repeat: provider delta 0 |
| REGFAIL-<M> | structured lock/registration failure, raw preserved, no handle; after release: success-or-explicit-missing-info, provider delta 0 | as stated |
| L-* | no run; probe only | n/a |

These predictions are frozen here; measured values go to `decision.md` unchanged in meaning.

## 4. Frozen command expectations (indices used in `commands.json`)

| id | what | expected harness rc | expected business result |
|---|---|---|---|
| CMD-I07B-SNAP-BEFORE | anchors + production identity + sample rehash | 0 | `raw_all_match=true`, `sidecar_all_match=true` |
| CMD-I07B-ISO-BASE / ISO-CASE | isolation construction | 0 | iso catalog `table_count==18`; case states as §3 |
| CMD-I07B-DRIFT | anchor drift old-vs-current diffs (difflib) | 0 | drift table written (recorded, not hidden) |
| CMD-I07B-WPROBE | counter wiring self-test (§5) | 0 | each counter +1 on a real wrapped invocation with 0 INSERTs |
| CMD-I07B-RUN-&lt;case&gt;-&lt;runN&gt; | the frozen entry argv for one case run | product rc recorded raw (0/2/3) | per §3.1/§3.2; harness driver exits 0 when evidence was captured regardless of product verdict |
| CMD-I07B-LIVE-PROBE | HTTPS reachability of the three provider hosts | 0 | per-host `reachable/unreachable` + auth-target record; no body downloads |
| CMD-I07B-VERIFY-&lt;case&gt; | deep verification (C4) against frozen values | 0 | per-case `verification.json` with pass/fail per C4 item |
| CMD-I07B-SNAP-AFTER | same as before, re-taken | 0 | production identity + sample hashes byte-identical to BEFORE |
| CMD-I07B-ISO-FINAL | iso tree snapshot | 0 | after-state recorded for recovery |

## 5. Counter wiring spec (frozen)

Mechanism: a `sitecustomize.py` spy directory placed FIRST on `PYTHONPATH` for every judged
run, so every process spawned by the chain (source_preparation → filing_fetch_client →
fetch_filing → `company_wiki.source_catalog.cli`) installs the same wrappers. The spy:
- is enabled only when `I07B_SPY_DIR` is set (no effect on any other process);
- appends one JSON line per event to `$I07B_SPY_DIR/events.jsonl` with
  `{counter, module, qualname, pid, t, args_digest, outcome}` — never secrets;
- counts CALLS to the real entry points (count-on-entry, before delegation), so a counter
  is never derived from an artifact/producer_events INSERT.

Counter classes and the wrapped entry points (exact `module.function` targets frozen with
the code map in `binding.json:counter_wiring`):

| counter | meaning | wrapped entry (frozen in binding.json) |
|---|---|---|
| `provider` | a real provider/network acquisition attempt (live or simulated) | the CW acquisition HTTP/download entry + `requests.sessions.Session.request` fallback (records URL host as auth target) |
| `scan` | a scan/registration pass over a root | the CW scanner entry function |
| `read` | an actual byte-read of a raw/source/artifact file | `builtins.open`/`Path.open` filtered to the isolated root's `companies/**` and `.source_catalog/derived/**` |
| `producer` | an actual producer invocation (normalize/summarize/sections/consumer-analysis run) | the CW producer entry functions (normalizer/summarizer/section-extractor run functions) |

W-probe (CMD-I07B-WPROBE): in a throwaway process with the spy active, invoke each wrapped
entry with inert/benign arguments (or trigger the underlying code path with a synthetic
argument that is expected to raise) and assert: counter +1, `events.jsonl` gained the line,
and no INSERT occurred (isolated throwaway catalog row counts unchanged). A counter that
cannot be probed this way is reported as `unwired`, not as 0.

## 6. Live reachability (frozen expectation shape)

Probe `https://www.cninfo.com.cn/`, `https://www.hkexnews.hk/`, `https://www.sec.gov/`
with a 10 s timeout, GET, no bodies saved beyond status/latency; record
`{host, url, auth_target_headers_present, status|error, reachable}` in
`evidence/live/reachability.json`. Any unreachable host ⇒ that market's L cell is
`unreachable` ⇒ it must not be counted as passed, and §0 declaration 2 forces the overall
three-market statement negative. No live call may be simulated, and the C-level frozen
provider simulation must be labelled `simulated` everywhere it appears.

## 7. Reviewer attack list (frozen before results)

1. Re-derive at least one case's raw sha256 and the initial_state table counts yourself.
2. Confirm the counters are call-wiring (read `sitecustomize.py`, run the W-probe record)
   and that no counter value equals an INSERT-derived count by construction.
3. Attack C3.2: read the isolated catalog row counts for the sample across run1/run2 — a
   second registration of the same version must show up.
4. Attack C4.1: pick one produced record and re-hash `canonical_path` yourself.
5. Attack the refusals: parse the error documents and say whether the "recovery
   requirements" are genuinely actionable or decorative.
6. Attack §0: find any sentence that claims a three-market pass despite a blocked market.
7. Attack simulation labels: any `simulated_in_isolation` event described as live is a fail.
