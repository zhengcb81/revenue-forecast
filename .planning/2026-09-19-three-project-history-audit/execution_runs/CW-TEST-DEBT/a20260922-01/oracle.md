# CW-TEST-DEBT — frozen oracle (a20260922-01)

Card: **CW-TEST-DEBT** — condition-1 debt pass of the GUARD-MERGE review
(verdict ACCEPT 2a26aaae): fix EXACTLY the two measured CW unit-test debts so the
merged faces' unit suites go green, for bundling into the upcoming single CW
commit together with the 3 merged source files.

Authority: GUARD-MERGE `reviewer_report.md §8.1` (condition 1) + the card text.
Frozen **before any edit to any test file, before any run**. Nothing in this file
may be edited after `oracle_freeze.json` is written; errata go to §9 as a dated
append (any hash change recorded there).

## 0. Inputs and live pins (recomputed read-only at attempt start, `evidence/raw/live_pins_start.json`)

| what | sha256 |
|---|---|
| **write target** `CW/tests/unit/test_readiness_graph.py` (before) | `71893f5d0db8ca675e05ebcda6d7feebefde7ee9a7a19350461efc0ece4708a7` |
| **write target** `CW/tests/unit/test_prompt_injection_guard.py` (before) | `c05e25fb4f2e3e1c72143ee3a7c56eccf8a7bddf750efb0394984561484f9bae` |
| CW live `src/…/prompt_injection_guard.py` (READ-ONLY) | `f900a13d7c22fe3bd742485c6b603de11b92a56d2414a2a046216ccd3b0b9c08` |
| CW live `src/…/prompt_injection.py` (READ-ONLY) | `7b22f23918d5e6b083a3c5272de2ed26c8a0c420b007f1268c664c0c86139618` |
| CW live `src/…/readiness_graph.py` (READ-ONLY) | `3f4c43b0049eca71fde4f7d9152b02674a26679b4470f6607383eb1820685acc` |
| merged face `GUARD-MERGE/…/iso/prompt_injection_guard.py` | `d71254782c10cd6d58c768eeb50e220de5e3d8047709e26f0604b5c59e67df0d` |
| merged face `iso/prompt_injection.py` | `88154de4ab7630606c2545cdcdf9c3ac44faf32bcae0f83f33a1cebc6d490f33` |
| merged face `iso/readiness_graph.py` | `50c94de28f328d125bd4834b2cda8a46794cba5f5f3f01c5415b4060b2d8c97b` |

The three live production sources equal the GUARD-MERGE *before* pins and the
three iso faces equal the reviewer's re-hashed ACCEPT pins (§1 table of
`reviewer_report.md`) — measured, not transcribed.

**Write authority (frozen):** the ONLY product writes authorized by this card are
the 2 unit-test files in `CW/tests/unit/`. CW **production sources stay
untouched** (that commit carries the merged sources separately). No git of any
kind. All scratch in `%TEMP%` or inside this attempt directory.

## 1. Verification target (frozen — this is the scope statement)

Production sources are **UNMERGED**. Therefore:

* **Every** verification run happens against the **merged iso** overlaid on a
  production copy inside a `%TEMP%` mirror (`%TEMP%\cwtd-a20260922-01`), exactly
  as the reviewer did (prod `src` copy + the 3 merged faces overlaid + prod
  `conftest.py`/`pytest.ini`/`tests` copied, `PYTHONIOENCODING=utf-8`,
  `-p no:cacheprovider`, RF/CW trees never written by a run).
* The edited tests **MUST NOT** be run against the CURRENT (unmerged)
  production guard until the CW commit lands: production `prompt_injection.py`
  has no `evidence_payload` binding, production `prompt_injection_guard.ReviewEvaluation`
  has no `state_domain`, and the production reader has no C7 gate — running the
  edited tests there would fail for the WRONG reason (production lacks the
  contract, not the tests). **No such run is part of this attempt.**
* Corollary pinned here and repeated in `decision.md`: green here means
  「merged faces + edited tests」; the pair only lands together in the one CW
  commit.

## 2. Frozen RED (pre-edit status quo — no fabricated red)

RED = the CURRENT (unedited, before-pinned) test files run once on the merged
mirror, BEFORE any edit. Required to reproduce GUARD-MERGE reviewer Run 1:

* combined **15 failed / 11 passed** (26 collected)
* `tests/unit/test_readiness_graph.py` = **4 failed / 5 passed**, failing names
  byte-identical to `informational_cw_readinessgraph_unadapted_seed.txt`:
  `test_ready_source_all_stages`, `test_safety_guard_drives_graph`,
  `test_safety_tampered_blocks_with_action`, `test_safety_ignored_blocks_with_action`
* `tests/unit/test_prompt_injection_guard.py` = **11 failed / 6 passed**,
  failing names byte-identical to the 11 in
  `informational_cw_unit_tests_on_merged.txt`

