# decision.md — GATE-TIMEOUT-1200 / attempt a20260922-01

Implementer record for owner ruling **§16 B = a**. Status handed off as
`review_pending`; this document is NOT an acceptance — an independent reviewer signs.

## 1. Ruling and authorized scope (verbatim)

`OWNER_DECISIONS.md` §16（第七批，原话逐字）: 「… **B: a（提高门超时到 1200，立卡红绿）** …」
表格行: `| **B = a** | 门超时 600→**1200**，立卡红绿 | 与建议一致（改门不绕门，全测照跑照判） | 待无-bug 确认回来后执行 |`
前置 §15 B（无-bug 确认）已由 given evidence 满足（oracle.md §2 原文重述，未复核）。

**The only production change** — `tools/pre_push_gate.py`, `_run()` signature default, line 73:

```diff
-    cmd: list[str], label: str, timeout: int = 600, *, blocking: bool = True
+    cmd: list[str], label: str, timeout: int = 1200, *, blocking: bool = True
```

| | sha256 |
|---|---|
| before / anchor / RED state | `0d290326200ebde819d3473589bd1aa0ed36da4806097d8a59dc8dc316fcc594` |
| after / authorized / GREEN state (final on disk) | `cf09ade8164e89d79237ff5a8409496ab1ae2a9c5f3ee2c253ccad20ef06df0b` |

- `git diff --numstat` = `1 1` (see `changes.diff`); no other byte of the gate differs.
- `oracle.md` frozen BEFORE the change (`evidence/oracle_freeze.json`:
  oracle sha256 `112fbe37…4b562`, gate untouched at freeze = before hash).
- **No `--skip-*` (no flag at all) was ever passed to the gate. No git add/commit/push
  by this attempt** — the parent commits.
- At close: `git status --porcelain -- tools tests e2e scripts` shows ONLY
  `M tools/pre_push_gate.py` (no test file touched).

## 2. RED arm — LIVE reproduced (mode = **live**, historical fallback NOT used)

Gate at anchor bytes (hash verified at start: `0d290326…`), invoked exactly
`C:\Miniconda\python.exe -u tools/pre_push_gate.py`, with exactly **8 CPU burners**
(`evidence/burners_red.json`, 8/8 alive, all stopped after).

- Window: `07:35:16.856Z → 07:46:32.438Z`, total **675.582 s**, gate **exit 1**.
- Steps 1–8 all `ok` (ruff 2.4 / compileall 1.4 / unique-symbols 5.2 / host-guard 9.9 /
  mypy 8.7 / meta-tests 32.3 / BOM 0.3 / install-check 14.2 — seconds).
- Step 9 `=== real-roots E2E ===` banner at +75.201 s; **killed at exactly 600 s**
  (`subprocess.TimeoutExpired … timed out after 600 seconds`) with the pytest argv naming
  **all 7 REAL_ROOTS_TESTS files, no skip/deselect flags**; no `pre-push gate GREEN` line;
  the real-data step was never reached.
- Full unfiltered capture: `after/gate_red_600.txt`; step times:
  `after/step_times_red_600.json`.

**RED verdict: predicate satisfied LIVE, under the pre-registered 8-burner load.**
Per oracle I-3, the killed run's own test count is recorded as
**"not observable (killed at 600 s)"** — never claimed as 55 passed, never read as a skip.

## 3. GREEN arm — two live attempts, disclosed separately

Gate at authorized bytes (hash verified at start of each: `cf09ade8…`), same invocation,
fresh identically configured **8 CPU burners** each time.

### 3.1 Attempt #1 — `after/gate_green_1200.txt` — **FAIL per oracle (not a timeout)**

- Window `07:47:30.351Z → 08:19:35.035Z`, total 1924.684 s, gate **exit 1**.
- Steps 1–9 all `ok` — **E2E completed in 687.506 s** (would have been killed by the old
  600 cap; the 1200 cap accommodated it).
- real-data **completed in 1182.3 s wall (pytest 1159.84 s < 1200 — no TimeoutExpired)**
  but with **`1 failed, 63 passed, 1 xfailed`**:
  `tests/test_fc1105_fault_injection.py::TestFaultInjection::test_f2_missing_samples_fails`
  ⇒ gate RED at real-data ⇒ oracle GREEN predicate NOT met ⇒ recorded **FAIL**.

