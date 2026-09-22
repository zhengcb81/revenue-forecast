# I-14-F-R1 decision — applying owner §16 E-1 (150/60) to the short-basetemp convention

- Card: **I-14-F-R1** (follow-up / calibration correction card of I-14-F)
- Attempt: `a20260922-01` (`<PLAN>\execution_runs\I-14-F-R1\a20260922-01`)
- Authorization: `OWNER_DECISIONS.md` §16, verbatim: 「**E-1: 150/60**」 —
  `GENERATION_RESERVE = 150` ⇒ relocate threshold **60**. Ruling-row note recorded by the
  owner sheet: 「**不同于建议**（建议为保留 86+修文档；owner 选更保守的全线重定位）」 — this is the
  **conservative-reroute option overriding the orchestrator's contrary recommendation**; it is
  adopted verbatim and not second-guessed.
- Input evidence (read-only): I-14-F `a20260919-01` — sealed/accepted; its
  `reviewer_report.md` (R-1/CF-I14F-1 measurements) and `handoff.json` (CF-I14F-1..8, X1).
- Oracle: `oracle.md`, sha256-pinned in `oracle.sha256` at **2026-09-22T08:35:44+01:00**,
  BEFORE any run of this attempt (first run artifact is the unit suite, later that morning).

## 1. Applied threshold logic (report item 1)

```
WIN32_PATH_LIMIT   = 210                       (unchanged; empirical envelope)
GENERATION_RESERVE = 150                       (owner §16 E-1; was 124)
BASETEMP_MAX_CHARS = 210 − 150 = 60
relocate  iff  len(resolved_basetemp) + 150 > 210   ⇔   len(resolved_basetemp) > 60
```

Applied in `<attempt>\iso\tree\conftest.py` (the isolated copy; production untouched,
promotion is a separate ungranted step). Decision records emitted by every session now carry
`"generation_reserve": 150, "threshold": 60`.

### Corrected doc figures (as measured by I-14-F's independent reviewer, R-1 / CF-I14F-1)

The docstring was rewritten to state the true figures:

| figure | old (wrong) | true (measured) |
|---|---|---|
| reserve derivation | `31 + 13 + 79 = 124` | arithmetic itself wrong: `31 + 13 + 79 = **123**, not 124`; and it described only the **child** node |
| logon node suffix | omitted entirely | **150** = 31 (`test_logon_wrapper_detaches_a_0`) + 24 (`\project path with spaces`) + 12 (`\fake-project`) + 15 (`\.source_catalog`) + 63 (`\worker_stdout-<32hex>-attempt-0001.log`) + 5 separators — measured on two **passing unrouted** runs (basetemps 74, 81) |
| child node suffix | 124 | **125** (basetemps 75, 116, 174) |
| old unrouted max | "210" / "clear of 240" | logon actually generated up to **236** unrouted (86 + 150); headroom was 4–5 chars, not ~30 |
| new unrouted max | — | **structural**: any unrelocated placement has `len ≤ 60` by construction ⇒ generated total ≤ 60 + 150 = **210** (logon, worst case) and ≤ 60 + 125 = 185 (child) |

Also corrected in the same docstring: Addendum-C's claim that "total 210–239 ⇒ rerouted
conservatively" was **false for the logon node** under the old constants (basetemps 87–115 were
rerouted, but 82–86 were not, producing 232–236 totals). Under 150/60 that whole band relocates.

## 2. The three frozen design consequences (oracle INV-1..3) — stated, never silent

1. **Boundary moved 86/87 → 60/61** (INV-1): 60 → 60+150 = 210 ⇒ unrelocated;
   61 → 61+150 = 211 ⇒ relocated. **Both halves pinned** twice:
   - unit: `test_criterion_table` cases resolved **60 → False** and **61 → True** (plus the
     `BASETEMP_MAX_CHARS == 60` constant pin) — this closes I-14-F F-5's "unpinned boundary"
     for the new threshold;
   - integration: sweep sizes **60 → relocated=false** and **61 → relocated=true** (§5 below).
2. **Basetemps 61–86 relocate; recorded controls flip EXPLICITLY** (INV-2) — see the
   control-flip list in §4 with the verbatim written reason.
3. **Thin margin becomes structural** (INV-3): every unrelocated generated total ≤ 210 by
   construction (was: nominal 86+124=210 but the logon node really ran to 236). The old
   untested 232–236 band is moot — and was verified to relocate and pass (sizes 82, 86).

## 3. What changed in the tree (vs I-14-F's sealed files)

Two files only (same shape as I-14-F; `changes.diff` is an all-additions diff against the
pristine `iso\red-tree`):

