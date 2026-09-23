# E2E-EXPAND 冻结预期（oracle）— a20260923-01

**Written BEFORE the first judged run. This file is never edited after any run.**

Owner constraints (verbatim, card line 1): 「各种可能情形都尽量覆盖，主要步骤都尽量加上，要用真实数据，测试要自建独立环境和数据，测试完数据要恢复（比如为了测试下载，那么测试完后要删除测试文件以保证下次再测试）。请用小规模数据测试，不要大张旗鼓。」

Card deliverables: RF `e2e/run_cross_repo_chain_e2e.py` (standalone runner) + ONE tests file
`tests/test_cross_repo_chain_e2e.py`. All evidence lives under this attempt dir.

## 0. Scope, budgets, honesty rules (frozen)

- Company: **宁德时代 (CATL, ticker 300750, CN/cninfo)** — one company; FF's own CN E2E seed
  (`e2e/expected/expected-biren-e2e-v1-*.json` CN row = stockCode 300750) and FF's own real-download
  test sample (`tests/test_e2e_download.py`, noted deterministic: "CATL yields exactly one").
- Filings: **2 max** — (a) CW's already-downloaded real FY2024 annual (offline chain input),
  (b) one fresh FY2025 annual download in S1 (deleted afterwards).
- Size: touched real filing bytes ≤ 50 MB (measured: 2 070 073 B offline copy + ~2 MB download).
- Scenarios: **7 defined, cap 8** (S1, S2, S3, S4, S5, S6 — table below).
- Runtime: whole suite ≤ ~4 min (S1 subprocess deadline 150 s; everything else offline).
- Production writes = 0 (isolated/temp only). Network = S1 ONLY (one reachability probe + one
  real download), recorded with URL/provider/auth-target (header NAMES only, no credentials).
