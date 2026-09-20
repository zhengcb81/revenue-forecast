"""Shared helpers for the I-04-C simulations.

Everything runs inside the attempt directory:
  - base   = evidence/run/<case>/          (refcount / owner / lock files)
  - fence  = evidence/run/<case>/_fence/   (gate markers and unblock fences)
  - journal= evidence/run/<case>/journal.jsonl

No production path, no network, no real worker/provider.  Participants are real
child processes of the isolated interpreter.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
ATTEMPT = os.path.dirname(HERE)
PYTHON = os.path.join(ATTEMPT, "iso", "venv", "Scripts", "python.exe")
PARTICIPANT = os.path.join(HERE, "participant.py")
STUB_WORKER = os.path.join(HERE, "stub_worker.py")
KERNEL = os.path.join(HERE, "kernel.py")

REFCOUNT = "filing_fetch_pause.refcount"
OWNER = "filing_fetch_pause.owner"
LOCK = "filing_fetch_pause.lock"
WORKER = "worker.json"


def b64(obj):
    raw = json.dumps(obj, sort_keys=True).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


class Harness:
    def __init__(self, case_id, root, worker_initial=None, verbose=False):
        self.case_id = case_id
        self.verbose = verbose
        self.root = os.path.abspath(root)
        self.base = os.path.join(self.root, case_id)
        self.fence = os.path.join(self.base, "_fence")
        os.makedirs(self.fence, exist_ok=True)
        self.journal = os.path.join(self.base, "journal.jsonl")
        self.fh = None
        self.procs = []
        self.state = {
            "desired_state": (worker_initial or {}).get("desired_state", "enabled"),
            "runtime_state": (worker_initial or {}).get("runtime_state", "running"),
            "actions": [],
            "blocked_resume": bool((worker_initial or {}).get("blocked_resume", False)),
        }
        self.write_worker()
        open(self.journal, "a", encoding="utf-8").close()
        open(os.path.join(self.base, LOCK), "ab").close()

    # ---------------- paths / low level ----------------

    def path(self, name):
        return os.path.join(self.base, name)

    @property
    def refcount_path(self):
        return self.path(REFCOUNT)

    @property
    def owner_path(self):
        return self.path(OWNER)

    @property
    def lock_path(self):
        return self.path(LOCK)

    def fence_path(self, name):
        return os.path.join(self.fence, name)

    def wait_fence(self, name, timeout=20.0):
        target = self.fence_path(name)
        deadline = time.monotonic() + timeout
        while not os.path.exists(target):
            if time.monotonic() >= deadline:
                raise AssertionError(f"{self.case_id}: fence {name} not reached in {timeout}s")
            time.sleep(0.01)
        return target

    def kill_declared(self, tag):
        """Model a crashed participant for the injected liveness probe.

        The dead invocation cannot remove its own alive file (that is exactly what
        a crash means), so the scheduler removes it -- the same state a real OS
        probe reports once the process is gone.
        """
        removed = []
        for name in os.listdir(self.base):
            if name.startswith("alive.") and name.endswith(f".{tag}.json"):
                os.unlink(os.path.join(self.base, name))
                removed.append(name)
        return removed

    def open_fence(self, name, tag=None):
        """Unblock the participant waiting at gate `name`.

        The fence name must match ``gate_wait`` exactly: ``<name>[.<tag>].fence``.
        """
        suffix = f".{tag}" if tag else ""
        target = self.fence_path(f"{name}{suffix}.fence")
        with open(target, "w", encoding="utf-8") as handle:
            handle.write("go")
        if self.verbose:
            print(f"[fence] opened {os.path.basename(target)}", flush=True)
        return target

    def gate_wait(self, name, tag=None):
        """Tell the participant to announce gate `name` and wait for its fence.

        With a tag the fence is per participant, which is what lets the scheduler
        hold one participant inside its critical section while releasing another.
        """
        suffix = f".{tag}" if tag else ""
        return {name: self.fence_path(f"{name}{suffix}.fence")}

    def reached(self, name, tag=None):
        if tag:
            return os.path.join(self.base, f"gate.{name}.{tag}.reached")
        return os.path.join(self.base, f"gate.{name}.reached")

    def wait_reached(self, name, timeout=20.0, tag=None):
        marker = self.reached(name, tag=tag)
        deadline = time.monotonic() + timeout
        while not os.path.exists(marker):
            if time.monotonic() >= deadline:
                raise AssertionError(f"{self.case_id}: gate {name} not reached in {timeout}s")
            time.sleep(0.01)
        return marker

    # ---------------- payload / processes ----------------

    def payload(self, tag, lease_id=None, **overrides):
        data = {
            "base": self.base,
            "journal": self.journal,
            "tag": tag,
            "lease_id": lease_id or uuid.uuid4().hex[:24],
            "mode": "protocol",
            "phase": "enter",
            "enabled": True,
            "request_budget": 100.0,
            "cleanup_budget": 30.0,
            "probe_b64": b64(overrides.pop("probe", {})),
            "status_b64": b64(overrides.pop("status", {"desired_state": "enabled",
                                                      "runtime_state": "running"})),
            # Liveness in these runs is the DECLARED participant model (see
            # oracle.md section 8); set declared_liveness=False to use the real
            # OS probe instead.
            "declared_liveness": True,
        }
        # The release phase replays the same lease, so it must also declare the
        # same holder: that is what keeps the lease alive until the release runs.
        if data["phase"] == "exit":
            data["holder"] = data["lease_id"]
        for key in ("resume_error", "resume_gate", "fake_start_time", "invocations",
                    "stop_after_enter", "stop_after_first_exit"):
            if key in overrides:
                value = overrides.pop(key)
                data["resume_error_b64" if key == "resume_error" else key] = (
                    b64(value) if key == "resume_error" else value
                )
        data.update(overrides)
        return data

    def spawn(self, payload, argv=None, env_extra=None):
        env = dict(os.environ)
        env["FILING_FETCH_SIM_PAYLOAD"] = b64(payload)
        env["PYTHONIOENCODING"] = "utf-8"
        if env_extra:
            env.update(env_extra)
        out = open(self.path(f"stdout.{payload['tag']}.txt"), "w", encoding="utf-8")
        err = open(self.path(f"stderr.{payload['tag']}.txt"), "w", encoding="utf-8")
        proc = subprocess.Popen(
            [PYTHON, "-B", PARTICIPANT, *(argv or [])],
            cwd=self.base,
            env=env,
            stdout=out,
            stderr=err,
            stdin=subprocess.DEVNULL,
        )
        proc._sim_tag = payload["tag"]  # type: ignore[attr-defined]
        proc._sim_payload = payload  # type: ignore[attr-defined]
        self.procs.append((payload["tag"], proc))
        return proc

    def run(self, payload, argv=None, timeout=90.0):
        proc = self.spawn(payload, argv=argv)
        return self.collect(proc, timeout=timeout)

    def collect(self, proc, timeout=90.0):
        tag = proc._sim_tag  # type: ignore[attr-defined]
        try:
            code = proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
            code = "TIMEOUT"
        envelope = self.envelope_of(tag)
        return {"tag": tag, "returncode": code, "envelope": envelope}

    def envelope_of(self, tag):
        path = self.path(f"stdout.{tag}.txt")
        if not os.path.exists(path):
            return {"kind": "missing"}
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                if line.startswith("ENVELOPE "):
                    data = json.loads(line[len("ENVELOPE "):])
                    # A "lifetime" participant (enter + release in one process)
                    # exposes the release step under "exit", so both invocations
                    # can be read through the same key.
                    if data.get("kind") == "lifetime":
                        data.setdefault("result", data.get("result"))
                    return data
        return {"kind": "none"}

    def wait_envelope(self, tag, timeout=60.0):
        """Block until the participant wrote its ENVELOPE line (i.e. finished the
        phase).  This lets the scheduler keep earlier participants ALIVE while it
        starts the later ones -- without it, sequential ``collect`` calls would
        make real-process liveness answer 'dead' for participants that already
        exited."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            envelope = self.envelope_of(tag)
            if envelope.get("kind") not in {"missing", "none"}:
                return envelope
            time.sleep(0.01)
        raise AssertionError(f"{self.case_id}: {tag} produced no envelope in {timeout}s")

    def wait_all_envelopes(self, tags, timeout=60.0):
        return {tag: self.wait_envelope(tag, timeout=timeout) for tag in tags}

    def enter(self, tag, **kwargs):
        payload = self.payload(tag, phase="enter", **kwargs)
        argv = ["--two-scopes"] if kwargs.pop("two_scopes", False) else None
        return self.run(payload, argv=argv)

    def enter_async(self, tag, two_scopes=False, **kwargs):
        payload = self.payload(tag, phase="enter", **kwargs)
        argv = ["--two-scopes"] if two_scopes else None
        return self.spawn(payload, argv=argv)

    def lifetime(self, tag, lease_id=None, **kwargs):
        """Start a participant that enters, holds (at the `lifetime_hold` gate if
        one is given) and then releases -- all inside one process."""
        payload = self.payload(tag, lease_id=lease_id, lifetime=True, **kwargs)
        return self.spawn(payload)

    def run_lifetime(self, tag, lease_id=None, **kwargs):
        return self.collect(self.lifetime(tag, lease_id=lease_id, **kwargs))

    def exit_async(self, tag, lease_id, **kwargs):
        payload = self.payload(tag, phase="exit", lease_id=lease_id,
                               holder=lease_id, **kwargs)
        return self.spawn(payload)

    # ---------------- worker stub ----------------

    def worker(self, subcommand, tag):
        """Run the stub worker CLI once (real child process, return code kept)."""
        payload = {"base": self.base, "journal": self.journal, "tag": tag}
        proc = subprocess.run(
            [PYTHON, "-B", STUB_WORKER, b64(payload), subcommand],
            cwd=self.base,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        return {"returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}

    # ---------------- observation ----------------

    def worker_state(self):
        with open(self.path(WORKER), "r", encoding="utf-8") as handle:
            return json.load(handle)

    def set_worker_state(self, **values):
        state = self.worker_state()
        state.update(values)
        with open(self.path(WORKER), "w", encoding="utf-8") as handle:
            json.dump(state, handle, sort_keys=True)

    def write_worker(self):
        with open(self.path(WORKER), "w", encoding="utf-8") as handle:
            json.dump(self.state, handle, sort_keys=True)

    def lease_view(self):
        if not os.path.exists(self.refcount_path):
            return {"exists": False, "entries": [], "generation": 0,
                    "owner_lease": None, "resume_required": False}
        with open(self.refcount_path, "r", encoding="utf-8") as handle:
            raw = handle.read()
        try:
            data = json.loads(raw)
        except ValueError:
            return {"exists": True, "corrupt": True, "sha256": hashlib.sha256(
                raw.encode("utf-8")).hexdigest()}
        if isinstance(data, list):
            return {"exists": True, "legacy": True, "entries": data}
        return {
            "exists": True,
            "entries": sorted(e.get("lease_id") for e in data.get("entries", [])),
            "raw_entries": data.get("entries", []),
            "generation": data.get("generation"),
            "owner_lease": (data.get("owner") or {}).get("lease_id"),
            "resume_required": bool((data.get("resume") or {}).get("required")),
        }

    def owner_exists(self):
        return os.path.exists(self.owner_path)

    def wait_for_owner(self, timeout=5.0):
        deadline = time.monotonic() + timeout
        while not os.path.exists(self.owner_path):
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.01)
        return True

    def journal_events(self, event=None):
        rows = []
        if not os.path.exists(self.journal):
            return rows
        with open(self.journal, "r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    rows.append({"event": "<unparsable>", "raw": line})
                    continue
                if event is None or row.get("event") == event:
                    rows.append(row)
        return rows

    def counts(self):
        state = self.worker_state()
        actions = state.get("actions", [])
        return {
            "pause_calls": actions.count("pause"),
            "resume_calls": actions.count("resume"),
            "actions": list(actions),
            "desired_state": state.get("desired_state"),
            "runtime_state": state.get("runtime_state"),
        }

    # ---------------- assertions / reporting ----------------

    def check(self, label, ok, detail=""):
        return {"check": label, "result": "PASS" if ok else "FAIL", "detail": detail}

    def finish(self, checks, extra=None):
        failed = [c for c in checks if c["result"] == "FAIL"]
        record = {
            "case": self.case_id,
            "status": "PASS" if not failed else "FAIL",
            "checks": checks,
            "lease_view": self.lease_view(),
            "counts": self.counts(),
            "owner_exists": self.owner_exists(),
            "lock_file_exists": os.path.exists(self.lock_path),
            "journal_lines": len(self.journal_events()),
        }
        if extra:
            record.update(extra)
        print(json.dumps(record, sort_keys=True))
        for name, proc in self.procs:
            try:
                proc.wait(timeout=5)
            except Exception:
                proc.kill()
        return 0 if not failed else 1


def banner(text):
    print(f"=== {text} ===")
