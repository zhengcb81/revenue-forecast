# REM79-MECHANIZATION — independent reviewer report

- Card: **REM79-MECHANIZATION** · Attempt: `a20260922-01` · Reviewer: independent session dispatched by parent `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`
- Evidence date: 2026-09-22 (card window ~09:46–10:28 UTC) · Review performed after the card closed
- Method: sampled independent verification, per the dispatch's 7 sections. Tools used: `read` / `grep` / `pwsh` only (per dispatch constraint; 域：dispatch tools-only rule). One smoke execution of the deliverable checker on corpus, plus one self-scan of this report (disclosed in Reviewer boundaries).
- This report is the reviewer's acceptance instrument. The implementer handoff remains unsigned (`implementer_signed=false`, `verdict_expressed=false` in `handoff.json` — 域：本报告 verdict block below).

## VERDICT: `accepted_scoped`

The three-segment frozen oracle chain, the triple-run RED/GREEN/mutation protocol, the declared quote-sample mini-GREEN, the live-scan/adjudication chain, the tool behavior, the honest-gap ledger, and the write boundaries all hold up under independent re-computation. Five findings are recorded below; none of the 5 is blocking (F1 is a disclosed documentation nit). Acceptance is scoped by the six items in the *Scope of acceptance* section (域：本节 = acceptance scope conditions, all six required by the dispatch).

---

## 1. Three-segment oracle chain — VERIFIED by independent recomputation

| segment | claim | my recomputation | result |
|---|---|---|---|
| FREEZE | `sha256(oracle.md bytes[:13029]) = 6faa0ae9…241f` | `6faa0ae90a0693ffeb03f9b63a811d4832d12f0e598f1699dcaf29462bdc241f` | MATCH |
| freeze record | `evidence/freeze_record.json` carries that sha + `checker_existed_at_freeze=false` | read: both present (also pins `oracle_table` + 6 corpus hashes) | MATCH |
| CORRECTION 1 | `bytes[:19324] = c8a6f209…` + C1 ledger | `c8a6f20931bbf92aea96b5ea2be9ece19f977bc2f778dcd22a2f1f00c83be824` == C1 ledger `post_sha256` == C2 ledger `pre_sha256` | MATCH |
| CORRECTION 2 | terminal sha `94306a43…5c830`, 26285 B + C2 ledger | whole-file `94306a4340e5ee6155629e1e2df06a08313f3e8d2326995935e7948d8535c830`, `26285` bytes | MATCH |
| table | `oracle_table.json = 366b1825…edae7` unchanged across both corrections | disk hash `366b18253c973306fc1a8ea237c377551bc3be68243e6fc83cf5f247a87edae7` == freeze-record value recorded before either correction | MATCH |
| corpus | 6 frozen payloads byte-stable | re-hashed the 6 payloads on disk against `freeze_record.json` — 6/6 exact | MATCH |

Both ledgers (`evidence/oracle_correction1_ledger.json`, `evidence/oracle_correction2_ledger.json`) read as append-only prefix proofs with empty self-audit arrays. `oracle.md` read end-to-end: §1–§10 frozen body, §11 corrections policy, then labelled `CORRECTION 1` (C1.1–C1.4) and `CORRECTION 2` (C2.1–C2.3) appended, each quoting old/new text and declaring "expectations invalidated: 0" with the C2 no-CORRECTION-3 freeze (域：本表 = 2 correction ledgers, both recomputed).

## 2. Protocol triple-run — VERIFIED, one disclosed deviation (F1)

Read the three `verify_summary.json` files in full:

