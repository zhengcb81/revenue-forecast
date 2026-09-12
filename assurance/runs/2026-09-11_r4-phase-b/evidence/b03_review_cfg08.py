"""B.VR(B03) independent probe: is CFG-08 complete for the boolean fields it
claims to guard?  (sampling the B01 dispositions that landed in be2e4ed/f0aacbf)

Drives the real admission point (``load_catalog_config``) with generated YAML;
modifies nothing.  Usage: python b03_review_cfg08.py <out.json>
"""

from __future__ import annotations

import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile

WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
sys.path.insert(0, str(WIKI / "src"))

from company_wiki.source_catalog.config import (  # noqa: E402
    CatalogConfigError,
    load_catalog_config,
)
from company_wiki.source_catalog.policy import _effective_reusable  # noqa: E402

TEMPLATE = """schema_version: "1.0"
catalog_dir: "${{PROJECT_ROOT}}/.source_catalog"
reusable_root_kinds: [directory]
roots:
  - root_id: probe
    kind: directory
    path: "${{PROJECT_ROOT}}"
{extra}
"""

CASES = [
    ("reusable_for_filing quoted false", '    reusable_for_filing: "false"'),
    ("reusable_for_filing quoted true", '    reusable_for_filing: "true"'),
    ("reusable_for_filing int 1", "    reusable_for_filing: 1"),
    ("reusable_for_filing int 0", "    reusable_for_filing: 0"),
    ("reusable_for_filing empty (null)", "    reusable_for_filing:"),
    ("read_only quoted true", '    read_only: "true"'),
    ("read_only quoted false", '    read_only: "false"'),
    ("read_only int 1", "    read_only: 1"),
    ("read_only int 0", "    read_only: 0"),
    ("read_only empty (null)", "    read_only:"),
    ("read_only yaml yes (1.1 bool)", "    read_only: yes"),
    ("reusable_for_filing yaml no (1.1 bool)", "    reusable_for_filing: no"),
    # non-boolean fields, same admission point (scope boundary of CFG-08)
    ("priority quoted int", '    priority: "10"'),
    ("priority yaml true", "    priority: true"),
    ("priority yaml yes", "    priority: yes"),
    ("max_file_size quoted int", '    max_file_size: "1000"'),
    ("max_file_size bool", "    max_file_size: true"),
]

ROWS: list[dict] = []


def main(argv):
    out_path = Path(argv[1]) if len(argv) > 1 else Path(tempfile.gettempdir()) / "b03_review_cfg08.json"
    base = Path(tempfile.mkdtemp(prefix="b03cfg-"))
    for name, extra in CASES:
        path = base / "cfg.yaml"
        path.write_text(TEMPLATE.format(extra=extra), encoding="utf-8")
        row: dict = {"case": name, "yaml": extra.strip()}
        try:
            config = load_catalog_config(path, project_root=base)
            spec = config.roots[0]
            row.update(
                admitted=True,
                read_only=repr(spec.read_only),
                read_only_type=type(spec.read_only).__name__,
                reusable_for_filing=repr(spec.reusable_for_filing),
                reusable_for_filing_type=type(spec.reusable_for_filing).__name__,
                effective_reusable=_effective_reusable(spec, config),
                priority=spec.priority,
                priority_type=type(spec.priority).__name__,
                max_file_size=spec.max_file_size,
                max_file_size_type=type(spec.max_file_size).__name__,
            )
        except CatalogConfigError as exc:
            row.update(admitted=False, error="CatalogConfigError", text=str(exc)[:160])
        except Exception as exc:  # noqa: BLE001
            row.update(admitted=False, error=type(exc).__name__, text=str(exc)[:160])
        ROWS.append(row)

    # which RootSpec / CatalogConfig fields are annotated boolean?
    import typing

    from company_wiki.source_catalog.models import CatalogConfig, RootSpec

    bool_fields = {}
    for cls in (RootSpec, CatalogConfig):
        hits = []
        for fname, ftype in getattr(cls, "__annotations__", {}).items():
            text = str(ftype)
            if "bool" in text:
                hits.append({"field": fname, "annotation": text})
        bool_fields[cls.__name__] = hits

    payload = {
        "probe": "b03_review_cfg08",
        "wiki_head": subprocess.run(
            ["git", "-C", str(WIKI), "rev-parse", "HEAD"],
            capture_output=True, text=True,
        ).stdout.strip(),
        "boolean_fields": bool_fields,
        "rows": ROWS,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with io.open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
    print(f"wrote {out_path} ({len(ROWS)} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
