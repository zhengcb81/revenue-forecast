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

<!-- ================= APPEND-ONLY: REVISION r4 BELOW ================= -->

# Revision r4 — E1/E11/E13 RE-FREEZE against B1's fixed tree (owner-approved)

- Fix-round instruction label: the card `I-08-C-REFREEZE` calls this "append-only
  oracle revision r3". The file already contains a **closed** r3 (see its closing
  line above: "any later change must open a new revision"), so this append is
  numbered **r4** — the instruction is satisfied in substance (one new
  append-only revision, same form) and the numbering follows the file's own rule.
  `handoff.json` fix-record points here as `oracle.md revision r4 (fix-round
  instruction label: "r3")`.
- Author of this append: I-08-C fix-round implementer (card `I-08-C-REFREEZE`).
  **Not** the reviewer. This append readies re-review; it does not sign anything.
- Trigger: card **B1** (`execution_runs/B1-I08C-product-fixes/a20260921-01`)
  closed product findings F1 and F3 in an isolated tree. Against that tree the
  r1/r2/r3 pinned-gap expectations for E11/E13 **necessarily fail**. That
  failure is **expected, not a regression** — it is exactly what the owner
  approved this re-freeze to resolve.
- Authority (verbatim, `OWNER_DECISIONS.md` §16, file 53286 B, sha256
  `4c9acf9ec95c8ec028b6e77719ddf32dbbbc1fb545c91cb702521d65a70aa2f3`):
  - owner 原话 (line 365): 「A-1: b（允许修 prune 代码，不授权执行 prune）
    **A-2: 批准** B: a（提高门超时到 1200，立卡红绿） C: 先推已收口的 4 张，
    B1/B3/I-14-D 攒第二批 D-G1: a D-G2: 留置/（或给取舍） E-1: 150/60
    E-2: 重跑 E-3: 立卡 E-4: 维持暂不签」
  - ruling table (line 370): 「**A-2 批准** | I-08-C oracle 追加式重冻
    （E11/E13 由"缺口在册"翻转为"攻击必拒"），收口归其 reviewer |
    与建议一致 | 已派 `I-08-C` refreeze 卡」
- Discipline: append-only. Everything above this marker (r1 body bytes
  `[0:6831]` **and** the whole r3 append region) is untouched; the prefix proof
  is in R4-8. No r1/r2/r3 expectation is rewritten — superseded expectations are
  **preserved verbatim** in R4-2 in the superseded-record form used by I-14-H's
  W1 2220→1740 correction (old value + new value + reason + provenance).

## R4-1 Why: B1 closed the gaps, so the pinned-gap expectation is now stale

- B1 fixed tree (READ-ONLY for this card):
  `<PLAN>\execution_runs\B1-I08C-product-fixes\a20260921-01\iso\fixed\rf`.
  Only three files differ from production-identical bytes:
  `scripts/revenue_publication.py` `bc2bb4a33e36ed9ad82bc4ffe33e57de8999002c2c7910b9c8b9d1565678fcd0`,
  `scripts/revenue_core.py` `8a761498f5eb729e4f4227f2a315d709253f8b96acf7baa7253ab425e73ac883`,
  `scripts/revenue_report.py` `212f00598feca408dc429d4c7a5332131ce25f1165b079347e4b295345df7d3b`.
  This round re-verified that B1's unfixed `iso/rf` is byte-identical to
  production for `revenue_publication.py`, `revenue_core.py`,
  `revenue_report.py`, `publication_registry.py`,
  `tests/test_recognition_bridge.py`, `tests/test_data_contract.py` (all six
  hashes match), so fixed vs unfixed differ **only** by B1's three files.
- B1's own handoff recorded this card's expected collateral verbatim
  (`B1 handoff.json`, 26788 B, sha256
  `c5696e780a9470cf22dd41333e05c24a82783080b7fd006862e181c25e624259`,
  `red_green.post_change_expected_collateral`): e11 "now FAILS — it pins the gap
  (business rc=3) and the fix necessarily invalidates it"; e13 same; verdict
  "expected, not a regression; the I-08-C oracle must be re-frozen by its owner".
