# I-08-C Independent Review — consumer rejection of forged / replayed / unsigned structures

- Plan: `2026-09-19-three-project-history-audit`
- Attempt: `execution_runs/I-08-C/a20260919-01`
- Reviewer role: independent (read-only; no production write, no git write command)
- Reviewer probes: `%TEMP%\i08c_review\probe_i08c.py`, `probe2.py`, `probe3.py`, `probe4.py`
- Reviewer rerun log: `reviewer_rerun_stdout.txt` (this directory)

## VERDICT: `changes_required`

The card's headline trust property is **not** satisfied. Two of the card's five
prescribed cases fail against the current production tree, and the failure is
worse than the implementer reported: **the honest, unmodified `unattested`
package is also accepted by every consumer entry point in this repo.** Consumers
are not merely under-verifying forged attestation — they verify attestation *not
at all*.

The implementer's own handoff is honest about this (`implementer_self_acceptance:
false`) and no false completion claim was made. The defect is in the product,
not in the reporting of it.

---

## Independently verified claims

| Claim | Result |
|---|---|
| 12/12 tests pass, `test_i08c_consumer_rejection.py`, 199 lines | **CONFIRMED** — rerun by reviewer: `12 passed in 5.05s` |
| Test file sha256 `5dd5a96c…` | **CONFIRMED** |
| `oracle.md` sha256 `478bd70e…` | **CONFIRMED** |
| `pytest_verdict.stdout.txt` sha256 `cb81112d…` | **CONFIRMED** |
| `revenue_publication.py` `183803bb…` | **CONFIRMED** on disk |
| `revenue_report.py` `a85fb484…` | **CONFIRMED** on disk |
| `publication_registry.py` drifted `44662744…` → `29aaae4f…` | **CONFIRMED** on disk; `is_registered` at line 188 |
| Production zero-write: `publications.jsonl` = `bc3256bb…` | **CONFIRMED** — hash matches; `LastWriteTime` 2026-09-18, i.e. pre-dates the card |
| git status clean for `scripts/ artifacts/ tests/ config/` | **CONFIRMED** — empty porcelain output; no production file under those paths modified in the attempt window |

## Oracle freeze order — `ADJUDICATED: no pre-registration violation`

Timeline reconstructed from filesystem mtimes (UTC), including the verdict-run
bytecode header:

| Time (UTC) | Event |
|---|---|
| 18:53:35 | pytest cache created (first run) |
| 18:56:19 | `.pytest_cache/v/cache/lastfailed` written — the exploratory run |
| **18:58:33** | **`oracle.md` r2 frozen** |
| 18:58:47 | `pytest_verdict.stdout.txt` written (verdict run) |
| 19:01:21 | verdict-run `.pyc` written |
| 19:01:07 | test source mtime (2.5 min *after* the verdict stdout) |

- **The r2 re-freeze genuinely precedes the verdict run** (18:58:33 < 18:58:47). The
  exploratory 8/12 run is disclosed in `oracle.md` ("Revision r2") and its pytest
  cache artifact from 18:56:19 corroborates that it happened before the freeze.
  This is a disclosed fixture-mechanics iteration, **not** a green-run-then-freeze.
- **The later test-file mtime is benign.** The verdict run's `.pyc` stores a
  timestamp-based source id (`flags = 0x0`): field1 = `1790017267` = the *current*
  file's mtime, field2 = `8542` = the *current* file's size. The verdict run
  therefore executed byte-for-byte the file that is frozen on disk now. The 19:01
  mtime is a content-identical rewrite (e.g. copy/save), not a post-verdict edit.
- **Two minor pre-registration blemishes (do not change the verdict):**
  1. `oracle.md` freezes 13 expectations (E1–E13) but the frozen test file contains
     12 tests — **E4 is absent** (`verification_context_sha256` mutation). Its
     mechanism is covered inside `test_e3`, so no property is unmeasured, but the
     oracle↔test mapping is incomplete with no stated reason.
  2. E13's expected outcome ("`validate_forecast_output` **ACCEPTS**") was pinned by
     observing the exploratory run rather than derived from code reading. E11's gap
     *was* predicted from code reading (`revenue_publication.py:222-226`). Only E13
     is post-hoc; it is honestly labelled as such.

---

## Product findings (adjudicated)

### F1 — `attestation_status` is a decorative label — **CONFIRMED, severity HIGH**

**Mechanism, verified by direct reading:**
- Issuance decides the label from a boolean: `revenue_core.py:167`
  `attestation_status = "host_signed" if attestation_capability() else "unattested"`.
- `attestation_capability()` (`revenue_core.py:113-125`) returns True if the
  `REVENUE_ATTESTATION_PROVIDER` path **exists as a file**. No key, no issuer, no
  signature, no provider invocation.
- Consumption only checks set membership: `revenue_publication.py:222-226`
  `require(attestation in (None, "host_signed", "unattested"), …)`. There is no
  signature, issuer, or `publication_attestation` check anywhere in `scripts/`.
- The label is not in the signed domain: the receipt's only gate is
  `gate_ids == ['output_recomputation']`, and `attestation_status` is not part of
  the embedded `input_document` (verified: `'attestation' in json(input_document)`
  → `False`). It is a member of the payload hash, but the attacker recomputes that
  hash, so the hash provides no protection.

**Reviewer reproduction (own probe, not the implementer's test):**
```
A-C2: U + ONLY attestation_status flipped to host_signed, self-hashes recomputed
  validate_publication_receipt: ACCEPTED   <-- property violated
  validate_forecast_output    : ACCEPTED   <-- property violated
