# Task Plan: G5-RF-INSTALL — selective installation sync & failure recovery

## Goal

Extend `tools/sync_installations.py` with an explicit, repeatable `--file` scope,
a zero-write `--plan` JSON, and a `--json` result so that only the named
installable files are checked/applied, with accurate partial-failure reporting
and idempotent re-runs — without changing G3's runtime closure, JSON contracts,
forecast/source rules, or the three real home installations.

## Next Step

Commit the PWF handoff package (implementation commit
`a2116ca6d5280c140b42a0d8bd2d94521ee80ccd` already made), then push
`codex/g5-rf-install` if the pre-push gate can run.

## Current Phase

Phase 5

## Phases

### Phase 1: Freeze, PWF, required reading

- [x] Original repo status captured (only 3 owner logs modified), baseline
      `ab7a7a4434bbb4c52a5bd2a6cd6ed710d7151eee` confirmed as HEAD.
- [x] Worktree `C:/Users/郑曾波/Projects/_g5/rf` created on `codex/g5-rf-install`.
- [x] `.planning/g5-rf-install/` three PWF files created; resolver binds on
      `PLAN_ID=g5-rf-install` + `PWF_PLAN_ROOT=<worktree>`.
- [x] Read: card, `tools/sync_installations.py`, both G3 test files,
      G3 `MAIN_ACCEPTANCE.md`, `SKILL.md` installation section, `g5_handoff.schema.json`.
- **Status:** complete

### Phase 2: Real investigation (read-only) & scope

- [x] Zero-write `installation_diff` run against the three home roots.
- [x] Drift measured and line-ending provenance separated from content drift.
- [x] Write set frozen: `tools/sync_installations.py`,
      `tools/tests/test_sync_installations.py`,
      `tools/tests/test_g5_selective_install.py`, own PWF only.
- **Status:** complete

### Phase 3: RED → minimal extension

- [x] RED tests written first (CLI `--file` unsupported; identical-bytes mtime
      rewritten; no partial report on a failed copy/replace).
- [x] Existing-GREEN item recorded separately (temp residue already cleaned by
      the old `finally` + `TemporaryDirectory`).
- [x] Minimal extension of the existing tool (no second installer).
- **Status:** complete

### Phase 4: Centralized test node & static checks

- [x] `python -B -m pytest -q -p no:cacheprovider --basetemp=.planning/test-tmp/g5-install`
      over the three G5 responsibility files → **33 passed / exit 0 / 17.13 s / 0 skipped**.
- [x] Related counter-examples: `tests/test_zr804_platform_shape.py` installed-copy
      identity (3 passed) and `tests/test_fc1004_platform.py` install-sync gate (1 passed).
- [x] `ruff check` exit 0; `host_assumption_guard` exit 0 with **0 new** violations;
      pre-commit hook passed.
- [x] Owner-log SHA-256 before/after identical; home installs read-only.
- **Status:** complete

### Phase 5: Handoff package

- [x] `.planning/g5-rf-install/{HANDOFF.md,handoff.json,main_wiring.md,install_delta.json}` written.
- [x] `handoff.json` validated against the read-only `g5_handoff.schema.json`.
- [x] Cleanup of `.planning/test-tmp/g5-install` scratch (restored `absent`, together
      with its parent, after the run).
- [ ] Commit on `codex/g5-rf-install`.
- **Status:** in_progress

## Key Questions

1. Observed live drift is not the card's 8 files — must be reported as fact
   without widening the live update list. (Answered: 8 is reproduced only when
   the canonical is the *original repo* working tree; see findings.md.)
2. `--plan` exit code: 0 whenever a plan is produced (machine fact, like the
   existing `--print-manifest`), non-zero (2) only on validation errors.

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Keep every existing public function signature | Card §4.1 "keep old positional args working"; G3 `test_old_public_callers_keep_their_signatures` locks it |
| `--plan` added to the existing mutually-exclusive mode group | Gives usage rejection (exit 2) before any write for free |
| Scope validated against `installable_files(canonical)` first, then all destinations planned read-only, then any write | Card §4.2 "all scope validated first; error ⇒ zero writes at every destination" |
| Apply re-reads source and target SHA immediately before each `os.replace` | Card §4.5 byte-level concurrency correctness, never overwriting from a stale plan |
| Directory obstruction as the controlled failure injection | `os.replace(file → directory)` fails on Windows *and* Linux; a read-only file only fails on Windows (host-assumption gate) |
| Only files whose bytes differ are staged/replaced | Card §4.5 + RED: repeated sync must not move identical bytes' mtime |
| `--file`/`--json` rejected with `--import-from`/`--print-manifest` via `parser.error` | Card §4.1 error parameters rejected before any write |

## Errors Encountered

| Error | Attempt | Resolution |
|-------|---------|------------|
| Live drift measured 12 files/root instead of the card's 8 | 1 | Traced to canonical byte state (working-tree line endings), not content; see findings.md — reported as fact, live update list not widened |
| `os.replace` onto a read-only file is a Windows-only failure | 1 | Switched controlled injection to a directory obstruction (portable) |
| `FileNotFoundError [WinError 3]` for 72 files on a fresh destination | 1 | `_stage_and_replace` had dropped the original `final.parent.mkdir(parents=True, exist_ok=True)`; restored it |
| Link-escape test passed for the wrong reason (`references/references.txt` is not in the synthetic closure) | 1 | Corrected to `references/references.py` and asserted the `escapes the installation target` message plus the absence of the out-of-closure message |
| `_snapshot` via `Path.rglob` would descend through a directory link | 1 | Rewrote it as an explicit `os.scandir` walk that records links/junctions instead of following them |
| RED re-run at the base commit via pytest hit `ImportError` on the new API names (collection error, exit 4) | 1 | Ran a base-compatible behavioural probe instead, restoring `tools/sync_installations.py` from `git show HEAD:` for the duration and restoring the implementation byte-for-byte afterwards |
| `pytest <dir> ::test` argument shape rejected (exit 4) | 1 | Use `<file>::<test>` selectors |
| A single long bash heredoc truncated the appended test content | 1 | Reverted to the last good line and appended the remaining tests in bounded `edit` chunks |

## Notes

- `~/.claude/skills/revenue-forecast` is a symlink to `~/.agents/skills/revenue-forecast`;
  `unique_destinations` already collapses it, so "three roots" = two physical trees.
- No authorization/binding/approval/expiry file is introduced anywhere.
