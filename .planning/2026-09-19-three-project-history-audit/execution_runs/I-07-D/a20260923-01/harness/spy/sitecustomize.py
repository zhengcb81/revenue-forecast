"""I-07-D counter spy — installed via PYTHONPATH ONLY for judged runs.

Activation: this file is imported as ``sitecustomize`` by every Python process
whose PYTHONPATH includes this directory AND only when ``I07D_SPY_DIR`` is set.
No other process on this machine is affected (the env var is per-run).

Counting rule (card clause 1): counters increment at the CALL of the real entry
function, BEFORE delegation — never derived from an artifact/producer_events
INSERT. Events are appended as JSON lines to ``$I07D_SPY_DIR/events.jsonl``.

Frozen provider simulation (scenario_matrix S-*-3, C level ONLY): when
``I07D_SIM_FROZEN_META`` points at a fixture JSON, the four adapter
``discover``/``fetch`` entry points are REPLACED by frozen implementations that
serve the fixture bytes. Every such event is labelled ``simulated: true`` and
must never be read as a live call (oracle R5/C5).

Wiring status (wrapped / unwired + reason) is written to
``$I07D_SPY_DIR/wiring.json`` at install time.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import traceback

_SPY_DIR = os.environ.get("I07D_SPY_DIR")
_EVENTS = None
_WIRING: dict[str, dict] = {}


def _event(counter: str, module: str, qualname: str, detail: dict) -> None:
    if not _SPY_DIR:
        return
    rec = {
        "counter": counter,
        "module": module,
        "qualname": qualname,
        "pid": os.getpid(),
        "t": round(time.time(), 3),
        "simulated": bool(os.environ.get("I07D_SIM_FROZEN_META")),
        **detail,
    }
    try:
        os.makedirs(_SPY_DIR, exist_ok=True)
        with open(os.path.join(_SPY_DIR, "events.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
    except OSError:
        pass


def _digest(value) -> str:
    try:
        raw = json.dumps(value, ensure_ascii=False, default=str, sort_keys=True)
    except (TypeError, ValueError):
        raw = repr(value)
    return hashlib.sha256(raw.encode("utf-8", "replace")).hexdigest()[:16]


def _wrap(counter: str, obj, name: str, detail_fn=None) -> bool:
    """Wrap ``obj.<name>`` so the counter increments on call entry."""
    key = f"{getattr(obj, '__module__', '?')}.{getattr(obj, '__qualname__', obj)}.{name}"
    original = getattr(obj, name, None)
    if original is None or getattr(original, "_i07d_spy", False):
        _WIRING[key] = {"status": "already" if original else "missing",
                        "counter": counter}
        return original is not None

    def wrapper(*args, **kwargs):
        detail = {}
        if detail_fn:
            try:
                detail = detail_fn(args, kwargs)
            except Exception:  # noqa: BLE001
                detail = {"detail_error": traceback.format_exc()[-300:]}
        _event(counter, getattr(obj, "__module__", "?"), name, detail)
        return original(*args, **kwargs)

    wrapper._i07d_spy = True  # type: ignore[attr-defined]
    wrapper._i07d_original = original  # type: ignore[attr-defined]
    try:
        setattr(obj, name, wrapper)
        _WIRING[key] = {"status": "wrapped", "counter": counter}
        return True
    except Exception as exc:  # noqa: BLE001
        _WIRING[key] = {"status": "failed", "counter": counter, "error": str(exc)}
        return False


def _try_import(name: str):
    try:
        return __import__(name, fromlist=["*"])
    except Exception:  # noqa: BLE001
        _WIRING[name] = {"status": "unwired", "reason": traceback.format_exc()[-400:]}
        return None


def _path_detail(args, kwargs):
    out = {}
    for a in list(args) + list(kwargs.values()):
        s = str(a)
        if "\\" in s or "/" in s:
            out.setdefault("paths", []).append(s)
    if "paths" in out:
        out["paths"] = out["paths"][:6]
    return out


def _http_detail(args, kwargs):
    url = kwargs.get("url") or (args[1] if len(args) > 1 else None)
    headers = kwargs.get("headers") or (args[3] if len(args) > 3 else None) or {}
    return {"auth_target": str(url),
            "auth_header_names": sorted(str(k) for k in dict(headers)),
            "method": kwargs.get("method") or (args[0] if args else None)}


def _install_frozen_provider(meta_path: str) -> None:
    """Replace the four adapter entry points with a frozen simulated provider."""
    meta = json.loads(open(meta_path, encoding="utf-8").read())
    acq = _try_import("company_wiki.source_catalog.acquisition")
    if acq is None:
        return
    cand_cls = acq.DownloadCandidate
    rec_cls = acq.DownloadReceipt
    ADAPTERS = ("company_wiki.source_catalog.adapter_process",
                "company_wiki.source_catalog.dayu_cli_adapter")
    FROZEN_DATE = meta["filing_date"]

    def make_discover(mod_name):
        def discover(self, request):
            _event("provider", mod_name, "discover",
                   {"simulated": True, "fixture": meta.get("fixture_id"),
                    "request_entity": getattr(request, "entity", None)})
            cand = cand_cls(
                candidate_id=meta["candidate_id"],
                provider=meta["provider"],
                provider_document_id=meta["provider_document_id"],
                market=meta["market"],
                entity=meta["entity"],
                title=meta["title"],
                source_url=meta["source_url"],
                document_kind=request.document_kind,
                filing_date=FROZEN_DATE,
                fiscal_year=request.fiscal_year if request.fiscal_year is not None
                else meta["fiscal_year"],
                form_type=meta.get("form_type"),
                fiscal_period=meta.get("fiscal_period", "FY"),
                language=meta.get("language"),
                amended=False,
                remote_size=meta.get("byte_size"),
            )
            return (cand,)
        discover._i07d_spy = True  # type: ignore[attr-defined]
        return discover

    def make_fetch(mod_name, provider_name):
        def fetch(self, candidate, request_directory):
            import hashlib as _h
            import shutil as _sh
            raw = meta["frozen_raw_path"]
            request_directory.mkdir(parents=True, exist_ok=True)
            fname = meta.get("staged_name") or (
                f"{candidate.provider_document_id}.{'pdf' if meta['mime_type'].endswith('pdf') else 'htm'}")
            dst = Path(request_directory) / fname
            _event("provider", mod_name, "fetch",
                   {"simulated": True, "fixture": meta.get("fixture_id"),
                    "staged_to": str(dst)})
            _sh.copyfile(raw, dst)
            data = dst.read_bytes()
            return rec_cls(
                candidate_id=candidate.candidate_id,
                provider=candidate.provider,
                provider_document_id=candidate.provider_document_id,
                source_url=candidate.source_url,
                staged_path=str(dst),
                content_sha256=_h.sha256(data).hexdigest(),
                byte_size=len(data),
                mime_type=meta["mime_type"],
                retrieved_at=meta["retrieved_at"],
                http_status=200,
                adapter_name=meta.get("adapter_name", "frozen-sim"),
                adapter_version=meta.get("adapter_version", "1.0.0"),
            )
        fetch._i07d_spy = True  # type: ignore[attr-defined]
        return fetch

    from pathlib import Path  # noqa: E402  (used by make_fetch)

    for mod_name in ADAPTERS:
        mod = _try_import(mod_name)
        if mod is None:
            continue
        cls = getattr(mod, "JsonCommandAdapter", None) or getattr(mod, "DayuCliDownloadAdapter", None)
        if cls is None:
            continue
        cls.discover = make_discover(mod_name)  # type: ignore[method-assign]
        cls.fetch = make_fetch(mod_name, getattr(cls, "name", "?"))  # type: ignore[method-assign]
        _WIRING[f"{mod_name}.frozen_provider"] = {"status": "replaced_simulated",
                                                  "counter": "provider",
                                                  "fixture": meta.get("fixture_id")}


def _install_scan_barrier(mod) -> None:
    """F04: park the process at the scan_catalog call boundary and register
    its PID.  Reaching the barrier proves the raw was already committed and
    registration has NOT started (trigger evidence: barrier + pid manifest).
    The sleep loop is only ever left by an external TerminateProcess — no
    Python finally runs here.
    """
    state_dir = os.environ.get("I07D_STATE_DIR")
    if not state_dir:
        return
    inner = mod.scan_catalog

    def barrier_scan(*args, **kwargs):
        pid = os.getpid()
        rec = {
            "point": "scan_catalog:after_raw_commit_before_registration",
            "pid": pid,
            "parent_pid": os.getppid(),
            "argv": list(sys.argv),
            "cwd": os.getcwd(),
            "registered_at": time.time(),
            "armed": "kill_before_scan",
            "note": "raw commit happened before this call "
                    "(canonical_writer.import_staged L181-184); registration "
                    "not started; orchestrator may kill ONLY this registered PID",
        }
        try:
            os.makedirs(state_dir, exist_ok=True)
            with open(os.path.join(state_dir, f"pid_{pid}.json"), "w",
                      encoding="utf-8") as fh:
                json.dump(rec, fh, ensure_ascii=False, indent=1)
            _event("scan", getattr(mod, "__name__", "?"), "scan_catalog",
                   {"armed_kill": True, "point": rec["point"]})
            with open(os.path.join(state_dir, f"barrier_{pid}.json"), "w",
                      encoding="utf-8") as fh:
                json.dump({"point": rec["point"], "pid": pid,
                           "armed": "kill_before_scan", "t": time.time()},
                          fh, ensure_ascii=False)
        except OSError:
            pass
        while True:  # real kill happens from outside; no finally may run here
            time.sleep(3600)
        # If control ever returned (only via a release we do not implement),
        # a pid_<pid>.released.json marker would be written here; its ABSENCE
        # after the kill is the proof the barrier was never resumed.
        raise RuntimeError("unreachable")

    barrier_scan._i07d_barrier = True  # type: ignore[attr-defined]
    barrier_scan._i07d_original = inner  # type: ignore[attr-defined]
    mod.scan_catalog = barrier_scan
    _WIRING[f"{getattr(mod, '__name__', 'scanner')}.scan_catalog_barrier"] = {
        "status": "armed_kill_before_scan", "counter": "scan",
        "state_dir": state_dir}


def _install() -> None:
    if not _SPY_DIR:
        return
    # 1) provider (real adapter entry points, counted even when not replaced)
    for mod_name, cls_name in (
        ("company_wiki.source_catalog.adapter_process", "JsonCommandAdapter"),
        ("company_wiki.source_catalog.dayu_cli_adapter", "DayuCliDownloadAdapter"),
    ):
        mod = _try_import(mod_name)
        cls = getattr(mod, cls_name, None) if mod else None
        if cls is None:
            continue
        _wrap("provider", cls, "discover", _http_detail)
        _wrap("provider", cls, "fetch", _http_detail)
    # HTTP fallback (records any live network call + auth target headers)
    try:
        import requests.sessions  # noqa: F401
        _wrap("provider", requests.sessions.Session, "request", _http_detail)
    except Exception:  # noqa: BLE001
        _WIRING["requests.sessions.Session.request"] = {"status": "unwired"}

    # 2) scan
    mod = _try_import("company_wiki.source_catalog.service")
    if mod is not None:
        _wrap("scan", mod.SourceCatalog, "scan", _path_detail)
    mod = _try_import("company_wiki.source_catalog.scanner")
    if mod is not None:
        _wrap("scan", mod, "scan_catalog", _path_detail)
    # canonical_writer holds its OWN module-global binding of scan_catalog
    # (import-order stale-binding bypass discovered in F04 run1: the direct
    # canonical-import scan at canonical_writer.py:185 never touched the
    # scanner-module wrapper).  Wrap THAT name too — count + F04 barrier.
    armed = os.environ.get("I07D_FAULT") == "kill_before_scan"
    cw = _try_import("company_wiki.source_catalog.canonical_writer")
    if cw is not None and getattr(cw, "scan_catalog", None) is not None:
        _wrap("scan", cw, "scan_catalog", _path_detail)
        # F04 kill arm (I-07-D oracle §2 F04): park exactly at the
        # canonical-import scan call — raw committed (import_staged L181-184),
        # registration not started.  The parked process registers ITS OWN pid
        # (pid_<pid>.json) before the barrier; orchestrator kills ONLY that PID.
        if armed:
            _install_scan_barrier(cw)
    elif armed and mod is not None:
        _install_scan_barrier(mod)

    # 3) read (actual byte reads of raw/source/artifact content)
    mod = _try_import("company_wiki.source_catalog.resolver")
    if mod is not None:
        _wrap("read", mod, "_sha256_of_file", _path_detail)
        _wrap("read", mod, "_read_verified_bytes", _path_detail)
    mod = _try_import("company_wiki.source_contract.source_manifest")
    if mod is not None:
        _wrap("read", mod.SourceManifest, "from_file", _path_detail)
    try:
        import company_wiki_source  # RF entry-side artifact reader
        _wrap("read", company_wiki_source, "verify_artifact_reads", _path_detail)
    except Exception:  # noqa: BLE001
        _WIRING["company_wiki_source.verify_artifact_reads"] = {"status": "unwired"}

    # 4) producer (real producer entry points)
    mod = _try_import("company_wiki.source_catalog.service")
    if mod is not None:
        for meth in ("normalize", "extract_sections", "summarize", "backfill"):
            if hasattr(mod.SourceCatalog, meth):
                _wrap("producer", mod.SourceCatalog, meth, _path_detail)
    for mod_name, fname in (
        ("company_wiki.source_catalog.normalizer", "normalize_catalog"),
        ("company_wiki.source_catalog.summarizer", "summarize_catalog"),
        ("company_wiki.source_catalog.section_extractor", "extract_sections_catalog"),
        ("company_wiki.source_catalog.llm_summarizer", "summarize_catalog_with_llm"),
    ):
        mod = _try_import(mod_name)
        if mod is not None and hasattr(mod, fname):
            _wrap("producer", mod, fname, _path_detail)

    sim = os.environ.get("I07D_SIM_FROZEN_META")
    if sim:
        try:
            _install_frozen_provider(sim)
        except Exception:  # noqa: BLE001
            _WIRING["frozen_provider"] = {"status": "failed",
                                          "error": traceback.format_exc()[-400:]}

    try:
        os.makedirs(_SPY_DIR, exist_ok=True)
        with open(os.path.join(_SPY_DIR, "wiring.json"), "w", encoding="utf-8") as fh:
            json.dump(_WIRING, fh, ensure_ascii=False, indent=1)
    except OSError:
        pass


try:
    _install()
except Exception:  # noqa: BLE001  — never break the interpreter
    try:
        if _SPY_DIR:
            with open(os.path.join(_SPY_DIR, "wiring.json"), "w", encoding="utf-8") as fh:
                json.dump({"install_error": traceback.format_exc()}, fh)
    except OSError:
        pass
