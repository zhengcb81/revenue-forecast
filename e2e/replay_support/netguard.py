"""Offline child-environment construction (W14 E02/E03/E05).

``chain_env`` builds the subprocess environment every judged child runs with:
an explicit PYTHONPATH over the frozen deployment (which also outranks any
editable install of company-wiki), scrubbed credential variables (names are
recorded, values never leave the process), path-redirect variables removed so
children fall back to the deployed no-secret defaults, and the guard hooks
below.

``SITECUSTOMIZE_SOURCE`` is materialized into the guard directory and loaded
by every child interpreter through PYTHONPATH.  It installs:

- an install marker (``install.jsonl``): proves the guard actually loaded in
  this child and records which wrappers wired;
- the provider counter spy: fires ``{"counter": "provider"}`` at real
  ``requests``/``http.client``/``urllib`` call sites BEFORE delegation —
  positive-control tested, never fabricated;
- the outbound-network block: with ``RF_E2E_NET_BLOCK=1`` non-loopback
  ``connect``/``connect_ex``/``getaddrinfo``/``sendto`` raise and each
  attempt is appended to the netlog (connect-level guard; a child that
  shells out to an external binary bypasses this — see handoff limits).

Provenance evidence: every child writes its PID and the actually imported
``company_wiki`` root to ``children.jsonl``.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

# Credential-looking variables scrubbed from child environments.  Names only
# are reported; values are never copied into evidence.
_CREDENTIAL_PATTERN = re.compile(
    r"(API_KEY|TOKEN|SECRET|PASSWORD|PASSPHRASE|CREDENTIAL|PRIVATE_KEY)$",
    re.IGNORECASE,
)
# Path-redirect variables that could point a child at a personal production
# configuration instead of the deployed no-secret defaults.  Removed (not
# merely masked) so the deployment default wins; names are recorded.
_PATH_REDIRECT_VARS = (
    "COMPANY_WIKI_BUDGET_CONFIG",
    "REVENUE_PUBLICATION_REGISTRY",
)
_CONTROLLED_KEYS = (
    "PYTHONPATH", "PYTHONDONTWRITEBYTECODE", "PYTHONUTF8", "PYTHONNOUSERSITE",
    "RF_E2E_SPY_DIR", "RF_E2E_NET_BLOCK", "RF_E2E_NETLOG",
)


def chain_env(
    deployment, guard_dir: Path, *, net_block: bool,
) -> tuple[dict, dict]:
    """(environment, evidence) for judged children of this deployment.

    ``deployment`` is a FrozenDeployment; its scratch paths lead PYTHONPATH so
    the frozen code always wins over a polluted PYTHONPATH, an editable
    install, or an old installed copy.  The evidence dict records the exact
    controlled values and the scrubbed credential NAMES (never values).
    """
    env = dict(os.environ)
    scrubbed = {}
    for name in list(env):
        if _CREDENTIAL_PATTERN.search(name):
            scrubbed[name] = "<scrubbed>"
            env.pop(name)
    env.pop("PYTHONSTARTUP", None)
    redirected = []
    for name in _PATH_REDIRECT_VARS:
        if name in env:
            env.pop(name)
            redirected.append(name)
    env["PYTHONPATH"] = os.pathsep.join([
        str(guard_dir),
        str(deployment.rf_scripts),
        str(deployment.cwp_src),
    ])
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONUTF8"] = "1"
    env["PYTHONNOUSERSITE"] = "1"
    env["RF_E2E_SPY_DIR"] = str(guard_dir)
    if net_block:
        env["RF_E2E_NET_BLOCK"] = "1"
        env["RF_E2E_NETLOG"] = str(guard_dir / "net_attempts.jsonl")
    else:
        env.pop("RF_E2E_NET_BLOCK", None)
        env.pop("RF_E2E_NETLOG", None)
    evidence = {
        "pythonpath_entries": env["PYTHONPATH"].split(os.pathsep),
        "net_block": bool(net_block),
        "scrubbed_credential_names": sorted(scrubbed),
        "removed_path_redirect_names": sorted(redirected),
        "controlled_values": {k: env.get(k) for k in _CONTROLLED_KEYS
                              if k in env},
    }
    return env, evidence


SITECUSTOMIZE_SOURCE = '''\
"""W14 guard: install marker + provider spy + offline network block.

