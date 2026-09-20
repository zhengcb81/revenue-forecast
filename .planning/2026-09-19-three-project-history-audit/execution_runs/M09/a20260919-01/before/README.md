# M09 before/after capture policy

This card modifies nothing, so `before/` and `after/` are the same capture point, taken after the card runs.
That is stated plainly here rather than dressed up as a pre-run capture.

What makes the read-only claim checkable anyway:

1. `before/git_status_revenue-forecast.txt` and `after/git_status_revenue-forecast.txt` are raw
   `git --no-optional-locks status --porcelain` output; the `*_filtered.txt` variants drop this batch's own
   new files. The filtered before/after views are identical.
2. `before/production_file_mtimes.txt` records the production file hashes and the mtime ordering
   (`iso/checkout_scripts/model_registry.py` was created before `evidence/M09/stdout.txt`), which anchors
   the production content to the pre-run moment even though the capture itself is later.
3. `after/console_A2-M09-isolated-snapshot_M09.txt` is the A2 console written **before** the product
   run; it already contains `MATCH production=<sha256> isolated=<sha256>`.
4. `before/reviews_mtime.txt` records the read-only audit anchor
   `reviews/second_wave/final_review_checks.json` (mtime `2026-09-19 10:05:32`), which this attempt never
   writes.

## Production mtime finding (recorded, not hidden)

An external writer rewrote production source files at `2026-09-20 03:41:57` with byte-identical content
(the same sha256 as the task anchors and as the frozen isolated copies). See
`evidence/M09/integrity.json` -> `production_working_tree_mtime_finding` for the file list and hashes.
This attempt issues no write command against any production path; the affected mtimes therefore cannot be
attributed to it, but mtime alone is not usable as an untouched-proof for this window - the sha256 evidence
is.
