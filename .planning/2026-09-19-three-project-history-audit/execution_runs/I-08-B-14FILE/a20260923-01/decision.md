# DECISION — I-08-B-14FILE / a20260923-01

- card: **I-08-B-14FILE** — the authorization-execution card for I-08-B's accepted `next_action`
  ("Apply the SAME 14 files (9 edited + 5 added) to the product repo from a card authorised to write it"),
  routed by RF-STEP9-TRIAGE finding #2 (attestation false-green rewrite authority = I-08-B).
- implementer: delegated session; **does not self-sign** — status `review_pending`.
- execution face: RF **read-only**; the authorized change is delivered **only** as this attempt's
  `changes.diff` (live-RF → after-state, exactly 14 paths); product/production writes = **ZERO**,
  git = **ZERO**, network = **ZERO**.

## 0. One-line outcome

All **14 authorized files landed verbatim** (carrier after-bytes, 14/14 sha-pinned) into a `%TEMP%` copy of the
live tree; **RED→GREEN→MUTATION proven per family (3/3/4 runs, every frozen expectation matched)**;
curated census **8 failed→4 failed, 0 new failures**; TRIAGE coexistence **green (H1+H2+H3+H4)** with one
file of real overlap (`tests/test_single_owner_guard.py`, conflict → this card's content wins per parent
ruling, re-apply is a merge-batch step); `changes.diff` round-trips byte-exactly to the carrier pins.

## 1. What was executed, and on whose authority (citations)

| # | source | text relied on |
|---|---|---|
| S1 | I-08-B `a20260919-01/handoff.json` (`status=accepted_scoped`, round-4 independent verdict) | `next_action`: "Apply the **SAME 14 files (9 edited + 5 added)** to the product repo from a card authorised to write it, and carry the 8 OPEN items … forward." + `changed_paths.production_patch_required_later` repeating the same 14 |
| S2 | I-08-B `oracle.md` §0/§7/§9 | acceptance face: §7.1 preconditions (RED first → re-intent, never assertion-stretching → reverse-case table → raw rc+stdout), OPEN-D* non-adjudication, freeze "不做" |
| S3 | I-08-B `binding.json.post_run_measurements.artifact_hashes` | the authorized after-bytes (re-measured 14/14 from `iso/rf`) |
| S4 | RF-STEP9-TRIAGE `decision.md` §1 row #2 + §3 + `handoff.md` receipt ① | "family-card-needed (本卡不动) → 落 I-08-B 14 文件"; "本卡改它=越权 → STOP"; "#2 → `I-08-B-14FILE/a20260923-01` 已派" |
| S5 | B1 `decision.md` §4 item 5 + §5.3 | "the false-green source I-08-A §7.1 identified by name … **rewriting it is I-08-B's item**" / the node is the repo's ONLY false-green source and must break |
| S6 | I-08-A `decision.md` §7.1 (L355-377) | frozen acceptance preconditions 1-4 (RED with E32; re-intent to "one successful handshake"; reverse table; raw evidence) |
| S7 | parent ruling (mid-run message, 2026-09-23) | my 14 = content baseline, land verbatim; REST-B/ratchet conflict pre-registered below, re-split = merge-batch step 2; ratchet reds recorded not fixed in-card; TRIAGE-compat arm as planned |

## 2. Per-file verdicts (all 14; shas in binding §2)

