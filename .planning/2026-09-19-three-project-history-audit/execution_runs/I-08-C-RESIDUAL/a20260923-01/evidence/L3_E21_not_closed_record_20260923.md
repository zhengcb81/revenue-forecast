# L3 (B1 review F3) — dated closure record: **E21 is recorded as NOT CLOSED**

- Date: 2026-09-23
- Author: I-08-C-RESIDUAL closure agent (this attempt; not a reviewer verdict)
- Condition being closed (verbatim, `B1-I08C-product-fixes/a20260921-01/reviewer_report.md` §9.3):
  "either implement E21 (`issuer`/`key_id` vs the resolved trust entry) or delete the
  E21 claim from the docstring and list it under 'not closed'."
- Form of closure: the condition's option (b), split by authority:
  1. **"list it under 'not closed'" — DONE, this file is the dated record.**
  2. **"delete the claim from the docstring" — landed as ready-to-apply patch `P-L3`**
     (`patches/P-L3_delete_E21_docstring_claim.patch`, exact one-clause change against
     the current promoted bytes `bc2bb4a3…`). Application is a production write; goal
     discipline ⑤ (生产零合并) and OWNER_DECISIONS.md:426 (父保留各仓提交权) reserve
     that to the parent's production batch. NOT applied by this card.
- Option (a) "implement E21" = **stopped at its honest label (BLOCKED-on-cap-change)**:
  `contracts/evidence._trusted_signer_public_keys()` resolves `fingerprint -> public_key`
  only (measured, `evidence/E_L3_trust_loader.json`); comparing the record's
  `issuer`/`key_id` "with the trust entry it resolved" requires the 12-field trust-entry
  schema (I-08-A E25, recorded NOT implemented, decision.md §6 of B1: "NOT implemented —
  recorded open"). That is a trust-schema capability change = a product-card decision,
  already routed on the E21 product-card track by the parent's REM-42 closure
  (REMEDIATION_REGISTER.md §28: "E21 实现=独立产品卡仍开放（残留转产品卡轨道）").

## Status of E21 as of 2026-09-23 (measurement domain: current on-disk bytes)

- Documented: YES — `validate_publication_attestation`'s docstring lists
  `issuer_key_binding_mismatch (E21)` (`scripts/revenue_publication.py:235-236`).
- Raised anywhere: **NO** — zero `raise` sites mention E21
  (`evidence/E_L3_e21_scan.json`, both production and B1 fixed-copy scans).
- `issuer` / `key_id` cryptographically bound: **NO** — both sit outside the signed
  canonical request field set (measured: `issuer_key_id_in_signed_request = {issuer: false,
  key_id: false}`), consistent with the reviewer's F3 measurement (a renamed `issuer`
  verifies fine).
- Loader capability: NO issuer/key_id fields in the trust domain (see above).

**Recorded verdict for the register/§7-style listing: `E21 — NOT CLOSED (documented
claim deleted-or-annotated by patch P-L3; implementation = product card, cap-change
blocked here).`** Security impact unchanged from the review: the label cannot be forged
(fingerprint must be in the trust domain and the Ed25519 signature must verify); the gap
only lets a party already holding a trusted key rename itself in the record.
