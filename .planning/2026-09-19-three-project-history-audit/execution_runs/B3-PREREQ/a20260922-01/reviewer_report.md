# B3-PREREQ (a20260922-01) — Independent Reviewer Report

**Verdict: `accepted_scoped`** — with one non-blocking wording finding (F-1).

Reviewer: independent, parent-dispatched (not the implementer). Date: 2026-09-22.
The attempt does not self-sign: `handoff.json` `status=review_pending`, `self_signed=false` (read ✓).
This report + its `.sha256` sidecar are the only files this review authored.

---

## 0. Review method (sample re-runs only, per brief)

Read in full: `handoff.json`, `decision.md` (D0 premise table, D1–D4), `oracle.md` + `oracle.sha256`,
`changes.diff` (3 diffs), `commands.json`, `binding.json`, all 21 evidence-manifest files, and the
headers of B3's findings in `reviewer_report.md` (RF-1 §5 line 315, RF-5 §5 line 395, CF-1 §4 line 267).

Independently executed by this reviewer (cheap checks + exactly one property test):

1. guard-order property test, RED on B3 baseline + GREEN on the fixed conftest (the one property re-run);
2. hash comparisons: `b3_reference/iso` vs B3's delivered `iso`, `iso/fixed2` vs `iso/fixed`, all 5 production pins, attempt/baseline conftest, fixed2 SP, oracle, both handoff versions;
3. REM-49 zero-delta: line-level byte diff + `ast.dump` + `compile()` on both SP copies;
4. REM-48 census: JSON parse of `after/integrity.json`, regex counts of `NOT_REHASHED` / `compares every frozen hash`, re-hash of the I-05-C oracle, `git status` (repo-wide + pathscoped), git commit-ancestry check of the `8b7229c3` citation;
5. FC-904 junit XML parse of both evidence files + read of `test_fc904_artifact_selection.py:379`;
6. `SHA256SUMS.txt` manifest re-verification after my re-run (21/21 ok, 0 mismatch).

Not executed (see §6 Unverified): mutations, FC-904 suite, final 11-test suite, W05B/W05C suites.

---

## 1. Claim 1 — REM-47 / RF-1 FIXED ✓

**(a) Single prefix assignment + origin check.** `changes.diff` diff 1 and the live `iso/conftest.py` show the
path order applied as one operation `sys.path[:0] = list(PATH_ORDER)` (per-entry `insert(0)` loop removed), and
`pytest_collection` now computes `expected = _expected_origin()` and raises unless
`find_spec_origin == expected` plus, in fixed mode, `sys.path[0] == PATH_ORDER[0]` — i.e. it checks what the
docstring claims, per mode (`B3_BYTES=fixed|production`).

**(b) Provenance refuses last-writer-wins.** `record_module_provenance()`: a later write with a different
sha256 sets `conflict=true`, `kept = dict(old)` (the FIRST write stays the reported value), `kept["writes"]`
retains the full ordered history of both writes; earlier modules are never dropped.

**My own property re-run (guard-order test, both halves):**

| target | command | result |
|---|---|---|
| B3 baseline conftest | `B3P_GUARD_CONFTEST=b3_reference/iso/conftest.py … pytest tests/test_rem47_guard_order.py` | **rc=1, 2 failed / 2 passed** — P2 fails (sys.path head = `[CW/src, RF/scripts, …]`, production first, inverted) and P3 fails (`find_spec` origin = production `scripts/company_wiki_source.py`); P0/P1 pass |
| this attempt's conftest | `… pytest tests/test_rem47_guard_order.py` (default target) | **rc=0, 4 passed** |

RED-on-B3-baseline / GREEN-on-fixed confirmed by my own execution. The provenance half was verified by code
reading + MUT-2 evidence (§4), not re-run — the brief budgeted one property re-run, spent on the guard test.

**C2 non-claim present in all three required carriers:**

- `iso/conftest.py` module docstring lines 36–38: "It is **NOT** the REM-12 prevention mechanism and must never be presented as 'the mechanism that prevents REM-12 recurring'" (+ history note at lines 84–85);
- `decision.md` D1 (lines 49–53): "this fixed guard is a runtime binding check … It is **NOT** the REM-12 prevention mechanism …";
- `handoff.json` line 19 (findings part 3): "explicit non-claim (reviewer condition C2) … is NOT a REM-12 prevention mechanism".