- **Round 1** (`evidence/verify_summary.json`): `PROTOCOL_SATISFIED`; RED `RED_FAILS_ORACLE_AS_REQUIRED` with the **14-line** naive misreport on `neg_domain_lines.md` `[4,6,…,30]` + `caught_all_oracle_positives=true`; GREEN exact 4/0, per-file exits **1/1/1/1/0/0**; mutations A `[4]` rc1 / B `[]` rc0 / C `[5] ≠ [4]`.
- **Round 2**: identical structure, RED still the **14-line** misreport (D8/D9 are domain-side, so — per oracle §C1.4 — they cannot change a domain-blind arm's output), GREEN 4/0 exact against the unchanged table, the 3 mutations re-pass; `checker_version 1.1.0-correction1`.
- **Round 3**: `PROTOCOL_SATISFIED`; GREEN/mutation JSONs each carry `"version": "1.2.0-correction2"`; RED arm carries `"version": "1.0.2-red-correction2"`; GREEN 4/0, per-file exits 1/1/1/1/0/0; mutations `[4] / [] / [5]`; RED verdict `RED_FAILS_ORACLE_AS_REQUIRED` — but its naive misreport is now **7 lines** `[4,6,12,18,22,26,30]`, not 14 (see F1).
- **§C1.4 domain-blind claim confirmed by grep** of `harness/naive_checker_marker_only.py`: the arm holds only CJK/EN marker lexicons and `domain_check: false`; its docstring states the domain-side changes (D8/D9/D8b) cannot affect what it reports. No domain pattern exists in that file (域：grep = 8 matches, all marker/`domain_check=false` mentions).
- **Raw corroboration**: round-1 naive stdout ends `18 violation(s) across 6 file(s)` (= 4 positives + 14 negatives); round-3 naive stdout ends `11 violation(s) across 6 file(s)` (= 4 + 7); GREEN text stdout ends `4 violation(s) across 6 file(s)`; `round1_findings_214.txt` = exactly 214 lines; oracle self-scan files present for all 3 rounds (0 violations each).

## 3. Quote-sample mini-GREEN (C2) — VERIFIED

- `evidence/correction2/quote_samples_verdict.json` = `C2_MINI_GREEN_PASS`: declared `[12,14]` == reported `[12,14]`, controls `[4,6,8,10]` clean, `rc 1`.
- Declaration-before-sample: oracle §C2.3 (frozen in the C2 append) states the layout (title/src/blank then payloads at 4,6,8,10,12,14), expected flags `[12,14]`, expected exit 1, **before the sample file existed**.
- Sample file on disk matches that declared layout (blank line 2 present; payload semantics: 4 = backticks, 6 = 「」, 8 = "", 10 = `>` line-start, 12/14 = spaced controls).
- **Honesty log exists**: `commands.json` unit X3 records that the first run reported `[11,13]` because the sample file was missing the declared blank line 2 — the fix corrected the sample layout, not the declarations, and the first-run outputs were overwritten only by that unit's final pass（域：X3 honesty log）.

## 4. Live-scan chain — VERIFIED (residual content checked, ruling not re-adjudicated)

- r1 = **214** (list file = 214 lines; per-file 131/37/46 sums to 214) → r2 = **48** (28/10/10; `round2_summary.json`: disappeared 167 by cause D8=136/D9=5/D10a=26, remained 47, new 1) → r3 = **2** (task_plan 1 / findings 1 / progress 0).
- `round3_summary.json`: `cleared_since_r1=212`, `remained_since_r1=2`, `new_vs_r1=0`, `round2_cleared_by_c2=46`, `correction3_opened=false`, `checker_version=1.2.0-correction2`.
- Round-2 NEW=1 attribution read (`round2_new1_attribution.md`): owner content drift on `progress.md` between scans, with the honest caveat that progress.md's disappear/cause labels are best-effort; `plan_hashes_unchanged_since_extraction=false` refers to progress.md **alone** — I independently confirmed: plan `task_plan.md` full sha `4096a44d…bc687bf` and plan `findings.md` full sha `5a6acccca01a…fc8f5a` are each **byte-identical to `sha256_at_extraction` in `corpus_manifest.json`**; progress.md drifted (extraction `e86b91cc…` → now `486fda5e…`).
- **Both adjudications archived and read**: `parent_adjudication_r1.md` (TP=0 over the 214; three FP classes a/b/c; protocol-path order incl. D8/D9/D10; "neither side edits files to suit the checker") and `parent_adjudication_r2_and_c2.md` (TP=0 over the 48; classes R-A Chinese-numeral counts / R-B hyphen-flag-code identifiers / R-C quotes; the D8b/D10b/D11 prescription; no-CORRECTION-3 seal; the conditional mini-GREEN requirement). Substance matches the ruling as the dispatch described it.
- **Final 2 lines — content vs ruling (no re-adjudication, as ordered)**: `task_plan.md:1630` reads `—— 全部以 **6 元组**解包 \`oracle.CASES\`，而 r3 把它**加宽为 7**（…）` — universal followed by 以+space with the count *after* it: exactly the "count-after-universal / paragraph-subject carry" shape of ruling **R-D**. `findings.md:633` reads ``**推送前第 0 步**：`drift_patrol` **ALL GREEN rc=0**（…七检）…`` — uppercase `ALL` vs the lowercase `all` literal in frozen b2en, with its bound carried across the parenthetical: exactly ruling **R-E**'s cross-language bound shape. Both contents match the parent's compliant rulings; neither falls inside D8b's five frozen sub-shapes, so leaving them (and opening no CORRECTION 3) is consistent with the seal order.

## 5. The tool — VERIFIED by one corpus smoke run

- `tools/check_domain_assertions.py` on disk: `VERSION = "1.2.0-correction2"`, sha256 `f019d5ff05ca…` (== `evidence/final_hashes.json` entry), imports just `argparse/json/re/sys` (stdlib-only; 域：import 表).
- **Smoke run** (my run): `python -X utf8 -B tools\check_domain_assertions.py corpus\pos_i14d_review_L349.md` → reported `corpus\pos_i14d_review_L349.md:4:[every] …` + `1 violation(s) across 1 file(s)`, **rc 1** — exactly the behavior and rc recorded for that file in `commands.json`/verify summaries (rc 1, line [4]). Read-only run; the 6 corpus files were re-hashed against the freeze record in §1 — 6/6 unchanged.
- Exit-code semantics observed match oracle §6 (0 clean / 1 violations / 2 usage-IO). No plan file was scanned by my run.

## 6. Honest-gap parity — VERIFIED (8 entries carry the 7 briefed gaps)

`handoff.json → remaining_gaps_honest` has **8** entries; every gap named in the dispatch (域：dispatch 7-gap list) is present verbatim-in-substance, plus one extra:

1. marker coverage (词表≠语义: 所有 / 均 / 每次 / always / each / both / bare `100%` pass silently) ✔ (dispatch ①)
2. domain presence-not-correctness (decorative qualifier anywhere on the line) ✔ (②)
3. line-bound by design (adjacent-line domain does not count) ✔ (③)
4. **D11 quoted-line skip = parent-ruled escape hatch**: a genuine un-scoped claim inside `…`/`"…"`/`「…」` or on a `>` line passes silently; explicitly *reverses the CORRECTION 1 keep-flagged stance on purpose*; "the risk is stated here so the owner carries it knowingly" ✔ (④ — held by the parent, exactly as briefed)
5. **two residuals outside D8b's five frozen sub-shapes** (`task_plan.md:1630`, `findings.md:633`) — deliberately NOT auto-cleared, **no CORRECTION 3** ✔ (⑤)
6. b2 universal-paired-NP breadth (extra, 8th entry — accepted trade-off of the subject-internal ruling)
7. non-UTF-8 bytes replaced, could hide markers
8. no truth checking at all (域：handoff gap 8): form checker, not a truth checker

## 7. Boundaries — VERIFIED with attribution notes

- **Plan-file edits by the card = 0 (supported).** The live-scan carriers are the plan-directory files (`../../../` from the attempt). Their mtimes vs the card window (~09:46–10:28 UTC 2026-09-22): `task_plan.md` **07:35:37Z** (pre-window; sha == extraction sha; `git status` clean for it), `findings.md` **09:14:07Z** (pre-window; sha == extraction sha; shows ` M`), `progress.md` **10:31:13Z** — *after* the card's newest write (`final_hashes.json` excepted, card's last artifact = 10:28:17Z) → parent/owner activity, not the card. The ` M` flags on findings/progress are therefore pre-existing-vs-HEAD (findings) and post-card parent writes (progress); the workspace-root `task_plan.md`/`findings.md`/`progress.md` (different files, root PWF copies) are clean with 2026-09-20 mtimes. Honest note: `round3_summary.plan_hashes_unchanged_since_extraction=false` reflects the progress.md drift alone (byte-proven in §4).
- **Git writes = 0**: no git command I observed or ran does anything but read (`git status --porcelain`, read-only; see the unverified list item 6). A zero-write claim is a negative claim, but nothing in the evidence contradicts it.
- **Writes confined to the attempt**: the attempt tree holds just its own artifacts; the 6 corpus files, oracle, tool, and evidence match their pinned hashes（域：final_hashes 5/5 + corpus 6/6 重算）.
- **Hash ledger**: `evidence/final_hashes.json` = `file_count 131`, covering every attempt file except the ledger itself (attempt total = 132 files pre-review; `evidence/` subtree = 104 files — see F2 for the wording nit). Spot-check **5/5 exact** (sha256 + byte length) against disk: `oracle.md`, `tools/check_domain_assertions.py`, `evidence/round3/verify_summary.json`, `evidence/correction2/quote_samples_verdict.json`, `evidence/live/round3_summary.json`.
- Handoff self-declaration consistent: `status=review_pending`, `verdict_expressed=false`, `implementer_never_signs_acceptance=true`, `network_used=false`, `git_writes=0`, `plan_file_edits=0`.

