# B1 — I-08-C product defects REM-01/02/03 — FROZEN ORACLE (r1)

- Plan: `2026-09-19-three-project-history-audit`
- Card: **B1 — I-08-C product defects REM-01/02/03**
- Attempt: `execution_runs/B1-I08C-product-fixes/a20260921-01`
- Implementer: delegated implementer session (**does NOT self-sign accepted**)
- Source of the three defects: `execution_runs/I-08-C/a20260919-01/review.md`
  sha256 `c1a8fd11b20f911c7407943dabe70bc493a9cb2959719c13beef21f8e7f1f2a3`
  and `execution_runs/I-08-C/a20260919-01/handoff.json`
- Isolation: this oracle is frozen **BEFORE** the pre-change (RED) run. No test
  file, no iso copy, and no production file has been executed for this card at
  the moment of freezing. Frozen-at hash is recorded in `binding.json`.

## 0. Scope, boundaries, and what this oracle does NOT claim

- **Production repos are READ-ONLY.** The entire fix lives in the isolated copy
  `<ATTEMPT>/iso/rf/` (pre-change) and `<ATTEMPT>/iso/fixed/rf/` (post-change).
  No file under `C:\Users\郑曾波\Projects\revenue-forecast` is written by this
  card. Production promotion is a **separate owner decision**.
- `disclosure_adaptation = unmapped`, `accuracy = unproven`. Nothing here is
  evidence of forecast accuracy or of disclosure adaptation.
- Failure-stop condition inherited from I-08-C: **"只测试验签helper却宣称消费者
  已接通"** (testing only the signature helper while claiming the consumer is
  wired). Every expectation below is therefore asserted at a **consumer entry
  point** (`validate_publication_receipt` / `validate_forecast_output`), never
  on a helper alone. Where a helper is asserted it is explicitly labelled
  *issuance-side* and is never presented as consumption-side evidence.
- Nothing here is self-signed: no `accepted` status is written by this card.

## 1. Baseline anchors (hashed BEFORE any run; full table in `before/production_anchors.json`)

| file | sha256 | bytes |
|---|---|---|
| `scripts/revenue_publication.py` | `183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba` | 10681 |
| `scripts/revenue_core.py` | `1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae` | 14136 |
| `scripts/revenue_report.py` | `a85fb48482216dca3f9269ee81b6d8204f419b454b64aaac14412151f00d971f` | 69765 |
| `scripts/contracts/evidence.py` | `054e364a7a5c428f43c6378f795429751b26f24af8de07e22da4b3d0ac8a4561` | 15232 |
| `scripts/publication_registry.py` | `29aaae4f9864d9c4dbb92720744daa49315a2980dfa158b0e3666cb86d886344` | 10599 |
| `artifacts/registry/publications.jsonl` | `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91` | 46369 |
| `config/trusted_signer_public_keys.json` | **ABSENT** | — |

`config/trusted_signer_public_keys.json` **does not exist** in production. That
is the correct fail-closed default (zero trusted signers) and it is preserved in
the iso copy: the iso tree therefore also has zero trusted signers unless a test
points `REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS` at an isolated fixture.

## 2. Defect restatement (what is frozen as FAILING before the fix)

### REM-01 (HIGH) — `attestation_status="host_signed"` is a plain label
Mechanism frozen from `review.md` F1:
- `revenue_core.py:167` sets the label from a boolean.
- `revenue_core.py:113-125` `attestation_capability()` returns True for **any
  path that exists as a file** — no key, no issuer, no signature, no provider
  invocation.
- `revenue_publication.py:222-226` consumes the label by **set membership only**.
- Reviewer's material proof (must reproduce): point
  `REVENUE_ATTESTATION_PROVIDER` at a 5-byte plain `.txt` ⇒ capability True ⇒
  formal publication stamped `host_signed` with **no signature or issuer field**
  ⇒ the strong dispatcher **ACCEPTS** it.

