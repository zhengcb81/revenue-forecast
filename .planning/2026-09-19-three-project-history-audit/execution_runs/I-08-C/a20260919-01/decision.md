# I-08-C decision.md — decisions taken, and what is explicitly NOT mine to decide

- Card: `I-08-C` (parent `I-08`) · attempt `a20260919-01` · revision **r3**
- Trigger for this revision: independent review returned **`changes_required`**
  (`review.md`, sha256 `c1a8fd11b20f911c7407943dabe70bc493a9cb2959719c13beef21f8e7f1f2a3`).
- Boundary of this revision: **deliverable side only.** No production file is
  written in any of the three repos. No product defect is repaired.
  `disclosure_adaptation = unmapped`, `accuracy = unproven`.
- Authorship: implementer. The implementer does **not** self-sign `accepted`; the
  card remains `changes_required` until an independent reviewer says otherwise.

## 0. One-line conclusion

E4 is now implemented and the exploratory phase is preserved and inventoried, so
the two *deliverable* defects in the review are closed; the card's headline
property still **fails against the product**, and that failure is recorded here
as the card's legitimate **negative result** (F1–F4), not repaired and not
hidden. `handoff.json` therefore carries `status = changes_required`.

## 1. Decisions I am authorised to make (each with reason, counter-case, compatibility)

### D-08C-R3-01 — E4: **implement**, not withdraw

- **Choice.** Add node `test_e4_verification_context_mutation_rejected` with four
  frozen sub-assertions (E4a–E4d, `oracle.md` R3-3).
- **Reason.** The reviewer allowed either branch. The mechanism exists in
  production (`revenue_publication.py:232-240`) and is testable in one node;
  withdrawing would knowingly remove a card-mandated case (A-C3 "每个被签域变异拒绝")
  from the matrix and leave the oracle↔test map at 12/13 forever.
- **Why not withdraw.** Withdrawal is only correct when the case is untestable or
  out of scope. Neither holds: the field is present on every formal receipt and
  the validator has a dedicated gate for it.
