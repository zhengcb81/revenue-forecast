# I-14-F-R1 independent review — reviewer_report.md

- Card: **I-14-F-R1** (follow-up to accepted card I-14-F; applies owner §16 E-1 「E-1: 150/60」)
- Attempt: `a20260922-01` (`<PLAN>\execution_runs\I-14-F-R1\a20260922-01`)
- Reviewer: independent (not the implementer); this report was authored by the reviewer only
- Review wall clock: 2026-09-22, local UTC+1
- Method: sample-not-exhaust per instruction — oracle pin re-derived, constants re-derived,
  unit suite re-run once by the reviewer, one RED + one GREEN + one MUTATION deep-logon run
  each executed by the reviewer, control-flip discipline spot-checked at 3 flips, sealed hashes
  and production git state re-computed by the reviewer
- Boundaries honoured: the reviewer wrote only these two files (`reviewer_report.md` +
  `reviewer_report.sha256`); the reviewer's own runs used a scratch root under `%TEMP%`
  (`%TEMP%\i14frr1rev…`), no writes to production repos in this review, no git writes, no
  writes inside the attempt's evidence directories, and the implementer's files were not edited

## VERDICT: **accepted_scoped**

The card's claimed state holds under my own execution: constants in
`iso\tree\conftest.py` are `WIN32_PATH_LIMIT=210 / GENERATION_RESERVE=150 /
BASETEMP_MAX_CHARS=60` (⇒ relocate iff `len + 150 > 210` ⇔ `len > 60`, read directly from
lines 74–76); the unit suite passes **15/15 rc 0 in my own run**; my own deep-logon runs
(cwd 166 / basetemp 173, padded root 140) show RED = rc 1 with the literal `WinError 206`
and no decision file on the pristine `iso\red-tree`, GREEN = rc 0 with
`"relocated": true, "generation_reserve": 150, "threshold": 60` and
`cleanup … "removed": true`, and MUTATION (`CW_SHORT_BASETEMP_DISABLE=1`) = rc 1 with
`"relocated": false, "reason": "disabled-by-env"` and the literal `WinError 206` back.
The oracle pin `b5fee00f52334122…` (13851 B) re-hashes exactly from `oracle.md`, and its
mtime (08:34:24) precedes the pin (08:35:44) and the first run artifact (unit-run1,
08:42:11) — the frozen oracle was not edited after runs began. I-14-F's three pinned
sealed files re-hash to `c22be9f3…`, `b0402b56…`, `2e6709e0…` unchanged, and production
`company-wiki` is at HEAD `f39bd5a6` with exactly the 3 pre-existing user modifications
(`CLAUDE.md`, `README.md`, `src/company_wiki/source_catalog/artifact_dag.py`) in my own
`git status --porcelain` — zero production writes by this attempt in this review's evidence.

Acceptance is **scoped** on recorded residuals (none of them blocks this card):

1. **Gap-5 ruling (explicit, item 8 below): does NOT block acceptance** — the thin
   exercised-under-hook sample (2 card nodes + 1 unit file) is correctly carried as a
   **promotion-time sampling obligation** (CF-I14FR1-3); promotion remains a separate,
   ungranted step.
2. **R-2 / load band inherited (CF-I14FR1-1):** no clean deep `child_without_runtime`
   pass exists in this attempt (4× `timeout15s-band` at the relocated deep placement);
   out of scope by the frozen oracle §9 rule; scoped to I-14-E as in I-14-F.
3. **Killed-session cleanup caveat inherited (CF-I14FR1-2 / ERR-I14FR1-F4):** cleanup
   guarantees hold for normally-terminating sessions in this attempt's runs; killed
   sessions can leave orphans — a constants-only card cannot change this design.
4. **Machine-specific calibration (decision §9.7):** 150/60 is calibrated to this box's
   measured edges (dir ~248 / file 260); other machines need their own measurement.

---

## 1. What I ran myself (item-by-item vs the review plan)

