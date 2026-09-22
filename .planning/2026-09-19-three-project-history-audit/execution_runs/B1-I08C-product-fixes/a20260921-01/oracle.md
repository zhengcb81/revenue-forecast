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

## Revision r3 — attestation record / wire contract correction (fixpoint), recorded BEFORE the GREEN run

**Reason:** two r1 §3 items are mutually unsatisfiable, and the r1 wire request
also demanded a value that cannot exist at request time. Neither is a relaxation
of a security expectation; both are corrections that make the frozen contract
implementable. The r1 body (bytes `[0:27697]`) and the r2 revision are
byte-untouched.

### R3-1. The defect in the r1 freeze

1. **A receipt cannot contain its own hash.** r1 §3.1 listed `receipt_sha256` as
   an attestation-record field, and r1 §3.4 put `receipt_sha256` in the provider
   **request**. But `receipt_sha256 = canonical_sha256(receipt minus that field)`
   and the record lives *inside* the receipt, so setting
   `record["receipt_sha256"] = receipt["receipt_sha256"]` changes the receipt and
   therefore changes the very value just written. There is no fixpoint. The
   production design already avoids this for `validated_payload_sha256` (the
   receipt excludes `publication_receipt` and `result_sha256` from its payload
   hash for exactly this reason).
2. **The request was built before the receipt existed**, so `receipt_sha256`
   could not have been signed over anyway.

### R3-2. Frozen correction (this supersedes r1 §3.1 and §3.4 on these points only)

- The attestation record field set is **11 fields**, not 12. `receipt_sha256` is
  **removed**: `{attestation_payload_schema_version, domain_separator, issuer,
  key_id, algorithm, fingerprint, request_id, payload_sha256, result_sha256,
  signed_at, signature}`. The set remains **closed and exact**; a record with an
  extra or missing key is still rejected.
- The provider **request** is
  `{attestation_request_schema_version, domain_separator, request_id,
  payload_sha256, result_sha256, canonical_payload_sha256}` — `receipt_sha256`
  removed. The signing target is the **whole request object including**
  `canonical_payload_sha256` (r1 §3.4's "explicitly-named signing target" wording
  is hereby made unambiguous: the target is the object, the extra key is a
  redundant naming of one of its members).
- **Nothing becomes unbound.** `payload_sha256` covers the receipt's whole
  payload (everything except `result_sha256` and `publication_receipt`), and
  `verification_context_sha256` covers the input anchor, the executed gate set
  and the validator version; the receipt's `receipt_sha256` covers both plus the
  record itself. The one field that leaves the record,
  `record["receipt_sha256"]`, was never independently checkable, so its removal
  removes no property that r1 could have measured. This is recorded as a
  **narrowing of the record's field list**, disclosed rather than glossed.
- Everything else in r1 §3.1/§3.4 stands: the identity triple
  (`issuer`/`key_id`/`fingerprint`), the frozen `domain_separator`, the 64-hex
  one-shot `request_id`, the byte-identical echo rule (E09), the exact-response
  field set (E08), the trust-domain binding (E20/E21) and the Ed25519
  verification target construction (`canonical_sha256(payload).encode("ascii")`,
  identical to `contracts/evidence._validate_host_signature`).
- r1 §3.4's response field set is **unchanged** (10 fields).

### R3-3. Consequential clarifications (no expectation changed)

- `PUBLICATION_ATTESTATION_FIELDS` in the fixed tree has 11 members; the frozen
  test's `ATTESTATION_FIELDS` mirrors that exactly, so the closed-set assertion
  still measures what r1 §3.1 intended.
- `build_publication_receipt(..., publication_attestation=...)` additionally
  **fails closed** when `attestation_status == "host_signed"` is requested with no
  record. r1 §3.3 implied this; r3 states it as a contract.
- The receipt-layer attestation check runs only for `formal_output_mode ==
  "formal"` (draft receipts certify no strong gate and carry an empty gate set;
  they are already rejected by the existing `gate_ids mismatch` require).

### R3-4. What this revision does NOT change

