# B3-PREREQ (a20260922-01) — carrier landing (bookkeeping transcription)

## VERDICT BLOCK

- **verdict** = `accepted_scoped` — with one non-blocking wording finding (F-1, P4 informational)
- **carrier** = `reviewer_report.md`
- **carrier sha256** = `F367984B6BA6A8793C5A3F598686077CAF8AFCF413FE6356B69B47D4B7B23C53` (lowercase `f367984b6ba6a8793c5a3f598686077caf8afcf413fe6356b69b47d4b7b23c53`) — **15544 B**, 189 LF-terminated lines, UTF-8 without BOM, 0 CR bytes (LF-only), single trailing LF
- **pin** = `reviewer_report.md.sha256` (84 B, sidecar's own sha256 `e5852d16205ad11f3055a32762bfd275ffa5bdb0dd681eb67522e724544fa655`) reads `F367984B6BA6A8793C5A3F598686077CAF8AFCF413FE6356B69B47D4B7B23C53  reviewer_report.md` — verified read-only at landing: independent re-hash of the carrier == sidecar content == dispatch pin; verdict line greps to `accepted_scoped`
- **ruling location** = `reviewer_report.md` **L3**: ``**Verdict: `accepted_scoped`** — with one non-blocking wording finding (F-1).``; claim sections **L30–L58** (REM-47/RF-1), **L60–L87** (REM-48/RF-5), **L89–L106** (REM-49/CF-1), **L108–L122** (mutations), **L124–L132** (boundaries), **L134–L143** (superseded runs); **F-1 L145–L160**; unverified list **L162–L169**; scope notes **L183–L189**
- **byte proof** = verdict line L3 bytes 60..138 (79 B) sha256 `2b5d869fb94dcb9451439a347b52b68e30ddf0876e3c57d8ecc3bf28523785b9`; claim1 L30–L58 bytes 1774..3906 (2133 B) `d9631f9f4779d96badf8f9f946ec4b1f3d8e8d90522ffc7db1ae603e4b1ab19d`; claim2 L60–L87 bytes 3909..6070 (2162 B) `2982493d5a0bae7666c64102d70783c2ae9410e7b5f44c726df419c3a80607cd`; claim3 L89–L106 bytes 6073..7508 (1436 B) `4aa24741b2985a6a1d9703b6c54441345047679f772f577ad515b81e4a229cbf`; claim4 L108–L122 bytes 7511..8762 (1252 B) `8bbc8989b64aa397993b8d65921c6191562dc342ad201a17a92052fd1731f839`; claim5 L124–L132 bytes 8765..10665 (1901 B) `21d13e6de32108329ddb25ed027447c4b8f2383c25b1f53eba6d26fb8b56ef12`; claim6 L134–L143 bytes 10668..11476 (809 B) `fd897dc2730427d36e5e1094494645ef3a4e663d747e7975435d86c1b10a5985`; **F-1 L145–L160 bytes 11479..12846 (1368 B) `1904fa604705e64d66a4695d36ec4b5ed1fec5061c4b783f423b2fb279e505e2`**; unverified list L162–L169 bytes 12849..13798 (950 B) `42618992c07c135c41ca88cd749cd3b5a143d66c6660a02cc5201a2dd2ec4bbe`; scope notes L183–L189 bytes 14767..15542 (776 B) `81266a39ad5fca5f6396b7bf00f9fcfadd8bc0ce35b25a36ff9fe39ecbcc7a9e`; whole file minus trailing LF 15543 B `af402840c4d52458034f4368e4a73b2b71bb6e931594bd6ad0e679c5192cb6e4`
- **reviewer** = 独立复核 (independent reviewer subagent, parent-dispatched, not the implementer; authored only `reviewer_report.md` + its `.sha256` sidecar inside this attempt)
- **nature of this file** = bookkeeping transcription, adds no acceptance of its own. The implementer never signs; this landing pass never signs; nothing here authorizes anything beyond restating the reviewer's ruling.

`review.md` did not previously exist in this attempt; created by the carrier-landing pass — not by the implementer and not by the reviewer.

## Transcribed scope of the acceptance (from the carrier)

### REM-47 / RF-1 — FIXED ✓ (report §1, L30–L58)

- Guard order: single prefix assignment `sys.path[:0] = list(PATH_ORDER)`; collection guard computes `expected = _expected_origin()` and raises unless `find_spec_origin == expected` (plus `sys.path[0] == PATH_ORDER[0]` in fixed mode). Provenance: later write with a different sha256 sets `conflict=true`, first write stays reported, full ordered `writes` history retained.
- **Reviewer's own property re-run**: guard-order test RED on B3 baseline conftest (rc=1, **2 failed / 2 passed — P2+P3 fail**) / GREEN on this attempt's conftest (rc=0, **4 passed**). Provenance half verified by code reading + MUT-2 evidence, not re-run (the brief budgeted one property re-run, spent on the guard test).
- **C2 non-claim present in all three required carriers**: `iso/conftest.py` docstring L36–38 (+ history note L84–85); `decision.md` D1 L49–53; `handoff.json` line 19 — this guard is **NOT** the REM-12 prevention mechanism.

### REM-48 / RF-5 — FIXED with premise correction ✓ (report §2, L60–L87)

- **Premise correction**: the "every hash compared" claim lives at **`handoff.json:188`, not `decision.md`** (reviewer's own greps: `decision.md` has 0 occurrences of either phrase); corrected `handoff.json` parses as valid JSON with 0 occurrences of the false phrase.
- **Flag census recounted by the reviewer**: `after/integrity.json` parses; exactly **4 `expected_frozen` keys**; exactly **1 `NOT_REHASHED`** (line 23, `I-05-C:oracle.md`); other 3 equal their `frozen_attempts` counterparts ⇒ 3 compared-and-matched-from-records + 1 never-re-hashed; **flag kept** (post-correction count still 1, and the corrected sentence quotes it).
- **Superseded retention hashes independently recomputed**: pre-correction copy `CEE4B0DD157A6ED2F322C40258534414C0C64187D3F2C3E9EA3F3DFF7DEC171D` ✓ and corrected `E33D82A9E418A7CDFE04FE17CE435FF2F48EA06C27CAF096A9AB590C4683A493` ✓; `changes.diff` diff 3 shows exactly line 188 changed.
- **Reviewer ALSO re-derived (closes handoff gap 3)**: `I-05-C/a20260919-01/oracle.md` = `E4004563B8BBC403D7C8E3856A5FCB95AC3107E57FE891D7B848C5E9834CB34B` ✓, file git-clean ✓, and `git diff 8b7229c3 HEAD -- <that path>` **empty** ⇒ the "matching, git-clean since 8b7229c3" sentence is supported by the repository, not just cited.

### REM-49 / CF-1 — FIXED ✓ (report §3, L89–L106)

- Wording at `iso/fixed2/rf_scripts/source_preparation.py:138` is the reviewer's suggested operative phrase verbatim ("requested missing roles + their non-reusable ancestors (never a blind full recompute)").
- **Zero-behaviour-delta chain, reviewer's own runs**: byte diff = **comment-only, exactly 1 differing line pair (L138), both sides `#`**; `ast.dump(ast.parse(base)) == ast.dump(ast.parse(fixed2))` → True; `compile()` on both → OK.
- **FC-904 parity (spot-verified, not re-run)**: `rem49_fc904_parity.json` — 16 nodes/side, identical node→status maps, 15 passed / 1 failed both sides, `per_node_identical=true`, sole failure `TestB3ProductionProvenance::test_module_under_test_is_the_bound_copy`; both junit XMLs parsed by the reviewer: **16 testcases / 1 failure each, same RF-3 node**; test file **line 379** holds the location-dependent assertion (`assert "B3-I05C-delivery-fixes" in str(resolved) or _BYTES == "production"`) inside `test_module_under_test_is_the_bound_copy` (L375) — **confirmed unedited**.

### Mutations — 3 declared shapes match evidence ✓ (report §4, L108–L122)

- MUT-1 guard-order revert → `2 failed, 2 passed` = exactly P2+P3 ✓ (restore pre=post `7437BA9D…`); MUT-2 provenance overwrite → `1 failed, 1 passed` = conflict not flagged ✓ (restore `7437BA9D…`); MUT-3 old comment restored → `3 failed, 2 passed` = C0/C1/C4 ✓ (restore `91A6DC32…`).
- **Restore hashes recomputed against the reviewer's own current-file hashes**: attempt `iso/conftest.py` = `7437BA9D8810BD016602B45710916FA8F83F0926DE265E12AE152558473F057D` ✓, `iso/fixed2/rf_scripts/source_preparation.py` = `91A6DC32466E9D67B9D034AC345349EE683F6D5FD9486A67CD3ADE009C6EBF4D` ✓ (`evidence/tree_integrity.txt` agrees).
- Final suite evidence `final_full_suite_GREEN.txt` = **11 passed**, rc=0 ✓ (read, not re-run). **0 of 3 mutations re-executed by the reviewer.**

### Boundaries ✓ (report §5, L124–L132)

- `b3_reference/iso` vs delivered `iso`: **21 files vs 21 files, 0 hash mismatches, 0 extras either direction — byte-exact** ✓.
- `iso/fixed2` vs `iso/fixed`: 11 vs 11, **differing = 1 file** (`rf_scripts/source_preparation.py`) ✓.
- **Production pins recomputed by the reviewer**: RF `scripts/company_wiki_source.py` `225FECDD…`; RF `tests/test_fc904_artifact_selection.py` `8C0B8E39…`; CW `artifact_dag.py` `0C8B1D6D…`; **production `scripts/source_preparation.py` `37A3EEAE…` == B3-fixed SP `37A3EEAE…` ⇒ REM-49 not in production** ✓; pathscoped `git status -- scripts tests` empty ✓.
- **No git writes** by this attempt: all 17 `commands.json` entries are attempt-scoped edits/copies or read-only `git status`/`git diff --no-index` ✓. CW never written this attempt (3 ` M` pre-date it; artifact_dag.py still on pin) ✓. Oracle `55A89D25…` == sidecar ✓; freeze *ordering* attested procedurally (the single in-file RECORD-DED amendment is recorded before the execution log; SETUP-ORACLE precedes R1), not re-derivable by hashing alone.

### Superseded runs honesty ✓ (report Claim 6, L134–L143)

- **4 superseded runs** honestly labeled in `commands.json.superseded_or_aborted_runs`, outside the authoritative `commands` array, each with why + observed outcome (R6a, R7a, MUT-1a, MUT-2a); authoritative evidence files separate; MUT-2 evidence file repeats the supersession note; `handoff.json` discloses the two superseded mutation attempts as "NOT the mutation evidence". No superseded run cited as evidence anywhere the reviewer checked.

### F-1 (P4, informational, non-blocking) — wording corrected in this landing

- Original phrasing ("git status shows exactly that one M") is **scope-dependent** and is restated here in its verified **directory-scoped** form: **scoped to `B3-I05C-delivery-fixes/` = exactly 1 ` M`** (the ` M …/a20260921-01/handoff.json` line-188 correction); **repo-wide at review time = 24 ` M`, 23 from concurrent plan activity** (REMEDIATION_REGISTER.md, findings.md, progress.md, B1-I08C oracle.md, 8 I-08-C, 5 I-14-D, 2 I-14-E, M05/M14/M20/M24 oracle.md — mtimes 2026-09-22 09:59–11:01, plus untracked concurrent attempt dirs), **none traceable to this attempt's 17 `commands.json` entries**; production `scripts/`+`tests/` pathscope-clean; attribution is inference from mtimes + command inventory, not proven file-by-file. The original wording is preserved byte-exact in `handoff.json` under `boundaries_observed.only_out_of_attempt_write_historical_pre_verdict` (REM-83 species — preserved proactively).

## Scope notes baked into acceptance (must appear; transcribed from report §9, L183–L189)

1. **REM-47/48/49 register closure + B3 batch-2 promotion are parent/owner calls.** The review accepts the *attempt*; it does not adjudicate register closure and does not authorize promotion.
2. **RF-3's location-dependent assertion is still present** in the carrier (`test_fc904:379`) — P4, owned by RF-3, fails identically in any relocated tree, and was correctly not edited here.
3. **W05B/W05C vendored suites were not re-run** in this review (§6.4).
4. **REM-49 deliberately not landed in production** (prod SP == B3 accepted `37A3EEAE…`); landing it is a separate production change if ever desired.

## Carried findings (registered here; append-only, mirrored in `handoff.json.carried_findings` and `evidence/B3-PREREQ/qualification.json`)

| id | sev | summary | disposition |
|---|---|---|---|
| **F-1** | P4 informational, non-blocking | The "git status shows exactly that one M" sentence in `handoff.json.boundaries_observed.only_out_of_attempt_write` and `binding.json` is scope-dependent. | Corrected in place to the directory-scoped form (`B3-I05C-delivery-fixes/` = 1 M; repo-wide = 24 M, 23 concurrent, none traceable to this attempt); original wording preserved under `*_historical_pre_verdict`. Citation-hygiene finding, **not a defect in the REM-48 correction**. |
| **U-1** | info | Mutations: **0 of 3 re-executed** by the reviewer — evidence-file reading + independently recomputed restore hashes only (report §6.1). | Declared boundary; carried unresolved by design. |
| **U-2** | info | **FC-904 suite not re-run** by the reviewer — parity-JSON internal consistency, junit-XML parsing, line-379 source read only (§6.2). | Declared boundary; carried unresolved by design. |
| **U-3** | info | **Final 11-test property suite not re-run** by the reviewer — `final_full_suite_GREEN.txt` read only (21-file manifest re-verified 21/21) (§6.3). | Declared boundary; carried unresolved by design. |
| **U-4** | info | **W05B/W05C vendored suites not re-run** in the attempt and not re-run by the reviewer (declared bounded gap; their bindings do not touch this card's changed files) (§6.4). | Declared boundary; carried unresolved by design. |
| **U-5** | info | **Dirty-file attribution is inference**: the other 23 repo-dirty tracked files (F-1) inferred from mtimes + absence of any writing command in `commands.json`, not proven file-by-file (§6.5). | Declared boundary; carried unresolved by design. |
| **U-6** | info | **Oracle freeze ordering procedurally attested**: by in-file amendment text + `commands.json` sequencing, not re-derivable by hashing alone (§6.6). | Declared boundary; carried unresolved by design. |

## Not granted

`disclosure_adaptation` stays **unmapped**; `accuracy` stays **unproven**. This landing grants no extension of scope beyond the carrier: **register-row closure for REM-47/48/49 and B3 batch-2 promotion remain parent/owner decisions this landing does not take**; RF-3's P4 assertion stays owned by RF-3; W05B/W05C stay un-re-run; REM-49 stays out of production. **0 production writes** by this landing: `reviewer_report.md` + its `.sha256` sidecar untouched (0 bytes), no git write, no pytest/test-suite run, no signature produced.

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent), 2026-09-22, on the parent's dispatch.
- Status transition: `review_pending` → `accepted_scoped`, performed in `handoff.json` by this pass; the verdict itself was authored only at `reviewer_report.md` L3 by 独立复核 — never by the implementer and never by this file's author.
- Exactly three files written: `review.md` (created, this file), `handoff.json` (status + status_before_bookkeeping_fix + status_authority + bookkeeping + carried_findings appended + F-1 wording corrected in place with `*_historical_pre_verdict` preservation; all other pre-existing keys untouched), `evidence/B3-PREREQ/qualification.json` (created).
- sha256 before → after: `review.md` **none → reported to the parent** (a file cannot embed its own final hash); `handoff.json` **`d6f63633f0678c1ac6bebf35b19264161229b4009bf3d26886bcbc0e38db8778` (7813 B) → reported to the parent**; `qualification.json` **none → reported to the parent**. Post-write, `reviewer_report.md` re-hashes to `F367984B…B23C53` / 15544 B (0 bytes written to the carrier).
- `implementer_signed: false`; `implementer_never_signs_acceptance: true`; `verdict_is_transcribed_not_authored: true`; **bookkeeping transcription, adds no acceptance of its own**.
