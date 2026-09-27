# REVIEWER REPORT — I-08-B-14FILE / a20260923-01

- reviewer: delegated independent reviewer (session under parent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`)
- card: I-08-B-14FILE (authorization-execution card, 14-file face) · attempt `a20260923-01`
- plan: `2026-09-19-three-project-history-audit`
- review date: 2026-09-24 (post-execution, independent re-run of every key arm (域=RGM/census/compat/round-trip 各 leg))
- boundary honored: RF READ-ONLY (verified by re-hashing, see §7) · CW not opened · read/grep/pwsh only (域=我的会话操作面) ·
  no network · no state-changing git · all my scratch under `%TEMP%` · only two files written (this report + sidecar) (域=本复审写入面)

## 0. VERDICT

**ACCEPT — the 14-file landing is accepted for merge as the content baseline** (verbatim carrier bytes,
round-trip proven, RED→GREEN→MUTATION satisfied on re-run, census 0 new failures, TRIAGE coexistence green).
Two **minor findings** (both documentation/pin hygiene; neither touches the delivered bytes):

| id | severity | one-liner |
|---|---|---|
| **F-01** | minor (doc-pin) | `binding.md` §2 row 1 prints a **transposed** after-sha for `scripts/contracts/constants.py` (`…f3d**79**967…`; true value `…f3d**97**967…`, first diff index 16, 2 chars). `oracle.md` has the correct value; `changes.diff`/round-trip/ISO all carry the true bytes → delivery unaffected; **fix the pin text at landing bookkeeping**. |
| **F-02** | minor (pin staleness) | The **TRIAGE final pin recorded in binding §4 / evidence c4** (`d476c408…`, 11212 B, mtime 23:54:56) is **not the live file**: live = **`c178a118bd9f1d1a683279b709613728bbc124a462d11facbca0f0519221ee0a`, 11211 B, mtime 2026-09-23 23:58:11** — edited after their close-pin and before `binding.md` was finalized (0:04:50). All substantive compat/conflict claims still hold against the live file (proven in §5); **merge batch must re-pin (current sha given here)**. |

Signature face: the implementer left `handoff.md` `status = review_pending`, unsigned, self-signing nothing —
correct per carrier convention. **This report is the independent review that signs the technical face of the
card for the parent's adjudication; it grants no `accepted` on any other card and closes nothing** (the
parent 追认 / human-confirm-unavailable disclosure is recorded separately by the parent per precedent; the card
discloses it at `oracle.md` L8 and `handoff.md` §unsigned).

rgm tally on independent re-run: **RED 3/3 · GREEN 3/3 · MUTATION 4/4 (=3/3/4)** — every frozen expectation (域=oracle §4 冻结的 RGM legs) matched. Census: before `8F/122P` → after `4F/139P`, after ⊂ before (set-wise), **0 new failures**.

## 1. Deliverables (the nine-step set + this report)

| # | deliverable | verified |
|---|---|---|
| 1 | `oracle.md` | present, mtime **23:09:53 < first raw 23:18:57** (frozen-first proven by mtime); 14-file table, drift disposition, overlap rules, RGM protocol all present (域=oracle 四要素)； human-confirm-unavailable disclosed (L8); parent 追认 to be recorded separately (per task, not the card's) |
| 2 | `binding.md` | present; carrier pins + measured before/after + env + volatile cross-card pins + results; **F-01 fix needed** in §2 |
| 3 | `commands.md` | present; every leg mapped to a raw (域=commands C0–C16/D1–D13 表); 6 incidents disclosed (binding §6) |
| 4 | `decision.md` | present; §3 B1-supersession + REM-02 reopening, §4 TRIAGE overlap + volatility pins, §5 REST-B/ratchet double-base + merge sequence ①②③ + R12 both-red, citations S1–S7; **S1 verified verbatim** against `I-08-B/a20260919-01/handoff.json` L28 ("Apply the SAME 14 files (9 edited + 5 added) … from a card authorised to write it"); grep of carrier decision.md for 棘輪|ratchet|≤6|cyclomatic = **0 hits** → §5's quoted sentences trace to parent ruling S7 + REST-B only; no carrier sentence was fabricated |
| 5 | `changes.diff` | 321042 B, sha `9721711a214c4dc7745dc960bf0be6280d86f25c8fe750376c9c9daf4a50bb66`; **14 sections; my independent regen byte-identical (rc=0, extras/missing empty)**; **round-trip re-done by me: 14/14 `roundtrip_equal=true`, rc=0, and every got_sha (域=14 files 的 section 集) == my own fresh carrier-ISO hash**; `gen_diff` exit-2 on out-of-range proven twice (extras ⇒ RC=2 on a mini-tree; missing-expected ⇒ RC=2). Edge noted: an expected path absent in after-tree exits 1 (`SystemExit` string), beyond the claimed condition |
| 6 | `handoff.md` | present; `status = review_pending`, unsigned section present, `closed_by_this_card = []`, unproven 1–7 all located (域=handoff L55–69) |
| 7 | `evidence/` | **exactly 29 raws**; spot-checked >10 (r1, r2, r5, r7, r8, r10, r11×2, r12×2, c1, c2, c3/c3b/c3c/c3d/c3e/c3f/c3g/c3h, c4) — each consistent with my re-run or with the disclosed incident chain |
| 8 | `recovery.md` | present; RF nothing-to-recover argument sound (backed by my close re-hash) |
| 9 | report to parent | final `send_message` (this review supersedes the need for re-verification) |
| 10 | this reviewer report + sidecar | written before reporting back (as ordered) |

## 2. Pins (re-measured myself, twice: mid-review and close)

- **RF live,9 edited = card's open pins (close == open): 9/9** —
  `278e3e02…` constants · `054e364a…` evidence · `29aaae4f…` publication_registry · `8a761498…` revenue_core ·
  `bc2bb4a3…` revenue_publication · `9abdcec5…` trust_anchor · `d1b7cf03…` test_attestation ·
  `ae6f158c…` test_single_owner_guard · `4e68b98c…` golden_behavior_hashes.
- **5 added paths ABSENT in RF live: 5/5** (`attestation_protocol.py`, `test_attestation_provider_protocol.py`,
  `test_attestation_legacy.py`, `test_publication_attestation_contract.py`, `e2e_support/i08b_fake_provider.py`).
- **Carrier ISO `I-08-B/a20260919-01/iso/rf` = binding after-pins: 14/14** (fresh hashes, stable across my session).
- **after_tree (`%TEMP%`) = carrier ISO: 14/14**; mutation trees deviate exactly where declared
  (mut_test: `test_attestation.py`=before d1b7cf03 only (域=14 pinned paths) · mut_prod: revenue_core+revenue_publication=before
  8a761498/bc2bb4a3 only (域=14 pinned paths) · mut_guard: guard=before ae6f158c only (域=14 pinned paths) · mut_golden: golden=before 4e68b98c only (域=14 pinned paths) ·
  compat_tree: 14/14 == ISO with the 7 non-guard TRIAGE sections applied, guard == carrier b5969ba6).
- `changes.diff` sha/bytes as recorded; regen byte-identical ⇒ no run mutated the after-state.

## 3. RGM re-run (their commands, `%TEMP%`, `C:\Miniconda\python.exe` 3.13.9 / pytest 9.1.1, PYTHONDONTWRITEBYTECODE=1, PYTHONIOENCODING=utf-8, per-leg basetemp)

| leg | card raw | my independent re-run | match |
|---|---|---|---|
| R1 RED F1 (before) | 1F/6P, exact node, `False is not true` | **1F/6P**, same node `test_configured_provider_means_host_signed_publication`, same assertion | ✓ |
| R2 GREEN F1 (after, 4 files) | rc0, `118 passed, 34 subtests passed` | **rc0, 118 passed** (default v) → with `-q`: legacy `22 passed,22 subtests` + contract `10 passed,12 subtests` + other two `86 passed,0 subtests` = **118/34 exactly** | ✓ (see N-1) |
| R3 MUT (mut_test, original test) | 4F/3P incl. false-green node +3 L2 nodes | **4F/3P, identical FAILED set** (configured_provider / forged_signature / stale_event / whitelist) | ✓ |
| R3b MUT (mut_prod, product2files reverted) | 9F/9P incl. handshake node + reverse cases | **9F/9P, identical FAILED set** (handshake + 8 E-cases: bare_py/directory/missing/no_provider/plain_txt/sys_executable/unset/unstartable) — two-way load-bearing proven | ✓ |
| R4 RED F2 (before) | 1F/2P `revenue_core.py imports subprocess` | **1F/2P**, same node, same message | ✓ |
| R5 GREEN F2 (after) | 5P | **5P** (3 original + 2 carrier AST hardening nodes) | ✓ |
| R6 MUT F2 (mut_guard) | 1F/2P fires on `attestation_protocol.py` | **1F/2P**, same node/message | ✓ |
| R7 RED F3 (13-file state) | 1F `volume output hash changed` | **1F**, byte-identical failure signature (`97b9044f… != 2f9337fd…`) — run on mut_golden, whose state (13 carrier + original golden) is content-identical to the retired 13-file tree; my R7 and R9 outputs are identical, as the state identity predicts | ✓ |
| R8 GREEN F3 (after 14/14) | 1P | **1P**, carrier golden as-is (exception rule not triggered) | ✓ |
| R9 MUT F3 (original golden) | 1F | **1F**, same signature | ✓ |
| census15 before | 8F/122P | **8F/122P, identical FAILED set** (F1 node, F2 node, receipt_attacks, zr1102-c1, zr1102-c4, zr601×2, zr708) | ✓ |
| census15 after | 4F/139P, after⊂before, 0 new | **4F/139P**; set {zr1102-c1, zr601×2, zr708} ⊂ the before-8; **0 new**; landing alone turned receipt_attacks #1 and zr1102-c4 green (present in before, absent in after) | ✓ |
| R10 compat (after14 + TRIAGE non-guard7) | 33P/1F only `zr1102::c1` | **33P/1F**, only `test_c1_no_orphaned_script_without_main` (域=R10 node set) | ✓ |
| R10b (current patrol) | 8P/1F same c1 | **8P/1F** | ✓ |
| R12 ratchet c3 | RED before / RED after | **RED both** — before: `model_extensions.py max 27 > 10` (+ `FAILED (failures=2)`); after: `attestation_protocol.py max 27 > 10` (+ failures=2) | ✓ |

**Census 15 / the 4 double-reds (path-disjointness verified):** `zr1102::c1` (scratch-`.git` artifact; its file
`tests/test_zr1102_adversarial_audit.py` is in neither the 14 nor TRIAGE's 7), `zr601×2`
(`tests/test_zr601_asset_facts.py` = TRIAGE H3 file), `zr708` (`tests/test_zr708_backtest_reverify.py` = TRIAGE
H4 file) — **all three files are outside `changes.diff`'s 14 sections**; the card's claim "TRIAGE-owned /
not-touched by my diff" holds for the domain of the delivered diff (zr1102 itself is nobody's TRIAGE file; it
is untouched by the 14 and its red is the disclosed scratch-env artifact).

**Notes (reconciled, not findings):**
- **N-1 (subtests):** the `34 subtests` figure appears only under `-q` (pytest core `_pytest.subtests`) (域=pytest 汇总行输出格式);
  default verbosity prints bare `118 passed`. My `-q` legs reproduce **22+12 = 34** subtests and **86+22+10
  = 118** tests → their headline number is exact, not inflated.
- **N-2 (stale pyc display):** their r1 raw traceback shows the RF absolute path (the disclosed binding §6.2
  incident); my re-run shows the same node/failure with tree-relative paths — 展示层 only (域=raw traceback 路径显示).
- **N-3:** r7 raw text vs my re-run: identical failure signature (byte-compare of tails).

## 4. Diff / scope mechanics (re-proved)

- Independent `gen_diff` regen: rc=0, sha `9721711a…` byte-identical,321042 B, `added=5 / modified=9 /
  extras=[] / missing=[]`.
- Independent `apply_diff verify`: **14/14 roundtrip_equal, rc=0**, each `want_sha` == fresh carrier-ISO hash
  (i.e. applying `changes.diff` to before_tree reproduces the carrier after-bytes byte-for-byte — stronger than
  the carrier's own diff, as the card claims).
- Exit-2 scope guard: **proven twice** (out-of-scope differing path ⇒ `RC_EXTRAS=2`; expected path dropped ⇒
  `RC_MISSING=2`). Edge: expected-path-absent-in-after ⇒ rc 1 (outside the claimed condition).
- Regeneration (域=D1 与 D12 两次 gen_diff) byte-identical ⇒ after-state stable (card's claim ✓).

## 5. Overlap adjudication (decision §4)

**(a) Documented 7 vs my 14 — I diffed the path lists myself:** TRIAGE `decision.md` L64–70 enumerates exactly
`{test_receipt_attacks, mutation_patrol, test_zr601_asset_facts, test_zr708_backtest_reverify, test_fc1102_t2_runner,
test_fc1302_scan_health, daily_t2_runner}` + #8 (L71) — identical to the card's decision §4(a) list;
**intersection with the 14 = ∅** ✓ and none of the 7 (域=TRIAGE decision L64–70 路径表) appears in `changes.diff` ✓.

**(b) LIVE TRIAGE diff:** currently **8 sections** (incl. `tests/test_single_owner_guard.py`) — sha now
**`c178a118…`/11211 B/23:58:11** (their close-pin `d476c408…`/11212 B/23:54:56 is stale → **F-02**).
Section-by-section vs their saved probes: receipt_attacks / fc1102 / fc1302 / zr601 / zr708 / daily_t2
**byte-identical across the whole window (6)**; `mutation_patrol` and `single_owner_guard` moved (as they said).
- **guard:** live section == `scratch/triage_guard_current.diff` (extracted 0:01:02) → **the c3h probe (0:01:03)
  WAS run against the live version**; the earlier c3d probe (23:51) used a genuinely different observed version
  (7 line-entries apart, comment/encoding level) → conflict proven at **both** observed versions, both
  `CONTEXT MISS @@ -37` with the same anchor line (`if path.name == CANONICAL_CLIENT or path.name in ORCHESTRATORS:`) — read both raws ✓. Path-forbid rc=3 read (c3, c3c) ✓.
- **patrol:** live section == saved23:56:46 probe; **I applied the LIVE patrol section to live RF bytes →
  sha `76111c51…` == compat_tree's mutation_patrol exactly** → compat state ≡ after14 + LIVE non-guard7, so my
  R10/R10b re-runs above are valid against the live diff (c3g "idempotent/already-post-state" claim ✓).

**Owner #8 "intent satisfied" — all three sub-claims verified (域=①grep ②guard 文件 ③R5 节点 三证):**
1. carrier `revenue_core.py` (ISO aec1cf69): **0 `subprocess` occurrences / 0 import lines** (live RF B1 file has
   1 import line) — grep ✓;
2. spawn lives in `scripts/attestation_protocol.py` (1 import line,11 occurrences), which the carrier guard
   `b5969ba6` **names in `NON_DOWNLOAD_SUBPROCESS_USERS = {"attestation_protocol.py"}`** and hardens with
   `FORBIDDEN_EXEMPT_IMPORTS` (11 download/network modules incl. `requests/http/socket/filing_fetch_client`),
   `FORBIDDEN_SYMBOLS`, and **two dedicated AST assertions** (exempted file must define no filing-owner symbol;
   exempted file must import no download/network module) — read the guard file ✓ (155 lines, 5 tests);
3. **#8 node green in R5 (5P)** on my re-run ✓.
⇒ the ruling's intent (subprocess allowed outside the download domain) is satisfied de-facto by the landing;
re-expressing TRIAGE's narrowed guard contract on top of the carrier guard stays a merge/owner step (correctly
left open by the card).

**Compat arm: re-run myself → 33P/1F (only c1) +8P/1F on the zr1102 slice** ✓ against the live-diff state (域=R10/R10b FAILED set).

## 6. Disclosures verified

1. **§3 REM-02 text (extra finding):** scanned **all 14 carrier files** (域=carrier iso/rf) for
   `NOT a security boundary | security boundary | PublicationReceiptOnlyWarning | validate_forecast_output |
   attestation_last_failure | SIGNED_RESULT_SHA256_SENTINEL` → **0 hits in the carrier**; the same phrases ARE
   in live RF `revenue_publication.py` (exact sentences: L24 `SECURITY BOUNDARY (B1 / REM-02): …`, L55
   `Marker: validate_publication_receipt is NOT a security boundary.`, L450 `… — NOT a security boundary.`) and
   `attestation_last_failure` in live `revenue_core.py` L156. **Landing the 14 therefore really does remove the
   REM-02 "NOT a security boundary" markers → I-08-C F2-text remediation reopens → merge step ② text-only
   backfill** — the card's disclosure is honest and correctly scoped (it refused to edit: verbatim authorization).
   B1-only API consumer grep (A5 claim): `attestation_last_failure|PublicationReceiptOnlyWarning|
   SIGNED_RESULT_SHA256_SENTINEL` in RF `scripts/` = only the two files themselves (域=RF scripts/*.py grep);
   RF `tests/` = 0; RF `tools/` = 0 → no dangling consumer ✓.
2. **§5 R12:** both raws read (before + after), both RED, quoted assertions match the tree states (before =
   pre-existing REST-B/RF-RATCHET domain `model_extensions.py27>10`; after = carrier's own new file
   `attestation_protocol.py27>10`) → "交合并批步骤2" is the right disposition, and **the card made no
   ratchet-driven edit to its 14** — proven structurally: my close re-hash shows all 14 scratch files (域=七棵 %TEMP% trees) still ==
   carrier ISO bytes (a ratchet edit would break that) ✓.
3. **§4 TRIAGE volatility:** current sha reported in F-02 / §5 above (`c178a118…`,11211 B,23:58:11) vs their
   pin `d476c408…`; merge must re-pin (their own handoff already mandates re-running compat at TRIAGE final sha —
   and my §5 shows the live sha already differs from their "final" pin).
4. **Unverified 7 — each located at `handoff.md` L55–69:** (1) full-suite census not run (this review also ran
   only the curated15 → still open, carried; 域=15 curated files); (2) fc1102/fc1302 nodes not exercised in compat (files byte-equal
   before/after and disjoint → transferred by file-identity, not re-proven — still open); (3) `zr1102::c1`
   real-RF status unmeasured (running pytest inside RF forbidden — still open); (4) per-function CC numbers not
   re-derived (REST-B's table is source — still open); (5) TRIAGE guard edited-again re-probe — **condition FIRED
   (23:58:11 edit) and was satisfied by c3h at0:01:03, which I proved section-identical to the live file**;
   (6) cross-repo/real-provider/accuracy untouched (still open); (7) WSL arm not run (Windows-local only (域=本机会话平台) —
   still open). Six remain open + item5 closed-by-evidence.

## 7. Boundary

- **RF zero-write (card): PASS for the domain checked (域=9+5 pinned paths / window mtime 扫描目录集)** —9/9 close==open (measured twice),5/5 added absent,
  window mtime scan23:12–00:10 over `scripts/ tests/ tools/ config/ references/` + RF root files = **NONE** (域=上述目录集),
  `__pycache__` newest = 2026-09-2310:45 (pre-window), `.pytest_cache` `nodeids`=20:37:58 / `lastfailed`=20:09:09
  (pre-window, unchanged even after MY runs — every one of my pytest legs (域=本复审 R0/R1–R12/census/compat 各跑) ran cwd=%TEMP% trees with basetemp
  under `%TEMP%`) → no test ever executed inside RF by the card or by me.
- **git:** card tooling is pure python (`gen_diff.py`/`apply_diff.py` import no subprocess/socket/http — grep
  clean); the only `git` strings anywhere in the attempt (域=attempt 目录全文 grep) are prose, diff-format headers, and the *content* of
  the failing zr1102 test (`git grep` inside test code) — **no git command was invoked by the card**; I invoked
  none (域=本复审全部 pwsh 命令) either.
- **network:** static only (域=attempt 工具面静态扫描) — `commands.md` declares none; no Invoke-WebRequest/curl/wget/requests/urllib usage in
  the attempt's tooling; **I cannot cryptographically exclude a network call inside a pytest leg** → residual
  unverifiable, stated.
- **carrier / I-08-B attempt untouched:** newest mtime under `execution_runs/I-08-B` (incl. iso) =
  2026-09-2015:48 (predates the window); the14 ISO hashes were stable across my whole session ✓.
- **my writes:** only this report + `.sha256` (and disposable `%TEMP%` scratch/basetemp/regen files) (域=本复审文件写入集).

## 8. Findings & unverified (for the parent's adjudication)

**Findings:** F-01 (binding §2 constants pin typo — fix text) · F-02 (TRIAGE final-pin stale — re-pin
`c178a118bd9f1d1a683279b709613728bbc124a462d11facbca0f0519221ee0a`/11211 B/23:58:11 at merge). No other defect
found on any arm re-run.

**Unverified / carried (not this card's to close):** full-suite census; fc1102/fc1302 compat nodes; real-RF
status of `zr1102::c1`; per-function CC re-derivation; WSL arm; network-call exclusion (static-only);
cross-repo consumers / real provider / disclosure accuracy; OPEN-D1/D2/D3/D5/D6/D7, E31, registry-anchor field
names, R4-1/2/3 (all correctly carried (域=OPEN 清单 8+3 items), `closed_by_this_card = []`).

## 9. Scope-if-accepting (merge instructions)

1. **Accept the14-file landing as the content baseline:** apply `changes.diff` (sha `9721711a…`,321042 B) —
   round-trip to carrier after-bytes is proven14/14 byte-exact by independent re-run.
2. **Merge sequence (recorded):** ① land the 14 verbatim → ② ratchet re-split of
   `revenue_core.py`/`revenue_publication.py` per the REST-B method (CC table + method; hunks must be redone,
   not stacked — dual bases pre-registered in decision §5) **+** REM-02 "NOT a security boundary" text backfill
   (text-only, reopens I-08-C F2) **+** #8-guard-final-check [parent note: run the guard test AFTER the14
   landing — green satisfies the owner ruling; red → re-express the narrowing on top of the carrier guard
   `b5969ba6`] → ③ ratchet re-green + family runs.
3. **Re-pin TRIAGE's `changes.diff` at merge** (§4 pin; current `c178a118…`) and re-run the compat command
   against that final sha before landing both diffs together.
4. Correct the F-01 pin text in binding bookkeeping; carry the unverified list.

REM-79 self-check: run on this file before delivery (result recorded in the sidecar/receipt line below).
