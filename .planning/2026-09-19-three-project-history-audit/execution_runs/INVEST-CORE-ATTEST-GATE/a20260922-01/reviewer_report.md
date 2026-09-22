# reviewer_report.md — INVEST-CORE-ATTEST-GATE — INDEPENDENT REVIEWER REPORT

- Card: **INVEST-CORE-ATTEST-GATE** (cross-repo, REM-01 consumer side)
- Attempt: `execution_runs/INVEST-CORE-ATTEST-GATE/a20260922-01`
- Reviewer: independent reviewer subagent (parent session `session-bfecd191-…`); **not** the implementer
- Package under review: `oracle.md` (r1+append-only r2), `decision.md`, `handoff.json`, `changes.diff`, `test_invest_attest.py`, `conftest.py`, `before/`, `after/`, `scratch/`
- Method: minimal reads + independent re-execution (3 pytest runs of the frozen test file, hash re-computation of every pinned anchor, a fresh diff round-trip on my own copies)
- Boundaries honored: wrote ONLY this report + its `.sha256` pin; all repos and the 3 install surfaces READ-ONLY; no `git` write command; no signature produced by me; never self-sign / never self-accept.

## VERDICT

**Reviewer disposition (three-state): `accepted_scoped`.**

**CONFIRMED — all 8 declared claims verified (claims 1–8), two minor disclosure-wording findings (F9, F10), one wording note (F11). RED→GREEN, mutation, diff round-trip, and zero-write boundaries all reproduced by my own runs. Merge remains NOT approved — merge authority is the invest-core owner; two adjudications below are the open owner decisions.**

### Scope statement for `accepted_scoped`

- **In scope, accepted**: the delivered patch (`changes.diff` → `iso/invest-core-fixed`, sha256 `d59d579c…`) and its frozen proof package — independently re-executed by this reviewer: RED `7 failed/3 passed` (exact declared set), GREEN `10 passed`, mutation M1 `7 failed/3 passed` (exact declared set, revert byte-exact), diff round-trip `--check` rc0 + apply rc0 → `d59d579c…` on two independently copied locations, all four consumer copies still `9ad8a146…`, oracle r1 prefix `7eaf81b9…` re-computed, trust anchors absent, production registry `bc3256bb…` unchanged, no self-sign.
- **Explicitly NOT accepted / NOT approved**: **merge** — authority = invest-core owner; this card delivers a patch, not a merge. Also outside this acceptance: promotion of B1's issuance fix and trust-anchor deployment (separate owner decisions).
- **Conditions attached to the scope**: (1) the 3 post-merge shipping-test failures are handled per adjudication B — open ONE test-design card (false-green rewrite = merge acceptance criterion; shared-cache deepcopy fix), with no test edits folded into the cross-repo merge diff; (2) landing follows adjudication A — trust-anchor deployment + B1 issuance-fix promotion → this patch (or one coordinated window), fail-closed as-is, **no bypass flag ever**; (3) **carried findings** registered with the carrier at landing: F9 (handoff before/after anchor-table "byte-identical" wording inaccurate — gap closed by my own re-hashing, zero-write conclusion stands), F10 (`…_git_status_product` filter scope undisclosed; the dirty path is `tools/pre_push_gate.py` from the concurrent GATE-TIMEOUT-1200 card, not this card), F11 (r2.1+r2.2 shipped as one combined append with one prefix proof). All LOW/INFO, none blocking.
- **Unchanged fields**: `disclosure_adaptation=unmapped`, `accuracy=unproven`, `status=review_pending`, `implementer_self_acceptance=false`.
- **Why not `changes_required`/`blocked`**: nothing in F9/F10/F11 impairs the patch, the frozen proof, or the zero-write boundary — F9's gap was closed by my own re-hashing, F10's dirty path is attributable to another card, F11 is wording only.

