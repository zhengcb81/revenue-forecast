# B3 — I-05-C delivery/evidence fixes (REM-11/12/13/14) — Decision

Attempt: `a20260921-01`. Card parent: I-05-C (`accepted_scoped`, 2026-09-20).
Source findings: `execution_runs/I-05-C/a20260919-01/review.md` — a carrier-landing
transcription of the owner-relayed signed verdict, not the reviewer's own report.

This file records the professional decisions taken where the remediation brief left a
choice, including the rejected alternatives, so the reviewer can audit the reasoning
independently of the result.

---

## D1 — REM-11: what the `bundle=None` path must return

**Choice**: unify both branches behind one scoping helper. With no bundle every role is
non-reusable, so `producer_events = requested roles ∪ transitive ancestors of requested
roles`, computed over CW's imported `ROLE_DEPENDENCIES`.

**Why**: the finding is that the no-bundle path ignores the request and returns the
*downstream closure* of the requested roles. Card I-05-C step 2 requires the recompute set
and the invalidation closure to be separated and forbids 盲补所有下游. The bundle-present
branch already implements the intended rule (accepted under I-05-C). Leaving the no-bundle
branch on a different rule means the same function answers the "what must be produced"
question two different ways depending on whether an envelope arrived — a latent
inconsistency that the reviewer's `normalized`-only counterexample exposed.

**Rejected alternatives**:
1. *Return a fixed all-roles constant when no bundle is present.* Rejected: that is the
   literal behaviour the finding calls vacuous; it also keeps two rules in one function.
2. *Narrow the default `roles` tuple* (e.g. to the four active-DAG production roles) so that
   "requested" always means "production-relevant". Rejected: `roles` is a published default
   consumed by `source_preparation.select_artifact_roles(handle)` with no argument, and
   FC-904 pins that path's output; narrowing the default would break a frozen acceptance test
   to fix a bug that does not require breaking it.
3. *Fix only the docstring (REM-13) and leave the behaviour.* Rejected: the docstring would
   then describe a behaviour no branch implements for the no-bundle case.

**Counterexample that must fail after the fix**: `roles=("normalized",)`, `bundle=None`
→ pre-fix returns 5 roles; post-fix returns `["normalized"]`.
**Compatibility**: the frozen FC-904 tests pass with **zero** edits to the frozen test file.
**Recovery**: the fix is a two-line branch change plus a helper extraction; reverting it
restores the pre-fix behaviour exactly (mutation M1).

### D1a — the FC-904 `test_no_bundle_all_produced` question

The brief asked whether the FC-904 wording and the I-05-C scoping genuinely conflict, and to
record the conflict rather than silently break FC-904.

**Frozen verdict (written into `oracle.md` before implementing): not a genuine conflict.**

`test_no_bundle_all_produced` requests the **default** tuple, which names all five roles. The
new rule produces the requested roles ∪ their ancestors; since all five are requested, all
five are produced. The assertion `produced == sorted(ALL_ROLES)` therefore still holds with
the frozen test untouched, and `test_prepare_source_unavailable_envelope_all_produced`
holds for the same reason through the live `source_preparation.py` path.

**The residual semantic shift is real and is recorded, not hidden**: the *justification*
changes from "no bundle ⇒ produce the global default universe" to "the default request itself
names all five roles". Under the old rule the output was independent of `roles`; under the new
rule it is a function of `roles`. The literal assertions in FC-904 cannot distinguish the two,
which is precisely why the reviewer's subset counterexample was the one that caught it.

**What would have made it a genuine conflict**: if the new rule had produced the
*active-DAG* role set (4 roles, dropping compatibility-only `markdown`), FC-904 would have
gone RED. That resolution is rejected in advance in D1 alternative 2. Recorded here so a
reviewer can confirm the conflict was assessed rather than assumed away.

### D1b — test evidence for D1
`iso/fixed/tests/test_w05c_minimal_production.py` gains `TestW05CXBundleNoneScoping`:
one test per request row of the oracle table, including the `normalized`-only case that is
RED pre-fix, plus an explicit `test_no_bundle_default_request_is_universe_scope` that documents
the D1a reading of `test_no_bundle_all_produced` in the same file.

---

## D2 — REM-12: how to re-point the regression at production

