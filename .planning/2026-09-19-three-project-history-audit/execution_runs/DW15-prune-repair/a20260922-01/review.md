# DW15-REPAIR — carrier landing (bookkeeping transcription)

## VERDICT BLOCK

- **verdict** = `accepted_scoped`
- **carrier** = `reviewer_report.md`
- **carrier sha256 (new)** = `a9b9076f731b8395c6f8a6fabcd90c835ea8a68a00cc7ffac7c9f14014b0801e`
  (supersedes the older `7944b17f…` pin after the reviewer's ruling addendum)
- **pin** = `reviewer_report.sha256` → `a9b9076f731b8395c6f8a6fabcd90c835ea8a68a00cc7ffac7c9f14014b0801e  reviewer_report.md` — verified by the carrier: measured hash == sidecar, 19466 B.
- **ruling location** = `reviewer_report.md` L24–L60 (`## RULING (reviewer, three-state): \`accepted_scoped\``)
- **reviewer** = 独立复核 (independent re-check; the reviewer wrote only `reviewer_report.md` + `reviewer_report.sha256`)
- **nature of this file** = bookkeeping transcription, adds no acceptance of its own. The carrier does not self-sign; the implementer never signs. This document authorizes nothing beyond restating the reviewer's ruling.

## Scope transcribed from the carrier (verbatim in substance)

### ACCEPTED (in scope)

Only the iso/fixed repair code — prune `0c99bbe0…` / 23115 B, archive `bbe855e4…` / 9894 B — as verified fixes of defects **D1–D5**, together with its evidence chain:

- oracle pin `003f48da31f1…` (frozen `oracle.md`),
- RED 15 failed / rc1 → GREEN 15 passed / rc0,
- mutation matrix M1–M5 declared == observed,
- M5 independently re-run by the reviewer.

i.e. acceptance covers **code correctness of the isolated copy against this attempt's frozen oracle, and only that** (reviewer_report.md L28–L34).

### EXPLICITLY OUT of scope — four independent states, none granted

(a) any **production prune/archive EXECUTION**, dry-run included, stays **unauthorized** (owner `OWNER_DECISIONS.md` §15/§16 `A-1`, §16 `E-4 = 维持暂不签`); (b) **promotion** of `iso/fixed` into `company-wiki` stays a separate, **undone** owner decision; (c) the **data-recovery re-sign** stays **unsigned** — it is a precondition of a future *execution* card, NOT of this card's acceptance. The reviewer's explicit argument, recorded as theirs: this card's authorized scope was "repair code only" (owner A-1) and that scope is now delivered and verified, so making the re-sign a condition of *this* card's acceptance would make the card permanently unaccept-able, contradicting the owner's explicit grant of the repair card; (d) the **handoff status transcription** is the **carrier's step**, not part of the ruling (reviewer_report.md L35–L45).

### Carried findings (registered, non-blocking) — F1–F6

F1 (multi-batch D4 "0 deleted" narrow window), F2 (conflicting-digest order dependence), F3+F5 (RED evidence captured `--tb=no`, UTF-16LE), F4 (no directory fsync → power-loss durability unproven), F6 (freeze ordering evidenced by mtimes + hash pin only) (L46–L50, detail L205–L233).

### Carried unverified items (registered) — U1–U8

U1–U8 as listed by the reviewer. Suggested — **not required for this card** — as entry criteria for any future *execution* card (receipt durability medium U5, address/waive F1/F2, scale behaviour U4, replace product contract tests U7); they are NOT conditions of this card's acceptance (L51–L55).

Conditions on this acceptance: **none blocking**; F1/F2 are LOW-severity edge cases, carried, not gating. This ruling does not sign, and does not release, any of the four out-of-scope states above (L57–L60).
