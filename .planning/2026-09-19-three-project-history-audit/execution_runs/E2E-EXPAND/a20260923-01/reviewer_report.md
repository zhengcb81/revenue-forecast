# E2E-EXPAND independent review — reviewer_report.md (attempt a20260923-01)

Reviewer: independent review subagent (parent session `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`),
N=1 signer, signing this report only. The implementer did not self-sign: `handoff.json`
`status=review_pending`, `reviewer_status="unsigned — no review.md written by this implementer"`
re-read live at review time. This reviewer's write surface = exactly two files
(`reviewer_report.md` + `reviewer_report.sha256` in this directory); this reviewer edited no other
path (final RF residue sweep outside `.planning`: count=0, §9).

Method: read / grep / pwsh + three reviewer re-runs into `%TEMP%` (pytest wrapper, standalone
runner, drift-gate probe) + gate re-runs (ruff / compileall / host-assumption-guard / fc1307a /
single-owner / complexity-ratchet). Production catalog: `Get-Item` stat only — N=0 opens by this
reviewer. No network by this reviewer (no web calls; the 3 reviewer-executed suite runs report
`live_gate=never`, `network_scope="none (live gate never)"`, and writes 0 `reachability.json`).
No git of any kind by this reviewer. Host TZ = GMT Standard Time (+01:00); ISO-Z timestamps below
are as recorded in the raw artifacts.

## 0. Verdict

**ACCEPTED — SCOPED.** The delivery is reproducible under independent re-derivation, its four
owner-constraints hold with evidence this reviewer re-computed, its disclosures are artifact-backed,
and its exit-honesty face is intact (the authorized-live FAIL was recorded, not amended).

Basis (independently measured this review): 3/3 deliverable file hashes + 14/14 product/data pins +
3/3 I-00-B contract pins re-computed and matched; oracle mtime precedes the first judged run;
snapshot before/after recomputed by this reviewer (content keys 7/7 identical, timestamp key aside);
production catalog size+mtime re-stated before AND after this reviewer's runs (49,677,344,768 B …);
both deletion proofs read and structure-verified (15/2/`post_absent=true`/`asserted=true`);
F-EE1 traced through journal row → resolver skip → envelope → FF response with code citations;
reviewer pytest re-run = 2 passed + 1 skipped rc=0; reviewer runner re-run = exit 0 with S1 skip
`live_gate_never` recorded and S2/S3/S5/S6/S4 pass; drift→exit-2 gate reproduced empirically
(rc=2 `E2E-EXIT2 … rebind required`); ruff/compileall/guard rc=0 (3/3) with guard `new=0`.

Acceptance carries the conditions/carry-scope in §12: parent commits the 3 RF files (batch-6);
F-EE1 is a NEW downstream product finding routed like I-07-B's F-findings (FC-704-class fake
download zero → owner/remediation ledger; the fix is NOT this card's surface); authorized-live-green
stays UNPROVEN until F-EE1 is fixed and the owner re-authorizes; the owner's four constraints are
carried as proven-by-evidence. Eleven minor review findings (F-RV-02…F-RV-11 + boundary note) are
record-/doc defects carried with this report — 0 of them changes the verdict (§10).

Central review question ruled (handoff `next_action`): **keep the red.** The frozen S1
`downloads==1` check is correctly specified against FF's own documented contract
(`fetch_filing.py:663-666`, READ-09/READ-10: "`stats["downloads"]` … 0 unless a download actually
committed"), and a committed download DID occur (journal `downloaded_new`=1, file+sidecar verified,
then deleted). The product reports 0 — that is the defect (F-EE1), not the oracle. The oracle was
not amended after the run either way (oracle.md mtime 2026-09-23T08:37:13Z, i.e. before the first
judged run at 09:31:41Z, and unchanged since).

## 1. Deliverables — live re-hash (task item 1)

| artifact | live value (this reviewer) | expected | match |
|---|---|---|---|
| `e2e/run_cross_repo_chain_e2e.py` | `88ac9e4a4d207c02bd8163a0f3bbec743e4d28e8a32443504398637935466648` / 66 643 B | `88ac9e4a…` / 66 643 B | ✓ (re-hashed twice: start and end of review — 域: RF 工作树该 3 文件) |
| `tests/test_cross_repo_chain_e2e.py` | `3e2b39ee10947c386f21833dbf19b135619d015817c3df91757d04ef7bcc9213` / 7 037 B | `3e2b39ee…` / 7 037 B | ✓ (same double re-hash) |
| `tests/contract/host_assumption_allowlist.json` | `ff9db8c8cdb11f71230de3c576b7b41e65ebf69594e5ddd52d2f712d2727c219` / 4 913 B | `ff9db8c8…` +11 pins | ✓ |
| allowlist pre-image | `bc6da8ff…` / 1 215 B = sha of the `ORIGINAL_ALLOWLIST` text embedded in `evidence/gen_changes_diff.py` (re-computed by this reviewer from that source) | `bc6da8ff…` | ✓ reconstruction verifiable; on-disk pre-image itself is git-unverifiable under the no-git rule (disclosed by decision §4 footnote) |
| `oracle.md` | 16 348 B, mtime 2026-09-23T08:37:13Z | frozen-before-first-run | ✓ by ordering (but see F-RV-04: no oracle sha recorded in handoff) |
| `binding.json` / `commands.json` / `decision.md` / `changes.diff` / `handoff.json` / `recovery/README.md` | present and read in full | present | ✓ |
| handoff state | `status=review_pending`, `reviewer_status=unsigned…`, `input_hashes` populated | review_pending/unsigned | ✓ |

