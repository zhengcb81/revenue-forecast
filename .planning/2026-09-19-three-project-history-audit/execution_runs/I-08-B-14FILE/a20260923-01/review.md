# REVIEW / carrier landing — I-08-B-14FILE / a20260923-01 (bookkeeping transcription)

## VERDICT BLOCK

- **verdict** = **ACCEPT** — verbatim from the independent reviewer's report (§0 L10):
  "**ACCEPT — the 14-file landing is accepted for merge as the content baseline** (verbatim carrier bytes,
  round-trip proven, RED→GREEN→MUTATION satisfied on re-run, census 0 new failures, TRIAGE coexistence green).
  Two **minor findings** (both documentation/pin hygiene; neither touches the delivered bytes)"
  → landed as **`accepted_scoped`** (four-value-domain mapping: `ACCEPT` → `accepted_scoped`) with
  **F-01 + F-02 carried** (both minor, doc/pin-hygiene, **0 blocking**).
- **carrier** = `reviewer_report.md` (attempt-relative path `execution_runs/I-08-B-14FILE/a20260923-01/reviewer_report.md`)
- **carrier sha256** = `b8b1590929ee3bb9cd5108c61198622157d145de77d581c77d9865c752413ba8` — **20868 B**, 212 lines,
  UTF-8 without BOM (first bytes `35 32 82` = ASCII `# R`), LF-only (0 CR), single trailing LF; re-hashed
  read-only at landing == dispatch pin == sidecar content.
- **pin (sidecar)** = `reviewer_report.sha256` — 85 B, sidecar file sha256
  `0fc6c177e98ac406009b2a63e2888b029f795d607ce7ebde81a1c7db226b0911`, content
  `b8b1590929ee3bb9cd5108c61198622157d145de77d581c77d9865c752413ba8  reviewer_report.md` — **CONTENT-MATCH
  VERIFIED** (sidecar sha == independent live re-hash == dispatch pin); sidecar **0 bytes written**.
- **ruling locations** (1-based lines inclusive; byte proof = 0-based offsets against the file as it stands at
  carrier sha256; multi-line regions include internal LFs and exclude the final LF):
  - title / reviewer face **L1–L9**
  - verdict heading **L10** (`## 0. VERDICT`); **verdict block L10–L27** (incl. F-01/F-02 table + signature note +
    rgm tally) — bytes **715..2722** (2008 B) sha256 `1a81a4d5bb0caca267284ab7279ca381a24675fcd93db05cfeb67897e8d7bfe7`
  - findings table **L16–L19** — bytes 1044..1968 (925 B) sha256 `47ee4c04d4998b10c539717cc27d6fadc3354f778d66b80ab1a922ad3194232e`
    - **F-01 row L18** — bytes **1088..1460** (373 B) sha256 `a73b17eb7470302336ce04ba7280688f5f0ff6f89c34d40dc6b159c14274d549`
    - **F-02 row L19** — bytes **1462..1968** (507 B) sha256 `db9c68bea019aabb532252fd5edfa362bb4de58ddb875e96b23099f249afdcae`
  - **findings + unverified §8 L187–L196** — bytes **18957..19679** (723 B) sha256 `32807d7f9f893108a7e9afafcd8d758e1f5c332c83dc56e0f10f7537dc9574ce`
  - **scope-if-accepting §9 L198–L212** — bytes **19682..20866** (1185 B) sha256 `7b1888a06bbb0f508ab8e273770f743fc7025caa0f88e10fb7bedc2c36053b31`
- **reviewer 独立复核 N=1** = one delegated independent reviewer (session under parent
  `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`), review date 2026-09-24 (post-execution, independent re-run of
  every key arm); method read-only (read/grep/pwsh only; no network; no state-changing git); **write surface
  inside this attempt = ONLY `reviewer_report.md` + `reviewer_report.sha256`** (report L8) — everything else
  zero-written; the implementation face was left `status = review_pending`, unsigned, self-signing nothing →
  acceptance authority rests exclusively with the report; **the report "grants no `accepted` on any other card
  and closes nothing"** (report §0).
