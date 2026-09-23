# E2E-EXPAND / a20260923-01 — review.md (carrier landing, bookkeeping transcription)

**This file is a bookkeeping transcription. It adds no acceptance of its own.**
It transcribes the verdict and findings of the independent reviewer's signed report; it does
not review, does not re-rule, and does not sign. **No self-signing**: the implementer did not
self-accept (`handoff.json` pre-image `status=review_pending`, `reviewer_status=unsigned`,
measured below), this carrier does not sign a verdict, and N=1 signer of the verdict remains
the independent reviewer subagent (parent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`),
signature block of `reviewer_report.md` lines 506–509.
`verdict_is_transcribed_not_authored: true`.

## 0. Verdict block (transcribed)

**ACCEPTED — SCOPED** (verbatim: `reviewer_report.md` §0 line 20: "**ACCEPTED — SCOPED.**").

| pin | value |
|---|---|
| source authority (the report carrying the verdict) | `reviewer_report.md`, this attempt dir |
| byte proof | **42 915 B** (live re-measured at landing = declared size) |
| sha256 (live re-hash at landing) | `de849e1adfb21ea39f610eaad0e08d5df249095d29bcb7197f164bdeb6fdd423` |
| sidecar `reviewer_report.sha256` | content-match: `de849e1a…  reviewer_report.md` == live re-hash ✓ (87 B, untouched) |
| verdict line range | §0 "Verdict" = lines 18–47 (verdict sentence line 20) |
| central ruling line range | lines 41–47 |
| findings table line range | §10 = lines 431–447 (F-RV-01 line 435 … F-RV-11 line 445; boundary note 447–448) |
| unverified line range | §11 = lines 450–467 |
| routing line range | §12 = lines 469–485 |
| carrier of this transcription | this file `review.md`; its sha256 is recorded in `handoff.json.status_authority` and `evidence/E2E-EXPAND/qualification.json` (a file cannot embed its own hash) |

**独立复核 (carrier's own independent re-checks at landing, read-only):**
re-hashed `reviewer_report.md` → 42 915 B + `de849e1a…` matches declared size/hash and the
sidecar byte-for-byte; read `handoff.json` pre-image → `status=review_pending` +
`reviewer_status="unsigned — no review.md written by this implementer…"` (5 663 B,
sha `255d37d5115bfe8670fc1f6663ebc1d5a00a933812f3186b1a98d825e606116d`); re-read
`fetch_filing.py:663-666` live → the READ-10 sentence is verbatim there; re-read
`resolver.py:1021-1029` live → the `download_events = 0` init and the
`request_id`-mismatch `continue` exist exactly as transcribed; re-measured `oracle.md` live
= 16 348 B, sha `dfc3a6fff9e7feb1236bd1c8ce2bfa82c24c0f15f30a64770ba7ffe04ffb08e4`,
mtime 2026-09-23T08:37:13Z; re-counted `evidence/` = **149 files / 1 763 067 B**.

**Central ruling — KEEP THE RED (transcribed from lines 41–47):** the frozen S1
`downloads==1` check is correctly specified against FF's own documented contract
(`FF/scripts/fetch_filing.py:663-666`, READ-09/READ-10: "`stats["downloads"]` is the
download event count from the final resolution envelope (0 unless a download actually
committed)…"), and a committed download DID occur (journal `downloaded_new`=1, file+sidecar
verified, then deleted). The product reports 0 — that is the defect (F-EE1), not the oracle.
The oracle was not amended after the run either way (oracle.md mtime 2026-09-23T08:37:13Z <
first judged run 09:31:41Z, unchanged since). Handoff `next_action`'s central review question
is hereby answered: **keep the red.**

## 1. Basis of acceptance — key verifications transcribed (§0, §1–§4)

- **Deliverables live re-hashed (3/3 + pre-image):** runner
  `88ac9e4a4d207c02bd8163a0f3bbec743e4d28e8a32443504398637935466648` / 66 643 B · tests
  `3e2b39ee10947c386f21833dbf19b135619d015817c3df91757d04ef7bcc9213` / 7 037 B · allowlist
  `ff9db8c8cdb11f71230de3c576b7b41e65ebf69594e5ddd52d2f712d2727c219` / 4 913 B (+11) ·
  allowlist pre-image `bc6da8ff…` reconstructed live from `evidence/gen_changes_diff.py`'s
  embedded `ORIGINAL_ALLOWLIST` ✓ (re-hashed at review start and end, identical).
- **3-file diff, +0 workflow hits:** `changes.diff` = exactly 3 file sections
  (2 × `/dev/null → b/…` + allowlist `@@ -12,6 +12,50 @@` = +44 lines = 11 × 4, 3 pre-existing
  entries preserved); forbidden-pattern grep over the whole diff = **0 hits** each for
  `workflow`, `.github`, `quality.yml`, `host_assumption_guard`, `ratchet`, `pyproject`,
  `conftest`, `pre-commit`, `make_gate` (the words `baseline`/`gate`/`CI` occur only on `+`
  lines inside the two new files' scenario code).
- **14/14 product/data pins + 3/3 I-00-B contract pins** re-computed live and matched
  (`fdb2a598…/f8a397ec…/e9c82fe4…`; I-07-B sitecustomize citation `58da8b36…` matched).

### Owner constraint 1 — REAL data (要用真实数据): PROVEN

Live re-hash of the CW real files: raw
`companies/宁德时代/raw/financial_reports/annual/2025-03-14_cninfo_1222806982_2024年年度报告.pdf`
= `b4f1713d7b821eb076c102711d177fe942ccc2bc8dd171ae5d7a95799a65b0ad` / 2 070 073 B and
sidecar `.source.json` = `601349fd9334af58aff992d94795c1081ff5a47e58fa1089e4b6f866af85ba40`
/ 3 108 B — both equal the binding pins, before AND after the review. S1's authorized
download pre-delete sha `c15272977147dee7e6935a38ea0e4fd6855370aabb106f54cfe20f7cf6048ec9`
/ 2 043 710 B (+ sidecar 3 214 B), now deleted. **Both deletion proofs read and
structure-verified: `pre_delete_inventory`=15 / `deleted_paths`=2 / `post_absent=true` /
`asserted=true`, ×2** — `evidence/run_live_pytest/s1/deletion_proof.json` (gate=force;
sidecar `5a02bb271cf6a09de23c6baba53c118ea53c4d332f7c9fc10f4b19779a2bfff2`) and
`evidence/accidental_auto_gate_run/s1/deletion_proof.json` (gate=auto; sidecar
`e319f62f…`). Default/CI runs also write the proof with `post_absent=true` with nothing
created (runner 662-667).

### Owner constraint 2 — Isolated env + restore: PROVEN

- **Drift→exit-2 gate proved empirically**: runner copied to `%TEMP%\rev_drift` with pins
  unresolvable → **rc=2**, stderr `E2E-EXIT2: binding drift / unusable workspace (rebind
  required)` listing the 8 code pins + `sibling repos absent`; only `preflight.json` written.
- **14/14 pins** live re-hash (above) + **I-00-B 3/3** + sitecustomize citation match.
- **Reviewer's own snapshot recomputation: content-keys 7/7 equal** (literal diff =
  `["captured"]`, the capture timestamp → F-RV-07 nuance), `temp_state` 3/3 true in every S4
  execution including the reviewer's, implementer work root absent at review time.
- **Production catalog stat-only, ×2 (before AND after the reviewer's runs), N=0 opens**:
  49 677 344 768 B / wal 0 B / shm 32 768 B, mtime ticks identical to
  `binding.json.production_catalog_baseline_stat_only`; no SQL connection ever opened by the
  reviewer.

### Owner constraint 3 — Small scale (小规模): PROVEN

1 company (宁德时代/300750, CN/cninfo) × 2 filings; 7 scenarios (cap 8). Runtimes re-derived
from raw ISO stamps: offline runner **36.234 s** (S2 14.181 / S3 13.169 / S5 4.127 / S6 3.421
/ S4 1.336 = decision's 36.2 s ✓); authorized S1 **23.988 s** (= decision's 24.0 s ✓).
Nuances carried: **F-RV-09** — "82.7 s" not raw-derivable (closest raw = nested runner
73.322 s; reviewer re-run 44.40 s, same outcome); **F-RV-10** — "≈8.2 MB" double-counts the 2
filings (unique 4.1 MB; 6.2 MB incl. accidental), conservative vs the 50 MB budget.

### Owner constraint 4 — 不大张旗鼓: PROVEN

`changes.diff` = the 3 card files and nothing else; zero workflow/gate/baseline hits (§1).
`.github/workflows/quality.yml` **untouched** (mtime 2026-09-20T14:17:13Z, 3 days pre-attempt;
its e2e step still `python e2e/run_revenue_forecast_e2e.py` line 88; tests file collected by
the pre-existing `pytest tests tools/tests` step line 36) and **no workflow reference**:
grep `.github/` for `run_cross_repo_chain|cross_repo` = **0 hits**. Allowlist **+11 = the
guard's own sanctioned remediation** (`tools/host_assumption_guard.py:316-318`): file has
exactly 14 hashes = 3 pre-existing + 11 new; **11/11 literals exist verbatim in the runner at
the claimed lines** (L68 `91a6dc32…`, L70 `b281e6d1…`, L72 `7d1bd8f9…`, L74 `867ac82b…`,
L76 `046cc7dc…`, L78 `2d1b2e33…`, L80 `8966e7e1…`, L82 `fad88c60…`, L92 `b4f1713d…`,
L94 `601349fd…`, L96 `d9a4860f…`); **string-splitting evasion = 0 hits** (no concat/slice/
`chr()`/hexdigest-slicing patterns; plain literals at runner lines 66-96).

## 2. The reviewer's own re-runs (transcribed §3–§4)

- **pytest wrapper**: `2 passed, 1 skipped in 44.40s`, **rc=0**; skip = the opt-in live
  test; 0 `reachability.json` in the reviewer's trees; both nested summaries
  `live_gate=never`, `network_scope="none (live gate never)"`, `exit_code=0`.
- **standalone runner**: **exit 0**, total 40.173 s — S1 **SKIP `live_gate_never`** (proof
  written), S2 PASS 15.259 s (28/28), S3 PASS 14.402 s (18/18 incl. zero provider/scan/
  producer/catalog-delta), S5 PASS 4.678 s, S6 PASS 4.194 s, **S4 PASS 1.638 s with 16/16
  `s4.*` checks true**; `production_writes=0`; default work root removed by S4 (+11% wall
  time vs decision, same shape/pass-set = host-load variance).
- **gates re-run on final code, all rc=0**: ruff 0.15.18 `All checks passed!`; compileall
  (pycache redirected to `%TEMP%`); host-assumption guard rc=0
  `violations=35; new=0; baseline=16; registered_hashes=14`; `test_fc1307a` = **3 passed +
  1 failed, the 1 failure pre-existing** (vendored-copy byte drift, §5 J-C1).

## 3. Tri-state gate behavior + J-E1 + F-RV-08 (transcribed §4)

`live_gate()` precedence (runner 518-528): `--live never` → `never` (outranks env) · env `0`
→ `never` (no probe) · env `1` → `force` · `--live force` → `force` · else → `auto`
(probe; unreachable/tool-missing/provider ⇒ SKIP with reason; offline identity/config/request
⇒ FAIL per oracle J6). Tests file: `skipif(env != "1")` (lines 129-133) ⇒ S1 runs only on
exact `1`; the two offline tests always pass `--live never` (lines 90, 118), which outranks
even `env=1`. **decision J-E1's rationale matches the implementation and oracle §1's frozen
table.** **F-RV-08 nuance**: under `gate=force` an unreachable probe does NOT itself skip
(runner line 686 `gate != "force"`), so oracle J6's "unreachable ⇒ skip" arm is deferred to
the subsequent fetch classification — never fired (both authorized probes = 200).

## 4. F-EE1 chain with citations (transcribed §5) — replicated ×2

1. Journal row: `journal_rows.json` → `outcome=downloaded_new`,
   `request_id=…sha256:e8177b377da8fc80f8e72695535cf97a5282d9261549634523705bbdd8d53ecb`.
2. Envelope/handle: `envelope.json` → `outcome=reused_existing`, `download_events=0`,
   `response_downloads_field=0`, `response_calls_field=3`,
   `handle_request_id=…sha256:47c3a925dc2ac33af0b343f187aba417961013837bf4304697234834c5e7e993`
   → **request_id mismatch** (`e8177b37…` ≠ `47c3a925…`).
3. Skip is live code: `CW/src/company_wiki/source_catalog/resolver.py:1021-1029` —
   `download_events = 0`; `for attempt in journal.read_all(): if attempt.request_id !=
   resolution.request_id: continue; … download_events = 1 if attempt.outcome in
   _ENVELOPE_DOWNLOAD_OUTCOMES else 0` → the row is skipped ⇒ structural
   `reused_existing` + `download_events=0` (carrier re-read these lines live at landing).
4. Propagation + contract: `FF/scripts/fetch_filing.py:622-629 _record_download_events()`
   mirrors `download_events` into `stats["downloads"]` ⇒ response `downloads: 0`;
   violates FF's documented contract **`fetch_filing.py:663-666` (READ-09/READ-10)** and the
   **FC-704** no-fabricated-download-evidence contract (`FF/tests/test_fetch_filing.py:315-317`;
   `RF/tests/test_source_preparation.py:159-197`, ENV-11) ⇒ `source_preparation`'s
   `reuse_receipt.download_calls` would claim 0 after a real download (the exact fake-zero
   class FC-704 exists to prevent).
5. Replication **×2**: R3 direct file pair; accidental run via `s1_fetch1_stdout.txt` +
   `journal_outcomes.json` (the named `journal_rows.json`/`envelope.json` pair is absent there
   — F-RV-06 pointer correction applied to decision.md during this landing).
   Oracle kept frozen / FAIL recorded (`status=fail, "s1.downloads: expected 1, got 0",
   exit_code=1` in `evidence/run_live_pytest/summary.json`, carried into decision §0/§6).

## 5. F1 / F2 / F3 re-observations (transcribed §6)

- **F2 observed, not fixed**: `stageB_refusal.json` — `explicit_missing_info.names_missing=true`
  (message names `prompt_injection_status=not_reviewed`) and
  `structured_actionable_present=false`, `actionable_recovery_fields={}` (candidates/
  next_action/required/missing/gap_plan/hint absent); checks true in every S2/S3 incl. reviewer's.
- **F1 entry-never-scan**: `catalog_count_delta={}` across S2/S3, `documents_pre_run_ge1`;
  judged-run spy stream = **6 events, 6/6 `counter="read"`**, zero `scan`/`provider`/
  `producer` events while `wiring.json` shows all wraps `status="wrapped"`.
- **F3 no review CLI**: grep FF `fetch_filing.py` subcommand construction + RF `scripts/` for
  a review/prompt-injection recorder = 0 hits; CW `cli.py` enumerates 47 subparsers, no
  `review`; hence J2's construction — `receipt_removal.json`
  (`receipt_present_before=true → receipt_absent_after=true`).

## 6. Disclosed deviations verified (transcribed §7)

- **J-D2 timeline**: R2 first execution 09:35:33Z `live_gate=auto` → probe 09:35:34Z status
  200 (`reachability.json`, `gate=auto` in the proof) → real download (retrieved_at 09:36:12Z,
  journal `downloaded_new`) → S1 FAIL on the frozen check (first F-EE1 exposure) → teardown
  proof 15/2/`post_absent=true` → accidental evidence dir = exactly 16 files (counted) → fix
  `--live never` added to the opt-in test → R2b + final run offline → **R3 authorized
  09:41:18Z `gate=force`, probe 09:41:20Z 200**. **Effective network ledger = 2 probes +
  2 downloads** (2× `reachability.json`, 2× `journal_outcomes=["downloaded_new"]`, 2×
  deletion proofs, both PDFs `c1527297…`/2 043 710 B) — each download verified then deleted
  with proof ✓. Structured-field defect F-RV-05 (RUN-R2 `network:"disabled"`) **fixed during
  this landing** (§8).
- **J4 pip-prose-only**: `commands.json` grep `git`=0; `pip`=2, BOTH prose inside ENV-02
  ("NO pip/network", "pip/PyPI would violate the network budget") — no pip command anywhere;
  ENV-01 = robocopy of the I-07-B venv, ENV-02 = file copies from Miniconda; live check
  `iso/venv/.../playwright` + `selenium` present; no product file touched.
- **J3**: `evidence/run_offline.pre_harness_fix1/` present (37 files), `summary.json` exit 1
  with exactly the two harness-defect signatures (single-line parser vs FF indent=2 stdout;
  volatile sqlite/lock entries incl. `-shm` advance), `S4 pass`, product checks passed;
  oracle untouched.
- **J5**: `evidence/snapshot.py` is the executed SNAP command; **0** `.ps1` under `evidence/`.
- **J1/J2/J6**: company choice, receipt-removal construction, pre-registered S1 classification
  table read and consistent with code; the FAIL arm triggered exactly once — on the frozen
  contract check.

## 7. J-C1 pre-existing reds — measure-only, §55 echo (transcribed §8)

3/3 reproduced live by the reviewer, each file predating the attempt:
1. `test_fc1307a_the_three_vendored_copies_are_byte_identical` **FAIL** — RF
   `9294dc7c8df916e0` vs CW+FF `20c9da56f6978bcd` (CW `scripts/host_assumption_guard.py`,
   FF `tools/…`; CI skips when siblings absent).
2. single-owner guard **FAIL** — `scripts/revenue_core.py` imports `subprocess` (second
   download owner).
3. `tools/tests/test_complexity_ratchet.py` **rc=1, 2 failures** — `analysis/confidence.py`
   32 > 23 and `model_extensions.py` 27 > 10 (ratchet scans `scripts/` only; card files live
   in `tests/`+`e2e/`).

Marked "not fixed by this card" — correct per the card rule; the three echo the parent's CI
root-cause **§55**.

## 8. Findings F-RV-01..11 with dispositions (transcribed §10)

| id | sev | disposition after this landing |
|---|---|---|
| F-RV-01 | MAJOR (downstream product) — F-EE1 confirmed: committed cninfo download reports false zero (request_id mismatch ⇒ resolver skip ⇒ envelope `reused_existing`/0 ⇒ response `downloads=0`), violating `fetch_filing.py:663-666` READ-10 + FC-704; replicated ×2 | **downstream carrier → REMEDIATION + fix card `F-EE1-FIX` OPENED by parent** (I-07-B F-finding route; NOT this card's surface; authorized-live-green stays unproven until fixed + owner re-authorizes) |
| F-RV-02 | minor (doc) — decision cited R3 sidecar as `e319f62f…` (that is the accidental run's sidecar; R3 proof says `5a02bb27…`) | **FIXED HERE** in decision.md, original retained (原值留痕) |
| F-RV-03 | minor (doc) — decision said "148 files"; live count 149 / 1 763 067 B | **FIXED HERE** in decision.md (149, original retained) |
| F-RV-04 | minor (process) — binding claimed oracle sha "recorded in handoff"; it is not (the handoff oracle entry is I-00-B's) | **FIXED HERE** in binding.json: freeze proof restated as mtime ordering (08:37:13Z < 09:31:41Z) + live-measured oracle sha `dfc3a6ff…` added to binding's own field; `handoff.input_hashes` deliberately NOT back-edited (frozen pre-review record) — original string retained |
| F-RV-05 | minor (ledger) — RUN-R2 structured `network:"disabled"` false for that execution (1 probe + 1 download) | **FIXED HERE** in commands.json: truthful structured value `{"network":"auto","consumed":"1 probe + 1 download (accidental, J-D2)","ledger_totals_correct":true}` + `__history` of the original string; prose 2+2 totals were already correct |
| F-RV-06 | minor (doc) — decision pointed at "the same pair" in the accidental dir; those 2 files are absent there | **FIXED HERE** in decision.md: substance via `s1_fetch1_stdout.txt` + `journal_outcomes.json`, original wording retained; ×2 replication upheld |
| F-RV-07 | note — literal snapshot key-diff = `["captured"]` (capture stamp); content keys 7/7 | **NOTED** (carried; disclosure nuance, no content drift) |
| F-RV-08 | note (unexercised) — under `force` an unreachable probe does not itself skip (runner 686) | **NOTED** (observed-not-fixed; for a future attempt's oracle/code alignment pass) |
| F-RV-09 | unverified number — "82.7 s" not raw-derivable (closest raw 73.322 s; reviewer 44.40 s) | **FIXED HERE** in decision.md as annotation (number retained, not derivable); qualitative claim re-proven |
| F-RV-10 | note — "≈8.2 MB" double-counts (unique 4.1 MB; 6.2 MB incl. accidental) | **FIXED HERE** in decision.md as annotation (number retained) |
| F-RV-11 | note (bookkeeping) — final tests execution reuses RUN-R2b's registry entry; R2b's nested evidence overwritten | **FIXED HERE** in commands.json `RUN-R2b.note_F_RV_11` (disclosed; superseded pointer: NONE — no pre-image exists) |

Boundary note (§9): the reviewer's own side-effect `.pyc` was created by its pytest re-run and
**deleted by the reviewer**; final RF residue sweep outside `.planning` = count 0.

## 9. Unverified / limitations carried (transcribed §11)

1. Authorized-live-green (`test_live_download_and_delete_restore` under
   `RF_E2E_LIVE_DOWNLOAD=1`) — blocked by F-EE1; reviewer ran no live download; S1-pass
   remains unproven pending product fix + owner re-authorize.
2. Linux CI execution of the new tests file — impossible on this Windows host; evidence =
   guard `new=0`, 0 host literals, code-honest skip-without-siblings; quality.yml path read,
   not executed.
3. The exact "82.7 s" runtime (F-RV-09) and the existence of a separate R2b execution beyond
   prose (F-RV-11).
4. On-disk allowlist pre-image (`bc6da8ff…`) — only the embedded reconstruction is
   verifiable under the no-git rule.
5. Second authorized live execution — deliberately not run (network discipline).
6. HK/dayu and US market paths — outside frozen CN/cninfo scope.
7. Git porcelain state of RF/CW/FF — not probed (boundary: no git); substituted by snapshot
   content-key equality + live pin re-hashes + mtime sweeps.

## 10. Boundaries (transcribed §9) + carrier write surface

- Reviewer write surface = **exactly 2 files** (`reviewer_report.md` +
  `reviewer_report.sha256`); reviewer network = **0**; reviewer git = **0**; production
  catalog opens by reviewer = **0** (stat-only ×2). Reviewer side-effect cleanup disclosed:
  its own assertion-rewrite `.pyc` deleted by the reviewer; one stray empty temp work root
  from the drift probe deleted by the reviewer; temp artifacts retained for audit
  (`%TEMP%\rev_e2e_pytest`, `rev_e2e_runner`, `rev_drift`, `rev_fc1307a`, `rev_ownerg`,
  `rev_pycache*`).
- RF porcelain: protocol snapshots content-identical before/after; `changes.diff` enumerates
  only the 3 card files; `s4.rf_diff.json` `new:[], changed:[], gone:[]` in every run;
  quality.yml pre-attempt; CW/FF zero writes (snapshot keys + S4 checks + live pin re-hashes).
- **This carrier's write surface for the landing**: record-defect fixes to `decision.md`,
  `commands.json`, `binding.json` (history-retaining); then exactly three artifacts —
  `review.md` (this file), `handoff.json`, `evidence/E2E-EXPAND/qualification.json`.
  `reviewer_report.md` and `reviewer_report.sha256` were NOT modified (re-hashed after all
  writes to confirm: 42 915 B / `de849e1a…` / sidecar unchanged). No git; no self-signing.

## 11. Routing conditions transcribed from §12

1. Parent commits the 3 RF files as **batch-6**: `e2e/run_cross_repo_chain_e2e.py`
   (`88ac9e4a…`), `tests/test_cross_repo_chain_e2e.py` (`3e2b39ee…`),
   `tests/contract/host_assumption_allowlist.json` (`ff9db8c8…`, +11 sanctioned pins).
2. **F-EE1 (F-RV-01)** = new downstream finding → owner/remediation ledger via the opened
   `F-EE1-FIX` card; fix NOT pulled into E2E-EXPAND.
3. **Authorized-live-green stays unproven** pending F-EE1 fix + owner re-authorization; until
   then the frozen S1 FAIL stands as the correct outcome (**KEEP THE RED**).
4. Owner's four constraints carried as proven-by-evidence (§1 of this transcription).
5. F-RV-02…F-RV-11 folded into decision/commands/handoff annotations by this landing
   (dispatcher/carrier action — the reviewer edited none of those files).