- What B1 implements (rejection reasons this revision freezes):
  - **REM-01(a) → E11**: a receipt claiming `attestation_status='host_signed'`
    without a `publication_attestation` binding record is rejected with
    `attestation_missing_record` (I-08-A E27), message "publication_receipt
    claims attestation_status='host_signed' but carries no
    publication_attestation record (E27)"
    (`iso/fixed/rf/scripts/revenue_publication.py:241-249`, call site `:559`).
  - **REM-03 → E13**: `segments[i].base_revenue` is bound to the embedded
    parameter by an output gate; a forged opening base is rejected with
    `segment base revenue mismatch`
    (`iso/fixed/rf/scripts/revenue_report.py:215-225`, reached via
    `_validate_segment_opening_bases` `:571` ← `validate_published_forecast`
    `:1307` ← `validate_forecast_output` `:1344`).
  - **REM-01(b) → collateral on E1**: `attestation_capability()`
    (`iso/fixed/rf/scripts/revenue_core.py:118+`) now requires a PROVEN signing
    handshake; file existence is no longer capability. The E1 fixture's provider
    is `sys.executable`, which cannot complete B1's handshake, so on the fixed
    tree the honest formal package is stamped **`unattested`** (B1 probe
    `after/probe_fixed.txt`, 1629 B, sha256
    `9ade20c2e0d34f33ac68cdef7e96420aa8984793ebde1170e405c3e8817643b3`:
    `P2_sys_executable_capability = False`, `P2_sys_executable_label =
    'unattested'`). The r1 E1 assertion `== "host_signed"` therefore encodes the
    I-08-A §7.1 **false-green** shape (B1's regression run shows the repo's own
    such test `tests/test_attestation.py::test_configured_provider_means_
    host_signed_publication` is REQUIRED to break) and cannot stay unconditional
    if the suite must be truthful on both trees.

## R4-2 Superseded records (old expectation preserved verbatim; I-14-H W1 shape)

Each entry: **superseded expectation (verbatim)** → **replacement expectation** →
**reason** → **provenance**. Nothing below deletes the old text; it lives here
and in the untouched r1/r2/r3 body above.

### S-1 · E11

- **Superseded expectation (verbatim, r1 body line 61 / R3-4 row):**
  > E11 | A-C2: U with ONLY `attestation_status` flipped to `host_signed`
  > (+ self-hashes recomputed) | **KNOWN GAP (finding, frozen pre-run):** both
  > the receipt validator AND the strong dispatcher PASS, because the
  > attestation label is a plain string checked only for set membership
  > (`revenue_publication.py:222-226`); the capability gate exists only at
  > issuance (`revenue_core.py:167`, `attestation_capability()` False without
  > provider). Consumers requiring a *trusted formal* package have no
  > consumption-side verification in this tree — this is the I-08-B follow-up
  > surface, reported to the reviewer, NOT counted as a pass of the security
  > property.

  and (R3-4): "E11 … 3 — **property VIOLATED**, recorded as the card's negative
  result F1 (not a pass)"; test body pinned acceptance with
  `validate_publication_receipt(flipped)  # GAP…` / `validate_forecast_output(flipped)  # GAP…`.
- **Replacement expectation (frozen now):** the SAME attacker move MUST be
  **rejected at BOTH entry points** with the specific reason B1 implements:
  `pytest.raises(ForecastInputError, match="attestation_missing_record")` for
  `validate_publication_receipt(flipped)` AND for
  `validate_forecast_output(flipped)`. Non-secret self-hashes are recomputed
  first, so the attestation gate is the only possible rejection reason.
