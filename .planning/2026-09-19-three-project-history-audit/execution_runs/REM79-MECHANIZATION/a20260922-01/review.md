# REM79-MECHANIZATION review.md — CARRIER LANDING (verdict transcribed by the carrier-landing executor; the implementer did NOT sign)

Status: **`accepted_scoped`**. The independent reviewer wrote the verdict in
`reviewer_report.md` (the byte-pinned carrier), **not** in this file. This file is the
carrier-landing bookkeeping landing of that verdict: it transcribes the reviewer's verdict so
the attempt's `review.md` slot exists. **It is a pure bookkeeping transcription: it is not a
signature, and it adds no acceptance of its own.** Read `reviewer_report.md` itself for the
reviewer's own words (§1–§7, Findings, Scope of acceptance, unverified list, boundaries). No
verdict, review, or acceptance was authored in this pass.

`review.md` did not previously exist in this attempt (no implementer stub to preserve); this
file was created by the carrier-landing pass — not by the implementer and not by the reviewer.

## Verdict block (transcribed)

- Card: **REM79-MECHANIZATION** (REM-79: every universal-quantifier claim must carry its
  domain on the same line — mechanized as a frozen-rule checker with a red/green/mutation
  proof and two parent-ordered append-only lexicon corrections)
- Attempt: `a20260922-01` (`<PLAN>\execution_runs\REM79-MECHANIZATION\a20260922-01`)
- Verdict: **`accepted_scoped`** — the reviewer's literal label is in
  `reviewer_report.md` line 8: ``## VERDICT: `accepted_scoped` ``; the rationale line
  (line 10) states "none of the 5 is blocking (F1 is a disclosed documentation nit)" and
  "Acceptance is scoped by the six items in the *Scope of acceptance* section".
- Verdict author: **独立复核** — an independent reviewer session dispatched by the parent
  (line 3); the reviewer's signing line (116) states "acceptance authority for this attempt
  rests with this report, not with the implementer handoff"; line 6 records the handoff
  remains unsigned (`implementer_signed=false`, `verdict_expressed=false` at review time).
- Verdict round: round 1 of this card (single independent review round); the verdict is
  **scoped**, not clean.

### Carrier (byte-pinned)

| field | value |
|---|---|
| carrier file | `reviewer_report.md` |
| path inside attempt | `reviewer_report.md` |
| sha256 | `0562158deac6661db2988e01e7ac505f7cc9372152838dbe043bf7b265de68c4` |
| bytes | 18393 (independently re-hashed at landing; see byte note below) |
| lines | 116 (LF-only, no BOM, single trailing LF) |
| pin sidecar | `reviewer_report.sha256` — **pre-existing** (reviewer-declared in its boundaries section); content `0562158deac6661db2988e01e7ac505f7cc9372152838dbe043bf7b265de68c4  reviewer_report.md`, 85 B, sidecar sha256 `4a34fe58134f9de938c11c884401b2d39312d5821f6b2fb1584cbf58a8cb810c`. Sidecar content **matches** this pass's independent re-hash ⇒ not overwritten; **0 bytes written** to it |
| verdict line | 8 |
| first line of verdict | ``## VERDICT: `accepted_scoped` `` |
| verdict-line byte region | bytes 834..862 inclusive (29 B, without the LF), sha256 `e73c0ee633559827314c0517d1f2bd64fafe5bdf2fd2906d8f614e4cbd46b55e` |
| verdict rationale line | 10 (bytes 865..1385, 521 B, sha256 `8bd087842a8b38fea442d38cd9ce3115a655cd4b970ce0d46b1b0b0faf498a61`) |
| handoff-unsigned disclosure line | 6 (bytes 622..831, 210 B, sha256 `6eff1520b81200a4b0ba3f611963bd4dd5fc09b212eab2fd503490549ed6ca4d`) |
| findings section lines | 81–91 (header 81; F1 line 83 bytes 12371..13366 sha256 `a427fac23b45ff4295709d1f34ab66e111896da109d53c6a302107dadfbc82ef`; F5 line 91) |
| scope-of-acceptance (six conditions) lines | 93–100 (heading 93 bytes 14710..14776 sha256 `ab971179fd2696f69e37f223f0d42ee37406e58c93fdcb2b74b5230aa230492b`; item 1 line 95 bytes 14779..15024 sha256 `0d4ea9583b5514812c7f4323adc3dea6e4f0af77887c9845ec71e39693425d03`; item 6 line 100 bytes 15956..16311 sha256 `16af7be82213bae9b567802911c17758d8ae87f82f10c9cec0b35a944ceb22c4`) |
| unverified/limits section lines | 102–110 |
| reviewer-boundaries section lines | 112–116 (signing/authority line 116 bytes 18235..18391, 157 B, sha256 `710f46b696026755b32cf3058acdfcd3a4ab0262d5796e08bcaa45c60a0ed5d3`) |
| carrier region (whole file minus the single trailing LF) | bytes 0..18391 inclusive (18392 B), sha256 `5ce0a824d18a965fbc02c34cae33f0e074b968b0b7a6a883b040c6e943086e88` |
| producer | independent reviewer (独立复核), not the implementer |

