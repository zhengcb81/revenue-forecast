# B3-I05C-delivery-fixes (a20260921-01) — carrier landing (bookkeeping transcription)

## VERDICT BLOCK (transcribed, not authored here)

- **verdict** = `ACCEPT` — with one new P3 finding (RF-1) and four documentation/precision
  findings (RF-2..RF-5), and with CF-1 accepted only as a *registered* carry.
- **status mapping** = `accepted_scoped` (scoped acceptance, not a clean bill; `disclosure_adaptation`
  stays `unmapped`, `accuracy` stays `unproven`).
- **carrier** = `reviewer_report.md` (this attempt) — written by the independent reviewer, not by the
  implementer and not by this file's author.
- **carrier sha256** = `3B8A9167BF0CAF163761D8702B619DFEFBE4F4EDB3EB2741EB5C58BDAB6E3DBE` (lowercase
  `3b8a9167bf0caf163761d8702b619dfebbe4f4edb3eb2741eb5c58bdab6e3dbe`) — **36110 B**, 534 LF-terminated
  lines + trailing LF (535 line starts), UTF-8 without BOM, 0 CR bytes (LF-only), single trailing LF.
- **pin** = `reviewer_report.sha256` (292 B) reads:
  `FINAL  sha256=3B8A9167BF0CAF163761D8702B619DFEFBE4F4EDB3EB2741EB5C58BDAB6E3DBE  bytes=36110  file=reviewer_report.md`
  and
  `BODY   sha256=71761E8E589C75BA89AF48DA0A5022309358ECAA2D3D0C388DF349970D9C253F  bytes=35345  file=reviewer_report.md (sections 1-10, before the BYTE PIN section was appended)`
  — verified read-only at landing: independent re-hash of the carrier == the sidecar's FINAL pin == 36110 B.
- **ruling location** = `reviewer_report.md` **§1 VERDICT L16–L42**; verdict sentence **L18–L19**;
  conditions **C1 L30–L34**, **C2 L35–L39**, no-promotion sentence **L41–L42**; CF-1 adjudication
  **§4 L267–L309** (its own conditions list L298–L309); findings **§5 L313** with **RF-1 L315–L356**,
  RF-2 L357–L362, RF-3 L363–L384, RF-4 L385–L394, **RF-5 L395–L404**, RF-6 L405–L415; reviewer-request
  statuses **§9 L493–L505** (all 8 CLOSED); one-line verdict **§10 L509–L516** (ACCEPT sentence L511);
  byte pin **§11 L520–L534**.
- **exact verdict line transcribed (verbatim, L18–L19):**

  ```
  **ACCEPT — with one new P3 finding (RF-1) and four documentation/precision findings
  (RF-2..RF-5), and with CF-1 accepted only as a *registered* carry.**
  ```

- **one-line verdict (verbatim, L511):** `**ACCEPT.** All nine claims verified by independent
  re-execution; the M4b vacuity proof is confirmed and strengthened; the FC-904 "no genuine conflict"
  ruling is correct and its counterfactual is now demonstrated; four of my five new findings are
  documentation/precision issues. The two things that must not be lost are **RF-1** (the conftest guard
  is weaker than advertised and one cited provenance file reports production bytes) and **CF-1's
  registration** (a carried finding that is not in the register is not carried).` (L511–L516)
