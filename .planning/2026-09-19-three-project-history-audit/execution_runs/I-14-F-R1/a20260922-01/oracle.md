# I-14-F-R1 oracle — FROZEN BEFORE ANY RUN (2026-09-22, attempt a20260922-01)

> Freeze discipline: this file is written and its sha256 pinned in `oracle.sha256` BEFORE the
> unit suite, RED, GREEN, mutation, or sweep is run. Expectations below come from (a) the owner
> ruling, (b) I-14-F's sealed attempt + its independent reviewer's measurements, (c) hand
> arithmetic verified by `harness/check_lengths.py` — never from observing this attempt's runs.
> Structurally append-only afterwards (owner discipline T1-12 / §16 family: new sections only,
> each naming the line(s) it supersedes).

## 0. Owner ruling this card applies (verbatim, not second-guessed)

`OWNER_DECISIONS.md` §16 (原话): 「… E-1: 150/60 …」, ruling row: **E-1 = 150/60** →
`GENERATION_RESERVE = 150` ⇒ threshold **60**; relation-to-recommendation recorded there as
「**不同于建议**（建议为保留 86+修文档；owner 选更保守的全线重定位）」— the conservative-reroute
option, **overriding** the orchestrator's contrary recommendation. Consequences of the choice
are stated explicitly in §2/§3 (no silent flips).

## 1. Fixed inputs

- Ruling: `GENERATION_RESERVE = 150`, threshold derived `> 60`; `WIN32_PATH_LIMIT = 210` unchanged.
- Trees (both under `<attempt>\iso`):
  - **green** `iso\tree` — copy of I-14-F's iso\tree (pre-edit hashes verified:
    conftest.py `c22be9f3…`, unit test `b0402b56…`), then EDITED here per E-1.
  - **red** `iso\red-tree` — same copy minus `conftest.py` + the unit test = pristine CW HEAD
    (anchors re-verified against I-14-F binding.json: worker.py `e8317991…`, bootstrap suite
    `32515aa6…`, control.py `553a3560…` — all True). Production never touched.
- Nodes (exactly the two I-14-C/I-14-F nodes):
  - `child_without_runtime` = `test_child_without_runtime_session_is_terminated_and_restarted`
  - `logon_wrapper_quoted`  = `test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths`
