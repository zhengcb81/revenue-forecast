# reviewer_report_r2.md — I-06-A / a20260922-02 (independent signing review, ROUND 2)

- Reviewer role: independent re-review of the implementer's round-2 remediation against round-1 `reviewer_report.md` (verdict `changes_required`, 1 blocking F1). This report is the round-2 review signature; `handoff.json` stays untouched — the implementer never self-signed, and this review does not sign for them.
- Date: 2026-09-22 (round-2 evidence window 23:51–00:02 CST).
- Tools used: `read`, `grep`, `pwsh` (re-hash / mtime / byte-compare / in-memory transform checks), plus `python` executed ONLY inside `%TEMP%` copies (one independent full-suite run of 17 cases + one helper-level probe script).
- Writes performed by this review: exactly the 2 deliverables of this review — `reviewer_report_r2.md` + `reviewer_report_r2.sha256`. Both product repos, the historical attempt, round-1's report+sidecar, and the rest of this attempt tree were treated read-only. No `git` command of any kind was run by this review.

---

## Verdict: **accepted_scoped** (round 2)

Round-1's single blocking item (finding 1, NaN ttl widening bypass) is FIXED and independently re-executed by this review; the round-1 low findings F3/F4/F5/F7 are closed with the claimed artifacts re-hashed live; F6 (tightening) is fixed with red/green/mutation proof; F8 is recorded; F9/F10 are dissolved as parent-attributed, and `decision.md` §7 + `handoff.json` both record them that way. Carried-open parity (round-1 re-review-path item iii) holds: each open carried by round-1 is still present in `handoff.open_items` and mirrored in `decision.md` §6.

Acceptance is scoped exactly per round-1's "Re-review path" (its four points i–iv), plus the dispatch's GUARD-MERGE coordination note — spelled out in §7 below. CLIP-vs-REJECT remains NOT adjudicated here (round-1 finding 2; parent's standardization).

---

## 1. Round-1 carrier integrity — UNTOUCHED

- `reviewer_report.md` live re-hash = `4c3f3f3d43a63e413eb808e7bcc8512b12eb31a4e71f69ae3a8226e0a6b2e26b`, byte length 30045, mtime 2026-09-22 23:37:40 — equals its own `reviewer_report.sha256` sidecar (`4c3f3f3d…`, written 23:37:41). Matches the dispatch's `4c3f3f3d…` prefix exactly. (The dispatch's "22499-ish" byte estimate is off; the hash is authoritative and matches, so no finding.)
- Round-1 raw evidence is preserved under `evidence/round1/` (7 files, mtimes 22:56–23:00, all predating the round-1 report) and round-2 `handoff.output_hashes` now pins each of those round-1 bytes (spot values re-hashed in §4/F4). No prior verdict was overwritten: round-2 wrote a NEW report file, as required.

## 2. F1 (the round-1 blocker) — FIXED, mechanism check + my own probes

**Code face (live bytes).**

- `iso/…/prompt_injection_guard.py` live SHA-256 = `c2af11b316c923623be9449c94f0cce9be4960bf7a463fccba61d57f5e9bd20c` (14064 B) = implementer's claim `c2af11b3…`; round-1's `cf9174b5…` is superseded (recorded in the handoff change ledger).
- `math.isfinite` gate present: `effective_receipt_ttl` raises `PromptInjectionGuardError("ttl_seconds must be a finite number")` at guard:92-93 for NaN/±inf; `effective_review_instant` raises `PromptInjectionGuardError("now must be a finite instant")` at guard:108-109 for non-finite numeric `now`; negative finite ttl still raises `"ttl_seconds must be >= 0"` (guard:94-95).
- **CLIP finite-super-cap mechanism unchanged and NOT prejudged**: guard:96 is still `return min(float(ttl_seconds), RECEIPT_TTL_POLICY_CAP_SECONDS)` after the isfinite gate — a finite ttl above the cap takes the clip path (no raise exists anywhere on the finite over-cap path); guard:110-116 keeps the past-`now` clip-forward to the policy clock, and unparseable `now` still passes through untouched so `_freshness` fails closed as `tampered`. Grep confirms no REJECT-for-finite was smuggled in: the only `raise`s in the TTL path sit on 3 lines (type, negative, non-finite). The parent's CLIP-vs-REJECT unification question is untouched by this fix.

