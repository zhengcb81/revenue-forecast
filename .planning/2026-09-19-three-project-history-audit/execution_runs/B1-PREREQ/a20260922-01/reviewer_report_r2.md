# Independent review round 2 — B1-PREREQ a20260922-01

- Card: **B1-PREREQ** (close B1 review F1–F5 = REM-40…44 before batch-2 promotion)
- Attempt under review: `execution_runs/B1-PREREQ/a20260922-01` — **r2 record-fix round only**
- Source attempt (SRC): `execution_runs/B1-I08C-product-fixes/a20260921-01`
- Round-1 verdict: `changes_required`, sole blocker **F-REV-B1P-01** (report 25883 B /
  `e25a2c83…`, re-verified untouched this round: on-disk hash ==
  `reviewer_report.md.sha256` sidecar, mtime 11:17:39)
- Reviewer: delegated independent review session round 2 — scope limited to (a) what
  round 1 changed/required and (b) confirmation that nothing else moved; reads/greps and
  read-only pwsh hashing only; **no arm, probe, pytest, or boundary tool re-execution by me**
- Review date: 2026-09-22; this report is written BEFORE the reviewer reports back and is
  pinned in `reviewer_report_r2.sha256`; the reviewer does **not** self-sign any
  `accepted` status for the card — the verdict below is returned to the parent, whose call it is

---

## 1. Verdict: **accepted_scoped**

Every required change from round 1 is implemented and independently re-measured by me
(§2). The blocker F-REV-B1P-01 is closed: the false "r1 RED stdout lost / final 11/1"
disclosure is retracted, corrected, and superseded-retained at every carrier I could
locate, and the corrected location map is now right (ruling (i), §4). The one side-effect
of the fix — a single disclosed freeze-pin divergence caused by round 1's own
F-REV-B1P-03 docstring requirement — does **not** block (ruling (ii), §5). One cosmetic
quote-accuracy defect was found (F-REV-B1P-R2-01); it is non-blocking. Scope conditions
are in §7.

---

## 2. Findings (numbered; each states what I recomputed myself)

### F-REV-B1P-R2-01 (COSMETIC, quote accuracy) — R7-2 item 7 is verbatim except one word

