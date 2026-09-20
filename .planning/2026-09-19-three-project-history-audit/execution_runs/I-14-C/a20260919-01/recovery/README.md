# I-14-C recovery

The card's recovery clause: "撤回隔离实现，保留合成日志" (withdraw the isolated
implementation, keep the synthetic logs).

## How to withdraw the implementation (proven, not asserted)

1. The pre-image of all three edited modules is materialised and hash-verified at
   `before/prefix_src/src/company_wiki/source_catalog/{worker,observability,cli}.py`.
   Rebuild it at any time with:

       <iso-python> -X utf8 -B harness/build_prefix_tree.py \
           --cw <company-wiki> --snap before/prefix_src \
           --diff changes.diff --python <iso-python>

   `before/prefix_tree.json` records `all_ok=true` plus, per module, the sha256 that was
   recorded *before* any edit and the newline form it was matched in.

2. To revert the product working tree, apply the inverse of `changes.diff`:

       git -C <company-wiki> apply --reverse --ignore-whitespace changes.diff

   NOT executed by this attempt (the card is pending review; the implementer does not
   revert while a reviewer still needs the diff). If the reviewer requires the revert to be
   demonstrated, run it and re-hash: the three files must then equal the `prefix_*` values
   in `after/hashes.json`.

3. **Never** use `git restore` / `git checkout --` / `git stash` in company-wiki:
   `CLAUDE.md` and `README.md` carry the user's own pre-existing modifications and a
   blanket restore would destroy them.

## What is deliberately preserved

- `before/runs-pass1-prefix/**` — the leak reproduction (raw JSONL with the synthetic
  marker), kept as the counterexample.
- `after/runs-pass2-after/**` — the closed-state logs.
- `before/quarantine/runs-pass1-prefix-attempt1-failed-import/` — the first pre-pass, kept
  even though it was invalid (import error from a mis-assembled tree) so the failure is not
  silently erased.
- `before/cmd-B1`, `before/cmd-B2` — pre-image test runs.
- `after/quarantine/**` — superseded post-fix passes, kept for the same reason.

## Restoration of the environment

Nothing outside this attempt directory was written by any run. The only product-repo
change is the three-file diff. No catalog was created, no migration ran, no worker started,
`worker_control.json` was never opened for writing (`desired_state` remained `paused`;
hash `9fcbe233efe76222a32316c07b9273b9c5128da3af6db27d706b1759680ac7bd` before and after).