- **Counter-case handled.** A test that only mutates the field cannot distinguish
  "the gate binds the context" from "the clone was already broken". E4d supplies
  the converse (correct value → ACCEPTED) and E4c supplies a *valid but foreign*
  context (`S2`'s) to show the binding is per-input, not merely "non-zero".
- **Compatibility.** Additive only. The r1 frozen expectation for E4 (line 54) is
  **not** changed. No r1/r2 expectation is relaxed. The oracle append is
  hash-proved append-only (`oracle.md` R3-5, `handoff.json.append_only_proof`).
- **Recovery.** If E4 had gone red, the correct action was to record the RED and
  re-open the case as a finding — **not** to edit the expectation. It went green
  on the first frozen run (13 passed), which is why the freeze order matters and
  is documented.

### D-08C-R3-02 — Oracle re-freeze discipline: append-only, with a stated self-correction

- **Choice.** Append a new `Revision r3` section to `oracle.md`; never touch the
  r1/r2 body. Prove it by locating the append marker and hashing the fixed
  prefix.
- **Reason.** The plan's own history records a wrong append-only proof built from
  length arithmetic (plan `findings.md` round 35, note 6). The prefix-hash form
  is the method that cannot drift.
- **Disclosed defect found while doing this.** The pre-append file had **no**
  trailing newline, so the act of appending necessarily inserts one byte
  (`\n`) at offset 6831 before the marker. That byte is whitespace only; bytes
  `[0:6831]` still hash to the recorded r2 digest `478bd70e…`.
- **Self-correction disclosed rather than hidden.** My first E4 derivation probe
  reconstructed the verification-context dict with the key `gate_ids` instead of
  `executed_gate_ids` (`revenue_publication.py:85-90`) and reported
  `E4c.equal = false`. Only probe revision 2 is archived, and the error is
  logged in `oracle.md` R3-2.
- **Also disclosed.** Within the r3 append region, section R3-5 was completed and
  R3-6 was given a forward pointer **after** the evidence run, once the real byte
  counts existed. Version 1 of those two sections was written in the same round,
  minutes earlier, and carried no expectations. See `oracle.md` R3-8.

### D-08C-R3-03 — Exploratory phase: preserve what exists, name what does not

- **Choice.** Archive the six surviving artefacts byte-identically
  (`exploratory/`, `exploratory_manifest.json`), write `exploratory_log.md`, and
  list the five things that are **not** recoverable.
- **Reason.** The reviewer's item (4) asks to preserve the exploratory log. The
  log itself did not survive; only cache artefacts did. Writing a plausible
  "reconstructed" stdout would be fabrication.
- **Counter-case handled.** The tempting shortcut is to present the surviving
  `.pyc` files as exploratory evidence. They are not — both carry the r2 source
  id (`field1 = 1790017267` = 2026-09-21T19:01:07Z, `field2 = 8542` bytes). Said
  explicitly in `exploratory_log.md` §2 and `oracle.md` R3-6.
- **Residual risk kept, not papered over.** The exploratory phase stays weakly
  evidenced (prose + cache timestamps). That is a process finding against the
  r1/r2 attempt and is recorded as such.

### D-08C-R3-04 — Verdict-run evidence handling: new file, old file untouched

- **Choice.** The r3 run writes `pytest_r3_verdict.stdout.txt`; the r2 file
  `pytest_verdict.stdout.txt` is **not** overwritten.
- **Reason.** The reviewer independently confirmed the r2 digest
  `cb81112d…`. Overwriting it would invalidate a check the reviewer already
  performed and destroy the r2 record.
- **Consistency check.** The old file is UTF-16LE (PowerShell `>` redirect), which
  is why a binary-safe reader is needed; the r3 file is written the same way for
  consistency, and both are declared in `commands.json`.
- **Binding note.** The r3 run executed the test file frozen at 10902 B /
  `0072b16019825b46e1fa27e2decec615675cb33336eb3968fae32fb8e0dfc7f5`, recorded
  before the run. `-B` + `PYTHONDONTWRITEBYTECODE=1` means no `.pyc` was
  regenerated, so the archived r2 bytecode headers survive as timeline evidence.

### D-08C-R3-05 — Exit-code classification is per case, not per pytest process

- **Choice.** Publish an `exit_code_legend` and classify all 13 cases
  individually (`oracle.md` R3-4), while recording the single raw pytest rc
  separately.
- **Reason.** `START_HERE.md` requires each batch to carry a self-describing
  legend; one pytest process returns one rc for 13 nodes, and E11/E13 are green
  pytest nodes whose *business* verdict is rc=3.
- **Consequence.** A reader must not infer "13 passed ⇒ card accepted". E11 and
  E13 pass only because they assert the offending behaviour is accepted by
  production — they are the pinning of a defect.

## 2. Decisions I am NOT authorised to make — recorded product findings

These are the reviewer's adjudicated findings. **None is repaired by this card.**
Each requires a separate card / owner decision, an owner-authorised scope, and
(in most cases) a product change in `scripts/`. Recording them here is the
card's legitimate negative result.

### F1 — `attestation_status="host_signed"` is a plain label; consumers verify it NOT AT ALL — HIGH

- **Mechanism (reviewer-verified, reproduced from source).** The label is set from
  a boolean: `revenue_core.py:167`
  `attestation_status = "host_signed" if attestation_capability() else "unattested"`;
  `attestation_capability()` (`revenue_core.py:113-125`) returns True if the
  `REVENUE_ATTESTATION_PROVIDER` path **exists as a file** — no key, no issuer,
  no signature, no provider invocation. Consumption is set membership only:
  `revenue_publication.py:222-226` `require(attestation in (None, "host_signed",
  "unattested"), …)`. There is no signature, issuer or `publication_attestation`
  check anywhere in `scripts/`.
- **Reviewer's new material finding.** Pointing `REVENUE_ATTESTATION_PROVIDER` at
  a 5-byte plain `.txt` yields `attestation_capability() == True`, so a **formal**
  publication is stamped `host_signed` with **no signature or issuer field**, and
  the strong dispatcher **accepts** it. Any operator can mint "host-signed"
  artifacts with an env var aimed at a text file.
- **Plus.** The honest `unattested` package is also accepted by every consumer
  entry point in this repo — consumers do not under-verify, they do not verify.
- **Independently pinned in this card** by `test_e11` (`oracle.md` E11, rc=3).
- **Not fixed here because:** the fix is a consumption-side trust gate in
  `scripts/` (product code), and the downstream `invest-*` consumer
  (`~/.claude/skills/invest-core/scripts/invest_contracts.py:1130-1142`, cited
  read-only from I-08-A) is in another repo owned by another card.
- **Reviewer's proposed direction (PROPOSAL — requires owner authorisation, not
  adopted here):** either carry a binding record (`publication_attestation` with
  issuer/key/domain, per I-08-A E27/G4) and require it whenever
  `attestation_status == "host_signed"`, or declare the label non-evidentiary and
  make trusted-formal consumers require an explicit verified-signature field;
  and stop treating file existence as signing capability.

### F2 — the receipt layer is hash-consistency only — MEDIUM