---

## Findings (numbered)

**F1 (low, disclosed — documentation nit).** Round-3 RED's naive misreport is **7 lines**, not the 14-line misreport the dispatch expected in each of the 3 summaries (rounds 1 and 2 each show the full 14). Cause: unit X2 mirrored the marker-side skips (D10b/D11) into the RED arm (`v1.0.2-red-correction2`), shrinking its detection surface; `handoff.json` round-3 RED note discloses exactly this ("marker-side skips now shared by both arms"), and oracle §C2.3 documents marker-side shrink as monotone. RED still fails the frozen table as required (`RED_FAILS_ORACLE_AS_REQUIRED`, all 4 positives caught), and the §C1.4 domain-blind argument itself is intact (grep-confirmed: no domain logic in the naive arm). Residual nit: frozen oracle §7 still literally says RED "flags the 14 `neg_domain_lines.md` payloads" with no explicit §7-supersession sentence (contrast the explicit §3 supersession in C2.2) — the actual round-3 count is 7. Non-blocking; the drift is disclosed in the handoff.

**F2 (info — wording).** "131 evidence files": precisely, `final_hashes.json` pins **131 entries = every attempt file except the ledger itself** (attempt = 132 files pre-review); the `evidence/` subtree alone holds 104 files. The ledger claim is true as ledger coverage; the phrase "131 evidence files" would be wrong if read as an evidence-subtree count.

