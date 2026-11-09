"""Public job facade for RF full research (OWNERPKG-REVENUE-FORECAST-01).

This module is the orchestration and state layer ONLY.  Every existing engine
or CLI (source_preparation.py, revenue_forecast.py, publication_registry.py,
report_catalog*.py) keeps its algorithm and semantics untouched; the facade
invokes them as subprocesses with fixed argv built from trusted deployment
configuration and the job scope.

Protocol ``rf-job/1`` (fixed routes, no paths/command strings/credentials in
the business request):

    submit       --request-json '<json>'   (or the request JSON on stdin)
    get-status   --job-id <id>
    act          --job-id <id> --action reconcile|resume
    list-jobs    [--limit N]

Trusted deployment arguments (never business input, same discipline as the
``--owner-root`` seam of report_catalog_deployment.py):

    --owner-root <absolute existing directory>   job store root
    --deployment-config <path>                   trusted chain/budget config

Catalog registration stays outside the facade (G-m8-RF-05). The owner
catalog admits eligible publications and unsuccessful research attempts through
separate management commands. The public read CLI serves historical catalog
records independently of the live job.

Durability: the job state document and every stage artifact live under
``<owner-root>/artifacts/rf_jobs/jobs/<owner_job_id>/``.  A process that dies
mid-stage leaves a recorded running attempt and releases its kernel mutex;
get-status derives the live state read-only, ``act reconcile`` re-derives and
repairs the state document from the durable records + artifacts (the
reconcile authority), and ``act resume`` continues from the first
non-completed stage without re-running completed stages or replaying their
write effects.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Callable, cast

from filing_upstream_cause import failure_observation
from owner_atomic_io import replace_file_bytes
from owner_file_lock import OwnerFileLock

PROJECT_ROOT = Path(__file__).resolve().parents[1]

PROTOCOL_SCHEMA = "rf-job/1"
JOB_STATE_SCHEMA = "rf-job-state/1"
DEPLOYMENT_SCHEMA = "rf-job-deployment/1"

STAGES: tuple[str, ...] = ("source", "compute", "publication")

STATUS_QUEUED = "queued"
STATUS_RUNNING = "running"
STATUS_SUCCEEDED = "succeeded"
STATUS_FAILED = "failed"
STATUS_INTERRUPTED = "interrupted"
STATUS_UNKNOWN = "unknown"

ACTION_RESUME = "resume"
ACTION_RECONCILE = "reconcile"

RECOVERY_DURABLE = "durable_owner_job"
RECOVERY_SHORT_REQUEST = "short_request_only"
RECOVERY_UNAVAILABLE = "unavailable"

COST_KNOWN = "known"
COST_UNKNOWN = "unknown"
COST_NOT_APPLICABLE = "not_applicable"

# G-m8-RF-04: every command class involved in a full_research job declares its
# recovery capability.  The catalog management import is not a facade command
# and cannot be recovered by the facade, so it is honestly "unavailable".
COMMAND_RECOVERY: dict[str, str] = {
    "rf_job.submit": RECOVERY_DURABLE,
    "rf_job.get_status": RECOVERY_DURABLE,
    "rf_job.act": RECOVERY_DURABLE,
    "rf_job.list_jobs": RECOVERY_DURABLE,
    "source_preparation": RECOVERY_SHORT_REQUEST,
    "revenue_forecast": RECOVERY_SHORT_REQUEST,
    "publication_registry.audit": RECOVERY_SHORT_REQUEST,
    "report_catalog.management_import": RECOVERY_UNAVAILABLE,
}

_SOURCE_SCRIPT = PROJECT_ROOT / "scripts" / "source_preparation.py"
_COMPUTE_SCRIPT = PROJECT_ROOT / "scripts" / "revenue_forecast.py"
_AUDIT_SCRIPT = PROJECT_ROOT / "scripts" / "publication_registry.py"


class JobFacadeError(RuntimeError):
    """A named, pathless facade failure."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class SimulatedProcessDeath(BaseException):
    """Test-only hard-crash surrogate.

    Derives from BaseException so no ``except Exception`` handler of the
    facade catches it: like a real process kill, it leaves the attempt record
    in its last durable state with no exit update.
    """


# ---------------------------------------------------------------- utilities


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _sha256_text(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_write_text(path: Path, text: str) -> None:
    replace_file_bytes(path, text.encode("utf-8"))


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    _atomic_write_text(path, json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                        allow_nan=False, indent=2) + "\n")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class JobLock(OwnerFileLock):
    """Per-job and store creation mutex using the owner lease protocol."""

    def __enter__(self) -> "JobLock":
        if not self.acquire():
            raise JobFacadeError("lock_unavailable",
                                 "another orchestration of this job is active")
        return self

    def __exit__(self, *_exc: object) -> None:
        self.release()


# ------------------------------------------------------- deployment config


