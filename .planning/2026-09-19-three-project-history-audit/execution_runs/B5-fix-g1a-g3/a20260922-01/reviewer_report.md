# reviewer_report.md — independent review of card `B5-fix-g1a-g3` (attempt `a20260922-01`)

- **Reviewer role**: independent (sibling of the implementer; the implementer did not self-sign; this file is one of my only two writes).
- **Verdict**: **`accepted_scoped`**
- **Scope of this review**: sampled, from-scratch re-execution and targeted reads (per brief: sample, do not exhaust). All my runs used **my own copies** of the card's patched runners + freshly copied frozen cases, executed in `%TEMP%\b5fix_g1a_reviewer\work\` — zero writes into `<PLAN>`, the attempt, the B5 attempt, production, or git.
- `disclosure_adaptation=unmapped`, `accuracy=unproven` for any downstream reuse of these notes.
- REM-79 note for my own text: every claim below carries its measurement domain on the same line (batch sampled, file grepped, window checked).

## 1. G1-a routing — fresh full-batch re-run of M25-M28 (verification item 1)

Own copies, byte-verified before running: patched `M25-M28/run_card.py` = `6d6dd6db…` (matches the card's handoff pin), `run_card_before.py` = `eab01162…` **≡ historical** `execution_runs/M25/a20260919-01/scripts/run_card.py` (sha equal in my copy check). Frozen `cases.json` copied from `execution_runs/M2x/a20260919-01/evidence/M2x/` at run time; interpreter/code-root = M25 `iso\venv` + `iso\checkout_scripts` (production anchors re-asserted: `model_registry.py 9ec65295…`, `model_extensions.py 9939480b…`). 20 of the 33 child processes I launched in this review (20 here + 12 on M01-M04 in §8 + 1 on M14 in §2); raw process rc only:

| arm (M25-M28, 4 cards each) | M25 | M26 | M27 | M28 | expected | verdict fields |
|---|---|---|---|---|---|---|
| E frozen | 0 | 0 | 0 | 0 | 0 | `pass` |
| F mutated `expected`→ValueError | 3 | 3 | 3 | 3 | 3 | `fail`, `set_level_declaration_route=3` |
| G key deleted | 2 | 2 | 2 | 2 | 2 | **`no_verdict`**, `route=2` |
| S extra unknown id (structural) | 1 | 1 | 1 | 1 | 1 | no output JSON |
| B historical byte-copy runner, same mutation as F | 1 | 1 | 1 | 1 | 1 (B5 record) | set-gate abort, no output JSON |

All 20 raw rcs match the claimed matrix (E=0, F=3, G=2 no_verdict, S=1, B=1) for this batch in my own runs. The set-level gate behaves load-bearing in this batch's routing: arm F reports `route=3` and exits 3; arm G reports `route=2` and exits 2 with `no_verdict`; a value difference never produced rc=1 in these 4 cards × {F} runs, and the structural/set-level aborts produced rc=1 in these 4 cards × {S,B} runs.

## 2. G3 reader proof — independent re-execution of one leg (verification item 2)

- Read `evidence/g3_reader_proof.json` (pin OK vs the card's handoff: `3aba66d1…`).
- My own extraction: line 75 of **historical bytes** `execution_runs/M14/a20260919-01/recovery/consolidated_report.py` (file sha `96938c9b…` matches the proof's `reader_file_sha256`) reads verbatim
  `                 run["expectation_consistency"]["facts"]["declared_expectations"]))` — byte-equal to the proof's recorded line. I regex-extracted `run["expectation_consistency"]["facts"]["declared_expectations"]` from that line and `eval`'d it against three documents:

| input (my independent eval) | result |
|---|---|
| frozen baseline `execution_runs/M14/a20260919-01/evidence/M14/run_result.json` | OK → `["ModelRegistryError"]` |
| B5's patched output `B5-plan-level-remediation/a20260921-01/_scratch/M13-M16/E/M14/run_result.json` (read-only) | **`KeyError: 'declared_expectations'`** — F-1 break reproduced |
| **my fresh run** of this card's patched `M13-M16/run_card.py` (sha `69370109…` = handoff pin) on M14, arm E, own copies (1 child process) | OK → `["ModelRegistryError"]`, and `facts` contains **both** `declared_expectations` and `declared_expectations_in_cases_json` with **equal** values |

## 3. G2 = 留置 with no precedence assertion (verification item 3)

Grepped `precedence|outrank|supersed|优先|优先级|高于|优先于` across the whole attempt (896 raw hits), then read every hit in the four designated carriers: `decision.md` D-F3 (lines 439-450), `report.md` §G2 (lines 125-138), `handoff.json` `g2_conflict_record`, and the patched runner's `frozen_rule_text_conflict` (`M25-M28/run_card.py` lines 62/285/316).

- **Affirmative precedence claims between the two frozen artifacts, in those four carriers on my inspection: 0.** Every occurrence there is a negation ("不裁定哪个冻结件优先", "无优先级断言", "NOT asserted - owner declined to rule", `no_precedence_asserted: true`, `precedence_claim_made_anywhere: false`).
- The word "precedence" appears affirmatively elsewhere in the attempt only as (a) the pre-existing rc legend (`"1 > 2 > 3"` / `"1 harness > 2 …"` in runner outputs — a domain-scoped exit-code ordering, present in historical runners too), (b) internal branch-order comments ("unusable-declaration check evaluated BEFORE case judging" — domain: this runner's own control flow), and (c) unrelated copied texts (`oq_rulings` driver_bounds, `oracle.md`/`PROPAGATION_CONTRACT.md` read-only context copies from B5). None of those ranks the frozen `case_contract.rule` against the frozen rc table.

## 4. F-3 — evidence arms populated (verification item 4)

Parsed `arms.{E,F,B,G}` from each batch `evidence.json` in the attempt (all 8 batch files in the attempt parsed on my inspection; the six authorized batches in scope for F-3 are the middle six rows):

| batch | E | F | B | G |
|---|---|---|---|---|
| M01-M04 | 0 | 0 | 0 | 1 |
| M05-M08 | 0 | 3 | 0 | 2 |
| M09-M12 | 0 | 3 | 3 | 2 |
| M13-M16 | 0 | 3 | 2 | 2 |
| M17-M20 | 0 | 3 | 3 | 2 |
| M21-M24 | 0 | 3 | 3 | 2 |
| M25-M28 | 0 | 3 | 1 | 2 |
| M29-M31 | 0 | 3 | 0 | 2 |

No nulls in the fields I read on those 8 files; values match the handoff `measurements.per_batch` block and the arm-B-unchanged claim for the six authorized batches. `commands.json` contains **128** `"raw_rc"` records (count of occurrences on that one file).

## 5. F-7 — append proof (verification item 5)

`evidence/start_here_append_proof_fixed.json` (pin OK vs handoff `7c4c95dc…`) on my read: `APPEND_ONLY=true`; `frozen_anchor_check.operand_count=19`, `operand_distinct_count=19`, `operand_is_distinct=true` (dedup asserted), `operand_equals_live_extraction_from_frozen_prefix=true`, all anchors full-line present in frozen prefix and current file, `missing_from_*=[]`; chain PRE `1bdfbd91…` (9895 B) → POST1 `e7cb90fc…` (16314 B) → POST2 `a9cb5a4a…` (18452 B). **On disk** `execution_v2/START_HERE.md` = 18452 B, sha **`a9cb5a4a34929fb21d43b3f8308c36b03440d73c43325b8952e81fe130f64caf`** — equal to B5's recorded POST2 value, i.e. content unchanged since B5 on the one hash axis checked for that file.

## 6. Boundaries (spot-check, verification item 6)

- **Frozen `cases.json`, sample 5 of 31** (M01/M09/M17/M25/M31): my computed shas (`462ea30c…`, `d0613d34…`, `e09bdc89…`, `268c8a47…`, `6063b2a8…`) all appear in the attempt's `evidence/boundary_verification.json`; mtimes 2026-09-20T15:52–15:58 (predating the B5 attempt day). The remaining 26 cases files rely on the card's own 31/31 census, which I did not re-hash.
- **Runner byte-identity, 2 pairs checked**: attempt `M25-M28/run_card_before.py` ≡ historical M25 runner; attempt `M01-M04/run_card.py` ≡ historical M01 runner (both sha-equal in my copy checks). The card's 68-copy census was read, not re-run.
- **Production anchors**: `scripts/model_registry.py` = `9ec65295…`, `scripts/model_extensions.py` = `9939480b…` — both equal the card's claimed anchors on my re-hash.
- **git**: `git status --porcelain` filtered to `execution_runs/M01..M31/` = **0 lines** on my run (the repo-wide 86 dirty lines are outside M01..M31: I-08/I-14/findings.md/etc., pre-existing and out of this card's claim domain).
- **B5 attempt zero-writes in my activity window** (2026-09-22T08:00→now): 0 B5 files with mtime in that window; newest B5 file overall = `reviewer_report.md` at 2026-09-21T23:00:40. The attempt itself: newest file = `handoff.json` at 2026-09-22T08:47:27 (implementer's, before my window from 08:50); my writes = this file + its `.sha256` pin only.
- **The card's own pins**: all 9 top-level handoff deliverable/evidence pins I recomputed (report.md, decision.md, commands.json, binding.json, changes.diff, g3_reader_proof, boundary_verification, append_proof_fixed, arm_matrix) = PIN-OK; all 8 per-batch `evidence.json` pins = PIN-OK.

## 7. Finding ⑤ adjudicated — B5's sealed records are internally inconsistent (verification item 7)

**Measured facts (all read-only):**

| artifact | mtime | sha / bytes |
|---|---|---|
| B5 `handoff.json` (records `binding.json` deliverable) | **2026-09-21T21:51:06** | declares `binding.json` = `06ff8064…` / 20819 B (its own file: `4ab00755…` / 17435 B) |
| B5 `binding.json` (on disk, actual) | **2026-09-21T21:52:21** (+75 s after handoff) | actual `96733875…` / 22652 B |
| B5 `evidence/deliverable_consistency.json` | 2026-09-21T21:52:29 | records `binding.json` = `96733875…` / 22652 B **and** `handoff.json` = `4ab00755…`; `problems: []`, `PASS: true` |
| B5 `reviewer_report.md` (B5's reviewer) | 2026-09-21T23:00:40 | does not pin binding.json (spot grep for `06ff8064`/`96733875` in B5 non-scratch files: only handoff and deliverable_consistency hit) |

**Which is stale:** the **handoff record is stale; the file changed after it was recorded.** binding.json's last write (21:52:21) postdates handoff.json's last write (21:51:06), so the record necessarily describes a pre-final version of binding.json (20819 B) that grew by 1833 B afterwards. Corroborating that handoff's digest machinery was otherwise sound on this axis: handoff's `changes.diff` record (`1b5fef49…`) equals the file checked 83 s later by B5's own consistency artifact, so the divergence is specific to `binding.json`, the one deliverable rewritten after the handoff was sealed. Residual uncertainty (stated, not hidden): the old 20819-B binding bytes are unrecoverable, so "correct at write time" is inferred from the mtime ordering, not proven byte-for-byte.

**Recommended disposition (no edit to B5 — I made none):** superseded-retention erratum **outside** the sealed B5 attempt, in the parent's register or a future authorized card: record both values with the timeline above; declare authoritative for content the on-disk `binding.json` (`96733875…`/22652 B) together with `evidence/deliverable_consistency.json` (`21:52:29`); mark handoff's `binding.json` deliverable entry (`06ff8064…`/20819 B) **STALE-SUPERSEDED, retained verbatim, not rewritten**. Also register two B5-era process defects as informational: (a) write-ordering — a carrier was rewritten after the handoff seal; (b) `deliverable_consistency.json` reported `PASS`/`problems:[]` while sitting on top of a declared-vs-actual digest mismatch for `binding.json`, i.e. that checker hashed files but did not cross-check handoff's declared digests. Neither defect is attributable to this fix card, which discovered and disclosed the mismatch read-only (`report.md` §G5, `handoff.json` scope_observations) exactly as measured here.

## 8. M01-M04 measurement (verification item 8, underpins REM-80)

Fresh runs, byte-copy historical runner (sha `b5fcc685…` ≡ `execution_runs/M01/a20260919-01/scripts/run_card.py`, and ≡ the attempt's `M01-M04/run_card.py`), own copies of the four cards' frozen cases, M01 `iso` interpreter — 12 child processes:

| arm | M01 | M02 | M03 | M04 | expected |
|---|---|---|---|---|---|
| E frozen | 0 | 0 | 0 | 0 | 0 |
| F mutated `expected` | 0 | 0 | 0 | 0 | 0 (fabricated green — confirmed) |
| G key deleted | 1 | 1 | 1 | 1 | 1 (stderr `KeyError: 'expected'` on all four) |

Confirms the card's scope observation: M01-M04 measure E=0/F=0/B=0/G=1 and are outside the six T1-8-authorized batches; uniformity on the card's matrix therefore stands at **27/31**, and patching M01-M04 remains an owner call.

## 9. Numbered findings

1. **[blocking → FIXED, verified]** G1-a three-way routing in the attempt's patched `M25-M28/run_card.py` is present and load-bearing: fresh runs on my own copies give F→rc=3 (`route=3`), G→rc=2 + `no_verdict` (`route=2`), S/B→rc=1 (20/20 raw rcs match claim §1). Domain: M25-M28, my 20 child processes.
2. **[blocking → FIXED, verified]** G3 dual-key emission: my fresh M14 output carries both `facts` keys with equal values, the historical reader expression (extracted from historical line 75) evaluates OK on baseline and on my fresh output and raises `KeyError` on B5's patched output — F-1's break is reproduced and closed.
3. **[verified]** F-3: `arms.{E,F,B,G}` populated with real rc on all 8 batch `evidence.json` files I parsed (no nulls in the fields read); 128 `raw_rc` records in `commands.json`.
4. **[verified]** F-7: `APPEND_ONLY=true`, 19/19 distinct anchors with dedup assertion and live-extraction equality; `START_HERE.md` on disk = `a9cb5a4a…` (unchanged since B5's recorded POST2).
5. **[verified]** Boundaries on my sample: 5/5 sampled frozen `cases.json` equal the card's recorded hashes with pre-B5 mtimes; 2/2 runner byte-identity pairs equal their historical sources; production anchors match; `git status` over `execution_runs/M01..M31/` = 0 lines; 0 B5-attempt writes in my window; all 17 of the card's own pins I recomputed = OK.
6. **[new finding ⑤ → adjudicated, B5-internal]** B5 `binding.json` actual `96733875…`/22652 B vs B5 handoff's record `06ff8064…`/20819 B: the handoff record is stale — binding.json was last written 75 s after the handoff was sealed; disposition = external superseded-retention erratum + informational process-defect notes (§7). No B5 edit; none made.
7. **[informational, B5-era]** `execution_v2/START_HERE.md` mtime is 2026-09-21T23:19:55, later than B5's own append-proof (21:45:50) and later than B5's reviewer report (23:00:40), yet its content still equals the POST2 sha `a9cb5a4a…` that both B5 records carry. Domain: that one file, content axis only — content unchanged; an unidentified content-preserving write/touch after B5's review is unexplained by any record I inspected. Not caused by this fix card (all its writes are 2026-09-22 08:31+). Recommend parent ask who touched it at 23:19; no remediation needed if content-pinned.
8. **[informational]** B5's `evidence/deliverable_consistency.json` reports `PASS`/`problems:[]` while recording the actual binding hash that contradicts handoff's declared hash — the checker gap feeding finding ⑤'s disposition.
9. **[open by owner ruling, correctly registered]** G2 conflict stays 留置 with zero precedence assertions in the four carriers (§3); F-4's START_HERE correction and F-8 remain outside this card's authorization and are listed as remaining gaps — consistent with the record, owner calls.

## 10. Unverified (sampled out, by design of this review)

- Arm values for M05-M08 / M09-M12 / M13-M16 / M17-M20 / M21-M24 / M29-M31 (E/F/B/G incl. the M17-M20 reference 0/3/2 and the arm-B-unchanged row for those batches): read from the attempt's evidence only; **not** re-executed by me. My 33 fresh child processes covered M25-M28 (4 arms+B × 4 cards = 20), M01-M04 (E/F/G × 4 cards = 12), and M14 arm E (1); the six authorized batches' other cards rely on the card's evidence plus the prior sibling reviewer's reruns.
- The 128 `raw_rc` records in `commands.json`: existence/count verified; individual records not re-executed.
- Frozen `cases.json` beyond the 5 sampled; the 68-runner census beyond 2 byte-identity pairs; `scripts/verify_append_fixed.py` and `scripts/verify_boundaries.py` not re-run by me (re-running them would write into the attempt, which my brief forbids) — I validated their output JSON fields and pins directly instead.
- Chain-proof prefixes PRE (`1bdfbd91…`) and POST1 (`e7cb90fc…`) accepted from the evidence record; only the current-file endpoint (`a9cb5a4a…`) was re-hashed live.
- "No rc constant renumbered" taken from behavior (observed rc set {0,1,2,3} across my runs matching the frozen legend) plus the diffs' visible additions; no exhaustive static audit of every rc literal in the patched runner.
- Who performed the 2026-09-21T23:19:55 content-preserving write to `START_HERE.md` (finding 7): undetermined from the records I sampled.

---

*All rc values above in §1/§8 are raw child-process exit codes from runs I launched myself on my own copies in this review window (2026-09-22 ~08:50–09:0x); every file read outside the two report files I wrote was read-only. `status` recommendation: `accepted_scoped` — move out of `review_pending` only by the parent/owner, not by the implementer.*
