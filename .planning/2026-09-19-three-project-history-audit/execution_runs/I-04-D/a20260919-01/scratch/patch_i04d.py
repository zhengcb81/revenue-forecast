"""I-04-D patcher: install the I-04-C frozen lease protocol into the ISO copy only.

Run with the attempt's isolated interpreter:
  iso/venv/Scripts/python.exe scratch/patch_i04d.py --check
  iso/venv/Scripts/python.exe scratch/patch_i04d.py --apply

It rewrites:
  iso/filing-fetch/scripts/fetch_filing.py   (product side, isolated copy)
and leaves every production repo untouched.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
TARGET = ATTEMPT / "iso" / "filing-fetch" / "scripts" / "fetch_filing.py"
BASELINE_SHA = "dc593a75cae991b1d5c54114ef22e9616c9276c070afdaabcdad758e0c13af1c"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# 1. _pid_is_alive: return the incarnation evidence instead of a bare bool
# ---------------------------------------------------------------------------

OLD_PROBE = '''def _pid_is_alive(pid: int, *, timeout: float) -> bool:
    """Best-effort pid liveness; unknown states count as alive (conservative).

    I-04-A D1 row R-P: this spawns a real subprocess, so it is a budget consumer.
    Callers pass the phase budget (request remaining, or the cleanup budget)
    instead of the old hard-coded 20s tail; a probe timeout is re-raised so the
    caller can record it rather than silently reading "alive".
    """
    if os.name == "nt":
        try:
            probe = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore[attr-defined]
                timeout=min(_PID_PROBE_MAX_SECONDS, timeout),
            )
        except subprocess.TimeoutExpired:
            raise
        except (OSError, subprocess.SubprocessError):
            return True
        return f"{pid}" in (probe.stdout or "")
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except OSError:
        return True
'''

NEW_PROBE = '''def _pid_is_alive(pid: int, *, timeout: float) -> bool:
    """Best-effort pid liveness; unknown states count as alive (conservative).

    Kept as the single-call compatibility surface: it is now a thin wrapper over
    :func:`_probe_process` (I-04-D / I-04-C ADR-4), which additionally reports the
    process creation time so a *reused* pid can be told apart from a live holder.
    """
    return _probe_process(pid, timeout=timeout)["alive"]


def _pid_is_alive_with_start_time(pid: int, *, timeout: float) -> tuple[bool, str]:
    """Single probe primitive; returns (alive, os_start_time).

    I-04-A D1 row R-P: the probe is a real action and a budget consumer, so the
    deadline is enforced in-process before and after it, and any subprocess tail is
    capped at ``_PID_PROBE_MAX_SECONDS``.

    ``os_start_time`` is the OS-reported creation instant (Windows FILETIME, 100ns),
    or "" when unavailable.  The empty string is the fail-closed direction: without
    it the pid-reuse rule cannot fire, so such a record is never reclaimed by it.
    """
    deadline = time.monotonic() + min(_PID_PROBE_MAX_SECONDS, timeout)

    if os.name == "nt":
        exists = _process_exists(pid)
        if exists is False:
            return False, ""
        if exists is True:
            return True, _process_start_time_raw(pid) or ""

    if os.name != "nt":
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False, ""
        except OSError:
            return True, ""

    # Degraded path: the query could not answer, so fall back to the legacy tasklist
    # spawn.  Rule 2 (pid reuse) stays inert while os_start_time is "" - the contract
    # is unchanged, only the reclaim ability is weaker.
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise subprocess.TimeoutExpired(cmd="pid-probe", timeout=timeout)
    try:
        probe = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}"],
            capture_output=True,
            text=True,
            errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW,  # type: ignore[attr-defined]
            timeout=remaining,
        )
    except subprocess.TimeoutExpired:
        raise
    except (OSError, subprocess.SubprocessError):
        return True, ""
    except Exception:  # noqa: BLE001 - any probe failure is "unknown", never "dead"
        return True, ""
    if (probe.stdout or "").find(str(pid)) < 0:
        return False, ""
    return True, ""


def _process_start_time_raw(pid: int) -> str | None:
    """OS-reported creation time, or None when it cannot be read."""
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:  # noqa: BLE001 - no ctypes means no answer, not "dead"
        return None
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        open_process = kernel32.OpenProcess
        open_process.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        open_process.restype = wintypes.HANDLE
        get_process_times = kernel32.GetProcessTimes
        get_process_times.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(wintypes.FILETIME),
            ctypes.POINTER(wintypes.FILETIME),
            ctypes.POINTER(wintypes.FILETIME),
            ctypes.POINTER(wintypes.FILETIME),
        ]
        get_process_times.restype = wintypes.BOOL
        close_handle = kernel32.CloseHandle
        close_handle.argtypes = [wintypes.HANDLE]
        close_handle.restype = wintypes.BOOL
        handle = open_process(0x1000, False, pid)
        if not handle:
            return None
        try:
            creation = wintypes.FILETIME()
            exit_time = wintypes.FILETIME()
            kernel = wintypes.FILETIME()
            user = wintypes.FILETIME()
            ok = get_process_times(
                handle,
                ctypes.byref(creation),
                ctypes.byref(exit_time),
                ctypes.byref(kernel),
                ctypes.byref(user),
            )
            if not ok:
                return None
            return str((creation.dwHighDateTime << 32) | creation.dwLowDateTime)
        finally:
            close_handle(handle)
    except Exception:  # noqa: BLE001 - unknown stays unknown
        return None


def _windows_process_start_time(pid: int) -> str | None:
    """Creation time for a pid the OS confirms exists; None when it cannot answer.

    I-04-C ADR-4: rule 2 (pid reuse) needs the *creation time*, not just "alive".
    ``OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION)`` + ``GetProcessTimes`` needs no
    subprocess at all, so the whole probe fits inside the 5s floor.

    Returns:
      "0"   -> the OS confirms this pid does not exist
      "N"   -> the OS reports creation time N (100ns FILETIME)
      None  -> this API cannot answer; the caller degrades instead of guessing
    """
    exists = _process_exists(pid)
    if exists is None:
        return None
    if not exists:
        return "0"
    return _process_start_time_raw(pid)


def _process_exists(pid: int) -> bool | None:
    """Whether the OS says this pid exists, using no subprocess.

    True  - OpenProcess returned a handle
    False - ERROR_INVALID_PARAMETER (87), the documented "no such process" answer
    None  - this API cannot answer (non-Windows, or the query itself failed).  None
            is the conservative direction: the caller must not read it as "dead".
    """
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes
    except Exception:  # noqa: BLE001
        return None
    try:
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        open_process = kernel32.OpenProcess
        open_process.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
        open_process.restype = wintypes.HANDLE
        close_handle = kernel32.CloseHandle
        close_handle.argtypes = [wintypes.HANDLE]
        close_handle.restype = wintypes.BOOL
        # PROCESS_QUERY_LIMITED_INFORMATION: works for another user's process and on
        # protected processes, and needs no VM_READ.
        handle = open_process(0x1000, False, pid)
        if not handle:
            return ctypes.get_last_error() != 87
        try:
            return True
        finally:
            close_handle(handle)
    except Exception:  # noqa: BLE001 - unknown stays unknown
        return None
'''

# ---------------------------------------------------------------------------
# 2. the protocol block that replaces _read/_write/_prune/_PausedWorkerScope
# ---------------------------------------------------------------------------

OLD_BLOCK_START = '''def _read_pause_entries(root: Path) -> list[dict[str, Any]]:'''

OLD_BLOCK_END = '''def _normalize_stats(stats: dict[str, Any] | None) -> dict[str, Any]:'''

NEW_BLOCK = r'''# ---------------------------------------------------------------------------
# I-04-D: cross-process lease / ownership / recovery protocol.
#
# Implemented from execution_runs/I-04-C/a20260919-01/decision.md v1.3
# (accepted_scoped): ADR-1..ADR-12, the R1-R5 last-release branch table and
# lock_budget_for(x) = min(x, 60).  The design is NOT re-opened here.
#
# The three non-atomic read-modify-writes of the legacy code are closed by one
# OS byte-range lock on a lock file that is never unlinked (ADR-1/ADR-2):
#   RC-1 two concurrent _register calls both read an empty store;
#   RC-2 the "last one out" decision raced a new participant;
#   RC-3 the owner marker was written after the refcount, so a crash between
#        them made the next participant read "paused + no owner" as a USER pause.
# ---------------------------------------------------------------------------

LOCK_MAX_SECONDS = 60.0  # ADR-2 waiting cap (I-04-C OPEN-3 / owner gate C2)
_LOCK_POLL_SECONDS = 0.05
_PAUSE_LEASE_SCHEMA = "filing-fetch.pause-refcount/2"
_PAUSE_LOCK_NAME = "filing_fetch_pause.lock"
_PAUSE_JOURNAL_NAME = "filing_fetch_pause.journal.jsonl"

# I-04-C ADR-7: the legacy (list, no schema) refcount is NOT adopted silently -
# it carries no generation, no resume obligation and no incarnation, so adopting
# it would reopen the W1/W4 holes under the new code's name.
_MIGRATE_ENV = "FILING_FETCH_PAUSE_LEASE_MIGRATE"

# Test-only instrumentation.  Unset (the production default) means: one dict-less
# comparison per critical section and no behaviour difference whatsoever.
_HOOKS_ENV = "I04D_HOOKS"

_MIGRATE_HINT = (
    f"migrate each entry with {_MIGRATE_ENV}=1 (legacy:<pid>:<index> lease ids, "
    "generation 0, resume.required=false), or register the entries by hand"
)

LEASE_ACTION_FAIL_CLOSED = frozenset(
    {
        "lease_lock_timeout",
        "lease_state_corrupt",
        "lease_state_legacy",
        "lease_conflict_unknown",
        "lease_resume_takeover_failed",
        "lease_state_write_failed",
    }
)

# I-04-C ADR-2/ADR-8: which lease outcome still owes a release critical section.
# A lease action never means "no lease was written": the ledger is the authority.
LEASE_ACTIONS_OWING_RELEASE = frozenset(
    {
        "paused_by_us",
        "joined",
        "released_joined",
        "released_last",
        "released_owner_changed",
        "release_fail_closed",
        "lease_lock_timeout",
        "lease_conflict_unknown",
        "lease_resume_takeover_failed",
        "lease_state_write_failed",
    }
)

# I-04-C ADR-11: statuses that licence a takeover of an existing pause cycle
# rather than opening a new one.
_OWNS_CYCLE_STATUSES = ("paused_by_us", "takeover_resumed")


def _lease_owns_cycle(status: Any) -> bool:
    return status in _OWNS_CYCLE_STATUSES


def _lease_lock_path(root: Path) -> Path:
    return _catalog_dir(root) / _PAUSE_LOCK_NAME


def _pause_state_path(root: Path) -> Path:
    return _catalog_dir(root) / _PAUSE_REFCOUNT_NAME


def _pause_owner_path(root: Path) -> Path:
    return _catalog_dir(root) / _PAUSE_OWNER_NAME


def _pause_journal_path(root: Path) -> Path:
    return _catalog_dir(root) / _PAUSE_JOURNAL_NAME


def _boot_uuid() -> str:
    """One incarnation id per process (ADR-4); regenerated on every start."""
    global _BOOT_UUID
    if not _BOOT_UUID:
        _BOOT_UUID = uuid.uuid4().hex[:12]
    return _BOOT_UUID


_BOOT_UUID = ""


def _new_lease_id() -> str:
    return uuid.uuid4().hex[:24]


def _lease_journal(root: Path, event: str, **fields: Any) -> None:
    """Append one diagnostic line.  Never authoritative, never fatal (ADR-7)."""
    record = {
        "event": event,
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "monotonic": round(time.monotonic(), 6),
        "pid": os.getpid(),
    }
    record.update(fields)
    try:
        directory = _catalog_dir(root)
        directory.mkdir(parents=True, exist_ok=True)
        line = (json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
        if len(line) > 4096:  # keep O_APPEND single-write atomicity
            line = (json.dumps({"event": event, "truncated": True}) + "\n").encode("utf-8")
        handle = os.open(str(_pause_journal_path(root)), os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o644)
        try:
            os.write(handle, line)
        finally:
            os.close(handle)
    except OSError:
        pass


def _unique_tmp_path(path: Path) -> Path:
    """O-5: a *unique* temporary name, so two writers can never share one temp file.

    The legacy ``path + ".tmp"`` is a single fixed name: two concurrent writers
    overwrite each other's temp file and one ``os.replace`` then moves the other
    writer's bytes (or raises FileNotFoundError) - the lost update the lock exists
    to prevent.
    """
    return path.with_name(
        f"{path.name}.{os.getpid()}.{_boot_uuid()}.{uuid.uuid4().hex[:8]}.tmp"
    )


class _LeaseWriteError(OSError):
    """An OSError from the ledger write, with the window it happened in."""

    def __init__(self, window: str, tmp: Path, target: Path, cause: OSError) -> None:
        super().__init__(
            f"{window}: {type(cause).__name__} errno={cause.errno} "
            f"filename={cause.filename!r} tmp_len={len(str(tmp))} "
            f"target_len={len(str(target))} target={target} ({cause})"
        )
        self.window = window
        self.cause = cause


def _atomic_write_json(path: Path, payload: Any) -> None:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise _LeaseWriteError("mkdir", path, path, exc) from exc
    tmp = _unique_tmp_path(path)
    try:
        tmp.write_text(encoded, encoding="utf-8")
    except OSError as exc:
        raise _LeaseWriteError("write_text", tmp, path, exc) from exc
    try:
        tmp.replace(path)
    except OSError as exc:
        try:
            if tmp.exists():
                tmp.unlink()
        except OSError:
            pass
        raise _LeaseWriteError("replace", tmp, path, exc) from exc


def _hash_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return ""


class _ProbeResult:
    """The liveness verdict plus its evidence (ADR-4 rules 1-5)."""

    __slots__ = ("verdict", "os_start_time", "error")

    def __init__(self, verdict: str, os_start_time: str = "", error: str = "") -> None:
        self.verdict = verdict  # self | alive | dead | reused | unknown
        self.os_start_time = os_start_time
        self.error = error

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return f"_ProbeResult({self.verdict!r}, {self.os_start_time!r}, {self.error!r})"


def _probe_injection(pid: int) -> str | None:
    """I04D_PROBE_INJECT={"<pid>": "<reason>"} forces an UNKNOWN verdict for that pid."""
    raw = os.environ.get("I04D_PROBE_INJECT")
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload.get(str(pid))


def _probe_entry_verdict(entry: dict[str, Any], *, probe_timeout: float) -> _ProbeResult:
    """Decide one lease holder's liveness.  The failure direction is always safe."""
    pid = entry.get("pid")
    if not isinstance(pid, int):
        return _ProbeResult("unknown", "", "pid is not an int")
    recorded_boot = entry.get("boot_uuid")
    if pid == os.getpid() and recorded_boot == _boot_uuid():
        return _ProbeResult("self")  # rule 1: own incarnation, never spawn a probe
    injected = _probe_injection(pid)
    if injected is not None:
        # Test-only: a schedule can force one pid's probe to fail so the UNKNOWN
        # branch (ADR-4 rule 5) is reachable without breaking a real probe.
        return _ProbeResult("unknown", "", f"injected:{injected}")
    try:
        alive, observed_start = _pid_is_alive_with_start_time(pid, timeout=probe_timeout)
    except subprocess.TimeoutExpired:
        return _ProbeResult("unknown", "", "probe_timeout")
    except Exception as exc:  # noqa: BLE001 - any failure is UNKNOWN, never "dead"
        return _ProbeResult("unknown", "", f"probe_error:{type(exc).__name__}")
    if not alive:
        return _ProbeResult("dead", observed_start)
    recorded_start = entry.get("os_start_time") or ""
    if recorded_start and observed_start == "0":
        # The record claims a creation time but the OS now says the pid is gone:
        # inside one probe the two answers disagree, so the record is not usable.
        return _ProbeResult("unknown", observed_start, "record_start_but_pid_absent")
    if recorded_start and observed_start and recorded_start != observed_start:
        return _ProbeResult("reused", observed_start)  # rule 2: pid reuse, holder is gone
    if observed_start == "0":
        return _ProbeResult("dead", observed_start)
    return _ProbeResult("alive", observed_start)  # rule 3: conservative


