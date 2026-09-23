# oracle.md — RF-E2E-ADAPT (frozen BEFORE any edit)

Attempt: `a20260923-01`
Frozen: 2026-09-23 (pre-edit; RED already reproduced, no fixture/test file touched yet)
Protocol: CI root-fix (`assurance/runs/2026-09-02_remaining-gap-closure/ci_root_fix.md`)
— fix root cause, do not bypass.

## Context

Pre-push gate `real-roots E2E` step went RED at push attempt `1fa090fe`
(4 failed / 51 passed): three `tests/test_fc1002_three_process_e2e.py` chain
tests (chain rc=3, `prompt injection not reviewed … prompt_injection_status=not_reviewed`)
plus `tests/test_zr803_chaos_recovery.py::test_lock_held_write_transaction_does_not_block_read_journey`
(investigate — attribution pending). Carry-forward consequence of the
just-promoted CW receipt contract (company-wiki `5d72529`: merged guard
requires `state_domain` + payload/dual-binding; read-side fail-closed on
missing). RF `scripts/source_preparation.py` unchanged since `91a6dc32`-era;
batch-4 push real-roots was GREEN.

## Gate's exact selection (quoted from `tools/pre_push_gate.py`)

```python
# tools/pre_push_gate.py:141-149
REAL_ROOTS_TESTS = (
    "tests/test_zr803_chaos_recovery.py",
    "tests/test_zr1103_journey_reverify.py",
    "tests/test_ca203_weekly_t3.py",
    "tests/test_fc1101_ci_manifest.py",
    "tests/test_compatibility_manifest.py",
    "tests/test_fc1002_three_process_e2e.py",
    "tests/test_ca302_three_journeys.py",
)
# tools/pre_push_gate.py:178-181
return _run(
    [sys.executable, "-m", "pytest", "-q", "--tb=short", *REAL_ROOTS_TESTS],
    "real-roots E2E (CI real-roots job)",
)
```

GREEN selection MUST be exactly:
`python -m pytest -q --tb=short tests/test_zr803_chaos_recovery.py tests/test_zr1103_journey_reverify.py tests/test_ca203_weekly_t3.py tests/test_fc1101_ci_manifest.py tests/test_compatibility_manifest.py tests/test_fc1002_three_process_e2e.py tests/test_ca302_three_journeys.py`

## Expectations (frozen)

(a) **Root cause identified with citation** — the exact line where the
envelope/status is produced AND the CW-side gate that now rejects old-shape
receipts, both quoted:

* RF producer/block line — `scripts/source_preparation.py:150-156`:
  ```python
  prompt_injection_status = envelope.get("prompt_injection_status")
  if prompt_injection_status is None:
      prompt_injection_status = "not_reviewed"  # defensive N-1 default
  if prompt_injection_status == "not_reviewed":
      raise RuntimeError(
          "prompt injection not reviewed — source preparation blocked "
          "per policy (prompt_injection_status=not_reviewed)")
  ```
* CW envelope default + receipt read — `company-wiki/src/company_wiki/source_catalog/resolver.py:1078`
  (`prompt_injection_status = "not_reviewed"`) and `resolver.py:1086-1088`
  (`review = read_prompt_injection_review(store, document_id)`; only a non-None
  receipt replaces the default).
* CW-side gate that now rejects old-shape receipts —
  `company-wiki/src/company_wiki/source_catalog/prompt_injection.py:449-452`
  (docstring `:425-426`: "A malformed receipt (bad schema/status, missing or
  illegal state_domain) fails closed as `not_reviewed` rather than being trusted."):
  ```python
  # C7 fail-closed: a state-carrying record without a valid domain tag
  # is ambiguous — never defaulted into either semantics.
  if receipt.get("state_domain") != STATE_DOMAIN_REVIEW:
      return None
  ```
  Guard-side twin — `prompt_injection_guard.py:201-203` (`_receipt_from_store`):
  `if receipt.get("state_domain") != STATE_DOMAIN_REVIEW: return None`
  ("C7 fail-closed: no valid domain tag => ambiguous => never trusted").
  New writer contract the fixtures must mirror — `prompt_injection.py:118-122`
  (P5-c dual binding MANDATORY), `:313-317` (`evidence_payload must be provided`),
  `:343-358` receipt shape incl. `:352` `"state_domain": STATE_DOMAIN_REVIEW`.
* RF fixture producing the OLD-shape receipt (no `state_domain` / binding /
  payload) — `tests/e2e_support/isolated_lake.py:338-344`.
* Eval-path confirmation (greps + LIVE reproduction, done pre-freeze):
  chain hops `source_preparation.py` → `scripts/filing_fetch_client.py` →
  `filing-fetch/scripts/fetch_filing.py:685-691` spawns
  `python -m company_wiki.source_catalog.cli`; `import company_wiki` resolves
  to `company-wiki/src/company_wiki/__init__.py` (live CW code, not vendored).
  Live probe (`evidence/probe_receipt_read.out`): fixture receipt keys =
  `[evidence_sha256, reviewed_at, reviewer, schema_version, status]` →
  `read_prompt_injection_review -> None` → `not_reviewed`; adding only
  `state_domain: review` → `not_detected`. Prime hypothesis CONFIRMED.

(b) **RED = the 4 gate failures reproduced standalone**, command:
`python -m pytest -q tests/test_fc1002_three_process_e2e.py "tests/test_zr803_chaos_recovery.py::test_lock_held_write_transaction_does_not_block_read_journey" --basetemp=%TEMP%\rf-e2e-adapt-red --tb=short`
from RF root, raw captured to `evidence/red_raw.txt`.
Result at freeze time: `4 failed in 30.64s` — the 3 fc1002 chain tests with
the exact `not_reviewed` upstream error (rc=3), zr803 lock test failing at
`tests/test_zr803_chaos_recovery.py:119` (chain rc!=0; its failure MESSAGE
additionally raises `AttributeError: 'str' object has no attribute 'decode'`
because the subprocess runs `text=True` — underlying cause attribution pending).

(c) **GREEN = after fix, those 4 pass + the full gate real-roots selection
passes** (exact selection quoted above — run THAT selection), raw captured.

(d) **Mutation = revert the fixture/receipt change ⇒ red returns** (fc1002
chain must fail again with the `not_reviewed` block), raw captured; fix
restored afterwards.

(e) **Zero CW product writes** — CW is READ-ONLY for this card. RF
test/fixture files only. IF the root cause turned out to be CW-side
test/fixture data: STOP and report before touching CW (parent routes it).
(Not the case: the failing data is the RF-side fixture receipt.)

(f) **No bypass markers anywhere** — gate steps untouched (`tools/pre_push_gate.py`
byte-identical), no baseline additions, no skip/xfail marks, no selection edits.

## zr803 (separate attribution)

Reproduce alone, attribute with evidence: same-family (chain blocked by the
same receipt root cause) vs independent vs load-flake. Independent
pre-existing findings (reproduces with the receipt issue absent) are recorded
honestly as out-of-scope + notified to parent — never silently folded into
the fix.

## Delivered evidence set

`evidence/red_raw.txt` (RED), `evidence/green_raw.txt` (gate-selection GREEN),
`evidence/mutation_raw.txt` (mutation RED), `evidence/probe_receipt_read.*`
(live eval-path probe), `binding.md` (before/after SHA-256 of every touched
file + gate log hash quote), `commands.md` (no bypass, no git), `decision.md`
(root-cause citation + fix-side rationale + zr803 attribution), `changes.diff`,
`handoff.md` (review_pending/unsigned/unmapped/unproven), `recovery.md`
(before-pins revert).