No security expectation is relaxed. E12/E13/E14/E16/E17/E20/E21/E26/E27 keep
their r1 meaning, spelling and trigger conditions. The REM-02 deliverable and
the REM-03 gates (`segment base revenue mismatch`, `segment opening base does not
reconcile`) are exactly as frozen in r1 §3.5/§3.6. The §5 mutation table and the
§6 run protocol stand.

### R3-5. Append-only proof for this revision

Recorded in `scratch/append_oracle_r3.stdout.json`: `append_marker_offset`,
`frozen_body_bytes_on_disk_now`, `frozen_body_sha256_on_disk_now`,
`frozen_body_untouched`. The r1 body hash must still equal
`81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281` (27697 bytes);
the r1+r2 prefix hash is recorded at the r2 append and is re-checked here.

## Revision r4 — R7 strengthened into two measured attacker moves; command-id correction

### R4-1. R7 (node `test_rem01_g_replayed_record_is_rejected`) strengthened

**Reason:** the r1 R7 shape mutated a bound value and then recomputed the record's
own `payload_sha256` copy before asserting rejection. That single case measures
**two** things at once — (i) the artifact binding and (ii) the Ed25519 binding —
so the mutation proof could not ask the narrower question "does removing one check
alone weaken the package?". R7 now performs **two separately asserted moves**:

| case | attacker move | expected rejection reason |
|---|---|---|
| (a) | mutate `confidence.score`, recompute payload/receipt/result hashes, leave the record untouched | `attestation_payload_hash_mismatch` (E16) — the record's `payload_sha256` no longer equals the live `validated_payload_sha256` |
| (b) | as (a) **and** also refresh the record's own `payload_sha256` copy (the strongest hash-recomputing move available) | the artifact binding / signature still rejects (`attestation`-prefixed message) |

R7's r1 **expectation text is unchanged** ("rejected"), and no other node changes.
The strengthened node is measured empirically: 12 passed / rc 0 on the fixed tree,
and it is RED on the unfixed tree for the structural reason already frozen (no
record exists at all).

### R4-2. Consequence for the §5 mutation table (r1) — adopted, not relaxed

The r1 §5 table said M1 must leave R7 GREEN. That expectation was written against
the r1 R7 shape. With the two-case shape, removing the whole
`validate_publication_attestation` call (M1) removes **both** checks, so **R7 is
red under M1 as a declared dependency, not as collateral**. §5's M1 row is
therefore amended as follows, and this is the only amendment:

| mutation | r1 §5 said R7 | r4 measures R7 |
|---|---|---|
| M1 | must stay GREEN | **expected RED**, declared as a dependency of M1 (M1 reverts the whole record check, not just E27) |

Everything else in §5 stands, and the **isolation claim is unchanged in strength**:
each mutation's declared red set must equal its observed red set **exactly**, with
no missing and no extra node. The measured sets are recorded in
`scratch/mutations/mutation_proof.json`:

| mutation | declared = observed red set |
|---|---|
| M1 | `{R1, R7}` |
| M2 | `{R2[plain_txt], R2[bare_py], R2[sys_executable], R6}` |
| M3 | `{R10, R12}` |
| M4 | `{R9}` |
| M5 | `{R7}` |

M2's R6 and M1's R7 are the only dependencies; both are stated above with their
mechanism, and both were observed rather than assumed.

### R4-3. Command-id correction (documentation only)

`commands.json` `B1-c0` was first drafted against
`scratch/production_status.py`. The script that actually produced
`before/production_anchors.json` is the inline anchoring step recorded in
`before/production_anchors.json` itself; `B1-c0`'s `argv` field has been corrected
to name `scratch/production_status.py` writing
`before/production_anchors.txt`, which is the reproducible equivalent. This is a
naming correction and changes no expectation and no evidence.

### R4-4. Append-only proof for this revision

Recorded in `scratch/append_oracle_r4.stdout.json`: `append_marker_offset`,
`frozen_prefix_bytes_on_disk_now`, `frozen_prefix_sha256_on_disk_now`,
`frozen_prefix_untouched`. The r1 body must still hash to
`81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281` (27697 bytes).