Loaded via PYTHONPATH by the replay harness only.  It never fakes provider
behavior: counters fire at real calls before delegation, and the network hook
only REFUSES non-loopback operations while recording the attempt.  The install
marker (install.jsonl) proves this file actually executed in this child and
records which wrappers wired, so a silent load failure cannot masquerade as
"zero events".
"""
from __future__ import annotations

import json
import os
import socket
import time

_SPY_DIR = os.environ.get("RF_E2E_SPY_DIR")
_NET_BLOCK = os.environ.get("RF_E2E_NET_BLOCK") == "1"
_NETLOG = os.environ.get("RF_E2E_NETLOG")
_LOOPBACK = ("127.0.0.1", "::1", "localhost", "")


def _record(filename: str, rec: dict) -> None:
    if not _SPY_DIR:
        return
    try:
        os.makedirs(_SPY_DIR, exist_ok=True)
        with open(os.path.join(_SPY_DIR, filename), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\\n")
    except OSError:
        pass


def _counter_event(counter: str, qualname: str, detail: dict) -> None:
    _record("events.jsonl", {
        "counter": counter, "qualname": qualname, "pid": os.getpid(),
        "t": round(time.time(), 3), **detail})


def _wrap_provider_request() -> bool:
    try:
        import requests.sessions
        original = requests.sessions.Session.request

        def request(self, method, url, *args, **kwargs):
            _counter_event("provider", "requests.Session.request",
                           {"method": str(method), "url": str(url)[:200]})
            return original(self, method, url, *args, **kwargs)

        requests.sessions.Session.request = request
        return True
    except Exception:
        return False


def _wrap_http_client() -> bool:
    try:
        import http.client
        original = http.client.HTTPConnection.connect

        def connect(self):
            host = getattr(self, "host", "?")
            _counter_event("provider", "http.client.HTTPConnection.connect",
                           {"host": str(host)[:200]})
            return original(self)

        http.client.HTTPConnection.connect = connect
        return True
    except Exception:
        return False


def _wrap_urlopen() -> bool:
    try:
        import urllib.request
        original = urllib.request.urlopen

        def urlopen(url, *args, **kwargs):
            _counter_event("provider", "urllib.request.urlopen",
                           {"url": str(url)[:200]})
            return original(url, *args, **kwargs)

        urllib.request.urlopen = urlopen
        return True
    except Exception:
        return False


def _install_net_block() -> bool:
    if not _NET_BLOCK:
        return False
    loopback_hosts = {"127.0.0.1", "::1", "localhost", "", None}

    def blocked_connect(original):
        def connect(self, address, *args, **kwargs):
            try:
                host = address[0] if isinstance(address, tuple) else address
            except Exception:
                host = str(address)
            if str(host) not in loopback_hosts:
                rec = {"pid": os.getpid(), "op": "connect",
                       "host": str(host)[:200],
                       "port": address[1] if isinstance(address, tuple)
                       and len(address) > 1 else None,
                       "t": round(time.time(), 3)}
                _record("net_attempts.jsonl", rec)
                raise OSError(
                    "rf-e2e net block: non-loopback connect refused: "
                    + str(host))
            return original(self, address, *args, **kwargs)
        return connect

    socket.socket.connect = blocked_connect(socket.socket.connect)
    socket.socket.connect_ex = blocked_connect(socket.socket.connect_ex)

    # DNS resolution to a non-loopback name would leak a packet before any
    # connect fires (getaddrinfo resolves natively) — block and record it.
    original_getaddrinfo = socket.getaddrinfo

    def getaddrinfo(host, port, *args, **kwargs):
        if host is not None and str(host) not in loopback_hosts:
            rec = {"pid": os.getpid(), "op": "getaddrinfo",
                   "host": str(host)[:200], "port": port,
                   "t": round(time.time(), 3)}
            _record("net_attempts.jsonl", rec)
            raise OSError(
                "rf-e2e net block: non-loopback DNS refused: " + str(host))
        return original_getaddrinfo(host, port, *args, **kwargs)

    socket.getaddrinfo = getaddrinfo

    original_sendto = socket.socket.sendto

    def sendto(self, data, *args, **kwargs):
        try:
            address = args[0] if args else kwargs.get("address")
            host = address[0] if isinstance(address, tuple) else address
        except Exception:
            host = str(address)
        if host is not None and str(host) not in loopback_hosts:
            rec = {"pid": os.getpid(), "op": "sendto",
                   "host": str(host)[:200], "t": round(time.time(), 3)}
            _record("net_attempts.jsonl", rec)
            raise OSError(
                "rf-e2e net block: non-loopback send refused: " + str(host))
        return original_sendto(self, data, *args, **kwargs)

    socket.socket.sendto = sendto
    return True


_WIRING = {"urlopen": False, "http_client": False, "requests": False,
           "net_block": False}


def _provenance() -> None:
    record = {"pid": os.getpid(),
              "argv0": (os.environ.get("_") or "")[:200],
              "python": os.environ.get("PYTHON", "")[:200]}
    try:
        import sys
        record["executable"] = sys.executable
        # recorded at interpreter EXIT (atexit): for `python -m` children
        # sys.argv[0] is still "-m" during site customization and only later
        # replaced by the module file path by runpy — exit-time capture is
        # the only point where argv identifies the executed module
        record["argv"] = [str(a)[:200] for a in sys.argv[:6]]
        main_module = sys.modules.get("__main__")
        record["main_module_file"] = str(
            getattr(main_module, "__file__", "") or "")[:300] or None
    except Exception:
        pass
    try:
        import company_wiki
        record["company_wiki_file"] = str(company_wiki.__file__)
    except Exception:
        record["company_wiki_file"] = None
    _record("children.jsonl", record)


def _install() -> None:
    # provenance is captured at EXIT so -m children record their real module
    # path; killed children (timeout) simply have no exit record — their PIDs
    # are still evidence via the runner's per-process argv files
    import atexit
    atexit.register(_provenance)
    _WIRING["urlopen"] = bool(_wrap_urlopen())
    _WIRING["http_client"] = bool(_wrap_http_client())
    _WIRING["requests"] = bool(_wrap_provider_request())
    _WIRING["net_block"] = bool(_install_net_block())
    # install marker: proof this file executed AND which wrappers wired —
    # a silent load failure cannot masquerade as "zero events"
    _record("install.jsonl", {"pid": os.getpid(), "wired": dict(_WIRING),
                              "net_block": _NET_BLOCK,
                              "t": round(time.time(), 3)})


try:
    _install()
except Exception:
    pass
'''


def materialize_guard(guard_dir: Path) -> None:
    guard_dir.mkdir(parents=True, exist_ok=True)
    (guard_dir / "sitecustomize.py").write_text(
        SITECUSTOMIZE_SOURCE, encoding="utf-8")


def net_attempts(guard_dir: Path) -> list[dict]:
    path = guard_dir / "net_attempts.jsonl"
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                out.append({"unparseable": line[:200]})
    return out


def counter_totals(guard_dir: Path) -> dict:
    path = guard_dir / "events.jsonl"
    if not path.is_file():
        return {}
    totals: dict[str, int] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            name = json.loads(line).get("counter")
        except ValueError:
            continue
        if name:
            totals[name] = totals.get(name, 0) + 1
    return totals


def child_provenance(guard_dir: Path) -> list[dict]:
    path = guard_dir / "children.jsonl"
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                out.append({"unparseable": line[:200]})
    return out


def install_records(guard_dir: Path) -> list[dict]:
    """Guard install markers: one per child that actually executed the
    sitecustomize, with its wiring status (positive control for the spy)."""
    path = guard_dir / "install.jsonl"
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.strip():
            try:
                out.append(json.loads(line))
            except ValueError:
                out.append({"unparseable": line[:200]})
    return out
