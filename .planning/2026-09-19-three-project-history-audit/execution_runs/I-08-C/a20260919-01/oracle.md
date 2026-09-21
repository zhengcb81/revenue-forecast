# I-08-C Oracle — frozen BEFORE the pytest run

- Card: `execution_v2/card_I-08-C.md` — consumers must reject forged receipts,
  cross-payload replay, and unsigned structures.
- Frozen at: 2026-09-19, derived ONLY from reading the production sources listed
  below (no code was executed before this file was written).
- Run interpreter: `C:\Miniconda\python.exe` (Python 3.13.9, pytest 9.1.1). No venv.

## Production anchors under test (READ-ONLY, referenced by path)

| Anchor | Function | SHA-256 on disk now | Card anchor | Match |
|---|---|---|---|---|
| `scripts/revenue_publication.py:185` | `validate_publication_receipt` | `183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba` | same | YES |
| `scripts/revenue_report.py:1196/1239` | `validate_published_forecast` / `validate_forecast_output` | `a85fb48482216dca3f9269ee81b6d8204f419b454b64aaac14412151f00d971f` | same | YES |
| `scripts/publication_registry.py:188` | `is_registered` | `29aaae4f9864d9c4dbb92720744daa49315a2980dfa158b0e3666cb86d886344` | `446627442500001e955a4c132f9c288524f3949d7cf94c1cb9b957fd6ad2d0aa` | **DRIFT** |

The registry drift is pre-existing: git log shows `1dbae639` (feat ZR-701)
touched `publication_registry.py` after the card froze its anchor. `is_registered`
still exists at line 188 with the same contract (fail-closed on corruption), so the
card is executable against the current file; the drift is reported, not repaired.

## Fixture plan (S / U / D, clone-mutate from S per card)

- Input: synthetic `forecast_document()` (repo test helper, direct_revenue segments).
- **S** = `run_forecast(doc)` formal with `REVENUE_ATTESTATION_PROVIDER` set to a
  runnable executable → the production issuer itself stamps `attestation_status`
  `host_signed`. No signature is forged; no expected value recomputed by helpers.
- **U** = same document, formal, provider absent → `unattested`.
- **D** = `run_forecast(doc, mode="draft")` → `build_draft_receipt` (empty gates).
- **S2** = mutated parameter value (×1.05) → different input anchor; formal.
- Mutations in tests are clones (`copy.deepcopy`); the original fixtures are never
  mutated in place.
- `REVENUE_PUBLICATION_REGISTRY` is redirected to a pytest temp file for the whole
  run because formal `run_forecast` **registers** publications; this keeps the
  production `artifacts/registry/publications.jsonl` READ-ONLY.

## Frozen expectations (per case, card table A-C1..A-C5)

> **Revision r2 (pre-verdict freeze):** one exploratory run (12 tests, 8 passed)
> was executed to validate fixture mechanics. It revealed the E6 forgery vector
> first chosen (`segments[0].base_revenue`) is NOT bound by any output gate for
> direct_revenue segments — pinned as new case E13 below. E6 now uses the
> top-level `base_revenue`, which IS bound (consolidated paths and CAGR are
> recomputed from it, `revenue_report.py:543/611`). The expectations below are
> frozen again BEFORE the verdict run; no expectation was copied from a green
> run — E13's "accepted" is the pinned result of the exploratory run and is
> reported as a finding, not derived from production helpers.

| # | Case | Expected outcome (exact gate) |
|---|---|---|
| E1 | A-C1: S legit, hashes/trusted domains consistent | `validate_publication_receipt(S)` passes; `validate_forecast_output(S)` passes; repeat read passes again; `S["publication_receipt"]["attestation_status"] == "host_signed"` |
| E2 | A-C3: payload value mutated, original receipt kept | `ForecastInputError` — `validated_payload_sha256 mismatch` |
| E3 | A-C3: `gate_ids` mutated (sensitivity gate appended) | `ForecastInputError` — `gate_ids mismatch` |
| E4 | A-C3: `verification_context_sha256` mutated | `ForecastInputError` — `verification context mismatch` |
| E5 | A-C3: S1's whole receipt replayed onto S2's payload | `ForecastInputError` (payload/anchor mismatch at receipt layer) |
| E6 | A-C3 core: attacker mutates a result VALUE and recomputes every non-secret self-hash (`validated_payload_sha256`, `receipt_sha256`, `result_sha256`) but keeps the original signed domain (`validated_input_sha256`, `verification_context_sha256`, `gate_ids`) | Receipt layer alone PASSES (hash-consistency only — **recorded limitation**); the real consumer dispatcher `validate_forecast_output` **REJECTS** (output recomputation from embedded input). Recomputing non-secret hashes does NOT repair the forgery. |
| E7 | A-C4: registry already holds S's anchor; same-anchor forged package presented | `is_registered(S.input_sha256)` is True AND `validate_forecast_output(forged)` raises — registration alone never admits a package |
| E8 | A-C5: S1's receipt grafted onto S2 with self-hashes recomputed but OLD verification context kept | `ForecastInputError` — `validated_input_sha256 mismatch`; dispatcher also raises |
| E9 | A-C2: D (draft receipt, empty gate_ids) to a formal consumer | `validate_publication_receipt(D)` raises `gate_ids mismatch`; `validate_forecast_output(D)` raises (formal-only entry) |
| E10 | A-C2: unsigned structure — result without `publication_receipt` | `ForecastInputError` — `missing field: publication_receipt` |
| E11 | A-C2: U with ONLY `attestation_status` flipped to `host_signed` (+ self-hashes recomputed) | **KNOWN GAP (finding, frozen pre-run):** both the receipt validator AND the strong dispatcher PASS, because the attestation label is a plain string checked only for set membership (`revenue_publication.py:222-226`); the capability gate exists only at issuance (`revenue_core.py:167`, `attestation_capability()` False without provider). Consumers requiring a *trusted formal* package have no consumption-side verification in this tree — this is the I-08-B follow-up surface, reported to the reviewer, NOT counted as a pass of the security property. |
| E12 | registry fail-closed | Tampered registry line → `is_registered` raises `RegistryError` (fail-closed; `lookup` shares the same `_read_entries` gate) |
| E13 | **pinned gap:** self-hash-consistent forgery of `segments[0].base_revenue` (direct_revenue) | Receipt layer passes AND `validate_forecast_output` **ACCEPTS** — the segment-level base feeds no recomputation comparison (`revenue_report.py:442` recalculates *from* it; nothing compares it to the input or stored modeled activity). Reported to reviewer as gate-coverage finding. |

## Scope notes (frozen)

- No production file is modified; the test file lives only in this attempt dir.
- invest-* consumers are out of scope for this run (owner cards), per card.
- The card's "真实消费者入口" for this repo is the validation dispatcher chain
  (`validate_forecast_output` → `validate_published_forecast` → receipt/recompute
  gates) plus `is_registered`; no separate CLI entry is exercised (T-PUB-equivalent
  node = this pytest node).