## Revision r5 — F1/REM-40: the executed attestation-record field set is 10, not 11

**Appended by the B1-PREREQ card** (`execution_runs/B1-PREREQ/a20260922-01`)
under this oracle's §9 revision policy, on commission of the independent
review's finding F1 (`reviewer_report.md` §6 F1 and §9.1: "append oracle
revision r5 correcting the §R3-2/R3-3 field-count text to 10 fields"). The r1
byte range, r2, r3 and r4 are untouched; the prefix proof is
`execution_runs/B1-PREREQ/a20260922-01/scratch/append_oracle_r5.stdout.json`
(`frozen_prefix_untouched: true`, marker at byte 39288 = 39287 + 1).

### R5-1. What was wrong

Revision r3 R3-2 froze *"the attestation record field set is **11 fields**,
not 12. `receipt_sha256` is removed: {attestation_payload_schema_version,
domain_separator, issuer, key_id, algorithm, fingerprint, request_id,
payload_sha256, **result_sha256**, signed_at, signature}"*, and R3-3 froze
*"`PUBLICATION_ATTESTATION_FIELDS` … has **11 members**"*. Both counts are
wrong about the artifact that was actually executed and delivered. The
executed record set — measured from the fixed tree, mirrored by the frozen
test's `ATTESTATION_FIELDS`, and independently measured by the reviewer — is
exactly **10 fields**:

```
{attestation_payload_schema_version, domain_separator, issuer, key_id,
 algorithm, fingerprint, request_id, payload_sha256, signed_at, signature}
```

`result_sha256` is **not** a record field; neither is `receipt_sha256`. The
set remains closed and exact (extra or missing key ⇒ reject), and
`set(record) == PUBLICATION_ATTESTATION_FIELDS → True` at 10 members.

### R5-2. Why r3's "11" was wrong

r3 removed `receipt_sha256` for a fixpoint reason — a receipt cannot contain
its own hash — but left `result_sha256` in the bullet list and in R3-3's
member count. The same class of fixpoint applies to `result_sha256`:
**`result_sha256` covers the receipt, and the receipt contains the record**,
so no consistent `result_sha256` value exists at record-assembly time either.
The executed design therefore also keeps `result_sha256` out of the record
and pins the **request's** `result_sha256` member to
`SIGNED_RESULT_SHA256_SENTINEL = "0" * 64` via
`publication_attestation_request()` (`iso/fixed/rf/scripts/revenue_publication.py`),
which keeps the signed request reconstructible at validation time (the
validator rebuilds the request with the sentinel before Ed25519 verification).
This is the same reasoning the review records as F6 and the code comment at
the record-verification site documents. r3's prose was internally inconsistent
with its own fixpoint argument; the delivered 10-field set was right.

### R5-3. Which artifacts were right all along

`handoff.json` ("10-field closed record + Ed25519 vs trust domain"), the
attempt's `decision.md` §3 ("carries **10** fields, not the 12 r1 first
froze") and `binding.json` all state 10; the frozen test file's
`ATTESTATION_FIELDS` enumerates precisely those 10 members. Only this
oracle's r3 prose said 11. The reviewer's measurement (F1) and an independent
re-measurement by the B1-PREREQ card
(`evidence/final_integrity_check.stdout.txt`) both give 10.

### R5-4. What this revision does NOT change

No security expectation is relaxed and none is added. The §3.1
closed-and-exact rule, E12/E13/E14/E16/E17/E20/E21/E26/E27 spellings, the §4
case matrix, the §5 mutation table, the §6 run protocol and the §7 not-closed
list all stand as frozen. This revision corrects a **count and a field list**
in r3's prose only; it does not edit r1–r4 bytes.

### R5-5. Append-only proof for this revision

Recorded in the B1-PREREQ attempt:
`scratch/append_oracle_r5.stdout.json` with `append_marker_offset: 39288`,
`frozen_prefix_untouched: true`, `sha256(bytes[0:39287]) =
fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae`
(the reviewer-pinned pre-r5 state), and re-checks of the r1
(`81af1240…`, 27697), r2 (`60ecbca7…`, 31081) and r3 (`231e7976…`, 35840)
prefix hashes.
## Revision r6 — F2/REM-41: mutation M6 joins the proof surface; R13-equivalent node pointer

