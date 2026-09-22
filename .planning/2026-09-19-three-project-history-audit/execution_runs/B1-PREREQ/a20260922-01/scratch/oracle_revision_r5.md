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