- After the three public self-hashes are recomputed, a mutated top-level value
  passes `validate_publication_receipt` and is rejected only by the strong
  dispatcher. Pinned in this card by `test_e6`.
- Severity stays **medium, not high**: both public consumers in this repo
  (`validate_forecast_output`, and `render_markdown` which calls it at
  `revenue_report.py:1278`) run the strong path. The exposure is a caller who
  picks the plausibly-named `validate_publication_receipt` and believes a
  publication was validated when only self-consistency was checked.
- **Proposed direction (PROPOSAL, not adopted):** document or deprecate
  `validate_publication_receipt` as a non-security hash-consistency check and
  state that consumers must call `validate_forecast_output`.

### F3 — `segments[i].base_revenue`: presentation-field coverage gap — MEDIUM (scope-narrowed)

- A self-hash-consistent forgery of `segments[0].base_revenue` is accepted by the
  receipt layer **and** the strong dispatcher, and renders into the official
  分部表. Pinned in this card by `test_e13`.
- **Scope-narrowed by the reviewer, and this card adopts that narrowing:** company
  totals do **not** move — `base_revenue` and
  `consolidated_forecast[scenario].annual_revenue` are independently validated by
  `_recompute_consolidated_paths` (`revenue_report.py:65-155`) — and a coherent
  full-story forgery that also moves the reported total and historicals is caught
  by `validate_base_reconciliation` (`contracts/document.py:955`) and by the
  receipt's `validated_input_sha256`. So this is a **result-layer coverage gap in
  a presentation field, not a route to a forged company total.** The
  implementer's original wording overstated it; the narrower wording is the one
  of record.
- **Proposed direction (PROPOSAL, not adopted):** cross-check
  `segments[i].base_revenue` against the segment's `base_revenue_parameter_id` in
  the embedded input, or fold it into the `incremental_contribution`
  reconciliation that already runs.

### F4 — card anchor drift — LOW

- `publication_registry.py` was changed by commit `1dbae639` ("feat(ZR-701)")
  after the card froze `44662744…`; the file now hashes `29aaae4f…`.
  `is_registered` is still at line 188 with the same fail-closed contract, so the
  card stays executable against the current file. Correctly reported, not
  repaired, per scope.

### Why none of F1–F4 is mine to close

1. Each fix touches production `scripts/` — outside this card's allowlist
   ("隔离 revenue 对应 publication/attestation/pipeline 测试"; the card's action 3 says to
   *check* that consumers do not pass on the label, not to add the trust gate).
2. F1's decisive consumer lives in a **different repo** (`invest-core`), which the
   card explicitly assigns to that consumer's owner.
3. Repairing a trust gate changes the publication contract for cross-repo
   consumers; that is a professional design decision requiring `decision.md`
   adjudication by the owning reviewer, not an implementer choice.
4. The card's own failure-stop condition forbids claiming the property is wired
   when only a helper was tested — so the honest deliverable is a documented
   negative result plus a handoff, which is what this revision produces.

## 3. Items this card does NOT decide (registration only)

- Whether `attestation_status` should keep its current name/semantics at all.
- Whether `validate_publication_receipt` is deprecated, renamed, or left as a
  documented convenience.
- Whether `segments[i].base_revenue` should be bound through the input parameter
  id or through the `incremental_contribution` reconciliation.
- Any change to `PUBLICATION_RECEIPT_SCHEMA_VERSION` or to the receipt contract.
- The status of `invest-*` consumers: **unverified by this card** (card-declared
  out of scope), so no claim of ecosystem-wide coverage is made.
- Card anchor refresh for `publication_registry.py`: reported as F4; the card
  document is not rewritten by an implementer.

## 4. Failure-stop self-check (card "失败停止条件")

| Condition | Status |
|---|---|
| Could not find a real consumer entry point | **Not triggered** — three real entries were exercised by path: `validate_publication_receipt`, `validate_forecast_output`/`validate_published_forecast`, `is_registered` |
| Only tested a signature helper while claiming consumers are wired | **Not triggered** — no claim of wiring is made; E11 pins the opposite. The card is handed over as `changes_required` |
| Needs a change in an out-of-scope repo without owner coordination | **Triggered and correctly stopped** — F1's `invest-core` side is recorded as an owner dependency instead of being edited |

## 5. Not done / not verified (carried forward, not closed)

1. `invest-*` consumers: **not executed**. The reviewer's unverified-list item 1
   stands unchanged.
2. No CLI publish transaction was exercised; F01/F02 are covered transitively
   through the dispatcher chain.