**Byte note (non-blocking, recorded honestly):** the landing dispatch cited the carrier as
18088 B; the file on disk is **18393 B** (UTF-8, no BOM, LF-only, single trailing LF; char
count 17994). The pin is authoritative, not the dispatch's byte figure: the pre-existing
sidecar's recorded sha256 equals this pass's independent re-hash of the current bytes, and
the verdict is on line 8 either way. The 18088 figure matches neither bytes nor chars and is
treated as a stale dispatch measurement — no file was changed to reconcile it.

No byte of the carrier was changed by this landing pass: `reviewer_report.md` and its
`reviewer_report.sha256` sidecar were read-only here (this pass wrote only `review.md`,
`handoff.json`, and `evidence/REM79-MECHANIZATION/qualification.json`).

## (a) Scope conditions — the six §4 items, VERBATIM from the carrier (`Scope of acceptance`, lines 93–100)

Acceptance is **SCOPED, not clean**. Reproduced word-for-word from the reviewer's report:

1. **Lexicon ≠ semantics (词表≠语义):** the frozen marker list is not the semantics of "universal" — claims written with 所有 / 均 / 每次 / 一律 / always / each / both / bare `100%` pass silently by design of the frozen contract.
2. **Domain presence, not correctness:** any domain pattern anywhere on the line satisfies the check; a decorative or wrong-domain qualifier clears the line (D1 `域` … D8b all share this epistemic class).
3. **Line-splitting by design:** a domain on the adjacent line does not count, and multi-line claims are scanned as separate lines — that *is* the letter of REM-79 as mechanized, not a defect.
4. **D11 escape-hatch risk is held knowingly by the parent:** after CORRECTION 2, a genuine un-scoped claim written inside `…`/`"…"`/`「…」` or on a `>` line passes silently; this reverses CORRECTION 1's keep-flagged stance on the owner's explicit ruling, and the risk is recorded in `remaining_gaps_honest` for the owner to carry.
5. **The tool is a scoping-shape checker, not a truth checker:** it verifies that a same-line domain *shape* is present; it never verifies the claim's truth or the measurement behind it.
6. **Live-scan residual = 2 lines, already parent-adjudicated compliant** (R-D paragraph-subject carry on `task_plan.md:1630`; R-E cross-language bound on `findings.md:633`) — this review verified the lines' content matches those rulings and did **not** re-adjudicate them; no CORRECTION 3 exists or will be opened by this attempt (lexicon sealed at v2).

(Dispatch shorthand for the same six: 词表≠语义、域在场非正确性、按行切分设计、D11 引语逃生口风险由父知情持有、工具=形态检查器非真值检查器、live 残差 2 条父已终裁合规.)

## (b) Findings — 5 recorded, NONE blocking (full records in `reviewer_report.md` lines 81–91; mirrored in `handoff.json.carried_findings`)

