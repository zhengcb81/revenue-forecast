# oracle.md — INVEST-CORE-ATTEST-GATE (r1, FROZEN before any run)

- Plan: `2026-09-19-three-project-history-audit`
- Card: **INVEST-CORE-ATTEST-GATE** (cross-repo; REM-01 consumer side)
- Attempt: `execution_runs/INVEST-CORE-ATTEST-GATE/a20260922-01`
- Owner ruling: `OWNER_DECISIONS.md` §16 verbatim 「E-3: 立卡」— open the card;
  the patch + red/green live in isolation; **merge pending the invest-core
  owner's approval** (this card does NOT self-merge into the other repo).
- Freeze policy: this r1 document is byte-frozen BEFORE the first pytest
  execution of this attempt. `before/frozen_artifacts.json` pins its sha256.
  Any later expectation change must be an APPEND-ONLY revision (r2+) with a
  hash proof that the r1 byte range is untouched; r1 expectations are never
  edited in place.

---

## 1. The defect (frozen statement)

Site: `invest_contracts.py` (sha256
`9ad8a146ab1535555b7fd74a14acbb8280c21d4eb22e3e92da3ab2965ba3cc45`,
2689 lines, byte-identical in all four located copies — see §7), lines
1130–1142, inside `adapt_revenue()` — the consumer entry point every
invest-* module uses to consume a revenue publication:

```python
attestation_status = receipt.get("attestation_status", "unattested")
if is_legacy:
    attestation_verification = "legacy_read_only"
elif attestation_status == "host_signed":
    attestation_verification = "host_signed"          # <-- label trusted as-is
else:
    if require_attestation:
        _fail(False, "revenue result is unattested; ...")
    attestation_verification = "unattested_bypassed"
```

The label is a plain string. The consumer accepts
`attestation_status == "host_signed"` **without verifying any binding record**,
so a package that claims the label with no `publication_attestation` record
(I-08-A E27 shape) is consumed as host-signed. Independent evidence this is
reachable in production issuance today: B1's review
(`execution_runs/B1-I08C-product-fixes/a20260921-01/reviewer_report.md`,
sha256-pin in §8) established that production `attestation_capability()`
treats any existing file as capability (a 5-byte `.txt` mints `host_signed`)
and that B1's issuance-side fix is **not promoted** — production issuance can
still mint the label with no record, and the invest-core consumer has never
been fixed (B1 report §8.2 names this site the decisive unverified consumer).

## 2. Remedy contract (what the FIXED consumer must do)

Frozen here so the patch can be judged against the expectation; rationale
lives in `decision.md`.

