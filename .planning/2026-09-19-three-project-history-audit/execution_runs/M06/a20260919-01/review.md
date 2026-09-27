# M06 · implementer review record

Card M06 (`usage_platform`), Parent I-10. Attempt `execution_runs/M06/a20260919-01`.

> ## PENDING independent review
> **Nothing in this file is an acceptance.** The implementer is not the reviewer. `formula` is recorded as
> `review_pending`; `disclosure_adaptation` stays `unmapped`; `accuracy` stays `unproven`.
> A separate session must read the artefacts below and issue its own verdict
> (`accepted_scoped` / `changes_required` / `blocked` / `not_applicable_with_reason`).

## 1. What was done

| Step | Result | Evidence |
|---|---|---|
| A binding | production code copied read-only into an attempt-local snapshot; hashes recorded and equal | `binding.json`, `evidence/M06/source_manifest.json` |
| B positive | `[23.0]` vs independent oracle `[23]`, within `1e-9*max(1,|e|)` | `evidence/M06/formula_result.json` |
| continuity positive | actual `[23.0, 44.0]` vs oracle `[23, 44]` | `evidence/M06/negative_results.json` |
| defaults case | actual `[20.0]` vs oracle `[20]` (not gating) | `evidence/M06/negative_results.json` |
| C negatives | 11/11 rejected with `ModelRegistryError` | `evidence/M06/negative_results.json` |
| D mapping | one real disclosed mapping with page, span, unit, period and PDF sha256; professional decisions written as PROPOSED only | `evidence/M06/disclosure_mapping.json`, `evidence/M06/accounting_decision.md` |
| E probe | recorded as `blocked` with the concrete reason; NOT a scenario set and NOT accuracy evidence | `evidence/M06/historical_mapping_probe.json` |
| F accuracy | **NOT DONE** - needs the I-12 frozen design | `evidence/M06/qualification.json` |

## 2. Independence of the oracle (the point of this card)

- Expected values come from `scripts/oracle_M06.py`, which imports only `argparse`, `hashlib`, `json`, `os`
  and `decimal` (see the `import_lines` list inside `evidence/M06/oracle_selfcheck.json`).
  It never imports `model_registry` or `model_extensions`; `product_import_present` is `false`.
- The runner `scripts/run_card.py` calls exactly one product function,
  `calculate_registered_model(model_id, base_revenue, drivers, years)`, and reads expectations only from
  `evidence/M06/oracle.json`.
- Negative cases are built in memory from a fresh `deepcopy` each time - never round-tripped through a JSON
  parser - so a JSON-parser rejection cannot masquerade as a model rejection (N01a uses a real `bool`,
  N01b-d use real `float('nan'/'inf'/'-inf')`).
- `PASS_rejected` requires `isinstance(exc, ModelRegistryError)`. `ImportError`, `ModuleNotFoundError` and
  `FileNotFoundError` are recorded as **FAIL**, never as pass.
- The same `run_card.py` (sha256 `fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a`) was used for M05-M08;
  there is no card-specific runner to drift.

## 3. Results in detail

- Registry formula observed from the isolated copy: `revenue = eligible_activity * monetization_rate + fixed_revenue`
- Registry required: `['eligible_activity', 'monetization_rate']`; optional: `['fixed_revenue']`; defaults: `{}`; driver_bounds: `{}`
- Rejections and their messages:
  - `NEG-CARD`: ModelRegistryError - `driver usage_platform.eligible_activity must be between 0.0 and inf: FY2027`
  - `N01a`: ModelRegistryError - `usage_platform.eligible_activity.FY2027 must be numeric`
  - `N01b`: ModelRegistryError - `usage_platform.eligible_activity.FY2027 must be finite`
  - `N01c`: ModelRegistryError - `usage_platform.eligible_activity.FY2027 must be finite`
  - `N01d`: ModelRegistryError - `usage_platform.eligible_activity.FY2027 must be finite`
  - `N02`: ModelRegistryError - `driver usage_platform.eligible_activity must contain one value per forecast year`
  - `N03`: ModelRegistryError - `missing drivers for usage_platform: eligible_activity`
  - `N04`: ModelRegistryError - `unsupported drivers for usage_platform: unknown_driver`
  - `N05a`: ModelRegistryError - `usage_platform.years must contain fiscal years`
  - `N05b`: ModelRegistryError - `usage_platform.years must contain fiscal years`
  - `CONT-BREAK`: ModelRegistryError - `usage_platform.years must be consecutive and increasing`

## 4. Observations (NOT pass/fail, recorded because they are design-relevant)

- `OBS-BASE-IGNORED`: raised=None actual=[23.0] matches_compared=True expect_equal=None matches_expected=None
  - why: rowwise calculator discards base_revenue; design observation only
- `OBS-RATE-GT1`: raised=None actual=[753.0] matches_compared=None expect_equal=None matches_expected=None
  - why: records empirically whether the implementation treats monetization_rate as a [0,1] probability; NO expectation and NO verdict is asserted

## 5. Judgement calls the reviewer should attack first

1. **`monetization_rate` is NOT constrained to [0,1].** The probe `OBS-RATE-GT1` (`rate=1.5`) returned
   `753.0`. That is consistent with the audit ledger's warning that the driver is money-per-activity, but it
   is **inconsistent** with the other ratio drivers in the same registry (`subscription.timing_factor` and
   `services.utilization` are both [0,1]). The reviewer should decide whether that asymmetry is intended
   contract or a gap; the implementer asserts no position and changed nothing.
2. **Zero-fill of `fixed_revenue`** (same mechanism as M05 item 3).
3. **The disclosed basis is qualitative only.** Tencent confirms the commission is a percentage of each
   transaction's value and publishes a principal-vs-agent policy, but no volume and no rate, so both required
   drivers are `missing` and the reconciliation is impossible without back-solving (circular).