**Appended by the B1-PREREQ card** (`execution_runs/B1-PREREQ/a20260922-01`)
under this oracle's §9 revision policy, on commission of review finding F2
(`reviewer_report.md` §9.2: fold an R13-equivalent node into the card's proof
set and add M6 to the mutation table). Revisions r1–r5 are untouched; the
prefix proof is
`execution_runs/B1-PREREQ/a20260922-01/scratch/append_oracle_r6.stdout.json`
(`frozen_prefix_untouched: true`, marker at `(post-r5 bytes) + 1`).

### R6-1. The measured blind spot (adopted as measured, not re-argued)

The independent reviewer authored mutation **M6** — short-circuit
`validate_publication_attestation` after the closed-set/structural checks
whenever `attestation_status != "host_signed"`, so a present-but-invalid
record becomes ignorable — declared its red set **before running**, and
measured the frozen 12-node file **12/12 GREEN on the M6 mutant**
(declared `{}` = observed `{}`). Every node that carries a record also
carries the `host_signed` label (R2/R3/R4 carry no record; R1/R7 carry the
label), so the r1 §3.1 clause *"a record that does not verify must never be
present-but-ignored"* was load-bearing in the implementation yet unmeasured
by this card's own proof set. F2.

### R6-2. §5 mutation table — appended row (§5 itself is frozen, so the row lives here)

| mutation | revert target | must go RED | must stay GREEN |
|---|---|---|---|
| **M6** | insert `if not claims_signed:` / `# MUTATION M6: only a labelled claim is held to its record.` / `return` immediately after the comment `…so any change to a bound value breaks the signature.` and before the `require(record["payload_sha256"] …)` check in `validate_publication_attestation` — exact bytes frozen in the B1-PREREQ attempt's `oracle.md` §3.2, applied by hash-asserted script (pre-hash `bc2bb4a3…`) **only to an attempt-local copy** | the new node `test_rem41_a_present_record_is_verified_even_when_label_is_unattested` | all 12 frozen nodes (their declared red set under M6 is `{}` — the blind spot, now declared explicitly rather than discovered) and the new node's positive control |

Isolation requirement unchanged in strength: on the 14-node surface (12
frozen + 2 new) the declared red set under M6 is exactly
`{test_rem41_a_present_record_is_verified_even_when_label_is_unattested}` —
no missing red, no extra red; measured red sets are recorded in the
B1-PREREQ attempt's `evidence/arm2_node_on_m6.stdout.txt` and
`evidence/arm3_frozen12_on_m6.stdout.txt`.

### R6-3. The node, frozen BEFORE execution

- File: `execution_runs/B1-PREREQ/a20260922-01/test_r13_equiv_rem41.py`,
  sha256 pinned in that attempt's `freeze.json` (entry
  `my_node_r13_equiv_rem41`), written and frozen before any run.
- It imports **this** attempt's frozen `test_b1_rem.py` fixtures and helpers
  (`fake_provider`, `trusted_domain`, `workdir`, `public_key_bytes`,
  `isolated_env`, `_rehash`, `_receipt_of`, `_record_of`, `_with_provider`,
  `_clear_provider`) so nothing is re-implemented; **neither this oracle's
  §4/§5 text nor `test_b1_rem.py` is edited** — the 12-node file keeps its
  pin `636b43c8d8e1dc59ccfa36d7c71125ea9b8665222f587510444a3656b6700c16`.
- Pre-registered arms (declared before running; B1-PREREQ `oracle.md` §3.2):
  fixed tree ⇒ 2 passed / rc 0; M6 mutant ⇒ node RED + control GREEN / rc 1;
  frozen 12-node file on the M6 mutant ⇒ 12 passed / rc 0; unfixed tree ⇒
  node RED + control GREEN / rc 1. Raw stdout of every arm is preserved
  byte-for-byte under that attempt's `evidence/` (evidence protocol, its
  finding F4).

