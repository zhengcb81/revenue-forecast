# B5 / REM-21 — propagation contract (frozen; every batch subagent MUST follow)

Authority: `OWNER_DECISIONS.md` §13 **T1-8** (TIER-1, owner-authorized). Attempt root:

```
PLAN     = C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit
ATTEMPT  = <PLAN>\execution_runs\B5-plan-level-remediation\a20260921-01
```

## 0. Hard boundaries (violating any of these fails the batch)

1. **Never write anywhere under `execution_runs/<CARD>/` or `execution_runs/<BATCH>/`** — those are
   historical audit artifacts. Read them freely; write only under `ATTEMPT\<batch>\` and `ATTEMPT\_scratch\`.
2. **Never modify** any `before/`, `after/`, frozen `oracle.md`/`oracle.json`/`cases.json`,
   `run_result.json`, `commands.json`, `handoff.json`, or any recorded rc value.
3. **Production repos are READ-ONLY.** Never touch `C:\Users\郑曾波\Projects\revenue-forecast\scripts\`.
4. Only the batch's **own copy** of the runner changes, and that copy lives in `ATTEMPT\<batch>\`.
5. Do **not** use `C:\Miniconda\python.exe` to run a card runner — use the batch's own isolated venv
   interpreter (given per batch below), always with `-B`.
6. Never self-sign. Report `review_pending`. Do not accept your own work.

## 1. Reference implementation (the thing being propagated)

The only runner that already enforces per-case `expected` by **exact exception type name** is
**M17–M20**, `execution_runs/M17/a20260919-01/scripts/run_card.py`:

* authoritative sha256 `94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252` (36744 B)
* confirmed by the card's own `handoff.json`, `after/final_deliverable_hashes.json`,
  `evidence/M17/evidence_hashes.json`, and by the independent reviewer's **r3** verdict
  (`M17/a20260919-01/review.md` lines 409, 422, 518).

> NOTE — a widely-quoted hash `5307d2cc…` is a **superseded r2-generation** value (review.md line 162).
> The r3 verdict that accepted the runner records `94619a98…`. Use `94619a98…`; record the
> discrepancy, do not "fix" any historical file.

The comparison, verbatim in semantics (M17 runner lines 395–473, 538–550):

```python
# `expected` MUST be a bare exception type name (e.g. "ModelRegistryError").
# Comparison is EXACT TYPE-NAME EQUALITY. isinstance() must NOT be used: ModelRegistryError is a
# subclass of ValueError, so a declared "ValueError" would silently pass under isinstance().
unusable_declared = [c.get("id") for c in cases_doc["cases"]
                     if not (isinstance(c.get("expected"), str) and c["expected"].strip())]
cases_declared_ok = not unusable_declared
...
declared = case.get("expected")            # per case
...
raised_name = type(exc).__name__
declared_usable = isinstance(declared, str) and bool(declared.strip())
if not declared_usable:
    verdict = "NOT_JUDGED_declaration_unusable"      # judged = False; NOT a mismatch
else:
    declared_ok = (raised_name == declared)          # exact type-name equality
    if not is_target:            verdict = "FAIL_wrong_exception_type"
    elif not declared_ok:        verdict = "FAIL_declared_expectation_mismatch"
    else:                        verdict = "PASS_rejected"
```

Exit-code classification (frozen table, `START_HERE.md` §"rc 码表", lines 90–115):

```
rc=0  pass
rc=1  harness failure (unusable environment / missing file)      <- only where the batch already has it
rc=2  NO VERDICT, issued BEFORE any case can be judged: the frozen declaration itself is
      missing/unusable (reason "cases_json_declared_expectation_missing:<ids>")
rc=3  a judgement WAS possible and did not hold (nothing raised, wrong type, or declaration mismatch)
```

**Precedence**: unusable-declaration (2) is evaluated before case judging; a case that is
`NOT_JUDGED_declaration_unusable` must never, by itself, produce rc=3.

## 2. Required counters / fields (additive; keep every existing key)

* per negative case: `declared` (the raw value), `raised` (exact type name),
  `declared_expectation_ok` (bool|None), `declared_expectation_mismatch` (bool),
  `declared_expectation_not_met` (bool|None), `declared_expectation_comparison` (human string
  containing both the raised and declared names), `judged` (bool).
* `negative_counts`: `declared_expectation_mismatch`, `declared_expectation_not_met`,
  `declared_expectation_missing_in_cases_json`.
* `negative_summary`: `declared_expectations_in_cases_json` (sorted distinct),
  `declared_expectation_comparison` (e.g. `"exact exception type name == cases.json's per-case
  'expected' string (NOT isinstance)"`), `declared_expectations_enforced` = `true`.
* `exit_code_semantics`: add `cases_json_declared_expectations_usable`,
  `declared_expectation_mismatch_case_ids` (or `declared_expectation_mismatch_ids`),
  and a `reason_namespace` note that `FAIL_wrong_exception_type` is a SUBSET of
  `declared_expectation_mismatch` **when the declaration is usable**.

