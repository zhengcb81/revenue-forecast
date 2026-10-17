# D-reviewer-2 — independent round-2 re-review (DU11-RF-CITATION-CLOSURE)

Reviewer: same independent agent as round 1 (not the author). Round 1 report:
`receipts/D-reviewer-1.md` (FAIL: 1 blocking + 6 should-fix + 10 nits).

## 1. Verdict

**FAIL** — no blocking defect remains, but one **new should-fix** robustness regression in the
B1 fix prevents a clean pass. All six round-1 should-fix items and the blocking item are
genuinely fixed; scope, compatibility, E2E, restore and gates all verify green.

- Blocking: **0**
- Should-fix: **1** (new: `TypeError` instead of a null/refusal for a malformed unread page/unit
  list when the sampling counts block is valid — unvalidated-context path only)
- New nits: **2** (INTERFACES error-code table split by the inserted paragraph; `progress.md`
  says "60 cases" where the suite has 66)
- Round-1 findings: B1, S1, S2, S3, S4, S5, S6 **FIXED**; nits N1–N4, N8 **FIXED**; N5, N6,
  N7, N9, N10 **ACCEPTED-AS-DOCUMENTED** (rationale in `findings.md` §10; I agree they are
  outside a correctness fix).

Reviewed HEAD: `1ae6c3b50501d53fdbcd20d341a081e87d80ebd8` on
`codex/du11-rf-citation-closure` (parent `1ada02e4`, base `568fb925`). Worktree clean
(`git status --porcelain` empty) before and after my runs; I wrote only this report.

## 2. Reviewed SHA-256 (recomputed; all nine match `receipts/B-final-tests.json`)

| # | path | SHA-256 |
|---|------|---------|
| 1 | `scripts/narrative_citation_context.py` | `8e0843a4145aa06e599894e8d6f596fc3ec267f21456f3aadd55af361559d21a` |
| 2 | `scripts/source_narrative_context.py` | `ee271c3f5be61b2c7df845b60f7962422fd45808c0c38b727a700ecc93ede259` (unchanged from round 1) |
| 3 | `scripts/research/input_evidence.py` | `c0a321f9ca905023846dafa4fe7c35b74e7d3cedc5e77bbd6882168579f338ed` |
| 4 | `tests/test_du11_narrative_citation_wire.py` | `f63ccfa381dfeb80d13c837f05a897305ee0749923e69ca77dc11122dbfdc620` |
| 5 | `tests/test_du11_narrative_citation_context.py` | `f4f9354a6bf4cfa4831bde65c41c88b0a807b383f7855dc17473b1ffaa1e857e` |
| 6 | `tests/test_du11_narrative_citation_consumption.py` | `cbd44c769240e341cb309856dc4f481aa28947fd073ea05de349cc6a00cbb7f7` |
| 7 | `tests/test_du11_narrative_citation_projection.py` | `55c071be5f6023faf6d369707267241ee88434b28635b3e97f25afe412607756` |
| 8 | `tests/test_du11_narrative_citation_e2e.py` | `cac76fe54690e34a7dfa49de2ac1bd493fbbd50030a3a952e80c4adc1361f24d` |
| 9 | `tests/fixtures/du11_narrative_citation/synthetic_reading2.json` | `368c9776402bb39497db1b95863c528ba0190b043f19905f62039f40de95c7de` |

## 3. Scope / process

- `git diff --name-only 568fb925..HEAD` is exactly the card whitelist: 3 scripts (1 new adapter,
  2 modified consumers), 5 new `test_du11_narrative_citation_*.py`, 1 new fixture, the card PWF
  dir. `git diff --name-status 568fb925..HEAD -- tests/` is all `A` (no existing test modified);
  `scripts/company_wiki_narrative_contracts.py` is untouched; no forecast/formula, CWP/FF/ET,
  `assurance/`, `.codegraph` or install/release path is touched.
- `1ada02e4..HEAD` additionally contains only the expected round-2 fixes + PWF/receipts; my
  round-1 report `receipts/D-reviewer-1.md` is committed verbatim (verified content and SHA
  `bd7ad7d8…`; the author did not edit my findings).
- `receipts/B-final-tests.json` was regenerated and its source SHA block matches my recomputation
  (9/9). `handoff.md` is `IMPLEMENTED_REVIEW_PENDING` (correct: COMPLETE/`handoff.json` only
  after a clean round 2). `handoff.json` is absent by design at this point.

## 4. Round-1 finding closure