| id | class | summary | disposition |
|---|---|---|---|
| **F1** | **low, disclosed — documentation nit (NON-BLOCKING)** | Round-3 RED's naive misreport is **7 lines** (`[4,6,12,18,22,26,30]`), not the 14-line misreport expected in each of the 3 summaries (rounds 1 and 2 each show the full 14). Cause: unit **X2 mirrored the marker-side skips (D10b/D11) into the RED arm** (`v1.0.2-red-correction2`), shrinking its detection surface. Disclosed in `handoff.json` round-3 RED note ("marker-side skips now shared by both arms") and by oracle §C2.3's documented **monotone shrink**. RED still `RED_FAILS_ORACLE_AS_REQUIRED` with **all 4 positives caught**; §C1.4's domain-blind argument is **grep-confirmed** intact (no domain logic in the naive arm). Residual nit: frozen **oracle §7 still literally says RED "flags the 14 `neg_domain_lines.md` payloads" with no explicit §7-supersession sentence** (contrast §3's explicit supersession in C2.2) — the actual round-3 count is 7. | **Non-blocking.** Drift is disclosed in the handoff; no oracle re-write (lexicon sealed, no CORRECTION 3). **Low-priority follow-up the parent may close by a register note** recording that oracle §7's "14" is superseded as to round 3 by §C2.3's monotone-shrink record. |
| **F2** | info — wording | "131 evidence files": precisely, `final_hashes.json` pins **131 entries = every attempt file except the ledger itself** (attempt = 132 files pre-review); the `evidence/` subtree alone holds 104 files. | True as ledger coverage; the phrase is wrong only if read as an evidence-subtree count. No action; wording recorded. |
| **F3** | info — counts | `remaining_gaps_honest` carries **8** entries where the brief expected 7: the 7 briefed gaps present verbatim-in-substance (incl. ④ D11 escape hatch and ⑤ the two sealed residuals) plus an 8th honest entry (b2 NP-breadth trade-off). | Superset ⇒ parity holds. No action. |
| **F4** | info — attribution | Plan-carrier ` M` flags in `git status` come from parent/pre-existing activity, not the card: `findings.md` mtime 09:14:07Z predates the card window (sha == extraction sha), `progress.md` mtime 10:31:13Z postdates the card's last write (10:28:17Z), `task_plan.md` clean and byte-identical to extraction. | Recorded so the ` M` state is not misattributed to REM79. No action. |
| **F5** | info — tooling | `grep`/`glob` intermittently failed in this workspace (permission-denied under `.planning/…/reviews/*/scratch\|pytest_tmp`, one `NUL` path error); each affected claim was re-verified via `read` and targeted `pwsh`. | No verdict impact. (This landing pass hit the same permission-denied dirs and, per F5's own method, used `read`/targeted `pwsh` instead.) |

## (c) Key verifications the reviewer performed (carrier §1–§7, all VERIFIED)

- **Three-segment prefix chain, recomputed independently:** FREEZE `sha256(oracle.md bytes[:13029]) = 6faa0ae9…241f` with `checker_existed_at_freeze=false` in `evidence/freeze_record.json`; CORRECTION 1 `bytes[:19324] = c8a6f209…` == C1 ledger `post_sha256` == C2 ledger `pre_sha256`; CORRECTION 2 terminal whole-file `94306a43…5c830` @ 26285 B; `oracle_table.json = 366b1825…edae7` unchanged across both corrections; 6/6 frozen corpus payloads re-hashed exact. Both ledgers read as append-only prefix proofs with empty self-audit arrays.
- **Triple-run protocol: `PROTOCOL_SATISFIED` ×3** (rounds 1/2/3). Every round: GREEN exact 4/0 against the unchanged table, per-file exits **1/1/1/1/0/0**, mutations A `[4]` rc1 / B `[]` rc0 / C `[5] ≠ [4]`, oracle self-scan 0 violations. RED = `RED_FAILS_ORACLE_AS_REQUIRED` in all three rounds (14-line naive misreport rounds 1–2, 7-line round 3 — F1). Round-3 JSONs carry `1.2.0-correction2` (GREEN/mutation) and `1.0.2-red-correction2` (RED). Raw stdout cross-checked: 18 violations (4+14) round 1, 11 (4+7) round 3, 4 for GREEN; `round1_findings_214.txt` = exactly 214 lines.
- **Quote mini-GREEN (C2):** `C2_MINI_GREEN_PASS` — declared `[12,14]` == reported `[12,14]`, controls `[4,6,8,10]` clean, rc 1; layout declared in oracle §C2.3 **before** the sample existed; honesty log (unit X3) records the first run's `[11,13]` caused by a missing blank line 2, fixed in the sample, not in the declarations.
- **Adjudication chain, both archived and read:** `parent_adjudication_r1.md` (TP=0 over 214; three FP classes a/b/c; D8/D9/D10 protocol order; "neither side edits files to suit the checker") and `parent_adjudication_r2_and_c2.md` (TP=0 over 48; classes R-A/R-B/R-C; the D8b/D10b/D11 prescription; no-CORRECTION-3 seal; conditional mini-GREEN). Live chain r1=214 → r2=48 → r3=2 (`cleared_since_r1=212`, `new_vs_r1=0`, `correction3_opened=false`); both residual lines' **content** checked against rulings R-D/R-E without re-adjudication; `task_plan.md`/`findings.md` byte-identical to extraction hashes (progress.md drift alone explains `plan_hashes_unchanged_since_extraction=false`).
- **Tool smoke test (reviewer's own read-only run):** `tools/check_domain_assertions.py` on `corpus\pos_i14d_review_L349.md` → line 4 `[every]`, **1 violation, rc 1** — matching the recorded behavior; `VERSION = "1.2.0-correction2"`, sha256 == `final_hashes.json`, stdlib-only imports; exit semantics 0/1/2 match oracle §6; corpus re-hashed 6/6 unchanged.
- **Honest-gap ledger:** `remaining_gaps_honest` = 8 entries, carrying all 7 briefed gaps verbatim-in-substance plus one extra (F3).
- **Boundaries:** plan-file edits by the card = 0 (supported by mtimes/hashes, with the honest `progress.md` post-card note); git writes = 0 (nothing observed contradicts it; negative claim flagged as such); writes confined to the attempt; `final_hashes.json` spot-check **5/5 exact**; handoff self-declaration consistent pre-landing (`status=review_pending`, `verdict_expressed=false`, `implementer_never_signs_acceptance=true`, `network_used=false`, `git_writes=0`, `plan_file_edits=0`).

## (d) NOT granted by this review (carrier "Not verified / limits" lines 102–110 + scope)

1. The full RED/GREEN/mutation harness was **not re-executed** — summaries read in full, raw stdout cross-checked, one corpus smoke test instead.
2. `final_hashes.json` spot-checked **5 of 131**; the other **126 were not re-hashed** (corpus separately re-hashed 6/6).
3. The correction ledgers' self-audit claims were read but the inline audit code was **not re-run**.
4. The REM79 plan-card original for the "7 gaps" enumeration was not located by grep; gap parity judged against the dispatch's substance.
5. The 214 + 48 live detections were **not** re-adjudicated line-by-line (parent's domain by instruction); the rulings themselves stand as the parent's.
6. "0 git writes" / "0 plan-file edits" are negative claims — supported, not provable to certainty from repository state.
7. `binding.json` internals not parsed entry-by-entry (tool hash verified via `final_hashes.json` + direct disk hash instead).

Also **not granted**: `disclosure_adaptation` stays **unmapped**, `accuracy` stays **unproven**; no production write authority; no edit to any frozen/oracle/harness artifact; no CORRECTION 3 (lexicon sealed at v2); no re-opening of the parent's adjudications; and **this file grants nothing** — it is bookkeeping transcription only.

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent), 2026-09-22.
- Status transition: `review_pending` → `accepted_scoped`, performed in `handoff.json` by this
  pass on the parent's dispatch; the verdict itself is the reviewer's (line 8).
- `implementer_signed: false`; `implementer_never_signs_acceptance: true`; the verdict is
  **transcribed, not authored**, by this pass.
- Authority: acceptance was written by an independent reviewer (独立复核) in
  `reviewer_report.md` (sha256 `0562158d…68c4`, 18393 B, pinned by the pre-existing
  `reviewer_report.sha256`), never by the implementer and never by this file's author.
- This pass wrote exactly three files: `review.md` (created, this file), `handoff.json`
  (status + status_authority + bookkeeping + 5 appended carried findings + pre-verdict prose
  retained under `*_historical_pre_verdict`; pre-existing content otherwise untouched), and
  `evidence/REM79-MECHANIZATION/qualification.json` (created). Zero bytes written to
  `reviewer_report.md`, its sidecar, any frozen/historical artifact, any plan file, any git
  state, or production.
