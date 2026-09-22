## Revision r7 — F4/REM-43 gap restated: the r1 RED stdout SURVIVES; only the r1 test file is lost

**Appended by the B1-PREREQ card, correction round r2**
(`execution_runs/B1-PREREQ/a20260922-01`, record-only round) under this
oracle's §9 revision policy, on commission of independent-review finding
**F-REV-B1P-01 (BLOCKER)** in
`execution_runs/B1-PREREQ/a20260922-01/reviewer_report.md`
(25883 B, sha256 `e25a2c837009aebf4be542a89cafa13e78a0dae59b3556a7766ae8bb397376f6`).
Revisions r1–r6 are untouched: this is a pure suffix append
(`new = old + b"\n" + revision`), marker at (post-r6 bytes) + 1, with proof in
`execution_runs/B1-PREREQ/a20260922-01/scratch/append_oracle_r7.stdout.json`
and post-append re-measurement in that attempt's
`evidence/r2/r2_09_post_append_verification.json` (four reviewer-recomputed
prefixes 27697 / 31081 / 35840 / 39287 **and** the post-r5 (43298) and
post-r6 (47538) prefixes all re-match; this revision's heading marker occurs
exactly once in the post-append file).

### R7-1. Corrected F4 gap statement (every fact re-measured 2026-09-22; raw outputs in the B1-PREREQ attempt's `evidence/r2/`)

1. `before/b1_unfixed.stdout.txt` = **30580 B**, sha256
   `58863ffbca21c72350b868e9b344cc7e5a1651060f6ccb5bb1fcd3f796701335`,
   encoding UTF-16LE+BOM. Decoded: **10 `FAILED` lines / 2 `PASSED` lines**,
   summary line exactly `10 failed, 2 passed in 8.18s`, failure-block line
   refs into the r1 test file `268, 296, 323, 348, 372, 407, 438, 460`. The
   string `11 failed, 1 passed` does **not** occur anywhere in it. It **IS the
   r1 RED run's stdout** — the very warrant for this oracle's Revision r2 —
   **not** a final 11/1 output.
2. git history of that path: exactly **one** commit, `980c9b7a`
   (2026-09-21 21:16:24); its blob is the same 30580 B / `58863ffb…` bytes and
   `HEAD`'s blob equals the working-tree bytes (`git status --porcelain` clean
   for the path; `git hash-object` = `ls-tree` blob id). It is also the only
   reachable blob ever stored at that path. Since 21:16:24 there has been no
   moment when this path held an 11/1 output.
3. Provenance as the r1 run: stdout mtime 21:15:12, run stderr mtime 21:14:45
   (the attempt's first pytest run), `scratch/oracle_revision_r2.md` (the r2
   warrant) written 21:15:35 — 23 s after the stdout. B1's sealed
   `handoff.json` records at line 137
   `red_r1 = {"label": "before/b1_unfixed", ..., "failed": 10, "passed": 2, ...}`,
   at line 198 `"red_r1_stdout": "before/b1_unfixed.stdout.txt"`, and at
   line 110 "The r1 RED stdout is preserved and was NOT overwritten by the r2
   run" — that preservation claim is **TRUE**.
4. The genuine 11/1 outputs are `before/b1_unfixed_r2.stdout.txt`
   (2026-09-21 21:18) and `before/b1_unfixed_r3.stdout.txt` (21:56), each
   "11 failed, 1 passed".