- **byte proof** (0-based, region lengths exclude the terminating LF):
  verdict sentence L18–L19 bytes 971..1124 (154 B) `51ed25d9ce26ca7a3795f313b18a2b5f5dcaa2cfe4597bfac1bfc5d299dd9047`;
  §1 verdict section L16–L42 bytes 956..2702 (1747 B) `5ba4fd6dded87762eacb1258331acea8133b0276ec4e17d326acc26b550ce41a`;
  conditions block L28–L42 bytes 1630..2702 (1073 B) `d20b0fa0e2e9981fcc24bc40a2d1868c3d9c5ef6897e68a40ce1363474b9b728`;
  **C1 L30–L34 bytes 1708..2149 (442 B) `44cb1f1878eb767a7539e2696a2476ac942cd3a78fa2b6878f45b1ae6ac7f713`**;
  **C2 L35–L39 bytes 2151..2574 (424 B) `a2a6f13f0bece79f40c420064abaabfa10eb322e9c9910c081bd2c0e6e5efe5d`**;
  no-promotion L41–L42 bytes 2577..2702 (126 B) `b2b2812307cea70b8155403738fa21c3cd8b5a786cc681ebb250f398b1c71646`;
  §4 CF-1 L267–L309 bytes 18138..20702 (2565 B) `f02f7e06e4b79bdd07b3373ac2bf91d54320f047c9869cf16f4a5251477b6795`;
  CF-1 conditions L298–L309 bytes 19812..20702 (891 B) `417009561b8685a4299459fe91908721f9c5a23938700615b3bd5db2b1db24b5`;
  §5 header L313 bytes 20710..20723 (14 B) `c5f27c01b15a2feb5d69bd7a907b9388794e929d27d8ee3646898c135f0515ae`;
  **RF-1 L315–L356 bytes 20726..23666 (2941 B) `9d87689c04b98851079517a101f38c4e9621c9fe15901c0d75604b934b4421fa`**;
  **RF-5 L395–L404 bytes 26425..27116 (692 B) `d8382ed5fec71ec365190bff2953acca68f77a1b9fafda1bdce9194c2e3b61e5`**;
  one-line verdict L511–L516 bytes 34822..35343 (522 B) `02005a11ee68ccfcfb3da5ed250bc3f9b31efecd2aa4bcacb44f028fceea5121`;
  whole file minus trailing LF 36109 B `b76f4efccbbaa0c1d17df1623a2dcbba3a19e9ed5549efbb8131d72bff6933d7`.
  Region definition: 0-based byte offsets against the file as it stands at the carrier sha256 above.
- **reviewer** = independent reviewer subagent (carrier L5: "Reviewer: independent (not the implementer,
  not self-signed)"); L7 boundary: read-only, all re-runs in a throwaway copy under
  `%TEMP%\b3-review-r2\`; L531–L534: the only files this review created inside the plan tree are
  `reviewer_report.md` and `reviewer_report.sha256`.
- **nature of this file** = bookkeeping transcription. It **adds no acceptance of its own**. The verdict
  remains the original independent reviewer's, cited here by file + line + sha, never re-authored,
  never re-signed. The implementer never signs acceptance; this landing pass never signs acceptance;
  nothing here authorizes anything beyond restating the reviewer's ruling.

`review.md` did not previously exist in this attempt (no implementer stub); created by the carrier-backfill
bookkeeping pass on the parent's dispatch — not by the implementer and not by the reviewer.

## Conditions the original review attached (transcribed)

- **C1 (blocking for promotion, not for this verdict), L30–L34:** CF-1 must be entered in
  `REMEDIATION_REGISTER.md` before `iso/fixed/rf_scripts/company_wiki_source.py` (`7D1BD8F9…`) is
  promoted into `RF:scripts/`. The register had no CF-1 row and still listed REM-11..14 as `待修`;
  "A carried finding that lives only in an attempt directory is not carried".
- **C2 (recommended before this conftest is reused), L35–L39:** RF-1 — the attempt's own
  `iso/conftest.py` binding guard does not check what its docstring says it checks and its `sys.path`
  prepend order is the inverse of its stated intent; contained by in-test explicit binding, so no
  recorded result is invalidated, but "it must not be carried forward as 'the mechanism that prevents
  REM-12 recurring'".
- **No promotion from this verdict, L41–L42 (verbatim):** `**Do not promote \`7D1BD8F9…\` from this
  verdict.** Promotion is an owner decision; this report only adjudicates the evidence.`
- **CF-1's own conditions, §4 L298–L309:** (C1) add CF-1 to `REMEDIATION_REGISTER.md`; (required before
  promotion) fold the comment fix into the next batch that touches `source_preparation.py` or fix it at
  promotion time; (suggested wording) `producer_events = requested missing roles + their non-reusable
  ancestors`.

## Condition closure — RF-1 / RF-5 / CF-1 closed by card B3-PREREQ

Each of the three pre-promotion findings was closed by the accepted attempt
`execution_runs\B3-PREREQ\a20260922-01`, whose independent reviewer returned
**`accepted_scoped`** at its own `reviewer_report.md` **L3** (``**Verdict: `accepted_scoped`** — with one
non-blocking wording finding (F-1).``), pin-verified:

- **fixcard carrier** = `execution_runs\B3-PREREQ\a20260922-01\reviewer_report.md` — sha256
  `F367984B6BA6A8793C5A3F598686077CAF8AFCF413FE6356B69B47D4B7B23C53`, **15544 B**, 189 lines; sidecar
  `reviewer_report.md.sha256` (84 B, sidecar's own sha256
  `e5852d16205ad11f3055a32762bfd275ffa5bdb0dd681eb67522e724544fa655`) content
  `F367984B6BA6A8793C5A3F598686077CAF8AFCF413FE6356B69B47D4B7B23C53  reviewer_report.md`.
- **fixcard carrier-landed files** = `B3-PREREQ\a20260922-01\review.md` **14706 B**, sha256
  `36939B189343C04FDE68EB2E8AF7D345F93A82B1B80333E403F3D945F7C8C80A`; and
  `B3-PREREQ\a20260922-01\evidence\B3-PREREQ\qualification.json` **17258 B**, sha256
  `47374014B5B7EEFD6D360F1B9D441F3D55A48BAEEB524125BB07DD0F3AB05200`.

| this card's finding | original carrier lines | closed by (B3-PREREQ) | fixcard claim range | fixcard evidence |
|---|---|---|---|---|
| **RF-1** (P3) — `iso/conftest.py` guard does not implement its own claim; `sys.path` order inverted; one cited provenance file reports production bytes | `reviewer_report.md` L315–L356; condition C2 L35–L39 | REM-47 / RF-1 fixed: single prefix assignment `sys.path[:0] = list(PATH_ORDER)` + origin check (`find_spec_origin == expected`, `sys.path[0] == PATH_ORDER[0]` in fixed mode); provenance refuses last-writer-wins (`conflict=true`, first write kept, full `writes` history) | fixcard `reviewer_report.md` §1 **L30–L58** | `evidence/rem47_guard_baseline_RED.txt` (RED on B3 baseline: 2 failed / 2 passed — P2+P3), `evidence/rem47_guard_fixed2_GREEN.txt` (4 passed), `evidence/rem47_provenance_baseline_RED.txt`, `evidence/rem47_provenance_fixed2_GREEN.txt`, `evidence/mutation_MUT1_guard_order_RED.txt`, `evidence/mutation_MUT2_provenance_RED.txt` |
| **RF-5** (P3, bounded) — `after/integrity.json` does not verify the I-05-C oracle (`expected_frozen` = literal `NOT_REHASHED`) while `handoff.json:188` claims "every frozen hash" compared | `reviewer_report.md` L395–L404 | REM-48 / RF-5 fixed with premise correction: claim located at `handoff.json:188` (0 matches in `decision.md`); census = 4 `expected_frozen`, exactly 1 `NOT_REHASHED` at `after/integrity.json:23`, flag kept and quoted; superseded wording retained (`CEE4B0DD…` pre-correction copy) → corrected `E33D82A9…`; fixcard reviewer additionally re-derived `I-05-C/a20260919-01/oracle.md = E4004563…` + git-clean + empty `git diff 8b7229c3 HEAD` | fixcard `reviewer_report.md` §2 **L60–L87** | `evidence/rem48_flag_census.txt`, `evidence/rem48_verification.txt`, `evidence/rem48_superseded/handoff.json.pre-correction`, `changes.diff` (diff 3) |
| **CF-1** (P3, carried) — `RF:scripts/source_preparation.py:134-138` comment asserts the old DAG-closure rule; ruling "ACCEPT AS CARRIED — conditional on registration (C1)" | `reviewer_report.md` §4 L267–L309 (conditions L298–L309) | REM-49 / CF-1 fixed: `iso/fixed2/rf_scripts/source_preparation.py:138` = the reviewer's suggested wording verbatim ("requested missing roles + their non-reusable ancestors (never a blind full recompute)"); comment-only (exactly 1 differing line pair, both `#`), `ast.dump` identical, `compile()` OK both sides; FC-904 parity 16 nodes/side, per-node identical | fixcard `reviewer_report.md` §3 **L89–L106** | `evidence/rem49_comment_fix_GREEN.txt`, `evidence/rem49_fc904_baseline.xml` / `rem49_fc904_fixed2.xml`, `evidence/rem49_fc904_parity.json`, `evidence/mutation_MUT3_comment_RED.txt` |