When (and only when) the package is **not legacy** and
`attestation_status == "host_signed"`, the consumer must verify a
`publication_attestation` binding record carried in `publication_receipt`,
mirroring B1's REM-01 remedy (`iso/fixed/rf/scripts/revenue_publication.py::
validate_publication_attestation`) exactly:

1. **E27** — record present; otherwise reject with a coded error whose message
   contains `attestation_missing_record`.
2. **Closed field set** — exactly these 10 fields, no more no fewer:
   `attestation_payload_schema_version`, `domain_separator`, `issuer`,
   `key_id`, `algorithm`, `fingerprint`, `request_id`, `payload_sha256`,
   `signed_at`, `signature`. Mismatch rejects with `attestation_payload_fields`.
3. **Constants** — `attestation_payload_schema_version == "1.0"`,
   `domain_separator == "revenue-forecast/publication-attestation/v1"`,
   `algorithm == "ed25519"`; `issuer`/`key_id` non-empty strings;
   `fingerprint` = 32 lowercase hex; `request_id` = 64 lowercase hex;
   `signed_at` = RFC3339 UTC `Z`; `signature` = 128 lowercase hex
   (absent signature rejects with `attestation_missing_signature`, malformed
   with `attestation_malformed_signature`).
4. **E16 payload binding** — `record["payload_sha256"]` must equal the
   receipt's `validated_payload_sha256`; mismatch rejects with
   `attestation_payload_hash_mismatch`.
5. **Signature (E14/E20), fail-closed** — reconstruct the signed request as
   `{attestation_request_schema_version: "1.0", domain_separator, request_id,
   payload_sha256, result_sha256: "0"*64, canonical_payload_sha256:
   payload_sha256}`, verify Ed25519 over `canonical_sha256(request)` against
   the trust domain loaded through **the revenue runtime's single loader**
   `contracts.evidence._trusted_signer_public_keys()` (source:
   `REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS` env, else the runtime's
   `config/trusted_signer_public_keys.json`; missing file ⇒ zero trusted
   signers). Unknown fingerprint rejects with `provider_key_untrusted`;
   verification failure or unavailable crypto rejects with
   `attestation_signature_invalid`. Every failure path fails CLOSED.

Placement (frozen): the verification fires for non-legacy `host_signed`
packages **after** the existing content strong-validation
(`revenue_reference(result)` at line 1143) and **before** the adapter is
built. Rationale (frozen so the regression set is predictable): content-forged
packages must keep their existing `invalid revenue forecast` rejection
surface (the shipping test
`test_forged_sensitivity_artifact_is_rejected_cross_repo` pins that message);
the label forgery this card closes is content-valid, so it is rejected by the
new guard either way — no security is lost by the ordering.

**Frozen non-changes** (oracle clause 3): for every package whose
`attestation_status` is not `host_signed` (including `unattested` with
`require_attestation` True/False, and legacy schema), `adapt_revenue` behaves
exactly as before: same accept/reject outcomes, same
`attestation_verification` values (`legacy_read_only`,
`unattested_bypassed`, rejection message containing `unattested`). The
adapter's `attestation_verification` value on success stays `"host_signed"`
(no new enum). The legacy bypass itself (lines 1116/1131–1132, OPEN-D6
R-LEGACY-1/E29) is OUT OF SCOPE for this card and must remain untouched.

## 3. Trees under test (frozen)

| arm | tree | consumer bytes |
|---|---|---|
| RED / regression baseline | `iso/invest-core` (pristine copy) | sha256 `9ad8a146…` (source bytes) |
| GREEN / regression fixed | `iso/invest-core-fixed` (the patch applied here) | differs only in `scripts/invest_contracts.py` |
| MUTATION | `iso/invest-core-mutant` (copy of fixed + one exact revert, §6) | fixed minus the guard |
| revenue runtime (all arms) | `iso/revenue-forecast` (copy of `~/.agents/skills/revenue-forecast`, byte-identical to the Projects repo for every pinned file — `before/production_anchors.json`) | read-only runtime for `revenue_runtime()`, `run_forecast`, `contracts.evidence` |

Isolation invariants (frozen): `REVENUE_FORECAST_DIR` is overridden to the iso
copy (the machine's global value points at the Projects repo and must NOT be
used); `REVENUE_PUBLICATION_REGISTRY` points into the attempt (`conftest.py`,
before any import) so no formal `run_forecast` can append to a repository
registry; `REVENUE_ATTESTATION_PROVIDER` is popped for honest fixtures and set
only to the attempt's tmp 5-byte `.txt` for node R1b; trust files and fixture
keys exist only under the pytest tmp dir (`REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS`
points there per test). No repo or install surface is written by any run.

## 4. Frozen node expectations (10 nodes, file `test_invest_attest.py`)

Fixture construction (frozen): every package starts from an honest
`run_forecast(forecast_document())` publication of the iso runtime (schema
3.7, formal, registered in the attempt registry), then receives exactly the
stated mutation with every non-secret self-hash recomputed
(`validated_payload_sha256`, `receipt_sha256`, `result_sha256` — the
strongest hash-recomputing attacker move). The **valid record** positive
control is signed by a fixture-only Ed25519 key whose public key is placed in
a trust file under the pytest tmp dir only; the private key never leaves the
test process and exists nowhere else (B1 reviewer precedent, isolated
fixture — this card never signs anything outside its own test run).

| id | node (test function) | package | expectation on FIXED consumer |
|---|---|---|---|
| R1a | `test_r1a_label_flip_without_record_is_rejected` | honest package, ONLY `attestation_status`→`host_signed`, rehashed | `InvestmentArtifactError`, message contains `attestation_missing_record` |
| R1b | `test_r1b_issuance_minted_host_signed_without_record_is_rejected` | **production issuance output**: `REVENUE_ATTESTATION_PROVIDER`=5-byte `.txt` (B1's evidence), `run_forecast` mints the label for real; node first asserts label==`host_signed` AND no record (issuance fingerprint) | `InvestmentArtifactError`, message contains `attestation_missing_record` |
| R2 | `test_r2_record_payload_hash_mismatch_is_rejected` | valid record whose `payload_sha256` is `0*64` (≠ receipt `validated_payload_sha256`) and whose signature is correctly made over that stamped value, trust anchor set | `attestation_payload_hash_mismatch` |
| R3 | `test_r3_record_signature_invalid_is_rejected` | record fully shaped + payload-bound, trusted fingerprint, `signature`=`0*128`, trust anchor set | `attestation_signature_invalid` |
| R3b | `test_r3b_untrusted_fingerprint_is_rejected` | record fully shaped + payload-bound + self-consistently signed, fingerprint not in the trust domain, trust anchor set | `provider_key_untrusted` |
| R4 | `test_r4_record_extra_field_is_rejected` | valid record + one extra key | `attestation_payload_fields` |
| R5 | `test_r5_valid_record_without_trust_anchor_is_rejected` | otherwise-valid record, NO trust anchor configured (today's production state: anchor file absent everywhere) | `provider_key_untrusted` (fail-closed) |
| P1 | `test_p1_valid_record_is_accepted_positive_control` | valid record, payload-bound, signature verifies against the isolated trust anchor | `adapt_revenue` RETURNS; `adapter["attestation_verification"] == "host_signed"` |
| B1 | `test_b1_unattested_default_rejected_unchanged` | honest `unattested` package, default policy | `InvestmentArtifactError`, message contains `unattested` |
| B2 | `test_b2_unattested_bypass_traced_unchanged` | honest `unattested` package, `require_attestation=False` | returns; `adapter["attestation_verification"] == "unattested_bypassed"` |

**Declared RED set on the UNFIXED consumer (`iso/invest-core`) — the 7
security nodes:** {R1a, R1b, R2, R3, R3b, R4, R5}. The unfixed consumer has
no record check at all: every one of those packages is ACCEPTED (the test's
`pytest.raises` fails).
**Declared GREEN on the unfixed consumer:** {P1, B1, B2} — accepted/behaved
as before, so the RED run is 7 failed / 3 passed, raw rc **1**.

**Declared outcomes on the FIXED consumer (`iso/invest-core-fixed`):**
all 10 nodes pass, raw rc **0**.

The R1a/R1b pair is the card's decisive RED→GREEN: RED = unfixed consumer
accepts the forged-label package; GREEN = fixed consumer rejects it with a
coded error; P1 is the required positive control.

## 5. Regression expectations (invest-core's own 4-file suite, `tests/`)

The suite must run UNMODIFIED (byte-identical files in both arms).

- **Pristine arm (`iso/invest-core/tests`)**: expected collected-pass with
  raw rc **0** in a clean environment (no attestation provider, no trust
  anchor, `REVENUE_FORECAST_DIR`→iso runtime).
  *Contingency (pre-registered, B1-r2 precedent): if the measured pristine
  baseline shows failures BEFORE any fix exists, those exact failures are
  recorded in append-only oracle r2 with their raw output, and only
  fix-attributable DELTAS (pristine vs fixed) count against this card. No
  expectation is silently edited.*
- **Fixed arm (`iso/invest-core-fixed/tests`)**: expected **exactly 2**
  failures, raw rc **1**, both in `tests/test_revenue_adapter.py`, neither
  test rewritten:
  1. `test_current_revenue_workflow_receipt_is_transferred` — it rebuilds a
     receipt with `attestation_status="host_signed"` via production
     `build_publication_receipt`, which CANNOT carry a record (issuance fix
     not promoted), and expects `adapt_revenue` to accept it. The guard must
     reject it: this is the false-green pattern the card exists to close
     (the analogue of I-08-A §7.1 / B1's required `test_attestation.py`
     failure).
  2. `test_growth_driver_summary_tampering_is_rejected` — CASCADE, declared
     in advance: the first test mutates the module-cached `"growth"` fixture
     IN PLACE (label→`host_signed`, no record) before failing, and this test
     consumes the same cached object afterwards, hitting the same guard.
  Any OTHER new failure on the fixed arm is an oracle violation: stop,
  investigate, disclose — do not accept it as expected collateral.

## 6. Mutation (frozen)

**M1 — remove the guard.** One exact literal edit to
`iso/invest-core-mutant/scripts/invest_contracts.py`: delete the
verification call introduced by the patch in `adapt_revenue` (the
`verify_host_signed_attestation(receipt)` invocation and its guard
condition), restoring the original unconditional
`attestation_verification = "host_signed"` acceptance. The rest of the patch
(constants, helper) may remain; the mutation must remove the enforcement.

- Declared red on the mutant (same file, same fixtures): the same 7 nodes
  {R1a, R1b, R2, R3, R3b, R4, R5}; declared green: {P1, B1, B2}; raw rc **1**.
- Method: fresh copy of `iso/invest-core-fixed` → `iso/invest-core-mutant`,
  apply the exact revert (verified present before applying), run the SAME
  frozen test file. Observed red set must EQUAL the declared red set exactly
  (no missing, no extra). `iso/invest-core-fixed` stays byte-stable.

## 7. Anchors (frozen)

All four located consumer copies are byte-identical:

```
9ad8a146ab1535555b7fd74a14acbb8280c21d4eb22e3e92da3ab2965ba3cc45  102388 B  2689 lines
  C:\Users\郑曾波\.agents\skills\invest-core\scripts\invest_contracts.py
  C:\Users\郑曾波\.claude\skills\invest-core\scripts\invest_contracts.py
  C:\Users\郑曾波\.codex\skills\invest-core\scripts\invest_contracts.py
  C:\Users\郑曾波\Projects\invest-skills\invest-core\scripts\invest_contracts.py   (git repo, HEAD 0ee17137f8575b48064051a5ed951073c717cb42, clean porcelain)
