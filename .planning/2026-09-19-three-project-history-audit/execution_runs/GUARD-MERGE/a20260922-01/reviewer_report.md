# Reviewer report — GUARD-MERGE / a20260922-01

Independent review of the parent-standardization composition of the three
sibling iso faces (TTL-30D-POLICY / FIX-W06-GAPS / I-06-A) into the final
production guard.

**Verdict: ACCEPT** (scope-limited to the three composed faces; conditions in
§8). Reviewer: independent review subagent of parent session
`session-bfecd191-fbc3-4a66-8ed1-6562479bf102`. Reviewed 2026-09-23 (reviewer
local clock, UTC+1 offset observed on this host). Method: read/grep/pwsh — domain: this review's declared tool scope;
reviewer runs in `%TEMP%\rvrev-gm` — domain: all %TEMP% runs of this review (mirror-only, RF/CW product trees opened
READ-ONLY); zero git state-changing verbs by this review (one read-only
`git status --porcelain` + `git log` spot, disclosed in §7); this report +
its `.sha256` sidecar are 2 written files — domain: my own writes in this session (this report + its sidecar).

Parent rules applied: `REMEDIATION_REGISTER.md` §48 (U-3 ruling items 1–5),
frozen verbatim in `oracle.md §1` (rules 1–5 = §48 items 1–3 unpacked: REJECT
form / FIX faces incl. `prompt_injection.py` / state_domain union / CLIP drop;
`oracle §4` = §48 item 4 batteries; `oracle §7` + handoff = §48 item 5
commit-after-review). I re-read §48 and confirm the card's five-battery plan
and commit gate match it.

## 1. Deliverables — re-hashed live this review

Every value below is MY live re-hash (Get-FileHash SHA256), not transcribed — domain: this review's 13-row re-hash table:

| artifact | claimed | observed | ok |
|---|---|---|---|
| `oracle.md` | `c346e450…552d5` | `c346e4503834db3a197177acd932a093d501d232fb6a3f361c47f0ac78e552d5` | ✓ |
| `oracle_freeze.json` | `b172e26f…95d8` | `b172e26f7f2bc338f74d8aebe2107e8b3f636264ebbdfb7bd5908fe6a68a95d8` | ✓ |
| `binding.json` | `983623c8…cf03` | `983623c820b9ef13adaa3fa825b70244f4cf84837506d1cd6eeafb64b530cf03` | ✓ |
| `commands.json` (C1–C19 present) | `86b08fdb…0904` | `86b08fdb78bd2696d8b83d24faab65c70d8289bf8f496447be15df0282030904` | ✓ |
| `decision.md` | `04078cb0…d831` | `04078cb01d690864f335e8c3b3b75d5dd86d5054f270ae485fe34277630bd831` | ✓ |
| `changes.diff` (difflib) | `87595cdb…201a` | `87595cdbad354409579d6ecd1e535783aa418fef04e9d886aad142e9165e201a` | ✓ |
| `handoff.json` (status `review_pending`, `signature.signed=false`) | `e8b7cef9…ca7f` | `e8b7cef9e69abd1369a476c29413241d2b46d62caf09b0fcef72a3578cc6ca7f` | ✓ |
| `recovery.md` (per-file revert table: TTL / FIX / I-06-A / before) | `f7365ae3…a942` | `f7365ae3d6106bdf44fbcf1b4456aee2f7e26695f169ad3728b2d39db9faa942` | ✓ |
| `evidence/SUMMARY.md` | `7061f6c9…ac95` | `7061f6c91f8a2e689284d3f6d4d16893375f06833a5fc0b9db92596034b6ac95` | ✓ |
| `evidence/final_deliverable_hashes.json` | (self) | `a75bed1d78f9e3f8081ca5b02e724f2a7bb846f4c383067e80d6ced63ece7d32` | ✓ read |
| `iso/prompt_injection_guard.py` | `d7125478…df0d` | `d71254782c10cd6d58c768eeb50e220de5e3d8047709e26f0604b5c59e67df0d` (14514 B) | ✓ |
| `iso/prompt_injection.py` | `88154de4…0f33` | `88154de4ab7630606c2545cdcdf9c3ac44faf32bcae0f83f33a1cebc6d490f33` (20100 B) | ✓ |
| `iso/readiness_graph.py` | `50c94de2…c97b` | `50c94de28f328d125bd4834b2cda8a46794cba5f5f3f01c5415b4060b2d8c97b` (7036 B) | ✓ |