**Closure statement:** RF-1, RF-5 and CF-1 are **CLOSED as findings** by B3-PREREQ's accepted fix work
(fixcard verdict `accepted_scoped`, carrier sha256 `F367984B…B23C53`, carrier landing `review.md`
`36939B18…` / `qualification.json` `47374014…`). The **owner-side halves are not closed by this
transcription**: CF-1's *register row* (C1) and the promotion of `7D1BD8F9…` remain parent/owner calls,
exactly as B3-PREREQ's own review states. This section records closure evidence; it adjudicates nothing.

## B3-PREREQ's conditions carry over into this card's scope (transcribed from fixcard `reviewer_report.md` §9, L183–L189)

1. **REM-47/48/49 register-row closure and B3's promotion (batch 2) are parent/owner calls.** That
   review accepts the *attempt*; it does not adjudicate register closure and does not authorize
   promotion — so on this card, C1's register row and the `7D1BD8F9…` promotion stay owner calls.
2. **RF-3's location-dependent assertion is still present** in the carrier
   (`test_fc904_artifact_selection.py:379`, `assert "B3-I05C-delivery-fixes" in str(resolved) or _BYTES
   == "production"`) — P4, owned by RF-3, fails identically in any relocated tree; correctly not edited.
3. **Vendored W05B/W05C suites were not re-run** in that review (fixcard §6.4) — and were not re-run by
   this landing either; they stay a declared bounded gap.
4. **REM-49 remains deliberately not landed in production** (production `source_preparation.py`
   `37A3EEAE…` == B3-accepted `37A3EEAE…`); landing it is a separate production change if ever desired.

Also carried, unchanged from this card's own review: **RF-2/RF-4/RF-6** and the §6 unverified list are
*not* closed by B3-PREREQ (B3-PREREQ fixed REM-47/48/49 = RF-1/RF-5/CF-1 only); they remain as the
original reviewer recorded them.

## Not granted

`disclosure_adaptation` stays **unmapped**; `accuracy` stays **unproven**. This landing grants no
extension of scope beyond the carrier: **register-row closure (C1) and promotion of `7D1BD8F9…` remain
parent/owner decisions this landing does not take**; RF-3's P4 assertion stays owned by RF-3; W05B/W05C
stay un-re-run; REM-49 stays out of production. **0 production writes** by this landing:
`reviewer_report.md` + `reviewer_report.sha256` untouched (0 bytes), no git write, no test-suite run,
no signature produced.

## Bookkeeping

- Landed by: carrier-backfill bookkeeping executor (delegated subagent), 2026-09-22, on the parent's
  dispatch.
- Status transition: `review_pending` → `accepted_scoped`, performed in `handoff.json` by this pass;
  the verdict itself was authored only at `reviewer_report.md` L18–L19 by the independent reviewer —
  never by the implementer and never by this file's author.
- Exactly three files written in this attempt: `review.md` (created, this file),
  `handoff.json` (status + `status_before_bookkeeping_fix` + `status_authority` + `bookkeeping` with
  the RF-1/RF-5/CF-1 condition-closure map, plus `reviewer_status`/`next_action` superseded with
  `*_historical_pre_verdict` retention; all other pre-existing keys untouched; pre-image 26076 B /
  sha256 `E33D82A9E418A7CDFE04FE17CE435FF2F48EA06C27CAF096A9AB590C4683A493`),
  `evidence/B3-I05C-product-fixes/qualification.json` (created).
- sha256 before → after: `review.md` **none → reported to the parent** (a file cannot embed its own
  final hash); `handoff.json` **`E33D82A9E418A7CDFE04FE17CE435FF2F48EA06C27CAF096A9AB590C4683A493`
  (26076 B) → reported to the parent**; `qualification.json` **none → reported to the parent**.
  Post-write, `reviewer_report.md` re-hashes to `3B8A9167BF0CAF163761D8702B619DFEFBE4F4EDB3EB2741EB5C58BDAB6E3DBE`
  / 36110 B (0 bytes written to the carrier).
- `implementer_signed: false`; `implementer_never_signs_acceptance: true`;
  `verdict_is_transcribed_not_authored: true`; **bookkeeping transcription, adds no acceptance of its own**.
