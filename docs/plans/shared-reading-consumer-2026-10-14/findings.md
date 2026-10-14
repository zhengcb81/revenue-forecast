# Findings

## Initial investigation (historical; speculative extensions superseded)

RF HEAD f0d694d6 has only the three pre-existing assurance/runs changes and untracked output. Independent sparse worktree excludes assurance/output/raw. No applicable root RF AGENTS.md was found in the checkout.

Actual saved public CWP response is refused with invalid_narrative_bundle because reading_context is absent from RF BUNDLE_FIELDS. Further seams already visible: strict summary claim field set excludes evidence_group_ids; versions allows only six legacy strings; NarrativeContext projection omits shared reading context and dependency identity. This is coordinated additive contract drift, not a reason to relax unknown-field validation globally.

## Formal current scope

The initial claim/group/versions/dependency extension hypothesis above was superseded by actual producer bytes: only optional `reading_context` is publicly additive. The six-field public claim/version allowlists are correct; they are not missing extensions.

Actual 0.9 public body is 11,549 bytes, SHA7d403b7e12bc3c4c094a08855190d8e422a09f88d2e465e89150d26cfb0bb2d2. Root bundle has reading_context optional, claim has exactly six canonical fields, versions exactly six historical fields. Producer model validates and removes evidence_group_ids before public typed draft; reading_dependencies is not in this current bundle contract. ROOT explicitly narrowed this lane to present public shape. No guessed future fields added.
The saved 0.9 body, official projection compatibility, reader subprocess, CLI projection, resource/type/reference mutations and real 0.8 preserved-shape tests pass:36 PASS/0.50s exit0 after decisive RED13FAIL/23PASS exit1. Initial ruff test-format errors were corrected without oracle changes. Manual mypy of this non-CI-target script shows nine existing errors; compare baseline/current logs before claiming a new regression. Windows mypy -c baseline exceeded command-line length; switched to owned TemporaryDirectory baseline source, cleaned afterwards.

## ROOT reception and publication — complete, 2026-10-14

- Code commit `512e85bbe274c357c780a78791f5784c3af66d2d` is on `main` and `origin/main`. ROOT's normal pre-push:416 PASS +36 subtests/38.11s; exact code CI run38563752875:success. Independent consumer review:8 PASS/exit0/0.412199s.
- Only the narrative contract script was installed, to two physical copies (`.agents`, `.codex`); `.claude` is a junction to `.agents`. Three-entry read-back LF SHA `ca878e4d1b5cfa254ec1db2734596eab36c7d542d49b3b28b5a95097d5cfa10a`; selected/unselected drift0. Full published LF/test hashes, CRLF author history and the dynamic owned manifest are recorded in [handoff.md](handoff.md).
- At this RF publication snapshot, the mother CWP source-recall node remains **CN9/10 and US7/8**. This card proves consumer compatibility/source-context preservation; it does not certify all forecasts, source semantics or complete the mother PWF.
