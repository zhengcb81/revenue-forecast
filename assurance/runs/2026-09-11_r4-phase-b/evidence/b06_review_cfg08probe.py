"""B.VR sampled-commit probe 2 (question g): CFG-08 null/non-bool admission.

Compares the pre-728b5e0 config.py against HEAD on three YAML shapes.
usage: python b06_review_cfg08probe.py <tree_root> <out.json>
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

TREE = Path(sys.argv[1])
OUT = Path(sys.argv[2])
sys.path.insert(0, str(TREE / "src"))

from company_wiki.source_catalog.config import (  # noqa: E402
    CatalogConfigError,
    load_catalog_config,
)

HEADER = [
    'schema_version: "1.0"',
    'catalog_dir: "${PROJECT_ROOT}/.source_catalog"',
    "reusable_root_kinds: [directory]",
    "roots:",
    "  - root_id: probe",
    "    kind: directory",
    '    path: "${PROJECT_ROOT}"',
]


def write(tmp: Path, name: str, line: str) -> Path:
    directory = tmp / "config"
    directory.mkdir(exist_ok=True)
    path = directory / f"{name}.yaml"
    path.write_text("\n".join([*HEADER, f"    {line}"]), encoding="utf-8")
    return path


def probe(tmp: Path, name: str, line: str) -> dict:
    path = write(tmp, name, line)
    try:
        config = load_catalog_config(path)
    except CatalogConfigError as exc:
        return {"line": line, "outcome": "refused(CatalogConfigError)", "error": str(exc)}
    except Exception as exc:  # noqa: BLE001 - classify any other error class
        return {
            "line": line,
            "outcome": f"refused({type(exc).__name__})",
            "error": str(exc),
        }
    root = config.roots[0]
    return {
        "line": line,
        "outcome": "accepted",
        "read_only": repr(root.read_only),
        "reusable_for_filing": repr(root.reusable_for_filing),
        "read_only_is_bool": isinstance(root.read_only, bool),
    }


def main() -> None:
    tmp = Path(tempfile.mkdtemp(prefix="cfg08rv-"))
    out = {
        "tree": str(TREE),
        "read_only_empty": probe(tmp, "ro_empty", "read_only:"),
        "read_only_quoted": probe(tmp, "ro_quoted", 'read_only: "false"'),
        "reusable_empty": probe(tmp, "rf_empty", "reusable_for_filing:"),
        "reusable_absent": probe(tmp, "rf_absent", "kind: directory"),
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
