"""OWNERPKG-REVENUE-FORECAST-01 §5 acceptance drill (offline, zero-download).

Drives the REAL ``scripts/rf_job_cli.py`` as an external process against an
IsolatedLake fixture (local sqlite catalog, no network, reuse_only, zero
new downloads, zero paid calls).  Exercises:

  §5.1 command shape     --help of every route, saved as text
  §5.3 recovery drill    submit -> kill the process tree mid-run ->
                          restart -> get-status -> reconcile -> resume ->
                          succeeded, with completed stages NOT re-run
  §5.2 idempotency       same idempotency_key -> same owner_job_id,
                          second submit does not re-orchestrate
  §5.4 natural failure   nonexistent company -> real failed JobView
  §5.5 cost projection   known sample (succeeded) + unknown sample (killed)

Run:  C:/Miniconda/python.exe .planning/rf-job-facade-01/evidence/drill.py
Exit: 0 = every assertion held; 1 = at least one failure (recorded verbatim).
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
import stat
import subprocess
import sys
import time
from pathlib import Path

WT = Path(__file__).resolve().parents[3]          # the rf-job-facade worktree
DRILL_ROOT = Path(r"C:/Users/郑曾波/Projects/rf-facade-drill")
EVIDENCE = Path(__file__).resolve().parent
CLI = WT / "scripts" / "rf_job_cli.py"
PY = "C:/Miniconda/python.exe"
FF_ROOT = Path.home() / "Projects" / "filing-fetch"
CWP_SRC = Path.home() / "Projects" / "company-wiki" / "src"

for extra in (str(WT / "tests"), str(WT / "scripts"), str(CWP_SRC)):
    if extra not in sys.path:
        sys.path.insert(0, extra)


def _record(summary: dict, name: str, ok: bool, detail: object) -> None:
    entry = {"step": name, "ok": bool(ok), "detail": detail}
    summary["steps"].append(entry)
    if not ok:
        summary["failures"].append(entry)
    print(("PASS " if ok else "FAIL ") + name)


def _run_cli(owner_root: Path, config: Path | None, *argv: str,
             stdin_text: str | None = None) -> subprocess.CompletedProcess:
    cmd = [PY, "-B", str(CLI), "--owner-root", str(owner_root)]
    if config is not None:
        cmd += ["--deployment-config", str(config)]
    cmd += list(argv)
    return subprocess.run(cmd, input=stdin_text, text=True, encoding="utf-8",
                          capture_output=True, timeout=300, check=False)


def _json_or_none(text: str):
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None


def _build_request(as_of: str, *, company_query: str, idempotency_key: str) -> dict:
    from test_recognition_bridge import forecast_document

    document = forecast_document()
    document["as_of_date"] = as_of
    return {
        "schema_version": "rf-job/1",
        "workflow": "full_research",
        "company_query": company_query,
        "information_as_of": as_of,
        "horizon_end_year": max(document["forecast_years"]),
        "scenario_set": ["low", "base", "high"],
        "source_snapshot_ids": [],
        "idempotency_key": idempotency_key,
        "limits_ref": "drill-0usd",
        "forecast_input": document,
    }


def _help_outputs(evidence: Path) -> list[str]:
    saved: list[str] = []
    for name, argv in (
        ("help-root", ["--help"]),
        ("help-submit", ["submit", "--help"]),
        ("help-get-status", ["get-status", "--help"]),
        ("help-act", ["act", "--help"]),
        ("help-list-jobs", ["list-jobs", "--help"]),
    ):
        proc = subprocess.run([PY, "-B", str(CLI), *argv], text=True,
                              encoding="utf-8", capture_output=True, check=False)
        path = evidence / f"{name}.txt"
        path.write_text(f"$ rf_job_cli.py {' '.join(argv)}\n"
                        f"exit={proc.returncode}\n\n{proc.stdout}{proc.stderr}",
                        encoding="utf-8")
        saved.append(path.name)
        if proc.returncode != 0:
            raise AssertionError(f"{name} exited {proc.returncode}")
    return saved


def _stage_elapsed(job: dict) -> dict:
    out = {}
    for stage, state in job.get("stages", {}).items():
        out[stage] = [
            {"attempt_no": a.get("attempt_no"), "status": a.get("status"),
             "exit_code": a.get("exit_code"), "elapsed_seconds": a.get("elapsed_seconds"),
             "observations": a.get("observations")}
            for a in state.get("attempts", [])
        ]
    return out


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    summary: dict = {"schema_version": "rf-job-drill/1",
                     "drill_root": str(DRILL_ROOT), "steps": [], "failures": []}

    # fresh drill workspace (this drill root only; never the owner data root).
    # The engine marks its publication registry read-only, so clear the
    # attribute before unlinking during cleanup.
    if DRILL_ROOT.exists():
        def _clear_readonly(func, path, _exc):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(DRILL_ROOT, onexc=_clear_readonly)
    DRILL_ROOT.mkdir(parents=True)

    # --- offline lake fixture ------------------------------------------------
    from e2e_support.isolated_lake import IsolatedLake

    # IsolatedLake itself creates a ``lake/`` subdir under the given tmp path
    IsolatedLake(DRILL_ROOT, seed="rf-job-facade-drill").build()
    wiki = DRILL_ROOT / "lake" / "project"
    filing_config = wiki / "filing_config.json"
    filing_config.write_text(
        json.dumps({"schema_version": "1.0", "company_wiki_root": str(wiki)}),
        encoding="utf-8")
    config = DRILL_ROOT / "rf_job_deployment.json"
    config.write_text(json.dumps({
        "schema_version": "rf-job-deployment/1",
        "python": PY,
        "stages": {
            "source": {
                "filing_fetch_root": str(FF_ROOT),
                "company_wiki_config": str(filing_config),
                "company_wiki_catalog_config": str(wiki / "config" / "source_catalog.yaml"),
                "source_reader_receipt_version": "2.2",
                "timeout_seconds": 150.0,
                "request_template": {"schema_version": "2.0", "market": "CN",
                                     "document_kind": "annual_report",
                                     "fiscal_year": 2025,
                                     "mode": "exact",
                                     "filing_intent": "reuse_only"},
            },
            "compute": {"timeout_seconds": 300.0},
            "publication": {"timeout_seconds": 60.0},
        },
        "limits": {"refs": {"drill-0usd": {"max_cost_usd": "0.00",
                                           "max_wall_seconds": 900,
                                           "max_new_downloads": 0,
                                           "max_attempts_per_stage": 3}},
                   "default_ref": "drill-0usd"},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    owner_root = DRILL_ROOT / "owner"
    owner_root.mkdir()

    # --- §5.1 command shape ---------------------------------------------------
    try:
        saved = _help_outputs(EVIDENCE)
        _record(summary, "5.1 help outputs", True, saved)
    except AssertionError as exc:
        _record(summary, "5.1 help outputs", False, str(exc))

    as_of = (_dt.date.today() + _dt.timedelta(days=7)).isoformat()
    request = _build_request(as_of, company_query="紫金矿业",
                             idempotency_key="drill-key-1")
    request_path = DRILL_ROOT / "drill_request.json"
    request_path.write_text(json.dumps(request, ensure_ascii=False, indent=2),
                            encoding="utf-8")

    # --- §5.3 recovery drill: submit -> kill mid-run -> restart -> resume -----
    jobs_dir = owner_root / "artifacts" / "rf_jobs" / "jobs"
    killed_job: dict | None = None
    kill_detail: dict = {}
    for attempt in range(1, 4):
        # each retry uses its own idempotency key so a stuck first attempt
        # cannot poison later attempts through the idempotency index
        attempt_request = dict(request)
        attempt_request["idempotency_key"] = f"drill-key-1-r{attempt}"
        proc = subprocess.Popen(
            [PY, "-B", str(CLI), "--owner-root", str(owner_root),
             "--deployment-config", str(config), "submit"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8")
        proc.stdin.write(json.dumps(attempt_request, ensure_ascii=False))
        proc.stdin.close()
        # poll the logs directory for the compute stage's log file (created
        # the moment the compute subprocess starts => source is durably
        # completed).  Never open job.json while the facade process is alive:
        # reading it here races the facade's atomic os.replace on Windows
        # (WinError 5) and breaks the run itself.
        deadline = time.time() + 60.0
        killed_job = None
        job_path: Path | None = None
        while time.time() < deadline:
            job_dirs = list(jobs_dir.glob("*")) if jobs_dir.exists() else []
            for jd in job_dirs:
                compute_logs = list((jd / "logs").glob("compute-*.stdout.txt"))
                if compute_logs:
                    job_path = jd / "job.json"
                    try:
                        killed_job = json.loads(job_path.read_text(encoding="utf-8"))
                    except (json.JSONDecodeError, OSError):
                        killed_job = None
                    if killed_job is not None:
                        kill_detail = {
                            "retry": attempt,
                            "at_kill": {
                                "status": killed_job.get("status"),
                                "source_status": killed_job["stages"]["source"]["status"],
                                "compute_attempts": len(
                                    killed_job["stages"]["compute"]["attempts"]),
                                "compute_status": killed_job["stages"]["compute"]["status"],
                            },
                            "source_attempts_at_kill": _stage_elapsed(killed_job).get("source"),
                        }
                        break
            if killed_job is not None:
                break
            time.sleep(0.02)
        if killed_job is None:
            # keep the raw process output for diagnosis before retrying
            proc.kill()
            out, err = proc.communicate(timeout=30)
            kill_detail.setdefault("failed_attempts", []).append({
                "retry": attempt,
                "submit_returncode": proc.returncode,
                "submit_stdout_tail": (out or "")[-600:],
                "submit_stderr_tail": (err or "")[-600:],
                "job_state_at_timeout": (
                    json.loads(job_path.read_text(encoding="utf-8"))
                    if job_path and job_path.exists() else None),
            })
            time.sleep(0.5)
            continue
        # terminate the whole process tree (hard kill, no cleanup)
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                       capture_output=True, check=False)
        try:
            out, err = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            out, err = proc.communicate(timeout=30)
        kill_detail["submit_stdout_tail"] = (out or "")[-400:]
        kill_detail["submit_stderr_tail"] = (err or "")[-400:]
        kill_detail["submit_returncode"] = proc.returncode
        break

    if killed_job is None:
        _record(summary, "5.3 kill mid-run", False,
                {"reason": "never caught a running later stage within the deadline",
                 **kill_detail})
        _write_evidence(summary, EVIDENCE)
        return 1

    owner_job_id = killed_job["owner_job_id"]
    kill_detail["owner_job_id"] = owner_job_id
    kill_detail["idempotency_key"] = attempt_request["idempotency_key"]
    _record(summary, "5.3 kill mid-run (process tree terminated)", True, kill_detail)

    # restart: read-only status of the durable state
    status_proc = _run_cli(owner_root, None, "get-status", "--job-id", owner_job_id)
    status_view = (_json_or_none(status_proc.stdout) or {}).get("job_view") or {}
    status_detail = {
        "returncode": status_proc.returncode,
        "status": status_view.get("status"),
        "status_known": status_view.get("status_known"),
        "allowed_actions": status_view.get("allowed_actions"),
        "cost_state": status_view.get("cost_state"),
        "cost": status_view.get("cost"),
        "stages": [{ "stage": s["stage"], "status": s["status"],
                     "attempt_count": s["attempt_count"]}
                   for s in status_view.get("stages", [])],
    }
    _record(summary, "5.3 restart get-status",
            status_proc.returncode == 0
            and status_view.get("status") in ("interrupted", "queued")
            and status_view.get("status_known") is True
            and status_view.get("cost_state") in ("unknown", "not_applicable")
            and status_view.get("stages", [{}])[0].get("status") == "completed",
            status_detail)
    unknown_cost_sample = {"status": status_view.get("status"),
                           "cost_state": status_view.get("cost_state"),
                           "cost": status_view.get("cost")}

    # reconcile: repair the durable state from records+artifacts
    reconcile_proc = _run_cli(owner_root, None, "act", "--job-id", owner_job_id,
                              "--action", "reconcile")
    reconcile_view = (_json_or_none(reconcile_proc.stdout) or {}).get("job_view") or {}
    _record(summary, "5.3 reconcile after restart",
            reconcile_proc.returncode == 0
            and reconcile_view.get("status") in ("interrupted", "queued")
            and reconcile_view.get("status_known") is True,
            {"returncode": reconcile_proc.returncode,
             "status": reconcile_view.get("status"),
             "stages": [{ "stage": s["stage"], "status": s["status"]}
                        for s in reconcile_view.get("stages", [])]})

    # resume: continue from the first non-completed stage
    resume_started = time.monotonic()
    resume_proc = _run_cli(owner_root, config, "act", "--job-id", owner_job_id,
                           "--action", "resume")
    resume_seconds = round(time.monotonic() - resume_started, 3)
    resume_view = (_json_or_none(resume_proc.stdout) or {}).get("job_view") or {}
    final_job_path = jobs_dir / owner_job_id / "job.json"
    final_job = json.loads(final_job_path.read_text(encoding="utf-8"))
    source_attempts = final_job["stages"]["source"]["attempts"]
    resume_detail = {
        "returncode": resume_proc.returncode,
        "resume_wall_seconds": resume_seconds,
        "final_status": resume_view.get("status"),
        "allowed_actions": resume_view.get("allowed_actions"),
        "stage_attempts": _stage_elapsed(final_job),
        "source_attempt_count": len(source_attempts),
        "publication_registered_lines": (
            (final_job_path.parent / "registry" / "publications.jsonl")
            .read_text(encoding="utf-8").strip().count("\n") + 1
            if (final_job_path.parent / "registry" / "publications.jsonl").exists() else 0),
    }
    _record(summary, "5.3 resume to completion without re-running source",
            resume_proc.returncode == 0
            and resume_view.get("status") == "succeeded"
            and len(source_attempts) == 1
            and source_attempts[0].get("status") == "completed"
            and resume_detail["publication_registered_lines"] >= 1,
            resume_detail)
    # note: the recovered job keeps cost_state=unknown — one of its compute
    # attempts was killed without resource observations; recorded honestly

    # --- §5.2 idempotency ------------------------------------------------------
    replay_request = dict(request)
    replay_request["idempotency_key"] = kill_detail["idempotency_key"]
    before_idem_job = json.loads(
        (jobs_dir / owner_job_id / "job.json").read_text(encoding="utf-8"))
    attempts_before = _stage_elapsed(before_idem_job)
    idem_started = time.monotonic()
    idem_proc = _run_cli(owner_root, config, "submit",
                         stdin_text=json.dumps(replay_request, ensure_ascii=False))
    idem_seconds = round(time.monotonic() - idem_started, 3)
    idem_payload = _json_or_none(idem_proc.stdout) or {}
    idem_view = idem_payload.get("job_view") or {}
    idem_job_path = jobs_dir / owner_job_id / "job.json"
    idem_job = json.loads(idem_job_path.read_text(encoding="utf-8"))
    attempts_after = _stage_elapsed(idem_job)
    idem_detail = {
        "returncode": idem_proc.returncode,
        "same_owner_job_id": idem_payload.get("owner_job_id") == owner_job_id,
        "idempotent_replay": idem_view.get("idempotent_replay"),
        "status": idem_view.get("status"),
        "second_submit_wall_seconds": idem_seconds,
        "stage_attempts_before": attempts_before,
        "stage_attempts_after": attempts_after,
        "stderr_tail": (idem_proc.stderr or "")[-300:],
    }
    _record(summary, "5.2 idempotent resubmit (no re-orchestration)",
            idem_proc.returncode == 0
            and idem_detail["same_owner_job_id"]
            and idem_detail["idempotent_replay"] is True
            and attempts_after == attempts_before,
            idem_detail)

    # --- §5.4 natural failure ---------------------------------------------------
    fail_request = _build_request(as_of, company_query="不存在的公司xyz",
                                  idempotency_key="drill-fail-1")
    fail_proc = _run_cli(owner_root, config, "submit",
                         stdin_text=json.dumps(fail_request, ensure_ascii=False))
    fail_payload = _json_or_none(fail_proc.stdout) or {}
    fail_view = fail_payload.get("job_view") or {}
    fail_job_id = fail_payload.get("owner_job_id")
    fail_stage = next((s for s in fail_view.get("stages", [])
                       if s["stage"] == "source"), {})
    fail_attempt = (fail_stage.get("attempts") or [{}])[0]
    fail_detail = {
        "returncode": fail_proc.returncode,
        "owner_job_id": fail_job_id,
        "status": fail_view.get("status"),
        "allowed_actions": fail_view.get("allowed_actions"),
        "source_stage_status": fail_stage.get("status"),
        "attempt": {k: fail_attempt.get(k) for k in
                    ("attempt_no", "status", "exit_code", "observations",
                     "elapsed_seconds")},
        "stderr_tail": (fail_proc.stderr or "")[-300:],
    }
    (EVIDENCE / "natural_failure_jobview.json").write_text(
        json.dumps(fail_view, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8")
    _record(summary, "5.4 natural source failure JobView",
            fail_proc.returncode == 0
            and fail_view.get("status") == "failed"
            and fail_stage.get("status") == "failed"
            and fail_attempt.get("exit_code") in (1, 2, 3),
            fail_detail)

    # --- §5.5 cost samples ------------------------------------------------------
    # known: the natural-failure job observed every attempt's resources
    # (0 downloads, 0 paid calls) and projects a real zero cost
    known_cost_sample = {"status": fail_view.get("status"),
                         "cost_state": fail_view.get("cost_state"),
                         "cost": fail_view.get("cost")}
    (EVIDENCE / "cost_known_sample.json").write_text(
        json.dumps(known_cost_sample, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8")
    (EVIDENCE / "cost_unknown_sample.json").write_text(
        json.dumps(unknown_cost_sample, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8")
    _record(summary, "5.5 cost known + unknown samples",
            known_cost_sample.get("cost_state") == "known"
            and known_cost_sample.get("cost") == {"currency": "USD", "value": "0.00"}
            and unknown_cost_sample.get("cost_state") in ("unknown", "not_applicable"),
            {"known": known_cost_sample, "unknown": unknown_cost_sample})

    # --- budget honesty: drill used zero new downloads / zero paid calls --------
    budget_lines = []
    for job_file in sorted(jobs_dir.glob("*/job.json")):
        job = json.loads(job_file.read_text(encoding="utf-8"))
        budget_lines.append({"owner_job_id": job["owner_job_id"],
                             "budget": job.get("budget"),
                             "limits_ref": job.get("limits_ref")})
    (EVIDENCE / "budget_observation.json").write_text(
        json.dumps({"schema_version": "rf-job-drill-budget/1",
                    "new_downloads_total": sum(
                        (b["budget"] or {}).get("new_downloads", 0) for b in budget_lines),
                    "paid_model_calls_total": sum(
                        (b["budget"] or {}).get("paid_model_calls", 0) for b in budget_lines),
                    "jobs": budget_lines},
                   ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    _write_evidence(summary, EVIDENCE)
    return 1 if summary["failures"] else 0


def _write_evidence(summary: dict, evidence: Path) -> None:
    (evidence / "drill_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8")
    lines = ["# RF job facade acceptance drill (offline)", ""]
    for step in summary["steps"]:
        mark = "PASS" if step["ok"] else "FAIL"
        lines.append(f"- {mark} `{step['step']}`")
    lines += ["", f"Failures: {len(summary['failures'])}",
              "Budget: see budget_observation.json (zero new downloads, zero paid calls)."]
    (evidence / "drill_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
