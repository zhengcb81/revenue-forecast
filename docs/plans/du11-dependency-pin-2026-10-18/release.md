# DU11 published source/citation dependency pins

This ROOT-owned dependency update changes only `compatibility/current.json` and this release record. It does not change RF runtime, the checkout tool, public contracts, frozen baselines, registry hashes, installed skill files or output.

## Published implementation inputs

- CWP: `0ccdc6896ee58063ff827e9ceab16043c7550e0c`. ROOT confirmed a successful normal push and exact remote `master` before authorizing this update. The producer's own full-unit/contract receipts remain with CWP; this RF update does not reclassify its real content acceptance.
- RF implementation base: `f8002f5fc8f56533c814f1616b7ecb68016f35e4`, already published on RF `main`. CI tests its current checkout HEAD and skips the revenue sibling checkout, so this implementation pin deliberately does not refer to the commit containing this manifest.
- FF: retain the existing published pin `5001dcbef1845a08e90cda6f2a86365610a662af`. A new FF pin must wait until that producer commit is actually remotely fetchable.

The existing sibling tool fetches exact manifest SHAs; no floating branch or new permission gate is introduced. `updated_at` and `note` describe this release. The installed skill packaging excludes the repository-only compatibility control plane; all three installed logical roots currently lack `compatibility/current.json`, so no installation file is created or synchronized.

## Focused verification

28 tests passed in 9.09 seconds using the existing FC-1101 manifest checks, compatibility validator/mutation controls and the three CA-301 C1 checkout/commit checks. Tests used an owned temporary directory, `-B`, `no:cacheprovider`, disabled optional pytest plugin loading and a minimal OS path/temp environment without credential variables. The owned temporary directory was deleted successfully. Full test command, XML, log and cleanup receipt are in the coordinating CWP ROOT worktree's `docs/plans/du11-source-closure-2026-10-18/review/du11-dependency-pin-tests.*`.

Normal commit hooks and the existing pre-push checks run as part of publication. Remote commit/CI status must be taken from the ROOT publication receipt after that operation, not inferred from these focused tests.

## Unrelated local state

The three pre-existing assurance WIP files are excluded from staging. Their observed pre-update SHA-256 values are:

| Path | SHA-256 |
|---|---|
| `assurance/runs/daily_alert.jsonl` | `8d4a7e41b2d4067e0dd82f504c582f245fe01ea5ff548f13f9c1f0fb8706791c` |
| `assurance/runs/weekly_alert.jsonl` | `a05699bf906b1cf3e78eda8cf98c4c1b3105e7f9ddf418aac39640d9fa11e7c2` |
| `assurance/runs/weekly_manifest.json` | `c41959e3cd5925c87c00164c089671e62ba193cf21c5f5de4b152515ba45a239` |

These are current observations, not permission to restore older values over externally generated updates. ROOT records hashes again after publication. The untracked `output/` directory is not read, staged or modified. No manual stash/reset, force push or hook bypass is part of this operation.
