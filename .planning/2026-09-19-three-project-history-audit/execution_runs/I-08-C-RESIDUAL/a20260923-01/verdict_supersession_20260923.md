# verdict_supersession_20260923.md — resolution of the `I-08-C/a20260919-01` original-attempt verdict state

- Date: 2026-09-23
- Author: I-08-C-RESIDUAL closure agent (delegated bookkeeping authority; NOT a reviewer,
  grants no acceptance)
- Written **inside this attempt** (`execution_runs/I-08-C-RESIDUAL/a20260923-01/`) and
  nowhere else. The original attempt is untouched: **before-hash of its `handoff.json`
  asserted unchanged** (below). 不改历史审计产物.

## 1. The state being resolved (dual-caliber)

`execution_runs/I-08-C/a20260919-01` carries two verdict calibers at once:

| carrier | line | text | author |
|---|---|---|---|
| `review.md` (round-1 review) | L9 | `## VERDICT: \`changes_required\`` | round-1 independent reviewer (sha256 `c1a8fd11b20f911c7407943dabe70bc493a9cb2959719c13beef21f8e7f1f2a3`, byte-prefix preserved) |
| `reviewer_report_r2.md` (round-2 re-review) | L10 | `## VERDICT: \`accepted_scoped\`` | round-2 independent reviewer (13285 B, sha256 `ee5046a5bafb8b75c3550d0abdb0520b337af894acb191302dd7c09a1179dc9a`, sidecar-matching) |

AUDIT-DESIGN read the first ("a20260919-01 = `changes_required`", report §3.1/§3.2(a));
AUDIT-GOAL read the second (`criterion1_eight_cards.md` row 4). The attempt's own
`handoff.json` already reconciles them (`status: accepted_scoped`, `status_history`
3 rounds, `reviewer_verdict_r1_superseded_by` field) but the round-1 headline line and
the HISTORICAL `verdict_summary` block still read `changes_required`, which is what the
audit compressed into 「原 attempt 双口径」.

## 2. Choice of handling option + authority

Dispatch options: **(i)** close-and-note as superseded-by-refreeze-chain with parent
ruling text; **(ii)** execute the reviewer's `changes_required` demands if still actionable.

**CHOSEN: (i)** — with the per-item finding (§3) that **(ii) has no remaining actionable
demand**: every round-1 demand ("What would close this card" (1)–(4)) was already executed
by the chain below and independently accepted at round 2, so re-execution would duplicate
evidence or touch history. Standing rule applied: closure-by-append/annotation + new
evidence, never rewriting old attempts.

**Authority cited:**