5. **The only genuinely lost artifact, within the reviewer's scanned domains
   (report §4.4/§5.3): the r1 test file — 18236 B, sha256
   `e6c0949c3b7d0d9c3bad101dc90a62cb8702dc4616715adfc2227dda60aa8f75`.** It is
   absent from the working tree, absent from every reachable commit (content
   blobs ever stored at the path: 18611 B / `da3d29bf…` at `980c9b7a`, then
   20631 B / `636b43c8…` at `HEAD`), and absent by size from all 1294
   reflog-unreachable blobs the reviewer scanned. Other recovery routes (editor
   backups, pack promisor partials, other clones' worktrees) were declared
   unexhausted by the reviewer (§5.3).
6. **REM-43 re-scope:** the protocol half stands **closed** (established,
   evidenced, 31-entry manifest re-verified); the historical gap is narrowed to
   the **r1 test file only**. The claim of an "unclosable permanent gap" for
   the r1 RED stdout is **withdrawn — the stdout is auditable right now**
   (byte-pinned here, in git, with line refs that match the r1 test file).

### R7-2. Superseded statements retained verbatim

`superseded_reason: "refuted by reviewer F-REV-B1P-01 with byte evidence"`.
Domain of refutation: bytes at `before/`, git objects reachable from
`HEAD`/`--unreachable`, and B1's sealed `handoff.json`, as re-measured
2026-09-22 (`B1-PREREQ/a20260922-01/evidence/r2/r2_01..r2_06*.json`). Nothing
below is deleted from its carrier; each carrier keeps its bytes and carries the
supersession pointer (B1-PREREQ `oracle.md` is frozen pre-run and therefore
keeps the false text as-is; its correction lives in that attempt's
`decision.md` §r2 and `handoff.json` r2 block).

1. B1-PREREQ `oracle.md` §1, closure check (frozen pre-run), verbatim:
   ```
   - **F4**: no `evidence/`-style raw-stdout protocol exists in SRC; the r1 RED
     stdout remains unrecoverable ⇒ open (protocol + disclosure only; the
     historical loss is **unclosable** — see §4).
   ```
   Refuted for the stdout: it is on disk at `before/b1_unfixed.stdout.txt`.
2. B1-PREREQ `oracle.md` §2 F4 (frozen pre-run), verbatim:
   ```
   - **F4 / REM-43 (LOW, evidence)** — the r1 RED stdout ("10 failed / 2 passed")
     was overwritten by a later run and the r1 test file (18236 B / `e6c0949c…`)
     is gone from disk and git ⇒ the disclosed r1 incident (the warrant for r2)
     is not independently auditable, contrary to the handoff's "preserved and
     NOT overwritten" claim. Fix: byte-preserved raw stdout for **every new**
     RED/GREEN arm under `evidence/` + record the r1 loss as a disclosed,
     **unclosable** historical gap.
   ```
   Refuted for the stdout (the handoff's preservation claim is true);
   sustained only for the r1 test file.
3. B1-PREREQ `oracle.md` §3.4 item 4 (frozen pre-run), verbatim:
   ```
   4. **Disclosed unclosable historical gap (r1):** B1's r1 RED stdout
      ("10 failed / 2 passed", warrant for oracle r2) and the r1 test file
      (`e6c0949c…`, 18236 B) were overwritten/removed before archiving and cannot
      be recreated by this or any later card; the surviving
      `before/b1_unfixed.stdout.txt` (`58863ffb…`) is the **final** 11/1 output,
      not r1's. This gap is recorded here and in `decision.md` as **open,
      disclosed, unclosable** — it is not claimed closed by this card.
   ```
   Refuted in both halves: the stdout was never overwritten and is not an 11/1
   output.
4. B1-PREREQ `oracle.md` §4 item 1 (frozen pre-run), verbatim:
   ```
   1. The r1 RED stdout / r1 test file loss (F4) — **unclosable**, disclosed.
   ```
   Refuted for the stdout; corrected scope = r1 test file only.
5. B1-PREREQ `decision.md` §F4, verbatim:
   ```
   - **Unclosable historical gap (not claimed closed):** B1's r1 RED stdout
     ("10 failed / 2 passed" — the warrant for oracle r2) and the r1 test file
     (18236 B / `e6c0949c…`) were overwritten/removed before archiving and cannot
     be recreated by this or any later card. The surviving
     `before/b1_unfixed.stdout.txt` (30580 B / `58863ffb…`, pinned in
     `freeze.json`) is the final 11/1 output, not r1's. Recorded here, in
     `oracle.md` §3.4/§4, `handoff.json`, and the register row it closes — REM-43
     closes as *protocol + disclosure*, explicitly leaving the historical loss
     open.
   ```
   Refuted; superseded by `decision.md` `## r2` (the §F4 text itself is kept).
6. B1-PREREQ `handoff.json` `findings.F4.unclosable_historical_gap`, verbatim:
   ```
   B1's r1 RED stdout ('10 failed / 2 passed', the warrant for oracle r2) and the r1 test file (18236 B / e6c0949c...) were overwritten/removed before archiving and cannot be recreated by any later card; the surviving before/b1_unfixed.stdout.txt (30580 B / 58863ffb..., pinned in freeze.json) is the final 11/1 output, not r1's. REM-43 closes the PROTOCOL half only; the loss stays open.
   ```
   Refuted; superseded by the `handoff.json` r2 block (the string itself is
   retained byte-for-byte under
   `findings.F4.unclosable_historical_gap__superseded.original_text_verbatim`).
7. SRC `reviewer_report.md` F4 (lines 386–401; sealed — origin of the wording;
   NOT edited here), key sentences verbatim:
   ```
   But the handoff/binding record their mtime as the r1 run's artifact whose content is *"10 failed / 2 passed"*, while the file on disk is the final 11-failed/1-passed output (mtime 21:15:12, `before/b1_unfixed_r3.*` written at 21:56) — and the r1 test file (18236 B / `e6c0949c…`) is no longer in the attempt directory or in git. I therefore **cannot reproduce the disclosed r1 "10 failed / 2 passed, R8 passed trivially" incident**, which is the entire stated warrant for oracle revision r2. […] the r1 artifact that would let a reviewer audit the claim was overwritten rather than preserved, contrary to `handoff.json`'s "the r1 RED stdout is preserved and NOT overwritten".
   ```
   Refuted on the bytes: the file on disk is r1's 10/2 output, and the handoff's
   preservation claim is true. Per F-REV-B1P-01 required correction #3 this
   sealed report needs an erratum/annotation in the plan's
   `REMEDIATION_REGISTER.md` — an **owner/parent register action**, recorded by
   the parent, not written by this card (B1's attempt stays sealed).

### R7-3. Where the false sentence actually lives (measured, not assumed)

Whitespace-normalized scan of the pre-r7 record
(`B1-PREREQ/a20260922-01/evidence/r2/r2_06_false_claim_locations.json`): the
false sentence is present in B1-PREREQ `oracle.md` (§1/§2/§3.4/§4 — frozen
pre-run), B1-PREREQ `decision.md` §F4, B1-PREREQ `handoff.json` F4, and SRC
`reviewer_report.md` F4; it is **absent** from this oracle's pre-r7 body, from
SRC `decision.md` and from SRC `handoff.json` — the latter two state the true
position ("the r1 RED stdout is preserved and was NOT overwritten"). This
revision therefore restates the gap scope in this oracle without contradicting
any pre-r7 byte of it, and corrects the review's location note by measurement.

### R7-4. What this revision does NOT change

No §4 case, no §3 design point, no E-code, no security expectation, no run
result, no B1 carrier file; r1–r6 byte ranges stay byte-untouched (prefix
proofs above). **No erratum to B1's F6 record** — the review's explicit ruling
(§5 of the B1-PREREQ review) is "NO erratum warranted"; the optional one-line
F6 clarification is registered by the parent in the plan register and in the
B1-PREREQ attempt's `decision.md` §r2, not here. F1/F2/F3/F5 dispositions are
unchanged (all confirmed by that review).