# B3-PREREQ — a20260922-01 — ORACLE (frozen BEFORE any run)

- Card: **B3-PREREQ** — close the three promotion-prerequisite findings **REM-47 / REM-48 / REM-49**
  raised by B3's ACCEPT review, so B3's iso fix can later be promoted as batch 2.
- This file is frozen before any test execution, mutation run, or suite run in this attempt.
  Everything below was derived by *reading* only (report text, source files, record files).
- Input (read-only): `.planning/2026-09-19-three-project-history-audit/execution_runs/B3-I05C-delivery-fixes/a20260921-01`
  (`reviewer_report.md`, delivered bytes `iso/fixed/**`, `iso/conftest.py`, `handoff.json`,
  `decision.md`, `after/integrity.json`, `scratch/module_provenance.json`).
- Source of the findings: `REMEDIATION_REGISTER.md` rows REM-47/48/49 (lines 116-118, 435, 534)
  → mapped by the register itself to B3 review findings **RF-1 / RF-5 / CF-1**.
- Boundaries: production READ-ONLY; no git writes; frozen `before/` untouched; B3's accepted
  `iso/fixed/` bytes are INPUT only (copied, never edited in place); no product changes outside
  `iso/`; never self-sign; `disclosure_adaptation=unmapped`; `accuracy=unproven`; promotion stays
  a separate owner decision.

---

## 0. Finding verification against B3's reviewer_report.md (done pre-oracle, by reading)