**F3 (info — counts).** `remaining_gaps_honest` carries **8** entries where the brief expected 7: the 7 briefed gaps present verbatim-in-substance (incl. ④ D11 escape hatch and ⑤ the two sealed residuals), plus an 8th honest entry (b2 NP-breadth trade-off). Superset, so parity holds.

**F4 (info — attribution).** Plan-carrier ` M` flags in `git status` come from parent/pre-existing activity, not the card: findings.md mtime (09:14:07Z) predates the card window while still differing from HEAD; progress.md mtime (10:31:13Z) postdates the card's last write (10:28:17Z); task_plan.md is clean and byte-identical to its extraction hash. Recorded here so the ` M` state is not misattributed to REM79.

**F5 (info — tooling).** `grep`/`glob` intermittently failed in this workspace (permission-denied under `.planning/…/reviews/*/scratch|pytest_tmp`, and one `NUL` path error); each claim they failed on was re-verified via `read` and targeted `pwsh`. No verdict impact.

## Scope of acceptance (binding — read together with the verdict)

1. **Lexicon ≠ semantics (词表≠语义):** the frozen marker list is not the semantics of "universal" — claims written with 所有 / 均 / 每次 / 一律 / always / each / both / bare `100%` pass silently by design of the frozen contract.
2. **Domain presence, not correctness:** any domain pattern anywhere on the line satisfies the check; a decorative or wrong-domain qualifier clears the line (D1 `域` … D8b all share this epistemic class).
3. **Line-splitting by design:** a domain on the adjacent line does not count, and multi-line claims are scanned as separate lines — that *is* the letter of REM-79 as mechanized, not a defect.
4. **D11 escape-hatch risk is held knowingly by the parent:** after CORRECTION 2, a genuine un-scoped claim written inside `…`/`"…"`/`「…」` or on a `>` line passes silently; this reverses CORRECTION 1's keep-flagged stance on the owner's explicit ruling, and the risk is recorded in `remaining_gaps_honest` for the owner to carry.
5. **The tool is a scoping-shape checker, not a truth checker:** it verifies that a same-line domain *shape* is present; it never verifies the claim's truth or the measurement behind it.
6. **Live-scan residual = 2 lines, already parent-adjudicated compliant** (R-D paragraph-subject carry on `task_plan.md:1630`; R-E cross-language bound on `findings.md:633`) — this review verified the lines' content matches those rulings and did **not** re-adjudicate them; no CORRECTION 3 exists or will be opened by this attempt (lexicon sealed at v2).