- **nature of this file** = bookkeeping transcription (簿记转录): it transcribes the reviewer's verdict and
  limits, **adds no acceptance of its own**. Verdict author = the independent reviewer only; the implementer
  never signs; this landing pass does not sign. **verdict_is_transcribed_not_authored = true**;
  **closed_by_this_card = []**.
- `review.md` pre-image = **none** (the file did not previously exist in this attempt; no implementer stub) —
  created by the carrier-landing bookkeeping pass.

## Corrections applied FIRST (append-only, before the three landing writes)

`decision.md` gained exactly one new section **`## F erratum (landing)`** (everything above it byte-identical):
- sha256 before → after = `61df3f123cec318e8a58176fc5615a904242cca15e88e9814ef75dc6e4b514ab` (14879 B) →
  **`7647f3db53147882cc5dfee773c553404593a7e187a0afa791af0560ff309a01` (18671 B)**; the first 14879 bytes
  re-hash to the pre-image sha (pure append proven), heading count = 1 (idempotency-checked).
- contents = **F-01** (binding §2 constants after-sha transposition: recorded
  `a299e95055f22f3d**79967**…` vs true `a299e95055f22f3d**97967**…`, first diff index 16 / 2 chars; true bytes
  carried by oracle.md L50 + c1 + c2 round-trip (got==want) + c5 + carrier ISO ⇒ delivery unaffected;
  **pin-text correction recorded in the erratum only — `binding.md` NOT rewritten** (sealed pin record);
  authoritative corrected pin = erratum + `handoff.json` bookkeeping + this qualification mirror) ·
  **F-02** (TRIAGE pin `d476c408…`/11212 B/23:54:56 stale vs LIVE
  `c178a118bd9f1d1a683279b709613728bbc124a462d11facbca0f0519221ee0a`/11211 B/2026-09-23 23:58:11, re-measured
  read-only at landing from `execution_runs/RF-STEP9-TRIAGE/a20260923-01/changes.diff`; substantive claims
  proven against live — guard section == c3h probe, patrol re-apply to live RF bytes →
  `76111c51c67cc622704e728c67606ed57761a0e31515ac95306c6768f040a242` exact ⇒ **merge must re-pin at c178a118 +
  re-run compat — recorded as merge precondition**) · **unverified-7 note** (#5 guard-re-change re-probe already
  satisfied by c3h == live; **remaining 6 carried**).

## What the review established (transcribed from `reviewer_report.md`)

### Pins (§2) — 9/9 · 5/5 · ISO 14/14 · after==ISO · mutation trees deviate only where declared
- **RF live, 9 edited == card's open pins (close == open): 9/9** — `278e3e02…` constants · `054e364a…` evidence ·
  `29aaae4f…` publication_registry · `8a761498…` revenue_core · `bc2bb4a3…` revenue_publication ·
  `9abdcec5…` trust_anchor · `d1b7cf03…` test_attestation · `ae6f158c…` test_single_owner_guard ·
  `4e68b98c…` golden_behavior_hashes (measured twice: mid-review + close).
- **5 added paths ABSENT in RF live: 5/5** — `attestation_protocol.py`, `test_attestation_provider_protocol.py`,
  `test_attestation_legacy.py`, `test_publication_attestation_contract.py`, `e2e_support/i08b_fake_provider.py`.
- **Carrier ISO `I-08-B/a20260919-01/iso/rf` == binding after-pins: 14/14**; **after_tree (%TEMP%) == carrier ISO: 14/14**.
- **Mutation trees deviate exactly where declared**: mut_test = `test_attestation.py` before `d1b7cf03` only ·
  mut_prod = revenue_core + revenue_publication before `8a761498`/`bc2bb4a3` only · mut_guard = guard before
  `ae6f158c` only · mut_golden = golden before `4e68b98c` only (each within the 14 pinned paths) ·
  compat_tree = 14/14 == ISO with the **7 non-guard** TRIAGE sections applied, guard == carrier `b5969ba6`.

