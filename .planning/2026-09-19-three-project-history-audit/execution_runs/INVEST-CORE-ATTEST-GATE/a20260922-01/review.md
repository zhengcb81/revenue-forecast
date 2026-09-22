# INVEST-CORE-ATTEST-GATE — carrier landing (bookkeeping transcription)

## VERDICT BLOCK

- **verdict** = `accepted_scoped` (reviewer three-state ruling, option A)
- **carrier** = `reviewer_report.md`
- **carrier sha256 (new)** = `09b4e13ec1bd242114521a19af645c3c82a47724aa9acb81df3082d604f00a74` — **24941 B**, 162 lines, UTF-8 without BOM, LF-only (0 CR), single trailing LF
- **pin** = `reviewer_report.md.sha256` (85 B, sidecar sha256 `2e09db60c4078775311495452f8e6f9cf5554b2597e4de8207e7d996ac678f9c`) reads `09b4e13ec1bd242114521a19af645c3c82a47724aa9acb81df3082d604f00a74  reviewer_report.md` — **RE-PINNED: this new hash supersedes the earlier `f0627660…` pin.** Verified at landing (read-only): independent re-hash == sidecar == dispatch pin; measured size == 24941 B; verdict line greps to `accepted_scoped`.
- **ruling location** = `reviewer_report.md` **L12**: ``**Reviewer disposition (three-state): `accepted_scoped`.**``, CONFIRMED summary **L14**; scope statement **L16–L22**
- **byte proof** = verdict line L12 bytes 895..952 (58 B) sha256 `db9d71ad918a1d5b9bc0a9031d7bb859a3595285466895bcf78c1d9aa8f48b93`; verdict section L10–L14 bytes 883..1315 (433 B) sha256 `e2f27f742d875f4f773500d4b52e3fa9f6750de0cce4bc3bca00a9a66a1c598f`; scope statement L16–L22 bytes 1318..3520 (2203 B) sha256 `614ea4b997d8a97a9e2f0b654c0d15d20d6da1aca19bffb8f34489aa374bb69a`; whole file minus trailing LF 24940 B sha256 `b463a333605999099ee58cd23d0dda8707f3ee55413209043a4196d2b3774729`
- **reviewer** = 独立复核 (independent reviewer subagent, sibling of the implementer; wrote only `reviewer_report.md` + its `.sha256` sidecar)
- **nature of this file** = bookkeeping transcription, adds no acceptance of its own. The implementer never signs; this landing pass never signs; nothing here authorizes anything beyond restating the reviewer's ruling.

`review.md` did not previously exist in this attempt (no implementer stub); created by the carrier-landing pass — not by the implementer and not by the reviewer.

## Scope of the acceptance (transcribed verbatim in substance from the carrier)

### In scope, accepted (L18)

The delivered patch — `changes.diff` → `iso/invest-core-fixed` (`d59d579ce12e5e844d5cb67c202d4cf58800c413f65d69284606f48d72e17ad8`) — together with its frozen proof package, **as re-executed by the reviewer himself**:

- **RED `7 failed / 3 passed`** on `iso/invest-core`, rc 1 — failure set == the declared set {R1a, R1b, R2, R3, R3b, R4, R5};
- **GREEN `10 passed`** on `iso/invest-core-fixed`, rc 0;
- **mutation M1 `7 failed / 3 passed`**, rc 1 — exact declared set, and the guard revert is **byte-exact** (mutant `03aa8bbb…` == `after/production_anchors.json`);
- **diff two-side round-trip** (`git apply -p1 --check` rc 0 + apply rc 0 → `d59d579c…`) on **two independent copies** (invest-skills copy + `.agents` install-surface copy), originals re-hashed after;
- all **four consumer sources still `9ad8a146ab1535555b7fd74a14acbb8280c21d4eb22e3e92da3ab2965ba3cc45`**;
- **oracle r1 prefix `7eaf81b925f21c21ba3f320111f3ea57c54dd74292a4ec5697111d0476f47796` recomputed** by the reviewer from `oracle.md[0:16936]`;
- **trust anchors ABSENT** everywhere (repo config, all 3 install surfaces, iso copy; recursive search after his runs);
- **production registry `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91` unchanged**;
- **no self-sign** — the only key material is the card's ephemeral pytest-tmp fixture; the reviewer produced no signature outside reproducing the card's own isolated fixture inside pytest tmp.

All 8 declared claims CONFIRMED (F1–F8): "RED→GREEN, mutation, diff round-trip, and zero-write boundaries all reproduced by my own runs" (L14).

