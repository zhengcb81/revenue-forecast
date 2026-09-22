# E1E7-ERRATA-LANDING review.md — CARRIER LANDING (verdict transcribed by the carrier-landing executor; the implementer did NOT sign)

Status: **`accepted_scoped`**. The independent reviewer wrote their verdict in
`reviewer_report.md` (the byte-pinned carrier), **not** in this file. This file is the
carrier-landing bookkeeping landing of that verdict: it transcribes the reviewer's verdict so
the attempt's `review.md` slot exists. **This is a pure bookkeeping transcription: it adds no
acceptance of its own.** Read `reviewer_report.md` itself for the reviewer's own words (§1–§4).
No verdict, review, or acceptance was authored in this pass.

`review.md` did not previously exist in this attempt (no implementer stub to preserve); this
file was created by the carrier-landing pass — not by the implementer and not by the reviewer.

## Verdict block (transcribed)

- Card: **E1E7-ERRATA-LANDING** (REM-18: E-1…E-7 编排层勘误 append-only 落地, no code, no tests)
- Attempt: `a20260921-01` (`<PLAN>\execution_runs\E1E7-ERRATA-LANDING\a20260921-01`)
- Verdict: **`accepted_scoped`** — the reviewer's literal label is written at
  `reviewer_report.md` **line 7**: `## Verdict: **accepted_scoped**`, restated in §4
  conclusion (**line 104**): "**accepted_scoped**：七项声明全部字节级复核通过……本报告**不代签**任何一项。"
- Verdict author: **独立复核** (independent review, 采样式复算 — reviewer_report.md line 3;
  boundary at line 5: the reviewer writes only `reviewer_report.md` + its sidecar, the four M-card
  `oracle.md` files stay read-only, no product writes, no self-signing of any M-card acceptance).
- Verdict round: round 1 of this card (single independent review round; the verdict is
  **scoped**, not clean — line 9: seven claims verified from bytes + 4 non-blocking minor
  observations + 5 explicitly unverified items).
- This pass **does not self-sign**: `implementer_signed: false`,
  `implementer_never_signs_acceptance: true`; the verdict is **transcribed, not authored**.

### Carrier (byte-pinned)

| field | value |
|---|---|
| carrier file | `reviewer_report.md` |
| path inside attempt | `reviewer_report.md` |
| sha256 | `fb05120a0f388b18d6d301b31fcd2edc4d86d047c675ca2ad2fe2c926e9444d5` |
| bytes | 10676 |
| lines | 104 (UTF-8 no BOM, LF-only, 0 CR, single trailing LF) |
| pin sidecar | `reviewer_report.sha256` (present; content `fb05120a…e9444d5  reviewer_report.md  bytes=10676`, 97 B, sha256 `367f22d7c3009a52ed04e0fbf20cb5f6591e4b31e40843955137472bd51c3363`) |
| verdict line | 7 |
| first line of verdict | `## Verdict: **accepted_scoped**` |
| verdict-line byte region | bytes 665..695 inclusive (31 B, without the LF), sha256 `b6787e111cf7249db03dd47bbc6cb4ddb40bfe89006d80338631b78d0969916f` |
| conclusion (§4) lines | 102–104 (region bytes 10229..10674 inclusive, 446 B, sha256 `4937770f9d1f4adabacc054cac320fe616298a9fd34a86b45dc99f17fb483169`) |
| scope / per-item section (§1) lines | 13–75 |
| findings section (§2) lines | 79–92 |
| unverified section (§3) lines | 94–100 |
| reviewer role / boundary lines | 3 / 5 |
| carrier region (whole file minus the single trailing LF) | bytes 0..10674 inclusive (10675 B), sha256 `4c1c36e05831b98880cd8e63ec8a90e239b1e0960eeb7ef45ba91f6db0584975` |
| producer | independent reviewer (独立复核), not the implementer |