class Deployment:
    """Validated trusted deployment configuration (rf-job-deployment/1)."""

    def __init__(self, payload: dict[str, Any]):
        if not isinstance(payload, dict):
            raise JobFacadeError("deployment_config_invalid", "deployment config must be a JSON object")
        if payload.get("schema_version") != DEPLOYMENT_SCHEMA:
            raise JobFacadeError("deployment_config_invalid",
                                 f"deployment config schema_version must be {DEPLOYMENT_SCHEMA}")
        python = payload.get("python")
        if python is not None and (not isinstance(python, str) or not python.strip()):
            raise JobFacadeError("deployment_config_invalid", "python must be a non-empty string")
        self.python: str = python or sys.executable

        stages = payload.get("stages")
        if not isinstance(stages, dict):
            raise JobFacadeError("deployment_config_invalid", "stages must be an object")
        source = stages.get("source")
        if not isinstance(source, dict):
            raise JobFacadeError("deployment_config_invalid", "stages.source must be an object")
        self.source_filing_fetch_root = self._absolute(source, "filing_fetch_root")
        self.source_company_wiki_config = self._absolute(source, "company_wiki_config")
        self.source_catalog_config = self._absolute(source, "company_wiki_catalog_config")
        receipt = source.get("source_reader_receipt_version", "2.1")
        if receipt not in ("2.1", "2.2"):
            raise JobFacadeError("deployment_config_invalid",
                                 "source_reader_receipt_version must be 2.1 or 2.2")
        self.source_receipt_version: str = receipt
        reader = source.get("source_reader_command")
        if reader is not None and (
            not isinstance(reader, list) or not reader
            or any(not isinstance(arg, str) or not arg.strip() or "\x00" in arg for arg in reader)
        ):
            raise JobFacadeError("deployment_config_invalid", "source_reader_command must be an argv list")
        self.source_reader_command: list[str] | None = reader
        self.source_timeout = self._positive(source, "timeout_seconds", default=900.0)
        template = source.get("request_template")
        if not isinstance(template, dict):
            raise JobFacadeError("deployment_config_invalid",
                                 "stages.source.request_template must be an object")
        for key in ("schema_version", "market", "document_kind", "fiscal_year", "filing_intent"):
            if key not in template:
                raise JobFacadeError("deployment_config_invalid",
                                     f"request_template is missing {key}")
        self.source_request_template: dict[str, Any] = dict(template)
        self.source_request_template.pop("company_query", None)
        self.source_request_template.pop("as_of_date", None)

        compute = stages.get("compute")
        if not isinstance(compute, dict):
            raise JobFacadeError("deployment_config_invalid", "stages.compute must be an object")
        self.compute_timeout = self._positive(compute, "timeout_seconds", default=900.0)
        publication = stages.get("publication")
        if not isinstance(publication, dict):
            raise JobFacadeError("deployment_config_invalid", "stages.publication must be an object")
        self.publication_timeout = self._positive(publication, "timeout_seconds", default=120.0)

        limits = payload.get("limits")
        if not isinstance(limits, dict):
            raise JobFacadeError("deployment_config_invalid", "limits must be an object")
        refs = limits.get("refs")
        if not isinstance(refs, dict) or not refs:
            raise JobFacadeError("deployment_config_invalid", "limits.refs must be a non-empty object")
        self.limits_refs: dict[str, dict[str, Any]] = {}
        for ref, value in refs.items():
            if not isinstance(ref, str) or not ref.strip() or not isinstance(value, dict):
                raise JobFacadeError("deployment_config_invalid", "limits.refs entries are malformed")
            self._validate_limits(value)
            self.limits_refs[ref] = value
        default_ref = limits.get("default_ref")
        if default_ref is not None and default_ref not in self.limits_refs:
            raise JobFacadeError("deployment_config_invalid", "limits.default_ref is not in limits.refs")

    @staticmethod
    def _validate_limits(limits: dict[str, Any]) -> None:
        max_cost = limits.get("max_cost_usd")
        if max_cost is not None:
            if not isinstance(max_cost, str):
                raise JobFacadeError("deployment_config_invalid", "max_cost_usd must be a decimal string")
            try:
                if float(max_cost) < 0:
                    raise ValueError
            except ValueError as exc:
                raise JobFacadeError("deployment_config_invalid",
                                     "max_cost_usd must be a non-negative decimal string") from exc

    @staticmethod
    def _absolute(container: dict[str, Any], key: str) -> Path:
        value = container.get(key)
        if not isinstance(value, str) or not value.strip():
            raise JobFacadeError("deployment_config_invalid", f"{key} must be a non-empty string")
        path = Path(value)
        if not path.is_absolute():
            raise JobFacadeError("deployment_config_invalid", f"{key} must be an absolute path")
        return path

    @staticmethod
    def _positive(container: dict[str, Any], key: str, *, default: float) -> float:
        value = container.get(key, default)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise JobFacadeError("deployment_config_invalid", f"{key} must be a positive number")
        return float(value)

    def limits_for(self, limits_ref: str) -> dict[str, Any]:
        limits = self.limits_refs.get(limits_ref)
        if limits is None:
            raise JobFacadeError("limits_ref_unknown",
                                 "the submitted limits_ref is not a configured owner budget reference")
        return limits

    @classmethod
    def load(cls, path: Path) -> "Deployment":
        try:
            payload = _read_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            raise JobFacadeError("deployment_config_invalid",
                                 "deployment config is unreadable or not JSON") from exc
        return cls(payload)


def resolve_owner_root(value: str | None) -> Path:
    """Validate the trusted job-store workspace (the facade's own rule).

    Unlike report_catalog_deployment.resolve_owner_root (whose managed-catalog
    requirement stays untouched for the catalog readers), the job store is a
    separate artifact: an existing absolute directory is enough.  Zero catalog
    rows never mean the workspace cannot host jobs; admission is a separate
    explicit management step.
    """
    if value is None:
        raise JobFacadeError("owner_root_required", "the job store requires --owner-root")
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise JobFacadeError("owner_root_invalid", "the owner root must be an absolute workspace path")
    path = Path(value)
    if not path.is_absolute():
        raise JobFacadeError("owner_root_invalid", "the owner root must be an absolute workspace path")
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        raise JobFacadeError("owner_root_invalid",
                             "the owner root must be an absolute workspace path") from exc
    if not resolved.is_dir():
        raise JobFacadeError("owner_root_absent", "the owner root does not exist")
    return resolved


# ---------------------------------------------------------- request intake


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def normalize_request(raw: Any) -> dict[str, Any]:
    """Validate the fixed-shape rf-job/1 request and return the normalized job.

    The request carries content, never paths, command strings or credentials.
    The engine input document is validated fail-fast with the engine's own
    validator (revenue_core.validate_document) plus scope cross-checks.
    """
    if not isinstance(raw, dict):
        raise JobFacadeError("request_invalid", "the request must be a JSON object")
    if raw.get("schema_version") != PROTOCOL_SCHEMA:
        raise JobFacadeError("request_invalid", f"schema_version must be {PROTOCOL_SCHEMA}")
    if raw.get("workflow") != "full_research":
        raise JobFacadeError("request_invalid", "workflow must be full_research")
    company_query = raw.get("company_query")
    if not isinstance(company_query, str) or not company_query.strip():
        raise JobFacadeError("request_invalid", "company_query must be a non-empty string")
    information_as_of = raw.get("information_as_of")
    if not isinstance(information_as_of, str):
        raise JobFacadeError("request_invalid", "information_as_of must be an ISO date string")
    try:
        from datetime import date as _date

        _date.fromisoformat(information_as_of)
    except ValueError as exc:
        raise JobFacadeError("request_invalid", "information_as_of must be an ISO date") from exc
    horizon = raw.get("horizon_end_year")
    if not _is_int(horizon):
        raise JobFacadeError("request_invalid", "horizon_end_year must be an integer")
    horizon_end_year: int = cast(int, horizon)
    scenario_set = raw.get("scenario_set")
    if (not isinstance(scenario_set, list) or not scenario_set
            or not all(isinstance(s, str) and s.strip() for s in scenario_set)
            or len(set(scenario_set)) != len(scenario_set)):
        raise JobFacadeError("request_invalid",
                             "scenario_set must be a non-empty list of unique scenario names")
    snapshots = raw.get("source_snapshot_ids", [])
    if (not isinstance(snapshots, list)
            or not all(isinstance(s, str) and s.strip() for s in snapshots)
            or len(set(snapshots)) != len(snapshots)):
        raise JobFacadeError("request_invalid",
                             "source_snapshot_ids must be a list of unique non-empty strings")
    idempotency_key = raw.get("idempotency_key")
    if not isinstance(idempotency_key, str) or not idempotency_key.strip() or len(idempotency_key) > 200:
        raise JobFacadeError("request_invalid", "idempotency_key must be a 1..200 character string")
    limits_ref = raw.get("limits_ref")
    if not isinstance(limits_ref, str) or not limits_ref.strip() or len(limits_ref) > 200:
        raise JobFacadeError("request_invalid", "limits_ref must be a 1..200 character string")
    forecast_input = raw.get("forecast_input")
    if not isinstance(forecast_input, dict):
        raise JobFacadeError("request_invalid",
                             "forecast_input must be the full RF input document object")
    _validate_forecast_input(forecast_input, information_as_of=information_as_of,
                             horizon_end_year=horizon_end_year, scenario_set=scenario_set)
    scope = {
        "workflow": "full_research",
        "company_query": company_query.strip(),
        "information_as_of": information_as_of,
        "horizon_end_year": horizon,
        "scenario_set": list(scenario_set),
        "source_snapshot_ids": list(snapshots),
    }
    return {
        "scope": scope,
        "forecast_input": forecast_input,
        "idempotency_key_sha256": _sha256_text(idempotency_key.strip()),
        "limits_ref": limits_ref.strip(),
        "request_sha256": _sha256_text(json.dumps(raw, ensure_ascii=False, sort_keys=True,
                                                  allow_nan=False)),
    }