| finding | status | independent evidence |
|---|---|---|
| **B1** free-form `layout_coverage` gated consumption | **FIXED** | `_layout_complete` now returns a bool or `None` (`narrative_citation_context.py:250-256`); `_unread_trace`/`_deferred_trace`/`_diagnostics_trace` degrade to null. Probe: a **wire-validated** `/2` context with `layout_coverage` = `{"complete":"partial"}`, `{"complete":1}`, `{"complete":null}`, `{}` all consume (`status=consumed`, `layout_complete=None`); `{"complete":true}` consumes with `True`; a non-object layout is refused by the **wire** (`invalid_reading_layout_coverage`), not the consumer. Entry 2 with a malformed `unread`/`deferred`/`selection_diagnostics`/`layout_coverage` consumes with nulls. Regression tests: `test_free_form_layout_diagnostic_never_gates_consumption[4]`, `test_free_form_layout_is_reduced_to_null_never_to_a_refusal[5]`. |
| **S1** legal `/1` span in two groups was a new gate | **FIXED** | Groups-only branch records the published-first group (`narrative_citation_context.py:404-410`). Probe with a `/1` span in **three** groups: default consumes with the first `group_id`; `citation_group_id=<third>` records the third; `/2` support-in-two-groups is **still** `narrative_citation_group_ambiguous` (ambiguity not weakened); `citation_view` on `/1` is `view_unknown`. INTERFACES §7 C2 updated; regression `test_groups_only_span_in_two_groups_is_recorded_deterministically`. |
| **S2** legacy entry-2 error texts changed | **FIXED** | Non-projected branch restores the baseline `require` pair, text and order *before* citation resolution (`input_evidence.py:326-338`). Baseline-vs-HEAD same-call comparison for missing `manifest`/`source_ref`/`narrative_ref` is **identical**: `…missing its read receipt or manifest`, `…missing its source or narrative reference`, `…missing its source or narrative reference`. Regression `test_entry_two_legacy_refusals_keep_their_published_text[3]`. |
| **S3** committed RED was stale (13 helper TypeErrors) | **FIXED** | I rebuilt the author's method independently: temp tree with the **current** `scripts/`+`tests/`+frozen wire, the two consumers restored byte-exactly from `568fb925` (`git hash-object` matches `1e6fb5e9…`/`57b1e6ff…`), adapter module absent → `27 failed, 10 passed`, exit 1, every failure behavioural (`KeyError: 'citation_trace'`, `DID NOT RAISE`, legacy/wrong projected reason); no `TypeError`, no import error. Receipt `A-red-baseline.txt` matches exactly (27/10, 9.80 s vs my 12.78 s). |
| **S4** E2E left its owned root; basetemp deletion unreceipted | **FIXED** | Fixture deletes `tmp_path/du11-owned` and records `root_removed: true` (`e2e.py:138-145`). All six committed `restore-*.json` show `restored: true`, `root_removed: true`; my independent E2E run with `DU11_PWF_RECEIPTS` in a temp dir produced 6/6 `restored=True root_removed=True`, and no `du11-owned` directory remains under `%TEMP%\pytest-of-*`. `receipts/C-basetemp.txt` records `BASETEMP=…du11-pytest-f6718281`, `DELETED=true`, `VERIFIED_ABSENT=True`; that path is absent now. |
| **S5** `_projected_parent` matched only the content SHA | **FIXED** | Requires `source_id` + `content_sha256` (`input_evidence.py:262-286`) and, when `subject_binding.item_key` exists, `projection_id`. Probe: a re-signed span against the other parent → `ForecastInputError: narrative span does not bind any projected parent source`; a re-signed `projection_id` → `…does not bind its projected subject`; a legitimate `/3` context still reaches `source_availability_unknown` (no invented publication). Regression `test_entry_two_cannot_borrow_a_foreign_projected_parent`. |
| **S6** stale/premature PWF; missing `handoff.json` | **FIXED** | `task_plan.md` phases A–C complete, D in progress; D9 corrected (no `reader_command`); D10–D12 record the review-driven decisions; `findings.md` §10 maps every round-1 finding to its fix; `handoff.md` is `IMPLEMENTED_REVIEW_PENDING` and says `handoff.json` is written only after a clean round 2. `handoff.json` absent is correct here (this round is not clean). |
| N1 wire "test" module had 0 tests | **FIXED** | `tests/test_du11_narrative_citation_wire.py` now has 5 tests (builder legality for `/2`, `/1`, no-reading; re-sign; tampered body refused). |
| N2 unknown→0/false | **FIXED** | Non-view closures: `context_evidence_limited=None`; trace counts split `context_evidence` / `context_evidence_unknown`; `deferred.listed=None` without a reading. Probe: `[nulls_group_only] {…'context_evidence': 0, 'context_evidence_unknown': 1…} limited=None`; `[nulls_absent] deferred={'count': None, 'listed': None, 'limited': None}`. INTERFACES/tests updated. |
| N3 no independent unit span | **FIXED** | Fixture adds `unit_note` (`unit_declaration`) as context in both table views; the two-view test asserts 3 context ids including the unit. |
| N4 Q/A second direction only a refusal | **FIXED (documented scope)** | `test_both_legal_directions_of_a_two_view_group_resolve_positively` consumes both directions of a two-view group over two company statements. The Q/A second direction stays a deliberate `source_role` refusal (INTERFACES §4 documents it). |
| N5/N6/N7/N9/N10 | **ACCEPTED-AS-DOCUMENTED** | Formula refs stay in the existing dependencies; the narrow structure re-check is justified by entry 2 accepting unvalidated dicts (it is not a second wire authority); per-binding re-validation is bounded by wire limits; the trace is additive under `…-consumption/1` and is separately versioned; the offline guard covers the pytest process while the only children are the local stub reader and calculator. I agree these are not correctness defects. |
| N8 receipt hygiene | **MOSTLY FIXED** | A-red now uses a `<baseline-temp-tree>` placeholder (no mojibake); B-final says `<20 modules>`; progress 265/3 corrected to 279/3. One new inaccuracy: `progress.md:51` says the 5 card modules are "60 cases" — the suite collects **66** (5/24/26/5/6). Nit R2-3. |