What my own runs measured (frozen `test_invest_attest.py`, sha256 `81555f4e…`, against the attempt's iso trees):

| run | tree | result | rc |
|---|---|---|---|
| GREEN (re-run by me) | `iso/invest-core-fixed` (`d59d579c…`) | **10 passed** | 0 |
| RED (re-run by me) | `iso/invest-core` (`9ad8a146…`) | **7 failed / 3 passed**, set == declared {R1a,R1b,R2,R3,R3b,R4,R5} | 1 |
| MUTATION M1 (re-run by me) | `iso/invest-core-mutant` (`03aa8bbb…`) | **7 failed / 3 passed**, set == declared | 1 |

---

## Numbered findings (claim-by-claim)

### F1 — Claim 1: four consumer copies, byte-identical, never written — **CONFIRMED**
Re-hashed all four myself (SHA-256, `Get-FileHash` + `[IO.File]::ReadAllLines`):

```
9ad8a146ab1535555b7fd74a14acbb8280c21d4eb22e3e92da3ab2965ba3cc45  102388 B  2689 lines
  .agents\skills\invest-core\scripts\invest_contracts.py
  .claude\skills\invest-core\scripts\invest_contracts.py
  .codex\skills\invest-core\scripts\invest_contracts.py
  Projects\invest-skills\invest-core\scripts\invest_contracts.py
```
- `Projects\invest-skills`: HEAD `0ee17137f8575b48064051a5ed951073c717cb42`, porcelain **empty** (checked by me after all my activity).
- Defect site confirmed in these exact bytes at `invest_contracts.py:1130–1142` (read directly): `elif attestation_status == "host_signed": attestation_verification = "host_signed"` with no record check; legacy bypass at 1116/1131–1132 as declared.
- Note: PowerShell `Measure-Object -Line` reports 2562 (it skips blank lines); `[IO.File]::ReadAllLines().Length` = 2689 — the declared 2689 is correct.
- `iso/invest-core` (RED arm) re-hashed to the same `9ad8a146…` after my runs.

### F2 — Claim 2: the remedy is really in the fixed code, step by step — **CONFIRMED**
I read `changes.diff` in full and the guard in `iso/invest-core-fixed/scripts/invest_contracts.py` (sha256 `d59d579ce12e5e844d5cb67c202d4cf58800c413f65d69284606f48d72e17ad8`):

1. **Closed 10-field set** — `PUBLICATION_ATTESTATION_FIELDS` frozenset, exactly the 10 declared fields; missing/extra → `attestation_payload_fields`. ✓
2. **Constants/formats** — schema `"1.0"`, domain `revenue-forecast/publication-attestation/v1` (mismatch → `attestation_domain_mismatch`), `algorithm == "ed25519"`, `issuer`/`key_id` non-empty, fingerprint 32-hex / request_id 64-hex / `signed_at` RFC3339-Z via `fullmatch`, signature present (`attestation_missing_signature`) and 128-hex (`attestation_malformed_signature`). ✓
3. **E16 payload binding** — `record["payload_sha256"] == receipt["validated_payload_sha256"]` else `attestation_payload_hash_mismatch`. ✓
4. **Ed25519 via the single runtime loader** — `_attestation_trusted_signers()` does `revenue_runtime()` then `from contracts.evidence import _trusted_signer_public_keys`, `except Exception: return {}`. I read that loader (`iso/revenue-forecast/scripts/contracts/evidence.py:242–267`): env `REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS` else `config/trusted_signer_public_keys.json`, **missing or corrupt ⇒ `{}` (zero trust)**. Fingerprint not in map → `provider_key_untrusted`; verify/ImportError → `attestation_signature_invalid`. Every path `_fail`/raise ⇒ fail-closed. ✓ Reconstructed request matches the frozen 6-field shape incl. `result_sha256 = "0"*64` sentinel. ✓
5. **Placement** — guard at fixed lines 1349–1350, immediately AFTER `ref = revenue_reference(result)` (line 1341, the content strong-validation) and before the scope check/adapter build; diff contains **exactly 2 hunks**, so the legacy block and all label≠host_signed behavior are byte-untouched (legacy `legacy_read_only` still at fixed line 1330). ✓ OPEN-D6 legacy gap left open as declared; **no E21/identity-binding claim** anywhere in the new docstring. ✓
6. **Label-only flip with no record, or with an invalid record, is rejected** — proven by execution, not just reading: my GREEN run passed R1a (no record), R2 (payload mismatch), R3 (bad sig), R3b (untrusted fp), R4 (extra field), R5 (no anchor), and P1 (valid record + isolated anchor ⇒ `attestation_verification == "host_signed"`). ✓

### F3 — Claim 3: RED→GREEN — **CONFIRMED (both their evidence and my re-runs)**
- Their capture: `before/RED_unfixed.stdout.txt` (UTF-16LE) = 7 FAILED / 3 PASSED, rc file `1`; `after/GREEN_fixed.stdout.txt` = 10 PASSED, rc `0`. Declared set == observed set on RED (R1a,R1b,R2,R3,R3b,R4,R5 failed; P1,B1,B2 passed). ✓
- **My re-run**: identical results both arms (table above). P1 exercises structure + E16 binding + real Ed25519 verification against a trust file that exists only under `%TEMP%\pytest-of-*\pytest-*\ic_gate0\` (I saw that path in my own RED output) — an ISOLATED anchor; `adapter["attestation_verification"] == "host_signed"` asserted and passing. ✓
- Freeze order: `before/frozen_artifacts.json` captured `2026-09-22T08:54:49` (oracle r1 16936 B `7eaf81b9…`, test file `81555f4e…`, conftest `9697c7a2…`) — BEFORE the first pytest output `before/RED_unfixed.stdout.txt` mtime `08:55:43`; I re-hashed the test file and conftest: **still equal to the frozen values**. ✓

### F4 — Claim 4: R1b production-issuance reproduction — **CONFIRMED (in their evidence and re-executed by me)**
The `issuance_minted` fixture (test lines 256–277) writes a 5-byte `.txt`, sets `REVENUE_ATTESTATION_PROVIDER` to it, runs real `run_forecast`, and **pre-asserts** `attestation_status == "host_signed"` AND `publication_attestation` absent — the issuance fingerprint. Then:
- unfixed consumer (my RED run): `DID NOT RAISE InvestmentArtifactError` at test line 293 ⇒ production issuance minted the label with no record and the consumer accepted it. ✓
- fixed consumer (my GREEN run): rejected with `attestation_missing_record`. ✓
This independently reproduces B1's evidence (5-byte `.txt` ⇒ `host_signed`) on today's production issuance code (B1's issuance fix unpromoted, as disclosed).

### F5 — Claim 5: mutation M1 — **CONFIRMED (revert verified byte-exact + re-run by me)**
- I diffed `iso/invest-core-mutant` vs `iso/invest-core-fixed` myself: the mutant differs by **exactly** the 7 comment lines + `if not is_legacy and attestation_status == "host_signed":` + `verify_host_signed_attestation(receipt)` — the exact call+guard+comment revert the oracle froze; the helper/constants remain (permitted). Mutant sha256 `03aa8bbdbd2e34e42219d04919680976bd6f3d3a8379dd4f52dc3dfb72a9914c` == `after/production_anchors.json`. ✓
- Their `scratch/mutations/mutation_proof.json`: declared == observed (7/3), missing/unexpected empty, rc `1`. ✓
- **My re-run of the same frozen test file on the mutant: 7 failed / 3 passed, rc 1, exact declared set.** ✓
- `iso/invest-core-fixed` re-hashed by me AFTER all three of my runs: still `d59d579c…`; pristine still `9ad8a146…`. ✓

### F6 — Claim 6: diff round-trip — **CONFIRMED (re-verified on 2 locations myself)**
- `changes.diff`: **10372 B**, sha256 `009debc218447e36616fb9f127782031e542ecb68381692c3f2905fcfa92181a` (re-computed), POSIX `a/invest-core/scripts/invest_contracts.py → b/…` (the only backslash in the file is inside a regex literal, line 37), **exactly 2 `@@` hunks**. ✓
- My own round-trip on fresh copies in `%TEMP%` (originals untouched):
  - copy of `Projects\invest-skills`: `git apply -p1 --check` rc **0**, `git apply -p1` rc **0**, applied file sha256 **`d59d579c…`** byte-exact;
  - copy of `.agents\skills` (install surface root): `git apply -p1 --check` rc **0**, apply rc **0**, applied file sha256 **`d59d579c…`**.
  - Both originals re-hashed after: `9ad8a146…` (never written). ✓
- Their proof additionally claims `--check` rc 0 at `.claude` and `.codex` roots (check-only) — read in `scratch/roundtrip/roundtrip_proof.json`, not re-executed by me (see unverified list).

### F7 — Claim 7: oracle r1 freeze + append-only r2.1/r2.2 — **CONFIRMED**
- I computed `sha256(oracle.md[0:16936])` myself = `7eaf81b925f21c21ba3f320111f3ea57c54dd74292a4ec5697111d0476f47796` = the frozen r1 digest. ✓
- Current full-file sha256 `8a38a403d2aa505f9bb9708520d1ed2c762abfc7cd101bf72e482e48bf0c36a6` == `scratch/append_oracle_r2.json`'s `oracle_sha256_after_r2` ⇒ **no edit after the append**; file mtime `09:10:07` equals the recorded append time. Proof says `r1_untouched: true`, and my independent prefix hash agrees. ✓
- Both disclosures are present as appended sections after the r1 byte range: **r2.1** (pristine contingency activated: 6 pre-existing clean-env `unattested`-default failures, both arms, listed by name) and **r2.2** (declared fixed-arm set corrected 2→3; the 3rd = `test_growth_driver_tree_is_hashed_and_compacted`, second consumer of the shared `"growth"` module-cached fixture mutated in place; `tests/` unchanged). ✓ No r1 expectation (node table §4, mutation §6, boundaries §10) was relaxed.
- Wording note: r2.1+r2.2 were emitted as **one** append event (single proof, single timestamp), not two separate appends — substance unaffected (F11).

### F8 — Claim 8: boundaries — **CONFIRMED**
- `handoff.json`: `status=review_pending`, `merge_authority="invest-core owner — NOT yet approved; this card delivers a patch, not a merge"`, `merge_status="NOT MERGED anywhere…"`, `disclosure_adaptation=unmapped`, `accuracy=unproven`, `implementer_self_acceptance=false`. ✓ No field claims acceptance.
- **No merge happened**: all four sources still `9ad8a146…` (re-hashed by me); invest-skills porcelain empty; HEAD unchanged. ✓
- **Trust anchors ABSENT** everywhere — I checked `config/trusted_signer_public_keys.json` in the rf repo, all 3 install surfaces' revenue-forecast, and the iso copy: all ABSENT; a recursive search of the repo + all 3 skill roots + invest-skills AFTER my runs found **zero** such files. ✓
- **Production registry unchanged**: `artifacts/registry/publications.jsonl` sha256 `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91`, mtime `2026-09-18T08:22:16` (before the attempt). My runs were redirected by the attempt's own `conftest.py` into `runner/registry/`. ✓
- **No self-sign**: the only key material is `b"\x23"*32` inside `test_invest_attest.py`; its trust file exists only under the pytest tmp dir; no production/install/iso trust file exists. I produced no signature outside reproducing the card's own ephemeral fixture signatures inside pytest tmp (same isolation design). ✓
- Zero-write anchors: every shared key of `before/production_anchors.json` vs `after/production_anchors.json` matches; consumer/install/repo/rf-runtime pins re-verified by me now — all match (including the keys the after-table dropped; see F9).

### F9 — Finding (LOW, disclosure wording): "byte-identical anchor tables" is not literally true
`handoff.json` requests "compare `before/production_anchors.json` and `after/production_anchors.json` (byte-identical tables)". They are **not** byte-identical and not key-identical: the after-table **drops** `rf_*/scripts/contracts/constants.py` (×2), `rf_*/SKILL.md` (×2), `trust_iso_config`, and **both git HEADs**, while adding iso arm hashes and `captured_at`. Consequence: for those keys the zero-write proof relies on the before-table alone. **I closed that gap myself**: `constants.py` = `278e3e02…` (repo+install), `SKILL.md` = `45e4e343…` (repo+install), iso trust config ABSENT, HEADs `0ee17137…` / `1d2288c0…` unchanged — all match. So the zero-write conclusion stands, but the handoff sentence should be corrected to "all shared keys equal, after-table is a reduced set" (or the after-capture should be regenerated key-complete).

### F10 — Finding (LOW, scope disclosure): rf-repo porcelain claim vs current state
Today the rf repo porcelain is NOT empty: many `.planning/**` modifications from later cards (expected) plus **`M tools/pre_push_gate.py`** — a 1-line change `timeout: int = 600 → 1200`, mtime `2026-09-22T08:47:22`, i.e. **inside this attempt's window** (before-capture `08:46:31`, after-capture `09:19:27`), while `after/production_anchors.json` records `revenue-forecast_git_status_product: ""`. Attribution: the diff contains no attestation/product content and a sibling untracked dir `execution_runs/GATE-TIMEOUT-1200/` exists with exactly that semantic ⇒ almost certainly a **concurrent card**, not this one (`commands.json` never touches `tools/`). But the filter behind the `…_git_status_product` key is **not disclosed** in `commands.json`, so either `tools/` was excluded from "product" (scope should be stated) or the after-capture is stale for that path. Not card-attributable; recommend the owner record the filter scope. The cards' own claimed anchors (4 consumers, rf scripts, registry, trust) are all independently verified unchanged by me.

### F11 — Finding (INFO): append mechanics wording
The parent's phrasing "r2.1/r2.2 append-only disclosures" holds in substance (both sections appended, r1 prefix hash proves untouched), but they were appended together in one event with one proof file — there are not two independent prefix proofs, just one covering the combined r2 block. Also `commands.json` discloses a failed first append attempt (parse error, no bytes written) — consistent with the single proof.

**Regression evidence (read, not re-executed — see unverified #1):** pristine suite capture = exactly the 6 declared `unattested`-default failures (35 passed/1 skipped/7 subtests, rc 1); fixed suite capture = 9 failures = those 6 + exactly the 3 declared delta failures (`test_current_revenue_workflow_receipt_is_transferred`, `test_growth_driver_summary_tampering_is_rejected`, `test_growth_driver_tree_is_hashed_and_compacted`), rc 1; delta-disappeared = none. I recomputed `tests/` identity myself: **5/5 files byte-identical across arms** (matches `after/tests_identity.json`).

---

## Unverified list (explicit)

1. **IC-c3/IC-c4 regression suites were not re-run by me** — I verified their captured stdout line-by-line, the delta arithmetic (6 pre-existing + exactly 3), and recomputed tests byte-identity myself; I did not re-execute the two full suite runs.
2. `--check` rc 0 at the **`.claude` and `.codex`** skills roots: their proof read, not re-executed (I re-verified `.agents` + the repo copy, as required — 2 locations).
3. **B1 report byte-pin** (`73feb059…` / 37135 B "PENDING" form): not recomputed; current B1 file is 37224 B (final form with substituted digest `6bfd2922…`).
4. The implementer's sweep for **other consumer copies** was not repeated; I verified only the four named locations.
5. **Freeze order** rests on file mtimes + self-reported `captured_at` (no external timestamp authority). Consistency checks all pass.
6. **"No network"** assertion taken from `commands.json` (not straced).
7. The **cryptography-missing** branch (`ImportError` → `attestation_signature_invalid`) is `pragma: no cover` and was not exercised (50.0.1 present).
8. I did not perform a whole-tree diff of every install surface; my zero-write conclusion is hash-based on all pinned anchors (re-computed after my runs).

## Adjudication A — merge semantics: is fail-closed-for-all-existing-host_signed acceptable as the LANDING state?

**Yes — acceptable as the landing state, as a declared breaking change; the staging must happen in the ORDER of owner decisions, not inside the guard.**

- The set that breaks is exactly the set that is unverifiable: today `host_signed` is minted from mere file existence (my F4/R1b reproduction), so every currently-"working" host_signed consumption is consuming an unverified — and trivially forgeable — claim. The patch does not remove a real capability; it removes the ability to consume a claim nobody can check. `decision.md` §4 discloses this precisely.
- A staged/soft landing *inside the guard* (warn-only, downgrade to `unattested_bypassed`, an env bypass) re-creates REM-01 under a different name — the exact "same spoofable string wearing a different name" rejection already argued in `decision.md` §3, and it would fail my R5 node (fail-closed-without-anchor is the frozen expectation).
- Blast radius is bounded and disclosed: only non-legacy `host_signed` consumption in invest-* hard-fails with a coded error; `unattested` paths (default reject + explicit bypass) and the legacy path are byte-unchanged (F2, B1/B2 nodes).
- Recommended landing sequence for the owner: (1) record the landing as **breaking/fail-closed** in the register; (2) land the three owner decisions in the order **trust-anchor deployment + B1 issuance-fix promotion → this consumer patch** (or together in one window) so the outage window is zero/short — order-staging, not behavior-staging; (3) never ship a bypass flag; (4) monitor the coded rejection `attestation_missing_record`/`provider_key_untrusted` as the operational signal during the window.

## Adjudication B — the 3 declared shipping-test failures: change the tests or open a test-design card?

**Open ONE test-design card, before/at merge; do not fold test edits into the cross-repo merge diff.** Split by nature:

1. `test_current_revenue_workflow_receipt_is_transferred` — **false-green**: it asserts that a receipt carrying production-minted `host_signed` (no record possible) is accepted, i.e. it pins the defect this card closes. It **must** change with the merge; changing it is not weakening a test, it is removing a test that requires the vulnerability. Rewrite target: either assert the E27 rejection, or build a record + isolated trust anchor (P1-style) and keep asserting the receipt transfer. This one is a **merge acceptance criterion**, reviewed in the same card as the merge.
2. `test_growth_driver_summary_tampering_is_rejected` + `test_growth_driver_tree_is_hashed_and_compacted` — **pure test-design cascades**: the mutator mutates the module-scoped cached `"growth"` fixture *in place*; alphabetical method order then hands the polluted object to one, then a second, consumer. Root fix is a `deepcopy` in the mutator (or a function-scoped fixture) — a 1-line change with no product-code interaction.

Why a card, not an inline edit: (a) `tests/` byte-identity is this card's own evidence baseline (`after/tests_identity.json`), so test bytes deserve their own frozen oracle + independent review, exactly like product bytes; (b) bundling test edits into a cross-repo merge makes the merge diff unauditable; (c) the false-green rewrite needs a design decision (invert vs re-anchor) that the merge owner should rule on explicitly.

**r2.2 sub-adjudication (requested by the oracle):** counting the third failure as the *same declared root cause* is **legitimate** — same cause (in-place mutation of the shared cache), same coded message (`attestation_missing_record … (E27)`), measured delta exactly 3 with zero disappeared, tests byte-identical, disclosed append-only rather than absorbed. And simultaneously the underlying in-place fixture mutation is a **genuine test-design finding** warranting the card above. Both statements are true; the disclosure was the correct "stop, investigate, disclose" move, and the test-design issue should be registered separately rather than left implicit in the cascade explanation.

**r2.1 sub-adjudication:** the 6 pristine failures are pre-existing clean-env `unattested`-default failures — they reproduce on the UNFIXED consumer, so they cannot be card-attributable; fix-attribution by delta (pristine→fixed) was the pre-registered method. **Sustained.**

---

## REM-79 self-audit (two-way difference on my own text)

- **declared \ observed** (claims in this report with no observation behind them): **∅** — every CONFIRMED line names the hash, file/line, or run output it rests on; my three pytest runs and my own hash computations are quoted verbatim.
- **observed \ declared** (observations I made that did not reach this report): **∅** — each is present: anchor-table key mismatch → F9; dirty rf porcelain + `tools/pre_push_gate.py` → F10; single-append proof mechanics → F11; the PowerShell 2562-vs-2689 line-count artifact → F1 note; attempt-local registry appends by my own runs and pytest-tmp fixture signatures → Boundaries note below; loader source read (evidence.py:242) → F2.4.
- **No oracle class was relaxed**: I treated no unexpected node as expected; all three of my runs matched the frozen sets exactly.
- **Direction check on the verdict itself**: nothing declared "verified" that I only read a claim about (read-only claims are listed in the unverified list instead); nothing observed is promoted beyond its evidence.

## Boundaries note (my own activity)

- Wrote only `reviewer_report.md` and `reviewer_report.md.sha256` in this attempt.
- My 3 pytest runs wrote only attempt-local state the card's own `conftest.py` redirects to (`runner/registry/publications.jsonl`) plus pytest tmp dirs under `%TEMP%`; `-B -p no:cacheprovider` prevented pycache/cache writes.
- Diff round-trip ran on copies under `%TEMP%`; the 4 originals re-hashed `9ad8a146…` afterwards.
- No `git` write command was executed; no trust anchor read as authority, created, or modified; no signature produced outside the card's own ephemeral pytest-tmp fixture design; **this report does not accept, approve, or merge anything.**

REPORT_SHA256: PENDING (this line is the substituted digest; the pin lives in `reviewer_report.md.sha256`)
