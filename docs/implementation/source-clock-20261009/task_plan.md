# RF source clock implementation

Status: in_progress; base e688b0a2; branch codex/source-clock-20261009.

## Scope

One RF owner. Preserve historical as_of=2026-10-08; actual current UTC read/capture/check may be later. One pure source clock policy and all source/capture/claim/narrative responsibility boundaries. Future publication and unknown-without-reliable-proof stay refused; exact raw SHA proof binding and old frozen bytes/runtime compatibility stay explicit. Optional public receipt2.2 proof consumer uses declared capability; CWP producer owned by MAIN.

Allowed: owned RF scripts/contracts/source_clock.py, card-listed RF boundaries/direct tests and this implementation directory; necessary RF version/compatibility docs. Forbidden: CWP/FF/Dayu code, production/registry, originals, installation copies, MAIN PWF.

## Phases

1. Confirm worktree/base and initialize this PWF: complete.
2. Actual 18-case responsibility RED: complete (16 FAIL /2 PASS).
3. Shared implementation and focused GREEN: complete (20 clock + 6 deadline responsibility cases).
4. Concentrated regression/targeted repair/static checks: complete; required offline CI gate GREEN (126 PASS /18.63s).
5. Scoped normal commit and INTERFACE/HANDOFF/handoff.json: pending.

## Next Step

Finish required offline gate, normal scoped implementation commit, and precise INTERFACE/HANDOFF with actual proof limits.

## Errors

Requested company-wiki/_harness_worktrees path absent; resolved real path via canonical git worktree list to Projects/_harness_worktrees/cmrf-20261008/rf-inputs. Default read of adjacent RF denied; normal require_escalated reads/writes used under existing explicit authorization. No WIP existed; old branch retained.