Verification at landing time (read-only): file length = **10676 B** ✓, independent re-hash =
**fb05120a…e9444d5** ✓ equals both the sidecar value and the pinned value in the dispatch, and
the sidecar itself records `bytes=10676` ✓; verdict line 7 reads `accepted_scoped` ✓. No byte of
the carrier was changed by this landing pass: `reviewer_report.md` and `reviewer_report.sha256`
were read-only here (this pass wrote only `review.md`, `handoff.json`, and
`evidence/E1E7-ERRATA-LANDING/qualification.json`).

## Scope of the acceptance (transcribed from the reviewer's report)

Acceptance is **SCOPED, not clean**. Transcribed scope:

1. **4/4 M-card oracle append-only errata landings verified** (M05/M14/M20/M24): prefix proofs
   recomputed from bytes 4/4 (`sha256(after[:bytes_before])` == binding before-hash, binding
   self-consistent against the on-disk files); insertion-only proven 4/4 by full difflib
   (`{equal, insert}` only, zero replace/delete, insert size == after − before, landing after
   the frozen body); verbatim-source checks — **12/12 quoted fragments** hit the I-10-B source
   text (M14 E-5/E-6 focus: 10 ellipsis quotes + 2 English long quotes),
   **5/5 §5 table rows** (`row ⊆ landed`), **7/7 E-labels** verbatim in their cards' appended
   sections; source handoff pin 23563 B / `867d59b8…b54f4` ✓; landed_text equals the on-disk
   append slices byte-for-byte (differing only by the 1 leading LF separator).
2. **M05 pin-drift root cause independently reproduced** (C6, read-only): applying
   `LF→CRLF` restoration of the 54 CRs after byte 8774 to the pre-append prefix yields
   **14844 B / `7fda03b153fd9a3707fba3a1057c9eb2ed6d2f772cdd79b6c1a33de9bb639320`** — exactly
   the pin value; the 8774-B frozen body untouched. Zero-change discipline corroborated by
   mtime scan (only the 4 `oracle.md` files at the append instant) + `git diff` (C4).
3. **Parent's four rulings present** (C5, presence-only, not reopened):
   - **F2 → 留置** (date label; no second append round) — `decision.md` DEC-E1E7-5 +
     `evidence/provenance_time_note.json` + handoff GAP-1.
   - **GAP-2 → no-JSON** (no `evidence/**/*.json` edit pass) — `decision.md` DEC-E1E7-3 + handoff GAP-2.
   - **GAP-4 → 留置** (M05 LF disclosure stays in DEC-E1E7-1a, not inside the M05 card) —
     `decision.md` DEC-E1E7-1a + handoff GAP-4.
   - **GAP-5 → registered, not fixed** (I-10-B stale key name `errata_pending_orchestration` vs
     actual `errata_pending`; I-10-B handoff sha still `867d59b8…` ⇒ untouched) — handoff GAP-5.
4. **Non-promotion wording identical across all four cards** (C7): each appended section contains
   exactly the same 4 lines (intersection 4/4) — the `iso/rf/scripts/` … NOT promoted path
   declaration, 「修复未晋升：在晋升之前…仍然权威…until promotion」, the forward-looking disclosure
   「不改变任何现行期望、不改变任何 status、不改变任何资格」, and the subsection title line.

