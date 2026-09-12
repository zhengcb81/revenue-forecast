"""Trace why ``read_only: null`` is not a CatalogConfigError (CFG-08 edge)."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import traceback

sys.path.insert(0, r"C:\Users\郑曾波\Projects\company-wiki\src")

from company_wiki.source_catalog.config import load_catalog_config  # noqa: E402

DOC = """schema_version: "1.0"
catalog_dir: "${PROJECT_ROOT}/.source_catalog"
reusable_root_kinds: [directory]
roots:
  - root_id: probe
    kind: directory
    path: "${PROJECT_ROOT}"
    read_only:
"""

base = Path(tempfile.mkdtemp(prefix="b03null-"))
path = base / "cfg.yaml"
path.write_text(DOC, encoding="utf-8")
try:
    config = load_catalog_config(path, project_root=base)
    print("ADMITTED", config.roots[0])
except Exception as exc:  # noqa: BLE001
    print(f"{type(exc).__name__}: {exc}")
    traceback.print_exc()
