# REGISTRY-CLOSURE review.md — CARRIER LANDING (verdict transcribed; never self-signed)

Status: **`accepted_scoped`** (`ACCEPTED-SCOPED — signed`). The independent reviewer (独立复核)
wrote the verdict in `reviewer_report.md` (the byte-pinned carrier), **not** in this file. This
file is the carrier-landing bookkeeping transcription of that verdict. **It adds no acceptance
of its own** (transcription-only). `review.md` did not previously exist in this attempt (no
implementer stub); it was created by this carrier-landing pass — not by the implementer and not
by the reviewer. Read `reviewer_report.md` itself for the reviewer's own words (§0–§12).

- Card: **REGISTRY-CLOSURE** (goal-item③ 残留排干 — 10 zero-disposition rows + 10 implicit
  closure rows + 16 registered-unfixed items + REM-78/79 numbering note + REM-95/96)
- Attempt: `<PLAN>\execution_runs\REGISTRY-CLOSURE\a20260923-01`
- Landing pass: 2026-09-23/24, delegated bookkeeping subagent of parent session
  `session-bfecd191-fbc3-4a66-8ed1-6562479bf102`

## 1. Verdict block (transcribed — adds nothing)

- Verdict: **ACCEPTED-SCOPED — 签署（signed），附 2 条非阻断 findings + 3 条 INFO** — carrier
  `reviewer_report.md` **line 9** (§0 Verdict, lines 7–14).
- **N = 1**: a single review round, a single carrier, accepted on the first review — no prior
  round exists for this card; nothing was superseded by a later verdict.
- Verdict author: **独立复核** (delegated independent reviewer, sibling of the implementer;
  carrier §12:129 — signer = the independent reviewer of the parent session; **实现者未自签
  保持**: `binding.json:2 implementer_signed=false`, untouched).
- This landing **does not self-sign**: `implementer_signed: false`,
  `implementer_self_acceptance: false`, `implementer_never_signs_acceptance: true`,
  `verdict_is_transcribed_not_authored: true`. The verdict is transcribed, not authored.

### Carrier (byte-pinned; re-hashed read-only at landing)

| field | value |
|---|---|
| carrier file | `reviewer_report.md` (round 1 = only round) |
| sha256 | `b7790be7f3f9d42995790af71f2310b6a06d7193f3951ab8efff5f2cebd78a05` — independent re-hash at landing **MATCHES** the dispatch pin exactly |
| bytes / lines | 19887 B / 135 lines (UTF-8 without BOM; LF-only, 0 CR; single trailing LF) |
| pin sidecar | `reviewer_report.sha256` — present, 85 B, sha256 `2e05b8ef7949cabb7ca6211bf66a4270352588606d86b8a7be5897fe6c777caf`, content `b7790be7f3f9d42995790af71f2310b6a06d7193f3951ab8efff5f2cebd78a05 *reviewer_report.md` — **matches** the re-hash ⇒ sidecar verified, 0 bytes written |
| verdict line | 9 — `**ACCEPTED-SCOPED — 签署（signed），附 2 条非阻断 findings + 3 条 INFO。**` — byte region [665, 753] incl. trailing LF, 89 B, sha256 `3f8465db4067431eb4ac59a9809512cfa949b82a71020161c4eb21d4e11e2cd7` |
| verdict section (§0) | lines 7–14, bytes [650, 1734], 1085 B, sha256 `688aa34a2efde40d1241c898747a59559fdbe0e7968ec774c81198dcfd2ad4cb` |
| scope section (§1, incl. owner post-close vote transcription) | lines 15–23, bytes [1735, 2889], 1155 B, sha256 `cc19c76db6e3a34c7c6284c1fd49087c7087b935c37fe3dcc3dacedf320103b2` |
| findings section (§8: F-R1..F-R5) | lines 92–101, bytes [14039, 15917], 1879 B, sha256 `d0edbe7d103aeb0a7c7fefb9b0b53f996bdf46334e0c3a7d788ed74971c30d87` |
| unverified section (§9) | lines 102–109, bytes [15918, 17038], 1121 B, sha256 `09bd0addc97ab0e4bc2ba1a719bffd5e5f5f3f61c0d4b96b66572c1865778f7f` |
| boundary section (§10) | lines 110–117, bytes [17039, 17904], 866 B, sha256 `881dc916c80313cbd34025a35c538a2dbc3f8aa7a4e38c1b7279aaada2dd39c2` |
| scope-if-accepting section (§11) | lines 118–125, bytes [17905, 19087], 1183 B, sha256 `d70855d8add07563607039cbe512f588b299a41ea8bdd503b597b6624300a458` |
| signature section (§12 + REM-79 self-check) | lines 126–135, bytes [19088, 19886], 799 B, sha256 `cda55a330901956cd476ec4cef20818e5261036cbc75f3e5d9c2386063b0e94a` |
| byte region definition | 0-based byte offsets against the file at the recorded sha256; regions include internal LFs and exclude the final LF (verdict-line region includes its trailing LF) |
| producer | independent reviewer (独立复核) — never the implementer; carrier is the sole verdict authority |

