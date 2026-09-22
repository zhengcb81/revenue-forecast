# Independent review — B1-PREREQ a20260922-01

- Card: **B1-PREREQ** (close B1 review F1–F5 = REM-40…44 before batch-2 promotion)
- Attempt under review: `execution_runs/B1-PREREQ/a20260922-01`
- Source attempt (SRC): `execution_runs/B1-I08C-product-fixes/a20260921-01`
- Reviewer: delegated independent review session (sampled verification; all reads targeted)
- Review date: 2026-09-22
- This report is written BEFORE the reviewer reports back; pin in `reviewer_report.sha256`.
  The reviewer does **not** self-sign any `accepted` status for the card; the verdict below
  is returned to the parent, whose call it is.

---

## 1. Verdict: **changes_required**

F1/REM-40, F2/REM-41, F3/REM-42, F5/REM-44 and every boundary claim I tested are
**confirmed by independent recomputation** (details §4). The blocker is **F4/REM-43's
disclosure half**: its central factual claim — that the surviving
`before/b1_unfixed.stdout.txt` (58863ffb…) is "the final 11/1 output, not r1's" and that
r1's "10 failed / 2 passed" stdout is an **unclosable permanent gap** — is **false on the
bytes in this repository** (Finding F-REV-B1P-01). The r1 RED stdout is present on disk and
in git. A false statement must not be frozen into the closure record, so the card cannot be
accepted as written; the required changes are narrow and do not touch F1/F2/F3/F5 or any
boundary.