## 5. New findings

### R2-1 — should-fix (new, introduced by the B1 lenient-coverage refactor): raw `TypeError` for a malformed unread page/unit list when the counts block is valid

- **File:line:** `scripts/narrative_citation_context.py:185-205` (`_unread_trace`), specifically
  the comparison at `:204`: `if all(value is not None and value >= available[name] …)`.
  `available[name]` is `None` when the corresponding `opaque_pages` / `deferred_pages` /
  `deferred_unit_ids` / `unassigned_unit_ids` list is missing or malformed, while `value` is an
  int from a valid `unread.counts` block → `int >= None` → `TypeError`.
- **Root cause:** the B1 fix made the list readers lenient (`_page_count`/`_id_count` return
  `None`) but the counts-vs-list consistency check still compares against that `None`; the
  "coverage degrades to null" invariant is broken exactly where the lists are missing.
  (Round 1 raised a named `narrative_citation_reading_invalid` here; round 2 now raises an
  unnamed `TypeError` — a regression for that input.)
- **Reproduction (temp probe / stdin, no repo write):**
  ```python
  ctx = validated("2").to_dict()
  ctx["reading_context"]["unread"]["opaque_pages"] = "not-a-list"   # counts/limited stay valid
  reading_trace(ctx)
  # TypeError: '>=' not supported between instances of 'int' and 'NoneType'
  bind_parameter_evidence(..., {"narrative_context": ctx, "span_id": answer})
  # same TypeError (the citation trace is built at the end)
  ```
  Also reproduced with `deferred_pages`, `deferred_unit_ids`, `unassigned_unit_ids`, and with the
  list deleted entirely. A malformed `unread.counts` value does **not** crash (the `value is not
  None` short-circuit holds); the crash is only counts-valid + list-unreadable.
- **Impact:** not reachable from a wire-validated context (the wire requires the four lists), so
  no production bundle / prediction is affected; but entry 2 is explicitly tested with
  unvalidated dicts (defensive refusals) and the adapter is a public function, so a malformed
  coverage block escapes as a raw `TypeError` instead of `null` or a named refusal — contrary to
  the frozen contract ("coverage parsing never gates… degrades to null") and to the author's
  round-2 claim.
- **Fix (small):** include `available[name] is not None` in the `all(...)` condition (or skip
  resolving counts when any consumed list is unreadable); add a regression for
  counts-valid + one list malformed/missing on both the pure adapter and entry 2.

### R2-2 — nit: the inserted "Groups-only" paragraph splits the frozen error-code table

`INTERFACES.md:50-58`: the paragraph at line 52 sits between the
`narrative_citation_span_invalid` row and the `narrative_citation_context_only` /
`narrative_citation_source_role_refused` rows, so the last two rows render outside the table.
Content is present and correct; move the paragraph after the table.

### R2-3 — nit: `progress.md` says "60 cases", the suite has 66

