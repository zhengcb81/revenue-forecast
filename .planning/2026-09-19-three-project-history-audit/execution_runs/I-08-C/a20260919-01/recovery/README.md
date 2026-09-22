# recovery/README.md — I-08-C (attempt a20260919-01), incl. fix round I-08-C-REFREEZE

## 1. Why this directory is almost empty

`review_and_handoff.md` asks each attempt to carry a recovery story for stateful
product operations. This card — in its r1/r2/r3 life **and** in this fix round —
performs **no stateful product operation**: no transaction, no lock, no
migration, and no registry write.

- The formal `run_forecast` path *does* append to the publication registry, so
  every run in this attempt redirects `REVENUE_PUBLICATION_REGISTRY` into a
  pytest temp dir (fixture) or an attempt-local dir. Production's
  `artifacts/registry/publications.jsonl` keeps its frozen hash
  `bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91`
  before and after all four fix-round runs.
- Consequently there is **no crash-recovery case to demonstrate**: nothing this
  attempt does can leave product state half-written. This matches the r3
  `steps_not_applicable.recovery/` entry; the fix round does not change it.

## 2. What "recovery" does mean for this fix round (interruption of the ATTEMPT)

If this round had been interrupted mid-way (it was not), the artefacts are
self-recovering in the sense that their integrity is machine-checkable and the
round is restartable without ambiguity:

| If interrupted at… | Recovery procedure | Integrity check |
|---|---|---|
| before the oracle r4 append | nothing to undo; the r3 file is intact (22335 B / `94a853e9…`) | `scratch/fixround/prefix_proof.py` fails loudly (pre-image mismatch) if anything changed |
| after the append, before the runs | re-run nothing; the four runs and the mutation build are deterministic from the frozen files | `prefix_proof.json` → `append_only_proof: true`; test file `13152 B / 3f83fdf2…` |
| after some runs | simply re-run ALL FOUR runs — each writes its own stdout file; expected rcs are frozen in `oracle.md` R4-4 (A=0, B=1, B2=1, M=1) | `scratch/fixround/rcs.txt` must read `RUN-A=0 RUN-B=1 RUN-B2=1 RUN-M=1` |
| mutation file lost | rebuild byte-exactly with `scratch/fixround/make_mutation.py` (it asserts the two r4 literals before writing) | rebuild output must hash to `eb19e628…` |
| changes.diff doubt | rebuild with `scratch/fixround/make_changes_diff.py` — it refuses to write unless the reconstructed r3 test file hashes to `0072b160…` and the oracle prefix to `94a853e9…` | script rc must be 0 |

## 3. Deliberately disposable / volatile state (no recovery needed)

- `runner/fixround/tmpA|tmpB|tmpB2|tmpM` — pytest `--basetemp` dirs; pytest
  removes and recreates them at each run start. Contents are registry temp
  files only.
- `__pycache__` / `.pytest_cache` — **not touched this round**: every fix-round
  command ran with `-B` + `PYTHONDONTWRITEBYTECODE=1` + `-p no:cacheprovider`,
  precisely so the r3 `.pytest_cache` node/lastfailed records survive as
  timeline evidence.

## 4. What must NOT be "recovered" (frozen evidence — restoring over it would be tampering)

- `oracle.md` bytes `[0:22335]` (r1/r2 body `[0:6831]` inside it) — append-only;
  both prefixes are hash-proved. Recovery = re-verify, never rewrite.
- `pytest_verdict.stdout.txt` (r2, reviewer-confirmed), `pytest_r3_verdict.stdout.txt`,
  `review.md`, `reviewer_rerun_stdout.txt`, `exploratory/**` — never overwritten
  by this round; a "restore" that changes any of them invalidates the review.
- B1's attempt (`execution_runs/B1-I08C-product-fixes/**`) — READ-ONLY for this
  card; there is nothing here for this card to restore there, and writing there
  would be a boundary violation, not a recovery.

## 5. State left behind by this round (all inside the attempt)

Evidence files under `scratch/fixround/`, four run stdouts + `rcs.txt`,
`changes.diff` fix-round addendum, `recovery/README.md` (this file), plus the
appended `oracle.md` revision r4 and the updated
`handoff.json` / `binding.json` / `commands.json` / `decision.md`. Hashes for
all of them are in `binding.json.post_run_hashes.current_after_fix_round` and
`handoff.json.deliverables`.
