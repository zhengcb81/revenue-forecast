"""w02a_bootstrap: isolated module loader for card I-02-A.

- code="prod": sys.path points at the read-only repo src; the production
  canonical_writer module is loaded read-only from the repo (the attempt
  copy is never imported) — used for the frozen before/after baseline only
  if needed.
- code="override": the SAME repo src backs every unmodified module, but the
  files modified for this card (models.py / scanner.py / canonical_writer.py)
  are pre-registered into sys.modules from A/iso/override BEFORE any package
  __init__ executes, so the writer/resolver import the override copies
  through exactly the same module names.  service.py / config.py /
  adapter_dispatch.py / config_doctor.py overrides are re-registered here too
  to keep ONE override tree consistent with I-01-A (D-W01 wiring inside the
  scanner's config import must hit the I-01-A config copy).

Injection contract (D-W02/D-卡): fake scanner/resolver behavior is injected
ONLY inside the test harness by attribute replacement on the already-loaded
module objects; no fake code ever lives inside the override product copies.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

REPO_SRC = Path(r"C:\Users\郑曾波\Projects\company-wiki\src")
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
        return
    if code != "override":
        raise SystemExit(f"unknown code mode: {code}")
    pkg = types.ModuleType("company_wiki")
    pkg.__path__ = [str(REPO_SRC / "company_wiki")]
    pkg.__package__ = "company_wiki"
    sys.modules["company_wiki"] = pkg

    _register("company_wiki.source_catalog.models", OVERRIDE / "models.py")
    package_init = REPO_SRC / "company_wiki" / "source_catalog" / "__init__.py"
    sc = types.ModuleType("company_wiki.source_catalog")
    sc.__path__ = [str(REPO_SRC / "company_wiki" / "source_catalog")]
    sc.__package__ = "company_wiki.source_catalog"
    sys.modules["company_wiki.source_catalog"] = sc
    adapters = types.ModuleType("company_wiki.source_catalog.adapters")
    adapters.__path__ = [str(REPO_SRC / "company_wiki" / "source_catalog" / "adapters")]
    adapters.__package__ = "company_wiki.source_catalog.adapters"
    sys.modules["company_wiki.source_catalog.adapters"] = adapters

    _register("company_wiki.source_catalog.models", OVERRIDE / "models.py")
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
        "company_wiki.source_catalog.adapter_dispatch", OVERRIDE / "adapter_dispatch.py"
    )
    _register("company_wiki.source_catalog.config", OVERRIDE / "config.py")
    _register("company_wiki.source_catalog.scanner", OVERRIDE / "scanner.py")
    _register("company_wiki.source_catalog.service", OVERRIDE / "service.py")
    _register(
        "company_wiki.source_catalog.canonical_writer", OVERRIDE / "canonical_writer.py"
    )
    # Exec the REAL package __init__ into the synthetic package module so its
    # ``from .x import ...`` re-exports bind through the override modules
    # registered above (needed by the runner's top-level imports).
    package_init = REPO_SRC / "company_wiki" / "source_catalog" / "__init__.py"
    exec(
        compile(package_init.read_text(encoding="utf-8"), str(package_init), "exec"),
        sc.__dict__,
    )
    return
