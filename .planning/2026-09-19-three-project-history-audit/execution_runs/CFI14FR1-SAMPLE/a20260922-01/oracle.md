# CFI14FR1-SAMPLE — broader company-wiki suite sampling with the repo-global short-basetemp hook ACTIVE — FROZEN ORACLE (r1)

- Plan: `2026-09-19-three-project-history-audit`
- Card: **CFI14FR1-SAMPLE** — discharge outstanding condition **CF-I14FR1-3** of the
  I-14-F-R1 card's acceptance: 「repo-global hook ⇒ broader company-wiki suite sampling
  before merge/at batch-4」
- Attempt: `execution_runs/CFI14FR1-SAMPLE/a20260922-01`
- Implementer: delegated sampling session (**does NOT self-sign accepted**; `handoff.status`
  stays `review_pending`, `disclosure_adaptation = unmapped`, `accuracy = unproven`,
  nothing here is signed)
- Dispatch-asserted context (recorded, **not verified here — git is forbidden by this
  card's boundaries**): CW repo has repo-root `conftest.py` with the 150/60
  short-basetemp redirect hook + a new contract test, committed at `ac4ebd0`;
  batch-4 pushed in revenue-forecast. Because no git command may run, this attempt binds
  **live file hashes instead of a commit id** (§1) — the commit claim stays dispatch
  context, unverified.
- Isolation: this oracle is frozen **BEFORE any pytest process of this attempt exists**.
  At freeze time: no pytest run, no collection, no probe of this card has been executed.
  Freeze ordering: `oracle.md` is the FIRST file created in this attempt; its sha256 is
  pinned later in `binding.json`; any post-freeze correction must be an append-only
  `## Revision rN` (r1–rN bytes never edited in place).

## 0. Scope, boundaries, and what this oracle does NOT claim

- **CW tree is READ-ONLY** (`C:\Users\郑曾波\Projects\company-wiki`). Zero product
  writes, zero authoring in CW. Allowed side effects, honestly pre-declared:
  1. pytest's cacheprovider updates `.pytest_cache/` (baseline mtime measured at freeze:
     `2026-07-18 14:09:05.073`; its post-run mtime impact is recorded in `decision.md`);
  2. `PYTHONDONTWRITEBYTECODE=1` is set for every python invocation of this card so no
     `__pycache__`/.pyc is written (baseline: CW root `__pycache__` ABSENT — must stay
     ABSENT; verified post-run);
  3. tests themselves may write into CW only if a test misbehaves — a post-run tree scan
     (files with LastWriteTime inside the run window) discloses any such write honestly;
     it is a FINDING about the test, not an action by this card.
- **Artifacts only under `%TEMP%` + this attempt.** The hook's fallback roots live under
  `%TEMP%\cw-pytest-basetemp\…` by design (and are removed in `pytest_unconfigure`);
  decision logs live under this attempt's `evidence/`.
- **No git** (not even read-only git), **no network**, no credential use, no product code
  change, no `REMEDIATION_REGISTER.md`/card/oracle of another card edited by this attempt.
- **This is a SAMPLE to observe hook effects — not an all-green gate.** Nothing in §4
  demands zero failures. Failures are observations that must be *recorded and attributed*,
  never papered over; a failing file does not by itself block or discharge the condition —
  the attribution does.
- The condition this card serves is a **sampling** obligation (broader suite run with the
  hook present before merge/at batch-4). It does not re-adjudicate I-14-F-R1's criterion,
  the owner §16 E-1 ruling, or batch-4 promotion itself.

## 1. Sample set — FIXED at freeze (measured live, not quoted from dispatch)

**In scope (the "broader suite" of this condition): every test file under two roots,
selected by directory, no per-file cherry-picking:**

| root | selection | files (counted at freeze) |
|---|---|---|
| `tests/contract/` | every `test_*.py` directly in the directory (full root) | **205** |
| `tests/unit/` | every `test_*.py` directly in the directory (full root) | **63** |
| **total sample** | | **268** |

- Rationale: `tests/contract/` is closest to the hook's contract surface (it contains the
  new hook contract test and the worker-bootstrap / launcher tests where path-length
  damage historically appeared); `tests/unit/` is the broad adjacent unit surface. Both
  roots run in ONE pytest process (one session, one hook decision) plus per-failure
  controls (§3).