`changes.diff` structure (this reviewer parsed all 1 735 lines): exactly 3 file sections —
`--- /dev/null → b/e2e/run_cross_repo_chain_e2e.py @@ -0,0 +1,1510 @@`,
`--- /dev/null → b/tests/test_cross_repo_chain_e2e.py @@ -0,0 +1,164 @@`,
`--- a/…allowlist.json +++ b/… @@ -12,6 +12,50 @@` (= +44 lines = 11 entries × 4 lines,
3 pre-existing entries preserved as context). Forbidden-pattern grep over the whole diff
(域: changes.diff 全文): `workflow`=0, `.github`=0, `quality.yml`=0, `host_assumption_guard`=0,
`ratchet`=0, `pyproject`=0, `conftest`=0, `pre-commit`=0, `make_gate`=0 hits. The words
`baseline`/`gate`/`CI` that do occur are lines INSIDE the two new files' scenario code (diff `+`
lines), i.e. scenario bookkeeping, not edits to gates/baselines.

Evidence integrity: `evidence/` = **149 files / 1 763 067 B** (1.68 MiB). No SHA manifest exists in
`evidence/` (searched `*manifest*`, `*.sha256` → 0 hits), so this reviewer spot-hashed 20 files
(≥15 required); values recorded here as the review-time integrity baseline (域: 20 个具名证据文件):

```
e747b10bdf882968e00cd0871850e61f2280ec504072d9d2fffa3369514fc649  snapshot_before.json
23e05f5f1e53c0ec2d166409c6d1468e8bfe32f97c59156813dcaa65d07801ea  snapshot_after.json
fa7a6cb449797475911d92e62fb4904a0febb83b2bf1ede7f8ce19d8fa9662b0  run_offline/summary.json
47664b95753d249792228f2cd487655e6e14706dff2e60e6d0b6e9d9b6583251  run_offline/s2/stageB_refusal.json
69dc49f2f6f843adbd9b369ad9bfd14bbd49eb083877a03184baf62bd2aa896d  run_offline/s2/build.json
be2302a4449aaf8f1aceb69334d76350225702752d879d3979f561a1daf78a55  run_offline/s2/receipt_removal.json
951ffed30b4dffcfe063e46607689361ba04f95e7d8f8e60d22e2e0edd270647  run_offline/s3/counters.json
aa936a9784a3a85aecb7e24bda3579f20a7decfddb760734ac4e9fc7dee32c75  run_offline/s4/post_snapshot.json
d0110d0619dd4ec75f0a600fc2d39e79d136ed76ab815b608d626d7a9cd18ca7  run_offline/s4/rf_diff.json
50dff09ba44e6fd9b45270dc916140b7ea66f9bc260e2249b6621b3b758fa159  run_offline/s5/s5_fetch_stdout.txt
657a50579445579e8bf6b66c0570c8332a8627ad61e445bf89bd5925b95e6fcd  run_offline/s6/s6_fetch_stdout.txt
a698d87350a513e88a6c7b7b9fd78d07a4eae4a14c82f0e08d9083fb04f12d55  run_live_pytest/s1/deletion_proof.json
9cce868dff2f8e69a44fbbf9e5af6aa5b5eb2781d1d085b04597005340d3768d  run_live_pytest/s1/journal_rows.json
ec54b1f2769f2a126db0670c4786595102fa4c1d23ac2bb0c374d13433583f52  run_live_pytest/s1/envelope.json
efb9b8ed7410fa447100d9e481a5869e47ebdd319c966adb4a9504ccd06cc24b  run_live_pytest/summary.json
916583d6ebcf88eb22add6f3adf3064f226aeb08adcae58e4c6bd7a772383a83  accidental_auto_gate_run/s1/deletion_proof.json
09c5c7b487d1506930588e52876f3cc9b45ae8703addc4491803e961e80b0a99  accidental_auto_gate_run/summary.json
b09afe7d47a2bb42fefc2750328ef7c28b38bd004e40105e3efa3ce000c5d613  run_pytest_offline_nested/summary.json
a5d5f132b12408315d4f6dff714f74d7f23e1e67683aac1341bdc50f9b18e4e5  run_offline.pre_harness_fix1/summary.json
0c4eb56efeba8c0ff81100a75293661ffff899efb012139c0493bfb56ed7db37  run_offline/preflight.json
```

Timeline proving oracle-first (域: 本 attempt 文件 mtime 与 summary 时间戳):
`snapshot_before 09:31:27Z → first judged run R1 preflight 09:31:41Z / run 09:31:41–09:32:29Z →
R1b 09:33:54–09:34:32Z → accidental auto-gate run 09:35:33–09:36:15Z → R3 authorized
09:41:18–09:41:45Z → snapshot_after 09:43:46Z → final nested pytest run 09:46:03–09:47:18Z →
changes.diff 09:48:48Z → decision 09:51:42Z → handoff 09:53:30Z`, while `oracle.md` = 08:37:13Z and
`binding.json` = 08:38:05Z. Oracle frozen before the 5 judged runs ✓ (0 judged runs precede it).
`commands.json` carries `frozen_before_judged_run: true`; its mtime (09:55:03Z) reflects post-run
result appends — the freeze itself is asserted, not mtime-provable (noted, not counted against:
results text for R2/R3 lives in that file plus decision/handoff).

## 2. The owner's four constraints — each verified with evidence

### 2.1 REAL data (要用真实数据) — VERIFIED

- CW raw bytes re-hashed LIVE by this reviewer:
  `companies/宁德时代/raw/financial_reports/annual/2025-03-14_cninfo_1222806982_2024年年度报告.pdf`
  = `b4f1713d7b821eb076c102711d177fe942ccc2bc8dd171ae5d7a95799a65b0ad` / 2 070 073 B ✓ and
  sidecar `.source.json` = `601349fd9334af58aff992d94795c1081ff5a47e58fa1089e4b6f866af85ba40` /
  3 108 B ✓ — both equal the binding pins, before and after this review (域: 这 2 个 CW 真实文件).
  S2's lake build re-hashes its copy against these pins (`s2.raw_pin_sha256/sidecar` true across
  each S2 execution incl. this reviewer's), `s2.no_synthetic_bytes=true`, and the builder's synthetic
  body-bytes are suppressed per oracle §2.
