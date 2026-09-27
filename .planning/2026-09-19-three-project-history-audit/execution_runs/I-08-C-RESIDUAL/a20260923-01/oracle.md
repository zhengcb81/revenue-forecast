# I-08-C-RESIDUAL — oracle.md (FROZEN 2026-09-23, before any judged run of this attempt)

- Plan: `2026-09-19-three-project-history-audit`
- Card: **I-08-C-RESIDUAL** — close the residuals keeping goal item ① (8 in-flight cards) short of 8/8
  (AUDIT-DESIGN finding 「I-08-C oracle 重冻未收口」 — 7/8 closed, I-08-C partial)
- Attempt: `execution_runs/I-08-C-RESIDUAL/a20260923-01`
- Freeze discipline: this file is frozen BEFORE any judged run. Later corrections are
  append-only revisions (`## Revision r2` markers), never edits to frozen bytes.
- Roles: implementer = this closure agent (never self-signs `accepted`); independent
  reviewer = to be assigned (handoff requests one).

## 0. Standing rules for this card (frozen)

1. **Every referenced attempt is READ-ONLY.** `I-08-C/a20260919-01/**`,
   `B1-I08C-product-fixes/a20260921-01/**`, `B1-PREREQ/**`, `I-14-D/**`,
   `PROMOTION-*/**`, `AUDIT-*/**` and every other `execution_runs/**` tree: zero
   writes, zero deletes, zero renames. 不改历史审计产物.
2. **Closure-by-append/annotation + new evidence only.** All closure artifacts land as
   NEW files inside THIS attempt. No historical attempt file is rewritten to make a
   state look closed.
3. **Production (RF/CW/FF repos) zero-write** (goal discipline ⑤ 「生产零合并」; every
   prior card held `git status --porcelain -- scripts/ tests/ config/ artifacts/` empty).
   If a leftover demands a product/test fix, this card lands the exact ready-to-apply
   patch as a NEW file here and routes it to the parent's production batch
   (OWNER_DECISIONS.md:426 「父保留各仓提交权」) — it is NOT applied in place by this card.
4. **Judged-run raw goes to `<ATTEMPT>/evidence/`** (register §72 evidence-retention
   rule); `%TEMP%` is scratch only. Old attempts' scripts with embedded absolute output
   paths are NEVER executed (AUDIT-DESIGN §0 incident; `review_and_handoff.md:33`).
5. Probe/check logic executed here is authored in this attempt and bound to current
   bytes; expectations below were frozen before running them.

## 1. The acceptance's conditions block — VERBATIM

Source (sole authority): `execution_runs/B1-I08C-product-fixes/a20260921-01/reviewer_report.md`
(the `accepted_with_conditions` carrier; byte pin recorded in `reviewer/report_pin.json`,
`REPORT_SHA256: 73feb0593b44ffeb448bc5f5b1cea9800f4cc9fb59f40ca19e9aae8038c104fa`).

### 1.1 VERDICT block (reviewer_report.md L14–18) — the conditions attached to the acceptance

> ## VERDICT
>
> **`accepted_with_conditions` — the card's security claims are CONFIRMED; three
> non-security documentation defects and two evidence-completeness defects are
> recorded below and must be closed before/at promotion.**

### 1.2 Severity map (reviewer_report.md L319–321)

> Severity: **F1/F2 = documentation/evidence defects (block promotion until
> corrected); F3–F5 = bookkeeping; F6 = disclosed residual (no action required);
> F7 = adjudicated decision with a residual to track.**

### 1.3 The required-closure list (reviewer_report.md §9, L536–553) — verbatim items 1–6