Not granted by the review (reviewer's own §3/§4): the five unverified items below stand as
declared; `disclosure_adaptation` stays **unmapped**, `accuracy` stays **unproven**; E-1…E-7 独立
验收、生产晋升、OQ-03 D/E 追认 remain with 独立 reviewer / 编排层 / owner — the report does not
代签 any of them.

## Carried findings (mirror summary; full records appended in `handoff.json.carried_findings`)

| id | class | summary | disposition |
|---|---|---|---|
| **CF-E1E7-1** (reviewer F-MIN-1, line 89) | pre-freeze wording inconsistency, non-blocking | binding/oracle say 「frozen before touching any M-card oracle」, but `commands.json` seq ordering shows reads (seq5/6/9) preceded the seq10 freeze ⇒ 「触碰」 true for modify, false for read. | Risk neutralized by the reviewer's independent before-image recompute (C1); pre-freeze wording clarification is an orchestration-layer T1-12 ① suggestion — this card cannot be rewritten. Carried, non-blocking. |
| **CF-E1E7-2** (reviewer F-MIN-2, line 90) | failure-handling wording differs | `decision.md` DEC-E1E7-2 writes 「回写原字节、STOP」 while this card's `oracle.md` §2.1 writes 「停止并保留原状（不回滚重试）」. | Moot — nothing failed (`stopped_or_skipped = {}`), no path triggered. Carried. |
| **CF-E1E7-3** (reviewer F-MIN-3, line 91) | expectation-annotation tension, awareness only | 行级「已过时，以本节为准」annotations land on expectation lines while the same section declares frozen values authoritative until promotion — inherent T1-12 ① tension. | Reconciled by the ④ disclaimer; orchestration-layer awareness only, not `changes_required`. Carried. |
| **CF-E1E7-4** (reviewer F-MIN-4, line 92) | date label | Appended-section label 2026-09-21 vs actual machine clock 2026-09-22 09:2x. | Already ruled **留置** by the parent (F2) and truthfully registered; not rewritten, no second round, **not reopened** here. Carried. |
| **U-1…U-5** (reviewer §3, lines 94–100) | explicitly unverified review boundary | U-1 pytest/mypy mtime attribution undecidable in a shared workspace (self-reported 0 pytest, not byte-provable); U-2 full `git status` aborted on an ACL-denied `.planning/.../scratch/model-tests/` dir (substitute: `git diff` + mtime scan); U-3 `commands.json` self-report has no independent cross-source, seq13 script not replayed; U-4 handoff frozen-body pin values (9367/13382/8774 B) not each traced back to the respective M-handoff bytes; U-5 M14 §3.4 cells not individually re-sourced. | Declared boundary, no inference substituted for conclusion. Carried unresolved by design. |
| **PARENT-RULINGS-4** | parent rulings recorded | no second append round for F2; no JSON edit pass (GAP-2); M05 LF disclosure stays in DEC-E1E7-1a (GAP-4); I-10-B stale key-name reference registered-not-fixed (GAP-5). | Present (C5 ✓); recorded here verbatim, none reopened, none re-adjudicated by this pass. |

## Not granted

`disclosure_adaptation` stays **unmapped**; `accuracy` stays **unproven**; no production write
authority is granted (0 production bytes written by this landing); the four M-card `oracle.md`
files and the sealed I-10-B attempt are untouched by this landing; E-1…E-7 acceptance,
production promotion, and OQ-03 D/E 追认 remain others' decisions.

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent), 2026-09-22.
- Status transition: `review_pending` → `accepted_scoped` (performed in `handoff.json` by this
  pass on the parent's dispatch; the verdict itself was authored only in `reviewer_report.md`
  line 7 by 独立复核 — never by the implementer and never by this file's author).
- `status_before_bookkeeping_fix: review_pending` recorded; `status_authority` added pointing at
  the carrier with line ranges, sha256 and byte proofs; stale implementer-era fields that
  asserted review-not-yet-done (`status_note`, `next_action`) preserved **byte-exact** under
  `*_historical_pre_verdict` keys and re-pointed at `status_authority`.
- `implementer_signed: false`; `implementer_never_signs_acceptance: true`;
  `verdict_is_transcribed_not_authored: true`.
- This pass wrote exactly three files: `review.md` (created, this file), `handoff.json`
  (status + status_before_bookkeeping_fix + status_authority + bookkeeping + carried_findings
  appended + the two stale-field supersessions; all other pre-existing keys untouched),
  `evidence/E1E7-ERRATA-LANDING/qualification.json` (created). Zero bytes written to
  `reviewer_report.md`, `reviewer_report.sha256`, any of the four M-card `oracle.md` files, any
  frozen/historical artifact, or production. Pre/post sha256 for every file this pass touched is
  reported to the parent (handoff.json pre-image: 11451 B / `c340891059baf1ae5f0a5ba6c0e99e9a3d090f71a8f010d02a3154c32ff55429`).