**My own probes (executed by this review in `%TEMP%`, attempt tree not touched).**

1. *(i) ttl=NaN on an EXPIRED receipt ⇒ must RAISE*: I copied `scripts/`+`iso/`+`before/` to `%TEMP%\i06a2-r2probe-906a899b` and ran the round-2 harness argv shape (`python …\w06a2_cases.py --target <temp>\iso --out <temp>\independent_green.json`). `W06A2-N8b` = PASS in my run (case at harness:773-831 records a receipt aged `cap+120`s, evaluates with `ttl_seconds=float("nan")`, and asserts a coded `PromptInjectionGuardError` carrying `"finite"` — a silent `hit` fails the case). The pre-fix revival itself is recorded verbatim in `evidence/red_prefix_iso.json` (`cache_state='hit'`, `reason='receipt fresh and bound'`) and reappears in the nan-arm mutant red — so raise-vs-revive is proven in all three states (red prefix / green / mutant).
2. *(ii) ttl=1e30 finite ⇒ clip to 2592000, not raise*: my helper probe — `effective_receipt_ttl(1e30) = 2592000` (CLIP, no exception). N8b check (3) (harness:822) pins the same.
3. *(iii) ttl=365d finite ⇒ clip*: my helper probe — `effective_receipt_ttl(365*86400) = 2592000`, not raise. (The frozen N8b case covers 1e30; 365d was my extra probe; both hit the same `min(...)` line.)
4. Gate side-checks from the same probe: `effective_receipt_ttl(nan/inf)` ⇒ `"ttl_seconds must be a finite number"`; `effective_review_instant(nan)` ⇒ `"now must be a finite instant"`; `effective_receipt_ttl(-1)` ⇒ `">= 0"`; cap constant = 2592000. `PROBE_ASSERTIONS=ALL_OK`, probe exit 0.
5. *N11 (two-of-three identity ⇒ `DemandRegistrationError` with "cover")*: `W06A2-N11` PASS in my run — 6 partial identities (three 2-of-3 variants, one 1-of-3, empty-string, None) each raise `DemandRegistrationError` with needle `"cover"` (harness:846-859), zero rows produced, full three-field positive control accepted. Gate code live at `processing_demand.py:390-400` (`covered = ("as_of_date","target","payload_digest")`, missing/None/empty ⇒ coded refusal).

Full independent suite result: **17 passed / 0 failed**, exit 0. (First attempt at my probe run scored 13/17 — see §6 for the honest disclosure; both causes were my probe environment, not the artifacts.)

## 3. Round-2 discipline — VERIFIED (frozen-first, counts, mutants)

**Oracle frozen-before-runs, pinned section.**

- Full `oracle.md` live SHA-256 = `2aa2f9bc6fa7bf5e237bc0d2b232caa81d437c020e08b5ed784128a93638644d` (14383 B), final write 23:51:05.
- The `§2-再补` dated-APPEND section (bytes from `## 2-再补` heading up to — not including — `## 3.`) = **2469 bytes, SHA-256 `ff2a67f93619896158bd1927638b785e5ac3abb0a62bbd1448c50d39f9c76639`** — re-computed independently (byte-offset-correct slicing) and equal to the handoff pin. The section text states it freezes before any round-2 run, sources only the ratified contract + round-1 verdict, keeps round-1's 15 case expectations unchanged, and adds exactly two gate cases (N8b, N11) + the three mutation arms.
- mtime ordering: oracle 23:51:05 < harness final write `scripts/w06a2_cases.py` 23:52:07 < first round-2 run `evidence/red_before.json` 23:53:03 < `red_prefix_iso.json` 23:53:22 < F1 fix (guard 23:53:42) < F6 fix (`processing_demand.py` 23:53:52) < `green_iso.json` 23:54:43 < mutants/mutation runs 23:54:44–23:55:20 < collector 23:55:52 < `commands.json` 23:58:57 < `decision.md` 23:58:15 < `handoff.json` 00:02:00. The append predates every round-2 run, and the RED-prefix run predates the fix it diagnoses.