def _validate_forecast_input(document: dict[str, Any], *, information_as_of: str,
                             horizon_end_year: int, scenario_set: list[str]) -> None:
    """Fail-fast engine validation plus scope cross-checks (no writes)."""
    if str(PROJECT_ROOT / "scripts") not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    try:
        from revenue_core import Collector, validate_document

        validate_document(document, collector=Collector())
    except Exception as exc:  # the engine raises its own input error types
        raise JobFacadeError("request_invalid",
                             f"forecast_input refused by the engine: {exc}") from exc
    if document.get("as_of_date") != information_as_of:
        raise JobFacadeError("request_invalid",
                             "forecast_input.as_of_date must equal information_as_of")
    years = document.get("forecast_years")
    if isinstance(years, list) and any(
            (not _is_int(year) or year > horizon_end_year) for year in years):
        raise JobFacadeError("request_invalid",
                             "forecast_input.forecast_years must not exceed horizon_end_year")
    document_scenarios: set[str] = set()
    for segment in document.get("segments", []):
        scenarios = segment.get("scenarios") if isinstance(segment, dict) else None
        if isinstance(scenarios, dict):
            document_scenarios.update(str(key) for key in scenarios)
    missing = [name for name in scenario_set if name not in document_scenarios]
    if missing:
        raise JobFacadeError("request_invalid",
                             "scenario_set contains scenarios the forecast_input does not model")


# ------------------------------------------------------------------- store