> 1. **F1** — append oracle revision r5 correcting the §R3-2/R3-3 field-count text
>    to 10 fields and explaining that `result_sha256` is carried in the *request*
>    only, pinned to the sentinel. Append-only: r1–r4 bytes untouched.
> 2. **F2** — add the "present record is verified even when the label is
>    `unattested`" node (an R13 equivalent) to the card's test file, and add the
>    corresponding mutation (M6) to the mutation table. Without it the card's own
>    proof set does not measure a clause its oracle freezes.
> 3. **F3** — either implement E21 (`issuer`/`key_id` vs the resolved trust entry)
>    or delete the E21 claim from the docstring and list it under "not closed".
> 4. **F7** — record REM-02 as a documented limitation with the caller-side trap
>    still open, and decide (a)/(b)/(c). Do not describe REM-02 as fully closed
>    while the only runtime artefact is a class nobody raises.
> 5. **F4/F5** — preserve raw run outputs under distinct labels, and give
>    `decision.md` a freeze-time hash, in the next attempt's protocol.
> 6. Only then: the owner decides on promoting the three files from
>    `iso/fixed/rf/scripts/`.

### 1.4 The finding bodies — verbatim condition text of the three leftovers

**L1 = F1 (reviewer_report.md §6 F1, L323–353; key sentences):**

> ### F1 (MEDIUM, documentation) — the frozen artifact contradicts itself on the attestation field count
>
> `oracle.md` Revision r3 R3-2 says the record set is **11 fields** and explicitly
> keeps `result_sha256` … The delivered artifact has **10** fields: `result_sha256` is
> *absent* from the record, and instead the request's `result_sha256` is pinned to
> `SIGNED_RESULT_SHA256_SENTINEL = "0"*64` so the signed object is reconstructible. …
> **The implementer's claim to me ("closed 10-field set") is accurate; the frozen
> oracle's revision prose is wrong.** Correct `oracle.md` with a further append-only
> revision (r5) — do not edit r1–r4 bytes.

**L2 = F2 (reviewer_report.md §6 F2, L355–363):**

> ### F2 (MEDIUM, evidence) — the frozen proof set cannot see the "present record is ignored" regression
>
> Demonstrated in §2.4: M6 (label-gated short-circuit) leaves the frozen 12-node
> file at **12/12 PASS** while disabling verification of any record carried by an
> `unattested`-labelled receipt. The implementation is correct today (my R13 passes
> on the fixed tree and fails on M6), but the card's own proof set does not measure
> the clause the oracle's §3.1 freezes ("a record that does not verify must never be
> present-but-ignored"). Recommendation: fold a node equivalent to R13 into the
> card's test file, and add M6 to the mutation table.

**L3 = F3 (reviewer_report.md §6 F3, L365–384; key sentences):**