---

## 2. Claim 2 — REM-48 / RF-5 FIXED with premise correction ✓

**Premise correction verified by my own greps of B3's attempt:**

- `decision.md`: **0** occurrences of `compares every frozen hash`, and **0** of `NOT_REHASHED` — the sub-premise "B3's decision.md says every hash compared" is indeed not present;
- the claim exists only as quoted in B3's `reviewer_report.md:397`, referring to `handoff.json:188` — the exact string is preserved verbatim in the superseded copy (`evidence/rem48_superseded/handoff.json.pre-correction`, line shown in `changes.diff` diff 3);
- corrected `handoff.json` now parses as valid JSON and contains **0** occurrences of the false phrase.

**Flag census recounted by me:** `after/integrity.json` parses; `expected_frozen` has exactly **4** keys;
exactly **1** `NOT_REHASHED` occurrence, at line 23, key `I-05-C:oracle.md`; the other 3 `expected_frozen`
values equal their `frozen_attempts` counterparts (`A3DD418F…`, `F9845F17…`, `A55602E5…`) ⇒ 3
compared-and-matched-from-records + 1 never-re-hashed. The flag was **not deleted** (post-correction count
still 1, and the corrected sentence quotes it).

**Superseded retention hashes independently recomputed by me:**

- pre-copy `evidence/rem48_superseded/handoff.json.pre-correction` = `CEE4B0DD157A6ED2F322C40258534414C0C64187D3F2C3E9EA3F3DFF7DEC171D` ✓ (matches claim);
- current B3 `handoff.json` = `E33D82A9E418A7CDFE04FE17CE435FF2F48EA06C27CAF096A9AB590C4683A493` ✓ (matches claim); `changes.diff` diff 3 shows exactly line 188 changed.

**Cited independent re-hash re-derived by me (closes handoff gap 3):** `I-05-C/a20260919-01/oracle.md` =
`E4004563B8BBC403D7C8E3856A5FCB95AC3107E57FE891D7B848C5E9834CB34B` ✓, file git-clean ✓, and
`git diff 8b7229c3 HEAD -- <that path>` is empty (content already equal at `8b7229c3`) ✓ — the corrected
sentence's "matching, git-clean since 8b7229c3" is supported by the repository, not just cited.

**Only out-of-attempt write:** `git status` scoped to `execution_runs/B3-I05C-delivery-fixes/` shows exactly
one ` M …/a20260921-01/handoff.json` ✓ — but see F-1 for the repo-wide wording caveat.

---

## 3. Claim 3 — REM-49 / CF-1 FIXED ✓

- **Wording**: `iso/fixed2/rf_scripts/source_preparation.py:138` reads
  `# requested missing roles + their non-reusable ancestors (never a blind full recompute).` — the reviewer's
  suggested wording (CF-1, report §4) verbatim as the operative phrase.
- **Zero-behaviour-delta chain, my own runs:**
  - byte diff: both files 231 lines, **exactly 1 differing line pair (line 138), both sides `#` comments** → comment-only ✓;
  - `ast.dump(ast.parse(base)) == ast.dump(ast.parse(fixed2))` → **True** ✓;
  - `compile()` on both sources (built-in, no `.pyc` written) → **OK** ✓.
- **FC-904 parity (not re-run; spot-verified as instructed):**
  - `evidence/rem49_fc904_parity.json`: 16 nodes per side, identical node→status maps, 15 passed / 1 failed both
    sides, `per_node_identical=true`, sole failure `TestB3ProductionProvenance::test_module_under_test_is_the_bound_copy` on both sides — internally consistent (its own counts match its own maps);
  - both junit XMLs parsed by me: root `pytest`, **16 testcases / 1 failure each**, failing node identical on both sides ✓;
  - the test file's line **379** contains the location-dependent assertion
    `assert "B3-I05C-delivery-fixes" in str(resolved) or _BYTES == "production"`, inside
    `test_module_under_test_is_the_bound_copy` (line 375) ✓ — exactly RF-3's declared P4 assertion, still present, not edited.

---

## 4. Claim 4 — Mutations (3 declared red sets) ✓ by evidence read + independent restore hashes