`progress.md:51` "(5 modules, 60 cases)". Observed collection:
wire 5 + context 24 + consumption 26 + projection 5 + e2e 6 = **66**; `B-final-tests.json`'s
366 total is consistent with 66 (+279 +21 from the three extra modules). Only the `progress.md`
number is wrong (the parent message repeats it).

## 6. Commands and exact results

All run in `C:/Users/郑曾波/Projects/revenue-forecast-du11-citation-closure`, `PYTHONDONTWRITEBYTECODE=1`,
`PYTHONUTF8=1`, `-p no:cacheprovider`.

| # | command | result |
|---|---------|--------|
| 1 | 5 card modules (`wire context consumption projection e2e`) | **66 passed**, 0 failed, 0 skipped, exit **0**, 10.06 s pytest / 17.9 s wall (author's "60" is **refuted**; per module 5/24/26/5/6) |
| 2 | card 12-module regression command | **279 passed, 3 skipped**, exit **0**, 68.04 s / 75.95 s |
| 3 | authoritative 20-module run | **366 passed, 4 skipped**, exit **0**, 145.22 s (author 99.37 s; counts match) |
| 4 | `python -m ruff check scripts tests tools` | `All checks passed!`, exit **0** |
| 5 | `python -m mypy scripts/contracts/ scripts/schema_compatibility.py scripts/filing_fetch_client.py scripts/trust_anchor.py` | `Success: no issues found in 11 source files`, exit **0** |
| 6 | `python tools/pre_push_gate.py` | **416 passed, 36 subtests**, `pre-push/CI checks GREEN`, exit **0**, 103.79 s (author 79.14 s; counts match) |
| 7 | RED reproduction: temp tree, current `scripts`/`tests`/wire, two consumers byte-exact from `568fb925`, adapter absent, 3 modules | **27 failed, 10 passed**, exit **1** — matches `A-red-baseline.txt`; all failures behavioural |
| 8 | compatibility: same legacy `/1` calls in baseline tree and HEAD (entry 1 document+receipt, entry 2 result, `citation_trace` removed) | `identical=True` for both |
| 9 | legacy messages: same three missing-block calls in baseline tree and HEAD | `identical=True` (three exact baseline strings) |
| 10 | E2E with `DU11_PWF_RECEIPTS` pointed at a temp dir | 6 passed; 6/6 `restored=True root_removed=True`; no `du11-owned` remains; basetemp receipt path absent |
| 11 | round-2 probe (`%TEMP%/du11_review2/probe2.py`, outside the repo) | layout family, coverage family, `/1` three-group, `/2` ambiguity, cross-parent/`projection_id`, mixed classic+narrative, nulls: all as reported above; the only unexpected result is R2-1 |

## 7. What I could NOT verify

1. CodeGraph index state / query results (`findings.md` §2) — not re-indexed, per the card.
2. A real CWP-produced `du-production-reading/2` bundle — the frozen public `actual-090` is `/1`;
   `/2` is the synthetic descriptor wire validated by the real RF contract.
3. The declared CWP/ET commits (`34a7dd71…`, `2584b7ee…`) — repos not read.
4. External consumers of `revenue-narrative-consumption/1` / the trace—none in this repo.
5. The historical basetemp deletion — `C-basetemp.txt` is a self-reported text receipt; the path
   is absent now, which is consistent.
6. The whole `pytest tests/` suite (ran the card commands, the 20-module set and the 416-test
   pre-push gate).
7. Real company-data quality — out of scope; fixture is synthetic.
8. The author's 99.37 s timing — I observed 145.22 s under concurrent load; counts match.

## 8. Redundant gate / duplicated validator / compatibility

- **No coverage gate remains:** the B1 defect is fixed structurally (only groups/views strict);
  the S1 ambiguity gate is removed with the published-first group documented; nothing gates on
  unread/deferred/sampling/layout.
- **No new gate:** coverage values degrade to null; the pure structure re-check (N6) remains as a
  documented, bounded re-check, not a second wire authority.
- **Compatibility:** legacy entry-1 document+receipt and entry-2 result are byte-identical to the
  baseline (minus `citation_trace`); the three legacy entry-2 messages are byte-identical; old
  binding-field message preserved; prediction values unchanged (card test + E2E CLI equality);
  no existing test modified. The trace gained an additive `context_evidence_unknown` key inside
  `revenue-narrative-citation-trace/1` (internal to this card, no external consumer yet); the
  `…-consumption/1` receipt version is unchanged by design.
- **Remaining issue:** R2-1 (raw `TypeError` for an unvalidated malformed unread list) — the only
  reason this round is not a PASS; it is a one-condition fix plus a regression test.
