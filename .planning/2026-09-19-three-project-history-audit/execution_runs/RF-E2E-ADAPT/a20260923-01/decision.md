# decision.md — RF-E2E-ADAPT (root cause, fix side, zr803 attribution)

## 1. Root cause (citation: exact producer line + exact rejecting gate)

**One root cause, two cited ends.**

### (i) Where the blocking status/error is produced (RF side)

`scripts/source_preparation.py:150-156` — the envelope's status is read and
`not_reviewed` is fail-closed into the exact gate-log error:

```python
prompt_injection_status = envelope.get("prompt_injection_status")
if prompt_injection_status is None:
    prompt_injection_status = "not_reviewed"  # defensive N-1 default
if prompt_injection_status == "not_reviewed":
    raise RuntimeError(
        "prompt injection not reviewed — source preparation blocked "
        "per policy (prompt_injection_status=not_reviewed)")
```

`RuntimeError` → `main()` writes `{"error_code": "upstream", ...}` and exits
rc=3 — byte-identical to the three fc1002 failures.

### (ii) Where the envelope status comes from (CW side)

`company-wiki/src/company_wiki/source_catalog/resolver.py:1078` defaults
`prompt_injection_status = "not_reviewed"`, and `resolver.py:1083-1088`
replaces it ONLY from a receipt the reader accepts:

```python
from .prompt_injection import read_prompt_injection_review
document_id = resolution.matches[0].document_id
review = read_prompt_injection_review(store, document_id)
if review is not None:
    prompt_injection_status = review["status"]
```

### (iii) The CW-side gate that now rejects old-shape receipts (the merged face)

`company-wiki/src/company_wiki/source_catalog/prompt_injection.py:449-452`
(docstring at `:425-426`: *"A malformed receipt (bad schema/status, missing or
illegal state_domain) fails closed as ``not_reviewed`` rather than being
trusted."*):

```python
# C7 fail-closed: a state-carrying record without a valid domain tag
# is ambiguous — never defaulted into either semantics.
if receipt.get("state_domain") != STATE_DOMAIN_REVIEW:
    return None
```

Guard-side twin (the merged guard) — `prompt_injection_guard.py:201-203` in
`_receipt_from_store`: `if receipt.get("state_domain") != STATE_DOMAIN_REVIEW:
return None` ("C7 fail-closed: no valid domain tag => ambiguous => never
trusted"). New **writer** contract the fixtures must satisfy —
`prompt_injection.py:118-122` (P5-c dual binding MANDATORY: `source_sha256`
+ `policy_hash`), `:313-317` (P5-a: `evidence_payload must be provided`),
`:320-322` (`sha256(payload) == evidence_sha256`), `:343-358` receipt shape
with `:352` `"state_domain": STATE_DOMAIN_REVIEW`. Ruling clauses: GUARD-MERGE
§1-2 / OPEN-6 C7 (`prompt_injection.py:46-50`, `prompt_injection_guard.py:38-45`),
OPEN-6 C2/P5-c (`prompt_injection.py:18-21`), P5-a (`:22-26`).

### (iv) The RF-side data that fails the gate

RF fixture receipts were hand-shaped **pre-contract** dicts (no
`state_domain`, no dual binding, no payload binding):

- `tests/e2e_support/isolated_lake.py:338-344` (before) — the receipt for
  every IsolatedLake document (fc1002 ×3, zr803 lock, fc1001/fc1003/fc1004/
  fc1102/fc1105/fc1302/zr802/zr804/zr805 all consume this fixture);
- `tests/test_preparation_e2e_success.py:89-93` (before) — hand-shaped
  receipt in its own fixture catalog;
- `tests/test_zr709_zijin_journey.py:425-431` (before) — same.

So: **RF fixture receipts predate the just-promoted CW contract ⇒ live CW
reader fail-closes them as `absent`/`not_reviewed` ⇒ envelope says
`not_reviewed` ⇒ RF policy blocks at source_preparation.py:153-156 ⇒ rc=3.**
The prime hypothesis from the card is CONFIRMED — not assumed.

### Eval-path confirmation (greps + LIVE reproduction, pre-freeze)

- Chain hops: `source_preparation.py:88-99` spawns `scripts/filing_fetch_client.py`;
  the client (`filing_fetch_client.py:200-210`) spawns
  `filing-fetch/scripts/fetch_filing.py`, which at `fetch_filing.py:685-691`
  spawns `python -m company_wiki.source_catalog.cli` — i.e. the CLI evaluates
  receipts through the **live CW package** (`python -c "import company_wiki"`
  resolves to `company-wiki/src/company_wiki/__init__.py`), not a vendored copy.
  The test process itself path-imports `WIKI_ROOT/"src"` (test_fc1002:29).
- **Live probe** (`evidence/probe_receipt_read.py` / `.out`): built a real
  IsolatedLake, read the actual fixture receipt — keys
  `[evidence_sha256, reviewed_at, reviewer, schema_version, status]` — called
  the live `read_prompt_injection_review` → `None` → `not_reviewed`; adding
  only `state_domain: "review"` → `not_detected`. Single-field proof of the
  gate at prompt_injection.py:451.

## 2. Fix side (evidence-first)

**Fix side = RF test/fixture files.** CW is READ-ONLY for this card — and the
failing DATA is RF-side fixture receipts (CW's own unit tests write the new
contract and pass; `tests/unit/test_prompt_injection_guard.py:87-97` shows the
writer call shape with `evidence_payload=…`,
`tests/unit/test_readiness_graph.py:118-127` shows a seed receipt with
`"state_domain": "review"`). No CW product or test file was written (zero CW
writes — oracle clause (e)).

Files changed (all RF test/fixture):

| file | change |
|---|---|
| `tests/e2e_support/isolated_lake.py` | hand-shaped receipt dict → CW writer call `record_prompt_injection_review(..., source_sha256=<sources.content_sha256>, policy_hash=RULESET_HASH, evidence_payload=<normalized bytes>)` — mirrors CW `test_prompt_injection_guard._write_receipt` exactly; `state_domain` stamped + payload/dual binding validated AT WRITE time |
| `tests/test_preparation_e2e_success.py` | same: receipt removed from `doc_meta`, written via the CW writer with `evidence_payload=pdf_body`, `evidence_sha256=source_sha256=PDF_SHA`, `policy_hash=RULESET_HASH` |
| `tests/test_zr709_zijin_journey.py` | same: receipt removed from `_document_row`, written via the CW writer per document with `evidence_payload=pdf_path.read_bytes()` |
| `tests/test_zr803_chaos_recovery.py` | **not** an assertion change — the asserted condition (`proc.returncode == 0`) is byte-identical; only the failure-MESSAGE expression `proc.stderr.decode(...)` → `proc.stderr[...]` (the run() helper uses `text=True` at line 90, so stderr is `str`; `.decode` raised `AttributeError` and MASKED the real chain error in the gate log). Business assertions untouched (see §3) |

Business assertions of the fc1002/zr803/prep-e2e/zr709 tests are **unchanged**
— every `assert` condition is byte-identical before/after (see `changes.diff`:
the only assert-line edit is the message expression in zr803). No
skip/xfail/baseline added (host guard: `new(not baselined/registered)=0`).

Why the writer instead of adding `state_domain` by hand: the merged contract
requires state_domain **+ payload binding + dual binding** (card clause; OPEN-6
C1/C2/C7, GUARD-MERGE §1-2) — a hand-shaped dict can satisfy today's reader
and silently fail tomorrow's binding/freshness checks (the exact failure class
this card exists for). The writer enforces the whole contract at write time.

