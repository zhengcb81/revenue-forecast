# RF Closeout: Preserved Temp Worktree Ledgers

These are exact byte copies of the only unique untracked runtime files found in two registered AppData Temp worktrees. Both corresponding branch tips are ancestors of RF `main`; all tracked changes in those worktrees were deletions from disposable/emptied worktrees. The JSONL ledgers are preserved before removing the two worktrees. SHA-256 and byte counts are listed below.

| Archived file | Original worktree | Original branch / HEAD | Bytes | SHA-256 |
|---|---|---|---:|---|
| `m3-period-evidence-publications.jsonl` | `C:\Users\郑曾波\AppData\Local\Temp\rf-period-evidence-20261010` | `codex/m3-period-evidence-20261010` / `f8ae04884237c39d204689883c8756ee7d33a0a9` | 35450 | `1e5fc87bb319814ab33932adbcbff9e3e757781bfb377b86a18cc7a65c8385ed` |
| `source-ref-v2-publications.jsonl` | `C:\Users\郑曾波\AppData\Local\Temp\rf-source-ref-v2-integration-20261003` | `codex/rf-source-ref-v2-integration-20261003` / `0573c40c739bdbe0bef9445e97e88046e3ef1b69` | 3830 | `89f9815b446be4076ebc2b87addc6c516c33af59419d3175937670ed75a0906e` |

The first ledger contains records produced by the period-evidence run; the second contains the earlier SourceRef v2 run records. These are provenance/runtime evidence, not canonical forecast inputs.