| # | file | verdict | face / condition | evidence |
|---|---|---|---|---|
| 1 | `scripts/contracts/constants.py` | **APPLIED VERBATIM** | receipt schema 2.0 + legacy set (D-08B-01; S2 §0 D4-row) | R2/R8/census green; diff hunk round-trip |
| 2 | `scripts/contracts/evidence.py` | **APPLIED VERBATIM** | trust-domain 12-field loader / E20-E25 fail-loud (I-08-A §3) | R2 (L2 nodes) green |
| 3 | `scripts/publication_registry.py` | **APPLIED VERBATIM** | additive attestation anchor keys, old rows readable (S2 §0 registry anchor) | census `test_publication_registry` green both arms |
| 4 | `scripts/revenue_core.py` | **APPLIED VERBATIM** (supersedes B1 — §3) | capability = one bounded handshake (R-PROV-1); spawn moved to `attestation_protocol.py` (guard face §4) | R2 118P; R3b 9F proves load-bearing; ratchet red → §5 |
| 5 | `scripts/revenue_publication.py` | **APPLIED VERBATIM** (supersedes B1 — §3) | record at result top-level (D-08B-02), E27 at validator (T-N46), inclusive payload projection (D-08B-04c), receipt 2.0 | R2/R8/census green; receipt_attacks green (§4) |
| 6 | `scripts/trust_anchor.py` | **APPLIED VERBATIM** | E30 raises coded `AttestationError` with verbatim historical message (D-08B-04d) | R2 (E30 nodes in legacy tests) green |
| 7 | `tests/test_attestation.py` | **APPLIED VERBATIM — the false-green rewrite (finding #2)** | §7.1 re-intent: fake provider + isolated temp trust domain → `host_signed` + verifiable record; reverse cases E01/E02/E32/E03/E04/E08 fail closed; test key never in `config/` | R1 red(1F/6P) → R2 green(0F) → R3 mutation(4F incl. node) + R3b(9F) |
| 8 | `tests/test_single_owner_guard.py` | **APPLIED VERBATIM** (TRIAGE overlap → §4) | CONFLICT-1 hardening: named exemption `NON_DOWNLOAD_SUBPROCESS_USERS` + 2 AST assertions (D-08B-08) | R4 red → R5 green(5P) → R6 mutation(1F) |
| 9 | `tests/golden_behavior_hashes.json` | **APPLIED VERBATIM, no re-refresh needed** | D-08B-04 documented refresh; carrier values validated on THIS tree (exception rule not triggered) | R7 red(13F) → R8 green(14F 1P) → R9 mutation(1F) |
| 10 | `scripts/attestation_protocol.py` | **ADDED (verbatim)** | provider protocol E01-E32, one-shot spawn, T/L refusal-by-default (D-08B-05/06) | imports exercised by R2's 118 nodes |
| 11 | `tests/test_attestation_provider_protocol.py` | **ADDED (verbatim)** | protocol negative/positive suite (S2 §4 T-N\*) | in R2 (0F) |
| 12 | `tests/test_attestation_legacy.py` | **ADDED (verbatim)** | G1-G4 classify, E29/E30 reachability, projection coverage (§6.1, D-08B-04c/04d) | in R2 (0F) |
| 13 | `tests/test_publication_attestation_contract.py` | **ADDED (verbatim)** | real-artifact verifier contract + AST single-projection guards (round-2 fix) | in R2 (0F) |
| 14 | `tests/e2e_support/i08b_fake_provider.py` | **ADDED (verbatim)** | bounded fake provider for the re-intended tests (S6 precondition 2) | in R2 (spawned by handshake/reverse nodes) |

**Product-source changes beyond the authorized 14: NONE.** The diff generator asserts the differing-path set
== the authorized list and exits non-zero otherwise (`extras=[]` in c1/c5 evidence).
Golden values were **not** hand-edited (R8 passed the carrier bytes as-is).

## 3. B1 supersession (the only base drift — disclosed, per parent ruling item 1)

- Drift: live RF `revenue_core.py`/`revenue_publication.py` = B1's promoted `ec307d20` subset implementation
  (spawn in-module, record in-receipt, schema 1.0, `attestation_last_failure()`,
  `PublicationReceiptOnlyWarning`, `SIGNED_RESULT_SHA256_SENTINEL`); carrier base = pre-B1 bytes.
- Disposition: **the authorized 14 win verbatim** — the carrier set is one internally consistent tree
  (the other 12 files assert top-level record + schema 2.0, which B1's placement/`1.0` cannot satisfy);
  a hybrid would break the carrier's own green face. E27 (host_signed without record ⇒ reject) remains
  enforced, at the validator (carrier T-N46) instead of at the builder (B1 REM-01a).
- Gains: full E01-E32 table, trust-domain triple + E20-E25, W/T/L refusal-by-default, replay/expiry split,
  G1-G4 classify, inclusive payload projection, receipt 2.0 + legacy readable, registry anchor keys.
- Losses (flagged for the reviewer/owner, NOT silently absorbed):
  1. `attestation_last_failure()` / `PublicationReceiptOnlyWarning` / sentinel — grep proof this session:
     consumed by **no** product test/tool outside the two files themselves (A5 evidence);
  2. **B1 REM-02's "receipt layer is NOT a security boundary" documentation/marker is NOT re-stated by the
     carrier's `revenue_publication.py`** (greps for `security boundary|PublicationReceiptOnlyWarning|
     validate_forecast_output` in carrier iso = zero hits). Landing the 14 therefore **re-opens I-08-C F2's
     documentation remediation** unless the merge batch re-adds equivalent wording into the carrier file
     (a text-only, non-behavioral addition — recommend merge-batch step 2 alongside the ratchet re-split).
     This card does not make that edit: it would break verbatim authorization.

## 4. Overlap with RF-STEP9-TRIAGE (relationship + resolution)

**(a) The documented 7-file TRIAGE diff vs my 14: intersection = ∅**, file-by-file:
TRIAGE {`tests/adversarial/test_receipt_attacks.py`, `tools/mutation_patrol.py`, `tests/test_zr601_asset_facts.py`,
`tests/test_zr708_backtest_reverify.py`, `tests/test_fc1102_t2_runner.py`, `tests/test_fc1302_scan_health.py`,
`tools/daily_t2_runner.py`} ∩ mine {14 files above} = **∅** → no coordination needed on those 7; none of them
appears in my `changes.diff`.

**(b) The LIVE TRIAGE `changes.diff` grew during my window to 8 sections — one REAL overlap:**
- `tests/test_single_owner_guard.py` was **appended to TRIAGE's diff at 23:46:39** (5423→11184 B, →11212 B at
  23:54:56): an owner-ruled #8 fix ("守卫收窄", OWNER_DECISIONS §22 / register §84 — narrow the guard to
  download-domain tokens). This is one of MY 14.
- **Resolution (applies the task's coordination rule + parent ruling "my content = baseline"):**
  - my `changes.diff` keeps the **carrier** guard bytes verbatim (named exemption + AST hardening, R4→R5→R6
    proven green on this tree);
  - TRIAGE's guard section **cannot apply** on the carrier file — CONTEXT MISS @@ -37 proven against **both**
    observed versions (`evidence/c3d…`, `c3h…`) and detected earlier by the path-forbid check (`c3…` rc=3);
  - the owner ruling's INTENT (subprocess allowed outside the download domain) is **already satisfied
    de-facto** by my landing: `revenue_core.py` no longer imports subprocess at all (spawn lives in
    `attestation_protocol.py`, named-exempted + AST-hardened) → the #8 node is GREEN (R5);
  - **merge-batch step**: re-express the owner-ruled narrow logic ON TOP of the carrier guard file if the
    owner wants the guard CONTRACT itself narrowed (currently the carrier keeps the stricter blanket rule
    + exemptions). Not done here (would break verbatim + it is the owner's text).
- **TRIAGE diff volatility disclosure**: pins in binding §4; my compat claims are pinned to the final
  observed pin (patrol section: current version re-run green R10b; guard: excluded, conflict; the other 6
  sections byte-identical across the window). The merge batch must re-run compat against TRIAGE's final sha.

**(c) Semantic relationship (H1/H2/E27):**
- My after-state keeps E27 enforced (validator-level), so TRIAGE's H1 (`test_receipt_attacks` build
  `unattested`) and H2 (`mutation_patrol._resign` → `unattested`) stay valid — **proven**: compat arm
  `33 passed` incl. receipt_attacks 3/3, zr1102-c4, zr601 (H3), zr708 (H4); only red = `zr1102::c1`, which is
  pre-existing in **both** census arms (its `git grep` needs `.git`, absent in scratch — symmetric artifact).
- Independent finding: my landing ALONE turned #1 (receipt_attacks) and #9's c4 node green in the census
  (after ⊂ before); TRIAGE's fixes remain correct-and-compatible, and their fc×5/zr601/zr708 greens stay
  theirs (files untouched by me, byte-identical before/after).

## 5. REST-B / complexity-ratchet conflict — PRE-REGISTERED (parent ruling items 1-2)

- **Conflict**: REST-B (a20260923-01, review `b7fb08cc` in flight) helper-split `revenue_core.py` (CC 23→6)
  and `revenue_publication.py` (16→5) **against live bytes 8a761498/bc2bb4a3** (B1-era); my diff takes the
  same two live bases to the **carrier** after-bytes (aec1cf69/e311b2bb). Direct stacking collides.
- **Dual sources, stated for the merge batch**:
  | file | REST-B diff base | REST-B target | my diff base | my target | merge order |
  |---|---|---|---|---|---|
  | scripts/revenue_core.py | 8a761498 (B1) | helper-split 23→6 | 8a761498 (B1) | carrier aec1cf69 | **my content first** |
  | scripts/revenue_publication.py | bc2bb4a3 (B1) | helper-split 16→5 | bc2bb4a3 (B1) | carrier e311b2bb | **my content first** |
- **合并序 = ① 我的14 落地（本 changes.diff, verbatim）→ ② 对这2 文件按 REST-B 方法重做 helper 拆分（引用
  REST-B 的 CC 表与方法；其 hunks 不会命中 carrier 内容，须重做而非套用）→ ③ 棘轮复绿。**
- **本 carrier 内容未过棘轮 ≤6/≤10 约束——复杂度重整=合并批步骤2**（在本卡14 落地后对这 2 文件按 REST-B
  方法重做 helper 拆分，引用 REST-B 的 CC 表与方法）。R12 measured: `test_c3_complexity_ratchet_green`
  is **RED in BOTH arms** (pre-existing in live RF = REST-B/RF-RATCHET-FIX domain, and still red on the
  carrier content) — recorded as **交合并批步骤2**; this card made **no** ratchet-driven edit to its 14 files.

## 6. Red → Green → Mutation + census (counts)

| family | RED | GREEN | MUTATION |
|---|---|---|---|
| F1 attestation false-green (finding #2) | R1: 1 failed/6 passed, exactly the named node, `False is not true` (B1-broken as §7.1 demanded; carrier's pre-B1 false-green raw = red1 evidence) | R2: **118 passed +34 subtests, 0 failed** | R3: original test → 4 failed (node RED returns; +3 enumerated L2-schema nodes) · R3b: product side reverted → 9 failed (handshake node + 8 reverse cases) |
| F2 single-owner guard | R4: 1 failed (`revenue_core imports subprocess`) | R5: **5 passed** | R6: original guard → 1 failed (fires on exempted spawn; RED returns) |
| F3 golden refresh | R7: 1 failed (13-file tree) | R8: **1 passed** (14/14, carrier values as-is) | R9: original golden → 1 failed |
| **totals** | **3 runs, 3/3 as frozen** | **3 runs, 3/3 rc=0** | **4 runs, 4/4 as frozen** |

Census (15 curated files): before `8 failed / 122 passed` → after `4 failed / 139 passed`;
**after ⊂ before, zero new failures**. Removed by this landing: F1 node, F2 node, TRIAGE #1, TRIAGE #9-c4.
Remaining 4 (both arms, unchanged): `zr1102::c1` (scratch `.git` artifact), `zr601`×2 (TRIAGE H3), `zr708`
(TRIAGE H4) — their files are untouched by my diff.
Compat: **33 passed / 1 pre-existing red** (R10) + current-patrol re-run **8 passed / 1 pre-existing** (R10b).

## 7. What this card does NOT decide (carried, `closed_by_this_card = []`)

- OPEN-D1/D2/D3/D5/D6/D7, E31, registry-anchor field names, R4-1/R4-2/R4-3 — carried per S1 (handoff).
- Owner ruling on the guard CONTRACT (narrow vs blanket+exemption) — §4(b); owner ruling on REM-02
  re-statement — §3 loss 2; merge order for REST-B — §5. All three are merge-batch/owner items.
- Cross-repo consumers (invest-core), real-provider qualification, forecast accuracy — untouched, unproven.
- This card grants no `accepted` on anything: its own status is `review_pending`.

## 8. Evidence index

oracle.md · binding.md · commands.md · changes.diff (sha binding §3) · handoff.md · recovery.md ·
evidence/r1…r12 (raw stdout+rc per leg) · evidence/c1…c5 (diff gen, roundtrip, TRIAGE apply/conflict,
RF close hashes) · scratch/{gen_diff.py, apply_diff.py, expected_14.txt, triage_*.diff}.

## F erratum (landing)

Appended by the carrier-landing bookkeeping pass (2026-09-24), BEFORE the three landing writes, per dispatch.
**Append-only**: every line above is the sealed original and stays byte-identical. `binding.md` is a sealed pin
record and is **NOT** rewritten — both corrections below are recorded here; this erratum + `handoff.json`
bookkeeping + `evidence/I-08-B-14FILE/qualification.json` mirrors = the authoritative correction surface.

Verdict landed: **ACCEPT** — independent reviewer report `reviewer_report.md` = **20868 B**, sha256
`b8b1590929ee3bb9cd5108c61198622157d145de77d581c77d9865c752413ba8` (== `reviewer_report.sha256` sidecar content,
self-verified read-only at landing). Two minor findings (F-01, F-02), both documentation/pin hygiene; the
delivered bytes (`changes.diff` 321042 B / `9721711a…`) are untouched by either.

1. **F-01 — `binding.md` §2 row 1 (`scripts/contracts/constants.py`) after-sha transposed (pin-TEXT only).**
   - as-sealed (binding §2 row 1): `a299e95055f22f3d79967e2fdab0522120a9011d6bd9fda213b000904a7f2564`
   - **true value: `a299e95055f22f3d97967e2fdab0522120a9011d6bd9fda213b000904a7f2564`**
   - first diff at byte-index **16**, **2 chars** (indices 16–17: recorded `79` ↔ true `97` — a digit transposition).
   - the true bytes are carried by `oracle.md` (L50 table), `evidence/c1_gen_diff.txt`,
     `evidence/c2_changes_diff_roundtrip.txt` (got_sha == want_sha), `evidence/c5_gen_diff_rerun.txt` and the
     carrier ISO `I-08-B/a20260919-01/iso/rf` → **delivery unaffected** (changes.diff / round-trip / ISO all
     carry the true bytes).
   - **pin-text correction recorded HERE only; `binding.md` NOT rewritten** (its content is a sealed pin
     record). Authoritative corrected pin = this erratum + `handoff.json` bookkeeping `f01_corrected_pin` +
     qualification.json corrected-pin mirror.
2. **F-02 — TRIAGE "final" pin stale; recorded as a merge precondition.**
   - stale pin (binding §4 row 1 + `evidence/c4_rf_close_hashes.txt` close-pin): **`d476c40899d1f2090849af912ccbeea5fe1e2a808587e1174e6ab9606848be45` / 11212 B / mtime 2026-09-23 23:54:56**.
   - **LIVE** (re-measured read-only at landing from `execution_runs/RF-STEP9-TRIAGE/a20260923-01/changes.diff`):
     **`c178a118bd9f1d1a683279b709613728bbc124a462d11facbca0f0519221ee0a` / 11211 B / mtime 2026-09-23 23:58:11**.
   - all substantive claims were verified by the reviewer **against the live file**: guard section ==
     `scratch/triage_guard_current.diff` (c3h probe 0:01:03 section-identical to live); patrol section re-applied
     to live RF bytes reproduces compat_tree's `mutation_patrol` sha
     `76111c51c67cc622704e728c67606ed57761a0e31515ac95306c6768f040a242` exactly.
   - **MERGE PRECONDITION: the merge batch must re-pin TRIAGE's `changes.diff` at `c178a118…` and re-run the
     compat command against that final sha before co-landing both diffs** (report §9 item 3).
3. **unverified-7 note:** item #5 (TRIAGE guard edited-again → re-probe) — the condition FIRED (23:58:11 edit)
   and was already **SATISFIED by c3h (0:01:03)**, which the reviewer proved section-identical to the live file.
   **Remaining unverified = 6, carried unchanged**: full-suite census; fc1102/fc1302 compat nodes; real-RF status
   of `zr1102::c1`; per-function CC re-derivation; WSL arm; cross-repo/real-provider/accuracy (plus static-only
   network exclusion, per report §7/§8).

Landing write surface (exactly 3 files + this append): `decision.md` (this section only) · `review.md` (create) ·
`handoff.json` (create) · `evidence/I-08-B-14FILE/qualification.json` (create, new dir). No git; RF untouched;
reviewer report / sidecar / oracle / binding / commands / changes.diff / handoff originals byte-untouched.
