# I-08-C-RESIDUAL — decision.md (final form 2026-09-23)

- Plan: `2026-09-19-three-project-history-audit`
- Card: **I-08-C-RESIDUAL** — close the residuals keeping goal item ① short of 8/8
  (AUDIT-DESIGN: 「I-08-C oracle 重冻未收口」, 7/8; I-08-C partial)
- Attempt: `execution_runs/I-08-C-RESIDUAL/a20260923-01`
- Roles: implementer = closure agent (never self-signs `accepted`);
  independent reviewer = to be assigned (handoff requests one).
- This file grew from the anti-death placeholder created before the oracle freeze; the
  placeholder section D-0 is preserved as-is below. Expectations were frozen in
  `oracle.md` before any judged run; nothing here rewrites a frozen expectation.

## D-0 (placeholder text preserved from 2026-09-23 pre-oracle)

> 1. Close the **3 leftover (遗留) conditions** the B1 reviewer attached to the
>    `accepted_with_conditions` acceptance of `B1-I08C-product-fixes/a20260921-01`.
> 2. Resolve the `I-08-C/a20260919-01` original-attempt verdict state via dated
>    `verdict_supersession_20260923.md` inside this attempt only.
> 3. State the goal-item counting basis precisely.

## D-1 — identification of "the 3 遗留" (conditions block extraction)

The acceptance's conditions block (`B1-I08C-product-fixes/a20260921-01/reviewer_report.md`
VERDICT L16–18, quoted verbatim in `oracle.md` §1) attaches five "must be closed
before/at promotion" defects (F1–F5) and two tracked residuals (F6/F7). Its own partition:
"**three non-security documentation defects and two evidence-completeness defects**".

**Frozen reading (oracle §2): the 3 leftovers = F1, F2, F3** — the three finding bodies
(oracle §1.4 verbatim) and §9 items 1–3 ("Required before promotion (in order)"); the
evidence-completeness pair = F4/F5 (§9 item 5 is literally evidence-preservation
protocol). F6 ("No action required") and F7 ("a residual to track") are by their own text
outside the must-close set.

**Disclosure:** the report's per-finding severity labels do not partition 3+2 as neatly as
the verdict sentence (only F1/F3 carry a "documentation" label; F2/F4 carry "evidence";
F5 is "pre-registration"). Under any alternate reading — {F1,F3,F5}+{F2,F4}, or the three
blocks literally labelled "Residual" (§3.2/F6/F7) — every member is still disposed with
fresh evidence in this attempt (D-2 rows). 一条不许静默丢: nothing is dropped under any reading.

## D-2 — per-residual table (condition → demand → closure evidence → status)