### Diff / scope mechanics (§4) — round-trip re-done · regen byte-identical · exit-2 double-proven
- Independent `gen_diff` regen: **rc=0**, sha `9721711a214c4dc7745dc960bf0be6280d86f25c8fe750376c9c9daf4a50bb66`
  **byte-identical**, 321042 B, `added=5 / modified=9 / extras=[] / missing=[]`.
- Independent `apply_diff verify`: **14/14 `roundtrip_equal=true`, rc=0**, every `want_sha` == the reviewer's own
  fresh carrier-ISO hash — applying `changes.diff` to before_tree reproduces the carrier after-bytes byte-for-byte.
- **Exit-2 scope guard proven twice**: out-of-scope differing path ⇒ `RC_EXTRAS=2`; expected path dropped ⇒
  `RC_MISSING=2`. Edge noted: expected-path-absent-in-after ⇒ rc 1 (`SystemExit` string), outside the claimed condition.
- Regeneration (D1 and D12, both) byte-identical ⇒ after-state stable; **no run mutated the delivered bytes**.

### RGM re-run (§3) — **3/3/4 all exact** (every frozen expectation matched)
- **RED 3/3**: R1 = 1F/6P, exact node `test_configured_provider_means_host_signed_publication`, `False is not true` ·
  R4 = 1F/2P, `revenue_core.py imports subprocess` · R7 = 1F `volume output hash changed`
  (`97b9044f… != 2f9337fd…`, byte-identical failure signature on mut_golden ≡ retired 13-file tree).
- **GREEN 3/3**: R2 = rc0 **118 passed** — reconciled **N-1: 118 P + 34 subtests** appear under `-q`
  (legacy `22 passed,22 subtests` + contract `10 passed,12 subtests` + other two `86 passed,0 subtests`
  = **118 tests / 34 subtests exactly**; default verbosity prints bare `118 passed`) · R5 = **5P** (3 original +
  2 carrier AST hardening nodes) · R8 = **1P** (carrier golden as-is, exception rule not triggered).
- **MUTATION 4/4**: R3 = 4F/3P identical FAILED set (false-green node + 3 L2 schema nodes) · R3b = 9F/9P
  (handshake node + all 8 reverse cases — two-way load-bearing) · R6 = 1F/2P fires on `attestation_protocol.py` ·
  R9 = 1F, same signature.
- Notes reconciled (not findings): N-1 subtests above · N-2 stale-pyc display = path-display layer only ·
  N-3 r7 tail byte-identical to re-run.

### Census (§3) — **8F/122P → 4F/139P, after ⊂ before, 0 new failures**
- before 8F/122P identical FAILED set (F1 node, F2 node, receipt_attacks, zr1102-c1, zr1102-c4, zr601×2, zr708);
  after **4F/139P**, set `{zr1102-c1, zr601×2, zr708}` ⊂ the before-8, **0 new**; the landing alone turned
  receipt_attacks #1 and zr1102-c4 green.
- **The 4 double-reds are path-disjoint from the delivered 14**: `zr1102::c1` (scratch-`.git` artifact; its file
  `tests/test_zr1102_adversarial_audit.py` is in neither the 14 nor TRIAGE's 7) · `zr601×2`
  (`tests/test_zr601_asset_facts.py` = TRIAGE H3 file) · `zr708` (`tests/test_zr708_backtest_reverify.py` =
  TRIAGE H4 file) — all three files outside `changes.diff`'s 14 sections.
- **Compat: 33P/1F + 8P/1F** — R10 = 33 passed / 1 failed, only `zr1102::test_c1_no_orphaned_script_without_main`
  (pre-existing in both arms; `git grep` needs `.git`, absent in scratch = symmetric env artifact);
  R10b (current patrol) = 8 passed / 1 failed, same c1. R12 ratchet = **RED in BOTH arms** (before:
  `model_extensions.py max 27 > 10` + failures=2; after: `attestation_protocol.py max 27 > 10` + failures=2).

### Overlap adjudication (§5) — 7∩14 = ∅ line-by-line · live 8 sections · forbid rc=3 · context-miss ×2
- **(a)** TRIAGE `decision.md` **L64–70** enumerates exactly `{test_receipt_attacks, mutation_patrol,
  test_zr601_asset_facts, test_zr708_backtest_reverify, test_fc1102_t2_runner, test_fc1302_scan_health,
  daily_t2_runner}` **+ #8 (L71)** — identical to the card's decision §4(a) list (re-read line-by-line at
  landing ✓); **intersection with the 14 = ∅** and none of the 7 appears in `changes.diff`.
