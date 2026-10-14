# RF shared reading consumer handoff — ROOT received and published

## ROOT reception and publication — complete, 2026-10-14

- Published implementation commit: `512e85bbe274c357c780a78791f5784c3af66d2d` (`fix: consume bounded shared document reading context`). ROOT integrated and pushed it; local `main` and `origin/main` were read back at this exact commit.
- Normal pre-push acceptance: **416 PASS +36 subtests, 38.11s**. Exact GitHub Actions run **38563752875** succeeded for this code commit, as recorded by ROOT. These are ROOT's publication results; the source author did not run a second publication or push.
- Independent ROOT consumer review: **8 PASS, exit0, 0.412199s**; author source/test/plan SHA unchanged during review, independent TEMP restored. This verifies the bounded consumer seam, not a complete company forecast.
- Scoped installation finished: only `scripts/company_wiki_narrative_contracts.py` changed. Three skill entries resolve to **two physical copies** (`.agents` and `.codex`); `.claude/skills/revenue-forecast` is a Windows junction to `.agents/skills/revenue-forecast`. Fresh read-back SHA for all three entries equals **`ca878e4d1b5cfa254ec1db2734596eab36c7d542d49b3b28b5a95097d5cfa10a`**, 49,584 bytes. Selected and unselected installation drift are both zero. The 97-owned-file content manifest is `5db2de9da6043b9a12bf5471ad32816261b88c9936883ae7a39048adb4ed1c36`; it is computed from bytes, so no permission/manifest JSON was added.
- Author-worktree CRLF source SHA `78aa128da01e0a711699ca8b478627132344eee84ccef0af4b96ad5fe52d42bb` normalizes to the published LF SHA above. The published LF test SHA is `b688875ea6dd176ba4b76a300628bd599a48745a0068b800cd0d165672c13558` (11,481 bytes); the retained source-author CRLF test SHA remains historical evidence.
- Mother-plan scope remains open: at this RF publication snapshot, the CWP source-recall replay is **CN9/10 and US7/8**. This RF card establishes consumer compatibility and source-context preservation; it does not claim all company research, financial forecasts, source semantic quality or the mother PWF is green/complete.

## Source-author worktree and base (historical)

- Worktree: C:/Users/郑曾波/Projects/_harness_worktrees/shared-reading-completion-20261014/rf-reader
- Branch: codex/shared-reading-rf-reader-20261014
- Base: f0d694d69a05ef3f7a449e87cd91cdb44d1ff8ce
- Historical source-author delivery was uncommitted: this author did not commit/push/install. ROOT received only the owned source, test and this plan subtree and then completed the publication recorded above.

## Root cause and precise current producer contract

RF's exact bundle allowlist was frozen before the shared reader added `reading_context`. Both raw narrative-bundle/2.0 and official-json narrative-bundle/3.0 used that old exact set; their NarrativeContext projection also omitted the additive field. Thus valid public source bytes were rejected at the adapter boundary before RF could inspect the original reference closure.

Actual saved 0.9 public response: 11,549 bytes; SHA256 7d403b7e12bc3c4c094a08855190d8e422a09f88d2e465e89150d26cfb0bb2d2. `actual_schema_observation.json` records exact actual root/claim/versions fields and typed producer code points. Portable small public request/bundle/receipt fixtures under fixtures/ retain the original request hash binding. These are a real executed public protocol over the synthetic Acme input; no original, output tree, credentials or production configuration was copied.

The current canonical public claim still has six fields. `evidence_group_ids` is a model input declaration which the CWP model validator checks then removes before the typed public draft. The versions object still has its six existing fields. ROOT explicitly narrowed this delivery to that current formal producer shape. No invented `reading_dependencies`, causal-version extensions, or new public claim fields were admitted; tests retain explicit refusal of those unpublished additions.

## Implemented scope

Only scripts/company_wiki_narrative_contracts.py is modified. The new tests are tests/test_shared_reading_narrative_contract.py. No reader subprocess/runtime, RF calc/input schema, CWP implementation, source configuration, provider/model or main WIP file changed.

- Add precisely optional `reading_context` to both exact bundle shapes; all other unknown fields remain refused.
- Validate du-production-reading/1 and its known sampled/unsampled forms.
- Validate known policy/facet/group field shapes, selected evidence reference membership/uniqueness, and single-original-parent group scope using the already transported span table.
- Preserve native text, structure and fine-layout completeness and full counts/sample limits independently; incomplete diagnostics remain data, not a new approval gate.
- Finite transport ceilings: 192KiB context, depth12/30,000 nodes,16,384-character strings,256-field objects/4,096-array entries; policies128/facets16/groups512/constraints32. No producer original reread, policy lookup, alias validation, permission receipt or fee-budget changes.
- Preserve the validated context unchanged in raw and official NarrativeContext DTOs. Existing CLI `.to_dict()` consequently retains it; subprocess and CLI projection are covered. Legacy 0.8 wire retains its old DTO shape.

Historical source-author worktree SHA256 (CRLF bytes, not the published LF files):

- scripts/company_wiki_narrative_contracts.py:78aa128da01e0a711699ca8b478627132344eee84ccef0af4b96ad5fe52d42bb
- tests/test_shared_reading_narrative_contract.py:901d91fc0ba0dbb7ef4cb691455ea156f668eebf4c606f17c4f3eb216d131d98

## Evidence / repeat

TDD RED: red.log,13 FAIL/23 PASS,exit1. First new-source GREEN:green.log,36 PASS/0.50s,exit0. No assertions were loosened.

Concentrated major-node command (normal host, independent standard TEMP; acceptance.json contains exact argv, child exit and cleanup):

```powershell
python -X utf8 -m pytest -q tests/test_company_wiki_narrative_reader.py tests/test_w04_public_consumer.py tests/test_narrative_container_lineage.py tests/test_company_wiki_narrative_process.py tests/test_narrative_source_preparation_transport.py tests/test_shared_reading_narrative_contract.py --basetemp <independent-owned-TEMP>
```

acceptance.log/json:153 PASS,2 existing POSIX-on-Windows SKIP,15.80s; actual pytest exit0; owned TEMP restored. New coverage includes actual 0.9 bytes, actual 0.8, real bounded reader subprocess, CLI projection, projected originals, cross-parent mutation, finite context bounds, unknown fields, missing/duplicate refs, false count/limited combinations, and detached output copies.

Ruff on changed source/new test, host-assumption guard on the new test, and git diff --check all pass. Direct additional mypy of this script is not part of its existing CI/pre-commit target; both exact base and current code have the same nine historical Optional-narrowing errors. baseline-mypy.log/current-mypy.log preserve this comparison. No type-check configuration or tests were weakened, and no new error was introduced. Initial test-format lint errors were fixed; baseline mypy -c exceeded Windows command-line length, so the baseline was checked in an owned normal TEMP which was cleaned.

Final RF main read-only status remains the three pre-existing assurance/runs/{daily_alert.jsonl,weekly_alert.jsonl,weekly_manifest.json} modifications and untracked output/. Main source and those runtime files were not written by this lane.

## ROOT handoff / remaining scope

ROOT has completed code reception, push, exact CI and the scoped installation. The only next receipt is this documentation-only handoff; this actor does not fast-forward main or push. Keep the original author evidence and unrelated RF assurance/output WIP. No repeated paid/source producer run or new permission is required to close this RF consumer card. The portable new test has no developer absolute paths or CWP imports.

This proves current consumer interoperability and finite source context preservation. It does not certify company research quality or a future unpublished DTO, and it does not rerun the original paid/source producer. Future formal schema changes should have explicit new fixtures/version coverage rather than broad unknown-field omission.
