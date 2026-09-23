# GATE-OQ-FIX — Oracle (FROZEN BEFORE ANY CHANGE)

- Card: `GATE-OQ-FIX`
- Plan: `C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit`
- Attempt: `execution_runs/GATE-OQ-FIX/a20260922-01`
- Freeze rule: this file is written and its sha256 recorded in `evidence/oracle_freeze.json`
  **before any byte of `tools/pre_push_gate.py` or `tests/test_fc1105_fault_injection.py`
  is modified**. Any predicate change after freeze is a disclosed oracle revision, never a
  silent edit.

## 1. Authorization (owner ruling, verbatim)

`OWNER_DECISIONS.md` §十八（【已裁定·第四批】，原话逐字）:

> 「A-1: 1, A-2: 授权, B: 全批， C:更新函件」

§十八 table row:

> `| **B = 全批** | §十七 B-1..B-7 **全部批准** | … ②OQ-01/02 修复卡 `GATE-OQ-FIX` 已派（4e29afc4）：real-data 步 1200→1800（仅该步）、f2 内部 timeout 120→300；③**父保留各仓提交权**（卡交付证据后由父分仓提交） |`

§十七 B-7 row (the item being cleared):

> `| B-7 | GATE OQ-01/02：real-data 单独预算复核、f2 timeout=120 脆弱性 | 登记未决 |`

**Authorized production changes — exactly TWO, in exactly two files:**

1. `tools/pre_push_gate.py`, function `_real_data()`'s `_run(...)` call only: pass an
   explicit `timeout=1800` argument (real-data step budget 1200→1800, **that step only**;
   every other step keeps the `_run` default `timeout: int = 1200` from GATE-TIMEOUT-1200).
2. `tests/test_fc1105_fault_injection.py`, the `_t2()` helper's internal
   `subprocess.run(... timeout=120 ...)` → `timeout=300` (the single `120` literal in the
   file, line 60 — the helper that `test_f2_missing_samples_fails` invokes).

