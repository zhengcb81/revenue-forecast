"""I-07-D fault/barrier hooks — TEST-BUILT CODE ONLY, enabled only when a
harness writer process arms them via the --fault argument.

Adapted verbatim-in-mechanism from I-09-C `harness/i09c_hooks.py`
(sha256 bced2576f54c1d901395a5a96bf1139e2542080860b4edd3efe235f4511013b6).
Design (I-09-C card 按序动作 1, carried):
  * Product files are NOT edited.  Hooks wrap module attributes at process
    start inside the writer subprocess only, so the production commit order is
    provably unchanged (zero product diff); the wrap positions below are the
    "hook 位置" list the independent reviewer checks.
  * Every hook point writes a line to hook_trace_<pid>.jsonl (trigger trace).
  * Armed as ``kill:<point>``  -> write barrier_<pid>.json and sleep forever;
    the orchestrator then TerminateProcess()es ONLY the PID registered in
    pid_<pid>.json (real kill; Python finally must NOT run).
  * Armed as ``err:<op>:<role>`` -> raise a real OSError at exactly that
    boundary (exception path only — never a substitute for the kill cases).
  * ``--fault none`` -> install() is never called -> hooks do not exist.

Hook positions (wrap targets; every target EXISTS in current production):
  H1 revenue_forecast.run_forecast        -> err:prepare_mid
  H2 revenue_forecast.prepare_forecast    -> kill prepare:before / prepare:after
  H3 revenue_forecast._atomic_write_text  -> kill member:<role>:before |
                                              member:<role>:tmp_opened |
                                              member:<role>:after |
                                              err write/flush/fsync/replace
      (<role> by call order: 1st call = output_json, 2nd = output_markdown —
       this mirrors production main(): JSON member first, Markdown second)
  H4 revenue_forecast.main                -> kill return:before
      (= F06 commit-boundary kill; current production has NO separate
       commit_publication function — repo grep is empty — so the caller-
       acknowledgement boundary IS main's return)
  H5 publication_registry._append         -> kill registry:before_append /
                                              registry:after_append |
                                              err:append_registry
  DROPPED vs I-09-C: H6 publication_registry.commit_publication — target
      absent in current production; install() skips it if missing instead of
      crashing (evidence: binding.json product_fault_paths_cited.(f)).
"""
from __future__ import annotations

import builtins
import errno as _errno
import json
import os
import time
from pathlib import Path

STATE = {
    "armed": None,
    "run_dir": None,
    "member_counter": 0,
    "scope_role": None,
    "installed": False,
}


