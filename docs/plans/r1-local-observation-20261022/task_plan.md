# RF local preparation observation compatibility

## Scope and interface

Base 674d08d92fe2ec64e1d42a3ebab0b364e0ac4354, branch codex/r1-local-budget-observation. Only this worktree owns RF consumer code/tests and this plan. ROOT owns CWP and integration; FF producer is frozen at 6dbb9e84d8389f4d4f2d8305c788b59e4f91d2bd. Mother RF assurance/output WIP is recorded in mother-baseline.json and must remain byte-identical.

RF must transparently preserve the optional nine-field filing-local-preparation-observation/1 object inside a complete safe FF v2 failure, including machine diagnostics/owner operations, null local_io_usage, real exit/cause/retry. This field never participates in acquisition, budget, source identity or period decisions. No FF internal import, source scan, download, API, install or main mutation.

## Steps (one final independent review owned by ROOT)

1. Freeze producer fixture and RED tests: small and >64 KiB actual RF client/source_preparation subprocesses; malformed, path/body, depth and cap controls; legacy behavior and safe cause survival.
2. Implement outer wire validation plus bounded generic machine JSON by reusing RF JSON/pathless primitives. Preserve legacy base 16 KiB and small stderr 64 KiB; only validated versioned observation may use compact 128 KiB plus 16 KiB base and hard 1 MiB raw parse allowance. Reject incomplete/unsafe/oversize payload, never truncate.
3. GREEN same tests, affected existing suites, existing public mypy set and ruff; add one test file to current smoke selection without a new gate. Record actual serialized byte sizes and transparent copies.
4. Normal hooks/commit, freeze source hashes, cleanup only owned test scratch, verify mother WIP unchanged, handoff to ROOT for independent review and consumer-first release. Do not push/merge/install.

## Acceptance

Valid owner observation survives FF stdout -> RF client stderr -> source_preparation stderr unchanged, including >64 KiB. Malformed optional objects never masquerade as complete sidecars; safe small failure cause remains. Above legacy raw cap only bounded, fully validated objects pass. Legacy no-sibling failures and normal GAP remain unchanged. Unknown machine codes remain opaque. No owner business enums or budget arithmetic is duplicated.