4. **The GMV/take-rate trap is real for this issuer.** Because the policy is gross-or-net depending on the
   principal/agent call, an `activity x rate` product can be internally consistent and still be on the wrong
   accounting basis. This is the card's STOP condition and it is not resolvable from this document set.

5. **Isolated-checkout provenance.** I-00-B binds the isolation *plan* and the two-stage command rule but
   does not materialise a checkout tree; this attempt therefore materialises its own read-only snapshot
   (`iso/checkout_scripts`, hashes equal to production). If the intended binding is a checkout materialised by
   I-00-B, that is a scope deviation to record - the code under test is byte-identical either way.
6. **Disclosure receipt strength.** Unlike the cninfo sidecars used by M01, the company-wiki sidecars for
   these documents carry no publisher content hash, so `local_hash_matches_publisher_receipt` is
   `NOT_VERIFIABLE` for all four cards. Stated as a gap.

## 6. What this card does NOT claim

- It does **not** claim the model is accurate, nor that one company's mapping generalises.
- It does **not** claim `disclosure_adaptation`; D needs a signed industry/accounting review plus a production
  forecast-entry-point mapping reviewed independently.
- It does **not** rewrite the formula. With no independent counter-example and no adjudicated specification,
  the existing implementation is retained.

## 7. Reviewer checklist (suggested)

1. Re-run `scripts/oracle_M06.py --card M06 --out-root <attempt>` in a scratch tree and diff the generated
   `oracle.json` against the frozen one; then re-run `scripts/run_card.py` and diff `run_result.json`.
2. Confirm the isolated copy hashes still equal production (`evidence/M06/source_manifest.json`).
3. Confirm `oracle.md` was not edited after the run (hash in `commands.json` / `source_manifest.json`).
4. Pick a case the implementer did not use and freeze its expectation BEFORE running.
5. Adjudicate the DEC items in `evidence/M06/accounting_decision.md`.

---

## Exit-code self-check (shared runner; self-check performed on M05)

| case | mutation | raw rc | expected | proves |
|---|---|---|---|---|
| A | `oracle.json positive.expected_float -> [999]` in a scratch copy | **3** | 3 | a corrupted expectation cannot hide behind rc=0 |
| B | `input.json` positive driver deleted in a scratch copy | **2** | 2 | rc=2 is reachable: no verdict exists |
| C | uncorrupted scratch copy | **0** | 0 | the repaired exit code stays 0 for a genuinely passing card |

Details: `execution_runs/M05/a20260919-01/recovery/selfcheck_result.json`.

---

## revision r2 - response to the independent review

Independent review of r1: **accepted_scoped (formula qualification only)**.

The nine r1 findings were handled as follows (nothing frozen was rewritten, no product file was touched):

- F-M06-01 (source_manifest wording)
- F-M06-02 (review.md exit-code section title)
- OQ-02 ruling

Details per finding (file:line) are in `evidence/M06/revision_r2.json`; the OQ-02 / OQ-04 rulings are in
`evidence/M06/oq_rulings.json`; the owner's three-step index remediation for M08 is in `handoff.json`.

New hashes after r2: `oracle.md`, `commands.json`, `after/rerun_sha256.json` and `evidence/M06/*` were all
re-hashed; see `evidence/M06/evidence_hashes.json` and `after/rerun_sha256.json`.

Status after r2: `formula` = review_pending (point review of r2), `disclosure_adaptation` = unmapped, `accuracy` = unproven.

---
## 独立验收裁定 · r2 态（M-T-REVIEW 点复审 · 2026-09-23）
- 结论：accepted_with_conditions —— 仅 formula、仅 r2 态、仅锚 9ec65295…。本块为缺失的 r2 点复审确认轮。
- carried：F-MT-01/02/03；F-MT-04/05 由本块闭合。OQ-02（monetization_rate）裁定 = 命名歧义非契约缺口，采信。
- 本次抽验：[23] 三方一致；负例 11/11；九件齐；pin 3/3（CRLF）；无产品重写。
- status_authority: { status: "accepted_scoped", reviewer_status: "r2 point review returned by M-T-REVIEW (N=1) 2026-09-23: accepted_scoped (formula only)", carrier: "…/reviews/M06.md + acceptance_rulings.md#M06", implementer_signed: false, supersedes: "review_pending (point review of r2)" }
— 独立审查员 M-T-REVIEW / N=1
- install_record (carrier landing batch 2026-09-23 | M-T-REVIEW/a20260923-01): append-only flip per landing_package/README.md; prefix proof: pre-append sha256 a0985855ee9d7177bf2681e096b6ec56f369677c664b9d6fff93fa95b499abef over 9099 bytes, verified post-install as sha256 of the first 9099 bytes of this file (PASS/FAIL + post sha in install_log.jsonl); F-RV-02 block_sha256 = 2164346e45a3e02d6a9b056bbedb9b394607a789a576e4ae4be1bc80897710a6 = sha256 of the appended block body above (header ## 独立验收裁定 line through the signature line — 独立审查员 M-T-REVIEW / N=1, LF-terminated, 776 bytes); F-RV-03 verdict_is_transcribed_not_authored: true; block transcribes the signed ruling carried by M-T-REVIEW/a20260923-01/reviews/M06.md (sha256 a6fcb761df72cb6c8d3a5db92cb0c4fead6b55a85f03f8c0b43f0616da6b9bf0) + acceptance_rulings.md (sha256 257e47da5f2924c2f6079f093c6884aa8ecc37a6eab2ce044c7fc26130e5495b); installer authors no verdict and signs nothing (never self-sign)
