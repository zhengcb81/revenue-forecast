# decision.md — INVEST-CORE-ATTEST-GATE

Card: **INVEST-CORE-ATTEST-GATE** (cross-repo, REM-01 consumer side)
Attempt: `execution_runs/INVEST-CORE-ATTEST-GATE/a20260922-01`
Status of this document: design rationale for the patch delivered in
`iso/invest-core-fixed/` + `changes.diff`. Expectations live in `oracle.md`
(frozen first); this file explains WHY that shape was chosen.

---

## 1. The choice the task posed

> require the binding record whenever the label is `host_signed`
> (or, if the record shape cannot be verified from this repo alone, make the
> label explicitly non-evidentiary and require an explicit
> verified-signature field — choose with rationale, mirroring B1's REM-01
> remedy)

**Decision: remedy A, in its FULL mirror form** — whenever a non-legacy
package claims `attestation_status == "host_signed"`, the consumer requires
a `publication_attestation` record and verifies it end-to-end: closed
10-field shape → constants and formats → payload binding (E16) → Ed25519
signature against the trust domain (E14/E20) — every path fail-closed.
Implementation: `verify_host_signed_attestation(receipt)` called from
`adapt_revenue` (both hunks of `changes.diff`).

## 2. Why the record shape CAN be verified from this repo alone

- **Shape, constants, formats, payload binding**: fully computable inside
  invest-core. The record's closed field set, the domain separator
  `revenue-forecast/publication-attestation/v1`, schema `1.0`,
  `algorithm=ed25519`, hex/RFC3339 formats, and the E16 binding
  (`record.payload_sha256 == receipt.validated_payload_sha256`) need only the
  receipt that adapt_revenue already holds and invest-core's own
  `canonical_sha256` (byte-identical algorithm to revenue-forecast's —
  both `ensure_ascii=False, sort_keys=True, separators=(",", ":")`).
  So the alternative remedy's precondition ("shape cannot be verified from
  this repo alone") does not hold.
- **Signature verification is reachable without creating any new trust
  authority**: the public-key set loads through the revenue runtime's single
  loader `contracts.evidence._trusted_signer_public_keys()`
  (`REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS` env, else the runtime's
  `config/trusted_signer_public_keys.json`; missing file ⇒ zero signers).
  invest-core already imports revenue primitives through
  `invest_contracts.revenue_runtime()` by design (skill hard rule), so this
  reuses the one loader instead of adding a second trust path. The Ed25519
  primitive comes from `cryptography` (50.0.1 present), imported lazily and
  fail-closed on ImportError — the same optional-dependency pattern B1's
  fixed revenue-forecast code uses.

## 3. Why not the alternative (label non-evidentiary + explicit verified-signature field)

Rejected for three reasons:

1. **It would be the same spoofable string wearing a different name.** An
   explicit `signature_verified` field, if checked for truth by the consumer,
   is another producer-controlled value inside the very receipt an attacker
   already forges (the receipt is self-hashed, non-secret — B1's REM-02
   established exactly this). It moves the claim without moving any
   verification, i.e. it re-creates the REM-01 defect with a longer field
   name.
2. **It would not mirror B1's REM-01 remedy.** B1's delivered fix at both
   revenue-forecast consumer entry points requires the record *and verifies
   the signature against the trust domain* (`validate_publication_attestation`).
   The card asks for the consumer-side counterpart of that fix; the
   field-declaration variant is strictly weaker than what issuance-side
   revenue-forecast will enforce once promoted.
