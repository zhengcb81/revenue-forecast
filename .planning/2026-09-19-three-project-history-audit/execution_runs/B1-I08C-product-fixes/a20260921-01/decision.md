# B1 — I-08-C product defects REM-01/02/03 — DECISION RECORD

- Plan: `2026-09-19-three-project-history-audit`
- Card: **B1 — I-08-C product defects REM-01/02/03**
- Attempt: `execution_runs/B1-I08C-product-fixes/a20260921-01`
- Implementer: delegated implementer session. **Does not self-sign.** Status is
  `review_pending`; production promotion is a separate owner decision.
- Inputs: `execution_runs/I-08-C/a20260919-01/review.md` (sha256
  `c1a8fd11b20f911c7407943dabe70bc493a9cb2959719c13beef21f8e7f1f2a3`) and
  `handoff.json`; design provenance
  `execution_runs/I-08-A/a20260919-01/decision.md` (§2.4 R-PROV-1, §2.5 code
  table, §3 trust domain, §4 payload/signature, §6.1-6.2 G3a/G3b/G4, §7.1).

---

## 1. What this card is and is not

**Is.** A product-side fix for the three defects the I-08-C independent reviewer
confirmed (F1 → REM-01, F2 → REM-02, F3 → REM-03), implemented **only** in an
isolated copy of the production tree.

**Is not.** It does not re-open I-08-C, does not close I-08-C, does not claim
`accepted`, and does not touch production. No file under
`C:\Users\郑曾波\Projects\revenue-forecast` (outside this attempt directory) was
written. `disclosure_adaptation = unmapped`; `accuracy = unproven`.

---

## 2. The three fixes

### REM-01 — `attestation_status="host_signed"` is now evidentiary (HIGH)

Two mechanisms, both fixed, both proven at a **consumer entry point**.

**(a) The label is bound to a verifying record.**
`revenue_publication.validate_publication_attestation` (new) is called from
`validate_publication_receipt`, and enforces:

- `attestation_status == "host_signed"` with **no** `publication_attestation`
  record ⇒ rejected with `attestation_missing_record` (I-08-A **E27**, G3b).
  Never silently downgraded to `unattested`.
- a record that **is** present is always verified, even when the label is
  `unattested` — a record can never be present-but-ignored.
- the record's field set is **closed** (extra or missing key ⇒ reject), the
  domain separator is the frozen `revenue-forecast/publication-attestation/v1`,
  `fingerprint`/`request_id`/`signature` have frozen formats, `payload_sha256`
  must equal the receipt's `validated_payload_sha256`, and the **Ed25519
  signature must verify** against a fingerprint in the trust domain over the
  reconstructed request object.
- `build_publication_receipt(..., attestation_status="host_signed")` **without**
  a record fails closed, so the label cannot be minted through the builder either.

**(b) File existence is no longer capability.**
`revenue_core.attestation_capability()` now performs a bounded one-shot provider
handshake (one JSON request on stdin, one JSON object on stdout, exact field set,
byte-identical echo of `request_id`/`payload_sha256`/`domain_separator`, trust-
domain fingerprint, verified Ed25519 signature over the request) and returns
`False` on every failure path. `run_forecast` sets `host_signed` **only** when
that handshake returned a record; otherwise it publishes an honest `unattested`
artifact. A failure reason is exposed by the read-only diagnostic
`attestation_last_failure()` and carries the I-08-A code.

Frozen negative results now GREEN: a 5-byte `.txt`, a bare `.py`, and
`sys.executable` each yield capability `False`, `attestation_status ==
"unattested"`, and **no** record. A provider whose key is not in the trust domain
yields `provider_key_untrusted` and stays `unattested`.

### REM-02 — the receipt layer is documented as non-security (MEDIUM)

`validate_publication_receipt`'s docstring now states in literal terms that it is
a hash-consistency check and **NOT a security boundary**, explains exactly what
it does and does not check, and names
**`revenue_report.validate_forecast_output`** as the function consumers must
call. The module docstring says the same, and an exported marker class
`PublicationReceiptOnlyWarning(UserWarning)` carries the limitation into the API
surface.