Landing-time re-verification: carrier re-hash **MATCH** (dispatch pin == sidecar == on-disk);
byte ranges recomputed from raw bytes; **0 bytes written** to `reviewer_report.md` and
`reviewer_report.sha256` by this pass.

## 2. Oracle freeze — recompute MATCH + freeze-first (transcribed + re-hashed)

- **Recompute**: `oracle.md` sha256 at landing = `16e4f2a07873a6a42342c57048ead393dd986660b10b1927e8d78916c44d156f`
  — **MATCHES** `oracle.sha256` sidecar content **and** `binding.json:6` byte-for-byte (carrier §2).
- **Freeze-first proven**: `oracle.md` mtime **22:37:42** precedes every disposition artifact
  (`changes.diff` 22:51:24, `decision.md` 22:54:10 pre-append, `binding.json` 22:55:23); the
  `oracle.sha256` sidecar itself landed at 22:55:22 (batch end, honestly logged as commands.md
  step 20) — content freeze happened first, proven by mtime + hash consistency (this is exactly
  carrier finding **F-R5**, INFO).
- `binding.json` also re-verified at landing: `changes_diff_sha256` = `fc3cf7412774e220960b26110a522962a9918fe0f51cf1327823ad2935d6dd2b` **MATCH** (live `changes.diff`);
  `decision_sha256` = `a68ed77fe922f768a845a6497000de93baab922f1d2128ffe9bbc5727fe79353` ==
  pre-erratum `decision.md` **MATCH** (see §10 bookkeeping: the commissioned F-R erratum append
  is the only delta after that pin; `binding.json` itself untouched).

## 3. Zero-source-writes — byte-proven (transcribed + re-hashed at landing)

Both bound targets re-hashed read-only at landing:

| target (binding.json targets) | frozen sha | landing re-hash | result |
|---|---|---|---|
| r6 generation tree `execution_runs/I-14-D/a20260919-01/iso/product_narrow_r6/src/company_wiki/source_catalog/observability.py` | `2f6449949c76b97c636d5d50e2ca848403116a85a1858bb9ba8f5a2808362464` | same | **MATCH** |
| production copy `C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\observability.py` | `edcbeccb9b13778efe2d80c58a401c345856bf04220462e1fbbe56ea96111f4e` | same | **MATCH** |

⇒ the card's zero-product-write claim stands byte-proven (carrier §2/§6): the only code deltas
ever produced are inside `changes.diff` (not applied to any tree), and the reviewer's own
porcelain read (§6) attributed 0 product writes to this card (its sole attributable artifact =
`?? .planning/…/REGISTRY-CLOSURE/`, the allowed write domain).

## 4. Independent 16-row spot check across all five classes (carrier §3 — transcribed)

Coverage line (carrier): **CLOSED-NOW ×5 rows, SUPERSEDED ×4, WORK-CARD ×4, OWNER-BLOCKED ×2,
EXTERNAL-BLOCKED ×1 = 16 rows ≥ 10, all five classes covered** — independent evidence, not the
card's self-attestation:

