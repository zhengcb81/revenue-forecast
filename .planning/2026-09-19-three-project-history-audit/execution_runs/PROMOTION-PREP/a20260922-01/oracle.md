# PROMOTION-PREP oracle (attempt a20260922-01)

## Source-of-truth rule
- Each accepted card's `binding.json`, `changes.diff`, `handoff.json` are the carriers of record.
- Every cited path hash MUST be measured LIVE in this attempt via `Get-FileHash -Algorithm SHA256` (working tree) or `git show <ref>:<path> | Get-FileHash`-equivalent (blob).
- MEMORY-CONSTRUCTED / HINTED HASHES ARE FORBIDDEN. Any number appearing in task hints, prior reports, or my own memory is UNVERIFIED until re-measured here.
- UNRESOLVED cells are allowed and preferred over guesses.

## Write boundary
- Zero production writes. All repos (revenue-forecast, company-wiki sibling, any others) are READ-ONLY.
- No pytest / no test runs. `git apply --check` only on %TEMP% copies, and only if time permits; otherwise mark UNRESOLVED-verification.
- No git writes (no add/commit/checkout/apply to real trees). No self-signing of any handoff.
- All writes confined to `<PLAN>\execution_runs\PROMOTION-PREP\a20260922-01\`.

## Order of work
1. Read OWNER_DECISIONS.md §十七 B-table (B-1..B-7) only.
2. Per item: read card carriers (binding.json pins, changes.diff '^diff' headers, handoff.json scope/gaps/conditions) via grep sections.
3. LIVE-hash source + target files.
4. Append manifest row immediately (incremental save).
5. Diffs/ordering notes last; skip `git apply --check` if time-pressured (mark UNRESOLVED-verification).
6. Finish minimal binding.json / decision.md / commands.json / recovery/README.md; report headline table + manifest sha256.