- **Reason:** B1 REM-01(a) closed F1 (owner ruling A-2: 由"缺口在册"翻转为
  "攻击必拒"). The gap no longer exists on the fixed tree; keeping the pin would
  make the frozen expectation fail for the *right* product reason and would
  misdescribe the tree under test.
- **Provenance:** owner §16 A-2 (verbatim in the header); B1
  `after/probe_fixed.txt` `P1_label_flip_receipt_layer` and
  `P1_label_flip_strong_dispatcher` both
  `REJECTED:attestation_missing_record: … (E27)` (recorded before this card
  existed); fixed source `revenue_publication.py:241-249`; B1 handoff
  `post_change_expected_collateral`. pre-image of this file at append time:
  22335 B / `94a853e978e34f522820cc2e03548fffe8ee2e599725d7a0131f872c93add8b3`.

### S-2 · E13

- **Superseded expectation (verbatim, r1 body line 63 / R3-4 row):**
  > E13 | **pinned gap:** self-hash-consistent forgery of
  > `segments[0].base_revenue` (direct_revenue) | Receipt layer passes AND
  > `validate_forecast_output` **ACCEPTS** — the segment-level base feeds no
  > recomputation comparison (`revenue_report.py:442` recalculates *from* it;
  > nothing compares it to the input or stored modeled activity). Reported to
  > reviewer as gate-coverage finding.

  and (R3-4): "E13 … 3 — **gap pinned**, recorded as F3"; test body pinned
  acceptance with `validate_forecast_output(forged)  # pinned: accepted by current gates`.
- **Replacement expectation (frozen now):** the receipt layer still
  **ACCEPTS** (F2/REM-02 is documentation-only; that limitation is unchanged
  and stays pinned as a limitation, not a security claim), and
  `validate_forecast_output(forged)` MUST **REJECT** with
  `pytest.raises(ForecastInputError, match="segment base revenue mismatch")`.