- No git commands. No mocks for live — a provider failure SKIPS with reason, never fakes a pass.
- Isolation mechanism: S1 uses FF's own `tests/e2e_support/isolated_wiki.IsolatedWiki`
  (`--config <temp>/company_wiki.json` → absolute temp `company_wiki_root`; NO junction needed —
  FF's config mechanism accepts an absolute temp root directly; staging_root stays inside temp).
  S2/S3 use RF's own `tests/e2e_support/isolated_lake.py` builder API (subclassed, see S2).
- Interpreter: attempt-level iso venv python for every judged product run (I-00-B rule 5);
  global Miniconda python not used to run product commands. cwd = attempt work dir for runs.

## 1. Exit-code / skip semantics (runner `e2e/run_cross_repo_chain_e2e.py`)

| runner exit | meaning |
|---|---|
| 0 | every selected scenario PASS or honest SKIP (skip = pass-with-reason, recorded) |
| 1 | ≥1 scenario FAIL (verification broken, restore violated, or offline product refusal deviates from this oracle) |
| 2 | preflight/binding failure: a pinned PRODUCT CODE file drifted vs `binding.json` → **rebind required, do not run on old pins** (I-00-B oracle rule 1); or unusable workspace |

Per-scenario status ∈ {pass, fail, skip}; every skip carries a machine-readable `reason`
(code + detail). `summary.json` in the evidence dir records each scenario's status, reason,
key checks, elapsed seconds.

### Live gate `RF_E2E_LIVE_DOWNLOAD` (frozen semantics)

| env value | runner (standalone) | tests file (CI step9) |
|---|---|---|
| unset (default) | **auto**: probe cninfo reachability → run if reachable; provider/tool failure ⇒ SKIP(reason) | S1 not executed ⇒ honest skip message, **no network in default path** |
| `0` | **force skip** (no probe, no network) | S1 skipped |
| `1` | force attempt (same provider-failure ⇒ SKIP classification) | S1 executed (explicit opt-in) |

Justification note (decision.md J-E1): the card phrased the force-skip as
"`RF_E2E_LIVE_DOWNLOAD=1` to FORCE-skip"; a value of `1` universally reads as *enable* and the
same card requires `=1`-style opt-in for the tests file's live part, so force-skip is bound to `0`
and opt-in to `1`. Both readings are honored by the tri-state; recorded as a deliberate,
documented mapping.

### S1 failure classification (frozen BEFORE run)

| observed | status |
|---|---|
| exit 0 + all verification checks green | **pass** |
| probe unreachable / stockinfo tool files missing / subprocess timeout (150 s) / exit 2 with provider-stage `not_found`·`upstream_error`·AMBIGUOUS | **skip** (reason recorded; reachability record written separately) |
| exit 2 `identity_error`/`config_error`/`request_error` (offline identity/config bugs — identity comes from the copied real security master) | **fail** |
| exit 1 fatal | **fail** |
| a file WAS committed (downloaded) but any verification check fails | **fail** |
| deletion/teardown could not be verified | **fail** (restore violated) |

## 2. Scenario table (frozen expectations)

### S1 — REAL DOWNLOAD → VERIFY → DELETE → VERIFY-GONE (network; owner's explicit restore rule)

- Fresh isolated env: `IsolatedWiki(<work>/s1-wiki)` + `use_production_adapters()` (real
  stockinfo-cninfo tool, absolute `${USER_PROFILE}` paths, staging inside temp). Production wiki
  never written.
- Frozen argv (I-00-B entry form + FF's own `--config` mechanism, request via file):
  `<venv-python> -X utf8 -B <FF>/scripts/fetch_filing.py --config <s1-wiki>/company_wiki.json
  --request-file <evidence>/s1/request.json --timeout-seconds 120 --allow-download`
- Request (schema 1.1 exact): `{"schema_version":"1.1","company_query":"300750","market":"CN",
  "document_kind":"annual_report","fiscal_year":2025,"as_of_date":"2026-09-23"}`.
- **Branch B1 (primary)**: exit 0, stdout JSON `status=capture_ready`, `downloads==1`;
  canonical file exists under `<s1-wiki>/companies/宁德时代/raw/financial_reports/annual/`,
  `size>0 == handle.byte_size == sidecar.byte_size`;
  `sha256(file) == handle.snapshot_sha256 == sidecar.content_sha256`;
  provenance consistent: `sidecar.provider=="cninfo"`, `sidecar.provider_document_id` non-empty,
  `sidecar.source_url` startswith `https://`, `sidecar.filing_date` matches `YYYY-MM-DD` ≤ as_of,
  `sidecar.retrieved_at` present, `handle.https_url` https, `handle.document_id ==
  "urn:company-wiki:document:sha256:"+content_sha256`; acquisition journal contains exactly one
  `downloaded_new`; staging holds **no leftover files**; `operation.lock` absent (FF residue rule).
- **Branch B2 (pre-registered fallback, FC-805 contract)**: if B1 returns structured `status=="gap"`
  with an actionable `gap_plan` → second identical CLI call, request upgraded to schema 1.2 with
  `authorization={"provider":<candidate.provider>,"allowed_accessions":[<candidate.
  provider_document_id>],"max_items":1,"max_bytes":200000000,"expires_at":"2099-01-01T00:00:00Z"}`
  + `--allow-download` → same end-state assertions as B1.
- **Teardown (ALWAYS, even on failure/skip)**: record pre-delete inventory (paths + sha256 + sizes)
  into `deletion_proof.json`; delete downloaded raw + sidecar + every file under `<work>/s1-wiki`;
  rmtree `<work>/s1-wiki` (retry ≤6 like FF's `cleanup_temporary`); assert
  `not Path(s1_wiki).exists()` afterwards → `deletion_proof.json.post_absent==true`,
  `asserted==true`, and every deleted path listed. **The suite itself asserts the deletion.**
  If a download had occurred this is the owner's 「测试完后要删除测试文件」 proof.
- Network record: reachability probe `GET https://www.cninfo.com.cn/` (urllib, 10 s, header names
  only) written to `reachability.json` with url/provider/auth_target/status/elapsed — mirrors
  I-07-B's live record. Probe runs only when the live gate allows (never in `never`, never in
  tests-default).

### S2 — ISOLATED-ENV FULL CHAIN, offline, REAL data already on disk

- Lake: RF `isolated_lake.IsolatedLake` subclass `CatlRealLake(<work>/s2-lake)`:
  - `_add_companies` copies (shutil.copy2, READ-only source) CW's real filing
    `companies/宁德时代/raw/financial_reports/annual/2025-03-14_cninfo_1222806982_2024年年度报告.pdf`
    (**sha256 `b4f1713d7b821eb076c102711d177fe942ccc2bc8dd171ae5d7a95799a65b0ad`**, 2 070 073 B)
    + its sidecar (**sha256 `601349fd9334af58aff992d94795c1081ff5a47e58fa1089e4b6f866af85ba40`**)
    into the lake; build re-hashes the copy and MUST equal these pins (drift ⇒ fail, rebind).
  - `_add_dayu`/`_add_dropbox` create ONLY empty roots — the builder's synthetic
    `_body()` bytes (紫金/平安/dayu fake PDFs) are **suppressed everywhere: zero synthetic filing
    bytes in this suite** (owner: 要用真实数据).
  - `_write_security_master` copies the REAL production `security_master/{cn,hk,us}.json`
    (identity data; contains 宁德时代/300750, active) instead of the builder's synthetic cn.json.
  - Rest of the builder runs as-is: production-shaped yaml configs, runtime policy, real
    `SourceCatalog.scan()` (registration stage), preset v2 artifacts + producer_events (built by
    the builder through CW's writer).
  - **State construction (recorded, not green-filling)**: afterwards the preset
    `documents.metadata_json["prompt_injection_review"]`(+`_audit`) key is REMOVED for the target
    document so the lake mirrors PRODUCTION reality — I-07-B J1 measured production has no review
    receipt and F3: no CLI exists to create one. Key presence before/after is recorded in
    `receipt_removal.json`. (Keeping the builder-written receipt would hand-author a review no
    operator can perform — the plan forbids hand-filled green.)
- **Stage A — FF parse step (FF's real CLI entry, read-only resolve, no download):**
  `<venv-python> -X utf8 -B <FF>/scripts/fetch_filing.py --config <evidence>/s2/company_wiki.json
  --request-file <evidence>/s2/request.json --timeout-seconds 60 --debug`
  Request: schema 1.1 exact, `company_query "300750"`, market CN, annual_report, `fiscal_year 2024`,
  `as_of_date 2026-09-23`. This exercises FF's real contract parse
  (`filing_contracts.validate_request`) → identify (real security master, offline) → resolve →
  deep handle validation.
  **Expected: exit 0, `status=capture_ready`, `calls>0`, `downloads==0`, handle checks**:
  `byte_size==2070073`, `snapshot_sha256==b4f1713d…`, `provider=="cninfo"`,
  `provider_document_id=="1222806982"`, canonical_path under the lake companies root,
  `published_date("2025-03-14") <= as_of`, https_url https.
- **Stage B — RF `scripts/source_preparation.py`, I-00-B-bound argv form** (binding.json
  `old_command_notes` entry pattern + I-07-B's measured isolation flags; no invented argv):
  `<venv-python> -X utf8 -B <RF>/scripts/source_preparation.py --request-file <req>
  --timeout-seconds 120 --company-wiki-config <evidence>/s2/company_wiki.json
  --filing-fetch-root <FF>`, cwd = work dir, `PYTHONPATH = <spy>;<RF>/scripts;<CW>/src`,
  `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1` (I-07-B run_case env, verbatim).
  **Expected (refusal at review gate — I-07-B's measured behavior)**:
  - exit **3**; stdout empty; stderr = ONE JSON line
    `{"error_code":"upstream","error":"prompt injection not reviewed — source preparation blocked
    per policy (prompt_injection_status=not_reviewed)"}` (absent receipt ⇒ resolver's explicit
    `not_reviewed`, resolver.py:1078 "absent receipt -> explicit not_reviewed").
  - Stage assertions: **raw** exists after, sha256 still `b4f1713d…` (unchanged);
    **注册** `documents≥1` BEFORE the run (builder's real scan registered it) and
    `catalog_count_delta=={}` during the run (resolve/ensure never scan — I-07-B code-map Q2/F1);
    **资格** no `RevenueSourceRecord` on stdout (refused before record emission);
    **review gate** refusal message EXPLICITLY names the missing condition
    (`names_missing==true`); **structured actionable recovery fields ABSENT**
    (`candidates/next_action/required/missing/gap_plan/hint` all absent) → **F2 gap OBSERVED,
    not fixed** (asserted as current behavior, per card "measure first, assert what IS").

### S3 — REUSE / SECOND RUN against the same isolated state (offline)

Re-run stage A then stage B with identical argv/env (spy counters baselined after S2):

- stage A rerun: exit 0, `capture_ready`, **`downloads==0`** (zero re-download).
- stage B rerun: exit 3, stderr refusal message **identical** to S2 (recovery story per current
  product: idempotent refusal that keeps naming the missing condition — explicit-missing-info arm;
  structured-recovery arm stays absent = F2 observed).
- Counters (I-07-B `sitecustomize` `_event`-before-original technique, adapted, gated by
  `RF_E2E_SPY_DIR`, wiring written to `wiring.json`):
  **provider delta == 0**, **scan delta == 0**, **producer delta == 0** (and wiring must show the
  producer wraps installed — "wrapped"), read delta recorded (may be >0: byte re-verification is
  allowed and expected), events file exists.
- `catalog_count_delta == {}` across both reruns (zero duplicate registration); artifacts/derived
  file hashes unchanged; raw sha256 unchanged.

### S4 — RESTORE INVARIANTS (always executed last over ALL scenarios)

Baseline captured by the runner BEFORE S1; post captured after every other scenario. All must hold:

1. `<work>/s1-wiki` absent; `<work>/s2-lake` absent (moved/removed; temp gone) — evidence files
   already persisted under the attempt evidence dir before removal.
2. CW real files re-hashed: CATL raw `b4f1713d…`, sidecar `601349fd…`,
   `security_master/cn.json` rehash == baseline (READ-only sources untouched).
3. Production catalog **stat-only, never opened**: `catalog.sqlite3` size+ticks, `-wal`, `-shm`
   all identical to baseline (49 677 344 768 B / 0 B / 32 768 B at baseline).
4. No new files in FF real config/storage roots: pre/post listing diff of `FF/config`,
   `FF/scripts`, `FF/e2e`, `FF/tests` (excluding `__pycache__`) and `CW/.source_catalog` top-level
   names and `CW/companies/宁德时代` recursive listing == {}.
5. RF repo unchanged except the two deliverable files: pre/post listing+hash of `RF/scripts`,
   `RF/e2e`, `RF/tests` (excluding `__pycache__`, `.pytest_cache`, `e2e/.runs` — outputs, covered
   by recovery.md) + RF top-level files; allowed-new set =
   {`e2e/run_cross_repo_chain_e2e.py`, `tests/test_cross_repo_chain_e2e.py`} only.

Any violation ⇒ S4 **fail** ⇒ runner exit 1.

### S5 — BAD FILING ID (same lake; structured refusal + nonzero exit)

FF CLI, request `{"schema_version":"1.1","company_query":"300750","market":"CN",
"document_kind":"annual_report","fiscal_year":1999,"provider_document_id":"does-not-exist-000",
"as_of_date":"2026-09-23"}` (no download flag).
**Expected: exit 2**, stdout = one structured JSON with `status=="not_found"` (or an explicit
non-capture_ready structured error), `error` names the non-reusable/missing condition, no `handle`
field, `downloads==0`. No network.

### S6 — COMPANY NOT FOUND (same lake; honest not_found)

FF CLI, `company_query "不存在的公司-XYZ-999"`, market CN, exact FY2024, no download.
**Expected: exit 2**, structured envelope with `status ∈ {identity_error, not_found}`
(identity resolution precedes filing lookup; expected measured value `identity_error`), honest
error text, no fabricated handle, `downloads==0`. No network.

## 3. CI-safety (frozen choice; justification in decision.md)

- The **tests file** default path is OFFLINE: S1 runs only under `RF_E2E_LIVE_DOWNLOAD=1`
  (honest pytest skip otherwise, with the reason string) — CI step9 (`pytest tests tools/tests`)
  therefore performs **no network** by default and never mocks a live call.
- The **runner** default (env unset) is *auto-run-if-reachable with skip-on-fail*: skip counts as
  pass-with-reason (exit 0), never as failure, never as a fabricated pass.
- 不大张旗鼓: no new CI job, no CI workflow edit, no gate change, no baseline additions — the
  runner is a standalone sibling of the existing e2e runners and is not wired into CI by this card.

## 4. Known-observed product gaps to ASSERT, not fix (measure-only)

- **F2** (I-07-B): no refusal returns structured actionable-recovery requirements — asserted as
  ABSENT fields in S2b/S3b (observed-not-fixed).
- **F3** (I-07-B): prompt-injection review receipt has no CLI — the state construction above
  exists precisely because production cannot have a receipt; asserted indirectly (review gate
  refusal is unreachable-to-green for any honestly built state).
- **F1** (I-07-B): the entry cannot recover registration (resolve/ensure never scan) — asserted as
  `catalog_count_delta=={}` + docs≥1 from the builder's own scan in S2/S3.