Freshness note (documented, deliberately unchanged): fixture `reviewed_at`
values stay fixed (`2026-08-12` / `2026-01-01`). The chain's reader
(`read_prompt_injection_review`) performs no TTL check, and `evaluate_review`
(the 30-day-cap freshness path) has no caller in this chain
(`evaluate_readiness` is only called from CW's own unit tests). Fixtures stay
byte-deterministic; if a future chain step routes through `evaluate_readiness`,
freshness must be revisited then (recorded as unproven below).

## 3. zr803 attribution (reproduced alone, evidence)

**Verdict: SAME-FAMILY (root cause), + a dependent masking defect — not
independent, not flake.**

1. Standalone reproduce (`evidence/red_zr803_lock_raw.txt`): the test fails at
   `tests/test_zr803_chaos_recovery.py:119` with
   `AttributeError: 'str' object has no attribute 'decode'` — the assertion
   MESSAGE crashes before showing the real chain error.
2. Attribution probe running the test's exact chain (`evidence/probe_zr803_chain.out`):
   `LOCK-HELD: returncode = 3` **and** `AFTER-RELEASE: returncode = 3`, both
   with `{"error_code": "upstream", "error": "prompt injection not reviewed …
   (prompt_injection_status=not_reviewed)"}` — byte-identical to the fc1002
   failures ⇒ the same receipt root cause (NOT lock-related: both legs fail
   identically; the lock holder holds a plain sqlite txn, WAL readers proceed).
3. The `.decode` mask is **not independent**: with the receipt fixed, the chain
   returns 0, the message expression never evaluates, and the test passes —
   it does NOT reproduce with the receipt issue absent. It is a dependent
   pre-existing defect whose only effect is hiding the root cause from the gate
   log (it fired precisely because the chain failed), hence fixed in-scope as a
   diagnostics repair with the assertion condition untouched.

## 4. No bypass (oracle clause f)

- `tools/pre_push_gate.py` untouched — SHA-256
  `3DF161A7CEEA17DE95B36845BDB3C4CEE729DCA215C56853868780DCE7331484` (not in
  this card's edit set; edits were exactly the 4 files in `changes.diff`).
- `scripts/source_preparation.py` untouched — SHA-256
  `91A6DC32466E9D67B9D034AC345349EE683F6D5FD9486A67CD3ADE009C6EBF4D`
  (= the card's `91a6dc32`-era pin).
- No baseline additions (`host_assumption_guard`: new=0 vs baseline=16),
  no skip/xfail markers, no selection edits, no git operations.