class JobStore:
    """Durable job state under ``<owner-root>/artifacts/rf_jobs/``."""

    def __init__(self, owner_root: Path):
        self.owner_root = owner_root.resolve()
        self.store_root = self._owned_path(self.owner_root / "artifacts" / "rf_jobs")
        self.jobs_dir = self.store_root / "jobs"
        self.index_dir = self.store_root / "index"
        self.locks_dir = self.store_root / "locks"
        self.idempotency_file = self._owned_path(self.index_dir / "idempotency.json")
        self.jobs_index_file = self._owned_path(self.index_dir / "jobs.jsonl")

    def _owned_path(self, path: Path) -> Path:
        resolved = path.resolve()
        if not resolved.is_relative_to(self.owner_root):
            raise JobFacadeError("job_store_path_invalid", "job storage must stay inside the owner workspace")
        return resolved

    @staticmethod
    def _valid_job_id(owner_job_id: Any) -> bool:
        return isinstance(owner_job_id, str) and re.fullmatch(r"rfjob-[A-Za-z0-9_-]{1,96}", owner_job_id) is not None

    def _require_job_id(self, owner_job_id: str) -> None:
        if not self._valid_job_id(owner_job_id):
            raise JobFacadeError("owner_job_id_invalid", "owner job id must be a job token")

    def job_dir(self, owner_job_id: str) -> Path:
        self._require_job_id(owner_job_id)
        return self._owned_path(self.jobs_dir / owner_job_id)

    def job_file(self, owner_job_id: str) -> Path:
        return self._owned_path(self.job_dir(owner_job_id) / "job.json")

    def lock(self, owner_job_id: str) -> JobLock:
        self._require_job_id(owner_job_id)
        return JobLock(self._owned_path(self.locks_dir / f"{owner_job_id}.lock"))

    def _creation_lock(self) -> JobLock:
        return JobLock(self._owned_path(self.locks_dir / "creation.lock"))

    def load_job(self, owner_job_id: str) -> dict[str, Any]:
        path = self.job_file(owner_job_id)
        if not path.exists():
            raise JobFacadeError("owner_job_not_found", "no such owner job exists in the store")
        try:
            payload = _read_json(path)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise JobFacadeError("job_state_unreadable",
                                 "the durable job state is unreadable; reconcile is required") from exc
        if (not isinstance(payload, dict) or payload.get("schema_version") != JOB_STATE_SCHEMA
                or payload.get("owner_job_id") != owner_job_id):
            raise JobFacadeError("job_state_unreadable",
                                 "the durable job state schema is unrecognized; reconcile is required")
        return payload

    def save_job(self, job: dict[str, Any]) -> None:
        job["updated_at"] = _utc_now()
        _atomic_write_json(self.job_file(job["owner_job_id"]), job)

    def idempotency_get(self, key_sha256: str) -> dict[str, Any] | None:
        try:
            index = _read_json(self.idempotency_file)
        except FileNotFoundError:
            return None
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise JobFacadeError("job_state_unreadable",
                                 "the idempotency index is unreadable") from exc
        return index.get(key_sha256)

    def idempotency_put(self, key_sha256: str, record: dict[str, Any]) -> None:
        try:
            index = _read_json(self.idempotency_file)
        except FileNotFoundError:
            index = {}
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            raise JobFacadeError("job_state_unreadable",
                                 "the idempotency index is unreadable") from exc
        if key_sha256 in index:
            raise JobFacadeError("idempotency_key_conflict",
                                 "the idempotency key was concurrently claimed by another submission")
        index[key_sha256] = record
        _atomic_write_json(self.idempotency_file, index)

    def append_jobs_index(self, owner_job_id: str, created_at: str) -> None:
        self.index_dir.mkdir(parents=True, exist_ok=True)
        line = json.dumps({"owner_job_id": owner_job_id, "created_at": created_at},
                          ensure_ascii=False, sort_keys=True)
        with open(self.jobs_index_file, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())

    def list_job_ids(self) -> list[str]:
        if not self.jobs_index_file.exists():
            return []
        ids: list[str] = []
        with open(self.jobs_index_file, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue  # tolerate a torn trailing line after a crash
                job_id = record.get("owner_job_id")
                if self._valid_job_id(job_id):
                    ids.append(job_id)
        return ids

    # ---- per-job workspace -------------------------------------------------

    def stage_dir(self, owner_job_id: str, stage: str) -> Path:
        return self._owned_path(self.job_dir(owner_job_id) / "stages" / stage)

    def logs_dir(self, owner_job_id: str) -> Path:
        return self._owned_path(self.job_dir(owner_job_id) / "logs")

    def registry_file(self, owner_job_id: str) -> Path:
        return self._owned_path(self.job_dir(owner_job_id) / "registry" / "publications.jsonl")

    def result_artifact(self, owner_job_id: str, stage: str) -> Path:
        if stage == "source":
            return self.stage_dir(owner_job_id, stage) / "result-envelope.json"
        if stage == "compute":
            return self.stage_dir(owner_job_id, stage) / "result.json"
        return self.stage_dir(owner_job_id, stage) / "audit.json"

    def log_paths(self, owner_job_id: str, stage: str, attempt_no: int) -> tuple[Path, Path]:
        logs_dir = self.logs_dir(owner_job_id)
        return (logs_dir / f"{stage}-{attempt_no}.stdout.txt",
                logs_dir / f"{stage}-{attempt_no}.stderr.txt")


# ------------------------------------------------------------ stage runners


class AttemptOutcome:
    """What the runner observed about one stage invocation."""

    def __init__(self, *, exit_code: int | None, killed: bool, elapsed_seconds: float):
        self.exit_code = exit_code
        self.killed = killed
        self.elapsed_seconds = elapsed_seconds


class SubprocessStageRunner:
    """Runs the fixed stage command as a subprocess, capturing stdout/stderr.

    On timeout the child is killed (subprocess.run does this after
    TimeoutExpired) and the attempt is recorded as interrupted with no exit
    code — the same durable shape a hard process kill leaves behind.
    """

    def __init__(self, store: JobStore, owner_job_id: str):
        self._store = store
        self._owner_job_id = owner_job_id

    def log_paths(self, stage: str, attempt_no: int) -> tuple[Path, Path]:
        return self._store.log_paths(self._owner_job_id, stage, attempt_no)

    def run(self, *, stage: str, command: list[str], timeout_seconds: float,
            env: dict[str, str] | None = None) -> AttemptOutcome:
        stdout_path, stderr_path = self.log_paths(stage, self._pending_attempt_no)
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()
        full_env = dict(os.environ)
        if env:
            full_env.update(env)
        killed = False
        exit_code: int | None = None
        try:
            with open(stdout_path, "wb") as out, open(stderr_path, "wb") as err:
                try:
                    proc = subprocess.run(
                        command, stdout=out, stderr=err, timeout=timeout_seconds,
                        check=False, env=full_env, cwd=str(PROJECT_ROOT),
                    )
                    exit_code = proc.returncode
                except subprocess.TimeoutExpired:
                    killed = True
        except OSError:
            # The child could not even be started; that is a failed attempt
            # with its diagnostic on stderr.
            stderr_path.parent.mkdir(parents=True, exist_ok=True)
            stderr_path.write_text(json.dumps({"error_code": "stage_spawn_failed",
                                               "error": "the stage command could not be started"}),
                                   encoding="utf-8")
            exit_code = 3
        elapsed = time.monotonic() - started
        return AttemptOutcome(exit_code=exit_code, killed=killed, elapsed_seconds=elapsed)

    _pending_attempt_no: int = 1


class FakeStageRunner(SubprocessStageRunner):
    """Test double: records the requested commands instead of spawning them.

    It validates the fixed command shape, so a broken command template still
    fails tests.  It never touches the network and never spawns the engine;
    its stage artifacts are produced by the real engine in draft mode (no
    publication write) so downstream state logic exercises real artifacts.
    """

    def __init__(self, store: JobStore, owner_job_id: str, *,
                 behavior: dict[str, Callable[[str, list[str]], AttemptOutcome]] | None = None,
                 die_on_stage: str | None = None,
                 failure_stderr: dict[str, Any] | None = None):
        super().__init__(store, owner_job_id)
        self.requests: list[dict[str, Any]] = []
        self._behavior = behavior or {}
        self._die_on_stage = die_on_stage
        self._failure_stderr = failure_stderr

    def run(self, *, stage: str, command: list[str], timeout_seconds: float,
            env: dict[str, str] | None = None) -> AttemptOutcome:
        attempt_no = self._pending_attempt_no
        self.requests.append({"stage": stage, "command": command, "attempt_no": attempt_no,
                              "timeout_seconds": timeout_seconds, "env": env})
        if self._die_on_stage == stage:
            # Leave the attempt record in its durable running state, exactly
            # like a real process kill, then die without any cleanup.
            raise SimulatedProcessDeath
        stdout_path, stderr_path = self.log_paths(stage, attempt_no)
        stdout_path.parent.mkdir(parents=True, exist_ok=True)
        outcome_factory = self._behavior.get(stage)
        outcome = outcome_factory(stage, command) if outcome_factory is not None else None
        if outcome is None:
            stdout_path.write_text(self._success_stdout(stage), encoding="utf-8")
            stderr_path.write_text("", encoding="utf-8")
            self._write_success_artifact(stage)
            outcome = AttemptOutcome(exit_code=0, killed=False, elapsed_seconds=0.05)
        else:
            stderr_path.write_text(
                json.dumps(self._failure_stderr, ensure_ascii=False, sort_keys=True)
                if self._failure_stderr else "", encoding="utf-8")
        return outcome

    def _success_stdout(self, stage: str) -> str:
        if stage == "source":
            return json.dumps({"schema_version": "source-preparation-result/1",
                               "source": {"reuse_receipt": {"download_calls": 0,
                                                            "outcome": "reused_existing",
                                                            "llm_calls": None,
                                                            "parser_calls": None}}},
                              ensure_ascii=False, sort_keys=True)
        return "no problems\n" if stage == "publication" else ""

    def _write_success_artifact(self, stage: str) -> None:
        if stage == "source":
            _atomic_write_text(self._store.result_artifact(self._owner_job_id, "source"),
                               self._success_stdout("source"))
        elif stage == "compute":
            sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
            from revenue_core import run_forecast

            job = self._store.load_job(self._owner_job_id)
            result = run_forecast(job["forecast_input"], mode="draft")
            _atomic_write_text(self._store.result_artifact(self._owner_job_id, "compute"),
                               json.dumps(result, ensure_ascii=False, sort_keys=True, allow_nan=False))
        elif stage == "publication":
            _atomic_write_text(self._store.result_artifact(self._owner_job_id, "publication"),
                               "no problems\n")


# ------------------------------------------------------------- job building


def _new_owner_job_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"rfjob-{stamp}-{uuid.uuid4().hex[:12]}"


def _fresh_job(*, owner_job_id: str, normalized: dict[str, Any], limits_ref: str,
               limits: dict[str, Any], request_sha256: str) -> dict[str, Any]:
    now = _utc_now()
    stages: dict[str, Any] = {}
    for stage in STAGES:
        stages[stage] = {"status": "pending", "attempts": []}
    return {
        "schema_version": JOB_STATE_SCHEMA,
        "protocol": PROTOCOL_SCHEMA,
        "kind": "rf_job",
        "owner_job_id": owner_job_id,
        "workflow": normalized["scope"]["workflow"],
        "scope": normalized["scope"],
        "forecast_input": normalized["forecast_input"],
        "idempotency_key_sha256": normalized["idempotency_key_sha256"],
        "request_sha256": request_sha256,
        "limits_ref": limits_ref,
        "limits": limits,
        "status": STATUS_QUEUED,
        "status_known": True,
        "created_at": now,
        "updated_at": now,
        "stages": stages,
        "budget": {"wall_seconds_used": 0.0, "new_downloads": 0, "paid_model_calls": 0},
        "result": None,
        "idempotent_replay": False,
    }


# ------------------------------------------------------------- orchestration


def _stage_command(job: dict[str, Any], store: JobStore, deployment: Deployment,
                   stage: str) -> tuple[list[str], dict[str, str] | None, float]:
    owner_job_id = job["owner_job_id"]
    python = deployment.python
    if stage == "source":
        request = dict(deployment.source_request_template)
        request["company_query"] = job["scope"]["company_query"]
        request["as_of_date"] = job["scope"]["information_as_of"]
        request_path = store.stage_dir(owner_job_id, "source") / "request.json"
        _atomic_write_json(request_path, request)
        command = [
            python, "-B", str(_SOURCE_SCRIPT),
            "--result-envelope",
            "--request-file", str(request_path),
            "--filing-fetch-root", str(deployment.source_filing_fetch_root),
            "--company-wiki-config", str(deployment.source_company_wiki_config),
            "--company-wiki-catalog-config", str(deployment.source_catalog_config),
            "--source-reader-receipt-version", deployment.source_receipt_version,
            "--timeout-seconds", str(deployment.source_timeout),
        ]
        if deployment.source_reader_command is not None:
            command.extend(("--source-reader-command-json", json.dumps(deployment.source_reader_command)))
        return command, None, deployment.source_timeout
    if stage == "compute":
        input_path = store.stage_dir(owner_job_id, "compute") / "input.json"
        _atomic_write_json(input_path, job["forecast_input"])
        output_path = store.stage_dir(owner_job_id, "compute") / "result.json"
        markdown_path = store.stage_dir(owner_job_id, "compute") / "report.md"
        command = [
            python, "-B", str(_COMPUTE_SCRIPT),
            str(input_path),
            "--output", str(output_path),
            "--markdown", str(markdown_path),
        ]
        env = {"REVENUE_PUBLICATION_REGISTRY": str(store.registry_file(owner_job_id))}
        return command, env, deployment.compute_timeout
    result_path = store.result_artifact(owner_job_id, "compute")
    command = [
        python, "-B", str(_AUDIT_SCRIPT),
        "audit", "--result", str(result_path),
    ]
    env = {"REVENUE_PUBLICATION_REGISTRY": str(store.registry_file(owner_job_id))}
    return command, env, deployment.publication_timeout
    # (no stage command ever receives the trusted owner root or the store
    #  root: stage commands only touch job-workspace paths the facade wrote)


def _source_observations(envelope: dict[str, Any]) -> dict[str, Any] | None:
    source = envelope.get("source")
    if not isinstance(source, dict):
        return None
    receipt = source.get("reuse_receipt")
    if not isinstance(receipt, dict):
        return None
    downloads = receipt.get("download_calls")
    llm_calls = receipt.get("llm_calls")
    if type(downloads) is not int or downloads not in (0, 1):
        return None
    return {
        "download_events": downloads,
        # The v2 source chain never starts a model: llm_calls None means
        # "none invoked", observed directly from the producer receipt.
        "model_calls": 0 if llm_calls is None or type(llm_calls) is int and llm_calls == 0 else None,
        "source_outcome": receipt.get("outcome"),
    }


def _companion_read_only(request: dict[str, Any]) -> bool:
    companion = request.get("companion_transcript")
    return companion is None or isinstance(companion, dict) and companion.get("intent") == "reuse_only"


def _source_failure_observations(stderr_path: Path, *, companion_read_only: bool) -> dict[str, Any] | None:
    """Real resource observations from a failed source attempt's stderr doc.

    The filing-fetch ``calls`` counter counts local company-wiki subprocess
    invocations (fetch_filing.py: "every real company-wiki subprocess
    invocation"), NOT paid model calls, so it is recorded as
    ``acquisition_calls`` and never enters the paid-call budget.
    """
    try:
        payload = json.loads(stderr_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError, UnicodeDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    observations: dict[str, Any] = {}
    downloads = payload.get("downloads")
    if isinstance(downloads, int) and not isinstance(downloads, bool):
        observations["download_events"] = downloads
    calls = payload.get("calls")
    if isinstance(calls, int) and not isinstance(calls, bool):
        observations["acquisition_calls"] = calls
    observed = failure_observation(payload)
    cause = observed.get("upstream_cause")
    companion = observed.get("companion_observation")
    acquisition = observed.get("acquisition_observation")
    if (observations.get("download_events") == 0 and cause is not None
            and cause.get("provider_started") is False and cause.get("usage_complete") is True
            and (companion_read_only or companion is not None)
            and (acquisition is None or (acquisition["provider_started"] is False
                and acquisition["usage_complete"] is True and acquisition["cost_usd"] is not None
                and Decimal(acquisition["cost_usd"]) == 0))):
        observations["source_no_external_effect"] = True
        observations["model_calls"] = 0
    return observations or None


def _compute_or_audit_observations(stage: str) -> dict[str, Any]:
    # The compute engine is a pure calculator (never touches the network and
    # starts no model); the publication audit is a read-only registry check.
    return {
        "download_events": 0,
        "model_calls": 0,
        "basis": "engine_is_pure_calculator" if stage == "compute" else "read_only_audit",
    }


def _freeze_source_artifact(stdout_path: Path, artifact_path: Path) -> bool:
    """Capture the source stage's stdout envelope as the durable artifact."""
    try:
        envelope = json.loads(stdout_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError, UnicodeDecodeError):
        return False
    if not isinstance(envelope, dict) or envelope.get("schema_version") != "source-preparation-result/1":
        return False
    _atomic_write_json(artifact_path, envelope)
    return True


def _freeze_audit_artifact(stdout_path: Path, artifact_path: Path) -> None:
    text = stdout_path.read_text(encoding="utf-8", errors="replace")
    _atomic_write_text(artifact_path, text)


def _mark_stage_failed(job: dict[str, Any], store: JobStore, stage: str) -> None:
    job["stages"][stage]["status"] = "failed"
    job["status"] = STATUS_FAILED
    store.save_job(job)


def _run_stage(job: dict[str, Any], *, stage: str, store: JobStore, deployment: Deployment,
               runner: SubprocessStageRunner) -> None:
    owner_job_id = job["owner_job_id"]
    limits = job["limits"]
    attempts = job["stages"][stage]["attempts"]
    max_attempts = limits.get("max_attempts_per_stage")
    max_attempts = max_attempts if isinstance(max_attempts, int) and max_attempts >= 1 else 3
    if len(attempts) >= max_attempts:
        raise JobFacadeError("stage_attempts_exhausted",
                             f"stage {stage} has exhausted its configured attempt budget")
    command, env, timeout = _stage_command(job, store, deployment, stage)
    attempt_no = len(attempts) + 1
    runner._pending_attempt_no = attempt_no  # runner writes per-attempt logs
    record: dict[str, Any] = {
        "attempt_id": f"{stage}-{attempt_no}",
        "attempt_no": attempt_no,
        "stage": stage,
        "status": "running",
        "started_at": _utc_now(),
        "pid": os.getpid(),
        "command_shape": command,
        "exit_code": None,
    }
    companion_read_only = _companion_read_only(deployment.source_request_template)
    if stage == "source":
        record["source_read_only"] = (
            deployment.source_request_template.get("filing_intent") == "reuse_only" and companion_read_only
        )
    attempts.append(record)
    job["stages"][stage]["status"] = "running"
    job["status"] = STATUS_RUNNING
    store.save_job(job)
    outcome = runner.run(stage=stage, command=command, timeout_seconds=timeout, env=env)
    record["ended_at"] = _utc_now()
    record["elapsed_seconds"] = round(outcome.elapsed_seconds, 6)
    record["exit_code"] = outcome.exit_code
    stdout_path, stderr_path = runner.log_paths(stage, attempt_no)
    if outcome.killed:
        record["status"] = "interrupted"
        job["stages"][stage]["status"] = "interrupted"
        job["status"] = STATUS_INTERRUPTED
        store.save_job(job)
        raise JobFacadeError("stage_interrupted", f"stage {stage} was interrupted by its timeout")
    if outcome.exit_code != 0:
        record["status"] = "failed"
        record["observations"] = (
            _source_failure_observations(stderr_path, companion_read_only=companion_read_only)
            if stage == "source" else None
        )
        _mark_stage_failed(job, store, stage)
        raise JobFacadeError("stage_failed",
                             f"stage {stage} failed with exit code {outcome.exit_code}")
    # completed: freeze and verify the durable result artifact
    artifact = store.result_artifact(owner_job_id, stage)
    if stage == "source":
        if not _freeze_source_artifact(stdout_path, artifact):
            record["status"] = "failed"
            _mark_stage_failed(job, store, stage)
            raise JobFacadeError("stage_failed",
                                 "the source stage exited zero without a readable source-preparation result")
    elif stage == "publication":
        _freeze_audit_artifact(stdout_path, artifact)
    else:  # compute: the engine wrote result.json itself; it must parse
        try:
            _read_json(artifact)
        except (OSError, json.JSONDecodeError, ValueError, UnicodeDecodeError):
            record["status"] = "failed"
            _mark_stage_failed(job, store, stage)
            raise JobFacadeError("stage_failed",
                                 "the compute stage exited zero without a readable forecast result")
    record["result_artifact"] = artifact.name
    record["result_sha256"] = _sha256_file(artifact)
    if stage == "source":
        try:
            envelope = _read_json(artifact)
        except (OSError, json.JSONDecodeError, ValueError):
            envelope = {}
        observations = _source_observations(envelope)
        if observations is None:
            record["status"] = "failed"
            _mark_stage_failed(job, store, stage)
            raise JobFacadeError("stage_failed",
                                 "the source result envelope does not carry a usable reuse receipt")
        if (companion_read_only and observations["source_outcome"] == "reused_existing"
                and observations["download_events"] == 0 and observations["model_calls"] == 0):
            observations["source_no_external_effect"] = True
    else:
        observations = _compute_or_audit_observations(stage)
    record["observations"] = observations
    record["status"] = "completed"
    job["stages"][stage]["status"] = "completed"
    budget = job["budget"]
    budget["wall_seconds_used"] = round(
        budget["wall_seconds_used"] + float(record.get("elapsed_seconds", 0.0)), 6)
    if isinstance(observations.get("download_events"), int):
        budget["new_downloads"] += observations["download_events"]
    if isinstance(observations.get("model_calls"), int):
        budget["paid_model_calls"] += observations["model_calls"]
    _enforce_budget(job, store)
    store.save_job(job)


def _enforce_budget(job: dict[str, Any], store: JobStore) -> None:
    """Post-hoc owner budget gate: stop the pipeline when a limit is crossed."""
    limits = job["limits"]
    budget = job["budget"]
    max_wall = limits.get("max_wall_seconds")
    if isinstance(max_wall, (int, float)) and not isinstance(max_wall, bool):
        if budget["wall_seconds_used"] > float(max_wall):
            job["status"] = STATUS_FAILED
            store.save_job(job)
            raise JobFacadeError("budget_exceeded",
                                 "the job exceeded its configured wall-clock budget")
    max_downloads = limits.get("max_new_downloads")
    if isinstance(max_downloads, int) and not isinstance(max_downloads, bool):
        if budget["new_downloads"] > max_downloads:
            job["status"] = STATUS_FAILED
            store.save_job(job)
            raise JobFacadeError("budget_exceeded",
                                 "the job exceeded its configured new-download budget")


def _orchestrate(job: dict[str, Any], *, store: JobStore, deployment: Deployment,
                 runner: SubprocessStageRunner) -> None:
    """Run the pipeline from the first non-completed stage."""
    for stage in STAGES:
        if job["stages"][stage]["status"] == "completed":
            continue
        try:
            _run_stage(job, stage=stage, store=store, deployment=deployment, runner=runner)
        except JobFacadeError as exc:
            # A job-level stop (attempt budget exhausted, owner budget gate)
            # must stay derivable from the durable record even though the
            # stage itself left no failed/interrupted attempt.
            job["stop"] = {"reason": exc.code, "stage": stage, "at": _utc_now()}
            if job.get("status") not in (STATUS_FAILED, STATUS_INTERRUPTED):
                job["status"] = STATUS_FAILED
            store.save_job(job)
            raise
    _finalize_succeeded(job, store)


def _finalize_succeeded(job: dict[str, Any], store: JobStore) -> None:
    job["status"] = STATUS_SUCCEEDED
    artifacts = {}
    for stage in STAGES:
        artifact = store.result_artifact(job["owner_job_id"], stage)
        if artifact.exists():
            artifacts[stage] = {"artifact": artifact.name, "sha256": _sha256_file(artifact)}
    job["result"] = {"stage_artifacts": artifacts}
    store.save_job(job)


# ------------------------------------------------------- state derivation


def _last_attempt(stage_state: dict[str, Any]) -> dict[str, Any] | None:
    attempts = stage_state.get("attempts")
    if isinstance(attempts, list) and attempts and isinstance(attempts[-1], dict):
        return attempts[-1]
    return None


def _stage_artifact_verified(job: dict[str, Any], store: JobStore, stage: str) -> bool:
    attempt = _last_attempt(job["stages"][stage])
    if attempt is None:
        return False
    artifact = store.result_artifact(job["owner_job_id"], stage)
    if not artifact.exists():
        return False
    recorded = attempt.get("result_sha256")
    if not isinstance(recorded, str):
        return False
    try:
        return _sha256_file(artifact) == recorded
    except OSError:
        return False


def _derive_stage_status(job: dict[str, Any], store: JobStore, stage: str, *,
                         lock_alive: bool) -> str | None:
    """One stage's authoritative status, or None when records are unusable."""
    stage_state = job.get("stages", {}).get(stage)
    if not isinstance(stage_state, dict):
        return None
    last = _last_attempt(stage_state)
    if last is None:
        return "pending"
    recorded = last.get("status")
    if recorded == "running":
        return "running" if lock_alive else "interrupted"
    if recorded == "completed":
        return "completed" if _stage_artifact_verified(job, store, stage) else "interrupted"
    if recorded in ("failed", "interrupted"):
        return str(recorded)
    return None


def derive_live_status(job: dict[str, Any], store: JobStore, *, lock_alive: bool) -> str:
    """Re-derive the authoritative job status from durable records + artifacts."""
    stages = job.get("stages")
    if not isinstance(stages, dict) or set(stages) != set(STAGES):
        return STATUS_UNKNOWN
    derived: dict[str, str] = {}
    for stage in STAGES:
        stage_status = _derive_stage_status(job, store, stage, lock_alive=lock_alive)
        if stage_status is None:
            return STATUS_UNKNOWN
        derived[stage] = stage_status
    if lock_alive and any(status == "running" for status in derived.values()):
        return STATUS_RUNNING
    if all(status == "completed" for status in derived.values()):
        return STATUS_SUCCEEDED
    if any(status == "failed" for status in derived.values()):
        return STATUS_FAILED
    if any(status == "interrupted" for status in derived.values()):
        return STATUS_INTERRUPTED
    # a persisted job-level stop (attempt budget, owner budget gate) with no
    # failed/interrupted attempt of its own is still a failed job
    if job.get("stop"):
        return STATUS_FAILED
    return STATUS_QUEUED


def derive_stage_views(job: dict[str, Any], store: JobStore, *, lock_alive: bool) -> list[dict[str, Any]]:
    views: list[dict[str, Any]] = []
    stages = job.get("stages")
    if not isinstance(stages, dict):
        return views
    for stage in STAGES:
        stage_state = stages.get(stage)
        attempts = stage_state.get("attempts") if isinstance(stage_state, dict) else []
        status = _derive_stage_status(job, store, stage, lock_alive=lock_alive) or "unknown"
        views.append({
            "stage": stage,
            "status": status,
            "attempt_count": len(attempts) if isinstance(attempts, list) else 0,
            "attempts": [
                {
                    "attempt_id": attempt.get("attempt_id"),
                    "attempt_no": attempt.get("attempt_no"),
                    "status": attempt.get("status"),
                    "exit_code": attempt.get("exit_code"),
                    "started_at": attempt.get("started_at"),
                    "ended_at": attempt.get("ended_at"),
                    "elapsed_seconds": attempt.get("elapsed_seconds"),
                    "observations": attempt.get("observations"),
                }
                for attempt in (attempts if isinstance(attempts, list) else [])
                if isinstance(attempt, dict)
            ],
        })
    return views


def _allowed_actions(status: str) -> list[str]:
    if status == STATUS_QUEUED:
        return [ACTION_RESUME]
    if status in (STATUS_FAILED, STATUS_INTERRUPTED):
        return [ACTION_RESUME, ACTION_RECONCILE]
    if status == STATUS_UNKNOWN:
        return [ACTION_RECONCILE]
    return []


def _source_attempt_is_safe(attempt: Any) -> bool:
    if not isinstance(attempt, dict):
        return False
    observations = attempt.get("observations")
    return attempt.get("source_read_only") is True or (
        isinstance(observations, dict) and observations.get("source_no_external_effect") is True
    )


def _cost_projection(job: dict[str, Any], status: str) -> tuple[dict[str, Any] | None, str]:
    attempts = [(stage, attempt) for stage in STAGES
                for attempt in job.get("stages", {}).get(stage, {}).get("attempts", [])]
    if status == STATUS_QUEUED or not attempts:
        return None, COST_NOT_APPLICABLE
    if status == STATUS_RUNNING:
        return None, COST_UNKNOWN
    for stage, attempt in attempts:
        if not isinstance(attempt, dict):
            return None, COST_UNKNOWN
        observations = attempt.get("observations")
        if (not isinstance(observations, dict)
                or type(observations.get("download_events")) is not int
                or observations["download_events"] != 0
                or type(observations.get("model_calls")) is not int
                or observations["model_calls"] != 0
                or (stage == "source" and not _source_attempt_is_safe(attempt))):
            return None, COST_UNKNOWN
    return {"currency": "USD", "value": "0.00"}, COST_KNOWN


def job_view(job: dict[str, Any], store: JobStore, *, lock_alive: bool | None = None) -> dict[str, Any]:
    if lock_alive is None:
        lock_alive = store.lock(str(job.get("owner_job_id", ""))).is_locked()
    status = derive_live_status(job, store, lock_alive=lock_alive)
    if status == STATUS_UNKNOWN:
        # an unparsable attempt record means the state is NOT known: keep the
        # contract pairing status=unknown <-> status_known=false intact
        return _unknown_view(job.get("owner_job_id"))
    stage_views = derive_stage_views(job, store, lock_alive=lock_alive)
    actions = _allowed_actions(status)
    if (ACTION_RESUME in actions and stage_views[0]["status"] != "completed"
            and not all(_source_attempt_is_safe(attempt) for attempt in job["stages"]["source"]["attempts"])):
        actions.remove(ACTION_RESUME)
    view: dict[str, Any] = {
        "schema_version": PROTOCOL_SCHEMA,
        "kind": "rf_job",
        "owner_job_id": job.get("owner_job_id"),
        "status": status,
        "status_known": True,
        "allowed_actions": actions,
        "cost": None,
        "cost_state": COST_NOT_APPLICABLE,
        "recovery_capability": RECOVERY_DURABLE,
        "command_recovery": dict(COMMAND_RECOVERY),
        "stages": stage_views,
        "scope": job.get("scope"),
        "limits_ref": job.get("limits_ref"),
        "budget": job.get("budget"),
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at"),
        "idempotent_replay": bool(job.get("idempotent_replay", False)),
        "result": job.get("result"),
        "catalog_history": {
            "cli": "scripts/report_catalog_cli.py",
            "registration": ("separate RF owner admission via import-research-publication "
                             "or import-research-attempt"),
            "this_job_registered": False,
        },
    }
    cost, cost_state = _cost_projection(job, status)
    view["cost"] = cost
    view["cost_state"] = cost_state
    return view


def _unknown_view(owner_job_id: str | None) -> dict[str, Any]:
    return {
        "schema_version": PROTOCOL_SCHEMA,
        "kind": "rf_job",
        "owner_job_id": owner_job_id,
        "status": STATUS_UNKNOWN,
        "status_known": False,
        "allowed_actions": [ACTION_RECONCILE],
        "cost": None,
        "cost_state": COST_UNKNOWN,
        "recovery_capability": RECOVERY_DURABLE,
        "command_recovery": dict(COMMAND_RECOVERY),
    }


# ------------------------------------------------------------- public ops


class JobFacade:
    """The public full_research job facade over one owner workspace."""

    def __init__(self, owner_root: Path, deployment: Deployment | None,
                 runner_factory: Callable[[JobStore, str], SubprocessStageRunner] | None = None):
        self.owner_root = owner_root
        self.store = JobStore(owner_root)
        self.deployment = deployment
        self._runner_factory = runner_factory or (
            lambda store, job_id: SubprocessStageRunner(store, job_id))

    def _required_deployment(self) -> Deployment:
        if self.deployment is None:
            raise JobFacadeError("deployment_config_required",
                                 "submit and resume require the trusted --deployment-config")
        return self.deployment

    # ---- submit ------------------------------------------------------------

    def submit(self, raw_request: Any) -> dict[str, Any]:
        normalized = normalize_request(raw_request)
        limits_ref = normalized["limits_ref"]
        limits = self._required_deployment().limits_for(limits_ref)
        key_sha = normalized["idempotency_key_sha256"]
        request_sha = normalized["request_sha256"]
        # Creation is serialized store-wide so two concurrent submits with the
        # same idempotency key cannot both win the index claim.
        with self.store._creation_lock():
            existing = self.store.idempotency_get(key_sha)
            if existing is not None:
                owner_job_id = existing.get("owner_job_id")
                if not isinstance(owner_job_id, str):
                    raise JobFacadeError("job_state_unreadable",
                                         "the idempotency index references an unusable job id")
                job = self.store.load_job(owner_job_id)
                if job.get("request_sha256") != request_sha:
                    raise JobFacadeError("idempotency_key_conflict",
                                         "the idempotency key is already bound to a different request")
                job["idempotent_replay"] = True
                return {"owner_job_id": owner_job_id, "job_view": job_view(job, self.store)}
            owner_job_id = _new_owner_job_id()
            job = _fresh_job(owner_job_id=owner_job_id, normalized=normalized,
                             limits_ref=limits_ref, limits=limits, request_sha256=request_sha)
            self.store.save_job(job)
            self.store.idempotency_put(key_sha, {
                "owner_job_id": owner_job_id,
                "request_sha256": request_sha,
                "created_at": _utc_now(),
            })
            self.store.append_jobs_index(owner_job_id, job["created_at"])
        return self._orchestrate_locked(owner_job_id, submitting=True)

    # ---- status ------------------------------------------------------------

    def get_status(self, owner_job_id: str) -> dict[str, Any]:
        self.store._require_job_id(owner_job_id)
        try:
            job = self.store.load_job(owner_job_id)
        except JobFacadeError as exc:
            if exc.code == "owner_job_not_found":
                raise
            return {"owner_job_id": owner_job_id, "job_view": _unknown_view(owner_job_id)}
        return {"owner_job_id": owner_job_id, "job_view": job_view(job, self.store)}

    def list_jobs(self, limit: int = 50) -> dict[str, Any]:
        ids = self.store.list_job_ids()
        selected = ids[-limit:] if limit > 0 else ids
        views: list[dict[str, Any]] = []
        for owner_job_id in selected:
            try:
                job = self.store.load_job(owner_job_id)
            except JobFacadeError:
                views.append(_unknown_view(owner_job_id))
                continue
            views.append(job_view(job, self.store))
        return {"schema_version": PROTOCOL_SCHEMA, "jobs": views}

    # ---- actions -----------------------------------------------------------

    def act(self, owner_job_id: str, action: str) -> dict[str, Any]:
        if action not in (ACTION_RESUME, ACTION_RECONCILE):
            raise JobFacadeError("action_not_allowed",
                                 "the requested action is not a facade action")
        if action == ACTION_RECONCILE:
            return self._reconcile(owner_job_id)
        return self._orchestrate_locked(owner_job_id)

    def _repair_stages(self, job: dict[str, Any], status: str) -> bool:
        """Repair only under the per-job owner mutex."""
        if status == STATUS_UNKNOWN:
            return False
        changed = job.get("status") != status or job.get("status_known") is not True
        job["status"] = status
        job["status_known"] = True
        for stage in STAGES:
            state = job["stages"][stage]
            last = _last_attempt(state)
            if last is not None and last.get("status") == "running":
                last["status"] = "interrupted"
                last["ended_at"] = last.get("ended_at") or _utc_now()
                last["interrupted_by"] = "reconcile"
                changed = True
            derived = _derive_stage_status(job, self.store, stage, lock_alive=False)
            changed |= state.get("status") != derived
            state["status"] = derived
        return changed

    def _reconcile(self, owner_job_id: str) -> dict[str, Any]:
        if not self.store.job_file(owner_job_id).is_file():
            return {"owner_job_id": owner_job_id, "job_view": _unknown_view(owner_job_id)}
        lock = self.store.lock(owner_job_id)
        if not lock.acquire():
            return self.get_status(owner_job_id)
        try:
            try:
                job = self.store.load_job(owner_job_id)
            except JobFacadeError:
                return {"owner_job_id": owner_job_id, "job_view": _unknown_view(owner_job_id)}
            status = derive_live_status(job, self.store, lock_alive=False)
            if self._repair_stages(job, status):
                self.store.save_job(job)
            return {"owner_job_id": owner_job_id,
                    "job_view": job_view(job, self.store, lock_alive=False)}
        finally:
            lock.release()

    def _orchestrate_locked(self, owner_job_id: str, *, submitting: bool = False) -> dict[str, Any]:
        if not self.store.job_file(owner_job_id).is_file():
            raise JobFacadeError("owner_job_not_found", "no such owner job exists in the store")
        lock = self.store.lock(owner_job_id)
        if not lock.acquire():
            if submitting:
                return self.get_status(owner_job_id)
            raise JobFacadeError("lock_unavailable", "another orchestration of this job is active")
        try:
            job = self.store.load_job(owner_job_id)
            view = job_view(job, self.store, lock_alive=False)
            if ACTION_RESUME not in view["allowed_actions"]:
                if submitting:
                    return {"owner_job_id": owner_job_id, "job_view": view}
                raise JobFacadeError("action_not_allowed", "resume would not safely advance this job")
            deployment = self._required_deployment()
            self._repair_stages(job, view["status"])
            job["status"] = STATUS_RUNNING
            job.pop("stop", None)
            self.store.save_job(job)
            runner = self._runner_factory(self.store, owner_job_id)
            try:
                _orchestrate(job, store=self.store, deployment=deployment, runner=runner)
            except JobFacadeError:
                pass  # phase failures are recorded durably
            return {"owner_job_id": owner_job_id,
                    "job_view": job_view(self.store.load_job(owner_job_id), self.store, lock_alive=False)}
        finally:
            lock.release()
