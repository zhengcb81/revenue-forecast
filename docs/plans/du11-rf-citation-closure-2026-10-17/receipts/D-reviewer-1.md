# D-reviewer-1 — independent final quality review (DU11-RF-CITATION-CLOSURE)

Reviewer: independent agent (not the author). Written under the card's rule "必须执行独立最终质量审查".

## 1. Verdict

**FAIL**

The implementation is substantively correct and every number the author reported reproduces
(46/279/346 tests, ruff 0, mypy 0, pre-push gate 416/36), and the legacy `/1` receipt/document
and entry-2 result are byte-identical to the baseline. However **one blocking defect** makes a
legal, wire-validated reading context a hard refusal on a diagnostic-only field
(`layout_coverage.complete`), which directly contradicts the card ("reading coverage 只作明确
诊断，不因此新增预测许可门禁") and the frozen interface ("an incomplete layout is a
diagnostic, never a gate"). Several smaller compatibility / evidence defects are listed as
should-fix. The source commit does not need to be rewritten; the blocking point is a ~3-line
fix plus a regression test.

- Blocking: **1**
- Should-fix: **6**
- Nits / observations: **10**

Reviewed commit: `1ada02e41c2f16717f8fd0013d972cd279370714` on
`codex/du11-rf-citation-closure`, base `568fb9256885eb31a0f76d9ead59fd0f98575073`.
Working-tree heading at review start: clean (`git status --porcelain` empty). During the review
the author wrote **PWF-only** files into the working tree (`handoff.md`,
`receipts/C-prepush-gate.txt`, edits to `findings.md`/`progress.md`); none of them touches the
reviewed source/test blobs, and `git diff --stat HEAD -- scripts tests` is empty.

## 2. Reviewed artefacts and SHA-256 (recomputed here)

`git status --porcelain` shows no modification under `scripts/` or `tests/`, so these worktree
hashes are also the blobs of `1ada02e4`; all nine match `receipts/B-final-tests.json`.

| # | path | SHA-256 |
|---|------|---------|
| 1 | `scripts/narrative_citation_context.py` | `5655afe94fbfd20009490a531f272cf99cfc8db1c7d92947f188063d056b9d55` |
| 2 | `scripts/source_narrative_context.py` | `ee271c3f5be61b2c7df845b60f7962422fd45808c0c38b727a700ecc93ede259` |
| 3 | `scripts/research/input_evidence.py` | `a252dd383886fc04ff228863427c4fada0c4dac4dfacfadf2a290d33501d5920` |
| 4 | `tests/test_du11_narrative_citation_consumption.py` | `6e30900e9635cac0db7adfd7d91b59ec82af1259001ee68aeb46e0aa34da4db4` |
| 5 | `tests/test_du11_narrative_citation_e2e.py` | `3c4cf4b7f40a893005579e748b6ccc8796eb914123aaaeeb545e1379c16cce23` |
| 6 | `tests/test_du11_narrative_citation_context.py` | `797bf9e4236c90de7498da2b6068ef0fa13d706f68d808b49e5c9a1275fdcb4f` |
| 7 | `tests/test_du11_narrative_citation_projection.py` | `3b565ae429c0ae00a5c5f291ec7f71f8f551abee959f34e4c2202cd22b129ba2` |
| 8 | `tests/test_du11_narrative_citation_wire.py` | `5e960cb7faaf28418933aa7c10b552a460729303d89f57af8d9efb6c0bd2ba91` |
| 9 | `tests/fixtures/du11_narrative_citation/synthetic_reading2.json` | `5173793191d646db4222a9a8b915bdaa54b579ef19db6802b602d5fd47d8561a` |

Scope check: `git diff --name-only 568fb925..HEAD` returns exactly the card whitelist (3 scripts
+ 5 new `test_du11_narrative_citation_*.py` + 1 fixture + the card PWF dir). No existing test was
modified, `scripts/company_wiki_narrative_contracts.py` is untouched (`git diff --stat` empty),
and there are no changes to forecast/formula, CWP/FF/ET, `assurance/`, `.codegraph`, install or
release files.

## 3. Compliance table

### Phase A (investigation / real RED)

| Requirement | Evidence | Verdict |
|---|---|---|
| Baseline + WIP isolation, fixed commit | HEAD `568fb925` basename; clean status at review start; diff scope above | PASS |
| CodeGraph structural query, index gap recorded | `findings.md` §2; I did not query/re-index CodeGraph (card forbids it), so the query results themselves are **unverified** | PARTIAL (documented) |
| Both real entries and their call chains identified | `findings.md` §3; confirmed in `scripts/source_narrative_context.py:103`, `scripts/research/input_evidence.py:49`, callers as listed | PASS |
| Baseline defects are real | Read `git show 568fb925:` of both files: entry 1 has the exact-field set + no `reading_context` use; entry 2 requires `manifest`/`source_ref` and therefore cannot read `/3`; neither keeps unread/deferred/layout | PASS |
| Behavioural RED (not a source-string check) | `receipts/A-red-baseline.txt` contains `KeyError: 'citation_trace'`, `DID NOT RAISE`, and the projected-wire message mismatch. **But 13 of its 18 failures are `TypeError: 'NarrativeContext' object is not subscriptable` at `test_du11_narrative_citation_consumption.py:69` (the pre-`as_value` helper); the committed line 69 is `request = request or {"as_of_date": as_value(context)["as_of_date"]}`.** I regenerated the RED independently: final 4 card modules against baseline sources (temp copy, `git show 568fb925:...`) → **21 failed, 25 passed**, all behavioural (no helper crash). So the substance is real; the receipt/summary is stale | PASS on substance, **FAIL on evidence accuracy (S3)** |
| Hand-calculation counterexamples (question span, first-view-wins, table row) | `test_du11_narrative_citation_consumption.py:156,162,172`; `test_du11_narrative_citation_context.py:78,93` | PASS |
| Frozen selection field / trace schema / error codes / compat matrix | `INTERFACES.md`; but the `/1` matrix row disagrees with the implementation (S1) | PARTIAL (S1) |

### Phase B (shared implementation + checklist)

All items below were exercised through the **real** entry functions (the test helper only patches
the reader boundary, `unittest.mock.patch("source_narrative_context.read_narrative_context")`).

| Card item | Proving test (file:line) | Verdict |
|---|---|---|
| old legal single span without `reading_context` | `consumption.py:246 test_absent_reading_context_never_claims_complete_coverage`; existing `test_source_preparation_complete_result.py` | PASS |
| `reading/1` | `consumption.py:230 test_reading_one_group_closure_has_no_view_claim`; E2E positive (`e2e.py:242-253`) | PASS |
| `reading/2` Q/A both directions + explicit wrong attribution | fixture `synthetic_reading2.json:32-38` has both views; `consumption.py:85` (answer=view 0), `consumption.py:162` (question refused as wrong attribution). The **question-supporting view is never positively consumed** (the `source_role` refusal fires first) — structurally present, only one direction observable (N4) | PASS w/ nit |
| table row + unit/header/footnote | `consumption.py:156,172`; fixture `:25-30`. There is **no separate unit span**; "unit" is only text inside the header (N3) | PASS w/ nit |
| several groups under one parent | `consumption.py:302`; `context.py:120` | PASS |
| ambiguous view | `consumption.py:172`; `context.py:78` | PASS |
| missing / duplicate / cross support-context ids | `context.py:156-185` (8 mutations: non-transported, duplicate view, missing partition, overlap, empty support, duplicate member); entry-2 `consumption.py:399` | PASS |
| foreign parent / source SHA | `projection.py:103`; `context.py:146`; `e2e.py:301` (foreign snapshot sha + stale as-of); entry-2 cross-parent only latent (S5) | PASS w/ S5 |
| projected v3 `source_locator`/`pointer` | `projection.py:82,112` (entry 1), `consumption.py:419` (entry 2 resolves parent then `source_availability_unknown`; `input_evidence.py:325-333,350-357`) | PASS |
| unread / opaque / deferred + sampling counts / `limited` | `consumption.py:85,267`; `context.py:68`; `e2e.py:245-249`; `synthetic_reading2.json:58-72` | PASS |
| empty binding / `not_consumed` | `consumption.py:322,334`; existing `test_source_preparation_complete_result` | PASS |
| unique context choice tied to the real formula dependency | `consumption.py:172-189` (explicit view) + `:134-137` (`formula_refs` non-empty, same claim/parameter); `:140` prediction equality; E2E CLI equality `e2e.py:255-259` | PASS |
| unread material not a refusal | `context.py:68`; `consumption.py:267` asserts consumed with `limited=True`; **but a free-form `layout_coverage.complete` is a refusal → B1** | **FAIL (B1)** |
| parameter/formula/prediction unchanged | `consumption.py:140`; E2E `e2e.py:255-258`; plus my baseline-vs-HEAD byte comparison (entry 1 receipt+document, entry 2 result, `citation_trace` removed) = **identical** | PASS |
| central regression | 279 passed / 3 skipped (card command set), 346 / 4 (author's 20 modules), see §5 | PASS |
| ruff / mypy | 0 / 0 | PASS |

### Phase C (isolated E2E) and delivery

| Requirement | Evidence | Verdict |
|---|---|---|
| frozen public wire, fake only at CWP process boundary | `e2e.py:45-75,167-183`: stub `company_wiki/source_catalog/narrative_transport_cli.py` on `PYTHONPATH`; the real reader starts the real bounded subprocess (`company_wiki_narrative_reader.py:20-25`), the real `validate_narrative_response` checks the bytes, the real consumer and `revenue_forecast.py` CLI run (`e2e.py:204-215`). Frozen `actual-090` is the synthetic `Acme business update` (`docs/plans/shared-reading-consumer-2026-10-14/fixtures/actual-090-*`, 982/4905/1860 B as in `findings.md` §5) | PASS |
| no real company original in fixtures/reports | only `synthetic_reading2.json` (marked `synthetic`) + existing frozen fixture; no company bytes | PASS |
| read CLI exports the complete context | `e2e.py:262-277` (exactly one reader call, `reading_context` and `evidence_spans` equal to the frozen bundle) | PASS |
| negative controls | `e2e.py:284-298` (bad bytes → `artifact_bytes_mismatch`, unavailable → `reader_unavailable`, sleep → `reader_timeout`); `:301-326` (wrong as-of, bad bytes/hash, foreign parent, stale input date). No real provider/network/LLM call | PASS |
| offline guard | `e2e.py:144-152` patches `socket.socket.connect`, `socket.create_connection`, `urllib.request.urlopen` in the pytest process only; child processes are not guarded (they run the stub and the calculator, which need no network) — N10 | PASS w/ nit |
| restore receipts prove SHA+mtime restoration | 6 × `receipts/restore-*.json`: `initial_bytes_mtime` for `sentinel.bin` + `out/existing.json`, `created`/`removed` lists, `restored: true`, `residual_directories: ["out","sentinel.bin"]`. The fixture asserts `after[name] == record` and `snapshot(root) == baseline` (`e2e.py:114-122`) | PASS on contents |
| owned TemporaryDirectory itself deleted | **not done by the test**: `root = tmp_path/"du11-owned"` is left in place; the handoff says the basetemp was deleted afterwards, but no receipt records it. Currently no `du11-owned` dir remains under `%TEMP%\pytest-of-*` (pytest retains only the 3 newest session roots; those came from my runs) — S4 | **PARTIAL** |
| delivery PWF | `task_plan.md` is stale (Phases pending, D9 wrong); `handoff.md` exists only as an uncommitted file; **`handoff.json` is absent**; `handoff.md` claims `COMPLETE` and cites `receipts/D-reviewer-1.md` before the review existed — S6 | **FAIL (S6)** |

## 4. Findings

### B1 — blocking: a free-form layout diagnostic gates consumption

- **File:line:** `scripts/narrative_citation_context.py:259-268` (`_layout_complete`), reached by
  `reading_trace` (`:283`), therefore by `narrative_read_receipt`
  (`scripts/source_narrative_context.py:44`), `consume_narrative_input`
  (`scripts/source_narrative_context.py:163`) and entry 2's `citation_trace`
  (`scripts/research/input_evidence.py:227`). Also reached by `source_preparation.py:438`.
- **Root cause:** the adapter treats `layout_coverage.complete` as a strict invariant although
  the only wire validator deliberately leaves `layout_coverage` a free dict
  (`scripts/company_wiki_narrative_contracts.py:621`: `isinstance(..., dict)` only) and the card
  and INTERFACES say layout coverage is diagnostic-only ("an incomplete layout is a diagnostic,
  never a gate", `INTERFACES.md`; card line 20/30/68). A diagnostic payload must degrade to
  `null`, never to a refusal.
- **Reproduction (probe, temp only):** build `tests/test_du11_narrative_citation_wire.py::wire("2")`,
  set `bundle["reading_context"]["layout_coverage"] = {"complete": "partial"}`, `resign(...)`,
  then `validate_narrative_response(...)` **succeeds**, and
  `consume_narrative_input(...)` raises
  `NarrativeCitationError: narrative_citation_reading_invalid: layout_coverage.complete is not a boolean`.
  My probe printed `[free_layout_wire_accepted] True` then
  `[free_layout_consume] NarrativeCitationError -> ... layout_coverage.complete is not a boolean`.
  (`{"complete": null}` / a missing key are accepted and yield `layout_complete: null`.)
- **Impact:** a legal `du-production-reading/1` or `/2` bundle from CWP that uses any other JSON
  value/form for the free-form layout dict cannot be consumed at all (both entries, and
  `source_preparation_result`). This is exactly the forbidden coverage gate.
- **Fix:** return `complete` only when `type(complete) is bool`, otherwise `None`; never `_fail`
  for this field; add a validated-wire regression test.

### S1 — should-fix: legal `/1` span in two groups is a new binding gate and the matrix is wrong

- **File:line:** `scripts/narrative_citation_context.py:419-429` (groups-only branch:
  `elif len(candidates) == 1 … else: _fail("narrative_citation_group_ambiguous")`), versus
  `INTERFACES.md` §7 row C2 ("`/1` + reading/1 → consume; group closure only").
- **Root cause:** the "no silent first pick" rule (correct for citation **views**) was extended to
  group-only membership, where the group carries no support/context semantics; the compatibility
  matrix was not updated.
- **Reproduction:** `descriptor()` + a second `/1` group containing `answer` validates through
  `validate_narrative_response` (3 groups; the wire imposes no cross-group uniqueness), then
  `consume_narrative_input(...)` raises `narrative_citation_group_ambiguous: the span belongs to
  more than one reading group`; it only consumes if the caller passes the **new**
  `citation_group_id`. Probe: `[groups_only_two_groups_valid] … groups= 3`,
  `[groups_only_span_in_two_groups] NarrativeCitationError -> ... group_ambiguous`,
  `[groups_only_named] closure= reading_group`.
- **Impact:** old callers of a legal overlapping `/1` wire (which the baseline consumed) now fail
  without knowing the new field; the frozen matrix says they consume.
- **Fix/decision:** either deterministically consume a group-only span (e.g. choose the first
  group by published order and record it — no support/context promotion is involved), or update
  INTERFACES §7 C2 and record the new requirement explicitly; add a test either way.

### S2 — should-fix: legacy entry-2 error messages changed

- **File:line:** `scripts/research/input_evidence.py:323-324` and `:337-338`.
- **Root cause:** the projected-`/3` branch split the two old `require` calls and reworded them
  instead of preserving the old texts on the non-projected path.
- **Reproduction (baseline temp tree vs HEAD, same golden `/1` context):**

  | missing block | baseline `ForecastInputError` | HEAD `ForecastInputError` |
  |---|---|---|
  | `manifest` | `narrative_context is missing its read receipt or manifest` | `narrative_context is missing its manifest or source reference` |
  | `source_ref` | `narrative_context is missing its source or narrative reference` | `narrative_context is missing its manifest or source reference` |
  | `narrative_ref` | `narrative_context is missing its source or narrative reference` | `narrative_context is missing its read receipt or narrative reference` |

- **Impact:** public error text on a legacy path changed, not required by the card. The happy
  path is byte-identical (verified), so no test catches it. ROOT/other repos that match the
  message (as the repo's own tests do elsewhere with `match=`) would see a different string.
- **Fix:** in the non-projected branch, raise the exact old messages; keep the new wording only
  where `/3` requires it.

### S3 — should-fix: the committed RED is stale relative to the frozen tests

- **File:line:** `receipts/A-red-baseline.txt:4-39` (13 × `TypeError: 'NarrativeContext' object
  is not subscriptable` at `test_du11_narrative_citation_consumption.py:69`),
  `receipts/B-final-tests.json` `red_evidence`, `progress.md` "RED (18 failures…)",
  uncommitted `handoff.md` "18 behavioural failures".
- **Root cause:** the RED was captured before the test helper `as_value` was added
  (`progress.md` "Test helpers indexed a `NarrativeContext` object"); the receipt was never
  regenerated after the final test file was frozen.
- **Reproduction:** line 69 in the committed test is `as_value(context)`; in the RED log the same
  line raised `TypeError`. I ran the final 4 card modules against the baseline implementation
  (temp copy with `git show 568fb925:scripts/source_narrative_context.py` and
  `…/research/input_evidence.py`): **21 failed, 25 passed**, all behavioural (`KeyError:
  'citation_trace'`, `DID NOT RAISE`, legacy/wrong message), no helper crash. So the RED
  substance is genuinely real, but "18 behavioural failures" is not accurate.
- **Fix:** regenerate `A-red-baseline.txt` with the frozen tests against `568fb925`, or annotate
  it (13 harness crashes + 5 behavioural) and correct the summaries. Also fix the mojibake in the
  logged Windows path.

### S4 — should-fix: the owned temporary root is not deleted by the E2E; the handoff claim is not receipted

- **File:line:** `tests/test_du11_narrative_citation_e2e.py:107-141` (`owned` fixture: `root =
  tmp_path/"du11-owned"`; asserts `snapshot(root) == baseline`, writes `residual_directories`,
  never removes `root`); all six `receipts/restore-*.json` record
  `residual_directories: ["out","sentinel.bin"]`.
- **Root cause:** the fixture restores *contents* but leaves the owned root to pytest; the card
  (line 66) requires the owned TemporaryDirectory itself to be deleted, and the handoff's
  "basetemp deleted afterwards and its absence verified" has no receipt.
- **Reproduction:** run the E2E with `DU11_PWF_RECEIPTS` set; the receipt is written while
  `tmp_path/du11-owned/` still contains `sentinel.bin` and `out/`. My current `%TEMP%` check
  found 0 remaining `du11-owned` dirs, but that is pytest's 3-session retention, not the test.
- **Fix:** `shutil.rmtree(root)` at the end of teardown (after the receipt is written) and record
  `root_removed: true`; or use a factory-owned root that is explicitly removed.

### S5 — should-fix (latent): `_projected_parent` matches only the content SHA, not the span's own source

- **File:line:** `scripts/research/input_evidence.py:262-276` (`_projected_parent`: `next(item …
  item.get("content_sha256") == parent_sha)` without `item["source_id"] == span["source_id"]`),
  versus the wire's own `_span_parent` (`scripts/company_wiki_narrative_contracts.py:785-791`,
  which requires both).
- **Root cause:** the new projected branch re-implements the parent lookup more loosely than the
  validator whose contract it claims to re-use ("A projected span keeps its own original parent;
  nothing is merged").
- **Reproduction (probe):** a validated two-parent `/3` context, one span's
  `structured_value.parent_content_sha256` changed to the other parent's SHA and its
  `output_sha256`/`span_id` re-signed (so the entry's own identity check passes) →
  `_projected_parent` returns the **foreign** parent:
  `[projected_cross_parent] accepted span.source_id=…bbbb… parent.source_id=…0dab… same= False`.
  Entry 2 then still refuses (always) with `[projected_cross_parent_entry] ForecastInputError ->
  source_availability_unknown`, so no wrong evidence is produced **today**; when CWP publishes
  the availability fact (the documented upstream need) this becomes live cross-parent stitching,
  which the card forbids.
- **Fix:** require `span["source_id"] == parent["source_id"]` (and, if practical,
  `projection_id == subject item_key`), matching `_span_parent`; add a negative test.

### S6 — should-fix: PWF delivery docs are stale / premature

- **File:line:** `docs/plans/du11-rf-citation-closure-2026-10-17/task_plan.md:36-93` (Phases
  A/B/C/D all `in_progress`/`pending`, checkboxes unchecked), `:107` (D9 claims
  "`consume_narrative_input` gains optional `reader_command`" — the code has no such parameter,
  `progress.md` says it was dropped, and `INTERFACES.md` §8 says the signature is unchanged);
  uncommitted `handoff.md:3` ("Status: **COMPLETE**"), `:113` references `handoff.json` which
  **does not exist**; it also cites `receipts/D-reviewer-1.md` before this review existed.
- **Root cause:** planning/handoff docs were not reconciled after implementation and after the
  independent-review gate was still open.
- **Reproduction:** `Test-Path …/handoff.json` → `False`; `git status` shows `handoff.md` only as
  an untracked working-tree file; `Select-String task_plan.md reader_command` shows D9.
- **Fix:** mark task_plan phases/decisions complete (with the actual interface), add
  `handoff.json` with the required fields, and keep the status `IMPLEMENTED_REVIEW_PENDING`
  until this review is resolved (the card forbids a self-declared COMPLETE before the reviewer
  signs off).

### Nits / observations

- **N1** `tests/test_du11_narrative_citation_wire.py` matches the `test_*` glob but contains
  **0 tests** (only fixture builders); it is counted as one of the "20 modules". Harmless, but
  rename it (e.g. `du11_narrative_citation_wire.py`) for honesty of module counts.
- **N2** Unknown-vs-zero: for `reading_group`/`ungrouped` closures
  `context_evidence_ids`/`context_evidence_count` are `null` but `context_evidence_limited` is
  `false`; `trace["counts"]["context_evidence"]` sums unknown as `0`; `deferred.listed` is `0`
  when there is no reading context. Probe: `[group_only_null] {'context_evidence_ids': None,
  'context_evidence_count': None, 'context_evidence_limited': False}`, `[absent_reading]
  {'deferred': {'count': None, 'listed': 0, 'limited': None}, …}`. INTERFACES does not freeze
  these as null, but the card's "unknown stays null" spirit suggests `null`.
- **N3** The "unit" element of "table row + unit/header/footnote" has no independent span: the
  USD unit is inside the header text (`synthetic_reading2.json:14`). Header/footnote behavior is
  proven; unit-as-context is only implicit.
- **N4** The Q/A "second direction" (the view with `support=[question]`) is never positively
  consumed: `source_role=investor_question` refuses before any test can observe that view's
  support ids. The fixture encodes it (`:36-37`) and the refusal is proven
  (`consumption.py:162`), but "双方视图" is one positive + one refusal, not two.
- **N5** The trace joins the real dependency by `claim_id`/`parameter_id`; `formula_refs` stay in
  the old `receipt["dependencies"]` and are not copied into the trace (documented in
  INTERFACES §4; the association is genuine, the trace itself is not decorative but is
  formula-ref-free).
- **N6** The pure adapter re-checks group membership, view partition and the unread sampling
  shape that `company_wiki_narrative_contracts._reading_context` already validates. It is
  bounded and justified by entry 2 accepting unvalidated dicts, and it is not a second
  *authority*; still, it is a partial second validator (the card said "avoid a second
  validator").
- **N7** `resolve_span` re-validates the whole reading context (all groups) on every binding, so
  consumption is O(bindings × groups); bounded by the wire limits (≤512 groups), acceptable.
- **N8** Receipt hygiene: `B-final-tests.json` says `"<19 modules>"` while its module list has
  20; `progress.md` says "265 passed, 3 skipped (12 modules)" but the card's 12-module command
  yields **279 passed, 3 skipped** (maybe a different subset — unverifiable); `A-red-baseline.txt`
  contains mojibake in the Windows path.
- **N9** The trace is added under `revenue-narrative-consumption/1` / `/3` without bumping the
  receipt schema version (INTERFACES D1 freezes this). Additive and harmless within RF, but
  strict external consumers of that versioned object would see a new key.
- **N10** The offline guard patches only the pytest process; E2E child processes are not guarded
  (they run the stub reader and the calculator, which need no network). Not a leak, but not an
  airtight guard.

## 5. Exact commands and results

All from `C:/Users/郑曾波/Projects/revenue-forecast-du11-citation-closure` (workdir), Windows,
`python = C:\Miniconda\python.exe`. `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUTF8=1` were set for
every run (the card command already sets them; I also set them for the regression command to keep
the worktree clean).

| # | command | result |
|---|---------|--------|
| 1 | `python -m pytest -q --tb=short -p no:cacheprovider tests/test_du11_narrative_citation_context.py tests/test_du11_narrative_citation_consumption.py tests/test_du11_narrative_citation_projection.py tests/test_du11_narrative_citation_e2e.py` | **46 passed**, 0 failed, 0 skipped, exit **0**, 16.20 s pytest / 23.47 s wall |
| 2 | `python -m pytest -q --tb=short -p no:cacheprovider tests/test_source_preparation_complete_result.py tests/test_architecture_dependency_uses.py tests/test_w04_public_consumer.py tests/test_citation_attribution_narrative_contract.py tests/test_shared_reading_narrative_contract.py tests/test_source_clock.py tests/test_evidence_input_lineage.py tests/test_input_semantics_e2e.py tests/test_narrative_source_preparation_transport.py tests/test_narrative_source_preparation_e2e.py tests/test_company_wiki_narrative_reader.py tests/test_source_preparation.py` | **279 passed, 3 skipped**, exit **0**, 83.48 s / 91.31 s |
| 3 | `python -m pytest -q --tb=short -p no:cacheprovider` + the author's 20 modules | **346 passed, 4 skipped**, exit **0**, 94.52 s / 109.52 s (author 346/4, 93.83 s → **confirmed**) |
| 4 | `python -m ruff check scripts tests tools` | `All checks passed!`, exit **0** |
| 5 | `python -m mypy scripts/contracts/ scripts/schema_compatibility.py scripts/filing_fetch_client.py scripts/trust_anchor.py` | `Success: no issues found in 11 source files`, exit **0** |
| 6 | `python tools/pre_push_gate.py` (repo CI gate) | `416 passed, 36 subtests passed`, `pre-push/CI checks GREEN`, exit **0**, 65.48 s (author 416/36, 79.14 s → confirmed) |
| 7 | RED reproduction: temp copy of the tree + `git show 568fb925:scripts/source_narrative_context.py` and `…/research/input_evidence.py`, then command #1 | **21 failed, 25 passed**, exit **1** — all failures behavioural (trace missing, silent context/question/ambiguity promotion, legacy message, projected-wire reason) |
| 8 | Compatibility: same `consume_narrative_input` / `bind_parameter_evidence` call in baseline temp tree and HEAD, JSON minus `citation_trace` | `[compat_entry1_receipt_and_doc] identical=True`; `[compat_entry2_result] identical=True` |
| 9 | Probe (`%TEMP%/du11_review/probe.py`, outside the repo) | all listed probes as reported in §4; exit 0 |

Note: the author's `A-red-baseline.txt` says 18 failures; my run of the *frozen* tests against the
baseline sources says 21. Both are RED; only mine corresponds to the committed test files.

## 6. What I could NOT verify, and why

1. **The CodeGraph index state / query results** (`findings.md` §2). The card forbids re-indexing;
   I did not run CodeGraph. The recorded gap is internally consistent but unreproduced.
2. **A real CWP-produced `du-production-reading/2` bundle.** The frozen public wire
   (`actual-090`) is `/1`; `/2` is the author's synthetic descriptor wire (validated by the real
   RF contract, but not produced by CWP). The adapter↔wire compatibility for `/2` is proven
   against the validator, not against a real CWP artifact.
3. **The declared upstream commits** `34a7dd71…` (CWP) and `2584b7ee…` (ET). I did not read the
   CWP/ET repos; the claim that nothing was extracted is consistent with the diff but not
   independently checked.
4. **External consumers of `revenue-narrative-consumption/1` and of the entry-2 result dict.**
   Within RF there is no exact-key validator; other repos (ROOT/CWP) were not inspected.
5. **The author's manual deletion of the pytest basetemp.** No receipt records it; the current
   temp state is clean only through pytest's 3-session retention.
6. **The full repository test suite.** I ran the card commands, the author's 20 modules and the
   pre-push smoke gate (416 tests), not `pytest tests/` (hundreds of modules, out of scope/time).
7. **Real company-data quality.** Explicitly out of scope; the fixture is synthetic.
8. **The author's "265 passed, 3 skipped (12 modules)" line** — I could not reconstruct that
   subset; the card's 12-module command gives 279/3.

## 7. Redundant gate / duplicated validator / compatibility break

- **Redundant/stricter gate introduced:** **yes — B1.** `layout_coverage.complete` is a
  diagnostic-only, free-form wire field, and the adapter turns a non-boolean value into
  `narrative_citation_reading_invalid`, gating both entries and `source_preparation_result`.
- **Additional binding gate (arguable):** **S1.** A legal `/1` span in two groups now requires
  the new `citation_group_id`; the baseline consumed it.
- **Duplicated validator:** **partial (N6).** The adapter re-checks the group/view/unread
  structure that `company_wiki_narrative_contracts._reading_context` already validates. It does
  not duplicate byte/identity/wire validation and is needed for entry 2's dict input, so it is
  bounded, but it is a second (narrower) validator of the same reading structure.
- **Compatibility break:** **yes, three (B1, S1, S2)** plus the additive-key nit (N9). On the
  legacy `/1` happy path, however, the entry-1 document+receipt and the entry-2 result are
  **byte-identical to the baseline** once `citation_trace` is removed (exact commands in §5, #8),
  and all old receipt keys/values and the old binding-field message ("narrative binding fields
  are invalid") are preserved.
- **Prediction values / formula refs / claims:** unchanged (compat comparison + card tests +
  E2E CLI equality). No new undeclared claim fields; nothing is written into the RF input
  document; `bind_parameter_evidence` still returns `parameter`/`claims`/`sources`/`lineage`
  (plus the additive `citation_trace`).
- **Source-role refusal:** applied consistently in both entries; it is card-justified
  ("问题span被当管理层事实") and does not wrongly block the exercised legitimate cases.
- **Entry-2 projected `/3`:** it does resolve the span's parent/pointer and then refuses with
  `source_availability_unknown` (no invented publication date) — verified by code reading,
  the passing reproduction test, and the probe. The parent lookup is too loose (S5).
- **Coverage never gates (except B1):** unread/opaque/deferred/sampling/`limited`, an incomplete
  layout expressed as a boolean, a missing `reading_context`, and an ungrouped span all still
  consume; the trace is diagnostic-labelled (`coverage_note`) and is not a permission gate.

---

Bottom line: the card's core semantic goal is met and the frozen evidence mostly holds, but B1
is a direct violation of the "coverage is diagnostic only" rule on a wire-valid input and must be
fixed; S1/S2/S5/S6 should be fixed before this is handed to ROOT. This reviewer did not modify
source, tests or the commit; the only writes were this report and one scratch probe under
`%TEMP%`.