3. **Structural-only variants are bypass theater.** A middle option — require
   the record but check only its shape — was also rejected: any attacker who
   can flip `attestation_status` can equally append a junk 10-field record
   with a random 128-hex signature. Structural-only would stop exactly one
   attacker (B1's broken-issuance artifact, which carries no record at all)
   and silently pass every deliberate forger. The signature check is the part
   that actually binds the claim to a key outside the artifact; without it
   the guard adds friction, not security.

## 4. Design points and their rationale

- **Placement after content validation** (`revenue_reference(result)`): the
  shipping test `test_forged_sensitivity_artifact_is_rejected_cross_repo`
  pins the rejection MESSAGE `invalid revenue forecast` for content-forged
  `host_signed` packages; running the content strong-validation first keeps
  that surface intact while the (content-valid) label forgery this card
  closes is still rejected by the guard. No security is lost: both classes
  of forgery are rejected either way; only the order of which error fires
  first differs. This also minimized fix-attributable regression churn to the
  declared set (oracle §5, corrected in r2.2).
- **Fail-closed on missing anchor / missing crypto / missing loader.**
  Mirrors issuance semantics: revenue-forecast's fixed issuance can only
  stamp `host_signed` when a trusted key verified a handshake, so a
  record-bearing package presupposes an anchor at issuance; consuming without
  that anchor would be key-continuity breakage, and rejecting is correct.
  **Disclosed production consequence:** today no anchor exists anywhere
  (I-08-A R-PROV-2) and no record-bearing package exists at all (issuance fix
  not promoted), so after a merge every current `host_signed` package is
  rejected at invest-core consumption until (a) the issuance fix is promoted
  and (b) an anchor is deployed. That is the intended fail-closed outcome of
  this card, not a regression.
- **Legacy bypass untouched** (lines 1116/1131–1133): OPEN-D6's
  R-LEGACY-1/E29 path is a separate defect with its own cross-repo
  authorization (T2-10) and is outside this card's frozen oracle. A legacy
  package's label already carries no authority (`legacy_read_only`).
- **`issuer`/`key_id` are format-checked but not bound to the trust entry
  (no E21)**: the production loader returns a fingerprint→key map with no
  identity fields, so identity binding is not implementable from this repo
  alone. This mirrors B1 exactly and inherits their disclosed F3 finding —
  the claim is not made anywhere in the code (no E21 listed in the new
  docstring), so there is no docstring-vs-behaviour mismatch.
- **Adapter enum unchanged**: success still records
  `attestation_verification == "host_signed"`; passing the gate now IMPLIES
  verification. No downstream artifact schema change ⇒ the patch stays
  mergeable without a schema bump (a receipt schema bump remains I-08-A
  OPEN-D4's question, listed in handoff open_questions).

## 5. "Never self-sign" — what was signed, exactly, and why that is not this card signing anything

The oracle's positive control (P1: a valid record must PASS) cannot exist
without *some* signature verifying against *some* anchor. This card:

- uses a **throwaway fixture key derived in test memory**
  (`b"\x23"*32`, Ed25519) — never written to any file in any repo or install
  surface;
- writes its public part only into a trust file under the **pytest tmp
  dir**, passed via `REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS` (B1's reviewer used
  the identical pattern: "private key never leaves my scratch dir");
- produces signatures **only inside its own test runs**, for its own
  fixtures, claiming issuer `invest-core-attest-gate-fixture` — no production
  trust anchor is created, read, or modified anywhere
  (`config/trusted_signer_public_keys.json` remains ABSENT in the repo, the
  install surfaces and the iso copy — re-verified after all runs in
  `after/production_anchors.json`).

No attestation, receipt, or artifact outside this attempt's test processes is
signed by anything this card runs; the card performs no git write and no
merge — the delivered object is a patch.

## 6. What a merge would mean (explicitly NOT done here)

`changes.diff` (10372 B, sha256 `009debc2…`) applies with
`git apply -p1` at the invest-skills repo root and at each installed skills
root (all three `--check` clean). Merging it would:

1. close the REM-01 consumer gap on all four located copies;
2. break exactly the three declared shipping tests (oracle §5/r2.2) — all
   three mint `host_signed` without a record through production issuance or
   consume the fixture that did; the merge owner must adjudicate them
   (they are the false-green pattern the card exists to close, plus two
   shared-cache cascades from the first one's in-place fixture mutation);
3. make every current production `host_signed` package fail closed at
   invest-core consumption (§4) until the issuance fix is promoted and an
   anchor is deployed.

The invest-core owner decides all of that. This card does not self-merge.