- S1's authorized download artifact: pre-delete sha retained in BOTH proof files as
  `c15272977147dee7e6935a38ea0e4fd6855370aabb106f54cfe20f7cf6048ec9` / 2 043 710 B (+ sidecar
  3 214 B); the bytes are now DELETED — `deleted_paths` point into pytest tmp trees that no longer
  exist, and both proofs assert `post_absent=true`, `asserted=true`:
  - `evidence/run_live_pytest/s1/deletion_proof.json`: `gate=force`,
    `pre_delete_inventory`=15 entries, `deleted_paths`=2 (PDF `c1527297…` + sidecar
    `5a02bb271cf6a09de23c6baba53c118ea53c4d332f7c9fc10f4b19779a2bfff2`), `post_absent=true`,
    `asserted=true` ✓ — NOTE: decision.md cites R3's sidecar as `e319f62f…`; that digest belongs to
    the accidental run's sidecar (retrieved_at differs: 09:41:43Z vs 09:36:12Z ⇒ different sidecar
    bytes) → F-RV-02.
  - `evidence/accidental_auto_gate_run/s1/deletion_proof.json`: `gate=auto`, 15 entries,
    `deleted_paths`=2 (PDF `c1527297…` + sidecar `e319f62f…`), `post_absent=true`,
    `asserted=true` ✓.
  - Default/CI runs: code path writes the proof with `post_absent=true` even with nothing created
    (runner lines 662-667) — confirmed in this reviewer's runs (`s1/deletion_proof.json` present
    under `%TEMP%\rev_e2e_runner\ev\s1\`).

### 2.2 Isolated env + restore (自建独立环境、测完恢复) — VERIFIED

- Preflight pin gate (drift→exit 2): runner lines 1382-1403 + 1439-1442 implement it; this
  reviewer PROVED it empirically by copying the runner to `%TEMP%\rev_drift\e2e\runner.py`
  (siblings absent ⇒ pins unresolvable): **rc=2**, stderr `E2E-EXIT2: binding drift / unusable
  workspace (rebind required): …` listing the 8 code pins + `sibling repos absent`; 0 files
  besides `preflight.json` were written — the run stopped BEFORE `baseline.json`/scenarios. (Side effect:
  main() creates the default temp work root before preflight, so that probe left one empty
  `%TEMP%\rf_e2e_expand_20260923-101340Z`; this reviewer deleted it — temp-only, zero product
  impact.)
- The 14 product/data pins from `binding.json` re-hashed LIVE = **14/14 MATCH**
  (`source_preparation 91a6dc32…`, `filing_fetch_client b281e6d1…`, `company_wiki_source
  7d1bd8f9…`, `isolated_lake 867ac82b…`, FF `fetch_filing 046cc7dc…`, `filing_contracts 2d1b2e33…`,
  `isolated_wiki 8966e7e1…`, CW `cli fad88c60…`, `prompt_injection 88154de4…`, `cn.json
  d9a4860f…`, CW 3 yaml pins `f9eb72a6…/5b8358de…/04fe21b4…`, FF `company_wiki.json 73917689…`).
  I-00-B contract pins also 3/3 MATCH live (`fdb2a598…/f8a397ec…/e9c82fe4…` at
  `execution_runs/I-00-B/a20260919-01/` — the attempt id in binding.json prose is a label, the files
  live under `a20260919-01`), and the I-07-B sitecustomize citation `58da8b36…` MATCHES.
- Temp storage/config (scope): work roots under `%TEMP%` (default `rf_e2e_expand_<stamp>`; judged runs
  used the explicit `%TEMP%\rf_e2e_expand_a20260923-01`), evidence under the attempt dir;
  `temp_state.json` = `{s1_wiki_absent:true, s2_lake_absent:true, work_root_absent:true}` in each
  S4 execution (R1b, nested ×2, accidental, R3, AND this reviewer's run); the implementer's fixed
  work root `%TEMP%\rf_e2e_expand_a20260923-01` is absent at review time ✓.
- **Restore invariants — recomputed by this reviewer**: read both `snapshot_before.json` and
  `snapshot_after.json`, compared key-by-key: keys = `captured, hashes, prod_catalog_stat,
  ff_config_files, cw_storage_top, cw_entity_files, rf_files`. Literal full diff = `["captured"]`
  (the `datetime.now(timezone.utc)` capture stamp — a timestamp, by construction non-equal);
  excluding that stamp, the content diff = **7/7 keys identical** (域: 这两份快照的 7 个内容键:
  `hashes`5项相等, `prod_catalog_stat` size+mtime_ns 相等, FF config listing, CW storage top,
  CW entity listing, RF scripts/e2e/tests+顶层文件清单 相等). The claim `DIFF_KEYS: []` therefore
  holds under the standard "exclude the capture-stamp key" reading; literal reading gives
  `["captured"]` → recorded as F-RV-07 (disclosure nuance, not a content drift).
- **Production catalog stat claim re-stated LIVE (stat-only, N=0 opens)**:
  `catalog.sqlite3` 49 677 344 768 B, mtime ticks 639253962954069191;
  `-wal` 0 B / 639257183781138917; `-shm` 32 768 B / 639257449760349211 — identical to
  `binding.json.production_catalog_baseline_stat_only` at review start AND at review end (after my
  re-runs). No SQL connection was opened by this reviewer at any point.

### 2.3 Small scale (请用小规模数据测试) — VERIFIED

- 1 company (宁德时代 / 300750, CN/cninfo) × 2 filings: offline FY2024 (2 070 073 B read-only copy)
  + S1 FY2025 download (2 043 710 B, deleted). Unique real bytes = 4.1 MB; counting the accidental
  J-D2 download as well = 6.2 MB; decision's "≈8.2 MB" counts each of the 2 filings twice —
  conservative and far under the 50 MB budget either way (arithmetic note F-RV-10, not a scale
  breach). 7 scenarios defined (cap 8).
- Runtime claims vs RAW outputs (域: 三个 summary.json 的 ISO 时间戳与 elapsed 字段):
  - runner offline **36.234 s** `started 09:33:54.899Z → finished 09:34:32.012Z`
    (S2 14.181 / S3 13.169 / S5 4.127 / S6 3.421 / S4 1.336) = decision's "36.2 s (14.2/13.2/4.1/
    3.4/1.3)" ✓.
  - authorized S1 **23.988 s** inside the R3 nested run `09:41:18.830 → 09:41:45.960`
    (run total 25.505 s) = decision's "24.0 s" ✓.
  - tests file "82.7 s full" — the raw pytest stdout was NOT preserved; the closest raw record is
    the final run's nested runner `run_pytest_offline_nested/summary.json` = **73.322 s**
    (`09:46:03.489 → 09:47:18.498`), consistent with a ~83 s full 3-test session. This reviewer's
    own full re-run = **44.40 s** (pytest-reported) for the same 2 passed + 1 skipped rc=0 outcome
    (faster host state at review time) → the 82.7 s figure is plausible-but-not-re-derivable
    (F-RV-09). The qualitative claim (2 passed + 1 skipped, rc=0) IS re-proven by this reviewer.

### 2.4 不大张旗鼓 — VERIFIED

- `changes.diff` = the 3 card files and nothing else (§1 counts); zero hits for any
  workflow/gate/baseline/tool edit.
- No new CI job: `.github/workflows/quality.yml` mtime = 2026-09-20T14:17:13Z (3 days before this
  attempt), and grep of `.github/` for `run_cross_repo_chain|cross_repo` = 0 hits — the runner is
  referenced by 0 workflows. quality.yml's e2e step remains `python e2e/run_revenue_forecast_e2e.py`
  (line 88); the new tests file is collected by the existing `pytest tests tools/tests` step
  (line 36), whose default path is offline (§4).
- host-assumption allowlist **+11 = the guard's own sanctioned remediation**: the guard's own text
  (`tools/host_assumption_guard.py:316-318`, `--emit-baseline … this script never writes into the
  tree`; allowlist `note` field) registers genuinely host-independent digests; decision J-E2 records
  the rejection of string-splitting as the warned "CONCATENATED … outside this gate's reach"
  evasion. Verified: (a) file has exactly 14 registered hashes = 3 pre-existing + 11 new;
  (b) each of the 11 new entries is a 64-hex CONTENT hash with `where`+`rationale` (域: allowlist
  的 11 个新键); (c) **11/11 literals exist verbatim in the new runner at the claimed lines** —
  spot-4 required, this reviewer verified 11/11: runner L68 `91a6dc32…`, L70 `b281e6d1…`,
  L72 `7d1bd8f9…`, L74 `867ac82b…`, L76 `046cc7dc…`, L78 `2d1b2e33…`, L80 `8966e7e1…`,
  L82 `fad88c60…`, L92 `b4f1713d…`, L94 `601349fd…`, L96 `d9a4860f…`; (d) string-splitting
  evasion NOT used — grep over the runner for concat/slice/chr-obfuscation patterns
  (`['"][0-9a-f]{6,}['"]\s*\+`, `+ …`, `hexdigest()[…]`, `chr(0x)`, sha-slicing) = 0 hits; the
  hashes are plain dict/assignment string literals (runner lines 66-96).

## 3. This reviewer's own re-runs (offline, into %TEMP%)

Interpreter = the attempt's iso venv python (the card's interpreter rule); cwd = RF root; env
`RF_E2E_LIVE_DOWNLOAD` removed (unset); no network.

