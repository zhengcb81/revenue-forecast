# Progress Log — G5-RF-INSTALL

## Session 1 (2026-10-07)

### Freeze & setup

- Original repo `C:/Users/郑曾波/Projects/revenue-forecast` HEAD =
  `ab7a7a4434bbb4c52a5bd2a6cd6ed710d7151eee`, status clean except the three
  owner logs.
- Worktree created: `C:/Users/郑曾波/Projects/_g5/rf`, branch `codex/g5-rf-install`.
- `.planning/g5-rf-install/{task_plan,findings,progress}.md` created from the
  PWF templates; resolver binds on `PLAN_ID=g5-rf-install` +
  `PWF_PLAN_ROOT=<worktree>`.

### Required reading done

`tools/sync_installations.py`, `tools/tests/test_sync_installations.py`,
`tools/tests/test_g3_skill_package.py`, G3 `MAIN_ACCEPTANCE.md`,
G3 `handoff.json`, `SKILL.md` installation section, `g5_handoff.schema.json`,
`.pre-commit-config.yaml`, `tools/host_assumption_guard.py`,
`scripts/revenue_forecast.py` `--version` block.

### Investigation (read-only, zero writes)

Owner-log SHA-256 before:

```
c3f88f63e12c143d6d722904fef7f29cd5d6c5751782d9b0fbd54ea9db11687d  assurance/runs/daily_alert.jsonl
108d0b14387dc50a7c0437cbe8f029d2e442dd6ed9c7bde7aea19e2113ae8ce0  assurance/runs/weekly_alert.jsonl
6562b768adf760fde2e0918344f9d15ccc51978dfe3ff4817c7eecd66d86d7ef  assurance/runs/weekly_manifest.json
```

- `~/.claude/skills/revenue-forecast` is a symlink →
  `~/.agents/skills/revenue-forecast`, so three configured roots = two physical
  trees (`unique_destinations` already collapses it).
- Full-runtime drift per physical root, measured three ways:
  | canonical | drift |
  |---|---|
  | original repo working tree | **8** (exactly the card list) |
  | this G5 worktree (fresh checkout of the same commit) | **12** |
  | git blob at `ab7a7a44` | **13** |
  The delta is working-tree line endings, not content; real content drift is
  the same 6 files under every canonical. Recorded in `findings.md` and
  `install_delta.json`; the live update list was **not** widened.

### RED (before any production change)

Behavioural probe run with `tools/sync_installations.py` restored from
`git show HEAD:tools/sync_installations.py`:

```
FAIL | RED1 cli --file two-file selection | returncode=2 ... error: unrecognized arguments: --file scripts/scripts.py --file SKILL.md
FAIL | RED2 repeat sync leaves identical bytes untouched | SKILL.md mtime_ns 1791401759673495700 -> 1791406759673495800
FAIL | RED3 controlled failure reports rf-install-result/1 | returncode=2 stdout='' payload=<JSONDecodeError>
PASS | GREEN temp hygiene already correct | raised=True residue=[]
SUMMARY 1 / 4
```

An earlier direct pytest RED run of the same three behaviours (with the
base-compatible import set, before any production line changed) reported
`3 failed, 1 passed in 1.89s` with the same three failures and the same
existing-GREEN temp-hygiene pass.

### Implementation

`tools/sync_installations.py` extended in place; `tools/tests/test_sync_installations.py`
and `tools/tests/test_g3_skill_package.py` untouched.

- `ScopeError`, `resolve_file_scope`, `plan_target`, `build_plan`,
  `apply_target`, `check_target`, `build_result`, `PLAN_SCHEMA`,
  `RESULT_SCHEMA`, `_target_file`, `_stage_and_replace`.
- `sync_installation` keeps its signature and now routes through the selective
  writer, re-raising `OSError` when anything failed.
- CLI gains `--file` (repeatable), `--plan`, `--json`; `--plan` sits in the
  existing mutually-exclusive mode group; `--file`/`--json` are rejected with
  `--import-from`/`--print-manifest` before any write.
- Default check / `--print-manifest` / `--apply` / `--import-from` output and
  exit codes unchanged.

### Validation

Centralized node (scratch root `.planning/test-tmp/g5-install`, which was
absent beforehand and restored to absent afterwards):

```
python -B -m pytest -q -p no:cacheprovider --basetemp=.planning/test-tmp/g5-install \
  tools/tests/test_sync_installations.py tools/tests/test_g3_skill_package.py tools/tests/test_g5_selective_install.py
```
→ **33 passed / exit 0 / 18.81 s / 0 skipped**

| node | command | exit | elapsed | result |
|---|---|---|---|---|
| related: installed-copy identity | `pytest -q tests/test_zr804_platform_shape.py::test_installed_copy_executes_with_canonical_identity` | 0 | 10.99 s | 3 passed (pre-existing GBK warnings) |
| related: install-sync gate | `pytest -q tests/test_fc1004_platform.py::test_install_sync_gate_detects_drift` | 0 | 7.13 s | 1 passed (pre-existing GBK warnings) |
| ruff | `ruff check` on the four owned/adjacent Python files | 0 | 0.05 s | All checks passed |
| host-assumption guard | `python tools/host_assumption_guard.py --roots tests tools scripts e2e` | 0 | 1.33 s | 39 violations, **0 new** (baseline 16, registered 18) |

Live read-only runs (no writes anywhere):

- `--plan` with the card's 8 files against the three home roots from this
  worktree → exit 0, `selected_drift=6`, `unselected_drift=6` per physical root.
- the same `--plan` with `--canonical` = the original repository → exit 0,
  `selected_drift=8`, `unselected_drift=0` per physical root — the card figure.
- default check with the original-repo canonical → `DIFF …: 8 files` per root.

Owner-log SHA-256 after: identical to the "before" block above.

### Not done (by design)

- No real home installation was written. `tests/test_zr804_platform_shape.py`
  and `tests/test_fc1004_platform.py` both target `tmp_path`, so they were safe
  to run; no other test touching home was executed.
- No full unified-completion suite, no paid/live calls, no coverage/CI gate
  change, no `--no-verify`.

## Next Step

Write `HANDOFF.md`, `handoff.json`, `main_wiring.md` against the implementation
commit, then commit the PWF handoff package and push the codex branch.
