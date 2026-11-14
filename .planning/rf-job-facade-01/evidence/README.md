# rf-job-facade-01 acceptance evidence (OWNERPKG-REVENUE-FORECAST-01 §5)

Drill workspace: `C:/Users/郑曾波/Projects/rf-facade-drill` (fresh per run; offline
IsolatedLake fixture, reuse_only, zero new downloads, zero paid calls, zero
network egress).  Budget boundary was reported to the operator before the
first drill run (see progress.md 2026-11-08; boundary reported and confirmed
2026-11-07/08, drill executed and green 2026-11-08).

Reproduce:

```
C:/Miniconda/python.exe .planning/rf-job-facade-01/evidence/drill.py   # exit 0 = all PASS
C:/Miniconda/python.exe -m pytest tests/ -q -k rf_job                   # 36 passed
C:/Miniconda/python.exe -m pytest tests/test_rf_job_boundary_regression.py \
    tests/test_report_catalog_deployment.py -q                          # 45 passed
```

## §5.1 命令形状

- `help-root.txt`, `help-submit.txt`, `help-get-status.txt`, `help-act.txt`,
  `help-list-jobs.txt` — real `--help` output of every rf-job/1 route.
- Fixed argv (aligned with `rf-job/1`), see `drill.py` `_run_cli` and the
  module docstring of `scripts/rf_job_cli.py`.

## §5.2 幂等证明

- `drill_summary.json` step `5.2 idempotent resubmit (no re-orchestration)`:
  same `idempotency_key` -> same `owner_job_id`, `idempotent_replay=true`,
  `stage_attempts_before == stage_attempts_after` (zero re-orchestration),
  second submit wall time recorded.
- Unit pins: `tests/test_rf_job_cost.py::test_same_idempotency_key_returns_same_job_without_rerun`.

## §5.3 状态与恢复演练

- `drill_summary.json` steps `5.3 *` (all PASS):
  submit -> `taskkill /T /F` the process tree while the compute stage runs
  (after source durably completed) -> restart `get-status` (interrupted,
  status_known=true, cost unknown) -> `act reconcile` -> `act resume` ->
  `succeeded` with **source stage NOT re-run** (one attempt only; the killed
  compute attempt legitimately retried).
- `stage_attempts` in `drill_summary.json` carry per-stage `elapsed_seconds`
  and resource observations (honest timings).

## §5.4 失败 attempt 样本

- `natural_failure_jobview.json` — a real failed JobView (nonexistent
  company, natural filing-fetch failure, exit recorded, zero downloads).

## §5.5 费用投影

- `cost_known_sample.json` — `known`, `{"currency":"USD","value":"0.00"}`
  (every attempt observed: 0 downloads, 0 paid calls).
- `cost_unknown_sample.json` — `unknown`, `cost=null` (killed attempt left
  no resource observations; never invented).

## §5.6 边界回归

- `tests/test_rf_job_boundary_regression.py` (7 tests) pins the nine
  READ_ONLY_COMMANDS, `WRITE_COMMANDS={"import-w09"}`,
  `assert_read_only_command` refusal, and that the facade widens no seam.
- `tests/test_report_catalog_deployment.py` (38 tests, existing) still green:
  45 passed together, exit 0.

## §5.7 诚实标注 (NOT_RUN / limits)

- **NOT_RUN**: cross-repo real production run against the real company-wiki
  and filing-fetch checkouts (the drill runs the real CLIs offline against
  the isolated-lake fixture instead).  Reason: budget gate — production runs
  are reserved for owner-approved drills only; the fixture path exercises the
  same subprocess contracts with zero downloads.
- **NOT_RUN**: catalog admission via
  `report_catalog_identity_cli.py import-research-attempt` — intentionally
  out of facade scope (G-m8-RF-05); the facade only produces the
  registration-ready evidence (stage artifacts + SHAs).
- `unit tests / FakeStageRunner` are NOT claimed as cross-repo evidence; only
  the drill and the real-subprocess tests in `tests/test_rf_job_facade_cli.py`
  are process-level evidence.
- Drill observations: `acquisition_calls` (local company-wiki subprocess
  count from filing-fetch stderr) is never treated as a paid model call.
- Known limitation: a job recovered from a kill keeps `cost_state=unknown`
  while any attempt lacks observations (honest, not backfilled).