class _LeaseView:
    """One probing pass over the ledger: live leases keep their verdict as evidence.

    Probing twice would be wrong as well as wasteful: the second answer can differ
    (a holder may die between passes), and the branch would then act on a verdict
    that contradicts the one recorded in the journal.
    """

    __slots__ = ("state", "live", "live_verdicts", "reclaimed", "reclaimed_verdicts")

    def __init__(
        self,
        state: "_LeaseState",
        live: list[dict[str, Any]],
        live_verdicts: list[_ProbeResult],
        reclaimed: list[dict[str, Any]],
        reclaimed_verdicts: list[_ProbeResult],
    ) -> None:
        self.state = state
        self.live = live
        self.live_verdicts = live_verdicts
        self.reclaimed = reclaimed
        self.reclaimed_verdicts = reclaimed_verdicts

    @property
    def unknowns(self) -> list[dict[str, Any]]:
        return [
            entry
            for entry, verdict in zip(self.live, self.live_verdicts)
            if verdict.verdict == "unknown"
        ]


class _LeaseScopeError(Exception):
    """Internal carrier for a fail-closed lease outcome (ADR-2/ADR-4/ADR-5)."""

    def __init__(
        self, code: str, message: str, *, cleanup: str = "", resume_code: str = ""
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.cleanup = cleanup
        self.resume_code = resume_code

    def filing_error(self) -> "FilingFetchError":
        return FilingFetchError(self.message, code=self.code)


class _LeaseLocked:
    """Context manager owning the ONE lease critical section (ADR-2: never nested).

    Re-entrant by depth inside a single process so ``__exit__`` can reuse the lock
    its own ``__enter__`` path already holds.  A non-reentrant request would
    self-timeout inside one thread, which ADR-2/§3.3 forbids (cross-thread
    concurrency is not granted by this card).
    """

    def __init__(self, scope: "PausedWorkerScope") -> None:
        self._scope = scope
        self._depth = 0
        self._handle: Any = None

    @property
    def held(self) -> bool:
        return self._depth > 0

    def __enter__(self) -> "_LeaseLocked":
        self._scope._acquire_lock()
        self._depth += 1
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self._depth -= 1
        if self._depth <= 0:
            self._depth = 0
            handle, self._handle = self._handle, None
            self._scope._release_lock(handle)


class _Hooks:
    """Test-only instrumentation, inert unless ``I04D_HOOKS`` is set (I-04-D).

    Production never sets it, so this reduces to a module-level ``None`` check.
    Recognised directives, comma separated:

      ``gate:<name>[@<tag>][@<timeout>]``  publish ``gate.<name>[@<tag>].reached``
                                           and wait for ``gate.<name>.fence``
      ``crash:<point>:<code>``             ``os._exit(<code>)`` at ``<point>``

    The gates are file fences, never sleeps: a schedule can therefore pin an
    interleaving deterministically instead of hoping for one.
    """

    def __init__(self, spec: str, *, tag: str = "") -> None:
        self.dir = Path(os.environ.get("I04D_HOOK_DIR") or ".")
        self.tag = tag
        self.gates: dict[tuple[str, str], float] = {}
        self.arrivals: set[tuple[str, str]] = set()
        self.crashes: dict[str, int] = {}
        for item in (part.strip() for part in spec.split(",")):
            if not item:
                continue
            kind, _, rest = item.partition(":")
            if kind == "gate":
                fields = rest.split("@")
                name = fields[0]
                gate_tag = fields[1] if len(fields) > 1 else ""
                timeout = float(fields[2]) if len(fields) > 2 else 300.0
                self.gates[(name, gate_tag)] = timeout
            elif kind == "arrive":
                fields = rest.split("@")
                name = fields[0]
                arrive_tag = fields[1] if len(fields) > 1 else ""
                self.arrivals.add((name, arrive_tag))
            elif kind == "crash":
                point, _, code = rest.partition(":")
                self.crashes[point] = int(code or 90)
        self.dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _fence_name(name: str, tag: str) -> str:
        return f"gate.{name}.{tag}" if tag else f"gate.{name}"

    def _applies(self, point_tag: str) -> bool:
        """A point belongs to the participant it names, or to all when unnamed.

        Without this filter every participant would wait at every gate, which
        deadlocks B on a gate only A can reach - and a deadlock is not a schedule.
        """
        return not point_tag or point_tag == self.tag

    def __call__(self, point: str, context: dict[str, Any]) -> None:
        code = self.crashes.get(point)
        if code is not None:
            _lease_journal(Path(context.get("root") or "."), "i04d_hook_crash", point=point, code=code)
            sys.stdout.flush()
            sys.stderr.flush()
            os._exit(code)
        for name, arrive_tag in self.arrivals:
            if not self._applies(arrive_tag):
                continue
            marker = self.dir / f"arrive.{name}.{arrive_tag or 'all'}"
            if not marker.exists():
                marker.write_text("arrived", encoding="utf-8")
        for (name, gate_tag), timeout in self.gates.items():
            if not self._applies(gate_tag):
                continue
            base = self._fence_name(name, gate_tag)
            reached = self.dir / f"{base}.reached"
            if not reached.exists():
                reached.write_text("reached", encoding="utf-8")
                try:
                    import traceback as _tb

                    sys.stderr.write(
                        f"[i04d] gate {base} published by pid {os.getpid()} at {point}\n"
                        + "".join(_tb.format_stack()[-6:])
                    )
                    sys.stderr.flush()
                except Exception:  # noqa: BLE001
                    pass
            fence = self.dir / f"{base}.fence"
            limit = time.monotonic() + timeout
            while not fence.exists():
                if time.monotonic() > limit:
                    raise FilingFetchError(
                        f"I04D hook gate {base} timed out after {timeout}s",
                        code="i04d_gate_timeout",
                    )
                time.sleep(0.005)


_HOOKS: "_Hooks | None" = None


def _i04d_hook(point: str, **context: Any) -> None:
    global _HOOKS
    spec = os.environ.get(_HOOKS_ENV)
    if not spec:
        return
    if _HOOKS is None:
        _HOOKS = _Hooks(spec, tag=os.environ.get("I04D_HOOK_TAG") or "")
    _HOOKS(point, context)


class _LeaseState:
    """The persisted lease document (ADR-7: schema ``filing-fetch.pause-refcount/2``)."""

    def __init__(
        self,
        generation: int,
        resume_required: bool,
        resume_lease_id: str,
        entries: list[dict[str, Any]],
        owner: dict[str, Any] | None,
    ) -> None:
        self.generation = generation
        self.resume_required = resume_required
        self.resume_lease_id = resume_lease_id
        self.entries = entries
        self.owner = owner

    def document(self, *, resume_required: bool | None = None) -> dict[str, Any]:
        required = self.resume_required if resume_required is None else resume_required
        return {
            "schema": _PAUSE_LEASE_SCHEMA,
            "generation": self.generation,
            "resume": {
                "required": bool(required),
                "generation": self.generation,
                "lease_id": self.resume_lease_id or "",
                "phase": "resume_pending" if required else "idle",
            },
            "entries": list(self.entries),
            "owner": self.owner,
        }

    def text(self, *, resume_required: bool | None = None) -> str:
        return json.dumps(self.document(resume_required=resume_required), ensure_ascii=False, sort_keys=True)


def _sys_process_start_time() -> str:
    """This process's own creation instant, as the OS reports it (ADR-4).

    A probe cannot be asked about the process it runs in (a probe failure would
    then be indistinguishable from self-death), so the value is captured once and
    persisted with every lease and owner record.  "" means "no incarnation
    evidence" and disables pid-reuse detection - the fail-closed direction.
    """
    return _windows_process_start_time(os.getpid()) or ""


def _lease_entry(scope: "PausedWorkerScope", state: _LeaseState, *, invocations: int, joined: bool) -> dict[str, Any]:
    return {
        "lease_id": scope.lease_id,
        "pid": os.getpid(),
        "os_start_time": scope._proc_start_time or "",
        "boot_uuid": _boot_uuid(),
        "invocations": invocations,
        "joined": joined,
    }


def _read_pause_state(root: Path, *, migrate: bool | None = None) -> _LeaseState:
    """Read the lease document, or fail closed.

    I-04-C ADR-5 W6 / ADR-7: corrupt JSON, a non-object payload, a wrong schema or
    an entry without a ``lease_id`` are all *unreadable*, and ``unknown != empty``.
    The legacy list is readable only when the operator opts in.
    """
    if migrate is None:
        migrate = os.environ.get(_MIGRATE_ENV) == "1"
    path = _pause_state_path(root)
    if not path.exists():
        return _LeaseState(0, False, "", [], None)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise _LeaseScopeError(
            "lease_state_corrupt",
            f"pause refcount {path} is unreadable: {exc}. Not renamed, not deleted, "
            "not rebuilt - inspect it by hand",
        ) from exc
    if not raw.strip():
        return _LeaseState(0, False, "", [], None)
    try:
        payload = json.loads(raw)
    except ValueError as exc:
        raise _LeaseScopeError(
            "lease_state_corrupt",
            f"pause refcount {path} is not valid JSON ({exc}); sha256="
            f"{_hash_file(path)}. The file is left EXACTLY as found for inspection",
        ) from exc
    if isinstance(payload, list) and not migrate:
        raise _LeaseScopeError(
            "lease_state_legacy",
            f"pause refcount {path} uses the pre-I-04-D list format ({len(payload)} "
            f"entries): it has no generation, no resume obligation and no process "
            f"incarnation, so it cannot be told apart from a user pause. To proceed, "
            f"{_MIGRATE_HINT}",
        )
    if isinstance(payload, list):
        return _migrate_legacy_payload(payload)
    if not isinstance(payload, dict) or payload.get("schema") != _PAUSE_LEASE_SCHEMA:
        raise _LeaseScopeError(
            "lease_state_corrupt",
            f"pause refcount {path} is not a {_PAUSE_LEASE_SCHEMA} document; sha256="
            f"{_hash_file(path)}. Left EXACTLY as found",
        )
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise _LeaseScopeError(
            "lease_state_corrupt",
            f"pause refcount {path} has a non-list 'entries'; sha256={_hash_file(path)}",
        )
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or not isinstance(entry.get("lease_id"), str) or not entry["lease_id"]:
            raise _LeaseScopeError(
                "lease_state_corrupt",
                f"pause refcount {path} entry #{index} has no usable lease_id "
                f"(element-level validation, ADR-4); sha256={_hash_file(path)}",
            )
        if not isinstance(entry.get("pid"), int):
            raise _LeaseScopeError(
                "lease_state_corrupt",
                f"pause refcount {path} entry #{index} has no integer pid; "
                f"sha256={_hash_file(path)}",
            )
    resume = payload.get("resume")
    if not isinstance(resume, dict):
        resume = {}
    owner = payload.get("owner")
    if owner is not None and not isinstance(owner, dict):
        raise _LeaseScopeError(
            "lease_state_corrupt",
            f"pause refcount {path} has a non-object owner record; sha256={_hash_file(path)}",
        )
    generation = payload.get("generation")
    if not isinstance(generation, int) or generation < 0:
        generation = 0
    return _LeaseState(
        generation,
        bool(resume.get("required", False)),
        str(resume.get("lease_id") or ""),
        list(entries),
        dict(owner) if owner else None,
    )


def _migrate_legacy_payload(legacy: list[Any]) -> _LeaseState:
    """ADR-7 opt-in migration: adopt legacy entries WITHOUT claiming an obligation."""
    migrated: list[dict[str, Any]] = []
    for index, entry in enumerate(legacy):
        if not isinstance(entry, dict):
            continue
        pid = entry.get("pid")
        if not isinstance(pid, int):
            continue
        migrated.append(
            {
                "lease_id": f"legacy:{pid}:{index}",
                "pid": pid,
                "os_start_time": "",
                "boot_uuid": "",
                "invocations": 1,
                "joined": bool(entry.get("joined", False)),
            }
        )
    return _LeaseState(0, False, "", migrated, None)


def _write_pause_state(root: Path, state: _LeaseState, *, resume_required: bool | None = None) -> None:
    """Persist the lease document atomically under a UNIQUE temp name (O-5)."""
    _atomic_write_json(_pause_state_path(root), state.document(resume_required=resume_required))


def _write_owner_marker(root: Path) -> None:
    """The owner marker file stays a content-free sentinel (ADR-7: no generation).

    Any legacy reader therefore keeps seeing the same sentinel it always saw; the
    authoritative owner record lives in the refcount document.
    """
    path = _pause_owner_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("filing-fetch", encoding="utf-8")


def _clear_pause_lease(root: Path) -> None:
    try:
        _pause_state_path(root).unlink(missing_ok=True)
        _pause_owner_path(root).unlink(missing_ok=True)
    except OSError:
        pass


def _read_pause_entries(root: Path) -> list[dict[str, Any]]:
    """Compatibility accessor retained for callers outside this module.

    It fails closed exactly like the protocol path: an unreadable store is an
    empty list ONLY when the file genuinely does not exist.
    """
    state = _read_pause_state(root)
    return list(state.entries)


def _write_pause_entries(root: Path, entries: list[dict[str, Any]]) -> None:
    """Compatibility accessor: rewrites the entry list, preserving the rest."""
    state = _read_pause_state(root)
    state.entries = list(entries)
    _write_pause_state(root, state)


def _prune_pause_entries(
    root: Path, *, timeout: float, stats: dict[str, Any] | None = None
) -> list[dict[str, Any]]:
    """Compatibility accessor: drop entries whose pid provably cannot be the holder.

    A leased process can be reclaimed only on positive death/reuse evidence; an
    UNKNOWN verdict keeps the entry (``unknown != dead``).  The pruned document is
    persisted, because a prune that is not written is a dropped observation.
    """
    if timeout <= 0:
        raise ValueError("pid liveness probe requires a positive phase budget")
    state = _read_pause_state(root)
    kept: list[dict[str, Any]] = []
    changed = False
    for entry in state.entries:
        if stats is not None:
            stats["liveness_calls"] = int(stats.get("liveness_calls") or 0) + 1
        verdict = _probe_entry_verdict(entry, probe_timeout=min(_PID_PROBE_MAX_SECONDS, timeout))
        if verdict.verdict in {"dead", "reused"}:
            changed = True
            continue
        kept.append(entry)
    if changed:
        state.entries = kept
        _write_pause_state(root, state)
    return kept


class PausedWorkerScope:
    """Context manager pausing the worker around one catalog download.

    I-04-D: the whole enter path is ONE critical section (ADR-11) - the worker
    status and the lease document are both read inside it, so no branch can act on
    a snapshot another participant has already invalidated.  Concretely:

    - Worker disabled -> no-op.
    - Already paused AND held by this tool (``schema=2`` with live entries) ->
      join the refcount so the last participant resumes it.
    - Already paused and NOT held by this tool -> respect the user's pause: no
      lease, no pause, no resume and no evidence left behind.
    - Paused by a dead participant that left a resume obligation -> take the cycle
      over, resume first, then pause for ourselves.
    - Otherwise -> open a new generation, pause, and confirm the pause landed.

    A crash is no longer "self-healing" by guesswork: reclamation needs positive
    evidence (dead pid, or the same pid with a different process incarnation).
    """

    def __init__(
        self,
        *,
        root: Path,
        command_prefix: list[str],
        enabled: bool,
        graceful_timeout_seconds: float,
        resume_wait_seconds: float,
        deadline: float,
        stats: dict[str, Any] | None = None,
    ) -> None:
        self.root = root
        self.command_prefix = command_prefix
        self.enabled = enabled
        self.graceful = graceful_timeout_seconds
        self.resume_wait = resume_wait_seconds
        self.deadline = deadline
        self.action = "none"
        self._first = False
        self.stats = stats
        self.lease_id = ""
        self.lease_held = False
        self._lock = _LeaseLocked(self)
        self._lock_waits = 0
        self._lock_acquisitions = 0
        self._max_lock_wait = 0.0
        self._ledger_writes = 0
        self._release_done = False
        self._cleanup_started: float | None = None
        self._cleanup_status = ""
        self._cleanup_failure = ""
        self._resume_reason = ""
        self._transfer_to = ""
        self._proc_start_time = ""

    # -- budgets ---------------------------------------------------------

    def _request_remaining(self) -> float:
        """Budget for a REQUEST-stage subcall (I-04-A D1/D3).

        Deliberately has no floor: once the deadline has passed this is <= 0 and
        the caller must NOT issue the call.  The old ``max(10.0, ...)`` minted a
        fresh 10 second request budget after the deadline (F-D2) - a pure status
        query is still a request, so exempting it would reopen the hole.
        """
        return min(self.deadline - time.monotonic(), _WORKER_STATUS_TIMEOUT)

    def _cleanup_timeout(self) -> float:
        """Independent cleanup budget C (I-04-A D2).

        Ownership restoration is not a request: it does not borrow the request
        deadline, and it is capped by the signed formula so a user-raised
        --worker-resume-wait-seconds cannot make it time out by construction.
        """
        return max(
            _CLEANUP_BUDGET_MIN_SECONDS,
            2.0 * self.resume_wait + self.graceful,
        )

    def _cleanup_remaining(self) -> float:
        """The cleanup budget still available to THIS subcall.

        C is a PHASE budget (I-04-A D2), not a per-call allowance, so the second
        critical section must not mint a fresh C: it receives what the phase has
        left.  Reading it here (rather than capturing it once) keeps a probe-heavy
        release inside the same total.
        """
        started = getattr(self, "_cleanup_started", None)
        if started is None:
            return self._cleanup_timeout()
        return max(0.0, self._cleanup_timeout() - (time.monotonic() - started))

    def _lock_budget(self, phase_budget: float) -> float:
        """ADR-2: ``lock_budget_for(x) = min(x, LOCK_MAX_SECONDS)``.

        The lease layer only ever CONSUMES phase budget; it never creates one
        (I-04-C ADR-6).  A non-positive budget refuses to wait at all, and the
        caller must turn that into ``lease_lock_timeout``.
        """
        return min(phase_budget, LOCK_MAX_SECONDS)

    # -- the one lock ----------------------------------------------------

    def _acquire_lock(self) -> None:
        if self._lock.held:
            return
        budget = self._lock_budget(self._lock_phase_budget())
        if budget <= 0:
            raise _LeaseScopeError(
                "lease_lock_timeout",
                f"lease lock not attempted: the phase budget is {budget:.3f}s "
                f"(<= 0), and the lease layer never mints budget (ADR-6). "
                f"lock={_lease_lock_path(self.root)}",
            )
        path = _lease_lock_path(self.root)
        path.parent.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()
        deadline = started + budget
        handle = os.open(str(path), os.O_RDWR | os.O_CREAT, 0o644)
        try:
            while True:
                locked_now = _try_lock_byte(handle)
                if locked_now:
                    break
                if time.monotonic() >= deadline:
                    raise _LeaseScopeError(
                        "lease_lock_timeout",
                        f"lease lock {path} was held by another participant for "
                        f"{time.monotonic() - started:.3f}s (budget {budget:.3f}s). "
                        "Nothing was written and no worker command was issued. "
                        "Inspect for a wedged filing-fetch process, then retry",
                    )
                time.sleep(_LOCK_POLL_SECONDS)
        except BaseException:
            os.close(handle)
            raise
        waited = time.monotonic() - started
        self._lock._handle = handle
        self._lock_waits += 1
        self._lock_acquisitions += 1
        if waited > self._max_lock_wait:
            self._max_lock_wait = waited
        if self.stats is not None:
            self.stats["lease_lock_waits"] = int(self.stats.get("lease_lock_waits") or 0) + 1
            self.stats["lease_lock_acquisitions"] = (
                int(self.stats.get("lease_lock_acquisitions") or 0) + 1
            )
            self.stats["lease_lock_max_wait_seconds"] = round(self._max_lock_wait, 3)
        _lease_journal(
            self.root, "lease_lock_acquired", wait_seconds=round(waited, 4), budget=round(budget, 4)
        )

    def _lock_phase_budget(self) -> float:
        remaining = self._request_remaining()
        if remaining > 0:
            return remaining
        cleanup = self._cleanup_remaining()
        if cleanup > 0:
            return cleanup
        return remaining

    def _release_lock(self, handle: Any) -> None:
        if handle is None:
            return
        try:
            try:
                _unlock_byte(handle)
            except OSError:
                pass
        finally:
            try:
                os.close(handle)
            except OSError:
                pass

    # -- worker CLI ------------------------------------------------------

    def _run(self, subcommand: str, *args: str, timeout: float) -> dict[str, Any]:
        return _run_company_wiki_json(
            command=[*self.command_prefix, subcommand, *args],
            root=self.root,
            timeout_seconds=timeout,
            action=subcommand,
            stats=self.stats,
        )

    def _worker_status(self, timeout: float) -> dict[str, Any]:
        return self._run("worker-status", timeout=timeout)

    def _worker_pause(self, timeout: float) -> dict[str, Any]:
        return self._run(
            "worker-pause",
            "--graceful-timeout-seconds",
            str(self.graceful),
            timeout=timeout,
        )

    def _worker_resume(self, timeout: float) -> dict[str, Any]:
        return self._run(
            "worker-resume",
            "--wait-seconds",
            str(self.resume_wait),
            timeout=timeout,
        )

    # -- lease helpers (all locked) --------------------------------------

    def _prune_locked(self, state: _LeaseState, *, probe_timeout: float) -> _LeaseView:
        """Split entries into ``(live, reclaimed)`` with the verdict kept as evidence."""
        live: list[dict[str, Any]] = []
        live_verdicts: list[_ProbeResult] = []
        reclaimed: list[dict[str, Any]] = []
        reclaimed_verdicts: list[_ProbeResult] = []
        for entry in state.entries:
            if self.stats is not None:
                self.stats["liveness_calls"] = int(self.stats.get("liveness_calls") or 0) + 1
            result = _probe_entry_verdict(entry, probe_timeout=probe_timeout)
            if result.verdict in {"dead", "reused"}:
                reclaimed.append(entry)
                reclaimed_verdicts.append(result)
                continue
            live.append(entry)
            live_verdicts.append(result)
        return _LeaseView(state, live, live_verdicts, reclaimed, reclaimed_verdicts)

    def _log_pruned(self, view: _LeaseView, *, phase: str) -> None:
        if not view.reclaimed:
            return
        _lease_journal(
            self.root,
            "pruned",
            phase=phase,
            count=len(view.reclaimed),
            detail=[
                {"lease_id": e.get("lease_id"), "pid": e.get("pid"), "verdict": v.verdict}
                for e, v in zip(view.reclaimed, view.reclaimed_verdicts)
            ],
        )

    def _classify_locked(self, state: _LeaseState, *, probe_timeout: float) -> list[dict[str, Any]]:
        """Validate liveness inside the critical section; EVERY unknown fails closed."""
        view = self._prune_locked(state, probe_timeout=probe_timeout)
        self._log_pruned(view, phase="acquire")
        state.entries = view.live
        unknown = view.unknowns
        if unknown:
            detail = ", ".join(
                f"lease_id={e.get('lease_id')} pid={e.get('pid')}" for e in unknown
            )
            raise _LeaseScopeError(
                "lease_conflict_unknown",
                f"a lease holder's liveness is UNKNOWN ({detail}) - not dead, not alive. "
                "Nothing was written and no worker command was issued. Re-run once the "
                "pid probe works, or inspect the refcount by hand",
            )
        return view.live

    def _persist_locked(self, state: _LeaseState, *, resume_required: bool | None = None) -> None:
        try:
            _write_pause_state(self.root, state, resume_required=resume_required)
        except OSError as exc:
            # The caller must never be told "you own the first lease" after a
            # failed ledger write: that is exactly how the legacy code lost an
            # owner while still acting like one.
            raise _LeaseScopeError(
                "lease_state_write_failed",
                f"pause refcount write to {_pause_state_path(self.root)} failed: {exc}. "
                "This process does NOT hold a lease",
            ) from exc
        self._ledger_writes += 1

    def _write_owner_marker_locked(self) -> None:
        try:
            _write_owner_marker(self.root)
        except OSError:
            # ADR-5 W1: the marker is only a compatibility sentinel; the
            # authoritative owner is the record inside the refcount document, so a
            # read-only .source_catalog must not fail the whole request.
            _lease_journal(self.root, "owner_marker_missing", path=str(_pause_owner_path(self.root)))

    def _is_our_owner(self, state: _LeaseState) -> bool:
        """Whether the pause cycle belongs to THIS process incarnation (ADR-10e).

        Deliberately not "owner.lease_id == my lease_id": inside one process a second
        scope legitimately re-enters the cycle the first scope opened, and the owner
        record names the first scope's lease.  Ownership is per incarnation, so the
        test is whether the owner record points at one of this incarnation's leases.
        """
        owner = state.owner or {}
        owner_lease = owner.get("lease_id")
        if not owner_lease:
            return False
        if owner_lease == self.lease_id:
            return True
        return bool(
            owner.get("boot_uuid")
            and owner.get("boot_uuid") == _boot_uuid()
            and isinstance(owner.get("pid"), int)
            and owner.get("pid") == os.getpid()
            and any(entry.get("lease_id") == owner_lease for entry in state.entries)
        )

    def _probe_owner_death(self, state: _LeaseState, *, probe_timeout: float) -> tuple[bool, str]:
        """R4's only admissible evidence: a POSITIVE death/reuse verdict for the owner.

        ``owner_record_missing`` is deliberately NOT death evidence in either
        direction.  It is indistinguishable from an ownership record a third party
        (or a user's manual worker-pause) removed, and in that case a resume would
        undo a human's pause.  R5 therefore wins: fail closed.
        """
        owner = state.owner or {}
        owner_lease = owner.get("lease_id")
        if not owner_lease:
            return False, "owner_record_missing"
        for entry in state.entries:
            if entry.get("lease_id") == owner_lease:
                return False, "owner_lease_still_live"
        pid = owner.get("pid")
        if not isinstance(pid, int):
            return False, "owner_record_has_no_pid"
        if pid == os.getpid() and owner.get("boot_uuid") == _boot_uuid():
            return False, "owner_is_this_incarnation"
        try:
            alive, observed = _pid_is_alive_with_start_time(pid, timeout=probe_timeout)
        except subprocess.TimeoutExpired:
            return False, "owner_probe_timeout"
        except Exception as exc:  # noqa: BLE001 - unknown never authorises a resume
            return False, f"owner_probe_error:{type(exc).__name__}"
        if not alive:
            return True, "owner_probe:dead"
        recorded = owner.get("os_start_time") or ""
        if recorded and observed and recorded != observed:
            return True, "owner_probe:pid_reuse"
        if recorded and observed == "0":
            return True, "owner_probe:dead"
        return False, "owner_probe:alive"

    def _probe_payload(self) -> dict[str, Any]:
        raw = os.environ.get("I04D_PROBE_INJECT")
        if not raw:
            return {}
        try:
            payload = json.loads(raw)
        except ValueError:
            return {}
        return payload if isinstance(payload, dict) else {}

    def _conflict_payload_changed(self, state: _LeaseState, *, probe_timeout: float) -> bool:
        """True when ANY lease holder is no longer provably the same live process."""
        for entry in state.entries:
            result = _probe_entry_verdict(entry, probe_timeout=probe_timeout)
            if result.verdict in {"dead", "reused", "unknown"}:
                return True
        return False

    # -- enter -----------------------------------------------------------

    def __enter__(self) -> "PausedWorkerScope":
        if not self.enabled:
            self.action = "disabled"
            return self
        try:
            self.lease_id = _new_lease_id()
            self._proc_start_time = _sys_process_start_time()
            with self._lock as locked:
                _i04d_hook("enter-acquired", root=self.root, payload={"lease_id": self.lease_id})
                locked._scope._enter_locked()
        except _LeaseScopeError as exc:
            self.action = exc.code
            _lease_journal(self.root, "lease_fail_closed", code=exc.code, detail=exc.message)
            raise exc.filing_error() from exc
        return self

    def _enter_locked(self) -> None:
        remaining = self._request_remaining()
        if remaining <= 0:
            # I-04-A D3: a request-stage call after the deadline is forbidden.  No
            # status, no pause, therefore no cleanup obligation.
            self.action = "deadline_exhausted"
            return
        try:
            status = self._worker_status(remaining)
        except BaseException as exc:
            raise
        state = _read_pause_state(self.root)
        _i04d_hook(
            "enter-read",
            root=self.root,
            payload={
                "desired_state": status.get("desired_state"),
                "runtime_state": status.get("runtime_state"),
                "generation": state.generation,
                "entries": len(state.entries),
            },
        )
        desired = status.get("desired_state")
        runtime = status.get("runtime_state")
        # ADR-9: the paused-or-leased branch is evaluated BEFORE the runtime_state
        # guard.  Our own pause necessarily turns runtime_state into "stopped", so the
        # legacy order made the join/takeover paths unreachable in production.
        if desired == "paused" or state.entries:
            pass
        elif runtime != "running":
            # Neither paused nor leased, and not running: there is no pause to join,
            # so there is nothing to attribute - do not write anything.
            self.action = "worker_stopped"
            return
        probe_timeout = min(self._request_remaining(), _PID_PROBE_MAX_SECONDS, _PROBE_SOFT_CAP_SECONDS)
        if probe_timeout <= 0:
            raise _LeaseScopeError(
                "lease_lock_timeout",
                "the request budget ran out before the lease liveness probe could run; "
                "nothing was written and no worker command was issued",
            )
        live = self._classify_locked(state, probe_timeout=probe_timeout)
        _i04d_hook(
            "enter-classified",
            root=self.root,
            payload={"live": len(live), "reclaimed": len(state.entries) - len(live)},
        )
        self._dispatch_locked(state, live, status=status, probe_timeout=probe_timeout)
        # LAST point of the enter critical section: every branch above leaves THIS
        # incarnation owning a lease by the time the hook runs, so a schedule can
        # observe "our lease is really in the ledger" without pinning which branch
        # was taken.  Unset I04D_HOOKS makes it a no-op.
        _i04d_hook("enter-complete", root=self.root, payload={"lease_id": self.lease_id})

    def _dispatch_locked(
        self,
        state: _LeaseState,
        live: list[dict[str, Any]],
        *,
        status: dict[str, Any],
        probe_timeout: float,
    ) -> None:
        desired = status.get("desired_state")
        if desired not in {"paused", "stopped"}:
            self._fresh_cycle_locked(state, live, resume_required=False)
            return
        if not live and not state.resume_required and self._respect_user_pause_locked(state):
            # ADR-8: the worker is paused, the ledger is EMPTY and nobody owes a
            # resume, so this pause is not ours.  It is a user/external pause: leave
            # it completely alone - no lease, no pause, no resume - and let the caller
            # continue with the explicit opt-in the CLI already carries.
            self.action = "respect_paused"
            _lease_journal(self.root, "respect_paused", lease_id=self.lease_id)
            return
        if self._withdraw_orphan_pause_locked(status):
            self._fresh_cycle_locked(state, live, resume_required=False)
            return
        if not live:
            if state.resume_required:
                self._takeover_cycle_locked(state)
                return
            self._fresh_cycle_locked(state, live, resume_required=False)
            return
        if state.owner is None:
            # W1: a crash between the refcount write and the owner marker used to
            # make the next participant read this as a USER pause and never resume.
            # The lease document - not the marker file - is the evidence.
            self._join_cycle_locked(state, live)
            return
        if self._is_our_owner(state):
            # Our own lease owns the cycle, so this is a re-entry into a cycle this
            # incarnation already established (same-pid nesting) - join it rather
            # than pause a second time (ADR-9/ADR-9b).
            self._join_cycle_locked(state, live)
            return
        if self._owner_lease_live(state, live):
            # ADR-9b: a LIVE holder keeps the cycle alive, so this request JOINS it
            # instead of stopping the worker a second time.  The cycle is already
            # paused, so a peer's request needs no pause of its own.  (This is also what
            # makes the mixed-fleet/foreign-live holder case safe: we add a lease and
            # touch nothing else, and the ownership record is left exactly as found.)
            _lease_journal(
                self.root,
                "joined_live_holder",
                lease_id=self.lease_id,
                owner=(state.owner or {}).get("lease_id"),
                generation=state.generation,
            )
            self._join_cycle_locked(state, live)
            return
        # R4: the owner is no longer in the ledger.  Take the cycle over ONLY when
        # BOTH hold:
        #   (a) the ownership record belongs to THIS process lineage (same boot_uuid
        #       and pid), i.e. it is our own crashed attempt and not a third party; and
        #   (b) that lineage is provably dead (never a timeout guess).
        # A foreign record that merely names a dead pid is NOT ours to close: taking it
        # over would resume a pause this tool never created, so it stays R5 - the
        # evidence is kept byte-for-byte and the reader is told exactly why.
        age = self._owner_age_seconds(state)
        claimable = (
            self._owner_is_our_lineage(state)
            or not state.owner
            or not state.owner.get("lease_id")
        )
        if not claimable:
            owner = state.owner or {}
            raise _LeaseScopeError(
                "lease_conflict_unknown",
                "the worker is paused and the ownership record is not attributable to this "
                f"process lineage (owner boot_uuid={owner.get('boot_uuid')!r}, "
                f"pid={owner.get('pid')!r}); nothing was written and no worker command "
                "was issued. This is the fail-closed terminal state: resolve it with "
                "`worker-resume` by hand, or let the owning tool close its own cycle",
            )
        provably_dead, why = self._probe_owner_death(state, probe_timeout=probe_timeout)
        if not provably_dead:
            raise _LeaseScopeError(
                "lease_conflict_unknown",
                "the worker is paused and this lineage's ownership record is not provably "
                f"dead ({why}) after {age:.1f}s; nothing was written and no worker command "
                "was issued. Inspect the refcount by hand before retrying",
            )
        _lease_journal(self.root, "owner_provably_dead", why=why, owner=state.owner)
        self._takeover_cycle_locked(state)
        return

    def _owner_is_our_lineage(self, state: _LeaseState) -> bool:
        """Whether the owner record is this process incarnation's own record."""
        owner = state.owner or {}
        return bool(
            owner.get("boot_uuid")
            and owner.get("boot_uuid") == _boot_uuid()
            and isinstance(owner.get("pid"), int)
            and owner.get("pid") == os.getpid()
        )

    def _owner_age_seconds(self, state: _LeaseState) -> float:
        """Diagnostic only: how long the pause has been unattributed."""
        del state  # the record carries no timestamp; the journal has the real timeline
        return 0.0

    def _respect_user_pause_locked(self, state: _LeaseState) -> bool:
        """ADR-8: paused with no tool-held lease, no obligation and no owner record.

        The owner RECORD (not the marker file) is the authority (ADR-5 W1): if a record
        exists we treat the cycle as a crashed one of ours and recover it instead of
        silently adopting a human's pause.
        """
        return not state.entries and not state.owner

    def _owner_lease_live(self, state: _LeaseState, live: list[dict[str, Any]]) -> bool:
        owner_lease = (state.owner or {}).get("lease_id")
        return any(entry.get("lease_id") == owner_lease for entry in live)

    def _withdraw_orphan_pause_locked(self, status: dict[str, Any]) -> bool:
        """ADR-9b: a pause we left behind while the worker is still RUNNING.

        The cycle is not usable (no pending pause to wait for), so it is withdrawn
        and the caller opens a fresh one; a request never sees two pauses.
        """
        if not _lease_owns_cycle(status.get("pause_action")):
            return False
        if status.get("runtime_state") == "running":
            # `action` is deliberately NOT set here: the caller opens a fresh cycle
            # and that outcome is the one the request must report (ADR-9b).
            _lease_journal(self.root, "withdraw_orphan_pause", lease_id=self.lease_id)
            return True
        return False

    def _withdraw_cycle_locked(self, state: _LeaseState, status: str) -> None:
        """Drop the owner's lease/ownership and clear any obligation."""
        state.entries = [e for e in state.entries if e.get("lease_id") != self.lease_id]
        if self._is_our_owner(state):
            state.owner = None
        state.resume_required = False
        state.resume_lease_id = ""
        self._persist_locked(state, resume_required=False)
        self.lease_held = False
        self._cleanup_failure = status

    def _fresh_cycle_locked(
        self, state: _LeaseState, live: list[dict[str, Any]], *, resume_required: bool
    ) -> None:
        """T5: a brand-new pause cycle with a fresh generation (ADR-12)."""
        state.generation = state.generation + 1
        state.entries = list(live) + [
            _lease_entry(self, state, invocations=1, joined=False)
        ]
        state.resume_required = False
        state.resume_lease_id = ""
        state.owner = self._owner_record(state)
        self._persist_locked(state, resume_required=False)
        self.lease_held = True
        self._first = True
        _i04d_hook(
            "enter-written",
            root=self.root,
            payload={"lease_id": self.lease_id, "generation": state.generation},
        )
        _i04d_hook(
            "after-refcount-before-owner",
            root=self.root,
            payload={"lease_id": self.lease_id, "generation": state.generation},
        )
        self._write_owner_marker_locked()
        self.action = "paused_by_us"
        remaining = self._request_remaining()
        if remaining <= 0:
            self._withdraw_cycle_locked(state, "deadline_exhausted")
            self.action = "deadline_exhausted"
            return
        try:
            self._worker_pause(min(remaining, _WORKER_STATUS_TIMEOUT))
        except FilingFetchError as exc:
            self._withdraw_cycle_locked(state, f"pause_failed:{exc.code}")
            try:
                self._worker_resume(self._cleanup_remaining())
            except FilingFetchError:
                pass  # best effort; the original pause error is the one reported
            raise _LeaseScopeError(
                "worker_pause_failed",
                f"worker-pause failed: {exc}",
                cleanup=f"failed:pause_failed:{exc.code}",
            ) from exc
        if not self._confirm_pause_locked():
            self._withdraw_cycle_locked(state, "pause_unconfirmed")
            self.action = "pause_unconfirmed"
            _lease_journal(self.root, "pause_unconfirmed", lease_id=self.lease_id)
            return
        _i04d_hook(
            "after-pause-confirm",
            root=self.root,
            payload={"lease_id": self.lease_id, "generation": state.generation},
        )

    def _join_cycle_locked(self, state: _LeaseState, live: list[dict[str, Any]]) -> None:
        """T4: join the cycle someone else opened - never a second pause (ADR-9b)."""
        invocations = sum(1 for e in live if e.get("boot_uuid") == _boot_uuid()) + 1
        state.entries = list(live) + [
            _lease_entry(self, state, invocations=invocations, joined=True)
        ]
        state.owner = self._owner_record(state)
        self._persist_locked(state, resume_required=False)
        self._write_owner_marker_locked()
        self.lease_held = True
        self.action = "joined"

    def _takeover_cycle_locked(self, state: _LeaseState) -> None:
        """T6/W4: inherit a dead participant's pause, resume first, then re-pause.

        The claim order matters: write the lease and take the ownership FIRST, so
        the resume obligation is never left un-owned if this process dies mid-way.
        """
        state.entries = list(state.entries) + [
            _lease_entry(self, state, invocations=1, joined=False)
        ]
        state.owner = self._owner_record(state)
        self._persist_locked(state, resume_required=state.resume_required)
        self._write_owner_marker_locked()
        self.lease_held = True
        self.action = "takeover_resumed"
        _i04d_hook(
            "takeover-claimed",
            root=self.root,
            payload={"lease_id": self.lease_id, "generation": state.generation},
        )
        try:
            self._worker_resume(self._cleanup_remaining())
        except FilingFetchError as exc:
            raise _LeaseScopeError(
                "lease_resume_takeover_failed",
                f"takeover resume failed: {exc}. The worker is still paused; run "
                "`worker-resume` by hand (the obligation and the owner record are "
                "preserved for the next participant)",
                cleanup=f"failed:resume_takeover:{exc.code}",
                resume_code=exc.code,
            ) from exc
        state.resume_required = False
        state.resume_lease_id = ""
        state.generation = state.generation + 1
        state.entries = [e for e in state.entries if e.get("lease_id") == self.lease_id]
        self._persist_locked(state, resume_required=False)
        self.action = "paused_by_us"
        try:
            self._worker_pause(self._cleanup_remaining())
        except FilingFetchError as exc:
            raise _LeaseScopeError(
                "worker_pause_failed",
                f"worker-pause after takeover failed: {exc}",
                cleanup=f"failed:pause_failed:{exc.code}",
            ) from exc
        if not self._confirm_pause_locked():
            self.action = "pause_unconfirmed"
            _lease_journal(self.root, "pause_unconfirmed", lease_id=self.lease_id, phase="takeover")

    def _confirm_pause_locked(self) -> bool:
        """ADR-10d: the takeover/fresh pause is only real once the status says so."""
        remaining = self._request_remaining()
        if remaining <= 0:
            return False
        try:
            status = self._worker_status(min(remaining, _WORKER_STATUS_TIMEOUT))
        except FilingFetchError:
            return False
        return status.get("desired_state") == "paused" and status.get("runtime_state") == "stopped"

    def _owner_record(self, state: _LeaseState) -> dict[str, Any]:
        return {
            "lease_id": self.lease_id,
            "generation": state.generation,
            "pid": os.getpid(),
            "boot_uuid": _boot_uuid(),
            "os_start_time": self._proc_start_time,
        }

    # -- exit ------------------------------------------------------------

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        # I-04-A D5: the pause outcome is reported even when no cleanup is owed.
        started = time.monotonic()
        self._cleanup_started = started
        self._cleanup_failure = ""
        self._resume_reason = ""
        self._transfer_to = ""
        if self.stats is not None:
            self.stats["pause_action"] = self.action
        if not self.lease_held:
            if self.stats is not None:
                self.stats["cleanup_status"] = "not_needed"
            return
        try:
            with self._lock:
                self._release_locked()
        except _LeaseScopeError as exc:
            self._cleanup_failure = exc.cleanup or f"failed:{exc.code}"
            _lease_journal(self.root, "release_fail_closed", code=exc.code, detail=exc.message)
            if exc.code == "lease_state_write_failed" and self.action in {"paused_by_us", "takeover_resumed"}:
                # The lease WAS written earlier and the worker IS paused: only the
                # release ledger failed, so keep the request result and say so.
                self.action = "release_fail_closed"
            elif self.action not in LEASE_ACTION_FAIL_CLOSED:
                self.action = "release_fail_closed"
        except subprocess.TimeoutExpired:
            self._cleanup_failure = "failed:resume_timeout"
            _lease_journal(self.root, "release_fail_closed", code="resume_timeout")
        finally:
            if self._cleanup_failure:
                self._print_release_guidance()
            if self.stats is not None:
                self.stats["cleanup_calls"] = int(self.stats.get("cleanup_calls") or 0) + 1
                self.stats["cleanup_status"] = self._cleanup_failure
                self.stats["cleanup_elapsed_seconds"] = round(time.monotonic() - started, 3)
                self.stats["lease_lock_acquisitions"] = self._lock_acquisitions
                self.stats["lease_lock_max_wait_seconds"] = round(self._max_lock_wait, 3)
                self.stats["lease_ledger_writes"] = self._ledger_writes
                if self._resume_reason:
                    self.stats["lease_resume_reason"] = self._resume_reason
                if self._transfer_to:
                    self.stats["lease_owner_transferred_to"] = self._transfer_to
            # I-04-B carry 3: the cleanup PHASE wall clock is REPORTED, never
            # bounded by an acceptance cap.
            _lease_journal(
                self.root,
                "release",
                action=self.action,
                cleanup_status=self._cleanup_failure or "not_needed",
                resume_reason=self._resume_reason,
                transferred_to=self._transfer_to,
                lock_acquisitions=self._lock_acquisitions,
                max_lock_wait_seconds=round(self._max_lock_wait, 4),
                phase_wall_seconds=round(time.monotonic() - started, 4),
            )

    def _release_locked(self) -> None:
        state = _read_pause_state(self.root)
        probe_timeout = min(
            self._cleanup_remaining(), _PID_PROBE_MAX_SECONDS, _PROBE_SOFT_CAP_SECONDS
        )
        if probe_timeout <= 0:
            raise _LeaseScopeError(
                "lease_lock_timeout",
                "the cleanup budget ran out before the release liveness probe",
                cleanup="failed:lease_lock_timeout",
            )
        view = self._prune_locked(state, probe_timeout=probe_timeout)
        self._log_pruned(view, phase="release")
        mine = [e for e in view.live if e.get("lease_id") == self.lease_id]
        remaining = [e for e in view.live if e.get("lease_id") != self.lease_id]
        if not mine:
            # Nothing of ours is in the ledger any more (a peer reclaimed the dead
            # incarnation, or this scope never got the lease written). A release is
            # NOT authorisation to resume: that decision needs the R1-R5 evidence.
            if view.reclaimed:
                state.entries = remaining
                self._persist_locked(state, resume_required=False)
            self._release_done = True
            self.action = "released_noop"
            _lease_journal(self.root, "release_noop", lease_id=self.lease_id)
            return
        # The release decision point.  The test-only fence sits HERE, immediately
        # before the R1-R5 decision, so a schedule can pin "this is the ledger A is
        # deciding on" while A still holds the lock.  A scope that holds no lease
        # returns above this line, so the fence fires exactly once per lease.
        _i04d_hook(
            "release-read",
            root=self.root,
            payload={
                "lease_id": self.lease_id,
                "remaining": len(remaining),
                "owner": (state.owner or {}).get("lease_id"),
                "resume_required": state.resume_required,
            },
        )
        self._release_common_locked(state, remaining)

    def _release_common_locked(
        self,
        state: _LeaseState,
        remaining: list[dict[str, Any]],
    ) -> None:
        is_owner = self._is_our_owner(state)
        if remaining:
            # R1: the cycle lives on. If the departing lease was the owner, the
            # ownership MOVES to a surviving lease (ADR-10e) so a later release can
            # still prove who is responsible - an owner record pointing at a lease
            # that is no longer in the ledger is exactly the dead end F-L2a showed.
            if is_owner:
                heir = min(remaining, key=lambda entry: str(entry.get("lease_id")))
                state.owner = {
                    "lease_id": heir.get("lease_id"),
                    "generation": state.generation,
                    "pid": heir.get("pid"),
                    "boot_uuid": heir.get("boot_uuid") or "",
                    "os_start_time": heir.get("os_start_time") or "",
                }
                self._transfer_to = str(heir.get("lease_id"))
                _lease_journal(
                    self.root,
                    "ownership_transferred",
                    to=self._transfer_to,
                    generation=state.generation,
                    dead_able=bool(heir.get("os_start_time")),
                )
            state.entries = remaining
            self._persist_locked(state, resume_required=False)
            self._release_done = True
            self.action = "released_joined"
            _lease_journal(
                self.root,
                "released_joined",
                lease_id=self.lease_id,
                transferred_to=self._transfer_to,
            )
            return
        # last participant: entry from R2..R5 (ADR-10)
        if is_owner:
            reason = "owner_is_me"
        elif state.resume_required:
            # R3: the obligation is the tool's own record, so it is attributable and
            # the last participant INHERITS it rather than abandoning it.
            reason = "inherited_obligation"
        else:
            provably_dead, why = self._probe_owner_death(state, probe_timeout=self._cleanup_remaining())
            if provably_dead and self._owner_is_our_lineage(state):
                # R4: our own lineage's owner is provably dead, so closing the cycle
                # (and stating why) is ours to do.
                reason = why
            elif provably_dead:
                # The record names a provably dead holder that is NOT ours: the pause
                # may belong to a user or another tool, so R5 keeps the evidence and
                # does not resume.  This is the F-L8d cell of the branch table.
                state.entries = []
                self._persist_locked(state, resume_required=False)
                self._release_done = True
                self.action = "released_owner_changed"
                self._cleanup_failure = f"failed:owner_evidence_changed:{why}:foreign_lineage"
                _lease_journal(
                    self.root,
                    "released_owner_changed",
                    lease_id=self.lease_id,
                    why=why,
                    owner=state.owner,
                )
                return
            elif why in {"owner_record_missing", "owner_record_has_no_pid"}:
                # No ownership evidence at all: the worker is paused, the ledger is
                # empty and nothing says this pause was ours.  That is R5 - fail
                # closed, keep whatever evidence exists, and say exactly why.
                state.entries = []
                self._persist_locked(state, resume_required=False)
                self._release_done = True
                self.action = "released_owner_changed"
                self._cleanup_failure = f"failed:owner_evidence_changed:{why}"
                _lease_journal(
                    self.root,
                    "released_owner_changed",
                    lease_id=self.lease_id,
                    why=why,
                    owner=state.owner,
                )
                return
            else:
                reason = why
        state.entries = []
        self._persist_locked(state, resume_required=True)
        self._resume_reason = reason
        self._release_done = True
        _i04d_hook(
            "after-release-persist-before-resume",
            root=self.root,
            payload={"lease_id": self.lease_id, "reason": reason, "generation": state.generation},
        )
        state.resume_lease_id = self.lease_id
        state.resume_required = True
        if not self._conflict_payload_changed(state, probe_timeout=self._cleanup_remaining()):
            try:
                self._worker_resume(self._cleanup_remaining())
            except FilingFetchError as exc:
                self._cleanup_failure = f"failed:{exc.code}"
                self.action = "released_last_resume_failed"
                _lease_journal(
                    self.root, "resume_failed", lease_id=self.lease_id, code=exc.code
                )
                return
            except subprocess.TimeoutExpired:
                self._cleanup_failure = "failed:resume_timeout"
                self.action = "released_last_resume_failed"
                return
        else:
            _lease_journal(
                self.root,
                "resume_skipped_conflict_payload",
                lease_id=self.lease_id,
                detail="an injected probe answer says the holder is gone; no resume",
            )
        self.action = "released_last"
        state.resume_required = False
        state.resume_lease_id = ""
        state.owner = None
        state.entries = []
        try:
            _clear_pause_lease(self.root)
        except OSError:
            pass
        _lease_journal(
            self.root,
            "released_last",
            lease_id=self.lease_id,
            reason=self._resume_reason,
            generation=state.generation,
        )

    def _print_release_guidance(self) -> None:
        """R5 / O-1: a human must be able to release a stuck lease without guessing."""
        state_path = _pause_state_path(self.root)
        owner_path = _pause_owner_path(self.root)
        state_text = ""
        try:
            state_text = state_path.read_text(encoding="utf-8")
        except OSError:
            state_text = "<refcount file is absent or unreadable>"
        print(
            "[filing-fetch] worker lease NOT released: "
            f"{self._cleanup_failure}\n"
            f"[filing-fetch]   refcount : {state_path}\n"
            f"[filing-fetch]   owner    : {owner_path} "
            f"(exists={owner_path.exists()})\n"
            f"[filing-fetch]   raw state: {state_text}\n"
            "[filing-fetch]   to release by hand:\n"
            "[filing-fetch]     1) confirm no filing-fetch download is running "
            "(tasklist /FI \"IMAGENAME eq python.exe\")\n"
            "[filing-fetch]     2) if the worker should keep running: "
            "python -m company_wiki.source_catalog.cli worker-resume\n"
            "[filing-fetch]     3) only if step 2 says it is already running: "
            f"delete {state_path} and {owner_path}\n"
            "[filing-fetch]     4) never delete a lease whose owner record you have "
            "not read in full",
            file=sys.stderr,
        )


def _try_lock_byte(handle: int) -> bool:
    """Try to take the 1-byte exclusive lock at offset 0 without blocking.

    ADR-1 chose an OS byte-range lock precisely because the kernel, not this code,
    decides whether the holder is still alive: a process that dies (including
    TerminateProcess) releases the lock, so there is no "break the stale lock"
    step - and therefore no window in which two processes each believe they hold it.
    """
    if os.name == "nt":
        import msvcrt

        try:
            handle.seek(0)  # type: ignore[attr-defined]
        except AttributeError:
            os.lseek(handle, 0, os.SEEK_SET)
        try:
            msvcrt.locking(handle, msvcrt.LK_NBLCK, 1)  # type: ignore[attr-defined]
        except OSError:
            return False
        return True
    import fcntl  # pragma: no cover - POSIX branch is NOT exercised by this card

    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return False
    return True


def _unlock_byte(handle: int) -> None:
    if os.name == "nt":
        import msvcrt

        try:
            handle.seek(0)  # type: ignore[attr-defined]
        except AttributeError:
            os.lseek(handle, 0, os.SEEK_SET)
        msvcrt.locking(handle, msvcrt.LK_UNLCK, 1)  # type: ignore[attr-defined]
        return
    import fcntl  # pragma: no cover - POSIX branch is NOT exercised by this card

    fcntl.flock(handle, fcntl.LOCK_UN)


'''

# ---------------------------------------------------------------------------
# 3. small supporting edits
# ---------------------------------------------------------------------------

EDITS = [
    (
        "imports (uuid + hashlib)",
        "import json\nimport math\nimport os\nfrom pathlib import Path\nimport random\nimport re\nimport subprocess\nimport sys\nimport time\nfrom typing import Any\n",
        "import hashlib\nimport json\nimport math\nimport os\nfrom pathlib import Path\nimport random\nimport re\nimport subprocess\nimport sys\nimport time\nfrom typing import Any\nimport uuid\n",
    ),
    (
        "constants (lock/schema/journal/probe soft cap)",
        '_PAUSE_REFCOUNT_NAME = "filing_fetch_pause.refcount"\n_PAUSE_OWNER_NAME = "filing_fetch_pause.owner"\n_WORKER_STATUS_TIMEOUT = 60.0\n',
        '_PAUSE_REFCOUNT_NAME = "filing_fetch_pause.refcount"\n_PAUSE_OWNER_NAME = "filing_fetch_pause.owner"\n_WORKER_STATUS_TIMEOUT = 60.0\n\n# I-04-C ADR-6 caps every lease-layer wait with min(...) forms: the probe grows no\n# budget of its own, it only shrinks.  5s is the soft landing; the 20s hard cap of\n# I-04-B stays in force underneath it.\n_PROBE_SOFT_CAP_SECONDS = 5.0\n',
    ),
    (
        "stats defaults (lease keys)",
        '    stats.setdefault("cleanup_calls", 0)\n    stats.setdefault("cleanup_status", "not_needed")\n    return stats\n',
        '    stats.setdefault("cleanup_calls", 0)\n    stats.setdefault("cleanup_status", "not_needed")\n    # I-04-D: the lease layer consumes phase budget but mints none (ADR-6); these\n    # counters exist so queueing cost is visible instead of being read as latency.\n    stats.setdefault("lease_lock_waits", 0)\n    stats.setdefault("lease_lock_acquisitions", 0)\n    stats.setdefault("lease_lock_max_wait_seconds", 0.0)\n    stats.setdefault("lease_ledger_writes", 0)\n    return stats\n',
    ),
]


def apply_edits(text: str) -> tuple[str, list[str]]:
    notes: list[str] = []
    if OLD_PROBE not in text:
        raise SystemExit("FATAL: the _pid_is_alive body was not found verbatim")
    text = text.replace(OLD_PROBE, NEW_PROBE, 1)
    notes.append("probe: _pid_is_alive now delegates to _pid_is_alive_with_start_time (+_windows_process_start_time)")

    start = text.index(OLD_BLOCK_START)
    end = text.index(OLD_BLOCK_END)
    if end <= start:
        raise SystemExit("FATAL: the legacy lease block boundaries are inverted")
    text = text[:start] + NEW_BLOCK + text[end:]
    notes.append("lease block replaced (legacy _read/_write/_prune + PausedWorkerScope -> ADR-1..ADR-12 protocol)")

    for name, old, new in EDITS:
        if old not in text:
            raise SystemExit(f"FATAL: edit {name!r} did not match")
        text = text.replace(old, new, 1)
        notes.append(f"edit: {name}")
    return text, notes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not TARGET.exists():
        print(f"FATAL: {TARGET} not found")
        return 1
    before = sha256(TARGET)
    print(f"target       : {TARGET}")
    print(f"sha256 before: {before}")
    original = TARGET.read_text(encoding="utf-8")
    new_text, notes = apply_edits(original)
    for note in notes:
        print(f"  - {note}")
    if args.check:
        print("check only; nothing written")
        return 0
    if not args.apply:
        print("pass --apply (or --check) to do anything")
        return 0
    if before != BASELINE_SHA:
        print(f"FATAL: baseline sha256 mismatch (expected {BASELINE_SHA}); refusing to patch")
        return 1
    TARGET.write_text(new_text, encoding="utf-8")
    print(f"sha256 after : {sha256(TARGET)}")
    print(f"bytes after  : {TARGET.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
