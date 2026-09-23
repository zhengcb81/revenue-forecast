# E2E-EXPAND a20260923-01 — recovery (how to remove everything this run created)

Deletion is safe at any time except: keep `<ATT>` (this attempt directory) until the
independent review is done — it holds the only copy of the evidence the reviewer needs.

## 1. Kept on purpose (the deliverable — do NOT delete unless the card is rejected)

- `revenue-forecast/e2e/run_cross_repo_chain_e2e.py` (new, sha `88ac9e4a…`)
- `revenue-forecast/tests/test_cross_repo_chain_e2e.py` (new, sha `3e2b39ee…`)
- `revenue-forecast/tests/contract/host_assumption_allowlist.json` (edited: +11
  registered content-hash pins; the 3 pre-existing entries untouched). **Revert only
  if the two files above are rejected** — restore the original 3-entry text committed
  verbatim as the difflib `-` side of `changes.diff` (sha `bc6da8ff…`, 1 215 B).

## 2. Attempt-local artifacts (delete after review acceptance)

- `<ATT>/iso/venv/` — the per-attempt iso venv (copy of the I-07-B template + the
  playwright-stack file copies from Miniconda; ~30 MB):
  `Remove-Item -LiteralPath "<ATT>\iso" -Recurse -Force`
- `<ATT>/evidence/`, `oracle.md`, `binding.json`, `commands.json`, `decision.md`,
  `changes.diff`, `handoff.json`, `recovery/` — the attempt record itself; delete the
  whole directory only after review sign-off:
  `Remove-Item -LiteralPath "<ATT>" -Recurse -Force`

## 3. Temp/isolation residue (already verified gone by the suite; listed for completeness)

- `%TEMP%\rf_e2e_expand_a20260923-01` — S1's temp wiki + S2's isolated lake; the
  suite's S4 asserts this whole work root **absent** after every run (summary:
  `s4.temp_storage_absent=true` in all five S4 executions). If a run was ever
  hard-killed mid-flight, remove leftovers manually:
  `Remove-Item -LiteralPath "$env:TEMP\rf_e2e_expand_a20260923-01" -Recurse -Force -ErrorAction SilentlyContinue`
- pytest temp trees from this attempt (`%TEMP%\pytest-of-*\pytest-66*`): hold nested
  runner work roots — already fully copied into `<ATT>/evidence/` where needed
  (`run_live_pytest/`, `accidental_auto_gate_run/`, `run_pytest_offline_nested/`).
  Safe to drop wholesale (they are pytest's own disposable dirs):
  `Get-ChildItem "$env:TEMP" -Directory -Filter "pytest-of-*" | Remove-Item -Recurse -Force`
  (pytest also garbage-collects old ones itself, retention=30.)
- Downloaded test files: **already deleted by the suite with recorded proof** —
  `evidence/run_live_pytest/s1/deletion_proof.json` and
  `evidence/accidental_auto_gate_run/s1/deletion_proof.json` each list the two deleted
  files (PDF + sidecar) with pre-delete sha256 and `post_absent=true`. Nothing to
  remove again.

## 4. Python cache residue

- All judged runs used `-B` / `PYTHONDONTWRITEBYTECODE=1` (no bytecode written by the
  suite). The one verification step that DOES write caches is the CI-mirror command
  `python -m compileall -q scripts tests tools e2e` (commands.json GATE-03 step),
  which refreshed `__pycache__/` under those trees. Regenerable, safe to clear:
  `Get-ChildItem -LiteralPath <RF> -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force`
  (in particular `tests/__pycache__/test_cross_repo_chain_e2e*.pyc` for the new file).
- `.pytest_cache` was NEVER touched by this attempt: every pytest invocation passed
  `-p no:cacheprovider`.
- `e2e/.runs/` was never touched: every runner invocation passed an explicit
  `--evidence-dir` inside `<ATT>` (the default `e2e/.runs/cross_repo_chain/<stamp>`
  path is only used when a future operator runs the runner with no flags — if that
  ever happens: `Remove-Item <RF>\e2e\.runs\cross_repo_chain -Recurse -Force`).

## 5. Production state (nothing to restore — verified unchanged, twice)

- Production catalog `company-wiki/.source_catalog/catalog.sqlite3(-wal,-shm)`: never
  opened by this attempt (stat-only); size+mtime identical before/after every runner
  run AND across the protocol snapshots (`DIFF_KEYS: []`).
- CW real data (`companies/宁德时代/...` raw+sidecar, `security_master/*.json`):
  hashes identical pre/post (READ-only copies into temp).
- FF real config/storage roots: listing diffs `{}` pre/post.
- Git: no git command was ever run — no index/worktree state to restore.
