# I-06-A / a20260922-02 review.md — CARRIER LANDING (verdict transcribed; never self-signed)

Status: **`accepted_scoped`** (round 2). The independent reviewer (独立复核) wrote the verdict in
`reviewer_report_r2.md` (the byte-pinned carrier), **not** in this file. This file is the
carrier-landing bookkeeping landing of that verdict: it transcribes the reviewer's verdict so the
attempt's `review.md` slot exists. **It is a bookkeeping transcription, adds no acceptance of its
own.** Round-1's verdict `changes_required` is preserved as history below and in
`handoff.json.status_history`; the round-1 report was never edited. Read `reviewer_report_r2.md`
itself for the reviewer's own words (§1–§7). No verdict, review, or acceptance was authored in
this pass; `implementer_signed` stays `false`.

`review.md` did not previously exist in this attempt (no implementer stub to preserve); this file
was created by the carrier-landing pass — not by the implementer and not by the reviewer.

## Verdict block (transcribed)

- Card: **I-06-A** / `a20260922-02` — 安全阻断前登记可持久恢复的需求 (persistent demand registration);
  plan `2026-09-19-three-project-history-audit`, path `<PLAN>\execution_runs\I-06-A\a20260922-02`.
- **Round-2 verdict: `accepted_scoped`** — the reviewer's literal label at carrier **line 10**:
  `## Verdict: **accepted_scoped** (round 2)`; scope stated in §7 (lines 94–103) per round-1's
  re-review path (i)–(iv) plus the dispatch's GUARD-MERGE coordination note. Reviewer's findings
  block (lines 105–109): **no new blocking finding**; 2 non-blocking notes.
- **Round-1 verdict preserved as history: `changes_required`** — carrier `reviewer_report.md`
  line 10, **30045 B / `4c3f3f3d43a63e413eb808e7bcc8512b12eb31a4e71f69ae3a8226e0a6b2e26b`** (175
  lines), pinned by `reviewer_report.sha256` (85 B, content matches). Sole blocker was finding 1
  (NaN ttl widening bypass). **UNTOUCHED**: this pass re-hashed it read-only before and after the
  landing; 0 bytes written.
- Verdict author: **独立复核** — the round-2 independent review session (carrier lines 3–6 record
  the reviewer role and that its sole outputs are `reviewer_report_r2.md` + its sidecar; line 3
  records that `handoff.json` stayed untouched because the implementer never self-signed).
- This pass **does not self-sign**: `implementer_signed: false`,
  `implementer_never_signs_acceptance: true`; the verdict is **transcribed, not authored**
  (`verdict_is_transcribed_not_authored: true` in `handoff.json.status_authority`), and the
  transcription **adds no acceptance of its own**.

### Carrier (byte-pinned)