SRC `oracle.md` Revision r7 §R7-2 item 7 labels the SRC `reviewer_report.md` F4 excerpt
"key sentences verbatim". Whitespace-normalized word-diff of the first fenced sentence
against the live sealed report (lines 390–396): the **only** textual delta is
**"record `their` mtime" (r7) vs "record `its` mtime" (source)**; everything after the
elision marker matches exactly, and the substantive false sentence ("the file on disk is
the final 11-failed/1-passed output … I therefore cannot reproduce the disclosed r1 …")
is quoted **verbatim**. Non-blocking: the sealed source is untouched and separately
hash-pinned (`6bfd2922…`, 37224 B = round-1's pin), so verifiability is intact; the
deviation is a transcription inflection in a lead-in clause, not in any refuted
proposition. Register may note it if it wants r7's "verbatim" claim to be word-perfect.

### F-REV-B1P-R2-02 (CONFIRMED) — claim 1: SRC oracle Revision r7 is a clean suffix append

Recomputed on the CURRENT file bytes (not quoted from r2's records):

- size **57911 B**, sha256 **`6e344a208f8fc43992d339693d74c51122b505d17c368a67f5899dbd43a222dc`** ✅
- prefix proofs on the current file: **[0:39287] = `fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae`**,
  **[0:43298] = `910ca4a8109b28afb739f4a7463dbf26e13fe85c296e115d806768bcb3bd3231`**,
  **[0:47538] = `a8f192f10215642d7df2d8ace240d074f3bf50671cd4f51920b35434ebcf972d`** —
  all three equal round 1's pins (r1 report §4.1: `fadf8a5e…`, `910ca4a8…`; §4.2 r6
  post-state `a8f192f1…`) ⇒ **r1–r6 byte ranges unbroken** ✅
- byte-level scan (not UTF-8 char index — the file has 447 non-ASCII bytes before the
  marker, so a decoded-string `IndexOf` reports 47198 and is a **measurement artifact**;
  future reviewers should scan bytes): `## Revision r7` occurs **exactly once**, at byte
  offset **47539 = 47538 + 1**, byte[47538] = `\n` ✅ (r2's claim @47539 confirmed in the
  same 0-based convention round 1 used for r5/r6)
- §R7-2 carries the global `superseded_reason: "refuted by reviewer F-REV-B1P-01 with
  byte evidence"` and quotes **7 carriers**; I extracted all 7 fenced blocks and
  substring-matched each (whitespace-normalized) against the live carriers: blocks 1–4 ∈
  this card's frozen `oracle.md` (§1/§2/§3.4/§4) ✅, block 5 ∈ `decision.md §F4` ✅,
  block 6 ∈ `handoff.json findings.F4.unclosable_historical_gap` ✅ (byte-identical to
  the text now retained under `…__superseded.original_text_verbatim`), block 7 ∈ SRC
  `reviewer_report.md` — see F-REV-B1P-R2-01 (one-word delta). The two carriers found
  later by r2's addendum scan (evidence/README, recovery/README — the brief's "two new
  sites") are **not** inside R7-2; they are handled exactly as expected: evidence/README
  disclosed + superseded by reference (decision §r2 + handoff `superseded_statements`),
  recovery/README corrected in place with old text preserved verbatim (see R2-05 below)
  ✅
- §R7-3 present and states the location-measurement correction ("absent from this
  oracle's pre-r7 body, from SRC `decision.md` and from SRC `handoff.json` … corrects
  the review's location note by measurement") ✅ — independently confirmed, see R2-03
- §R7-1 states the corrected gap (r1 test file only), §R7-4 disclaims F6/F1/F2/F3/F5
  changes ✅; `r2_09_post_append_verification.json`: `all_checks_pass: true`,
  `all_six_prefixes_match`, `marker_counts_exactly_one_each` (its content consistent with
  my own recomputation above; manifest hash re-verified)

### F-REV-B1P-R2-03 (CONFIRMED — location dispute adjudicated in r2's favour; ruling (i) in §4)

I grepped/decided the dispute myself, on the CURRENT bytes:

- **SRC `oracle.md` pre-r7 body (bytes 0–47537):** contains **none** of `58863ffb`,
  `final 11`, `b1_unfixed.stdout`, `unclosable`, `recreated`, `any later card`. Its only
  `overwrit` hit is line 483: "the r1 RED stdout is **not** overwritten" — and R2-4
  (line 474ff) says `before/b1_unfixed.*` "is preserved as the r1 RED run's raw stdout …
  the r1 RED stdout is **not** overwritten". **Both true.** ✅
- **SRC `decision.md`:** line 158 "the r1 RED stdout is preserved un-overwritten" — true ✅
- **SRC `handoff.json`:** line 110 "The r1 RED stdout is preserved and was NOT
  overwritten by the r2 run" — true ✅ (matches B1's sealed handoff as quoted by round 1)
- **Origin of the false text:** SRC `reviewer_report.md` lines 388–401, read directly:
  "while the file on disk is the final 11-failed/1-passed output … I therefore cannot
  reproduce the disclosed r1 … the r1 artifact … was overwritten rather than preserved,
  contrary to `handoff.json`'s …" — sealed, hash `6bfd2922…` = round-1's pin ✅
- **Conclusion:** round 1's F-REV-B1P-01 location note ("SRC oracle §2 F4 / §3.4 / §4")
  **does not reproduce** — those false sentences live in **this card's** frozen `oracle.md`
  (§1/§2/§3.4/§4), not SRC's. r2's `r2_06_false_claim_locations.json` (whitespace-
  normalized; `src_oracle_md: {}`, `src_oracle_mentions_b1_unfixed_stdout: []`) matches my
  independent scan. Corrected erratum scope: §4 ruling (i).

### F-REV-B1P-R2-04 (CONFIRMED) — claim 3: F4 correction states the full provenance truth

`decision.md §r2.1` (read in full) and `handoff.json findings.F4` (parsed as JSON) now
state: surviving `58863ffb…` = r1's 10/2 RED stdout with **UTF-16LE+BOM**, summary
`10 failed, 2 passed in 8.18s`, no `11 failed, 1 passed` anywhere; git **single commit
`980c9b7a`** (blob = HEAD = working bytes, never an 11/1 state since 21:16:24);
provenance **mtime 21:15:12 / stderr 21:14:45 / r2 warrant 21:15:35**; **B1 handoff:137
`red_r1` failed 10 / passed 2**, `:198 red_r1_stdout`, `:110` preservation claim TRUE;
failure-block line refs **268, 296, 323, 348, 372, 407, 438, 460** (r1 test-file refs,
+6 = r2-era as round 1 measured); genuine 11/1 outputs = `b1_unfixed_r2/r3` ✅. The
original false claim is retained byte-for-byte under
`handoff.json findings.F4.unclosable_historical_gap__superseded.original_text_verbatim`
(+ `disposition__superseded`), and REM-43 is re-scoped in both files
(`rem43_rescope_r2`: PROTOCOL closed; historical gap = **r1 test file only, 18236 B /
`e6c0949c…`**; "No unclosable-stdout claim stands anywhere in this record") ✅.

### F-REV-B1P-R2-05 (CONFIRMED) — claims 2/6: the two README carriers + F6 wording + F-B1P-04/05 + scope notes

- **`evidence/README.md`**: false text still at L5 and L23–30 (read); file **2406 B /
  `737e2b18…`** = freeze entry `my_evidence_readme` **and** `evidence/SHA256SUMS.txt`
  (31-entry manifest, hash `0a4157f5…` = binding r1 pin; contains the `737e2b18` pin) ⇒
  **pinned → not edited, disclosed + superseded by reference (decision §r2 full-carrier
  addendum + handoff `superseded_statements` entry with line ranges + SRC r7 §R7-3
  context)** ✅ as claimed
- **`recovery/README.md`**: not in freeze.json (I checked: zero recovery entries) ⇒
  unpinned; corrected in place (mtime 11:51:42; new 3240 B / `ff08665f…` = binding
  `r2_pins` entry); old wording preserved **verbatim** inside at L40–48 under
  `superseded_reason: refuted by reviewer F-REV-B1P-01 with byte evidence` with the r1
  bytes recorded (`2008 / 6fe88d7b…` in `r1_pins_superseded_for`) — and the preserved
  quote matches the pre-edit scan fragment in `r2_14` (written 11:50:45, i.e. BEFORE the
  11:51:42 edit, so r2_14 saw the r1 bytes) ✅
- **F6 wording**: `decision.md §r2.2` and `handoff.json findings.F6.divergence` both
  carry the procedure-domain sentence — 中文句 present verbatim in both (grep:
  `不重算任意改写 ⇒ receipt ACCEPTED / forecast REJECTED；F6 原测量 = 改写+一致重算 …
  ⇒ both ACCEPTED，本卡未复测该变体`), plus English gloss; old over-claim retained under
  `divergence__superseded.original_text_verbatim` ✅; `erratum_ruling` = "NO erratum to
  B1's F6 … B1 stays sealed" ✅; `clarification_for_register` present with the one-line
  clarification text for the parent register ✅. I also re-read SRC
  `reviewer/scratch/probe_attest.py:225–231` directly: rewrite **then**
  `canonical_sha256({k: v … if k != "result_sha256"})` with the "fully-informed
  attacker" comment — F6's rewrite+consistent-recompute procedure confirmed at source
  (consistent with round 1's §3 ruling; r2_05's quoted sources match the live files) ✅
- **F-B1P-04**: `handoff.json r2.freeze_ordering_disclosure_F_REV_B1P_04` present with
  the mtime+prose disclosure and the §3.5 future-policy pointer ✅ (no action, as
  commissioned)
- **F-B1P-05**: `scratch/make_changes_diff.py` L70 boundary comment now cites
  `evidence/final_integrity_check_v2.stdout.txt: 14/14 ok` + the two r2 re-checks ✅;
  regenerated `changes.diff` header shows `_v2` and "Revisions r5 + r6 + r7" ✅
- **scope notes**: `handoff.json r2.scope_notes_review_section_6` registered with keys
  `rem_40_44_closure` (parent/owner register; REM-43 = protocol closed + r1 test file
  only), `e21_implementation` (separate product card), `b1_promotion_batch2` (owner
  decision) ✅; mirrored in `decision.md §r2.6` ✅

### F-REV-B1P-R2-06 (CONFIRMED) — claim 5: probe docstring fix + the chain consequence

- Live `scratch/probe_e21_binding.py` L19 = "(b) the original value restored — a
  control, NOT a recompute (oracle §3.3)." ✅ (read); frozen copy
  `evidence/r2/probe_e21_binding.py.frozen_pre_r2_5c9f4508.py` re-hashed by me =
  **10365 B / `5c9f4508…` = freeze entry `my_probe_e21`** byte-exact ✅
- `r2_10_probe_docstring_fix.json`: `all_checks_pass: true`, old/new line strings exact,
  `no_other_byte_changed: true`, suffix-anchor identity, r2 state 10383 B / `5f53f5bb…`
  (live file re-hashed by me = `5f53f5bb…` 10383 B ✅); manifest hash re-verified
- `r2_11_*post_r7_prefixefix.json`: rc file = `0`, **`all_ok: true`, 14/14 checks** —
  and I re-hashed it: **byte-identical** to r1's
  `evidence/final_integrity_check_v2.stdout.txt` (both `2a3c4c3a…`, 4270 B) ✅
- `r2_12_*post_docstring_fix.json`: rc file = `1`, 14 checks (same key set as r2_11),
  `failures = ["freeze_chain_verifies"]` **exactly one**, its sole detail entry
  `my_probe_e21: live 5f53f5bb… != 5c9f4508…`; the **other 13 checks ok**, including
  `production_git_porcelain_empty` (rc 0, empty), `iso_fixed_product_files_unchanged`
  (4 anchors), `production_anchors_unchanged` (4 anchors), both 10-field AST checks,
  `runtime_record_from_probe_is_exactly_10`, `b1_frozen_files_unchanged`,
  `production_trust_file_still_absent`, the r5/r6 marker/prefix checks ✅
- Disclosures present in `decision.md §r2.3` and
  `handoff.json r2.freeze_chain_disclosure_r2`: "the ONE deliberate freeze-pin
  divergence", restore-offer for the owner ✅. Ruling: §5.

### F-REV-B1P-R2-07 (CONFIRMED) — claim 7: nothing else moved

- **`binding.json r2_rebinding`:** keys `r2_pins` (**17**), `r1_pins_superseded_for`
  (**7** entries = exactly the r1-pinned files whose bytes legitimately changed:
  decision, handoff, changes.diff, make_changes_diff, probe, SRC oracle post-r6,
  recovery/README), `superseded_binding_state` (r1 binding `10789 / dd11d853…` recorded
  + `open_disclosures_item_superseded` verbatim), `reverified_unchanged_after_r2`,
  `integrity_after_r2`, `status` = not self-signed (handoff `status: review_pending`,
  `implementer_self_acceptance: false`) ✅. **I re-hashed all 17 `r2_pins` against the
  live files: 17/17 match (bytes + sha256), 0 mismatches** ✅
- **`evidence/r2/SHA256SUMS_r2.txt`:** **23 entries** (covers every file in `evidence/r2/`
  except itself — I enumerated the directory: 24 files) ✅; **I re-hashed 5 of them**
  (L3 `r2_01`, L11 `r2_06`, L15 `r2_10`, L19 `r2_12`, L23 `r2_14`): **5/5 match,
  0 mismatches** ✅
- **This card's frozen pins vs round 1** (re-hashed by me; compared to freeze.json /
  binding r1 pins which round 1 re-verified): `oracle.md` **19928 / `9d5a09a6…`** =
  freeze `my_oracle_md` ✅; `freeze.json` **20308 / `e593931b…`** = binding
  `my_attempt_pinned.freeze.json` ✅; node `test_r13_equiv_rem41.py` **5604 /
  `6aa0f1a8…`** = freeze ✅ (round-1 §4.2 pin); `conftest.py` **771 / `f9939e4f…`** =
  freeze ✅; `runner/run_arm.ps1` **1882 / `ec5d70a3…`** = freeze ✅
- **Full freeze-vs-live sweep (my own, all 24 entries):** exactly **2** naive full-file
  mismatches and both are explained: (a) `src_oracle_pre_r5` — a **prefix-pin** entry
  (pins the pre-r5 state; its 47538-byte prefix re-hashes to `a8f192f1…` on the current
  post-r7 file ✅ — this is why `r2_11` shows the chain OK at r7 state); (b)
  `my_probe_e21` — the disclosed docstring divergence (ruling §5). **No other freeze entry
  moved** ✅. Binding `my_attempt_pinned` + `evidence_key_outputs` (11 outputs) vs live:
  mismatches = exactly the 7 superseded-listed files; every other pin (oracle, commands,
  node, conftest, runner, both check tools, m6 proofs, r5/r6 revisions, SHA256SUMS)
  matches ✅
- **Nothing undeclared touched inside the attempt:** mtime scan ≥ 11:17:55 (round-1
  report write) returns **exactly the declared r2 set** — `scratch/r2_*.py` (5) +
  `oracle_revision_r7.md` + `append_oracle_r7.stdout.json`, `probe_e21_binding.py`,
  `make_changes_diff.py`, `decision.md`, `recovery/README.md`, `changes.diff`,
  `handoff.json`, `binding.json`, `evidence/r2/**`, `reviewer_report.md.sha256` — 39
  files (counted from my scan), none undeclared ✅. **No arm/probe re-run:** all `evidence/arm*` and
  `evidence/probe_e21.*` labels keep their r1 mtimes (10:48:31–10:50:10), no new
  arm/probe labels exist ✅
- **SRC read-only except the commissioned append:** recursive mtime scan ≥ 2026-09-22 of
  the whole SRC attempt returns **exactly one file: `oracle.md` (57911 B, 11:36:18)** ✅;
  SRC `reviewer_report.md` re-hashed = **`6bfd2922…` 37224 B** (round-1 pin, sealed
  untouched); SRC `handoff.json`/`decision.md`/`binding.json` are absent from that scan
  (round 1 measured their mtimes at 2026-09-21) ✅
- **Production / git (read-only, my own commands):** `git status --porcelain
  --untracked-files=all -- scripts tests config artifacts` → rc 0, **EMPTY** ✅;
  `git log -1` still `6f74b056` (2026-09-22 09:58:58 — no commit in the attempt or r2
  windows); reflog top-5 = commit entries only (no checkout/reset/stash) ⇒ **zero git
  writes** ✅; trust file absence re-confirmed via `r2_12.production_trust_file_still_absent`
  ok (my own anchor re-hash not repeated — see §6)
- **F1/F2/F3/F5 untouched:** `decision.md` read end-to-end — the F1/REM-40, F2/REM-41,
  F3/REM-42, F5/REM-44 sections are unchanged in content (all r2 material is confined to
  the appended `## r2`); in `handoff.json`, no r2 marker appears in the F1/F2/F3/F5
  blocks and `r1_pins_superseded_for` declares changes only to F4/F6 + appended fields
  (byte-level diff impossible — see §6) ✅ (content-level)

---

## 3. What round 1 required vs what landed (checklist)

| Round-1 required change (F-REV-B1P-01 #1–4 + F-REV-B1P-02/03/04/05) | Status | Evidence I re-measured |
|---|---|---|
| #1 append-only SRC oracle revision restating the gap + prefix proof | ✅ | R7 + my three prefix hashes (R2-02) |
| #2 correct `decision.md §F4` + `handoff.json F4` (own deliverables) | ✅ | §r2.1 / F4 corrected + `__superseded` verbatim (R2-04) |
| #3 register erratum for sealed SRC reviewer F4 sentence | ✅ registered as owner/parent action (not written by this card — correct boundary) | `decision.md §r2.1` "Register actions deliberately NOT taken here"; `handoff r2.findings.F-REV-B1P-01.register_actions_owner` |
| #4 re-scope REM-43 (protocol closed; gap = test file only) | ✅ | `rem43_rescope_r2` + `decision.md §r2.1` (R2-04) |
| F-REV-B1P-02 F6 procedure-domain reword + optional clarification | ✅ | `§r2.2` + `F6.divergence` + `clarification_for_register` (R2-05) |
| F-REV-B1P-03 probe docstring fix ("no re-run needed") | ✅ no re-run; fix landed with byte-history proof | R2-06 |
| F-REV-B1P-04 ordering disclosure carried | ✅ | `freeze_ordering_disclosure_F_REV_B1P_04` |
| F-REV-B1P-05 `changes.diff` comment → `_v2` | ✅ | `make_changes_diff.py` L70 + regenerated header |

---

## 4. RULING (i) — corrected erratum scope (the location dispute)

**I measured it myself; r2 is right and round 1's location note was wrong.**

**False-text carriers (the sentences asserting "r1 RED stdout lost / surviving file is
the final 11/1 / unclosable") — 8 sites:**

1. **SRC `reviewer_report.md` F4, lines 388–401** — the origin; **sealed**; needs the
   register erratum/annotation = **owner/parent action** (round-1 required correction #3;
   B1's attempt stays sealed).
2. **This card's frozen `oracle.md` §1 / §2 / §3.4 / §4** — freeze-pinned; cannot be
   edited without destroying F5; superseded by SRC r7 §R7-2 (items 1–4, verbatim) +
   `decision.md §r2`.
3. **This card's `decision.md §F4`** — kept byte-for-byte in place; superseded by
   `decision.md §r2` (+ R7-2 item 5 verbatim).
4. **This card's `handoff.json findings.F4.unclosable_historical_gap`** (and the
   `steps_not_applicable` "impossible; unclosable" item) — retained verbatim under
   `…__superseded` / listed in `r2.superseded_statements` (+ R7-2 item 6 verbatim).
5. **`evidence/README.md` L5 and L23–30** — freeze-pinned + SHA256SUMS-pinned; **not
   edited**; disclosed and superseded by reference in `decision.md §r2` (full-carrier
   addendum), `handoff.superseded_statements`, and SRC r7's corrected restatement.
6. **`recovery/README.md` L29–35 (r1 state)** — unpinned; **corrected in place**, old
   wording preserved verbatim inside the file (L40–48) with r1 bytes recorded
   (`2008 / 6fe88d7b…`).
7. **`binding.json open_disclosures` item** — retained in place; superseded with verbatim
   retention in `r2_rebinding.superseded_binding_state.open_disclosures_item_superseded`.
8. **`changes.diff` diff-context echoes** — generated artifact; regenerated; carries both
   old (as context) and new text.

**Exonerated (do NOT carry the false text; no erratum owed to them):**

- **SRC `oracle.md` pre-r7 body** — my byte-scan: no `58863ffb`, no "final 11", no
  `b1_unfixed.stdout`, no `unclosable`; R2-4 explicitly says the r1 RED stdout is
  **preserved / not overwritten** (true). Round-1's "SRC oracle §2 F4 / §3.4 / §4"
  attribution does not reproduce — those sentences live in **this card's** oracle.
- **SRC `decision.md`** (L158 "preserved un-overwritten") — true.
- **SRC `handoff.json`** (L110 "preserved and was NOT overwritten") — true.
- Round 1's F-REV-B1P-01 **substance stands** (the false claim WAS frozen into the
  closure record); only the carrier map is corrected as above. The erratum register row
  is owed to the sealed SRC reviewer report (#1), not to SRC's oracle/decision/handoff.

---

## 5. RULING (ii) — the probe-docstring chain deviation does NOT block acceptance

**Ruling: NOT a blocker; accept with the single stale pin disclosed (as r2 discloses it).**

Reasoning, both sides:

1. **The fix implements round 1's own finding.** F-REV-B1P-03 required the docstring
   sentence be fixed; a known-false sentence should not remain in a frozen-pinned file.
   Blocking the card on the *consequence* of doing the required fix would be
   self-contradictory: the only non-disclosing way to keep the chain green would be to
   leave the false sentence (which round 1 rejected), to edit `freeze.json` (which would
   break the chain far worse), or to delete the probe (unfounded). Round 1 itself said
   "fix in any future reissue … no re-run needed" — the fix was always sanctioned; r2
   merely pulled it forward into a record-only round and disclosed it.
2. **The deviation is exactly one freeze entry, fully evidenced and reversible.**
   `r2_12` proves the sole failing check is `freeze_chain_verifies` with the sole detail
   `my_probe_e21 live 5f53f5bb != 5c9f4508`; the other **13/14** checks pass (production
   porcelain, 4+4 anchors, both 10-field AST checks, runtime record, B1 frozen pins,
   trust-file absence). `r2_10` proves the delta is docstring-only (byte-identity of
   prefix/suffix, AST-parse preserved) — no executed evidence moved
   (`evidence/probe_e21.*` + `SHA256SUMS.txt` untouched). `r2_11` proves that at
   pinned-bytes state the chain is 14/14 and **byte-identical** to r1's final
   integrity output (`2a3c4c3a…` — I re-hashed both). The original bytes are preserved
   byte-exact (`5c9f4508…` copy re-hashed by me) with an explicit restore offer.
3. **What the stale pin does and does not mean.** The chain's purpose (F5) is to prove
   the *pre-run* expectation-bearing state; `my_probe_e21` still proves that state via
   the prefix/hash history — what is lost is only "the live file currently equals its
   freeze pin", which r2 reports honestly as rc 1 rather than hiding. A future boundary
   run will be red on this one check until the owner chooses fix-kept (re-pin/rebuild at
   the owner's discretion) or rollback (copy on file). That choice is exactly the one
   r2 hands to the owner; it is a disclosed, single-entry, owner-reversible condition —
   not a false statement and not an evidence-integrity breach.

Dissent noted for the record: a strict reading ("freeze_chain_verifies must be green at
acceptance") would block; I find that reading untenable for the reason in point 1 and
would resolve it by making the owner's fix-kept-vs-rollback choice an explicit scope
condition (§7) instead of a blocker.

---

## 6. Unverified / out of scope for this round

1. **No tool was re-executed by me** — no arm, no probe, no pytest, no
   `final_integrity_check*`; `r2_11`/`r2_12` are trusted as pinned raw records (hashes
   re-verified, rc files read: `0` and `1`), not re-run.
2. **Production anchor re-hash not repeated by me**: zero-write rests on my own empty
   porcelain (`-- scripts tests config artifacts --untracked-files=all`) + r2_11/r2_12's
   `production_anchors_unchanged`/`iso_fixed_product_files_unchanged` ok; round 1
   re-hashed the anchors directly.
3. **`handoff.json` F1/F2/F3/F5 blocks: no byte-level r1 diff** — the file was edited in
   place (r1 bytes `19073 / 4460c91e…` not retained anywhere); verified structurally
   (JSON parses; no r2 markers in those blocks; `r1_pins_superseded_for` scopes the
   edits). Same for `decision.md` (content-level only; r1 bytes gone by design of the
   append).
4. **r1 bytes of `recovery/README.md` (`2008 / 6fe88d7b…`) and of pre-r2
   `binding.json` (`10789 / dd11d853…`)** are no longer on disk — recorded hashes only;
   the recovery text's verbatim retention is corroborated by `r2_14`'s pre-edit scan and
   the in-file quote, not by a re-hash of the original bytes.
5. **r1 test-file (18236 B / `e6c0949c…`) absence not re-scanned** — accepted from
   round 1's 1294-unreachable-blob scan + r2_02b/c (manifest-verified); other recovery
   routes remain unexhausted exactly as round 1 §5.3 scoped.
6. **`changes.diff` (206219 B) header/section-1-head verified, body not read
   line-by-line**; **SRC `iso/**` trees not per-file re-hashed this round** (covered by
   r2_13's anchor checks + round 1's sweep).
7. **`evidence/r2/r2_01*, r2_02*, r2_03, r2_04, r2_07, r2_08`** contents spot-read via
   manifest + r2_09 cross-check only; their underlying facts (stdout decode, git history,
   provenance mtimes) were independently measured by **round 1** and are not re-derived
   here (round-1 report §2 F-REV-B1P-01 items 1–6).
8. F7/REM-02, I-08-C, E21 implementation, batch-2 promotion, register writes — out of
   scope, untouched, not adjudicated.

---

## 7. Scope notes (apply to this verdict regardless of disposition)

- **REM-40…44 register closure = parent/owner register update.** With the corrected
  scope: REM-43 may be recorded as **protocol ✅ closed; historical gap = the r1 test
  file (18236 B / `e6c0949c…`) only**; the register erratum for the **sealed SRC
  reviewer report F4** sentence (ruling (i), carrier #1) is likewise the owner's — and
  SRC's oracle/decision/handoff need no erratum (exonerated).
- **F6: clarification, NOT an erratum**, for the parent's plan register (text under
  `handoff.json findings.F6.clarification_for_register`); B1 stays sealed.
- **E21 implementation = separate product card**; this card is read-only on product.
- **Batch-2 promotion = owner decision**; no `iso/fixed/rf/scripts/**` byte proposed or
  authorized here.
- **Single stale probe-pin disclosed**: `freeze.json my_probe_e21` live `5f53f5bb…` !=
  pinned `5c9f4508…` after the commissioned docstring fix; restoration copy on file at
  `evidence/r2/probe_e21_binding.py.frozen_pre_r2_5c9f4508.py` (byte-exact, re-hashed by
  me); owner chooses fix-kept (re-pin) vs rollback (ruling (ii)).
- **r1 test file = the only permanent gap** (within round 1's scanned domains §4.4/§5.3);
  the r1 RED stdout survives and is auditable (`58863ffb…`, UTF-16LE, git `980c9b7a`).
- **Cosmetic note for the register**: R7-2 item 7's "verbatim" quote differs from the
  sealed source by one word ("their" vs "its") — F-REV-B1P-R2-01.
- No file outside this round's two reviewer outputs was written by me; SRC and
  production read-only; no git write of any kind; nothing self-signed.

---

## 8. REM-79 self-check on this report

- Every universal-sounding claim carries its measurement domain: current bytes as of
  2026-09-22, exact paths, byte offsets (0-based, stated), the 24-entry freeze, the
  17-entry `r2_pins`, the 23-entry `SHA256SUMS_r2`, mtime windows (≥ 2026-09-22 for
  SRC; ≥ 11:17:55 for the attempt), git HEAD/reflog as observed.
- Set claims checked in both directions: freeze-vs-live mismatches enumerated **as a
  complete set of 2** with both explained, and every one of the 22 matching entries
  stated as matching; touched-file scan compared against the declared r2 list in **both**
  directions (no undeclared file; every declared file present); carrier map lists both
  the false-text set (8) and the exonerated set (3) with the measurement for each;
  `r2_pins` verified 17/17, not sampled.
- Where a tool could mislead I said so: UTF-8 char-index vs byte-level marker scan
  (447 non-ASCII bytes); naive full-file hashing vs prefix-pin semantics; JSON parses as
  structural, not byte, verification.
- Sampled items (5 of 23 manifest entries; 7 fenced quotes of 7) are labelled as samples;
  the 17 binding pins and 24 freeze entries were **not** sampled — checked exhaustively.

*(End of round-2 review. Verdict: **accepted_scoped**; blocker F-REV-B1P-01 closed;
findings: 1 cosmetic (F-REV-B1P-R2-01), 6 confirmed; rulings: (i) corrected erratum
scope §4, (ii) probe-pin chain deviation non-blocking §5.)*
