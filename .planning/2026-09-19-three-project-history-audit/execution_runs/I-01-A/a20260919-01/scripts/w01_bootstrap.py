"""w01_bootstrap: dual-mode loader.

- code="prod": sys.path points at the read-only repo src; the production
  config_doctor module is loaded read-only from the repo scripts directory
  (the attempt copy is never imported).
- code="override": the SAME repo src still backs every module, but the files
  modified for this card are pre-registered into sys.modules from
  A/iso/override BEFORE any package __init__ executes, so both the doctor and
  the scan import the override copies through exactly the same module names.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

REPO_SRC = Path(r"C:\Users\郑曾波\Projects\company-wiki\src")
REPO_SCRIPTS = Path(r"C:\Users\郑曾波\Projects\company-wiki\scripts")
HERE = Path(__file__).resolve().parent
OVERRIDE = HERE.parent / "iso" / "override"


def _register(dotted: str, path: Path) -> None:
    """Exec module by file path under a dotted name (relative imports use the
    synthetic package __path__ registered above; already-loaded siblings are
    resolved from sys.modules)."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(dotted, path)
    assert spec is not None and spec.loader is not None, path
    module = importlib.util.module_from_spec(spec)
    sys.modules[dotted] = module
    spec.loader.exec_module(module)
    # keep the lexical parent's attribute binding consistent for absolute-path
    # imports of the form ``from company_wiki.source_catalog import x``
    parent = dotted.rpartition(".")[0]
    if parent in sys.modules:
        setattr(sys.modules[parent], dotted.rpartition(".")[2], module)


def setup(code: str) -> None:
    if code == "prod":
        sys.path.insert(0, str(REPO_SRC))
        _register("config_doctor", REPO_SCRIPTS / "config_doctor.py")
        return
    if code != "override":
        raise SystemExit(f"unknown code mode: {code}")
    pkg = types.ModuleType("company_wiki")
    pkg.__path__ = [str(REPO_SRC / "company_wiki")]
    pkg.__package__ = "company_wiki"
    sys.modules["company_wiki"] = pkg
    sc = types.ModuleType("company_wiki.source_catalog")
    sc.__path__ = [str(REPO_SRC / "company_wiki" / "source_catalog")]
    sc.__package__ = "company_wiki.source_catalog"
    sys.modules["company_wiki.source_catalog"] = sc
    adapters = types.ModuleType("company_wiki.source_catalog.adapters")
    adapters.__path__ = [str(REPO_SRC / "company_wiki" / "source_catalog" / "adapters")]
    adapters.__package__ = "company_wiki.source_catalog.adapters"
    sys.modules["company_wiki.source_catalog.adapters"] = adapters

    _register("company_wiki", REPO_SRC / "company_wiki" / "__init__.py")
    _register("company_wiki.source_catalog.models", OVERRIDE / "models.py")
    _register(
        "company_wiki.source_catalog.flags",
        REPO_SRC / "company_wiki" / "source_catalog" / "flags.py",
    )
    _register(
        "company_wiki.source_catalog.adapters.registry",
        REPO_SRC / "company_wiki" / "source_catalog" / "adapters" / "registry.py",
    )
    _register(
        "company_wiki.source_catalog.adapters.interface",
        REPO_SRC / "company_wiki" / "source_catalog" / "adapters" / "interface.py",
    )
    _register(
        "company_wiki.source_catalog.adapters.common",
        REPO_SRC / "company_wiki" / "source_catalog" / "adapters" / "common.py",
    )
    _register(
        "company_wiki.source_catalog.lock",
        REPO_SRC / "company_wiki" / "source_catalog" / "lock.py",
    )
    _register(
        "company_wiki.source_catalog.adapters.sidecar",
        REPO_SRC / "company_wiki" / "source_catalog" / "adapters" / "sidecar.py",
    )
    _register(
        "company_wiki.source_catalog.adapters.company_raw",
        REPO_SRC / "company_wiki" / "source_catalog" / "adapters" / "company_raw.py",
    )
    _register(
        "company_wiki.source_catalog.adapters.dayu",
        REPO_SRC / "company_wiki" / "source_catalog" / "adapters" / "dayu.py",
    )
    _register(
        "company_wiki.source_catalog.store",
        REPO_SRC / "company_wiki" / "source_catalog" / "store.py",
    )
    _register(
        "company_wiki.source_catalog.runtime_policy",
        REPO_SRC / "company_wiki" / "source_catalog" / "runtime_policy.py",
    )
    _register(
        "company_wiki.source_catalog.adapter_dispatch", OVERRIDE / "adapter_dispatch.py"
    )
    _register("company_wiki.source_catalog.scanner", OVERRIDE / "scanner.py")
    _register("company_wiki.source_catalog.service", OVERRIDE / "service.py")
    _register("company_wiki.source_catalog.config", OVERRIDE / "config.py")
    _register("config_doctor", OVERRIDE / "config_doctor.py")