| field | value |
|---|---|
| carrier file | `reviewer_report_r2.md` (round 2) |
| sha256 | `2f685f0f6fe06795bbf572518a640526a951c1f33c18e7c3994b579145910e3f` |
| bytes / lines | 21629 (matches the dispatch figure exactly) / 127 (UTF-8 no BOM, LF-only, 0 CR, single trailing LF) |
| pin sidecar | `reviewer_report_r2.sha256` (87 B, sha256 `b8f30e9c0dcfacdb0d3fe128211e809e22a2b749e8f0f5af3e1c7f78bbc04395`, content `2f685f0f…10e3f  reviewer_report_r2.md`) — **content-match** against this pass's independent re-hash ⇒ 0 bytes written |
| verdict line | 10 (`## Verdict: **accepted_scoped** (round 2)`), bytes 1022..1062 inclusive (41 B), sha256 `5428d16b09e7bc714d8afdbf29d222803f363c557bbe961739098a8d73a480ec` |
| verdict section (lines 10–14) | bytes 1022..1882, 861 B, sha256 `dab9c4544f6c227af6f3acb3ca56bfe8132304f9937b7d2f2fd84df4c51dc6d6` |
| §1 round-1 carrier integrity (18–21) | bytes 1890..2646, 757 B, sha256 `16d061576369b3859e28e8d5448e6d4229687cd5c6745a81db20fbc716c60a20` |
| §2 F1 fix (23–39) | bytes 2649..6232, 3584 B, sha256 `e12dfe68463abd01a9a2c1cf6b2fc687539d858b1f20782cb10fd2f74d1231c9` |
| §3 round-2 discipline (41–66) | bytes 6235..10607, 4373 B, sha256 `5a360321d182971d6114bd257c91c44085f55dede025a5cd27b420d6299ab83b` |
| §4 round-1 low findings (68–76) | bytes 10610..14128, 3519 B, sha256 `68f0d823c2f125cc08abbc1dda935f8ac26e8d1d76b9fb8156e301a81f219aa3` |
| §5 carried opens + boundaries (78–86) | bytes 14131..16228, 2098 B, sha256 `0d1bce1eb3ee233f5b2c1dc0839177677be164c36e421b4757327af682644bc6` |
| §6 reviewer re-execution disclosure (88–92) | bytes 16231..17234, 1004 B, sha256 `09b67b485ad005878e6c19d4e902cab5d8ce2265320d11aaddfd9dfe326bc26d` |
| §7 scope + GUARD-MERGE (94–103) | bytes 17237..18541, 1305 B, sha256 `2da4241bc0574c8b13d9ce54ef4ede6338b5a719dfb48c58fabc9b48049c7cf4` |
| GUARD-MERGE coordination line 103 | bytes 18315..18541, 227 B, sha256 `d0f653fb0d1893d8e8d55f0ec42a3b980606e5f6191cca124723c3b4f3df4870` |
| findings round-2 (105–109) | bytes 18544..19074, 531 B, sha256 `08a0193d144dd7da21902ed6a649fe688295f87bd324cd976ea4ade290e9b711` |
| unverified list (111–118) | bytes 19077..20454, 1378 B, sha256 `2a40751eafa4fb2124d27dff2368177888026dc8bc61c527fe8a009fcc652bd6` |
| REM-79 self-check (120–123) | bytes 20457..21150, 694 B, sha256 `819647d07e14a71ee7121650f852de5a99e4c46b1f118b957858070eeeb92fc1` |
| closing signature (125–127) | bytes 21153..21627, 475 B, sha256 `a28f8d0e048318779df2812a9e9edac3d439883b8ee0ba31c3a1120f16d8dd36` |
| round-1 reference / reviewer role (3–6) | bytes 89..1014, 926 B, sha256 `fe59612718ac0c42b7700f2ca54ba78ce900e8fe51d55d1ea5342f35f1a7e6e7` |
| round-1 carrier (history, untouched) | `reviewer_report.md` — 30045 B, sha256 `4c3f3f3d43a63e413eb808e7bcc8512b12eb31a4e71f69ae3a8226e0a6b2e26b`, 175 lines, sidecar `reviewer_report.sha256` (85 B) content-matches; verdict `changes_required` at line 10; verdict section bytes 883..1535 (sha256 `55f79830a8d35a9b4b0ae22f3fbddd80c6b8f0e00a50354e2a4df0c258f28893`), findings 140–152, re-review path 169–171, signature 173–175 |
| byte-region definition | 0-based byte offsets against the file at the recorded sha256; multi-line regions include internal LFs and exclude the final LF |
| producer | independent reviewer (独立复核), round 2 — not the implementer |

Verification at landing (read-only): r2 length **21629 B** ✓, re-hash **`2f685f0f…10e3f`** ✓ equals
both the dispatch pin and the sidecar content; **127 lines** ✓; line 10 reads `accepted_scoped` ✓.
r1 re-hash **`4c3f3f3d…e26b` / 30045 B** == its sidecar ✓ **untouched**. 0 bytes written to either
report or either sidecar by this pass.

## (a) F1 (the round-1 blocker) — FIXED, transcribed from carrier §2 (lines 23–39)

- **Code face**: iso `prompt_injection_guard.py` live SHA-256
  **`c2af11b316c923623be9449c94f0cce9be4960bf7a463fccba61d57f5e9bd20c`** (14064 B); round-1's
  `cf9174b5…` is superseded (recorded in the handoff change ledger).
- **`math.isfinite` gates**: `effective_receipt_ttl` raises
  `PromptInjectionGuardError("ttl_seconds must be a finite number")` at **guard:92–93** for
  NaN/±inf; `effective_review_instant` raises `"now must be a finite instant"` at
  **guard:108–109** for non-finite numeric `now`; negative finite ttl still raises
  `"ttl_seconds must be >= 0"` (guard:94–95).