iso copy: iso/invest-core/scripts/invest_contracts.py — same sha256 (verified at copy time)
```

Full before-run anchor table: `before/production_anchors.json` (RF runtime
files pinned identical between `~/.agents/skills/revenue-forecast` and the
Projects repo; RF registry `bc3256bb…`; trust anchor ABSENT in repo config,
install config and iso config; both git porcelains empty at freeze time).

## 8. Input pins

- B1 reviewer report: `execution_runs/B1-I08C-product-fixes/a20260921-01/reviewer_report.md`
  — byte-pinned by its own §10 protocol (final-byte form sha256
  `73feb0593b44ffeb448bc5f5b1cea9800f4cc9fb59f40ca19e9aae8038c104fa`,
  37135 bytes with the REPORT_SHA256 line reading PENDING).
- Owner ruling: `OWNER_DECISIONS.md` §16 line 「E-3 = 立卡 | invest-core 消费者卡
  （跨仓）| 与建议一致（补丁+红绿在隔离副本，合入待该仓 owner）| 派卡」, verbatim quote
  block 「…E-3: 立卡…」.
- Record shape source: B1's delivered fixed tree
  `iso/fixed/rf/scripts/revenue_publication.py` lines 147–333 (E27/G4).

## 9. rc legend and expected exit codes (frozen)

pytest rc: `0` = all collected passed, `1` = at least one test failed.
No harness-only code is expected for the five test commands.

| command id | what | expected rc |
|---|---|---|
| IC-c0 | anchors + freeze (hashing only) | 0 |
| IC-c1 | RED: frozen test file vs `iso/invest-core` | 1 (7 failed / 3 passed) |
| IC-c2 | GREEN: frozen test file vs `iso/invest-core-fixed` | 0 (10 passed) |
| IC-c3 | regression suite vs pristine | 0 (contingency §5) |
| IC-c4 | regression suite vs fixed | 1 (exactly the 2 declared §5) |
| IC-c5 | mutation M1 run | 1 (same 7 red) |
| IC-c6 | changes.diff generation + round-trip `git apply -p1` on a COPY | 0 |
| IC-c7 | post-run production/install zero-write re-hash | 0 |

## 10. Boundaries (frozen)

All repos and install surfaces READ-ONLY: the fix exists only under this
attempt (`iso/`, `changes.diff`). No writes to
`Projects/invest-skills`, any `.agents/.claude/.codex` skill root, or the
revenue-forecast repo outside this attempt directory; no `git` write command
(add/commit/checkout/stash/restore/…) anywhere; the production registry is
never appended to (env redirection in `conftest.py` before any import);
`config/trusted_signer_public_keys.json` is never created anywhere. This card
NEVER self-signs: the only signatures produced anywhere are ephemeral
fixture signatures inside the pytest tmp dir for node P1 (and its negative
derivatives), with a throwaway key that exists only in test memory/tmp.
`handoff.json` ships with `status=review_pending`,
`merge_authority="invest-core owner — NOT yet approved; this card delivers a
patch, not a merge"`, `disclosure_adaptation=unmapped`, `accuracy=unproven`.