Do **not** remove or rename existing fields — downstream evidence files were generated from them.

## 3. Per-batch facts (measured by the B5 scan; do not re-derive, verify instead)

| batch | rep card | runner sha256 (12) | bytes | existing `expected` handling |
|---|---|---|---|---|
| M05-M08 | M05 | `fd3a11c9226a` | 14758 | none (rc 0/**2**/3, no rc=1) |
| M09-M12 | M09 | `997c553b0b9e` | 28912 | computes `raised_matches_expected_name` but does **not** gate on it |
| M13-M16 | M13 | `9e4a6450d6ab` | 32038 | set-level declaration gap check only |
| M21-M24 | M21 | `a5ee7599c37e` | 20133 | computes `expected_type_matches_raised` but does **not** gate on it |
| M25-M28 | M25 | `eab0116220df` | 22720 | whole-set "every case declares the same single value" gate only |
| M29-M31 | M29 | `9ea69c72dced` | 28242 | none (rc 0/1/2/3) |

All 31 cards' frozen `cases.json` were scanned: **347 cases, zero compound `expected`, zero missing,
zero non-string** — every `expected` is the bare type name `ModelRegistryError`. So exact-equality
comparison cannot produce a false red today (`evidence/b5_scan.json`).

## 4. How to run a batch's runner (proven pattern)

The `B` unit of each batch's own `commands.json` is the bound invocation
(`evidence/batch_invocations.json`). Reproduce it with every path redirected into your own scratch:

```
<batch-iso>\venv\Scripts\python.exe -X utf8 -B <your-copy>\run_card.py \
  --card <CARD> \
  --attempt   <ATTEMPT>\_scratch\<batch>\<arm>\          # scratch ROOT: reads <root>/evidence/<CARD>/*
  --code-root <ATTEMPT>\_scratch\<batch>\code_root       # copy of iso/checkout_scripts (2 files)
  --out       <ATTEMPT>\_scratch\<batch>\<arm>\out.json \
  [--run-result-out | --formula-out | --negative-out | --stdout-out | --stderr-out  ...]
```

* Build the scratch root as `_scratch/<batch>/<arm>/evidence/<CARD>/` containing a **copy** of the
  frozen `input.json`, `cases.json`, `oracle.json` (+ `negative_results.json` if the batch's argv
  referenced it). Copy with `Copy-Item`; never move, never edit the originals.
