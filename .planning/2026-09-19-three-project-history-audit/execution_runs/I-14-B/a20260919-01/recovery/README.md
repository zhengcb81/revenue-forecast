# I-14-B recovery / rollback (attempt-local, no product state)

## What this card changed

Only two kinds of files exist in this attempt:

1. the subject under test `iso/natural_window.py` (attempt-local classifier), and
2. evidence / harness files under this attempt directory.

No product file was created, edited, moved or deleted. `changes.diff` is the diff
between the BEFORE revision (`before/natural_window.baseline.py`) and the AFTER
revision (`iso/natural_window.py`); it contains nothing else.

## Why a rollback cannot touch product state

The card starts no worker, no scheduler, no downloader and no background process
(the card body says "默认不启动后台"). It writes no catalog, no registry, no
receipt and no runtime policy. The only product-side reads are read-only hash and
porcelain captures.

Verified untouched (see `evidence/baseline_repos.before.json` and
`...after.json`):

- `company-wiki/.source_catalog/worker_control.json` sha256
  `9fcbe233efe76222a32316c07b9273b9c5128da3af6db27d706b1759680ac7bd`,
  `desired_state = "paused"` — **the original pause intent is unchanged and was
  never overridden by this card**;
- `company-wiki/.source_catalog/runtime_policy.json` sha256
  `a0ce50c99bee075d3f0a873dc92288b623dc4aa44d8d0180092d3b5feebb01e1`;
- production catalog `catalog.sqlite3` 49,677,344,768 B, mtime
  `2026-09-19T06:31:35Z`, `-wal` 0 B.

## How to roll this attempt back

```powershell
# 1. return the subject under test to the BEFORE revision
Copy-Item <attempt>\before\natural_window.baseline.py <attempt>\iso\natural_window.py -Force

# 2. re-run the frozen gate: it must go RED again (this is the documented RED->GREEN pair)
& <attempt>\iso\venv\Scripts\python.exe -X utf8 -B <attempt>\harness\run_cases.py `
    --sut <attempt>\iso\natural_window.py --out-dir <attempt>\recovery\rollback-check --label rollback
#    expected: runner rc 1, accepted_ineligible_count 12, mismatch_count >= 213
```

Nothing else needs undoing: there is no lock, no partially written artifact and
no half-updated registry. Re-running any command in `commands.json` is idempotent
because every command writes only inside its own evidence directory.

## Stop-the-observation rule (card: "恢复：停止本次观察，不改变worker原暂停意图")

This attempt never started an observation. Stopping therefore means: do not
launch anything, leave `worker_control.json` exactly as found (`paused`), and
keep the real 30/60/120 s login window and every natural day/week/month window
unstarted — they are recorded as `pending` / `blocked` in
`evidence/calendar_mapping.json`, not as executed.

## Failure handling actually used

- Two intermediate AFTER mismatches (C1 missed `R-FUTURE-CLOCK`; L2/L2b raised a
  spurious `R-SAME-INSTANT`) were resolved by fixing the **implementation**, not
  the oracle: per-judgement violation detection is now independent of the
  counting loop, and duplicate-instant detection looks only at `sampled_at`.
  The intermediate report was overwritten in place by the corrected re-run; the
  note is preserved at `after/cmd-CASES/FIXCYCLE.md`.
- One harness revision (adding the frozen output-shape check) happened between
  the exploratory RED `before/cmd-CASES-r0` and the evidence RED
  `before/cmd-CASES-r1`; both are kept and the ordering is declared in
  `oracle.md` section 8-errata-2. A stricter check can only add mismatches.
- No command was retried blindly after two identical failures.
