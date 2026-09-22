# I-14-D — INDEPENDENT REVIEWER REPORT (r7)

Card: I-14-D · attempt `a20260919-01` · review round r7 · date 2026-09-22
Predecessor: `reviewer_report_r6.md` returned `changes_required` (F-REV-R6-01/02/03, fix list = its §9).
Reads kept to the four authorized sources (r6 report §0+§9, `oracle.md` CORRECTION 7 C7.1–C7.5,
`review.md` `## r7`, `handoff_r6.json` `r7` block); every claim below was re-checked with my own
instruments (hashes, byte reconstruction, fresh harness runs, an independent redaction probe).

## 0. VERDICT

**`accepted_scoped`** — all four items of the r6 §9 fix list are registered, corrected, and
reproduced by my own instruments (domain: this verdict's scope — the r7 record fix only: the two r6
harness row lists, `oracle.md`, `review.md`, `handoff_r6.json`, their measure outputs and probe
evidence; it does NOT close, ratify, or re-adjudicate the carried findings, the declared
`registered_open` residuals, or any code question outside r7's sites).

What is verified by my instruments (§2–§6): F-REV-R6-01 is registered in **both** instruments as 4
new `registered_open` rows, each carrying marker AND 39-char credential in input and declaration,
with the C7.2 family+domain paragraph; my independent probe reproduces leak-on-narrow /
redact-on-base for all four inputs; F-REV-R6-02's two r7-owned sites are append-supersessions with
byte proofs that hold exactly (L349 byte-untouched inside the r6 prefix; C6.1 lines 649–651 inside
the pinned unchanged segment); F-REV-R6-03 is a sole 2-byte in-place cell edit, reconstructable to
the r6 pin, with old value 16 retained as superseded at every site r7 owns; my fresh harness runs
reproduce **oracle 44 cases, rc 0, pass, registered_open = 6 (confirmed 6)** and **rule table 95
rows, rc 3, verdict `negative` by design since r3** — outputs byte-identical to their pins;
generation isolation holds (r3/r4/r5 harness pins, r3–r6 tree pins, production anchor, zero
non-pyc writes under `iso/` since the r6 review); no carrier anywhere claims "rc 0" for the rule
table (domain: the three r7 carriers `oracle.md` C7.1/C7.5-block, `review.md ## r7`,
`handoff_r6.json` r7 block — grep result: each explicitly disclaims it); the carried-unaddressed
list shows no silent closure; `status: review_pending`, `verdict_expressed: false`, no self-sign.

Nothing in this verdict reverses the r6 grants already standing (the `[^\s]+` code fix closes
F-REV-R5-01 within its domain) or the r6 refusals: acceptance remains scoped as stated above.

## 1. METHOD AND DISCLOSURE (my own run artifacts)

Both harnesses were re-run by me with `<ATTEMPT>\iso\venv\Scripts\python.exe -B`,
`PYTHONDONTWRITEBYTECODE=1`, `--label r7`, against `iso/product_narrow_r6/src`, outputs to
`execution_runs/_r7_measure_20260922/`. **Disclosure:** my first attempt passed `--src` with an
absolute path and then with forward-slash relative form; because the report JSON embeds `args.src`
verbatim, those runs produced byte-different (count-identical) outputs and overwrote the two
measure files. I then reproduced the exact invocation form their pins were made with
(`--src .\iso\product_narrow_r6\src`) and both files now hash **byte-identically to the pins
recorded in `handoff_r6.json`** (oracle `1a859a5c…`, rule `405abfaa…`) — i.e. their evidence is
restored exactly and independently regenerated (domain: the two files in
`_r7_measure_20260922/`, verified by sha equality after my final run). Counts, rc, and verdicts
were identical in every run.

## 2. F-REV-R6-01 — REGISTERED (both instruments, both credentials, with domain) — VERIFIED

* **Row presence:** grep of `harness/run_i14d_oracle_r6.py` shows `R7a-line3-bare-credential`,
  `R7b-prebreak-cr`, `R7c-prebreak-vtab`, `R7d-prebreak-ff`, all kind `registered_open`
  (lines 213–232); `harness/run_rule_table_i14d_r6.py` shows `open-line3-bare-credential`,
  `open-prebreak-cr`, `open-prebreak-vtab`, `open-prebreak-ff`, all kind `registered_open`
  (lines 276–287) — 4 new rows in each, inserted after the last r6 row (proved byte-exactly in §5).
* **Both credentials in input AND declaration:** constants are `M = "SYNTHETIC_AUDIT_TOKEN"`
  (21 chars) and `S39/REVIEWER_SECRET = "ghp_ZQ7ReviewerFakeCredential0123456789"` (39 chars).
  Every one of the 4 oracle rows has input containing `S39` and `M`, and its declared residual
  containing `R + S39 + M`; every one of the 4 rule-table rows has input and `expected` both
  containing `MARKER` and `REVIEWER_SECRET` (verified by reading all 8 row tuples).
* **Independent probe (mine, not theirs):** fresh inline run of `redact_text` over the four inputs
  on both trees: on `iso/product_narrow_r6` all four outputs contain BOTH marker and credential
  (A1 → `Authorization: <redacted>\n<39>\n<marker>`, Bcr/Bvt/Bff → `Authorization: <redacted>\c t\n…`
  forms); on `iso/product_base` all four collapse to exactly `Authorization: <redacted>`. This
  matches their `scratch/r7_shape_probe.json` (2700 B, sha `9989714df0b87f7a3a2435819fec41e041b3134eb020d0a257bc527400e0b63b`
  — computed by me, matches the handoff claim) field-for-field.
* **Family + domain paragraph = C7.2:** present, naming both shapes (line-3 bare credential; control
  whitespace `\r \v \f` at the pre-break position) and carrying 域=r1/M4,r2,r3,r4,r5,r6 树持久化，
  `iso/product_base` 脱敏 ⇒ 声明开放的 base 回归, non-designed — i.e. exactly the r6 §9.1 remedy text.
* **C7.1/C7.4 domain statements and the `credential_leaks`-filtering rationale** (C7.1 final
  paragraph) are present with their scope.

## 3. F-REV-R6-02 — SAME-LINE DOMAIN, APPEND SUPERSESSION — VERIFIED

* `review.md` has an appended `## r7` section (line 372) that supersedes L349; **L349 byte-untouched**:
  `sha256(first 22100 B) = 8a2ff101b5501a9de93651ff1988fab339d76af779982cbe1c398b734fc28ae7` — equals
  the r6 pin, recomputed by me; L349's byte range (20375–20698) lies inside that prefix. File now
  26172 B / `163cb939a11da0f245823ad24bb3ad1949890c02afced41ea53308343a58f373` (= handoff claim).
* The corrected restatement carries its domain on the same line as the universal (review.md L382;
  oracle C7.3 quote), and C7.3 is appended (lines 742–748).
* **Prefix proof across the oracle append:** `sha256(first 41469 B) = 02248237e563cb68ca2c92d71f138fc827e28449907e96f888d608f5e4d52007`
  — recomputed by me, unchanged; segment `[37676, 41469) = 02645f3a091abbadfcdc1dc7c9b2ec002d0b3315105db689d1d37682643ec2a9`
  recomputed, and lines 649–651 (the C6.1 headline universal; I printed them — L649 starts with
  "`[^\s]+` closes **every character r4 or r5 closed…") lie inside it (line 649 starts at 37741,
  line 651 ends at 37976; domain: those exact line byte-ranges).
* Third carrier site `task_plan.md` Round 76 is declared the parent's file; r7 did not touch it
  (not among files with mtime newer than the r6 review, §6).

## 4. F-REV-R6-03 — 16 → 18, SOLE IN-PLACE EDIT — VERIFIED

* Cell at bytes [37674, 37676) of `oracle.md` reads `b'18'` (line 646, C6.1 table).
  Reconstruction `prefix + b"16" + suffix` over the first 41469 B reproduces the r6 pin
  `468fb300a76d00a87dab7fe94d2c64b825ce72ec03fabc00a034dc32e6501694` exactly, and both flanking
  segments hash as C7.5 claims (`[0,37674) = 287d4006…db126`, `[37676,41469) = 02645f3a…ec2a9`) ⇒
  the 16→18 cell is the **sole** in-place change of r7 inside those 41469 bytes (domain: oracle.md
  bytes [0,41469), established by reconstruction from both ends).
* `handoff_r6.json` → `responses.F-REV-R5-01.sweep_result`: `r4_class_leaking_count = 18`,
  `r4_class_leaking_count_r6_record = 16`, plus a supersession note; the r7 block's
  `old_values_retained_as_superseded` also keeps 16 (and the r6 counts 40/91 and old harness pins).
  JSON parses.
* Source of truth: `execution_runs/_r6_measure_20260922/r6_measurement.json` →
  `candidates.r4-tchar.leaking_single_chars` has **18** entries (counted by me).
* `oracle.md` C7.4 records 16 as superseded with its domain (95 printable ASCII @ pre-break, shape
  `Bo<c>t\n`, r4 tree).
* **task_plan L1991/L1994 = parent's edits, present and correct:** L1991 reads "…| **18 个**
  (F-REV-R6-03 更正：域=…；原写 16 为错…)"; L1994 reads the universal with **域 on the same line**
  ("…**只剩空格**（**域：95 个可打印 ASCII 字符 @ pre-break 位…空白字符…不在该域内且同样泄漏——见
  F-REV-R6-02；本域限定由 r6 复审提出、父代理直接落于本行**）…"). Both match the old→new the r7
  record reports; treated as the parent's worktree edits, not the implementer's write.

## 5. HARNESS RE-RUNS (mine) + GENERATION ISOLATION — VERIFIED

Fresh runs (`-B`, `PYTHONDONTWRITEBYTECODE=1`, `--src .\iso\product_narrow_r6\src`, `--label r7`):

* **Oracle: 44 cases, rc 0, verdict `pass`**, `narrow_must_failed []`, `keep_must_failed []`,
  `registered_open` = 6, `registered_open_confirmed` = all 6 (R3a, R3b, R7a–R7d); output
  `oracle_r7_harness.json` = 21452 B, sha `1a859a5c9af2a4e3f60faa5eaea018d1e2e475c26153f18dd5810925723fbe37`
  — **byte-identical to the handoff pin**.
* **Rule table: 95 rows (`entries: 95`), rc 3, verdict `negative`** — BY DESIGN since r3
  (F-REV-R6-04), `credential_leaks []`, `touched_but_should_not_be []`, `fidelity_ok true`,
  `registered_open_rows` 6, `registered_open_leaking` 6; output `rule_r7_harness.json` = 34610 B,
  sha `405abfaaae041aa9aba1d395cac25769faf03a457435320a008dcdda1ae18690` — **byte-identical to the
  handoff pin**.
* **No "rc 0" claim anywhere for the rule table** (domain: grep over `oracle.md`, `review.md`,
  `handoff_r6.json` for `rc 0`): every hit either attributes rc 0 to the oracle harness (which I
  reproduced) or explicitly disclaims it for the rule table ("claims no rc 0", "not reported as
  rc 0", "no claim of rc 0 is made").

Isolation, by reconstruction and pins:

* **r6 rows byte-untouched, insert after last r6 row:** I brute-forced a contiguous window whose
  removal reproduces the r6 pins: oracle — remove 1823 B at offset 10882 ⇒
  `8b47e0b7da821eb5342eed369c96727aae6a6d3554ff0a150aab186b73836658` (= the pin the r6 reviewer
  independently recorded, report table L246); the window is exactly the r7 comment block + 4 new
  rows, contains no r6 row id, and the surviving prefix ends on the last r6 row
  (`N5w-auth-ampersand-secret`). Rule table — remove 1699 B at offset 16133 ⇒
  `c7ea6efd5a687c4ca63a3e387c3915d6fbfb1894a52d60e278c54db25eda8bb7` (= r6 pin, r6 report L247);
  window contains all 4 new row ids, no r6 row id, prefix ends on `cred-auth-ampersand-with-key`.
  Current harness shas match the handoff claims (`85a1b064…` / `8f5feffd…`).
* **r3/r4/r5 harnesses byte-untouched:** recomputed shas equal the pins the r6 reviewer verified:
  `run_i14d_oracle.py` f7c94c60…/11043, `run_rule_table_i14d.py` 01a3187e…/19378,
  `_r4` 240d181c…/12316 and 610ce4b8…/20006, `_r5` 38a22101…/13293 and 1e51373a…/20600.
* **Tree pins unchanged:** `observability.py` r3 `a551cc45…` (= handoff_r3), r4 `15446f4d…`
  (= handoff_r4), r5 `ca13fb81…` (= handoff_r5), r6 `2f6449949c76b97c636d5d50e2ca848403116a85a1858bb9ba8f5a2808362464`
  (= handoff_r6 line 93), 43746 B.
* **Production anchor:** `scripts/model_registry.py` = `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f`
  / 26446 B, recomputed by me — unchanged; production READ-ONLY held.
* **Write-scope scan:** every file under the attempt with mtime newer than the r6 review is a
  declared r7 site (`oracle.md`, `review.md`, `handoff_r6.json`, the two r6 harnesses; plus the r6
  reviewer's own `.sha256` written 27 s after its report, and the cited scratch probe files).
  **Zero** non-`.pyc` files under `iso/` were modified since the r6 review.

## 6. CARRIED-UNADDRESSED LIST — NO SILENT CLOSURE — VERIFIED

`F-REV-R3-02/03/05/06..10`, `F-REV-R4-02`, `F-REV-R5-03..08`: grep of `review.md` shows their last
registration at L358 (the byte-untouched `## r6` section) and **no occurrence in the `## r7`
section** (lines 372–395); the `handoff_r6.json` r7 block's `responses` cover only
F-REV-R6-01..05 and make no closure claim about the older list (domain: grep hits across both
carriers — none of those ids appears after byte 22100 of review.md or anywhere in the r7 block).
They remain carried exactly as the r6 review left them. **F-REV-R6-05/C10:** correctly still open —
`review.md` L395 and `handoff_r6.json` F-REV-R6-05 both state the two C10 rows
(`R3a`/`R3b`, `open-two-token-then-wrap`/`open-quoted-two-token`) remain credential-only, and r7's
four rows close the marker gap **for their own family only**, each statement with its domain on the
same line.

## 7. FINDINGS (r7 round) — none blocking

1. **F-REV-R7-01 — INFO:** the pre-r7 bytes of `handoff_r6.json` were never pinned (the r6
   report recorded no handoff sha; grep found none), so "r6 content of that carrier untouched
   except the 16→18 line and the inserted r7 block" is verified only field-by-field and by JSON
   validity, not by reconstruction (domain: this one carrier; all other carriers have pins that I
   reproduced).
2. **F-REV-R7-02 — INFO (record nit):** the carriers' command notation `--src iso/product_narrow_r6/src`
   (forward slashes) does not reproduce the pinned measure-file bytes; the pins were produced with
   `--src .\iso\product_narrow_r6\src` (+5 JSON bytes from escaped backslashes). Counts, rc and
   verdict are identical either way; only byte-reproduction of the outputs needs the exact form
   (domain: the two files in `_r7_measure_20260922/`).
3. **F-REV-R7-03 — INFO:** `review.md ## r7` and the handoff r7 block do not restate the full
   carried list; it survives only via the untouched `## r6` section. Not a closure (§6), but a
   future reader of `## r7` alone sees a shorter carried inventory (domain: those two r7 texts).

## 8. UNVERIFIED LIST

* Pre-r7 `handoff_r6.json` bytes (F-REV-R7-01) — no pin exists to check against.
* Implementer process assertions ("r6 pins re-verified by r7 before editing", how the probe file
  was produced) — process claims; the resulting bytes and facts I did verify.
* `task_plan.md` Round 76 beyond L1991/L1994 (parent's file; outside my read list) — I verified
  only that L1991/L1994 exist and carry the corrected text with domains.
* The implementer's exact old→new text as reported to the parent (not in my read scope); I judged
  L1991/L1994 by their current content only.
* Full 152-file byte comparison of every iso tree this round — I used observability pins for
  r3–r6 + base, the production anchor, and a whole-tree mtime scan (no non-pyc writes since the
  r6 review) instead of a full re-hash.
* r1/r2-era carriers (`changes.diff`, `decision.md`, `commands.json`, …) contents — mtime shows
  untouched since the r6 review; contents not re-audited (not in the authorized read list).

## 9. HOW TO REPRODUCE THIS REVIEW

```
# §5 harness re-runs (from <ATTEMPT>)
$env:PYTHONDONTWRITEBYTECODE='1'
.\iso\venv\Scripts\python.exe -B .\harness\run_i14d_oracle_r6.py   --src .\iso\product_narrow_r6\src --label r7 --out ../../_r7_measure_20260922/oracle_r7_harness.json   # rc 0, 44 cases, pass
.\iso\venv\Scripts\python.exe -B .\harness\run_rule_table_i14d_r6.py --src .\iso\product_narrow_r6\src --label r7 --out ../../_r7_measure_20260922/rule_r7_harness.json    # rc 3, 95 rows, negative
Get-FileHash -A SHA256 ..\..\_r7_measure_20260922\*.json   # 1a859a5c… / 405abfaa… = handoff pins
# §4 oracle.md byte proofs
#   first 41469 B -> 02248237…52007; [0,37674)->287d4006…db126; [37674,37676)=="18";
#   [37676,41469)->02645f3a…ec2a9; prefix+"16"+suffix over [0,41469) -> 468fb300…1694
# §3 review.md: first 22100 B -> 8a2ff101…8ae7; L349 range (20375,20698) inside it
# §2 my probe: inline redact_text over the four inputs on product_narrow_r6 and product_base
# §5 isolation: window-removal reconstruction of 8b47e0b7… (oracle, 1823 B @10882) and
#   c7ea6efd… (rule, 1699 B @16133); sha256 of r3–r5 harnesses and iso observability.py;
#   sha256 production scripts/model_registry.py -> 9ec6529550f189a4…/26446 B
# §6 grep review.md for F-REV-R3-02|F-REV-R4-02|F-REV-R5-0[3-8]: last hit L358, none in ## r7
```

## REM-79 self-audit of this report

Every claim of the form only / all / none / whole family / zero carries its domain on the same
line (domain: this report's own universal claims — verdict scope in §0, "sole in-place change"
bounded to `oracle.md` bytes [0,41469) in §4, "no rc 0 claim" bounded to the three r7 carriers in
§5, "no closure" bounded to the grep hits named in §6, isolation claims bounded to the named pins
and the mtime scan's window, "zero non-pyc writes" bounded to `iso/` files newer than the r6
review timestamp 2026-09-22 08:29:10). Measurement claims name their instrument (hash, window
reconstruction, fresh run, or grep) and their inputs. Superseded values (16, 40/91, the old
harness pins) are referenced as superseded, not deleted. This report expresses the r7 verdict and
signs nothing of the implementer's: no carrier file was edited by me.
