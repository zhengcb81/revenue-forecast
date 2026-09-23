# CW-TEST-DEBT — decision record (a20260922-01)

Card **CW-TEST-DEBT**: condition-1 debt pass of the GUARD-MERGE review
(`reviewer_report.md` verdict **ACCEPT 2a26aaae**, §8.1). Scope: fix exactly the
two measured CW unit-test debts so the merged faces' unit suites go green, for
bundling into the upcoming single CW commit together with the 3 merged source
files. **The only product writes authorized here are the 2 unit-test files.**

## 0. Order and oracle proof

| step | fact | evidence |
|---|---|---|
| pins first | live SHA-256 of both write targets, the 3 production sources and the 3 merged iso faces | `evidence/raw/live_pins_start.json` |
| **oracle frozen BEFORE any edit/run** | `oracle.md` `9334302aa236da374e74f69d9cbfa95e40aaf5ae0d3e76afd0f246079e820a42` @ `2026-09-22T23:59:56.707Z` | `oracle_freeze.json` |
| copy-out of the 2 before-files | byte-identical to the live pre-edit pins | `binding.json → write_targets_before_after[].before_copy_matches_live_before_pin = true` |
| edit set frozen in the oracle (E1–E5) | the whole authorized diff was written into `oracle.md §4` before the first edit | `oracle.md §4` |
| RED before edit | 15 F / 11 P on the merged mirror | `evidence/raw/red_unedited_on_merged.txt` |

`oracle.md` has not been edited since the freeze (re-hash at close must equal
the freeze value — see `evidence/final_deliverable_hashes.json`).

## 1. RED (pre-edit status quo, reproduced)

Both **unedited** test files run once on the merged mirror
(`%TEMP%\cwtd-a20260922-01` = production `src` copy + the 3 merged iso faces
overlaid + prod `conftest.py`/`pytest.ini`/`tests` copied):

**15 failed, 11 passed** — decomposed 4 F + 5 P (readiness) and 11 F + 6 P
(prompt-injection), i.e. reviewer Run 1 exactly. The 15 failing names are
byte-identical to the 4 in `informational_cw_readinessgraph_unadapted_seed.txt`
plus the 11 in `informational_cw_unit_tests_on_merged.txt`
(`checks.red_matches_reviewer_run1 = true` in `evidence/raw/oracle_checks.json`).

## 2. Edit-by-edit rationale (authority = reviewer condition-1, quoted per edit)

### E1 — `test_readiness_graph.py::_seed` adds ONE line
Reviewer §8.1(a): *「tests/unit/test_readiness_graph.py::_seed — add the 1-line
`"state_domain": "review"` receipt tag (my Run 1→2 proves it flips the 4
readiness failures to green)」*.

```python
                        "policy_hash": RULESET_HASH,
+                       "state_domain": "review",
```
Hunk count: **1**. No assertion, no expectation, no comment line touched (the
card says ONE line; GUARD-MERGE's own mirror patch carried two extra comment
lines — deliberately NOT reproduced, the rationale lives here instead).
Mechanism: the merged reader `_receipt_from_store`/`read_prompt_injection_review`
reject any receipt whose `state_domain != "review"` (C7 fail-closed), so the
untagged seeded receipt read as `absent` and the four safety-stage expectations
(`hit`/`expired`/`tampered`/`ignored`) could not be reached.

### E2 — `evidence_payload` on **every** `record_prompt_injection_review(...)` call
Reviewer §8.1(b)(i): *「pass `evidence_payload` to every
`record_prompt_injection_review` call (supply the text payload each test
already scans/owns)」* — this is P5-a.

Two coupled facts drove the exact shape:
1. P5-a refuses a write with `evidence_payload must be provided`, and
2. P5-a also requires `sha256(evidence_payload) == evidence_sha256`.

The old placeholder `evidence_sha256="e" * 64` therefore cannot bind **any**
payload, so the calls need both arguments. Chosen form: a module-level clean
text `_EVIDENCE_PAYLOAD = "zr-302 receipt evidence payload for this test file."`
plus `_evidence_sha256()` (= `hashlib.sha256(payload)`) — the payload is clean
so the writer's internal `scan_text(payload)` re-verification returns
`not_detected`, matching the `status` every call declares. Data-producer change
only; no assertion reads `evidence_sha256`. This is the same adaptation pattern
GUARD-MERGE already proved in `evidence/raw/battery_i_probe_fixture_adaptation.diff`
(its `_payload` + `hashlib.sha256(...)` line-for-line).