- **(b)** LIVE TRIAGE diff = **8 sections** (incl. `tests/test_single_owner_guard.py`), sha
  **`c178a118bd9f1d1a683279b709613728bbc124a462d11facbca0f0519221ee0a` / 11211 B / 23:58:11** (their close-pin
  `d476c408…`/11212 B/23:54:56 stale → **F-02**). Six sections byte-identical across the window.
  - guard: live section == `scratch/triage_guard_current.diff` (extracted 0:01:02) → **c3h probe (0:01:03) WAS run
    against the live version**; earlier c3d (23:51) used a genuinely different observed version (7 line-entries
    apart) → conflict proven at **both** observed versions, both `CONTEXT MISS @@ -37` with the same anchor line
    (`if path.name == CANONICAL_CLIENT or path.name in ORCHESTRATORS:` as printed in the raws) — **context-miss ×2**;
    path-forbid rc=3 read (c3, c3c).
  - patrol: live section == saved 23:56:46 probe; **LIVE patrol section re-applied to live RF bytes → sha
    `76111c51c67cc622704e728c67606ed57761a0e31515ac95306c6768f040a242` == compat_tree's `mutation_patrol`
    exactly** ⇒ compat state ≡ after14 + LIVE non-guard 7, so R10/R10b are valid against the live diff.
- **(c)** E27 stays enforced (validator-level) ⇒ TRIAGE H1/H2/H3/H4 valid: compat 33P incl. receipt_attacks 3/3,
  zr1102-c4, zr601 (H3), zr708 (H4); landing alone turned #1 and #9-c4 green in the census.

### Owner #8 "intent satisfied" — **triple-verified** (§5)
1. carrier `revenue_core.py` (ISO `aec1cf69`): **0 `subprocess` occurrences / 0 import lines** (live RF B1 file has
   1 import line) — grep ✓;
2. spawn lives in `scripts/attestation_protocol.py` (1 import line, 11 occurrences), which the carrier guard
   **`b5969ba6`** names in **`NON_DOWNLOAD_SUBPROCESS_USERS = {"attestation_protocol.py"}`** and hardens with
   `FORBIDDEN_EXEMPT_IMPORTS` (**11** download/network modules incl. `requests/http/socket/filing_fetch_client`),
   `FORBIDDEN_SYMBOLS`, and **two dedicated AST assertions** (exempted file defines no filing-owner symbol;
   imports no download/network module) — guard file read ✓ (155 lines, 5 tests);
3. **#8 node green in R5 (5P)** on the reviewer's re-run ✓.
⇒ the ruling's intent (subprocess allowed outside the download domain) is satisfied de-facto by the landing;
re-expressing TRIAGE's narrowed guard contract on top of the carrier guard stays a merge/owner step.

### Disclosures verified (§6)
- **REM-02 text**: **all 14 carrier files** scanned for `NOT a security boundary | security boundary |
  PublicationReceiptOnlyWarning | validate_forecast_output | attestation_last_failure |
  SIGNED_RESULT_SHA256_SENTINEL` → **0 hits in the carrier**; the phrases ARE in live RF
  (`revenue_publication.py` L24/L55/L450, `revenue_core.py` L156) ⇒ landing the 14 really does remove the REM-02
  markers → **I-08-C F2-text remediation reopens → merge step ② text-only backfill** (the card refused to edit:
  verbatim authorization). B1-only API consumer grep: RF `scripts/` = the two files themselves only; `tests/` = 0;
  `tools/` = 0 → no dangling consumer ✓.
- **R12**: both raws red; after-arm red = the carrier's own new file (27>10) → "merge step ②" is the right
  disposition; **the card made no ratchet-driven edit to its 14** — proven structurally (close re-hash: all 14
  scratch files still == carrier ISO bytes).
