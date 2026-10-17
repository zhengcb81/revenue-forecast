# D-reviewer-3 — independent round-3 re-review (DU11-RF-CITATION-CLOSURE)

Reviewer: same independent agent as rounds 1–2 (not the author). Prior reports:
`receipts/D-reviewer-1.md` (FAIL: 1 blocking + 6 should-fix + 10 nits) and
`receipts/D-reviewer-2.md` (FAIL: 0 blocking + 1 new should-fix R2-1 + 2 doc nits).

## 1. Verdict

**PASS — 0 unresolved blocking, 0 unresolved should-fix.**

R2-1 is genuinely fixed, both round-2 doc nits are fixed, and no earlier fix regressed. Scope,
compatibility, RED, E2E/restore and every gate verify green independently below. The card may
be marked COMPLETE after the author writes `handoff.json` / the final pure-documentation handoff
commit, with the reviewed source SHAs below unchanged (the card allows that final documentation
commit by ROOT against the frozen source).

Reviewed HEAD: `f1f7d0683726098c9f5b5614ca26f4beb64898aa` on
`codex/du11-rf-citation-closure` (parent `1ae6c3b5`, base `568fb925`). Worktree clean
(`git status --porcelain` empty) before and after my runs; I wrote only this report.

## 2. Reviewed SHA-256 (recomputed; all nine match `receipts/B-final-tests.json`)

| # | path | SHA-256 |
|---|------|---------|
| 1 | `scripts/narrative_citation_context.py` | `3699df45774a9db0a1ad1b8440db00a3a09efa3f6db8d40bc7bad38120d018f5` (changed in round 3) |
| 2 | `scripts/source_narrative_context.py` | `ee271c3f5be61b2c7df845b60f7962422fd45808c0c38b727a700ecc93ede259` (unchanged since round 1) |
| 3 | `scripts/research/input_evidence.py` | `c0a321f9ca905023846dafa4fe7c35b74e7d3cedc5e77bbd6882168579f338ed` (unchanged since round 2) |
| 4 | `tests/test_du11_narrative_citation_wire.py` | `f63ccfa381dfeb80d13c837f05a897305ee0749923e69ca77dc11122dbfdc620` |
| 5 | `tests/test_du11_narrative_citation_context.py` | `bac9badb89d7852f5684981189bc0db1f41c4806597f1ce8a222b32f708013ed` (changed in round 3) |
| 6 | `tests/test_du11_narrative_citation_consumption.py` | `cbd44c769240e341cb309856dc4f481aa28947fd073ea05de349cc6a00cbb7f7` |
| 7 | `tests/test_du11_narrative_citation_projection.py` | `55c071be5f6023faf6d369707267241ee88434b28635b3e97f25afe412607756` |
| 8 | `tests/test_du11_narrative_citation_e2e.py` | `cac76fe54690e34a7dfa49de2ac1bd493fbbd50030a3a952e80c4adc1361f24d` |
| 9 | `tests/fixtures/du11_narrative_citation/synthetic_reading2.json` | `368c9776402bb39497db1b95863c528ba0190b043f19905f62039f40de95c7de` (unchanged since round 2) |

## 3. Scope / process

- `git diff --name-only 568fb925..HEAD` is exactly the card whitelist: 3 scripts (1 new adapter,
  2 modified consumers), 5 new `test_du11_narrative_citation_*.py`, 1 new fixture, the card PWF
  dir. `git diff --name-status 568fb925..HEAD -- tests/` is all `A` (no existing test modified);
  `scripts/company_wiki_narrative_contracts.py` is untouched; no forecast/formula, CWP/FF/ET,
  `assurance/`, `.codegraph` or install/release path is touched.
- `git diff 1ae6c3b5..HEAD` (round 3) is only `scripts/narrative_citation_context.py` (one
  condition), `tests/test_du11_narrative_citation_context.py` (8-case regression), and PWF
  docs/receipts. My round-2 report `receipts/D-reviewer-2.md` is committed verbatim (verified
  head/tail and the verdict/R2-1 text; no edits).
- Worktree clean before/after; my E2E re-run wrote only to a `%TEMP%` receipts dir.

## 4. Round-2 finding closure (and re-confirmation of earlier fixes)

