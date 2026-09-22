# GATE-TIMEOUT-1200 / a20260922-01 — Recovery README

## What this attempt changed in production

Exactly ONE line in `tools/pre_push_gate.py` (owner ruling `OWNER_DECISIONS.md` §16, B = a):

```diff
 def _run(
-    cmd: list[str], label: str, timeout: int = 600, *, blocking: bool = True
+    cmd: list[str], label: str, timeout: int = 1200, *, blocking: bool = True
 ) -> int:
```

| state | sha256 |
|---|---|
| original / anchor (also RED-arm state) | `0d290326200ebde819d3473589bd1aa0ed36da4806097d8a59dc8dc316fcc594` |
| authorized final (GREEN-arm state) | `cf09ade8164e89d79237ff5a8409496ab1ae2a9c5f3ee2c253ccad20ef06df0b` |

Byte-exact copies of both states:
- original: `before/pre_push_gate.py.orig`
- the authorized state is `before/pre_push_gate.py.orig` with the single line above replaced
  (this reconstruction was hash-verified equal to the after hash before the GREEN arm ran —
  `evidence/line_change.json`).

No other production file was written by this attempt (verify with
`evidence/git_status_before_red.txt` vs `evidence/git_status_after_green.txt` and
`git diff --numstat`).

## If the working tree must be restored to the original gate (rollback)

```powershell
git -C C:\Users\郑曾波\Projects\revenue-forecast checkout -- tools/pre_push_gate.py
# or, byte-exact without git:
Copy-Item <attempt>\before\pre_push_gate.py.orig `
          C:\Users\郑曾波\Projects\revenue-forecast\tools\pre_push_gate.py -Force
```

Then re-hash: must be `0d290326…ec594`.

## If the authorized state was lost (e.g. checkout during the RED window)

```powershell
Copy-Item <attempt>\before\pre_push_gate.py.orig <temp>
# apply changes.diff, or simply replace the one line 600 -> 1200 as above
git -C C:\Users\郑曾波\Projects\revenue-forecast apply <attempt>\changes.diff   # only when file is at anchor
```

Hash must be `cf09ade8…6df0b` before any push is attempted.

## Re-running an arm (reproduce)

```powershell
# RED (bounded to ONE live attempt by the card; a re-run is a NEW attempt id):
& <attempt>\scripts\run_red.ps1
# GREEN:
& <attempt>\scripts\run_green.ps1
```

Each script: (1) hash-verifies the gate state it needs, (2) starts exactly 8 CPU burners
(`scripts/cpu_burner.py`) and records PIDs, (3) runs the gate through
`scripts/timed_gate_run.py` (full unfiltered capture + per-step timestamps), (4) stops the
burners, (5) prints verdict markers. Interrupt handling: if a script dies mid-arm, kill any
leftover burner PIDs (they are pure busy loops) with
`Get-Process python | Where-Object { $_.Path -eq 'C:\Miniconda\python.exe' }` cross-checked
against `evidence/burners_*.json` pids, then `Stop-Process -Id <pid> -Force`.

## Facts needed to interpret the evidence

- RED capture: `after/gate_red_600.txt`; step times: `after/step_times_red_600.json`.
- GREEN capture: `after/gate_green_1200.txt`; step times: `after/step_times_green_1200.json`.
- The gate was run with python `-u` (line-unbuffered stdout for truthful step timestamps)
  and NO gate flags. `-u` is a capture-fidelity flag only; it changes no gate logic.
- RED's killed pytest run cannot print a final `55 passed` summary — per oracle I-3 that
  absence is inherent to RED and is never to be read as a skip or a deselection.
- `tools/sync_installations.py` runs inside the gate by design and may refresh stale
  installed skill copies (`~/.agents`, `~/.claude`, `~/.codex`); that is the gate's own
  documented behavior, not a change made by this card.
