# I-08-A production-repo delta analysis (read-only capture)

`git_status_before.txt` / `git_status_after.txt` each contain, in order:

1. a raw capture `git -C <repo> status --porcelain 2>&1` (stdout **and** stderr, so the six git "could not open directory ... Permission denied" warnings appear inline);
2. a clean view `git -C <repo> status --porcelain 2>$null` (stdout only).

**Integrity caveat (stated, not hidden):** the clean view was appended to both files *after* the run, so the "before" clean block is a synchronously-recorded copy of the same moment, not a second pre-run capture. Only the **raw** blocks are true before/after captures. The raw block is therefore the authoritative before/after evidence.

## Raw block comparison

| repo | before raw lines | after raw lines | delta |
|---|---:|---:|---|
| revenue-forecast | 58 (6 warnings + 52 entries) | 59 (6 warnings + 53 entries) | **+1 entry** |
| filing-fetch | 1 | 1 | 0 |
| company-wiki | 2 | 2 | 0 |

The single added entry is:

```
?? .planning/2026-09-19-three-project-history-audit/execution_runs/I-14-C/
```

## Attribution of that delta

`I-14-C` is **not** an I-08-A path. I-08-A owns only
`.planning/2026-09-19-three-project-history-audit/execution_runs/I-08-A/`, which was already present as an
untracked entry in the *before* capture. The `I-14-C` directory appeared during the I-08-A run window and is
attributable to concurrent plan activity in this workspace (git reports an untracked directory as one porcelain
entry, so one new directory = one new line).

Evidence that I-08-A did not create it:

* the I-08-A write allowlist is `<attempt>/iso/**`, `<attempt>/before/**`, `<attempt>/after/**` and the attempt's own
  top-level deliverables (`binding.json`, `oracle.md`, `decision.md`, `commands.json`, `review.md`, `handoff.json`,
  `run_c3.py`, `run_c3.cmd`) — see `binding.json.allowed_write_roots`;
* no command in `commands.json` writes outside those roots; the only writes the probe performs are under
  `<attempt>/iso/scratch/**` plus the isolated scratch registries;
* no I-08-A path is named `I-14-C` anywhere in this attempt.

## No modified-file delta in any repo

Besides that one untracked directory, the set of ` M ` entries and the set of `?? ` entries is identical between
the two raw captures: the same 30 modified paths in revenue-forecast, the same 1 in filing-fetch and the same 2 in
company-wiki. In particular **no file under `scripts/`, `config/`, `artifacts/registry/`, `tests/` or
`.planning/.../reviews/` changed during this attempt**, and nothing was staged, committed, restored or stashed.

## Reviewer action

When re-running the comparison, expect the untracked-entry list to keep growing for reasons unrelated to I-08-A
(other cards in this plan create their own attempt directories). Compare the **` M ` (modified) sets** and the
per-repo `scripts/` subtree, not the raw line count.