- The full name/bytes/sha256 manifest of all 268 files, generated at freeze BEFORE any
  run, is `evidence/sample_set_freeze.txt` (referenced here; pinned in `binding.json`).
  A file that changes between freeze and run is a binding violation, detected by the
  post-run re-hash (§4 A5).

**Anchor pins measured LIVE at freeze (sha256, bytes):**

| file | sha256 | bytes |
|---|---|---|
| `conftest.py` (the hook) | `a908c9da7b77ace08a8d60715093a19f28cb9ae67152ccf5627bb4d070084249` | 9031 |
| `tests/contract/test_short_basetemp_convention.py` (new contract test) | `dfb7c6cd149e395c0a3c87d733547833d05b53020195c6f649c987917f5df868` | 11366 |
| `pytest.ini` | `013980c5b2d94d7aacc078c198e810e6fe84ead0825065bbf5d8fd5a62f78909` | 360 |
| `tests/conftest.py` (hermetic guard) | `ab0dc93e71f29c054fce5ee8d8f9856a6c80f7f343b34f95ebc075a0bcd80e62` | 6715 |
| `tests/contract/conftest.py` | `1f495987d7fa3316578b7d4f7ec6a7769232e0f9c466e830bd156e469cd41ef8` | 2011 |

- Dispatch said "conftest.py + test file hashes at run time = `dfb7c6cd…`-era". Measured:
  `dfb7c6cd…` is the **contract test file**, and the live hook `conftest.py` is
  `a908c9da…`; both are pinned above exactly as measured (the prefix claim resolves, with
  the file identity corrected to what the bytes say).

**EXCLUSIONS (explicit; nothing else is excluded):**

- `tests/acceptance/` (2 test files), `tests/e2e/` (1), `tests/integration/` (2),
  `tests/archive/` (0) — outside the two sampled roots; acceptance/e2e/integration need
  live environments beyond this card's hermetic boundary.
- Root-level `tests/test_config_doctor.py`, `tests/test_relevance.py` — outside the two
  sampled roots.
- `tests/fixtures/`, `tests/helpers/`, `tests/**/__pycache__/` — not test files.
- **Network/credentials:** no in-scope file *requires* network or credentials to run —
  `tests/conftest.py` is hermetic by construction (pops `*_API_KEY`, sets
  `PYTHON_DOTENV_DISABLED=1`, `COMPANY_WIKI_NETWORK=blocked`, `COMPANY_WIKI_REAL_LLM=0`,
  monkeypatches `socket.connect`/`create_connection` to raise). Files that gate on REAL
  external conditions **self-skip inside the sample** (e.g.
  `test_lt_uj_real_e2e.py::REQUIRE_REAL` skipif, `test_r9_v1_removal_gate.py` module
  skipif) and are expected to appear as **skipped — recorded, not excluded**. If any
  in-scope test nevertheless fails for missing network/credentials, that is recorded and
  attributed (pre-existing/environment), never silently dropped.
- **No marker deselection**: the fixed argv carries no `-m` filter, so `slow` /
  `integration` / `e2e`-marked tests that live inside the two roots DO run (they are part
  of the broader sample).

## 2. The hook under test (read from `conftest.py` at freeze — constants quoted from the live file)

- Criterion: relocate iff `len(resolved_basetemp) + 150 > 210` ⇒ **relocate iff
  `len > 60`** (`WIN32_PATH_LIMIT=210`, `GENERATION_RESERVE=150`,
  `BASETEMP_MAX_CHARS=60`; owner §16 E-1 「E-1: 150/60」).
- Evidence channels: `CW_BASETEMP_DECISION_FILE` (env) receives JSON lines
  (`event=decision` / `event=cleanup`); stdout carries `CW-BASETEMP-DECISION {…}` /
  `CW-BASETEMP-CLEANUP {…}` lines.
- Disable env for A/B controls: **`CW_SHORT_BASETEMP_DISABLE`** (=1 ⇒ `disabled-by-env`).
  Fallback root: `%TEMP%\cw-pytest-basetemp\<UTCstamp>-<8hex>`, fresh per relocating
  session, removed in `pytest_unconfigure` (so the *record* of it — decision + cleanup
  lines — is the durable artifact, not the directory).
