# I-07-A / a20260919-01 — recovery and take-over notes

This card changes no product code and runs no product path, so there is no state to roll back.
What a successor needs is recorded here instead.

## Rollback rule

Nothing to revert. The attempt wrote only under
`execution_runs/I-07-A/a20260919-01/`. The single production-adjacent artifact it created is
`iso/catalog_root/**`, which is a set of **copies** — deleting it changes nothing in
`company-wiki/companies`. Each source file was re-hashed after copying and still matches the
manifest (`iso/isolated_state.json:copied[].source_still_present_after_copy`).

## Repository head pointer (read this before citing a head value)

| when | revenue-forecast HEAD | who moved it |
|---|---|---|
| capture time of `before/snapshot.json` (V0) and `after/snapshot.json` (V5′) | `7d7ea1edc5e0371ffefee0d2ab3c4a34643199d5` | — |
| now | `1ac01f029c16b90adba92dd0f1bc3a1825ff9552` | **the orchestration layer (parent agent)**, commit "审计实施段：I-04-C 接受…" at 2026-09-20 03:41:55 +0100 |

**The product tree and `tools/` did not change.** That commit touches only `.planning/` (49 files);
`tools/slo_probe.py` carries the same blob id `413aad5f788732520ace76acbaebcf06633f34d5` at both HEADs
and in the worktree, and `7d7ea1ed` is an ancestor of `1ac01f0`. The five frozen anchors recompute
identically.

The two snapshots still record `7d7ea1ed`. **They are correct for their capture time and were
deliberately not rewritten** — rewriting a captured observation is exactly what this plan forbids.
Read them as "HEAD at capture", never as "HEAD now".

## Porcelain state (correct the record if you read otherwise)

`git -C company-wiki status --porcelain` returns **exactly two** lines:

```
 M CLAUDE.md
 M README.md
```

Both are the user's pre-existing edits (on-disk sha256 `963869fa08…` / `302bd10b38…`, mtime
2026-09-19 11:20, both differing from their HEAD blobs). They were **not** reverted by this card.

One of the re-reads reported this tree as "completely empty". **That claim is wrong** — the correct
statement is "only the two pre-existing ` M` entries". It changes no conclusion: neither file is in
this card's anchor set, and the material scope check
(`git status --porcelain -- src config scripts tests`) **is** empty.

## If you must re-verify this card

1. `git -C <RF> rev-parse HEAD` and compare against `before/snapshot.json:repos`.
2. Re-derive one raw sha256 and compare against `after/rehash.json` and the plan manifest.
3. Compare `before/snapshot.json` and `after/snapshot.json` on `(catalog.bytes, catalog.mtime_iso,
   catalog.wal_bytes)` — they must be equal.
4. Re-run `harness/i07a_helpers.py observe` only if you accept a fresh read-only production query;
   the frozen numbers live in `after/observe_readonly.json` and `after/r2_review_facts.json`.

## Known traps for the next card

- **Do not reuse `iso/catalog/catalog.sqlite3`.** It is a 5-table minimal schema against production's
  18; I-07-B must bind a production-isomorphic or table-filtered catalog.
- The dimension count is **7 plan rows + 1 extra family (`generality`) = 8 families, 29 cells**.
  Any "six" you find refers to the number of *review findings* (F-I07A-01…06), not dimensions —
  see `oracle.md` §8.
- `config.legal_fifth_root` is **`planned`**; `decision.md` §J2's original `bound` position is marked
  **OVERRULED** in its r2 section and must not be cited.
