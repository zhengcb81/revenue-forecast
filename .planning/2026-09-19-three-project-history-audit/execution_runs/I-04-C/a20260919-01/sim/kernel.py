"""I-04-C simulation kernel.

Two implementations live here:

  mode="protocol"  -- the FROZEN protocol proposed by decision.md (OS byte-range
                      lease lock, lease_id-only removal, generation + persisted
                      resume obligation, resume inside the release critical
                      section, fail closed on unknown/corrupt/legacy).
  mode="legacy"    -- a faithful port of the CURRENT production machinery
                      (fetch_filing.py L409-610: read/prune/append/write with no
                      lock, pid-wide delete on release, unlink(owner) then resume).
                      It exists ONLY to produce the RED / counterexample evidence
                      for F-L1 (lost update) and the crash windows.

Nothing here is product code. No production repo is imported or written.
The worker CLI is a stub (sim/stub_worker.py) driving a JSON file; the liveness
probe answers are injected per participant through the payload, so every run is
deterministic and no real process is inspected or killed.

Scheduling gates: payload["wait_for"] maps a gate name to an absolute path; the
participant blocks (bounded) until that file exists. Gates are honoured at
"enter", "release" (inside the release critical section) and "resume" (before
the resume subcall). payload["gates"] additionally maps an arbitrary label to a
path; the label is then written as a gate file the scheduler may wait on.

Usage:  <python> sim/kernel.py <base64-json-payload>
Payload keys are documented in sim/scheduler.py (build_payload).
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import time
import uuid

SCHEMA_V2 = "filing-fetch.pause-refcount/2"
REFCOUNT_NAME = "filing_fetch_pause.refcount"
OWNER_NAME = "filing_fetch_pause.owner"
LOCK_NAME = "filing_fetch_pause.lock"
JOURNAL_LOCK_NAME = "filing_fetch_pause.journal.lock"
OWNER_MARKER = "filing-fetch"

LOCK_POLL_SECONDS = 0.02
LOCK_MAX_SECONDS = 60.0
PROBE_MAX_SECONDS = 5.0
GATE_MAX_SECONDS = 20.0

BOOT_UUID = uuid.uuid4().hex[:12]


class ScopeError(Exception):
    def __init__(self, code, message):
        super().__init__(f"{code}: {message}")
        self.code = code


def decode_b64(payload, key):
    raw = payload.get(key)
    if not raw:
        return None
    return json.loads(base64.b64decode(raw).decode("utf-8"))


def _payload_b64(payload):
    return base64.b64encode(json.dumps(payload, sort_keys=True).encode("utf-8")).decode("ascii")


# --------------------------------------------------------------------------
# tiny OS file lock (real, cross-process; also used for the stress test)
# --------------------------------------------------------------------------


class FileLock:
    def __init__(self, path, budget, poll=LOCK_POLL_SECONDS, payload=None, name="lock",
                 code="lock_timeout"):
        self.path = path
        self.budget = max(0.0, float(budget))
        self.poll = poll
        self.handle = None
        self.waited = 0.0
        self.payload = payload
        self.name = name
        # r3 F-I04C-11: the error CODE is a parameter.  The lease lock reports
        # `lease_lock_timeout` (the code the frozen decision/oracle text uses and
        # the one the request-phase action mapping knows); the journal lock keeps
        # the generic `lock_timeout`.  Before r3 the lease lock raised the generic
        # code, so the documented timeout never appeared in any envelope.
        self.code = code

    def _try(self):
        if os.name == "nt":
            import msvcrt

            try:
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
                return True
            except OSError:
                return False
        import fcntl

        try:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def acquire(self):
        start = time.monotonic()
        self.handle = open(self.path, "a+b")
        while True:
            if self._try():
                self.waited = time.monotonic() - start
                if self.payload is not None:
                    journal(self.payload, {"event": "lock_acq", "name": self.name,
                                           "waited": round(self.waited, 6)})
                return self
            if time.monotonic() - start >= self.budget:
                self.handle.close()
                self.handle = None
                if self.payload is not None:
                    journal(self.payload, {"event": "lock_timeout", "name": self.name,
                                           "code": self.code, "budget": self.budget})
                raise ScopeError(
                    self.code,
                    f"lock {os.path.basename(self.path)} wait > {self.budget}s",
                )
            time.sleep(self.poll)

    def release(self):
        if self.handle is None:
            return
        if self.payload is not None:
            journal(self.payload, {"event": "lock_rel", "name": self.name})
        if os.name == "nt":
            import msvcrt

            try:
                self.handle.seek(0)
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_UNLCK, 1)
            except OSError:
                pass
        else:
            import fcntl

            try:
                fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
        self.handle.close()
        self.handle = None

    def __enter__(self):
        return self.acquire()

    def __exit__(self, *_exc):
        self.release()
        return False


# --------------------------------------------------------------------------
# state helpers
# --------------------------------------------------------------------------


def refcount_path(payload):
    return os.path.join(payload["base"], REFCOUNT_NAME)


def owner_path(payload):
    return os.path.join(payload["base"], OWNER_NAME)


def lock_path(payload):
    return os.path.join(payload["base"], LOCK_NAME)


def unlink_quiet(path):
    try:
        if os.path.exists(path):
            os.unlink(path)
    except OSError:
        pass


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise ScopeError("lease_state_corrupt", f"cannot read {path}: {exc}")


def write_atomic(payload, path, text, tmp_tag):
    tag = payload.get("tag") or "x"
    tmp = f"{path}.{tag}.{os.getpid()}.{tmp_tag}.tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(text)
    os.replace(tmp, path)


def lock_budget_for(phase_budget):
    """ADR-2 (v2, measured): the lock wait is the phase budget itself, capped.

    v1 froze a flat 10 s cap, and the contention simulation showed it failing the
    whole request once the queue of participants exceeds ~6 (each critical section
    runs a worker-status child process).  A wait can never usefully outlive the
    phase it belongs to, so the budget IS the phase budget, capped at 60 s; the
    request-phase budget has no floor (I-04-A D3), so a deadline that has already
    passed still yields zero and the acquisition is refused.
    """
    return max(0.0, min(float(phase_budget), LOCK_MAX_SECONDS))


def lease_lock(payload, budget):
    """The ONE lease critical-section lock.

    r3 F-I04C-11: it raises `lease_lock_timeout` (the code the frozen text uses).
    """
    return FileLock(lock_path(payload), budget, payload=payload, name="lease",
                    code="lease_lock_timeout")


def journal(payload, event):
    event = dict(event)
    event.setdefault("pid", os.getpid())
    event.setdefault("tag", payload.get("tag"))
    event.setdefault("monotonic", round(time.monotonic(), 6))
    line = json.dumps(event, ensure_ascii=True, sort_keys=True)
    lock = FileLock(os.path.join(payload["base"], JOURNAL_LOCK_NAME), 10.0)
    try:
        lock.acquire()
        with open(payload["journal"], "a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
    except (ScopeError, OSError):
        pass
    finally:
        lock.release()


def gate(payload, name):
    """Announce a reached label, then optionally wait for its unblock fence.

    The reached marker is written BOTH generically (``gate.<name>.reached``) and
    per participant (``gate.<name>.<tag>.reached``), because several participants
    can pass through the same gate and the scheduler must be able to wait for one
    specific participant (otherwise an earlier participant's marker satisfies the
    wait and the scheduler mistakes a blocked participant for a finished one).
    """
    markers = [os.path.join(payload["base"], f"gate.{name}.reached")]
    tag = payload.get("tag")
    if tag:
        markers.append(os.path.join(payload["base"], f"gate.{name}.{tag}.reached"))
    for marker in markers:
        with open(marker, "w", encoding="utf-8") as handle:
            handle.write("reached")
    target = (payload.get("wait_for") or {}).get(name)
    if not target:
        return
    deadline = time.monotonic() + GATE_MAX_SECONDS
    while not os.path.exists(target):
        if time.monotonic() >= deadline:
            journal(payload, {"event": "gate_timeout", "gate": name, "path": target})
            return
        time.sleep(0.01)


def maybe_exit_at(payload, point):
    """Hard-exit at a named window, after a best-effort journal line."""
    if payload.get("exit_at") != point:
        return False
    journal(payload, {"event": "crash", "point": point})
    sys.stdout.flush()
    os._exit(90)


def marker_present(payload):
    return os.path.isfile(owner_path(payload))


def read_lease(payload):
    """Read + validate. Unknown/corrupt/legacy => fail closed."""
    raw = read_text(refcount_path(payload))
    if raw is None or not raw.strip():
        return {"generation": 0, "entries": [], "resume": {"required": False}, "owner": {}}
    try:
        data = json.loads(raw)
    except ValueError as exc:
        raise ScopeError(
            "lease_state_corrupt",
            f"{REFCOUNT_NAME} is not valid JSON: {exc} (len={len(raw)})",
        )
    if isinstance(data, list):
        raise ScopeError(
            "lease_state_legacy",
            f"{REFCOUNT_NAME} holds a legacy list of {len(data)} entries",
        )
    if not isinstance(data, dict):
        raise ScopeError("lease_state_corrupt", f"{REFCOUNT_NAME} root is {type(data).__name__}")
    schema = data.get("schema")
    if schema != SCHEMA_V2:
        raise ScopeError("lease_state_corrupt", f"unsupported schema {schema!r}")
    entries = data.get("entries")
    if not isinstance(entries, list):
        raise ScopeError("lease_state_corrupt", "entries is not a list")
    cleaned = []
    for item in entries:
        if not isinstance(item, dict) or not isinstance(item.get("lease_id"), str):
            raise ScopeError("lease_state_corrupt", "entry without a string lease_id")
        cleaned.append(item)
    return {
        "generation": int(data.get("generation", 0) or 0),
        "entries": cleaned,
        "resume": data.get("resume") or {"required": False},
        "owner": data.get("owner") or {},
    }


def write_lease(payload, generation, entries, resume, owner, tmp_tag):
    body = {
        "schema": SCHEMA_V2,
        "generation": generation,
        "entries": entries,
        "resume": resume,
        "owner": owner,
        "updated_at": round(time.monotonic(), 6),
    }
    write_atomic(payload, refcount_path(payload), json.dumps(body, sort_keys=True), tmp_tag)


def os_liveness(pid):
    """Real OS liveness for a pid: True / False / None (cannot tell).

    Windows uses ``tasklist`` (a real subprocess, like the frozen
    ``_pid_is_alive``); POSIX uses ``os.kill(pid, 0)``.  ``None`` means the
    answer is UNKNOWN and the caller must fail closed.
    """
    if os.name == "nt":
        try:
            probe = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
                errors="replace",
                timeout=20,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        return str(pid) in (probe.stdout or "")
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except OSError:
        return None


def declared_liveness(payload, pid):
    """Injected liveness model: True / False / None.

    Every simulated invocation publishes ``alive.<pid>.<holder>.<tag>.json`` at
    launch and removes it on a clean return; a crashed one (os._exit) leaves the
    file behind.  The lease is a HOLDER (one participant, which may span an enter
    and an exit invocation with the same lease_id), so the holder is alive while
    any of its invocations is still running.  Declared simulation input -- see
    oracle.md section 8; it replaces the real OS probe, which cannot model
    "scheduler calls the release step later".
    """
    if not payload.get("declared_liveness"):
        return None
    base = payload["base"]
    if not os.path.isdir(base):
        return None
    matches = []
    for name in os.listdir(base):
        if not name.startswith(f"alive.{pid}.") or not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(base, name), "r", encoding="utf-8") as handle:
                recorded = json.load(handle)
        except (OSError, ValueError):
            continue
        matches.append(recorded)
    if not matches:
        return None
    # The holder is alive exactly while one of its invocations is running; a
    # crashed invocation leaves its file behind, but the OS then says the pid is
    # gone, which wins.
    if not any(bool(item.get("alive")) for item in matches):
        return False
    if os_liveness(pid) is False:
        return False
    return True


def classify_pid(payload, pid, boot_uuid=None, recorded_start=None):
    """Same precedence as classify() but for a bare pid (owner evidence, r2)."""
    if pid == os.getpid() and (boot_uuid is None or boot_uuid == BOOT_UUID):
        return "alive"
    recorded = recorded_start or ""
    scripted = (decode_b64(payload, "probe_b64") or {}).get(str(pid))
    if scripted is not None:
        if scripted.get("error"):
            return "unknown"
        if scripted.get("alive") is False:
            return "dead"
        observed = scripted.get("start_time")
    else:
        live = declared_liveness(payload, pid)
        if live is None:
            live = os_liveness(pid)
        if live is False:
            return "dead"
        if live is None:
            return "unknown"
        observed = (payload.get("os_start_time_of") or {}).get(str(pid))
    if recorded and observed and str(recorded) != str(observed):
        return "pid_reuse"
    if recorded and not observed:
        return "unknown"
    return "alive"


def classify(payload, entry):
    """Return 'alive' | 'dead' | 'pid_reuse' | 'unknown' (unknown => fail closed).

    Order matters:
      1. our own incarnation is alive by definition (no probe needed);
      2. a SCRIPTED answer (synthetic pid) wins over everything else -- tests use
         it to model a dead holder or a pid-reuse collision;
      3. otherwise the DECLARED liveness model when the run enables it, then the
         REAL OS answer: dead => reclaimable, live => alive, cannot-tell =>
         unknown (fail closed).

    ``pid_reuse`` requires both a recorded and an observed creation time; a
    recorded time with no observable timer is UNKNOWN, never "alive enough".
    """
    if entry.get("pid") == os.getpid() and entry.get("boot_uuid") == BOOT_UUID:
        return "alive"
    return classify_pid(payload, entry.get("pid"), entry.get("boot_uuid"),
                        entry.get("os_start_time"))


def prune(payload, entries):
    kept, pruned = [], []
    for entry in entries:
        verdict = classify(payload, entry)
        if verdict == "alive":
            kept.append(entry)
        else:
            pruned.append({"lease_id": entry.get("lease_id"), "pid": entry.get("pid"),
                           "reason": verdict})
    return kept, pruned


def entry(payload, invocations=1):
    return {
        "pid": os.getpid(),
        "boot_uuid": BOOT_UUID,
        "os_start_time": str(payload.get("fake_start_time") or ""),
        "lease_id": payload["lease_id"],
        "invocations": invocations,
    }


def read_view(payload):
    """Best-effort snapshot for the result envelope (never raises)."""
    try:
        state = read_lease(payload)
        return {
            "lease_set": sorted(e.get("lease_id") for e in state["entries"]),
            "generation": state["generation"],
            "owner_lease": (state.get("owner") or {}).get("lease_id"),
            "resume_required": bool((state.get("resume") or {}).get("required")),
        }
    except ScopeError as exc:
        return {"lease_set": ["<unreadable>"], "generation": None,
                "owner_lease": None, "resume_required": None, "state_error": exc.code}


# --------------------------------------------------------------------------
# stub company-wiki client
# --------------------------------------------------------------------------


class Client:
    """Calls the STUB company-wiki worker CLI as a real child process.

    The stub only mutates a JSON state file inside the attempt directory; every
    pause/resume therefore shows up exactly once in the worker's action log,
    which is what the oracle counts.
    """

    def __init__(self, payload):
        self.payload = payload
        self.pause_calls = 0
        self.resume_calls = 0
        self.stub = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stub_worker.py")

    def _cli(self, subcommand):
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        return subprocess.run(
            [sys.executable, "-B", self.stub, _payload_b64(self.payload), subcommand],
            cwd=self.payload["base"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
        )

    def probe(self, name):
        answers = decode_b64(self.payload, "probe_b64") or {}
        entry = answers.get(name)
        if entry is None:
            raise ScopeError("probe_missing", f"no scripted answer for {name}")
        if entry.get("error"):
            raise ScopeError("worker_status_failed", entry["error"])
        return entry

    def worker_status(self):
        answer = decode_b64(self.payload, "status_b64")
        if answer is not None and answer.get("error"):
            raise ScopeError("worker_status_failed", answer["error"])
        proc = self._cli("worker-status")
        if proc.returncode != 0:
            raise ScopeError("worker_status_failed", (proc.stderr or "").strip())
        return json.loads(proc.stdout)

    def worker_pause(self):
        self.pause_calls += 1
        # r3: an injected per-pause cost makes the queue-crosses-budget boundary
        # deterministic.  The pause happens INSIDE the lease critical section, so
        # this value IS the "critical-section hold time" of the ADR-2 analysis.
        hold = float(self.payload.get("pause_hold_seconds", 0.0) or 0.0)
        if hold:
            time.sleep(hold)
        answers = decode_b64(self.payload, "probe_b64") or {}
        answer = answers.get("worker-pause")
        if answer is not None and answer.get("error"):
            raise ScopeError("worker_pause_failed", answer["error"])
        proc = self._cli("worker-pause")
        if proc.returncode != 0:
            raise ScopeError("worker_pause_failed", (proc.stderr or "").strip())
        return json.loads(proc.stdout)

    def worker_resume(self):
        self.resume_calls += 1
        delay = float(self.payload.get("resume_delay", 0.0) or 0.0)
        if delay:
            time.sleep(delay)
        budget = float(self.payload.get("resume_budget", 0.0) or 0.0)
        if budget and delay > budget:
            raise ScopeError("resume_timeout", f"resume exceeded budget {budget}s")
        err = decode_b64(self.payload, "resume_error_b64")
        if err:
            # Injected failure BEFORE the CLI call: the worker never sees it, but
            # the attempt is still counted (reported as attempted_resumes).
            raise ScopeError("resume_failed", err)
        proc = self._cli("worker-resume")
        if proc.returncode != 0:
            raise ScopeError("resume_refused", (proc.stderr or "").strip())
        return json.loads(proc.stdout)


# --------------------------------------------------------------------------
# protocol mode: acquire path (T0-T7)
#
# v1.2 (r2) structure: the WHOLE acquire path runs inside ONE lease critical
# section.  The worker status is read inside it (ADR-11), the lease is read
# inside it, the decision is taken on that same snapshot, and the mutation
# (prune / register / owner marker / pause) happens in the same hold.  There is
# no pre-lock read whose staleness could be used as a criterion (see
# run_protocol_stale_v1 for the deliberately wrong v1 shape that this replaces).
# --------------------------------------------------------------------------


def _owner_record(payload, generation):
    """Owner evidence: enough to decide later whether this pause is OURS.

    v1.2 adds pid/boot_uuid/os_start_time so a later participant can prove the
    owner is gone instead of having to guess from a lease_id alone (r2 F-I04C-01).
    """
    return {
        "lease_id": payload["lease_id"],
        "generation": generation,
        "pid": os.getpid(),
        "boot_uuid": BOOT_UUID,
        "os_start_time": str(payload.get("fake_start_time") or ""),
    }


def owner_resumable(payload, owner, pruned, kept):
    """May this participant resume a pause that the refcount says is ours?

    Returns (True/False, reason).  A pause is resumable ONLY on evidence:
      owner_is_me          -- the recorded owner lease is the caller's own;
      owner_alive_in_cycle -- the owner is a living lease in the same refcount;
      owner_pruned:<why>   -- the owner lease was reclaimed as dead/pid_reuse;
      owner_probe:<why>    -- the owner record carries a pid the probe says is gone.
    Anything else (foreign owner, owner record with no lease_id, unverifiable
    owner) is NOT resumable: the caller must fail closed and must not rewrite the
    owner evidence (r2 F-I04C-02; ADR-5 W7/T10, ADR-8).
    """
    lease = owner.get("lease_id") if isinstance(owner, dict) else None
    if not lease:
        return False, "owner_absent"
    if lease == payload["lease_id"]:
        return True, "owner_is_me"
    if any(e.get("lease_id") == lease for e in kept):
        return True, "owner_alive_in_cycle"
    if lease in pruned and pruned[lease] in {"dead", "pid_reuse"}:
        return True, f"owner_pruned:{pruned[lease]}"
    pid = owner.get("pid") if isinstance(owner, dict) else None
    if isinstance(pid, int):
        verdict = classify_pid(payload, pid, owner.get("boot_uuid"),
                               owner.get("os_start_time"))
        if verdict in {"dead", "pid_reuse"}:
            return True, f"owner_probe:{verdict}"
        if verdict == "unknown":
            return False, "owner_probe_unknown"
    return False, "owner_unproven"


def run_protocol(payload):
    client = Client(payload)
    out = {"mode": "protocol", "pid": os.getpid(), "lease_id": payload["lease_id"],
           "phase": "enter", "action": None, "pause_calls": 0, "resume_calls": 0,
           "cleanup_status": "not_needed", "writes": 0, "code": None, "error": None,
           "actions": []}
    try:
        if not payload.get("enabled", True):
            out["action"] = "disabled"
            return out

        request_budget = max(0.0, float(payload.get("request_budget", 100.0)))
        cleanup_budget = max(0.0, float(payload.get("cleanup_budget", 30.0)))
        lock_budget = lock_budget_for(request_budget)

        lock = lease_lock(payload, lock_budget)
        lock.acquire()
        out["lock_wait"] = round(lock.waited, 6)
        try:
            gate(payload, "enter_lock_held")
            try:
                status = client.worker_status()
            except ScopeError as exc:
                out["action"] = "no_status"
                out["note"] = str(exc)
                return out
            out["lock_status"] = status
            state = read_lease(payload)
            verdicts = [(e, classify(payload, e)) for e in state["entries"]]
            out.update(read_view(payload))
            if any(verdict == "unknown" for _, verdict in verdicts):
                # ADR-5 W6: an unverifiable participant is NEVER treated as gone,
                # and never silently joined with.
                out["action"] = "lease_conflict_unknown"
                out["code"] = "lease_conflict_unknown"
                out["error"] = json.dumps(
                    [{"lease_id": e.get("lease_id"), "pid": e.get("pid"), "verdict": v}
                     for e, v in verdicts if v == "unknown"])
                return out
            paused = status.get("desired_state") == "paused"
            has_state = bool(state["entries"]) or bool(
                (state["resume"] or {}).get("required")) or marker_present(payload)
            if paused or has_state:
                handled, _needs_fresh = protocol_paused_branch(
                    payload, client, out, status, state, verdicts, cleanup_budget)
                if handled:
                    return out
                _fresh_cycle_locked(payload, client, out, state, verdicts, recovering=True)
                return out
            if status.get("runtime_state") != "running":
                out["action"] = "worker_stopped"
                return out
            _fresh_cycle_locked(payload, client, out, state, verdicts, recovering=False)
            return out
        finally:
            lock.release()
    except ScopeError as exc:
        out["code"] = exc.code
        out["error"] = str(exc)
        out["action"] = {  # fail closed: no write, no CLI
            "lease_lock_timeout": "lease_lock_timeout",
            "lease_state_corrupt": "lease_state_corrupt",
            "lease_state_legacy": "lease_state_legacy",
        }.get(exc.code, "lease_fail_closed")
        out.update(read_view(payload))
        return out


def protocol_paused_branch(payload, client, out, status, state, verdicts, cleanup_budget):
    """The paused / tool-evidence branch.  Returns (handled, recovering).

    PRECONDITION (r2 F-I04C-07): the caller HOLDS the lease lock, and `status`,
    `state` and `verdicts` were all read inside that same hold.  This function
    must not take the lock and must not re-read the status.
    """
    kept, pruned_list = prune(payload, state["entries"])
    pruned = {p["lease_id"]: p["reason"] for p in pruned_list}
    if pruned_list:
        journal(payload, {"event": "pruned", "items": pruned_list})
    owner = state.get("owner") or {}
    marker = marker_present(payload)
    required = bool((state["resume"] or {}).get("required"))
    had_entries = bool(state["entries"])
    out["owner_verdict"] = owner_resumable(payload, owner, pruned, kept)[1]

    if required:
        return _takeover_cycle(payload, client, out, state, "recorded_obligation", status)

    if not kept:
        tool_evidence = marker or had_entries
        if not tool_evidence:
            # No lease, no marker, no obligation: this really is the user's pause.
            out["action"] = "respect_paused"
            return True, False
        resumable, why = owner_resumable(payload, owner, pruned, kept)
        if not resumable:
            # r2 F-I04C-02: never resume (nor rewrite) a pause we cannot attribute.
            out["action"] = "owner_evidence_foreign"
            out["code"] = "owner_evidence_foreign"
            out["cleanup_status"] = f"failed:owner_evidence_foreign:{why}"
            return True, False
        return _takeover_cycle(payload, client, out, state, why, status)

    resumable, why = owner_resumable(payload, owner, pruned, kept)
    if owner and not resumable:
        out["action"] = "owner_evidence_foreign"
        out["code"] = "owner_evidence_foreign"
        out["cleanup_status"] = f"failed:owner_evidence_foreign:{why}"
        return True, False
    if status.get("runtime_state") == "running":
        # ADR-9b: leases exist but the pause never landed.  Clear any stray pause,
        # keep the live leases and open one fresh cycle (still one pause per cycle).
        journal(payload, {"event": "stale_running_cycle",
                          "kept": [e.get("lease_id") for e in kept]})
        try:
            client.worker_resume()   # best effort; a no-op when already enabled
        except ScopeError as exc:
            journal(payload, {"event": "stale_resume_noop", "error": str(exc)})
        return False, True
    # join the running cycle
    kept = kept + [entry(payload, payload.get("invocations", 1))]
    if not marker:
        maybe_exit_at(payload, "after-refcount-before-owner")
        write_atomic(payload, owner_path(payload), OWNER_MARKER, "owner")
    write_lease(payload, state["generation"], kept, state["resume"], owner, "join")
    out["writes"] += 1
    out["action"] = "joined"
    out["actions"].append("joined")
    gate(payload, "enter_registered")
    return True, False


def _takeover_cycle(payload, client, out, state, why, status=None):
    """Close somebody else's dangling pause and open OUR cycle, under the lock.

    ADR-10d: a takeover is a COMPLETE cycle (resume, then our own pause), never a
    passive lease on a worker we just woke up.  If the worker is not actually
    paused there is nothing to restore, so the resume is skipped instead of being
    sent (and refused) for nothing.
    """
    generation = state["generation"]
    owner = _owner_record(payload, generation)
    mine = [entry(payload, payload.get("invocations", 1))]
    write_lease(payload, generation, mine,
                {"required": True, "generation": generation,
                 "lease_id": payload["lease_id"], "phase": f"takeover:{why}"},
                owner, "takeover")
    out["writes"] += 1
    out["takeover_reason"] = why
    paused = status is not None and status.get("desired_state") == "paused"
    if paused:
        maybe_exit_at(payload, "wm-takeover-before-resume")
        gate(payload, "takeover_before_resume")
        try:
            client.worker_resume()
        except ScopeError as exc:
            # Keep the obligation AND our lease so the next participant (or our own
            # release step) can finish the recovery honestly.
            out["resume_calls"] = client.resume_calls
            out["cleanup_status"] = f"failed:{exc.code}"
            out["code"] = "lease_resume_takeover_failed"
            out["error"] = str(exc)
            out["action"] = "takeover_failed"
            out["actions"].append("takeover_failed")
            out.update(read_view(payload))
            return True, False
        out["resume_calls"] = client.resume_calls
        out["actions"].append("takeover_resumed")
        out["action"] = "takeover_resumed"
    else:
        # Nothing to undo: the worker is already running, the dangling state was
        # only the refcount (ADR-5 W2).
        out["actions"].append("resume_skipped_worker_running")
    out["cleanup_status"] = "restored"
    # The pause is closed; now open OUR cycle in the same critical section.  The
    # state is re-read so the fresh cycle sees exactly what the takeover wrote.
    return _fresh_cycle_locked(payload, client, out, read_lease(payload), None,
                               recovering=False, keep=mine)


def _fresh_cycle_locked(payload, client, out, state, verdicts, recovering,
                        keep=None):
    """Open a fresh cycle while already holding the lock.

    Idempotent about our own entry so the takeover path can hand its lease over.
    """
    kept, pruned_list = prune(payload, state["entries"])
    if pruned_list:
        journal(payload, {"event": "pruned", "items": pruned_list})
    generation = int(state.get("generation", 0) or 0) + 1
    mine = keep if keep is not None else []
    entries = list(mine) + [e for e in kept
                            if e.get("lease_id") not in {m.get("lease_id") for m in mine}]
    if not any(e.get("lease_id") == payload["lease_id"] for e in entries):
        entries = entries + [entry(payload, payload.get("invocations", 1))]
    write_lease(payload, generation, entries, {"required": False},
                _owner_record(payload, generation), "fresh")
    out["writes"] += 1
    maybe_exit_at(payload, "after-refcount-before-owner")
    # Compat sentinel only; the refcount remains the authority (ADR-5 W1).
    write_atomic(payload, owner_path(payload), OWNER_MARKER, "owner")
    gate(payload, "before_pause")
    maybe_exit_at(payload, "after-owner-before-pause")
    error = None
    try:
        client.worker_pause()
    except ScopeError as exc:
        error = exc
    out["pause_calls"] = client.pause_calls
    out["generation"] = generation
    out.update(read_view(payload))
    if error is not None:
        out["action"] = "pause_failed"
        out["error"] = str(error)
        _withdraw_after_failed_pause(payload, client, out)
        return True, False
    out["action"] = "paused_by_us"
    out["actions"].append("paused_by_us")
    # The gate fires once our registration AND the pause we own are both on disk.
    gate(payload, "enter_registered")
    maybe_exit_at(payload, "after-pause-confirm")
    return True, False


def _withdraw_after_failed_pause(payload, client, out):
    """T7: withdraw our own lease (lock already held); resume only if last."""
    state = read_lease(payload)
    entries = [e for e in state["entries"] if e.get("lease_id") != payload["lease_id"]]
    owner = state.get("owner") or {}
    if entries:
        write_lease(payload, state["generation"], entries, state["resume"], owner, "pf")
        out["writes"] += 1
        out.update(read_view(payload))
        return
    resumable, why = owner_resumable(payload, owner, {}, entries)
    if not resumable:
        # Fail closed: remove our lease, keep the owner evidence untouched.
        write_lease(payload, state["generation"], [], {"required": False}, owner, "pf")
        out["writes"] += 1
        out["cleanup_status"] = f"failed:owner_evidence_foreign:{why}"
        out.update(read_view(payload))
        return
    write_lease(payload, state["generation"], [],
                {"required": True, "generation": state["generation"],
                 "lease_id": payload["lease_id"], "phase": "pause_failed"}, owner, "pf")
    out["writes"] += 1
    try:
        client.worker_resume()
    except ScopeError as exc:
        out["cleanup_status"] = f"failed:{exc.code}"
        out.update(read_view(payload))
        return
    out["cleanup_status"] = "restored"
    write_lease(payload, state["generation"], [], {"required": False}, {}, "pf")
    out["writes"] += 1
    unlink_quiet(refcount_path(payload))
    unlink_quiet(owner_path(payload))
    out.update(read_view(payload))


def run_protocol_stale_v1(payload):
    """DELIBERATELY WRONG (v1 shape): read the status BEFORE the lock and use that
    snapshot as the branch criterion.  Only used by the F-L2e pair to show what
    ADR-11 removes; never used by any other case.
    """
    client = Client(payload)
    out = {"mode": "protocol_stale_v1", "pid": os.getpid(),
           "lease_id": payload["lease_id"], "phase": "enter", "action": None,
           "pause_calls": 0, "resume_calls": 0, "cleanup_status": "not_needed",
           "writes": 0, "code": None, "error": None, "actions": []}
    request_budget = max(0.0, float(payload.get("request_budget", 100.0)))
    cleanup_budget = max(0.0, float(payload.get("cleanup_budget", 30.0)))
    lock_budget = lock_budget_for(request_budget)
    try:
        stale = client.worker_status()          # <-- outside the lock (the bug)
        out["prelock_status"] = stale
        gate(payload, "stale_prelock_read")
        lock = lease_lock(payload, lock_budget)
        lock.acquire()
        out["lock_wait"] = round(lock.waited, 6)
        try:
            gate(payload, "enter_lock_held")
            state = read_lease(payload)
            verdicts = [(e, classify(payload, e)) for e in state["entries"]]
            out.update(read_view(payload))
            if stale.get("desired_state") == "paused" or state["entries"]:
                handled, _recovering = protocol_paused_branch(
                    payload, client, out, stale, state, verdicts, cleanup_budget)
                if handled:
                    return out
                _fresh_cycle_locked(payload, client, out, state, verdicts, recovering=True)
                return out
            if stale.get("runtime_state") != "running":
                out["action"] = "worker_stopped"
                return out
            _fresh_cycle_locked(payload, client, out, state, verdicts, recovering=False)
            return out
        finally:
            lock.release()
    except ScopeError as exc:
        out["code"] = exc.code
        out["error"] = str(exc)
        out["action"] = "lease_fail_closed"
        out.update(read_view(payload))
        return out


# --------------------------------------------------------------------------
# protocol mode: release path (T8-T10) -- run by sim/participant.py
# --------------------------------------------------------------------------


def run_protocol_exit(payload):
    client = Client(payload)
    out = {"mode": "protocol", "pid": os.getpid(), "lease_id": payload["lease_id"],
           "phase": "exit", "action": None, "resume_calls": 0,
           "cleanup_status": "not_needed", "writes": 0, "code": None, "error": None,
           "actions": []}
    cleanup_budget = max(0.0, float(payload.get("cleanup_budget", 30.0)))
    try:
        with lease_lock(payload, lock_budget_for(cleanup_budget)) as held:
            out["lock_wait"] = round(held.waited, 6)
            gate(payload, "release_lock_held")
            gate(payload, "release_before_decision")
            state = read_lease(payload)
            entries = [e for e in state["entries"] if e.get("lease_id") != payload["lease_id"]]
            owner = state.get("owner") or {}
            generation = state["generation"]
            required = bool((state["resume"] or {}).get("required"))
            out["generation"] = generation
            out["owner_lease"] = owner.get("lease_id")
            out["lease_set"] = sorted(e.get("lease_id") for e in entries)
            if entries:
                # ADR-10e (r2): if WE are the recorded owner and we are leaving
                # while others stay, ownership must move to a surviving lease --
                # otherwise the owner record names a participant that is no longer
                # in the refcount, and the eventual last releaser would have to
                # guess (or fail closed) instead of resuming the cycle it owns.
                if owner.get("lease_id") == payload["lease_id"]:
                    successor = sorted(entries, key=lambda e: e.get("lease_id") or "")[0]
                    owner = {
                        "lease_id": successor.get("lease_id"),
                        "generation": generation,
                        "pid": successor.get("pid"),
                        "boot_uuid": successor.get("boot_uuid"),
                        "os_start_time": successor.get("os_start_time", ""),
                    }
                    out["ownership_transferred_to"] = owner["lease_id"]
                write_lease(payload, generation, entries, state["resume"], owner, "rel")
                out["writes"] += 1
                out["action"] = "released_joined"
                out["actions"].append("released_joined")
                out.update(read_view(payload))
                out["pause_calls"] = 0
                out["attempted_resumes"] = client.resume_calls
                return out
            # We emptied the refcount UNDER THE LOCK, so nothing can slip between
            # "empty" and the resume decision (ADR-3).  Whether we may CLOSE the
            # cycle is an evidence question (r2 F-I04C-01/02):
            pruned = {payload["lease_id"]: "self_release"}
            resumable, why = owner_resumable(payload, owner, pruned, entries)
            if required:
                reason = "inherited_obligation"
            elif owner.get("lease_id") == payload["lease_id"]:
                reason = "owner_is_me"
            elif resumable:
                reason = why
            else:
                reason = None
            out["resume_reason"] = reason
            if reason is None:
                # F-I04C-02: the recorded owner is foreign/unproven.  Remove our
                # own lease, keep the owner evidence EXACTLY as it was, never
                # claim the cycle and never resume (ADR-5 W7/T10, ADR-8).
                write_lease(payload, generation, [], {"required": False}, owner, "rel")
                out["writes"] += 1
                out["action"] = "released_owner_changed"
                out["actions"].append("released_owner_changed")
                out["cleanup_status"] = f"failed:owner_evidence_changed:{why}"
                out.update(read_view(payload))
                out["pause_calls"] = 0
                out["attempted_resumes"] = client.resume_calls
                return out
            # Persist the recovery obligation BEFORE acting on it (ADR-3).
            write_lease(payload, generation, [],
                        {"required": True, "generation": generation,
                         "lease_id": payload["lease_id"], "phase": f"resume_pending:{reason}"},
                        owner, "rel")
            out["writes"] += 1
            maybe_exit_at(payload, "wm-release-before-resume")
            gate(payload, "before_resume")
            try:
                client.worker_resume()
            except ScopeError as exc:
                out["resume_calls"] = client.resume_calls
                out["cleanup_status"] = f"failed:{exc.code}"
                out["action"] = "released_last_resume_failed"
                out["actions"].append("released_last_resume_failed")
                out["code"] = "lease_resume_failed"
                out["error"] = str(exc)
                out.update(read_view(payload))
                out["pause_calls"] = 0
                out["attempted_resumes"] = client.resume_calls
                return out
            out["resume_calls"] = client.resume_calls
            out["cleanup_status"] = "restored"
            out["action"] = "released_last"
            out["actions"].append("released_last")
            maybe_exit_at(payload, "wm-resume-crash")
            # Neutral residue, then remove the files: the next cycle starts at
            # generation 1 again (documented in decision.md ADR-12).
            write_lease(payload, generation, [], {"required": False}, {}, "rel")
            out["writes"] += 1
            unlink_quiet(refcount_path(payload))
            unlink_quiet(owner_path(payload))
            out.update(read_view(payload))
    except ScopeError as exc:
        out["code"] = exc.code
        out["error"] = str(exc)
        out["action"] = "release_fail_closed"
        out["cleanup_status"] = f"failed:{exc.code}"
    out["pause_calls"] = 0
    out["attempted_resumes"] = client.resume_calls
    return out
    client = Client(payload)

# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# legacy mode: faithful port of the current production machinery
# --------------------------------------------------------------------------


def legacy_read_entries(payload):
    raw = read_text(refcount_path(payload))
    try:
        data = json.loads(raw) if raw else []
    except (OSError, ValueError):
        return []
    if not isinstance(data, list):
        return []
    return [e for e in data if isinstance(e, dict) and isinstance(e.get("pid"), int)]


def legacy_write_entries(payload, entries):
    write_atomic(payload, refcount_path(payload), json.dumps(entries), "legacy")


def legacy_pid_alive(payload, pid):
    """Current code: unknown/failed probes count as alive (L419-431)."""
    live = os_liveness(pid)
    if live is None:
        scripted = (decode_b64(payload, "probe_b64") or {}).get(str(pid))
        if scripted is not None and not scripted.get("error"):
            return bool(scripted.get("alive"))
        return True
    return live


def legacy_prune(payload):
    return [e for e in legacy_read_entries(payload) if legacy_pid_alive(payload, e["pid"])]


def legacy_register(payload):
    entries = legacy_prune(payload)
    first = not entries
    entries.append({"pid": os.getpid(), "joined": bool(payload.get("joined", False))})
    journal(payload, {"event": "legacy_register", "first": first,
                      "entries": [e.get("pid") for e in entries]})
    # Frozen fence: exactly between the read/prune and the write, i.e. inside the
    # non-atomic read-modify-write of the current machinery (L566-L569).
    gate(payload, "racestop")
    legacy_write_entries(payload, entries)
    maybe_exit_at(payload, "after-refcount-before-owner")
    if first:
        write_atomic(payload, owner_path(payload), OWNER_MARKER, "owner")
    return first


def legacy_unregister(payload):
    entries = legacy_prune(payload)
    entries = [e for e in entries if e.get("pid") != os.getpid()]
    if not entries:
        unlink_quiet(refcount_path(payload))
        unlink_quiet(owner_path(payload))
    else:
        legacy_write_entries(payload, entries)
    journal(payload, {"event": "legacy_unregister", "empty": not entries})
    return not entries


def run_legacy(payload):
    client = Client(payload)
    out = {"mode": "legacy", "pid": os.getpid(), "lease_id": payload["lease_id"],
           "phase": "enter", "action": None, "pause_calls": 0, "resume_calls": 0,
           "writes": 0, "code": None, "error": None}
    request_budget = max(0.0, float(payload.get("request_budget", 100.0)))
    mutex = FileLock(lock_path(payload), min(LOCK_MAX_SECONDS, request_budget),
                     payload=payload, name="lease", code="lease_lock_timeout")
    use_lock = bool(payload.get("use_lock"))
    try:
        if not payload.get("enabled", True):
            out["action"] = "disabled"
            return out
        try:
            status = client.worker_status()
        except ScopeError as exc:
            out["action"] = "no_status"
            out["note"] = str(exc)
            return out
        if status.get("runtime_state") != "running":
            out["action"] = "worker_stopped"
            return out
        if status.get("desired_state") == "paused":
            if marker_present(payload):
                out["action"] = "joined"
                if use_lock:
                    mutex.acquire()
                try:
                    gate(payload, "enter_lock_held")
                    legacy_register(payload)
                finally:
                    if use_lock:
                        mutex.release()
            else:
                out["action"] = "respect_paused"
            return out
        if use_lock:
            mutex.acquire()
        try:
            gate(payload, "enter_lock_held")
            first = legacy_register(payload)
        finally:
            if use_lock:
                mutex.release()
        if first:
            try:
                client.worker_pause()
            except ScopeError as exc:
                out["action"] = "pause_failed"
                out["error"] = str(exc)
                if use_lock:
                    mutex.acquire()
                try:
                    if legacy_unregister(payload):
                        try:
                            client.worker_resume()
                        except ScopeError:
                            pass
                finally:
                    if use_lock:
                        mutex.release()
                out["pause_calls"] = client.pause_calls
                out["resume_calls"] = client.resume_calls
                return out
        out["pause_calls"] = client.pause_calls
        out["action"] = "paused_by_us"
        return out
    except ScopeError as exc:
        out["code"] = exc.code
        out["error"] = str(exc)
        out["action"] = "legacy_error"
        return out

def run_legacy_exit(payload):
    client = Client(payload)
    out = {"mode": "legacy", "pid": os.getpid(), "lease_id": payload["lease_id"],
           "phase": "exit", "action": None, "resume_calls": 0, "writes": 0}
    cleanup_budget = max(0.0, float(payload.get("cleanup_budget", 30.0)))
    mutex = lease_lock(payload, lock_budget_for(cleanup_budget))
    use_lock = bool(payload.get("use_lock"))
    if use_lock:
        mutex.acquire()
    try:
        gate(payload, "release_lock_held")
        empty = legacy_unregister(payload)
    finally:
        if use_lock:
            mutex.release()
    if not empty:
        out["action"] = "released_joined"
        return out
    out["action"] = "released_last"
    maybe_exit_at(payload, "wm-release-before-resume")
    gate(payload, "before_resume")
    try:
        client.worker_resume()
        out["resume_calls"] = client.resume_calls
        out["cleanup_status"] = "restored"
    except ScopeError as exc:
        out["resume_calls"] = client.resume_calls
        out["code"] = exc.code
        out["error"] = str(exc)
        out["cleanup_status"] = f"failed:{exc.code}"
    return out


# --------------------------------------------------------------------------


def main(argv):
    payload = json.loads(base64.b64decode(argv[1]).decode("utf-8"))
    os.makedirs(payload["base"], exist_ok=True)
    phase = payload.get("phase", "enter")
    mode = payload.get("mode", "protocol")
    if mode == "protocol":
        result = run_protocol(payload) if phase == "enter" else run_protocol_exit(payload)
    elif mode == "protocol_stale_v1":
        # deliberately wrong v1 shape, used only by the F-L2e pair
        result = (run_protocol_stale_v1(payload) if phase == "enter"
                  else run_protocol_exit(payload))
    else:
        result = run_legacy(payload) if phase == "enter" else run_legacy_exit(payload)
    result["tag"] = payload.get("tag")
    print("RESULT " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