3. The exploratory run's stdout is unrecoverable (`exploratory_log.md` §3).
4. E13's expectation was originally pinned empirically rather than derived from
   code reading; retained and labelled, not retro-fitted.
5. `is_registered`'s fail-closed behaviour was exercised in-harness only
   (`test_e12` against a temp registry), not against an independently corrupted
   registry copy outside the harness.
6. Per this card's scope, `disclosure_adaptation = unmapped` and
   `accuracy = unproven`; nothing here is evidence of forecast accuracy.

---

# Fix round `I-08-C-REFREEZE` — decision record (appended after r3 closed)

## 6. WHY this re-freeze exists (the owner ruling, verbatim)

Owner ruling, `OWNER_DECISIONS.md` §16 (file 53286 B, sha256
`4c9acf9ec95c8ec028b6e77719ddf32dbbbc1fb545c91cb702521d65a70aa2f3`):

- 原话 (line 365): 「A-1: b（允许修 prune 代码，不授权执行 prune）
  **A-2: 批准** B: a（提高门超时到 1200，立卡红绿） C: 先推已收口的 4 张，
  B1/B3/I-14-D 攒第二批 D-G1: a D-G2: 留置/（或给取舍） E-1: 150/60
  E-2: 重跑 E-3: 立卡 E-4: 维持暂不签」
- 裁定表 (line 370): 「**A-2 批准** | I-08-C oracle 追加式重冻
  （E11/E13 由"缺口在册"翻转为"攻击必拒"），收口归其 reviewer |
  与建议一致 | 已派 `I-08-C` refreeze 卡」

**The core reason, in one paragraph.** I-08-C's frozen oracle pinned **E11**
(attestation-label flip) and **E13** (forged `segments[i].base_revenue`) as
EXPECTED GAPS: the attack passed, recorded as green nodes with business rc=3.
Card **B1** closed both gaps — and the e1 collateral (file-existence is no
longer signing capability) — in an isolated tree
(`B1-I08C-product-fixes\a20260921-01\iso\fixed\rf`). Against that tree the
pinned-gap expectation necessarily FAILS. That failure is **expected, not a
regression**: it is exactly why the owner approved this re-freeze (A-2: 批准).
Keeping the pin would have made the frozen expectation wrong about the tree it
describes; flipping it to "attack MUST be rejected" makes the suite a real gate
again. 收口 (closure) stays with the reviewer — this round never self-signs.

## 7. Decisions taken this round (each with reason, counter-case, boundary)

### D-08C-RF-01 — number this append **r4**, not "r3"

- **Choice.** The fix-round card says "append-only oracle revision r3"; the file
  already contains a **closed** r3 whose closing line forbids further r3 edits
  ("any later change must open a new revision"). Appended as **Revision r4**,
  labelled in its header as "fix-round instruction label: r3".
- **Why not follow the instruction's number literally.** It would either
  duplicate a revision id or violate the file's own append-only rule; the
  instruction's substance (one new append-only revision, same form) is fully
  satisfied, and `handoff.json`'s fix-record points at "revision r4 (instruction
  label: r3)" so no reader can lose the thread.

### D-08C-RF-02 — superseded-record form for E11/E13, and for the E1 collateral

- **Choice.** Flip E11/E13 to rejection with B1's exact reasons
  (`attestation_missing_record` / `segment base revenue mismatch`); preserve
  each old expectation **verbatim** as a superseded record with reason +
  provenance — the same shape as I-14-H's W1 2220→1740 correction.
