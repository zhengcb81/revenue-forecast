# I-14-D recovery

The fix is a single-file, pure-function change (no persistence, no migration, no
crash-restart surface), so recovery is a byte-exact revert:

1. `harness/apply_i14d_narrow.py --op reverse --tree <tree>` restores the redactor
   pre-image (verified: `recovery/recovery-tree/src/company_wiki/source_catalog/observability.py`
   sha256 `c5608c4b45a55cce03df9988561e1a3ad1cab0970c51e8b3af630239fe9de35c` ==
   `iso/product_base` == I-14-C r5-final; `RECOVERY_BYTE_IDENTICAL: True`).
2. Equivalently, `git apply -R changes.diff` in a scratch repo reproduces the base
   tree (forward direction proven by `after/git_apply_verification.json`,
   GIT_APPLY_REPRODUCES true; the reverse direction is proven by (1)).
3. `iso/product_base` was never edited and is kept as the pristine pre-image;
   `iso/product_mut_*` are mutation specimens, not part of any recovery path.

Crash/restart evidence: NA — `redact_text`/`redact_and_truncate` are pure functions;
the real-exit drivers wrote only attempt-local scratch state (re-running any probe
against a fresh run root reproduces the evidence).

Synthetic logs stay in this attempt dir (before/runs-*, after/runs-*) per the card
recovery clause. No production file was written by this attempt; the pre-existing
user/other-card modifications in company-wiki (`CLAUDE.md`, `README.md`,
`artifact_dag.py`, the last one dated 2026-09-20 11:48 UTC, before this attempt)
were left untouched — see `after/external_edit_note.json`.