| # | row / class | independent evidence (reviewer's own) |
|---|---|---|
| 1 | A1 REM-05 / CLOSED-NOW | J1 = 2 comment-insertion hunks × 2 targets; reviewer-ran AST: `_VALUE` 1 assign / 0 loads → DEAD on both trees; `evidence/rem05_behavior_identity.txt` 20 shapes `all_identical=true` + compile OK; comment-only (+11/−2 ×2, 0 non-comment lines) |
| 2 | A2 REM-06 / WORK-CARD | `key_is_credential_context` probe: `token2/secret2/password2/api_key2=[false,false]`, suffix keys stay plaintext ⇒ WC-1 routing stands |
| 3 | A3 REM-07 / WORK-CARD (degradation = sweep⑥) | reviewer's own probe on r6 tree: `Authorization:\ndoc=17\nstage=summarize` → `Authorization:\n<redacted>` — **both keys swallowed**; `I-14-D handoff.json:144` "the narrowing saves stage=summarize" falsified on r6 ⇒ CONFIRMED |
| 4 | A4 REM-08 / SUPERSEDED | `I-14-D binding.json:72` verbatim "…claimed 'one-line tree-pointing change'. **It never did**…" + conftest `783b1774…`/275 B ✓ |
| 5 | A5 REM-16 / CLOSED-NOW | `evidence/rem16_command_runs_registration.txt` (7-dir list + 7th `r2-verify-before/`); independent disk check: exactly 7 subdirs incl. `r2-verify-before` ✓ |
| 6 | A7 REM-25 / SUPERSEDED | `OWNER_DECISIONS:365` verbatim "E-1: 150/60", `:375` ruling, `:400` in-effect; I-14-F-R1 decision §1–§3: 210/124/86 → 210/150/60 + real-number docstring + 60/61 boundary double-pin ✓ (audit's "choice never landed" = misreading) |
| 7 | A8 REM-30 / SUPERSEDED | I-14-F-R1 decision:189-191 "…are **fixed directly**…"; production test header :11/:17 + cases :83/:86 pin 60/61 both halves ✓ |
| 8 | A9 REM-35 / SUPERSEDED | `I-14-I handoff.json.derived_keys_discharge…` now reads "CORRECTED BY THE CARRIER-LANDING PASS per reviewer finding F-1 … the gate's rc 0 must NOT be read as 'the derivation is gate-proven'" ✓ (old text retained marked SUPERSEDED) |
| 9 | B1/B2 REM-09/10 / CLOSED-NOW | I-14-I handoff: `accepted_scoped`, gate `ok=true case_count=14 runner_rc=0`, `review_pending→accepted_scoped` transition; git `980c9b7a` "I-14-I complete (14-case gate rc 0…)" ✓ |
| 10 | B4 REM-24 / OWNER-BLOCKED (sweep④ reverse misjudgment) | M14 `oracle.md:323/334/336/380` verbatim "D/E 层是否追认由 owner 决定" `carried_not_resolved` / "只登记，不代裁" ⇒ registration ≠ ratification CONFIRMED (post-close §23 vote later lifted it — §8 below) |
| 11 | B10 REM-78 / CLOSED-NOW (mechanized) | `REM79-MECHANIZATION\a20260922-01\tools\check_domain_assertions.py` on disk; register :760/:827/:837 record v1.2.0-correction2; `:353` stale "仍欠机制化"; `:436` mislabel → D1 disambiguation stands ✓ |
| 12 | C16 F12 / WORK-CARD + OWNER dual-track | `SA-DEFECT:165` "断言在返回后开火" vs `I-09-C handoff:54` "rc=120 … CPython stdio flush failure at finalization…" + `pipe_controls.json` A=0/B=120/C=0 + `probe_f12.py:65` stderr mislabel ⇒ mechanism erratum (sweep⑦) + dual routing CONFIRMED |
| 13 | C10a R5-03 / CLOSED-NOW | `reviewer_report_r5.md:471-481` unique-reading prescription matches J2 replacement verbatim; `evidence/r503_patch_production.diff` present; post-apply 4 lines comment-only + compile OK ✓ |
| 14 | D1/D2 / CLOSED-NOW + WC-5 | same row evidence as #11; WC-5 spec at decision:96-97 + register:1717 ✓ |
| 15 | E1 REM-95 / WORK-CARD (WC-6) | register:1312 `C1(F-REV-1)` verbatim matches decision E1 (`_to_scanner_candidate` drops remediation reason → `locations.error=NULL`); WC-6 spec decision:99-100 + register:1718 ✓ |
| 16 | E2 REM-96 / EXTERNAL-BLOCKED | register:1307 holdout: "criterion-(i) 合格 ∩ https-source_url-capable = **0**" (10,596 items) + :1313 `F-REV-7` register row (= REM-96's text source) ⇒ data-track external routing stands ✓ |

## 5. Count reconciliation (carrier §4 — CONFIRMED)

- **SA-DEFECT version** (`report_SA-DEFECT.md:185`): the "16" string enumerates, flattened,
  **4+1+3+5+6+3+2+1 = 25 units**.
- **AUDIT-GOAL version** (`audit_report.md:168`): same string **without REM-62** = **24 units**.
- Neither self-described "16" matches either enumeration; the two versions differ by **exactly
  REM-62** ⇒ **25 vs 24** ✓ as the card states.
- The card's own "all 25 units disposed" recomputes: C-group **17 disposition rows**
  (C5/C6/C9a–e/C10a–f/C12/C14/C15/C16) **+ 8 cross-reference units** (C1–C4, C7, C8, C11, C13)
  = **25** ✓.

## 6. 42 = 40 mapping recompute (carrier §5 — CONFIRMED, no silent row loss)

- decision table: **45 table rows − 3 non-disposition rows** (the `C1–C4` cross-reference row,
  the `C9`/`C10` group-header rows) = **42 disposition rows** (ids: A1–A9, A10①, A10③ | B1–B10 |
  C5, C6, C9a–e, C10a–f, C12, C14, C15, C16 | D1, D2 | E1, E2).
- **40 mandate items → 42 rows**: A 10→11 (A10 split ①③), B 10 (REM-79 comparison row lives in
  D2), C 16→17 (C9/C10 expand per ID; cross-references not double-counted), D 1+1, E 2→2; **no
  oracle item missing** (A1–A10 / B1–B10 / C1–C16 / D / E all mapped).
- class-label sum = 16+13+11+2+1 = **43 = 42 rows + 1**: the exact excess is **C16/F12 — one
  physical row with two class labels** (see F-R3). Register §八十四:1658 count row agrees with
  decision and handoff (16/13/11/2/1) — three-way consistent (landing re-read ✓).

## 7. changes.diff — comment-only proof + py_compile (carrier §6) and the F-R1 apply experiment

- Structure: **4 hunks = 2 comment-level fixes × 2 targets** (J1 = REM-05 annotation ×2;
  J2 = F-REV-R5-03 rewrite ×2) ✓ matches its header note.
- **Comment-only proof**: difflib comparison of applied result vs original per target →
  **+11 / −2 per target, added_non_comment=0, removed_non_comment=0 → COMMENT-ONLY PASS**;
  **py_compile OK ×2** after apply.
- **`git apply --check` as delivered = FAIL rc=128**:
  `error: patch fragment without header at line 22: @@ -284,6 +284,15 @@` — root cause
  `changes.diff:20 = "#--- a/iso/…"` (first file header comment-prefixed; :39/:58/:72 are normal
  bare `--- `) → **F-R1** (landing re-read of `changes.diff:20` ✓ confirms the `#--- ` prefix).
- **After the exactly-one-line fix (`#--- `→`--- `)**: `--check rc=0` → `apply rc=0` →
  `py_compile OK ×2`, inside a `%TEMP%` mirror (`%TEMP%\rc_a20260923_01_apply*`) — patch content
  valid, anchors in place, behavior surface unchanged. ⇒ **apply the header fix first at landing**
  (merge-wave precondition, §10).

## 8. Sweep 5/7 confirmed (carrier §7) + owner-vote integration (carrier §1/§11)

- **Sweep spot (carrier §7 heading "spot 5/7")**: items ① REM-25 ② REM-30 ③ REM-35 (three
  stale-OPEN misjudgments) CONFIRMED; ④ REM-24 reverse misjudgment (the most dangerous class)
  CONFIRMED; ⑥ REM-07 degradation CONFIRMED; ⑦ F12 mechanism misstatement CONFIRMED; ⑤ stale
  status reads: REM-08 CONFIRMED on spot — closing line: **7/7 sampled, 6 CONFIRMED**, the sole
  item not re-derived verbatim being REM-18's 4/4 prefix size series (explicitly §9.1 unverified).
- **Owner-vote integration (OWNER_DECISIONS §23, :481–486, landed after card close; re-read at
  landing ✓; card table rows untouched)**:
  1. **REM-24 = 追认** (owner verbatim "1，追认") ⇒ M14 OQ-03 D/E layers signed off as-is, no
     separate signed covenant needed ⇒ **REM-24 = CLOSED (owner-ratified)**; the card's
     OWNER-BLOCKED for REM-24 lifted externally.
  2. **F12 = 记为待修** (owner verbatim "2，记为待修") ⇒ frozen rc domain **stays {0,2}**;
     observed **rc=120** (finalization flush failure self-report) = **recorded as a product
     defect to fix** ⇒ **WC-4-RC120 dispatched — WC-4 is running** (flush-failure path brought
     in-domain rc=2 + error text retained; SA-DEFECT mechanism misstatement corrected with the
     fix).
  - Result recorded by the carrier: **card-internal OWNER-BLOCKED 2 → 0 achieved post-close**
    (transcribed in carrier §1/§11; no card row rewritten). Register §八十七 (:1745–1749)
    carries both votes (re-read at landing ✓).

## 9. F-R1..F-R5 dispositions (carrier §8 → landed in decision.md erratum)

| ID | level | disposition at landing |
|---|---|---|
| **F-R1** | **MEDIUM** (blocks the `git apply` path, not the verdict) | `changes.diff:20` first header `#--- a/…` ⇒ as-delivered `git apply --check` rc=128; content fully valid (1-line fix → check rc0 / apply rc0 / py_compile OK×2 / comment-only PASS, reviewer-proven). **Action = first item of the J1/J2 merge-wave list: fix that one line before apply** (or commands.md manual-insert fallback). **Landed verbatim in `decision.md` § "F-R erratum (landing)" item 1.** |
| **F-R2** | LOW | Stale section numbers: `decision.md:120` preview heading says §七十九 and `handoff.md:30` says "本节号=七十九"; the actually appended register section = **§八十四** (`commands.md` step 21 correct; §79 taken by the parent). **Landed erratum-style as item 2** (append-only; sealed rows untouched; register itself correct — heading ×1 at :1655, count row :1658, §85/§86 collision corrections on file :1731/:1741, all re-read at landing). |
| **F-R3** | INFO | F12 physically one row with two class labels (class labels 43 = 42 + 1; totals close, no drops) — **landed as item 3**, downstream reads "rows 42 / labels 43 (F12 double-counted)". |
| **F-R4** | INFO | Register line citations drift +1 from concurrent parent appends (REM-95/96 now :1312/:1313 — landing re-read ✓) + `register_sha256_at_freeze` not re-derivable by design (append-only) — **landed as item 3 (F-R4)**; anchor on row text; no action. |
| **F-R5** | INFO | `oracle.sha256` sidecar written at batch end (22:55, honestly logged commands.md step 20; content-freeze-first proven by oracle.md mtime 22:37 + hash consistency) — **landed as item 3 (F-R5)**; no action (convention note for the next card). |

## 10. Unverified — the carrier's 5 explicit items (§9), not used as pass basis

1. **REM-18's 4/4 prefix size series** (M05 14790→18889 etc.) not re-measured — its
   `E1E7-ERRATA-LANDING accepted` conclusion taken from the register/re-review record on file.
2. **`register_sha256_at_freeze` (468dc316…)** cannot be recomputed after the fact (register
   append-only advanced + concurrent parent appends) — **not re-derivable by design, not a defect**.
3. **REM-21 (B3) / REM-56/59/60/61 (B5–B8) / REM-62 (C5) / REM-64 (B9) / C9d audit §10 family /
   REM-67③ "N5f–N5w/R7a–R7d all non-shape" enumeration / REM-06 "95-row rule table" count**: not
   re-derived verbatim (out-of-class sampling already ≥16 rows); their evidence pointers are in
   the decision rows; remaining carrier evidence beyond both audit lists = per what is on disk
   (handoff carried states the same).
4. **C6 "review.md `overall PASS` 0 hits"** not re-grepped (the row is CLOSED-NOW with a
   disclosure; the disclosure text is in the decision row).
5. **No script inside any historical attempt was executed** (recovery.md:14 self-imposed
   discipline, honored by the reviewer) — REM-78's "five-round live self-scan" details taken from
   the register record (tool exists + vocabulary iteration table checked).

## 11. Boundary attestation (carrier §10, transcribed)

- **Zero network verbs**: the card's whole commands log is read/grep/hash/difflib/`git diff
  --no-index` (read-only, discarded after a CRLF-warning polluted its output — commands.md step
  19); the reviewer likewise ran zero network. **This landing pass: zero network.**
- **Zero stateful git**: the card used **`git diff --no-index` only** (read); the reviewer used
  `git show` / `git status --porcelain` (read) and `git apply` inside `%TEMP%` mirrors (outside
  the repos). **Both repos' HEAD/index untouched. This landing pass ran no git command at all**
  (no git verbs of any kind).
- **Attempt self-consistency**: F-R2 was the only internal record inconsistency (preview/handoff
  vs terminal section number) — now carried by the decision erratum; everything else
  oracle↔binding↔decision↔handoff↔register hashes/counts/classes is mutually consistent.
- **Handoff defaults intact**: `disclosure_adaptation: unmapped`, `accuracy: unproven`,
  `verdict_authority` was "待独立 reviewer" pre-verdict (now superseded by the carrier, recorded
  in `handoff.json.*_historical_pre_verdict`).
- **Never self-signed**: `implementer_signed=false` untouched; the signature in the carrier §12
  belongs to the independent reviewer; this file signs nothing.

## 12. Scope-if-accepting (carrier §11 — transcribed)

- **42-row disposition table transcribed into register §八十四** as the single row-level
  backfill (historical rows zero-modified; heading exactly once at :1655 — landing re-read ✓).
- **Owner routing terminals**: REM-24 = CLOSED by OWNER_DECISIONS §23 (追认); F12 numeric domain
  = ruled ({0,2} kept, rc=120 to fix) → **WC-4 running (WC-4-RC120 dispatched)**; card
  OWNER-BLOCKED 2→0 achieved post-close (§8 above).
- **WC routing** (register §八十六:1739 + §八十七): **WC-1 dispatched** (I-14-D-R8, `d28ac9ef`),
  **WC-6 dispatched** (REM-95-ADAPTER-DISPATCH, `9d8cb419`), **WC-4 dispatched after the owner
  vote** (its former owner-gated precondition lifted); **WC-2 / WC-3 / WC-5 queued** for a slot
  (specs taken on demand from this card's `decision.md`).
- **BOOKKEEP +2 landed**: ① R5-06 note — `_review_i14d_r5_20260922/` added to git in the
  BOOKKEEP-REPAIR batch; ② REF §八十四 **full-name cross-reference** (citations carry section
  titles for disambiguation, per the §35 discipline).
- **J1/J2 hunks = the merge-wave list**: J1 (REM-05 comments ×2 targets) + J2 (R5-03 unique-
  reading rewrite ×2 targets), **landing precondition = the F-R1 header-line fix first**; each
  use re-reviewed independently before application (handoff carried-2 says the same).

## Not granted

`disclosure_adaptation` stays **unmapped**; `accuracy` stays **unproven**; no production write
authority (0 product bytes by this pass); no WC implementation; no register/history writes; and
**this file grants nothing** — it is bookkeeping transcription only.

## Bookkeeping (sha256 before → after, this pass)

| file | before | after |
|---|---|---|
| `decision.md` | 23413 B / `a68ed77fe922f768a845a6497000de93baab922f1d2128ffe9bbc5727fe79353` | 26557 B / `5e2759683489eb09dece52ca68a0cf8d5ad4b05fc88b340251e53bbe018a23cd` — pure append proven: first 23413 bytes re-hash to the exact pre-image sha (`append_only=True`); sole delta = the `## F-R erratum (landing)` section |
| `review.md` | did not exist (no stub) | created by this pass (sha in `handoff.json` / `qualification.json`) |
| `handoff.json` | did not exist | created by this pass (sha in `qualification.json`) |
| `evidence/REGISTRY-CLOSURE/qualification.json` | dir + file did not exist | created by this pass |

- **Exactly three files written** (`review.md`, `handoff.json`,
  `evidence/REGISTRY-CLOSURE/qualification.json`) **plus the one commissioned decision append**.
- **Untouched (re-hashed/read-only)**: `reviewer_report.md` + `reviewer_report.sha256`,
  `oracle.md` + `oracle.sha256`, `binding.json`, `commands.md`, `changes.diff`, `recovery.md`,
  `handoff.md` (pre-image 2568 B / `db22321d38a8f6a06e35437feb004fb7d091bd5bd921e45eae5d642d0e805b38`),
  all `evidence/*` originals, `fix_rem05/*`, `fix_r503/*`, and `REMEDIATION_REGISTER.md`
  (zero register writes by this pass).
- **No git, no network, no self-signing.**
