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

<!-- ================= APPEND-ONLY BELOW THIS LINE ================= -->
<!-- Everything above this marker is the r1+r2 frozen body and is NOT edited by
     revision r3. Body = first 6831 bytes, sha256
     478bd70e0a1dfbfb924ebec0175bb2bdcdd199880de1c554de099d8ac8723c90.
     The append copies this file to oracle.md.r2_frozen_copy.txt and proves the
     frozen prefix byte-for-byte; see section R3-5. -->

# Revision r3 — E4 IMPLEMENTED (post-verdict remediation of the deliverable)

- Author of this append: I-08-C implementer (remediation round after an
  independent `changes_required` verdict). **Not** the reviewer.
- Appended at: 2026-09-21, container clock `2026-09-21T19:26:02Z` (local
  `2026-09-21T20:26:02Z`). Container clock is UTC+8 against a UTC-stamped
  filesystem here; all absolute times below are **filesystem** times.
- Trigger: independent `review.md` (sha256
  `c1a8fd11b20f911c7407943dabe70bc493a9cb2959719c13beef21f8e7f1f2a3`) item (4)
  "Re-freeze the oracle with E4 either implemented or explicitly withdrawn, and
  preserve the exploratory run log", and `unverified_list` item 4 (E4 absent).
- Discipline: append-only. The r1/r2 body above is untouched and its prefix is
  hash-proved in R3-5. No r1/r2 expectation is revised, withdrawn or relaxed.

## R3-1 Disposition chosen: **IMPLEMENT E4** (not withdraw)

The reviewer allowed either branch. Implement is chosen because E4's mechanism
exists in production and is testable in one node, so withdrawing it would
knowingly drop a card-mandated case (A-C3 每个被签域变异拒绝) from the matrix.

**E4's expectation is UNCHANGED from the r1 freeze** (line 54):

> E4 | A-C3: `verification_context_sha256` mutated | `ForecastInputError` —
> `verification context mismatch`

This append adds detail and a derivation record; it does not re-pin the outcome.

## R3-2 E4 derivation (independent re-derivation, `expected` NOT produced by the SUT)

`expected` is taken from the production **source text**, not from calling the
receipt builder to generate an expected value:

- `scripts/revenue_publication.py:232-240` (sha256
  `183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba`): for
  `formal_output_mode == "formal"` the validator builds the expected
  `VerificationContext(result["input_sha256"], expected_publication_gates(result),
  ENGINE_VERSION)` and requires the stored `verification_context_sha256` to equal
  `expected_context.context_sha256()`, else
  `"publication_receipt verification context mismatch"`.