- **CLIP finite mechanism unchanged — no REJECT-for-finite smuggled**: guard:96 is still
  `min(float(ttl_seconds), RECEIPT_TTL_POLICY_CAP_SECONDS)` after the gate — a finite ttl above
  the cap takes the clip path (no raise exists anywhere on the finite over-cap path);
  guard:110–116 keeps the past-`now` clip-forward to the policy clock; unparseable `now` still
  passes through so `_freshness` fails closed as `tampered`. The only `raise`s in the TTL path sit
  on 3 lines (type, negative, non-finite). The parent's CLIP-vs-REJECT question is untouched.
- **Reviewer's own `%TEMP%` probes** (attempt tree not touched): full independent suite
  **17/17 PASS, exit 0**, including **N8b** (NaN ttl on an expired receipt ⇒ coded raise carrying
  `"finite"`; the pre-fix revival is recorded verbatim in `evidence/red_prefix_iso.json`
  `cache_state='hit' … 'receipt fresh and bound'`, so raise-vs-revive is proven in all three
  states: red-prefix / green / mutant), **(ii) ttl=1e30 ⇒ 2592000 (CLIP, no exception)**,
  **(iii) ttl=365d ⇒ 2592000 (clip)**, gate side-checks (`nan/inf` ⇒ finite error, `now=nan` ⇒
  finite-instant error, `-1` ⇒ `>= 0`, cap = 2592000; `PROBE_ASSERTIONS=ALL_OK`), and **N11** (6
  partial identities — three 2-of-3 variants, one 1-of-3, empty string, None — each raise
  `DemandRegistrationError` with needle `"cover"`, zero rows, full three-field positive control
  accepted; gate live at `processing_demand.py:390-400`).
- **Honest first-run disclosure (carrier §6)**: the reviewer's first probe copy scored **13/17** —
  both causes were the probe environment (`PYTHONIOENCODING=utf-8` vs the harness's locale decode
  in `subprocess.run`, killing P1/P2/N1; a missing `before/` copy killing P3), not the artifacts;
  a clean second copy (`scripts/`+`iso/`+`before/`, no encoding override) scored **17/17**. The
  self-correction is disclosed, not hidden.

## (b) Round-2 discipline — transcribed from carrier §3 (lines 41–66)

- **Oracle `§2-再补` dated APPEND** (frozen before any round-2 run): section =
  **2469 bytes, SHA-256 `ff2a67f93619896158bd1927638b785e5ac3abb0a62bbd1448c50d39f9c76639`** —
  re-computed independently by the reviewer (byte-offset-correct slicing) and equal to the handoff
  pin; full `oracle.md` = 14383 B / `2aa2f9bc…644d`. The append keeps round-1's 15 case
  expectations unchanged and adds exactly N8b + N11 + the three mutation arms.
- **mtime chain verified**: oracle 23:51:05 < harness 23:52:07 < first round-2 run
  `red_before.json` 23:53:03 < `red_prefix_iso.json` 23:53:22 < F1 fix (guard 23:53:42) < F6 fix
  (`processing_demand.py` 23:53:52) < `green_iso.json` 23:54:43 < mutants/mutation runs
  23:54:44–23:55:20 < collector 23:55:52 < `decision.md` 23:58:15 < `commands.json` 23:58:57 <
  `handoff.json` 00:02:00 — the append predates every round-2 run and the RED-prefix run predates
  the fix it diagnoses.
- **Counts re-read from raw JSON (6 runs)**: RED `red_before.json` **0/17**; iso-increment
  `red_prefix_iso.json` **15/17** (only N8b + N11 red, both pre-fix behaviors verbatim);
  GREEN `green_iso.json` **17/17**; mutation arms **key 14/17** (N1 + P4/N5 same-guard
  collateral), **nan 16/17** (N8b alone, F1 revival text), **identity 16/17** (N11 alone) — each
  arm reds exactly its target family.
- **Mutants byte-exact (round-1 F7 closed)**: `w06a2_make_mutant.py` uses
  `read_bytes`/`write_bytes` with a single-occurrence anchor check; the reviewer's in-memory
  transform reproduced each live mutant byte-for-byte (`anchor_count=1`, `rebuilt_len == mut_len`,
  byte-equal): key = `processing_demand.py` 39486→39448, nan = guard 14064→13993, identity =
  `processing_demand.py` 39486→39308; each tree differs from iso in exactly one source file.
  **Zero CR** in the mutated files (round-1's CRLF artifact gone; `store.py` CRLF 1616 is
  pre-existing production bytes). `MUTATION.json` re-hashes: `a191bf2e…` / `63681132…` /
  `fadd5d38…` all equal their handoff pins. `changes.diff` regenerated: `6a5fa817…`, 1088 lines,
  header scope exactly the 3 declared source files; before-vs-iso file set 35 vs 35 (0 added,
  0 removed).