1. **Tests wrapper** — `python -m pytest tests/test_cross_repo_chain_e2e.py -q -p no:cacheprovider
   --basetemp %TEMP%\rev_e2e_pytest` → **`2 passed, 1 skipped in 44.40s`, rc=0** ✓. The skip is the
   opt-in live test (marker reason = "opt-in live download: set RF_E2E_LIVE_DOWNLOAD=1 …").
   Zero-network assertions over my basetemp tree: `reachability.json` count = **0**; both nested
   `summary.json` = `live_gate=never`, `network_scope="none (live gate never)"`, `exit_code=0`,
   statuses {S1 skip(live_gate_never), S4 pass} and {S2/S3/S5/S6/S4 pass}. **Zero provider fetch in
   my run** (no probe file, no journal, gate=never everywhere).
2. **Standalone runner** — `python -X utf8 -B e2e/run_cross_repo_chain_e2e.py --live never
   --evidence-dir %TEMP%\rev_e2e_runner\ev` (work-root left to its documented default =
   `%TEMP%\rf_e2e_expand_<stamp>`; evidence-dir pointed at %TEMP% on purpose so that RF's default
   `e2e/.runs/…` path was NOT used — RF write-surface protection, deviation-from-optional-instruction
   disclosed here) → **exit 0**, `total 40.173s`:
   - S1 **SKIP `live_gate_never`** ("RF_E2E_LIVE_DOWNLOAD=0 or --live never: no network attempted"),
     deletion proof written;
   - S2 PASS 15.259s (28/28 checks true), S3 PASS 14.402s (18/18 true, incl.
     `s3.zero_provider_calls/zero_scan_calls/zero_producer_calls/zero_catalog_row_delta`),
     S5 PASS 4.678s, S6 PASS 4.194s, S4 PASS 1.638s (**16/16 `s4.*` checks true**);
   - `summary.json`: `live_gate=never`, `network_scope="none (live gate never)"`,
     `production_writes=0`, `exit_code=0`; no `reachability.json` written; the default work root was
     removed by S4 (`temp_state` 3/3 true, dir absent afterwards).
   - Key numbers vs decision §5: mine 15.3/14.4/4.7/4.2/1.6, total 40.2 s vs 14.2/13.2/4.1/3.4/1.3,
     total 36.2 s — same shape, +11% wall time (host-load variance; ordering and pass-set identical).
3. **Drift-gate probe** (bonus): rc=2 `E2E-EXIT2 … rebind required` as detailed in §2.2.

## 4. CI-safety (task item 4) — re-run on final code

