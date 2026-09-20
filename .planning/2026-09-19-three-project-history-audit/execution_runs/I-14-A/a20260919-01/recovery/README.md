# I-14-A / a20260919-01 — recovery and take-over notes

## Rollback rule

Nothing in the product tree was modified, so there is no rollback. Everything this card wrote lives
under `execution_runs/I-14-A/a20260919-01/`. Reverting the meter means nothing more than not
promoting `iso/slo_probe_patched.py`: `RF/tools/slo_probe.py` is still the untouched original
(sha256 `f051feec00658bb5fefee8d22c2c7630e0bd348b5384ae80f0c882c822f48059`, blob
`413aad5f788732520ace76acbaebcf06633f34d5`, equal to `HEAD:tools/slo_probe.py` and to the worktree).

## Promotion gate (the one thing that must not be skipped)

`iso/slo_probe_patched.py` **must not** be copied into `RF/tools/` (nor its test into
`RF/tools/tests/`) until **D1** is signed by an ops reviewer who is **not** the author of this probe.
D2 belongs to the production SLO / probe owner; D3 belongs to I-16. See `decision.md`.

## Repository head pointer (read this before citing a head value)

| when | revenue-forecast HEAD | who moved it |
|---|---|---|
| capture time of `after/snapshot.json` | `7d7ea1edc5e0371ffefee0d2ab3c4a34643199d5` | — |
| now | `1ac01f029c16b90adba92dd0f1bc3a1825ff9552` | **the orchestration layer (parent agent)**, commit "审计实施段：I-04-C 接受…" at 2026-09-20 03:41:55 +0100 |

**The product tree and `tools/` did not change**: that commit touches only `.planning/`, and
`tools/slo_probe.py` has the same blob id at both HEADs and in the worktree — the fact this card's RED
baseline rests on. `7d7ea1ed` is an ancestor of `1ac01f0`.

`after/snapshot.json` still records `7d7ea1ed` and is **correct for its capture time**; it was not
rewritten (rewriting a captured observation is forbidden). Read it as "HEAD at capture".

**The pointer is still moving — it is a live value, not a fact to copy.** Observed sequence during this
round: `7d7ea1ed` → `1ac01f02` → `66bd75f1` → `ddc81ab6` → **`cc78c5298acd5a5ff8b898d9aa237fc5a8559979`**
(2026-09-20 04:27:52 +0100). Every one of those commits is confined to
`.planning/2026-09-19-three-project-history-audit/` (the last one: 1636 paths, none under `tools/`), each
is an ancestor of the next, and `tools/slo_probe.py` keeps blob id
`413aad5f788732520ace76acbaebcf06633f34d5` at **all** of those revisions and in the worktree. The card's
anchors are therefore unaffected; the `head_pointer_note` in `handoff.json` records `1ac01f0` because
that is the value the review flagged at the time — treat it as an example of the rule, not as current.

## Porcelain state (correct the record if you read otherwise)

`git -C company-wiki status --porcelain` returns **exactly two** lines — ` M CLAUDE.md` and
` M README.md`, the user's pre-existing edits (sha256 `963869fa08…` / `302bd10b38…`, mtime
2026-09-19 11:20, both differing from their HEAD blobs). They were **not** reverted.

A re-read reported this tree as "completely empty". **That claim is wrong**; the correct statement is
"only the two pre-existing ` M` entries". No conclusion changes: neither file is in this card's anchor
set, and the material scope checks (`-- tools` for RF, `-- src config scripts tests` for CW,
`--untracked-files=all` for FF) are all empty.

## If you must re-verify this card

1. `git -C <RF> rev-parse HEAD`; compare `hash-object tools/slo_probe.py` against
   `HEAD:tools/slo_probe.py`.
2. `<iso-python> harness/run_probe_cases.py --tool iso/slo_probe_patched.py --out <fresh> --all`
   → expect E1a/E1b = 4, E1c/E2/E3/E7 = 2.
3. `<iso-python> -m pytest harness/tests/test_i14a_failure_branches.py` → 12 passed / 1 skipped;
   with `I14A_TOOL=iso/tool_prod/slo_probe.py` → 10 failed / 2 passed / 1 skipped.
4. `harness/run_bundle_control.py <patched> <out> <prod>` → rc 0.

## Known traps for the next card

- **`--rss-sampler none` is the deterministic no-sample branch**; a fast child still yields one live
  sample because the sampler reads at spawn time.
- **The peak is a tree sum and overestimates by the launcher's own RSS** (≈11 MB measured).
- **`peak_pid` is often `null`** — use `peak_tree_pids`.
- **The patched tool exits 2 on every default run** (no `--bundle-measurement`). This is intended and
  still awaits signature (F-I14A-01); I-16 must supply a bundle measurement file before its
  production gate can read green.
- A hash citation names the file **and** its capture time; `after/summary.json:r2_new_hashes` carries
  `self_invalidating` markers for files that are edited after capture. `captured_at_utc` there is an
  aware UTC timestamp (review residue N2: the earlier value was naive local time wearing a hand-written
  `+00:00`, which was already 1 h off on this host).

## Attribution of `review.md` (r4) — read before citing it

`review.md` has **two different provenances**; citing the wrong one would misrepresent the independent
review:

| range | provenance | citable as reviewer-authored? |
|---|---|---|
| `:3`, `:156`, `:189`, `:276-415` | **the independent reviewer's own words** — PENDING preamble, r2 block, the r3-confirmation sentence re-registered in the r2 frame, and the r4 attestation it appended itself | **yes** |
| `:234-241` | the reviewer's attribution marker (a pure insertion) | yes |
| `:242-272` | **a BOOKKEEPING TRANSCRIPTION** of the reviewer's r3 report, produced by this attempt's bookkeeping pass — **not** the reviewer | **no** |

The reviewer explicitly declines to own `:242-272` and is not the author of its verdict sentence at
`:244`. Do not treat its assertions as endorsed: the reviewer's own §6.2 states that any other statement
in that range "is someone else's text and is not endorsed by this signature". If a reviewer-authored r3
block is wanted, **the reviewer must add it itself**. The reviewer's §7/§8 line maps carry its own
off-by-one corrections; §8 is its last word.

`handoff.json` records this attribution in `reviewer_status_source` and `reviewer_r4_verdict`, and
**`handoff.json` is deliberately NOT hash-cited anywhere** — it is extended continuously by bookkeeping,
so a citation of it (or inside it) goes stale on the next write. That is review finding P4, reopened by
the reviewer and closed here by option 2: the file is declared uncited in
`after/summary.json:r2_new_hashes.uncited_files`. Recompute with `Get-FileHash` if you need a value.
