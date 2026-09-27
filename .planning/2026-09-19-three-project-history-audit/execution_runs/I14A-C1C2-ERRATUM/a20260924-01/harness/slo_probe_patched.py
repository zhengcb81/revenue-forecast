"""FC-1303 / I-14-A: production SLO probe (READ-ONLY), failure-branch first.

This file is an ISOLATED COPY of ``RF/tools/slo_probe.py``
(sha256 f051feec00658bb5fefee8d22c2c7630e0bd348b5384ae80f0c882c822f48059) with the
I-14-A changes applied.  Nothing here is installed and the product repo was not
edited.

What I-14-A changes, and why:

* the resolve subprocess **return code** is captured and a non-zero rc is a
  measurement failure, never a success sample (the audit row "SLO 探针 … 忽略子进程
  rc");
* a **business-status** failure is a measurement failure even when rc == 0;
* RSS is sampled **while the child is alive** by a sampler thread keyed to the
  child pid; "no sample collected" is reported as ``null`` with
  ``peak_rss_source = "uncollected"`` and can never read as 0.0 or as green;
* three separate windows are reported: the SLO business-latency window, the RSS
  sampling window, and a separately labelled ``quick_check`` window, plus the
  whole-command duration;
* ``--catalog`` and the config's own ``catalog_dir`` are checked for
  consistency and a mismatch is refused (exit 3) instead of silently measuring
  a different catalog than the one named;
* the real bundle path is measured separately; a copied ``exact`` latency can no
  longer grant bundle eligibility (``bundle.basis`` must be ``measured``).

Frozen budgets are untouched: exact/latest/bundle p95 = 5.0s, peak_rss_gb = 2.0.

Exit codes: 0 green; 1 catalog missing / bad probe arguments; 2 budget breach
(alarm, not fatal); 3 binding refusal; 4 measurement failure.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WIKI_ROOT = PROJECT_ROOT.parent / "company-wiki"
DEFAULT_CATALOG = WIKI_ROOT / ".source_catalog" / "catalog.sqlite3"
DEFAULT_CONFIG = WIKI_ROOT / "config" / "source_catalog.yaml"

# Frozen SLO budgets (seconds) — measured then frozen (FC-1303, findings 62).
BUDGETS = {
    "exact_p95": 5.0,
    "latest_p95": 5.0,
    "bundle_p95": 5.0,
    "peak_rss_gb": 2.0,
}

SAMPLES = 10

# Canary probes (real production documents registered by FC-504/FC-906).
EXACT_PROBE = {"company_query": "紫金矿业", "market": "CN",
               "document_kind": "annual_report", "fiscal_year": 2025}
LATEST_PROBE = {"company_query": "紫金矿业", "market": "CN",
                "document_kind": "annual_report", "mode": "latest_as_of"}

DEFAULT_RESOLVE_TEMPLATE = [
    sys.executable, "-m", "company_wiki.source_catalog.cli", "resolve",
]

# I-14-A: a resolve call is a *business* success only when it exits 0 AND its
# stdout carries an explicit success status.  Anything else is a failed request
# that must be reported as a failure, never dropped to make the SLO look green.
SUCCESS_STATUSES = {"ok", "success", "succeeded", "resolved", "found", "completed"}
FAILURE_STATUSES = {"failed", "failure", "error", "missing", "not_found", "refused",
                    "ambiguous", "blocked"}

RSS_SAMPLE_INTERVAL_SECONDS = 0.05


# --------------------------------------------------------------------------- #
# config / catalog binding
# --------------------------------------------------------------------------- #
def _strip_scalar(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    elif " #" in value:
        value = value.split(" #", 1)[0].strip()
    return value


def config_catalog_dir(config: Path) -> Path:
    """Resolve ``catalog_dir`` from a source_catalog.yaml the way the product does.

    Deliberately a small top-level scalar reader, not a YAML implementation: the
    probe must not gain a dependency it cannot audit, and the value it needs is a
    single unquoted-or-quoted scalar.  The limits are recorded in the attempt's
    oracle.md; a config whose scalar uses YAML block/escape forms must make this
    function fail rather than guess (it raises ValueError).
    """
    text = config.read_text(encoding="utf-8")
    found = None
    for line in text.splitlines():
        if line.startswith(("#", " ", "\t", "-")):
            continue
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        if key.strip() != "catalog_dir":
            continue
        found = _strip_scalar(rest)
        break
    if found is None:
        raise ValueError(f"catalog_dir not found in {config}")
    project_root = config.resolve().parents[1]
    expanded = found.replace("${PROJECT_ROOT}", str(project_root))
    expanded = expanded.replace("${USER_PROFILE}",
                                os.environ.get("USERPROFILE", str(Path.home())))
    if "${" in expanded:
        raise ValueError(f"unresolved variable in catalog_dir: {found}")
    return Path(expanded)


def _probe_catalog_path(catalog_dir: Path) -> Path:
    """The catalog file the product's own resolver would open for ``catalog_dir``.

    The product tolerates a stale ``catalog.sqlite3`` next to a live ``catalog.db``
    (its own config lands on ``catalog.sqlite3``, its release-readiness gate on
    ``catalog.db``), so this must not be guessed: the caller compares against the
    actual file it was pointed at and refuses when the directory is the same but
    the filename is one of the two known catalog names.
    """
    return catalog_dir / "catalog.sqlite3"


def check_catalog_binding(catalog: Path, config: Path) -> dict:
    """I-14-A: --catalog used to be an existence check while resolve used --config.

    ``catalog_dir`` names a *directory*; ``--catalog`` names the sqlite *file* to
    measure.  The binding is consistent when the file lives inside the configured
    directory under one of the two catalog names the product itself uses
    (``catalog.sqlite3`` / ``catalog.db``).  A file outside the configured
    directory is a mismatch and is refused.
    """
    result = {
        "catalog_argument": str(catalog),
        "config_path": str(config),
        "config_exists": config.is_file(),
        "configured_catalog_dir": None,
        "same_directory": None,
        "catalog_filename_allowed": None,
        "consistent": None,
        "basis": "catalog_file_within_config_catalog_dir",
    }
    if not config.is_file():
        result["consistent"] = False
        result["error"] = "config_missing"
        return result
    try:
        configured = config_catalog_dir(config)
    except ValueError as exc:
        result["consistent"] = False
        result["error"] = "config_unreadable_by_probe_parser"
        result["detail"] = str(exc)
        return result
    result["configured_catalog_dir"] = str(configured)
    result["configured_catalog_file"] = str(_probe_catalog_path(configured))
    try:
        same_dir = configured.resolve(strict=False) == catalog.resolve(strict=False).parent
    except OSError:
        same_dir = str(configured) == str(catalog.parent)
    result["same_directory"] = same_dir
    result["catalog_filename_allowed"] = catalog.name in ("catalog.sqlite3", "catalog.db")
    result["consistent"] = bool(same_dir and result["catalog_filename_allowed"])
    return result


# --------------------------------------------------------------------------- #
# RSS sampling
# --------------------------------------------------------------------------- #
class RssSampler:
    """Sample the child process tree's RSS while it is alive.

    ``psutil`` may be absent; then nothing is collected and the probe reports the
    sample as *uncollected*, never as zero (the old code fell back to the probe's
    own peak working set, which is a different process).
    """

    def __init__(self, enabled: bool = True,
                 interval: float = RSS_SAMPLE_INTERVAL_SECONDS) -> None:
        self.enabled = enabled
        self.interval = interval
        # (t, tuple_of_pids_measured, rss_bytes) — the pid set is recorded so the
        # report can prove *which* processes were sampled, not just the tree root.
        self.samples: list[tuple[float, tuple[int, ...], int]] = []
        self._pid: int | None = None
        self._stop = threading.Event()
        self._tick = threading.Event()
        self._thread: threading.Thread | None = None
        self._psutil = None
        self._error: str | None = None
        if enabled:
            try:
                import psutil  # noqa: PLC0415
                self._psutil = psutil
            except ImportError:
                self._error = "psutil_missing"

    def start(self, pid: int) -> None:
        self._pid = pid
        if not self.enabled or self._psutil is None:
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def sample_now(self) -> None:
        """Force one extra sample at a known-good moment (child still alive).

        A very short child can finish before the interval timer fires again, so a
        sample is requested the moment its stdout envelope is read — that is the
        last moment the child is known to be alive.
        """
        self._tick.set()

    def _collect(self) -> None:
        if self._pid is None or self._psutil is None:
            return
        try:
            proc = self._psutil.Process(self._pid)
            tree = [proc, *proc.children(recursive=True)]
        except Exception as exc:                     # process already gone
            self._error = f"{type(exc).__name__}"
            return
        # Windows fact: `Popen.pid` is the process CreateProcess started, while the
        # measured program may run in a descendant (observed here: the isolated
        # venv's python.exe is the parent and the script body is its child), so the
        # tree — not a single pid — is what gets summed, and every pid in it is
        # recorded with the sample.
        measured: list[int] = []
        total = 0
        for item in tree:
            try:
                total += item.memory_info().rss
                measured.append(item.pid)
            except Exception:
                continue
        if measured:
            self.samples.append((time.perf_counter(), tuple(sorted(measured)), total))

    def _run(self) -> None:
        self._collect()
        while not self._stop.is_set():
            self._tick.wait(self.interval)
            self._tick.clear()
            self._collect()

    def stop(self, child_exit_monotonic: float) -> dict:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5.0)
        if not self.enabled:
            return self._summary(None, "sampler_disabled", child_exit_monotonic)
        if self._psutil is None:
            return self._summary(None, f"uncollected:{self._error}", child_exit_monotonic)
        nonzero = [s for s in self.samples if s[2] > 0]
        if not nonzero:
            reason = "uncollected:no_sample" if not self.samples \
                else "uncollected:all_samples_zero"
            return self._summary(None, reason, child_exit_monotonic)
        peak_t, peak_pids, peak_rss = max(nonzero, key=lambda s: s[2])
        summary = self._summary(peak_rss / (1024 ** 3), "live_sample",
                                child_exit_monotonic)
        summary["peak_pid"] = peak_pids[0] if len(peak_pids) == 1 else None
        summary["peak_tree_pids"] = list(peak_pids)
        summary["peak_sample_age_seconds"] = round(child_exit_monotonic - peak_t, 6)
        return summary

    def _summary(self, peak_gb, source: str, child_exit_monotonic: float) -> dict:
        pids = sorted({pid for _, sample_pids, _ in self.samples for pid in sample_pids})
        window = 0.0
        if self.samples:
            window = self.samples[-1][0] - self.samples[0][0]
        return {
            "peak_rss_gb": round(peak_gb, 3) if peak_gb is not None else None,
            "peak_rss_source": source,
            "rss_sample_count": len(self.samples),
            "rss_sampled_pids": pids,
            "rss_sampling_interval_seconds": self.interval,
            "rss_sample_window_seconds": round(window, 6),
            "rss_sampler_thread_alive_during_child": self._thread is not None,
            "rss_error": self._error,
            "child_exit_monotonic": round(child_exit_monotonic, 6),
        }


# --------------------------------------------------------------------------- #
# one resolve call
# --------------------------------------------------------------------------- #
def _request_argv(request: dict) -> list[str]:
    argv: list[str] = []
    if "company_query" in request:
        argv += ["--company-query", str(request["company_query"])]
    elif "entity" in request:
        argv += ["--entity", str(request["entity"])]
    if request.get("market"):
        argv += ["--market", str(request["market"])]
    argv += ["--document-kind", str(request["document_kind"])]
    if request.get("mode") == "latest_as_of":
        argv += ["--mode", "latest_as_of"]
    elif request.get("mode"):
        argv += ["--mode", str(request["mode"])]
    else:
        argv += ["--fiscal-year", str(request["fiscal_year"])]
    return argv


def _business_status(stdout: str) -> tuple[bool, str, str | None]:
    """(ok, kind, detail) for the call's stdout envelope contract.

    The envelope is the **first** non-empty stdout line.  A resolver may print
    progress or a trailing summary after the envelope (fixture F3 does), so
    parsing the whole stream as one JSON document would reject a successful call
    for the wrong reason; the contract is explicitly "the first line is the
    envelope", and any later line is not part of it.
    """
    text = (stdout or "").strip()
    if not text:
        return False, "business_empty_stdout", None
    first = next((line for line in text.splitlines() if line.strip()), "")
    try:
        payload = json.loads(first)
    except json.JSONDecodeError as exc:
        return False, "business_unparseable", str(exc)[:160]
    if not isinstance(payload, dict):
        return False, "business_not_an_object", type(payload).__name__
    status = payload.get("status")
    if status is None:
        return False, "business_missing_status", None
    lowered = str(status).lower()
    if lowered in SUCCESS_STATUSES:
        return True, "ok", None
    if lowered in FAILURE_STATUSES:
        return False, "business_failure_status", str(status)
    return False, "business_unknown_status", str(status)


def _resolve_once(request: dict, config: Path, template: list[str], cwd: Path,
                  timeout: float, sampler: RssSampler) -> tuple[float, dict]:
    """One resolve call; returns (elapsed, call record).

    A failure to *spawn* the resolver is itself a measurement failure: it must be
    recorded and must never leave the run looking green.
    """
    cmd = [*template, "--config", str(config), *_request_argv(request)]
    spawn_t = time.perf_counter()
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, encoding="utf-8", errors="replace",
                                cwd=str(cwd))
    except OSError as exc:
        exit_t = time.perf_counter()
        record = {
            "argv_tail": cmd[len(template):],
            "child_pid": None,
            "raw_returncode": None,
            "spawn_error": f"{type(exc).__name__}: {exc}",
            "timed_out": False,
            "elapsed_seconds": round(exit_t - spawn_t, 6),
            "stdout_head": "",
            "stderr_head": "",
            "rss": sampler.stop(exit_t),
            "succeeded": False,
            "failure_kind": "spawn_error",
            "business_kind": "not_evaluated",
        }
        return record["elapsed_seconds"], record
    sampler.start(proc.pid)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        timed_out = False
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        timed_out = True
    # The child has just exited.  Its tree membership was only observable while it
    # lived, so ask for the final sample now rather than hoping the interval timer
    # fired in time.
    sampler.sample_now()
    exit_t = time.perf_counter()
    elapsed = exit_t - spawn_t
    rss = sampler.stop(exit_t)

    record = {
        "argv_tail": cmd[len(template):],
        "child_pid": proc.pid,
        "raw_returncode": proc.returncode,
        "timed_out": timed_out,
        "elapsed_seconds": round(elapsed, 6),
        "stdout_head": (stdout or "")[:400],
        "stderr_head": (stderr or "")[:400],
        "rss": rss,
    }
    if timed_out:
        record.update(succeeded=False, failure_kind="timeout",
                      business_kind="not_evaluated")
        return elapsed, record

    ok, kind, detail = _business_status(stdout)
    record["business_kind"] = kind
    record["business_detail"] = detail
    if proc.returncode != 0:
        record.update(succeeded=False, failure_kind="subprocess_rc", business_ok=ok)
    elif not ok:
        record.update(succeeded=False, failure_kind="business_status", business_ok=False)
    else:
        record.update(succeeded=True, failure_kind=None, business_ok=True)
    return elapsed, record


def _percentiles(values: list[float]) -> dict[str, float]:
    ordered = sorted(values)
    return {
        "p50": statistics.median(ordered),
        "p95": ordered[min(len(ordered) - 1, int(len(ordered) * 0.95))],
        "p99": ordered[min(len(ordered) - 1, int(len(ordered) * 0.99))],
    }


def _latency_block(calls: list[dict]) -> dict:
    ok = [c["elapsed_seconds"] for c in calls if c["succeeded"]]
    failed = [c["elapsed_seconds"] for c in calls if not c["succeeded"]]
    block = {"succeeded": _percentiles(ok) if ok else None,
             "succeeded_count": len(ok),
             "failed_count": len(failed)}
    if failed:
        block["failed_elapsed_seconds"] = {
            "min": round(min(failed), 6), "max": round(max(failed), 6),
            "values": [round(v, 6) for v in failed]}
    return block


def _quick_check(catalog: Path, python: str, timeout: float) -> dict:
    """Separately labelled DB check window — deliberately outside the SLO window."""
    sql = ("import sqlite3,sys;c=sqlite3.connect(sys.argv[1]);"
           "print(c.execute('PRAGMA quick_check').fetchone()[0])")
    t0 = time.perf_counter()
    try:
        proc = subprocess.run([python, "-B", "-c", sql, str(catalog)],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout)
        rc, out, err = proc.returncode, proc.stdout.strip(), proc.stderr[:400]
    except subprocess.TimeoutExpired:
        rc, out, err = None, "", "timeout"
    return {
        "enabled": True,
        "scope": "separate_window_excluded_from_slo",
        "argv": [python, "-B", "-c", "<PRAGMA quick_check>", str(catalog)],
        "raw_returncode": rc,
        "result": out,
        "stderr_head": err,
        "elapsed_seconds": round(time.perf_counter() - t0, 6),
    }


def _load_bundle_measurement(path: Path | None, exact_calls: list[dict]) -> dict:
    """Real bundle-path measurement, never a copy of the exact latencies."""
    out: dict = {"measured": False, "basis": "unmeasured", "source": None,
                 "identity_check": None}
    if path is None or not path.is_file():
        out["note"] = ("no --bundle-measurement given: the bundle budget cannot be "
                       "satisfied by the exact latency (I-14-A)")
        return out
    payload = json.loads(path.read_text(encoding="utf-8"))
    values = payload.get("bundle_latencies_seconds")
    if not isinstance(values, list) or not values:
        out["basis"] = "invalid_measurement_file"
        return out
    out.update(measured=True, basis="measured", source=str(path),
               values=[float(v) for v in values],
               measured_window_seconds=payload.get("window_seconds"),
               command=payload.get("command"))
    exact_values = [c["elapsed_seconds"] for c in exact_calls if c["succeeded"]]
    same_object = values is exact_values
    same_values = bool(exact_values) and len(values) == len(exact_values) and \
        all(abs(a - b) < 1e-12 for a, b in zip(values, exact_values))
    out["identity_check"] = {
        "same_list_object_as_exact": same_object,
        "numerically_identical_to_exact": same_values,
        "verdict": "copied_exact" if (same_object or same_values) else "independent",
    }
    if out["identity_check"]["verdict"] == "copied_exact":
        out.update(measured=False, basis="copied_from_exact")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--samples", type=int, default=SAMPLES)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--resolve-cmd", default=None,
                        help="JSON list: template argv that receives the resolve "
                             "arguments (I-14-A injection; default = the frozen "
                             "company_wiki resolve CLI)")
    parser.add_argument("--resolve-cwd", type=Path, default=None)
    parser.add_argument("--timeout-seconds", type=float, default=120.0)
    parser.add_argument("--rss-sampler", choices=("auto", "none"), default="auto")
    parser.add_argument("--bundle-measurement", type=Path, default=None)
    parser.add_argument("--quick-check", choices=("auto", "skip"), default="auto")
    parser.add_argument("--require-catalog-config-match",
                        choices=("reject", "warn", "off"), default="reject")
    args = parser.parse_args(argv)

    command_total_t0 = time.perf_counter()
    if not args.catalog.is_file():
        print(f"catalog missing: {args.catalog}", file=sys.stderr)
        return 1

    binding = check_catalog_binding(args.catalog, args.config)
    if binding["consistent"] is not True:
        if args.require_catalog_config_match == "reject":
            payload = {"error": "catalog_config_mismatch", "binding": binding,
                       "measured": False}
            if args.report is not None:
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(json.dumps(payload, ensure_ascii=False,
                                                  indent=2), encoding="utf-8")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
            return 3
        if args.require_catalog_config_match == "warn":
            print(f"WARNING: catalog/config mismatch: {binding}", file=sys.stderr)

    template = DEFAULT_RESOLVE_TEMPLATE
    if args.resolve_cmd:
        template = json.loads(args.resolve_cmd)
        if not isinstance(template, list) or not template:
            print("--resolve-cmd must be a non-empty JSON list", file=sys.stderr)
            return 1
    run_cwd = args.resolve_cwd or WIKI_ROOT

    samples = max(3, args.samples)
    exact_calls: list[dict] = []
    latest_calls: list[dict] = []
    slo_t0 = time.perf_counter()
    for _ in range(samples):
        for bucket, request in ((exact_calls, EXACT_PROBE),
                                (latest_calls, LATEST_PROBE)):
            sampler = RssSampler(args.rss_sampler == "auto")
            _, rec = _resolve_once(request, args.config, template, run_cwd,
                                   args.timeout_seconds, sampler)
            bucket.append(rec)
    slo_window = time.perf_counter() - slo_t0

    exact_block = _latency_block(exact_calls)
    latest_block = _latency_block(latest_calls)
    bundle = _load_bundle_measurement(args.bundle_measurement, exact_calls)

    all_calls = exact_calls + latest_calls
    rss_sources = [c["rss"]["peak_rss_source"] for c in all_calls]
    rss_peaks = [c["rss"]["peak_rss_gb"] for c in all_calls
                 if c["rss"]["peak_rss_gb"] is not None]
    rss_pids = sorted({pid for c in all_calls for pid in c["rss"]["rss_sampled_pids"]})
    rss_windows = [c["rss"]["rss_sample_window_seconds"] for c in all_calls]
    rss_counts = [c["rss"]["rss_sample_count"] for c in all_calls]
    rss_peak_gb = round(max(rss_peaks), 3) if rss_peaks else None
    rss_uncollected = None if rss_peaks else (
        rss_sources[0] if rss_sources else "uncollected:no_call")

    quick = ({"enabled": False, "scope": "separate_window_excluded_from_slo"}
             if args.quick_check == "skip"
             else _quick_check(args.catalog, sys.executable, args.timeout_seconds))

    calls_failed = [c for c in all_calls if not c["succeeded"]]
    failed_kinds: dict[str, int] = {}
    for c in calls_failed:
        failed_kinds[c["failure_kind"]] = failed_kinds.get(c["failure_kind"], 0) + 1

    results = {
        "exact": {"percentiles": exact_block["succeeded"],
                  "succeeded_count": exact_block["succeeded_count"],
                  "failed_count": exact_block["failed_count"],
                  "failed_elapsed_seconds": exact_block.get("failed_elapsed_seconds")},
        "latest": {"percentiles": latest_block["succeeded"],
                   "succeeded_count": latest_block["succeeded_count"],
                   "failed_count": latest_block["failed_count"],
                   "failed_elapsed_seconds": latest_block.get("failed_elapsed_seconds")},
        "bundle": {"percentiles": (_percentiles(bundle["values"])
                                   if bundle.get("measured") else None),
                   "measured": bool(bundle.get("measured")),
                   "basis": bundle.get("basis"),
                   "identity_check": bundle.get("identity_check")},
        "peak_rss_gb": rss_peak_gb,
        "peak_rss_source": ("live_sample" if rss_peak_gb is not None
                            else rss_uncollected),
        "rss_sampled_pids": rss_pids,
        "rss_sample_count_total": sum(rss_counts),
        "rss_sample_count_min": min(rss_counts) if rss_counts else 0,
        "samples": samples,
        "catalog": str(args.catalog),
        "config": str(args.config),
    }
    windows = {
        "command_total_seconds": round(time.perf_counter() - command_total_t0, 6),
        "slo_window_seconds": round(slo_window, 6),
        "rss_sample_window_seconds_max": round(max(rss_windows), 6) if rss_windows else 0.0,
        "quick_check_seconds": quick.get("elapsed_seconds"),
        "quick_check_included_in_slo_window": False,
    }
    calls = {
        "total": len(all_calls),
        "succeeded": len(all_calls) - len(calls_failed),
        "failed": len(calls_failed),
        "failed_kinds": failed_kinds,
        "success_latency_and_failure_rate_reported_separately": True,
    }

    breaches: list[str] = []
    if exact_block["succeeded"] is None:
        breaches.append("exact: no successful call — latency unmeasurable")
    elif exact_block["succeeded"]["p95"] > BUDGETS["exact_p95"]:
        breaches.append(
            f"exact p95 {exact_block['succeeded']['p95']:.3f}s > {BUDGETS['exact_p95']}s")
    if latest_block["succeeded"] is None:
        breaches.append("latest: no successful call — latency unmeasurable")
    elif latest_block["succeeded"]["p95"] > BUDGETS["latest_p95"]:
        breaches.append(
            f"latest p95 {latest_block['succeeded']['p95']:.3f}s > {BUDGETS['latest_p95']}s")
    if not bundle.get("measured"):
        breaches.append(f"bundle: basis={bundle.get('basis')} — bundle SLO is NOT qualified")
    elif bundle["values"] and _percentiles(bundle["values"])["p95"] > BUDGETS["bundle_p95"]:
        breaches.append(
            f"bundle p95 {_percentiles(bundle['values'])['p95']:.3f}s > "
            f"{BUDGETS['bundle_p95']}s")
    if results["peak_rss_gb"] is None:
        breaches.append(f"peak RSS not measured ({results['peak_rss_source']}) — "
                        "an unmeasured RSS can never be reported as within budget")
    elif results["peak_rss_gb"] > BUDGETS["peak_rss_gb"]:
        breaches.append(
            f"peak RSS {results['peak_rss_gb']}GB > {BUDGETS['peak_rss_gb']}GB")

    report = {
        "slo_probe": results,
        "windows": windows,
        "calls": calls,
        "quick_check": quick,
        "binding": binding,
        "per_call": all_calls,
        "budgets": BUDGETS,
        "breaches": breaches,
        "measured_targets": {"resolve_template": template, "resolve_cwd": str(run_cwd)},
    }
    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                               encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "per_call"},
                     ensure_ascii=False, indent=2))
    if calls_failed:
        return 4
    return 2 if breaches else 0


if __name__ == "__main__":
    sys.exit(main())