| gate | this reviewer's re-run | result |
|---|---|---|
| ruff (CI line 31 scope, on the 2 new files) | `ruff check e2e/run_cross_repo_chain_e2e.py tests/test_cross_repo_chain_e2e.py` (ruff 0.15.18 = CI pin) | **rc=0** "All checks passed!" |
| compileall (CI line 32) | `python -m compileall -q scripts tests tools e2e` with `PYTHONPYCACHEPREFIX=%TEMP%\rev_pycache` (bytecode redirected out of the RF tree) | **rc=0** |
| host-assumption guard (step9/test_fc1307a) | `tools/host_assumption_guard.py --roots tests tools scripts e2e` (tool is read-only by design, lines 53-55) | **rc=0**, `violations=35; new(not baselined/registered)=0; baseline=16; registered_hashes=14` ✓ |
| `tests/test_fc1307a_host_assumption_gate.py` | pytest, basetemp→%TEMP% | **3 passed, 1 failed** — the 1 failure = pre-existing `test_fc1307a_the_three_vendored_copies_are_byte_identical` (RF `9294dc7c8df916e0` vs CW+FF `20c9da56f6978bcd`, reproduced live; CI skips it because siblings are absent there — test lines 76-78) |

**S1 default = skip/never + tri-state statement (actual code behavior this reviewer read):**
- Runner `live_gate()` (lines 518-528), precedence order: `--live never` → `never` (outranks the
  env); env `RF_E2E_LIVE_DOWNLOAD=0` → `never` (force skip, no probe); env `=1` → `force`;
  `--live force` → `force` (when env unset); otherwise → `auto` (probe cninfo; unreachable ⇒
  SKIP with reason; tool files missing ⇒ SKIP; provider-classified failures ⇒ SKIP; offline
  identity/config/request errors ⇒ FAIL per oracle J6 table).
- Tests file: `@pytest.mark.skipif(os.environ.get("RF_E2E_LIVE_DOWNLOAD") != "1", …)` (lines
  129-133) ⇒ S1 executes when env == `1` (exact match); unset/`0`/anything-else ⇒ honest skip.
  The two offline tests always pass `--live never` to the nested runner (lines 90, 118), and
  `--live never` outranks even `env=1` in `live_gate()` — belt-and-braces confirmed.
- decision.md J-E1's stated rationale ("`=1` universally reads as enable ⇒ opt-in for tests;
  force-skip bound to `0`") **matches the implementation**, and matches oracle §1's frozen table.
  One unexercised nuance: under `force`, an unreachable probe does NOT itself skip (line 686
  `gate != "force"`), so oracle J6's "probe unreachable ⇒ skip" arm is reached via the
  subsequent fetch classification — both authorized runs probed `200`, so this path never fired
  (F-RV-08).
- **Runner not referenced by quality.yml**: grep `.github` for `run_cross_repo_chain|cross_repo` =
  0 hits; quality.yml mtime predates the attempt (§2.4). The new tests file is collected by the
  pre-existing pytest step with the offline default — no CI surface added beyond that collection.

## 5. F-EE1 finding — independent verification (task item 5)

The four legs verified against raw evidence + product code:

1. **Journal request_id ≠ resolution request_id** (域: R3 s1 证据两文件):
   - `evidence/run_live_pytest/s1/journal_rows.json` → 1 row, `outcome="downloaded_new"`,
     `request_id="urn:company-wiki:source-request:sha256:e8177b377da8fc80f8e72695535cf97a5282d9261549634523705bbdd8d53ecb"`
     (= `e8177b37…`) ✓;
   - `evidence/run_live_pytest/s1/envelope.json` → `outcome="reused_existing"`,
     `download_events=0`, `response_downloads_field=0`, `response_calls_field=3`,
     `handle_request_id="…sha256:47c3a925dc2ac33af0b343f187aba417961013837bf4304697234834c5e7e993"`
     (= `47c3a925…`, also `handle.request_id` in `s1_fetch1_stdout.txt` line 36) ✓.
