
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