- **Unverified 7, each located at `handoff.md` L55–69**: (1) full-suite census (curated-15 only — carried);
  (2) fc1102/fc1302 compat nodes (transferred by file-identity — carried); (3) `zr1102::c1` real-RF status
  unmeasured (pytest inside RF forbidden — carried); (4) per-function CC numbers (REST-B's table is source —
  carried); (5) **TRIAGE guard edited-again re-probe — condition FIRED (23:58:11) and SATISFIED by c3h (0:01:03),
  proven section-identical to live → closed-by-evidence**; (6) cross-repo/real-provider/accuracy (carried);
  (7) WSL arm (Windows-local; carried). **Six remain open + item 5 closed-by-evidence.**

### Boundary (§7)
- **RF zero-write: PASS for the domain checked** — 9/9 close==open (measured twice), 5/5 added absent,
  window mtime scan 23:12–00:10 over `scripts/ tests/ tools/ config/ references/` + RF root files = **NONE**;
  `__pycache__` newest 2026-09-23 10:45 (pre-window); **`.pytest_cache` `nodeids` = 20:37:58 / `lastfailed` =
  20:09:09 (pre-window, unchanged even after the reviewer's own runs — every pytest leg of card and reviewer ran
  cwd=%TEMP% trees)** → **no test ever executed inside RF**.
- **git: ZERO** — card tooling is pure python (`gen_diff.py`/`apply_diff.py` import no subprocess/socket/http);
  the only `git` strings in the attempt are prose, diff-format headers, and the failing zr1102 test's own
  `git grep` content — no git command invoked by card or reviewer.
- **network:** static-only declaration; residual "cannot cryptographically exclude a network call inside a pytest
  leg" stated as unverifiable.
- **carrier / I-08-B attempt untouched:** newest mtime under `execution_runs/I-08-B` (incl. iso) =
  **2026-09-20 15:48** (predates the window); the 14 ISO hashes stable across the reviewer's session.
- reviewer's own writes = only the report + sidecar (+ disposable %TEMP% scratch).

## Findings & dispositions (carrier §8, byte region L187–L196)

| id | class | finding (transcribed) | landing disposition |
|---|---|---|---|
| **F-01** | minor, doc-pin | `binding.md` §2 row 1 prints a transposed after-sha for `scripts/contracts/constants.py` (`…f3d79967…`; true `…f3d97967…`, first diff index 16, 2 chars). oracle.md correct; changes.diff/round-trip/ISO carry true bytes → delivery unaffected; "fix the pin text at landing bookkeeping" | **CORRECTED via append-only erratum** (`decision.md ## F erratum (landing)` item 1): authoritative corrected pin recorded there + in `handoff.json` bookkeeping `f01_corrected_pin` + qualification corrected-pin mirror. **`binding.md` NOT rewritten** (sealed pin record; dispatch order). |
| **F-02** | minor, pin staleness | TRIAGE final pin in binding §4 / c4 (`d476c408…`, 11212 B, 23:54:56) ≠ live file (live `c178a118bd9f1d1a683279b709613728bbc124a462d11facbca0f0519221ee0a`, 11211 B, 23:58:11); all substantive claims hold against live; "merge batch must re-pin" | **RECORDED AS MERGE PRECONDITION** in the decision erratum (item 2) + `handoff.json` `f02_re_pin_precondition` + qualification re-pin mirror: merge must **re-pin at `c178a118…` and re-run compat against that final sha before co-landing both diffs** (report §9 item 3). Both shas recorded. |

No other defect was found on any arm re-run.

## Unverified / carried (§8 second paragraph + §6 item 4)
Six items carried unchanged (item 5 closed-by-evidence, above): full-suite census (curated-15 only) ·
fc1102/fc1302 compat nodes · real-RF status of `zr1102::c1` · per-function CC re-derivation · WSL arm ·
cross-repo consumers / real provider / disclosure accuracy (+ static-only network exclusion); plus OPEN-D1/D2/
D3/D5/D6/D7, E31, registry-anchor field names, R4-1/2/3 all correctly carried, `closed_by_this_card = []`.

