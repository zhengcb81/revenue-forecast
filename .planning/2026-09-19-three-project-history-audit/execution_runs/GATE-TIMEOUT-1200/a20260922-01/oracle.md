# GATE-TIMEOUT-1200 — Oracle (FROZEN BEFORE ANY CHANGE)

- Card: `GATE-TIMEOUT-1200`
- Plan: `C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit`
- Attempt: `execution_runs/GATE-TIMEOUT-1200/a20260922-01`
- Freeze rule: this file is written and its sha256 recorded in `evidence/oracle_freeze.json`
  **before any byte of `tools/pre_push_gate.py` is modified**. If any predicate below
  must change later, that is an oracle revision and must be disclosed as such — it is
  not allowed to be edited silently after the arms run.

## 1. Authorization (owner ruling, verbatim)

`OWNER_DECISIONS.md` §16（【已裁定·第七批】，原话逐字）:

> 「A-1: b（允许修 prune 代码，不授权执行 prune） A-2: 批准 **B: a（提高门超时到 1200，立卡红绿）** C: 先推已收口的 4 张，B1/B3/I-14-D 攒第二批 D-G1: a D-G2: 留置/（或给取舍） E-1: 150/60 E-2: 重跑 E-3: 立卡 E-4: 维持暂不签」

§16 table row: `| **B = a** | 门超时 600→**1200**，立卡红绿 | 与建议一致（改门不绕门，全测照跑照判） | 待无-bug 确认回来后执行 |`

前置（§15 B, already satisfied — the no-bug confirmation came back and is given evidence below):
「提高门超时，但先确认测试本身没有 bug」+「确认无 bug 后才改 `pre_push_gate.py`，且须留红绿证据」。

**Authorized production change — exactly ONE line**: `tools/pre_push_gate.py`, function
`_run()` signature default `timeout: int = 600` → `timeout: int = 1200` (line 73).
Nothing else in the gate may change. No `--skip-*` flag, no flag at all, may be passed
to the gate in any arm.

## 2. Given evidence (given to this attempt as already-confirmed facts; restated, NOT re-litigated)

1. The 7 E2E files contain NO `xfail` and NO `time.sleep`; 4 conditional `pytest.skip`
   exist but did NOT trigger.
2. Full run: **55 passed, 0 skipped, 0 xfailed** in **419.34 s** (light load).
   (55 = 8+6+3+6+8+19+5 across the seven `REAL_ROOTS_TESTS` files —
   REMEDIATION_REGISTER.md §「E2E 超时的精确定位」per-file table.)
3. Slowest single test **70.25 s** (`test_ca203_weekly_t3.py::test_c3_amendment_downloads_only_missing_new_period`)
   — real work, no hang; top-20 durations show no outlier approaching a hang.
4. Under concurrent session load the same suite exceeded the 600 s cap: recorded
   `subprocess.TimeoutExpired ... timed out after 600 seconds` artifacts (see `findings.md`
   close-out section 「【收尾】2026-09-21」 and
   `execution_runs/_isolation_incidents/20260920-precommit-stash-production-rollback/PUSH_TIMEOUT_INCIDENT.md`);
   a sequential per-file run under load totaled **861.7 s** with **55 passed / 0 failed**.