## (c) Round-1 low findings — F3–F10 closures (carrier §4, lines 68–76)

- **F3 (pid/argv) — CLOSED**: `evidence/demand.cross-process.json` (`b0dc1731…`, handoff-pinned)
  records per-step pid + literal argv in each of the 7 envelopes and again in `children[]`; the
  reviewer re-checked the **7 pids by hand — 28488 / 35072 / 44068 / 38712 / 46832 / 16860 /
  41816 are 7 distinct values**, argvs literal (`--target <attempt>\iso --child … --db
  %TEMP%\w06a2-evid-*\catalog.sqlite3`), `seven_distinct_child_pids: true`.
- **F4 (full hash ledger) — CLOSED**: `handoff.output_hashes` grew to the full ledger; the
  reviewer re-hashed **every** row live (the 6 dispatched spot values plus all others incl. the
  6 round-2 and 7 round-1 evidence JSONs, all 3 `MUTATION.json`, oracle + append section,
  `changes.diff`) — **zero mismatch** against its pins.
- **F5 (N8 RED wording) — CLOSED**: `decision.md` §2 N8 RED cell now carries round-1's honest
  wording — behavioral revival = code-true + sibling-card proven, **本卡 RED 未执行该复活行为**.
- **F6 (any-of vs covers-three) — fixed beyond the round-1 ask**: gate at
  `processing_demand.py:390-400` (`covered = (as_of_date, target, payload_digest)`, missing/None/
  empty ⇒ coded refusal); proof triple = **N11 red-prefix / green / mutant** (15/17, 17/17,
  16/17 — the target alone red).
- **F7 — CLOSED** (§3 above: byte-exact mutants, zero CR).
- **F8 — recorded** in `decision.md` §7 + `handoff.input_hashes` (brief prefix slip `7b26…` vs
  live `7b22f239…`; UNCHANGED claim re-hashed equal across real/before/iso).
- **F9 / F10 — dissolved as parent-attributed**: `decision.md` §7 and
  `handoff.status_note`/`review_round_2.fixes.F9/F10` record the historical-attempt transcription
  file and the in-window repo activity as the parent's transcription/batch commits, NOT this
  card's — as round-1 required. The 18-entry command ledger (9 round-1 + 9 round-2) contains **no
  git verb** and targets only the attempt dir + `%TEMP%`.

## (d) Carried opens parity + boundaries — PRESENT / HELD (carrier §5, lines 78–86)

- **Carried-open parity holds — all 9 opens intact** in `handoff.open_items` and mirrored in
  `decision.md` §6: (1) I-06-B consumption/CLI fail-able face; (2) **no CLI adapter file** — no
  ruling froze a file name (「未冻结具体文件禁止猜建」); (3) **RF `source_preparation.py` caller
  wiring + CLI-level c8/c9/c10 re-probes**; (4) **P4-SCOPE** cross-repo verbatim pinning of the RF
  blocked-message sentence; (5) **OPEN-4/6 留置①** full-bytes runtime probe; (6) **P5-b** reviewer
  identity chain = **BLOCKED-on-external** (函 B trust root); (7) **cross-PROCESS concurrent
  claim** (same-process covered by N5); (8) **CLIP-vs-REJECT standardization = parent's**; (9)
  **production promotion solely after independent review + owner commit**. Round-2 added no new
  open that displaces a carried one.
- **Zero product writes (re-hashed live this round)**: CW live `prompt_injection_guard.py` =
  `f900a13d7c22fe3bd742485c6b603de11b92a56d2414a2a046216ccd3b0b9c08` == `before/` — production
  carries **NEITHER implementation** (not round-1 `cf9174b5…`, not round-2 `c2af11b3…`); CW
  `store.py` `1a783240…`, `processing_demand.py` `90f232ed…`, `prompt_injection.py` `7b22f239…`
  each equal their `before/` pins (`evidence/prod-unchanged.json` agrees).
- **No CLI file**: before-vs-iso file-set compare 35 vs 35, zero added/removed; the pre-existing
  `source_contract/cli.py`/`announcement_cli.py` copies are byte-identical.
- **Handoff face at review time** (pre-bookkeeping): `status=review_pending`,
  `implementer_signed=false`, `disclosure_adaptation=unmapped`, `accuracy=unproven`,
  `reviewer_status="PENDING independent review round 2 — implementer 未自签"` — this pass
  supersedes only the stale status prose (retained byte-exact under `*_historical_pre_verdict`);
  `implementer_signed`, `disclosure_adaptation` and `accuracy` are untouched.

