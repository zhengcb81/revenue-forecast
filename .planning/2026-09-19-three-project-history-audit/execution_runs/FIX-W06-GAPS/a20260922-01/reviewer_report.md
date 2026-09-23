# reviewer_report.md — independent review of FIX-W06-GAPS / a20260922-01

Card FIX-W06-GAPS · attempt `execution_runs/FIX-W06-GAPS/a20260922-01` · review date 2026-09-22
Reviewer: delegated independent reviewer subagent of session `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`.
Method: read/grep/pwsh exclusively; live re-hashing; sampled re-runs into `%TEMP%` (`%TEMP%\fix-w06-gaps-review\`);
read-only git queries for step 2 (`git --no-optional-locks status --porcelain`, `rev-parse`, `hash-object`, no `-w`,
no index/worktree writes); product repos revenue-forecast + company-wiki READ-ONLY (zero product writes by this
review); outputs of this review = this file + `reviewer_report.sha256` and nothing further. This report signs the
REVIEW solely — `implementer_signed` in the card's own ledger remains false (no self-signing).

## VERDICT — ACCEPT (scoped), with findings F1–F7

Each substantive claim in the 7-step verification brief was re-checked against live bytes or fresh runs.
F1/F2 are ledger-hygiene findings the parent should know before the batch commit; F3/F4/F5 are spec-wording /
placement deviations with working coverage; F6/F7 are disclosure items. No finding overturns the card's
red/green conclusions: the sampled counts re-ran green on the exact iso bytes the binding pins, and the mutation
artifacts are genuinely RED.

## 1. Deliverables ledger — re-hashed live; each pin matches

| artifact | sha256 (live) | brief pin | lines |
|---|---|---|---|
| binding.json | `caa240c57c277128…` | `caa240c5…` | 446 |
| oracle.md | `2ebbf969137c77448…` | `2ebbf969…` | 296 |
| changes.diff | `5eb95a1e7312d6c0…` (1689 lines) | `5eb95a1e…` | 1689 |
| decision.md | `e917230151978e66…` | `e9172301…` | 117 |
| handoff.json | `b06874fef79fc8dd…` | `b06874fe…` | 47 |
| commands.json | `722f4785d431fde8…` | `722f4785…` | 51 |
| recovery/README.md | `e3a784296bc96fb8…` | `e3a78429…` | 33 |

- **Full-ledger re-hash** (the `caa240c5…` ledger, parsed as UTF-8): 62 attempt-internal pins (11 before/ + 10 iso/
  after + 11 scripts/ + 29 evidence/ incl. byte-lengths + the oracle pin) — N=62, mismatches=0, missing=0.
  Product writes live: `tests/test_message_contract_pins.py` = `41da045c…` ✓, `tests/test_fc905b_trusted_receipt.py`
  = `db8bbb48…` ✓ (before `e5c965e5…` recorded in `before/MANIFEST.json` = `0f00c7ba…`, itself matching the ledger).
  `product_source_integrity` 9 paths re-hashed now — changed_count=0 (the `unchanged:true` claims hold).
  Final re-hash after my runs: the 7 deliverables + 2 product tests still show the table values (my runs wrote
  solely into `%TEMP%`).
- **oracle structure**: header `FROZEN before any run`, `frozen: 2026-09-22, before ANY red/green/mutation run`,
  immutability sentence L6, marker L222 `«APPEND sections (dated, additive only) follow below»`, then APPEND A
  (L224), APPEND B (L253), APPEND D (L264), APPEND C body (L288) + `## APPEND C` header (L296) — 4 dated
  sections (2026-09-22), content additive, frozen body L1–222 structurally intact including the original
  evidence-map table (4 columns, L194–195) and the ①–⑦ frozen criteria table (L205–219). See F5 for the
  APPEND C/D ordering blemish; see U1 for the freeze-evidence limitation.
- **changes.diff**: three sections located —
  - L7 `## repo:revenue-forecast [APPLIED (test-only surface, parent-authorized)]`
  - L340 `## repo:company-wiki [PROPOSED ONLY — product source READ-ONLY, not applied]`
  - L986 `## attempt:FIX-W06-GAPS/a20260922-01 [attempt-local copies (fix in COPIES)]`
  header comment L4–5 declares the CW hunks PROPOSED. Matches the brief exactly.
- **handoff.json**: `status=review_pending`, `implementer_signed=false`, `accuracy=unproven`,
  `disclosure_adaptation=unmapped` — the four fields as briefed.
- **recovery/README.md**: exact before-restore recipe (Copy-Item back the tightened test, Remove-Item the new one)
  + hash check `e5c965e5…` against `before/MANIFEST.json` + no-git/no-db-side-effects note (sqlite effects in
  `%TEMP%\fix-w06-gaps\`). Before-copies of the 2 test/product files are byte-identical: git blob of
  `before/rf/test_fc905b…` = `HEAD:tests/test_fc905b…` = `5b29e18f…` ✓.
- **commands.json honest ledger**: argv match each script's argparse (`--module`/`--pkg-dir`/`--out`, `-X utf8 -B`,
  `PYTHONDONTWRITEBYTECODE=1`); RED target=before/, GREEN target=iso/ corroborated by run-recorded hashes
  (`module sha256 : 7bc5feb0…` in RED_* vs `1bbcf9ce…` in GREEN_*); the sole git mention is
  `"git_writes": "none"` (zero git verbs anywhere in the card).

## 2. before/ anchors (spot 6/10) + product-source integrity — re-hashed; each matches

| anchor | live sha256 | pin |
|---|---|---|
| before/candidate/processing_demand_store.py | `7bc5feb0cb5e5022…` | ✓ |
| before/cw/prompt_injection.py | `7b22f23918d5e6b0…` | ✓ |
| before/cw/prompt_injection_guard.py | `f900a13d7c22fe3b…` | ✓ |
| before/cw/processing_demand.py | `90f232edb7804f78…` (= ZR-507 pin) | ✓ |
| before/rf/source_preparation.py | `91a6dc32466e9d67…` | ✓ |
| before/rf/test_fc905b_trusted_receipt.py | `e5c965e5bfea6759…` | ✓ |

**Porcelain + hash-object (read-only), revenue-forecast (HEAD `865428f8`)**: product surface = exactly the 2
claimed test files (`?? tests/test_message_contract_pins.py`, ` M tests/test_fc905b_trusted_receipt.py`);
`git hash-object` vs `HEAD:` blob: `scripts/source_preparation.py`, `scripts/processing_demand.py`,
`scripts/revenue_core.py` each unchanged=True; `tests/test_fc905b` live blob `0b7f5c61…` ≠ HEAD `5b29e18f…`
(= before-copy blob, so before==HEAD proven) and live==iso copy (`0b7f5c61…`); pins file live==iso
(`4e300d05…`). **company-wiki (HEAD `ac4ebd0`)**: porcelain = exactly 3 files (`M CLAUDE.md`, `M README.md`,
`M src/company_wiki/source_catalog/artifact_dag.py`) — these 3 paths are not card files; the 4 card-relevant
source_catalog files each hash-object-equal their HEAD blob (prompt_injection, guard, processing_demand,
readiness_graph: unchanged_vs_HEAD=True). See F7 for the wider plan-space porcelain.

## 3. Counts spot re-run (THREE chosen, plus one gap-closer) — into %TEMP%, GREEN on live iso

- **(a) P1 N-1 upgrade** — `s_p1_migration.py --module iso\candidate\processing_demand_store.py` → rc=0,
  `P1 SCENARIOS (S1..S7): PASS`, `S3_n1_additive_migrate: PASS` with
  `new_columns_added = [attempts, candidate_marker, key_version, lease_owner, lease_until, request_json,
  request_sha256]` = 7 columns (incl. key_version), `new_columns_missing: []`,
  `migrate_1st_rc=0 / migrate_2nd_rc=0` (idempotent), `old_rows_preserved: true`, `old_rows_defaults_ok: true`,
  both old rows present with `attempts=0, lease_owner=null, lease_until=null, key_version='triple-v1'` defaults;
  S4 register rc=0 (new registration writes `key_version='request-identity-v2'`), S5 claim rc=0,
  S6 bypassed-migrator failure = `DemandStoreUnavailable: demand store write failed: … no such column: key_version
  [store_owned=True]` (store-owned type). Run-recorded `module sha256 = 1bbcf9ce…` = binding after-pin ✓.
- **(b) P5-b, no trust root** — `s_p5_receipt.py --pkg-dir iso\pi_pkg` → rc=0, `P5B_disposal_gate: PASS`,
  `P5 SCENARIOS: PASS` (P5A/P5C/P5D PASS too). The literal refusal observed:
  `[P5-b spoofed detected_and_ignored, no tuple, no trust root] -> rc=1 … "disposal authorization unavailable:
  ignore_reason"` — 15 lines carrying the exact `disposal authorization unavailable: ` prefix in the run output.
  Run-recorded pkg hash `prompt_injection.py = 88154de4…` = binding after-pin ✓.
- **(c) P7 c8-variant** — `s_p7_key.py --module iso\candidate\processing_demand_store.py` → rc=0,
  `P7_key_c8c9c10: PASS`, `P7 SCENARIOS: PASS`. c8 (`as_of_date` 2026-09-22 vs 2026-12-31, payload/target equal) →
  `distinct_ids/d distinct_keys=true`, `row_count=2`, row1 `request_sha256=6ae0a321…` and row2
  `request_sha256=3b697d01…` with `request_sha_a_ok/request_sha_b_ok=true` — two rows, each carrying its own
  request hash. c9/c10 likewise 2/2. Legacy arm: `legacy_key_version='triple-v1'`, `merged_silently=false`,
  `rows_after=2`. `module sha256 = 1bbcf9ce…` ✓.
- **(d) extra gap-closer: C7** — because of F2 I also re-ran `s_c7_state_domain.py --pkg-dir iso\pi_pkg` →
  `C7_N1…N4: PASS`, `C7 SCENARIOS: PASS` with `prompt_injection.py = 88154de4…` (dual negatives, missing/illegal
  negatives, `_SAFETY_MAP` unknown ⇒ strictest `unrecognized safety cache_state — fail closed`).

## 4. Mutation table — 12/12 RED confirmed, two artifacts re-read raw, after-hash re-match done

- Verdict lines re-read from each raw artifact: MUTATION_C7/P1/P2B/P3/P4a/P4b/P5a/P5b/P5c/P6A/P6B/P7 —
  N=12 files, each `RED (mutation broke …)`. See F1 for the summary artifact.
- **Raw spot A (P5-b 去处置闸)** `evidence/MUTATION_P5b.txt`: mutation source = `run_mutations.py:184-194`
  (`if status == "detected_and_ignored":` → `if False:`), observed tail `P5B_disposal_gate: FAIL`,
  `P5 SCENARIOS: FAIL` ⇒ RED ✓ (P5A/P5C/P5D stayed PASS — one mutation, one family broken).
- **Raw spot B (P7 去 as_of_date)** `evidence/MUTATION_P7.txt`: mutation source = `run_mutations.py:241-249`
  (`"as_of_date": request.get("as_of_date")` → `"as_of_date": None`, i.e. APPEND D's disjoint-component drop),
  observed tail `P7_key_c8c9c10: FAIL`, `P7 SCENARIOS: FAIL` ⇒ RED ✓ (legacy arm PASS).
- **Restore / after-hash re-match**: there is no in-place mutation to restore — `run_mutations.py:43-52
  mutate_tree()` copies iso/ into `%TEMP%\fix-w06-gaps\mutations\…` and mutates exclusively that scratch copy
  (code-inspected). The equivalent of their after-hash re-match was executed by this review: after the recorded
  runs, the full ledger re-hash shows the 62 attempt-internal pins — incl. the 10 iso/ after-pins (N=62) — still
  matching binding.json (see §1), and RED/GREEN artifacts re-log the before-hash `7bc5feb0…` / after-hash
  `1bbcf9ce…` respectively, except the two stale GREEN files in F2.

## 5. Attribution & append discipline — grep-verified myself

- **decision.md §3 conflict-table item 6** = `execution_runs/T2-SIM-OPEN5-RF/a20260922-01/ruling.md:233-234`.
  I opened that file at :225-246: L233-234 carry the normative consumption bottom line
  «消费只接受有效且绑定完好的审核结论，`tampered/ignored/expired/absent` 一律不可消费» with the self-note
  «（词汇取自 I-06-B 实测 cache_state：`handoff.json:44-57`）» — matches decision.md's quoted text verbatim
  (cache_state sits at the :234 region; citation character = normative contract, not description) ✓.
- **OPEN-6 file = non-carrier**: I opened `T2-SIM-OPEN6-SEC/a20260922-01/ruling.md` :165-269 — the
  `cache_state="ignored"` mentions decision.md lists as descriptive-only are present exactly where claimed
  (:173 C7 condition row, :201 §7.1(5) doubt entry, :218 §7.2#5 re-verification row, :249 记6, :262-263
  归属核验注记 which itself states «末项 ruling.md:233-234 非本裁定文件…本文件…仅四处描述性引用…无逐字钉点») —
  each such mention demands disambiguation, contains zero verbatim pin, and the file's own attribution note
  agrees with decision.md ✓.
- **APPEND D honest disclosure — both texts retained**: APPEND A item 1 still holds the original literal
  `payload_digest: sha256(canonical_json(request))` (full request, L237-238) and APPEND A item 3 still holds the
  drop-as_of_date ⇒ c8-collapse mutation criterion (L246-247); APPEND D (L264-286) records the observed tension
  (`«the full-request digest absorbs every single-field drop»`) and the 3-component disjoint decomposition
  (`request minus {as_of_date, target}`), keeping row-level `request_sha256 = sha256(canonical(FULL request))`.
  Conflict-resolution record present in decision.md §4 «P7 authorities» bullet + handoff scope item 17 ✓ —
  disclosed, not silently rewritten (both frozen texts untouched) ✓.
- **APPEND B disclosed, not silent**: oracle APPEND B (L253-262) states the GREEN-phase discovery verbatim
  («the bare `sqlite3.OperationalError "database is locked"` surfaced at the CALLER-side `connection.commit()`
  (06 Phase A2 reproduced it in GREEN pre-amendment)») and amends the P6-B contract (writer owns the transaction
  end); decision.md §4 «P6-B contract amendment (oracle APPEND B)» repeats it with the measured-escape origin;
  handoff scope line P6-B cites «(APPEND B)». Disclosure chain complete ✓.

## 6. Boundary honesty — each claim located and checked

- **resume/complete = not-defect**: decision.md §4 first bullet (handoff L240「不得假装存在」correct absence;
  construction = I-06-B nine-step card; P3-A/P3-B built instead; structural-absence pinned via P3D +
  face-2 `test_resume_refusal_surface_structurally_absent` — which my face-2 run executed green) ✓.
- **I-06-B snap2 case K double-green corroborates EXPECTED-ABSENT**: `I-06-B/a20260922-02/evidence/green/K.json`
  and `evidence/green_snap1_0b6e723e/K.json` both `verdict: PASS`, checks K1/K2/K3×2/K4 each `ok: true`
  (class/module have no resume/complete; CLI rejects `resume`/`complete` with rc=2; RF entry has no resume
  token) — two snaps, double-green ✓ (also cross-listed in that card's 8-item double-green guard set).
- **store UNRATIFIED + D-W06 freeze signature absent**: recorded in handoff `awaiting[]` («owner/ratification for
  D-W06 frozen contract (store owner, schema/API, key) — candidate remains UNRATIFIED») and decision.md §4
  («D-W06 frozen owner/schema/API signature still absent; candidate marker unchanged»). Corroboration: letter
  `outward_requests/A_DW06_OPEN-4-5-6.md` still shows 待裁 items, drafter explicitly 非签署者, and
  `RESPONSES.md` carries no D-W06 entry ✓.
- **CW hunks PROPOSED, no CW write from this card**: changes.diff L340 header + L4-5 comment mark those hunks
  PROPOSED; CW porcelain = the 3 pre-existing dirty paths + HEAD `ac4ebd0`, with the 4 card files byte-equal to HEAD
  and binding's before/now hashes identical — no new CW modification from this card ✓.
- **zero git (commands verbs)**: commands.json contains no git invocation; sole occurrence is
  `"git_writes": "none"` ✓; recovery README repeats no-git. (This review itself used solely read-only git
  queries per the step-2 instruction — disclosed in the header and U6.)

## 7. Product test face quality — run, pin-style grep, mutation spot-verify

- **Fresh run (product tree, %TEMP% logs)**: `pytest tests/test_message_contract_pins.py
  tests/test_fc905b_trusted_receipt.py -q --no-header -p no:cacheprovider` (python 3.13.9, `-B`,
  `PYTHONDONTWRITEBYTECODE=1`) → **14 passed** (matches `evidence/PRODUCT_tests_run.txt` = `14 passed`).
  Attempt-local faces re-run too: face-1 `iso/candidate/test_candidate_message_pins.py` → **4 passed**;
  face-2 `iso/rf/test_message_contract_pins.py` → **8 passed** (byte-identical to the product file per hash).
  No `__pycache__`/`.pytest_cache` left anywhere in the attempt or product tree.
- **Pin-style grep (exact-match, not loose regex)**: face-2 file — assertions are `==`, set-dict equality
  (`texts == {case: verbatim …}`), full-string AST-constant membership (`BLOCK_SENTENCE in constants` +
  `constants.count(BLOCK_SENTENCE) == 1`), exact `str(excinfo.value) == "…"` for the
  `{field} must be a lowercase SHA-256` family; the single `match=` hit is the module docstring describing the
  replaced loose coverage (no loose assert remains). Face-1 file — 13 `==` asserts, 0 regex-style matches, incl.
  **demand_store_error= / demand_queued clause pins**: `test_demand_store_error_clause_verbatim` and
  `test_demand_queued_clause_verbatim` assert the FULL assembled strings byte-for-byte against frozen fixtures
  (`== EXPECTED_STORE_ERROR_CLAUSE` / `== EXPECTED_DEMAND_QUEUED_CLAUSE`). **3-copy block-sentence
  convergence** lives in face-1 `test_block_sentence_single_source_convergence`: product literal (byte-exact
  implicit-concat fragments in `scripts/source_preparation.py`) == `block_message_base("not_reviewed") ==
  BLOCK_SENTENCE` == `w06a_apply_candidate._ANCHOR_MESSAGE`, `REPLACED in product_source`, plus a
  count==1 anti-duplication assert. Tightened fc905b (live product): L88/L97 now
  `match=re.escape(BLOCK_SENTENCE)` — verbatim pin ✓; see F3 for the sibling that was not tightened.
- **Single-byte mutation ⇒ RED (P4b pattern, scratch copy)**: reviewer script copied
  `scripts/source_preparation.py` + `scripts/processing_demand.py` into `%TEMP%\…\mut_scripts\`, flipped one
  byte (`…blocked` → `…bloqked`) in the scratch copy alone, re-ran the product pins file with
  `GAPS_PIN_RF_SCRIPTS` pointed at the scratch → **1 failed, 7 passed**
  (`test_block_sentence_pinned_verbatim: AssertionError: the full blocked sentence drifted…`), rc=1 —
  mutation visible; product tree untouched (rc recorded in `%TEMP%\fix-w06-gaps-review\mutate_and_run.py` log).

## Findings (numbered)

- **F1 (ledger hygiene, medium)** — `evidence/MUTATION_summary.txt` is 48 bytes containing
  `{"P4a": "RED (mutation broke the pins)"}`: a later `run_mutations.py --only P4a` invocation overwrote the
  rollup, so the summary artifact does NOT summarize the 12-family run that commands.json describes. The
  substantive 12/12 claim survives on the 12 individual artifacts (each re-read, each RED), and binding.json
  faithfully pins the narrowed file (hash `195e694c…`, 48 B) — so the ledger is internally consistent while the
  summary misstates coverage. Suggested fix at parent: re-run the full mutation sweep once (or rename the rollup
  artifact), no product impact.
- **F2 (evidence freshness, medium)** — `GREEN_P5_receipt.txt:3` and `GREEN_C7_state_domain.txt:3` record
  `prompt_injection.py sha256=5fabc1e7eceb1ba3…`, a value matching neither the before-pin (`7b22f239…`) nor the
  binding's final iso-pin (`88154de4ab763060…`), while `GREEN_P6_concurrent.txt:3` records `88154de4…` ✓.
  2 of the 6 GREEN artifacts therefore attest an intermediate iso state (the file was edited after those runs
  were captured and the artifacts were not regenerated), so the card's run-recorded after-hash re-match fails
  for exactly these two files. Mitigation executed by this review: fresh P5 (step 3b) and C7 (extra) re-runs
  against the live iso each PASS with `88154de4…`, so the substantive P5/C7 GREEN claims hold on the exact bytes
  binding pins; the on-disk artifacts alone are stale.
- **F3 (oracle-wording deviation, low–medium)** — oracle P4-SCOPE replaces «the loose regex `not reviewed|blocked`
  … (and the sibling loose `parser|llm|counts` match, same defect class)», but the delivered/tightened
  `tests/test_fc905b_trusted_receipt.py` keeps the loose sibling at L123 and L125
  (`match="parser|llm|counts"`); the block-sentence pair alone was replaced (L88/L97, `re.escape`). Coverage is
  nonetheless non-vacuous: face-2 `test_counts_sentence_pinned_verbatim` pins the full counts sentence as an
  AST constant (one-byte drift ⇒ RED), so the defect class the parenthetical targeted is covered — by the pins
  file rather than by the fc905b replacement the oracle promised.
- **F4 (face-assignment deviation, low–medium)** — oracle Face-2 assigns «the three-copy convergence for item 14»
  to the shipped product file `tests/test_message_contract_pins.py`; the delivered product file pins solely the
  product-side literal (membership + count==1). The actual 3-copy convergence test
  (`test_block_sentence_single_source_convergence`, product literal == candidate constant == apply anchor) sits
  in attempt-local face-1, which is green 4/4 in my run but is NOT part of the product-tree test face the parent
  is about to commit. Net: the pins set covers everything exactly once (clause pins in face-1 per oracle Face-1
  ✓), yet the committed product tests alone cannot detect drift between the product literal and the candidate
  copies. Parent decision needed whether to ship face-1's convergence test alongside (it is absolute-path
  tolerant and ran green from both locations).
- **F5 (append ordering blemish, low)** — in oracle.md, APPEND D (L264) precedes APPEND C's body (L288) and the
  `## APPEND C — 2026-09-22 (mutation checklist consolidation)` header is the file's LAST line with no body
  beneath it: the four dated sections are present and additive, but C's header/body are mis-ordered (header
  dangles at EOF). No frozen text was touched (frozen body L1–222 intact; original table columns unchanged).
- **F6 (missing raw artifacts, low)** — commands.json's `pins` phase lists the face-1 and face-2 pytest runs, but
  evidence/ keeps just `PRODUCT_tests_run.txt` (the product run); no raw stdout artifact exists for the two
  attempt-local pin-face runs. Reproduced by this review: face-1 4 passed, face-2 8 passed (logs in %TEMP%).
- **F7 (porcelain disclosure, low)** — the brief's shorthand `«only the two RF test files differ from HEAD»` is
  true FOR THE PRODUCT SURFACE (`scripts/` clean; `tests/` = the 2 files), but the whole-repo porcelain also
  shows 9 modified plan-space files (`REMEDIATION_REGISTER.md`, `progress.md`, `outward_requests/*`,
  `execution_v2/START_HERE.md`, and notably
  `execution_runs/T2-SIM-OPEN6-SEC/a20260922-01/ruling.md` whose C-续 text cross-references this card's
  decision.md conflict table), untracked plan dirs (incl. this attempt), `.tmp-r41-mutation/`, and
  `assurance/unified_completion/manifests/plan_inputs.json.bak`. The card's ledgers do not claim those writes
  (declared write set = attempt dir + the 2 test files), and the parent REMEDIATION_REGISTER L1109 separately
  adjudicates the two test-file writes as this card's authorized face — attribution of the plan-space dirt
  (likely orchestration C8 registration / other rounds) stays unresolved from disk state alone.

## Unverified / limitations

- **U1** — no freeze-time hash of oracle.md's pre-append body exists anywhere I could locate (the binding pins
  just the final full-ledger hash), and plan-level `progress.md:40` already rules «`oracle.md` 文本不作「事前
  冻结证据」». Append-not-rewrite is therefore verified STRUCTURALLY (frozen header + marker + 4 dated additive
  sections + intact frozen tables), not cryptographically against a pre-append pin.
- **U2** — temporal pre-existence of CW's dirty-3 and of the plan-space modifications (F7): paths are unrelated
  to this card and card-relevant files are byte-equal to HEAD, but disk state cannot prove WHEN those edits
  landed.
- **U3** — the intermediate iso bytes behind `5fabc1e7…` (F2) are not retained anywhere findable; the exact edit
  and its timing between the P5/C7 GREEN capture and the final `88154de4…` pin are not reconstructable from the
  ledger.
- **U4** — re-run sampling: this review freshly re-ran P1, P5, P7 (required) + C7 (gap-closer). P2-B, P3-A/B,
  P6-A/B RED/GREEN conclusions rest on their hash-pinned artifacts + RED/GREEN pairs + mutation artifacts, which
  I verified by hash and content but did not re-execute.
- **U5** — there is no explicit per-mutation «restore» record in the card (by design: mutations never leave
  `%TEMP%`); the after-hash re-match was verified via code inspection + full-ledger re-hash instead (§1, §4),
  with F2 as the 1 documented exception.
- **U6** — git usage by this review was limited to read-only queries (`status --porcelain` with
  `--no-optional-locks`, `rev-parse`, `hash-object`; no `-w`, no checkout/stash/commit) executed for step 2 as
  the brief instructed; the brief's «no git» boundary was read as «no git writes». Two permission-denied scratch
  dirs (`reviews/*/scratch/*`, `.tmp-zr408-*`) were unreadable during porcelain — pre-existing, outside this
  card's surface.
- **U7** — external-domain items were checked solely for honest recording, not for substance: letter B identity
  chain, OPEN-6 C1/C2 implementation carrier, D-W06 freeze signature, P6-A single-slot queueing ratification,
  clip-vs-REJECT unification (owed at parent while I-06-A and TTL cards are in review).
- **U8** — REM-79 mechanized check was applied to this reviewer report (result below), not to the card's own
  prose files.

## REM-79 self-check

Tool: `execution_runs/REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py`
(version `1.2.0-correction2`, stdlib-only, never writes). Command:
`python -X utf8 -B tools/check_domain_assertions.py <this file>` → **exit 0 — `0 violation(s) across 1 file(s)`** (final run 2026-09-22; earlier drafts were revised until clean).

## Acceptance scope (as ruled by the parent)

Accepting FIX-W06-GAPS/a20260922-01 under exactly this scope:
1. **RF test-face commit = parent (batch)**: the two `revenue-forecast/tests/` files
   (`test_message_contract_pins.py` NEW `41da045c…`, tightened `test_fc905b_trusted_receipt.py` `db8bbb48…`)
   commit in the parent batch card; nothing else in either repo is written by this card.
2. **CW hunks stay PROPOSED** until CW-side application is authorized and recorded in a separate card.
3. **Store stays UNRATIFIED** until the D-W06 freeze signature exists (store owner, schema/API, key).
4. **Residual faces** = letter B (identity chain) + OPEN-6 C1/C2 implementation carrier (P5-a residual forgery
   face and full P5-b identity closure ride these, per decision.md §4).
5. **P6-A single-slot queueing semantics** = ruling-track open (ack-or-defined-reject + audit trail are in;
   queue/merge slot semantics await ratification).
6. **clip-vs-REJECT unification** is owed at the parent (I-06-A + TTL cards both in review).
7. Findings F1–F2 should be repaired in a bookkeeping pass (regenerate the mutation rollup; regenerate or
   annotate the two stale GREEN artifacts); F3–F7 are disclosed deviations for the parent's judgment and do not
   block this acceptance.

## Reviewer sign-off

ACCEPT (scoped), findings F1–F7 above. — independent reviewer subagent of session
`session-bfecd191-fbc3-4a66-8ed1-6562479bf102`, 2026-09-22. `implementer_signed=false` in the card ledger
stands; this signature attests the review alone.