1. `iso\tree\conftest.py` — constants 210/124/86 → **210/150/60**; docstring rewritten per §1
   (true figures, calibration history through E-1, structural-margin statement, boundary pair,
   flip reason). Runtime logic **unchanged** (same criterion function, fallback, cleanup,
   decision/cleanup records, opt-out env).
2. `iso\tree\tests\contract\test_short_basetemp_convention.py` — **13 → 15 tests**:
   - constants test → 210/150/60;
   - criterion table grows to 9 cases: original 7 retained with **3 explicit expectation flips**
     (resolved 84, 82, 78: false → true) and **2 boundary pins added** (60, 61); every comment
     now states the REAL constructed length (174, 154, 119, 60, 61, 84, 82, 360, 78) — fixing
     F-5's 4 misstated comments directly;
   - `test_decide…`: the 64-char dir flips false → true (written reason inline) and a 44-char
     dir retains within-budget branch coverage; asserts 64/44/204 lengths;
   - hook within-budget test keeps its 58-char basetemp (58 ≤ 60, margin stated) with a
     threshold-relative assert.

   Every flip carries the inline written reason: **"owner §16 E-1 chose 150/60; this control's
   unrouted expectation is superseded."**

Note on suite count: the card says "the 13 unit/criterion tests (expect boundary 60/61
pinned)". The original 13 are all retained (3 expectations flipped with written reasons, 4
comments corrected); pinning BOTH boundary halves adds 2 cases ⇒ **15 tests**, all passing
(adjudicating run `after\unit-run3\stdout.txt`: `15 passed`, rc 0). The two earlier unit-run
failures are kept and explained in §6 (both were this attempt's own test-construction/setup
defects, not criterion failures).

## 4. Control-flip list (INV-2) — every recorded expectation that 150/60 reverses

Written reason for each flip (verbatim, required wherever recorded):
**"owner §16 E-1 chose 150/60; this control's unrouted expectation is superseded."**

| recorded control / case (source) | basetemp len | old expected relocated | new expected relocated | flip? | evidence here |
|---|---|---|---|---|---|
| I-14-F control pair 69/68 | 69, 68 | false | **true** | YES (reason above) | 69 swept (relocated+pass); 68 by criterion (unit, pure) |
| I-14-F control pair 76/75 (E-G2 boundary probe) | 76, 75 | false | **true** | YES | 76 swept; 75 by criterion |
| I-14-F control pair 82/81 (SHORT control) | 82, 81 | false | **true** | YES | 82 swept; 81 by criterion |
| I-14-F old boundary max | 86 | false | **true** | YES | 86 swept (relocated+pass) |
| I-14-F old boundary upper | 87 | true | true | no | subsumed by new boundary |
| unit criterion case (resolved 84) | 84 | false | **true** | YES | unit case flipped, inline reason |
| unit criterion case (resolved 82) | 82 | false | **true** | YES | unit case flipped, inline reason |
| unit criterion case (resolved 78, relative) | 78 | false | **true** | YES | unit case flipped, inline reason |
| `decide()` synthetic dir (64 chars) | 64 | false | **true** | YES | unit case flipped, inline reason |
| reviewer's 3rd no-reroute datapoint (unit-run1, 52-char basetemp) | 52 | false | false | **NO — must not flip** (52 ≤ 60) | by criterion; deliberately NOT flipped |
| NEW boundary lower / upper | 60 / 61 | — | false / true | pinned fresh | unit + sweep (both halves) |

## 5. Run results (all phases; full rows with argv/cwd in `commands.json`)

