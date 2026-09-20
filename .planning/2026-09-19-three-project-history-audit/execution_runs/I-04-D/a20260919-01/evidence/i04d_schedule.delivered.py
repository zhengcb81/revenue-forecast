"""I-04-D scheduler: real multi-process, barrier-ordered lease cases.

Every participant is a separate OS process (its own pid, its own fake-worker
children).  Ordering is pinned by FILE FENCES, never by sleeps: a participant that
reaches an instrumented point writes ``gate.<name>.<tag>.reached`` and then blocks
until the scheduler writes ``gate.<name>.fence``.

Usage (from iso/filing-fetch):
  python scripts/i04d_schedule.py list
  python scripts/i04d_schedule.py run <case> --out <dir> [--case <case> ...]

Outputs, per case, into <dir>/<case>/:
  participants.json  argv, pid, start/end monotonic, exit code, report
  journal.jsonl      the lease protocol journal (from the code under test)
  worker.jsonl       fake-worker invocations (pause/resume counters live here)
  worker_state.json  final worker state
  summary.json       the DERIVED observables the oracle is judged against
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
PYTHON = sys.executable
PARTICIPANT = HERE / "i04d_participant.py"
FAKE_WORKER = HERE / "i04d_fake_worker.py"

CATALOG = ".source_catalog"
REFCOUNT = "filing_fetch_pause.refcount"
OWNER = "filing_fetch_pause.owner"
LOCK = "filing_fetch_pause.lock"
PROTOCOL_JOURNAL = "filing_fetch_pause.journal.jsonl"

TRUNCATED = '{"schema": "filing-fetch.pause-refcount/2", "entries": ['
LEGACY = '[{"pid": 9003, "joined": false}]'
ELEMENT_CORRUPT = '{"schema": "filing-fetch.pause-refcount/2", "generation": 1, "resume": {"required": false}, "entries": [{"pid": 1}], "owner": null}'
THIRD_PARTY_OWNER = {
    "lease_id": "third-party-owner",
    "generation": 1,
    "pid": 999999,
    "boot_uuid": "ffffffffffff",
    "os_start_time": "",
}


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _sha256(path: Path) -> str:
    import hashlib

    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


class CaseRun:
    def __init__(self, name: str, out: Path) -> None:
        self.name = name
        base = os.environ.get("I04D_CASE_ROOT")
        self.dir = (Path(base) / name) if base else (out / name)
        if self.dir.exists():
            shutil.rmtree(self.dir)
        self.dir.mkdir(parents=True)
        self.root = self.dir / "wiki"
        (self.root / CATALOG).mkdir(parents=True)
        self.state = self.dir / "worker_state.json"
        self.worker_journal = self.dir / "worker.jsonl"
        self.state.write_text(
            json.dumps({"desired_state": "enabled", "runtime_state": "running"}),
            encoding="utf-8",
        )
        self.worker_journal.write_text("", encoding="utf-8")
        self.procs: dict[str, subprocess.Popen] = {}
        self.meta: dict[str, dict] = {}
        self.argv: dict[str, list[str]] = {}

    # -- path helpers ----------------------------------------------------
    @property
    def catalog(self) -> Path:
        return self.root / CATALOG

    @property
    def refcount(self) -> Path:
        return self.catalog / REFCOUNT

    @property
    def owner(self) -> Path:
        return self.catalog / OWNER

    @property
    def lock(self) -> Path:
        return self.catalog / LOCK

    @property
    def protocol_journal(self) -> Path:
        return self.catalog / PROTOCOL_JOURNAL

    # -- fences ----------------------------------------------------------
    def reached(self, name: str, tag: str = "") -> Path:
        base = f"gate.{name}.{tag}" if tag else f"gate.{name}"
        return self.dir / f"{base}.reached"

    def fence(self, name: str, tag: str = "") -> Path:
        base = f"gate.{name}.{tag}" if tag else f"gate.{name}"
        return self.dir / f"{base}.fence"

    def wait_reached(self, name: str, tag: str = "", timeout: float = 30.0) -> bool:
        path = self.reached(name, tag)
        limit = time.monotonic() + timeout
        while time.monotonic() < limit:
            if path.exists():
                return True
            time.sleep(0.01)
        return False

    def release(self, name: str, tag: str = "") -> None:
        self.fence(name, tag).write_text("go", encoding="utf-8")

    def arrival(self, name: str, tag: str = "") -> Path:
        return self.dir / f"arrive.{name}.{tag or 'all'}"

    def wait_arrival(self, name: str, tag: str = "", timeout: float = 30.0) -> bool:
        """Wait for a NON-BLOCKING arrival marker (the participant keeps running)."""
        path = self.arrival(name, tag)
        limit = time.monotonic() + timeout
        while time.monotonic() < limit:
            if path.exists():
                return True
            time.sleep(0.01)
        return False

    # -- participants ----------------------------------------------------
    def spawn(
        self,
        tag: str,
        *,
        request_budget: float = 900.0,
        hooks: str = "",
        nested: str = "",
        worker_enabled: str = "1",
        graceful: float = 1.0,
        resume_wait: float = 1.0,
        sleep_seconds: float = 0.0,
        wait_for: str = "",
        wait_timeout: float = 60.0,
        hold_for: str = "",
        hold_timeout: float = 60.0,
        extra_env: dict | None = None,
    ) -> subprocess.Popen:
        report = self.dir / f"report.{tag}.json"
        argv = [
            PYTHON,
            "-X",
            "utf8",
            "-B",
            str(PARTICIPANT),
            "--case",
            self.name,
            "--tag",
            tag,
            "--root",
            str(self.root),
            "--report",
            str(report),
            "--state",
            str(self.state),
            "--journal",
            str(self.worker_journal),
            "--request-budget",
            str(request_budget),
            "--graceful",
            str(graceful),
            "--resume-wait",
            str(resume_wait),
            "--worker-enabled",
            worker_enabled,
        ]
        if sleep_seconds:
            argv.extend(["--sleep-seconds", str(sleep_seconds)])
        if wait_for:
            argv.extend(["--wait-for", str(wait_for), "--wait-timeout", str(wait_timeout)])
        if hold_for:
            argv.extend(["--hold-for", str(hold_for), "--hold-timeout", str(hold_timeout)])
        if hooks:
            argv.extend(["--hooks", hooks])
        if nested:
            argv.extend(["--nested", nested])
        env = dict(os.environ)
        env["PYTHONUTF8"] = "1"
        env["I04D_WORKER_STATE"] = str(self.state)
        env["I04D_WORKER_JOURNAL"] = str(self.worker_journal)
        env["I04D_HOOK_DIR"] = str(self.dir)
        if extra_env:
            env.update(extra_env)
        stdout_path = self.dir / f"stdout.{tag}.txt"
        stderr_path = self.dir / f"stderr.{tag}.txt"
        self.argv[tag] = argv
        stdout_handle = stdout_path.open("wb")
        stderr_handle = stderr_path.open("wb")
        started = time.monotonic()
        proc = subprocess.Popen(  # noqa: S603 - argv list, no shell
            argv,
            cwd=str(HERE.parent),
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stdout_handle,
            stderr=stderr_handle,
        )
        proc._i04d_handles = (stdout_handle, stderr_handle)  # type: ignore[attr-defined]
        self.procs[tag] = proc
        self.meta[tag] = {
            "tag": tag,
            "argv": argv,
            "pid": proc.pid,
            "started_monotonic": started,
            "stdout": str(stdout_path),
            "stderr": str(stderr_path),
            "report": str(report),
        }
        return proc

    def reap(self, tag: str, timeout: float = 60.0) -> int:
        proc = self.procs[tag]
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            code = proc.wait(timeout=10)
            self.meta[tag]["killed_by_scheduler"] = True
        handles = getattr(proc, "_i04d_handles", ())
        for handle in handles:
            try:
                handle.close()
            except OSError:
                pass
        self.meta[tag]["exit_code"] = code
        hooks = self.argv[tag]
        if "--hooks" in hooks:
            spec = hooks[hooks.index("--hooks") + 1]
            for directive in spec.split(","):
                if directive.startswith("crash:"):
                    point, _, injected = directive.partition(":")[2].partition(":")
                    self.meta[tag]["injected_crash_point"] = point
                    self.meta[tag]["injected_crash_code"] = int(injected or 90)
        self.meta[tag]["finished_monotonic"] = time.monotonic()
        self.meta[tag]["elapsed_seconds"] = round(
            self.meta[tag]["finished_monotonic"] - self.meta[tag]["started_monotonic"], 4
        )
        return code

    def kill_recorded(self, tag: str) -> None:
        """Crash-window injection: kill ONLY a pid this harness itself recorded."""
        proc = self.procs.get(tag)
        if proc is None or proc.poll() is not None:
            return
        proc.kill()
        proc.wait(timeout=10)
        self.meta[tag]["killed_by_scheduler"] = True
        self.meta[tag]["exit_code"] = proc.returncode

    def report(self, tag: str) -> dict:
        return _read_json(self.dir / f"report.{tag}.json") or {}

    def wait_snapshot(self, tag: str, timeout: float = 30.0) -> bool:
        """Wait until the participant is parked in its scope body.

        The participant writes ``signal.<tag>.ready`` just before it starts waiting,
        so this observes a real state instead of guessing a sleep.
        """
        path = self.dir / f"signal.{tag}.ready"
        limit = time.monotonic() + timeout
        while time.monotonic() < limit:
            if path.exists():
                return True
            time.sleep(0.005)
        return False

    # -- finalisation ----------------------------------------------------
    def worker_calls(self) -> dict:
        counts = {"worker-status": 0, "worker-pause": 0, "worker-resume": 0, "other": 0}
        events = []
        try:
            lines = self.worker_journal.read_text(encoding="utf-8").splitlines()
        except OSError:
            lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except ValueError:
                continue
            subcommand = record.get("subcommand")
            if subcommand in counts:
                counts[subcommand] += 1
            else:
                counts["other"] += 1
            events.append(
                {
                    "subcommand": subcommand,
                    "pid": record.get("pid"),
                    "ppid": record.get("ppid"),
                    "result": record.get("result"),
                    "desired_state": record.get("desired_state"),
                    "runtime_state": record.get("runtime_state"),
                    "monotonic": record.get("monotonic"),
                }
            )
        return {"counts": counts, "events": events}

    def summarise(self) -> dict:
        worker = self.worker_calls()
        final_state = _read_json(self.state) or {}
        snapshot = {
            "refcount_exists": self.refcount.exists(),
            "refcount_sha256": _sha256(self.refcount),
            "lease_set": [],
            "generation": None,
            "owner": None,
            "resume_required": None,
            "owner_marker_exists": self.owner.exists(),
            "lock_exists": self.lock.exists(),
            "lock_bytes": self.lock.stat().st_size if self.lock.exists() else None,
        }
        payload = _read_json(self.refcount)
        if isinstance(payload, dict):
            entries = payload.get("entries") or []
            snapshot["lease_set"] = sorted(
                str(e.get("lease_id")) for e in entries if isinstance(e, dict)
            )
            snapshot["generation"] = payload.get("generation")
            snapshot["owner"] = payload.get("owner")
            snapshot["resume_required"] = bool((payload.get("resume") or {}).get("required"))
        protocol_events = []
        try:
            for line in self.protocol_journal.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    protocol_events.append(json.loads(line))
        except (OSError, ValueError):
            pass
        lock_acquisitions = sum(
            1 for e in protocol_events if e.get("event") == "lease_lock_acquired"
        )
        max_lock_wait = max(
            [float(e.get("wait_seconds") or 0.0) for e in protocol_events if e.get("event") == "lease_lock_acquired"]
            or [0.0]
        )
        summary = {
            "case": self.name,
            "dir": str(self.dir),
            "root": str(self.root),
            "participants": self.meta,
            "reports": {tag: self.report(tag) for tag in self.procs},
            "worker": worker,
            "pause_calls": worker["counts"]["worker-pause"],
            "resume_calls": worker["counts"]["worker-resume"],
            "status_calls": worker["counts"]["worker-status"],
            "final_worker_state": final_state,
            "final_lease": snapshot,
            "protocol_journal": protocol_events,
            "lock_acquisitions": lock_acquisitions,
            "max_lock_wait_seconds": round(max_lock_wait, 4),
            "phase_wall_seconds": round(
                max(
                    (m.get("elapsed_seconds") or 0.0) for m in self.meta.values() if isinstance(m, dict)
                )
                if self.meta
                else 0.0,
                4,
            ),
        }
        (self.dir / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=1), encoding="utf-8"
        )
        return summary


# ---------------------------------------------------------------------------
# cases
# ---------------------------------------------------------------------------


def case_f_l5(run: CaseRun) -> None:
    """Two real processes, two live leases in ONE ledger (card F-L5 + ADR-11).

    A is HELD ALIVE inside its scope (the harness keeps it there), so B's whole
    register-then-pause sequence happens while A's lease is still in the ledger: at the
    moment the scheduler reads it, both leases are live.  A then leaves first; because
    A is the cycle's owner and B is still live, ADR-10e transfers ownership to B and A
    must NOT resume the worker.  B resumes when it leaves.  That is exactly the
    sequence the legacy prune-then-write could not produce - it deleted every same-pid
    entry and unlinked the owner marker, so the worker was woken under a live lease.
    """
    a_release = run.dir / "hold.A.release"
    run.spawn("A", resume_wait=0.2, graceful=0.2, hold_for=str(a_release))
    assert run.wait_snapshot("A"), "A never reached the scope body"
    run.meta["a_holding"] = {"lease": run.summarise()["final_lease"]}
    run.spawn("B", resume_wait=0.2, graceful=0.2)
    run.reap("B")
    run.meta["after_b_exit"] = {"lease": run.summarise()["final_lease"]}
    a_release.write_text("go", encoding="utf-8")
    run.reap("A")


def case_f_l6(run: CaseRun) -> None:
    """Three sequential cycles: each one pauses and resumes exactly once (F-L6 base)."""
    for tag in ("A", "B", "C"):
        run.spawn(tag, resume_wait=0.2, graceful=0.2)
        run.reap(tag)


def case_f_l6b(run: CaseRun) -> None:
    """A leaves while B holds a live lease, then B leaves last (F-L6 + ADR-10e).

    A's release is NOT gated, so both participants run their release concurrently:
    the OS lock is the only thing ordering them.  Exactly ONE resume may occur, and
    it must come from B - an implementation that resumed whenever the ledger looked
    empty would produce two.
    """
    run.spawn("A", hooks="gate:enter-complete@A", resume_wait=0.2, graceful=0.2)
    assert run.wait_reached("enter-complete", "A"), "A never finished its enter critical section"
    # B is held out of the critical section while A pauses; B's own enter parks at
    # enter-complete with its lease already persisted, so both leases coexist.
    run.spawn("B", hooks="gate:enter-complete@B,gate:release-read@B", resume_wait=0.2, graceful=0.2)
    run.release("enter-complete", "A")
    assert run.wait_reached("enter-complete", "B"), "B never finished its enter critical section"
    # B is parked with its lease durable while A is ALSO still inside its own scope, so
    # this snapshot is the overlap the case is about.
    run.meta["b_joined"] = {"lease": run.summarise()["final_lease"]}
    run.release("enter-complete", "B")
    run.reap("A")
    run.meta["after_a_exit"] = {"lease": run.summarise()["final_lease"]}
    assert run.wait_reached("release-read", "B"), "B never reached its release critical section"
    run.release("release-read", "B")
    run.reap("B")


def case_f_l7(run: CaseRun) -> None:
    """Same-pid nesting: the inner release must remove exactly its own lease (F-L7)."""
    run.spawn("nest", nested="outer-then-inner")
    run.reap("nest")


def case_f_l7b(run: CaseRun) -> None:
    """Same participant, nested scopes, inner exits while outer stays (F-L7)."""
    run.spawn("nest", nested="inner-exits-first")
    run.reap("nest")


def case_f_l7c(run: CaseRun) -> None:
    """Same PID, two scopes, the OUTER scope's lease removed first is impossible;
    this variant pins the resume counter after both scopes closed."""
    run.spawn("nest", nested="sequential-pair")
    run.reap("nest")


def case_f_l9a(run: CaseRun) -> None:
    """Initial user pause: zero writes, zero worker commands (F-L9b)."""
    run.state.write_text(
        json.dumps({"desired_state": "paused", "runtime_state": "stopped"}), encoding="utf-8"
    )
    run.spawn("user")
    run.reap("user")


def case_f_l9c(run: CaseRun) -> None:
    """A user pause DURING our scope, in its DISTINGUISHABLE form (F-L9c).

    A human running ``worker-pause`` only flips ``desired_state`` on the wiki side,
    which our ledger cannot see - that is the I-04-C section 8 O-2 limitation, and it
    is registered as a cross-repo dependency rather than papered over here.  The
    DISTINGUISHABLE form is the one where the user's action also invalidates our
    ownership evidence: the operator pauses the worker and removes the ownership
    record our marker backed (W7/T10).  The tool must then NOT resume the user's
    pause, must not fabricate new ownership evidence, and must say so.

    A parks in the SCOPE BODY until the signal file appears, so the ledger is edited
    between A's enter and A's release without instrumenting either.
    """
    signal = run.dir / "signal.edit"
    run.spawn(
        "A",
        resume_wait=0.2,
        graceful=0.2,
        wait_for=str(signal),
    )
    assert run.wait_snapshot("A"), "A never reached the scope body"
    payload = _read_json(run.refcount)
    if not isinstance(payload, dict):
        raise AssertionError(
            "refcount is not an object: "
            f"{payload!r}; catalog listing="
            f"{sorted(x.name for x in run.catalog.iterdir())!r}"
        )
    run.meta["live_ledger"] = {
        "sha256": _sha256(run.refcount),
        "lease_set": sorted(
            str(e.get("lease_id")) for e in payload.get("entries") or [] if isinstance(e, dict)
        ),
        "owner_record": payload.get("owner"),
        "worker_state": _read_json(run.state),
    }
    run.state.write_text(
        json.dumps({"desired_state": "paused", "runtime_state": "stopped"}), encoding="utf-8"
    )
    if run.owner.exists():
        run.owner.unlink()
    # Rewrite ONLY the owner field: schema, generation, entries and the resume
    # obligation stay exactly as the code under test wrote them, so this case tests an
    # ownership-evidence change rather than a hand-made ledger.
    payload["owner"] = None
    run.refcount.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    run.meta["user_action"] = {
        "owner_marker_removed": not run.owner.exists(),
        "owner_record": payload.get("owner"),
        "sha256": _sha256(run.refcount),
        "worker_state": _read_json(run.state),
    }
    signal.write_text("edit", encoding="utf-8")
    run.reap("A")
    run.meta["after"] = {
        "sha256": _sha256(run.refcount) if run.refcount.is_file() else "<absent>",
        "payload": _read_json(run.refcount),
        "worker_state": _read_json(run.state),
        "owner_marker_exists": run.owner.exists(),
    }


def case_f_l8d(run: CaseRun) -> None:
    """The owner evidence is rewritten under us: R5 fails closed (F-L8d).

    A third party replaces the ownership record while A is parked in the scope body,
    i.e. after A's lease is durable and before A releases.  The third party is a pid
    that does NOT exist, so its record is neither attributable nor resumable: the
    release must keep it byte-for-byte instead of taking the cycle over - taking it
    over would resume a pause this tool never created (a user's, in the worst case).
    """
    signal = run.dir / "signal.edit"
    run.spawn(
        "A",
        resume_wait=0.2,
        graceful=0.2,
        wait_for=str(signal),
    )
    assert run.wait_snapshot("A"), "A never reached the scope body"
    payload = _read_json(run.refcount)
    if not isinstance(payload, dict):
        raise AssertionError(
            "refcount is not an object: "
            f"{payload!r}; catalog listing="
            f"{sorted(x.name for x in run.catalog.iterdir())!r}"
        )
    payload["owner"] = THIRD_PARTY_OWNER
    run.refcount.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    run.meta["owner_rewrite"] = {
        "sha256": _sha256(run.refcount),
        "owner": payload["owner"],
        "lease_set": sorted(
            str(e.get("lease_id")) for e in payload.get("entries") or [] if isinstance(e, dict)
        ),
        "worker_state": _read_json(run.state),
    }
    signal.write_text("edit", encoding="utf-8")
    run.reap("A")
    run.meta["after"] = {
        "sha256": _sha256(run.refcount) if run.refcount.is_file() else "<absent>",
        "payload": _read_json(run.refcount),
        "worker_state": _read_json(run.state),
    }


def case_f_l8a_w1(run: CaseRun) -> None:
    """Crash between the refcount write and the owner marker (W1 / RC-3)."""
    run.spawn("A", hooks="crash:after-refcount-before-owner:90")
    run.reap("A")
    run.meta["crash_after"] = {
        "refcount_sha256": _sha256(run.refcount),
        "owner_marker_exists": run.owner.exists(),
        "lease_set": (run.summarise()["final_lease"]["lease_set"]),
        "worker_state": _read_json(run.state),
    }
    run.spawn("B")
    run.reap("B")


def case_f_l8a_w1b(run: CaseRun) -> None:
    """W1 crash, then a THIRD participant rejoins the recovered cycle.

    A is gone (its pid is dead), B reclaimed A's orphan lease and owns the cycle.  B is
    parked inside its RELEASE critical section, so the worker is paused and B's lease is
    in the ledger for the whole of C's visit: C therefore joins a live cycle (R1) rather
    than opening its own, and B - the last leaver - is the one that restores the worker.
    """
    run.spawn("A", hooks="crash:after-refcount-before-owner:90")
    run.reap("A")
    run.spawn("B", hooks="gate:release-read@B", resume_wait=0.2, graceful=0.2)
    assert run.wait_reached("release-read", "B"), "B never reached its release critical section"
    run.meta["b_state"] = {
        "lease": run.summarise()["final_lease"],
        "worker_state": _read_json(run.state),
    }
    # B holds the lock here, so C cannot misread the cycle as ended.
    run.spawn("C", hooks="gate:enter-complete@C", resume_wait=0.2, graceful=0.2)
    run.release("release-read", "B")
    assert run.wait_reached("enter-complete", "C"), "C never finished its enter"
    run.release("enter-complete", "C")
    run.meta["c_joined"] = {"lease": run.summarise()["final_lease"]}
    run.reap("C")
    run.meta["after_c_exit"] = {"lease": run.summarise()["final_lease"]}
    run.reap("B")


def case_f_l8b_w2(run: CaseRun) -> None:
    """Crash after the pause is confirmed, before any release (W2 / W3)."""
    run.spawn("A", hooks="crash:after-pause-confirm:91")
    run.reap("A")
    run.meta["crash_after"] = {
        "refcount_sha256": _sha256(run.refcount),
        "owner_marker_exists": run.owner.exists(),
        "worker_state": _read_json(run.state),
    }
    run.spawn("B")
    run.reap("B")


def case_f_l8c_w4(run: CaseRun) -> None:
    """Crash after the obligation is persisted, before the resume (W4)."""
    run.spawn("A", hooks="crash:after-release-persist-before-resume:92")
    run.reap("A")
    run.meta["crash_after"] = {
        "refcount_sha256": _sha256(run.refcount),
        "worker_state": _read_json(run.state),
        "lease": run.summarise()["final_lease"],
    }
    run.spawn("B")
    run.reap("B")


def case_f_l8h_writefail(run: CaseRun) -> None:
    """A lease write that cannot succeed must never be reported as ownership.

    The refcount path is pre-created as a DIRECTORY, so ``os.replace`` of the temp
    file onto it fails for a real OS reason (no hook, no monkeypatch).  A process
    that cannot persist its lease must fail loudly instead of pretending to own the
    first lease - that pretence is how the legacy code lost an owner while still
    acting like one, and it is the failure the card calls out explicitly.
    """
    run.refcount.mkdir(parents=True, exist_ok=True)
    run.meta["precondition"] = {"refcount_is_directory": run.refcount.is_dir()}
    run.spawn("A")
    run.reap("A")
    run.meta["after"] = {
        "refcount_still_directory": run.refcount.is_dir(),
        "owner_marker_exists": run.owner.exists(),
        "worker_state": _read_json(run.state),
    }


def case_f_l8g_unknown(run: CaseRun) -> None:
    """A liveness probe that CANNOT answer is UNKNOWN, never "dead" (ADR-4 rule 5).

    The ledger carries one live peer (the scheduler's own pid, which is demonstrably
    alive) and that peer's probe is forced to fail.  The request must then fail closed:
    no lease written, no worker command, and not one byte of the ledger changed.  A
    run that reclaimed the entry instead would resume or re-pause over a holder it
    never proved dead.
    """
    run.refcount.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "filing-fetch.pause-refcount/2",
        "generation": 1,
        "resume": {"required": False, "generation": 1, "lease_id": "", "phase": "idle"},
        "entries": [
            {
                "lease_id": "synthetic-probe-fails",
                "pid": os.getpid(),
                "os_start_time": "1",
                "boot_uuid": "000000000000",
                "invocations": 1,
                "joined": False,
            }
        ],
        "owner": {
            "lease_id": "synthetic-probe-fails",
            "generation": 1,
            "pid": os.getpid(),
            "boot_uuid": "000000000000",
            "os_start_time": "1",
        },
    }
    run.refcount.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")
    run.meta["injected"] = {
        "pid": os.getpid(),
        "sha256": _sha256(run.refcount),
        "worker_state": _read_json(run.state),
    }
    run.spawn(
        "prober",
        resume_wait=0.2,
        graceful=0.2,
        extra_env={"I04D_PROBE_INJECT": json.dumps({os.getpid(): "unknown"})},
    )
    run.reap("prober")
    run.meta["after"] = {
        "sha256": _sha256(run.refcount),
        "worker_state": _read_json(run.state),
        "payload": _read_json(run.refcount),
    }


def case_f_lk_timeout(run: CaseRun) -> None:
    """An external process really holds the lock: the lease fails closed."""
    holder = subprocess.Popen(  # noqa: S603
        [
            PYTHON,
            "-X",
            "utf8",
            "-B",
            "-c",
            (
                "import msvcrt,sys,time,os;"
                "p=sys.argv[1];"
                "h=os.open(p, os.O_RDWR|os.O_CREAT);"
                "msvcrt.locking(h, msvcrt.LK_NBLCK, 1);"
                "sys.stdout.write('locked\\n'); sys.stdout.flush();"
                "time.sleep(float(sys.argv[2]))"
            ),
            str(run.lock),
            "6",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    run.lock.parent.mkdir(parents=True, exist_ok=True)
    line = holder.stdout.readline()
    run.meta["lock_holder"] = {"pid": holder.pid, "said": line.strip()}
    try:
        run.spawn("A", request_budget=0.2)
        run.reap("A")
    finally:
        holder.kill()
        holder.wait(timeout=10)


def case_f_lk_timeout_zero(run: CaseRun) -> None:
    """A non-positive budget must not even attempt to take the lock (<I-04-A D3>)."""
    run.spawn("A", request_budget=0.0)
    run.reap("A")


def case_f_lk_holder_crash(run: CaseRun) -> None:
    """A holder that dies releases the lock in the kernel: no cleanup step exists."""
    run.lock.parent.mkdir(parents=True, exist_ok=True)
    holder = subprocess.Popen(  # noqa: S603
        [
            PYTHON,
            "-X",
            "utf8",
            "-B",
            "-c",
            (
                "import msvcrt,sys,time,os;"
                "p=sys.argv[1];"
                "h=os.open(p, os.O_RDWR|os.O_CREAT);"
                "msvcrt.locking(h, msvcrt.LK_NBLCK, 1);"
                "sys.stdout.write('locked\\n'); sys.stdout.flush();"
                "time.sleep(1.0); os._exit(90)"
            ),
            str(run.lock),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    said = holder.stdout.readline().strip()
    run.meta["lock_holder"] = {"pid": holder.pid, "said": said}
    holder.wait(timeout=20)
    run.meta["lock_holder"]["exit_code"] = holder.returncode
    # the holder is gone; take the lock for real and measure how long it takes
    probe = subprocess.run(  # noqa: S603
        [
            PYTHON,
            "-X",
            "utf8",
            "-B",
            "-c",
            (
                "import msvcrt,sys,os,time;"
                "p=sys.argv[1];"
                "h=os.open(p, os.O_RDWR|os.O_CREAT);"
                "t=time.monotonic();"
                "msvcrt.locking(h, msvcrt.LK_NBLCK, 1);"
                "print('%.4f' % (time.monotonic()-t))"
            ),
            str(run.lock),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    run.meta["reacquire"] = {
        "stdout": probe.stdout.strip(),
        "returncode": probe.returncode,
        "lock_bytes": run.lock.stat().st_size if run.lock.exists() else None,
    }


def case_f_lk_never_unlink(run: CaseRun) -> None:
    """The lock file must survive a full cycle (ADR-1: never unlinked)."""
    run.spawn("A")
    run.reap("A")
    run.meta["lock_exists_after"] = run.lock.exists()
    run.meta["lock_bytes_after"] = run.lock.stat().st_size if run.lock.exists() else None
    run.spawn("B")
    run.reap("B")


CASES = {
    "I04D-CASE-F-L5": case_f_l5,
    "I04D-CASE-F-L6": case_f_l6,
    "I04D-CASE-F-L6b": case_f_l6b,
    "I04D-CASE-F-L7": case_f_l7,
    "I04D-CASE-F-L7b": case_f_l7b,
    "I04D-CASE-F-L7c": case_f_l7c,
    "I04D-CASE-F-L9a": case_f_l9a,
    "I04D-CASE-F-L9c": case_f_l9c,
    "I04D-CASE-F-L8d": case_f_l8d,
    "I04D-CASE-F-L8a-W1": case_f_l8a_w1,
    "I04D-CASE-F-L8a-W1b": case_f_l8a_w1b,
    "I04D-CASE-F-L8b-W2": case_f_l8b_w2,
    "I04D-CASE-F-L8c-W4": case_f_l8c_w4,
    "I04D-CASE-F-L8h-WRITEFAIL": case_f_l8h_writefail,
    "I04D-CASE-F-L8g-UNKNOWN": case_f_l8g_unknown,
    "I04D-CASE-F-LK-TIMEOUT": case_f_lk_timeout,
    "I04D-CASE-F-LK-TIMEOUT-ZERO": case_f_lk_timeout_zero,
    "I04D-CASE-F-LK-HOLDER-CRASH": case_f_lk_holder_crash,
    "I04D-CASE-F-LK-NEVER-UNLINK": case_f_lk_never_unlink,
}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["list", "run"])
    parser.add_argument("cases", nargs="*")
    parser.add_argument("--out", default="")
    args = parser.parse_args(argv[1:])
    if args.action == "list":
        for name in CASES:
            print(name)
        return 0
    if not args.out:
        print("--out is required for run")
        return 2
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    names = args.cases or list(CASES)
    failures = []
    for name in names:
        if name not in CASES:
            print(f"UNKNOWN CASE {name}")
            failures.append(name)
            continue
        started = time.monotonic()
        run = CaseRun(name, out)
        try:
            CASES[name](run)
        except Exception as exc:  # noqa: BLE001 - a harness error is not a pass
            run.meta["harness_error"] = f"{type(exc).__name__}: {exc}"
        summary = run.summarise()
        summary["harness_error"] = run.meta.get("harness_error", "")
        summary["case_wall_seconds"] = round(time.monotonic() - started, 4)
        (run.dir / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=1), encoding="utf-8"
        )
        print(
            json.dumps(
                {
                    "case": name,
                    "wall": summary["case_wall_seconds"],
                    "harness_error": summary["harness_error"],
                    "pause_calls": summary["pause_calls"],
                    "resume_calls": summary["resume_calls"],
                    "exits": {
                        tag: meta.get("exit_code") for tag, meta in summary["participants"].items()
                        if isinstance(meta, dict) and "exit_code" in meta
                    },
                },
                sort_keys=True,
            ),
            flush=True,
        )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