Nothing else in either file may change. No gate flag. No full gate run by this card
(the parent's batch-4 push runs the gate live). No git writes. No load faking.

## 2. Given evidence (given as already-confirmed; restated, NOT re-litigated)

From `execution_runs/GATE-TIMEOUT-1200/a20260922-01`:

1. **OQ-01 evidence** (`after/gate_green_1200.txt` + `commands.json` G1): under
   extreme ambient load (that card's 8 burners + orchestration-measured 34 python
   procs at 08:13:29Z incl. other sessions), the **real-data step wall = 1182.3 s
   against the 1200 s cap → ~17.7 s margin (~1.5% of the cap)**, while pytest inside
   it reported `1159.84s`; the step completed but the gate went RED because a test
   inside it failed. In the RED-comparable load domain the same step took **691.71 s**
   (GREEN attempt #2).
2. **OQ-02 evidence** (same file, line 65-66): `FAILED
   tests/test_fc1105_fault_injection.py::TestFaultInjection::test_f2_missing_samples_fails`
   — its internal subprocess `timeout=120` was exceeded under that load.
   Standalone, light load: **`1 passed in 44.00s`**
   (`evidence/f2_standalone_lightload.txt`) → load-induced, not code-induced.
3. The prior card's `handoff.json` OQ-01/OQ-02 wording and `reviewer_report.md` L10:
   "extreme ambient can still exceed 1200 s, which is an owner call outside §16-B
   (OQ-01)"; "f2 helper internal `timeout=120` fragility, registered-not-fixed, passes
   standalone 44 s". Both are now ruled by §十八 B=全批.

## 3. Machine context recorded at freeze time

- CPU: 10 cores / 12 logical processors; RAM ≈ 16 GB; OS Windows.
- Interpreter: `C:\Miniconda\python.exe` (Python 3.13.9).
- Repo HEAD at freeze: `4b1c690b8b798e521cf0c59b538bb1522a5a107c`.
- `git status --porcelain -- tools/pre_push_gate.py tests/test_fc1105_fault_injection.py`
  at freeze: **EMPTY** (both target files clean vs HEAD).
- **before sha256 `tools/pre_push_gate.py`** (= GATE-TIMEOUT-1200's authorized after hash):
  `cf09ade8164e89d79237ff5a8409496ab1ae2a9c5f3ee2c253ccad20ef06df0b`
- **before sha256 `tests/test_fc1105_fault_injection.py`**:
  `0bcd7ac81dba2c03362c9d0fa21ef59188f096f872b49e6efffc9cb028a0856e`
- Byte copies: `before/pre_push_gate.py.orig`, `before/test_fc1105_fault_injection.py.orig`.
- Ambient python processes at freeze: 2 (shared machine; this card starts NO burners —
  no load is induced, faked, or inflated by this card).
- Parallel cards are running (full porcelain shows other `.planning/**` modifications);
  this card's production scope is only the two files above.

## 4. Expected after-states (pre-registered; verified by hash + diff after the edits)

### Fix 1 (OQ-01) — `tools/pre_push_gate.py`

`_real_data()`'s `_run(...)` call grows ONE line:

```python
    return _run(
        [sys.executable, "-m", "pytest", "-q", "--tb=line", *REAL_DATA_TESTS],
        "real-data suite (production catalog; CI needs a self-hosted runner)",
        timeout=1800,
    )
```

- numstat for this file: **1 added, 0 deleted** (a new `timeout=1800,` line).
- `_run` signature default stays `timeout: int = 1200` (untouched — the other steps,
  including real-roots E2E, keep 1200).
- After-hash computed post-edit and recorded in `binding.json` / `handoff.json`
  (NOT precomputable — it is the measurement, not a prediction target).

### Fix 2 (OQ-02) — `tests/test_fc1105_fault_injection.py`

Line 60, the `_t2()` helper, exactly one literal flips:

- before: `        capture_output=True, text=True, encoding="utf-8", timeout=120,`
- after:  `        capture_output=True, text=True, encoding="utf-8", timeout=300,`

- numstat for this file: **1 added, 1 deleted**.
- Expected total numstat across both files: **2 added, 1 deleted** ("tiny").
- Cross-check: flipping that literal back to `120` must reproduce the before-hash
  `0bcd7ac8…856e` byte-exactly (it is the ONLY change).

### Scope predicates (invariants)

- **I-1 (surgical scope)**: `git diff --numstat -- tools/pre_push_gate.py
  tests/test_fc1105_fault_injection.py` shows only those two files, total `2 1`;
  `git diff` hunks touch ONLY the two authorized lines described above.
- **I-2 (no bypass)**: no `--skip-*`, `-k`, `--deselect`, `-x`, or any flag is passed
  to the gate or to the f2 test run; the f2 run selects the exact node id
  `tests/test_fc1105_fault_injection.py::TestFaultInjection::test_f2_missing_samples_fails`.
- **I-3 (no full gate run)**: this card executes NO `python tools/pre_push_gate.py`
  gate run (only `--help` smoke, which argparse answers before any gate step).
- **I-4 (no git writes)**: only read-only `git status/diff/numstat/rev-parse`.

## 5. Verification plan (pre-registered)

1. **Syntax/integrity of the gate file**: `python -m compileall tools/pre_push_gate.py`
   → rc 0 (raw output in `evidence/compileall.txt`), plus `python -c "import ast; ..."`
   parse of both files → rc 0 (`evidence/ast_check.txt`).
2. **Smoke**: `python tools/pre_push_gate.py --help` → rc 0, argparse usage printed,
   NO gate step executed (`evidence/help_smoke.txt`).
3. **Lint (extra, read-only)**: `ruff check tools/pre_push_gate.py
   tests/test_fc1105_fault_injection.py` → rc 0 expected (`evidence/ruff_two_files.txt`).
4. **Fix-2 standalone run (PASS expected)**: exact node id, `-q --tb=short`,
   raw stdout preserved → `evidence/f2_standalone_timeout300.txt`; expect
   `1 passed` in the 44–46 s band (ambient python count snapshotted alongside).
5. **Mutation-style honesty check**: temporarily set the literal back to `120`
   (byte-state must equal the before-hash) → re-run the same standalone command →
   expected STILL PASS in the same band (`evidence/f2_mutation_120_rerun.txt`) →
   restore `300` → re-verify after-hash equality.
   **Pre-registered reading**: a standalone PASS at both 120 and 300 proves the fix is
   NOT load-proven standalone. Honest conclusion (mandated wording): load-proof of
   `timeout=300` (and of the 1800 step budget) requires the **batch-4 push's live
   gate run under load** (§十八 执行序: "batch-4 提交+推送（门实跑验证 OQ-01/02 的
   负载侧 GREEN）"), which this card does NOT run.
6. **GREEN evidence plan (recorded, not executed here)**: the next batch push runs the
   gate live with both fixes on disk; its real-data step (a) completes within 1800 s
   and (b) passes `test_f2_missing_samples_fails` under that push's ambient load.
   Owed to: parent's batch-4 push. This card does not run the full gate.

## 6. Why 1800 and 300 (arithmetic pre-registered; decision.md carries the full derivation)

- **1800** = 1.5 × 1200. Worst measured real-data step = 1182.3 s (extreme ambient);
  `1800 − 1182.3 = 617.7 s` headroom (~+52% inflation tolerated vs ~1.5% at 1200:
  `1800 / 1182.3 ≈ 1.52`). Covers the normal-domain 691.71 s at ≈2.6×. Bounded —
  NOT unbounded: a genuine hang still kills the step instead of hanging a push forever.
- **300** ≈ 6.8–7 × the 44.00 s standalone (`300 / 44.00 ≈ 6.82`); the observed load
  failure means inflation ≥ `120 / 44 ≈ 2.7×` already happened once, and 300 absorbs
  ≈2.5× more than 120 did. Bounded — NOT unbounded, so a real hang still trips.

## 7. Boundaries

- Only `tools/pre_push_gate.py` (one explicit `timeout=` argument) and
  `tests/test_fc1105_fault_injection.py` (the one timeout literal) may change.
  Mutation step 5 must restore the final state to `300` (after-hash re-verified).
- All other writes stay inside this attempt directory.
- No git commit/add/push/stash/checkout/reset/restore (parent commits, per §十八 ③).
- No full gate run; no load faking/inflating; no network; no production data changes.
- `disclosure_adaptation = unmapped`, `accuracy = unproven` — these two timeout
  parameters qualify no formula, no disclosure mapping, no accuracy claim.
- `handoff.json` status = `review_pending`; implementer never signs acceptance.

## 8. Capture rules

- Raw stdout of every verification command → `evidence/` (byte-faithful, rc recorded).
- Command ledger with expected/raw rc → `commands.json`.
- Before/after sha256 + numstat → `binding.json`, `changes.diff`, `handoff.json`.