def _trace(point: str, **extra) -> None:
    run_dir = STATE["run_dir"]
    if not run_dir:
        return
    rec = {"t": time.time(), "pid": os.getpid(), "armed": STATE["armed"], "point": point}
    rec.update(extra)
    path = Path(run_dir) / f"hook_trace_{os.getpid()}.jsonl"
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def checkpoint(point: str) -> None:
    _trace(point)
    if STATE["armed"] == f"kill:{point}":
        barrier = Path(STATE["run_dir"]) / f"barrier_{os.getpid()}.json"
        barrier.write_text(
            json.dumps(
                {
                    "point": point,
                    "pid": os.getpid(),
                    "armed": STATE["armed"],
                    "t": time.time(),
                    "note": "barrier reached; orchestrator may kill ONLY this registered PID",
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        while True:  # real kill happens from outside; no finally may run here
            time.sleep(3600)


def _faulted(op: str) -> bool:
    role = STATE["scope_role"]
    if role is None or not STATE["armed"]:
        return False
    return STATE["armed"] == f"err:{op}:{role}"


class _OpenProxy:
    def __init__(self, handle, role):
        self._h = handle
        self._role = role

    def __enter__(self):
        self._h.__enter__()
        checkpoint(f"member:{self._role}:tmp_opened")
        return self

    def __exit__(self, *exc):
        return self._h.__exit__(*exc)

    def write(self, data):
        if _faulted("write"):
            _trace("err_raised", op="write", role=self._role)
            raise OSError(_errno.ENOSPC, "I-07-D injected write failure", "member write")
        return self._h.write(data)

    def flush(self):
        if _faulted("flush"):
            _trace("err_raised", op="flush", role=self._role)
            raise OSError(_errno.EIO, "I-07-D injected flush failure", "member flush")
        return self._h.flush()

    def __getattr__(self, name):
        return getattr(self._h, name)


def _patched_open(file, mode="r", *args, **kwargs):
    path_str = str(file)
    role = STATE["scope_role"]
    run_dir = str(STATE["run_dir"] or "")
    in_scope = role is not None and run_dir and path_str.startswith(run_dir)
    if in_scope and any(ch in mode for ch in "wxa+"):
        if _faulted("write"):
            _trace("err_raised", op="write", role=role, path=path_str)
            raise OSError(_errno.ENOSPC, "I-07-D injected open/write failure", path_str)
        handle = _OPEN_ORIG(file, mode, *args, **kwargs)
        return _OpenProxy(handle, role)
    return _OPEN_ORIG(file, mode, *args, **kwargs)


def _patched_fsync(fd):
    if _faulted("fsync"):
        _trace("err_raised", op="fsync", role=STATE["scope_role"])
        raise OSError(_errno.EIO, "I-07-D injected fsync failure", "fsync")
    return _FSYNC_ORIG(fd)


def _patched_replace(src, dst, *args, **kwargs):
    if _faulted("replace"):
        _trace("err_raised", op="replace", role=STATE["scope_role"], src=str(src))
        raise OSError(_errno.EACCES, "I-07-D injected replace failure", str(dst))
    return _REPLACE_ORIG(src, dst, *args, **kwargs)


_OPEN_ORIG = builtins.open
_FSYNC_ORIG = os.fsync
_REPLACE_ORIG = os.replace


def install(armed: str, run_dir) -> dict:
    """Wrap the product call sites listed in this module's docstring."""
    if STATE["installed"]:
        return {"installed": True, "note": "already installed"}
    setup_paths()
    import revenue_forecast as RF
    import publication_registry as PR

    STATE["armed"] = armed or None
    STATE["run_dir"] = str(run_dir)
    STATE["installed"] = True

    # H1 — prepare 中: fail during payload/identity computation
    orig_run_forecast = RF.run_forecast

    def run_forecast(*a, **k):
        if STATE["armed"] == "err:prepare_mid":
            _trace("err_raised", op="prepare_mid")
            raise OSError(_errno.EIO, "I-07-D injected prepare failure", "run_forecast")
        return orig_run_forecast(*a, **k)

    RF.run_forecast = run_forecast

    # H2 — prepare 前 / 后
    orig_prepare = RF.prepare_forecast

    def prepare_forecast(data, *, mode="formal"):
        checkpoint("prepare:before")
        out = orig_prepare(data, mode=mode)
        checkpoint("prepare:after")
        return out

    RF.prepare_forecast = prepare_forecast

    # H3 — member writes (JSON / Markdown): barriers + write/flush/fsync/replace faults
    orig_awt = RF._atomic_write_text

    def _atomic_write_text(path, text):
        STATE["member_counter"] += 1
        n = STATE["member_counter"]
        role = "output_json" if n == 1 else ("output_markdown" if n == 2 else f"member_{n}")
        checkpoint(f"member:{role}:before")
        STATE["scope_role"] = role
        try:
            builtins.open = _patched_open
            os.fsync = _patched_fsync
            os.replace = _patched_replace
            orig_awt(path, text)
        finally:
            builtins.open = _OPEN_ORIG
            os.fsync = _FSYNC_ORIG
            os.replace = _REPLACE_ORIG
            STATE["scope_role"] = None
        checkpoint(f"member:{role}:after")

    RF._atomic_write_text = _atomic_write_text

    # H4 — 返回前 (= F06 commit-boundary point; runs BEFORE writer's exit record)
    orig_main = RF.main

    def main():
        rc = orig_main()
        checkpoint("return:before")
        return rc

    RF.main = main

    # H5 — registry 持久化 前/后 + registry 故障
    orig_append = PR._append

    def _append(entry):
        checkpoint("registry:before_append")
        if STATE["armed"] == "err:append_registry":
            _trace("err_raised", op="append_registry")
            raise OSError(_errno.EACCES, "I-07-D injected registry failure", "registry append")
        out = orig_append(entry)
        checkpoint("registry:after_append")
        return out

    PR._append = _append

    # H6 (I-09-C only) — publication_registry.commit_publication does NOT exist
    # in current production: skip guarded, never crash the install.
    skipped = []
    orig_commit = getattr(PR, "commit_publication", None)
    if orig_commit is None:
        skipped.append("publication_registry.commit_publication (absent in current production)")
    else:

        def commit_publication(*a, **k):
            checkpoint("commit:before")
            out = orig_commit(*a, **k)
            checkpoint("commit:after")
            return out

        PR.commit_publication = commit_publication

    points = [
        "prepare:before", "prepare:after", "member:<role>:before",
        "member:<role>:tmp_opened", "member:<role>:after", "return:before",
        "registry:before_append", "registry:after_append",
        "err:prepare_mid", "err:write:<role>", "err:flush:<role>",
        "err:fsync:<role>", "err:replace:<role>", "err:append_registry",
    ]
    if orig_commit is not None:
        points += ["commit:before", "commit:after"]
    _trace("hooks_installed", points=points, skipped=skipped)
    return {"installed": True, "armed": STATE["armed"], "run_dir": STATE["run_dir"],
            "points": points, "skipped": skipped}


def setup_paths() -> None:
    from common import setup_paths as _setup

    _setup()