1. Owner ruling (parent ruling text, verbatim from `OWNER_DECISIONS.md` L365/L370):
   - 原话: 「A-1: b（允许修 prune 代码，不授权执行 prune） **A-2: 批准** B: a（提高门超时到 1200，立卡红绿） C: 先推已收口的 4 张，B1/B3/I-14-D 攒第二批 D-G1: a D-G2: 留置/（或给取舍） E-1: 150/60 E-2: 重跑 E-3: 立卡 E-4: 维持暂不签」
   - ruling row: 「**A-2 批准** | I-08-C oracle 追加式重冻（E11/E13 由"缺口在册"翻转为"攻击必拒"），**收口归其 reviewer** | 与建议一致 | 已派 `I-08-C` refreeze 卡」
   - (OWNER_DECISIONS.md sha256 at this card's freeze = `4bed42c685579fb114ade92c4a63192af4c84db9933b8b24329e2f1e88f7c083`.)
2. The closure authority the ruling names (「收口归其 reviewer」) = the round-2 carrier
   verdict `accepted_scoped` (`reviewer_report_r2.md`), transcribed-not-authored into
   `handoff.json` (`status_authority` block).
3. Parent bookkeeping dispatch: `REMEDIATION_REGISTER.md` §74 —
   「I-08-C-RESIDUAL 收口卡已排（3 遗留+原 attempt 双口径处置）」 (register sha256 at
   freeze `535152f0fd7bd44b5fe830d416bf8e6ee8ecd744d99c464f94d2f7849c17a088`).

## 3. The actual supersession chain (measured from the attempts' handoffs/reports)

The dispatch's tentative "the refreeze chain = B1-I08C → I-14-D r7?" is **corrected:
I-14-D r6/r7 is a different chain** (closes REM-04/REM-81 on the I-14-D track). The
I-08-C refreeze chain is:

1. `I-08-C/a20260919-01/review.md` round 1 = `changes_required` + four demands
   (1) bind attestation at consumption (F1), (2) bind `segments[i].base_revenue` (F3),
   (3) document/deprecate `validate_publication_receipt` (F2), (4) re-freeze the oracle
   (E4 implemented/withdrawn) + preserve the exploratory run log.
2. Demands (1)–(3) → **`B1-I08C-product-fixes/a20260921-01`** (its `handoff.json`
   `parent_card: "I-08 (via the I-08-C changes_required verdict)"`; fixes in
   `iso/fixed/rf`) → independent review **`accepted_with_conditions`** (2026-09-21,
   `reviewer_report.md`, conditions F1–F7).
3. Conditions F1–F5 → **`B1-PREREQ/a20260922-01`** (SRC oracle r5/r6/r7 append-only;
   R13-equivalent node; E21 probe; evidence protocol) → its round-2 review
   `accepted_scoped` (`50437289…`) → parent closed REM-40…44 (register §28).
4. Demand (4) + the refreeze proper → fix round **FIX-I08C-REFREEZE-1** *inside*
   `I-08-C/a20260919-01`: append-only oracle **revision r4** (prefix proofs
   `[0:22335]=94a853e9…`, `[0:6831]=478bd70e…`), E11/E13 gap pins flipped to
   attack-must-be-rejected under owner A-2; 13-node suite re-evidenced (RUN-A 13/13 on
   B1's fixed tree; RUN-B/B2/M exactly {e11,e13} red = anti-vacuity) → round-2 re-review
   **`reviewer_report_r2.md` = `accepted_scoped`**, scope = "verification/evidence + the
   append-only oracle re-freeze (revision r4) + round-1 items (1)–(3) as implemented in
   B1's ISOLATED tree, behaviorally re-verified".
5. Product side, separate owner decision: owner 「B: 全批」 (OWNER_DECISIONS.md L420/L426,
   父保留各仓提交权) → PROMOTION-PREP/PROMOTION-EXEC promoted the three fixed files;
   production now carries `bc2bb4a3…`/`8a761498…`/`212f0059…` (re-measured this card,
   `evidence/c11_production_state.json`).

Per-item state of the round-1 demands at supersession time:

| round-1 demand | executed by | independently accepted | residual carried |
|---|---|---|---|
| (1) bind attestation at consumption + fix `attestation_capability()` | B1 REM-01(a)(b), then promoted | B1 review CONFIRMED + round-2 RUN-A re-verified | invest-* consumers unverified (INVEST-CORE card) |
| (2) bind `segments[i].base_revenue` | B1 REM-03 (two gates G-A/G-B), then promoted | B1 review CONFIRMED (original exploit dead at 3 entry points) | §3.2 input-re-anchoring residual (accepted-by-design) |
| (3) document/deprecate `validate_publication_receipt` | B1 REM-02 (docstring + marker, no behaviour change per frozen decision) | B1 review CONFIRMED as implemented | F7 caller trap OPEN — "documented limitation, consumer-side guardrail not yet in place" + (a)+(c) decided (this attempt, AX-3) |
| (4) re-freeze oracle + preserve exploratory log | r3 (E4 implemented as DF-1/DF-3, exploratory inventory DF-2) + fix round r4 (E11/E13 re-freeze) | round-2 `accepted_scoped` | none |

⇒ **Supersession statement (this document is its dated carrier):** the round-1
`changes_required` state of `I-08-C/a20260919-01` is **SUPERSEDED — close-and-note** by
the chain above and by the round-2 carrier verdict `accepted_scoped` (authority:
「收口归其 reviewer」, owner A-2). The round-1 verdict text remains on record, byte-untouched,
as the historical verdict of the r3 package at 2026-09-21; it is not the current state.
Current state of the attempt for all counting purposes: **`accepted_scoped` (round-2
carrier), scope-limited exactly as that carrier's "Explicitly OUT of the accepted scope"**
(no re-widening here: production promotion — since performed separately by owner
「B: 全批」; F2/F4 as carried; invest-* consumers; CLI transactions;
`disclosure_adaptation = unmapped`, `accuracy = unproven`).

## 4. Untouched-old-attempt assertion (before/after hashes)

Command pair: `I08CR-c0` (before) / `I08CR-c12` (after + comparison),
`evidence/manifests_before.json` → `evidence/manifests_after.json` +
`evidence/manifests_comparison.json` (sha256 of every file, all three referenced attempts).

| tree | before → after |
|---|---|
| **`I-08-C/a20260919-01` (the original attempt)** | 73 files → 73 files; **added 0 / removed 0 / content-changed 0 / mtime-changed 0** |
| **`I-08-C/a20260919-01/handoff.json` (explicit assertion demanded by dispatch)** | sha256 `b83e04a670d464343816e978c102dab269dadc79aef2b9842d9d0c505ef82f12` / 58814 B / mtime_ns 1790067548253599400 **= before = after (UNCHANGED, asserted)** |
| `B1-PREREQ/a20260922-01` | 298 → 298 files; 0 added / 0 removed / 0 changed |
| `B1-I08C-product-fixes/a20260921-01` | 2763 → 2765 files: **`review.md` and `evidence_erratum_20260923.md` ADDED, `handoff.json` CHANGED — NOT by this card** (see concurrency note) |

**Concurrency note (honest, measured):** during this card's run window a sibling
bookkeeping session (BOOKKEEP-REPAIR / a20260923-01, parent dispatch #15 — its files say
so verbatim) performed the B1 carrier landing in the `B1-I08C-product-fixes` tree:
`review.md` (7581 B, mtime 2026-09-23 22:56:31 — the D4 missing review slot,
transcription-only), `handoff.json` status-flip bookkeeping (22:56:32; `status` is now
`"accepted_with_conditions"`), and `evidence_erratum_20260923.md` (3886 B, 23:04:27 —
the D1b erratum, same disposition as this attempt's AX-5 record). None of this card's 13
commands has any of those paths in its argv or write roots (every raw output of this card
is under `<ATTEMPT>/evidence/**` or `%TEMP%\I08C-RESIDUAL-a20260923-01\**`; see
`commands.json`); the additions are attributed to the sibling session by content authorship
("BOOKKEEP-REPAIR / a20260923-01（父派单 #15）") and timestamp. The demanded assertion —
the ORIGINAL ATTEMPT `I-08-C/a20260919-01` untouched, its `handoff.json` hash unchanged —
holds strictly; the B1 change is external to this card and is reported, never repaired or
re-attributed.

## 5. What this supersession does NOT do

- It grants no acceptance of its own (`implementer_signed: false`; acceptance is and stays
  the round-2 reviewer's).
- It re-opens nothing, rewrites nothing, and widens no scope (the carrier's
  out-of-scope list survives verbatim).
- It does not extend I-08-C coverage to invest-* cross-repo consumers (unverified;
  INVEST-CORE card owns that site).
