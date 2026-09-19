"""w02d_bootstrap: isolated module loader for card I-02-D (reentry/dedup).

Same synthetic-package technique as the accepted I-01-A/I-02-A/I-02-C chain:
the read-only repo src backs the package __path__; modified/contract files
are pre-registered from this attempt's iso/override tree BEFORE any package
__init__ executes.

- code="prod": sys.path points at the read-only repo src (before-side probe
  of the unmodified production dedup branch only).
- code="override": D-W02 contract chain (I-02-A models/scanner/service,
  I-02-C canonical_writer/acquisition_service/acquisition_journal/cli
  baseline) loads from this attempt's iso/override copies; canonical_writer
  carries the I-02-D dedup-eligibility + staging-timing fix.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

REPO = Path(r"C:\Users\郑曾波\Projects\company-wiki")
REPO_SRC = REPO / "src"
SC_DIR = REPO_SRC / "company_wiki" / "source_catalog"
ADAPTERS_DIR = SC_DIR / "adapters"
HERE = Path(__file__).resolve().parent
OVERRIDE = HERE.parent / "iso" / "override"


def _register(dotted: str, path: Path) -> None:
    import importlib.util

    spec = importlib.util.spec_from_file_location(dotted, path)
    assert spec is not None and spec.loader is not None, path
    module = importlib.util.module_from_spec(spec)
    sys.modules[dotted] = module
    spec.loader.exec_module(module)
    parent = dotted.rpartition(".")[0]
    if parent in sys.modules:
        setattr(sys.modules[parent], dotted.rpartition(".")[2], module)


def setup(code: str) -> None:
    if code == "prod":
        sys.path.insert(0, str(REPO_SRC))
        return
    if code != "override":
        raise SystemExit(f"unknown code mode: {code}")
    marker = getattr(_register, "_w02d_override_ready", False)
    if marker:
        return  # idempotent: re-registration would split class identities
    _register._w02d_override_ready = True

    pkg = types.ModuleType("company_wiki")
    pkg.__path__ = [str(REPO_SRC / "company_wiki")]
    pkg.__package__ = "company_wiki"
    sys.modules["company_wiki"] = pkg

    sc = types.ModuleType("company_wiki.source_catalog")
    sc.__path__ = [str(SC_DIR)]
    sc.__package__ = "company_wiki.source_catalog"
    sys.modules["company_wiki.source_catalog"] = sc

    adapters = types.ModuleType("company_wiki.source_catalog.adapters")
    adapters.__path__ = [str(ADAPTERS_DIR)]
    adapters.__package__ = "company_wiki.source_catalog.adapters"
    sys.modules["company_wiki.source_catalog.adapters"] = adapters

    _register("company_wiki.source_catalog.models", OVERRIDE / "models.py")
    _register(
        "company_wiki.source_catalog.adapters.registry",
        ADAPTERS_DIR / "registry.py",
    )
    _register(
        "company_wiki.source_catalog.adapters.interface",
        ADAPTERS_DIR / "interface.py",
    )
    _register(
        "company_wiki.source_catalog.adapters.common",
        ADAPTERS_DIR / "common.py",
    )
    _register("company_wiki.source_catalog.lock", OVERRIDE / "lock.py")
    _register(
        "company_wiki.source_catalog.adapters.sidecar",
        ADAPTERS_DIR / "sidecar.py",
    )
    _register(
        "company_wiki.source_catalog.adapters.company_raw",
        ADAPTERS_DIR / "company_raw.py",
    )
    _register(
        "company_wiki.source_catalog.adapters.dayu",
        ADAPTERS_DIR / "dayu.py",
    )
    _register(
        "company_wiki.source_catalog.adapter_dispatch", OVERRIDE / "adapter_dispatch.py"
    )
    _register("company_wiki.source_catalog.config", OVERRIDE / "config.py")
    _register("company_wiki.source_catalog.scanner", OVERRIDE / "scanner.py")
    _register("company_wiki.source_catalog.service", OVERRIDE / "service.py")
    # canonical_writer FIRST: acquisition_service's package-relative import
    # must bind to the override copy, not lazily re-load repo src.
    _register(
        "company_wiki.source_catalog.canonical_writer",
        OVERRIDE / "canonical_writer.py",
    )
    _register(
        "company_wiki.source_catalog.acquisition_journal",
        OVERRIDE / "acquisition_journal.py",
    )
    _register(
        "company_wiki.source_catalog.acquisition_service",
        OVERRIDE / "acquisition_service.py",
    )
    _register("company_wiki.source_catalog.cli", OVERRIDE / "cli.py")

    # Exec the REAL source_catalog package __init__ so its re-exports bind
    # through the override chain registered above.
    package_init = REPO_SRC / "company_wiki" / "source_catalog" / "__init__.py"
    exec(
        compile(
            package_init.read_text(encoding="utf-8"),
            str(package_init),
            "exec",
        ),
        sc.__dict__,
    )