### E3 — the two equality-assert constructions get `state_domain="cache"`
Reviewer §8.1(b)(ii): *「construct `ReviewEvaluation(..., state_domain="cache")`
… (per FIX's convention)」*. Exactly two tests build a `ReviewEvaluation` in an
`assert … ==`: `test_evaluate_hit` and `test_evaluate_absent`. The merged dataclass
declares `state_domain` with **no default** (it precedes `reason: str = ""`, so
omitting it raises `TypeError` — that TypeError was RED #9). FIX's convention is
the literal `state_domain="cache"` (see `prompt_injection_guard.ReviewEvaluation`
docstring *«Cache evaluation of a stored review receipt (state_domain="cache")»*
and FIX's N1 evidence line `…state_domain='cache'…`). Reasoning/expected values
untouched.

### E4 — the legacy no-binding test is replaced (P5-c invalidates it BY DESIGN)
Reviewer §8.1(b)(iii): *「drop/replace the legacy no-binding expectation
(`test_record_without_binding_keeps_legacy_shape`) which P5-c makes invalid by
design」* + card: rename for honest name lineage + one-line comment citing
P5-c/OPEN-6 C2.

* **old name** → **new name**: `test_record_without_binding_keeps_legacy_shape`
  → `test_record_without_binding_rejected`
* **citation line (P5-c / OPEN-6 C2)**, verbatim, the new docstring:
  ```python
  """P5-c / OPEN-6 C2: a receipt without source/policy binding is
  refused — the write side of the fail-closed contract."""
  ```
* **name-lineage comment**, verbatim:
  ```python
  # Replaces test_record_without_binding_keeps_legacy_shape: P5-c made dual
  # binding MANDATORY, so the legacy "keeps the FC-905 shape" expectation is
  # invalid BY DESIGN (there is no longer any way to write an unbound receipt).
  ```
* **new body = forward contract**: an unbound write is rejected with the
  `must be a lowercase SHA-256`-class defined error for **both** binding fields
  (`source_sha256 must be a lowercase SHA-256`, then, with a valid source bound,
  `policy_hash must be a lowercase SHA-256`), and `read_prompt_injection_review`
  still returns `None` afterwards (nothing was written).

**P5-c design note**: `_validate_review_inputs` now calls
`_require_sha256(source_sha256, …)` / `_require_sha256(policy_hash, …)` with
`optional=False` (the FIX face changed the two `optional=True` parameters). A
receipt without dual binding can no longer exist in a database written through
the product writer, so the old expectation 「written without binding ⇒ stays
readable and keeps the legacy FC-905 shape」 is not merely failing — it is
unreachable-by-design. Keeping it would pin the suite to a gap the FIX face
closed.

### E5 — the two further adaptations the card's list did not cover (frozen as oracle §4-E5 / §R2 before the run)

Attribution of the 11 RED names (raw-backed, `oracle.md §R2`) shows the three
literal sub-edits fix only 9 of them:

**(E5a) `test_record_bad_binding_hash_rejected`** — its second
`pytest.raises(match="policy_hash")` was masked: with `source_sha256` defaulted
to `None`, the mandatory source binding raises `source_sha256 must be a
lowercase SHA-256` first, so the expected `policy_hash` error never surfaced
(raw: `Expected regex: 'policy_hash' / Actual message: 'source_sha256 …'`).
Fix = supply a **valid** `source_sha256="a" * 64` in that one call, plus the
standard payload pair. The expectation `match="policy_hash"` is untouched — this
edit makes the existing expectation *reachable* rather than changing it.

**(E5b) `test_evaluate_legacy_unbound_receipt_is_tampered_not_hit`** — this test
**produced** an unbound receipt through the writer; P5-c now refuses that write,
the same design fact as E4. Per the parent's ruling (裁定 2, received before this
record was written): **name, docstring and both assertions
(`status == "not_reviewed"`, `cache_state == "tampered"`) are byte-for-byte
unchanged; only the data producer changed** — the legacy row is planted directly
with SQL, the same technique `test_evaluate_malformed_receipt_fails_closed`
already uses two tests earlier. The planted row carries `"state_domain":
"review"` so it passes the C7 read gate and still exercises the real
`_binding_mismatch` → `tampered` (never `hit`) path the test is **named for**.
The disclosure comment (verbatim) states that the writer can no longer produce
this row and that a pre-C7 row *without* the tag reads `absent` instead
(GUARD-MERGE `handoff.unproven[2]` — deliberately NOT asserted here).

The rejected alternative (assert `absent` instead) would have changed **what the
test asserts** = semantic drift; the parent rejected it for the same reason.

## 3. Finding 1 — the card's 「22/22」 is arithmetically impossible (parent ruling recorded)

Measured read-only **before the freeze**: the file contains exactly **17**
`def test_` (no `parametrize`), the reviewer's own Run 1 records it as
`11 failed / 6 passed` = 17, and the combined RED is 15 F + 11 P = **26** =
17 + 9. `22 = 26 − 4` double-counts readiness's 9 tests (9 + 22 = 31 > 26).
The only self-consistent GREEN split is **9 (readiness) + 17 (prompt-injection)
= 26, 0 failed**.

The oracle was frozen with binding form **(b')** = 「0 failed; collected count
== 17; the 11 RED names map one-for-one to GREEN」 (`oracle.md §R`), before any
edit or run. **No test was added, deleted, skipped or xfailed** to reach a
number (`oracle.md §7.5`).

**Parent ruling (received this attempt)**: *「裁定 1 … 你的口径胜出、我的
『22/22』作废」* — the parent's `22/22` is void, (b') stands, the refusal to pad
the suite is correct, and the parent has recorded its own arithmetic slip on the
register trail as a dispatch arithmetic artifact.

## 4. GREEN + mutations (all against the merged iso mirror)

| run | result | evidence |
|---|---|---|
| RED, unedited both files, merged iso | **15 failed / 11 passed** (= reviewer Run 1) | `evidence/raw/red_unedited_on_merged.txt` |
| GREEN (a) `test_readiness_graph.py` | **9 passed / 0 failed** | `evidence/raw/green_a_readiness.txt` |
| GREEN (b) `test_prompt_injection_guard.py` | **17 passed / 0 failed** (11 F → 0) | `evidence/raw/green_b_prompt_injection_guard.txt` |
| GREEN combined | **26 passed / 0 failed** | `evidence/raw/green_combined.txt` |
| M1 − seed tag (mirror-local) | **4 failed / 5 passed**, the same 4 names | `evidence/raw/mut1_seed_tag_removed.txt` |
| M2 − `evidence_payload` from `_write_receipt` (mirror-local) | **7 failed / 10 passed**, exactly the 7 payload-dependent names | `evidence/raw/mut2_payload_removed.txt` |
| restore (mirror reloaded from the delivered files) | **26 passed**, restored sha256 == after-pins | `evidence/raw/mut_restored_confirm_green.txt` |

Machine-checked: `evidence/raw/oracle_checks.json` → all five checks `true`;
`evidence/raw/mutation_summary.json` → `M1/M2/R matches_oracle = true`.

## 5. Verification scope (oracle §1) — runs NEVER touched unmerged production

Every run above happened in `%TEMP%\cwtd-a20260922-01` with the **merged** faces
overlaid. The edited tests were **not** run against the current (unmerged)
production guard at any point: production `prompt_injection.py` has no
`evidence_payload` binding, production `ReviewEvaluation` has no `state_domain`,
and the production reader has no C7 gate — such a run would fail for the WRONG
reason (production lacks the contract, not the tests). The pair only becomes
runnable in-tree **after** the single CW commit lands both sides together.
RF/CW product trees were never opened for write by any run; only the two
authorized test files differ from their start pins.

## 6. Boundaries / close

* CW production sources re-hashed at close:
  `f900a13d…b0c08` / `7b22f239…39618` / `3f4c43b0…85acc` — **unchanged, 3/3**
  (`evidence/raw/live_pins_close.json` → `production_sources_read_only[*].unchanged = true`).
* Exactly **2** files written in the CW tree (the two unit tests); 0 other CW
  writes, 0 sibling-attempt writes, **0 git commands**, scratch in
  `%TEMP%\cwtd-a20260922-01` + pytest's `%TEMP%` basetemp only.
* This attempt writes inside itself only: `oracle*`, `binding`, `commands`,
  `decision`, `changes.diff`, `handoff`, `recovery`, `before/`, `scripts/`,
  `evidence/`.

## 7. What is deliberately NOT claimed

* No run of the rest of CW's suite (only the 2 files in scope) and no run of
  the edited tests against production sources (see §5).
* No real pre-C7 production receipt rows were read; the E5b `absent`-arm note is
  a disclosed code-path observation, not an assertion (GUARD-MERGE `unproven[2]`
  stands).
* The CW commit itself is the parent's (reviewer condition-4 / register §48
  item 5); this pass ends at `handoff.status = review_pending`, unsigned.