### Explicitly NOT accepted / NOT approved (L19)

- **merge** — authority = **invest-core owner**; *this card delivers a patch, not a merge*. `changes.diff` is unapplied anywhere; the four sources remain `9ad8a146…`.
- **B1 issuance-side promotion** and **trust-anchor deployment** — separate owner decisions, outside this acceptance.

### Conditions attached to the scope (L20)

1. **The 3 failing tests → open ONE test-design card** (adjudication B): the false-green rewrite (`test_current_revenue_workflow_receipt_is_transferred`) is a **merge acceptance criterion**, reviewed in the same card as the merge; the shared-cache cascade gets the **deepcopy fix** in the mutator; **test edits are NOT folded into the cross-repo merge diff**.
2. **Landing order per adjudication A**: trust-anchor deployment + B1 issuance promotion → this patch (or one coordinated window); stay **fail-closed** as-is; **no bypass flag ever**.
3. **F9 / F10 / F11 carried** and registered with the carrier at landing (below). All LOW/INFO, none blocking.

Unchanged by this verdict (L21): `disclosure_adaptation=unmapped`, `accuracy=unproven`, `implementer_self_acceptance=false`.

### Adjudication A — transcribed (L124–L131)

**Fail-closed-for-all-existing-`host_signed` is acceptable as the landing state, as a declared breaking change; the staging happens in the ORDER of owner decisions, not inside the guard.** The set that breaks is exactly the set that is unverifiable — today `host_signed` is minted from mere file existence (reviewer re-reproduced R1b), so every currently-"working" host_signed consumption is consuming an unverifiable, trivially forgeable claim. A staged/soft landing *inside* the guard (warn-only, downgrade to `unattested_bypassed`, env bypass) would re-create REM-01 under a different name and fail the frozen R5 expectation. Blast radius bounded and disclosed (only non-legacy `host_signed` consumption hard-fails with a coded error; `unattested` paths and the legacy path are byte-unchanged). Owner sequence: (1) record the landing as breaking/fail-closed; (2) **trust-anchor deployment + B1 issuance-fix promotion → this consumer patch (or together in one window)** — order-staging, not behavior-staging; (3) **never ship a bypass flag**; (4) monitor `attestation_missing_record` / `provider_key_untrusted` as the operational signal.

### Adjudication B — transcribed (L133–L144)

**Open ONE test-design card, before/at merge; do not fold test edits into the cross-repo merge diff.** (1) `test_current_revenue_workflow_receipt_is_transferred` is a **false-green** pinning the defect this card closes — it **must** change with the merge; the rewrite (assert the E27 rejection, or build a record + isolated trust anchor P1-style) is a **merge acceptance criterion**. (2)+(3) `test_growth_driver_summary_tampering_is_rejected` + `test_growth_driver_tree_is_hashed_and_compacted` are **pure test-design cascades** of the in-place mutation of the module-scoped `"growth"` fixture — root fix is a **deepcopy in the mutator** (or a function-scoped fixture), one line, no product-code interaction. Why a card: `tests/` byte-identity is this card's own evidence baseline; bundling test edits into a cross-repo merge makes the diff unauditable; the rewrite needs an explicit owner design ruling. **r2.2 sub-adjudication**: counting the third failure as the same declared root cause is *legitimate* AND the in-place fixture mutation is a *genuine test-design finding* — both true; disclosure was the correct move. **r2.1 sub-adjudication**: the 6 pristine failures are pre-existing clean-env `unattested`-default failures that reproduce on the unfixed consumer — **sustained**, not card-attributable.

## Carried findings (registered here; append-only, mirrored in `handoff.json.carried_findings` and `evidence/INVEST-CORE-ATTEST-GATE/qualification.json`)