## Not verified / limits of this review (unverified list)

1. The full RED/GREEN/mutation harness was **not re-executed**; I read the 3 summaries in full, cross-checked raw stdout totals, and ran one corpus smoke test instead.
2. `final_hashes.json` was spot-checked on **5 of 131** entries (5/5 exact); the remaining 126 were not re-hashed. Corpus files were separately re-hashed 6/6 against the freeze record.
3. The correction ledgers' *self-audit claims* (0 marker-lines-without-domain in the appended text under the old lexicon) were read but the inline audit code was **not re-run**.
4. The plan-side card text for REM79 (the likely source of the brief's "7 gaps" enumeration) could not be located by grep in `task_plan.md` (grep found 1 unrelated REM-79 scoring line; 域：grep 结果); gap parity was therefore judged against the dispatch's substance, not against a plan-card original.
5. The 214 + 48 live detections were **not** re-adjudicated line-by-line (parent's domain by instruction); the final-2 content was verified against the rulings, but the rulings themselves are accepted as the parent's.
6. "0 git writes by the card" and "0 plan-file edits by the card" are negative claims: supported by mtimes/hashes/evidence consistency above, but not provable to certainty from repository state alone.
7. `binding.json` internals (tool hashes / forbidden list) were not parsed entry-by-entry; the tool hash was instead verified via `final_hashes.json` + direct disk hash.

## Reviewer boundaries (this review)

- Files written: exactly two — `reviewer_report.md` and `reviewer_report.sha256` (both inside the attempt). No plan file, product file, evidence file, or git state was modified; `git` was used read-only (`status` alone); the checker smoke run was read-only; REM-79 self-scan: `check_domain_assertions.py reviewer_report.md` → **rc 0**, re-run after the final edit (域：reviewer self-check).

— reviewer, independent session; acceptance authority for this attempt rests with this report, not with the implementer handoff (域：本报告签署行).