`changes.diff` hunk count (my `^@@` scan per section): guard **9** + pi
**6** + readiness **3** = 18, matching the claimed 9+6+3, each section keyed
to the correct before pin (`f900a13d…` / `7b22f239…` / `3f4c43b0…`).

**Oracle frozen-first (disk CreationTime)**: `oracle.md` created
00:00:12.419, `oracle_freeze.json` 00:00:13.871 (`frozen_at_utc`
2026-09-22T23:00:13.766Z, host clock = UTC+1). The pre-freeze files in the attempt
created BEFORE the freeze are the 3 `before/` copies and the 5 `sources/`
copies (all at 23:59:38, read-only copy-out) — domain: the 8 copy-out files. First composition write
(`iso/prompt_injection_guard.py`) = 00:01:12; first battery artifact =
00:01:30/00:01:37. Disk times therefore satisfy the freeze invariant
「frozen BEFORE any composition run or battery」 (see finding F1 for a
commands.json ordering nit).

Evidence volume: `evidence/raw` holds **39** top-level files (see F2) plus
26 files in the 3 battery subdirectories (`battery_iv_i06b/`,
`battery_v_disposal_mutant/`, `battery_v_disposal_restored/`) = 65 raw files
in the attempt at review time.

## 2. Composition correctness — G1–G14 spot (7) + full merged-vs-source diff

I read the merged guard in full (339 lines) and diffed it against both
sources (`sources/FIX_guard_after.py`, `sources/TTL_guard_after.py`).
Spot seven, per the review order:

- **G5** — `POLICY_RECEIPT_TTL_CAP_SECONDS = 86400 * 30` with the
  §十九/C6/4c comment block: my line-block byte-compare of the 11 lines
  around the constant, TTL source vs merged, = **identical**.
- **G6** — `require_state_domain` body: my extraction-and-compare, FIX vs
  merged = **byte-identical**; both FIX texts present verbatim
  (`state_domain 'X' is missing or illegal — fail closed (ambiguity is never
  defaulted)` / `… record cannot be read as 'Y'`).
- **G7** — `ReviewEvaluation.state_domain` declared with no default (field
  precedes `reason: str = ""`, so omitting it raises TypeError) +
  `__post_init__` domain checks (`ReviewEvaluation state_domain must be
  'cache', got …`) present from the FIX face.
- **G8** — the union point: `__post_init__` extra check
  `cache_state not in CACHE_STATES → raise … is not a legal cache-domain
  state — fail closed`, present in merged (lines 149–155) with the
  I-06-A-strictness comment, helper `state_domain_of` dropped.