2. **resolver.py:1025-1029 skip logic is live and exactly as claimed** — read
   `CW/src/company_wiki/source_catalog/resolver.py` lines 1021-1029:
   `download_events = 0` … `for attempt in journal.read_all(): if attempt.request_id !=
   resolution.request_id: continue; outcome = _ENVELOPE_OUTCOME_BY_JOURNAL…; download_events = 1
   if attempt.outcome in _ENVELOPE_DOWNLOAD_OUTCOMES else 0`. The `e8177b37…` row is skipped ⇒
   `outcome` stays the structural `_STRUCTURAL_OUTCOME[status]` = `reused_existing` and
   `download_events` stays 0. (Context also confirms resolver.py:1078
   `prompt_injection_status = "not_reviewed"` default — oracle's line cite is right.)
3. **Envelope outcome=reused_existing + downloads=0 while journal says downloaded_new** ✓ — and the
   response field is produced by FF mirroring the envelope:
   `FF/scripts/fetch_filing.py:622-629 _record_download_events()` copies
   `handle.resolution_envelope.download_events` into `stats["downloads"]` ⇒ the false 0 propagates
   to the response (`downloads: 0` in `s1_fetch1_stdout.txt` line 103).
4. **FF's documented contract (cite)** — `FF/scripts/fetch_filing.py:660-666`:
   *"`stats["downloads"]` is the download event count from the final resolution envelope
   (0 unless a download actually committed). Final success and failure both preserve these counts
   in the response envelope (READ-09/READ-10)."` — a download DID commit ⇒ reporting 0 violates
   this contract. Cross-contract: **FC-704 forbids fabricated download evidence** —
   `FF/tests/test_fetch_filing.py:315-317`: "an envelope with an impossible download_events count
   is an upstream error — the consumer must never see fabricated evidence"; `RF/tests/
   test_source_preparation.py:159-197` (FC-704 block): ENV-11 "the receipt may never silently claim
   zero downloads … counts come from events/journal, never inferred from the result".
   Consequence chain as decision states: `source_preparation`'s `reuse_receipt.download_calls`
   would claim 0 after a real download — the exact fake-zero class FC-704 exists to prevent.

**Oracle kept frozen / FAIL recorded**: `oracle.md` mtime 08:37:13Z (before first judged run), never
edited after any run (single mtime, no later re-write); the authorized-S1 outcome is recorded as
`status=fail, reason "s1.downloads: expected 1, got 0", exit_code=1` in
`evidence/run_live_pytest/summary.json` and carried into decision §0/§6 as an open review question —
recorded, NOT amended ✓. Replication: the accidental auto-gate run shows the same fake zero from the
same evidence classes (`journal_outcomes.json=["downloaded_new"]` + `s1_fetch1_stdout.txt`
`outcome=reused_existing`/`downloads: 0`, `summary` failures identical) — decision's pointer to
"the same pair" of files (journal_rows/envelope) in that directory is imprecise: those two files
exist in `run_live_pytest/s1/` alone — 0 such files in the accidental dir (F-RV-06); the mismatch substance is present in both runs.

## 6. F1/F2/F3 re-observations (task item 6)

- **S2 raw refusal** — `evidence/run_offline/s2/stageB_refusal.json` (hash spot-recorded §1):
  `explicit_missing_info.names_missing=true` with the message naming
  `prompt_injection_status=not_reviewed` (EXPLICIT-missing-info TRUE ✓) and
  `structured_actionable_present=false`, `actionable_recovery_fields={}` (candidates/next_action/
  required/missing/gap_plan/hint ABSENT ✓ = F2 gap observed, asserted not fixed; summary checks
  `s2.stageB_explicit_missing_info` + `s2.stageB_no_structured_recovery` true in each S2/S3
  execution incl. mine).
- **Entry-never-scan (F1)** — `catalog_count_delta={}` across S2/S3 (`s2.stageB_catalog_delta`,
  `s3.zero_catalog_row_delta` true in each run incl. mine), `documents_pre_run_ge1` true, and the
  spy event stream for the judged offline run contains **6 events, 6/6 `counter="read"`** (域:
  run_offline/counters/events.jsonl) — zero `scan` / `provider` / `producer` events from the entry
  runs while `wiring.json` shows those wraps installed (`status="wrapped"` for
  `SourceCatalog.scan`, both JsonCommandAdapter methods, 3 producer wraps, module-level
  normalizer/summarizer/extractor/llm wraps) ⇒ resolve/ensure never scan, as claimed.
- **No review CLI (F3)** — grep FF `fetch_filing.py` (subcommand construction) and RF `scripts/` for
  any review/prompt-injection recorder: 0 hits; CW `source_catalog/cli.py` enumerates 47
  subparsers (scan/normalize/…/resolve/ensure/close_gap/…) — no `review` command exists. The suite's
  state construction therefore removes the builder receipt to mirror production:
  `receipt_removal.json` = `receipt_present_before=true, audit_present_before=true,
  receipt_absent_after=true` for the CATL document ✓ (J2's construction, honestly recorded).

## 7. Disclosed deviations — verified (task item 7)

- **J-D2 (one accidental real download outside frozen scope)** — timeline from raw stamps:
  R2 first execution `09:35:33Z` with runner `live_gate=auto` → probe `09:35:34Z` status 200
  (`reachability.json`, `gate=auto` in the deletion proof) → real download (retrieved_at
  `09:36:12Z`, journal `downloaded_new`) → S1 FAIL on the same frozen check (first F-EE1 exposure)
  → teardown proof 15/2/`post_absent=true` → evidence dir has exactly **16 files** (counted ✓) →
  fix = `--live never` added to the opt-in test (tests file lines 90/118 now carry it) → R2b and the
  final run both offline (preserved final nested evidence: `gate=never`,
  `network_scope="none (live gate never)"`) → R3 authorized `09:41:18Z` (`gate=force`, probe
  `09:41:20Z` 200). **Effective network ledger = 2 probes + 2 downloads** (2×
  `reachability.json`, 2× `journal_outcomes=["downloaded_new"]`, 2× deletion proofs, both PDFs
  `c1527297…`/2 043 710 B) ✓ — matches decision. Structured-field caveat: `commands.json` RUN-R2
  still carries `"network": "disabled"` while that execution actually consumed the probe+download
  (prose `result_run1` discloses it fully) → F-RV-05.
- **J4 (playwright stack file-copied, pip forbidden)** — `commands.json` grep: `git`=0 hits,
  `pip`=2 hits, BOTH inside prose of ENV-02 ("NO pip/network", "pip/PyPI would violate the network
  budget") — no pip command anywhere in the registry; ENV-01 = robocopy of the I-07-B venv, ENV-02
  = Copy-Item/robocopy of Miniconda site-packages. Live check: `iso/venv/Lib/site-packages/
  playwright` and `selenium` present ✓. No product file touched by ENV-02 (snapshot content keys
  identical, §2.2).
- **J3 (harness-only defects; superseded run preserved)** — `evidence/run_offline.pre_harness_fix1/`
  present (37 files); its `summary.json` = exit 1 with exactly the two described defect signatures:
  (a) S2/S3/S5/S6 failures `stageA… expected …, got None` (single-line parser vs FF's multi-line
  indent=2 stdout), (b) S3 `lake_tree_unchanged` diffing the volatile sqlite/lock entries
  (catalog.sqlite3-shm mtime advance), while `S4 pass` and the product checks passed — matches
  decision J3; oracle untouched (§1 timeline).
- **J5** — `evidence/snapshot.py` (python) is the executed SNAP command; **0** `.ps1` files exist
  under `evidence/` ✓.
- **J1/J2/J6** — company choice rationale, receipt-removal state construction, and the pre-registered
  S1 classification table read and consistent with the code (§2/§4/§6); the classification table
  triggered its FAIL arm exactly once — on the frozen contract check ✓.

## 8. Pre-existing reds J-C1 — measure-only, out of write surface (task item 7 tail)

Reproduced live by this reviewer (3/3 confirmed; each file predates the attempt):

1. `test_fc1307a_the_three_vendored_copies_are_byte_identical` **FAIL** —
   `this repo 9294dc7c8df916e0 vs {company-wiki: 20c9da56f6978bcd, filing-fetch: 20c9da56f6978bcd}`
   (RF `tools/host_assumption_guard.py` live hash `9294dc7c8df916e0…`; CW's copy is at
   `scripts/host_assumption_guard.py` = `20c9da56…`; FF's at `tools/…` = `20c9da56…`). CI skips this
   test (siblings absent). File mtime 2026-09-20 — untouched by this card.
2. single-owner guard **FAIL** — `tests/test_single_owner_guard.py`:
   `AssertionError: 'subprocess' unexpectedly found … revenue_core.py imports subprocess (second
   download owner)` → 1 failed, 2 passed. (`scripts/revenue_core.py` mtime 2026-09-22 — untouched.)
3. `tools/tests/test_complexity_ratchet.py` **rc=1, 2 failures** —
   `analysis/confidence.py max 32 > 23` and `model_extensions.py max 27 > 10` (both under `scripts/`
   = the ratchet's scan root; the card's files live in `tests/`+`e2e/`, outside that ratchet).

The three are marked measure-only / outside the write surface in decision §2, echo the parent's
CI root-cause §55, and are unaffected by the 3 card files (域: 这 3 个先红测试与其断言的文件).
Marked "not fixed by this card" — correct per the card rule.

## 9. Boundaries (task item 8)

- **RF porcelain = the 3 card files (+pre-existing)**: protocol snapshots (content keys) identical
  before/after the attempt; `changes.diff` enumerates the 3 card files (0 others); this reviewer re-hashed the 3 at
  review start and end (identical); `s4.rf_diff.json` (each run incl. mine) = `new:[], changed:[],
  gone:[]`; `e2e/.runs/` contains 0 entries created today and 0 `cross_repo_chain/` dir (pre-existing
  run dirs date to Aug/Sep-18); `.github/workflows/quality.yml` mtime 2026-09-20 (pre-attempt).
  A git porcelain probe was NOT run (this reviewer's boundary forbids git) — the independent
  residue control instead: full RF mtime sweep outside `.planning` for anything written after this
  reviewer's session start = **count 0** after cleanup (see boundary note below).
- **CW/FF zero writes**: snapshot content keys (`cw_entity_files`, `cw_storage_top`,
  `ff_config_files`) identical before/after; runner S4 checks (`ff_*_listing`, `ff_config_bytes`,
  `cw_entity_files`, `cw_real_files_unchanged`) true in each run incl. mine; this reviewer re-hashed
  the CW/FF pins live (MATCH, §2.2) and re-stated the production catalog stat before/after (MATCH).
- **No git verbs**: `commands.json` regex `\bgit\b` = 0 hits; `changes.diff` header + generator
  (`evidence/gen_changes_diff.py`) is pure `difflib` (no git, no `--no-index`); this reviewer ran
  zero git commands.
- **Network ledger**: registry = 12 entries `"disabled"` + 1 entry `"S1-ONLY"` (R3) + the J-D2
  accidental disclosed in RUN-R2's `result_run1` prose (flag stale → F-RV-05); artifacts = 2
  `reachability.json` + 2 `journal_outcomes` + 2 deletion proofs ⇒ 2 probes + 2 downloads total,
  each download verified-then-deleted with proof. This reviewer's own footprint: **0 network** (no
  web tools used; reviewer-executed suite runs 3/3 gate=never; 0 `reachability.json` in my trees).
- **Reviewer writes**: `reviewer_report.md` + `reviewer_report.sha256` in this attempt dir (2 files, 0 others).
  Boundary note (disclosed): my pytest re-run (no `-B`) wrote one assertion-rewrite cache file
  `tests/__pycache__/test_cross_repo_chain_e2e.cpython-313-pytest-9.1.1.pyc` (mtime 11:11:18 local,
  cache-only, excluded from snapshot/S4 scopes by `EXCLUDE_DIRS`); it did not exist validly before
  (their runs used `-B`), and this reviewer **deleted it** — final RF sweep outside `.planning`
  (files written after session start) = count 0. My other runs used `-B` /
  `PYTHONPYCACHEPREFIX=%TEMP%` and `%TEMP%` basetemps; one stray empty temp work root from the
  drift probe was deleted; temp artifacts retained for audit: `%TEMP%\rev_e2e_pytest`,
  `rev_e2e_runner`, `rev_drift`, `rev_fc1307a`, `rev_ownerg`, `rev_pycache*`.

## 10. Findings (this reviewer's numbering)

| id | sev | finding | disposition |
|---|---|---|---|
| F-RV-01 | MAJOR (downstream product) | **F-EE1 confirmed**: committed cninfo download reports a false zero (journal `e8177b37…` ≠ resolution `47c3a925…` ⇒ resolver skip ⇒ envelope `reused_existing`/`download_events=0` ⇒ response `downloads=0`), violating FF READ-10 (`fetch_filing.py:663-666`) and the FC-704 no-fabricated-download-evidence contract (FF `test_fetch_filing.py:315-317`, RF `test_source_preparation.py:159-197`). Replicated ×2 (direct file pair in R3; stdout+journal_outcomes in the accidental run). | **Carrier to owner/remediation ledger** (product defect class, I-07-B F-finding route); fix is NOT this card's surface; authorized-live-green stays unproven until fixed + owner re-authorizes. |
| F-RV-02 | minor (doc) | decision.md deletion-proof line cites R3's sidecar pre-delete sha as `e319f62f…`; the R3 proof file says `5a02bb27…` (`e319f62f…` is the accidental run's sidecar — different `retrieved_at`). PDF `c1527297…` correct in both. | record-correction carried with this report; evidence files are correct as-is. |
| F-RV-03 | minor (doc) | decision §5 says "Evidence footprint 148 files"; live count = **149 files / 1 763 067 B**. | record-correction carried with this report. |
| F-RV-04 | minor (process) | binding.json claims the oracle's "sha256 recorded in handoff", but `handoff.json.input_hashes` records no sha for THIS card's `oracle.md`; the oracle entry present belongs to I-00-B. Freeze proof therefore rests on mtime ordering (08:37:13Z < 09:31:41Z). | record gap; dispatcher/owner may request the hash be added at落定; not re-runnable now without git. |
| F-RV-05 | minor (ledger) | `commands.json` RUN-R2 structured `"network": "disabled"` although that execution performed 1 probe + 1 download (prose-disclosed in `result_run1`). Machine-readable field stale; prose totals (2 probes + 2 downloads) match the artifacts. | record-correction carried with this report. |
| F-RV-06 | minor (doc) | decision F-EE1 evidence pointer claims "the same pair" (`journal_rows.json`+`envelope.json`) in `accidental_auto_gate_run/s1/` — those 2 files are absent there; the mismatch substance exists via `s1_fetch1_stdout.txt` + `journal_outcomes.json`. | pointer imprecision; replication claim substantively upheld. |
| F-RV-07 | note | protocol snapshot literal key-diff = `["captured"]` (capture timestamp); content keys 7/7 identical. `DIFF_KEYS: []` holds under the exclude-timestamp reading. | disclosure nuance recorded. |
| F-RV-08 | note (unexercised) | under `gate=force`, an unreachable probe does not itself skip (runner line 686), so oracle J6's "unreachable ⇒ skip" arm is deferred to the fetch classification. Never fired (both authorized probes = 200). | observed-not-fixed; for a future attempt's oracle/code alignment pass. |
| F-RV-09 | unverified number | decision's "tests file 82.7 s" has no preserved raw pytest output; closest raw = nested runner 73.322 s; reviewer re-run = 44.40 s for the identical outcome. | qualitative claim (2 passed + 1 skipped rc=0) re-proven; the exact seconds are left unverified. |
| F-RV-10 | note | "≈8.2 MB real bytes touched" double-counts the 2 filings (unique 4.1 MB; 6.2 MB including the accidental 2nd download) — conservative vs the 50 MB budget. | arithmetic basis clarified; budget honored by a wide margin. |
| F-RV-11 | note (bookkeeping) | the final tests execution (~09:46Z) has no distinct `commands.json` entry (it re-uses RUN-R2b's identical argv/env), and the final nested evidence is what remains (R2b's copy overwritten). | registry rule "every executed argv recorded" satisfied by argv-identity; evidence-per-execution is thinner for R2b — noted. |

Boundary note (§9): one reviewer-written `.pyc` cache file created and then removed by this
reviewer; final residue count 0.

## 11. Unverified / limitations (honest list)

1. Authorized-live-green (`test_live_download_and_delete_restore` passing under
   `RF_E2E_LIVE_DOWNLOAD=1`) — blocked by F-EE1, by design of the frozen contract; this reviewer
   did NOT execute any live download (network budget + review boundary), so S1-pass remains unproven
   pending product fix + owner re-authorize.
2. Linux CI execution of the new tests file — impossible on this Windows host; available evidence =
   host-assumption guard `new=0`, 0 host literals in the tests file (pathlib/sibling-derived),
   skip-without-siblings path code-honest. The `quality.yml` collection path was read, not executed.
3. The exact "82.7 s" tests runtime (F-RV-09) and the existence of a separate R2b execution beyond
   prose (F-RV-11).
4. On-disk pre-image of the allowlist (`bc6da8ff…`) — the embedded reconstruction is what is
   verifiable under the no-git rule (decision discloses this).
5. Second authorized live execution — deliberately not run (network discipline), consistent with the
   attempt's own choice.
6. HK/dayu and US market paths — outside the frozen CN/cninfo scope; no claim made or checked.
7. Git porcelain state of RF/CW/FF — not probed (boundary: no git); substituted by the snapshot
   content-key equality + live pin re-hashes + mtime sweeps (§2.2, §9).

## 12. Scope conditions if accepting (routing)

1. **Parent commits the 3 RF files as batch-6**: `e2e/run_cross_repo_chain_e2e.py`
   (`88ac9e4a…`), `tests/test_cross_repo_chain_e2e.py` (`3e2b39ee…`),
   `tests/contract/host_assumption_allowlist.json` (`ff9db8c8…`, +11 sanctioned pins).
2. **F-EE1 (F-RV-01)** = new downstream finding, routed like I-07-B's F-findings: product-defect
   class (fake download zero = FC-704-forbidden) → carrier to the owner / remediation ledger;
   the fix is NOT this card's surface and must not be pulled into E2E-EXPAND.
3. **Authorized-live-green stays unproven** pending (a) F-EE1 product fix and (b) owner
   re-authorization of a live run; until then the frozen S1 FAIL stands as the correct outcome.
4. **Owner's four constraints carried as proven-by-evidence** (§2): REAL data (live CW hashes +
   deletion proofs), isolated env + restore (pin gate, temp-only, recomputed snapshot diff, stat-only
   catalog), small scale (1×2, ≤50 MB, runtimes from raw stamps), 不大张旗鼓 (3-file diff, zero
   CI/workflow edits, +11 allowlist pins = sanctioned mechanism, no string-splitting).
5. Findings F-RV-02…F-RV-11 = record corrections / notes carried with this report;落定 step may
   fold them into decision/commands/handoff annotations (dispatcher action — this reviewer did not
   edit those files).

## 13. REM-79 self-check

Tool: `.planning/2026-09-19-three-project-history-audit/execution_runs/REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py`
run as `PYTHONIOENCODING=utf-8 python <tool> reviewer_report.md` from this directory.
RESULT: **exit 0 — 0 violations** (§13.1); `reviewer_report.sha256` is computed over the final
bytes of this file after that green run.

### §13.1 command record

```
$env:PYTHONIOENCODING='utf-8'
python iso/venv/Scripts/python.exe -X utf8 -B \
  ..\..\REM79-MECHANIZATION\a20260922-01\tools\check_domain_assertions.py reviewer_report.md

# iteration 1: 36 violation(s) across 1 file(s)  -> rc=1  (unscoped quantifier words;
#             wording revised in place: scope-quantifiers replaced with explicit counts/scoped phrasing)
# iteration 2: 0 violation(s) across 1 file(s)   -> rc=0  (final state of this file)
```

---
Signed: independent reviewer subagent, N=1 signer (implementer did not self-sign; `handoff.json`
remains `review_pending` — state transitions are the dispatcher's/parent's to make, not this
reviewer's write surface).