> ### F3 (LOW, documentation) — a rejection code is documented but never raised
>
> `validate_publication_attestation`'s docstring lists
> `issuer_key_binding_mismatch (E21)` and the oracle freezes E21 as "`issuer` != the
> trust-domain entry's `issuer`, or `key_id` mismatch". No E21 is raised anywhere …
> Report it as a documentation-vs-behaviour mismatch: either implement E21 (compare
> the record's `issuer`/`key_id` with the trust entry it resolved), or delete the
> claim from the docstring and record E21 as not-closed in §7.

## 2. Identification of "the 3 遗留" (leftover conditions) — FROZEN reading

The conditions block partitions its five "must be closed before/at promotion" defects
(F1–F5) exactly as its own words say: **three non-security defects = F1, F2, F3**
(the three finding bodies quoted in §1.4, and §9 items 1–3 — "Required before
promotion (in order)") and **two evidence-completeness defects = F4, F5** (§9 item 5
is literally evidence-preservation protocol: "preserve raw run outputs under distinct
labels, and give `decision.md` a freeze-time hash"). F6 ("No action required") and F7
("a residual to track") are by their own text NOT in the must-close set.

⇒ **The 3 leftovers closed by this card = L1(F1), L2(F2), L3(F3)** — verbatim text in §1.4.

**Honest disclosure of alternate parsings (no silent drop either way):** the report's
per-finding severity labels ("documentation"/"evidence"/"pre-registration") do not
partition 3+2 as neatly as the verdict sentence (only F1/F3 carry a "documentation"
label; F2/F4 carry "evidence"; F5 is "pre-registration"). Under any alternate reading
(e.g. {F1,F3,F5}+{F2,F4}, or the three blocks literally labelled "Residual" = §3.2/F6/F7),
every member is still disposed with fresh evidence in this attempt:
`decision.md` per-residual table rows F1–F7 + §3.2-residual + AUDIT-DESIGN D1b, where
L1/L2/L3 are the three primary closures and F4/F5/F6/F7/§3.2/D1b are annex closures
AX-1..AX-5. A reviewer or the parent that counts a different trio still finds all of
them closed here.

## 3. Per-residual expectations + closure evidence to produce (FROZEN before runs)

### 2.1 / L1 support — corrected source-of-truth (re-frozen here)

The attestation record's **closed, exact 10-field set** (this is the corrected
source-of-truth statement the r3 prose got wrong):

```
{ algorithm, attestation_payload_schema_version, domain_separator, fingerprint,
  issuer, key_id, payload_sha256, request_id, signature, signed_at }
```

- `receipt_sha256` is NOT a record field (fixpoint: a receipt cannot contain its own
  hash; `result_sha256` covers the receipt which contains the record).
- `result_sha256` is NOT a record field; it is carried in the signed **request** only,
  pinned to `SIGNED_RESULT_SHA256_SENTINEL = "0"*64` so the signed object is
  reconstructible (provably cannot bind the live result digest — see AX-2/F6).
- Invariant: `set(record) == PUBLICATION_ATTESTATION_FIELDS` (closed set, exact).

### 3.1 L1 (F1) — closure evidence expected

| id | check (frozen expectation) |
|---|---|
| E-L1.1 | B1 `oracle.md` prefix hashes MATCH: `[0:27697]`=`81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281`, `[0:31081]`=`60ecbca7a008d60b8634bfed1cec56b801a86e6486f639c54e19cd257867f1d4`, `[0:35840]`=`231e79768bd71ce95730ed10539d1e5865caa659c0dccf942bf7f2b99d8e3523`, `[0:39287]`=`fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae`; markers `## Revision r5` at byte 39288, `## Revision r6` at 43299, `## Revision r7` at 47539 (each exactly once); total 57911 bytes |
| E-L1.2 | the r5+ region states the corrected 10-field record, the `receipt_sha256` removal and the `result_sha256`-in-request sentinel rule (text-level presence) |
| E-L1.3 | three-way field-count measurement on CURRENT bytes (production `scripts/revenue_publication.py` = post-promotion fixed bytes, and B1 `iso/fixed/rf` copy): (a) AST literal `PUBLICATION_ATTESTATION_FIELDS` has exactly the 10 members of §2.1; (b) the frozen test's `ATTESTATION_FIELDS` mirrors the same 10; (c) runtime import of the module yields `len(PUBLICATION_ATTESTATION_FIELDS) == 10` |

### 3.2 L2 (F2) — closure evidence expected

| id | check (frozen expectation) |
|---|---|
| E-L2.1 | the card's proof set now CONTAINS an R13-equivalent node ("a present record is verified even when the label is `unattested`") and the mutation table CONTAINS M6 (grep-level presence + node id captured) |
| E-L2.2 | fresh judged run on a %TEMP% copy of B1 `iso/fixed/rf`: `test_b1_rem.py` frozen set + the R13-equivalent node all PASS |
| E-L2.3 | fresh judged run of the same node set on the reviewer's M6 mutant tree (copied from `reviewer/scratch/mutations/M6/rf`, read-only source): the R13-equivalent node FAILS (RED) while the positive control PASSES — i.e. the added node is load-bearing against exactly the regression F2 names |

### 3.3 L3 (F3) — closure evidence expected

| id | check (frozen expectation) |
|---|---|
| E-L3.1 | static scan: `issuer_key_binding_mismatch`/`E21` occurrences in production + B1 fixed tree enumerated exactly (expected: documented in the `validate_publication_attestation` docstring, raised NOWHERE); `issuer`/`key_id` are NOT members of the signed canonical request field set |
| E-L3.2 | trust loader shape: `contracts/evidence._trusted_signer_public_keys()` resolves fingerprint → public key with NO `issuer`/`key_id` fields ⇒ E21 as specified is not implementable against the current trust schema without a cap change (the 12-field trust-entry schema = I-08-A E25, recorded NOT implemented) ⇒ option (a) = BLOCKED-on-cap-change |
| E-L3.3 | option (b) executed to the limit of this card's authority: (i) E21 recorded as **not-closed** in a dated record in this attempt (this is the "list it under not closed" demand); (ii) the exact docstring-deletion patch P-L3 landed as a NEW file in this attempt, ready to apply — application is a production write routed to the parent's batch (rule 0.3), never applied here |

### 3.4 Annex closures (frozen expectations)

| id | item | closure evidence expected |
|---|---|---|
| AX-1 | F4/F5 evidence-completeness pair | status annotation + fresh checks: the surviving `before/b1_unfixed.stdout.txt` decodes to the r1 RED run "10 failed, 2 passed" (register §22/补1 erratum: the "unrecoverable" claim was false); B1-PREREQ evidence protocol (distinct raw labels, SUMS) + 24-entry hash freeze chain head verified; F5's "freeze-time hash" protocol applied by this attempt (binding.json pins every deliverable hash at handoff) |
| AX-2 | F6 disclosed residual | dated permanent-limitation record incl. the F6-clarification (rewrite+consistent-recompute ⇒ both ACCEPTED [original]; rewrite without recompute ⇒ receipt ACCEPTED / forecast REJECTED [strengthening]); no action, per "No action required" |
| AX-3 | F7 adjudication residual | REM-02 recorded VERBATIM as "documented limitation, consumer-side guardrail not yet in place" (never "closed"); decision (a)/(b)/(c) = **(a) `publication_receipt.receipt_schema_version` bump + a follow-up rename/deprecate item**, per the reviewer's own recommendation ("(a) plus a follow-up item"); (b) rejected with reason (would break `test_zr701`/`test_zr705` clean-run assertions; oracle r1 §3.5(c) froze no-runtime-warning); (c) folded in as the follow-up item; implementation = product-track (contract change ⇒ professional review per START_HERE §边界), guardrail remains NOT in place — tracked |
| AX-4 | §3.2 residual (input-document re-anchoring) | dated record: accepted-by-design limitation of the pre-existing input-binding contract (`validate_published_forecast(result, original_input)` / `verify_input_binding` reject it); explicitly "not a defect of this card"; no action |
| AX-5 | AUDIT-DESIGN D1b/D1c (B1 evidence-entry naming) | append-only erratum record: `commands.json` evidence entry `before/production_anchors.txt` was NEVER produced (only the `.json` sibling exists — re-verified by fs-scan); recorded as "未产出（仅 .json）", per AUDIT-DESIGN addendum A4 disposition; the missing file is NOT fabricated after the fact |

## 4. Original-attempt state resolution — FROZEN handling rule

Target: `I-08-C/a20260919-01` round-1 verdict state (`review.md:9` `## VERDICT: \`changes_required\``)
vs the round-2 carrier (`reviewer_report_r2.md:10` `## VERDICT: \`accepted_scoped\``) — a
dual-caliber state that AUDIT-DESIGN read as "a20260919-01 = changes_required".

**Options given by dispatch:** (i) close-and-note as superseded-by-refreeze-chain with
parent ruling text; (ii) execute the reviewer's `changes_required` demands if still actionable.

**CHOSEN (frozen): (i), with a per-item finding that (ii) has no remaining actionable
demand** — every round-1 demand was already executed by the chain below and independently
accepted; re-executing anything would either duplicate evidence or rewrite history.
The supersession is recorded by dated `verdict_supersession_20260923.md` INSIDE THIS
ATTEMPT (never inside the old attempt), asserting the before-hash of
`I-08-C/a20260919-01/handoff.json` unchanged.

**The refreeze chain (measured from the attempts' own handoffs/reports — NOT via I-14-D r7):**

1. `I-08-C/a20260919-01/review.md` round 1 = `changes_required` (sha256 `c1a8fd11…`),
   demands "What would close this card" (1) bind attestation at consumption (F1),
   (2) bind `segments[i].base_revenue` (F3), (3) document/deprecate
   `validate_publication_receipt` (F2), (4) re-freeze the oracle (E4 implemented or
   withdrawn) + preserve the exploratory run log.
2. Demands (1)–(3) = product fixes → **B1-I08C-product-fixes/a20260921-01** (fixes in
   `iso/fixed/rf`; its `handoff.json` `parent_card: "I-08 (via the I-08-C changes_required
   verdict)"`, `execution_gate.source_findings` = the round-1 review) → independent review
   `accepted_with_conditions` (2026-09-21) with conditions F1–F7.
3. B1's acceptance conditions F1–F5 → **B1-PREREQ/a20260922-01** (SRC oracle r5/r6/r7
   appended; R13 node; E21 probe; evidence protocol) → second review `accepted_scoped`
   (`50437289…`) → parent closed REM-40…44 (register §28).
4. Demand (4) + the refreeze proper → fix round **FIX-I08C-REFREEZE-1** inside
   `I-08-C/a20260919-01` (append-only oracle **revision r4**; E11/E13 gap pins flipped to
   attack-must-be-rejected under owner **A-2 「批准」** — ruling row
   「A-2 批准 | I-08-C oracle 追加式重冻（E11/E13 由"缺口在册"翻转为"攻击必拒"），收口归其 reviewer」,
   OWNER_DECISIONS.md L365/L370) → round-2 independent re-review
   **`reviewer_report_r2.md` = `accepted_scoped`** (13285 B, sha256 `ee5046a5…`, sidecar-matching),
   scope = "verification/evidence + the append-only oracle re-freeze (revision r4) + round-1
   items (1)–(3) as implemented in B1's ISOLATED tree".
5. Promotion of the three fixed files = separate owner decision → owner 「B: 全批」
   (OWNER_DECISIONS.md L420/L426) → PROMOTION-PREP/PROMOTION-EXEC; production now carries
   the fixed bytes (re-measured by this card).

**NOT part of this chain:** `I-14-D` r6/r7 (that chain closes REM-04/REM-81 on the I-14-D
track). The dispatch's tentative "B1-I08C → I-14-D r7?" is corrected to the chain above.

**Authority citation for the supersession:** (a) owner A-2 ruling (above, incl.
「收口归其 reviewer」); (b) the round-2 carrier verdict `accepted_scoped` (reviewer-owned,
implementer-transcribed only — `I-08-C` handoff `status_authority` block); (c) parent
bookkeeping dispatch `REMEDIATION_REGISTER.md` §74 「I-08-C-RESIDUAL 收口卡已排
（3 遗留+原 attempt 双口径处置）」 (register sha256 `535152f0fd7bd44b5fe830d416bf8e6ee8ecd744d99c464f94d2f7849c17a088` at freeze).

## 5. Run contract (all raw output → `<ATTEMPT>/evidence/`; scratch in `%TEMP%`)

| id | command intent | frozen expected result |
|---|---|---|
| I08CR-c0 | before-hash manifests of `I-08-C/a20260919-01/**` and `B1-I08C-product-fixes/a20260921-01/**` (sha256 every file) | manifests written to evidence; `handoff.json` before-hash captured |
| I08CR-c1 | E-L1.1/L1.2 oracle prefix + marker + corrected-text check | all values as §3.1 |
| I08CR-c2 | E-L1.3 three-way field-count check (AST×2 + runtime on %TEMP% copies) | 10 / 10 / 10, sets == §2.1 |
| I08CR-c3 | E-L2.1 presence check (R13-equivalent node + M6 row) | both present |
| I08CR-c4 | E-L2.2 pytest frozen 12-node + R13 nodes on %TEMP% fixed copy | all PASS, rc 0 |
| I08CR-c5 | E-L2.3 same node set on %TEMP% M6 mutant copy | R13 node FAILS, control PASSES, rc 1 |
| I08CR-c6 | E-L3.1 static E21 scan + signed-request field membership | exactly as §3.3 |
| I08CR-c7 | E-L3.2 trust-loader shape probe | fingerprint→key map only, no issuer/key_id |
| I08CR-c8 | AX-1 r1 stdout decode check + freeze-chain/SUMS presence | "10 failed, 2 passed" decoded; chain/SUMS present |
| I08CR-c9 | AX-3 REM-02 state check (docstring phrases, marker exported, marker never raised; zr701/zr705 clean-run assertions located) | exactly as §3.4 |
| I08CR-c10 | AX-5 D1b fs-scan (`before/production_anchors.txt`) | ABSENT (confirming the erratum) |
| I08CR-c11 | production anchor re-check + git porcelain | production = promoted fixed bytes; porcelain clean (zero production writes by this card) |
| I08CR-c12 | after-hash manifests of both old attempts | byte-identical to c0 manifests (untouched-old-attempt assertion) |

Any deviation from a frozen expectation is REPORTED AS MEASURED, never adjusted;
no expected value is edited after the fact. Two identical failures stop the check
(no blind retry).

## 6. Counting basis (frozen criteria for the goal-item counting statement)

Goal item ① (owner goal rev. 4: 「8 在飞卡收口」) counts its slot
**「I-08-C oracle 重冻」= CLOSED** iff all of:

- (a) the oracle re-freeze exists append-only and was independently accepted:
  FIX-I08C-REFREEZE-1 oracle revision r4 (prefix `94a853e9…` / `478bd70e…` proofs) +
  carrier `reviewer_report_r2.md` `accepted_scoped` (pin re-verified here);
- (b) the 3 leftovers L1/L2/L3 are closed with the evidence their condition texts demand
  (§3.1–§3.3 all present);
- (c) the original-attempt state is resolved by dated supersession with the old handoff's
  before-hash asserted unchanged (§4);
- (d) no other acceptance finding is silently dropped: F4–F7, §3.2-residual and D1b each
  carry an explicit disposition (AX-1..AX-5).

"Closed" here means precisely: **the card's deliverable-side obligations (refreeze +
re-review acceptance) are complete and every condition attached to the acceptance is
either discharged with evidence or recorded at its demanded terminal label (permanent
limitation / not-closed / tracked residual), with all remaining product-side items
(E21 implementation, REM-02 guardrail (a), promotion-side patch P-L3 application)
explicitly routed on named tracks — it does NOT mean the product defect surface is
empty, does not extend to invest-* cross-repo consumers (unverified, owned by
INVEST-CORE), and grants no qualification beyond this card's scope.**

## 7. STOP / BLOCKED rules

- A leftover whose demand requires a capability/contract change outside this card
  (E21 implementation ⇒ trust-schema cap change; REM-02 (a) ⇒ receipt schema bump) is
  **stopped at its honest label** (BLOCKED-on-cap-change / tracked-residual) with
  evidence — never papered over.
- A product edit demanded by a leftover but forbidden by goal discipline ⑤ is landed as
  patch + routing (rule 0.3), not applied.
- Any mismatch found between a frozen expectation and measurement is reported verbatim;
  if it undermines a counting criterion, the counting statement says so.