### REM-02 (MEDIUM) — `validate_publication_receipt` is hash-consistency only
It recomputes self-hashes and checks `gate_ids` / `verification_context_sha256`
deterministically from the receipt+payload, so a fully-recomputed forgery passes
it. It is not a security boundary. Frozen consequence (from `review.md` F2):
both public consumers in this repo already run the strong path, so severity is
medium: the exposure is a **caller who believes this function is a gate**.

### REM-03 (MEDIUM) — `segments[i].base_revenue` bound by no output gate
Frozen scope-narrowing from `review.md` F3 (the reviewer's narrowing is adopted
verbatim, not re-widened):
- company totals do **not** move (`_recompute_consolidated_paths`,
  `revenue_report.py:65-155`);
- partial forgery **is** already blocked by `validate_base_reconciliation`
  (`contracts/document.py:955`);
- the gap is a **presentation-field coverage gap**: a self-consistent forgery of
  `segments[0].base_revenue` is accepted by the receipt layer AND the strong
  dispatcher and renders into the official 分部表 (`render_markdown`,
  `revenue_report.py:1461`).
This oracle therefore claims only: **the per-segment opening-base column becomes
bound.** It does NOT claim company totals were ever forgeable.

## 3. FROZEN TARGET DESIGN (r1) — the contract the fix must implement

### 3.1 New receipt sub-object `publication_receipt["publication_attestation"]`

Field set is **closed and exact** (extra or missing key ⇒ reject). Frozen now:

```
publication_attestation = {
  "attestation_payload_schema_version": "1.0",
  "domain_separator":  "revenue-forecast/publication-attestation/v1",
  "issuer":            <str, non-empty>,
  "key_id":            <str, non-empty>,
  "algorithm":         "ed25519",
  "fingerprint":       <32 lowercase hex>,
  "request_id":        <64 lowercase hex>,
  "payload_sha256":    <64 lowercase hex>,   # == receipt["validated_payload_sha256"]
  "result_sha256":     <64 lowercase hex>,
  "receipt_sha256":    <64 lowercase hex>,
  "signed_at":         <RFC3339 UTC 'Z', second precision>,
  "signature":         <128 lowercase hex>,
}
```

- Provenance: this is a **deliberately reduced** subset of the I-08-A §4.2 L3
  payload (`execution_runs/I-08-A/a20260919-01/decision.md` §4.2). The I-08-A
  frozen identity triple `{issuer, key_id, fingerprint}` plus the frozen
  `domain_separator` string are adopted **verbatim**; `request_id` is adopted as
  the frozen 64-hex one-shot nonce; `signature_algorithm` is renamed to
  `algorithm` for internal consistency with the trust-domain entry field name.
  The I-08-A fields `expires_at`, `issued_at`, `input_sha256`,
  `engine_version`, `forecast_schema_version`,
  `publication_receipt_schema_version`, `validator_version`, `gate_ids` are
  **NOT** included. Reason, frozen here so it cannot be quietly widened later:
  `input_sha256`, the version fields and `gate_ids` are **already bound** by
  `validated_input_sha256` + `verification_context_sha256` +
  `validated_payload_sha256` in the receipt, and re-binding them inside the
  signature adds no property this card must prove while multiplying the fields
  that must match byte-for-byte. The **replay window semantics** (`issued_at` /
  `expires_at` / `W`, I-08-A §5) and the full provider protocol (I-08-A §2.3
  `attestation_response` schema `1.0`) remain **I-08-A scope, NOT implemented
  here** — §7 lists them as explicitly not-closed.
- **Binding rule (REM-01(a))**: `attestation_status == "host_signed"` **REQUIRES**
  a valid `publication_attestation`. A `host_signed` receipt with the key absent,
  `None`, or non-dict ⇒ **REJECT** with
  `attestation_missing_record (E27)`; **never** silently downgrade to
  `unattested`.
