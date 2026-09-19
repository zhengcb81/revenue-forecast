"""w02b_bootstrap: isolated module loader for card I-02-B.

Synthesizes the company_wiki / source_catalog package chain pointed at the
READ-ONLY CW repo src, then pre-registers the card's override copies from
A/iso/override (error_taxonomy / acquisition_service / acquisition_journal /
cli) BEFORE any package import resolves, so the deep-layer runner imports the
modified copies under the exact product module names.  Unmodified modules
load from the real repo via the synthetic package __path__.

No read-only repo file is ever modified.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

REPO_SRC = Path(r"C:\Users\郑曾波\Projects\company-wiki") / "src"
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


def setup() -> None:
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

    _register(
        "company_wiki.source_catalog.error_taxonomy", OVERRIDE / "error_taxonomy.py"
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

    # Exec the REAL package __init__ files so absolute/re-exports and any
    # ``company_wiki.source_catalog`` attribute bindings stay consistent.
    top_init = REPO_SRC / "company_wiki" / "__init__.py"
    exec(
        compile(top_init.read_text(encoding="utf-8"), str(top_init), "exec"),
        pkg.__dict__,
    )
    package_init = REPO_SRC / "company_wiki" / "source_catalog" / "__init__.py"
    exec(
        compile(package_init.read_text(encoding="utf-8"), str(package_init), "exec"),
        sc.__dict__,
    )
