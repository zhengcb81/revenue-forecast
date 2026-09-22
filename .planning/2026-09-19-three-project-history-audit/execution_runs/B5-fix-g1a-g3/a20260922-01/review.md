# B5-fix-g1a-g3 review.md — CARRIER LANDING (verdict transcribed by the carrier-landing executor; the implementer did NOT sign)

Status: **`accepted_scoped`**. The independent reviewer wrote their verdict in
`reviewer_report.md` (the byte-pinned carrier), **not** in this file. This file is the
carrier-landing bookkeeping landing of that verdict: it transcribes the reviewer's verdict so
the attempt's `review.md` slot exists. **It is a pure bookkeeping transcription: it is not a
signature, and it adds no acceptance of its own.** Read `reviewer_report.md` itself for the
reviewer's own words (§1–§10). No verdict, review, or acceptance was authored in this pass.

`review.md` did not previously exist in this attempt (no implementer stub to preserve); this
file was created by the carrier-landing pass — not by the implementer and not by the reviewer.

## Verdict block (transcribed)

- Card: **B5-fix-g1a-g3** (fix card closing B5's BLOCKING findings F-1 (G3 both-keys) and
  F-2 (G1-a routing) + F-3..F-7)
- Attempt: `a20260922-01` (`<PLAN>\execution_runs\B5-fix-g1a-g3\a20260922-01`)
- Verdict: **`accepted_scoped`** — the reviewer's literal label is
  **`accepted_scoped`** (`reviewer_report.md` line 4: `- **Verdict**: **\`accepted_scoped\`**`;
  status recommendation repeated at line 122: "`status` recommendation: `accepted_scoped` —
  move out of `review_pending` only by the parent/owner, not by the implementer.")
- Verdict author: **独立复核** — an independent reviewer session (sibling of the
  implementer; the implementer did not self-sign; the reviewer's report states it is one of
  their only two writes, `reviewer_report.md` line 3).
- Verdict round: round 1 of this card (single independent review round; the verdict is
  **scoped**, not clean).

### Carrier (byte-pinned)

| field | value |
|---|---|
| carrier file | `reviewer_report.md` |
| path inside attempt | `reviewer_report.md` |
| sha256 | `69ea3b033d2278977b6956b953e1f9113dc45c0ee5da0fd72fa4e8a81620130e` |
| bytes | 16710 |
| lines | 122 (LF-only, no BOM, single trailing LF) |
| pin sidecar | `reviewer_report.md.sha256` (present; content `69ea3b03…20130e  reviewer_report.md`, 85 B, sha256 `f15f60eaf40f8a9b857563e8564a0657cd88fd43528a34c7a94ba4938ec73a0b`) |
| verdict line | 4 |
| first line of verdict | ``- **Verdict**: **`accepted_scoped`**`` |
| verdict-line byte region | bytes 232..267 inclusive (36 B, without the LF), sha256 `193fab116c4e3e422f240a78183b0d48f5df4e65fdaf24a4e450b1a4c0092a82` |
| status-recommendation line | 122 (byte region 16354..16708 inclusive, 355 B, sha256 `bd22a92ec25017602f7b91f19fb2a4e3e35c509a2de233dcb08277dee473a03f`) |
| findings section (§9) lines | 99–109 |
| unverified/not-covered section (§10) lines | 111–118 |
| finding ⑤ adjudication (§7) lines | 72–85 |
| carrier region (whole file minus the single trailing LF) | bytes 0..16708 inclusive (16709 B), sha256 `d5f908edc97ac24559e60571091754c079fd4d9da2adedf6c8d2ca83bd2ea940` |
| producer | independent reviewer (独立复核), not the implementer |

No byte of the carrier was changed by this landing pass: `reviewer_report.md` and its
`.sha256` sidecar were read-only here (this pass wrote only `review.md`, `handoff.json`, and
`evidence/B5-fix/qualification.json`).

## Scope of the acceptance (transcribed from the reviewer's report)

Acceptance is **SCOPED, not clean**. The reviewer's scope was sampled from-scratch
re-execution and targeted reads on their own copies (33 fresh child processes): full M25-M28
arm re-run (20/20 raw rcs match: E=0, F=3, G=2 `no_verdict`, S=1, B=1) proving the G1-a
three-way routing load-bearing; independent G3 reader-expression re-eval proving the F-1 break
reproduced on B5's output and closed on this card's output; a 896-hit precedence grep proving
zero affirmative precedence assertions (G2 stays 留置); F-3 arm parse on all 8 batch
evidence files; F-7 append proof fields; boundary spot-checks (5/5 frozen cases, 2/2 runner
byte-identity pairs, production anchors, `git status` 0 lines over M01..M31, 0 B5-attempt
writes, all 17 recomputed card pins OK); and fresh M01-M04 measurement confirming the 27/31
scope-wording correction.

Explicitly **not** granted / not verified by the review (reviewer's §10): arm values on the
six authorized batches beyond what was sampled were read, not re-executed; frozen `cases.json`
beyond 5/31 sampled; the 68-runner census beyond 2 pairs; `verify_append_fixed.py` /
`verify_boundaries.py` not re-run; chain-proof prefixes PRE/POST1 accepted from the record;
no exhaustive static rc-literal audit; `disclosure_adaptation` stays **unmapped**, `accuracy`
stays **unproven**; no production write authority is granted.

## Carried findings (mirror summary; full records appended in `handoff.json.carried_findings`)

| id | class | summary | disposition |
|---|---|---|---|
| **CF-B5FIX-1** (from reviewer finding ⑤, §7/finding 6, adjudicated) | B5-internal stale sealed record | B5's sealed handoff records `binding.json` = `06ff8064…` / 20819 B (handoff written 21:51:06) while `binding.json` was last written 21:52:21 (+75 s; now `96733875…` / 22652 B); B5's own `evidence/deliverable_consistency.json` (21:52:29) records the **new** values yet reports `PASS`/`problems:[]` ⇒ B5's consistency checker only computes hashes and never cross-checks the digests declared in handoff (its `changes.diff` entry matches, so the divergence is specific to the binding entry). | **Do not edit B5.** External superseded-retention erratum: mark B5 handoff's binding entry **`STALE-SUPERSEDED`** (both values + timeline), retained verbatim, not rewritten; authoritative content = on-disk `binding.json` + `deliverable_consistency.json`. Two B5-era process defects registered: (a) carrier rewritten after handoff seal; (b) consistency-checker coverage gap. Residual uncertainty (reviewer's own): the old 20819-B bytes are unrecoverable; "correct at write time" is inferred from mtime ordering, not proven byte-for-byte. |
| **CF-B5FIX-2** (informational) | content-preserving touch of `START_HERE.md` | `execution_v2/START_HERE.md` mtime `2026-09-21T23:19:55` is later than B5's append proof (21:45:50) and later than B5's review report (23:00:40), yet its content still equals the recorded POST2 `a9cb5a4a…` ⇒ one content-unchanged touch, not by this fix card (all its writes are 09-22 08:31+). | No remediation needed — content is pinned. **Attribution open**: who touched it at 23:19 is undetermined; parent may ask. |
| **CF-B5FIX-3** (informational) | F-8 out of scope | F-8 (repeated frozen-table header row in B5's appended section) is not on this card's finding list. | Not dispositioned here; byte-level pure-append is already covered by the re-run chain proof (`APPEND_ONLY=true`). |

## Not granted

`disclosure_adaptation` stays **unmapped**; `accuracy` stays **unproven**; no production write
authority is granted; B5's sealed attempt is not edited by this landing (its stale record
stays stale — only its disposition is registered here).

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent), 2026-09-22.
- Status transition: `review_pending` → `accepted_scoped` (performed in `handoff.json` by this
  pass on the parent's dispatch; the reviewer's line-122 recommendation reserves the move to
  the parent/owner — never the implementer).
- `implementer_signed: false`; `implementer_never_signs_acceptance: true`; the verdict is
  **transcribed, not authored** by this pass.
- Authority: the acceptance was written by an independent reviewer (独立复核) in
  `reviewer_report.md`, never by the implementer and never by this file's author.
- This pass wrote exactly three files: `review.md` (created, this file), `handoff.json`
  (status + status_authority + bookkeeping + carried_findings appended; pre-existing content
  otherwise untouched), `evidence/B5-fix/qualification.json` (created). Zero bytes written to
  `reviewer_report.md`, its sidecar, any frozen/historical artifact, the B5 attempt, or
  production.