- **G9** — `_receipt_from_store`: `receipt.get("state_domain") !=
  STATE_DOMAIN_REVIEW → `None` (line 202) — missing/foreign tag rejected at
  the read boundary.
- **G12** — `evaluate_review` validation block: my byte-compare, TTL source
  vs merged = **identical**, order `source_sha256 → policy_hash → ttl<0 →
  >cap` raise literal `ttl_seconds exceeds policy cap of 2592000s` →
  `math.isfinite` — all five validation checks (domain: evaluate_review body) precede `_receipt_from_store`.
- **G11** (bonus of the read) — `_freshness` `now_seconds < reviewed_at`
  branch returns `not_reviewed/tampered` with reason
  domain: verbatim guard reason — `receipt reviewed_at is after now (clock anomaly; now may only tighten
  freshness)`; the TTL docstring is byte-present in merged.

Full merged-vs-FIX unified diff = exactly 8 hunks, each traceable: TTL
docstring policy block (G1), `import math` (G3), constant+comment (G5),
cache_state union check (G8), `_freshness` docstring + clock branch (G11),
`evaluate_review` docstring + cap/isfinite validation (G12), `__all__`
additions `POLICY_RECEIPT_TTL_CAP_SECONDS` + `STATE_DOMAINS` (G14).
Everything else in the merged guard is the FIX face (G2/G4/G6/G7/G9/G10/G13).

**DROP list (rule §1-5) — grep counts (N=12 dropped markers) on the merged guard, all 0**:
`import time`(0), `_policy_clock`(0), `effective_receipt_ttl`(0),
`effective_review_instant`(0), `_iso_of`(0),
`RECEIPT_TTL_POLICY_CAP_SECONDS`(0), `min(float(ttl`(0),
`state_domain_of`(0), `REVIEW_STATES`(0), and both CLIP call lines
`ttl_seconds = effective_receipt_ttl` / `now = effective_review_instant`
(0/0).

**Byte-identity**: `iso/prompt_injection.py` == FIX iso
`88154de4…0f33` (re-hashed on BOTH sides this review) ✓;
`iso/readiness_graph.py` == FIX iso `50c94de2…c97b` (re-hashed on BOTH
sides) ✓. **Before == live production**, re-hashed at review START and at
review END: guard `f900a13d…b0c08`, pi `7b22f239…39618`, readiness
`3f4c43b0…85acc` — three-for-three matches, i.e. production zero-write held
across this review too.

## 3. Conflicts C-1..C-7 — raw-first confirmed

- **C-1**: I read `evidence/raw/battery_i_unmodified_conflict.log` —
  genuine traceback of TTL's UNMODIFIED probe crashing at `make_store()` with
  `PromptInjectionReviewError: evidence_payload must be provided` against the
  merged writer (the paired .json is honestly recorded as missing in
  decision.md §2 because rc=1 crashed before emission).
- **C-2**: `battery_i_adapted_probe_r1.json` raw shows
  `gating_failed: ["TTL-G2"]`, 15/16 — matches decision.md §2; the one-line
  seed-tag fix diff is in `battery_i_seed_fixture_adaptation.diff` (I read it:
  exactly 1 hunk adding `"state_domain": "review"` + 2 comment lines).
- **decision.md §3 side-by-side P1–P7**: read; each row names I-06-A form,
  FIX form, union/stricter choice, and its pinning battery.
- **C-4 / rule-4 side battery (decision.md §4)**: raw
  `battery_rule4_i06a_cases_on_merged.json` reports `"passed": 13,
  "failed": 4`; the 4 failures are attributed row-by-row (N6 payload = rules
  §1-3/§1-2 P5-a; N8+N8b = §1-1 spelling + §1-5 CLIP drop; N10 =
  §1-5 minimality + supersession). The 13 passes cover their store /
  processing_demand face, which this ruling does not touch.
- **C-5/C-6/C-7**: read in decision.md §2; C-7 (I-06-A guard drift
  `cf9174b5 → c2af11b3` by its own concurrent fix round) is disclosed in
  `binding.json → sources_read_only[2].drift_observed` with the marker-grep
  equivalence argument.
- **DROP vs rule5**: the binding `dropped[]` list (CLIP lines, effective_*
  helpers, `_policy_clock`, I-06-A cap spelling, `state_domain_of`) is
  grep-verified absent from the merged guard per §2 above — the DROP list
  matches rule 5 one-for-one.

## 4. Batteries — reviewer re-runs + raw verification

| # | my verification | result |
|---|---|---|
| i | raw: `battery_i_green.json` + `battery_i_green_final_confirm.json` — `guard_sha256=d7125478…df0d`, `gating_failed=[]`, 16/16 (both runs) — plus **my own re-run of two frozen cases** (over-cap **N1** and past-now **N5**) in `%TEMP%` against a fresh mirror whose `source_catalog` holds the merged faces | **rc=0**: N1 raised `PromptInjectionGuardError` with message exactly `ttl_seconds exceeds policy cap of 2592000s`; N5 returned `not_reviewed`/`tampered` with reason exactly `receipt reviewed_at is after now (clock anomaly; now may only tighten freshness)`; loaded guard sha == `d7125478…df0d` (full output in `%TEMP%\rvrev-gm\case_recheck_out.json`) |
| ii | raw-verified only: `battery_ii_rf_product_tests.txt` | `14 passed in 4.17s` ✓ (not re-run by reviewer — domain: battery ii raw) |
| iii | raw `battery_iii_state_domain_four_negatives.txt` = N1–N4 PASS, `C7 SCENARIOS: PASS`, **plus my own re-run** of FIX's `s_c7_state_domain.py --pkg-dir <my %TEMP% pkg copy>` (python `-B`, output to `%TEMP%`) | **rc=0, all four PASS**, incl. the missing-state negative N3: receipt read without `state_domain` → `None` (never trusted), `ReviewEvaluation` without `state_domain` → `TypeError`; pkg hashes echoed by the script = merged faces (domain: battery iii re-run) |
| iv | raw `battery_iv_i06b/summary.json` + `run_log.txt` + `H2.json` + `L3.json` | `green:16, red:2, total:18`; the 2 RED are exactly **H2** (checks `H2a`+`H2b`, gap-validator surface noted as outside FIX scope) and **L3**; within L3 only `L3b_pin_test_pins_frozen_sentence` failed while `L3a_pin_test_exists` = ok (pin test exists) — the claimed L3b-only residual, L3a-passes form ✓ (not re-run by reviewer) (domain: battery iv raw set) |
| v | raw `battery_v_mutations_summary.json` + `battery_v_disposal_summary.json`; spot TWO per order | **spot 1 — disposal gate → case J**: mutant pi `if status == "detected_and_ignored"` disabled → verdict FAIL with `J1_disposal_gate_rejects` + `J2_zero_product_semantic_rows` red; restore byte-identical (`restored_pi_sha256 == merged == 88154de4…`) and `restored_verdict: PASS` (restore-then-green ✓). **spot 2 — past-now → N5/N6**: v2 observed red `[TTL-N5, TTL-N6]` == expect; `_restored.mirror_guard_sha256 == merged == d7125478…`, `restored_byte_identical: true`, `confirm_green_gating_passed: 16` (restore-then-green ✓), corroborated by `battery_v_probe_confirm_green.json` (16/16, `d7125478…`) |

Five mutation groups for the record (raw): v1 cap-only `[G1,N1,N2,N3]`,
v1b cap+isfinite `[G1,N1,N2,N3,N8,N9]` (TTL MUT-1 exact), v2 past-now
`[N5,N6]`, v3 isfinite `[N8]`, disposal→J — each `ok: true` with
byte-identical restores. NaN coverage per oracle §4-v: `TTL-N8` exists and
v3 turns exactly it red (raw confirmed) — no new case was needed.

## 5. RED/GREEN status quo — read `red_green_status_quo.json`

4/4 RED confirmed on the before faces with observed values (R1 over-cap
accepted → `cache_state: hit`; R2 `detected_and_ignored` written with no
tuple/trust root/signature; R3 unbound write accepted; R4 past-now → `hit`),
and 4/4 GREEN on the merged faces with the exact literals
(`ttl_seconds exceeds policy cap of 2592000s`;
`PromptInjectionReviewError: disposal authorization unavailable: ignore_reason`;
`source_sha256 must be a lowercase SHA-256`;
domain: GREEN literal #4 — `receipt reviewed_at is after now (clock anomaly; now may only tighten
freshness)`); `summary.red_all_four_confirmed=true`,
`green_all_four_ok=true`. My own re-runs independently re-proved R1 and R4
(§4 row i); R2/R3 are raw-verified in this file (see §7 unverified).

## 6. Test-edit debt — measured numbers re-verified by the reviewer

Per order, both CW test files were run ONCE each in a fresh `%TEMP%` mirror
(prod `src` copy + merged 3 faces overlaid, prod conftest/tests copied,
`PYTHONIOENCODING=utf-8`, `-p no:cacheprovider`; RF/CW trees unwritten):

- **Run 1 (production/unadapted seed, both files, merged faces)**:
  `15 failed, 11 passed` — decomposed exactly as claimed:
  - `test_readiness_graph.py`: **4 failed / 5 passed**, and the 4 failing
    names are byte-for-byte the same four as the card's
    `informational_cw_readinessgraph_unadapted_seed.txt`
    (`test_ready_source_all_stages`, `test_safety_guard_drives_graph`,
    `test_safety_tampered_blocks_with_action`,
    `test_safety_ignored_blocks_with_action`) → confirms
    「needs the 1-line seed tag (4 fail without)」.
  - `test_prompt_injection_guard.py`: **11 failed / 6 passed**, and the 11
    failing names are byte-for-byte the same eleven as the card's
    `informational_cw_unit_tests_on_merged.txt` → confirms the 11-fail side
    of the claim (causes: `evidence_payload` P5-a, `ReviewEvaluation`
    `state_domain` C7, and the P5-c-mandatory legacy no-binding expectation
    `test_record_without_binding_keeps_legacy_shape`).
- **Run 2 (the same mirror with ONLY the 1-line seed tag applied — domain: mirror-local patch)**:
  `11 failed, 15 passed` → confirms the claimed combined
  「11 fail / 15 pass」 (decision.md §5) exactly.

`handoff.json → unproven[1]` records the debt with these same numbers and
the debt is NOT fixed in this attempt (the two production test files were
opened READ-ONLY for measurement; my patch landed only in `%TEMP%` (domain: the 2 product test files) in the
mirror).

**CW porcelain spot** (read-only `git status --porcelain` + `git log`):
exactly 3 modified files — `CLAUDE.md`, `README.md`,
`src/company_wiki/source_catalog/artifact_dag.py` — all three dirt rows (domain: `git status --porcelain` listing) show LastWriteTime
2026-09-22 22:23:23 (pre-existing dirt from before this attempt's 23:59:38
start); the 3 dirty paths are outside this card's scope (domain: GUARD-MERGE target scope); none of the 3 target
files (`prompt_injection_guard.py` / `prompt_injection.py` /
`readiness_graph.py`) appears dirty. HEAD = `ac4ebd0` (register §45 push) —
no GUARD-MERGE commit exists yet (domain: `git log -6` HEAD=`ac4ebd0`), consistent with §48 item 5 (commit only
after review). The review boundary 「no git」 was honoured as 「no git
state-changing verbs」; the two read-only inspection commands above were run
because the review order explicitly requested the porcelain spot.

## 7. Boundaries, source pins, re-run condition

- **Production zero-write**: the three CW live files hash to the before pins
  at review end (§2) — `f900a13d…` / `7b22f239…` / `3f4c43b0…`.
  `commands.json` scanned: 0 git verbs; `changes.diff` = difflib (its header
  sections are repo-relative, no git metadata). No file inside the attempt
  was modified after card close (00:21:11) before this report was written.
- **Sources read-only**: sibling pins re-hashed live this review —
  FIX iso guard `17f0dc58…ed31b`, pi `88154de4…0f33`, rdg `50c94de2…c97b`,
  TTL iso guard `142ae848…d7dd` — all (N=4) re-hashed sibling pins equal the card's start/close pins, so
  the card's source pins match the FINAL isos it merged from.
- **Re-run condition note**: `handoff.unproven[0]` stands — a re-run of
  batteries (i)–(v) is required if FIX or I-06-A land further changes to
  `prompt_injection*` / `readiness_graph*`. Since the card wrote that note,
  FIX's review has landed (`FIX-W06-GAPS handoff.status = accepted_scoped`)
  and I-06-A round-2 has landed (its `binding.json` now pins
  `c2af11b3…`, 1 occurrence, `cf9174b5` 0 occurrences) — but the FINAL FIX
  isos still hash to `17f0dc58`/`88154de4`/`50c94de2` (re-hashed above), so
  the re-run trigger did NOT fire for the three faces this card merged.
  The I-06-A guard drift `cf9174b5 → c2af11b3` is disclosed as **C-7** and
  irrelevant to the composed result (its guard face is SUPERSEDED — domain: ruling §1-5 — only its
  store/processing_demand face remains its own).
- **Reviewer-side writes**: `%TEMP%\rvrev-gm` (mirror, pkg copy, run
  outputs, patched test file) + these two report files — nothing else.

## 8. Findings and conditions

**Verdict: ACCEPT**, subject to these conditions (state for the parent):

1. **Commit scope = the 3 merged files BUNDLED with the measured test-edit
   debt fixes, via a separate small pass before the commit.** The debt fixes
   are exactly the two measured items: (a)
   `tests/unit/test_readiness_graph.py::_seed` — add the 1-line
   `"state_domain": "review"` receipt tag (my Run 1→2 proves it flips the 4
   readiness failures to green); (b)
   `tests/unit/test_prompt_injection_guard.py` — pass `evidence_payload` to
   every `record_prompt_injection_review` call (domain: call sites in that test file), construct
   `ReviewEvaluation(..., state_domain="cache")`, and drop/replace the
   legacy no-binding expectation (P5-c makes it invalid by design). The
   single CW commit lands only after that pass — domain: §48 item 5 sequencing.
2. `handoff.unproven[0]` (re-run batteries (i)–(v) if either sibling lands
   further changes to the three faces) stands as written.
3. The store UNRATIFIED note stands (domain: scope = 3 composed faces): this report ratifies only this card's three
   composed faces; the I-06-A store/processing_demand face and the
   `candidate-unratified-I-06-A-a20260919-01` marker rows are untouched and
   remain unratified here.
4. The parent performs the commit (§48 item 5); this review executed zero
   state-changing git verbs and did not edit `handoff.json` (it stays
   `review_pending`/unsigned as the card left it — this report + sidecar are
   the review authority, per the FIX/TTL carrier pattern).

**Findings (minor, none blocking — domain: this review's finding list):**

- **F1 (doc nit)**: `commands.json` states 「run_utc sequence in order」 and
  lists C2 (write oracle) before C3 (scaffold + copy faces), but disk
  CreationTimes show the C3 copy-out at 23:59:38, i.e. ~34 s BEFORE the
  oracle freeze at 00:00:12. The freeze invariant itself holds (copy-out is
  not a composition run or battery; nothing runnable existed before the
  freeze), so this is a step-ordering bookkeeping mismatch only (domain: commands.json step labels).
- **F2 (count nit)**: `evidence/raw` top-level count is **39** files at
  review time, not 38 — `battery_i_green_final_confirm.json` (00:21:11) was
  written after `SUMMARY.md` (00:20:57), which likely explains the sampled
  38.
- **F3 (disclosed-by-design)**: the merged G2 docstring is annotated
  (「GUARD-MERGE ruling §1-2」, `COPIES ONLY` dropped) and therefore not
  byte-identical to FIX's docstring wording; decision.md G2 row records this
  hunk, and no semantic text changed.
- **F4 (scope note)**: RED/GREEN R2/R3 greens are raw-verified, not
  reviewer-re-executed (the reviewer re-executed R1/R4 via N1/N5 and the C7
  battery; R2's negative path also re-proved indirectly by the disposal
  mutation raw).

**Unverified / residual (carried from card + this review):**

- Batteries (ii), (iv), and the four mutation groups other than the two
  spots were NOT re-executed by the reviewer — verified against raw only (domain: §4 battery rows ii/iv/v).
- P5-b disposal positive path with a REAL trust root + Ed25519 signature:
  not exercised beyond J's fail-closed arm (card `unproven[3]`).
- Pre-C7 production receipts (no `state_domain`) read as `absent` — no rows
  checked this review (card `unproven[2]`; shadow-only surface).
- RULESET/policy_hash numeric coverage of the cap constant (card `unmapped`
  U-2, TTL card scope); I-06-B case K + OPEN-5 C4 (own cards).
- Single-platform (Windows CPython 3.13.9), single-runner evidence only (domain: this attempt's evidence base).

---
Signed: independent reviewer (GUARD-MERGE a20260922-01), verdict
**ACCEPT (scope-limited, conditions §8.1–§8.4)**. Sidecar:
`reviewer_report.sha256`.