**Scoreboard — counts re-read from raw JSON (6 runs; pass/fail format as in round-1):**

| Run | Claimed | Re-read live | Failing cases re-verified |
|---|---|---|---|
| RED `red_before.json` | 0/17 | `passed:0, failed:17` ✓ | N8b/N11 present, both `AttributeError: … no attribute 'CatalogDemandStore'` (API-absent class, same as the other 15) |
| RED-prefix `red_prefix_iso.json` (incremental behavioral) | 15/17 (N8b+N11 red) | `passed:15, failed:2` ✓ | N8b red = revival text verbatim `cache_state='hit' … 'receipt fresh and bound'`; N11 red = 2-field identity ACCEPTED as a `ProcessingDemandRecord` — both pre-fix behaviors recorded in `red_prefix` as claimed |
| GREEN `green_iso.json` | 17/17 | `passed:17, failed:0` ✓ | N8b measurement `{"nonfinite":"coded refusal","finite_over_cap":"clipped"}`; N11 `{"partials_refused":6,"rows":1}` |
| MUTATION key arm | 14/17 (N1+P4+N5) | `passed:14, failed:3` ✓ | FAILs = W06A2-P4, N1, N5 — each `DemandIdempotencyViolation` at the second identity-divergent `register` (same-guard collateral, tracebacks re-read) |
| MUTATION nan arm | 16/17 (N8b red alone) | `passed:16, failed:1` ✓ | FAIL = W06A2-N8b alone, red text = F1 revival verbatim |
| MUTATION identity arm | 16/17 (N11 red alone) | `passed:16, failed:1` ✓ | FAIL = W06A2-N11 alone |

**Mutants byte-exact (round-1 F7 closed) + MUTATION.json re-hash.**