---

## Revision r2 (append-only; r1 byte range untouched)

Appended after IC-c3/IC-c4, i.e. after the first regression measurements, to
execute the two commitments r1 §5 pre-registered. **No r1 security
expectation is relaxed by this revision**: the node table (§4), the mutation
declaration (§6) and the boundaries (§10) are untouched. Proof of append-only:
sha256 of `oracle.md[0:16936]` remains
`7eaf81b925f21c21ba3f320111f3ea57c54dd74292a4ec5697111d0476f47796`
(the frozen r1 digest), recorded in `scratch/append_oracle_r2.json`.

### r2.1 — §5 pristine contingency ACTIVATED (measured baseline recorded)

Measured pristine arm (UNFIXED consumer, `before/suite_pristine.stdout.txt`,
raw rc 1): **6 failed / 35 passed / 1 skipped / 7 subtests passed**.

The six failures: `test_company_adapter_copies_validated_paths`,
`test_management_target_summary_is_hashed_and_transferred`,
`test_segment_adapter_copies_recognized_revenue`,
`test_segment_adapter_prefers_revenue_owned_effective_path`,
`test_tampered_forecast_is_rejected`,
`test_unregistered_anchor_opt_out_is_explicit_and_traced`.
Every one is the PRE-EXISTING default-policy rejection: in a clean
environment (no `REVENUE_ATTESTATION_PROVIDER` anywhere — verified at IC-c0)
`run_forecast` fixtures are `unattested`, and these six tests expect
`adapt_revenue`'s default `require_attestation=True` to SUCCEED
(`test_tampered_forecast` fails only because the `unattested` rejection
preempts its expected `invalid revenue forecast` message). This is
pre-existing suite behavior in a clean environment — it reproduces on the
UNFIXED consumer, so this card cannot be its cause. Fix-attribution is
therefore by DELTA pristine→fixed, exactly as the r1 §5 contingency
prescribes.