* `code_root` = copy of `<batch attempt>\iso\checkout_scripts\` (both `model_registry.py` and
  `model_extensions.py`); verify `model_registry.py` sha256 ==
  `9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f` before running.
* Pass **exactly the same optional output flags** the batch's own B unit used, pointed into the arm dir.
* `-B` everywhere: no `__pycache__` may be created anywhere, least of all in a historical dir.
* Capture the raw process exit code; a PowerShell wrapper must propagate the child rc
  (use `$LASTEXITCODE` / `exit $LASTEXITCODE`, or run the child directly).

## 5. The four arms every batch must produce

| arm | runner | scratch `cases.json` | required observation |
|---|---|---|---|
| **E** green control | **new** | frozen, unmodified | rc = **0**, all negatives `PASS_rejected`, `declared_expectation_mismatch = 0` |
| **F** mutation arm (the deliverable) | **new** | one negative case's `expected` → `"ValueError"` | rc = **3**, `declared_expectation_mismatch` ≥ 1, verdict shows `FAIL_declared_expectation_mismatch` (or the batch's equivalent mismatch label) |
| **B** inertness control | **old** (byte copy of the historical runner) | same mutated cases.json as F | rc = **0** (proves the OLD runner did not fire — this is the "fabricated green" the owner ruling names) |
| **G** rc-classification arm (prereq 2) | **new** | one negative case's `expected` key **deleted** | rc = **2**, `verdict = no_verdict`, reason names the case as having a missing/unusable declaration; that case must **not** be counted as a mismatch |

Pick the mutated case as the **first** negative case (lowest `id`) whose frozen `expected` is
`"ModelRegistryError"`; record its id. `ValueError` is the correct decoy because
`ModelRegistryError` subclasses it, so an `isinstance` check would let it through.

If the batch's runner has no `--run-result-out`-style flag for negatives, extract the fields you need
from whatever JSON it does write into the arm dir (and from stdout).

## 6. Required output per batch: `ATTEMPT\<batch>\evidence.json`

```json
{
  "batch": "M05-M08",
  "cards": ["M05","M06","M07","M08"],
  "runner_before": {"path":"<PLAN-relative>","sha256":"...","bytes":0},
  "runner_after":  {"path":"<ATTEMPT-relative>","sha256":"...","bytes":0},
  "diff_path": "<ATTEMPT-relative>/runner.diff",
  "diff_stats": {"added_lines":0,"removed_lines":0},
  "cards_cases_sha256": {"M05":"..."},
  "insertion_points": [{"file":"run_card.py","line":0,"what":"..."}],
  "arms": {
    "E": {"rc":0,"verdict":"...","declared_expectation_mismatch":0,"mutated_case":null,"note":"..."},
    "F": {"rc":3,"verdict":"...","declared_expectation_mismatch":1,"mutated_case":"N01","note":"..."},
    "B": {"rc":0,"verdict":"...","declared_expectation_mismatch":null,"mutated_case":"N01","note":"..."},
    "G": {"rc":2,"verdict":"no_verdict","declared_expectation_mismatch":0,"mutated_case":"N01","note":"..."}
  },
  "rc_codes_after": {"0":"pass","2":"no verdict ...","3":"..."},
  "isolated_code_root_sha256": {"model_registry.py":"9ec65295...","model_extensions.py":"9939480b..."},
  "historical_writes": [],
  "boundaries_respected": true,
  "unmet_prerequisites": [],
  "open_issues": []
}
```

Every claim in this file must be a **measured** value from a real run, with the raw rc read from the
process, not inferred. If an arm cannot be made to fire, say so plainly in `open_issues` and set
`boundaries_respected` honestly — a truthful negative is worth far more than a fabricated pass.

## 7. Report back

Return a short summary: batch, before/after sha256, arm rc values (E/F/B/G), the inserted
enforcement's line numbers, any prerequisite you found unmet, and any deviation from this contract
with its reason. Keep it under ~40 lines.

---

## 8. ERRATUM 1 (appended; **§3 and §5 are partly superseded — read this section as authoritative**)

**Trigger**: the M21-M24 worker measured arm B = **rc=3**, contradicting §5's prediction of rc=0.
Verified by the orchestrator directly in the historical bytes.

**§3's `expected`-handling column is WRONG for two batches.** §3's line for M21-M24 said
"computes `expected_type_matches_raised` but does **not** gate on it" — that is false:
`M21/a20260919-01/scripts/run_card.py:304` computes it and **`:312-313` gates the verdict on it**
(`elif not entry["expected_type_matches_raised"]: entry["verdict"] = "FAIL_expected_type_mismatch"`).
The same is true of M09-M12: `M09/a20260919-01/scripts/run_card.py:427` computes
`raised_matches_expected_name` and **`:430-431` gates on it**
(`elif is_target and entry["raised_matches_expected_name"]: PASS_rejected`).

**The `compares_raised_to_expected` flag in `evidence/b5_scan.json` is UNRELIABLE** — it was `false`
for all 8 batches, including the reference M17-M20 which provably compares. Superseded by
`evidence/ast_gate_analysis.json`, an AST analysis **self-tested against a positive control**
(M17-M20 → L3 true) and a negative control (M29-M31 → L3 false), which reports:

| batch | L1 reads `expected` | L2 computes equality | **L3 gates the verdict** | gate test |
|---|---|---|---|---|
| M01-M04 | yes | no | **no** | — |
| M05-M08 | yes | no | **no** | — |
| M09-M12 | yes | yes | **YES (already correct)** | `is_target and entry['raised_matches_expected_name']` |
| M13-M16 | yes | no | **no** | — |
| M17-M20 | yes | yes | **YES (reference)** | `not declared_ok` |
| M21-M24 | yes | yes | **YES (already correct)** | `not entry['expected_type_matches_raised']` |
| M25-M28 | yes | yes | **no** (whole-set `case_contract` gate only) | — |
| M29-M31 | yes | no | **no** | — |

**Corrected scope**: of the six authorized batches, **four genuinely lacked the per-case gate**
(M05-M08, M13-M16, M25-M28, M29-M31) and **two already had it** (M09-M12, M21-M24). The owner's
premise ("only M17-M20 compares `expected`") is **overstated**; the observation that the ruling
counts "four batches" happens to match, but the batch *labels* differ from the measured set.

**Corrected arm-B rule (§5 superseded on this point only)**:

> Arm B's rc is a **MEASUREMENT, not a prediction**. Report the real process exit code.
> `rc=0` ⇒ the historical runner did not gate (the "fabricated green"). `rc=3` ⇒ it **already
> gated**. Both are legitimate findings. Never adjust a measured value to fit §5.
> On `rc=3`, also set `"historical_runner_already_gated": true` and state in `open_issues` what
> the patch actually adds beyond what was already there.

Arms **E** (rc=0), **F** (rc=3) and **G** (rc=2) keep their expectations unchanged.

**Lesson registered** (this project's recurring family, cf. `T1-8/a20260920-03`'s own addendum
"a guard must itself be tested for FALSE POSITIVES and for DISCRIMINATION"): the orchestrator's own
first-pass scan was a guard that returned `false` everywhere and was therefore indistinguishable
from a correct discriminator until it was run against a known-positive control.