- `scripts/w06a2_make_mutant.py` uses `read_bytes`/`write_bytes` (lines 88/93) with a single-occurrence anchor check (`count(old) != 1` ⇒ abort), and each `MUTATION.json` carries `write_mode: "byte-exact (read_bytes/write_bytes; no newline translation)"` plus declared `before`/`after`.
- My in-memory transform check: applying each declared `before→new` replacement to the live iso bytes reproduces the live mutant bytes EXACTLY (`anchor_count=1`, `rebuilt_len == mut_len`, byte-equal) for all three arms: key = `processing_demand.py` 39486→39448, nan = guard 14064→13993, identity = `processing_demand.py` 39486→39308. Each tree differs from iso in exactly one source file (the declared one); the other two of the three core files are byte-identical to iso.
- Zero CR: mutated `processing_demand.py`/`prompt_injection_guard.py` have CR=0 in iso and in each mutant tree (3 trees; round-1's CRLF artifact is gone). Note (benign): `store.py` is CRLF (1616 CR) in iso AND each mutant tree — pre-existing production bytes, untouched by each arm.
- The three `MUTATION.json` re-hash: `iso-mutant/MUTATION.json` = `a191bf2e14b8b8f457c4e28d2b28692c19da7a25005881b81efec17a7ffa45ff` ✓, `iso-mutant-nan/…` = `6368113297d5dedc37c8ffa93011ef32e4bd7fc45a012599fe19f1f2d40be0bd` ✓, `iso-mutant-identity/…` = `fadd5d38f23b31e8c9f92a4ff87cdd9c2bfa4e92fff2a598aa93fa778e861dea` ✓ — equal to the handoff pins.
- `changes.diff` regenerated: SHA-256 `6a5fa817…`, 1088 lines, header scope = exactly `processing_demand.py` + `prompt_injection_guard.py` + `store.py` (difflib unified, `w06a2_make_diff.py` runs no git); before-vs-iso file-set compare = 35 vs 35 files, zero added, zero removed.

## 4. Round-1 low findings — status against live bytes

- **F3 (pid/argv) — CLOSED.** `evidence/demand.cross-process.json` (`b0dc1731311f092dafe718fe840d29a70c33a0fc9b3837a5743ecee07a52c95d`, handoff-pinned) now records per-step `pid` + literal `argv` in each of the 7 scenario envelopes and again in `children[]`; assertions include `seven_distinct_child_pids: true` and `children_self_report_argv: true`. I re-checked the 7 recorded pids by hand — 28488 / 35072 / 44068 / 38712 / 46832 / 16860 / 41816 are 7 distinct values, and each argv is the literal `[w06a2_cases.py, --target, <attempt>\iso, --child, …, --db, %TEMP%\w06a2-evid-*\catalog.sqlite3, …]` with scenario-specific child verbs (`register`×4 / `query`×3) matching the scenario list.
- **F4 (full hash ledger) — CLOSED.** `handoff.output_hashes` grew from 9 pins to the full ledger (3 iso files, 4 scripts, oracle + its append section, changes.diff, commands/decision/recovery/binding, all 6 round-2 evidence JSONs, all 7 round-1 evidence JSONs, 3× MUTATION.json). Spot re-hash of the 6 dispatched entries vs round-1 §1.1 recompute values: `recovery/README.md` = `7284f498…` ✓, `scripts/w06a2_make_diff.py` = `2cb334fb…` ✓, `iso store.py` = `b8e00362…` ✓, `iso prompt_injection.py` = `7b22f239…` ✓, `evidence/round1/red_before.json` = `2d493176a11db34ec5a9ca9416a14ddb3a6297e1e7873ad0303c6a2f3c437ff0` ✓, `iso-mutant/MUTATION.json` = `a191bf2e…` ✓. Beyond the dispatched six I re-hashed every other ledger row live (cases `1945b91d`, evidence-script `7a471acc`, make_mutant `ffdcc7c7`, commands `8640ae93`, decision `b453427c`, binding `53776519`, iso pd `ca195655`, oracle `2aa2f9bc`, append section `ff2a67f9`, changes.diff `6a5fa817`, all 6 round-2 evidence JSONs, all 7 round-1 evidence JSONs, nan/identity MUTATION.json) — every value equals its pin; no mismatch found.
- **F5 (N8 RED cell wording) — CLOSED.** `decision.md` §2 N8 RED cell now reads 「如实归位（复审 F5）…代码真（before guard 无双钳制）+ 兄弟卡 TTL-30D-POLICY 的 RED 实测证；**本卡 RED 未执行该复活行为**（N8 在首个 AttributeError 处即中止）」 — exactly round-1's honest wording (behavioral revival = code-true + sibling-proven, not executed in this RED).
- **F6 (any-of vs covers-three) — fixed beyond the round-1 ask** (round-1 listed it as a low finding with a tighten-or-document choice): gate at `processing_demand.py:390-400`, proof triple = N11 red-prefix/green/mutant (verified in §2/§3).
- **F7 — CLOSED** (§3, byte-exact mutants, zero CR).
- **F8 — recorded** in `decision.md` §7 + `handoff.input_hashes` (brief prefix slip `7b26…` vs live `7b22f239…`; UNCHANGED claim holds across real/before/iso — I re-hashed each of the 3 copies equal).
- **F9 / F10 — parent-attributed, not card-written.** `decision.md` §7: F9 = 「已消解（父 agent 确认）… 该文件 = 父转录批（owner 终确后的授权记账）…非本卡所写」; F10 = 「已消解（父 agent 确认）= 父批次提交 + FIX 测试写，均在本卡冻结面之外」. `handoff.status_note`/`review_round_2.fixes.F9/F10` mirror it ("dissolved by PARENT confirmation… parent transcription batch / parent batch commits"). Both the transcription file and the in-window repo activity are recorded as the parent's, NOT this card's — as the round-1 findings required. The 18-entry command ledger (9 round-1 + 9 round-2) contains no git verb and targets only the attempt dir + `%TEMP%`.

## 5. Carried opens parity + boundaries — PRESENT / HELD

**Carried-open parity (round-1 re-review-path item iii):** `handoff.open_items` still carries each open handed over by round-1 — RF `source_preparation.py` caller wiring + CLI-level c8/c9/c10 re-probes (item 3, mirrored `decision.md` §6.1); P4-SCOPE cross-repo verbatim pinning of the RF blocked-message sentence (item 4, mirrored §6.4); OPEN-4/OPEN-6 留置① full-bytes runtime probe (item 5, mirrored §6.7); P5-b reviewer identity chain = BLOCKED-on-external (item 6, mirrored §6.6); cross-PROCESS concurrent claim case (item 7, mirrored §6.5/§6.9); CLIP-vs-REJECT standardization = parent's (item 8, mirrored decision 10 + §7 F2); I-06-B consumption face (item 1, mirrored §6.2); CLI adapter file not frozen (item 2, mirrored §6.3); production promotion solely after independent review + owner commit (item 9). Nothing was dropped between round-1 and round-2; round-2 added no new open that displaces a carried one.

**Handoff face:** `status=review_pending`, `implementer_signed=false`, `disclosure_adaptation=unmapped`, `accuracy=unproven`, `reviewer_status="PENDING independent review round 2 — implementer 未自签"` — unchanged posture; the implementer did not self-sign.

**Zero product writes (re-hashed live this round):** CW live `prompt_injection_guard.py` = `f900a13d7c22fe3bd742485c6b603de11b92a56d2414a2a046216ccd3b0b9c08` == `before/` copy — production carries NEITHER implementation (not round-1 `cf9174b5…`, not round-2 `c2af11b3…`). CW live `store.py` `1a783240…`, `processing_demand.py` `90f232ed…`, `prompt_injection.py` `7b22f239…` each equal their `before/` pins. `evidence/prod-unchanged.json` + `before`-vs-live equality confirm the same.

**No CLI file:** before-vs-iso file-set compare = 35 files each, zero added, zero removed (the only diffs are the 3 declared source files); the pre-existing `source_contract/cli.py`/`announcement_cli.py` copies are byte-identical. `handoff.scope_boundary` and `decision.md` §0/决策 2 keep the "未冻结具体文件禁止猜建" rationale.

## 6. My re-execution and its one artifact (honest disclosure)

- Probe copy A (`%TEMP%\i06a2-r2probe-cfdc78bc`): I set `PYTHONIOENCODING=utf-8` for the whole run and omitted `before/`. Result 13/17 — P1/P2/N1 died in `subprocess` reader threads (`UnicodeDecodeError: 'gbk' codec` — my env var made children emit UTF-8 while the harness decodes with the locale in `subprocess.run(..., text=True)`, harness:184-192) and P3 died with `ModuleNotFoundError` because `case_p3` loads `ATTEMPT/"before"` (harness:273) which my copy lacked. Both causes are in MY probe setup; neither touches the artifacts.
- Probe copy B (`%TEMP%\i06a2-r2probe-906a899b`): exact layout (`scripts/`+`iso/`+`before/`), no encoding override — **17/17 PASS, exit 0**, including N8b and N11. Helper-level clip/gate probe: all assertions OK (§2).
- Nothing outside `%TEMP%` and my two report files was written by this review; the attempt tree's own `__pycache__` mtimes were not advanced by these runs (copies were made first).

## 7. Scope of this acceptance + coordination

Following round-1's "Re-review path" (four points), acceptance scopes as **accepted_scoped** for this attempt's frozen face:

1. **Production promotion = parent commit under the established owner pattern** — zero product writes remain until the owner commits (CW live bytes still `f900a13d…`, verified this round).
2. **Consumption face = resume/complete CLI fail-able test face stays with I-06-B**, in flight; this card promotes the store-side lifecycle face alone.
3. **Carried opens unchanged** (round-1 item iii list, each re-confirmed present in §5): RF caller wiring + CLI-level c8/c9/c10 re-probes; P4-SCOPE RF blocked-sentence pinning; OPEN-4/6 留置① full-bytes probe; P5-b identity chain (blocked external); cross-process concurrent-claim case.
4. **CLIP-vs-REJECT divergence + the F1 mechanism choice stay recorded for the parent's standardization** — this review does not adjudicate the global choice (finite over-cap CLIP verified unchanged; non-finite = coded rejection, shaped to match the sibling card).

**GUARD-MERGE coordination (per dispatch):** this card's guard face is superseded by the merge card; this card's `store.py`/`processing_demand.py` face promotes with this card; the unification itself stays parent/GUARD-MERGE's.

## Findings (round 2)

- **No new blocking finding.** Each round-1 finding is closed (F1/F3/F4/F5/F6/F7) or properly recorded/dissolved (F2/F8/F9/F10) with live-byte or raw-JSON verification as shown above.
- **NOTE (round-1 brief transcription):** the dispatch recalled round-1's report size as "22499-ish"; live size is 30045 bytes with matching hash — brief-side recollection only, no integrity impact.
- **NOTE (probe environment):** my first independent run needed a clean-env second run (§6); disclosed rather than hidden.

## Unverified / limitations of this review

- Evidence-window honesty of "single run per round-2 step": mtimes establish oracle-freeze-first and fix-after-RED-prefix ordering, but overwritten earlier runs cannot be excluded by mtimes alone; `commands.json` documents each iteration historically (round-1 iterations were logged), so the ledger is accepted as the record.
- RF repo in-window mtimes and the actor-attribution behind F9/F10: dissolved by parent confirmation and recorded as such (round-1 §6/finding 9-10 did the mtime legwork); this review re-verified the RECORDING, not the parent's confirmation itself.
- `git status --porcelain` of both repos: not run by this review (no-git boundary); zero-product-writes rests on live re-hash of the frozen surface (= `before/` pins), matching round-1's method.
- Mutation-arm runs were not re-executed by me (writes outside `%TEMP%` copies would be needed against the real mutant trees); the raw mutation JSONs were re-read, pins re-hashed, and each mutant's bytes re-derived from the declared transform — sufficient for non-hollowness, with my independent 17/17 covering the un-mutated face.
- Cross-PROCESS concurrency (simultaneous claim from two processes): still a carried open by design (same-process concurrency covered by N5).
- P5-b identity chain, 留置① probe, RF CLI wiring: outside this card, carried (§5).

## REM-79 self-check record

- Checker: `execution_runs/REM79-MECHANIZATION/a20260922-01/tools/check_domain_assertions.py` (v `1.2.0-correction2`), run with `PYTHONIOENCODING=utf-8` against this file before the sidecar was written. Result recorded in `reviewer_report_r2.sha256`'s companion line and reproduced at the end of this section once run.
- Result: checker run on the final bytes of this file (the bytes hashed into `reviewer_report_r2.sha256`) printed `0 violation(s) across 1 file(s)`, exit 0 — v `1.2.0-correction2`, `PYTHONIOENCODING=utf-8`. First pass found 13 violations (bare universal markers without same-line domains); wording was tightened to carry domains before hashing.

## Signature

This `reviewer_report_r2.md` + its `reviewer_report_r2.sha256` pin are this review's sole outputs. Round-1's `reviewer_report.md` + `reviewer_report.sha256` remain byte-untouched (re-verified in §1). The implementer handoff remains unsigned by the implementer (`implementer_signed=false`, `review_pending`); with this report the attempt is review-signed as **accepted_scoped** under §7's scope — promotion to production still requires the owner-side commit.
