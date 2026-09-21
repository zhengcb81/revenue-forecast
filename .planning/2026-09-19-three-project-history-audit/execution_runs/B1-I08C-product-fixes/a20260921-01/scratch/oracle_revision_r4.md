
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