| phase | runs | result vs oracle |
|---|---|---|
| **E-U unit** (`after\unit-run3`) | 15 tests | **15 passed, rc 0** — boundary 60/61 pinned; constants 210/150/60 (oracle §4) ✓ |
| **E-R RED** (pristine `iso\red-tree`, cwd 166/167, basetemp 173/174) | 6 | **6/6 rc=1**; logon **3/3 literal WinError 206**; child run1 frozen `FileNotFound-launcher-events`, runs 2/3 surfaced `timeout15s-band` and were **artifact-adjudicated path-caused** (`before\artifact-measure\red-child-artifacts.txt`: lock 256 + cli.py 254 created, `worker_launcher_events.jsonl` ~**264** ≥ file edge 260 missing, 0 worker logs); **zero** `CW-BASETEMP-DECISION` lines; geometry guard 6/6 ✓ (oracle §5) |
| **E-G GREEN** (150/60 tree, same geometry) | 6 + 1 rerun | **relocated=true 7/7**; `generation_reserve=150, threshold=60` in every decision; `cleanup removed=true` 7/7; **logon 3/3 rc=0 pass**; **zero path-family signatures**; child 3×`timeout15s-band` (non-adjudicating per oracle §9) → ONCE-rerun kept alongside (`after\deep-rerun\`), rerun also `timeout15s-band` but on the **relocated 75-char** `-ProjectRoot` (short paths ⇒ load-caused, R-2/I-14-E scope) (oracle §6) ✓ |
| **E-M MUTATION** (`CW_SHORT_BASETEMP_DISABLE=1`, same geometry) | 2 | **2/2 rc=1**, `relocated=false`, `reason=disabled-by-env`; logon **literal WinError 206**; child `timeout15s-band` surface → artifact-adjudicated **path-caused** (`after\mut\child-artifacts.txt`: same 264-char unreachable events file; disabled ⇒ no cleanup ⇒ artifacts survived as pre-registered) (oracle §7) ✓ |
| **E-S SIZE SWEEP** (logon; absolute basetemp of exact length; short cwd; length guard) | 7 | **40 → false, 60 → false (both rc=0 pass)**; **61, 69, 76, 82, 86 → true, all rc=0 pass**; every `guard_ok` (exact N-char basetemp). Matches oracle §8 table **7/7** ✓ |

Guard summary: 22/22 placement rows `guard_ok=true` (deep cwd guard 166/167; sweep
basetemp-length guard); no rc 97 anywhere.

## 6. Process anomalies of THIS attempt (retained, not hidden)

1. `after\unit-run1` (rc 1): 11 passed + 4 setup errors — my invocation deleted the basetemp's
   *parent* dir and pytest `mkdir`s the explicit basetemp without `parents=True`. Harness-invocation
   defect, not a suite defect; the capture is kept.
2. `after\unit-run2` (rc 1): 14 passed + 1 failed — my new `decide()` case constructed
   `Path("C:\")/"s"*60` expecting 64 chars; pathlib joins without an extra separator ⇒ 63.
   Because the **oracle had frozen 64/44/204**, the test *construction* was corrected (names
   61/41/201) to realize the frozen lengths — oracle expectations were NOT changed to fit the
   run. Capture kept; adjudicating run is `unit-run3` (15 passed).
3. `harness\check_lengths.py`: the pre-freeze script's decide()-dir arithmetic used
   `3+1+len(name)`; correct pathlib length is `3+len(name)`. All criterion-table values
   (which drove oracle §2/§4) were string concatenation and correct; the script was corrected
   post-freeze with an inline comment marking the correction (oracle untouched — append-only).

## 7. ERRATA REGISTRY (append-only) — I-14-F's sealed doc defects NOT fixable here

I-14-F `a20260919-01` is sealed/accepted: its `decision.md`, `oracle.md`, `handoff.json` and
`commands.json` bodies were never written by this attempt (byte-verified unchanged in
`after\readonly-check.txt`). The following defects in those frozen bodies are registered here
as **errata**, each citing its carried-finding ID:

### ERR-I14FR1-F2 — stale Addendum-B calibration presented as current (cites **CF-I14F-4** / reviewer F-2)
- **Defect:** I-14-F `decision.md` §1/§6 still presents the *Addendum-B* calibration as current
  ("… i.e. `len > 116`", `WIN32_PATH_LIMIT = 240`, §6 "constant coherence (160 = 260 − 100)")
  while the shipped code and unit test used 210/124/86. Frozen 20:14:58, before Addendum C
  (20:21:45), never superseded in-file.
- **Not fixed here because:** the file is sealed attempt evidence.
- **Erratum:** for I-14-F `decision.md` §1/§6, the Addendum-B numbers are **superseded**; the
  shipped calibration of that card was 210/124/86 (as reviewed), and the current calibration of
  record is **210/150/60** per owner §16 E-1 (this attempt). Reading I-14-F decision.md without
  this erratum is reading a stale design stage.

### ERR-I14FR1-F3 — silent oracle substitution E-G4 >380 → 190/189 (cites **CF-I14F-3** / R-3, reviewer F-3)
- **Defect:** frozen oracle E-G4 specified an over-deep cwd `> 380`; actual runs used 190/189
  with the driver guard re-declared to match, **no addendum recorded** the deviation (it was
  forced — a >380 dir is uncreatable on this box, mkdir edge ~248 — but silent).
- **Not fixed here because:** amending I-14-F's frozen oracle is that card's
  owner/reviewer decision (append-only addendum recommended there).
- **Erratum:** I-14-F `oracle.md` §4 E-G4's "> 380" geometry was in practice **190/189**; the
  two over-deep GREEN rows (`after\over-deep\`, relocated, 2/2 pass) adjudicate the 190/189
  geometry only. This attempt did not re-run an over-deep case (no new information needed for
  E-1; the criterion change is length-only).

### ERR-I14FR1-F4 — cleanup NOT guaranteed for KILLED sessions (cites **CF-I14F-5** / reviewer F-4)
- **Defect:** I-14-F `decision.md` §4's "a failed session still cleans up (unconfigure always
  runs)" **overstates**: cleanup holds for *terminated* sessions (26/26 `removed=true`) but not
  for *killed* ones — 3 orphan `%TEMP%\cw-pytest-basetemp\*` dirs were observed (2 empty; one
  holding 61 KB from an explicitly interrupted run).
- **Not fixed here because:** the file is sealed; and the cleanup *design* itself is unchanged
  by owner §16 E-1 (150/60 is a constants change only) — altering cleanup would exceed this
  card's scope and belongs to the I-14-E artifact-retention decision (CF-I14F-X1).
- **Erratum:** the guarantee is "**cleanup runs when pytest unconfigures normally (rc or
  assertion failure both unconfigure); a KILLED pytest process leaves its fallback dir behind**".
  This caveat applies **equally to this attempt's shipped conftest** (same mechanism) — recorded
  as a known limitation, not a new claim. (This attempt killed no session; all 15 relocating
  sessions here report `cleanup removed=true`.)

### ERR-I14FR1-F6 — `commands.json` lacks argv/cwd (cites **CF-I14F-7** / reviewer F-6)
- **Defect:** I-14-F `handoff.json` step 11 called `commands.json` "real argv/cwd/rc per run",
  but that file contains **no argv/cwd strings** (real argv lived in each
  `summary-placement.json`); its "2/7 at deep-relocated" child-pass count also disagreed with
  `evidence_index.json` (12 deep-relocated child runs / 3 passes). Step 11's wording was later
  corrected in I-14-F's handoff, but the sealed `commands.json` itself stays as built.
- **Not fixed here because:** sealed evidence.
- **Erratum:** I-14-F `commands.json` is a *summary-index*, not a command log; per-run argv/cwd
  for I-14-F lives in its `after/**/summary-placement.json` files. **This attempt's
  `commands.json` records real `argv` + `cwd` per row** (verified: all 22 rows carry both).

(F-5's comment misstatements and unpinned boundary are **fixed directly** in this attempt's test
file — §3. F-1/R-1's figures are **fixed directly** in this attempt's docstring — §1. F-7 is
already-disclosed narrative smear on I-14-F side; no action, not re-registered.)

## 8. Read-only / boundaries attestation

- Production (`company-wiki`): **HEAD f39bd5a6 unchanged**; `status --porcelain` = exactly the
  3 pre-existing user modifications (CLAUDE.md, README.md, artifact_dag.py) — same as the
  independent reviewer recorded; zero writes by this attempt (`after\readonly-check.txt`).
- I-14-F sealed attempt: **zero writes**; pinned artifacts re-hashed unchanged (conftest
  `c22be9f3…`, unit test `b0402b56…`, `changes.diff` `a4c48acb…`, `reviewer_report.md`
  `2e6709e0…`) — `after\readonly-check.txt`.
- The fix lives only in `iso\`; **promotion is a separate step** and is not granted here.
- `disclosure_adaptation = unmapped`, `accuracy = unproven`; test-infrastructure only.

## 9. Remaining gaps (report item 6)

1. **No independent review yet** — `handoff.json.status = review_pending`; the implementer did
   not and will not self-sign (`review.md` is an unsigned stub).
2. **R-2 persists (scoped to I-14-E):** still no clean `child_without_runtime` pass at deep
   geometry under final-era-style constants — this attempt's child shows 4 × `timeout15s-band`
   at the relocated deep placement (path criterion fully green: relocated, cleanup ok, zero
   path-family). The load band remains unadjudicated by design (oracle §9).
3. **Sweep node scope:** integration sweep ran the **logon** node only (child excluded by
   frozen oracle §8 to keep "relocate AND pass" free of the load band); child relocation was
   exercised at deep geometry (RED/GREEN/mutation).
4. **Flip-control values 68, 75, 81** were verified by the pure criterion + unit tests, not by
   dedicated integration runs (only 69/76/82/86 were swept); arithmetic is identical (>60).
5. **Killed-session cleanup caveat** (ERR-I14FR1-F4) ships with this attempt's conftest too;
   artifact retention for relocated/killed runs remains an open I-14-E owner decision
   (CF-I14F-X1).
6. **Repo-global blast radius** unchanged from I-14-F: only the two card nodes + the unit file
   were exercised with the root conftest present; the rest of the company-wiki suite was not
   run under the hook (any basetemp > 60 in that suite will now relocate — worth a follow-up
   note for promotion).
7. **Machine/era-specific calibration** remains a standing caveat (I-14-F open question):
   150/60 is conservative on THIS box's measured edges (dir ~248 / file 260); a different box
   needs its own envelope measurement before relying on 210.
8. `check_lengths.py` / unit-run history anomalies of this attempt are disclosed in §6 (none
   affects the frozen expectations or final results).