## Scope-if-accepting (carrier §9, byte region L19682..20866) — merge instructions transcribed

1. **Accept the 14-file landing as the content baseline**: apply `changes.diff` (sha
   `9721711a…`, 321042 B) — round-trip to carrier after-bytes proven **14/14 byte-exact** by independent re-run.
2. **Merge sequence (recorded)**: **① land the 14 verbatim → ② ratchet re-split of
   `revenue_core.py`/`revenue_publication.py` per the REST-B method (CC table + method; hunks must be REDONE,
   not stacked — dual bases pre-registered in decision §5) + REM-02 "NOT a security boundary" text backfill
   (text-only, reopens I-08-C F2) + #8-guard-final-check [run the guard test AFTER the 14 landing — green
   satisfies the owner ruling; red → re-express the narrowing on top of the carrier guard `b5969ba6`] →
   ③ ratchet re-green + family runs.**
3. **Re-pin TRIAGE's `changes.diff` at merge (current `c178a118…`) and re-run the compat command against that
   final sha before landing both diffs together** — F-02 precondition, recorded in the decision erratum.
4. Correct the F-01 pin text in binding bookkeeping (**done via the erratum; binding bytes untouched**);
   carry the unverified list.

## Not granted / boundaries of THIS file

No product-quality judgment, no promotion, no owner ruling (guard contract narrow-vs-blanket; REM-02
re-statement; REST-B merge order are owner/merge-batch items per decision §4/§3/§5); `disclosure_adaptation`
stays **unmapped** and `accuracy` stays **unproven**; `closed_by_this_card = []`; OPEN-D1/D2/D3/D5/D6/D7, E31,
registry-anchor names, R4-1/2/3 carried; **zero git**; **zero product writes**. This landing wrote exactly
**three files + one decision append**: `decision.md` (erratum section only) · `review.md` (this file, created) ·
`handoff.json` (created) · `evidence/I-08-B-14FILE/qualification.json` (created, new directory).
**Byte-untouched originals (re-hashed read-only at landing)**: `reviewer_report.md`
`b8b15909…`/20868 B · `reviewer_report.sha256` `0fc6c177…`/85 B · `oracle.md` `9afa500e…`/18141 B ·
`binding.md` `063e6ccf…`/11648 B · `commands.md` `fb86b083…`/8079 B · `changes.diff` `9721711a…`/321042 B ·
`handoff.md` `9f0e28f5…`/6278 B · `recovery.md` `040b22f3…`/3209 B · `evidence/` 29 raws · `scratch/` originals.

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent of parent
  `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`), 2026-09-24.
- Corrections FIRST: `decision.md` `## F erratum (landing)` appended before these three writes;
  sha `61df3f123cec318e8a58176fc5615a904242cca15e88e9814ef75dc6e4b514ab` (14879 B) →
  `7647f3db53147882cc5dfee773c553404593a7e187a0afa791af0560ff309a01` (18671 B), pure-append proven
  (first 14879 bytes == pre-image sha; heading ×1).
- Handoff pre-image: `handoff.md` 6278 B, sha256
  `9f0e28f59ceeeb9917734ee1ff02dbb900a7e664c6cc0f7bbe14502d94984051`, `status: **review_pending**` (L3),
  unsigned section L33–L38, `closed_by_this_card = []`, unproven 1–7 at L55–69 — **left byte-untouched**
  (this attempt's `handoff.json` did not exist pre-landing; status_before is sourced from this pre-image).
- sha256 before → after per file: `decision.md` as above · `review.md` = created (this file; hash reported to
  the parent) · `handoff.json` = created (hash reported to the parent) ·
  `evidence/I-08-B-14FILE/qualification.json` = created (hash reported to the parent).
- `implementer_signed: false` · `implementer_never_signs_acceptance: true` ·
  `verdict_is_transcribed_not_authored: true` · reviewer **N=1** · no signature produced · no git.

---
carrier-landing transcription · parent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102` · verdict = **ACCEPT**
→ `accepted_scoped` (F-01 + F-02 carried, both minor doc/pin-hygiene; merge preconditions ②③ binding) ·
this file adds no acceptance of its own.