- **Why not simply rewrite.** The r1/r3 pins are part of the historical record
  (they were the card's legitimate negative result); the supersession must show
  *what* changed, *why*, and *on whose authority* — otherwise a re-freeze is
  indistinguishable from fitting expectations to a green run.
- **The E1 collateral (counter-case handled).** The disclosed exploratory run
  showed E1 failing on the fixed tree: B1 REM-01(b) retired
  "file existence == capability", so the honest fixture stamped with
  `sys.executable` is now truthfully `unattested`. Asserting `== "host_signed"`
  unconditionally would pin the I-08-A §7.1 **false-green** as an expected value
  — the same staleness class as E11/E13, in the positive direction. Decision:
  make the label assertion **tree-conditional** (fixed tree → `unattested` +
  no record; any other tree → the original `host_signed` assertion, byte-for-byte
  the r1 check), keep the validators-pass-twice property unconditional, and
  supersede the old line in oracle R4-2/S-3 with B1's probe as provenance. The
  alternative — building a working fake provider so S is genuinely
  `host_signed` everywhere — was rejected as a much larger test rewrite whose
  fixture machinery would be copied from B1's attempt.

### D-08C-RF-03 — env-var import-root override, hashed in three stages

- **Choice.** `REPO = Path(os.environ.get("RF_IMPORT_ROOT") or <production>)`;
  unset ⇒ byte-identical default to every prior run. Recorded hashes: r3 file
  `10902 B / 0072b160…` → override-only interim `11360 B / 61ef2b67…`
  (exploratory only) → **r4 frozen `13152 B / 3f83fdf2…`**.
- **Reason.** The suite bound production by fixed path; pointing it at B1's
  isolated trees requires a root override. Defaulting to production keeps the
  r3 evidence runs reproducible.

### D-08C-RF-04 — node ids renamed for the flipped cases only

- **Choice.** E11 → `…_is_rejected_at_consumption`, E13 →
  `…_forgery_is_rejected_by_output_gates`; every other id untouched; old→new
  mapping recorded in oracle R4-3.
- **Reason.** The old names *asserted the retired gap*; keeping them would make
  a green node read as a red claim. Renaming any other node would have churned
  cross-card references (B1 quotes the old ids) for no gain.

### D-08C-RF-05 — freeze order, with the exploratory run disclosed rather than hidden

- **Order:** env-override edit (hashed) → exploratory run vs the fixed tree
  (disclosed; revealed the E1 collateral; stdout archived) → r4 test file frozen
  (hashed) → oracle r4 appended (prefix-proved) → the four evidence runs.
- **Counter-case handled.** Because the exploratory run observed the fixed-tree
  outcome first, the r4 expectations are *corroborated* by it; their primary
  derivation is B1's `after/probe_fixed.txt` (written before this card) plus the
  fixed source lines, and the falsifiable half of the contract (unfixed trees and
  the mutation must go RED, frozen in oracle R4-4 **before** those runs ran) is
  what prevents circularity. Recorded in oracle R4-6.

### D-08C-RF-06 — three discriminating runs, all matching the frozen contract

| Run | Tree | Frozen in R4-4 | Observed |
|---|---|---|---|
| RUN-A | B1 `iso/fixed/rf` | 13 passed, rc 0 | **13 passed, rc 0** ✓ |
| RUN-B | production (unfixed, override unset) | exactly {e11,e13} failed, rc 1 | **exactly {e11,e13} failed, rc 1** ✓ |
| RUN-B2 | B1 `iso/rf` (production-identical) | exactly {e11,e13} failed, rc 1 | **exactly {e11,e13} failed, rc 1** ✓ |
| RUN-M | fixed tree + superseded-expectation mutation file (`12976 B / eb19e628…`) | exactly {e11,e13} failed, rc 1 | **exactly {e11,e13} failed, rc 1** ✓ |

RUN-B/B2 are the anti-vacuity proof (the gap still reproduces on unfixed
bytes ⇒ the flip is load-bearing); RUN-M is the mutation proof (the old
pinned-gap expectation cannot pass against the fix ⇒ the flip is not vacuous).

### D-08C-RF-07 — status `changes_required` → `review_pending`, never self-signed

- **Choice.** `handoff.json.status = review_pending`,
  `implementer_self_acceptance = false`, `ready_for_re_review = true`, with a
  fix-record pointing at oracle r4.
- **Reason.** Owner ruling: 收口归其 reviewer. This card re-freezes the oracle
  and readies re-review; the verdict is the reviewer's to give.
- **Two separate steps remain, stated in the handoff too:** (1) promotion of
  B1's fix into production is an owner decision not taken here (production stays
  byte-identical, verified after every run); (2) I-08-C's acceptance is a future
  reviewer verdict on this re-frozen package. Neither is implied by this round.

### Boundaries re-asserted this round

- Production READ-ONLY: anchor hashes unchanged
  (`183803bb…` / `1821fd2a…` / `a85fb484…` / `29aaae4f…` /
  `bc3256bb…`), `git status --porcelain -- scripts tests config artifacts`
  empty (rc 0) after all four runs; no git write command executed.
- B1's attempt READ-ONLY: executed from only, with `-B` +
  `PYTHONDONTWRITEBYTECODE=1` + `-p no:cacheprovider` + `--basetemp` inside this
  attempt; after the runs the newest mtime under B1's tree is still
  `2026-09-21 23:14:47` (B1's own files) and its three fixed hashes are unchanged.
- Oracle change APPEND-ONLY: `sha256(bytes[0:22335])` still
  `94a853e9…` and `sha256(bytes[0:6831])` still `478bd70e…`
  (`scratch/fixround/prefix_proof.json`, `append_only_proof: true`, rc 0).
- `disclosure_adaptation = unmapped`, `accuracy = unproven` unchanged.
