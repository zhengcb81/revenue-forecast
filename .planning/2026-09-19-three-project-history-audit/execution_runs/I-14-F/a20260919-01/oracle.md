# I-14-F oracle — FROZEN BEFORE ANY RUN (2026-09-19, attempt a20260919-01)

> **ADDENDUM B (frozen before the adjudicating GREEN set; falsifying evidence kept).**
> The §2 criterion constants (260/100 ⇒ threshold 160) were **FALSIFIED** by attempt evidence:
> - `<attempt>\P0-logon_wrapper_quoted-1` (cwd 148, basetemp 155, relocated=false by the old
>   criterion) failed with **literal WinError 206** creating `...\fake-project\company_wiki\source_catalog`
>   (total 253 chars). Historical cmd-A5 (basetemp 147, deepest 245) had passed — so the true
>   boundary on this box is between 245 and 253, not 260.
> - `<attempt>\P0-child_without_runtime-1` (basetemp 156, relocated=false) never spawned a
>   child: the launcher's `Start-Process -RedirectStandardOutput/-Error` paths reach
>   basetemp+124 chars (redirect log ≈ 279 total) and every attempt died before writing a log —
>   23 restarts, no logs, no runtime file. The redirect log path, not the mkdir chain, is the
>   **longest** artifact the suite generates under basetemp: 31 (test dir) + 13 (\fake-project)
>   + 79 (\`.source_catalog\worker_stdout-<32hex>-attempt-0001.log`) = **124 under basetemp**.
> - Controlled envelope on this attempt (same tree, same venv): generated paths ≤ ~200 pass;
>   ≥ 253 fail. cmd-A5's child pass at ~271 while this attempt's child fails at ~279 remains
>   UNEXPLAINED (open question for the reviewer) — the criterion therefore stays strictly
>   inside this attempt's own measured envelope.
> **Recalibrated frozen constants: WIN32_PATH_LIMIT = 240** (between measured pass 200 and
> measured fail 253), **GENERATION_RESERVE = 124** (measured longest artifact), ⇒
> **BASETEMP_MAX_CHARS = 116**. Consequences, all frozen before the adjudicating reruns:
> - E-G2 (no-reroute control) moves to the **boundary probe**: run dir 109, basetemp 116 under
>   `%TEMP%\i14f-normal116\<62-char pad>` ⇒ expect relocated=false **and pass** (validates the
>   no-reroute edge at exactly the threshold).
> - The old NORMAL placement (attempt-root run dirs, basetemp 155/156) is re-labelled
>   **falsified-normal**: expect relocated=true **and pass** (it failed unrouted with 206).
>   The failed rerouted=false runs stay under `after\falsified-normal-r1\`.
> - §4 E-G2 text and §2's correction block describing threshold 160 are superseded by this
>   addendum; nothing else moves. E-G1 (deep) is re-run with the final constants for a
>   coherent after-set; the earlier deep GREEN rows (relocation 174→75) remain valid evidence
>   that relocation mechanics work — the constant change does not affect any placement with
>   basetemp > 160, which all still relocate.
> - §5 unit case table updated to the recalibrated constants (155/156 ⇒ relocate; 116 ⇒ no).

> **ADDENDUM C (final calibration; frozen before the adjudicating after-set).**
> Addendum B's boundary probe (run dir 109, basetemp 116 unrouted) DEGRADED: `logon_wrapper_quoted`
> passed at 115, but `child_without_runtime` ran 19 spawn attempts — children 1–3 executed the
> fake cli (count file = 3), attempts 4–19 never executed (0-byte logs, no runtime), launcher
> looped to the 15 s timeout. No 206/Errno anywhere, but 116-unrouted is demonstrably not clean.
> Final measured envelope for the launcher node family (this attempt, controlled):
> generated-path totals ≤ ~205 → repeatedly clean (I-14-C short 12/12 ≈ 200–205; this attempt
> 76/75-basetemp controls clean); 240 → spawn degradation; 253 → literal WinError 206; 278+ →
> dead spawns. **Final frozen constants: WIN32_PATH_LIMIT = 210, GENERATION_RESERVE = 124, ⇒
> BASETEMP_MAX_CHARS = 86.** 210 respects every measured-clean datapoint (81, 76/75) and stays
> clear of the degradation onset (240). The untested band (total 210–239, i.e. basetemp
> 87–115) is rerouted conservatively — documented as an open gap, not silently blessed.
> - The no-reroute boundary probe moves to: root `%TEMP%\n\ppppppp` (41 chars) ⇒ run dir 68/67,
>   **basetemp 76/75 ≤ 86 ⇒ expect relocated=false AND pass** (exactly the proven envelope).
> - The basetemp-116 probe evidence stays under `%TEMP%\i14f-normal116\` with captures copied
>   to `after\boundary116-captures\` — kept as the Addendum-C falsifier.
> - SHORT control (`%TEMP%\i14f-short-green`, run dirs 75/74, basetemp 82/81): 82 ≤ 86 ⇒
>   expect **relocated=false AND pass** — consistent with the historical clean envelope
>   (I-14-C's own 80/81 control passed 12/12 unrouted).
> - Unit case table updated again to 210/124/86 (155/156/116-edges ⇒ relocate; 86/81/76 ⇒ no).

> **ADDENDUM A (frozen before the adjudicated runs; quarantined env-r1 evidence in
> `before/quarantine-env-r1/`).** Three corrections, all found from failed *setup*, none from
> observing adjudicated results:
> 1. **Interpreter package gap.** The venv initially lacked `requests` (needed by
>    `company_wiki.source_catalog.__init__` → `security_identity`); `logon_wrapper_quoted`
>    failed with `ModuleNotFoundError` at BOTH placements. Fixed by installing the exact
>    I-14-C r5 recorded set: requests 2.34.2, urllib3 2.8.0, certifi 2026.7.22,
>    charset-normalizer 3.5.1, idna 3.20. The iso venv is otherwise unchanged.
> 2. **SHORT-control length arithmetic.** §1 predicted cwd_len 74/72 for `%TEMP%\i14f-short`;
>    correct value is **69/68** (root = 31+11 = 42 chars). The criterion ("≪160 ⇒ no
>    relocation ⇒ pass") is unaffected.
> 3. **Parallel-load contamination.** The first SHORT control ran concurrently with the DEEP
>    runs; `child_without_runtime` hit the 15 s launcher timeout under that load — the known
>    I-14-E band, self-inflicted. All adjudicated phases run strictly sequentially; the
>    contaminated runs are quarantined unadjudicated.

Nothing below is derived from running the fix; expected values come from (a) the frozen
I-14-C r5 observations (review.md §4a, 12 deep runs + 12 short controls, captured per run)
and (b) hand-measured path lengths of this attempt. The implementation must meet these
expectations; expectations are not adjusted to fit the implementation.

## 0. Fixed inputs

- Suite file: `tests/contract/test_source_catalog_worker_bootstrap.py` (company-wiki HEAD
  f39bd5a64224cd0c7aa098f23f64bf3811fa8939, isolated copy `<attempt>\iso\tree`).
- Nodes (exactly the two I-14-C §4a nodes):
  - `child_without_runtime` = `test_child_without_runtime_session_is_terminated_and_restarted`
  - `logon_wrapper_quoted`  = `test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths`
- Per-run argv (identical shape to the frozen I-14-C driver):
  `<iso-python> -X utf8 -B -m pytest -p no:cacheprovider --basetemp <run_dir>\pytest -q <tree>\tests\contract\test_source_catalog_worker_bootstrap.py::<node>`
  with cwd=`<run_dir>` and the stripped env of the I-14-C driver (`PYTHONPATH=<tree>\src` etc.).
- Basetemp discipline: `<run_dir>\pytest` is a newly created empty dir for THIS run only;
  never the attempt root, never an evidence root, never a previous run's dir.
- rc legend (frozen START_HERE table): 0 = pass, 1 = test/harness failure, 2 = no verdict /
  correctly refused negative, 3 = positive failed / negative not rejected.

## 1. Placement geometry (hand-measured, asserted by the driver guard)

`%TEMP%` on this machine = `C:\Users\郑曾波\AppData\Local\Temp` (31 chars; consistent with the
I-14-C §4a short-control cwd lens 74/75). Attempt root length = 122 chars.

| placement | run-dir root | expected cwd_len child | expected cwd_len logon |
|---|---|---|---|
| DEEP (before/after) | `<attempt>\before\deep\pad55` resp. `<attempt>\after\deep\pad666` (both 140 chars) | **167** | **166** |
| SHORT control | `%TEMP%\i14f-short` | 69 (Addendum A) | 68 (Addendum A) |
| NORMAL control | `<attempt>\after\normal` (137 chars) | 164 | 163 |
| OVER-DEEP negative | `<attempt>\after\over-deep\<200-char pad>` | > 380 | > 380 |
| MUTATION A/B | `%TEMP%\i14f-mutation-deep\<pad to 140 chars>` | 167 | 166 |

The child/logon tags are `P0-<node>-<run>`; child tag is 26 chars, logon tag 25 chars, hence
the 1-char difference in cwd_len. DEEP reproduces the exact 167/166 lens of the frozen I-14-C
deep observation. The driver prints `cwd_len` per run and is flagged `--require-cwd-len`; a
mismatch aborts the phase (no silent geometry drift).

## 2. Decision criterion (frozen numbers, to be implemented in the tree's root conftest.py)

- `WIN32_PATH_LIMIT = 260` (classic Win32 MAX_PATH budget for non-`\\?\` consumers such as
  `powershell.exe` and `os.mkdir` on this box).
- `GENERATION_RESERVE = 100` — measured deepest suffix the suite generates under basetemp:
  pytest test dir name (max 31: `test_logon_wrapper_detaches_a_0`) + `\project path with spaces`
  (24) + `\fake-project` (12) + `\company_wiki\source_catalog` (27) + separators ⇒ 97; +3 margin ⇒ 100.
- `BASETEMP_MAX_CHARS = WIN32_PATH_LIMIT - GENERATION_RESERVE = 160`.
- relocate iff `len(resolved_basetemp) + GENERATION_RESERVE > WIN32_PATH_LIMIT`, where
  `resolved_basetemp = basetemp` if absolute else `cwd\basetemp` (cwd participates through
  resolution of relative basetemps; an explicit short absolute basetemp under a deep cwd needs
  no relocation and must not get one).
- fallback root: `%TEMP%\cw-pytest-basetemp\<UTCstamp>-<8hex>` — a fresh empty dir created per
  relocating session; removed (rmtree) in `pytest_unconfigure`, only the dir this session created.
- Opt-out for the mutation A/B: env `CW_SHORT_BASETEMP_DISABLE=1` makes the hook print the
  decision (`relocated=false`, reason `disabled`) and do nothing else.
- Calibration against all four frozen datapoints (must hold):
  - I-14-C deep: basetemp 173/174 chars ⇒ 174+100=274 > 260 ⇒ relocate (was: fail).
  - I-14-C short control: basetemp ≈ 81/80 ⇒ ≪ 260 ⇒ no reroute (passed then; must stay pass).
  - I-14-C cmd-A5 historical full-suite run: basetemp 147 ⇒ 247 ≤ 260 ⇒ no reroute (passed).
  - NORMAL control here: basetemp 171 ⇒ 171+100 = 271 > 260 ⇒ relocates.
- PRE-RUN CORRECTION (frozen before any run; no expectation was edited after seeing results):
  an `<attempt>\after\normal`-rooted control is NOT a valid "no needless reroute" case — its
  basetemp (171) genuinely exceeds the 160 budget, real generated depth 171+97 = 268 > 260, so
  relocation there is correct behaviour. The NORMAL (no-relocate) control therefore uses run
  dirs directly under the attempt root: `<attempt>\P0-<node>-<run>` ⇒ child run dir 149,
  **basetemp 156 ≤ 160 ⇒ no relocate**, real generated depth 156+97 = 253 ≤ 260 (safe, like the
  historical cmd-A5 247). The `<attempt>\after\normal` placement is kept as an extra data point
  labelled `boundary-normal` with **expected relocate=true AND pass** (the convention catches a
  genuinely-too-deep, historically-untested placement without anyone shortening cwd).
- The over-deep negative case: cwd > 380 chars, basetemp = run_dir\pytest ⇒ relocate ⇒ pass.
- A deep cwd with a SHORT explicit basetemp must pass WITHOUT relocation — this is exactly
  what the DEEP-after runs prove (cwd stays 167/166; basetemp relocated to %TEMP%).

## 3. RED expectations — tree WITHOUT the convention (pre-implementation)

- E-R1 DEEP, `{child_without_runtime, logon_wrapper_quoted}` × runs {1,2,3} (fresh dirs):
  every run **rc=1**. Failure signatures (frozen from I-14-C §4a captures):
  - `logon_wrapper_quoted`: traceback containing `WinError 206` (文件名或扩展名太长) raised from
    `os.mkdir`/`pathlib.mkdir` while creating `...\project path with spaces\fake-project\company_wiki...`.
  - `child_without_runtime`: `FileNotFoundError` — either the literal `[WinError 206]` inside
    the launcher spawn or `[Errno 2] ...worker_launcher_events.jsonl` (the launcher died before
    writing events; same deep-path family, exactly as captured in I-14-C T4 evidence).
  - Acceptance of E-R1: 6/6 runs rc=1; `WinError 206` text appears in at least the logon runs
    (3/3); child runs fail with one of the two frozen signatures (record which).
- E-R2 SHORT control, both nodes × run 1: **rc=0 each** (tree healthy at short placement —
  proves the RED is placement-caused, not tree-caused).
- No `CW-BASETEMP-DECISION` line exists anywhere in RED outputs (convention not implemented yet).

## 4. GREEN expectations — same tree + root `conftest.py` + criterion unit tests

- E-G1 DEEP, both nodes × runs {1,2,3} (fresh dirs, cwd_len re-asserted 167/166): every run
  **rc=0**, stdout contains a `CW-BASETEMP-DECISION {...}` line with `"relocated": true`,
  `requested_basetemp_len` ∈ {173, 174}, and an effective basetemp under
  `%TEMP%\cw-pytest-basetemp\`. No `WinError 206` / `Errno 2 ... worker_launcher_events`
  anywhere. Exit condition of the card: deep cwd no longer produces 206, without moving cwd.
- E-G2 NORMAL (attempt-root run dirs): both nodes × run 1 → rc=0 with
  `"relocated": false` (no needless reroute; behavior identical to pre-convention normal runs).
- E-G3 SHORT control (fresh dirs): both nodes × run 1 → rc=0, `"relocated": false`.
- E-G4 OVER-DEEP negative: both nodes × run 1 → rc=0, `"relocated": true` (the convention
  catches a deliberately over-deep cwd and the nodes succeed).
- E-G5 boundary-normal (`<attempt>\after\normal`): both nodes × run 1 → rc=0,
  `"relocated": true` (a genuinely too-deep placement is caught, not silently passed).
- E-G6 unit tests: `<tree>\tests\contract\test_short_basetemp_convention.py` → rc=0. Frozen
  case table (criterion function, pure):
  | requested basetemp | cwd | expected relocate |
  |---|---|---|
  | 174-char absolute | 167-char cwd | true |
  | 156-char absolute | 149-char cwd | false |
  | 90-char absolute | 74-char cwd | false |
  | relative `pytest` | 357-char cwd | true (364 resolved) |
  | relative `pytest` | 100-char cwd | false |
  plus: `BASETEMP_MAX_CHARS == 160 == 260-100`; fallback dirs are fresh & unique per call;
  disable-env branch reports `reason=disabled`.
- E-G7 cleanup: for every relocating session (E-G1/G4/G5), the created fallback dir is removed
  by session end — `CW-BASETEMP-CLEANUP removed=1` (or path=…) present in stdout and the
  `%TEMP%\cw-pytest-basetemp\<id>` path no longer exists after the driver returns.

## 5. MUTATION proof (active-ingredient check)

- E-M1: identical DEEP geometry, tree WITH the convention, env `CW_SHORT_BASETEMP_DISABLE=1`,
  both nodes × run 1 → **rc=1** again with the frozen deep-path signatures (§3). This proves
  the convention itself (not tree drift, not interpreter drift, not cwd change) turns RED into
  GREEN: same tree, same cwd, only the convention toggled.

## 6. Flakes (frozen handling)

`child_without_runtime`/`logon_wrapper_quoted` carry a known ~25% load-dependent flake band
(I-14-E, out of scope here). Controls (E-R2/E-G2/E-G3) are single-run; if such a control fails
with an assertion-level (non-path) signature, rerun ONCE with a fresh run dir and keep BOTH
outputs; only path-length signatures adjudicate this card.

## 7. Exit / recovery (card text)

- Exit: E-G1..G7 + E-M1 hold ⇒ deep cwd no longer shows 206; normal/short behavior unchanged.
- Recovery: revert = delete `<tree>\conftest.py` + `tests\contract\test_short_basetemp_convention.py`
  (the only added files); RED observations (§3) and I-14-C's 166/167 + 74/75 datapoints stay on file.
- Boundary declaration: `disclosure_adaptation = unmapped`, `accuracy = unproven` (this card
  earns test-infrastructure qualification only). Reviewer, not implementer, signs acceptance.
