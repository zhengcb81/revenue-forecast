# recovery/README.md — DW15-REPAIR recovery & review notes

## What this card produced

- `iso/baseline/` — byte-identical pristine copy of the production
  `src/company_wiki` tree (the two defective scripts:
  `prune_retired_evidence.py` sha256 `2358c73b…`, `archive_retired_evidence.py`
  sha256 `143fef01…`, both matching I-15-A's declared hashes).
- `iso/fixed/` — the repaired tree; **only** those two files differ
  (byte-verified: 146 files compared, 2 modified). See `changes.diff`.
- `tests/`, `harness/`, `mutants/`, `evidence/` — the RED/GREEN suite, fixture
  guard, the five single-fix reverts, and run evidence.
- `oracle.md` (frozen before any run), `decision.md`, `binding.json`,
  `commands.json`, `handoff.json`.

## Zero real data was touched

- Every catalog / archive / manifest / receipt used by the tests is synthetic,
  built by the tests themselves under `%TEMP%` (pytest `tmp_path`), and
  `guard_scratch()` hard-refuses (`SystemExit: BINDING-REFUSED`) any fixture
  path outside `%TEMP%`/this attempt or containing `.source_catalog`.
- **No production prune or archive execution of any kind occurred** (dry-run
  included). The 49.7 GB production catalog was never opened.
- After the attempt: production script hashes unchanged
  (`2358c73b…` / `143fef01…`, both in `Projects\company-wiki` and in the
  `.review-zr407-20260818` snapshot); `worker_control.json` unchanged
  (`9fcbe233…`, desired_state=paused); no git write operations were run.

## Synthetic fixture residue (safe to delete)

- `%TEMP%\pytest-of-*\pytest-*\` — per-run synthetic catalogs/archives created
  by pytest. They contain ONLY fake rows (doc-A/doc-B/doc-C, spans a1/a2/a3/b1/c1).
  Deleting them is safe and needs no review.
- `mutants/`, `iso/` — attempt-local code copies; no real data.

## What "recoverable" means here (and what a reviewer should check)

- A published snapshot can only exist complete: it is written to a temp file,
  fsynced, re-read and digest-verified, then atomically published
  create-if-absent. A kill never leaves a truncated file at a published path.
- Prune publishes a **pending receipt**
  (`<catalog>/artifacts/gates/prune-retired-<token>.json`) naming the FULL plan
  (span ids, row digests, archive sha256s, plan hash) **before the first
  delete**, updates it after each committed batch, and marks it `complete` at
  the end. After any crash:
  `deleted ids = receipt.plan ∩ (rows now absent from the catalog)`, and every
  such id is also present in the manifest-verified snapshot — i.e. the exact
  deleted set is restorable from durable artifacts (row-digest identity), not
  guesswork. Tests t_d5_2/t_d5_3 pin this.

## Gates before anything real runs (NOT satisfied by this card)

1. **Data-recovery reviewer re-sign** — outstanding by design (owner §15/§16:
   A-1 authorised repairing code only; D-W15 production execution stays
   unsigned). This is the expected remaining gap.
2. **Promotion decision** — moving `iso/fixed` into the `company-wiki` repo is a
   separate owner decision; the repo currently still holds the defective
   originals.
3. **Receipt durability medium** — JSON-under-`artifacts/gates` implemented per
   I-15-A D-W15-4 option (b); the reviewer may replace it with a DB table.
4. **Scale validation** — 25.7M-row / 49.7 GB behaviour is untested here.
5. **Product contract-test replacement** — the old tests encode the wrong oracle
   (I-15-A) and the archive test calls the old signature; both need replacement
   at promotion.

Until 1–2 are signed, treat `iso/fixed` as an isolated, reviewable repair and
nothing more.
