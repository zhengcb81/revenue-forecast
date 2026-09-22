# recovery/README — B1-PREREQ a20260922-01

**State model: stateless.** This attempt performs no stateful product
operation — no transaction, no lock, no migration, no registry write into any
repository. Every publication `run_forecast` executed here was redirected to
attempt-local registries (`runner/registry/publications.jsonl` via
`conftest.py`/`run_arm.ps1`, and `scratch/probe_work/publications.jsonl` by the
probe), so there is **nothing in production to recover**. The trust fixture's
private key exists only in pytest temp dirs and `scratch/probe_work/`
(the provider signs with the same fixed demo key as B1's frozen fixture;
non-secret by design).

## If this attempt's artifacts need rebuilding

1. **M6 mutant** (scratch-only): `commands.json` `PR-c3` — copy
   `SRC/iso/fixed/rf` → `scratch/mutations/M6/rf`, run `scratch/apply_m6.py`
   (refuses to patch anything whose pre-hash ≠ `bc2bb4a3…`), then
   `scratch/verify_m6_delta.py` (refuses unless exactly one file differs).
2. **Evidence**: never rebuild *over* an existing label. `run_arm.ps1` exits 99
   on collision; a rebuild uses a NEW label plus a disclosure in `handoff.json`
   (F4 protocol, `evidence/README.md`).
3. **Freeze verification**: `scratch/final_integrity_check_v2.py <MY> <SRC>
   <PROD>` re-hashes the whole `freeze.json` chain (SRC oracle prefix-pinned)
   plus every boundary pin. Expected rc 0, `all_ok: true`.
4. **SRC oracle appends**: already applied (r5, r6). They are append-only and
   must never be re-applied; `append_revision.py` refuses when the marker is
   already present or any frozen prefix hash mismatches.

## What is NOT recoverable (disclosed; r2-corrected scope)

- **r1 test file only**: sha256 `e6c0949c…`, 18236 B — absent from the working
  tree, from every reachable commit (reachable content blobs for the path are
  18611 B / `da3d29bf…` then 20631 B / `636b43c8…`), and by size from the 1294
  reflog-unreachable blobs the reviewer scanned (reviewer report §4.4/§5.3).
- The r1 RED stdout is **NOT lost**: `SRC/before/b1_unfixed.stdout.txt`
  (30580 B / `58863ffb…`, UTF-16LE+BOM, "10 failed, 2 passed in 8.18s") survives
  on disk and in git (single commit `980c9b7a`, blob == HEAD == working bytes)
  — re-measured in `evidence/r2/r2_01*`, `r2_02*`, `r2_03*`.

Superseded wording, retained verbatim (`superseded_reason: refuted by reviewer
F-REV-B1P-01 with byte evidence`; first published in this file's r1 bytes,
sha256 `6fe88d7b8078ede4fab1b4daefe12be36b49ba9d1f49d712e9e91c7b3109052e`):

> - B1's r1 RED stdout ("10 failed / 2 passed") and the r1 test file
>   (`e6c0949c…`, 18236 B) — overwritten/removed before archiving by B1's own
>   run sequence. No later card can recreate those bytes. This is the F4/REM-43
>   historical gap; it stays open and disclosed (this card closed only the
>   *protocol* half of REM-43).

Note: the sibling frozen carrier `evidence/README.md` (freeze entry
`my_evidence_readme`, SHA256SUMS entry) still holds the same refuted wording at
its lines 5 and 23–30 and CANNOT be edited without breaking the F5 chain; it is
superseded by `decision.md` §r2 and SRC `oracle.md` Revision r7 (carrier scan:
`evidence/r2/r2_14_false_carrier_addendum.json`).
