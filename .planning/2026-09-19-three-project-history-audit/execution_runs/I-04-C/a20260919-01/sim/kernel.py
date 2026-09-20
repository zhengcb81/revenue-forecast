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
    def __init__(self, path, budget, poll=LOCK_POLL_SECONDS, payload=None, name="lock"):
        self.path = path
        self.budget = max(0.0, float(budget))
        self.poll = poll
        self.handle = None
        self.waited = 0.0
        self.payload = payload
        self.name = name

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
                                           "budget": self.budget})
                raise ScopeError(
                    "lock_timeout", f"lock {os.path.basename(self.path)} wait > {self.budget}s"
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
    return FileLock(lock_path(payload), budget, payload=payload, name="lease")


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
    pid = entry.get("pid")
    recorded = entry.get("os_start_time") or ""
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
# --------------------------------------------------------------------------


def run_protocol(payload):
    client = Client(payload)
    out = {"mode": "protocol", "pid": os.getpid(), "lease_id": payload["lease_id"],
           "phase": "enter", "action": None, "pause_calls": 0, "resume_calls": 0,
           "cleanup_status": "not_needed", "writes": 0, "code": None, "error": None}
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

        request_budget = max(0.0, float(payload.get("request_budget", 100.0)))
        cleanup_budget = max(0.0, float(payload.get("cleanup_budget", 30.0)))
        lock_budget = lock_budget_for(request_budget)
        probe_budget = min(20.0, PROBE_MAX_SECONDS, request_budget)

        # ADR-11 (measured, this card): the first status read can be arbitrarily
        # stale -- another participant may pause between it and lock acquisition,
        # and acting on a stale "enabled/running" is exactly what produces a second
        # pause for one cycle.  Re-read the status and the lease INSIDE the critical
        # section and branch on that.
        lock = lease_lock(payload, lock_budget)
        lock.acquire()
        out["lock_wait"] = round(lock.waited, 6)
        try:
            gate(payload, "enter_lock_held")
            fresh = client.worker_status()
            state = read_lease(payload)
            verdicts = [(e, classify(payload, e)) for e in state["entries"]]
            out["lock_status"] = fresh
            out.update(read_view(payload))
        finally:
            lock.release()
        if any(verdict == "unknown" for _, verdict in verdicts):
            # ADR-5 W6: an unverifiable participant is NEVER treated as gone, and
            # never silently joined with.
            out["action"] = "lease_conflict_unknown"
            out["code"] = "lease_conflict_unknown"
            out["error"] = json.dumps(
                [{"lease_id": e.get("lease_id"), "pid": e.get("pid"), "verdict": v}
                 for e, v in verdicts if v == "unknown"])
            return out
        if fresh.get("desired_state") == "paused" or verdicts:
            # ADR-9: the paused branch is evaluated BEFORE the runtime_state guard.
            # Checking runtime_state first makes the join/takeover path unreachable
            # in production, because our own pause sets runtime_state=stopped
            # before anyone can join it.
            # ADR-9b: live leases also route here even when the status still says
            # enabled, so a cycle whose pause has not landed yet is joined or
            # recovered instead of starting a second pause.
            done, needs_fresh = protocol_paused_branch(
                payload, client, out, fresh, state, verdicts, lock_budget)
            if done:
                return out
        elif fresh.get("runtime_state") != "running":
            out["action"] = "worker_stopped"
            return out
        return protocol_fresh_cycle(payload, client, out, lock_budget, cleanup_budget)
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


def protocol_paused_branch(payload, client, out, status, state, verdicts, lock_budget):
    """The paused-worker branch.  Returns (handled, needs_fresh_cycle).

    The lease read and the status read both come from the ADR-11 critical section
    in run_protocol; this function only re-takes the lock to mutate.
    """
    lock = lease_lock(payload, lock_budget)
    lock.acquire()
    out["lock_wait"] = round(lock.waited, 6)
    try:
        gate(payload, "enter_paused_branch")
        # Reclaim dead leases FIRST and decide on what actually survives (ADR-9c):
        # deciding on the pre-prune list is what lets a participant "join" a cycle
        # whose only lease is dead -- and then walk away from a paused worker with
        # an empty refcount and nobody obliged to resume it.
        kept, pruned = prune(payload, state["entries"])
        if pruned:
            journal(payload, {"event": "pruned", "items": pruned})
        if (state["resume"] or {}).get("required"):
            action = "takeover_resume"
        elif not kept and marker_present(payload):
            # A paused worker with an owner marker and no surviving lease is an
            # orphaned cycle (its only participant died between the pause and the
            # release).  It must be taken over and resumed, never mistaken for a
            # user pause (ADR-5 W3).
            action = "takeover_resume"
        elif kept:
            action = "joined"
        else:
            action = "respect_paused"
        out["action"] = action
        if action == "respect_paused":
            return True, False
        if action == "joined":
            if status.get("runtime_state") == "running":
                # ADR-9b (measured): leases exist but the worker is not paused, so
                # that cycle's pause never landed.  Clear any stray pause and open
                # a fresh cycle that KEEPS the live leases; pause exactly once.
                journal(payload, {"event": "stale_running_cycle",
                                  "kept": [e.get("lease_id") for e in kept]})
                try:
                    client.worker_resume()   # best effort; a no-op when enabled
                except ScopeError as exc:
                    journal(payload, {"event": "stale_resume_noop", "error": str(exc)})
                out["action"] = "fresh_cycle_recovering"
                return False, True
            kept = kept + [entry(payload, payload.get("invocations", 1))]
            if not marker_present(payload):
                maybe_exit_at(payload, "after-refcount-before-owner")
                write_atomic(payload, owner_path(payload), OWNER_MARKER, "owner")
            write_lease(payload, state["generation"], kept, state["resume"],
                        state.get("owner") or {}, "join")
            out["writes"] += 1
            gate(payload, "enter_registered")
            return True, False
        # takeover_resume (W4): the orphaned pause is resumed under the lock, and
        # this participant then opens the pause cycle it actually needs (ADR-10d:
        # a takeover is a COMPLETE cycle, never a passive lease on a running
        # worker).
        generation = state["generation"]
        owner = {"lease_id": payload["lease_id"], "generation": generation}
        entries = [entry(payload, payload.get("invocations", 1))]
        reclaimed = [{"lease_id": e.get("lease_id"), "reason": v}
                     for e, v in verdicts if v != "alive"]
        if reclaimed:
            journal(payload, {"event": "pruned", "items": reclaimed})
        write_lease(payload, generation, entries,
                    {"required": True, "generation": generation,
                     "lease_id": payload["lease_id"], "phase": "takeover"},
                    owner, "takeover")
        out["writes"] += 1
        maybe_exit_at(payload, "wm-takeover-before-resume")
        gate(payload, "takeover_before_resume")
        try:
            client.worker_resume()
        except ScopeError as exc:
            write_lease(payload, generation, [],
                        {"required": True, "generation": generation,
                         "lease_id": payload["lease_id"], "phase": "takeover_failed"},
                        owner, "takeover_failed")
            out["writes"] += 1
            out["cleanup_status"] = f"failed:{exc.code}"
            out["code"] = "lease_resume_takeover_failed"
            out["error"] = str(exc)
            out["resume_calls"] = client.resume_calls
            out.update(read_view(payload))
            return True, False
        out["resume_calls"] = client.resume_calls
        out["cleanup_status"] = "restored"
        out["action"] = "takeover_resumed"
        # A takeover is a phase, not the final action: the participant then opens
        # its own pause cycle, and the envelope reports the sequence.
        out.setdefault("actions", []).append("takeover_resumed")
        out.update(read_view(payload))
        return False, True
    finally:
        lock.release()


def protocol_fresh_cycle(payload, client, out, lock_budget, cleanup_budget):
    """T5: fresh cycle.  The lock spans registration, owner sentinel and pause."""
    lock = lease_lock(payload, lock_budget)
    lock.acquire()
    out["lock_wait"] = round(lock.waited, 6)
    error = None
    try:
        gate(payload, "enter_lock_held")
        state = read_lease(payload)
        kept, pruned = prune(payload, state["entries"])
        if pruned:
            journal(payload, {"event": "pruned", "items": pruned})
        generation = state["generation"] + 1
        entries = kept
        if not any(e.get("lease_id") == payload["lease_id"] for e in entries):
            entries = kept + [entry(payload, payload.get("invocations", 1))]
        write_lease(payload, generation, entries, {"required": False},
                    {"lease_id": payload["lease_id"], "generation": generation}, "fresh")
        out["writes"] += 1
        maybe_exit_at(payload, "after-refcount-before-owner")
        # Compat sentinel only; the refcount remains the authority (ADR-5 W1).
        write_atomic(payload, owner_path(payload), OWNER_MARKER, "owner")
        gate(payload, "before_pause")
        maybe_exit_at(payload, "after-owner-before-pause")
        try:
            client.worker_pause()
        except ScopeError as exc:
            error = exc
        out["pause_calls"] = client.pause_calls
        out["generation"] = generation
        out.update(read_view(payload))
        # The gate fires only once this participant's registration AND the pause
        # it owns are both on disk (still inside the critical section).
        gate(payload, "enter_registered")
        maybe_exit_at(payload, "after-pause-before-confirm")
    finally:
        lock.release()
    if error is not None:
        out["action"] = "pause_failed"
        out["error"] = str(error)
        cleanup_after_failed_pause(payload, client, cleanup_budget, out)
        out["resume_calls"] = client.resume_calls
        out.update(read_view(payload))
        return out
    out["action"] = "paused_by_us"
    return out


def cleanup_after_failed_pause(payload, client, cleanup_budget, out):
    """T7: withdraw our own lease, then resume only if we were the last one."""
    with lease_lock(payload, lock_budget_for(cleanup_budget)):
        state = read_lease(payload)
        entries = [e for e in state["entries"] if e.get("lease_id") != payload["lease_id"]]
        owner = state.get("owner") or {}
        if entries:
            write_lease(payload, state["generation"], entries, state["resume"], owner, "pf")
            out["writes"] += 1
            return
        write_lease(payload, state["generation"], [],
                    {"required": True, "generation": state["generation"],
                     "lease_id": payload["lease_id"], "phase": "pause_failed"}, owner, "pf")
        out["writes"] += 1
        try:
            client.worker_resume()
        except ScopeError as exc:
            out["cleanup_status"] = f"failed:{exc.code}"
            return
        out["cleanup_status"] = "restored"
        unlink_quiet(refcount_path(payload))
        unlink_quiet(owner_path(payload))


# --------------------------------------------------------------------------
# protocol mode: release path (T8-T10) -- run by sim/participant.py
# --------------------------------------------------------------------------


def run_protocol_exit(payload):
    client = Client(payload)
    out = {"mode": "protocol", "pid": os.getpid(), "lease_id": payload["lease_id"],
           "phase": "exit", "action": None, "resume_calls": 0,
           "cleanup_status": "not_needed", "writes": 0, "code": None, "error": None}
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
            out["generation"] = generation
            out["owner_lease"] = owner.get("lease_id")
            out["lease_set"] = sorted(e.get("lease_id") for e in entries)
            if entries:
                write_lease(payload, generation, entries, state["resume"], owner, "rel")
                out["writes"] += 1
                out["action"] = "released_joined"
            elif owner.get("lease_id") == payload["lease_id"]:
                # ADR-3/ADR-10: we emptied the refcount UNDER THE LOCK, so no new
                # participant can slip in between "empty" and "resume"; and because
                # we are the recorded owner we resume the pause we opened.
                # Persist the recovery obligation BEFORE acting on it.
                write_lease(payload, generation, [],
                            {"required": True, "generation": generation,
                             "lease_id": payload["lease_id"], "phase": "resume_pending"},
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
                    out["code"] = "lease_resume_failed"
                    out["error"] = str(exc)
                    # keep resume.required + owner marker: never claim restored
                    out.update({k: v for k, v in read_view(payload).items()})
                    return out
                out["resume_calls"] = client.resume_calls
                out["cleanup_status"] = "restored"
                out["action"] = "released_last"
                maybe_exit_at(payload, "wm-resume-crash")
                # Neutral residue: no owner, no obligation, no lease.
                write_lease(payload, generation, [], {"required": False}, {}, "rel")
                out["writes"] += 1
                unlink_quiet(refcount_path(payload))
                unlink_quiet(owner_path(payload))
            elif (state["resume"] or {}).get("required"):
                # ADR-10 recovery: the cycle owner already exited and left this
                # participant the pending obligation.  Resume it ourselves and
                # close the cycle instead of walking away from a paused worker.
                out["action"] = "released_with_pending_resume"
                gate(payload, "before_resume")
                try:
                    client.worker_resume()
                except ScopeError as exc:
                    out["resume_calls"] = client.resume_calls
                    out["cleanup_status"] = f"failed:{exc.code}"
                    out["action"] = "released_last_resume_failed"
                    out["code"] = "lease_resume_failed"
                    out["error"] = str(exc)
                    out.update({k: v for k, v in read_view(payload).items()})
                    return out
                out["resume_calls"] = client.resume_calls
                out["cleanup_status"] = "restored"
                write_lease(payload, generation, [], {"required": False}, {}, "rel")
                out["writes"] += 1
                unlink_quiet(refcount_path(payload))
                unlink_quiet(owner_path(payload))
            else:
                # ADR-10: we are the last lease but we are NOT the cycle owner, so
                # the pause would be left running with nobody obliged to resume it.
                # Take the cycle over and keep the obligation rather than resume.
                transfer = {"required": True, "generation": generation,
                            "lease_id": payload["lease_id"], "phase": "ownership_transfer"}
                write_lease(payload, generation, [], transfer,
                            {"lease_id": payload["lease_id"], "generation": generation}, "rel")
                out["writes"] += 1
                out["action"] = "released_took_ownership"
                out["cleanup_status"] = "deferred:ownership_transfer"
            out.update({k: v for k, v in read_view(payload).items()})
    except ScopeError as exc:
        out["code"] = exc.code
        out["error"] = str(exc)
        out["action"] = "release_fail_closed"
        out["cleanup_status"] = f"failed:{exc.code}"
    out["pause_calls"] = 0
    out["attempted_resumes"] = client.resume_calls
    return out


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
    mutex = FileLock(lock_path(payload), min(LOCK_MAX_SECONDS, request_budget))
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
    else:
        result = run_legacy(payload) if phase == "enter" else run_legacy_exit(payload)
    result["tag"] = payload.get("tag")
    print("RESULT " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