### R6-4. What this revision does NOT change

No §4 case, no §3 design point, no E-code, no security expectation changes.
M6 is an **addition** to the mutation proof surface (strengthening it); it
does not amend the declared red sets of M1–M5 measured in r4.

### R6-5. Append-only proof

`execution_runs/B1-PREREQ/a20260922-01/scratch/append_oracle_r6.stdout.json`:
`append_marker_offset` = (post-r5 byte count) + 1, `structural_ok: true`,
`frozen_prefix_untouched: true` with re-checks of the 27697, 31081, 35840,
39287 and post-r5 prefix hashes.
## Revision r7 — F4/REM-43 gap restated: the r1 RED stdout SURVIVES; only the r1 test file is lost

**Appended by the B1-PREREQ card, correction round r2**
(`execution_runs/B1-PREREQ/a20260922-01`, record-only round) under this
oracle's §9 revision policy, on commission of independent-review finding
**F-REV-B1P-01 (BLOCKER)** in
`execution_runs/B1-PREREQ/a20260922-01/reviewer_report.md`
(25883 B, sha256 `e25a2c837009aebf4be542a89cafa13e78a0dae59b3556a7766ae8bb397376f6`).
Revisions r1–r6 are untouched: this is a pure suffix append
(`new = old + b"\n" + revision`), marker at (post-r6 bytes) + 1, with proof in
`execution_runs/B1-PREREQ/a20260922-01/scratch/append_oracle_r7.stdout.json`
and post-append re-measurement in that attempt's
`evidence/r2/r2_09_post_append_verification.json` (four reviewer-recomputed
prefixes 27697 / 31081 / 35840 / 39287 **and** the post-r5 (43298) and
post-r6 (47538) prefixes all re-match; this revision's heading marker occurs
exactly once in the post-append file).

### R7-1. Corrected F4 gap statement (every fact re-measured 2026-09-22; raw outputs in the B1-PREREQ attempt's `evidence/r2/`)

1. `before/b1_unfixed.stdout.txt` = **30580 B**, sha256
   `58863ffbca21c72350b868e9b344cc7e5a1651060f6ccb5bb1fcd3f796701335`,
   encoding UTF-16LE+BOM. Decoded: **10 `FAILED` lines / 2 `PASSED` lines**,
   summary line exactly `10 failed, 2 passed in 8.18s`, failure-block line
   refs into the r1 test file `268, 296, 323, 348, 372, 407, 438, 460`. The
   string `11 failed, 1 passed` does **not** occur anywhere in it. It **IS the
   r1 RED run's stdout** — the very warrant for this oracle's Revision r2 —
   **not** a final 11/1 output.
2. git history of that path: exactly **one** commit, `980c9b7a`
   (2026-09-21 21:16:24); its blob is the same 30580 B / `58863ffb…` bytes and
   `HEAD`'s blob equals the working-tree bytes (`git status --porcelain` clean
   for the path; `git hash-object` = `ls-tree` blob id). It is also the only
   reachable blob ever stored at that path. Since 21:16:24 there has been no
   moment when this path held an 11/1 output.
3. Provenance as the r1 run: stdout mtime 21:15:12, run stderr mtime 21:14:45
   (the attempt's first pytest run), `scratch/oracle_revision_r2.md` (the r2
   warrant) written 21:15:35 — 23 s after the stdout. B1's sealed
   `handoff.json` records at line 137
   `red_r1 = {"label": "before/b1_unfixed", ..., "failed": 10, "passed": 2, ...}`,
   at line 198 `"red_r1_stdout": "before/b1_unfixed.stdout.txt"`, and at
   line 110 "The r1 RED stdout is preserved and was NOT overwritten by the r2
   run" — that preservation claim is **TRUE**.
4. The genuine 11/1 outputs are `before/b1_unfixed_r2.stdout.txt`
   (2026-09-21 21:18) and `before/b1_unfixed_r3.stdout.txt` (21:56), each
   "11 failed, 1 passed".