**Decision, stated explicitly: no behaviour change and no runtime warning.**
The oracle froze this (r1 §3.5(c)): `_validate_receipt_blocks`
(`revenue_report.py:258`) calls this function on **every** strong validation, so
a `DeprecationWarning` there would be pure noise, and the documented limitation
is what the reviewer asked for ("document or deprecate"). A self-consistent
forgery still passes this function — that is the disclosed limitation, not an
unfinished fix.

### REM-03 — `segments[i].base_revenue` is now bound (MEDIUM)

New `revenue_report._validate_segment_opening_bases`, called from
`_validate_forecast_output`, runs two gates on pre-existing fields only:

- **per-segment identity**: the segment's `base_revenue_parameter_id` must
  resolve in `parameter_trace` to a revenue-dimension parameter for `base_year`
  whose value equals `segments[i].base_revenue` (same lookup the engine performs
  in `forecast/segments.py:141`). Failure: `segment base revenue mismatch`.
- **opening-base reconciliation**: `sum(segments[i].base_revenue)` must equal
  `result["base_revenue"]` within the declared `reconciliation_tolerance`
  (default `1e-6`, the same default as `contracts/document.py:950`). Failure:
  `segment opening base does not reconcile`.

The reviewer's exploit — inflate only `segments[0].base_revenue`, leave
`input_document`/`input_sha256`/`parameter_trace` untouched, recompute all three
public self-hashes — is now rejected with
`segment base revenue mismatch: Segment A opening base 1100.0 does not match
segment_a_base (100)`.

**Scope, adopted from the reviewer's narrowing and NOT re-widened.** Company
totals were never forgeable through this path
(`_recompute_consolidated_paths`, `revenue_report.py:65-155`) and partial forgery
was already blocked by `validate_base_reconciliation`
(`contracts/document.py:955`). This fix closes the **per-segment presentation
column of the official 分部表**, nothing more.

---

## 3. Design provenance and the one place this deviates from I-08-A

The I-08-A decision record froze the target design. This card implements a
**deliberately reduced** subset and says so:

| I-08-A item | Here |
|---|---|
| §2.5 code spellings (E12/E13/E14/E16/E17/E20/E21/E26/E27) | adopted **verbatim** in the raised messages and in `attestation_last_failure()` |
| §2.4 hard rule **R-PROV-1** (existence/executability/`.py`/`sys.executable` is never capability) | implemented |
| §3 trust-domain identity triple (`issuer` + `key_id` + `fingerprint`) | implemented over the **existing** loader `contracts/evidence._trusted_signer_public_keys()` |
| §4.3 signature object construction (`canonical_sha256(payload).encode("ascii")`) | implemented identically |
| §6.1/§6.2 G3a / G3b / E27 | implemented (E26 = legal, kept; E27 = reject) |
| §3 12-field trust-domain entry schema, E25 fail-loud loading, `not_before`/`not_after`/`status`/`revoked_at`/`environment`, **E24** test-key rejection | **NOT implemented** — recorded open (§6) |
| §5 replay window `issued_at`/`expires_at`/`W` (E18), `request_id` reuse ledger (E19) | **NOT implemented** — recorded open (§6) |
| §2.3 full `attestation_response` schema | reduced to the 10-field record §3.4 set — deviation disclosed in oracle r3 |

**The one real design deviation, disclosed.** The attestation record carries
**10** fields, not the 12 r1 first froze. Two were removed because they are
mutually unsatisfiable with a receipt that contains the record:

- `receipt_sha256` — a receipt cannot contain its own hash (`receipt_sha256 =
  canonical_sha256(receipt without that field)`); there is no fixpoint. The
  production design already excludes `publication_receipt` from
  `validated_payload_sha256` for exactly this reason.
- `result_sha256` — `result_sha256` covers the whole result **including** the
  receipt, and the receipt contains the record, so citing it inside the record is
  the same fixpoint one level up.

