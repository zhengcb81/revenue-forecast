# RF-RATCHET-REST-A — Step 3: COMMANDS (log, disclosed)

All git usage read-only (`git log`, `git diff`, `git show`); no index/HEAD/branch/worktree
mutations. No production writes: RF sources only read; all pytest/scratch confined to
`%TEMP%` + this attempt dir.

| # | command (abbrev) | purpose | outputs |
|---|---|---|---|
| 1 | `git log --oneline -3 70dd9f6e` / `git show --stat 70dd9f6e` | identify checkpoint commit | — |
| 2 | `git log 70dd9f6e..HEAD -- <3 files>` (empty) | prove current == checkpoint content | — |
| 3 | `git show 70dd9f6e^:<path>` via `subprocess` (exact bytes, no PS encoding) | extract pre-images | `pre70dd/*.blob` |
| 4 | `git diff 70dd9f6e^ 70dd9f6e -- <calc> <template>` | strategy: what behavior did checkpoint add | ORACLE §5 |
| 5 | `python scan_ratchet.py .` | full-row RED scan, 2 implementations | `evidence/scan_red.*` |
| 6 | `python family_inventory.py .` | 55-test family inventory | `evidence/family_inventory.*` |
| 7 | `robocopy RF %TEMP%\rf-rest-a-iso2 /MIR /XD .git .planning <caches>` | iso copy (disclosed; plain file copy, **no .git metadata — not a git worktree**); first attempt incl. `.planning` was killed as too slow (job pwsh-162), lean rerun = pwsh-167 (1923 files / 26 MB / 26 s) | `%TEMP%\rf-rest-a-iso2` |
| 8 | `python -m pytest <55 family files> -q --junitxml ...` in iso (env `PYTHONDONTWRITEBYTECODE=1`, `-p no:cacheprovider`) | baseline RED-context family run | `evidence/family_before/` |
| 9 | `python -B diff_probe.py <prod scripts>` | ORIG differential probe (read-only, `-B`) | `evidence/probe_orig.json` |
| 10 | `Copy-Item pre70dd/*.blob → iso scripts` + family run | revert-strategy test (pre-images swapped **only in iso**) | `evidence/family_pre70dd/` |
| 11 | (next) swap `refactored/*` → iso; family run; probe NEW; ratchet per-row + mutations | GREEN + non-vacuity | `evidence/family_after/`, `probe_new.json`, `mutation_*` |
| 12 | (next) `changes.diff` = prod vs refactored, assert exactly 3 files | delivery | `changes.diff` |

Encoding notes (honesty): PowerShell `>`/`Set-Content -Encoding UTF8` emit UTF-16/BOM on this
host — probe outputs were normalized to UTF-8 in-place before JSON parsing; pre-image extraction
deliberately avoided PS redirection (subprocess bytes).