| id | sev | summary | disposition |
|---|---|---|---|
| **F9** | LOW | Anchor-table wording gap: `handoff.json` said "byte-identical anchor tables"; they are **not** byte-identical and not key-identical — the after-table drops `rf_*/scripts/contracts/constants.py` (×2), `rf_*/SKILL.md` (×2), `trust_iso_config` and **both git HEADs**, while adding iso arm hashes + `captured_at`. | The reviewer **closed each dropped key himself**: constants `278e3e02…` (repo+install), SKILL `45e4e343…` (repo+install), iso trust ABSENT, HEADs `0ee17137…` / `1d2288c0…` unchanged — all match, so the **zero-write conclusion stands**; wording fixed here (see `handoff.json` supersessions). |
| **F10** | LOW | `…_git_status_product` filter scope undisclosed; rf-repo porcelain today shows `M tools/pre_push_gate.py` — 1-line `timeout: 600 → 1200`, mtime `2026-09-22T08:47:22`, **inside this attempt's window** (before-capture `08:46:31`, after-capture `09:19:27`) while the after-table records `""`. | Real source = the concurrent **GATE-TIMEOUT-1200** card editing `tools/pre_push_gate.py` — **not this card**: this card's `commands.json` never touches `tools/` (verified at landing: zero `tools/` references; corroborated `tools/pre_push_gate.py` now declares `timeout: int = 1200`). **Filter scope recorded here**: the key covers "product" paths only and excluded `tools/`; not card-attributable, the card's own pinned anchors all independently verified unchanged. |
| **F11** | INFO | Oracle r2.1+r2.2 = **one combined append with one prefix proof** (`scratch/append_oracle_r2.json`), not two independent prefix proofs; `commands.json` also discloses a failed first append attempt (parse error, no bytes written). | Substance holds — both sections appended after the r1 byte range; `sha256(oracle.md[0:16936])` = `7eaf81b9…` proves r1 untouched. Wording note only. |
| **COND-TEST-DESIGN-CARD** | carried | Test-design card owed (Adjudication B) — false-green rewrite = merge acceptance criterion; shared-cache deepcopy fix; test edits not folded into the merge diff. | Owed, one card, before/at merge. |
| **COND-LANDING-ORDER** | carried | Landing order (Adjudication A): trust-anchor deployment + B1 issuance promotion → this patch (or one window); stay fail-closed; **no bypass flag ever**. | Owner decision order; carried. |
| **COND-MERGE-NOT-APPROVED** | carried | **Merge NOT approved** — authority = invest-core owner; this card delivers a patch, not a merge. | Open owner decision. |
| **COND-ISSUER-NOT-PROMOTED** | carried | Issuer fix (B1) not promoted — production still mints the label from a **5-byte `.txt`** today; the reviewer re-reproduced R1b live in his own RED run. | Open owner decision; defense-in-depth value of the patch stands. |
| **U-1..U-8** | info | Reviewer's 8-item explicit unverified list (L113–L122): ① IC-c3/IC-c4 full regression suites not re-run (captured stdout verified line-by-line + delta arithmetic + `tests/` byte-identity recomputed instead); ② `--check` rc0 at `.claude`/`.codex` roots not re-executed (`.agents` + repo copy re-verified); ③ B1 report byte-pin `73feb059…`/37135 B "PENDING" form not recomputed (current 37224 B / `6bfd2922…`); ④ "no other copy" sweep not repeated (only the 4 named locations); ⑤ freeze-order rests on mtimes + self-reported `captured_at`; ⑥ "no network" not straced; ⑦ cryptography-missing `ImportError` branch unexercised (`pragma: no cover`); ⑧ no whole-tree diff of every install surface (hash-based anchors instead). | Declared boundary with reasons; no inference substituted for conclusion; carried unresolved by design. |

## Not granted

Merge, B1 issuance-side promotion, and trust-anchor deployment remain the invest-core owner's / separate owner decisions — this landing grants none of them. `disclosure_adaptation` stays **unmapped**; `accuracy` stays **unproven**. **0 production bytes written** by this landing: the 3 install surfaces and `Projects\invest-skills` untouched, `reviewer_report.md` + its sidecar untouched (0 bytes), no git write, no signature produced, no trust anchor created.

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent), 2026-09-22.
- Status transition: `review_pending` → `accepted_scoped`, performed in `handoff.json` by this pass on the parent's dispatch; the verdict itself was authored only at `reviewer_report.md` L12 by 独立复核 — never by the implementer and never by this file's author.
- Exactly three files written: `review.md` (created, this file), `handoff.json` (status + status_before_bookkeeping_fix + status_authority + bookkeeping + 8 carried findings appended + stale-field supersessions; all other pre-existing keys untouched), `evidence/INVEST-CORE-ATTEST-GATE/qualification.json` (created).
- sha256 before → after: `review.md` **none → created**; `handoff.json` **`1a6d6e74608c218ed813603bc341d3835f61e77d5fdb4b9800a5f94a917c415a` (25944 B) → reported to the parent** (a file cannot embed its own final hash); `qualification.json` **none → reported to the parent**. Post-write, `reviewer_report.md` re-hashes to `09b4e13e…` / 24941 B (0 bytes written to the carrier).
- `implementer_signed: false`; `implementer_never_signs_acceptance: true`; `verdict_is_transcribed_not_authored: true`.