- Interpreter measured at freeze: `python` → `C:\Miniconda\python.exe`, Python 3.13.9,
  pytest 9.1.1 (matches the CW `cpython-313-pytest-9.1.1` pycache era).
- `%TEMP%` measured at freeze: `C:\Users\郑曾波\AppData\Local\Temp` (**31 chars**);
  run-01 requested basetemp `…\Temp\cf14fr1-with-hook` = **49 chars**.

## 3. Runs (commands frozen here; observed values recorded in evidence/handoff — never by editing this file)

Raw-capture protocol (F4-style, applies to every label): byte-level OS redirection
(`cmd /c '… > file 2>&1'`), labels WRITE-ONCE (a label whose output exists is never
overwritten; a re-run needs a new label + disclosure), rc recorded separately,
`evidence/SHA256SUMS.txt` pins every byte stream after the runs. Env for every run:
`PYTHONUTF8=1` (deterministic UTF-8 byte streams for capture), `PYTHONDONTWRITEBYTECODE=1`
(read-only CW tree), `CW_BASETEMP_DECISION_FILE=<this attempt>\evidence\<label>.decision.jsonl`,
`CW_SHORT_BASETEMP_DISABLE` **absent** except where a run says otherwise.

| label | command (cwd = CW root) | env delta | expected-to-record |
|---|---|---|---|
| `01_with_hook` | `python -m pytest -q tests/contract tests/unit --basetemp %TEMP%\cf14fr1-with-hook` | hook ACTIVE (no disable env) | raw stdout+stderr byte-preserved in `evidence/01_with_hook.txt`; a decision line exists whose arithmetic is **pre-computed at freeze: len 49 ≤ 60 ⇒ `reason=within-budget`, `relocated=false`** (hook evaluated and NO-OP'd — this is the within-budget branch of the 150/60 logic, itself the observation: the repo-global hook must not disturb the broader suite); per-file inventory; rc recorded. Any deviation from the pre-computed decision is recorded as a deviation. |
| `02_<stem>_rerun` (one per failing file) | `python -m pytest -q tests/<root>/<file> --basetemp %TEMP%\cf14fr1-with-hook` | **`CW_SHORT_BASETEMP_DISABLE=1`** (hook redirect disabled — the conftest disable env read at freeze) | a decision line `reason=disabled-by-env` (proof the control really ran with the redirect off); the file's outcome with the redirect off, for the attribution delta in §4 A4. |
| `03_redirect_probe` | `python -m pytest -q tests/contract/test_short_basetemp_convention.py --basetemp %TEMP%\cf14fr1-deep\over-budget-basetemp-for-redirect-probe` (path **84 chars**, > 60 — measured at freeze) | hook ACTIVE | direct redirect evidence, because run 01 is a within-budget NO-OP by arithmetic: decision line **`reason=resolved-basetemp-exceeds-budget`, `relocated=true`**, `effective_basetemp` under `%TEMP%\cw-pytest-basetemp\…` (len ≤ 60), cleanup line **`removed=true`**, and the requested over-budget dir NEVER created. This makes "hook's basetemp redirect observed via decision.jsonl evidence" literally true for this repo state. |

Exit-code legend: pytest rc 0 = all collected nodes passed; rc 1 = ≥1 node failed or
collection/harness error — **the per-node outcomes in the raw output are authoritative**;
the raw rc alone never decides anything (recorded, not interpreted as a verdict).

## 4. ORACLE ASSERTIONS — expected-to-record (this is a SAMPLE; all-green is NOT demanded)

- **A1 — raw output byte-exact.** Every label's stdout+stderr exists on disk, is pinned
  (bytes + sha256) in `evidence/SHA256SUMS.txt`, and is never re-written after the run.
  Write-once; a burned label is disclosed, not overwritten.
- **A2 — hook-effect evidence.** `evidence/01_with_hook.decision.jsonl` contains ≥1
  `event=decision` line for run 01 (pre-computed: within-budget / not relocated, quoted
  verbatim in `decision.md`); `evidence/03_redirect_probe.decision.jsonl` contains the
  `relocated=true` decision **and** the `cleanup removed=true` record (the 150/60 logic
  FIRING, quoted verbatim), with the corresponding `CW-BASETEMP-DECISION` /
  `CW-BASETEMP-CLEANUP` stdout lines quoted from the raw outputs. Which branch fired is
  an OBSERVATION; both branches must be evidenced across the card (01 = no-op branch,
  03 = firing branch).
- **A3 — per-file pass/fail/skip inventory.** `evidence/summary.json` records, for every
  collected file under both roots, counts of pass/fail/skip/error/xfail/xpass, per-root
  totals and grand totals; totals must reconcile with the raw output's final summary line
  (e.g. `N passed, M failed, K skipped in Ts`) — a reconciliation mismatch is itself
  recorded, not smoothed. Cross-check: `.pytest_cache/v/cache/lastfailed` is copied to
  `evidence/00_baseline_lastfailed.json` BEFORE run 01 and to
  `evidence/01_with_hook.lastfailed.json` after it; new failures = post − pre.
- **A4 — every failure attributed (pre-existing vs hook-induced).** For EACH failing
  file: run `02_<stem>_rerun` (same file, `CW_SHORT_BASETEMP_DISABLE=1`, same basetemp),
  then record in `decision.md`'s attribution table: failing node set with hook vs without
  hook, quoted delta of node sets and failure-message heads, and a verdict:
  - `pre-existing` — control reproduces the same failing node set (same nodes, same
    failure class) with the redirect OFF;
  - `hook-induced` — control passes where the main run failed, or failure class changes
    to/from path-length/`WinError 206`/basetemp/redirect;
  - `environmental` — failure is hermetic/credential/infra shaped and unrelated to the
    hook in either arm (still stated with the delta).
  Suspicion triggers (always get the delta quoted, never a bare verdict): failure message
  mentions `basetemp`, `WinError 206`, `ERROR_FILENAME_EXCED_RANGE`, path length, or
  `cw-pytest-basetemp`; or outcome differs between arms. Given run 01 is a within-budget
  no-op by arithmetic, the PRIOR expectation (not a demand) is `pre-existing` for
  identical arms — but the verdict is whatever the bytes say.
- **A5 — boundary held.** Post-run: all 268 sample files + the five anchor pins re-hash
  identical to freeze (esp. `dfb7c6cd…` contract test, `a908c9da…` conftest); CW root
  `__pycache__` still absent; tree scan discloses every file whose mtime fell inside the
  run window (expected: `.pytest_cache/**` only — its mtime impact recorded honestly in
  `decision.md`; anything else is disclosed as a test-induced write with file, mtime and
  owning test where determinable); no git command was executed by this card.
- **Explicitly NOT asserted:** zero failures; a specific pass count; acceptance of the
  condition; any change to I-14-F-R1's card, oracle, or the owner's E-1 ruling.

## 5. Deliverables (this attempt)

`oracle.md` (frozen first, this file) · `commands.json` (pre-registered argv/env/labels) ·
`binding.json` (live hashes at run time: hook + contract test + 268-file manifest + every
evidence byte stream) · `decision.md` (attribution table, hook-effect quotes, `.pytest_cache`
honesty note) · `evidence/` raw (`00_baseline_*`, `01_with_hook.txt`, `01_with_hook.rc.txt`,
`*.decision.jsonl`, `02_*_rerun.txt`, `03_redirect_probe.txt`, `sample_set_freeze.txt`,
`summary.json`, `tree_scan_after.json`, `SHA256SUMS.txt`) · `handoff.json`
(`status=review_pending`, `disclosure_adaptation=unmapped`, `accuracy=unproven`,
`signed=false`, implementer does not self-sign) · `recovery/README.md` (**nothing to
revert — no product writes were made**; only %TEMP% + this attempt artifacts, the fallback
dirs were self-cleaned by the hook, `.pytest_cache` is a pytest side effect not reverted).

## 6. Freeze declaration

This file, as hashed in `binding.json → oracle_frozen`, is FROZEN and was created before
any pytest process of this attempt. Later corrections, if any, are append-only
`## Revision rN` with a prefix-hash proof; the r1 bytes above are never edited.