Neither removal leaves anything unbound: the signed request binds the payload
digest (everything except `result_sha256` and `publication_receipt`) and the
one-shot `request_id`, and `validated_payload_sha256` / `verification_context_sha256`
/ `receipt_sha256` cover the rest. The signature is verified over a request
**reconstructed from the record's own fields**, so a signature cannot be moved
onto a different payload or request. Both removals are frozen in `oracle.md`
revision r3 (`scratch/oracle_revision_r3.md`) with an append-only proof; the r1
body is byte-untouched (27697 bytes,
`81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281`).

**Second deviation, disclosed.** The r2 RED run showed the r1 oracle marked node
R8 as RED on the unfixed tree, but R8's assertion as first written passed
trivially there (the label is set from a boolean, so `host_signed` appears with
no record and the old validators accept it). R8 was **strengthened** to assert
the record's presence and field set — which is what r1's own prose already
required — and the r1 RED stdout is preserved un-overwritten as
`before/b1_unfixed.*`. Frozen in `oracle.md` revision r2.

---

## 4. Owner / professional-review items this card does NOT decide

1. **The invest-core consumer** (`~/.claude/skills/invest-core/scripts/
   invest_contracts.py:1130-1142`) is a different repo, was **not touched and not
   executed**, and is the decisive consumer for REM-01. The label is now bound in
   this repo; whether that consumer verifies the binding is unverified. **Subject
   to a separate card and that repo's owner.**
2. **Cross-repo contract change.** `publication_receipt` gains a
   `publication_attestation` sub-object and `host_signed` receipts without one are
   now rejected. That changes the publication contract for every consumer. This
   card implements it under the I-08-A mandate; the **consumer-side rollout is an
   owner decision**, not this card's.
3. **Production trust anchor.** `config/trusted_signer_public_keys.json` stays
   **absent**, so in production `attestation_capability()` is `False` and all
   publications are `unattested`. Adding a trust anchor is a capability grant
   (I-08-A R-PROV-2) and is explicitly not done here.
4. **Provider parameters `T` and `L`.** I-08-A OPEN-D7 owns their values. The
   implementation uses `T = 10.0 s` and `L = 65536` bytes, recorded in
   `binding.json` and **not** claimed as normative.
5. **`test_attestation.py::test_configured_provider_means_host_signed_publication`**
   is now RED on the fixed tree. This is the false-green source I-08-A §7.1
   identified by name and required to be broken before the new semantics land;
   rewriting it is I-08-B's item, and its expected failure reason is the frozen
   E32 (`provider_capability_unproven`), observed here as
   `attestation_capability() is False`.
6. **`I-08-C/test_i08c_consumer_rejection.py::test_e11` and `::test_e13`** now
   FAIL on the fixed tree. Those two nodes are the gap *pins* (rc=3 business
   verdicts), so the fix must necessarily invalidate them. Measured on the
   unfixed tree they still pass 13/13 (`before/i08c13_unfixed.*`); on the fixed
   tree they fail. A reviewer should treat this as expected and require the
   I-08-C oracle to be re-frozen — **not** as a regression.

---

## 5. Measured results

### 5.1 RED → GREEN

| run | tree | result | raw rc |
|---|---|---|---|
| pre-change probe | `iso/rf` | all three defects reproduce | 0 |
| RED r1 (`before/b1_unfixed`) | `iso/rf` | 10 failed / 2 passed | 1 |
| RED r2 (`before/b1_unfixed_r2`) | `iso/rf` | 11 failed / 1 passed | 1 |
| RED r3, final test revision (`before/b1_unfixed_r3`) | `iso/rf` | 11 failed / 1 passed | 1 |
| **GREEN** (`after/b1_fixed`) | `iso/fixed/rf` | **12 passed** | **0** |
| post-change probe | `iso/fixed/rf` | P1/P3 rejected, P2 all `unattested`, P4 documented | 0 |

The one node GREEN on the unfixed tree is
`test_rem03_honest_package_still_accepted`, the deliberate positive control.

### 5.2 Mutation proof — every fix is load-bearing, and the proofs isolate

Each mutation is a single exact literal revert applied to a fresh copy of the
fixed tree; the **same** frozen test file is then run and the observed red set is
required to equal the declared red set **exactly** (no missing red, no extra red).