Also required (non-blocking but part of the record): an F6-wording correction — the card's
"F6's 'both ACCEPTED' does not hold" over-reads a **procedure-mismatched** probe variant
(§5, my F6 ruling: **no erratum to B1's F6 is warranted**).

---

## 2. Findings

### F-REV-B1P-01 (BLOCKER, evidence record) — the F4 "unclosable r1 gap" disclosure is false: r1's RED stdout survives

Domain of this claim: bytes on disk at `SRC/before/` and blobs reachable from `HEAD` /
`--unreachable` in `C:\Users\郑曾波\Projects\revenue-forecast` git, as measured 2026-09-22
during this review.

Measured facts (each independently recomputed by me, not quoted):

1. `SRC/before/b1_unfixed.stdout.txt` = 30580 B, sha256 `58863ffbca21c72350b868e9b344cc7e5a1651060f6ccb5bb1fcd3f796701335`
   (matches the card's own freeze pin, entry `src_before_b1_unfixed_stdout`).
   Encoding UTF-16LE+BOM; decoded: **10 `FAILED` lines, 2 `PASSED` lines, summary line
   `10 failed, 2 passed in 8.18s`**. It is **not** an 11/1 output.
2. git history of that path: exactly one commit, `980c9b7a` (2026-09-21 21:16:24), blob =
   the same 30580 B / `58863ffb…` bytes; no later commit touches it, and `HEAD`/working
   tree still equals that blob. Since 21:16:24 there has therefore never been a moment when
   this path held an 11/1 output.
3. Provenance as **the r1 run**: mtime 21:15:12 with run stderr starting 21:14:45, i.e.
   the first pytest run of the attempt; `scratch/oracle_revision_r2.md` (the warrant for
   oracle r2) was written 21:15:35, 23 s later. B1's own `handoff.json` records
   `red_r1 = {label: before/b1_unfixed, failed: 10, passed: 2}` (line 137),
   `red_r1_stdout = before/b1_unfixed.stdout.txt` (line 198) and "The r1 RED stdout is
   preserved and was NOT overwritten by the r2 run" (line 110).
4. Line-number forensics tie this stdout to the **lost r1 test file**, not to the r2-era
   file: r1-run refs `268, 296, 323, 348, 372, 407, 438, 460` vs r2-run refs
   `268, 296, 323, 348, 372, 391, 413, 444, 466` — first five identical, last three differ
   by exactly **+6 lines**, consistent with a 6-line insertion after line 372 between the
   r1 file (18236 B, `e6c0949c…`) and the r2 file (18611 B, git `980c9b7a` blob
   `da3d29bf…`, 467 lines).
5. The genuine 11/1 outputs are `before/b1_unfixed_r2.stdout.txt` (21:18, "11 failed,
   1 passed") and `before/b1_unfixed_r3.stdout.txt` (21:56, "11 failed, 1 passed").
6. What is actually unrecoverable: the **r1 test file** only — 18236 B / `e6c0949c…` is
   absent from the working tree, from every reachable commit (earliest reachable blob =
   18611 B / `da3d29bf…`), and absent by size from all **1294** reflog-unreachable blobs
   scanned this session.

Where the false claim was frozen (all three copies carry it):

- SRC `oracle.md` §2 F4 and §3.4 item 4 / §4 ("the surviving
  `before/b1_unfixed.stdout.txt` (`58863ffb…`) is the **final** 11/1 output, not r1's";
  r1 stdout "cannot be recreated by this or any later card").
- This attempt's `oracle.md` §2 F4 / §3.4 item 4 (frozen pre-run).
- `decision.md` §F4 and `handoff.json.findings.F4.unclosable_historical_gap`.

Origin: the wording is inherited verbatim from SRC `reviewer_report.md` F4 lines 388–401
("the file on disk is the final 11-failed/1-passed output … I therefore cannot reproduce
the disclosed r1 '10 failed / 2 passed' incident"). The source reviewer mis-measured (or
mis-decoded the UTF-16 file); the card adopted it and certified it as re-verified, despite
its own closure-check claiming each finding was re-measured. This is the register's
"false/exaggerated record" species (cf. REM-72/REM-77).

Impact: no security expectation moves and the **protocol half** of REM-43 stands (§4 F4),
but the "permanent unclosable gap" scope is wrong — the r1 RED stdout is auditable right
now (byte-pinned, in git, line refs matching the r1 test file), and only the r1 test file
is lost. Accepting the card as written would put a refutable falsehood into the closure
record and into the parent's scope notes.

Required corrections (all append-only / register-level; nothing sealed gets edited):

1. Append-only correction to SRC `oracle.md` under its §9 convention (suggested
   `## Revision r7`) restating F4's gap as **"r1 test file (18236 B / `e6c0949c…`) lost;
   r1 RED stdout PRESERVED at `before/b1_unfixed.stdout.txt` (30580 B / `58863ffb…`,
   UTF-16LE, git `980c9b7a`, `10 failed, 2 passed`, r1-test-file line refs)"`, with prefix
   proof (current state: 47538 B / `a8f192f1…`, marker would be 47539).
2. Correct `decision.md` §F4 and `handoff.json.findings.F4` (these are this attempt's own
   unfrozen deliverables — plain correction is fine).
3. Register action for the owner: SRC `reviewer_report.md` F4's sentence "the file on disk
   is the final 11-failed/1-passed output" is refuted; it needs an erratum/annotation in
   `REMEDIATION_REGISTER.md` (owner's register; B1's attempt stays sealed).
4. Re-scope REM-43's closure: protocol ✅ closed; historical gap narrowed to the r1 test
   file (still unclosable for stdout? **no** — stdout survives; test file only).

### F-REV-B1P-02 (MEDIUM, procedure attribution) — the F6 "divergence" is a variant mismatch, and the card's conclusion sentence over-claims

Domain: `reviewer/scratch/probe_attest.py` (SRC, lines 225–231), this attempt's
`scratch/probe_e21_binding.py` (lines 225–251) and `evidence/probe_e21.stdout.txt`.

- The source reviewer's actual F6 measurement (b1) is: set `result_sha256` to an arbitrary
  value, then **immediately overwrite it with the canonical recompute**
  (`canonical_sha256({k: v … if k != "result_sha256"})`, with the code comment "a
  fully-informed attacker recomputes it, so emulate the strongest real move"), then
  `validate_forecast_output` → ACCEPTED. That is exactly F6's wording "rewriting … **and
  recomputing it consistently**".
- The card's probe variant (a) is **rewrite only, no recompute** → forecast layer REJECTED
  (`forecast result hash mismatch`, revenue_report.py:343-347 + 507-509 — code reading
  confirmed by me). Variant (b) is **restore the original value** (probe source lines
  238–244), i.e. a control, **not** the "full self-consistent recompute of every self-hash
  chain" its module docstring (line 19) claims.
- Therefore `handoff.json`/`decision.md`'s "F6's 'both ACCEPTED' does not reproduce /
  does not hold" compares two **different procedures**. F6's measured statement is not
  contradicted; the rejection of an *inconsistent* self-hash is strictly additional
  information that **strengthens** F6's disposition.

Required: reword the divergence record to carry its procedure domain (REM-79): e.g.
"unrecomputed arbitrary rewrite ⇒ receipt ACCEPTED / forecast REJECTED; F6's
rewrite+consistent-recompute variant ⇒ both ACCEPTED, not re-measured by this card".
Optionally register a clarification (not an erratum) against B1's F6 — see §5.

### F-REV-B1P-03 (LOW, probe documentation) — probe docstring misdescribes variant (b)

`scratch/probe_e21_binding.py` docstring line 19 says variant (b) = "full self-consistent
recompute of every self-hash chain"; the code restores the original value instead. The
frozen oracle §3.3 describes variant (b) as "the honest value restored ⇒ both ACCEPTED",
so **oracle and code agree** and no evidence is invalidated — only the docstring is wrong.
Fix in any future reissue of the probe; no re-run needed.

### F-REV-B1P-04 (LOW, ordering evidence) — for THIS attempt, freeze-before-run still rests on mtimes + disclosed prose

Domain: `freeze.json` content (chain verified by me) vs filesystem mtimes of
`evidence/*` this session. The hash chain proves **content integrity and entry order**;
it cannot prove `freeze.json` existed before the runs (a chain built later is
indistinguishable). Measured: final freeze build 10:48:31, first arm evidence 10:48:39;
the SRC appends (10:44) and M6 build (10:45:48) precede the final freeze — disclosed in
`decision.md` D-3 (three builds; builds 1/2 hashes `e177d719…`/`eb90c1a0…` exist only in
prose, no artifact). Expectations-bearing artifacts are content-pinned and their claims
re-verify, and the card disclosed all of this honestly; still, the freeze-vs-run ordering
for this attempt is mtime-evidenced, which is the very thing REM-44 demoted. Acceptable as
disclosed for this attempt; the new §3.5 policy binds **future** freezes. Note for the
owner: a self-timing mechanism (e.g. committing the freeze in the same operation as the
first evidence byte) is the only way to close this class.

### F-REV-B1P-05 (cosmetic) — `changes.diff` §2 header points at the burned label

Section-2 boundary comment cites `evidence/final_integrity_check.stdout.txt` (the burned,
empty, rc-1 label) instead of `evidence/final_integrity_check_v2.stdout.txt` (14/14, rc 0).
Cosmetic; `changes.diff` is a generated artifact.

---

## 3. F6-erratum ruling (asked of me explicitly)

**Ruling: NO erratum to B1's F6 record is warranted.** Optionally register a one-line
*clarification*; do not correct F6's conclusion.

Reasoning:

1. F6's sentence is procedure-qualified — "rewriting `result_sha256` to any value **and
   recomputing it consistently** leaves both … ACCEPTED" — and the source reviewer's own
   measurement code performs exactly that two-step move (`probe_attest.py:227-229`). The
   card's probe did **not** run that procedure; it ran rewrite-only (variant a) and
   restore-original (variant b). A divergence between different procedures is not a
   refutation of the original measurement.
2. Code reading confirms both behaviours are what the implementation does:
   `revenue_report.py:343-347` requires `result_sha256 == canonical_sha256(hash_payload)`
   with `hash_payload` = everything except `result_sha256` (lines 507-509) ⇒
   (i) an unrecomputed arbitrary value is REJECTED (card's variant a), and
   (ii) any value the attacker computes with that same public canonical function is
   ACCEPTED — which is precisely why `result_sha256` binds nothing externally, F6's point.
3. F6's substantive claims remain independently verified by this review: the
   record/attestation layer genuinely cannot bind the live result digest (sentinel
   fixpoint; record = 10 fields with no `result_sha256`, verified by AST on both the fixed
   tree and the frozen test, plus runtime `record_field_count: 10`), and the receipt layer
   contains no `result_sha256` check (probe: receipt ACCEPTED for an arbitrary rewrite).
   F6's disposition "no action required" therefore stands unchanged.
4. What deserves recording (clarification, not erratum): "an **unrecomputed** arbitrary
   `result_sha256` is accepted at the receipt layer but **rejected** by
   `validate_forecast_output`" — a fact F6 did not state and that makes the residual
   strictly *smaller* than F6's wording implies for careless (non-recomputing) attackers,
   while leaving the fully-informed-attacker case exactly as F6 described.

Because B1's attempt is sealed, anything recorded here goes into the register as a
clarification entry, not into `B1-I08C-product-fixes/a20260921-01/**`.

---

## 4. Claim-by-claim verification (what I recomputed myself)

### 4.1 F1 / REM-40 — **CONFIRMED**

- Recomputed on `SRC/oracle.md` bytes: total 47538 B, sha256 `a8f192f10215642d7df2d8ace240d074f3bf50671cd4f51920b35434ebcf972d` ✅.
- Prefix proofs recomputed by me: `[0:27697]` = `81af1240…`, `[0:31081]` = `60ecbca7…`,
  `[0:35840]` = `231e7976…`, `[0:39287]` = `fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae` — **all four match r1–r4 pins**; `[0:43298]`
  = `910ca4a8…` (post-r5) ✅. Marker `## Revision r5` found at byte **39288** (=39287+1),
  `## Revision r6` at **43299** (=43298+1), byte 39287/43298 = `\n`, each marker occurs
  exactly once ✅.
- 10-field truth, three routes: (a) AST of fixed-tree
  `PUBLICATION_ATTESTATION_FIELDS` — the value is a `frozenset(...)` call; parsing its
  literal argument gives **exactly the 10 named fields**, no `result_sha256`/`receipt_sha256`
  ✅; (b) AST of frozen test `ATTESTATION_FIELDS` = the same 10 ✅; (c) runtime
  `record_field_count: 10` in `evidence/probe_e21.stdout.txt` and in
  `evidence/final_integrity_check_v2.stdout.txt` ✅. Revision r5 text (appended) states the
  correction and the fixpoint reason ✅.

### 4.2 F2 / REM-41 — **CONFIRMED**

- Node + M6 bytes frozen before runs: `test_r13_equiv_rem41.py` (5604 B, `6aa0f1a8…`) is
  freeze entry `my_node_r13_equiv_rem41`; M6's 3-line bytes are verbatim in this attempt's
  oracle §3.2 and in SRC oracle Revision r6; `apply_m6.py` (freeze-pinned) asserts pre-hash
  `bc2bb4a3…` ✅.
- Raw arm evidence read byte-for-byte: arm1 **2 passed / rc 0**; arm2 **1 failed
  (`DID NOT RAISE ForecastInputError`) + 1 passed / rc 1**; arm3 **12 passed / rc 0**;
  arm4 **2 failed / rc 1** ✅ — exactly the frozen expectations for arms 1–3 and the
  disclosed deviation for arm4.
- Blind spot reproduced: the frozen 12-node file passes 12/12 on the M6 mutant (declared
  `{}` = observed `{}`), while the new node alone goes RED ⇒ 14-node declared red
  `{test_rem41_a…}` = observed ✅.
- **Arm4 control deviation**: present in the raw stdout (control fails at
  `isinstance(_record_of(ok), dict)` because the unfixed tree carries no record), disclosed
  in `handoff.json.deviations.arm4_control` and `decision.md` §F2 with the corrected
  expectation, **without** editing the node, re-running the arm, or appending to any frozen
  oracle — I searched both SRC `oracle.md` (post-r6) and this attempt's frozen
  `oracle.md`: the correction strings ("record absent", "control RED", "2 failed") are
  **absent** from both ✅.
- SRC Revision r6: appended (marker 43299), prefix untouched proof recomputed ✅; text
  contains the M6 table row, the declared 14-node red set `{test_rem41_a…}` and the node
  pointer ✅.
- Mutant integrity, recomputed by me: `scratch/mutations/M6/rf` vs `SRC/iso/fixed/rf`
  (excluding `__pycache__`: 174 vs 174 files) — **exactly one** file differs,
  `scripts/revenue_publication.py`, 25026 B / `ffc782ac…` (matches `m6_build.stdout.txt`),
  M6 marker present only in the mutant; SRC tree still `bc2bb4a3…` ✅. (Their
  `m6_delta_proof.json` counts 197 vs 197 files — same conclusion; the count differs only
  because `__pycache__` is included there. Domain noted.)

### 4.3 F3 / REM-42 — **CONFIRMED as documented-not-bindable-here**

`evidence/probe_e21.stdout.txt` (rc 0) shows, with executed-source hashes equal to the
freeze pins: Q1 loader output has `issuer_present_in_loader_output: false`,
`key_id_present_in_loader_output: false`, 32-hex keys → `bytes`, while the trust-file entry
keys are `[fingerprint, issuer, key_id, name, public_key]` ✅; Q2 issuer rename to
`revenue-forecast/evil` **ACCEPTED at `validate_publication_receipt` AND at
`validate_forecast_output`**, key_id rename **ACCEPTED** (receipt), negative control
(corrupt signature) **REJECTED** with `attestation_signature_invalid … (E14)` ✅.
Unbindable-3-causes and what-would-bind-3-steps are in `decision.md` F3 (lines ~159–191)
with exact code sites (`contracts/evidence.py:242-267`, issuance + consumption comparison
sites, absent trust anchor) ✅. Disposition (documented, evidenced, non-silent; E21
implementation = product card) is an acceptable closure for REM-42 **as a documentation
closure** — subject to the owner confirming they want the product card scheduled rather
than the finding held open.

### 4.4 F4 / REM-43 — **protocol half CONFIRMED; disclosure half REFUTED (F-REV-B1P-01)**

- Protocol: frozen in this attempt's oracle §3.4 before runs; `runner/run_arm.ps1` enforces
  write-once labels (collision → **exit 99**, verified in source lines 21–26) and captures
  raw stdout/stderr/rc via `cmd /c` redirection ✅;
  `evidence/SHA256SUMS.txt` has **31 entries** and I recomputed **every** hash — 0
  mismatches ✅. Ten labels as listed; both `final_integrity_check` (burned) and `_v2`
  present and distinct ✅.
- r1 disclosure wording: **false** — see F-REV-B1P-01. **No one fabricated a reconstructed
  r1 stdout**: the only place the string "10 failed" appears in this attempt's evidence is
  `evidence/README.md` quoting the claim; no synthetic r1 artifact exists. The problem is
  the opposite of fabrication: an existing authentic artifact is misdescribed as lost.

### 4.5 F5 / REM-44 — **CONFIRMED**

- `freeze.json`: 24 entries, declared 24. I re-derived the whole chain independently:
  canonical JSON = `json.dumps(entry minus entry_sha256, sort_keys=True, separators=(',',':'))`;
  recomputed all 24 `entry_sha256`, all 24 `prev_entry_sha256` links (genesis all-zeros),
  and the chain head = `8f3d35ccaf503cb918a9b5881f3f401212f7920b1869457677b771bab82d9b4b`
  (matches declaration) ✅. (The task asked for 2–3 links; I recomputed all of them.)
- I re-hashed **all 24 pinned files**: 0 mismatches — including SRC `reviewer_report.md`
  `6bfd2922…`, frozen `test_b1_rem.py` `636b43c8…`, both `before/` artifacts, the four
  fixed-tree product files, and this attempt's oracle/node/runner/commands/probe/tools ✅.
- Post-run re-verification: `evidence/final_integrity_check_v2.stdout.txt` — rc 0,
  `all_ok: true`, **14/14 checks** including `production_git_porcelain_empty` (rc 0,
  empty stdout), `iso_fixed_product_files_unchanged` (4 anchors), `production_anchors_unchanged`
  (4 anchors), `fixed_tree_…_is_exactly_10`, `frozen_test_…_is_exactly_10`,
  `freeze_chain_verifies: ok=true`, `production_trust_file_still_absent` ✅.
- AST-defect disclosure confirmed: burned label `final_integrity_check` has rc 1, empty
  stdout, and stderr = verbatim traceback ending `ValueError: malformed node or string on
  line 154: <ast.Call …>` (i.e. `ast.literal_eval` on the `frozenset(...)` call — the same
  defect class I hit myself when naively `literal_eval`-ing that constant); successor ran
  under the NEW label `_v2`; both label triples exist once each and are pinned in
  `SHA256SUMS.txt` — **no overwrite** ✅. `decision.md` §F5 + `binding.json` pinning
  `decision.md` (hash `1a295207f70e4a5fbe3e9aa97ca58f8e1cb11e27896084d6cfcb6fbe0c6ba480`
  = on-disk) ✅.

### 4.6 F6 divergence evidence — measured as claimed; interpretation corrected in F-REV-B1P-02

Probe raw output shows exactly what the card reports (receipt ACCEPTED / forecast REJECTED
for the unrecomputed rewrite; both ACCEPTED for the restored control; code sites
`revenue_report.py:343-347, 507-509` verified by reading them). My ruling on the erratum
question is §5 above.

### 4.7 Boundaries — **CONFIRMED**

Domain: mtimes/hashes measured 2026-09-22 during this review; git state read-only.

- **Product zero writes**: `git status --porcelain --untracked-files=all -- scripts tests
  config artifacts` → rc 0, **empty** (run by me); the four production anchors re-hashed by
  me all match `final_integrity_check_v2` (`evidence.py 054e364a…`, `revenue_core.py
  1821fd2a…`, `revenue_publication.py 183803bb…`, `revenue_report.py a85fb484…`);
  `config/trusted_signer_public_keys.json` still ABSENT ✅; the four fixed-tree anchors
  re-hashed via the freeze chain (`8a761498…`, `bc2bb4a3…`, `212f0059…`, `054e364a…`) ✅.
- **B1 attempt writes**: recursive mtime scan of the whole SRC attempt (including both iso
  trees) for `LastWriteTime >= 2026-09-22` returns **exactly one file: `oracle.md`
  (47538 B)** — the two commissioned appends. `reviewer_report.md`, `test_b1_rem.py`,
  `binding.json`, `handoff.json`, `decision.md`, `before/`, `after/`, `reviewer/`,
  `scratch/` all still carry 2026-09-21 mtimes and the pinned ones re-hash equal ✅.
- **No git writes by the attempt**: last commit before the attempt window is `6f74b056`
  (2026-09-22 09:58:58); the attempt's files were written 10:35–10:57 and no commit exists
  in that window; reflog shows commit entries only (no checkout/reset/stash) ✅. (Domain:
  this repository's `HEAD` history + reflog as of this review.)
- **Frozen before/ untouched**: both `before/` artifacts re-hash equal to their freeze pins
  (`58863ffb…`, `4721d1fb…`) ✅.
- **changes.diff** (135696 B): header-grepped, not read whole — Section 1 is the SRC
  `oracle.md.pre_r5 → oracle.md` append delta (r5+r6 only; hunk starts at the r1-r4 tail);
  Section 2 contains **only** `B1-PREREQ/a20260922-01/**` authored files, no product path
  (24 file headers enumerated, all attempt-local) ✅. (Cosmetic defect: F-REV-B1P-05.)

---

## 5. Unverified / out-of-scope for this review

1. **No arm or probe was re-executed by me** — arms/probe are verified from write-once raw
   evidence pinned by `SHA256SUMS.txt` (all hashes recomputed) plus code reading; I did not
   re-run pytest (read-only review; zero-product-change card made a re-run low-value).
2. **Freeze-vs-run temporal order** for this attempt is mtime+prose evidenced (F-REV-B1P-04);
   the chain proves content, not pre-run existence. Superseded freeze builds 1/2
   (`e177d719…`, `eb90c1a0…`) exist only in `decision.md` D-3 prose — unverifiable.
3. **r1 test-file recovery**: I excluded working tree, reachable commits, and the 1294
   reflog-unreachable blobs (by size 18236/18611/20631) — other routes (editor backups,
   pack promisor partials, worktrees of other clones) not exhausted, but nothing found.
4. **F6's exact "consistent recompute" run output** from the source reviewer is not pinned
   as raw evidence (only his script + report text); my no-erratum ruling rests on the script
   source and code reading, not on a re-execution.
5. **`commands.json`**: pin verified; contents (argv/expectations table) not line-read.
6. **B1 `iso/rf` (unfixed tree) full re-hash**: verified by "no 2026-09-22 mtime anywhere in
   the attempt" rather than by a per-file manifest comparison.
7. The **100-module regression subset** was not run (card changed zero product bytes — the
   zero-diff premise is what I verified).
8. F7/REM-02, I-08-C verdict, invest-core consumer, E21 implementation, batch-2 promotion —
   out of scope for this card, untouched, not adjudicated here.

---

## 6. Scope notes (apply to this verdict regardless of disposition)

- **REM-40…44 closure is a parent/owner register update**, not something this card or this
  review can write by itself; with F-REV-B1P-01 outstanding, REM-43 must not be recorded as
  closed in its current wording.
- **E21 implementation = separate product card** (loader identity return + two comparison
  sites + owner-approved trust anchor); this card is read-only on product by design.
- **r1 evidence gap**: as written in the card it is claimed as a permanent unclosable gap —
  **that claim is refuted for the stdout** (F-REV-B1P-01). The corrected permanent gap is
  the **r1 test file (18236 B / `e6c0949c…`) only**, within the domains I scanned (§4.4/§5.3).
- **B1 promotion (batch 2) remains an owner decision** — this review neither proposes nor
  authorizes any `iso/fixed/rf/scripts/**` byte.
- No file outside this attempt's two reviewer outputs was written by me; production and
  B1's attempt were read-only; no git write of any kind; nothing self-signed.

---

## 7. REM-79 self-check on this report (scoped assertions + both difference sets)

- Every universal-sounding claim above carries its measurement domain (bytes/git state as
  of 2026-09-22; specific file paths; the 24-entry freeze; the 31-entry manifest; the 1294
  unreachable blobs). Where I could not scope exhaustively I moved the claim to §5.
- Set-change claims were checked in **both directions**:
  - F4 recoverable-set: `stdout ∉ lost-set` (recovered: `58863ffb…` on disk + git) and
    `test file ∈ lost-set` (absent from tree, reachable commits, and the unreachable-blob
    size scan) — both differences measured, neither inferred from the other.
  - M6 delta: files that differ (exactly 1), files only in SRC (0), files only in M6 (0).
  - Freeze chain: link check and entry-hash check recomputed in both directions (declared
    head vs recomputed head; recomputed file hash vs declared pin).
- No sentence in this report asserts a class-wide property from a single instance; each
  "all/every/only/never" is bound to a enumerated, re-measured list.

*(End of review. Verdict: **changes_required**, blocker = F-REV-B1P-01; F6 erratum: **not
warranted**.)*
