"""E2E-EXPAND counter spy — installed via PYTHONPATH ONLY for judged runs.

Adapted from I-07-B harness/spy/sitecustomize.py (binding pin 58da8b36…).
Every wrapper fires `_event` BEFORE delegating to the original function.
No frozen/simulated provider exists here — this suite runs real steps only.
"""
from __future__ import annotations

import json
import os
import time
import traceback

_SPY_DIR = os.environ.get("RF_E2E_SPY_DIR")
_WIRING: dict = {}


def _event(counter: str, module: str, qualname: str, detail: dict) -> None:
    if not _SPY_DIR:
        return
    rec = {"counter": counter, "module": module, "qualname": qualname,
           "pid": os.getpid(), "t": round(time.time(), 3), "simulated": False,
           **detail}
    try:
        os.makedirs(_SPY_DIR, exist_ok=True)
        with open(os.path.join(_SPY_DIR, "events.jsonl"), "a",
                  encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")
    except OSError:
        pass


def _wrap(counter: str, obj, name: str, detail_fn=None) -> bool:
    key = "%s.%s.%s" % (getattr(obj, "__module__", "?"),
                        getattr(obj, "__qualname__", obj), name)
    original = getattr(obj, name, None)
    if original is None or getattr(original, "_e2eexpand_spy", False):
        _WIRING[key] = {"status": "already" if original else "missing",
                        "counter": counter}
        return original is not None

    def wrapper(*args, **kwargs):
        detail = {}
        if detail_fn:
            try:
                detail = detail_fn(args, kwargs)
            except Exception:
                detail = {"detail_error": traceback.format_exc()[-300:]}
        _event(counter, getattr(obj, "__module__", "?"), name, detail)
        return original(*args, **kwargs)

    wrapper._e2eexpand_spy = True
    wrapper._e2eexpand_original = original
    try:
        setattr(obj, name, wrapper)
        _WIRING[key] = {"status": "wrapped", "counter": counter}
        return True
    except Exception as exc:
        _WIRING[key] = {"status": "failed", "counter": counter,
                        "error": str(exc)}
        return False


def _try_import(name: str):
    try:
        return __import__(name, fromlist=["*"])
    except Exception:
        _WIRING[name] = {"status": "unwired",
                         "reason": traceback.format_exc()[-400:]}
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


def _install() -> None:
    if not _SPY_DIR:
        return
    for mod_name, cls_name in (
        ("company_wiki.source_catalog.adapter_process", "JsonCommandAdapter"),
        ("company_wiki.source_catalog.dayu_cli_adapter",
         "DayuCliDownloadAdapter"),
    ):
        mod = _try_import(mod_name)
        cls = getattr(mod, cls_name, None) if mod else None
        if cls is None:
            continue
        _wrap("provider", cls, "discover", _http_detail)
        _wrap("provider", cls, "fetch", _http_detail)
    try:
        import requests.sessions  # noqa: F401
        _wrap("provider", requests.sessions.Session, "request", _http_detail)
    except Exception:
        _WIRING["requests.sessions.Session.request"] = {"status": "unwired"}
    mod = _try_import("company_wiki.source_catalog.service")
    if mod is not None:
        _wrap("scan", mod.SourceCatalog, "scan", _path_detail)
        for meth in ("normalize", "extract_sections", "summarize", "backfill"):
            if hasattr(mod.SourceCatalog, meth):
                _wrap("producer", mod.SourceCatalog, meth, _path_detail)
    mod = _try_import("company_wiki.source_catalog.scanner")
    if mod is not None:
        _wrap("scan", mod, "scan_catalog", _path_detail)
    mod = _try_import("company_wiki.source_catalog.resolver")
    if mod is not None:
        _wrap("read", mod, "_sha256_of_file", _path_detail)
        _wrap("read", mod, "_read_verified_bytes", _path_detail)
    mod = _try_import("company_wiki.source_contract.source_manifest")
    if mod is not None:
        _wrap("read", mod.SourceManifest, "from_file", _path_detail)
    try:
        import company_wiki_source
        _wrap("read", company_wiki_source, "verify_artifact_reads",
              _path_detail)
    except Exception:
        _WIRING["company_wiki_source.verify_artifact_reads"] =             {"status": "unwired"}
    for mod_name, fname in (
        ("company_wiki.source_catalog.normalizer", "normalize_catalog"),
        ("company_wiki.source_catalog.summarizer", "summarize_catalog"),
        ("company_wiki.source_catalog.section_extractor",
         "extract_sections_catalog"),
        ("company_wiki.source_catalog.llm_summarizer",
         "summarize_catalog_with_llm"),
    ):
        mod = _try_import(mod_name)
        if mod is not None and hasattr(mod, fname):
            _wrap("producer", mod, fname, _path_detail)
    try:
        os.makedirs(_SPY_DIR, exist_ok=True)
        with open(os.path.join(_SPY_DIR, "wiring.json"), "w",
                  encoding="utf-8") as fh:
            json.dump(_WIRING, fh, ensure_ascii=False, indent=1)
    except OSError:
        pass


try:
    _install()
except Exception:
    try:
        if _SPY_DIR:
            with open(os.path.join(_SPY_DIR, "wiring.json"), "w",
                      encoding="utf-8") as fh:
                json.dump({"install_error": traceback.format_exc()}, fh)
    except OSError:
        pass