| mutation | declared | evidence file shows | restore claim |
|---|---|---|---|
| MUT-1 guard-order revert | 2 failed (P2+P3) | `2 failed, 2 passed`, failures are exactly P2 (order inverted) + P3 (production wins) ✓ | pre=post `7437BA9D…` ✓ |
| MUT-2 provenance overwrite | 1 failed (conflict not flagged) | `1 failed, 1 passed`, failure = `conflicting writes were NOT flagged` ✓ | pre=post `7437BA9D…` ✓ |
| MUT-3 old comment restored | 3 failed (C0/C1/C4) | `3 failed, 2 passed`, failures = C0 changed-file, C1 comment-only, C4 wording; C2/C3 pass by construction ✓ | pre=post `91A6DC32…` ✓ |

Restore hashes confirmed against **my own current-file hashes**: attempt `iso/conftest.py` =
`7437BA9D8810BD016602B45710916FA8F83F0926DE265E12AE152558473F057D` ✓, `iso/fixed2/rf_scripts/source_preparation.py` =
`91A6DC32466E9D67B9D034AC345349EE683F6D5FD9486A67CD3ADE009C6EBF4D` ✓ (`evidence/tree_integrity.txt` agrees).
Final suite evidence `final_full_suite_GREEN.txt` = `11 passed`, rc=0 ✓ (read, not re-run).
**0 of 3 mutations were re-executed by me** — the one sample re-run budget was spent on the guard property test.

---

## 5. Claim 5 — Boundaries ✓ (one wording caveat: F-1)