### r2.2 — §5 fixed-arm declared set CORRECTED from 2 to 3 (r1 under-count disclosed)

Measured fixed arm (`after/suite_fixed.stdout.txt`, raw rc 1):
**9 failed / 32 passed / 1 skipped**. Delta vs pristine =
**exactly 3 new failures, 0 disappeared** (Compare-Object of the FAILED
lists), all three raised through `verify_host_signed_attestation` with the
identical coded message `attestation_missing_record … (E27)`:

1. `test_current_revenue_workflow_receipt_is_transferred` — **as declared in
   r1** (the mutator: it rebuilds a receipt with `attestation_status=
   "host_signed"` via production `build_publication_receipt`, which cannot
   carry a record; fails at its own `adapt_revenue` call, test line 130).
2. `test_growth_driver_summary_tampering_is_rejected` — **as declared in r1**
   (cascade: consumes the module-cached `"growth"` fixture the mutator
   mutated in place).
3. `test_growth_driver_tree_is_hashed_and_compacted` — **NOT declared in r1**.
   Same root cause, same cache: alphabetical method order runs the mutator
   first, and this is the SECOND later consumer of the polluted cached
   fixture (`growth_driver_summary` < `growth_driver_tree`; r1 counted only
   the first). Disclosed as an r1 under-count of the declared cascade, not
   absorbed silently. No test byte changed in either arm — `tests/` and
   `tests_support/` are byte-identical across arms (5/5 files,
   `after/tests_identity.json`).

The authoritative fixed-arm expectation is now: 6 pre-existing failures (r2.1)
+ these 3 fix-attributable failures = 9 failed, rc 1, with `tests/`
unmodified. Reviewer adjudication requested specifically on r2.2: is
counting the third cascade consumer as the same declared root cause
legitimate, or should the mutator test's in-place fixture mutation be called
out separately as a test-design finding against the shipping suite?
