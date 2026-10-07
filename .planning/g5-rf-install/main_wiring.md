# main_wiring — G5-RF-INSTALL

What MAIN does with this branch after merge. Nothing here has been executed by
this lane: the three real home installations were only read (stat / SHA-256 /
file names).

## 1. Where to run the apply from — read this first

The card's figure of **8 drifted files per root** reproduces **only** when the
canonical is the original repository working tree:

```
python tools/sync_installations.py --canonical C:/Users/郑曾波/Projects/revenue-forecast
→ DIFF C:/Users/郑曾波/.agents/skills: 8 files
→ DIFF C:/Users/郑曾波/.codex/skills: 8 files      (exactly the card's list)
```

Run from a **fresh checkout of the same commit** (any new worktree, any CI
clone) and the same read-only check reports **12**; compare against the raw git
blob and it reports **13**. The extra files are identical content with a
different line-ending byte state, not new content drift:

| canonical bytes | drift per physical root |
|---|---|
| original repository working tree | **8** — the card list, `unselected_drift = 0` |
| this G5 worktree / any fresh checkout | **12** |
| `git show ab7a7a44:<path>` | **13** |
| real content drift (all three agree) | **6** |

Do **not** widen the live update list to 12 or 13. The per-file evidence for the
card's 8 × 3 scope is in `install_delta.json`.

## 2. Three configured roots, two physical trees

`~/.claude/skills/revenue-forecast` is a **symlink** to
`~/.agents/skills/revenue-forecast`. `unique_destinations` collapses it, so a
default run reports two targets, not three. The `.claude` surface is updated by
the `.agents` write; no third write is needed and none is missing.

## 3. Exact commands (all from the original repository, after merge)

```bash
# 1. read-only pre-flight — expect "DIFF ...: 8 files" twice
python -B tools/sync_installations.py

# 2. zero-write plan — expect selected_drift=8, unselected_drift=0 per target,
#    exit 0, one rf-install-plan/1 value on stdout
python -B tools/sync_installations.py \
  --file .gitignore --file SKILL.md --file agents/openai.yaml \
  --file references/extended-models.md --file references/input-construction.md \
  --file references/model-library.md --file references/schema-migration-3.6-to-3.7.md \
  --file scripts/revenue_forecast.py \
  --plan

# 3. the 24-candidate selective apply — writes only those 8 files per root,
#    exit 0, one rf-install-result/1 value on stdout
python -B tools/sync_installations.py \
  --file .gitignore --file SKILL.md --file agents/openai.yaml \
  --file references/extended-models.md --file references/input-construction.md \
  --file references/model-library.md --file references/schema-migration-3.6-to-3.7.md \
  --file scripts/revenue_forecast.py \
  --apply --json

# 4. verify — expect "MATCH ...: 8 selected files" and exit 0;
#    an unselected residual prints a NOTE line but cannot fail the run
python -B tools/sync_installations.py \
  --file .gitignore --file SKILL.md --file agents/openai.yaml \
  --file references/extended-models.md --file references/input-construction.md \
  --file references/model-library.md --file references/schema-migration-3.6-to-3.7.md \
  --file scripts/revenue_forecast.py

# 5. whole-runtime confirmation — expect "MATCH ...: 75 files" twice, exit 0
python -B tools/sync_installations.py
```

A `partial` result (exit 1, non-empty `failed`) means the batch did not
complete: it names exactly which files were written, which were not, and which
conflicted. Re-running the same command against the *current* differences
converges on the remainder — files already written are not touched again. There
is no rollback and no second transaction store, by design.

## 4. Installed entry points

After the apply, from each physical installation root, with `PYTHONPATH` and
`PYTHONHOME` unset and `cwd` inside the installation:

```bash
python -B scripts/revenue_forecast.py --help
python -B scripts/revenue_forecast.py --version   # revenue-forecast 4.1.0 manifest_sha256=76b37ec851b558eb
```

Both were proven against three tmp installation roots in
`tools/tests/test_g5_selective_install.py::test_e2e_three_tmp_roots_plan_apply_idempotence_and_recovery`.

## 5. Tests that touch installations (already safe)

| path | action | reason |
|---|---|---|
| `tests/test_zr804_platform_shape.py::test_installed_copy_executes_with_canonical_identity` | verify | runs the real `--apply` against **three `tmp_path` destinations**, never home. Ran here: 3 passed. |
| `tests/test_fc1004_platform.py::test_install_sync_gate_detects_drift` | verify | runs `--apply` against two `tmp_path` destinations. Ran here: 1 passed. |
| `tools/tests/test_sync_installations.py` | no_change | untouched by this lane |
| `tools/tests/test_g3_skill_package.py` | no_change | untouched by this lane |
| `.githooks/pre-commit` / `.pre-commit-config.yaml` | no_change | ruff + host-assumption-guard both green on the new code; nothing removed to go green |
| `.githooks/pre-push` / `tools/pre_push_gate.py` | no_change | if a sibling repository is missing, point it at the existing `FF_V2_CODE_ROOT` / `CWP_V2_CODE_ROOT` explicit committed read-only entry instead of bypassing the gate |
| `scripts/revenue_forecast.py` `--version` `_root_directories` | no_change | already `{"agents","config","references","scripts"}` at the base commit; `manifest_sha256=76b37ec851b558eb` measured here |
| `assurance/runs/{daily_alert,weekly_alert}.jsonl`, `weekly_manifest.json` | no_change | SHA-256 identical before and after this lane |

## 6. What this lane deliberately did **not** do

- No `--apply` against `~/.agents`, `~/.claude` or `~/.codex`.
- No home file was created, replaced, renamed or deleted; the only home reads
  were stat / SHA-256 / file names.
- No authorization, binding, approval or expiry file exists anywhere in this
  package. `--plan` output is machine fact, never a receipt or an eligibility
  gate, and a plan file is never required before `--apply`.
- No forecast, no paid/live call, no production data path was exercised.
- `tools/sync_installations.py` is not in the runtime manifest and nothing
  under `tools/` or `tools/tests/` is copied into a user skill installation.