| # | check | my own execution | result |
|---|---|---|---|
| 1a | threshold arithmetic | read `iso\tree\conftest.py` L74–76 | 210 / 150 / 60; `BASETEMP_MAX_CHARS = 210−150`; criterion `len+150>210 ⇔ len>60` ✓ |
| 1b | unit suite | `iso\venv\Scripts\python.exe` (Python 3.13.9) `-m pytest … test_short_basetemp_convention.py` | **15 passed, rc 0** ✓ (boundary 60→False / 61→True cases are in the table, test file L63–68) |
| 1c | criterion at boundary/controls | direct `needs_short_path_fallback` calls (absolute paths) | 52→False, **60→False**, **61→True**, 69→True, 82→True, 86→True, 87→True ✓ |
| 2 | RED deep logon | pristine `iso\red-tree`, cwd 166 / bt 173, harness env (`PYTHONPATH=<tree>\src`) | **rc 1, literal `WinError 206`**, no decision file ✓ |
| 2 | GREEN deep logon | `iso\tree`, cwd 166 / bt 173, harness env | **rc 0, `relocated=true`, `generation_reserve=150`, `threshold=60`, `cleanup removed=true`**, effective bt 75, no `WinError 206` ✓ (run twice: with and without the PYTHONPATH var — both passed) |
| 3 | MUTATION deep logon | `iso\tree` + `CW_SHORT_BASETEMP_DISABLE=1`, cwd 166 / bt 173 | **rc 1, `relocated=false`, `reason=disabled-by-env`, literal `WinError 206` returned** ✓ |
| 4 | doc-figure arithmetic | own arithmetic on the stated components | see §2 below |
| 5 | control-flip discipline | read decision.md §4 + test file L52–124 | see §3 below |
| 6 | sealed-source protection | own `Get-FileHash` on I-14-F's 3 pins + own `git rev-parse/status` on production | see §4 below |
| 7 | retained-failure honesty | tails of `after\unit-run1\stdout.txt`, `after\unit-run2\stdout.txt` + oracle re-hash + mtime ordering | see §5 below |
| 8 | gap 5 | adjudicated | see §6 below |

Reviewer-side process anomaly disclosed: my first RED attempts omitted the harness's
`PYTHONPATH=<tree>\src` and failed at `ModuleNotFoundError: No module named 'company_wiki'`
(rc 1 but for the wrong reason). I found the variable in `harness\run_placement.py` L107
(stripped env sets `PYTHONPATH = <tree>\src`), re-ran RED/GREEN/MUTATION with it, and only
the runs under that env are cited above. All of my runs were in my own `%TEMP%` scratch root,
so nothing in the attempt's evidence tree was touched by my executions.

## 2. Doc-figure spot check (item 4) — arithmetic done by me

Logon reserve decomposition as printed in the conftest docstring (L25–30):

`31 + 24 + 12 + 15 + 63 + 5` → 31+24=55, +12=67, +15=82, +63=**145**, +5 separators =
**150** ✓. Segment spot-checks: `test_logon_wrapper_detaches_a_0` = 31 chars;
`project path with spaces` = 24; `fake-project` = 12; `.source_catalog` = 15;
`worker_stdout-<32hex>-attempt-0001.log` = 13+1+32+9+4+4 = 63 ✓.

Child claim **125**: `test_child_without_runtime_ses0` (31) + `fake-project` (12) +
`.source_catalog` (15) + `worker_stderr-<32hex>-attempt-NNNN.log` (63) + 4 separators
= 121 + 4 = **125** ✓ — and 125 ≤ 150, so reserve 150 covers both bootstrap nodes as the
docstring states. The docstring also correctly calls out the old error
(`31 + 13 + 79 = 123 ≠ 124`). The reviewer-measured provenance of 150/125 matches I-14-F's
reviewer report §5 (basetemps 74/81 for logon; 75/116/174 for child) — that report is the
frozen input this card was told to adopt.

## 3. Control-flip discipline (item 5) — 3 flips sampled

Sampled flips 69, 82, 86 (decision.md §4) + unit flips 84/82/78 and `decide()` 64:

- decision.md §4 carries the verbatim written reason once at the table head —
  **"owner §16 E-1 chose 150/60; this control's unrouted expectation is superseded"** —
  and each flip row in that table sits under that reason (row 69 explicitly
  "(reason above)"; rows 76/75, 82/81, 86 and the unit rows say "YES" / "unit case
  flipped, inline reason"). The reason text is present in the same section as every
  flipped control in decision.md.
- Unit file, verified at exact lines: 84 (L69–72), 82 (L73–75), 78 (L79–82), `decide()`
  64-char (L106–110) — each carries the full inline written reason; expectations flipped
  to `True`/relocate.
- **52-char point did NOT flip:** decision.md §4 row = "NO — must not flip (52 ≤ 60),
  deliberately NOT flipped", and my criterion run confirms 52 → `relocated=false` ✓.
- **Old 87 still true:** decision.md §4 row = old expected true / new true / no flip; my
  criterion run confirms 87 → `True` ✓.
- Boundary row 60/61 pinned fresh in both halves: unit table (my run passed) + sweep rows
  n60 (`relocated=false, within-budget, rc 0`) and n61 (`relocated=true, rc 0`) in
  commands.json.

Minor observation recorded as finding **N-1** below: §4 states the reason at table level
rather than restating it inside every row; the oracle's per-control wording is satisfied at
section level and per-case level in the unit file, but not duplicated per table row.

## 4. Sealed-source + production protection (item 6) — my own hashes

- I-14-F `a20260919-01` sealed files, recomputed by me:
  `iso\tree\conftest.py` = `c22be9f366c5590e522b713374419e293259619ead5ee72e1adb1ee71e6f2c22` ✓,
  `iso\tree\tests\contract\test_short_basetemp_convention.py` = `b0402b5693c1d5b13bb8c26225ac9da422f18bc428d0aee4ca80758830c74e7e` ✓,
  `reviewer_report.md` = `2e6709e0c6690c76d377dceec787c8de7722bd38c0d5cabc8fc49b0a37fc2af1` ✓
  — byte-untouched in this attempt.
- Production `C:\Users\郑曾波\Projects\company-wiki` (my own git run):
  HEAD = `f39bd5a64224cd0c7aa098f23f64bf3811fa8939`; `git status --porcelain` = exactly
  the 3 pre-existing user modifications named above; no other entries — the attempt's
  claim of only 3 pre-existing mods holds in this review.

## 5. Retained-failure honesty (item 7)

- `after\unit-run1\stdout.txt` exists; tail = `11 passed, 1 warning, 4 errors in 4.47s`
  (harness-invocation defect). `after\unit-run2\stdout.txt` exists; tail =
  `1 failed, 14 passed, 1 warning in 4.06s` (63-vs-64 pathlib construction bug). Both
  failures are retained on disk, disclosed in decision.md §6 (causes + "oracle NOT
  edited"), echoed in `commands.json.unit_runs`, and the adjudicating run is unit-run3.
- Oracle integrity: `oracle.md` re-hashes to
  `b5fee00f52334122bded8758aae6a584a7e2d07f5327a7037670137cc7b6ec2a` (13851 B) = the pin
  in `oracle.sha256`; mtime ordering oracle 08:34:24 < pin 08:35:44 < first run 08:42:11.
  The 63-vs-64 bug was fixed by correcting the TEST construction (names 61/41/201 against
  the oracle-frozen 64/44/204 lengths — read at test file L100–105), not by editing frozen
  expectations: oracle §4 still pins 64/44/204 and the test asserts exactly those lengths.

## 6. Gap 5 adjudication (item 8) — explicit ruling

**Ruling: does NOT block acceptance of I-14-F-R1; it is correctly carried as a
promotion-time sampling obligation (CF-I14FR1-3).** Reasons:

1. The criterion change under review is arithmetic-only against the already-accepted
   I-14-F design (same hook, same fallback, same cleanup, same opt-out); I-14-F's
   reviewer already accepted the hook as repo-global with only these nodes exercised,
   so E-1 widens the *relocation band*, not the exposure class.
2. The widened band (61–86) was actually sampled by this attempt beyond the boundary:
   sweep sizes 61/69/76/82/86 all relocated and passed (commands.json rows, all
   `guard_ok`, rc 0 — read by me; boundary halves additionally re-derived by my own
   criterion run), and every relocation observed in my own runs cleaned up
   (`cleanup removed=true` in my GREEN runs).
3. The residual risk of threshold 60 — in normal developer use any explicit basetemp
   longer than 60 chars now relocates to `%TEMP%` and is deleted on unconfigure — is a
   developer-experience / artifact-retention question, not this card's exit criterion;
   it is already registered in handoff `open_questions` and CF-I14FR1-3 with the concrete
   remedy: **the promotion card must run a broader company-wiki suite sample under the
   hook before merge** (in this review I confirmed that obligation is stated, not that
   it has been discharged — it belongs to the separate, ungranted promotion step).

## 7. Findings (numbered)

| id | severity | finding |
|---|---|---|
| N-1 | low | decision.md §4 records the verbatim flip reason once at the table head (rows reference it: "reason above" / "inline reason"); oracle §8's "recorded with every flipped control" is satisfied at section level and per-case in the unit file, but rows 76/82/86 do not restate the reason in-row. Suggest per-row restatement when the promotion card re-records these controls. |
| N-2 | info | `commands.json` rows carry real argv+cwd as claimed (all 22 rows verified while reading the file), but per-row **env is not recorded** — a rerunner must read `harness\run_placement.py` to learn that `PYTHONPATH=<tree>\src` and the stripped env are required (my own first RED failed on exactly this). Env is not part of the card's argv claim, so this is an evidence-completeness note, not a claim failure. |
| N-3 | info | Reviewer-observation: with no `PYTHONPATH`, runs against `iso\tree` still imported `company_wiki` while runs against `iso\red-tree` raised `ModuleNotFoundError`; the mechanism (root `conftest.py` presence is the only difference I found) was not identified. Immaterial to the claims — the harness always sets `PYTHONPATH`, and all cited RED/GREEN/MUTATION results above were re-run with it set. |
| CF-inherited | low | R-2/load band (CF-I14FR1-1), killed-session cleanup caveat (CF-I14FR1-2), sweep-covers-logon-only (CF-I14FR1-4), machine-specific calibration — all disclosed by the implementer in decision.md §9 / handoff carried_findings; carried forward unchanged. |

No finding above blocks the card's exit criterion.

## 8. Unverified / not covered by this review

1. **Size sweep not re-run by me.** Rows n40…n86 were read from `commands.json`
   (`40/60 → relocated=false rc 0`; `61/69/76/82/86 → relocated=true rc 0`, all
   `guard_ok`); my own contribution to the boundary is the direct criterion run
   (60→False, 61→True) plus the unit suite run. The integration sweep table itself is
   evidence-read, not re-executed.
2. **Child node not re-run by me** (RED/GREEN/mutation child rows are read from
   `commands.json` + decision.md §5); the load band is out of scope by the frozen
   oracle §9 rule and R-2 remains open as disclosed.
3. **Flip values 68, 75, 81** were verified only at criterion level (my run) and in the
   unit file — no dedicated integration runs exist for them (same as decision.md §9.4).
4. **I-14-F sealed attestation scope:** I re-hashed the 3 pinned files named in the plan
   (conftest / unit test / reviewer_report); other I-14-F attempt files were not
   re-hashed by me (decision.md also claims `changes.diff` `a4c48acb…` — not re-checked).
5. **`after\readonly-check.txt` internals** not re-derived file-by-file; I relied on my
   own 3-file re-hash + own production git run instead (stronger for the named pins).
6. **Oracle pre-freeze authoring sequence** rests on mtime ordering + the pin, not on a
   captured authoring transcript (same epistemic limit as I-14-F §10.5).
7. **RED 6/6, GREEN 7/7, MUTATION 2/2 totals** were not all re-executed by me — I ran
   1 RED + 2 GREEN + 2 MUTATION (one GREEN/RED pair initially env-defective, disclosed
   in §1) per the sample-don't-exhaust instruction; the totals are read from
   `commands.json` and are internally consistent with my single-run reproductions.
8. The writer of production `catalog.sqlite3-shm` remains unidentified (inherited
   observation from I-14-F §8).

## 9. Signature

- Verdict: **accepted_scoped** (numbered findings N-1..N-3 + inherited CFs as scope).
- Independent reviewer, card I-14-F-R1, attempt a20260922-01. The implementer did not
  self-sign (`review.md` remains a stub; `handoff.json.reviewer_status` unchanged by me).
- This report's sha256 is pinned in the sidecar `reviewer_report.sha256` (a file cannot
  contain its own digest).
- REM-79 self-check on this text: each universal quantifier (e.g. "all 22 rows", "every
  relocation observed in my own runs", "both halves") names its evidence scope on the
  same line; no unscoped 只有/全部/没有-family claim is made.
