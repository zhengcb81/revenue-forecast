# I-08-C-RESIDUAL / a20260923-01 — INDEPENDENT REVIEWER REPORT

- Plan: `2026-09-19-three-project-history-audit`
- Card: **I-08-C-RESIDUAL** (close the residuals keeping goal item ① short of 8/8)
- Attempt reviewed: `execution_runs/I-08-C-RESIDUAL/a20260923-01`
- Reviewer role: **independent** (this session). Methods = read/grep/pwsh; re-executions of this review (domain: this session) run in
  `%TEMP%\I08C-RESIDUAL-REVIEW`; RF production and each referenced attempt READ-ONLY;
  no network; no state-changing git. Files written by me: **this report + its `.sha256`
  sidecar — nothing else** (the implementer's `review.md` slot is left untouched; I do
  not transcribe any self-assessment).
- Review date: 2026-09-23/24. Interpreter: `C:\Miniconda\python.exe` 3.13.9; git 2.51.2.
- Measurement domains are stated per claim (recomputed-hash / file-read / suite-executed
  / fs-scan) per REM-79 discipline.

---

## VERDICT

**`accepted_scoped`** — the card's three closures (L1/F1, L2/F2, L3/F3) are
independently re-verified by my own %TEMP% re-executions; the annex dispositions
(F4/F5/F6/F7/§3.2/D1b) each carry a dated record; the original-attempt supersession is
chain-verified link-by-link; the boundary (production zero-write, old-attempt
zero-touch) holds on my own recount/re-hash. Acceptance is **scope-limited** and
**conditional on one application-time fix** (F-1 below):

- **Grant:** closure-by-record/annotation obligations of this card for goal item ① slot
  「I-08-C oracle 重冻」, on the counting basis of `decision.md` D-4 as re-ruled in §9 of
  this report ⇒ **8/8 transcription is endorsed with the caveats transcribed verbatim**.