A-C4: forged label + registry genuinely holds the same input anchor (True)
  validate_publication_receipt: ACCEPTED
  validate_forecast_output    : ACCEPTED
control: honest unattested package, no flips at all
  validate_publication_receipt: ACCEPTED
  validate_forecast_output    : ACCEPTED
```
**Severity HIGH — raised above a pure label-forgery concern by two facts:**
1. The label is a **false capability signal even without an attacker**. Setting
   `REVENUE_ATTESTATION_PROVIDER` to a 5-byte plain `.txt` file yields a formal
   publication stamped `host_signed` whose receipt contains no signature or issuer
   field, and the strong dispatcher accepts it. Any operator can mint
   "host-signed" artifacts by pointing an env var at a text file.
2. The audit's own I-08-A record establishes the downstream consumer
   (`~/.claude/skills/invest-core/scripts/invest_contracts.py:1130-1142`) **passes
   on `attestation_status == "host_signed"` and verifies no signing entity**. So the
   label is the *only* thing standing between a forged package and a trusted
   formal consumer. That consumer is out of scope here and cannot be patched in
   this repo — which is precisely why the product-side gate is required.

This directly violates card case **A-C2** ("要求可信formal的消费者拒绝") and the
card's failure-stop condition ("只测试验签helper却宣称消费者已接通").

### F2 — receipt layer is hash-consistency only — **CONFIRMED, severity MEDIUM**

Verified independently: after recomputing the three public self-hashes, a mutated
top-level value passes `validate_publication_receipt` and is rejected only by the
strong dispatcher (`CAGR mismatch in low` — a genuine recomputation failure, not an
input-binding failure). All of E2/E5/E6/E8/E9/E10 were re-run by the reviewer and
each rejects for the **correct** gate reason (`validated_payload_sha256 mismatch`,
`validated_input_sha256 mismatch`, `gate_ids mismatch`, `missing field:
publication_receipt`) — no accidental passes.

Severity **medium, not high**: the two public consumers in this repo
(`validate_forecast_output`, and `render_markdown` which calls it at
`revenue_report.py:1278`) do run the strong path. The exposure is that a caller
choosing the plausibly-named `validate_publication_receipt` believes it has
validated a publication when it has only checked hash self-consistency. Keep the
finding; the mitigating fact should be recorded alongside it.

### F3 — `segments[i].base_revenue` is bound by no gate — **CONFIRMED but SCOPE-NARROWED, severity MEDIUM**

The mechanism is real and I reproduced a **material** exploit, but the
implementer's description ("renders into official report tables") understates one
protection and overstates another.

**Verified exploit (reviewer's own construction, not the implementer's test):**
Keep the embedded `input_document`, `input_sha256` and `parameter_trace`
**completely unchanged** (so `verify_input_binding` and
`parameter_trace == data["parameters"]` both pass honestly), inflate only
`segments[0].base_revenue` 100 → 130, rebuild `modeled_activity` with the
production model so the per-segment recomputation gate matches, scale
`recognized_revenue` / `effective_revenue` / the segment bridge to stay coherent,
recompute the public self-hashes:
```
receipt layer     : ACCEPTED
strong dispatcher : ACCEPTED
render_markdown  分部表  ORIGINAL: | Segment A | direct_revenue | 100.00 | …
render_markdown  分部表  FORGED  : | Segment A | direct_revenue | 130.00 | …
```
The forged opening base renders into the official report's segment table. It does
**not** move the company total: `base_revenue` and
`consolidated_forecast[scenario].annual_revenue` remain independently validated by
`_recompute_consolidated_paths` (`revenue_report.py:65-155`), so the reported
company-level base and terminal revenue stay honest. **Impact is confined to the
per-segment opening-base column and per-segment derived figures, not company
totals.**

**Scope narrowing the implementer missed:** the input layer *does* protect the
total. Attempting to inflate the segment base in the input document is caught by
`validate_base_reconciliation` (`contracts/document.py:955`,
`base revenue does not reconcile: segments+adjustments=180.0, reported=150.0`) and
by historical-base reconciliation; a coherent full-story forgery that also moves
the reported total and historicals must change `input_sha256`, which the receipt's
`validated_input_sha256` then rejects. So F3 is a **result-layer coverage gap in a
presentation field**, not an unbound path to a forged company total. Also note the
legacy no-input read path is not an escape hatch: the dispatcher rejects
current-schema artifacts lacking a bound input, and older schema/engine pairs are
not documented compatibility pairs.

Severity **medium** — a wrong per-segment opening base in an official report is a
real integrity defect that survives every gate, and the fix is small (cross-check
`segments[i].base_revenue` against the segment's `base_revenue_parameter_id` /
the embedded input, or fold it into the `incremental_contribution` reconciliation),
but it cannot move company-level revenue.

### F4 — card anchor drift — **CONFIRMED, severity LOW**

`publication_registry.py` was changed by commit `1dbae639` ("feat(ZR-701)"), which
touched the file with `11 +-` after the card froze its anchor
`446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa`; the file now
hashes `29aaae4f9864d9c4dbb92720744daa49315a2980dfa158b0e3666cb86d886344`.
`is_registered` is still at **line 188** (`lookup` at 183) with the same
fail-closed contract, so the card remains executable against the current file.
Correctly reported, not repaired, per scope. **Low.**

---

## Unverified list

1. **invest-\* consumers are unverified** (card-declared out of scope). The
   `attestation_status == "host_signed"` gate in
   `~/.claude/skills/invest-core/scripts/invest_contracts.py:1130-1142` was **not
   executed** by this review — it is cited from the I-08-A decision record as
   read-only evidence. Whether any invest-* consumer performs its own signature or
   issuer verification was not established. I-08-C cannot be closed as covering
   these.
2. **No CLI / transaction entry point was exercised.** F01/F02 are claimed to be
   covered transitively through the dispatcher chain; the reviewer verified the
   dispatcher, not a CLI publish transaction.
3. **The exploratory 8/12 run left no preserved log.** `oracle.md` names the 8
   passing tests in prose, but no stdout file, and `lastfailed` was overwritten to
   `{}` by the verdict run. The claim "8 passed" is corroborated only by the
   18:56:19 cache write and cannot be fully reconstructed.
4. **E4 is absent** from the frozen test file despite being frozen in the oracle
   (see above); its mechanism is covered inside `test_e3` but never independently
   asserted.
5. **`is_registered`'s `RegistryError` fail-closed behaviour** was exercised by
   `test_e12` against a temp registry; the reviewer confirmed the test passes and
   rejects for the right reason, but did not independently corrupt a registry copy
   outside the test harness.

---

## What would close this card

1. **Bind attestation at consumption** (F1, blocking): the label must not be
   accepted on set membership. Either (a) carry the binding record
   (`publication_attestation` with issuer/key/domain, per I-08-A's E27/G4) and
   require it whenever `attestation_status == "host_signed"`, or (b) declare the
   label non-evidentiary and make trusted-formal consumers require an explicit
   verified-signature field. Also fix `attestation_capability()` so existence of a
   file is not treated as signing capability.
2. **Bind `segments[i].base_revenue`** (F3): cross-check it against the segment's
   `base_revenue_parameter_id` in the embedded input, or include it in the
   `incremental_contribution` reconciliation that already runs.
3. **Document or deprecate `validate_publication_receipt`** (F2): state in its
   docstring/API that it is a hash-consistency check and not a security gate, and
   that consumers must call `validate_forecast_output`.
4. Re-freeze the oracle with E4 either implemented or explicitly withdrawn, and
   preserve the exploratory run log.