| finding | status | independent evidence |
|---|---|---|
| **R2-1** (should-fix) valid `unread.counts` + unreadable page/unit list raised a raw `TypeError` | **FIXED** | `_unread_trace` now requires `available[name] is not None` (`narrative_citation_context.py:204`). My exact repro for all **four** lists × {wrong-type, missing} (`unread.<list> = "not-a-list"` and `del unread.<list>`), with the sampling block still valid: `reading_trace` returns `counts=None`, `limited=None`, the affected count `None`, and the same context still resolves `citation_view`; entry 2 consumes (`status=closed`, `counts=None`, `limited=None`). No `TypeError` in any of the 9 repro variants. Regression `test_unreadable_unread_list_degrades_the_counts_to_null[8]`. |
| **R2-2** (nit) groups-only paragraph split the frozen error-code table | **FIXED** | `INTERFACES.md` §3 now holds all 11 frozen codes in one table; the "Groups-only reads never become an ambiguity gate" paragraph sits after the table. Content unchanged. |
| **R2-3** (nit) `progress.md` said 60 card cases | **FIXED** | `progress.md` now says 74 cases (5/32/26/5/6); my collection is exactly 5/32/26/5/6 = 74 and the suite passes 74. `B-final-tests.json` (`du11-test-receipt/3`) records 374/4 and the real per-module counts. |
| **B1** coverage never gates | **STILL FIXED** | Wire-validated free-form `layout_coverage` variants still consume with `layout_complete=null`; the additional coverage-family probe (unread not a dict, deferred not a list, diagnostics malformed, layout string/`{"complete":"partial"}`) consumes with nulls; groups/views remain strict (non-transported member and overlap still raise `narrative_citation_reading_invalid`). |
| **S1** `/1` multi-group gate | **STILL FIXED** | A `/1` span in three groups consumes deterministically with the published-first group; `citation_group_id` names the third; a `/2` span support in two groups still raises `narrative_citation_group_ambiguous` (no silent pick). |
| **S2** legacy entry-2 messages | **STILL FIXED** | Baseline-vs-HEAD same-call comparison of the three missing-block refusals is identical (`…missing its read receipt or manifest`; `…missing its source or narrative reference` ×2). |
| **S3** RED evidence | **STILL VALID** | The RED set (consumption/projection/e2e modules and both baseline consumers) is byte-identical to round 2; I re-ran it against the baseline tree: **27 failed, 10 passed**, exit 1, all behavioural. The round-3 fix is in the context module, which the RED deliberately excludes. |
| **S4** owned root / basetemp | **STILL FIXED** | All six committed `restore-*.json` show `restored: true`, `root_removed: true`; my independent E2E run with a temp receipts dir produced 6/6 `restored=True root_removed=True`; no `du11-owned` dir remains; both basetemp paths (`du11-pytest-f6718281`, `du11-pytest-fa65b328`) are absent, matching `C-basetemp.txt` / `C-basetemp-3.txt`. |
| **S5** projected parent identity | **STILL FIXED** | Source and code unchanged since round 2; cross-parent and `projection_id` refusals remain, legitimate `/3` still ends in `source_availability_unknown`. |
| **S6** PWF/handoff | **STILL FIXED** | `task_plan.md` records rounds 1–2 and keeps round 3 open; `findings.md` §11 maps R2-1/R2-2/R2-3; `handoff.md` is `IMPLEMENTED_REVIEW_PENDING` with 374/4. `handoff.json` is correctly deferred to the final documentation commit (the author writes it only after this PASS). |
| Round-1 nits N1–N4, N8 | **STILL FIXED** | Wire module 5 tests; null split (`context_evidence_unknown`, `context_evidence_limited=None`, `deferred.listed=None`); separate `unit_note` context span; both directions of a two-view group resolve positively; RED placeholder/B-final 20-module/279-3 lines correct. |
| N5/N6/N7/N9/N10 | **ACCEPTED-AS-DOCUMENTED** | Unchanged design observations recorded in `findings.md` §10; no correctness impact. |

## 5. New findings

**None.** No blocking, should-fix or nit was found in round 3. The one-condition fix is correct
and minimal: for a wire-valid context the four lists are always integer lists, so
`available[name] is not None` is always true and behaviour is unchanged; for an unvalidated /
malformed context it now keeps the counts unknown instead of raising.

## 6. Commands and exact results

All run in `C:/Users/郑曾波/Projects/revenue-forecast-du11-citation-closure`, `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONUTF8=1`, `-p no:cacheprovider`.

