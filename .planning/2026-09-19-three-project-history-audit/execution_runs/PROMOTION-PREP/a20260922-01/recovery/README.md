# recovery/README.md — PROMOTION-PREP a20260922-01

This attempt wrote ONLY inside `<PLAN>\execution_runs\PROMOTION-PREP\a20260922-01\`.
No production, sibling-repo, git-index, or other-card attempt files were touched, so
nothing needs restoring.

## Files (all reproducible by re-running the commands in ../commands.json)
- `oracle.md` — freeze written on call 1 (source-of-truth rules).
- `handoff.json` — skeleton (status=review_pending, implementer_signed=false).
- `promotion_batch_manifest.md` — the deliverable: 6 rows B-1..B-6.
- `binding.json`, `decision.md`, `commands.json`, this file.

## Recovery steps
1. If the manifest is lost: re-run commands.json C4–C5 (carriers are read-only sources;
   hashes are re-measurable) and rebuild the table — never restore hashes from memory.
2. Known UNRESOLVED cells to re-probe on recovery: B-6b production `natural_window.py`
   path (probe RF `scripts/` + CW `src/` recursively); all `git apply --check` rows
   (perform only on %TEMP% copies, per oracle rules).
3. No pre-existing state was modified; no superseded versions exist to roll back.