| # | condition (verbatim text pinned in `oracle.md` §1) | what it demands | closure produced by this card | status |
|---|---|---|---|---|
| **L1 = F1** (MEDIUM, documentation): "Correct `oracle.md` with a further append-only revision (r5) — do not edit r1–r4 bytes" (§9.1: correct the §R3-2/R3-3 field-count text to 10 fields; `result_sha256` in the *request* only, pinned to the sentinel) | append-only oracle correction + corrected source-of-truth | **re-freeze with corrected source-of-truth = `oracle.md` §2.1 of THIS attempt** (closed 10-field set, `receipt_sha256` fixpoint exclusion, `result_sha256`→request-sentinel rule) + fresh verification of the landed correction: E-L1.1 four prefix hashes MATCH (`81af1240`/`60ecbca7`/`231e7976`/`fadf8a5e`), markers `## Revision r5`@39288 / `r6`@43299 / `r7`@47539 single-at-offset, total 57911 B (`evidence/E_L1_checks.json`); E-L1.2 corrected text present in the r5+ region (verbatim dump `evidence/E_L1_r5_region_dump.txt`); E-L1.3 three-way field count **10/10/10** (fixed-tree AST, frozen-test AST, runtime import — all three sets == §2.1) (`evidence/E_L1_fieldcount_threeway.json`) | **CLOSED** (correction landed earlier by B1-PREREQ r5+r7 under REM-40; independently re-measured + re-frozen here) |
| **L2 = F2** (MEDIUM, evidence): "fold a node equivalent to R13 into the card's test file, and add M6 to the mutation table" (§9.2) | node + mutation-table entry, and proof they measure the clause | E-L2.1 presence: `B1-PREREQ/test_r13_equiv_rem41.py` (sha256 `6aa0f1a8…` = the register's pinned node; 2 nodes, fixtures imported from the frozen module) + "## Revision r6 — F2/REM-41: mutation M6 joins the proof surface" in the SRC oracle (`evidence/E_L2_presence.json`); E-L2.2 **fresh judged run on the fixed tree: 14/14 PASSED, rc 0** (`evidence/E_L2_run_fixed.stdout.txt`); E-L2.3 **fresh judged run on the M6 mutant: exactly `test_rem41_a…` FAILED, 13 passed, rc 1**, positive control green (`evidence/E_L2_run_m6.stdout.txt`) — the added node is load-bearing against exactly the regression F2 names, and the frozen 12-node set's blind spot (12/12 green on M6) is reproduced | **CLOSED** (landed earlier by B1-PREREQ under REM-41; independently re-executed here, both arms) |
| **L3 = F3** (LOW, documentation): "either implement E21 (`issuer`/`key_id` vs the resolved trust entry) or delete the E21 claim from the docstring and record E21 as not-closed" (§9.3) | implement E21 **or** delete claim + record not-closed | option (a) **stopped at its honest label: BLOCKED-on-cap-change** (trust loader resolves fingerprint→public key only, no `issuer`/`key_id` — `evidence/E_L3_trust_loader.json`; E21 needs the 12-field trust-entry schema = I-08-A E25, NOT implemented); option (b) executed to the limit of this card's authority: **E21 recorded as NOT-CLOSED** (`evidence/L3_E21_not_closed_record_20260923.md`, dated) + **exact docstring-deletion patch `patches/P-L3_delete_E21_docstring_claim.patch`** landed (ready-to-apply against current promoted bytes `bc2bb4a3…`); application = production write reserved to the parent's batch (goal discipline ⑤ 生产零合并 + OWNER_DECISIONS.md:426 父保留各仓提交权) — see D-5. Supporting measurement: E21 documented at `scripts/revenue_publication.py:235-236`, **zero raise sites**, `issuer`/`key_id` outside the signed request set (`evidence/E_L3_e21_scan.json`) | **CLOSED as documentation closure (option b), with one routed residue**: P-L3 application in the parent's next production batch. If the parent's counting requires the deletion APPLIED in production bytes, that single one-clause edit remains owner/parent-batch-gated — stated, not hidden |
| AX-1 = F4/F5 (the two evidence-completeness defects) | "preserve raw run outputs under distinct labels, and give `decision.md` a freeze-time hash, in the next attempt's protocol" (§9.5) | this attempt IS the next attempt: distinct raw label per run (incl. preserved superseded `c9_*` run + refined `c9b_*`), deliverable hashes frozen at handoff; fresh re-verification of the F4 historical question: the r1 RED stdout `58863ffb…` decodes (UTF-16) to **"10 failed, 2 passed"** (2 PASSED / 10 FAILED node lines) = register §22/补1 erratum re-confirmed (the true permanent gap is only the r1 test file 18236 B/`e6c0949c…`); F5 substance: 24-entry hash freeze chain + SHA256SUMS 31/23 lines present (`evidence/AX1_f4f5_checks.json`) | **CLOSED as protocol + record** (register REM-43/44 closed earlier; re-measured here) |
| AX-2 = F6 (disclosed residual) | "No action required"; make the residual unambiguous | dated permanent-limitation record incl. the parent's F6-clarification (rewrite+consistent-recompute ⇒ both ACCEPTED [unchanged]; without recompute ⇒ receipt ACCEPTED / forecast REJECTED [strengthening]) (`evidence/AX_annex_closure_records_20260923.md` §AX-2) | **CLOSED as recorded permanent limitation** |
| AX-3 = F7 (adjudication residual) | "record REM-02 as a documented limitation with the caller-side trap still open, and decide (a)/(b)/(c)" (§9.4) | status recorded verbatim: **"documented limitation, consumer-side guardrail not yet in place"** (never "closed"); **decision = (a) `receipt_schema_version` bump + (c) follow-up rename/deprecate item** (reviewer's recommendation "(a) plus a follow-up item"); (b) rejected with reason (frozen design decision r1 §3.5(c); measured limitation of that rationale disclosed honestly); state re-measured on promoted bytes (phrases present, marker exported, zero warn/raise sites) (`evidence/c9b_check_rem02.stdout.txt`) | **CLOSED as record + decision**; implementation of (a)/(c) = product/contract track (guardrail explicitly still NOT in place) |
| AX-4 = §3.2 residual (input-document re-anchoring) | recorded, "not a defect of this card" | dated accepted-by-design record (`evidence/AX_annex_closure_records_20260923.md` §AX-4) | **CLOSED as recorded limitation** |
| AX-5 = AUDIT-DESIGN D1b/D1c (B1 evidence-entry naming) | append-only erratum; "不得事后补文件冒充当时证据" | fresh fs-scan re-confirms `before/production_anchors.txt` NEVER produced (0 hits plan tree + RF repo; `.json` sibling exists) (`evidence/AX5_d1b_fsscan.json`); dated erratum record: entry = **未产出（仅 .json）** (`evidence/AX_annex_closure_records_20260923.md` §AX-5). Sibling carrier: BOOKKEEP-REPAIR landed `evidence_erratum_20260923.md` in the B1 tree concurrently (same disposition, cross-referenced, not duplicated as a claim) | **CLOSED as append-only erratum** |

## D-3 — original-attempt state resolution (summary; full record = `verdict_supersession_20260923.md`)

- Dual-caliber: `review.md:9` round-1 `changes_required` vs `reviewer_report_r2.md:10`
  round-2 `accepted_scoped`.
- **Option (i) chosen** (close-and-note superseded-by-refreeze-chain), with the per-item
  finding that **option (ii) has no remaining actionable demand** — all four round-1
  demands were executed by the chain (B1 product fixes → B1-PREREQ F1–F5 closures →
  FIX-I08C-REFREEZE-1 oracle r4 → round-2 `accepted_scoped`; promotion separately under
  owner 「B: 全批」) and independently accepted. Chain corrected: **NOT via I-14-D r7**
  (that is the REM-04/REM-81 chain).
- Authority: owner **A-2 「批准」** + ruling row 「…追加式重冻…**收口归其 reviewer**」
  (OWNER_DECISIONS.md L365/L370) + the round-2 carrier verdict + parent dispatch
  (register §74).
- **Before-hash assertion: `I-08-C/a20260919-01/handoff.json` =
  `b83e04a670d464343816e978c102dab269dadc79aef2b9842d9d0c505ef82f12` / 58814 B =
  before = after (UNCHANGED)** (`evidence/manifests_comparison.json`);
  whole original attempt 73→73 files, 0/0/0.

## D-4 — goal-item counting basis (the counting statement)

**Goal item① (owner goal rev. 4: 「8 在飞卡收口」) counts its slot 「I-08-C oracle 重冻」as
CLOSED (8/8) on the following basis — "closed" used in exactly this sense:**

1. **The oracle re-freeze is delivered and independently accepted.** FIX-I08C-REFREEZE-1
   appended I-08-C `oracle.md` revision r4 (E11/E13 gap pins → attack-must-be-rejected;
   prefix proofs `[0:22335]=94a853e9…`, `[0:6831]=478bd70e…`; superseded records S-1/S-2/S-3
   preserved verbatim), and the round-2 independent re-review accepted exactly that scope:
   `reviewer_report_r2.md` `## VERDICT: accepted_scoped` (13285 B / `ee5046a5…`,
   sidecar re-verified), owner-ruled 「收口归其 reviewer」.
2. **The 3 leftover conditions attached to the B1 acceptance (F1/F2/F3 — verbatim in
   `oracle.md` §1.4) are closed with the evidence their own texts demand**: L1 corrected
   source-of-truth re-frozen + 10/10/10 three-way measurement; L2 R13-equivalent node +
   M6 in the mutation table + fresh 14/14 GREEN and M6 exactly-1-RED anti-vacuity arms;
   L3 E21 recorded NOT-CLOSED + docstring-claim deletion landed as apply-ready patch P-L3
   (application routed to the parent's production batch — the only routed residue).
3. **The original-attempt state is resolved** by dated supersession
   (`verdict_supersession_20260923.md`): round-1 `changes_required` = superseded-by-chain
   close-and-note, handoff before-hash asserted unchanged, round-2 `accepted_scoped` is
   the current state with the carrier's scope limits intact.
4. **No acceptance finding is silently dropped**: F4/F5 (protocol + erratum re-verified),
   F6 (permanent limitation), F7 (recorded + (a)/(c) decided), §3.2 (recorded), AUDIT-DESIGN
   D1b/D1c (append-only erratum) each carry an explicit disposition (D-2).

**What "closed" does NOT mean (scope discipline, carried verbatim into the handoff):** it
does not mean the product defect surface is empty (E21 implementation and the REM-02
consumer guardrail (a) remain on named product tracks; the caller-side trap is open by
explicit record); it grants no qualification beyond this card's scope; it does not extend
to invest-* cross-repo consumers (unverified — INVEST-CORE card owns that site); it claims
nothing about forecast accuracy (`accuracy = unproven`) or disclosure adaptation
(`disclosure_adaptation = unmapped`).

With item「I-08-C oracle 重冻」closed on this basis, the eight in-flight cards of goal
item ① count **8/8 closed** (the other 7 were already carried as closed by both audits).

## D-5 — changes.diff justification (product/test fix question)

`changes.diff` contains **NEW files of this attempt only** plus **P-L3 as an
apply-ready product patch that is deliberately NOT applied**. Justification: the leftover
L3 does demand a product-doc edit (delete the E21 docstring claim); but every card in this
plan holds production zero-write (goal discipline ⑤ 「生产零合并」; this card re-verified
`git status --porcelain -- scripts/ tests/ config/ artifacts/` = EMPTY,
`evidence/c11_production_state.json`), and production commit rights are reserved
(OWNER_DECISIONS.md:426 「**父保留各仓提交权**」). Applying P-L3 in place would leave the
RF repo dirty outside any promotion batch and break the discipline the audits score.
Therefore: patch landed + routed (D-2 L3 row); no product/test file was modified by this
card. P-L3 is a one-clause docstring change against the current promoted bytes
(`bc2bb4a3…`), verified against line numbers `scripts/revenue_publication.py:235-236`.

## D-6 — process disclosures (honest, all preserved)

1. `I08CR-c0` attempts 1–2 were harness errors **before any measurement succeeded**:
   (1) my `Out-File` targeted a not-yet-created `evidence/` dir (capture failed; the
   read-only hashing ran but its raw stdout was lost); (2) my `manifests.py` had a
   `parents[1]`/`parents[2]` path bug (reported 0 files). Both fixed; attempt 3 is the
   recorded `c0_manifests.stdout.txt`. No evidence file was fabricated from the lost raws.
2. `I08CR-c9` run 1 returned rc=3 on a checker artifact: my needle `"not a security
   boundary"` was case-sensitive and the docstring renders it `**NOT a security boundary**`
   (bold caps). Raw preserved as `c9_check_rem02.stdout.txt`; checker refined
   (case-insensitive) and re-run as `c9b_check_rem02.stdout.txt` (rc 0). The measured
   limitation found in the same run is carried, not smoothed: `test_zr701`/`test_zr705`
   contain no locatable explicit warnings assertion (see AX-3).
3. **Concurrency event:** during the run window a sibling session (BOOKKEEP-REPAIR /
   a20260923-01, parent dispatch #15) landed `review.md`, `evidence_erratum_20260923.md`
   and the `handoff.json` status flip in the B1 attempt (mtimes 22:56:31/23:04:27/22:56:32).
   Attribution measured (`verdict_supersession_20260923.md` §4): not this card's writes;
   reported, never repaired or re-attributed. The demanded untouched-assertion concerns the
   ORIGINAL attempt `I-08-C/a20260919-01`, which is strictly 0/0/0.
4. Minor measured notes: the needle `"hash-pin"` was not found in the B1 oracle text
   (`b1prereq_oracle_hash_pin_policy_present: false` — wording differs from my needle);
   AX-1 recorded as measured.
5. This card executed no git write command and no network call.

## D-7 — unverified / not closed by this card

1. invest-* cross-repo consumers (incl. the decisive `invest_contracts.py:1130-1142`
   gate) — unverified here, INVEST-CORE card owns that site.
2. P-L3 application in production bytes (routed, see D-5); E21 implementation
   (cap-change blocked, product card); REM-02 guardrail (a) implementation
   (contract change ⇒ professional review, product track).
3. The full I-08-A provider protocol (E18/E19/E22–E25/E29, 12-field trust schema,
   L1/L2/L3 proof domain) and CLI/transaction entry points — out of scope of the whole
   chain, unchanged.
4. The r1 test file (18236 B / `e6c0949c…`) is a permanent historical gap (never
   rewritten); the r1 exploratory 8/12 stdout is permanently lost (old loss, carried).
5. `disclosure_adaptation = unmapped`, `accuracy = unproven` — unchanged.

## F erratum (landing)

Appended 2026-09-24 by the carrier-landing pass, BEFORE the three landing writes
(corrections-first rule). This section records the independent reviewer's findings F-1..F-4
verbatim; D-0..D-7 above are retained byte-untouched (append-only erratum, same style as the
sibling landings). Verdict authority (transcribed, never authored here):
`reviewer_report.md` sha256 `cc63bd99ce96bf0ede4c0e2d5da467942cb42d18e19c694d6160a1c21a2f7593`
(31795 B / 434 lines, `.sha256` sidecar round-trip verified at landing), verdict block at
bytes [922,2284) / lines 17-36, findings at bytes [2284,6820), counting ruling at bytes
[24272,26638), scope-if-accepting at bytes [29854,31187).

### F-1 (MUST-FIX — batch precondition) — P-L3 is not plain-apply-ready

Recorded verbatim (carrier §1 F-1, bytes [2300,3880)):

> P-L3 patch NOT plain-apply-ready — `@@ -232,8 +232,12 @@` header vs 13 new body lines →
> `git apply --check` rc128 "corrupt patch at line19"; **batch rule: apply with
> `git apply --recount` OR fix digit12→13, then `--check` rc0 required**; applied result
> verified AST-equal-stripped = zero behavior (single docstring hunk @232-243); card never
> claimed --check ran (inspection-based "apply-ready" refined, not falsified).

- Disposition: **CARRIED as a batch precondition.** `patches/P-L3_delete_E21_docstring_claim.patch`
  enters the parent's next production batch ONLY under the recount rule above (plain
  `git apply --check` on its current bytes FAILS, rc 128 — reviewer-measured, git 2.51.2).
  Not a counting blocker: the reviewer's §9 ruling counts L3 CLOSED with P-L3 ROUTED,
  *conditional on this F-1 fix being carried into the application step*. Mirrored in
  handoff.json `bookkeeping.f1_batch_precondition` and qualification.json F-mirror.

### F-2 (disclosure; not a counting blocker) — freeze-time pins of the two living parent documents are not retro-verifiable

Recorded verbatim:

> freeze-time living-doc pins `4bed42c6…`(OWNER_DECISIONS)/`535152f0…`(REGISTER) not
> retro-verifiable (docs changed, no freeze copies) — mitigated: all cited authority lines
> content-verified against current bytes (L365 A-2 原话, L370, L420「B: 全批」, L426 父保留提交权,
> REM-42@L70, E21@L780, RESIDUAL 排卡@L1493 — verbatim matches) → **pin supersession to be
> ledgered at next parent register edit (this note = that ledger entry)**.

- Disposition: **LEDGERED** — this note is the pin-supersession ledger entry (mirrored in
  handoff.json `bookkeeping.f2_pin_supersession_ledger`). Content verification of every
  cited authority line stands in for the non-reproducible freeze-time hash pins; all 4 owner
  citations and both register citations matched at their cited line numbers.

### F-3 (trivial) — one process disclosure sits in the wrong file

Recorded verbatim:

> F-3 commands.json trailing-comma fix disclosure add to D-6 list

- Disposition: **ADDED to the D-6 list** (via this erratum): **D-6 addendum** — the
  `commands.json` final-form trailing-comma fix (previously disclosed only in handoff
  `deliverable_hashes` note) is hereby a numbered D-6 process disclosure; JSON validity was
  re-checked under Python `json` + PS `ConvertFrom-Json` at the original fix and again at
  landing. D-6 items 1-5 above retained verbatim.

### F-4 (trivial, wording) — command-count wording

Recorded verbatim:

> F-4 "13 commands"=13 frozen+c9b=14 executions, c9b mtime ordering cosmetic

- Disposition: **NOTED** — `verdict_supersession_20260923.md` §4's "13 commands" means the
  13 frozen `commands.json` entries; executions were 14 (`c9` + refined `c9b`). The
  `commands_executed` array's implied ordering vs c9b mtime (23:08, after c10/c11 at 23:01)
  is cosmetic: argv and write-roots are per-entry, expectations unchanged, both c9 raws
  preserved under distinct labels. Supersession §4 left byte-untouched.

### Note (parent prompt typo)

Recorded verbatim:

> typo note: r4 prefix real value `fadf8a5e…` (parent prompt's `fadf8e5e` was wrong; card
> matched reality).

- Confirmed at landing: reviewer independent extraction = `fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae`
  (prefix[0:39287]); the card/oracle/handoff value `fadf8a5e…` was correct, the dispatch's
  `fadf8e5e` was the typo.

### Erratum record (self-describing)

- File: `decision.md`, append-only; heading `## F erratum (landing)`; original 157 lines
  (D-0..D-7) retained byte-for-byte above this heading.
- sha256 before: `ab744fd38796d7fd00919dea3d2d12e9e14be1e9b36c6953daf529ec193643b1` /
  16478 B / 157 lines (== the value the reviewer re-hashed byte-for-byte in §2).
- sha256 after: recorded in handoff.json `bookkeeping.files_written` and
  `evidence/I-08-C-RESIDUAL/qualification.json` (computed after this append).
- This is the single sanctioned decision-record edit of the landing; no other original was
  modified.