- **`b3_reference/iso` byte-exact vs B3's delivered `iso`:** my independent compare = 21 files vs 21 files, 21 common, **0 hash mismatches, 0 extras in either direction** ✓ ⇒ B3's own `iso/**` was never written after the copy (a post-copy write to either side would surface here).
- **`iso/fixed2` vs `iso/fixed`:** 11 vs 11 files, **differing = 1** (`rf_scripts/source_preparation.py`), 0 extras ✓.
- **Production pins recomputed by me:** RF `scripts/company_wiki_source.py` = `225FECDD…` ✓; RF `tests/test_fc904_artifact_selection.py` = `8C0B8E39…` ✓; CW `src/…/artifact_dag.py` = `0C8B1D6D…` ✓; production `scripts/source_preparation.py` = `37A3EEAE…` **==** `b3_reference` B3-fixed SP `37A3EEAE…` ⇒ REM-49 deliberately NOT landed in production ✓. `git status --porcelain -- scripts tests` in the RF repo → empty ✓.
- **No git writes by this attempt:** all 17 entries in `commands.json` are attempt-scoped edits/copies or read-only `git status`/`git diff --no-index` — no git-write command appears ✓.
- **CW never written this attempt:** CW `git status` shows exactly 3 ` M` (CLAUDE.md, README.md, artifact_dag.py) with mtimes 2026-09-19 / 2026-09-20 — all three pre-date the 2026-09-22 attempt ✓; `artifact_dag.py` still at pin `0C8B1D6D…` ✓.
- **Oracle:** current `sha256(oracle.md)` = `55A89D256DF6AA86C85BBF80BD207CD7C42346421BCFF48D3615E59AA109BC46` = sidecar ✓; the single pre-run amendment (RECORD-DED: REM-49 target pinned to reviewer's verbatim wording) is recorded in-file before the execution log in `commands.json` (SETUP-ORACLE precedes R1) ✓ — freeze *ordering* is attested procedurally, not re-derivable by hashing alone.
- **Attempt conftest pin:** baseline `b3_reference/iso/conftest.py` = `81FED78B…` ✓ (also implied by the 21/21 compare), fixed = `7437BA9D…` ✓.

## Claim 6 — Superseded attempts honesty ✓

`commands.json.superseded_or_aborted_runs` lists **all 4** declared superseded/aborted runs as their own
array, outside the authoritative `commands` array, each with why + observed outcome: R6a and R7a
(junitxml path resolved to `C:\`, PermissionError at sessionfinish → re-run as R6/R7), MUT-1a (encoding
artifact → re-done as MUT-1), MUT-2a (patch-string SyntaxError → re-done as MUT-2). The authoritative
evidence files are separate (`mutation_MUT1/2/3*.txt`, `rem49_fc904_baseline/fixed2.xml`), and the MUT-2
evidence file itself repeats the supersession note. `handoff.json` mutation_summary discloses the two
superseded *mutation* attempts as "NOT the mutation evidence". Labeled correctly; no superseded run is
cited as evidence anywhere I checked.

## F-1 (P4, informational, non-blocking) — the "exactly that one ` M`" sentence is scope-dependent

`handoff.json` (`boundaries_observed.only_out_of_attempt_write`) and `binding.json` (REM-48 delta note) both
phrase the claim as "git status shows exactly that one M". Verified true for `git status` **scoped to
`execution_runs/B3-I05C-delivery-fixes/`** (the scope `production_readonly_check.txt` actually ran, and the
scope in which the single ` M …/a20260921-01/handoff.json` appears). **Repo-wide** `git status --porcelain`
at review time shows **24 ` M` lines total**: the B3 handoff plus 23 others (REMEDIATION_REGISTER.md,
findings.md, progress.md, B1-I08C oracle.md, 8 I-08-C files, 5 I-14-D files, 2 I-14-E files,
M05/M14/M20/M24 oracle.md), all with 2026-09-22 09:59–11:01 mtimes, alongside several untracked concurrent
attempt dirs (B1-PREREQ, E1E7-ERRATA-LANDING, DW15-prune-repair, REM79-MECHANIZATION, …). None of those
paths appears in any of this attempt's 17 `commands.json` entries, and production `scripts/`+`tests/` are
pathscope-clean — so I found no evidence that B3-PREREQ wrote them; the mtimes are equally consistent with
the other cards running concurrently on 2026-09-22. Recommendation to the parent: quote the claim in its
directory-scoped form ("the only ` M` under `B3-I05C-delivery-fixes/`"), not as a repo-wide statement.

---

## 6. Unverified (explicitly out of this review's sample scope)

1. **Mutation re-execution**: 0/3 mutations re-run — verified by evidence-file reading plus independently recomputed restore hashes only.
2. **FC-904 suite**: not re-run — verified via parity-JSON internal consistency, independent junit-XML parsing, and the line-379 source read only.
3. **Final 11-test property suite**: not re-run — `final_full_suite_GREEN.txt` read only (its 21-file manifest verified 21/21 by me).
4. **B3's W05B/W05C vendored suites**: not re-run in the attempt and not re-run here (declared bounded gap; their bindings do not touch this card's changed files).
5. **Attribution of the other 23 repo-dirty tracked files** (F-1): inferred from mtimes + absence of any writing command in `commands.json`, not proven file-by-file.
6. **Oracle freeze ordering**: attested by in-file amendment text + `commands.json` sequencing, not re-derivable by hashing alone.

## 7. Review side effects (disclosed)

- My authorized property-test re-run regenerated attempt-local probe state (`scratch/binding_state.json`, `scratch/module_provenance.json`, `b3_reference/scratch/*`) as an inherent byproduct of loading the conftests under test; **no** evidence file, deliverable, production file, or git index/path was written by this review (`SHA256SUMS.txt` re-verified after the re-run: 21/21 match, 0 mismatch).
- This report + `reviewer_report.md.sha256` are the only files this review authored.

## 8. REM-79 self-check (universals carry same-line domain)

Every count in this report is domain-bound on its own line: "21/21 evidence-manifest entries",
"all 4 `superseded_or_aborted_runs` entries in `commands.json`", "all 24 ` M` lines in repo-wide `git status`",
"all 17 `commands.json` entries", "0 of 3 mutations re-executed", "21 files vs 21 files, 0 hash mismatches
in either direction", "exactly 1 differing line pair (line 138)".

## 9. Scope notes attached to this acceptance

- **REM-47/48/49 register-row closure and B3's promotion (batch 2) are parent/owner calls.** This review accepts the *attempt*; it does not adjudicate register closure and does not authorize promotion.
- **RF-3's location-dependent assertion is still present** in the carrier (`test_fc904:379`) — P4, owned by RF-3, fails identically in any relocated tree, and was correctly not edited here.
- **Vendored W05B/W05C suites were not re-run** in this review (§6.4).
- **REM-49 remains deliberately not landed in production** (prod SP == B3 accepted `37A3EEAE…`); landing it is a separate production change if ever desired.
- F-1 is a wording-precision finding for citation hygiene, not a defect in the REM-48 correction itself.