- Whenever `publication_attestation` **is present** (even with
  `attestation_status == "unattested"`), it must be structurally valid, and its
  `payload_sha256` / `result_sha256` / `receipt_sha256` must match the live
  values ⇒ otherwise **REJECT**. A record that does not verify must never be
  present-but-ignored.
- `attestation_status == "unattested"` **with the key absent** is legal and
  accepted (G3a, `attestation_absent (E26)`) — the honest unattested package
  stays consumable by this repo's consumers, exactly as today. This card does
  **not** add a "trusted-formal consumers must reject unattested" gate; that is
  a consumer-policy decision belonging to the invest-core owner.

### 3.2 `attestation_capability()` semantics (REM-01(b))
Frozen: capability is **NOT** file existence. It is True **iff all** hold:
1. `REVENUE_ATTESTATION_PROVIDER` is set and resolves to an existing file
   (bare name via `shutil.which`, else expanded absolute path); and
2. a **bounded one-shot handshake** with that provider succeeds: the provider is
   spawned as a subprocess, receives exactly one JSON request object on stdin,
   and returns exactly one JSON object on stdout within the bound; and
3. the handshake response's identity is **trusted**: its `fingerprint` resolves
   in the trust domain (I-08-A §3), its `issuer` equals that entry's `issuer`,
   `key_id` equals that entry's `key_id`, and its Ed25519 `signature` verifies
   over the canonical hash of the echoed request; and
4. the response echoes `request_id` and `payload_sha256` **byte-for-byte**.

Consequences frozen as expectations: a plain `.txt`, a bare `.py`, and
`sys.executable` all yield capability **False** and publication
`attestation_status == "unattested"`. The provider file is **never read,
imported, or executed as a script** by the host — it is only spawned; if the
resolved path does not exist, it is not spawned at all.

Trust-domain loading for this card uses the **existing** loader
`contracts/evidence._trusted_signer_public_keys()` (`config/public_keys` style,
`REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS` override). The I-08-A §3 12-field frozen
entry schema (`not_before`/`not_after`/`status`/`revoked_at`/`environment` +
E25 fail-loud loading) is **I-08-A scope and NOT implemented here**; §7 records
it as not-closed. `config/trusted_signer_public_keys.json` is ABSENT in both the
production tree and the iso copy, so the default is zero trusted signers.

### 3.3 Issuance path (`run_forecast`, formal mode)
Frozen order, preserving the existing protective freezes (I-08-A §7 items 1-2):
`_build_forecast_draft` → `validate_published_forecast` → build provider request
→ provider handshake → assemble `publication_attestation` → build receipt with
`attestation_status` → `validate_publication_receipt` → register.

- **Fail closed on signing failure**: any handshake/signature/trust failure ⇒
  `attestation_status = "unattested"` and `publication_attestation` **absent**.
  The publication still succeeds (it is an honest unattested publication), and a
  structured reason is recorded in `result["attestation_failure"]` with
  `{"code": <E-code>, "message": <str>}`. A failure must **never** produce
  `host_signed` and must **never** produce a partial record.
- On success the record's `payload_sha256` equals the receipt's
  `validated_payload_sha256`, and the signed message is
  `canonical_sha256(payload).encode("ascii")` where `payload` is the request
  object — the same construction as the existing `_validate_host_signature`
  (`contracts/evidence.py:296-304`).

### 3.4 Provider protocol v1 (the exact wire contract frozen for this card)
**Request** (host → provider stdin, one JSON object, then stdin closed):

```
{
  "attestation_request_schema_version": "1.0",
  "domain_separator": "revenue-forecast/publication-attestation/v1",
  "request_id":     <64 lowercase hex>,
  "payload_sha256": <64 lowercase hex>,
  "result_sha256":  <64 lowercase hex>,
  "receipt_sha256": <64 lowercase hex>,
  "canonical_payload_sha256": <64 lowercase hex>   # == payload_sha256; explicit signing target
}
```

**Response** (provider stdout → host, exactly one JSON object, no trailing junk):