- `scripts/revenue_publication.py:85-93`: `context_sha256()` is
  `canonical_sha256(self.to_dict())` and `to_dict()` uses the key
  **`executed_gate_ids`** (not the receipt's `gate_ids`).
- `scripts/revenue_publication.py:43-54`: for this fixture
  `expected_publication_gates(result) == ("output_recomputation",)` because the
  result carries no `sensitivities`.

Derivation evidence (probe, **not** the frozen evidence run, stdout kept):
`scratch/e4_derivation_probe.py` → `scratch/e4_derivation_probe.stdout.txt`,
run with `C:\Miniconda\python.exe`, raw return code 0:

| Probe case | Observed | Meaning |
|---|---|---|
| E4a `verification_context_sha256` ← `"0"*64` | RAISED `ForecastInputError: publication_receipt verification context mismatch` at the receipt layer; dispatcher raises the same | the field is not settable by an outsider |
| E4b E4a + every non-secret self-hash recomputed | RAISED `...verification context mismatch` | re-hashing does not repair the mutation (card A-C3 clause) |
| E4c production `context_sha256` vs independent reconstruction over literal keys `{validated_input_sha256, executed_gate_ids, validator_version}` | `a70d6f66802c6709f8ec79cd7c86685c95679993e8cf09ee6ccc8a0380568355` == `a70d6f66…` | the recomputation is derivable from source text, so no SUT-generated expected is used |
| control: unmutated S at the receipt layer | ACCEPTED | the record is evidence, not a rubber stamp |

**Disclosed self-correction (pre-freeze):** probe revision 1 reconstructed the
context dict with the key `gate_ids` instead of `executed_gate_ids` and reported
`E4c.equal = false`. The key was corrected by reading
`scripts/revenue_publication.py:85-90`; only revision 2 is recorded above and its
stdout is the archived one. This is logged because a probe whose "independent"
reconstruction silently disagrees with production is exactly the failure mode
the freeze discipline exists to catch.

## R3-3 E4 contract frozen for the r3 evidence run (node `test_e4_verification_context_mutation_rejected`)

Four assertions, all derived above; the node is **RED** (i.e. rc=3) if any fails:

| Id | Injected value | Frozen expectation |
|---|---|---|
| E4a | S clone, `publication_receipt.verification_context_sha256` ← `"0"*64` | `validate_publication_receipt` raises `ForecastInputError` matching `verification context mismatch`; `validate_forecast_output` also raises |
| E4b | E4a plus recomputed `validated_payload_sha256`, `receipt_sha256`, `result_sha256` | still `ForecastInputError` matching `verification context mismatch` |
| E4c | S clone, `verification_context_sha256` ← the context of a **different** input, i.e. `VerificationContext(S2.input_sha256, ("output_recomputation",), "4.1.0")` | `ForecastInputError` matching `verification context mismatch`; documents *which* wrong values are expressible (a valid context belongs to exactly one input) |
| E4d | S clone, `verification_context_sha256` ← the **correct** value `a70d6f66…` reconstructed inside the test from literals | receipt layer ACCEPTED — the field is necessary and sufficient for its own gate, so E4a–E4c fail for the right reason and not because the clone is broken |

E4 does **not** touch `attestation_status`; E11 remains the separate, still-failing
property (consumers do not verify attestation at all).

## R3-4 Frozen case → test-node map for the r3 evidence run (13 nodes)

| Case | Test node | Business rc under the frozen legend |
|---|---|---|
| E1 | `test_e1_legit_signed_package_passes_repeatably` | 0 (positive case passes) |
| E2 | `test_e2_forged_payload_with_original_receipt_rejected` | 2 (negative correctly rejected) |
| E3 | `test_e3_forged_gate_ids_and_context_rejected` | 2 |
| **E4** | **`test_e4_verification_context_mutation_rejected`** | **2** |
| E5 | `test_e5_whole_receipt_replayed_onto_other_payload_rejected` | 2 |
| E6 | `test_e6_recomputed_self_hashes_do_not_repair_value_forgery` | 2 |
| E7 | `test_e7_registry_anchor_does_not_admit_forged_package` | 2 |
| E8 | `test_e8_old_verification_context_on_other_input_rejected` | 2 |
| E9 | `test_e9_draft_package_rejected_by_formal_consumer` | 2 |
| E10 | `test_e10_result_without_receipt_rejected` | 2 |
| E11 | `test_e11_host_signed_label_flip_is_not_bound_at_consumption` | 3 — **property VIOLATED**, recorded as the card's negative result F1 (not a pass) |
| E12 | `test_e12_registry_fail_closed_on_corruption` | 2 |
| E13 | `test_e13_segment_base_revenue_not_bound_by_output_gates` | 3 — **gap pinned**, recorded as F3 |

`exit_code_legend` (frozen, START_HERE rc table): `0` pass · `1` harness failure ·
`2` no-verdict / correctly-rejected negative · `3` not as expected (应红未红 /
应绿未绿). Because pytest reports a single rc for the node set, the per-node
business rc above is classified from each node's assertions, and the suite-level
raw rc is recorded separately in `commands.json` / `handoff.json`. E11 and E13
are rc=3 by design: they are the pinned *product* gaps, and they are why this
card's handoff status is `changes_required` and not `accepted`.

## R3-5 Append-only proof and revision hashes

```
oracle.md pre-append bytes        = 6831
oracle.md pre-append sha256       = 478bd70e0a1dfbfb924ebec0175bb2bdcdd199880de1c554de099d8ac8723c90
test file pre-r3 bytes            = 8542
test file pre-r3 sha256           = 5dd5a96c415307e6abd1cc5eb2e1c05df3f35d1c929e5f098b672fa68a00864f
```

`oracle.md.r2_frozen_copy.txt` is a byte copy of the recorded r2 frozen body
(6831 B, sha256 `478bd70e…` — recomputed, matches). Mechanical proof via
`scratch/make_frozen_copy.py` → `scratch/make_frozen_copy.stdout.txt`, raw return
code 0, `append_only_proof: true`:

```
current oracle.md bytes            = 20377   sha256 867340f3e5ecca51b068c9edf17747ea35339c2e990fae49a54a228860e7c3dc
append region bytes                = 13545   (starts at offset 6832)
bytes[0:6831]  sha256              = 478bd70e…  == recorded r2 body  -> body untouched
bytes[6831:6832]                   = b'\n'      (whitespace only; the pre-append file
                                                 had no trailing newline, so normalising
                                                 it is the ONLY byte added before the marker)
current file starts with bytes[0:6832]         -> prefix intact
frozen copy (written from bytes[0:6831])       -> sha256 478bd70e…, equals recorded body
```

*(The byte/sha values above are the final r3 values, re-measured after the last
append-region edit; the earlier pass-1 figures and the reason for the second
measurement are disclosed in R3-8.)*

Proof is by **locating the append marker and hashing the fixed prefix**, not by
total-length arithmetic (that form was already caught wrong once in this plan —
see plan `findings.md` round 35 追加段 note 6). The same values are recorded
machine-readably in `handoff.json` under `append_only_proof`.

## R3-6 Exploratory-phase preservation (probe-side, filesystem-side)

See the new file **`exploratory_log.md`** in this directory: it inventories the
surviving artefacts of the exploratory 8/12 run, archives the ones that were
about to be overwritten by the r3 run, and lists explicitly what is **not**
recoverable. Summary of the honest position:

- **Not recoverable:** the exploratory run's stdout. It was never written to a
  file; the implementer-of-record kept only a prose summary in this oracle
  ("Revision r2": 12 tests, 8 passed) and in the original `handoff.json`
  `oracle.provenance`.
- **Surviving and now archived:** `.pytest_cache/v/cache/lastfailed` (already
  overwritten to `{}` by the r2 verdict run **before** this round — the loss
  pre-dates the remediation and is not caused by it), `.pytest_cache/v/cache/nodeids`
  (the r2 verdict-run node list, 12 ids), and both `__pycache__` `.pyc` headers
  (timestamp-based source id `1790017267` / size `8542`, i.e. the r2 frozen test
  file — so these are r2 artefacts, **not** exploratory artefacts).
- The exploratory run is corroborated only by the disclosed prose, the r2 freeze
  time and the pytest-cache write time; the independent review reached the same
  conclusion and adjudicated **no pre-registration violation**. Nothing in this
  round fabricates a log for it.
- **Full inventory with sizes, mtimes and sha256:** `exploratory_log.md` plus
  `exploratory_manifest.json` and the byte copies under `exploratory/`. Notable
  correction recorded there: **neither surviving `.pyc` is an exploratory
  artefact** — both carry the r2 source id (mtime `1790017267` / size `8542`), so
  the exploratory bytecode was already replaced before the r2 run.

## R3-7 What r3 does NOT change (scope)

- No production file is written, in any of the three repos. No git write command.
- No product finding is repaired: F1 (label never verified at consumption),
  F2 (`validate_publication_receipt` is hash-consistency only), F3
  (`segments[i].base_revenue` presentation-field coverage gap) and F4 (registry
  anchor drift) are recorded as the card's **negative result** in
  `decision.md` §3 and in `handoff.json`, and are handed to the owner as
  **out-of-scope product changes requiring a separate card/owner decision**.
- E11 and E13 keep their r1-pinned ("accepted-by-production") outcomes. They are
  not re-labelled as passes, and no oracle text is rewritten to fit a green run.
- `disclosure_adaptation = unmapped` and `accuracy = unproven` are unchanged by
  this card; no consumer outside `scripts/` (invest-*) is exercised here.

## R3-8 Provenance of edits inside the r3 append region, and r3 run result

The r1/r2 body is byte-frozen (R3-5). The **append region itself** is not
hash-frozen, and two of its sections were written in more than one pass inside
this round. Disclosed rather than silently normalised:

| Section | Passes | Final state |
|---|---|---|
| R3-1 … R3-4, R3-7 | single pass, before the r3 run | unchanged |
| R3-5 | pass 1 predicted the proof values; **pass 2 (after `scratch/make_frozen_copy.py` ran, raw rc 0)** replaced the predictions with the measured byte counts, the inserted boundary byte `\n`, and the derived hashes; **pass 3** re-measured those figures after the R3-8 append grew the file | completed after the evidence run |
| R3-6 | pass 1 summary; **pass 2** added the forward pointer to `exploratory_log.md` and the correction that neither surviving `.pyc` is an exploratory artefact | completed after the evidence run |

Neither pass carried or changed any **expectation**: R3-1–R3-4 and R3-7 held all
frozen outcomes and were fixed before the run. Nothing was relaxed.

**r3 evidence run result** (raw rc 0, full stdout in
`pytest_r3_verdict.stdout.txt`):

```
13 collected -> 13 passed in 2.37s
raw_returncode = 0            expected_returncode = 0
executed test file = 10902 B  sha256 0072b16019825b46e1fa27e2decec615675cb33336eb3968fae32fb8e0dfc7f5
```

Business verdict by case, per R3-4: E1–E10 and E12 as frozen (rc 0 / rc 2);
**E11 and E13 remain rc=3** — the product gaps reproduce exactly as pinned in the
pre-verdict exploratory run and in the independent review. The r3 run therefore
**confirms the card's headline property is still violated** (F1) and adds E4 to
the matrix without weakening any other case. Handoff status stays
`changes_required`.

## R3-9 Final measurement, self-reference disclosure, and close of revision r3

Two administrative defects in this append region must be stated rather than
tidied away:

1. **The R3-5 block is stale.** It quotes `current oracle.md bytes = 17360` — a
   figure measured *before* R3-8 and R3-9 were written. A file that quotes its
   own byte count is self-referential: each edit that updates the figure changes
   it again. R3-5 is therefore left as a **point-in-time snapshot** and is not
   edited further.
2. **R3-8's pass table understates the passes.** R3-5 was written in three passes
   (predicted values → measured values → re-measured after R3-8 existed). All
   passes carried only its own bookkeeping values; none carried or altered a
   frozen expectation.

The authoritative, non-self-referential record of every hash in this attempt is
`handoff.json` (`deliverables`, `oracle.sha256`, `oracle.frozen_body_sha256`,
`append_only_proof`) plus the raw stdout of `scratch/make_frozen_copy.py`
(`scratch/make_frozen_copy.stdout.txt`). Where this prose and those artefacts
disagree, **the artefacts win**, and the disagreement is a defect in the prose —
never a change to a frozen expectation.

Append-only status is unaffected: the r1/r2 body (bytes `[0:6831]`, sha256
`478bd70e0a1dfbfb924ebec0175bb2bdcdd199880de1c554de099d8ac8723c90`) is untouched,
the only non-append byte is the normalising `\n` at offset 6831, and
`scratch/make_frozen_copy.py` returns `append_only_proof: true` (raw rc 0) at file
close.

**Revision r3 is closed at this line.** No further edit to `oracle.md` is part of
r3; any later change must open a new revision and repeat the freeze discipline.