**Load domain of attempt #1 (REM-79 rule — domain stated in the same sentence):**
under this machine's concurrent load at that window — this card's 8 burners plus a
mid-run python-process count of **20 at 08:08:35Z** (of which 8 = this card's burners)
and the orchestration layer's independent measurement of **34 python processes at
09:13:29 local (08:13:29Z)** including other sessions' campaigns (I-14-E-APPLY burners /
pytest) — the real-data suite **completed within 1200 s but one test failed**.
The correct statement is 「**在本机当时并发负载（实测 python 进程数 34 / 快照 20，含其他会话战役）下 real-data 步完成但 1 个测试失败**」.
It is explicitly **NOT** claimed that "1200 s is insufficient for this suite" —
the suite finished inside 1200 s in this very attempt.

Corroborations (both captured):
- The failed test run **standalone under light load: `1 passed in 44.00 s`**
  (`evidence/f2_standalone_lightload.txt`) ⇒ the failure is **load-induced** (the test's
  own helper `subprocess.run(..., timeout=120)`), not deterministic, and not caused by the
  one-line change (the line only raises the gate's own subprocess cap).
- The attempt #1 summary's `1 xfailed` is a **pre-existing static marker** at
  `tests/test_fc1001_isolated_lake.py:146` (`pytest.param(..., marks=pytest.mark.xfail(...))`)
  — present in source before this card; nothing new was marked.

Attempt #1 evidence is preserved byte-for-byte; it was never overwritten.

### 3.2 Attempt #2 (same-domain control, per orchestration instruction) — `after/gate_green_1200_attempt2_samedomain.txt` — **GREEN**

Same configuration as the RED arm's domain: ambient python = **2** before burners,
8 burners started (8/8 alive, `evidence/burners_green2.json`), mid-run snapshot
python = 12 (= 8 burners + gate + pytest + ambient 2, `evidence/load_snapshot_green2_mid.json`),
ambient back to 2 after stop (`…green2_end.json`).

- Window `08:24:55.688Z → 08:47:12.422Z`, total **1336.734 s**, gate **exit 0**, final line
  `pre-push gate GREEN — safe to push (then self-monitor CI).`
- **Every step `ok`, no FAILED, no TimeoutExpired.**

Per-step wall times (banner-to-banner, `after/step_times_green_1200_attempt2.json`):

| # | step | wall (s) |
|---|---|---|
| 1 | ruff (CI WU-1.2 full scope) | 2.05 |
| 2 | compileall | 1.32 |
| 3 | unique test symbols (CI WU-1.1) | 1.54 |
| 4 | host assumption guard (FC-1307-a) | 9.35 |
| 5 | mypy public contracts (FC-1204-c) | 3.52 |
| 6 | meta/binding tests | 33.82 |
| 7 | UTF-8 BOM scan | 0.41 |
| 8 | installed-skill consistency (check only — passed, no sync applied) | 3.89 |
| 9 | **real-roots E2E (55 tests)** | **588.64** |
| 10 | **real-data suite (65 tests)** | **691.71** |
| — | total gate run | 1336.73 |

**GREEN verdict: predicate satisfied LIVE in the RED arm's load domain (attempt #2).**

## 4. Invariant (both arms) — evidence

- **I-1 selection / no bypass:** RED-state file ≡ anchor bytes (hash-verified at arm
  start); GREEN-state file ≡ anchor + the one line (hash-verified at arm start and at
  close). `changes.diff` numstat `1 1`. The RED traceback shows the gate's own pytest argv
  with all 7 files and no skip/deselect/`-k`/`-x`; GREEN uses the same source lines (only
  the timeout number differs — the timeout never enters the pytest argv).
  No test file modified (git status).
- **I-2 counts, live:** because the gate discards successful subprocess output (prints
  only `ok`), the summaries were reproduced with the gate's **exact argv**, standalone,
  light load (ambient 2, no burners), rc captured:
  - E2E (7 files): **`55 passed` in 185.96 s, rc=0, no skipped line** ⇒ **55 passed,
    0 skipped** (`evidence/invariant_e2e_55_count_check.txt`).
  - real-data (10 files): **`64 passed, 1 xfailed, 2 warnings` in 246.64 s, rc=0,
    0 skipped** = 65 total (`evidence/invariant_realdata_count_check.txt`); the xfail is
    the pre-existing marker above, so **no new skip/xfail/deselect exists**.
  - GREEN attempt #1's live real-data summary: `1 failed, 63 passed, 1 xfailed` = 65,
    0 skipped (same total, load-induced failure only).
- **I-3 RED caveat (pre-registered):** RED's own count = "not observable (killed at 600 s)".

## 5. Errors encountered during this attempt (logged, not hidden)

| # | what | disposition |
|---|---|---|
| E-1 | First RED driver launch failed before any work: BOM-less `.ps1` with non-ASCII path literals was decoded as ANSI by Windows PowerShell 5.1 (path mangled). Gate hash check failed → script aborted. | **No burners started, no gate run, gate untouched** — logged `after/red_driver_log_attempt1_FAILED_encoding.txt`; drivers rewritten ASCII-only with `$PSScriptRoot` derivation and byte-verified (0 non-ASCII bytes). Does NOT consume the single bounded RED gate attempt. |
| E-2 | `git status` warnings about permission-denied scratch dirs under `.planning/…/reviews/*/scratch` and `.tmp-zr408-unit*` (pre-existing) | warning only; snapshots written |
| E-3 | real-data warnings `UnicodeDecodeError: 0xd4` in pytest reader threads (`test_install_sync_gate_detects_drift`, GBK byte in child output) | pre-existing warnings class, non-fatal (suite rc=0 in GREEN #2); registered below as a gap |
| E-4 | GREEN attempt #1 real-data `1 failed` under higher ambient load | disclosed in §3.1 with domain; load-induced (standalone 44 s pass); attempt #2 same-domain GREEN |

## 6. Remaining gaps / non-claims

1. **`disclosure_adaptation = unmapped`, `accuracy = unproven`** — this card proves only
   the gate-timeout red/green behavior.
2. **real-data margin under extreme ambient:** attempt #1 finished the real-data step in
   1182 s wall against the new 1200 cap (a 18 s margin) while one of its tests already
   failed on its own internal 120 s timeout. If ambient load grows further, the real-data
   step can still exceed 1200 s — in that case the honest verdict is
   「在实测 N python 进程的并发负载下未完成」, **not** 「1200 不足」 (REM-79 domain rule).
   Registering, not deciding: whether real-data deserves its own (larger or load-aware)
   budget / test-level timeout review is an owner call, NOT covered by §16-B.
3. **Load-induced test fragility exists at test level** (`_t2(..., timeout=120)` in
   `test_fc1105_fault_injection.py`): observed once under heavy ambient; passes standalone.
   Registered as a gap; fixing tests was not authorized here.
4. **Both arms ran with python `-u`** (capture-fidelity flag; no gate logic change) and no
   gate flags. Gate success output is discarded by the gate itself — hence the standalone
   count-check runs in §4 (same argv, disclosed).
5. **No commit/push was made by this attempt** (only read-only git status/diff/rev-parse).
   At closing time the orchestration layer's own commit job had already committed the
   authorized line as **`6f74b056`** ("… gate timeout 600->1200 (live RED/GREEN pair) …";
   `HEAD:tools/pre_push_gate.py` blob `483486bd…` = the authorized post-image this attempt
   measured), so the scoped `git status` for `tools/tests/e2e/scripts` is now clean —
   that commit was the parent's, not this attempt's. `handoff.json` = `review_pending`;
   implementer did not sign.

## 7. What a reviewer should check

1. `binding.json` anchors vs live: re-hash `tools/pre_push_gate.py` = `cf09ade8…6df0b`;
   `before/pre_push_gate.py.orig` = `0d290326…c594`; `changes.diff` = 1 line.
2. `after/gate_red_600.txt` (RED, live) vs `after/gate_green_1200_attempt2_samedomain.txt`
   (GREEN, live, same domain) — both arms' load records in `evidence/burners_*.json` and
   `evidence/load_snapshot_*.json`.
3. `after/gate_green_1200.txt` = attempt #1 FAIL (high ambient), preserved, with the
   domain sentence of §3.1.
4. Invariant files `evidence/invariant_*_count_check.txt` (55 passed 0 skipped /
   64 passed 1 xfailed 0 skipped).
5. Oracle freeze chain: `evidence/oracle_freeze.json` precedes
   `evidence/line_change.json` in time.