Any deviation ⇒ stop and record it; no expectation may be edited to fit.

## 3. Frozen GREEN expectations

**(a) `tests/unit/test_readiness_graph.py` passes 9/9 on the merged faces**
(its 4 F become 0) — reviewer Run 1→2 proves the single seed-tag line does this
(their mirror-only patch flipped combined to `11 failed / 15 passed`, i.e.
readiness 0 F).

**(b) `tests/unit/test_prompt_injection_guard.py`: 0 failed, every collected
test passes, collected count = 17, and the 11 RED names become 11 GREEN names
(one-for-one; no test added or removed except the single authorized rename).**

*Card-number reconciliation (frozen at §R below, before any run): the card says
「22/22」; the measured collected count is 17 — see §R.*

**(c)** Scope as frozen in §1: green is asserted only against the merged mirror.

**(d) Mutations (non-vacuity) — each mirror-local, restored and re-greened after:**

| id | mutation (mirror-local) | required |
|---|---|---|
| M1 | delete the added `"state_domain": "review"` line from the mirror's `test_readiness_graph.py::_seed` | the **same 4** readiness F return (4 failed / 5 passed) |
| M2 | delete `evidence_payload=_EVIDENCE_PAYLOAD` from `_write_receipt` in the mirror's `test_prompt_injection_guard.py` | the **7 payload-dependent** F return: `test_record_with_binding_fields`, `test_evaluate_hit`, `test_evaluate_ignored_when_policy_changed`, `test_evaluate_expired`, `test_evaluate_ttl_boundary_equality_is_still_hit`, `test_evaluate_tampered_when_source_changed`, `test_evaluate_input_validation` (7 failed / 10 passed) |
| R | restore byte-identical to the delivered file (sha256 == after-pin) | 0 failed again |

Mutations are mirror-local ONLY: the delivered CW files are never mutated.

## 4. Frozen edit set (the whole authorized diff — verbatim before the first edit)

**E1 — `tests/unit/test_readiness_graph.py::_seed`** (card §2 + reviewer §8.1(a)):
add ONE line to the seeded receipt dict, after `"policy_hash": RULESET_HASH,`:

```
                        "state_domain": "review",
```

Mirror-only line; **expectations untouched** (no assert changed); no comment
lines added (card says ONE line; the rationale lives in `decision.md`).

**E2 — `test_prompt_injection_guard.py`: payload on every write call**
(reviewer §8.1(b)(i), P5-a): the file gains `import hashlib` + a module-level
`_EVIDENCE_PAYLOAD` (clean text ⇒ `scan_text` ⇒ `not_detected`, matching the
`status` every call declares) and a `_evidence_sha256()` helper;
`_write_receipt` and every direct `record_prompt_injection_review(...)` call
pass `evidence_payload=_EVIDENCE_PAYLOAD` with
`evidence_sha256=_evidence_sha256()` (P5-a requires
`evidence_sha256 == sha256(evidence_payload)`; the old placeholder `"e" * 64`
cannot bind any payload). Data-producer change only.