| my id | register id | review finding | verified location | verified content |
|---|---|---|---|---|
| F1 | REM-47 | RF-1 (report §5, line 315) | `iso/conftest.py:36-40`, `:66-84`, `:87-108` + `scratch/module_provenance.json` | (a) prepend loop inserts each entry at index 0 → final order puts **production ahead of the fixed copy**, inverse of the comment at `:32-35`; (b) the collection guard only checks `FIXED_RF in sys.path` + file existence — the computed `find_spec_origin` is recorded but **never checked**; (c) `module_provenance.json` is last-writer-wins: as delivered it records `company_wiki_source = 225FECDD…/19364` = **PRODUCTION bytes** (last conftest-loaded run was the production control CTRL-D), while `handoff.json` cites that file as binding proof. |
| F2 | REM-48 | RF-5 (report §5, line 395) | `handoff.json:188` vs `after/integrity.json:23` | The "compares **every** frozen hash … **all matched**" claim lives in **`handoff.json` (frozen_artifacts_untouched.verification), NOT in `decision.md`** — `decision.md` was grepped and contains no such claim (recorded correction of the brief's premise). The flags: exactly **1** `NOT_REHASHED` occurrence in B3's records (`after/integrity.json:23`, key `I-05-C:oracle.md`) out of **4** `expected_frozen` entries ⇒ 3 compared+matched, 1 never re-hashed by the attempt. Reviewer independently re-hashed it: `E4004563…` matches, git-clean since `8b7229c3`. |
| F3 | REM-49 | CF-1 (report §4, line 267) | `iso/fixed/rf_scripts/source_preparation.py:134-138` | Comment is **doubly wrong**: `producer_events` is neither a downstream "DAG closure" nor "of the non-reusable roles" — it is the ancestor-closure of the **requested** roles. Reviewer: promoting B3 while it stands **reproduces the REM-13 defect class** in the same file pair. Reviewer's suggested wording: `producer_events = requested missing roles + their non-reusable ancestors`. |

---

## 1. The three fixes (what will be built)

**FIX-1a — guard order (REM-47 part 1).** In this attempt's fresh copy of B3's iso tree
(`iso/conftest.py` + `iso/fixed2/`), the path binding must put the fixed copy **first**:
`sys.path[:4] == [FIXED_CW, FIXED_RF, RF/scripts, CW/src]`, assigned as a whole prefix
(not per-entry `insert(0)`), and `importlib.util.find_spec("company_wiki_source").origin`
must resolve to the attempt-local fixed copy. The module comment/docstring must state exactly
what the code does (docstring = reality).

**FIX-1b — provenance conflict refusal (REM-47 part 2).** `scratch/module_provenance.json`
must no longer be last-writer-wins: a second write of **different bytes** for the same module
must be **flagged as a conflict** and **both writes retained** (first write stays the reported
value); identical re-writes are allowed without a conflict flag.

**FIX-1c — explicit non-claim (reviewer condition C2).** The fixed guard must be recorded — in
`decision.md`, `handoff.json`, and the conftest module docstring — as **NOT** a REM-12
prevention mechanism, and must never be presented as "the mechanism that prevents REM-12
recurring".

**FIX-2 — record contradiction (REM-48).** Correct the false "compares every frozen hash …
all matched" wording in B3's `handoff.json:188` to what was actually done, with the counted
truth (4 expected_frozen entries; 3 compared+matched; 1 `NOT_REHASHED` = `I-05-C:oracle.md`,
independently re-hashed by the reviewer as `E4004563…`). `handoff.json` is **not** a frozen
carrier (frozen carriers = `before/**`, `oracle.md`, the I-05-B/I-05-C frozen attempts), so the
correction is done **in place with superseded retention**: the pre-edit file copy + its SHA256 +
the original sentence are retained under `evidence/rem48_superseded/`. The `NOT_REHASHED` flag
itself is **not deleted** (no silent deletion of flags).

**FIX-3 — comment double-error (REM-49).** In `iso/fixed2/rf_scripts/source_preparation.py`
(a copy — B3's accepted bytes stay untouched) correct lines 134-138 **comment-only**, using
the reviewer's suggested semantics: `producer_events = requested missing roles + their
non-reusable ancestors` (reviewer §4 suggested wording verbatim; matches the implementation
docstring at `company_wiki_source.py:174-175`). No behaviour change of any kind.

---

## 2. Expected outcomes — declared BEFORE running

**T1 — guard-order property test** (own fixture; subprocess loads a target conftest; both
production and fixed copies on the path with conflicting bytes):
production `company_wiki_source.py` = `225FECDD…`/19364 vs fixed = `7D1BD8F9…`/20545 (hashes
differ ⇒ genuinely conflicting values; asserted as a precondition).
Assertions, in order:
1. `sys.path[:4] == [FIXED_CW, FIXED_RF, RF/scripts, CW/src]` (the order the conftest's own
   comment claims: "attempt-local fixed sources first … then the production repos");
2. `find_spec("company_wiki_source").origin == FIXED_RF/company_wiki_source.py` (**fixed wins**);
3. the conftest source states the fixed-first claim (so "docstring = reality" is checkable).
Expected: **RED on B3's current guard** (its per-entry insert(0) leaves production at index 0
and `find_spec` origin = production ⇒ assertions 1 and 2 fail), **GREEN on `iso/conftest.py`**.

**T2 — provenance conflict-refusal property test** (own fixture; same harness for both
conftests): call `pytest_sessionfinish` twice in one process with module stubs whose bytes
differ — write 1 = the fixed copy's bytes (`7D1BD8F9…`), write 2 = production bytes
(`225FECDD…`) — then read `scratch/module_provenance.json`.
Assertions:
1. `modules.company_wiki_source.sha256 == 7D1BD8F9…` (the FIRST write is kept — never silently
   replaced by production bytes);
2. top-level `conflict == true`;
3. `writes` retains **both** distinct writes (2 entries, 2 distinct sha256).
Also run the reverse order (production first, fixed second) — same three assertions must hold.
Expected: **RED on B3's current conftest** (plain overwrite ⇒ file holds only the last write, no
`conflict`, no `writes` ⇒ assertions 1-3 all fail), **GREEN on `iso/conftest.py`**.

**T3 — comment fix, zero behaviour delta** (own checks + focused suite):
1. byte diff `iso/fixed2/rf_scripts/source_preparation.py` vs B3's
   `iso/fixed/rf_scripts/source_preparation.py`: **every changed line pair is comment-only**
   (both sides start with `#` after stripping);
2. `ast.dump(ast.parse(...))` **identical** for both files (comments do not enter the AST ⇒
   zero behaviour delta), and `tokenize` streams identical outside COMMENT tokens;
3. `py_compile` succeeds on both;
4. focused test run — the relevant suite for this file is the FC-904 carrier
   (`test_fc904_artifact_selection.py`, which binds and executes the live
   `source_preparation.py`): run it once against the baseline tree (B3 bytes) and once against
   `iso/fixed2/`, and obtain **identical per-node results** (declared acceptable form of
   "unchanged results"). Known pre-existing caveat declared in advance: RF-3's
   location-dependent assertion (`test_fc904_artifact_selection.py:379`,
   `"B3-I05C-delivery-fixes" in str(resolved)`) fails in a relocated tree — it must fail
   **identically in both runs**; that is RF-3 (P4, not in this card), not a REM-49 effect.
Expected: T3 assertions 1-3 GREEN on the fix; **RED once MUT-3 restores the old comment**;
suite results identical baseline vs fixed2.

**MUTATIONS (3, declared now):**
- **MUT-1**: revert the guard order in `iso/conftest.py` to B3's per-entry `insert(0)` loop
  ⇒ **T1 must go RED**.
- **MUT-2**: revert provenance recording in `iso/conftest.py` to plain overwrite
  (last-writer-wins) ⇒ **T2 must go RED**.
- **MUT-3**: restore the original lines 134-138 in `iso/fixed2/rf_scripts/source_preparation.py`
  ⇒ **T3 (comment-corrected assertions) must go RED** (the zero-delta assertions stay green by
  construction — the RED must come from "the comment is corrected").
After each mutation the tree is restored and the suite re-run GREEN; raw stdout of every run is
preserved under `evidence/`.

**REM-48 evidence (not a property test — a record correction):**
- flag census: `NOT_REHASHED` occurrences in B3's records = **1** (`after/integrity.json:23`),
  of 4 `expected_frozen` entries;
- after the fix: corrected sentence present in `handoff.json`, the `NOT_REHASHED` flag still
  present (assert count still 1), superseded original retained under
  `evidence/rem48_superseded/` with the pre-edit SHA256 of `handoff.json`.

---

## 3. Success criteria for the card (per finding)

- **F1 / REM-47**: fixed — T1 RED on B3 baseline → GREEN on the fresh copy; T2 RED on baseline →
  GREEN on the fresh copy; MUT-1/MUT-2 each produce RED; non-claim (C2) explicitly recorded.
- **F2 / REM-48**: fixed — wording corrected to the counted truth, flag retained, superseded
  retention in place; no silent deletion.
- **F3 / REM-49**: fixed — comment-only diff + AST/tokenize/compile parity + FC-904 suite results
  identical before/after; MUT-3 produces RED.

**Not claimed / out of scope**: no product change outside `iso/`; B3's accepted `iso/fixed/`
bytes remain byte-identical (pinned in `binding.json`); promotion decision stays with the owner;
this attempt never signs its own acceptance (`handoff.status = review_pending`).

---

## Pre-run amendment (recorded BEFORE any run was executed)

FIX-3's target comment text is pinned to the reviewer's **verbatim** suggested wording
(`producer_events = requested missing roles + their non-reusable ancestors`, reviewer §4 /
register REM-49), replacing the earlier loose paraphrase "requested roles + their ANCESTOR
closure". Reason: the paraphrase drops "missing" / "non-reusable" and would itself overstate
the implemented rule (`company_wiki_source.py:174-175`, `_production_scope`), which is exactly
the accuracy class REM-49 is about. T3's "comment corrected" assertion asserts this exact
phrase. No run, test, mutation, or suite execution had been executed when this amendment was
written; `oracle.sha256` was recomputed after it.