```
{
  "attestation_response_schema_version": "1.0",
  "request_id":     "<echo, byte-identical>",
  "payload_sha256": "<echo, byte-identical>",
  "domain_separator": "<echo, byte-identical>",
  "issuer":         "<str, non-empty>",
  "key_id":         "<str, non-empty>",
  "fingerprint":    "<32 lowercase hex>",
  "algorithm":      "ed25519",
  "signature":      "<128 lowercase hex>",
  "signed_at":      "<RFC3339 UTC 'Z'>"
}
```

Failure codes used by this card (subset of the I-08-A §2.5 table, same
spelling; the numbering is I-08-A's and is referenced, not re-invented):

| code | name | condition |
|---|---|---|
| E01 | `provider_absent` | env var unset |
| E02 | `provider_path_unopenable` | path does not exist as a file; **not spawned** |
| E03 | `provider_protocol_violation` | no JSON object on stdout, or trailing junk, or empty stdout |
| E04 | `provider_invalid_json` | stdout not parseable as JSON |
| E05 | `provider_exit_nonzero` | exit code != 0 |
| E06 | `provider_output_too_large` | stdout exceeds the output bound; truncated prefix **never** parsed |
| E07 | `provider_timeout` | provider exceeded the timeout; child terminated |
| E08 | `provider_schema_mismatch` | response key set is not exactly the frozen set, or a field has the wrong type/format |
| E09 | `provider_binding_mismatch` | `request_id` / `payload_sha256` / `domain_separator` echo not byte-identical |
| E10 | `provider_signing_unavailable` | provider explicitly reports it cannot sign |
| E20 | `provider_key_untrusted` | fingerprint not in the trust domain |
| E21 | `issuer_key_binding_mismatch` | `issuer` != the trust-domain entry's `issuer`, or `key_id` mismatch |
| E12 | `attestation_missing_signature` | attested record has no `signature` field |
| E13 | `attestation_malformed_signature` | signature not exactly 128 lowercase hex |
| E14 | `attestation_signature_invalid` | Ed25519 verification failed |
| E16 | `attestation_payload_hash_mismatch` | record's `payload_sha256`/`result_sha256`/`receipt_sha256` != live values |
| E17 | `attestation_domain_mismatch` | record's `domain_separator` != the current domain |
| E27 | `attestation_missing_record` | `attestation_status == "host_signed"` but no `publication_attestation` |
| E26 | `attestation_absent` | current-schema package makes no signing claim (legal, kept) |

The numeric bound `L` (stdout cap) and `T` (timeout) are **parameters, not
frozen values** (I-08-A OPEN-D7). This card therefore freezes only that a bound
exists and that exceeding it is E06/E07; the two concrete values used are
recorded in `binding.json` and are **not** claimed as normative.

### 3.5 REM-02 frozen target
`validate_publication_receipt` must state, in its own docstring **and** in the
raised-error path, that it is a **hash-consistency check and NOT a security
boundary**, and that consumers must call `validate_forecast_output`. Frozen
expectations: (a) the docstring contains both literal phrases `NOT a security
boundary` and `validate_forecast_output`; (b) an explicit
`PublicationReceiptOnlyWarning`-class marker is exported and named in the
docstring; (c) the function emits `DeprecationWarning`? **NO** — frozen decision:
**do not** emit a runtime warning, because existing production call sites
(`revenue_report.py:258` inside `_validate_receipt_blocks`) call it on every
strong validation and a warning there would be noise, and `test_zr701` /
`test_zr705` assert clean runs. The documentation + exported marker is the
deliverable; **no behaviour change** is frozen for REM-02. (c') Consequently the
REM-02 test asserts documentation and marker, not a raised exception.

### 3.6 REM-03 frozen target — two new gates inside `_validate_forecast_output`
Applied to the **pre-existing fields only** (no new result field is introduced,
so the payload hash domain is unchanged for honest artifacts):

**G-A (per-segment bind).** For each `result["segments"][i]` that carries a
`base_revenue_parameter_id`, the `parameter_trace` entry with that
`parameter_id` must exist, have `dimension == "revenue"`, have
`period == f"FY{base_year}"`, and have
`math.isclose(value, segments[i].base_revenue, rel_tol=1e-9, abs_tol=1e-9)`.
Failure message (frozen substring): `segment base revenue mismatch`.

**G-B (opening-base reconciliation).** With
`adjustment_tolerance = float(result.get("reconciliation_tolerance", 1e-6))`:

```
|sum(segments[i].base_revenue) - result["base_revenue"]| <= max(1.0, |result["base_revenue"]|) * adjustment_tolerance
```

Failure message (frozen substring): `segment opening base does not reconcile`.
Frozen rationale for using only segments (not adjustments): the result does not
expose the base-adjustment set, and widening the result schema would change the
signed payload domain for honest artifacts. The segments-only sum is the
stronger **presentation** claim and is exact whenever
`base_adjustment_parameter_ids` is empty (true for the fixture and for any
single-entity forecast); when a base adjustment is present the tolerance test
above still holds *within that tolerance* only if adjustments are zero, so
`G-B` is frozen as conditional on `abs(sum - base) <= tolerance` **OR** the
result declaring base adjustments — **decision frozen as: no conditional**. If
the fixture shows a non-zero base adjustment, G-B is relaxed to a documented
`require` that is skipped only when
`result.get("base_adjustment_parameter_ids")` is non-empty, and that skip must
be recorded in `decision.md` as a stated limitation. The RED run resolves which
branch applies.

**G-C (parameter-identity bind, from G-A).** In addition, the parameter id must
resolve in **both** `parameter_trace` and (when `input_document` is embedded)
`input_document["parameters"]`; a divergence between the two is already an
error via `verify_input_binding`, so G-A's lookup target is `parameter_trace`,
which `_validate_forecast_output` already requires to equal the validated input
parameters under the strong path (`revenue_report.py:294-297`).

Frozen exploit that MUST be rejected after the fix (the reviewer's F3
construction, adopted): keep `input_document`, `input_sha256` and
`parameter_trace` **completely unchanged**, inflate only
`segments[0].base_revenue` by +1000, rebuild nothing else, recompute the three
public self-hashes (`validated_payload_sha256`, `receipt_sha256`,
`result_sha256`):

- BEFORE: `validate_publication_receipt` ACCEPTS, `validate_forecast_output`
  ACCEPTS, `render_markdown` 分部表 prints the inflated opening base.
- AFTER: `validate_publication_receipt` **ACCEPTS** (REM-02 is documentation
  only, by design), `validate_forecast_output` **REJECTS** with
  `segment base revenue mismatch`.

## 4. Frozen case matrix

`iso/rf` = unfixed isolated copy (byte-identical to production, hashes in
`before/iso_tree_manifest.json` and `binding.json`). `iso/fixed/rf` = fixed
isolated copy. `before/` and `after/` hold the raw stdout of each run.

| # | node | input | FROZEN expectation BEFORE (iso/rf) | FROZEN expectation AFTER (iso/fixed/rf) | rc |
|---|---|---|---|---|---|
| R1 | `test_rem01_a_label_only_flip_is_rejected` | honest `unattested` package, label flipped to `host_signed`, self-hashes recomputed | **FAIL** — both layers ACCEPT the flip (`validate_publication_receipt` passes, `validate_forecast_output` passes) | **PASS** — `validate_publication_receipt` raises `attestation_missing_record`, `validate_forecast_output` raises | 3 → 0 |
| R2 | `test_rem01_b_plain_txt_provider_grants_no_capability` | 5-byte plain `.txt` as `REVENUE_ATTESTATION_PROVIDER`, formal `run_forecast` | **FAIL** — `attestation_capability() is True` and receipt stamped `host_signed` with no attestation record | **PASS** — capability is `False`, label is `unattested`, no record, `validate_forecast_output` accepts (honest unattested) | 3 → 0 |
| R3 | `test_rem01_c_bare_py_provider_grants_no_capability` | a bare `.py` file with **no protocol response** as provider | **FAIL** — capability `True`, label `host_signed`, no record | **PASS** — capability `False`, label `unattested` | 3 → 0 |
| R4 | `test_rem01_d_sys_executable_grants_no_capability` | `sys.executable` as provider | **FAIL** — capability `True`, label `host_signed`, no record | **PASS** — capability `False`, label `unattested` | 3 → 0 |
| R5 | `test_rem01_e_trusted_provider_yields_verifiable_record` | isolated fake provider holding an Ed25519 key whose **public** half is in an **isolated** trust file (`REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS`) | **FAIL** — label may be `host_signed` but the receipt carries **no** `publication_attestation` (`KeyError`/absent) | **PASS** — label `host_signed`; record present; exact field set; signature verifies; `validate_publication_receipt` and `validate_forecast_output` accept | 3 → 0 |
| R6 | `test_rem01_f_untrusted_provider_is_not_host_signed` | same provider but trust file **absent/unrelated** | **FAIL** — label `host_signed` (existence only) | **PASS** — label `unattested`, no record, `attestation_failure.code == "provider_key_untrusted"` | 3 → 0 |
| R7 | `test_rem01_g_record_is_replay_bound` | trusted signed package; payload mutated (a bound field) with all self-hashes recomputed, record kept | **FAIL** — no record exists to test | **PASS** — rejected (`attestation_payload_hash_mismatch` or `attestation_signature_invalid`) | 3 → 0 |
| R8 | `test_rem01_h_honest_signed_read_is_repeatable_and_label_preserved` | trusted signed package read twice | **FAIL** — no record | **PASS** — both reads accept; label unchanged; no nonce consumption between reads (R-REPLAY-1) | 3 → 0 |
| R9 | `test_rem02_receipt_layer_is_documented_as_non_security` | source text of `revenue_publication.validate_publication_receipt` + module export set | **FAIL** — no `NOT a security boundary` statement, no exported marker | **PASS** — docstring states non-security and names `validate_forecast_output`; marker exported | 3 → 0 |
| R10 | `test_rem03_forged_segment_base_revenue_is_rejected` | honest package; `segments[0].base_revenue` += 1000; self-hashes recomputed; input/parameter_trace untouched | **FAIL** — `validate_forecast_output` ACCEPTS the forgery | **PASS** — `validate_forecast_output` rejects with `segment base revenue mismatch` | 3 → 0 |
| R11 | `test_rem03_honest_package_still_accepted` | honest formal package | **PASS** | **PASS** (no regression) | 0 → 0 |
| R12 | `test_rem03_gate_b_accepts_consistent_and_rejects_inconsistent_totals` | (a) honest package; (b) `segments[0].base_revenue` moved by +1000 with `result["base_revenue"]` moved by +1000 too | **FAIL** — (b) ACCEPTED | **PASS** — (a) accepted; (b) rejected (G-A) | 3 → 0 |

Notes that make the matrix falsifiable rather than decorative:

- R2/R3/R4 assert **both** the issuance side (`attestation_capability()` and the
  emitted label) **and** the consumption side (`validate_forecast_output`), so
  passing them cannot be mistaken for "helper-only" evidence.
- R1 is the direct statement of card case A-C2 on the product: the label must
  not be accepted on set membership.
- R10/REM-03 is asserted **only** about the per-segment presentation field. The
  oracle explicitly does **not** claim company totals were forgeable (§2 REM-03).
- R12(b) is expected to be rejected by **G-A** (per-segment bind) before G-B can
  be reached; if it is rejected by G-B's message instead, that is **still
  PASS** for the security property but must be reported as a deviation from the
  frozen *mechanism*, not silently accepted.

## 5. Frozen mutation proof (revert-each-fix ⇒ that test goes RED)

Each fix gets an isolated revert; the reverted tree must make **its own** test
RED and must leave the other fixes' tests GREEN (isolation of the proof).
Reverts are produced by hash-addressed patch application in a scratch tree, not
by hand-editing the fixed tree.

| mutation | revert target | must go RED | must stay GREEN |
|---|---|---|---|
| M1 | drop the `host_signed` ⇒ record-required gate from `validate_publication_receipt` | R1 (and R7/R10 unaffected) | R5, R11 — and R2/R3/R4 must stay PASS because they assert the *issuance* side which M1 does not touch |
| M2 | restore `attestation_capability()` to file-existence semantics | R2, R3, R4 | R1, R5 — note M2 alone does **not** re-open R1 |
| M3 | drop `G-A` (per-segment base bind) from `revenue_report` | R10, R12 | R1, R5, R11 |
| M4 | remove the REM-02 non-security documentation | R9 | all others |
| M5 | remove the `publication_attestation` verification tail (so a present record is ignored) | R7 | R1, R10, R11 |

If a mutation makes a test RED that it must not, that is a **failure of the
isolation of the proof** and must be reported as such, not explained away.

## 6. Frozen RED→GREEN run protocol

1. Run `commands.json` `B1-c1-red` against `iso/rf` (unfixed). Capture raw stdout
   + rc into `before/`. Expected: node set {R1..R10, R12} FAIL, R11 PASS;
   runner rc non-zero (the harness reports one rc per process; the **business**
   verdict is derived per node from the captured output, per the frozen rc
   legend in `commands.json`).
2. Implement the three fixes in `iso/fixed/rf`.
3. Run `B1-c2-green` against `iso/fixed/rf`. Expected: **all nodes PASS**,
   runner rc 0.
4. Run `B1-c3-mutation` (x5) in scratch copies. Expected: exactly the frozen
   RED/GREEN split of §5.
5. Re-hash production `scripts/ tests/ config/ artifacts/` and record
   `git status --porcelain` for those paths in `after/`. Expected: production
   unchanged.

## 7. Explicitly NOT closed by this card (must not be read as coverage)

1. **The invest-core consumer** (`~/.claude/skills/invest-core/scripts/
   invest_contracts.py:1130-1142`) is in a different repo and is **not touched
   or executed**. The label is now bound in this repo, but whether that consumer
   verifies the binding is **unverified and out of scope**.
2. **No CLI / transaction entry point** is exercised; coverage is the dispatcher
   chain, as in I-08-C.
3. **I-08-A's full provider protocol is not implemented**: response
   `attestation_response_schema_version 1.0` exact-set parity is *reduced* here
   to the frozen §3.4 response set; the I-08-A `issued_at`/`expires_at`/`W`
   replay window (E18), `request_id` reuse ledger (E19), trust-domain 12-field
   entry schema with `not_before`/`not_after`/`status`/`revoked_at`/
   `environment`, fail-loud trust loading (E25) and **E24** test-key rejection
   are **NOT implemented**. Codes E18/E19/E22/E23/E24/E25/E29 and the L3
   three-layer proof domain remain **OPEN**.
4. **`config/trusted_signer_public_keys.json` stays absent.** This card adds no
   production trust anchor and MUST NOT: adding one would be a capability grant,
   not a fix (I-08-A R-PROV-2).
5. **REM-02 is documentation only.** The function still accepts a
   self-consistent forgery — that is the frozen, documented limitation, not an
   unfinished fix.
6. **I-08-C remains `changes_required`.** This card supplies product-side
   fixes for review; it does not and cannot close I-08-C, whose verdict belongs
   to its own reviewer.

## 8. Frozen rc legend (copied from `execution_v2/START_HERE.md`; owner ruling T1-19 / §13)

| rc | meaning |
|---|---|
| 0 | pass — normal end **and** business verdict pass |
| 1 | harness failure — import/fixture/binding error |
| 2 | no verdict / correctly-rejected negative |
| 3 | not as expected — a positive failed, or a negative was **not** rejected |

`case_results` in `handoff.json` must classify each node by this table. A single
pytest process returns ONE rc for the whole file; a reader must never infer
"all passed ⇒ accepted".

## 9. Oracle revision policy

This body is frozen as **r1** and is **append-only** thereafter. Any revision
must be appended under a clearly labelled `## Revision rN` heading with the
reason, and the r1 byte range must remain byte-untouched with a hash proof
(locate the append marker, hash the fixed prefix).

## Revision r2 — correction of one frozen RED expectation, recorded BEFORE the r2 RED run

**Date of revision:** written after the r1 RED run and before the r2 RED run.
**Reason:** the r1 RED run exposed an imprecision in the r1 freeze, not a defect
in the fix. This revision narrows one expectation; it does **not** relax any
security expectation and does **not** touch the r1 byte range.

### R2-1. What happened

The r1 oracle §4 marked node **R8** (`test_rem01_h_signed_record_is_repeatable_and_stable`)
as `FAIL` on the unfixed tree. In the r1 test file, R8 asserted only that the
label reads `host_signed` and that two consecutive reads are accepted. On the
unfixed tree that assertion is **trivially satisfied**: the label is set from a
boolean, no record is required, and `validate_publication_receipt` /
`validate_forecast_output` accept it. R8 therefore **PASSED** on the unfixed
tree, and the r1 RED run reported `10 failed, 2 passed` instead of the frozen
`11 failed, 1 passed`.

### R2-2. Adjudication — this is a test-strength defect, and it is fixed

The r1 R8 assertion was **too weak to measure REM-01**: a node that passes on a
tree where `host_signed` carries no signature cannot be the regression guard for
"`host_signed` must carry a verifiable record". The correct reading of the r1
freeze is the one stated in the r1 §4 table itself, which already required for
AFTER: *"label `host_signed`; record present; exact field set; signature
verifies"*. R8 is therefore **strengthened** to assert the record's presence and
its exact field set in addition to repeatability. Its r1 expectation text
("PASS after the fix") is **unchanged**; only the assertion set that measures it
was brought up to what r1 already said.

Consequence, frozen for the r2 RED run: **R1-R10 and R12 FAIL, R11 PASSES →
`11 failed, 1 passed`, runner rc 1.** R11 (`test_rem03_honest_package_still_accepted`)
is a deliberate positive control and is expected GREEN on both trees; it is the
node that proves the new gates do not break honest artifacts.

### R2-3. What this revision does NOT change

- No expectation in r1 §4 is relaxed. R8's frozen AFTER expectation is identical.
- No §3 design field, code, or rule is changed. §3.1-§3.6, the §3.4 wire
  contract, the §5 mutation table and the §6 run protocol stand as frozen.
- §7's not-closed list stands unchanged.
- The E27 code spelling, the `attestation_missing_record` message and the
  `segment base revenue mismatch` message are unchanged.

### R2-4. Honest blemish recorded

The r1 test file (sha256 `e6c0949c3b7d0d9c3bad101dc90a62cb8702dc4616715adfc2227dda60aa8f75`,
18236 bytes) was written and hashed **before** the r1 RED run, together with the
r1 oracle (`81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281`,
27697 bytes). Both r1 hashes remain recorded in `before/frozen_artifacts.json`
and `before/b1_unfixed.*` is preserved as the r1 RED run's raw stdout. The r2
test file is stronger, not different in intent: the added lines assert the
record that the r1 prose already required. This is disclosed rather than
silently re-baselined, and the r1 RED stdout is **not** overwritten.

### R2-5. Append-only proof for this revision

Recorded in `scratch/append_oracle_r2.stdout.json`:
`append_marker_offset`, `frozen_body_bytes_on_disk_now`,
`frozen_body_sha256_on_disk_now`, `frozen_body_untouched`.