5. **The only genuinely lost artifact, within the reviewer's scanned domains
   (report §4.4/§5.3): the r1 test file — 18236 B, sha256
   `e6c0949c3b7d0d9c3bad101dc90a62cb8702dc4616715adfc2227dda60aa8f75`.** It is
   absent from the working tree, absent from every reachable commit (content
   blobs ever stored at the path: 18611 B / `da3d29bf…` at `980c9b7a`, then
   20631 B / `636b43c8…` at `HEAD`), and absent by size from all 1294
   reflog-unreachable blobs the reviewer scanned. Other recovery routes (editor
   backups, pack promisor partials, other clones' worktrees) were declared
   unexhausted by the reviewer (§5.3).
6. **REM-43 re-scope:** the protocol half stands **closed** (established,
   evidenced, 31-entry manifest re-verified); the historical gap is narrowed to
   the **r1 test file only**. The claim of an "unclosable permanent gap" for
   the r1 RED stdout is **withdrawn — the stdout is auditable right now**
   (byte-pinned here, in git, with line refs that match the r1 test file).

### R7-2. Superseded statements retained verbatim

`superseded_reason: "refuted by reviewer F-REV-B1P-01 with byte evidence"`.
Domain of refutation: bytes at `before/`, git objects reachable from
`HEAD`/`--unreachable`, and B1's sealed `handoff.json`, as re-measured
2026-09-22 (`B1-PREREQ/a20260922-01/evidence/r2/r2_01..r2_06*.json`). Nothing
below is deleted from its carrier; each carrier keeps its bytes and carries the
supersession pointer (B1-PREREQ `oracle.md` is frozen pre-run and therefore
keeps the false text as-is; its correction lives in that attempt's
`decision.md` §r2 and `handoff.json` r2 block).

1. B1-PREREQ `oracle.md` §1, closure check (frozen pre-run), verbatim:
   ```
   - **F4**: no `evidence/`-style raw-stdout protocol exists in SRC; the r1 RED
     stdout remains unrecoverable ⇒ open (protocol + disclosure only; the
     historical loss is **unclosable** — see §4).
   ```
   Refuted for the stdout: it is on disk at `before/b1_unfixed.stdout.txt`.
2. B1-PREREQ `oracle.md` §2 F4 (frozen pre-run), verbatim:
   ```
   - **F4 / REM-43 (LOW, evidence)** — the r1 RED stdout ("10 failed / 2 passed")
     was overwritten by a later run and the r1 test file (18236 B / `e6c0949c…`)
     is gone from disk and git ⇒ the disclosed r1 incident (the warrant for r2)
     is not independently auditable, contrary to the handoff's "preserved and
     NOT overwritten" claim. Fix: byte-preserved raw stdout for **every new**
     RED/GREEN arm under `evidence/` + record the r1 loss as a disclosed,
     **unclosable** historical gap.
   ```
   Refuted for the stdout (the handoff's preservation claim is true);
   sustained only for the r1 test file.
3. B1-PREREQ `oracle.md` §3.4 item 4 (frozen pre-run), verbatim:
   ```
   4. **Disclosed unclosable historical gap (r1):** B1's r1 RED stdout
      ("10 failed / 2 passed", warrant for oracle r2) and the r1 test file
      (`e6c0949c…`, 18236 B) were overwritten/removed before archiving and cannot
      be recreated by this or any later card; the surviving
      `before/b1_unfixed.stdout.txt` (`58863ffb…`) is the **final** 11/1 output,
      not r1's. This gap is recorded here and in `decision.md` as **open,
      disclosed, unclosable** — it is not claimed closed by this card.
   ```
   Refuted in both halves: the stdout was never overwritten and is not an 11/1
   output.
4. B1-PREREQ `oracle.md` §4 item 1 (frozen pre-run), verbatim:
   ```
   1. The r1 RED stdout / r1 test file loss (F4) — **unclosable**, disclosed.
   ```
   Refuted for the stdout; corrected scope = r1 test file only.
5. B1-PREREQ `decision.md` §F4, verbatim:
   ```
   - **Unclosable historical gap (not claimed closed):** B1's r1 RED stdout
     ("10 failed / 2 passed" — the warrant for oracle r2) and the r1 test file
     (18236 B / `e6c0949c…`) were overwritten/removed before archiving and cannot
     be recreated by this or any later card. The surviving
     `before/b1_unfixed.stdout.txt` (30580 B / `58863ffb…`, pinned in
     `freeze.json`) is the final 11/1 output, not r1's. Recorded here, in
     `oracle.md` §3.4/§4, `handoff.json`, and the register row it closes — REM-43
     closes as *protocol + disclosure*, explicitly leaving the historical loss
     open.
   ```
   Refuted; superseded by `decision.md` `## r2` (the §F4 text itself is kept).
6. B1-PREREQ `handoff.json` `findings.F4.unclosable_historical_gap`, verbatim:
   ```
   B1's r1 RED stdout ('10 failed / 2 passed', the warrant for oracle r2) and the r1 test file (18236 B / e6c0949c...) were overwritten/removed before archiving and cannot be recreated by any later card; the surviving before/b1_unfixed.stdout.txt (30580 B / 58863ffb..., pinned in freeze.json) is the final 11/1 output, not r1's. REM-43 closes the PROTOCOL half only; the loss stays open.
   ```
   Refuted; superseded by the `handoff.json` r2 block (the string itself is
   retained byte-for-byte under
   `findings.F4.unclosable_historical_gap__superseded.original_text_verbatim`).
7. SRC `reviewer_report.md` F4 (lines 386–401; sealed — origin of the wording;
   NOT edited here), key sentences verbatim:
   ```
   But the handoff/binding record their mtime as the r1 run's artifact whose content is *"10 failed / 2 passed"*, while the file on disk is the final 11-failed/1-passed output (mtime 21:15:12, `before/b1_unfixed_r3.*` written at 21:56) — and the r1 test file (18236 B / `e6c0949c…`) is no longer in the attempt directory or in git. I therefore **cannot reproduce the disclosed r1 "10 failed / 2 passed, R8 passed trivially" incident**, which is the entire stated warrant for oracle revision r2. […] the r1 artifact that would let a reviewer audit the claim was overwritten rather than preserved, contrary to `handoff.json`'s "the r1 RED stdout is preserved and NOT overwritten".
   ```
   Refuted on the bytes: the file on disk is r1's 10/2 output, and the handoff's
   preservation claim is true. Per F-REV-B1P-01 required correction #3 this
   sealed report needs an erratum/annotation in the plan's
   `REMEDIATION_REGISTER.md` — an **owner/parent register action**, recorded by
   the parent, not written by this card (B1's attempt stays sealed).

### R7-3. Where the false sentence actually lives (measured, not assumed)

Whitespace-normalized scan of the pre-r7 record
(`B1-PREREQ/a20260922-01/evidence/r2/r2_06_false_claim_locations.json`): the
false sentence is present in B1-PREREQ `oracle.md` (§1/§2/§3.4/§4 — frozen
pre-run), B1-PREREQ `decision.md` §F4, B1-PREREQ `handoff.json` F4, and SRC
`reviewer_report.md` F4; it is **absent** from this oracle's pre-r7 body, from
SRC `decision.md` and from SRC `handoff.json` — the latter two state the true
position ("the r1 RED stdout is preserved and was NOT overwritten"). This
revision therefore restates the gap scope in this oracle without contradicting
any pre-r7 byte of it, and corrects the review's location note by measurement.

### R7-4. What this revision does NOT change

No §4 case, no §3 design point, no E-code, no security expectation, no run
result, no B1 carrier file; r1–r6 byte ranges stay byte-untouched (prefix
proofs above). **No erratum to B1's F6 record** — the review's explicit ruling
(§5 of the B1-PREREQ review) is "NO erratum warranted"; the optional one-line
F6 clarification is registered by the parent in the plan register and in the
B1-PREREQ attempt's `decision.md` §r2, not here. F1/F2/F3/F5 dispositions are
unchanged (all confirmed by that review).