| # | command | result |
|---|---------|--------|
| 1 | 5 card modules (`wire context consumption projection e2e`) | **74 passed**, 0 failed, 0 skipped, exit **0**, 10.21 s pytest / 16.28 s wall; per module **5/32/26/5/6** (author's 74 confirmed) |
| 2 | card 12-module regression command | **279 passed, 3 skipped**, exit **0**, 82.05 s |
| 3 | authoritative 20-module run | **374 passed, 4 skipped**, exit **0**, 101.31 s (author 85.79 s under different load; counts match) |
| 4 | `python -m ruff check scripts tests tools` | `All checks passed!`, exit **0** |
| 5 | `python -m mypy scripts/contracts/ scripts/schema_compatibility.py scripts/filing_fetch_client.py scripts/trust_anchor.py` | `Success: no issues found in 11 source files`, exit **0** |
| 6 | `python tools/pre_push_gate.py` | **416 passed, 36 subtests**, `pre-push/CI checks GREEN`, exit **0**, 71.50 s |
| 7 | RED re-run (unchanged RED modules, byte-exact baseline consumers) | **27 failed, 10 passed**, exit **1** — receipts/A-red-baseline.txt still faithful |
| 8 | compatibility (legacy `/1` same call in baseline tree vs HEAD: entry-1 document+receipt, entry-2 result, `citation_trace` removed) | `identical=True` for both |
| 9 | legacy-message comparison (3 missing-block refusals) | `identical=True` (the three baseline strings) |
| 10 | prediction values (`run_forecast` before/after the traced consume on the synthetic `/2` input) | `forecast_same=True`, `segments_same=True` |
| 11 | E2E with `DU11_PWF_RECEIPTS` in a temp dir | 6 passed; 6/6 `restored=True root_removed=True`; no `du11-owned` left; basetemps absent |
| 12 | round-3 probe (`%TEMP%/du11_review3/probe3.py`, outside the repo) | R2-1 ×8, entry-2 R2-1, coverage family, group/view resolution, nulls, compatibility, prediction: all as reported; no unexpected exception |

## 7. What I could NOT verify

1. CodeGraph index state / query results (`findings.md` §2) — not re-indexed, per the card.
2. A real CWP-produced `du-production-reading/2` bundle — the frozen public `actual-090` is `/1`;
   `/2` is the synthetic descriptor wire validated by the real RF contract.
3. The declared CWP/ET commits (`34a7dd71…`, `2584b7ee…`) — those repos were not read.
4. External consumers of `revenue-narrative-consumption/1` / the trace — none in this repo.
5. The historical basetemp deletion — `C-basetemp.txt` / `C-basetemp-3.txt` are self-reported
   text receipts; both paths are absent now, which is consistent.
6. The whole `pytest tests/` suite (ran the card commands, the 20-module set and the 416-test
   pre-push gate).
7. Real company-data quality — out of scope; the fixture is synthetic.
8. The author's 85.79 s timing — I observed 101.31 s under load; counts match.

## 8. Redundant gate / duplicated validator / compatibility

- **No coverage gate remains:** coverage values (unread block, deferred, diagnostics, layout)
  degrade to `null`; only groups/views (the support-vs-context decision) are strict. The R2-1
  `TypeError` is gone; the added condition is inert for wire-valid contexts.
- **No duplicated validator / no new permission gate:** the narrow structure re-check (N6) stays
  as documented; `/1` group-only determinism (S1) is documented; the `source_role` refusal is
  card-justified.
- **Compatibility:** entry-1 document+receipt and entry-2 result are byte-identical to the
  baseline (minus `citation_trace`); the three legacy entry-2 messages are byte-identical; the
  old binding-field message is preserved; prediction values are unchanged; no existing test was
  modified. The trace has additive keys inside `revenue-narrative-citation-trace/1`
  (`context_evidence_unknown`, null-limited) and the `…-consumption/1` receipt version is
  unchanged by design; there is no external consumer yet.
- **Remaining delivery step (not a defect):** `handoff.json` and the COMPLETE status are written
  in the final pure-documentation commit after this PASS; the reviewed source SHAs above must
  not change.

---

**Conclusion:** round 3 is clean. The card's semantic goal (source-owned support/context closure
kept in the real RF claim/parameter/formula dependencies, coverage diagnostic-only, no new
permission gate, old wire and old fields compatible) is met and independently verified; the
three review rounds (1 blocking, 6+1 should-fix, 10+2 nits) are all closed. **PASS** with
0 unresolved blocking / 0 unresolved should-fix; the author may write COMPLETE + `handoff.json`
against the frozen source SHAs above.