**E3 — the two equality-assert constructions** (reviewer §8.1(b)(ii), C7): build
`ReviewEvaluation(..., state_domain="cache")` (FIX's convention) in
`test_evaluate_hit` and `test_evaluate_absent`.

**E4 — legacy-test replacement** (reviewer §8.1(b)(iii), P5-c): rename
`test_record_without_binding_keeps_legacy_shape` →
`test_record_without_binding_rejected`, one-line comment citing P5-c / OPEN-6 C2
+ the old name, body asserts an unbound write is **rejected** with the
`must be a lowercase SHA-256`-class defined error (both binding fields) and that
nothing was written. The old expectation is invalid BY DESIGN (P5-c made dual
binding mandatory).

**E5 — two further minimal adaptations, required because E2+E3+E4 alone leave 2
of the 11 RED tests red** (frozen here so the oracle covers them; see §R2):

* **E5a** `test_record_bad_binding_hash_rejected`: the second `pytest.raises`
  (`match="policy_hash"`) is masked by P5-c — with `source_sha256` defaulted to
  `None` the writer raises `source_sha256 must be a lowercase SHA-256` first.
  Fix = pass a VALID `source_sha256="a" * 64` in that one call so the intended
  `policy_hash` rejection surfaces. Expectation (`match="policy_hash"`) untouched.
* **E5b** `test_evaluate_legacy_unbound_receipt_is_tampered_not_hit`: the test
  PRODUCES an unbound receipt through the writer, which P5-c now refuses — the
  same design fact that invalidates E4. Fix = keep the name, the docstring and
  the `status == "not_reviewed"` / `cache_state == "tampered"` expectations
  byte-for-byte, and replace only the data producer: plant the legacy (unbound)
  receipt row directly with SQL, exactly as
  `test_evaluate_malformed_receipt_fails_closed` already plants its malformed
  row. The planted row carries `"state_domain": "review"` so it passes the C7
  read gate and the test still exercises the real `_binding_mismatch` →
  `tampered` (never `hit`) path it is named after. A comment must disclose that
  the writer can no longer produce the row (P5-c) and that a pre-C7 row without
  the domain tag reads as `absent` instead (GUARD-MERGE `unproven[2]`, not this
  card's assertion).

No other test, fixture, assertion, docstring or line in either file may change.

## 5. Order of execution (frozen)

pins → **oracle freeze** → scaffold/copy-out → **RED** (unedited tests on merged
mirror, §2) → apply E1–E5 to the two CW test files → **GREEN** (§3a/§3b) →
**mutations M1/M2 + restore** (§3d) → deliverables → close pins.

## 6. Deliverables

`oracle.md` + `oracle_freeze.json`; `binding.json` (before-pins of both test
files from CW live + merged-iso pins + after-pins); `commands.json`;
`decision.md` (per-edit rationale citing reviewer condition-1 + the P5-c design
note for the replaced test + §R reconciliations); `changes.diff` (difflib, the
2 test files, no git metadata); `handoff.json`
(`review_pending` / unsigned / `unmapped` / `unproven`); `recovery.md`
(before-pin restore = exact revert); `evidence/raw/*` (RED, GREEN, mutations,
mirror setup, start+close live pins); `evidence/SUMMARY.md`.

## 7. Boundaries (frozen)

1. CW **sources read-only** — guard/pi/rdg must still hash to
   `f900a13d…` / `7b22f239…` / `3f4c43b0…` at close.
2. Only the 2 unit-test files may be modified in the CW tree.
3. No git command of any kind (read-only git inspection is out of scope here —
   this card runs **zero** git verbs).
4. Scratch only in `%TEMP%\cwtd-a20260922-01` (+ pytest's own `%TEMP%`
   basetemp) and inside this attempt directory.
5. No test may be added, deleted, skipped or xfailed to reach a number; the only
   rename is E4.

## 8. Non-goals

No production source edit; no commit (the parent performs §48-item-5 commit
after review); no re-run of GUARD-MERGE batteries (i)–(v); no claim about real
pre-C7 production rows (synthetic-row evidence only).

## R. Card-number reconciliation (frozen here, read-only measurements, BEFORE any run)

The card states expectation (b) as 「passes **22/22**」. Measured before freeze:

* `grep -c '^\s*def test_'` on `tests/unit/test_prompt_injection_guard.py` =
  **17** (no `parametrize`); a workspace glob finds exactly **one** copy of that
  file, so no double-collection is possible.
* Reviewer Run 1 (report §6): that file on the merged mirror = **11 failed /
  6 passed** = 17 collected.
* Combined RED (card §3) = 15 F / 11 P = 26 = 17 (this file) + 9 (readiness).

22 = 26 − 4, i.e. the combined total minus readiness's 4 failures — which
double-counts readiness's 9 tests (9 + 22 = 31 > 26 collected). The only
self-consistent GREEN split of the 26 collected tests is **9 (readiness) + 17
(this file) = 26, 0 failed**.

Frozen binding form of (b): **0 failed; pass count == collected count == 17;
the 11 RED names map one-for-one to GREEN.** The invariant the card cares about
(「its 11 F become 0」) is asserted exactly; no test is created to reach 22
(§7.5 forbids it).

## R2. Why the card's three literal sub-edits are insufficient (frozen analysis)

Attribution of the 11 RED names to their cause, read off the raw
`informational_cw_unit_tests_on_merged.txt` tracebacks:

| cause | tests | fixed by |
|---|---|---|
| P5-a `evidence_payload must be provided` (via `_write_receipt`) | 7: `record_with_binding_fields`, `evaluate_hit`, `evaluate_ignored_when_policy_changed`, `evaluate_expired`, `evaluate_ttl_boundary_equality_is_still_hit`, `evaluate_tampered_when_source_changed`, `evaluate_input_validation` | E2 |
| P5-c `source_sha256 must be a lowercase SHA-256` on an unbound write | 2: `record_without_binding_keeps_legacy_shape`, `evaluate_legacy_unbound_receipt_is_tampered_not_hit` | E4 (first), **E5b (second — not covered by the card's list)** |
| masked `match="policy_hash"` assertion | 1: `record_bad_binding_hash_rejected` | **E5a — not covered by the card's list** |
| `TypeError: ReviewEvaluation.__init__() missing state_domain` | 1: `evaluate_absent` | E3 |

⇒ E2+E3+E4 leave exactly **2** red (`E5a`, `E5b`); oracle §3(b) can only be met
with E5 included, which is why E5 is frozen in the edit set rather than
discovered mid-run. Nothing else in the file may change.

## 9. Errata

(none at freeze)