**Choice**: re-point, do not refresh. Host the **untouched** I-05-B test carrier in this
attempt and prepend the production repos to `sys.path`, so the carrier's own
`ISO_ROOT/checkout_scripts` entry no longer wins. Prove the binding with a hash assertion on
the loaded module's `__file__`.

**Why**: the finding is that `w05b-regression` passed against `A55602E5…` (the I-05-B
attempt's frozen isolated copy, one generation behind production `225FECDD…`). Two remedies
were offered — re-point at production, or refresh the iso to `225FECDD…` first.

**Rejected alternative**: *refresh the I-05-B iso copy in place.* Rejected because the I-05-B
attempt is frozen evidence for an accepted card; overwriting its isolated checkout would
retroactively change what that attempt's recorded evidence means, and the brief explicitly
forbids modifying frozen attempt material. Copying the carrier into this attempt and pointing
it at production achieves the same evidential force without touching history.

**Expected behaviour**: 20/20 pass with the loaded `company_wiki_source` hash `225FECDD…`.
**Vacuity proof retained**: the same carrier run against the stale I-05-B iso bytes also
passes 20/20 — captured side by side, because a regression suite that passes on both the stale
and the production bytes is *only* meaningful when the binding is proven, and pretending
otherwise would repeat the original defect.
**Recovery**: nothing to recover — the carrier is a copy; production was never written to.

---

## D3 — REM-13: docstring scope

**Choice**: rewrite the `select_artifact_roles` docstring (RF `company_wiki_source.py`) to
describe the implemented rule, including the REM-11 no-bundle rule.

**Rejected alternative**: *also rewrite the companion comment at
`source_preparation.py:134-138`*, which repeats the same stale "producer_events = the DAG
closure of the non-reusable roles" wording. `source_preparation.py` is inside card I-05-C's
allowlist and the comment is now inaccurate in the same way. Rejected from *this* fix's
allowlist anyway: REM-13 as scoped names the docstring only, and the execution protocol
forbids widening an allowlist by convenience. Registered as a carried finding (CF-1) with the
exact line range so the owner can fold it into whichever batch next touches that file.

---

## D4 — REM-14: fix the record, not the test

**Choice**: correct the evidence JSON row 3 `test` field to `test_invocation_trace_accuracy`;
leave the frozen test unchanged.

**Why**: row 3 reports 4 calls / 1 artifact. `test_invocation_trace_accuracy` uses
`fail_count=3, max_retries=4` → 3 failed + 1 success = 4 calls, 1 artifact. The named test,
`test_retry_count_vs_artifact_count_diverge`, uses `fail_count=2` → 3 calls, 1 artifact.
The numbers belong to the former; only the name is wrong. Rows 1 and 2 were re-derived and
are correctly attributed.

**Rejected alternative**: *change the diverge test to `fail_count=3, max_retries=4` so the
JSON becomes true.* Rejected: that edits frozen test code to fit a misattributed record, i.e.
the exact inversion step 6 of the execution protocol forbids, and it would weaken the W05C-N2
oracle's 2-call retry example.

**Landing**: the corrected file is `iso/fixed/tests/retry-count-vs-artifact-count.json`.
The frozen I-05-C copy is untouched; the correction is published as a replacement artifact for
the owner to land.

---

## Carried findings (not fixed here)

| id | severity | finding |
|---|---|---|
| CF-1 | P3 | `RF:scripts/source_preparation.py:134-138` comment still says "producer_events = the DAG closure of the non-reusable roles"; same stale semantics as REM-13, outside REM-13's named scope. |
| CF-2 | P2 | Inherited from I-05-C and **not** addressed by this card: `produce_for_demand` remains mock-only in tests (GAP-1); `consumer_analysis` real producer absent (GAP-2); `InvocationTracker` event schema unapproved for persistence (GAP-3). |
| CF-3 | P3 | Inherited P3-2: shared audit harness `scripts/run_card.py` never validates `cases.json` `expected`. |
| CF-4 | P3 | Inherited P3-3: the reviewer's original I-05-C report is still not archived; `review.md` is a carrier-landing transcription. |

## Boundaries
- Production repos stayed read-only; all edits are in this attempt's `iso/fixed/` tree.
- `disclosure_adaptation = unmapped`; `accuracy = unproven`.
- Status ends at `review_pending`; the implementer never signs acceptance.
- Promoting the fixed files into RF/CW is a separate owner decision, not taken here.
