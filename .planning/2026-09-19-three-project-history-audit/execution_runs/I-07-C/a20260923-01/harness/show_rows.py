"""I-07-C attempt-support row viewer (NOT a product command): prints sources /
locations / entities of one cell's catalog dump.

  python show_rows.py <path-to-catalog_dump.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    arg = Path(sys.argv[1])
    if arg.is_file():
        dump = json.loads(arg.read_text(encoding="utf-8"))
    else:
        # treat as a cell name: dump the LIVE isolated catalog read-only
        from i07c_common import CASES, dump_catalog
        dump = dump_catalog(CASES / arg / "cwroot")
    print("SOURCES")
    for s in dump["sources"]:
        print("  ", json.dumps(s, ensure_ascii=False))
    print("LOCATIONS")
    for loc in dump["locations"]:
        print("   root=%s rel=%s role=%s status=%s src=%s doc=%s size=%s error=%s" % (
            loc["root_id"], loc["relative_path"], loc["role"],
            loc["location_status"], (loc["source_id"] or "")[-16:],
            (loc["document_id"] or "")[-12:], loc["observed_size"],
            loc.get("error")))
    print("ENTITIES", json.dumps(dump["entities"], ensure_ascii=False))
    print("DOC_ENT", json.dumps(dump["document_entities"], ensure_ascii=False))
    print("DOC_METADATA")
    for doc in dump.get("document_metadata") or []:
        print("  ", json.dumps(doc, ensure_ascii=False)[:1200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