- **Does NOT grant:** an empty product defect surface; E21 implementation; the REM-02
  consumer guardrail (a); P-L3 application (parent batch, with F-1's header fix);
  anything about invest-* cross-repo consumers, CLI transactions,
  `disclosure_adaptation=unmapped`, `accuracy=unproven`; no re-widening of the round-2
  `accepted_scoped` carrier's out-of-scope list.
- **Condition:** `patches/P-L3_delete_E21_docstring_claim.patch` must be applied with
  `git apply --recount` **or** after correcting its hunk header (F-1) — a plain
  `git apply --check` on its current bytes FAILS (measured, §4).

---

## 1. Findings

### F-1 (MUST-FIX at application; minor, one-character) — P-L3 is not plain-`git apply`-ready

- Command run by me (fresh copy of the current production file →
  `%TEMP%\I08C-RESIDUAL-REVIEW\patchcheck`): `git apply --check
  patches\P-L3_delete_E21_docstring_claim.patch` → **rc=128, `error: corrupt patch at
  line 19`** (measured, git 2.51.2).
- Root cause (measured): hunk header `@@ -232,8 +232,12 @@` declares 12 new lines; the
  hunk body contains **13** new lines (7 `+` lines + 3 context after + 3 context before;
  independent line count: old=8 ✓, new=13 ✗).
- `git apply --check --recount` → **rc=0**; `git apply --recount` → rc=0.
- Applied-result verification by me: `git diff --no-index` = **one hunk, docstring lines
  235-243 region only** (2 lines removed, 7 added; identical to `changes.diff` §1
  verbatim); **AST equal with docstrings stripped = True**, full AST differs solely in the
  docstring constant ⇒ zero behaviour change confirmed (not merely "asserted by
  inspection" as the card wrote).
- Consequence: the handoff's "apply-ready" claim is accurate as to content and
  inaccurate as to tooling. Not a counting blocker (L3's demanded terminal label
  "recorded not-closed" is landed independently of application), but the parent's
  production batch must apply with `--recount` or fix the digit 12→13 first, then
  re-run `git apply --check` (expect rc 0).
- The card never claimed to have run `git apply --check` (grep of the attempt: zero
  hits) — this is a refinement of an inspection-based claim, not a caught false claim.

### F-2 (disclosure; not a counting blocker) — freeze-time pins of the two living parent documents are not retro-verifiable

- `binding.json` pins `OWNER_DECISIONS.md = 4bed42c6…` and
  `REMEDIATION_REGISTER.md = 535152f0…` "at freeze". My re-hash of the current files:
  `OWNER_DECISIONS.md = c13feca4…` (mtime **2026-09-23 23:12:30**, i.e. mid-run,
  external to this card), `REMEDIATION_REGISTER.md = 2e9f3a40…` (mtime **23:57:34**,
  after handoff). No freeze-time copies are stored in the attempt, so the two pin values
  cannot be re-derived from disk (fs-scan + git history of the RF repo).
- Mitigation I executed instead — **content verification by line of each cited authority line
  against current bytes** (line numbers via Select-String, which is the numbering the
  card cited): `OWNER_DECISIONS.md` **L365** = the A-2 原话 quote (verbatim match),
  **L370** = 「A-2 批准 | I-08-C oracle 追加式重冻（E11/E13 由"缺口在册"翻转为"攻击必拒"），
  **收口归其 reviewer** | 与建议一致 | 已派 `I-08-C` refreeze 卡」 (verbatim match),
  **L420** = 「B: 全批」原话, **L426** = B=全批 row containing 「**父保留各仓提交权**（卡交付
  证据后由父分仓提交）」 (verbatim match); register rows verified by content:
  REM-42 (F3, line 70), 「E21 实现=独立产品卡仍开放（残留转产品卡轨道）」 (line 780),
  「I-08-C-RESIDUAL 收口卡已排（3 遗留+原 attempt 双口径处置）」 (line 1493). All 4 owner
  citations and both register citations **match at the cited line numbers**.
- Judgment: the citations survive; the hash pins alone are non-reproducible. Recommend
  the parent, when next editing these living docs, ledger "pins 4bed42c6/535152f0 were
  freeze-time self-measurements, superseded by later parent edits".

### F-3 (trivial) — one process disclosure sits in the wrong file

`commands.json`'s final-form trailing-comma fix is disclosed in `handoff.json`
(deliverable_hashes note) but not listed in `decision.md` D-6's numbered disclosures
(D-6 covers c0 harness errors, c9→c9b, concurrency, needle note, git/network). Disclosed
either way; noted for completeness.

### F-4 (trivial, wording) — command-count wording

`verdict_supersession_20260923.md` §4 says "None of this card's **13** commands…";
`commands.json` has 13 frozen entries and **14** executions (`c9` + refined `c9b`), and
handoff/`commands_executed` list 14. Also the `commands_executed` array implies c9b
before c10/c11 while mtimes show c9b at 23:08 after c10/c11 at 23:01. Cosmetic: argv
and write-roots are per-entry and unaffected; expectations unchanged (both c9 raws
preserved). Noted in passing.

### Note (parent prompt typo)

The dispatch spelled the r4 prefix `fadf8e5e`; the actual value (handoff, oracle §3.1,
and my independent extraction) is **`fadf8a5ebfdb7ca7…`**. Everything else in the
dispatch's hash list matched.

---

## 2. Deliverables inventory (re-hashed by me; values below recomputed, not copied)

The 24 entries pinned as deliverable hashes in `handoff.json deliverable_hashes` **match my
re-hash byte-for-byte** for: `oracle.md` 4e031c43…/21681 B, `binding.json` 8c97cbfe…,
`commands.json` 76575529…, `decision.md` ab744fd3…, `changes.diff` bffdee35…,
`review.md` 5a58743e…/919 B, `verdict_supersession_20260923.md` 6ea8d077…,
`patches/P-L3…patch` cc05fe6e…/1073 B, `recovery/README.md` 86d0daa1…,
`manifests_before/after/comparison` 56848a64…/a3ea8ebb…/73e11ca8…,
`E_L1_checks` bb552685…, `E_L1_fieldcount_threeway` cb05d60e…, `E_L2_presence` ef3f673e…,
`E_L2_run_fixed.stdout` 9f468762…, `E_L2_run_m6.stdout` 5c7e1550…, `E_L3_e21_scan`
d3ee5f63…, `E_L3_trust_loader` 9ec1b6c3…, `AX1_f4f5_checks` 4ebe9260…, `AX3_rem02_state`
2565d0f9…, `AX5_d1b_fsscan` 7c43cbfe…, `L3_E21_not_closed_record` bce805d6…,
`AX_annex_closure_records` 9f46eef2…. `handoff.json` self-hash on my receipt:
**9ca79604032ddc505d9a698e9424e7a14a703280748c8de8d468a9f0ed58b13e / 17267 B**.

- **Oracle frozen before runs (mtime evidence):** `oracle.md` 2026-09-23 **22:40:00**,
  `binding.json` 22:43:37, first judged-run artifact `manifests_before.json`/`c0` **22:49:00**,
  the 30 `evidence/` files span ≥ 22:49 ≤ 23:15 ⇒ freeze-before-runs holds on mtimes;
  `commands.json` execution order c0→c12 matches evidence mtimes modulo the disclosed
  c9b re-run (F-4).
- **`commands.json`:** 13 frozen entries + `commands_executed` of 14 (= handoff's "14
  runs"); parses under both PS `ConvertFrom-Json` and Python `json` (rc 0/0); raw vs
  expected rc deviations are the disclosed c0×2 and c9 ones only (checked both maps
  myself: raw c9=3 vs expected 0 is the sole raw≠expected pair, plus the two c0 harness
  errors never got an entry — as disclosed).
- **`review.md`:** empty slot, no verdict anywhere in it (read in full); implementer
  self-acceptance flags false/true as claimed (handoff lines 10-14). Implementer did NOT
  self-review ✓.
- **`handoff.json`:** `status=review_pending`, `disclosure_adaptation=unmapped`,
  `accuracy=unproven`, unsigned (`independent_reviewer: NOT YET ASSIGNED`), and exactly
  **9** `requested_of_the_reviewer` entries — each answered in §10 below.
- **`changes.diff`:** NEW-files inventory matches the attempt's actual file listing I
  took (dir walk); production + referenced-attempt modification sets declared EMPTY and
  independently confirmed (§8).
- **`evidence/` + `recovery/`:** 30 files with distinct per-run labels (incl. preserved
  superseded `c9_*` + refined `c9b_*` — both raws read by me); `recovery/README.md` read:
  sensible no-rollback boundary (%TEMP% scratch disposable; historical artifacts never
  repaired in place).

---

## 3. L1 (F1) — re-measured by me from current bytes

**(a) B1 oracle prefix chain + markers** (my own byte extraction, not their JSON):

| check | expected | my measurement | match |
|---|---|---|---|
| total bytes | 57911 | 57911 | ✓ |
| full sha256 | 6e344a20… | `6e344a208f8fc43992d339693d74c51122b505d17c368a67f5899dbd43a222dc` | ✓ |
| prefix[0:27697] (r1) | 81af1240… | `81af124047eef968d6db84b8f4c1c1b22e77a5f4781b2664d2ca6e8555f74281` | ✓ |
| prefix[0:31081] (r1-2) | 60ecbca7… | `60ecbca7a008d60b8634bfed1cec56b801a86e6486f639c54e19cd257867f1d4` | ✓ |
| prefix[0:35840] (r1-3) | 231e7976… | `231e79768bd71ce95730ed10539d1e5865caa659c0dccf942bf7f2b99d8e3523` | ✓ |
| prefix[0:39287] (r1-4) | fadf8a5e… (**not** fadf8e5e) | `fadf8a5ebfdb7ca771031790e0fa1701a31fedf15becbf6da8c9cbaf5460fbae` | ✓ |
| `## Revision r5` | @39288, count 1 | @39288, count 1 | ✓ |
| `## Revision r6` | @43299, count 1 | @43299, count 1 | ✓ |
| `## Revision r7` | @47539, count 1 | @47539, count 1 | ✓ |
| r5+ region | 18623 B, corrected text | 18623 B; contains "10 fields", `SIGNED_RESULT_SHA256_SENTINEL`, receipt/result_sha256 fixpoint prose; I read the dump head: R5-1 states the exact 10-member set and "result_sha256 is **not** a record field; neither is receipt_sha256" | ✓ |

**(b) three-way field count** (my own script, authored this session in %TEMP%, run
against: fixed-tree copy, B1's frozen `test_b1_rem.py`, and a runtime import of the
%TEMP% fixed copy; plus a 4th production-AST arm I added):

| arm | count | set == oracle §2.1 closed set |
|---|---|---|
| (a) fixed-tree AST `PUBLICATION_ATTESTATION_FIELDS` | **10** | ✓ |
| (b) frozen-test AST `ATTESTATION_FIELDS` | **10** | ✓ |
| (c) runtime import (from `%TEMP%\…\fixed\rf\scripts`) | **10** | ✓ (import proven to come from the temp copy, not production) |
| (d) production `scripts/revenue_publication.py` AST (extra) | **10** | ✓ |

⇒ **10/10/10 (+1) confirmed independently**; sets equal member-for-member to
{algorithm, attestation_payload_schema_version, domain_separator, fingerprint, issuer,
key_id, payload_sha256, request_id, signature, signed_at}.

## 4. L2 (F2) — BOTH arms re-run by me on my own %TEMP% copies

Copies: `B1/iso/fixed/rf → %TEMP%\I08C-RESIDUAL-REVIEW\fixed\rf` (identity re-hash:
`revenue_publication.py` = `bc2bb4a3…` = the pinned promoted bytes) and
`B1/reviewer/scratch/mutations/M6/rf → …\m6\rf` (`38011e2c…` = pinned M6 value).
Command shape per the card's frozen contract: `python -X utf8 -B -m pytest -p
no:cacheprovider --noconftest -q --no-header -rA --basetemp <temp> <B1 test_b1_rem.py>
<B1-PREREQ test_r13_equiv_rem41.py>` with `B1_REPO_ROOT` + `REVENUE_PUBLICATION_REGISTRY`
redirected into %TEMP%.

| arm | my result | claim | match |
|---|---|---|---|
| fixed tree | **rc 0, "14 passed in 24.35s"** (12 frozen + rem41_a + rem41b) | 14/14 PASSED rc 0 | ✓ |
| M6 mutant | **rc 1, "1 failed, 13 passed in 16.79s"**; the single FAILED node = `test_rem41_a_present_record_is_verified_even_when_label_is_unattested` (`DID NOT RAISE ForecastInputError`); `test_rem41b` control PASSED | exactly rem41_a FAILED / 13 passed rc 1 | ✓ |
| frozen 12-node set on M6 | **12/12 PASSED** (my count from the -rA list) | blind-spot-reproduced claim (M6 leaves frozen file green) | ✓ |
| node file | `B1-PREREQ/test_r13_equiv_rem41.py` = `6aa0f1a82f91ee11987309ca1d8f2efbebaddafec2376e80dd9ebe7e5699e57c` / 5604 B (my re-hash) | 6aa0f1a8… | ✓ |
| M6 presence in oracle r6 region | their `E_L2_presence.json` (r6 marker @43299; M6 first hit at r6+39 = "mutation M6 joins the proof surface", appended by B1-PREREQ) — read + consistent with my r6 marker offset | M6 in mutation table | ✓ |

## 5. L3 (F3) — record read, patch tested, option (a) reasoning spot-read

- `evidence/L3_E21_not_closed_record_20260923.md` read in full: dated, option (b)
  split by authority (list-not-closed DONE here; deletion routed), option (a)
  BLOCKED-on-cap-change. It never claims E21 closed ✓.
- **E21 documented / never raised — my own greps over production `scripts/`:**
  `issuer_key_binding_mismatch` and `\bE21\b` each occur **exactly once**, at
  `scripts/revenue_publication.py:235` (the docstring line 235-236 the card cites);
  raise sites matching E21: **zero hits** (grep over `scripts/`, 5 files).
- **issuer/key_id outside the signed request — direct read:** `publication_attestation_request`
  (production lines 336-363) returns exactly
  `{attestation_request_schema_version, domain_separator, request_id, payload_sha256,
  result_sha256 (=SIGNED_RESULT_SHA256_SENTINEL), canonical_payload_sha256}` — no
  `issuer`, no `key_id` ⇒ their `issuer_key_id_in_signed_request={false,false}` confirmed.
- **Trust loader shape — direct read:** `contracts/evidence._trusted_signer_public_keys`
  (lines 242-267) parses just `public_keys[].public_key` + `fingerprint` →
  `dict[str, bytes]`; **no issuer/key_id parsing anywhere in the loader**; fail-closed on
  absence. `config/trusted_signer_public_keys.json` **ABSENT** (my Test-Path: False) =
  fail-closed default. ⇒ "E21 as specified needs the 12-field trust-entry schema (I-08-A
  E25, not implemented) = cap change" reasoning **holds** (spot-read of the cited product
  lines + schema absence both confirmed).
- **P-L3 apply-check:** see **F-1** — plain `git apply --check` rc=128 (corrupt patch at
  line 19: header says `+232,12`, body has 13 new lines); `--recount` rc=0; applied
  content diff = the docstring clause alone (single hunk @232-243), AST(docstrings
  stripped) identical ⇒ docstring-only, zero behaviour change **verified**, but
  "apply-ready" is true only under `--recount`/header fix.

## 6. Annexes AX-1..AX-5

- **AX-1 (F4/F5):** my own decode of `B1 …/before/b1_unfixed.stdout.txt` (re-hash
  `58863ffbca21c72350b868e9b344cc7e5a1651060f6ccb5bb1fcd3f796701335`, 30580 B, UTF-16LE):
  summary line = **"10 failed, 2 passed in 8.18s"**, node lines = 2 PASSED / 10 FAILED
  ⇒ register §22/补1 erratum (the F4 "raw not auditable/overwritten" reading) is
  **re-confirmed false as to stdout**; the true permanent gap stays the r1 test file
  (18236 B / `e6c0949c…`) + the lost exploratory 8/12 stdout (their CF-RES-5, unchanged).
  F5 substance: B1-PREREQ `freeze.json` re-parsed by me: **entry_count=24 = len(entries)=24,
  chain_head 8f3d35cc…, frozen_before_any_run=true**; SHA256SUMS 31/23 lines per their
  evidence (files present by fs listing). Their honest note that the needle "hash-pin"
  was absent from the B1 oracle text (`…_present:false`) is recorded-as-measured, not
  smoothed ✓. F4/F5 protocol of THIS attempt = distinct raw labels incl. both c9 runs ✓.
- **AX-2 (F6):** permanent-limitation record present (§AX-2): "permanent, provable
  limitation — no action", with the parent's F6 clarification (rewrite+recompute ⇒ both
  ACCEPTED; without recompute ⇒ receipt ACCEPTED / forecast REJECTED = strengthening)
  carried; no over-claim of binding `result_sha256` anywhere (claim scan over the attempt
  found no positive claims) ✓.
- **AX-3 (F7):** verbatim demanded status present —
  **"documented limitation, consumer-side guardrail not yet in place"** (record §AX-3 +
  `AX3_rem02_state.json.f7_status_record`); decision = **(a) receipt_schema_version bump
  + (c) follow-up rename/deprecate item**, (b) rejected with the frozen-design rationale
  ✓. **Their honest zr701/zr705 measurement-gap admission: verified by my own scan** —
  `tests/test_zr701_f1_draft_formal.py` and `tests/test_zr705_draft_formal_swap.py`
  contain **zero** lines matching `warn|warnings|filterwarnings|pytest.warns|catch_warnings`
  (fs-scan of both files) ⇒ the "would break zr701/zr705 clean-run assertions" leg is
  indeed NOT independently re-verified, exactly as they admitted (c9 raw `asserts_clean=false`
  for both, preserved; c9b carries `measured_limitation` text). Preserved-not-smoothed ✓.
  Marker state re-confirmed from their promoted-bytes run: exported, zero warn/raise sites.
- **AX-4 (§3.2):** accepted-by-design record present (§AX-4), explicitly "not a defect
  of this card", carried into handoff `carried_findings` CF-RES-4 ✓.
- **AX-5 (D1b):** **my own fs-scan re-confirms `production_anchors.txt` STILL ABSENT**
  (0 hits across the whole plan tree, 0 hits in the RF repo incl. hidden files);
  `before/production_anchors.json` sibling EXISTS; B1 `commands.json` lines 27/35/38
  register the `.txt` (read directly). Erratum entry = 未产出（仅 .json）, file not
  fabricated ✓.

## 7. Supersession + chain (each link re-hashed/re-read by me)

| link | my measurement | match |
|---|---|---|
| round-1 `I-08-C/review.md` = `changes_required` | full-file `2e3751b7…`/17098 B; **prefix[0:13700] = `c1a8fd11b20f911c7407943dabe70bc493a9cb2959719c13beef21f8e7f1f2a3`** | ✓ (byte-prefix preservation claim holds) |
| demands (1)-(3) → B1 carrier | B1 `reviewer_report.md` self-pin recomputed **by the documented PENDING-sentinel rule: `73feb059…` over 37086 B (37224 B on disk)** = `REPORT_PIN_VALUE.txt` = report_pin.json = handoff pin; VERDICT L16-18, severity map L319-321, §9 items 1-6 L536-553 each verbatim-matched against my read of the report; verdict `accepted_with_conditions` | ✓ |
| B1 conditions → B1-PREREQ (r5/r6/r7, R13 node, evidence protocol) | node `6aa0f1a8…` ✓; oracle r5/r6/r7 markers ✓ (§3); round-2 carrier `B1-PREREQ/reviewer_report_r2.md` = **`50437289bc5b83d76c5adbb34b4481008498cb47125bd02b62fa9676b33aa558`**/28775 B + sidecar present; `freeze.json` 24-entry chain | ✓ |
| demand (4) refreeze → FIX-I08C-REFREEZE-1 (oracle r4) | `I-08-C/oracle.md` total 40311 B; **[0:22335] = `94a853e978e34f522820cc2e03548fffe8ee2e599725d7a0131f872c93add8b3`**, **[0:6831] = `478bd70e0a1dfbfb924ebec0175bb2bdcdd199880de1c554de099d8ac8723c90`** | ✓ |
| round-2 acceptance | `reviewer_report_r2.md` L10 = `## VERDICT: \`accepted_scoped\``; file **`ee5046a5…`/13285 B**; sidecar content = same digest; scope text read (verification + evidence + oracle re-freeze r4 + round-1 items (1)-(3) in B1's isolated tree) | ✓ |
| owner authority A-2 | `OWNER_DECISIONS.md` **L365/L370** read: 「A-2: 批准」+ ruling row 「…收口归其 reviewer」 verbatim | ✓ (content; see F-2 for pin) |
| promotion 「B: 全批」 | `OWNER_DECISIONS.md` **L420/L426** read: 「B: 全批」+ 「父保留各仓提交权」 | ✓ (content; F-2) |
| parent dispatch §74 / §28 / REM-42 | register lines 1493 / 780 / 70 read: quotes match | ✓ (content; F-2) |
| production carries promoted bytes | my re-hash: `revenue_publication.py bc2bb4a3…`, `revenue_core.py 8a761498…`, `revenue_report.py 212f0059…`, `publication_registry.py 29aaae4f…`, `contracts/evidence.py 054e364a…`; `git status --porcelain --untracked-files=all -- scripts tests config artifacts` = **EMPTY (rc 0, 0 lines)** (my own run) | ✓ |
| **NOT I-14-D** | register rows: **REM-04 = "I-14-D F-REV-D-01" (line 15)**, **REM-81 = "I-14-D r6 复审" (line 370)**, line 426 "REM-04 … r7 修正中", line 523 "REM-81 … r7 复审 accepted_scoped ⇒ CLOSED"; I-14-D attempt carries `reviewer_report_r6.md`/`reviewer_report_r7.md` + sidecars. ⇒ the dispatch's tentative "B1-I08C → I-14-D r7?" is correctly **excluded**; I-14-D r6/r7 belongs to the REM-04/REM-81 track | ✓ |

Option (i) vs (ii) ruling: **(i) justified** — the per-item table in
`verdict_supersession` §3 maps each of the four round-1 demands to an executor and an
independent acceptance, and each mapping above re-verified from the carrier bytes;
re-executing (ii) would duplicate evidence and require rewriting sealed attempts,
contradicting standing rules 0.1/0.2. Chain attribution is measured (carrier hashes +
line-level citations), not asserted. Nothing in the supersession grants a new
acceptance (`implementer_signed: false` present, §5 read).

## 8. Boundary / zero-touch / concurrency

- **I-08-C/a20260919-01:** my recount = **73 files**; their before/after manifests
  re-compared **by my own script**: 73→73, added 0 / removed 0 / content-changed 0 /
  mtime-changed 0; `handoff.json` before == after == **`b83e04a670d464343816e978c102dab269dadc79aef2b9842d9d0c505ef82f12` / 58814 B / mtime_ns 1790067548253599400**, and I
  re-hashed the live file this session: same digest/size ⇒ **b83e04a6 before == after ==
  now** ✓.
- **B1-PREREQ/a20260922-01:** my recount = **298 files**; manifests 298→298, 0/0/0 ✓.
- **B1-I08C/a20260921-01:** my recount = **2765**; manifests 2763→2765 with
  added = `evidence_erratum_20260923.md`, `review.md`; content- + mtime-changed =
  `handoff.json` — exactly the three attributed files, nothing else (my recompute).
- **Concurrency attribution — verified:**
  - mtimes: `review.md` **22:56:31**/7581 B, `handoff.json` **22:56:32**/28595 B,
    `evidence_erratum_20260923.md` **23:04:27**/3886 B — byte-identical to
    `verdict_supersession` §4's numbers (file-read).
  - content signatures: `review.md` self-describes as BOOKKEEP-REPAIR carrier-landing,
    transcription-only, `verdict_is_transcribed_not_authored: true`,
    `implementer_never_signs_acceptance: true`; `evidence_erratum_20260923.md` header =
    **"by: BOOKKEEP-REPAIR / a20260923-01（父派单 #15）"**; `handoff.json` line 10 =
    `"status": "accepted_with_conditions"`.
  - cross-claim: `BOOKKEEP-REPAIR/a20260923-01/handoff.json` line 33 explicitly claims
    **"execution_runs/B1-I08C-product-fixes/a20260921-01/review.md (new) + handoff.json
    (flip) + evidence_erratum_20260923.md (new)"** (sibling attempt exists, file read).
  - **not one of this card's 14 commands can produce those three files** (my audit):
    each `commands.json` argv targets `scratch/*.py` or the two test modules; write
    roots are `<attempt>/evidence` + `%TEMP%\I08C-RESIDUAL-a20260923-01\**` and nothing else;
    `scratch/manifests.py` (read in full) writes solely into `EVID/`; `check_fields.py`
    copies **from** the B1 trees into %TEMP% (source-read, no B1 write); grep of
    `commands.json` for `review.md|evidence_erratum|…handoff` = zero argv hits (one
    purpose-text mention of I-08-C's own handoff). Their c5 evidence file landed at
    22:56:35 — inside the siblings' 22:56:31-32 window ⇒ concurrent, mutually external,
    as disclosed.
- **Production:** trust file ABSENT, porcelain EMPTY, five anchors = promoted pins (each
  re-measured by me, §7). No git write command appears in `commands.json` (argv audit);
  no network reaches any bound command (binding §isolation read; pytest run locally).

## 9. Counting statement D-4 — explicit ruling (review request #8)

**RULING: ACCEPT the counting statement AS SCOPED — goal item ① slot 「I-08-C oracle
重冻」 counts CLOSED ⇒ 8/8, with the caveats transcribed verbatim; L3 counts CLOSED with
P-L3 ROUTED (applied production bytes are NOT required for counting), conditional on
F-1's header fix being carried into the application step.**

Reasons (each criterion of oracle §6 re-checked by me):
- (a) refreeze exists append-only + independently accepted: oracle r4 prefix proofs
  + round-2 `accepted_scoped` carrier + sidecar re-hashed by me (§7); owner 「收口归其
  reviewer」 line read ✓.
- (b) the 3 leftovers closed with the evidence their condition texts demand: L1 10/10/10
  + chain (my runs, §3); L2 both arms (my runs, §4); L3 not-closed record + apply-tested
  patch (§5, F-1 condition) ✓.
- (c) original state resolved by dated supersession with before-hash unchanged ✓ (§7/§8).
- (d) no silent drop under any reading: D-1's alternate-parsing disclosure checked
  against the actual report (§2 partition matches VERDICT L16-18 + §9 items 1-6 +
  severity map L319-321 verbatim); F4/F5/F6/F7/§3.2/D1b each have a dated disposition
  (§6) ✓.
- Scope honesty of "closed": D-4's "what closed does NOT mean" paragraph explicitly
  keeps: product defect surface NOT empty (E21 impl, REM-02 (a), P-L3 application on
  named tracks), invest-* consumers unverified/INVEST-CORE-owned,
  `disclosure_adaptation=unmapped`, `accuracy=unproven` — and a claim scan over the
  attempt found **no positive-shaped mentions** of invest/CLI/disclosure/accuracy (zero
  positive over-claims) ✓. Handoff keeps `unmapped`/`unproven` fields ✓.
- Why routed-not-applied suffices for L3: the conditions clause is disjunctive
  ("implement E21 **or** delete the claim and list it under not-closed"); the
  list-under-not-closed half is landed (dated record); the delete half is landed as an
  apply-tested artifact and blocked from application solely by goal discipline ⑤
  (生产零合并) + owner 「父保留各仓提交权」 — both read at the cited lines. Requiring
  applied bytes in-card would require violating a higher-priority frozen discipline.
  This is stated here so the caveat travels with the 8/8 number: **the count includes one
  not-yet-applied docstring edit.**

## 10. The 9 review requests — answers

1. **Oracle re-hash + freeze-before-runs + three-way recompute** → done: hashes in §2,
   mtime ordering 22:40 < 22:49 in §2, my own 10/10/10 (+production arm) in §3(a)(b).
2. **Re-run the L2 pair myself** → done: fixed rc0/14 passed; M6 rc1 with exactly
   `test_rem41_a` red, 13 passed, frozen 12-node green on M6 (blind spot reproduced),
   control green (§4).
3. **Prefix chain + r5/r6/r7 offsets + r5+ region read** → done, values in §3(a);
   dump head read (corrected 10-field text present).
4. **Identification argument D-1 + no silent drop** → done: partition matches the source
   report verbatim; F1-F7/§3.2/D1b each disposed (§6, §9(d)); alternate readings
   disclosed in oracle §2/D-1 and every member disposed either way (D-2 rows read).
5. **Audit verdict_supersession (measured chain, option (i) vs (ii), before-hash)** →
   done: §7 (links re-hashed, owner lines read, (i) justified) + §8 (b83e04a6
   before==after==now, 73→73 0/0/0).
6. **Concurrency attribution audit** → done: §8 — three files' mtimes/content/sibling
   cross-claim verified; zero argv/write-root overlap with the 14 commands.
7. **D-6 disclosures preserved-not-smoothed** → done: c0 recorded raw = attempt 3 with
   the two harness errors disclosed (no fabricated raws possible to check, but the
   disclosure is specific); c9 raw (`all_ok:false`, phrase absent) **and** c9b raw both
   preserved under distinct labels (I read both); zr701/zr705 gap admitted and **independently
   confirmed by my scan** (§6 AX-3); needle "hash-pin" absence recorded as measured.
   Judgment: **preserved, not smoothed.**
8. **L3 closed-with-routed vs applied-bytes** → my explicit ruling in §9: closed with
   P-L3 routed; applied bytes NOT required for counting; F-1 condition attached.
9. **No over-claim of invest-*/CLI/disclosure/accuracy** → done: claim scan found no statements beyond
   caveat statements (§9); handoff fields `unmapped`/`unproven` intact; supersession §5
   explicitly does not widen scope.

## 11. Unverified / carried as unverified by me

1. The two freeze-time document pins `4bed42c6…` / `535152f0…` (F-2): not retro-verifiable;
   content of each cited line verified instead.
2. c0 attempts 1-2 raw stdout (lost pre-measurement): unverifiable by nature; disclosure
   specific and plausible (D-6.1), no evidence file claims to contain them.
3. invest-* cross-repo consumers (`invest_contracts.py:1130-1142`): unverified here —
   their own D-7 + CF-RES-6 disposition, INVEST-CORE card owns the site.
4. I did not re-hash the 3134 manifest entries against live disk entry-by-entry; I
   re-derived the before/after comparison from their two manifests with my own script,
   recounted the 3 trees live, and directly re-hashed the decisive files (I-08-C
   handoff, node file, carriers, production anchors).
5. The B1 `SHA256SUMS` line counts (31/23) are their measurement; I verified the files
   exist and `freeze.json` (24 entries + chain head + frozen flag) directly.
6. Historical claims that cannot be re-executed (B1 reviewer's 2026-09-21 runs, r1
   test-file loss) — taken as recorded, consistent with carriers read.

## 12. Scope-if-accepting (for the parent's transcription)

- Goal item ①: **I-08-C slot = CLOSED ⇒ 8/8**, transcribed WITH the exact caveats:
  closed = deliverable-side obligations complete + each acceptance condition either
  discharged with evidence or at its demanded terminal label; **not** an empty product
  defect surface; invest-* consumers unmapped/unverified (INVEST-CORE); `accuracy=unproven`;
  `disclosure_adaptation=unmapped`; named tracks: **P-L3 → next production batch
  (parent, apply with `--recount` or header fix per F-1)**, **E21 implementation →
  product card (cap-change, 12-field trust schema)**, **REM-02 (a)+(c) → contract track
  (professional review)**.
- Register rows to add (parent-written): AX-2 (F6 permanent limitation), AX-3 (F7
  record + (a)/(c) decision, guardrail not in place), AX-5 (D1b erratum 未产出) —
  carrier = this attempt's `evidence/AX_annex_closure_records_20260923.md`.
- Transcribe: L2 arm results (my runs: fixed 14/14 rc0; M6 exactly rem41_a red /13
  passed rc1; frozen 12/12 green on M6) and the concurrency attribution (BOOKKEEP-REPAIR
  dispatch #15 landing `review.md`/`handoff.json` flip/`evidence_erratum_20260923.md` at
  22:56:31/22:56:32/23:04:27, external to this card).
- Carry F-1 into the batch step; ledger F-2's pin note at next parent edit.

## 13. Boundary statement (this review)

Methods = read/grep/pwsh, nothing beyond; RF production and each referenced attempt read-only (my sole
writes: this report + `.sha256`, plus disposable scratch under
`%TEMP%\I08C-RESIDUAL-REVIEW`); no network; git usage limited to read-only/status/
`apply` **inside %TEMP%** (`--check`/`apply` on a temp copy) and `status --porcelain`
in RF — no state-changing git anywhere; the implementer's `review.md` slot was not
filled by me; this verdict is mine as the assigned independent reviewer (the implementer
did not self-sign).

— Independent reviewer, 2026-09-24