- Per-run argv (same shape as I-14-C r5 / I-14-F):
  `<iso-python> -X utf8 -B -m pytest -p no:cacheprovider --basetemp <basetemp> -q
  <tree>\tests\contract\test_source_catalog_worker_bootstrap.py::<node>`, cwd = run_dir,
  stripped env + `CW_BASETEMP_DECISION_FILE`. Driver: `harness\run_placement.py`
  (adapted from I-14-F's; adds `--target-root-len` and `--basetemp-len`, records argv/cwd).
- Deep geometry (frozen): padded root of **exactly 140 chars** ⇒ cwd **166 (logon) / 167 (child)**,
  basetemp `<run_dir>\pytest` = **173/174**. Driver asserts via `--require-cwd-len
  child_without_runtime=167,logon_wrapper_quoted=166` (mismatch ⇒ rc 97, no silent drift).
- rc legend (START_HERE): 0 = pass, 1 = test/harness failure, 2 = no verdict/negative accepted,
  3 = negative not rejected, 97 = driver geometry guard.
- `%TEMP%` = `C:\Users\郑曾波\AppData\Local\Temp` (31 chars); attempt root = **125 chars**.
- Sequential only; no parallel phases (Addendum-A lesson from I-14-F).

## 2. Criterion as applied (150/60)

```
WIN32_PATH_LIMIT   = 210
GENERATION_RESERVE = 150   (owner §16 E-1)
BASETEMP_MAX_CHARS = 210 − 150 = 60
relocate  iff  len(resolved_basetemp) + 150 > 210   ⇔   len(resolved_basetemp) > 60
resolved_basetemp = basetemp (absolute)  |  cwd\basetemp (relative)
```

True reserve figures **as measured by I-14-F's independent reviewer** (R-1 / CF-I14F-1), which
the corrected docstring must state:

| node | longest generated suffix under basetemp | measured at |
|---|---|---|
| `logon_wrapper_quoted` | **150** = 31 (`test_logon_wrapper_detaches_a_0`) + 24 (`\project path with spaces`) + 12 (`\fake-project`) + 15 (`\.source_catalog`) + 63 (`\worker_stdout-<32hex>-attempt-0001.log`) + 5 separators | basetemps 74 and 81, both **passing unrouted** runs |
| `child_without_runtime` | **125** (`\test_child_without_runtime_ses0\fake-project\.source_catalog\worker_stderr-<32hex>-attempt-NNNN.log`) | basetemps 75, 116, 174 (three independent placements) |

The old docstring arithmetic was wrong twice over: `31 + 13 + 79 = 123 ≠ 124` (internally
inconsistent), and it described only the child node while omitting the logon node's extra
`\project path with spaces` level. With reserve 150 the criterion covers BOTH nodes (125 ≤ 150).

## 3. THREE FROZEN INVARIANTS (the design consequences of 150/60 — stated, not silent)

**INV-1 — the boundary pair moves from 86/87 to 60/61.**
- basetemp 60 → 60+150 = **210** → `relocated=false` (within budget, NOT > 210).
- basetemp 61 → 61+150 = **211** → `relocated=true`.
- BOTH sides must be pinned by unit tests (`BOUNDARY 60` / `BOUNDARY 61` cases) AND exercised
  by the integration sweep (§8 sizes 60 and 61). This also closes I-14-F F-5's
  "unpinned boundary" defect for the new threshold.

**INV-2 — basetemps 61–86 now relocate; every recorded no-reroute control in that band flips
EXPLICITLY with a written reason.**
- I-14-F's recorded no-reroute controls at basetemps **69/68, 76/75, 82/81** previously asserted
  `relocated=false`; under 150/60 they WILL relocate (`69>60, 68>60, 76>60, 75>60, 82>60, 81>60`).
- Required flip text (verbatim reason, wherever the flip is recorded):
  **"owner §16 E-1 chose 150/60; this control's unrouted expectation is superseded"** —
  never a silent change.
- The reviewer's third no-reroute datapoint (52-char basetemp) stays `relocated=false`
  (52 ≤ 60) — it does NOT flip; recorded here so a false flip is detectable.
- Unit-case expectation flips frozen in advance (all under the same written reason):
  - case resolved **84** : false → **true**
  - case resolved **82** : false → **true**
  - case resolved **78** (relative, short cwd): false → **true**
  - `decide()` short dir **64**: false → **true** (and a new 44-char dir pins the
    within-budget branch, so the false-branch keeps coverage)
  - cases resolved 174 / 154 / 119 / 360: unchanged **true**
  - `decide()` deep dir 204: unchanged true; disabled / no-explicit branches unchanged
  - hook within-budget basetemp 58 (58 ≤ 60): unchanged **false** (2 chars of margin — comment
    must say so)

**INV-3 — the thin margin becomes STRUCTURAL.**
- Under 150/60 every unrelocated placement satisfies `len(resolved) ≤ 60` by construction, so
  every generated total ≤ **60 + 150 = 210** for the logon node (worst case) and ≤ 60 + 125 = 185
  for the child node. The old nominal claim (86 + 124 = 210) was false for the logon node, which
  actually generated up to 86 + 150 = **236** unrouted.
- The previously untested logon band 232–236 (basetemps 82–86 unrouted) is therefore **moot**:
  those sizes now relocate. This attempt must VERIFY (§8) that basetemps 82 and 86 relocate and
  pass — not merely assert it.

## 4. E-U unit/criterion suite (expected BEFORE running)

`<green>\tests\contract\test_short_basetemp_convention.py` → rc 0, **15 passed**.

Frozen composition (the original 13 retained + 2 boundary pins added):

| # | test | expected |
|---|---|---|
| 1 | `test_constants_match_the_frozen_budget` | 210 / **150** / **60** (was 210/124/86) |
| 2–10 | `test_criterion_table` (9 cases; lengths verified by `harness/check_lengths.py`) | cwd 163 / resolved **174** → true; cwd 143 / **154** → true; cwd 108 / **119** → true; cwd 49 / **60** → **false (BOUNDARY-1, INV-1)**; cwd 50 / **61** → **true (BOUNDARY-2, INV-1)**; cwd 73 / **84** → true (FLIP, INV-2); cwd 71 / **82** → true (FLIP, INV-2); cwd 353 / **360** relative → true; cwd 71 / **78** relative → true (FLIP, INV-2) |
| 11 | `test_relative_basetemp_resolution_uses_cwd` | unchanged |
| 12 | `test_decide_reports_lengths_and_reasons` | 64-char dir → **true (FLIP, INV-2, written reason in comment)**; new 44-char dir → false (within-budget branch retained); 204-char dir → true; disabled → `disabled-by-env`; None → `no-explicit-basetemp` |
| 13 | `test_fallback_dirs_are_fresh_and_unique` | unchanged |
| 14 | `test_configure_hook_rewrites_option_and_cleans_up` | unchanged (272-char basetemp → relocate + cleanup removed=true) |
| 15 | `test_configure_hook_within_budget_never_reroutes` | unchanged outcome: 58-char basetemp → false (comment corrected: 58 ≤ 60, margin 2) |

Also frozen as part of F-5's fix: every case-table comment states the REAL constructed length
(174, 154, 119, 60, 61, 84, 82, 360, 78) — the reviewer-measured values that exposed I-14-F's
4 misstated comments.

## 5. E-R RED (pristine tree, deep geometry) — frozen expectations

- Tree: `iso\red-tree` (NO conftest), deep root (driver-padded to exactly 140), runs {1,2,3} ×
  {child, logon} = **6 runs**.
- Expect **6/6 rc=1**; signatures frozen from I-14-C §4a / I-14-F:
  - `logon_wrapper_quoted`: literal `WinError 206` (expected 3/3) raised from mkdir while
    creating `...\project path with spaces\fake-project\company_wiki...`.
  - `child_without_runtime`: path-family — `FileNotFoundError` with literal `[WinError 206]` or
    `[Errno 2] … worker_launcher_events.jsonl`.
  - **Pre-registered surface-noise rule (CF-I14F-X1 / reviewer §3):** if a child run surfaces as
    `timeout15s-band` instead, the run stays rc=1 and is adjudicated at ARTIFACT level from the
    surviving unrelocated basetemp (RED does not relocate, so artifacts persist): the deep chain
    `...\source_catalog` / `worker_launcher*` must exist beyond the ~248/~260 measured edges or
    the deepest created entries must sit at the measured fail band ⇒ path-caused. Band labels
    alone never adjudicate.
- No `CW-BASETEMP-DECISION` line may appear in any RED output (no conftest in the tree).
- Geometry guard must pass (cwd 166/167, basetemp 173/174) for all 6.

## 6. E-G GREEN (green tree with 150/60 conftest, same deep geometry) — frozen expectations

- Runs {1,2,3} × {child, logon} = 6 runs, fresh dirs, guard re-asserted 166/167.
- **Adjudicating expectation: both nodes `relocated=true` in 6/6**, decision line
  `"generation_reserve": 150, "threshold": 60`, `requested_basetemp_len` ∈ {173,174}, effective
  basetemp under `%TEMP%\cw-pytest-basetemp\`, `cleanup removed=true`, **zero path-family
  signatures** (no `WinError 206` / `Errno 2 … worker_launcher_events`) anywhere.
- Pass expectation: `logon_wrapper_quoted` **3/3 rc=0**. `child_without_runtime` **rc=0 expected**
  but it carries the I-14-E load band (frozen handling, oracle §6 lineage): `timeout15s-band` /
  `restart-band` / `launcher-rc1-quiet` are **non-adjudicating**; if hit, rerun ONCE with a fresh
  run dir and keep BOTH outputs. The child's GREEN for THIS card is `relocated=true + no
  path-family signature`; a clean rc=0 pass is recorded when the load allows (R-2 from I-14-F
  stays open and is NOT re-argued here).

## 7. E-M MUTATION (active ingredient) — frozen expectations

- Same green tree, same deep geometry, env `CW_SHORT_BASETEMP_DISABLE=1`,
  runs {1} × {child, logon} = 2 runs (E-M1 shape from I-14-F oracle §5).
- Expect **2/2 rc=1**, `relocated=false`, `reason=disabled-by-env`, with the frozen deep-path
  signatures: logon = literal `WinError 206`; child = path-family (artifact-adjudication rule
  of §5 applies — disabled sessions do NOT relocate and do NOT clean up, so the deep basetemp
  artifacts survive for measurement).
- Same tree, same cwd, only the convention toggled ⇒ RED→GREEN is attributable to the convention.

## 8. E-S SIZE SWEEP (logon node; basetemp length is the only variable) — frozen expectations

Driver mode `--basetemp-len N`: absolute basetemp `%TEMP%\cwR1bt<pad>` of EXACT length N (guard
asserts the length, rc 97 on mismatch), cwd = short run dir under `%TEMP%\i14fr1sz`
(captures + decision json copied back to `after\sizes\caps\`), fresh basetemp per run.

| basetemp len N | N+150 | expected relocated | expected rc | note |
|---|---|---|---|---|
| 40 | 190 | **false** (unrelocated) | 0 (pass expected) | adjudicated expectation = stays unrelocated |
| **60** | 210 | **false** (unrelocated) | 0 (pass expected) | **INV-1 boundary lower half** |
| **61** | 211 | **true** | 0 (pass) | **INV-1 boundary upper half** |
| 69 | 219 | **true** | 0 (pass) | flip datapoint: I-14-F control 69/68 (INV-2) |
| 76 | 226 | **true** | 0 (pass) | flip datapoint: I-14-F control 76/75 (INV-2) |
| 82 | 232 | **true** | 0 (pass) | flip datapoint: I-14-F control 82/81 (INV-2); old untested band |
| 86 | 236 | **true** | 0 (pass) | old boundary max; old untested band (INV-3 moot) |

- Flip reason recorded with every flipped control: **"owner §16 E-1 chose 150/60; this control's
  unrouted expectation is superseded"**.
- `child_without_runtime` is NOT part of the sweep (its load band would confound "AND pass";
  the child node is exercised at deep geometry in §5–§7 instead). Recorded as scope, not omission.
- Load-band handling: same frozen §6 rule; a band failure on a relocated size reruns once with a
  fresh dir, both outputs kept.

## 9. Flakes (frozen handling, inherited)

`child_without_runtime` carries the known ~25% load-dependent restart band (I-14-E, out of
scope). Only path-length signatures adjudicate this card (frozen rule, I-14-F oracle §6).
Controls/sweep failures with assertion-level (non-path) signatures rerun ONCE, fresh dir, both
outputs kept. A `timeout15s-band` label alone never adjudicates (CF-I14F-X1).

## 10. Boundaries / exit

- Exit: §4–§8 all hold ⇒ 150/60 applied, boundary pinned, RED reproduced, GREEN relocated+
  passes, mutation fails both nodes frozen-signature, sweep table as above.
- Recovery: revert = restore I-14-F's conftest/test hashes (`c22be9f3…`/`b0402b56…`) or delete
  the two files; I-14-F's sealed attempt and production are untouched either way.
- `disclosure_adaptation = unmapped`, `accuracy = unproven`; test-infrastructure only;
  promotion separate; reviewer (not implementer) signs; handoff stays `review_pending`.