- **Reason:** B1 REM-03 closed F3 by binding the segment opening base to the
  embedded `base_revenue_parameter_id` parameter; company totals were never
  movable (reviewer's scope-narrowing stands) — this gate covers the
  presentation field the card's F3 named.
- **Provenance:** owner §16 A-2; B1 `after/probe_fixed.txt`
  `P3_receipt_layer = 'ACCEPTED'`, `P3_strong_dispatcher =
  'REJECTED:segment base revenue mismatch: Segment A opening base 1100.0 does
  not match segment_a_base (100)'`; fixed source `revenue_report.py:215-225`;
  B1 mutation M3 (reverting REM-03 turns exactly R10/R12 red).

### S-3 · E1 (collateral of the same fix, discovered and disclosed)

- **Superseded expectation (verbatim, r1 body line 51):**
  > E1 | A-C1: S legit, hashes/trusted domains consistent |
  > `validate_publication_receipt(S)` passes; `validate_forecast_output(S)`
  > passes; repeat read passes again;
  > `S["publication_receipt"]["attestation_status"] == "host_signed"`
- **Replacement expectation (frozen now):** validators pass twice (UNCHANGED);
  the label assertion becomes **tree-conditional** — on a tree exposing
  `revenue_publication.validate_publication_attestation` (B1 fixed) the honest
  S package MUST be `unattested` with NO `publication_attestation` record
  (sys.executable cannot prove signing); on any other tree (production /
  production-identical bytes) the original `== "host_signed"` assertion still
  holds. Node id unchanged.
- **Reason:** asserting `host_signed` for a provider that cannot sign is the
  I-08-A §7.1 false-green pinned as an expected value; B1 REM-01(b) retired
  file-existence capability, so the old assertion would fail on the fixed tree
  and would be *wrong* about that tree. The supersession is forced by the
  owner-approved fix, not chosen for convenience.
- **Provenance:** B1 probe `P2_sys_executable_capability = False`;
  B1 regression `after/suite_fixed.stdout.txt` (the required false-green break);
  disclosed exploratory run of this round (R4-6) observed
  `AssertionError: assert 'unattested' == 'host_signed'` at
  `test_i08c_consumer_rejection.py:93`.

## R4-3 Frozen node map and expectations after r4 (13 nodes, ids stable except two renames)

| Case | Test node (r4) | Frozen expectation (exact gate) | business rc on FIXED / on UNFIXED |
|---|---|---|---|
| E1 | `test_e1_legit_signed_package_passes_repeatably` | see S-3 (tree-conditional label + validators twice) | 0 / 0 |
| E2–E10, E12 | unchanged ids, unchanged expectations | unchanged from r1/r2/r3 | as r3 |
| **E11** | `test_e11_host_signed_label_flip_is_rejected_at_consumption` (renamed from `…_is_not_bound_at_consumption`; the old name asserted the retired gap) | BOTH entry points raise `ForecastInputError` matching `attestation_missing_record` | **2 / 3** |
| **E13** | `test_e13_segment_base_revenue_forgery_is_rejected_by_output_gates` (renamed from `…_not_bound_by_output_gates`) | receipt layer accepts (F2 limitation); dispatcher raises `ForecastInputError` matching `segment base revenue mismatch` | **2 / 3** |

`exit_code_legend` unchanged. Note the semantic shift this revision introduces:
under r3, E11/E13 were **green pytest nodes carrying business rc=3** (the gap,
pinned). After r4, on a tree with B1's fix they are ordinary correctly-rejected
negatives (business rc=2), and on the **unfixed** tree they are genuine pytest
FAILURES (raw rc=1) — the gap now shows as red instead of as a pinned green.

## R4-4 Evidence-run contract (frozen BEFORE any of these runs)

| Run | Tree (RF_IMPORT_ROOT) | Frozen expectation |
|---|---|---|
| RUN-A (evidence) | B1 `iso/fixed/rf` | 13 collected, **13 passed, 0 failed**, raw rc **0** |
| RUN-B (anti-vacuity) | unset → production (production-identical unfixed bytes) | 13 collected, **exactly {e11, e13} failed**, 11 passed, raw rc **1** |
| RUN-B2 (anti-vacuity, isolated unfixed) | B1 `iso/rf` (verified production-identical) | same as RUN-B: exactly {e11, e13} failed, raw rc **1** |
| RUN-M (mutation) | B1 `iso/fixed/rf`, mutation test file with the OLD pinned-gap bodies restored for e11/e13 | **exactly {e11, e13} failed**, raw rc **1** |

RUN-B/B2 prove the flip is **load-bearing** (the gap still reproduces on the
unfixed bytes); RUN-M proves the flip is not vacuous in the other direction
(the old expectation cannot pass against the fix). Any deviation from these
frozen sets must be reported as observed, never edited into the expectation.

## R4-5 Test-file revisions this round (fix-round edits are allowed; all hashed)

| Stage | Bytes | sha256 | Used by |
|---|---|---|---|
| r3 frozen file (pre-fix-round) | 10902 | `0072b16019825b46e1fa27e2decec615675cb33336eb3968fae32fb8e0dfc7f5` | r3 evidence run, B1's `before/i08c13_unfixed` run |
| interim: `RF_IMPORT_ROOT` import-root override ONLY | 11360 | `61ef2b67bdb048664c9b752606d195b43528f622b256f099b7e0d4072eeaa9f1` | the disclosed exploratory run only |
| **r4 final (frozen before all four runs above)** | 13152 | `3f83fdf2b7d81aba9a0bbafeb08c6c5fdf9344607fce5e5a34bb920da6454fbb` | RUN-A, RUN-B, RUN-B2, RUN-M (mutation file is a hashed derivative) |

Changes in the r4 file, complete list: (1) import-root override
`REPO = Path(os.environ.get("RF_IMPORT_ROOT") or <production path>)` — default
byte-equivalent to every prior run; (2) E11 body flipped to rejection +
node renamed; (3) E13 body flipped to dispatcher rejection + node renamed;
(4) E1 label assertion made tree-conditional (S-3). Nothing else changed.

## R4-6 Freeze-order disclosure (exploratory run, before the freeze)

Order of this round, disclosed rather than implied:
1. env-override edit (hashed, R4-5); 2. **exploratory run** of the then-current
file against the fixed tree (`scratch/fixround/exploratory_fixed.stdout.txt`,
7358 B, sha256
`f9d650eb5a47b95a9a1b8a30cdc62aaa4c4ca4064b16bf3f3aff0a947cfb4ac0`, raw rc 1:
`3 failed, 10 passed`, failed = {e1, e11, e13}); 3. final test file frozen
(hashed); 4. **this oracle append**; 5. the four evidence runs of R4-4.

Honest reading of that order: the exploratory run measured the fixed-tree
collateral (it is how E1's breakage was found rather than guessed), so the
r4 expectations are **corroborated** by it. Their primary derivation is NOT the
exploratory run but B1's `after/probe_fixed.txt` (written before this card) and
the fixed source lines cited in R4-1/R4-2 — the same provenance chain I-14-H
used for W1. The falsifiable half of the contract (RUN-B/B2/RUN-M must go RED,
fixed before those runs) is what keeps this round honest; if RUN-B/B2 had been
run first, the round would be circular, so they were not.

## R4-7 What r4 does NOT change (scope)

- **No production write.** Production stays byte-identical
  (`revenue_publication.py` `183803bb…`, `revenue_core.py` `1821fd2a…`,
  `revenue_report.py` `a85fb484…`); no promotion is performed or implied.
- **B1's attempt is READ-ONLY** from this card: executed-from only, with `-B`,
  `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`, `--basetemp` inside this
  attempt, cwd = this attempt, so no byte in B1's tree is written.
- **F2 limitation stays pinned** (E13 keeps asserting receipt-layer acceptance;
  REM-02 was documentation-only), **F4** anchor drift unchanged, **invest-***
  consumers still out of scope and unverified, **no CLI publish transaction**.
- `disclosure_adaptation = unmapped`, `accuracy = unproven` unchanged.
- **Two separate steps remain after this card:** (1) promotion of B1's fix to
  production is an owner decision not taken here; (2) I-08-C's *acceptance* is
  the reviewer's verdict on the re-frozen package — this card only re-freezes
  the oracle and readies re-review (`ready_for_re_review=true`, never self-signed).
- E2–E10 and E12 expectations are untouched; their r3 business rcs stand.

## R4-8 Append-only prefix proof (byte-prefix form)

Recorded BEFORE this append (measured on the file this text is appended to):

```
oracle.md pre-append bytes        = 22335
oracle.md pre-append sha256       = 94a853e978e34f522820cc2e03548fffe8ee2e599725d7a0131f872c93add8b3
r2 frozen body bytes[0:6831] sha256 (recheck target)
                                  = 478bd70e0a1dfbfb924ebec0175bb2bdcdd199880de1c554de099d8ac8723c90
pre-append file ended with        = 0x0A (newline), so the append needed NO
                                    boundary-byte normalisation (unlike r1→r3)
```

Post-append verification (`scratch/fixround/prefix_proof.py` →
`scratch/fixround/prefix_proof.json`, raw rc recorded in `commands.json`):
`sha256(bytes[0:22335])` MUST equal `94a853e9…` and
`sha256(bytes[0:6831])` MUST equal `478bd70e…`. Method: hash the fixed prefix
ranges directly — never total-length arithmetic (the failure mode recorded in
plan `findings.md` round 35). The authoritative post-append figures live in
`prefix_proof.json`, `handoff.json` and `binding.json`; per R3-9's rule, where
prose and artefacts disagree, **the artefacts win**.

**Revision r4 is closed at this line.** No further edit to `oracle.md` is part
of this fix round; any later change must open a new revision and repeat the
freeze discipline.
