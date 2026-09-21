# I-14-F independent review — reviewer_report.md

- Card: **I-14-F** (deep-cwd WinError 206 → product-side short-basetemp convention)
- Attempt: `a20260919-01` (`<PLAN>\execution_runs\I-14-F\a20260919-01`)
- Reviewer: independent (not the implementer; no implementer artifact was authored or edited by me)
- Review wall clock: 2026-09-21 21:00–21:20 local (UTC+1; TimeZone `GMT Standard Time`)
- Boundaries honoured: read-only on production repos; all reviewer writes confined to
  `<attempt>\review\` (plus one pristine extraction at `<attempt>\rev\tree`)

## VERDICT: **ACCEPTED — SCOPED**

The card's exit criterion is met and independently reproduced: at the frozen deep geometry
(cwd 166/167, basetemp 173/174) a pristine HEAD tree fails with the literal
`FileNotFoundError: [WinError 206]`, the same geometry with the shipped `conftest.py`
relocates the basetemp and passes, and disabling only the convention (`CW_SHORT_BASETEMP_DISABLE=1`)
restores the failure. Production is untouched (zero writes, HEAD unchanged). The change is a
pure addition of two files, verified byte-for-byte against a fresh `git archive` of
company-wiki HEAD.

Acceptance is **scoped** on three recorded residuals:

1. **R-1 (calibration arithmetic is wrong in the optimistic direction).** The frozen
   `GENERATION_RESERVE = 124` is the *child* node's longest generated suffix; the *logon*
   node's is **150**. The real unrouted maximum is therefore **236 chars**, not the
   documented 210, and the "clear of the 240 degradation onset" claim has **4–5 chars** of
   headroom, not ~30. Not blocking (the 206 class needs ≥248 for directory creation / ≥260
   for files; unrouted maxima measured 177 dir / 236 file), but the numbers in
   `conftest.py`'s docstring, `decision.md`, `oracle.md` Addendum C and `handoff.json` are
   factually wrong and must be corrected on the record.
2. **R-2 (child-node GREEN at the frozen geometry is inferred, not demonstrated).** Under the
   *final* constants, the 3 deep child runs at 167/166 all failed with the I-14-E load-band
   signature (0/3 clean). Its clean deep passes (pad666 2/3, effective basetemp 75) come from
   the falsified-constant era; the relocation decision and effective path depth are identical,
   so they remain valid evidence for the path criterion — but no final-era clean child pass at
   167/166 exists.
3. **R-3 (frozen oracle geometry for the over-deep negative was silently substituted).**
   E-G4 specified cwd > 380; the actual runs used 190/189, and the driver guard was
   re-declared to match. A >380-char directory is not creatable on this box (the mkdir edge is
   ~248), so the substitution was forced — but it was not recorded in an addendum.

Everything else the implementer claims held up under independent re-execution. **Gap (b) does
not block acceptance**: the child's thin GREEN is correctly scoped to I-14-E, because the band
also hits short/unrouted placements and the path-family criterion is fully adjudicated for that
node (details in §6).

---

## 1. What I re-ran myself (not a re-read of implementer output)

Driver: `review/reviewer_reverify.py` — written by me, does **not** import or reuse
`harness/run_placement.py`; same argv shape/env/cwd discipline as `oracle.md` §0; strictly
sequential (Addendum A #3). Consolidated record: `review/reviewer_runs.json`.

| phase | tree | cwd_len | basetemp_len | rc | signature | relocated | cleanup |
|---|---|---|---|---|---|---|---|
| RED (logon) | pristine `git archive` HEAD, no conftest | 166 | 173 | **1** | **WinError 206** | n/a (no hook) | n/a |
| GREEN (logon) | `iso\tree` (with conftest) | 166 | 173 | **0** | pass | **true** (effective 75) | **removed=true** |
| MUTATION (logon) | `iso\tree`, `CW_SHORT_BASETEMP_DISABLE=1` | 166 | 173 | **1** | **WinError 206** | false (`disabled-by-env`) | n/a |
| MUTATION (child) | `iso\tree`, `CW_SHORT_BASETEMP_DISABLE=1` | 167 | 174 | **1** | timeout15s-band † | false (`disabled-by-env`) | n/a |

† the child's *surface* signature differed from the implementer's recorded
`FileNotFound-launcher-events`; §3 shows with retained artifacts that the failure is
nonetheless path-caused.

Also re-run by me: the 13-case unit suite → **13 passed** (`review/unit-run1`), independently
confirming the criterion table and that a relocating session of any kind cleans up.

## 2. Claim-by-claim verification

| # | Implementer claim | Verdict | Basis |
|---|---|---|---|
| 1 | `conftest.py` hash `c22be9f3…`; relocate iff `len(resolved)+124 > 210` (threshold 86); fallback `%TEMP%\cw-pytest-basetemp\<UTC>-<8hex>` per session, rmtree'd at `pytest_unconfigure`; opt-out env | **CONFIRMED** | my hash matches `final_hashes.json`; code read; observed live in my RED/GREEN/MUTATION runs (decision + cleanup JSON lines) |
| 2 | RED at 167/166 → 6/6 fail (logon 3/3 literal 206; child 3/3 FileNotFound-launcher-events) | **CONFIRMED** | my own pristine-tree RED reproduced the literal 206 at exactly 166/173; implementer captures (`before\deep\pad55\*`) show the frozen signatures |
| 3 | GREEN relocation fires 6/6 at deep; logon 10/10 across placements; over-deep 190/189 relocates 2/2; controls at 76/75 and 82/81 stay unrouted | **CONFIRMED with era caveat** | all rows in `after\evidence_index.json`; **caveat**: the 6 deep firings at 167/166 split by calibration era — `pad666` (6 runs) under the falsified 160/260/100 constants, `pad777` (6 runs) under the final 86/210/124; logon relocated runs 10/10 rc=0 (deep 9 + boundary-normal 1), plus over-deep and both unrouted controls pass |
| 4 | Mutation: `DISABLE=1` → relocated=false and **both** nodes fail with the frozen signatures | **CONFIRMED (child signature differs)** | logon: my run = WinError 206 at 166/173 ✓. child: `rc=1` ✓, `relocated=false` ✓, but mine surfaced as a 15 s launcher timeout rather than `Errno 2`; artifact-level proof of path causation in §3 |
| 5 | Threshold calibration: 160 falsified by measurement; final 210/124/86 conservative; 87–115 an open documented gap | **PARTLY CONFIRMED** | falsification real and reproducible (see §4); "final 210/124/86 conservative" is **arithmetically wrong** for the logon node (§5) |
| 6 | Production untouched; isolated tree from company-wiki HEAD `f39bd5a6` via `git archive` | **CONFIRMED** | fresh `git archive HEAD` (1913 members, matching `binding.json`) extracted to a length-matched path; vs `iso\tree`: **0 content-differing files**, `only-in-iso` = exactly `conftest.py` + `tests\contract\test_short_basetemp_convention.py`; production HEAD/reflog/status unchanged (see §7) |

## 3. Mutation, adjudicated at artifact level

Because the disabled session does **not** relocate and does **not** clean up, its deep tmp tree
survives and can be measured. From my own mutation child run (basetemp 174, deepest entries):

| artifact under basetemp | total chars | exists? |
|---|---|---|
| dir `…\fake-project\company_wiki\source_catalog` | 247 | yes (⇒ directory-creation edge is ~248, not 260) |
| file `…\source_catalog\cli.py` | 254 | yes |
| file `…\.source_catalog\worker_launcher.lock` | 256 | yes |
| file `…\.source_catalog\worker_launcher_events.jsonl` | **264** | **no** (>260) |
| file `…\worker_stdout-<32hex>-attempt-0001.log` (modelled) | **299** | **no** (>260) |

So at deep+disabled the child fails because the launcher's redirect-log/events paths are
unreachable, not because of load: the failure is path-caused, and the surface signature is just
environment-dependent (whether the launcher dies instantly → `Errno 2`, or loops to the test's
15 s timeout → `TimeoutExpired`). **Consequence for future adjudication: a `timeout15s-band`
label alone cannot distinguish path from load causation for this node; the retained basetemp
artifacts are the discriminator.**

## 4. Is the falsification honestly recorded? — YES

Two falsifiers, both readable and both reproduced from raw evidence:

1. **160-era (Addendum B).** `after\falsified-normal-r1\P0-logon_wrapper_quoted-1\stdout.txt`
   shows `threshold: 160, win32_path_limit: 260, generation_reserve: 100, relocated: false,
   reason: within-budget` at cwd 148 / basetemp **155**, and the node **fails** (index
   signature `WinError206`). The same placement re-run after recalibration
   (`after\falsified-normal-r2-driver.log`, dir mtime 20:38) gives `relocated=true` and
   **passes**. Same geometry, same tree, only the criterion changed.
2. **116-era (Addendum C).** The unrelocated probe survives at
   `%TEMP%\i14f-normal116\…`: 19 `worker_stdout`/`worker_stderr` log pairs, **all 19 zero
   bytes**, `fake_worker_count.txt = 3`, events `1×starting / 19×child_started /
   18×child_unresponsive / 18×restarting`, longest redirect path **241**. That is exactly the
   degradation Addendum C describes, measured by me from the artifacts.

**Pre-registration ordering holds — but only after correcting a timezone trap.** The fallback
stamps inside the decision lines are UTC (`datetime.now(timezone.utc)`); filesystem mtimes are
local = UTC+1 on this box (proved twice: my own GREEN run stamped `20:04:56` while its capture
mtime is `21:05:24`; PowerShell `recorded_at 18:56:39Z` inside the attempt-1 capture whose file
mtime is `19:56:41`). Corrected timeline:

| local time | event |
|---|---|
| 20:15:53 | 160-era falsifier run (`falsified-normal-r1`) |
| 20:16:15 | 116-era probe (Addendum B's E-G2 probe) |
| **20:21:03** | `iso\tree\conftest.py` written with the final 210/124/86 |
| **20:21:45** | `oracle.md` (Addendum C) last written |
| 20:22:08 → 20:43:30 | every final-era adjudicating run: boundary-76, deep pad777, root controls, short-green, over-deep, boundary-normal, mutation |

So Addendum C **was** frozen before the adjudicating after-set, and Addendum B's probe ran
before the constants moved. `oracle.md` is structurally append-only: the body still carries the
original `260/100/160` text of §2 unedited, and the corrections live in prepended blockquotes
(A, B, C) that name their own falsifiers. Nothing I could check shows a frozen expectation being
rewritten to fit a result.

## 5. The calibration constant is mis-derived for the logon node (R-1)

`GENERATION_RESERVE = 124` is documented as "test dir 31 + `\fake-project` 13 +
`\.source_catalog\worker_stdout-<32hex>-attempt-0001.log` 79". Measured from retained
unrelocated artifacts:

| node | longest generated path | suffix under basetemp | measured at |
|---|---|---|---|
| `child_without_runtime` | `\test_child_without_runtime_ses0\fake-project\.source_catalog\worker_stderr-<32hex>-attempt-NNNN.log` | **125** | basetemps 75, 116, 174 (three independent placements) |
| `logon_wrapper_quoted` | `\test_logon_wrapper_detaches_a_0\project path with spaces\fake-project\.source_catalog\worker_stdout-<32hex>-attempt-0001.log` | **150** | basetemps 74 and 81 (both **passing** unrouted runs) |

Segment lengths: 31 (`test_logon_wrapper_detaches_a_0`) + 24 (`project path with spaces`) + 12
(`fake-project`) + 15 (`.source_catalog`) + 63 (`worker_stdout-<32hex>-attempt-0001.log`) + 5
separators = 150. The logon node's project root is one level deeper than the child's, which is
exactly what the reserve omits. The docstring's own arithmetic is also internally inconsistent
(31 + 13 + 79 = 123, not 124).

Consequences, stated precisely:

- Shipped criterion ⇒ unrouted (`len ≤ 86`) ⇒ real maxima: child file **211**, logon file
  **236**; directory maxima 177 (child) / 172 (logon).
- Measured edges: directory creation succeeds at 247 and fails at 253 (⇒ ~248, the classic
  MAX_PATH − 12 for 8.3 names); file creation fails at 264 (⇒ 260). **Both edges are still
  clear of every unrouted maximum**, so the card's criterion (no 206 at any unrouted basetemp)
  holds — this is why R-1 does not block.
- But the claimed margin is wrong: the highest *measured-clean* total is **231** (the logon
  control at basetemp 81, which passed), and the observed degradation onset is **240/241**
  (child at basetemp 116). At the largest unrouted basetemp (86) the logon node would generate
  **236**-char paths — i.e. the band **232–236 is untested for the logon node**, and it is
  *not* rerouted. `oracle.md` Addendum C asserts the untested band is "total 210–239 ⇒ rerouted
  conservatively"; for the logon node that assertion is false.
- Recommended correction (owner's call, not required for this card's exit criterion): either
  record the true numbers and accept 231-clean as the empirical envelope, or set
  `GENERATION_RESERVE = 150` (⇒ `BASETEMP_MAX_CHARS = 60`) if the documented margin is to be
  the *real* margin. The second option would start rerouting the deep-boundary controls
  (76/75, 82/81 stay fine; the two frozen deep lenses are unaffected).

Secondary, same family: the unit-test case-table comments misstate path lengths (actual values
from pytest collection: 174, **154**, **119**, **84**, 82, 360, 78 against comments claiming
174, "155/156", "116", "86 boundary", "~81", "364") and the true boundary pair (86 ⇒ no
relocate, 87 ⇒ relocate) is **not pinned by any case**; nearest are 84 and 119. All seven
outcomes match their expectations (0 mismatches), so this is a pinning-quality defect, not a
wrong test.

## 6. Is the conservative band (87–115 rerouted) acceptable? — YES, with R-1 noted

The convention is **strictly additive**: every placement with `len ≤ 86` behaves exactly as
before the fix (same basetemp, same paths), so no previously-working placement can regress
through the criterion itself. Over-rerouting is the only new cost, and it is
behaviour-preserving where I could measure it: relocated sessions pass, create a fresh unique
dir, and remove it (`cleanup removed=true` in every one of my runs and in 26/26 implementer
decision files that have a cleanup event). The residual costs are (a) `%TEMP%` basetemps for
the 87–115 band instead of the caller's directory, and (b) the relocated artifacts are deleted
by design, so post-mortem of relocated runs is impossible — both already disclosed in
`handoff.json.open_questions`; (c) the reserve error in R-1, which means the band that is
*not* rerouted is larger than the oracle believes.

One further design residual worth recording (not a card defect): the hook only inspects an
**explicit** `--basetemp`; a deep `%TEMP%` with no `--basetemp` is unguarded, and the fallback
target itself is assumed short (75 chars here; it inherits `%TEMP%`'s depth).

## 7. Gap (b): does thin child GREEN block acceptance? — NO, correctly scoped to I-14-E

Facts I verified: the child's failures at relocated deep placements are `timeout15s-band`,
`restart-band`, `launcher-rc1-quiet` — never a path-family signature; the same band types occur
at *short/unrouted* placements (basetemps 62–82: `boundary76`, `boundary76-r2`, `short-green`,
`attempt1`), so the band is placement-independent; the child's RED (unrouted deep) signature is
the path-family one 3/3; and my own disabled deep run reproduced path causation at the artifact
level (§3). Under the frozen oracle §6, only path-length signatures adjudicate this card, and
that rule was frozen before the runs.

So: **not blocking, correctly scoped** — with two caveats recorded rather than waved away:
(i) per R-2 there is no final-era clean child pass at 167/166, so the child's deep GREEN rests
on same-depth (effective basetemp 75) clean passes from the falsified-constant era plus the
absence of any path-family signature; (ii) `timeout15s-band` is not by itself proof of load
causation (§3), so the I-14-E work should retain basetemp artifacts when it tackles the band —
the current cleanup design destroys exactly the evidence it will need.

## 8. Production zero-write — CONFIRMED

- `git -C company-wiki rev-parse HEAD` = `f39bd5a64224cd0c7aa098f23f64bf3811fa8939` (as bound);
  reflog top unchanged (no new commits); `git status --porcelain` = exactly the 3 pre-existing
  user modifications (`CLAUDE.md`, `README.md`, `src/company_wiki/source_catalog/artifact_dag.py`)
  with mtimes 09-19 11:20 and 09-20 12:48 — all **before** the attempt window (09-21 19:36).
- No untracked files. The isolated tree equals a fresh HEAD archive except the two added files
  (§2 row 6). The venv contains **no** `company_wiki` distribution and no `.pth` pointing at
  production, so the runs could not import or write product code; every run cwd and basetemp
  lived under the attempt or `%TEMP%`.
- Re-checked **after** all my runs: still exactly the same 3 modifications, same HEAD, and
  `iso\tree` still byte-identical to pristine + 2 files (my runs left no `.pyc`, no
  `.pytest_cache`).
- Only observation outside the attempt: the gitignored
  `company-wiki\.source_catalog\catalog.sqlite3-shm` has mtime 09-21 20:56:56 — after the
  attempt's last artifact (20:47) — and it did **not** change across my five pytest runs, so it
  is not attributable to I-14-F (some other live process holds the production catalog open).
  Recorded as an observation, not a violation.

## 9. Documentation / evidence-pack findings (non-blocking)

| id | severity | finding |
|---|---|---|
| F-1 | medium | R-1: reserve/limit derivation wrong for the logon node (124 vs measured 150); "unrouted max 210" and "clear of 240" claims incorrect; false in `conftest.py` docstring, `decision.md` §1/§6, `oracle.md` Addendum C, `handoff.json` |
| F-2 | low | `decision.md` still presents the *Addendum-B* calibration as current (`… i.e. len > 116`, `WIN32_PATH_LIMIT = 240`, and §6 "constant coherence (160 = 260−100)") while the shipped code and unit test use 210/124/86; it was frozen at 20:14:58, before Addendum C (20:21:45), and never superseded in-file |
| F-3 | low | Oracle E-G4's over-deep geometry (>380) was replaced by 190/189 with the guard re-declared to match, without an addendum recording the deviation (R-3) |
| F-4 | low | Cleanup is guaranteed for sessions that terminate (26/26 cleanup events `removed=true`; my runs included) but **not** for killed sessions: 3 orphan `%TEMP%\cw-pytest-basetemp\*` dirs remain (2 empty; `…193155…` holds 61 KB from the explicitly interrupted run). `decision.md` §4's "a failed session still cleans up (unconfigure always runs)" overstates this |
| F-5 | low | Unit-test comments misstate 4 of 7 case lengths and the 86/87 boundary is unpinned (§5) |
| F-6 | info | `handoff.json` step 11 calls `commands.json` "real argv/cwd/rc per run"; it contains no argv/cwd strings (real argv is in each `summary-placement.json`). `handoff.json`'s "2/7 at deep-relocated" also doesn't match `evidence_index.json` (deep-relocated child runs = 12, passes = 3). Narrative only |
| F-7 | info | `after\external-summaries\RED-short-control-attempt1-band.json` carries a mixed row (rc=1 with signature `pass`), already disclosed in `open_questions`; the raw attempt-1 capture is preserved and I verified it (`assert 3 == 2` restart band, not a path error) |

## 10. Unverified / not covered by this review

1. I did **not** run the child node at the frozen 167/166 geometry with the final constants
   (only its mutation-disabled counterpart). The child's "passes when the load allows" claim
   remains inferred from same-effective-depth passes; R-2 stands until someone gets a clean run.
2. I did **not** re-derive I-14-C's historical datapoints (deep 173/174 → 12/12 fail; short
   80/81 → 12/12 pass) from I-14-C's own evidence tree; I relied on the frozen oracle plus this
   attempt's passing unrouted logon artifacts (basetemps 74, 81).
3. I did **not** measure the logon node at basetemps 82–86 unrouted (the 232–236 total band
   that R-1 identifies as untested).
4. I did **not** run the rest of the company-wiki suite with the new root `conftest.py` present
   — the hook is repo-global (every pytest session in that tree now prints a decision line and
   may relocate), and only the two card nodes plus the new unit file were exercised.
5. I could **not** identify the process writing the production `catalog.sqlite3-shm`, nor
   recover the implementer's session transcript, so the "frozen before" reading in §4 rests on
   artifact timestamps plus code/commit ordering, not on a captured authoring sequence.
6. I did not attempt to reproduce the historic cmd-A5 anomaly (child passing at ~271 while this
   attempt's child fails at ~279) — still open, as the implementer states, and outside this
   card's envelope.

## 11. Reviewer artifacts (all under `<attempt>\review\`)

| file | purpose |
|---|---|
| `reviewer_reverify.py` | my independent RED/GREEN/MUTATION driver (own argv/env/cwd handling) |
| `reviewer_compare.py` | pristine-archive vs isolated-tree byte comparison |
| `reviewer_units.py` | extracts the unit suite's real case values via pytest collection and re-derives the criterion |
| `reviewer_consolidate.py` | builds `reviewer_runs.json` from my own captures |
| `reviewer_runs.json` | the four verification runs with decisions, cleanup, capture hashes |
| `captures\M-mut-*.txt` | raw mutation captures (run dirs live under `%TEMP%`) |
| `deep\pad55\*` | raw RED and GREEN captures |
| `unit-run1\` | independent 13/13 unit-suite run |

SHA-256 pins (verified implementer artifacts are unchanged from `final_hashes.json`):

```
c22be9f366c5590e522b713374419e293259619ead5ee72e1adb1ee71e6f2c22  iso/tree/conftest.py
b0402b5693c1d5b13bb8c26225ac9da422f18bc428d0aee4ca80758830c74e7e  iso/tree/tests/contract/test_short_basetemp_convention.py
a4c48acbf8706b74add97bc2391487d407edfd72f4c15ace8742876501d659b1  changes.diff
131a0bde097eb0091ce667abe429b9ac238d86e7ba54aa2a33674416f2b6c78d  after/evidence_index.json
9508c3fd108c93ac90a305b9ed7ccb28cdb180955b1fda40eaf981f84568414f  harness/run_placement.py
```

The hash of this report is pinned in the sidecar `reviewer_report.sha256` (a file cannot contain
its own digest).

## 12. Recommended disposition

- **Accept I-14-F as scoped** (`accepted_scoped`): card criterion met and independently
  reproduced; production untouched; change is additive and reversible by deleting two files.
- **Carry forward as recorded residuals**: R-1 (correct the reserve/threshold arithmetic; decide
  whether to adopt reserve 150), R-2 (child deep GREEN pending I-14-E load work; retain
  relocated artifacts for that work), R-3 (amend the oracle for the over-deep substitution),
  plus F-2 (supersede the stale calibration text in `decision.md`) and F-4 (state that cleanup
  is not guaranteed for killed sessions).
- Reviewer signature: independent reviewer, card I-14-F, attempt a20260919-01. Implementer did
  not self-sign (`review.md` remains a stub; `handoff.json.reviewer_status` unchanged by me).
