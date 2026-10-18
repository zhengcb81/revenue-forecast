# DU11 published source/citation dependency pins

This ROOT-owned dependency update changes only `compatibility/current.json` and this release record. It does not change RF runtime, the checkout tool, public contracts, frozen baselines, registry hashes, installed skill files or output.

## Stage 1 published implementation inputs

- CWP: `0ccdc6896ee58063ff827e9ceab16043c7550e0c`. ROOT confirmed a successful normal push and exact remote `master` before authorizing this update. The producer's own full-unit/contract receipts remain with CWP; this RF update does not reclassify its real content acceptance.
- RF implementation base: `f8002f5fc8f56533c814f1616b7ecb68016f35e4`, already published on RF `main`. CI tests its current checkout HEAD and skips the revenue sibling checkout, so this implementation pin deliberately does not refer to the commit containing this manifest.
- FF: retain the existing published pin `5001dcbef1845a08e90cda6f2a86365610a662af`. A new FF pin must wait until that producer commit is actually remotely fetchable.

The existing sibling tool fetches exact manifest SHAs; no floating branch or new permission gate is introduced. `updated_at` and `note` describe this release. The installed skill packaging excludes the repository-only compatibility control plane; all three installed logical roots currently lack `compatibility/current.json`, so no installation file is created or synchronized.

## Focused verification

28 tests passed in 9.09 seconds using the existing FC-1101 manifest checks, compatibility validator/mutation controls and the three CA-301 C1 checkout/commit checks. Tests used an owned temporary directory, `-B`, `no:cacheprovider`, disabled optional pytest plugin loading and a minimal OS path/temp environment without credential variables. The owned temporary directory was deleted successfully. Full test command, XML, log and cleanup receipt are in the coordinating CWP ROOT worktree's `docs/plans/du11-source-closure-2026-10-18/review/du11-dependency-pin-tests.*`.

Normal commit hooks and the existing pre-push checks run as part of publication. Remote commit/CI status must be taken from the ROOT publication receipt after that operation, not inferred from these focused tests.

## Stage 2: final published FF implementation

Stage 1 was normally committed and pushed as `e73646395c3b0aea0bca054ffdcc46b2f1e66c45`. The normal pre-push checks passed Ruff, public types and 416 tests plus 36 subtests in 70.53 seconds. Its exact GitHub quality run `39094965965` completed successfully. This first-stage evidence is retained rather than replaced by the final pin update.

ROOT then confirmed FF `main` and remote both at the published implementation commit `e8740748f91999cb24169b42f8e789726ed50482`, after FF's normal checks/push. Only `current_triplet.filing` now moves to that commit. The final triplet is:

- CWP `0ccdc6896ee58063ff827e9ceab16043c7550e0c`;
- RF implementation base `f8002f5fc8f56533c814f1616b7ecb68016f35e4`;
- FF `e8740748f91999cb24169b42f8e789726ed50482`.

The same existing focused checks passed again: 28 tests in 9.23 seconds, with the owned temporary directory restored. Stage-2 command, XML and cleanup receipt are adjacent `du11-dependency-pin-stage2-tests.*` in the ROOT worktree review directory. No pure documentation HEAD is chased and no recursive self-pin is created. Final normal-push/remote-CI evidence is recorded after publication in the same ROOT publication report.

At stage-2 start the daily and weekly alert hashes below were unchanged. The observed weekly manifest hash was now `49803e12057c3fd284797a67678ce47a0829db40dbcebafc92af7c9d53d22324`, changed during stage 1 from the earlier observation. This record does not attribute its writer or restore any historical value.

## Unrelated local state

The three pre-existing assurance WIP files are excluded from staging. Their observed pre-update SHA-256 values are:

| Path | SHA-256 |
|---|---|
| `assurance/runs/daily_alert.jsonl` | `8d4a7e41b2d4067e0dd82f504c582f245fe01ea5ff548f13f9c1f0fb8706791c` |
| `assurance/runs/weekly_alert.jsonl` | `a05699bf906b1cf3e78eda8cf98c4c1b3105e7f9ddf418aac39640d9fa11e7c2` |
| `assurance/runs/weekly_manifest.json` | `c41959e3cd5925c87c00164c089671e62ba193cf21c5f5de4b152515ba45a239` |

These are current observations, not permission to restore older values over externally generated updates. ROOT records hashes again after publication. The untracked `output/` directory is not read, staged or modified. No manual stash/reset, force push or hook bypass is part of this operation.