Conclusion that follows from the given evidence (owner's premise for §16-B): the suite
has no skip/xfail/sleep bug; the 600 s gate cap, not the tests, is the failure cause.

## 3. Machine context recorded at freeze time

- CPU: 10 cores / 12 logical processors; RAM ≈ 16 GB; OS Windows.
- Interpreter for the gate: `C:\Miniconda\python.exe` (Python 3.13.9).
- Repo HEAD at freeze: `1d2288c0`; `git status --porcelain -- tools/pre_push_gate.py`
  was EMPTY (working tree clean for the target file).
- `tools/pre_push_gate.py` sha256 at freeze (= **before** hash, also the RED-arm anchor):
  `0d290326200ebde819d3473589bd1aa0ed36da4806097d8a59dc8dc316fcc594`
- HEAD blob id of the file (git SHA-1 blob, different algorithm, recorded for cross-check):
  `b5725cb61d98b12a6ab9169b4556c1f2a4ab4e30`
- Shared machine: 2 unrelated python processes were already running at freeze (load not zero).

## 4. Predicates

### RED arm (live, pre-registered)

- Config: `tools/pre_push_gate.py` at the **pre-change bytes** (sha256 = before hash above,
  i.e. `_run()` default `timeout: int = 600`), invoked exactly
  `C:\Miniconda\python.exe tools/pre_push_gate.py` from the repo root, while **exactly 8 CPU
  burner processes** (busy loops, `scripts/cpu_burner.py`) run concurrently for the whole run.
- **RED fires iff** the captured full output `after/gate_red_600.txt` shows the gate's
  `=== real-roots E2E (CI real-roots job) ===` step raising
  `subprocess.TimeoutExpired: ... timed out after 600 seconds` (uncaught traceback, gate
  exit code ≠ 0, no `pre-push gate GREEN` line).
- **Bounded: ONE live attempt only.** If the E2E step does not exceed 600 s under this
  induced load (machine variance), stop the loading immediately and fall back to the
  recorded TimeoutExpired artifacts of §2.4 as RED evidence, labeled verbatim:
  **"historical repro record, not live-reproduced this round"**. The load is never faked,
  inflated, or re-attempted.

### GREEN arm (live)

- Config: the **authorized** file state (default `timeout: int = 1200`, sha256 = the
  after hash recorded when the line is applied), the same invocation with **no flags**,
  and a fresh, identically configured set of **8 CPU burners**.
- **GREEN fires iff** the captured full output `after/gate_green_1200.txt` shows every gate
  step reporting `ok` and ends with `pre-push gate GREEN — safe to push (then self-monitor CI).`
  with gate exit code 0. Per-step wall times are recorded (sidecar
  `after/step_times_green_1200.json`, derived from `=== <label> ===` banner timestamps).

### INVARIANT (both arms)

- **I-1 (no bypass)**: the diff between the anchor bytes and the arm's bytes is exactly the
  one authorized line (`changes.diff`, 1 line changed). The gate's E2E command still names
  all 7 `REAL_ROOTS_TESTS` files; no `--skip-*`, `-k`, `--deselect`, or `-x` is ever passed.
- **I-2 (test count / no new skips)**: in any arm where a pytest step completes normally,
  the 7-file E2E step summary must report **`55 passed`** with **`0 skipped`**
  (and no newly introduced `xfail`/`xpass`); any skip appearing where the given evidence
  had none is a RED invariant violation regardless of gate color.
- **I-3 (pre-registered RED caveat, honesty rule)**: if RED manifests as the 600 s kill,
  the killed pytest process cannot emit its final `55 passed` summary — that absence is
  **inherent to the RED condition and is NOT counted as a skip or a lost test-selection**.
  In that case the RED-arm invariant evidence is: (a) the captured gate invocation line
  selecting all 7 files with no skip/deselect flags, (b) the one-line diff proof, (c) the
  given §2.2 light-load `55 passed, 0 skipped` evidence, and (d) the GREEN arm's live
  `55 passed, 0 skipped` report. The RED run's own count is then recorded as
  **"not observable (killed at 600 s)"** — never as "55 passed", never as "0 skipped
  observed live".

## 5. Boundaries

- The only production change is the one authorized line (owner §16-B). No other gate logic
  touched; nothing bypassed; no `--skip-*` flags used.
- This attempt performs NO git commit and NO git push (the parent does those).
- Production repos otherwise READ-ONLY; this attempt writes only inside this attempt
  directory, except (a) the one authorized line in `tools/pre_push_gate.py`, and (b) the
  gate's own normal, documented side effects when it runs unmodified — notably
  `tools/sync_installations.py` may refresh stale installed skill copies under
  `~/.agents`, `~/.claude`, `~/.codex` (the gate auto-syncs installs by design) and pytest
  cache/temp files. Disclosed, not hidden.
- `disclosure_adaptation = unmapped`, `accuracy = unproven` — this card proves a gate
  timeout configuration and its red/green behavior only; it qualifies no formula, no
  disclosure mapping, and no accuracy claim.
- `handoff.json` status must be `review_pending`; the implementer never signs acceptance.

## 6. Capture rules (both arms)

- FULL unfiltered output → `after/gate_red_600.txt` / `after/gate_green_1200.txt`
  (stdout+stderr merged, byte-faithful, via `scripts/timed_gate_run.py`, which only adds
  line-buffering fidelity: the gate is run with python's `-u`; no gate argument is added).
- Burner PIDs, start/stop times → `evidence/burners_red.json` / `evidence/burners_green.json`.
- Per-step wall times → `after/step_times_red_600.json` / `after/step_times_green_1200.json`.
- Command ledger with rc + durations → `commands.json`.