## (e) Scope of acceptance + GUARD-MERGE coordination (carrier §7, lines 94–103)

1. **Production promotion = parent commit under the established owner pattern** — zero product
   writes remain until the owner commits (CW live bytes still `f900a13d…`, verified this round).
2. **Consumption face** = resume/complete CLI fail-able test face stays with **I-06-B**, in
   flight; this card promotes the store-side lifecycle face alone.
3. **Carried opens unchanged** — the five re-review-path items re-confirmed in §(d) above.
4. **CLIP-vs-REJECT divergence + the F1 mechanism choice stay recorded for the parent's
   standardization** — not adjudicated here (finite over-cap CLIP verified unchanged;
   non-finite = coded rejection, shaped to match the sibling card).

**GUARD-MERGE coordination (carrier line 103)**: this card's **guard face is superseded by the
merge card**; this card's **`store.py`/`processing_demand.py` face promotes WITH this card**; the
**unification itself stays parent/GUARD-MERGE's** (not this iso's guard alone).

## (f) Round-2 findings, unverified list, REM-79 (carrier lines 105–123)

- **Findings: no new blocking finding** — every round-1 finding closed (F1/F3/F4/F5/F6/F7) or
  properly recorded/dissolved (F2/F8/F9/F10). Two notes: round-1 brief byte recollection
  ("22499-ish" vs live 30045, hash-authoritative) and the disclosed probe-environment self-run.
- **Unverified list carried in full** (lines 111–118): evidence-window single-run honesty rests on
  mtimes + the `commands.json` ledger; RF in-window mtimes / F9-F10 actor attribution recorded as
  parent-confirmed (re-verified as RECORDING only); no `git status --porcelain` by this review
  (no-git boundary); mutation arms not re-executed by the reviewer (raw JSONs re-read, pins
  re-hashed, mutants re-derived — sufficient for non-hollowness); cross-PROCESS concurrency still
  carried by design; P5-b / 留置① / RF CLI wiring outside this card.
- **REM-79 self-check**: checker `check_domain_assertions.py` v `1.2.0-correction2` — **first pass
  13 violations → tightened wording → 0 violations across 1 file, exit 0** on the final hashed
  bytes (`first13→final0`).

## Not granted

`disclosure_adaptation` stays **unmapped**; `accuracy` stays **unproven**; no production write
authority (0 product bytes here and 0 by this pass); no CLIP-vs-REJECT adjudication (parent/
GUARD-MERGE); no promotion of this iso's guard face alone (GUARD-MERGE composition); no
consumption/CLI face (I-06-B); and **this file grants nothing** — it is bookkeeping transcription
only.

## Bookkeeping

- Landed by: carrier-landing bookkeeping executor (delegated subagent), 2026-09-22.
- Status transition: `review_pending` → `accepted_scoped`, performed in `handoff.json` by this
  pass on the parent's dispatch; the verdict itself is the reviewer's (line 10 / §7 / signature
  lines 125–127). `status_before_bookkeeping_fix: review_pending` recorded; `status_history`
  records round-1 `changes_required` (30045 B / `4c3f3f3d…e26b`, untouched) and round-2
  `accepted_scoped` (21629 B / `2f685f0f…10e3f`); `status_authority` carries the carriers +
  line ranges + sha256 + byte proofs + `verdict_is_transcribed_not_authored: true`.
- `implementer_signed: false`; authority: acceptance was written by 独立复核 in
  `reviewer_report_r2.md` (21629 B / `2f685f0f…10e3f`, pinned by the pre-existing
  `reviewer_report_r2.sha256`), never by the implementer and never by this file's author;
  round-1 `changes_required` is preserved as history (r1 report untouched).
- This pass wrote exactly three files: `review.md` (created, this file), `handoff.json` (status +
  `status_before_bookkeeping_fix` + `status_history` + `status_authority` + `bookkeeping` +
  `carried_findings` (F1–F10 round-2 dispositions) + two stale pre-verdict prose fields superseded
  byte-exact under `*_historical_pre_verdict`; pre-existing content otherwise untouched — all 9
  `open_items` kept), and `evidence/I-06-A/qualification.json` (created). Zero bytes to either
  reviewer report or sidecar, zero product bytes, zero git state. **No self-signing anywhere.**