| mutation | reverted fix | declared = observed red set | isolated |
|---|---|---|---|
| M1 | `host_signed` requires a verifying record | R1, R7 | yes |
| M2 | file existence is not signing capability | R2×3, R6 | yes |
| M3 | `segments[i].base_revenue` bound by a gate | R10, R12 | yes |
| M4 | REM-02 non-security documentation | R9 | yes |
| M5 | a present record is actually verified | R7 | yes |

Two of those nodes are **declared dependencies**, reported rather than smoothed
over: R7 is red under M1 because M1 reverts the whole record check (not just
E27); R6 is red under M2 because R6 also asserts the failure *code*
`provider_key_untrusted`, and file-existence capability never reaches the trust
check. The capability nodes stay green under M1 and the consumption-side nodes
stay green under M2, which is the evidence that the two halves of REM-01 are
independently load-bearing.

**Disclosed harness incident.** The first M1 run declared R7 as must-stay-green
and reported it as collateral. Investigating showed M1 genuinely removes both
record checks, so the declaration was wrong, not the observation; R7 was moved to
M1's declared-red set. The R7 node itself was also strengthened from one
conflated case into two separately asserted attacker moves (oracle revision r4)
so that this question could be asked narrowly. Superseded runs are not deleted:
the corrected measurement is `scratch/mutations/mutation_proof.json`.

### 5.3 No collateral breakage

100 production tests across 11 modules that exercise the publication, attestation
and report surface: **100 pass before**, **99 pass + 1 expected failure after**.
The single failure is
`tests/test_attestation.py::AttestationTests::test_configured_provider_means_host_signed_publication`
— the repo's only false-green source, named by I-08-A §7.1 as the test that MUST
break before the new semantics land. It fails with
`AssertionError: False is not true` on `attestation_capability()`, i.e. exactly
the frozen E32 behaviour.

`tests/test_zr907_drift_patrol.py` could not be collected in **either** tree
(`No module named 'drift_patrol'`) — pre-existing, unrelated, excluded rather
than counted as a pass.

## 6. Evidence map

| claim | evidence |
|---|---|
| defects reproduce pre-change | `before/probe_unfixed.txt` |
| defects closed post-change | `after/probe_fixed.txt` |
| RED (pre-change) node outcomes | `before/b1_unfixed.*` (r1), `before/b1_unfixed_r2.*` (r2), `before/b1_unfixed_r3.*` (final test revision) |
| GREEN (post-change) node outcomes | `after/b1_fixed.*` (12 passed, rc 0) |
| no collateral breakage | `before/suite_unfixed.*` (100 passed) vs `after/suite_fixed.*` (99 passed, 1 expected false-green failure) |
| each fix is load-bearing | `scratch/mutations/M1..M5/**` + `scratch/mutations/mutation_proof.json` |
| oracle frozen before running | `oracle.md` (r1) + `scratch/append_oracle_r{2,3,4}.stdout.json` |
| production untouched | `after/production_status.txt` |
| isolated copies are byte-identical to production pre-fix | `before/iso_tree_manifest.json`, `binding.json` |
| final artifact hashes | `after/frozen_artifacts_r3.json` |

---

## 7. Explicitly not closed (must not be read as coverage)

1. invest-core consumer — unverified, different repo.
2. No CLI / transaction entry point exercised; coverage is the dispatcher chain.
3. I-08-A full provider protocol: E18 (replay window/`W`), E19 (`request_id`
   reuse ledger), E22 (`key_outside_validity_window`), E23 (`key_revoked`), E24
   (test key in production trust domain), E25 (fail-loud trust-domain loading),
   E29 (opt-in schema bypass), and the L1/L2/L3 three-layer proof domain are
   **NOT implemented**.
4. `validate_publication_receipt` still accepts a fully recomputed forgery — by
   design, documented.
5. I-08-C is still `changes_required`; this card supplies product-side fixes for
   review and cannot close it.
6. Forecast accuracy and disclosure adaptation: untouched and unproven.
