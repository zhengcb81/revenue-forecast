# Shared reading consumer compatibility — 2026-10-14

## Objective and ownership

RF consumes CWP source-oriented narrative bundles, including bounded shared reading context, without re-parsing originals or discarding new metadata. Isolated branch: codex/shared-reading-rf-reader-20261014, base f0d694d69a05ef3f7a449e87cd91cdb44d1ff8ce. ROOT receives changes; this lane does not commit/push. RF main assurance/runs runtime files and output remain untouched.

Owned source: scripts/company_wiki_narrative_contracts.py and necessary RF-owned narrative reader/projector. Owned test: tests/test_shared_reading_narrative_contract.py. Plan: this directory. No CWP implementation import, model/download, production configuration or original writes. No extra human authorization gate or duplicate upstream source responsibility checks.

## Phases

1. [complete] Read published schema plus actual public bundle, locate all consumer projection seams; specify exact additive DTO and compatibility.
2. [complete] TDD decisive RED: actual 0.9 body, canonical public claims/versions (unchanged), parent/scope/reference consistency and finite bounds, legacy 0.8.
3. [complete] Implement shared-reading DTO validation and preservation through RF context/projector.
4. [complete] One concentrated old-reader + new-contract/actual-body integration acceptance, static checks, unchanged-main status, handoff and SOURCE STOP.

## Next Step

SOURCE STOP. ROOT reviews the isolated diff and saved acceptance evidence, then commits/replays the public RF boundary. No further lane edits.

## Acceptance

Keep existing legacy oracle; preserve current reading_context; public claim/versions remain their exact six fields and do not broadly ignore unknown fields. Validate bounded schema and references using the already transported evidence table, not file paths or another raw-source read. Preserve incomplete-read diagnostics as data rather than pretending complete coverage. Test actual public bytes in an independent reproducible fixture without CWP source imports. Record real pytest exit and TEMP cleanup at the major acceptance node.

## Errors

Sandbox git status on RF main reported not-a-worktree; normal host read-only check succeeded with expected main WIP. No main content was changed.
